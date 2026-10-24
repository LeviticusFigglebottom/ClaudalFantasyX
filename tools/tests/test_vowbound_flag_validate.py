"""A Vowbound's bound_flag in tools/validate_data.py (M2-UI-05: the battle scene binds a Vowbound
while its story flag is set). Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

VOW = vd.VOWBOUND_FILE


class VowboundFlagValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = vd.load_json_files(ROOT, vd.Report())
        self.declared = vd.declared_flags_quiet(ROOT)

    def errors(self, doc: object) -> list[str]:
        return vd.vowbound_flag_errors(doc, self.declared)

    def test_the_shipped_rows_name_declared_flags(self) -> None:
        self.assertEqual(self.errors(self.files[VOW]), [])
        ilun = next(r for r in self.files[VOW]["vowbound"] if r["id"] == "ilun")
        self.assertEqual(ilun["bound_flag"], "ch03_ilun_bound")

    def test_an_undeclared_flag_is_an_error(self) -> None:
        doc = copy.deepcopy(self.files[VOW])
        doc["vowbound"][0]["bound_flag"] = "ch99_nobody_bound"
        errs = self.errors(doc)
        self.assertEqual(len(errs), 1)
        self.assertIn("ch99_nobody_bound", errs[0])

    def test_a_non_string_flag_is_an_error(self) -> None:
        doc = copy.deepcopy(self.files[VOW])
        doc["vowbound"][0]["bound_flag"] = 3
        self.assertEqual(len(self.errors(doc)), 1)

    def test_the_flag_is_optional(self) -> None:
        doc = copy.deepcopy(self.files[VOW])
        del doc["vowbound"][0]["bound_flag"]
        self.assertEqual(self.errors(doc), [])

    def test_run_reports_it(self) -> None:
        rep = vd.Report()
        doc = copy.deepcopy(self.files[VOW])
        doc["vowbound"][0]["bound_flag"] = "ch99_nobody_bound"
        files = dict(self.files)
        files[VOW] = doc
        vd.check_vowbound_flags(files, self.declared, rep)
        self.assertEqual(len(rep.errors), 1)


if __name__ == "__main__":
    unittest.main()
