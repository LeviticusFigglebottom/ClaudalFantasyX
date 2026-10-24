"""Saltgrass Causeway ambience beds (M2-AUD-13; vertical_slice.md B05/B06): two seamless stereo loops for the route.

The causeway is a tidal path of saltgrass and coral boulders, exposed only at low tide, with tidepools and wind
(act_outline.md Ch3). Everything here is synthesized from noise, oscillators and the bubble model in this file,
field_ambience.py and tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio). It is
original material: nothing is taken from or modelled on any existing recording.

Each bed is one loop body (LOOPSTART = 0, LOOPLENGTH = the whole file) built like the M2-AUD-05 beds: continuous
layers are noise shaped on the loop's own FFT grid (`circ_noise`, periodic by construction) times modulators made of
whole cycles per loop (`plfo`, `snap`); events wrap through `LoopMixer.add`; the bus filters and the reverb run in
steady state. So the sample after the last is the first, with no end crossfade at all.

Beds (assets/audio/ambience/):
    causeway_wind.ogg  52 s  the wind on an open tidal flat: a low body that breathes in gusts, the saltgrass's dry
                             hiss and its fast flutter (blades beating against each other, louder and quicker in the
                             gusts), grass swept flat in a few long swishes, and a faint hollow whistle across the
                             coral boulders at the strongest gusts. Brighter and grainier than Haluna's `wind` bed.
    tidepools.ogg      46 s  close to the pools at low tide: water trickling between them (streams of tiny Minnaert
                             bubbles in bursts), small pops and clicks from the creatures in the rock, drips off the
                             coral, a sucking gurgle now and then, and the surf line far out across the flat, low and
                             slow, so the sea is always there but never near.

Master: `master_loop` to -26 LUFS integrated with a -6 dBFS ceiling (mix.md §2), Ogg Vorbis q1 (noise beds, mix.md
§7), LOOPSTART/LOOPLENGTH tags and a `.loop.json` sidecar.

Render:  python3 assets_src/sfx/causeway_ambience.py   (or tools/audio/render_all.py --only causeway_ambience)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.water import bubble, drip  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(os.path.dirname(__file__),
                                                                              "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "ambience")
SEED = 20261213
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0  # noise beds: see field_ambience.py's docstring and mix.md §7
LOOPS = {"causeway_wind": 52.0, "tidepools": 46.0}


# --------------------------------------------------------------------------- sources


def grass_swish(g: np.random.Generator, dur: float) -> np.ndarray:
    """A field of saltgrass swept flat by one gust: bright noise whose band slides up and back as the gust passes,
    with the blades' flutter riding on it. Mono."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    shape = np.sin(np.pi * t / dur) ** 2
    lo = filt(g.standard_normal(n), [bq_bandpass(2600.0, 0.9)])
    hi = filt(g.standard_normal(n), [bq_bandpass(5200.0, 1.1)])
    flutter = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * np.cumsum(14.0 + 10.0 * shape) / SR))
    y = (lo * (1 - 0.6 * shape) + hi * (0.4 + 0.6 * shape)) * shape * flutter
    return y / (np.abs(y).max() + 1e-12)


def trickle(g: np.random.Generator, dur: float, rate: float) -> np.ndarray:
    """Water running over a lip of rock between two pools: a Poisson stream of tiny bubbles (radius 0.6-2 mm,
    2-5 kHz) whose rate swells and eases, over a faint hiss of the moving film. Mono."""
    n = int(dur * SR)
    y = np.zeros(n + int(0.3 * SR))
    t = 0.0
    while t < dur:
        u = t / dur
        local = rate * (0.35 + 0.65 * np.sin(np.pi * u) ** 1.2)
        t += float(g.exponential(1.0 / max(local, 1.0)))
        if t >= dur:
            break
        b = bubble(float(g.uniform(0.6, 2.0)), float(g.uniform(0.25, 1.0)), rise=float(g.uniform(0.05, 0.2)))
        s = int(t * SR)
        y[s: s + len(b)] += b[: len(y) - s]
    film = filt(g.standard_normal(len(y)), [bq_bandpass(3800.0, 0.8)])
    tt = np.arange(len(y)) / SR
    env = np.clip(tt / 0.3, 0, 1) * np.clip((dur - tt) / 0.5, 0, 1)
    return y * env + 0.03 * film * env


def pop(g: np.random.Generator) -> np.ndarray:
    """A small sharp pop in the rock (a shell closing, an anemone letting go of a bubble, a shrimp's snap): a
    0.5-1 ms click through a narrow body resonance, sometimes with a tiny bubble after it. Mono."""
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    k = int(float(g.uniform(0.0005, 0.0012)) * SR)
    click = np.zeros(n)
    click[:k] = g.standard_normal(k) * np.linspace(1, 0, k)
    f = float(g.uniform(2200.0, 6500.0))
    y = 0.5 * filt(click, [bq_highpass(1500.0, 0.7)]) + filt(click, [bq_bandpass(f, 6.0)]) * 3.0
    y *= np.exp(-t / 0.012)
    if g.random() < 0.4:
        b = bubble(float(g.uniform(0.8, 1.6)), 0.4, rise=0.15)
        s = int(0.004 * SR)
        y[s: s + len(b)] += b[: n - s]
    return y


def gurgle(g: np.random.Generator) -> np.ndarray:
    """Water sucked out of a crevice as the last of the ebb drains: a low burst and a run of larger bubbles. Mono."""
    y = FA.burst(g, 0.9, [bq_lowpass(700.0, 0.7), bq_highpass(90.0, 0.7)], 0.05, 0.25)
    t = 0.03
    for _ in range(int(g.integers(4, 9))):
        b = bubble(float(g.uniform(3.0, 7.0)), float(g.uniform(0.3, 0.8)), rise=0.12)
        s = int(t * SR)
        y[s: s + len(b)] += b[: len(y) - s]
        t += float(g.uniform(0.03, 0.11))
    return y


# --------------------------------------------------------------------------- beds


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def _flat(seed: int) -> ModFDNReverb:
    """An open tidal flat: almost no room, a short low-level spread from the boulders."""
    return ModFDNReverb(rt60=0.8, rt60_high=0.35, predelay=0.025, size=1.8, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.4, lowcut=180.0, highcut=6500.0, seed=seed)


# Bus gains were set from measured bus loudness (render_bed(..., stats)["bus_lufs"]) for these levels relative to
# the lead layer, the wind's body (0 LU): the saltgrass hiss -3 LU (it is the place's colour, so close behind),
# its flutter -8, the swishes -9 (events: louder at their peak), the boulder whistle -15 (only at gust peaks).
def causeway_wind(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("causeway_wind")
    mx.bus("body", 0.0)
    mx.bus("hiss", -5.6)
    mx.bus("flutter", -2.1)
    mx.bus("swish", 7.2, send=0.15, process=lambda x: filt(x, [bq_highpass(900.0, 0.7)]))
    mx.bus("whistle", -4.8, send=0.3)
    gust = 0.5 + 0.5 * FA.plfo(L, 0.09, g)          # slow gusts, whole cycles per loop
    fast = 0.5 + 0.5 * FA.plfo(L, 0.6, g)           # the gusts' own turbulence
    # the body: low and mid wind, brighter in the gusts (two bands crossfaded by gust strength)
    low = FA.stereo_noise(L, g, [bq_lowpass(380.0, 0.6), bq_highpass(55.0, 0.7)], 0.5)
    mid = FA.stereo_noise(L, g, [bq_bandpass(700.0, 0.8)], 0.35)
    body_env = 0.45 + 0.55 * gust * (0.8 + 0.2 * fast)
    mx.add("body", (low + 0.6 * mid * gust[:, None]) * body_env[:, None], 0.0)
    # the saltgrass hiss: a dry high band (3-8 kHz) that never quite stops, swelling with the gusts
    hiss = FA.stereo_noise(L, g, [bq_highpass(2800.0, 0.7), bq_lowpass(8500.0, 0.7), bq_peak(5200.0, 3.0, 0.8)],
                           0.2)
    mx.add("hiss", hiss * (0.35 + 0.65 * gust ** 1.4)[:, None], 0.0)
    # the flutter: blades beating against each other, an amplitude grain at 12-30 Hz that speeds up in the gusts.
    # Its phase is scaled so the loop holds a whole number of cycles, so it comes back round exactly at the wrap.
    cyc = np.concatenate([[0.0], np.cumsum(12.0 + 14.0 * gust)[:-1] / SR])   # cycles elapsed, from 0
    total = cyc[-1] + (12.0 + 14.0 * gust[-1]) / SR
    ph = 2 * np.pi * cyc * np.round(total) / total   # scaled so the loop holds a whole number of cycles
    grain = (0.5 + 0.5 * np.sin(ph)) ** 3
    blades = FA.stereo_noise(L, g, [bq_bandpass(3400.0, 1.4)], 0.15)
    mx.add("flutter", blades * (grain * gust ** 2)[:, None], 0.0)
    # swishes: a few gusts strong enough to sweep the grass flat, wandering across the field
    for t in FA.schedule(L, 9.0, g, 0.3):
        d = float(g.uniform(1.8, 3.2))
        mx.add("swish", grass_swish(g, d), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.5, 1.0)))
    # the boulders' hollow whistle: two narrow bands, only near the strongest gusts
    peak = np.clip((gust - 0.7) / 0.3, 0, 1) ** 2
    for f, w in ((640.0, 1.0), (930.0, 0.6)):
        mx.add("whistle", w * FA.stereo_noise(L, g, [bq_bandpass(f, 30.0)], 0.8) * peak[:, None], 0.0)
    return mx, _flat(SEED % 9973 + 1)


# Bus gains from measured bus loudness for these levels relative to the lead layer, the trickles (0 LU): the far
# surf line -3 LU (it carries the bed's floor), drips -7, pops -9 (sharp, so they read at a low level), the
# gurgles -8, the breeze -9.
def tidepools(g: np.random.Generator) -> tuple[LoopMixer, ModFDNReverb]:
    mx, L = _mixer("tidepools")
    loop_s = LOOPS["tidepools"]
    mx.bus("trickle", 0.0, send=0.15, process=lambda x: filt(x, [bq_highpass(400.0, 0.7)]))
    mx.bus("surf", -17.8, send=0.1)
    mx.bus("drips", 17.5, send=0.35, process=lambda x: filt(x, [bq_highpass(300.0, 0.7)]))
    mx.bus("pops", 6.0, send=0.2)
    mx.bus("gurgle", -5.4, send=0.2)
    mx.bus("breeze", -25.5)
    # three trickles in different places, each running in bursts of 3-8 s
    for k, (period, rate, pan) in enumerate(((7.5, 60.0, -0.55), (11.0, 35.0, 0.35), (15.0, 90.0, 0.7))):
        for t in FA.schedule(L, period, g, 0.2):
            d = float(g.uniform(3.0, 8.0))
            mx.add("trickle", trickle(g, d, rate * float(g.uniform(0.8, 1.2))), t, pan=pan + float(g.uniform(-0.1, 0.1)),
                   gain=float(g.uniform(0.6, 1.0)))
    # the surf line far across the flat: a low roar, a wave cycle of ~9 s snapped to the loop, very dark
    tt = np.arange(L) / SR
    wave = 0.5 + 0.5 * np.sin(2 * np.pi * FA.snap(1 / 9.2, L) * tt + 0.7)
    wave2 = 0.5 + 0.5 * np.sin(2 * np.pi * FA.snap(1 / 13.1, L) * tt + 2.1)
    roar = FA.stereo_noise(L, g, [bq_lowpass(420.0, 0.6), bq_highpass(45.0, 0.7)], 0.6)
    crest = FA.stereo_noise(L, g, [bq_bandpass(900.0, 0.7), bq_lowpass(1400.0, 0.7)], 0.4)
    mx.add("surf", roar * (0.55 + 0.3 * wave + 0.15 * wave2)[:, None]
           + 0.35 * crest * (wave ** 4 * (0.6 + 0.4 * wave2))[:, None], 0.0)
    # drips off the coral overhangs into the pools: two regular drips and strays
    for period, r, vel, pan in ((3.7, 2.0, 0.5, -0.3), (5.9, 3.2, 0.4, 0.5)):
        for t in FA.schedule(L, period, g, 0.06):
            mx.add("drips", drip(vel, r, seed=int(g.integers(1 << 30))), t, pan=pan)
    for t in FA.schedule(L, 6.5, g, 0.45):
        mx.add("drips", drip(0.3, float(g.uniform(1.2, 3.5)), seed=int(g.integers(1 << 30))), t,
               pan=float(g.uniform(-0.9, 0.9)))
    # pops and clicks: sparse, scattered, in small clusters
    t = 0.2
    while t < loop_s:
        for j in range(int(g.integers(1, 4))):
            mx.add("pops", pop(g), t + 0.05 * j + float(g.uniform(0, 0.04)), pan=float(g.uniform(-0.9, 0.9)),
                   gain=float(g.uniform(0.3, 1.0)))
        t += float(g.exponential(0.9)) + 0.15
    for t in (8.0, 24.5, 39.0):
        mx.add("gurgle", gurgle(g), t + float(g.uniform(-1, 1)), pan=float(g.uniform(-0.6, 0.6)))
    # a soft breeze over the flat (the causeway_wind bed carries the wind; this only keeps the pools outdoors)
    br = FA.stereo_noise(L, g, [bq_bandpass(1800.0, 0.6), bq_highpass(400.0, 0.7)], 0.3)
    mx.add("breeze", br * (0.6 + 0.4 * FA.plfo(L, 0.08, g))[:, None], 0.0)
    return mx, _flat(SEED % 9973 + 2)


BEDS = {"causeway_wind": causeway_wind, "tidepools": tidepools}


def render_bed(name: str, out_dir: str = OUT_DIR, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED + 101 * (list(BEDS).index(name) + 1))
    mx, verb = BEDS[name](g)
    _, loop = mx.render(reverb=verb, reverb_return_db=-6.0, hp_hz=30.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report=rep)
    L = len(loop)
    path = os.path.join(out_dir, name + ".ogg")
    write_ogg(path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.join(out_dir, name + ".loop.json"), SR, 0, L, None, None)
    m = measure(loop)
    m["limiter"] = rep
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  peak {m['sample_peak_dbfs']:.2f} dBFS  "
              f"limited {100 * rep.get('fraction_limited', 0):.2f} %")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    return {name: render_bed(name, out_dir, verbose) for name in BEDS}


if __name__ == "__main__":
    only = sys.argv[1:]
    for bed in BEDS:
        if not only or bed in only:
            render_bed(bed)
