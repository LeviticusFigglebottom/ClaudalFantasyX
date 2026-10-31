#!/usr/bin/env python3
"""Ch10, the Fen of the Kirru: env-art's fen kit (ossa_fen.py, reedhollow.py, fen_zones.py; M3-ENV-718/733) on the two
greybox zones `ch10/ossa_fen` and `ch10/reedhollow` (M4-A2P-040; ossa_fen.md §4's swap map; ADR 0200).

The greybox keeps the gameplay (collision, spawns, marks, triggers, the story): every walk, rail, trunk, platform and
house block stays as it is and only its look is swapped. The ground is the zone's own heightfield (fen_zones.py, built
from the same greybox), so nothing here moves a walking surface.

Writes, per zone (game/levels/ch10/<zone>/):
  <zone>_dressing.json         ZoneKitDressing's layout: the walks tiled with their 6 m pieces, the platforms and
                               roosts, the clutch's stone and the name-shell cords, the mangrove system (the greybox's
                               trunks, then the channels' own trees in four variants), reed beds in the slack water and
                               the far tree-line.
  <zone>_environment.tres      the zone's grade: colour script ch10 (18:20 overcast dusk, lut_ch10_fen), the arena's sky.
  <zone>_water_material.tres   the tannin_fen water (brown-black tea, caustics off).
and env-art's preview of each zone (game/levels/_tests/ossa_fen_kit/<zone>_dressed.tscn): the zone's own script and
greybox with the Water, the Tide and this Dressing mounted, and ten composed cameras, until the zone mounts it.

    python3 tools/act2/ch10_fen_dressing.py
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(KIT_SRC))
import arena_scenes as ar  # noqa: E402
sys.path.insert(0, str(KIT_SRC.parent.parent))
import zone_edges  # noqa: E402
import ossa_fen as of  # noqa: E402
import reedhollow as rh  # noqa: E402

KIT = "res://assets/environments/kits/haluna/"
ZONES = ROOT / "game" / "levels" / "ch10"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "ossa_fen_kit"
WATER_Y = of.WATER_Y
LUT = "res://assets/environments/arenas/ossa_fen_roots/lut_ch10_fen.png"

TREE_CLEAR_M = 3.4  # a mangrove's foot this far off a walk's centre line at least (its root cage reaches ~3 m)
TREE_MIN_GAP_M = 1.2  # never closer than this to a walk's edge (the root cage's reach past its foot is ~3 m)
TREE_WALK_GAP_M = 5.0  # the channels' own trees: this far from any walk, platform or land
REED_GAP_M = 3.0
# Where the field camera settles at Ossa Fen's spawns, (camera xz, leader xz), measured headless (walk_stills' arrival):
# no living tree within CAMERA_LINE_GAP_M of the line, so no trunk or limb stands in the lens (DrownerArena's did).
# Re-measure if the field camera's spawn rules change.
CAMERA_LINES = {"FenEdge": ((-8.0, 8.13), (-8.0, 0.0)), "FromReedhollow": ((116.0, 0.0), (134.0, 0.0)),
                "DrownerArena": ((101.05, -7.97), (104.0, 0.0))}
CAMERA_LINE_GAP_M = 4.5
VARIANTS = (("mangrove_tree", 0.30), ("mangrove_tall", 0.20), ("mangrove_low", 0.30), ("mangrove_young", 0.20))
SEED = 10
ZONE_FILL = 0.85


CARVER_AT = (66.8, 2.8)  # Reedhollow's shore, behind the clutch, clear of the ground's fallen poles


def r3(v: float) -> float:
    return round(float(v), 3)


def _layout(zone: str) -> dict:
    return json.loads((ZONES / zone / f"{zone}_layout.json").read_text(encoding="utf-8"))


def _put(piece: str, x: float, y: float, z: float, yaw: float, **kw) -> dict:
    row = {"piece": piece, "at": [r3(x), r3(z)], "y": r3(y), "yaw_deg": r3(yaw)}
    row.update(kw)
    return row


def _axes(b: dict) -> tuple[tuple[float, float], tuple[float, float]]:
    """A block's local +X and +Z on the ground, for Godot's rotation_degrees.y = yaw."""
    a = math.radians(float(b.get("yaw", 0.0)))
    return (math.cos(a), -math.sin(a)), (math.sin(a), math.cos(a))


def _strips(lay: dict, prefixes: tuple[str, ...]) -> list[dict]:
    return [b for b in lay["blocks"] if b["id"].startswith(prefixes) and "Rail" not in b["id"] and "Trunk" not in b["id"]
            and "Bound" not in b["id"] and b["size"][2] == 3.6]


def tile_strip(b: dict, piece: str) -> list[dict]:
    """A strip tiled along its length with 6 m pieces, the last one pulled back to end flush (it overlaps its
    neighbour, never overhangs the block)."""
    length = float(b["size"][0])
    n = max(1, math.ceil(length / rh.STRIP_LEN - 1e-6))
    (ax, az), _ = _axes(b)
    x0, z0 = b["pos"][0], b["pos"][2]
    out = []
    for k in range(n):
        c = -length / 2 + rh.STRIP_LEN / 2 + min(k * rh.STRIP_LEN, length - rh.STRIP_LEN)
        out.append(_put(piece, x0 + ax * c, 0.0, z0 + az * c, float(b.get("yaw", 0.0)) + (180.0 if k % 2 else 0.0)))
    return out


def _segments(lay: dict) -> list[tuple[tuple[float, float], tuple[float, float], float]]:
    """Every walkable strip and platform as a segment (a, b, half width) on the ground."""
    segs = []
    for b in lay["blocks"]:
        if "Rail" in b["id"] or "Trunk" in b["id"] or "Bound" in b["id"] or b["id"] in ("Water", "Bed"):
            continue
        if b["pos"][1] > 0.0 or b["size"][1] > 1.5:
            continue  # houses, roots and the stone stand, they are not walked
        (ax, az), (bx, bz) = _axes(b)
        hx, hz = b["size"][0] / 2, b["size"][2] / 2
        x, z = b["pos"][0], b["pos"][2]
        if hx >= hz:
            segs.append(((x - ax * hx, z - az * hx), (x + ax * hx, z + az * hx), hz))
        else:
            segs.append(((x - bx * hz, z - bz * hz), (x + bx * hz, z + bz * hz), hx))
    return segs


def _seg_dist(p, a, b) -> float:
    ax, az = a
    bx, bz = b
    px, pz = p
    dx, dz = bx - ax, bz - az
    t = 0.0 if dx == dz == 0 else max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / (dx * dx + dz * dz)))
    return math.hypot(px - (ax + dx * t), pz - (az + dz * t))


def clear_of(p, segs, gap: float) -> bool:
    return all(_seg_dist(p, a, b) - hw > gap for a, b, hw in segs)


def off_camera_lines(piece: dict) -> bool:
    """A tree clear of every spawn's camera line (CAMERA_LINES)."""
    p = (piece["at"][0], piece["at"][1])
    return all(_seg_dist(p, a, b) > CAMERA_LINE_GAP_M for a, b in CAMERA_LINES.values())


def _variant(rng: random.Random) -> str:
    r, acc = rng.random(), 0.0
    for name, w in VARIANTS:
        acc += w
        if r <= acc:
            return name
    return VARIANTS[-1][0]


def trunk_trees(lay: dict, rng: random.Random) -> list[dict]:
    """The greybox's *Trunk* blocks become mangroves, pushed out to TREE_CLEAR_M off their walk's centre line so the
    root cage stays off the walk (the trunk block keeps its collision where it stands)."""
    walks = {b["id"]: b for b in lay["blocks"] if not any(s in b["id"] for s in ("Rail", "Trunk", "Bound"))}
    out = []
    for b in lay["blocks"]:
        if "Trunk" not in b["id"]:
            continue
        owner = walks.get(b["id"].split("Trunk")[0])
        x, z = b["pos"][0], b["pos"][2]
        if owner is not None:
            _, (nx, nz) = _axes(owner)
            ox, oz = owner["pos"][0], owner["pos"][2]
            off = (x - ox) * nx + (z - oz) * nz
            push = math.copysign(max(abs(off), TREE_CLEAR_M + rng.uniform(0.0, 1.5)), off or 1.0) - off
            x, z = x + nx * push, z + nz * push
        # Where two walks meet, the push off one can land on the other: step away from whichever is nearest.
        strips = [sg for sg in _segments(lay) if sg[2] < 5.0]
        for _ in range(8):
            d, (a, b, _hw) = min((_seg_dist((x, z), a, b) - hw, (a, b, hw)) for a, b, hw in strips)
            if d >= TREE_CLEAR_M - rh.HALF_W:
                break
            px, pz = _closest((x, z), a, b)
            ux, uz = x - px, z - pz
            n = math.hypot(ux, uz) or 1.0
            step = TREE_CLEAR_M - rh.HALF_W - d + 0.3
            x, z = x + ux / n * step, z + uz / n * step
        if not clear_of((x, z), strips, TREE_MIN_GAP_M):
            continue  # squeezed between two walks (or a walk and a platform): no tree; its block is behind the rails
        out.append(_put(_variant(rng), x, 0.0, z, rng.uniform(0.0, 360.0), scale=r3(rng.uniform(0.85, 1.15))))
    return out


def _closest(p, a, b) -> tuple[float, float]:
    ax, az = a
    dx, dz = b[0] - ax, b[1] - az
    t = 0.0 if dx == dz == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - az) * dz) / (dx * dx + dz * dz)))
    return ax + dx * t, az + dz * t


def channel_trees(lay: dict, rng: random.Random, area, count: int, segs, lands) -> list[dict]:
    """The mangrove system: trees across the channels, on their own root-mats, away from every walk and the land,
    clumped (a seed tree, then two or three round it) so the channels read as islands of trees, not a lawn."""
    out, placed = [], []
    x0, x1, z0, z1 = area
    tries = 0
    while len(out) < count and tries < count * 60:
        tries += 1
        cx, cz = rng.uniform(x0, x1), rng.uniform(z0, z1)
        clump = [(cx, cz)] + [(cx + rng.uniform(-6, 6), cz + rng.uniform(-6, 6)) for _ in range(rng.randint(1, 3))]
        for x, z in clump:
            if len(out) >= count:
                break
            if not clear_of((x, z), segs, TREE_WALK_GAP_M) or any(_in_rect((x, z), r, 4.0) for r in lands):
                continue
            if any(math.hypot(x - px, z - pz) < 4.2 for px, pz in placed):
                continue
            placed.append((x, z))
            out.append(_put(_variant(rng), x, 0.0, z, rng.uniform(0.0, 360.0), scale=r3(rng.uniform(0.8, 1.25))))
    return out


def _in_rect(p, r, pad: float) -> bool:
    x0, x1, z0, z1 = r
    return x0 - pad <= p[0] <= x1 + pad and z0 - pad <= p[1] <= z1 + pad


def reeds(rng: random.Random, area, count: int, segs, lands, trees) -> list[dict]:
    out = []
    x0, x1, z0, z1 = area
    tries = 0
    while len(out) < count and tries < count * 80:
        tries += 1
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        if not clear_of((x, z), segs, REED_GAP_M) or any(_in_rect((x, z), r, 1.0) for r in lands):
            continue
        if any(math.hypot(x - t["at"][0], z - t["at"][1]) < 3.0 for t in trees):
            continue
        out.append(_put("reed_bed", x, WATER_Y - 0.02, z, rng.uniform(0.0, 360.0), scale=r3(rng.uniform(0.7, 1.2))))
    return out


def _rect(b: dict):
    (x, _y, z), (sx, _sy, sz) = b["pos"], b["size"]
    return x - sx / 2, x + sx / 2, z - sz / 2, z + sz / 2


def ossa_fen() -> dict:
    lay = _layout("ossa_fen")
    blocks = {b["id"]: b for b in lay["blocks"]}
    rng = random.Random(SEED)
    pieces = [_put("ossa_fen_ground", 0.0, 0.0, 0.0, 0.0)]
    for b in _strips(lay, ("Walk", "Pocket", "Exit")):
        pieces += tile_strip(b, "root_walk_6m")
    pe = blocks["PocketEnd"]
    pieces.append(_put("reed_platform_6m", pe["pos"][0], 0.0, pe["pos"][2], 0.0))
    # The Drowner's clearing: the arena's dead tree where it stands to its anchor (ossa_fen_roots: the dead tree's foot is
    # (-1.3, -3.7) from the anchor, leaning at it), living trees on their roots round the clearing's root walls.
    dr = blocks["DrownerRoots"]
    ax, az = dr["pos"][0], dr["pos"][2]
    dead_dx, dead_dz = of.DEAD_AT[0] - of.DROWNER_AT[0], of.DEAD_AT[1] - of.DROWNER_AT[2]
    pieces.append(_put("mangrove_dead", ax + dead_dx, 0.0, az + dead_dz, 0.0))
    segs = _segments(lay)
    lands = [_rect(blocks[i]) for i in ("Bank", "Clearing")]
    trees = trunk_trees(lay, rng)
    cl = blocks["Clearing"]
    for k in range(9):  # round the clearing's root walls, outside them
        th = 2 * math.pi * k / 9 + rng.uniform(-0.15, 0.15)
        r = 12.5 + rng.uniform(0.0, 2.5)
        x, z = cl["pos"][0] + math.cos(th) * r, cl["pos"][2] + math.sin(th) * r
        if math.hypot(x - (ax + dead_dx), z - (az + dead_dz)) < 7.0 or not clear_of((x, z), [s for s in segs if s[2] < 5], 3.0):
            continue
        trees.append(_put(_variant(rng), x, 0.0, z, rng.uniform(0, 360), scale=r3(rng.uniform(0.9, 1.25))))
    for k in range(10):  # the bank's western edge: a wall of trees behind BankBoundW
        x, z = -30.0 + rng.uniform(-2.5, 1.0), -14.0 + k * 3.2 + rng.uniform(-0.8, 0.8)
        trees.append(_put(_variant(rng), x, 0.0, z, rng.uniform(0, 360), scale=r3(rng.uniform(0.9, 1.2))))
    for k in range(5):  # behind the exit's end wall
        x, z = 145.0 + rng.uniform(0.0, 6.0), -8.0 + k * 4.0 + rng.uniform(-1, 1)
        trees.append(_put(_variant(rng), x, 0.0, z, rng.uniform(0, 360), scale=r3(rng.uniform(0.9, 1.2))))
    trees += channel_trees(lay, rng, (-6.0, 150.0, -42.0, 37.0), 70, segs, lands)
    pieces += [t for t in trees if off_camera_lines(t)]
    pieces += reeds(rng, (-6.0, 150.0, -40.0, 35.0), 34, segs, lands, trees)
    pieces.append(_put("fen_far_mangroves", 64.0, WATER_Y, -2.0, 0.0, scale=1.35, lod1_from_m=900.0))
    return {"pieces": pieces}


def reedhollow() -> dict:
    lay = _layout("reedhollow")
    blocks = {b["id"]: b for b in lay["blocks"]}
    rng = random.Random(SEED + 1)
    pieces = [_put("reedhollow_ground", 0.0, 0.0, 0.0, 0.0)]
    for b in _strips(lay, ("Causeway", "Ring")):
        pieces += tile_strip(b, "reed_causeway_6m")
    centre = (44.0, 0.0)
    for b in lay["blocks"]:
        if b["id"].startswith("HousePlatform"):
            pieces.append(_put("reed_platform_6m", b["pos"][0], 0.0, b["pos"][2], float(b.get("yaw", 0.0))))
        elif b["id"].startswith("House"):
            dx, dz = centre[0] - b["pos"][0], centre[1] - b["pos"][2]  # the lodge opens (+Z) toward the lagoon
            pieces.append(_put("kirru_roost", b["pos"][0], -of.ROOST_DECK_Y + 0.03, b["pos"][2],
                               math.degrees(math.atan2(dx, dz))))
    cs = blocks["ClutchStone"]
    pieces.append(_put("clutch_stone", cs["pos"][0], 0.0, cs["pos"][2], 90.0))
    # M5-A3P-1403 (act3_ch18 K04): the shell-carver's place behind the clutch, against the shore's back edge, clear of
    # the clutch's line (x 64.4-65.3) and Pell's mark; Ch10's carver bark and Ch18's new shell both happen here.
    pieces.append(_put("shellcarver_mat", CARVER_AT[0], 0.0, CARVER_AT[1], 250.0))
    sh = blocks["Shore"]
    edge_x = sh["pos"][0] - sh["size"][0] / 2 + 0.4  # the shore's water edge, toward the lagoon (the clutch faces it)
    for z in (-3.6, 3.6):  # the name-shell cords along it (F02, F04)
        pieces.append(_put("name_shell_cord", edge_x, 0.0, z, 90.0))
    segs = _segments(lay)
    lands = [_rect(sh)]
    trees = trunk_trees(lay, rng)
    for k in range(14):  # behind the shore, a dark wall of old trees (the clutch's backs to the water, F02)
        x, z = 70.5 + rng.uniform(0.0, 6.0), -15.0 + k * 2.3 + rng.uniform(-0.6, 0.6)
        trees.append(_put(_variant(rng), x, 0.0, z, rng.uniform(0, 360), scale=r3(rng.uniform(1.0, 1.3))))
    trees += channel_trees(lay, rng, (-4.0, 80.0, -30.0, 30.0), 34, segs, lands)
    pieces += trees
    pieces += reeds(rng, (-4.0, 80.0, -30.0, 30.0), 22, segs, lands, trees)
    pieces.append(_put("fen_far_mangroves", 38.0, WATER_Y, 0.0, 40.0, scale=1.0, lod1_from_m=900.0))
    return {"pieces": pieces}


def layout(zone: str) -> dict:
    body = {"ossa_fen": ossa_fen, "reedhollow": reedhollow}[zone]()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": f"Generated by tools/act2/ch10_fen_dressing.py from env-art's fen kit on ch10/{zone}'s greybox "
                  "(M4-A2P-040; ossa_fen.md §4). Do not edit by hand.",
        "seed": SEED,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 45.0,
        "lod_end_m": 600.0,
        "lod_margin_m": 3.0,
        "greybox": {"hide_all": True, "keep": []},
        "environment": f"res://game/levels/ch10/{zone}/{zone}_environment.tres",
        "time_of_day_h": 18.33,
        **body,
        # Invisible walls along the walks' open edges over the water (the human's playtest in Oruvel, 10-30).
        "edge_walls": edge_walls(zone),
    }


def edge_walls(zone: str) -> list[dict]:
    lay = _layout(zone)
    return zone_edges.walls(lay, zone_edges.hideable_ids(lay))


def write_water_material(out: Path) -> None:
    m = ar.TANNIN_FEN
    lines = ['[gd_resource type="ShaderMaterial" load_steps=2 format=3]', "",
             f'[ext_resource type="Shader" path="{m["shader"]}" id="1_ocean"]', "", "[resource]",
             f'resource_name = "{m["name"].replace("arena_", "")}"', "render_priority = 0",
             'shader = ExtResource("1_ocean")']
    for k, v in m["params"]:
        if isinstance(v, str) and v.startswith("#"):
            c = [int(v[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            v = f"Color({c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f}, 1)"
        lines.append(f"shader_parameter/{k} = {v}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


# Ten composed cameras per zone (the art sheet's F01-F04 among them; SPEC §8.4): (name, pos, look_at, fov)
CAMERAS = {
    "ossa_fen": [
        ("F01_channel", (40.0, 0.85, 6.0), (62.0, 2.0, -4.0), 62.0),
        ("F03_dead_tree", (108.0, 1.2, 4.0), (113.0, 8.0, -9.0), 72.0),
        ("FenEdge_arrival", (-12.0, 1.7, 0.5), (14.0, 1.2, 1.5), 50.0),
        ("Walk0_root_walk", (4.0, 1.7, 3.5), (20.0, 0.8, 0.5), 50.0),
        ("Walk1_bend", (25.0, 1.7, -0.5), (40.0, 1.2, -9.0), 50.0),
        ("Walk3_islands", (62.0, 2.4, 6.0), (86.0, 1.0, -6.0), 46.0),
        ("Pocket_side", (63.0, 1.7, -8.0), (66.0, 1.0, -26.0), 50.0),
        ("Clearing_wide", (98.0, 3.2, 8.0), (116.0, 2.5, -4.0), 56.0),
        ("Exit_onward", (124.0, 1.7, 0.0), (150.0, 1.5, 0.0), 50.0),
        ("Overhead_channels", (60.0, 22.0, 30.0), (60.0, 0.0, -6.0), 55.0),
    ],
    "reedhollow": [
        ("F02_clutch_edge", (54.0, 1.5, 7.0), (66.0, 2.0, -1.0), 45.0),
        ("F04_name_shells", (58.5, 1.4, -1.5), (60.2, 1.3, -3.6), 40.0),
        ("Gate_arrival", (0.5, 1.7, 0.0), (30.0, 1.2, 0.0), 50.0),
        ("Causeway_mid", (18.0, 1.7, 1.0), (40.0, 1.6, 4.0), 50.0),
        ("Ring_lodges", (34.0, 1.7, 8.0), (50.0, 2.2, -14.0), 52.0),
        ("Lagoon_across", (44.0, 1.4, 14.0), (44.0, 1.6, -14.0), 58.0),
        ("Shore_clutch_stone", (62.0, 1.7, 3.0), (65.3, 0.4, 0.0), 45.0),
        ("Lodge_close", (52.5, 1.7, -10.0), (57.3, 2.2, -13.3), 50.0),
        ("From_shore_back", (66.0, 1.8, 0.0), (20.0, 1.0, 0.0), 50.0),
        ("Overhead_ring", (44.0, 26.0, 26.0), (44.0, 0.0, 0.0), 55.0),
    ],
}


def write_preview(zone: str) -> Path:
    cls = {"ossa_fen": "OssaFen", "reedhollow": "Reedhollow"}[zone]
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch10/ch10_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="3_tide"]',
             '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]',
             '[ext_resource type="Resource" path="res://game/world/water/lagoon_waves.tres" id="5_waves"]',
             f'[ext_resource type="Material" path="res://game/levels/ch10/{zone}/{zone}_water_material.tres" id="6_mat"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="7_cast"]', "",
             f'[node name="{cls}" type="Node3D"]', 'script = ExtResource("1_zone")', f'location_id = &"ch10/{zone}"',
             f'layout_path = "res://game/levels/ch10/{zone}/{zone}_layout.json"', "",
             '[node name="Cast" type="Node" parent="."]', 'script = ExtResource("7_cast")', "",
             '[node name="Water" type="Node3D" parent="."]',
             f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {WATER_Y}, 0)", 'script = ExtResource("4_water")',
             "publishes_water_level = true", 'wave_set = ExtResource("5_waves")', 'material = ExtResource("6_mat")',
             "amplitude_scale = 0.08", "",
             '[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]',
             'script = ExtResource("3_tide")', f"tide_line_y = {WATER_Y}", f"water_height_y = {WATER_Y}",
             'water = NodePath("../Water")', "",
             '[node name="Dressing" type="Node3D" parent="." node_paths=PackedStringArray("tide")]',
             'script = ExtResource("2_dressing")', f'layout_path = "res://game/levels/ch10/{zone}/{zone}_dressing.json"',
             'tide = NodePath("../Tide")', "", '[node name="Cameras" type="Node3D" parent="."]', ""]
    for name, pos, look, fov in CAMERAS[zone]:
        lines += [f'[node name="{name}" type="Camera3D" parent="Cameras"]', f"fov = {fov}", "near = 0.1", "far = 1500.0",
                  f"transform = {_look_xform(pos, look)}", ""]
    out = PREVIEW / f"{zone}_dressed.tscn"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    return out


def _look_xform(pos, look) -> str:
    f = [look[i] - pos[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in f))
    f = [c / n for c in f]
    z = [-c for c in f]  # Godot cameras look down -Z
    up = (0.0, 1.0, 0.0)
    x = [up[1] * z[2] - up[2] * z[1], up[2] * z[0] - up[0] * z[2], up[0] * z[1] - up[1] * z[0]]
    xn = math.sqrt(sum(c * c for c in x))
    x = [c / xn for c in x]
    y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
    m = [x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2]]
    return "Transform3D(" + ", ".join(f"{v:.5f}" for v in m) + f", {pos[0]}, {pos[1]}, {pos[2]})"


def main() -> int:
    for zone in ("ossa_fen", "reedhollow"):
        out = ZONES / zone
        # The arena's grade, with the fill lifted for the walk: the colour script's fill 0.5 frames a battle; at a
        # player's eye, looking every way at dusk, it left the flat land black (M4-A2P-040's renders).
        spec = dict(ar.FEN_ARENA, sub_frame="ch10", lut=LUT, fill=dict(ar.FEN_ARENA["fill"], energy=ZONE_FILL))
        ar.write_environment(spec, out / f"{zone}_environment.tres")
        write_water_material(out / f"{zone}_water_material.tres")
        lay = layout(zone)
        (out / f"{zone}_dressing.json").write_text(json.dumps(lay, indent=1) + "\n", encoding="utf-8")
        write_preview(zone)
        print(f"DRESSING {zone}: {len(lay['pieces'])} pieces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
