#!/usr/bin/env python3
"""env-art's player-height stills at every POI and interactable of the Prologue–Ch4 zones (the Lead's 10-30 pass).

Each zone is staged as tools/act1/walkthrough.py stages it (level, spawn, flags). walk_render.tscn's auto_targets mode
then stands an eye off every Interactable in the level and every zone-map POI (game/data/ui/zone_maps.json) and saves a
frame of each. Never a test or a baseline: env-art views the frames.

    python3 tools/act1/poi_stills.py --out DIR [--zone ID ...]

writes DIR/<zone>/targets.json and prints the godot-render line for each zone (frames to DIR/<zone>/).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import walkthrough  # noqa: E402

# walkthrough's zones, one per level (its Haluna "touch" walk is the same level), and Act II's Ch10–Ch12 (the Lead's
# 10-30 pass): (level, spawn, flags).
ACT2 = {z.replace("/", "_"): (f"res://game/levels/{z}/{z.split('/')[1]}.tscn", spawn, []) for z, spawn in (
    ("ch10/ossa_fen", "FenEdge"), ("ch10/reedhollow", "Gate"), ("ch11/sunken_vey", "Landing"),
    ("ch11/lowlight", "Gate"), ("ch12/keth_pass", "PassFoot"), ("ch12/quellan", "FromPass"),
    ("ch12/cloudloom", "Approach"))}
ZONES = [z for z in walkthrough.ZONES if z != "ch02_haluna_touch"] + list(ACT2)
ZONE_MAPS = ROOT / "game" / "data" / "ui" / "zone_maps.json"


def pois(level_path: str) -> list[dict]:
    zones = json.loads(ZONE_MAPS.read_text(encoding="utf-8"))["zone_maps"]["zones"]
    rows = zones.values() if isinstance(zones, dict) else zones
    for z in rows:
        if z.get("scene") == level_path:
            return [{"id": p["id"], "at": p["at"]} for p in z.get("pois", [])]
    return []


def targets(zone: str) -> dict:
    level, spawn, flags = ACT2[zone] if zone in ACT2 else walkthrough.ZONES[zone][:3]
    return {"level_path": level, "spawn": spawn, "flags": flags, "auto_targets": True, "pois": pois(level),
            "points": []}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--zone", action="append", choices=ZONES)
    args = ap.parse_args()
    for zone in args.zone or ZONES:
        d = args.out / zone
        d.mkdir(parents=True, exist_ok=True)
        (d / "targets.json").write_text(json.dumps(targets(zone), indent=1) + "\n", encoding="utf-8")
        print(f"godot-render --path {ROOT} --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan "
              f"res://game/levels/_tests/walkthrough/walk_render.tscn -- --walk={d / 'targets.json'} --out={d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
