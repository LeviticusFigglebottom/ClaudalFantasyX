"""Read and opening checks in tools/validate_data.py (M1-CMB-03, formulas.md § Openings).
Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

READ = {"id": "read", "kind": "support", "target": "single_foe", "read": True}
CRAB = {"id": "crab", "name_key": "ENEMY_CRAB", "lore_key": "LORE_CRAB"}


def _rows(name: str) -> list:
    return json.loads((ROOT / f"game/data/battle/{name}.json").read_text())[name]


class ReadOpeningsValidateTests(unittest.TestCase):
    def errs(self, skills: list | None = None, enemies: list | None = None, encounters: list | None = None) -> list:
        return vd.read_openings_errors([READ] if skills is None else skills, [CRAB] if enemies is None else enemies,
                                       [] if encounters is None else encounters)

    def test_clean(self) -> None:
        self.assertEqual(self.errs(encounters=[{"id": "a", "opening": "ambush"}, {"id": "b"}]), [])

    def test_repo_tables_are_clean(self) -> None:
        self.assertEqual(vd.read_openings_errors(_rows("skills"), _rows("enemies"), _rows("encounters")), [])
        self.assertTrue(any(s.get("read") is True for s in _rows("skills")), "the repo has a Read skill")

    def test_read_must_be_a_bool(self) -> None:
        self.assertIn("'read' must be true or false", self.errs(skills=[dict(READ, read="yes")])[0])

    def test_read_is_a_single_foe_support_row(self) -> None:
        self.assertIn("kind 'support'", self.errs(skills=[dict(READ, kind="physical")])[0])
        self.assertIn("target 'single_foe'", self.errs(skills=[dict(READ, target="all_foes")])[0])
        self.assertEqual(self.errs(skills=[dict(READ, read=False, kind="physical")]), [], "read: false is plain")

    def test_enemies_need_lore_and_name_when_read_exists(self) -> None:
        got = self.errs(enemies=[{"id": "eel", "name_key": ""}, "junk"])
        self.assertEqual(len(got), 2)
        self.assertTrue(any("needs a lore_key" in e for e in got))
        self.assertTrue(any("needs a name_key" in e for e in got))
        self.assertEqual(self.errs(skills=[{"id": "attack"}], enemies=[{"id": "eel"}]), [], "no Read, no demand")

    def test_opening_values(self) -> None:
        got = self.errs(encounters=[{"id": "x", "opening": "first_strike"}, "junk"])
        self.assertEqual(len(got), 1)
        self.assertIn("encounters.x: opening must be one of", got[0])
        for ok in sorted(vd.OPENINGS):
            self.assertEqual(self.errs(encounters=[{"id": "x", "opening": ok}]), [], ok)

    def test_check_reports_through_the_report(self) -> None:
        rep = vd.Report()
        files = {"game/data/battle/skills.json": {"skills": [dict(READ, kind="heal")]},
                 "game/data/battle/enemies.json": {"enemies": "not a list"},
                 "game/data/battle/encounters.json": []}
        vd.check_read_openings(files, rep)
        self.assertEqual(len(rep.errors), 1)


if __name__ == "__main__":
    unittest.main()
