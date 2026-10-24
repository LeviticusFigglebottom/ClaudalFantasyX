"""M2-CMB-05 / M2-FP-17: validate_data's checks for vowbound.json bound_flag, the foes_all_absorb AI
condition and skills.json requires_field."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as v  # noqa: E402


class VowboundRulesValidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.files = v.load_json_files(ROOT, v.Report())
        self.declared = v.declared_flags_quiet(ROOT)

    def _vowbound_flag_errors(self, flag: str) -> list:
        files = copy.deepcopy(self.files)
        files[v.VOWBOUND_FILE]["vowbound"][0]["bound_flag"] = flag
        rep = v.Report()
        v.check_vowbound_flags(files, self.declared, rep)
        return rep.errors

    def test_the_real_data_is_clean(self) -> None:
        rep = v.Report()
        v.check_vowbound_flags(self.files, self.declared, rep)
        self.assertEqual(rep.errors, [])

    def test_an_undeclared_bound_flag_is_reported(self) -> None:
        errs = self._vowbound_flag_errors("no_such_flag")
        self.assertTrue(any("undeclared bound_flag" in e for e in errs), errs)

    def test_foes_all_absorb_takes_an_element(self) -> None:
        self.assertIn("foes_all_absorb", v.AI_CONDITIONS)
        self.assertTrue(v._ai_arg_ok("foes_all_absorb", "water", set()))
        self.assertFalse(v._ai_arg_ok("foes_all_absorb", "none", set()))
        self.assertFalse(v._ai_arg_ok("foes_all_absorb", 3, set()))

    def test_requires_field_must_name_a_field(self) -> None:
        refs = {"skills": set(), "enemies": set(), "flags": set(), "statuses": set()}
        errs = v._boss_skill_errors({"id": "x", "requires_field": ""}, refs)
        self.assertTrue(any("requires_field" in e for e in errs), errs)
        self.assertEqual(v._boss_skill_errors({"id": "x", "requires_field": "flood"}, refs), [])


if __name__ == "__main__":
    unittest.main()
