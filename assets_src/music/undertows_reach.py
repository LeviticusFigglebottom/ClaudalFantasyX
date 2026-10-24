"""`undertows_reach`: the Undertow's Reach boss (M3-AUD-09; act_outline Ch8): three synchronized stems, a 70 s loop.

Original composition for this project (SPEC §2, §9). The drowned men's chorale, the twin-flute theme, the wave
ostinato and the current-song line below were written for this fight and are not derived from any existing melody.
The brief: the Undertow comes for Corrow; the boss is a colossal limb of the storm at the seawall, fought in
phases and ended by a scripted escape. Corrow has no weapon against it and nobody pretends otherwise, and the wall
falls anyway. So the music is not a hero's fight: it is the sea's size against a stair that was not wide enough.

G octatonic (half-whole: G Ab Bb B C# D E F), 12/8 at 96 dotted quarters a minute (a bar is 2.5 s), 28 bars. The
mode is new to the score and belongs to the storm alone: it repeats at every minor third, so its four minor triads
(G, Bb, C#, E) are equal and none of them is home, and a line moved down a minor third stays in it (the twin flutes).
The wave ostinato groups the twelve eighths 3+3+2+2+2: two long swells and three short breakers.

**Stem 1** (`undertows_reach_p1.ogg`, the Reach rises; plays from the start):
* the drowned: a low men's chorale, hummed (the Order hums; only Cantors sing), the theme in long notes from bar 5,
  each note struck once on a low metallophone bar;
* the storm: a noise band that swells through each bar and breaks on its short groups;
* a fingered bass and frame drums on the 3+3+2+2+2, a big drum on the two swells;
* Corrow: the beacon (a kettle gong on F#, the seawall cue's own; F# lies outside the storm's mode, the town's one
  fixed note) at each four bars, a large gong at bars 1 and 21.

**Stem 2** (`undertows_reach_p2.ogg`, the Reach strikes; phase 2):
* the theme on two hard-blown breath flutes a minor third apart, the upper doubled an octave up by a metallophone;
* muted plucks running the minor triads in eighths, rising and falling like the swell (the rope and block of the
  seawall cue, now at speed); frame-drum teks filling every eighth, slaps on the swells;
* low strings (the saw-ensemble pad, kept low).

**Stem 3** (`undertows_reach_p3.ogg`, the escape; the stair):
* the drive: the big drum on every dotted quarter, the bass doubled in running eighths an octave up, jingles on
  every eighth, a slap roll into each four-bar group and a noise riser through it;
* the current-song: high women's voices humming a slow line that never resolves, through the whole loop (what Rhen
  hears inside the storm's wall).

Form: 1-4 the Reach rises (storm, bass, drums) | 5-12 A | 13-20 B (higher) | 21-24 the limb draws back (the chorale
holds low, the drums thin) | 25-28 A' (shortened), the C# chord falling a tritone to bar 1's G.

Mastering (as the Drownbell): the three stems share one gain (the full stack at -16 LUFS) and one limiter gain curve
computed on the full stack (synth.mixer.limit_gain), so the stems sum exactly to the limited mix. Stems 2 and 3 are
trimmed so each step up is about 1.5-2 LU. Loop: LOOPSTART = 0 on all three; equal lengths. The files start a
sixteenth before bar 1's downbeat (the sidecars' `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.
The sidecars count dotted quarters (bpm 96, four to the bar).

Render:  python3 assets_src/music/undertows_reach.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum, jingle  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music")
OUT = os.path.join(OUT_DIR, "undertows_reach_p1.ogg")
STEM_NAMES = ("undertows_reach_p1.ogg", "undertows_reach_p2.ogg", "undertows_reach_p3.ogg")
SEED = 20261289
TARGET_LUFS = -16.0
BPM = 96.0                           # dotted quarters
E8 = 60.0 / BPM / 3                  # one eighth note
BAR_E = 12                           # 12/8
BAR = BAR_E * E8
BARS = 28
LOOP_S = BARS * BAR
ACC = (1, 4, 7, 9, 11)               # 3+3+2+2+2
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## the files start a sixteenth (half an eighth) before bar 1's downbeat; see render()
LEAD_IN_E = 0.5
## Trims at mastering (dB) on stems 2 and 3, so each layer lifts the stack about 1.5-2 LU (render prints the steps).
STEM2_GAIN_DB = -1.6
STEM3_GAIN_DB = 2.1

CHORDS = (["G", "G", "Bb", "G"]
          + ["G", "Bb", "C#", "Bb", "G", "E", "C#", "G"]
          + ["E", "E", "C#", "Bb", "E", "C#", "Bb", "Ab"]
          + ["G", "G", "Bb", "C#"]
          + ["G", "Bb", "E", "C#"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["D"] * 4 + ["A2"] * 4
ROOT_MIDI = {"G": "G1", "Bb": "Bb1", "C#": "C#2", "E": "E2", "Ab": "Ab1"}
FIFTH = {"G": 7, "Bb": 7, "C#": 7, "E": 7, "Ab": 6}      # Ab's fifth in the mode is D (diminished)
## the minor triads (and Ab's diminished one) for the plucks: root, third, fifth, octave
TONES = {"G": ["G3", "Bb3", "D4", "G4"], "Bb": ["Bb3", "C#4", "F4", "Bb4"], "C#": ["C#4", "E4", "Ab4", "C#5"],
         "E": ["E3", "G3", "B3", "E4"], "Ab": ["Ab3", "B3", "D4", "Ab4"]}
PLUCK = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1]

## the drowned men's chorale, (pitch, eighths), 12 eighths a bar, bars 5-28 in one breath-staggered line
HUM_A = [[("D4", 6), ("Bb3", 6)], [("F4", 9), ("D4", 3)], [("E4", 6), ("C#4", 6)], [("D4", 12)],
         [("G4", 6), ("F4", 3), ("D4", 3)], [("E4", 6), ("B3", 6)], [("C#4", 6), ("Bb3", 6)], [("G3", 12)]]
HUM_B = [[("E4", 12)], [("B3", 6), ("E4", 6)], [("C#4", 12)], [("F4", 6), ("D4", 6)],
         [("B3", 12)], [("C#4", 6), ("E4", 6)], [("D4", 6), ("F4", 6)], [("D4", 12)]]
HUM_D = [[("G3", 12)], [("G3", 12)], [("F3", 12)], [("E3", 12)]]
HUM_A2 = [HUM_A[0], HUM_A[1], [("E4", 6), ("B3", 6)], [("C#4", 6), ("Bb3", 3), ("Ab3", 3)]]
## the flutes' theme (the lower flute plays it a minor third down)
FL_A = [[("D5", 3), ("E5", 1), ("F5", 2), ("D5", 3), ("Bb4", 3)], [("F5", 4), ("E5", 2), ("D5", 3), ("F5", 3)],
        [("E5", 3), ("G5", 3), ("E5", 2), ("C#5", 4)], [("D5", 9), (None, 3)],
        [("G5", 3), ("F5", 3), ("D5", 3), ("Bb4", 3)], [("E5", 4), ("G5", 2), ("B5", 6)],
        [("Bb5", 3), ("Ab5", 3), ("G5", 3), ("E5", 3)], [("G5", 8), (None, 4)]]
FL_B = [[("B5", 6), ("Ab5", 3), ("G5", 3)], [("E5", 3), ("G5", 3), ("Ab5", 3), ("B5", 3)],
        [("C#6", 9), ("Bb5", 3)], [("D6", 6), ("C#6", 3), ("Bb5", 3)],
        [("B5", 6), ("Ab5", 3), ("E5", 3)], [("E5", 3), ("G5", 3), ("Ab5", 3), ("Bb5", 3)],
        [("Bb5", 6), ("F5", 3), ("D5", 3)], [("D5", 9), (None, 3)]]
FL_A2 = [FL_A[0], FL_A[1], FL_A[5], FL_A[6]]
## the current-song: one held tone a bar (women, high), the whole loop
SONG = {"G": "D5", "Bb": "C#5", "C#": "E5", "E": "B4", "Ab": "B4"}


def t_of(bar: int, e: float = 1.0) -> float:
    """Seconds from the loop start to eighth `e` (1-based) of `bar`."""
    return (bar - 1) * BAR + (e - 1) * E8


def add_flute(mx: LoopMixer, bus: str, bars: list, start_bar: int, seed: int, vel: float, pan: float,
              shift: int = 0, metal_bus: str | None = None) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, ee in bar:
            d = ee * E8
            if p is None:
                pos += d
                first = True
                continue
            m = n(p) + shift
            x = breath_flute(m, d * 0.93 + 0.02, vel * g.uniform(0.95, 1.04), seed=seed + int(round(pos * 1000)),
                             breath=0.55, scoop_cents=40.0 if first else 12.0, vib_cents=11.0 if ee >= 6 else 3.0,
                             vib_rate=5.6, swell=0.25 if ee >= 8 else 0.0, attack=0.03, release=0.15, beta=0.62)
            mx.add(bus, x, pos - FLUTE_PRE + float(g.normal(0, 0.003)), pan=pan)
            if metal_bus:
                y = metallophone_note(m + 12, 0.42, seed=seed + 7 + int(round(pos * 1000)), decay=2.2, hardness=0.7,
                                      ombak_hz=6.0, damp_at=min(d, 0.5))
                mx.add(metal_bus, y, pos, pan=0.1)
            pos += d
            first = False


def surge(g, sr: int = SR) -> np.ndarray:
    """One bar of storm: a noise band climbing 220 -> 900 Hz through the two swells, breaking on the short groups."""
    N = int((BAR + 0.8) * sr)
    t = np.arange(N) / sr
    noise = g.standard_normal(N)
    out = np.zeros(N)
    hop = int(0.2 * sr)
    for i in range(0, N, hop):
        c = 220.0 * (900.0 / 220.0) ** min(1.0, i / (BAR * sr))
        a = max(0, i - hop)
        seg = noise[a: min(N, i + 2 * hop)]
        y = filt(seg, [bq_bandpass(c, 0.8, sr)], sr=sr)
        out[a: a + len(y)] += y * np.hanning(len(y)) * 0.5
    peak = t_of(1, 7)
    env = np.where(t < peak, 0.25 + 0.75 * (t / peak) ** 1.4, np.exp(-(t - peak) / 0.6))
    for e in (9, 11):                                       # the breakers
        s = t_of(1, e)
        env += np.where(t >= s, 0.5 * np.exp(-(t - s) / 0.25), 0.0)
    env *= np.minimum(1.0, (N - np.arange(N)) / (0.2 * sr))
    return out * env / (np.std(out) + 1e-9)


def riser(seconds: float, g, sr: int = SR) -> np.ndarray:
    """A noise riser over four bars, 400 -> 4000 Hz, swelling to the next group's downbeat."""
    N = int(seconds * sr)
    noise = g.standard_normal(N)
    out = np.zeros(N)
    hop = int(0.2 * sr)
    for i in range(0, N, hop):
        c = 400.0 * 10.0 ** (i / N)
        a = max(0, i - hop)
        y = filt(noise[a: min(N, i + 2 * hop)], [bq_bandpass(c, 1.1, sr)], sr=sr)
        out[a: a + len(y)] += y * np.hanning(len(y)) * 0.5
    x = np.arange(N) / N
    out *= x ** 2.2
    k = int(0.05 * sr)
    out[-k:] *= np.linspace(1, 0, k)
    return out / (np.std(out) + 1e-9)


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch])
        thin = sec == "D" and bar < 23
        mx.add("storm", surge(rng(SEED + 500 + bar)), t_of(bar), pan=0.0)
        for e, dur_e, off, v in ((1, 2.7, 0, 0.85), (4, 2.7, 0, 0.7), (7, 1.8, 12, 0.72), (9, 1.8, 7, 0.6),
                                 (11, 1.8, 0, 0.64)):
            if thin and e not in (1, 7):
                continue
            o = FIFTH[ch] if off == 7 else off
            x = bass_note(root + o, dur_e * E8, v * g.uniform(0.93, 1.05), seed=SEED + 6000 + 20 * bar + e, mute=0.3)
            mx.add("bass", x, t_of(bar, e) + 0.003)
        for e in ACC:
            if thin and e not in (1, 7):
                continue
            v = 0.9 if e in (1, 7) else 0.66
            mx.add("drums", frame_drum("dum", v * g.uniform(0.92, 1.05), variant=bar * 12 + e, seed=SEED + 3),
                   t_of(bar, e) + float(g.normal(0, 0.003)), pan=0.05)
        for e in (1, 7):
            mx.add("drums", big_drum(0.9 if e == 1 else 0.72, variant=bar + e, seed=SEED + 4), t_of(bar, e))
        if (bar - 1) % 4 == 0:
            mx.add("beacon", kettle_gong(n("F#4"), 0.4, seed=SEED + 400 + bar, t60=3.0), t_of(bar), pan=0.35)
    for bar in (1, 21):
        mx.add("gong", large_gong(n("G1"), 0.6, seed=SEED + 80 + bar, t60=9.0), t_of(bar), pan=-0.1)
    # the drowned: one chorale line, bars 5-28
    bars = HUM_A + HUM_B + HUM_D + HUM_A2
    line = [(n(p), ee * E8) for bar in bars for p, ee in bar]
    x = hum_ensemble(line, voices=14, seed=SEED + 70, register="low", spread=0.85)
    env = np.ones(len(x))
    k = int(1.5 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    end = int((len(bars) * BAR - 0.1) * SR)
    env[end - k: end] *= np.linspace(1, 0, k) ** 2
    env[end:] = 0.0
    mx.add("hum", x * env[:, None], t_of(5) - 0.12)
    pos_bar = 5
    for bar in bars:                                         # each chorale note struck once on a low bar
        pos = t_of(pos_bar)
        for p, ee in bar:
            mx.add("lowmetal", metallophone_note(n(p), 0.5, seed=SEED + 900 + int(round(pos * 1000)), decay=3.0,
                                                 hardness=0.45, ombak_hz=4.0), pos, pan=-0.2)
            pos += ee * E8
        pos_bar += 1


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar in range(1, BARS + 1):
        ch = CHORDS[bar - 1]
        sec = SECTION[bar - 1]
        tones = TONES[ch]
        brk = sec == "D" and bar < 23
        for e in range(1, BAR_E + 1):
            if brk and e % 2 == 0:
                continue
            v = (0.55 if e in ACC else 0.4) * g.uniform(0.9, 1.06)
            x = string_pluck(n(tones[PLUCK[e - 1]]), E8 * 0.9, v, seed=SEED + 2000 + 20 * bar + e, pick_pos=0.14,
                             t60=1.4, mute=0.45, max_f=4500.0, release=0.03)
            mx.add("pluck", x, t_of(bar, e) + float(g.normal(0, 0.003)), pan=0.3 if e % 2 else -0.3)
            if not brk and e not in ACC:
                mx.add("drums2", frame_drum("tek" if e % 2 == 0 else "ghost", 0.42 * g.uniform(0.85, 1.1),
                                            variant=bar * 12 + e, seed=SEED + 5), t_of(bar, e), pan=-0.15)
        if not brk:
            for e in (4, 10):
                mx.add("drums2", frame_drum("slap", 0.7 * g.uniform(0.92, 1.05), variant=bar + e, seed=SEED + 5),
                       t_of(bar, e), pan=0.08)
    for bar in range(1, BARS + 1, 2):
        ch = CHORDS[bar - 1]
        root = n(ROOT_MIDI[ch]) + 12
        x = pad_chord([root, root + FIFTH[ch], root + 12], 2 * BAR - 0.05, 0.85, seed=SEED + 3000 + bar, voices=5,
                      spread_cents=12.0, attack=0.4, release=0.6, width=0.7)
        mx.add("strings", x, t_of(bar) - 0.03)
    for bars, start, s in ((FL_A, 5, 100), (FL_B, 13, 200), (FL_A2, 25, 300)):
        add_flute(mx, "flute", bars, start, SEED + s, 0.9, -0.15, metal_bus="flute_metal")
        add_flute(mx, "flute2", bars, start, SEED + s + 50, 0.8, 0.3, shift=-3)


def build_p3(mx: LoopMixer) -> None:
    g = rng(SEED + 2)
    for bar in range(1, BARS + 1):
        ch = CHORDS[bar - 1]
        root = n(ROOT_MIDI[ch])
        last = bar % 4 == 0
        for e in (1, 4, 7, 10):
            mx.add("drums3", big_drum(0.85 if e == 1 else 0.7, variant=bar + e, seed=SEED + 7), t_of(bar, e), pan=0.15)
        for e in range(1, BAR_E + 1):
            off = 12 if e % 2 else 24
            x = bass_note(root + off, E8 * 0.8, (0.7 if e in ACC else 0.5) * g.uniform(0.93, 1.05),
                          seed=SEED + 8000 + 20 * bar + e, mute=0.6)
            mx.add("bass2", x, t_of(bar, e) + 0.002)
            mx.add("jingle", jingle(0.45 if e in (1, 4, 7, 10) else 0.3, variant=bar + e, seed=SEED + 9),
                   t_of(bar, e), pan=0.3)
        if last:                                               # a slap roll into the next group (ends a sixteenth early)
            for k in range(10):
                e = 7 + 0.5 * k
                mx.add("drums3", frame_drum("slap" if k % 2 else "dum", 0.45 + 0.05 * k, variant=k, seed=SEED + 6),
                       t_of(bar, e), pan=-0.05)
    for start in range(1, BARS + 1, 4):
        mx.add("riser", riser(4 * BAR - E8, rng(SEED + 600 + start)), t_of(start), pan=0.0)
    line = [(n(SONG[ch]), BAR) for ch in CHORDS]
    x = hum_ensemble(line, voices=8, seed=SEED + 90, register="high", spread=0.9, loop=True)
    mx.add("song", x, 0.0)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "hum": 0.0, "lowmetal": -3.7, "storm": -30.2, "bass": -7.1, "drums": -8.9, "beacon": -9.9, "gong": -16.2,
    "flute": -6.3, "flute2": -9.0, "flute_metal": -4.9, "pluck": -0.3, "drums2": -0.3, "strings": -5.7,
    "drums3": -8.9, "bass2": -9.1, "jingle": 2.3, "riser": -42.5, "song": 6.7,
}
## The plan (LU relative to the stem-1 lead, the drowned chorale, by each bus's integrated loudness over the loop).
PLAN = {
    "hum": 0.0, "lowmetal": -8.0, "storm": -10.0, "bass": -6.0, "drums": -4.0, "beacon": -12.0, "gong": -12.0,
    "flute": -1.0, "flute2": -5.0, "flute_metal": -8.0, "pluck": -9.0, "drums2": -7.0, "strings": -10.0,
    "drums3": -5.0, "bass2": -9.0, "jingle": -12.0, "riser": -12.0, "song": -6.0,
}


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("hum", G["hum"], send=0.55)
        mx.bus("lowmetal", G["lowmetal"], send=0.3)
        mx.bus("storm", G["storm"], send=0.2, process=lambda x: filt(x, [bq_highpass(120, 0.7)]))
        mx.bus("bass", G["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(90, 2.0, 0.9),
                                                                        bq_lowpass(3000, 0.7)]))
        mx.bus("drums", G["drums"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7)]))
        mx.bus("beacon", G["beacon"], send=0.45)
        mx.bus("gong", G["gong"], send=0.4)
    elif stem == 2:
        fl = lambda x: filt(x, [bq_highpass(220, 0.7), bq_peak(2300, 2.0, 1.0)])  # noqa: E731
        mx.bus("flute", G["flute"], send=0.22, process=fl)
        mx.bus("flute2", G["flute2"], send=0.25, process=fl)
        mx.bus("flute_metal", G["flute_metal"], send=0.3)
        mx.bus("pluck", G["pluck"], send=0.15, process=lambda x: filt(x, [bq_highpass(140, 0.7),
                                                                           bq_lowpass(4200, 0.7)]))
        mx.bus("drums2", G["drums2"], send=0.12, process=lambda x: filt(x, [bq_peak(3500, 1.5, 0.8)]))
        mx.bus("strings", G["strings"], send=0.3, process=lambda x: string_body(x, cutoff=1400.0))
    else:
        mx.bus("drums3", G["drums3"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7)]))
        mx.bus("bass2", G["bass2"], send=0.0, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(2500, 0.7)]))
        mx.bus("jingle", G["jingle"], send=0.1)
        mx.bus("riser", G["riser"], send=0.2, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
        mx.bus("song", G["song"], send=0.6)


# Levels (LU relative to the drowned chorale, the stem-1 lead; PLAN above): its low bars -8, the storm -10, bass -6,
# drums -4, the beacon and the gong -12; in stem 2 the upper flute -1, the lower flute -5, the metallophone doubling
# -8, plucks -9, the teks and slaps -7, strings -10; in stem 3 the big drums -5, the running bass -9, jingles -12, the
# riser -12, the current-song -6. GAINS were set from a render's measured bus loudness to land these, and confirmed
# by a second render.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2), (3, build_p3)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=9.0)
        _bus_setup(mx, stem)
        build(mx)
        sea = ModFDNReverb(rt60=2.6, rt60_high=1.0, predelay=0.025, size=1.0, mod_depth=8.0, mod_rate=0.5,
                           early_level=0.3, lowcut=110.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=sea, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    loops[2] = loops[2] * db_to_lin(STEM3_GAIN_DB)
    # The loop is periodic, so the files may start anywhere: a sixteenth before bar 1's downbeat, so the wrap seam
    # falls in a quiet sixteenth instead of on the heaviest attack (big drums, gong, beacon and bass at once).
    lead_in = int(round(LEAD_IN_E * E8 * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1] + loops[2]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    # one limiter gain curve for all stems, from the full stack (wrap-aware), iterated to the target
    for _ in range(4):
        f = full * gain
        lg = limit_gain(np.concatenate([f[-ctx:], f, f[:ctx]]), -2.0)[ctx: ctx + L]
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path] + [os.path.join(os.path.dirname(out_path), s) for s in STEM_NAMES[1:]]
    extra = {"stems_of": "undertows_reach", "loop_bars": BARS, "meter": "12/8 (bpm counts dotted quarters)",
             "downbeat_offset_s": lead_in / SR}
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=3.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1] + stems[2])
    steps = [integrated_lufs(stems[0]), integrated_lufs(stems[0] + stems[1])]
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["stem1_lufs"], stats["stems12_lufs"] = steps
        stats["limited_fraction"] = float((lg < 0.999).mean())
    if verbose:
        print(f"undertows_reach: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP "
              f"{m['true_peak_dbtp']:.2f} dBTP; stem 1 alone {steps[0]:.2f}, stems 1+2 {steps[1]:.2f} LUFS; "
              f"limited {(lg < 0.999).mean() * 100:.2f} %, max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        lead = bus_lufs["hum"]
        print("  buses (LU vs the chorale)", {k: round(v - lead, 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
