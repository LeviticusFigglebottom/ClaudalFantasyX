"""Underwater ambience beds and Rhen's diving sounds (M3-AUD-06; Ch1's drowned-tower dive, M2-RND-02's underwater).

Everything is synthesized here and in tools/audio/synth/ from noise, oscillators and simple physical models
(SPEC §2, §9: no samples, no recordings, no generated audio). Under water the ear hears mostly by bone
conduction: little above 2-3 kHz, a lot of low pressure, and every bubble (Minnaert, synth/water.py) close and
clear. Two tools carry that:

* `muffle()`: a low-pass whose cutoff glides over time (crossfaded fixed low-passes), so the splash of an entry
  is bright in the air and closes over as the head goes under, and a surfacing opens back out.
* `uw_room()`: a dark modulated FDN (high frequencies die fast) folded to mono, for a body of water.

Beds (assets/audio/ambience/, seamless stereo loops at -26 LUFS integrated, <= -6 dBFS, Vorbis q1 like
field_ambience.py; LOOPSTART = 0, LOOPLENGTH = the file, plus a .loop.json sidecar):
    underwater_deep.ogg  46 s  open deep water: a pressure hum (sub-bass noise and a slowly beating low tone),
                               distant creaks of something old and large settling, slow bubble trains rising
                               from far below, and a faint particulate tick
    drowned_tower.ogg    42 s  inside the drowned tower: the stone shaft's resonances excited by the current, a
                               current that surges through the openings, small stones ticking down, air leaking
                               from cracks in short trains, and once in a while the tower groaning

Diving SFX (assets/audio/sfx/dive/, mono, -18 LUFS momentary max, peaks <= -1.5 dBFS, q4; strokes at -20):
    dive_entry.ogg        the splash in the air, then the muffle closing over: bubbles, the rush past the ears
    dive_surface.ogg      bubbles rising, the surface breaking (the muffle opens), water streaming off, drips,
                          and a long breath out through the lips: unvoiced, no gasp, no voice
    dive_bubble_burst.ogg a puff of air let go: a dense burst of bubbles, one big low blub, stragglers
    dive_stroke_1..4.ogg  swimming strokes under water: the displacement swoosh of a pull, a few bubbles
    dive_lantern_hum.ogg  the lantern under water: a warm low hum (beating low partials and a soft flame roar
                          heard through the glass); a 6 s seamless loop at -24 LUFS integrated (<= -6 dBFS)

Render:  python3 assets_src/sfx/underwater_sfx.py   (or tools/audio/render_all.py --only underwater_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from field_ambience import circ_noise, modal, plfo, schedule, snap, stereo_noise, stick_slip  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, normalize_integrated, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio")  # files go to ambience/ and sfx/dive/ under it
SEED = 20261206
BED_TARGET, BED_CEILING, BED_QUALITY = -26.0, -6.0, 1.0
SFX_TARGET, STROKE_TARGET, SFX_CEILING = -18.0, -20.0, -1.5
HUM_TARGET, HUM_LOOP_S = -24.0, 6.0
BEDS = {"underwater_deep": 46.0, "drowned_tower": 42.0}


# --------------------------------------------------------------------------- building blocks


def _n(sec: float) -> int:
    return int(round(sec * SR))


def _t(n: int) -> np.ndarray:
    return np.arange(n) / SR


def place(buf: np.ndarray, x: np.ndarray, t: float, gain: float = 1.0) -> None:
    s = _n(t)
    if s >= len(buf):
        return
    if s < 0:
        x, s = x[-s:], 0
    e = min(len(buf), s + len(x))
    buf[s:e] += gain * x[: e - s]


def muffle(x: np.ndarray, f_from: float, f_to: float, t0: float, t1: float, steps: int = 12) -> np.ndarray:
    """A low-pass whose cutoff glides (log) from f_from (before t0) to f_to (after t1): crossfaded fixed
    low-passes, since the FFT biquads are time-invariant."""
    t = _t(len(x))
    u = np.clip((t - t0) / max(t1 - t0, 1e-6), 0, 1)
    pos = u * (steps - 1)
    out = np.zeros(len(x))
    for i in range(steps):
        w = np.clip(1 - np.abs(pos - i), 0, 1)
        if not w.any():
            continue
        fc = f_from * (f_to / f_from) ** (i / (steps - 1))
        out += w * filt(x, [bq_lowpass(fc, 0.6), bq_lowpass(fc * 1.3, 0.6)])
    return out


def uw_room(x: np.ndarray, seed: int, rt60: float = 1.4, mix: float = 0.3, tail: float = 1.2,
            highcut: float = 2200.0) -> np.ndarray:
    """A body of water around the listener: a dark modulated FDN folded to mono, `tail` seconds appended."""
    rv = ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.3, predelay=0.008, size=0.9, mod_depth=6.0, mod_rate=0.4,
                      early_level=0.25, lowcut=60.0, highcut=highcut, seed=seed)
    xs = np.concatenate([x, np.zeros(_n(tail))])
    wet = rv.process(np.stack([xs, xs], 1), tail=0.0)[: len(xs)].mean(axis=1)
    return (1 - mix) * xs + mix * wet


def air_room(x: np.ndarray, seed: int, mix: float = 0.12, tail: float = 0.6) -> np.ndarray:
    """Open air over water: a short, bright, sparse reflection field."""
    rv = ModFDNReverb(rt60=0.7, rt60_high=0.4, predelay=0.02, size=1.4, mod_depth=4.0, mod_rate=0.3,
                      early_level=0.35, lowcut=200.0, highcut=7000.0, seed=seed)
    xs = np.concatenate([x, np.zeros(_n(tail))])
    wet = rv.process(np.stack([xs, xs], 1), tail=0.0)[: len(xs)].mean(axis=1)
    return (1 - mix) * xs + mix * wet


def noise(g: np.random.Generator, n: int, sections=None) -> np.ndarray:
    x = g.standard_normal(n)
    return filt(x, sections) if sections else x


def env_swell(n: int, peak: float, rise: float = 2.0, fall: float = 0.3) -> np.ndarray:
    t = _t(n)
    return np.clip(t / peak, 0, 1) ** rise * np.where(t > peak, np.exp(-(t - peak) / fall), 1.0)


def bubble_cloud(g: np.random.Generator, n: int, rate: float, r_lo: float, r_hi: float, env=None,
                 amp: float = 1.0) -> np.ndarray:
    """Poisson bubbles at `rate` per second (scaled by env), log-uniform radii in mm."""
    out = np.zeros(n)
    env = np.ones(n) if env is None else env
    peak = float(env.max()) + 1e-12
    tt = 0.0
    while tt < n / SR:
        e = env[min(n - 1, _n(tt))] / peak
        if g.random() < e:
            r = float(np.exp(g.uniform(np.log(r_lo), np.log(r_hi))))
            place(out, bubble(r, amp * float(g.uniform(0.3, 1.0)), rise=float(g.uniform(0.05, 0.18))), tt)
        tt += float(g.exponential(1.0 / rate))
    return out


def bubble_train(g: np.random.Generator, count: int, r_lo: float, r_hi: float, gap: tuple[float, float],
                 amp: float = 1.0, fade: float = 0.0) -> np.ndarray:
    """Bubbles one after another from a single source (a leak, a sinking thing): similar radii, steady gaps."""
    r0 = float(g.uniform(r_lo, r_hi))
    times = np.cumsum(g.uniform(gap[0], gap[1], count))
    out = np.zeros(_n(float(times[-1]) + 0.5))
    for i, at in enumerate(times):
        lvl = amp * (1 - fade * i / max(1, count - 1)) * float(g.uniform(0.6, 1.0))
        place(out, bubble(r0 * float(g.uniform(0.85, 1.15)), lvl, rise=float(g.uniform(0.1, 0.25))), float(at))
    return out


def stroke(g: np.random.Generator, size: float = 1.0, bright: float = 1600.0) -> np.ndarray:
    """A swimming stroke under water: the pull's displacement swoosh (a band that rises and falls with the hand's
    speed), the softer recovery, and a few bubbles shed by the fingers."""
    sec = 0.9 + 0.2 * size
    n = _n(sec)
    pull_at = float(g.uniform(0.18, 0.28))
    swoosh = noise(g, n, [bq_lowpass(420 * size ** 0.3, 0.7), bq_highpass(45, 0.7)])
    swoosh = 0.7 * swoosh + 0.5 * filt(swoosh, [bq_bandpass(float(g.uniform(160, 260)), 1.4)])
    e = env_swell(n, pull_at, 1.6, 0.16 * size)
    rec_at = pull_at + float(g.uniform(0.3, 0.4))
    e += 0.35 * np.exp(-(((_t(n) - rec_at) / 0.09) ** 2))
    x = swoosh * e
    x += bubble_cloud(g, n, 26.0, 1.4, 3.6, env=e, amp=0.5)
    x = filt(x, [bq_lowpass(bright, 0.6)])
    return x * np.minimum(1.0, _t(n) / 0.02)


def splash_air(g: np.random.Generator, size: float = 1.0) -> np.ndarray:
    """A body entering water, heard in the air: the cavity's whump, the sheet of spray, and droplets falling back."""
    n = _n(1.6)
    t = _t(n)
    f = 120.0 * (0.45 + 0.55 * np.exp(-t / 0.06))
    whump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.08 * size))
    spray = noise(g, n, [bq_highpass(450, 0.7), bq_lowpass(9000, 0.7)])
    spray *= np.clip(t / 0.004, 0, 1) * np.exp(-t / (0.13 * size))
    sheet = noise(g, n, [bq_bandpass(1400, 0.7)]) * env_swell(n, 0.05, 1.0, 0.25 * size)
    x = 0.9 * whump + 0.55 * spray + 0.35 * sheet
    for i in range(int(10 * size)):
        place(x, drip(float(g.uniform(0.3, 0.8)), float(g.uniform(1.5, 3.5)), seed=int(g.integers(1 << 30))),
              float(g.uniform(0.15, 1.1)), gain=2.0)
    return x * np.minimum(1.0, t / 0.0008)


def exhale(g: np.random.Generator, sec: float = 1.0) -> np.ndarray:
    """A long breath out through relaxed lips: unvoiced (no tone, no voice), a breathy /h/ into a soft /f/."""
    n = _n(sec + 0.2)
    t = _t(n)
    h = noise(g, n, [bq_bandpass(1300, 0.9), bq_peak(2500, 4.0, 1.5), bq_highpass(300, 0.7)])
    f_ = noise(g, n, [bq_highpass(2500, 0.7), bq_lowpass(7500, 0.7)])
    u = np.clip(t / sec, 0, 1)
    e = np.clip(t / 0.09, 0, 1) ** 1.5 * (1 - u) ** 1.2 * (1 + 0.12 * np.sin(2 * np.pi * 3.3 * t))
    return (0.8 * (1 - 0.6 * u) * h + 0.4 * (0.3 + 0.7 * u) * f_) * e


def finish(x: np.ndarray, target: float = SFX_TARGET, fade_s: float = 0.06) -> np.ndarray:
    k = min(len(x) // 3, _n(fade_s))
    x = x.copy()
    x[-k:] *= np.linspace(1, 0, k) ** 2
    x = filt(x, [bq_highpass(30, 0.7)])
    return normalize_momentary(x, target, ceiling_db=SFX_CEILING)


# --------------------------------------------------------------------------- diving SFX


def dive_entry() -> np.ndarray:
    g = rng(SEED + 10)
    n = _n(2.8)
    x = np.zeros(n)
    place(x, splash_air(g, 1.0), 0.0)
    t = _t(n)
    # under: the bubble cloud the body drags down, the rush past the ears, the pressure coming on
    cloud_env = np.clip((t - 0.08) / 0.05, 0, 1) * np.exp(-np.maximum(t - 0.13, 0) / 0.45)
    x += bubble_cloud(g, n, 420.0, 1.4, 7.0, env=cloud_env, amp=0.45)
    x += 0.5 * noise(g, n, [bq_lowpass(500, 0.7), bq_highpass(50, 0.7)]) * env_swell(n, 0.25, 1.2, 0.7)
    x += 0.25 * noise(g, n, [bq_lowpass(110, 0.7), bq_highpass(25, 0.7)]) * np.clip((t - 0.2) / 0.8, 0, 1)
    x = muffle(x, 11000.0, 1300.0, 0.14, 0.45)
    return finish(uw_room(x, SEED + 11, mix=0.32), fade_s=0.4)


def dive_surface() -> np.ndarray:
    g = rng(SEED + 20)
    n = _n(3.2)
    t = _t(n)
    brk = 0.7
    under = np.zeros(n)
    place(under, stroke(g, 1.2), 0.0, gain=0.8)
    up = np.clip(t / 0.3, 0, 1) * (t < brk)
    under += bubble_cloud(g, n, 160.0, 1.6, 5.0, env=up + 1e-3, amp=0.4) * (t < brk + 0.05)
    under = uw_room(under, SEED + 21, mix=0.3, tail=0.0)[:n]
    over = np.zeros(n)
    # the surface breaks: a sheet of water falls off the head and shoulders, then drips
    sheet = noise(g, n, [bq_highpass(700, 0.7), bq_lowpass(8500, 0.7)])
    over += 0.5 * sheet * np.clip((t - brk) / 0.03, 0, 1) * np.exp(-np.maximum(t - brk, 0) / 0.35) * (t >= brk)
    pour = noise(g, n, [bq_bandpass(900, 0.8)])
    over += 0.25 * pour * np.clip((t - brk) / 0.1, 0, 1) * np.exp(-np.maximum(t - brk, 0) / 0.6) * (t >= brk)
    for _ in range(14):
        place(over, drip(float(g.uniform(0.3, 0.9)), float(g.uniform(1.8, 4.0)), seed=int(g.integers(1 << 30))),
              brk + float(g.uniform(0.1, 2.0)) ** 1.3, gain=2.2)
    place(over, exhale(g, 1.1), brk + 0.28, gain=0.55)
    x = filt(under, [bq_lowpass(1300.0, 0.6), bq_lowpass(1700.0, 0.6)])
    x += muffle(over, 1600.0, 12000.0, brk - 0.02, brk + 0.12)
    return finish(air_room(x, SEED + 22), fade_s=0.3)


def dive_bubble_burst() -> np.ndarray:
    g = rng(SEED + 30)
    n = _n(1.4)
    t = _t(n)
    x = bubble_cloud(g, n, 600.0, 2.0, 10.0, env=np.exp(-t / 0.12) + 0.02 * np.exp(-t / 0.6), amp=0.5)
    place(x, bubble(15.0, 1.0, rise=0.25), 0.03, gain=0.9)
    place(x, bubble(11.0, 0.7, rise=0.3), 0.11, gain=0.8)
    x += 0.25 * noise(g, n, [bq_lowpass(380, 0.7), bq_highpass(50, 0.7)]) * env_swell(n, 0.03, 1.0, 0.15)
    x = filt(x, [bq_lowpass(2600, 0.6)])
    return finish(uw_room(x, SEED + 31, mix=0.3), fade_s=0.3)


def dive_stroke(v: int) -> np.ndarray:
    g = rng(SEED + 40 + v)
    x = stroke(g, (0.9, 1.0, 1.1, 0.95)[v], bright=1500.0)
    return finish(uw_room(x, SEED + 50 + v, mix=0.28, tail=0.6), target=STROKE_TARGET, fade_s=0.2)


def lantern_hum() -> np.ndarray:
    """6 s seamless mono loop: every partial and modulator is a whole number of cycles per loop."""
    g = rng(SEED + 60)
    L = _n(HUM_LOOP_S)
    t = _t(L)
    x = np.zeros(L)
    f1 = snap(98.0, L)
    for k, a in ((1, 1.0), (2, 0.55), (3, 0.3), (4, 0.16), (5, 0.08)):
        for split, w in ((0.0, 1.0), (snap(0.5, L), 0.6)):
            x += a * w * np.sin(2 * np.pi * (k * f1 + split) * t + float(g.uniform(0, 6.28)))
    x *= 1 + 0.07 * plfo(L, 3.0, g)  # the flame flickers
    flame = circ_noise(L, g, [bq_bandpass(220, 0.9), bq_lowpass(600, 0.7)]) * (0.6 + 0.4 * plfo(L, 4.0, g))
    x = 0.12 * x + 0.12 * flame
    X = np.fft.rfft(x)  # a periodic low-pass through the glass and the water (on the loop's own grid)
    f = np.fft.rfftfreq(L, 1 / SR)
    X *= 1 / np.sqrt(1 + (f / 700.0) ** 4)
    X[0] = 0
    x = np.fft.irfft(X, L)
    return normalize_integrated(x, HUM_TARGET, ceiling_db=BED_CEILING)


# --------------------------------------------------------------------------- beds


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=BEDS[name], preroll_s=9.0)
    return mx, mx.L


def creak_far(g: np.random.Generator) -> np.ndarray:
    """Something large and old settling far off: a slow stick-slip through low, wide wooden/iron modes."""
    c = stick_slip(g, float(g.uniform(1.6, 3.0)), 6, 28, [(85, 1.0), (150, 0.7), (240, 0.4), (410, 0.2)], q=4.0)
    return filt(c, [bq_lowpass(800, 0.7)])


def underwater_deep(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("underwater_deep")
    loop_s = BEDS["underwater_deep"]
    mx.bus("pressure", -6.0)
    mx.bus("hum", -16.0)
    mx.bus("creaks", -14.0, send=0.7)
    mx.bus("bubbles", -12.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(2400, 0.6)]))
    mx.bus("ticks", -30.0, send=0.3)
    swell = 0.5 + 0.5 * plfo(L, 0.06, g)
    mx.add("pressure", stereo_noise(L, g, [bq_lowpass(130, 0.6), bq_highpass(18, 0.7)], 0.7)
           * (0.75 + 0.25 * swell)[:, None], 0.0)
    tt = _t(L)
    hum = np.zeros(L)
    for f, a in ((snap(41.0, L), 1.0), (snap(41.4, L), 0.8), (snap(82.2, L), 0.35), (snap(123.0, L), 0.12)):
        hum += a * np.sin(2 * np.pi * f * tt + float(g.uniform(0, 6.28)))
    hum *= 0.7 + 0.3 * plfo(L, 0.05, g)
    mx.add("hum", np.stack([hum, np.roll(hum, 211)], axis=1), 0.0)
    for t in (4.0, 17.5, 31.0, 40.0):
        mx.add("creaks", creak_far(g), t + float(g.uniform(-1.0, 1.0)), pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.5, 1.0)))
    for t in schedule(L, 6.5, g, 0.3):
        tr = bubble_train(g, int(g.integers(6, 15)), 3.0, 8.0, (0.12, 0.35), amp=0.8, fade=0.5)
        mx.add("bubbles", tr, t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.35, 1.0)))
    for t in schedule(L, 0.7, g, 0.45):
        k = modal([float(g.uniform(2500, 4200))], [0.004], [1.0], 0.02, g, click=0.2)
        mx.add("ticks", k, t % loop_s, pan=float(g.uniform(-1, 1)), gain=float(g.uniform(0.2, 1.0)))
    verb = ModFDNReverb(rt60=3.0, rt60_high=0.8, predelay=0.05, size=2.0, mod_depth=8.0, mod_rate=0.25,
                        early_level=0.2, lowcut=40.0, highcut=2000.0, seed=SEED % 9973 + 1)
    return mx, verb


def underwater_tower(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("drowned_tower")
    loop_s = BEDS["drowned_tower"]
    mx.bus("current", -8.0, send=0.25)
    mx.bus("stone", -10.0, send=0.3)
    mx.bus("ticks", -20.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(2200, 0.7)]))
    mx.bus("leaks", -16.0, send=0.45, process=lambda x: filt(x, [bq_lowpass(2600, 0.6)]))
    mx.bus("groan", -12.0, send=0.6)
    surge = 0.5 + 0.5 * np.sin(2 * np.pi * snap(0.095, L) * _t(L) + 0.8) * (0.7 + 0.3 * plfo(L, 0.03, g))
    own = 0.5 + 0.5 * plfo(L, 0.2, g)
    cur = stereo_noise(L, g, [bq_lowpass(650, 0.6), bq_highpass(70, 0.7)], 0.45)
    mx.add("current", cur * (0.35 + 0.5 * surge ** 1.5 + 0.15 * own)[:, None], 0.0)
    # the shaft: a stone tube a few metres across rings at its own low modes when the current pushes through it
    exc = stereo_noise(L, g, [bq_lowpass(400, 0.7)], 0.6) * (0.4 + 0.6 * surge)[:, None]
    shaft = np.zeros((L, 2))
    for f, a in ((58.0, 1.0), (97.0, 0.8), (141.0, 0.6), (188.0, 0.4), (236.0, 0.3), (301.0, 0.18)):
        X = np.fft.rfft(exc, axis=0)
        fr = np.fft.rfftfreq(L, 1 / SR)
        bw = f / 14.0
        X *= (1 / (1 + ((fr - f) / bw) ** 2))[:, None]
        shaft += a * np.fft.irfft(X, L, axis=0)
    shaft /= np.abs(shaft).max() + 1e-12
    mx.add("stone", shaft, 0.0)
    for t in schedule(L, 7.5, g, 0.35):
        n_hits = int(g.integers(2, 5))
        for j in range(n_hits):
            base = float(g.uniform(500, 900))
            k = modal([base, base * 2.3, base * 3.9], [0.02, 0.012, 0.006], [1.0, 0.5, 0.25], 0.12, g, click=0.4)
            mx.add("ticks", k, (t + j * float(g.uniform(0.15, 0.45))) % loop_s, pan=float(g.uniform(-0.7, 0.7)),
                   gain=float(g.uniform(0.3, 1.0)) * (0.8 ** j))
    for t in schedule(L, 9.0, g, 0.3):
        tr = bubble_train(g, int(g.integers(4, 9)), 2.0, 4.0, (0.06, 0.16), amp=0.7, fade=0.4)
        mx.add("leaks", tr, t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.4, 1.0)))
    for t in (11.0, 32.0):
        c = stick_slip(g, float(g.uniform(2.2, 3.2)), 4, 16, [(62, 1.0), (118, 0.6), (190, 0.3)], q=3.0)
        mx.add("groan", filt(c, [bq_lowpass(500, 0.7)]), t, pan=float(g.uniform(-0.4, 0.4)))
    verb = ModFDNReverb(rt60=2.2, rt60_high=0.7, predelay=0.02, size=1.2, mod_depth=7.0, mod_rate=0.3,
                        early_level=0.35, lowcut=40.0, highcut=2500.0, seed=SEED % 9973 + 2)
    return mx, verb


BED_FNS = {"underwater_deep": underwater_deep, "drowned_tower": underwater_tower}
DIVE = {"dive_entry": dive_entry, "dive_surface": dive_surface, "dive_bubble_burst": dive_bubble_burst,
        **{f"dive_stroke_{v + 1}": (lambda i=v: dive_stroke(i)) for v in range(4)}}


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    g = rng(SEED + 101 * (list(BED_FNS).index(name) + 1))
    mx, verb = BED_FNS[name](g)
    _, loop = mx.render(reverb=verb, reverb_return_db=-3.0, hp_hz=16.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, BED_TARGET, ceiling_db=BED_CEILING, report=rep)
    L = len(loop)
    path = os.path.join(out_dir, "ambience", name + ".ogg")
    write_ogg(path, loop, quality=BED_QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.join(out_dir, "ambience", name + ".loop.json"), SR, 0, L, None, None)
    m = measure(loop)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS  "
              f"limited {100 * rep.get('fraction_limited', 0):.2f} %")
    return m


def render_hum(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    x = lantern_hum()
    L = len(x)
    path = os.path.join(out_dir, "sfx", "dive", "dive_lantern_hum.ogg")
    write_ogg(path, x, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(path)[0] + ".loop.json", SR, 0, L, None, None)
    m = measure(x)
    if verbose:
        print(f"dive_lantern_hum: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    res = {name: render_bed(name, out_dir, verbose) for name in BED_FNS}
    for name, fn in DIVE.items():
        x = fn()
        write_ogg(os.path.join(out_dir, "sfx", "dive", name + ".ogg"), x, quality=4.0)
        res[name] = measure(x)
        if verbose:
            print(f"{name}: {res[name]['seconds']:.2f}s  Mmax {res[name]['momentary_max_lufs']:.2f}  "
                  f"peak {res[name]['sample_peak_dbfs']:.2f}")
    res["dive_lantern_hum"] = render_hum(out_dir, verbose)
    return res


if __name__ == "__main__":
    render()
