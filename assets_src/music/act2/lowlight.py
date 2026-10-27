"""`lowlight`: Ch11, the Lowlight temple, half underwater, and the Lamp Engine still running in it (M3-AUD-841
final of the M3-AUD-804 sketch; act_outline Ch11, bible §5.6): a 149.0 s seamless loop.

Original composition for this project (SPEC §2, §9). Original-material check: the themes are the sketch's
(assets_src/music/lowlight.py, loaded here, never retyped): the Kirru call (reedhollow.py's cell, our own) on the
flute and the Hush's outline (hush_theme_v2.py, our own) on the glass. What this final adds was written for it and
grows only out of those two: the development "binds" the call into the temple's mode (its raised third and sixth
pulled down to Eb and G, its answer stepping down C minor), the glass answers with the Hush's fall and a new turn
D-Eb-C, a low flute counterline sits under the Hush's return, and the coda hands the call's first cell to the glass.
No existing melody or style is quoted.

The brief: the Ice temple, a half-flooded gallery temple whose sanctum is underwater at the foot of a Lit Age
well-shaft; the deep's cold wells up through the floor and drowned glimmer sifts down like silt. Its guardian is the
Lamp Engine, a still-running machine full of bound dead. A dead machine still keeping time: its stroke is mechanical
and its bound light steady (the glass's held pedals, the hum), never a pulse that reads as breathing. The call and the
Hush never quite meet: when the call is pulled into C minor it loses its leap, and when it comes back it is itself.

C minor (Aeolian: C D Eb F G Ab Bb; the G chord takes B natural), as the sketch. The Kirru call keeps its own E and
F# over a bare open fifth wherever it sounds free. 4/4 at 58 BPM (a bar is 4.138 s), 36 bars.

Ensemble (the sketch's palette, all synthesized; no samples): the Lamp Engine (act2_voices.engine_thud) and its
conduits' hum (act2_voices.conduit_hum on C2); the deep's cold (act2_voices.deep_cold); a low breath flute (C4-A4);
a glass harmonica (act2_voices.glass); a dark low string pad; the silt (soft pure glints falling down the scale).

Form (bars):
*  1-4   the engine alone (hum, the deep, the open fifth, the silt);
*  5-8   A, the Kirru call (the sketch's KIRRU_A) over the open fifth;
*  9-12  B, the Hush on glass (HUSH_A) over Cm Ab Fm G;
* 13-20  C, the binding: Ab Eb Fm Cm | Ab Bb G G. The call in C minor (flute) under a held glass Eb, the glass's
         fall and turn over a held flute C, the bound call again, then both on G; the engine strains (a stutter every
         second bar, softer strokes) and drops beat 4 of bar 20;
* 21-24  A', the call as itself again, the glass holding G5 above it like a lamp that will not go out;
* 25-28  B', the Hush on glass over a low flute counterline (Eb-D | C | C-F | D);
* 29-32  D, both at once (the sketch's close: KIRRU_B with HUSH_B) over C5 C5 Fm G;
* 33-36  coda, the engine alone, the glass touching the call's cell once (C-D-E), and the stall: bar 36's beats 3
         and 4 are missing, and the engine catches again on bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth (the engine's stall).

Render:  python3 assets_src/music/act2/lowlight.py   (or tools/audio/render_all.py --act2 --only act2/lowlight)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("lowlight_sketch", os.path.join(MUSIC, "lowlight.py"))   # the sketch: its themes, voices and timing
V = S.V

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "lowlight.ogg")
SEED = 20261841
TARGET_LUFS = -16.0
BPM, BEAT, BAR = S.BPM, S.BEAT, S.BAR
BARS = 36
LOOP_S = BARS * BAR
LEAD_IN_BEATS = S.LEAD_IN_BEATS
QUALITY = 3.0

SECTION = (["I"] * 4 + ["A"] * 4 + ["B"] * 4 + ["C"] * 8 + ["A2"] * 4 + ["B2"] * 4 + ["D"] * 4 + ["coda"] * 4)
CHORDS = (["C5"] * 4
          + ["C5"] * 4
          + ["Cm", "Ab", "Fm", "G"]
          + ["Ab", "Eb", "Fm", "Cm", "Ab", "Bb", "G", "G"]
          + ["C5"] * 4
          + ["Cm", "Ab", "Fm", "G"]
          + ["C5", "C5", "Fm", "G"]
          + ["C5"] * 4)
PAD = dict(S.PAD, Eb="Eb2 Bb2 Eb3 G3", Bb="Bb1 F2 Bb2 D3")

## C, the binding: the call pulled into C minor (its third to Eb, its leap falling short to G), and the glass's
## answer (the Hush's fall, then a new turn D-Eb-C); each over the other's held note
CALL_BOUND_1 = [[("C4", 1), ("D4", .5), ("Eb4", 2.5)],
                [("G4", 3), (None, 1)]]
CALL_BOUND_2 = [[("C4", 1), ("D4", .5), ("Eb4", 1.5), ("F4", 1)],
                [("G4", 2), ("F4", 1), ("D4", 1)],
                [("D4", 4)],
                [(None, 4)]]
GLASS_ANSWER = [[("F5", 2), ("Eb5", 2)],
                [("D5", 1), ("Eb5", 1), ("C5", 2)]]
GLASS_ON_G = [[("G5", 4)],
              [("F5", 1), ("D5", 1), ("B4", 2)]]
GLASS_PEDAL_EB = [[("Eb5", 7), (None, 1)]]          # one unbroken note: the bound light does not swell
FLUTE_PEDAL_C = [[("C4", 7), (None, 1)]]
## A': the lamp that will not go out
GLASS_PEDAL_G = [[("G5", 15), (None, 1)]]
## B': the flute's low counterline under the Hush
COUNTER = [[("Eb4", 3), ("D4", 1)],
           [("C4", 4)],
           [("C4", 2), ("F4", 2)],
           [("D4", 3), (None, 1)]]
## coda: the call's first cell, once, on the glass
GLASS_CELL = [[(None, 4)], [("C5", 1), ("D5", .5), ("E5", 2.5)]]

LEAD = "flute"
LEVELS = S.LEVELS
GAINS = dict(S.GAINS, glass=S.GAINS["glass"] + 0.8)   # the glass carries more of the long form
SILT_RATE = {"I": 1.0, "A": 1.0, "B": 1.0, "C": 1.6, "A2": 1.0, "B2": 1.2, "D": 1.2, "coda": 0.8}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_engine(mx: LoopMixer) -> None:
    """The sketch's engine, carried through the long form: a stroke on every beat, beat 4 limping late, a stutter on
    beat 2 of every fourth bar (every second bar in C, where the strokes also weaken); bar 20 drops beat 4, and
    bar 36 stalls after beat 2."""
    g = rng(SEED + 100)
    for bar in range(1, BARS + 1):
        sec = SECTION[bar - 1]
        strain = sec == "C"
        for beat in range(4):
            if (bar == BARS and beat >= 2) or (bar == 20 and beat == 3):
                continue
            vel = (0.95 if bar in (1, 13, 21) else 0.85, 0.45, 0.7, 0.45)[beat] * float(g.uniform(0.9, 1.05))
            vel *= 0.82 if strain else 1.0
            late = (0.06 if strain else 0.045) if beat == 3 else 0.0
            t0 = t_of(bar, beat) + late + float(g.normal(0, 0.012))
            mx.add("engine", V.engine_thud(g, vel), t0, pan=-0.05)
            if beat == 1 and bar % (2 if strain else 4) == 0:
                mx.add("engine", V.engine_thud(g, vel * 0.6), t0 + 0.17, pan=0.05)


def add_silt(mx: LoopMixer, g) -> None:
    """The sketch's silt (strings of three to five glints, each a step lower), thicker in the binding."""
    pos = float(g.uniform(0.5, 2.0))
    while pos < LOOP_S - 1.0:
        sec = SECTION[min(BARS - 1, int(pos // BAR))]
        top = int(g.integers(4, len(S.SILT)))
        count = int(g.integers(3, 6))
        pan = float(g.uniform(-0.7, 0.7))
        tt = pos
        for k in range(count):
            idx = top - k
            if idx < 0:
                break
            f = midi_to_hz(n(S.SILT[idx]))
            N = int(1.2 * SR)
            t = np.arange(N) / SR
            x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) * np.minimum(1.0, t / 0.01)
            mx.add("silt", 0.2 * float(g.uniform(0.5, 1.0)) * x, tt, pan=pan - 0.05 * k)
            tt += float(g.uniform(0.25, 0.6))
        pos += float(g.uniform(3.0, 7.0)) / SILT_RATE[sec]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("hum", V.conduit_hum(LOOP_S, n("C2"), rng(SEED + 7)), 0.0)
    mx.add("deep", V.deep_cold(LOOP_S, SEED + 8), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        vel = 0.4 if SECTION[bar - 1] in ("I", "coda") else 0.45
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.95, vel, seed=SEED + 200 + bar, voices=4,
                      attack=1.8, release=1.8, width=0.7)
        mx.add("pad", x, t_of(bar) - 0.4)
    add_engine(mx)
    add_silt(mx, g)
    # A and B: the sketch's themes
    S.add_flute(mx, S.KIRRU_A, 5, SEED + 600, 0.5)
    S.add_glass(mx, S.HUSH_A, 9, SEED + 700, 0.7)
    # C: the binding
    S.add_flute(mx, CALL_BOUND_1, 13, SEED + 610, 0.48)
    S.add_glass(mx, GLASS_PEDAL_EB, 13, SEED + 705, 0.32)
    S.add_glass(mx, GLASS_ANSWER, 15, SEED + 710, 0.62)
    S.add_flute(mx, FLUTE_PEDAL_C, 15, SEED + 612, 0.36)
    S.add_flute(mx, CALL_BOUND_2, 17, SEED + 614, 0.5)
    S.add_glass(mx, GLASS_ON_G, 19, SEED + 715, 0.6)
    # A': the call as itself, under a held lamp
    S.add_flute(mx, S.KIRRU_A, 21, SEED + 630, 0.52)
    S.add_glass(mx, GLASS_PEDAL_G, 21, SEED + 725, 0.3)
    # B': the Hush over the low counterline
    S.add_glass(mx, S.HUSH_A, 25, SEED + 730, 0.68)
    S.add_flute(mx, COUNTER, 25, SEED + 640, 0.4)
    # D: both at once (the sketch's close)
    S.add_flute(mx, S.KIRRU_B, 29, SEED + 620, 0.46)
    S.add_glass(mx, S.HUSH_B, 29, SEED + 720, 0.6)
    # coda
    S.add_glass(mx, GLASS_CELL, 33, SEED + 740, 0.4)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=12.0)
    G = GAINS
    mx.bus("flute", G["flute"], send=0.45, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(1300, 1.0, 1.0),
                                                                       bq_lowpass(5000, 0.7)]))
    mx.bus("glass", G["glass"], send=0.55, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    mx.bus("engine", G["engine"], send=0.35, process=lambda x: filt(x, [bq_lowpass(900, 0.7), bq_highpass(30, 0.7)]))
    mx.bus("hum", G["hum"], send=0.25, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("deep", G["deep"], send=0.15)
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=800.0))
    mx.bus("silt", G["silt"], send=0.7)
    build(mx)
    hall = ModFDNReverb(rt60=4.2, rt60_high=1.0, predelay=0.04, size=1.35, mod_depth=9.0, mod_rate=0.3,
                        early_level=0.25, lowcut=80.0, seed=SEED % 9973)
    return V.finish(mx, "lowlight", out_path, BPM, 4, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -2.5, verbose,
                    stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
