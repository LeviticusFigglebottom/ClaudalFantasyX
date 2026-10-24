"""Boss-mechanics checks in tools/validate_data.py (M2-FP-06, battle_ctb.md "The Drownbell").
Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

SKILLS = [
    {"id": "slam"}, {"id": "toll"},
    {"id": "gather", "charge": {"skill": "toll", "turns": 2}},
    {"id": "rouse", "summon": "polyp"},
    {"id": "call", "requires_flag": "bound", "clears_field": "flood"},
]
BELL = {
    "id": "bell", "skills": ["slam", "gather", "toll"], "weak_point": {"hits": 3, "max_delay": 200, "name_key": "K"},
    "phases": [{
        "id": "flood", "at_hp_pct": 40, "name_key": "PK", "prompt_key": "TK", "skills": ["slam", "rouse"],
        "field": "flood", "spawn": ["polyp"], "stats": {"defense": 10}, "affinities": {"water": "absorb"},
        "ai": [{"if": {"field_active": "flood", "allies_alive_below": 3}, "pick": [{"skill": "rouse", "target": "self"}]},
               {"pick": [{"skill": "slam", "target": "largest_ally"}]}],
    }],
}
POLYP = {"id": "polyp", "field": "flood", "skills": ["slam"]}
REFS = {"skills": {s["id"] for s in SKILLS}, "enemies": {"bell", "polyp"}, "statuses": {"haste"}, "flags": {"bound"}}


class BossValidateTests(unittest.TestCase):
    def check(self, skills: list | None = None, enemies: list | None = None) -> tuple[list[str], list[str]]:
        return vd.boss_errors(SKILLS if skills is None else skills, [BELL, POLYP] if enemies is None else enemies, REFS)

    def test_clean_data(self) -> None:
        self.assertEqual(self.check(), ([], []))

    def test_skill_fields(self) -> None:
        bad = copy.deepcopy(SKILLS)
        bad[2]["charge"] = {"skill": "nope", "turns": 2}
        bad[3]["summon"] = "ghost"
        bad[4]["requires_flag"] = "undeclared"
        bad[4]["clears_field"] = ""
        errs, _ = self.check(skills=bad)
        self.assertEqual(len(errs), 4, errs)
        bad = copy.deepcopy(SKILLS)
        bad[2]["charge"]["turns"] = 0
        self.assertIn("charge 'turns'", " ".join(self.check(skills=bad)[0]))

    def test_weak_point_and_field(self) -> None:
        bell = copy.deepcopy(BELL)
        bell["weak_point"] = {"hits": 0, "max_delay": 200}
        polyp = dict(POLYP, field="")
        errs, _ = self.check(enemies=[bell, polyp])
        self.assertEqual(len(errs), 2, errs)

    def test_phase_rows(self) -> None:
        bell = copy.deepcopy(BELL)
        p = bell["phases"][0]
        p.update({"at_hp_pct": 100, "colour": 1, "stats": {"hp": 5}, "spawn": ["ghost"], "delay_immune": "yes"})
        p["ai"][1]["pick"][0]["skill"] = "toll"
        errs, _ = self.check(enemies=[bell, POLYP])
        text = " ".join(errs)
        for needle in ("at_hp_pct", "unknown key 'colour'", "stat 'hp'", "unknown enemy 'ghost'", "delay_immune",
                       "the phase does not have"):
            self.assertIn(needle, text)

    def test_phases_must_descend_and_have_unique_ids(self) -> None:
        bell = copy.deepcopy(BELL)
        second = copy.deepcopy(bell["phases"][0])
        second["at_hp_pct"] = 60
        bell["phases"].append(second)
        text = " ".join(self.check(enemies=[bell, POLYP])[0])
        self.assertIn("unique string 'id'", text)
        second["id"] = "later"
        self.assertIn("at_hp_pct", " ".join(self.check(enemies=[bell, POLYP])[0]))

    def test_a_field_nothing_clears_is_a_warning(self) -> None:
        skills = [s for s in SKILLS if s["id"] != "call"]
        errs, warns = vd.boss_errors(skills, [BELL, POLYP], REFS)
        self.assertEqual(errs, [])
        self.assertEqual(len(warns), 1)

    def test_new_ai_vocabulary(self) -> None:
        self.assertIn("field_active", vd.AI_CONDITIONS)
        self.assertIn("largest_ally", vd.AI_TARGETS)
        self.assertTrue(vd._ai_arg_ok("field_active", "flood", set()))
        self.assertFalse(vd._ai_arg_ok("field_active", "", set()))

    def test_repo_data_is_clean(self) -> None:
        rep = vd.run(ROOT)
        self.assertEqual(rep.errors, [], rep.errors)


if __name__ == "__main__":
    unittest.main()
