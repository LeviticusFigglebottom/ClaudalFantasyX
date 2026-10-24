"""A cast bronze tower bell (M2-AUD-03, the Drownbell's toll motif).

A bell's partials are named by their ratio to the strike note's *prime*: the hum an octave below, the prime, the
tierce a minor third above (the minor-third tierce is what makes a bell sound like a bell, and sad), the quint,
the nominal an octave up, then a cluster of higher partials. Each is a doublet (the bell is not perfectly round),
so most beat slowly. The hum rings longest; the upper partials die fast, so the strike note (which the ear hears
near the nominal) fades into the hum. The clapper's strike is a short bright thump.
Ratios and relative decays follow typical measurements of tuned bells (Rossing, "The Science of Sound").
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_bandpass, bq_lowpass, filt, midi_to_hz, rng

# (name, ratio to the prime, amplitude, relative T60, doublet split in Hz)
PARTIALS = [
    ("hum", 0.5, 0.80, 1.00, 0.35),
    ("prime", 1.0, 0.70, 0.62, 0.6),
    ("tierce", 1.2, 0.85, 0.48, 0.9),
    ("quint", 1.5, 0.30, 0.35, 0.0),
    ("nominal", 2.0, 0.90, 0.30, 1.3),
    ("deciem", 2.5, 0.35, 0.20, 0.0),
    ("undeciem", 2.67, 0.25, 0.18, 1.7),
    ("duodeciem", 3.0, 0.30, 0.15, 0.0),
    ("upper octave", 4.0, 0.22, 0.10, 2.2),
    ("upper 5.3", 5.33, 0.12, 0.07, 0.0),
    ("upper 6.7", 6.67, 0.08, 0.05, 0.0),
]


def tower_bell(m: float, vel: float = 0.8, seed: int = 0, t60: float = 9.0, dark: float = 0.0,
               sr: int = SR) -> np.ndarray:
    """One strike of a bell whose prime is MIDI m. t60 is the hum's; dark (0..1) softens the strike and the
    upper partials (a bell heard over water, or struck with a padded clapper). Mono."""
    g = rng(seed)
    f1 = midi_to_hz(m)
    N = int(t60 * 1.05 * sr)
    t = np.arange(N) / sr
    out = np.zeros(N)
    for _, r, a, rt, split in PARTIALS:
        f = f1 * r * (1 + g.uniform(-0.002, 0.002))
        if f > 0.45 * sr:
            continue
        T = t60 * rt
        bright = (0.55 + 0.45 * vel) ** max(0.0, r - 1.0) * (1.0 - dark) ** max(0.0, r - 1.5)
        mode = np.sin(2 * np.pi * f * t + g.uniform(0, 6.28))
        if split > 0:
            mode = 0.5 * (mode + np.sin(2 * np.pi * (f + split) * t + g.uniform(0, 6.28)))
        out += a * bright * np.exp(-6.91 * t / T) * mode
    nn = int(0.012 * sr)
    strike = filt(g.standard_normal(nn), [bq_bandpass(f1 * 4.0, 0.8, sr), bq_lowpass(9000 * (1 - 0.7 * dark), 0.7, sr)],
                  sr=sr)
    out[:nn] += 0.5 * vel * (1 - 0.6 * dark) * strike / (np.abs(strike).max() + 1e-9) * np.exp(-np.arange(nn) / sr / 0.003)
    out *= np.minimum(1.0, t / 0.0008)
    k = int(0.1 * sr)
    out[-k:] *= np.linspace(1, 0, k) ** 2
    return out / (np.abs(out).max() + 1e-9) * vel
