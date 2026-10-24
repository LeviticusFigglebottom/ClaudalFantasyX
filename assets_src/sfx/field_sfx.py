"""Field SFX (M2-AUD-05): footsteps by surface and the UI sounds of the new menus.

All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio).
Mono, 44.1 kHz, Ogg Vorbis q4 (mix.md §5).

Footsteps (World bus, -18 LUFS momentary max, peaks <= -1 dBFS), five variants per surface, each a heel strike
and a softer toe roll 50-100 ms later:
    step_sand_01..05   a low thump of sand giving way plus a short crunch of grains (Poisson noise grains)
    step_stone_01..05  a hard heel click, a sandal scuff, a small stone room
    step_wood_01..05   a heel on a plank (the board's modes ring briefly); two variants carry a small creak

UI (UI bus, -20 LUFS momentary max, peaks <= -3 dBFS), in the palette of ui_sfx.py (metallophone bars, soft air):
    ui_menu_open       two bars rising a fourth over a soft breath of air
    ui_menu_close      the same bars falling, softer and shorter
    ui_page            a page or tab switch: a soft paper swish and a tiny high tick
    ui_buy             coins: three small inharmonic chinks settling into a pouch (the shop's buy)
    ui_inn_rest        the inn's rest: a soft kettle gong with a fifth and an octave above it blooming in a room
                       (a sonority, not a tune: it is not derived from any existing melody)
    ui_error           denied: two muted low taps
    ui_vowbound_open   the Vowbound's menu: a soft glass tone (rubbed-rim partials 1 : 2.32 : 4.25 with a slow
                       beat), the one UI sound that swells instead of striking

Render:  python3 assets_src/sfx/field_sfx.py   (or tools/audio/render_all.py --only field_sfx)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import FDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 5151
STEP_TARGET = -18.0
STEP_CEILING = -1.6  # sample peak, so the decoded true peak stays under -1 dBTP (mix.md §2)
UI_TARGET = -20.0
UI_CEILING = -3.0
VARIANTS = 5


def _place(buf: np.ndarray, x: np.ndarray, t: float) -> None:
    s = int(t * SR)
    e = min(len(buf), s + len(x))
    buf[s:e] += x[: e - s]


def _env(n_: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n_) / SR
    return np.clip(t / max(attack, 1e-4), 0, 1) * np.exp(-np.maximum(t - attack, 0) / decay)


def _noise(g, sec: float, sections, attack: float, decay: float) -> np.ndarray:
    k = int(sec * SR)
    return filt(g.standard_normal(k), sections) * _env(k, attack, decay)


def _modal(freqs, decays, amps, sec: float, g) -> np.ndarray:
    k = int(sec * SR)
    t = np.arange(k) / SR
    y = sum(a * np.exp(-t / d) * np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) for f, d, a in zip(freqs, decays, amps))
    return y * np.minimum(1.0, t / 0.0006)


def _room(x: np.ndarray, rt60: float, mix: float, seed: int) -> np.ndarray:
    wet = FDNReverb(rt60=rt60, predelay=0.006, damping=0.35, size=0.45, early_level=0.2,
                    lowcut=300, highcut=8000, seed=seed).process(np.stack([x, x], 1), tail=0.0)
    return (1 - mix) * x + mix * wet.mean(axis=1)[: len(x)]


def _tail_fade(x: np.ndarray, sec: float = 0.02) -> np.ndarray:
    k = int(sec * SR)
    x[-k:] *= np.linspace(1, 0, k) ** 2
    return x


def _grains(g, sec: float, count: int, lo: float, hi: float, decay: float) -> np.ndarray:
    """Poisson-placed short noise grains, denser early and thinning out (sand grains shearing)."""
    k = int(sec * SR)
    buf = np.zeros(k)
    times = np.sort(g.exponential(decay, count))
    for t in times[times < sec * 0.9]:
        m = int(float(g.uniform(0.0003, 0.0015)) * SR)
        _place(buf, g.standard_normal(m) * np.hanning(m) * float(g.uniform(0.3, 1.0)), float(t))
    return filt(buf, [bq_highpass(lo, 0.7), bq_lowpass(hi, 0.7)])


# --------------------------------------------------------------------------- footsteps


def step_sand(v: int) -> np.ndarray:
    g = rng(SEED + 100 + v)
    buf = np.zeros(int(0.34 * SR))
    toe = float(g.uniform(0.06, 0.1))
    for t0, lvl in ((0.0, 1.0), (toe, 0.55)):
        _place(buf, lvl * 0.9 * _noise(g, 0.2, [bq_lowpass(260, 0.7), bq_highpass(50, 0.7)], 0.006, 0.04), t0)
        _place(buf, lvl * 0.5 * _grains(g, 0.16, int(g.integers(50, 90)), 900, 4200, 0.03), t0 + 0.002)
    return _tail_fade(filt(buf, [bq_lowpass(6000, 0.7)]))


def step_stone(v: int) -> np.ndarray:
    g = rng(SEED + 200 + v)
    buf = np.zeros(int(0.4 * SR))
    toe = float(g.uniform(0.07, 0.1))
    for t0, lvl in ((0.0, 1.0), (toe, 0.45)):
        click = _noise(g, 0.01, [bq_bandpass(float(g.uniform(2300, 3200)), 1.2), bq_highpass(900, 0.7)], 0.0003,
                       0.0015)
        knock = _modal([float(g.uniform(110, 140)), float(g.uniform(240, 290))], [0.02, 0.012], [1.0, 0.5], 0.08, g)
        _place(buf, lvl * 0.5 * click, t0)
        _place(buf, lvl * 0.7 * knock, t0)
    scuff = _noise(g, 0.08, [bq_bandpass(2600, 0.6), bq_highpass(1000, 0.7)], 0.012, 0.025)
    _place(buf, 0.3 * scuff, 0.012)
    return _tail_fade(_room(buf, 0.7, 0.14, SEED + 210 + v))


def step_wood(v: int) -> np.ndarray:
    g = rng(SEED + 300 + v)
    buf = np.zeros(int(0.45 * SR))
    base = float(g.uniform(0.92, 1.08))
    modes = [110 * base, 245 * base, 415 * base, 690 * base, 1060 * base]
    toe = float(g.uniform(0.07, 0.1))
    for t0, lvl in ((0.0, 1.0), (toe, 0.5)):
        hit = _modal(modes, [0.11, 0.07, 0.045, 0.03, 0.018], [1.0, 0.7, 0.45, 0.3, 0.18], 0.35, g)
        thud = _noise(g, 0.03, [bq_lowpass(1800, 0.7)], 0.0005, 0.004)
        _place(buf, lvl * hit, t0)
        _place(buf, lvl * 0.6 * thud, t0)
    if v in (2, 4):  # a board that gives a little
        k = int(0.12 * SR)
        t = np.arange(k) / SR
        ph = np.cumsum(40 + 50 * np.sin(np.pi * t / 0.12)) / SR
        imp = np.zeros(k)
        imp[np.nonzero(np.diff(np.floor(ph)) > 0)[0] + 1] = 1.0
        creak = filt(imp, [bq_bandpass(520 * base, 6.0)]) * np.sin(np.pi * t / 0.12)
        _place(buf, 0.35 * creak / (np.abs(creak).max() + 1e-9), toe + 0.04)
    return _tail_fade(filt(buf, [bq_highpass(60, 0.7)]))


# --------------------------------------------------------------------------- UI


def _air(g, sec: float, attack: float, decay: float, f: float = 2200.0) -> np.ndarray:
    return _noise(g, sec, [bq_bandpass(f, 0.7), bq_highpass(600, 0.7)], attack, decay)


def ui_menu_open() -> np.ndarray:
    g = rng(SEED + 401)
    buf = np.zeros(int(0.7 * SR))
    _place(buf, 0.02 * _air(g, 0.3, 0.06, 0.08), 0.0)
    _place(buf, metallophone_note(n("D6"), 0.45, seed=SEED + 402, decay=0.55, hardness=0.4, ombak_hz=6.0), 0.03)
    _place(buf, metallophone_note(n("G6"), 0.5, seed=SEED + 403, decay=0.5, hardness=0.4, ombak_hz=6.0), 0.085)
    buf = filt(buf, [bq_highpass(350, 0.7)])
    return _tail_fade(_room(buf, 0.5, 0.2, SEED + 404), 0.08)


def ui_menu_close() -> np.ndarray:
    g = rng(SEED + 411)
    buf = np.zeros(int(0.5 * SR))
    _place(buf, 0.015 * _air(g, 0.25, 0.01, 0.07, 1800.0), 0.0)
    _place(buf, metallophone_note(n("G5"), 0.4, seed=SEED + 412, decay=0.35, hardness=0.3, ombak_hz=5.0), 0.0)
    _place(buf, metallophone_note(n("D5"), 0.34, seed=SEED + 413, decay=0.35, hardness=0.25, ombak_hz=5.0), 0.06)
    buf = filt(buf, [bq_highpass(250, 0.7), bq_lowpass(4200, 0.7)])
    return _tail_fade(_room(buf, 0.4, 0.15, SEED + 414), 0.06)


def ui_page() -> np.ndarray:
    g = rng(SEED + 421)
    buf = np.zeros(int(0.22 * SR))
    swish = _noise(g, 0.12, [bq_bandpass(2800, 0.9), bq_highpass(1200, 0.7)], 0.025, 0.03)
    _place(buf, 0.05 * swish, 0.0)
    _place(buf, metallophone_note(n("A6"), 0.22, seed=SEED + 422, decay=0.14, hardness=0.5, pair=False), 0.03)
    return _tail_fade(filt(buf, [bq_highpass(600, 0.7)]))


def ui_buy() -> np.ndarray:
    g = rng(SEED + 431)
    buf = np.zeros(int(0.6 * SR))
    _place(buf, 0.25 * _noise(g, 0.05, [bq_lowpass(700, 0.7)], 0.002, 0.012), 0.0)  # the pouch
    ratios = (1.0, 1.68, 2.32, 2.93, 3.61)
    for t0, vel in ((0.01, 1.0), (0.062, 0.7), (0.128, 0.45)):
        f0 = float(g.uniform(2500, 3300))
        coin = _modal([f0 * r * float(g.uniform(0.99, 1.01)) for r in ratios], [0.32, 0.22, 0.16, 0.11, 0.08],
                      [1.0, 0.55, 0.5, 0.3, 0.2], 0.5, g)
        _place(buf, vel * coin, t0)
    return _tail_fade(_room(filt(buf, [bq_highpass(400, 0.7)]), 0.45, 0.15, SEED + 432), 0.06)


def ui_inn_rest() -> np.ndarray:
    buf = np.zeros(int(2.4 * SR))
    _place(buf, 0.9 * kettle_gong(n("D4"), 0.35, seed=SEED + 441, t60=2.0), 0.0)
    _place(buf, metallophone_note(n("A5"), 0.28, seed=SEED + 442, decay=1.6, hardness=0.25, ombak_hz=4.5), 0.18)
    _place(buf, metallophone_note(n("D6"), 0.22, seed=SEED + 443, decay=1.4, hardness=0.25, ombak_hz=4.5), 0.42)
    buf = filt(buf, [bq_highpass(140, 0.7), bq_lowpass(6000, 0.7)])
    return _tail_fade(_room(buf, 1.4, 0.3, SEED + 444), 0.3)


def ui_error() -> np.ndarray:
    g = rng(SEED + 451)
    buf = np.zeros(int(0.22 * SR))
    for t0, f, vel in ((0.0, 330.0, 1.0), (0.075, 300.0, 0.8)):
        tap = _modal([f, f * 2.4, f * 4.1], [0.025, 0.012, 0.006], [1.0, 0.35, 0.12], 0.1, g)
        _place(buf, vel * tap, t0)
        _place(buf, vel * 0.2 * _noise(g, 0.01, [bq_lowpass(2000, 0.7)], 0.0003, 0.002), t0)
    return _tail_fade(filt(buf, [bq_highpass(150, 0.7), bq_lowpass(2600, 0.7)]))


def ui_vowbound_open() -> np.ndarray:
    g = rng(SEED + 461)
    k = int(1.9 * SR)
    t = np.arange(k) / SR
    f0 = midi_to_hz(n("E5"))
    swell = (1 - np.exp(-t / 0.09)) * np.exp(-np.maximum(t - 0.18, 0) / 0.55)
    y = np.zeros(k)
    for r, a, beat in ((1.0, 1.0, 1.1), (2.32, 0.32, 1.7), (4.25, 0.1, 2.3)):
        f = f0 * r
        y += a * (np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) + 0.6 * np.sin(2 * np.pi * (f + beat) * t))
    y *= swell
    y += 0.004 * _air(g, 1.9, 0.08, 0.3, 3000.0)
    return _tail_fade(_room(filt(y, [bq_highpass(300, 0.7)]), 1.0, 0.3, SEED + 462), 0.25)


UI = {"ui_menu_open": ui_menu_open, "ui_menu_close": ui_menu_close, "ui_page": ui_page, "ui_buy": ui_buy,
      "ui_inn_rest": ui_inn_rest, "ui_error": ui_error, "ui_vowbound_open": ui_vowbound_open}
STEPS = {"sand": step_sand, "stone": step_stone, "wood": step_wood}


def outputs() -> list[str]:
    """Every file render() writes, in order (render_all.py's JOBS list)."""
    steps = [f"step_{s}_{v + 1:02d}.ogg" for s in STEPS for v in range(VARIANTS)]
    return steps + [f"{u}.ogg" for u in UI]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    res = {}
    todo = [(f"step_{s}_{v + 1:02d}", (lambda f=fn, i=v: f(i)), STEP_TARGET, STEP_CEILING)
            for s, fn in STEPS.items() for v in range(VARIANTS)]
    todo += [(name, fn, UI_TARGET, UI_CEILING) for name, fn in UI.items()]
    for name, fn, target, ceiling in todo:
        x = normalize_momentary(fn(), target, ceiling_db=ceiling)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS")
    return res


if __name__ == "__main__":
    render()
