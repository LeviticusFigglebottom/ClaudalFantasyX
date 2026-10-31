#!/usr/bin/env python3
"""M5-A3P-1015 greybox: Ch21's `ch21/heart` (act3_ending.md H01-H09, R1): the bottom of the well, the Undertow's heart.
The last layer's walk in (H01), the heart's floor round the two close lamps (Imra and Dace, drawn as light: H02), the
Kite come to rest at the floor's edge, the dark Choir-stone where the party rests and saves (R1), and the battle floor
where Kesh and Sefir are fought (H03-H07) and the Great Unbinding (H09) is played.

The floor is walled; the lamps stand in a ring the party can't enter (arm's length). Writes
game/levels/ch21/heart/heart_layout.json.
Usage: python3 tools/act3/ch21_greybox.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "act2"))
from ch10_greybox import box, r3  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402
from ch15_16_greybox import write  # noqa: E402

COL_DARK = "#1e2a34"
COL_FLOOR = "#2c3a46"
COL_STONE = "#3a3a44"
COL_KITE = "#7a5a3a"
GLOW_HELD = "#7fdcff"
GLOW_WARM = "#ffd9a0"
WALK_HZ = 9.0  # the last layer's half length, along z
WALK_HX = 2.5
HEART = (0.0, -22.0, 12.0, 12.0)  # the heart floor's centre x, z and half sizes
LAMP_R = 2.4  # the ring round the two lamps (the party stops at arm's length)
WALL_H = 1.2
# (shot ids, the camera's offset from the heart's centre, its look-at offset, fov): HT01-HT02 on the walk in, the
# rest round the heart
WALK_SHOTS = ["HT01", "HT02"]
HEART_SHOTS = [f"HT{n:02d}" for n in range(3, 23)]


def heart() -> dict:
    cx, cz, hx, hz = HEART
    wz = cz + hz + WALK_HZ  # the walk's centre, running south from the heart
    blocks = [floor("LastLayer", 0.0, wz, WALK_HX, WALK_HZ, 0.0, COL_FLOOR),
              floor("HeartFloor", cx, cz, hx, hz, 0.0, COL_FLOOR)]
    blocks += walls("LastLayer", 0.0, wz, WALK_HX, WALK_HZ, 0.0, WALL_H, {"n": (-WALK_HX, WALK_HX)})
    blocks += walls("HeartFloor", cx, cz, hx, hz, 0.0, WALL_H, {"s": (-WALK_HX, WALK_HX)})
    # the two lamps (light columns, no figures) inside a low ring nobody crosses
    for side, name, glow in ((-1.0, "ImraLamp", GLOW_HELD), (1.0, "DaceLamp", GLOW_WARM)):
        blocks.append(box(name, side * 0.8, 3.0, cz, 0.5, 6.0, 0.5, color=glow, emission=glow, emission_energy=1.2,
                          solid=False))
    blocks.append(box("LampRing", 0.0, 0.2, cz, 2 * LAMP_R, 0.4, 2 * LAMP_R, color=COL_STONE))
    blocks.append(box("ChoirStone", -8.0, 0.6, cz + 8.0, 1.6, 1.2, 1.0, color=COL_STONE))
    blocks.append(box("KiteHull", 8.5, 0.9, cz + 7.0, 3.0, 1.8, 7.0, color=COL_KITE))
    shots = {}
    for k, sid in enumerate(WALK_SHOTS):
        shots[sid] = {"pos": [r3(1.8 - 3.6 * k), 2.2, r3(wz + WALK_HZ - 1.0)], "look_at": [0.0, 1.2, r3(cz)], "fov": 50}
    for k, sid in enumerate(HEART_SHOTS):  # round the lamps, every 18 degrees from the south, outside the ring
        a = math.radians(18.0 * k)
        d = 6.0 + (k % 3) * 1.5
        shots[sid] = {"pos": [r3(math.sin(a) * d), r3(1.6 + (k % 2) * 1.2), r3(cz + math.cos(a) * d)],
                      "look_at": [0.0, 1.4, r3(cz)], "fov": 45 if k % 2 else 55}
    marks = {
        "arms_length": [0.0, 0.0, r3(cz + LAMP_R + 0.6), 180.0], "two_lamps": [0.0, 0.0, r3(cz), 0.0],
        "imra": [-0.8, 0.0, r3(cz), 0.0], "dace": [0.8, 0.0, r3(cz), 0.0], "heart_floor": [0.0, 0.0, r3(cz + 5.0), 0.0],
        "sefir": [0.0, 0.0, r3(cz - LAMP_R - 1.5), 0.0], "kesh": [-4.0, 0.0, r3(cz - 4.0), 0.0],
        "kesh_far": [-7.0, 0.0, r3(cz - 9.0), 0.0], "lamp_key": [-4.0, 1.2, r3(cz - 4.0), 0.0],
        "asha_sleeve": [-1.0, 0.0, r3(cz + 5.0), 0.0], "kite_lamps": [8.5, 1.8, r3(cz + 7.0), 0.0],
        "choir_stone": [-8.0, 0.0, r3(cz + 9.2), 0.0], "storm_wall": [0.0, 6.0, r3(cz - hz), 0.0],
    }
    triggers = [
        # H02: at the heart's mouth, the two lamps; Kesh is called after (H03)
        {"id": "two_lamps", "activation": "touch", "at": [0.0, 0.0, r3(cz + hz - 2.0)], "size": [2 * WALK_HX, 0, 3.0],
         "requires_flag": "ch21_started", "blocked_by_flag": "ch21_kesh_beaten", "payload": {"beat": "two_lamps"},
         "yaw": 0.0},
        # R1: the dark Choir-stone saves; the flow starts the Warden when the party steps onto the battle floor
        {"id": "choir_stone", "activation": "interact", "at": [-8.0, 0.0, r3(cz + 9.2)], "size": [1.6, 0, 1.2],
         "prompt_key": "FIELD_PROMPT_REST", "requires_flag": "ch21_kesh_released", "blocked_by_flag": "ch21_unbound",
         "payload": {"save_shrine": "heart_choir_stone"}, "yaw": 0.0},
        {"id": "the_warden", "activation": "touch", "at": [0.0, 0.0, r3(cz + LAMP_R + 2.0)], "size": [8.0, 0, 2.0],
         "requires_flag": "ch21_kesh_released", "blocked_by_flag": "ch21_warden_beaten",
         "payload": {"beat": "the_warden"}, "yaw": 0.0},
    ]
    return {
        "doc": "M5-A3P-1015 greybox (tools/act3/ch21_greybox.py; do not edit by hand): the Undertow's heart. The last "
        "layer's walk (LastLayer, H01), the heart's floor (HeartFloor) round the two close lamps (ImraLamp, DaceLamp: "
        "light, no figures, inside LampRing; arms_length where Rhen stops), the Kite at rest (KiteHull, kite_lamps), "
        "the dark Choir-stone (ChoirStone: R1, the save) and the battle floor before the lamps (H03-H09).",
        "sun": {"pitch_deg": -85.0, "yaw_deg": 0.0, "energy": 0.2, "color": "#9fe8f0"},
        "environment": {"background": "#020a12", "ambient_color": "#1a3a4a", "ambient_energy": 0.5},
        "block_color": COL_FLOOR,
        "blocks": blocks,
        "spawns": {"LastLayer": [0.0, 0.0, r3(wz + WALK_HZ - 1.5), 180.0],
                   "HeartFloor": [0.0, 0.0, r3(cz + 6.0), 180.0],
                   "ChoirStone": [-8.0, 0.0, r3(cz + 10.5), 180.0]},
        "marks": marks,
        "actors": {},
        "shots": shots,
        "camera_volumes": [],
        "triggers": triggers,
    }


def main() -> None:
    write("ch21", "heart", heart())


if __name__ == "__main__":
    main()
