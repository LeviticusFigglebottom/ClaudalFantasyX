"""`cloudloom`: Ch12, Cloudloom, the Ullari's open-roofed weaving-hall (M4-A2P-091; act2_plan.md §2 Ch12; the cue
sheet): a 120 s seamless zone loop.

Original composition for this project (SPEC §2, §9). The loom figure, the chords and the women's line were written
for this cue. The style evoked is a work-song for weavers: the shuttle's pattern becomes the rhythm. No phrase is
taken from any existing tune. There is no Order hum: this is the Ullari's place, not the Order's.

The brief (act2_plan Ch12; art/environments/keth_pass.md): the stair up, then the open-roofed hall with thousands of
keth cords, and noon light writing their shadows on white stone. Hesk is bound here. Reverent and busy at once. So:
* **the loom figure:** plucked strings in eighths grouped 3+3+2 (the beater's three strokes and the shuttle's pass),
  through each bar's chord, with a wooden beater click on each group's first eighth;
* **the light:** a high metallophone shimmer, one or two tones a bar, from bar 9;
* **the weavers:** a few women humming a long line in A minor (bars 17-28), written for this cue, without words;
* the figure thins to itself for the last two bars, which lead back to bar 1.

A minor, 4/4 at 72 BPM (a bar is 3.33 s), 36 bars. A minor ties it to Keth Pass's E minor and lifts to Hesk's A major
binding (hesk_bound). Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file, which starts a sixteenth before bar 1's
downbeat (the sidecar's `downbeat_offset_s`). Vorbis q3, -16 LUFS integrated. Plain git (ADR 0175).

Render:  python3 tools/audio/render_all.py --only cloudloom
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "sfx"))

from field_ambience import modal  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))   # finish(): the Act II loops' render path

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "cloudloom.ogg")
SEED = 20261950
TARGET_LUFS = -16.0
BPM = 72.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 36
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
EIGHTH = BEAT / 2
PROGRESSION = ["Am", "F", "C", "G", "Am", "F", "G", "Am"]
CHORDS = (PROGRESSION * 5)[:BARS - 2] + ["Am", "Am"]
VOICING = {"Am": "A2 E3 A3 C4 E4", "F": "F2 C3 F3 A3 C4", "C": "C3 G3 C4 E4 G4", "G": "G2 D3 G3 B3 D4"}
# The loom figure: (eighth, voicing index, velocity); groups of 3+3+2, each group led by a low tone
FIGURE = [(0, 0, 0.62), (1, 3, 0.36), (2, 4, 0.38), (3, 1, 0.55), (4, 3, 0.34), (5, 4, 0.36), (6, 2, 0.52),
          (7, 4, 0.33)]
THIN = (BARS - 1, BARS)
SHIMMER_FROM = 9
# The weavers' line (bars 17-28): (pitch, beats); 48 beats, 12 bars
WEAVERS = [("A4", 4), ("C5", 4), ("B4", 2), ("A4", 2), ("E5", 8), ("D5", 4), ("C5", 4), ("B4", 4), ("A4", 4),
           ("G4", 4), ("A4", 8)]
WEAVERS_AT = 17
GAINS = {"loom": 0.0, "beater": -10.0, "pad": -12.0, "shimmer": -7.0, "weavers": 2.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def beater(g, vel: float):
    b = float(g.uniform(290, 330))
    return vel * modal([b, b * 2.3, b * 4.4], [0.03, 0.018, 0.01], [1.0, 0.5, 0.2], 0.12, g, click=0.6)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, ch in enumerate(CHORDS, start=1):
        tones = [n(p) for p in VOICING[ch].split()]
        figure = FIGURE[:3] + FIGURE[6:7] if bar in THIN else FIGURE
        for eighth, idx, vel in figure:
            v = vel * float(g.uniform(0.9, 1.05))
            x = string_pluck(tones[idx], EIGHTH * 2.2, v, seed=SEED + 100 + 16 * bar + eighth, pick_pos=0.14, t60=1.6,
                             B=5e-5, max_f=6000.0, release=0.1)
            mx.add("loom", x, t_of(bar) + eighth * EIGHTH + float(g.normal(0, 0.005)), pan=-0.3 + 0.15 * idx)
            if eighth in (0, 3, 6):
                mx.add("beater", beater(g, 0.8 if eighth == 0 else 0.6), t_of(bar) + eighth * EIGHTH, pan=0.35)
        x = pad_chord([t - 12 for t in tones[:3]], BAR * 1.02, 0.35, seed=SEED + 300 + bar, attack=0.9, release=1.4)
        mx.add("pad", x, t_of(bar) - 0.1)
        if SHIMMER_FROM <= bar < THIN[0]:                                  # the light through the open roof
            for k in range(int(g.integers(1, 3))):
                m = tones[int(g.integers(2, 5))] + 24
                mx.add("shimmer", metallophone_note(m, 0.3 * float(g.uniform(0.7, 1.0)), seed=SEED + 400 + 4 * bar + k,
                                                    decay=3.0, hardness=0.25, pair=False),
                       t_of(bar, float(g.choice([0.0, 1.5, 2.0, 3.0]))), pan=float(g.uniform(-0.8, 0.8)))
    line = [(n(p), b * BEAT) for p, b in WEAVERS]
    mx.add("weavers", hum_ensemble(line, voices=6, seed=SEED + 500, register="high", spread=0.8), t_of(WEAVERS_AT) - 0.1)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = GAINS
    mx.bus("loom", G["loom"], send=0.35, process=lambda x: filt(x, [bq_highpass(80, 0.7), bq_lowpass(5500, 0.7)]))
    mx.bus("beater", G["beater"], send=0.3, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1200.0))
    mx.bus("shimmer", G["shimmer"], send=0.6, process=lambda x: filt(x, [bq_lowpass(8000, 0.7)]))
    mx.bus("weavers", G["weavers"], send=0.5, process=lambda x: filt(x, [bq_lowpass(3200, 0.7)]))
    build(mx)
    hall = ModFDNReverb(rt60=2.2, rt60_high=1.1, predelay=0.03, size=1.5, mod_depth=8.0, mod_rate=0.35,
                        early_level=0.25, lowcut=100.0, seed=SEED % 9973)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "cloudloom", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -2.0, verbose,
                    stats, quality=3.0)


if __name__ == "__main__":
    render()
