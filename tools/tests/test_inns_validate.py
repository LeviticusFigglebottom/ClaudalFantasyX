"""Inn rows in game/data/items/shops.json (M2-UI-06): tools/validate_data.py inns_errors.
Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

SHOPS = ROOT / "game/data/items/shops.json"
FLAGS = {"ch02_met_asha"}


def _doc(*rows: dict) -> dict:
    return {"rules": {}, "shops": [], "inns": list(rows)}


GOOD = {"id": "haluna_inn", "name_key": "INN_HALUNA", "price": 30, "requires_flag": "ch02_met_asha"}


class InnsValidatorTests(unittest.TestCase):
    def test_shipped_inns_are_clean_and_haluna_has_one(self) -> None:
        doc = json.loads(SHOPS.read_text(encoding="utf-8"))
        self.assertEqual(vd.inns_errors(doc, vd.declared_flags_quiet(ROOT)), [])
        self.assertIn("haluna_inn", [r["id"] for r in doc["inns"]])

    def test_no_inns_is_fine(self) -> None:
        self.assertEqual(vd.inns_errors({"rules": {}, "shops": []}, FLAGS), [])

    def test_inns_must_be_a_list_of_objects(self) -> None:
        self.assertTrue(vd.inns_errors({"inns": {}}, FLAGS))
        self.assertTrue(any("must be an object" in e for e in vd.inns_errors(_doc("x"), FLAGS)))  # type: ignore[arg-type]

    def test_missing_fields_and_duplicates(self) -> None:
        errs = vd.inns_errors(_doc({"id": "a"}, dict(GOOD), dict(GOOD)), FLAGS)
        self.assertTrue(any("missing name_key, price" in e for e in errs), errs)
        self.assertTrue(any("duplicate inn id 'haluna_inn'" in e for e in errs), errs)

    def test_price_must_be_a_non_negative_int(self) -> None:
        for bad in (-1, 2.5, "30", True):
            errs = vd.inns_errors(_doc(dict(GOOD, price=bad)), FLAGS)
            self.assertTrue(any("price" in e for e in errs), (bad, errs))
        self.assertEqual(vd.inns_errors(_doc(dict(GOOD, price=0)), FLAGS), [], "a free bed is allowed")

    def test_flags_must_be_declared_and_strings_non_empty(self) -> None:
        errs = vd.inns_errors(_doc(dict(GOOD, requires_flag="ch99_nope", desc_key="")), FLAGS)
        self.assertTrue(any("undeclared story flag 'ch99_nope'" in e for e in errs), errs)
        self.assertTrue(any("desc_key" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
