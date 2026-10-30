"""The Act I mix pass (tools/audio/act1_mix_pass.py) finds its hand-overs: cutscene -> field, field <-> battle and
field <-> boss pairs for Act I, each naming two cues the deck can play. Levels are not measured here (slow); run the
tool for the report. Run: python3 -m unittest discover -s tools/tests"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("act1_mix_pass", ROOT / "tools/audio/act1_mix_pass.py")
mix = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mix)


class Act1MixPassTest(unittest.TestCase):
    def test_it_pairs_every_kind_of_hand_over_in_act1(self) -> None:
        mix.A.set_act(1)
        rows = mix.pairs()
        kinds = {k.split(" (")[0] for _, k, _, _ in rows}
        self.assertTrue({"cutscene -> field", "field <-> battle", "field <-> boss"} <= kinds, kinds)
        self.assertFalse(any(ch.startswith("ch1") for ch, _, _, _ in rows), "Act I only")

    def test_every_paired_cue_has_files(self) -> None:
        mix.A.set_act(1)
        for _, _, a, b in mix.pairs():
            for cue in (a, b):
                got = mix.cue_files(cue)
                self.assertIsNotNone(got, cue)
                self.assertTrue(all(p.is_file() for p in got[0]), cue)
