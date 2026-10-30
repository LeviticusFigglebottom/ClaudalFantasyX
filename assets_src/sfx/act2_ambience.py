"""Act II's ambience beds (M4-A2P-093, ADR 0205; plain git under assets/audio/act2/ambience/, ADR 0175).

Each bed is a seamless loop built as act1_final_ambience.py builds Act I's (LoopMixer, field_ambience's sources,
-26 LUFS integrated with peaks well down, about 10 LU under its zone's music; mix.md), from its environment sheet and
the cue sheet (docs/kb/plan/act2/audio/act2_cue_sheet.md §4). New beds go at the end of BEDS: each bed's seed is its
index, so appending keeps every earlier bed byte-identical.

    fen_dusk           Ch10, Ossa Fen (art/environments/ossa_fen.md): mangrove channels at dusk, root-walks over tannin
                       water. The dusk insect chorus, frogs in the roots, drips into still brown water, the roots
                       creaking, water lapping under the walks, and a fen bird far off. Fireflies are seen, not heard.
    reedhollow_roost   Ch10, Reedhollow, the Kirru roost-village: woven reed lodges on mangrove roots round a lagoon.
                       Reed wind through the screens, the lagoon under the platforms, lodges creaking, a cook-fire, and
                       the clutch's wordless hum far across the water (a line in the Kirru mode on A, A B C# D# F#
                       with no E, written for this bed: the Kirru sing without words; they are a people, act2_roster).

assets/audio/act2/ambience/<bed>.ogg + .loop.json (stereo, Vorbis q1 like the Act I beds; the rule
`act2/ambience/*.ogg`: -26 LUFS integrated +- 0.5, true peak under -5 dBTP). Synthesized here and in tools/audio/synth/
(SPEC §2, §9): no samples, no recordings, no generated audio.

Render:  python3 tools/audio/render_all.py --only act2_ambience
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.water import drip  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(HERE, "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "ambience")
SEED = 20261900
TARGET_LUFS = -26.0
CEILING_DB = -6.0
QUALITY = 1.0
LOOPS = {"fen_dusk": 48.0, "reedhollow_roost": 46.0}
# The Kirru mode on A (reedhollow.py): A B C# D# F#, G# only as the top of a rise; never E.
KIRRU = {"A3": 57, "B3": 59, "C#4": 61, "D#4": 63, "F#4": 66, "F#3": 54, "G#4": 68}


def _mixer(name: str) -> tuple[LoopMixer, int]:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOPS[name], preroll_s=6.0)
    return mx, mx.L


def _room(seed: int, rt60: float, size: float, highcut: float = 7000.0) -> ModFDNReverb:
    return ModFDNReverb(rt60=rt60, rt60_high=rt60 * 0.45, predelay=0.03, size=size, mod_depth=6.0, mod_rate=0.3,
                        early_level=0.3, lowcut=120.0, highcut=highcut, seed=seed)


# --------------------------------------------------------------------------- sources


def creak(g, dur: float, lo: float, hi: float) -> np.ndarray:
    """Wet wood working: a mangrove root or a lodge's lashing under weight."""
    return FA.stick_slip(g, dur, lo, hi, [(240.0, 1.0), (610.0, 0.55), (1300.0, 0.2)])


def croak(g) -> np.ndarray:
    """A fen frog: a short rattle of throat pulses through a low formant, two or three times."""
    rate = float(g.uniform(16, 26))
    f = float(g.uniform(420, 820))
    out = np.zeros(int(1.4 * SR))
    for k in range(int(g.integers(1, 4))):
        n = int(float(g.uniform(0.18, 0.32)) * SR)
        t = np.arange(n) / SR
        pulses = (np.sin(np.pi * rate * t) ** 8) * np.sin(np.pi * t / t[-1])
        body = filt(g.standard_normal(n), [bq_bandpass(f, 3.0), bq_bandpass(f * 2.1, 2.0)])
        y = pulses * body / (np.abs(body).max() + 1e-9)
        s = int((k * float(g.uniform(0.36, 0.5))) * SR)
        out[s: s + n] += y[: len(out) - s]
    return out


def dusk_buzz(L: int, g, carrier: float, am_hz: float) -> np.ndarray:
    """A dusk insect's continuous buzz: a narrow noise band pulsing fast, swelling and resting slowly (stereo)."""
    t = np.arange(L) / SR
    am = 0.55 + 0.45 * np.sin(2 * np.pi * FA.snap(am_hz, L) * t) ** 2
    swell = 0.5 + 0.5 * FA.plfo(L, 0.03, g)
    band = FA.stereo_noise(L, g, [bq_bandpass(carrier, 6.0), bq_lowpass(carrier * 1.4, 0.7)], 0.3)
    return band * (am * swell)[:, None]


def fen_bird(g) -> np.ndarray:
    """A fen bird far off at dusk: two falling whistled notes, the second lower and longer."""
    out = np.zeros(int(1.6 * SR))
    f0 = float(g.uniform(2100, 2700))
    for k, (ratio, dur) in enumerate(((1.0, 0.22), (0.78, 0.42))):
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = f0 * ratio * (1.0 - 0.06 * t / dur)
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.004 * np.sin(2 * np.pi * 22 * t))) / SR
        y = np.sin(ph) * np.sin(np.pi * t / dur) ** 1.5
        s = int((0.0 if k == 0 else 0.3) * SR)
        out[s: s + n] += y
    return out


def reed_rustle(g, sec: float) -> np.ndarray:
    """Reeds and woven screens moving in a gust: a dry, fibrous rustle swelling and falling."""
    n = int(sec * SR)
    t = np.arange(n) / n
    y = filt(g.standard_normal(n), [bq_bandpass(float(g.uniform(1800, 3200)), 0.9)])
    grain = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * float(g.uniform(25, 45)) * np.arange(n) / SR))
    return y * grain * np.sin(np.pi * t) ** 1.2


def fire(g, sec: float) -> np.ndarray:
    """A small cook-fire on a clay hearth: a low breathing flame with a few pops."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = 0.4 * filt(g.standard_normal(n), [bq_lowpass(700, 0.7), bq_highpass(90, 0.7)])
    y = y / (np.abs(y).max() + 1e-9) * 0.5
    for _ in range(int(sec * 3)):
        s = int(float(g.uniform(0, sec - 0.01)) * SR)
        k = int(0.004 * SR)
        y[s: s + k] += filt(g.standard_normal(k), [bq_highpass(1500, 0.7)]) * np.linspace(1, 0, k) * float(g.uniform(0.2, 0.7))
    return y * np.clip(t / 0.5, 0, 1) * np.clip((sec - t) / 0.5, 0, 1)


def clutch_line(loop_s: float) -> list[tuple[float, float]]:
    """The clutch's wordless hum, one loop long: slow phrases in the Kirru mode with breaths of silence (midi 0)."""
    phrases = [
        [("A3", 3.0), ("C#4", 2.0), ("B3", 2.5), ("A3", 3.5)],
        [("F#3", 2.5), ("A3", 2.0), ("B3", 4.0)],
        [("C#4", 2.0), ("D#4", 2.0), ("F#4", 3.0), ("D#4", 1.5), ("C#4", 2.0), ("B3", 4.0)],
    ]
    line: list[tuple[float, float]] = []
    for ph in phrases:
        line += [(float(KIRRU[n]), d) for n, d in ph]
        line.append((0.0, 2.5))
    used = sum(d for _, d in line)
    line[-1] = (0.0, line[-1][1] + (loop_s - used))  # the last breath fills the loop exactly
    return line


# --------------------------------------------------------------------------- the beds


def fen_dusk(g):
    mx, L = _mixer("fen_dusk")
    mx.bus("air", 0.0, send=0.05)
    mx.bus("insects", 0.0, send=0.25, process=lambda x: filt(x, [bq_lowpass(6500, 0.7)]))
    mx.bus("frogs", 0.0, send=0.3)
    mx.bus("water", 0.0, send=0.15)
    mx.bus("roots", 0.0, send=0.25)
    mx.bus("far", 0.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    mx.add("air", FA.stereo_noise(L, g, [bq_lowpass(300, 0.6), bq_highpass(40, 0.7)], 0.6) * 0.14, 0.0)  # humid air
    mx.add("insects", dusk_buzz(L, g, 4300.0, 31.0) * 0.05, 0.0)
    mx.add("insects", dusk_buzz(L, g, 5200.0, 43.0) * 0.03, 0.0)
    for _ in range(3):                                                     # crickets in the roots, each its own
        carrier = float(g.uniform(3600, 4600))
        period = float(g.uniform(0.6, 1.1))
        pan = float(g.uniform(-0.9, 0.9))
        for t in FA.schedule(L, period, g, 0.08):
            mx.add("insects", FA.cricket_chirp(g, carrier, int(g.integers(2, 4)), float(g.uniform(24, 32))), t,
                   pan=pan, gain=float(g.uniform(0.15, 0.35)))
    for t in FA.schedule(L, 3.1, g, 0.6):                                  # frogs, near and far
        mx.add("frogs", croak(g), t, pan=float(g.uniform(-0.9, 0.9)), gain=float(g.uniform(0.15, 0.5)))
    for t in FA.schedule(L, 0.9, g, 0.6):                                  # drips into the tannin water
        mx.add("water", drip(float(g.uniform(0.15, 0.5)), float(g.uniform(1.4, 3.0)), seed=int(g.integers(1 << 30))),
               t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.15, 0.4)))
    for t in FA.schedule(L, 2.2, g, 0.5):                                  # water lapping under the root-walks
        mx.add("water", FA.lap(g, float(g.uniform(0.5, 0.9))), t, pan=float(g.uniform(-0.6, 0.6)),
               gain=float(g.uniform(0.25, 0.6)))
    for t in FA.schedule(L, 5.5, g, 0.5):                                  # the roots creaking
        mx.add("roots", creak(g, float(g.uniform(0.6, 1.4)), 40, 180), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.2, 0.4)))
    for t in FA.schedule(L, 14.0, g, 0.4):                                 # a fen bird far off
        mx.add("far", fen_bird(g), t, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.15, 0.3)))
    return mx, _room(SEED % 9973 + 1, 1.1, 1.6, highcut=6000.0)


def reedhollow_roost(g):
    mx, L = _mixer("reedhollow_roost")
    mx.bus("wind", 0.0, send=0.1)
    mx.bus("reeds", 0.0, send=0.2)
    mx.bus("water", 0.0, send=0.15)
    mx.bus("lodges", 0.0, send=0.3)
    mx.bus("clutch", 0.0, send=0.55, process=lambda x: filt(x, [bq_lowpass(2600, 0.7)]))
    gust = 0.5 + 0.5 * FA.plfo(L, 0.07, g)
    mx.add("wind", FA.stereo_noise(L, g, [bq_bandpass(1400, 0.5), bq_highpass(250, 0.7)], 0.4)
           * (0.35 + 0.65 * gust ** 1.3)[:, None] * 0.1, 0.0)
    for t in FA.schedule(L, 1.6, g, 0.6):                                  # reeds and woven screens in the gusts
        mx.add("reeds", reed_rustle(g, float(g.uniform(0.8, 1.8))), t, pan=float(g.uniform(-0.9, 0.9)),
               gain=float(g.uniform(0.1, 0.3)))
    for t in FA.schedule(L, 1.5, g, 0.5):                                  # the lagoon under the platforms
        mx.add("water", FA.slap(g) if g.random() < 0.4 else FA.lap(g, 0.8), t, pan=float(g.uniform(-0.8, 0.8)),
               gain=float(g.uniform(0.25, 0.6)))
    for t in FA.schedule(L, 4.0, g, 0.5):                                  # the lodges on their roots
        mx.add("lodges", creak(g, float(g.uniform(0.6, 1.2)), 60, 260), t, pan=float(g.uniform(-0.7, 0.7)),
               gain=float(g.uniform(0.15, 0.35)))
    mx.add("lodges", fire(g, LOOPS["reedhollow_roost"] - 1.0), 0.5, pan=-0.45, gain=0.12)  # a cook-fire
    hum = hum_ensemble(clutch_line(LOOPS["reedhollow_roost"]), voices=9, seed=int(g.integers(1 << 30)),
                       register="high", spread=0.9, loop=True)
    mx.add("clutch", hum[:L] * 0.25, 0.0)                                  # the clutch, far across the water
    return mx, _room(SEED % 9973 + 2, 1.4, 1.8, highcut=6000.0)


BEDS = {"fen_dusk": fen_dusk, "reedhollow_roost": reedhollow_roost}
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
    render()
