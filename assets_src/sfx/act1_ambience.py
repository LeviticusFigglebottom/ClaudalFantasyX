"""Act I zone ambience beds (M3-AUD-16): Tamsule port, the Tamsule Bell's galleries, the Brine Shoals, the Pemakar
terraces, Ashcrown, and Corrow's seawall. Seamless loops at -26 LUFS (mix.md §2), Vorbis q1 like the M2-AUD-05 beds.

All synthesized from the building blocks in field_ambience.py (circular noise on the loop's own FFT grid, periodic
LFOs, laps, slaps, stick-slip creaks, murmured phrases, gulls); no recordings. Every event is placed in loop time
(it wraps), every modulation runs whole cycles per loop, so the beds have no seam.

* tamsule_port: harbour water slapping hulls, rigging tinkling on masts, a far market murmur, gulls, a ship's bell
  once a loop (the Tamsule Bell's own colour, far and small).
* tamsule_bell: inside the arena's galleries: a big, resonant enclosed air, water lapping the sphere's footing
  below, the Bell's faint sympathetic hum, footsteps and voices far across the bowl.
* brine_shoals: mud flats: sucking mud pops, trickles in the channels, wreck timbers creaking, a low wind, and far
  crackle from the burned camp's embers.
* pemakar_terraces: the terrace channels running in small falls, leaf-boats bumping the stones, leaves, a distant
  festival murmur (Lanternfall among the graves).
* ashcrown: mountain wind, a fine hiss of falling ash, copper ticking as it cools, a far rumble of the plume.
* corrow_seawall: a hard wind, waves booming against the wall and the spray coming over, flag and rope.

Render:  python3 assets_src/sfx/act1_ambience.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(os.path.dirname(__file__),
                                                                               "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "ambience")
SEED = 20261125
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0
LOOPS = {"tamsule_port": 44.0, "tamsule_bell": 40.0, "brine_shoals": 46.0, "pemakar_terraces": 42.0,
         "ashcrown": 40.0, "corrow_seawall": 44.0}


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def _room(seed: int, rt60: float, size: float) -> ModFDNReverb:
    return ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=0.03, size=size, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.3, lowcut=120.0, highcut=7000.0, seed=seed)


def tink(g) -> np.ndarray:
    """A halyard tinking on a metal mast."""
    f = float(g.uniform(1800, 2600))
    return FA.modal([f, f * 2.76, f * 5.4], [0.25, 0.08, 0.03], [1.0, 0.4, 0.15], 0.6, g, click=0.3)


def mud_pop(g) -> np.ndarray:
    """A bubble of gas freeing itself from mud: a low, slow Minnaert pop with a sucking lead-in."""
    y = np.zeros(int(0.5 * SR))
    suck = FA.burst(g, 0.12, [bq_lowpass(700, 0.7), bq_highpass(120, 0.7)], 0.06, 0.03)
    y[: len(suck)] += 0.5 * suck
    b = bubble(float(g.uniform(9.0, 16.0)), 1.0, rise=0.25)
    s = int(0.09 * SR)
    y[s: s + len(b)] += b[: len(y) - s]
    return y


def ember(g) -> np.ndarray:
    """A crackle from a burned-out fire: a few tiny broadband pops."""
    y = np.zeros(int(0.25 * SR))
    for _ in range(int(g.integers(1, 4))):
        s = int(float(g.uniform(0, 0.18)) * SR)
        k = int(0.004 * SR)
        y[s: s + k] += g.standard_normal(k) * np.linspace(1, 0, k) * float(g.uniform(0.3, 1.0))
    return filt(y, [bq_highpass(1200, 0.7)])


def boom(g) -> np.ndarray:
    """A wave striking a wall: a deep thump, then the spray falling back."""
    t = np.arange(int(2.5 * SR)) / SR
    y = np.sin(2 * np.pi * (38 + 25 * np.exp(-t / 0.15)) * t) * np.exp(-t / 0.35)
    y += 0.5 * filt(g.standard_normal(len(t)), [bq_lowpass(300, 0.7)]) * np.exp(-t / 0.25)
    spray = filt(g.standard_normal(len(t)), [bq_bandpass(3000, 0.5)]) * np.clip((t - 0.3) / 0.3, 0, 1) * np.exp(
        -np.maximum(t - 0.6, 0) / 0.7)
    return y + 0.35 * spray


def tamsule_port(g):
    mx, L = _mixer("tamsule_port")
    mx.bus("water", 0.0, send=0.1)
    mx.bus("rigging", 0.0, send=0.3)
    mx.bus("voices", 0.0, send=0.45, process=lambda x: filt(x, [bq_lowpass(2600, 0.7)]))
    mx.bus("gulls", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(4200, 0.7)]))
    mx.bus("bell", 0.0, send=0.5)
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(500, 0.6), bq_highpass(60, 0.7)], 0.5)
           * (0.7 + 0.3 * FA.plfo(L, 0.08, g))[:, None] * 0.2, 0.0)
    for t in FA.schedule(L, 1.6, g, 0.35):
        mx.add("water", FA.slap(g) if g.random() < 0.5 else FA.lap(g, 0.8), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.4, 1.0)))
    for t in FA.schedule(L, 2.3, g, 0.45):
        mx.add("rigging", tink(g), t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.3, 1.0)))
    t = 0.5
    while t < LOOPS["tamsule_port"] - 2.0:
        mx.add("voices", FA.murmur_phrase(g, bool(g.random() < 0.5)), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.4, 1.0)))
        t += float(g.uniform(1.0, 3.0))
    for t in FA.schedule(L, 12.0, g, 0.3):
        mx.add("gulls", FA.gull_call(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.5, 1.0)))
    mx.add("bell", tower_bell(n("A3"), 0.4, seed=SEED + 7, t60=6.0, dark=0.5), 21.0, pan=0.6)
    return mx, _room(SEED % 9973 + 1, 1.0, 1.6)


def tamsule_bell(g):
    mx, L = _mixer("tamsule_bell")
    mx.bus("air", 0.0, send=0.6)
    mx.bus("water", 0.0, send=0.5)
    mx.bus("hum", 0.0, send=0.7)
    mx.bus("far", 0.0, send=0.8, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.add("air", FA.stereo_noise(L, g, [bq_lowpass(300, 0.6), bq_highpass(40, 0.7)], 0.7)
           * (0.85 + 0.15 * FA.plfo(L, 0.05, g))[:, None], 0.0)
    for t in FA.schedule(L, 1.2, g, 0.4):
        mx.add("water", FA.lap(g, float(g.uniform(0.5, 1.0))), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.3, 0.9)))
    tt = np.arange(L) / SR
    hum = np.zeros(L)
    for k, a in ((1, 1.0), (2, 0.4), (2.4, 0.25)):       # the Bell's hum, prime and tierce, faint and still
        hum += a * np.sin(2 * np.pi * FA.snap(110.0 * k, L) * tt)
    hum *= 0.6 + 0.4 * (0.5 + 0.5 * FA.plfo(L, 0.04, g))
    mx.add("hum", np.stack([hum, hum * 0.9], 1), 0.0)
    for t in FA.schedule(L, 3.5, g, 0.5):
        mx.add("far", FA.murmur_phrase(g, bool(g.random() < 0.4)), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.3, 0.8)))
    return mx, _room(SEED % 9973 + 2, 3.5, 2.0)


def brine_shoals(g):
    mx, L = _mixer("brine_shoals")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("mud", 0.0, send=0.2)
    mx.bus("trickle", 0.0, send=0.2)
    mx.bus("timber", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(2200, 0.7)]))
    mx.bus("embers", 0.0, send=0.4, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    mx.add("wind", FA.stereo_noise(L, g, [bq_bandpass(420, 0.5), bq_lowpass(1400, 0.6)], 0.5)
           * (0.5 + 0.5 * (0.5 + 0.5 * FA.plfo(L, 0.1, g)))[:, None], 0.0)
    for t in FA.schedule(L, 1.4, g, 0.45):
        mx.add("mud", mud_pop(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.3, 1.0)))
    for t in FA.schedule(L, 0.25, g, 0.45):
        b = bubble(float(g.uniform(1.0, 3.5)), float(g.uniform(0.2, 0.7)), rise=0.12)
        mx.add("trickle", b, t, pan=float(g.uniform(-0.7, 0.7)))
    for t in FA.schedule(L, 9.0, g, 0.3):
        c = FA.stick_slip(g, float(g.uniform(0.8, 1.6)), 10, 45, [(160, 1.0), (340, 0.6), (700, 0.3)])
        mx.add("timber", c, t, pan=float(g.uniform(-0.8, 0.8)))
    for t in FA.schedule(L, 0.7, g, 0.5):
        mx.add("embers", ember(g), t, pan=float(g.uniform(0.3, 0.9)), gain=float(g.uniform(0.2, 1.0)))
    return mx, _room(SEED % 9973 + 3, 0.9, 1.6)


def pemakar_terraces(g):
    mx, L = _mixer("pemakar_terraces")
    mx.bus("falls", 0.0, send=0.2)
    mx.bus("boats", 0.0, send=0.3)
    mx.bus("leaves", 0.0, send=0.1)
    mx.bus("festival", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(2000, 0.7)]))
    mx.add("falls", FA.stereo_noise(L, g, [bq_bandpass(1300, 0.6), bq_highpass(300, 0.7)], 0.3)
           * (0.8 + 0.2 * FA.plfo(L, 0.3, g))[:, None], 0.0)
    for t in FA.schedule(L, 0.18, g, 0.45):
        b = bubble(float(g.uniform(1.2, 4.0)), float(g.uniform(0.2, 0.6)), rise=0.1)
        mx.add("falls", b * 0.4, t, pan=float(g.uniform(-0.8, 0.8)))
    for t in FA.schedule(L, 4.5, g, 0.4):
        bump = FA.modal([float(g.uniform(180, 260)), float(g.uniform(500, 700))], [0.06, 0.03], [1.0, 0.4], 0.3, g,
                        click=0.2)
        mx.add("boats", bump, t, pan=float(g.uniform(-0.7, 0.7)), gain=float(g.uniform(0.4, 1.0)))
    mx.add("leaves", FA.stereo_noise(L, g, [bq_bandpass(4500, 0.6), bq_highpass(2000, 0.7)], 0.2)
           * (0.3 + 0.7 * (0.5 + 0.5 * FA.plfo(L, 0.15, g)) ** 2)[:, None], 0.0)
    t = 0.3
    while t < LOOPS["pemakar_terraces"] - 2.0:
        mx.add("festival", FA.murmur_phrase(g, bool(g.random() < 0.5)), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.3, 0.8)))
        t += float(g.uniform(1.5, 3.5))
    return mx, _room(SEED % 9973 + 4, 1.2, 1.7)


def ashcrown(g):
    mx, L = _mixer("ashcrown")
    mx.bus("wind", 0.0, send=0.15)
    mx.bus("ash", 0.0, send=0.1)
    mx.bus("copper", 0.0, send=0.4)
    mx.bus("plume", 0.0, send=0.3)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.08, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_bandpass(600, 0.4), bq_lowpass(2500, 0.6)], 0.4)
           * (0.3 + 0.7 * gust ** 1.5)[:, None], 0.0)
    mx.add("ash", FA.stereo_noise(L, g, [bq_highpass(5000, 0.7)], 0.1) * 0.5, 0.0)
    for t in FA.schedule(L, 2.0, g, 0.5):
        f = float(g.uniform(2500, 4200))
        tick = FA.modal([f, f * 1.9], [0.02, 0.01], [1.0, 0.4], 0.1, g, click=0.4)
        mx.add("copper", tick, t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.2, 0.8)))
    rum = FA.stereo_noise(L, g, [bq_lowpass(90, 0.7), bq_highpass(25, 0.7)], 0.8) * (0.5 + 0.5 * (
        0.5 + 0.5 * FA.plfo(L, 0.05, g)))[:, None]
    mx.add("plume", rum, 0.0)
    return mx, _room(SEED % 9973 + 5, 1.4, 2.0)


def corrow_seawall(g):
    mx, L = _mixer("corrow_seawall")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("waves", 0.0, send=0.3)
    mx.bus("rope", 0.0, send=0.2)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.12, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_bandpass(500, 0.45), bq_lowpass(3000, 0.6)], 0.4)
           * (0.4 + 0.6 * gust ** 1.3)[:, None], 0.0)
    for t in FA.schedule(L, 5.5, g, 0.25):
        mx.add("waves", boom(g), t, pan=float(g.uniform(-0.4, 0.4)), gain=float(g.uniform(0.6, 1.0)))
    flap = np.abs(FA.circ_noise(L, g, [bq_lowpass(12, 0.7)]))
    flag = FA.stereo_noise(L, g, [bq_bandpass(900, 0.8)], 0.3) * (flap / flap.max() * gust)[:, None]
    mx.add("rope", flag, 0.0)
    for t in FA.schedule(L, 7.0, g, 0.4):
        c = FA.stick_slip(g, float(g.uniform(0.5, 1.0)), 18, 70, [(420, 1.0), (880, 0.6), (1500, 0.3)])
        mx.add("rope", c, t, pan=float(g.uniform(-0.8, 0.8)))
    return mx, _room(SEED % 9973 + 6, 1.0, 1.8)


BEDS = {"tamsule_port": tamsule_port, "tamsule_bell": tamsule_bell, "brine_shoals": brine_shoals,
        "pemakar_terraces": pemakar_terraces, "ashcrown": ashcrown, "corrow_seawall": corrow_seawall}
# Bus gains per bed (dB), set from measured bus loudness (render_bed(stats=True) prints them): the bed's lead layer
# at 0, the rest at the planned levels in the comment of each line.
GAINS = {
    # harbour water lead; rigging -8, voices -6, gulls -9, the far bell -10
    "tamsule_port": {"water": 0.0, "rigging": -12.2, "voices": 7.4, "gulls": -16.5, "bell": 1.6},
    # the galleries' air lead; water -6, the Bell's hum -12, far voices -10
    "tamsule_bell": {"air": 0.0, "water": 21.0, "hum": -8.9, "far": 20.3},
    # the wind lead; mud -6, trickles -9, timbers -9, embers -14
    "brine_shoals": {"wind": 0.0, "mud": 13.6, "trickle": 18.4, "timber": 14.0, "embers": 19.3},
    # the falls lead; boats -8, leaves -8, the far festival -8
    "pemakar_terraces": {"falls": 0.0, "boats": 15.3, "leaves": -5.9, "festival": 25.6},
    # the wind lead; ash -10, copper ticks -12, the plume -6
    "ashcrown": {"wind": 0.0, "ash": -11.2, "copper": 9.7, "plume": -4.2},
    # the wind lead; the waves -2, flag and rope -9
    "corrow_seawall": {"wind": 0.0, "waves": 15.3, "rope": 2.9},
}


# M3-AUD-835 (the listening note's "check the wrap of tamsule_bell"): the PCM loop is circular, but the Vorbis encoder
# leaves a small step at the file's two ends, and this quiet humming bed showed it (a decoded wrap 9.7 times an
# ordinary sample step). The loop is rotated so the file's ends fall at its quietest moment (0.1 times). Rotating a
# circular loop changes only where it starts; the other beds keep their bytes.
QUIET_SEAM = ("tamsule_bell",)
QUIET_STEP = 512      # where to look for the quiet stretch (samples)
QUIET_WIN = 4096      # the stretch's length: about 0.1 s of energy


def quiet_seam(loop: np.ndarray) -> np.ndarray:
    """loop rotated to start at its quietest sample: the lowest-energy stretch, then its smallest sample there."""
    energy = np.convolve((loop ** 2).sum(axis=1), np.ones(QUIET_WIN) / QUIET_WIN, mode="same")
    c = int(np.argmin(energy[::QUIET_STEP])) * QUIET_STEP
    w = slice(max(0, c - QUIET_WIN // 2), min(len(loop), c + QUIET_WIN // 2))
    k = w.start + int(np.argmin(np.abs(loop[w]).sum(axis=1)))
    return np.roll(loop, -k, axis=0)


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True, stats: bool = False) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb = BEDS[name](g)
    for bus, db in GAINS[name].items():
        mx.buses[bus].gain_db = db
    _, loop = mx.render(reverb=verb, reverb_return_db=-4.0, hp_hz=30.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report=rep)
    if name in QUIET_SEAM:
        loop = quiet_seam(loop)
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
