#!/usr/bin/env python3
"""Ch21 "The Heart" greybox (M5-A3P-1015; act3_ending.md H01-H09): ch21/heart, the story layer over env-art's Heart kit
(assets_src/environments/kits/haluna/undertow_heart.py): the floor of held light (heart_floor, r 11, flat at y 0), Imra's
column (heart_column, at (-9.5, -12)) and the eyewall round it all (heart_eyewall, r 160). The party comes in at the
floor's south edge (HeartEdge); the fights and Sefir are at its centre (Centre). Collision only under the kit; the
anchors the scenes name are marks (the Great Unbinding's lights rise round the eyewall). This writes the layout and
the zone scene.

x is east, north is -Z.

    python3 tools/act1/ch21_greybox.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import box  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch21" / "heart"
KIT = "res://assets/environments/kits/haluna/"
COLUMN = (-9.5, -12.0)
# H09's six cutaways and the storm wall, as lights rising round the eyewall (act3_ending §2 H09)
UNBINDING = ["iskarra_columns", "kite_lamps", "lowlight_conduits", "sanctum_basin", "storm_wall", "tamsule_bell",
             "tide_wheel"]


def layout() -> dict:
    marks = {"heart_floor": [0.0, 0.2, 0.0, 0.0], "two_lamps": [-1.0, 1.0, -1.0, 0.0],
             "arms_length": [-0.6, 0.0, 1.6, 0.0], "asha_sleeve": [-1.6, 1.3, 1.2, 0.0], "sleeve": [-1.6, 1.3, 1.2, 0.0],
             "kesh": [-3.0, 1.5, -5.0, 0.0], "lamp_key": [-2.6, 1.0, -4.6, 0.0], "sefir": [3.0, 1.5, -5.0, 0.0],
             "kesh_far": [COLUMN[0], 8.0, COLUMN[1], 0.0]}
    for k, a in enumerate(UNBINDING):
        ang = 2 * math.pi * k / len(UNBINDING)
        marks[a] = [round(60 * math.cos(ang), 3), 10.0, round(-60 * math.sin(ang) - 20, 3), 0.0]
    shots = {}
    frames = [((0, 3, 12), (0, 1, 0), 55), ((2, 1.7, 3), (-1, 1.2, -1), 35), ((-4, 2, 6), (0, 1.2, -2), 45),
              ((1.2, 1.6, 2.8), (-0.6, 1.5, 1.6), 32), ((-2.5, 1.6, 3.0), (-1.6, 1.4, 1.2), 32),
              ((0, 6, 14), (0, 1, -4), 50), ((6, 2, 4), (3, 1.5, -5), 40), ((-1, 1.8, 0), (-3, 1.5, -5), 35)]
    for n in range(1, 16):
        pos, look, fov = frames[(n - 1) % len(frames)]
        shots[f"HT{n:02d}"] = {"pos": list(pos), "look_at": list(look), "fov": fov}
    for n, a in zip(range(16, 23), UNBINDING):
        x, y, z, _ = marks[a]
        shots[f"HT{n:02d}"] = {"pos": [0.0, 4.0, 6.0], "look_at": [x, y, z], "fov": 40}
    return {
        "doc": "M5-A3P-1015 greybox (tools/act1/ch21_greybox.py; do not edit by hand): the Heart on env-art's Heart kit "
        "(heart_floor r 11, heart_column, heart_eyewall, instanced by the zone scene); collision only. The edge the party "
        "comes in at, the centre where Kesh and Sefir are fought, the two lamps, the anchors the scenes name, and H09's "
        "lights rising round the eyewall (cinematics may cut them to their own places).",
        "sun": {"pitch_deg": -80.0, "yaw_deg": 0.0, "energy": 0.4, "color": "#7fd0d8"},
        "environment": {"background": "#04101a", "ambient_color": "#2a5060", "ambient_energy": 0.5},
        "block_color": "#4a5058",
        "blocks": [box("HeartFloor", 0.0, -0.25, 0.0, 22.0, 0.5, 22.0, visible=False)],
        "spawns": {"HeartEdge": [0.0, 0.0, 9.0, 0.0], "Centre": [0.0, 0.0, 2.0, 0.0]},
        "marks": marks,
        "actors": {},
        "shots": shots,
        "camera_volumes": [],
        "triggers": [{"id": "ch21_kesh", "activation": "touch", "at": [0.0, 0.0, 2.5], "size": [6.0, 0, 1.0],
                      "requires_flag": "ch21_started", "blocked_by_flag": "ch21_kesh_fought",
                      "payload": {"beat": "ch21_kesh"}}],
    }


def scene() -> str:
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch21/ch21_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="90_cast"]']
    lines += [f'[ext_resource type="PackedScene" path="{KIT}{p}.glb" id="p_{p}"]'
              for p in ("heart_floor", "heart_column", "heart_eyewall")]
    lines += ["", '[node name="Heart" type="Node3D"]', 'script = ExtResource("1_zone")', 'location_id = &"ch21/heart"',
              'layout_path = "res://game/levels/ch21/heart/heart_layout.json"',
              'hold_field_path = "res://game/data/flow/act3_field.json"', "",
              '[node name="Floor" parent="." instance=ExtResource("p_heart_floor")]', "",
              '[node name="Column" parent="." instance=ExtResource("p_heart_column")]',
              f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {COLUMN[0]}, 0, {COLUMN[1]})", "",
              '[node name="Eyewall" parent="." instance=ExtResource("p_heart_eyewall")]', "",
              '[node name="Cast" type="Node" parent="."]', 'script = ExtResource("90_cast")']
    return "\n".join(lines) + "\n"


def main() -> None:
    ZONE.mkdir(parents=True, exist_ok=True)
    (ZONE / "heart_layout.json").write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "heart.tscn").write_text(scene(), encoding="utf-8")


if __name__ == "__main__":
    main()
