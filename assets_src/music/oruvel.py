"""`oruvel`: Ch1, the Oruvel raft-town (M3-AUD-10; act_outline.md Ch1): a 73.8 s seamless town loop.

Original composition for this project (SPEC §2, §9): the tune, its harmony and every part below were written for this
cue. It evokes a harbour-dance style (a free-reed squeezebox over an oom-pah left hand) and quotes no existing tune,
shanty or folk melody. Oruvel is a raft-town of divers and salvage: Rhen surfaces from a dive to haggle and joke,
Mother Kell sells the divers their oil and wicks, and the whole community is about to die. So the music is lively,
salt-worn and sure of itself, and only its middle section looks away for a moment.

How it stays apart from Haluna (D pentatonic, 6/8, breath flute and interlocking metallophones; haluna_theme.py):
* G mixolydian (the flattened seventh, F natural, is the town's colour; the cadences borrow F# from D major), 4/4 at
  104 BPM with swung eighths: a stepping harbour dance, not a rolling festival;
* the lead is a **free-reed squeezebox** (synthesized here: two reeds tuned a few cents apart, the "wet" beating of a
  salt-worn instrument, a bellows pressure envelope that brightens the reeds as it rises, a dip at each bellows
  turn), with its own left hand: a reed bass on beats 1 and 3, a short reed chord on 2 and 4;
* a **salvage cittern** (paired wire courses through a small bright body) chops the off-beats and takes the tune
  alone in the tag;
* rope and trade: a block-and-tackle knock on 2 and 4 (a wooden sheave), a frame drum on 1 and 3, hand claps when
  the market is fullest, a rope creaking against a cleat, and a ship's bell rung twice at the loop's start (the
  harbour) and once at the B section. Unlike Haluna's tune, this one lands on its home note: a town at home.

Form (bars): 1-4 the raft-town wakes (left hand, block, drum, the ship's bell) | 5-12 A, the tune | 13-20 A', the
cittern's chop and the claps join, the tune ends high | 21-28 B, E minor: the tune drops and slows, longer notes, the
drum thins to the block (the community about to die, for eight bars) | 29-32 the cittern alone with the tune's head,
and a D7 turnaround back into bar 1.

Render:  python3 assets_src/music/oruvel.py   (or tools/audio/render_all.py --only oruvel)
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
from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz,  # noqa: E402
                       rng, smooth_noise)
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(ROOT, "assets_src", "sfx",
                                                                              "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT = os.path.join(ROOT, "assets", "audio", "music", "oruvel.ogg")
SEED = 20261215
TARGET_LUFS = -16.0
BPM = 104.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 32
LOOP_S = BARS * BAR
SWING = 0.62            # where the off-beat eighth falls inside its beat (0.5 = straight)
DOWNBEAT_OFFSET_S = 0.0

# Chords per bar.
CHORDS = (["G", "C", "D", "G"]
          + ["G", "G", "C", "D", "G", "Em", "CD", "G"]
          + ["G", "G", "C", "D", "G", "Em", "CD", "G"]
          + ["Em", "C", "G", "D", "Em", "C", "AmD", "D"]
          + ["G", "C", "GD7", "G"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["A2"] * 8 + ["B"] * 8 + ["T"] * 4
# The left hand: (bass, chord) per chord name; the bass alternates root and fifth.
LH = {"G": ("G2", "D2", "B3 D4 G4"), "C": ("C3", "G2", "C4 E4 G4"), "D": ("D3", "A2", "A3 D4 F#4"),
      "D7": ("D3", "A2", "A3 C4 F#4"), "Em": ("E2", "B2", "B3 E4 G4"), "Am": ("A2", "E2", "A3 C4 E4")}

# The tune, in swung eighths (eight to a bar): (pitch | None, eighths).
TUNE_A = [
    [("D5", 2), ("B4", 1), ("G4", 1), ("A4", 1), ("B4", 1), ("C5", 1), ("D5", 1)],
    [("E5", 1), ("D5", 1), ("B4", 1), ("G4", 1), ("F5", 2), ("D5", 2)],
    [("E5", 2), ("G5", 1), ("E5", 1), ("C5", 2), ("E5", 1), ("G5", 1)],
    [("A5", 3), ("F#5", 1), ("D5", 4)],
    [("G5", 2), ("F5", 1), ("D5", 1), ("B4", 2), ("D5", 1), ("G5", 1)],
    [("E5", 1), ("G5", 1), ("B5", 1), ("G5", 1), ("E5", 2), ("D5", 2)],
    [("C5", 1), ("E5", 1), ("A5", 1), ("G5", 1), ("F#5", 1), ("E5", 1), ("D5", 1), ("C5", 1)],
    [("B4", 2), ("G4", 2), (None, 4)],
]
TUNE_A2_END = [
    [("C5", 1), ("E5", 1), ("G5", 1), ("A5", 1), ("B5", 2), ("A5", 1), ("F5", 1)],
    [("G5", 4), (None, 2), ("D5", 1), ("E5", 1)],
]
# B: lower and slower, in E minor; the only bars where the town looks away.
TUNE_B = [
    [("B4", 3), ("E5", 1), ("G5", 3), ("F#5", 1)],
    [("E5", 4), ("C5", 2), ("D5", 2)],
    [("D5", 3), ("B4", 1), ("D5", 2), ("G5", 2)],
    [("F#5", 6), (None, 2)],
    [("G5", 3), ("F#5", 1), ("E5", 2), ("B4", 2)],
    [("C5", 3), ("D5", 1), ("E5", 2), ("G5", 2)],
    [("A5", 2), ("G5", 1), ("E5", 1), ("D5", 2), ("C5", 1), ("A4", 1)],
    [("A4", 6), (None, 2)],
]
# The tag: the cittern alone with the tune's head, then the turnaround.
TAG = [
    [("D5", 2), ("B4", 1), ("G4", 1), ("A4", 1), ("B4", 1), ("C5", 1), ("D5", 1)],
    [("E5", 1), ("D5", 1), ("C5", 1), ("E5", 1), ("G5", 2), ("E5", 2)],
    [("D5", 2), ("B4", 1), ("A4", 1), ("F#4", 2), ("A4", 1), ("C5", 1)],
    [("B4", 2), (None, 6)],
]


def t_of(bar: int, eighth: float = 0.0) -> float:
    """Start time (s) of swung eighth `eighth` in 1-based `bar` (fractional eighths are straight)."""
    beat, rem = divmod(eighth, 2)
    off = rem * SWING if rem < 1 else SWING + (rem - 1) * (1 - SWING)
    return (bar - 1) * BAR + (beat + off) * BEAT + DOWNBEAT_OFFSET_S


def free_reed(m: float, dur: float, vel: float, seed: int, detune_cents: float = 9.0, bright: float = 1.0,
              release: float = 0.07, attack: float = 0.03, sr: int = SR) -> np.ndarray:
    """A free-reed note (squeezebox): two reeds a few cents apart (the 'wet' tuning beats a couple of times a
    second), a harmonic spectrum shaped by the reed chamber (formants near 1.5 and 3.2 kHz), and a bellows pressure
    envelope: the upper harmonics rise faster than the fundamental as pressure builds, so a soft note is darker,
    not just quieter. A little air noise rides on the pressure. Mono."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int((dur + 6 * release + 0.02) * sr)
    t = np.arange(N) / sr
    wob = 1.0 + 0.025 * smooth_noise(N, 3.0, g, sr)
    P = np.clip(t / attack, 0, 1) ** 1.5 * np.where(t > dur, np.exp(-(t - dur) / release), 1.0) * wob
    P *= vel
    K = int(max(1, min(48, 7500.0 / f0)))
    y = np.zeros(N)
    for j, cents in enumerate((0.0, detune_cents)):
        f = f0 * 2 ** (cents / 1200.0) * (1.0 - 0.0008 * P)     # reeds sag a hair flat under pressure
        ph = 2 * np.pi * np.cumsum(f) / sr + g.uniform(0, 6.28)
        for k in range(1, K + 1):
            fk = k * f0
            a = k ** -1.05 * (1.0 + 2.0 * np.exp(-((fk - 1500.0) / 700.0) ** 2)
                              + 0.8 * np.exp(-((fk - 3200.0) / 900.0) ** 2)) / (1.0 + (fk / 5200.0) ** 4)
            y += (0.8 if j else 1.0) * a * P ** (1.0 + 0.11 * (k - 1) / bright) * np.sin(k * ph)
    air = filt(g.standard_normal(N), [bq_bandpass(2200.0, 0.8)]) * P * 0.015
    out = y + air
    k2 = int(0.005 * sr)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.2 * out


def cittern_body(seed: int, sr: int = SR) -> np.ndarray:
    """A small, bright, thin-topped body (a cittern patched from salvage): higher and drier modes than Haluna's
    lute body, and a stronger click."""
    g = rng(seed)
    t = np.arange(int(0.18 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((190.0, 10, 0.7), (360.0, 12, 0.6), (640.0, 9, 0.5), (1250.0, 7, 0.35), (2900.0, 5, 0.25)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * 0.09
    return ir / np.abs(ir).max()


def cittern(m: float, dur: float, vel: float, seed: int, body: np.ndarray, mute: float = 0.0) -> np.ndarray:
    """A paired wire course: two strings a few cents apart, plucked near the bridge, through the body."""
    a = string_pluck(m, dur, vel, seed=seed, pick_pos=0.08, t60=1.4, mute=mute, B=1.5e-4, max_f=8000.0,
                     release=0.06)
    b = string_pluck(m + 0.04, dur, vel * 0.85, seed=seed + 1, pick_pos=0.09, t60=1.3, mute=mute, B=1.5e-4,
                     max_f=8000.0, release=0.06)
    k = int(0.003 * SR)
    x = np.zeros(len(a) + k)
    x[: len(a)] += a
    x[k: k + len(b)] += b
    return fft_convolve(x, body)[: len(x) + 3000]


def block_knock(g: np.random.Generator, vel: float) -> np.ndarray:
    """A block-and-tackle knock: a wooden sheave against its cheek (a hard, short, hollow modal hit)."""
    base = float(g.uniform(0.95, 1.05))
    return vel * FA.modal([820 * base, 1630 * base, 2650 * base, 3900 * base], [0.035, 0.022, 0.014, 0.008],
                          [1.0, 0.55, 0.3, 0.15], 0.2, g, click=0.6)


def clap(g: np.random.Generator, vel: float) -> np.ndarray:
    """A hand clap: three or four noise bursts a few ms apart (the hands meeting unevenly), then the cupped
    body's short ring."""
    n_ = int(0.18 * SR)
    y = np.zeros(n_)
    t = 0
    for _ in range(int(g.integers(3, 5))):
        b = FA.burst(g, 0.012, [bq_bandpass(float(g.uniform(1000, 1500)), 1.2)], 0.0005, 0.003)
        y[t: t + len(b)] += b * float(g.uniform(0.5, 1.0))
        t += int(float(g.uniform(0.004, 0.009)) * SR)
    tail = FA.burst(g, 0.16, [bq_bandpass(1150.0, 1.5)], 0.001, 0.035)
    y[int(0.01 * SR): int(0.01 * SR) + len(tail)] += 0.5 * tail[: n_ - int(0.01 * SR)]
    return vel * y / (np.abs(y).max() + 1e-12)


def _human(g, t: float) -> float:
    return t + float(g.normal(0.0, 0.005))


def _bar_lists(chord: str) -> list[tuple[str, int]]:
    """A bar's chord(s) and their beats: 'CD' = C for two beats then D; 'GD7' = G then D7; 'AmD' = Am then D."""
    split = {"CD": [("C", 2), ("D", 2)], "GD7": [("G", 2), ("D7", 2)], "AmD": [("Am", 2), ("D", 2)]}
    return split.get(chord, [(chord, 4)])


def add_line(mx: LoopMixer, bus: str, bars: list, start_bar: int, g, play, pan: float) -> None:
    for i, bar_notes in enumerate(bars):
        pos = 0
        for p, d in bar_notes:
            if p is not None:
                t0 = t_of(start_bar + i, pos)
                t1 = t_of(start_bar + i, pos + d) if pos + d < 8 else t_of(start_bar + i + 1, 0)
                mx.add(bus, play(n(p), t1 - t0, pos, d), _human(g, t0), pan=pan)
            pos += d


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = cittern_body(SEED + 5)
    for bar, (chord, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        beat = 0
        for name, beats in _bar_lists(chord):
            root, fifth, triad = LH[name]
            for b in range(beat, beat + beats):
                if b % 2 == 0:            # bass reed on 1 and 3 (root, then the fifth)
                    p = root if (b == 0 or beats == 2) else fifth
                    x = free_reed(n(p), BEAT * 0.8, 0.62 * g.uniform(0.95, 1.03), SEED + 1000 + 10 * bar + b,
                                  detune_cents=6.0, bright=0.8, release=0.05)
                    mx.add("lh", x, _human(g, t_of(bar, 2 * b)), pan=-0.1)
                    if not (sec == "I" and bar < 2):
                        y = bass_note(n(p) - 12 if n(p) > 45 else n(p), BEAT * 0.9, 0.5, seed=SEED + 2000 + 10 * bar + b,
                                      mute=0.35)
                        mx.add("bass", y, t_of(bar, 2 * b) + 0.003, pan=0.0)
                else:                     # the chord stab on 2 and 4
                    for k, p in enumerate(triad.split()):
                        x = free_reed(n(p), BEAT * 0.42, 0.45 * g.uniform(0.95, 1.03),
                                      SEED + 3000 + 100 * bar + 10 * b + k, detune_cents=7.0, bright=0.9,
                                      release=0.04, attack=0.02)
                        mx.add("lh", x, _human(g, t_of(bar, 2 * b)), pan=-0.1 + 0.1 * k)
            # the cittern's off-beat chop (A', B softly, not in the tag where it carries the tune)
            if sec in ("A2", "B"):
                for b in range(beat, beat + beats):
                    for k, p in enumerate(triad.split()):
                        v = (0.34 if sec == "A2" else 0.24) * g.uniform(0.9, 1.05)
                        x = cittern(n(p) + 12 * (k == 0), BEAT * 0.3, v, SEED + 4000 + 100 * bar + 10 * b + k, body,
                                    mute=0.45)
                        mx.add("cittern", x, _human(g, t_of(bar, 2 * b + 1)) + 0.006 * k, pan=0.35)
            beat += beats
        # percussion: frame drum on 1 and 3, the block on 2 and 4, claps in A' with the block
        for b in range(4):
            if b % 2 == 0 and sec != "B":
                mx.add("drum", frame_drum("dum", (0.5 if b == 0 else 0.38) * g.uniform(0.92, 1.05),
                                          variant=bar * 4 + b, seed=SEED + 1), _human(g, t_of(bar, 2 * b)), pan=0.05)
            if b % 2 == 1:
                mx.add("block", block_knock(g, (0.8 if sec != "B" else 0.55) * g.uniform(0.9, 1.05)),
                       _human(g, t_of(bar, 2 * b)), pan=0.3)
            if sec in ("A", "A2", "T") and b == 3:
                mx.add("drum", frame_drum("tek", 0.22 * g.uniform(0.9, 1.05), variant=bar * 4 + 7, seed=SEED + 1),
                       _human(g, t_of(bar, 2 * b + 1)), pan=-0.1)
            if sec == "A2" and b % 2 == 1:
                for who in range(3):      # three people clapping, never quite together
                    mx.add("claps", clap(g, 0.7 * g.uniform(0.7, 1.0)),
                           t_of(bar, 2 * b) + float(g.normal(0.004, 0.008)), pan=-0.5 + 0.5 * who)
    # the tune: the squeezebox's right hand
    def reed_play(m, dur, pos, d):
        accent = 1.08 if pos in (0, 4) else 1.0
        return free_reed(m, dur * 0.92, 0.75 * accent * g.uniform(0.95, 1.03), int(g.integers(1 << 30)),
                         detune_cents=10.0, bright=1.1, release=0.06)

    def reed_soft(m, dur, pos, d):
        return free_reed(m, dur * 0.97, 0.6 * g.uniform(0.96, 1.02), int(g.integers(1 << 30)), detune_cents=10.0,
                         bright=0.8, release=0.12, attack=0.05)

    def cit_play(m, dur, pos, d):
        return cittern(m, dur, 0.6 * g.uniform(0.95, 1.04), int(g.integers(1 << 30)), body)

    add_line(mx, "reed", TUNE_A, 5, g, reed_play, 0.05)
    add_line(mx, "reed", TUNE_A[:6] + TUNE_A2_END, 13, g, reed_play, 0.05)
    add_line(mx, "reed", TUNE_B, 21, g, reed_soft, 0.05)
    add_line(mx, "tag", TAG, 29, g, cit_play, 0.2)
    # the harbour: the ship's bell twice at the loop's start, once at B; a rope creaking against a cleat
    for t, v in ((t_of(1), 0.5), (t_of(1, 1.2), 0.42), (t_of(21), 0.4)):
        mx.add("bell", tower_bell(n("A5"), v, seed=SEED + 600 + int(t * 10), t60=3.5, dark=0.35), t, pan=0.45)
    for bar in (3, 11, 19, 26):
        c = FA.stick_slip(g, float(g.uniform(0.6, 1.0)), 20, 80, [(520, 1.0), (1050, 0.6), (1800, 0.3)], q=7.0)
        mx.add("creak", c, t_of(bar, 3), pan=float(g.uniform(-0.7, -0.3)))


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# squeezebox's tune (0 LU): its left hand -7 LU, the bass -10, the cittern's chop -10, the cittern's tag -2 (it
# carries the tune alone there), the frame drum -9, the block -11, the claps -13, the ship's bell -12, the rope -18.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=5.0)
    mx.bus("reed", 0.0, send=0.22, process=lambda x: filt(x, [bq_highpass(120, 0.7), bq_peak(3200, -1.5, 1.0)]))
    mx.bus("lh", -0.1, send=0.15, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(5000, 0.7)]))
    mx.bus("bass", 8.2, send=0.05, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("cittern", 5.4, send=0.2, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    mx.bus("tag", 10.4, send=0.25, process=lambda x: filt(x, [bq_highpass(120, 0.7)]))
    mx.bus("drum", 9.0, send=0.12)
    mx.bus("block", -3.6, send=0.2)
    mx.bus("claps", -2.8, send=0.3)
    mx.bus("bell", 0.2, send=0.35)
    mx.bus("creak", -5.4, send=0.3, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    build(mx)
    air = ModFDNReverb(rt60=1.1, rt60_high=0.6, predelay=0.015, size=0.8, mod_depth=7.0, mod_rate=0.5,
                       early_level=0.35, lowcut=140.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=air, reverb_return_db=-4.0)
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
        print(f"oruvel: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
