"""`pilgrims_wake`: Ch4, "The Pilgrim's Wake" (M3-AUD-10; act_outline.md Ch4): Asha's living funeral, an 83.5 s loop.

Original composition for this project (SPEC §2, §9): the hymn, the ground bass under it and the dance figures were
written for this cue and are not derived from any existing tune. The descending minor ground (C Bb Ab G) is a
centuries-old lament shape, used here as a bass pattern only, under our own melody.

The scene: Haluna holds a feast for the Cantor who is leaving and will not come back. It is a feast and a funeral at
once, and Rhen, finally understanding that, leaves it angry. The cue plays the two at the same time, at two speeds:
* **the funeral** moves in half notes: a hymn in C minor (the grand piano's top voice first, then the village
  humming it; nobody sings words, only Cantors sing) over an eight-bar descending ground, Cm Bb Ab G | Fm Cm/Eb
  D-half-diminished G7, played by the piano's left hand and struck once a round by a low, dark funeral bell;
* **the feast** moves in sixteenths: frame drums and a bright plucked harp in a 3+3+2 dance, jingles and hand claps
  in the second round, all in the same key, so the feast and the funeral are one harmony and two tempos.
Each round of the hymn ends on B over G7, unresolved; the wrap to bar 1 resolves it to C as the dance comes back in.

How it stays apart from Haluna's own palette (D pentatonic, 6/8, breath flute, interlocking metallophones;
haluna_theme.py) though it is Haluna's feast: C minor, 4/4, no flute and no interlocking bars. The harp's figures
are arpeggios of the ground's chords, not the village tune.

4/4 at 69 BPM (a bar is 3.48 s), 24 bars, three rounds of the ground:
1-8 the feast in full swing, the piano alone with the hymn | 9-16 the village hums the hymn, claps and jingles,
the dance at its fullest | 17-24 the hymn in two octaves (women's and men's hum) with the piano doubling it; the
dance thins from bar 21 and stops in bar 23, leaving the hymn's last two bars bare (the feast forgetting itself for
a moment), until the wrap brings the dance back.

The grand piano runs with a fixed light pedal (a constant `PedalCurve`), so its soundboard bus is time-invariant and
renders in the loop's steady state like any other bus.

Render:  python3 assets_src/music/pilgrims_wake.py   (or tools/audio/render_all.py --only pilgrims_wake)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.drums import frame_drum, jingle  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.grand import PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "pilgrims_wake.ogg")
SEED = 20261216
TARGET_LUFS = -16.0
BPM = 69.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 24
LOOP_S = BARS * BAR
S16 = BEAT / 4
## The file starts a sixteenth before bar 1's downbeat, so the wrap doesn't land on its heaviest attack (the
## dance, the bass and the funeral bell coming back in together after the bare end); the loop is periodic, so
## nothing else changes. The sidecar records it.
DOWNBEAT_OFFSET_S = S16
PEDAL_DEPTH = 0.3       # a light, constant pedal: some sympathetic halo, the dampers still mostly on

# The ground, one chord (or two) per bar: (bass, chord tones for the piano, chord tones for the harp).
GROUND = [
    [("C2", "G3 C4 Eb4", "C5 Eb5 G5 C6")],
    [("Bb1", "F3 Bb3 D4", "Bb4 D5 F5 Bb5")],
    [("Ab1", "Eb3 Ab3 C4", "Ab4 C5 Eb5 Ab5")],
    [("G1", "D3 G3 B3", "G4 B4 D5 G5")],
    [("F1", "F3 Ab3 C4", "F4 Ab4 C5 F5")],
    [("Eb2", "G3 C4 Eb4", "G4 C5 Eb5 G5")],
    [("D2", "F3 Ab3 C4", "D5 F5 Ab5 C6"), ("G1", "F3 G3 B3", "D5 F5 G5 B5")],
    [("G1", "D3 G3 B3", "G4 B4 D5 F5")],
]
# The hymn, (pitch, beats), one list per bar of the ground.
HYMN = [
    [("G4", 2), ("Ab4", 1), ("G4", 1)],
    [("F4", 2), ("D4", 1), ("Eb4", 1)],
    [("C5", 3), ("Bb4", 1)],
    [("G4", 4)],
    [("Ab4", 2), ("G4", 1), ("F4", 1)],
    [("Eb4", 2), ("G4", 1), ("C5", 1)],
    [("D5", 2), ("C5", 1), ("B4", 1)],
    [("B4", 3), (None, 1)],
]
DANCE = [("dum", 0.50), None, None, ("tek", 0.30), None, None, ("dum", 0.36), ("tek", 0.22)]  # 3+3+2 sixteenths
HARP_ORDER = [0, 1, 2, 0, 1, 2, 3, 2]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT + DOWNBEAT_OFFSET_S


def harp_body(seed: int, sr: int = SR) -> np.ndarray:
    """A small harp's soundbox: a long, light box with low air and box modes and little click."""
    g = rng(seed)
    t = np.arange(int(0.3 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((140.0, 14, 0.6), (290.0, 15, 0.5), (520.0, 11, 0.35), (980.0, 8, 0.2), (2100.0, 5, 0.1)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * 0.06
    return ir / np.abs(ir).max()


def _piano_jobs(notes: list[dict], seed: int) -> list:
    pedal = PedalCurve(np.array([0.0, 1.0e6]), np.array([PEDAL_DEPTH, PEDAL_DEPTH]))
    return [(grand_note, dict(m=nt["m"], vel=nt["vel"], key_up=nt["key_up"], seed=seed + 7919 * k, t_abs=nt["t0"],
                              pedal=pedal)) for k, nt in enumerate(notes)]


def _chords_of(bar: int) -> list[tuple[float, float, tuple[str, str, str]]]:
    """[(start beat, beats, (bass, piano chord, harp chord))] for 1-based loop bar `bar`."""
    row = GROUND[(bar - 1) % 8]
    if len(row) == 1:
        return [(0.0, 4.0, row[0])]
    return [(0.0, 2.0, row[0]), (2.0, 2.0, row[1])]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = harp_body(SEED + 5)
    ground_notes, mel_notes = [], []
    for bar in range(1, BARS + 1):
        rnd = (bar - 1) // 8 + 1
        for b0, beats, (bass, chord, harp) in _chords_of(bar):
            t0 = t_of(bar, b0)
            # the piano's left hand: the bass in octaves, the chord on the half notes
            for k, m in enumerate((n(bass), n(bass) + 12)):
                ground_notes.append(dict(m=m, vel=(0.42 if k == 0 else 0.34) * g.uniform(0.95, 1.04),
                                         t0=t0 + float(g.normal(0, 0.004)), key_up=beats * BEAT * 0.97))
            for half in np.arange(0.0, beats, 2.0):
                for k, p in enumerate(chord.split()):
                    ground_notes.append(dict(m=n(p), vel=0.26 * g.uniform(0.94, 1.05),
                                             t0=t_of(bar, b0 + half) + 0.012 * k + float(g.normal(0, 0.004)),
                                             key_up=2 * BEAT * 0.95))
            # the feast: the harp's 3+3+2 figure in sixteenths, thinning in round 3
            if rnd < 3 or bar <= 20 or (bar <= 22 and b0 == 0.0):
                tones = harp.split()
                for s in range(int(beats * 4)):
                    if rnd == 3 and bar >= 21 and s % 2:
                        continue
                    p = tones[HARP_ORDER[s % 8]]
                    acc = 1.15 if s % 8 in (0, 3, 6) else 1.0
                    v = (0.40 if rnd == 2 else 0.34) * acc * g.uniform(0.9, 1.05)
                    x = string_pluck(n(p), S16 * 2.5, v, seed=SEED + 10000 + 100 * bar + 10 * int(b0) + s,
                                     pick_pos=0.3, t60=2.4, max_f=6000.0, release=0.2)
                    mx.add("harp", fft_convolve(x, body)[: len(x) + 4000],
                           t_of(bar, b0) + s * S16 + float(g.normal(0, 0.004)), pan=0.35)
        # the feast's drums (stopping at bar 23), jingles and claps in round 2
        if bar <= 22:
            for s, hit in enumerate(DANCE * 2):
                if hit is None:
                    continue
                stroke, v = hit
                if bar >= 21 and stroke == "tek":
                    continue
                mx.add("drum", frame_drum(stroke, v * g.uniform(0.9, 1.06), variant=bar * 16 + s, seed=SEED + 1),
                       t_of(bar) + s * S16 + float(g.normal(0, 0.004)), pan=-0.15 if stroke == "tek" else 0.05)
        if rnd == 2:
            for s in range(16):
                if s % 8 in (0, 3, 6):
                    mx.add("drum", jingle(0.3 if s % 8 == 0 else 0.2, variant=bar * 16 + s, open_=(s == 0),
                                          seed=SEED + 2), t_of(bar) + s * S16, pan=0.5)
                if s % 8 in (3, 6):
                    for who in range(3):
                        mx.add("claps", _clap(g, 0.7 * g.uniform(0.7, 1.0)),
                               t_of(bar) + s * S16 + float(g.normal(0.004, 0.007)), pan=-0.6 + 0.6 * who)
    # the hymn: the piano's top voice in round 1, doubling the hum an octave up in round 3
    for rnd, octave, vel in ((1, 0, 0.5), (3, 12, 0.36)):
        for i, bar_notes in enumerate(HYMN):
            pos = 0.0
            for p, beats in bar_notes:
                if p is not None:
                    mel_notes.append(dict(m=n(p) + octave, vel=vel * g.uniform(0.96, 1.03),
                                          t0=t_of(8 * (rnd - 1) + i + 1, pos) + float(g.normal(0, 0.004)),
                                          key_up=beats * BEAT * 1.02))
                pos += beats
    for bus, notes, seed in (("piano", ground_notes, SEED + 20), ("piano_mel", mel_notes, SEED + 30)):
        for nt, x in zip(notes, render_jobs(_piano_jobs(notes, seed))):
            mx.add(bus, x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    # the village hums the hymn: women at pitch in rounds 2 and 3, men an octave down in round 3
    line = []
    for bar_notes in HYMN:
        for p, beats in bar_notes:
            if p is None:
                line[-1] = (line[-1][0], line[-1][1] + beats * BEAT * 0.4)
                continue
            line.append((n(p), beats * BEAT))
    for rnd, octave, register, voices in ((2, 0, "high", 12), (3, 0, "high", 12), (3, -12, "low", 10)):
        h = hum_ensemble(line, voices=voices, seed=SEED + 300 + 10 * rnd + (octave != 0), register=register,
                         spread=0.7, breath_every=(7.0, 12.0))
        mx.add("hum", h * (0.8 if octave else 1.0), t_of(8 * (rnd - 1) + 1) - 0.08)
    # the funeral bell once a round, kettle gongs on the half-rounds, a low gong under the bare end
    for rnd in range(3):
        mx.add("bell", tower_bell(n("C3"), 0.6, seed=SEED + 600 + rnd, t60=7.0, dark=0.55), t_of(8 * rnd + 1),
               pan=-0.2)
        mx.add("gong", kettle_gong(n("G3"), 0.3, seed=SEED + 700 + rnd, t60=2.4), t_of(8 * rnd + 4), pan=0.3)
        mx.add("gong", kettle_gong(n("C4"), 0.26, seed=SEED + 710 + rnd, t60=2.4), t_of(8 * rnd + 8), pan=0.3)
    mx.add("gong", large_gong(n("C2"), 0.3, seed=SEED + 800, t60=7.0), t_of(23), pan=-0.1)


def _clap(g: np.random.Generator, vel: float) -> np.ndarray:
    """A hand clap: three or four noise bursts a few ms apart, then the cupped hands' short ring."""
    n_ = int(0.18 * SR)
    y = np.zeros(n_)
    t = 0
    for _ in range(int(g.integers(3, 5))):
        m = int(0.012 * SR)
        tt = np.arange(m) / SR
        b = filt(g.standard_normal(m), [bq_bandpass(float(g.uniform(1000, 1500)), 1.2)]) * np.exp(-tt / 0.003)
        y[t: t + m] += b * float(g.uniform(0.5, 1.0))
        t += int(float(g.uniform(0.004, 0.009)) * SR)
    m = int(0.16 * SR)
    tt = np.arange(m) / SR
    tail = filt(g.standard_normal(m), [bq_bandpass(1150.0, 1.5)]) * np.exp(-tt / 0.035)
    s = int(0.01 * SR)
    y[s: s + m] += 0.5 * tail[: n_ - s]
    return vel * y / (np.abs(y).max() + 1e-12)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# hymn (0 LU; the piano's top voice in round 1 and the hum in rounds 2-3 both carry it): the piano's ground -4 LU
# (the funeral is as present as the feast), the harp's dance -7, the drums -7, the claps -12, the funeral bell -11,
# the gongs -14. (The grand piano model's raw level here is about 20 dB under the hum, hence its gain.)
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    mx.bus("piano_mel", 20.6, send=0.25, process=PianoBody(PedalCurve(np.array([0.0, 1.0e6]),
                                                                     np.array([PEDAL_DEPTH, PEDAL_DEPTH]))))
    mx.bus("piano", 15.5, send=0.25, process=PianoBody(PedalCurve(np.array([0.0, 1.0e6]),
                                                                 np.array([PEDAL_DEPTH, PEDAL_DEPTH]))))
    # M3-AUD-864: the Act I listening report found this the muddiest zone loop (250-800 Hz 13.5 dB over mid and
    # presence; the set's median is +5): the hum's chest and the bell's 250 Hz boost stacked there. The hum gives
    # 3 dB at 380 Hz and the bell keeps its tone without the boost.
    mx.bus("hum", 0.0, send=0.35, process=lambda x: filt(x, [bq_highpass(90, 0.7), bq_peak(380, -3.0, 0.9)]))
    mx.bus("harp", -9.3, send=0.3, process=lambda x: filt(x, [bq_highpass(180, 0.7), bq_lowpass(7000, 0.7)]))
    mx.bus("drum", -4.2, send=0.18)
    mx.bus("claps", -16.3, send=0.3)
    mx.bus("bell", -14.7, send=0.4, process=lambda x: filt(x, [bq_lowpass(3000, 0.7), bq_peak(250, 0.0, 1.0)]))
    mx.bus("gong", -12.2, send=0.4)
    build(mx)
    hall = ModFDNReverb(rt60=2.2, rt60_high=1.0, predelay=0.02, size=1.0, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.3, lowcut=110.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"pilgrims_wake: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
