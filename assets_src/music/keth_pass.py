"""`keth_pass`: Ch12, Keth Pass, the mountain route into the Ullar Heights (M3-AUD-804 sketch; act_outline Ch12,
bible §5.7): a 62.6 s seamless loop.

Original composition for this project (SPEC §2, §9). The tune, the low pipe's verse, the harmony and every part below
were written for this cue. Original-material check: the tune is built from one cell of our own (a fall from the
fifth to the third, B-A-G, then the long tonic) and its climb back (G-A-B to D); it comes from this cue's scale,
not from any melody we know. The style evoked is a highland one (a panpipe split between two players who play
alternate notes, a hocket, over an open-fifth drone), without quoting any tune or any real instrument's repertoire.
Nothing is borrowed from another cue; the wind is the saltgrass causeway's recipe with new rates (act2_voices.wind).

The brief: the pass-cords strung across every pass, where the Ullari tie a knot for their dead and walk on without
looking back; thin air and enormous skies; in the cold, Toma notices that Kerrid's breath doesn't fog (act_outline
Ch12, bible §5.7). Cold, wind-borne and wide: the pipes are breathy and high, the space is huge, the wind never
stops, and the cords whistle in it.

E minor (Aeolian: E F# G A B C D; the tune keeps to E G A B D, the pentatonic inside it), 6/8 at 46 dotted
quarters a minute (a bar is 2.609 s), 24 bars. Apart from every Act I cue: the only cue in E minor, and the slowest
6/8 (Haluna's is 64, the Hullgnaw's 90).

Ensemble (all synthesized; no samples):
* two pipes (synth.winds.breath_flute, very breathy, bright and short of vibrato), hard left and right, playing the
  tune in hocket: each plays every other note, so the tune exists only between them (bars 5-12 and 17-24, the
  second time an octave higher for four bars);
* one pipe alone, lower and slower (bars 13-16): the verse, over C D G Em;
* the wind (act2_voices.wind), and the pass-cords (act2_voices.cord_song): very narrow bands of wind-noise on E, G,
  B and E, whistling and fading on their own slow gusts;
* an open-fifth string pad on the chords, wide;
* a big drum, far below, every four bars, and a frame drum's soft step on the second dotted quarter in the tune.

Form (bars): 1-4 the pass (wind, cords, pad, the far drum) | 5-12 A, the hocket | 13-16 B, one pipe alone | 17-24
A', the hocket, the first four bars an octave higher, and the long tonic leads back to bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/keth_pass.py   (or tools/audio/render_all.py --only keth_pass)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__), "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT = os.path.join(ROOT, "assets", "audio", "music", "keth_pass.ogg")
SEED = 20261805
TARGET_LUFS = -16.0
BPM = 46.0                       # dotted quarters
DQ = 60.0 / BPM
EIGHTH = DQ / 3
BAR = 2 * DQ
BARS = 24
LOOP_S = BARS * BAR
LEAD_IN_EIGHTHS = 0.5            # a sixteenth
QUALITY = 3.0

CHORDS = (["Em", "Em", "C", "Em"]
          + ["Em", "Em", "G", "D", "C", "D", "Em", "Em"]
          + ["C", "D", "G", "Em"]
          + ["Em", "Em", "G", "D", "C", "D", "Em", "Em"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 4 + ["A2"] * 8
PAD = {"Em": "E2 B2 E3 G3", "C": "C2 G2 C3 E3", "G": "G1 D2 G2 B2", "D": "D2 A2 D3 F#3"}

## the tune: one list per bar of (pitch, eighths)
TUNE = [
    [("B4", 3), ("A4", 1), ("G4", 2)],
    [("E4", 6)],
    [("G4", 2), ("A4", 1), ("B4", 3)],
    [("D5", 3), ("B4", 3)],
    [("E5", 3), ("D5", 1), ("B4", 2)],
    [("A4", 4), ("G4", 2)],
    [("A4", 2), ("B4", 1), ("G4", 2), ("E4", 1)],
    [("E4", 6)],
]
VERSE = [
    [("C5", 4), ("B4", 2)],
    [("A4", 3), ("B4", 3)],
    [("D5", 4), ("B4", 2)],
    [("G4", 3), ("E4", 3)],
]

LEAD = "pipes"
LEVELS = {"pipes": 0.0, "verse": -1.0, "wind": -12.0, "cords": -14.0, "pad": -11.0, "drum": -12.0, "step": -15.0}
GAINS = {"pipes": 0.0, "verse": -0.3, "wind": 7.4, "cords": -3.0, "pad": 2.7, "drum": -2.3, "step": 4.4}


def t_of(bar: int, eighth: float = 0.0) -> float:
    return (bar - 1) * BAR + eighth * EIGHTH


def pipe(m: float, d: float, vel: float, seed: int, first: bool) -> object:
    return breath_flute(m, d * 0.92 + 0.02, vel, seed=seed, breath=0.85, scoop_cents=25.0 if first else 8.0,
                        vib_cents=4.0 if d > 1.0 else 0.0, vib_rate=5.0, swell=0.15 if d > 1.0 else 0.0, attack=0.04,
                        release=0.3, beta=0.7)


def add_hocket(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, octave: int = 0) -> None:
    g = rng(seed)
    k = 0
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, e in bar:
            d = e * EIGHTH
            side = k % 2
            v = vel * float(g.uniform(0.92, 1.05)) * (1.06 if e >= 3 else 1.0)
            x = pipe(n(p) + 12 * octave, d, v, seed + int(round(pos * 1000)), k == 0)
            mx.add("pipes", x, pos - V.FLUTE_PRE + float(g.normal(0, 0.008)), pan=-0.5 if side == 0 else 0.5)
            pos += d
            k += 1


def add_verse(mx: LoopMixer, seed: int, vel: float) -> None:
    g = rng(seed)
    for i, bar in enumerate(VERSE):
        pos = t_of(13 + i)
        for j, (p, e) in enumerate(bar):
            d = e * EIGHTH
            x = breath_flute(n(p), d * 0.96 + 0.03, vel * float(g.uniform(0.94, 1.04)), seed=seed + int(round(pos * 1000)),
                             breath=0.7, scoop_cents=40.0 if j == 0 else 15.0, vib_cents=8.0, vib_rate=4.4,
                             swell=0.3, attack=0.1, release=0.6, beta=0.55)
            mx.add("verse", x, pos - V.FLUTE_PRE + float(g.normal(0, 0.005)), pan=0.0)
            pos += d


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("wind", V.wind(LOOP_S, SEED + 3, lo_hz=300.0, hi_hz=2400.0, gusts=(3, 7, 2), hi_level=0.3), 0.0)
    mx.add("cords", V.cord_song(LOOP_S, [n("E5"), n("G5"), n("B5"), n("E6")], SEED + 4, q=45.0), 0.0)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.95, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=1.2, release=1.6, width=0.95)
        mx.add("pad", x, t_of(bar) - 0.3)
        if sec in ("A", "A2"):
            x = frame_drum("dum", 0.16 * float(g.uniform(0.9, 1.08)), variant=bar, size=1.2, seed=SEED + 1)
            mx.add("step", x, t_of(bar, 3) + float(g.normal(0, 0.01)), pan=0.1)
    for bar in range(1, BARS + 1, 4):
        mx.add("drum", big_drum(0.4 if bar in (1, 13) else 0.3, variant=bar, seed=SEED + 2), t_of(bar), pan=0.0)
    add_hocket(mx, TUNE, 5, SEED + 600, 0.55)
    add_hocket(mx, TUNE[:4], 17, SEED + 640, 0.5, octave=1)
    add_hocket(mx, TUNE[4:], 21, SEED + 660, 0.55)
    add_verse(mx, SEED + 700, 0.5)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = GAINS
    pipe_eq = [bq_highpass(220, 0.7), bq_peak(2500, 1.5, 1.0), bq_lowpass(7000, 0.7)]
    mx.bus("pipes", G["pipes"], send=0.45, process=lambda x: filt(x, pipe_eq))
    mx.bus("verse", G["verse"], send=0.45, process=lambda x: filt(x, [bq_highpass(160, 0.7), bq_lowpass(6000, 0.7)]))
    mx.bus("wind", G["wind"], send=0.15)
    mx.bus("cords", G["cords"], send=0.35)
    mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=1400.0))
    mx.bus("drum", G["drum"], send=0.6, process=lambda x: filt(x, [bq_lowpass(1200, 0.7)]))
    mx.bus("step", G["step"], send=0.4, process=lambda x: filt(x, [bq_lowpass(2000, 0.7)]))
    build(mx)
    sky = ModFDNReverb(rt60=3.4, rt60_high=1.4, predelay=0.06, size=1.5, mod_depth=8.0, mod_rate=0.3,
                       early_level=0.12, lowcut=120.0, seed=SEED % 9973)
    return V.finish(mx, "keth_pass", out_path, BPM, 2, BARS, LEAD_IN_EIGHTHS * EIGHTH, TARGET_LUFS, sky, -2.5,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
