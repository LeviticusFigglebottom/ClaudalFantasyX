"""`reedhollow`: Ch10, Reedhollow, the Kirru roost-village on the mangrove roots (M3-AUD-804 sketch; act_outline
Ch10, bible §5.5, §8): a 61.5 s seamless loop.

Original composition for this project (SPEC §2, §9). The Kirru are a people with their own music, so this cue
invents its instruments and its mode instead of borrowing the coast's. Original-material check: the whistled tune is
built from one cell of our own (A-B-C#, then a leap up to F#, every long note sliding up into pitch) and its answer
a fourth below; the root-harp's figure and the clutch's rising line (A B C# D# F#, one step a bar, never coming
down) were written here. None is taken from any melody we know, and no folk or game tune is evoked note for note:
the style is invented (whistles, a plucked frame over water, a floating drum, tongue-clicks). Nothing is borrowed
from another cue, and Haluna's material (D major pentatonic, interlocking metallophones, the breath flute) is
deliberately absent.

The brief: woven reed lodges raised on mangrove roots. The Kirru are tall, still, unhurried and fond of silence;
among themselves they use whistle-clicks and hand-shapes; their dead are sung off at dusk with the farewell-tide, a
wordless rising song, and then the clutch turns its back so the dead are not anchored by being watched (bible §8).
So the music rises and never comes down to rest, its phrases end in silence rather than in cadences, and the last
bars are only clicks and the harp's root: the backs turned.

The Kirru mode, on A: A B C# D# F# (and G# as the top of a rise). It has no fifth (no E anywhere in the cue), so it
never sits down on a tonic chord the way the coast's music does; its raised fourth (D#) floats. The harmony moves
between A (A C# F#) and B (B D# F#) a whole tone apart, with F-sharp minor in the middle section. 5/4 at 78 BPM,
grouped 3+2 (a bar is 3.846 s), 16 bars. Apart from Haluna (D major pentatonic, 6/8) and from every Act I cue: the
only fifthless mode and the only 5/4 grouped 3+2.

Ensemble (all synthesized; no samples), all of it act2_voices.py's new voices:
* two whistlers (kirru_whistle): a low, near-pure whistle that glides between notes and slides up into its long
  ones, with a tongue-click at each phrase start; the first left, the answer right;
* the root-harp (root_harp): gut strings over a root frame and the water's hollow, a figure on every bar in the 3+2
  shape; on the "rise" notes the player presses the string up into pitch after the pluck;
* the water-gourds (gourd): low floating drums on the two group starts (beats 1 and 4);
* tongue-clicks (tongue_click), singly and in pairs, on the offbeats: the Kirru's talk;
* the clutch (synth.voice.hum_ensemble, high register, wordless) in the middle section: the farewell-tide's shape,
  one step up a bar;
* a faint drone on A, C# and F# (no fifth).

Form (bars): 1-4 the roost (harp, gourds, clicks) | 5-10 A, the whistlers' call and answer | 11-14 B, the clutch's
rising line, the whistles silent | 15 the call's first cell once more | 16 the backs turned: only clicks and the
harp's root, which leads back to bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/reedhollow.py   (or tools/audio/render_all.py --only reedhollow)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__), "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT = os.path.join(ROOT, "assets", "audio", "music", "reedhollow.ogg")
SEED = 20261802
TARGET_LUFS = -16.0
BPM = 78.0
BEAT = 60.0 / BPM
BAR = 5 * BEAT
BARS = 16
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25

CHORDS = (["A", "A", "B", "A"]
          + ["A", "B", "A", "B", "F#m", "B"]
          + ["A", "B", "F#m", "B"]
          + ["A", "A"])
## the harp's chord tones, low to high
HARP = {"A": "A3 C#4 F#4 A4 C#5", "B": "B3 D#4 F#4 B4 D#5", "F#m": "F#3 A3 C#4 F#4 A4"}
## the harp's figure: (eighth of the bar's ten, chord-tone index, velocity, rise in cents) in the 3+2 shape
HARP_PAT = [(0, 0, 0.6, 0.0), (2, 1, 0.4, 0.0), (3, 2, 0.45, 0.0), (4, 3, 0.5, 150.0), (6, 4, 0.5, 0.0),
            (7, 2, 0.4, 0.0), (8, 3, 0.45, 120.0)]
HARP_LAST = [(0, 0, 0.55, 0.0), (6, 3, 0.35, 150.0)]

## the whistled tune: phrases of (bar list, start bar, whistler); a bar is a list of (pitch | None, beats, rise)
CALL = [[("A4", 1, False), ("B4", .5, False), ("C#5", 1.5, True), ("F#5", 2, True)],
        [("D#5", 1, False), ("C#5", 1, False), ("B4", 1, False), (None, 2, False)]]
ANSWER = [[("F#4", 1, False), ("A4", .5, False), ("B4", 1.5, True), ("D#5", 2, True)],
          [("C#5", 1.5, False), ("B4", .5, False), ("A4", 1, False), (None, 2, False)]]
CLIMB = [[("A4", 1, False), ("C#5", 1, False), ("D#5", 1, False), ("F#5", 1, True), ("G#5", 1, True)],
         [("F#5", 3, False), (None, 2, False)]]
HEAD = [[("A4", 1, False), ("B4", .5, False), ("C#5", 1.5, True), (None, 2, False)]]
PHRASES = [(CALL, 5, 0), (ANSWER, 7, 1), (CLIMB, 9, 0), (HEAD, 15, 1)]
## the clutch's rising line (bars 11-14): (pitch, beats)
CLUTCH = [("A3", 5), ("B3", 5), ("C#4", 2.5), ("D#4", 2.5), ("F#4", 5)]

LEAD = "whistle"
LEVELS = {"whistle": 0.0, "harp": -6.0, "gourd": -9.0, "clicks": -13.0, "clutch": -3.0, "drone": -15.0}
GAINS = {"whistle": 0.0, "harp": -11.1, "gourd": -4.1, "clicks": -0.5, "clutch": 1.1, "drone": -11.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_whistles(mx: LoopMixer) -> None:
    g = rng(SEED + 600)
    for k, (bars, start, who) in enumerate(PHRASES):
        notes, pos = [], 0.0
        for bar in bars:
            for p, beats, rise in bar:
                if p is not None:
                    notes.append((pos * BEAT, beats * BEAT * 0.97, n(p), 0.75 * float(g.uniform(0.92, 1.04)), rise))
                pos += beats
        x = V.kirru_whistle(notes, SEED + 610 + k, vib_cents=16.0 if who == 0 else 22.0)
        mx.add("whistle", x, t_of(start) + float(g.normal(0, 0.01)), pan=-0.35 if who == 0 else 0.35)


def add_harp(mx: LoopMixer, body: np.ndarray) -> None:
    g = rng(SEED + 100)
    for bar, ch in enumerate(CHORDS, start=1):
        tones = [n(p) for p in HARP[ch].split()]
        for eighth, idx, vel, rise in (HARP_LAST if bar == BARS else HARP_PAT):
            v = vel * float(g.uniform(0.88, 1.06)) * (1.1 if eighth in (0, 6) else 1.0)
            x = V.root_harp(tones[idx], v, SEED + 1000 + 16 * bar + eighth, body, rise_cents=rise)
            pan = -0.25 + 0.12 * idx
            mx.add("harp", x, t_of(bar, eighth / 2) + float(g.normal(0, 0.007)), pan=pan)


def add_drums(mx: LoopMixer) -> None:
    g = rng(SEED + 200)
    for bar in range(1, BARS + 1):
        x = V.gourd(n("A2"), 0.6 * float(g.uniform(0.9, 1.06)), SEED + 2000 + bar)
        mx.add("gourd", x, t_of(bar) + float(g.normal(0, 0.006)), pan=0.1)
        if bar not in (1, 2, BARS):
            x = V.gourd(n("B2"), 0.42 * float(g.uniform(0.9, 1.06)), SEED + 2100 + bar)
            mx.add("gourd", x, t_of(bar, 3) + float(g.normal(0, 0.006)), pan=-0.15)
        # the clicks: the Kirru talking, on the offbeats (more of them in the stillness of the last bar)
        count = 6 if bar == BARS else int(g.integers(2, 5))
        slots = g.choice([1, 3, 5, 7, 9], size=min(count, 5), replace=False)
        for s in sorted(int(v) for v in slots):
            f = float(g.choice([1900.0, 2600.0]))
            pan = float(g.uniform(-0.7, 0.7))
            t0 = t_of(bar, s / 2) + float(g.normal(0, 0.01))
            mx.add("clicks", V.tongue_click(g, float(g.uniform(0.5, 0.9)), f), t0, pan=pan)
            if g.random() < 0.35:
                mx.add("clicks", V.tongue_click(g, float(g.uniform(0.4, 0.7)), f * 1.12), t0 + 0.07, pan=pan)


def add_clutch(mx: LoopMixer) -> None:
    line = [(n(p), b * BEAT) for p, b in CLUTCH]
    x = hum_ensemble(line, voices=10, seed=SEED + 11, register="high", spread=0.9)
    env = np.ones(len(x))
    k = int(2.5 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    s = int((4 * BAR - 1.0) * SR)
    env[s:] = np.exp(-np.arange(len(env) - s) / SR / 1.2)
    mx.add("clutch", x * env[:, None], t_of(11) - 0.2)


def build(mx: LoopMixer) -> None:
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("A2"), 1.0), (n("C#3"), 0.3), (n("F#3"), 0.25)], SEED + 3,
                                     partials=5, breath_s=LOOP_S / 4), 0.0)
    add_harp(mx, V.root_harp_body(SEED + 5))
    add_drums(mx)
    add_whistles(mx)
    add_clutch(mx)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = GAINS
    mx.bus("whistle", G["whistle"], send=0.35, process=lambda x: filt(x, [bq_highpass(200, 0.7),
                                                                           bq_lowpass(5000, 0.7)]))
    mx.bus("harp", G["harp"], send=0.35, process=lambda x: filt(x, [bq_lowpass(4500, 0.7)]))
    mx.bus("gourd", G["gourd"], send=0.30, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    mx.bus("clicks", G["clicks"], send=0.40, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    mx.bus("clutch", G["clutch"], send=0.60)
    mx.bus("drone", G["drone"], send=0.30, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    build(mx)
    air = ModFDNReverb(rt60=1.9, rt60_high=0.9, predelay=0.02, size=1.0, mod_depth=7.0, mod_rate=0.4,
                       early_level=0.3, lowcut=120.0, seed=SEED % 9973)
    return V.finish(mx, "reedhollow", out_path, BPM, 5, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, air, -3.5,
                    verbose, stats)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
