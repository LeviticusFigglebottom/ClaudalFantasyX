"""Act II's three new footstep surfaces (M4-A2P-093; ADR 0204 §11; plain git, ADR 0175).

Built exactly as hero_foley.py builds Act I's sand, stone, wood and water steps (its heel-and-toe gait, grains,
struck-body modes, twist and small room), so the new grounds sit with the old ones. FootstepAudio plays them on the
World bus at the feet, by footsteps.json `surfaces`; env-art marks the ground in the Act II kits.

    root    Ch10, the mangrove root-walks over tannin water: wet, hollow living wood. The heel's dull knock is damped
            by the wet, the sole squelches on the slick bark, and a root gives a little under weight; a run flicks
            drops off the roots.
    snow    Ch12, snow on the pass and the Ram's shelf: the crust breaking under the heel, the packed snow's squeak as
            it compresses, a soft low thud; a run kicks loose snow. (ADR 0015: snow is weather, never ice.)
    slate   Ch12, Keth Pass and Quellan's cut slate: thin hard plates, a brighter, shorter tick than Act I's stone, a
            plate that rocks once under the toe, and grit.

Steps -18 LUFS momentary max (six variants per gait), stops -20 and turns -21 (two variants each), the rules of
hero_foley.py. Mono, Ogg Vorbis q4, under assets/audio/act2/sfx/foley/. Synthesized (SPEC §2, §9).

Render:  python3 tools/audio/render_all.py --only act2_hero_foley
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import hero_foley as H  # noqa: E402
from field_ambience import stick_slip  # noqa: E402
from field_sfx import _grains, _modal, _noise, _place, _room, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "sfx", "foley")
SEED = 86500
SURFACES = ("root", "snow", "slate")


# --------------------------------------------------------------------------- steps


def step_root(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 100 + v + (50 if run else 0))
    p = H._gait(run)
    buf = np.zeros(int(0.5 * SR))
    base = float(g.uniform(0.85, 1.1))
    modes = [85 * base, 190 * base, 340 * base, 560 * base]       # a living root: lower and deader than a plank
    toe = float(g.uniform(*p["roll"]))
    for t0, lvl in ((0.0, p["heel"]), (toe, p["toe"])):
        _place(buf, lvl * 0.9 * _modal(modes, [0.05, 0.03, 0.02, 0.012], [1.0, 0.6, 0.3, 0.15], 0.25, g), t0)
        squelch = _noise(g, 0.09, [bq_bandpass(float(g.uniform(500, 800)), 1.0), bq_lowpass(1600, 0.7)], 0.004, 0.03)
        _place(buf, lvl * 0.55 * squelch, t0 + 0.005)
    for _ in range(int(g.integers(1, 4))):                         # the wet bark under the sole
        _place(buf, bubble(float(g.uniform(2.0, 4.0)), float(g.uniform(0.05, 0.12)), rise=0.08),
               float(g.uniform(0.01, toe + 0.05)))
    if v in (2, 5):                                                # a root that gives a little
        _place(buf, 0.3 * stick_slip(g, 0.14, 30.0, 80.0, [(380 * base, 1.0), (900 * base, 0.4)], q=6.0), toe + 0.03)
    if run:                                                        # drops flicked off the roots
        for _ in range(int(g.integers(2, 4))):
            d = drip(float(g.uniform(0.3, 0.5)), float(g.uniform(1.5, 2.5)), seed=int(g.integers(1 << 30)))
            _place(buf, 0.25 * d, float(g.uniform(toe + 0.08, toe + 0.25)))
    return _tail_fade(filt(buf, [bq_highpass(50, 0.7), bq_lowpass(7000, 0.7)]))


def step_snow(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 200 + v + (50 if run else 0))
    p = H._gait(run)
    buf = np.zeros(int(0.45 * SR))
    toe = float(g.uniform(*p["roll"]))
    for t0, lvl in ((0.0, p["heel"]), (toe, p["toe"])):
        _place(buf, lvl * 0.7 * _noise(g, 0.16, [bq_lowpass(220, 0.7), bq_highpass(40, 0.7)], 0.006, 0.04), t0)
        crunch = _grains(g, 0.14, int(g.integers(70, 110) * p["grit"]), 1500, 6500, 0.03)   # the crust breaking
        _place(buf, lvl * 0.6 * crunch, t0 + 0.003)
        squeak = stick_slip(g, 0.07, 280.0, 520.0, [(1100.0, 1.0), (2400.0, 0.35)], q=5.0)  # packed snow squeaking
        _place(buf, lvl * 0.25 * squeak, t0 + 0.02)
    if run:                                                        # loose snow kicked off the toe
        _place(buf, 0.2 * H._scatter(g, 0.3, int(g.integers(10, 18)), 1800, 6000, 0.0, 0.15), toe + 0.05)
    return _tail_fade(filt(buf, [bq_lowpass(7000, 0.7)]))


def step_slate(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 300 + v + (50 if run else 0))
    p = H._gait(run)
    buf = np.zeros(int(0.42 * SR))
    toe = float(g.uniform(*p["roll"]))
    plate = [float(g.uniform(640, 820)), float(g.uniform(1500, 1800)), float(g.uniform(2700, 3200))]
    for t0, lvl in ((0.0, p["heel"]), (toe, p["toe"] * 0.8)):
        click = _noise(g, 0.008, [bq_bandpass(float(g.uniform(3000, 4000)), 1.3), bq_highpass(1200, 0.7)], 0.0003,
                       0.0012)
        _place(buf, lvl * 0.2 * click, t0)   # kept low: the click alone would hit the peak ceiling first
        _place(buf, lvl * 0.6 * _modal(plate, [0.02, 0.012, 0.006], [1.0, 0.5, 0.25], 0.08, g), t0)
        _place(buf, lvl * 0.5 * _modal([float(g.uniform(130, 160))], [0.015], [1.0], 0.05, g), t0)  # the rock below
    if v in (0, 3):                                                # a plate rocking once under the toe
        _place(buf, 0.3 * _modal(plate[:2], [0.01, 0.006], [1.0, 0.4], 0.05, g), toe + 0.045)
    scuff = _noise(g, 0.1 if run else 0.08, [bq_bandpass(3000, 0.6), bq_highpass(1200, 0.7)], 0.01, 0.03)
    _place(buf, (0.45 if run else 0.35) * scuff, 0.012)  # the sole dragging on the plate, as the stone step's
    grit = _grains(g, 0.1, int(g.integers(10, 20) * p["grit"]), 2800, 8000, 0.02)
    _place(buf, 0.25 * p["grit"] * grit, 0.004)
    return _tail_fade(filt(_room(buf, 0.6, 0.12, SEED + 310 + v + (50 if run else 0)), [bq_lowpass(9500, 0.7)]))


STEPS = {"root": step_root, "snow": step_snow, "slate": step_slate}


# --------------------------------------------------------------------------- halts and turns


def stop_root(v: int) -> np.ndarray:
    g = rng(SEED + 500 + v)
    buf = np.zeros(int(0.55 * SR))
    _place(buf, 0.7 * _modal([85, 190, 340], [0.05, 0.03, 0.02], [1.0, 0.6, 0.3], 0.25, g), 0.0)
    _place(buf, 0.5 * _noise(g, 0.2, [bq_bandpass(600, 0.8), bq_lowpass(1500, 0.7)], 0.02, 0.06), 0.01)  # a slide
    _place(buf, 0.35 * stick_slip(g, 0.2, 30.0, 70.0, [(360.0, 1.0), (850.0, 0.35)], q=6.0), 0.1)
    return _tail_fade(filt(buf, [bq_highpass(50, 0.7)]))


def stop_snow(v: int) -> np.ndarray:
    g = rng(SEED + 510 + v)
    buf = np.zeros(int(0.5 * SR))
    _place(buf, 0.6 * _grains(g, 0.3, int(g.integers(120, 170)), 1500, 6000, 0.08), 0.0)   # sliding to a halt
    _place(buf, 0.6 * _noise(g, 0.15, [bq_lowpass(220, 0.7)], 0.006, 0.04), float(g.uniform(0.15, 0.2)))
    _place(buf, 0.25 * stick_slip(g, 0.1, 260.0, 480.0, [(1100.0, 1.0), (2400.0, 0.3)], q=5.0), 0.18)
    return _tail_fade(filt(buf, [bq_lowpass(6500, 0.7)]))


def stop_slate(v: int) -> np.ndarray:
    g = rng(SEED + 520 + v)
    buf = np.zeros(int(0.5 * SR))
    _place(buf, 0.5 * _noise(g, 0.18, [bq_bandpass(float(g.uniform(2600, 3300)), 0.9), bq_highpass(1000, 0.7)],
                             0.015, 0.05), 0.0)
    _place(buf, 0.35 * _grains(g, 0.18, int(g.integers(25, 40)), 2800, 8000, 0.05), 0.01)
    plate = [float(g.uniform(640, 820)), float(g.uniform(1500, 1800))]
    _place(buf, 0.55 * _modal(plate, [0.012, 0.007], [1.0, 0.5], 0.06, g), float(g.uniform(0.14, 0.2)))
    return _tail_fade(_room(buf, 0.6, 0.12, SEED + 525 + v))


def turn_root(v: int) -> np.ndarray:
    g = rng(SEED + 600 + v)
    buf = np.zeros(int(0.4 * SR))
    _place(buf, 0.5 * H._twist(g, 0.16, 500, 900, 1.0), 0.0)                 # the sole twisting on wet bark
    _place(buf, 0.4 * stick_slip(g, 0.12, 80.0, 200.0, [(700.0, 1.0), (1500.0, 0.4)], q=8.0), 0.02)
    _place(buf, bubble(3.0, 0.08, rise=0.08), 0.05)
    return _tail_fade(filt(buf, [bq_highpass(60, 0.7)]))


def turn_snow(v: int) -> np.ndarray:
    g = rng(SEED + 610 + v)
    buf = np.zeros(int(0.35 * SR))
    _place(buf, 0.35 * H._twist(g, 0.16, 1500, 2600, 1.2), 0.0)
    _place(buf, 0.6 * _grains(g, 0.2, int(g.integers(60, 90)), 1500, 6000, 0.06), 0.0)
    _place(buf, 0.3 * stick_slip(g, 0.08, 300.0, 520.0, [(1200.0, 1.0)], q=5.0), 0.03)
    return _tail_fade(buf)


def turn_slate(v: int) -> np.ndarray:
    g = rng(SEED + 620 + v)
    buf = np.zeros(int(0.35 * SR))
    _place(buf, 0.6 * H._twist(g, 0.14, 2200, 3800, 1.6), 0.0)
    _place(buf, 0.3 * _grains(g, 0.15, int(g.integers(20, 35)), 2800, 8000, 0.04), 0.005)
    return _tail_fade(_room(buf, 0.6, 0.12, SEED + 625 + v))


STOPS = {"root": stop_root, "snow": stop_snow, "slate": stop_slate}
TURNS = {"root": turn_root, "snow": turn_snow, "slate": turn_slate}


def _todo() -> list[tuple]:
    out = []
    for s, fn in STEPS.items():
        for gait in H.GAITS:
            for v in range(H.STEP_VARIANTS):
                out.append((f"step_{s}_{gait}_{v + 1:02d}", (lambda f=fn, i=v, r=gait == "run": f(i, r)),
                            H.STEP_TARGET, H.STEP_CEILING))
    for s in SURFACES:
        for v in range(H.SCUFF_VARIANTS):
            out.append((f"stop_{s}_{v + 1}", (lambda f=STOPS[s], i=v: f(i)), H.STOP_TARGET, H.STEP_CEILING))
            out.append((f"turn_{s}_{v + 1}", (lambda f=TURNS[s], i=v: f(i)), H.TURN_TARGET, H.STEP_CEILING))
    return out


FILES = [f"{name}.ogg" for name, *_ in _todo()]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, fn, target, ceiling in _todo():
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
