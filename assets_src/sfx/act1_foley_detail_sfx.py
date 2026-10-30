"""Act I foley, the detail pass as played (M3-AUD-864; the Lead's 10-30 item): what an Act I player touched or heard
walk and found silent. Plain git under assets/audio/sfx/ (ADR 0174; Act I's small SFX).

**The other three heroes' gear** (footsteps.json `foley.gear`; every other step, as Rhen's, Asha's and Toma's in
hero_foley.py; cutscene actors walk with it too). Until now they fell back to Rhen's lantern:
    gear_book_1..4     Ysolde: the lacquer book held shut against her hip, a soft hard-cover tap on the robe, and
                       the ink-guards on her left hand ticking (fine curved metal)
    gear_anchor_1..4   Kerrid: the iron anchor-ring over his shoulder shifting on its strap, a low iron knock, and the
                       fluke at his hip
    gear_harness_1..4  Liss: the crossed harness straps creaking and the launcher at her hip, its brass latch rattling

**Ch8's Coilspire flue-key trial** (coilspire_sfx.json; the trial had no sound but the menu's touch):
    flue_key_open      a brass key turned in its copper flue: ratchet, the latch giving, the damper opening and the
                       draught pulled up the copper
    flue_key_shut      the key back, the damper shutting with a dull copper thunk, the draught cut
    flue_cough         a wrong flue: the fire coughs back down the copper, a muffled whoomph, soot rattling, smoke
    flue_lit           a tier lit: the fire catches and is drawn roaring up the flue, the copper ticking as it heats
    flue_niche_open    the side flue's niche: a stone seal grinding aside and dropping
    flue_key_seized    the seized key: strained brass that will not turn, a hard knock, nothing gives

**Field objects used** (interact_sfx.json, InteractAudio; under the menu's soft `ui_interact` touch):
    obj_rope_cut       a lashing cut: the knife's strokes through wet rope, the rope parting, the slack falling
    obj_tether_drop    a tether let run: rope paying out fast through the hands, the drop's thump at the bottom
    obj_hinge_pry      a brass hinge prised free: a metal groan, the pin popping, the brass in the hand
    obj_tin_open       an old tin: the rusted lid levered off, its contents rattling
    obj_take_small     a small thing taken up (a charm): a light knock and a cloth fold
    obj_door_locked    a shut door tried: the latch rattled, the wood holding

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Mono, q4.

Render:  python3 tools/audio/render_all.py --only act1_foley_detail_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import act2_creature_sfx as A2  # noqa: E402
from creature_sfx import buf, burst, crackle, creak, glass_ring, room, slosh, tap, thump, unit  # noqa: E402
from field_ambience import stick_slip  # noqa: E402
from field_sfx import _modal, _noise, _place, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, noise, place  # noqa: E402

SFX_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 20262700
GEAR_TARGET = -24.0           # hero_foley.py's FOLEY_TARGET: carried gear under the step
GEAR_VARIANTS = 4
COPPER = [(310.0, 1.0), (760.0, 0.5), (1450.0, 0.25)]
WOOD = [(180.0, 1.0), (430.0, 0.6), (980.0, 0.25)]


# --------------------------------------------------------------------------- gear (foley/)
def gear_book(v: int) -> np.ndarray:
    g = rng(SEED + 10 + v)
    x = np.zeros(int(0.4 * SR))
    tapb = _modal([float(g.uniform(420, 520)), float(g.uniform(1100, 1300))], [0.03, 0.015], [1.0, 0.35], 0.08, g)
    _place(x, 0.8 * tapb, 0.0)                               # the book's hard cover on the robe
    rub = _noise(g, 0.12, [bq_bandpass(1800, 0.7)], 0.02, 0.05)
    _place(x, 0.25 * rub, 0.01)
    for t0 in np.sort(g.uniform(0.04, 0.14, int(g.integers(2, 4)))):   # the ink-guards, fine curved metal
        f = float(g.uniform(4200, 5600))
        _place(x, 0.3 * _modal([f, f * 1.7], [0.01, 0.006], [1.0, 0.4], 0.04, g), float(t0))
    return _tail_fade(filt(x, [bq_highpass(250, 0.7)]), 0.05)


def gear_anchor(v: int) -> np.ndarray:
    g = rng(SEED + 20 + v)
    x = np.zeros(int(0.5 * SR))
    ring = _modal([float(g.uniform(260, 320)) * r for r in (1.0, 2.6, 4.9)], [0.12, 0.06, 0.03], [1.0, 0.4, 0.15], 0.3, g)
    _place(x, 0.7 * ring, 0.0)                               # the iron ring knocking on its strap
    _place(x, 0.5 * stick_slip(g, 0.14, 30.0, 70.0, [(300.0, 1.0), (700.0, 0.4)], q=4.0), 0.02)
    fluke = _modal([float(g.uniform(900, 1100)), float(g.uniform(2300, 2600))], [0.04, 0.02], [1.0, 0.3], 0.1, g)
    _place(x, 0.3 * fluke, float(g.uniform(0.08, 0.16)))     # the fluke at his hip
    return _tail_fade(filt(x, [bq_highpass(120, 0.7)]), 0.06)


def gear_harness(v: int) -> np.ndarray:
    g = rng(SEED + 30 + v)
    x = np.zeros(int(0.42 * SR))
    _place(x, 0.55 * stick_slip(g, float(g.uniform(0.12, 0.18)), 30.0, 80.0, [(420.0, 1.0), (900.0, 0.5),
                                                                                (1700.0, 0.2)], q=4.0), 0.0)
    for t0 in np.sort(g.uniform(0.03, 0.12, 2)):             # the launcher's brass latch
        f = float(g.uniform(2700, 3200))
        _place(x, 0.4 * _modal([f, f * 2.3], [0.015, 0.008], [1.0, 0.35], 0.05, g), float(t0))
    return _tail_fade(filt(x, [bq_highpass(220, 0.7)]), 0.05)


GEARS = {"book": gear_book, "anchor": gear_anchor, "harness": gear_harness}


# --------------------------------------------------------------------------- the Coilspire (coilspire/)
def _draught(g, sec: float, rise: bool = True) -> np.ndarray:
    n = _n(sec)
    t = _t(n)
    env = np.clip(t / (0.6 * sec), 0, 1) ** 1.5 if rise else np.exp(-t / (0.25 * sec))
    return unit(noise(g, n, [bq_bandpass(420, 0.6), bq_lowpass(1500, 0.7)])) * env


def flue_key_open(g):
    x = buf(2.4)
    place(x, A2.Engine.ratchet(g, 0.35, 10, 16, 0.5), 0.0)         # the key's wards
    place(x, tap(g, [1300.0, 2900.0, 4400.0], [0.05, 0.03, 0.015], 0.8, 0.8), 0.38)   # the latch gives
    place(x, creak(g, 0.4, 60, 180, COPPER, 0.5), 0.42)           # the damper swinging
    place(x, _draught(g, 1.6), 0.55, 0.6)                          # the draught pulled up the copper
    return x


def flue_key_shut(g):
    x = buf(1.8)
    place(x, A2.Engine.ratchet(g, 0.3, 14, 9, 0.45), 0.0)
    place(x, thump(g, 210, 120, 0.06, 0.5, 0.3), 0.32, 0.9)      # a dull copper thunk
    place(x, tap(g, [f for f, _ in COPPER], [0.12, 0.07, 0.04], 0.5, 0.3), 0.32)
    place(x, _draught(g, 0.8, rise=False), 0.3, 0.4)             # the draught cut
    return x


def flue_cough(g):
    x = buf(2.6)
    place(x, thump(g, 90, 40, 0.18, 0.2, 0.7), 0.0, 1.0)         # the whoomph back down the flue
    place(x, unit(noise(g, _n(0.6), [bq_lowpass(700, 0.7)])) * np.exp(-_t(_n(0.6)) / 0.18), 0.0, 0.7)
    place(x, crackle(g, 1.2, 50, 3000, 0.7, 0.3), 0.15, 0.5)      # soot rattling down the copper
    place(x, tap(g, [f * 1.8 for f, _ in COPPER], [0.2, 0.1, 0.05], 0.4, 0.3), 0.05)
    smoke = unit(noise(g, _n(1.4), [bq_bandpass(900, 0.6)])) * np.exp(-_t(_n(1.4)) / 0.5)
    place(x, smoke, 0.25, 0.35)
    return x


def flue_lit(g):
    x = buf(3.4)
    n = _n(2.6)
    t = _t(n)
    roar = unit(noise(g, n, [bq_bandpass(350, 0.5), bq_lowpass(1600, 0.7)])) * np.clip(t / 0.9, 0, 1) ** 1.3 \
        * np.clip((2.6 - t) / 0.8, 0, 1)
    place(x, roar, 0.1, 0.9)                                    # caught, and drawn roaring up the flue
    place(x, crackle(g, 2.4, 45, 2600, 0.8, 0.5), 0.2, 0.5)
    for i in range(6):                                          # the copper ticking as it heats
        place(x, tap(g, [float(g.uniform(2400, 3400))], [0.01], 0.3, 0.9), 0.9 + 0.35 * i + float(g.uniform(0, 0.1)))
    return x


def flue_niche_open(g):
    x = buf(2.6)
    grind = stick_slip(g, 1.4, 8.0, 22.0, [(140.0, 1.0), (320.0, 0.6), (700.0, 0.25)], q=3.0)
    place(x, grind * np.sin(np.pi * np.clip(_t(len(grind)) / 1.4, 0, 1)) ** 0.6, 0.0, 0.9)
    place(x, thump(g, 120, 50, 0.12, 0.5, 0.5), 1.45, 1.0)      # the seal dropping
    place(x, crackle(g, 0.6, 30, 2000, 0.8, 0.2), 1.5, 0.3)
    return x


def flue_key_seized(g):
    x = buf(1.4)
    place(x, stick_slip(g, 0.5, 20.0, 40.0, [(900.0, 1.0), (2100.0, 0.4)], q=6.0), 0.0, 0.7)   # strained brass
    place(x, tap(g, [700.0, 1650.0, 3100.0], [0.04, 0.02, 0.01], 0.9, 0.9), 0.5)            # a hard knock
    place(x, tap(g, [700.0, 1650.0, 3100.0], [0.04, 0.02, 0.01], 0.6, 0.9), 0.62)
    return x


# --------------------------------------------------------------------------- field objects (interact/)
def obj_rope_cut(g):
    x = buf(1.6)
    for k in range(3):                                          # the knife's strokes through wet rope
        place(x, stick_slip(g, 0.12, 40.0, 140.0, [(1400.0, 1.0), (2800.0, 0.4)], q=3.0), 0.05 + 0.16 * k, 0.6)
    place(x, burst(g, 0.05, [bq_bandpass(900, 0.9)], 0.001, 0.015), 0.55, 0.8)   # parting
    place(x, A2.whoosh(g, 0.35, 1400, 400, 0.4), 0.58)                            # the slack falling
    place(x, thump(g, 150, 90, 0.04, 0.3, 0.2), 0.9, 0.4)
    return x


def obj_tether_drop(g):
    x = buf(2.0)
    n = _n(1.0)
    run = unit(noise(g, n, [bq_bandpass(1600, 0.8)])) * np.clip(_t(n) / 0.1, 0, 1) * np.clip((1.0 - _t(n)) / 0.2, 0, 1)
    place(x, run, 0.0, 0.6)                                      # rope paying out through the hands
    place(x, stick_slip(g, 0.9, 60.0, 140.0, [(700.0, 1.0), (1500.0, 0.4)], q=3.0), 0.05, 0.3)
    place(x, thump(g, 110, 50, 0.1, 0.4, 0.5), 1.05, 1.0)        # the bottom
    place(x, slosh(g, 0.6, 0.4, 2.5), 1.08)
    return x


def obj_hinge_pry(g):
    x = buf(1.4)
    place(x, stick_slip(g, 0.45, 15.0, 35.0, [(800.0, 1.0), (1900.0, 0.5), (3300.0, 0.2)], q=5.0), 0.0, 0.7)
    place(x, tap(g, [2100.0, 4700.0], [0.03, 0.015], 1.0, 0.9), 0.48)           # the pin popping
    place(x, glass_ring(g, 1650.0, 0.5, 0.3), 0.5)                               # the brass in the hand
    return x


def obj_tin_open(g):
    x = buf(1.3)
    place(x, stick_slip(g, 0.25, 25.0, 60.0, [(1200.0, 1.0), (2800.0, 0.4)], q=4.0), 0.0, 0.6)
    place(x, tap(g, [1800.0, 4100.0], [0.04, 0.02], 0.9, 0.8), 0.28)            # the lid off
    for k in range(5):                                           # its contents rattling
        place(x, tap(g, [float(g.uniform(1500, 2600))], [0.02], 0.4, 0.8), 0.38 + 0.06 * k + float(g.uniform(0, 0.03)))
    return x


def obj_take_small(g):
    x = buf(0.8)
    place(x, tap(g, [900.0, 2200.0], [0.02, 0.01], 0.7, 0.6), 0.0)
    place(x, _noise(g, 0.2, [bq_bandpass(1500, 0.7)], 0.03, 0.08), 0.08, 0.3)   # a cloth fold
    return x


def obj_door_locked(g):
    x = buf(1.2)
    for k in range(3):                                           # the latch rattled, the wood holding
        place(x, tap(g, [f for f, _ in WOOD], [0.05, 0.03, 0.015], 0.7 - 0.1 * k, 0.6), 0.1 * k)
        place(x, tap(g, [2300.0, 3900.0], [0.02, 0.01], 0.5, 0.8), 0.1 * k + 0.01)
    place(x, creak(g, 0.3, 40, 120, WOOD, 0.3), 0.35)
    return x


# name -> (folder, fn, momentary max)
ONE_SHOTS: list[tuple[str, str, object, float]] = [
    ("coilspire", "flue_key_open", flue_key_open, -20.0), ("coilspire", "flue_key_shut", flue_key_shut, -21.0),
    ("coilspire", "flue_cough", flue_cough, -18.0), ("coilspire", "flue_lit", flue_lit, -18.0),
    ("coilspire", "flue_niche_open", flue_niche_open, -19.0), ("coilspire", "flue_key_seized", flue_key_seized, -20.0),
    ("interact", "obj_rope_cut", obj_rope_cut, -21.0), ("interact", "obj_tether_drop", obj_tether_drop, -21.0),
    ("interact", "obj_hinge_pry", obj_hinge_pry, -21.0), ("interact", "obj_tin_open", obj_tin_open, -22.0),
    ("interact", "obj_take_small", obj_take_small, -24.0), ("interact", "obj_door_locked", obj_door_locked, -22.0),
]
FILES = ([f"foley/gear_{k}_{v}.ogg" for k in GEARS for v in range(1, GEAR_VARIANTS + 1)]
         + [f"{d}/{name}.ogg" for d, name, _, _ in ONE_SHOTS])


def render(out_dir: str = SFX_DIR, verbose: bool = True) -> dict:
    res = {}
    for k, fn in GEARS.items():
        for v in range(1, GEAR_VARIANTS + 1):
            x = normalize_momentary(fn(v), GEAR_TARGET, ceiling_db=-3.0)
            path = os.path.join(out_dir, "foley", f"gear_{k}_{v}.ogg")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_ogg(path, x, quality=4.0)
            res[f"gear_{k}_{v}"] = measure(x)
    for i, (d, name, fn, tgt) in enumerate(ONE_SHOTS):
        seed = SEED + 1000 + 100 * i
        x = room(fn(rng(seed)), seed + 7, mix=0.14, tail=0.5, rt60=1.0)
        x = normalize_momentary(x, tgt, ceiling_db=-3.0)   # struck brass and rope decode over a -2 ceiling
        path = os.path.join(out_dir, d, name + ".ogg")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_ogg(path, x, quality=4.0)
        res[name] = measure(x)
    if verbose:
        for k, m in res.items():
            print(f"{k}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  TP {m['true_peak_dbtp']:.2f}")
    return res


if __name__ == "__main__":
    render()
