#!/usr/bin/env python3
"""Ch13 "Gold and Lacquer" greybox (M4-C13-02): the geography of ch13/ansedra, ch13/sanctum and ch13/lamp_archive,
before the beat sheet (M4-C13-01) adds the story. From act_outline.md (Ch13; ADR 0016's Lamp Archive, ADR 0022 (c)'s
Kerrid at the moorings) and the colour script's `ch13` (an overcast 16:30, perfectly still air, gold bowl-domes doubled
in a mirror lagoon under a white-grey sky; gold that must feel cold).

  ch13/ansedra       the holy city on its mirror lagoon: the outer moorings (south, `kerrid_moorings`: Kerrid sits
                     out the nights there among the barge-polers), a stone causeway north to the central island and
                     Sefir's house (`sefir_door`), a causeway west to the house Ysolde shared with Corran
                     (`corran_house`: the side scene), one east to the Lamp Archive's doors (to_archive) and one north
                     to the Sanctum's gate (to_sanctum); gold bowl-domes on every island.
  ch13/sanctum       the Glimmer temple: the vestibule, then the nave round the basin, a perfect mirror lit from
                     beneath by a light that never moves (not walkable: a kneeling ledge rings it), Ethren's place at
                     its head (`ethren`) and Corran's (`corran`). Kerrid never comes in.
  ch13/lamp_archive  the Order's library of Lit Age records: the reading room's tables (`ledgers`, `cantor_roll`)
                     between long stacks.

x is east, north is -Z. Shares Ch10's and Ch11's builders.

    python3 tools/act1/ch13_greybox.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import WALK_W, box, follow_volumes, walk, water  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ZONES = ROOT / "game" / "levels" / "ch13"
COL_STONE = "#bab4a8"
COL_PARAPET = "#8a8478"
COL_GOLD = "#b8a070"  # gold, cooled (lut_ch13_still)
COL_LACQUER = "#7a2a24"
COL_MIRROR = "#5e6e80"
COL_SHELF = "#4a3a2c"
COL_TABLE = "#6a5640"
GLOW_STILL = "#f0e8c8"  # the light under the basin that never moves (glimmer_bound, held)
SUN = {"pitch_deg": -25.0, "yaw_deg": 130.0, "energy": 1.6, "color": "#fff9f2"}
ENV = {"background": "#c8c4ba", "ambient_color": "#8a96a4", "ambient_energy": 0.6}
INTERIOR_ENV = {"background": "#2a2620", "ambient_color": "#8a8478", "ambient_energy": 0.5}
# M4-A2P-103 (env-art-b, ch13_sanctum_dressing.py REQUESTED_SUN_ENERGY / REQUESTED_FILL): the Sanctum's only light is
# the bound light under the basin, so no sun through the vault's seams and a dim cool fill
SANCTUM_SUN = dict(SUN, energy=0.0)
SANCTUM_ENV = {"background": "#2a2620", "ambient_color": "#8a96a4", "ambient_energy": 0.2}


def causeway(cid: str, a: tuple[float, float], b: tuple[float, float]) -> list[dict]:
    return walk(cid, a, b, trim=WALK_W * 0.5, posts=("Lamp", 0.3, 3.2, COL_GOLD), colors=(COL_STONE, COL_PARAPET))


def doorstep(sid: str) -> list[dict]:
    """The step outside a room's south door (z 0 .. 2), where the way back to the city is."""
    return [floor(sid, 0.0, 1.0, 2.6, 1.0, 0.0, COL_STONE),
            box(f"{sid}Bound", 0.0, 1.0, 2.25, 5.2, 2.0, 0.5, color=COL_PARAPET)]


def island(iid: str, cx: float, cz: float, h: float, dome: bool, gaps: dict) -> list[dict]:
    out = [floor(iid, cx, cz, h, h, 0.0, COL_STONE)] + walls(iid, cx, cz, h, h, 0.0, 1.0, gaps)
    if dome:
        out.append(box(f"{iid}Dome", cx, 4.0, cz, h * 0.9, 8.0, h * 0.9, color=COL_GOLD, solid=False))
    return out


# --- Ansedra ----------------------------------------------------------------------------------------------------------

def overheard(dialogue: str, at: tuple[float, float, float], size: tuple[float, float, float],
              requires: str = "ch13_started", blocked_by: str = "") -> dict:
    """M4-A2P-1003 E5: a bark heard once in passing (a touch box; the dialogue plays overheard, the walk goes on)."""
    row = {"id": dialogue.removeprefix("ch13_"), "activation": "touch", "at": list(at), "size": list(size),
           "once": True, "requires_flag": requires, "payload": {"dialogue": dialogue, "overheard": True}, "yaw": 0.0}
    if blocked_by:
        row["blocked_by_flag"] = blocked_by
    return row


def listen(tid: str, dialogue: str, at: tuple[float, float, float], requires: str, blocked_by: str = "",
           prompt: str = "FIELD_PROMPT_LISTEN", beat: str = "") -> dict:
    """M4-A2P-1003 E5: someone (or something) to stop at: an interact box with a prompt."""
    row = {"id": tid, "activation": "interact", "at": list(at), "size": [1.6, 0, 1.6], "prompt_key": prompt,
           "requires_flag": requires, "payload": {"beat": beat} if beat else {"dialogue": dialogue}, "yaw": 0.0}
    if blocked_by:
        row["blocked_by_flag"] = blocked_by
    return row


def ansedra() -> dict:
    blocks = water(-60.0, 60.0, -120.0, 30.0, color=COL_MIRROR)
    blocks += island("Moorings", 0.0, 10.0, 8.0, False, {"n": (-2.2, 2.2)})
    blocks.append(box("BargeA", -11.0, -0.1, 10.0, 2.0, 0.6, 9.0, color=COL_LACQUER, solid=False))
    blocks.append(box("BargeB", 11.0, -0.1, 12.0, 2.0, 0.6, 9.0, color=COL_LACQUER, solid=False))
    blocks += causeway("CausewayN", (0.0, 2.0), (0.0, -30.0))
    blocks += island("Centre", 0.0, -40.0, 10.0, False, {"s": (-2.2, 2.2), "w": (-2.2, 2.2), "e": (-2.2, 2.2),
                                                        "n": (-2.2, 2.2)})
    blocks.append(box("SefirHouse", 5.0, 3.0, -46.0, 8.0, 6.0, 6.0, color=COL_LACQUER))
    blocks.append(box("SefirHouseDome", 5.0, 7.0, -46.0, 6.0, 2.0, 5.0, color=COL_GOLD, solid=False))
    blocks += causeway("CausewayW", (-10.0, -40.0), (-34.0, -40.0))
    blocks += island("CorranIsle", -42.0, -40.0, 8.0, False, {"e": (-2.2, 2.2)})
    blocks.append(box("CorranHouse", -44.0, 2.5, -44.0, 6.0, 5.0, 5.0, color=COL_PARAPET))
    blocks += causeway("CausewayE", (10.0, -40.0), (34.0, -40.0))
    blocks += island("ArchiveIsle", 42.0, -40.0, 8.0, True, {"w": (-2.2, 2.2)})
    blocks += causeway("CausewaySanctum", (0.0, -50.0), (0.0, -82.0))
    blocks += island("SanctumIsle", 0.0, -94.0, 12.0, True, {"s": (-2.2, 2.2)})
    return {
        "doc": "M4-C13-02 greybox (tools/act1/ch13_greybox.py; do not edit by hand): Ansedra, the holy city on its "
        "mirror lagoon at an overcast 16:30 (colour script ch13). The outer moorings (Moorings; kerrid_moorings: "
        "Kerrid sits out the nights there among the barge-polers, ADR 0022 (c)), a causeway north to the central "
        "island and Sefir's house (sefir_door), west to Corran's old house (corran_house: Ysolde's side scene), east "
        "to the Lamp Archive (to_archive), north to the Sanctum (to_sanctum); gold bowl-domes. The story waits on the "
        "beat sheet (M4-C13-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_STONE,
        "blocks": blocks,
        "spawns": {"Moorings": [0.0, 0.0, 12.0, 0.0], "FromSanctum": [0.0, 0.0, -78.0, 180.0],
                   "FromArchive": [38.0, 0.0, -40.0, 90.0]},
        "marks": {"kerrid_moorings": [-6.0, 0.0, 14.0, 90.0], "sefir_door": [5.0, 0.0, -42.4, 180.0],
                  "corran_house": [-44.0, 0.0, -40.8, 180.0],
                  # M4-A2P-013: Sefir at the head of his table (C2); Sefir across from Liss on the Archive causeway (C7)
                  "house_sefir": [5.0, 0.0, -41.6, 180.0], "pact_sefir": [36.5, 0.0, -40.0, 270.0]},
        # M4-A2P-013: Kerrid sits out the nights at the moorings among the barge-polers once the party are Sefir's
        # guests (ADR 0022 (c)): the stage actor hides his follower, so he never walks the inner causeways
        "actors": {"kerrid": {"at": [-6.0, 0.0, 14.0, 90.0], "color": "#8a7a5a", "radius": 0.38, "height": 1.95,
                              "hidden": True}},
        "states": [{"flag": "ch13_guest_of_sefir", "show": ["kerrid"]}],
        "shots": {"A01": {"pos": [0.0, 2.5, 16.0], "look_at": [0.0, 6.0, -94.0], "fov": 40},
                  # M4-A2P-013 (docs/kb/plan/act2/chapters/ch13.md §4): C1 the domes doubled in the still lagoon
                  # (static; the mirror is the subject); C2 Sefir's table, Sefir at the head; C5 a causeway, the
                  # wedding announced; C7 Sefir and Liss close, the dead-still lagoon behind; C8 Corran's doorway
                  "A02": {"pos": [6.5, 1.6, 3.5], "look_at": [20.0, 3.0, -60.0], "fov": 45},
                  "A03": {"pos": [1.2, 1.6, -36.8], "look_at": [5.0, 1.5, -41.6], "fov": 45},
                  "A04": {"pos": [1.63, 2.15, -81.81], "look_at": [0.0, 1.5, -74.0], "fov": 50},
                  "A05": {"pos": [36.5, 1.57, -36.0], "look_at": [36.5, 1.5, -40.0], "fov": 40},
                  "A06": {"pos": [-41.18, 1.71, -36.21], "look_at": [-44.0, 1.5, -41.5], "fov": 45}},
        # M4-A2P-013: a pan-follow per causeway (the domes block the hub orbit), the moorings and the central island
        "camera_volumes": [
            {"id": "Moorings", "mode": "pan_follow", "at": [0.0, 1.5, 10.0], "size": [16.0, 4.0, 16.0],
             "pos": [0.0, 6.0, 22.0], "look_at": [0.0, 0.5, 8.0], "fov": 50, "priority": 1},
            {"id": "Centre", "mode": "pan_follow", "at": [0.0, 1.5, -40.0], "size": [20.0, 4.0, 20.0],
             "pos": [0.0, 7.0, -27.0], "look_at": [0.0, 0.5, -42.0], "fov": 50, "priority": 1},
            {"id": "ArchiveIsle", "mode": "pan_follow", "at": [42.0, 1.5, -40.0], "size": [16.0, 4.0, 16.0],
             "pos": [30.0, 5.0, -34.0], "look_at": [42.0, 0.5, -40.0], "fov": 50, "priority": 1}]
        + follow_volumes("CausewayN", [(0.0, 2.0), (0.0, -30.0)])
        + follow_volumes("CausewayW", [(-10.0, -40.0), (-34.0, -40.0)])
        + follow_volumes("CausewayE", [(10.0, -40.0), (34.0, -40.0)])
        + follow_volumes("CausewaySanctum", [(0.0, -50.0), (0.0, -82.0)]),
        "triggers": [{"id": "to_sanctum", "activation": "touch", "at": [0.0, 0.0, -84.0], "size": [4.0, 0, 1.5],
                      "payload": {"beat": "to_sanctum"}, "yaw": 0.0},
                     {"id": "to_archive", "activation": "touch", "at": [46.0, 0.0, -40.0], "size": [2.0, 0, 4.0],
                      "payload": {"beat": "to_archive"}, "yaw": 0.0},
                     # M4-A2P-1003 E8: the pact at the moorings, where Kerrid sits out the nights (B10)
                     {"id": "pact", "activation": "touch", "at": [-6.0, 0.0, 14.0], "size": [3.0, 0, 3.0],
                      "once": True, "requires_flag": "ch13_archive_read", "blocked_by_flag": "ch13_pact_of_silence",
                      "payload": {"beat": "pact"}, "yaw": 0.0},
                     # E1: Sefir's door: the night's rest, then the Lacquer Court in the morning
                     listen("rest", "", (2.5, 0.0, -41.6), "ch13_pact_of_silence", prompt="FIELD_PROMPT_REST",
                            beat="rest"),
                     # E5: the city's barks, side scenes and the guest house's camp
                     overheard("ch13_bark_liss_palm", (0.0, 0.0, -4.0), (4.0, 0, 2.0)),
                     overheard("ch13_bark_pilgrim", (0.0, 0.0, -18.0), (4.0, 0, 2.0)),
                     overheard("ch13_bark_stillguard", (-22.0, 0.0, -40.0), (2.0, 0, 4.0)),
                     overheard("ch13_bark_ysolde_holiness", (22.0, 0.0, -40.0), (2.0, 0, 4.0)),
                     overheard("ch13_bark_tender", (0.0, 0.0, -62.0), (4.0, 0, 2.0)),
                     listen("npc_bargeman", "ch13_bark_bargeman", (7.0, 0.0, 8.0), "ch13_started"),
                     # the still basin on the moorings, a save shrine (ShrineServices)
                     {"id": "shrine", "activation": "interact", "at": [4.0, 0.0, 15.0], "size": [1.6, 0, 1.6],
                      "prompt_key": "FIELD_PROMPT_REST", "requires_flag": "ch13_started",
                      "payload": {"beat": "shrine", "save_shrine": "ansedra_shrine"}, "yaw": 0.0},
                     # the purveyor on the central island (shops.json ansedra_purveyor)
                     {"id": "shop", "activation": "interact", "at": [-6.0, 0.0, -44.0], "size": [1.6, 0, 1.6], "prompt_key": "SHOP_PROMPT",
                      "requires_flag": "ch13_started", "payload": {"shop": "ansedra_purveyor"}, "yaw": 0.0},
                     listen("npc_seamstress", "ch13_bark_seamstress", (-6.0, 0.0, -35.0), "ch13_wedding_announced"),
                     listen("side_the_leaning_flame", "ch13_side_the_leaning_flame", (6.0, 0.0, -34.0),
                            "ch13_wedding_announced"),
                     listen("side_corran_house", "ch13_someone_elses_house", (-44.0, 0.0, -39.0), "ch13_started",
                            "ch13_corran_house", "FIELD_PROMPT_LOOK"),
                     listen("moorings_kerrid", "ch13_moorings_kerrid", (-4.5, 0.0, 14.0), "ch13_guest_of_sefir",
                            "ch13_sat_at_moorings"),
                     listen("camp", "ch13_camp_twenty_four_years", (8.0, 0.0, -41.0), "ch13_ethren_bound",
                            "ch13_camp_talk", "FIELD_PROMPT_REST")],
    }


# --- The Sanctum ------------------------------------------------------------------------------------------------------

def sanctum() -> dict:
    blocks = [floor("Vestibule", 0.0, -6.0, 6.0, 6.0, 0.0, COL_STONE)] + doorstep("GateStep")
    blocks += walls("Vestibule", 0.0, -6.0, 6.0, 6.0, 0.0, 6.0, {"s": (-2.2, 2.2), "n": (-3.0, 3.0)})
    blocks.append(floor("Nave", 0.0, -30.0, 12.0, 18.0, 0.0, COL_STONE))
    blocks += walls("Nave", 0.0, -30.0, 12.0, 18.0, 0.0, 10.0, {"s": (-3.0, 3.0)})
    blocks.append(box("Basin", 0.0, -0.05, -30.0, 10.0, 0.1, 18.0, color=COL_MIRROR, emission=GLOW_STILL,
                      emission_energy=0.6, solid=False))
    for k, (x, z, sx, sz) in enumerate(((0.0, -20.8, 10.8, 0.4), (0.0, -39.2, 10.8, 0.4), (-5.2, -30.0, 0.4, 18.0),
                                        (5.2, -30.0, 0.4, 18.0))):
        blocks.append(box(f"KneelingLedge{k}", x, 0.2, z, sx, 0.4, sz, color=COL_PARAPET))
    blocks.append(box("BasinBed", 0.0, -1.0, -30.0, 10.0, 0.2, 18.0, color=COL_MIRROR))
    blocks.append(box("Apse", 0.0, 5.0, -47.5, 24.0, 10.0, 1.0, color=COL_GOLD))
    return {
        "doc": "M4-C13-02 greybox (tools/act1/ch13_greybox.py; do not edit by hand): the Sanctum of the Level, the "
        "Glimmer temple. The vestibule (Gate), then the nave round the basin, a perfect mirror that has not stirred in "
        "four hundred years, lit from beneath by a light that never moves (Basin; a kneeling ledge rings it: nobody "
        "walks on it), Ethren's place at its head (ethren) and Corran's (corran). Kerrid never comes in. Back to the "
        "city at to_city. The story waits on the beat sheet (M4-C13-01).",
        "sun": SANCTUM_SUN,
        "environment": SANCTUM_ENV,
        "block_color": COL_STONE,
        "blocks": blocks,
        "spawns": {"Gate": [0.0, 0.0, -5.0, 0.0]},  # in from the door: the followers trail inside the vestibule
        "marks": {"ethren": [0.0, 0.0, -42.0, 0.0], "corran": [7.5, 0.0, -42.0, 300.0], "pilgrims": [0.0, 0.0, -19.4, 0.0],
                  "basin_ysolde": [7.5, 0.0, -39.6, 0.0]},  # M4-A2P-013: C4, Ysolde before Corran
        "actors": {},
        "shots": {"S01": {"pos": [0.0, 1.6, -16.0], "look_at": [0.0, 0.5, -40.0], "fov": 45},
                  # M4-A2P-013: C4 Ysolde before Corran at the basin's head, a Cantor beside her
                  "S02": {"pos": [-3.0, 1.8, -35.0], "look_at": [7.5, 1.0, -41.0], "fov": 45}},
        # M4-A2P-013: the gate and the basin's edge
        "camera_volumes": [
            {"id": "Gate", "mode": "pan_follow", "at": [0.0, 1.5, -5.0], "size": [12.0, 4.0, 12.0],
             "pos": [0.0, 3.5, 0.0], "look_at": [0.0, 1.0, -10.0], "fov": 50, "priority": 1},
            {"id": "BasinEdge", "mode": "pan_follow", "at": [0.0, 1.5, -30.0], "size": [24.0, 4.0, 36.0],
             "pos": [0.0, 5.5, -13.0], "look_at": [0.0, 0.5, -32.0], "fov": 55, "priority": 1}],
        "triggers": [{"id": "to_city", "activation": "touch", "at": [0.0, 0.0, 0.5], "size": [4.0, 0, 1.0],
                      "payload": {"beat": "to_city"}, "yaw": 0.0},
                     # M4-A2P-114: the basin's edge among the pilgrims, where Ethren is bound (B05-B06)
                     {"id": "ledge", "activation": "touch", "at": [0.0, 0.0, -19.4], "size": [4.0, 0, 1.5],
                      "requires_flag": "ch13_entered_sanctum", "blocked_by_flag": "ch13_ethren_bound",
                      "payload": {"beat": "ledge"}, "yaw": 0.0},
                     # M4-A2P-1003 E5: the kneelers at the ledge, and Wenna's third mark behind the vestibule's rail
                     listen("npc_kneeler", "ch13_bark_kneeler", (-4.0, 0.0, -17.5), "ch13_entered_sanctum"),
                     listen("npc_pilgrim_child", "ch13_bark_pilgrim_child", (4.0, 0.0, -17.5), "ch13_entered_sanctum"),
                     listen("wenna_mark", "ch13_wenna_mark", (-4.0, 0.0, -8.0), "ch13_entered_sanctum",
                            "ch13_found_wenna_mark", "FIELD_PROMPT_LOOK")],
    }


# --- The Lamp Archive -------------------------------------------------------------------------------------------------

STACKS = 5


def lamp_archive() -> dict:
    blocks = [floor("ReadingRoom", 0.0, -16.0, 10.0, 16.0, 0.0, COL_STONE)] + doorstep("DoorStep")
    blocks += walls("ReadingRoom", 0.0, -16.0, 10.0, 16.0, 0.0, 8.0, {"s": (-2.2, 2.2)})
    for k in range(STACKS):
        z = -6.0 - k * 5.5
        for side in (-1.0, 1.0):
            blocks.append(box(f"Stack{k}{'WE'[side > 0]}", side * 7.0, 3.0, z, 5.0, 6.0, 1.0, color=COL_SHELF))
    blocks.append(box("LedgerTable", -1.5, 0.45, -12.0, 2.0, 0.9, 4.0, color=COL_TABLE))
    blocks.append(box("RollTable", 1.5, 0.45, -24.0, 2.0, 0.9, 4.0, color=COL_TABLE))
    return {
        "doc": "M4-C13-02 greybox (tools/act1/ch13_greybox.py; do not edit by hand): the Lamp Archive, the Order's "
        "library of Lit Age records (ADR 0016): the reading room between long stacks, the table where Liss lays the "
        "founders' lamp-ledgers side by side (ledgers) and the one with the Cantor roll (cantor_roll). Back to the city "
        "at to_city. The story waits on the beat sheet (M4-C13-01).",
        "sun": SUN,
        "environment": INTERIOR_ENV,
        "block_color": COL_STONE,
        "blocks": blocks,
        "spawns": {"Door": [0.0, 0.0, -2.0, 0.0]},
        "marks": {"ledgers": [-3.2, 0.0, -12.0, 270.0], "cantor_roll": [3.2, 0.0, -24.0, 90.0]},
        "actors": {},
        "shots": {"R01": {"pos": [0.0, 2.2, -4.0], "look_at": [0.0, 1.0, -24.0], "fov": 50},
                  # M4-A2P-013: C6b the kept/spent column (insert; then Liss's face); C6c the pages side by side
                  "R02": {"pos": [-2.91, 2.02, -12.0], "look_at": [-1.5, 0.9, -12.0], "fov": 35},
                  "R03": {"pos": [1.5, 3.45, -23.51], "look_at": [1.5, 0.9, -24.0], "fov": 40}},
        # M4-A2P-013: the two reading bays between the stacks
        "camera_volumes": [
            {"id": "LedgerBay", "mode": "pan_follow", "at": [0.0, 1.5, -10.0], "size": [10.0, 4.0, 16.0],
             # in the aisle inside the door, over the ledger table (the POI stills, 10-30: at z 1.5 it stood outside the
             # south wall, in the door frame)
             "pos": [2.0, 3.4, -3.0], "look_at": [-1.5, 0.8, -11.0], "fov": 50, "priority": 1},
            {"id": "RollBay", "mode": "pan_follow", "at": [0.0, 1.5, -24.0], "size": [10.0, 4.0, 12.0],
             "pos": [0.0, 3.5, -15.0], "look_at": [1.0, 0.8, -24.0], "fov": 50, "priority": 1}],
        "triggers": [{"id": "to_city", "activation": "touch", "at": [0.0, 0.0, 0.5], "size": [4.0, 0, 1.0],
                      "payload": {"beat": "to_city"}, "yaw": 0.0},
                     # M4-A2P-114: the ledger table (B07, the first day; E2: once Ethren is bound); the Cantor roll (B08) is the
                     # second day's arrival (E9)
                     {"id": "ledgers", "activation": "touch", "at": [-3.2, 0.0, -12.0], "size": [1.5, 0, 3.0],
                      "requires_flag": "ch13_ethren_bound", "blocked_by_flag": "ch13_read_ledgers",
                      "payload": {"beat": "ledgers"}, "yaw": 0.0},
                     # M4-A2P-1003 E5: the clerk, and the pilgrims' register on its stand by the door
                     listen("npc_archivist", "ch13_bark_archivist", (3.0, 0.0, -4.0), "ch13_entered_archive"),
                     listen("velamir_register", "ch13_find_velamir_register", (-3.0, 0.0, -3.5),
                            "ch13_entered_archive", "ch13_found_velamir_register", "FIELD_PROMPT_LOOK")],
    }


def main() -> None:
    for name, layout in (("ansedra", ansedra()), ("sanctum", sanctum()), ("lamp_archive", lamp_archive())):
        out = ZONES / name / f"{name}_layout.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
