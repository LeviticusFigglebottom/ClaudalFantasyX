"""`terraces_of_ash`: Pemakar and Lanternfall (M3-AUD-04; act_outline Ch5, bible §5.2): an 80 s seamless area loop.

Original composition for this project (SPEC §2, §9). The melody, the bass, the lantern figures and the gong cycle
below were written for this area and are not derived from any existing tune. The brief: Pemakar's Lanternfall, a
thousand leaf-boats floated down the terrace channels at night among the graves, so the whole mountain becomes a
waterfall of small fires (pillar 2, beauty in decline); above it Ashcrown, a stair-mountain of dark volcanic stone
with copper veins and an ash plume. A festival held in a cemetery: it should be lovely and grave at once, slow, and
lit from many small points.

F with a five-note "in"-type scale (F Gb Bb C Db: the flat second and flat sixth give it the grave colour), 3/4 at
72 BPM (a bar is 2.5 s), 32 bars. A different palette from every earlier cue: no flute and no interlocking bars.

Ensemble (all synthesized; no samples):
* a plucked zither (synth.electric.string_pluck, a long bright string through a long box body): the tune, with a
  grace note into each phrase and a soft re-strike on its long notes; a low zither string on the roots;
* the lanterns: soft, high bars (a light-mallet metallophone with a slow shimmer) in short falling runs of the
  scale, scattered left and right like small fires going over the terrace lips; more of them in the tail;
* the channels: tuned bubbles (Minnaert, r = 3.26 / f) at scale pitches, irregular and quiet;
* the mourners: women humming the tune an octave down through B and A' (the Order hums; only Cantors sing);
* copper: a kettle gong on each bar's downbeat, a large gong every eight bars (the stair-mountain's cycle); a frame
  drum's soft procession (dum on 1, ghost on 3).

Form (bars): 1-4 the lanterns (no tune) | 5-12 A | 13-20 B (higher; the women hum with the zither) | 21-28 A (with
the hum) | 29-32 the lanterns again and the tune's first cell once, softly; the roots (F Gb Bb C) lead back to bar
1's F.

Render:  python3 assets_src/music/terraces_of_ash.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.water import bubble  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "terraces_of_ash.ogg")
SEED = 20261202
TARGET_LUFS = -16.0
BPM = 72.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 32
LOOP_S = BARS * BAR

SCALE_PC = [n(x) % 12 for x in "F4 Gb4 Bb4 C5 Db5".split()]
LANTERN = ["F5", "Gb5", "Bb5", "C6", "Db6", "F6", "Gb6"]
ROOTS = (["F", "F", "F", "F"]
         + ["F", "F", "Gb", "F", "Bb", "Db", "Gb", "C"]
         + ["Db", "Db", "Bb", "Bb", "Gb", "Gb", "F", "F"]
         + ["F", "F", "Gb", "F", "Bb", "Db", "Gb", "C"]
         + ["F", "Gb", "Bb", "C"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["A2"] * 8 + ["T"] * 4
ROOT_MIDI = {"F": "F2", "Gb": "Gb2", "Bb": "Bb1", "C": "C2", "Db": "Db2"}

## the tune: one list per bar of (pitch, beats)
TUNE_A = [
    [("C5", 2), ("Db5", 1)],
    [("C5", 3)],
    [("Bb4", 1), ("C5", 1), ("Gb4", 1)],
    [("F4", 3)],
    [("Bb4", 2), ("C5", 1)],
    [("Db5", 2), ("F5", 1)],
    [("Gb5", 1.5), ("F5", .5), ("Db5", 1)],
    [("C5", 3)],
]
TUNE_B = [
    [("F5", 2), ("Gb5", 1)],
    [("F5", 1), ("Db5", 1), ("C5", 1)],
    [("Bb4", 3)],
    [("C5", 2), ("Db5", 1)],
    [("C5", 1), ("Bb4", 1), ("Gb4", 1)],
    [("F4", 2), ("Gb4", 1)],
    [("F4", 3)],
    [(None, 3)],
]
TAIL_CELL = [[("C5", 2), ("Db5", 1)], [("C5", 3)]]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def scale_below(m: float) -> float:
    """The scale tone just below MIDI m (the grace note)."""
    k = m - 1
    while k % 12 not in SCALE_PC:
        k -= 1
    return k


def zither_body(seed: int, sr: int = SR) -> np.ndarray:
    """A long, shallow box (a zither's): more low-mid modes than a lute's, broad (low Q) so no note of the tune
    lands on a resonance much louder than its neighbours."""
    g = rng(seed)
    t = np.arange(int(0.35 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((92.0, 6, 0.7), (175.0, 6, 0.8), (290.0, 5.5, 0.6), (455.0, 5, 0.45), (720.0, 4.5, 0.35),
                    (1150.0, 4, 0.25), (2100.0, 3.5, 0.15), (3600.0, 3, 0.08)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.5)) * np.exp(-t / d) * 0.07
    return ir / np.abs(ir).max()


def zither(m: float, dur: float, vel: float, seed: int, body: np.ndarray) -> np.ndarray:
    x = string_pluck(m, dur, vel, seed=seed, pick_pos=0.09, t60=3.6, B=3e-5, max_f=7000.0, release=0.25)
    return fft_convolve(x, body)[: len(x) + 6000]


def low_string(m: float, dur: float, vel: float, seed: int) -> np.ndarray:
    """The zither's low strings, without the box (its low modes would boom on some roots and not others)."""
    return string_pluck(m, dur, vel, seed=seed, pick_pos=0.14, t60=4.0, B=5e-5, max_f=4000.0, release=0.3)


def add_tune(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, body: np.ndarray,
             hum: list | None = None) -> None:
    """The zither line; appends (midi, seconds) to `hum` (an octave down) when given."""
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is None:
                if hum is not None:
                    hum.append((None, d))
                pos += d
                first = True
                continue
            m = n(p)
            v = vel * g.uniform(0.92, 1.05)
            ts = pos + float(g.normal(0, 0.006))
            if first:      # a grace note from the scale step below, just ahead of the beat
                gm = scale_below(m)
                mx.add("zither", zither(gm, 0.08, v * 0.55, seed + 3 * int(pos * 100) + 1, body), ts - 0.07,
                       pan=-0.12)
            mx.add("zither", zither(m, d, v, seed + 3 * int(pos * 100), body), ts, pan=-0.12)
            if beats >= 2:  # a soft re-strike one beat in, so the long note keeps glowing
                mx.add("zither", zither(m, d - BEAT, v * 0.42, seed + 3 * int(pos * 100) + 2, body), ts + BEAT,
                       pan=-0.08)
            if hum is not None:
                hum.append((m - 12, d))
            pos += d
            first = False


def merged_line(line: list) -> list:
    """hum_ensemble wants (midi, seconds) with no rests: a rest extends the note before it."""
    out: list = []
    for m, d in line:
        if m is None and out:
            out[-1] = (out[-1][0], out[-1][1] + d)
        elif m is not None:
            out.append((m, d))
    return out


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = zither_body(SEED + 5)
    for bar, (root, sec) in enumerate(zip(ROOTS, SECTION), start=1):
        r = n(ROOT_MIDI[root])
        # the low zither string: the root, its octave on beat 3 (only the root in the intro and tail)
        mx.add("low", low_string(r, 2.2 * BEAT, 0.55 * g.uniform(0.94, 1.04), SEED + 3000 + bar), t_of(bar),
               pan=0.05)
        if sec not in ("I", "T"):
            mx.add("low", low_string(r + 12, 0.9 * BEAT, 0.34, SEED + 3100 + bar), t_of(bar, 2), pan=0.15)
        # copper: a kettle gong on each downbeat (C or F), a large gong every eight bars
        p = "C4" if bar % 2 else "F3"
        mx.add("gong", kettle_gong(n(p), 0.26 * g.uniform(0.9, 1.05), seed=SEED + 400 + bar, t60=2.4), t_of(bar),
               pan=0.3 if bar % 2 else -0.25)
        # a soft procession on the frame drum
        if sec != "I" or bar >= 3:
            for b, stroke, v in ((0, "dum", 0.36), (2, "ghost", 0.14), (2.5, "ghost", 0.10)):
                if sec == "T" and stroke == "ghost" and b == 2.5:
                    continue
                x = frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=bar * 3 + int(b), size=1.2, seed=SEED + 1)
                mx.add("drums", x, t_of(bar, b) + float(g.normal(0, 0.006)), pan=-0.05)
        # the lanterns: short falling runs of the scale, high and soft
        runs = 2 if sec in ("I", "T") else (1 if bar % 2 == 0 else 0)
        for j in range(runs):
            top = int(g.integers(3, len(LANTERN)))
            length = int(g.integers(3, 5))
            start = t_of(bar, float(g.uniform(0.3, 2.2)) if j == 0 else float(g.uniform(1.4, 2.6)))
            pan = float(g.uniform(-0.7, 0.7))
            step = BEAT * g.uniform(0.38, 0.55)
            for k in range(length):
                idx = top - k
                if idx < 0:
                    break
                x = metallophone_note(n(LANTERN[idx]), 0.22 * g.uniform(0.8, 1.05) * (1 - 0.1 * k),
                                      seed=SEED + 5000 + 10 * bar + 100 * j + k, decay=2.6, hardness=0.2,
                                      ombak_hz=3.0)
                mx.add("lantern", x, start + k * step + float(g.normal(0, 0.01)), pan=pan + 0.06 * k)
        # the channels: tuned bubbles, irregular
        for _ in range(3):
            pc = SCALE_PC[int(g.integers(0, len(SCALE_PC)))]
            m = 84 + pc + (12 if g.random() < 0.3 else 0)
            f = midi_to_hz(m)
            x = bubble(3260.0 / f, 1.0, rise=float(g.uniform(0.01, 0.03)))
            mx.add("water", x * g.uniform(0.3, 1.0), t_of(bar, float(g.uniform(0, 3))), pan=float(g.uniform(-0.8, 0.8)))
    for bar in (1, 9, 17, 25):
        mx.add("gong", large_gong(n("F1"), 0.32 if bar in (1, 17) else 0.24, seed=SEED + 500 + bar, t60=9.0),
               t_of(bar), pan=-0.1)
    # the tune
    add_tune(mx, TUNE_A, 5, SEED + 600, 0.62, body)
    hum: list = []
    add_tune(mx, TUNE_B, 13, SEED + 700, 0.66, body, hum=hum)
    add_tune(mx, TUNE_A, 21, SEED + 800, 0.62, body, hum=hum)
    add_tune(mx, TAIL_CELL, 29, SEED + 900, 0.42, body)
    # the mourners, an octave under the zither through B and A'
    women = hum_ensemble(merged_line(hum), voices=10, seed=SEED + 11, register="high", spread=0.85)
    env = np.ones(len(women))
    k = int(2.0 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    end = int(16 * BAR * SR)
    env[end:] = np.exp(-np.arange(len(env) - end) / SR / 0.8)
    mx.add("hum", women * env[:, None], t_of(13) - 0.1)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# zither (0 LU): low string -9, lanterns -9, the hum -6 (measured over the whole loop; it sounds only in B and A'),
# gongs -11, drums -14, water -17.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("zither", 0.0, send=0.30, process=lambda x: filt(x, [bq_highpass(140, 0.7), bq_peak(2800, 1.5, 1.0),
                                                                  bq_lowpass(8000, 0.7)]))
    mx.bus("low", -7.5, send=0.25, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.bus("lantern", -2.9, send=0.60)
    mx.bus("water", -20.6, send=0.50, process=lambda x: filt(x, [bq_highpass(400, 0.7)]))
    mx.bus("hum", -11.4, send=0.75)
    mx.bus("gong", -12.3, send=0.45)
    mx.bus("drums", -12.6, send=0.30, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
    build(mx)
    night = ModFDNReverb(rt60=3.4, rt60_high=1.4, predelay=0.04, size=1.2, mod_depth=10.0, mod_rate=0.45,
                         early_level=0.22, lowcut=100.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=night, reverb_return_db=-2.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 3, extra={"loop_bars": BARS})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"terraces_of_ash: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
