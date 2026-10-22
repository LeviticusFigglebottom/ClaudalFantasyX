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
