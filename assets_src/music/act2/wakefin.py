"""`wakefin`: the Wakefin boss (M3-AUD-845; act_outline Ch15): two synchronized stems, a 75.3 s loop.

Original composition for this project (SPEC §2, §9). Original-material check: the theme's continuation, its answer,
the high strings' counter-lines, the circling bass ostinato and the glow's circling figure below were written for
this fight and are not derived from any existing melody. The one borrowed phrase is our own: the theme opens with
Unlamped's vigil (Bb held, Cb-Bb-Gb-F falling to Eb), its pitches loaded from the zone's sketch
(assets_src/music/unlamped.py, `VIGIL`, never retyped) and set to the fight's pulse; and in the dive a far flute plays
the vigil's first two bars at the zone's own speed. So the fight is the night's grief with something circling under
it. The sea and the low E-flat drone are the sketch's own (`sea`, `drone`). The style evoked is a dark, low,
pulse-driven sea piece; nothing is quoted.

The brief: an Undertow-spawn sailfish whose dorsal sail has grown into a tall swept blade; it followed the first wake
out of Ansedra's lagoon, and is fought on the drifting bridal barge in the dark, with no lamp: the sea-glow is the
only light. Most of the fight it is the fin alone, circling the barge with a glowing wake; to strike it breaches
along the rail; it dives, the water goes dark, and a ring of sea-glow marks where it comes up. Stem 1 is the circling,
stem 2 the breaches (the game brings it in for the second half). Menace under the water and the cut of the blade,
never a bright attack: every struck sound here is dark (frame drums low-passed, no slaps; soft glass bars), and the
blade is heard as a sweep through the water, not a hit.

E-flat minor (Eb F Gb Ab Bb Cb Db, with D as the leading tone over B-flat, as Unlamped's final), 4/4 at 102 BPM
(exactly twice the zone's 51: a bar is 2.353 s), 32 bars. The pulse is sixteenths grouped 3+3+3+3+4: five uneven
strokes a bar that turn against the 4/4 the way the fin turns round the barge.

**Stem 1** (`wakefin_p1.ogg`, the circling; plays from the start):
* the theme on the low breath flute (the vigil's voice, played harder) doubled an octave below by low strings (A, A');
  the answer (B) higher, the flute climbing to G-flat and the leading tone;
* the circle: a fingered bass in the 3+3+3+3+4 (root, root, octave, root, fifth, octave), and low frame drums on the
  same groups with ghosted sixteenths between, a big drum on beats 1 and 3; all low-passed;
* the glow: soft glass bars (metallophone, hardness 0.12) circling a three-note chord figure on the five group
  strokes, so the figure lands on a different stroke each bar; in the dive, rising motes (the ring of sea-glow);
* the fin: every second bar a sweep of filtered water-noise with a faint falling whistle (the blade's edge), moving
  across the stereo field, left to right and back (the fin circling the barge);
* the night: the sketch's sea and its bowed low E-flat drone; a dark open-fifth string pad.

**Stem 2** (`wakefin_p2.ogg`, the breaches; the game fades it in for the second half):
* the breaches: a surge (water-noise and a low tone rising for two beats, two bars before the dive's breach) into a
  hit: a big drum, a sub-bass drop, a burst of spray falling back and the bubbles of the plunge; at bars 5, 9, 13, 17,
  25, 29 and, off the phrase, on beat 3 of bars 11, 19 and 31; the plunge at bar 21 (the fin goes under);
* low strings driving every sixteenth (root and fifth on the group strokes, the root between);
* high strings held over the answer (the vigil's Cb sighing to Bb) and over A' (G-flat falling to D);
* a second drum: the big drum on the pickups into beats 1 and the third group, low frame drums filling.

Form (bars): 1-4 the night (the sea and the drone; the bass and the glow come in at 3; the fin passes) | 5-12 A, the
theme | 13-20 B, the answer | 21-24 the dive: the drums stop, the bass holds, rising motes, the vigil on a far flute
at the zone's own speed; the circle comes back in 24 | 25-32 A', a drum fill in bar 32 that stops a sixteenth short,
so bar 1's downbeat lands after a breath.

Mastering (as the Cinder Matron): both stems share one gain (the full stack at -16 LUFS) and one limiter gain curve
computed on the full stack (synth.mixer.limit_gain), so stem 1 + stem 2 is exactly the limited mix; equal lengths.
The curve is the stricter of the full stack's and each stem's own, so neither stem alone peaks over the ceiling.
Stem 2 is trimmed so the stack sits about +2 LU over stem 1 alone. Loop: LOOPSTART = 0 on both. The files start a
sixteenth before bar 1's downbeat (the sidecars' `downbeat_offset_s`), so the wrap seam falls in bar 32's silent last
sixteenth.

Render:  python3 assets_src/music/act2/wakefin.py   (or tools/audio/render_all.py --act2 --only act2/wakefin)
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

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng,  # noqa: E402
                       smooth_noise)
from synth.electric import bass_note  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.water import bubble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("_wakefin_unlamped_sketch", os.path.join(MUSIC, "unlamped.py"))   # the night: its vigil, sea and drone

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music", "act2")
OUT = os.path.join(OUT_DIR, "wakefin_p1.ogg")
OUT2 = os.path.join(OUT_DIR, "wakefin_p2.ogg")
SEED = 20261846
TARGET_LUFS = -16.0
QUALITY = 3.0
BPM = 2 * S.BPM                      # 102, twice the zone
BEAT = 60.0 / BPM
S16 = BEAT / 4                       # one sixteenth, 0.147 s
BAR_S16 = 16
BAR = 4 * BEAT
BARS = 32
LOOP_S = BARS * BAR
FLUTE_PRE = S.FLUTE_PRE
## the file starts a sixteenth before bar 1's downbeat; bar 32's fill leaves that sixteenth silent
LEAD_IN_S16 = 1
## Stem 2's trim at mastering: the breaches lift the stack about 2 LU over stem 1 alone (render prints both).
STEM2_GAIN_DB = 1.5                  # measured: stack -16.09, stem 1 alone -17.95 LUFS
GROUPS = (0, 3, 6, 9, 12)            # the 3+3+3+3+4 group strokes (sixteenths, 0-based)

_A = ["Ebm", "Cb", "Ebm", "Bb", "Ebm", "Cb", "Abm", "Bb"]
_B = ["Cb", "Abm", "Fb", "Bb", "Cb", "Abm", "Bb", "Bb"]
CHORDS = ["Ebm", "Ebm", "Cb", "Bb"] + _A + _B + ["Ebm", "Ebm", "Cb", "Bb"] + _A
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["D"] * 4 + ["A2"] * 8
ROOT_MIDI = {"Ebm": "Eb2", "Cb": "Cb2", "Bb": "Bb1", "Abm": "Ab1", "Fb": "Fb2"}
FIFTH = {"Ebm": 7, "Cb": 7, "Bb": 7, "Abm": 7, "Fb": 7}
PAD = {"Ebm": "Eb3 Bb3", "Cb": "Cb3 Gb3", "Bb": "Bb2 F3", "Abm": "Ab2 Eb3", "Fb": "Fb3 Cb4"}
## the glow's circling figure: three chord tones a chord, cycled over the five group strokes
GLOW = {"Ebm": "Eb5 Gb5 Bb5", "Cb": "Eb5 Gb5 Cb6", "Bb": "D5 F5 Bb5", "Abm": "Eb5 Ab5 Cb6", "Fb": "Ab5 Cb6 Fb5"}
LOUD = ("A", "B", "A2")
FILL_BAR = 32

## the vigil's pitches (the sketch's bars 3-6: Bb, Cb-Bb-Gb-F, Eb), loaded, not retyped
_V = [p for b in (3, 4, 5, 6) for p, _ in S.VIGIL[b] if p is not None]
## the theme (pitch, sixteenths), one list per bar of 16: the vigil set to the pulse, then driven on
THEME_A = [
    [(_V[0], 6), (_V[1], 2), (_V[2], 4), (_V[3], 4)],
    [(_V[4], 8), (_V[5], 8)],
    [("Bb4", 6), ("Cb5", 2), ("Db5", 4), ("Cb5", 4)],
    [("D5", 4), ("Cb5", 4), ("Bb4", 8)],
    [("Eb5", 6), ("D5", 2), ("Eb5", 4), ("Bb4", 4)],
    [("Gb4", 6), ("Ab4", 2), ("Bb4", 4), ("Cb5", 4)],
    [("Cb5", 4), ("Bb4", 4), ("Ab4", 4), ("Gb4", 4)],
    [("F4", 12), (None, 4)],
]
## the answer, higher
THEME_B = [
    [("Gb5", 8), ("F5", 4), ("Eb5", 4)],
    [("Cb5", 8), ("Eb5", 4), ("Cb5", 4)],
    [("Ab4", 6), ("Bb4", 2), ("Cb5", 4), ("Db5", 4)],
    [("D5", 8), ("F5", 4), ("D5", 4)],
    [("Eb5", 6), ("Gb5", 2), ("F5", 4), ("Eb5", 4)],
    [("Eb5", 4), ("Cb5", 4), ("Ab4", 8)],
    [("Bb4", 4), ("Cb5", 4), ("D5", 4), ("F5", 4)],
    [("D5", 6), ("Cb5", 2), ("Bb4", 8)],
]
## stem 2: the high strings, one held note a bar: the vigil's sigh (Cb to Bb) over B, G-flat falling to D over A'
COUNTER_B = ["Cb6", "Cb6", "Cb6", "Bb5", "Cb6", "Cb6", "Bb5", "Bb5"]
COUNTER_A = ["Gb5", "Gb5", "Gb5", "F5", "Gb5", "Gb5", "Eb5", "D5"]
## stem 2: the breaches (bar, sixteenth), and the plunge as the dive starts
BREACHES = ((5, 0), (9, 0), (11, 8), (13, 0), (17, 0), (19, 8), (25, 0), (29, 0), (31, 8))
PLUNGE = 21
## the glow's rising motes in the dive (bar, sixteenth, notes): the ring of sea-glow where it will come up
MOTES = [(21, 2, "Bb4 Eb5 Gb5"), (21, 10, "Gb4 Bb4 Eb5"), (22, 4, "Eb5 Gb5 Bb5"), (22, 12, "Bb4 Db5 Eb5"),
         (23, 2, "Eb5 Gb5 Cb6"), (23, 9, "Gb5 Cb6 Eb6"), (24, 0, "D5 F5 Bb5"), (24, 6, "F5 Bb5 D6")]

for _bar in THEME_A + THEME_B:
    assert sum(e for _, e in _bar) == BAR_S16, _bar


def t_of(bar: int, s: float = 0.0) -> float:
    """Seconds from the loop start to sixteenth `s` (0-based) of `bar`."""
    return (bar - 1) * BAR + s * S16


def fight_flute(m: float, d: float, vel: float, seed: int, first: bool) -> np.ndarray:
    """The vigil's low flute blown harder: less breath, a quicker tongue, vibrato only on the long notes."""
    return breath_flute(m, d * 0.92 + 0.03, vel, seed=seed, breath=0.45, scoop_cents=35.0 if first else 12.0,
                        vib_cents=9.0 if d > 0.8 else 3.0, vib_rate=5.0, swell=0.25 if d > 0.8 else 0.0,
                        attack=0.04, release=0.2, beta=0.55)


def add_theme(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """The flute, and the low strings an octave below it."""
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, ee in bar:
            d = ee * S16
            if p is None:
                pos += d
                first = True
                continue
            v = vel * float(g.uniform(0.94, 1.04)) * (1.06 if ee >= 6 else 1.0)
            x = fight_flute(n(p), d, v, seed + int(round(pos * 1000)), first)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=0.1)
            y = pad_chord([n(p) - 12], d * 0.95, 0.8 * v, seed=seed + 7 + int(round(pos * 1000)), voices=5,
                          spread_cents=8.0, attack=0.05, release=0.22, width=0.5)
            mx.add("cellos", y, pos - 0.01)
            pos += d
            first = False


def fin_cut(dur: float, g, left_to_right: bool) -> np.ndarray:
    """The blade through the water: noise swept up through a run of band-passes and back down (crossfaded), with a
    faint falling whistle from the blade's edge, carried across the stereo field. Stereo, normalized."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    u = t / dur
    noise = g.standard_normal(N + 2048)
    centres = (300.0, 520.0, 850.0, 1300.0, 850.0, 520.0)
    k = len(centres)
    x = np.zeros(N)
    for i, fc in enumerate(centres):
        band = filt(noise, [bq_bandpass(fc, 1.6)])[2048:]
        w = np.clip(1.0 - np.abs(u * (k - 1) - i), 0.0, 1.0)
        x += band * w
    x /= np.std(x) + 1e-9
    f = 760.0 * 2 ** (-0.45 * u) * (1 + 0.004 * np.sin(2 * np.pi * 6.0 * t))
    whistle = 0.12 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * u) ** 3
    env = np.sin(np.pi * np.clip(u, 0, 1)) ** 1.6 * (0.8 + 0.2 * np.abs(smooth_noise(N, 7.0, g)))
    y = (x + whistle) * env
    p = (u if left_to_right else 1 - u) * 1.6 - 0.8
    a = (p + 1) * np.pi / 4
    out = np.stack([y * np.cos(a), y * np.sin(a)], axis=1)
    return out / (np.abs(out).max() + 1e-9)


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("sea", S.sea(mx.L, SEED + 3), 0.0)
    mx.add("drone", S.drone(mx.L, SEED + 4), 0.0)
    glow_i = 0
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch])
        held = (sec == "I" and bar <= 2) or (sec == "D" and bar < 24)
        # the pad: a dark open fifth, one chord a bar
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.97, 0.4, seed=SEED + 200 + bar, voices=4,
                      attack=0.4, release=0.7, width=0.9)
        mx.add("pad", x, t_of(bar) - 0.06)
        # the bass: held in the night and the dive, else the circle
        if held:
            mx.add("bass", bass_note(root, BAR - 0.08, 0.75, seed=SEED + 6900 + bar, mute=0.0), t_of(bar))
        else:
            for s, dur, off, v in ((0, 3, 0, 0.9), (3, 3, 0, 0.6), (6, 3, 12, 0.7), (9, 3, 0, 0.62),
                                   (12, 2, FIFTH[ch], 0.68), (14, 2, 12, 0.58)):
                x = bass_note(root + off, dur * S16 * 0.9, v * float(g.uniform(0.93, 1.05)),
                              seed=SEED + 6000 + 20 * bar + s, mute=0.4)
                mx.add("bass", x, t_of(bar, s) + 0.003)
        # the glow's circling figure (from bar 3, not in the dive)
        if not held:
            figure = [n(p) for p in GLOW[ch].split()]
            for s in GROUPS:
                m = figure[glow_i % 3]
                glow_i += 1
                x = metallophone_note(m, 0.3 * float(g.uniform(0.8, 1.0)), seed=SEED + 4000 + 20 * bar + s,
                                      decay=1.6, hardness=0.12, ombak_hz=2.2, damp_at=0.55)
                mx.add("glow", x, t_of(bar, s) + float(g.normal(0, 0.003)), pan=-0.4 + 0.2 * GROUPS.index(s))
        # the drums
        if held:
            if sec == "D" or bar == 1:
                mx.add("drums", big_drum(0.5 if sec == "D" else 0.7, variant=bar, seed=SEED + 5), t_of(bar))
            continue
        if bar == FILL_BAR:
            mx.add("drums", big_drum(0.9, variant=bar, seed=SEED + 5), t_of(bar))
            for k, s in enumerate(range(4, 15)):          # sixteenths 4..14: the last sixteenth is left silent
                mx.add("drums", frame_drum("dum", 0.42 + 0.045 * k, variant=k, size=1.2, seed=SEED + 6),
                       t_of(bar, s), pan=-0.2 if k % 2 else 0.2)
            mx.add("drums", big_drum(0.7, variant=bar + 1, seed=SEED + 5), t_of(bar, 8))
            continue
        intro = sec == "I"
        for s in range(BAR_S16):
            if s in GROUPS:
                st, v = "dum", (0.85 if s == 0 else 0.62)
            else:
                if intro:
                    continue
                st, v = "ghost", (0.3 if s % 2 == 0 else 0.22)
            v *= 0.7 if intro else 1.0
            mx.add("drums", frame_drum(st, v * float(g.uniform(0.9, 1.06)), variant=bar * 16 + s, size=1.2,
                                       seed=SEED + 6), t_of(bar, s) + float(g.normal(0, 0.003)),
                   pan=0.05 if st == "dum" else -0.2)
        mx.add("drums", big_drum(0.9, variant=bar, seed=SEED + 5), t_of(bar))
        if sec in LOUD:
            mx.add("drums", big_drum(0.6, variant=bar + 2, seed=SEED + 5), t_of(bar, 8))
    # the fin: every second bar, across the field and back (not in the dive: it is under)
    gf = rng(SEED + 30)
    for i, bar in enumerate(range(1, BARS + 1, 2)):
        if SECTION[bar - 1] == "D":
            continue
        mx.add("fin", fin_cut(1.5 * BAR, gf, i % 2 == 0), t_of(bar, 4))
    # the dive: rising motes, and the vigil's first two bars on a far flute at the zone's own speed
    for i, (bar, s, notes) in enumerate(MOTES):
        for j, p in enumerate(notes.split()):
            x = metallophone_note(n(p), 0.3 * float(g.uniform(0.8, 1.0)) * 0.9 ** j, seed=SEED + 4500 + 10 * i + j,
                                  decay=3.5, hardness=0.1, ombak_hz=1.6)
            mx.add("glow", x, t_of(bar, s + 1.5 * j) + float(g.normal(0, 0.01)), pan=-0.5 + 0.13 * i)
    gp = rng(SEED + 50)
    pos, first = t_of(21), True
    for b in (3, 4):
        for p, beats in S.VIGIL[b]:
            d = 2 * beats * BEAT              # one zone beat is two of ours
            x = breath_flute(n(p), d * 0.95 + 0.05, 0.45 * float(gp.uniform(0.95, 1.04)),
                             seed=SEED + 5000 + int(round(pos * 1000)), breath=0.55,
                             scoop_cents=45.0 if first else 15.0, vib_cents=8.0, vib_rate=4.0, swell=0.3,
                             attack=0.14 if first else 0.08, release=0.9, beta=0.5)
            mx.add("far", x, pos - FLUTE_PRE + float(gp.normal(0, 0.006)), pan=-0.3)
            pos += d
            first = False
    # the theme
    add_theme(mx, THEME_A, 5, SEED + 100, 0.62)
    add_theme(mx, THEME_B, 13, SEED + 200, 0.64)
    add_theme(mx, THEME_A, 25, SEED + 300, 0.66)


def surge(dur: float, g) -> np.ndarray:
    """The rise before a breach: water-noise climbing through low band-passes and a low tone gliding up an octave,
    swelling to the hit and cut there. Mono."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    u = t / dur
    noise = g.standard_normal(N + 2048)
    centres = (120.0, 220.0, 400.0, 700.0)
    k = len(centres)
    x = np.zeros(N)
    for i, fc in enumerate(centres):
        band = filt(noise, [bq_bandpass(fc, 1.0)])[2048:]
        x += band * np.clip(1.0 - np.abs(u * (k - 1) - i), 0.0, 1.0)
    x /= np.std(x) + 1e-9
    f = 38.0 * 2 ** u
    tone = 0.8 * np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = u ** 2.4
    y = (x + tone) * env
    c = int(0.012 * SR)
    y[-c:] *= np.linspace(1, 0, c)
    return y


def breach(g, vel: float = 1.0) -> np.ndarray:
    """The hit as it breaks the surface: a sub-bass drop, a dark burst of spray, the spray falling back a moment
    later, and the bubbles of the plunge. No bright transient: the spray is low-passed at 2.4 kHz. Stereo."""
    N = int(3.0 * SR)
    t = np.arange(N) / SR
    f = 30.0 + 42.0 * np.exp(-t / 0.18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7) * np.minimum(1.0, t / 0.008)
    out = np.zeros((N, 2))
    for ch in range(2):
        spray = filt(g.standard_normal(N), [bq_lowpass(2400.0, 0.7), bq_lowpass(2400.0, 0.7),
                                            bq_highpass(140.0, 0.7)])
        spray /= np.std(spray) + 1e-9
        burst = np.minimum(1.0, t / 0.02) * np.exp(-t / 0.28)
        fall = 0.55 * np.clip((t - 0.35) / 0.15, 0, 1) * np.exp(-np.clip(t - 0.35, 0, None) / 0.7)
        out[:, ch] = 0.9 * sub + 0.45 * spray * (burst + fall)
    for _ in range(14):
        b = bubble(float(g.uniform(4.0, 14.0)), float(g.uniform(0.05, 0.18)), rise=0.1)
        s = int(g.uniform(0.15, 1.6) * SR)
        ch = int(g.integers(0, 2))
        e = min(N, s + len(b))
        out[s:e, ch] += b[: e - s]
    k = int(0.05 * SR)
    out[-k:] *= np.linspace(1, 0, k)[:, None]
    return vel * out / (np.abs(out).max() + 1e-9)


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch]) + 12
        quiet = (sec == "I" and bar <= 2) or (sec == "D" and bar < 24)
        if not quiet:
            # the strings drive every sixteenth: root and fifth on the group strokes, the root between
            for s in range(BAR_S16):
                ramp = 0.45 + 0.55 * s / (BAR_S16 - 1) if sec == "D" else 1.0   # bar 24: the circle comes back
                if bar == FILL_BAR and s == BAR_S16 - 1:
                    continue
                grp = s in GROUPS
                notes = [root, root + FIFTH[ch]] if grp else [root]
                v = (0.95 if grp else 0.5) * ramp * float(g.uniform(0.94, 1.04))
                x = pad_chord(notes, S16 * 0.8, v, seed=SEED + 2000 + 16 * bar + s, voices=4, spread_cents=10.0,
                              attack=0.008, release=0.05, width=0.6)
                mx.add("strings", x, t_of(bar, s))
            # the second drum: the pickups into beat 1 and the third group, low frame drums filling
            if sec in LOUD and bar != FILL_BAR:
                mx.add("drums2", big_drum(0.55, variant=bar, seed=SEED + 9), t_of(bar, 15))
                mx.add("drums2", big_drum(0.5, variant=bar + 1, seed=SEED + 9), t_of(bar, 5))
                for s in (2, 8, 11, 14):
                    mx.add("drums2", frame_drum("dum", 0.5 * float(g.uniform(0.9, 1.06)), variant=bar * 4 + s,
                                                size=1.5, seed=SEED + 8), t_of(bar, s) + 0.004, pan=0.3)
        i = (bar - 1) % 8
        if sec == "B":
            x = pad_chord([n(COUNTER_B[i])], BAR * 0.98, 0.9, seed=SEED + 2800 + bar, voices=5, spread_cents=8.0,
                          attack=0.3, release=0.6, width=0.5)
            mx.add("counter", x, t_of(bar) - 0.05)
        elif sec == "A2":
            x = pad_chord([n(COUNTER_A[i])], BAR * 0.98, 0.9, seed=SEED + 2900 + bar, voices=5, spread_cents=8.0,
                          attack=0.3, release=0.6, width=0.5)
            mx.add("counter", x, t_of(bar) - 0.05)
    # the breaches, each with its surge; the dive's breach (bar 25) rises out of two bars of dark water
    for k, (bar, s) in enumerate(BREACHES):
        gb = rng(SEED + 3000 + k)
        hit = t_of(bar, s)
        sd = 2 * BAR if bar == 25 else 2 * BEAT
        mx.add("surge", surge(sd, gb), hit - sd)
        mx.add("breach", breach(gb, 1.0), hit)
        mx.add("drums2", big_drum(1.0, variant=k, seed=SEED + 9), hit)
    # the plunge: the fin goes under as the dive starts
    gpl = rng(SEED + 3100)
    pl = breach(gpl, 0.55)
    pl = filt(pl, [bq_lowpass(700.0, 0.7)])
    mx.add("breach", pl, t_of(PLUNGE))


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "flute": 0.0, "cellos": 5.8, "far": -2.2, "glow": 2.3, "bass": -3.9, "drums": -6.2, "pad": 2.0, "sea": -19.0,
    "drone": -23.5, "fin": -17.0, "strings": 6.0, "counter": 0.0, "drums2": -4.8, "surge": -28.2, "breach": -9.6,
}
## The plan (LU relative to the stem-1 lead, the flute, by each bus's integrated loudness over the loop).
PLAN = {
    "flute": 0.0, "cellos": -5.0, "far": -5.0, "glow": -10.0, "bass": -5.0, "drums": -4.0, "pad": -12.0,
    "sea": -11.0, "drone": -13.0, "fin": -8.0, "strings": -4.0, "counter": -6.0, "drums2": -6.0, "surge": -9.0,
    "breach": -4.0,
}
LEAD = "flute"


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        flute_eq = [bq_highpass(160, 0.7), bq_peak(1000, 1.5, 1.0), bq_lowpass(5000, 0.7)]
        mx.bus("flute", G["flute"], send=0.3, process=lambda x: filt(x, flute_eq))
        mx.bus("cellos", G["cellos"], send=0.25, process=lambda x: string_body(x, cutoff=1300.0))
        mx.bus("far", G["far"], send=0.85, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_lowpass(2600, 0.7)]))
        mx.bus("glow", G["glow"], send=0.6, process=lambda x: filt(x, [bq_highpass(400, 0.7), bq_lowpass(4200, 0.7)]))
        mx.bus("bass", G["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(32, 0.7), bq_peak(90, 2.0, 0.9),
                                                                        bq_lowpass(2200, 0.7)]))
        mx.bus("drums", G["drums"], send=0.15, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_peak(110, 2.0, 1.0),
                                                                           bq_lowpass(2200, 0.7)]))
        mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1100.0))
        mx.bus("sea", G["sea"], send=0.15)
        mx.bus("drone", G["drone"], send=0.3, process=lambda x: filt(x, [bq_lowpass(700, 0.7)]))
        mx.bus("fin", G["fin"], send=0.3, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_lowpass(3500, 0.7)]))
    else:
        mx.bus("strings", G["strings"], send=0.18, process=lambda x: string_body(x, cutoff=1600.0))
        mx.bus("counter", G["counter"], send=0.4, process=lambda x: string_body(x, cutoff=2400.0))
        mx.bus("drums2", G["drums2"], send=0.15, process=lambda x: filt(x, [bq_highpass(30, 0.7),
                                                                             bq_lowpass(2000, 0.7)]))
        mx.bus("surge", G["surge"], send=0.2, process=lambda x: filt(x, [bq_highpass(30, 0.7)]))
        mx.bus("breach", G["breach"], send=0.3, process=lambda x: filt(x, [bq_highpass(25, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        night = ModFDNReverb(rt60=3.2, rt60_high=1.1, predelay=0.04, size=1.5, mod_depth=10.0, mod_rate=0.25,
                             early_level=0.15, lowcut=100.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=night, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
        del mx
        gc.collect()
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    lead_in = int(round(LEAD_IN_S16 * S16 * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    # one limiter gain curve for both stems (wrap-aware), iterated to the target: the stricter of the curves the full
    # stack and each stem alone would need, so the sum stays exactly the limited mix and neither stem alone peaks over
    # the ceiling (the breaches' sub drop can partly cancel against stem 1's bass, so stem 2 alone peaks higher)
    def _lg(x: np.ndarray) -> np.ndarray:
        return limit_gain(np.concatenate([x[-ctx:], x, x[:ctx]]), -2.0)[ctx: ctx + L]

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
    extra = {"stems_of": "wakefin", "loop_bars": BARS, "meter": "4/4", "downbeat_offset_s": lead_in / SR}
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
        print(f"wakefin: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP {m['true_peak_dbtp']:.2f} "
              f"dBTP; stem 1 alone {m1['integrated_lufs']:.2f} LUFS; limited {(lg < 0.999).mean() * 100:.2f} %, "
              f"max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        lead = bus_lufs[LEAD]
        print("  buses (LU vs the flute)", {k: round(v - lead, 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
