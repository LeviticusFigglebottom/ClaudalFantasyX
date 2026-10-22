"""Core DSP helpers shared by every instrument and the mixer.

Pure numpy. No scipy: IIR filters are applied in the frequency domain
(exact for LTI filters up to tail truncation, which we avoid by padding),
and the few recursive structures we need (combs, allpasses, the FDN) are
processed block-wise with block length <= the shortest delay so each block
is a vectorized operation.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

SR = 44100


# --------------------------------------------------------------------------- #
# Pitch / level conversions
# --------------------------------------------------------------------------- #
def midi_to_hz(m: float) -> float:
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 20.0)


def lin_to_db(x: float) -> float:
    return 20.0 * np.log10(max(float(x), 1e-12))


def rng(seed: int) -> np.random.Generator:
    """All randomness goes through explicitly seeded generators (determinism)."""
    return np.random.default_rng(int(seed) & 0xFFFFFFFF)


# --------------------------------------------------------------------------- #
# Envelopes
# --------------------------------------------------------------------------- #
def time_axis(n: int, sr: int = SR) -> np.ndarray:
    return np.arange(n, dtype=np.float64) / sr


def adsr(n: int, a: float, d: float, s: float, r: float, gate: float, sr: int = SR,
         curve: float = 3.0) -> np.ndarray:
    """Exponential-ish ADSR. a/d/r in seconds, s level 0..1, gate = note-on length (s)."""
    t = time_axis(n, sr)
    env = np.empty(n)
    a = max(a, 1e-4)
    d = max(d, 1e-4)
    r = max(r, 1e-4)
    att = t < a
    env[att] = (1 - np.exp(-curve * t[att] / a)) / (1 - np.exp(-curve))
    dec = ~att
    env[dec] = s + (1 - s) * np.exp(-curve * (t[dec] - a) / d)
    # release starts from whatever level we were at when the gate closed
    g = int(gate * sr)
    if g < n:
        level = env[g - 1] if g > 0 else 0.0
        tr = t[g:] - gate
        env[g:] = level * np.exp(-curve * 2.0 * tr / r)
    return env


def fade(x: np.ndarray, fade_in: float = 0.0, fade_out: float = 0.0, sr: int = SR) -> np.ndarray:
    y = x.copy()
    n = len(y)
    if fade_in > 0:
        k = min(n, int(fade_in * sr))
        w = np.sin(0.5 * np.pi * np.linspace(0, 1, k)) ** 2
        y[:k] = (y[:k].T * w).T
    if fade_out > 0:
        k = min(n, int(fade_out * sr))
        w = np.cos(0.5 * np.pi * np.linspace(0, 1, k)) ** 2
        y[n - k:] = (y[n - k:].T * w).T
    return y


# --------------------------------------------------------------------------- #
# Biquad design (RBJ cookbook) and frequency-domain application
# --------------------------------------------------------------------------- #
def _w0(fc, sr):
    return 2 * np.pi * min(fc, 0.49 * sr) / sr


def bq_lowpass(fc, q=0.7071, sr=SR):
    w = _w0(fc, sr); al = np.sin(w) / (2 * q); c = np.cos(w)
    return ([(1 - c) / 2, 1 - c, (1 - c) / 2], [1 + al, -2 * c, 1 - al])


def bq_highpass(fc, q=0.7071, sr=SR):
    w = _w0(fc, sr); al = np.sin(w) / (2 * q); c = np.cos(w)
    return ([(1 + c) / 2, -(1 + c), (1 + c) / 2], [1 + al, -2 * c, 1 - al])


def bq_bandpass(fc, q=1.0, sr=SR):
    """Constant 0 dB peak gain band-pass."""
    w = _w0(fc, sr); al = np.sin(w) / (2 * q); c = np.cos(w)
    return ([al, 0.0, -al], [1 + al, -2 * c, 1 - al])


def bq_peak(fc, gain_db, q=1.0, sr=SR):
    A = 10 ** (gain_db / 40); w = _w0(fc, sr); al = np.sin(w) / (2 * q); c = np.cos(w)
    return ([1 + al * A, -2 * c, 1 - al * A], [1 + al / A, -2 * c, 1 - al / A])


def bq_highshelf(fc, gain_db, q=0.7071, sr=SR):
    A = 10 ** (gain_db / 40); w = _w0(fc, sr); al = np.sin(w) / (2 * q); c = np.cos(w)
    sa = 2 * np.sqrt(A) * al
    b = [A * ((A + 1) + (A - 1) * c + sa), -2 * A * ((A - 1) + (A + 1) * c),
         A * ((A + 1) + (A - 1) * c - sa)]
    a = [(A + 1) - (A - 1) * c + sa, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sa]
    return (b, a)


def bq_lowshelf(fc, gain_db, q=0.7071, sr=SR):
    A = 10 ** (gain_db / 40); w = _w0(fc, sr); al = np.sin(w) / (2 * q); c = np.cos(w)
    sa = 2 * np.sqrt(A) * al
    b = [A * ((A + 1) - (A - 1) * c + sa), 2 * A * ((A - 1) - (A + 1) * c),
         A * ((A + 1) - (A - 1) * c - sa)]
    a = [(A + 1) + (A - 1) * c + sa, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sa]
    return (b, a)


def _next_pow2(n: int) -> int:
    return 1 << int(np.ceil(np.log2(max(2, n))))


@lru_cache(maxsize=3)
def _unit_circle(nfft: int) -> tuple[np.ndarray, np.ndarray]:
    """z^-1 and z^-2 on the rfft grid (cached: identical values, computed once per size)."""
    k = np.arange(nfft // 2 + 1)
    z1 = np.exp(-2j * np.pi * k / nfft)
    z1.setflags(write=False)
    z2 = z1 * z1
    z2.setflags(write=False)
    return z1, z2


def freq_response(sections, nfft: int) -> np.ndarray:
    """Complex response of a cascade of (b, a) biquads on the rfft grid."""
    z1, z2 = _unit_circle(nfft)
    H = np.ones(len(z1), dtype=np.complex128)
    for b, a in sections:
        H *= (b[0] + b[1] * z1 + b[2] * z2) / (a[0] + a[1] * z1 + a[2] * z2)
    return H


def filt(x: np.ndarray, sections, tail: float = 0.25, sr: int = SR, keep_tail: bool = False) -> np.ndarray:
    """Apply a cascade of biquads (list of (b, a)) to mono (N,) or multichannel (N, C) x.

    Done as one big FFT multiply: equivalent to causal IIR filtering as long as
    the impulse response has decayed within the zero padding `tail` seconds.
    """
    if isinstance(sections, tuple):
        sections = [sections]
    n = len(x)
    pad = int(tail * sr)
    nfft = _next_pow2(n + pad)
    X = np.fft.rfft(x, nfft, axis=0)
    H = freq_response(sections, nfft)
    if x.ndim == 2:
        H = H[:, None]
    y = np.fft.irfft(X * H, nfft, axis=0)
    return y[: n + pad] if keep_tail else y[:n]


def fft_convolve(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Full linear convolution along axis 0. h is mono; x may be (N,) or (N, C)."""
    n = len(x) + len(h) - 1
    nfft = _next_pow2(n)
    X = np.fft.rfft(x, nfft, axis=0)
    Hh = np.fft.rfft(h, nfft)
    if x.ndim == 2:
        Hh = Hh[:, None]
    return np.fft.irfft(X * Hh, nfft, axis=0)[:n]


# --------------------------------------------------------------------------- #
# Oscillators
# --------------------------------------------------------------------------- #
def phase_from_freq(freq: np.ndarray, sr: int = SR, phase0: float = 0.0) -> np.ndarray:
    """Phase in cycles from an instantaneous-frequency array."""
    return phase0 + np.cumsum(freq) / sr


def polyblep_saw(freq: np.ndarray, sr: int = SR, phase0: float = 0.0) -> np.ndarray:
    """Band-limited (polyBLEP) sawtooth with time-varying frequency, fully vectorized."""
    ph = np.mod(phase_from_freq(freq, sr, phase0), 1.0)
    dt = np.clip(freq / sr, 1e-9, 0.5)
    y = 2.0 * ph - 1.0
    m = ph < dt
    t = ph[m] / dt[m]
    y[m] -= t + t - t * t - 1.0
    m = ph > 1.0 - dt
    t = (ph[m] - 1.0) / dt[m]
    y[m] -= t * t + t + t + 1.0
    return y


def smooth_noise(n: int, rate_hz: float, g: np.random.Generator, sr: int = SR) -> np.ndarray:
    """Slow random wobble in [-1, 1] (cosine-interpolated random points). Used for drift LFOs."""
    pts = int(np.ceil(n * rate_hz / sr)) + 2
    v = g.uniform(-1, 1, pts)
    x = np.arange(n) * rate_hz / sr
    i = np.floor(x).astype(int)
    fr = x - i
    w = 0.5 - 0.5 * np.cos(np.pi * fr)
    return v[i] * (1 - w) + v[i + 1] * w


# --------------------------------------------------------------------------- #
# Recursive structures, block-vectorized
# --------------------------------------------------------------------------- #
def feedback_comb(x: np.ndarray, delay: float, g: float) -> np.ndarray:
    """y[n] = x[n] + g * interp(y, n - delay), fractional delay via linear interpolation.

    The linear interpolation doubles as a gentle loop low-pass (string/bore loss).
    Processed in blocks of floor(delay) samples so each block only reads the past.
    """
    di = int(np.floor(delay))
    fr = delay - di
    if di < 2:
        raise ValueError("comb delay too short")
    n = len(x)
    y = np.zeros(n + di + 1)
    off = di + 1  # y index offset so y[off + k] is output sample k
    y_x = np.concatenate([np.zeros(off), x])
    for s in range(off, n + off, di):
        e = min(s + di, n + off)
        y[s:e] = y_x[s:e] + g * ((1 - fr) * y[s - di:e - di] + fr * y[s - di - 1:e - di - 1])
    return y[off:]


def allpass_block(x: np.ndarray, d: int, g: float) -> np.ndarray:
    """Schroeder allpass y[n] = -g x[n] + x[n-d] + g y[n-d], block-vectorized (block = d)."""
    n = len(x)
    xp = np.concatenate([np.zeros(d), x])
    yp = np.zeros(n + d)
    for s in range(d, n + d, d):
        e = min(s + d, n + d)
        yp[s:e] = -g * xp[s:e] + xp[s - d:e - d] + g * yp[s - d:e - d]
    return yp[d:]


def pan_mono(x: np.ndarray, pan: float) -> np.ndarray:
    """Constant-power pan, pan in [-1, 1]. Returns (N, 2)."""
    th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], axis=1)
