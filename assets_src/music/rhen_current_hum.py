"""`rhen_current_hum`: Ch1 C1-06, Rhen humming the current-song as he rides the shaft (M3-AUD-819; act1_ch01.md §6).

Original material (SPEC §2): the tune is Dace's current-song as written once in motifs.py (CURRENT_SONG, phrase 1:
"sound, sound, the set rising"), our own working chart in D dorian, composed for this project and not derived from
any existing melody. This file only performs it; it never re-types its notes.

The brief: "Diegetic, one pass. Rhen humming the current-song under his breath as he rides the shaft. This is the
motif of the chapter, and of Dace." It binds three later cues (`going_under` in C1-15, Ch8's `current_song`, act3
E2's `goodbye_dace`), so the phrase is stated plainly, with its two "soundings" (the D struck twice, as a leadsman
calls a depth) heard as two separate hums, not one long note.

Layers (all synthesized; no samples):
* **Rhen**: one young man's voice (synth.voice.sing), mouth closed ("m"), an octave under the motif's written
  pitch (D3-A3, where a man hums without thinking about it), soft phonation, light vibrato, a little scoop into
  the long notes. Each note is re-articulated with a small dip of breath, the repeated D most of all;
* **his breath**: an in-breath before he starts, and a short train of bubbles (his exhale through the mask's valve,
  the same Minnaert bubbles as lamp_diver) between the two passes;
* **the shaft**: a close, slightly closed-in voice (the mask) in a small, dark stone tube (a short reverb).

Form (~15 s, one pass, not a loop): the breath in | phrase 1, at the motif's tempo with a working man's rubato, the
held A leaned on | a breath and the bubbles | phrase 1 once more, fainter and a little slower, his attention going up
the shaft to the light; the last A thins out to nothing. The script crossfades to `oruvel_raft` over the second pass
(ch01_current_shaft.dlg: `@wait 6.0`, then U09), so the hum sinks under the town's music as he surfaces.

Render:  python3 assets_src/music/rhen_current_hum.py   (or tools/audio/render_all.py --only rhen_current_hum)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from motifs import phrases_in_seconds  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import sing  # noqa: E402
from synth.water import bubble  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "rhen_current_hum.ogg")
SEED = 20261819
TARGET_LUFS = -16.0
OCTAVE = -12.0             # hummed an octave under the motif's written pitch
T0 = 0.75                  # the in-breath comes first
GAP_S = 2.6                # the breath (and the bubbles) between the passes
## Rubato: each note's stretch (the soundings even, the climb pressed on, the held A leaned on)
LEAN = [1.0, 1.04, 1.06, 0.97, 0.98, 1.02, 1.22]


def phrase_notes(t0: float, slow: float) -> list[tuple[float, float, float]]:
    """[(t, dur, midi)] of motifs.CURRENT_SONG phrase 1 from t0, with the rubato above, slowed by `slow`."""
    out, t = [], t0
    for (m, d), lean in zip(phrases_in_seconds()[0], LEAN):
        dur = d * lean * slow
        out.append((t, dur, m + OCTAVE))
        t += dur
    return out


def hum_pass(notes: list[tuple[float, float, float]], vel: float, seed: int, fade_last: bool) -> np.ndarray:
    """One pass of the phrase as one breath: a closed-mouth hum, each note re-articulated by a dip of breath."""
    g = rng(seed)
    t0 = notes[0][0]
    pitches = []
    for i, (t, d, m) in enumerate(notes):
        scoop = 0.18 if d > 0.6 else 0.0                       # a little scoop up into the long notes
        if scoop:
            pitches += [(m - scoop, 0.07), (m, d - 0.07)]
        else:
            pitches.append((m, d))
    total = sum(d for _, d in pitches)
    y = sing([("m", total)], pitches, vel=vel, seed=seed, scale=1.06, tilt=2.05, breath=0.14, vib_cents=9.0,
             vib_rate=4.9, jitter_cents=5.0, release=0.35)
    tt = np.arange(len(y)) / SR
    env = np.ones(len(y))
    for i in range(1, len(notes)):
        on = notes[i][0] - t0
        same = notes[i][2] == notes[i - 1][2]
        depth = 0.62 if same else 0.28                          # the second sounding: a separate hum
        env *= 1.0 - depth * np.exp(-((tt - on + 0.012) / 0.038) ** 2)
    if fade_last:                                              # the last A thins out as he looks up
        last = notes[-1][0] - t0
        env *= np.where(tt > last + 0.3, np.exp(-(tt - last - 0.3) / 1.3), 1.0)
    env *= 1.0 + 0.04 * np.sin(2 * np.pi * float(g.uniform(0.3, 0.5)) * tt)
    return y * env


def in_breath(g) -> np.ndarray:
    """A quiet breath in through the nose before he starts: soft band noise rising and cut off."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    x = filt(g.standard_normal(n), [bq_bandpass(1300.0, 0.7), bq_highpass(400.0, 0.7), bq_lowpass(4000.0, 0.7)])
    env = np.clip(t / 0.4, 0, 1) ** 1.5 * np.clip((0.55 - t) / 0.08, 0, 1)
    return x / (np.std(x) + 1e-9) * env * 0.02


def bubble_train(g, count: int) -> np.ndarray:
    """His exhale: a short run of small bubbles leaving the mask's valve and rising past him."""
    out = np.zeros(int(1.4 * SR))
    for k in range(count):
        b = bubble(float(g.uniform(1.4, 4.0)), float(g.uniform(0.3, 1.0)), rise=0.16)
        s = int((k * 0.075 + float(g.uniform(0.0, 0.035))) * SR)
        e = min(len(out), s + len(b))
        out[s:e] += b[: e - s]
    return out


def mask(x: np.ndarray) -> np.ndarray:
    """The voice close and slightly closed-in: the mask's small cavity (a low-mid bump), the top rolled off."""
    return filt(x, [bq_highpass(85.0, 0.7), bq_peak(420.0, 2.5, 1.2), bq_peak(2600.0, -3.0, 1.0),
                    bq_lowpass(3400.0, 0.7)])


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]): Rhen at L; his breath (the
## in-breath and the bubbles) about L-14, heard only in the gaps.
GAINS = {"voice": 0.0, "breath": -21.7}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    first = phrase_notes(T0, 1.0)
    end1 = first[-1][0] + first[-1][1]
    second = phrase_notes(end1 + GAP_S, 1.15)
    end2 = second[-1][0] + second[-1][1]
    length = end2 + 5.5
    mx = Mixer(length)
    mx.bus("voice", GAINS["voice"], send=0.30, process=mask)
    mx.bus("breath", GAINS["breath"], send=0.25, process=lambda x: filt(x, [bq_highpass(250.0, 0.7),
                                                                             bq_lowpass(3500.0, 0.7)]))
    mx.add("breath", in_breath(g), T0 - 0.62, pan=-0.02)
    mx.add("voice", hum_pass(first, 0.62, SEED + 1, False), T0, pan=-0.04)
    mx.add("breath", bubble_train(g, 9), end1 + 0.35, pan=0.15)
    mx.add("breath", in_breath(g) * 0.7, second[0][0] - 0.6, pan=-0.02)
    mx.add("voice", hum_pass(second, 0.62 * 10 ** (-6.5 / 20), SEED + 2, True), second[0][0], pan=-0.04)
    shaft = ModFDNReverb(rt60=1.5, rt60_high=0.6, predelay=0.012, size=0.55, mod_depth=6.0, mod_rate=0.5,
                         early_level=0.4, lowcut=120.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=shaft, reverb_return_db=-4.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(1.5 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=4.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["second_pass_s"] = second[0][0]
    if verbose:
        print(f"rhen_current_hum: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  second pass at {second[0][0]:.2f}s")
        print("  buses (LU vs the voice)", {k: round(v - bus_lufs["voice"], 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
