#!/usr/bin/env python3
"""Ch5 Pemakar: env-art's Pemakar kit (M3-ENV-03) dresses ch05/pemakar (M3-C05-1213, ADR 0200).

The kit's frame (pemakar_common.py): the sea at y 0, the town's ten tiers on arcs about TOWN_CENTRE (0, -150), tier
t's front at radius 150 - 7 t (z = -7 t on the axis) and its tread at y 8 + 2.4 t; one stair flight per tier on the
axis (x 0), each descending 4.2 m out on to the tier below; the massif's slope runs down from tier 0 to the shore at
z 29. Tier kinds: 0 market (and the smithy, x 23), 1-2 houses, 3 and 6 paddies, 4-5 and 7-9 graves.

The story's places, each on its tier (the greybox ran them north up a flat slope in the same order):
  the harbour        env-art's harbour_quay at the shore (front z 27, top y 1.2; M3-ENV-1214), the Brightwater
                     ferry (the Ch4 kit's) alongside, the wake-wall at the quay's back, and the sea-cut weir at the
                     quay's east end (WEIR_AT: the preview sets it at the bottom channel's outlet, x -39, but B05's
                     weir folk stand at the quay's east end, so the weir comes to them; --weir-relayout moved them)
  the market         tier 0 about the stair head (the kit keeps |x| < 3.4 clear of all but the stair and lamps)
  the forge lane     tier 0 at the smithy, which trades places with the house_b by the stair (x 6.3): the kit's
                     tiers are dressing, not lanes (house_b's veranda and house_a's plinth close the lane at
                     d 1.4), so the story keeps near the stair
  the inn            tier 2 west: the kit's veranda house nearest the stair, moved along its arc from x -14 to
                     -6.6 (the third tier; the roofs of tier 1's houses reach over tier 2's lane further out)
  the grave terraces tier 4 east, above tier 3's paddies
  the crown channel  tier 9, the top, at the stair head and its open-hand gate; the way to Ashcrown behind
The greybox's points are moved region by region (relayout(): REGIONS, then SPECIAL by hand).

Writes next to the zone (game/levels/ch05/pemakar/):
  pemakar_dressing.json   the preview's pieces, lamps (night: they follow the Lamps block, which the day variant
                          hides), the leaf-boats, the far and sea lights and frangipani, the quay, the ferry, the
                          awnings; the massif collides as an LOD0 trimesh, houses, smithy, graves and lamps as boxes.
  pemakar_collision.json  the treads and walls as boxes, the stairs as ramps between cheek walls, the quay and its
                          edge, the town's bounds and the shore.
and copies the preview's night and dusk grades and the sea. With --relayout it also moves the story points (once).

    python3 tools/act1/ch05_pemakar_dressing.py [--relayout] [--weir-relayout]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "pemakar"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "brightwater_ferry"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bf_common as bf  # noqa: E402
import ch05_09_zone_looks as zl  # noqa: E402
import numpy as np  # noqa: E402
import pemakar_common as pc  # noqa: E402
import pemakar_skyline as sky  # noqa: E402
import pemakar_terraces as pt  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch05" / "pemakar"
LAYOUT = ZONE / "pemakar_layout.json"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "pemakar_kit"
RES_PREVIEW = "res://game/levels/_tests/pemakar_kit/"
RES_ZONE = "res://game/levels/ch05/pemakar/"
KIT = "res://assets/environments/kits/pemakar/"
FERRY_KIT = "res://assets/environments/kits/brightwater_ferry/"
VEG = "res://assets/environments/vegetation/"
NIGHT_BLOCK = "Lamps"  # the greybox's lamp line: the day variant hides it, and the festival with it
TIERS = pc.TOWN_TIERS
QUAY_FRONT_Z = 27.0
QUAY_Y = 1.2
QUAY_HALF_X = 16.0
MASSIF_ROWS = np.linspace(80.0, -130.0, 34)  # the massif mesh's near rows (pemakar_skyline.massif): linear between
QUAY_BACK_Z = float(MASSIF_ROWS[9])  # where the slope comes down to the quay's height (y 1.18)
ROAD_HALF_X = 5.0
FERRY_AT = (-2.0, -bf.WATERLINE_Y, QUAY_FRONT_Z + 3.4 + 0.6)  # alongside, port side to the quay, bow west
FERRY_YAW = 90.0
# env-art's sea_cut_weir (pemakar_harbour.py): its west cheek's outer face (WEIR_HALF_M + 0.8 from its axis) against the
# quay's east end; its cheek tops (0.5 over the crest) flush with the quay's deck, so the crest stands 0.7 over the sea
WEIR_CHEEK_OUT_M = 4.0
WEIR_CHEEK_TOP_M = 0.5
WEIR_AT = (QUAY_HALF_X + 0.2 + WEIR_CHEEK_OUT_M, QUAY_Y - WEIR_CHEEK_TOP_M, QUAY_FRONT_Z + 0.6)
# B05's light at the weir (P11: "the lamplight ends here"): a lamp pillar at the quay's east end (the kit's lamp
# 1.35 m up it, as the preview lights its pillars) and the boats' fires going over the spill; both follow the Lamps
# block, so the day has neither
WEIR_LAMP_AT = (QUAY_HALF_X - 0.6, QUAY_Y, QUAY_BACK_Z + 0.8)  # clear of the weir folk's marks
WEIR_LIGHTS = [
    {"at": [WEIR_LAMP_AT[0], WEIR_LAMP_AT[1] + 1.35, WEIR_LAMP_AT[2]], "color": "#FFA757", "energy": 1.6, "range": 7.0},
    {"at": [WEIR_AT[0], WEIR_AT[1] + 0.3, WEIR_AT[2] + 0.5], "color": "#FF9A4A", "energy": 1.1, "range": 5.0},
]
# The quay at night (the Lead's 10-29 final-quality audit): the party lands on a quay that read pitch black at player
# height, lit only by their own hand lanterns. The kit's lamp pillars stand along its back edge, clear of the story's
# marks (the weir folk, the wake wall, the line), each with the weir lamp's light.
QUAY_LAMP_XS = (-12.5, -6.0, 10.5)
QUAY_LAMP_Z = QUAY_BACK_Z + 0.45
QUAY_LIGHTS = [{"at": [x, QUAY_Y + 1.35, QUAY_LAMP_Z], "color": "#FFA757", "energy": 1.6, "range": 7.0}
               for x in QUAY_LAMP_XS]
# The plume at night (the Lead's gate review, 10-28): the kit's far plume material is a hard-edged near-black
# silhouette from the harbour, so it read as a blob in the sky. The zone's own night material (the same
# env_ash_plume shader) softens and thins its edges and lifts the crater's ember up its underside, so it reads as
# smoke lit from below. It is written here (PLUME_NIGHT_PARAMS) and the plume row takes it by slot.
PLUME_NIGHT = "pemakar_plume_night"
PLUME_NIGHT_PARAMS = {
    "col_body": "Color(0.29, 0.27, 0.26, 1)", "col_body_top": "Color(0.36, 0.35, 0.36, 1)", "body_darken": 0.42,
    "mottle": 0.55, "opacity": 0.92, "edge_soft": 0.65, "top_fade": 0.45, "alpha_mottle": 0.55,
    "ember_energy": 0.55, "ember_height": 0.32, "ember_underside": 1.0, "town_glow": 0.05, "rim_energy": 0.0,
}
# The story pieces env-art built for the greybox's stand-ins (M3-ENV-1214): each follows its block
# The leat feeding the weir (b_leat.py, M3-ENV-1307): from a culvert in tier 0's wall down the flank to the back of
# the weir's cut (its bed 0.05 under the crest, 3 m upstream of it); it follows the weir's block
LEAT_AT = (WEIR_AT[0], WEIR_AT[1] - 0.05, WEIR_AT[2] - 3.0)
STORY_PIECES = {"wake_wall": "WakeWall", "sea_cut_weir": "SeaCutWeir", "crown_bell": "CrownBell"}
TOWN_HALF_X = 44.0
SHORE_Z = 29.0
STAIR_RUN = pt.STEP_RUN_M * round(pc.WALL_H_M / pt.STEP_RISE_M)  # 4.2 m out on to the tier below
STAIR_HALF_W = pt.STAIR_HALF_W_M
WALL_T = pt.WALL_THICK_M
RAIL_H = 1.1
COLLIDE_BOX = {"shrine_box", "grave_stele_a", "grave_stele_b", "grave_cairn", "grave_curb", "copper_outcrop"}
COLLIDE_TRIMESH = {"house_pemakar_a", "house_pemakar_b", "smithy"}  # their bounds take in the eaves over the band


def r3(v: float) -> float:
    return round(float(v), 3)


def tier_y(t: int) -> float:
    return float(pc.tier_tread_y(t))


def tier_r(t: int) -> float:
    return pc.TOWN_R0_M - pc.TREAD_D_M * t


def on_tier(t: int, x: float, d: float) -> list[float]:
    """A point on tier t's tread at lateral x, `d` m behind its front edge (on the arc)."""
    r = tier_r(t) - d
    th = math.asin(max(-1.0, min(1.0, x / r)))
    rise = pt.TREAD_FALL_M * min(max((d - 0.25) / (pc.TREAD_D_M - 0.25), 0.0), 1.0)
    return [r3(r * math.sin(th)), r3(tier_y(t) + rise), r3(pc.TOWN_CENTRE[1] + r * math.cos(th))]


def tier_yaw(x: float, z: float) -> float:
    """Yaw (deg) of a point's outward (downhill) direction on the arcs (a module's local +Z)."""
    return r3(math.degrees(math.atan2(x - pc.TOWN_CENTRE[0], z - pc.TOWN_CENTRE[1])))


_noise = None


def ground(x: float, z: float) -> float:
    """The massif's height (pemakar_skyline.massif_height; the mesh is coarser, so this is near, not exact)."""
    global _noise
    if _noise is None:
        _noise = pc.kc.Noise3(pc.kc.rng_for("mountain_massif", 801))
    return float(sky.massif_height(np.array([x]), np.array([z]), _noise)[0])


def local(at: list[float], yaw: float, lx: float, ly: float, lz: float) -> list[float]:
    a = math.radians(yaw)
    return [at[0] + lx * math.cos(a) + lz * math.sin(a), at[1] + ly, at[2] - lx * math.sin(a) + lz * math.cos(a)]


def box(bid: str, at: list[float], yaw: float, centre: tuple, size: tuple) -> dict:
    """A box in a module's frame: `centre` (local x, y, z) and `size` (x, y, z)."""
    c = local(at, yaw, *centre)
    return {"id": bid, "pos": [r3(v) for v in c], "size": [r3(v) for v in size], "yaw": r3(yaw)}


def ramp(rid: str, a: list[float], b: list[float], width: float) -> dict:
    return {"id": rid, "from": [r3(v) for v in a], "to": [r3(v) for v in b], "width": r3(width)}


def stair_line(t: int) -> tuple[list[float], list[float]]:
    """Tier t's flight as a ramp line: its foot out on the tier below, its head at the coping, level with the tread's
    collision top (the tread box starts there)."""
    p = {round(m["at"][1], 1): m for m in modules("stair_flight")}[round(tier_y(t), 1)]
    at, yaw = p["at"], p["yaw_deg"]
    foot = local(at, yaw, 0.0, -pc.WALL_H_M + pt.TREAD_FALL_M * 0.5, STAIR_RUN + float(pc.batter_z(-pc.WALL_H_M)))
    return foot, local(at, yaw, 0.0, pt.TREAD_FALL_M * 0.5, 0.05)


def road() -> list[dict]:
    """The harbour road up the massif's slope from the quay's back to tier 0's flight, on the mesh's own rows (the
    mesh is linear between them along the axis), ending where the slope meets the flight's line."""
    foot, head = stair_line(0)
    pts = [[0.0, ground(0.0, z), float(z)] for z in MASSIF_ROWS if foot[2] - pc.TREAD_D_M < z <= QUAY_BACK_Z + 1e-6]
    a, b = pts[-1], [0.0, ground(0.0, float(MASSIF_ROWS[len(pts) + 9])), float(MASSIF_ROWS[len(pts) + 9])]
    k = (head[1] - foot[1]) / (foot[2] - head[2])  # the flight's rise per metre toward -z
    s = (b[1] - a[1]) / (a[2] - b[2])
    z = (a[1] + s * a[2] - foot[1] - k * foot[2]) / (s - k)  # a[1] + s (a.z - z) = foot.y + k (foot.z - z)
    pts.append([0.0, a[1] + s * (a[2] - z), z])
    return [ramp(f"Road{i}", [p[0], p[1] + 0.02, p[2]], [q[0], q[1] + 0.02, q[2]], 2 * ROAD_HALF_X)
            for i, (p, q) in enumerate(zip(pts, pts[1:]))]


def preview() -> dict:
    return json.loads((PREVIEW / "pemakar_preview_layout.json").read_text(encoding="utf-8"))


def modules(kind: str) -> list[dict]:
    return [p for p in preview()["pieces"] if p["piece"] == kind]


# --- collision ---------------------------------------------------------------------------------------------------
def collision() -> dict:
    blocks: list[dict] = []
    ramps: list[dict] = []
    stairs = {round(p["at"][1], 1): p for p in modules("stair_flight")}
    walls = modules("terrace_wall_4m") + modules("terrace_wall_copper")
    for i, p in enumerate(modules("terrace_tread_4m") + modules("paddy_tread_4m")):
        at = p["at"]
        blocks.append(box(f"Tread{i}", at, p["yaw_deg"], (0.0, -0.5 + pt.TREAD_FALL_M * 0.5, -pc.TREAD_D_M * 0.5),
                          (pc.MODULE_M + 0.1, 1.0, pc.TREAD_D_M)))
    for i, p in enumerate(walls):
        at = p["at"]
        blocks.append(box(f"Wall{i}", at, p["yaw_deg"], (0.0, -pc.WALL_H_M * 0.5, -WALL_T * 0.5),
                          (pc.MODULE_M + 0.05, pc.WALL_H_M, WALL_T)))
    for t in range(TIERS):
        p = stairs[round(tier_y(t), 1)]
        at, yaw = p["at"], p["yaw_deg"]
        foot, head = stair_line(t)
        ramps.append(ramp(f"Stair{t}", foot, head, 2 * STAIR_HALF_W))
        for side in (-1.0, 1.0):  # the cheek walls beside the flight's head and its parapets down the run
            blocks.append(box(f"StairCheek{t}{'LR'[side > 0]}", at, yaw,
                              (side * (STAIR_HALF_W + 0.65), -pc.WALL_H_M * 0.5, -WALL_T * 0.5),
                              (1.3, pc.WALL_H_M, WALL_T)))
            blocks.append(box(f"StairParapet{t}{'LR'[side > 0]}", at, yaw,
                              (side * (STAIR_HALF_W + 0.15), -pc.WALL_H_M * 0.5 + RAIL_H * 0.5, STAIR_RUN * 0.5),
                              (0.3, pc.WALL_H_M + RAIL_H, STAIR_RUN)))
    # the quay: a deck at the shore, its sea edge railed (no swimming), the ferry's side beyond
    blocks.append({"id": "Quay", "pos": [0.0, QUAY_Y - 1.0, r3((QUAY_FRONT_Z + QUAY_BACK_Z) * 0.5)],
                   "size": [2 * QUAY_HALF_X, 2.0, r3(QUAY_FRONT_Z - QUAY_BACK_Z)]})
    ramps += road()
    blocks.append({"id": "QuayEdge", "pos": [0.0, QUAY_Y + RAIL_H * 0.5, QUAY_FRONT_Z + 0.1],
                   "size": [2 * QUAY_HALF_X, RAIL_H, 0.2]})
    for side in (-1.0, 1.0):
        blocks.append({"id": f"QuayEnd{'WE'[side > 0]}", "pos": [r3(side * (QUAY_HALF_X + 0.1)), QUAY_Y,
                                                                   QUAY_FRONT_Z - 1.5], "size": [0.2, 2.4, 3.0]})
    # the bounds: the shore either side of the quay, the town's flanks, the crown's back
    for side in (-1.0, 1.0):
        x0 = QUAY_HALF_X if side > 0 else -60.0
        x1 = 60.0 if side > 0 else -QUAY_HALF_X
        blocks.append({"id": f"Shore{'WE'[side > 0]}", "pos": [r3((x0 + x1) * 0.5), 1.0, SHORE_Z - 4.0],
                       "size": [r3(x1 - x0), 6.0, 0.4]})
        blocks.append({"id": f"Flank{'WE'[side > 0]}", "pos": [r3(side * (TOWN_HALF_X + 2.0)), 20.0, -25.0],
                       "size": [0.4, 60.0, 110.0]})
    back = tier_r(TIERS - 1) - pc.TREAD_D_M
    blocks.append({"id": "CrownBack", "pos": [0.0, tier_y(TIERS - 1) + 2.0, r3(pc.TOWN_CENTRE[1] + back - 0.4)],
                   "size": [2 * TOWN_HALF_X + 6.0, 6.0, 0.4]})
    return {"_about": "Generated by tools/act1/ch05_pemakar_dressing.py (ADR 0200); do not edit by hand.",
            "blocks": blocks, "ramps": ramps}


# --- dressing ----------------------------------------------------------------------------------------------------
def ferry() -> list[dict]:
    return [{"piece": p, "kit_dir": FERRY_KIT, "at": [FERRY_AT[0], FERRY_AT[2]], "y": r3(FERRY_AT[1]),
             "yaw_deg": FERRY_YAW, "block": "Ferry"}
            for p in ("ferry_hull", "ferry_rig", "ferry_deckhouse", "ferry_awning", "ferry_cargo")]


SMITHY_SWAP = (22.8, 6.3)  # the smithy's x and the tier-0 house_b's: they trade places (the forge by the stair)


# (piece, tier, its x, the x it moves to along its arc): the inn and its door's shrine-box
MOVES = (("house_pemakar_b", 2, -14.013, -6.6), ("shrine_box", 2, -16.816, -9.403))


def along_arc(p: dict, x_to: float) -> dict:
    """The piece turned about the town's centre so it stands at `x_to` on its own arc (same depth, same facing)."""
    cx, cz = pc.TOWN_CENTRE
    x, y, z = p["at"]
    r = math.hypot(x - cx, z - cz)
    a0 = math.atan2(x - cx, z - cz)
    a1 = math.asin(max(-1.0, min(1.0, (x_to - cx) / r)))
    return dict(p, at=[r3(cx + r * math.sin(a1)), y, r3(cz + r * math.cos(a1))],
                yaw_deg=r3(p["yaw_deg"] + math.degrees(a1 - a0)))


def swapped(p: dict) -> dict:
    """A preview piece, with the smithy and the house_b by the stair traded, and the inn moved (MOVES)."""
    for kind, t, x_from, x_to in MOVES:
        if p["piece"] == kind and abs(p["at"][1] - tier_y(t)) < 0.1 and abs(p["at"][0] - x_from) < 0.1:
            return along_arc(p, x_to)
    if abs(p["at"][1] - tier_y(0)) > 0.1:
        return p
    for kind, other, x in (("smithy", "house_pemakar_b", SMITHY_SWAP[1]), ("house_pemakar_b", "smithy", SMITHY_SWAP[0])):
        if p["piece"] == kind and abs(p["at"][0] - SMITHY_SWAP[0 if kind == "smithy" else 1]) < 0.6:
            twin = [q for q in preview()["pieces"] if q["piece"] == other and abs(q["at"][0] - x) < 0.6
                    and abs(q["at"][1] - tier_y(0)) < 0.1][0]
            return dict(p, at=twin["at"], yaw_deg=twin["yaw_deg"])
    return p


# The weir's stone (the PC's pass 3, row 62: its slabs read as flat grey boxes): the kit's dry dressed stone is pale
# and salt-white everywhere, but the sea runs over this one. Darker, wet-dark below the crest, weed in a band at the
# waterline and the salt only above it. The kit preview's weir row takes the same material (pemakar_layout.py).
WEIR_STONE = "kit_weir_stone"  # in the kit's materials folder, so the kit preview (which names slots) can take it
# The PC's pass 5 (row 62 still flat grey): each block takes its own value (variation 0.4), the relief and the cavities
# are stronger, and the salt crust and the algae band are wider, so the courses read as separate wet stones.
WEIR_STONE_OVERRIDES = {"col_tint": "Color(0.9, 0.88, 0.86, 1)", "use_algae": "true", "salt_coverage": "Vector2(0.2, 0.6)",
                        "normal_strength": "1.7", "cavity_darken": "0.6", "variation_value": "0.4",
                        "variation_warmth": "0.06", "detail_scale_m": "0.3", "salt_band_m": "Vector2(0.4, 10000)"}
# Soaked stone keeps its relief and most of its value (the shader's defaults, 0.6 flatten and x0.55, made the whole
# wet weir one smooth dark face).
WEIR_STONE_ADDED = {"algae_band_m": "Vector2(-0.9, 0.35)", "algae_coverage": "Vector2(0.5, 0.95)",
                    "wet_darken": "0.75", "wet_flatten": "0.15", "wet_roughness": "0.3",
                    "col_algae": "Color(0.239, 0.29, 0.161, 1)"}
# ... and the water arriving over the crest runs (the kit's flowing spill water), not the channels' still near-mirror,
# which read as a flat pale panel on the crest under a grey sky
WEIR_SLOTS = {"kit_volcanic_dressed": KIT + "materials/" + WEIR_STONE + ".tres",
              "kit_channel_water": KIT + "materials/kit_water_spill.tres"}
# The kit's flat StandardMaterial metals and lacquers (M3-ENV-1326): the shrine-boxes, gates, bell frame and forge read
# as plastic at player height. Zone looks by slot on every Pemakar piece (`kit_material_paths`), and on the Pemakar
# pieces Ashcrown borrows (ch05_ashcrown_dressing.py reads PEMAKAR_SLOTS).
KIT_LOOKS = {
    "kit_lacquer_red": ("pemakar_lacquer_red_material.tres", zl.lacquer((0.702, 0.149, 0.1176))),
    "kit_lacquer_black": ("pemakar_lacquer_black_material.tres",
                          zl.lacquer((0.1137, 0.0980, 0.0863), undercoat=(0.3216, 0.1176, 0.0863))),
    "kit_copper_vein": ("pemakar_copper_vein_material.tres", dict(zl.VERDIGRIS)),
    "kit_copper_raw": ("pemakar_copper_raw_material.tres", dict(zl.NEW_COPPER)),
    "kit_gold_leaf": ("pemakar_gold_leaf_material.tres", dict(zl.GOLD)),
    "kit_iron": ("pemakar_iron_material.tres", dict(zl.SEA_IRON, col_bronze=(0.1647, 0.149, 0.1412))),
}
PEMAKAR_SLOTS = {slot: RES_ZONE + name for slot, (name, _) in KIT_LOOKS.items()}


def dressing() -> dict:
    pv = preview()
    pieces = []
    for p in pv["pieces"]:
        p = swapped(p)
        row = {k: v for k, v in p.items() if k != "at"}
        row.update(at=[r3(p["at"][0]), r3(p["at"][2])], y=r3(p["at"][1]))
        if p["piece"] == "sea_cut_weir":
            row.update(at=[r3(WEIR_AT[0]), r3(WEIR_AT[2])], y=r3(WEIR_AT[1]), material_paths=dict(WEIR_SLOTS))
            row.pop("materials", None)  # the preview's override is a path (its own dresser); the zone's is material_paths
        if p["piece"] in STORY_PIECES:
            row["block"] = STORY_PIECES[p["piece"]]
        if p["piece"] == "ash_plume":
            row.update(kit_dir=KIT, materials={"kit_plume": PLUME_NIGHT}, materials_dir=RES_ZONE)
        if p["piece"] == "mountain_massif":
            row["collide"] = "trimesh_lod0"
        elif p["piece"] in COLLIDE_BOX:
            row["collide"] = True
        elif p["piece"] in COLLIDE_TRIMESH:
            row["collide"] = "trimesh"
        pieces.append(row)
    for p in pv.get("plants", []):
        pieces.append({"piece": p["plant"], "kit_dir": VEG, "materials_dir": VEG + "materials/",
                       "at": [r3(p["at"][0]), r3(p["at"][2])], "y": r3(p["at"][1]), "yaw_deg": p["yaw_deg"],
                       "scale": p["scale"], "collide": True})
    pieces += ferry()
    pieces.append({"piece": "lamp_pillar", "at": [r3(WEIR_LAMP_AT[0]), r3(WEIR_LAMP_AT[2])], "y": WEIR_LAMP_AT[1],
                   "yaw_deg": 0.0, "block": NIGHT_BLOCK, "collide": True})
    for x in QUAY_LAMP_XS:
        pieces.append({"piece": "lamp_pillar", "at": [r3(x), r3(QUAY_LAMP_Z)], "y": QUAY_Y, "yaw_deg": 0.0,
                       "block": NIGHT_BLOCK, "collide": True})
    pieces.append({"piece": "weir_leat", "at": [r3(LEAT_AT[0]), r3(LEAT_AT[2])], "y": r3(LEAT_AT[1]), "yaw_deg": 0.0,
                   "block": STORY_PIECES["sea_cut_weir"]})
    lights = [dict({k: v for k, v in light.items() if k != "at"}, at=light["at"], block=NIGHT_BLOCK)
              for light in pv["lights"] + WEIR_LIGHTS + QUAY_LIGHTS]
    boats = pv["boats"]
    far = [dict(pv[k], name=n, block=NIGHT_BLOCK) for k, n in (("far_lights", "FarLights"), ("sea_lights",
                                                                                            "SeaLights"))]
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch05_pemakar_dressing.py from env-art's Pemakar kit (M3-ENV-03); do not "
        "edit by hand. The kit's frame.",
        "seed": 5,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": pv["lod1_from_m"],
        "lod_end_m": pv["lod_end_m"],
        "lod_margin_m": pv["lod_margin_m"],
        "environment": RES_ZONE + "pemakar_night_environment.tres",
        "time_of_day_h": 20.0,
        "greybox": {"hide_all": True, "keep": []},
        "fire_light_color": "#FFA757",
        "fire_lights": lights,
        "multimeshes": [{"name": "LeafBoats", "piece": boats["piece"], "transforms": boats["transforms"],
                         "block": NIGHT_BLOCK}],
        "far_lights": far,
        "kit_material_paths": dict(PEMAKAR_SLOTS),
        "pieces": pieces,
    }


def write_plume_night() -> None:
    lines = ['[gd_resource type="ShaderMaterial" load_steps=2 format=3]', "",
             '[ext_resource type="Shader" path="res://game/shaders/environment/env_ash_plume.gdshader" id="1_shader"]',
             "", "[resource]", f'resource_name = "{PLUME_NIGHT}"', 'shader = ExtResource("1_shader")']
    lines += [f"shader_parameter/{k} = {v}" for k, v in sorted(PLUME_NIGHT_PARAMS.items())]
    (ZONE / f"{PLUME_NIGHT}.tres").write_text("\n".join(lines) + "\n", encoding="utf-8")


# The night fill (PC QA pass 3 row 49: the harbour read near-black from the field camera, the party lost). The
# preview's night grade takes its ambient from a near-black sky, so the layout's fill colour did nothing; the zone's
# copy takes a colour ambient (as the day grade does) and the layout's `environment` row carries a moonlit fill.
NIGHT_SUN = {"pitch_deg": -55.0, "yaw_deg": -20.0, "energy": 0.45, "color": "#5a6c94"}
NIGHT_FILL = {"ambient_color": "#6c7898", "ambient_energy": 0.8}  # pass 4: the harbour's foreground still near-black at 0.6


def copy_grades() -> None:
    for name in ("pemakar_night_environment.tres", "pemakar_dusk_environment.tres", "pemakar_day_environment.tres",
                 "pemakar_sea_material.tres"):
        text = (PREVIEW / name).read_text(encoding="utf-8").replace(RES_PREVIEW, RES_ZONE)
        if name == "pemakar_night_environment.tres":
            assert text.count("ambient_light_source = 3") == 1
            text = text.replace("ambient_light_source = 3", "ambient_light_source = 2")
        (ZONE / name).write_text(text, encoding="utf-8")


def night_fill() -> None:
    """The night `sun` and `environment` rows (one-key text edits: the layout is hand-formatted and act1-chapters
    edits it too)."""
    text = LAYOUT.read_text(encoding="utf-8")
    g = json.loads(text)
    for key, want in (("sun", NIGHT_SUN), ("environment", dict(g["environment"], **NIGHT_FILL))):
        have = g[key]
        if have == want:
            continue
        old = json.dumps(have)
        assert text.count(old) == 1, old
        text = text.replace(old, json.dumps(want))
    LAYOUT.write_text(text, encoding="utf-8")


# --- the one-time move of the story points ----------------------------------------------------------------------
def harbour(x: float, z: float) -> list[float]:
    """The greybox's harbour (its quay z 1-11, the sea beyond 12) on the kit's quay (z 20-27) and the slope behind."""
    zk = min(QUAY_FRONT_Z - 0.5, QUAY_FRONT_Z - (11.0 - z) * 0.45)  # the weir folk stand at the edge, not over it
    if zk >= QUAY_BACK_Z:
        return [r3(x), QUAY_Y, r3(zk)]
    return [r3(x), r3(ground(x, zk)), r3(zk)]


# (name, greybox test, tier, x(x), depth(z)): the first region a point is in moves it on to that tier
LANE_D = 1.6  # a tier's lane: between the channel's kerb (d 0.84) and the house fronts (d 1.9); shrine boxes at 1.1
REGIONS = [
    ("crown", lambda x, z: z <= -38.0, TIERS - 1, lambda x: x, lambda z: 0.9 + (-38.0 - z) * 0.22),
    ("inn", lambda x, z: x <= -9.0 and z <= -28.0, 2, lambda x: -3.6 + (x + 13.0) * 0.3, lambda z: LANE_D),
    ("graves", lambda x, z: x >= 7.0 and z <= -26.0, 4, lambda x: x, lambda z: LANE_D),
    ("forge", lambda x, z: x <= -7.0 and z <= -17.0, 0, lambda x: SMITHY_SWAP[1] + (x + 13.0) * 0.5,
     lambda z: LANE_D),
    ("market", lambda x, z: z <= -3.0, 0, lambda x: x * 0.42, lambda z: LANE_D),
]
SPECIAL = {  # by hand: [x, y, z] (+ yaw), kit frame
    "FromAshcrown": on_tier(TIERS - 1, 0.0, 6.0) + [180.0],
    "tender": on_tier(TIERS - 1, -2.0, 5.6) + [180.0],
    "grave_terrace": on_tier(4, 12.0, LANE_D) + [0.0],
    "harbour_road": harbour(0.0, 10.0),
    "sea": [10.0, 1.0, 40.0, 0.0],
}


def to_kit(name: str, p: list) -> list:
    x, y, z = float(p[0]), float(p[1]), float(p[2])
    yaw = float(p[3]) if len(p) > 3 else None
    if name in SPECIAL:
        w = list(SPECIAL[name])
        return w[:3] + ([r3(w[3] if len(w) > 3 else yaw)] if yaw is not None else [])
    for _rname, inside, t, fx, fd in REGIONS:
        if inside(x, z):
            d = max(0.9, min(pc.TREAD_D_M - 0.8, fd(z)))
            w = on_tier(t, fx(x), d)
            w[1] = r3(w[1] + y)
            break
    else:
        w = harbour(x, z)
        w[1] = r3(w[1] + y)
    return w + ([r3(yaw % 360.0)] if yaw is not None else [])


SHOTS = {  # by hand where the greybox's framing no longer reads
    "P01": {"pos": [-8.0, 1.6, 58.0], "look_at": [0.0, 22.0, -40.0], "fov": 46},
    "P08": {"pos": [0.0, tier_y(TIERS - 1) + 7.0, -71.0], "look_at": [0.0, 8.0, -4.0], "fov": 60},
}
DROPPED = {"Ground", "Sea", "HarbourQuay", "MarketAwningW", "MarketAwningE", "Forge1", "Forge2", "ForgeCoals",
           "GraveSteps", "ShrineBox", "Paddies", "Inn", "InnGatePost", "OpenHandGate", "CrownChannel", "WeirChannel",
           "WallW", "WallE", "WallN"}


MAP_CHORDS = 8


def map_blocks() -> list[dict]:
    """Flat, non-solid blocks for the area map (ZoneMapShapes reads only the layout's blocks; M3-UI-1212): the tiers
    (chords of their arcs), the quay and the road as pads, the houses and the smithy as buildings (MapHouse*, hinted in
    zone_maps.json), the sea (MapSea, hinted)."""
    out = []
    for t in range(TIERS):
        r = tier_r(t) - pc.TREAD_D_M * 0.5
        a0 = math.asin(TOWN_HALF_X / r)
        for i in range(MAP_CHORDS):
            a = -a0 + 2 * a0 * (i + 0.5) / MAP_CHORDS
            c = [pc.TOWN_CENTRE[0] + r * math.sin(a), 0.1, pc.TOWN_CENTRE[1] + r * math.cos(a)]
            out.append({"id": f"MapTier{t}_{i}", "pos": [r3(v) for v in c],
                        "size": [r3(2 * r * math.sin(a0 / MAP_CHORDS) + 0.3), 0.2, pc.TREAD_D_M],
                        "yaw": r3(math.degrees(a))})
    out.append({"id": "MapQuay", "pos": [0.0, 0.1, r3((QUAY_FRONT_Z + QUAY_BACK_Z) * 0.5)],
                "size": [2 * QUAY_HALF_X, 0.2, r3(QUAY_FRONT_Z - QUAY_BACK_Z)]})
    out.append({"id": "MapRoad", "pos": [0.0, 0.1, r3(QUAY_BACK_Z * 0.5)], "size": [2 * ROAD_HALF_X, 0.2, r3(QUAY_BACK_Z)]})
    out.append({"id": "MapSea", "pos": [0.0, -0.5, r3(QUAY_FRONT_Z + 30.0)], "size": [200.0, 0.2, 60.0]})
    houses = [swapped(q) for q in preview()["pieces"] if q["piece"] in ("house_pemakar_a", "house_pemakar_b", "smithy")]
    for i, q in enumerate(houses):
        size = (6.0, 5.0) if q["piece"] == "smithy" else ((5.0, 6.0) if q["piece"] == "house_pemakar_a" else (4.0, 6.5))
        out.append({"id": f"MapHouse{i}", "pos": [r3(q["at"][0]), 0.1, r3(q["at"][2])], "size": [size[0], 0.2, size[1]],
                    "yaw": r3(q["yaw_deg"])})
    for row in out:
        row["solid"] = False
    return out


def relayout() -> None:
    from ch08_corrow_relayout import dump

    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    g["doc"] = g["doc"].replace(
        "M3-C05-02: Pemakar (act1_ch05.md B01-B06, B11) as a greybox, flat for the controller (no step-up)",
        "M3-C05-02: Pemakar (act1_ch05.md B01-B06, B11), moved on to env-art's Pemakar kit (M3-C05-1213, ADR 0200: "
        "the kit's frame, tools/act1/ch05_pemakar_dressing.py: the harbour a quay at the shore, the market and the "
        "forge on tier 0, the inn on tier 2, the graves on tier 4, the crown channel on tier 9). It was a greybox, "
        "flat for the controller (no step-up)")
    g["sun"] = dict(NIGHT_SUN)
    blocks = []
    for b in g["blocks"]:
        if b["id"] in DROPPED:
            continue
        foot = to_kit(b["id"], [b["pos"][0], b["pos"][1] - b["size"][1] * 0.5, b["pos"][2]])
        row = dict(b, pos=[foot[0], r3(foot[1] + b["size"][1] * 0.5), foot[2]])
        if b["id"] == "Ferry":
            row.update(pos=[FERRY_AT[0], 1.6, FERRY_AT[2]], size=[26.0, 3.2, 6.8], solid=False)
        if b["id"] == "SeaCutWeir":  # the sea-cut's lip, east of the quay, in the water
            row.update(pos=[10.0, 0.2, r3(QUAY_FRONT_Z + 0.7)], size=[6.0, 0.4, 1.2], solid=False)
        if b["id"] == "WakeWall":
            row["yaw"] = 0.0
        if b["id"] == "Lamps":
            row.update(pos=on_tier(0, 0.0, 1.0), solid=False)
        if b["id"] == "CrownBell":
            row["pos"] = on_tier(TIERS - 1, 3.0, 4.0)
            row["pos"][1] = r3(row["pos"][1] + b["size"][1] * 0.5)
        blocks.append(row)
    g["blocks"] = blocks + map_blocks()
    g["spawns"] = {k: to_kit(k, v) for k, v in g["spawns"].items()}
    g["marks"] = {k: to_kit(k, v) for k, v in g["marks"].items()}
    g["actors"] = {k: dict(v, at=to_kit(k, v["at"])) for k, v in g["actors"].items()}
    shots = {}
    for k, v in g["shots"].items():
        if k in SHOTS:
            shots[k] = SHOTS[k]
            continue
        shots[k] = dict(v, pos=to_kit(k + ".pos", v["pos"]), look_at=to_kit(k + ".look", v["look_at"]))
    g["shots"] = shots
    for t in g["triggers"]:
        t["at"] = to_kit(t["id"], t["at"])
        if len(t["at"]) > 3:
            t["at"] = t["at"][:3]
        t["yaw"] = tier_yaw(t["at"][0], t["at"][2]) if t["at"][2] < 0.0 else 0.0
    for v in g.get("variants", []):
        v["environment_res"] = RES_ZONE + "pemakar_dusk_environment.tres"
    g["collision_path"] = RES_ZONE + "pemakar_collision.json"
    LAYOUT.write_text(dump(g), encoding="utf-8")


# --weir-relayout (once, after M3-ENV-1214): B05's weir folk move east with the weir to the quay's east end, keeping
# their spacing and facings (WEIR_DX), with the cameras that frame them; the dawn variant takes env-art's day grade.
WEIR_DX = 4.6
WEIR_MARKS = ("weir_step", "weir_guard", "weir_asha_in", "dawn_kerrid_in")
WEIR_ACTORS = ("kerrid", "weir_child", "boat_fisher")
WEIR_SHOTS = {
    "P11": {"pos": [21.0, 1.5, 31.5], "look_at": [15.0, 1.9, 26.6], "fov": 40},  # from the sea side, low
    "P12": {"pos": [17.1, 2.8, 25.425], "look_at": [14.6, 2.6, 26.5], "fov": 36},
    "P02D": {"pos": [3.0, 2.977, 22.05], "look_at": [12.6, 1.8, 26.5], "fov": 40},
}
DAY_SUN = {"pitch_deg": -24.0, "yaw_deg": -72.0, "energy": 2.4, "color": "#ffd9b0"}  # env-art's day: 24 deg / az 252


def weir_relayout() -> None:
    from ch08_corrow_relayout import dump

    g = json.loads(LAYOUT.read_text(encoding="utf-8"))

    def east(p: list) -> list:
        return [r3(min(p[0] + WEIR_DX, QUAY_HALF_X - 0.4))] + p[1:]

    for k in WEIR_MARKS:
        g["marks"][k] = east(g["marks"][k])
    for k in WEIR_ACTORS:
        g["actors"][k]["at"] = east(g["actors"][k]["at"])
    g["spawns"]["Weir"] = east(g["spawns"]["Weir"])
    g["shots"].update(WEIR_SHOTS)
    for b in g["blocks"]:
        if b["id"] == "SeaCutWeir":
            b.update(pos=[r3(WEIR_AT[0]), r3(WEIR_AT[1] + 0.2), r3(WEIR_AT[2])], size=[8.0, 0.4, 1.2])
    for v in g.get("variants", []):
        v["environment_res"] = RES_ZONE + "pemakar_day_environment.tres"
        v["sun"] = DAY_SUN
    LAYOUT.write_text(dump(g), encoding="utf-8")


def main() -> None:
    copy_grades()
    write_plume_night()
    if "--relayout" in sys.argv:
        relayout()
    if "--weir-relayout" in sys.argv:
        weir_relayout()
    night_fill()
    (ZONE / "pemakar_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "pemakar_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    for name, params in KIT_LOOKS.values():
        (ZONE / name).write_text(zl.bronze_material(name, params), encoding="utf-8")
    (ROOT / "assets/environments/kits/pemakar/materials" / (WEIR_STONE + ".tres")).write_text(
        zl.copy_material(KIT + "materials/kit_volcanic_dressed.tres", WEIR_STONE, WEIR_STONE_OVERRIDES, WEIR_STONE_ADDED),
        encoding="utf-8")


if __name__ == "__main__":
    main()
