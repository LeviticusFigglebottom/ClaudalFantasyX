"""Act II's Vowbound stings (M4-A2P-091; act2_plan.md §4.4; the cue sheet §3): each new Vowbound's `*_bound` sting
(its binding cinematic; a music.json cue, as Act I's virel_bound) and `*_summon` sting (battle_sfx.json
`vowbound_stings`, on the Music bus, as virel_summon). Kesh is callable from Ch16 on (vowbound.json `kesh`,
`bound_flag` ch16_kesh_bound), so she has her `kesh_summon` too; Act III's H03 reuses it.

Original (SPEC §2, §9). Each sting is built from its Vowbound's own world. Every figure was written here or is our
own motif, imported: the Kirru-mode Letting cell is farewell_tide.py's, and the loom figure is cloudloom.py's. None
is taken from any existing music.

    nhoa_bound     Ch11, Ressa bound: Pell kneels and says nothing. High glass and one Kirru whistle on the first three
                   notes of the Letting's cell in the Kirru mode (C#5 D#5 F#5), held; no drums. About 8 s.
    nhoa_summon    Nhoa called: the only Vowbound whose motes go up. Glass chimes rising through the cell, quicker, on
                   a breath of air. About 5 s.
    hesk_bound     Ch12, Hesk bound in the weaving-hall: Cloudloom's loom figure condensed into one bar in A major (lifted
                   from the hall's A minor), the hall's bells, and a Cantor's single sung note (only Cantors sing).
                   About 8 s.
    hesk_summon    Hesk called: the cords plucked in a rising sweep, and the bell. About 5 s.
    ethren_bound   Ch13, Ethren (Corran) bound in the Sanctum: glass harmonics over a held C major and Kerrid's bowed
                   string with no attack. Nothing strikes: still water. About 8 s.
    ethren_summon  Ethren called: a C major swell with no attack, a glass ring at its top, held. About 5 s.
    kesh_bound     Ch16, Kesh bound, all six elements in turn: six short colours chained (a fire-bell with crackle, ice
                   glass, a static chime, water bubbling, a holy bell, glimmer shimmer), resolving onto the Hush's A
                   minor. About 8 s.
    kesh_summon    Kesh called: the six colours again, quick (a flick each), and the Hush's A minor under them. About
                   5 s.

Stereo, -16 LUFS integrated, Vorbis q4, under assets/audio/act2/music/stings/ (plain git, ADR 0175).

Render:  python3 tools/audio/render_all.py --only vowbound_stings
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

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import sing  # noqa: E402
from synth.water import bubble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))
FT = _mod("farewell_tide", os.path.join(HERE, "farewell_tide.py"))     # LETTING_KIRRU
CL = _mod("cloudloom", os.path.join(HERE, "cloudloom.py"))             # FIGURE, beater()
KS = _mod("kerrid_stair", os.path.join(MUSIC, "kerrid_stair.py"))      # bowed(), cello_body()

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "music", "stings")
SEED = 20261970
TARGET_LUFS = -16.0


def _glass(m: float, vel: float, seed: int, decay: float = 3.0) -> np.ndarray:
    return metallophone_note(m, vel, seed=seed, decay=decay, hardness=0.2, pair=False)


def nhoa_bound(mx: Mixer, g) -> float:
    cell = FT.LETTING_KIRRU[:3]
    notes, pos = [], 0.6
    for i, (p, beats) in enumerate(cell):
        d = beats * 0.6 + (3.5 if i == len(cell) - 1 else 0.0)
        notes.append((pos, d, n(p), 0.7, i == 0))
        pos += beats * 0.6
    mx.add("voice", V.kirru_whistle([(s - 0.6, d, m, v, r) for s, d, m, v, r in notes], SEED + 1, vib_cents=14.0,
                                        breath=0.005), 0.6)
    for i, p in enumerate(("C#6", "F#6", "C#7")):
        mx.add("glass", _glass(n(p), 0.4, SEED + 10 + i, decay=4.0), 0.1 + 1.6 * i, pan=-0.5 + 0.5 * i)
    return 8.0


def nhoa_summon(mx: Mixer, g) -> float:
    for i, (p, _) in enumerate(FT.LETTING_KIRRU):
        mx.add("glass", _glass(n(p) + 12, 0.45, SEED + 20 + i, decay=2.5), 0.15 + 0.32 * i, pan=-0.6 + 0.2 * i)
    k = int(2.5 * SR)
    air = filt(g.standard_normal(k), [bq_bandpass(3000, 0.6)]) * np.sin(np.pi * np.arange(k) / k) ** 2
    mx.add("air", np.stack([air, air[::-1]], axis=1) * 0.06, 0.0)
    return 5.0


def hesk_bound(mx: Mixer, g) -> float:
    tones = [n(p) for p in ("A2", "E3", "A3", "C#4", "E4")]
    for eighth, idx, vel in CL.FIGURE:
        mx.add("pluck", string_pluck(tones[idx], 0.9, vel, seed=SEED + 30 + eighth, pick_pos=0.14, t60=2.0, B=5e-5,
                                     max_f=6000.0, release=0.1), 0.2 + eighth * 0.42, pan=-0.3 + 0.15 * idx)
        if eighth in (0, 3, 6):
            mx.add("pluck", CL.beater(g, 0.5), 0.2 + eighth * 0.42, pan=0.35)
    mx.add("bells", tower_bell(n("A3"), 0.55, seed=SEED + 40, t60=7.0, dark=0.3), 3.6, pan=-0.2)
    mx.add("bells", tower_bell(n("E4"), 0.45, seed=SEED + 41, t60=6.0, dark=0.3), 3.9, pan=0.3)
    mx.add("voice", sing([("a", 3.8)], [(n("C#5"), 3.8)], vel=0.55, seed=SEED + 42, vib_cents=10.0), 3.7)  # a Cantor
    return 8.0


def hesk_summon(mx: Mixer, g) -> float:
    for i, p in enumerate(("A2", "E3", "A3", "C#4", "E4", "A4", "C#5", "E5")):
        mx.add("pluck", string_pluck(n(p), 1.6, 0.5, seed=SEED + 50 + i, pick_pos=0.13, t60=2.2, B=5e-5, max_f=6500.0,
                                     release=0.1), 0.1 + 0.07 * i, pan=-0.6 + 0.16 * i)
    mx.add("bells", tower_bell(n("A4"), 0.55, seed=SEED + 60, t60=5.0, dark=0.2), 0.75)
    return 5.0


def ethren_bound(mx: Mixer, g) -> float:
    mx.add("pad", pad_chord([n(p) for p in ("C2", "G2", "C3", "E3", "G3")], 6.0, 0.4, seed=SEED + 70, attack=2.5,
                            release=2.0), 0.0)
    mx.add("bow", KS.bowed(n("C3"), 5.5, 0.38, seed=SEED + 71, attack=2.2, release=2.0), 0.4)
    for i, p in enumerate(("G5", "C6", "E6", "G6")):
        mx.add("glass", _glass(n(p), 0.18, SEED + 72 + i, decay=5.0), 1.5 + 1.2 * i, pan=-0.45 + 0.3 * i)
    return 8.0


def ethren_summon(mx: Mixer, g) -> float:
    mx.add("pad", pad_chord([n(p) for p in ("C3", "G3", "C4", "E4")], 3.5, 0.45, seed=SEED + 80, attack=1.6,
                            release=1.2), 0.0)
    mx.add("glass", _glass(n("C7"), 0.3, SEED + 81, decay=3.0), 1.6)
    return 5.0


def kesh_bound(mx: Mixer, g) -> float:
    t = 0.1
    # fire: a bell struck hot, with crackle
    mx.add("bells", tower_bell(n("A4"), 0.5, seed=SEED + 90, t60=2.0, dark=0.0), t, pan=-0.6)
    for _ in range(14):
        k = int(0.004 * SR)
        mx.add("air", np.repeat((filt(g.standard_normal(k), [bq_highpass(1500, 0.7)]) * np.linspace(1, 0, k)
                                 * float(g.uniform(0.2, 0.6)))[:, None], 2, axis=1), t + float(g.uniform(0, 0.8)))
    t += 0.9
    mx.add("glass", _glass(n("E7"), 0.4, SEED + 91, decay=1.5), t, pan=-0.35)          # ice
    mx.add("glass", _glass(n("B6"), 0.3, SEED + 92, decay=1.5), t + 0.08, pan=-0.3)
    t += 0.9
    k = int(0.5 * SR)                                                                     # lightning: a static chime
    static = np.zeros(k)                                                                  # sparse, band-limited ticks
    for _ in range(10):
        s0 = int(g.uniform(0, k - 200))
        static[s0: s0 + 120] += filt(g.standard_normal(120), [bq_bandpass(float(g.uniform(3000, 6000)), 1.5)]) \
            * np.linspace(1, 0, 120) * float(g.uniform(0.2, 0.6))
    mx.add("air", np.stack([static, static], axis=1) * 0.25, t)
    mx.add("glass", _glass(n("D#6"), 0.35, SEED + 93, decay=1.2), t, pan=0.0)
    t += 0.9
    for _ in range(10):                                                                   # water
        mx.add("air", np.repeat(bubble(float(g.uniform(2.0, 5.0)), float(g.uniform(0.1, 0.25)))[:, None], 2, axis=1),
               t + float(g.uniform(0, 0.7)), pan=0.3)
    t += 0.9
    mx.add("bells", tower_bell(n("E5"), 0.5, seed=SEED + 94, t60=3.0, dark=0.2), t, pan=0.4)   # holy
    t += 0.9
    for i, p in enumerate(("A6", "C7", "E7")):                                               # glimmer
        mx.add("glass", _glass(n(p), 0.2, SEED + 95 + i, decay=2.0), t + 0.12 * i, pan=0.5)
    t += 0.6
    mx.add("pad", pad_chord([n(p) for p in ("A2", "E3", "A3", "C4", "E4")], 3.0, 0.5, seed=SEED + 99, attack=0.6,
                            release=1.5), t)                                                # the Hush's A minor
    return 8.5


def kesh_summon(mx: Mixer, g) -> float:
    t = 0.05
    flicks = [("bells", lambda: tower_bell(n("A5"), 0.4, seed=SEED + 110, t60=1.2, dark=0.0)),          # fire
              ("glass", lambda: _glass(n("E7"), 0.3, SEED + 111, decay=1.0)),                          # ice
              ("glass", lambda: _glass(n("D#6"), 0.3, SEED + 112, decay=0.8)),                         # lightning
              ("air", lambda: np.repeat(bubble(3.5, 0.2)[:, None], 2, axis=1)),                        # water
              ("bells", lambda: tower_bell(n("E5"), 0.4, seed=SEED + 113, t60=2.0, dark=0.2)),          # holy
              ("glass", lambda: _glass(n("C7"), 0.25, SEED + 114, decay=1.6))]                         # glimmer
    for i, (bus, f) in enumerate(flicks):
        mx.add(bus, f(), t + 0.32 * i, pan=-0.6 + 0.24 * i)
    mx.add("pad", pad_chord([n(p) for p in ("A2", "E3", "A3", "C4", "E4")], 2.6, 0.45, seed=SEED + 115, attack=0.9,
                            release=1.2), 0.4)                                                      # the Hush's A minor
    return 5.0


STINGS = {"nhoa_bound": nhoa_bound, "nhoa_summon": nhoa_summon, "hesk_bound": hesk_bound, "hesk_summon": hesk_summon,
          "ethren_bound": ethren_bound, "ethren_summon": ethren_summon, "kesh_bound": kesh_bound,
          "kesh_summon": kesh_summon}
FILES = [f"{s}.ogg" for s in STINGS]


def render_one(name: str, out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    g = rng(SEED + 1000 * (list(STINGS).index(name) + 1))
    mx = Mixer(10.5)
    mx.bus("voice", -2.0, send=0.45, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_lowpass(5500, 0.7)]))
    mx.bus("glass", -6.0, send=0.6, process=lambda x: filt(x, [bq_lowpass(9000, 0.7)]))
    mx.bus("air", -12.0, send=0.4, process=lambda x: filt(x, [bq_lowpass(7000, 0.7)]))
    mx.bus("pluck", 0.0, send=0.35, process=lambda x: filt(x, [bq_lowpass(5500, 0.7)]))
    mx.bus("bells", -4.0, send=0.5, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
    mx.bus("pad", -4.0, send=0.45, process=lambda x: string_body(x, cutoff=1600.0))
    mx.bus("bow", -2.0, send=0.4, process=lambda x: filt(KS.cello_body(x), [bq_lowpass(1500, 0.7)]))
    length = STINGS[name](mx, g)
    hall = ModFDNReverb(rt60=2.6, rt60_high=1.1, predelay=0.03, size=1.3, mod_depth=8.0, mod_rate=0.4,
                        early_level=0.25, lowcut=110.0, seed=SEED % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-3.0)[: int(length * SR)]
    k = int(1.2 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-3.0)   # crackle and glass overshoot when decoded
    write_ogg(os.path.join(out_dir, name + ".ogg"), y, quality=4.0)
    m = measure(y)
    if verbose:
        print(f"{name}: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    return {s: render_one(s, out_dir, verbose) for s in STINGS}


if __name__ == "__main__":
    render()
