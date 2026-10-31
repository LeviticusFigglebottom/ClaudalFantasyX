#!/usr/bin/env python3
"""Ch19 "Iskarra" greybox (M5-A3P-1007; act3_ch19.md §2 I01-I10): the story layer over env-art's Iskarra kit.

  ch19/iskarra        the Prologue's plaza at dusk (assets/environments/zones/iskarra/iskarra_city.tscn, the scene the
                      Prologue stands in): collision only, under the kit (the plaza floor, the steps, the edge), the
                      Kite set on the water beside it (I01), the seven Prologue places (the vigil, I02: P01 and P02 are
                      the Prologue's own shots, copied), the plaza's edge at night (the hitch, I03), the steps (the
                      words, I04), and the spire's door (to the crown).
  ch19/iskarra_spire  the Lamp Spire's crown (env-art's spire_crown_floor, r 12, and anchor_engine at its centre) with
                      the antechamber south of it (a greybox room: the duty lectern, I05-I06), the engine lever (I07),
                      where the Wardens lie (I08), and the crown's edge facing the sea (the eye, I09).

x is east, north is -Z. Shares Ch10's and Ch11's builders.

    python3 tools/act1/ch19_greybox.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import box  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ROOT / "game" / "levels" / "ch19"
COL_STONE = "#c8bca4"
DUSK_SUN = {"pitch_deg": -12.0, "yaw_deg": 160.0, "energy": 2.2, "color": "#ff9f46"}  # the Prologue's sun
DUSK_ENV = {"background": "#e0a060", "ambient_color": "#a08070", "ambient_energy": 0.7}
NIGHT = {"sun": {"pitch_deg": -30.0, "yaw_deg": 200.0, "energy": 0.15, "color": "#8090b0"},
         "environment": {"background": "#101828", "ambient_color": "#2a3444", "ambient_energy": 0.35}}
MORNING = {"sun": {"pitch_deg": -25.0, "yaw_deg": 100.0, "energy": 1.4, "color": "#f6ead2"},
           "environment": {"background": "#c8d0d4", "ambient_color": "#a8b0b4", "ambient_energy": 0.8}}


def _hidden(row: dict) -> dict:
    row["visible"] = False
    return row


def plaza() -> dict:
    blocks = [_hidden(floor("Plaza", 0.0, 4.0, 16.0, 12.0, 0.0)),  # x -16..16, z -8..16: the broken plaza
              _hidden(floor("Steps", -3.0, -10.0, 6.0, 2.0, 0.5)),  # the steps up to the spire's door
              _hidden(floor("Landing", 0.0, -14.0, 4.0, 2.0, 1.0))]
    blocks += [_hidden(b) for b in walls("Plaza", 0.0, 4.0, 16.0, 12.0, 0.0, 1.2, {"n": (-10.0, 4.0)})]
    return {
        "doc": "M5-A3P-1007 greybox (tools/act1/ch19_greybox.py; do not edit by hand): the Prologue's plaza on "
        "env-art's Iskarra kit; collision only (the kit is the look). The Kite on the water (kite_lamps), the seven "
        "Prologue places (vigil_*), P01 and P02 (the Prologue's own shots), the plaza's edge (the hitch), the steps (the "
        "words), the spire's door (to_spire). Dusk; the night of the hitch and the morning after are variants.",
        "sun": DUSK_SUN,
        "environment": DUSK_ENV,
        "block_color": COL_STONE,
        "blocks": blocks,
        "spawns": {"Landing": [6.0, 0.0, 12.0, 0.0], "SpireDoor": [0.0, 1.0, -13.0, 180.0]},
        "marks": {"kite_lamps": [8.0, 1.0, 24.0, 0.0], "plaza_steps": [-3.0, 0.5, -9.5, 0.0],
                  "vigil_kerrid": [9.5, 0.0, -5.5, 0.0], "vigil_pell": [-12.0, 0.0, 1.5, 270.0],
                  "vigil_liss": [4.5, 0.0, -6.5, 0.0], "vigil_ysolde": [-12.0, 0.0, 3.5, 90.0],
                  "vigil_toma": [7.5, 0.0, 1.0, 90.0], "vigil_asha": [-3.2, 0.0, -3.0, 165.0],
                  "by_asha": [-2.0, 0.0, -2.2, 315.0], "plaza_edge": [12.0, 0.0, 6.0, 270.0],
                  "plaza_edge_b": [10.6, 0.0, 6.6, 270.0], "plaza_steps_b": [-4.4, 0.5, -9.0, 0.0]},
        "actors": {},
        "shots": {"I01": {"pos": [6.0, 6.0, 30.0], "look_at": [-2.0, 2.0, 8.0], "fov": 50},  # the Kite comes down
                  "I02": {"pos": [3.0, 2.0, 14.0], "look_at": [-3.0, 1.0, -9.5], "fov": 45},  # the steps
                  "P01": {"pos": [1.5, 3.4, 21.0], "look_at": [-4.0, 7.5, -40.0]},  # the Prologue's (prologue.tscn)
                  "P02": {"pos": [-0.3, 2.4, 1.6], "look_at": [-2.8, 2.0, -2.8]},
                  "I03": {"pos": [8.5, 1.4, 9.5], "look_at": [11.3, 0.8, 6.3], "fov": 38},  # the hitch, at night
                  "I04": {"pos": [-1.0, 1.8, -5.5], "look_at": [-3.8, 1.2, -9.2], "fov": 40}},  # the words
        "camera_volumes": [{"id": "Plaza", "mode": "pan_follow", "at": [0.0, 1.5, 4.0], "size": [32.0, 4.0, 24.0],
                            "pos": [0.0, 7.0, 20.0], "look_at": [0.0, 0.8, 0.0], "fov": 55, "priority": 1}],
        "triggers": [
            {"id": "ch19_vigil", "activation": "touch", "at": [-2.0, 0.0, -2.2], "size": [3.0, 0, 2.0],
             "requires_flag": "ch19_started", "blocked_by_flag": "ch19_vigil", "payload": {"beat": "ch19_vigil"}},
            {"id": "ch19_hitch", "activation": "interact", "at": [11.3, 0.0, 6.3], "size": [1.6, 0, 1.6],
             "prompt_key": "FIELD_PROMPT_CH19_SIT", "requires_flag": "ch19_vigil",
             "blocked_by_flag": "ch19_learned_the_hitch", "payload": {"beat": "ch19_hitch"}},
            {"id": "ch19_words", "activation": "interact", "at": [-4.4, 0.5, -8.4], "size": [1.6, 0, 1.2],
             "prompt_key": "FIELD_PROMPT_LISTEN", "requires_flag": "ch19_learned_the_hitch",
             "blocked_by_flag": "ch19_words_whole", "payload": {"beat": "ch19_words"}},
            {"id": "ch19_to_spire", "activation": "touch", "at": [0.0, 1.0, -15.0], "size": [4.0, 0, 1.0],
             "requires_flag": "ch19_learned_the_hitch", "blocked_by_flag": "ch19_complete",
             "payload": {"beat": "ch19_to_spire"}},
        ],
        "variants": [{"when": {"set": ["ch19_vigil"], "unset": ["ch19_learned_the_hitch"]}, **NIGHT},
                     {"when": {"set": ["ch19_learned_the_hitch"]}, **MORNING}],
    }


def spire() -> dict:
    blocks = [_hidden(floor("Crown", 0.0, 0.0, 12.0, 12.0, 0.0)),
              floor("Antechamber", 0.0, 17.0, 4.0, 4.0, 0.0, COL_STONE)]
    blocks += [_hidden(b) for b in walls("Crown", 0.0, 0.0, 12.0, 12.0, 0.0, 1.2, {"s": (-2.0, 2.0)})]
    blocks += walls("Antechamber", 0.0, 17.0, 4.0, 4.0, 0.0, 3.0, {"n": (-1.2, 1.2)})
    blocks.append(box("DutyLectern", 0.0, 0.55, 16.0, 1.0, 1.1, 0.6, color="#7a6a50"))
    return {
        "doc": "M5-A3P-1007 greybox (tools/act1/ch19_greybox.py; do not edit by hand): the Lamp Spire's crown on "
        "env-art's spire_crown_floor (r 12) with the anchor_engine at its centre (collision only), and the antechamber "
        "south of it, a greybox room with the duty lectern (the signatures). The Wardens' fight is the encounter "
        "ch19_abiding_wardens (combat, M5-A3P-1009); the engine lever, where they lie, the crown's edge facing the sea.",
        "sun": MORNING["sun"],
        "environment": MORNING["environment"],
        "block_color": COL_STONE,
        "blocks": blocks,
        "spawns": {"Antechamber": [0.0, 0.0, 20.0, 0.0]},
        "marks": {"duty_lectern": [0.0, 0.0, 16.8, 0.0], "engine_lever": [0.0, 0.0, 3.5, 0.0],
                  "hesper_oan": [-3.0, 0.0, -4.0, 90.0], "wardens": [-2.6, 0.3, -4.2, 0.0],
                  "sea": [0.0, 0.0, -80.0, 0.0]},
        "actors": {},
        "shots": {"I05": {"pos": [3.0, 2.0, 20.5], "look_at": [0.0, 1.0, 16.2], "fov": 45},  # the antechamber
                  "I06": {"pos": [1.2, 1.6, 15.2], "look_at": [0.0, 1.0, 16.0], "fov": 30},  # the two hands
                  "I07": {"pos": [3.5, 2.0, 6.0], "look_at": [0.0, 1.2, 2.0], "fov": 42},  # the lever
                  "I08": {"pos": [-0.6, 1.8, -1.2], "look_at": [-3.0, 0.3, -4.0], "fov": 40},  # where they lie
                  "I09": {"pos": [0.0, 2.0, -10.0], "look_at": [0.0, 1.0, -60.0], "fov": 50}},  # the eye opens
        "camera_volumes": [{"id": "Crown", "mode": "pan_follow", "at": [0.0, 1.5, 0.0], "size": [24.0, 4.0, 24.0],
                            "pos": [0.0, 9.0, 16.0], "look_at": [0.0, 0.8, 0.0], "fov": 55, "priority": 1}],
        "triggers": [
            {"id": "ch19_engine", "activation": "interact", "at": [0.0, 0.0, 3.0], "size": [1.6, 0, 1.2],
             "prompt_key": "FIELD_PROMPT_CH19_ENGINE", "requires_flag": "ch19_abiding_beaten",
             "blocked_by_flag": "ch19_engine_stopped", "payload": {"beat": "ch19_engine"}},
        ],
    }


def main() -> None:
    for name, layout in (("iskarra", plaza()), ("iskarra_spire", spire())):
        out = LEVELS / name / f"{name}_layout.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
