"""Gamelan-like metallophone: inharmonic modal bars in beating pairs.

Each note is two bars (a "pair", like the paired instruments of a Balinese
ensemble): the second bar is tuned a fixed number of Hz higher, so the pair
beats at `ombak_hz` (the shimmer). Each bar has four inharmonic modes
(free-bar-like ratios) with their own decays, plus a tube-resonator
"bloom" that reinforces the fundamental a few ms after the strike, and a
mallet click whose level follows mallet hardness.
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_highpass, filt, midi_to_hz, rng

MODE_RATIOS = (1.0, 2.76, 5.40, 8.93)


def metallophone_note(m: float, vel: float = 0.6, seed: int = 0, sr: int = SR,
                      decay: float = 4.5, hardness: float = 0.5, ombak_hz: float = 5.5,
                      damp_at: float | None = None, pair: bool = True) -> np.ndarray:
    """decay = fundamental T60 in seconds; damp_at = optional hand-damp time (s)."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    h = float(np.clip(hardness, 0, 1))
    amps = np.array([1.0, 0.45 * h + 0.08, 0.22 * h * h + 0.02, 0.10 * h ** 3])
    t60 = np.array([decay, decay * 0.32, decay * 0.13, decay * 0.06])
    length = decay * 1.05 if damp_at is None else min(decay * 1.05, damp_at + 0.5)
    N = int(length * sr)
    t = np.arange(N) / sr
    out = np.zeros(N)
    bars = [(0.0, 1.0)] + ([(ombak_hz / f0, 0.85)] if pair else [])
    for rel, bamp in bars:
        for k, r in enumerate(MODE_RATIOS):
            f = f0 * (1 + rel) * r * (1 + g.uniform(-0.004, 0.004) * (k > 0))
            if f > 0.45 * sr:
                continue
            env = np.exp(-6.91 * t / t60[k])
            out += bamp * amps[k] * env * np.sin(2 * np.pi * f * t + g.uniform(0, 2 * np.pi))
        # resonator bloom on the fundamental (slow attack, long decay)
        bloom = (1 - np.exp(-t / 0.035)) * np.exp(-6.91 * t / (decay * 1.15))
        out += bamp * 0.35 * bloom * np.sin(2 * np.pi * f0 * (1 + rel) * t + g.uniform(0, 2 * np.pi))
    # mallet click
    nc = int(0.006 * sr)
    click = filt(g.standard_normal(nc), [bq_highpass(2500, 0.7, sr)], sr=sr)
    out[:nc] += (0.05 + 0.25 * h) * click * np.exp(-np.arange(nc) / sr / 0.0012)
    out *= np.minimum(1.0, t / 0.0008 + 0.0)  # tiny anti-click on the attack
    if damp_at is not None:
        ds = int(damp_at * sr)
        if ds < N:
            out[ds:] *= np.exp(-(t[ds:] - damp_at) / 0.07)
    k = min(N // 4, int(0.08 * sr))
    out[-k:] *= np.linspace(1, 0, k) ** 2
    return 0.22 * vel ** 1.3 * out
