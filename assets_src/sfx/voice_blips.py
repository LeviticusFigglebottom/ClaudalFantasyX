"""Per-speaker dialogue voice blips (M3-AUD-07; docs/kb/tech/audio_runtime.md "Voices").

Each blip is one murmured syllable, not a beep: a band-limited voiced pulse (a sawtooth with a small pitch fall,
a little pitch drift and aspiration noise) through three formant band-passes, with a quick attack and a short
decay. A timbre is a voice: its fundamental, its vocal-tract scale (formants rise for a shorter tract), its
spectral tilt and its breathiness. Each timbre has three vowel variants (the game picks one per blip, never the
same twice running) so a run of blips sounds like speech rhythm rather than a repeated click.

Timbres (game/data/audio/voices.json maps every speaker to one, with its own pitch and rate):
    soft     ~220 Hz, "oh/ah/uh", warm tilt          (Rhen, Ysolde)
    bright   ~320 Hz, "eh/ah/ih", clear upper formant (Asha, Liss, the vendor, Reed)
    low      ~145 Hz, "oh/uh/ah", dark, longer        (Toma, Kerrid, Pell, the fisher)
    breathy  ~250 Hz, mostly air over a weak voice    (Sefir, the netmender, Neme)
    child    ~400 Hz, "ah/eh/ih", small tract         (the child)

Outputs (mono, 44.1 kHz, Ogg Vorbis q4): assets/audio/sfx/voice/blip_<timbre>_<1..3>.ogg, 55-75 ms each.
Loudness (docs/kb/audio/mix.md, tools/audio/targets.py): -27 LUFS momentary max, sample peaks <= -3 dBFS, the same
as the shared text_blip. No room: the Voice bus is dry, and a blip is too short to carry one.

Render:  python3 assets_src/sfx/voice_blips.py   (or tools/audio/render_all.py --only voice_blips)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, polyblep_saw, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "voice")
SEED = 7307
TARGET = -27.0
CEILING = -3.0

# F1, F2, F3 (Hz) of an adult tract; a timbre's `scale` multiplies them
VOWELS = {
    "ah": (700, 1150, 2500),
    "oh": (520, 860, 2450),
    "uh": (600, 1050, 2350),
    "eh": (520, 1750, 2500),
    "ih": (400, 2000, 2650),
}

# f0 Hz, tract scale, tilt (low-pass Hz), aspiration (noise level), duration s, decay s, F3 gain, vowels
TIMBRES = {
    "soft": dict(f0=220.0, scale=1.0, tilt=2100.0, breath=0.06, dur=0.060, decay=0.020, f3=0.14,
                 vowels=("oh", "ah", "uh")),
    "bright": dict(f0=320.0, scale=1.1, tilt=3600.0, breath=0.04, dur=0.055, decay=0.017, f3=0.30,
                   vowels=("eh", "ah", "ih")),
    "low": dict(f0=145.0, scale=0.9, tilt=1700.0, breath=0.05, dur=0.075, decay=0.026, f3=0.10,
                vowels=("oh", "uh", "ah")),
    "breathy": dict(f0=250.0, scale=1.05, tilt=2600.0, breath=0.55, dur=0.065, decay=0.024, f3=0.22,
                    vowels=("ah", "oh", "eh")),
    "child": dict(f0=400.0, scale=1.25, tilt=4200.0, breath=0.05, dur=0.050, decay=0.015, f3=0.26,
                  vowels=("ah", "eh", "ih")),
}
VARIANTS = 3


def _tail_fade(x, sec=0.008):
    k = int(sec * SR)
    x[-k:] *= np.linspace(1, 0, k) ** 2
    return x


def blip(timbre: str, vowel: str, seed: int) -> np.ndarray:
    p = TIMBRES[timbre]
    g = rng(seed)
    dur = p["dur"]
    N = int((dur + 0.012) * SR)
    t = np.arange(N) / SR
    fall = 0.5 + 0.4 * g.random()                     # 0.5..0.9 semitone fall over the syllable
    f0 = p["f0"] * 2 ** (-fall * t / dur / 12)
    f0 = f0 * (1 + 0.004 * g.standard_normal(N).cumsum() / np.sqrt(N))
    voiced = filt(polyblep_saw(f0, SR, 0.0), [bq_lowpass(p["tilt"], 0.6)])
    air = filt(g.standard_normal(N), [bq_highpass(900, 0.7), bq_lowpass(6000, 0.7)])
    src = (1.0 - min(p["breath"], 0.8)) * voiced + p["breath"] * air
    f1, f2, f3 = (f * p["scale"] for f in VOWELS[vowel])
    vox = (1.0 * filt(src, [bq_bandpass(f1, 6.0)]) + 0.55 * filt(src, [bq_bandpass(f2, 7.0)])
           + p["f3"] * filt(src, [bq_bandpass(f3, 8.0)]))
    env = np.clip(t / 0.006, 0, 1) * np.exp(-np.maximum(t - 0.012, 0) / p["decay"])
    y = filt(vox * env, [bq_highpass(max(110.0, 0.7 * p["f0"]), 0.7)])
    return _tail_fade(y)


def files() -> list[str]:
    return [f"blip_{name}_{i + 1}.ogg" for name in TIMBRES for i in range(VARIANTS)]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for ti, (name, p) in enumerate(TIMBRES.items()):
        for i, vowel in enumerate(p["vowels"][:VARIANTS]):
            x = normalize_momentary(blip(name, vowel, SEED + 10 * ti + i), TARGET, ceiling_db=CEILING)
            fname = f"blip_{name}_{i + 1}.ogg"
            write_ogg(os.path.join(out_dir, fname), x, quality=4.0)
            m = measure(x)
            res[fname] = m
            if verbose:
                print(f"{fname}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                      f"peak {m['sample_peak_dbfs']:.2f} dBFS")
    return res


if __name__ == "__main__":
    render()
