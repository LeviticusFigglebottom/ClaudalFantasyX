"""`ossa_fen` (final): Ch10, Ossa Fen, the mangrove channels of the Kirru estuary (M3-AUD-840; the M3-AUD-804
sketch grown into a full piece; act_outline Ch10, bible §5.5): a 154.8 s seamless loop.

Original composition for this project (SPEC §2, §9). The sketch's material (assets_src/music/ossa_fen.py: the
pipe's tune, the low flute's answer, the chords, every voice and level) is imported from it, not retyped, and the
sketch file is untouched. Original-material check: everything new here grows from the sketch's own two cells (the
low sway D-F-G, and the stepwise climb through the Dorian sixth). The development (bars 17-24) is the sway moved up a
fourth (G-Bb-C) and handed between the pipe and the flute, climbing to the high E natural over C major; the flute's
counter-line under the returning tune (bars 29-36) is a plain line of thirds and sixths below it; the stillness
(bars 25-28) is two fragments of the sway. None of it is taken from any melody we know; the style evoked (a nasal
reed pipe over a still drone, as in many river musics) is a colour, not a quotation. Nothing is borrowed from
another cue.

The brief (as the sketch): tannin-dark water between mangrove roots, white egrets, the Kirru's country, the first
place the Order does not own. Humid and still: nothing hurries. The final keeps that stillness for two and a half
minutes: its one moment of reaching is the development's high E, and right after it the fen goes quiet again.

G Dorian (G A Bb C D E F; the raised sixth, E natural, is the fen's colour), 4/4 at 62 BPM (a bar is 3.871 s),
40 bars. The sketch's palette, unchanged: the fen pipe (act2_voices.reed_pipe), a low breath flute, the breathing
G/D drone, a dark low string pad, the pole (a muted low pluck on 1 and the "and" of 3), a frame drum's "dum" on 3,
the insects (act2_voices.insects) and drips from the roots.

Form (bars):
*  1-4   the channels: drone, pad, insects, drips, the pole (the sketch's bars 1-4)
*  5-12  A, the pipe's tune (the sketch's A)
* 13-16  B, the low flute answers over C Bb F Dm (the sketch's B)
* 17-24  C, the development: the sway a fourth higher, pipe and flute trading two-bar phrases over C Gm Bb F, then
         together over Eb C Dm, the pipe reaching the high E natural (bar 22); the drum adds a soft second stroke
* 25-28  the stillness: the drum and the pipe drop out, the pole only on 1, two fragments of the sway in the low
         flute over Eb C Gm Gm, more drips
* 29-36  A', the pipe's tune again, the low flute under it in thirds and sixths
* 37-40  B', the flute's answer, the pipe echoing its last two bars; Dm leads back to bar 1's G minor

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth. Vorbis q2, as the sketch: the insects
and the drips are broadband noise.

Render:  python3 assets_src/music/act2/ossa_fen.py   (or tools/audio/render_all.py --act2 --only act2/ossa_fen)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import drip  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SK = _mod("ossa_fen_sketch", os.path.join(HERE, "..", "ossa_fen.py"))
V = SK.V

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "ossa_fen.ogg")
SEED = SK.SEED + 840_000
TARGET_LUFS = SK.TARGET_LUFS
BPM, BEAT, BAR = SK.BPM, SK.BEAT, SK.BAR
BARS = 40
LOOP_S = BARS * BAR
LEAD_IN_BEATS = SK.LEAD_IN_BEATS
QUALITY = SK.QUALITY
t_of = SK.t_of

CHORDS = (SK.CHORDS
          + ["C", "Gm", "Bb", "F", "Eb", "C", "Dm", "Dm"]
          + ["Eb", "C", "Gm", "Gm"]
          + SK.CHORDS[4:12]
          + SK.CHORDS[12:16])
SECTION = (SK.SECTION + ["C"] * 8 + ["S"] * 4 + ["A"] * 8 + ["B"] * 4)
assert len(CHORDS) == len(SECTION) == BARS

## the development: (start bar, voice, bars); a bar is a list of (pitch | None, beats)
DEV = [
    (17, "pipe", [[("G4", 1.5), ("Bb4", .5), ("C5", 2)],                  # the sway, a fourth higher
                  [("D5", 1), ("C5", .5), ("Bb4", .5), ("C5", 2)]]),
    (19, "flute", [[("F4", 2), ("D4", 1), ("F4", 1)],
                   [("A4", 1), ("G4", 1), ("F4", 2)]]),
    (21, "pipe", [[("G4", 1.5), ("Bb4", .5), ("C5", 1), ("D5", 1)],
                  [("E5", 2), ("D5", 1), ("C5", 1)],                      # the high Dorian sixth
                  [("D5", 1.5), ("C5", .5), ("A4", 1), ("F4", 1)],
                  [("A4", 3), (None, 1)]]),
    (23, "flute", [[("F4", 2), ("A4", 2)],
                   [("D4", 4)]]),
]
## the stillness: two fragments of the sway in the low flute
STILL = [[(None, 4)], [(None, 2), ("D4", 1.5), ("F4", .5)], [("G4", 3), (None, 1)], [(None, 4)]]
## A': the low flute under the returning tune, in thirds and sixths
COUNTER_A = [
    [("Bb3", 2), ("D4", 2)],
    [("C4", 2), ("A3", 2)],
    [("G3", 2), ("Bb3", 2)],
    [("F4", 2), ("D4", 1), (None, 1)],
    [("Bb3", 2), ("D4", 2)],
    [("E4", 2), ("C4", 2)],
    [("Eb4", 2), ("D4", 2)],
    [("D4", 3), (None, 1)],
]
## B': the pipe echoes the answer's last two bars
ECHO_B = [[("C5", 2), ("A4", 2)], [("A4", 2), (None, 2)]]


class _Later:
    """A mixer seen `dt` seconds later: lets the sketch's phrase writers (which start on a downbeat) start a phrase
    after a rest."""

    def __init__(self, mx: LoopMixer, dt: float) -> None:
        self.mx, self.dt = mx, dt

    def add(self, bus: str, x, start: float, pan: float = 0.0) -> None:
        self.mx.add(bus, x, start + self.dt, pan=pan)


def add_phrase(mx: LoopMixer, voice: str, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """A phrase on the pipe or the flute through the sketch's writers; the flute's rests split it into runs (the
    sketch's flute writer takes no rests), each run starting where its first note falls."""
    if voice == "pipe":
        SK.add_pipe(mx, bars, start_bar, seed, vel)
        return
    for i, bar in enumerate(bars):
        beat, run, run_at = 0.0, [], 0.0
        for p, beats in bar + [(None, 0.0)]:
            if p is None:
                if run:
                    SK.add_flute(_Later(mx, run_at * BEAT), [run], start_bar + i, seed + 31 * i + int(run_at), vel)
                run = []
                beat += beats
                run_at = beat
                continue
            run.append((p, beats))
            beat += beats


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("G2"), 1.0), (n("D3"), 0.35)], SEED + 3, breath_s=16.0), 0.0)
    mx.add("insects", V.insects(LOOP_S, SEED + 4), 0.0)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        x = pad_chord([n(p) for p in SK.PAD[ch].split()], BAR * 0.95, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=1.8, release=1.8, width=0.75)
        mx.add("pad", x, t_of(bar) - 0.4)
        r = n(SK.ROOTS[ch]) + 12
        strokes = ((0.0, 0.5),) if sec == "S" else ((0.0, 0.55), (2.5, 0.35))
        for beat, v in strokes:
            x = string_pluck(r, BEAT * 1.2, v * float(g.uniform(0.9, 1.05)), seed=SEED + 300 + 4 * bar + int(beat),
                             pick_pos=0.2, t60=1.6, mute=0.45, B=1e-4, max_f=2500.0, release=0.1)
            mx.add("pole", x, t_of(bar, beat) + float(g.normal(0, 0.008)), pan=-0.05)
        if sec in ("A", "C"):
            x = frame_drum("dum", 0.2 * float(g.uniform(0.9, 1.08)), variant=bar, size=1.3, seed=SK.SEED + 1)
            mx.add("drum", x, t_of(bar, 2) + float(g.normal(0, 0.008)), pan=0.15)
        if sec == "C" and bar % 2 == 0:
            x = frame_drum("dum", 0.12 * float(g.uniform(0.9, 1.08)), variant=bar + 3, size=1.3, seed=SK.SEED + 1)
            mx.add("drum", x, t_of(bar, 3.5) + float(g.normal(0, 0.008)), pan=0.2)
        lo, hi = (2, 4) if sec == "S" else (1, 3)
        for _ in range(int(g.integers(lo, hi))):
            x = drip(float(g.uniform(0.3, 0.7)), radius_mm=float(g.uniform(1.8, 4.0)), seed=int(g.integers(1 << 30)))
            mx.add("drips", x, t_of(bar, float(g.uniform(0, 4))), pan=float(g.uniform(-0.8, 0.8)))
    # the sketch's A and B, as they were
    SK.add_pipe(mx, SK.TUNE_A, 5, SK.SEED + 600, 0.62)
    SK.add_flute(mx, SK.TUNE_B, 13, SK.SEED + 650, 0.5)
    # the development
    for k, (start, voice, bars) in enumerate(DEV):
        add_phrase(mx, voice, bars, start, SEED + 700 + 50 * k, 0.6 if voice == "pipe" else 0.5)
    add_phrase(mx, "flute", STILL, 25, SEED + 900, 0.42)
    # A' and B'
    SK.add_pipe(mx, SK.TUNE_A, 29, SEED + 1000, 0.6)
    add_phrase(mx, "flute", COUNTER_A, 29, SEED + 1100, 0.36)
    SK.add_flute(mx, SK.TUNE_B, 37, SEED + 1200, 0.5)
    SK.add_pipe(mx, ECHO_B, 39, SEED + 1300, 0.42)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = SK.GAINS
    mx.bus("pipe", G["pipe"], send=0.30, process=lambda x: filt(x, [bq_highpass(180, 0.7), bq_lowpass(6500, 0.7)]))
    mx.bus("flute", G["flute"], send=0.40, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(1400, 1.0, 1.0),
                                                                       bq_lowpass(5500, 0.7)]))
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=900.0))
    mx.bus("drone", G["drone"], send=0.25, process=lambda x: filt(x, [bq_lowpass(1200, 0.7)]))
    mx.bus("pole", G["pole"], send=0.25, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.bus("drum", G["drum"], send=0.30, process=lambda x: filt(x, [bq_lowpass(2200, 0.7)]))
    mx.bus("insects", G["insects"], send=0.20)
    mx.bus("drips", G["drips"], send=0.55)
    build(mx)
    hall = ModFDNReverb(rt60=2.6, rt60_high=0.8, predelay=0.03, size=1.1, mod_depth=8.0, mod_rate=0.35,
                        early_level=0.2, lowcut=110.0, seed=SK.SEED % 9973)
    return V.finish(mx, "ossa_fen (final)", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -3.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
