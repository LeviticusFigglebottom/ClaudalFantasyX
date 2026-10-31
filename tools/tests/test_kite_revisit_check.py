"""M5-A3P-1981: tools/act3/kite_revisit_check.py (a Kite revisit never replays a chapter's arrival)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act3"))

import kite_revisit_check as krc  # noqa: E402

KITE = {"open_flag": "kite_flying", "destinations": [{"id": "town", "location_id": "c1/town", "spawn": "Gate"}]}


def chapter(*arrive: dict) -> dict:
    return {"c1.json": {"zones": {"c1/town": {"arrive": list(arrive)}}}}


class SettableFlagsTest(unittest.TestCase):
    def test_steps_dialogue_and_scripts_set_flags_but_a_when_does_not(self):
        docs = [{"steps": [{"set": "a"}, {"battle": "x", "victory_flag": "b"}], "when": {"set": ["never"]}},
                {"triggers": [{"sets_flag": "c"}]}]
        flags = krc.settable_flags(docs, ["<<set $d = true>>"], ['Game.set_flag(&"e")'])
        self.assertEqual(flags, {"a", "b", "c", "d", "e"})


class RevisitErrorsTest(unittest.TestCase):
    def test_a_first_arrival_gated_on_its_own_flag_does_not_replay(self):
        rows = chapter({"when": {"unset": ["c1_arrived"]}, "steps": [{"chapter": 1}, {"set": "c1_arrived"}]})
        self.assertEqual(krc.revisit_errors(KITE, rows, {"c1_arrived"}), [])

    def test_a_row_whose_unset_flag_nothing_sets_replays(self):
        rows = chapter({"when": {"set": ["c1_arrived"], "unset": ["c1_typo"]}, "steps": [{"battle": "boss"}]})
        errors = krc.revisit_errors(KITE, rows, {"c1_arrived"})
        self.assertEqual(len(errors), 1)
        self.assertIn("arrive[0] replays", errors[0])

    def test_a_row_waiting_on_the_kite_itself_replays(self):
        rows = chapter({"when": {"set": ["kite_flying"]}, "steps": [{"play": "x"}]})
        self.assertEqual(len(krc.revisit_errors(KITE, rows, set())), 1)


class RepoTest(unittest.TestCase):
    def test_no_kite_revisit_replays_a_chapter(self):
        self.assertEqual(krc.check(ROOT), [])


if __name__ == "__main__":
    unittest.main()
