"""M3-ARC-01: the chapter flow and greybox layout checks (tools/chapter_flow_check.py) on the
ZoneStory test fixture (game/levels/_tests/zone_story/) and on planted mistakes.
Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import chapter_flow_check as cf  # noqa: E402
import validate_data as vd  # noqa: E402

FIXTURE = ROOT / "game/levels/_tests/zone_story"


def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


class ChapterFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chapter = _json(FIXTURE / "test_chapter.json")
        cls.layout_a = _json(FIXTURE / "zone_a_layout.json")
        cls.layout_b = _json(FIXTURE / "zone_b_layout.json")
        enc = _json(ROOT / "game/data/battle/encounters.json")
        chars = _json(ROOT / "game/data/battle/characters.json")
        cls.ctx = cf.Context(
            flags=vd.declared_flags_quiet(ROOT),
            dialogue={p.stem for p in (ROOT / "game/data/dialogue/compiled").glob("*.json")},
            encounters={r["id"] for r in enc["encounters"]},
            heroes={r["id"] for r in chars["characters"]},
            locations={"zone_story_a": "res://a.tscn", "zone_story_b": "res://b.tscn"},
            layouts={"zone_story_a": cls.layout_a, "zone_story_b": cls.layout_b},
            scene_exists=lambda res: (ROOT / res.removeprefix("res://")).is_file(),
        )

    def _errs(self, chapter: dict) -> list[str]:
        return cf.chapter_errors(chapter, "test_chapter.json", self.ctx)

    def test_the_fixture_passes(self) -> None:
        self.assertEqual(self._errs(self.chapter), [])
        self.assertEqual(cf.layout_errors(self.layout_a, "a", self.ctx), [])
        self.assertEqual(cf.layout_errors(self.layout_b, "b", self.ctx), [])

    def test_the_shipped_registry_passes(self) -> None:
        files = vd.load_json_files(ROOT, vd.Report())
        self.assertEqual(cf.check(ROOT, files, vd.declared_flags_quiet(ROOT)), [])

    def test_bad_names_are_caught(self) -> None:
        c = copy.deepcopy(self.chapter)
        a = c["zones"]["zone_story_a"]
        a["arrive"][0]["when"]["unset"].append("no_such_flag")
        a["arrive"][0]["steps"][1]["play"] = "no_such_scene"
        a["beats"]["gate"]["steps"][0]["battle"] = "no_such_fight"
        a["beats"]["gate"]["steps"][0]["return_spawn"] = "Nowhere"
        a["beats"]["leave"]["steps"][2]["go"]["spawn"] = "Nowhere"
        a["party"]["party"].append("nobody")
        errs = self._errs(c)
        for needle in ("no_such_flag", "no_such_scene", "no_such_fight", "zone_story_a has no spawn 'Nowhere'",
                       "zone_story_b has no spawn 'Nowhere'", "unknown hero 'nobody'"):
            self.assertTrue(any(needle in e for e in errs), f"{needle}: {errs}")

    def test_a_hand_off_must_end_its_steps(self) -> None:
        c = copy.deepcopy(self.chapter)
        c["zones"]["zone_story_a"]["beats"]["onward"]["steps"].append({"set": "test_flag"})
        self.assertTrue(any("must come last" in e for e in self._errs(c)))

    def test_unknown_locations_and_steps(self) -> None:
        c = copy.deepcopy(self.chapter)
        c["zones"]["nowhere"] = {"arrive": [{"steps": [{"dance": True}]}]}
        errs = self._errs(c)
        self.assertTrue(any("not a location" in e for e in errs), errs)
        self.assertTrue(any("exactly one of" in e for e in errs), errs)

    def test_a_trigger_beat_must_exist(self) -> None:
        c = copy.deepcopy(self.chapter)
        del c["zones"]["zone_story_a"]["beats"]["gate"]
        self.assertTrue(any("names no beat 'gate'" in e for e in self._errs(c)))

    def test_layout_shapes_and_flags(self) -> None:
        lay = copy.deepcopy(self.layout_a)
        lay["blocks"].append({"pos": [0, 0]})
        lay["spawns"]["Bad"] = [1, 2]
        lay["triggers"].append({"id": "gate", "at": [0, 0, 0], "size": [1, 0, 1], "requires_flag": "nope"})
        lay["triggers"].append({"id": "x", "at": [0, 0, 0], "size": [1, 0, 1], "activation": "shove"})
        errs = cf.layout_errors(lay, "a", self.ctx)
        for needle in ("blocks[2]", "spawns.Bad", "unique non-empty id", "undeclared flag 'nope'", "activation"):
            self.assertTrue(any(needle in e for e in errs), f"{needle}: {errs}")

    def test_greybox_scenes_read_their_spawns_from_the_layout(self) -> None:
        text = (FIXTURE / "zone_a.tscn").read_text(encoding="utf-8")
        self.assertEqual(cf.greybox_layout_path(text), "res://game/levels/_tests/zone_story/zone_a_layout.json")
        self.assertEqual(vd.scene_spawns(text), {"Start", "AfterFight"})


if __name__ == "__main__":
    unittest.main()
