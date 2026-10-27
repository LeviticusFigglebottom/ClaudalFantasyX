"""`hearer_hum`: Ch4 C4-06, "The dock in the dark" (M3-AUD-820; act1_ch04.md §6): a 61 s seamless loop.

Original material for this project (SPEC §2, §9): a sound-picture with no melody at all; the one held tone is a
single pitch, so there is nothing here that could quote or derive from any tune.

The brief: "Near silence: the sea, the far wake behind, and under it, very low, a held tone like 'someone humming in
the next room' (Asha's own words). Audible only in this scene and when Asha speaks of the dead later." Haluna's dock
at 21:50, every lamp up at the wall behind them; Rhen sits at the dock's end, Asha brings two pieces of cake and sits
beside him. She is a hearer: "I can hear them. It's like someone humming in the next room. All the time."

Layers (all synthesized; no samples):
* **the sea under the dock**: low water swelling on an eight-swell cycle, slaps against the pilings at each crest,
  small laps against the planks (field_ambience.py's dock and surf building blocks, nearer and calmer);
* **the far wake**: the village at the wall, a long way behind: voices talking (field_ambience.murmur_phrase, no
  words) and, twice a loop, a far hand drum's two strokes, all dark and far back;
* **the hum**: three low voices humming one D (synth.voice.hum_ensemble, closed mouth), each breathing on its own so
  the tone never stops, heard **through a wall**: everything above about 450 Hz is gone, the room's low resonance
  (about 180 Hz) colours it, and it sits under the water, steady. It is the dead, and it is not a tune. It is a D so
  it sits under Haluna (D major) without belonging to any of its cues.

Mastered to the music target (-16 LUFS) like every music cue: "near silence" is in its character (dark, sparse, no
pulse), not its level; the dialogue duck (-4 dB) applies as for any music.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file; no pulse (the sidecar's bpm is 0). Every swell, noise bed and
LFO is periodic over the loop, the hum's voices wrap at their own phases (hum_ensemble loop mode), and the reverb runs
in steady state, so the wrap is seamless.

Render:  python3 assets_src/music/hearer_hum.py   (or tools/audio/render_all.py --only hearer_hum)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(ROOT, "assets_src", "sfx",
                                                                              "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT = os.path.join(ROOT, "assets", "audio", "music", "hearer_hum.ogg")
SEED = 20261422
TARGET_LUFS = -16.0
LOOP_S = 61.0
HUM_PITCH = "D3"
HUM_VOICES = 3
SWELLS = 8                       # sea swells per loop (about 7.6 s each: a calm night)
# The far wake: (time s, high voice?) murmur phrases, and the far drum's two strokes
MURMURS = [(3.0, False), (5.1, True), (14.5, False), (22.0, True), (24.4, False), (35.5, True), (41.0, False),
           (43.3, True), (52.8, False)]
DRUM_AT = (18.0, 47.5)


def through_wall(x: np.ndarray) -> np.ndarray:
    """Heard through a wood-and-clay wall: the top gone, the room's low resonance left."""
    return filt(x, [bq_highpass(70, 0.7), bq_peak(180, 4.0, 1.4), bq_lowpass(450, 0.6), bq_lowpass(700, 0.7)])


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    L = mx.L
    tt = np.arange(L) / SR
    swell_hz = FA.snap(SWELLS / LOOP_S, L)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * swell_hz * tt)
    mx.add("water", FA.stereo_noise(L, g, [bq_lowpass(520, 0.6), bq_highpass(55, 0.7)], 0.5)
           * (0.45 + 0.55 * swell * (0.85 + 0.15 * FA.plfo(L, 0.06, g)))[:, None], 0.0)
    for k in range(SWELLS):
        crest = (k + 0.25) / swell_hz
        for j in range(int(g.integers(1, 3))):
            mx.add("slaps", FA.slap(g), crest + j * float(g.uniform(0.4, 0.9)) + float(g.uniform(-0.12, 0.12)),
                   pan=float(g.uniform(-0.6, 0.6)), gain=float(g.uniform(0.35, 0.8)))
    for t in FA.schedule(L, 2.3, g, 0.3):
        mx.add("slaps", FA.lap(g, float(g.uniform(0.5, 0.9))), t, pan=float(g.uniform(-0.5, 0.5)),
               gain=float(g.uniform(0.2, 0.5)))
    for t, high in MURMURS:
        mx.add("wake", FA.murmur_phrase(g, high), t, pan=float(g.uniform(-0.35, 0.05)), gain=float(g.uniform(0.6, 1.0)))
    for t in DRUM_AT:
        for k, (stroke, v) in enumerate((("dum", 0.5), ("tek", 0.25))):
            mx.add("wake", frame_drum(stroke, v, variant=int(t) + k, seed=SEED + 9), t + 0.42 * k, pan=-0.2, gain=0.5)
    hum = hum_ensemble([(n(HUM_PITCH), LOOP_S)], voices=HUM_VOICES, seed=SEED + 11, register="low", spread=0.25,
                       scatter_cents=4.0, loop=True)
    mx.add("hum", hum, 0.0)


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the sea's water
# (0 LU): the slaps and laps -4, the hum -6 (under the water, but always there), the far wake -15.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    mx.bus("water", -20.0, send=0.12)
    mx.bus("slaps", 6.6, send=0.18, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
    mx.bus("hum", -0.3, send=0.25, process=through_wall)
    mx.bus("wake", -7.9, send=0.6, process=lambda x: filt(x, [bq_lowpass(1100, 0.7), bq_highpass(120, 0.7)]))
    build(mx)
    night = ModFDNReverb(rt60=1.8, rt60_high=0.7, predelay=0.03, size=1.1, mod_depth=8.0, mod_rate=0.4,
                         early_level=0.15, lowcut=100.0, seed=SEED % 9973)    # open water, the village behind
    _, loop = mx.render(reverb=night, reverb_return_db=-3.0)
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
        print(f"hearer_hum: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
