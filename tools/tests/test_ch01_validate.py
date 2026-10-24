"""M3-C01-02: validate_data checks an encounter's "party_skills" (the skills a tutorial fight lends,
ADR 0034): a {hero id: [skill ids]} object naming real heroes and skills. Runs on the repo's real
battle tables with one encounter row changed. And a chapter's zone root that extends GreyboxZone
(Ch01Zone and its subclasses) counts as a greybox zone: its spawns come from its layout, and it
places the player with the place_at it inherits.
Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import chapter_flow_check as cf  # noqa: E402
import validate_data as vd  # noqa: E402

ENCOUNTERS = "game/data/battle/encounters.json"


def _errors(party_skills: object) -> list[str]:
    rep = vd.Report()
    files = vd.load_json_files(ROOT, rep)
    files = dict(files)
    enc = copy.deepcopy(files[ENCOUNTERS])
    for row in enc["encounters"]:
        if row["id"] == "ch01_hullgnaw":
            row["party_skills"] = party_skills
    files[ENCOUNTERS] = enc
    out = vd.Report()
    vd.check_battle(files, out)
    return [e for e in out.errors if "party_skills" in e]


class PartySkillsTest(unittest.TestCase):
    def test_the_shipped_lend_is_clean(self) -> None:
        self.assertEqual(_errors({"rhen": ["kick_off"]}), [])

    def test_unknown_hero_and_skill_are_errors(self) -> None:
        errs = _errors({"nobody": ["kick_off"], "rhen": ["no_such_skill"]})
        self.assertTrue(any("unknown hero 'nobody'" in e for e in errs), errs)
        self.assertTrue(any("unknown skill 'no_such_skill'" in e for e in errs), errs)

    def test_a_list_is_not_the_shape(self) -> None:
        self.assertTrue(_errors(["kick_off"]))


class GreyboxSubclassTest(unittest.TestCase):
    SCENES = {
        "game/levels/ch01/oruvel_underway/oruvel_underway.tscn": "Drop",
        "game/levels/ch01/oruvel/oruvel.tscn": "ScaleHull",
    }

    def test_a_subclassed_zone_reads_its_spawns_from_its_layout(self) -> None:
        for rel, spawn in self.SCENES.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertTrue(cf.greybox_layout_path(text, ROOT).endswith("_layout.json"), rel)
            self.assertIn(spawn, vd.scene_spawns(text), rel)

    def test_a_subclassed_zone_places_its_player(self) -> None:
        scripts = {"res://" + p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
                   for p in (ROOT / "game").rglob("*.gd")}
        for rel in self.SCENES:
            self.assertTrue(vd.scene_has_player((ROOT / rel).read_text(encoding="utf-8"), {}, scripts), rel)

    def test_a_scene_with_a_layout_but_no_zone_root_is_not_a_zone(self) -> None:
        text = '[gd_scene format=3]\n\n[ext_resource type="Script" path="res://nowhere.gd" id="1"]\n\n' \
               '[node name="X" type="Node3D"]\nscript = ExtResource("1")\nlayout_path = "res://a.json"\n'
        self.assertIsNone(cf.greybox_layout_path(text, ROOT))


class Ch01ChapterTest(unittest.TestCase):
    def test_the_shipped_chapter_and_its_layouts_are_clean(self) -> None:
        files = vd.load_json_files(ROOT, vd.Report())
        self.assertIn("res://game/data/flow/chapters/ch01.json", files["game/data/flow/chapters.json"]["chapters"]["files"])
        self.assertEqual(cf.check(ROOT, files, vd.declared_flags_quiet(ROOT)), [])

    def test_a_battle_step_may_name_its_own_party(self) -> None:
        ctx = cf.Context(flags={"won"}, dialogue=set(), encounters={"fight"}, heroes={"rhen"},
                         locations={"z": "res://z.tscn"}, layouts={"z": {"spawns": {"S": [0, 0, 0]}}},
                         scene_exists=lambda _r: True)
        doc = {"zones": {"z": {"beats": {"b": {"steps": [
            {"battle": "fight", "party": ["rhen"], "reserve": [], "return_spawn": "S", "victory_flag": "won"}]}}}}}
        self.assertEqual(cf.chapter_errors(doc, "c", ctx), [])
        doc["zones"]["z"]["beats"]["b"]["steps"][0]["party"] = ["nobody"]
        self.assertTrue(any("unknown hero 'nobody'" in e for e in cf.chapter_errors(doc, "c", ctx)))


if __name__ == "__main__":
    unittest.main()
