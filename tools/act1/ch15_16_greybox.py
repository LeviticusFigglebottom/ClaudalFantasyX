#!/usr/bin/env python3
"""Ch15 "Unlamped" and Ch16 "The Edge of the World" greybox (M4-C15-02, M4-C16-02): ch15/open_sea, ch17/hollowmere
(its first visit), ch16/pale_rim and ch16/drowned_choir, before the beat sheets (M4-C15-01, M4-C16-01). From
act_outline.md (Ch15, Ch16; ADR 0016, 0020, 0022) and the colour script's `ch15` and `ch16`.

  ch15/open_sea      the bridal barge adrift at night with no lamp: its deck the whole walkable world, Tobin's bier
                     under Merel's bridal cloth (`tobin_bier`), the stern where Kerrid sits and holds his hands still
                     (`kerrid_sits`), the shoal of an old Rising's held dead under the water (Shoal: the motes come up
                     off it toward him), the bow (`bow`: at dawn Liss sings into the fog; to_hollowmere).
  ch17/hollowmere    the Saltwright town of lashed hulls at dawn in the fog (Act III's zone, its first visit): the dock
                     the barge comes in to (Dock), hull-houses on their platforms, Liss's father's (`fathers_door`),
                     the pyre-raft at the dock's end (`pyre_raft`), the supper on the dock (`supper`) and the
                     Hollowmere ship that carries them to the Rim (to_rim).
  ch16/pale_rim      the white shallows: the ship waiting at the Rim (west), then a long wade east over white sand
                     under a white sky with no shadows (the water a hand deep over a level floor), cairns, to the
                     Choir's edge (to_choir).
  ch16/drowned_choir the ring of colossal mouths at moonrise round a stone floor: Kesh's place at the ring's head
                     (`kesh`), where Sefir comes (`sefir`), Kerrid's line behind Asha (`kerrid_line`).

x is east, north is -Z. Shares Ch10's and Ch11's builders.

    python3 tools/act1/ch15_16_greybox.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import WALK_W, box, follow_volumes, r3, walk, water  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ROOT / "game" / "levels"
COL_BARGE = "#7a2a22"
COL_GOLD = "#8a7650"
COL_CLOTH = "#a83228"
COL_NIGHT_SEA = "#061a2b"
GLOW_HELD = "#2fb8c8"  # held cyan: the shoal's dead, Kerrid's rope-burns
COL_HULL = "#5a4636"
COL_PLANK = "#6a5640"
COL_FOG_SEA = "#4a5a60"
COL_SAND = "#e8e4d8"
COL_RIM_WATER = "#5e8c90"
COL_CAIRN = "#c8c4b8"
COL_CHOIR = "#6a6e70"


def write(zone: str, name: str, layout: dict) -> None:
    out = LEVELS / zone / name / f"{name}_layout.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")


# --- Ch15: the open sea -----------------------------------------------------------------------------------------------

def open_sea() -> dict:
    blocks = water(-80.0, 80.0, -80.0, 80.0, color=COL_NIGHT_SEA)
    blocks.append(box("Deck", 0.0, -0.25, 0.0, 4.0, 0.5, 10.0, color=COL_BARGE))
    for side in (-1.0, 1.0):
        blocks.append(box(f"Rail{'WE'[side > 0]}", side * 2.1, 0.3, 0.0, 0.2, 0.6, 10.0, color=COL_GOLD))
    for end in (-1.0, 1.0):
        blocks.append(box(f"Rail{'NS'[end > 0]}", 0.0, 0.3, end * 5.1, 4.4, 0.6, 0.2, color=COL_GOLD))
    blocks.append(box("Bier", 0.0, 0.3, 1.5, 1.2, 0.6, 2.4, color=COL_CLOTH))
    blocks.append(box("Shoal", 6.0, -3.0, -8.0, 30.0, 0.5, 20.0, color=COL_NIGHT_SEA, emission=GLOW_HELD,
                      emission_energy=0.3, solid=False))
    return {
        "doc": "M4-C15-02 greybox (tools/act1/ch15_16_greybox.py; do not edit by hand): the open sea at night aboard "
        "the bridal barge, unlamped (colour script ch15: the only light the sea and the dead). The deck (Deck), Tobin's "
        "bier under the bridal cloth (tobin_bier), the stern where Kerrid sits (kerrid_sits), the shoal of an old "
        "Rising's held dead under the water (Shoal), the bow (bow: to_hollowmere at dawn). The Wakefin's fight is on "
        "this deck. The story waits on the beat sheet (M4-C15-01).",
        "sun": {"pitch_deg": -20.0, "yaw_deg": 0.0, "energy": 0.25, "color": "#9fb4d6"},  # the moon
        "environment": {"background": "#0b1630", "ambient_color": "#1c2a40", "ambient_energy": 0.35},
        "block_color": COL_BARGE,
        "blocks": blocks,
        # M4-A2P-015: Reveal is Rhen's place at the stern for C3, clear of U04's line to Kerrid
        "spawns": {"Deck": [0.0, 0.0, 3.5, 0.0], "Reveal": [1.4, 0.0, 3.0, 180.0]},
        "marks": {"tobin_bier": [0.8, 0.0, 1.5, 270.0], "kerrid_sits": [0.0, 0.0, 4.2, 0.0], "bow": [0.0, 0.0, -4.2, 0.0],
                  # M4-A2P-015: the party seated about the stern for the reveal (C3); Liss at the bow (C4)
                  "reveal_asha": [-1.4, 0.0, 1.0, 180.0], "reveal_toma": [-1.4, 0.0, 2.2, 180.0],
                  "reveal_liss": [-1.4, 0.0, 3.3, 180.0], "reveal_ysolde": [1.4, 0.0, 1.8, 180.0],
                  "bow_liss": [0.0, 0.0, -4.4, 0.0]},
        "actors": {},
        "shots": {"U01": {"pos": [1.6, 1.4, -3.0], "look_at": [0.0, 0.8, 4.2], "fov": 40},
                  # M4-A2P-015 (docs/kb/plan/act2/chapters/ch15.md §4): C1 the bier under the bridal cloth; C2a low
                  # on the water by the stern as the Wakefin rises; C3 the reveal, a medium single at Kerrid's seated
                  # eye level that holds (~2.5 min), the insert on his hands, the party listening across the deck;
                  # C4 the bow in fog, Liss singing
                  "U02": {"pos": [-2.49, 1.93, -0.57], "look_at": [0.0, 0.6, 1.5], "fov": 45},
                  "U03": {"pos": [3.24, 0.19, 7.77], "look_at": [-0.5, 0.8, 4.5], "fov": 50},
                  "U04": {"pos": [0.4, 1.0, 2.2], "look_at": [0.0, 0.95, 4.2], "fov": 35},
                  "U05": {"pos": [0.6, 0.9, 3.2], "look_at": [0.0, 0.7, 4.0], "fov": 30},
                  "U06": {"pos": [0.6, 1.3, 4.8], "look_at": [0.0, 0.9, 0.5], "fov": 50},
                  "U07": {"pos": [1.42, 1.49, -1.27], "look_at": [-0.5, 1.3, -8.0], "fov": 45}},
        # M4-A2P-015: the deck from astern, high enough that the orbit sees the bier and the bow
        "camera_volumes": [{"id": "Deck", "mode": "pan_follow", "at": [0.0, 1.0, 0.0], "size": [6.0, 4.0, 12.0],
                            "pos": [3.5, 3.5, 7.0], "look_at": [0.0, 0.5, 0.0], "fov": 50, "priority": 1}],
        "triggers": [{"id": "dawn", "activation": "interact", "at": [0.0, 0.0, -4.2], "size": [2.0, 0, 1.2],
                      "prompt_key": "FIELD_PROMPT_CH15_BOW", "payload": {"beat": "to_hollowmere"}, "yaw": 0.0}],
    }


# --- Ch15/17: Hollowmere ----------------------------------------------------------------------------------------------

def hollowmere() -> dict:
    blocks = water(-40.0, 90.0, -50.0, 40.0, color=COL_FOG_SEA)
    blocks += walk("Dock", (0.0, 0.0), (60.0, 0.0), trim=WALK_W * 0.5, posts=("Pile", 0.4, 3.0, COL_HULL),
                   colors=(COL_PLANK, COL_HULL), rails=(False, False))
    blocks.append(box("DockBoundW", -2.5, 1.0, 0.0, 1.0, 2.0, WALK_W + 1.0, color=COL_HULL))
    blocks.append(box("DockBoundE", 62.3, 1.0, 0.0, 1.0, 2.0, WALK_W + 1.0, color=COL_HULL))
    # the dock's rails: open on the north at the three jetties, on the south where the ship lies alongside
    for side, z, gaps in (("N", -WALK_W * 0.5 - 0.2, [(10.0, 14.0), (26.0, 30.0), (42.0, 46.0)]),
                          ("S", WALK_W * 0.5 + 0.2, [(24.0, 36.0)])):
        x0 = -2.0
        for k, (g0, g1) in enumerate(gaps + [(61.8, 61.8)]):
            blocks.append(box(f"DockRail{side}{k}", (x0 + g0) * 0.5, 0.25, z, g0 - x0, 0.5, 0.4, color=COL_HULL))
            x0 = g1
    for k, x in enumerate((12.0, 28.0, 44.0)):
        blocks += walk(f"Jetty{k}", (x, -1.8), (x, -14.0), trim=0.0, posts=("Pile", 0.4, 3.0, COL_HULL),
                       colors=(COL_PLANK, COL_HULL), rails=(True, True))
        blocks.append(floor(f"HousePlatform{k}", x, -19.0, 5.0, 4.0, 0.0, COL_PLANK))
        blocks += walls(f"HousePlatform{k}", x, -19.0, 5.0, 4.0, 0.0, 0.5, {"s": (-2.2, 2.2)})
        blocks.append(box(f"HullHouse{k}", x, 2.2, -21.0, 7.0, 4.4, 4.0, color=COL_HULL))
    blocks.append(box("PyreRaft", 66.0, -0.15, 0.0, 3.0, 0.3, 4.0, color=COL_PLANK, solid=False))
    blocks.append(box("Ship", 30.0, 1.0, 7.0, 16.0, 3.0, 5.0, color=COL_HULL))
    return {
        "doc": "M4-C15-02 greybox (tools/act1/ch15_16_greybox.py; do not edit by hand): Hollowmere at dawn in the fog, "
        "its first visit (colour script ch15; Act III's zone). The dock the barge comes in to (Dock), jetties to "
        "hull-houses on their platforms, Liss's father's (fathers_door), the pyre-raft off the dock's end (pyre_raft), "
        "the supper on the dock (supper: the side scene) and the Hollowmere ship moored along the dock (to_rim). The "
        "story waits on the beat sheet (M4-C15-01).",
        "sun": {"pitch_deg": -6.0, "yaw_deg": 90.0, "energy": 0.6, "color": "#c8d0d8"},  # 05:40, the sun in the fog
        "environment": {"background": "#a8b0b8", "ambient_color": "#8a96a0", "ambient_energy": 0.6},
        "block_color": COL_PLANK,
        "blocks": blocks,
        "spawns": {"Dock": [2.0, 0.0, 0.0, 270.0]},
        "marks": {"fathers_door": [28.0, 0.0, -16.6, 0.0], "pyre_raft": [60.5, 0.0, 0.0, 270.0],
                  "supper": [40.0, 0.0, -0.8, 180.0],
                  # M4-A2P-015: Toma and Liss by the bier at the dock's end (C6); Liss's father across the table (C8)
                  "confess_toma": [57.0, 0.0, 0.6, 90.0], "confess_liss": [58.4, 0.0, -0.4, 270.0],
                  "supper_father": [40.0, 0.0, 1.0, 0.0]},
        "actors": {},
        "shots": {"H01": {"pos": [-1.0, 2.6, 2.0], "look_at": [40.0, 1.5, -10.0], "fov": 45},
                  # M4-A2P-015: C6 Toma and Liss by the bier, close; C7 the pyre-raft pushed off, wide; C8 the supper
                  # table side-on, Rhen and Liss's father both in frame (the table rule)
                  "H02": {"pos": [55.56, 1.56, -2.38], "look_at": [57.7, 1.4, 0.0], "fov": 40},
                  "H03": {"pos": [52.06, 2.99, -7.97], "look_at": [68.0, 0.5, 0.0], "fov": 45},
                  "H04": {"pos": [37.42, 1.44, 0.2], "look_at": [40.0, 1.1, 0.2], "fov": 45}},
        # M4-A2P-015: the dock in two runs and the jetty to Liss's father's house (Act III re-uses them)
        "camera_volumes": follow_volumes("Dock", [(0.0, 0.0), (30.0, 0.0), (60.0, 0.0)])
        + follow_volumes("FathersJetty", [(28.0, -1.8), (28.0, -19.0)]),
        "triggers": [{"id": "ship", "activation": "interact", "at": [30.0, 0.0, 1.6], "size": [6.0, 0, 1.2],
                      "prompt_key": "FIELD_PROMPT_CH15_SHIP", "payload": {"beat": "to_rim"}, "yaw": 0.0}],
    }


# --- Ch16: the Pale Rim -----------------------------------------------------------------------------------------------

RIM_LEN = 220.0


def pale_rim() -> dict:
    blocks = [box("Sand", RIM_LEN * 0.5 - 20.0, -0.5, 0.0, RIM_LEN + 40.0, 1.0, 60.0, color=COL_SAND),
              box("Shallows", RIM_LEN * 0.5 - 20.0, 0.12, 0.0, RIM_LEN + 40.0, 0.04, 60.0, color=COL_RIM_WATER,
                  solid=False)]
    for side, (x, z, sx, sz) in enumerate(((RIM_LEN * 0.5 - 20.0, -30.5, RIM_LEN + 40.0, 1.0),
                                           (RIM_LEN * 0.5 - 20.0, 30.5, RIM_LEN + 40.0, 1.0),
                                           (-40.5, 0.0, 1.0, 60.0), (RIM_LEN + 1.0, 0.0, 1.0, 60.0))):
        blocks.append(box(f"Haze{side}", x, 1.5, z, sx, 3.0, sz, color=COL_SAND))  # the white closes in: bounds
    blocks.append(box("Ship", -30.0, 1.5, 0.0, 6.0, 3.0, 18.0, color=COL_HULL))
    for k in range(8):  # cairns the waders keep to
        x = 10.0 + k * (RIM_LEN - 20.0) / 7
        blocks.append(box(f"Cairn{k}", x, 0.6, (-1.0) ** k * 4.0, 0.8, 1.2, 0.8, color=COL_CAIRN))
    return {
        "doc": "M4-C16-02 greybox (tools/act1/ch15_16_greybox.py; do not edit by hand): the Pale Rim, the white "
        "shallows at a white overcast noon (colour script ch16: no shadows). The ship waits at the Rim (west, Rim), then "
        "a long wade east over white sand a hand deep in water, the cairns the waders keep to, Kerrid last in the line "
        "(the party's order is the beat sheet's), to the Choir's edge (to_choir). The story waits on the beat sheet "
        "(M4-C16-01).",
        "sun": {"pitch_deg": -70.0, "yaw_deg": 0.0, "energy": 1.6, "color": "#f2f2ee"},
        "environment": {"background": "#f2f2ee", "ambient_color": "#d8dee4", "ambient_energy": 0.9},
        "block_color": COL_SAND,
        "blocks": blocks,
        # M4-A2P-016: ChoirEdge, where the montage (C2) sets the party down, ~25 m short of to_choir
        "spawns": {"Rim": [-24.0, 0.0, 0.0, 270.0], "ChoirEdge": [RIM_LEN - 15.0, 0.0, 0.0, 270.0]},
        "marks": {"choir_edge": [RIM_LEN, 0.0, 0.0, 270.0]},
        "actors": {},
        "shots": {"P01": {"pos": [-22.0, 1.8, 3.0], "look_at": [120.0, 1.0, 0.0], "fov": 40},
                  # M4-A2P-016 (docs/kb/plan/act2/chapters/ch16.md §4): C2's montage, three times of day (the grade
                  # changes, not the place): side-on wide by a cairn; low ahead, looking back down the line; high
                  # behind, Kerrid last, the line going on into the white
                  "P02": {"pos": [45.0, 1.4, 14.0], "look_at": [38.0, 1.0, 0.0], "fov": 40},
                  "P03": {"pos": [80.0, 0.6, 2.0], "look_at": [60.0, 1.2, 0.0], "fov": 35},
                  "P04": {"pos": [90.0, 4.0, -10.0], "look_at": [110.0, 1.0, 0.0], "fov": 45}},
        # M4-A2P-016: the Rim by the ship, then the wade in 60 m runs (the field is the walked legs either side of the
        # montage cut); the camera trails the line and a little south, so the cairns pass across the frame
        "camera_volumes": [{"id": "Rim", "mode": "pan_follow", "at": [-22.0, 1.5, 0.0], "size": [16.0, 4.0, 30.0],
                            "pos": [-12.0, 4.0, 12.0], "look_at": [-24.0, 1.0, 0.0], "fov": 50, "priority": 2}]
        + [{"id": f"Wade{k}", "mode": "pan_follow", "at": [r3(x0 + 30.0), 1.5, 0.0], "size": [60.0, 4.0, 60.0],
            "pos": [r3(x0 - 6.0), 4.5, 8.0], "look_at": [r3(x0 + 30.0), 0.8, 0.0], "fov": 50, "priority": 1}
           for k, x0 in enumerate((-30.0, 30.0, 90.0, 150.0, 210.0 - 30.0))],
        # M4-A2P-1500 (env-art-b): the exit stands on the sand, which ends at RIM_LEN; the east haze closes there
        "triggers": [{"id": "to_choir", "activation": "touch", "at": [RIM_LEN - 4.0, 0.0, 0.0], "size": [2.0, 0, 20.0],
                      "payload": {"beat": "to_choir"}, "yaw": 0.0}],
        # M4-C16-03: the rim's random fights (act2_roster.md Ch16); none in the Drowned Choir
        "encounters": {"table": [{"encounter": "ch16_rim_skates", "weight": 1}, {"encounter": "ch16_rim_crawlers", "weight": 1}],
                       "min_m": 95, "max_m": 145, "when": {"set": ["ch16_started"]}, "seed": 16},
    }


# --- Ch16: the Drowned Choir ------------------------------------------------------------------------------------------

CHOIR_R = 26.0
MOUTHS = 16


def drowned_choir() -> dict:
    blocks = water(-60.0, 60.0, -60.0, 60.0, color=COL_RIM_WATER)
    blocks.append(floor("Floor", 0.0, 0.0, CHOIR_R - 2.0, CHOIR_R - 2.0, 0.0, COL_CHOIR))
    blocks += walls("Floor", 0.0, 0.0, CHOIR_R - 2.0, CHOIR_R - 2.0, 0.0, 1.0, {"s": (-3.0, 3.0)})
    for k in range(MOUTHS):  # the ring of colossal mouths, open to the sky
        a = 2 * math.pi * k / MOUTHS
        x, z = CHOIR_R * math.sin(a), -CHOIR_R * math.cos(a)
        if abs(x) < 4.0 and z > 0.0:
            continue  # the way in, from the south
        blocks.append(box(f"Mouth{k}", r3(x), 7.0, r3(z), 7.0, 14.0, 4.0, math.degrees(-a), color=COL_CHOIR,
                          solid=False))
    blocks.append(floor("Approach", 0.0, CHOIR_R + 2.0, 3.0, 4.0, 0.0, COL_SAND))
    blocks.append(box("ApproachBound", 0.0, 1.0, CHOIR_R + 6.25, 6.0, 2.0, 0.5, color=COL_CHOIR))
    return {
        "doc": "M4-C16-02 greybox (tools/act1/ch15_16_greybox.py; do not edit by hand): the Drowned Choir at moonrise "
        "(colour script ch16): a ring of colossal mouths round a stone floor, the way in from the south (Approach). "
        "Kesh's place at the ring's head (kesh), where Sefir comes (sefir), Kerrid's line behind Asha (kerrid_line). "
        "Sefir's Abiding guard and the storm waking early are fought here; the act ends on a Rhen voice-over. The story "
        "waits on the beat sheet (M4-C16-01).",
        "sun": {"pitch_deg": -12.0, "yaw_deg": 90.0, "energy": 0.4, "color": "#c8d4e8"},  # the moon rising in the east
        "environment": {"background": "#1c2430", "ambient_color": "#5e8c90", "ambient_energy": 0.4},
        "block_color": COL_CHOIR,
        "blocks": blocks,
        "spawns": {"Approach": [0.0, 0.0, CHOIR_R + 1.0, 0.0]},
        "marks": {"kesh": [0.0, 0.0, -CHOIR_R + 6.0, 180.0], "sefir": [5.0, 0.0, -CHOIR_R + 9.0, 210.0],
                  "kerrid_line": [0.0, 0.0, 6.0, 0.0],
                  # M4-A2P-016: the party at the ring's heart facing Kesh's place (C4-C6); Kerrid a step behind Asha
                  "ring_rhen": [0.0, 0.0, -6.0, 0.0], "ring_asha": [-1.5, 0.0, -5.6, 0.0],
                  "ring_toma": [-3.0, 0.0, -5.0, 0.0], "ring_ysolde": [1.5, 0.0, -5.6, 0.0],
                  "ring_liss": [3.0, 0.0, -5.0, 0.0], "ring_kerrid": [-1.8, 0.0, -3.6, 0.0],
                  "sefir_ring": [5.0, 0.0, -CHOIR_R + 9.0, 210.0]},
        "actors": {},
        "shots": {"D01": {"pos": [0.0, 2.0, CHOIR_R - 4.0], "look_at": [0.0, 5.0, -CHOIR_R], "fov": 55},
                  # M4-A2P-016: C4 Kesh's point of view a thousand years ago (the memory grade), from her place down
                  # the ring; C5 Sefir across the ring, the stones behind him; C6 the three refusals in singles
                  # (D04 Asha, D06 Ysolde, D07 Kerrid), each from Sefir's side; C8 the storm waking over the ring,
                  # low behind Kerrid holding the line
                  "D02": {"pos": [0.0, 1.7, -20.5], "look_at": [0.0, 1.4, 0.0], "fov": 50},
                  "D03": {"pos": [1.0, 1.7, -9.0], "look_at": [5.0, 1.6, -17.0], "fov": 40},
                  "D04": {"pos": [0.2, 1.7, -8.4], "look_at": [-1.5, 1.6, -5.6], "fov": 40},
                  "D06": {"pos": [3.0, 1.7, -8.6], "look_at": [1.5, 1.6, -5.6], "fov": 40},
                  "D07": {"pos": [0.0, 1.9, -7.0], "look_at": [-1.8, 1.8, -3.6], "fov": 40},
                  "D05": {"pos": [1.5, 1.2, 10.0], "look_at": [0.0, 8.0, -CHOIR_R], "fov": 60}},
        # M4-A2P-016: the way in, then the bowl's floor (the ring itself is cutscene-only)
        "camera_volumes": [
            {"id": "Approach", "mode": "pan_follow", "at": [0.0, 1.5, CHOIR_R + 1.0], "size": [8.0, 4.0, 10.0],
             "pos": [0.0, 4.0, CHOIR_R + 7.0], "look_at": [0.0, 1.5, CHOIR_R - 10.0], "fov": 50, "priority": 2},
            {"id": "Bowl", "mode": "pan_follow", "at": [0.0, 1.5, 0.0], "size": [48.0, 4.0, 48.0],
             "pos": [0.0, 8.0, CHOIR_R + 4.0], "look_at": [0.0, 0.5, -4.0], "fov": 50, "priority": 1}],
        "triggers": [],
    }


def main() -> None:
    write("ch15", "open_sea", open_sea())
    write("ch17", "hollowmere", hollowmere())
    write("ch16", "pale_rim", pale_rim())
    write("ch16", "drowned_choir", drowned_choir())


if __name__ == "__main__":
    main()
