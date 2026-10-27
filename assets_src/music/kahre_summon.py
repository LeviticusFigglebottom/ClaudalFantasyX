"""`kahre_summon`: the sting when Asha calls Kahre, the Lightning Vowbound (M3-AUD-821; act1_ch05.md §6), ~5.5 s.

Original (SPEC §2). The brief: "Sting (<= 6 s). Struck anvil, a white crack, the Hush's second phrase on low brass."
Kahre is the smith Daro Pemakan, the thirty-sixth Cantor, bound in Ashcrown's anvil court; Pemakar calls the plume's
thunder "Daro's hammer". The material is our own Hush theme's second phrase (hush_theme_v2.py MEL_B: A G F | G D),
not taken from any existing tune; ilun_summon.py states the first phrase the same way, on glass, very high.

* 0.10 s: a hammer on an anvil: a steel block's inharmonic modes (bright, long-ringing high partials over a short,
  heavy body thump), struck once hard;
* 0.32 s: the white crack: a lightning stroke close by, a broadband snap with a few sizzling after-crackles and a
  short low roll under it (no long thunder: the sting has to clear the battle quickly);
* 0.55 s: the Hush's second phrase, its first five notes, on low brass two octaves down (A3 G3 F3 | G3 D3): two
  tenor horns in unison with a bass an octave under, each a lip-buzzed additive tone that brightens as it gets
  louder; the last D held, under the anvil's ring, and released.

Stereo, on the Music bus over the ducked battle cue (sfx.json `kahre_summon`; battle_sfx.json vowbound_stings), like
ilun_summon.

Render:  python3 assets_src/music/kahre_summon.py   (or tools/audio/render_all.py --only kahre_summon)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, midi_to_hz,  # noqa: E402
                       rng, smooth_noise)
from synth.loudness import momentary_max_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "sfx", "kahre_summon.ogg")
SEED = 20261822
TARGET_LUFS = -16.0
LENGTH = 5.5
ANVIL_AT = 0.10
CRACK_AT = 0.32
BRASS_AT = 0.55
BEAT = 0.30                     # the phrase's beat: quick, but every note speaks
## MEL_B's first five notes (hush_theme_v2.py), two octaves down, in beats; the last D held
PHRASE = [("A3", 2.0), ("G3", 0.5), ("F3", 0.5), ("G3", 2.0), ("D3", 7.0)]
## a brass note speaks after its lip buzz builds: placed this much early
BRASS_PRE = 0.03


def anvil(g, vel: float) -> np.ndarray:
    """A hammer on a steel anvil: inharmonic plate-and-block modes (the high ones ring for seconds), a short heavy
    thump of the block, and the hammer's click. Mono."""
    sec = 4.5
    N = int(sec * SR)
    t = np.arange(N) / SR
    out = np.zeros(N)
    base = 1180.0 * float(g.uniform(0.98, 1.02))
    for r, a, t60 in ((1.0, 1.0, 3.2), (1.47, 0.55, 2.6), (2.31, 0.7, 2.9), (2.98, 0.35, 1.9), (3.86, 0.42, 2.2),
                      (4.73, 0.22, 1.5), (5.91, 0.18, 1.2), (7.32, 0.10, 0.8)):
        f = base * r
        beat = 1 + 0.5 * np.cos(2 * np.pi * float(g.uniform(0.4, 1.6)) * t)      # a slow beating pair
        out += a * np.exp(-6.91 * t / t60) * (np.sin(2 * np.pi * f * t + g.uniform(0, 6.28))
                                              + 0.3 * beat * np.sin(2 * np.pi * f * 1.0013 * t))
    body = np.sin(2 * np.pi * 210.0 * t) * np.exp(-t / 0.05) * 1.2
    nn = int(0.004 * SR)
    click = np.zeros(N)
    click[:nn] = filt(g.standard_normal(nn), [bq_highpass(2500, 0.7)]) * np.linspace(1, 0, nn)
    y = 0.35 * out + body + 1.5 * click
    return vel * y * np.clip(t / 0.0004, 0, 1)


def white_crack(g, vel: float) -> np.ndarray:
    """A lightning stroke near by: a broadband snap (a few milliseconds), sizzling after-crackles over 0.3 s, and a
    short low roll. Mono."""
    sec = 2.2
    N = int(sec * SR)
    t = np.arange(N) / SR
    snap_n = int(0.012 * SR)
    snap = np.zeros(N)
    snap[:snap_n] = g.standard_normal(snap_n) * np.exp(-np.arange(snap_n) / (0.003 * SR))
    snap = filt(snap, [bq_highpass(300, 0.7), bq_peak(3500, 4.0, 0.8)])
    sizzle = np.zeros(N)
    for _ in range(26):
        at = 0.32 * float(g.uniform(0.01, 1.0)) ** 1.4      # most of them early
        k = int(float(g.uniform(0.001, 0.004)) * SR)
        s = int(at * SR)
        if s + k < N:
            amp = float(g.uniform(0.2, 0.8)) * np.exp(-at / 0.15)
            sizzle[s: s + k] += g.standard_normal(k) * np.linspace(1, 0, k) * amp
    sizzle = filt(sizzle, [bq_highpass(1800, 0.7)])
    roll = filt(g.standard_normal(N), [bq_lowpass(260, 0.7), bq_highpass(30, 0.7)]) * np.exp(-t / 0.45)
    roll *= np.clip(t / 0.03, 0, 1) * (0.7 + 0.3 * smooth_noise(N, 9.0, g))
    return vel * (2.2 * snap + 0.9 * sizzle + 0.8 * roll)


def low_brass(m: float, dur: float, vel: float, seed: int, attack: float = 0.05, release: float = 0.22) -> np.ndarray:
    """A lip-buzzed low brass tone: additive harmonics whose upper partials rise faster than the fundamental as the
    pressure rises (the brass 'brassiness'), a formant near 550 Hz and 1.2 kHz, a scoop up into the note from the
    lips settling, a little buzz noise at the attack. Mono."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int((dur + 5 * release + 0.04) * SR)
    t = np.arange(N) / SR
    P = np.clip(t / attack, 0, 1) ** 1.2 * np.where(t > dur, np.exp(-(t - dur) / release), 1.0)
    P *= (1.0 + 0.22 * np.exp(-t / 0.06)) * (1.0 + 0.03 * smooth_noise(N, 3.0, g))     # the attack's blat
    cents = -35.0 * np.exp(-t / 0.035) + 3.0 * smooth_noise(N, 1.2, g)
    ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200.0)) / SR
    K = int(max(1, min(40, 6500.0 / f0)))
    y = np.zeros(N)
    for k in range(1, K + 1):
        fk = k * f0
        form = 1.0 + 1.4 * np.exp(-((fk - 550.0) / 260.0) ** 2) + 0.8 * np.exp(-((fk - 1200.0) / 420.0) ** 2)
        a = form / k ** 0.6 / (1.0 + (fk / 3500.0) ** 3)
        y += a * (P * vel) ** (1.0 + 0.28 * (k - 1)) * np.sin(k * ph + 0.3 * k)
    buzz = filt(g.standard_normal(N), [bq_bandpass(900.0, 0.8)]) * P * np.exp(-t / 0.08) * 0.05
    out = y + buzz
    k2 = int(0.006 * SR)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.1 * out


# Bus gains from measured momentary loudness at each hit (render(stats=...)): the brass at L over its phrase, the
# anvil at L+1 at its strike (it opens the sting), the crack at L-1 at its snap.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = Mixer(LENGTH + 3.0)
    mx.bus("anvil", -3.0, send=0.45, process=lambda x: filt(x, [bq_highpass(150, 0.7)]))
    mx.bus("crack", -1.7, send=0.30, process=lambda x: filt(x, [bq_highpass(25, 0.7)]))
    mx.bus("brass", 0.0, send=0.35, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(6000, 0.7)]))
    mx.add("anvil", anvil(g, 0.9), ANVIL_AT, pan=-0.15)
    mx.add("crack", white_crack(g, 1.0), CRACK_AT, pan=0.2)
    pos = BRASS_AT
    for i, (p, beats) in enumerate(PHRASE):
        d = beats * BEAT
        last = i == len(PHRASE) - 1
        v = (0.82 if beats >= 2 else 0.72) * (0.92 if last else 1.0) * g.uniform(0.97, 1.02)
        for j, (dm, pan, lvl) in enumerate(((0.0, -0.18, 1.0), (0.06, 0.18, 0.9), (-12.0, 0.0, 0.8))):
            x = low_brass(n(p) + dm, d * (0.97 if not last else 1.0), v * lvl, SEED + 10 * i + j,
                          release=0.5 if last else 0.12)
            mx.add("brass", x, pos - BRASS_PRE + 0.008 * j + float(g.normal(0, 0.004)), pan=pan)
        pos += d
    hall = ModFDNReverb(rt60=2.4, rt60_high=1.2, predelay=0.02, size=1.0, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.25, seed=SEED % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-3.0)[: int((LENGTH + 0.5) * SR)]
    k = int(1.0 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    if stats is not None:
        stats["bus_mmax"] = {}
        for b in mx.buses.values():
            x = b.process(b.buf) if b.process else b.buf
            stats["bus_mmax"][b.name] = momentary_max_lufs(db_to_lin(b.gain_db) * x)
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, y, quality=4.0)
    m = measure(y)
    if verbose:
        print(f"kahre_summon: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  Mmax {m['momentary_max_lufs']:.2f}"
              f"  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    st: dict = {}
    render(stats=st)
    print("  buses (momentary max)", {k: round(v, 1) for k, v in st["bus_mmax"].items()})
