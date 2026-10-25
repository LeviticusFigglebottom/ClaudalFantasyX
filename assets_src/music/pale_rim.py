"""`pale_rim`: Ch16 "The Edge of the World", the Pale Rim, the white shallows (M3-AUD-805; act_outline Ch16): a 61 s
seamless loop. An Act II sketch, for the human to judge the direction.

Original composition for this project (SPEC §2, §9). Original-material check: the flute's three short calls (B-E;
F#-E-B; C#-B, then A# once) were written for this cue and share no phrase with the game's other themes or any
melody we know. The style evoked is a near-static drone piece with a distant wind voice; nothing is quoted.

The brief: the southern edge of the known sea. Days of wading, ankle- to waist-deep, over white sand under a white
sky; the horizon goes white. Kerrid walks last in the line, as on a stair, behind Asha, toward the Choir where the
woman he got up his stair was spent. Bleached, vast, almost silent.

So the cue is mostly air. E, with no third at all for most of the loop (only fifths and octaves: no colour, the
white), 4/4 at 51 BPM (a bar is 4.71 s), 13 bars. A halo of high, pure tones (E6, B6, E7 and a faint F#7) beats slowly,
like glare. Under it, far down, an open fifth on E. The only motion is the party's wading: a soft swash of water at
every step, at walking pace through the shallows, a little irregular (five walkers, one of them a step behind). The
flute is very far off and plays three short calls in thirteen bars, with long silences between. In bar 10 it touches
A# (the raised fourth) and G# (the loop's only third): the white turned, for a moment, toward something.

Ensemble (all synthesized; no samples):
* the halo: high sine doublets (every frequency snapped to whole cycles per loop, so it is exactly periodic),
  breathing slowly;
* the floor: E1-B1-E2 as a dark sine fifth, barely there;
* wading: filtered-noise swashes with a few small bubbles, each walker a step every beat and a half;
* breath flute, far off (heavily reverbed, high-cut): the three calls, bars 3, 7 and 10.

Form (bars): 1-2 the halo and the wading | 3-4 the first call (B, E) | 5-6 wading | 7-8 the second call (F#, E, B) |
9 wading | 10-11 the third call (C#, B; A#, G#, B) | 12-13 wading, which is bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), between two steps, so the seam falls in the halo alone.

Render:  python3 assets_src/music/pale_rim.py   (or tools/audio/render_all.py --only pale_rim)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "pale_rim.ogg")
SEED = 20261613
TARGET_LUFS = -16.0
BPM = 51.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 13
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
QUALITY = 3.0  # mix.md §5's sparse-cue quality

## the halo: (note, level, doublet split in Hz)
HALO = [("E6", 1.0, 0.21), ("B6", 0.6, 0.33), ("E7", 0.35, 0.45), ("F#7", 0.12, 0.6)]
FLOOR = [("E1", 1.0), ("B1", 0.6), ("E2", 0.45)]
## the calls: (bar, beat, [(pitch, beats)])
CALLS = [(3, 0.5, [("B4", 2), ("E5", 5)]),
         (7, 1.0, [("F#5", 1.5), ("E5", 1.5), ("B4", 4)]),
         (10, 0.0, [("C#5", 2), ("B4", 2), ("A#4", 1), ("G#4", 1), ("B4", 5)])]

# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], the whole loop) for these levels
# relative to the flute (0 LU; it plays about five bars of thirteen): the halo -4, the floor -8, the wading -8.
GAINS = {"flute": 0.0, "halo": -23.0, "floor": -20.2, "wade": -12.2}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def sustained(L: int, partials: list, seed: int, cycles: tuple[int, int] = (2, 5)) -> np.ndarray:
    """Sine doublets (note, level[, split Hz]) held for the whole loop, each frequency snapped to whole cycles per
    loop and each level breathing on its own whole-cycle LFO, so the result is exactly periodic. Stereo, peak 1."""
    g = rng(seed)
    t = np.arange(L) / SR
    Ls = L / SR
    out = np.zeros((L, 2))
    for row in partials:
        p, a = row[0], row[1]
        split = row[2] if len(row) > 2 else 0.12
        f = round(midi_to_hz(n(p)) * Ls) / Ls
        s = max(1, round(split * Ls)) / Ls
        lfo = 0.75 + 0.25 * np.cos(2 * np.pi * int(g.integers(*cycles)) * t / Ls + g.uniform(0, 6.28))
        for ch in range(2):
            ph0, ph1 = g.uniform(0, 2 * np.pi, 2)
            out[:, ch] += a * lfo * 0.5 * (np.sin(2 * np.pi * f * t + ph0) + np.sin(2 * np.pi * (f + s) * t + ph1))
    return out / np.abs(out).max()


def wade(seed: int, vel: float) -> np.ndarray:
    """One step through shallow water: a leg pushing through (a soft swash of band-limited noise that rises and
    falls), the foot settling into sand, and two or three small bubbles. Mono, about 0.8 s."""
    g = rng(seed)
    N = int(0.8 * SR)
    t = np.arange(N) / SR
    env = np.clip(t / 0.09, 0, 1) ** 1.5 * np.exp(-np.clip(t - 0.09, 0, None) / 0.18)
    nz = filt(g.standard_normal(N), [bq_bandpass(float(g.uniform(700, 1100)), 0.7), bq_lowpass(3500, 0.7)])
    y = nz / (np.std(nz) + 1e-9) * env
    for _ in range(int(g.integers(2, 4))):
        b = bubble(float(g.uniform(1.5, 3.5)), float(g.uniform(0.3, 0.7)))
        k = int(g.uniform(0.08, 0.4) * SR)
        m = min(len(b), N - k)
        y[k: k + m] += b[:m]
    return vel * y / (np.abs(y).max() + 1e-9)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("halo", sustained(mx.L, HALO, SEED + 1, cycles=(3, 7)), 0.0)
    mx.add("floor", sustained(mx.L, FLOOR, SEED + 2, cycles=(2, 4)), 0.0)
    # wading: five walkers, a step every 1.5 beats each, each on its own phase; the last one (Kerrid) a little behind
    steps = int(round(BARS * 4 / 1.5))
    for w in range(5):
        phase = (0.2 + 0.29 * w) % 1.5
        for k in range(steps):
            beat = (phase + 1.5 * k) % (BARS * 4)
            if beat > BARS * 4 - 0.6 or beat < 0.6:     # nobody's foot lands at the seam
                continue
            v = (0.55 if w < 4 else 0.4) * g.uniform(0.7, 1.05)
            mx.add("wade", wade(SEED + 100 + 1000 * w + k, v), beat * BEAT + float(g.normal(0, 0.05)),
                   pan=float(-0.5 + 0.25 * w + g.normal(0, 0.05)))
    for i, (bar, beat, notes) in enumerate(CALLS):
        pos, first = t_of(bar, beat), True
        for p, beats in notes:
            d = beats * BEAT
            x = breath_flute(n(p), d * 0.95, 0.42 * g.uniform(0.95, 1.04), seed=SEED + 500 + int(pos * 100),
                             breath=0.6, scoop_cents=40.0 if first else 12.0, vib_cents=6.0, vib_rate=4.2,
                             swell=0.4 if beats >= 4 else 0.15, attack=0.2 if first else 0.1, release=1.2, beta=0.5)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.01)), pan=0.35 - 0.3 * i)
            pos += d
            first = False


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=14.0)
    G = GAINS
    mx.bus("flute", G["flute"], send=0.85, process=lambda x: filt(x, [bq_highpass(250, 0.7), bq_lowpass(3200, 0.7)]))
    mx.bus("halo", G["halo"], send=0.4)
    mx.bus("floor", G["floor"], send=0.1, process=lambda x: filt(x, [bq_lowpass(300, 0.7)]))
    mx.bus("wade", G["wade"], send=0.2, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_lowpass(2600, 0.7)]))
    build(mx)
    white = ModFDNReverb(rt60=7.0, rt60_high=2.0, predelay=0.08, size=1.8, mod_depth=12.0, mod_rate=0.2,
                         early_level=0.05, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=white, reverb_return_db=-1.0)
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"pale_rim: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
