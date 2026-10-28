#!/usr/bin/env python3
"""Ch7 the Tamsule Bell: env-art's Tamsule Bell kit (M3-ENV-01) dresses ch07/tamsule_bell_galleries (M3-C07-1211,
ADR 0200).

The kit's arena frame: the Bell's axis at the origin, the river datum at y 0, azimuth clockwise from north (-Z), so
90 is east. The catch-pool's coping is a ring at r 12.0-13.2 (y 0.6); the galleries are six segments (half-arc 25
deg) at azimuths 40, 90, 140, 220, 270, 320: a walkway at y 2.4 from r 32 to 33.6, then five seating tiers; the
captains' platforms run from the galleries at 90 and 270 in towards the pool (deck y 2.0, r 15.4-32, half-width 1.6),
each ending in a raised prow step (y 2.46, r 13-15.4), the naming place. Oruvel's gallery and prow are the west
(the party's; Tavi on the prow), Sorrin's the east. The two runs of galleries are parted by open water (the boat
lanes north and south), so Oruvel's empty moorings, which the preview sets at azimuth 35, are set on the party's side
at azimuth 325 (the preview's posts and boat there are left out): six posts in an arc at r 21, a staging of two
boardwalk modules behind them, reached by a third from the north-west gallery.

The greybox's story points have plain meanings, so each is placed by hand on the kit (SPAWNS, MARKS, ACTORS,
TRIGGERS, SHOTS; relayout()).

Writes next to the zone (game/levels/ch07/tamsule_bell_galleries/):
  tamsule_bell_galleries_dressing.json   the kit as the preview places it (the Bell, gantry, pool, galleries,
                                         platforms, moorings, posts, boats, pennants, the port's edge), the
                                         moorings' staging and its bridge, and Tavi's boat.
  tamsule_bell_galleries_collision.json  the walkways and their front rails, the tiers' fronts, the platforms, their
                                         rails and prow steps, the staging and its bridge, a floor under the water.
and copies the preview's grade and water. With --relayout it also moves the layout's story points (once).

    python3 tools/act1/ch07_tamsule_bell_dressing.py [--relayout]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "tamsule_bell"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bell as tb_bell  # noqa: E402
import gallery as tg  # noqa: E402
import port as tp  # noqa: E402
import preview_scene as tps  # noqa: E402
import waterline as tw  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch07" / "tamsule_bell_galleries"
LAYOUT = ZONE / "tamsule_bell_galleries_layout.json"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "tamsule_bell_kit"
RES_PREVIEW = "res://game/levels/_tests/tamsule_bell_kit/"
RES_ZONE = "res://game/levels/ch07/tamsule_bell_galleries/"
KIT = "res://assets/environments/kits/tamsule_bell/"
HALVES = ((15.0, 165.0), (195.0, 345.0))  # the galleries' two runs; the gaps north and south are open water
OURS, THEIRS = 270.0, 90.0  # Oruvel's gallery and platform (the party's), Sorrin's
WALK_R = (tg.R_FRONT + tg.R_WALK) * 0.5
PROW_R = (tg.PLATFORM_R[0], tg.PLATFORM_R[0] + 2.4)  # the raised prow step (gallery.build_platform)
PROW_Y = tg.PLATFORM_DECK_Y + 0.46
DECK = tg.PLATFORM_DECK_Y
MOOR_R, MOOR_AZ = 21.0, 325.0  # Oruvel's moorings: the preview's radius, on the party's run of galleries
CLEARED = {"OruvelMoorings", "Mooring10", "Mooring11", "Boat4"}  # the preview's, moved or in the way
MOOR_YAW = -MOOR_AZ
POSTS_X = [-6.0 + 12.0 * i / (tw.ORUVEL_POSTS - 1) for i in range(tw.ORUVEL_POSTS)]  # ring 1 (the name-peg) at -6
STAGING_Z = -2.0  # the staging's centre line in the moorings' frame (local +Z faces the arena, so out is -Z)
STAGING_HALF = 1.5  # boardwalk_8m is 8 m by 3 m
BOARD_Y = tp.DECK_Y
COPING = (tw.POOL_R[0] + tw.POOL_R[1]) * 0.5
WATER_FLOOR_Y = -0.6
RAIL_H = 1.1
ARC_STEP_DEG = 10.0


def r3(v: float) -> float:
    return round(float(v), 3)


def wrap(deg: float) -> float:
    return r3((deg + 180.0) % 360.0 - 180.0)


def polar(r: float, az: float, y: float = 0.0) -> list[float]:
    a = math.radians(az)
    return [r3(r * math.sin(a)), r3(y), r3(-r * math.cos(a))]


def inward(az: float) -> float:
    """Yaw (deg) of a box or piece at azimuth `az` whose local +Z points at the Bell's axis."""
    return wrap(-az)


def outward(az: float) -> float:
    """Yaw (deg) of a box or piece at azimuth `az` whose local +Z points away from the Bell's axis."""
    return wrap(180.0 - az)


def facing_in(az: float) -> float:
    """Yaw (deg) of an actor, mark or spawn at azimuth `az` facing the Bell's axis: they face their -Z (the cutscene
    sequencer turns an actor's -Z to its target), so it is the yaw whose +Z points out."""
    return outward(az)


def facing_out(az: float) -> float:
    return inward(az)


def moor(x: float, z: float, y: float = 0.0) -> list[float]:
    """A point in the moorings piece's own frame (X along the arc of posts, +Z towards the arena)."""
    o = polar(MOOR_R, MOOR_AZ)
    a = math.radians(MOOR_YAW)
    return [r3(o[0] + x * math.cos(a) + z * math.sin(a)), r3(y), r3(o[2] - x * math.sin(a) + z * math.cos(a))]


def ring(i: int) -> list[float]:
    x = POSTS_X[i - 1]
    return moor(x, 0.04 * x * x, 1.4)


def box(bid: str, pos: list[float], size: tuple[float, float, float], yaw: float) -> dict:
    return {"id": bid, "pos": [r3(v) for v in pos], "size": [r3(v) for v in size], "yaw": r3(yaw)}


def arc_box(bid: str, az0: float, az1: float, r0: float, r1: float, y0: float, y1: float, pad: float = 0.2) -> dict:
    """A box tangent to the ring at the middle azimuth, covering r0-r1 (a chord: arcs are cut in ARC_STEP_DEG)."""
    am = (az0 + az1) * 0.5
    span = 2.0 * r1 * math.sin(math.radians(abs(az1 - az0)) * 0.5) + pad
    return box(bid, polar((r0 + r1) * 0.5, am, (y0 + y1) * 0.5), (span, y1 - y0, r1 - r0), inward(am))


def radial_box(bid: str, az: float, r0: float, r1: float, half_w: float, y0: float, y1: float, side_m: float = 0.0
               ) -> dict:
    """A box along the radius at `az`, moved `side_m` sideways (positive: clockwise)."""
    c = polar((r0 + r1) * 0.5, az, (y0 + y1) * 0.5)
    t = polar(side_m, az + 90.0)
    return box(bid, [c[0] + t[0], c[1], c[2] + t[2]], (2 * half_w, y1 - y0, r1 - r0), inward(az))


def moor_box(bid: str, x0: float, x1: float, z0: float, z1: float, y0: float, y1: float) -> dict:
    return box(bid, moor((x0 + x1) * 0.5, (z0 + z1) * 0.5, (y0 + y1) * 0.5), (x1 - x0, y1 - y0, z1 - z0), MOOR_YAW)


def ramp(rid: str, a: list[float], b: list[float], width: float) -> dict:
    return {"id": rid, "from": a, "to": b, "width": r3(width)}


def arcs(a0: float, a1: float, step: float = ARC_STEP_DEG) -> list[tuple[float, float]]:
    n = max(1, int(math.ceil((a1 - a0) / step - 1e-9)))
    return [(a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n) for i in range(n)]


def openings() -> list[tuple[float, float]]:
    """Azimuth spans where the walkways' front rail is open: the two platforms and the moorings' bridge."""
    out = []
    for az, half_m in ((OURS, tg.PLATFORM_HALF_W), (THEIRS, tg.PLATFORM_HALF_W), (MOOR_AZ, STAGING_HALF)):
        d = math.degrees(half_m / tg.R_FRONT)
        out.append((az - d, az + d))
    return out


def front_rail(k: int, b0: float, b1: float) -> list[dict]:
    """The walkway's front rail over b0-b1, with the openings cut out."""
    spans = [(b0, b1)]
    for g0, g1 in openings():
        nxt = []
        for s0, s1 in spans:
            if g1 <= s0 or g0 >= s1:
                nxt.append((s0, s1))
                continue
            if g0 > s0:
                nxt.append((s0, g0))
            if g1 < s1:
                nxt.append((g1, s1))
        spans = nxt
    return [arc_box(f"WalkRail{k}_{j}", s0, s1, tg.R_FRONT - 0.25, tg.R_FRONT, tg.DECK_Y, tg.DECK_Y + RAIL_H, 0.0)
            for j, (s0, s1) in enumerate(spans) if s1 - s0 > 0.2]


def bridge_r() -> tuple[float, float]:
    """The bridge's radii at the moorings' azimuth: from the staging's outer edge to the walkway's front."""
    return MOOR_R - STAGING_Z + STAGING_HALF, tg.R_FRONT


def collision() -> dict:
    blocks: list[dict] = [{"id": "WaterFloor", "pos": [0.0, WATER_FLOOR_Y - 0.5, 0.0], "size": [400.0, 1.0, 400.0]}]
    ramps: list[dict] = []
    k = 0
    for h, (a0, a1) in enumerate(HALVES):
        for b0, b1 in arcs(a0, a1):
            blocks.append(arc_box(f"Walk{k}", b0, b1, tg.R_FRONT, tg.R_WALK, tg.DECK_Y - 1.0, tg.DECK_Y))
            blocks.append(arc_box(f"TierFront{k}", b0, b1, tg.R_WALK, tg.R_WALK + 0.4, tg.DECK_Y, tg.DECK_Y + 3.0))
            blocks += front_rail(k, b0, b1)
            k += 1
        for i, a in enumerate((a0, a1)):
            blocks.append(radial_box(f"WalkEnd{h}{i}", a, tg.R_FRONT - 0.3, tg.R_WALK + 0.4, 0.2, tg.DECK_Y,
                                     tg.DECK_Y + RAIL_H))
    hw = tg.PLATFORM_HALF_W
    for name, az in (("Our", OURS), ("Their", THEIRS)):
        deck0 = PROW_R[1]
        blocks.append(radial_box(f"{name}Platform", az, deck0, tg.R_FRONT - 1.6, hw, DECK - 1.0, DECK))
        blocks.append(radial_box(f"{name}Prow", az, PROW_R[0], deck0 - 0.5, hw - 0.25, PROW_Y - 1.0, PROW_Y))
        blocks.append(radial_box(f"{name}ProwEnd", az, PROW_R[0] - 0.2, PROW_R[0], hw, PROW_Y, PROW_Y + RAIL_H))
        for side in (-1.0, 1.0):
            blocks.append(radial_box(f"{name}Rail{'LR'[side > 0]}", az, PROW_R[0], tg.R_FRONT, 0.1, DECK,
                                     DECK + RAIL_H, side * (hw + 0.1)))
        # up from the deck to the walkway, and up on to the prow step
        ramps.append(ramp(f"{name}ToWalk", polar(tg.R_FRONT - 1.6, az, DECK), polar(tg.R_FRONT + 0.4, az, tg.DECK_Y),
                          2 * hw))
        ramps.append(ramp(f"{name}ToProw", polar(deck0 + 0.6, az, DECK), polar(deck0 - 0.5, az, PROW_Y), 2 * hw - 0.5))
    # the pool's coping, where the poolkeeper and the divers stand (the player never reaches it: the prows end in rails)
    for i, (b0, b1) in enumerate(arcs(0.0, 360.0)):
        blocks.append(arc_box(f"Coping{i}", b0, b1, tw.POOL_R[0], tw.POOL_R[1], tw.POOL_COPING_Y - 1.0,
                              tw.POOL_COPING_Y))
    # the moorings: the staging behind the posts and the bridge up to the north-west gallery's walkway
    st0, st1 = STAGING_Z - STAGING_HALF, STAGING_Z + STAGING_HALF
    blocks.append(moor_box("Staging", -8.0, 8.0, st0, st1, BOARD_Y - 1.0, BOARD_Y))
    blocks.append(moor_box("StagingRailIn", -8.0, 8.0, st1 - 0.1, st1 + 0.1, BOARD_Y, BOARD_Y + RAIL_H))
    for nm, x0, x1 in (("StagingRailOutW", -8.0, -STAGING_HALF), ("StagingRailOutE", STAGING_HALF, 8.0)):
        blocks.append(moor_box(nm, x0, x1, st0 - 0.1, st0 + 0.1, BOARD_Y, BOARD_Y + RAIL_H))
    for nm, x in (("StagingEndW", -8.1), ("StagingEndE", 8.1)):
        blocks.append(moor_box(nm, x - 0.1, x + 0.1, st0, st1, BOARD_Y, BOARD_Y + RAIL_H))
    r0, r1 = bridge_r()
    for side in (-1.0, 1.0):
        blocks.append(radial_box(f"BridgeRail{'LR'[side > 0]}", MOOR_AZ, r0, r1, 0.1, BOARD_Y, tg.DECK_Y + RAIL_H,
                                 side * (STAGING_HALF + 0.1)))
    ramps.append(ramp("Bridge", polar(r0 - 0.4, MOOR_AZ, BOARD_Y), polar(r1 + 0.4, MOOR_AZ, tg.DECK_Y),
                      2 * STAGING_HALF))
    return {"_about": "Generated by tools/act1/ch07_tamsule_bell_dressing.py (ADR 0200); do not edit by hand.",
            "blocks": blocks, "ramps": ramps}


# The Bell's weeping column (M3-ENV-1321, taking M3-RND-26's column half under ADR 0041): the kit's weep_column
# (b_column.py) on the Column block's foot, its slots dressed with this zone's own still water, lit from within
# (WEEP_MATERIALS, written here; the port's column uses the same files).
WEEP_MATERIALS = {
    # turquoise_shallow under turquoise_shallow's +1 on-screen glow: the drop's own cyan (M3-RND-26)
    "weep_column_water_material": {"albedo": "Color(0.247, 0.816, 0.788, 0.5)", "emission": "Color(0.612, 0.831, 0.824, 1)",
                                   "energy": 0.6},
    "weep_spray_water_material": {"albedo": "Color(0.918, 0.973, 0.98, 0.4)", "emission": "Color(0.875, 0.973, 1, 1)",
                                  "energy": 0.35},
}
WEEP_SLOTS = {"tb_drop_proxy": "weep_column_water_material", "tb_salt_glass": "weep_spray_water_material"}


def write_weep_materials() -> None:
    for name, m in WEEP_MATERIALS.items():
        (ZONE / f"{name}.tres").write_text(
            '[gd_resource type="StandardMaterial3D" load_steps=1 format=3]\n\n[resource]\n'
            f'resource_name = "{name}"\ntransparency = 1\ncull_mode = 2\nshading_mode = 0\n'
            f"albedo_color = {m['albedo']}\nemission_enabled = true\nemission = {m['emission']}\n"
            f"emission_energy_multiplier = {m['energy']}\n", encoding="utf-8")


def weep_row(piece: str, block: dict) -> dict:
    # Its foot on the catch-pool's water (the kit's pool; the block's foot is the river datum)
    return {"piece": piece, "at": [r3(block["pos"][0]), r3(block["pos"][2])],
            "y": r3(block["pos"][1] - block["size"][1] * 0.5 + tb_bell.POOL_WATER_Y), "yaw_deg": 0.0, "kit_dir": KIT,
            "materials": dict(WEEP_SLOTS), "materials_dir": RES_ZONE, "block": block["id"]}


# The held drop itself (M3-RND-26): Rendering's WaterSphereRig on the kit's SphereAnchor (the contract's centre).
DROP_PROFILE = "tamsule_drop"


def drop_rows() -> list[dict]:
    return [{"name": "Drop", "at": [r3(v) for v in tb_bell.DROP_CENTER], "profile": DROP_PROFILE}]


def dressing() -> dict:
    pieces = []
    for name, piece, pos, yaw, scale in tps.layout():
        if piece == "reefball_drop_proxy" or name in CLEARED:
            continue
        row = {"piece": piece, "at": [r3(pos[0]), r3(pos[2])], "y": r3(pos[1]), "yaw_deg": r3(yaw)}
        if scale != 1.0:
            row["scale"] = scale
        pieces.append(row)
    o = moor(0.0, 0.0)
    pieces.append({"piece": "oruvel_moorings", "at": [o[0], o[2]], "y": 0.0, "yaw_deg": wrap(MOOR_YAW)})
    for x in (-4.0, 4.0):  # the staging, its rail (+Z) along the posts
        p = moor(x, STAGING_Z)
        pieces.append({"piece": "boardwalk_8m", "at": [p[0], p[2]], "y": 0.0, "yaw_deg": r3(MOOR_YAW)})
    r0, r1 = bridge_r()
    p = polar((r0 + r1) * 0.5, MOOR_AZ)
    # the bridge's deck sits halfway between the staging's and the walkway's (its collision is a ramp)
    pieces.append({"piece": "boardwalk_8m", "at": [p[0], p[2]], "y": r3((tg.DECK_Y - BOARD_Y) * 0.5),
                   "yaw_deg": r3(90.0 - MOOR_AZ)})
    boat = moor(2.0, STAGING_Z - STAGING_HALF - 1.4)
    pieces.append({"piece": "watch_boat", "at": [boat[0], boat[2]], "y": 0.0, "yaw_deg": r3(MOOR_YAW + 3.0)})
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    pieces.append(weep_row("weep_column", next(b for b in g["blocks"] if b["id"] == "Column")))
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch07_tamsule_bell_dressing.py from env-art's Tamsule Bell kit (M3-ENV-01); "
        "do not edit by hand. The kit's arena frame.",
        "seed": 7,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + "tamsule_noon_environment.tres",
        "time_of_day_h": 12.25,
        "greybox": {"hide_all": True, "keep": []},
        "pieces": pieces,
        "drops": drop_rows(),
    }


def copy_grades() -> None:
    for name in ("tamsule_noon_environment.tres", "tamsule_water_material.tres"):
        text = (PREVIEW / name).read_text(encoding="utf-8").replace(RES_PREVIEW, RES_ZONE)
        (ZONE / name).write_text(text, encoding="utf-8")


# --- the one-time move of the story points ----------------------------------------------------------------------
def _on(az: float, r: float, y: float, yaw: float | None = None) -> list[float]:
    p = polar(r, az, y)
    return p + [r3(yaw % 360.0)] if yaw is not None else p


def _side(az: float, r: float, y: float, side_m: float, yaw: float) -> list[float]:
    """On the platform at azimuth `az`, `side_m` across it (positive: clockwise)."""
    return _on(az + math.degrees(side_m / r), r, y, yaw)


def _moor(x: float, z: float, y: float, yaw: float) -> list[float]:
    return moor(x, z, y) + [r3(yaw % 360.0)]


FACE_POSTS, FACE_OUT = MOOR_YAW + 180.0, MOOR_YAW  # the moorings frame's +Z faces the arena; an actor faces its -Z
SPAWNS = {
    "Entrance": _on(250.0, WALK_R, tg.DECK_Y, facing_in(250.0) - 60.0),
    "Gallery": _on(262.0, WALK_R, tg.DECK_Y, facing_in(262.0)),
    "PoolSteps": _on(OURS, 17.6, DECK, facing_in(OURS)),
    "CatchPool": _on(OURS, 19.6, DECK, facing_in(OURS)),
}
MARKS = {
    "divers_boat": _on(290.0, COPING, tw.POOL_COPING_Y, facing_out(290.0)),  # on the coping, toward their moorings
    "tavi_leaves": _on(OURS, 30.6, DECK, facing_out(OURS)),  # B07: Tavi walks up his platform, away from the pool
    "tavi_away": _moor(-7.4, STAGING_Z, BOARD_Y, 90.0 - MOOR_YAW),  # B09: off along the staging (then hidden)
    "asha_staging": _moor(1.5, STAGING_Z - 0.6, BOARD_Y, FACE_POSTS),  # B09: where Asha waits as the scene opens
    "poolkeeper_rim": _on(279.0, COPING, tw.POOL_COPING_Y, facing_out(279.0)),
    "bell_ribs": [0.0, 38.0, 0.0],
    "drop": [0.0, 31.5, 0.0],
    "column_foot": [0.0, 0.5, 0.0],
    "tavi_boat": _moor(2.0, STAGING_Z - STAGING_HALF + 0.5, BOARD_Y, FACE_OUT),
    "asha_rim": _side(OURS, 17.0, DECK, -0.9, facing_in(OURS)),
    "toma_rim": _side(OURS, 17.6, DECK, 0.9, facing_in(OURS)),
    "liss_rim": _side(OURS, 18.6, DECK, -0.9, facing_in(OURS)),
    "ysolde_rim": _side(OURS, 19.2, DECK, 0.9, facing_in(OURS)),
    "rhen_moorings": _moor(-4.5, STAGING_Z - 0.3, BOARD_Y, FACE_POSTS),
    "asha_ring_1": _moor(POSTS_X[0] + 0.3, STAGING_Z + 0.9, BOARD_Y, FACE_POSTS),
    "asha_ring_3": _moor(POSTS_X[2], STAGING_Z + 0.9, BOARD_Y, FACE_POSTS),
    "asha_ring_6": _moor(POSTS_X[5] - 0.4, STAGING_Z + 0.9, BOARD_Y, FACE_POSTS),
    "rhen_ring_6": _moor(POSTS_X[5] - 1.2, STAGING_Z + 0.9, BOARD_Y, FACE_POSTS),
    "kerrid_far": _on(4.0, 52.0, -0.5, facing_in(4.0)),
    "ring_wicklight": ring(3) + [r3(FACE_POSTS % 360.0)],
    "ring_gull": ring(6) + [r3(FACE_POSTS % 360.0)],
    "river_mouth": _on(185.0, 80.0, 0.0, facing_out(185.0)),
}
ACTORS = {
    # seated at the head of Oruvel's platform, each in line with their rim mark, so B07's walk is straight down it
    "asha": _side(OURS, 32.4, tg.DECK_Y, -0.9, facing_in(OURS)),
    "toma": _side(OURS, 32.4, tg.DECK_Y, 0.9, facing_in(OURS)),
    "liss": _side(OURS, 33.2, tg.DECK_Y, -0.9, facing_in(OURS)),
    "ysolde": _side(OURS, 33.2, tg.DECK_Y, 0.9, facing_in(OURS)),
    "kerrid": _on(0.0, 48.0, -0.5, facing_out(0.0)),  # knee-deep, his back to the Bell
    "tavi": _on(OURS, 14.4, PROW_Y, facing_out(OURS)),
    "ione": _on(THEIRS, 14.4, PROW_Y, facing_in(THEIRS)),
    "poolkeeper": _on(300.0, COPING, tw.POOL_COPING_Y, facing_in(300.0)),
    "oruvel_diver_1": _on(264.0, COPING, tw.POOL_COPING_Y, facing_in(264.0)),
    "oruvel_diver_2": _on(259.0, COPING, tw.POOL_COPING_Y, facing_in(259.0)),
    "sorrin_diver_1": _on(96.0, COPING, tw.POOL_COPING_Y, facing_in(96.0)),
    "sorrin_diver_2": _on(101.0, COPING, tw.POOL_COPING_Y, facing_in(101.0)),
}
TRIGGERS = {  # (at, size, yaw); a trigger's size is in its own frame
    "rim": (_on(OURS, 16.2, DECK), [2 * tg.PLATFORM_HALF_W, 0.0, 1.2], facing_in(OURS)),
    "moorings": (moor(2.0, STAGING_Z, BOARD_Y), [3.0, 0.0, 2.6], MOOR_YAW),
    "to_port": (_on(244.0, WALK_R, tg.DECK_Y), [3.0, 0.0, 2.0], facing_in(244.0)),
}


def _shot(pos: list[float], look: list[float], fov: float) -> dict:
    return {"pos": [r3(v) for v in pos[:3]], "look_at": [r3(v) for v in look[:3]], "fov": fov}


def _head(p: list[float], h: float = 1.55) -> list[float]:
    return [p[0], p[1] + h, p[2]]


SHOTS = {
    "R01": _shot(_on(292.0, 37.0, 7.6), _on(OURS, 15.0, 2.6), 55),
    "R01A": _shot(_on(275.0, 30.6, 3.9), _head(ACTORS["asha"]), 24),
    "R02": _shot(_on(OURS, 18.0, 3.4), [0.0, 31.5, 0.0], 62),
    "R02K": _shot(_on(338.0, 33.4, 4.2), _head(ACTORS["kerrid"], 1.0), 30),
    "R03": _shot(_on(OURS, 31.2, 4.6), _on(OURS, 14.4, 3.4), 58),
    "R04": _shot(_on(OURS, 16.8, PROW_Y + 1.5), _head(ACTORS["tavi"]), 28),
    "R05": _shot([0.0, 25.0, 0.1], [0.0, 0.0, 0.0], 70),
    "R06": _shot(_on(254.0, COPING, 1.4), _head(ACTORS["tavi"], 1.2), 45),
    "R07": _shot(_on(286.0, WALK_R, 4.6), moor(0.0, 0.0, 1.0), 50),
    "R08": _shot(_on(MOOR_AZ - 4.0, 30.5, 4.2), moor(0.0, 0.0, 0.6), 55),
    "R09": _shot(moor(-1.2, STAGING_Z + 0.6, 2.1), ring(5), 40),
}


MAP_GALLERY_STEP_DEG = 25.0


def map_blocks() -> list[dict]:
    """Flat, non-solid blocks for the area map (ZoneMapShapes reads only the layout's blocks; M3-UI-1212): the
    walkways, platforms, staging and bridge as pads, the galleries' tiers as buildings (zone_maps.json hints)."""
    out = []
    for i, (b0, b1) in enumerate(a for h in HALVES for a in arcs(*h)):
        out.append(arc_box(f"MapWalk{i}", b0, b1, tg.R_FRONT, tg.R_WALK, 0.0, 0.2))
    for i, (b0, b1) in enumerate(a for h in HALVES for a in arcs(*h, step=MAP_GALLERY_STEP_DEG)):
        out.append(arc_box(f"MapGallery{i}", b0, b1, tg.R_WALK, tg.R_BACK, 0.0, 0.2))
    for name, az in (("MapPlatformW", OURS), ("MapPlatformE", THEIRS)):
        out.append(radial_box(name, az, PROW_R[0], tg.R_FRONT, tg.PLATFORM_HALF_W, 0.0, 0.2))
    out.append(moor_box("MapStaging", -8.0, 8.0, STAGING_Z - STAGING_HALF, STAGING_Z + STAGING_HALF, 0.0, 0.2))
    out.append(radial_box("MapBridge", MOOR_AZ, *bridge_r(), STAGING_HALF, 0.0, 0.2))
    for row in out:
        row["solid"] = False
    return out


def relayout() -> None:
    from ch08_corrow_relayout import dump

    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    g["doc"] = g["doc"].replace(
        "M3-C07-02 greybox STAND-IN", "M3-C07-02 greybox, moved on to env-art's Tamsule Bell kit (M3-C07-1211, ADR "
        "0200: the kit's arena frame, tools/act1/ch07_tamsule_bell_dressing.py; the galleries are the west, Oruvel's, "
        "the rim is Oruvel's prow, the moorings at azimuth 325, on the party's side). It was a STAND-IN")
    g["sun"] = {"pitch_deg": -78.0, "yaw_deg": 0.0, "energy": 3.2, "color": "#fff3e7"}
    keep = []
    for b in g["blocks"]:
        if b["id"] == "Column":  # the weeping column, from the pool up to the drop (the kit's SphereAnchor)
            keep.append(dict(b, pos=[0.0, 15.75, 0.0], size=[0.5, 31.5, 0.5]))
        elif b["id"] == "River":
            keep.append(dict(b, pos=[0.0, -1.5, 0.0], size=[260.0, 1.0, 260.0], solid=False))
        elif b["id"] == "CatchPool":
            keep.append(dict(b, pos=[0.0, 0.02, 0.0], size=[24.0, 0.04, 24.0]))
    g["blocks"] = keep + map_blocks()
    g["spawns"] = SPAWNS
    g["marks"] = MARKS
    g["actors"] = {k: dict(v, at=ACTORS[k]) for k, v in g["actors"].items()}
    g["shots"] = SHOTS
    for t in g["triggers"]:
        at, size, yaw = TRIGGERS[t["id"]]
        t.update(at=at, size=size, yaw=yaw)
    g["collision_path"] = RES_ZONE + "tamsule_bell_galleries_collision.json"
    LAYOUT.write_text(dump(g), encoding="utf-8")


def main() -> None:
    copy_grades()
    write_weep_materials()
    if "--relayout" in sys.argv:
        relayout()
    (ZONE / "tamsule_bell_galleries_collision.json").write_text(json.dumps(collision(), indent=1) + "\n",
                                                                encoding="utf-8")
    (ZONE / "tamsule_bell_galleries_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n",
                                                               encoding="utf-8")


if __name__ == "__main__":
    main()
