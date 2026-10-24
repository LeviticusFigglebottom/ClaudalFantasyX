"""UI SFX for the M3 menus (M3-AUD-15): the Lattice board, Equip, the zone map, the tip card and the title screen.

All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio). In the
palette of ui_sfx.py and field_sfx.py (metallophone bars, soft air, a small room), so the new menus sound like the
same world. Mono, 44.1 kHz, Ogg Vorbis q4 (mix.md §5). UI bus: -20 LUFS momentary max, sample peaks <= -3 dBFS, so
the decoded true peak stays under -2.5 dBTP (tools/audio/targets.py "sfx/ui_*.ogg").

    ui_lattice_node     a Lattice node wakes: a small, padded bell (minor-third tierce, a warm hum under it) with a
                        bar an octave above as its glint, blooming in a room. The one UI sound meant to feel earned.
    ui_lattice_unlock   a gate opens (a path unlocked): a soft low kettle gong, a latch's dry click and three bars
                        rising D-A-D over an upward breath of air
    ui_lattice_step     the hero walks a path on the board: two soft, quick bar taps a third apart
    ui_equip            a piece worn: a clasp's small inharmonic click, a low bar and a cloth settle
    ui_unequip          a piece taken off: a lighter click, a bar falling a fourth and the cloth lifting
    ui_map_open         the map unrolls: a crackle of dry paper rising in band, then two bars a fifth apart
    ui_map_close        the map rolls up: the crackle shorter and falling, the bars falling
    ui_map_tick         the legend's cursor (the map rings a place): a tiny wooden tick with a paper flick
    ui_map_marker       a place set on the map with the pointer: a pin's muted tap and a small bell glint
    ui_tip              a tip card fades in: a soft glass ping (partials 1 : 2.76 with a slow beat) on a breath
    ui_title_confirm    the title's Begin / Continue: a low soft gong under a rolled D-A-D chord of bars, a longer room
    ui_title_swell      the title menu first appears: a slow pad swell (D-A-E, an open sonority, not a melody) with a
                        rubbed-glass tone fading in above it, about three seconds

Render:  python3 assets_src/sfx/menu_sfx.py   (or tools/audio/render_all.py --only menu_sfx)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.pad import pad_chord  # noqa: E402
from synth.reverb import FDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 7373
UI_TARGET = -20.0
UI_CEILING = -3.0


def _place(buf: np.ndarray, x: np.ndarray, t: float) -> None:
    s = int(t * SR)
    e = min(len(buf), s + len(x))
    if e > s:
        buf[s:e] += x[: e - s]


def _env(n_: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n_) / SR
    return np.clip(t / max(attack, 1e-4), 0, 1) * np.exp(-np.maximum(t - attack, 0) / decay)


def _noise(g, sec: float, sections, attack: float, decay: float) -> np.ndarray:
    k = int(sec * SR)
    return filt(g.standard_normal(k), sections) * _env(k, attack, decay)


def _air(g, sec: float, attack: float, decay: float, f: float = 2200.0) -> np.ndarray:
    return _noise(g, sec, [bq_bandpass(f, 0.7), bq_highpass(600, 0.7)], attack, decay)


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


def _crackle(g, sec: float, count: int, rate: float, lo: float, hi: float) -> np.ndarray:
    """Dry paper: short noise grains at a Poisson rate (`rate` per second, `count` at most), band-limited."""
    k = int(sec * SR)
    buf = np.zeros(k)
    times = np.cumsum(g.exponential(1.0 / rate, count))
    for t in times[times < sec * 0.92]:
        m = int(float(g.uniform(0.0004, 0.0025)) * SR)
        _place(buf, g.standard_normal(m) * np.hanning(m) * float(g.uniform(0.25, 1.0)), float(t))
    return filt(buf, [bq_highpass(lo, 0.7), bq_lowpass(hi, 0.7)])


def _sweep_noise(g, sec: float, f_from: float, f_to: float, q: float = 1.2, blocks: int = 24) -> np.ndarray:
    """Noise through a band-pass gliding from f_from to f_to (block-wise, crossfaded)."""
    k = int(sec * SR)
    src = g.standard_normal(k)
    out = np.zeros(k)
    edges = np.linspace(0, k, blocks + 1).astype(int)
    for i in range(blocks):
        f = f_from * (f_to / f_from) ** (i / max(blocks - 1, 1))
        y = filt(src, [bq_bandpass(f, q)])
        w = np.zeros(k)
        s, e = edges[i], edges[i + 1]
        w[s:e] = 1.0
        out += y * w
    return filt(out, [bq_lowpass(9000, 0.7)])


# --------------------------------------------------------------------------- Lattice


def ui_lattice_node() -> np.ndarray:
    g = rng(SEED + 101)
    buf = np.zeros(int(1.7 * SR))
    bell = tower_bell(n("A5"), 0.55, seed=SEED + 102, t60=1.5, dark=0.55)
    _place(buf, 0.8 * bell, 0.0)
    _place(buf, metallophone_note(n("A6"), 0.32, seed=SEED + 103, decay=0.9, hardness=0.35, ombak_hz=5.0), 0.012)
    _place(buf, 0.012 * _air(g, 0.6, 0.12, 0.25, 1600.0), 0.0)
    buf = filt(buf, [bq_highpass(220, 0.7), bq_peak(4800, -2.5, 1.0), bq_lowpass(9000, 0.7)])
    return _tail_fade(_room(buf, 1.1, 0.26, SEED + 104), 0.3)


def ui_lattice_unlock() -> np.ndarray:
    g = rng(SEED + 111)
    buf = np.zeros(int(1.5 * SR))
    _place(buf, 0.55 * kettle_gong(n("D4"), 0.3, seed=SEED + 112, t60=1.2), 0.0)
    latch = _modal([1450.0, 2630.0, 3900.0], [0.012, 0.007, 0.004], [1.0, 0.5, 0.25], 0.06, g)
    _place(buf, 0.35 * latch, 0.0)
    _place(buf, 0.03 * _sweep_noise(g, 0.5, 700.0, 3600.0) * _env(int(0.5 * SR), 0.3, 0.12), 0.02)
    for i, (note, vel) in enumerate((("D6", 0.42), ("A6", 0.46), ("D7", 0.4))):
        _place(buf, metallophone_note(n(note), vel, seed=SEED + 113 + i, decay=0.7, hardness=0.45, ombak_hz=6.0),
               0.09 + 0.075 * i)
    buf = filt(buf, [bq_highpass(160, 0.7), bq_peak(5200, -2.0, 1.0)])
    return _tail_fade(_room(buf, 0.9, 0.24, SEED + 117), 0.25)


def ui_lattice_step() -> np.ndarray:
    buf = np.zeros(int(0.36 * SR))
    _place(buf, metallophone_note(n("E6"), 0.28, seed=SEED + 121, decay=0.18, hardness=0.3, pair=False), 0.0)
    _place(buf, metallophone_note(n("G6"), 0.24, seed=SEED + 122, decay=0.16, hardness=0.3, pair=False), 0.07)
    buf = filt(buf, [bq_highpass(500, 0.7), bq_lowpass(7000, 0.7)])
    return _tail_fade(_room(buf, 0.35, 0.12, SEED + 123), 0.05)


# --------------------------------------------------------------------------- Equip


def ui_equip() -> np.ndarray:
    g = rng(SEED + 201)
    buf = np.zeros(int(0.5 * SR))
    clasp = _modal([1780.0, 2950.0, 4410.0, 6120.0], [0.02, 0.012, 0.008, 0.005], [1.0, 0.6, 0.35, 0.2], 0.1, g)
    _place(buf, 0.18 * clasp, 0.0)
    _place(buf, 0.06 * _noise(g, 0.14, [bq_bandpass(900, 0.8), bq_highpass(300, 0.7)], 0.02, 0.04), 0.0)
    _place(buf, metallophone_note(n("A5"), 0.4, seed=SEED + 202, decay=0.35, hardness=0.45, ombak_hz=5.0), 0.018)
    buf = filt(buf, [bq_highpass(260, 0.7)])
    return _tail_fade(_room(buf, 0.4, 0.14, SEED + 203), 0.06)


def ui_unequip() -> np.ndarray:
    g = rng(SEED + 211)
    buf = np.zeros(int(0.45 * SR))
    clasp = _modal([2100.0, 3380.0, 5020.0], [0.012, 0.008, 0.005], [1.0, 0.5, 0.25], 0.08, g)
    _place(buf, 0.13 * clasp, 0.0)
    _place(buf, 0.05 * _noise(g, 0.12, [bq_bandpass(1300, 0.8), bq_highpass(400, 0.7)], 0.03, 0.03), 0.01)
    _place(buf, metallophone_note(n("D6"), 0.32, seed=SEED + 212, decay=0.28, hardness=0.35, ombak_hz=5.0), 0.02)
    _place(buf, metallophone_note(n("A5"), 0.26, seed=SEED + 213, decay=0.28, hardness=0.3, ombak_hz=5.0), 0.085)
    buf = filt(buf, [bq_highpass(260, 0.7), bq_lowpass(6000, 0.7)])
    return _tail_fade(_room(buf, 0.35, 0.12, SEED + 214), 0.06)


# --------------------------------------------------------------------------- the zone map


def ui_map_open() -> np.ndarray:
    g = rng(SEED + 301)
    buf = np.zeros(int(0.85 * SR))
    k = int(0.32 * SR)
    paper = _crackle(g, 0.32, 90, 260.0, 1200.0, 7000.0) * np.linspace(0.4, 1.0, k) * _env(k, 0.02, 0.2)
    _place(buf, 0.35 * paper, 0.0)
    _place(buf, 0.02 * _sweep_noise(g, 0.32, 1200.0, 3200.0, 0.9) * _env(k, 0.12, 0.12), 0.0)
    _place(buf, metallophone_note(n("D6"), 0.36, seed=SEED + 302, decay=0.5, hardness=0.35, ombak_hz=6.0), 0.2)
    _place(buf, metallophone_note(n("A6"), 0.4, seed=SEED + 303, decay=0.5, hardness=0.35, ombak_hz=6.0), 0.27)
    buf = filt(buf, [bq_highpass(350, 0.7)])
    return _tail_fade(_room(buf, 0.5, 0.18, SEED + 304), 0.08)


def ui_map_close() -> np.ndarray:
    g = rng(SEED + 311)
    buf = np.zeros(int(0.55 * SR))
    k = int(0.2 * SR)
    paper = _crackle(g, 0.2, 60, 280.0, 1000.0, 5500.0) * np.linspace(1.0, 0.35, k)
    _place(buf, 0.3 * paper, 0.0)
    _place(buf, metallophone_note(n("A5"), 0.32, seed=SEED + 312, decay=0.32, hardness=0.3, ombak_hz=5.0), 0.1)
    _place(buf, metallophone_note(n("D5"), 0.28, seed=SEED + 313, decay=0.32, hardness=0.25, ombak_hz=5.0), 0.16)
    buf = filt(buf, [bq_highpass(250, 0.7), bq_lowpass(5000, 0.7)])
    return _tail_fade(_room(buf, 0.4, 0.15, SEED + 314), 0.06)


def ui_map_tick() -> np.ndarray:
    g = rng(SEED + 321)
    buf = np.zeros(int(0.15 * SR))
    tick = _modal([2350.0, 3720.0, 5600.0], [0.03, 0.015, 0.008], [1.0, 0.35, 0.15], 0.12, g)
    tick *= np.minimum(1.0, np.arange(len(tick)) / (0.0025 * SR))
    _place(buf, tick, 0.0)
    _place(buf, 0.08 * _noise(g, 0.02, [bq_highpass(3000, 0.7)], 0.001, 0.004), 0.0)
    return _tail_fade(filt(buf, [bq_highpass(800, 0.7)]), 0.02)


def ui_map_marker() -> np.ndarray:
    g = rng(SEED + 331)
    buf = np.zeros(int(0.65 * SR))
    pin = _modal([420.0, 1010.0, 1730.0], [0.03, 0.012, 0.007], [1.0, 0.4, 0.2], 0.12, g)
    _place(buf, 0.45 * pin, 0.0)
    _place(buf, 0.08 * _noise(g, 0.03, [bq_lowpass(2500, 0.7)], 0.0005, 0.006), 0.0)
    _place(buf, metallophone_note(n("B6"), 0.34, seed=SEED + 332, decay=0.45, hardness=0.5, ombak_hz=6.5), 0.03)
    buf = filt(buf, [bq_highpass(200, 0.7)])
    return _tail_fade(_room(buf, 0.45, 0.16, SEED + 333), 0.08)


# --------------------------------------------------------------------------- the tip card


def ui_tip() -> np.ndarray:
    g = rng(SEED + 401)
    k = int(0.8 * SR)
    t = np.arange(k) / SR
    f0 = midi_to_hz(n("F#6"))
    env = (1 - np.exp(-t / 0.012)) * np.exp(-t / 0.22)
    y = np.zeros(k)
    for r, a, beat in ((1.0, 1.0, 1.4), (2.76, 0.22, 2.1)):
        f = f0 * r
        y += a * (np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) + 0.5 * np.sin(2 * np.pi * (f + beat) * t))
    y *= env
    y += 0.006 * _air(g, 0.8, 0.03, 0.12, 3200.0)
    return _tail_fade(_room(filt(y, [bq_highpass(400, 0.7)]), 0.6, 0.22, SEED + 402), 0.1)


# --------------------------------------------------------------------------- the title screen


def ui_title_confirm() -> np.ndarray:
    g = rng(SEED + 501)
    buf = np.zeros(int(2.0 * SR))
    _place(buf, 0.6 * kettle_gong(n("D3"), 0.32, seed=SEED + 502, t60=1.8), 0.0)
    for i, (note, vel) in enumerate((("D5", 0.42), ("A5", 0.46), ("D6", 0.5), ("A6", 0.3))):
        _place(buf, metallophone_note(n(note), vel, seed=SEED + 503 + i, decay=1.2, hardness=0.4, ombak_hz=5.5),
               0.012 + 0.028 * i)
    _place(buf, 0.01 * _air(g, 0.5, 0.05, 0.2, 2000.0), 0.0)
    buf = filt(buf, [bq_highpass(110, 0.7), bq_lowpass(7500, 0.7)])
    return _tail_fade(_room(buf, 1.3, 0.28, SEED + 508), 0.35)


def ui_title_swell() -> np.ndarray:
    g = rng(SEED + 601)
    pad = pad_chord([n("D4"), n("A4"), n("E5")], 1.4, vel=0.45, seed=SEED + 602, attack=1.1, release=0.6)
    y = pad.mean(axis=1)
    k = int(3.2 * SR)
    y = np.pad(y, (0, max(0, k - len(y))))[:k]
    t = np.arange(k) / SR
    f0 = midi_to_hz(n("A5"))
    glass_env = np.clip((t - 0.5) / 1.0, 0, 1) ** 2 * np.exp(-np.maximum(t - 1.6, 0) / 0.7)
    glass = (np.sin(2 * np.pi * f0 * t + g.uniform(0, 6.28)) + 0.6 * np.sin(2 * np.pi * (f0 + 1.3) * t)
             + 0.2 * np.sin(2 * np.pi * f0 * 2.32 * t + g.uniform(0, 6.28)))
    peak = float(np.max(np.abs(y))) or 1.0
    y = y / peak + 0.18 * glass * glass_env
    y += 0.01 * _air(g, 3.2, 1.0, 0.8, 1800.0)
    y = filt(y, [bq_highpass(120, 0.7), bq_lowpass(6500, 0.7)])[:k]
    return _tail_fade(_room(y, 1.4, 0.25, SEED + 603), 0.6)


UI = {
    "ui_lattice_node": ui_lattice_node,
    "ui_lattice_unlock": ui_lattice_unlock,
    "ui_lattice_step": ui_lattice_step,
    "ui_equip": ui_equip,
    "ui_unequip": ui_unequip,
    "ui_map_open": ui_map_open,
    "ui_map_close": ui_map_close,
    "ui_map_tick": ui_map_tick,
    "ui_map_marker": ui_map_marker,
    "ui_tip": ui_tip,
    "ui_title_confirm": ui_title_confirm,
    "ui_title_swell": ui_title_swell,
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
