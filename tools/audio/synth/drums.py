"""Frame drums and jingles (modal membranes).

A frame drum is a membrane on a shallow hoop, so nearly all of its sound is
the membrane's own modes. We use the ideal circular-membrane ratios (zeros
of the Bessel functions J_m), with air loading pulling the low modes a
little closer together, and choose which modes a stroke excites from where
it lands:

* ``dum``   centre stroke: the (0, n) family and (1, 1) dominate, low and
            round, with a downward pitch glide (tension modulation: a hard
            hit stretches the skin and raises its pitch for a moment).
* ``tek``   rim stroke: high (m, 1) modes, short, plus a rim click.
* ``slap``  open slap near the edge: a noise burst through mid modes. In
            the battle cue it takes the backbeat role.
* ``ghost`` a soft, damped tek.

`jingle` is a cluster of small inharmonic metal discs that hit a few ms
apart (riq/tambourine-like), used for the hi-hat role.
`big_drum` is a large frame drum (or a barrel drum) for downbeat impacts.

Each hit is short, so we cache renders by (stroke, quantized velocity,
round-robin variant): repeated patterns cost almost nothing.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng

# (ratio, centre weight, edge weight, relative T60)
MEMBRANE = [
    (1.000, 1.00, 0.30, 1.00), (1.594, 0.45, 0.70, 0.70), (2.136, 0.20, 0.90, 0.55), (2.296, 0.55, 0.25, 0.50),
    (2.653, 0.10, 0.85, 0.42), (2.918, 0.25, 0.55, 0.38), (3.156, 0.06, 0.75, 0.33), (3.501, 0.18, 0.45, 0.30),
    (3.600, 0.30, 0.15, 0.28), (3.652, 0.04, 0.60, 0.27), (4.060, 0.12, 0.40, 0.24), (4.154, 0.03, 0.50, 0.22),
    (4.601, 0.08, 0.35, 0.20), (4.832, 0.02, 0.40, 0.18), (5.131, 0.05, 0.30, 0.16), (5.412, 0.02, 0.32, 0.15),
]


STROKE_IDS = {"dum": 1, "tek": 2, "slap": 3, "ghost": 4}


def _air_loaded(r: float) -> float:
    """Air loading lowers the low modes most; compress the bottom of the series slightly."""
    return 1.0 + (r - 1.0) * (0.86 + 0.14 * min(1.0, (r - 1.0) / 3.0))


def _membrane(f1: float, t60: float, pos: float, vel: float, glide: float, g: np.random.Generator,
              length: float, sr: int, brightness: float = 1.0) -> np.ndarray:
    N = int(length * sr)
    t = np.arange(N) / sr
    out = np.zeros(N)
    # pitch glide shared by all modes (the whole skin is stretched)
    gl = 1.0 + glide * vel * np.exp(-t / 0.045)
    ph_base = 2 * np.pi * np.cumsum(gl) / sr
    for r, wc, we, rt in MEMBRANE:
        f = f1 * _air_loaded(r) * (1 + g.uniform(-0.006, 0.006))
        if f > 0.42 * sr:
            continue
        w = (1 - pos) * wc + pos * we
        w *= 1.0 / (1.0 + (f / (2500.0 * brightness * (0.6 + 0.8 * vel))) ** 2)
        T = t60 * rt
        out += w * np.exp(-6.91 * t / T) * np.sin(f * ph_base + g.uniform(0, 2 * np.pi))
    # strokes near the rim also excite the dense, short-lived high-order modes
    n_hi = int(40 * pos)
    for r in np.sort(g.uniform(5.6, 48.0, n_hi)):
        f = f1 * r
        if f > 0.42 * sr:
            continue
        w = pos * 0.35 * (5.6 / r) ** 0.5 * (0.4 + 0.6 * vel)
        T = t60 * 0.12 * (5.6 / r) ** 0.7
        out += w * np.exp(-6.91 * t / T) * np.sin(f * ph_base + g.uniform(0, 2 * np.pi))
    return out


@lru_cache(maxsize=512)
def _frame_drum_cached(stroke: str, vq: int, variant: int, size: float, seed: int, sr: int) -> np.ndarray:
    vel = vq / 100.0
    g = rng(seed * 1009 + variant * 7919 + vq * 31 + STROKE_IDS[stroke] * 104729)  # no hash(): it is salted per process
    f1 = 92.0 / size * (1 + g.uniform(-0.01, 0.01))
    if stroke == "dum":
        body = _membrane(f1, 0.55 * size, 0.1, vel, 0.07, g, 0.9 * size, sr)
        nn = int(0.012 * sr)
        hit = filt(g.standard_normal(nn), [bq_lowpass(900, 0.7, sr)], sr=sr) * np.exp(-np.arange(nn) / sr / 0.003)
        body[:nn] += 0.5 * hit
        lvl = 1.0
    elif stroke in ("tek", "ghost"):
        body = _membrane(f1 * 1.02, 0.16, 0.92, vel, 0.02, g, 0.35, sr, brightness=1.8)
        nn = int(0.008 * sr)
        click = filt(g.standard_normal(nn), [bq_bandpass(3200, 1.2, sr)], sr=sr) * np.exp(-np.arange(nn) / sr / 0.0015)
        body[:nn] += 0.9 * click
        lvl = 0.55 if stroke == "tek" else 0.22
        if stroke == "ghost":
            body *= np.exp(-np.arange(len(body)) / sr / 0.05)
    elif stroke == "slap":
        body = _membrane(f1 * 1.05, 0.22, 0.6, vel, 0.03, g, 0.45, sr, brightness=2.2)
        nn = int(0.06 * sr)
        tn = np.arange(nn) / sr
        crack = filt(g.standard_normal(nn), [bq_bandpass(1400, 0.6, sr), bq_highpass(400, 0.7, sr)], sr=sr)
        crack = crack / (np.std(crack) + 1e-9) * np.exp(-tn / 0.018) * (1 - np.exp(-tn / 0.0008))
        body /= np.abs(body).max() + 1e-9
        body[:nn] += 0.9 * crack
        lvl = 0.8
    else:
        raise ValueError(stroke)
    body *= np.minimum(1.0, np.arange(len(body)) / (0.0006 * sr))
    k = min(len(body) // 4, int(0.03 * sr))
    body[-k:] *= np.linspace(1, 0, k) ** 2
    body /= np.abs(body).max() + 1e-9
    return lvl * vel ** 1.4 * body


def frame_drum(stroke: str, vel: float, variant: int = 0, size: float = 1.0, seed: int = 0, sr: int = SR) -> np.ndarray:
    """One stroke (mono). Velocity is quantized to 0.01 for caching; `variant` picks a round-robin take."""
    vq = int(round(float(np.clip(vel, 0.01, 1.0)) * 100))
    return _frame_drum_cached(stroke, vq, int(variant) % 8, float(size), int(seed), sr).copy()


@lru_cache(maxsize=256)
def _jingle_cached(vq: int, variant: int, open_: bool, seed: int, sr: int) -> np.ndarray:
    vel = vq / 100.0
    g = rng(seed * 31 + variant * 131 + vq + (7 if open_ else 0))
    L = 0.45 if open_ else 0.14
    N = int(L * sr)
    t = np.arange(N) / sr
    out = np.zeros(N)
    for _ in range(5):                      # five discs, hitting a few ms apart
        t0 = g.uniform(0.0, 0.006)
        s = int(t0 * sr)
        tt = t[: N - s]
        for f in g.uniform(4500, 13000, 6):
            if f > 0.45 * sr:
                continue
            T = g.uniform(0.05, 0.25) * (1.0 if open_ else 0.35)
            out[s:] += g.uniform(0.3, 1.0) * np.exp(-6.91 * tt / T) * np.sin(2 * np.pi * f * tt + g.uniform(0, 6.28))
    nz = filt(g.standard_normal(N), [bq_highpass(6000, 0.7, sr)], sr=sr) * np.exp(-t / 0.01)
    out += 0.8 * nz
    out *= np.minimum(1.0, t / 0.0005)
    k = min(N // 4, int(0.02 * sr))
    out[-k:] *= np.linspace(1, 0, k) ** 2
    out /= np.abs(out).max() + 1e-9
    return 0.35 * vel ** 1.2 * out


def jingle(vel: float, variant: int = 0, open_: bool = False, seed: int = 0, sr: int = SR) -> np.ndarray:
    vq = int(round(float(np.clip(vel, 0.01, 1.0)) * 100))
    return _jingle_cached(vq, int(variant) % 8, bool(open_), int(seed), sr).copy()


@lru_cache(maxsize=64)
def _big_drum_cached(vq: int, variant: int, seed: int, sr: int) -> np.ndarray:
    vel = vq / 100.0
    g = rng(seed * 17 + variant * 3 + vq)
    body = _membrane(52.0, 1.4, 0.05, vel, 0.12, g, 2.2, sr, brightness=0.6)
    nn = int(0.02 * sr)
    hit = filt(g.standard_normal(nn), [bq_lowpass(600, 0.7, sr)], sr=sr) * np.exp(-np.arange(nn) / sr / 0.005)
    body[:nn] += 0.4 * hit
    body *= np.minimum(1.0, np.arange(len(body)) / (0.001 * sr))
    k = int(0.05 * sr)
    body[-k:] *= np.linspace(1, 0, k) ** 2
    body /= np.abs(body).max() + 1e-9
    return vel ** 1.3 * body


def big_drum(vel: float, variant: int = 0, seed: int = 0, sr: int = SR) -> np.ndarray:
    vq = int(round(float(np.clip(vel, 0.01, 1.0)) * 100))
    return _big_drum_cached(vq, int(variant) % 4, int(seed), sr).copy()
