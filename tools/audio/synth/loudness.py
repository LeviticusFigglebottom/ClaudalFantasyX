"""Approximate ITU-R BS.1770-4 loudness (LUFS) in numpy.

* K-weighting: the two-stage pre-filter (high-shelf ~ +4 dB above ~1.7 kHz,
  then a ~38 Hz high-pass), designed for any sample rate by bilinear
  transform of the analog prototype (the libebur128 approach). At 48 kHz the
  design reproduces the coefficients printed in the standard to < 1e-6
  (checked by self_test()).
* Integrated loudness: 400 ms blocks, 75 % overlap, absolute gate -70 LUFS,
  relative gate -10 LU.
* Momentary max (400 ms window, 10 ms hop) for short SFX, where integrated
  loudness is not meaningful.
* True-peak estimate by 4x FFT oversampling (BS.1770 Annex 2 asks for a
  polyphase FIR; FFT interpolation is a close stand-in for offline use).

Channel weights: L/R = 1.0 (we never render surround).
"""
from __future__ import annotations

import numpy as np

from .dsp import SR, filt

_SHELF = dict(G=3.99984385397, Q=0.7071752369554193, fc=1681.9744509555319)
_HP = dict(Q=0.5003270373253953, fc=38.13547087613982)


def k_weighting_sections(sr: int = SR):
    """Bilinear-transform design of the K-weighting pre-filter (as in libebur128)."""
    K = np.tan(np.pi * _SHELF["fc"] / sr)
    Q = _SHELF["Q"]
    Vh = 10 ** (_SHELF["G"] / 20.0)
    Vb = Vh ** 0.4996667741545416
    a0 = 1.0 + K / Q + K * K
    b1 = [(Vh + Vb * K / Q + K * K) / a0, 2.0 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a1 = [1.0, 2.0 * (K * K - 1.0) / a0, (1.0 - K / Q + K * K) / a0]
    K = np.tan(np.pi * _HP["fc"] / sr)
    Q = _HP["Q"]
    d = 1.0 + K / Q + K * K
    a2 = [1.0, 2.0 * (K * K - 1.0) / d, (1.0 - K / Q + K * K) / d]
    b2 = [1.0, -2.0, 1.0]  # the standard leaves stage 2 numerator un-normalized
    return [(b1, a1), (b2, a2)]


def _as2d(x):
    x = np.asarray(x, dtype=np.float64)
    return x[:, None] if x.ndim == 1 else x


def _block_powers(x, sr, win_s, hop_s):
    y = filt(_as2d(x), k_weighting_sections(sr), tail=0.1, sr=sr)
    win = int(round(win_s * sr))
    hop = int(round(hop_s * sr))
    if len(y) < win:
        y = np.concatenate([y, np.zeros((win - len(y), y.shape[1]))])
    cs = np.concatenate([np.zeros((1, y.shape[1])), np.cumsum(y * y, axis=0)])
    starts = np.arange(0, len(y) - win + 1, hop)
    ms = (cs[starts + win] - cs[starts]) / win  # mean square per channel per block
    return ms.sum(axis=1)  # channel weights all 1.0


def _to_lufs(p):
    return -0.691 + 10 * np.log10(np.maximum(p, 1e-20))


def integrated_lufs(x, sr: int = SR) -> float:
    p = _block_powers(x, sr, 0.4, 0.1)
    lk = _to_lufs(p)
    p = p[lk > -70.0]
    if len(p) == 0:
        return -np.inf
    rel = _to_lufs(p.mean()) - 10.0
    p2 = p[_to_lufs(p) > rel]
    return float(_to_lufs(p2.mean())) if len(p2) else -np.inf


def momentary_max_lufs(x, sr: int = SR) -> float:
    """Max 400 ms momentary loudness; signals shorter than 400 ms are zero-padded."""
    return float(_to_lufs(_block_powers(x, sr, 0.4, 0.01)).max())


def true_peak_dbtp(x, oversample: int = 4) -> float:
    x = _as2d(x)
    n = len(x)
    X = np.fft.rfft(x, axis=0)
    y = np.fft.irfft(X, n * oversample, axis=0) * oversample
    return float(20 * np.log10(max(np.abs(y).max(), 1e-12)))


def sample_peak_dbfs(x) -> float:
    return float(20 * np.log10(max(np.abs(np.asarray(x)).max(), 1e-12)))


def self_test() -> None:
    """Sanity checks: 48 kHz coefficients and the 997 Hz / -20 dBFS reference point."""
    (b1, a1), (b2, a2) = k_weighting_sections(48000)
    ref_b1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]
    ref_a1 = [1.0, -1.69065929318241, 0.73248077421585]
    ref_a2 = [1.0, -1.99004745483398, 0.99007225036621]
    assert np.allclose(b1, ref_b1, atol=1e-6) and np.allclose(a1, ref_a1, atol=1e-6)
    assert np.allclose(a2, ref_a2, atol=1e-6)
    # A 0 dBFS-peak 997 Hz sine in one channel reads about -3.01 LUFS.
    t = np.arange(SR * 5) / SR
    s = np.sin(2 * np.pi * 997 * t)
    v = integrated_lufs(s, SR)
    assert abs(v - (-3.01)) < 0.1, v
