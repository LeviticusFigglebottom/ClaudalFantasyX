"""`corrow_night`: Ch9 B01, B03 and B08 (stripped), Corrow's strand the night the wall fell (M3-AUD-819;
act1_ch09.md §6): a 61.2 s seamless loop.

Original material (SPEC §2): the tune is our own Corrow day tune (corrow_seawall.py TUNE_A, TUNE_B and TUNE_A2,
written for this project), and the hum is the Order's congregational tune as written once in motifs.py (ORDER_HUM,
first heard in the Shell Shrine). Neither is re-typed here, and neither derives from an existing melody.

The brief: "Night bed: corrow_day's wind melody slowed and alone over the surf, with the Order's congregational hum
far off, broken, people humming while they do other things." The town is counting its dead on the strand. The
day cue's ground bass, plucks, drums, gongs and the Watchers' chorale are gone: only the tune is left, and it no
longer has anything under it.

B minor, 4/4 at 51 BPM (the day cue's 76, slowed by a third; a bar is 4.7 s), 13 bars.
* the tune: the same low breath flute as the day cue (a fisher's whistle), slower, softer, more air in it, a slow
  vibrato only on the held notes: phrase a (bars 1-4), a bar of nothing, phrase b (6-9), a bar of nothing, and the
  end of a' (11-12: "G E | F#"), left on the F# with nobody to answer it;
* the surf: waves breaking on the strand, slower than the day's (8-11 s apart), low and wide, exactly one loop long;
* the Order's hum, far off and broken: one or two or three people at a time humming a few notes of ORDER_HUM, each at
  their own pitch, their own pace, starting in the middle of the tune and stopping before its end, as people hum
  over work (laying out the dead, mending, carrying water). Never the whole tune, never together.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The tune starts a beat into the file, so the wrap seam falls
on the surf alone (the sidecar's `downbeat_offset_s` is bar 1's downbeat).

Render:  python3 assets_src/music/corrow_night.py   (or tools/audio/render_all.py --only corrow_night)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from motifs import ORDER_HUM_BPM, order_hum_in_seconds  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DAY = _mod("corrow_seawall", os.path.join(HERE, "corrow_seawall.py"))
FA = _mod("field_ambience", os.path.join(ROOT, "assets_src", "sfx", "field_ambience.py"))

OUT = os.path.join(ROOT, "assets", "audio", "music", "corrow_night.ogg")
SEED = 20261822
TARGET_LUFS = -16.0
BPM = 51.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 13
LOOP_S = BARS * BAR
T0 = BEAT                              # bar 1's downbeat, a beat into the file
FLUTE_PRE = 0.065                      # breath_flute speaks this late
## the day tune's phrases, by bar: a (1-4), b (6-9), the end of a' (11-12)
PHRASES = [(1, DAY.TUNE_A), (6, DAY.TUNE_B), (11, DAY.TUNE_A2[2:])]
## the hum's fragments: (loop time s, first note, notes, voices, register, pace vs ORDER_HUM_BPM, pan)
HUM_FRAGMENTS = [(2.5, 0, 3, 1, "low", 0.92, -0.65), (13.0, 4, 3, 2, "low", 1.05, 0.55),
                 (22.0, 1, 4, 1, "high", 0.97, 0.75), (30.5, 5, 4, 3, "low", 0.9, -0.4),
                 (41.0, 2, 3, 1, "low", 1.1, 0.2), (47.5, 6, 3, 2, "high", 0.95, -0.75),
                 (55.0, 0, 2, 1, "low", 1.0, 0.45)]


def t_of(bar: int, beat: float = 0.0) -> float:
    return T0 + (bar - 1) * BAR + beat * BEAT


def add_tune(mx: LoopMixer, bars: list, start_bar: int, seed: int) -> None:
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
            held = beats >= 2
            x = breath_flute(n(p), d * 0.96 + 0.04, 0.44 * g.uniform(0.94, 1.04) * (1.04 if held else 1.0),
                             seed=seed + int(round(pos * 1000)), breath=0.62, scoop_cents=45.0 if first else 14.0,
                             vib_cents=10.0 if held else 2.0, vib_rate=3.9, swell=0.2 if beats >= 3 else 0.0,
                             attack=0.12 if first else 0.06, release=0.5, beta=0.45)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.006)), pan=-0.05)
            pos += d
            first = False


def surf(g) -> np.ndarray:
    """One loop of waves on the strand at night: a low roar floor and seven slow breaks, whole cycles per loop."""
    L = int(round(LOOP_S * SR))
    tt = np.arange(L) / SR
    floor = FA.stereo_noise(L, g, [bq_lowpass(300, 0.6), bq_highpass(40, 0.7)], 0.5) * (0.8 + 0.2 * FA.plfo(L, 0.04, g)
                                                                                      )[:, None]
    low = FA.stereo_noise(L, g, [bq_lowpass(550, 0.6), bq_highpass(60, 0.7)], 0.5)
    crash = FA.stereo_noise(L, g, [bq_lowpass(3500, 0.6), bq_highpass(200, 0.7)], 0.35)
    foam = FA.stereo_noise(L, g, [bq_bandpass(2200, 0.7), bq_highpass(800, 0.7)], 0.2)
    per = g.uniform(8.0, 11.0, 6)
    per *= LOOP_S / per.sum()
    starts = np.concatenate([[0.0], np.cumsum(per)[:-1]]) + 3.0
    e_low, e_crash, e_foam = (np.zeros((L, 2)) for _ in range(3))
    for s, p in zip(starts, per):
        size = float(g.uniform(0.5, 1.0))
        pan = float(g.uniform(-0.6, 0.6))
        lr = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
        d = (tt - s) % LOOP_S
        pre = d - LOOP_S
        swell = np.exp(-(pre / 1.8) ** 2) * (pre > -5.0)
        brk = np.where(d < p, np.clip(d / 0.2, 0, 1) * np.exp(-d / 1.1), 0.0)
        run = np.where(d < p, np.clip((d - 0.3) / 0.7, 0, 1) * np.exp(-np.maximum(d - 1.0, 0) / 2.0), 0.0)
        e_low += size * (0.5 * swell + 0.8 * brk + 0.3 * run)[:, None] * lr
        e_crash += size * brk[:, None] * lr
        e_foam += size * run[:, None] * lr
    return 0.05 * (0.5 * floor + 0.9 * low * e_low + 0.5 * crash * e_crash + 0.35 * foam * e_foam)


def hum_fragment(first: int, count: int, voices: int, register: str, pace: float, seed: int) -> np.ndarray:
    """A few notes of the Order's tune (motifs.ORDER_HUM from note `first`), hummed by `voices` people at their own
    pace, faded in and let go (nobody finishes it)."""
    line = order_hum_in_seconds(ORDER_HUM_BPM * pace)[first: first + count]
    shift = -12.0 if register == "low" else 0.0
    x = hum_ensemble([(m + shift, d) for m, d in line], voices=voices, seed=seed, register=register, spread=0.25,
                     scatter_cents=14.0)
    env = np.ones(len(x))
    k = int(0.6 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    stop = int(sum(d for _, d in line) * SR * 0.85)                      # the last note let go early
    env[stop:] *= np.exp(-np.arange(len(env) - stop) / SR / 0.5)
    return x * env[:, None]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("surf", surf(rng(SEED + 3)), 0.0)
    for k, (start, bars) in enumerate(PHRASES):
        add_tune(mx, bars, start, SEED + 100 * (k + 1))
    for i, (t, first, count, voices, reg, pace, pan) in enumerate(HUM_FRAGMENTS):
        x = hum_fragment(first, count, voices, reg, pace, SEED + 500 + i)
        th = (pan + 1) * np.pi / 4                                       # the whole fragment placed at its pan
        mono = x.mean(axis=1)
        mx.add("hum", np.stack([mono * np.cos(th), mono * np.sin(th)], axis=1) * np.sqrt(2),
               t + float(g.uniform(-0.3, 0.3)))


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]): the flute at L, the surf L-7 (the
## strand, under the tune), the far hum L-9.
GAINS = {"flute": 0.0, "surf": -1.8, "hum": -4.1}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("flute", GAINS["flute"], send=0.38,
           process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(1800, 1.0, 1.0), bq_lowpass(5500, 0.7)]))
    mx.bus("surf", GAINS["surf"], send=0.08, process=lambda x: filt(x, [bq_highpass(45, 0.7)]))
    mx.bus("hum", GAINS["hum"], send=0.75, process=lambda x: filt(x, [bq_highpass(90, 0.7), bq_lowpass(1500, 0.7)]))
    build(mx)
    night = ModFDNReverb(rt60=2.8, rt60_high=0.9, predelay=0.03, size=1.3, mod_depth=8.0, mod_rate=0.4,
                         early_level=0.2, lowcut=110.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=night, reverb_return_db=-3.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": T0})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"corrow_night: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses (LU vs the flute)", {k: round(v - mx.bus_lufs["flute"], 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
