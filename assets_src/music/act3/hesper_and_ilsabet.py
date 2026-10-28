"""`hesper_and_ilsabet`: Ch19, Wardens Hesper Oan and Ilsabet Rue, the revenant pair on the Lamp Spire's crown
(M3-AUD-858; act3_plan.md §2, act_outline Ch19, bible §4 the Abiding Conclave): two synchronized stems, a 90.0 s loop.

Original composition for this project (SPEC §2, §9). The one tune in it that recurs is the game's own and is loaded,
never retyped: the Order's hum (motifs.py `ORDER_HUM`, G A B A G E G D E G), here a hummed **ground**, the
congregation's tune augmented to nine bars and repeated five times under the whole fight, as the Order has repeated
it for four hundred years. The glass harmonica is Sefir's own instrument (sefir_theme.py `glass`, loaded): the
Conclave's sound, beautiful and airless. Hesper's line, Ilsabet's line, the harmony over the ground, the driving
ostinati and the bell figure were written for this fight and are not derived from any existing melody. The style
evoked is a driven, ground-bass battle piece in a cold modal key; nothing is quoted.

The brief: two of the five Abiding, Wardens who have held their posts for centuries and fought side by side the whole
time, on the open crown of the Iskarra Lamp Spire, 112 m over the drowned city, with the founders' anchor-engine's
teal core behind them (art/environments/iskarra.md). **Two lines that never meet.** Stem 0 is Hesper's line, stem 1
Ilsabet's: two independent voices in counterpoint that never land on a unison or share a cadence. When one Warden
falls, music.json `phases` takes that Warden's stem out (`stems_off`) and the other plays on alone, so each stem
carries its own half of the pulse and the harmony and stands as a whole fight by itself. Order's-hum colour, but a
battle: driven, not a lament.

E aeolian over the hum's G (the ground never cadences: it ends on C major-seventh over G and turns back to E minor
over G, so the fight never comes to rest), 4/4 at 120 BPM (a bar is 2.0 s), 45 bars = five grounds of nine.

**How the lines never meet** (checked by `never_meet()` at every render, which raises if either rule breaks):
* both phrases are a ground long (36 beats), but **Ilsabet's start half a ground after Hesper's** (beat 18), so each
  Warden holds a cadence while the other is moving: Hesper holds his on ground beats 29-35, Ilsabet hers on 11-16.5;
* the held cadence notes differ: Hesper's are B (the C major-seventh's seventh) or F# (its sharp eleventh), Ilsabet's
  always D (a ninth over C), so neither is ever a tonic and they are never the same note;
* no two notes of the same pitch class start together (within a sixteenth), and no two of the same pitch class sound
  together for more than a beat; and the registers never cross (Hesper B3-E5, Ilsabet F#5-A6), so there is no
  unison at all.

**Stem 0, Hesper** (`hesper_and_ilsabet_s0.ogg`): Hesper's line on low strings, marcato, doubled an octave below
(firm, quick, stepwise: an old soldier's line); the Order's hum as the ground, the low congregation humming
ORDER_HUM at half speed (G2 and down); the low-string ostinato driving eighths on the ground's note, accented 3+3+2;
frame drums on the 3+3+2 with ghosted eighths between, a big drum on every downbeat and a fill into each ground.

**Stem 1, Ilsabet** (`hesper_and_ilsabet_s1.ogg`): Ilsabet's line on Sefir's glass harmonica, high, in long notes,
doubled at the unison by soft violins (no attack, no wake); the harmony as a high open string pad and a bowed low
root; the bell figure, a soft metallophone (the lamp-engine's tick) running the chord's three tones in eighths in the
same 3+3+2; a big drum on the first two groups and a low kettle gong on the third. So stem 1 alone is the same fight
with the same accents, struck on other instruments.

Form: the ground five times (bars 1-9, 10-18, 19-27, 28-36, 37-45). Hesper: A B A B A'. Ilsabet: A B A B A, each
starting on ground beat 18 (bar 5's third beat), the fifth wrapping over the loop seam into bar 1. The drums build
over the grounds and the fill at each ground's end leads into the next; the loop wraps on bar 45's fill into bar 1.

Mastering (as wakefin): stem 1 is trimmed to stem 0's loudness, then both stems share one gain (the pair at -16
LUFS) and one limiter gain curve, the stricter of the pair's and each stem's own, so stem 0 + stem 1 is exactly the
limited mix and neither alone peaks over the ceiling. Two equal, uncorrelated halves sit about 3 LU under the pair.
Equal lengths, LOOPSTART = 0 on both. The files start a sixteenth before bar 1's downbeat (the sidecars'
`downbeat_offset_s`), so the wrap seam falls between strokes instead of on bar 1's big drum.

Render:  python3 assets_src/music/act3/hesper_and_ilsabet.py
         (or tools/audio/render_all.py --act3 --only act3/hesper_and_ilsabet)
"""
from __future__ import annotations

import gc
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import ORDER_HUM  # noqa: E402
from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act3_hi_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SEFIR = _mod("sefir_theme")          # the Conclave's glass harmonica

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music", "act3")
OUT = os.path.join(OUT_DIR, "hesper_and_ilsabet_s0.ogg")
OUT2 = os.path.join(OUT_DIR, "hesper_and_ilsabet_s1.ogg")
SEED = 20261858
TARGET_LUFS = -16.0
QUALITY = 3.0
CEILING_DB = -2.0
BPM = 120.0
BEAT = 60.0 / BPM
E8 = BEAT / 2                        # one eighth
S16 = BEAT / 4
## the files start a sixteenth before bar 1's downbeat, so the wrap seam falls between strokes, not on the downbeat
LEAD_IN_S16 = 1
BAR = 4 * BEAT
GROUND_BARS = 9
GROUNDS = 5
BARS = GROUND_BARS * GROUNDS         # 45
LOOP_S = BARS * BAR                  # 90.0 s
GROUND_BEATS = 4 * GROUND_BARS       # 36

## the ground: ORDER_HUM at half speed (its beats doubled), loaded from motifs.py
GROUND = [(m, 2.0 * b) for m, b in ORDER_HUM]
assert abs(sum(b for _, b in GROUND) - GROUND_BEATS) < 1e-9
## one chord over each ground note (E aeolian; the last, C major-seventh over G, never closes the ground)
CHORDS = ["E G B", "A C E", "B D F#", "D F# A", "C E G", "E G B", "G B D", "D F# A", "A C E", "C E G B"]
assert len(CHORDS) == len(GROUND)
## the open high pad's voicing per chord (stem 1) and the bell figure's three tones (B4-B5)
PAD_HI = ["E4 B4 G5", "A4 E5 C6", "B4 F#5 D6", "A4 D5 F#5", "G4 E5 C6", "E4 B4 G5", "G4 D5 B5", "A4 D5 F#5",
          "A4 E5 C6", "G4 E5 B5"]
BELLS = ["B4 E5 G5", "C5 E5 A5", "B4 D5 F#5", "A4 D5 F#5", "C5 E5 G5", "B4 E5 G5", "B4 D5 G5", "A4 D5 F#5",
         "C5 E5 A5", "B4 E5 G5"]

## Hesper's phrases (note, beats), one ground long, from ground beat 0; his cadence is held on beats 29-35
H_A = [("B3", 1), ("E4", 1), ("D4", .5), ("E4", .5), ("G4", 1),
       ("A4", 1.5), ("G4", .5), ("E4", 1),
       ("F#4", 1), ("D4", 1), ("B3", 1), ("D4", 1),
       ("A3", .5), ("D4", .5), ("F#4", 1),
       ("G4", 1.5), ("E4", .5), ("C4", 1), ("E4", 1),
       ("B3", 1), ("G3", .5), ("A3", .5), ("B3", 1), ("E4", 1),
       ("D4", 1), ("B3", .5), ("D4", .5), ("G4", 1),
       ("F#4", 1.5), ("E4", .5), ("D4", 1),
       ("E4", 1), ("C4", 1), ("B3", 6), (None, 1)]
H_B = [("E4", .5), ("F#4", .5), ("G4", 1), ("B4", 1), ("A4", .5), ("G4", .5),
       ("A4", 1), ("C5", 1), ("B4", .5), ("A4", .5),
       ("B4", 1.5), ("A4", .5), ("F#4", 1), ("D4", 1),
       ("E4", .5), ("F#4", .5), ("A4", 1),
       ("G4", 1), ("E4", 1), ("G4", .5), ("A4", .5), ("B4", 1),
       ("E5", 1.5), ("D5", .5), ("B4", 1), ("G4", 1),
       ("A4", .5), ("B4", .5), ("D5", 1), ("B4", 1),
       ("A4", 1), ("F#4", 1), ("D4", 1),
       ("E4", 1), ("G4", 1), ("F#4", 6), (None, 1)]
## A' (the fifth ground): A with its last bars pushed up, into the loop's turn
H_A2 = H_A[:-4] + [("E4", 1), ("G4", 1), ("B3", 6), (None, 1)]
HESPER = [H_A, H_B, H_A, H_B, H_A2]

## Ilsabet's phrases (note, beats), one ground long, from ground beat 18; her cadence (D6) is held on beats 11-16.5
I_A = [("B5", 3), ("G6", 1), ("D6", 2), ("A5", 2), ("F#5", 1), ("C6", 1.5), ("E6", 1.5),
       ("G6", 2), ("E6", 1), ("D6", 1), ("C6", 2),
       ("G6", 2), ("F#6", 1), ("E6", 1), ("C6", 3), ("A5", 2), ("E6", 2), ("D6", 5.5), (None, 1.5)]
I_B = [("E6", 1.5), ("F#6", .5), ("D6", 1), ("G6", 3), ("D6", 1), ("E6", 1), ("F#6", 1), ("A6", 1.5), ("G6", 1.5),
       ("E6", 2), ("G6", 1), ("A6", 1), ("G6", 1), ("E6", 1),
       ("D6", 2), ("G6", 2), ("E6", 3), ("D6", 1), ("E6", 1), ("A6", 2), ("D6", 5.5), (None, 1.5)]
ILSABET = [I_A, I_B, I_A, I_B, I_A]
ILSABET_FROM = 18.0                  # ground beats: half a ground after Hesper
## each ground's dynamic (a slow build over the loop; the fifth eases so the wrap lands on the first)
GROUND_VEL = [0.86, 0.93, 1.0, 1.04, 0.95]

for _ph in HESPER + ILSABET:
    assert abs(sum(b for _, b in _ph) - GROUND_BEATS) < 1e-9, _ph


def t_of(bar: int, eighth: float = 0.0) -> float:
    """Seconds from the loop start to eighth `eighth` (0-based) of `bar` (1-based)."""
    return (bar - 1) * BAR + eighth * E8


def timeline(phrases: list, offset_beats: float) -> list[tuple[float, float, float, int]]:
    """[(start beat, beats, midi, ground index)] of a voice's five phrases, starting at `offset_beats` into ground 0;
    start beats wrap modulo the loop."""
    out, total = [], GROUNDS * GROUND_BEATS
    for gi, ph in enumerate(phrases):
        pos = gi * GROUND_BEATS + offset_beats
        for p, b in ph:
            if p is not None:
                out.append((pos % total, float(b), n(p), gi))
            pos += b
    return out


def never_meet() -> dict:
    """The rule of the cue, checked: Hesper's and Ilsabet's lines never start the same pitch class together, never
    hold the same pitch class together for more than a beat, never share a held cadence, and never cross."""
    total = GROUNDS * GROUND_BEATS
    h, s = timeline(HESPER, 0.0), timeline(ILSABET, ILSABET_FROM)

    def overlap(a0: float, ad: float, b0: float, bd: float) -> float:
        best = 0.0
        for k in (-total, 0.0, total):
            best = max(best, min(a0 + ad, b0 + k + bd) - max(a0, b0 + k))
        return best

    def onset_gap(a0: float, b0: float) -> float:
        d = abs(a0 - b0) % total
        return min(d, total - d)

    worst_hold, onsets = 0.0, 0
    for a0, ad, am, _ in h:
        for b0, bd, bm, _ in s:
            same = int(am) % 12 == int(bm) % 12
            ov = overlap(a0, ad, b0, bd)
            if same and onset_gap(a0, b0) < 0.25:
                raise AssertionError(f"same pitch class starts together: beat {a0} and {b0}")
            if same:
                worst_hold = max(worst_hold, ov)
                if ov > 1.0:
                    raise AssertionError(f"same pitch class held together {ov} beats: {a0}, {b0}")
            if ad >= 4 and bd >= 4 and ov > 0:
                raise AssertionError(f"cadences meet: {a0}, {b0}")
            onsets += 1
    if max(m for _, _, m, _ in h) >= min(m for _, _, m, _ in s):
        raise AssertionError("the lines cross")
    return {"pairs_checked": onsets, "longest_same_class_overlap_beats": worst_hold}


# ----------------------------------------------------------------------------------------------------------------
# Stem 0: Hesper
# ----------------------------------------------------------------------------------------------------------------
def build_s0(mx: LoopMixer) -> None:
    g = rng(SEED)
    # the ground, hummed by the low congregation: ORDER_HUM at half speed, an octave down, five times round
    line = [(m - 12, b * BEAT) for _ in range(GROUNDS) for m, b in GROUND]
    mx.add("hum", hum_ensemble(line, voices=14, seed=SEED + 1, register="low", loop=True), 0.0)
    # Hesper's line: marcato low strings, and the octave below
    for i, (b0, d, m, gi) in enumerate(timeline(HESPER, 0.0)):
        v = GROUND_VEL[gi] * float(g.uniform(0.94, 1.04)) * (1.08 if d >= 1.5 else 1.0)
        dur = d * BEAT * (0.97 if d >= 1 else 0.88)
        t = b0 * BEAT
        x = pad_chord([m], dur, 0.95 * v, seed=SEED + 1000 + i, voices=5, spread_cents=7.0, attack=0.035,
                      release=0.28 if d >= 4 else 0.12, width=0.45)
        mx.add("hesper", x, t - 0.012, pan=-0.18)
        y = pad_chord([m - 12], dur, 0.8 * v, seed=SEED + 3000 + i, voices=4, spread_cents=8.0, attack=0.04,
                      release=0.3 if d >= 4 else 0.14, width=0.35)
        mx.add("hesper_low", y, t - 0.008, pan=-0.1)
    # the ostinato and the drums, bar by bar
    for bar in range(1, BARS + 1):
        gi = (bar - 1) // GROUND_BARS
        gv = GROUND_VEL[gi]
        last = (bar - 1) % GROUND_BARS == GROUND_BARS - 1
        for e in range(8):
            beat = ((bar - 1) % GROUND_BARS) * 4 + e * 0.5
            root = n(_ground_note_at(beat)) - 12
            acc = e in (0, 3, 6)
            v = (0.95 if acc else 0.55) * gv * float(g.uniform(0.94, 1.04))
            x = pad_chord([root, root + 12] if acc else [root], E8 * 0.78, v, seed=SEED + 5000 + 8 * bar + e,
                          voices=4, spread_cents=10.0, attack=0.006, release=0.05, width=0.5)
            mx.add("ostinato", x, t_of(bar, e))
        mx.add("drums", big_drum(0.85 * gv, variant=bar, seed=SEED + 5), t_of(bar))
        for e in range(8):
            if last and e >= 5:
                continue
            if e in (0, 3, 6):
                st, v = "dum", 0.8 if e == 0 else 0.62
            elif e in (2, 5, 7):
                st, v = "ghost", 0.26 + 0.04 * gi
            else:
                continue
            mx.add("drums", frame_drum(st, v * gv * float(g.uniform(0.92, 1.05)), variant=bar * 8 + e, size=1.3,
                                       seed=SEED + 6), t_of(bar, e) + float(g.normal(0, 0.003)),
                   pan=0.08 if st == "dum" else -0.22)
        if last:                     # the fill into the next ground: sixteenths through beats 3.5-4
            for k in range(6):
                mx.add("drums", frame_drum("dum", (0.4 + 0.08 * k) * gv, variant=900 + 10 * bar + k, size=1.15,
                                           seed=SEED + 7), t_of(bar, 5 + 0.5 * k), pan=-0.25 + 0.1 * k)


def _ground_note_at(beat: float) -> int:
    """The ground's note (midi) at a beat within one ground."""
    pos = 0.0
    for m, b in GROUND:
        if beat < pos + b - 1e-9:
            return m
        pos += b
    return GROUND[-1][0]


def _ground_index_at(beat: float) -> int:
    pos = 0.0
    for i, (_, b) in enumerate(GROUND):
        if beat < pos + b - 1e-9:
            return i
        pos += b
    return len(GROUND) - 1


# ----------------------------------------------------------------------------------------------------------------
# Stem 1: Ilsabet
# ----------------------------------------------------------------------------------------------------------------
def build_s1(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    # Ilsabet's line: the Conclave's glass, high, long notes, with soft violins at the unison
    for i, (b0, d, m, gi) in enumerate(timeline(ILSABET, ILSABET_FROM)):
        v = GROUND_VEL[gi] * float(g.uniform(0.95, 1.03))
        dur = d * BEAT * 0.98
        t = b0 * BEAT
        mx.add("glass", SEFIR.glass(m, dur, 0.85 * v, seed=SEED + 7000 + i), t - 0.18, pan=0.2)
        x = pad_chord([m], dur, 0.7 * v, seed=SEED + 8000 + i, voices=6, spread_cents=6.0, attack=0.22,
                      release=0.6, width=0.5)
        mx.add("violins", x, t - 0.12, pan=0.15)
    # the harmony: one chord per ground note, a high open pad and a bowed low root
    for gi in range(GROUNDS):
        pos = gi * GROUND_BEATS
        for ci, (m, b) in enumerate(GROUND):
            t, d = pos * BEAT, b * BEAT
            x = pad_chord([n(p) for p in PAD_HI[ci].split()], d * 0.98, 0.5 * GROUND_VEL[gi],
                          seed=SEED + 9000 + 20 * gi + ci, voices=4, attack=0.35, release=0.6, width=0.9)
            mx.add("pad", x, t - 0.15)
            y = pad_chord([m - 12, m - 24], d * 0.98, 0.7 * GROUND_VEL[gi], seed=SEED + 9500 + 20 * gi + ci,
                          voices=4, spread_cents=6.0, attack=0.25, release=0.5, width=0.4)
            mx.add("low", y, t - 0.1)
            pos += b
    # the bell figure and the drums, bar by bar
    for bar in range(1, BARS + 1):
        gi = (bar - 1) // GROUND_BARS
        gv = GROUND_VEL[gi]
        last = (bar - 1) % GROUND_BARS == GROUND_BARS - 1
        for e, k in enumerate((0, 1, 2, 0, 1, 2, 1, 2)):
            beat = ((bar - 1) % GROUND_BARS) * 4 + e * 0.5
            tones = [n(p) for p in BELLS[_ground_index_at(beat)].split()]
            acc = e in (0, 3, 6)
            v = (0.42 if acc else 0.27) * gv * float(g.uniform(0.9, 1.04))
            x = metallophone_note(tones[k], v, seed=SEED + 10000 + 8 * bar + e, decay=1.4, hardness=0.16,
                                  ombak_hz=3.1, damp_at=0.42)
            mx.add("bells", x, t_of(bar, e) + float(g.normal(0, 0.002)), pan=0.35 - 0.1 * k)
        mx.add("drums2", big_drum(0.8 * gv, variant=100 + bar, seed=SEED + 15), t_of(bar))
        if not last:
            mx.add("drums2", big_drum(0.55 * gv, variant=200 + bar, seed=SEED + 15), t_of(bar, 3))
        root = n(_ground_note_at(((bar - 1) % GROUND_BARS) * 4 + 3)) - 12
        mx.add("gong", kettle_gong(root, 0.5 * gv, seed=SEED + 300 + bar, t60=1.1, damp_at=0.6), t_of(bar, 6),
               pan=-0.2)
        if last:                     # her side of the fill: three gong strokes rising to the turn
            for k in range(3):
                mx.add("gong", kettle_gong(root + 2 * k, (0.4 + 0.1 * k) * gv, seed=SEED + 700 + 10 * bar + k,
                                           t60=0.9, damp_at=0.4), t_of(bar, 4 + k * 0.5 + (0.5 if k else 0)),
                       pan=0.2 - 0.2 * k)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "hesper": 0.0, "hesper_low": -2.0, "hum": -1.4, "ostinato": 0.8, "drums": -9.8,
    "glass": 0.0, "violins": 11.2, "pad": 9.5, "low": 14.0, "bells": 10.9, "gong": 5.0, "drums2": 4.7,
}
## The plan (LU relative to each stem's lead, by each bus's integrated loudness over the loop).
PLAN = {
    "hesper": 0.0, "hesper_low": -5.0, "hum": -6.0, "ostinato": -5.0, "drums": -3.0,
    "glass": 0.0, "violins": -5.0, "pad": -9.0, "low": -6.0, "bells": -6.0, "gong": -6.0, "drums2": -4.0,
}
LEADS = ("hesper", "glass")


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 0:
        mx.bus("hesper", G["hesper"], send=0.25, process=lambda x: string_body(x, cutoff=2600.0))
        mx.bus("hesper_low", G["hesper_low"], send=0.2, process=lambda x: string_body(x, cutoff=1400.0))
        mx.bus("hum", G["hum"], send=0.5, process=lambda x: filt(x, [bq_lowpass(2200, 0.7)]))
        mx.bus("ostinato", G["ostinato"], send=0.12, process=lambda x: string_body(x, cutoff=1500.0))
        mx.bus("drums", G["drums"], send=0.15, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_peak(110, 2.0, 1.0),
                                                                           bq_lowpass(3000, 0.7)]))
    else:
        mx.bus("glass", G["glass"], send=0.55, process=lambda x: filt(x, [bq_highpass(250, 0.7)]))
        mx.bus("violins", G["violins"], send=0.45, process=lambda x: string_body(x, cutoff=3600.0))
        mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=2800.0))
        mx.bus("low", G["low"], send=0.25, process=lambda x: string_body(x, cutoff=900.0))
        mx.bus("bells", G["bells"], send=0.4, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(5000, 0.7)]))
        mx.bus("gong", G["gong"], send=0.3, process=lambda x: filt(x, [bq_highpass(40, 0.7), bq_lowpass(3500, 0.7)]))
        mx.bus("drums2", G["drums2"], send=0.15, process=lambda x: filt(x, [bq_highpass(30, 0.7),
                                                                             bq_lowpass(2600, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    meet = never_meet()
    loops, bus_lufs = [], {}
    for stem, build in ((0, build_s0), (1, build_s1)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        # the open crown: a wide, bright air over the drowned city, longer than a room
        crown = ModFDNReverb(rt60=3.4, rt60_high=1.6, predelay=0.035, size=1.4, mod_depth=9.0, mod_rate=0.3,
                             early_level=0.12, lowcut=90.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=crown, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
        del mx
        gc.collect()
    # stem 1 to stem 0's loudness, so either Warden alone is as present as the other
    trim_db = integrated_lufs(loops[0]) - integrated_lufs(loops[1])
    loops[1] = loops[1] * db_to_lin(trim_db)
    lead_in = int(round(LEAD_IN_S16 * S16 * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)

    def _lg(x: np.ndarray) -> np.ndarray:
        return limit_gain(np.concatenate([x[-ctx:], x, x[:ctx]]), CEILING_DB)[ctx: ctx + L]

    for _ in range(4):
        f = full * gain
        lg = np.minimum.reduce([_lg(f), _lg(loops[0] * gain), _lg(loops[1] * gain)])
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    extra = {"stems_of": "hesper_and_ilsabet", "loop_bars": BARS, "meter": "4/4", "downbeat_offset_s": lead_in / SR}
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1])
    m0, m1 = measure(stems[0]), measure(stems[1])
    if stats is not None:
        stats.update(bus_lufs=bus_lufs, never_meet=meet, stem0=m0, stem1=m1, pair=m, stem1_trim_db=trim_db,
                     limited_fraction=float((lg < 0.999).mean()))
    if verbose:
        print(f"hesper_and_ilsabet: {m['seconds']:.2f}s  pair {m['integrated_lufs']:.2f} LUFS TP "
              f"{m['true_peak_dbtp']:.2f} dBTP; stem 0 {m0['integrated_lufs']:.2f} LUFS TP {m0['true_peak_dbtp']:.2f};"
              f" stem 1 {m1['integrated_lufs']:.2f} LUFS TP {m1['true_peak_dbtp']:.2f} (trim {trim_db:+.2f} dB); "
              f"limited {(lg < 0.999).mean() * 100:.2f} %, max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        print("  never meet:", meet)
        for lead, names in (("hesper", ("hesper", "hesper_low", "hum", "ostinato", "drums")),
                            ("glass", ("glass", "violins", "pad", "low", "bells", "gong", "drums2"))):
            print(f"  buses (LU vs {lead})", {k: round(bus_lufs[k] - bus_lufs[lead], 1) for k in names})
            print("  raw", {k: round(bus_lufs[k], 1) for k in names})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
