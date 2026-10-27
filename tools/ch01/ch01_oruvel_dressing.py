#!/usr/bin/env python3
"""Ch1 Oruvel: env-art's raft-town kit (M3-ENV-07) placed on the greybox zone (M3-C01-100, ADR 0200).

Writes game/levels/ch01/oruvel/oruvel_dressing.json (ZoneKitDressing's layout) in the greybox zone's frame (x east,
north = -Z; the scale-hull south at (0, 10), the commons at (0, -12), the outer mooring west at (-27, -12), the
keel-hull north at (0, -34), Kell's second mooring east at (30, -6), the dive mooring at (45, -6), the net-pen at
(30, -22)). The greybox keeps the gameplay: its decks are flat at y 0 and the controller has no step-up, so every
kit deck is sunk by its deck height (oruvel.md: raft_deck +0.80, raft_deck_small +0.70, dive_raft +0.75, net_pen
+0.60, keel_hull +1.0, chandlery +0.5, scale_hull +0.4), which puts the hulls' waterline at SEA_Y. The kit's
preview grade and water look are copied next to the zone (shipped scenes never load game/levels/_tests/).
Story blocks the kit has no piece for stay greybox (`keep`).
Every cabin's ridge and the keel-hull's carry their open-throat lintel-gull (C1-11: every carved gull faces the sea,
which is south here as in the kit preview), at the kit's own ridge heights (env-art's ov_* modules, read-only).
The Seventh Terrace is the Brightwater ferry kit's (she is Ch4's derelict, and O07's name-board must match D06), so
she has her own dressing (oruvel_terrace_dressing.json): env-art's composition of her at the outer mooring
(oruvel_seventh_terrace_layout.json), moved to the greybox's mooring and sunk to its waterline; her pieces follow the
SeventhTerrace and NameBoard blocks, so the storm takes her. Kell's beacon is the ferry kit's lantern with a lamp.
Re-run after the kit changes:
    python3 tools/ch01/ch01_oruvel_dressing.py [--check]
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# env-art's Oruvel kit modules, read-only: the cabins' and heroes' ridge heights for the lintel-gulls.
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "oruvel"))
import ov_cabins as ocab
import ov_common as oc
import ov_heroes as oh

ZONE = ROOT / "game" / "levels" / "ch01" / "oruvel"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_kit"
OUT = ZONE / "oruvel_dressing.json"
OUT_TERRACE = ZONE / "oruvel_terrace_dressing.json"
TERRACE_PREVIEW = PREVIEW / "oruvel_seventh_terrace_layout.json"
RES_ZONE = "res://game/levels/ch01/oruvel/"
COPIES = {  # preview file -> zone file (the kit's grade and water look)
    "oruvel_ch01_environment.tres": "oruvel_ch01_environment.tres",
    "oruvel_storm_environment.tres": "oruvel_storm_environment.tres",
    "oruvel_water_material.tres": "oruvel_water_material.tres",
}
DECK = {"raft_deck": 0.80, "raft_deck_small": 0.70, "dive_raft": 0.75, "net_pen": 0.60, "keel_hull": 1.0,
        "chandlery": 0.5, "scale_hull": 0.4, "cookboat": 0.6, "hull_outrigger": 0.3, "hull_cabin": 0.5}
SEA_Y = -0.8  # the raft decks' waterline once sunk; the greybox's solid sea floor is at -1.0
KEEP = ["LowHull", "StormWall"]
GULL_YAW = -70.0  # the carving's +X out to sea (the kit preview's GULL_YAW)
GULL_JITTER = 8.0
# The Seventh Terrace: her origin (main deck amidships) at the greybox's outer mooring, clear of its deck (x -33),
# her main deck PREVIEW_DECK_Y above the water as in the preview; bow north, the name-board on her stern.
TERRACE_AT = (-36.6, -15.835)
PREVIEW_SEA_Y = 0.0
KELL_BEACON = (32.0, 3.0, -9.0)  # the greybox KellBeacon block's top: the lantern hangs from it


def piece(name: str, x: float, z: float, yaw: float = 0.0, y: float | None = None, **extra: object) -> dict:
    """A kit piece at (x, z); a deck piece sinks by its deck height unless `y` is given."""
    yy = -DECK[name] if y is None and name in DECK else (y or 0.0)
    row: dict = {"piece": name, "at": [round(x, 3), round(z, 3)], "y": round(yy, 3), "yaw_deg": round(yaw, 2)}
    row.update(extra)
    return row


def bridge(x0: float, z0: float, x1: float, z1: float) -> list[dict]:
    """plank_bridge spans 6.3 m from its origin along local +Z; chained along the greybox bridge's axis."""
    dx, dz = x1 - x0, z1 - z0
    length = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(dx, dz))  # local +Z toward (x1, z1)
    rows, s = [], 0.0
    while s < length - 0.5:
        rows.append(piece("plank_bridge", x0 + dx * s / length, z0 + dz * s / length, yaw, y=0.0))
        s += 6.0
    return rows


def local(x: float, z: float, yaw: float, lx: float, lz: float) -> tuple[float, float]:
    """World (x, z) of a piece's local (lx, lz) (Godot's Basis(UP, yaw)), as the kit preview's local()."""
    a = math.radians(yaw)
    return x + lx * math.cos(a) + lz * math.sin(a), z - lx * math.sin(a) + lz * math.cos(a)


def gull(rng: random.Random, x: float, y: float, z: float, scale: float = 1.0) -> dict:
    row = piece("lintel_gull_open", x, z, GULL_YAW + rng.uniform(-GULL_JITTER, GULL_JITTER), y=y)
    if scale != 1.0:
        row["scale"] = scale
    return row


def gulls(rows: list[dict]) -> list[dict]:
    """The lintel-gull on every cabin ridge, the chandlery's and the keel-hull's (ov_preview_layout's rules)."""
    rng = random.Random(1)
    out = []
    L, _b, D, eave, sheer = ocab.KEELROOF
    for r in rows:
        x, z, yaw, y = r["at"][0], r["at"][1], r["yaw_deg"], r["y"]
        if r["piece"] == "cabin_keelroof":
            gz = ocab.KEELROOF_GULL_Z if abs(((yaw + 180.0) % 360.0) - 180.0) < 90.0 else -ocab.KEELROOF_GULL_Z
            out.append(gull(rng, *_xyz(local(x, z, yaw, 0.0, gz), y + oc.keel_roof_ridge(gz, L, D, eave, sheer))))
        elif r["piece"] == "cabin_patched":
            out.append(gull(rng, *_xyz(local(x, z, yaw, -1.85, 0.0), y + 3.12)))
        elif r["piece"] == "chandlery":
            ridge = oh.CHANDLERY_DECK_Y + 2.22 + oh.CHANDLERY_ROOF[2] + 0.08
            out.append(gull(rng, *_xyz(local(x, z, yaw, 0.0, 0.9), y + ridge)))  # y: the chandlery's origin
        elif r["piece"] == "keel_hull":
            out.append(gull(rng, *_xyz(local(x, z, yaw, 0.0, 6.7), y + oh.KEEL_HULL_RIDGE), scale=1.35))
    return out


def _xyz(xz: tuple[float, float], y: float) -> tuple[float, float, float]:
    return xz[0], y, xz[1]


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
    return rows + gulls(rows)


def terrace() -> dict:
    """The Seventh Terrace from env-art's composition, moved onto the greybox's outer mooring, and Kell's beacon."""
    src = json.loads(TERRACE_PREVIEW.read_text(encoding="utf-8"))
    hull = next(p for p in src["pieces"] if p["piece"] == "terrace_hull")
    ox, oz, oy = hull["at"][0], hull["at"][1], hull["y"]
    dy = SEA_Y - PREVIEW_SEA_Y
    rows = []
    for p in src["pieces"]:
        x = TERRACE_AT[0] + p["at"][0] - ox
        z = TERRACE_AT[1] + p["at"][1] - oz
        block = "NameBoard" if p["piece"] == "terrace_name_board" else "SeventhTerrace"
        rows.append(piece(p["piece"], x, z, p["yaw_deg"], y=p["y"] + dy, block=block))
    rows.append(piece("ferry_lantern", KELL_BEACON[0], KELL_BEACON[2], 0.0, y=KELL_BEACON[1], block="KellBeacon"))
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/ch01/ch01_oruvel_dressing.py from env-art's Seventh Terrace at Oruvel "
                  "(game/levels/_tests/oruvel_kit/oruvel_seventh_terrace_layout.json, the Brightwater ferry kit); do "
                  f"not edit by hand. Her main deck amidships at ({TERRACE_AT[0]}, {round(oy + dy, 3)}, "
                  f"{TERRACE_AT[1]}). The zone's main Dressing hides the greybox and sets the grade.",
        "seed": 1,
        "kit_dir": src["kit_dir"],
        "materials_dir": src["materials_dir"],
        "lod1_from_m": src["lod1_from_m"],
        "lod_end_m": src["lod_end_m"],
        "lod_margin_m": src["lod_margin_m"],
        "fire_lights": [{"at": [KELL_BEACON[0], KELL_BEACON[1] - 0.25, KELL_BEACON[2]], "energy": 1.2, "range": 5.0,
                         "block": "KellBeacon"}],
        "pieces": rows,
    }


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
    outs = {OUT: json.dumps(dressing(), indent=1) + "\n", OUT_TERRACE: json.dumps(terrace(), indent=1) + "\n"}
    stale = [out for out, text in outs.items() if not out.exists() or out.read_text(encoding="utf-8") != text]
    for src, dst in COPIES.items():
        a, b = PREVIEW / src, ZONE / dst
        if not b.exists() or a.read_bytes() != b.read_bytes():
            stale.append(b)
    if args.check:
        for p in stale:
            print(f"{p.relative_to(ROOT)} is stale: run tools/ch01/ch01_oruvel_dressing.py")
        return 1 if stale else 0
    for out, text in outs.items():
        out.write_text(text, encoding="utf-8")
    for src, dst in COPIES.items():
        shutil.copyfile(PREVIEW / src, ZONE / dst)
    print(f"wrote {OUT.relative_to(ROOT)}, {OUT_TERRACE.relative_to(ROOT)} and the zone's grade and water copies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
