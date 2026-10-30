"""`virel_bound`: the sting when Asha binds Virel, the Fire Vowbound, in the Coilspire's crown chamber (M3-AUD-822;
act1_ch08.md B06, after `coilspire_flues`), 7.9 s and its drone held on.

Original (SPEC §2). The brief: "The Hush's first phrase on a high reed instrument over the flue drone. It is the first
statement of the theme by a wind instrument." The phrase is our own Hush theme's first six notes (hush_theme_v2.py
MEL_A: E D C | A G A, read from that file, never re-typed), moved into the Coilspire's F-sharp minor (coilspire.py)
and up an octave: C#6 B5 A5 | F#5 E5 F#5. It is played once, slowly, on the spire reed, a new double-reed voice
written for this cue (`spire_reed` below; virel_summon.py plays it too): bright, a little hard, with a delayed narrow
vibrato, and its last note held. Virel is "a kite made of fire, held perfectly still", so nothing under the reed
moves: the flues' drone is F# and C#, the trial's tiers (F#2, C#3, F#3, C#4), each a breathy tuned air column that
breathes slowly, with a thin copper hiss over it. The drone swells in, the reed sings, the last F# is held, and the
drone settles low and holds on under the scene's end (HOLD_S), then lets go. No drums, no crackle (Virel's fire belongs to her battle sting).

Stereo, at the music target (-16 LUFS integrated), on the Music bus (`@music virel_bound`; music.json).

Render:  python3 assets_src/music/virel_bound.py   (or tools/audio/render_all.py --only virel_bound)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng,  # noqa: E402
                       smooth_noise)
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _mod("hush_theme_v2")

OUT = os.path.join(ROOT, "assets", "audio", "music", "virel_bound.ogg")
SEED = 20261822
TARGET_LUFS = -16.0
LENGTH = 7.9
# The flues' drone held after the sting (the Lead's 10-30 19:25 item, Act I's beats as played): ch08_binding runs
# about 4 s past the 7.9 s sting, and the zone's cue returns 3 s after that (act1_playthrough.py), so the drone stays
# on, settled HOLD_DB down (under the loudness gate: the sting's -16 LUFS doesn't move), for HOLD_S, and lets go.
HOLD_S = 10.0
HOLD_DB = -12.0
## MEL_A (A minor) into the Coilspire's F-sharp minor, an octave up: -3 + 12 semitones
VIREL_SHIFT = 9
PHRASE_NOTES = 6              # the Hush's first phrase: MEL_A's first six notes (two bars of 3/4)
BEAT = 0.6                    # one beat of MEL_A here (s): 100 BPM, slow and still
PHRASE_T0 = 1.15              # the reed enters once the drone has swelled in
LAST_HOLD = 1.5               # the last note is held this much longer than written
FLUES = [("F#2", 0.9), ("C#3", 0.75), ("F#3", 0.55), ("C#4", 0.32)]   # the trial's tiers (pitch, level)
## spire_reed's tone speaks after a short tonguing transient: notes are placed this much early
REED_PRE = 0.02


def spire_reed(m: float, dur: float, vel: float, seed: int, attack: float = 0.05, release: float = 0.16,
               scoop_cents: float = 30.0, vib_cents: float = 9.0, vib_rate: float = 5.4) -> np.ndarray:
    """The spire reed: a high double reed (bright, a little hard), additive. A full harmonic spectrum with formants
    near 1.5 and 3.1 kHz, brightness that rises with breath pressure (each harmonic follows the pressure to a higher
    power), a small scoop into each note, a narrow vibrato that starts late, the reed's buzz (noise pulsed in step
    with the tone) and a short tonguing transient. Mono."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int((REED_PRE + dur + 5 * release + 0.03) * SR)
    t = np.arange(N) / SR - REED_PRE
    tt = np.maximum(t, 0.0)
    P = np.clip(tt / attack, 0, 1) ** 1.3 * np.where(t > dur, np.exp(-(t - dur) / release), 1.0)
    P *= (1.0 + 0.03 * smooth_noise(N, 3.0, g)) * vel
    P[t < 0] = 0.0
    vib_on = np.clip((tt - 0.35) / 0.4, 0, 1)
    cents = (-scoop_cents * np.exp(-tt / 0.045) + vib_cents * vib_on * np.sin(2 * np.pi * vib_rate * tt
                                                                             + g.uniform(0, 6.28))
             + 2.5 * smooth_noise(N, 0.7, g))
    ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200.0)) / SR
    K = int(max(1, min(40, 9500.0 / f0)))
    y = np.zeros(N)
    for k in range(1, K + 1):
        fk = k * f0
        a = k ** -0.75 * (1.0 + 1.6 * np.exp(-((fk - 1500.0) / 520.0) ** 2)
                          + 0.9 * np.exp(-((fk - 3100.0) / 800.0) ** 2)) / (1.0 + (fk / 5200.0) ** 4)
        y += a * P ** (1.0 + 0.2 * (k - 1)) * np.sin(k * ph + 0.3 * k)
    pulse = 0.5 + 0.5 * np.sin(ph)
    buzz = filt(g.standard_normal(N), [bq_bandpass(2600.0, 0.8)]) * P * pulse ** 4 * 0.05
    air = filt(g.standard_normal(N), [bq_bandpass(4200.0, 0.7)]) * P * 0.012
    k0 = int(REED_PRE * SR)
    tongue = np.zeros(N)
    nt = int(0.012 * SR)
    tongue[k0: k0 + nt] = filt(g.standard_normal(nt + 64), [bq_bandpass(1800.0, 1.2)])[:nt] \
        * np.exp(-np.arange(nt) / (0.003 * SR)) * 0.1 * vel
    out = y + buzz + air + tongue
    k2 = int(0.006 * SR)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.16 * out


def reed_phrase(t0: float, beat: float, last_hold: float, shift: int = VIREL_SHIFT,
                count: int = PHRASE_NOTES) -> list[tuple[float, float, float, float]]:
    """The Hush's first phrase from hush_theme_v2.MEL_A: [(start_s, dur_s, midi, vel)], legato, the last note held."""
    out = []
    pos = t0
    notes = HUSH.MEL_A[:count]
    for i, (p, beats, v) in enumerate(notes):
        d = beats * beat
        if i == len(notes) - 1:
            d += last_hold
        out.append((pos, d, n(p) + shift, v))
        pos += beats * beat
    return out


def flue(m: float, seconds: float, level: float, g, swell_in: float, let_go: float) -> np.ndarray:
    """One copper flue: a tuned air column (a near-sine with a weak octave, plus noise in a narrow band at the pipe's
    pitch) that breathes slowly. Swells in over `swell_in` s, lets go from `let_go` s. Mono."""
    f = midi_to_hz(m)
    N = int(seconds * SR)
    t = np.arange(N) / SR
    wob = 1.0 + 0.08 * smooth_noise(N, 0.35, g)
    ph = 2 * np.pi * np.cumsum(f * (1.0 + 0.0006 * smooth_noise(N, 0.5, g))) / SR
    tone = np.sin(ph) + 0.18 * np.sin(2 * ph + 0.7) + 0.05 * np.sin(3 * ph + 1.3)
    noise = filt(g.standard_normal(N), [bq_bandpass(f, 18.0), bq_bandpass(f, 12.0)])
    noise /= np.std(noise) + 1e-9
    env = np.clip(t / swell_in, 0, 1) ** 2 * np.where(t > let_go, np.exp(-(t - let_go) / 0.7), 1.0)
    return level * (0.8 * tone + 0.35 * noise) * env * wob


# Bus gains from measured bus loudness (HUSH._bus_stats, gated integrated per bus): the reed is the lead (0 LU), the
# flue drone about -6 LU under it, the copper hiss about -20.
GAINS = {"reed": 0.0, "flues": -17.2, "hiss": -9.2}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = Mixer(LENGTH + HOLD_S + 0.5)
    mx.bus("reed", GAINS["reed"], send=0.38, process=lambda x: filt(x, [bq_highpass(400, 0.7),
                                                                         bq_peak(3000, -2.0, 1.0)]))
    mx.bus("flues", GAINS["flues"], send=0.45, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(2500, 0.7)]))
    mx.bus("hiss", GAINS["hiss"], send=0.3, process=lambda x: filt(x, [bq_highpass(5000, 0.7)]))
    phrase = reed_phrase(PHRASE_T0, BEAT, LAST_HOLD)
    end = phrase[-1][0] + phrase[-1][1]
    for i, (t0, d, m, v) in enumerate(phrase):
        x = spire_reed(m, d + 0.03, 0.55 + 0.6 * v, SEED + 10 + i, scoop_cents=35.0 if i == 0 else 18.0,
                       vib_cents=10.0 if d > 0.8 else 4.0)
        mx.add("reed", x, t0 - REED_PRE + float(g.normal(0, 0.004)), pan=0.05)
    for j, (p, lvl) in enumerate(FLUES):
        x = flue(n(p), LENGTH, lvl, rng(SEED + 100 + j), swell_in=1.0 + 0.2 * j, let_go=end - 0.2 + 0.15 * j)
        mx.add("flues", x, 0.0, pan=(-0.45, 0.4, -0.2, 0.25)[j])
    held = 10 ** (HOLD_DB / 20)
    for j, (p, lvl) in enumerate(FLUES[:2]):                              # F# and C# stay on, low and still
        x = flue(n(p), HOLD_S + 1.5, lvl * held, rng(SEED + 200 + j), swell_in=1.2, let_go=HOLD_S - 1.0)
        mx.add("flues", x, end - 0.6, pan=(-0.45, 0.4)[j])
    hiss = g.standard_normal(int(LENGTH * SR))
    tt = np.arange(len(hiss)) / SR
    hiss *= np.clip(tt / 1.5, 0, 1) * np.where(tt > end, np.exp(-(tt - end) / 0.8), 1.0) * 0.05
    mx.add("hiss", hiss, 0.0, pan=0.0)
    hall = ModFDNReverb(rt60=3.0, rt60_high=1.3, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.28, lowcut=90.0, seed=SEED % 9973)
    st: dict = {}
    HUSH._bus_stats(mx, st)
    y = mx.render(reverb=hall, reverb_return_db=-2.0)[: int((LENGTH + HOLD_S) * SR)]
    k = int(1.4 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, y, quality=4.0)
    m = measure(y)
    if stats is not None:
        stats.update(st)
    if verbose:
        lead = st.get("bus_reed_lufs", 0.0)
        print(f"virel_bound: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  Mmax {m['momentary_max_lufs']:.2f}"
              f"  TP {m['true_peak_dbtp']:.2f}")
        print("  buses (LU vs the reed)", {k[4:-5]: round(v - lead, 1) for k, v in st.items()})
    return m


if __name__ == "__main__":
    render()
