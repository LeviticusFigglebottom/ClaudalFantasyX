"""M2-FP-03: a root script with place_at counts as a player when Godot writes the script as a
property line under the node header (`script = ExtResource("..")`), as every saved .tscn does.
Run: python3 -m unittest discover -s tools/tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

ZONE_GD = "res://game/levels/zone.gd"
PLACE = "func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:\n\treturn true\n"
SCENE = f"""[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="{ZONE_GD}" id="1_root"]

[node name="Zone" type="Node3D"]
script = ExtResource("1_root")

[node name="Spawns" type="Node3D" parent="."]

[node name="Start" type="Marker3D" parent="Spawns"]
"""


class ScenePlaceAtPropertyTest(unittest.TestCase):
    def test_root_script_property_with_place_at_is_a_player(self) -> None:
        self.assertTrue(vd.scene_has_player(SCENE, {}, {ZONE_GD: PLACE}))

    def test_root_script_property_without_place_at_is_not(self) -> None:
        self.assertFalse(vd.scene_has_player(SCENE, {}, {ZONE_GD: "func _ready() -> void:\n\tpass\n"}))

    def test_a_child_script_does_not_count(self) -> None:
        child = SCENE.replace('[node name="Zone" type="Node3D"]\nscript = ExtResource("1_root")\n',
                              '[node name="Zone" type="Node3D"]\n\n[node name="Rig" type="Node3D" parent="."]\n'
                              'script = ExtResource("1_root")\n')
        self.assertFalse(vd.scene_has_player(child, {}, {ZONE_GD: PLACE}))

    def test_the_real_prologue_counts(self) -> None:
        path = "res://game/levels/prologue/prologue.tscn"
        text = (ROOT / path.removeprefix("res://")).read_text(encoding="utf-8")
        gd = "res://game/levels/prologue/prologue_scene.gd"
        scripts = {gd: (ROOT / gd.removeprefix("res://")).read_text(encoding="utf-8")}
        self.assertTrue(vd.scene_has_player(text, {}, scripts))


if __name__ == "__main__":
    unittest.main()
