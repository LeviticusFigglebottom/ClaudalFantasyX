"""The Undertow's storm as ambience (M3-AUD-865 / act1-chapters' M3-AUD-1254 ask; the human's playtest FAST-TRACK,
11-03): the beds under the storm's fights and fields, so a storm battle no longer carries the field's day beds.

Original sound design for this project (SPEC §2, §9), synthesized with field_ambience.py's helpers (imported) as the
Act II beds are (act2_ambience.py's choir_storm is the model: the same gale, surge and roar, without the Choir's
mouths, which belong to Ch16 alone).

    storm_gale   Ch1 Oruvel after the gulls (the breaking raft) and Ch8's headland after the beacon: the gale in
                 gusts, rain driven onto water and wood (a dense hiss, and drops hard on planks), the swell breaking
                 against hulls, and the Undertow's low roar under everything
    storm_wall   Ch8 Corrow's seawall in the storm (the stair-head, the hoist, the surge arenas, and the field between
                 the waves): the same gale and rain, the sea booming against the stone face every few seconds and
                 its spray coming over, the roar heavier

assets/audio/ambience/storm_gale.ogg, storm_wall.ogg (stereo loops, q1; plain git, not an LFS path): -26 LUFS
integrated, peaks under -5 dBTP (targets.py `ambience/*.ogg`).

Render:  python3 tools/audio/render_all.py --only storm_ambience
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(HERE, "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "ambience")
SEED = 20261865
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0
LOOPS = {"storm_gale": 40.0, "storm_wall": 42.0}


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def _room(seed: int, rt60: float, size: float, highcut: float = 6000.0) -> ModFDNReverb:
    return ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=0.03, size=size, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.3, lowcut=120.0, highcut=highcut, seed=seed)


def _weather(mx: LoopMixer, L: int, g, roar: float) -> np.ndarray:
    """The gale in gusts, the rain's hiss riding them, hard drops on wood, and the low roar. Returns the gust curve."""
    mx.bus("gale", 0.0, send=0.1)
    mx.bus("rain", 0.0, send=0.12)
    mx.bus("drops", 0.0, send=0.15)
    mx.bus("roar", 0.0, send=0.2, process=lambda x: filt(x, [bq_lowpass(220, 0.7)]))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.11, g)
    mx.add("gale", FA.stereo_noise(L, g, [bq_lowpass(2400, 0.6), bq_highpass(150, 0.7)], 0.3)
           * (0.4 + 0.6 * gust ** 1.3)[:, None] * 0.22, 0.0)
    whistle = FA.stereo_noise(L, g, [bq_bandpass(1300, 6.0)], 0.2) * (gust ** 3)[:, None] * 0.05
    mx.add("gale", whistle, 0.0)                                           # the gusts singing in the rigging
    mx.add("rain", FA.stereo_noise(L, g, [bq_highpass(2500, 0.7), bq_lowpass(9000, 0.7)], 0.1)
           * (0.55 + 0.45 * gust)[:, None] * 0.12, 0.0)
    for t in FA.schedule(L, 0.05, g, 0.9):                                 # drops hard on planks, driven
        k = int(0.012 * SR)
        d = filt(g.standard_normal(k), [bq_bandpass(float(g.uniform(1800, 4200)), 1.6)]) * np.linspace(1, 0, k) ** 3
        mx.add("drops", d, t, pan=float(g.uniform(-0.95, 0.95)), gain=float(g.uniform(0.02, 0.08)))
    mx.add("roar", FA.stereo_noise(L, g, [bq_lowpass(160, 0.6), bq_highpass(30, 0.7)], 0.7) * roar, 0.0)
    return gust


def storm_gale(g):
    mx, L = _mixer("storm_gale")
    _weather(mx, L, g, 0.22)
    mx.bus("swell", 0.0, send=0.25)
    for t in FA.schedule(L, 2.6, g, 0.5):                                  # the swell breaking against the hulls
        mx.add("swell", FA.burst(g, 1.6, [bq_lowpass(1400, 0.7), bq_highpass(110, 0.7)], 0.2, 0.7), t,
               pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.2, 0.42)))
        mx.add("swell", FA.slap(g), t + 0.15, pan=float(g.uniform(-0.6, 0.6)), gain=float(g.uniform(0.15, 0.3)))
    return mx, _room(SEED % 9973 + 1, 1.6, 1.8)


def storm_wall(g):
    mx, L = _mixer("storm_wall")
    _weather(mx, L, g, 0.3)
    mx.bus("boom", 0.0, send=0.3, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("spray", 0.0, send=0.2)
    for t in FA.schedule(L, 4.2, g, 0.35):                                 # the sea against the stone face
        n = int(2.4 * SR)
        tt = np.arange(n) / SR
        body = np.sin(2 * np.pi * (48.0 + 22.0 * np.exp(-tt / 0.25)) * tt) * np.exp(-tt / 0.6)
        body *= np.minimum(1.0, tt / 0.02)
        wash = filt(g.standard_normal(n), [bq_lowpass(500, 0.7)]) * np.exp(-tt / 0.8) * np.minimum(1.0, tt / 0.05)
        hit = 0.7 * body + 0.5 * wash
        mx.add("boom", np.stack([hit, hit], 1), t, gain=float(g.uniform(0.25, 0.45)))
        mx.add("spray", FA.burst(g, 1.2, [bq_highpass(1500, 0.7), bq_lowpass(8000, 0.7)], 0.25, 0.6), t + 0.5,
               pan=float(g.uniform(-0.7, 0.7)), gain=float(g.uniform(0.06, 0.12)))
    return mx, _room(SEED % 9973 + 2, 2.2, 2.4, highcut=5000.0)


BEDS = {"storm_gale": storm_gale, "storm_wall": storm_wall}
FILES = [f"{b}{ext}" for b in BEDS for ext in (".ogg", ".loop.json")]


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb = BEDS[name](g)
    _, loop = mx.render(reverb=verb, reverb_return_db=-4.0, hp_hz=30.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report={})
    n_ = len(loop)
    write_ogg(os.path.join(out_dir, name + ".ogg"), loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(n_)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, n_, None, None)
    m = measure(loop)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    return {name: render_bed(name, out_dir, verbose) for name in BEDS}


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT_DIR)
