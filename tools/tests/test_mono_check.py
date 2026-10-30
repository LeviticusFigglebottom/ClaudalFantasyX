"""tools/audio/mono_check.py (the Lead's 10-30 21:25 accessibility item): the mono fold-down judge. A wide but
honest stereo part passes; a part in anti-phase, which vanishes for a mono listener, fails; a quiet out-of-phase tail
is not judged. The full scan over assets/audio is run by hand (minutes); this holds the judge itself."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audio"))
import mono_check as mc  # noqa: E402
from synth.dsp import SR  # noqa: E402
from synth.mixer import write_ogg  # noqa: E402


def _tone(sec: float, hz: float = 220.0) -> np.ndarray:
    t = np.arange(int(sec * SR)) / SR
    return 0.3 * np.sin(2 * np.pi * hz * t)


class MonoCheckTest(unittest.TestCase):
    def _measure(self, stereo: np.ndarray) -> dict:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.ogg")
            write_ogg(p, stereo, quality=6.0)
            return mc.measure(p)

    def test_a_panned_part_and_decorrelated_noise_pass(self) -> None:
        g = np.random.default_rng(1)
        tone = _tone(3.0)
        noise = 0.05 * g.standard_normal((len(tone), 2))
        wide = np.stack([tone, 0.4 * tone], 1) + noise
        row = self._measure(wide)
        self.assertEqual(mc.failing(row), [], row)

    def test_a_part_in_anti_phase_fails(self) -> None:
        tone = _tone(3.0)
        row = self._measure(np.stack([tone, -tone], 1))
        self.assertTrue(any("goes missing" in w for w in mc.failing(row)), row)

    def test_a_quiet_out_of_phase_tail_is_not_judged(self) -> None:
        tone = _tone(2.0)
        tail = 0.003 * _tone(1.0, 330.0)
        x = np.concatenate([np.stack([tone, tone], 1), np.stack([tail, -tail], 1)])
        row = self._measure(x)
        self.assertEqual(mc.failing(row), [], row)

    def test_a_mono_file_passes(self) -> None:
        tone = _tone(1.0)
        self.assertTrue(self._measure(np.stack([tone, tone], 1))["mono"])


if __name__ == "__main__":
    unittest.main()
