"""`corrow_aftermath`: Ch8, the cut rope and the end of the chapter (M3-AUD-822; act1_ch08.md B18): a 62.4 s
seamless loop.

Original composition for this project (SPEC §2, §9). The counting figure below was written for this scene and is
not derived from any existing tune. Original-material check: it is one repeated note (B3) in groups of 3, 4, 5, 6
and 3, each group ending one step lower (A3, G3, F#3, E3) and the last on C#4; there is no melody to borrow, and none
we know is like it. The style evoked is a single plucked string in the rain; nothing is quoted.

The brief: "Rain, a single plucked string, very slow. It is not yet grief, just counting." 18:30: the storm has
gone on along the coast, the rain is easing, the low town is a black lake to the eaves, and on the surviving
wall-head the Stillguard are counting. Liss coils what is left of the rope ("Good rope. Seated true. She held."),
and Toma walks the shield-line asking after a name. So the string counts: one note on a slow pulse (25 a minute,
one every 2.4 s), in groups that grow by one each time, with a rest between groups, and the last count of each
group falls a step, as if the count were getting heavier. The last group stops short, on C#, and the loop starts
counting again. B minor is Corrow's key (corrow_seawall.py), and the B is its tonic, so the counting stands where
the town's music stood.

Ensemble (all synthesized; no samples):
* one plucked string (synth.electric.string_pluck through a small wooden body), open and long, played softly;
* the rain, easing but steady: a fine hiss, drops on stone and on water, the runoff off the wall's face;
* the storm going away down the coast: one far roll of thunder in the loop, very low.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file (26 pulses). The file starts 0.3 s before the first count (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in rain, not on a pluck.

Render:  python3 assets_src/music/corrow_aftermath.py   (or tools/audio/render_all.py --only corrow_aftermath)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "sfx"))

import numpy as np  # noqa: E402

from field_ambience import circ_noise, plfo, stereo_noise  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import drip  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "corrow_aftermath.ogg")
SEED = 20261825
TARGET_LUFS = -16.0
BPM = 25.0                    # the count's pulse
PULSE = 60.0 / BPM            # 2.4 s
LEAD_IN = 0.3                 # the file starts this long before the first count
## the count: groups of repeated B3, each group's last count on the note given; a rest pulse after each group
COUNT_NOTE = "B3"
GROUPS = [(3, "A3"), (4, "G3"), (5, "F#3"), (6, "E3"), (3, "C#4")]
PULSES = sum(k + 1 for k, _ in GROUPS)      # 26
LOOP_S = PULSES * PULSE
THUNDER_AT = 37.0
## the drops on stone are the peaks: a lower ceiling keeps the decoded true peak clear of -1 dBTP
CEILING_DB = -3.5


def counts() -> list[tuple[float, str, bool]]:
    """[(time s, pitch, last of its group)] over one loop."""
    out = []
    p = 0
    for k, last in GROUPS:
        for i in range(k):
            out.append((LEAD_IN + p * PULSE, last if i == k - 1 else COUNT_NOTE, i == k - 1))
            p += 1
        p += 1
    return out


def small_body(seed: int) -> np.ndarray:
    """A small wooden body (a few damped modes) as an impulse response."""
    g = rng(seed)
    t = np.arange(int(0.25 * SR)) / SR
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((105.0, 10, 0.8), (210.0, 12, 0.35), (390.0, 10, 0.4), (610.0, 8, 0.25), (1200.0, 6, 0.15)):
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t * np.pi * f / q) * 0.08
    return ir / np.abs(ir).max()


def add_string(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    body = small_body(SEED + 2)
    for i, (t, p, last) in enumerate(counts()):
        v = (0.31 if last else 0.30) * g.uniform(0.92, 1.06)
        x = string_pluck(n(p), PULSE * (1.6 if last else 0.95), v, seed=SEED + 100 + i, pick_pos=0.18, t60=4.5,
                         B=4e-5, max_f=4500.0, release=0.4)
        mx.add("string", fft_convolve(x, body)[: len(x) + 4000], t + float(g.normal(0, 0.012)), pan=-0.08)


def add_rain(mx: LoopMixer, L: int) -> None:
    g = rng(SEED + 3)
    ease = 0.85 + 0.15 * plfo(L, 0.05, g)                  # the rain breathes, never stops
    mx.add("hiss", stereo_noise(L, g, [bq_highpass(1500, 0.7), bq_peak(5000, 3.0, 0.7), bq_lowpass(10000, 0.7)],
                                0.3) * ease[:, None], 0.0)
    run = circ_noise(L, g, [bq_bandpass(700, 0.9), bq_lowpass(1500, 0.7)]) * (0.7 + 0.3 * plfo(L, 0.2, g))
    mx.add("runoff", run * ease, 0.0, pan=0.35)
    # drops: on water (small bubbles) and on stone (short ticks), scattered through the loop (they wrap)
    tt = float(g.uniform(0, 0.1))
    while tt < LOOP_S:
        if g.random() < 0.65:
            x = drip(vel=float(g.uniform(0.15, 0.45)), radius_mm=float(g.uniform(1.0, 2.2)),
                     seed=int(g.integers(1 << 30)))
            mx.add("drops", x, tt, pan=float(g.uniform(-0.9, 0.9)))
        else:
            k = int(g.uniform(0.002, 0.005) * SR)
            tick = filt(g.standard_normal(k + 64), [bq_bandpass(float(g.uniform(2500, 6000)), 1.4)])[:k]
            tick *= np.exp(-np.arange(k) / (0.25 * k)) * float(g.uniform(0.1, 0.4))
            mx.add("drops", tick, tt, pan=float(g.uniform(-0.9, 0.9)))
        tt += float(g.exponential(1.0 / 9.0))


def thunder(g) -> np.ndarray:
    """A far roll of thunder down the coast: a low noise band that rolls in over ~1.5 s and dies over ~6 s. Mono."""
    N = int(9.0 * SR)
    t = np.arange(N) / SR
    x = filt(g.standard_normal(N), [bq_lowpass(160, 0.7), bq_highpass(30, 0.7), bq_peak(70, 4.0, 0.8)])
    x /= np.std(x) + 1e-9
    env = (1 - np.exp(-t / 0.8)) * np.exp(-t / 2.4) * (1.0 + 0.4 * np.sin(2 * np.pi * 0.7 * t) ** 2)
    return x * env


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"]), for these levels relative to the string
# (0 LU): the rain's hiss -8, the runoff -8, the drops -12, the thunder -13 (over the whole loop). The string is sparse,
# so its notes stand well over this. M3-AUD-864: the hiss was -1 and the runoff -6: the Act I listening report found
# the cue the harshest and most static of the score (presence 14 dB over the set's median, 74% of its 3 s windows
# near-copies), the rain's broadband hiss and the drops' stone ticks (2.5-6 kHz, about nine a second) filling the band over the string. The rain now sits under the counting.
GAINS = {"string": 0.0, "hiss": -40.7, "runoff": -31.5, "drops": -0.7, "thunder": -29.3}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    mx.bus("string", GAINS["string"], send=0.32, process=lambda x: filt(x, [bq_highpass(80, 0.7)]))
    mx.bus("hiss", GAINS["hiss"], send=0.1)
    mx.bus("runoff", GAINS["runoff"], send=0.15)
    mx.bus("drops", GAINS["drops"], send=0.25, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("thunder", GAINS["thunder"], send=0.3)
    add_string(mx)
    add_rain(mx, mx.L)
    mx.add("thunder", thunder(rng(SEED + 4)), THUNDER_AT, pan=-0.3)
    wall = ModFDNReverb(rt60=2.4, rt60_high=0.8, predelay=0.03, size=1.3, mod_depth=7.0, mod_rate=0.4,
                        early_level=0.25, lowcut=90.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=wall, reverb_return_db=-3.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=2.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_pulses": PULSES, "downbeat_offset_s": LEAD_IN, "meter": "free (bpm counts pulses)"})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"corrow_aftermath: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        lead = mx.bus_lufs["string"]
        print("  buses (LU vs the string)", {k: round(v - lead, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
