"""`hollowmere_answers`: Ch15 C4, dawn in fog: Liss sings a current-song and Hollowmere answers (M4-A2P-090;
act2_plan.md §2 Ch15; ADR 0204 §10; the cue sheet): about 60 s, through-composed, carrying into the `hollowmere`
zone loop.

Original composition for this project (SPEC §2, §9). The tune is our own: motifs.py CURRENT_SONG, Dace's
current-song, the Saltwright sung chart for reading water (imported, never retyped). The voices, horn and bells were
written for this scene. Nothing is taken from any existing music. Liss sings, though she is no Cantor: a current-song
is a work-song, not a rite (ADR 0204 §10; Narrative confirms in review).

The brief (act2_plan Ch15): at dawn in fog the unlamped barge drifts blind; Liss sings a current-song into the fog,
and Hollowmere answers. The flotilla is found by its people singing the same chart back. So:
* **the fog** (0-3 s): a low D drone, barely there;
* **Liss** (3-21 s): the whole song alone, close, its three phrases with a breath after each;
* **the silence** (21-23 s): nothing answers, for two seconds;
* **Hollowmere answers** (23-38 s): the first phrase sung back by many voices far off across the water, a horn on a
  held D under them, and the flotilla's bells;
* **together** (38-58 s): the second and third phrases, Liss close and the flotilla far, home to D, the bells
  again; it rings into the `hollowmere` loop (D Dorian, the same mode).

D Dorian at CURRENT_SONG_BPM (76). The cue row's `beat` grid follows it. Vorbis q3, -16 LUFS integrated. Plain git
(ADR 0175).

Render:  python3 tools/audio/render_all.py --only hollowmere_answers
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import CURRENT_SONG, CURRENT_SONG_BPM  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import sing  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "hollowmere_answers.ogg")
SEED = 20261990
TARGET_LUFS = -16.0
BEAT = 60.0 / CURRENT_SONG_BPM
LISS_AT = 3.0
ANSWER_AT = 23.0
TOGETHER_AT = 38.0
BREATH_BEATS = 1.0
VOWELS = ["a", "o", "a", "e", "o", "a", "u"]
GAINS = {"liss": 0.0, "flotilla": -5.0, "horn": -9.0, "bells": -10.0, "drone": -14.0}


def phrase_line(phrase: list, t0: float) -> tuple[list, list, float]:
    """A phrase as sing()'s phonemes and pitches, starting at t0; returns them and the end time."""
    ph = [(VOWELS[i % len(VOWELS)], b * BEAT) for i, (_, b) in enumerate(phrase)]
    pi = [(float(m), b * BEAT) for m, b in phrase]
    return ph, pi, t0 + sum(b for _, b in phrase) * BEAT


def add_singer(mx: Mixer, bus: str, phrases: list, t0: float, seed: int, vel: float, scale: float, pan: float,
               cents: float = 0.0) -> float:
    t = t0
    for k, phrase in enumerate(phrases):
        ph, pi, end = phrase_line(phrase, t)
        pi = [(m + cents / 100.0, d) for m, d in pi]
        x = sing(ph, pi, vel=vel, seed=seed + k, scale=scale, vib_cents=14.0)
        mx.add(bus, x, t, pan=pan)
        t = end + BREATH_BEATS * BEAT
    return t


def build(mx: Mixer) -> None:
    g = rng(SEED)
    total = TOGETHER_AT + 24.0
    drone = pad_chord([38.0, 45.0, 50.0], total, 0.35, seed=SEED + 1, attack=3.0, release=4.0)   # D2 A2 D3
    mx.add("drone", drone, 0.0)
    add_singer(mx, "liss", CURRENT_SONG, LISS_AT, SEED + 10, 0.6, 1.17, -0.1)                 # Liss, close
    for v in range(7):                                                                           # the flotilla, far
        add_singer(mx, "flotilla", CURRENT_SONG[:1], ANSWER_AT + float(g.uniform(0, 0.25)), SEED + 100 + 10 * v,
                   0.5, float(g.choice([1.0, 1.17])), float(g.uniform(-0.9, 0.9)), cents=float(g.normal(0, 8)))
        add_singer(mx, "flotilla", CURRENT_SONG[1:], TOGETHER_AT + float(g.uniform(0, 0.25)), SEED + 200 + 10 * v,
                   0.5, float(g.choice([1.0, 1.17])), float(g.uniform(-0.9, 0.9)), cents=float(g.normal(0, 8)))
    add_singer(mx, "liss", CURRENT_SONG[1:], TOGETHER_AT, SEED + 20, 0.6, 1.17, -0.1)
    mx.add("horn", breath_flute(50.0, 12.0, 0.5, seed=SEED + 30, breath=0.4, vib_cents=4.0, swell=0.3, attack=1.0,
                                release=2.0), ANSWER_AT + 0.5, pan=0.4)                         # the horn on D3
    mx.add("horn", breath_flute(50.0, 16.0, 0.5, seed=SEED + 31, breath=0.4, vib_cents=4.0, swell=0.2, attack=1.0,
                                release=3.0), TOGETHER_AT + 0.5, pan=0.4)
    for k, (t, m) in enumerate(((ANSWER_AT + 1.0, 62.0), (ANSWER_AT + 4.5, 57.0), (TOGETHER_AT + 2.0, 62.0),
                                (TOGETHER_AT + 16.0, 50.0), (TOGETHER_AT + 18.5, 57.0))):
        mx.add("bells", tower_bell(m, 0.5, seed=SEED + 40 + k, t60=8.0, dark=0.5), t, pan=float(g.uniform(-0.8, 0.8)))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(TOGETHER_AT + 30.0)
    mx.bus("liss", GAINS["liss"], send=0.35, process=lambda x: filt(x, [bq_highpass(180, 0.7), bq_lowpass(6500, 0.7)]))
    mx.bus("flotilla", GAINS["flotilla"], send=0.85, process=lambda x: filt(x, [bq_highpass(150, 0.7),
                                                                               bq_lowpass(2200, 0.7)]))   # across water
    mx.bus("horn", GAINS["horn"], send=0.7, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.bus("bells", GAINS["bells"], send=0.7, process=lambda x: filt(x, [bq_lowpass(4000, 0.7)]))
    mx.bus("drone", GAINS["drone"], send=0.5, process=lambda x: string_body(x, cutoff=700.0))
    build(mx)
    fog = ModFDNReverb(rt60=4.0, rt60_high=0.9, predelay=0.08, size=2.0, mod_depth=10.0, mod_rate=0.25,
                       early_level=0.1, lowcut=90.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=fog, reverb_return_db=-1.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(3.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
    if verbose:
        print(f"hollowmere_answers: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
