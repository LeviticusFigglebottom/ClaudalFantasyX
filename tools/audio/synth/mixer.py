"""A small offline mixer: stereo buses with gain / pan / reverb send, a shared
reverb return, a transparent look-ahead peak limiter, loudness normalization
to a LUFS target, and Vorbis encoding through ffmpeg.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field

import numpy as np

from .dsp import SR, bq_highpass, db_to_lin, filt, pan_mono
from .loudness import integrated_lufs, momentary_max_lufs, sample_peak_dbfs, true_peak_dbtp
from .reverb import FDNReverb

FFMPEG = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"


@dataclass
class Bus:
    name: str
    gain_db: float = 0.0
    send: float = 0.0           # linear send level into the shared reverb
    process: object = None      # optional callable(stereo) -> stereo, applied pre-fader
    buf: np.ndarray = field(default=None, repr=False)


class Mixer:
    def __init__(self, seconds: float, sr: int = SR):
        self.sr = sr
        self.n = int(seconds * sr)
        self.buses: dict[str, Bus] = {}

    def bus(self, name: str, gain_db: float = 0.0, send: float = 0.0, process=None) -> Bus:
        b = Bus(name, gain_db, send, process, np.zeros((self.n, 2)))
        self.buses[name] = b
        return b

    def add(self, bus: str, sig: np.ndarray, start: float, pan: float = 0.0, gain: float = 1.0) -> None:
        """Place a mono (panned) or stereo signal at `start` seconds on a bus."""
        b = self.buses[bus]
        s = int(round(start * self.sr))
        if s >= self.n:
            return
        st = pan_mono(sig, pan) if sig.ndim == 1 else sig
        e = min(self.n, s + len(st))
        b.buf[s:e] += gain * st[: e - s]

    def render(self, reverb: FDNReverb | None = None, reverb_return_db: float = 0.0) -> np.ndarray:
        dry = np.zeros((self.n, 2))
        send = np.zeros((self.n, 2))
        for b in self.buses.values():
            x = b.process(b.buf) if b.process else b.buf
            x = x * db_to_lin(b.gain_db)
            dry += x
            if b.send > 0:
                send += b.send * x
        if reverb is not None and np.any(send):
            wet = reverb.process(send, tail=0.0)[: self.n]
            dry += db_to_lin(reverb_return_db) * wet
        return filt(dry, [bq_highpass(28, 0.6, self.sr)], sr=self.sr)


# --------------------------------------------------------------------------- #
# Dynamics and loudness
# --------------------------------------------------------------------------- #
def _running_min_centered(x: np.ndarray, half: int) -> np.ndarray:
    """min over [n-half, n+half] using O(log) doubling passes."""
    pad = np.ones(half)
    y = np.concatenate([pad, x, pad])
    w = 1
    m = y.copy()
    target = 2 * half + 1
    while w * 2 <= target:
        m[:-w] = np.minimum(m[:-w], m[w:])
        w *= 2
    if w < target:  # finish with an overlapping window (min is idempotent)
        r = target - w
        m[:-r] = np.minimum(m[:-r], m[r:])
    return m[: len(x)]


def _box_centered(x: np.ndarray, L: int) -> np.ndarray:
    cs = np.concatenate([[0.0], np.cumsum(x)])
    h = L // 2
    i = np.arange(len(x))
    a = np.clip(i - h, 0, len(x))
    b = np.clip(i - h + L, 0, len(x))
    return (cs[b] - cs[a]) / np.maximum(b - a, 1)


def limit_gain(x: np.ndarray, ceiling_db: float = -1.5, window_ms: float = 6.0, sr: int = SR) -> np.ndarray:
    """The gain curve limit() applies to x (1.0 where it does nothing). Apply it to the stems of x to limit them
    linked: their sum is then exactly limit(x), and no stem is ever made louder (M2-AUD-03 boss stems)."""
    c = db_to_lin(ceiling_db)
    peak = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
    req = np.minimum(1.0, c / np.maximum(peak, 1e-12))
    if req.min() >= 1.0:
        return np.ones(len(x))
    W = max(4, int(window_ms * sr / 1000))
    return np.minimum(_box_centered(_running_min_centered(req, W), W), 1.0)


def limit(x: np.ndarray, ceiling_db: float = -1.5, window_ms: float = 6.0, sr: int = SR) -> np.ndarray:
    """Zero-latency (offline, look-ahead) linked-stereo peak limiter.

    Gain is the windowed minimum of the required gain, then box-smoothed with a
    window half as long, which guarantees the ceiling at every sample peak while
    keeping the gain curve smooth (no clicks, ~6 ms attack/release).
    """
    c = db_to_lin(ceiling_db)
    peak = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
    req = np.minimum(1.0, c / np.maximum(peak, 1e-12))
    if req.min() >= 1.0:
        return x
    W = max(4, int(window_ms * sr / 1000))
    g = _box_centered(_running_min_centered(req, W), W)
    g = np.minimum(g, 1.0)
    return x * (g[:, None] if x.ndim == 2 else g)


def normalize_integrated(x: np.ndarray, target_lufs: float = -16.0, ceiling_db: float = -1.5,
                         sr: int = SR, iters: int = 4) -> np.ndarray:
    """Gain to target integrated loudness, peak-limit, repeat until within 0.1 LU."""
    y = x
    for _ in range(iters):
        cur = integrated_lufs(y, sr)
        y = limit(y * db_to_lin(target_lufs - cur), ceiling_db, sr=sr)
        if abs(integrated_lufs(y, sr) - target_lufs) < 0.1:
            break
    return y


def normalize_momentary(x: np.ndarray, target_lufs: float, ceiling_db: float = -3.0, sr: int = SR) -> np.ndarray:
    """For short SFX: gain so the 400 ms momentary max hits the target, then limit."""
    y = x * db_to_lin(target_lufs - momentary_max_lufs(x, sr))
    return limit(y, ceiling_db, window_ms=2.0, sr=sr)


def measure(x: np.ndarray, sr: int = SR) -> dict:
    return dict(integrated_lufs=integrated_lufs(x, sr), momentary_max_lufs=momentary_max_lufs(x, sr),
                sample_peak_dbfs=sample_peak_dbfs(x), true_peak_dbtp=true_peak_dbtp(x),
                seconds=len(x) / sr)


# --------------------------------------------------------------------------- #
# Encoding
# --------------------------------------------------------------------------- #
def write_ogg(path: str, x: np.ndarray, sr: int = SR, quality: float = 4.0, tags: dict | None = None) -> None:
    """Encode float audio to Ogg Vorbis with ffmpeg/libvorbis, bit-exact flags on
    so the Ogg stream serial and metadata do not change between runs.

    `tags` become Vorbis comments (e.g. LOOPSTART / LOOPLENGTH in samples)."""
    x = np.clip(np.asarray(x, dtype=np.float64), -1.0, 1.0)
    ch = 1 if x.ndim == 1 else x.shape[1]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    meta = []
    for k, v in sorted((tags or {}).items()):
        meta += ["-metadata", f"{k}={v}"]
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "f32le", "-ar", str(sr), "-ac", str(ch), "-i", "pipe:0",
           "-map_metadata", "-1", *meta, "-fflags", "+bitexact", "-flags:a", "+bitexact",
           "-c:a", "libvorbis", "-q:a", str(quality), "-ar", str(sr), path]
    subprocess.run(cmd, input=x.astype("<f4").tobytes(), check=True)


def read_audio(path: str, sr: int = SR, channels: int = 2) -> np.ndarray:
    """Decode any file back to float for verification (uses ffmpeg)."""
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-i", path, "-f", "f32le",
           "-ac", str(channels), "-ar", str(sr), "pipe:1"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype="<f4").astype(np.float64)
    return y.reshape(-1, channels) if channels > 1 else y
