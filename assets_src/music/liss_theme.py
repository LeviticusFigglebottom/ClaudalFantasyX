"""`liss_theme`: Liss Varrow's theme, its first statement (M3-AUD-821; act1_ch06.md B06-B07, §6), a 61.1 s loop.

Original composition for this project (SPEC §2, §9). The tune, the tide-wheel's figure and the harmony were written
for Liss and are not derived from any existing tune. The brief: "Character theme, first statement. Plucked strings
over a tide-wheel ostinato that's a little off the beat, bright and guarded." Liss is a Saltwright girl who has just
run out of a burning hull with a crate of bound parts: quick, practical, sharp-tongued, and she gives nothing away
(ch06_after_barge.dlg and ch06_liss_lantern.dlg, by the burning tide-wheel).

D major, 4/4 at 110 BPM (a bar is 2.18 s), 28 bars. **Bright:** a major key, the tune high and quick, crisply
plucked. **Guarded:** the tune never lands on D where a phrase ends; its phrases close on E, on A, on the C major
chord (the flattened seventh, a door pulled to), and the one approach to D (bar 15) steps aside to B. **Off the
beat:** the tide-wheel's paddles knock on a cycle of seven eighth notes against the bar's eight, so its accent walks
one eighth earlier every bar and only meets the downbeat again every seven bars (four times a loop); and every knock
lands a little late, as a wheel turned by the tide does.

Ensemble (all synthesized; no samples):
* the tune: a small, bright wright-built cittern (plucked strings through a small, stiff body), close to the ear;
* the tide-wheel: seven tuned wooden paddles knocking (D4 A3 F#4 A3 E4 A3 B3), an axle's thunk and a slop of water
  on each turn;
* a plucked low string on the roots (beat 1) and fifths (beat 3), and soft plucked dyads on beats 2 and 4.

Form (bars): 1-2 the wheel and the low string | 3-6 A (closes on E) | 7-10 A' (closes on A) | 11-18 B, higher, the C
major bar, the step aside from D, closing on A | 19-22 the wheel and only fragments of the tune (D C G A) | 23-26 A an
octave up, lighter | 27-28 the wheel and the low string (G A), back to bar 1's D.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file; the file starts a sixteenth before bar 1 (DOWNBEAT_OFFSET_S).

Render:  python3 assets_src/music/liss_theme.py   (or tools/audio/render_all.py --only liss_theme)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, db_to_lin, fft_convolve, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__),
                                                                           "act2_voices.py"))
AV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AV)

OUT = os.path.join(ROOT, "assets", "audio", "music", "liss_theme.ogg")
SEED = 20261826
TARGET_LUFS = -16.0
BPM = 110.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
E8 = BEAT / 2
BARS = 28
LOOP_S = BARS * BAR
## the file starts a sixteenth before bar 1's downbeat (render_all's seam flux gate)
DOWNBEAT_OFFSET_S = BEAT / 4
WHEEL = ["D4", "A3", "F#4", "A3", "E4", "A3", "B3"]     # the paddles, one an eighth
WHEEL_LAG_S = 0.032                                      # every knock a little late

CHORDS = (["D", "D"]
          + ["D", "A", "G", "A"] + ["D", "D/F#", "G", "A"]
          + ["D", "Bm", "G", "C", "D/F#", "G", "Bm", "A"]
          + ["D", "C", "G", "A"]
          + ["D", "A", "G", "A"]
          + ["G", "A"])
## (bass on 1, bass on 3, the dyad on 2 and 4)
VOICING = {"D": ("D2", "A2", "F#4 A4"), "A": ("A1", "E2", "C#4 E4"), "G": ("G1", "D2", "B3 D4"),
           "Bm": ("B1", "F#2", "D4 F#4"), "C": ("C2", "G2", "C4 E4"), "D/F#": ("F#1", "A1", "D4 A4")}

## the tune, (pitch, beats) per bar; None is a rest
T_A = [[("A4", .5), ("B4", .5), ("D5", 1), ("B4", .5), ("A4", .5), ("F#4", 1)],
       [("E4", 1.5), ("F#4", .5), ("A4", 2)],
       [("B4", .5), ("D5", .5), ("E5", 1), ("D5", .5), ("B4", .5), ("A4", .5), ("B4", .5)],
       [("E4", 3), (None, 1)]]
T_A2 = [T_A[0],
        [("E4", 1), ("F#4", .5), ("A4", .5), ("D5", 1.5), ("C#5", .5)],
        [("B4", 1), ("A4", .5), ("F#4", .5), ("G4", 1), ("F#4", 1)],
        [("E4", 2), ("A4", 2)]]
T_B = [[("F#5", 1), ("E5", .5), ("D5", .5), ("E5", 2)],
       [("A5", 1), ("F#5", .5), ("E5", .5), ("D5", 1), ("B4", 1)],
       [("D5", 1.5), ("E5", .5), ("F#5", 1), ("A5", 1)],
       [("G5", 2), ("E5", 2)],
       [("F#5", 1), ("E5", .5), ("D5", .5), ("B4", 1), ("A4", 1)],
       [("B4", .5), ("D5", .5), ("E5", 1), ("D5", .5), ("B4", .5), ("A4", 1)],
       [("F#4", 1), ("A4", 1), ("B4", 2)],
       [("A4", 4)]]
FRAGMENTS = [[("A4", .5), ("B4", .5), ("D5", 1), (None, 2)],
             [(None, 2), ("E5", .5), ("D5", .5), ("C5", 1)],
             [("B4", .5), ("D5", .5), ("E5", 1), (None, 2)],
             [(None, 2), ("C#5", 1), ("E5", 1)]]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT + DOWNBEAT_OFFSET_S


def cittern_body(seed: int) -> np.ndarray:
    """A small, stiff, wright-built body: bright modes, little low end."""
    return AV.body_ir([(280.0, 8.0, 0.7), (560.0, 7.0, 0.6), (1150.0, 6.0, 0.5), (2300.0, 5.0, 0.4),
                       (4100.0, 4.0, 0.25)], seed, length=0.15)


def paddle(m: float, vel: float, seed: int) -> np.ndarray:
    """A wooden paddle knocking in the wheel: a short, pitched wood tone (three bar modes) and a click. Mono."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int(0.35 * SR)
    t = np.arange(N) / SR
    y = np.zeros(N)
    for r, a, t60 in ((1.0, 1.0, 0.20), (2.76, 0.35, 0.08), (5.40, 0.15, 0.035)):
        y += a * np.exp(-6.91 * t / t60) * np.sin(2 * np.pi * f0 * r * t + g.uniform(0, 6.28))
    k = int(0.003 * SR)
    y[:k] += 0.6 * filt(g.standard_normal(k), [bq_highpass(2000, 0.7)]) * np.linspace(1, 0, k)
    return vel * y * np.clip(t / 0.0005, 0, 1)


def axle(g) -> np.ndarray:
    """The wheel's turn: a low wooden thunk of the axle and a slop of water off the paddles. Mono."""
    N = int(0.8 * SR)
    t = np.arange(N) / SR
    y = np.sin(2 * np.pi * 78.0 * t) * np.exp(-t / 0.07)
    y += 0.3 * filt(g.standard_normal(N), [bq_lowpass(500, 0.7)]) * np.exp(-t / 0.03)
    for _ in range(6):
        b = bubble(float(g.uniform(2.5, 7.0)), amp=float(g.uniform(0.1, 0.3)), rise=0.08)
        s = int(float(g.uniform(0.05, 0.45)) * SR)
        e = min(N, s + len(b))
        y[s:e] += b[: e - s]
    return y


def add_line(mx: LoopMixer, body: np.ndarray, bars: list, start_bar: int, seed: int, vel: float,
             octave: int = 0) -> None:
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = 0.0
        for p, beats in bar:
            if p is not None:
                m = n(p) + 12 * octave
                d = beats * BEAT
                v = vel * g.uniform(0.92, 1.05) * (1.08 if pos in (0.0, 2.0) else 1.0)
                x = string_pluck(m, d * 0.92, v, seed=seed + 100 * i + int(pos * 4), pick_pos=0.08, t60=1.7,
                                 B=4e-5, max_f=9000.0, release=0.09)
                mx.add("tune", fft_convolve(x, body)[: len(x) + 3000], t_of(start_bar + i, pos)
                       + float(g.normal(0, 0.005)), pan=0.12)
            pos += beats


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = cittern_body(SEED + 5)
    # the tide-wheel: a knock every eighth on a seven-paddle cycle, a little late; the axle on every turn
    for e in range(BARS * 8):
        k = e % len(WHEEL)
        lag = WHEEL_LAG_S + 0.010 * np.sin(2 * np.pi * e / (BARS * 8) * 3)       # the tide pushes and slackens
        v = (0.62 if k == 0 else 0.42) * g.uniform(0.88, 1.06)
        mx.add("wheel", paddle(n(WHEEL[k]), v, SEED + 2000 + 13 * k + (e % 3)), e * E8 + DOWNBEAT_OFFSET_S + lag,
               pan=0.35 - 0.1 * k)
        if k == 0:
            mx.add("axle", axle(rng(SEED + 3000 + e)), e * E8 + DOWNBEAT_OFFSET_S + lag + 0.01, pan=0.4)
    # the low string and the dyads
    for bar, ch in enumerate(CHORDS, start=1):
        b1, b3, dyad = VOICING[ch]
        for beat, p, v in ((0, b1, 0.62), (2, b3, 0.48)):
            x = string_pluck(n(p), 1.8 * BEAT, v * g.uniform(0.94, 1.04), seed=SEED + 400 + 4 * bar + beat,
                             pick_pos=0.16, t60=2.2, B=8e-5, max_f=3000.0, release=0.12)
            mx.add("low", x, t_of(bar, beat) + float(g.normal(0, 0.004)), pan=-0.1)
        if 3 <= bar <= 26:
            for beat in (1, 3):
                for j, p in enumerate(dyad.split()):
                    x = string_pluck(n(p), 0.4 * BEAT, 0.38 * g.uniform(0.9, 1.05), seed=SEED + 600 + 8 * bar
                                     + 2 * beat + j, pick_pos=0.12, t60=0.8, max_f=6000.0, release=0.05)
                    mx.add("dyad", fft_convolve(x, body)[: len(x) + 3000], t_of(bar, beat) + 0.008 * j
                           + float(g.normal(0, 0.004)), pan=-0.35)
    add_line(mx, body, T_A, 3, SEED + 700, 0.62)
    add_line(mx, body, T_A2, 7, SEED + 800, 0.62)
    add_line(mx, body, T_B, 11, SEED + 900, 0.66)
    add_line(mx, body, FRAGMENTS, 19, SEED + 1000, 0.55)
    add_line(mx, body, T_A, 23, SEED + 1100, 0.48, octave=1)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# tune (0 LU, over bars 3-18 where it plays throughout): the wheel -6 (the ostinato is the other half of the theme),
# the axle -14, the low string -8, the dyads -11; the wheel, the axle and the low string measured over the loop.
GAINS = {"tune": 0.0, "wheel": -10.5, "axle": -23.5, "low": -4.8, "dyad": -14.9}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=6.0)
    mx.bus("tune", GAINS["tune"], send=0.22, process=lambda x: filt(x, [bq_highpass(180, 0.7),
                                                                        bq_peak(3200, 1.0, 1.0)]))
    mx.bus("wheel", GAINS["wheel"], send=0.18, process=lambda x: filt(x, [bq_highpass(120, 0.7),
                                                                          bq_lowpass(6000, 0.7)]))
    mx.bus("axle", GAINS["axle"], send=0.15, process=lambda x: filt(x, [bq_highpass(40, 0.7)]))
    mx.bus("low", GAINS["low"], send=0.12, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1600, 0.7)]))
    mx.bus("dyad", GAINS["dyad"], send=0.2, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    build(mx)
    yard = ModFDNReverb(rt60=1.4, rt60_high=0.6, predelay=0.015, size=0.85, mod_depth=6.0, mod_rate=0.5,
                        early_level=0.2, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=yard, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = _bus_stats(mx)
        stats["limiter"] = rep
    if verbose:
        print(f"liss_theme: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
    return m


def _bus_stats(mx: LoopMixer) -> dict:
    out = {}
    a, e = int(t_of(3) * SR), int(t_of(19) * SR)
    for b in mx.buses.values():
        x = db_to_lin(b.gain_db) * (b.process(b.loop) if b.process else b.loop)
        out[b.name] = integrated_lufs(x[a:e] if b.name in ("tune", "dyad") else x)
    return out


if __name__ == "__main__":
    st: dict = {}
    render(stats=st)
    print("  buses", {k: round(v, 1) for k, v in st["bus_lufs"].items()})
