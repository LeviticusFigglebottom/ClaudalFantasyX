"""docs/kb/audio/act2_direction_holds.json (act1_playthrough.py --holds): every script it names exists and every shot is
one of that script's `@camera` ids, so a renamed shot (Ch11's L-ids became V00/V10/T00) can't drop out of the gap
check unseen; and with the holds the staged Act II scenes have no music gap past the one Story has to answer for."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
HOLDS = ROOT / "docs/kb/audio/act2_direction_holds.json"
CAMERA = re.compile(r"^\s*@camera\s+(\S+)", re.M)
# Story's open question (the live log): is ch14_the_vows' silence after peace_wedding_break meant?
KNOWN = ("ch14_the_vows",)


class DirectionHoldsTest(unittest.TestCase):
    def test_every_hold_names_a_real_shot(self) -> None:
        holds = json.loads(HOLDS.read_text(encoding="utf-8"))
        scripts = {p.stem: p for p in (ROOT / "game/data/dialogue").rglob("*.dlg")}
        for stem, shots in holds.items():
            if stem.startswith("_"):
                continue
            self.assertIn(stem, scripts, f"{stem} is a script")
            cams = set(CAMERA.findall(scripts[stem].read_text(encoding="utf-8")))
            for cam, sec in shots.items():
                self.assertIn(cam, cams, f"{stem}: {cam} is one of its shots")
                self.assertGreater(float(sec), 0.0)

    def test_the_staged_scenes_have_no_music_gap(self) -> None:
        import act1_playthrough as P
        import act1_audio_audit as A

        A.set_act(2)
        holds = json.loads(HOLDS.read_text(encoding="utf-8"))
        gaps = [r for p in A._dlg_files() if "@music" in p.read_text(encoding="utf-8")
                for r in P.scan(p, 0.2, holds) if " gap: " in r and not any(k in r for k in KNOWN)]
        self.assertEqual(gaps, [])


if __name__ == "__main__":
    unittest.main()
