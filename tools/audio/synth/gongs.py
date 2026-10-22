"""Gongs: a large hanging gong (gong-ageng-like) and small kettle gongs.

Bossed gongs have a strong, nearly harmonic low partial set (the boss
tunes them), but real ones show (a) closely spaced mode pairs that beat
slowly (the "wave" players listen for), (b) a slow amplitude bloom after
the strike as energy flows from the strike point into the low modes, and
(c) a slight downward pitch glide while the amplitude is high (a
stiffening nonlinearity). All three are modelled; kettle gongs are the
same idea, small and short.
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_lowpass, filt, midi_to_hz, rng

# (ratio, amplitude, relative T60, pair split in Hz)
LARGE = [(1.0, 1.0, 1.0, 0.55), (2.01, 0.45, 0.6, 0.9), (2.97, 0.25, 0.42, 1.3), (3.62, 0.12, 0.3, 0.0),
         (4.43, 0.10, 0.25, 1.9), (5.38, 0.06, 0.18, 0.0), (6.12, 0.04, 0.15, 0.0)]
KETTLE = [(1.0, 1.0, 1.0, 1.6), (1.52, 0.30, 0.45, 0.0), (2.04, 0.35, 0.5, 2.4), (2.71, 0.12, 0.3, 0.0),
          (3.33, 0.10, 0.22, 0.0), (4.12, 0.05, 0.16, 0.0)]


def _gong(f0: float, modes, t60: float, vel: float, bloom: float, glide: float, length: float,
          g: np.random.Generator, sr: int) -> np.ndarray:
    N = int(length * sr)
    t = np.arange(N) / sr
    out = np.zeros(N)
    gl = 1.0 - glide * vel * np.exp(-t / 0.6)
    ph = 2 * np.pi * np.cumsum(gl) / sr
    for r, a, rt, split in modes:
        f = f0 * r * (1 + g.uniform(-0.003, 0.003))
        if f > 0.45 * sr:
            continue
        T = t60 * rt
        env = np.exp(-6.91 * t / T) * (1 - np.exp(-t / bloom)) if r < 1.5 else np.exp(-6.91 * t / T)
        mode = np.sin(f * ph + g.uniform(0, 6.28))
        if split > 0:
            mode = 0.5 * (mode + np.sin((f + split) * ph + g.uniform(0, 6.28)))
        out += a * (0.6 + 0.4 * vel) ** (r - 1) * env * mode
    nn = int(0.03 * sr)
    out[:nn] += 0.15 * vel * filt(g.standard_normal(nn), [bq_lowpass(1800, 0.7, sr)], sr=sr) * np.exp(
        -np.arange(nn) / sr / 0.006)
    out *= np.minimum(1.0, t / 0.002)
    k = int(0.1 * sr)
    out[-k:] *= np.linspace(1, 0, k) ** 2
    return out / (np.abs(out).max() + 1e-9) * vel


def large_gong(m: float = 28.0, vel: float = 0.8, seed: int = 0, t60: float = 9.0, sr: int = SR) -> np.ndarray:
    g = rng(seed)
    return _gong(midi_to_hz(m), LARGE, t60, vel, bloom=0.08, glide=0.006, length=t60 * 1.05, g=g, sr=sr)


def kettle_gong(m: float, vel: float = 0.6, seed: int = 0, t60: float = 1.6, damp_at: float | None = None,
                sr: int = SR) -> np.ndarray:
    g = rng(seed)
    x = _gong(midi_to_hz(m), KETTLE, t60, vel, bloom=0.004, glide=0.002, length=t60 * 1.05, g=g, sr=sr)
    if damp_at is not None:
        t = np.arange(len(x)) / sr
        x = np.where(t > damp_at, x * np.exp(-(t - damp_at) / 0.05), x)
    return 0.6 * x
