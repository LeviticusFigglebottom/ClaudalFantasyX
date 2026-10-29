"""The prologue's room tone (M3-AUD-817): Iskarra's drowned plaza at dusk, a seamless loop at -26 LUFS (mix.md §2),
Vorbis q1 like the other beds.

The Lit Age capital, drowned to its sixth storey: white ceramic towers, dead lamp-columns, plazas under clear
water, and seven people keeping their vigils apart. Nothing else lives here, so the bed is sparse on purpose: no
birds, no voices, no insects.
* water: small laps against the plaza's stone edges, and now and then the slow suck of a swell through a doorway.
* towers: the evening wind through the towers, low, with a faint singing where it crosses the ceramic openings
  (two very quiet tones, snapped to whole cycles per loop, swelling with the gusts).
* drips: far drips falling into still water inside the drowned storeys.
* far: the open sea far beyond the city, a slow low surge.
* vigil (M3-AUD-847): the seven keeping their vigils apart. Now and then, far across the plaza, a voice murmurs a
  few words to itself (the villagers' murmur, life_sfx.py, low-passed and set back), never close enough to follow.
  Rhen's lamp crackles at the lamp itself (cutscene_foley.json `lamps`), not in this bed.

All synthesized from the building blocks in field_ambience.py (circular noise on the loop's own FFT grid, periodic
LFOs, laps); no recordings. Every event is placed in loop time (it wraps) and every modulation runs whole cycles
per loop, so the bed has no seam.

Render:  python3 assets_src/sfx/prologue_ambience.py   (or tools/audio/render_all.py --only prologue_ambience)
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
from synth.water import drip  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(os.path.dirname(__file__),
                                                                               "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)
_lspec = importlib.util.spec_from_file_location("life_sfx", os.path.join(os.path.dirname(__file__), "life_sfx.py"))
LIFE = importlib.util.module_from_spec(_lspec)
_lspec.loader.exec_module(LIFE)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "ambience")
SEED = 20261127
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0
LOOPS = {"iskarra_dusk": 44.0}
# Bus gains (dB) from measured bus loudness (render_bed(stats=True)): the towers' wind lead at 0; water -4, the far
# sea -8, drips -12, the vigil's murmurs about -15 while one speaks (M3-AUD-847).
GAINS = {"iskarra_dusk": {"towers": 0.0, "water": 23.6, "drips": 34.2, "far": -4.4, "vigil": 15.0}}
VIGIL_EVERY_SEC = 13.0  # about three murmurs a loop, each from somewhere else on the plaza


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def surge(g) -> np.ndarray:
    """A swell drawing through a drowned doorway: a slow low rush in and a softer one out."""
    sec = float(g.uniform(3.5, 5.0))
    n = int(sec * SR)
    t = np.arange(n) / n
    y = filt(g.standard_normal(n), [bq_lowpass(450, 0.7), bq_highpass(60, 0.7)])
    return y * (np.sin(np.pi * t) ** 2) * (0.7 + 0.3 * np.sin(2 * np.pi * t))


def iskarra_dusk(g):
    mx, L = _mixer("iskarra_dusk")
    mx.bus("towers", 0.0, send=0.5)
    mx.bus("water", 0.0, send=0.35)
    mx.bus("drips", 0.0, send=0.8, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("far", 0.0, send=0.6, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.06, g)
    wind = FA.stereo_noise(L, g, [bq_bandpass(380, 0.8)], 0.3) * (0.4 + 0.6 * gust)[:, None]
    wind += 0.5 * FA.stereo_noise(L, g, [bq_bandpass(900, 1.0)], 0.3) * (gust ** 2)[:, None]
    tt = np.arange(L) / SR
    sing = np.zeros(L)
    for f, a in ((FA.snap(612.0, L), 1.0), (FA.snap(918.0, L), 0.6)):  # the ceramic openings, a fifth apart
        sing += a * np.sin(2 * np.pi * f * tt) * (0.5 + 0.5 * FA.plfo(L, 0.11, g))
    sing *= np.clip((gust - 0.55) / 0.45, 0, 1) ** 2 * 0.06
    mx.add("towers", wind + np.stack([sing, sing * 0.8], 1), 0.0)
    for t in FA.schedule(L, 2.6, g, 0.4):
        mx.add("water", FA.lap(g, float(g.uniform(0.4, 0.8))), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.3, 0.8)))
    for t in FA.schedule(L, 11.0, g, 0.3):
        mx.add("water", surge(g), t, pan=float(g.uniform(-0.5, 0.5)), gain=float(g.uniform(0.5, 0.9)))
    for t in FA.schedule(L, 3.7, g, 0.6):
        mx.add("drips", drip(vel=float(g.uniform(0.3, 0.6)), radius_mm=float(g.uniform(2.0, 3.5)),
                             seed=int(g.integers(1 << 30))), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.2, 0.7)))
    mx.add("far", FA.stereo_noise(L, g, [bq_lowpass(250, 0.6), bq_highpass(35, 0.7)], 0.6)
           * (0.6 + 0.4 * FA.plfo(L, 0.045, g))[:, None], 0.0)
    mx.bus("vigil", 0.0, send=0.9, process=lambda x: filt(x, [bq_lowpass(1600, 0.7), bq_highpass(220, 0.7)]))
    for i, t in enumerate(FA.schedule(L, VIGIL_EVERY_SEC, g, 0.4)):
        mx.add("vigil", LIFE.murmur(i, bool(g.random() < 0.4)), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.6, 1.0)))
    verb = ModFDNReverb(rt60=2.4, rt60_high=1.0, predelay=0.04, size=1.8, mod_depth=6.0, mod_rate=0.25,
                        early_level=0.25, lowcut=120.0, highcut=6500.0, seed=SEED % 9973 + 3)
    return mx, verb


BEDS = {"iskarra_dusk": iskarra_dusk}


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True, stats: bool = False) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb = BEDS[name](g)
    for bus, db in GAINS[name].items():
        mx.buses[bus].gain_db = db
    _, loop = mx.render(reverb=verb, reverb_return_db=-4.0, hp_hz=30.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report=rep)
    L = len(loop)
    path = os.path.join(out_dir, name + ".ogg")
    write_ogg(path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, L, None, None)
    m = measure(loop)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS")
    if stats:
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    return {name: render_bed(name, out_dir, verbose) for name in BEDS}


if __name__ == "__main__":
    for bed in BEDS:
        if len(sys.argv) < 2 or bed in sys.argv[1:]:
            render_bed(bed, stats=True)
