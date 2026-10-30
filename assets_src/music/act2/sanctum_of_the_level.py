"""`sanctum_of_the_level`: Ch13, the Sanctum of the Level (M4-A2P-091; act2_plan.md §2 Ch13; the cue sheet): a 120 s
seamless zone loop. It is the one Act II loop where monotony is the design.

Original composition for this project (SPEC §2, §9). The held chord, the bell's place and the glass halo were written
for this cue; the only borrowed line is our own: ORDER_HUM (motifs.py), its first notes hummed far off. Nothing is
taken from any existing music.

The brief (act2_plan Ch13): the still basin lit from beneath by a light that never moves. Awe that becomes unease;
Liss stands before the light; Ethren is bound here; Kerrid never enters. So nothing in the cue moves:
* one C-major chord (Ansedra's key), low and wide, held through the whole loop. It **never changes**, and its
  partials are snapped to the loop so the seam cannot be heard;
* a bell every four bars, the same note each time (C3, dark), and nothing answers it;
* a glass halo: a few high partials of the chord, steady, just audible;
* the Order's hum far off, its first four notes, twice a loop, as if from another room.
The listening report should list this cue's flatness as intended, not as a flaw.

C major, 4/4 at 40 BPM (a bar is 6.0 s), 20 bars. Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file, which starts a
sixteenth before bar 1's downbeat (the sidecar). Vorbis q3, -16 LUFS integrated. Plain git (ADR 0175).

Render:  python3 tools/audio/render_all.py --only sanctum_of_the_level
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import ORDER_HUM  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))   # periodic_drone(), finish()

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "sanctum_of_the_level.ogg")
SEED = 20261960
TARGET_LUFS = -16.0
BPM = 40.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 20
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
CHORD = [("C2", 1.0), ("G2", 0.6), ("C3", 0.45), ("E3", 0.3), ("G3", 0.25)]
HALO = [("E5", 0.6), ("G5", 0.5), ("C6", 0.35)]
BELL_BARS = (1, 5, 9, 13, 17)
HUM_BARS = (3, 13)
GAINS = {"chord": -3.0, "halo": -20.0, "bell": -6.0, "hum": -10.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("chord", V.periodic_drone(LOOP_S, [(n(p), lvl) for p, lvl in CHORD], SEED + 1, partials=6,
                                     breath_s=LOOP_S / 2), 0.0)
    mx.add("halo", V.periodic_drone(LOOP_S, [(n(p), lvl) for p, lvl in HALO], SEED + 2, partials=2,
                                    breath_s=LOOP_S / 4), 0.0)
    for k, bar in enumerate(BELL_BARS):
        mx.add("bell", tower_bell(n("C3"), 0.55, seed=SEED + 10 + k, t60=9.0, dark=0.6), t_of(bar), pan=0.15)
    line = [(float(m), b * BEAT) for m, b in ORDER_HUM[:4]]
    for k, bar in enumerate(HUM_BARS):
        x = hum_ensemble(line, voices=10, seed=SEED + 20 + k, register="low", spread=0.6)
        env = np.ones(len(x))
        f = int(2.0 * SR)
        env[:f] = np.linspace(0, 1, f)
        env[-f:] = np.linspace(1, 0, f)
        mx.add("hum", x * env[:, None], t_of(bar), pan=-0.4 + 0.8 * k + float(g.normal(0, 0.05)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=14.0)
    G = GAINS
    mx.bus("chord", G["chord"], send=0.4, process=lambda x: filt(x, [bq_lowpass(1600, 0.7)]))
    mx.bus("halo", G["halo"], send=0.6, process=lambda x: filt(x, [bq_highpass(500, 0.7)]))
    mx.bus("bell", G["bell"], send=0.6, process=lambda x: filt(x, [bq_lowpass(4000, 0.7)]))
    mx.bus("hum", G["hum"], send=0.8, process=lambda x: filt(x, [bq_lowpass(1200, 0.7)]))     # from another room
    build(mx)
    basin = ModFDNReverb(rt60=6.0, rt60_high=2.0, predelay=0.06, size=2.0, mod_depth=4.0, mod_rate=0.15,
                         early_level=0.15, lowcut=60.0, seed=SEED % 9973)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "sanctum_of_the_level", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, basin, -2.0,
                    verbose, stats, quality=3.0)


if __name__ == "__main__":
    render()
