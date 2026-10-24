"""Vowbound rows in tools/validate_data.py (M2-CMB-04: game/data/battle/vowbound.json).
Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

VOW = vd.VOWBOUND_FILE
SKILLS = "game/data/battle/skills.json"


class VowboundValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = vd.load_json_files(ROOT, vd.Report())

    def errors(self, files: dict) -> list[str]:
        rep = vd.Report()
        vd.check_vowbound(files, rep)
        return rep.errors

    def ilun(self, files: dict) -> dict:
        return next(r for r in files[VOW]["vowbound"] if r["id"] == "ilun")

    def edited(self, **fields: object) -> dict:
        files = copy.deepcopy(self.files)
        self.ilun(files).update(fields)
        return files

    def test_repo_rows_pass_and_feed_the_loc_check(self) -> None:
        self.assertEqual(self.errors(self.files), [])
        self.assertIn("VOWBOUND_ILUN", vd.check_vowbound(self.files, vd.Report()))

    def test_the_finisher_is_no_heros_swell_row(self) -> None:
        rep = vd.Report()
        vd.check_swell(self.files, rep)
        self.assertEqual(rep.errors, [], "Floodnet needs no swell.json hero")

    def test_missing_file_and_array(self) -> None:
        files = copy.deepcopy(self.files)
        del files[VOW]
        self.assertEqual(self.errors(files), [f"{VOW}: missing"])
        files[VOW] = {"vowbound": {}}
        self.assertEqual(self.errors(files), [f"{VOW}: needs a 'vowbound' array"])

    def test_the_caller_must_be_a_hero(self) -> None:
        got = self.errors(self.edited(caller="pell"))
        self.assertEqual(len(got), 1)
        self.assertIn("caller must be a character id", got[0])

    def test_the_call_has_a_rank(self) -> None:
        self.assertIn("call_rank must be an int in 1..8", self.errors(self.edited(call_rank=0))[0])
        self.assertIn("call_rank", self.errors(self.edited(call_rank="3"))[0])

    def test_stat_blocks_need_every_stat_but_level(self) -> None:
        base = dict(self.ilun(self.files)["base"])
        del base["luck"]
        self.assertIn("base must give exactly", self.errors(self.edited(base=base))[0])
        scale = dict(self.ilun(self.files)["scale_pct"], level=100)
        self.assertIn("scale_pct must give exactly", self.errors(self.edited(scale_pct=scale))[0])
        neg = dict(self.ilun(self.files)["scale_pct"], hp=-1)
        self.assertIn("values must be ints >= 0", self.errors(self.edited(scale_pct=neg))[0])
        dead = dict(self.ilun(self.files)["base"], hp=0)
        self.assertIn("base hp must be >= 1", self.errors(self.edited(base=dead))[0])

    def test_skills_are_known_and_never_a_swell_row(self) -> None:
        self.assertIn("unknown skill 'tide_song'", self.errors(self.edited(skills=["attack", "tide_song"]))[0])
        self.assertIn("is a Swell technique", self.errors(self.edited(skills=["floodnet"]))[0])
        self.assertIn("non-empty list", self.errors(self.edited(skills=[]))[0])

    def test_affinities_and_swell_block(self) -> None:
        self.assertIn("affinities", self.errors(self.edited(affinities={"none": "weak"}))[0])
        self.assertIn("affinities", self.errors(self.edited(affinities={"water": "drinks"}))[0])
        self.assertIn("needs a swell block", self.errors(self.edited(swell=None))[0])
        self.assertIn("swell.rate", self.errors(self.edited(swell={"rate": 0, "technique": "floodnet"}))[0])
        got = self.errors(self.edited(swell={"rate": 150, "technique": "brine_lash"}))
        self.assertIn("swell.technique must be a skills.json row with swell true", got[0])

    def test_a_finisher_row_is_marked_vowbound(self) -> None:
        files = copy.deepcopy(self.files)
        next(s for s in files[SKILLS]["skills"] if s["id"] == "floodnet").pop("vowbound")
        self.assertIn('needs "vowbound": true', self.errors(files)[0])
        rep = vd.Report()
        vd.check_swell(files, rep)
        self.assertIn("skills.floodnet: a Swell row that no hero", rep.errors[0], "unmarked, swell.json claims it")

    def test_a_learned_finisher_is_caught(self) -> None:
        files = copy.deepcopy(self.files)
        chars = files["game/data/battle/characters.json"]["characters"]
        next(c for c in chars if c["id"] == "asha")["skills"].append("floodnet")
        self.assertIn("is learned by a character or enemy", self.errors(files)[0])

    def test_an_id_may_not_shadow_a_hero(self) -> None:
        self.assertIn("clashes with a character id", self.errors(self.edited(id="rhen"))[0])

    def test_the_banned_class_name_is_not_a_field(self) -> None:
        self.assertNotIn("summ" + "oner", self.ilun(self.files), "the caller field avoids the banned term")


if __name__ == "__main__":
    unittest.main()
