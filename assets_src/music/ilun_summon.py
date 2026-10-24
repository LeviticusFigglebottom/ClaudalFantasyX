"""`ilun_summon`: the sting when Asha calls Ilun, the first Vowbound (M2-AUD-03; vertical_slice.md B10), ~5.5 s.

Original (SPEC §2). The brief: "Glass and water, the first phrase of the Hush, very high." The Hush theme's first
six notes (hush_theme_v2.py MEL_A: E D C | A G A) two octaves up on hard glass-like bars, quick and close together so
they ring into one another; under them, water gathering (a swelling field of small bubbles) and a breath of high
shimmer; they settle on an open A and E left ringing. Stereo, on the Music bus over the ducked battle cue.

Render:  python3 assets_src/music/ilun_summon.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "sfx", "ilun_summon.ogg")
SEED = 20261110
TARGET_LUFS = -16.0
LENGTH = 5.5
PHRASE = [("E7", 0.0, .55), ("D7", 0.36, .45), ("C7", 0.54, .42), ("A6", 0.72, .5), ("G6", 1.26, .4), ("A6", 1.44, .48)]
CHORD = [("A5", 1.9), ("E6", 1.96), ("A6", 2.02)]


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = Mixer(LENGTH + 3.0)
    mx.bus("glass", 0.0, send=0.5, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("water", -10.0, send=0.35, process=lambda x: filt(x, [bq_highpass(400, 0.7), bq_lowpass(7000, 0.7)]))
    mx.bus("shimmer", -22.0, send=0.6)
    for i, (p, t, v) in enumerate(PHRASE):
        x = metallophone_note(n(p), v, seed=SEED + i, decay=3.5, hardness=0.85, ombak_hz=7.5)
        mx.add("glass", x, 0.15 + t, pan=-0.35 + 0.14 * i)
    for i, (p, t) in enumerate(CHORD):
        x = metallophone_note(n(p), 0.42, seed=SEED + 50 + i, decay=4.5, hardness=0.6, ombak_hz=5.0)
        mx.add("glass", x, 0.15 + t, pan=-0.3 + 0.3 * i)
    w = np.zeros(int(LENGTH * SR))
    tt = 0.0
    while tt < 2.6:
        r = float(np.exp(g.uniform(np.log(0.8), np.log(3.0))))
        b = bubble(r, g.uniform(0.2, 1.0), rise=0.12)
        s = int(tt * SR)
        w[s: s + len(b)] += b[: len(w) - s] * (0.3 + 0.7 * min(1.0, tt / 1.8))
        tt += g.exponential(1.0 / (20.0 + 90.0 * min(1.0, tt / 1.6)))
    mx.add("water", w, 0.0, pan=0.0)
    t = np.arange(int(3.0 * SR)) / SR
    sh = filt(g.standard_normal(len(t)), [bq_highpass(7000, 0.7)]) * np.sin(np.pi * np.clip(t / 3.0, 0, 1)) ** 2
    mx.add("shimmer", sh, 0.6, pan=0.2)
    hall = ModFDNReverb(rt60=2.6, rt60_high=1.6, predelay=0.02, size=1.0, mod_depth=8.0, mod_rate=0.5, seed=SEED % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-2.0)[: int((LENGTH + 0.5) * SR)]
    k = int(1.2 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, y, quality=4.0)
    m = measure(y)
    if verbose:
        print(f"ilun_summon: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  Mmax {m['momentary_max_lufs']:.2f}"
              f"  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
