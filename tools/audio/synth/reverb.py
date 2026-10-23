"""Algorithmic reverb: early-reflection taps + input allpass diffusion + an
8-line feedback delay network (FDN) with a Hadamard mixing matrix.

The FDN is processed in blocks no longer than its shortest delay line, which
makes every block a handful of vectorized numpy operations (no per-sample
Python loop). Per-line gains are set from RT60 at DC; a one-zero low-pass in
each loop ("damping") makes high frequencies decay faster, like air and
soft surfaces do.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dsp import SR, allpass_block, bq_highpass, bq_lowpass, filt, rng


def _hadamard(n: int) -> np.ndarray:
    h = np.array([[1.0]])
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]])
    return h / np.sqrt(n)


@dataclass
class FDNReverb:
    rt60: float = 2.4            # seconds, at low frequencies
    predelay: float = 0.020      # seconds
    damping: float = 0.30        # 0 = bright, 0.5 = very dark
    size: float = 1.0            # scales all delay lengths
    early_level: float = 0.35
    diffusion: float = 0.62      # input allpass coefficient
    lowcut: float = 140.0        # high-pass on the reverb input (keeps the bass dry)
    highcut: float = 7500.0      # low-pass on the reverb input
    seed: int = 1771
    sr: int = SR

    # Mutually prime delay lengths (samples at 44.1 kHz, size = 1): ~29-71 ms.
    BASE_DELAYS = (1283, 1511, 1733, 1999, 2239, 2503, 2843, 3121)
    DIFFUSERS = (142, 107, 379, 277)

    def process(self, x: np.ndarray, tail: float = 3.0) -> np.ndarray:
        """x: (N, 2) dry send. Returns the wet signal, shape (N + tail, 2)."""
        sr = self.sr
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        n = len(x) + int(tail * sr)
        xin = np.zeros((n, 2))
        xin[: len(x)] = x
        xin = filt(xin, [bq_highpass(self.lowcut, 0.7, sr), bq_lowpass(self.highcut, 0.7, sr)], sr=sr)

        pd = int(self.predelay * sr)
        xin = np.concatenate([np.zeros((pd, 2)), xin])[:n]

        # --- early reflections: a sparse stereo tapped delay ------------------
        g = rng(self.seed)
        early = np.zeros((n, 2))
        taps = np.sort(g.uniform(0.004, 0.045, 10))
        for i, tt in enumerate(taps):
            d = int(tt * self.size * sr)
            amp = (0.8 ** i) * (1 if i % 2 == 0 else -1)
            ch = i % 2
            early[d:, ch] += amp * xin[: n - d, ch]
            early[d:, 1 - ch] += 0.4 * amp * xin[: n - d, 1 - ch]

        # --- input diffusion (mono-ish, keeps L/R a little distinct) ---------
        dl = xin[:, 0] + 0.25 * early[:, 0]
        dr = xin[:, 1] + 0.25 * early[:, 1]
        for i, d in enumerate(self.DIFFUSERS):
            dl = allpass_block(dl, int(d * self.size), self.diffusion)
            dr = allpass_block(dr, int(d * self.size * 1.07) + 1, self.diffusion)

        # --- FDN ---------------------------------------------------------------
        L = np.array([max(64, int(d * self.size * sr / 44100)) for d in self.BASE_DELAYS])
        nl = len(L)
        H = _hadamard(nl)
        gains = 10.0 ** (-3.0 * L / (self.rt60 * sr))
        inj = np.zeros((nl, n))
        inj[0::2] = dl[None, :] * 0.5
        inj[1::2] = dr[None, :] * 0.5
        maxd = int(L.max()) + 2
        s = np.zeros((nl, n + maxd), dtype=np.float64)  # line input signals, offset by maxd
        out = np.zeros((nl, n))
        B = int(L.min())
        dmp = self.damping
        for t0 in range(0, n, B):
            t1 = min(t0 + B, n)
            o = np.empty((nl, t1 - t0))
            od = np.empty((nl, t1 - t0))
            for j in range(nl):
                a = t0 + maxd - L[j]
                o[j] = s[j, a:a + (t1 - t0)]
                od[j] = (1 - dmp) * o[j] + dmp * s[j, a - 1:a - 1 + (t1 - t0)]
            out[:, t0:t1] = o
            s[:, t0 + maxd:t1 + maxd] = inj[:, t0:t1] + H @ (gains[:, None] * od)
        signs_l = np.array([1, -1, 1, 1, -1, 1, -1, -1], dtype=float)[:nl]
        signs_r = np.array([1, 1, -1, 1, 1, -1, -1, 1], dtype=float)[:nl]
        late = np.stack([signs_l @ out, signs_r @ out], axis=1) / np.sqrt(nl)
        return late + self.early_level * early


# --------------------------------------------------------------------------- #
# M1-AUD-02: modulated 16-line FDN (FDNReverb above stays frozen for the M1 sketch)
# --------------------------------------------------------------------------- #
def _lagrange3(buf: np.ndarray, pos: np.ndarray) -> np.ndarray:
    """Cubic Lagrange read of each row of `buf` at fractional positions `pos` (rows x samples)."""
    i = np.floor(pos).astype(np.int64)
    d = pos - i
    rows = np.arange(buf.shape[0])[:, None]
    ym1 = buf[rows, i - 1]
    y0 = buf[rows, i]
    y1 = buf[rows, i + 1]
    y2 = buf[rows, i + 2]
    return (-d * (d - 1) * (d - 2) / 6 * ym1 + (d + 1) * (d - 1) * (d - 2) / 2 * y0
            - (d + 1) * d * (d - 2) / 2 * y1 + (d + 1) * d * (d - 1) / 6 * y2)


@dataclass
class ModFDNReverb:
    """16-line FDN with slowly modulated delay lengths and per-line frequency-dependent loss.

    Why: the 8-line `FDNReverb` has fixed delays, so its late tail is a set of
    stationary, under-overlapped modes (modal overlap ~0.3 at RT60 2.6 s),
    which is what "metallic ring" is. Here (a) the total delay is ~2.3x
    longer (16 lines, 25-100 ms), (b) every delay is modulated by a few
    samples at sub-hertz rates, so no mode stays put long enough to ring, and
    (c) each loop has a 3-tap linear-phase loss filter set from two RT60s
    (DC and 8 kHz), so decay is consistent across lines (Jot's method).
    Delay reads use cubic Lagrange interpolation; the loop is processed in
    blocks shorter than the shortest (modulated) delay, so every block is a
    few vectorized numpy operations.
    """
    rt60: float = 2.4              # seconds at low frequencies
    rt60_high: float = 1.0         # seconds at 8 kHz
    predelay: float = 0.020
    size: float = 1.0
    mod_depth: float = 12.0        # samples (peak)
    mod_rate: float = 0.7          # Hz (mean; each line differs)
    early_level: float = 0.30
    diffusion: float = 0.62
    lowcut: float = 120.0
    highcut: float = 9000.0
    width: float = 1.0
    seed: int = 1771
    sr: int = SR
    loop_period: float = 0.0       # > 0: snap every LFO to a whole number of cycles per period (loops)
    t_offset: float = 0.0          # LFO time origin, seconds (to phase-align an intro with a loop)

    BASE_DELAYS = (1109, 1223, 1361, 1489, 1627, 1789, 1951, 2137,
                   2333, 2549, 2777, 3023, 3299, 3593, 3917, 4271)
    DIFFUSERS = (149, 113, 337, 251, 89, 61)

    def _early(self, xin: np.ndarray, n: int, g: np.random.Generator) -> np.ndarray:
        early = np.zeros((n, 2))
        taps = np.sort(g.uniform(0.003, 0.060, 18))
        for i, tt in enumerate(taps):
            d = int(tt * self.size * self.sr)
            amp = (0.86 ** i) * float(g.choice([-1.0, 1.0]))
            ch = int(g.integers(0, 2))
            early[d:, ch] += amp * xin[: n - d, ch]
            early[d:, 1 - ch] += 0.35 * amp * xin[: n - d, 1 - ch]
        return early

    def process(self, x: np.ndarray, tail: float = 3.0) -> np.ndarray:
        """x: (N, 2) dry send. Returns the wet signal, shape (N + tail, 2)."""
        sr = self.sr
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        n = len(x) + int(tail * sr)
        xin = np.zeros((n, 2))
        xin[: len(x)] = x
        xin = filt(xin, [bq_highpass(self.lowcut, 0.7, sr), bq_lowpass(self.highcut, 0.7, sr)], sr=sr)
        pd = int(self.predelay * sr)
        xin = np.concatenate([np.zeros((pd, 2)), xin])[:n]
        g = rng(self.seed)
        early = self._early(xin, n, g)

        # The early taps are NOT fed into the late network: a fixed tap pattern at
        # the FDN input shows up as a fixed autocorrelation peak in the whole tail.
        dl = xin[:, 0].copy()
        dr = xin[:, 1].copy()
        for d in self.DIFFUSERS:
            dl = allpass_block(dl, max(2, int(d * self.size)), self.diffusion)
            dr = allpass_block(dr, max(2, int(d * self.size * 1.071) + 1), self.diffusion)

        nl = len(self.BASE_DELAYS)
        L = np.array([max(256, int(d * self.size * sr / 44100)) for d in self.BASE_DELAYS], dtype=np.float64)
        H = _hadamard(nl)
        # per-line loss filter g_dc * [c, 1 - 2c, c]: one extra sample of delay, accounted for
        w8 = 2 * np.pi * 8000.0 / sr
        g_dc = 10.0 ** (-3.0 * (L + 1) / (self.rt60 * sr))
        g_hi = 10.0 ** (-3.0 * (L + 1) / (self.rt60_high * sr))
        c = np.clip((1 - g_hi / g_dc) / (2 * (1 - np.cos(w8))), 0.0, 0.25)
        signs_in = g.choice([-1.0, 1.0], size=(nl, 2))
        even = (np.arange(nl) % 2 == 0)[:, None]
        inj = 0.5 * np.where(even, signs_in[:, :1] * dl[None, :], signs_in[:, 1:] * dr[None, :])
        rates = self.mod_rate * g.uniform(0.55, 1.45, nl)
        if self.loop_period > 0:
            # whole cycles per loop: the modulated tail is then exactly periodic, so a
            # loop rendered in steady state has no seam in its reverb either
            rates = np.maximum(1.0, np.round(rates * self.loop_period)) / self.loop_period
        phases = g.uniform(0, 2 * np.pi, nl) + 2 * np.pi * rates * self.t_offset
        depth = self.mod_depth * g.uniform(0.7, 1.0, nl) * min(1.0, self.size)

        maxd = int(L.max() + depth.max()) + 8
        s = np.zeros((nl, n + maxd))
        out = np.zeros((nl, n))
        B = int(L.min() - depth.max() - 4)
        cc = c[:, None]
        for t0 in range(0, n, B):
            t1 = min(t0 + B, n)
            tt = np.arange(t0, t1)
            dly = L[:, None] + depth[:, None] * np.sin(2 * np.pi * rates[:, None] * tt[None, :] / sr
                                                       + phases[:, None])
            pos = (tt[None, :] + maxd) - dly
            o = g_dc[:, None] * (cc * _lagrange3(s, pos) + (1 - 2 * cc) * _lagrange3(s, pos - 1)
                                 + cc * _lagrange3(s, pos - 2))
            out[:, t0:t1] = o
            s[:, t0 + maxd:t1 + maxd] = inj[:, t0:t1] + H @ o
        tap_l = H[1] * np.sqrt(nl)
        tap_r = H[2] * np.sqrt(nl)
        late = np.stack([tap_l @ out, tap_r @ out], axis=1) / np.sqrt(nl)
        if self.width < 1.0:
            mid = late.mean(axis=1, keepdims=True)
            late = mid + self.width * (late - mid)
        return late + self.early_level * early
