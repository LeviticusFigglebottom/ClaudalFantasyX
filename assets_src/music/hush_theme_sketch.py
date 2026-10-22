"""'Hush' main theme: M1 sketch (score-as-code).

Original composition for this project (SPEC §2, §9). Piano-led, melancholy,
A minor (Aeolian with a major V for the bittersweet half cadences), 3/4 at
~72 BPM with a closing ritardando. Light gamelan-like metallophone, a soft
string pad, and a brief breathy-flute counterline in the reprise.

Form (bars):  1-2 intro | 3-10 A (statement) | 11-18 B (rise to the A5
climax in bar 14) | 19-24 A' (reprise, the head now climbs instead of
falls, flute counterline) | 25-26 tail.

The melodic cell is: long held note, stepwise fall of a third (E-D-C), then
the line settling a sixth below (A) with a turn. It was written for this
project, not adapted from any existing melody.

Render:  python3 assets_src/music/hush_theme_sketch.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, fft_convolve, rng  # noqa: E402
from synth.flute import flute_note  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.piano import piano_note, soundboard_ir  # noqa: E402
from synth.reverb import FDNReverb  # noqa: E402
from synth.score import Score, TempoMap, ns  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "hush_theme_sketch.ogg")
SEED = 20261022
TARGET_LUFS = -16.0
BARS = 26

# --------------------------------------------------------------------------- #
# Harmony. Per bar: left-hand broken-chord tones (bass, fifth, colour1, colour2)
# and a pad voicing.  None = same as previous bar.
# --------------------------------------------------------------------------- #
LH = {
    1: "A2 E3 B3 C4", 2: "A2 E3 B3 C4",
    # A section
    3: "A2 E3 B3 C4",    # Am(add9)
    4: "F2 C3 A3 E4",    # Fmaj7
    5: "G2 E3 C4 D4",    # C/G (add9)
    6: "E2 B2 G3 D4",    # Em7
    7: "D2 A2 F3 E4",    # Dm9
    8: "C3 E3 A3 B3",    # Am/C (add9)
    9: "E2 B2 A3 D4",    # E7sus4
    10: "E2 B2 G#3 D4",  # E7
    # B section
    11: "F2 C3 A3 E4",   # Fmaj7
    12: "G2 D3 A3 B3",   # G(add9)
    13: "E2 B2 G3 D4",   # Em7
    14: "A2 E3 B3 C4",   # Am(add9)  - climax
    15: "D2 A2 F3 C4",   # Dm7
    16: "G2 D3 F3 C4",   # G7sus4
    17: "C3 G3 B3 E4",   # Cmaj7
    18: "G#2 E3 B3 D4",  # E7/G#
    # A' reprise
    19: "A2 E3 B3 C4",   # Am(add9)
    20: "F2 C3 A3 E4",   # Fmaj7
    21: "D2 A2 F3 E4",   # Dm9
    22: "E2 B2 A3 D4",   # E7sus4 -> E7 (G# on beat 3)
    23: "F2 C3 A3 B3",   # Fmaj7(#11)
    24: "A2 E3 B3 C4",   # Am(add9)
}

PAD = {
    1: "A3 E4 B4", 3: "A3 C4 E4 B4", 4: "F3 A3 C4 E4", 5: "G3 C4 E4 D5", 6: "E3 G3 B3 D4",
    7: "D3 F3 A3 E4", 8: "C4 E4 A4", 9: "E3 A3 B3 D4", 10: "E3 G#3 B3 D4",
    11: "F3 A3 C4 E4", 12: "G3 B3 D4 A4", 13: "E3 G3 B3 D4", 14: "A3 C4 E4 B4", 15: "D3 F3 A3 C4",
    16: "G3 C4 D4 F4", 17: "C4 E4 G4 B4", 18: "G#3 B3 D4 E4",
    19: "A3 C4 E4 B4", 20: "F3 A3 C4 E4", 21: "D3 F3 A3 E4", 22: "E3 A3 B3 D4", 23: "F3 A3 B3 E4",
    24: "A3 C4 E4 B4",
}

# Melody (right hand). (pitch, beats[, velocity]).
MEL_A = [  # bars 3-10
    ("E5", 2, .52), ("D5", .5, .44), ("C5", .5, .42),
    ("A4", 2, .46), ("G4", .5, .38), ("A4", .5, .40),
    ("G4", 1, .42), ("C5", 1, .46), ("D5", 1, .50),
    ("E5", 2, .55), ("G5", 1, .52),
    ("F5", 1.5, .56), ("E5", .5, .48), ("D5", 1, .46),
    ("C5", 2, .46), ("B4", .5, .40), ("A4", .5, .38),
    ("B4", 1, .42), ("D5", 1, .46), ("E5", 1, .50),
    ("E5", 3, .44),
]
MEL_B = [  # bars 11-18
    ("A5", 2, .62), ("G5", .5, .52), ("F5", .5, .50),
    ("G5", 2, .58), ("D5", 1, .48),
    ("E5", 1.5, .55), ("F5", .5, .56), ("G5", 1, .62),
    ("A5", 3, .72),
    ("F5", 1, .58), ("E5", 1, .53), ("D5", 1, .50),
    ("D5", 1.5, .52), ("C5", .5, .46), ("B4", 1, .44),
    ("C5", 1, .46), ("E5", 1, .52), ("G5", 1, .56),
    ("B4", 2, .48), ("G#4", 1, .42),
]
MEL_C = [  # bars 19-24
    ("E5", 2, .46), ("D5", .5, .40), ("C5", .5, .38),
    ("A4", 2, .40), ("B4", .5, .37), ("C5", .5, .39),
    ("D5", 1, .42), ("F5", 1, .46), ("E5", 1, .42),
    ("E5", 2, .42), ("D5", .5, .36), ("B4", .5, .34),
    ("C5", 3, .36),
    ("A4", 3.6, .32),
]
# Soft inner dyads under the B section (RH thumb), one per bar on beat 1.
INNER = {11: "C4 E4", 12: "B3 D4", 13: "B3 E4", 14: "C4 E4", 15: "A3 D4", 16: "F4", 17: "E4 G4", 18: "D4 E4"}

FLUTE = [  # bars 19-23, a quiet counterline above the reprise
    ("C6", 3, .40), ("C6", 2, .42), ("B5", 1, .40), ("A5", 3, .42), ("B5", 2, .40), ("G#5", 1, .36),
    ("A5", 2.6, .34),
]

# Metallophone: (bar, beat, pitch, vel, decay)
METAL = [
    (1, 1, "E5", .42, 5.0), (1, 2.5, "A5", .32, 4.5), (2, 1, "B5", .36, 4.5), (2, 3, "E5", .28, 4.0),
    (3, 1, "A5", .26, 4.5), (7, 1, "A5", .24, 4.0),
    (11, 1, "C6", .32, 4.0), (13, 1, "B5", .32, 4.0), (14, 1, "E6", .36, 4.5), (15, 1, "A5", .30, 4.0),
    (17, 1, "G5", .30, 4.0), (18, 2, "B5", .26, 3.5),
    (19, 1, "A5", .26, 4.5), (23, 1, "E6", .24, 4.5),
    (24, 1, "A5", .34, 6.0), (24, 1, "E5", .26, 6.0), (25, 2, "B5", .22, 5.0),
]


def build_score() -> Score:
    sc = Score(beats_per_bar=3)
    # Left hand: six eighths per bar, pattern bass-fifth-c1-c2-c1-fifth.
    for bar in range(1, 25):
        b, f, c1, c2 = LH[bar].split()
        pat = [b, f, c1, c2, c1, f]
        if bar == 22:  # sus4 resolves on beat 3
            pat = [b, f, c1, c2, "G#3", f]
        intro = bar <= 2
        for i, p in enumerate(pat):
            vel = (0.40 if i == 0 else 0.27 if i in (1, 5) else 0.31) * (0.8 if intro else 1.0)
            if 11 <= bar <= 18:
                vel *= 1.12
            if bar >= 22:
                vel *= 0.85
            sc.add("piano", bar, 1 + 0.5 * i, p, 0.5 if i else 1.5, vel, lh=True)
    # final low octave
    sc.add("piano", 25, 1, ["A1", "A2"], 3, 0.30)
    sc.line("piano", 3, MEL_A)
    sc.line("piano", 11, MEL_B)
    sc.line("piano", 19, MEL_C)
    for bar, notes in INNER.items():
        sc.add("piano", bar, 1, notes.split(), 2.5, 0.26)
    sc.line("flute", 19, FLUTE)
    for bar, beat, p, v, d in METAL:
        sc.add("metal", bar, beat, p, 0.0, v, decay=d)
    # pad: one chord per harmony change, held until the next one
    keys = sorted(PAD)
    for i, bar in enumerate(keys):
        nxt = keys[i + 1] if i + 1 < len(keys) else 26
        vel = 0.55 if bar < 11 else 0.75 if bar < 19 else 0.5
        sc.add("pad", bar, 1, PAD[bar].split(), (nxt - bar) * 3 + 0.4, vel)
    return sc


def tempo() -> TempoMap:
    bpb = 3
    pts = [(0, 70), ((3 - 1) * bpb, 72), ((14 - 1) * bpb, 74), ((16 - 1) * bpb, 72),
           ((22 - 1) * bpb, 70), ((24 - 1) * bpb, 58), ((25 - 1) * bpb, 50), (26 * bpb, 50)]
    return TempoMap(pts, total_beats=BARS * bpb)


def pedal_release(tm: TempoMap, t_off: float) -> float:
    """Sustain pedal changes on every downbeat (legato pedalling, lifted just
    after the new bass note). A note's damper falls at the first pedal lift
    after its key-up."""
    beat = np.interp(t_off, tm.times, tm.grid)
    bar_beat = (np.floor(beat / 3) + 1) * 3   # next downbeat
    if beat % 3 < 0.05:                       # key-up right on a downbeat
        bar_beat = np.floor(beat / 3) * 3
    return max(t_off, tm.t(bar_beat) + 0.07)


def render(out_path: str = OUT, verbose: bool = True) -> dict:
    sc = build_score()
    tm = tempo()
    g = rng(SEED)
    end_t = tm.t(BARS * 3) + 4.5
    mx = Mixer(end_t)
    sb = soundboard_ir()
    mx.bus("piano", 0.0, send=0.22, process=lambda x: 0.75 * x + 0.25 * fft_convolve(x, sb)[: len(x)])
    mx.bus("metal", -9.0, send=0.40)
    mx.bus("pad", -15.0, send=0.55, process=string_body)
    mx.bus("flute", -17.0, send=0.40)

    for k, ev in enumerate(sorted(sc.events, key=lambda e: (e.beat, e.inst))):
        t0 = tm.t(ev.beat)
        dur = tm.t(ev.beat + ev.beats) - t0
        jit = g.normal(0, 0.006)
        vel = float(np.clip(ev.vel * (1 + g.normal(0, 0.05)), 0.05, 1.0))
        seed = SEED + 7919 * k
        if ev.inst == "piano":
            pitches = ev.pitch if isinstance(ev.pitch, list) else [ev.pitch]
            for j, p in enumerate(pitches):
                hold = pedal_release(tm, t0 + dur * 0.95) - t0
                if ev.beat >= 23 * 3:  # last bars: pedal held down to the end
                    hold = tm.t(BARS * 3) - t0 + 1.0
                x = piano_note(p, vel, hold, seed=seed + j)
                pan = float(np.clip((p - 64) / 40.0, -0.45, 0.45))  # player's-eye keyboard spread
                mx.add("piano", x, max(0.0, t0 + jit + 0.004 * j), pan=pan)
        elif ev.inst == "metal":
            x = metallophone_note(ev.pitch, vel, seed=seed, decay=ev.opts.get("decay", 4.5), hardness=0.45,
                                  ombak_hz=5.5)
            mx.add("metal", x, max(0.0, t0 + jit), pan=0.25)
        elif ev.inst == "flute":
            x = flute_note(ev.pitch, dur * 0.97, vel, seed=seed, breath=0.32)
            mx.add("flute", x, max(0.0, t0 + jit), pan=-0.2)
        elif ev.inst == "pad":
            x = pad_chord(ev.pitch, dur, vel, seed=seed, attack=1.4 if ev.beat > 0 else 3.0, release=2.0)
            mx.add("pad", x, max(0.0, t0))

    hall = FDNReverb(rt60=2.6, predelay=0.024, damping=0.32, size=1.1, seed=SEED % 9973)
    master = mx.render(reverb=hall, reverb_return_db=-2.0)
    # trim trailing silence below -70 dBFS, then a short fade
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(1.5 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=4.0)
    m = measure(master)
    if verbose:
        print(f"hush_theme_sketch: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  "
              f"peak {m['sample_peak_dbfs']:.2f} dBFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
