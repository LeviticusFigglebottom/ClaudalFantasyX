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
        self.assertTrue(self._errs(lambda c: c["outro"]["victory"].update(hop_m=-1)))
        self.assertTrue(self._errs(lambda c: c["outro"]["escape"].update(clip="run")))
        self.assertTrue(self._errs(lambda c: c["outro"].pop("settle_sec")))
        self.assertEqual(vc.choreo_errors({}, SKILLS), [f"{vc.CHOREO_FILE}: needs a 'choreo' object"])

    def test_camera(self) -> None:
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"].pop("target")))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["actor"].update(anchor="orbit")))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["actor"].update(side_m=-1)))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["actor"].update(fov=170)))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["push"].update(push=2)))
        self.assertTrue(self._errs(lambda c: c["camera"]["by_style"].pop("melee")))
        self.assertTrue(self._errs(lambda c: c["camera"]["by_style"]["melee"].update(lead="swirl")))
        self.assertTrue(self._errs(lambda c: c["camera"]["enemy"].update(contact="nope")))
        self.assertTrue(self._errs(lambda c: c["camera"].update(blend_out_sec=-1)))
        self.assertTrue(self._errs(lambda c: c["camera"]["safe_frame"].update(bottom=0.6)))
        self.assertTrue(self._errs(lambda c: c.pop("camera")))
        self.assertFalse(self._errs(lambda c: c["camera"]["by_style"]["melee"].update(contact="")))


class ArenaValidateTest(unittest.TestCase):
    DOC = json.loads((ROOT / vc.ARENAS_FILE).read_text(encoding="utf-8"))
    ENC = json.loads((ROOT / vc.ENCOUNTERS_FILE).read_text(encoding="utf-8"))

    def _exists(self, res: str) -> bool:
        return vd._res_path(ROOT, res).is_file()

    def test_shipped_data_passes(self) -> None:
        self.assertEqual(vc.arena_errors(self.DOC, self.ENC, self._exists), [])

    def test_bad_rows(self) -> None:
        doc = copy.deepcopy(self.DOC)
        doc["arenas"]["by_encounter"]["no_such_fight"] = "causeway_dusk"
        doc["arenas"]["by_encounter"]["drownbell"] = "nowhere"
        doc["arenas"]["scenes"]["ghost"] = "res://game/battle/arenas/ghost.tscn"
        self.assertEqual(len(vc.arena_errors(doc, self.ENC, self._exists)), 3)
        self.assertTrue(vc.arena_errors({}, self.ENC, self._exists))


if __name__ == "__main__":
    unittest.main()
