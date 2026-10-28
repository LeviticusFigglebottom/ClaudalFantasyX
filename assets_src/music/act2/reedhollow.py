"""`reedhollow` (final): Ch10, Reedhollow, the Kirru roost-village on the mangrove roots (M3-AUD-840; the
M3-AUD-804 sketch grown into a full piece; act_outline Ch10, bible §5.5, §8): a 153.8 s seamless loop.

Original composition for this project (SPEC §2, §9). The sketch's material (assets_src/music/reedhollow.py: the
whistlers' call, answer, climb and head, the root-harp's figure, the clutch's rising line, the chords, every voice
and level) is imported from it, not retyped, and the sketch file is untouched. Original-material check: the new
section's whistled phrases (bars 15-22) are built from the call's own cell (a step, a step, a slide up and a leap)
moved onto F-sharp and B, and they end in silence as the sketch's do; the harp's second figure keeps the 3+2 shape
with its tones reordered; the clutch's second rising (bars 29-34) is the sketch's line carried one step further, to
G#, the top of a rise. None is taken from any melody we know, and the style stays invented (whistles, a plucked
frame over water, a floating drum, tongue-clicks). Haluna's material is still absent.

The brief (as the sketch): the Kirru are tall, still, unhurried and fond of silence; they talk in whistle-clicks;
their dead are sung off at dusk with the farewell-tide, a wordless rising song, and then the clutch turns its back
(bible §8). So the music rises and never comes down to rest, its phrases end in silence, and the last two bars are
only clicks and the harp's root: the backs turned.

The clutch line is kept apart in `CLUTCH_LINES` and `add_clutch` so it can be swapped whole: act3_plan.md §4 Q2 may
have it carry the Letting's first cell once that motif exists. Nothing else reads it.

The Kirru mode on A: A B C# D# F# (G# as the top of a rise); no fifth (no E anywhere). Harmony between A (A C# F#) and
B (B D# F#), with F-sharp minor in the middle. 5/4 at 78 BPM, grouped 3+2 (a bar is 3.846 s), 40 bars.

Form (bars):
*  1-4   the roost: harp, gourds, clicks (the sketch's bars 1-4)
*  5-10  A, the whistlers' call and answer, then the climb (the sketch's A)
* 11-14  B, the clutch's rising line, the whistles silent (the sketch's B)
* 15-22  C, new: the two whistlers overlapping over F#m B F#m A B F#m B B, the harp's second figure, a third gourd
         stroke on beat 3
* 23-28  A', the call and the answer in stretto (the answer a bar behind), the climb, a bar of harp alone
* 29-34  B', the clutch's line again, rising one step further (to G#), one whistle rising above it in bar 33
* 35-38  the roost thinning; the call's first cell once more (bar 37)
* 39-40  the backs turned: only clicks and the harp's root, which leads back to bar 1

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth. Vorbis q3.

Render:  python3 assets_src/music/act2/reedhollow.py   (or tools/audio/render_all.py --act2 --only act2/reedhollow)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

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


SK = _mod("reedhollow_sketch", os.path.join(HERE, "..", "reedhollow.py"))
V = SK.V

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "reedhollow.ogg")
SEED = SK.SEED + 840_000
TARGET_LUFS = SK.TARGET_LUFS
BPM, BEAT, BAR = SK.BPM, SK.BEAT, SK.BAR
BARS = 40
LOOP_S = BARS * BAR
LEAD_IN_BEATS = SK.LEAD_IN_BEATS
t_of = SK.t_of

CHORDS = (SK.CHORDS[:14]
          + ["F#m", "B", "F#m", "A", "B", "F#m", "B", "B"]
          + SK.CHORDS[4:10]
          + ["A", "B", "F#m", "B", "A", "B"]
          + ["A", "B", "A", "A"]
          + ["A", "A"])
assert len(CHORDS) == BARS
NEW_SECTION = range(15, 23)
BACKS_TURNED = (39, 40)

## the harp's second figure for the new section: the 3+2 shape, its tones reordered
HARP_PAT_C = [(0, 0, 0.6, 0.0), (1, 2, 0.32, 0.0), (2, 1, 0.4, 0.0), (3, 3, 0.45, 120.0), (5, 4, 0.42, 0.0),
              (6, 2, 0.5, 0.0), (7, 4, 0.38, 0.0), (8, 3, 0.45, 150.0), (9, 1, 0.3, 0.0)]

## the new section's whistled phrases: (bar list, start bar, start beat, whistler); a bar is (pitch | None, beats, rise)
NEW_PHRASES = [
    ([[("C#5", 1, False), ("D#5", .5, False), ("F#5", 1.5, True), ("A5", 2, True)],
      [("G#5", 1, False), ("F#5", 1, False), (None, 3, False)]], 15, 0.0, 0),
    ([[("F#4", 1.5, False), ("A4", .5, False), ("B4", 1, True), ("C#5", 2, True)],
      [("B4", 1, False), ("A4", 1, False), (None, 3, False)]], 17, 0.0, 1),
    ([[("D#5", 1, False), ("F#5", .5, False), ("G#5", 1.5, True), (None, 2, False)],
      [("A5", 3, True), (None, 2, False)]], 19, 0.0, 0),
    ([[("C#5", 1.5, True), ("D#5", 1.5, True), (None, 2, False)]], 20, 0.0, 1),
    ([[("F#5", 2, True), ("D#5", 1, False), ("C#5", 2, False)]], 21, 0.0, 0),
    ([[("B4", 2, True), ("A4", 1, False), (None, 1, False)]], 21, 1.0, 1),
]
## the sketch's phrases (bar list, start bar, start beat, whistler), placed for the final
PHRASES = ([(bars, start, 0.0, who) for bars, start, who in SK.PHRASES if start < 15]
           + NEW_PHRASES
           + [(SK.CALL, 23, 0.0, 0), (SK.ANSWER, 24, 0.0, 1), (SK.CLIMB, 26, 0.0, 0),
              ([[(None, 2, False), ("F#5", 1, True), ("G#5", 2, True)]], 33, 0.0, 1),
              (SK.HEAD, 37, 0.0, 1)])

## --- the clutch (the farewell-tide). Swappable as a unit: act3_plan.md §4 Q2 may put the Letting's first cell
## here. Each entry: (start bar, length in bars, line of (pitch, beats)).
CLUTCH_LINES = [
    (11, 4, SK.CLUTCH),
    (29, 6, SK.CLUTCH + [("G#4", 10)]),           # the second rising, one step further: G#, the top of a rise
]


def add_clutch(mx: LoopMixer, start_bar: int, bars: int, line: list, seed: int) -> None:
    """The clutch's wordless rising line (the sketch's recipe): fades in over 2.5 s and away over its last second."""
    x = hum_ensemble([(n(p), b * BEAT) for p, b in line], voices=10, seed=seed, register="high", spread=0.9)
    env = np.ones(len(x))
    k = int(2.5 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    s = int((bars * BAR - 1.0) * SR)
    env[s:] = np.exp(-np.arange(len(env) - s) / SR / 1.2)
    mx.add("clutch", x * env[:, None], t_of(start_bar) - 0.2)
## --- end of the clutch


def add_whistles(mx: LoopMixer) -> None:
    g = rng(SEED + 600)
    for k, (bars, start, beat0, who) in enumerate(PHRASES):
        notes, pos = [], 0.0
        for bar in bars:
            for p, beats, rise in bar:
                if p is not None:
                    notes.append((pos * BEAT, beats * BEAT * 0.97, n(p), 0.75 * float(g.uniform(0.92, 1.04)), rise))
                pos += beats
        lead = notes[0][0]
        notes = [(s - lead, d, m, v, r) for s, d, m, v, r in notes]
        x = V.kirru_whistle(notes, SEED + 610 + k, vib_cents=16.0 if who == 0 else 22.0)
        mx.add("whistle", x, t_of(start, beat0) + lead + float(g.normal(0, 0.01)), pan=-0.35 if who == 0 else 0.35)


def add_harp(mx: LoopMixer, body: np.ndarray) -> None:
    g = rng(SEED + 100)
    for bar, ch in enumerate(CHORDS, start=1):
        tones = [n(p) for p in SK.HARP[ch].split()]
        pat = SK.HARP_LAST if bar in BACKS_TURNED else HARP_PAT_C if bar in NEW_SECTION else SK.HARP_PAT
        for eighth, idx, vel, rise in pat:
            v = vel * float(g.uniform(0.88, 1.06)) * (1.1 if eighth in (0, 6) else 1.0)
            x = V.root_harp(tones[idx], v, SEED + 1000 + 16 * bar + eighth, body, rise_cents=rise)
            mx.add("harp", x, t_of(bar, eighth / 2) + float(g.normal(0, 0.007)), pan=-0.25 + 0.12 * idx)


def add_drums(mx: LoopMixer) -> None:
    g = rng(SEED + 200)
    for bar in range(1, BARS + 1):
        x = V.gourd(n("A2"), 0.6 * float(g.uniform(0.9, 1.06)), SEED + 2000 + bar)
        mx.add("gourd", x, t_of(bar) + float(g.normal(0, 0.006)), pan=0.1)
        if bar not in (1, 2) + BACKS_TURNED:
            x = V.gourd(n("B2"), 0.42 * float(g.uniform(0.9, 1.06)), SEED + 2100 + bar)
            mx.add("gourd", x, t_of(bar, 3) + float(g.normal(0, 0.006)), pan=-0.15)
        if bar in NEW_SECTION:
            x = V.gourd(n("C#3"), 0.28 * float(g.uniform(0.9, 1.06)), SEED + 2200 + bar)
            mx.add("gourd", x, t_of(bar, 2) + float(g.normal(0, 0.006)), pan=0.3)
        # the clicks: the Kirru talking, on the offbeats (more of them while the backs are turned)
        count = 6 if bar in BACKS_TURNED else int(g.integers(2, 5))
        slots = g.choice([1, 3, 5, 7, 9], size=min(count, 5), replace=False)
        for s in sorted(int(v) for v in slots):
            f = float(g.choice([1900.0, 2600.0]))
            pan = float(g.uniform(-0.7, 0.7))
            t0 = t_of(bar, s / 2) + float(g.normal(0, 0.01))
            mx.add("clicks", V.tongue_click(g, float(g.uniform(0.5, 0.9)), f), t0, pan=pan)
            if g.random() < 0.35:
                mx.add("clicks", V.tongue_click(g, float(g.uniform(0.4, 0.7)), f * 1.12), t0 + 0.07, pan=pan)


def build(mx: LoopMixer) -> None:
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("A2"), 1.0), (n("C#3"), 0.3), (n("F#3"), 0.25)], SEED + 3,
                                     partials=5, breath_s=LOOP_S / 10), 0.0)
    add_harp(mx, V.root_harp_body(SK.SEED + 5))
    add_drums(mx)
    add_whistles(mx)
    for k, (start, bars, line) in enumerate(CLUTCH_LINES):
        add_clutch(mx, start, bars, line, SEED + 11 + k)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = SK.GAINS
    mx.bus("whistle", G["whistle"], send=0.35, process=lambda x: filt(x, [bq_highpass(200, 0.7),
                                                                           bq_lowpass(5000, 0.7)]))
    mx.bus("harp", G["harp"], send=0.35, process=lambda x: filt(x, [bq_lowpass(4500, 0.7)]))
    mx.bus("gourd", G["gourd"], send=0.30, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    mx.bus("clicks", G["clicks"], send=0.40, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    mx.bus("clutch", G["clutch"], send=0.60)
    mx.bus("drone", G["drone"], send=0.30, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    build(mx)
    air = ModFDNReverb(rt60=1.9, rt60_high=0.9, predelay=0.02, size=1.0, mod_depth=7.0, mod_rate=0.4,
                       early_level=0.3, lowcut=120.0, seed=SK.SEED % 9973)
    return V.finish(mx, "reedhollow (final)", out_path, BPM, 5, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, air, -3.5,
                    verbose, stats)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
