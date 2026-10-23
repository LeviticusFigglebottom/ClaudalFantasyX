"""Objective measurements for instruments, reverbs and rendered cues.

Nobody on the agent side can listen, so quality claims have to rest on
numbers that can be compared with physical expectations:

* piano notes   inharmonicity coefficient B (fitted from measured partial
                frequencies), per-partial decay rates in dB/s (heterodyne
                envelopes plus a least-squares slope), spectral-centroid
                trajectory over the decay, crest factor;
* reverbs       normalized echo density (Abel & Huang 2006), late-tail
                spectral peakiness against the Rayleigh statistics of a
                diffuse field, tail periodicity (normalized autocorrelation),
                band RT60s by Schroeder backward integration, modal overlap;
* loops         seam continuity (the jump at the wrap point compared with the
                signal's typical sample-to-sample change, and the spectral flux
                there compared with elsewhere).

Everything is plain numpy and deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from .dsp import SR, bq_bandpass, filt

ERFC_1_SQRT2 = math.erfc(1.0 / math.sqrt(2.0))  # 0.3173: fraction of Gaussian samples beyond 1 sigma
RAYLEIGH_P99_OVER_MEDIAN_DB = 10.0 * math.log10(math.log(100.0) / math.log(2.0))  # 8.22 dB


def mono(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return x.mean(axis=1) if x.ndim == 2 else x


# --------------------------------------------------------------------------- #
# General
# --------------------------------------------------------------------------- #
def crest_factor_db(x: np.ndarray, gate_db: float = -50.0, sr: int = SR) -> float:
    """Peak over RMS (dB), RMS taken over 50 ms frames louder than `gate_db` re the peak frame."""
    y = mono(x)
    hop = int(0.05 * sr)
    nfr = max(1, len(y) // hop)
    fr = y[: nfr * hop].reshape(nfr, hop)
    p = (fr ** 2).mean(axis=1)
    keep = p > p.max() * 10 ** (gate_db / 10)
    rms = math.sqrt(p[keep].mean())
    return 20 * math.log10(np.abs(y).max() / max(rms, 1e-12))


def spectral_centroid_at(x: np.ndarray, times, win: float = 0.046, sr: int = SR) -> list[float]:
    """Spectral centroid (Hz) of a Hann window centred at each time (seconds)."""
    y = mono(x)
    n = int(win * sr)
    w = np.hanning(n)
    f = np.fft.rfftfreq(n, 1 / sr)
    out = []
    for t in times:
        s = int(t * sr) - n // 2
        seg = np.zeros(n)
        a, b = max(0, s), min(len(y), s + n)
        if b > a:
            seg[a - s: b - s] = y[a:b]
        mag = np.abs(np.fft.rfft(seg * w))
        out.append(float((f * mag).sum() / max(mag.sum(), 1e-12)))
    return out


# --------------------------------------------------------------------------- #
# Piano partials
# --------------------------------------------------------------------------- #
def find_partials(x: np.ndarray, f0: float, B: float, count: int, t0: float = 0.02, length: float = 0.8,
                  sr: int = SR) -> np.ndarray:
    """Measured frequencies of partials 1..count (NaN when not found).

    Searches near the stiff-string prediction n f0 sqrt(1 + B n^2) within
    +-35 % of f0, on a zero-padded Hann spectrum, with parabolic peak
    interpolation on the log magnitude.
    """
    y = mono(x)
    s = int(t0 * sr)
    e = min(len(y), int((t0 + length) * sr))
    seg = y[s:e] * np.hanning(e - s)
    nfft = 1 << int(np.ceil(np.log2(len(seg) * 8)))
    mag = np.abs(np.fft.rfft(seg, nfft)) + 1e-15
    df = sr / nfft
    out = np.full(count, np.nan)
    floor = mag.max() * 10 ** (-90 / 20)
    for k in range(1, count + 1):
        pred = k * f0 * math.sqrt(1 + B * k * k)
        if pred > 0.45 * sr:
            break
        lo, hi = int((pred - 0.35 * f0) / df), int((pred + 0.35 * f0) / df)
        lo, hi = max(lo, 1), min(hi, len(mag) - 2)
        if hi <= lo:
            continue
        i = lo + int(np.argmax(mag[lo:hi]))
        if mag[i] < floor:
            continue
        a, b, c = np.log(mag[i - 1: i + 2])
        den = a - 2 * b + c
        d = 0.5 * (a - c) / den if den != 0 else 0.0
        out[k - 1] = (i + d) * df
    return out


def fit_inharmonicity(freqs: np.ndarray) -> tuple[float, float]:
    """Least-squares fit of (f_n / n)^2 = f0^2 (1 + B n^2). Returns (f0, B)."""
    n = np.arange(1, len(freqs) + 1, dtype=np.float64)
    ok = np.isfinite(freqs)
    if ok.sum() < 3:
        return float("nan"), float("nan")
    yv = (freqs[ok] / n[ok]) ** 2
    A = np.stack([np.ones(ok.sum()), n[ok] ** 2], axis=1)
    (c0, c1), *_ = np.linalg.lstsq(A, yv, rcond=None)
    return math.sqrt(c0), c1 / c0


def partial_envelope_db(x: np.ndarray, freq: float, bw: float = 8.0, sr: int = SR,
                        hop: float = 0.01) -> tuple[np.ndarray, np.ndarray]:
    """Heterodyne envelope (dB) of one partial: shift to DC, then a moving-average
    low-pass of length 1/bw seconds. Returns (times, dB)."""
    y = mono(x)
    t = np.arange(len(y)) / sr
    z = y * np.exp(-2j * np.pi * freq * t)
    L = max(8, int(sr / bw))
    cs = np.concatenate([[0], np.cumsum(z)])
    idx = np.arange(0, len(y) - L, int(hop * sr))
    env = np.abs(cs[idx + L] - cs[idx]) / L * 2
    return (idx + L / 2) / sr, 20 * np.log10(np.maximum(env, 1e-12))


def decay_rate_db_per_s(x: np.ndarray, freq: float, t0: float, t1: float, sr: int = SR) -> float:
    """Least-squares slope (positive = decaying) of a partial's envelope between t0 and t1."""
    tt, db = partial_envelope_db(x, freq, sr=sr)
    m = (tt >= t0) & (tt <= t1)
    if m.sum() < 4:
        return float("nan")
    slope = np.polyfit(tt[m], db[m], 1)[0]
    return float(-slope)


# --------------------------------------------------------------------------- #
# Reverb impulse responses
# --------------------------------------------------------------------------- #
def echo_density_profile(ir: np.ndarray, win: float = 0.02, hop: float = 0.005,
                         sr: int = SR) -> tuple[np.ndarray, np.ndarray]:
    """Normalized echo density (Abel & Huang 2006). 1.0 = Gaussian-like (fully diffuse)."""
    h = mono(ir)
    n = int(win * sr)
    w = np.hanning(n)
    w /= w.sum()
    times, ned = [], []
    for s in range(0, len(h) - n, int(hop * sr)):
        seg = h[s: s + n]
        sd = math.sqrt(float((w * seg * seg).sum()))
        if sd <= 0:
            ned.append(0.0)
        else:
            ned.append(float((w * (np.abs(seg) > sd)).sum()) / ERFC_1_SQRT2)
        times.append((s + n / 2) / sr)
    return np.array(times), np.array(ned)


def mixing_time(ir: np.ndarray, threshold: float = 0.95, sr: int = SR) -> float:
    """First time the echo density stays above `threshold` for 50 ms."""
    t, d = echo_density_profile(ir, sr=sr)
    run = 0
    for i, v in enumerate(d):
        run = run + 1 if v >= threshold else 0
        if run >= 10:
            return float(t[i - 9])
    return float("nan")


def _tail_segment(ir: np.ndarray, t0: float, t1: float, sr: int) -> np.ndarray:
    h = mono(ir)[int(t0 * sr): int(t1 * sr)]
    # remove the exponential decay so the segment is (ideally) stationary noise
    hop = int(0.01 * sr)
    nfr = len(h) // hop
    rms = np.sqrt((h[: nfr * hop].reshape(nfr, hop) ** 2).mean(axis=1) + 1e-30)
    tt = (np.arange(nfr) + 0.5) * hop
    a, b = np.polyfit(tt, np.log(rms), 1)
    env = np.exp(a * np.arange(len(h)) + b)
    return h / env


def tail_spectral_peakiness(ir: np.ndarray, t0: float = 0.4, t1: float = 1.4, fmin: float = 500.0,
                            fmax: float = 5000.0, sr: int = SR) -> dict:
    """Spectral fine structure of the late tail against a diffuse-field model.

    A dense, well-mixed tail has a Rayleigh-distributed magnitude spectrum:
    the power in each bin, divided by the smoothed spectrum, is exponential,
    so its 99th percentile sits 8.2 dB above its median, and almost no bin is
    more than 10x the local mean (p = 4.5e-5). Stationary, under-damped FDN
    modes ("metallic ring") push both numbers up.
    """
    seg = _tail_segment(ir, t0, t1, sr)
    w = np.hanning(len(seg))
    P = np.abs(np.fft.rfft(seg * w)) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / sr)
    band = (f >= fmin) & (f <= fmax)
    # local mean over +-1/6 octave
    logf = np.log2(np.maximum(f, 1.0))
    cs = np.concatenate([[0], np.cumsum(P)])
    lo = np.searchsorted(logf, logf - 1 / 6)
    hi = np.searchsorted(logf, logf + 1 / 6)
    smooth = (cs[hi] - cs[lo]) / np.maximum(hi - lo, 1)
    r = P[band] / np.maximum(smooth[band], 1e-30)
    p99, med = np.percentile(r, 99), np.median(r)
    return dict(p99_over_median_db=float(10 * np.log10(p99 / med)),
                frac_over_10x=float((r > 10).mean()),
                expected_p99_over_median_db=RAYLEIGH_P99_OVER_MEDIAN_DB)


def tail_periodicity(ir: np.ndarray, t0: float = 0.3, t1: float = 1.3, min_lag: float = 0.004,
                     max_lag: float = 0.25, sr: int = SR) -> float:
    """Largest normalized autocorrelation of the (decay-flattened) tail for lags in
    [min_lag, max_lag]. Repeating echo patterns (flutter) read high; white noise reads ~ 3/sqrt(N)."""
    seg = _tail_segment(ir, t0, t1, sr)
    seg = seg - seg.mean()
    n = len(seg)
    nfft = 1 << int(np.ceil(np.log2(2 * n)))
    S = np.fft.rfft(seg, nfft)
    ac = np.fft.irfft(S * np.conj(S), nfft)[:n]
    ac /= ac[0]
    a, b = int(min_lag * sr), int(max_lag * sr)
    return float(np.abs(ac[a:b]).max())


def tail_kurtosis(ir: np.ndarray, t0: float = 0.3, t1: float = 1.3, sr: int = SR) -> float:
    """Kurtosis of the decay-flattened tail (Gaussian noise = 3)."""
    s = _tail_segment(ir, t0, t1, sr)
    s = s - s.mean()
    return float((s ** 4).mean() / (s ** 2).mean() ** 2)


def rt60_band(ir: np.ndarray, fc: float, sr: int = SR) -> float:
    """T20-based RT60 (fit from -5 to -25 dB of the Schroeder curve) in an octave band."""
    h = filt(mono(ir), [bq_bandpass(fc, 1.41, sr), bq_bandpass(fc, 1.41, sr)], sr=sr)
    e = np.cumsum((h ** 2)[::-1])[::-1]
    db = 10 * np.log10(e / e[0] + 1e-30)
    t = np.arange(len(db)) / sr
    m = (db <= -5) & (db >= -25)
    if m.sum() < 10:
        return float("nan")
    slope = np.polyfit(t[m], db[m], 1)[0]
    return float(-60.0 / slope)


# --------------------------------------------------------------------------- #
# Loops
# --------------------------------------------------------------------------- #
def loop_seam_report(y: np.ndarray, loop_start: int, sr: int = SR) -> dict:
    """How seamless is the jump from the last sample back to `loop_start`?

    jump_ratio: |y[start] - y[end]| compared with the median absolute
    sample-to-sample difference of the whole loop body (1.0 = an ordinary
    sample step; a click is usually > 10).
    flux_ratio: spectral flux across the seam (a 1024-sample frame either
    side) divided by the median flux of frame pairs inside the body.
    """
    y2 = y if y.ndim == 2 else y[:, None]
    body = y2[loop_start:]
    d = np.abs(np.diff(body, axis=0)).max(axis=1)
    med = float(np.median(d)) + 1e-12
    jump = float(np.abs(body[0] - body[-1]).max())
    n = 1024
    w = np.hanning(n)[:, None]

    def spec(seg):
        return np.abs(np.fft.rfft(seg * w, axis=0)).sum(axis=1)

    seam = np.concatenate([body[-n:], body[:n]])
    flux_seam = float(np.abs(spec(seam[n:]) - spec(seam[:n])).sum())
    fl = []
    for s in range(n, len(body) - n, len(body) // 64):
        fl.append(np.abs(spec(body[s: s + n]) - spec(body[s - n: s])).sum())
    return dict(jump_ratio=jump / med, flux_ratio=flux_seam / (float(np.median(fl)) + 1e-12))
