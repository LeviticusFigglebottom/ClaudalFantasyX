#!/usr/bin/env python3
"""Ch1 Oruvel: env-art's raft-town kit (M3-ENV-07) placed on the greybox zone (M3-C01-100, ADR 0200).

Writes game/levels/ch01/oruvel/oruvel_dressing.json (ZoneKitDressing's layout) in the greybox zone's frame (x east,
north = -Z; the scale-hull south at (0, 10), the commons at (0, -12), the outer mooring west at (-27, -12), the
keel-hull north at (0, -34), Kell's second mooring east at (30, -6), the dive mooring at (45, -6), the net-pen at
(30, -22)). The greybox keeps the gameplay: its decks are flat at y 0 and the controller has no step-up, so every
kit deck is sunk by its deck height (oruvel.md: raft_deck +0.80, raft_deck_small +0.70, dive_raft +0.75, net_pen
+0.60, keel_hull +1.0, chandlery +0.5, scale_hull +0.4), which puts the hulls' waterline at SEA_Y. The kit's
preview grade and water look are copied next to the zone (shipped scenes never load game/levels/_tests/).
Story blocks the kit has no piece for stay greybox (`keep`). Re-run after the kit changes:
    python3 tools/ch01/ch01_oruvel_dressing.py [--check]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch01" / "oruvel"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_kit"
OUT = ZONE / "oruvel_dressing.json"
RES_ZONE = "res://game/levels/ch01/oruvel/"
COPIES = {  # preview file -> zone file (the kit's grade and water look)
    "oruvel_ch01_environment.tres": "oruvel_ch01_environment.tres",
    "oruvel_storm_environment.tres": "oruvel_storm_environment.tres",
    "oruvel_water_material.tres": "oruvel_water_material.tres",
}
DECK = {"raft_deck": 0.80, "raft_deck_small": 0.70, "dive_raft": 0.75, "net_pen": 0.60, "keel_hull": 1.0,
        "chandlery": 0.5, "scale_hull": 0.4, "cookboat": 0.6, "hull_outrigger": 0.3, "hull_cabin": 0.5}
SEA_Y = -0.8  # the raft decks' waterline once sunk; the greybox's solid sea floor is at -1.0
KEEP = ["SeventhTerrace", "NameBoard", "KeelGull", "KellBeacon", "LowHull", "StormWall", "DiveGull"]


def piece(name: str, x: float, z: float, yaw: float = 0.0, y: float | None = None, **extra: object) -> dict:
    """A kit piece at (x, z); a deck piece sinks by its deck height unless `y` is given."""
    yy = -DECK[name] if y is None and name in DECK else (y or 0.0)
    row: dict = {"piece": name, "at": [round(x, 3), round(z, 3)], "y": round(yy, 3), "yaw_deg": round(yaw, 2)}
    row.update(extra)
    return row


def bridge(x0: float, z0: float, x1: float, z1: float) -> list[dict]:
    """plank_bridge spans 6.3 m from its origin along local +Z; chained along the greybox bridge's axis."""
    import math
    dx, dz = x1 - x0, z1 - z0
    length = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(dx, dz))  # local +Z toward (x1, z1)
    rows, s = [], 0.0
    while s < length - 0.5:
        rows.append(piece("plank_bridge", x0 + dx * s / length, z0 + dz * s / length, yaw, y=0.0))
        s += 6.0
    return rows


def pieces() -> list[dict]:
    rows: list[dict] = []
    # The scale-hull deck (south), its counter on the scale_hull, the bridge to the commons.
    rows.append(piece("raft_deck", 0.0, 10.0))
    rows.append(piece("scale_hull", 0.0, 5.2, 90.0))
    rows += bridge(0.0, 0.0, 0.0, 5.0)
    # The commons: six decks lashed in two rows, the cookboats' stall, the net lanes, the roof cabin.
    for x in (-12.0, 0.0, 12.0):
        for z in (-6.0, -18.0):
            rows.append(piece("raft_deck", x, z, 0.0 if (x + z) % 24 else 180.0))
    rows.append(piece("cookboat", -19.4, -3.0, 2.0))
    rows.append(piece("stall_awning", -12.0, -9.0, 180.0))
    rows.append(piece("salvage_heap", -6.0, -2.5, 30.0))
    rows.append(piece("net_frame", 15.5, -7.0, 90.0))
    rows.append(piece("net_frame", 15.5, -11.5, 90.0))
    rows.append(piece("cabin_keelroof", -12.0, -19.0, 90.0))
    rows.append(piece("cabin_patched", 7.0, -20.5, 0.0))
    rows.append(piece("stall_awning", 3.5, -6.0, 0.0))
    # The outer mooring (west), Sadi's.
    rows.append(piece("raft_deck", -27.0, -12.0, 90.0))
    rows += bridge(-18.0, -12.0, -21.0, -12.0)
    rows.append(piece("hull_outrigger", -27.0, -19.5, 90.0))
    # The keel-hull (north), Sabe's meeting deck, and its bridge.
    rows.append(piece("keel_hull", 0.0, -34.0, 90.0))
    rows += bridge(0.0, -24.0, 0.0, -28.0)
    # Kell's second mooring (east): her chandlery over the greybox stall, the bridges there and on to the dive.
    rows += bridge(18.0, -6.0, 25.0, -6.0)
    rows.append(piece("raft_deck", 30.0, -6.0))
    rows.append(piece("chandlery", 32.5, -8.6, 90.0))
    rows += bridge(35.0, -6.0, 41.0, -6.0)
    rows.append(piece("dive_raft", 45.0, -6.0))
    # The run (C1-12/13): the planks south of the dive mooring to the net-pen, the pen and its bridge.
    rows += bridge(45.0, -10.0, 45.0, -16.0)
    rows += bridge(46.0, -17.0, 34.0, -17.0)
    rows.append(piece("net_pen", 30.0, -22.0))
    rows += bridge(18.0, -22.0, 24.0, -22.0)
    # Moored hulls between the rafts, and the far town on the horizon.
    rows.append(piece("hull_outrigger", 8.0, 2.5, 90.0))
    rows.append(piece("hull_cabin", -9.0, 6.0, 0.0))
    rows.append(piece("hull_outrigger", 22.0, -14.0, 0.0))
    rows.append(piece("town_far", -70.0, -60.0, 20.0, y=-0.45))
    rows.append(piece("town_far", 80.0, -70.0, -15.0, y=-0.45))
    return rows


def dressing() -> dict:
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/ch01/ch01_oruvel_dressing.py from env-art's Oruvel kit (M3-ENV-07); do not "
                  "edit by hand. The greybox zone's frame: x east, north = -Z.",
        "seed": 1,
        "kit_dir": "res://assets/environments/kits/oruvel/",
        "materials_dir": "res://assets/environments/kits/oruvel/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + "oruvel_ch01_environment.tres",
        "time_of_day_h": 10.5,
        "greybox": {"hide_all": True, "keep": KEEP},
        "pieces": pieces(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = json.dumps(dressing(), indent=1) + "\n"
    stale = []
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
        stale.append(OUT)
    for src, dst in COPIES.items():
        a, b = PREVIEW / src, ZONE / dst
        if not b.exists() or a.read_bytes() != b.read_bytes():
            stale.append(b)
    if args.check:
        for p in stale:
            print(f"{p.relative_to(ROOT)} is stale: run tools/ch01/ch01_oruvel_dressing.py")
        return 1 if stale else 0
    OUT.write_text(text, encoding="utf-8")
    for src, dst in COPIES.items():
        shutil.copyfile(PREVIEW / src, ZONE / dst)
    print(f"wrote {OUT.relative_to(ROOT)} and the zone's grade and water copies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
