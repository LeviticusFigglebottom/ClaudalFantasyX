"""Soft string pad: a small "section" of detuned band-limited saws per note.

Each voice is a polyBLEP sawtooth with its own slow random pitch drift
(players never agree on pitch), a tiny vibrato, and its own stereo position.
The sum is filtered at the bus level by `string_body` (a darkening low-pass
plus broad body resonances), which is what turns raw saws into something
string-like rather than synth-like.
"""
from __future__ import annotations

import numpy as np

from .dsp import (SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, pan_mono, polyblep_saw,
                  rng, smooth_noise)


def pad_chord(notes, dur: float, vel: float = 0.5, seed: int = 0, sr: int = SR,
              voices: int = 4, spread_cents: float = 9.0, attack: float = 1.2,
              release: float = 1.8, width: float = 0.8) -> np.ndarray:
    """notes: iterable of MIDI pitches. Returns stereo (N, 2)."""
    g = rng(seed)
    N = int((dur + release * 3.0) * sr)
    t = np.arange(N) / sr
    env = np.clip(t / attack, 0, 1) ** 2 * (3 - 2 * np.clip(t / attack, 0, 1))  # smoothstep swell
    rel = t > dur
    env[rel] *= np.exp(-(t[rel] - dur) / (release / 2.5))
    out = np.zeros((N, 2))
    notes = list(notes)
    for ni, m in enumerate(notes):
        f0 = midi_to_hz(m)
        for v in range(voices):
            off = spread_cents * ((v / max(voices - 1, 1)) * 2 - 1) if voices > 1 else 0.0
            drift = 3.0 * smooth_noise(N, 0.4 + 0.2 * g.random(), g, sr)
            vib = 4.0 * np.sin(2 * np.pi * (5.0 + g.uniform(-0.4, 0.4)) * t + g.uniform(0, 6.28))
            freq = f0 * 2 ** ((off + drift + vib * np.clip(t / 1.5, 0, 1)) / 1200)
            s = polyblep_saw(freq, sr, g.random())
            pan = width * (((v + ni) % voices) / max(voices - 1, 1) * 2 - 1)
            out += pan_mono(s, pan)
    k = int(0.05 * sr)
    env[-k:] *= np.linspace(1, 0, k)
    out *= (env * 0.08 * vel / np.sqrt(voices * len(notes)))[:, None]
    return out


def string_body(x: np.ndarray, sr: int = SR, cutoff: float = 2200.0) -> np.ndarray:
    """Bus filter for the pad: removes the buzzy saw top and adds body."""
    return filt(x, [bq_highpass(90, 0.7, sr), bq_lowpass(cutoff, 0.6, sr), bq_lowpass(cutoff * 1.6, 0.7, sr),
                    bq_peak(420, 3.0, 1.1, sr), bq_peak(1250, 2.0, 1.3, sr), bq_peak(3200, -3, 0.9, sr)], sr=sr)
