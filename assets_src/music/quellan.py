"""`quellan`: Ch12, Quellan, the highland town of stone and woven awnings (M3-AUD-804 sketch; act_outline Ch12,
bible §5.7): a 62.6 s seamless loop.

Original composition for this project (SPEC §2, §9). The tune, its harmony line, the strum pattern and every part
below were written for this cue. Original-material check: the tune is built from one cell of our own (C-A-C, a leap
up to the tonic F, then a stepwise fall E-D-C) and its second phrase, which reaches A5 and comes down through the
relative minor; it is not taken from any melody we know. The style evoked is a highland town's (a small bright lute
strummed long-short-short on every beat, a warm flute, a bass drum on the downbeat), quoting no tune and no real
instrument's repertoire. Nothing is borrowed from another cue.

The brief: Quellan is warm against the cold of Keth Pass: thick walls of fitted stone, layered hand-woven cloth in
dense patterns, woolback herders coming in with their animals' bells (bible §5.7). The Ullari are stoic about death
in a way the coast finds cold, but at home they are a town like any other, and this is the first warm room after
the pass. So: a major key, a dancing strum, a close, small room and the herds outside.

F major (F G A Bb C D E; the turnaround at the end borrows C7's B-flat), 4/4 at 92 BPM (a bar is 2.609 s), 24 bars.
Apart from every Act I cue: the only cue in F major, and the only highland one (Keth Pass, next to it, is in E
minor and 6/8).

Ensemble (all synthesized; no samples):
* a breath flute in its warm middle (E4-A5), low breath: the tune; a second flute a third below it in A' (bars
  17-24), softer;
* the ten-string (act2_voices.ten_string): a small, deep-backed lute of paired wire courses, strummed down on each
  beat and up-down on the second half (long-short-short), high and bright;
* a fingered bass (synth.electric.bass_note) on beats 1 and 3;
* a big drum on 1, a frame drum's slap on the "and" of 2 and a ghost on 4;
* outside: the woolbacks' bells (act2_voices.herd_bell), wooden clonks in small uneven clusters, far off.

Form (bars): 1-4 the town (strum, bass, drums, the herds) | 5-12 A, the flute | 13-16 B, over Dm Bb F C | 17-24 A',
the flute and its third below, and a C7 turnaround in the last half-bar back to bar 1's F.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a sixteenth between strums.

Render:  python3 assets_src/music/quellan.py   (or tools/audio/render_all.py --only quellan)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__), "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT = os.path.join(ROOT, "assets", "audio", "music", "quellan.ogg")
SEED = 20261806
TARGET_LUFS = -16.0
BPM = 92.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 24
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
QUALITY = 3.0

## one chord per bar, or two (first half | second half)
CHORDS = (["F", "F", "Bb", "C"]
          + ["F", "C", "Bb", "C", "F", "Dm", "Bb|C", "F"]
          + ["Dm", "Bb", "F", "C"]
          + ["F", "C", "Bb", "C", "F", "Dm", "Bb|C", "F|C7"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 4 + ["A2"] * 8
STRUM = {"F": "F4 A4 C5 F5", "C": "E4 G4 C5 E5", "Bb": "F4 Bb4 D5 F5", "Dm": "F4 A4 D5 F5", "C7": "E4 Bb4 C5 E5"}
BASS = {"F": ("F2", "C2"), "C": ("C2", "G2"), "Bb": ("Bb1", "F2"), "Dm": ("D2", "A2"), "C7": ("C2", "G2")}
## the strum on each beat: (offset in beats, up stroke, velocity, mute): long-short-short
STROKES = [(0.0, False, 0.62, 0.0), (0.5, True, 0.40, 0.25), (0.75, False, 0.44, 0.3)]

## the tune: one list per bar of (pitch | None, beats)
TUNE_A = [
    [("C5", 1), ("A4", .5), ("C5", .5), ("F5", 2)],
    [("E5", 1), ("D5", 1), ("C5", 2)],
    [("Bb4", 1), ("D5", .5), ("C5", .5), ("Bb4", 1), ("F4", 1)],
    [("G4", 3), (None, 1)],
    [("C5", 1), ("A4", .5), ("C5", .5), ("F5", 1.5), ("G5", .5)],
    [("A5", 1), ("G5", .5), ("F5", .5), ("D5", 2)],
    [("D5", 1), ("Bb4", .5), ("A4", .5), ("G4", 1), ("E4", 1)],
    [("F4", 3), (None, 1)],
]
TUNE_B = [
    [("D5", 2), ("F5", 1), ("E5", 1)],
    [("D5", 1), ("C5", 1), ("Bb4", 2)],
    [("A4", 1.5), ("C5", .5), ("F5", 1), ("E5", 1)],
    [("D5", 2), ("C5", 1), (None, 1)],
]
SCALE = ["F", "G", "A", "Bb", "C", "D", "E"]

LEAD = "flute"
LEVELS = {"flute": 0.0, "flute2": -5.0, "strum": -5.0, "bass": -9.0, "drums": -10.0, "bells": -16.0}
GAINS = {"flute": 0.0, "flute2": -3.2, "strum": -8.9, "bass": -4.2, "drums": -1.7, "bells": -18.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def third_below(p: str) -> str:
    """The diatonic third below a note of F major (two scale steps down)."""
    name, octv = p[:-1], int(p[-1])
    i = SCALE.index(name)
    j = i - 2
    if j < 0:
        j += 7
    # the octave number changes when the step down crosses C
    lower = SCALE[j]
    oc = octv - 1 if ("CDEFGAB".index(lower[0]) > "CDEFGAB".index(name[0])) else octv
    return f"{lower}{oc}"


def add_flute(mx: LoopMixer, bus: str, bars: list, start_bar: int, seed: int, vel: float, pan: float,
              harmony: bool = False) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            m = n(third_below(p)) if harmony else n(p)
            v = vel * float(g.uniform(0.94, 1.04)) * (1.04 if beats >= 2 else 1.0)
            x = breath_flute(m, d * 0.94 + 0.02, v, seed=seed + int(round(pos * 1000)), breath=0.4,
                             scoop_cents=35.0 if first else 10.0, vib_cents=12.0 if beats >= 2 else 4.0,
                             vib_rate=4.8, swell=0.2 if beats >= 2 else 0.0, attack=0.07 if first else 0.04,
                             release=0.3, beta=0.5)
            mx.add(bus, x, pos - V.FLUTE_PRE + float(g.normal(0, 0.005)), pan=pan)
            pos += d
            first = False


def chord_at(bar: int, beat: float) -> str:
    parts = CHORDS[bar - 1].split("|")
    return parts[0] if (len(parts) == 1 or beat < 2) else parts[1]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = V.ten_string_body(SEED + 5)
    for bar in range(1, BARS + 1):
        for beat in range(4):
            ch = chord_at(bar, beat)
            tones = [n(p) for p in STRUM[ch].split()]
            for off, up, vel, mute in STROKES:
                x = V.strum(tones, BEAT * (0.9 if off == 0 else 0.4), vel * float(g.uniform(0.9, 1.06)),
                            SEED + 1000 + 16 * bar + 4 * beat + int(off * 4), body, up=up, mute=mute)
                mx.add("strum", x, t_of(bar, beat + off) + float(g.normal(0, 0.005)), pan=0.3)
        for beat, idx in ((0, 0), (2, 1)):
            ch = chord_at(bar, beat)
            x = bass_note(n(BASS[ch][idx]), BEAT * 1.6, 0.6 * float(g.uniform(0.92, 1.05)),
                          seed=SEED + 300 + 4 * bar + beat)
            mx.add("bass", x, t_of(bar, beat) + float(g.normal(0, 0.004)), pan=-0.05)
        mx.add("drums", big_drum(0.36, variant=bar, seed=SEED + 2), t_of(bar), pan=0.0)
        if SECTION[bar - 1] != "I" or bar >= 3:
            x = frame_drum("tek", 0.26 * float(g.uniform(0.9, 1.08)), variant=bar, size=1.0, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, 1.5) + float(g.normal(0, 0.005)), pan=-0.2)
            x = frame_drum("ghost", 0.18 * float(g.uniform(0.9, 1.08)), variant=bar + 2, size=1.0, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, 3) + float(g.normal(0, 0.005)), pan=-0.2)
    # the herds outside: clusters of two to four clonks, each animal's bell its own pitch
    pos = float(g.uniform(0.3, 1.5))
    while pos < LOOP_S - 1.0:
        f = float(g.choice([620.0, 710.0, 830.0, 955.0]))
        pan = float(g.uniform(-0.9, 0.9))
        tt = pos
        for _ in range(int(g.integers(2, 5))):
            mx.add("bells", V.herd_bell(g, float(g.uniform(0.4, 0.9)), f), tt, pan=pan)
            tt += float(g.uniform(0.18, 0.5))
        pos += float(g.uniform(2.0, 5.0))
    add_flute(mx, "flute", TUNE_A, 5, SEED + 600, 0.55, -0.08)
    add_flute(mx, "flute", TUNE_B, 13, SEED + 620, 0.55, -0.08)
    add_flute(mx, "flute", TUNE_A, 17, SEED + 640, 0.55, -0.08)
    add_flute(mx, "flute2", TUNE_A, 17, SEED + 660, 0.45, 0.35, harmony=True)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=6.0)
    G = GAINS
    fl = [bq_highpass(170, 0.7), bq_peak(1500, 1.0, 1.0), bq_lowpass(6500, 0.7)]
    mx.bus("flute", G["flute"], send=0.30, process=lambda x: filt(x, fl))
    mx.bus("flute2", G["flute2"], send=0.35, process=lambda x: filt(x, fl))
    mx.bus("strum", G["strum"], send=0.25, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_lowpass(7000, 0.7)]))
    mx.bus("bass", G["bass"], send=0.10, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.bus("drums", G["drums"], send=0.25, process=lambda x: filt(x, [bq_lowpass(4000, 0.7)]))
    mx.bus("bells", G["bells"], send=0.5, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    build(mx)
    room = ModFDNReverb(rt60=1.5, rt60_high=0.7, predelay=0.015, size=0.8, mod_depth=6.0, mod_rate=0.5,
                        early_level=0.35, lowcut=140.0, seed=SEED % 9973)
    return V.finish(mx, "quellan", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, room, -4.0, verbose,
                    stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
