#!/usr/bin/env python3
"""Ch6 Brine Shoals: env-art's kit (M3-ENV-02) placed on the greybox zone (M3-C06-1200, ADR 0200).

Writes game/levels/ch06/brine_shoals/brine_shoals_dressing.json (ZoneKitDressing's layout) in the greybox
zone's frame (x east, north = -Z; the road runs north up x = 0, the camp is at (0, -38), the shoal channel runs
north up x = -24 from z = -24, the dusk camp is at (24, -40)), and copies the kit preview's grade (environment,
LUT) and water look next to the zone, since shipped scenes never load game/levels/_tests/.

Every piece sits near y = 0 because the greybox collision is flat (the controller has no step-up): the hard is
sunk 1.0 m so only its shingle core shows. Story pieces carry their greybox block id, so the layout's "states"
rows show and hide them. Re-run after the kit's generators (bs_preview_layout.py, bs_zone_lut.py) change:

    python3 tools/act1/ch06_brine_shoals_dressing.py
"""
from __future__ import annotations

import json
import math
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch06" / "brine_shoals"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "brine_shoals_kit"
RES_ZONE = "res://game/levels/ch06/brine_shoals/"
CELL = 24.0
COLS = (-72.0, -48.0, -24.0, 0.0, 24.0, 48.0)  # the kit apron's hole is 6 x 8 cells
ROWS = (-84.0, -60.0, -36.0, -12.0, 12.0, 36.0, 60.0, 84.0)
APRON_DX = -24.0  # the preview's block spans x -60..84; this zone's spans -84..60
CHANNEL_X = -24.0
CHANNEL_FROM_Z = -24.0  # the channel's silted head; cells run north of it


def piece(name: str, x: float, z: float, y: float = 0.0, yaw: float = 0.0, **extra: object) -> dict:
    row: dict = {"piece": name, "at": [round(x, 3), round(z, 3)], "y": round(y, 3), "yaw_deg": round(yaw, 2)}
    row.update(extra)
    return row


def ground() -> list[dict]:
    rows = [piece("mudflat_far", APRON_DX, 0.0)]
    for i, x in enumerate(COLS):
        for j, z in enumerate(ROWS):
            if x == CHANNEL_X and z < CHANNEL_FROM_Z:
                rows.append(piece("channel_straight_a" if j % 2 == 0 else "channel_straight_b", x, z))
            else:  # the preview's a/b and yaw rotation, so no two neighbours repeat
                rows.append(piece("mudflat_patch_a" if (i + j) % 2 == 0 else "mudflat_patch_b", x, z,
                                  yaw=90.0 * ((i * 3 + j) % 4)))
    return rows


def road() -> list[dict]:
    """The plank walk up the wreck-ridges (pillar 3: the readable path), Entry to the last ridge: a gentle
    meander (one slow sine), each plank turned along it, so the boards read as one laid line."""
    rows = []
    z = 74.0
    while z > -10.0:
        x = 0.6 * math.sin(z / 14.0)
        slope = 0.6 / 14.0 * math.cos(z / 14.0)  # dx/dz
        rows.append(piece("plank_walk", x, z, y=-0.04, yaw=math.degrees(math.atan(slope))))
        z -= 3.95
    return rows


def wrecks() -> list[dict]:
    return [
        # the road's ridges (act1_ch06.md W01-W04): each sits on its greybox block's footprint
        piece("wreck_hull_section", 6.0, 55.0, yaw=90.0, block="LitAgeWreck"),
        piece("wreck_ribs_large", -6.0, 22.0, yaw=90.0, block="MiddayHull"),
        piece("wreck_hull_section", 5.5, -2.0, yaw=90.0, block="ChalkHull"),
        piece("wreck_hull_section", 4.5, -17.0, yaw=90.0, block="HoldHull"),
        piece("wreck_mast_standing", -4.5, 38.0, y=-0.05, yaw=160.0, collide=True),
        # the flats and the far side: decor off the route, with box colliders
        piece("wreck_ribs_large", -30.0, 44.0, y=-0.08, yaw=10.0, collide=True),
        piece("wreck_ribs_large", -36.0, 4.0, y=-0.08, yaw=75.0, collide=True),
        piece("wreck_mast_fallen", 34.0, 20.0, y=-0.04, yaw=20.0, collide=True),
        piece("wreck_bow", 40.0, 52.0, yaw=205.0, collide=True),
        piece("wreck_ribs_large", 44.0, -14.0, y=-0.09, yaw=140.0, collide=True),
        # the channel's silted head: a bow across the cut
        piece("wreck_bow", CHANNEL_X - 3.0, CHANNEL_FROM_Z - 1.0, y=-0.3, yaw=90.0),
    ]


def camp() -> list[dict]:
    """The Saltwright salvage camp after the Order's raid (B05-B08): burned and intact from one seed."""
    return [
        piece("camp_hard", 0.0, -38.0, y=-1.0, yaw=0.0),
        piece("camp_tent", -6.0, -29.0, y=0.1, yaw=90.0, block="Tents"),
        piece("camp_tent_burned", -11.5, -33.5, y=0.1, yaw=15.0, collide=True),
        piece("camp_tent_burned", 2.5, -45.5, y=0.05, yaw=100.0, collide=True),
        piece("salvage_rack", 6.0, -30.0, y=0.1, yaw=90.0, block="LampRacks"),
        piece("salvage_rack_burned", -1.0, -48.5, y=0.05, yaw=0.0, collide=True),
        piece("crate_stack", -8.0, -27.0, y=0.1, yaw=30.0, block="PapersTable"),
        piece("crate_stack_burned", 7.0, -40.5, y=0.08, yaw=-20.0, collide=True),
        piece("salvage_pile_burned", -2.0, -36.5, y=0.08, yaw=30.0, collide=True),
        piece("brine_vat", 3.5, -33.5, y=0.1, yaw=0.0, collide=True),
        piece("brine_vat_burned", -11.0, -45.0, y=0.05, yaw=40.0, collide=True),
        piece("branding_brazier", -6.0, -43.0, y=0.05, block="Brazier"),
        piece("liss_crate", 8.0, -18.0, y=0.05, yaw=12.0),
        # the burning hulk east of the camp, and its smoke (hidden with the Smoke block at dusk)
        piece("wreck_hull_section", 11.0, -47.0, y=0.0, yaw=0.0, block="BurningHulk"),
        piece("smoke_plume", 11.5, -45.5, y=1.2, yaw=-150.0, scale=1.0, block="Smoke"),
        piece("smoke_plume", -11.5, -33.0, y=0.6, yaw=-152.0, scale=0.7, block="Smoke"),
        piece("smoke_plume", 2.5, -45.0, y=0.6, yaw=-154.0, scale=0.55, block="Smoke"),
        # the Warden's barge in the channel (shown from the Inquisitor's yielding to Sefir's leaving)
        piece("white_barge", -22.5, -44.0, y=-0.15, yaw=90.0, block="Barge"),
    ]


def dusk_camp() -> list[dict]:
    """The high hull where the party camps at dusk (B08-B09) and the tideline below it."""
    return [
        piece("wreck_ribs_large", 24.0, -46.0, y=-0.05, yaw=0.0, collide=True),
        piece("wreck_bow", 26.5, -48.5, y=-0.2, yaw=0.0, collide=True),
        piece("tideline_wrack", 18.0, -58.0, y=0.0, yaw=2.0),
        piece("tideline_wrack", 26.0, -58.3, y=0.0, yaw=-3.0),
        piece("lamp_burial", 22.0, -58.0, y=0.0, yaw=20.0, block="Lamp"),
        # stand-ins until M3-ENV-1201's pieces: the fire's ember bed, the purser's goods (the shrine is the bow)
        piece("salvage_pile_burned", 22.0, -40.0, y=-0.25, yaw=40.0, scale=0.35, block="Fire"),
        piece("crate_stack", 29.0, -37.0, y=0.05, yaw=80.0, block="VendorBoat"),
    ]


def layout() -> dict:
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch06_brine_shoals_dressing.py from env-art's Brine Shoals kit "
        "(M3-ENV-02); do not edit by hand. The greybox zone's frame: x east, north = -Z.",
        "seed": 6,
        "kit_dir": "res://assets/environments/kits/brine_shoals/",
        "materials_dir": "res://assets/environments/kits/brine_shoals/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + "brine_shoals_environment.tres",
        "time_of_day_h": 15.5,
        # the shrine is a rest point: its greybox stands in until M3-ENV-1201
        "greybox": {"hide_all": True, "keep": ["ChalkMark", "Hatch", "Shrine"]},
        "fire_light_color": "#E0702E",
        "fire_lights": [
            {"at": [11.5, 2.4, -45.5], "energy": 1.6, "range": 9.0, "block": "Smoke"},
            {"at": [-6.0, 1.2, -43.0], "energy": 0.8, "range": 4.0},
            {"at": [22.0, 0.6, -40.0], "energy": 1.2, "range": 7.0},
        ],
        "pieces": ground() + road() + wrecks() + camp() + dusk_camp(),
    }


def copy_grade() -> None:
    """The preview's ch06 grade and water, repointed at copies next to the zone."""
    shutil.copyfile(PREVIEW / "lut_ch06_smoke.png", ZONE / "lut_ch06_smoke.png")
    if (ZONE / "lut_ch06_smoke.png.import").exists():
        imp = None  # Godot owns the copy's import file once it has imported it (its uid and cache path)
    else:
        imp = (PREVIEW / "lut_ch06_smoke.png.import").read_text(encoding="utf-8")
    if imp is not None:
        imp = re.sub(r'^(uid|path)=.*\n', "", imp, flags=re.M)  # Godot writes this copy's own uid and cache path
        imp = re.sub(r'^dest_files=.*\n', "", imp, flags=re.M)
        imp = imp.replace("res://game/levels/_tests/brine_shoals_kit/", RES_ZONE)
        (ZONE / "lut_ch06_smoke.png.import").write_text(imp, encoding="utf-8")
    env = (PREVIEW / "brine_shoals_ch06_environment.tres").read_text(encoding="utf-8")
    env = env.replace("res://game/levels/_tests/brine_shoals_kit/", RES_ZONE)
    (ZONE / "brine_shoals_environment.tres").write_text(env, encoding="utf-8")
    shutil.copyfile(PREVIEW / "brine_shoals_water_material.tres", ZONE / "brine_shoals_water_material.tres")


def main() -> None:
    (ZONE / "brine_shoals_dressing.json").write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    copy_grade()


if __name__ == "__main__":
    main()
