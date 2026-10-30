"""Act I crowd walla where the town beds had none (M3-AUD-864, the foley detail pass as played; the Lead's 10-30 item:
"crowd walla in towns"). Haluna by day, Oruvel, Tamsule's market and Pemakar's festival already carry their people
(field_ambience.py, act1_ambience.py, act1_final_ambience.py); two zones had none:

    corrow_town     Ch8, Corrow by day, a working seawall town (its chandler, its netmender, the Okeru's people):
                    corrow_seawall is wind, waves and rope only. Voices along the mole (murmured, no words), a
                    netmender's mallet, a cart on the cobbles, a door, a far hammer on a hull.
    haluna_mourners Ch4, the wake at Haluna (haluna_wake: the village at its tables at night): haluna_night is the
                    crickets and the water. Low voices at the tables, quiet (a wake), cups and bowls set down on wood,
                    a bench, a child hushed; no laughter, no song.

Each is a layer under the zone's own bed: the zone row lists both (ambience.json). The file is at the beds' -26 LUFS
(render_all.py's rule for every bed) and its row plays it 4 dB down (`volume_db` -4; the wake's mourners 7 dB, so a
line's blips stay clear over the wake's four beds: tools/tests/test_dialogue_clarity.py), so the layer sits under the
zone's bed and the pair stays about 10 LU under the zone music (act1_loop_check.py). Seamless loops, plain git
under assets/audio/ambience/ (ADR 0174). Synthesized here and in tools/audio/synth/ (SPEC §2, §9).

Render:  python3 tools/audio/render_all.py --only act1_walla_ambience
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FA = _load("field_ambience")

OUT_DIR = os.path.join(ROOT, "assets", "audio", "ambience")
SEED = 20262800
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0
LOOPS = {"corrow_town": 40.0, "haluna_mourners": 42.0}


def _room(seed: int, rt60: float, size: float) -> ModFDNReverb:
    return ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=0.03, size=size, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.3, lowcut=120.0, highcut=6000.0, seed=seed)


def _knock(g, f0: float, decay: float) -> np.ndarray:
    return FA.modal([f0, f0 * 2.3, f0 * 4.1], [decay, decay * 0.5, decay * 0.25], [1.0, 0.4, 0.15], decay * 4, g,
                    click=0.5)


def _cart(g, sec: float) -> np.ndarray:
    """A handcart on cobbles: a run of small wooden knocks and a wheel's grind, swelling past."""
    n = int(sec * SR)
    y = np.zeros(n)
    t = 0.0
    while t < sec - 0.1:
        k = _knock(g, float(g.uniform(180, 320)), 0.03)
        s = int(t * SR)
        y[s: s + len(k)] += k[: n - s] * float(g.uniform(0.3, 0.8))
        t += float(g.uniform(0.07, 0.16))
    grind = filt(g.standard_normal(n), [bq_bandpass(700, 1.2)]) * 0.15
    return (y + grind) * np.sin(np.pi * np.arange(n) / n) ** 1.5


def corrow_town(g):
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS["corrow_town"], preroll_s=6.0)
    L = mx.L
    mx.bus("voices", 0.0, send=0.4, process=lambda x: filt(x, [bq_lowpass(2600, 0.7), bq_highpass(150, 0.7)]))
    mx.bus("work", -6.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    t = 0.4
    while t < LOOPS["corrow_town"] - 1.5:                       # voices along the mole, murmured
        mx.add("voices", FA.murmur_phrase(g, bool(g.random() < 0.45)), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.35, 1.0)))
        t += float(g.uniform(0.8, 2.6))
    for t in FA.schedule(L, 1.1, g, 0.4):                       # the netmender's mallet, a far hammer on a hull
        f0 = float(g.choice([260.0, 420.0]))
        mx.add("work", _knock(g, f0, 0.05), t, pan=float(g.uniform(-0.6, 0.6)), gain=float(g.uniform(0.3, 0.8)))
    for k in range(2):                                          # a cart past, twice a loop
        mx.add("work", _cart(g, 4.0), 6.0 + 20.0 * k, pan=-0.5 + k, gain=0.6)
    mx.add("work", _knock(g, 140.0, 0.12), 17.0, pan=0.4, gain=0.7)   # a door
    return mx, _room(SEED % 9973 + 1, 1.1, 1.6), {"voices": 0.0, "work": -9.0}


def haluna_mourners(g):
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS["haluna_mourners"], preroll_s=6.0)
    L = mx.L
    mx.bus("voices", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(2000, 0.7), bq_highpass(140, 0.7)]))
    mx.bus("tables", 0.0, send=0.3, process=lambda x: filt(x, [bq_lowpass(4500, 0.7)]))
    t = 0.6
    while t < LOOPS["haluna_mourners"] - 1.5:                   # low voices at the tables, quiet: a wake
        mx.add("voices", FA.murmur_phrase(g, bool(g.random() < 0.3)), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.3, 0.8)))
        t += float(g.uniform(1.4, 3.8))
    for t in FA.schedule(L, 3.0, g, 0.5):                       # cups and bowls set down on wood
        mx.add("tables", _knock(g, float(g.uniform(900, 1500)), 0.025), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.3, 0.7)))
    for t in FA.schedule(L, 11.0, g, 0.3):                      # a bench
        mx.add("tables", _knock(g, float(g.uniform(160, 220)), 0.06), t, pan=float(g.uniform(-0.6, 0.6)), gain=0.5)
    mx.add("voices", FA.murmur_phrase(g, True) * 0.6, 27.0, pan=0.5)   # a child, hushed
    return mx, _room(SEED % 9973 + 2, 0.8, 1.4), {"voices": 0.0, "tables": -10.0}


BEDS = {"corrow_town": corrow_town, "haluna_mourners": haluna_mourners}
FILES = [f"{b}{ext}" for b in BEDS for ext in (".ogg", ".loop.json")]


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb, gains = BEDS[name](g)
    for bus, db in gains.items():
        mx.buses[bus].gain_db = db
    _, loop = mx.render(reverb=verb, reverb_return_db=-4.0, hp_hz=40.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB)
    L = len(loop)
    os.makedirs(out_dir, exist_ok=True)
    write_ogg(os.path.join(out_dir, name + ".ogg"), loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, L, None, None)
    m = measure(loop)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS  "
              f"buses {{{', '.join(f'{k}: {v:.1f}' for k, v in mx.bus_lufs.items())}}}")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    return {name: render_bed(name, out_dir, verbose) for name in BEDS}


if __name__ == "__main__":
    render()
