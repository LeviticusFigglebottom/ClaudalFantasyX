"""Temple-trial ambience (M1-AUD-02 prototype): an 80 s seamless loop.

Original composition for this project (SPEC §2, §9). A temple of the Order
of the Still Water: stone, still water, and the Order's own sound, which is
the congregation *humming* (only Cantors sing; bible §4). D minor
pentatonic colour (D F G A C), no pulse.

Layers
* Drone: D2 with its fifth A2, an additive tone whose partials beat slowly
  and whose upper partials "breathe" on a 13.3 s cycle. Every frequency and
  LFO is snapped to a whole number of cycles per loop, so it is exactly
  periodic.
* Congregation: men hum a slow chant line (D3 E3 F3 E3 D3 C3 D3 A2 C3 D3)
  through the whole loop; women join a fifth above (parallel-fifth organum)
  for the middle 44 s, which is the cue's only swell. Each voice breathes
  on its own schedule, so the hum never stops all at once.
* Sparse metallophone (soft mallets, long decays), two breath-flute phrases
  far back in the room, a soft gong at the midpoint.
* Water: three drip sources with their own periods (2.5, 3.2 and 5.0 s,
  +-4 % jitter) plus a few strays, Minnaert-bubble physics.
* A distant Cantor (alto) sings three Lamptongue words once per loop:
  "vey ... ennu ... mir" (water ... hush ... stay), from the glossary roots.
  This is the element most at risk of sounding synthetic; it is mixed low
  and far, and can be muted with CANTOR = False.

Loop: LOOPSTART = 0, LOOPLENGTH = the whole file (80.0 s).

Render:  python3 assets_src/music/temple_trial.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble, sing  # noqa: E402
from synth.water import drip  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "temple_trial.ogg")
SEED = 20261025
TARGET_LUFS = -16.0
LOOP_S = 80.0
CANTOR = True

CHANT = [("D3", 8), ("E3", 6), ("F3", 8), ("E3", 5), ("D3", 8), ("C3", 6), ("D3", 10), ("A2", 6), ("C3", 6),
         ("D3", 17)]
FIFTH_UP = {"D3": "A3", "E3": "B3", "F3": "C4", "C3": "G3", "A2": "E3"}
WOMEN_FROM, WOMEN_TO = 18.0, 62.0

METAL = [(2.0, "A5", .35, 6.0), (9.5, "D6", .30, 6.0), (11.0, "C6", .22, 5.0), (19.0, "F5", .32, 6.5),
         (27.5, "A5", .30, 6.0), (29.0, "G5", .20, 5.0), (31.0, "D5", .28, 7.0), (43.0, "D6", .28, 6.0),
         (52.0, "A5", .30, 6.0), (53.5, "C6", .22, 5.0), (61.0, "F5", .30, 6.0), (63.0, "G5", .25, 5.0),
         (70.0, "D5", .32, 7.0), (75.5, "A5", .20, 5.0)]
FLUTE = [
    (23.0, [("A4", 3.5), ("C5", 2.0), ("D5", 4.0), ("C5", 1.0), ("A4", 3.0)]),
    (56.0, [("F5", 2.5), ("G5", 1.5), ("A5", 4.5), ("G5", 1.0), ("F5", 1.5), ("D5", 4.0)]),
]
CANTOR_WORDS = [  # (start s, phonemes, pitches)
    (46.0, [("e", 0.9), ("i", 0.5)], [(69, 1.4)]),
    (48.3, [("e", 0.7), ("n", 0.3), ("u", 1.6)], [(72, 1.0), (69, 1.6)]),
    (51.2, [("m", 0.35), ("i", 1.9)], [(67, 0.35), (69, 1.9)]),
]
DRIPS = [  # (period s, radius mm, velocity, pan)
    (2.5, 2.2, 0.50, -0.6), (3.2, 3.0, 0.40, 0.5), (5.0, 1.6, 0.30, 0.1),
]


def _snap(f: float) -> float:
    """Nearest frequency with a whole number of cycles per loop."""
    return max(1.0, round(f * LOOP_S)) / LOOP_S


def drone(sr: int = SR) -> np.ndarray:
    """Exactly periodic (one loop long) low drone, stereo."""
    g = rng(SEED + 3)
    N = int(round(LOOP_S * sr))
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * _snap(1 / 13.33) * t)          # 0..1, 6 cycles per loop
    for root, lvl in ((n("D2"), 1.0), (n("A2"), 0.45)):
        f0 = midi_to_hz(root)
        for k, a in ((1, 1.0), (2, 0.55), (3, 0.30), (4, 0.18), (5, 0.12), (6, 0.07), (7, 0.04)):
            for side, det in ((0, 0.0), (1, 0.11 + 0.03 * k)):
                f = _snap(f0 * k + det)
                swell = 1.0 + (0.5 * (k - 1) / 6) * (breath - 0.5) * 2       # upper partials breathe more
                ph = g.uniform(0, 2 * np.pi)
                s = lvl * a * swell * np.sin(2 * np.pi * f * t + ph)
                out[:, side] += s
                out[:, 1 - side] += 0.6 * s
    out += 0.25 * np.sin(2 * np.pi * _snap(midi_to_hz(n("D1"))) * t)[:, None]
    return out * 0.05


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    # drone (exactly one loop long, placed at 0)
    mx.add("drone", drone(), 0.0)
    # congregation: men all loop long (loop mode = staggered breathing across the seam)
    men = hum_ensemble([(n(p), d) for p, d in CHANT], voices=14, seed=SEED + 11, register="low", loop=True)
    mx.add("hum", men, 0.0)
    # women: the middle of the line, a fifth above
    line, t = [], 0.0
    for p, d in CHANT:
        a, b = max(t, WOMEN_FROM), min(t + d, WOMEN_TO)
        if b > a:
            line.append((n(FIFTH_UP[p]), b - a))
        t += d
    women = hum_ensemble(line, voices=9, seed=SEED + 12, register="high", spread=0.9)
    fade = np.ones(len(women))
    k = int(3.0 * SR)
    fade[:k] = np.linspace(0, 1, k) ** 2
    mx.add("hum_hi", women * fade[:, None], WOMEN_FROM)
    # metallophone
    for i, (ts, p, v, dec) in enumerate(METAL):
        x = metallophone_note(n(p), v, seed=SEED + 101 * i, decay=dec, hardness=0.3, ombak_hz=4.2)
        mx.add("metal", x, ts, pan=float(g.uniform(-0.5, 0.5)))
    # flute
    for j, (ts, phrase) in enumerate(FLUTE):
        tt = ts
        for i, (p, d) in enumerate(phrase):
            x = breath_flute(n(p), d * 0.96, 0.42, seed=SEED + 503 * j + 7 * i, breath=0.42, scoop_cents=55.0,
                             vib_cents=10.0, vib_rate=4.2, swell=0.3 if d >= 3.5 else 0.0, release=0.5)
            mx.add("flute", x, tt - 0.05, pan=-0.35 if j == 0 else 0.3)
            tt += d
    # gong at the midpoint, kettle gongs
    mx.add("gong", large_gong(n("D2"), 0.35, seed=SEED + 31, t60=12.0), 40.0, pan=0.1)
    for ts, p in ((14.0, "A5"), (66.0, "D6")):
        mx.add("metal", kettle_gong(n(p), 0.25, seed=SEED + int(ts), t60=3.0), ts, pan=0.4)
    # cantor (distant alto)
    if CANTOR:
        for i, (ts, phon, pit) in enumerate(CANTOR_WORDS):
            x = sing(phon, pit, vel=0.8, seed=SEED + 900 + i, scale=1.17, tilt=1.6, breath=0.10, vib_cents=22.0,
                     vib_rate=5.2, release=0.5)
            mx.add("cantor", x, ts, pan=0.15)
    # water
    for si, (period, r, v, pan) in enumerate(DRIPS):
        count = int(round(LOOP_S / period))
        for i in range(count):
            ts = i * LOOP_S / count + g.normal(0, 0.04 * period)
            mx.add("water", drip(v * g.uniform(0.8, 1.1), r, seed=SEED + 1000 * si + i), ts % LOOP_S,
                   pan=pan + float(g.normal(0, 0.05)))
    for i in range(9):
        ts = float(g.uniform(0, LOOP_S))
        mx.add("water", drip(g.uniform(0.15, 0.35), g.uniform(1.2, 4.0), seed=SEED + 7000 + i), ts,
               pan=float(g.uniform(-0.9, 0.9)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    dark = lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(1800, 0.6)])  # noqa: E731
    mx.bus("drone", -10.0, send=0.30, process=dark)
    mx.bus("hum", 0.0, send=0.55)
    mx.bus("hum_hi", -3.0, send=0.60)
    mx.bus("metal", -4.0, send=0.55)
    mx.bus("flute", -9.0, send=0.75)
    mx.bus("gong", -11.0, send=0.5)
    mx.bus("cantor", -18.0, send=0.85)
    mx.bus("water", -9.0, send=0.45, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    build(mx)
    hall = ModFDNReverb(rt60=4.8, rt60_high=2.0, predelay=0.045, size=1.3, mod_depth=10.0, mod_rate=0.4,
                        early_level=0.25, lowcut=90.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-1.0)
    intro = np.zeros((0, 2))
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, None, None)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["L"] = L
        stats["limiter"] = rep
    if verbose:
        print(f"temple_trial: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  "
              f"peak {m['sample_peak_dbfs']:.2f} dBFS  TP {m['true_peak_dbtp']:.2f} dBTP  loop 0+{L}")
    return m


if __name__ == "__main__":
    render()
