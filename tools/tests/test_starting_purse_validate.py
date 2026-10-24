"""The new-game purse rule in tools/validate_data.py (M2-CMB-07): items.json rules.starting_currency.
Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

RULE = "rules.starting_currency"


def _errors(starting: object = None, drop: bool = False) -> list[str]:
    items = json.loads((ROOT / "game/data/items/items.json").read_text(encoding="utf-8"))
    if drop:
        items["rules"].pop("starting_currency", None)
    elif starting is not None:
        items["rules"]["starting_currency"] = starting
    refs = {k: set() for k in ("characters", "statuses", "harmful", "beneficial", "facets", "flags")}
    return [e for e in vd.items_errors({"items": items}, refs) if RULE in e]


class StartingPurseTests(unittest.TestCase):
    def test_repo_value_is_valid(self) -> None:
        self.assertEqual(_errors(), [])

    def test_optional(self) -> None:
        self.assertEqual(_errors(drop=True), [])

    def test_zero_and_cap_are_allowed(self) -> None:
        self.assertEqual(_errors(0), [])
        self.assertEqual(_errors(9999999), [])

    def test_negative_fraction_and_over_cap_are_errors(self) -> None:
        for bad in (-1, 2.5, "100", 10000000):
            with self.subTest(bad=bad):
                self.assertTrue(_errors(bad), f"{bad!r} should be refused")


if __name__ == "__main__":
    unittest.main()
