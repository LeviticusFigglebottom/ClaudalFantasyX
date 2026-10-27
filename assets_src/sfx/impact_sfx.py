"""Battle impact weight (M3-AUD-816): low layers by a blow's weight, and the KO slow-motion swell.

The human's playtest said battles looked primitive; battle-presentation's M3-BPR-401 added hit-stop, shake by
damage and a KO slow-mo (BattleImpact). These are the sounds ImpactAudio (game/audio/impact_audio.gd) layers on
BattleImpact's `landed` and `slowmo_planned`. The element hit itself stays BattleVfx's (battle_sfx.py): these sit
under it, mostly below 300 Hz, so a heavy blow is felt rather than heard twice. All synthesized here and in
tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio). Mono, 44.1 kHz, Ogg Vorbis q4
(mix.md §5), under assets/audio/sfx/battle/, on the Combat bus.

    impact_medium_1..3     a body blow: a short sub drop (75 -> 48 Hz) and a dull low-mid knock
    impact_heavy_1..3      a heavy blow: a deeper, longer sub drop (62 -> 34 Hz), a dry crack on the transient and a
                           short low room after it (it lands as the hit-stop releases)
    impact_crushing_1..2   the heaviest: the heavy blow with a grit of debris and a long low bloom
    ko_slowmo_1..2         the last foe falling in slow motion: the air drawn in and down (a band of noise sinking
                           from 2 kHz to 300 Hz), a sub swell under it, and one muffled heartbeat at its end
Loudness (momentary max; peaks <= -2 dBFS sample, so decoded true peaks stay <= -1 dBTP): medium -24, heavy -21,
crushing -19, slow-mo -20 LUFS. Combat SFX are -18 (mix.md §2), so each layer stays under the hit it supports.

Render:  python3 assets_src/sfx/impact_sfx.py   (or tools/audio/render_all.py --only impact_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from field_sfx import _env, _noise, _place, _room, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "battle")
SEED = 81600
CEILING = -2.0
TARGETS = {"medium": -24.0, "heavy": -21.0, "crushing": -19.0, "slowmo": -20.0}
VARIANTS = {"medium": 3, "heavy": 3, "crushing": 2, "slowmo": 2}


def _g(kind: str, v: int) -> np.random.Generator:
    return rng(SEED + 100 * list(TARGETS).index(kind) + v)


def _sub_drop(sec: float, f_from: float, f_to: float, decay: float) -> np.ndarray:
    """A sine whose pitch falls exponentially from f_from to f_to, with a fast attack and an exponential decay."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    f = f_to + (f_from - f_to) * np.exp(-t / (sec * 0.3))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return y * np.clip(t / 0.003, 0, 1) * np.exp(-t / decay)


def impact_medium(v: int) -> np.ndarray:
    g = _g("medium", v)
    sub = _sub_drop(0.32, float(g.uniform(70, 80)), float(g.uniform(45, 50)), 0.09)
    knock = _noise(g, 0.12, [bq_lowpass(float(g.uniform(900, 1300)), 0.8), bq_highpass(120, 0.7)], 0.002, 0.03)
    buf = np.zeros(int(0.4 * SR))
    _place(buf, sub, 0.0)
    _place(buf, knock * 0.6, 0.0)
    return _tail_fade(buf)


def _heavy(g: np.random.Generator, length: float) -> np.ndarray:
    sub = _sub_drop(length, float(g.uniform(58, 66)), float(g.uniform(32, 36)), length * 0.4)
    body = _noise(g, 0.25, [bq_lowpass(600, 0.9), bq_highpass(60, 0.7)], 0.002, 0.07) * 0.8
    crack = _noise(g, 0.03, [bq_bandpass(float(g.uniform(2200, 3000)), 1.3)], 0.0005, 0.006) * 0.5
    buf = np.zeros(int((length + 0.3) * SR))
    _place(buf, sub, 0.0)
    _place(buf, body, 0.0)
    _place(buf, crack, 0.0)
    wet = _room(filt(buf, [bq_lowpass(1500, 0.7)]), 0.6, 0.18, int(g.integers(1 << 30)))
    return wet[: len(buf)]


def impact_heavy(v: int) -> np.ndarray:
    return _tail_fade(_heavy(_g("heavy", v), 0.6))


def impact_crushing(v: int) -> np.ndarray:
    g = _g("crushing", v)
    y = _heavy(g, 1.0)
    debris = np.zeros_like(y)
    for _ in range(int(g.integers(18, 30))):
        k = int(0.008 * SR)
        grain = filt(g.standard_normal(k), [bq_bandpass(float(g.uniform(1500, 4000)), 1.5)]) * _env(k, 0.0005, 0.004)
        _place(debris, grain * float(g.uniform(0.1, 0.3)), float(g.uniform(0.04, 0.5)))
    bloom = filt(g.standard_normal(len(y)), [bq_lowpass(220, 0.7)]) * _env(len(y), 0.08, 0.5) * 0.35
    return _tail_fade(y + debris + bloom, 0.1)


def ko_slowmo(v: int) -> np.ndarray:
    """The air drawn in and down over 1.6 s, a sub swell under it, and one muffled heartbeat at the end."""
    g = _g("slowmo", v)
    sec = 1.9
    n = int(sec * SR)
    t = np.arange(n) / SR
    draw = 1.6
    # a band of noise whose centre sinks from 2 kHz to 300 Hz: filtered in short blocks so the band can move
    block = 512
    noise = g.standard_normal(n)
    air = np.zeros(n)
    for s in range(0, n, block):
        frac = min(s / SR / draw, 1.0)
        fc = 2000.0 * (300.0 / 2000.0) ** frac
        e = min(n, s + block * 4)
        seg = filt(noise[s:e], [bq_bandpass(fc, 1.6)])
        air[s: min(n, s + block)] += seg[: min(block, n - s)]
    swell = np.clip(t / draw, 0, 1) ** 1.6 * (t < draw) + (t >= draw) * np.exp(-(t - draw) / 0.06)
    sub = np.sin(2 * np.pi * np.cumsum(55.0 - 15.0 * np.clip(t / draw, 0, 1)) / SR) * swell * 0.7
    beat = _sub_drop(0.25, 70.0, 45.0, 0.07) * 0.9
    y = air * swell * 0.5 + sub
    _place(y, beat, draw + 0.02)
    return _tail_fade(y, 0.1)


SOURCES = {"medium": impact_medium, "heavy": impact_heavy, "crushing": impact_crushing, "slowmo": ko_slowmo}


def _name(kind: str, v: int) -> str:
    return f"ko_slowmo_{v + 1}" if kind == "slowmo" else f"impact_{kind}_{v + 1}"


def _todo() -> list[tuple]:
    return [(_name(k, v), (lambda f=SOURCES[k], i=v: f(i)), TARGETS[k]) for k in SOURCES for v in range(VARIANTS[k])]


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
