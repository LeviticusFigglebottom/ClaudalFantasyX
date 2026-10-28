#!/usr/bin/env python3
"""Act I's loops by ear's proxy (M3-AUD-861, ADR 0041): every music loop and ambience bed an Act I zone plays, decoded
from the shipped file (git lfs pull first) and measured the way render_all.py measures a render:

  seam     loop_seam_report at the sidecar's loop point: the jump (sample step at the wrap, against the file's median
           step) and the spectral flux (against its median). A click shows as a jump well over 10, a gap or a bump in
           the texture as flux over 3 (render_all.py's gate).
  level    integrated LUFS and true peak against the file's targets.py rule.
  balance  each zone's bed against its music: mix.md puts beds about 10 LU under the music (-26 against -16).

Run: python3 tools/audio/act1_loop_check.py [--md]   (exit 1 when any row fails)"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))

import targets  # noqa: E402
from synth.analysis import loop_seam_report  # noqa: E402
from synth.loudness import integrated_lufs, true_peak_dbtp  # noqa: E402
from synth.mixer import read_audio  # noqa: E402

DATA = ROOT / "game" / "data" / "audio"
ACT1 = ["prologue"] + [f"ch0{i}" for i in range(1, 10)]
JUMP_MAX, FLUX_MAX = 10.0, 3.0
BALANCE_LU = (6.0, 14.0)   # a bed this many LU under its zone's music


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _rel(res: str) -> str:
    p = res.removeprefix("res://")
    for root in ("assets/lfs/audio/", "assets/audio/"):
        if p.startswith(root):
            return p[len(root):]
    return p


def zone_files() -> list[tuple[str, str, str]]:
    """(zone, kind, res path) for each Act I zone's music (and variants) and beds, in a fixed order."""
    music = _json(DATA / "music.json")
    cues = music["cues"]
    amb = _json(DATA / "ambience.json")
    out = []

    def cue_files(cid: str) -> list[str]:
        r = cues.get(cid, {})
        return [r["file"]] if r.get("file") else list(r.get("stems", []))

    for z in music["zones"]:
        scene = z["scene"]
        if not any(f"/levels/{d}/" in scene for d in ACT1):
            continue
        zone = scene.split("/")[-1].removesuffix(".tscn")
        for cid in [z.get("music")] + [v.get("music") for v in z.get("variants", [])]:
            for f in cue_files(cid) if cid else []:
                out.append((zone, f"music {cid}", f))
    for scene, z in amb["zones"].items():
        if not any(f"/levels/{d}/" in scene for d in ACT1):
            continue
        zone = scene.split("/")[-1].removesuffix(".tscn")
        for bid in z.get("day", []) + z.get("night", []):
            f = amb["ambience"].get(bid, {}).get("file")
            if f:
                out.append((zone, f"bed {bid}", f))
    seen, uniq = set(), []
    for row in out:
        if row not in seen:
            seen.add(row)
            uniq.append(row)
    return uniq


def measure(res: str) -> dict:
    p = ROOT / res.removeprefix("res://")
    side = Path(str(p)[:-4] + ".loop.json")
    y = read_audio(str(p), channels=2)
    m = {"il": integrated_lufs(y), "tp": true_peak_dbtp(y), "seam": None}
    if side.is_file():
        meta = _json(side)
        m["seam"] = loop_seam_report(y, int(meta["loop_start_samples"]))
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", action="store_true", help="print a markdown table")
    args = ap.parse_args()
    rows, bad, cache = [], [], {}
    for zone, kind, res in zone_files():
        m = cache.get(res) or measure(res)
        cache[res] = m
        rule = targets.rule_for(_rel(res))
        _, metric, target, tol, ceiling, _ = rule if rule else (None, None, None, 0, 0, None)
        notes = []
        seam = m["seam"]
        if seam is None:
            notes.append("no loop sidecar")
        elif seam["jump_ratio"] > JUMP_MAX or seam["flux_ratio"] > FLUX_MAX:
            notes.append("SEAM")
        if rule and metric in ("integrated", "stem") and metric == "integrated" and abs(m["il"] - target) > tol:
            notes.append("LEVEL")
        if rule and m["tp"] > ceiling + 0.05:
            notes.append("PEAK")
        rows.append((zone, kind, res, m, ", ".join(notes) or "ok"))
        if any(n in notes for n in ("SEAM", "LEVEL", "PEAK", "no loop sidecar")):
            bad.append((zone, kind))
    # balance: each zone's first bed against its music's level
    by_zone: dict[str, dict] = {}
    for zone, kind, res, m, _ in rows:
        k = "music" if kind.startswith("music") else "bed"
        by_zone.setdefault(zone, {}).setdefault(k, []).append(m["il"])
    balance = {}
    for zone, d in by_zone.items():
        if d.get("music") and d.get("bed"):
            gap = max(d["music"]) - max(d["bed"])
            balance[zone] = gap
            if not (BALANCE_LU[0] <= gap <= BALANCE_LU[1]):
                bad.append((zone, f"balance {gap:.1f} LU"))
    if args.md:
        print("| Zone | What | LUFS | TP dBTP | Seam jump | Seam flux | |")
        print("|---|---|---|---|---|---|---|")
    for zone, kind, res, m, note in rows:
        s = m["seam"] or {"jump_ratio": float("nan"), "flux_ratio": float("nan")}
        if args.md:
            print(f"| {zone} | {kind} | {m['il']:.2f} | {m['tp']:.2f} | x{s['jump_ratio']:.2f} | x{s['flux_ratio']:.2f} "
                  f"| {note} |")
        else:
            print(f"{zone:24} {kind:34} {m['il']:7.2f} {m['tp']:6.2f}  jump x{s['jump_ratio']:5.2f} "
                  f"flux x{s['flux_ratio']:5.2f}  {note}")
    print()
    for zone, gap in sorted(balance.items()):
        print(f"{'- ' if args.md else ''}{zone}: bed {gap:.1f} LU under the music")
    print(f"\n{len(rows)} file(s), {len(bad)} problem(s){': ' + str(bad) if bad else ''}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
