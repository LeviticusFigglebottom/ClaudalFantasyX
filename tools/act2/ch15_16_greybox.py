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

    python3 tools/act2/ch15_16_greybox.py
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


def overheard(dialogue: str, at: tuple[float, float, float], size: tuple[float, float, float], requires: str,
              blocked_by: str = "") -> dict:
    """M4-A2P-1012: a bark heard once in passing (a touch box; the dialogue plays overheard, the walk goes on)."""
    row = {"id": dialogue.split("_", 1)[1], "activation": "touch", "at": list(at), "size": list(size), "once": True,
           "requires_flag": requires, "payload": {"dialogue": dialogue, "overheard": True}, "yaw": 0.0}
    if blocked_by:
        row["blocked_by_flag"] = blocked_by
    return row


def listen(tid: str, dialogue: str, at: tuple[float, float, float], requires: str, blocked_by: str = "",
           prompt: str = "FIELD_PROMPT_LISTEN") -> dict:
    """M4-A2P-1012: someone (or something) to stop at: an interact box with a prompt."""
    row = {"id": tid, "activation": "interact", "at": list(at), "size": [1.4, 0, 1.4], "prompt_key": prompt,
           "requires_flag": requires, "payload": {"dialogue": dialogue}, "yaw": 0.0}
    if blocked_by:
        row["blocked_by_flag"] = blocked_by
    return row


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
        "doc": "M4-C15-02 greybox (tools/act2/ch15_16_greybox.py; do not edit by hand): the open sea at night aboard "
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
                  "bow_liss": [0.0, 0.0, -4.4, 0.0],
                  # M4-A2P-105: the shoal's held dead (ch15_the_shoal's `@vfx glimmer_held` cues; env-art-b's
                  # EbbingMotes field): `shoal` is the field's centre on the Shoal block's top, shoal_floor the same
                  # floor, shoal_rising half way up to the barge, kerrid_orbit about him at his seated chest,
                  # kerrid_scar his rope-burned hands
                  "shoal": [6.0, -2.75, -8.0, 0.0], "shoal_floor": [6.0, -2.75, -8.0, 0.0],
                  "shoal_rising": [3.0, -1.2, -1.0, 0.0], "kerrid_orbit": [0.0, 0.9, 4.2, 0.0],
                  "kerrid_scar": [0.0, 0.6, 4.0, 0.0]},
        # M4-A2P-105: the dawn at the bow (the `to_hollowmere` beat sets ch15_dawn): grey-rose, no sun yet; env-art-b
        # adds the dawn grade (environment_res: fog 0.03) and the fog bank at the bow to this row
        "variants": [{"when": {"set": ["ch15_dawn"]}, "sun": {"energy": 0.0},
                      "environment": {"background": "#b8a4a8", "ambient_color": "#9a8e96", "ambient_energy": 0.55}}],
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
        # M4-A2P-1012: at the bow, the wait for dawn is broken by the fin (B03-B04); after the shoal it comes (B09)
        "triggers": [{"id": "fin", "activation": "interact", "at": [0.0, 0.0, -4.2], "size": [2.0, 0, 1.2],
                      "prompt_key": "FIELD_PROMPT_CH15_BOW", "requires_flag": "ch15_started",
                      "blocked_by_flag": "ch15_wakefin_felled", "payload": {"beat": "fin"}, "yaw": 0.0},
                     {"id": "dawn", "activation": "interact", "at": [0.0, 0.0, -4.2], "size": [2.0, 0, 1.2],
                      "prompt_key": "FIELD_PROMPT_CH15_BOW", "requires_flag": "ch15_kerrid_revealed",
                      "payload": {"beat": "to_hollowmere"}, "yaw": 0.0}]
        # B02: the deck at night, talk to each (before the fin)
        + [listen(f"deck_{who}", f"ch15_deck_{who}", at, "ch15_started", "ch15_wakefin_felled")
           for who, at in (("liss", (0.8, 0.0, 1.5)), ("asha", (-1.4, 0.0, 0.4)), ("toma", (-1.4, 0.0, 2.2)),
                           ("ysolde", (1.4, 0.0, -0.2)), ("pell", (1.4, 0.0, -1.8)), ("kerrid", (0.0, 0.0, 4.6)))],
    }


# --- Ch15/17: Hollowmere ----------------------------------------------------------------------------------------------

# --- Ch17 (Act III, M5-A3P-1001): Dace's dry-dock on Hollowmere's east -----------------------------------------------
# env-art-b's placement (M5-A3P-1500): Dace's hull at DACE_AT, yaw 30, its frame's y over the water at DACE_Y; the
# berths in a row along its beam, 8.5 m apart, the first nearest the dock's east end, Tobin's post at its outer corner.
# The hull's +X (bow) runs along BOW, the row (first berth to Dace's) along ROW.
DACE_AT = (78.0, -24.0)
DACE_Y = -0.9
HULL_YAW = 30.0
BOW = (math.cos(math.radians(HULL_YAW)), -math.sin(math.radians(HULL_YAW)))
ROW = (BOW[1], -BOW[0])
FIRST_BERTH = (90.75, -1.92)
THIRD_BERTH = (82.25, -16.64)
TOBINS_POST = (98.7, -2.9)
ROW_SIDE_M = 3.0  # the walk runs this far off the berths' heads, toward the dock


def hull_point(x: float, y: float, z: float = 0.0) -> list[float]:
    """A point in Dace's hull's frame (x along it, bow +X; y over the water; z across), in the zone."""
    wx = DACE_AT[0] + x * BOW[0] - z * BOW[1]
    wz = DACE_AT[1] + x * BOW[1] + z * BOW[0]
    return [r3(wx), r3(y + DACE_Y), r3(wz)]


def act3_dry_dock() -> dict:
    """M5-A3P-1001: the gangway from the dock's east end to the first berth, the walk along the berths' heads, Tobin's
    berth, and floors for the hull's deck, cabin and engine bay (env-art-b's frame; its kit collision replaces them).
    Hidden until Ch17 (variants); in Ch17 the dock's east bound opens."""
    g1 = (r3(FIRST_BERTH[0] - BOW[0] * ROW_SIDE_M), r3(FIRST_BERTH[1] - BOW[1] * ROW_SIDE_M))
    g3 = (r3(THIRD_BERTH[0] - BOW[0] * ROW_SIDE_M), r3(THIRD_BERTH[1] - BOW[1] * ROW_SIDE_M))
    blocks = walk("Gangway", (60.0, 0.0), g1, trim=WALK_W * 0.5, posts=("GangPile", 0.3, 2.0, COL_HULL),
                  colors=(COL_PLANK, COL_HULL))
    blocks += walk("BerthWalk", g1, g3, trim=WALK_W * 0.5, posts=("BerthPile", 0.3, 2.0, COL_HULL),
                   colors=(COL_PLANK, COL_HULL))
    mid = ((FIRST_BERTH[0] + TOBINS_POST[0]) * 0.5, (FIRST_BERTH[1] + TOBINS_POST[1]) * 0.5)
    dx, dz = TOBINS_POST[0] - FIRST_BERTH[0], TOBINS_POST[1] - FIRST_BERTH[1]
    blocks.append(box("FirstBerthDeck", mid[0], -0.25, mid[1], r3(math.hypot(dx, dz) + 3.0), 0.5, 3.0,
                      math.degrees(math.atan2(-dz, dx)), color=COL_PLANK))
    deck, cabin, engine = hull_point(-4.0, 3.8), hull_point(-3.55, 1.85), hull_point(-0.6, 1.85)
    blocks.append(box("HullDeck", deck[0], r3(deck[1] - 0.25), deck[2], 4.4, 0.5, 3.0, HULL_YAW, color=COL_PLANK))
    blocks.append(box("HullCabinFloor", cabin[0], r3(cabin[1] - 0.15), cabin[2], 3.1, 0.3, 2.4, HULL_YAW,
                      color=COL_PLANK))
    blocks.append(box("HullEngineFloor", engine[0], r3(engine[1] - 0.15), engine[2], 2.0, 0.3, 2.4, HULL_YAW,
                      color=COL_PLANK))
    ids = [b["id"] for b in blocks]
    face_bow, face_row = r3(-60.0), r3(30.0)  # yaw that faces BOW, and ROW
    spawns = {"HullDeck": deck + [face_bow], "Cabin": hull_point(-2.8, 1.85, -0.23) + [face_bow],
              "EngineBay": engine + [face_bow], "Berths": [g1[0], 0.0, g1[1], face_row],
              "Fathers": [28.0, 0.0, -17.5, 0.0]}
    marks = {"cabin_seat": hull_point(-2.8, 1.85, -0.23) + [face_bow],
             "cabin_seat_b": hull_point(-2.8, 1.85, 0.6) + [face_bow],
             "deck_centre": deck + [face_bow], "deck_rail": hull_point(-4.0, 3.8, -1.3) + [face_bow],
             "deck_rail_b": hull_point(-4.0, 3.8, 1.3) + [face_bow],
             "engine_bench": engine + [face_bow], "engine_bench_b": hull_point(-0.6, 1.85, 0.8) + [face_bow],
             "fathers_table": [28.0, 0.0, -19.5, 0.0],
             "first_berth": [r3(TOBINS_POST[0] - BOW[0] * 1.2), 0.0, r3(TOBINS_POST[1] - BOW[1] * 1.2), 120.0],
             "first_berth_b": [r3(TOBINS_POST[0] - BOW[0] * 2.4), 0.0, r3(TOBINS_POST[1] - BOW[1] * 2.4), 120.0],
             "berth_walk": [r3((g1[0] + g3[0]) * 0.5), 0.0, r3((g1[1] + g3[1]) * 0.5), face_row]}
    gangway_x = 64.0
    triggers = [
        # B03: on the gangway, the dock-master walks them to the berths and points at the last one
        {"id": "a3_berths", "activation": "touch", "at": [gangway_x, 0.0, -0.1], "size": [2.0, 0, WALK_W],
         "once": True, "requires_flag": "ch17_started", "blocked_by_flag": "ch17_saw_the_hull",
         "payload": {"beat": "berths"}, "yaw": 0.0},
        # B04: the hull from the walk's end (the sails), then aboard (the ladder) to its rack, chart wall and cabin
        listen("a3_hull_sails", "ch17_hull_sails", (g3[0], 0.0, g3[1]), "ch17_saw_the_hull", prompt="FIELD_PROMPT_LOOK"),
        {"id": "a3_board", "activation": "interact", "at": [r3(g3[0] - ROW[0] * 1.6), 0.0, r3(g3[1] - ROW[1] * 1.6)],
         "size": [1.6, 0, 1.6], "prompt_key": "FIELD_PROMPT_CLIMB", "requires_flag": "ch17_saw_the_hull",
         "payload": {"beat": "board"}, "yaw": 0.0},
        # the tool rack and the chart wall are nodes of ch17_hull_sails, not scenes a trigger can start: they wait on
        # M5-A3P-1202 (one scene per file), as do the tally keeper, the chandler, Pell at the windmills and Ysolde
        # asleep (nodes of ch17_bark_lookout)
        # B05-B06: the hatch to the cabin: the ledger, then dusk on the deck
        {"id": "a3_hatch", "activation": "interact", "at": hull_point(-3.0, 3.8), "size": [1.4, 0, 1.4],
         "prompt_key": "FIELD_PROMPT_CLIMB", "requires_flag": "ch17_saw_the_hull",
         "blocked_by_flag": "ch17_read_the_ledger", "payload": {"beat": "ledger"}, "yaw": 0.0},
        # B08-B11: night on the deck (the choice), the first lamp next morning, Ysolde's table
        {"id": "a3_night", "activation": "interact", "at": hull_point(-2.4, 3.8), "size": [1.4, 0, 1.4],
         "prompt_key": "FIELD_PROMPT_REST", "requires_flag": "ch17_read_the_ledger",
         "blocked_by_flag": "ch17_chose_the_unbinding", "payload": {"beat": "night"}, "yaw": 0.0},
        # B07 (optional): the first berth, at Tobin's post
        listen("a3_first_berth", "ch17_first_berth", (r3(TOBINS_POST[0] - BOW[0] * 1.8), 0.0,
                                                      r3(TOBINS_POST[1] - BOW[1] * 1.8)),
               "ch17_read_the_ledger", "ch17_first_berth"),
        # B12: Hollowmere at work, and the hull boarded for the maiden flight (ch17_complete)
        {"id": "a3_aboard", "activation": "interact", "at": hull_point(-5.4, 3.8), "size": [1.4, 0, 1.4],
         "prompt_key": "FIELD_PROMPT_CH15_SHIP", "requires_flag": "ch17_verse_begun",
         "blocked_by_flag": "ch17_complete", "payload": {"beat": "aboard"}, "yaw": 0.0},
        overheard("ch17_bark_lookout", (30.0, 0.0, 0.0), (2.0, 0, WALK_W), "ch17_started"),
        # M5-A3P-1004: back aboard the Kite, moored off the dock's head (Ch18)
        {"id": "a3_to_kite", "activation": "interact", "at": [5.0, 0.0, -1.4], "size": [1.4, 0, 1.4],
         "prompt_key": "FIELD_PROMPT_CH18_BACK_TO_KITE", "requires_flag": "ch18_world_open",
         "payload": {"beat": "to_kite"}, "yaw": 0.0}]
    variants = [{"when": {"unset": ["ch17_started"]}, "hide": ids},
                {"when": {"set": ["ch17_started"]}, "hide": ["DockBoundE"], "show": ids}]
    return {"blocks": blocks, "spawns": spawns, "marks": marks, "triggers": triggers, "variants": variants}


def hollowmere() -> dict:
    act3 = act3_dry_dock()
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
    blocks += act3["blocks"]
    return {
        "doc": "M4-C15-02 greybox (tools/act2/ch15_16_greybox.py; do not edit by hand): Hollowmere at dawn in the fog, "
        "its first visit (colour script ch15; Act III's zone). The dock the barge comes in to (Dock), jetties to "
        "hull-houses on their platforms, Liss's father's (fathers_door), the pyre-raft off the dock's end (pyre_raft), "
        "the supper on the dock (supper: the side scene) and the Hollowmere ship moored along the dock (to_rim). The "
        "story waits on the beat sheet (M4-C15-01).",
        "sun": {"pitch_deg": -6.0, "yaw_deg": 90.0, "energy": 0.6, "color": "#c8d0d8"},  # 05:40, the sun in the fog
        "environment": {"background": "#a8b0b8", "ambient_color": "#8a96a0", "ambient_energy": 0.6},
        "block_color": COL_PLANK,
        "blocks": blocks,
        "spawns": {"Dock": [2.0, 0.0, 0.0, 270.0], **act3["spawns"]},
        "marks": {"fathers_door": [28.0, 0.0, -16.6, 0.0], "pyre_raft": [60.5, 0.0, 0.0, 270.0],
                  "supper": [40.0, 0.0, -0.8, 180.0],
                  # M4-A2P-015: Toma and Liss by the bier at the dock's end (C6); Liss's father across the table (C8)
                  "confess_toma": [57.0, 0.0, 0.6, 90.0], "confess_liss": [58.4, 0.0, -0.4, 270.0],
                  "supper_father": [40.0, 0.0, 1.0, 0.0], **act3["marks"]},
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
                      "prompt_key": "FIELD_PROMPT_CH15_SHIP", "requires_flag": "ch15_pyre_raft",
                      "blocked_by_flag": "ch15_complete", "payload": {"beat": "to_rim"}, "yaw": 0.0},
                     # M4-A2P-1012: the bier at the dock's end: "Let me carry him." (B12), then the pyre-raft (B13)
                     {"id": "jetty", "activation": "touch", "at": [56.0, 0.0, 0.0], "size": [2.0, 0, WALK_W],
                      "once": True, "requires_flag": "ch15_liss_told_father", "blocked_by_flag": "ch15_toma_confessed",
                      "payload": {"beat": "jetty"}, "yaw": 0.0},
                     # B14 and the side errands, the camp, Hollowmere's people (B11)
                     # Hollowmere's shrine by the dock's head, and the Rim's by the ship: save shrines
                     {"id": "shrine", "activation": "interact", "at": [3.0, 0.0, 1.4], "size": [1.6, 0, 1.6],
                      "prompt_key": "FIELD_PROMPT_REST", "requires_flag": "ch15_reached_hollowmere",
                      "payload": {"beat": "shrine", "save_shrine": "hollowmere_shrine"}, "yaw": 0.0},
                     # the chandler on the dock (shops.json hollowmere_chandler)
                     {"id": "shop", "activation": "interact", "at": [12.0, 0.0, 1.4], "size": [1.6, 0, 1.6], "prompt_key": "SHOP_PROMPT",
                      "requires_flag": "ch15_reached_hollowmere", "payload": {"shop": "hollowmere_chandler"}, "yaw": 0.0},
                     listen("supper", "ch15_two_daces", (40.0, 0.0, -1.2), "ch15_pyre_raft", "ch15_supper_with_father",
                            "FIELD_PROMPT_REST"),
                     listen("side_current_phrase", "ch15_side_the_current_phrase", (8.0, 0.0, -1.4),
                            "ch15_reached_hollowmere", "ch15_learned_current_phrase"),
                     listen("side_tally_hull", "ch15_side_the_tally_hull", (12.0, 0.0, -17.0), "ch15_toma_confessed",
                            "ch15_toma_on_the_tally", "FIELD_PROMPT_LOOK"),
                     listen("camp", "ch15_camp_the_bottom_step", (44.0, 0.0, -17.0), "ch15_kerrid_revealed",
                            "ch15_camp_talk", "FIELD_PROMPT_REST"),
                     listen("npc_wright", "ch15_bark_wright_pump", (20.0, 0.0, -1.4), "ch15_reached_hollowmere", "ch15_complete"),
                     listen("npc_outside", "ch15_bark_outside_the_level", (20.0, 0.0, 1.4), "ch15_reached_hollowmere", "ch15_complete"),
                     listen("npc_widow", "ch15_bark_widow", (34.0, 0.0, -1.4), "ch15_reached_hollowmere", "ch15_complete"),
                     listen("npc_lookout", "ch15_bark_lookout", (48.0, 0.0, -1.4), "ch15_reached_hollowmere", "ch15_complete"),
                     listen("npc_cook", "ch15_bark_raft_cook", (52.0, 0.0, 1.4), "ch15_reached_hollowmere", "ch15_complete"),
                     listen("npc_kerrid", "ch15_bark_kerrid_night", (28.0, 0.0, -8.0), "ch15_pyre_raft", "ch15_complete"),
                     overheard("ch15_bark_current_singer", (5.0, 0.0, 0.0), (2.0, 0, WALK_W), "ch15_reached_hollowmere", "ch15_complete"),
                     overheard("ch15_bark_child_pell", (16.0, 0.0, 0.0), (2.0, 0, WALK_W), "ch15_reached_hollowmere", "ch15_complete"),
                     overheard("ch15_bark_kerrid_floors", (38.0, 0.0, 0.0), (2.0, 0, WALK_W), "ch15_kerrid_revealed", "ch15_complete"),
                     overheard("ch15_bark_raft_child", (46.0, 0.0, 0.0), (2.0, 0, WALK_W), "ch15_pyre_raft", "ch15_complete")]
        + act3["triggers"],
        "variants": act3["variants"],
    }


# --- Ch16: the Pale Rim -----------------------------------------------------------------------------------------------

RIM_LEN = 220.0


def cairn(k: int) -> tuple[float, float]:
    """The k-th cairn the waders keep to (x, z)."""
    return 10.0 + k * (RIM_LEN - 20.0) / 7, (-1.0) ** k * 4.0


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
        x, z = cairn(k)
        blocks.append(box(f"Cairn{k}", x, 0.6, z, 0.8, 1.2, 0.8, color=COL_CAIRN))
    return {
        "doc": "M4-C16-02 greybox (tools/act2/ch15_16_greybox.py; do not edit by hand): the Pale Rim, the white "
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
                      "payload": {"beat": "to_choir"}, "yaw": 0.0}]
        # M4-A2P-1012: the wade's barks, day by day (B02), across the whole white; the cairns' finds and people
        + [overheard(d, (x, 0.0, 0.0), (2.0, 0, 58.0), "ch16_started")
           for d, x in (("ch16_bark_rhen_forward", 15.0), ("ch16_bark_ysolde_corran", 45.0),
                        ("ch16_bark_liss_cairns", 80.0), ("ch16_bark_toma_walked_back", 110.0),
                        ("ch16_bark_kerrid_south", 145.0), ("ch16_bark_asha_mother", 175.0))]
        + [listen("npc_cairn_wader", "ch16_bark_cairn_wader", (cairn(1)[0], 0.0, cairn(1)[1] + 1.4), "ch16_started"),
           listen("npc_turning_back", "ch16_bark_turning_back", (cairn(4)[0], 0.0, cairn(4)[1] - 1.4),
                  "ch16_started"),
           listen("counting_stone", "ch16_find_the_counting_stone", (cairn(2)[0], 0.0, cairn(2)[1] - 1.4),
                  "ch16_started", "ch16_found_counting_stone", "FIELD_PROMPT_LOOK"),
           listen("fallen_cairn", "ch16_side_the_fallen_cairn", (cairn(5)[0], 0.0, cairn(5)[1] + 1.4),
                  "ch16_started", "ch16_rebuilt_cairn", "FIELD_PROMPT_LOOK"),
           {"id": "shrine", "activation": "interact", "at": [-20.0, 0.0, 3.0], "size": [1.6, 0, 1.6],
            "prompt_key": "FIELD_PROMPT_REST", "requires_flag": "ch16_started",
            "payload": {"beat": "shrine", "save_shrine": "pale_rim_shrine"}, "yaw": 0.0},
           listen("camp", "ch16_camp_coming_up", (RIM_LEN - 30.0, 0.0, 3.0), "ch16_started", "ch16_camp_talk",
                  "FIELD_PROMPT_REST")],
        # M4-C16-03: the rim's random fights (act2_roster.md Ch16); none in the Drowned Choir
        "encounters": {"table": [{"encounter": "ch16_rim_skates", "weight": 1}, {"encounter": "ch16_rim_crawlers", "weight": 1}],
                       "min_m": 95, "max_m": 145, "when": {"set": ["ch16_started"]}, "seed": 16},
    }


# --- Ch16: the Drowned Choir ------------------------------------------------------------------------------------------

CHOIR_R = 26.0
MOUTHS = 16
# M4-A2P-106: the kit's amphitheatre (ch16_drowned_choir.md): the dais to r 7.5 at y 0, the flooded channel to r 9.5
# at -0.8, six 2 m tiers rising to 2.15 m at r 21.5; the singers stand in the sea at r 44
DAIS_R = 7.5
CHANNEL_R = 9.5
CHANNEL_Y = -0.8
TIERS = 6
TIER_W = 2.0
TIER_TOP = 2.15
TIER_RIM = CHANNEL_R + TIERS * TIER_W
AISLE_HW = 2.0
RING_SEGMENTS = 32
SINGERS_R = 44.0


def head_y(r: float) -> float:
    """The north aisle's height at radius r (its ramp from the bridge to the tiers' rim)."""
    return r3(TIER_TOP * min(max((r - CHANNEL_R) / (TIER_RIM - CHANNEL_R), 0.0), 1.0))


def drowned_choir() -> dict:
    """M4-A2P-106: the kit's amphitheatre (choir_amphitheatre): a dais, the flooded channel round it, six tiers. The
    tiers are ring segments; the south gap is the way in at sea level (over the south bridge), the north aisle a ramp
    up the tiers to Kesh's place (over the north bridge). Invisible curbs keep the player off the channel's water
    (the controller has no step-up). env-art-b's collision file can replace these blocks (collision_path)."""
    blocks = water(-60.0, 60.0, -60.0, 60.0, color=COL_RIM_WATER)
    blocks.append(box("ChannelBed", 0.0, CHANNEL_Y - 0.5, 0.0, 2 * CHANNEL_R, 1.0, 2 * CHANNEL_R, color=COL_RIM_WATER))
    for k in range(6):  # the dais: a 12-gon of rotated squares
        blocks.append(box(f"Dais{k}", 0.0, -0.5, 0.0, 2 * DAIS_R * math.cos(math.pi / 12), 1.0,
                          2 * DAIS_R * math.cos(math.pi / 12), 15.0 * k, color=COL_CHOIR))
    for side, z in (("S", 1.0), ("N", -1.0)):  # the bridges over the channel, on the aisles
        blocks.append(box(f"Bridge{side}", 0.0, -0.25, r3(z * (DAIS_R + CHANNEL_R) * 0.5), 2 * AISLE_HW, 0.5,
                          CHANNEL_R - DAIS_R + 1.0, color=COL_CHOIR))
    for k in range(RING_SEGMENTS):
        a = 2 * math.pi * (k + 0.5) / RING_SEGMENTS
        sa, ca = math.sin(a), -math.cos(a)  # 0 is north (-z)
        for t in range(TIERS):  # the tiers, open on the two aisles
            r0 = CHANNEL_R + t * TIER_W
            rm = r0 + TIER_W * 0.5
            if abs(rm * sa) < AISLE_HW + TIER_W * 0.5:
                continue
            h = TIER_TOP * (t + 1) / TIERS
            arc = 2 * math.pi * (r0 + TIER_W) / RING_SEGMENTS + 0.05
            blocks.append(box(f"Tier{t}_{k}", r3(rm * sa), r3((h + CHANNEL_Y) * 0.5), r3(rm * ca), arc,
                              r3(h - CHANNEL_Y), TIER_W, math.degrees(-a), color=COL_CHOIR))
        rc = DAIS_R + 0.15  # the curb on the dais's edge, but on the bridges
        if abs(rc * sa) > AISLE_HW:
            blocks.append(box(f"Curb{k}", r3(rc * sa), 0.5, r3(rc * ca), 2 * math.pi * rc / RING_SEGMENTS + 0.1, 1.0,
                              0.3, math.degrees(-a), color=COL_CHOIR, visible=False))
    gap_end = CHOIR_R - 1.5  # under the approach's near end
    blocks.append(floor("SouthGap", 0.0, r3((CHANNEL_R + gap_end) * 0.5), AISLE_HW, r3((gap_end - CHANNEL_R) * 0.5),
                        0.0, COL_CHOIR))
    for side in (-1.0, 1.0):  # the aisle's walls where the tiers stand above it
        blocks.append(box(f"AisleWallS{'WE'[side > 0]}", side * (AISLE_HW + 0.25), 1.0,
                          r3((CHANNEL_R + TIER_RIM) * 0.5), 0.5, 2.0, TIER_RIM - CHANNEL_R, color=COL_CHOIR,
                          visible=False))
        blocks.append(box(f"AisleWallN{'WE'[side > 0]}", side * (AISLE_HW + 0.25), TIER_TOP * 0.5 + 0.5,
                          r3(-(CHANNEL_R + TIER_RIM) * 0.5), 0.5, TIER_TOP + 1.0, TIER_RIM - CHANNEL_R,
                          color=COL_CHOIR, visible=False))
    blocks.append(box("HeadBound", 0.0, TIER_TOP + 0.5, -TIER_RIM - 0.25, 2 * AISLE_HW + 1.0, 1.0, 0.5,
                      color=COL_CHOIR, visible=False))
    for k in range(MOUTHS):  # the singers in the sea (dressing), the way in from the south clear
        a = 2 * math.pi * k / MOUTHS
        x, z = SINGERS_R * math.sin(a), -SINGERS_R * math.cos(a)
        if abs(x) < 6.0 and z > 0.0:
            continue
        blocks.append(box(f"Mouth{k}", r3(x), 7.0, r3(z), 7.0, 14.0, 4.0, math.degrees(-a), color=COL_CHOIR,
                          solid=False))
    blocks.append(floor("Approach", 0.0, CHOIR_R + 2.0, 3.0, 4.0, 0.0, COL_SAND))
    blocks.append(box("ApproachBound", 0.0, 1.0, CHOIR_R + 6.25, 6.0, 2.0, 0.5, color=COL_CHOIR))
    ramps = [{"id": "HeadAisle", "from": [0.0, 0.0, -CHANNEL_R], "to": [0.0, TIER_TOP, -TIER_RIM],
              "width": 2 * AISLE_HW, "color": COL_CHOIR}]
    return {
        "doc": "M4-C16-02 greybox (tools/act2/ch15_16_greybox.py; do not edit by hand): the Drowned Choir at moonrise "
        "(colour script ch16). M4-A2P-106: the kit's amphitheatre: the dais, the flooded channel (bridged north and "
        "south), six tiers to the rim, the singers standing in the sea at r 44; the way in from the south (Approach) "
        "through the tiers' gap, the north aisle a ramp up to Kesh's place. "
        "Kesh's place at the ring's head (kesh), where Sefir comes (sefir), Kerrid's line behind Asha (kerrid_line). "
        "Sefir's Abiding guard and the storm waking early are fought here; the act ends on a Rhen voice-over. The story "
        "waits on the beat sheet (M4-C16-01).",
        "sun": {"pitch_deg": -12.0, "yaw_deg": 90.0, "energy": 0.4, "color": "#c8d4e8"},  # the moon rising in the east
        "environment": {"background": "#1c2430", "ambient_color": "#5e8c90", "ambient_energy": 0.4},
        "block_color": COL_CHOIR,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": {"Approach": [0.0, 0.0, CHOIR_R + 1.0, 0.0]},
        # M4-A2P-106: Kesh's place on the north aisle near the rim, Sefir on the fifth tier beside it
        "marks": {"kesh": [0.0, head_y(20.0), -20.0, 180.0], "sefir": [5.0, r3(TIER_TOP * 5 / TIERS), -17.0, 210.0],
                  "kerrid_line": [0.0, 0.0, 6.0, 0.0],
                  # M4-A2P-016: the party at the ring's heart facing Kesh's place (C4-C6); Kerrid a step behind Asha
                  "ring_rhen": [0.0, 0.0, -6.0, 0.0], "ring_asha": [-1.5, 0.0, -5.6, 0.0],
                  "ring_toma": [-3.0, 0.0, -5.0, 0.0], "ring_ysolde": [1.5, 0.0, -5.6, 0.0],
                  "ring_liss": [3.0, 0.0, -5.0, 0.0], "ring_kerrid": [-1.8, 0.0, -3.6, 0.0],
                  "sefir_ring": [5.0, r3(TIER_TOP * 5 / TIERS), -17.0, 210.0]},
        "actors": {},
        "shots": {"D01": {"pos": [0.0, 2.0, CHOIR_R - 4.0], "look_at": [0.0, 5.0, -CHOIR_R], "fov": 55},
                  # M4-A2P-016: C4 Kesh's point of view a thousand years ago (the memory grade), from her place down
                  # the ring; C5 Sefir across the ring, the stones behind him; C6 the three refusals in singles
                  # (D04 Asha, D06 Ysolde, D07 Kerrid), each from Sefir's side; C8 the storm waking over the ring,
                  # low behind Kerrid holding the line
                  "D02": {"pos": [0.0, r3(head_y(20.5) + 1.7), -20.5], "look_at": [0.0, 1.4, 0.0], "fov": 50},
                  "D03": {"pos": [1.0, 1.7, -9.0], "look_at": [5.0, r3(TIER_TOP * 5 / TIERS + 1.6), -17.0], "fov": 40},
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
