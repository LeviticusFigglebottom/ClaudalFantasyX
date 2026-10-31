#!/usr/bin/env python3
"""Ch12 "The Cold Road" greybox (M4-C12-02): the geography of ch12/keth_pass, ch12/quellan and ch12/cloudloom, before
the beat sheet (M4-C12-01) adds the story. From act_outline.md (Ch12) and the colour script's `ch12` (a 09:00 morning,
thin air, hard sun between cloud banks; woven reds the only warm notes; white stone under open sky in Cloudloom, no
ice in the temple, ADR 0015).

  ch12/keth_pass  the mountain route: from the pass foot (south) up switchback flights (ramps: no step-up) along a
                  cliff, the pass-cords strung post to post on the drop side, a cord post with knots on the first
                  landing (`knot_post`: the Ullari woman's side scene), the terrace shelf under a Lit Age terrace wall
                  that seeps drowned glimmer (RamArena: the Avalanche Ram), and the saddle at the top (`cold_ledge`:
                  where Toma sees Kerrid's breath not fog, against the dark of the cliff), on to Quellan.
  ch12/quellan    the highland town on its terrace: the road in from the pass (west), a street of houses, the inn
                  (`inn_door`: Ysolde's confession to Asha that night), the well in the square, and the road up north
                  to Cloudloom.
  ch12/cloudloom  the summit temple: the stair up from the south (a ramp), the open-roofed weaving-hall on white
                  stone, rows of keth hanging from the beams (thousands; Ama's among them), and Hesk's place at its
                  north end (`hesk`), where the noon light writes the keth's shadows on the floor.

x is east, north is -Z. Shares Ch10's builders (tools/act2/ch10_greybox.py) and Ch11's rooms.

    python3 tools/act2/ch12_greybox.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import WALK_T, box, r3  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ZONES = ROOT / "game" / "levels" / "ch12"
COL_ROCK = "#6a6e74"
COL_PATH = "#8a8478"
COL_SNOW = "#e8eef4"
COL_CORD = "#b0302a"  # woven red: the only warm note
COL_POST = "#4a4038"
COL_HOUSE = "#7a6a58"
COL_ROOF = "#5a4a40"
COL_WHITE = "#e6e2da"
COL_TERRACE = "#7a7060"
GLOW_DROWNED = "#e8d8a0"  # drowned glimmer seeping from the Lit Age wall
SUN = {"pitch_deg": -30.0, "yaw_deg": 40.0, "energy": 2.0, "color": "#faf6ff"}  # 09:00, the sun in the south-east
ENV = {"background": "#c8d8e8", "ambient_color": "#7fa6dc", "ambient_energy": 0.8}
FLIGHT_W = 4.0
CLIFF_H = 10.0
PARAPET_H = 1.1
CORD_STEP_M = 8.0
CORD_Y = 1.2


def flight(fid: str, a: tuple[float, float, float], b: tuple[float, float, float], cliff_side: float,
           cords: bool = True) -> tuple[list[dict], list[dict]]:
    """A ramp from a to b (x, y, z) with the cliff on one side (+1: left of a -> b, -1: right) and a parapet on the
    drop side, the pass-cords on posts along the parapet. Returns (blocks, ramps)."""
    dx, dz = b[0] - a[0], b[2] - a[2]
    length = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(-dz, dx))
    nx, nz = -dz / length, dx / length
    mx, mz, my = (a[0] + b[0]) * 0.5, (a[2] + b[2]) * 0.5, (a[1] + b[1]) * 0.5
    ramps = [{"id": fid, "from": [r3(v) for v in a], "to": [r3(v) for v in b], "width": FLIGHT_W, "color": COL_PATH}]
    blocks = []
    rise = abs(b[1] - a[1])
    for side in (1.0, -1.0):
        off = side * (FLIGHT_W * 0.5 + 0.25)
        cliff = side == cliff_side
        h = CLIFF_H if cliff else PARAPET_H
        lo = min(a[1], b[1]) - 0.5
        blocks.append(box(f"{fid}{'Cliff' if cliff else 'Parapet'}", mx + nx * off, lo + (rise + h + 0.5) * 0.5,
                          mz + nz * off, length, rise + h + 0.5, 0.5, yaw, color=COL_ROCK if cliff else COL_POST))
        if cliff or not cords:
            continue
        n = int(length // CORD_STEP_M)
        for k in range(n + 1):
            t = k / max(n, 1)
            px, pz = a[0] + dx * t + nx * (off + side * 0.4), a[2] + dz * t + nz * (off + side * 0.4)
            py = a[1] + (b[1] - a[1]) * t
            blocks.append(box(f"{fid}CordPost{k}", px, py + 0.9, pz, 0.15, 1.8, 0.15, color=COL_POST, solid=False))
        cy = my + CORD_Y + 0.4
        blocks.append(box(f"{fid}Cord", mx + nx * (off + side * 0.4), cy, mz + nz * (off + side * 0.4), length, 0.04,
                          0.04, yaw, color=COL_CORD, solid=False))
    return blocks, ramps


def landing(lid: str, cx: float, y: float, cz: float, hx: float, hz: float, gaps: dict) -> list[dict]:
    return [floor(lid, cx, cz, hx, hz, y, COL_PATH)] + walls(lid, cx, cz, hx, hz, y, PARAPET_H, gaps)


# --- Keth Pass --------------------------------------------------------------------------------------------------------

def climb_volumes(prefix: str, runs: list[tuple[tuple[float, float, float], tuple[float, float, float]]],
                  back_m: float = 5.0, up_m: float = 4.5, side_m: float = 0.0) -> list[dict]:
    """M4-A2P-012: a pan-follow volume per flight (the hub orbit sees the cliff on the inside turn): the camera stands
    back_m behind the flight's foot, up_m over it, and looks up the flight to its middle. side_m moves it to the left of
    the climb, away from a cliff on its right (the PC's row 86: on Keth Pass the cliff filled half the frame)."""
    out = []
    for i, (a, b) in enumerate(runs):
        dx, dz = b[0] - a[0], b[2] - a[2]
        n = math.hypot(dx, dz)
        ux, uz = dx / n, dz / n
        out.append({"id": f"{prefix}{i}", "mode": "pan_follow",
                    "at": [r3((a[0] + b[0]) / 2), r3((a[1] + b[1]) / 2 + 1.5), r3((a[2] + b[2]) / 2)],
                    "size": [r3(abs(dx) + FLIGHT_W + 1.0), r3(abs(b[1] - a[1]) + 4.0), r3(abs(dz) + FLIGHT_W + 1.0)],
                    "pos": [r3(a[0] - ux * back_m + uz * side_m), r3(a[1] + up_m), r3(a[2] - uz * back_m - ux * side_m)],
                    "look_at": [r3((a[0] + b[0]) / 2), r3((a[1] + b[1]) / 2 + 0.8), r3((a[2] + b[2]) / 2)], "fov": 50,
                    "priority": 1})
    return out


# M4-A2P-1003 E5: the climb's barks (B02), overheard once each on the flights: (dialogue, at on the ramp, size)
PASS_BARKS = (("ch12_bark_traveller", (0.0, 1.29, -12.0), (4.0, 0, 3.0)),
              ("ch12_bark_asha_even_here", (0.0, 3.0, -20.0), (4.0, 0, 3.0)),
              ("ch12_bark_toma_cairn", (12.0, 7.29, -40.0), (3.0, 0, 4.0)),
              ("ch12_bark_ysolde_knot", (26.0, 10.29, -40.0), (3.0, 0, 4.0)),
              ("ch12_bark_liss_launcher", (62.0, 13.29, -40.0), (3.0, 0, 4.0)),
              ("ch12_bark_liss_counting", (76.0, 16.29, -40.0), (3.0, 0, 4.0)))


def overheard(dialogue: str, at: tuple[float, float, float], size: tuple[float, float, float],
              requires: str = "ch12_started", blocked_by: str = "") -> dict:
    """A bark heard once in passing (a touch box; the dialogue plays overheard, the walk goes on)."""
    row = {"id": dialogue.removeprefix("ch12_"), "activation": "touch", "at": list(at), "size": list(size),
           "once": True, "requires_flag": requires, "payload": {"dialogue": dialogue, "overheard": True}, "yaw": 0.0}
    if blocked_by:
        row["blocked_by_flag"] = blocked_by
    return row


def listen(tid: str, dialogue: str, at: tuple[float, float, float], requires: str, blocked_by: str = "",
           prompt: str = "FIELD_PROMPT_LISTEN") -> dict:
    """Someone to talk to: an interact box with a prompt."""
    row = {"id": tid, "activation": "interact", "at": list(at), "size": [1.6, 0, 1.6], "prompt_key": prompt,
           "requires_flag": requires, "payload": {"dialogue": dialogue}, "yaw": 0.0}
    if blocked_by:
        row["blocked_by_flag"] = blocked_by
    return row


def keth_pass() -> dict:
    blocks, ramps = [], []
    blocks += landing("Foot", 0.0, 0.0, 0.0, 6.0, 6.0, {"n": (-2.2, 2.2)})
    for fid, a, b, cliff in (("Flight1", (0.0, 0.0, -6.0), (0.0, 6.0, -34.0), 1.0),
                             ("Flight2", (6.0, 6.0, -40.0), (34.0, 12.0, -40.0), 1.0),
                             ("Flight3", (56.0, 12.0, -40.0), (84.0, 18.0, -40.0), 1.0)):
        fb, fr = flight(fid, a, b, cliff)
        blocks += fb
        ramps += fr
    blocks += landing("Landing1", 0.0, 6.0, -40.0, 6.0, 6.0, {"s": (-2.2, 2.2), "e": (-2.2, 2.2)})
    blocks.append(box("KnotPost", -3.0, 7.0, -44.5, 0.3, 2.0, 0.3, color=COL_POST))
    blocks.append(box("Knots", -3.0, 7.6, -44.2, 0.5, 0.6, 0.12, color=COL_CORD, solid=False))
    blocks += landing("RamArena", 45.0, 12.0, -40.0, 11.0, 10.0, {"w": (-2.2, 2.2), "e": (-2.2, 2.2)})
    blocks.append(box("TerraceWall", 45.0, 15.0, -50.5, 22.0, 6.0, 1.0, color=COL_TERRACE, emission=GLOW_DROWNED,
                      emission_energy=0.5))
    blocks += landing("Saddle", 95.0, 18.0, -40.0, 11.0, 10.0, {"w": (-2.2, 2.2), "e": (-2.2, 2.2)})
    blocks.append(box("SaddleCliff", 95.0, 23.0, -51.0, 24.0, 10.0, 1.0, color=COL_ROCK))
    blocks.append(box("Snowfield", 40.0, -2.0, -40.0, 160.0, 1.0, 120.0, color=COL_SNOW, solid=False))
    blocks.append(box("ExitStep", 108.0, 18.0 - WALK_T * 0.5, -40.0, 4.0, WALK_T, 4.4, color=COL_PATH))
    blocks.append(box("ExitBound", 110.25, 19.0, -40.0, 0.5, 2.0, 4.4, color=COL_POST))
    return {
        "doc": "M4-C12-02 greybox (tools/act2/ch12_greybox.py; do not edit by hand): Keth Pass on a 09:00 morning "
        "(colour script ch12). From the pass foot (PassFoot) up switchback flights (ramps) along the cliff, the "
        "pass-cords on the drop side, the first landing's knotted cord post (knot_post), the terrace shelf under the "
        "Lit Age wall seeping drowned glimmer (RamArena: the Avalanche Ram), and the saddle (cold_ledge: Kerrid's "
        "breath against the cliff), on to Quellan (to_quellan). The story waits on the beat sheet (M4-C12-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_PATH,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": {"PassFoot": [-1.0, 0.0, 1.0, 0.0], "RamArena": [40.0, 12.0, -40.0, 270.0],
                   "FromQuellan": [102.0, 18.0, -40.0, 90.0]},
        "marks": {"knot_post": [-1.6, 6.0, -43.6, 90.0], "cold_ledge": [95.0, 18.0, -47.0, 0.0]},
        "actors": {},
        "shots": {"K01": {"pos": [91.0, 19.7, -36.0], "look_at": [95.0, 19.6, -47.0], "fov": 35},
                  # M4-A2P-012 (docs/kb/plan/act2/chapters/ch12.md): K01 is C1's breath at the cold ledge; the cords
                  # on the first flight, the Ram's shelf under the seeping wall, the knotted post (C5)
                  "K02": {"pos": [2.5, 4.5, -8.0], "look_at": [0.0, 3.0, -22.0], "fov": 50},
                  "K04": {"pos": [44.0, 15.5, -33.0], "look_at": [48.0, 13.5, -46.0], "fov": 50},  # M4-A2P-0421: re-aimed on the dressing
                  "K05": {"pos": [-0.5, 7.6, -42.0], "look_at": [-3.0, 7.4, -44.5], "fov": 35}},
        "camera_volumes": climb_volumes("Flight", [((0.0, 0.0, -6.0), (0.0, 6.0, -34.0)),
                                                    ((6.0, 6.0, -40.0), (34.0, 12.0, -40.0)),
                                                    ((56.0, 12.0, -40.0), (84.0, 18.0, -40.0))],
                                        up_m=6.0, side_m=2.5)
        + [{"id": "RamShelf", "mode": "pan_follow", "at": [45.0, 13.5, -40.0], "size": [22.0, 4.0, 20.0],
            "pos": [37.0, 18.0, -30.0], "look_at": [46.0, 12.8, -42.0], "fov": 55, "priority": 2},
           {"id": "Saddle", "mode": "pan_follow", "at": [95.0, 19.5, -40.0], "size": [22.0, 4.0, 20.0],
            "pos": [86.0, 23.0, -30.0], "look_at": [96.0, 18.8, -42.0], "fov": 55, "priority": 2},
           # the pass's foot: PassFoot and the "Encounter" return spawn (the origin) sit below Flight0's box
           {"id": "Foot", "mode": "pan_follow", "at": [0.0, 1.5, 1.0], "size": [10.0, 4.0, 10.0],
            "pos": [0.0, 4.5, 9.0], "look_at": [0.0, 2.0, -6.0], "fov": 50, "priority": 1}],
        "triggers": [{"id": "to_quellan", "activation": "touch", "at": [108.5, 18.0, -40.0], "size": [1.5, 0, 4.0],
                      "payload": {"beat": "to_quellan"}, "yaw": 0.0},
                     # M4-A2P-114: the seeping wall's terrace, where the Avalanche Ram comes down (B06)
                     {"id": "terrace", "activation": "touch", "at": [40.0, 12.0, -40.0], "size": [2.0, 0, 4.0],
                      "requires_flag": "ch12_started", "blocked_by_flag": "ch12_ram_felled",
                      "payload": {"beat": "terrace"}, "yaw": 0.0},
                     # M4-A2P-1003 E4: the saddle, across its whole width, plays Kerrid's breath (B03, never cut)
                     {"id": "cold_ledge", "activation": "touch", "at": [90.0, 18.0, -40.0], "size": [2.0, 0, 18.0],
                      "once": True, "requires_flag": "ch12_ram_felled", "blocked_by_flag": "ch12_toma_saw_breath",
                      "payload": {"beat": "cold_ledge"}, "yaw": 0.0},
                     # E12: the Ullari woman's knot at the first landing's cord post (B04, optional)
                     {"id": "knot_post", "activation": "interact", "at": [-1.6, 6.0, -43.0], "size": [2.0, 0, 2.0],
                      "prompt_key": "FIELD_PROMPT_LOOK", "requires_flag": "ch12_started",
                      "blocked_by_flag": "ch12_heard_the_knot", "payload": {"dialogue": "ch12_the_knot"}, "yaw": 0.0}]
        + [overheard(bid, at, size) for bid, at, size in PASS_BARKS],
        # M4-C12-03: the pass's random fights (act2_roster.md Ch12); none in Quellan or the Cloudloom
        "encounters": {"table": [{"encounter": "ch12_pass_lynxes", "weight": 2}, {"encounter": "ch12_pass_moths", "weight": 1},
                                 {"encounter": "ch12_pass_scree", "weight": 1}],
                       "min_m": 95, "max_m": 145, "when": {"set": ["ch12_started"]}, "seed": 12},
    }


# --- Quellan ----------------------------------------------------------------------------------------------------------

STREET = (0.0, 60.0, 0.0, 4.0)  # x0, x1, z, half width; the town's floor is y 0


def quellan() -> dict:
    x0, x1, sz, hw = STREET
    blocks = [floor("Terrace", (x0 + x1) * 0.5, sz, (x1 - x0) * 0.5 + 6.0, 22.0, 0.0, COL_PATH),
              box("TerraceEdgeS", (x0 + x1) * 0.5, PARAPET_H * 0.5, sz + 22.25, x1 - x0 + 12.0, PARAPET_H, 0.5,
                  color=COL_POST),
              box("TerraceEdgeW", x0 - 6.25, 1.0, sz, 0.5, 2.0, 44.0, color=COL_POST),
              box("TerraceEdgeNW", (x0 - 6.0 + 56.0 - FLIGHT_W * 0.5) * 0.5, 1.0, sz - 22.25,
                  56.0 - FLIGHT_W * 0.5 - (x0 - 6.0), 2.0, 0.5, color=COL_POST),
              box("TerraceEdgeNE", (56.0 + FLIGHT_W * 0.5 + x1 + 6.0) * 0.5, 1.0, sz - 22.25,
                  x1 + 6.0 - 56.0 - FLIGHT_W * 0.5, 2.0, 0.5, color=COL_POST),
              box("TerraceEdgeE", x1 + 6.25, 1.0, sz, 0.5, 2.0, 44.0, color=COL_POST)]
    for k, x in enumerate((8.0, 20.0, 44.0)):  # houses either side of the street
        for side in (-1.0, 1.0):
            blocks.append(box(f"House{k}{'NS'[side > 0]}", x, 2.0, sz + side * (hw + 4.0), 8.0, 4.0, 6.0,
                              color=COL_HOUSE))
            blocks.append(box(f"Roof{k}{'NS'[side > 0]}", x, 4.6, sz + side * (hw + 4.0), 8.6, 1.2, 6.6, color=COL_ROOF))
    blocks.append(box("Inn", 32.0, 2.5, sz - hw - 5.0, 10.0, 5.0, 8.0, color=COL_HOUSE))
    blocks.append(box("InnRoof", 32.0, 5.6, sz - hw - 5.0, 10.6, 1.2, 8.6, color=COL_ROOF))
    blocks.append(box("InnBanner", 32.0, 3.2, sz - hw - 0.9, 1.2, 1.8, 0.05, color=COL_CORD, solid=False))
    blocks.append(box("Well", 54.0, 0.5, sz + 10.0, 1.6, 1.0, 1.6, color=COL_ROCK))
    north_y = 8.0
    ramps = [{"id": "RoadUp", "from": [56.0, 0.0, -hw], "to": [56.0, north_y, -36.0], "width": FLIGHT_W,
              "color": COL_PATH}]
    for side in (-1.0, 1.0):
        blocks.append(box(f"RoadUpWall{'WE'[side > 0]}", 56.0 + side * (FLIGHT_W * 0.5 + 0.25), north_y * 0.5 + 0.5,
                          -20.0, 0.5, north_y + 2.0, 32.0, color=COL_ROCK))
    blocks.append(floor("RoadTop", 56.0, -40.0, 3.0, 4.0, north_y, COL_PATH))
    blocks.append(box("RoadTopBound", 56.0, north_y + 1.0, -44.25, 6.0, 2.0, 0.5, color=COL_POST))
    blocks.append(box("Snowfield", 30.0, -2.0, 0.0, 160.0, 1.0, 120.0, color=COL_SNOW, solid=False))
    return {
        "doc": "M4-C12-02 greybox (tools/act2/ch12_greybox.py; do not edit by hand): Quellan, the highland town "
        "(colour script ch12). The road in from Keth Pass (west, FromPass), a street of houses, the inn with its "
        "red banner (inn_door: Ysolde's confession to Asha that night), the well in the square, and the road up north "
        "to Cloudloom (a ramp; to_cloudloom). Back to the pass at to_pass. The story waits on the beat sheet "
        "(M4-C12-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_PATH,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": {"FromPass": [2.0, 0.0, 0.0, 270.0], "FromCloudloom": [56.0, north_y, -38.0, 180.0],
                   "Shrine": [56.0, 0.0, 7.5, 180.0]},
        "marks": {"inn_door": [32.0, 0.0, r3(sz - hw + 0.4), 0.0], "well": [52.4, 0.0, r3(sz + 10.0), 270.0]},
        "actors": {},
        "shots": {"Q01": {"pos": [-2.0, 3.0, 2.0], "look_at": [40.0, 2.0, -2.0], "fov": 50},
                  # M4-A2P-012: C4 at night, Ysolde and Asha at the well
                  "Q02": {"pos": [50.0, 1.7, 6.0], "look_at": [53.5, 1.2, 10.0], "fov": 40}},  # M4-A2P-0421: out of House2S
        "camera_volumes": [
            {"id": "StreetWest", "mode": "pan_follow", "at": [15.0, 1.5, 0.0], "size": [30.0, 4.0, 8.0],
             "pos": [-5.0, 5.0, 6.0], "look_at": [15.0, 0.5, 0.0], "fov": 50, "priority": 1},
            {"id": "StreetEast", "mode": "pan_follow", "at": [45.0, 1.5, 0.0], "size": [30.0, 4.0, 8.0],
             "pos": [25.0, 5.0, 6.0], "look_at": [45.0, 0.5, 0.0], "fov": 50, "priority": 1}],
        "triggers": [{"id": "to_pass", "activation": "touch", "at": [-4.5, 0.0, 0.0], "size": [1.5, 0, 6.0],
                      "payload": {"beat": "to_pass"}, "yaw": 0.0},
                     # M5-A3P-1004: back aboard the Kite, moored over the road in (Ch18)
                     {"id": "a3_to_kite", "activation": "interact", "at": [4.0, 0.0, -2.5], "size": [1.4, 0, 1.4],
                      "prompt_key": "FIELD_PROMPT_CH18_BACK_TO_KITE", "requires_flag": "ch18_world_open",
                      "payload": {"beat": "to_kite"}, "yaw": 0.0},
                     {"id": "to_cloudloom", "activation": "touch", "at": [56.0, north_y, -42.5], "size": [4.0, 0, 1.5],
                      "payload": {"beat": "to_cloudloom"}, "yaw": 0.0},
                     # M4-A2P-1003 E5: Quellan's people (B08), the side errands and the inn's camp
                     overheard("ch12_bark_toma_kinder", (6.0, 0.0, 0.0), (2.0, 0, 8.0), "ch12_reached_quellan"),
                     overheard("ch12_bark_quellan_boy", (38.0, 0.0, 0.0), (2.0, 0, 8.0), "ch12_reached_quellan"),
                     overheard("ch12_bark_quellan_night", (26.0, 0.0, 0.0), (2.0, 0, 8.0), "ch12_hesk_bound",
                               "ch12_complete"),
                     listen("npc_herder", "ch12_bark_herder", (14.0, 0.0, 3.0), "ch12_reached_quellan"),
                     listen("npc_weaver", "ch12_bark_weaver", (24.0, 0.0, 3.0), "ch12_reached_quellan"),
                     listen("npc_innkeeper", "ch12_bark_innkeeper", (36.0, 0.0, -3.0), "ch12_reached_quellan"),
                     listen("npc_reader", "ch12_bark_reader", (51.0, 0.0, 8.0), "ch12_reached_quellan"),
                     listen("side_dorros_cord", "ch12_side_dorros_cord", (10.0, 0.0, -3.0), "ch12_ram_felled",
                            "ch12_returned_herd_cord"),
                     listen("side_the_boys_knot", "ch12_side_the_boys_knot", (42.0, 0.0, 3.0), "ch12_reached_quellan"),
                     # M4-A2P-1003 E5: the Order's Level-stone by the well, a save shrine (ShrineServices)
                     {"id": "shrine", "activation": "interact", "at": [56.0, 0.0, 10.0], "size": [1.6, 0, 1.6],
                      "prompt_key": "FIELD_PROMPT_REST", "requires_flag": "ch12_reached_quellan",
                      "payload": {"beat": "shrine", "save_shrine": "quellan_shrine"}, "yaw": 0.0},
                     # the trader on the street (shops.json quellan_trader)
                     {"id": "shop", "activation": "interact", "at": [30.0, 0.0, 3.2], "size": [1.6, 0, 1.6], "prompt_key": "SHOP_PROMPT",
                      "requires_flag": "ch12_reached_quellan", "payload": {"shop": "quellan_trader"}, "yaw": 0.0},
                     listen("camp", "ch12_camp_the_end_of_the_road", (29.0, 0.0, -3.0), "ch12_ysolde_confessed",
                            "ch12_camp_talk", "FIELD_PROMPT_REST")],
    }


# --- Cloudloom --------------------------------------------------------------------------------------------------------

HALL = (0.0, -40.0, 14.0, 20.0)  # centre x, z and half sizes; floor y 6 (the stair climbs to it)
HALL_Y = 6.0
KETH_ROWS = 6
KETH_PER_ROW = 9


def cloudloom() -> dict:
    hx0, hz0, hx, hz = HALL
    blocks = landing("Approach", 0.0, 0.0, 0.0, 5.0, 5.0, {"n": (-2.2, 2.2)})
    fb, ramps = flight("Stair", (0.0, 0.0, -5.0), (0.0, HALL_Y, hz0 + hz), 1.0, cords=False)  # to the hall's south edge
    blocks += fb
    blocks.append(floor("Hall", hx0, hz0, hx, hz, HALL_Y, COL_WHITE))
    blocks += walls("Hall", hx0, hz0, hx, hz, HALL_Y, 3.0, {"s": (-2.2, 2.2)})
    for k in range(4):  # the open roof's beams the keth hang from (the roof itself is open sky)
        bz = hz0 - hz + (k + 1) * 2 * hz / 5
        blocks.append(box(f"Beam{k}", hx0, HALL_Y + 6.0, bz, 2 * hx, 0.4, 0.4, color=COL_ROOF, solid=False))
    for row in range(KETH_ROWS):
        z = hz0 - hz + 4.0 + row * (2 * hz - 12.0) / (KETH_ROWS - 1)
        for i in range(KETH_PER_ROW):
            if abs(i - KETH_PER_ROW // 2) <= 1:
                continue  # the aisle up the middle
            x = hx0 - hx + 2.0 + i * (2 * hx - 4.0) / (KETH_PER_ROW - 1)
            blocks.append(box(f"Keth{row}_{i}", x, HALL_Y + 3.6, z, 0.25, 3.6, 0.05, color=COL_CORD, solid=False))
    blocks.append(box("HeskDais", hx0, HALL_Y + 0.2, hz0 - hz + 3.0, 6.0, 0.4, 3.0, color=COL_WHITE))
    return {
        "doc": "M4-C12-02 greybox (tools/act2/ch12_greybox.py; do not edit by hand): Cloudloom, the summit temple "
        "(colour script ch12: white stone under open sky, no ice anywhere in it, ADR 0015). The stair up from the "
        "south (Approach; a ramp), the open-roofed weaving-hall on white stone, rows of keth hanging from its beams with "
        "an aisle up the middle, and Hesk's place on the dais at its north end (hesk). Back down to Quellan at "
        "to_quellan. The story waits on the beat sheet (M4-C12-01).",
        "sun": {"pitch_deg": -75.0, "yaw_deg": 10.0, "energy": 2.2, "color": "#faf6ff"},  # noon: the keth's shadows
        "environment": ENV,
        "block_color": COL_WHITE,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": {"Approach": [0.0, 0.0, 2.0, 0.0], "Hall": [0.0, HALL_Y, -24.0, 0.0]},
        "marks": {"hesk": [r3(hx0), HALL_Y, r3(hz0 - hz + 6.0), 180.0]},  # before the dais (no step-up onto it)
        "actors": {},
        "shots": {"C01": {"pos": [0.0, HALL_Y + 2.0, -23.0], "look_at": [0.0, HALL_Y + 2.0, -57.0], "fov": 50},
                  # M4-A2P-012: C3 the weaving-hall from high in the open roof; Ysolde reading Ama's keth
                  "C02": {"pos": [8.0, HALL_Y + 12.0, -26.0], "look_at": [0.0, HALL_Y + 2.0, -48.0], "fov": 60},
                  "C03": {"pos": [2.5, HALL_Y + 1.6, -50.0], "look_at": [0.0, HALL_Y + 1.5, -54.0], "fov": 35}},
        "camera_volumes": climb_volumes("Stair", [((0.0, 0.0, -5.0), (0.0, HALL_Y, hz0 + hz))])
        + [{"id": "Hall", "mode": "pan_follow", "at": [hx0, HALL_Y + 1.5, hz0], "size": [2 * hx, 4.0, 2 * hz],
            # up the aisle from just inside the south wall, under the beams, to the dais (the POI stills, 10-30: at z -15 it
            # stood outside the hall, inside the stair's cliff)
            "pos": [hx0, HALL_Y + 4.5, hz0 + hz - 2.5], "look_at": [hx0, HALL_Y + 0.8, hz0 - hz + 6.0], "fov": 55,
            "priority": 1},
           {"id": "Foot", "mode": "pan_follow", "at": [0.0, 1.5, 1.0], "size": [8.0, 4.0, 8.0],
            "pos": [0.0, 4.0, 8.0], "look_at": [0.0, 3.0, -8.0], "fov": 50, "priority": 1}],
        "triggers": [{"id": "to_quellan", "activation": "touch", "at": [0.0, 0.0, 4.25], "size": [4.0, 0, 1.5],
                      "payload": {"beat": "to_quellan"}, "yaw": 0.0},
                     # M4-A2P-114: up the aisle before the dais, where Hesk is bound (B10-B11)
                     {"id": "dais", "activation": "touch", "at": [hx0, HALL_Y, -50.0], "size": [4.0, 0, 1.5],
                      "requires_flag": "ch12_reached_cloudloom", "blocked_by_flag": "ch12_hesk_bound",
                      "payload": {"beat": "dais"}, "yaw": 0.0},
                     # M4-A2P-1003 E5: the Order's keeper, by the hall's door
                     listen("npc_keeper", "ch12_bark_cloudloom_keeper", (5.0, HALL_Y, -26.0), "ch12_reached_cloudloom")],
    }


def main() -> None:
    for name, layout in (("keth_pass", keth_pass()), ("quellan", quellan()), ("cloudloom", cloudloom())):
        out = ZONES / name / f"{name}_layout.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
