#!/usr/bin/env python3
"""M5-A3P-1007 greybox: Ch19's `ch19/iskarra_spire` (act3_ch19.md I01-I10): drowned Iskarra's broken plaza at dusk
(the Prologue's frame: the Kite comes down, the vigil, the hitch, the words), the Lamp Spire's foot, its four tiers
climbed by switchback ramps (I06: the spire's fights; each tier sets ch19_spire_tier_<n>), the crown's antechamber
(the signatures) and the crown with its anchor-engine (the Wardens, the engine stops).

The spire stands on one ground floor at sea level (its first tier): a fall from a higher tier lands where the first
ramp starts, so nothing soft-locks. Writes game/levels/ch19/iskarra_spire/iskarra_spire_layout.json.
Usage: python3 tools/act3/ch19_greybox.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "act2"))
from ch10_greybox import box, r3  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402
from ch15_16_greybox import write  # noqa: E402

COL_STONE = "#9a948a"
COL_DROWNED = "#6e7c80"
COL_BRASS = "#a8884a"
COL_GATE = "#4a4440"
TIER_H = 6.0  # each tier's rise
TIER_HX = 6.0
TIER_HZ = 5.0
SOUTH_Z = -4.0  # the tiers over the ground (1, 3) and the antechamber
NORTH_Z = -26.0  # the tiers between (2, 4)
RAMP_X = 4.5
RAMP_W = 3.0
CROWN = (14.0, -4.0, 8.0, 5.0)  # centre x, z and half sizes, at the antechamber's height
GROUND = (-7.0, 23.0, 1.0, -32.0)  # x0, x1, z0, z1 of the spire's sea-level floor


def tier_y(n: int) -> float:
    return (n - 1) * TIER_H


def iskarra_spire() -> dict:
    gx0, gx1, gz0, gz1 = GROUND
    blocks = [floor("Plaza", 0.0, 22.0, 12.0, 7.0, 0.0, COL_DROWNED),
              floor("SpireFoot", 0.0, 7.5, 4.0, 7.5, 0.0, COL_STONE),
              floor("Ground", r3((gx0 + gx1) * 0.5), r3((gz0 + gz1) * 0.5), r3((gx1 - gx0) * 0.5),
                    r3((gz0 - gz1) * 0.5), 0.0, COL_STONE)]
    blocks += walls("Plaza", 0.0, 22.0, 12.0, 7.0, 0.0, 1.0, {"n": (-4.0, 4.0)})
    blocks += walls("Ground", r3((gx0 + gx1) * 0.5), r3((gz0 + gz1) * 0.5), r3((gx1 - gx0) * 0.5),
                    r3((gz0 - gz1) * 0.5), 0.0, 1.2, {"s": (-11.0, -3.0)})
    blocks.append(box("SpireGate", 0.0, 1.5, 3.0, 8.0, 3.0, 0.5, color=COL_GATE))
    for n, cz in ((2, NORTH_Z), (3, SOUTH_Z), (4, NORTH_Z)):
        blocks.append(floor(f"Tier{n}", 0.0, cz, TIER_HX, TIER_HZ, tier_y(n), COL_STONE))
    blocks.append(floor("Antechamber", 0.0, SOUTH_Z, TIER_HX, TIER_HZ, tier_y(5), COL_STONE))
    cx, cz, hx, hz = CROWN
    blocks.append(floor("Crown", cx, cz, hx, hz, tier_y(5), COL_STONE))
    blocks.append(box("AnchorEngine", 21.0, tier_y(5) + 1.5, cz, 1.6, 3.0, 4.0, color=COL_BRASS))
    ramps = []
    for n in range(1, 5):  # tier n up to tier n + 1 (5: the antechamber), switching sides
        up_north = n % 2 == 1
        x = RAMP_X if up_north else -RAMP_X
        z0, z1 = (SOUTH_Z - TIER_HZ, NORTH_Z + TIER_HZ) if up_north else (NORTH_Z + TIER_HZ, SOUTH_Z - TIER_HZ)
        ramps.append({"id": f"Flight{n}", "from": [x, tier_y(n), z0], "to": [x, tier_y(n + 1), z1],
                      "width": RAMP_W, "color": COL_STONE})
    tier_at = {1: SOUTH_Z, 2: NORTH_Z, 3: SOUTH_Z, 4: NORTH_Z}
    triggers = [
        # I03 (night): the hitch at the plaza's edge; I04 (optional): the words on the steps
        {"id": "hitch", "activation": "interact", "at": [-9.0, 0.0, 18.5], "size": [1.6, 0, 1.6],
         "prompt_key": "FIELD_PROMPT_LISTEN", "requires_flag": "ch19_vigil",
         "blocked_by_flag": "ch19_learned_the_hitch", "payload": {"beat": "hitch"}, "yaw": 0.0},
        {"id": "words", "activation": "interact", "at": [3.0, 0.0, 16.5], "size": [1.6, 0, 1.6],
         "prompt_key": "FIELD_PROMPT_LISTEN", "requires_flag": "ch19_learned_the_hitch",
         "blocked_by_flag": "ch19_words_whole", "payload": {"beat": "words"}, "yaw": 0.0}]
    for n, tz in tier_at.items():  # I06: each tier reached
        triggers.append({"id": f"tier_{n}", "activation": "touch", "at": [-2.0, tier_y(n), tz],
                         "size": [6.0, 0, 6.0], "once": True, "sets_flag": f"ch19_spire_tier_{n}",
                         "requires_flag": "ch19_learned_the_hitch", "payload": {}, "yaw": 0.0})
    # I07-I08: the signatures in the antechamber, then the Wardens on the crown
    triggers.append({"id": "signatures", "activation": "touch", "at": [3.0, tier_y(5), SOUTH_Z], "size": [2.0, 0, 8.0],
                     "requires_flag": "ch19_spire_tier_4", "blocked_by_flag": "ch19_abiding_beaten",
                     "payload": {"beat": "signatures"}, "yaw": 0.0})
    top = tier_y(5)
    return {
        "doc": "M5-A3P-1007 greybox (tools/act3/ch19_greybox.py; do not edit by hand): drowned Iskarra at dusk, the "
        "Prologue's broken plaza (Plaza; by_asha, the plaza's edge and steps: I01-I04), the Lamp Spire's foot (its "
        "gate open after the hitch), four tiers by switchback ramps (I06, the spire's fights), the antechamber (I07) "
        "and the crown with the anchor-engine (I08-I10).",
        "sun": {"pitch_deg": -8.0, "yaw_deg": 250.0, "energy": 0.7, "color": "#ffc89a"},
        "environment": {"background": "#5a6070", "ambient_color": "#7a8090", "ambient_energy": 0.55},
        "block_color": COL_STONE,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": {"Plaza": [0.0, 0.0, 26.0, 0.0], "SpireFoot": [0.0, 0.0, 6.0, 0.0],
                   "Antechamber": [-2.0, top, SOUTH_Z, 270.0], "Crown": [10.0, top, cz, 270.0]},
        "marks": {"by_asha": [2.0, 0.0, 21.0, 0.0], "plaza_edge": [-10.0, 0.0, 18.0, 90.0],
                  "plaza_edge_b": [-9.0, 0.0, 19.5, 90.0], "plaza_steps_b": [3.0, 0.0, 16.0, 0.0],
                  "duty_lectern": [-3.0, top, -6.0, 90.0], "hesper_oan": [16.0, top, cz, 90.0],
                  "engine_lever": [19.5, top, cz, 270.0]},
        "actors": {},
        "shots": {"I01": {"pos": [6.0, 3.0, 30.0], "look_at": [0.0, 6.0, -10.0], "fov": 50}},
        "camera_volumes": [
            {"id": "Plaza", "mode": "pan_follow", "at": [0.0, 1.5, 22.0], "size": [24.0, 4.0, 14.0],
             "pos": [0.0, 7.0, 32.0], "look_at": [0.0, 0.5, 18.0], "fov": 55, "priority": 1},
            {"id": "Crown", "mode": "pan_follow", "at": [cx, top + 1.5, cz], "size": [2 * hx, 4.0, 2 * hz],
             "pos": [cx - 6.0, top + 6.0, cz + 8.0], "look_at": [cx + 2.0, top + 0.5, cz], "fov": 55, "priority": 2}],
        "triggers": triggers,
        "variants": [{"when": {"set": ["ch19_learned_the_hitch"]}, "hide": ["SpireGate"]}],
        # I06: the spire's fights (act3_roster.md Ch19), once the night of the hitch is over
        "encounters": {"table": [{"encounter": "ch19_spire_wicks", "weight": 1},
                                 {"encounter": "ch19_spire_lamps", "weight": 1},
                                 {"encounter": "ch19_spire_moths", "weight": 1}],
                       "min_m": 95, "max_m": 145, "when": {"set": ["ch19_learned_the_hitch"]}, "seed": 19},
    }


def main() -> None:
    write("ch19", "iskarra_spire", iskarra_spire())


if __name__ == "__main__":
    main()
