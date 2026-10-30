#!/usr/bin/env python3
"""Ch7 Tamsule port: env-art's port pieces (M3-C07-04, the Tamsule Bell kit's market.py) dress ch07/tamsule (ADR 0200).

The frame is the greybox zone's (x east, north -Z, the decks' tops at y 0, the river 1.6 m under them), which is also
the frame of env-art's port preview (assets_src/environments/kits/tamsule_bell/port_preview.py). Its `pieces()` are
the source: every greybox block dressed at its place, and the Bell's whole ring on its axis at (0, -1.6, -75), north of
the gantry foot (the galleries reach r 41, so the greybox stand-in's z -40 would cover the gantry foot).

Writes next to the zone (game/levels/ch07/tamsule/):
  tamsule_dressing.json    ZoneKitDressing's layout: the preview's rows, story pieces on their blocks, the Ch7 noon
                           grade (the galleries' copy of the Bell kit preview's).
  tamsule_collision.json   KitCollision's blocks: a rail along every open edge of the walkable decks and bridges
                           (the greybox let a player step off into a river floor 0.6 m above the water), and a floor
                           under the river.
With --relayout it also moves the layout's Bell-side story points once (the Bell is 35 m further north) and gives the
zone the galleries' sun, and sets the layout's collision_path.

    python3 tools/act1/ch07_tamsule_port_dressing.py [--relayout]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "tamsule_bell"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ch05_09_zone_looks as zl  # noqa: E402
import bell  # noqa: E402
import port_preview as pp  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch07" / "tamsule"
LAYOUT = ZONE / "tamsule_layout.json"
GALLERIES = ROOT / "game" / "levels" / "ch07" / "tamsule_bell_galleries" / "tamsule_bell_galleries_layout.json"
RES_ZONE = "res://game/levels/ch07/tamsule/"
RES_GALLERIES = "res://game/levels/ch07/tamsule_bell_galleries/"
KIT = pp.KIT
CW = pp.CW
OTHER_KIT = {"trader_boat": CW}
# Corrow's canvas on the trader's sail and bales (M3-ENV-1326; written by ch08_corrow_dressing.py)
OTHER_SLOTS = {"trader_boat": {"cw_sail": "res://game/levels/ch08/corrow/corrow_canvas_material.tres"},
               "trader_cargo": {"cw_sail": "res://game/levels/ch08/corrow/corrow_canvas_material.tres"}}
# The trader's deck cargo as lashed bales over the boat's box bales (M3-ENV-1326, Corrow's b_cargo.py)
RIDERS = {"trader_boat": "trader_cargo"}
# Story pieces that follow a greybox block (hide_block / show_block / states drive them).
BLOCKS = {"Trader": "Trader", "StallA": "MarketStallA", "StallB": "MarketStallB"}
WATER_Y = pp.WATER_Y
DECK_TOP_Y = 0.0
RAIL_H = 1.1
RAIL_T = 0.25
RIVER_FLOOR_Y = WATER_Y - 1.4  # under the water, so a boat's draught never meets it
EDGE_EPS = 0.05
BELL_AXIS = pp.BELL_AT
# --relayout: the story points that look at or stand by the Bell, onto the kit's ring (the moorings nearest the port).
BELL_MOORINGS = (7.0, 0.0, -53.3)


def r3(v: float) -> float:
    return round(float(v), 3)


def rows() -> list[dict]:
    out = []
    for name, piece, (x, y, z), yaw, scale in pp.pieces():
        row: dict = {"name": name, "piece": piece, "at": [r3(x), r3(z)], "y": r3(y), "yaw_deg": r3(yaw)}
        if scale != 1.0:
            row["scale"] = r3(scale)
        if piece in OTHER_KIT:
            row["kit_dir"] = OTHER_KIT[piece]
            row["materials_dir"] = OTHER_KIT[piece] + "materials/"
        if piece in OTHER_SLOTS:
            row["material_paths"] = dict(OTHER_SLOTS[piece])
        if name in BLOCKS:
            row["block"] = BLOCKS[name]
        out.append(row)
        if piece in RIDERS:  # a piece riding on this one at its transform (the trader's lashed bales)
            out.append(dict(row, name=name + "_" + RIDERS[piece], piece=RIDERS[piece]))
    return out


# The Bell's weeping column seen from the port (M3-ENV-1321): the kit's weep_column (the galleries' piece) under the
# kit's Bell at BELL_AXIS, as the galleries stand it under theirs, dressed with the galleries' column materials
# (tools/act1/ch07_tamsule_bell_dressing.py writes them). The layout's BellColumn block is the greybox's (z -40, before
# the Bell moved to its ring); the column follows it only for show/hide.
WEEP_SLOTS = {"tb_drop_proxy": "weep_column_water_material", "tb_salt_glass": "weep_spray_water_material"}


def weep_rows() -> list[dict]:
    return [{"name": "WeepColumn", "piece": "weep_column", "at": [r3(BELL_AXIS[0]), r3(BELL_AXIS[2])],
             "y": r3(BELL_AXIS[1] + bell.POOL_WATER_Y), "yaw_deg": 0.0, "kit_dir": KIT, "materials": dict(WEEP_SLOTS),
             "materials_dir": RES_GALLERIES}]


# The held drop over it (M3-RND-26): the galleries' WaterSphereRig profile on the kit's SphereAnchor under this Bell.
def drop_rows() -> list[dict]:
    return [{"name": "Drop", "at": [r3(a + c) for a, c in zip(BELL_AXIS, bell.DROP_CENTER)],
             "profile": "tamsule_drop"}]


def galleries_env() -> tuple[str, float]:
    d = json.loads((ROOT / "game" / "levels" / "ch07" / "tamsule_bell_galleries"
                    / "tamsule_bell_galleries_dressing.json").read_text(encoding="utf-8"))
    return d["environment"], float(d["time_of_day_h"])


def layout() -> dict:
    env, tod = galleries_env()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch07_tamsule_port_dressing.py from env-art's Tamsule port preview "
        "(port_preview.py, M3-C07-04); do not edit by hand. The greybox zone's frame: x east, north = -Z.",
        "seed": 71,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "environment": env,
        "time_of_day_h": tod,
        "greybox": {"hide_all": True, "keep": []},
        "kit_material_paths": dict(KIT_SLOTS),
        "pieces": rows() + weep_rows(),
        "drops": drop_rows(),
    }


# ---------------------------------------------------------------------------------------------
# Collision: rails on the decks' open edges
# ---------------------------------------------------------------------------------------------
def walk_rects(blocks: list[dict]) -> list[tuple[float, float, float, float]]:
    """The walkable deck tops (solid, unrotated, top at the deck datum) as (x0, x1, z0, z1)."""
    out = []
    for b in blocks:
        if b.get("solid", True) is False or b.get("yaw", 0.0):
            continue
        (x, y, z), (sx, sy, sz) = b["pos"], b["size"]
        if abs(y + sy * 0.5 - DECK_TOP_Y) > EDGE_EPS or sy > 2.0:
            continue
        out.append((x - sx * 0.5, x + sx * 0.5, z - sz * 0.5, z + sz * 0.5))
    return out


def _subtract(seg: tuple[float, float], cuts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    parts = [seg]
    for c0, c1 in cuts:
        nxt = []
        for a, b in parts:
            if c1 <= a or c0 >= b:
                nxt.append((a, b))
                continue
            if c0 > a:
                nxt.append((a, c0))
            if c1 < b:
                nxt.append((c1, b))
        parts = nxt
    return [(a, b) for a, b in parts if b - a > 0.2]


def edge_rails(rects: list[tuple[float, float, float, float]]) -> list[dict]:
    """A rail just outside every stretch of a deck's edge that no other deck continues."""
    rails = []
    n = 0
    for i, (x0, x1, z0, z1) in enumerate(rects):
        others = [r for j, r in enumerate(rects) if j != i]
        for side, fixed in (("n", z0), ("s", z1)):
            probe = fixed - EDGE_EPS if side == "n" else fixed + EDGE_EPS
            cuts = [(a0, a1) for a0, a1, b0, b1 in others if b0 <= probe <= b1]
            for a, b in _subtract((x0, x1), cuts):
                off = -RAIL_T * 0.5 if side == "n" else RAIL_T * 0.5
                rails.append({"id": f"Rail{n}", "pos": [r3((a + b) * 0.5), r3(RAIL_H * 0.5), r3(fixed + off)],
                              "size": [r3(b - a), RAIL_H, RAIL_T], "solid": True, "visible": False})
                n += 1
        for side, fixed in (("w", x0), ("e", x1)):
            probe = fixed - EDGE_EPS if side == "w" else fixed + EDGE_EPS
            cuts = [(b0, b1) for a0, a1, b0, b1 in others if a0 <= probe <= a1]
            for a, b in _subtract((z0, z1), cuts):
                off = -RAIL_T * 0.5 if side == "w" else RAIL_T * 0.5
                rails.append({"id": f"Rail{n}", "pos": [r3(fixed + off), r3(RAIL_H * 0.5), r3((a + b) * 0.5)],
                              "size": [RAIL_T, RAIL_H, r3(b - a)], "solid": True, "visible": False})
                n += 1
    return rails


def collision(blocks: list[dict]) -> dict:
    return {
        "_about": "Generated by tools/act1/ch07_tamsule_port_dressing.py (ADR 0200); do not edit by hand.",
        "blocks": [{"id": "RiverFloor", "pos": [0.0, r3(RIVER_FLOOR_Y - 0.5), 0.0], "size": [400.0, 1.0, 400.0],
                    "visible": False}] + edge_rails(walk_rects(blocks)),
    }


def relayout(text: str) -> str:
    """Once, as line edits so the hand-written layout keeps its form: the River block stops being a floor (the
    collision file's rails keep the player on the decks, its floor lies under the water), the Bell's mark and T09
    move onto the kit's ring, the zone takes the galleries' Ch7 noon sun and environment, and the collision file."""
    gal = json.loads(GALLERIES.read_text(encoding="utf-8"))
    bx, by, bz = BELL_MOORINGS
    subs = [
        (r'(\{"id": "River", [^\n]*?"color": "#3a7c8a")\}', r'\1, "solid": false}'),
        (r'"bell_moorings": \[[^\]]*\]', f'"bell_moorings": [{bx}, {by}, {bz}, 0]'),
        (r'("T09": \{[^\n]*?"look_at": )\[[^\]]*\]', rf'\g<1>[{bx}, 0.6, {bz}]'),
        (r'"sun": \{[^\n]*\}', '"sun": ' + json.dumps(gal["sun"])),
        (r'"environment": \{[^\n]*\},', '"environment": ' + json.dumps(gal["environment"]) + ',\n  "collision_path": "'
         + RES_ZONE + 'tamsule_collision.json",'),
    ]
    for pat, rep in subs:
        text, n = re.subn(pat, rep, text, count=1)
        if n != 1:
            raise SystemExit(f"relayout: no match for {pat}")
    return text


# The kit's gilt (`tb_gold_leaf`, the boards' and counters' edges, the Bell's ring trim) is a flat StandardMaterial: worn
# gilt by slot on every Tamsule piece in both Ch7 zones (M3-ENV-1326; the galleries' dressing names the same file).
GOLD_NAME = "tamsule_gold_leaf_material.tres"
GOLD = {"col_bronze": (0.8314, 0.6431, 0.2157), "col_worn": (0.5490, 0.3922, 0.1961),
        "col_patina": (0.3725, 0.5412, 0.4706), "col_patina_pale": (0.5216, 0.6588, 0.5843),
        "metallic_bronze": 1.0, "roughness_bronze": 0.28, "roughness_worn": 0.45, "patina_coverage": (0.0, 0.15),
        "patina_shade_bias": 0.1, "patina_roughness": 0.85, "streak_strength": 0.2, "wear_strength": 0.6,
        "detail_scale_m": 0.5, "normal_strength": 0.3, "normal_tile_m": 1.6}
# The kit's dyed cloths (the stalls' awnings, the boats' canopies and sun umbrellas) are 92 % flat paint over the weave:
# at walk range they read as flat colour (the player-height walk, 10-30). The zone's copies let the weave show
# through a sun-faded dye.
CLOTHS = ("tb_cloth_faded_teal", "tb_cloth_indigo", "tb_cloth_red", "tb_cloth_sand", "tb_cloth_sea_blue")
CLOTH_LOOK = {"paint_cover": "0.7", "normal_strength": "1.0", "tile_m": "Vector2(0.35, 0.35)"}
CLOTH_KIT = "res://assets/environments/kits/tamsule_bell/materials/"


def cloth_name(slot: str) -> str:
    return "tamsule_" + slot.removeprefix("tb_") + "_material.tres"


KIT_SLOTS = {"tb_gold_leaf": "res://game/levels/ch07/tamsule/" + GOLD_NAME,
             **{c: "res://game/levels/ch07/tamsule/" + cloth_name(c) for c in CLOTHS}}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--relayout", action="store_true")
    args = ap.parse_args(argv)
    if args.relayout:
        LAYOUT.write_text(relayout(LAYOUT.read_text(encoding="utf-8")), encoding="utf-8")
    data = json.loads(LAYOUT.read_text(encoding="utf-8"))
    (ZONE / "tamsule_dressing.json").write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    (ZONE / GOLD_NAME).write_text(zl.bronze_material(GOLD_NAME, GOLD), encoding="utf-8")
    for c in CLOTHS:
        (ZONE / cloth_name(c)).write_text(zl.copy_material(CLOTH_KIT + c + ".tres", cloth_name(c).removesuffix(".tres"),
                                                           CLOTH_LOOK), encoding="utf-8")
    (ZONE / "tamsule_collision.json").write_text(json.dumps(collision(data["blocks"]), indent=1) + "\n",
                                                 encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
