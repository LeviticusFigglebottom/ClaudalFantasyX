"""The Ashcrown strike trial's sounds (M3-AUD-825; act1_ch05.md B08; M3-C05-04 "a run along the veins, the landing").

The trial (game/levels/ch05/ashcrown/ashcrown_trial.gd): catch a strike at the crown in a tier's copper rod, walk
the charge down the copper veins tier by tier before it fades, turning vein-gates to trace its path. AshcrownAudio
(game/audio/ashcrown_audio.gd) plays these on the trial's signals, at the bowl or the gate when the zone has it.
All synthesized here and in tools/audio/synth/ (SPEC §2, §9: no samples, no recordings, no generated audio), on the
copper and ash palette of ashcrown.py (struck copper modes, crackle, a dry stone court). Mono, 44.1 kHz, Ogg Vorbis
q4, under assets/audio/sfx/ashcrown/, on World. Each at -18 LUFS momentary max (the trial's world SFX, like the
shrine's), the stud tick quieter (-24: it repeats every few metres).

    ash_catch           the rod takes the strike: a white crack, then the bowl's copper humming with the charge
    ash_stud_1..2       one stud of the ring going dark: a small copper tick and a fizz
    ash_fade            the charge fading out of the bowl: the hum sinking and a last sputter
    ash_vein_run        the strike running the traced veins: a crackling sweep that travels and arrives
    ash_vein_ground     lost into the ground: the run cut off in a thud and a hiss
    ash_vein_seal       stopped at the quench seal: a hard crack against stone, and a ring
    ash_landed          the strike lands in the anvil court: a deep boom and the anvil-stone ringing
    ash_gate_1..2       a vein-gate turned a quarter: a ratchet clunk of copper on stone
    ash_plate           a floor plate settling under a step: a stone shift
    ash_alcove          the sealed alcove grinding open

Render:  python3 assets_src/sfx/ashcrown_sfx.py   (or tools/audio/render_all.py --only ashcrown_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from field_ambience import modal, stick_slip  # noqa: E402
from field_sfx import _env, _noise, _place, _room, _tail_fade  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "ashcrown")
SEED = 82500
CEILING = -2.0
TARGET = -18.0
STUD_TARGET = -24.0


def _g(name: str) -> np.random.Generator:
    return rng(SEED + sum((i + 1) * ord(c) for i, c in enumerate(name)) % 9973)


def _crackle(g, sec: float, rate: float, lo: float = 1800.0) -> np.ndarray:
    buf = np.zeros(int(sec * SR))
    for _ in range(int(sec * rate)):
        k = int(float(g.uniform(0.001, 0.004)) * SR)
        _place(buf, g.standard_normal(k) * np.linspace(1, 0, k) * float(g.uniform(0.3, 1.0)), float(g.uniform(0, sec)))
    return filt(buf, [bq_highpass(lo, 0.7)])


def _copper(g, f0: float, sec: float, ring: float) -> np.ndarray:
    return modal([f0, f0 * 2.76, f0 * 5.4, f0 * 8.9], [ring, ring * 0.6, ring * 0.3, ring * 0.15], [1.0, 0.5, 0.25, 0.1],
                 sec, g, click=0.4)


def _hum(sec: float, f: float, attack: float, release: float) -> np.ndarray:
    n = int(sec * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)
    return y * np.clip(t / attack, 0, 1) * np.clip((sec - t) / release, 0, 1) * (1 + 0.2 * np.sin(2 * np.pi * 9 * t))


def ash_catch(g):
    buf = np.zeros(int(2.2 * SR))
    n = int(0.06 * SR)
    _place(buf, filt(g.standard_normal(n), [bq_bandpass(3200, 0.7)]) * _env(n, 0.0003, 0.015) * 1.2, 0.0)
    _place(buf, _crackle(g, 0.5, 120) * 0.6, 0.0)
    _place(buf, _hum(2.0, 110.0, 0.15, 0.4) * 0.35, 0.05)
    _place(buf, _copper(g, 620.0, 1.6, 0.6) * 0.3, 0.02)
    return buf


def ash_stud(g):
    buf = np.zeros(int(0.5 * SR))
    _place(buf, _copper(g, float(g.uniform(1500, 1900)), 0.3, 0.06) * 0.6, 0.0)
    _place(buf, _noise(g, 0.15, [bq_bandpass(4500, 1.0)], 0.002, 0.05) * 0.2, 0.01)
    return buf


def ash_fade(g):
    sec = 1.6
    n = int(sec * SR)
    t = np.arange(n) / SR
    f = 110.0 * (1 - 0.35 * t / sec)
    hum = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.5)
    buf = hum * 0.6 + _crackle(g, sec, 25) * np.exp(-t / 0.4)
    _place(buf, _noise(g, 0.2, [bq_bandpass(2500, 0.8)], 0.005, 0.07) * 0.4, 1.0)
    return buf


def ash_vein_run(g):
    sec = 1.4
    n = int(sec * SR)
    t = np.arange(n) / SR
    sweep = np.zeros(n)
    for k in range(0, n, 256):
        fc = 900 + 3200 * (k / n)
        seg = filt(g.standard_normal(min(1024, n - k)), [bq_bandpass(fc, 1.2)])
        sweep[k: k + 256] += seg[: min(256, n - k)]
    sweep *= np.clip(t / 0.05, 0, 1) * np.clip((sec - t) / 0.25, 0, 1)
    buf = sweep * 0.5 + _crackle(g, sec, 160) * 0.7
    _place(buf, _copper(g, 520.0, 0.8, 0.3) * 0.5, sec - 0.35)  # it arrives at the next bowl
    return buf


def ash_vein_ground(g):
    buf = ash_vein_run(g)[: int(0.7 * SR)]
    buf = np.concatenate([buf, np.zeros(int(1.0 * SR))])
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * 55 * t) * np.exp(-t / 0.15) + 0.5 * filt(g.standard_normal(n), [bq_lowpass(300, 0.7)]) \
        * np.exp(-t / 0.1)
    _place(buf, thud, 0.68)
    _place(buf, _noise(g, 0.8, [bq_bandpass(3000, 0.8)], 0.01, 0.3) * 0.25, 0.7)
    return buf


def ash_vein_seal(g):
    buf = ash_vein_run(g)[: int(0.7 * SR)]
    buf = np.concatenate([buf, np.zeros(int(1.4 * SR))])
    n = int(0.05 * SR)
    _place(buf, filt(g.standard_normal(n), [bq_bandpass(2200, 0.7)]) * _env(n, 0.0003, 0.012) * 1.3, 0.68)
    _place(buf, _copper(g, 340.0, 1.3, 0.5) * 0.6, 0.69)
    return buf


def ash_landed(g):
    buf = np.zeros(int(3.5 * SR))
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (40 + 30 * np.exp(-t / 0.1)) * t) * np.exp(-t / 0.4)
    _place(buf, boom, 0.0)
    _place(buf, _crackle(g, 0.6, 200, 1200) * 0.8, 0.0)
    _place(buf, _copper(g, 196.0, 3.0, 1.2) * 0.5, 0.02)  # the anvil-stone ringing
    return _room(buf, 1.6, 0.25, int(g.integers(1 << 30)))


def ash_gate(g):
    buf = np.zeros(int(0.8 * SR))
    for k in range(3):  # the ratchet's teeth
        _place(buf, _copper(g, float(g.uniform(900, 1200)), 0.08, 0.02) * 0.4, 0.03 * k)
    _place(buf, stick_slip(g, 0.2, 150, 450, [(400.0, 1.0), (1000.0, 0.5)]) * 0.4, 0.05)
    _place(buf, _copper(g, 280.0, 0.5, 0.12), 0.25)
    return buf


def ash_plate(g):
    buf = np.zeros(int(0.8 * SR))
    _place(buf, stick_slip(g, 0.25, 40, 120, [(180.0, 1.0), (420.0, 0.5)]) * 0.6, 0.0)
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    _place(buf, (np.sin(2 * np.pi * 90 * t) * np.exp(-t / 0.06)) * 0.7, 0.24)
    return buf


def ash_alcove(g):
    buf = np.zeros(int(3.0 * SR))
    _place(buf, stick_slip(g, 2.2, 20, 70, [(120.0, 1.0), (300.0, 0.6), (700.0, 0.25)]), 0.0)
    _place(buf, filt(g.standard_normal(int(2.2 * SR)), [bq_lowpass(400, 0.7)]) * 0.2, 0.0)
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    _place(buf, np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.12), 2.2)
    return buf


CUES = [
    ("ash_catch", ash_catch, TARGET), ("ash_stud_1", ash_stud, STUD_TARGET), ("ash_stud_2", ash_stud, STUD_TARGET),
    ("ash_fade", ash_fade, TARGET), ("ash_vein_run", ash_vein_run, TARGET), ("ash_vein_ground", ash_vein_ground, TARGET),
    ("ash_vein_seal", ash_vein_seal, TARGET), ("ash_landed", ash_landed, TARGET), ("ash_gate_1", ash_gate, TARGET),
    ("ash_gate_2", ash_gate, TARGET), ("ash_plate", ash_plate, TARGET), ("ash_alcove", ash_alcove, TARGET),
]
FILES = [f"{name}.ogg" for name, _, _ in CUES]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, fn, target in CUES:
        x = normalize_momentary(_tail_fade(np.asarray(fn(_g(name)), dtype=np.float64), 0.05), target, ceiling_db=CEILING)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.2f}s  momentary max {m['momentary_max_lufs']:.2f} LUFS  "
                  f"peak {m['sample_peak_dbfs']:.2f} dBFS")
    return res


if __name__ == "__main__":
    render()
