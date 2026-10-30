"""`kesh_memory`: Ch16 C4, Kesh's memory, a thousand years back (M4-A2P-090; the cue sheet §3 Ch16; the script
ch16_the_choir.dlg, `@music kesh_memory`): about 90 s, the Drowned Choir heard through water and time.

Original composition for this project (SPEC §2, §9), made only from this project's own lines: the Act II final of
`drowned_choir` (assets_src/music/act2/drowned_choir.py, decoded from its render) and the Hush's first phrase
(hush_theme_v2.py MEL_A), imported, never retyped. Nothing is taken from any existing music.

The brief (the cue sheet's proposal, Ch16 C4): what the Hush really does, shown as a memory. The mix's muffle leaves the
Music bus out on purpose (the score is not in the water, mix.json), so the memory is in the cue itself:
* the Choir's music from its top, low-passed (as if through water), widened, and drifting slowly in pitch (a few cents,
  never in tune with itself for long), its level breathing;
* over it, MEL_A sung once by one far voice on an open "ah", slow, the way the Cantor first sang it;
* it fades in over 2 s and out over the last 6 s, so the scene's `@music` change carries it.

A minor (the Hush's key, the Choir's), free (the cue row's `beat` is "free"). Vorbis q3, -16 LUFS integrated. Plain git
(ADR 0175).

Render:  python3 tools/audio/render_all.py --only kesh_memory
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

from hush_theme_v2 import MEL_A  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng, smooth_noise  # noqa: E402
from synth.mixer import measure, normalize_integrated, read_audio, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import sing  # noqa: E402

CHOIR = os.path.join(ROOT, "assets", "audio", "music", "act2", "drowned_choir.ogg")
OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "kesh_memory.ogg")
SEED = 20262050
TARGET_LUFS = -16.0
LENGTH_S = 92.0
FADE_IN_S, FADE_OUT_S = 2.0, 6.0
DRIFT_CENTS, DRIFT_PERIOD_S = 9.0, 11.0
VOICE_AT_S = 14.0
VOICE_BEAT = 60.0 / 50.0           # MEL_A, slow
VOICE_DB = -9.0


def through_water(x: np.ndarray) -> np.ndarray:
    """Low-passed, widened, and drifting in pitch (a slow time warp: a few cents either way)."""
    y = filt(x, [bq_lowpass(1100, 0.7), bq_lowpass(1700, 0.6), bq_highpass(45, 0.7)])
    t = np.arange(len(y)) / SR
    a = DRIFT_CENTS / 1200 * np.log(2) * DRIFT_PERIOD_S / (2 * np.pi)
    warp = t + a * np.sin(2 * np.pi * t / DRIFT_PERIOD_S)
    y = np.stack([np.interp(warp, t, y[:, c]) for c in range(2)], axis=1)
    mid, side = (y[:, 0] + y[:, 1]) / 2, (y[:, 0] - y[:, 1]) / 2
    side = 1.6 * side + 0.3 * np.roll(mid, int(0.013 * SR))       # widened: more side, a little delayed mid in it
    return np.stack([mid + side, mid - side], axis=1)


def far_voice(g) -> np.ndarray:
    ph, pi = [], []
    for p, beats, _ in MEL_A:
        d = beats * VOICE_BEAT
        ph.append(("a", d))
        pi.append((float(n(p)), d))
    v = sing(ph, pi, vel=0.5, seed=SEED + 1, scale=1.17, vib_cents=12.0, breath=0.1)
    v = filt(v, [bq_highpass(220, 0.7), bq_lowpass(2600, 0.7)])     # far, and under the water too
    return np.stack([v * 0.8, v * 0.6], axis=1)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    N = int(LENGTH_S * SR)
    choir = read_audio(CHOIR, SR, 2)[:N]
    x = through_water(choir)
    x *= (0.8 + 0.2 * smooth_noise(len(x), 0.08, g))[:, None]          # its level breathing
    v = far_voice(g)
    hall = ModFDNReverb(rt60=5.5, rt60_high=1.2, predelay=0.06, size=1.8, mod_depth=12.0, mod_rate=0.2,
                        early_level=0.2, lowcut=120.0, seed=SEED % 9973)
    wet = hall.process(v)
    vv = np.zeros_like(x)
    k0 = int(VOICE_AT_S * SR)
    seg = (0.35 * np.pad(v, ((0, len(wet) - len(v)), (0, 0))) + wet)[: N - k0]
    vv[k0: k0 + len(seg)] = seg
    x = x + 10 ** (VOICE_DB / 20) * vv / (np.abs(vv).max() + 1e-9) * np.abs(x).max()
    t = np.arange(N) / SR
    x *= (np.clip(t / FADE_IN_S, 0, 1) * np.clip((LENGTH_S - t) / FADE_OUT_S, 0, 1) ** 2)[:, None]
    x = normalize_integrated(x, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, x, quality=3.0)
    m = measure(x)
    if verbose:
        print(f"kesh_memory: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
