"""`dace_ledger`: Ch17, Rhen reads Dace's logs in the dry-dock (M3-AUD-852; act3_plan.md §2, act_outline Ch17):
about 90 s, through-composed, not looped.

Original composition for this project (SPEC §2): the two tunes in it are the game's own and are imported, never
retyped: Dace's current-song (motifs.py CURRENT_SONG), in pieces, and, in the second half, Ysolde's zither line
(ysolde_theme.py LINE, bars 1-7, her own zither voice) as she begins reconstructing the Eighth Verse. The bed (a
low D pedal under D-C-D-C-F, and a leadsman's two plucked "soundings" marking the entries) was written for this cue
and shares no phrase with any melody we know. The style evoked is a slow bed for reading; nothing is quoted.

The brief: the ledger is read on screen, never in Dace's voice (N-26). Rhen finds his own name in every entry, the
Corrow stair, the comb carried to Haluna, and why Dace never came home. The last entry, written the night Dace
went into the storm after Imra, breaks off: "Let him be one. After the storm", and the next page is blank. So the
current-song never gets home: every fragment stops short, and the last one, "sound again, and home to D", breaks
off on its C a step from the D, and everything stops with it. What is left is the room, and then silence.

This is a **bed for reading**, so the 300 Hz-3 kHz band is left light (iskarra_vigil's method): everything lives
below or above it, and a wide cut centred on 1 kHz on the master takes out what leaks.
* **below** (under about 300 Hz): a bowed D1-A1 pedal that breathes, low strings on the chords (D2-A2, C2-G2, ...),
  plucked low Ds (the soundings: a leadsman's call, struck twice), and the current-song on a solo low string **an
  octave under** its written pitch (D3-C4), slowed to a reading pace, filtered dark;
* **above** (over about 3 kHz): only Ysolde, from 46 s: her zither line three octaves up (G7-G8), exact and dry, a
  cold light in the dark. Her C major and Dace's D dorian are the same seven notes, so her line sits on his bed
  without a single clash: she is reconstructing from what he left.

Timeline (s): 0-8 the pedal and the bed (D) breathe in; 2 the first soundings | 8 "sound, sound" | 13-20 "the set
rising" | 24 the bed to C; 26-31 "over the shoal", stopping on F | 33 the soundings | 36 D again; 37-41 the
soundings and the set, stopping on A | 46 the bed to C; Ysolde's line (her bars 1-4) above | 53-57 "and along", E F
G | 58 the last soundings | 62 the bed to F; Ysolde's bars 5-7, left unfinished | 75 "sound again, and home to D":
A A F E C, and at 80.3 it breaks off on the C; every layer stops with it | 80-90 the room's tail, then silence.

Render:  python3 assets_src/music/act3/dace_ledger.py   (or tools/audio/render_all.py --act3 --only act3/dace_ledger)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import CURRENT_SONG, CURRENT_SONG_BPM  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act3_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


YS = _mod("ysolde_theme")    # her line, her tempo and her zither
V = _mod("act2_voices")      # body_ir

OUT = os.path.join(ROOT, "assets", "audio", "music", "act3", "dace_ledger.ogg")
SEED = 20261753
TARGET_LUFS = -16.0
LENGTH_S = 90.0
VOICE_BAND = (300.0, 3000.0)
BAND_CUT = (1000.0, -9.0, 0.45)    # master: centre Hz, gain dB, Q
LOW_LP = 320.0                     # every low layer stays under this
HIGH_HP = 2800.0                   # Ysolde stays over this
SLOW = 1.65                        # the current-song at a reading pace: this many times its own beat
CB = SLOW * 60.0 / CURRENT_SONG_BPM
SONG_SHIFT = -12                   # an octave under the written pitch
YS_SHIFT = 36                      # Ysolde three octaves up
T_BREAK = 80.3                     # "After the storm": everything stops here

## the current-song in pieces: (start s, phrase, first note, last note + 1, last-note lean)
FRAGMENTS = [
    (8.0, 0, 0, 2, 1.3),           # sound, sound
    (13.0, 0, 2, 7, 1.4),          # the set rising
    (26.0, 1, 0, 4, 1.6),          # over the shoal ... stops on F
    (37.0, 0, 0, 3, 1.5),          # the soundings and the set, stopping on A
    (53.0, 1, 4, 7, 1.4),          # and along: E F G
]
LAST = (75.0, 2, 0, 5)             # sound again, and home to ... C, broken off (the D never comes)
## the bed: (start s, end s, notes); each overlaps the next by a second
BED = [(0.0, 25.0, "D2 A2"), (24.0, 37.0, "C2 G2"), (36.0, 47.0, "D2 A2 F3"), (46.0, 63.0, "C2 G2 E3"),
       (62.0, T_BREAK, "F2 C3")]
SOUNDINGS = [2.0, 33.0, 58.0]      # a leadsman's call: a low D plucked twice
## Ysolde: (start s, her first bar, her last bar)
YSOLDE = [(46.0, 1, 4), (62.5, 5, 7)]


def low_band(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(32, 0.7), bq_lowpass(LOW_LP, 0.6), bq_lowpass(LOW_LP * 1.3, 0.7)])


def high_band(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(HIGH_HP, 0.6), bq_highpass(HIGH_HP * 0.9, 0.7), bq_lowpass(9000, 0.7)])


def stop_env(N: int, fade_in: float, sr: int = SR) -> np.ndarray:
    """In over `fade_in` s; out over 0.4 s at T_BREAK (it breaks off, it does not fade)."""
    t = np.arange(N) / sr
    return np.clip(t / fade_in, 0, 1) ** 2 * np.clip((T_BREAK - t) / 0.4, 0, 1) ** 2


def pedal(g, sr: int = SR) -> np.ndarray:
    """A bowed D1-A1 pedal: detuned partial pairs breathing on an 11 s cycle. Stereo, the whole cue long."""
    N = int(LENGTH_S * sr)
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * t / 11.0)
    for root, lvl in ((n("D1"), 1.0), (n("A1"), 0.5), (n("D2"), 0.3)):
        f0 = midi_to_hz(root)
        for k, a in ((1, 1.0), (2, 0.55), (3, 0.25), (4, 0.12), (5, 0.06)):
            for side, det in ((0, 0.0), (1, 0.06 + 0.03 * k)):
                s = lvl * a * (0.7 + 0.3 * breath) * np.sin(2 * np.pi * (f0 * k + det) * t + g.uniform(0, 6.28))
                out[:, side] += s
                out[:, 1 - side] += 0.55 * s
    return out * stop_env(N, 8.0)[:, None] * 0.05


def song_notes(phrase: int, a: int, b: int, t0: float, lean: float) -> list[tuple[float, float, float]]:
    """[(t, dur, midi)] for CURRENT_SONG[phrase][a:b] from t0 at the reading pace; the last note leans long."""
    out, pos = [], t0
    for i, (m, beats) in enumerate(CURRENT_SONG[phrase][a:b]):
        d = beats * CB * (lean if i == b - a - 1 else 1.0)
        out.append((pos, d, float(m + SONG_SHIFT)))
        pos += d
    return out


def ysolde_notes(t0: float, first: int, last: int) -> list[tuple[float, float, float]]:
    """[(t, dur, midi)] of her LINE, bars first..last, at her own tempo, from t0."""
    out = []
    for bi, bar in enumerate(YS.LINE[first - 1:last]):
        pos = t0 + bi * YS.BAR
        for p, beats in bar:
            d = beats * YS.BEAT
            if p is not None:
                out.append((pos, d, n(p) + YS_SHIFT))
            pos += d
    return out


# Bus gains from measured bus loudness (gated integrated per bus, render(stats=...)), relative to the low string's
# current-song (0 LU): the bed -3, the pedal -5, the soundings -6 where they sound, Ysolde -4 (the only layer over
# the reading band, so it carries the second half's air; the plucks' raw level is very high, hence their gain).
# Measured on the master (render(stats=...)): the 300 Hz-3 kHz band is 0.8 % of the spectrum's energy.
GAINS = {"song": 0.0, "bed": -2.3, "pedal": -10.1, "sound": -40.1, "ysolde": 14.2}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = Mixer(LENGTH_S)
    G = GAINS
    mx.bus("song", G["song"], send=0.35, process=low_band)
    mx.bus("bed", G["bed"], send=0.3, process=low_band)
    mx.bus("pedal", G["pedal"], send=0.2, process=low_band)
    mx.bus("sound", G["sound"], send=0.3, process=low_band)
    mx.bus("ysolde", G["ysolde"], send=0.3, process=high_band)
    mx.add("pedal", pedal(rng(SEED + 1)), 0.0)
    for i, (t0, t1, notes) in enumerate(BED):            # low strings on the chords, bowed, overlapping
        x = pad_chord([n(p) for p in notes.split()], t1 - t0, 0.6, seed=SEED + 100 + i, voices=4, spread_cents=6.0,
                      attack=6.0 if i == 0 else 2.0, release=0.6 if t1 >= T_BREAK else 2.4, width=0.6)
        mx.add("bed", x, t0)
    body = V.body_ir(((70.0, 9, 1.0), (140.0, 10, 0.7), (260.0, 8, 0.4), (500.0, 6, 0.2)), SEED + 7, length=0.3)
    for k, t in enumerate(SOUNDINGS):                    # the leadsman's call: twice
        for j in range(2):
            x = string_pluck(n("D2"), 2.4, 0.6 - 0.08 * j, seed=SEED + 300 + 10 * k + j, pick_pos=0.22, t60=2.2,
                             B=2e-5, max_f=1500.0, release=0.4)
            mx.add("sound", fft_convolve(x, body)[: len(x) + 3000], t + 0.62 * j + float(g.normal(0, 0.006)),
                   pan=-0.15)
    lines = [song_notes(ph, a, b, t0, lean) for t0, ph, a, b, lean in FRAGMENTS]
    t0, ph, a, b = LAST
    last = song_notes(ph, a, b, t0, 1.0)
    lt, _, lm = last[-1]
    last[-1] = (lt, T_BREAK - lt, lm)                    # the C, until the page runs out
    for li, line in enumerate(lines + [last]):           # the current-song on a solo low string, sul tasto
        for i, (t, d, m) in enumerate(line):
            broken = li == len(lines) and i == len(line) - 1
            x = pad_chord([m], d, vel=0.75 if d > 0.6 else 0.62, seed=SEED + 500 + 20 * li + i, voices=3,
                          spread_cents=4.0, attack=min(0.45, 0.35 * d), release=0.5 if broken else 1.3, width=0.35)
            mx.add("song", x, t - 0.06)
    box = YS.lacquer_box(SEED + 9)
    for k, (t0, first, lastbar) in enumerate(YSOLDE):    # Ysolde, exact: her 2 ms of scatter
        for i, (t, d, m) in enumerate(ysolde_notes(t0, first, lastbar)):
            v = 0.5 * g.uniform(0.97, 1.03) * (0.8 if m > n("C8") else 1.0)
            x = YS.zither(m, d, v, SEED + 700 + 50 * k + i, box)
            mx.add("ysolde", x, t + float(g.normal(0, YS.SCATTER)), pan=0.3)
    room = ModFDNReverb(rt60=2.6, rt60_high=1.1, predelay=0.03, size=1.1, mod_depth=7.0, mod_rate=0.35,
                        early_level=0.25, lowcut=40.0, seed=SEED % 9973)     # a covered dry-dock: wood, close
    st: dict = {}
    for name, bb in mx.buses.items():
        x = (bb.process(bb.buf) if bb.process else bb.buf) * 10 ** (bb.gain_db / 20)
        st[f"bus_{name}_lufs"] = float(integrated_lufs(x))
    master = mx.render(reverb=room, reverb_return_db=-3.0)
    f, gdb, q = BAND_CUT
    master = filt(master, [bq_peak(f, gdb, q)])
    k = int(2.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    spec = np.abs(np.fft.rfft(master.mean(axis=1))) ** 2
    fr = np.fft.rfftfreq(len(master), 1.0 / SR)
    band = (fr >= VOICE_BAND[0]) & (fr <= VOICE_BAND[1])
    st["voice_band_energy_pct"] = float(100 * spec[band].sum() / spec.sum())
    st["voice_band_pct_of_above_300"] = float(100 * spec[band].sum() / spec[fr >= VOICE_BAND[0]].sum())
    if stats is not None:
        stats.update(st)
    if verbose:
        print("  buses", {k_: round(v, 1) for k_, v in st.items()})
        print(f"dace_ledger: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
