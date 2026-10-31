#!/usr/bin/env python3
"""Ch10 "Fen of the Kirru" greybox (M4-C10-02): the geography of ch10/ossa_fen and ch10/reedhollow, before the beat
sheet (M4-C10-01) adds the story. From act_outline.md (Ch10), act1_ch09.md §10 (where Act II starts) and the colour
script's `ch10` (overcast dusk 18:20, a sun 2 deg up in the west, tannin water).

  ch10/ossa_fen   the fen's edge, a dry bank where the coast road ends (FenEdge; Pell stops here, the first image of
                  Act II), then the Kirru's root-walks east over brown-black water between mangrove trunks: five
                  bends, a side pocket north (a rest point), the Drowner's clearing (a round platform in the roots,
                  the boss's arena) and the way on to Reedhollow.
  ch10/reedhollow the Kirru village: a reed causeway from the fen to a ring of platforms round the lagoon, reed houses
                  on their own platforms off the ring, and the shore on the lagoon's east side where the clutch stands
                  for the farewell-tide.

Greybox collision is boxes and the controller has no step-up, so every walk is level at y 0 with root rails along its
edges; the water is a surface at WATER_Y over a bed the rails keep everyone out of. x is east, north is -Z.

    python3 tools/act2/ch10_greybox.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONES = ROOT / "game" / "levels" / "ch10"
WATER_Y = -0.3
BED_Y = -1.6
WALK_W = 3.6
WALK_T = 0.5
RAIL = (0.4, 0.5)  # root rails: width, height above the walk
TRUNK = (0.7, 7.0)  # mangrove trunks: width, height
TRUNK_STEP_M = 7.0  # one trunk each side every this far along a walk, set back from its edge
TRUNK_BACK_M = 2.4
COL_WALK = "#4a3c2c"
COL_RAIL = "#2e241a"
COL_TRUNK = "#3a3026"
COL_WATER = "#3a2a18"
COL_BED = "#1e1511"
COL_BANK = "#4f4a3a"
COL_REED = "#9a8a62"
COL_PLATFORM = "#5a4a34"
SUN = {"pitch_deg": -8.0, "yaw_deg": -85.0, "energy": 0.9, "color": "#fffefa"}  # low in the west (elevation 2 deg)
ENV = {"background": "#9a9488", "ambient_color": "#6f7e8e", "ambient_energy": 0.85}  # M4-A2P-0401: 0.5 left the bank black at eye height
PARTY = ["rhen", "asha", "toma"]


def r3(v: float) -> float:
    return round(float(v), 3)


def box(bid: str, x: float, y: float, z: float, sx: float, sy: float, sz: float, yaw: float = 0.0, **kw) -> dict:
    row = {"id": bid, "pos": [r3(x), r3(y), r3(z)], "size": [r3(sx), r3(sy), r3(sz)]}
    if yaw:
        row["yaw"] = r3(yaw)
    row.update(kw)
    return row


def walk(bid: str, a: tuple[float, float], b: tuple[float, float], rails: tuple[bool, bool] = (True, True),
         trim: float = 0.0, posts: tuple[str, float, float, str] = ("Trunk", TRUNK[0], TRUNK[1], COL_TRUNK),
         colors: tuple[str, str] = (COL_WALK, COL_RAIL)) -> list[dict]:
    """A level walk from a to b (overlapping its neighbours by half its width), its two rails (trimmed `trim` m short at
    each end, so junctions stay open) and posts along both sides (`posts`: name, width, height, colour; Ch10's mangrove
    trunks by default, Ch11's drowned pillars)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(-dz, dx))  # Godot: the box's local x along a -> b
    mx, mz = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
    nx, nz = -dz / length, dx / length  # left of a -> b
    post_name, post_w, post_h, post_col = posts
    out = [box(bid, mx, -WALK_T * 0.5, mz, length + WALK_W, WALK_T, WALK_W, yaw, color=colors[0])]
    for side, on in zip((1.0, -1.0), rails):
        off = side * (WALK_W * 0.5 + RAIL[0] * 0.5)
        if on:
            out.append(box(f"{bid}Rail{'LR'[side < 0]}", mx + nx * off, RAIL[1] * 0.5, mz + nz * off,
                           max(length - 2.0 * trim, 0.5), RAIL[1], RAIL[0], yaw, color=colors[1]))
        k = 0
        s = TRUNK_STEP_M * 0.5
        while s < length:
            t = s / length
            back = side * (WALK_W * 0.5 + TRUNK_BACK_M + (0.8 if k % 2 else 0.0))
            out.append(box(f"{bid}{post_name}{'LR'[side < 0]}{k}", a[0] + dx * t + nx * back, post_h * 0.5 + WATER_Y,
                           a[1] + dz * t + nz * back, post_w, post_h, post_w, color=post_col, solid=False))
            k += 1
            s += TRUNK_STEP_M
    return out


def water(x0: float, x1: float, z0: float, z1: float, color: str = COL_WATER) -> list[dict]:
    return [box("Water", (x0 + x1) * 0.5, WATER_Y - 0.05, (z0 + z1) * 0.5, x1 - x0, 0.1, z1 - z0, color=color,
                solid=False),
            box("Bed", (x0 + x1) * 0.5, BED_Y - 0.5, (z0 + z1) * 0.5, x1 - x0, 1.0, z1 - z0, color=COL_BED)]


# --- Ossa Fen ---------------------------------------------------------------------------------------------------------

def follow_volumes(prefix: str, route: list[tuple[float, float]], back_m: float = 5.0, up_m: float = 4.5) -> list[dict]:
    """M4-A2P-010: a pan-follow camera volume per walk run (the hub orbit looks through the mangrove trunks): the camera
    stands back_m behind the run's start, up_m up, and looks down the walk between the trunk rows."""
    out = []
    for i, (a, b) in enumerate(zip(route, route[1:])):
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz)
        ux, uz = dx / n, dz / n
        out.append({"id": f"{prefix}{i}", "mode": "pan_follow",
                    "at": [r3((a[0] + b[0]) / 2), 1.5, r3((a[1] + b[1]) / 2)],
                    "size": [r3(abs(dx) + WALK_W), 4.0, r3(abs(dz) + WALK_W)],
                    "pos": [r3(a[0] - ux * back_m), up_m, r3(a[1] - uz * back_m)],
                    "look_at": [r3((a[0] + b[0]) / 2), 0.8, r3((a[1] + b[1]) / 2)], "fov": 50, "priority": 1})
    return out


FEN_ROUTE = [(0.0, 0.0), (24.0, 5.0), (40.0, -9.0), (62.0, -6.0), (84.0, 8.0), (104.0, 1.0)]  # into the clearing
FEN_POCKET = ((62.0, -6.0), (66.0, -24.0))
CLEARING = (112.0, 0.0, 9.0)  # the Drowner's clearing: centre x, z and half size
FEN_EXIT = ((121.0, 0.0), (140.0, 0.0))


def ossa_fen() -> dict:
    blocks = water(-10.0, 160.0, -45.0, 40.0)
    blocks.append(box("Bank", -14.0, -0.5, 0.0, 28.0, 1.0, 30.0, color=COL_BANK))  # the fen's edge (dry)
    blocks.append(box("BankBoundW", -28.5, 1.0, 0.0, 1.0, 2.0, 30.0, color=COL_BANK))
    for i, (a, b) in enumerate(zip(FEN_ROUTE, FEN_ROUTE[1:])):
        blocks += walk(f"Walk{i}", a, b, trim=WALK_W * 0.5)
    blocks += walk("Pocket", *FEN_POCKET, trim=WALK_W * 0.5)
    blocks.append(box("PocketEnd", 66.0, -0.25, -27.0, 6.0, WALK_T, 6.0, color=COL_WALK))
    cx, cz, h = CLEARING
    blocks.append(box("Clearing", cx, -0.25, cz, 2 * h, WALK_T, 2 * h, color=COL_WALK))
    gap = WALK_W * 0.5 + 0.5  # the west and east edges open where the walks come in (z about 0)
    edges = [(0.0, -h, 2 * h, 0.4), (0.0, h, 2 * h, 0.4)]
    for ex in (-h, h):
        edges += [(ex, -(h + gap) * 0.5, 0.4, h - gap), (ex, (h + gap) * 0.5, 0.4, h - gap)]
    for k, (dx, dz, sx, sz) in enumerate(edges):
        blocks.append(box(f"ClearingRoots{k}", cx + dx, 0.6, cz + dz, sx, 1.2, sz, color=COL_TRUNK))
    blocks.append(box("DrownerRoots", cx + 3.0, 1.5, cz - 6.5, 6.0, 3.0, 2.0, color=COL_TRUNK, solid=False))
    blocks += walk("Exit", *FEN_EXIT, trim=WALK_W * 0.5)
    blocks.append(box("ExitBound", 141.5, 1.0, 0.0, 1.0, 2.0, WALK_W + 1.0, color=COL_RAIL))
    return {
        "doc": "M4-C10-02 greybox (tools/act2/ch10_greybox.py; do not edit by hand): Ossa Fen at the overcast dusk "
        "(colour script ch10). The fen's edge is the dry bank at the west, where the coast road from Corrow ends and "
        "Pell stops (act1_ch09.md §10: the first image of Act II); the Kirru's root-walks run east over tannin water "
        "between mangrove trunks, a side pocket north, the Drowner's clearing (the boss's arena, DrownerArena) and "
        "the way on to Reedhollow (to_reedhollow). The story waits on the beat sheet (M4-C10-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_WALK,
        "blocks": blocks,
        "spawns": {"FenEdge": [-8.0, 0.0, 0.0, 270.0], "DrownerArena": [104.0, 0.0, 0.0, 270.0],
                   "FromReedhollow": [134.0, 0.0, 0.0, 90.0]},
        "marks": {"pell_edge": [-3.0, 0.0, 2.5, 270.0], "fen_mouth": [2.0, 0.0, 0.0, 270.0],
                  "pocket_end": [66.0, 0.0, -27.0, 0.0],
                  # M4-A2P-010 (docs/kb/plan/act2/chapters/ch10.md): where C4's party stands at the clearing's mouth
                  "clearing_asha": [104.0, 0.0, 1.8, 270.0], "clearing_toma": [104.0, 0.0, -1.8, 270.0]},
        "actors": {"pell": {"at": [-3.0, 0.0, 2.5, 270.0], "color": "#7a8a6a", "radius": 0.34, "height": 1.9}},
        "shots": {"F01": {"pos": [-14.0, 2.2, 6.0], "look_at": [20.0, 1.0, 0.0], "fov": 40},
                  # M4-A2P-010: C1 Pell at the fen's edge (from low over the water, his face, the party behind);
                  # C4 the Drowner's clearing, wide and low; the root-lift from below, tilting up with the motes
                  "F02": {"pos": [3.95, 1.21, -2.71], "look_at": [-4.0, 1.4, 1.5], "fov": 40},
                  "F03": {"pos": [98.14, 1.0, 3.22], "look_at": [115.0, 2.0, -6.0], "fov": 50},
                  "F04": {"pos": [110.0, 0.6, -2.0], "look_at": [115.0, 5.0, -6.5], "fov": 55}},
        "camera_volumes": follow_volumes("Walk", FEN_ROUTE) + follow_volumes("Pocket", list(FEN_POCKET))
        + follow_volumes("Exit", list(FEN_EXIT))
        + [{"id": "Clearing", "mode": "pan_follow", "at": [112.0, 1.5, 0.0], "size": [18.0, 4.0, 18.0],
            # the camera stands in the clearing's east side, back to the Drowner's water, and looks west over the platform
            # at the way in (the POI stills, 10-30: from outside the root ring it sat in the mangrove canopy)
            "pos": [118.0, 5.0, 6.0], "look_at": [106.0, 0.8, 0.0], "fov": 55, "priority": 2}],
        "triggers": [{"id": "clearing", "activation": "touch", "at": [96.0, 0.0, 0.5], "size": [2.0, 0, WALK_W],
                      "requires_flag": "ch10_started", "blocked_by_flag": "ch10_drowner_defeated",
                      "payload": {"beat": "drowner"}, "yaw": 0.0},  # M4-A2P-010: the Drowner's clearing
                     {"id": "to_reedhollow", "activation": "touch", "at": [138.0, 0.0, 0.0], "size": [2.0, 0, WALK_W],
                      "requires_flag": "ch10_drowner_defeated", "payload": {"beat": "to_reedhollow"}, "yaw": 0.0}],
        # M4-C10-03: the root-walks' random fights (act2_roster.md Ch10); none in Reedhollow (the roster's proposal)
        "encounters": {"table": [{"encounter": "ch10_fen_archers", "weight": 2}, {"encounter": "ch10_fen_roots", "weight": 1},
                                 {"encounter": "ch10_fen_leeches", "weight": 1}],
                       "min_m": 95, "max_m": 145, "when": {"set": ["ch10_started"]}, "seed": 10},
    }


# --- Reedhollow -------------------------------------------------------------------------------------------------------

LAGOON = (44.0, 0.0, 14.0)  # centre x, z and the ring's middle radius
RING_N = 12
HOUSES = (1, 2, 4, 5, 7, 8, 10, 11)  # ring segments with a house off their outer edge (0 is east: the shore)
HOUSE = (6.0, 4.0, 6.0)


def reedhollow() -> dict:
    cx, cz, r = LAGOON
    blocks = water(-10.0, 80.0, -30.0, 30.0)
    blocks += walk("Causeway", (0.0, 0.0), (cx - r, 0.0), trim=WALK_W * 0.5)
    blocks.append(box("CausewayBoundW", -2.5, 1.0, 0.0, 1.0, 2.0, WALK_W + 1.0, color=COL_RAIL))
    seg = 2 * math.pi / RING_N
    pts = [(cx + r * math.cos(i * seg), cz - r * math.sin(i * seg)) for i in range(RING_N)]
    for i in range(RING_N):
        a, b = pts[i], pts[(i + 1) % RING_N]
        # the ring's outer rail stays open where the causeway (west, segments 5-6) and the houses join it
        outer_open = i in HOUSES or i in (5, 6)
        blocks += walk(f"Ring{i}", a, b, rails=(not outer_open, True), trim=WALK_W * 0.5)
    for i in HOUSES:
        ang = (i + 0.5) * seg
        dist = r + WALK_W * 0.5 + HOUSE[0] * 0.5
        hx, hz = cx + dist * math.cos(ang), cz - dist * math.sin(ang)
        yaw = math.degrees(ang)
        blocks.append(box(f"HousePlatform{i}", hx, -0.25, hz, HOUSE[0], WALK_T, HOUSE[2], yaw, color=COL_PLATFORM))
        blocks.append(box(f"House{i}", hx + 1.0 * math.cos(ang), HOUSE[1] * 0.5, hz - 1.0 * math.sin(ang), 3.6, HOUSE[1],
                          3.6, yaw, color=COL_REED))
    shore = (cx + r + WALK_W * 0.5 + 4.0, cz)
    ang4 = 4.5 * seg  # the child's house platform (ring segment 4); facing the ring
    child = (cx + (r + WALK_W * 0.5 + 1.2) * math.cos(ang4), cz - (r + WALK_W * 0.5 + 1.2) * math.sin(ang4),
             math.degrees(ang4) + 90.0)
    blocks.append(box("Shore", shore[0], -0.25, shore[1], 8.0, WALK_T, 12.0, color=COL_PLATFORM))
    blocks.append(box("ShoreBoundE", shore[0] + 4.5, 1.0, shore[1], 1.0, 2.0, 12.0, color=COL_RAIL))
    blocks.append(box("ClutchStone", shore[0] + 1.5, 0.4, shore[1], 1.2, 0.8, 1.2, color=COL_BANK))
    return {
        "doc": "M4-C10-02 greybox (tools/act2/ch10_greybox.py; do not edit by hand): Reedhollow, the Kirru village, "
        "at the overcast dusk (colour script ch10). A reed causeway from Ossa Fen (west, Gate) to a ring of platforms "
        "round the lagoon, reed houses off the ring, and the shore on its east side (Shore, ClutchStone) where the "
        "clutch stands for the farewell-tide and the motes lift. Pell is not let in (act_outline Ch10). The story waits "
        "on the beat sheet (M4-C10-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_PLATFORM,
        "blocks": blocks,
        "spawns": {"Gate": [2.0, 0.0, 0.0, 270.0], "Shore": [r3(shore[0] - 2.0), 0.0, r3(shore[1]), 270.0]},
        "marks": {"clutch": [r3(shore[0] + 0.5), 0.0, r3(shore[1]), 90.0], "pell_gate": [0.5, 0.0, 0.0, 90.0]},
        # M4-A2P-010: the Kirru stand hidden until their bodies exist (characters: one Kirru base on Pell's rig; ADR
        # 0041's bar, no capsules): the clutch on the shore for the farewell-tide, the child on a house platform
        "actors": dict({f"clutch_{k}": {"at": [r3(shore[0] + 1.5 - 0.9 * (k % 2)), 0.0, r3(shore[1] - 4.5 + 1.3 * k),
                                              90.0], "color": "#8a7a5a", "radius": 0.34, "height": 1.7, "hidden": True}
                        for k in range(8)},
                       kirru_child={"at": [r3(child[0]), 0.0, r3(child[1]), r3(child[2])], "color": "#8a7a5a",
                                    "radius": 0.24, "height": 1.1, "hidden": True},
                       pell={"at": [0.5, 0.0, 0.0, 90.0], "color": "#7a8a6a", "radius": 0.34, "height": 1.9,
                             "hidden": True}),
        "shots": {"R01": {"pos": [38.48, 3.78, 5.46], "look_at": [r3(shore[0]), 1.5, 0.0], "fov": 45},
                  # M4-A2P-010 (positions from tools/act1/shot_check's solver): C2 through the gate, Pell small beyond it; C5 Asha level with the child; C3 the
                  # farewell-tide: the lagoon wide, the clutch from behind, the tilt up with the motes
                  "R02": {"pos": [8.0, 1.6, 1.5], "look_at": [1.0, 1.3, 0.0], "fov": 40},
                  "R03": {"pos": [34.97, 1.16, -9.69], "look_at": [r3(child[0]), 0.9, r3(child[1])], "fov": 40},
                  "R04": {"pos": [r3(shore[0] + 3.0), 4.0, -8.0], "look_at": [cx, 0.5, 0.0], "fov": 50},
                  "R05": {"pos": [64.8, 1.66, -2.84], "look_at": [cx, 1.0, 0.0], "fov": 45},
                  "R06": {"pos": [58.67, 1.29, -1.54], "look_at": [r3(shore[0] + 0.5), 6.0, 0.0], "fov": 60}},
        "camera_volumes": [
            {"id": "Causeway", "mode": "pan_follow", "at": [r3((cx - r) / 2), 1.5, 0.0],
             "size": [r3(cx - r + 2.0), 4.0, WALK_W + 2.0], "pos": [-1.98, 5.0, 0.5], "look_at": [r3((cx - r) / 2), 0.8, 0.0],
             "fov": 50, "priority": 1},
            {"id": "Ring", "mode": "pan_follow", "at": [cx, 1.5, cz], "size": [r3(2 * r + 12.0), 4.0, r3(2 * r + 12.0)],
             "pos": [cx, 7.0, cz], "look_at": [r3(cx + r), 0.5, cz], "fov": 55, "priority": 1},
            {"id": "Shore", "mode": "pan_follow", "at": [r3(shore[0]), 1.5, r3(shore[1])], "size": [8.0, 4.0, 12.0],
             "pos": [56.17, 3.94, -4.9], "look_at": [r3(shore[0] + 0.5), 0.8, 0.0], "fov": 50, "priority": 2}],
        "triggers": [{"id": "to_fen", "activation": "touch", "at": [-1.0, 0.0, 0.0], "size": [1.5, 0, WALK_W],
                      "payload": {"beat": "to_fen"}, "yaw": 0.0},
                     # M4-A2P-1003 D2: a Kirru on the causeway names Ressa, overheard as the party walks in (the
                     # sheet's first naming, before the shore)
                     {"id": "kirru_ressa", "activation": "touch", "at": [24.0, 0.0, 0.0], "size": [1.5, 0, 3.6],
                      "once": True, "requires_flag": "ch10_reached_reedhollow", "blocked_by_flag": "ch10_heard_ressa",
                      "payload": {"dialogue": "ch10_bark_kirru_ressa", "overheard": True}, "yaw": 0.0},
                     # M4-A2P-114: the shore, where the farewell-tide is watched (B09), then the dawn gate (B11)
                     {"id": "shore", "activation": "touch", "at": [61.8, 0.0, 0.0], "size": [2.0, 0, 3.0],
                      "requires_flag": "ch10_reached_reedhollow", "blocked_by_flag": "ch10_complete",
                      "payload": {"beat": "shore"}, "yaw": 0.0}],
    }


def main() -> None:
    for name, layout in (("ossa_fen", ossa_fen()), ("reedhollow", reedhollow())):
        out = ZONES / name / f"{name}_layout.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
