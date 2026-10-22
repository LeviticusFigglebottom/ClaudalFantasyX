"""Breathy flute: harmonic core + noise-excited bore resonator.

This is a simplified waveguide: instead of the full jet/bore loop with a
cubic jet nonlinearity (which is hard to keep in tune without per-sample
Python), the breath is white noise driven through a tuned feedback comb
(the bore: a delay line with a lossy interpolating reflection), which turns
the noise into pitched, airy "breath tone". A soft additive harmonic core
supplies the stable pitch, with delayed vibrato, an attack pitch scoop, and
a "chiff" transient.
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, feedback_comb, filt, midi_to_hz, rng, smooth_noise

HARM = (1.0, 0.38, 0.14, 0.07, 0.035, 0.02)


def flute_note(m: float, dur: float, vel: float = 0.5, seed: int = 0, sr: int = SR,
               breath: float = 0.30, vib_rate: float = 4.8, vib_cents: float = 14.0,
               attack: float = 0.09, release: float = 0.22) -> np.ndarray:
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int((dur + release * 2.6 + 0.03) * sr)
    t = np.arange(N) / sr

    # amplitude envelope: soft swell with a small overshoot, then release
    env = np.where(t < attack, (t / attack) ** 1.5, 1.0)
    env *= 1 + 0.08 * np.exp(-np.maximum(t - attack, 0) / 0.12) * (t >= attack)
    env *= 1 + 0.04 * smooth_noise(N, 2.5, g, sr)                 # breath unsteadiness
    rel = t > dur
    env[rel] *= np.exp(-(t[rel] - dur) / (release / 3))

    # pitch: scoop from -25 cents into the note, delayed vibrato
    vib_depth = vib_cents * np.clip((t - 0.25) / 0.5, 0, 1)
    cents = -25 * np.exp(-t / 0.035) + vib_depth * np.sin(2 * np.pi * vib_rate * t + g.uniform(0, 6.28))
    cents += 3 * smooth_noise(N, 1.3, g, sr)
    freq = f0 * 2 ** (cents / 1200)
    phase = 2 * np.pi * np.cumsum(freq) / sr
    bright = 0.6 + 0.6 * vel
    core = np.zeros(N)
    for k, a in enumerate(HARM, start=1):
        if f0 * k > 0.45 * sr:
            break
        core += a * bright ** (k - 1) * np.sin(k * phase + g.uniform(0, 6.28))
    # amplitude tremolo that goes with the vibrato (real flutes do this)
    core *= 1 + 0.06 * (vib_depth / max(vib_cents, 1e-6)) * np.sin(2 * np.pi * vib_rate * t)

    # breath through the bore resonator (pitched noise) + raw air
    noise = g.standard_normal(N)
    bore = feedback_comb(noise * 0.05, sr / f0, 0.965)
    bore = filt(bore, [bq_highpass(f0 * 0.8, 0.7, sr), bq_lowpass(6500, 0.7, sr)], sr=sr)
    air = filt(noise, [bq_bandpass(min(4000 + f0, 0.4 * sr), 0.6, sr)], sr=sr)
    bore /= (np.std(bore) + 1e-9)
    air /= (np.std(air) + 1e-9)

    # chiff: a short noisy burst around the 2nd-3rd harmonic at the onset
    chiff = filt(noise, [bq_bandpass(min(2.5 * f0, 0.4 * sr), 2.0, sr)], sr=sr)
    chiff = chiff / (np.std(chiff) + 1e-9) * np.exp(-t / 0.025) * (1 - np.exp(-t / 0.004))

    y = env * (0.55 * core + breath * (0.35 * bore + 0.12 * air)) + 0.10 * vel * chiff
    k = int(0.03 * sr)
    y[-k:] *= np.linspace(1, 0, k)
    return 0.18 * vel ** 0.8 * y
