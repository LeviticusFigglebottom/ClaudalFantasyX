"""Water drips: a falling drop's splash plus the bubble it entrains.

Most of the "plink" of a drip into a pool is a small air bubble ringing at
its Minnaert frequency, f = sqrt(3 gamma p0 / rho) / (2 pi r) ~ 3.26 / r Hz
(r in metres), with damping that grows with frequency and a pitch that
rises as the bubble nears the surface (van den Doel, "Physically based
models for liquid sounds", 2005). Each drip = a 1-2 ms splash transient +
one main bubble (+ sometimes a smaller secondary bubble a few ms later).
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_bandpass, filt, rng


def bubble(radius_mm: float, amp: float = 1.0, rise: float = 0.10, sr: int = SR) -> np.ndarray:
    r = radius_mm / 1000.0
    f0 = 3.26 / r
    d = 0.043 * f0 + 0.0014 * f0 ** 1.5            # damping, 1/s (van den Doel's fit)
    T = min(0.4, 9.0 / d)
    N = int(T * sr)
    t = np.arange(N) / sr
    f = f0 * (1.0 + rise * d * t)                   # rising chirp
    ph = 2 * np.pi * np.cumsum(f) / sr
    return amp * np.exp(-d * t) * np.sin(ph) * np.minimum(1.0, t / 0.0004)


def drip(vel: float = 0.6, radius_mm: float = 2.5, seed: int = 0, sr: int = SR) -> np.ndarray:
    g = rng(seed)
    r = radius_mm * g.uniform(0.85, 1.15)
    main = bubble(r, 1.0, rise=g.uniform(0.06, 0.14), sr=sr)
    out = np.zeros(len(main) + int(0.03 * sr))
    s = int(g.uniform(0.0005, 0.002) * sr)
    out[s: s + len(main)] += main
    if g.random() < 0.45:
        sec = bubble(r * g.uniform(0.35, 0.6), g.uniform(0.2, 0.45), rise=0.1, sr=sr)
        s2 = s + int(g.uniform(0.004, 0.02) * sr)
        out[s2: s2 + len(sec)] += sec[: len(out) - s2]
    nn = int(0.002 * sr)
    splash = filt(g.standard_normal(nn), [bq_bandpass(5000, 0.7, sr)], sr=sr) * np.linspace(1, 0, nn) ** 2
    out[:nn] += 0.25 * splash
    k = min(len(out) // 4, int(0.01 * sr))
    out[-k:] *= np.linspace(1, 0, k)
    return 0.3 * vel * out
