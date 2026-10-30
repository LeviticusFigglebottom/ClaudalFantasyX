"""M3-BPR-411: the battle VFX coverage audit runs on the real tables and proposes only library effects."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import battle_vfx_coverage as cov  # noqa: E402


class CoverageTests(unittest.TestCase):
    def test_runs_on_the_real_tables(self) -> None:
        c = cov.coverage()
        self.assertIn("skills", c)
        self.assertIn("items", c)

    def test_proposes_only_existing_effects(self) -> None:
        c = cov.coverage()
        self.assertEqual(c["proposal_missing_effects"], [])
        for table in ("skills", "items"):
            for sid, effect in c["proposal"][table].items():
                self.assertIn(effect, c["effects"], f"{table}.{sid}")

    def test_a_guard_with_no_damage_is_a_gap_and_a_blow_is_not(self) -> None:
        elements = {"none", "fire"}
        self.assertEqual(cov._skill_gap({"id": "g", "kind": "support", "power": 0, "target": "self"}, set(), elements),
                         "stance")
        self.assertEqual(cov._skill_gap({"id": "b", "kind": "physical", "power": 20, "element": "fire"}, set(),
                                        elements), "")
        self.assertEqual(cov._skill_gap({"id": "w", "kind": "magical", "power": 20, "element": "wind"}, set(),
                                        elements), "element")
        self.assertEqual(cov._skill_gap({"id": "m", "kind": "support", "power": 0}, {"m"}, elements), "")

    def test_every_gap_has_a_stage_answer(self) -> None:
        c = cov.coverage()
        for table in ("skills", "items"):
            for sid, answer in c["staged"][table].items():
                self.assertTrue(answer, f"{table}.{sid} ({c[table][sid]}) plays nothing on stage either")



    def test_every_gap_is_explained(self) -> None:  # M3-BPR-411: closed; what is left is kept on purpose
        c = cov.coverage()
        self.assertEqual(c["unexplained"], [], c["unexplained"])

if __name__ == "__main__":
    unittest.main()
