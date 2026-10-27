"""Village and wildlife life in the field (M3-AUD-814): the villagers' talk and work, the gulls, crabs and fish.

The human's playtest said the slice's parts "look primitive": the villagers worked and chatted in silence and the
wildlife moved without a sound. These are the positional one-shots LifeAudio (game/audio/life_audio.gd) plays at
creatures' FieldNpc villagers and WildlifeLayer animals. All synthesized here and in tools/audio/synth/ (SPEC §2,
§9: no samples, no recordings, no generated audio), on field_ambience.py's and field_sfx.py's palette (its murmur
voice, gull voice, stick-slip creaks and struck-body modes), so the near sounds match the far beds. Mono, 44.1 kHz,
Ogg Vorbis q4 (mix.md §5). Files go to assets/audio/sfx/life/, on the World bus.

Villagers (-26 LUFS momentary max for talk, -25 for work; peaks <= -3 dBFS):
    villager_murmur_low_1..6, villager_murmur_high_1..6   one turn of a chat: vowel and nasal syllables on a falling
                          contour with everything over ~1 kHz gone, so it reads as voices, never as words
    work_net_1..4         mending a net: a twine rasp through the fingers, a knot pulled tight (a short creak)
    work_sweep_1..4       a palm broom's two strokes over a stone court
    work_wares_1..4       setting out a stall: a wooden bowl or a clay jar set down, a small knock or two
    work_bowl_1..4        a pestle worked round a clay bowl: a gritty circling scrape and the bowl's faint ring
Wildlife (gull calls -22, takeoff -26, crabs -30, fish -29 LUFS momentary max; peaks <= -3 dBFS):
    gull_call_near_1..6   a gull's call series close by (field_ambience's voice, brighter, less filtered)
    gull_takeoff_1..3     a gull lifting off: four to six wing claps slowing into the glide
    crab_scuttle_1..4     a crab bolting sideways over wet sand: a quick patter of tiny leg ticks
    fish_dart_1..3        a startled school flicking at the surface: tiny plips and a skitter of drops

Render:  python3 assets_src/sfx/life_sfx.py   (or tools/audio/render_all.py --only life_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from field_ambience import gull_call, modal, murmur_phrase, stick_slip  # noqa: E402
from field_sfx import _env, _noise, _place, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "life")
SEED = 81400
CEILING = -3.0
MURMUR_TARGET = -26.0
WORK_TARGET = -25.0
GULL_TARGET = -22.0
TAKEOFF_TARGET = -26.0
CRAB_TARGET = -30.0
FISH_TARGET = -29.0
MURMUR_VARIANTS = 6
WORK_VARIANTS = 4
GULL_VARIANTS = 6
TAKEOFF_VARIANTS = 3
CRAB_VARIANTS = 4
FISH_VARIANTS = 3


def _g(kind: str, v: int) -> np.random.Generator:
    return rng(SEED + 1000 * (sum(map(ord, kind)) % 97) + v)


# --------------------------------------------------------------------------- villagers


def murmur(v: int, high: bool) -> np.ndarray:
    """One turn of a chat, with a short breath before it (the turn starts on the breath, not mid-syllable)."""
    g = _g("murmur_high" if high else "murmur_low", v)
    y = murmur_phrase(g, high)
    pre = _noise(g, 0.18, [bq_bandpass(900, 0.8)], 0.06, 0.1) * 0.05
    return _tail_fade(np.concatenate([pre, y]), 0.08)


def work_net(v: int) -> np.ndarray:
    """Twine drawn through the fingers (a dry band-passed rasp with a slow grain), then a knot pulled tight."""
    g = _g("net", v)
    sec = float(g.uniform(1.1, 1.6))
    buf = np.zeros(int(sec * SR))
    pulls = int(g.integers(2, 4))
    for i in range(pulls):
        dur = float(g.uniform(0.18, 0.32))
        n = int(dur * SR)
        grain = 1 + 0.6 * np.sin(2 * np.pi * float(g.uniform(30, 55)) * np.arange(n) / SR)
        rasp = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(2600, 3400)), 1.4)]) * grain
        _place(buf, rasp * _env(n, 0.03, dur * 0.5) * float(g.uniform(0.5, 0.8)), 0.05 + i * float(g.uniform(0.26, 0.34)))
    knot = stick_slip(g, float(g.uniform(0.09, 0.14)), 180.0, 420.0, [(620.0, 5.0), (1450.0, 7.0)])
    _place(buf, knot * 0.9, sec - 0.3)
    return _tail_fade(buf)


def work_sweep(v: int) -> np.ndarray:
    """Two strokes of a palm broom: bristles brushed over stone, each a swell of hissing grit that sweeps downward."""
    g = _g("sweep", v)
    buf = np.zeros(int(1.5 * SR))
    for i in range(2):
        dur = float(g.uniform(0.38, 0.5))
        n = int(dur * SR)
        t = np.arange(n) / n
        hiss = np.zeros(n)
        for lo, hi, w in ((5200, 3600, 0.6), (2600, 1800, 0.4)):
            band = filt(g.standard_normal(n), [bq_bandpass((lo + hi) * 0.5, 0.9)])
            hiss += w * band * (1 - t * (lo - hi) / lo)
        grit = (g.random(n) < 0.004) * g.standard_normal(n) * 1.4
        stroke = (hiss + filt(grit, [bq_highpass(2500, 0.7)])) * np.sin(np.pi * t) ** 1.4
        _place(buf, stroke * float(g.uniform(0.7, 1.0)), 0.05 + i * float(g.uniform(0.55, 0.7)))
    return _tail_fade(buf)


def work_wares(v: int) -> np.ndarray:
    """A stall being set out: a wooden bowl or a clay jar set down on a board, then a smaller knock or two."""
    g = _g("wares", v)
    buf = np.zeros(int(1.2 * SR))
    clay = v % 2 == 1
    base = float(g.uniform(0.9, 1.15))
    freqs = [520 * base, 1310 * base, 2380 * base] if clay else [240 * base, 610 * base, 1180 * base]
    decays = [0.11, 0.06, 0.035] if clay else [0.05, 0.03, 0.018]
    hits = int(g.integers(2, 4))
    t = 0.04
    for i in range(hits):
        hit = modal(freqs, decays, [1.0, 0.5, 0.25], 0.35, g, click=0.6)
        _place(buf, hit * (1.0 if i == 0 else float(g.uniform(0.35, 0.6))), t)
        t += float(g.uniform(0.18, 0.34))
    scrape = _noise(g, 0.12, [bq_bandpass(1800, 1.2)], 0.01, 0.08) * 0.15
    _place(buf, scrape, 0.02)
    return _tail_fade(buf)


def work_bowl(v: int) -> np.ndarray:
    """A pestle worked round a clay bowl: a circling gritty scrape (louder on the far side of each turn) and the
    bowl's faint ring under it."""
    g = _g("bowl", v)
    sec = float(g.uniform(1.2, 1.7))
    n = int(sec * SR)
    t = np.arange(n) / SR
    turns = float(g.uniform(1.6, 2.4))
    circle = 0.55 + 0.45 * np.sin(2 * np.pi * turns * t / sec) ** 2
    grit = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(1900, 2500)), 1.1)])
    crunch = filt((g.random(n) < 0.01) * g.standard_normal(n), [bq_highpass(1500, 0.7)])
    ring = modal([880.0, 2150.0], [0.6, 0.3], [1.0, 0.4], sec, g)
    y = (0.8 * grit + 0.9 * crunch) * circle + 0.06 * ring[:n] * circle
    return _tail_fade(y * _env(n, 0.08, sec * 0.6), 0.1)


# --------------------------------------------------------------------------- wildlife


def gull_near(v: int) -> np.ndarray:
    """field_ambience's gull voice, heard close: the bright upper partials kept, a touch of the breath."""
    g = _g("gull", v)
    y = gull_call(g)
    return _tail_fade(filt(y, [bq_highpass(500, 0.7), bq_lowpass(6500, 0.7)]))


def gull_takeoff(v: int) -> np.ndarray:
    """A gull lifting off: wing claps, each a low thump of air with a feather hiss, slowing into a glide."""
    g = _g("takeoff", v)
    claps = int(g.integers(4, 7))
    buf = np.zeros(int(1.4 * SR))
    t = 0.03
    gap = float(g.uniform(0.11, 0.14))
    for i in range(claps):
        thump = _noise(g, 0.09, [bq_lowpass(420, 0.8)], 0.004, 0.05)
        hiss = _noise(g, 0.07, [bq_bandpass(3800, 0.9)], 0.003, 0.04) * 0.35
        w = 1.0 - 0.1 * i
        _place(buf, thump * w, t)
        _place(buf, hiss * w, t)
        t += gap
        gap *= float(g.uniform(1.08, 1.18))
    return _tail_fade(buf)


def crab_scuttle(v: int) -> np.ndarray:
    """A crab bolting sideways: a patter of tiny ticks (eight legs, a quick gait) over wet sand, fading as it goes."""
    g = _g("crab", v)
    sec = float(g.uniform(0.35, 0.55))
    buf = np.zeros(int((sec + 0.1) * SR))
    count = int(g.integers(14, 22))
    times = np.sort(g.uniform(0.0, sec, count))
    for k, at in enumerate(times):
        n = int(0.006 * SR)
        tick = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(4200, 6800)), 2.0)]) * _env(n, 0.0005, 0.004)
        _place(buf, tick * (1.0 - 0.6 * k / count) * float(g.uniform(0.6, 1.0)), float(at))
    wet = _noise(g, sec, [bq_bandpass(2400, 0.8)], 0.02, sec * 0.6) * 0.08
    _place(buf, wet, 0.0)
    return _tail_fade(buf)


def fish_dart(v: int) -> np.ndarray:
    """A school startled in the shallows: tiny surface plips and a skitter of drops within a quarter second."""
    g = _g("fish", v)
    buf = np.zeros(int(0.7 * SR))
    for _ in range(int(g.integers(5, 9))):
        at = float(g.uniform(0.0, 0.25))
        _place(buf, bubble(float(g.uniform(0.8, 1.6)), amp=float(g.uniform(0.3, 0.7))), at)
    for k in range(int(g.integers(3, 6))):
        _place(buf, drip(vel=float(g.uniform(0.3, 0.6)), radius_mm=float(g.uniform(1.2, 2.0)),
                         seed=int(g.integers(1 << 30))) * 0.5, float(g.uniform(0.02, 0.32)))
    flick = _noise(g, 0.05, [bq_highpass(3000, 0.7)], 0.002, 0.03) * 0.3
    _place(buf, flick, 0.0)
    return _tail_fade(buf)


# --------------------------------------------------------------------------- render


def _todo() -> list[tuple]:
    out = []
    for high in (False, True):
        for v in range(MURMUR_VARIANTS):
            name = f"villager_murmur_{'high' if high else 'low'}_{v + 1}"
            out.append((name, (lambda i=v, h=high: murmur(i, h)), MURMUR_TARGET))
    for kind, fn in (("net", work_net), ("sweep", work_sweep), ("wares", work_wares), ("bowl", work_bowl)):
        for v in range(WORK_VARIANTS):
            out.append((f"work_{kind}_{v + 1}", (lambda f=fn, i=v: f(i)), WORK_TARGET))
    for v in range(GULL_VARIANTS):
        out.append((f"gull_call_near_{v + 1}", (lambda i=v: gull_near(i)), GULL_TARGET))
    for v in range(TAKEOFF_VARIANTS):
        out.append((f"gull_takeoff_{v + 1}", (lambda i=v: gull_takeoff(i)), TAKEOFF_TARGET))
    for v in range(CRAB_VARIANTS):
        out.append((f"crab_scuttle_{v + 1}", (lambda i=v: crab_scuttle(i)), CRAB_TARGET))
    for v in range(FISH_VARIANTS):
        out.append((f"fish_dart_{v + 1}", (lambda i=v: fish_dart(i)), FISH_TARGET))
    return out


FILES = [f"{name}.ogg" for name, *_ in _todo()]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, fn, target in _todo():
        x = normalize_momentary(fn(), target, ceiling_db=CEILING)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS")
    return res


if __name__ == "__main__":
    render()
