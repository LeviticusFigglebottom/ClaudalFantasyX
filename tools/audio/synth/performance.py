"""Expressive performance: phrase rubato, dynamic shaping, voicing, pedalling.

The M1 sketch had only a global tempo map, +-6 ms jitter and +-5 % velocity
noise. A pianist does much more, and most of it is systematic, so it can be
modelled (after the "phrase arch" models of Todd 1992 and the KTH rule
system, and Palmer's melody-lead measurements):

* **Phrase arch.** Within a phrase, tempo and loudness rise together toward
  the climax and relax after it; the last notes get an extra ritardando.
  `Phrase.peak` places the climax (0..1), and the depths are small (a few %).
* **Voicing.** Melody notes are played louder than the accompaniment (a
  per-role velocity scale), and they *lead* in time by ~15-30 ms, more when
  the velocity difference is larger.
* **Metric and contour accents.** Downbeats are slightly stronger, high
  notes slightly louder, and the bass note of each left-hand figure leans.
* **Pedal.** A continuous sustain-pedal depth curve: legato ("syncopated")
  changes just after each new harmony's bass note, with human jitter in when
  the foot lifts and how far, occasional half-changes, a little drift while
  held, and a slow final release. Dampers then follow the curve per note
  (see `grand.damper_engagement`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .grand import PedalCurve


@dataclass
class Phrase:
    start: float                 # absolute beat (0-based)
    end: float
    peak: float = 0.6            # climax position inside the phrase, 0..1
    tempo_depth: float = 0.035   # +-3.5 % tempo swing over the arch
    dyn_depth: float = 0.12      # +-12 % velocity swing
    final_rit: float = 0.10      # extra slowing over the last 15 %


def arch(x: np.ndarray | float, peak: float) -> np.ndarray:
    """0 at both ends, 1 at `peak` (a warped half-sine)."""
    x = np.clip(np.asarray(x, dtype=np.float64), 0.0, 1.0)
    a = math.log(0.5) / math.log(min(max(peak, 0.05), 0.95))
    return np.sin(np.pi * x ** a)


class ExpressiveTempo:
    """Beats -> seconds with phrase rubato on top of a base (beat, bpm) map.

    Duck-types `score.TempoMap` (`t`, `grid`, `times`)."""

    def __init__(self, points: list[tuple[float, float]], total_beats: float, phrases: list[Phrase],
                 res: int = 64):
        pts = sorted(points)
        grid = np.arange(int(total_beats * res) + res * 8 + 1) / res
        bpm = np.interp(grid, [p[0] for p in pts], [p[1] for p in pts])
        for ph in phrases:
            m = (grid >= ph.start) & (grid < ph.end)
            x = (grid[m] - ph.start) / (ph.end - ph.start)
            f = 1.0 + ph.tempo_depth * (2.0 * arch(x, ph.peak) - 1.0)
            tail = np.clip((x - 0.85) / 0.15, 0, 1)
            f *= 1.0 - ph.final_rit * tail ** 2
            bpm[m] *= f
        self.bpm = bpm
        dt = 60.0 / bpm / res
        self.grid = grid
        self.times = np.concatenate([[0.0], np.cumsum(dt[:-1])])

    def t(self, beat: float) -> float:
        return float(np.interp(beat, self.grid, self.times))

    def local_bpm_range(self) -> tuple[float, float]:
        return float(self.bpm.min()), float(self.bpm.max())


def phrase_dynamics(beat: float, phrases: list[Phrase]) -> float:
    for ph in phrases:
        if ph.start <= beat < ph.end:
            x = (beat - ph.start) / (ph.end - ph.start)
            return 1.0 + ph.dyn_depth * (2.0 * float(arch(x, ph.peak)) - 1.0)
    return 1.0


@dataclass
class Voicing:
    scale: dict = field(default_factory=lambda: {"mel": 1.12, "inner": 0.80, "acc": 0.88, "bass": 0.95})
    lead_s: float = 0.018          # melody lead at equal velocity
    lead_per_vel: float = 0.06     # extra lead per unit velocity difference
    jitter_s: dict = field(default_factory=lambda: {"mel": 0.005, "inner": 0.007, "acc": 0.006, "bass": 0.005})
    vel_noise: float = 0.035


def shape_velocity(vel: float, role: str, beat: float, bpb: int, pitch: float, phrases: list[Phrase],
                   voicing: Voicing, g: np.random.Generator, contour_ref: float = 72.0) -> float:
    v = vel * voicing.scale.get(role, 1.0) * phrase_dynamics(beat, phrases)
    if abs(beat % bpb) < 1e-6:
        v *= 1.05                                   # metric accent
    if role == "mel":
        v *= 1.0 + 0.008 * (pitch - contour_ref)     # higher notes sing out a little
    v *= 1.0 + g.normal(0.0, voicing.vel_noise)
    return float(np.clip(v, 0.04, 1.0))


def onset_offset(role: str, vel: float, acc_vel: float, voicing: Voicing, g: np.random.Generator) -> float:
    """Seconds to add to the nominal onset (negative = early)."""
    off = g.normal(0.0, voicing.jitter_s.get(role, 0.006))
    if role == "mel":
        off -= min(0.035, voicing.lead_s + voicing.lead_per_vel * max(0.0, vel - acc_vel))
    return off


def plan_pedal(changes: list[float], start: float, end_release: float, release_len: float,
               g: np.random.Generator, half: set[int] | None = None, step: float = 0.002) -> PedalCurve:
    """Legato pedal: down shortly before `start`; at each harmony change time
    (seconds, the new bass note's onset) lift 20-60 ms after it, to near zero
    (or to ~0.35 for indices in `half`), and press again 90-200 ms after it.
    A slow release begins at `end_release` and lasts `release_len` seconds."""
    half = half or set()
    T = end_release + release_len + 1.0
    t = np.arange(0.0, T, step)
    d = np.zeros_like(t)

    def ramp(a: float, b: float, v0: float, v1: float) -> None:
        m = (t >= a) & (t < b)
        x = (t[m] - a) / max(b - a, 1e-6)
        d[m] = v0 + (v1 - v0) * (0.5 - 0.5 * np.cos(np.pi * x))
        d[t >= b] = v1

    level = 0.9 + 0.08 * g.random()
    ramp(max(0.0, start - 0.25), max(0.0, start - 0.25) + 0.12, 0.0, level)
    for i, tc in enumerate(changes):
        up_at = tc + g.uniform(0.02, 0.06)
        up_len = g.uniform(0.035, 0.07)
        low = 0.30 + 0.1 * g.random() if i in half else g.uniform(0.0, 0.10)
        hold = g.uniform(0.02, 0.06)
        down_len = g.uniform(0.06, 0.12)
        new_level = 0.86 + 0.13 * g.random()
        ramp(up_at, up_at + up_len, level, low)
        ramp(up_at + up_len + hold, up_at + up_len + hold + down_len, low, new_level)
        level = new_level
    # a little foot drift while held, never past fully down
    drift = np.interp(t, np.arange(0, T + 1.0, 0.7), g.uniform(-0.03, 0.03, len(np.arange(0, T + 1.0, 0.7))))
    d = np.where(d > 0.6, np.clip(d + drift, 0.0, 1.0), d)
    ramp(end_release, end_release + release_len, float(np.interp(end_release, t, d)), 0.0)
    return PedalCurve(t, d)
