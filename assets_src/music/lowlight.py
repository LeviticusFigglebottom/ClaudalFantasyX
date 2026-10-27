"""`lowlight`: Ch11, the Lowlight temple, half underwater, and the Lamp Engine still running in it (M3-AUD-804
sketch; act_outline Ch11, bible §5.6): a 62.1 s seamless loop.

Original composition for this project (SPEC §2, §9). Original-material check: the two tunes here are the game's own
motifs, developed, and nothing else is borrowed. (1) The flute plays the Kirru call from reedhollow.py (A-B-C#, a
leap up to F#; written for this task), moved to C and ending on a sixth instead of a raised fourth, and its answer
turned downward, sinking: Nhoa is Ressa, the only Kirru Cantor, held at the foot of the well-shaft. (2) The glass
plays the Hush's outline (hush_theme_v2.py: a long held note, a stepwise fall of a third, then the line settling a
sixth lower with a turn), in C minor: the Cantor's song she was given. The engine's pulse, the hum and every other
part were written for this cue. No existing melody or style is quoted.

The brief: the Ice temple, a half-flooded gallery temple whose sanctum is entirely underwater at the foot of a Lit
Age well-shaft, where the deep's cold wells up through the floor and drowned glimmer sifts down like silt (nothing
is frozen; the cold is the deep's, bible §5.6). Its guardian is the Lamp Engine, a still-running Lit Age machine full
of bound dead. So the cue is cold and deep, and under it a dead machine keeps a pulse: a muffled piston stroke on
every beat, limping on beat 4, stuttering every fourth bar, and stalling for two beats at the end of the loop before
it catches again.

C minor (Aeolian: C D Eb F G Ab Bb; the G chord at the end of each phrase takes B natural). The Kirru call brings
its own E and F# with it and sounds over a bare open fifth (C and G, no third), so the two musics never quite meet.
4/4 at 58 BPM (a bar is 4.138 s), 15 bars. Apart from every Act I cue: the only cue on C minor, and the only one with
a machine for a rhythm section.

Ensemble (all synthesized; no samples):
* the Lamp Engine (act2_voices.engine_thud): a low, sagging thump through water with a muffled valve clank; and
  its conduits' hum (act2_voices.conduit_hum: a choked buzz on C2 that flickers and sometimes nearly fails);
* the deep's cold (act2_voices.deep_cold): a very low heaving band of noise;
* a breath flute, low (C4-A4): the Kirru call (bars 4-7 and 12-14);
* a glass harmonica (act2_voices.glass): the Hush's outline (bars 8-11 and 12-15);
* a dark low string pad on the chords;
* the silt: tiny, very soft glints (pure tones of the scale) drifting down in register.

Form (bars): 1-3 the engine alone | 4-7 A, the Kirru call over the open fifth | 8-11 B, the Hush on glass over Cm
Ab Fm G | 12-15 both at once, and the engine stalls in bar 15 (beats 3 and 4 missing), catching again on bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth (the engine's stall).

Render:  python3 assets_src/music/lowlight.py   (or tools/audio/render_all.py --only lowlight)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__), "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT = os.path.join(ROOT, "assets", "audio", "music", "lowlight.ogg")
SEED = 20261804
TARGET_LUFS = -16.0
BPM = 58.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 15
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
QUALITY = 3.0

CHORDS = (["C5", "C5", "C5"]
          + ["C5", "C5", "C5", "C5"]
          + ["Cm", "Ab", "Fm", "G"]
          + ["C5", "C5", "Fm", "G"])
PAD = {"C5": "C2 G2 C3 G3", "Cm": "C2 G2 C3 Eb3", "Ab": "Ab1 Eb2 Ab2 C3", "Fm": "F1 C2 F2 Ab2", "G": "G1 D2 G2 B2"}

## the Kirru call, in C, low and slow (reedhollow.CALL's cell, its answer turned down)
KIRRU_A = [[("C4", 1), ("D4", .5), ("E4", 2.5)],
           [("A4", 3), (None, 1)],
           [("F#4", 1), ("E4", 1), ("D4", 2)],
           [("C4", 3), (None, 1)]]
KIRRU_B = [[("C4", 1), ("D4", .5), ("E4", 2.5)],
           [("A4", 3), (None, 1)],
           [("D4", 2), (None, 2)]]
## the Hush's outline on glass: the held note, the fall of a third, the turn a sixth below
HUSH_A = [[("G5", 4)],
          [("F5", 2), ("Eb5", 2)],
          [("Ab4", 1), ("G4", 1), ("F4", 1), ("G4", 1)],
          [("G4", 3), (None, 1)]]
HUSH_B = [[("G5", 4)],
          [("F5", 2), ("Eb5", 2)],
          [("Ab4", 1), ("G4", 1), ("F4", 1), ("G4", 1)],
          [("G4", 3), (None, 1)]]
SILT = ["C6", "D6", "Eb6", "G6", "Ab6", "C7", "D7", "Eb7", "G7"]

LEAD = "flute"
LEVELS = {"flute": 0.0, "glass": -1.0, "engine": -6.0, "hum": -12.0, "deep": -15.0, "pad": -11.0, "silt": -19.0}
GAINS = {"flute": 0.0, "glass": -6.9, "engine": -10.3, "hum": 1.2, "deep": -13.8, "pad": 2.2, "silt": -21.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def add_flute(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
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
            v = vel * float(g.uniform(0.94, 1.04))
            x = breath_flute(n(p), d * 0.96 + 0.03, v, seed=seed + int(round(pos * 1000)), breath=0.65,
                             scoop_cents=60.0 if first else 20.0, vib_cents=7.0 if beats >= 2 else 2.0,
                             vib_rate=3.8, swell=0.35 if beats >= 2 else 0.0, attack=0.14 if first else 0.07,
                             release=0.6, beta=0.4)
            mx.add("flute", x, pos - V.FLUTE_PRE + float(g.normal(0, 0.006)), pan=-0.15)
            pos += d
            first = False


def add_glass(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is not None:
                x = V.glass(n(p), d * 0.98, vel * float(g.uniform(0.93, 1.04)), seed + int(round(pos * 100)))
                mx.add("glass", x, pos - V.GLASS_PRE, pan=0.2)
            pos += d


def add_engine(mx: LoopMixer) -> None:
    """A stroke on every beat; beat 4 limps late; every fourth bar beat 2 stutters; bar 15 stalls after beat 2."""
    g = rng(SEED + 100)
    for bar in range(1, BARS + 1):
        for beat in range(4):
            if bar == BARS and beat >= 2:
                continue
            vel = (0.95 if bar == 1 else 0.85, 0.45, 0.7, 0.45)[beat] * float(g.uniform(0.9, 1.05))
            late = 0.045 if beat == 3 else 0.0
            t0 = t_of(bar, beat) + late + float(g.normal(0, 0.012))
            mx.add("engine", V.engine_thud(g, vel), t0, pan=-0.05)
            if beat == 1 and bar % 4 == 0:
                mx.add("engine", V.engine_thud(g, vel * 0.6), t0 + 0.17, pan=0.05)


def add_silt(mx: LoopMixer, g) -> None:
    """Drowned glimmer sifting down: strings of three to five glints, each a step lower in the scale."""
    pos = float(g.uniform(0.5, 2.0))
    while pos < LOOP_S - 1.0:
        top = int(g.integers(4, len(SILT)))
        count = int(g.integers(3, 6))
        pan = float(g.uniform(-0.7, 0.7))
        tt = pos
        for k in range(count):
            idx = top - k
            if idx < 0:
                break
            f = midi_to_hz(n(SILT[idx]))
            N = int(1.2 * SR)
            t = np.arange(N) / SR
            x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) * np.minimum(1.0, t / 0.01)
            mx.add("silt", 0.2 * float(g.uniform(0.5, 1.0)) * x, tt, pan=pan - 0.05 * k)
            tt += float(g.uniform(0.25, 0.6))
        pos += float(g.uniform(3.0, 7.0))


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("hum", V.conduit_hum(LOOP_S, n("C2"), rng(SEED + 7)), 0.0)
    mx.add("deep", V.deep_cold(LOOP_S, SEED + 8), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.95, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=1.8, release=1.8, width=0.7)
        mx.add("pad", x, t_of(bar) - 0.4)
    add_engine(mx)
    add_silt(mx, g)
    add_flute(mx, KIRRU_A, 4, SEED + 600, 0.5)
    add_flute(mx, KIRRU_B, 12, SEED + 620, 0.46)
    add_glass(mx, HUSH_A, 8, SEED + 700, 0.7)
    add_glass(mx, HUSH_B, 12, SEED + 720, 0.6)


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
