"""Formant voices: the Order's hummed congregation and a sung cantor line.

Source-filter synthesis (the cascade-formant idea of Klatt's synthesizer),
done per harmonic so it stays vectorized:

* **Source.** A glottal spectrum built additively: harmonic k at k^-tilt
  (soft phonation ~ -12 dB/oct), with jitter (fast pitch noise), slow
  drift, an irregular vibrato, shimmer, and aspiration noise.
* **Tract.** The magnitude response of 5 cascaded formant resonators
  (each unity gain at DC, |H| = F^2 / sqrt((F^2 - f^2)^2 + (f B)^2)) is
  evaluated at each harmonic's moving frequency, on a decimated grid, and
  interpolated. Formant targets glide between phonemes, so syllables
  connect the way speech does.
* **Nasals and the hum.** /m/ and /n/ close the mouth: a low nasal formant
  (~250 Hz), a nasal anti-resonance (a spectral zero near 1 kHz for /m/,
  1.6 kHz for /n/), and a strongly damped upper spectrum. The congregation
  hum is a closed-mouth /m/.
* **Ensemble.** `hum_ensemble` renders many independent voices (pitch
  scatter of several cents, staggered entries, staggered breaths so the
  sound never stops all at once, and per-voice distance colouring), at a
  reduced internal sample rate (the hum has nothing above ~3 kHz) and
  upsamples once.

The cantor line is optional colour: a synthesized singing voice is the
element most likely to sound uncanny, so it is mixed distant and low.
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, midi_to_hz, rng, smooth_noise

# formant tables (F1..F5 Hz, B1..B5 Hz), adult male; "f" variants scale for higher voices
VOWELS = {
    "a": ((730, 1090, 2440, 3400, 4500), (80, 90, 120, 180, 250)),
    "e": ((530, 1840, 2480, 3400, 4500), (60, 100, 120, 180, 250)),
    "i": ((290, 2250, 3000, 3500, 4500), (50, 90, 140, 200, 250)),
    "o": ((570, 840, 2410, 3400, 4500), (70, 80, 110, 180, 250)),
    "u": ((320, 870, 2240, 3400, 4500), (60, 80, 110, 180, 250)),
    "m": ((260, 1100, 2200, 3300, 4400), (90, 300, 350, 400, 450)),
    "n": ((260, 1500, 2500, 3300, 4400), (90, 250, 300, 400, 450)),
}
NASAL_ZERO = {"m": 1000.0, "n": 1600.0}


def _formant_mag(f: np.ndarray, F: np.ndarray, Bw: np.ndarray) -> np.ndarray:
    """Cascade of unity-DC-gain resonators at frequencies f (H x T) for formants F, B (5 x T)."""
    out = np.ones_like(f)
    for i in range(F.shape[0]):
        Fi = F[i][None, :]
        Bi = Bw[i][None, :]
        out *= Fi ** 2 / np.sqrt((Fi ** 2 - f ** 2) ** 2 + (f * Bi) ** 2)
    return out


def _zero_mag(f: np.ndarray, Fz: np.ndarray, depth: np.ndarray, bw: float = 180.0) -> np.ndarray:
    """A soft spectral notch (anti-resonance), depth 0..1."""
    x = (f - Fz[None, :]) / bw
    return 1.0 - depth[None, :] * 0.92 / (1.0 + x * x)


def sing(phonemes: list[tuple[str, float]], pitches: list[tuple[float, float]], vel: float = 0.6, seed: int = 0,
         sr: int = SR, scale: float = 1.0, tilt: float = 1.9, breath: float = 0.06, vib_cents: float = 18.0,
         vib_rate: float = 5.0, jitter_cents: float = 4.0, max_f: float = 6000.0, dec: int = 32,
         release: float = 0.25) -> np.ndarray:
    """One voice. phonemes = [(symbol, seconds)], pitches = [(midi, seconds)] (lengths should match in total).

    scale > 1 raises the formants (shorter tract: alto/soprano ~ 1.15-1.2).
    """
    g = rng(seed)
    total = sum(d for _, d in phonemes)
    N = int((total + release * 3) * sr)
    nd = N // dec + 2
    td = np.arange(nd) * dec / sr

    # pitch curve: steps with ~80 ms glides, drift, jitter, irregular delayed vibrato
    pt = np.zeros(nd)
    edges = np.cumsum([0.0] + [d for _, d in pitches])
    for (m, _), a, b in zip(pitches, edges[:-1], edges[1:]):
        pt[(td >= a)] = m
    k = max(1, int(0.08 * sr / dec))
    pt = np.convolve(np.concatenate([np.full(k, pt[0]), pt]), np.ones(k) / k, mode="same")[k:]
    vib_on = np.clip((td - 0.4) / 0.8, 0, 1)
    vib = vib_cents / 100 * vib_on * np.sin(2 * np.pi * np.cumsum(vib_rate * (1 + 0.1 * smooth_noise(nd, 0.6, g, sr / dec)))
                                            * dec / sr)
    pt = pt + vib + 0.06 * smooth_noise(nd, 0.3, g, sr / dec) + jitter_cents / 100 * smooth_noise(nd, 18.0, g, sr / dec)
    f0d = 440.0 * 2 ** ((pt - 69) / 12)

    # formant tracks with smooth transitions (~60 ms)
    Fd = np.zeros((5, nd))
    Bd = np.zeros((5, nd))
    zero_f = np.full(nd, 1000.0)
    zero_d = np.zeros(nd)
    amp = np.zeros(nd)
    e2 = np.cumsum([0.0] + [d for _, d in phonemes])
    for (ph, _), a, b in zip(phonemes, e2[:-1], e2[1:]):
        m = (td >= a) & (td < b + (release if b == e2[-1] else 0.0))
        F, Bw = VOWELS["m" if ph == "hum" else ph] if ph in VOWELS or ph == "hum" else VOWELS["a"]
        Fd[:, m] = np.array(F)[:, None] * scale
        Bd[:, m] = np.array(Bw)[:, None]
        nz = "m" if ph == "hum" else ph
        if nz in NASAL_ZERO:
            zero_f[m] = NASAL_ZERO[nz] * scale
            zero_d[m] = 1.0
        amp[m] = 0.55 if ph in ("m", "n", "hum") else 1.0
    k = max(1, int(0.06 * sr / dec))
    ker = np.ones(k) / k
    for arr in (Fd, Bd):
        for i in range(5):
            arr[i] = np.convolve(np.pad(arr[i], (k, k), mode="edge"), ker, mode="same")[k:-k]
    zero_d = np.convolve(np.pad(zero_d, (k, k), mode="edge"), ker, mode="same")[k:-k]
    zero_f = np.convolve(np.pad(zero_f, (k, k), mode="edge"), ker, mode="same")[k:-k]
    # breath-phrase envelope: soft onset, release at the end
    env = np.clip(td / 0.12, 0, 1) * np.where(td > total, np.exp(-(td - total) / (release / 2.5)), 1.0)
    env *= 1 + 0.06 * smooth_noise(nd, 1.5, g, sr / dec)        # shimmer
    amp = np.convolve(np.pad(amp, (k, k), mode="edge"), ker, mode="same")[k:-k] * env

    K = int(min(64, max_f / max(f0d.min(), 40.0)))
    kk = np.arange(1, K + 1, dtype=np.float64)[:, None]
    fk = kk * f0d[None, :]
    src = kk ** -tilt
    mag = src * _formant_mag(fk, Fd, Bd) * _zero_mag(fk, zero_f, zero_d) * (fk < min(max_f, 0.45 * sr))
    t = np.arange(N)
    f0 = np.interp(t, np.arange(nd) * dec, f0d)
    ph = 2 * np.pi * np.cumsum(f0) / sr
    out = np.zeros(N)
    grid = np.arange(nd) * dec
    for i in range(K):
        if not mag[i].any():
            continue
        out += np.interp(t, grid, mag[i] * amp) * np.sin((i + 1) * ph + g.uniform(0, 6.28))
    # aspiration: noise shaped by the upper formants, stronger on open vowels
    if breath > 0:
        nz = g.standard_normal(N)
        asp = filt(nz, [bq_bandpass(min(Fd[1].mean() * 1.2, 0.4 * sr), 0.8, sr), bq_highpass(500, 0.7, sr)], sr=sr)
        asp = asp / (np.std(asp) + 1e-9) * np.interp(t, grid, amp) * (1 + 0.5 * np.cos(ph))
        out += breath * 0.02 * asp
    k2 = min(N // 4, int(0.05 * sr))
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.1 * vel * out


def hum_ensemble(line: list[tuple[float, float]], voices: int = 14, seed: int = 0, sr: int = SR,
                 register: str = "low", spread: float = 0.8, scatter_cents: float = 9.0,
                 breath_every: tuple[float, float] = (6.0, 11.0)) -> np.ndarray:
    """A congregation humming a slow line together. line = [(midi, seconds)].

    Each voice gets its own pitch offset, entry delay, timing drift, breath
    gaps (taken at random points, so the ensemble never breathes at once) and
    a distance (darker and quieter when far). Returns stereo (N, 2)."""
    g = rng(seed)
    total = sum(d for _, d in line)
    dec_sr = 11025
    q = sr // dec_sr
    N = int((total + 1.5) * sr)
    out = np.zeros((N, 2))
    scale = 1.0 if register == "low" else 1.17
    for v in range(voices):
        offs = g.normal(0, scatter_cents) / 100.0
        delay = abs(g.normal(0, 0.12))
        # breath gaps: split the line into breath phrases of 6-11 s with 0.6-1.1 s gaps
        segs = []
        tcur = 0.0
        while tcur < total:
            seg = g.uniform(*breath_every)
            segs.append((tcur, min(total, tcur + seg)))
            tcur += seg + g.uniform(0.6, 1.1)
        dist = g.uniform(0, 1)
        lvl = 1.0 - 0.45 * dist
        pan = spread * g.uniform(-1, 1)
        xl = np.zeros(N // q + 1)          # accumulated at the reduced rate
        for a, b in segs:
            # the slice of the line inside [a, b)
            pts = []
            e = np.cumsum([0.0] + [d for _, d in line])
            for (m, _), s0, s1 in zip(line, e[:-1], e[1:]):
                lo, hi = max(a, s0), min(b, s1)
                if hi > lo:
                    pts.append((m + offs, hi - lo))
            if not pts:
                continue
            y = sing([("hum", b - a)], pts, vel=lvl, seed=int(g.integers(1 << 30)), sr=dec_sr, scale=scale,
                     tilt=2.2, breath=0.0, vib_cents=6.0 + 6 * g.random(), vib_rate=g.uniform(4.2, 5.4),
                     jitter_cents=5.0, max_f=2600.0, dec=16, release=0.6)
            s = int((a + delay) * dec_sr)
            seg_n = min(len(y), len(xl) - s)
            if seg_n > 0:
                xl[s: s + seg_n] += y[:seg_n]
        # one exact (FFT) resampling to the output rate per voice
        X = np.fft.rfft(xl)
        Xu = np.zeros(N // 2 + 1, dtype=np.complex128)
        m = min(len(X), len(Xu))
        Xu[:m] = X[:m]
        x = np.fft.irfft(Xu, N) * (N / len(xl))
        x = filt(x, [bq_lowpass(2800 - 1600 * dist, 0.7, sr)], sr=sr)
        th = (pan + 1) * np.pi / 4
        out[:, 0] += x * np.cos(th)
        out[:, 1] += x * np.sin(th)
    return out / np.sqrt(voices)
