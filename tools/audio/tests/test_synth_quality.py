"""Fast objective regression tests for the synth library (M1-AUD-02).

    python3 -m unittest discover -s tools/audio/tests      (about 20 s)

These turn the measurements in docs/kb/audio/pipeline.md into guards: if a
change makes the piano lose its stiff-string partials or two-stage decay,
the reverb ring again, or a loop click, a test fails.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np  # noqa: E402

from synth import analysis as A  # noqa: E402
from synth.dsp import SR, midi_to_hz  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.grand import PedalCurve, grand_note, hammer_force, inharmonicity  # noqa: E402
from synth.looping import LoopMixer, master_loop  # noqa: E402
from synth.performance import ExpressiveTempo, Phrase, plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402


class PianoTests(unittest.TestCase):
    def test_measured_inharmonicity_matches_the_register_table(self):
        for m in (48, 60, 72):
            x = grand_note(m, 0.55, 3.0, seed=3)
            fr = A.find_partials(x, midi_to_hz(m), inharmonicity(m), 12, t0=0.05, length=1.0)
            _, B = A.fit_inharmonicity(fr)
            self.assertLess(abs(np.log(B / inharmonicity(m))), np.log(1.3), f"m={m} B={B:.2e}")

    def test_two_stage_decay_and_frequency_dependent_decay(self):
        x = grand_note(60, 0.55, 8.0, seed=3)
        fr = A.find_partials(x, midi_to_hz(60), inharmonicity(60), 8, t0=0.05, length=1.0)
        early = A.decay_rate_db_per_s(x, fr[0], 0.1, 1.0)
        late = A.decay_rate_db_per_s(x, fr[0], 2.0, 6.0)
        self.assertTrue(6 <= early <= 16, early)
        self.assertLess(late, 0.6 * early)
        rates = [A.decay_rate_db_per_s(x, fr[k], 0.1, 1.0) for k in range(8)]
        self.assertGreater(np.polyfit(fr[:8], rates, 1)[0], 0.0, "higher partials must decay faster")

    def test_harder_blows_are_shorter_and_brighter(self):
        c_soft = len(hammer_force(60, 0.2))
        c_hard = len(hammer_force(60, 0.9))
        self.assertLess(c_hard, c_soft)
        soft = A.spectral_centroid_at(grand_note(60, 0.2, 1.0, seed=1), [0.03])[0]
        hard = A.spectral_centroid_at(grand_note(60, 0.9, 1.0, seed=1), [0.03])[0]
        self.assertGreater(hard, 1.3 * soft)

    def test_pedal_keeps_the_note_ringing_after_key_up(self):
        up = grand_note(60, 0.5, 0.3, seed=2, pedal=PedalCurve.up())
        down = grand_note(60, 0.5, 0.3, seed=2, pedal=PedalCurve(np.array([0.0, 10.0]), np.array([1.0, 1.0])))
        self.assertGreater(len(down), 3 * len(up))

    def test_notes_are_deterministic(self):
        a = grand_note(55, 0.6, 1.0, seed=9)
        b = grand_note(55, 0.6, 1.0, seed=9)
        self.assertTrue(np.array_equal(a, b))


class ReverbTests(unittest.TestCase):
    def test_modulated_fdn_tail_is_close_to_diffuse(self):
        imp = np.zeros((SR * 3, 2))
        imp[0] = 1.0
        ir = ModFDNReverb(rt60=2.6, rt60_high=1.1, seed=7).process(imp, tail=0.0)
        pk = A.tail_spectral_peakiness(ir, 0.4, 1.4)
        self.assertLess(pk["p99_over_median_db"], 10.5)       # old FDN: 15.9; ideal noise: ~8.5
        self.assertLess(A.tail_periodicity(ir), 0.15)          # old FDN: 0.35
        self.assertTrue(2.2 < A.rt60_band(ir, 500) < 3.0)


class PerformanceTests(unittest.TestCase):
    def test_rubato_keeps_phrase_length_close_and_moves_tempo(self):
        tm = ExpressiveTempo([(0, 72), (24, 72)], 24, [Phrase(0, 12, peak=0.6), Phrase(12, 24, peak=0.4)])
        lo, hi = tm.local_bpm_range()
        self.assertLess(lo, 72)
        self.assertGreater(hi, 72)
        self.assertLess(abs(tm.t(24) - 20.0), 1.0)

    def test_pedal_lifts_at_each_change(self):
        p = plan_pedal([1.0, 2.0, 3.0], start=0.5, end_release=4.0, release_len=1.0, g=np.random.default_rng(1))
        for tc in (1.0, 2.0, 3.0):
            win = (p.times > tc) & (p.times < tc + 0.25)
            self.assertLess(p.depth[win].min(), 0.2)
            self.assertGreater(p.at(np.array([tc + 0.4]))[0], 0.8)


class LoopTests(unittest.TestCase):
    def test_steady_state_loop_has_no_seam(self):
        mx = LoopMixer(intro_s=2.0, loop_s=4.0, preroll_s=3.0)
        mx.bus("d", 0.0, send=0.4)
        for i in range(8):   # hits between the seam points, so the seam sits in ringing tails
            x = frame_drum("dum", 0.8, variant=i)
            mx.add("d", x, 0.25 + i * 0.5)
            if i >= 4:       # the intro is the loop's last 2 s, so its tails match the loop start's
                mx.add("d", x, 0.25 + (i - 4) * 0.5, part="intro")
        rv = ModFDNReverb(rt60=1.2, seed=3)
        intro, loop = mx.render(reverb=rv)
        intro, loop = master_loop(intro, loop, -16.0)
        y = np.concatenate([intro, loop])
        seam = A.loop_seam_report(y, len(intro))
        self.assertLess(seam["flux_ratio"], 3.0)
        self.assertLess(mx.splice_residual_db, -60.0)


if __name__ == "__main__":
    unittest.main()
