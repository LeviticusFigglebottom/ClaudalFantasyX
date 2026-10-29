"""The Kite's foley (M3-AUD-859; act3_plan.md §2 "SFX for Act III"; docs/kb/art/environments/kite.md): the deck of
Dace's hull in flight, its two bound-light lift engines and their stopping at H09, and E4's landing by hand.

The Kite (Ch18 on) is Dace's 12 m hull, decked and railed, with two kite wings of battened sailcloth panels on an 11 m
mast (the rig follows Virel's sails, so its cloth is her luff and snap, vowbound_sfx.py), stayed to the deck, and two
lift engines on outriggers under it: bronze drums with a ring of vanes and a salt-glass band showing the bound core.
Bound light never pulses (the Lamp Engine's family: act2_creature_sfx.hum), so the engines are a steady two-partial
hum with the vanes' soft whirr on it. After H09 every bound light is gone and the Kite glides on sail alone (E1-E4):
the same deck with no engines, the wind and the cloth carrying everything. All synthesized (SPEC §2, §9).

assets/audio/sfx/act3/ (Git LFS, ADR 0039: rendered only with render_all.py --act3, never committed until LFS is live;
plain git has about 0.5 MiB left in its 72 MiB budget):
    kite_deck.ogg + .loop.json        the hub's deck bed in flight: wind, sails, stays, timber, the two engines  -26 I
    kite_deck_dark.ogg + .loop.json   E1-E4: the same deck after H09, gliding dark on sail alone                -26 I
    kite_engine_stop.ogg              H09: both engines winding down to nothing, the vanes slowing, a last knock
    kite_lantern_out_1..2             H09: a bow or stern lantern's light leaving its glass
    kite_sail_fill_1..2               a wing filling at once
    kite_rope_strain_1..3             E4: Liss (and the player's hold) taking the strain on a sheet
    kite_landing.ogg                  E4: the hull meeting the water hard; everyone survives
    kite_tiller_1..2                  the tiller worked
    kite_chest_open.ogg               the ledger chest by the hatch

Render:  python3 tools/audio/render_all.py --act3 --only kite_foley
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, SFX)

import numpy as np  # noqa: E402

from act2_creature_sfx import hum, splash, whoosh  # noqa: E402
from creature_sfx import buf, burst, finish, glass_ring, thump, unit  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from underwater_sfx import _n, _t, place  # noqa: E402
from vowbound_sfx import luff, snap  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(SFX, "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "act3")
SEED = 20261859
BED_LUFS = -26.0      # ambience beds (mix.md)
BED_CEILING = -6.0
BED_QUALITY = 1.0     # the Act I beds' quality
QUALITY = 4.0         # one-shots, as vowbound_sfx
ENGINE_HZ = 55.0      # A1: the engines' bound core (the Lamp Engine's family sits low)
VANES = 7             # vanes on each engine's ring
ENGINE_REV = 1.9      # revolutions a second
LOOPS = {"kite_deck": 40.0, "kite_deck_dark": 40.0}


def _room(seed: int) -> ModFDNReverb:
    # open air over the sea: a short, thin early field off the deck and sails, no hall
    return ModFDNReverb(rt60=0.6, rt60_high=0.3, predelay=0.012, size=0.8, mod_depth=4.0, mod_rate=0.3,
                        early_level=0.35, lowcut=150.0, highcut=6500.0, seed=seed)


def _whole(f: float, L: int) -> float:
    """The nearest frequency that fits a whole number of cycles in L samples (so a drone loops without a seam)."""
    return max(1, round(f * L / SR)) * SR / L


def engine_drone(L: int, g, f0: float = ENGINE_HZ) -> np.ndarray:
    """Both lift engines, steady: the bound core's hum (two near partials beating slowly, never pulsing) and the vane
    ring's soft whirr at VANES x ENGINE_REV, all periodic in the loop."""
    t = np.arange(L) / SR
    y = np.zeros(L)
    for k, a in ((1, 1.0), (2, 0.5), (3, 0.22), (5, 0.08)):
        f = _whole(f0 * k, L)
        y += a * (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * _whole(f * 1.004, L) * t + float(g.uniform(0, 6.28))))
    blade = _whole(VANES * ENGINE_REV, L)
    whirr = FA.circ_noise(L, g, [bq_bandpass(900, 0.8)]) * (0.55 + 0.45 * np.sin(2 * np.pi * blade * t)) ** 2
    return unit(y) + 0.35 * unit(whirr)


def stays(L: int, g, gust: np.ndarray) -> np.ndarray:
    """The stays and sheets singing in the wind: a low thrum and a thin aeolian whistle, both riding the gusts."""
    t = np.arange(L) / SR
    thrum = sum(a * np.sin(2 * np.pi * _whole(f, L) * t + float(g.uniform(0, 6.28)))
                for f, a in ((92.0, 1.0), (184.0, 0.4), (276.0, 0.15)))
    whistle = FA.circ_noise(L, g, [bq_bandpass(1450, 9.0), bq_bandpass(1450, 9.0)])
    return (0.6 * unit(thrum) + 0.4 * unit(whistle)) * (0.4 + 0.6 * gust)


def creak(g, dur: float = 0.8, lo: float = 60.0, hi: float = 240.0) -> np.ndarray:
    """Timber working under load: the mast step, a spar, the rail."""
    return FA.stick_slip(g, dur, lo, hi, [(280.0, 1.0), (690.0, 0.6), (1500.0, 0.25)])


def rope(g, dur: float = 1.2, lo: float = 120.0, hi: float = 520.0) -> np.ndarray:
    """A sheet under strain: fibre creak, higher and drier than timber."""
    return FA.stick_slip(g, dur, lo, hi, [(900.0, 1.0), (2100.0, 0.5), (3800.0, 0.2)], q=4.0)


def _deck(g, engines: bool):
    name = "kite_deck" if engines else "kite_deck_dark"
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    L = mx.L
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("cloth", 0.0, send=0.25)
    mx.bus("stays", 0.0, send=0.2)
    mx.bus("timber", 0.0, send=0.35)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.09, g)
    wind_gain = 0.3 if engines else 0.42   # with the engines gone the wind carries the scene
    mx.add("wind", FA.stereo_noise(L, g, [bq_lowpass(700, 0.6), bq_highpass(50, 0.7)], 0.5)
           * (0.55 + 0.45 * gust)[:, None] * wind_gain, 0.0)
    mx.add("stays", stays(L, g, gust) * 0.05, 0.0, pan=-0.2)
    for t in FA.schedule(L, 3.1 if engines else 2.6, g, 0.4):
        mx.add("cloth", luff(g, float(g.uniform(1.2, 2.4)), float(g.uniform(9.0, 14.0)), 1.0, swell=True), t,
               pan=float(g.uniform(-0.7, 0.7)), gain=float(g.uniform(0.15, 0.35)))
    for t in FA.schedule(L, 9.0, g, 0.4):
        mx.add("cloth", snap(g, 1.0), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.15, 0.3)))
    for t in FA.schedule(L, 4.5, g, 0.5):
        mx.add("timber", creak(g, float(g.uniform(0.5, 1.1))), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.15, 0.35)))
    if engines:
        mx.bus("engines", 0.0, send=0.15, process=lambda x: filt(x, [bq_lowpass(2400, 0.7)]))
        e = engine_drone(L, g)
        mx.add("engines", np.stack([e, np.roll(engine_drone(L, g), L // 3)], axis=1) * 0.12, 0.0)
    return mx, _room(SEED % 9973 + (1 if engines else 2))


def render_bed(name: str, out_dir: str) -> dict:
    g = rng(SEED + (1 if name == "kite_deck" else 2))
    mx, verb = _deck(g, name == "kite_deck")
    _, loop = mx.render(reverb=verb, reverb_return_db=-6.0, hp_hz=30.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, BED_LUFS, ceiling_db=BED_CEILING, report={})
    L = len(loop)
    write_ogg(os.path.join(out_dir, name + ".ogg"), loop, quality=BED_QUALITY,
              tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, L, None, None)
    return measure(loop)


# --------------------------------------------------------------------------- one-shots


def engine_stop(g):
    """H09: every bound light goes out. Both engines' hum sinks to nothing, the vanes slow, one last knock of the drum."""
    x = buf(7.0)
    place(x, hum(g, 5.5, ENGINE_HZ * 2, 1.0, bend=(1.0, 0.25)), 0.0)
    place(x, hum(g, 5.0, ENGINE_HZ * 3.01, 0.5, bend=(1.0, 0.22)), 0.05)
    n = _n(5.0)
    t = _t(n)
    rate = VANES * ENGINE_REV * np.exp(-t / 1.6)
    whirr = filt(g.standard_normal(n), [bq_bandpass(900, 0.8)]) * (0.55 + 0.45 * np.sin(2 * np.pi * np.cumsum(rate) / SR)) ** 2
    place(x, 0.4 * unit(whirr) * np.exp(-t / 1.8), 0.0)
    place(x, thump(g, 90, 40, 0.18, 0.4, 0.8), 5.1)
    place(x, glass_ring(g, 1320.0, 0.8, 0.15), 5.15)
    return x


def lantern_out(g, v):
    """A lantern's bound light leaving its glass: the glass ticks as it cools, and its faint hum goes."""
    x = buf(2.2)
    place(x, hum(g, 1.4, 880.0 + 40 * v, 0.25, bend=(1.0, 0.7)), 0.0)
    place(x, glass_ring(g, 2600.0 + 300 * v, 0.5, 0.6), 1.25)
    place(x, glass_ring(g, 3400.0 - 200 * v, 0.3, 0.3), 1.6)
    return x


def sail_fill(g, v):
    x = buf(2.4)
    place(x, snap(g, 1.0), 0.0)
    place(x, luff(g, 1.8, 12.0 + 2 * v, 0.6, swell=True), 0.02)
    place(x, whoosh(g, 1.0, 300, 1100, 0.4), 0.0)
    place(x, creak(g, 0.6, 80, 300), 0.15, 0.5)
    return x


def rope_strain(g, v):
    """E4: the strain taken on a sheet, hand over hand: the fibre creaking up as it loads, a block's knock."""
    x = buf(2.4)
    place(x, rope(g, 1.6 + 0.2 * v, 140 + 20 * v, 600 + 60 * v), 0.0)
    place(x, creak(g, 0.7, 60, 200), 0.6, 0.5)
    place(x, burst(g, 0.06, [bq_bandpass(700, 1.2)], 0.001, 0.015), 1.7, 0.4)
    return x


def landing(g):
    """E4: the glide runs out and the hull meets the water hard: the keel's slam, spray over the rail, timber groaning,
    the wings coming down slack. Hard, and survived: it settles, it does not break."""
    x = buf(6.0)
    place(x, whoosh(g, 1.0, 1400, 300, 0.5), 0.0)
    place(x, thump(g, 80, 32, 0.4, 0.5, 1.4), 0.85)
    place(x, splash(g, 2.8, 1.0, 1800), 0.85)
    place(x, creak(g, 1.4, 40, 160), 1.0, 0.7)
    place(x, luff(g, 2.0, 8.0, 0.5) * np.linspace(1.0, 0.0, _n(2.0)), 1.2)
    for k in range(3):
        place(x, FA.lap(g, 1.4 - 0.3 * k), 2.4 + 0.9 * k, 0.6 - 0.15 * k)
    return x


def tiller(g, v):
    x = buf(1.2)
    place(x, creak(g, 0.7 + 0.1 * v, 70 + 10 * v, 260), 0.0)
    return x


def chest_open(g):
    """The ledger chest: the iron hasp lifting, the lid's hinge, the lid laid back on the deck."""
    x = buf(1.8)
    place(x, glass_ring(g, 1900.0, 0.25, 0.3), 0.0)
    place(x, burst(g, 0.05, [bq_bandpass(2400, 1.0)], 0.0005, 0.01), 0.0, 0.5)
    place(x, creak(g, 0.8, 90, 320), 0.2)
    place(x, thump(g, 160, 90, 0.05, 0.4, 0.3), 1.1, 0.5)
    return x


ONE_SHOTS: list[tuple[str, object, float]] = [
    ("kite_engine_stop", engine_stop, -20.0),
    ("kite_lantern_out_1", lambda g: lantern_out(g, 0), -24.0),
    ("kite_lantern_out_2", lambda g: lantern_out(g, 1), -24.0),
    ("kite_sail_fill_1", lambda g: sail_fill(g, 0), -21.0),
    ("kite_sail_fill_2", lambda g: sail_fill(g, 1), -21.0),
    ("kite_rope_strain_1", lambda g: rope_strain(g, 0), -21.0),
    ("kite_rope_strain_2", lambda g: rope_strain(g, 1), -21.0),
    ("kite_rope_strain_3", lambda g: rope_strain(g, 2), -21.0),
    ("kite_landing", landing, -18.0),
    ("kite_tiller_1", lambda g: tiller(g, 0), -24.0),
    ("kite_tiller_2", lambda g: tiller(g, 1), -24.0),
    ("kite_chest_open", chest_open, -22.0),
]
FILES = [f"{b}{ext}" for b in LOOPS for ext in (".ogg", ".loop.json")] + [n + ".ogg" for n, _, _ in ONE_SHOTS]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {name: render_bed(name, out_dir) for name in LOOPS}
    for i, (name, fn, target) in enumerate(ONE_SHOTS):
        x = finish(fn(rng(SEED + 100 + i)), target)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=QUALITY)
        res[name] = measure(x)
    if verbose:
        for name, m in res.items():
            print(f"{name}: {m['seconds']:.2f}s  I {m['integrated_lufs']:.2f}  Mmax {m['momentary_max_lufs']:.2f}")
    return res


if __name__ == "__main__":
    render()
