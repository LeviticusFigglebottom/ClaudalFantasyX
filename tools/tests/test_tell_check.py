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


def _unfetched() -> list[str]:
    """The tells and attacks this needs, where the checkout holds a Git LFS pointer instead of audio (never pulled)."""
    rows = tc._sfx_rows()
    battle = tc.json.load(open(os.path.join(tc.ROOT, "game", "data", "audio", "battle_sfx.json")))
    voices = tc.json.load(open(os.path.join(tc.ROOT, "game", "data", "audio", "creature_voices.json")))["creatures"]
    ids = [battle["vfx"].get(s) or battle["skills"].get(s) for s in tc.ACT1_TELLS]
    ids += [((voices.get(e) or {}).get("events") or {}).get("attack") for e, _ in tc.ACT1_TELLS.values()]
    out = []
    for i in filter(None, ids):
        with open(tc._file(rows, i), "rb") as f:
            if f.read(23) == b"version https://git-lfs":
                out.append(i)
    return out


@unittest.skipIf(_unfetched(), "Act I's battle sounds are Git LFS and not fetched here (git lfs pull to judge them)")
class TellCheckTest(unittest.TestCase):
    def test_act1_tells_are_distinct_where_it_matters(self) -> None:
        self.assertEqual(tc.main([]), 0)

    def test_the_judge_tells_a_sound_from_itself_apart_from_nothing(self) -> None:
        rows = tc._sfx_rows()
        f = tc.features(tc._file(rows, "skill_gnaw_coil"))
        self.assertEqual(tc.compare(f, f)["cues"], [])


if __name__ == "__main__":
    unittest.main()
