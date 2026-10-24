"""The Shell Shrine trial's sounds (M2-AUD-01; vertical_slice.md B07): you hear the water go where you sent it.

Physical-ish models, all synthesized here (no samples):
* stone_turn: a basin turning on its stone seat. Stick-slip grinding: impulses at a rate that follows the turn's
  speed (a sine arch over the 1.2 s turn), each ringing a few short stone modes, over band-passed rumble; the lip
  seats with a low knock at the end. Three variants (slightly different stone).
* pour: the water reaching the inner pool: a stream's noise rush plus a dense field of Minnaert bubbles.
* spill: water lost onto a floor grate: splatter on metal bars (short high modes) and patter.
* drain: the water reaching the side pool's sluice: hollow gurgles through a stone channel (a resonant tube).
* side_drain: the side pool emptying for good (3 s): gurgles that quicken, then the last suck and a glug.
* door: the door's shell valve sinking: a deep slow grind, water rushing through, a low settling boom.
* charm: the net-float charm's glint: two tiny high bars and a breath of shimmer.
* pool_fill (a 6 s stereo loop; see render_fill): the inner pool filling while the water reaches it.

Every sound is placed in the same small stone room (a short modulated FDN). Loudness: world SFX at -18 LUFS
momentary max with peaks <= -1 dBFS (mix.md); the fill loop at -24 LUFS integrated (it sits under the cue).

Render:  python3 assets_src/sfx/shrine_sfx.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.water import bubble  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "shrine")
SEED = 20261103
WORLD_TARGET = -18.0
FILL_TARGET = -24.0
FILL_LOOP_S = 6.0
FILES = ["shrine_stone_turn_1.ogg", "shrine_stone_turn_2.ogg", "shrine_stone_turn_3.ogg", "shrine_pour.ogg",
         "shrine_spill.ogg", "shrine_drain.ogg", "shrine_side_drain.ogg", "shrine_door.ogg", "shrine_charm.ogg"]


def _t(sec: float) -> np.ndarray:
    return np.arange(int(sec * SR)) / SR


def _place(buf: np.ndarray, x: np.ndarray, t: float) -> None:
    s = int(t * SR)
    if s >= len(buf):
        return
    e = min(len(buf), s + len(x))
    buf[s:e] += x[: e - s]


def _modes(freqs, decays, amps, sec: float, g) -> np.ndarray:
    t = _t(sec)
    out = np.zeros(len(t))
    for f, d, a in zip(freqs, decays, amps):
        out += a * np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) * np.exp(-t / d)
    return out


def _room(x: np.ndarray, seed: int, wet: float = 0.22, rt60: float = 1.5) -> np.ndarray:
    """The shrine room: a short modulated FDN, mixed down to mono."""
    rv = ModFDNReverb(rt60=rt60, rt60_high=0.7, predelay=0.012, size=0.6, mod_depth=6.0, mod_rate=0.5,
                      early_level=0.3, lowcut=120.0, seed=seed)
    tail = int(rt60 * SR)
    xs = np.concatenate([x, np.zeros(tail)])
    w = rv.process(np.stack([xs, xs], 1), tail=0.0)[: len(xs)].mean(axis=1)
    return xs + wet * w


def _finish(x: np.ndarray, fade_s: float = 0.05) -> np.ndarray:
    k = int(fade_s * SR)
    x = x.copy()
    x[-k:] *= np.linspace(1, 0, k) ** 2
    x = filt(x, [bq_highpass(35, 0.7)])
    return normalize_momentary(x, WORLD_TARGET, ceiling_db=-1.5)


def stone_turn(variant: int) -> np.ndarray:
    g = rng(SEED + 10 + variant)
    T = 1.2
    sec = T + 0.5
    out = np.zeros(int(sec * SR))
    speed = np.sin(np.pi * np.clip(_t(sec) / T, 0, 1)) ** 0.7
    scale = (0.94, 1.0, 1.07)[variant]
    freqs = [f * scale for f in (170.0, 310.0, 505.0, 880.0, 1460.0)]
    tt, ev = 0.03, []
    while tt < T:
        rate = 40.0 + 220.0 * speed[int(tt * SR)]
        ev.append(tt)
        tt += g.exponential(1.0 / rate)
    for e in ev:
        sp = speed[int(e * SR)]
        hit = _modes(freqs, [0.012, 0.010, 0.008, 0.006, 0.004], [1.0, 0.7, 0.45, 0.3, 0.2], 0.05, g)
        _place(out, hit * sp * g.uniform(0.4, 1.0), e)
    rumble = filt(g.standard_normal(len(out)), [bq_bandpass(220 * scale, 0.9), bq_lowpass(700, 0.7)])
    out = 0.012 * out + 0.10 * rumble * speed
    knock = _modes([62.0 * scale, 118.0 * scale, 240.0], [0.09, 0.05, 0.02], [1.0, 0.5, 0.3], 0.4, g)
    _place(out, 0.9 * knock, T - 0.04)
    return _finish(_room(out, SEED + 20 + variant))


def _stream(sec: float, g, lo: float = 1.2, hi: float = 5.5, rate: float = 160.0, rush: float = 0.25,
            env=None) -> np.ndarray:
    """A stream of water: band-limited rush noise plus Poisson bubbles of random radius (mm)."""
    out = np.zeros(int(sec * SR))
    env = np.ones(len(out)) if env is None else env
    tt = 0.0
    while tt < sec:
        r = float(np.exp(g.uniform(np.log(lo), np.log(hi))))
        b = bubble(r, g.uniform(0.2, 1.0), rise=g.uniform(0.05, 0.15))
        _place(out, b * env[min(len(env) - 1, int(tt * SR))], tt)
        tt += g.exponential(1.0 / rate)
    noise = filt(g.standard_normal(len(out)), [bq_bandpass(900, 0.5), bq_lowpass(4000, 0.7)])
    return 0.08 * out + rush * 0.12 * noise * env


def pour() -> np.ndarray:
    g = rng(SEED + 30)
    sec = 1.8
    t = _t(sec)
    env = np.minimum(1.0, t / 0.12) * np.exp(-np.maximum(0, t - 0.5) / 0.6)
    x = _stream(sec, g, 1.5, 6.0, 220.0, 0.35, env)
    splash = filt(g.standard_normal(int(0.08 * SR)), [bq_bandpass(2500, 0.6)]) * np.exp(-_t(0.08) / 0.02)
    _place(x, 0.15 * splash, 0.0)
    return _finish(_room(x, SEED + 31))


def spill() -> np.ndarray:
    g = rng(SEED + 40)
    sec = 1.5
    out = np.zeros(int(sec * SR))
    tt = 0.0
    while tt < 1.1:
        bar = _modes([g.uniform(2200, 2600), g.uniform(3900, 4500), g.uniform(6100, 6900)],
                     [0.03, 0.015, 0.008], [1.0, 0.5, 0.3], 0.08, g)
        _place(out, bar * g.uniform(0.2, 1.0) * np.exp(-tt / 0.6), tt)
        tt += g.exponential(1.0 / 45.0)
    t = _t(sec)
    patter = _stream(sec, g, 0.8, 2.5, 120.0, 0.6, np.minimum(1.0, t / 0.05) * np.exp(-t / 0.5))
    x = 0.025 * out + patter
    return _finish(_room(x, SEED + 41))


def _gurgle(sec: float, g, tube_hz: float, rate_fn, lo: float = 4.0, hi: float = 10.0) -> np.ndarray:
    out = np.zeros(int(sec * SR))
    tt = 0.0
    while tt < sec - 0.2:
        r = float(np.exp(g.uniform(np.log(lo), np.log(hi))))
        _place(out, bubble(r, g.uniform(0.4, 1.0), rise=g.uniform(0.15, 0.35)), tt)
        tt += g.exponential(1.0 / max(1.0, rate_fn(tt)))
    tube = filt(out, [bq_bandpass(tube_hz, 2.0)]) * 3.0 + 0.5 * out
    return 0.12 * tube


def drain() -> np.ndarray:
    g = rng(SEED + 50)
    sec = 1.8
    t = _t(sec)
    x = _gurgle(sec, g, 320.0, lambda tt: 30.0 * np.exp(-tt / 0.9))
    x += _stream(sec, g, 1.5, 4.0, 90.0, 0.25, np.minimum(1.0, t / 0.1) * np.exp(-t / 0.7))
    return _finish(_room(x, SEED + 51))


def side_drain() -> np.ndarray:
    g = rng(SEED + 60)
    sec = 3.4
    t = _t(sec)
    x = _gurgle(sec, g, 260.0, lambda tt: 8.0 + 40.0 * (tt / 2.6) ** 2 if tt < 2.6 else 4.0)
    suck_t = _t(0.6)
    sweep = filt(g.standard_normal(len(suck_t)), [bq_bandpass(700, 0.8)]) * np.sin(np.pi * suck_t / 0.6) ** 2
    _place(x, 0.06 * sweep, 2.55)
    _place(x, 0.9 * bubble(14.0, 1.0, rise=0.4) * 0.3, 3.05)
    x += 0.05 * filt(g.standard_normal(len(t)), [bq_lowpass(500, 0.7)]) * np.clip(t / 2.6, 0, 1) * (t < 2.9)
    return _finish(_room(x, SEED + 61), fade_s=0.1)


def door() -> np.ndarray:
    g = rng(SEED + 70)
    T = 1.5
    sec = T + 1.2
    t = _t(sec)
    speed = np.sin(np.pi * np.clip(t / T, 0, 1)) ** 0.5
    grind = filt(g.standard_normal(len(t)), [bq_bandpass(110, 0.8), bq_lowpass(400, 0.7)]) * speed
    tick = np.zeros(len(t))
    tt = 0.02
    while tt < T:
        _place(tick, _modes([95.0, 180.0, 330.0], [0.02, 0.012, 0.008], [1, .6, .3], 0.06, g) * g.uniform(.3, 1), tt)
        tt += g.exponential(1.0 / (30 + 90 * speed[int(tt * SR)]))
    rush = _stream(sec, g, 2.0, 7.0, 140.0, 0.6, np.clip((t - 0.3) / 0.8, 0, 1) * np.exp(-np.maximum(0, t - T) / 0.5))
    boom = _modes([42.0, 61.0, 97.0], [0.5, 0.3, 0.15], [1.0, 0.6, 0.3], 1.2, g)
    x = 0.2 * grind + 0.015 * tick + 0.8 * rush
    _place(x, 0.8 * boom, T - 0.05)
    return _finish(_room(x, SEED + 71, wet=0.3, rt60=2.0), fade_s=0.2)


def charm() -> np.ndarray:
    g = rng(SEED + 80)
    sec = 1.2
    x = np.zeros(int(sec * SR))
    _place(x, metallophone_note(100.0, 0.30, seed=SEED + 81, decay=0.9, hardness=0.6,
                                ombak_hz=6.0)[: len(x)], 0.0)
    _place(x, metallophone_note(95.0, 0.22, seed=SEED + 82, decay=0.8, hardness=0.6, ombak_hz=7.0)[: len(x)], 0.09)
    shimmer = filt(g.standard_normal(len(x)), [bq_highpass(6000, 0.7)]) * np.exp(-_t(sec) / 0.25) * 0.02
    return _finish(_room(x + shimmer, SEED + 83, wet=0.3))


def render_fill(out_path: str, verbose: bool = False) -> dict:
    """The inner pool filling: a 6 s seamless stereo loop of the stream and its bubbles."""
    g = rng(SEED + 90)
    mx = LoopMixer(intro_s=0.0, loop_s=FILL_LOOP_S, preroll_s=2.5)
    mx.bus("water", 0.0, send=0.3)
    for side, pan in ((0, -0.4), (1, 0.4)):
        x = _stream(FILL_LOOP_S, g, 1.5, 6.0, 200.0, 0.4)
        mx.add("water", x, 0.0, pan=pan)
    rv = ModFDNReverb(rt60=1.5, rt60_high=0.7, predelay=0.012, size=0.6, mod_depth=6.0, mod_rate=0.5,
                      early_level=0.3, lowcut=120.0, seed=SEED + 91)
    _, loop = mx.render(reverb=rv, reverb_return_db=-4.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, FILL_TARGET, ceiling_db=-6.0)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, None, None)
    m = measure(loop)
    if verbose:
        print(f"shrine_pool_fill: {m['seconds']:.2f}s {m['integrated_lufs']:.2f} LUFS")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> None:
    os.makedirs(out_dir, exist_ok=True)
    sounds = [stone_turn(0), stone_turn(1), stone_turn(2), pour(), spill(), drain(), side_drain(), door(), charm()]
    for name, x in zip(FILES, sounds):
        write_ogg(os.path.join(out_dir, name), x[:, None] if x.ndim == 1 else x, quality=4.0)
        if verbose:
            m = measure(np.stack([x, x], 1))
            print(f"{name:28} {m['seconds']:5.2f}s  Mmax {m['momentary_max_lufs']:6.2f}  peak {m['sample_peak_dbfs']:6.2f}")


if __name__ == "__main__":
    render()
    render_fill(os.path.join(OUT_DIR, "shrine_pool_fill.ogg"), verbose=True)
