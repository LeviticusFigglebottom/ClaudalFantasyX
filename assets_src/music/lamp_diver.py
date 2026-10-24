"""`lamp_diver`: Ch1 "Lamp-Diver", the underwater dive (M3-AUD-01; act_outline.md Ch1): a 90 s seamless loop.

Original composition for this project (SPEC §2): written for this cue, not derived from any existing melody. Rhen's
salvage dive in a drowned tower, a tutorial dungeon in which his lantern lights the way. It has to sit with the
underwater look (M2-RND-02): murky, pressurised, cold, and one warm light.

D minor (Dorian colour, B natural), no meter you can tap: everything is slow and heavy, as heard through water.
* pressure: a sub drone (D1, A1) breathing on a 30 s cycle, low-passed hard; every frequency and LFO is snapped to
  whole cycles per loop, so it wraps exactly;
* the lantern: a warm sustained fifth (D3 A3, a soft string section, low-passed) that swells and recedes, and soft
  glints of a metallophone (D Dorian pentatonic) that ring a long time, dulled by the water;
* a heartbeat: a muffled low drum, two beats every 2.4 s, slowing slightly in the middle of the loop;
* bubble trains from Rhen's breath and the tower, every few seconds (Minnaert bubbles);
* far below, once a loop, a hint of the current-song: one long note and a fall of a third (the opening gesture of
  our own Hush theme, never its whole phrase), hummed by a single distant voice. The player shouldn't be sure it
  was there.
Every layer except the glints and the bubbles passes a low-pass near 900 Hz (the water's muffle) into a long, dark
reverb.

Render:  python3 assets_src/music/lamp_diver.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.water import bubble  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "lamp_diver.ogg")
SEED = 20261112
TARGET_LUFS = -16.0
LOOP_S = 90.0
GLINTS = [(3.0, "A5", .30), (9.5, "D6", .26), (17.0, "F5", .28), (24.5, "C6", .24), (31.0, "A5", .28),
          (40.0, "E6", .22), (46.5, "D6", .26), (55.0, "B5", .24), (63.0, "A5", .28), (70.5, "G5", .24),
          (78.0, "D6", .26), (85.0, "F5", .22)]
SWELLS = [(0.0, ["D3", "A3"], 22.0), (22.5, ["C3", "G3"], 22.0), (45.0, ["Bb2", "F3"], 22.0), (67.5, ["D3", "A3"], 22.0)]
CURRENT_SONG = (52.0, [("E3", 3.5), ("D3", 1.2), ("C3", 4.0)])


def _snap(f: float) -> float:
    return max(1.0, round(f * LOOP_S)) / LOOP_S


def pressure(sr: int = SR) -> np.ndarray:
    g = rng(SEED + 3)
    N = int(round(LOOP_S * sr))
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * _snap(1 / 30.0) * t)
    for root, lvl in ((n("D1"), 1.0), (n("A1"), 0.5), (n("D2"), 0.25)):
        f0 = midi_to_hz(root)
        for k, a in ((1, 1.0), (2, 0.35), (3, 0.12)):
            for side, det in ((0, 0.0), (1, 0.05 * k)):
                s = lvl * a * (0.7 + 0.3 * breath) * np.sin(2 * np.pi * _snap(f0 * k + det) * t + g.uniform(0, 6.28))
                out[:, side] += s
                out[:, 1 - side] += 0.7 * s
    return out * 0.05


def heart_times() -> list[float]:
    """Two beats (lub-dub) every period; the period stretches from 2.4 to 2.8 s mid-loop and back. Whole loop."""
    times, t = [], 0.4
    while t < LOOP_S - 2.2:
        period = 2.4 + 0.4 * np.sin(np.pi * t / LOOP_S) ** 2
        times += [t, t + 0.32]
        t += period
    return times


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("pressure", pressure(), 0.0)
    for t0, notes, dur in SWELLS:
        x = pad_chord([n(p) for p in notes], dur, 0.8, seed=SEED + int(t0 * 10), voices=4, attack=6.0, release=5.0)
        mx.add("lantern", x, t0)
    for i, (t0, p, v) in enumerate(GLINTS):
        x = metallophone_note(n(p), v, seed=SEED + 100 + i, decay=7.0, hardness=0.2, ombak_hz=3.0)
        mx.add("glint", x, t0, pan=float(g.uniform(-0.6, 0.6)))
    for i, t0 in enumerate(heart_times()):
        mx.add("heart", big_drum(0.55 if i % 2 == 0 else 0.35, variant=i, seed=SEED + 4), t0)
    tt = 1.0
    while tt < LOOP_S:
        train = np.zeros(int(1.6 * SR))
        for k in range(int(g.integers(5, 14))):
            b = bubble(float(g.uniform(1.5, 5.5)), float(g.uniform(0.3, 1.0)), rise=0.18)
            s = int((k * 0.07 + g.uniform(0, 0.04)) * SR)
            e = min(len(train), s + len(b))
            train[s:e] += b[: e - s]
        mx.add("bubbles", train, tt, pan=float(g.uniform(-0.5, 0.5)))
        tt += float(g.uniform(4.0, 9.0))
    t0, line = CURRENT_SONG
    x = hum_ensemble([(n(p), d) for p, d in line], voices=1, seed=SEED + 70, register="low", spread=0.0)
    env = np.ones(len(x))
    k = int(1.2 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    env[-k:] *= np.linspace(1, 0, k) ** 2
    mx.add("song", x * env[:, None], t0)


# Bus gains from measured bus loudness: the lantern swell is the lead (L), pressure L-3, the glints L-8 at their
# peaks (they are sparse), the heartbeat L-10, bubbles L-12, the current-song L-14 (barely there).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    muffle = [bq_highpass(30, 0.7), bq_lowpass(900, 0.6)]
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("lantern", 0.0, send=0.5, process=lambda x: filt(string_body(x, cutoff=1200.0), muffle))
    mx.bus("pressure", -3.9, send=0.2, process=lambda x: filt(x, muffle))
    mx.bus("glint", -3.4, send=0.7, process=lambda x: filt(x, [bq_lowpass(2600, 0.7)]))
    mx.bus("heart", -15.7, send=0.3, process=lambda x: filt(x, [bq_lowpass(260, 0.7)]))
    mx.bus("bubbles", -23.7, send=0.4, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_lowpass(3000, 0.7)]))
    mx.bus("song", -14.3, send=0.9, process=lambda x: filt(x, muffle))
    build(mx)
    deep = ModFDNReverb(rt60=5.0, rt60_high=0.8, predelay=0.04, size=1.4, mod_depth=12.0, mod_rate=0.3,
                        early_level=0.15, lowcut=60.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=deep, reverb_return_db=-2.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, None, None)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"lamp_diver: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
