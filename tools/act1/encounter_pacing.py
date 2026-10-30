#!/usr/bin/env python3
"""Field encounter pacing (the Lead's FAST-TRACK, 2026-10-30, from the human's playtest: "combat encounters still
seemed too frequent after one another"). For every zone layout with an `encounters` block, the breather between two
ordinary fights at the run (game/data/world/field_movement.json `run_speed_mps`): FieldEncounters walks the post-battle
`grace_m`, then a gap drawn in [max(min_m, min_gap_m), max(max_m, min_gap_m)], and holds the fight until `grace_s` of
field time has passed too (game/world/zone/field_encounters.gd; defaults in game/data/world/greybox_defaults.json).

The meter is pure distance plus field time, so the bounds are exact for a straight run. Walking (`walk_speed_mps`)
only lengthens them, and so do Light Step and Ch1's lantern shutter. The fade back from a battle is never counted
(field time starts at Rhen's first step back).

Fails when any zone's shortest breather at the run is under TARGET_S, the low end of the Lead's 30-45 s.
Run: python3 tools/act1/encounter_pacing.py [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULTS = ROOT / "game/data/world/greybox_defaults.json"
MOVEMENT = ROOT / "game/data/world/field_movement.json"
LEVELS = ROOT / "game/levels"
## The Lead's breather between ordinary fights: at least ~30-45 s.
TARGET_S = 30.0
## Test fixtures, not zones the player walks.
SKIP_DIR = "_tests"


def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def zone_rows(root: Path = ROOT) -> list[dict]:
    """One row per zone with random encounters: its breather bounds at the run, in seconds."""
    defaults = _json(root / DEFAULTS.relative_to(ROOT)).get("encounters", {})
    run = float(_json(root / MOVEMENT.relative_to(ROOT))["run_speed_mps"])
    rows = []
    for p in sorted((root / LEVELS.relative_to(ROOT)).rglob("*_layout.json")):
        if SKIP_DIR in p.parts:
            continue
        block = _json(p).get("encounters")
        if not block:
            continue
        grace_m = float(block.get("grace_m", defaults.get("grace_m", 0.0)))
        grace_s = float(block.get("grace_s", defaults.get("grace_s", 0.0)))
        floor = float(block.get("min_gap_m", defaults.get("min_gap_m", 0.0)))
        lo = max(float(block["min_m"]), floor)
        hi = max(float(block.get("max_m", block["min_m"])), floor)
        rows.append({
            "layout": str(p.relative_to(root)),
            "gap_m": [lo, hi],
            "grace_m": grace_m,
            "grace_s": grace_s,
            "min_s": round(max((lo + grace_m) / run, grace_s), 1),
            "max_s": round(max((hi + grace_m) / run, grace_s), 1),
        })
    return rows


def errors(rows: list[dict]) -> list[str]:
    return [f"{r['layout']}: the shortest breather is {r['min_s']} s at the run (target >= {TARGET_S} s)"
            for r in rows if r["min_s"] < TARGET_S]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    rows = zone_rows()
    if args.json:
        print(json.dumps(rows, indent=1))
    else:
        for r in rows:
            print(f"{r['min_s']:6.1f}-{r['max_s']:5.1f} s  gap {r['gap_m'][0]:g}-{r['gap_m'][1]:g} m"
                  f" + grace {r['grace_m']:g} m / {r['grace_s']:g} s  {r['layout']}")
    errs = errors(rows)
    for e in errs:
        print("ERROR " + e, file=sys.stderr)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
