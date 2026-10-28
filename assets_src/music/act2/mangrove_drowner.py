"""`mangrove_drowner`: the Mangrove Drowner boss (M3-AUD-844; act_outline Ch10, docs/kb/art/creatures/act2/
mangrove_drowner.md): two synchronized stems, a 77.4 s loop.

Original composition for this project (SPEC §2, §9). Original-material check: the theme, the flute's counter-line,
the haul in the bass and every part below were written for this fight. The theme grows from Ossa Fen's own cell (the
low sway D-F-G, ossa_fen.py, ours) **turned over**: G-F-D, the sway dragged down instead of rising, and the fen's
raised sixth (E natural, the note the fen owns) pulled down to Eb. The spawn's moan is a falling semitone, nothing
more. None of it is taken from any melody we know; the style evoked (a nasal reed over drums in a churning compound
meter) is a colour, not a quotation. Nothing is borrowed from another cue but the fen's instruments.

The brief: Ossa Fen, in the roots of an old mangrove: Undertow-spawn that took root, its body a dome of twelve
arched prop-roots round a wet black core, motes it dragged down snagged in its roots. It fights by dragging (two roots
reach out along the water and haul back; the water draws toward it first). Phase 2 `uprooted` (50% HP): it wrenches
free, the stump splinters, six roots plant as legs and it rises. So the boss belongs to the fen (its pipe, its gourds,
its drips, its bar) but is darker and heavier: the fen's still water starts to pull.

G Aeolian (G A Bb C D Eb F; the fen's E natural gone to Eb), with the spawn's Ab (the Phrygian second) in its moan and
its chord in the breakdown; the D chord takes F#. 12/8 at 62 dotted quarters a minute: Ossa Fen's 62 BPM bar exactly
(3.871 s), churned into twelve eighths, 20 bars.

**Stem 1** (`mangrove_drowner_p1.ogg`, Rooted; plays from the start):
* the theme on the fen pipe (act2_voices.reed_pipe), shadowed an octave below by a darker pipe (A: bars 3-10, the
  sway's fragment in bar 11, B: 13-16, A': 17-20);
* the haul: a fingered bass whose long notes are dragged down into pitch (V.bend) on the 1 and the 7;
* frame drums on every eighth (dum, slap on the dotted beats), a big drum on the 1 and the 7; water-gourds
  (act2_voices.gourd) on the 6 and the 12, their pitch falling as the water swings;
* the draw: a band of water noise swelling over the last dotted beat of every second bar into the downbeat (the
  drag's telegraph, the water drawing toward it), the biggest into bars 3, 11 and 13;
* the spawn's moan: a low, three-voiced "oo" that slides down a semitone (Ab-G in bars 1-2, Eb-D in bars 11-12);
* a very dark low string pad on the chords; drips from the roots.

**Stem 2** (`mangrove_drowner_p2.ogg`, Uprooted; the game fades it in when the roots plant as legs):
* the walk: six root-knocks a bar (a struck-wood voice on six tuned roots, one per leg, on the odd eighths, panned
  across the legs), the gait of a six-legged cage;
* a hard-blown breath flute, high, with a sustained counter-line over A, B and A';
* low strings (root, fifth, octave) on every chord; the rising water (a noise band climbing in pitch and level over
  each phrase, bubbles thickening) and a sub-bass surge into each section;
* splinters (short woody cracks) and a second drum line (the big drum on the 4 and the 10, slaps on the 6 and 12).

Form (bars): 1-2 the roots (the haul, drums, gourds, the moan) | 3-10 A | 11-12 breakdown (the moan, the sway's
fragment, the big draw; the drums build from bar 12's seventh eighth) | 13-16 B | 17-20 A', ending on F#-D over the D
chord with a drum fill in bar 20; its last eighth is a rest, and D leads to bar 1's G minor.

Mastering (as cinder_matron.py): both stems share one gain (the full stack at -16 LUFS) and one limiter gain curve
computed on the full stack (synth.mixer.limit_gain), so stem 1 + stem 2 is exactly the limited mix. Stem 2 is
trimmed so the stack sits about +2 LU over stem 1 alone. Loop: LOOPSTART = 0 on both; equal lengths. The files start
half an eighth before bar 1's downbeat (the sidecars' `downbeat_offset_s`), so the wrap seam falls in bar 20's last,
empty eighth. Vorbis q3.

Render:  python3 assets_src/music/act2/mangrove_drowner.py   (or tools/audio/render_all.py --act2 --only
act2/mangrove_drowner)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, fft_convolve, filt,  # noqa: E402
                       midi_to_hz, rng, smooth_noise)
from synth.electric import bass_note  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble, drip  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(MUSIC, "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music", "act2")
OUT = os.path.join(OUT_DIR, "mangrove_drowner_p1.ogg")
OUT2 = os.path.join(OUT_DIR, "mangrove_drowner_p2.ogg")
SEED = 20261844
TARGET_LUFS = -16.0
BPM = 62.0                           # dotted quarters (Ossa Fen's tempo)
E8 = 60.0 / BPM / 3                  # one eighth, 0.323 s
BAR_E = 12                           # 12/8
BAR = BAR_E * E8
BARS = 20
LOOP_S = BARS * BAR
QUALITY = 3.0
## the file starts half an eighth before bar 1's downbeat, so the wrap seam falls in bar 20's last (empty) eighth
LEAD_IN_E = 0.5
## Stem 2's trim at mastering: the Uprooted stem lifts the stack about 2 LU over stem 1 alone (render prints both).
STEM2_GAIN_DB = 0.0

CHORDS = (["Gm", "Gm"]
          + ["Gm", "Cm", "Bb", "Gm", "Eb", "F", "Cm", "Gm"]
          + ["Gm", "Ab"]
          + ["Eb", "Cm", "Ab", "D"]
          + ["Eb", "F", "Cm", "D"])
SECTION = ["I"] * 2 + ["A"] * 8 + ["D"] * 2 + ["B"] * 4 + ["A2"] * 4
ROOT_MIDI = {"Gm": "G1", "Cm": "C2", "Bb": "Bb1", "Eb": "Eb2", "F": "F1", "Ab": "Ab1", "D": "D2"}
THIRD = {"Gm": 3, "Cm": 3, "Bb": 4, "Eb": 4, "F": 4, "Ab": 4, "D": 4}

## the theme (pitch | None, eighths); each bar is 12 eighths. The fen's sway turned over (G-F-D), its sixth at Eb.
THEME_A = [
    [("G4", 3), ("F4", 1), ("D4", 2), ("Eb4", 5), (None, 1)],
    [("D4", 2), ("F4", 1), ("G4", 3), ("Ab4", 3), ("G4", 3)],
    [("Bb4", 3), ("A4", 1), ("G4", 2), ("F4", 2), ("Eb4", 1), ("D4", 3)],
    [("G3", 6), (None, 3), ("D4", 1), ("F4", 1), ("G4", 1)],
    [("Bb4", 3), ("C5", 1), ("D5", 2), ("Eb5", 5), (None, 1)],
    [("D5", 2), ("C5", 1), ("Bb4", 3), ("C5", 3), ("A4", 3)],
    [("Bb4", 2), ("G4", 1), ("F4", 3), ("Eb4", 3), ("D4", 3)],
    [("G4", 9), (None, 3)],
]
FRAGMENT = [[("G4", 3), ("F4", 1), ("D4", 2), (None, 6)]]       # bar 11: the sway's fall, alone
THEME_B = [
    [("D5", 3), ("Eb5", 3), ("D5", 2), ("C5", 1), ("Bb4", 3)],
    [("C5", 3), ("D5", 3), ("Bb4", 3), ("G4", 3)],
    [("Ab4", 3), ("Bb4", 3), ("C5", 2), ("Bb4", 1), ("Ab4", 3)],
    [("G4", 6), ("F#4", 3), (None, 3)],
]
THEME_A2 = THEME_A[4:7] + [[("G4", 3), ("F#4", 3), ("D4", 4), (None, 2)]]
## stem 2: the flute's counter-line
COUNTER_A = [
    [("D5", 12)], [("Eb5", 6), ("G5", 6)], [("F5", 12)], [("D5", 9), (None, 3)],
    [("G5", 6), ("Bb5", 6)], [("A5", 6), ("C6", 6)], [("G5", 6), ("Eb5", 3), ("F5", 3)], [("D5", 9), (None, 3)],
]
COUNTER_B = [[("G5", 6), ("Bb5", 6)], [("Eb5", 6), ("G5", 6)], [("C6", 6), ("Eb6", 6)], [("D6", 9), (None, 3)]]
COUNTER_A2 = COUNTER_A[4:7] + [[("F#5", 6), ("A5", 4), (None, 2)]]
## the six legs (stem 2): each root's knock pitch (Hz), pan, and the eighth it plants on
LEGS = [(176.0, -0.7, 1), (208.0, 0.55, 3), (151.0, -0.25, 5), (233.0, 0.7, 7), (189.0, -0.55, 9), (162.0, 0.25, 11)]
LEG_VEL = (0.95, 0.55, 0.7, 0.85, 0.55, 0.7)


def t_of(bar: int, e: float = 1.0) -> float:
    """Seconds from the loop start to eighth `e` (1-based) of `bar`."""
    return (bar - 1) * BAR + (e - 1) * E8


# --------------------------------------------------------------------------- #
# voices written for this cue
# --------------------------------------------------------------------------- #
def moan(m0: float, m1: float, dur: float, vel: float, seed: int) -> np.ndarray:
    """The spawn's moan: one low voice on an "oo" (formants near 380 and 820 Hz), swelling in, holding `m0` and
    sliding down to `m1` over the middle of its last third, a slow wavering vibrato and breath. Mono."""
    g = rng(seed)
    N = int((dur + 1.0) * SR)
    t = np.arange(N) / SR
    slide = np.clip((t - 0.62 * dur) / (0.28 * dur), 0, 1)
    slide = slide * slide * (3 - 2 * slide)
    cents = (100.0 * (m1 - m0) * slide + 10.0 * np.clip(t / 2.0, 0, 1) * np.sin(2 * np.pi * 3.6 * t + g.uniform(0, 6))
             + 6.0 * smooth_noise(N, 0.7, g))
    f0 = midi_to_hz(m0)
    ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200.0)) / SR
    env = np.clip(t / 0.9, 0, 1) ** 2 * np.where(t > dur, np.exp(-(t - dur) / 0.35), 1.0)
    env *= 1.0 + 0.18 * np.sin(np.pi * np.clip(t / dur, 0, 1))
    K = int(min(40, 3600.0 / f0))
    y = np.zeros(N)
    for k in range(1, K + 1):
        fk = k * f0
        a = k ** -0.8 * (np.exp(-((fk - 380.0) / 150.0) ** 2) + 0.6 * np.exp(-((fk - 820.0) / 220.0) ** 2)
                         + 0.06 * np.exp(-((fk - 2500.0) / 500.0) ** 2) + 0.02)
        y += a * np.sin(k * ph + g.uniform(0, 6.28))
    air = filt(g.standard_normal(N), [bq_bandpass(600.0, 0.8)]) * 0.04
    out = (y + air) * env * vel
    k2 = int(0.01 * SR)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.12 * out


def draw(dur: float, vel: float, g) -> np.ndarray:
    """The water drawing toward it: a noise band that brightens (a low band crossfading to a higher one) and swells
    to the downbeat, then stops; a few bubbles caught in the pull near its end. Stereo."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    w = (t / dur) ** 1.5
    env = (t / dur) ** 2.5
    k = int(0.03 * SR)
    env[-k:] *= np.linspace(1, 0, k)
    out = np.zeros((N, 2))
    for ch in range(2):
        lo = filt(g.standard_normal(N), [bq_bandpass(260.0, 0.7), bq_lowpass(700.0, 0.7)])
        hi = filt(g.standard_normal(N), [bq_bandpass(1300.0, 0.9)])
        out[:, ch] = (lo * (1 - w) + 0.7 * hi * w) * env
    for _ in range(4):
        b = bubble(float(g.uniform(1.5, 3.5)), 0.25, rise=0.15)
        s = int(float(g.uniform(0.45, 0.92)) * N)
        e = min(N - k, s + len(b))
        if e > s:
            out[s:e, int(g.integers(2))] += b[: e - s]
    return vel * out


_KNOCKS: dict = {}


def root_knock(leg: int, vel: float, variant: int) -> np.ndarray:
    """One leg planting: a struck, knuckled root (a short excitation through four wood modes tuned to that root)
    and a low thump of the mud under it. Cached per leg and variant, scaled by `vel`. Mono."""
    key = (leg, variant)
    if key not in _KNOCKS:
        f, _, _ = LEGS[leg]
        g = rng(SEED + 7000 + 31 * leg + variant)
        ir = V.body_ir(((f, 26, 1.0), (f * 2.37, 22, 0.6), (f * 4.1, 16, 0.35), (f * 6.3, 12, 0.18)),
                       SEED + 7100 + 31 * leg + variant, length=0.3, scale=0.5)
        nn = int(0.004 * SR)
        exc = filt(g.standard_normal(nn), [bq_lowpass(3200.0, 0.7)]) * np.exp(-np.arange(nn) / (0.001 * SR))
        x = fft_convolve(exc, ir)
        x /= np.abs(x).max() + 1e-9
        tt = np.arange(int(0.25 * SR)) / SR
        thump = np.sin(2 * np.pi * (f * 0.42) * tt) * np.exp(-tt / 0.06) * np.minimum(1.0, tt / 0.003)
        y = np.zeros(max(len(x), len(thump)))
        y[: len(x)] += x
        y[: len(thump)] += 0.6 * thump
        k = int(0.01 * SR)
        y[-k:] *= np.linspace(1, 0, k)
        _KNOCKS[key] = y
    return vel * _KNOCKS[key]


def splinters(seconds: float, density: float, g) -> np.ndarray:
    """Short woody cracks (the stump splintering, the roots tearing) scattered at `density` per second. Mono."""
    N = int(seconds * SR)
    out = np.zeros(N)
    tt = float(g.exponential(1.0 / density))
    while tt < seconds - 0.05:
        k = int(g.uniform(0.004, 0.018) * SR)
        pop = filt(g.standard_normal(k + 64), [bq_bandpass(float(g.uniform(700, 2600)), 1.4)])[:k]
        pop *= np.exp(-np.arange(k) / (0.3 * k)) * g.uniform(0.3, 1.0)
        s = int(tt * SR)
        out[s: s + k] += pop[: N - s]
        tt += float(g.exponential(1.0 / density))
    return out


def rising_water(seconds: float, g, end_fade: float = 0.04) -> np.ndarray:
    """The water climbing the roots: a noise band moving up (crossfaded bands 220 -> 1500 Hz) and swelling over
    `seconds`, with bubbles thickening as it rises; a short fade at its end. Stereo."""
    N = int(seconds * SR)
    t = np.arange(N) / SR
    u = t / seconds
    bands = (220.0, 480.0, 900.0, 1500.0)
    out = np.zeros((N, 2))
    for ch in range(2):
        acc = np.zeros(N)
        for i, fc in enumerate(bands):
            w = np.clip(1.0 - np.abs(u * (len(bands) - 1) - i), 0, 1)
            acc += w * filt(g.standard_normal(N), [bq_bandpass(fc, 1.1)])
        out[:, ch] = acc
    out *= (0.15 + 0.85 * u ** 2)[:, None]
    tb = 0.0
    while tb < seconds - 0.3:
        b = bubble(float(g.uniform(1.8, 5.0)), float(g.uniform(0.2, 0.5)), rise=0.12)
        s = int(tb * SR)
        e = min(N, s + len(b))
        out[s:e, int(g.integers(2))] += b[: e - s] * (0.3 + u[s])
        tb += float(g.exponential(1.0 / (2.0 + 14.0 * u[s])))
    k = int(end_fade * SR)
    out[-k:] *= np.linspace(1, 0, k)[:, None]
    return out


# --------------------------------------------------------------------------- #
# parts
# --------------------------------------------------------------------------- #
def add_pipe(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """The theme on the fen pipe, its shadow an octave below on a darker pipe."""
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, ee in bar:
            d = ee * E8
            if p is not None:
                v = vel * float(g.uniform(0.94, 1.04)) * (1.06 if ee >= 3 else 1.0)
                s = seed + int(round(pos * 1000))
                x = V.reed_pipe(n(p), d * 0.94, v, s, attack=0.04, sag_cents=30.0 if ee >= 5 else 10.0)
                mx.add("pipe", x, pos + float(g.normal(0, 0.004)), pan=0.08)
                y = V.reed_pipe(n(p) - 12, d * 0.94, 0.8 * v, s + 3, attack=0.05, sag_cents=40.0 if ee >= 5 else 14.0,
                                nasal=0.4)
                mx.add("pipe_low", y, pos + float(g.normal(0, 0.004)), pan=-0.12)
            pos += d


def add_flute(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
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
            x = breath_flute(n(p), d * 0.95 + 0.02, vel * float(g.uniform(0.95, 1.04)),
                             seed=seed + int(round(pos * 1000)), breath=0.55, scoop_cents=50.0 if first else 18.0,
                             vib_cents=11.0 if ee >= 6 else 4.0, vib_rate=5.2, swell=0.3 if ee >= 9 else 0.1,
                             attack=0.04, release=0.2, beta=0.62)
            mx.add("flute", x, pos - V.FLUTE_PRE + float(g.normal(0, 0.003)), pan=0.12)
            pos += d
            first = False


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch])
        loud = sec in ("A", "B", "A2")
        brk = sec == "D"
        # the dark pad
        third = THIRD[ch]
        x = pad_chord([root + 12, root + 19, root + 24, root + 24 + third], BAR * 0.96, 0.5,
                      seed=SEED + 200 + bar, voices=4, attack=0.9, release=1.2, width=0.7)
        mx.add("pad", x, t_of(bar) - 0.2)
        # the haul: long notes dragged down into pitch on the 1 and the 7, short ones between
        if not brk:
            for e, dur_e, off, v, drag in ((1, 2.6, 0, 0.9, 140.0), (4, 0.9, 12, 0.55, 0.0), (5, 0.9, 0, 0.6, 0.0),
                                           (7, 2.6, 0, 0.8, 100.0), (10, 1.4, 7, 0.6, 0.0), (12, 0.8, 12, 0.5, 0.0)):
                if bar == BARS and e == 12:
                    continue
                x = bass_note(root + off, dur_e * E8, v * float(g.uniform(0.93, 1.05)),
                              seed=SEED + 6000 + 13 * bar + e, mute=0.3 if drag else 0.45)
                if drag:
                    x = V.bend(x, drag, 0.09)
                mx.add("bass", x, t_of(bar, e) + 0.003)
        elif bar == 11:
            x = V.bend(bass_note(root, 2 * BAR - 0.2, 0.85, seed=SEED + 6900, mute=0.0), 220.0, 0.25)
            mx.add("bass", x, t_of(bar))
        # drums: every eighth (dum on the 1 and the 7, slaps on the 4 and the 10)
        if loud or sec == "I" or (bar == 12):
            for e in range(1, BAR_E + 1):
                if bar == 12 and e < 7:
                    continue
                if bar == BARS and e >= 7:
                    continue                                         # the fill takes over
                if e in (1, 7):
                    st, v = "dum", (0.9 if e == 1 else 0.75)
                elif e in (4, 10):
                    st, v = "slap", 0.66
                else:
                    st, v = ("tek" if e % 3 == 0 else "ghost"), 0.42
                if sec == "I" and st in ("tek", "ghost") and e % 3 != 0:
                    continue
                if bar == 12:
                    v *= 0.55 + 0.08 * (e - 7)
                mx.add("drums", frame_drum(st, v * float(g.uniform(0.9, 1.06)), variant=bar * 12 + e, seed=SEED + 3),
                       t_of(bar, e) + float(g.normal(0, 0.003)), pan=0.05 if st == "dum" else -0.15)
            if bar != 12:
                mx.add("drums", big_drum(0.95 if (bar - 3) % 4 == 0 else 0.82, variant=bar, seed=SEED + 4), t_of(bar))
                if bar != BARS:
                    mx.add("drums", big_drum(0.62, variant=bar + 1, seed=SEED + 4), t_of(bar, 7))
        elif bar == 11:
            mx.add("drums", big_drum(0.8, variant=bar, seed=SEED + 4), t_of(bar))
            for e in (1, 7):
                mx.add("drums", frame_drum("dum", 0.6, variant=e, seed=SEED + 3), t_of(bar, e))
        if bar == BARS:                                              # the fill: eighths 7-11, the 12th left empty
            for k, e in enumerate((7, 8, 9, 9.5, 10, 10.5, 11)):
                mx.add("drums", frame_drum("slap" if k % 2 else "dum", 0.55 + 0.06 * k, variant=k, seed=SEED + 6),
                       t_of(bar, e), pan=0.05)
            for e in (7, 9, 11):
                mx.add("drums", big_drum(0.6 + 0.08 * (e - 7) / 2, variant=e, seed=SEED + 4), t_of(bar, e))
        # gourds on the 6 and the 12
        if bar != 11:
            for e, p in ((6, "G2"), (12, "D2")):
                if bar == BARS and e == 12:
                    continue
                v = (0.75 if e == 6 else 0.62) * float(g.uniform(0.9, 1.06)) * (0.7 if brk else 1.0)
                mx.add("gourd", V.gourd(n(p), v, SEED + 900 + 12 * bar + e), t_of(bar, e) + float(g.normal(0, 0.004)),
                       pan=-0.3 if e == 6 else 0.3)
        # the draw: over the last dotted beat of every second bar (none into the seam), big into 3, 11 and 13
        if bar % 2 == 0 and bar != BARS:
            big = bar in (2, 10, 12)
            dur = (6 if bar == 12 else 3) * E8
            x = draw(dur, 1.0 if big else 0.55, rng(SEED + 4000 + bar))
            mx.add("draw", x, t_of(bar + 1) - dur)
        # drips from the roots
        for _ in range(int(g.integers(1, 3))):
            x = drip(float(g.uniform(0.3, 0.7)), radius_mm=float(g.uniform(1.8, 4.0)), seed=int(g.integers(1 << 30)))
            mx.add("drips", x, t_of(bar, float(g.uniform(1, 12))), pan=float(g.uniform(-0.8, 0.8)))
    # the moan: a falling semitone, three voices
    for start, (m0, m1) in ((1, ("Ab2", "G2")), (11, ("Eb3", "D3"))):
        for k, (det, pan, lvl) in enumerate(((0.0, -0.2, 1.0), (0.07, 0.25, 0.8), (-12.0, 0.0, 0.55))):
            x = moan(n(m0) + det, n(m1) + det, 2 * BAR - 0.6, lvl, SEED + 80 + 10 * start + k)
            mx.add("moan", x, t_of(start) + 0.15 * k, pan=pan)
    add_pipe(mx, THEME_A, 3, SEED + 100, 0.7)
    add_pipe(mx, FRAGMENT, 11, SEED + 150, 0.6)
    add_pipe(mx, THEME_B, 13, SEED + 200, 0.75)
    add_pipe(mx, THEME_A2, 17, SEED + 300, 0.75)


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch]) + 12
        loud = sec in ("A", "B", "A2")
        x = pad_chord([root, root + 7, root + 12], BAR - 0.05, 0.85, seed=SEED + 2000 + bar, voices=5,
                      spread_cents=12.0, attack=0.35, release=0.5, width=0.7)
        mx.add("strings", x, t_of(bar) - 0.03)
        # the walk: six legs a bar
        if bar != 11:
            for leg, (_, pan, e) in enumerate(LEGS):
                if bar == 12 and e < 7:
                    continue
                v = LEG_VEL[leg] * float(g.uniform(0.9, 1.06)) * (1.0 if loud else 0.8)
                mx.add("knock", root_knock(leg, v, bar % 2), t_of(bar, e) + float(g.normal(0, 0.004)), pan=pan)
        mx.add("splinter", splinters(BAR, 3.0 if loud else 1.2, rng(SEED + 3500 + bar)), t_of(bar), pan=-0.5)
        mx.add("splinter", splinters(BAR, 3.0 if loud else 1.2, rng(SEED + 3700 + bar)), t_of(bar), pan=0.5)
        # the second drums: big drum on the 4 and the 10, slaps on the 6 and the 12
        if loud or sec == "I":
            for e, v in ((4, 0.62), (10, 0.62)):
                mx.add("drums2", big_drum(v, variant=bar + e, seed=SEED + 7), t_of(bar, e))
            for e in (6, 12):
                if bar == BARS and e == 12:
                    continue
                mx.add("drums2", frame_drum("slap", 0.6 * float(g.uniform(0.9, 1.06)), variant=bar * 2 + e,
                                            seed=SEED + 8), t_of(bar, e), pan=0.2)
    # the rising water over each phrase; the last ends before bar 20's empty eighth
    for start, bars, fade in ((3, 4, 0.04), (7, 4, 0.04), (11, 2, 0.04), (13, 4, 0.04), (17, 4, None)):
        dur = bars * BAR - (0 if fade else 2 * E8)
        x = rising_water(dur, rng(SEED + 5000 + start), end_fade=fade or 0.25)
        mx.add("water", x, t_of(start))
    for start in (3, 11, 13, 17):
        sub_t = np.arange(int(2.0 * SR)) / SR
        sub = np.sin(2 * np.pi * (36.0 + 14.0 * np.exp(-sub_t / 0.4)) * sub_t) * np.exp(-sub_t / 0.8)
        sub *= np.minimum(1.0, sub_t / 0.01)
        mx.add("sub", sub, t_of(start), pan=0.0)
    add_flute(mx, COUNTER_A, 3, SEED + 500, 0.9)
    add_flute(mx, COUNTER_B, 13, SEED + 600, 0.92)
    add_flute(mx, COUNTER_A2, 17, SEED + 700, 0.94)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "pipe": 0.0, "pipe_low": -0.6, "bass": 5.7, "drums": 2.8, "gourd": -1.7, "draw": -6.4, "moan": 3.4, "pad": 8.2,
    "drips": 6.7,
    "flute": 3.1, "strings": 5.4, "knock": -0.1, "splinter": 0.8, "water": -13.9, "drums2": 3.7, "sub": -9.5,
}
## The plan (LU relative to the stem-1 lead, the fen pipe, by each bus's integrated loudness over the loop).
PLAN = {
    "pipe": 0.0, "pipe_low": -8.0, "bass": -5.0, "drums": -4.0, "gourd": -10.0, "draw": -11.0, "moan": -5.0,
    "pad": -12.0, "drips": -17.0,
    "flute": -1.0, "strings": -9.0, "knock": -7.0, "splinter": -17.0, "water": -12.0, "drums2": -7.0, "sub": -11.0,
}
LEAD = "pipe"


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("pipe", G["pipe"], send=0.28, process=lambda x: filt(x, [bq_highpass(180, 0.7), bq_peak(1100, 1.5, 1.0),
                                                                         bq_lowpass(6500, 0.7)]))
        mx.bus("pipe_low", G["pipe_low"], send=0.25, process=lambda x: filt(x, [bq_highpass(90, 0.7),
                                                                                 bq_lowpass(2400, 0.7)]))
        mx.bus("bass", G["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(90, 2.0, 0.9),
                                                                        bq_lowpass(2500, 0.7)]))
        mx.bus("drums", G["drums"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7),
                                                                           bq_lowpass(5000, 0.7)]))
        mx.bus("gourd", G["gourd"], send=0.2, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
        mx.bus("draw", G["draw"], send=0.2)
        mx.bus("moan", G["moan"], send=0.45, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(2400, 0.7)]))
        mx.bus("pad", G["pad"], send=0.35, process=lambda x: string_body(x, cutoff=700.0))
        mx.bus("drips", G["drips"], send=0.5)
    else:
        mx.bus("flute", G["flute"], send=0.22, process=lambda x: filt(x, [bq_highpass(250, 0.7),
                                                                           bq_peak(2400, 2.0, 1.0)]))
        mx.bus("strings", G["strings"], send=0.3, process=lambda x: string_body(x, cutoff=1300.0))
        mx.bus("knock", G["knock"], send=0.15, process=lambda x: filt(x, [bq_highpass(60, 0.7)]))
        mx.bus("splinter", G["splinter"], send=0.15, process=lambda x: filt(x, [bq_highpass(500, 0.7)]))
        mx.bus("water", G["water"], send=0.2, process=lambda x: filt(x, [bq_highpass(120, 0.7)]))
        mx.bus("drums2", G["drums2"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7)]))
        mx.bus("sub", G["sub"], send=0.0, process=lambda x: filt(x, [bq_lowpass(120, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        hall = ModFDNReverb(rt60=2.4, rt60_high=0.8, predelay=0.03, size=1.1, mod_depth=8.0, mod_rate=0.35,
                            early_level=0.25, lowcut=110.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
        del mx
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    # The loop is periodic, so the file may start anywhere; LEAD_IN_E > 0 starts it before bar 1's downbeat.
    lead_in = int(round(LEAD_IN_E * E8 * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    # one limiter gain curve for both stems, from the full stack (wrap-aware), iterated to the target
    for _ in range(4):
        f = full * gain
        lg = limit_gain(np.concatenate([f[-ctx:], f, f[:ctx]]), -2.0)[ctx: ctx + L]
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    extra = {"stems_of": "mangrove_drowner", "loop_bars": BARS, "meter": "12/8 (bpm counts dotted quarters)",
             "downbeat_offset_s": lead_in / SR}
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1])
    m1 = measure(stems[0])
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["stem1_lufs"] = m1["integrated_lufs"]
        stats["limited_fraction"] = float((lg < 0.999).mean())
    if verbose:
        print(f"mangrove_drowner: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP "
              f"{m['true_peak_dbtp']:.2f} dBTP; stem 1 alone {m1['integrated_lufs']:.2f} LUFS; limited "
              f"{(lg < 0.999).mean() * 100:.2f} %, max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        lead = bus_lufs[LEAD]
        print("  buses (LU vs the pipe)", {k: round(v - lead, 1) for k, v in bus_lufs.items()})
        print("  gains for the plan", {k: round(GAINS[k] + PLAN[k] - (v - lead), 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
