"""`quellan`: Ch12, Quellan, the highland town of stone and woven awnings (M3-AUD-841 final of the M3-AUD-804
sketch; act_outline Ch12, bible §5.7): a 125.2 s seamless loop.

Original composition for this project (SPEC §2, §9). Original-material check: the tune, its B phrase and the
long-short-short strum are the sketch's (assets_src/music/quellan.py, loaded here, never retyped): one cell of our own
(C-A-C, a leap up to the tonic F, a stepwise fall E-D-C) and a second phrase that reaches A5 and comes down through
the relative minor. What this final adds was written for it: a contrasting middle in D minor (the same notes, the
relative minor's centre) where the strum gives way to picked courses and the flute sings a new, lower tune that
rises by thirds (F-A-D, C-E-A) and turns back down; the B phrase's return in thirds; and a closing town interlude.
The style evoked is a highland town's (a small bright lute, a warm flute, a bass drum on the downbeat), quoting no
tune and no real instrument's repertoire. Nothing is borrowed from another cue.

The brief: Quellan is warm against the cold of Keth Pass: thick walls of fitted stone, layered hand-woven cloth in
dense patterns, woolback herders coming in with their animals' bells. The Ullari are stoic about death in a way the
coast finds cold, but at home they are a town like any other, and this is the first warm room after the pass. The
middle is the weaving-room in the evening: quieter, picked rather than strummed, the herds coming in nearer.

F major (F G A Bb C D E; the turnaround borrows C7's B-flat), as the sketch. 4/4 at 92 BPM (a bar is 2.609 s),
48 bars.

Ensemble (the sketch's palette, all synthesized; no samples): a breath flute in its warm middle, and a second flute
a third below; the ten-string (act2_voices.ten_string), strummed long-short-short on every beat, or in the middle
picked a course at a time in eighths; a fingered bass (synth.electric.bass_note); a big drum on 1, a frame drum's
slap on the "and" of 2 and a ghost on 4; outside, the woolbacks' bells (act2_voices.herd_bell).

Form (bars):
*  1-4   the town (strum, bass, drums, the herds): F F Bb C;
*  5-12  A, the flute (the sketch's TUNE_A): F C Bb C F Dm Bb|C F;
* 13-16  B (TUNE_B): Dm Bb F C;
* 17-24  A', the flute and its third below;
* 25-32  C, the weaving-room: Dm Am Bb F | Gm Dm Bb C; picked courses, the bass on 1 only, the big drum alone, the
         herds nearer; the flute's new low tune;
* 33-36  B', the B phrase in thirds, the strum back;
* 37-44  A'', the tune in thirds again, the frame drum full;
* 45-48  the town again (F F Bb C|C7), the C7 turnaround in the last half-bar back to bar 1's F.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a sixteenth between strums.

Render:  python3 assets_src/music/act2/quellan.py   (or tools/audio/render_all.py --act2 --only act2/quellan)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("quellan_sketch", os.path.join(MUSIC, "quellan.py"))   # the sketch: its themes, voices and timing
V = S.V

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "quellan.ogg")
SEED = 20261843
TARGET_LUFS = -16.0
BPM, BEAT, BAR = S.BPM, S.BEAT, S.BAR
BARS = 48
LOOP_S = BARS * BAR
LEAD_IN_BEATS = S.LEAD_IN_BEATS
QUALITY = 3.0

_A = ["F", "C", "Bb", "C", "F", "Dm", "Bb|C", "F"]
CHORDS = (["F", "F", "Bb", "C"] + _A + ["Dm", "Bb", "F", "C"] + _A
          + ["Dm", "Am", "Bb", "F", "Gm", "Dm", "Bb", "C"]
          + ["Dm", "Bb", "F", "C"] + _A + ["F", "F", "Bb", "C|C7"])
SECTION = (["I"] * 4 + ["A"] * 8 + ["B"] * 4 + ["A2"] * 8 + ["C"] * 8 + ["B2"] * 4 + ["A3"] * 8 + ["I2"] * 4)
STRUM = dict(S.STRUM, Am="E4 A4 C5 E5", Gm="G4 Bb4 D5 G5")
BASS = dict(S.BASS, Am=("A1", "E2"), Gm=("G1", "D2"))
## C's picked courses: indices into the four-course voicing, one per eighth
PICK = [0, 2, 1, 3, 2, 1, 3, 2]
PICK_VEL = [0.5, 0.32, 0.36, 0.34, 0.42, 0.3, 0.36, 0.3]

## C, the weaving-room: a new, lower tune rising by thirds and turning back down (pitch | None, beats)
TUNE_C = [
    [("F4", 1), ("A4", 1), ("D5", 2)],
    [("C5", 1), ("E5", 1), ("A4", 2)],
    [("Bb4", 1), ("D5", .5), ("F5", .5), ("E5", 1), ("D5", 1)],
    [("C5", 3), (None, 1)],
    [("Bb4", 1), ("G4", 1), ("D5", 2)],
    [("F5", 1), ("E5", .5), ("D5", .5), ("A4", 2)],
    [("G4", 1), ("Bb4", 1), ("D5", 1), ("C5", 1)],
    [("C5", 2), ("E4", 1), ("G4", 1)],
]

LEAD = "flute"
LEVELS = dict(S.LEVELS, pick=-7.0)
GAINS = dict(S.GAINS, pick=-4.0)


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def chord_at(bar: int, beat: float) -> str:
    parts = CHORDS[bar - 1].split("|")
    return parts[0] if (len(parts) == 1 or beat < 2) else parts[1]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = V.ten_string_body(SEED + 5)
    for bar in range(1, BARS + 1):
        sec = SECTION[bar - 1]
        for beat in range(4):
            ch = chord_at(bar, beat)
            tones = [n(p) for p in STRUM[ch].split()]
            if sec == "C":
                for h in range(2):
                    k = 2 * beat + h
                    x = V.ten_string(tones[PICK[k]], BEAT * 0.9, PICK_VEL[k] * float(g.uniform(0.9, 1.06)),
                                     SEED + 3000 + 16 * bar + k, body)
                    mx.add("pick", x, t_of(bar, beat + 0.5 * h) + float(g.normal(0, 0.006)), pan=0.25)
                continue
            for off, up, vel, mute in S.STROKES:
                x = V.strum(tones, BEAT * (0.9 if off == 0 else 0.4), vel * float(g.uniform(0.9, 1.06)),
                            SEED + 1000 + 16 * bar + 4 * beat + int(off * 4), body, up=up, mute=mute)
                mx.add("strum", x, t_of(bar, beat + off) + float(g.normal(0, 0.005)), pan=0.3)
        for beat, idx in (((0, 0),) if sec == "C" else ((0, 0), (2, 1))):
            ch = chord_at(bar, beat)
            x = bass_note(n(BASS[ch][idx]), BEAT * (3.4 if sec == "C" else 1.6), 0.6 * float(g.uniform(0.92, 1.05)),
                          seed=SEED + 300 + 4 * bar + beat)
            mx.add("bass", x, t_of(bar, beat) + float(g.normal(0, 0.004)), pan=-0.05)
        mx.add("drums", big_drum(0.3 if sec == "C" else 0.36, variant=bar, seed=SEED + 2), t_of(bar), pan=0.0)
        if sec not in ("I", "C") or bar in (3, 4):
            x = frame_drum("tek", 0.26 * float(g.uniform(0.9, 1.08)), variant=bar, size=1.0, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, 1.5) + float(g.normal(0, 0.005)), pan=-0.2)
            x = frame_drum("ghost", 0.18 * float(g.uniform(0.9, 1.08)), variant=bar + 2, size=1.0, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, 3) + float(g.normal(0, 0.005)), pan=-0.2)
        if sec == "A3" and bar % 2 == 0:
            x = frame_drum("ghost", 0.14 * float(g.uniform(0.9, 1.08)), variant=bar + 5, size=1.0, seed=SEED + 1)
            mx.add("drums", x, t_of(bar, 3.5) + float(g.normal(0, 0.005)), pan=-0.2)
    # the herds outside: clusters of two to four clonks, each animal's bell its own pitch; nearer in the middle
    pos = float(g.uniform(0.3, 1.5))
    while pos < LOOP_S - 1.0:
        near = SECTION[min(BARS - 1, int(pos // BAR))] == "C"
        f = float(g.choice([620.0, 710.0, 830.0, 955.0]))
        pan = float(g.uniform(-0.9, 0.9))
        tt = pos
        for _ in range(int(g.integers(2, 5))):
            mx.add("bells", V.herd_bell(g, float(g.uniform(0.4, 0.9)) * (1.6 if near else 1.0), f), tt, pan=pan)
            tt += float(g.uniform(0.18, 0.5))
        pos += float(g.uniform(2.0, 5.0)) * (0.7 if near else 1.0)
    S.add_flute(mx, "flute", S.TUNE_A, 5, SEED + 600, 0.55, -0.08)
    S.add_flute(mx, "flute", S.TUNE_B, 13, SEED + 620, 0.55, -0.08)
    S.add_flute(mx, "flute", S.TUNE_A, 17, SEED + 640, 0.55, -0.08)
    S.add_flute(mx, "flute2", S.TUNE_A, 17, SEED + 660, 0.45, 0.35, harmony=True)
    S.add_flute(mx, "flute", TUNE_C, 25, SEED + 670, 0.5, -0.05)
    S.add_flute(mx, "flute", S.TUNE_B, 33, SEED + 680, 0.55, -0.08)
    S.add_flute(mx, "flute2", S.TUNE_B, 33, SEED + 685, 0.45, 0.35, harmony=True)
    S.add_flute(mx, "flute", S.TUNE_A, 37, SEED + 690, 0.56, -0.08)
    S.add_flute(mx, "flute2", S.TUNE_A, 37, SEED + 695, 0.46, 0.35, harmony=True)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=6.0)
    G = GAINS
    fl = [bq_highpass(170, 0.7), bq_peak(1500, 1.0, 1.0), bq_lowpass(6500, 0.7)]
    mx.bus("flute", G["flute"], send=0.30, process=lambda x: filt(x, fl))
    mx.bus("flute2", G["flute2"], send=0.35, process=lambda x: filt(x, fl))
    mx.bus("strum", G["strum"], send=0.25, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_lowpass(7000, 0.7)]))
    mx.bus("pick", G["pick"], send=0.35, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_lowpass(6000, 0.7)]))
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
