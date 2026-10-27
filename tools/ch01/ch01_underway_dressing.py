#!/usr/bin/env python3
"""Ch1 Oruvel Underway: env-art's drowned-tower kit (M3-ENV-05) composed in the greybox rooms (M3-C01-101, ADR 0200).

Writes game/levels/ch01/oruvel_underway/oruvel_underway_dressing.json (ZoneKitDressing's layout) in the greybox zone's
frame (x east, north = -Z). The greybox lays the tower's floors side by side at y 0 (the crown, the first bell-room,
the galleries with the tin alcove, the stair lip and the gauge room off them); its walls sit on the kit's 6 m grid,
so each room is a run of the tower's own cells: floor slabs, bays on the wall lines (outer face local +Z, so yaw 0
on a south wall, 90 east, 180 north, 270 west), corner piers, and the story props on their blocks. The gameplay
stays on the greybox (collision, triggers, the shutter's curtain, the cut gauge wheel's swap). The kit preview's
ch01 frame is copied next to the zone (shipped scenes never load game/levels/_tests/). Re-run after the kit or the
rooms change:
    python3 tools/ch01/ch01_underway_dressing.py [--check]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch01" / "oruvel_underway"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_underway_kit"
OUT = ZONE / "oruvel_underway_dressing.json"
RES_ZONE = "res://game/levels/ch01/oruvel_underway/"
COPIES = {"oruvel_underway_ch01_environment.tres": "oruvel_underway_ch01_environment.tres"}
CELL = 6.0
# Story blocks the kit has no piece for stay greybox: none yet (the tin is a trigger, the low lights a GlimmerField).
KEEP: list[str] = []
BAYS = ("tower_bay", "tower_bay_broken", "tower_bay_solid")


def piece(name: str, x: float, z: float, yaw: float = 0.0, y: float = 0.0, **extra: object) -> dict:
    row: dict = {"piece": name, "at": [round(x, 3), round(z, 3)], "y": round(y, 3), "yaw_deg": round(yaw, 2)}
    row.update(extra)
    return row


def cells(x0: float, z0: float, x1: float, z1: float) -> list[tuple[float, float]]:
    """The 6 m cell centres of a room [x0, x1] x [z0, z1] (both multiples of CELL apart)."""
    nx, nz = round((x1 - x0) / CELL), round((z1 - z0) / CELL)
    return [(x0 + CELL * (i + 0.5), z0 + CELL * (k + 0.5)) for i in range(nx) for k in range(nz)]


def wall(side: str, x0: float, z0: float, x1: float, z1: float, kinds: str, skip: tuple = ()) -> list[dict]:
    """Bays along one wall line of the room; `kinds` picks per bay (b = bay, x = broken, s = solid), cycling."""
    yaw = {"s": 0.0, "e": 90.0, "n": 180.0, "w": 270.0}[side]
    if side in "sn":
        z = z1 if side == "s" else z0
        spots = [(x0 + CELL * (i + 0.5), z) for i in range(round((x1 - x0) / CELL))]
    else:
        x = x1 if side == "e" else x0
        spots = [(x, z0 + CELL * (k + 0.5)) for k in range(round((z1 - z0) / CELL))]
    rows = []
    for i, (x, z) in enumerate(spots):
        if i in skip:
            continue
        kind = BAYS["bxs".index(kinds[i % len(kinds)])]
        rows.append(piece(kind, x, z, yaw))
    return rows


def corners(x0: float, z0: float, x1: float, z1: float) -> list[dict]:
    return [piece("tower_pier", x, z) for x in (x0, x1) for z in (z0, z1)]


def floor(x0: float, z0: float, x1: float, z1: float, broken: dict | None = None, skip: tuple = ()) -> list[dict]:
    """Floor slabs (their tops at y 0); `broken` {(x, z): yaw} the collapsed cells (the tether drops)."""
    broken = broken or {}
    rows = []
    for c in cells(x0, z0, x1, z1):
        if c in skip:
            continue
        rows.append(piece("floor_slab_broken", *c, broken[c]) if c in broken else piece("floor_slab", *c))
    return rows


def crown() -> list[dict]:
    """F14, the crown: the top storey, open to the light; its walls broken along a falling line."""
    r = floor(-9, -4, 9, 20, broken={(0.0, -1.0): 90.0})
    r += wall("n", -9, -4, 9, 20, "xbx") + wall("s", -9, -4, 9, 20, "bxb")
    r += wall("w", -9, -4, 9, 20, "bxxb") + wall("e", -9, -4, 9, 20, "xbbx") + corners(-9, -4, 9, 20)
    r.append(piece("tether_line", 0.0, 0.0, block="CrownTether"))
    r += [piece("lit_fragments", -4.5, 12.0, 30.0), piece("lit_fragments", 5.0, 3.5, 200.0),
          piece("lamp_column_fallen", -6.2, 17.0, 15.0), piece("coral_head_a", 7.0, 18.2, 40.0),
          piece("coral_head_b", -7.4, -2.4, 120.0, scale=0.8), piece("seagrass_patch", 6.6, 9.0, 70.0),
          piece("seagrass_patch", -6.8, 5.5, 160.0)]
    return r


def bell_room() -> list[dict]:
    """F13, the first bell-room: sealed (blind bays), the hinge door on the north wall, the tether's slot west."""
    r = floor(34, 2, 46, 14, broken={(37.0, 5.0): 0.0})
    r += wall("n", 34, 2, 46, 14, "s", skip=(1,)) + wall("s", 34, 2, 46, 14, "s")
    r += wall("w", 34, 2, 46, 14, "s") + wall("e", 34, 2, 46, 14, "s") + corners(34, 2, 46, 14)
    r.append(piece("hinge_door", 43.0, 2.0, 180.0))
    r.append(piece("tether_line", 36.0, 3.6, y=-2.8, block="BellTether"))
    r.append(piece("lit_fragments", 42.0, 11.5, 300.0))
    return r


def galleries() -> list[dict]:
    """F9, the galleries: the colonnade of dead lamp-columns, the tin alcove west, the stair lip north-east with the
    divers' cord across the flight, and the gauge room east with its wheel and the current shaft."""
    r = floor(74, -40, 86, 20, skip=((83.0, -37.0),))
    r += wall("w", 74, -40, 86, 20, "b", skip=(6,)) + wall("e", 74, -22, 86, 20, "bbs")
    r += wall("s", 74, -40, 86, 20, "b") + wall("n", 74, -40, 86, 20, "s")
    r += [piece("tower_pier", 74.0, 20.0), piece("tower_pier", 86.0, 20.0), piece("tower_pier", 74.0, -40.0),
          piece("tower_pier", 74.0, -4.0), piece("tower_pier", 74.0, 2.0), piece("tower_pier", 86.0, -22.0)]
    for i, (x, z, yaw) in enumerate(((75.5, 10.0, 280.0), (84.5, 2.0, 24.0), (75.5, -8.0, 139.0), (84.5, -16.0, 251.0))):
        r.append(piece("lamp_column", x, z, yaw, block=f"LampColumn{i + 1}"))
    r += [piece("lamp_column_fallen", 84.6, -27.0, 205.0), piece("lit_fragments", 80.0, 6.0, 30.0),
          piece("lit_fragments", 78.5, -12.0, 200.0), piece("coral_head_b", 85.0, 12.5, 40.0, scale=0.8),
          piece("coral_head_b", 75.0, -30.6, 200.0, scale=0.7), piece("pipe_run", 85.8, 6.0, 90.0),
          piece("pipe_run", 74.2, -26.0, 90.0), piece("seagrass_patch", 76.0, 17.5, 20.0),
          piece("seagrass_patch", 84.2, -6.0, 110.0)]
    # The stair lip: the flight runs north from the lip (local +X down), the cord at the top.
    r += [piece("stair_flight", 83.0, -34.0, 90.0), piece("divers_cord", 83.0, -34.3, 90.0, block="KnottedCord")]
    # The tin alcove behind the west wall's coral curtain.
    r += floor(68, -4, 74, 2) + wall("w", 68, -4, 74, 2, "s") + wall("n", 68, -4, 74, 2, "s")
    r += wall("s", 68, -4, 74, 2, "s") + [piece("tower_pier", 68.0, -4.0), piece("tower_pier", 68.0, 2.0)]
    r += [piece("coral_curtain", 74.0, -2.5, 90.0, block="CoralCurtain"),
          piece("coral_curtain", 74.0, 0.5, 90.0, block="CoralCurtain"), piece("lit_fragments", 70.0, -1.5, 80.0)]
    # The gauge room.
    r += floor(86, -40, 104, -22) + wall("e", 86, -40, 104, -22, "s") + wall("n", 86, -40, 104, -22, "s")
    r += wall("s", 86, -40, 104, -22, "s") + [piece("tower_pier", 104.0, -40.0), piece("tower_pier", 104.0, -22.0)]
    r += [piece("gauge_wheel", 97.0, -31.0, 90.0, block="GaugeWheel"),
          piece("gauge_wheel_cut", 97.0, -31.0, 90.0, block="GaugeWheelCut"),
          piece("current_shaft", 97.0, -38.0, 11.0), piece("pipe_run", 103.8, -31.0, 90.0),
          piece("lit_fragments", 91.0, -25.0, 140.0)]
    return r


def dressing() -> dict:
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/ch01/ch01_underway_dressing.py from env-art's Oruvel Underway kit (M3-ENV-05); "
                  "do not edit by hand. The greybox zone's frame: x east, north = -Z; every room's floor at y 0.",
        "seed": 5,
        "kit_dir": "res://assets/environments/kits/oruvel_underway/",
        "materials_dir": "res://assets/environments/kits/oruvel_underway/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + "oruvel_underway_ch01_environment.tres",
        "time_of_day_h": 11.0,
        "greybox": {"hide_all": True, "keep": KEEP},
        "pieces": crown() + bell_room() + galleries(),
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
            print(f"{p.relative_to(ROOT)} is stale: run tools/ch01/ch01_underway_dressing.py")
        return 1 if stale else 0
    OUT.write_text(text, encoding="utf-8")
    for src, dst in COPIES.items():
        shutil.copyfile(PREVIEW / src, ZONE / dst)
    print(f"wrote {OUT.relative_to(ROOT)} and the zone's grade copy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
