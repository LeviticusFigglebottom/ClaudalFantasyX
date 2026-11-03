"""M3-CMB-05: validate_data.field_usable_errors (spells castable from the field menu)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import validate_data  # noqa: E402


def _doc(**row: object) -> dict:
    base = {"id": "x", "kind": "heal", "target": "single_ally", "mp_cost": 4}
    base.update(row)
    return {"skills": [base]}


class FieldUsableTest(unittest.TestCase):
    def test_shipped_skills_are_clean(self) -> None:
        doc = json.loads((ROOT / "game/data/battle/skills.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_data.field_usable_errors(doc), [])
        usable = {s["id"] for s in doc["skills"] if s.get("field_usable")}
        self.assertTrue({"mend", "chorus_mend"} <= usable, usable)

    def test_a_heal_on_allies_passes(self) -> None:
        self.assertEqual(validate_data.field_usable_errors(_doc(field_usable=True)), [])
        self.assertEqual(validate_data.field_usable_errors(_doc(field_usable=False, target="single_foe")), [])

    def test_a_cleanse_passes(self) -> None:
        row = _doc(field_usable=True, kind="support", cleanses=["poison"])
        self.assertEqual(validate_data.field_usable_errors(row), [])

    def test_refusals(self) -> None:
        self.assertTrue(validate_data.field_usable_errors(_doc(field_usable="yes")))
        self.assertTrue(validate_data.field_usable_errors(_doc(field_usable=True, target="single_foe")))
        self.assertTrue(validate_data.field_usable_errors(_doc(field_usable=True, kind="support")))
        self.assertTrue(validate_data.field_usable_errors(_doc(field_usable=True, swell=True)))
        self.assertTrue(validate_data.field_usable_errors(_doc(field_usable=True, drain_pct=50)))


if __name__ == "__main__":
    unittest.main()
