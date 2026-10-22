"""Score-as-code helpers: note names, a tempo map with ritardandi, and a
plain event list that cue scripts fill and instruments render.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

_NOTE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")
_PC = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)


def n(name: str | int | float) -> float:
    """'C4' -> 60, 'F#3' -> 54, 'Bb5' -> 82. Numbers pass through."""
    if isinstance(name, (int, float)):
        return float(name)
    mm = _NOTE.match(name.strip())
    if not mm:
        raise ValueError(f"bad note name {name!r}")
    letter, acc, octv = mm.groups()
    v = _PC[letter.upper()] + (1 if acc == "#" else -1 if acc == "b" else 0)
    return float(12 * (int(octv) + 1) + v)


def ns(names: str) -> list[float]:
    """'A2 E3 B3 C4' -> [45, 52, 59, 60]."""
    return [n(x) for x in names.split()]


class TempoMap:
    """Beats -> seconds. Tempo is piecewise linear between (beat, bpm) points,
    integrated numerically on a fine grid (deterministic)."""

    def __init__(self, points: list[tuple[float, float]], total_beats: float, res: int = 64):
        pts = sorted(points)
        self.res = res
        grid = np.arange(int(total_beats * res) + res * 8 + 1) / res
        bpm = np.interp(grid, [p[0] for p in pts], [p[1] for p in pts])
        dt = 60.0 / bpm / res
        self.grid = grid
        self.times = np.concatenate([[0.0], np.cumsum(dt[:-1])])

    def t(self, beat: float) -> float:
        return float(np.interp(beat, self.grid, self.times))


@dataclass
class Event:
    inst: str
    beat: float          # absolute beat (0-based)
    beats: float         # duration in beats
    pitch: object        # MIDI number or list (chords)
    vel: float = 0.5
    opts: dict = field(default_factory=dict)


class Score:
    def __init__(self, beats_per_bar: int = 3):
        self.bpb = beats_per_bar
        self.events: list[Event] = []

    def at(self, bar: int, beat: float = 1.0) -> float:
        """Bar and beat are 1-based, like sheet music."""
        return (bar - 1) * self.bpb + (beat - 1)

    def add(self, inst, bar, beat, pitch, beats, vel=0.5, **opts):
        p = [n(x) for x in pitch] if isinstance(pitch, (list, tuple)) else n(pitch)
        self.events.append(Event(inst, self.at(bar, beat), beats, p, vel, opts))

    def line(self, inst, bar, notes, vel=0.5, beat=1.0, **opts):
        """Add a monophonic line: notes = [(pitch | None for rest, beats[, vel]), ...]."""
        b = self.at(bar, beat)
        for item in notes:
            p, d = item[0], item[1]
            v = item[2] if len(item) > 2 else vel
            if p is not None:
                self.events.append(Event(inst, b, d, n(p), v, dict(opts)))
            b += d
        return b
