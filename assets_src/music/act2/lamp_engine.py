"""`lamp_engine`: the Lamp Engine boss (M3-AUD-844; act_outline Ch11, docs/kb/art/creatures/act2/lamp_engine.md):
two synchronized stems, a 74.5 s loop.

Original composition for this project (SPEC §2, §9). Original-material check: the theme, the glass's counter-line,
the three rings' figures, the lift and every part below were written for this fight. The theme's B phrase opens with
the bound call from Lowlight's final (lowlight.py's CALL_BOUND: C-D-Eb, the Kirru call pulled into C minor, ours),
so the guardian belongs to its temple. None of it is taken from any melody we know; the style evoked (a hard-blown
low flute over a clockwork of struck metal and drums) is a colour, not a quotation. Nothing is borrowed from another
cue but Lowlight's engine stroke and glass (act2_voices.engine_thud, act2_voices.glass).

The brief: Lowlight, the engine hall below the sanctum, half under water: a Lit Age machine for keeping light, a
chapel-sized lamp-stand on four jointed legs, three gimballed brass rings of four salt-glass lamps (twelve) turning
against each other round one core, two long trimming arms with scissor heads. Each lamp holds a bound dead light,
steady and unpulsing. It isn't cruel; it keeps. Phase 2 `opened` (50% HP): the rings fold back like petals and the
core shows, a cracked salt-glass globe with the brightest bound light in it. Releasing the core lets a small lift of
motes rise (a foreshadowing). So stem 1 is the machine running (it keeps Lowlight's stroke, now at fighting speed)
and stem 2 is what it holds: the dead, and their light. Its light never swells or beats: every held tone in this cue
is steady (no tremolo, no detuned twins), so nothing in it reads as breathing.

C minor (Aeolian: C D Eb F G Ab Bb; the G chord takes B natural). 4/4 at 116 BPM, twice Lowlight's 58: the engine's
stroke falls on the 1 and the 3, Lowlight's beat exactly (a bar is 2.069 s), 36 bars. The rings turn against the bar:
ring 1 in dotted eighths (its four lamps come round every 12 sixteenths), ring 2 in quarters (16), ring 3 in dotted
quarters (24), so all three line up again only every three bars; the drums and the bass push the same 3+3+2.

**Stem 1** (`lamp_engine_p1.ogg`, the Housing; plays from the start):
* the theme on a hard-blown low breath flute, its long notes struck on a brass kettle gong (A: bars 5-12, B: 13-20,
  the theme's first bar alone in the breakdown, A': 25-32; the bound call again in 33-34);
* the escapement: a dry brass tick on every eighth (tick and tock), the engine's stroke (act2_voices.engine_thud) on
  the 1 and the 3;
* ring 1: a hand-damped metallophone on the chord's four lamps in dotted eighths;
* a fingered bass in driving eighths, accented 3+3+2; frame drums and a big drum on the 3+3+2;
* the trim: the shears' snip (two blades crossing and a ring of steel) on the last eighth of every second bar,
  into the downbeat;
* a dark low string pad on the chords, and the twelve lamps: a steady, very soft tone (C5, G5, Eb6).

**Stem 2** (`lamp_engine_p2.ogg`, the Core; the game fades it in when the housing opens):
* the glass harmonica (act2_voices.glass), a long held counter-line over A, B and A', a held G5 through the
  breakdown, and the lift: the core's release, a rising line G4-B4-C5-D5 | Eb5-F5-G5 in bars 35-36, doubled softly on
  metallophone, the last thing stem 2 plays before the loop turns;
* the bound dead: a low hummed congregation (synth.voice.hum_ensemble) under A, B and A';
* rings 2 and 3, freed: a high soft metallophone in quarters and low kettle gongs in dotted quarters;
* the escapement racing: ticks on the off-sixteenths; a second drum line (big drum on the and of 3, slaps on 2 and
  4); low strings (root, fifth, octave); a sub-bass surge into each section; the core's own light, a steady high
  tone (C6, G6) with a faint cracked partial.

Form (bars): 1-4 the machine starts (engine, ticks, ring, bass; the drums at half until bar 3) | 5-12 A | 13-20 B |
21-24 breakdown (Cm Ab Fm G: the engine, the ticks, ring 1, the pad, the theme's first bar; the glass holds; the
drums build from bar 24's third beat) | 25-32 A' | 33-36 the turn (Ab Bb G G: the bound call, then stem 2's lift;
a drum fill in bar 36, whose last eighth is empty), and G leads to bar 1's C minor.

Mastering (as cinder_matron.py): both stems share one gain (the full stack at -16 LUFS) and one limiter gain curve
computed on the full stack (synth.mixer.limit_gain), so stem 1 + stem 2 is exactly the limited mix. Stem 2 is
trimmed so the stack sits about +2 LU over stem 1 alone. Loop: LOOPSTART = 0 on both; equal lengths. The files start
half an eighth before bar 1's downbeat (the sidecars' `downbeat_offset_s`), so the wrap seam falls in bar 36's last,
empty eighth. Vorbis q3.

Render:  python3 assets_src/music/act2/lamp_engine.py   (or tools/audio/render_all.py --act2 --only
act2/lamp_engine)
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
                       midi_to_hz, rng)
from synth.electric import bass_note  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(MUSIC, "act2_voices.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music", "act2")
OUT = os.path.join(OUT_DIR, "lamp_engine_p1.ogg")
OUT2 = os.path.join(OUT_DIR, "lamp_engine_p2.ogg")
SEED = 20261845
TARGET_LUFS = -16.0
BPM = 116.0                          # quarters (twice Lowlight's 58)
BEAT = 60.0 / BPM
E8 = BEAT / 2                        # one eighth, 0.259 s
BAR_E = 8                            # 4/4 in eighths
BAR = BAR_E * E8
BARS = 36
LOOP_S = BARS * BAR
QUALITY = 3.0
## the file starts half an eighth before bar 1's downbeat, so the wrap seam falls in bar 36's last (empty) eighth
LEAD_IN_E = 0.5
## Stem 2's trim at mastering: the Core lifts the stack about 2 LU over stem 1 alone (render prints both).
STEM2_GAIN_DB = 0.0

CHORDS = (["Cm", "Cm", "Ab", "G"]
          + ["Cm", "Cm", "Ab", "Bb", "Cm", "Fm", "G", "G"]
          + ["Ab", "Eb", "Fm", "Cm", "Ab", "Bb", "G", "G"]
          + ["Cm", "Ab", "Fm", "G"]
          + ["Cm", "Cm", "Ab", "Bb", "Cm", "Fm", "G", "G"]
          + ["Ab", "Bb", "G", "G"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["D"] * 4 + ["A2"] * 8 + ["T"] * 4
ROOT_MIDI = {"Cm": "C2", "Ab": "Ab1", "Bb": "Bb1", "G": "G1", "Fm": "F1", "Eb": "Eb2"}
THIRD = {"Cm": 3, "Fm": 3, "Ab": 4, "Bb": 4, "Eb": 4, "G": 4}
LOUD = ("A", "B", "A2", "T")

## the theme (pitch | None, eighths); each bar is 8 eighths
THEME_A = [
    [("C4", 3), ("Eb4", 1), ("G4", 2), ("F4", 1), ("Eb4", 1)],
    [("D4", 2), ("Eb4", 1), ("C4", 5)],
    [("Ab4", 3), ("G4", 1), ("F4", 2), ("Eb4", 2)],
    [("F4", 2), ("G4", 2), ("Bb4", 4)],
    [("C5", 3), ("Bb4", 1), ("G4", 2), ("Ab4", 2)],
    [("F4", 3), ("Eb4", 1), ("D4", 2), ("C4", 2)],
    [("B3", 2), ("D4", 2), ("G4", 4)],
    [("G4", 6), (None, 2)],
]
## B opens on Lowlight's bound call (C-D-Eb), here in eighths
THEME_B = [
    [("C5", 2), ("D5", 1), ("Eb5", 5)],
    [("G5", 3), ("F5", 1), ("Eb5", 2), ("Bb4", 2)],
    [("Ab4", 2), ("C5", 2), ("F5", 4)],
    [("Eb5", 3), ("D5", 1), ("C5", 4)],
    [("C5", 2), ("D5", 1), ("Eb5", 3), ("F5", 2)],
    [("G5", 2), ("F5", 2), ("D5", 4)],
    [("D5", 3), ("Eb5", 1), ("D5", 2), ("B4", 2)],
    [("G4", 6), (None, 2)],
]
THEME_A2 = THEME_A[:6] + [[("B3", 2), ("D4", 2), ("F4", 2), ("Ab4", 2)], [("G4", 6), (None, 2)]]
FRAGMENT = [[("C4", 3), ("Eb4", 1), ("G4", 4)], [(None, 8)]]                # breakdown: the theme's first bar, alone
CALL = [[("C5", 2), ("D5", 1), ("Eb5", 5)], [("F5", 3), ("Eb5", 1), ("D5", 4)]]   # the turn: the bound call
## stem 2: the glass (long and steady)
COUNTER_A = [[("G5", 16)], [], [("Eb5", 8)], [("F5", 8)], [("G5", 8)], [("Ab5", 8)], [("G5", 14), (None, 2)], []]
COUNTER_B = [[("Eb6", 8)], [("Bb5", 8)], [("C6", 8)], [("G5", 8)], [("Ab5", 8)], [("F5", 8)], [("D5", 8)],
             [("B4", 6), (None, 2)]]
GLASS_PEDAL = [[("G5", 30), (None, 2)], [], [], []]
## the lift: the core's release, rising, the last thing stem 2 plays
LIFT = [[("G4", 2), ("B4", 2), ("C5", 2), ("D5", 2)], [("Eb5", 2), ("F5", 2), ("G5", 3), (None, 1)]]


def t_of(bar: int, e: float = 1.0) -> float:
    """Seconds from the loop start to eighth `e` (1-based) of `bar`."""
    return (bar - 1) * BAR + (e - 1) * E8


# --------------------------------------------------------------------------- #
# voices written for this cue
# --------------------------------------------------------------------------- #
_TICKS: dict = {}


def tick(tock: bool, vel: float, variant: int) -> np.ndarray:
    """The escapement: a dry brass tick (a pallet striking a toothed wheel): a click through three short metal
    modes, the tock pitched lower and a touch longer. Cached per kind and variant, scaled by `vel`. Mono."""
    key = (tock, variant % 6)
    if key not in _TICKS:
        g = rng(SEED + 9000 + 17 * key[1] + (5 if tock else 0))
        base = (1650.0 if tock else 2900.0) * float(g.uniform(0.98, 1.02))
        ir = V.body_ir(((base, 30, 1.0), (base * 1.63, 26, 0.6), (base * 2.41, 20, 0.35)),
                       SEED + 9100 + 17 * key[1] + (5 if tock else 0), length=0.12, scale=0.6)
        nn = int(0.0015 * SR)
        exc = filt(g.standard_normal(nn + 32), [bq_highpass(1200.0, 0.7)])[:nn] * np.linspace(1, 0, nn)
        x = fft_convolve(exc, ir)
        x /= np.abs(x).max() + 1e-9
        k = int(0.008 * SR)
        x[-k:] *= np.linspace(1, 0, k)
        _TICKS[key] = x
    return vel * _TICKS[key]


def snip(vel: float, g) -> np.ndarray:
    """The trim: two blades crossing (a quick rising scrape of steel, then a shorter second one) and the shears
    ringing a moment after they close. Mono."""
    N = int(0.5 * SR)
    t = np.arange(N) / SR
    out = np.zeros(N)
    for start, length, lo, hi, a in ((0.0, 0.07, 2800.0, 5200.0, 1.0), (0.085, 0.04, 3600.0, 6400.0, 0.7)):
        s, k = int(start * SR), int(length * SR)
        x = g.standard_normal(k)
        u = np.linspace(0, 1, k)
        # the scrape: a band sweeping up, in four crossfaded slices
        y = np.zeros(k)
        for i in range(4):
            fc = lo + (hi - lo) * (i + 0.5) / 4
            w = np.clip(1.0 - np.abs(u * 3 - i), 0, 1)
            y += w * filt(x, [bq_bandpass(fc, 3.0)])
        y *= np.sin(np.pi * u) ** 0.7
        out[s: s + k] += a * y
    s = int(0.12 * SR)
    tr = t[: N - s]
    f = float(g.uniform(4100.0, 4300.0))
    ring = (np.sin(2 * np.pi * f * tr) + 0.4 * np.sin(2 * np.pi * f * 1.52 * tr)) * np.exp(-tr / 0.09)
    out[s:] += 0.35 * ring * np.minimum(1.0, tr / 0.002)
    k = int(0.01 * SR)
    out[-k:] *= np.linspace(1, 0, k)
    return vel * out / (np.abs(out).max() + 1e-9)


def steady_light(pitches: list[tuple[str, float]], seed: int, crack: float = 0.0) -> np.ndarray:
    """A bound light: a few pure tones at constant level, each snapped to whole cycles per loop, so it neither
    swells, beats nor seams (no detuned twins); each tone sits at its own place in the stereo field. `crack` adds a
    faint inharmonic partial over the top one (the cracked core). Exactly one loop long, stereo."""
    g = rng(seed)
    N = int(round(LOOP_S * SR))
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    tones = [(midi_to_hz(n(p)), lvl) for p, lvl in pitches]
    if crack > 0:
        tones.append((tones[-1][0] * 2.76, crack))
    for i, (f, lvl) in enumerate(tones):
        pan = -0.5 + i / max(1, len(tones) - 1)
        s = lvl * (np.sin(2 * np.pi * V.snap(f, LOOP_S) * t + g.uniform(0, 6.28))
                   + 0.12 * np.sin(2 * np.pi * V.snap(2 * f, LOOP_S) * t + g.uniform(0, 6.28)))
        out[:, 0] += s * np.sqrt(0.5 * (1 - pan))
        out[:, 1] += s * np.sqrt(0.5 * (1 + pan))
    return 0.05 * out


def ring_notes(ch: str, ring: int) -> list[float]:
    """The four lamps of ring `ring` (1-3) on chord `ch`, in the order they come round."""
    r = n(ROOT_MIDI[ch])
    th = THIRD[ch]
    if ring == 1:
        return [r + 36, r + 36 + 7, r + 36 + th, r + 48]
    if ring == 2:
        return [r + 48 + 7, r + 60, r + 48 + th + 12, r + 48 + 7 + 12]
    return [r + 24, r + 31, r + 36, r + 31]


# --------------------------------------------------------------------------- #
# parts
# --------------------------------------------------------------------------- #
def add_flute(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """The theme on a hard-blown low flute; its notes of a quarter or longer struck on a brass kettle gong."""
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
            s = seed + int(round(pos * 1000))
            x = breath_flute(n(p), d * 0.93 + 0.02, vel * float(g.uniform(0.95, 1.04)), seed=s, breath=0.6,
                             scoop_cents=40.0 if first else 12.0, vib_cents=9.0 if ee >= 4 else 3.0, vib_rate=5.4,
                             swell=0.2 if ee >= 5 else 0.0, attack=0.025, release=0.14, beta=0.68)
            mx.add("flute", x, pos - V.FLUTE_PRE + float(g.normal(0, 0.003)), pan=0.06)
            if ee >= 2:
                y = kettle_gong(n(p), 0.7 * vel * float(g.uniform(0.94, 1.04)), seed=s + 5, t60=1.2 + 0.2 * ee,
                                damp_at=d + 0.1)
                mx.add("gong", y, pos + float(g.normal(0, 0.002)), pan=-0.12)
            pos += d
            first = False


def add_glass(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, bus: str = "glass",
              metal: bool = False) -> None:
    """The glass (steady held notes); `metal` doubles each note softly on a metallophone (the lift)."""
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, ee in bar:
            d = ee * E8
            if p is not None:
                s = seed + int(round(pos * 1000))
                mx.add(bus, V.glass(n(p), d * 0.97, vel, s), pos - V.GLASS_PRE, pan=0.15)
                if metal:
                    y = metallophone_note(n(p) + 12, 0.5 * vel, seed=s + 3, decay=2.2, hardness=0.35, ombak_hz=0.0,
                                          pair=False)
                    mx.add("lift_metal", y, pos + float(g.normal(0, 0.002)), pan=-0.2)
            pos += d


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch])
        loud = sec in LOUD
        brk = sec == "D"
        last = bar == BARS
        # the dark pad
        x = pad_chord([root + 12, root + 19, root + 24, root + 24 + THIRD[ch]], BAR * 0.96, 0.5,
                      seed=SEED + 200 + bar, voices=4, attack=0.6, release=0.9, width=0.7)
        mx.add("pad", x, t_of(bar) - 0.1)
        # the escapement: tick and tock on every eighth, the engine's stroke on the 1 and the 3
        for e in range(1, BAR_E + 1):
            if last and e == 8:
                continue
            v = (0.95 if e in (1, 5) else 0.7 if e in (3, 7) else 0.5) * float(g.uniform(0.92, 1.05))
            mx.add("tick", tick(e % 2 == 0, v, bar * 8 + e), t_of(bar, e) + float(g.normal(0, 0.0015)),
                   pan=0.35 if e % 2 else -0.3)
        for e, v in ((1, 0.95), (5, 0.8)):
            mx.add("engine", V.engine_thud(g, v * float(g.uniform(0.94, 1.04))), t_of(bar, e), pan=-0.05)
        # ring 1: the chord's four lamps in dotted eighths (a 12-sixteenth cycle against the bar)
        lamps = ring_notes(ch, 1)
        for s16 in range(16):
            k = (bar - 1) * 16 + s16
            if k % 3 or (last and s16 >= 12):
                continue
            v = (0.5 if s16 in (0, 6, 12) else 0.4) * float(g.uniform(0.92, 1.05)) * (0.75 if brk else 1.0)
            y = metallophone_note(lamps[(k // 3) % 4], v, seed=SEED + 300 + k, decay=1.6, hardness=0.7, ombak_hz=5.0,
                                  damp_at=0.3)
            mx.add("ring", y, t_of(bar, 1 + s16 / 2) + float(g.normal(0, 0.002)), pan=-0.3 + 0.2 * ((k // 3) % 4))
        # the bass: driving eighths, accented 3+3+2 (in the breakdown it holds the root)
        if not brk:
            for e, dur_e, off, v in ((1, 1.5, 0, 0.9), (2, 0.8, 0, 0.5), (3, 0.8, 12, 0.55), (4, 1.4, 0, 0.8),
                                     (5, 0.8, 0, 0.5), (6, 0.8, 12, 0.55), (7, 1.0, 7, 0.75), (8, 0.8, 12, 0.5)):
                if last and e == 8:
                    continue
                if sec == "I" and bar <= 2 and e in (2, 5, 8):
                    continue
                x = bass_note(root + off, dur_e * E8, v * float(g.uniform(0.93, 1.05)),
                              seed=SEED + 6000 + 11 * bar + e, mute=0.4)
                mx.add("bass", x, t_of(bar, e) + 0.003)
        elif bar in (21, 23):
            mx.add("bass", bass_note(root, 2 * BAR - 0.15, 0.8, seed=SEED + 6900 + bar, mute=0.0), t_of(bar))
        # drums: frame drums on every eighth (dum on the 3+3+2), the big drum on the groups
        if not brk:
            for e in range(1, BAR_E + 1):
                if last and e >= 5:
                    continue                                          # the fill takes over
                if e in (1, 4, 7):
                    st, v = "dum", (0.9 if e == 1 else 0.75)
                elif e in (3, 5):
                    st, v = "slap", 0.64
                else:
                    st, v = ("tek" if e % 2 == 0 else "ghost"), 0.42
                if sec == "I" and bar <= 2 and st not in ("dum",):
                    continue
                mx.add("drums", frame_drum(st, v * float(g.uniform(0.9, 1.06)), variant=bar * 8 + e, seed=SEED + 3),
                       t_of(bar, e) + float(g.normal(0, 0.003)), pan=0.05 if st == "dum" else -0.15)
            mx.add("drums", big_drum(0.95 if bar in (5, 13, 25, 33) else 0.82, variant=bar, seed=SEED + 4), t_of(bar))
            if loud and not last:
                mx.add("drums", big_drum(0.6, variant=bar + 1, seed=SEED + 4), t_of(bar, 4))
                mx.add("drums", big_drum(0.66, variant=bar + 2, seed=SEED + 4), t_of(bar, 7))
        else:
            mx.add("drums", big_drum(0.7, variant=bar, seed=SEED + 4), t_of(bar))
            if bar == 24:                                              # the build: sixteenths from beat 3
                for k, e in enumerate((5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5)):
                    mx.add("drums", frame_drum("dum" if k % 2 == 0 else "slap", 0.45 + 0.06 * k, variant=k,
                                               seed=SEED + 6), t_of(bar, e), pan=0.05)
        if last:                                                       # the fill: eighths 5-7, the 8th left empty
            for k, e in enumerate((5, 5.5, 6, 6.5, 7, 7.5)):
                mx.add("drums", frame_drum("slap" if k % 2 else "dum", 0.55 + 0.07 * k, variant=k, seed=SEED + 6),
                       t_of(bar, e), pan=0.05)
            for e in (5, 6, 7):
                mx.add("drums", big_drum(0.6 + 0.1 * (e - 5), variant=e, seed=SEED + 4), t_of(bar, e))
        # the trim: the shears snip into the next downbeat every second bar (none into the seam)
        if bar % 2 == 0 and not last and (loud or bar in (2, 4, 22)):
            mx.add("shears", snip(0.9 if bar in (4, 12, 20, 32) else 0.7, rng(SEED + 4000 + bar)), t_of(bar, 8),
                   pan=0.45 if bar % 4 else -0.45)
    mx.add("lamps", steady_light([("C5", 1.0), ("G5", 0.7), ("Eb6", 0.45)], SEED + 50), 0.0)
    add_flute(mx, THEME_A, 5, SEED + 100, 0.82)
    add_flute(mx, THEME_B, 13, SEED + 200, 0.86)
    add_flute(mx, FRAGMENT, 21, SEED + 250, 0.7)
    add_flute(mx, THEME_A2, 25, SEED + 300, 0.86)
    add_flute(mx, CALL, 33, SEED + 350, 0.8)


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch]) + 12
        loud = sec in LOUD
        brk = sec == "D"
        last = bar == BARS
        x = pad_chord([root, root + 7, root + 12], BAR - 0.05, 0.85, seed=SEED + 2000 + bar, voices=5,
                      spread_cents=10.0, attack=0.3, release=0.5, width=0.7)
        mx.add("strings", x, t_of(bar) - 0.03)
        # the escapement racing: ticks on the off-sixteenths
        for e in range(1, BAR_E + 1):
            if (last and e >= 8) or (brk and e % 2 == 0):
                continue
            mx.add("tick2", tick(False, 0.5 * float(g.uniform(0.85, 1.05)), bar * 8 + e + 3),
                   t_of(bar, e + 0.5) + float(g.normal(0, 0.0015)), pan=-0.5 if e % 2 else 0.5)
        # rings 2 (high, quarters) and 3 (low kettle gongs, dotted quarters), freed
        hi, lo = ring_notes(ch, 2), ring_notes(ch, 3)
        for s16 in range(16):
            k = (bar - 1) * 16 + s16
            if last and s16 >= 12:
                continue
            if k % 4 == 0:
                y = metallophone_note(hi[(k // 4) % 4], 0.38 * float(g.uniform(0.9, 1.05)), seed=SEED + 2500 + k,
                                      decay=2.4, hardness=0.45, ombak_hz=0.0, pair=False, damp_at=0.5)
                mx.add("ring2", y, t_of(bar, 1 + s16 / 2), pan=0.55 - 0.3 * ((k // 4) % 4))
            if k % 6 == 0 and not brk:
                y = kettle_gong(lo[(k // 6) % 4], 0.5 * float(g.uniform(0.9, 1.05)), seed=SEED + 2700 + k, t60=1.4,
                                damp_at=0.6)
                mx.add("ring3", y, t_of(bar, 1 + s16 / 2), pan=-0.35)
        # the second drums: the big drum on the and of 3, slaps on 2 and 4
        if loud or (sec == "I" and bar >= 3):
            if not last:
                mx.add("drums2", big_drum(0.62, variant=bar + 3, seed=SEED + 7), t_of(bar, 6))
            for e in (3, 7):
                if last and e == 7:
                    continue
                mx.add("drums2", frame_drum("slap", 0.6 * float(g.uniform(0.9, 1.06)), variant=bar * 2 + e,
                                            seed=SEED + 8), t_of(bar, e), pan=0.2)
    # the bound dead: a low hummed congregation under A, B and A'
    for start, line in ((5, [("C3", 2), ("Ab2", 2), ("C3", 2), ("G2", 2)]),
                        (13, [("Ab2", 2), ("F2", 2), ("Ab2", 2), ("G2", 2)]),
                        (25, [("C3", 2), ("Ab2", 2), ("C3", 2), ("G2", 2)])):
        x = hum_ensemble([(n(p), b * BAR) for p, b in line], voices=10, seed=SEED + 70 + start, register="low",
                         spread=0.8)
        env = np.ones(len(x))
        k = int(1.0 * SR)
        env[:k] = np.linspace(0, 1, k) ** 2
        env[-k:] *= np.linspace(1, 0, k) ** 2
        mx.add("dead", x * env[:, None], t_of(start) - 0.1)
    for start in (5, 13, 25, 33):
        sub_t = np.arange(int(1.6 * SR)) / SR
        sub = np.sin(2 * np.pi * (38.0 + 15.0 * np.exp(-sub_t / 0.35)) * sub_t) * np.exp(-sub_t / 0.7)
        sub *= np.minimum(1.0, sub_t / 0.01)
        mx.add("sub", sub, t_of(start), pan=0.0)
    mx.add("core", steady_light([("C6", 1.0), ("G6", 0.55)], SEED + 60, crack=0.12), 0.0)
    add_glass(mx, COUNTER_A, 5, SEED + 500, 0.75)
    add_glass(mx, COUNTER_B, 13, SEED + 600, 0.75)
    add_glass(mx, GLASS_PEDAL, 21, SEED + 650, 0.6)
    add_glass(mx, COUNTER_A, 25, SEED + 700, 0.78)
    add_glass(mx, LIFT, 35, SEED + 800, 0.8, metal=True)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "flute": 0.0, "gong": -5.9, "tick": -5.0, "engine": -9.8, "ring": -0.2, "bass": -3.2, "drums": -5.0,
    "shears": -18.4, "pad": 1.9, "lamps": -11.7,
    "glass": -6.3, "lift_metal": -8.7, "dead": 2.4, "tick2": -3.3, "ring2": -2.2, "ring3": -5.5, "strings": -0.4,
    "drums2": -2.1, "sub": -15.9, "core": -11.5,
}
## The plan (LU relative to the stem-1 lead, the flute, by each bus's integrated loudness over the loop).
PLAN = {
    "flute": 0.0, "gong": -8.0, "tick": -11.0, "engine": -6.0, "ring": -9.0, "bass": -5.0, "drums": -4.0,
    "shears": -15.0, "pad": -12.0, "lamps": -18.0,
    "glass": -2.0, "lift_metal": -20.0, "dead": -7.0, "tick2": -13.0, "ring2": -11.0, "ring3": -10.0,
    "strings": -9.0, "drums2": -7.0, "sub": -11.0, "core": -18.0,
}
LEAD = "flute"


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("flute", G["flute"], send=0.25, process=lambda x: filt(x, [bq_highpass(200, 0.7),
                                                                           bq_peak(1500, 1.5, 1.0)]))
        mx.bus("gong", G["gong"], send=0.3, process=lambda x: filt(x, [bq_highpass(150, 0.7)]))
        mx.bus("tick", G["tick"], send=0.12, process=lambda x: filt(x, [bq_highpass(800, 0.7)]))
        mx.bus("engine", G["engine"], send=0.25, process=lambda x: filt(x, [bq_highpass(30, 0.7),
                                                                             bq_lowpass(1200, 0.7)]))
        mx.bus("ring", G["ring"], send=0.25, process=lambda x: filt(x, [bq_highpass(250, 0.7)]))
        mx.bus("bass", G["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(95, 2.0, 0.9),
                                                                        bq_lowpass(2800, 0.7)]))
        mx.bus("drums", G["drums"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7),
                                                                           bq_peak(3500, 1.5, 0.8)]))
        mx.bus("shears", G["shears"], send=0.3, process=lambda x: filt(x, [bq_highpass(1500, 0.7)]))
        mx.bus("pad", G["pad"], send=0.35, process=lambda x: string_body(x, cutoff=800.0))
        mx.bus("lamps", G["lamps"], send=0.2)
    else:
        mx.bus("glass", G["glass"], send=0.45, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
        mx.bus("lift_metal", G["lift_metal"], send=0.45)
        mx.bus("dead", G["dead"], send=0.5, process=lambda x: filt(x, [bq_highpass(70, 0.7), bq_lowpass(2600, 0.7)]))
        mx.bus("tick2", G["tick2"], send=0.12, process=lambda x: filt(x, [bq_highpass(1000, 0.7)]))
        mx.bus("ring2", G["ring2"], send=0.35)
        mx.bus("ring3", G["ring3"], send=0.25, process=lambda x: filt(x, [bq_highpass(90, 0.7)]))
        mx.bus("strings", G["strings"], send=0.3, process=lambda x: string_body(x, cutoff=1300.0))
        mx.bus("drums2", G["drums2"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7)]))
        mx.bus("sub", G["sub"], send=0.0, process=lambda x: filt(x, [bq_lowpass(120, 0.7)]))
        mx.bus("core", G["core"], send=0.3)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        hall = ModFDNReverb(rt60=2.6, rt60_high=0.9, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.3,
                            early_level=0.3, lowcut=100.0, seed=SEED % 9973)
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
    extra = {"stems_of": "lamp_engine", "loop_bars": BARS, "meter": "4/4", "downbeat_offset_s": lead_in / SR}
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
        print(f"lamp_engine: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP "
              f"{m['true_peak_dbtp']:.2f} dBTP; stem 1 alone {m1['integrated_lufs']:.2f} LUFS; limited "
              f"{(lg < 0.999).mean() * 100:.2f} %, max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        lead = bus_lufs[LEAD]
        print("  buses (LU vs the flute)", {k: round(v - lead, 1) for k, v in bus_lufs.items()})
        print("  gains for the plan", {k: round(GAINS[k] + PLAN[k] - (v - lead), 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
