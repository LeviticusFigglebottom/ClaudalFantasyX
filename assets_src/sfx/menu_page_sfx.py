"""UI SFX for the menus track's pages (M2-AUD-14): Items, Formation, Customize and the zone map's pan.

M3-AUD-15 (menu_sfx.py) covers Lattice, Equip, the map's open, close and ticks, the tip card and the title; this file
adds the sounds inside the other pages. All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no
recordings, no generated audio), from menu_sfx.py's own helpers and palette (metallophone bars on D-A-E, dry paper,
soft air, small modal clicks, a small room), so the pages sound like one set with the menus around them. Mono,
44.1 kHz, Ogg Vorbis q4 (mix.md §5). UI bus: -20 LUFS momentary max, sample peaks <= -3 dBFS, so the decoded true
peak stays under -2.5 dBTP (tools/audio/targets.py "sfx/ui_*.ogg").

    ui_item_use         an item used on a hero: a small glass vial's ping (1 : 2.32, a slow beat), three tiny bubble
                        chirps rising and a soft bar a fifth below settling under them
    ui_item_sort        the bag sorted another way: two quick paper flicks a moment apart and a tiny wooden tick
    ui_formation_pick   a hero lifted from their place: a cloth lifting (air rising in band) and one soft bar with
                        a faint glint an octave up
    ui_formation_swap   two heroes trade places: a soft footfall-like tap, a short air swish falling, and two bars
                        crossing (D6 down to A5 while A5 answers up to D6, a hair apart)
    ui_customize_open   Customize's recipes open on an empty slot: a soft low hum of a small bell, a bar and a short
                        breath rising, a workbench uncovered rather than a door
    ui_craft            an ability set into a piece: two small hammer taps (inharmonic, padded) and a bright bell glint
                        with a bar a fifth above it: a stone set, earned but small beside the Lattice node
    ui_map_pan          the zone map dragged: a soft paper slide, a short swell of band-passed grain with no pitch,
                        played as a sparse train while the map moves (its row's cooldown and volume_db keep it under
                        the cursor)

Render:  python3 assets_src/sfx/menu_page_sfx.py   (or tools/audio/render_all.py --only menu_page_sfx)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from menu_sfx import _air, _crackle, _env, _modal, _noise, _place, _room, _sweep_noise, _tail_fade  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 8484
UI_TARGET = -20.0
UI_CEILING = -3.0


def _glass(f0: float, sec: float, decay: float, g) -> np.ndarray:
    """A small glass ping: partials 1 and 2.32, each with a slowly beating twin."""
    k = int(sec * SR)
    t = np.arange(k) / SR
    y = np.zeros(k)
    for r, a, beat in ((1.0, 1.0, 1.1), (2.32, 0.25, 1.9)):
        f = f0 * r
        y += a * (np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) + 0.45 * np.sin(2 * np.pi * (f + beat) * t))
    return y * (1 - np.exp(-t / 0.004)) * np.exp(-t / decay)


def _bubble(f0: float, sec: float, g) -> np.ndarray:
    """A tiny bubble chirp: a sine gliding up about a quarter as it dies (a Minnaert bubble, very small)."""
    k = int(sec * SR)
    t = np.arange(k) / SR
    f = f0 * (1.0 + 0.25 * t / sec)
    ph = 2 * np.pi * np.cumsum(f) / SR + g.uniform(0, 6.28)
    return np.sin(ph) * np.minimum(1.0, t / 0.001) * np.exp(-t / (sec * 0.35))


# --------------------------------------------------------------------------- Items


def ui_item_use() -> np.ndarray:
    g = rng(SEED + 101)
    buf = np.zeros(int(0.95 * SR))
    _place(buf, 0.6 * _glass(midi_to_hz(n("A6")), 0.7, 0.16, g), 0.0)
    for i, (f, at) in enumerate(((1900.0, 0.05), (2400.0, 0.09), (2150.0, 0.14))):
        _place(buf, (0.16 - 0.03 * i) * _bubble(f, 0.03, g), at)
    _place(buf, metallophone_note(n("D6"), 0.3, seed=SEED + 102, decay=0.5, hardness=0.3, ombak_hz=5.0), 0.06)
    _place(buf, 0.008 * _air(g, 0.4, 0.04, 0.12, 2600.0), 0.0)
    buf = filt(buf, [bq_highpass(320, 0.7), bq_peak(5200, -2.0, 1.0), bq_lowpass(9000, 0.7)])
    return _tail_fade(_room(buf, 0.55, 0.2, SEED + 103), 0.12)


def ui_item_sort() -> np.ndarray:
    g = rng(SEED + 201)
    buf = np.zeros(int(0.32 * SR))
    for at, rate in ((0.0, 420.0), (0.07, 380.0)):
        k = int(0.06 * SR)
        flick = _crackle(g, 0.06, 24, rate, 1500.0, 7500.0) * _env(k, 0.008, 0.02)
        _place(buf, 0.32 * flick, at)
    tick = _modal([2600.0, 4100.0], [0.02, 0.01], [1.0, 0.3], 0.08, g)
    tick *= np.minimum(1.0, np.arange(len(tick)) / (0.002 * SR))
    _place(buf, 0.5 * tick, 0.12)
    buf = filt(buf, [bq_highpass(900, 0.7), bq_lowpass(8000, 0.7)])
    return _tail_fade(_room(buf, 0.25, 0.08, SEED + 202), 0.03)


# --------------------------------------------------------------------------- Formation


def ui_formation_pick() -> np.ndarray:
    g = rng(SEED + 301)
    buf = np.zeros(int(0.45 * SR))
    k = int(0.16 * SR)
    _place(buf, 0.04 * _sweep_noise(g, 0.16, 700.0, 2200.0, 1.0, 12) * _env(k, 0.06, 0.05), 0.0)
    _place(buf, metallophone_note(n("E6"), 0.34, seed=SEED + 302, decay=0.32, hardness=0.35, ombak_hz=5.5), 0.03)
    _place(buf, metallophone_note(n("E7"), 0.12, seed=SEED + 303, decay=0.18, hardness=0.3, pair=False), 0.035)
    buf = filt(buf, [bq_highpass(300, 0.7), bq_lowpass(8000, 0.7)])
    return _tail_fade(_room(buf, 0.35, 0.12, SEED + 304), 0.05)


def ui_formation_swap() -> np.ndarray:
    g = rng(SEED + 401)
    buf = np.zeros(int(0.6 * SR))
    tap = _modal([190.0, 470.0, 820.0], [0.03, 0.012, 0.006], [1.0, 0.35, 0.15], 0.1, g)
    _place(buf, 0.4 * tap, 0.0)
    _place(buf, 0.05 * _noise(g, 0.04, [bq_lowpass(1800, 0.7)], 0.001, 0.01), 0.0)
    k = int(0.14 * SR)
    _place(buf, 0.03 * _sweep_noise(g, 0.14, 2600.0, 1100.0, 1.1, 12) * _env(k, 0.05, 0.05), 0.01)
    _place(buf, metallophone_note(n("D6"), 0.32, seed=SEED + 402, decay=0.35, hardness=0.35, ombak_hz=5.0), 0.03)
    _place(buf, metallophone_note(n("A5"), 0.3, seed=SEED + 403, decay=0.35, hardness=0.3, ombak_hz=5.0), 0.045)
    _place(buf, metallophone_note(n("A5"), 0.24, seed=SEED + 404, decay=0.32, hardness=0.3, ombak_hz=5.0), 0.12)
    _place(buf, metallophone_note(n("D6"), 0.28, seed=SEED + 405, decay=0.32, hardness=0.35, ombak_hz=5.0), 0.135)
    buf = filt(buf, [bq_highpass(150, 0.7), bq_lowpass(7000, 0.7)])
    return _tail_fade(_room(buf, 0.4, 0.14, SEED + 406), 0.06)


# --------------------------------------------------------------------------- Customize


def ui_customize_open() -> np.ndarray:
    g = rng(SEED + 501)
    buf = np.zeros(int(0.75 * SR))
    _place(buf, 0.35 * tower_bell(n("A4"), 0.3, seed=SEED + 502, t60=0.8, dark=0.8), 0.0)
    k = int(0.3 * SR)
    _place(buf, 0.025 * _sweep_noise(g, 0.3, 900.0, 2800.0, 0.9, 16) * _env(k, 0.18, 0.08), 0.0)
    _place(buf, metallophone_note(n("E6"), 0.34, seed=SEED + 503, decay=0.45, hardness=0.35, ombak_hz=5.5), 0.06)
    buf = filt(buf, [bq_highpass(180, 0.7), bq_lowpass(7500, 0.7)])
    return _tail_fade(_room(buf, 0.5, 0.18, SEED + 504), 0.08)


def ui_craft() -> np.ndarray:
    g = rng(SEED + 601)
    buf = np.zeros(int(1.15 * SR))
    for i, at in enumerate((0.0, 0.085)):
        tap = _modal([1320.0, 2410.0, 3770.0, 5150.0], [0.025, 0.012, 0.007, 0.004], [1.0, 0.55, 0.3, 0.15], 0.1, g)
        tap *= np.minimum(1.0, np.arange(len(tap)) / (0.0015 * SR))
        _place(buf, (0.22 if i == 0 else 0.3) * tap, at)
    _place(buf, 0.06 * _noise(g, 0.02, [bq_bandpass(1800, 0.8)], 0.0005, 0.005), 0.085)
    _place(buf, 0.55 * tower_bell(n("E6"), 0.4, seed=SEED + 602, t60=0.9, dark=0.5), 0.1)
    _place(buf, metallophone_note(n("B6"), 0.3, seed=SEED + 603, decay=0.6, hardness=0.45, ombak_hz=6.0), 0.12)
    _place(buf, 0.01 * _air(g, 0.5, 0.08, 0.18, 2400.0), 0.08)
    buf = filt(buf, [bq_highpass(240, 0.7), bq_peak(5000, -2.5, 1.0), bq_lowpass(9000, 0.7)])
    return _tail_fade(_room(buf, 0.75, 0.22, SEED + 604), 0.2)


# --------------------------------------------------------------------------- the zone map


def ui_map_pan() -> np.ndarray:
    g = rng(SEED + 701)
    k = int(0.18 * SR)
    t = np.arange(k) / SR
    swell = np.sin(np.pi * np.clip(t / 0.15, 0, 1)) ** 2
    grain = filt(g.standard_normal(k), [bq_bandpass(1700.0, 0.9), bq_highpass(700, 0.7), bq_lowpass(5000, 0.7)])
    paper = _crackle(g, 0.18, 8, 60.0, 1400.0, 5000.0)
    y = (grain + 0.25 * paper) * swell
    return _tail_fade(y, 0.02)


UI = {
    "ui_item_use": ui_item_use,
    "ui_item_sort": ui_item_sort,
    "ui_formation_pick": ui_formation_pick,
    "ui_formation_swap": ui_formation_swap,
    "ui_customize_open": ui_customize_open,
    "ui_craft": ui_craft,
    "ui_map_pan": ui_map_pan,
}


def outputs() -> list[str]:
    """Every file render() writes, in order (render_all.py's JOBS list)."""
    return [f"{u}.ogg" for u in UI]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    res = {}
    for name, fn in UI.items():
        x = normalize_momentary(fn(), UI_TARGET, ceiling_db=UI_CEILING)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS  true peak {m['true_peak_dbtp']:.2f} dBTP")
    return res


if __name__ == "__main__":
    render()
