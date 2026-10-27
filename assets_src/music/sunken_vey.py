"""`sunken_vey`: Ch11, Sunken Vey, the drowned galleries of the great Lit Age city (M3-AUD-804 sketch; act_outline
Ch11, bible §5.6): a 62.6 s seamless loop.

Original composition for this project (SPEC §2, §9). The glass song, its harmony and every part below were written
for this cue. Original-material check: the song is built from one cell of our own (a falling third, Bb-Ab-Gb, held
long) answered by a rise through the Dorian sixth (F-Ab-C); it comes from this cue's scale, not from any melody we
know. No style is quoted; the glass harmonica is the game's own voice for glimmer (sefir_theme.py), and its recipe
is copied into act2_voices.glass so that cue stays frozen. Nothing else is borrowed.

The brief: the largest Lit Age ruin still above water. Towered stone galleries stand chest-deep in a turquoise
lagoon, wrapped in strangler-fig roots, and the old ceramic conduits still pulse faintly with bound light. Silent,
gorgeous and dead (bible §5.6). Act II's colour is cold blue stone. So: submerged, glassy and slow; everything but
the glass is heard as if through water (low-passed), and nothing has an attack except the drowned bell and the
roots.

E-flat Dorian (Eb F Gb Ab Bb C Db; the raised sixth, C natural, is the light still in the conduits, and it is the
top of the song's answer over A-flat major), 3/4 at 46 BPM (a bar is 3.913 s), 16 bars. Apart from every Act I cue:
the only cue in E-flat minor and the slowest 3/4.

Ensemble (all synthesized; no samples):
* a glass harmonica (act2_voices.glass): the song (bars 5-15), and a second glass an octave below doubling its
  long notes in bars 9-15;
* the water: a low drone on Eb and Bb, low-passed hard (underwater), and a soft, very dark string pad on the
  chords;
* a drowned bell (synth.bells.tower_bell, dark, low-passed) on bars 1 and 9;
* the roots: a low, muted plucked string every other bar, felt more than heard;
* the conduits: a faint pair of high tones (Bb5 and Eb6) whose light pulses slowly, once every two beats;
* bubbles (synth.water.bubble) rising in short strings, far off and low-passed.

Form (bars): 1-4 the galleries (drone, pad, bell, conduits, bubbles) | 5-8 A, the song | 9-12 A', with the low
glass and the bell | 13-15 the song's last phrase, rising to the Dorian sixth and settling on Bb | 16 silence over
A-flat major, which leads back to bar 1's E-flat minor.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/sunken_vey.py   (or tools/audio/render_all.py --only sunken_vey)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__), "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT = os.path.join(ROOT, "assets", "audio", "music", "sunken_vey.ogg")
SEED = 20261803
TARGET_LUFS = -16.0
BPM = 46.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 16
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
QUALITY = 3.0

CHORDS = (["Ebm", "Ebm", "Ab", "Ebm"]
          + ["Ebm", "Gb", "Ab", "Bbm", "Db", "Gb", "Ab", "Ebm"]
          + ["Gb", "Ab", "Bbm", "Ab"])
PAD = {"Ebm": "Eb2 Bb2 Eb3 Gb3", "Gb": "Gb2 Db3 Gb3 Bb3", "Ab": "Ab2 Eb3 Ab3 C4", "Bbm": "Bb1 F2 Bb2 Db3",
       "Db": "Db2 Ab2 Db3 F3"}
ROOTS = {"Ebm": "Eb2", "Gb": "Gb1", "Ab": "Ab1", "Bbm": "Bb1", "Db": "Db2"}

## the glass song: one list per bar of (pitch | None, beats)
SONG = [
    [("Bb4", 2), ("Ab4", 1)],
    [("Gb4", 3)],
    [("F4", 1), ("Ab4", 1), ("C5", 1)],         # the Dorian sixth: the light in the conduits
    [("Bb4", 3)],
    [("Db5", 2), ("C5", 1)],
    [("Bb4", 1.5), ("Ab4", 1.5)],
    [("Ab4", 1), ("F4", 2)],
    [("Eb4", 3)],
    [("Gb4", 2), ("F4", 1)],
    [("Eb4", 1), ("F4", 1), ("C5", 1)],
    [("Bb4", 3)],
]

LEAD = "glass"
LEVELS = {"glass": 0.0, "glass_low": -6.0, "drone": -11.0, "pad": -12.0, "bell": -8.0, "roots": -13.0,
          "conduits": -16.0, "bubbles": -17.0}
GAINS = {"glass": 0.0, "glass_low": -5.4, "drone": -4.1, "pad": 7.3, "bell": -3.7, "roots": 2.4, "conduits": -0.8,
         "bubbles": -9.8}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_song(mx: LoopMixer) -> None:
    g = rng(SEED + 600)
    for i, bar in enumerate(SONG):
        b = 5 + i
        pos = t_of(b)
        for p, beats in bar:
            d = beats * BEAT
            v = 0.7 * float(g.uniform(0.92, 1.04))
            mx.add("glass", V.glass(n(p), d * 0.98, v, SEED + 700 + int(round(pos * 100))), pos - V.GLASS_PRE,
                   pan=-0.1)
            if b >= 9 and beats >= 2:
                mx.add("glass_low", V.glass(n(p) - 12, d * 0.98, v, SEED + 800 + int(round(pos * 100))),
                       pos - V.GLASS_PRE + 0.03, pan=0.25)
            pos += d


def conduits(sr: int = SR) -> np.ndarray:
    """The bound light in the conduits: Bb5 and Eb6, each a detuned pair, pulsing together once every two beats
    (a slow, soft, light-like swell, not a beat). Exactly one loop long, stereo."""
    g = rng(SEED + 7)
    N = int(round(LOOP_S * sr))
    t = np.arange(N) / sr
    puls = (0.5 + 0.5 * np.sin(2 * np.pi * V.snap(1.0 / (2 * BEAT), LOOP_S) * t - np.pi / 2)) ** 3
    out = np.zeros((N, 2))
    for k, (p, lvl) in enumerate((("Bb5", 1.0), ("Eb6", 0.6))):
        f0 = midi_to_hz(n(p))
        for side, det in ((0, 0.0), (1, 0.4 + 0.2 * k)):
            s = lvl * np.sin(2 * np.pi * V.snap(f0 + det, LOOP_S) * t + g.uniform(0, 6.28))
            out[:, side] += s
            out[:, 1 - side] += 0.5 * s
    return 0.03 * out * (0.15 + 0.85 * puls)[:, None]


def add_bubbles(mx: LoopMixer, g) -> None:
    pos = float(g.uniform(0.5, 2.0))
    while pos < LOOP_S - 0.5:
        count = int(g.integers(3, 8))
        pan = float(g.uniform(-0.8, 0.8))
        r0 = float(g.uniform(1.2, 3.0))
        tt = pos
        for k in range(count):
            x = bubble(r0 * float(g.uniform(0.8, 1.2)), float(g.uniform(0.4, 1.0)), rise=float(g.uniform(0.05, 0.15)))
            mx.add("bubbles", x, tt, pan=pan + 0.04 * k)
            tt += float(g.uniform(0.04, 0.12))
        pos += float(g.uniform(2.5, 6.0))


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("Eb2"), 1.0), (n("Bb2"), 0.4)], SEED + 3, partials=5,
                                     breath_s=LOOP_S / 4), 0.0)
    mx.add("conduits", conduits(), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.96, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=2.0, release=2.0, width=0.85)
        mx.add("pad", x, t_of(bar) - 0.5)
        if bar % 2 == 1:
            x = string_pluck(n(ROOTS[ch]), BAR, 0.5 * float(g.uniform(0.9, 1.05)), seed=SEED + 300 + bar,
                             pick_pos=0.22, t60=2.5, mute=0.4, B=1e-4, max_f=1500.0, release=0.2)
            mx.add("roots", x, t_of(bar) + float(g.normal(0, 0.01)), pan=0.05)
    for bar, vel in ((1, 0.7), (9, 0.55)):
        mx.add("bell", tower_bell(n("Eb3"), vel, seed=SEED + 500 + bar, t60=8.0, dark=0.9), t_of(bar), pan=-0.2)
    add_bubbles(mx, g)
    add_song(mx)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    G = GAINS
    water = [bq_lowpass(520, 0.7), bq_lowpass(700, 0.7)]
    mx.bus("glass", G["glass"], send=0.55, process=lambda x: filt(x, [bq_highpass(180, 0.7)]))
    mx.bus("glass_low", G["glass_low"], send=0.55, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.bus("drone", G["drone"], send=0.25, process=lambda x: filt(x, water))
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=700.0))
    mx.bus("bell", G["bell"], send=0.6, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("roots", G["roots"], send=0.3, process=lambda x: filt(x, water))
    mx.bus("conduits", G["conduits"], send=0.5)
    mx.bus("bubbles", G["bubbles"], send=0.4, process=lambda x: filt(x, [bq_lowpass(1600, 0.7)]))
    build(mx)
    hall = ModFDNReverb(rt60=4.6, rt60_high=1.2, predelay=0.045, size=1.4, mod_depth=10.0, mod_rate=0.3,
                        early_level=0.2, lowcut=90.0, seed=SEED % 9973)
    return V.finish(mx, "sunken_vey", out_path, BPM, 3, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -2.0, verbose,
                    stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
