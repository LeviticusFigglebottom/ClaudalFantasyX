"""`iskarra_ruins`: Ch19 "Iskarra", the Iskarra Ruins in full, the prologue's place now understood (M3-AUD-856;
act3_plan.md §2, act_outline Ch19, docs/kb/art/environments/iskarra.md): a 136.8 s seamless zone loop.

Original composition for this project (SPEC §2, §9). Original-material check: the only tune not written here is the
Hush's first verse (hush_theme_v2.py MEL_A), imported and never retyped; it sounds two octaves down, as
iskarra_vigil.py set it, and its first cell answers once in the glass. The motes' rising figures and the halo's
pitches are iskarra_vigil's own (loaded from it, not retyped), so the loop is that cue's world. Everything else was
written for this cue and shares no phrase with the game's other themes or any melody we know: the chord plan, and
the viola's counterline in B and A' (a line that climbs a step at a time from A4 and comes to rest on E5, then
rhymes itself an octave-span wider). The style evoked is an elegy for strings over a sea drone; nothing is quoted.

The brief: the Lit Age capital drowned to its sixth storey, white towers in gold dusk light, the prologue's vigil
plaza ("Everyone I'm going to tell you about is still here tonight"), seen again with everything the player now
knows. The iskarra_vigil's world as a loop: the deep MEL_A two octaves down, the drone on A, glass motes that rise.
Beauty in decline: an elegy, never a lament that wallows, so the middle register is warm (dusk gold, a string pad
and a viola) and every line in it climbs; nothing sobs, nothing swells past mezzo-piano. No voices and no words.
It plays over the `iskarra_dusk` ambience bed (prologue_ambience.py: the towers' wind, the laps, the drips), so it
carries no wind or lapping of its own: only the deep sea under the drone.

A aeolian (A B C D E F G), over a drone on A that never moves. 3/4 at 50 BPM (a beat is 1.2 s, a bar 3.6 s; the
vigil's deep line was 1.6 s a beat, through-composed; a loop walks a little faster), 38 bars.

Ensemble (all synthesized; no samples):
* the sea drone on A (A1, E2, A2: act2_voices.periodic_drone, breathing once every 13.7 s, exactly periodic) and the
  deep's slow heave under it (act2_voices.deep_cold);
* MEL_A two octaves down on low strings, sul tasto and filtered dark (iskarra_vigil's recipe), twice;
* the dusk gold: a warm string pad in the middle register (B, A' and the thinning), and a viola's counterline;
* deep piano octaves under a light constant pedal, filtered as if heard through the sea, at the phrases' joints;
* above 2.6 kHz: the glass motes rising (iskarra_vigil.RISE, more of them as the loop goes on), a faint high halo
  of beating glass tones (iskarra_vigil.HALO, each pair snapped to whole cycles so it wraps), and MEL_A's first
  cell in the glass once, the theme above answering the theme below.

Form (bars):
*  1-4   the sea: the drone, the deep; a piano octave on A; the first motes rise
*  5-12  A: MEL_A two octaves down over the drone alone (the vigil, looped)
* 13-20  B, the dusk gold: the pad (F C Dm Am | F G Em Am) and the viola's climbing line, ending held on E5; a piano
         octave on E at the phrase's joint
* 21-28  A': MEL_A in the deep again, now harmonized (Am F C Am | Dm F Em Am) with the viola answering above it
* 29-34  the thinning: the pad (F F Dm Dm Em Em), a piano octave on A with its fifth, the glass's answer (MEL_A's
         first cell), the motes rising thickest
* 35-38  the sea again; the last rising figure (iskarra_vigil.RISE_LAST) left open on B; bar 38 is bar 1's sea

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a quarter of a beat before bar 1's downbeat (the
sidecar's `downbeat_offset_s`); nothing is struck there, so the seam falls inside the drone.

Render:  python3 assets_src/music/act3/iskarra_ruins.py   (or tools/audio/render_all.py --act3 --only
act3/iskarra_ruins)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.grand import PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act3_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _mod("act2_voices")      # the Act II kit: periodic_drone, deep_cold, snap, finish()
ISK = _mod("iskarra_vigil")  # the Act I break: its rising figures, its halo, its band filters
HUSH = ISK.HUSH              # hush_theme_v2: MEL_A

OUT = os.path.join(ROOT, "assets", "audio", "music", "act3", "iskarra_ruins.ogg")
SEED = 20261856
TARGET_LUFS = -16.0
QUALITY = 3.0
BPM = 50.0
BEAT = 60.0 / BPM
BAR_BEATS = 3
BAR = BAR_BEATS * BEAT
BARS = 38
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
DEEP_SHIFT = -24             # MEL_A two octaves down (iskarra_vigil.DEEP_SHIFT)
LINE_BARS = (5, 21)          # where MEL_A starts in the deep (it is 8 bars long)
CELL_SHIFT = 36              # MEL_A's first cell in the glass: three octaves up (E8 D8 C8 A7, as the vigil)
PEDAL_DEPTH = 0.4            # the deep octaves: a light, constant pedal, so the soundboard bus is time-invariant

## the pad, bar by bar (None: no pad)
CHORDS = ([None] * 12
          + ["F", "C", "Dm", "Am", "F", "G", "Em", "Am"]
          + ["Am", "F", "C", "Am", "Dm", "F", "Em", "Am"]
          + ["F", "F", "Dm", "Dm", "Em", "Em"]
          + [None] * 4)
PAD = {"F": "F3 C4 A4", "C": "E3 G3 C4", "Dm": "D3 A3 F4", "Am": "E3 A3 C4", "G": "D3 G3 B3", "Em": "E3 B3 G4"}

## the viola: bar -> [(pitch | None, beats)]
VIOLA = {
    13: [("A4", 2), ("C5", 1)], 14: [("G4", 1.5), ("E4", 0.5), ("G4", 1)], 15: [("F4", 2), ("A4", 1)],
    16: [("E4", 3)], 17: [("A4", 1), ("C5", 1), ("D5", 1)], 18: [("D5", 2), ("B4", 1)],
    19: [("B4", 1.5), ("C5", 0.5), ("D5", 1)], 20: [("E5", 3)],
    21: [(None, 1), ("C5", 2)], 22: [("A4", 3)], 23: [(None, 1), ("E5", 2)], 24: [("C5", 3)],
    25: [(None, 1), ("F5", 2)], 26: [("E5", 1.5), ("D5", 1.5)], 27: [("B4", 1.5), ("C5", 0.5), ("D5", 1)],
    28: [("E5", 3)],
}

## the deep piano octaves: (bar, pitches, velocity)
PIANO = [(1, ("A0", "A1"), 0.42), (13, ("E1", "E2"), 0.36), (29, ("A0", "A1", "E2"), 0.4), (35, ("E1", "E2"), 0.3)]

## the motes: (bar, beat, figure); "rise" is the vigil's four, "short" its first three
MOTES = [(1, 1.5, "rise"), (3, 0.5, "short"), (6, 1.0, "rise"), (9, 2.0, "rise"), (11, 0.5, "short"),
         (14, 1.0, "rise"), (16, 2.0, "short"), (18, 0.5, "rise"), (22, 1.5, "rise"), (24, 2.0, "short"),
         (26, 0.5, "rise"), (29, 1.0, "rise"), (30, 0.5, "short"), (30, 2.5, "rise"), (31, 1.5, "rise"),
         (32, 2.0, "short"), (33, 0.5, "rise"), (33, 2.5, "short"), (34, 1.5, "rise")]
LAST_RISE_BAR = 36           # iskarra_vigil.RISE_LAST, left open on B
CELL_BAR = 30                # the glass answers the second deep line


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def halo(seed: int) -> np.ndarray:
    """iskarra_vigil's halo as a loop: each HALO tone a slowly beating pair whose frequencies and swell are snapped
    to whole cycles per loop, so it wraps without a seam. Stereo, exactly one loop long."""
    g = rng(seed)
    N = int(round(LOOP_S * SR))
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    for k, (p, lvl) in enumerate(ISK.HALO):
        f0 = midi_to_hz(n(p))
        sw = 0.5 - 0.5 * np.cos(2 * np.pi * V.snap(1.0 / (11.0 + 3.0 * k), LOOP_S) * t + g.uniform(0, 6.28))
        s = lvl * sw * (np.sin(2 * np.pi * V.snap(f0, LOOP_S) * t + g.uniform(0, 6.28))
                        + 0.8 * np.sin(2 * np.pi * V.snap(f0 + 0.4 + 0.25 * k, LOOP_S) * t + g.uniform(0, 6.28)))
        out[:, k % 2] += s
        out[:, 1 - k % 2] += 0.5 * s
    return out * 0.02


def deep_line(bar: int) -> list[tuple[float, float, int, float]]:
    """MEL_A two octaves down from `bar`: [(t, dur, midi, vel)]; its long notes lean a little long (legato)."""
    out, pos = [], t_of(bar)
    for p, beats, v in HUSH.MEL_A:
        d = beats * BEAT
        out.append((pos, d * (1.1 if beats >= 2 else 1.0), n(p) + DEEP_SHIFT, v))
        pos += d
    return out


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("A1"), 1.0), (n("E2"), 0.55), (n("A2"), 0.35)], SEED + 1,
                                     partials=5, breath_s=LOOP_S / 10, tilt=0.5), 0.0)
    mx.add("deep", V.deep_cold(LOOP_S, SEED + 2), 0.0)
    mx.add("halo", halo(SEED + 3), 0.0)
    # MEL_A in the deep, twice: low strings, legato, sul tasto
    for k, bar in enumerate(LINE_BARS):
        for i, (t0, d, m, v) in enumerate(deep_line(bar)):
            x = pad_chord([m], d + 0.25, vel=0.5 + 0.6 * v, seed=SEED + 100 + 40 * k + i, voices=4, spread_cents=7.0,
                          attack=min(0.6, 0.4 * d), release=1.4, width=0.5)
            mx.add("line", x, t0 - 0.1)
    # the dusk gold: one pad swell per run of the same chord
    bar = 1
    while bar <= BARS:
        ch = CHORDS[bar - 1]
        run = 1
        while bar + run <= BARS and CHORDS[bar + run - 1] == ch:
            run += 1
        if ch is not None:
            x = pad_chord([n(p) for p in PAD[ch].split()], run * BAR - 0.3, 0.42, seed=SEED + 200 + bar, attack=1.4,
                          release=2.0, voices=3, spread_cents=6.0, width=0.7)
            mx.add("pad", x, t_of(bar) - 0.4)
        bar += run
    # the viola
    for bar in sorted(VIOLA):
        pos = t_of(bar)
        for p, beats in VIOLA[bar]:
            d = beats * BEAT
            if p is not None:
                x = pad_chord([n(p)], d * 0.98, 0.7 * float(g.uniform(0.95, 1.03)), seed=SEED + 400 + int(pos * 10),
                              voices=3, spread_cents=4.0, attack=min(0.45, 0.3 * d), release=1.0, width=0.35)
                mx.add("viola", x, pos - 0.08, pan=0.2)
            pos += d
    # the deep piano octaves
    notes = [dict(m=n(p), vel=v - 0.04 * j, t0=t_of(bar) + 0.05 * j, key_up=9.0)
             for bar, ps, v in PIANO for j, p in enumerate(ps)]
    pedal = PedalCurve(np.array([0.0, 1.0e6]), np.array([PEDAL_DEPTH, PEDAL_DEPTH]))
    jobs = [(grand_note, dict(m=nt["m"], vel=nt["vel"], key_up=nt["key_up"], seed=SEED + 7919 * k, t_abs=nt["t0"],
                              pedal=pedal)) for k, nt in enumerate(notes)]
    for nt, x in zip(notes, render_jobs(jobs)):
        mx.add("piano", x, nt["t0"], pan=-0.1)
    # the motes rise
    for k, (bar, beat, fig) in enumerate(MOTES):
        notes_ = ISK.RISE if fig == "rise" else ISK.RISE[:3]
        for j, p in enumerate(notes_):
            x = metallophone_note(n(p), 0.2 + 0.03 * j, seed=SEED + 500 + 10 * k + j, decay=4.0, hardness=0.2,
                                  ombak_hz=3.5)
            mx.add("motes", x, t_of(bar, beat) + 0.28 * j + float(g.normal(0, 0.01)), pan=-0.5 + 0.33 * j)
    for j, p in enumerate(ISK.RISE_LAST):
        x = metallophone_note(n(p), 0.22, seed=SEED + 800 + j, decay=5.0, hardness=0.18, ombak_hz=3.0)
        mx.add("motes", x, t_of(LAST_RISE_BAR, 0.5) + 0.45 * j, pan=-0.3 + 0.3 * j)
    # the theme above answers the theme below: MEL_A's first cell (its first four notes, in their own rhythm)
    pos = t_of(CELL_BAR, 0.5)
    for j, (p, beats, v) in enumerate(HUSH.MEL_A[:4]):
        x = metallophone_note(n(p) + CELL_SHIFT, 0.24, seed=SEED + 700 + j, decay=4.5, hardness=0.18, ombak_hz=3.0)
        mx.add("motes", x, pos, pan=0.35)
        pos += beats * BEAT * 0.7


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"], each bus gated where it plays), relative to
# the deep line (0 LU): the viola -3, the pad -6, the drone -5 (the bed itself), the deep -12, the piano -6 where it
# sounds, the motes -6 and the halo -12 (the only layers over 2.6 kHz, so they carry the loop's air).
GAINS = {"line": 0.0, "viola": -3.5, "pad": -1.0, "drone": -9.0, "deep": -15.5, "piano": 16.5, "motes": -3.8,
         "halo": -5.0}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = GAINS
    low = ISK.low_band
    mx.bus("line", G["line"], send=0.3, process=lambda x: filt(string_body(x, cutoff=700.0), [bq_lowpass(900, 0.7)]))
    mx.bus("viola", G["viola"], send=0.4, process=lambda x: string_body(x, cutoff=2400.0))
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1400.0))
    mx.bus("drone", G["drone"], send=0.2, process=low)
    mx.bus("deep", G["deep"], send=0.15, process=low)
    body = PianoBody(PedalCurve(np.array([0.0, 1.0e6]), np.array([PEDAL_DEPTH, PEDAL_DEPTH])))
    mx.bus("piano", G["piano"], send=0.3, process=lambda x: low(body(x)))
    mx.bus("motes", G["motes"], send=0.55, process=ISK.high_band)
    mx.bus("halo", G["halo"], send=0.4, process=ISK.high_band)
    build(mx)
    hall = ModFDNReverb(rt60=3.8, rt60_high=1.6, predelay=0.035, size=1.25, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.18, lowcut=40.0, seed=SEED % 9973)     # the vigil's hall: open dusk over water
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "iskarra_ruins", out_path, BPM, BAR_BEATS, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, hall, -2.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
