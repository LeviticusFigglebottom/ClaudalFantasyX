#!/usr/bin/env python3
"""Palette measurements over rendered PNGs (M1-ENV-01, review-sweep-F).

Two jobs, both in Oklab (ΔE_ok is plain Euclidean distance in Oklab, as the colour script uses):

  coverage  How much of a frame (or a rectangle of it) each palette swatch covers, and the two
            budget masks of haluna.md §6 ("gold ≤ 5%, red ≤ 8%"). A pixel counts for the swatch
            whose on-screen value (any of the -1 / 0 / +1 columns of palette.json `onscreen_hex`)
            is nearest, if that distance is ≤ --max-de. The HSV red mask is the one the art
            review used before this tool existed (hue < 25° or > 340°, saturation > 0.35), kept so
            the numbers stay comparable; the swatch masks are the stricter reading.

  check     Runs the numeric checks in tests/screenshots/palette_checks.json against a directory
            of shots (the committed baselines by default) and exits 1 on any failure. A check
            selects pixels inside a rectangle (optionally filtered by Oklab L / C / hue), takes a
            statistic, and compares it with a palette swatch's on-screen value or with a bound.

Usage:
  palette_check.py coverage <png> [--rect x0,y0,x1,y1] [--max-de 0.08] [--top 12]
  palette_check.py check [--checks FILE] [--dir DIR] [--shots a,b]
  palette_check.py region <png> --rect x0,y0,x1,y1 [--C-min ..] [--C-max ..] [--L-min ..] [--L-max ..]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pngio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "docs" / "kb" / "art" / "palette.json"
CHECKS = ROOT / "tests" / "screenshots" / "palette_checks.json"
BASELINES = ROOT / "tests" / "screenshots" / "baselines"
LEVELS = ("-1", "0", "+1")
# The review's HSV red mask (haluna.md §6 red budget, before the swatch-mask view existed).
HSV_RED_HUE_LO_DEG = 25.0
HSV_RED_HUE_HI_DEG = 340.0
HSV_RED_SAT_MIN = 0.35
RED_SWATCHES = ("roof_clay", "laterite", "lacquer_red", "lacquer_red_deep", "ember_orange")
GOLD_SWATCHES = ("gold_leaf", "gold_leaf_hi", "brass")


# ---------------------------------------------------------------- colour maths


def srgb8_to_linear(rgb: np.ndarray) -> np.ndarray:
    c = rgb.astype(np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_oklab(lin: np.ndarray) -> np.ndarray:
    """Linear sRGB (..., 3) -> Oklab (..., 3) (Björn Ottosson's matrices)."""
    m1 = np.array(
        [
            [0.4122214708, 0.5363325363, 0.0514459929],
            [0.2119034982, 0.6806995451, 0.1073969566],
            [0.0883024619, 0.2817188376, 0.6299787005],
        ]
    )
    m2 = np.array(
        [
            [0.2104542553, 0.7936177850, -0.0040720468],
            [1.9779984951, -2.4285922050, 0.4505937099],
            [0.0259040371, 0.7827717662, -0.8086757660],
        ]
    )
    lms = np.cbrt(lin @ m1.T)
    return lms @ m2.T


def hex_to_rgb8(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i : i + 2], 16) for i in (0, 2, 4)], dtype=np.uint8)


def hex_to_oklab(h: str) -> np.ndarray:
    return linear_to_oklab(srgb8_to_linear(hex_to_rgb8(h)))


def rgb8_to_hex(rgb: np.ndarray) -> str:
    r, g, b = (int(round(float(v))) for v in rgb[:3])
    return f"#{r:02X}{g:02X}{b:02X}"


def lch(lab: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Oklab -> (L, C, hue in degrees 0..360)."""
    L = lab[..., 0]
    C = np.hypot(lab[..., 1], lab[..., 2])
    h = np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360.0
    return L, C, h


def image_oklab(img: np.ndarray) -> np.ndarray:
    rgb = img[:, :, :3]
    if img.dtype == np.uint16:
        rgb = (rgb.astype(np.float64) / 257.0).round()
    return linear_to_oklab(srgb8_to_linear(rgb))


def hsv(img: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """8-bit sRGB -> (hue degrees, saturation, value), the plain HSV of the encoded values."""
    c = img[:, :, :3].astype(np.float64) / 255.0
    mx, mn = c.max(axis=2), c.min(axis=2)
    d = mx - mn
    r, g, b = c[:, :, 0], c[:, :, 1], c[:, :, 2]
    safe = np.where(d > 0, d, 1.0)
    h = np.where(
        mx == r, ((g - b) / safe) % 6.0, np.where(mx == g, (b - r) / safe + 2.0, (r - g) / safe + 4.0)
    )
    h = np.where(d > 0, h * 60.0, 0.0)
    s = np.where(mx > 0, d / np.where(mx > 0, mx, 1.0), 0.0)
    return h, s, mx


# ---------------------------------------------------------------- palette


def load_palette(path: Path = PALETTE) -> dict[str, dict[str, np.ndarray]]:
    """{swatch: {level: oklab}} for every swatch with on-screen values."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, np.ndarray]] = {}
    for name, sw in data["swatches"].items():
        on = sw.get("onscreen_hex")
        if on:
            out[name] = {lv: hex_to_oklab(on[lv]) for lv in LEVELS if lv in on}
    return out


def nearest_swatch(lab: np.ndarray, palette: dict[str, dict[str, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    """Per pixel: (index into sorted swatch names, ΔE_ok to the nearest column of that swatch)."""
    names = sorted(palette)
    flat = lab.reshape(-1, 3)
    best_d = np.full(flat.shape[0], np.inf)
    best_i = np.zeros(flat.shape[0], dtype=np.int32)
    for i, n in enumerate(names):
        for ref in palette[n].values():
            d = np.linalg.norm(flat - ref, axis=1)
            better = d < best_d
            best_d[better] = d[better]
            best_i[better] = i
    return best_i.reshape(lab.shape[:2]), best_d.reshape(lab.shape[:2])


# ---------------------------------------------------------------- measurements


def crop(arr: np.ndarray, rect: list[int] | None) -> np.ndarray:
    if not rect:
        return arr
    x0, y0, x1, y1 = rect
    return arr[y0:y1, x0:x1]


def hsv_red_mask(img: np.ndarray) -> np.ndarray:
    h, s, _ = hsv(img)
    return ((h < HSV_RED_HUE_LO_DEG) | (h > HSV_RED_HUE_HI_DEG)) & (s > HSV_RED_SAT_MIN)


def coverage(img: np.ndarray, palette: dict, max_de: float, rect: list[int] | None = None) -> dict:
    img = crop(img, rect)
    lab = image_oklab(img)
    names = sorted(palette)
    idx, dist = nearest_swatch(lab, palette)
    hit = dist <= max_de
    n = float(idx.size)
    per = {names[i]: float(np.count_nonzero(hit & (idx == i))) / n for i in range(len(names))}
    red_sw = sum(per.get(s, 0.0) for s in RED_SWATCHES)
    gold_sw = sum(per.get(s, 0.0) for s in GOLD_SWATCHES)
    return {
        "pixels": int(n),
        "matched": float(np.count_nonzero(hit)) / n,
        "swatches": dict(sorted(per.items(), key=lambda kv: -kv[1])),
        "red_hsv": float(np.count_nonzero(hsv_red_mask(img))) / n,
        "red_swatch": red_sw,
        "gold_swatch": gold_sw,
    }


def select(lab: np.ndarray, sel: dict) -> np.ndarray:
    L, C, h = lch(lab)
    m = np.ones(L.shape, dtype=bool)
    for key, arr in (("L", L), ("C", C), ("h", h)):
        if f"{key}_min" in sel:
            m &= arr >= sel[f"{key}_min"]
        if f"{key}_max" in sel:
            m &= arr <= sel[f"{key}_max"]
    return m


def region_stats(img: np.ndarray, rect: list[int] | None, sel: dict | None = None) -> dict:
    """Stats of the selected pixels: median colour (hex + Oklab LCh) and L percentiles."""
    sub = crop(img, rect)
    lab = image_oklab(sub)
    m = select(lab, sel or {})
    count = int(np.count_nonzero(m))
    if count == 0:
        return {"count": 0, "fraction": 0.0}
    pix = lab[m]
    L, C, h = lch(pix)
    med_rgb = np.median(sub[:, :, :3][m].astype(np.float64), axis=0)
    med_lab = linear_to_oklab(srgb8_to_linear(np.round(med_rgb)))
    mL, mC, mh = lch(med_lab)
    return {
        "count": count,
        "fraction": count / float(m.size),
        "median_hex": rgb8_to_hex(med_rgb),
        "median_lab": med_lab,
        "L_median": float(mL),
        "C_median": float(mC),
        "h_median": float(mh),
        "L_p05": float(np.percentile(L, 5)),
        "L_p95": float(np.percentile(L, 95)),
        "C_mean": float(np.mean(C)),
    }


def grain(img: np.ndarray, rect: list[int] | None, sel: dict | None = None) -> float:
    """Pixel-scale grain (stipple, per-pixel march jitter): the MEDIAN over selected pixels of the
    larger absolute second difference of L (x or y). A smooth gradient has ~0 second difference and a
    shape edge only touches a thin line of pixels, which the median ignores; grain lifts every pixel."""
    lab = image_oklab(crop(img, rect))
    L = lab[..., 0]
    m = select(lab, sel or {})
    d2x = np.abs(L[1:-1, :-2] - 2.0 * L[1:-1, 1:-1] + L[1:-1, 2:])
    d2y = np.abs(L[:-2, 1:-1] - 2.0 * L[1:-1, 1:-1] + L[2:, 1:-1])
    mm = m[1:-1, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:] & m[:-2, 1:-1] & m[2:, 1:-1]
    v = np.maximum(d2x, d2y)[mm]
    return float(np.median(v)) if v.size else 0.0


# ---------------------------------------------------------------- checks


def run_check(chk: dict, img: np.ndarray, palette: dict) -> tuple[bool, str]:
    kind = chk["kind"]
    rect = chk.get("rect")
    sel = chk.get("select")
    if kind == "mask_fraction":
        cov = coverage(img, palette, chk.get("max_de", 0.08), rect)
        val = cov[chk["mask"]]
        return val <= chk["max"], f"{chk['mask']} {val:.3f} (max {chk['max']:.3f})"
    if kind == "grain":
        val = grain(img, rect, sel)
        return val <= chk["max"], f"grain {val:.4f} (max {chk['max']:.4f})"
    st = region_stats(img, rect, sel)
    min_count = chk.get("min_fraction", 0.02)
    if st["count"] == 0 or st["fraction"] < min_count:
        return False, f"selection covers {st.get('fraction', 0.0):.3f} of the rect (< {min_count})"
    if kind == "near_swatch":
        ref = palette[chk["swatch"]][chk["level"]]
        de = float(np.linalg.norm(st["median_lab"] - ref))
        msg = f"median {st['median_hex']} ΔE_ok {de:.3f} to {chk['swatch']} {chk['level']} (max {chk['max_de']})"
        return de <= chk["max_de"], msg
    if kind == "stat":
        val = st[chk["stat"]]
        ok = chk.get("min", -np.inf) <= val <= chk.get("max", np.inf)
        bounds = f"[{chk.get('min', '-')}, {chk.get('max', '-')}]"
        return ok, f"{chk['stat']} {val:.3f} in {bounds} (median {st['median_hex']}, {st['fraction']:.2f} of rect)"
    raise ValueError(f"unknown check kind {kind}")


def run_checks(checks_path: Path, shot_dir: Path, only: set[str] | None = None) -> tuple[int, list[str]]:
    spec = json.loads(checks_path.read_text(encoding="utf-8"))
    palette = load_palette()
    failures = 0
    lines: list[str] = []
    cache: dict[str, np.ndarray] = {}
    for chk in spec["checks"]:
        sid = chk["shot"]
        if only and sid not in only:
            continue
        p = shot_dir / f"{sid}.png"
        if not p.exists():
            failures += 1
            lines.append(f"FAIL {sid} {chk['name']}: no image at {p}")
            continue
        if sid not in cache:
            cache[sid] = pngio.read(p)
        ok, msg = run_check(chk, cache[sid], palette)
        failures += 0 if ok else 1
        lines.append(f"{'ok  ' if ok else 'FAIL'} {sid} {chk['name']}: {msg}")
    return failures, lines


# ---------------------------------------------------------------- CLI


def _rect(s: str | None) -> list[int] | None:
    return [int(v) for v in s.split(",")] if s else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("coverage")
    c.add_argument("png", type=Path)
    c.add_argument("--rect")
    c.add_argument("--max-de", type=float, default=0.08)
    c.add_argument("--top", type=int, default=12)
    k = sub.add_parser("check")
    k.add_argument("--checks", type=Path, default=CHECKS)
    k.add_argument("--dir", type=Path, default=BASELINES)
    k.add_argument("--shots", default="")
    r = sub.add_parser("region")
    r.add_argument("png", type=Path)
    r.add_argument("--rect")
    for key in ("L", "C", "h"):
        r.add_argument(f"--{key}-min", type=float)
        r.add_argument(f"--{key}-max", type=float)
    a = ap.parse_args(argv)
    if a.cmd == "coverage":
        cov = coverage(pngio.read(a.png), load_palette(), a.max_de, _rect(a.rect))
        print(f"{a.png.name}: {cov['pixels']} px, {cov['matched'] * 100:.1f}% within ΔE_ok {a.max_de}")
        print(f"  red (HSV mask)     {cov['red_hsv'] * 100:5.1f}%")
        print(f"  red (swatch mask)  {cov['red_swatch'] * 100:5.1f}%   {', '.join(RED_SWATCHES)}")
        print(f"  gold (swatch mask) {cov['gold_swatch'] * 100:5.1f}%   {', '.join(GOLD_SWATCHES)}")
        for name, frac in list(cov["swatches"].items())[: a.top]:
            print(f"  {name:24s} {frac * 100:5.1f}%")
        return 0
    if a.cmd == "region":
        sel = {f"{key}_{b}": getattr(a, f"{key}_{b}") for key in ("L", "C", "h") for b in ("min", "max")}
        sel = {kk: v for kk, v in sel.items() if v is not None}
        img = pngio.read(a.png)
        st = region_stats(img, _rect(a.rect), sel)
        st.pop("median_lab", None)
        st["grain"] = grain(img, _rect(a.rect), sel)
        print(json.dumps({kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in st.items()}))
        return 0
    only = {s for s in a.shots.split(",") if s} or None
    failures, lines = run_checks(a.checks, a.dir, only)
    print("\n".join(lines))
    print(f"palette checks: {len(lines) - failures} ok, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
