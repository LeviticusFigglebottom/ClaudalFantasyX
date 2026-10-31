#!/usr/bin/env python3
"""M5-A3P-1004 greybox: Ch18's `ch18/kite`, Dace's hull flying (act3_ch18.md K01, K02, K07, K08): the deck from the
bow to the stern rail, the wheel aft, the chart table amidships. Until Design's Kite world map exists (act3_ch18.md §9),
the chart table's courses are interactables round it: Reedhollow, Hollowmere, Pemakar, Tamsule, Corrow, Quellan,
Ansedra (seen from the air) and, once the night aboard has played, Iskarra.

Writes game/levels/ch18/kite/kite_layout.json. Usage: python3 tools/act3/ch18_greybox.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "act2"))
from ch10_greybox import box, r3  # noqa: E402
from ch15_16_greybox import write  # noqa: E402

COL_DECK = "#8a7458"
COL_RAIL = "#5a4a3a"
COL_TABLE = "#6a5640"
COL_WHEEL = "#4a3a2c"
DECK_HW = 2.6  # the deck's half width
DECK_BOW = -9.0
DECK_STERN = 9.0
# the courses (act3_ch18.md §4): id, its prompt's destination, where it stands (round the chart table and along the
# rails), the flag it waits on
COURSES = (("reedhollow", (-1.6, -3.2), "ch18_world_open"), ("hollowmere", (-1.6, -1.6), "ch18_world_open"),
           ("pemakar", (-1.6, 0.0), "ch18_world_open"), ("tamsule", (1.6, -3.2), "ch18_world_open"),
           ("corrow", (1.6, -1.6), "ch18_world_open"), ("quellan", (1.6, 0.0), "ch18_world_open"),
           ("ansedra", (0.0, -4.4), "ch18_world_open"), ("iskarra", (0.0, -7.6), "ch18_night_aboard"))


def kite() -> dict:
    length = DECK_STERN - DECK_BOW
    blocks = [box("Deck", 0.0, -0.25, 0.0, 2 * DECK_HW, 0.5, length, color=COL_DECK)]
    for side in (-1.0, 1.0):
        blocks.append(box(f"Rail{'WE'[side > 0]}", side * (DECK_HW + 0.1), 0.5, 0.0, 0.2, 1.0, length,
                          color=COL_RAIL))
    for end, z in (("Bow", DECK_BOW - 0.1), ("Stern", DECK_STERN + 0.1)):
        blocks.append(box(f"Rail{end}", 0.0, 0.5, z, 2 * DECK_HW + 0.4, 1.0, 0.2, color=COL_RAIL))
    blocks.append(box("ChartTable", 0.0, 0.45, -1.6, 1.6, 0.9, 2.4, color=COL_TABLE))
    blocks.append(box("Wheel", 0.0, 0.7, 6.4, 0.3, 1.4, 0.3, color=COL_WHEEL))
    blocks.append(box("Mast", 0.0, 4.0, 2.0, 0.3, 8.0, 0.3, color=COL_WHEEL))
    triggers = [{"id": "chart", "activation": "interact", "at": [0.0, 0.0, -0.1], "size": [1.4, 0, 0.8],
                 "prompt_key": "FIELD_PROMPT_LOOK", "requires_flag": "ch18_started",
                 "blocked_by_flag": "ch18_world_open", "payload": {"beat": "chart"}, "yaw": 0.0}]
    for cid, (x, z), flag in COURSES:
        triggers.append({"id": f"course_{cid}", "activation": "interact", "at": [x, 0.0, z], "size": [1.2, 0, 1.2],
                         "prompt_key": f"FIELD_PROMPT_CH18_COURSE_{cid.upper()}", "requires_flag": flag,
                         "payload": {"beat": f"course_{cid}"}, "yaw": 0.0})
    return {
        "doc": "M5-A3P-1004 greybox (tools/act3/ch18_greybox.py; do not edit by hand): Ch18's Kite, Dace's hull flying "
        "(act3_ch18.md). The deck (Deck) from the bow rail to the stern rail (stern_rail), the wheel aft (kite_wheel), "
        "the chart table amidships (chart_table: K02, where the world opens). Until the Kite world map exists, the "
        "courses stand round the table as interactables (course_*).",
        "sun": {"pitch_deg": -35.0, "yaw_deg": 120.0, "energy": 1.4, "color": "#fff4e6"},
        "environment": {"background": "#9cb8d4", "ambient_color": "#a8b8c8", "ambient_energy": 0.7},
        "block_color": COL_DECK,
        "blocks": blocks,
        "spawns": {"Deck": [0.0, 0.0, 3.0, 0.0], "ChartTable": [0.0, 0.0, 0.2, 0.0]},
        "marks": {"chart_table": [0.0, 0.0, -0.3, 0.0], "kite_wheel": [0.0, 0.0, 7.0, 0.0],
                  "stern_rail": [0.0, 0.0, 8.4, 180.0]},
        "actors": {},
        "shots": {"K01": {"pos": [3.8, 2.4, 9.5], "look_at": [0.0, 1.2, -4.0], "fov": 50}},
        "camera_volumes": [{"id": "Deck", "mode": "pan_follow", "at": [0.0, 1.5, 0.0],
                            "size": [2 * DECK_HW + 2.0, 4.0, r3(length + 2.0)], "pos": [0.0, 6.0, 12.0],
                            "look_at": [0.0, 0.5, -1.0], "fov": 55, "priority": 1}],
        "triggers": triggers,
    }


def main() -> None:
    write("ch18", "kite", kite())


if __name__ == "__main__":
    main()
