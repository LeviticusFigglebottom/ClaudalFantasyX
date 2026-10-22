"""UI sound effects (score-as-code for SFX).

They reuse the music palette on purpose, so menus sound like the same world
as the score: the cursor and confirm sounds are tiny metallophone strikes,
cancel is the same bar struck soft and falling, and the dialogue blip is a
short formant-filtered voiced pulse (an "oo/ah" murmur, not a beep).

Outputs (mono, 44.1 kHz, Ogg Vorbis):
    assets/audio/sfx/ui_cursor.ogg   ~0.15 s   cursor move
    assets/audio/sfx/ui_confirm.ogg  ~0.7 s    confirm / accept
    assets/audio/sfx/ui_cancel.ogg   ~0.45 s   cancel / back
    assets/audio/sfx/text_blip.ogg   ~0.06 s   one dialogue voice blip; the game varies
                                               pitch_scale per blip (+/- 6 %) and per speaker
Loudness (see docs/kb/audio/mix.md): UI = -20 LUFS momentary max, blip = -27 LUFS
momentary max, sample peaks <= -3 dBFS.

Render:  python3 assets_src/sfx/ui_sfx.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz,  # noqa: E402
                       polyblep_saw, rng)
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from synth.reverb import FDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
SEED = 4242
UI_TARGET = -20.0
BLIP_TARGET = -27.0


def _place(buf, x, t):
    s = int(t * SR)
    e = min(len(buf), s + len(x))
    buf[s:e] += x[: e - s]


def _room(x, rt60=0.5, mix=0.18, seed=1):
    wet = FDNReverb(rt60=rt60, predelay=0.006, damping=0.35, size=0.45, early_level=0.2,
                    lowcut=400, highcut=9000, seed=seed).process(np.stack([x, x], 1), tail=0.0)
    return (1 - mix) * x + mix * wet.mean(axis=1)[: len(x)]


def _tail_fade(x, sec=0.02):
    k = int(sec * SR)
    x[-k:] *= np.linspace(1, 0, k) ** 2
    return x


def ui_cursor():
    g = rng(SEED + 1)
    N = int(0.15 * SR)
    buf = np.zeros(N)
    _place(buf, metallophone_note(n("E7"), 0.6, seed=SEED + 11, decay=0.22, hardness=0.6, pair=False), 0.0)
    t = np.arange(int(0.012 * SR)) / SR
    tick = np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.0025)
    buf[: len(tick)] += 0.05 * tick
    buf += 0.004 * filt(g.standard_normal(N), [bq_highpass(5000, 0.7)]) * np.exp(-np.arange(N) / SR / 0.003)
    buf = filt(buf, [bq_highpass(700, 0.7)])
    return _tail_fade(buf)


def ui_confirm():
    N = int(0.75 * SR)
    buf = np.zeros(N)
    _place(buf, metallophone_note(n("E6"), 0.55, seed=SEED + 21, decay=0.75, hardness=0.6, ombak_hz=7.0), 0.0)
    _place(buf, metallophone_note(n("B6"), 0.65, seed=SEED + 22, decay=0.65, hardness=0.6, ombak_hz=7.0), 0.065)
    # a soft high partial "glint" an octave above the second note
    t = np.arange(int(0.4 * SR)) / SR
    glint = np.sin(2 * np.pi * midi_to_hz(n("B7")) * t) * np.exp(-t / 0.07) * (1 - np.exp(-t / 0.004))
    _place(buf, 0.015 * glint, 0.07)
    buf = filt(buf, [bq_highpass(350, 0.7), bq_peak(5500, -3, 1.0)])
    return _tail_fade(_room(buf, 0.55, 0.2, SEED + 23), 0.08)


def ui_cancel():
    N = int(0.45 * SR)
    buf = np.zeros(N)
    _place(buf, metallophone_note(n("B5"), 0.5, seed=SEED + 31, decay=0.40, hardness=0.25, ombak_hz=4.0), 0.0)
    _place(buf, metallophone_note(n("F#5"), 0.42, seed=SEED + 32, decay=0.40, hardness=0.2, ombak_hz=4.0), 0.07)
    buf = filt(buf, [bq_highpass(250, 0.7), bq_lowpass(3800, 0.7)])
    return _tail_fade(_room(buf, 0.4, 0.15, SEED + 33), 0.06)


def text_blip():
    g = rng(SEED + 41)
    dur = 0.055
    N = int((dur + 0.01) * SR)
    t = np.arange(N) / SR
    f0 = 300.0 * 2 ** (-0.6 * t / dur / 12)          # small fall, like a murmured syllable
    f0 = f0 * (1 + 0.004 * g.standard_normal(N).cumsum() / np.sqrt(N))
    src = polyblep_saw(f0, SR, 0.0) + 0.05 * g.standard_normal(N)
    src = filt(src, [bq_lowpass(2500, 0.6)])          # glottal-ish spectral tilt
    # formants roughly between "ah" and "oh"
    vox = (1.0 * filt(src, [bq_bandpass(640, 6.0)]) + 0.55 * filt(src, [bq_bandpass(1050, 7.0)])
           + 0.18 * filt(src, [bq_bandpass(2500, 8.0)]))
    env = np.clip(t / 0.006, 0, 1) * np.exp(-np.maximum(t - 0.012, 0) / 0.018)
    y = filt(vox * env, [bq_highpass(180, 0.7)])
    return _tail_fade(y, 0.008)


SFX = {
    "ui_cursor": (ui_cursor, UI_TARGET),
    "ui_confirm": (ui_confirm, UI_TARGET),
    "ui_cancel": (ui_cancel, UI_TARGET),
    "text_blip": (text_blip, BLIP_TARGET),
}


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    res = {}
    for name, (fn, target) in SFX.items():
        x = normalize_momentary(fn(), target, ceiling_db=-3.0)
        path = os.path.join(out_dir, name + ".ogg")
        write_ogg(path, x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.3f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS")
    return res


if __name__ == "__main__":
    render()
