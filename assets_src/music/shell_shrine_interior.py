"""Shell Shrine interior (M2-AUD-01; vertical_slice.md B07/B08 `shell_shrine_interior`): a 72 s seamless loop.

Original composition for this project (SPEC §2, §9). The brief: "water drips tuned to a drone, a hummed
congregation far off" (the Order hums; only Cantors sing, bible §4), in "a tended, loved place" where water obeys a
gentle hand. Where the M1 temple cue (temple_trial.py) is D minor and a little ominous, this one is warm: G with a
pentatonic colour (G A B D E), and the shadow is only the low E the hum leans on before it settles.

Layers
* Drone: G2 and D3, additive partials that beat slowly and breathe on an 18 s cycle; every frequency and LFO is
  snapped to whole cycles per loop, so it is exactly periodic.
* Tuned drips: three drip sources whose periods divide the loop (2.4, 3.0 and 4.5 s). Each drip is a Minnaert
  bubble whose radius is chosen so it rings at a pentatonic pitch (r = 3.26 / f), plus the faint ring of the shell
  basin it falls into at the same pitch. The pitch sequence of each source is a fixed, slowly turning pattern, so the
  drips spell short figures that never quite repeat inside the loop.
* Congregation, far off: men hum a slow original line (G3 A3 B3 A3 G3 E3 G3 D3 E3 G3); women join a fourth above
  for the middle 30 s. Mixed far back (high reverb send), under the drips.
* Shell horn: two low breath-flute phrases (a conch-like low register, breathy), far left and far right.
* A soft kettle gong at the loop's two quarter points.

Loop: LOOPSTART = 0, LOOPLENGTH = the whole file.

Render:  python3 assets_src/music/shell_shrine_interior.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.water import bubble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "shell_shrine_interior.ogg")
SEED = 20261102
TARGET_LUFS = -16.0
LOOP_S = 72.0

CHANT = [("G3", 7), ("A3", 6), ("B3", 8), ("A3", 5), ("G3", 7), ("E3", 8), ("G3", 7), ("D3", 6), ("E3", 6),
         ("G3", 12)]
FOURTH_UP = {"G3": "C4", "A3": "D4", "B3": "E4", "E3": "A3", "D3": "G3"}
WOMEN_FROM, WOMEN_TO = 21.0, 51.0
PENTA = ["G5", "A5", "B5", "D6", "E6", "G6"]
# (period s, pitch pattern as indices into PENTA, velocity, pan)
DRIPS = [
    (2.4, [3, 2, 0, 2, 3, 4, 3, 1], 0.55, -0.55),
    (3.0, [0, 1, 2, 1, 0, 3], 0.45, 0.45),
    (4.5, [5, 4, 3, 4], 0.35, 0.05),
]
HORN = [
    (12.0, [("D4", 3.0), ("E4", 1.5), ("G4", 4.0), ("E4", 2.5)], -0.6),
    (47.0, [("B3", 2.5), ("D4", 2.0), ("E4", 3.5), ("D4", 1.0), ("B3", 3.0)], 0.6),
]


def _snap(f: float) -> float:
    """Nearest frequency with a whole number of cycles per loop."""
    return max(1.0, round(f * LOOP_S)) / LOOP_S


def drone(sr: int = SR) -> np.ndarray:
    """Exactly periodic (one loop long) G drone, stereo."""
    g = rng(SEED + 3)
    N = int(round(LOOP_S * sr))
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * _snap(1 / 18.0) * t)
    for root, lvl in ((n("G2"), 1.0), (n("D3"), 0.40)):
        f0 = midi_to_hz(root)
        for k, a in ((1, 1.0), (2, 0.50), (3, 0.24), (4, 0.15), (5, 0.08), (6, 0.05)):
            for side, det in ((0, 0.0), (1, 0.09 + 0.025 * k)):
                f = _snap(f0 * k + det)
                swell = 1.0 + (0.45 * (k - 1) / 5) * (breath - 0.5) * 2
                s = lvl * a * swell * np.sin(2 * np.pi * f * t + g.uniform(0, 2 * np.pi))
                out[:, side] += s
                out[:, 1 - side] += 0.6 * s
    return out * 0.05


def tuned_drip(m: float, vel: float, seed: int, sr: int = SR) -> np.ndarray:
    """A drip whose bubble rings at pitch m (Minnaert radius r = 3.26 / f), plus the shell basin's faint ring."""
    g = rng(seed)
    f = midi_to_hz(m)
    radius_mm = 3260.0 / f
    main = bubble(radius_mm, 1.0, rise=g.uniform(0.008, 0.02), sr=sr)
    ring_len = int(1.6 * sr)
    t = np.arange(ring_len) / sr
    ring = np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) * np.exp(-t / 0.45) * np.minimum(1.0, t / 0.004)
    ring += 0.25 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.12)  # a shell's inharmonic second mode
    out = np.zeros(ring_len + int(0.01 * sr))
    s = int(g.uniform(0.0005, 0.002) * sr)
    out[s: s + len(main)] += main
    out[s: s + ring_len] += 0.10 * ring
    nn = int(0.002 * sr)
    out[:nn] += 0.2 * g.standard_normal(nn) * np.linspace(1, 0, nn) ** 2
    return 0.3 * vel * out


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("drone", drone(), 0.0)
    men = hum_ensemble([(n(p), d) for p, d in CHANT], voices=12, seed=SEED + 11, register="low", loop=True)
    mx.add("hum", men, 0.0)
    line, t = [], 0.0
    for p, d in CHANT:
        a, b = max(t, WOMEN_FROM), min(t + d, WOMEN_TO)
        if b > a:
            line.append((n(FOURTH_UP[p]), b - a))
        t += d
    women = hum_ensemble(line, voices=8, seed=SEED + 12, register="high", spread=0.9)
    env = np.ones(len(women))
    k = int(4.0 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    env[-k:] *= np.linspace(1, 0, k) ** 2
    mx.add("hum_hi", women * env[:, None], WOMEN_FROM)
    for si, (period, pattern, vel, pan) in enumerate(DRIPS):
        count = int(round(LOOP_S / period))
        for i in range(count):
            ts = i * period + g.normal(0, 0.03 * period)
            m = n(PENTA[pattern[i % len(pattern)]])
            v = vel * g.uniform(0.75, 1.05)
            mx.add("drips", tuned_drip(m, v, seed=SEED + 1000 * si + i), ts % LOOP_S,
                   pan=pan + float(g.normal(0, 0.06)))
    for j, (ts, phrase, pan) in enumerate(HORN):
        tt = ts
        for i, (p, d) in enumerate(phrase):
            x = breath_flute(n(p), d * 0.95, 0.40, seed=SEED + 503 * j + 7 * i, breath=0.55, scoop_cents=40.0,
                             vib_cents=8.0, vib_rate=4.0, swell=0.25 if d >= 3.0 else 0.0, release=0.6, beta=0.4)
            mx.add("horn", x, tt - 0.05, pan=pan)
            tt += d
    for ts, p in ((18.0, "D5"), (54.0, "G5")):
        mx.add("gong", kettle_gong(n(p), 0.22, seed=SEED + int(ts), t60=3.5), ts, pan=0.25)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("drone", -9.0, send=0.30, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(1600, 0.6)]))
    mx.bus("hum", -4.0, send=0.80)
    mx.bus("hum_hi", -7.0, send=0.85)
    mx.bus("drips", 1.0, send=0.50, process=lambda x: filt(x, [bq_highpass(250, 0.7)]))
    mx.bus("horn", -12.0, send=0.75, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    mx.bus("gong", -13.0, send=0.55)
    build(mx)
    hall = ModFDNReverb(rt60=4.2, rt60_high=1.8, predelay=0.035, size=1.15, mod_depth=10.0, mod_rate=0.4,
                        early_level=0.28, lowcut=90.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-1.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, None, None)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"shell_shrine_interior: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  "
              f"TP {m['true_peak_dbtp']:.2f} dBTP  limiter {rep}  buses {mx.bus_lufs}")
    return m


if __name__ == "__main__":
    render()
