"""`brightwater_ferry`: the dawn ferry across Brightwater strait (M3-AUD-11; act_outline Ch4, zone
`ch04/brightwater_ferry`): a 76.2 s seamless field loop.

Original composition for this project (SPEC §2, §9). The flute's tune, the rigging figure, Ysolde's two-note
figure and the harmony were written for this crossing and are not derived from any existing tune. The brief: a
dawn crossing of open water, the first time the pilgrimage leaves the coast; Ysolde boards by Order appointment,
cold and correct; mid-strait the ferry comes on a trader lost in the Rising, drifting with its sails still set and
nobody at the helm. The cue is the deck: wide and lit, with the drowned hull in the middle of it.

E-flat Lydian (Eb F G A Bb C D: the raised fourth, A natural, is the dawn's colour; the F major chord over an Eb
pedal is its sound), 9/8 at 52 dotted quarters (a bar is 3.46 s, one roll of the hull), 22 bars. The derelict
passage darkens to the parallel minor's chords (Cb major and Ab minor, the Gb that Lydian never has).

Ensemble (all synthesized; no samples):
* the sea: a band of noise that swells once a bar (the hull's roll), seamless across the wrap;
* the hull: a low string pad on the roots, swelling into each bar;
* the rigging: plucked strings through a small wooden body, rolling in eighths (3+3+3);
* breath flute, high (Bb4-C6): the tune;
* Ysolde: a hand-damped metallophone striking two even notes a bar, against the 9/8's three: duple, unswung,
  exactly on the grid (cold and correct). It is the only part with no human timing;
* the derelict: a ship's bell heard over water (dark), rung off the beat by the roll, twice;
* a frame drum knocking on each downbeat, like the hull on the swell.

Form: 1-2 the sea and the rigging | 3-10 the tune (A) | 11-14 Ysolde's figure; the flute answers (B) | 15-18 the
derelict: Cb and Ab minor, the bell, one long flute note on Gb then Eb | 19-22 the tune again (A'), ending on a
suspended Bb that the wrap resolves to bar 1's Eb.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file.

Render:  python3 assets_src/music/brightwater_ferry.py   (or tools/audio/render_all.py --only brightwater_ferry)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("haluna_village", os.path.join(os.path.dirname(__file__),
                                                                               "haluna_village.py"))
HV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HV)

OUT = os.path.join(ROOT, "assets", "audio", "music", "brightwater_ferry.ogg")
SEED = 20261241
TARGET_LUFS = -16.0
BPM = 52.0                       # dotted quarters
BEAT = 60.0 / BPM
E8 = BEAT / 3                    # an eighth
BAR = 3 * BEAT
BARS = 22
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## The file starts this long before bar 1's downbeat (0 = on it); see render_all's seam flux gate.
DOWNBEAT_OFFSET_S = 0.0

CHORDS = (["Eb", "Eb"] + ["Eb", "F/Eb", "Eb", "Cm7", "Gm", "F", "Bbsus", "Eb"] + ["Gm", "Cm", "F", "Bb"]
          + ["Cb", "Abm", "Cb", "Bb"] + ["Eb", "F/Eb", "Cm", "Bbsus"])
PAD = {"Eb": "Eb2 Bb2 G3", "F/Eb": "Eb2 C3 A3", "Cm7": "C2 G2 Eb3 Bb3", "Gm": "G1 D2 Bb2", "F": "F1 C2 A2",
       "Bbsus": "Bb1 F2 Eb3", "Bb": "Bb1 F2 D3", "Cm": "C2 G2 Eb3", "Cb": "B1 F#2 D#3", "Abm": "Ab1 Eb2 B2"}
RIG = {"Eb": "Eb3 Bb3 Eb4 F4", "F/Eb": "Eb3 C4 F4 A4", "Cm7": "C3 G3 Bb3 Eb4", "Gm": "G3 D4 G4 A4",
       "F": "F3 C4 F4 G4", "Bbsus": "Bb2 F3 Bb3 Eb4", "Bb": "Bb2 F3 Bb3 D4", "Cm": "C3 G3 C4 D4",
       "Cb": "B2 F#3 B3 D#4", "Abm": "Ab2 Eb3 Ab3 B3"}
ROLL = (0, 1, 2, 1, 2, 3, 0, 2, 1)       # rigging: indices into RIG per eighth

## the tune, (pitch, eighths) per bar (9 eighths a bar); None is a rest
TUNE_A = [[("Bb4", 3), ("Eb5", 2), ("F5", 1), ("G5", 3)], [("A5", 6), ("G5", 3)], [("F5", 3), ("Eb5", 3), ("Bb4", 3)],
          [("C5", 6), (None, 3)], [("D5", 3), ("F5", 2), ("G5", 1), ("Bb5", 3)], [("A5", 3), ("C6", 3), ("A5", 3)],
          [("G5", 4), ("F5", 2), ("Eb5", 3)], [("Eb5", 6), (None, 3)]]
TUNE_B = [[(None, 3), ("D5", 3), ("G5", 3)], [("Eb5", 6), ("D5", 1), ("C5", 2)], [("C5", 3), ("F5", 3), ("A5", 3)],
          [("Bb5", 4), ("A5", 2), ("F5", 3)]]
DRIFT = [[(None, 9)], [(None, 3), ("Gb5", 6)], [("Eb5", 9)], [(None, 3), ("D5", 6)]]
TUNE_A2 = [[("Bb4", 3), ("Eb5", 2), ("F5", 1), ("G5", 3)], [("A5", 6), ("Bb5", 3)], [("G5", 3), ("F5", 3), ("Eb5", 3)],
           [("F5", 6), (None, 3)]]
## Ysolde: two even strikes a bar (at 0 and 4.5 eighths), bars 11-14
YSOLDE = [("D6", "Bb5"), ("C6", "G5"), ("C6", "A5"), ("D6", "F5")]


def t_of(bar: int, eighth: float = 0.0) -> float:
    return (bar - 1) * BAR + eighth * E8 + DOWNBEAT_OFFSET_S


def sea(sr: int = SR) -> np.ndarray:
    """One loop of open water: two noise bands swelling once a bar (the roll) under a slower tide. Rendered k samples
    longer than the loop and the extra folded into the start with a crossfade, so the wrap is seamless."""
    g = rng(SEED + 3)
    N = int(round(LOOP_S * sr))
    k = int(0.5 * sr)
    t = np.arange(N + k) / sr
    out = np.zeros((N + k, 2))
    for ch in range(2):
        lo = filt(g.standard_normal(N + k), [bq_bandpass(260.0, 0.6), bq_lowpass(900, 0.6)])
        hi = filt(g.standard_normal(N + k), [bq_bandpass(2400.0, 0.9)])
        roll = 0.45 + 0.55 * np.sin(np.pi * (t - DOWNBEAT_OFFSET_S) / BAR + 0.5 + 0.35 * ch) ** 2
        tide = 0.75 + 0.25 * np.sin(2 * np.pi * 2 * t / LOOP_S + ch)
        out[:, ch] = (lo + 0.18 * hi * roll ** 2) * roll * tide
    w = np.linspace(0, 1, k)[:, None]
    loop = out[:N].copy()
    loop[:k] = out[:k] * w + out[N:] * (1 - w)
    return loop * 0.05


def add_line(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, pan: float = -0.1) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = 0.0
        for p, eighths in bar:
            d = eighths * E8
            if p is None:
                pos += eighths
                first = True
                continue
            v = vel * g.uniform(0.94, 1.04) * (1.05 if eighths >= 6 else 1.0)
            x = breath_flute(n(p), d * 0.95 + 0.03, v, seed=seed + 31 * i + int(pos), breath=0.38,
                             scoop_cents=30.0 if first else 10.0, vib_cents=11.0 if eighths >= 3 else 3.0,
                             vib_rate=4.8, swell=0.3 if eighths >= 6 else 0.0, attack=0.08 if first else 0.04,
                             release=0.4, beta=0.55)
            mx.add("flute", x, t_of(start_bar + i, pos) - FLUTE_PRE + float(g.normal(0, 0.005)), pan=pan)
            pos += eighths
            first = False


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = HV.lute_body(SEED + 5)
    mx.add("sea", sea(), 0.0)
    for bar, ch in enumerate(CHORDS, start=1):
        drift = 15 <= bar <= 18
        # the hull: the pad swells into each bar
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.9, 0.55 if drift else 0.5, seed=SEED + 200 + bar,
                      attack=1.1, release=1.6, spread_cents=7.0 if not drift else 11.0)
        mx.add("pad", x, t_of(bar) - 0.25)
        # the rigging
        tones = [n(p) for p in RIG[ch].split()]
        for e, idx in enumerate(ROLL):
            if drift and e % 3:
                continue
            if bar == 1 and e < 3:
                continue
            v = (0.48 if e == 0 else 0.40 if e % 3 == 0 else 0.30) * g.uniform(0.9, 1.06)
            x = string_pluck(tones[idx], E8 * (2.2 if drift else 1.3), v, seed=SEED + 1000 + 10 * bar + e,
                             pick_pos=0.16, t60=2.4, mute=0.15 if not drift else 0.3, max_f=5000.0, release=0.08)
            mx.add("rig", fft_convolve(x, body)[: len(x) + 3000],
                   t_of(bar, e + (0.08 if e % 3 == 1 else 0.0)) + float(g.normal(0, 0.005)),
                   pan=0.30 if e % 2 else 0.18)
        # the hull's knock on the swell
        knock = frame_drum("dum", (0.30 if not drift else 0.24) * g.uniform(0.92, 1.06), variant=bar, seed=SEED + 1,
                           size=1.2)
        mx.add("drum", knock, t_of(bar) + float(g.normal(0, 0.004)), pan=-0.05)
        if not drift and bar > 2:
            mx.add("drum", frame_drum("ghost", 0.10 * g.uniform(0.9, 1.1), variant=bar + 3, seed=SEED + 1),
                   t_of(bar, 6) + float(g.normal(0, 0.006)), pan=-0.12)
    # the tune
    add_line(mx, TUNE_A, 3, SEED + 600, 0.52)
    add_line(mx, TUNE_B, 11, SEED + 700, 0.48)
    add_line(mx, DRIFT, 15, SEED + 800, 0.42, pan=-0.2)
    add_line(mx, TUNE_A2, 19, SEED + 900, 0.52)
    # Ysolde: exact, damped, two to the bar
    for i, pair in enumerate(YSOLDE):
        for k, p in enumerate(pair):
            x = metallophone_note(n(p), 0.50 if k == 0 else 0.42, seed=SEED + 3000 + 2 * i + k, decay=2.8,
                                  hardness=0.65, ombak_hz=0.0, damp_at=E8 * 3.6, pair=False)
            mx.add("ysolde", x, t_of(11 + i, 4.5 * k), pan=0.35)
    # the derelict's bell, rung by the roll (off the beat), far away
    for bar, eighth, v in ((15, 4.0, 0.42), (17, 7.0, 0.34)):
        mx.add("bell", tower_bell(n("Bb3"), v, seed=SEED + 4000 + bar, t60=7.0, dark=0.75), t_of(bar, eighth), pan=-0.4)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# flute (0 LU): the pad -8, the rigging -9, the sea -9 (the scene), Ysolde -5 (measured where she plays: bars
# 11-14), the bell -9, the drum -13.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=9.0)
    mx.bus("flute", 0.0, send=0.35, process=lambda x: filt(x, [bq_highpass(180, 0.7), bq_peak(2200, 1.5, 1.0),
                                                                 bq_lowpass(7500, 0.7)]))
    mx.bus("pad", 4.0, send=0.30, process=lambda x: string_body(x, cutoff=1600.0))
    mx.bus("rig", -16.2, send=0.22, process=lambda x: filt(x, [bq_highpass(110, 0.7), bq_lowpass(4500, 0.7)]))
    mx.bus("sea", 12.0, send=0.08, process=lambda x: filt(x, [bq_highpass(70, 0.7)]))
    mx.bus("ysolde", 3.4, send=0.25, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("bell", -8.2, send=0.55, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
    mx.bus("drum", -2.3, send=0.2, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    build(mx)
    deck = ModFDNReverb(rt60=2.4, rt60_high=1.1, predelay=0.03, size=1.0, mod_depth=9.0, mod_rate=0.45,
                        early_level=0.12, lowcut=130.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=deck, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 3,
                       extra={"loop_bars": BARS, "meter": "9/8", "downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"brightwater_ferry: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
