#!/usr/bin/env python3
"""Screenshot regression (SPEC §5.5, M1-QA-01, ADR 0009).

Flow:
  1. tools/screenshots/capture.sh (or godot-render ... res://tests/screenshots/capture.tscn)
     renders every shot in tests/screenshots/shots.json to tests/screenshots/out/<id>.png.
  2. This script compares out/ against tests/screenshots/baselines/: RMSE over RGB in *linear*
     light (sRGB decoded, values 0..1), failing any shot above its `threshold_rmse`. It writes
     out/diff/<id>.png for every compared shot: the baseline darkened, with per-pixel error in red.

Usage:
  compare.py                       compare every shot (exit 1 on drift, missing output or baseline)
  compare.py --manifest-only       validate shots.json and list baselines (no capture needed)
  compare.py --update-baselines [ID ...]   approve: copy out/<id>.png over the baseline(s)
  compare.py --shots a,b           restrict to these shot ids
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pngio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "tests" / "screenshots" / "shots.json"
BASELINES = ROOT / "tests" / "screenshots" / "baselines"
OUT = ROOT / "tests" / "screenshots" / "out"
REQUIRED = ("id", "scene", "camera", "resolution", "threshold_rmse")
SETUP_KEYS = {"globals", "nodes", "viewport", "time_scale"}  # must match CaptureSetup.KEYS (M1-QA-04)
# A new shot waits for its first baseline: `"pending_baseline": true` until the Lead's gate views and approves it
# (then the key goes). compare.py reports it PENDING instead of failing; with a baseline present it is compared.
PENDING = "pending_baseline"
BASELINE_META = "baselines.json"
DIFF_GAIN = 8.0  # error 1/8 of full scale (linear) saturates the red channel in the diff image
DIFF_BACKDROP = 0.35  # baseline brightness under the red error overlay


def load_shots(path: Path) -> list[dict]:
    """Return the shots with manifest defaults applied. Raises ValueError on a bad manifest."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    defaults = manifest.get("defaults", {})
    shots: list[dict] = []
    seen: set[str] = set()
    for raw in manifest.get("shots", []):
        shot = {**defaults, **raw}
        missing = [k for k in REQUIRED if k not in shot]
        if missing:
            raise ValueError(f"shot {shot.get('id', '?')}: missing {', '.join(missing)}")
        if shot["id"] in seen:
            raise ValueError(f"duplicate shot id {shot['id']}")
        setup = shot.get("setup", {})
        if not isinstance(setup, dict) or not set(setup) <= SETUP_KEYS:
            raise ValueError(f"shot {shot['id']}: setup must be an object with keys from {sorted(SETUP_KEYS)}")
        if not isinstance(shot.get(PENDING, False), bool):
            raise ValueError(f"shot {shot['id']}: {PENDING} must be true or false")
        seen.add(shot["id"])
        shots.append(shot)
    return shots


def srgb_to_linear(img: np.ndarray) -> np.ndarray:
    """uint8/uint16 sRGB-encoded RGB(A) -> float64 linear RGB in 0..1 (alpha dropped)."""
    scale = 65535.0 if img.dtype == np.uint16 else 255.0
    if img.shape[2] < 3:  # greyscale (+alpha)
        img = np.repeat(img[:, :, :1], 3, axis=2)
    c = img[:, :, :3].astype(np.float64) / scale
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb8(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, 1.0)
    s = np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
    return np.round(s * 255.0).astype(np.uint8)


def rmse_linear(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape[:2] != b.shape[:2]:
        raise ValueError(f"size mismatch: {a.shape[1]}x{a.shape[0]} vs {b.shape[1]}x{b.shape[0]}")
    return float(np.sqrt(np.mean((srgb_to_linear(a) - srgb_to_linear(b)) ** 2)))


def diff_image(baseline: np.ndarray, actual: np.ndarray) -> np.ndarray:
    """Baseline darkened, per-pixel linear error painted in red (8-bit sRGB RGB)."""
    la, lb = srgb_to_linear(actual), srgb_to_linear(baseline)
    err = np.clip(np.sqrt(np.mean((la - lb) ** 2, axis=2)) * DIFF_GAIN, 0.0, 1.0)
    out = lb * DIFF_BACKDROP
    out[:, :, 0] = np.maximum(out[:, :, 0], err)
    out[:, :, 1:] *= (1.0 - err)[:, :, None]
    return linear_to_srgb8(out)


def compare_shot(shot: dict, out_dir: Path, base_dir: Path) -> tuple[bool, str]:
    sid = shot["id"]
    actual_p, base_p = out_dir / f"{sid}.png", base_dir / f"{sid}.png"
    if not actual_p.exists():
        return False, "no capture (run tools/screenshots/capture.sh)"
    if not base_p.exists():
        if shot.get(PENDING, False):
            return True, "PENDING its first baseline (the gate views and approves it)"
        return False, "no baseline (inspect out/, then compare.py --update-baselines %s)" % sid
    actual, base = pngio.read(actual_p), pngio.read(base_p)
    if actual.shape[:2] != base.shape[:2]:
        return False, f"size {actual.shape[1]}x{actual.shape[0]} != baseline {base.shape[1]}x{base.shape[0]}"
    want = tuple(shot["resolution"])
    if (actual.shape[1], actual.shape[0]) != want:
        return False, f"capture is {actual.shape[1]}x{actual.shape[0]}, manifest wants {want[0]}x{want[1]}"
    err = rmse_linear(actual, base)
    (out_dir / "diff").mkdir(parents=True, exist_ok=True)
    pngio.write(out_dir / "diff" / f"{sid}.png", diff_image(base, actual))
    limit = float(shot["threshold_rmse"])
    return err <= limit, f"rmse {err:.5f} (limit {limit:.5f})"


def update_baselines(shots: list[dict], ids: list[str], out_dir: Path, base_dir: Path) -> int:
    known = {s["id"] for s in shots}
    targets = ids or sorted(known)
    unknown = [i for i in targets if i not in known]
    if unknown:
        print(f"ERROR unknown shot id(s): {', '.join(unknown)}")
        return 1
    meta_p = base_dir / BASELINE_META
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    report_p = out_dir / "capture_report.json"
    report = json.loads(report_p.read_text(encoding="utf-8")) if report_p.exists() else {}
    base_dir.mkdir(parents=True, exist_ok=True)
    for sid in targets:
        src = out_dir / f"{sid}.png"
        if not src.exists():
            print(f"ERROR {sid}: no capture at {src}")
            return 1
        shutil.copyfile(src, base_dir / f"{sid}.png")
        meta[sid] = {k: report.get(k, "?") for k in ("godot", "rendering_method", "rendering_driver", "adapter")}
        print(f"approved {sid}")
    meta_p.write_text(json.dumps(dict(sorted(meta.items())), indent=2) + "\n", encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, default=SHOTS)
    ap.add_argument("--baselines", type=Path, default=BASELINES)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--shots", default="", help="comma-separated shot ids")
    ap.add_argument("--manifest-only", action="store_true")
    ap.add_argument("--update-baselines", nargs="*", metavar="ID")
    args = ap.parse_args(argv)
    try:
        shots = load_shots(args.manifest)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"ERROR {args.manifest}: {e}")
        return 1
    if args.shots:
        wanted = set(args.shots.split(","))
        shots = [s for s in shots if s["id"] in wanted]
    if args.update_baselines is not None:
        return update_baselines(shots, args.update_baselines, args.out, args.baselines)
    if args.manifest_only:
        for s in shots:
            has = (args.baselines / f"{s['id']}.png").exists()
            print(f"{'ok     ' if has else 'NO BASE'} {s['id']} ({s['scene']}, camera {s['camera']})")
        print(f"screenshot manifest: {len(shots)} shot(s) valid")
        return 0
    failed = 0
    for s in shots:
        ok, msg = compare_shot(s, args.out, args.baselines)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} {s['id']}: {msg}")
    print(f"Screenshots: {len(shots)} compared, {failed} failed (diffs in {args.out / 'diff'})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
