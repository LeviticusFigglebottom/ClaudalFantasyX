"""Monophonic virtual-analog lead (the fusion lead voice of the battle cue).

Rendered a whole phrase at a time, like a player on a mono synth:

* Pitch: a target-note step curve with exponential portamento between
  legato notes (gap < 25 ms), a short scoop into detached notes, delayed
  vibrato on notes longer than ~0.35 s, and slow drift.
* Oscillators: two detuned saw+square blends, built additively (so they are
  alias-free at any pitch).
* Filter: a resonant 4-pole low-pass applied *per harmonic* from its
  analytic magnitude response, with a per-note envelope on cutoff. Doing the
  filter spectrally keeps it fully vectorized and click-free while the
  cutoff and pitch move.
* Amplitude: per-note attack/decay/sustain, retriggered on detached notes,
  continuous across legato.
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, midi_to_hz, rng, smooth_noise


def _lp4_mag(f: np.ndarray, fc: np.ndarray, q: float) -> np.ndarray:
    x = f / fc
    h2 = 1.0 / np.sqrt((1 - x * x) ** 2 + (x / q) ** 2)
    return h2 * h2


def lead_phrase(notes: list[tuple[float, float, float, float]], sr: int = SR, seed: int = 0,
                glide: float = 0.035, vib_cents: float = 22.0, vib_rate: float = 5.6, saw_mix: float = 0.65,
                detune_cents: float = 7.0, cutoff: float = 1800.0, env_amt: float = 2.2, q: float = 1.3,
                dec: int = 16) -> np.ndarray:
    """notes: [(start_s, dur_s, midi, vel)], times relative to the phrase. Returns mono."""
    g = rng(seed)
    notes = sorted(notes)
    end = max(s + d for s, d, _, _ in notes) + 0.4
    N = int(end * sr)
    nd = N // dec + 2
    td = np.arange(nd) * dec / sr

    target = np.full(nd, np.nan)
    amp = np.zeros(nd)
    fenv = np.zeros(nd)
    vib_amt = np.zeros(nd)
    vel_curve = np.zeros(nd)
    prev_end = -1.0
    for i, (s, d, m, v) in enumerate(notes):
        a, b = int(s * sr / dec), int((s + d) * sr / dec)
        target[a:] = m
        legato = s - prev_end < 0.025
        tt = td[a:] - s
        if not legato:
            env = np.minimum(1.0, tt / 0.008) * (0.82 + 0.18 * np.exp(-tt / 0.2))
            amp[a:] = env
            fenv[a:] = np.exp(-tt / 0.22)
            # scoop up into detached notes
            target[a: a + int(0.05 * sr / dec)] = m - 0.6 * np.exp(-tt[: int(0.05 * sr / dec)] / 0.02)
        else:
            fenv[a:] = 0.35 * np.exp(-tt / 0.15)
        vel_curve[a:] = v
        if d > 0.35:
            vib_amt[a:b] = np.clip((tt[: b - a] - 0.22) / 0.35, 0, 1)
        nxt = notes[i + 1][0] if i + 1 < len(notes) else None
        if nxt is None or nxt - (s + d) >= 0.025:
            r = td[b:] - (s + d)
            amp[b:] *= np.exp(-np.maximum(r, 0) / 0.06)
        prev_end = s + d
    target = np.where(np.isnan(target), notes[0][2], target)
    # portamento: one-pole slew toward the target (in semitones), on the slow grid
    a_g = np.exp(-dec / (glide * sr))
    pitch = np.empty(nd)
    p = target[0]
    for i in range(nd):
        p = a_g * p + (1 - a_g) * target[i]
        pitch[i] = p
    vib = vib_cents / 100.0 * vib_amt * np.sin(2 * np.pi * vib_rate * td + g.uniform(0, 6.28))
    pitch = pitch + vib + 0.04 * smooth_noise(nd, 0.8, g, sr / dec)
    f0d = midi_to_hz(69) * 2 ** ((pitch - 69) / 12)
    fcd = cutoff * (0.8 + 0.5 * vel_curve) * (1 + env_amt * fenv) * (f0d / 440.0) ** 0.3
    fcd = np.minimum(fcd, 14000.0)

    t = np.arange(N)
    f0 = np.interp(t, np.arange(nd) * dec, f0d)
    out = np.zeros(N)
    for vi, det in enumerate((-detune_cents, detune_cents)):
        ratio = 2 ** (det / 1200)
        ph = 2 * np.pi * np.cumsum(f0 * ratio) / sr + g.uniform(0, 6.28)
        kmax = int(min(80, 16000.0 / max(f0d.min(), 30.0)))
        for k in range(1, kmax + 1):
            fk_d = f0d * ratio * k
            if fk_d.min() > 16000:
                break
            c = saw_mix / k + (1 - saw_mix) * ((1.0 / k) if k % 2 else 0.0)
            a_k = c * _lp4_mag(fk_d, fcd, q) * (fk_d < 0.45 * sr)
            out += np.interp(t, np.arange(nd) * dec, a_k) * np.sin(k * ph)
    out *= np.interp(t, np.arange(nd) * dec, amp * (0.5 + 0.5 * vel_curve))
    k2 = int(0.02 * sr)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.12 * out
