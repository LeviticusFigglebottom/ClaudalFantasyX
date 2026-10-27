"""`tidecup_crowd`: Ch7, the galleries filling before the Tidecup match (M3-AUD-822; act1_ch07.md B04): a 62 s
seamless loop.

Original (SPEC §2, §9). An ambience cue, all synthesized: no recording, no sample, no melody. The only tune-like
thing in it is a drummer's idle pattern (dum, tek, dum-dum, tek) written for this cue.

The brief: "A packed bowl of people under a bronze roof, the column's weep, a drum somewhere." The stilt galleries
ring the catch-pool tier on tier inside the Tamsule Bell, packed, waiting for the captains. Toma tells Asha he sat
there for Haluna as a boy; Liss says the Bell is glimmer-made, and nobody answers. Warmth with a crack in it. It plays
on the Music bus at the music target (`@music tidecup_crowd`, under the separate `bell_hum` layer), so it is built to
sit under dialogue: the talk is a wash of people, never words.
* the bowl: about sixty talkers at three distances (assets_src/sfx/reefball_sfx.py's own talkers: vowel-and-nasal
  formant voices on speech contours, so the crowd here is the same crowd as the match's), over a babble floor; now
  and then a call across the galleries;
* the bronze roof: the hall is long and bright-edged, and the crowd's sound sets the Bell's own partials ringing
  very faintly (a noise floor through narrow resonances at the tower_bell's hum, prime, tierce, quint and nominal
  on A2, so the roof is the same bronze as the Bell in tidecup_match and the galleries' cue);
* the column's weep: the thin, steady fall of water from the drop into the pool, centre and a little far: a fine
  splash and the small bubbles it makes;
* a drum somewhere: one frame drum high up in the galleries, someone tapping an idle pattern at about 100 BPM, four
  times in the loop, never in time with anything else.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file; everything is placed in loop time and wraps, and the beds are
circular noise, so the seam is a continuous crowd. No beat (bpm 0).

Render:  python3 assets_src/music/tidecup_crowd.py   (or tools/audio/render_all.py --only tidecup_crowd)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "sfx"))

import numpy as np  # noqa: E402

from field_ambience import circ_noise, plfo, stereo_noise  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import drip  # noqa: E402


def _mod(name: str, folder: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(folder, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CROWD = _mod("reefball_sfx", os.path.join(ROOT, "assets_src", "sfx"))

OUT = os.path.join(ROOT, "assets", "audio", "music", "tidecup_crowd.ogg")
SEED = 20261826
TARGET_LUFS = -16.0
LOOP_S = 62.0
TALKERS = 60
DIST = {"near": 2600.0, "mid": 1700.0, "far": 1000.0}      # each distance's low-pass (Hz), as reefball_sfx's
CALLS = 9                                                   # calls across the galleries per loop
## the Bell's partials (ratios to the prime A2) that the roof rings with: hum, prime, tierce, quint, nominal
ROOF_PARTIALS = [(0.5, 0.7), (1.0, 1.0), (1.2, 0.8), (1.5, 0.5), (2.0, 0.6)]
ROOF_PRIME = "A2"
DRUM_BPM = 100.0
DRUM_AT = [4.5, 19.0, 33.5, 49.0]                           # the drummer's four idle spells (s)
## one spell: (beat, stroke, velocity), two bars of 4/4 played twice
DRUM_SPELL = [(0.0, "dum", 0.5), (1.0, "tek", 0.3), (1.5, "ghost", 0.15), (2.0, "dum", 0.42), (2.5, "dum", 0.36),
              (3.0, "tek", 0.32), (4.0, "dum", 0.5), (5.0, "tek", 0.3), (6.0, "dum", 0.4), (6.5, "slap", 0.3),
              (7.0, "tek", 0.26), (7.5, "ghost", 0.14)]


def add_bowl(mx: LoopMixer, L: int) -> None:
    g = rng(SEED + 1)
    swell = 0.5 + 0.5 * plfo(L, 0.06, g)                   # the bowl's talk rises and falls a little
    mx.add("floor", CROWD.babble(g, L) * (0.8 + 0.2 * swell)[:, None], 0.0)
    for _ in range(TALKERS):
        dist = ["near", "mid", "mid", "far", "far", "far"][int(g.integers(0, 6))]
        pan = float(g.uniform(-1, 1))
        lvl = float(g.uniform(0.4, 1.0))
        high = bool(g.random() < 0.5)
        t = float(g.uniform(0, 4.0))
        end = t + LOOP_S - float(g.uniform(0.3, 1.0))
        while t < end:
            p = CROWD.phrase(g, high, False)
            sw = float(swell[int(t * SR) % L])
            mx.add(dist, p, t, pan=pan, gain=lvl * (0.6 + 0.4 * sw))
            t += len(p) / SR + float(g.uniform(0.25, 1.5))
    for _ in range(CALLS):
        c = CROWD.call(g, bool(g.random() < 0.5), float(g.uniform(2, 5)), float(g.uniform(-4, -1)),
                       float(g.uniform(0.4, 0.8)))
        mx.add("calls", c, float(g.uniform(0, LOOP_S)), pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.4, 0.9)))


def roof(L: int, g) -> np.ndarray:
    """The bronze answering the crowd: a speech-shaped noise floor through narrow resonances at the Bell's partials."""
    src = circ_noise(L, g, [bq_bandpass(500, 0.7)])
    out = np.zeros(L)
    f1 = midi_to_hz(n(ROOF_PRIME))
    for r, a in ROOF_PARTIALS:
        out += a * circ_noise(L, g, [bq_bandpass(f1 * r, 60.0), bq_bandpass(f1 * r, 40.0)])
    return out * (0.7 + 0.3 * np.abs(src).clip(0, 3) / 3)


def weep(L: int, g) -> np.ndarray:
    """The column's weep: a thin steady fall into the pool (a fine splash, flickering), (L, 2)."""
    fall = stereo_noise(L, g, [bq_highpass(900, 0.7), bq_peak(3200, 4.0, 0.8), bq_lowpass(8000, 0.7)], 0.7)
    flick = circ_noise(L, g, [bq_lowpass(25, 0.7)])
    return fall * (0.6 + 0.4 * np.tanh(flick))[:, None]


def add_drops(mx: LoopMixer) -> None:
    """The small bubbles the weep makes in the pool."""
    g = rng(SEED + 4)
    tt = 0.0
    while tt < LOOP_S:
        x = drip(vel=float(g.uniform(0.2, 0.5)), radius_mm=float(g.uniform(1.2, 2.8)), seed=int(g.integers(1 << 30)))
        mx.add("weep", 0.4 * x, tt, pan=float(g.uniform(-0.25, 0.25)))
        tt += float(g.exponential(1.0 / 14.0))


def add_drum(mx: LoopMixer) -> None:
    g = rng(SEED + 5)
    beat = 60.0 / DRUM_BPM
    for k, t0 in enumerate(DRUM_AT):
        pan = (0.55, 0.5, 0.6, 0.45)[k]
        for rep in range(2):
            for b, stroke, v in DRUM_SPELL:
                t = t0 + (8 * rep + b) * beat + float(g.normal(0, 0.008))
                mx.add("drum", frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=k * 40 + rep * 12 + int(2 * b),
                                          seed=SEED + 6), t, pan=pan)


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"]), for these levels relative to the mid-distance
# talkers (0 LU): near -2, far -3, the babble floor -6, calls -9, the roof -18, the weep -9, the drum -12.
GAINS = {"near": -2.1, "mid": 0.0, "far": -5.6, "floor": -28.1, "calls": -17.6, "roof": -40.6, "weep": -29.2,
         "drum": -1.8}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = GAINS
    for i, (k, fc) in enumerate(DIST.items()):
        mx.bus(k, G[k], send=0.3 + 0.15 * i, process=lambda x, f=fc: filt(x, [bq_lowpass(f, 0.7)]))
    mx.bus("floor", G["floor"], send=0.35)
    mx.bus("calls", G["calls"], send=0.5, process=lambda x: filt(x, [bq_lowpass(2800, 0.7)]))
    mx.bus("roof", G["roof"], send=0.4)
    mx.bus("weep", G["weep"], send=0.3, process=lambda x: filt(x, [bq_highpass(400, 0.7), bq_lowpass(7000, 0.7)]))
    mx.bus("drum", G["drum"], send=0.6, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    L = mx.L
    add_bowl(mx, L)
    mx.add("roof", np.stack([roof(L, rng(SEED + 2)), roof(L, rng(SEED + 12))], axis=1), 0.0)
    mx.add("weep", weep(L, rng(SEED + 3)), 0.0)
    add_drops(mx)
    add_drum(mx)
    bowl = ModFDNReverb(rt60=2.8, rt60_high=1.1, predelay=0.04, size=2.0, mod_depth=7.0, mod_rate=0.3,
                        early_level=0.3, lowcut=140.0, highcut=5500.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=bowl, reverb_return_db=-3.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=2.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, None, 4, extra={"meter": "free"})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"tidecup_crowd: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        lead = mx.bus_lufs["mid"]
        print("  buses (LU vs the mid talkers)", {k: round(v - lead, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
