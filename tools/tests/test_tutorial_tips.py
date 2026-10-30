"""M2-UI-24: validate_data's tutorial tip checks. Run: python3 -m unittest discover -s tools/tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_data as vd  # noqa: E402


def _doc(*tips: dict) -> dict:
    return {"tutorial_tips": {"tips": list(tips)}}


GOOD = {"id": "a", "on": "near", "tag": "shop", "flag": "seen_a", "title_key": "T", "body_key": "B"}


class TutorialTipsTest(unittest.TestCase):
    def test_a_good_tip_passes_and_returns_its_keys(self) -> None:
        errs, keys = vd.tutorial_tip_errors(_doc(GOOD), {"seen_a"})
        self.assertEqual(errs, [])
        self.assertEqual(keys, ["T", "B"])

    def test_undeclared_flags_unknown_triggers_and_shared_flags_fail(self) -> None:
        bad = dict(GOOD, on="sometime")
        errs, _ = vd.tutorial_tip_errors(_doc(bad, dict(GOOD, id="b", requires=["nope"])), {"seen_a"})
        self.assertTrue(any("'on' must be" in e for e in errs))
        self.assertTrue(any("'nope' is not declared" in e for e in errs))
        self.assertTrue(any("used by another tip" in e for e in errs))

    def test_a_list_of_whens_and_requires_any_are_checked_flag_by_flag(self) -> None:
        tip = dict(GOOD, on="flag", when=["seen_a", "nope_when"], requires_any=["nope_any"])
        errs, _ = vd.tutorial_tip_errors(_doc(tip), {"seen_a"})
        self.assertTrue(any("'nope_when' is not declared" in e for e in errs))
        self.assertTrue(any("'nope_any' is not declared" in e for e in errs))

    def test_the_shipped_file_is_clean(self) -> None:
        root = Path(__file__).resolve().parents[2]
        import json

        doc = json.loads((root / vd.TUTORIAL_TIPS_FILE).read_text(encoding="utf-8"))
        flags = vd.declared_flags_quiet(root)
        self.assertEqual(vd.tutorial_tip_errors(doc, flags)[0], [])


if __name__ == "__main__":
    unittest.main()
