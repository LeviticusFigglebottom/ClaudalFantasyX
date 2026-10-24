"""`hullgnaw`: the Hullgnaw boss (M3-AUD-08; act_outline Ch1): a 2.7 s intro and a 64.0 s loop.

Original composition for this project (SPEC §2, §9). The eel's crawling bass, the rope ostinato and the flute's
theme were written for this fight and are not derived from any existing tune. The brief (act_outline Ch1):
Hullgnaw is an Undertow-spawn eel grown through the ribs of a sunken ship, fought on a breaking raft at Oruvel while
the raft-town is torn apart. It is the turn-order tutorial, so the cue has to be readable before it is heavy: one
clear pulse the player can count, one tune at a time, and nothing that fights the timeline for attention.

G minor (Aeolian, with D major as the dominant: F# is the only borrowed note, plus the Ab chord in B), 6/8 at a
dotted quarter of 90 (a bar is 1.333 s), 48 bars. Two big beats a bar, like a raft heaving on the swell; nothing in
it is in the 4/4 of the other battles.

Ensemble (all synthesized; no samples):
* the eel: a fingered bass that sits on each root and then **crawls** chromatically into the next one (from below
  when the harmony moves, from above when it stays), so the low line is always coiling;
* the raft: a muted plucked string through a small wooden body in running eighths (rope and lashings: Oruvel is a
  town of rope), and frame drums in 6/8 (the dum on 1, the slap on 4) with the big drum on each bar;
* the hull: a low gong at G1 (the ship's ribs groaning) at each section, and hard frame-drum slaps (timbers
  cracking) through the break;
* the theme: a hard-blown breath flute in G4-C6, with an open plucked counterline (two strokes a bar) when the
  theme comes back.

Form: 1-8 the timbers (drums, the eel, the rope) | 9-16 A, ending on the dominant | 17-24 A', closing on G |
25-32 B, higher (Eb, Cm, Ab, D) | 33-40 the raft breaks: the drums drop to the big drum, the gong and cracking
timbers over the eel, building back from 37 | 41-48 A'' with the counterline, a drum fill in bar 48 into the wrap.

Loop: the intro is a copy of bars 47-48 (so the splice into bar 1 carries the same tails); LOOPSTART = its length,
LOOPLENGTH = 48 bars.

Render:  python3 assets_src/music/hullgnaw.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.gongs import large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "hullgnaw.ogg")
SEED = 20261024
TARGET_LUFS = -16.0
BPM = 90.0                 # dotted quarters
BAR = 2 * 60.0 / BPM
E8 = BAR / 6
BARS = 48
LOOP_S = BARS * BAR
INTRO_BARS = 2
INTRO_S = INTRO_BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065

CHORDS = (["Gm"] * 4 + ["Eb", "Eb", "D", "D"]
          + ["Gm", "Gm", "Eb", "F", "Gm", "Gm", "D", "D"]
          + ["Gm", "Gm", "Eb", "F", "Gm", "Cm", "D", "Gm"]
          + ["Eb", "Eb", "Cm", "Cm", "Ab", "Ab", "D", "D"]
          + ["Gm"] * 4 + ["Eb", "Eb", "D", "D"]
          + ["Gm", "Gm", "Eb", "F", "Gm", "Cm", "D", "Gm"])
SECTION = ["I"] * 8 + ["A"] * 8 + ["A1"] * 8 + ["B"] * 8 + ["X"] * 8 + ["A2"] * 8
ROOTS = {"Gm": "G1", "Eb": "Eb2", "D": "D2", "F": "F2", "Cm": "C2", "Ab": "Ab1"}
## the rope's chord tones (root, third, fifth, octave) and the counterline's two notes a bar
TONES = {"Gm": ["G3", "Bb3", "D4", "G4"], "Eb": ["Eb3", "G3", "Bb3", "Eb4"], "D": ["D3", "F#3", "A3", "D4"],
         "F": ["F3", "A3", "C4", "F4"], "Cm": ["C3", "Eb3", "G3", "C4"], "Ab": ["Ab2", "C3", "Eb3", "Ab3"]}
ROPE = [0, 2, 3, 2, 1, 2]                 # indices into TONES, one per eighth
COUNTER = {"Gm": ("Bb4", "D5"), "Eb": ("G4", "Bb4"), "D": ("F#4", "A4"), "F": ("A4", "C5"), "Cm": ("Eb4", "G4"),
           "Ab": ("C5", "Eb5")}

## the theme, (pitch, eighths) per bar
THEME_A = [[("G4", 3), ("A4", 1), ("Bb4", 2)], [("D5", 4), ("C5", 1), ("Bb4", 1)],
           [("Bb4", 2), ("C5", 1), ("Eb5", 3)], [("D5", 3), ("C5", 2), ("A4", 1)],
           [("G4", 3), ("Bb4", 1), ("D5", 2)], [("G5", 4), ("F5", 1), ("Eb5", 1)],
           [("D5", 3), ("C5", 2), ("Bb4", 1)], [("A4", 5), (None, 1)]]
THEME_A1 = THEME_A[:6] + [[("D5", 2), ("C5", 1), ("A4", 2), ("F#4", 1)], [("G4", 5), (None, 1)]]
THEME_B = [[("G5", 3), ("F5", 1), ("Eb5", 2)], [("Bb5", 4), ("G5", 2)],
           [("C6", 3), ("Bb5", 1), ("G5", 2)], [("Eb5", 5), (None, 1)],
           [("C6", 2), ("Bb5", 1), ("Ab5", 3)], [("Eb5", 3), ("F5", 1), ("G5", 2)],
           [("A5", 3), ("G5", 1), ("F#5", 2)], [("D5", 5), (None, 1)]]


def t_of(bar: int, eighth: float = 0.0) -> float:
    return (bar - 1) * BAR + eighth * E8


class Placer:
    """Adds each loop event, and a copy of every event that sounds in the loop's last INTRO_BARS bars (including the
    tails of earlier ones) to the intro, at the same place relative to the loop end."""

    def __init__(self, mx: LoopMixer):
        self.mx = mx
        self.win = LOOP_S - INTRO_S

    def __call__(self, bus: str, x: np.ndarray, t: float, pan: float = 0.0) -> None:
        self.mx.add(bus, x, t, pan=pan)
        tm = t % LOOP_S
        # (an event humanized up to 50 ms before bar 1 is already in the mixer's cold copy of the loop start)
        if tm + x.shape[0] / SR > self.win and not -0.05 <= t < 0.0:
            self.mx.add(bus, x, tm - self.win, pan=pan, part="intro")


def wood_body(seed: int, sr: int = SR) -> np.ndarray:
    """A small wooden box (a few damped modes and a click) as an impulse response: the rope's block and the raft."""
    g = rng(seed)
    t = np.arange(int(0.2 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((130.0, 10, 0.8), (240.0, 12, 0.6), (450.0, 9, 0.4), (820.0, 7, 0.25), (1900.0, 4, 0.12)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * 0.08
    return ir / np.abs(ir).max()


def eel_line(bar: int) -> list[tuple[float, float, float]]:
    """The bass in one bar: (midi, start eighth, length in eighths). The root, then a crawl into the next root."""
    r = n(ROOTS[CHORDS[bar - 1]])
    r2 = n(ROOTS[CHORDS[bar % BARS]])
    if abs(r2 - r) > 6:
        r2 += -12 if r2 > r else 12
    if r2 == r:                      # the harmony stays: coil down from above
        crawl = [r + 3, r + 2, r + 1]
    else:                            # it moves: slither up (or down) into the next root
        s = 1 if r2 > r else -1
        crawl = [r2 - 3 * s, r2 - 2 * s, r2 - s]
    return [(r, 0, 2.6), (r + 12, 2, 0.8)] + [(m, 3 + i, 1.05) for i, m in enumerate(crawl)]


def add_theme(place: Placer, bars: list, start_bar: int, seed: int, vel: float, pan: float = -0.1) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, e in bar:
            d = e * E8
            if p is None:
                pos += d
                first = True
                continue
            x = breath_flute(n(p), d * 0.93 + 0.02, vel * g.uniform(0.94, 1.04), seed=seed + int(round(pos * 1000)),
                             breath=0.52, scoop_cents=35.0 if first or e >= 3 else 10.0,
                             vib_cents=9.0 if e >= 3 else 0.0, vib_rate=5.2, swell=0.2 if e >= 4 else 0.0,
                             attack=0.03, release=0.14, beta=0.6)
            place("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.003)), pan=pan)
            pos += d
            first = False


def build(mx: LoopMixer) -> None:
    place = Placer(mx)
    g = rng(SEED)
    body = wood_body(SEED + 5)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        broken = sec == "X"
        # the eel
        for m, e, ln in eel_line(bar):
            v = (0.85 if e == 0 else 0.6) * g.uniform(0.93, 1.05)
            place("bass", bass_note(m, ln * E8, v, seed=SEED + 100 * bar + int(e), mute=0.25),
                  t_of(bar, e) + 0.003)
        # the rope
        if not broken or bar >= 37 or bar % 2 == 1:
            for e, k in enumerate(ROPE):
                v = (0.5 if e in (0, 3) else 0.36) * g.uniform(0.9, 1.06)
                x = string_pluck(n(TONES[ch][k]), E8 * 1.6, v, seed=SEED + 20000 + 10 * bar + e, pick_pos=0.16,
                                 t60=1.6, mute=0.55, max_f=5000.0, release=0.04)
                place("rope", fft_convolve(x, body)[: len(x) + 3000], t_of(bar, e) + float(g.normal(0, 0.004)),
                      pan=0.25 if e % 2 else 0.12)
        # drums: the dum on 1, the slap on 4, teks and ghosts between; the big drum on each bar
        if not broken or bar >= 37:
            lvl = 0.85 if sec == "I" else 1.0
            for e, (stroke, v) in enumerate((("dum", 0.9), ("ghost", 0.35), ("tek", 0.5), ("slap", 0.8),
                                              ("ghost", 0.35), ("tek", 0.5))):
                place("drums", frame_drum(stroke, lvl * v * g.uniform(0.9, 1.06), variant=bar * 6 + e, seed=SEED + 3),
                      t_of(bar, e) + float(g.normal(0, 0.003)), pan=-0.1 if stroke in ("tek", "ghost") else 0.0)
            place("big", big_drum(0.8 * lvl, variant=bar, seed=SEED + 4), t_of(bar))
            if sec in ("B", "A2"):
                place("big", big_drum(0.55, variant=bar + 2, seed=SEED + 4), t_of(bar, 3))
        else:
            place("big", big_drum(0.75, variant=bar, seed=SEED + 4), t_of(bar))
            # timbers cracking: hard slaps, a different beat each bar
            for e in ((2, 5) if bar % 2 else (1, 4.5)):
                place("drums", frame_drum("slap", 0.85 * g.uniform(0.9, 1.05), size=0.7, variant=bar + int(e),
                                          seed=SEED + 8), t_of(bar, e), pan=0.35 if bar % 2 else -0.35)
        if bar in (39, 40):
            for e in (3, 4, 5):
                place("big", big_drum(0.5 + 0.1 * e - 0.3, variant=bar * 3 + e, seed=SEED + 4), t_of(bar, e))
        if bar == 48:
            for k, e in enumerate((3, 3.5, 4, 4.5, 5, 5.5)):
                place("drums", frame_drum("slap" if k % 2 else "dum", 0.55 + 0.07 * k, variant=k, seed=SEED + 6),
                      t_of(bar, e), pan=0.05)
        # the counterline (A', A'')
        if sec in ("A1", "A2"):
            for k, e in enumerate((0, 3)):
                x = string_pluck(n(COUNTER[ch][k]), 3 * E8, 0.5 * g.uniform(0.94, 1.04),
                                 seed=SEED + 30000 + 10 * bar + k,
                                 pick_pos=0.12, t60=2.4, mute=0.0, max_f=6000.0, release=0.1)
                place("counter", fft_convolve(x, body)[: len(x) + 3000], t_of(bar, e) + 0.006, pan=0.4)
    # the hull groaning
    for bar, v in ((1, 0.6), (25, 0.55), (33, 0.75), (37, 0.5), (41, 0.6)):
        place("gong", large_gong(n("G1"), v, seed=SEED + 80 + bar, t60=6.0), t_of(bar))
    add_theme(place, THEME_A, 9, SEED + 100, 0.85)
    add_theme(place, THEME_A1, 17, SEED + 200, 0.85)
    add_theme(place, THEME_B, 25, SEED + 300, 0.9)
    add_theme(place, THEME_A1, 41, SEED + 400, 0.9)


## Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
## flute (0 LU, measured over the loop; it plays 32 of the 48 bars): drums -6, the big drum -8, the eel -5, the
## rope -9, the counterline -9 (it plays 16 bars), the gong -14. The tutorial rule: the drums and the eel carry the
## pulse, but the tune is always the loudest thing when it plays.
GAINS = {"flute": 0.0, "drums": -2.7, "big": -5.5, "bass": -2.8, "rope": -9.5, "counter": -2.1, "gong": -13.5}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=INTRO_S, loop_s=LOOP_S, intro_tail_s=6.0, preroll_s=8.0)
    mx.bus("flute", GAINS["flute"], send=0.22, process=lambda x: filt(x, [bq_highpass(220, 0.7),
                                                                          bq_peak(2200, 2.5, 1.0)]))
    mx.bus("drums", GAINS["drums"], send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7),
                                                                          bq_peak(4000, 1.5, 0.8)]))
    mx.bus("big", GAINS["big"], send=0.15, process=lambda x: filt(x, [bq_highpass(30, 0.7)]))
    mx.bus("bass", GAINS["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(90, 2.0, 0.9),
                                                                       bq_lowpass(3000, 0.7)]))
    mx.bus("rope", GAINS["rope"], send=0.15, process=lambda x: filt(x, [bq_highpass(140, 0.7),
                                                                        bq_lowpass(4500, 0.7)]))
    mx.bus("counter", GAINS["counter"], send=0.28, process=lambda x: filt(x, [bq_highpass(160, 0.7)]))
    mx.bus("gong", GAINS["gong"], send=0.45)
    build(mx)
    room = ModFDNReverb(rt60=1.6, rt60_high=0.7, predelay=0.016, size=0.85, mod_depth=8.0, mod_rate=0.6,
                        early_level=0.35, seed=SEED % 9973)
    intro, loop = mx.render(reverb=room, reverb_return_db=-3.0)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    write_ogg(out_path, y, quality=3.0, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 2,
                       extra={"intro_bars": INTRO_BARS, "loop_bars": BARS, "meter": "6/8"})
    m = measure(y)
    if stats is not None:
        stats["splice_residual_db"] = mx.splice_residual_db
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"hullgnaw: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  loop {S}+{L}  splice {mx.splice_residual_db:.1f} dB  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
