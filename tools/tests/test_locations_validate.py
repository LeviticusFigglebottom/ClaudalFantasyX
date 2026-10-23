"""Location registry and party rest checks in tools/validate_data.py (M1-ARC-06).
Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

ZONE = "res://game/levels/zone.tscn"
ZONE_TEXT = """[gd_scene format=3]

[ext_resource type="PackedScene" path="res://game/world/save_shrine/save_shrine.tscn" id="7_shrine"]

[node name="Zone" type="Node3D"]

[node name="Spawns" type="Node3D" parent="."]

[node name="Gate" type="Marker3D" parent="Spawns"]

[node name="Shrine" type="Marker3D" parent="Spawns" unique_id=1]

[node name="Deep" type="Marker3D" parent="Spawns/Gate"]

[node name="Player" type="CharacterBody3D" parent="."]

[node name="SaveShrine" parent="." instance=ExtResource("7_shrine")]
id = &"zone_shrine"
location_id = &"zone"
network_id = &"zone_shrine"
"""
DOC = {
    "default_location": "zone",
    "new_game": {"location_id": "zone", "spawn": "Gate"},
    "locations": [{"id": "zone", "scene": ZONE, "spawn": "Shrine", "name_key": "LOCATION_ZONE"}],
    "shrines": [{"id": "zone_shrine", "location_id": "zone", "spawn": "Shrine"}],
}
REST = {"carried_statuses": ["poison", "zombie"], "carried_duration": -1, "shrine_cures": ["poison"]}
STATUSES = {"poison", "zombie", "sleep"}


def errors(doc=None, rest=None, text=ZONE_TEXT, loc=None):
    doc = copy.deepcopy(DOC) if doc is None else doc
    rest = copy.deepcopy(REST) if rest is None else rest
    scenes = {ZONE: text} if text is not None else {}
    shrines = {"game/levels/zone.tscn": vd.shrine_instances(text)} if text is not None else {}
    return vd.locations_errors(doc, scenes, {"LOCATION_ZONE"} if loc is None else loc, STATUSES, rest, shrines)


class LocationValidatorTests(unittest.TestCase):
    def test_valid_registry_passes(self) -> None:
        self.assertEqual(errors(), [])

    def test_repo_registry_passes(self) -> None:
        rep = vd.Report()
        files = vd.load_json_files(ROOT, rep)
        vd.check_locations(ROOT, files, rep)
        self.assertEqual(rep.errors, [])

    def test_spawns_are_direct_children_of_spawns(self) -> None:
        self.assertEqual(vd.scene_spawns(ZONE_TEXT), {"Gate", "Shrine"})

    def test_shrine_instances_are_found(self) -> None:
        self.assertEqual(vd.shrine_instances(ZONE_TEXT),
                         [{"node": "SaveShrine", "location_id": "zone", "network_id": "zone_shrine"}])
        self.assertEqual(vd.shrine_instances("[gd_scene format=3]\n"), [])

    def test_missing_scene(self) -> None:
        self.assertTrue(any("does not exist" in e for e in errors(text=None)))

    def test_missing_spawn_and_name_key(self) -> None:
        doc = copy.deepcopy(DOC)
        doc["locations"][0]["spawn"] = "Deep"
        errs = errors(doc=doc, loc=set())
        self.assertTrue(any("spawn 'Deep'" in e for e in errs), errs)
        self.assertTrue(any("name_key 'LOCATION_ZONE'" in e for e in errs), errs)

    def test_default_new_game_and_shrine_rows_must_resolve(self) -> None:
        doc = copy.deepcopy(DOC)
        doc["default_location"] = "nowhere"
        doc["new_game"] = {"location_id": "zone", "spawn": "Attic"}
        doc["shrines"].append({"id": "zone_shrine", "location_id": "elsewhere"})
        errs = errors(doc=doc)
        self.assertTrue(any("default_location: unknown location 'nowhere'" in e for e in errs), errs)
        self.assertTrue(any("new_game: spawn 'Attic'" in e for e in errs), errs)
        self.assertTrue(any("duplicate shrine id" in e for e in errs), errs)
        self.assertTrue(any("unknown location 'elsewhere'" in e for e in errs), errs)

    def test_shrine_instances_must_resolve(self) -> None:
        text = ZONE_TEXT.replace('location_id = &"zone"', 'location_id = &"ch09/void"').replace(
            'network_id = &"zone_shrine"', 'network_id = &"lost"')
        errs = errors(text=text)
        self.assertTrue(any("location_id 'ch09/void' is not in" in e for e in errs), errs)
        self.assertTrue(any("network_id 'lost' has no 'shrines' row" in e for e in errs), errs)

    def test_rest_rules(self) -> None:
        errs = errors(rest={"carried_statuses": ["poison", "gloom"], "carried_duration": "x",
                            "shrine_cures": ["sleep"]})
        self.assertTrue(any("unknown status 'gloom'" in e for e in errs), errs)
        self.assertTrue(any("shrine cure 'sleep' is never carried" in e for e in errs), errs)
        self.assertTrue(any("carried_duration" in e for e in errs), errs)
        self.assertTrue(any("must be an object" in e for e in errors(rest=[])))
        self.assertTrue(any("must be a list" in e for e in errors(rest={"carried_duration": -1})))

    def test_shape_errors(self) -> None:
        self.assertEqual(errors(doc=[]), [f"{vd.LOCATIONS_FILE}: must be an object"])
        errs = errors(doc={"locations": [{"scene": ZONE}, "row"], "shrines": [{}]})
        self.assertTrue(any("needs a string id" in e for e in errs), errs)
        self.assertTrue(any("at least one location" in e for e in errs), errs)
        doc = copy.deepcopy(DOC)
        doc["locations"].append(copy.deepcopy(doc["locations"][0]))
        self.assertTrue(any("duplicate location id" in e for e in errors(doc=doc)))

    def test_scene_has_player(self) -> None:
        self.assertTrue(vd.scene_has_player(ZONE_TEXT))
        no_player = ZONE_TEXT.replace('[node name="Player" type="CharacterBody3D" parent="."]\n', "")
        self.assertFalse(vd.scene_has_player(no_player))
        self.assertFalse(vd.scene_has_player(no_player + '[node name="Player" type="Node3D" parent="Deep"]\n'),
                         "a Player deeper than the root's children is not found by place_player")
        grouped = no_player + '[node name="Hero" type="Node3D" parent="Rig" groups=["actors", "player"]]\n'
        self.assertTrue(vd.scene_has_player(grouped))

    def test_scene_has_player_sees_instanced_players(self) -> None:
        """M1-ARC-12 (review-sweep-H nit): a player inside an instanced sub-scene, an inherited scene,
        and a zone that places its own player (place_at) are not false errors."""
        no_player = ZONE_TEXT.replace('[node name="Player" type="CharacterBody3D" parent="."]\n', "")
        rig = "res://game/actors/rig.tscn"
        hero = "res://game/actors/hero.tscn"
        scenes = {
            hero: '[gd_scene format=3]\n\n[node name="Hero" type="CharacterBody3D" groups=["player"]]\n',
            rig: (f'[gd_scene format=3]\n\n[ext_resource type="PackedScene" path="{hero}" id="1_h"]\n\n'
                  '[node name="Rig" type="Node3D"]\n\n[node name="Body" parent="." instance=ExtResource("1_h")]\n'),
        }
        nested = no_player.replace('[node name="Zone" type="Node3D"]',
                                   f'[ext_resource type="PackedScene" path="{rig}" id="9_rig"]\n\n'
                                   '[node name="Zone" type="Node3D"]\n\n'
                                   '[node name="Party" parent="." instance=ExtResource("9_rig")]')
        self.assertFalse(vd.scene_has_player(nested), "without the scene map the rule stays conservative")
        self.assertTrue(vd.scene_has_player(nested, scenes), "group player two instances deep")
        scenes[hero] = scenes[hero].replace(' groups=["player"]', "")
        self.assertFalse(vd.scene_has_player(nested, scenes), "an instanced scene with no player")
        base = "res://game/levels/base_zone.tscn"
        inherited = (f'[gd_scene format=3]\n\n[ext_resource type="PackedScene" path="{base}" id="1_b"]\n\n'
                     '[node name="Zone2" instance=ExtResource("1_b")]\n')
        self.assertTrue(vd.scene_has_player(inherited, {base: ZONE_TEXT}), "the base scene's Player")
        self.assertFalse(vd.scene_has_player(inherited, {base: no_player}))
        zone_gd = "res://game/levels/zone.gd"
        scripted = no_player.replace(
            '[node name="Zone" type="Node3D"]',
            f'[ext_resource type="Script" path="{zone_gd}" id="2_s"]\n\n'
            '[node name="Zone" type="Node3D" script=ExtResource("2_s")]')
        place = "func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:\n\treturn true\n"
        self.assertTrue(vd.scene_has_player(scripted, {}, {zone_gd: place}), "the zone places its own player")
        self.assertFalse(vd.scene_has_player(scripted, {}, {zone_gd: "func _ready() -> void:\n\tpass\n"}))
        loop = {base: inherited.replace(base, base)}
        self.assertFalse(vd.scene_has_player(inherited, loop), "a self-instancing scene ends")

    def test_a_scene_with_no_player_must_be_marked_not_playable(self) -> None:
        """M1-ARC-11 (review-sweep-G S1 on M1-ENV-04): Continue into a player-less scene strands
        the player, so the row must say so, and the fallbacks must be playable."""
        no_player = ZONE_TEXT.replace('[node name="Player" type="CharacterBody3D" parent="."]\n', "")
        errs = errors(text=no_player)
        self.assertTrue(any("has no player" in e for e in errs), errs)
        doc = copy.deepcopy(DOC)
        doc["locations"].append({"id": "mood", "scene": ZONE, "spawn": "Gate", "name_key": "LOCATION_ZONE",
                                 "playable": False})
        self.assertEqual(errors(doc=doc), [])
        doc["locations"][1]["playable"] = "no"
        self.assertTrue(any("'playable' must be true or false" in e for e in errors(doc=doc)))
        doc["locations"][1]["playable"] = False
        doc["default_location"] = "mood"
        doc["new_game"] = {"location_id": "mood", "spawn": "Gate"}
        errs = errors(doc=doc)
        self.assertTrue(any("default_location: location 'mood' is not playable" in e for e in errs), errs)
        self.assertTrue(any("new_game: location 'mood' is not playable" in e for e in errs), errs)

    def test_repo_data_files_parse(self) -> None:
        for rel in (vd.LOCATIONS_FILE, vd.PARTY_REST_FILE):
            self.assertIsInstance(json.loads((ROOT / rel).read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
