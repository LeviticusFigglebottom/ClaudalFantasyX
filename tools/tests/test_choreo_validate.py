"""Battle choreography data checks (M2-BPR-01; tools/validate_choreo.py).
Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_choreo as vc  # noqa: E402
import validate_data as vd  # noqa: E402

DOC = json.loads((ROOT / vc.CHOREO_FILE).read_text(encoding="utf-8"))
SKILLS = json.loads((ROOT / vc.SKILLS_FILE).read_text(encoding="utf-8"))


class ChoreoValidateTest(unittest.TestCase):
    def _errs(self, mutate) -> list[str]:
        doc = copy.deepcopy(DOC)
        mutate(doc["choreo"])
        return vc.choreo_errors(doc, SKILLS)

    def test_shipped_data_passes(self) -> None:
        self.assertEqual(vc.choreo_errors(DOC, SKILLS), [])

    def test_validate_data_runs_it(self) -> None:
        self.assertFalse([e for e in vd.run(ROOT).errors if vc.CHOREO_FILE in e])

    def test_strike_and_contact_bounds(self) -> None:
        self.assertTrue(self._errs(lambda c: c["styles"]["melee"].update(strike_sec=0)))
        self.assertTrue(self._errs(lambda c: c["styles"]["melee"].update(contact_at=1.5)))
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].update(approach_sec=-1)))

    def test_clip_must_be_in_the_contract(self) -> None:
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].update(clip="twirl")))
        self.assertTrue(self._errs(lambda c: c["reaction"]["damage"].update(clip="twirl")))

    def test_style_references(self) -> None:
        self.assertTrue(self._errs(lambda c: c["style_by_skill"].update(attack="nope")))
        self.assertTrue(self._errs(lambda c: c["style_by_skill"].update(no_such_skill="melee")))
        self.assertTrue(self._errs(lambda c: c["style_by_kind"].pop("magical")))
        self.assertTrue(self._errs(lambda c: c.update(item_style="nope")))
        self.assertTrue(self._errs(lambda c: c["styles"].pop("melee")))

    def test_travel_needs_its_distance(self) -> None:
        self.assertTrue(self._errs(lambda c: c["styles"]["melee"].pop("stop_short_m")))
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].pop("step_m")))
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].update(travel="fly")))

    def test_blocks(self) -> None:
        self.assertTrue(self._errs(lambda c: c["ko"].update(collapse_sec=-1)))
        self.assertTrue(self._errs(lambda c: c["enter"].update(clip="nope")))
        self.assertTrue(self._errs(lambda c: c["reduced_motion"].update(travel_scale=2)))
        self.assertTrue(self._errs(lambda c: c["speeds"].update(min=0)))
        self.assertTrue(self._errs(lambda c: c.update(settle_sec="x")))
        self.assertEqual(vc.choreo_errors({}, SKILLS), [f"{vc.CHOREO_FILE}: needs a 'choreo' object"])


if __name__ == "__main__":
    unittest.main()
