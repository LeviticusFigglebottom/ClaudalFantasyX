"""Skill target kinds in tools/validate_data.py (M2-CMB-02: all_other_allies, skills only).
Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

SKILLS = "game/data/battle/skills.json"


class SkillTargetsValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = vd.load_json_files(ROOT, vd.Report())

    def target_errors(self, files: dict) -> list[str]:
        rep = vd.Report()
        vd.check_battle(files, rep)
        return [e for e in rep.errors if "target must be one of" in e]

    def _with_verse_target(self, target: str) -> dict:
        files = copy.deepcopy(self.files)
        for s in files[SKILLS]["skills"]:
            if s["id"] == "shallows_verse":
                s["target"] = target
        return files

    def test_repo_verse_is_a_song_for_the_others(self) -> None:
        verse = next(s for s in self.files[SKILLS]["skills"] if s["id"] == "shallows_verse")
        self.assertEqual(verse["target"], "all_other_allies")
        self.assertEqual(self.target_errors(self.files), [])

    def test_all_other_allies_is_a_skill_only_kind(self) -> None:
        self.assertIn("all_other_allies", vd.SKILL_ONLY_TARGETS)
        self.assertNotIn("all_other_allies", vd.SKILL_TARGETS, "items do not take it")

    def test_unknown_skill_target_is_caught(self) -> None:
        got = self.target_errors(self._with_verse_target("everyone_but_me"))
        self.assertEqual(len(got), 1)
        self.assertIn("skills.shallows_verse", got[0])
        self.assertIn("all_other_allies", got[0], "the message lists the skill-only kind")

    def test_items_refuse_all_other_allies(self) -> None:
        refs = {k: set() for k in ("characters", "statuses", "harmful", "beneficial", "facets", "flags")}
        item = {"id": "song_shell", "category": "consumable", "name_key": "K", "desc_key": "K", "price": 1,
                "battle": {"target": "all_other_allies", "rank": 3, "effects": []}}
        errs = vd.items_errors({"items": {"items": [item]}}, refs)
        self.assertTrue(any("battle.target must be one of" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
