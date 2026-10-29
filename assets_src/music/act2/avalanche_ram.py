"""`avalanche_ram`: the Avalanche Ram boss (M3-AUD-845; act_outline Ch12): two synchronized stems, an 83.5 s loop.

Original composition for this project (SPEC §2, §9). Original-material check: the charge theme, its answer, the
charging calls, the gallop and the bass ostinato below were written for this fight and are not derived from any
existing melody. The one borrowed phrase is our own: in the breakdown a far pipe plays Keth Pass's cell (the fall
B-A-G to the long E, and its climb back G-A-B to D), loaded from the zone's sketch (assets_src/music/keth_pass.py,
`TUNE`, never retyped) and played at the pass's own speed. The theme itself is built on that cell's climb (G-A-B),
started from the tonic and driven on (E-G-A-B), so the fight is the pass's music turned into a charge. The style
evoked is a highland one (hocketed pipes, an open-fifth drone, a big drum) set to a gallop; nothing is quoted.

The brief: an Ullari woolback, a long-necked shaggy pack animal, grown monstrous on drowned glimmer seeping from a
Lit Age terrace wall above the Keth Pass road; huge, its fleece matted into frozen locks hung with ice; it charges and
bellows; a frayed herd-cord is still tied round its neck. No model phases: stem 2 is its rage, which the game brings
in under 50% HP. It belongs to the mountain (the pass's key, meter, pipes, wind and cords), but as a fight: the
weight of a charge, an avalanche's rumble, and the animal it was (the herd bell).

E minor (Aeolian: E F# G A B C D, as Keth Pass), 6/8 at 92 dotted quarters a minute (exactly twice the pass's 46: a
bar is 1.304 s), 64 bars. The 6/8 is a gallop: a heavy fall on each dotted quarter and the hooves between.

**Stem 1** (`avalanche_ram_p1.ogg`, the fight; plays from the start):
* the theme on two hard-blown pipes (synth.winds.breath_flute, less breath than the pass's) in hocket, hard left and
  right, as the pass plays its tune (A); the answer (B) on the two pipes in octaves; the charging calls (C, E);
* the gallop: frame drums on every eighth (a heavy stroke on each dotted quarter) and the big drum on both; on the
  stamp bars the hooves paw twice, then a run of sixteenths drives into the next downbeat;
* a fingered bass ostinato (root, root, octave | root, fifth, octave) under the gallop;
* the mountain: the pass's wind and cords (act2_voices.wind, cord_song on E G B E), an open-fifth string pad;
* the herd bell (act2_voices.herd_bell, a woolback's wooden-clappered bell) swaying in the intro and the breakdown,
  and the far pipe playing the pass's cell (the sketch's own pipe, the sketch's TUNE) over it.

**Stem 2** (`avalanche_ram_p2.ogg`, the rage; the game fades it in under 50% HP):
* the bellow: a low, brassy, throat-formant call (synthesized saws, a subharmonic and a rasp) that scoops up a fourth
  into the chord's root and sags at the end, at every phrase start of the loud sections;
* low strings driving the gallop on every eighth (root and fifth, short, accented on the dotted quarters), and a
  held string counter-line under the pipes' answer (B, B');
* the avalanche: a low rumble that gathers over each eight bars, and a tumbling big-drum roll on the last bar of each;
  a sub-bass surge into every section;
* a second frame drum filling the gallop, and the ice: cracking high bars and a scatter of ice-crackle.

Form (bars): 1-8 the terrace wall (the gallop, the bass, the herd bell; the pipes' first call at 5) | 9-16 A, the
theme in hocket | 17-24 B, the answer in octaves | 25-32 C, the charge: the calls climbing, the stamp bars 26 28 30
32 | 33-40 the breakdown: the gallop stops, the bass holds E, the herd bell, the pass's cell on a far pipe (33-36 the
fall, 37-40 the climb as the drums come back) | 41-48 A' | 49-56 B' | 57-64 the charge again (stamps 58 60 62), a
drum fill in bar 64 that stops a sixteenth short, so bar 1's downbeat lands after a breath.

Mastering (as the Cinder Matron): both stems share one gain (the full stack at -16 LUFS) and one limiter gain curve
computed on the full stack (synth.mixer.limit_gain), so stem 1 + stem 2 is exactly the limited mix; equal lengths.
Stem 2 is trimmed so the stack sits about +2 LU over stem 1 alone. Loop: LOOPSTART = 0 on both. The files start a
sixteenth before bar 1's downbeat (the sidecars' `downbeat_offset_s`), so the wrap seam falls in bar 64's silent
last sixteenth.

Render:  python3 assets_src/music/act2/avalanche_ram.py
         (or tools/audio/render_all.py --act2 --only act2/avalanche_ram)
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
from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, midi_to_hz,  # noqa: E402
                       polyblep_saw, rng, smooth_noise)
from synth.electric import bass_note  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("_ram_keth_pass_sketch", os.path.join(MUSIC, "keth_pass.py"))   # the pass: its cell and its pipe
V = S.V                                                                   # the Act II kit

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music", "act2")
OUT = os.path.join(OUT_DIR, "avalanche_ram_p1.ogg")
OUT2 = os.path.join(OUT_DIR, "avalanche_ram_p2.ogg")
SEED = 20261845
TARGET_LUFS = -16.0
QUALITY = 3.0
BPM = 2 * S.BPM                      # 92 dotted quarters a minute, twice the pass
DQ = 60.0 / BPM
E8 = DQ / 3                          # one eighth, 0.217 s
BAR_E = 6
BAR = BAR_E * E8
BARS = 64
LOOP_S = BARS * BAR
FLUTE_PRE = V.FLUTE_PRE
## the file starts a sixteenth (half an eighth) before bar 1's downbeat; bar 64's fill leaves that sixteenth silent
LEAD_IN_E = 0.5
## Stem 2's trim at mastering: the rage lifts the stack about 2 LU over stem 1 alone (render prints both).
STEM2_GAIN_DB = 1.0                  # measured: stack -16.05, stem 1 alone -17.94 LUFS

_A = ["Em", "Em", "D", "Em", "C", "D", "Em", "Em"]
_B = ["C", "C", "G", "D", "Am", "Am", "C", "D"]
_CH = ["Em", "Em", "Em", "Em", "C", "C", "D", "D"]
CHORDS = (["Em", "Em", "C", "Em", "Em", "Em", "C", "D"] + _A + _B + _CH + _CH + _A + _B
          + ["Em", "Em", "C", "Em", "Em", "Em", "C", "D"])
SECTION = ["I"] * 8 + ["A"] * 8 + ["B"] * 8 + ["C"] * 8 + ["D"] * 8 + ["A2"] * 8 + ["B2"] * 8 + ["E"] * 8
ROOT_MIDI = {"Em": "E2", "C": "C2", "D": "D2", "G": "G1", "Am": "A1"}
PAD = {"Em": "E2 B2 E3", "C": "C2 G2 C3", "D": "D2 A2 D3", "G": "G1 D2 G2", "Am": "A1 E2 A2"}
STAMP_BARS = (26, 28, 30, 32, 58, 60, 62)
FILL_BAR = 64
LOUD = ("A", "B", "C", "A2", "B2", "E")

## the theme (pitch, eighths), one list per bar of 6 eighths: the pass's climb driven on from the tonic
THEME_A = [
    [("E5", 1), ("G5", 1), ("A5", 1), ("B5", 3)],
    [("A5", 2), ("G5", 1), ("E5", 3)],
    [("F#5", 1), ("G5", 1), ("A5", 1), ("D6", 3)],
    [("B5", 3), (None, 1), ("A5", 1), ("G5", 1)],
    [("G5", 2), ("E5", 1), ("C6", 3)],
    [("B5", 2), ("A5", 1), ("F#5", 3)],
    [("G5", 1), ("A5", 1), ("B5", 1), ("A5", 1), ("G5", 1), ("F#5", 1)],
    [("E5", 5), (None, 1)],
]
## the answer, on two pipes in octaves
THEME_B = [
    [("C6", 3), ("B5", 2), ("A5", 1)],
    [("G5", 3), ("E5", 3)],
    [("D6", 3), ("B5", 2), ("G5", 1)],
    [("A5", 4), ("F#5", 2)],
    [("E5", 1), ("A5", 2), ("B5", 1), ("C6", 2)],
    [("B5", 3), ("A5", 3)],
    [("G5", 2), ("A5", 1), ("B5", 2), ("C6", 1)],
    [("D6", 3), ("B5", 2), ("A5", 1)],
]
## the charge: the climb called and called again, a step higher (bars 25-31, 57-63, 5 and 7)
CALLS = {
    25: [("E5", 1), ("G5", 1), ("A5", 1), ("B5", 3)],
    27: [("G5", 1), ("A5", 1), ("B5", 1), ("D6", 3)],
    29: [("C6", 1), ("B5", 1), ("A5", 1), ("G5", 3)],
    31: [("A5", 1), ("B5", 1), ("C6", 1), ("D6", 3)],
}
CALLS.update({b + 32: v for b, v in CALLS.items()})
CALLS.update({5: CALLS[25], 7: [("G5", 1), ("A5", 1), ("B5", 1), ("A5", 3)]})
## stem 2: the strings' held counter-line under the answer (one note a bar)
COUNTER_B = ["G4", "E4", "B4", "A4", "C5", "A4", "G4", "F#4"]
## stem 2: the bellow at each phrase start of the loud sections (and as the gallop comes back, bar 37)
BELLOWS = (9, 13, 17, 21, 25, 29, 37, 41, 45, 49, 53, 57, 61)


def t_of(bar: int, e: float = 1.0) -> float:
    """Seconds from the loop start to eighth `e` (1-based) of `bar`."""
    return (bar - 1) * BAR + (e - 1) * E8


def fight_pipe(m: float, d: float, vel: float, seed: int, first: bool) -> np.ndarray:
    """The pass's pipe blown hard: less breath, a quicker tongue, a little vibrato only on the long notes."""
    return breath_flute(m, d * 0.9 + 0.02, vel, seed=seed, breath=0.42, scoop_cents=30.0 if first else 10.0,
                        vib_cents=7.0 if d > 0.5 else 0.0, vib_rate=5.6, swell=0.15 if d > 0.5 else 0.0,
                        attack=0.025, release=0.14, beta=0.7)


def add_hocket(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """Two pipes, hard left and right, each playing every other note (as the pass plays its tune)."""
    g = rng(seed)
    k = 0
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, ee in bar:
            d = ee * E8
            if p is not None:
                v = vel * float(g.uniform(0.93, 1.05)) * (1.07 if ee >= 3 else 1.0)
                x = fight_pipe(n(p), d, v, seed + int(round(pos * 1000)), k == 0)
                mx.add("pipes", x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=-0.5 if k % 2 == 0 else 0.5)
                k += 1
            pos += d


def add_octaves(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """The answer: the two pipes together, an octave apart."""
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
            for k, (off, vv, pan, bus) in enumerate(((0, 1.0, 0.25, "pipes"), (-12, 0.8, -0.25, "pipes_low"))):
                x = fight_pipe(n(p) + off, d, vel * vv * float(g.uniform(0.94, 1.04)),
                               seed + 17 * k + int(round(pos * 1000)), first)
                mx.add(bus, x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=pan)
            pos += d
            first = False


def herd_bell(mx: LoopMixer, bars: range, seed: int, vel: float) -> None:
    """The herd bell, swaying with the neck: the clapper on both sides of the bell, a dotted quarter apart, loosely."""
    g = rng(seed)
    for bar in bars:
        for k, e in enumerate((1, 4)):
            f = 620.0 if k == 0 else 590.0
            x = V.herd_bell(g, vel * float(g.uniform(0.6, 1.0)), f)
            mx.add("bell", x, t_of(bar, e) + float(g.uniform(0.02, 0.12)), pan=0.3)


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("wind", V.wind(LOOP_S, SEED + 3, lo_hz=300.0, hi_hz=2400.0, gusts=(8, 19, 5), hi_level=0.3), 0.0)
    mx.add("cords", V.cord_song(LOOP_S, [n("E5"), n("G5"), n("B5"), n("E6")], SEED + 4, q=45.0), 0.0)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch])
        brk = sec == "D" and bar < 37
        stamp = bar in STAMP_BARS
        # the pad: the open fifth, one chord a bar
        x = pad_chord([n(p) + 12 for p in PAD[ch].split()], BAR * 0.97, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=0.35, release=0.6, width=0.9)
        mx.add("pad", x, t_of(bar) - 0.05)
        # the bass
        if brk:
            if bar % 2 == 1:
                mx.add("bass", bass_note(root, 2 * BAR - 0.1, 0.8, seed=SEED + 6900 + bar, mute=0.0), t_of(bar))
        elif stamp:
            for e, dur_e, off, v in ((1, 0.8, 0, 0.95), (2, 0.8, 0, 0.9), (4, 0.5, 0, 0.6), (4.5, 0.5, 3, 0.62),
                                     (5, 0.5, 5, 0.66), (5.5, 0.5, 7, 0.7), (6, 0.9, 10, 0.75)):
                x = bass_note(root + off, dur_e * E8, v * float(g.uniform(0.94, 1.04)),
                              seed=SEED + 6000 + 10 * bar + int(2 * e), mute=0.4)
                mx.add("bass", x, t_of(bar, e) + 0.003)
        elif sec == "I" and bar <= 4:
            for e in (1, 4):
                mx.add("bass", bass_note(root, 2.6 * E8, 0.8, seed=SEED + 6500 + 10 * bar + e, mute=0.2), t_of(bar, e))
        else:
            soft = 0.8 if (sec == "D") else 1.0
            for e, dur_e, off, v in ((1, 1.7, 0, 0.88), (2, 0.8, 0, 0.5), (3, 0.9, 12, 0.66), (4, 1.6, 0, 0.8),
                                     (5, 0.8, 7, 0.56), (6, 0.9, 12, 0.55)):
                x = bass_note(root + off, dur_e * E8, soft * v * float(g.uniform(0.93, 1.05)),
                              seed=SEED + 6000 + 10 * bar + e, mute=0.35)
                mx.add("bass", x, t_of(bar, e) + 0.003)
        # the gallop
        if brk:
            mx.add("drums", big_drum(0.55, variant=bar, seed=SEED + 5), t_of(bar), pan=0.0)
            continue
        if bar <= 4:
            mx.add("drums", big_drum(0.85, variant=bar, seed=SEED + 5), t_of(bar, 1))
            mx.add("drums", big_drum(0.6, variant=bar + 1, seed=SEED + 5), t_of(bar, 4))
            if bar >= 3:
                for e in (3, 6):
                    mx.add("drums", frame_drum("tek", 0.3 + 0.04 * bar, variant=bar * 6 + e, seed=SEED + 6),
                           t_of(bar, e), pan=-0.15)
            continue
        if stamp:
            # the hooves paw twice; then the drive, sixteenths into the downbeat
            for e in (1, 2):
                mx.add("drums", big_drum(1.0, variant=bar + e, seed=SEED + 5), t_of(bar, e))
                mx.add("drums", frame_drum("slap", 0.85, variant=bar + e, seed=SEED + 6), t_of(bar, e), pan=0.1)
            for k in range(6):
                e = 4 + 0.5 * k
                mx.add("drums", frame_drum("tek" if k % 2 else "dum", 0.42 + 0.08 * k, variant=bar * 8 + k,
                                           seed=SEED + 6), t_of(bar, e), pan=0.05 if k % 2 == 0 else -0.15)
            continue
        if bar == FILL_BAR:
            mx.add("drums", big_drum(0.9, variant=bar, seed=SEED + 5), t_of(bar, 1))
            for k in range(9):          # 2.5 .. 6.5: the last sixteenth is left silent (the seam)
                e = 2.0 + 0.5 * k
                mx.add("drums", frame_drum("slap" if k % 2 else "dum", 0.45 + 0.055 * k, variant=k, seed=SEED + 6),
                       t_of(bar, e), pan=0.05)
            mx.add("drums", big_drum(0.75, variant=bar + 2, seed=SEED + 5), t_of(bar, 4))
            continue
        for e in range(1, BAR_E + 1):
            if e in (1, 4):
                st, v = "dum", (0.9 if e == 1 else 0.75)
            elif e == 6:
                st, v = "slap", 0.55
            else:
                st, v = ("tek" if e == 3 else "ghost"), (0.45 if e == 3 else 0.35)
            mx.add("drums", frame_drum(st, v * float(g.uniform(0.9, 1.06)), variant=bar * 8 + e, seed=SEED + 6),
                   t_of(bar, e) + float(g.normal(0, 0.003)), pan=0.05 if st == "dum" else -0.15)
        mx.add("drums", big_drum(0.9, variant=bar, seed=SEED + 5), t_of(bar, 1))
        if sec in LOUD:
            mx.add("drums", big_drum(0.62, variant=bar + 1, seed=SEED + 5), t_of(bar, 4))
    # the herd bell, and the pass's cell on its own far pipe at the pass's own speed (one pass eighth = two of ours)
    herd_bell(mx, range(1, 5), SEED + 40, 0.5)
    herd_bell(mx, range(33, 41), SEED + 41, 0.7)
    gp = rng(SEED + 50)
    for i, bar in enumerate(S.TUNE[:4]):
        pos = t_of(33 + 2 * i)
        for j, (p, ee) in enumerate(bar):
            d = 2 * ee * E8
            x = S.pipe(n(p), d, 0.5 * float(gp.uniform(0.95, 1.04)), SEED + 5000 + int(round(pos * 1000)), j == 0)
            mx.add("far", x, pos - FLUTE_PRE + float(gp.normal(0, 0.006)), pan=-0.35)
            pos += d
    # the pipes
    for bar, line in CALLS.items():
        add_hocket(mx, [line], bar, SEED + 300 + bar, 0.62)
    add_hocket(mx, THEME_A, 9, SEED + 100, 0.62)
    add_octaves(mx, THEME_B, 17, SEED + 200, 0.6)
    add_hocket(mx, THEME_A, 41, SEED + 400, 0.64)
    add_octaves(mx, THEME_B, 49, SEED + 500, 0.62)


def bellow(m: float, dur: float, vel: float, seed: int) -> np.ndarray:
    """The bellow: a low brassy call from a long throat. Three detuned saws and a subharmonic scoop up a fourth into
    pitch, waver, and sag at the end; they brighten as they swell (a dark and a formant-lit copy, crossfaded by
    level), with a rasp of throat noise. Mono."""
    g = rng(seed)
    N = int((dur + 0.9) * SR)
    t = np.arange(N) / SR
    f0 = midi_to_hz(m)
    vib = 22.0 * np.sin(2 * np.pi * 4.3 * t) * np.clip((t - 0.45) / 0.6, 0, 1)
    cents = (-500.0 * np.exp(-t / 0.11) + vib + 6.0 * smooth_noise(N, 1.5, g)
             - 260.0 * np.clip((t - (dur - 0.3)) / 0.5, 0, 1) ** 2)
    freq = f0 * 2 ** (cents / 1200.0)
    x = np.zeros(N)
    for k, det in enumerate((-9.0, 0.0, 8.0)):
        x += polyblep_saw(freq * 2 ** (det / 1200.0), SR, float(g.random()))
    ph = 2 * np.pi * np.cumsum(freq / 2) / SR
    x += 0.9 * np.sin(ph)
    a = np.clip(t / 0.22, 0, 1)
    env = a * a * (3 - 2 * a) * (0.75 + 0.25 * np.clip(t / 0.7, 0, 1))
    env = np.where(t > dur, env * np.exp(-(t - dur) / 0.18), env)
    dark = filt(x, [bq_lowpass(420.0, 0.7)])
    lit = filt(x, [bq_lowpass(2400.0, 0.7), bq_peak(620.0, 6.0, 1.4), bq_peak(1150.0, 4.0, 1.8)])
    b = np.clip(env, 0, 1) ** 1.5
    rasp = filt(g.standard_normal(N), [bq_bandpass(700.0, 1.0)]) * (1 + 0.6 * np.sin(ph))
    y = env * ((1 - b) * dark + b * lit + 0.25 * rasp)
    k = int(0.02 * SR)
    y[-k:] *= np.linspace(1, 0, k)
    return 0.12 * vel * y


def rumble(seconds: float, g) -> np.ndarray:
    """The avalanche: a low noise band (35-220 Hz) that gathers over `seconds`, tumbling (slow random bumps) and
    thickening into its end, then dropping away. Mono."""
    N = int(seconds * SR)
    t = np.arange(N) / SR
    x = filt(g.standard_normal(N), [bq_lowpass(220.0, 0.7), bq_lowpass(220.0, 0.7), bq_highpass(35.0, 0.7)])
    x /= np.std(x) + 1e-9
    tumble = 0.7 + 0.3 * np.abs(smooth_noise(N, 3.0, g))
    env = (0.15 + 0.85 * (t / seconds) ** 2.2) * tumble
    k = int(0.35 * SR)
    env[-k:] *= np.linspace(1, 0, k) ** 2
    return x * env


def ice_crackle(seconds: float, density: float, g) -> np.ndarray:
    """Ice cracking off the locks: short, high, band-limited pops (2.5-8 kHz), scattered. Mono."""
    N = int(seconds * SR)
    out = np.zeros(N)
    tt = float(g.exponential(1.0 / density))
    while tt < seconds - 0.05:
        k = int(g.uniform(0.002, 0.006) * SR)
        pop = filt(g.standard_normal(k + 64), [bq_bandpass(float(g.uniform(2500, 8000)), 1.5)])[:k]
        pop *= np.exp(-np.arange(k) / (0.25 * k)) * float(g.uniform(0.2, 1.0))
        s = int(tt * SR)
        out[s: s + k] += pop[: N - s]
        tt += float(g.exponential(1.0 / density))
    return out


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch]) + 12
        quiet = (sec == "D" and bar < 37) or (sec == "I" and bar <= 4)
        # the strings drive the gallop: root and fifth on every eighth, heavier on the dotted quarters
        if not quiet and bar not in STAMP_BARS:
            for e in range(1, BAR_E + 1):
                v = 0.95 if e in (1, 4) else 0.55
                x = pad_chord([root, root + 7], E8 * 0.78, v * float(g.uniform(0.94, 1.04)),
                              seed=SEED + 2000 + 8 * bar + e, voices=4, spread_cents=10.0, attack=0.012,
                              release=0.07, width=0.6)
                mx.add("strings", x, t_of(bar, e))
        elif bar in STAMP_BARS:
            for e in (1, 2):
                x = pad_chord([root, root + 7, root + 12], E8 * 0.9, 1.0, seed=SEED + 2600 + 8 * bar + e, voices=4,
                              spread_cents=10.0, attack=0.01, release=0.1, width=0.6)
                mx.add("strings", x, t_of(bar, e))
        if sec in ("B", "B2"):
            i = (bar - 1) % 8
            x = pad_chord([n(COUNTER_B[i])], BAR * 0.98, 0.9, seed=SEED + 2800 + bar, voices=5, spread_cents=8.0,
                          attack=0.25, release=0.5, width=0.5)
            mx.add("strings_hi", x, t_of(bar) - 0.04)
        if quiet:
            continue
        # the second drum: the gallop's hooves filled in
        for e in (2, 3, 5, 6):
            if bar in STAMP_BARS and e < 4:
                continue
            mx.add("drums2", frame_drum("dum" if e in (3, 6) else "ghost", 0.55 * float(g.uniform(0.9, 1.06)),
                                        variant=bar * 4 + e, size=1.3, seed=SEED + 8), t_of(bar, e) + 0.004, pan=0.25)
    # the avalanche over each eight bars, and its tumbling roll in the last
    for start in range(1, BARS + 1, 8):
        if SECTION[start - 1] == "D":
            continue
        mx.add("rumble", rumble(8 * BAR, rng(SEED + 3000 + start)), t_of(start), pan=0.0)
        last = start + 7
        if last != FILL_BAR:
            for k in range(12):
                e = 1 + 0.5 * k
                mx.add("drums2", big_drum(0.35 + 0.05 * k, variant=k, seed=SEED + 9), t_of(last, e),
                       pan=-0.3 if k % 2 else 0.3)
    for start in (1, 9, 17, 25, 37, 41, 49, 57):
        sub_t = np.arange(int(1.4 * SR)) / SR
        sub = np.sin(2 * np.pi * np.cumsum(36.0 + 18.0 * np.exp(-sub_t / 0.3)) / SR) * np.exp(-sub_t / 0.6)
        sub *= np.minimum(1.0, sub_t / 0.01)
        mx.add("sub", sub, t_of(start), pan=0.0)
    # the bellow
    for bar in BELLOWS:
        m = n(ROOT_MIDI[CHORDS[bar - 1]])
        if m < n("C2"):
            m += 12
        x = bellow(m, 1.7 * BAR, 1.0, SEED + 4000 + bar)
        y = bellow(m + 12, 1.7 * BAR, 0.5, SEED + 4100 + bar)
        mx.add("bellow", x, t_of(bar) - 0.08, pan=-0.1)
        mx.add("bellow", y, t_of(bar) - 0.06, pan=0.15)
    # the ice: cracking bars at the stamps and the bellows, and a scatter of crackle through the loud sections
    for bar in sorted(set(STAMP_BARS) | set(BELLOWS)):
        for k in range(3):
            m = n("E7") - float(g.integers(0, 7))
            x = metallophone_note(m, 0.4 * float(g.uniform(0.7, 1.0)), seed=SEED + 4500 + 10 * bar + k, decay=0.7,
                                  hardness=1.0, ombak_hz=9.0, damp_at=0.12)
            mx.add("ice", x, t_of(bar, 1.5 + 1.3 * k + float(g.uniform(0, 0.4))), pan=float(g.uniform(-0.7, 0.7)))
    for bar, sec in enumerate(SECTION, start=1):
        if sec in LOUD:
            for pan in (-0.6, 0.6):
                mx.add("ice", ice_crackle(BAR, 6.0, rng(SEED + 4700 + 2 * bar + (pan > 0))), t_of(bar), pan=pan)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "pipes": 0.0, "pipes_low": -2.8, "far": -1.0, "drums": -6.9, "bass": -7.0, "pad": 0.8, "wind": 6.3,
    "cords": -4.1, "bell": -5.5, "strings": 4.4, "strings_hi": -1.5, "bellow": -6.1, "rumble": -22.4, "drums2": -6.8,
    "sub": -17.2, "ice": -6.8,
}
## The plan (LU relative to the stem-1 lead, the pipes, by each bus's integrated loudness over the loop).
PLAN = {
    "pipes": 0.0, "pipes_low": -6.0, "far": -4.0, "drums": -3.0, "bass": -6.0, "pad": -12.0, "wind": -14.0,
    "cords": -16.0, "bell": -9.0, "strings": -5.0, "strings_hi": -7.0, "bellow": -3.0, "rumble": -11.0,
    "drums2": -7.0, "sub": -11.0, "ice": -15.0,
}
LEAD = "pipes"


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        pipe_eq = [bq_highpass(240, 0.7), bq_peak(2500, 2.0, 1.0), bq_lowpass(8000, 0.7)]
        mx.bus("pipes", G["pipes"], send=0.28, process=lambda x: filt(x, pipe_eq))
        mx.bus("pipes_low", G["pipes_low"], send=0.28, process=lambda x: filt(x, [bq_highpass(180, 0.7)]))
        mx.bus("far", G["far"], send=0.85, process=lambda x: filt(x, [bq_highpass(260, 0.7), bq_lowpass(3200, 0.7)]))
        mx.bus("drums", G["drums"], send=0.14, process=lambda x: filt(x, [bq_highpass(30, 0.7),
                                                                           bq_peak(120, 2.0, 1.0)]))
        mx.bus("bass", G["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(32, 0.7), bq_peak(90, 2.0, 0.9),
                                                                        bq_lowpass(2800, 0.7)]))
        mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1400.0))
        mx.bus("wind", G["wind"], send=0.15)
        mx.bus("cords", G["cords"], send=0.35)
        mx.bus("bell", G["bell"], send=0.5, process=lambda x: filt(x, [bq_highpass(250, 0.7)]))
    else:
        mx.bus("strings", G["strings"], send=0.18, process=lambda x: string_body(x, cutoff=1900.0))
        mx.bus("strings_hi", G["strings_hi"], send=0.35, process=lambda x: string_body(x, cutoff=2400.0))
        mx.bus("bellow", G["bellow"], send=0.35, process=lambda x: filt(x, [bq_highpass(40, 0.7)]))
        mx.bus("rumble", G["rumble"], send=0.1, process=lambda x: filt(x, [bq_highpass(30, 0.7)]))
        mx.bus("drums2", G["drums2"], send=0.15, process=lambda x: filt(x, [bq_highpass(30, 0.7)]))
        mx.bus("sub", G["sub"], send=0.0, process=lambda x: filt(x, [bq_lowpass(110, 0.7)]))
        mx.bus("ice", G["ice"], send=0.4, process=lambda x: filt(x, [bq_highpass(1500, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        sky = ModFDNReverb(rt60=2.6, rt60_high=1.0, predelay=0.04, size=1.4, mod_depth=8.0, mod_rate=0.3,
                           early_level=0.2, lowcut=120.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=sky, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
        del mx
        gc.collect()
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
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
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    extra = {"stems_of": "avalanche_ram", "loop_bars": BARS, "meter": "6/8 (bpm counts dotted quarters)",
             "downbeat_offset_s": lead_in / SR}
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 2, extra=extra)
    m = measure(stems[0] + stems[1])
    m1 = measure(stems[0])
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["stem1_lufs"] = m1["integrated_lufs"]
        stats["limited_fraction"] = float((lg < 0.999).mean())
    if verbose:
        print(f"avalanche_ram: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP {m['true_peak_dbtp']:.2f} "
              f"dBTP; stem 1 alone {m1['integrated_lufs']:.2f} LUFS; limited {(lg < 0.999).mean() * 100:.2f} %, "
              f"max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        lead = bus_lufs[LEAD]
        print("  buses (LU vs the pipes)", {k: round(v - lead, 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
