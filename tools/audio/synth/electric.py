"""The rock/fusion layer: plucked bass, electric guitar strings, and an amp.

* `string_pluck` is a modal plucked string: harmonic partials with a little
  stiffness, a pick-position comb, frequency-dependent decay, a short
  pitch-sharp attack, and palm muting (heavy high-partial damping and a fast
  decay). Bass and guitar both use it.
* `bass_note` adds a sub-fundamental reinforcement and a finger/pick thump.
* `power_chord` strums root, fifth and octave a few ms apart.
* `Amp` is a bus processor: mid-hump pre-EQ, two asymmetric soft-clip
  stages with an interstage high-pass, all at 4x oversampling (FFT
  resampling in overlapping chunks, so harmonics above Nyquist do not fold
  back as inharmonic aliases), then a synthesized 4x12-style cabinet
  (resonant low end, presence peak, steep roll-off above ~5 kHz, plus a short
  random "cone" response for the irregular ripple of a real speaker).

A distorted guitar is a nonlinear *bus* effect, so notes are summed first
and the amp runs once per track; double-tracked guitars are two tracks with
independent takes, panned hard left and right.
"""
from __future__ import annotations

import numpy as np

from .dsp import (SR, bq_highpass, bq_highshelf, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz,
                  rng)


def string_pluck(m: float, dur: float, vel: float = 0.7, seed: int = 0, sr: int = SR, pick_pos: float = 0.13,
                 t60: float = 3.0, mute: float = 0.0, B: float = 6e-5, max_f: float = 6000.0,
                 release: float = 0.05) -> np.ndarray:
    """Mono plucked string. mute = 0 (open) .. 1 (hard palm mute)."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    K = int(max(1, min(60, max_f / f0)))
    k = np.arange(1, K + 1, dtype=np.float64)
    fk = k * f0 * np.sqrt(1 + B * k * k)
    amp = np.abs(np.sin(np.pi * k * pick_pos)) / k ** 0.9
    amp *= 1.0 / (1.0 + (fk / (900.0 + 4500.0 * vel * (1 - 0.85 * mute))) ** 2)
    T1 = t60 * (1 - 0.94 * mute)
    Tk = T1 / (1.0 + (fk / (1400.0 * (1 - 0.8 * mute))) ** 1.4)
    hold = min(dur, 7.0 * T1)
    L = hold + release * 4 + 0.01
    N = int(L * sr)
    t = np.arange(N) / sr
    # damping after the note's end (fret hand lifts / mute)
    rel = np.where(t > hold, np.exp(-(t - hold) / release), 1.0)
    sharp = 1.0 + (0.0012 + 0.002 * vel) * np.exp(-t / 0.03)        # pluck goes a little sharp
    phase = 2 * np.pi * np.cumsum(sharp) / sr
    out = np.zeros(N)
    for i in range(K):
        if fk[i] > 0.45 * sr:
            break
        n_i = min(N, int(min(L, 6.0 * Tk[i]) * sr))
        out[:n_i] += amp[i] * np.exp(-6.91 * t[:n_i] / Tk[i]) * np.sin(fk[i] * phase[:n_i] + g.uniform(-0.3, 0.3))
    out *= rel
    nn = int(0.004 * sr)
    out[:nn] += 0.15 * vel * filt(g.standard_normal(nn), [bq_highpass(1500, 0.7, sr)], sr=sr) * np.linspace(1, 0, nn)
    out *= np.minimum(1.0, t / 0.0004)
    k2 = min(N // 4, int(0.01 * sr))
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.25 * vel * out


def bass_note(m: float, dur: float, vel: float = 0.7, seed: int = 0, sr: int = SR, mute: float = 0.15) -> np.ndarray:
    """Fingered electric bass: pluck + sub reinforcement + thump."""
    g = rng(seed + 1)
    x = string_pluck(m, dur, vel, seed=seed, sr=sr, pick_pos=0.18, t60=2.4, mute=mute, B=1.2e-4, max_f=3500.0,
                     release=0.03)
    N = len(x)
    t = np.arange(N) / sr
    f0 = midi_to_hz(m)
    env = np.exp(-t / (0.9 * (1 - 0.6 * mute))) * np.minimum(1.0, t / 0.004)
    env *= np.where(t > dur, np.exp(-(t - dur) / 0.03), 1.0)
    x += 0.10 * vel * env * np.sin(2 * np.pi * f0 * t)
    nn = min(N, int(0.03 * sr))
    th = filt(g.standard_normal(nn), [bq_lowpass(220, 0.8, sr)], sr=sr) * np.exp(-np.arange(nn) / sr / 0.008)
    x[:nn] += 0.05 * vel * th / (np.abs(th).max() + 1e-9)
    return x


def power_chord(root: float, dur: float, vel: float = 0.8, seed: int = 0, sr: int = SR, mute: float = 0.0,
                octave: bool = True, strum: float = 0.008) -> np.ndarray:
    notes = [root, root + 7] + ([root + 12] if octave else [])
    g = rng(seed)
    parts = []
    for j, p in enumerate(notes):
        d = int((j * strum + g.uniform(0, 0.002)) * sr)
        x = string_pluck(p, dur, vel * (1 - 0.08 * j), seed=seed + 31 * j, sr=sr, pick_pos=0.12, t60=3.5,
                         mute=mute, B=8e-5, max_f=5000.0, release=0.04)
        parts.append(np.concatenate([np.zeros(d), x]))
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[: len(p)] += p
    return out


# --------------------------------------------------------------------------- #
# Amp
# --------------------------------------------------------------------------- #
def oversampled(x: np.ndarray, fn, factor: int = 4, chunk: int = 1 << 15, margin: int = 2048) -> np.ndarray:
    """Apply a memoryless nonlinearity at `factor` x the sample rate (mono x).

    Overlap-save in chunks: each chunk (plus margins) is band-limited-upsampled
    by FFT zero-padding, shaped, low-passed and decimated by FFT truncation,
    and only the centre is kept."""
    n = len(x)
    out = np.zeros(n)
    xp = np.concatenate([np.zeros(margin), x, np.zeros(margin + chunk)])
    for s in range(0, n, chunk):
        seg = xp[s: s + chunk + 2 * margin]
        L = len(seg)
        X = np.fft.rfft(seg)
        up = np.fft.irfft(np.concatenate([X, np.zeros(L * factor // 2 + 1 - len(X))]), L * factor) * factor
        y = fn(up)
        Y = np.fft.rfft(y)[: L // 2 + 1]
        Y[-1] = 0.0
        down = np.fft.irfft(Y, L) / factor
        e = min(chunk, n - s)
        out[s: s + e] = down[margin: margin + e]
    return out


def _clip_stage(x: np.ndarray, bias: float) -> np.ndarray:
    return np.tanh(x + bias) - np.tanh(bias)


def cabinet_ir(seed: int = 412, sr: int = SR) -> np.ndarray:
    """A synthesized closed-back 4x12-style speaker cabinet response."""
    g = rng(seed)
    n = int(0.012 * sr)
    t = np.arange(n) / sr
    cone = g.standard_normal(n) * np.exp(-t / 0.0012)
    cone = filt(cone, [bq_lowpass(6000, 0.7, sr)], sr=sr)
    cone /= np.sqrt((cone ** 2).sum())
    ir = np.zeros(n)
    ir[0] = 1.0
    ir += 0.45 * cone
    ir = filt(ir, [bq_highpass(78, 1.0, sr), bq_peak(115, 3.5, 1.2, sr), bq_peak(420, -3.0, 0.9, sr),
                   bq_peak(2300, 4.0, 1.3, sr), bq_peak(3600, 2.0, 2.0, sr), bq_lowpass(4800, 0.75, sr),
                   bq_lowpass(5200, 0.65, sr)], tail=0.05, sr=sr, keep_tail=True)
    return ir / np.abs(np.fft.rfft(ir, 8192)).max()


class Amp:
    """High-gain amp + cab for one mono track. Use one instance per guitar track."""

    def __init__(self, drive_db: float = 30.0, bias: float = 0.18, tone_db: float = 1.0, seed: int = 412,
                 sr: int = SR, in_gain: float = 6.0):
        self.drive = 10 ** (drive_db / 20)
        self.in_gain = in_gain          # fixed (not signal-derived), so intro and loop renders match
        self.bias = bias
        self.tone_db = tone_db
        self.sr = sr
        self.cab = cabinet_ir(seed, sr)

    def mono(self, x: np.ndarray) -> np.ndarray:
        sr = self.sr
        pre = filt(x, [bq_highpass(95, 0.7, sr), bq_peak(760, 8.0, 0.8, sr), bq_lowpass(6500, 0.7, sr)], sr=sr)
        pre = pre * self.in_gain
        y = oversampled(pre * self.drive, lambda v: _clip_stage(v, self.bias))
        y = filt(y, [bq_highpass(180, 0.7, sr), bq_lowpass(7000, 0.7, sr)], sr=sr)
        y = oversampled(y * 3.0, lambda v: _clip_stage(v, -0.08))
        y = fft_convolve(y, self.cab)[: len(x)]
        y = filt(y, [bq_highshelf(3000, self.tone_db, 0.7, sr)], sr=sr)
        return y / self.in_gain

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Stereo bus in, stereo out: each channel is treated as its own track."""
        return np.stack([self.mono(x[:, 0]) if np.any(x[:, 0]) else x[:, 0],
                         self.mono(x[:, 1]) if np.any(x[:, 1]) else x[:, 1]], axis=1)
