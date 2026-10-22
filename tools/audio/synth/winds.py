"""Breath flute (end-blown, shakuhachi-like in spirit, not in repertoire).

Improvements over `flute.py` (which stays frozen for the M1 sketch):

* **Pressure-dependent spectrum.** A breath-pressure envelope P(t) drives
  both loudness and brightness: harmonic k scales as P^(beta (k - 1)), so
  swells brighten the tone the way overblowing a real jet does.
* **Pulsed jet turbulence.** The breath noise is amplitude-modulated in
  sync with the oscillation phase (turbulence is shed once per cycle). This
  is what makes real flute noise sound *attached* to the tone instead of
  layered on top of it.
* **Bore-tuned breath.** Some noise also goes through a feedback comb tuned
  to the note, which gives the pitched "air" of a wide bore.
* **Articulation.** A breath burst that precedes the tone by tens of ms, a
  pitch scoop from below (meri-style), a delayed and slightly irregular
  vibrato, optional mid-note swell, and a release where the tone dies
  faster than the breath.
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, feedback_comb, filt, midi_to_hz, rng, smooth_noise

HARM = (1.0, 0.42, 0.20, 0.11, 0.06, 0.035, 0.02, 0.012)


def breath_flute(m: float, dur: float, vel: float = 0.5, seed: int = 0, sr: int = SR, breath: float = 0.35,
                 scoop_cents: float = 45.0, vib_cents: float = 16.0, vib_rate: float = 4.6,
                 swell: float = 0.0, attack: float = 0.12, release: float = 0.35, beta: float = 0.55) -> np.ndarray:
    """Mono note. `swell` > 0 adds a mid-note crescendo (fraction of level)."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    pre = 0.05 + 0.03 * g.random()                    # breath precedes the tone
    N = int((pre + dur + release * 2.5 + 0.05) * sr)
    t = np.arange(N) / sr
    tn = t - pre                                       # tone time

    # breath pressure envelope
    P = np.clip(tn / attack, 0, 1) ** 1.3
    if swell > 0:
        x = np.clip(tn / max(dur, 1e-3), 0, 1)
        P *= 1 + swell * np.sin(np.pi * x) ** 2
    P *= 1 + 0.05 * smooth_noise(N, 3.0, g, sr)
    rel = tn > dur
    P[rel] *= np.exp(-(tn[rel] - dur) / (release / 2.2))
    P[tn < 0] = 0.0
    P = np.maximum(P, 0.0)

    # pitch: scoop up into the note, delayed irregular vibrato, slow wander
    vib_on = np.clip((tn - 0.35) / 0.6, 0, 1)
    vib_rate_t = vib_rate * (1 + 0.08 * smooth_noise(N, 0.7, g, sr))
    vib_phase = 2 * np.pi * np.cumsum(vib_rate_t) / sr
    cents = (-scoop_cents * np.exp(-np.maximum(tn, 0) / 0.06) + vib_cents * vib_on * np.sin(vib_phase)
             + 4 * smooth_noise(N, 0.9, g, sr))
    freq = f0 * 2 ** (cents / 1200)
    phase = 2 * np.pi * np.cumsum(freq) / sr

    pn = np.maximum(P, 1e-6) * (0.55 + 0.45 * vel)
    core = np.zeros(N)
    for k, a in enumerate(HARM, start=1):
        if f0 * k > 0.42 * sr:
            break
        core += a * pn ** (beta * (k - 1)) * np.sin(k * phase + g.uniform(0, 6.28))
    core *= 1 + 0.07 * vib_on * np.sin(vib_phase)       # amplitude follows the vibrato

    noise = g.standard_normal(N)
    jet = filt(noise, [bq_highpass(900, 0.7, sr), bq_lowpass(5200, 0.7, sr)], sr=sr)
    jet = jet / (np.std(jet) + 1e-9) * (1 + 0.65 * np.cos(phase))          # pulsed turbulence
    bore = feedback_comb(filt(noise, [bq_bandpass(min(3 * f0, 0.4 * sr), 0.5, sr)], sr=sr) * 0.05,
                         sr / f0, 0.955)
    bore = filt(bore, [bq_highpass(f0 * 0.8, 0.7, sr), bq_lowpass(5500, 0.7, sr)], sr=sr)
    bore /= np.std(bore) + 1e-9

    # breath envelope: starts before the tone, bursts at the attack, lingers on release
    Bv = np.clip((t) / pre, 0, 1) * np.exp(-np.maximum(tn, 0) / 0.09) * 1.4 + np.sqrt(P) * 0.6
    Bv[rel] = np.sqrt(np.maximum(P[rel], 0)) * 0.9
    y = P * core * 0.62 + breath * Bv * (0.15 * jet + 0.28 * bore)
    k = int(0.04 * sr)
    y[-k:] *= np.linspace(1, 0, k)
    return 0.2 * vel ** 0.7 * y
