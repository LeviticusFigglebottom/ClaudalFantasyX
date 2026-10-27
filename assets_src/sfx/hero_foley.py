"""Hero footsteps and movement foley (M3-AUD-802): the real field heroes, keyed to their clips' foot contacts.

All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio), on
field_sfx.py's helpers and palette (its heel-and-toe envelope, Poisson grains, struck-body modes and small stone
room), so the new steps sit with the old ones. Mono, 44.1 kHz, Ogg Vorbis q4 (mix.md §5). Files go to
assets/audio/sfx/foley/; FootstepAudio (game/audio/footstep_audio.gd) plays them on the World bus at the feet.

Steps (-18 LUFS momentary max, peaks <= -1 dBTP), six variants per surface and gait. Each is a heel strike and a
toe roll. A run lands the heel harder, rolls to the toe sooner and kicks off with more grit or spray:
    step_sand_{walk,run}_01..06    a low thump of sand giving way and a crunch of grains; a run throws grains after
    step_stone_{walk,run}_01..06   a heel click, the knock of the slab, a sandal scuff; a run adds grit under the sole
    step_wood_{walk,run}_01..06    a heel on a plank (its modes ring briefly), two variants per gait creak
    step_water_{walk,run}_01..06   wading in shallow water: the slap of the foot, the cavity's plunk, bubbles,
                                   drops falling back and the drag of the lifted foot; a run sprays more
Halts and turns (stop -20, turn -21 LUFS momentary max), two variants per surface:
    stop_<surface>_1..2   the hero plants and settles: grains sliding, a sandal scrape, a plank settling with a
                          creak, water sloshing round the ankles
    turn_<surface>_1..2   a pivot on the ball of the foot: a twisting scuff, a grinding scrape, a plank's squeak,
                          a swirl
Foley, layered on the steps at low level (-24 LUFS momentary max, peaks <= -3 dBFS), four variants each:
    cloth_walk_1..4, cloth_run_1..4   a tunic and sleeves swishing with the stride (a run: two quicker flaps)
    gear_lantern_1..4    Rhen's brass lantern on his hip: the cage's small inharmonic clink, the bail's rattle and
                         a faint ring of the glass
    gear_shells_1..4     Asha's bell-shells: three or four tiny shell clicks settling
    gear_leather_1..4    Toma's belt and scabbard: a leather creak and a buckle tick

Render:  python3 assets_src/sfx/hero_foley.py   (or tools/audio/render_all.py --only hero_foley)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from field_ambience import stick_slip  # noqa: E402
from field_sfx import STEP_TARGET, _env, _grains, _modal, _noise, _place, _room, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "foley")
SEED = 80200
STOP_TARGET = -20.0
TURN_TARGET = -21.0
FOLEY_TARGET = -24.0
FOLEY_CEILING = -3.0
STEP_CEILING = -2.2  # sample peak: the run heels decode up to 0.9 dB over it, so this keeps them under -1 dBTP
STEP_VARIANTS = 6
SCUFF_VARIANTS = 2
FOLEY_VARIANTS = 4
SURFACES = ("sand", "stone", "wood", "water")
GAITS = ("walk", "run")
GEAR = ("lantern", "shells", "leather")


def _gait(run: bool) -> dict:
    """How a run differs from a walk: a heavier heel, a quicker roll to the toe, more grit or spray."""
    if run:
        return {"heel": 1.0, "toe": 0.7, "roll": (0.04, 0.06), "grit": 1.8, "kick": 1.0}
    return {"heel": 0.8, "toe": 0.55, "roll": (0.065, 0.1), "grit": 1.0, "kick": 0.0}


def _scatter(g, sec: float, count: int, lo: float, hi: float, at: float, spread: float) -> np.ndarray:
    """A few grains thrown by the push-off, spread over `spread` seconds from `at`, then landing."""
    k = int(sec * SR)
    buf = np.zeros(k)
    for t in np.sort(g.uniform(at, at + spread, count)):
        m = int(float(g.uniform(0.0004, 0.0012)) * SR)
        _place(buf, g.standard_normal(m) * np.hanning(m) * float(g.uniform(0.2, 0.7)), float(t))
    return filt(buf, [bq_highpass(lo, 0.7), bq_lowpass(hi, 0.7)])


# --------------------------------------------------------------------------- steps


def step_sand(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 100 + v + (50 if run else 0))
    p = _gait(run)
    buf = np.zeros(int(0.42 * SR))
    toe = float(g.uniform(*p["roll"]))
    for t0, lvl in ((0.0, p["heel"]), (toe, p["toe"])):
        thump = _noise(g, 0.2, [bq_lowpass(240 if run else 270, 0.7), bq_highpass(45, 0.7)], 0.005, 0.045)
        _place(buf, lvl * 0.95 * thump, t0)
        grains = _grains(g, 0.18, int(g.integers(55, 95) * p["grit"]), 900, 4600 if run else 4000, 0.032)
        _place(buf, lvl * 0.5 * grains, t0 + 0.002)
    if run:  # the push-off throws sand that patters back down
        _place(buf, 0.22 * _scatter(g, 0.3, int(g.integers(14, 24)), 1500, 6000, 0.0, 0.18), toe + 0.05)
    return _tail_fade(filt(buf, [bq_lowpass(6500, 0.7)]))


def step_stone(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 200 + v + (50 if run else 0))
    p = _gait(run)
    buf = np.zeros(int(0.42 * SR))
    toe = float(g.uniform(*p["roll"]))
    for t0, lvl in ((0.0, p["heel"]), (toe, p["toe"] * 0.8)):
        click = _noise(g, 0.01, [bq_bandpass(float(g.uniform(2300, 3300)), 1.2), bq_highpass(900, 0.7)], 0.0003,
                       0.0015)
        knock = _modal([float(g.uniform(105, 140)), float(g.uniform(235, 295)), float(g.uniform(520, 640))],
                       [0.022, 0.013, 0.007], [1.0, 0.5, 0.2], 0.09, g)
        _place(buf, lvl * 0.5 * click, t0)
        _place(buf, lvl * (0.8 if run else 0.7) * knock, t0)
    scuff = _noise(g, 0.1 if run else 0.08, [bq_bandpass(2600, 0.6), bq_highpass(1000, 0.7)], 0.01, 0.03)
    _place(buf, (0.42 if run else 0.3) * scuff, 0.012)
    grit = _grains(g, 0.12, int(g.integers(12, 22) * p["grit"]), 2500, 7500, 0.025)  # sand on the slab
    _place(buf, 0.25 * p["grit"] * grit, 0.004)
    # the click is the sharpest transient here: rounding its top keeps the decoded true peak under the ceiling
    return _tail_fade(filt(_room(buf, 0.7, 0.14, SEED + 210 + v + (50 if run else 0)), [bq_lowpass(9000, 0.7)]))


def step_wood(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 300 + v + (50 if run else 0))
    p = _gait(run)
    buf = np.zeros(int(0.48 * SR))
    base = float(g.uniform(0.9, 1.1))
    modes = [110 * base, 245 * base, 415 * base, 690 * base, 1060 * base]
    toe = float(g.uniform(*p["roll"]))
    for t0, lvl in ((0.0, p["heel"]), (toe, p["toe"])):
        hit = _modal(modes, [0.11, 0.07, 0.045, 0.03, 0.018], [1.0, 0.7, 0.45, 0.3, 0.18], 0.36, g)
        thud = _noise(g, 0.03, [bq_lowpass(1600 if run else 1800, 0.7)], 0.0005, 0.005 if run else 0.004)
        _place(buf, lvl * hit, t0)
        _place(buf, lvl * (0.8 if run else 0.6) * thud, t0)
    if run:  # the next board along answers, a little later and duller
        rattle = _modal([m * 1.13 for m in modes[:3]], [0.04, 0.025, 0.015], [0.6, 0.4, 0.2], 0.12, g)
        _place(buf, 0.3 * rattle, 0.018)
    if v in (1, 4):  # a board that gives a little
        creak = stick_slip(g, 0.12, 40.0, 95.0, [(520 * base, 1.0), (1180 * base, 0.4)], q=6.0)
        _place(buf, 0.3 * creak, toe + 0.04)
    return _tail_fade(filt(buf, [bq_highpass(60, 0.7)]))


def _plunk(g, f0: float, sec: float) -> np.ndarray:
    """The air cavity behind the foot collapsing: a sine whose pitch falls as it closes."""
    k = int(sec * SR)
    t = np.arange(k) / SR
    f = f0 * (0.5 + 0.5 * np.exp(-t / 0.035))
    return np.sin(2 * np.pi * np.cumsum(f) / SR + g.uniform(0, 6.28)) * np.exp(-t / 0.05) * np.minimum(1, t / 0.001)


def step_water(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 400 + v + (50 if run else 0))
    p = _gait(run)
    sec = 0.7 if run else 0.6
    buf = np.zeros(int(sec * SR))
    toe = float(g.uniform(*p["roll"]))
    for t0, lvl in ((0.0, p["heel"]), (toe, p["toe"] * 0.6)):
        slap = _noise(g, 0.06, [bq_highpass(500, 0.7), bq_lowpass(7000 if run else 5500, 0.7)], 0.001, 0.012)
        _place(buf, lvl * 0.7 * slap, t0)
        _place(buf, lvl * 0.55 * _plunk(g, float(g.uniform(150, 210)), 0.18), t0 + 0.003)
    sheet = _noise(g, 0.25, [bq_bandpass(1500, 0.7)], 0.02, 0.06 * (1 + p["kick"]))  # the sheet of spray
    _place(buf, (0.3 + 0.2 * p["kick"]) * sheet, 0.006)
    for _ in range(int(g.integers(5, 9)) + int(6 * p["kick"])):  # bubbles shaken loose round the ankle
        b = bubble(float(g.uniform(1.4, 4.0)), float(g.uniform(0.08, 0.22)), rise=float(g.uniform(0.05, 0.15)))
        _place(buf, b, float(g.uniform(0.01, 0.16)))
    for _ in range(int(g.integers(4, 7)) + int(8 * p["kick"])):  # drops falling back
        d = drip(float(g.uniform(0.3, 0.7)), float(g.uniform(1.6, 3.2)), seed=int(g.integers(1 << 30)))
        _place(buf, 0.35 * d, float(g.uniform(0.09, sec * 0.7)))
    drag = _noise(g, 0.3, [bq_lowpass(700, 0.7), bq_highpass(90, 0.7)], 0.08, 0.08)  # the foot lifted through it
    _place(buf, 0.35 * drag, toe + 0.08)
    return _tail_fade(filt(buf, [bq_highpass(70, 0.7), bq_lowpass(9000, 0.7)]), 0.05)


STEPS = {"sand": step_sand, "stone": step_stone, "wood": step_wood, "water": step_water}


# --------------------------------------------------------------------------- halts and turns


def stop_sand(v: int) -> np.ndarray:
    g = rng(SEED + 500 + v)
    buf = np.zeros(int(0.45 * SR))
    _place(buf, 0.9 * _noise(g, 0.2, [bq_lowpass(250, 0.7), bq_highpass(45, 0.7)], 0.006, 0.05), 0.0)
    slide = _grains(g, 0.32, int(g.integers(130, 180)), 900, 4500, 0.09)  # the sole sliding to a halt
    _place(buf, 0.6 * slide, 0.01)
    _place(buf, 0.5 * _noise(g, 0.15, [bq_lowpass(240, 0.7)], 0.006, 0.04), float(g.uniform(0.16, 0.22)))
    return _tail_fade(filt(buf, [bq_lowpass(6000, 0.7)]))


def stop_stone(v: int) -> np.ndarray:
    g = rng(SEED + 510 + v)
    buf = np.zeros(int(0.5 * SR))
    scrape = _noise(g, 0.2, [bq_bandpass(float(g.uniform(2000, 2800)), 0.8), bq_highpass(800, 0.7)], 0.02, 0.06)
    _place(buf, 0.55 * scrape, 0.0)
    _place(buf, 0.3 * _grains(g, 0.2, int(g.integers(25, 40)), 2500, 7500, 0.05), 0.01)
    knock = _modal([float(g.uniform(110, 135)), float(g.uniform(240, 280))], [0.02, 0.012], [1.0, 0.5], 0.08, g)
    _place(buf, 0.6 * knock, float(g.uniform(0.14, 0.2)))  # the other foot set down beside it
    return _tail_fade(_room(buf, 0.7, 0.14, SEED + 515 + v))


def stop_wood(v: int) -> np.ndarray:
    g = rng(SEED + 520 + v)
    buf = np.zeros(int(0.55 * SR))
    base = float(g.uniform(0.92, 1.08))
    modes = [110 * base, 245 * base, 415 * base, 690 * base]
    _place(buf, 0.7 * _modal(modes, [0.1, 0.06, 0.04, 0.025], [1.0, 0.6, 0.4, 0.25], 0.35, g), 0.0)
    _place(buf, 0.5 * _modal(modes, [0.1, 0.06, 0.04, 0.025], [1.0, 0.6, 0.4, 0.25], 0.35, g), 0.15)
    creak = stick_slip(g, 0.2, 35.0, 80.0, [(480 * base, 1.0), (1100 * base, 0.35)], q=7.0)
    _place(buf, 0.3 * creak, 0.08)
    return _tail_fade(filt(buf, [bq_highpass(60, 0.7)]))


def stop_water(v: int) -> np.ndarray:
    g = rng(SEED + 530 + v)
    sec = 0.8
    buf = np.zeros(int(sec * SR))
    slosh = _noise(g, 0.5, [bq_lowpass(900, 0.7), bq_highpass(90, 0.7)], 0.03, 0.14)  # the wake catching up
    _place(buf, 0.6 * slosh, 0.0)
    _place(buf, 0.3 * _noise(g, 0.3, [bq_bandpass(1300, 0.7)], 0.04, 0.08), 0.12)  # lapping at the shins
    for _ in range(int(g.integers(5, 8))):
        _place(buf, bubble(float(g.uniform(2.0, 5.0)), float(g.uniform(0.08, 0.18)), rise=0.1),
               float(g.uniform(0.05, 0.4)))
    for _ in range(int(g.integers(3, 5))):
        d = drip(float(g.uniform(0.3, 0.6)), float(g.uniform(1.8, 3.0)), seed=int(g.integers(1 << 30)))
        _place(buf, 0.3 * d, float(g.uniform(0.15, 0.55)))
    return _tail_fade(filt(buf, [bq_highpass(70, 0.7)]), 0.08)


def _twist(g, sec: float, f_from: float, f_to: float, q: float) -> np.ndarray:
    """A pivot: noise through a band that slides from f_from to f_to (the sole twisting on the ground)."""
    k = int(sec * SR)
    x = g.standard_normal(k)
    steps = 8
    out = np.zeros(k)
    seg = k // steps
    for i in range(steps):
        f = f_from + (f_to - f_from) * i / (steps - 1)
        y = filt(x, [bq_bandpass(f, q)])
        w = np.zeros(k)
        w[i * seg: (i + 1) * seg] = 1.0
        out += y * w
    out = filt(out, [bq_lowpass(max(f_from, f_to) * 1.5, 0.7)])
    return out * np.sin(np.pi * np.arange(k) / k) ** 1.2


def turn_sand(v: int) -> np.ndarray:
    g = rng(SEED + 600 + v)
    buf = np.zeros(int(0.32 * SR))
    _place(buf, 0.4 * _twist(g, 0.16, 1400, 2600, 1.2), 0.0)
    _place(buf, 0.6 * _grains(g, 0.2, int(g.integers(60, 90)), 1000, 4500, 0.06), 0.0)
    _place(buf, 0.5 * _noise(g, 0.12, [bq_lowpass(260, 0.7)], 0.005, 0.03), 0.0)
    return _tail_fade(buf)


def turn_stone(v: int) -> np.ndarray:
    g = rng(SEED + 610 + v)
    buf = np.zeros(int(0.35 * SR))
    _place(buf, 0.7 * _twist(g, 0.15, 1800, 3400, 1.6), 0.0)
    _place(buf, 0.3 * _grains(g, 0.15, int(g.integers(20, 35)), 2500, 7500, 0.04), 0.005)
    return _tail_fade(_room(buf, 0.7, 0.14, SEED + 615 + v))


def turn_wood(v: int) -> np.ndarray:
    g = rng(SEED + 620 + v)
    buf = np.zeros(int(0.4 * SR))
    base = float(g.uniform(0.92, 1.08))
    squeak = stick_slip(g, 0.14, 120.0, 260.0, [(900 * base, 1.0), (1900 * base, 0.4)], q=9.0)
    _place(buf, 0.45 * squeak, 0.0)
    tap = _modal([110 * base, 245 * base, 415 * base], [0.08, 0.05, 0.03], [1.0, 0.6, 0.35], 0.25, g)
    _place(buf, 0.5 * tap, 0.02)
    return _tail_fade(filt(buf, [bq_highpass(60, 0.7)]))


def turn_water(v: int) -> np.ndarray:
    g = rng(SEED + 630 + v)
    buf = np.zeros(int(0.55 * SR))
    swirl = _twist(g, 0.3, 500, 1100, 0.9)
    _place(buf, 0.6 * swirl, 0.0)
    for _ in range(int(g.integers(4, 7))):
        _place(buf, bubble(float(g.uniform(1.6, 4.0)), float(g.uniform(0.08, 0.2)), rise=0.1),
               float(g.uniform(0.04, 0.3)))
    d = drip(0.5, float(g.uniform(2.0, 3.0)), seed=int(g.integers(1 << 30)))
    _place(buf, 0.3 * d, float(g.uniform(0.2, 0.35)))
    return _tail_fade(filt(buf, [bq_highpass(80, 0.7)]), 0.06)


STOPS = {"sand": stop_sand, "stone": stop_stone, "wood": stop_wood, "water": stop_water}
TURNS = {"sand": turn_sand, "stone": turn_stone, "wood": turn_wood, "water": turn_water}


# --------------------------------------------------------------------------- foley


def cloth(v: int, run: bool) -> np.ndarray:
    g = rng(SEED + 700 + v + (50 if run else 0))
    buf = np.zeros(int(0.42 * SR))
    flaps = ((0.0, 1.0), (float(g.uniform(0.11, 0.15)), 0.7)) if run else ((0.0, 1.0),)
    for t0, lvl in flaps:
        sec = 0.14 if run else float(g.uniform(0.22, 0.28))
        f = float(g.uniform(900, 1500)) * (1.3 if run else 1.0)
        swish = _noise(g, sec, [bq_bandpass(f, 0.6), bq_highpass(350, 0.7)], sec * 0.4, sec * 0.25)
        _place(buf, lvl * swish, t0)
        rustle = _grains(g, sec, int(g.integers(10, 20)), 2500, 6500, sec * 0.5)  # weave catching on itself
        _place(buf, lvl * 0.25 * rustle, t0 + sec * 0.2)
    return _tail_fade(filt(buf, [bq_lowpass(7000, 0.7)]), 0.05)


def gear_lantern(v: int) -> np.ndarray:
    g = rng(SEED + 800 + v)
    buf = np.zeros(int(0.5 * SR))
    ratios = (1.0, 2.76, 5.4)
    f0 = float(g.uniform(1700, 2300))
    clink = _modal([f0 * r * float(g.uniform(0.99, 1.01)) for r in ratios], [0.08, 0.04, 0.02], [1.0, 0.45, 0.2],
                   0.3, g)
    _place(buf, clink, 0.0)
    for t0 in sorted(g.uniform(0.04, 0.12, 2)):  # the bail rattling in its lugs
        tick = _noise(g, 0.006, [bq_bandpass(float(g.uniform(3500, 4500)), 2.0)], 0.0002, 0.0012)
        _place(buf, 0.5 * tick, float(t0))
    glass = _modal([float(g.uniform(3100, 3600))], [0.18], [1.0], 0.4, g)
    _place(buf, 0.12 * glass, 0.002)
    return _tail_fade(filt(buf, [bq_highpass(600, 0.7)]), 0.08)


def gear_shells(v: int) -> np.ndarray:
    g = rng(SEED + 810 + v)
    buf = np.zeros(int(0.4 * SR))
    for t0 in np.sort(g.uniform(0.0, 0.1, int(g.integers(3, 5)))):
        f = float(g.uniform(2600, 4200))
        click = _modal([f, f * 1.83, f * 2.9], [0.012, 0.007, 0.004], [1.0, 0.5, 0.25], 0.06, g)
        _place(buf, float(g.uniform(0.5, 1.0)) * click, float(t0))
    return _tail_fade(filt(buf, [bq_highpass(1200, 0.7)]), 0.05)


def gear_leather(v: int) -> np.ndarray:
    g = rng(SEED + 820 + v)
    buf = np.zeros(int(0.42 * SR))
    creak = stick_slip(g, float(g.uniform(0.14, 0.2)), 25.0, 70.0, [(380.0, 1.0), (820.0, 0.5), (1600.0, 0.2)], q=4.0)
    _place(buf, 0.6 * creak, 0.0)
    buckle = _modal([float(g.uniform(2400, 2900)), float(g.uniform(5200, 6000))], [0.02, 0.01], [1.0, 0.4], 0.08, g)
    _place(buf, 0.4 * buckle, float(g.uniform(0.05, 0.12)))
    return _tail_fade(filt(buf, [bq_highpass(200, 0.7)]), 0.05)


GEARS = {"lantern": gear_lantern, "shells": gear_shells, "leather": gear_leather}


# --------------------------------------------------------------------------- render


def _todo() -> list[tuple]:
    out = []
    for s, fn in STEPS.items():
        for gait in GAITS:
            for v in range(STEP_VARIANTS):
                out.append((f"step_{s}_{gait}_{v + 1:02d}", (lambda f=fn, i=v, r=gait == "run": f(i, r)),
                            STEP_TARGET, STEP_CEILING))
    for s in SURFACES:
        for v in range(SCUFF_VARIANTS):
            out.append((f"stop_{s}_{v + 1}", (lambda f=STOPS[s], i=v: f(i)), STOP_TARGET, STEP_CEILING))
            out.append((f"turn_{s}_{v + 1}", (lambda f=TURNS[s], i=v: f(i)), TURN_TARGET, STEP_CEILING))
    for gait in GAITS:
        for v in range(FOLEY_VARIANTS):
            out.append((f"cloth_{gait}_{v + 1}", (lambda i=v, r=gait == "run": cloth(i, r)), FOLEY_TARGET,
                        FOLEY_CEILING))
    for k, fn in GEARS.items():
        for v in range(FOLEY_VARIANTS):
            out.append((f"gear_{k}_{v + 1}", (lambda f=fn, i=v: f(i)), FOLEY_TARGET, FOLEY_CEILING))
    return out


FILES = [f"{name}.ogg" for name, *_ in _todo()]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
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
