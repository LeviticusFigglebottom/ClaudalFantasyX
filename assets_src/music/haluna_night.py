"""`haluna_night`: Haluna at night (M2-AUD-03; vertical_slice.md B11, the dock): an 83.5 s seamless loop.

Original composition for this project (SPEC §2, §9). The brief: "haluna_village stripped back to flute and a
drone, slower." The same tune (haluna_theme.py) at 46 dotted-quarter beats per minute, freer: the flute breathes
between phrases and the B phrase comes an octave lower, closer, as if played on the dock for nobody. Under it a
D drone (D2, A2, D3) that breathes on a 21 s cycle, a low metallophone on every other downbeat, and two soft
kettle gongs. No drums, no lute: the town is asleep.

Form (bars of 2.61 s): 1-4 drone | 5-12 A | 13-16 the drone, two bars answered by the metallophone | 17-24 B,
an octave down | 25-28 the first cell, very soft | 29-32 the drone alone into the wrap.

Render:  python3 assets_src/music/haluna_night.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("haluna_theme", os.path.join(os.path.dirname(__file__), "haluna_theme.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

OUT = os.path.join(ROOT, "assets", "audio", "music", "haluna_night.ogg")
SEED = 20261105
TARGET_LUFS = -16.0
BPM = 46.0
E8 = 60.0 / BPM / 3.0
BAR = 6 * E8
BARS = 32
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
CHORDS = ["D"] * 4 + T.CHORDS_A + ["G", "A", "G", "A"] + T.CHORDS_B + ["D", "D", "G", "A"] + ["D", "D", "G", "A"]
CELL = [("F#5", 2), ("E5", 1), ("D5", 2), ("E5", 1), ("F#5", 3), ("A5", 3), ("E5", 6)]


def bar_t(bar: int, eighth: float = 0.0) -> float:
    return (bar - 1) * BAR + eighth * E8


def _snap(f: float) -> float:
    return max(1.0, round(f * LOOP_S)) / LOOP_S


def drone(sr: int = SR) -> np.ndarray:
    """Exactly periodic D drone (D2 A2 D3), breathing on a 21 s cycle; one loop long, stereo."""
    g = rng(SEED + 3)
    N = int(round(LOOP_S * sr))
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * _snap(1 / 21.0) * t)
    for root, lvl in ((n("D2"), 1.0), (n("A2"), 0.42), (n("D3"), 0.30)):
        f0 = midi_to_hz(root)
        for k, a in ((1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)):
            for side, det in ((0, 0.0), (1, 0.07 + 0.02 * k)):
                s = lvl * a * (1.0 + 0.35 * (k - 1) / 4 * (breath - 0.5) * 2)
                s = s * np.sin(2 * np.pi * _snap(f0 * k + det) * t + g.uniform(0, 2 * np.pi))
                out[:, side] += s
                out[:, 1 - side] += 0.6 * s
    return out * 0.05


def add_flute(mx: LoopMixer, notes: list, start: float, seed: int, vel: float, pan: float, octave: int = 0) -> None:
    """The tune, freer than by day: each phrase-half leans (a little slower into its long note)."""
    g = rng(seed)
    t = start
    first = True
    for i, (p, d) in enumerate(notes):
        stretch = 1.06 if d >= 3 else 0.98
        dur = d * E8 * stretch
        if p is None:
            t += dur
            first = True
            continue
        x = breath_flute(n(p) + 12 * octave, dur * 0.97 + 0.05, vel * g.uniform(0.93, 1.04), seed=seed + 7 * i,
                         breath=0.42, scoop_cents=60.0 if first else 22.0, vib_cents=14.0 if d >= 3 else 5.0,
                         vib_rate=4.4, swell=0.32 if d >= 5 else 0.0, attack=0.10 if first else 0.05, release=0.45)
        mx.add("flute", x, t - FLUTE_PRE + float(g.normal(0, 0.008)), pan=pan)
        t += dur
        first = False


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", drone(), 0.0)
    for bar in range(1, BARS + 1, 2):
        root = n(T.BASS[CHORDS[bar - 1]]) + 24
        x = metallophone_note(root, 0.30 * g.uniform(0.9, 1.05), seed=SEED + 100 + bar, decay=5.0, hardness=0.22,
                              ombak_hz=3.4)
        mx.add("metal", x, bar_t(bar), pan=0.1)
    for bar, cell in ((14, ["A5", "F#5", "E5"]), (16, ["B5", "A5", "E5"])):
        for i, p in enumerate(cell):
            x = metallophone_note(n(p), 0.22, seed=SEED + 300 + 10 * bar + i, decay=4.0, hardness=0.3, ombak_hz=4.6)
            mx.add("metal", x, bar_t(bar, 1.5 * i), pan=0.45)
    add_flute(mx, T.notes_in_order([T.PHRASE_A]), bar_t(5), SEED + 600, 0.46, -0.1)
    add_flute(mx, T.notes_in_order([T.PHRASE_B]), bar_t(17), SEED + 700, 0.44, -0.1, octave=-1)
    add_flute(mx, CELL, bar_t(25), SEED + 800, 0.34, 0.05)
    for bar, p in ((12, "D5"), (24, "A4")):
        mx.add("gong", kettle_gong(n(p), 0.24, seed=SEED + 900 + bar, t60=3.5), bar_t(bar), pan=0.3)


# Bus gains from measured bus loudness: the drone -9 LU under the flute, the metallophone -9, the gongs -14.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    mx.bus("drone", -9.5, send=0.25, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(1400, 0.6)]))
    mx.bus("flute", 0.0, send=0.42)
    mx.bus("metal", 0.9, send=0.45)
    mx.bus("gong", -6.6, send=0.5)
    build(mx)
    hall = ModFDNReverb(rt60=2.6, rt60_high=1.2, predelay=0.025, size=1.0, mod_depth=8.0, mod_rate=0.45,
                        early_level=0.22, lowcut=100.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-2.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM * 3 / 2, 2)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"haluna_night: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
