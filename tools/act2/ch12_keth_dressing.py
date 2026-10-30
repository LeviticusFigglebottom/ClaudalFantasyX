#!/usr/bin/env python3
"""Ch12, the Cold Road: env-art's Keth kit (keth.py, keth_zones.py; M3-ENV-717/734) on the three greybox zones
`ch12/keth_pass`, `ch12/quellan` and `ch12/cloudloom` (M4-A2P-042; keth_pass.md §6's swap map; ADR 0200).

The greybox keeps the gameplay (collision, spawns, marks, triggers, the story): every walk, wall, house and beam stays
as it is and only its look is swapped. Each zone's ground, road, walls and houses are built from the same greybox
(keth_zones.py), so their stones stand where the collision does. Nothing frozen (ADR 0015).

Writes, per zone (game/levels/ch12/<zone>/):
  <zone>_dressing.json      ZoneKitDressing's layout
  <zone>_environment.tres   the zone's grade: colour script ch12 (thin air, hard sun between cloud banks, lut_ch12_heights)
and env-art's preview of each zone (game/levels/_tests/ch12_zones/<zone>_dressed.tscn): the zone's own script and
greybox with this Dressing mounted, and ten composed cameras, until the zone mounts it.

    python3 tools/act2/ch12_keth_dressing.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_scenes as ar  # noqa: E402
import ch10_fen_dressing as fen  # noqa: E402  (the shared helpers: _put, _look_xform)
import keth_zones as kz  # noqa: E402

KIT = "res://assets/environments/kits/haluna/"
ZONES = ROOT / "game" / "levels" / "ch12"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "ch12_zones"
SEED = 12
NEVER_LOD_M = 5000.0  # a zone-built piece spans the zone: its origin's distance means nothing, keep LOD0
FAR_RIDGES_Y = -20.0
TIME_OF_DAY = {"keth_pass": 9.0, "quellan": 10.5, "cloudloom": 12.0}  # the morning climb, the town, noon at the summit
CURTAIN_X = 9.0  # each row of keth hangs in two curtains either side of the aisle (the greybox's columns 6-12 m out)

r3 = fen.r3
_put = fen._put


def _layout(zone: str) -> dict:
    return json.loads((ZONES / zone / f"{zone}_layout.json").read_text(encoding="utf-8"))


ZONE_PIECES = {"keth_pass": ("keth_pass_ground", "keth_pass_road", "keth_pass_arena"),
               "quellan": ("quellan_ground", "quellan_town", "quellan_houses_n", "quellan_houses_s"), "cloudloom": ("cloudloom_ground", "cloudloom_temple")}


def _built(zone: str) -> list[dict]:
    """The zone's greybox-built pieces (keth_zones.py), at the zone's origin."""
    return [_put(n, 0.0, 0.0, 0.0, 0.0, lod1_from_m=NEVER_LOD_M) for n in ZONE_PIECES[zone]]


def keth_pass() -> dict:
    lay = _layout("keth_pass")
    bl = {b["id"]: b for b in lay["blocks"]}
    rng = random.Random(SEED)
    pieces = _built("keth_pass")
    # The Lit Age wall behind the Ram's terrace (two 12 m modules on TerraceWall, their faces at its front).
    tw = bl["TerraceWall"]
    x0, x1, y0, _y1, _z0, z1 = kz._box(tw)
    floor_y = kz._box(bl["RamArena"])[3]
    for x in (tw["pos"][0] - 6.0, tw["pos"][0] + 6.0):
        pieces.append(_put("lit_terrace_wall", x, floor_y, z1 - 0.5, 0.0))
    pieces.append(_put("seep_pool", x0 + 3.5, floor_y, z1 + 2.8, 20.0))
    # The saddle: a cord across it under the cliff, two cairns by the road (cold_ledge is Kerrid's, under the cliff).
    sd = bl["Saddle"]
    sy = kz._box(sd)[3]
    pieces.append(_put("pass_cord", sd["pos"][0] - 1.0, sy, sd["pos"][2] + 7.5, 0.0))
    pieces.append(_put("cairn", sd["pos"][0] + 6.5, sy, sd["pos"][2] + 4.5, rng.uniform(0, 360), collide=True))
    pieces.append(_put("cairn", 86.5, sy, -35.0, rng.uniform(0, 360), collide=True))
    # The pass foot: a cairn where the road starts up, the herders' trough by the wall.
    pieces.append(_put("cairn", -4.0, 0.0, -3.8, rng.uniform(0, 360), collide=True))
    pieces.append(_put("woolback_trough", 3.4, 0.0, 4.6, 180.0, collide=True))
    pieces.append(_put("keth_far_ridges", 40.0, FAR_RIDGES_Y, -40.0, 0.0, lod1_from_m=NEVER_LOD_M))
    return {"pieces": pieces}


def quellan() -> dict:
    lay = _layout("quellan")
    bl = {b["id"]: b for b in lay["blocks"]}
    rng = random.Random(SEED + 1)
    pieces = _built("quellan")
    inn = bl["Inn"]
    pieces.append(_put("quellan_inn", inn["pos"][0], 0.0, kz._box(inn)[5], 0.0))
    w = bl["Well"]
    pieces.append(_put("quellan_well", w["pos"][0], 0.0, w["pos"][2], 0.0))
    # The square: a trough by the well, a market awning and a cairn at the road up.
    pieces.append(_put("woolback_trough", w["pos"][0] + 4.0, 0.0, w["pos"][2] + 4.0, 90.0, collide=True))
    pieces.append(_put("woven_awning", 60.5, 0.0, 15.5, 200.0, collide=True))
    pieces.append(_put("cairn", 52.0, 0.0, -18.5, rng.uniform(0, 360), collide=True))
    pieces.append(_put("cairn", -3.5, 0.0, -6.0, rng.uniform(0, 360), collide=True))
    pieces.append(_put("keth_far_ridges", 30.0, FAR_RIDGES_Y, 0.0, 70.0, lod1_from_m=NEVER_LOD_M))
    return {"pieces": pieces}


def cloudloom() -> dict:
    lay = _layout("cloudloom")
    bl = {b["id"]: b for b in lay["blocks"]}
    pieces = _built("cloudloom")
    # The keth hanging from the lattice over the open roof (thousands of cords: twelve curtains of 240).
    for z, top in kz.keth_rows(lay):
        for x in (-CURTAIN_X, CURTAIN_X):
            pieces.append(_put("keth_curtain", x, top + 0.14, z, 0.0))
    d = bl["HeskDais"]
    pieces.append(_put("hesk_dais", d["pos"][0], kz._box(d)[2], d["pos"][2], 0.0))
    pieces.append(_put("keth_far_ridges", 0.0, FAR_RIDGES_Y, -40.0, 140.0, lod1_from_m=NEVER_LOD_M))
    return {"pieces": pieces}


def layout(zone: str) -> dict:
    body = {"keth_pass": keth_pass, "quellan": quellan, "cloudloom": cloudloom}[zone]()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": f"Generated by tools/act2/ch12_keth_dressing.py from env-art's Keth kit on ch12/{zone}'s greybox "
                  "(M4-A2P-042; keth_pass.md §6). Do not edit by hand.",
        "seed": SEED,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 60.0,
        "lod_end_m": 900.0,
        "lod_margin_m": 3.0,
        "greybox": {"hide_all": True, "keep": []},
        "environment": f"res://game/levels/ch12/{zone}/{zone}_environment.tres",
        "time_of_day_h": TIME_OF_DAY[zone],
        **body,
    }


# Ten composed cameras per zone (the beat sheet's frames among them; SPEC §8.4): (name, pos, look_at, fov)
CAMERAS = {
    "keth_pass": [
        ("Foot_up", (0.0, 1.7, 4.0), (0.0, 4.0, -24.0), 55.0),
        ("Flight1_climb", (-0.5, 3.6, -16.0), (0.0, 6.5, -36.0), 55.0),
        ("Knot_post", (1.0, 7.6, -38.5), (-3.0, 7.3, -44.4), 45.0),
        ("Landing_back", (4.0, 7.7, -42.0), (-2.0, 2.0, -6.0), 55.0),
        ("Flight2_climb", (8.0, 8.1, -40.0), (34.0, 13.0, -40.0), 55.0),
        ("Ram_terrace", (52.0, 13.8, -32.5), (40.0, 14.0, -49.0), 60.0),
        ("Flight3_view", (60.0, 14.6, -41.0), (84.0, 19.5, -40.0), 55.0),
        ("K01_cold_ledge", (91.0, 19.7, -36.0), (95.0, 19.6, -47.0), 35.0),
        ("Saddle_on", (88.0, 19.8, -40.0), (110.0, 19.5, -40.0), 55.0),
        ("Over_the_pass", (-20.0, 30.0, 10.0), (40.0, 8.0, -40.0), 55.0),
    ],
    "quellan": [
        ("Q01_in", (-2.0, 3.0, 2.0), (40.0, 2.0, -2.0), 50.0),
        ("Street", (6.0, 1.7, 0.5), (30.0, 2.0, 0.0), 55.0),
        ("Inn_door", (32.0, 1.6, 4.0), (32.0, 2.6, -5.0), 55.0),
        ("Houses_south", (14.0, 1.7, -2.0), (20.0, 2.6, 6.0), 55.0),
        ("Square_well", (46.0, 1.7, 4.0), (54.0, 0.8, 10.0), 50.0),
        ("Road_up", (56.0, 1.7, 2.0), (56.0, 6.0, -30.0), 55.0),
        ("From_road_top", (56.0, 9.7, -36.0), (30.0, 2.0, 2.0), 55.0),
        ("Terrace_edge", (60.0, 1.7, 18.0), (20.0, -4.0, 40.0), 55.0),
        ("Back_lane", (30.0, 1.7, -15.0), (0.0, 2.0, -15.0), 55.0),
        ("Over_town", (30.0, 30.0, 40.0), (30.0, 0.0, 0.0), 55.0),
    ],
    "cloudloom": [
        ("Approach_up", (0.0, 1.7, 3.0), (0.0, 5.0, -20.0), 55.0),
        ("Stair_top", (0.0, 6.5, -16.0), (0.0, 8.0, -30.0), 60.0),
        ("C01_hall", (0.0, 8.0, -23.0), (0.0, 8.0, -57.0), 50.0),
        ("Aisle", (0.0, 7.6, -32.0), (0.0, 7.4, -55.0), 60.0),
        ("Under_keth", (-9.0, 7.4, -42.0), (-9.0, 11.0, -46.0), 60.0),
        ("Floor_writing", (6.0, 9.5, -36.0), (8.0, 6.0, -46.0), 60.0),
        ("Hesk_dais", (0.0, 7.6, -50.0), (0.0, 6.8, -57.5), 50.0),
        ("Up_through_roof", (2.0, 7.6, -40.0), (4.0, 20.0, -44.0), 70.0),
        ("Out_the_door", (0.0, 7.7, -48.0), (0.0, 4.0, -10.0), 55.0),
        ("Over_summit", (-30.0, 30.0, 10.0), (0.0, 6.0, -40.0), 55.0),
    ],
}
CLS = {"keth_pass": "KethPass", "quellan": "Quellan", "cloudloom": "Cloudloom"}


def write_preview(zone: str) -> Path:
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch12/ch12_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="7_cast"]', "",
             f'[node name="{CLS[zone]}" type="Node3D"]', 'script = ExtResource("1_zone")', f'location_id = &"ch12/{zone}"',
             f'layout_path = "res://game/levels/ch12/{zone}/{zone}_layout.json"', "",
             '[node name="Cast" type="Node" parent="."]', 'script = ExtResource("7_cast")', "",
             '[node name="Dressing" type="Node3D" parent="."]', 'script = ExtResource("2_dressing")',
             f'layout_path = "res://game/levels/ch12/{zone}/{zone}_dressing.json"', "",
             '[node name="Cameras" type="Node3D" parent="."]', ""]
    for name, pos, look, fov in CAMERAS[zone]:
        lines += [f'[node name="{name}" type="Camera3D" parent="Cameras"]', f"fov = {fov}", "near = 0.1", "far = 2500.0",
                  f"transform = {fen._look_xform(pos, look)}", ""]
    out = PREVIEW / f"{zone}_dressed.tscn"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    return out


def main() -> int:
    for zone in ("keth_pass", "quellan", "cloudloom"):
        out = ZONES / zone
        ar.write_environment(dict(ar.KETH_ARENA), out / f"{zone}_environment.tres")
        lay = layout(zone)
        (out / f"{zone}_dressing.json").write_text(json.dumps(lay, indent=1) + "\n", encoding="utf-8")
        write_preview(zone)
        print(f"DRESSING {zone}: {len(lay['pieces'])} pieces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
