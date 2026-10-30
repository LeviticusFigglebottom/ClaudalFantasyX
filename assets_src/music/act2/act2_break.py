"""`act2_break`: Ch16 C9, the act break (M4-A2P-090; act2_plan.md §2 Ch16; the cue sheet): about 90 s, a bed for
Rhen's voice-over after the storm has swept the party away. Spent, honest, still going.

Original composition for this project (SPEC §2, §9). The only lines here are our own: the Hush's first phrase
(hush_theme_v2.py MEL_A) and the Letting's first cell (motifs.letting(), MEL_A's cell turned upward), both imported,
never retyped. Nothing is taken from any existing music.

The brief (act2_plan Ch16): the storm wakes early at the Choir, Kerrid holds the line, the party is swept away; then
the act break, Rhen speaking over black. So the cue is a bed for a voice, as Act I's iskarra_vigil:
* a low drone on A, breathing, under 700 Hz;
* the Hush's first phrase on the breath flute, alone, slow, far, with long silences between its halves, as if
  remembered;
* at the end, the Letting's cell once, on the same flute, up to its held E, unresolved: the Act III answer, heard
  before anyone can name it;
* the voice band is left open; the flute sits above it and away from the words.

A minor, free (the cue row's `beat` is "free"). About 90 s, ending on the held E and then silence. Vorbis q3,
-16 LUFS integrated. Plain git (ADR 0175).

Render:  python3 tools/audio/render_all.py --only act2_break
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import letting  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _mod("hush_theme_v2", os.path.join(MUSIC, "hush_theme_v2.py"))   # MEL_A
V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))          # periodic_drone()

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "act2_break.ogg")
SEED = 20262010
TARGET_LUFS = -16.0
BEAT = 1.15                         # slow and free: a beat of the remembered phrase
LENGTH_S = 88.0
HALVES = [(8.0, 0, 6), (26.0, 6, 12)]      # (start s, MEL_A from, to): its two halves, a long silence between
LETTING_AT = 62.0
FLUTE_PRE = 0.065
GAINS = {"drone": -6.0, "flute": 0.0}


def flute(mx: Mixer, notes: list, t0: float, seed: int, vel: float) -> float:
    pos = t0
    for i, (p, beats) in enumerate(notes):
        d = beats * BEAT
        last = i == len(notes) - 1
        x = breath_flute(n(p), d + (6.0 if last else 0.0), vel, seed=seed + i, breath=0.3, scoop_cents=20.0,
                         vib_cents=10.0 if beats >= 1 else 3.0, swell=0.15 if beats >= 2 else 0.0, attack=0.12,
                         release=2.5 if last else 0.4)
        mx.add("flute", x, pos - FLUTE_PRE, pan=0.15)
        pos += d
    return pos


def build(mx: Mixer) -> None:
    g = rng(SEED)
    drone = V.periodic_drone(LENGTH_S, [(n("A1"), 1.0), (n("E2"), 0.4), (n("A2"), 0.3)], SEED + 1, partials=4,
                             breath_s=11.0)
    k = int(6.0 * SR)
    drone[:k] *= np.linspace(0, 1, k)[:, None] ** 2
    drone[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    mx.add("drone", drone, 0.0)
    for start, a, b in HALVES:
        flute(mx, [(p, beats) for p, beats, *_ in HUSH.MEL_A[a:b]], start, SEED + 10 + a,
              0.42 * float(g.uniform(0.97, 1.02)))
    flute(mx, letting(), LETTING_AT, SEED + 50, 0.45)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(LENGTH_S + 10.0)
    mx.bus("drone", GAINS["drone"], send=0.4, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
    mx.bus("flute", GAINS["flute"], send=0.6, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(6000, 0.7)]))
    build(mx)
    far = ModFDNReverb(rt60=5.0, rt60_high=1.2, predelay=0.07, size=1.8, mod_depth=10.0, mod_rate=0.25,
                       early_level=0.1, lowcut=80.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=far, reverb_return_db=-1.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(4.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
    if verbose:
        print(f"act2_break: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
