#!/usr/bin/env python3
"""Ch18 "The Kite" greybox (M5-A3P-1004; act3_ch18.md §2 K01-K02, K07-K08, §4 Ansedra, §5 Ysolde's heirloom): ch18/kite,
Dace's hull flying. The deck is the whole walkable world, bow east: the wheel at the stern (`kite_wheel`), the chart table
amidships (`chart_table`: the world opens, then Kerrid's finger on Iskarra), the stern rail (`stern_rail`: Kerrid at night),
the bow rail (Ansedra from the air), the engine's lamps under the deck (`kite_lamps`: bound light, still), two masts and
their flare-kite sails. Nothing under the hull but sky; the flotilla's song comes up from below (`flotilla`).

x is east, north is -Z. Shares Ch10's and Ch11's builders.

    python3 tools/act3/ch18_kite_greybox.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "act1"))
from ch10_greybox import box  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "game" / "levels" / "ch18" / "kite" / "kite_layout.json"
DECK = (12.0, 0.0, 12.0, 4.0)  # centre x, z and half sizes: 24 m by 8 m, bow east
COL_DECK = "#6a5640"
COL_HULL = "#5a4636"
COL_BRASS = "#8a6a3a"
COL_SAIL = "#d8d0c0"


def kite() -> dict:
    cx, cz, hx, hz = DECK
    blocks = [floor("Deck", cx, cz, hx, hz, 0.0, COL_DECK)]
    blocks += walls("Deck", cx, cz, hx, hz, 0.0, 1.0, {})
    blocks.append(box("Hull", cx, -1.6, cz, 2 * hx + 0.6, 2.4, 2 * hz + 0.6, color=COL_BRASS, solid=False))
    blocks.append(box("Wheel", 2.0, 0.6, 0.0, 0.4, 1.2, 1.2, color=COL_HULL))
    blocks.append(box("ChartTable", 10.0, 0.45, 1.6, 2.2, 0.9, 1.2, color=COL_HULL))
    blocks.append(box("EngineHatch", 6.0, 0.1, -2.0, 2.0, 0.2, 1.6, color=COL_BRASS))
    for k, x in enumerate((8.0, 16.0)):
        blocks.append(box(f"Mast{k}", x, 4.5, 0.0, 0.3, 9.0, 0.3, color=COL_HULL))
        blocks.append(box(f"Sail{k}", x + 0.3, 6.0, 0.0, 0.1, 4.0, 7.0, color=COL_SAIL, solid=False))
    return {
        "doc": "M5-A3P-1004 greybox (tools/act3/ch18_kite_greybox.py; do not edit by hand): the Kite in flight, its deck "
        "the whole walkable world (act3_ch18.md §2): the wheel, the chart table, the stern and bow rails, the lamps "
        "under the deck, the masts and the flare-kite sails. Day; the night aboard (K07) is a variant.",
        "sun": {"pitch_deg": -45.0, "yaw_deg": 150.0, "energy": 1.1, "color": "#f6f0e2"},
        "environment": {"background": "#9ab8d0", "ambient_color": "#a8b8c8", "ambient_energy": 0.9},
        "block_color": COL_DECK,
        "blocks": blocks,
        "spawns": {"Deck": [12.0, 0.0, 0.0, 270.0]},
        "marks": {"kite_wheel": [2.8, 0.0, 0.0, 270.0], "chart_table": [10.0, 0.0, 2.8, 0.0],
                  "stern_rail": [0.9, 0.0, -2.0, 90.0], "bow_rail": [23.0, 0.0, 0.0, 270.0],
                  "kite_lamps": [6.0, -0.6, -2.0, 0.0], "sails": [12.0, 6.0, 0.0, 0.0],
                  "flotilla": [-30.0, -40.0, 10.0, 0.0], "iskarra": [10.0, 1.0, 1.6, 0.0],
                  "ansedra": [90.0, -60.0, -50.0, 0.0]},
        "actors": {},
        "shots": {
            "K01": {"pos": [26.0, 4.0, 8.0], "look_at": [10.0, 2.0, 0.0], "fov": 50},  # the hull lifts
            "K02": {"pos": [-10.0, -4.0, 12.0], "look_at": [8.0, 1.0, 0.0], "fov": 50},  # from below: the flotilla's song
            "K03": {"pos": [6.0, 2.0, -2.5], "look_at": [12.0, 6.0, 0.0], "fov": 45},  # Liss looks up at the sails
            "K04": {"pos": [12.5, 2.0, 4.2], "look_at": [10.0, 0.9, 1.6], "fov": 42},  # the chart table
            "K13": {"pos": [11.6, 1.8, 3.8], "look_at": [10.0, 0.9, 1.6], "fov": 32},  # Kerrid's finger on Iskarra
            "K14": {"pos": [4.0, 2.2, 3.0], "look_at": [0.9, 1.5, -2.0], "fov": 45},  # the stern at night
            "K22": {"pos": [21.0, 2.0, 2.5], "look_at": [90.0, -60.0, -50.0], "fov": 40},  # Ansedra from the air
            "K23": {"pos": [21.0, 2.0, 2.5], "look_at": [90.0, -60.0, -50.0], "fov": 10},  # Merel's window, close
        },
        "camera_volumes": [{"id": "Deck", "mode": "pan_follow", "at": [cx, 1.5, cz], "size": [2 * hx, 4.0, 2 * hz],
                            "pos": [cx, 7.0, 9.0], "look_at": [cx, 0.8, cz], "fov": 55, "priority": 1}],
        "triggers": [
            {"id": "ch18_chart", "activation": "interact", "at": [10.0, 0.0, 2.6], "size": [2.2, 0, 1.0],
             "prompt_key": "FIELD_PROMPT_CH18_CHART", "requires_flag": "ch18_started",
             "blocked_by_flag": "ch18_world_open", "payload": {"beat": "ch18_chart"}},
            {"id": "ch18_iskarra", "activation": "interact", "at": [10.0, 0.0, 2.6], "size": [2.2, 0, 1.0],
             "prompt_key": "FIELD_PROMPT_CH18_CHART", "requires_flag": "ch18_night_aboard",
             "blocked_by_flag": "ch18_complete", "payload": {"beat": "ch18_iskarra"}},
            {"id": "ch18_heirloom_ysolde", "activation": "interact", "at": [14.0, 0.0, -2.8], "size": [1.4, 0, 1.0],
             "prompt_key": "FIELD_PROMPT_LOOK", "requires_flag": "ch18_world_open",
             "blocked_by_flag": "ch18_heirloom_ysolde", "payload": {"dialogue": "ch18_heirloom_ysolde"}},
            {"id": "ch18_ansedra", "activation": "interact", "at": [22.6, 0.0, 0.0], "size": [1.0, 0, 3.0], "once": True,
             "prompt_key": "FIELD_PROMPT_LOOK", "requires_flag": "ch18_world_open",
             "payload": {"dialogue": "ch18_revisit_ansedra"}},
        ],
        # the night aboard (K07): from the farewell-tide until the night scene has played
        "variants": [{"when": {"set": ["ch18_learned_farewell_tide"], "unset": ["ch18_night_aboard"]},
                      "sun": {"pitch_deg": -30.0, "yaw_deg": 200.0, "energy": 0.12, "color": "#8090b0"},
                      "environment": {"background": "#0e1420", "ambient_color": "#2a3444", "ambient_energy": 0.35}}],
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(kite(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
