"""`heart_approach` and `heart_rest`: Ch21 H01–H02 and R1, the last layer and the save point before Sefir (M5-A3P-1951;
act3_ending.md H01, H02, R1; ADR 0208). Both loop.

Original composition for this project (SPEC §2). The one tune in it is the game's own and is loaded, never retyped:
the first verse's first line (hush_first_verse.py `VERSE`, the Hush's first phrase as it is sung), here backwards.

The brief (act3_ending.md): H01 "*Music:* `heart_approach`, a low drone with the Hush theme's first phrase played
backwards, very slow." "Everything in the frame drifts down and inward, toward the heart." H02 thins it to silence on
Sefir's first word (the scene's `@music silence`). R1: "`heart_rest`, the drone only."

**heart_approach** (a loop of 72 s):
* the drone: the heart's own low A (A1, E2, A2) in low strings and a breath of filtered air, its colour sinking in
  slow waves, as everything in the frame sinks;
* the Hush's first phrase backwards in two senses. Its notes are taken last to first (A G A | C D E: the fall now
  climbs, but toward nothing). Each is a piano note rendered whole, soundboard and room included, and then reversed
  in time, so it swells out of nothing and stops dead where the hammer would have struck. Very slow: one of the
  verse's beats lasts 4 s. The phrase is said twice a loop, the second time an octave lower, deeper in;
* nothing else: no pulse, no voice.

**heart_rest** (a loop of 48 s): the drone alone, the same heart, a little closer and quieter (R1: the party stands in
silence; Asha looks at her full sleeve for the last time).

A minor (the heart's A, the Hush's key), unmetred.

Render:  python3 assets_src/music/act3/heart.py   (both; or tools/audio/render_all.py --only act3/heart)
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
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.grand import PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FV = _load("hush_first_verse")
OUT_DIR = os.path.join(ROOT, "assets", "audio", "act3", "music")
OUT = os.path.join(OUT_DIR, "heart_approach.ogg")
OUT_REST = os.path.join(OUT_DIR, "heart_rest.ogg")
SEED = 20261033
TARGET_LUFS = -16.0
LOOP_S = 72.0
REST_LOOP_S = 48.0
SLOW_BEAT = 4.0              # one of the verse's beats, very slow
PHRASE_AT = (6.0, 40.0)      # the two statements in a loop; the second an octave lower
# From measured bus loudness: the drone strings and the reversed piano level at L (the swells end at full strength, so
# the piano stays level with the drone, never over it: momentary max about -9.6 LUFS), the air L-8.
GAINS = {"piano": 20.9, "drone": 10.4, "air": -11.5}
# heart_rest: the drone at L, the air L-10.
REST_GAINS = {"drone": 0.0, "air": -22.9}


def backwards_phrase() -> list[tuple[str, float]]:
    """The first verse's first line, last note first (its rhythm reversed with it)."""
    return list(reversed([(p, float(b)) for p, b in FV.VERSE[0]]))


def reversed_piano(m: float, dur: float, vel: float, seed: int) -> np.ndarray:
    """A piano note rendered whole (bridge, soundboard, pedal down) and turned round: it swells out of nothing for
    `dur` seconds and stops where the hammer would have struck."""
    pedal = PedalCurve(np.array([0.0, dur + 4.0]), np.array([1.0, 1.0]))
    x = grand_note(m, vel, key_up=dur, seed=seed, pedal=pedal)
    x = x[: int((dur + 0.02) * SR)]
    st = np.stack([x, x], axis=1)
    y = PianoBody(pedal, seed=seed % 9973)(st)[: len(x)]
    fade = int(0.012 * SR)
    y[:fade] *= np.linspace(0.0, 1.0, fade)[:, None]
    return y[::-1].copy()


def drone(length: float, seed: int, closer: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """The heart's low A in strings, and a breath of air whose colour sinks in slow waves. (strings, air)"""
    g = rng(seed)
    strings = pad_chord([n("A1"), n("E2"), n("A2")] + ([n("E3")] if closer else []), length, vel=0.5, seed=seed,
                        attack=4.0, release=4.0, voices=4, spread_cents=6.0)[: int(length * SR)]
    N = int(length * SR)
    t = np.arange(N) / SR
    noise = g.standard_normal((N, 2))
    air = np.zeros((N, 2))
    # three overlapping bands, each falling an octave over its wave and fading in and out, so the colour keeps sinking
    period = length / 3.0
    for k in range(3):
        u = ((t / period) + k / 3.0) % 1.0
        fc = 900.0 * 2 ** (-u)
        w = np.sin(np.pi * u) ** 2
        for c in range(2):
            band = np.zeros(N)
            for s in range(0, N, int(0.25 * SR)):                     # the band's centre stepped every 250 ms
                e = min(N, s + int(0.25 * SR))
                band[s:e] = filt(noise[s:e, c], [bq_bandpass(float(fc[s]), 1.4)])
            air[:, c] += band * w
    return strings, 0.25 * air


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("piano", GAINS["piano"], send=0.55, process=lambda x: filt(x, [bq_highpass(60, 0.7)]))
    mx.bus("drone", GAINS["drone"], send=0.3, process=lambda x: string_body(x, cutoff=600.0))
    mx.bus("air", GAINS["air"], send=0.4, process=lambda x: filt(x, [bq_highpass(80, 0.7), bq_lowpass(1200, 0.7)]))
    strings, air = drone(LOOP_S + 8.0, SEED + 1)
    mx.add("drone", strings, -4.0)
    mx.add("air", air, -4.0)
    for si, t0 in enumerate(PHRASE_AT):
        t = t0
        for i, (p, beats) in enumerate(backwards_phrase()):
            d = beats * SLOW_BEAT
            m = float(n(p)) - 12 * si
            # the reversed note ends at its beat's end: it swells across the beat and stops on the next
            mx.add("piano", reversed_piano(m, d, 0.42 - 0.04 * si, SEED + 100 * si + i), t, pan=-0.15 + 0.06 * i)
            t += d
    hall = ModFDNReverb(rt60=6.0, rt60_high=1.5, predelay=0.05, size=1.5, mod_depth=8.0, mod_rate=0.25,
                        early_level=0.15, lowcut=50.0, width=0.75, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-2.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report={})
    _write(out_path, loop, LOOP_S)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"heart_approach: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    render_rest(os.path.join(os.path.dirname(out_path), os.path.basename(OUT_REST)), verbose=verbose, stats=stats)
    return m


def render_rest(out_path: str = OUT_REST, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=REST_LOOP_S, preroll_s=10.0)
    mx.bus("drone", REST_GAINS["drone"], send=0.25, process=lambda x: string_body(x, cutoff=700.0))
    mx.bus("air", REST_GAINS["air"], send=0.35, process=lambda x: filt(x, [bq_highpass(80, 0.7),
                                                                           bq_lowpass(1200, 0.7)]))
    strings, air = drone(REST_LOOP_S + 8.0, SEED + 2, closer=True)
    mx.add("drone", strings, -4.0)
    mx.add("air", air, -4.0)
    hall = ModFDNReverb(rt60=5.0, rt60_high=1.4, predelay=0.04, size=1.3, mod_depth=8.0, mod_rate=0.25,
                        early_level=0.18, lowcut=50.0, width=0.75, seed=SEED % 9973 + 1)
    _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
    # quieter than the approach: the save point's stillness (mix.md's bed level, -22)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS - 6.0, ceiling_db=-6.0, report={})
    _write(out_path, loop, REST_LOOP_S)
    m = measure(loop)
    if stats is not None:
        stats["rest_bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"heart_rest: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


def _write(out_path: str, loop: np.ndarray, loop_s: float) -> None:
    L = len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, None, 3)


if __name__ == "__main__":
    render()
