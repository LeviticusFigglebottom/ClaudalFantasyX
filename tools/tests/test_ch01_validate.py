"""M3-C01-02: validate_data checks an encounter's "party_skills" (the skills a tutorial fight lends,
ADR 0034): a {hero id: [skill ids]} object naming real heroes and skills. Runs on the repo's real
battle tables with one encounter row changed.
Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
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


if __name__ == "__main__":
    unittest.main()
