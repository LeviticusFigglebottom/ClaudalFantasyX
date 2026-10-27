"""`ossa_fen`: Ch10, Ossa Fen, the mangrove channels of the Kirru estuary (M3-AUD-804 sketch; act_outline Ch10, bible
§5.5): a 61.9 s seamless loop.

Original composition for this project (SPEC §2, §9). The pipe's tune, the low flute's answer, the harmony and every
part below were written for this cue. Original-material check: the tune grows from one cell of our own (a low sway,
D-F-G, rising a fourth and settling on the tonic) and its answer (a stepwise climb through the Dorian sixth, E
natural); neither is taken from any melody we know. The style evoked (a nasal reed pipe over a still drone, as in
many river musics) is a colour, not a quotation. Nothing is borrowed from another cue; the only shared things are
the instruments of the palette (the breath flute, the pad, the frame drum) and the shell-shrine's idea that water
can be heard as drips.

The brief: tannin-dark water between mangrove roots, white egrets, the Kirru's country, and the first place in the
game the Order does not own. Humid and still: nothing hurries, the air is thick, and the water does not move. The
insects are implied by texture (narrow bands of noise in pulse trains, synthesized), never by samples.

G Dorian (G A Bb C D E F; the raised sixth, E natural, is the fen's colour: it is the note the Order's G minor would
not have, and it sounds in the C major chord of bars 10 and 13), 4/4 at 62 BPM (a bar is 3.871 s), 16 bars. Apart
from every Act I cue: the only Dorian cue on G, and the first to use a reed (a double-reed pipe) as its lead.

Ensemble (all synthesized; no samples):
* the fen pipe (act2_voices.reed_pipe): a double reed, nasal and close, a little flat at the end of each long note;
  the tune (bars 5-12);
* a breath flute, low and soft (G3-Bb4): the answer (bars 13-16), with the pipe silent;
* the still water: a held drone on G and D that breathes once every 16 s; a very dark low string pad on the chords;
* a low, muted plucked string on 1 and the "and" of 3 (a pole finding the mud);
* a frame drum's soft "dum" on beat 3 in the tune (bars 5-12);
* the fen itself: insects (act2_voices.insects: clustered chirps, a faint high bed, a far frog's purr) and drips
  from the roots (synth.water.drip), sparse and wide.

Form (bars): 1-4 the channels (drone, pad, insects, drips, the pole) | 5-12 A, the pipe | 13-16 B, the low flute
answers over C Bb F Dm, and Dm leads back to bar 1's G minor.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/ossa_fen.py   (or tools/audio/render_all.py --only ossa_fen)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import drip  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__), "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT = os.path.join(ROOT, "assets", "audio", "music", "ossa_fen.ogg")
SEED = 20261801
TARGET_LUFS = -16.0
BPM = 62.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 16
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
## Vorbis quality: the insects and the drips are broadband noise, which costs bits; q2 keeps the file near 0.8 MiB
QUALITY = 2.0

CHORDS = (["Gm", "Gm", "Eb", "Gm"]
          + ["Gm", "F", "Eb", "Dm", "Gm", "C", "Eb", "Gm"]
          + ["C", "Bb", "F", "Dm"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 4
PAD = {"Gm": "G1 D2 G2 Bb2", "F": "F1 C2 F2 A2", "Eb": "Eb2 Bb2 Eb3 G3", "Dm": "D2 A2 D3 F3", "C": "C2 G2 C3 E3",
       "Bb": "Bb1 F2 Bb2 D3"}
ROOTS = {"Gm": "G1", "F": "F1", "Eb": "Eb2", "Dm": "D2", "C": "C2", "Bb": "Bb1"}

## the pipe's tune: one list per bar of (pitch | None, beats)
TUNE_A = [
    [("D4", 1.5), ("F4", .5), ("G4", 2)],                    # the sway
    [("A4", 1), ("G4", .5), ("F4", .5), ("G4", 2)],
    [("Bb4", 1.5), ("C5", .5), ("Bb4", 1), ("G4", 1)],
    [("A4", 3), (None, 1)],
    [("D4", 1.5), ("F4", .5), ("G4", 1), ("A4", 1)],         # the sway, reaching
    [("C5", 1.5), ("A4", .5), ("G4", 1), ("E4", 1)],         # the Dorian sixth
    [("F4", 1), ("G4", 1), ("Bb4", 1.5), ("A4", .5)],
    [("G4", 3), (None, 1)],
]
## the low flute's answer
TUNE_B = [
    [("E4", 2), ("G4", 1), ("A4", 1)],
    [("Bb4", 2), ("A4", 1), ("F4", 1)],
    [("G4", 1), ("F4", 1), ("A4", 2)],
    [("A4", 1), ("F4", 1), ("D4", 2)],
]

LEAD = "pipe"
## planned levels relative to the pipe (LU, each bus measured where it plays)
LEVELS = {"pipe": 0.0, "flute": -1.0, "pad": -10.0, "drone": -13.0, "pole": -11.0, "drum": -13.0, "insects": -17.0,
          "drips": -15.0}
## bus gains (dB) that give LEVELS, set from a render with every gain at 0 (render(stats=...)["bus_lufs"]) and checked
## on the re-render (each bus within 0.1 LU of its plan)
GAINS = {"pipe": 0.0, "flute": 5.2, "pad": 9.9, "drone": -6.5, "pole": 5.5, "drum": 8.3, "insects": 13.2, "drips": 5.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_pipe(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is None:
                pos += d
                continue
            v = vel * float(g.uniform(0.93, 1.04)) * (1.05 if beats >= 2 else 1.0)
            x = V.reed_pipe(n(p), d * 0.95, v, seed + int(round(pos * 1000)), sag_cents=22.0 if beats >= 2 else 8.0)
            mx.add("pipe", x, pos + float(g.normal(0, 0.006)), pan=0.08)
            pos += d


def add_flute(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            v = vel * float(g.uniform(0.94, 1.04))
            x = breath_flute(n(p), d * 0.96 + 0.03, v, seed=seed + int(round(pos * 1000)), breath=0.6,
                             scoop_cents=45.0 if first else 12.0, vib_cents=9.0 if beats >= 2 else 3.0,
                             vib_rate=4.2, swell=0.25 if beats >= 2 else 0.0, attack=0.12 if first else 0.06,
                             release=0.5, beta=0.45)
            mx.add("flute", x, pos - V.FLUTE_PRE + float(g.normal(0, 0.005)), pan=-0.12)
            pos += d
            first = False


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("G2"), 1.0), (n("D3"), 0.35)], SEED + 3, breath_s=16.0), 0.0)
    mx.add("insects", V.insects(LOOP_S, SEED + 4), 0.0)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.95, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=1.8, release=1.8, width=0.75)
        mx.add("pad", x, t_of(bar) - 0.4)
        # the pole: a low muted string on 1 and the "and" of 3
        r = n(ROOTS[ch]) + 12
        for beat, v in ((0.0, 0.55), (2.5, 0.35)):
            x = string_pluck(r, BEAT * 1.2, v * float(g.uniform(0.9, 1.05)), seed=SEED + 300 + 4 * bar + int(beat),
                             pick_pos=0.2, t60=1.6, mute=0.45, B=1e-4, max_f=2500.0, release=0.1)
            mx.add("pole", x, t_of(bar, beat) + float(g.normal(0, 0.008)), pan=-0.05)
        if sec == "A":
            x = frame_drum("dum", 0.2 * float(g.uniform(0.9, 1.08)), variant=bar, size=1.3, seed=SEED + 1)
            mx.add("drum", x, t_of(bar, 2) + float(g.normal(0, 0.008)), pan=0.15)
        # drips from the roots: one or two a bar, anywhere, wide
        for _ in range(int(g.integers(1, 3))):
            x = drip(float(g.uniform(0.3, 0.7)), radius_mm=float(g.uniform(1.8, 4.0)), seed=int(g.integers(1 << 30)))
            mx.add("drips", x, t_of(bar, float(g.uniform(0, 4))), pan=float(g.uniform(-0.8, 0.8)))
    add_pipe(mx, TUNE_A, 5, SEED + 600, 0.62)
    add_flute(mx, TUNE_B, 13, SEED + 650, 0.5)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = GAINS
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
                        early_level=0.2, lowcut=110.0, seed=SEED % 9973)
    return V.finish(mx, "ossa_fen", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -3.0, verbose,
                    stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
