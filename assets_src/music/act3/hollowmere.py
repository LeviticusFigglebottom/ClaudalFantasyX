"""`hollowmere`: Ch17 "Hollowmere", the Saltwright flotilla and Dace's dry-dock (M3-AUD-852; act3_plan.md §2,
act_outline Ch17): a 135 s seamless zone loop.

Original composition for this project (SPEC §2, §9). Original-material check: the only tune not written here is
Dace's current-song (motifs.py CURRENT_SONG), imported and never retyped; the wright's whistle carries it in
fragments (a phrase, the two "soundings" alone, an echo from a far hull). Everything else was written for this cue
and shares no phrase with the game's other themes or any melody we know: the three wrights' interlocking mallet
patterns, the deck-bass, the chord plan (Dm C G, the dorian major IV, and an F-Am-G turn), and the low string's
lament in the B section (A3 falling through G-F-E to C, climbing back only as far as G and left there). The style
evoked is work music on the water (a raft-town's caulking and lashing in a slow three); nothing is quoted.

The brief: the Hollowmere flotilla, Dace's floating dry-dock and his unfinished hull. Saltwright work music:
mallets on hulls, rope, a wright's whistle carrying the current-song (the Saltwrights navigate by sung charts,
bible §7). Warm and communal, but not jolly: Liss's father hasn't spoken since Tobin's pyre-raft, so the middle of
the loop lets the work thin to one mallet and gives the silence to a single low string.

D dorian, 3/4 at 76 BPM (motifs.CURRENT_SONG_BPM, so the whistle's fragments sit in the song's own tempo; a bar is
2.37 s; the song's first two phrases are two bars each), 57 bars (odd, so the loop never settles into pairs).

Ensemble (all synthesized; no samples):
* three wrights' mallets on hulls: a wooden mallet on a struck hull (a short pulse through the hull's modes), a
  deep hull on the downbeat, a smaller one on beat two and its "and", and a mallet on a caulking iron (a small dry
  tink on A6) on the off-beats;
* the rope: stick-slip creaks of lashings under strain, on the swell;
* the sea against the hulls: a low wash swelling every three bars, and small laps;
* a bowed D-A drone under everything (exactly periodic over the loop), and a warm string pad on the chords;
* the deck-bass: a plucked low string through a wooden box, root on 1 and fifth on 3;
* the wright's whistle (the Act II kit's whistled voice, no tongue-click), an octave over the song's written pitch,
  and a second whistler on a far hull, wetter, at the written pitch;
* a low string (cello), the lament in the B section and a counterline in C.

Form (bars):
  1-4   the dock: the sea, the drone, the rope; one deep mallet from bar 2
  5-12  the work gathers: Dm Dm C C G G Dm Dm; the pad and the deck-bass; the mid mallet from 7, the iron from 9
  13-20 A: the whistle: phrase 1 (13-14), the soundings echoed from the far hull (17), phrase 2 (18-19)
  21-32 B, the silence: F F Am Am G G Dm Dm F C Am Am; the mallets thin to one knock every other bar and stop at
        29; the whistle is gone; the low string's lament, left on G over A minor
  33-44 A': the work comes back a wright at a time; the whistle's phrase 3, "sound again, and home to D" (37-39);
        the soundings passed from near to far (41-42)
  45-52 C, together: the cello's counterline; the near and far whistlers in octaves, phrase 2 then phrase 3
  53-57 the dock again: the mallets drop out; bar 57 is the sea and the rope, which is bar 1

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`); nothing is struck there, so the seam falls inside the sea's wash.

Render:  python3 assets_src/music/act3/hollowmere.py   (or tools/audio/render_all.py --act3 --only act3/hollowmere)
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
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"_act3_{name}", os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _mod("act2_voices")      # the Act II kit: the whistle, body_ir, periodic_drone, finish()

OUT = os.path.join(ROOT, "assets", "audio", "music", "act3", "hollowmere.ogg")
SEED = 20261752
TARGET_LUFS = -16.0
QUALITY = 3.0
BPM = CURRENT_SONG_BPM
BEAT = 60.0 / BPM
BAR_BEATS = 3
BAR = BAR_BEATS * BEAT
BARS = 57
LOOP_S = BARS * BAR
LEAD_IN_BEATS = 0.25
EIGHTH = BEAT / 2
SWELLS = 19                  # the sea lifts once every three bars
SCATTER = 0.006              # mallet timing scatter (s): hands, not a clock

## the pad, bar by bar (None: no pad)
CHORDS = ([None] * 4
          + ["Dm", "Dm", "C", "C", "G", "G", "Dm", "Dm"]
          + ["Dm", "Dm", "C", "G", "Dm", "F", "C", "Dm"]
          + ["F", "F", "Am", "Am", "G", "G", "Dm", "Dm", "F", "C", "Am", "Am"]
          + ["Dm", "Dm", "C", "G", "Dm", "C", "Dm", "Dm", "C", "G", "Dm", "Dm"]
          + ["Dm", "G", "F", "C", "Dm", "C", "Dm", "Dm"]
          + ["Dm", "C", "G", "Dm", None])
PAD = {"Dm": "D3 A3 F4", "C": "C3 G3 E4", "G": "G2 D3 B3", "Am": "A2 E3 C4", "F": "F2 C3 A3"}
ROOTS = {"Dm": ("D2", "A2"), "C": ("C2", "G2"), "G": ("G1", "D2"), "Am": ("A1", "E2"), "F": ("F1", "C2")}
BASS_BARS = set(range(5, 21)) | set(range(33, 57))

## the wright's whistle: (bar, beat, phrase index, first note, last note + 1, transpose, who)
WHISTLE_UP = 12
FRAGMENTS = [
    (13, 0.0, 0, 0, 7, WHISTLE_UP, "near"),      # phrase 1 whole
    (17, 0.0, 0, 0, 3, WHISTLE_UP, "far"),       # the soundings, from a far hull
    (18, 0.0, 1, 0, 7, WHISTLE_UP, "near"),      # phrase 2
    (37, 0.0, 2, 0, 6, WHISTLE_UP, "near"),      # phrase 3: sound again, and home to D
    (41, 0.0, 0, 0, 3, WHISTLE_UP, "near"),      # the soundings passed along ...
    (42, 0.0, 0, 0, 3, WHISTLE_UP, "far"),       # ... and answered
    (47, 0.0, 1, 0, 7, WHISTLE_UP, "near"),      # together: phrase 2 in octaves
    (47, 0.0, 1, 0, 7, 0, "far"),
    (49, 0.0, 2, 0, 6, WHISTLE_UP, "near"),      # and phrase 3
    (49, 0.0, 2, 0, 6, 0, "far"),
]

## the low string: bar -> [(pitch | None, beats)]; the lament (B) and the counterline (C)
CELLO = {
    21: [("A3", 3)], 22: [("G3", 1.5), ("F3", 1.5)], 23: [("E3", 3)], 24: [("C3", 2), ("E3", 1)],
    25: [("D3", 3)], 26: [("B2", 2), ("D3", 1)], 27: [("F3", 3)], 28: [("E3", 1.5), ("D3", 1.5)],
    29: [("C3", 3)], 30: [("E3", 2), ("G3", 1)], 31: [("A3", 3)], 32: [("G3", 2), (None, 1)],
    45: [("F3", 3)], 46: [("D3", 3)], 47: [("C3", 1.5), ("A2", 1.5)], 48: [("G3", 3)],
    49: [("F3", 2), ("D3", 1)], 50: [("E3", 3)], 51: [("D3", 3)], 52: [("D3", 2.5), (None, 0.5)],
}

## the mallets: which eighths (0-5) each wright strikes, bar by bar
DEEP, MID, IRON = "deep", "mid", "iron"


def mallet_plan() -> list[tuple[int, str, int, float]]:
    """[(bar, wright, eighth, velocity)]."""
    out = []
    for bar in range(1, BARS + 1):
        full = 9 <= bar <= 20 or 37 <= bar <= 52
        if 2 <= bar <= 20 or 33 <= bar <= 55:
            v = 0.5 if bar < 5 else 0.75
            out.append((bar, DEEP, 0, v))
            if full and (bar % 2 == 0 or bar >= 45):
                out.append((bar, DEEP, 4, 0.5))
        if 21 <= bar <= 28 and bar % 2 == 1:                 # B: one knock every other bar, fading
            out.append((bar, DEEP, 0, 0.6 - 0.07 * (bar - 21)))
        if 7 <= bar <= 20 or 35 <= bar <= 54:
            out += [(bar, MID, 2, 0.6), (bar, MID, 3, 0.45)]
        if full:
            out += [(bar, IRON, 1, 0.4), (bar, IRON, 5, 0.32)]
    return out


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def _circ(x: np.ndarray, sections, pre_s: float = 2.0) -> np.ndarray:
    """Filter a periodic signal (one cycle) in steady state: its own last seconds are fed in first."""
    k = int(pre_s * SR)
    y = filt(np.concatenate([x[-k:], x]), sections)
    return y[k: k + len(x)]


def sea(L: int, seed: int) -> np.ndarray:
    """The sea in the lanes between hulls: a low wash lifting SWELLS times a loop and a thin hiss behind it.
    Exactly periodic over L samples. Stereo."""
    g = rng(seed)
    t = np.arange(L) / SR
    Ls = L / SR
    out = np.zeros((L, 2))
    wash0 = _circ(g.standard_normal(L), [bq_lowpass(420, 0.7), bq_highpass(45, 0.7)])
    for ch in range(2):
        wash = 0.8 * wash0 + 0.55 * _circ(g.standard_normal(L), [bq_lowpass(420, 0.7), bq_highpass(45, 0.7)])
        hiss = _circ(g.standard_normal(L), [bq_bandpass(2200, 0.6), bq_lowpass(5000, 0.7)])
        ph = 0.1 * ch
        lift = 0.5 + 0.5 * np.cos(np.pi * (SWELLS * t / Ls - ph)) ** 2
        brk = (0.5 + 0.5 * np.cos(2 * np.pi * (SWELLS * t / Ls - ph - 0.2))) ** 3
        out[:, ch] = wash / np.std(wash) * lift + 0.2 * hiss / np.std(hiss) * brk
    return out / np.abs(out).max()


def hull_ir(scale: float, seed: int) -> np.ndarray:
    """A hull's planking as a resonant body: low wooden modes (scaled up for smaller hulls), a little ring."""
    modes = ((88.0, 18, 1.0), (151.0, 16, 0.7), (236.0, 14, 0.6), (402.0, 12, 0.45), (690.0, 9, 0.28),
             (1240.0, 7, 0.14), (2300.0, 5, 0.06))
    return V.body_ir([(f * scale, q, a) for f, q, a in modes], seed, length=0.4, scale=0.08)


def mallet(ir: np.ndarray, vel: float, width_ms: float, g) -> np.ndarray:
    """A wooden mallet on a hull: a half-sine contact pulse (wider = softer) with a breath of grain, through the
    hull's modes. Mono."""
    w = int(width_ms * 1e-3 * SR * float(g.uniform(0.9, 1.1)))
    exc = np.sin(np.pi * np.arange(w) / w)
    exc = np.concatenate([exc, np.zeros(64)])
    exc[:w] += 0.15 * g.standard_normal(w) * exc[:w]
    y = fft_convolve(exc, ir)
    k = int(0.01 * SR)
    y[-k:] *= np.linspace(1, 0, k)
    return vel * y / (np.abs(y).max() + 1e-9)


def iron_tink(vel: float, seed: int, g) -> np.ndarray:
    """A mallet on a caulking iron: a short, dry, pitched tink (A6) over a small wooden knock. Mono."""
    x = metallophone_note(n("A6") + float(g.uniform(-0.08, 0.08)), 0.5, seed=seed, decay=0.5, hardness=0.75,
                          ombak_hz=0.0, pair=False)
    return vel * x / (np.abs(x).max() + 1e-9)


def rope_creak(dur: float, f_lo: float, f_hi: float, g) -> np.ndarray:
    """Lashings under strain: stick-slip (a train of tiny slips whose rate rises and falls with the load) through
    the rope's and the block's resonances. Mono."""
    N = int(dur * SR)
    t = np.arange(N) / SR
    load = np.sin(np.pi * t / dur) ** 1.5
    rate = f_lo + (f_hi - f_lo) * load * (1 + 0.15 * np.sin(2 * np.pi * float(g.uniform(2, 5)) * t))
    ph = np.cumsum(rate) / SR
    slips = np.diff(np.floor(ph), prepend=0.0)
    slips *= g.uniform(0.5, 1.0, N)
    y = filt(slips, [bq_bandpass(float(g.uniform(780, 980)), 4.0)]) + 0.6 * filt(slips, [bq_bandpass(1850, 5.0)]) \
        + 0.8 * filt(slips, [bq_bandpass(360, 3.0)])
    return y * load / (np.abs(y).max() + 1e-9)


def lap(g) -> np.ndarray:
    """A small lap of water against a hull: a soft burst of mid-low noise, quickly gone. Mono."""
    N = int(0.4 * SR)
    t = np.arange(N) / SR
    x = filt(g.standard_normal(N), [bq_bandpass(float(g.uniform(380, 700)), 0.9), bq_lowpass(1600, 0.7)])
    env = (1 - np.exp(-t / 0.012)) * np.exp(-t / float(g.uniform(0.06, 0.12)))
    return x * env / (np.abs(x * env).max() + 1e-9)


def whistle_notes(phrase: int, a: int, b: int, transpose: int, vel: float) -> list:
    """A slice of CURRENT_SONG as kirru_whistle notes [(start, dur, midi, vel, rise)]: short notes are tongued
    apart, so the soundings are heard as two calls."""
    out, pos = [], 0.0
    for i, (m, beats) in enumerate(CURRENT_SONG[phrase]):
        d = beats * BEAT
        if a <= i < b:
            last = i == b - 1
            out.append((pos, d * (0.8 if beats <= 0.5 else 0.93) * (1.25 if last else 1.0), float(m + transpose),
                        vel * (1.0 if beats > 0.5 else 0.88), False))
        pos += d
    s0 = out[0][0]
    return [(s - s0, d, m, v, r) for s, d, m, v, r in out]


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    L = mx.L
    mx.add("sea", sea(L, SEED + 1), 0.0)
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("D2"), 1.0), (n("A2"), 0.5)], SEED + 2, partials=6,
                                     breath_s=LOOP_S / 7, tilt=0.5), 0.0)
    # the pad: one swell per run of the same chord
    bar = 1
    while bar <= BARS:
        ch = CHORDS[bar - 1]
        run = 1
        while bar + run <= BARS and CHORDS[bar + run - 1] == ch:
            run += 1
        if ch is not None:
            x = pad_chord([n(p) for p in PAD[ch].split()], run * BAR - 0.3, 0.5, seed=SEED + 100 + bar, attack=1.1,
                          release=1.6, voices=3, spread_cents=7.0, width=0.6)
            mx.add("pad", x, t_of(bar) - 0.35)
        bar += run
    # the deck-bass
    box = V.body_ir(((110.0, 8, 0.8), (230.0, 10, 0.6), (480.0, 8, 0.4), (900.0, 6, 0.2)), SEED + 7)
    for bar in sorted(BASS_BARS):
        ch = CHORDS[bar - 1]
        for beat, p, v in ((0.0, ROOTS[ch][0], 0.7), (2.0, ROOTS[ch][1], 0.5)):
            x = string_pluck(n(p) + 12, 1.6, v * float(g.uniform(0.92, 1.05)), seed=SEED + 300 + 4 * bar + int(beat),
                             pick_pos=0.2, t60=1.4, mute=0.25, B=3e-5, max_f=3000.0, release=0.2)
            mx.add("bass", fft_convolve(x, box)[: len(x) + 2000], t_of(bar, beat) + float(g.normal(0, 0.005)))
    # the mallets
    irs = {DEEP: [hull_ir(1.0, SEED + 11), hull_ir(1.06, SEED + 12)],
           MID: [hull_ir(1.75, SEED + 13), hull_ir(1.85, SEED + 14)]}
    pans = {DEEP: -0.35, MID: 0.4, IRON: 0.15}
    for i, (bar, who, e, v) in enumerate(mallet_plan()):
        vv = v * float(g.uniform(0.88, 1.06))
        if who == IRON:
            x = iron_tink(vv, SEED + 2000 + i, g)
        else:
            x = mallet(irs[who][i % 2], vv, 3.2 if who == DEEP else 2.2, g)
        mx.add(who, x, t_of(bar) + e * EIGHTH + float(g.normal(0, SCATTER)), pan=pans[who])
    # the rope: a creak on most swells, between the lift and the break
    for k in range(SWELLS):
        if g.uniform() < 0.25:
            continue
        x = rope_creak(float(g.uniform(0.6, 1.1)), float(g.uniform(30, 50)), float(g.uniform(90, 160)), g)
        mx.add("rope", x, (k + 0.35 + float(g.uniform(-0.05, 0.05))) * LOOP_S / SWELLS,
               pan=float(g.uniform(-0.7, 0.7)), gain=float(g.uniform(0.6, 1.0)))
    # laps against the hulls
    pos = float(g.uniform(0.3, 1.0))
    while pos < LOOP_S - 0.5:
        mx.add("laps", lap(g), pos, pan=float(g.uniform(-0.8, 0.8)), gain=float(g.uniform(0.4, 1.0)))
        pos += float(g.uniform(0.9, 2.6))
    # the whistlers
    for j, (bar, beat, ph, a, b, tr, who) in enumerate(FRAGMENTS):
        notes = whistle_notes(ph, a, b, tr, 0.9 if who == "near" else 0.7)
        x = V.kirru_whistle(notes, SEED + 800 + j, glide=0.035, vib_cents=12.0, breath=0.05, click=False)
        mx.add("whistle" if who == "near" else "far", x, t_of(bar, beat) - 0.02,
               pan=0.2 if who == "near" else -0.55)
    # the low string
    for bar in sorted(CELLO):
        pos = t_of(bar)
        for p, beats in CELLO[bar]:
            d = beats * BEAT
            if p is not None:
                x = pad_chord([n(p)], d * 0.97, 0.75 * float(g.uniform(0.95, 1.03)), seed=SEED + 1200 + int(pos * 10),
                              voices=3, spread_cents=4.0, attack=min(0.5, 0.3 * d), release=0.9, width=0.3)
                mx.add("cello", x, pos - 0.08)
            pos += d


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"], each bus gated where it plays), relative to
# the near whistle (0 LU): the cello -3, the pad -7, the deep mallet -8, the mid -10, the iron -13, the deck-bass -9,
# the far whistle -7, the drone -13, the sea -14, the laps -20, the rope -20 (the mallets and the rope read low on
# a loudness meter for how present they are: short strokes).
GAINS = {"whistle": 0.0, "far": -3.5, "cello": 8.5, "pad": 8.5, "deep": -1.5, "mid": -1.0, "iron": -7.0,
         "bass": -12.5, "drone": -7.0, "sea": -19.5, "laps": -17.5, "rope": -14.5}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = GAINS
    mx.bus("whistle", G["whistle"], send=0.3, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("far", G["far"], send=0.75, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(3000, 0.7)]))
    mx.bus("cello", G["cello"], send=0.35, process=lambda x: string_body(x, cutoff=1500.0))
    mx.bus("pad", G["pad"], send=0.4, process=lambda x: string_body(x, cutoff=1300.0))
    mx.bus("deep", G["deep"], send=0.3, process=lambda x: filt(x, [bq_highpass(50, 0.7)]))
    mx.bus("mid", G["mid"], send=0.3, process=lambda x: filt(x, [bq_highpass(80, 0.7)]))
    mx.bus("iron", G["iron"], send=0.35, process=lambda x: filt(x, [bq_lowpass(7000, 0.7)]))
    mx.bus("bass", G["bass"], send=0.15, process=lambda x: filt(x, [bq_lowpass(1600, 0.7), bq_peak(250, -2.0, 1.0)]))
    mx.bus("drone", G["drone"], send=0.2, process=lambda x: filt(x, [bq_lowpass(800, 0.7)]))
    mx.bus("sea", G["sea"], send=0.1)
    mx.bus("laps", G["laps"], send=0.2)
    mx.bus("rope", G["rope"], send=0.25, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    build(mx)
    air = ModFDNReverb(rt60=2.0, rt60_high=0.9, predelay=0.03, size=1.3, mod_depth=8.0, mod_rate=0.3,
                       early_level=0.2, lowcut=90.0, seed=SEED % 9973)     # open water among hulls: wide, not wet
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    return V.finish(mx, "hollowmere", out_path, BPM, BAR_BEATS, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, air, -3.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
