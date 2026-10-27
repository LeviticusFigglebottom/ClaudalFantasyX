"""`dawn_road`: Ch9 B09 "The road out" (M3-AUD-819; act1_ch09.md §6): a 61.9 s seamless field loop.

Original material (SPEC §2): the walking pulse and the melody are our own Saltgrass Causeway's (saltgrass_causeway.py
LOW, the pulse's root-fifth-octave-fifth figure, and MEL_A, written for this project; nothing re-typed), and the
closing call in open fifths was written for this cue. None of it derives from an existing tune.

The brief: "Field bed, short. Sparse plucked strings and one wind instrument in open fifths: the Saltgrass
Causeway's walking pulse (ch03) come back, slower and older. The pilgrimage resumes." Dawn after the Ebbing: the line
forms on the coast road, and Kerrid falls in last. The causeway was the pilgrimage's first road (three voices
walking out, exposed); this is the same walk with more people in it and less left.

A minor pentatonic over open fifths (no thirds under the tune, so it is neither warm nor sad), 4/4 at 62 BPM (the
causeway's 84, slowed: a bar is 3.87 s), 16 bars.
* the walking pulse: the causeway's plucked low string through its small body on every beat (root, fifth, octave,
  fifth), slower and older: plucked nearer the middle, darker, shorter, the strings a little out with each other;
  a soft frame drum on the downbeat only;
* one wind: a low breath flute (wood, more breath than tone at the start of each phrase) plays the causeway's MEL_A,
  slower, then answers it with a call in open fifths (A-E, D-A, G-D, then the E held), the line the walkers
  carry on with;
* the morning air: a thin wind, much quieter than the causeway's, breathing on whole cycles per loop.
Form: 1-2 the pulse alone | 3-10 MEL_A on the flute | 11-14 the call in fifths | 15-16 the pulse alone, thinning,
an E to turn back to A at bar 1.

Loop: LOOPSTART = 0. The file starts a sixteenth before bar 1's downbeat (the sidecar's `downbeat_offset_s`), so the
wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/dawn_road.py   (or tools/audio/render_all.py --only dawn_road)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SG = _mod("saltgrass_causeway", os.path.join(HERE, "saltgrass_causeway.py"))
FA = _mod("field_ambience", os.path.join(ROOT, "assets_src", "sfx", "field_ambience.py"))

OUT = os.path.join(ROOT, "assets", "audio", "music", "dawn_road.ogg")
SEED = 20261823
TARGET_LUFS = -16.0
BPM = 62.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 16
LOOP_S = BARS * BAR
DOWNBEAT_OFFSET_S = BEAT / 4
FLUTE_PRE = 0.065                      # breath_flute speaks this late
## the roots per bar: the pulse alone (1-2), MEL_A's own roots on the causeway (its bars 5-12), the call (11-14),
## the pulse alone (15-16)
ROOTS = ["A", "A"] + SG.ROOTS[4:12] + ["A", "D", "G", "A"] + ["A", "E"]
PULSE = (12, 19, 24, 19)               # the causeway's figure on each beat: root, fifth, octave, fifth
## the call in open fifths over bars 11-14: (bar, beat, pitch, beats)
CALL = [(11, 0.0, "A4", 1.5), (11, 2.0, "E5", 2.0), (12, 0.0, "D5", 1.5), (12, 2.0, "A5", 2.0),
        (13, 0.0, "G4", 1.5), (13, 2.0, "D5", 2.0), (14, 0.0, "E5", 3.5)]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT + DOWNBEAT_OFFSET_S


def air(sr: int = SR) -> np.ndarray:
    """The morning air: a thin band of wind breathing on whole cycles per loop (periodic, so it wraps exactly)."""
    g = rng(SEED + 3)
    L = int(round(LOOP_S * sr))
    breath = 0.6 + 0.4 * (0.5 + 0.5 * FA.plfo(L, 0.08, g))
    lo = FA.stereo_noise(L, g, [bq_bandpass(420.0, 0.5), bq_lowpass(1400, 0.6)], 0.5)
    hi = FA.stereo_noise(L, g, [bq_bandpass(2100.0, 1.2)], 0.3)
    return (lo + 0.2 * hi) * breath[:, None] * 0.05


def flute_note(m: float, d: float, vel: float, seed: int, first: bool, held: bool) -> np.ndarray:
    return breath_flute(m, d * 0.95 + 0.04, vel, seed=seed, breath=0.5 if first else 0.38,
                        scoop_cents=35.0 if first else 10.0, vib_cents=8.0 if held else 2.5, vib_rate=4.3,
                        swell=0.18 if held else 0.0, attack=0.1 if first else 0.05, release=0.4, beta=0.46)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = SG.HV.lute_body(SEED + 5)
    mx.add("air", air(), 0.0)
    for bar, root in enumerate(ROOTS, start=1):
        low = n(SG.LOW[root])
        thin = bar >= 15
        for beat, off in enumerate(PULSE):
            if thin and beat % 2:
                continue
            v = (0.46 if beat == 0 else 0.32) * g.uniform(0.9, 1.06)
            out_of_true = float(g.normal(0.0, 0.06))                     # older strings, not quite with each other
            x = string_pluck(low + off + out_of_true, BEAT * 1.4, v, seed=SEED + 100 * bar + beat, pick_pos=0.3,
                             t60=1.3, mute=0.15, max_f=2800.0, release=0.12)
            mx.add("pulse", fft_convolve(x, body)[: len(x) + 4000], t_of(bar, beat) + float(g.normal(0, 0.009)),
                   pan=-0.15)
        mx.add("drum", frame_drum("dum", 0.3 * g.uniform(0.9, 1.06), variant=bar, seed=SEED + 1),
               t_of(bar) + float(g.normal(0, 0.006)), pan=0.1)
    # the wind: MEL_A from bar 3, slower than the causeway's plucked line, then the call in fifths
    first = True
    for i, bar_notes in enumerate(SG.MEL_A):
        pos = 0.0
        for p, beats in bar_notes:
            if p is None:
                first = True
            else:
                d = beats * BEAT
                x = flute_note(n(p), d, 0.5 * g.uniform(0.95, 1.04), SEED + 5000 + 37 * i + int(pos * 4), first,
                               beats >= 2)
                mx.add("flute", x, t_of(3 + i, pos) - FLUTE_PRE + float(g.normal(0, 0.005)), pan=0.15)
                first = False
            pos += beats
    for k, (bar, beat, p, beats) in enumerate(CALL):
        x = flute_note(n(p), beats * BEAT, 0.48 * g.uniform(0.95, 1.04), SEED + 7000 + k, beat == 0.0, beats >= 2)
        mx.add("flute", x, t_of(bar, beat) - FLUTE_PRE, pan=0.15)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]): the flute at L, the walking pulse
## L-4, the drum L-12, the air L-13.
GAINS = {"flute": 0.0, "pulse": -19.2, "drum": -2.3, "air": -12.2}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=6.0)
    mx.bus("flute", GAINS["flute"], send=0.3, process=lambda x: filt(x, [bq_highpass(160, 0.7), bq_peak(1600, 1.0, 1.0),
                                                                           bq_lowpass(6000, 0.7)]))
    mx.bus("pulse", GAINS["pulse"], send=0.2, process=lambda x: filt(x, [bq_highpass(45, 0.7), bq_lowpass(3000, 0.7)]))
    mx.bus("drum", GAINS["drum"], send=0.15)
    mx.bus("air", GAINS["air"], send=0.05, process=lambda x: filt(x, [bq_highpass(90, 0.7)]))
    build(mx)
    hall = ModFDNReverb(rt60=1.8, rt60_high=0.8, predelay=0.02, size=1.0, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.22, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"dawn_road: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses (LU vs the flute)", {k: round(v - mx.bus_lufs["flute"], 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
