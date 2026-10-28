"""`kerrid_last_night`: Ch19, Kerrid's last quiet night with Rhen (M3-AUD-858; act3_plan.md §2, act_outline Ch19):
about 73 s, through-composed, not looped.

Original composition for this project (SPEC §2, §9). The one tune in it that recurs is the game's own and is loaded,
never retyped: Kerrid's stair (motifs.py `KERRID_STAIR`, D3 falling a fourth to A2, one note a stride, at
`KERRID_STAIR_BPM`), played on his own low bowed string over his own frame-drum tread (kerrid_stair.py `bowed`,
`cello_body`, loaded). The cello's melody over it, the harmony and the night sea's placing were written for this cue
and are not derived from any existing melody (the sea is unlamped.py's night sea, the game's own). The style evoked
is a slow, warm night piece for a low string; nothing is quoted. No voices.

The brief: his last quiet night with Rhen, at rest. In Ansedra he sat the nights out at the outer moorings among
the barge-polers (Ch13); here he and Rhen sit out the last one before the dive, with the drowned city of Iskarra
below and the night sea moving. **KERRID_STAIR's stride under a low string, unhurried**, at KERRID_STAIR_BPM; **the
night sea**; **nothing ends yet**. So:
* the stride never changes speed: 48 BPM from the first step to the last, a step on every beat (the first of each
  pair heavier) and the two notes a stride each. E3's `goodbye_kerrid` owns the slowing to a stop (motifs.py's rule,
  act3_ending E3); this cue does not spend it. Here the tread is softened (a hand on the drum, the bow light) and it
  walks on past the cue's end, fading in level, never in tempo;
* the low string is a solo cello in its tenor (A3-A4), above the stair: a warm, plain line in D, phrased in pairs of
  bars, the way two men talk when neither needs to;
* it ends open, on a held G major-ninth (a IV chord with the cello's A on top), not a cadence and not a slowing:
  the chord is still sounding and the stride still walking as the cue goes out.

D major, 4/4 at 48 BPM (a beat is 1.25 s, a stride 2.5 s, a bar 5 s), 14 bars and the held chord's ring.
Chords: D D | D Bm7 Gmaj9 D/F# | Em11 Gmaj9 Bm7 Asus4 | D Gmaj9 Em11 | Gmaj9, held. Every chord holds both of the
stair's notes, D and A (as root, fifth, ninth or eleventh), so the stride never clashes and never has to stop.

Layers (all synthesized; no samples): the tread (kerrid_stair's frame drum, played softer and muffled); the stair
(D3, A2) on his bowed low string, light; the cello's melody (the same bowed string, sul tasto); soft violas on the
chords above it and a low string root under it; the night sea.

Timeline (bars): 1 the sea and the tread | 2 the stair walks in under it | 3-12 the cello, five two-bar phrases, the
violas and the low root with it | 13 the cello rises E-F# toward the open A | 14 the A held over G major-ninth; the
stride walks on under it, quieter each step, and the cue goes out on the chord.

Render:  python3 assets_src/music/act3/kerrid_last_night.py
         (or tools/audio/render_all.py --act3 --only act3/kerrid_last_night)
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

from motifs import KERRID_STAIR, KERRID_STAIR_BPM, KERRID_STAIR_STRIDE  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, db_to_lin, filt, rng  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act3_kln_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KS = _mod("kerrid_stair")            # his bowed low string and its body
NIGHT = _mod("unlamped")             # the night sea

OUT = os.path.join(ROOT, "assets", "audio", "music", "act3", "kerrid_last_night.ogg")
SEED = 20261859
TARGET_LUFS = -16.0
QUALITY = 3.0
BPM = KERRID_STAIR_BPM               # 48, never changed
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 14
LEAD_IN = 0.3
RING = 3.4                           # the held chord's ring after bar 14
LENGTH = LEAD_IN + BARS * BAR + RING
FADE_FROM = 12.0                     # bars: from here the tread and the stair quieten (level only, never tempo)
STAIR_FROM = 1.0                     # bars: the stair walks in on bar 2
MELODY_FROM = 3
BOW_PRE = KS.BOW_PRE

## (chord, violas above, low root) per bar; bar 14's chord is the held one
CHORDS = [("D", "A4 D5 F#5", "D2"), ("D", "A4 D5 F#5", "D2"),
          ("D", "A4 D5 F#5", "D2"), ("Bm7", "A4 B4 D5 F#5", "B1"), ("Gmaj9", "F#4 A4 B4 D5", "G1"),
          ("D/F#", "A4 D5 F#5", "F#2"), ("Em11", "G4 A4 B4 D5", "E2"), ("Gmaj9", "F#4 A4 B4 D5", "G1"),
          ("Bm7", "A4 B4 D5 F#5", "B1"), ("Asus4", "A4 D5 E5", "A1"), ("D", "A4 D5 F#5", "D2"),
          ("Gmaj9", "F#4 A4 B4 D5", "G1"), ("Em11", "G4 A4 B4 D5", "E2"), ("Gmaj9", "F#4 B4 D5 F#5", "G1")]
assert len(CHORDS) == BARS
## the cello (note, beats) from bar 3: five two-bar phrases, the rise, and the open A held to the end
MELODY = [("A3", 1), ("D4", 1), ("F#4", 2), ("E4", 1.5), ("D4", .5), ("B3", 2),
          ("D4", 1), ("B3", 1), ("A3", 2), (None, 1), ("A3", 1), ("D4", 1), ("E4", 1),
          ("G4", 2), ("F#4", 1), ("E4", 1), ("D4", 3), ("B3", 1),
          ("D4", 1), ("E4", 1), ("F#4", 2), ("A4", 3), ("G4", 1),
          ("F#4", 2), ("E4", 1), ("D4", 1), ("B3", 2), ("D4", 2),
          ("E4", 2), ("F#4", 2),
          ("A4", 4 + RING / BEAT)]
assert abs(sum(b for _, b in MELODY[:-1]) - 4 * (BARS - MELODY_FROM)) < 1e-9


def t_of(bar: float, beat: float = 0.0) -> float:
    """Seconds from the file start to `beat` (0-based) of `bar` (1-based)."""
    return LEAD_IN + (bar - 1) * BAR + beat * BEAT


def walk_level(t: float) -> float:
    """The tread's and the stair's level: full until FADE_FROM, then quieter each step to the file's end (a
    diminuendo; the tempo never moves)."""
    t0, t1 = t_of(FADE_FROM + 1), LENGTH
    if t <= t0:
        return 1.0
    u = min(1.0, (t - t0) / (t1 - t0))
    return float((1.0 - u) ** 1.6)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = Mixer(LENGTH + 6.0)
    G = GAINS
    mx.bus("cello", G["cello"], send=0.32, process=KS.cello_body)
    mx.bus("stair", G["stair"], send=0.28, process=KS.cello_body)
    mx.bus("tread", G["tread"], send=0.22, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1500, 0.7)]))
    mx.bus("violas", G["violas"], send=0.5, process=lambda x: string_body(x, cutoff=2200.0))
    mx.bus("root", G["root"], send=0.3, process=lambda x: string_body(x, cutoff=700.0))
    mx.bus("sea", G["sea"], send=0.12)
    # the night sea, under everything, from the start to the end
    L = int(LENGTH * SR)
    sea = NIGHT.sea(L, SEED + 3)
    env = np.ones(L)
    k = int(4.0 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    mx.add("sea", sea * env[:, None], 0.0)
    # the tread: a step on every beat at 48, the first of each pair heavier, softened, walking on to the end
    beats = int((LENGTH - LEAD_IN - 0.4) / BEAT) + 1
    for i in range(beats):
        t = t_of(1, i)
        lvl = walk_level(t)
        if lvl < 0.03:
            break
        v = (0.42 if i % 2 == 0 else 0.27) * lvl * float(g.uniform(0.96, 1.03))
        mx.add("tread", frame_drum("dum", v, variant=i, size=1.7, seed=SEED + 1), t + float(g.normal(0, 0.004)),
               pan=-0.06)
    # the stair: D3 then A2, a stride each, from bar 2, light, to the end
    stride = KERRID_STAIR_STRIDE * BEAT
    i = 0
    while True:
        t = t_of(1 + STAIR_FROM) + i * stride
        lvl = walk_level(t)
        if t > LENGTH - 0.8 or lvl < 0.04:
            break
        m, _ = KERRID_STAIR[i % len(KERRID_STAIR)]
        x = KS.bowed(m, stride - 0.1, 0.5 * lvl * float(g.uniform(0.97, 1.02)), SEED + 100 + i, attack=0.4,
                     release=1.1)
        mx.add("stair", x, t - BOW_PRE, pan=0.06)
        i += 1
    # the cello's melody, sul tasto, from bar 3
    pos = t_of(MELODY_FROM)
    for j, (p, b) in enumerate(MELODY):
        d = b * BEAT
        if p is None:
            pos += d
            continue
        last = j == len(MELODY) - 1
        v = (0.72 if b >= 2 else 0.64) * float(g.uniform(0.97, 1.03)) * (0.9 if last else 1.0)
        x = KS.bowed(n(p) + 0.0, d + 0.06, v, SEED + 300 + j, attack=0.45 if b >= 2 else 0.3,
                     release=1.4 if last else 0.9)
        x = filt(x, [bq_lowpass(1900.0, 0.7)])                        # sul tasto: the bow over the fingerboard
        mx.add("cello", x, pos - BOW_PRE, pan=0.12)
        pos += d
    # the chords: violas above, a low root under, from bar 3; bar 14's held to the end
    for bar in range(MELODY_FROM, BARS + 1):
        _, hi, lo = CHORDS[bar - 1]
        held = bar == BARS
        d = BAR * 1.02 + (RING if held else 0.0)
        x = pad_chord([n(p) for p in hi.split()], d, 0.42, seed=SEED + 500 + bar, voices=4, spread_cents=7.0,
                      attack=1.3, release=2.2 if held else 1.4, width=0.8)
        mx.add("violas", x, t_of(bar) - 0.5)
        y = pad_chord([n(lo) + 12], d, 0.55, seed=SEED + 600 + bar, voices=3, spread_cents=5.0, attack=1.0,
                      release=2.0 if held else 1.2, width=0.3)
        mx.add("root", y, t_of(bar) - 0.4)
    st = {name: _bus_lufs(mx, name) for name in mx.buses}
    night = ModFDNReverb(rt60=3.0, rt60_high=1.2, predelay=0.03, size=1.3, mod_depth=8.0, mod_rate=0.3,
                         early_level=0.15, lowcut=60.0, seed=SEED % 9973)       # the open air over the water
    y = mx.render(reverb=night, reverb_return_db=-3.0)[:L]
    k = int(RING * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 1.5
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=QUALITY)
    m = measure(y)
    if stats is not None:
        stats["bus_lufs"] = st
    if verbose:
        print(f"kerrid_last_night: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  "
              f"TP {m['true_peak_dbtp']:.2f} dBTP")
        print("  buses (LU vs the cello)", {k_: round(v - st["cello"], 1) for k_, v in st.items()})
        print("  raw", {k_: round(v, 1) for k_, v in st.items()})
    return m


def _bus_lufs(mx: Mixer, name: str) -> float:
    """One bus's integrated loudness after its fader and processing (for setting the gains)."""
    b = mx.buses[name]
    x = b.process(b.buf) if b.process else b.buf
    return integrated_lufs(db_to_lin(b.gain_db) * x)


## Bus gains (dB), set from measured bus loudness for the planned levels: the cello at L, the stair L-4, the tread
## L-6, the violas L-10, the low root L-9, the sea L-12.
GAINS = {"cello": 0.0, "stair": -1.4, "tread": 8.3, "violas": 6.5, "root": 7.6, "sea": -15.7}


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
