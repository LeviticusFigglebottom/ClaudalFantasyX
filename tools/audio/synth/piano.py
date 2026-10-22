"""Additive / modal piano approximation.

Per note:
* Stiff-string partials f_n = n f0 sqrt(1 + B n^2) with pitch-dependent
  inharmonicity B (stretched upper partials).
* Spectral envelope from the hammer: strike-position comb |sin(pi n p)|,
  a velocity-dependent brightness low-pass (harder hits excite more partials),
  and a gentle 1/n^k tilt.
* Two strings per note, detuned by a fraction of a cent: partial n beats at
  ~n * detune, which is what makes a sustained piano tone shimmer.
* Two-stage decay per partial (fast "prompt sound" + slow "aftersound"), with
  higher partials decaying faster.
* Dampers: after key-up (or pedal-up) each partial is damped with a short,
  frequency-dependent time constant; bass dampers are slower.
* Hammer noise: a short band-passed noise burst plus a low "thump".

A soundboard-ish body is applied once per bus (see `soundboard_ir`) rather
than per note, to save CPU.
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_bandpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng


def inharmonicity(m: float) -> float:
    return 0.5 * 10 ** (-4.0 + 1.9 * (m - 21) / 87.0)


def piano_note(m: float, vel: float, hold: float, seed: int = 0, sr: int = SR,
               brightness: float = 1.0) -> np.ndarray:
    """Render one piano note.

    m      MIDI pitch (may be fractional)
    vel    0..1 key velocity
    hold   seconds until the damper falls (key-up, or pedal-up if later)
    Returns a mono float64 array (attack at index 0).
    """
    g = rng(seed)
    f0 = midi_to_hz(m)
    nyq = sr / 2
    B = inharmonicity(m)
    cap = int(np.clip(56 - (m - 21) * 0.55, 8, 48))
    n = np.arange(1, cap + 1)
    fn = n * f0 * np.sqrt(1 + B * n * n)
    keep = fn < min(0.45 * sr, 11000.0)
    n, fn = n[keep], fn[keep]

    p = 1.0 / 8.5 + g.uniform(-0.004, 0.004)          # strike position along the string
    comb = np.abs(np.sin(np.pi * n * p)) + 0.06
    fc = (700 + 5200 * vel ** 1.7) * brightness        # hammer felt gets harder with velocity
    amp = comb * n ** -0.75 / (1 + (fn / fc) ** 2.2)
    amp /= np.sqrt(np.sum(amp ** 2))
    amp *= 0.35 * vel ** 1.6

    t60_f = float(np.clip(15.0 * 2.0 ** (-(m - 36) / 15.0), 1.3, 16.0))
    t60 = t60_f / (1 + (fn / 1300.0) ** 1.35)
    tau_slow = t60 / 6.91
    tau_fast = tau_slow * 0.22
    after = 0.14  # aftersound share, about -17 dB

    reg = np.clip((m - 21) / 87.0, 0, 1)
    tau_d = (0.05 + 0.30 * (1 - reg) ** 2) / (1 + fn / 2500.0)  # damper time constants

    hold = max(hold, 0.03)
    # length: until the slowest partial is ~-70 dB after the damper, or natural decay
    nat = 7.0 * tau_slow.max()
    total = min(hold + 10.0 * tau_d.max(), nat) + 0.02
    N = int(total * sr)
    t = np.arange(N) / sr
    hs = int(hold * sr)

    out = np.zeros(N)
    det = g.uniform(0.35, 1.4) * (1 if g.random() < 0.5 else -1)  # cents
    attack = 1 - np.exp(-t / 0.0012)
    for k in range(len(n)):
        # samples needed for this partial (stop at ~-80 dB)
        need_nat = int(min(N, tau_slow[k] * np.log(max(amp[k], 1e-9) / 1e-5) * sr) if amp[k] > 1e-5 else 0)
        need = min(N, max(need_nat, 1))
        if need < 32:
            continue
        need_d = hs + int(10 * tau_d[k] * sr)
        need = min(need, max(need_d, 1))
        tt = t[:need]
        env = (1 - after) * np.exp(-tt / tau_fast[k]) + after * np.exp(-tt / tau_slow[k])
        if need > hs:
            env[hs:] *= np.exp(-(tt[hs:] - hold) / tau_d[k])
        env *= attack[:need]
        ph1, ph2 = g.uniform(0, 2 * np.pi, 2)
        d = 2 ** (det * (0.6 + 0.4 * g.random()) / 1200.0)
        s1 = np.sin(2 * np.pi * fn[k] * tt + ph1)
        s2 = 0.92 * np.sin(2 * np.pi * fn[k] * d * tt + ph2)
        out[:need] += amp[k] * env * (s1 + s2) * 0.5

    # hammer contact noise + thump
    nh = int(0.035 * sr)
    th = np.arange(nh) / sr
    noise = g.standard_normal(nh)
    click = filt(noise, [bq_bandpass(1100 + 2600 * vel, 0.8, sr)], sr=sr) * np.exp(-th / 0.004)
    thump = filt(noise, [bq_bandpass(110 + 0.6 * f0 if f0 < 400 else 220, 1.2, sr)], sr=sr) * np.exp(-th / 0.012)
    out[:nh] += (0.010 * click + 0.016 * thump) * vel ** 1.4
    return out


def soundboard_ir(sr: int = SR, seed: int = 88, length: float = 0.09) -> np.ndarray:
    """A short synthetic body response: decaying noise shaped by a few broad
    resonances. Convolved with the piano bus at a modest wet level."""
    g = rng(seed)
    n = int(length * sr)
    t = np.arange(n) / sr
    ir = g.standard_normal(n) * np.exp(-t / 0.018)
    ir = filt(ir, [bq_peak(180, 6, 1.4, sr), bq_peak(520, 3, 1.2, sr), bq_peak(2400, -4, 0.8, sr),
                   bq_lowpass(5200, 0.7, sr)], sr=sr)
    ir /= np.sqrt(np.sum(ir ** 2))
    ir[0] += 1.0  # direct path
    return ir / np.sqrt(2.0)
