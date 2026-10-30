"""tools/audio/tell_check.py (the Lead's 10-30 21:25 accessibility item): every Act I wind-up tell differs from its
enemy's attack and from every tell it can meet in one fight, so a player who hears it knows a threat is gathering and
which. A retuned tell or attack that makes two alike fails here."""

from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audio"))
import tell_check as tc  # noqa: E402


class TellCheckTest(unittest.TestCase):
    def test_act1_tells_are_distinct_where_it_matters(self) -> None:
        self.assertEqual(tc.main([]), 0)

    def test_the_judge_tells_a_sound_from_itself_apart_from_nothing(self) -> None:
        rows = tc._sfx_rows()
        f = tc.features(tc._file(rows, "skill_gnaw_coil"))
        self.assertEqual(tc.compare(f, f)["cues"], [])


if __name__ == "__main__":
    unittest.main()
