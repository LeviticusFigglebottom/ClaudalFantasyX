"""`saltgrass_causeway`: the B06 field bed (M2-AUD-11; vertical_slice.md §6): an 80 s seamless loop.

Original composition for this project (SPEC §2); the melody below was written for this cue and is not derived
from any existing tune. The brief: "Wind, sparse plucked strings, open fifths, a walking pulse." B06's emotional
purpose: three voices walking a tidal causeway at low tide, exposed; "the path leads somewhere that doesn't come
back."

A minor pentatonic (A C D E G) over open fifths (no thirds in the accompaniment, so it is neither warm nor sad),
4/4 at 84 BPM (a walk), 28 bars.
* wind: a band of noise breathing on a 20 s cycle, with slower gusts, exactly one loop long;
* the walking pulse: a plucked low string through a small body on every beat (root, fifth, octave, fifth), a soft
  frame drum on beats 1 and 3;
* the melody: a sparse plucked line, high and bare, with long rests; its phrases end on D or A, never on the third,
  and the B phrase climbs to C6 once and comes back down;
* a far kettle gong at each section.
Form: 1-4 wind and pulse | 5-12 melody A | 13-16 the pulse turns to F and G | 17-24 melody B | 25-28 pulse thins.

Render:  python3 assets_src/music/saltgrass_causeway.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

_spec = importlib.util.spec_from_file_location("haluna_village", os.path.join(os.path.dirname(__file__),
                                                                               "haluna_village.py"))
HV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HV)

OUT = os.path.join(ROOT, "assets", "audio", "music", "saltgrass_causeway.ogg")
SEED = 20261111
TARGET_LUFS = -16.0
BPM = 84.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 28
LOOP_S = BARS * BAR

ROOTS = (["A", "A", "D", "A"] + ["A", "A", "D", "E", "A", "A", "F", "G"] + ["F", "G", "A", "A"]
         + ["D", "D", "A", "A", "F", "G", "E", "E"] + ["A", "A", "D", "A"])
LOW = {"A": "A1", "D": "D2", "E": "E2", "F": "F1", "G": "G1"}
MEL_A = [[("E5", 2), ("D5", 1), ("C5", 1)], [("A4", 4)], [(None, 2), ("C5", 1), ("D5", 1)], [("E5", 3), ("G5", 1)],
         [("A5", 2), ("G5", 1), ("E5", 1)], [("D5", 4)], [(None, 2), ("E5", 1), ("D5", 1)], [("D5", 4)]]
MEL_B = [[("G5", 2), ("A5", 2)], [("C6", 3), ("A5", 1)], [("G5", 2), ("E5", 1), ("D5", 1)], [("E5", 4)],
         [("A5", 2), ("G5", 1), ("E5", 1)], [("D5", 2), ("C5", 2)], [("D5", 3), ("E5", 1)], [("A4", 4)]]


## The file starts a sixteenth before bar 1's downbeat, so the wrap doesn't land on its heaviest attack (gong, pulse
## and drum together); the loop is periodic, so nothing else changes. The sidecar records it.
DOWNBEAT_OFFSET_S = BEAT / 4


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT + DOWNBEAT_OFFSET_S


def wind(sr: int = SR) -> np.ndarray:
    """One loop of wind: noise through a slowly moving band, breathing on whole cycles per loop. Rendered k samples
    longer than the loop, and the extra k folded into the start with a crossfade, so the sample after the loop's
    last one continues it (the wrap is seamless)."""
    g = rng(SEED + 3)
    N = int(round(LOOP_S * sr))
    k = int(0.5 * sr)
    t = np.arange(N + k) / sr
    out = np.zeros((N + k, 2))
    for ch in range(2):
        lo = filt(g.standard_normal(N + k), [bq_bandpass(380.0, 0.5), bq_lowpass(1500, 0.6)])
        hi = filt(g.standard_normal(N + k), [bq_bandpass(1900.0, 1.2)])
        breath = 0.55 + 0.45 * np.sin(2 * np.pi * 4 * t / LOOP_S + ch * 0.9) ** 2
        gust = 0.7 + 0.3 * np.sin(2 * np.pi * 11 * t / LOOP_S + 1.3 + ch) * np.sin(2 * np.pi * 3 * t / LOOP_S)
        out[:, ch] = (lo + 0.25 * hi * breath) * breath * gust
    w = np.linspace(0, 1, k)[:, None]
    loop = out[:N].copy()
    loop[:k] = out[:k] * w + out[N:] * (1 - w)
    return loop * 0.05


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = HV.lute_body(SEED + 5)
    mx.add("wind", wind(), 0.0)
    for bar, root in enumerate(ROOTS, start=1):
        low = n(LOW[root])
        thin = bar >= 27
        for beat, off in enumerate((12, 19, 24, 19)):
            if thin and beat % 2:
                continue
            v = (0.50 if beat == 0 else 0.36) * g.uniform(0.92, 1.05)
            x = string_pluck(low + off, BEAT * 1.6, v, seed=SEED + 100 * bar + beat, pick_pos=0.2, t60=2.0,
                             max_f=4000.0, release=0.1)
            mx.add("pulse", fft_convolve(x, body)[: len(x) + 4000], t_of(bar, beat) + float(g.normal(0, 0.006)),
                   pan=-0.15)
        for beat, (stroke, v) in enumerate((("dum", 0.42), ("ghost", 0.12), ("dum", 0.30), ("ghost", 0.12))):
            if bar <= 2 and stroke == "ghost":
                continue
            mx.add("drum", frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=bar * 4 + beat, seed=SEED + 1),
                   t_of(bar, beat) + float(g.normal(0, 0.005)), pan=0.1)
    for start, mel in ((5, MEL_A), (17, MEL_B)):
        for i, bar_notes in enumerate(mel):
            pos = 0.0
            for p, beats in bar_notes:
                if p is not None:
                    x = string_pluck(n(p), beats * BEAT, 0.55 * g.uniform(0.94, 1.04), seed=SEED + 5000 + 97 * start
                                     + 13 * i + int(pos * 4), pick_pos=0.11, t60=3.2, max_f=7000.0, release=0.25)
                    mx.add("melody", fft_convolve(x, body)[: len(x) + 4000],
                           t_of(start + i, pos) + float(g.normal(0, 0.008)), pan=0.25)
                pos += beats
    for bar, p in ((1, "A5"), (13, "E5"), (25, "A5")):
        mx.add("gong", kettle_gong(n(p), 0.25, seed=SEED + 900 + bar, t60=3.0), t_of(bar), pan=-0.3)


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"]): the melody at L, the walking pulse L-4,
# the wind L-6 (it is the scene, not a backdrop), the drum L-10, the gongs L-14.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=6.0)
    mx.bus("melody", 0.0, send=0.35, process=lambda x: filt(x, [bq_highpass(150, 0.7)]))
    mx.bus("pulse", -27.0, send=0.2, process=lambda x: filt(x, [bq_highpass(45, 0.7), bq_lowpass(3500, 0.7)]))
    mx.bus("wind", 4.8, send=0.1, process=lambda x: filt(x, [bq_highpass(80, 0.7)]))
    mx.bus("drum", -10.5, send=0.15)
    mx.bus("gong", -16.3, send=0.5)
    build(mx)
    hall = ModFDNReverb(rt60=1.6, rt60_high=0.9, predelay=0.02, size=0.9, mod_depth=8.0, mod_rate=0.6,
                        early_level=0.2, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"saltgrass_causeway: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
