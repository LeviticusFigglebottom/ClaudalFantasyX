"""M2-MNU-306: every hero row in characters.json names its role word (role_key), checked by
tools/validate_data.py. Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402


def _characters() -> list:
    return json.loads((ROOT / "game/data/battle/characters.json").read_text(encoding="utf-8"))["characters"]


class CharacterRolesTest(unittest.TestCase):
    def test_shipped_heroes_all_have_a_role(self) -> None:
        self.assertEqual(vd.character_role_errors(_characters()), [])

    def test_a_missing_or_empty_role_key_is_an_error(self) -> None:
        rows = _characters()
        del rows[0]["role_key"]
        rows[1]["role_key"] = ""
        errs = vd.character_role_errors(rows)
        self.assertEqual(len(errs), 2)
        self.assertTrue(all("role_key" in e for e in errs))
        self.assertIn(rows[0]["id"], errs[0])


if __name__ == "__main__":
    unittest.main()
