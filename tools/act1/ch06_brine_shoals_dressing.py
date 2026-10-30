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


# The Level-stone's kit slot is a flat pale StandardMaterial that read as white plastic on the flats (M3-ENV-1326); it
# takes the Order's shrine stone, as Haluna's shrines wear it.
LEVEL_STONE_NAME = "brine_shoals_level_stone_material.tres"
LEVEL_STONE = {"bs_level_stone": RES_ZONE + LEVEL_STONE_NAME}
# ... in the shrine stone toned down for the flats (the 10-29 audit: in Haluna's bright shrine stone it still read as a
# white cube at the shrine): weathered grey and salt-stained (Ch8's borrowed shrine takes the same file).
LEVEL_STONE_SRC = "res://assets/environments/kits/haluna/materials/kit_shrine_stone.tres"
LEVEL_STONE_OVERRIDES = {"col_tint": "Color(0.64, 0.66, 0.64, 1)", "use_salt": "true", "variation_value": "0.2"}


# The kit's flat StandardMaterial metals and lacquer (M3-ENV-1326): the camp's brass, gold and iron and the barge's
# lacquer read as plastic. Zone looks by slot on every Brine Shoals piece (`kit_material_paths`).
KIT_LOOKS = {
    "bs_lacquer_red": ("brine_shoals_lacquer_red_material.tres", None),
    "bs_brass": ("brine_shoals_brass_material.tres", None),
    "bs_gold": ("brine_shoals_gold_material.tres", None),
    "bs_iron": ("brine_shoals_iron_material.tres", None),
}


def kit_looks() -> dict:
    import ch05_09_zone_looks as zl  # noqa: PLC0415

    return {
        "bs_lacquer_red": zl.lacquer((0.702, 0.149, 0.1176)),
        "bs_brass": dict(zl.NEW_COPPER, col_bronze=(0.5490, 0.4235, 0.2353), col_worn=(0.7804, 0.6353, 0.3922),
                         patina_coverage=(0.05, 0.4)),
        "bs_gold": dict(zl.GOLD),
        "bs_iron": dict(zl.SEA_IRON),
    }


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
        # the burning hulk east of the camp (its smoke is SMOKES')
        piece("wreck_hull_section", 11.0, -47.0, y=0.0, yaw=0.0, block="BurningHulk"),
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
        # M3-ENV-1201's pieces on their blocks: the party's fire, the purser's boat, the Level-stone shrine in the bow
        piece("ridge_fire", 22.0, -40.0, y=0.0, block="Fire"),
        piece("vendor_boat", 29.0, -37.0, y=0.0, block="VendorBoat"),
        piece("level_stone_shrine", 27.0, -44.5, y=0.0, block="Shrine", material_paths=dict(LEVEL_STONE)),
    ]


def story_marks() -> list[dict]:
    """M3-ENV-1201's pieces for the raid: the burning tide-wheel (W14's two-shot), the chalk sign on the hull (B02) and
    the hold's hatch in its side (B03), each on its block (the chalk mark and the hatch are centred on theirs)."""
    return [
        piece("tide_wheel_burned", 9.0, -36.0, y=0.0, block="TideWheel"),
        piece("chalk_mark", 4.45, -2.0, y=1.2, block="ChalkMark"),
        piece("hatch", 3.45, -17.0, y=0.7, block="Hatch"),
    ]


HALUNA = "res://assets/environments/kits/haluna/"
# What the raid left strewn on the flats either side of the plank road (env-art's note from viewing ch06_brine_road, and
# the shoals arena's mix): (piece, kit_dir or "", sink m, collides)
AFTERMATH = (("net_heap", HALUNA, 0.05, False), ("tide_debris", HALUNA, 0.0, False), ("crate_stack", "", 0.05, True),
             ("rope_coil", HALUNA, 0.0, False), ("cargo_sacks", HALUNA, 0.05, True), ("tideline_wrack", "", 0.0, False),
             ("salvage_pile", "", 0.1, True), ("tide_debris", HALUNA, 0.0, False), ("vendor_boat", "", 0.25, True))
AFTERMATH_CLEAR_M = 2.5  # off every story point (marks, actors, spawns, triggers)


# The raid's flames (M3-ENV-1313, B02-B04 "by the burning hulk"): the kit's b_fire.py pieces at the burning hulk and
# the tide-wheel's foot, on the Smoke block, so they go out with the smoke when the evening camp is made
RAID_FIRES = (("camp_fire_large", 11.0, -46.0, 30.0), ("camp_fire_small", 13.6, -44.6, 200.0),
              ("camp_fire_small", 8.4, -45.4, 110.0), ("camp_fire_large", 9.6, -35.2, 300.0))


def raid_fires() -> list[dict]:
    return [piece(name, x, z, yaw=yaw, block="Smoke") for name, x, z, yaw in RAID_FIRES]


# The camp's smoke (M3-RND-21): Rendering's volumetric columns (SmokeColumn, the "camp" profile) where the kit's
# smoke_plume shells stood, in their frame (+X downwind, the same yaw and scale), off the burning hulk and the two
# burned tents; hidden with the Smoke block at dusk. (name, x, y, z, yaw, scale, seed)
SMOKES = (("SmokeHulk", 11.5, 1.2, -45.5, -150.0, 1.0, 0.0), ("SmokeTentWest", -11.5, 0.6, -33.0, -152.0, 0.7, 0.37),
          ("SmokeTentSouth", 2.5, 0.6, -45.0, -154.0, 0.55, 0.71))


def smokes() -> list[dict]:
    return [{"name": n, "at": [x, y, z], "yaw_deg": yaw, "scale": s, "profile": "camp", "seed": sd, "block": "Smoke"}
            for n, x, y, z, yaw, s, sd in SMOKES]


def road_aftermath() -> list[dict]:
    import random

    rng = random.Random(61)
    g = json.loads((ZONE / "brine_shoals_layout.json").read_text(encoding="utf-8"))
    keep = [v[:3] for v in list(g.get("marks", {}).values()) + list(g.get("spawns", {}).values())]
    keep += [a["at"][:3] for a in g.get("actors", {}).values()] + [t["at"][:3] for t in g.get("triggers", [])]
    blocks = [b for b in g["blocks"] if b.get("solid", True) is not False and b["pos"][1] > 0.2]
    rows = []
    z, k = 70.0, 0
    while z > 2.0:
        for side in (-1.0, 1.0):
            name, kit, sink, collides = AFTERMATH[k % len(AFTERMATH)]
            k += 1
            x = side * rng.uniform(3.5, 9.0) + 0.6 * math.sin(z / 14.0)
            zz = z + rng.uniform(-2.0, 2.0)
            if any(math.hypot(x - p[0], zz - p[2]) < AFTERMATH_CLEAR_M for p in keep):
                continue
            if any(abs(x - b["pos"][0]) < b["size"][0] * 0.5 + 1.5 and abs(zz - b["pos"][2]) < b["size"][2] * 0.5 + 1.5
                   for b in blocks):
                continue
            extra: dict = {"collide": True} if collides else {}
            if kit:
                extra.update(kit_dir=kit, materials_dir=kit + "materials/")
            rows.append(piece(name, x, zz, y=-sink, yaw=rng.uniform(0.0, 360.0), **extra))
        z -= rng.uniform(6.0, 9.0)
    return rows


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
        "greybox": {"hide_all": True, "keep": []},
        "fire_light_color": "#E0702E",
        "fire_lights": [
            {"at": [11.5, 2.4, -45.5], "energy": 1.6, "range": 9.0, "block": "Smoke"},
            {"at": [-6.0, 1.2, -43.0], "energy": 0.8, "range": 4.0},
            {"at": [22.0, 0.6, -40.0], "energy": 1.2, "range": 7.0},
            {"at": [9.0, 2.4, -35.0], "energy": 1.4, "range": 7.0, "block": "TideWheel"},  # the burning wheel
            {"at": [27.0, 1.2, -44.0], "energy": 0.6, "range": 3.0, "color": "#9fd8e0", "block": "Shrine"},  # rest
        ],
        "kit_material_paths": {slot: RES_ZONE + name for slot, (name, _) in KIT_LOOKS.items()},
        "pieces": ground() + road() + wrecks() + camp() + dusk_camp() + story_marks() + road_aftermath()
        + raid_fires(),
        "smokes": smokes(),
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
    (ZONE / "brine_shoals_environment.tres").write_text(zone_fog(env), encoding="utf-8")
    shutil.copyfile(PREVIEW / "brine_shoals_water_material.tres", ZONE / "brine_shoals_water_material.tres")


# The zone's haze (env-art-b's beauty pass, 10-30): the preview's volumetric fog (0.02 over 80 m, sky untouched) capped
# the far flats in a flat brown band under a pale sky. Thinner volumetric fog, and a depth fog that takes the sky's
# colour (aerial perspective) and lies low over the flats, let the shoals fade into the sea light instead.
ZONE_FOG = {
    "fog_light_color": "Color(0.78, 0.74, 0.66, 1)",
    "fog_sun_scatter": "0.25",
    "fog_density": "0.008",
    "fog_aerial_perspective": "0.9",
    "fog_sky_affect": "0.45",
    "fog_height": "1.5",
    "fog_height_density": "0.12",
    "volumetric_fog_density": "0.007",
}


def zone_fog(env: str) -> str:
    """The preview's environment with ZONE_FOG set: each key replaces its line, or is added after fog_enabled."""
    for key, value in ZONE_FOG.items():
        line = f"{key} = {value}"
        env, n = re.subn(rf"^{key} = .*$", line, env, flags=re.M)
        if n == 0:
            env = re.sub(r"^fog_enabled = true$", lambda m, add=line: m.group(0) + "\n" + add, env, count=1, flags=re.M)
    return env


def main() -> None:
    (ZONE / "brine_shoals_dressing.json").write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    import ch05_09_zone_looks as zl  # noqa: PLC0415

    (ZONE / LEVEL_STONE_NAME).write_text(zl.copy_material(LEVEL_STONE_SRC, LEVEL_STONE_NAME, LEVEL_STONE_OVERRIDES),
                                         encoding="utf-8")
    looks = kit_looks()
    for slot, (name, _) in KIT_LOOKS.items():
        (ZONE / name).write_text(zl.bronze_material(name, looks[slot]), encoding="utf-8")
    copy_grade()


if __name__ == "__main__":
    main()
