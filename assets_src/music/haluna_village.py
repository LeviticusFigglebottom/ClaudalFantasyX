"""`haluna_village`: Haluna by day (M2-AUD-03; vertical_slice.md B02, B03, B05): a 75 s seamless town loop.

Original composition for this project (SPEC §2, §9); the material is in haluna_theme.py (see its docstring for
the melody's design and why it never resolves). 6/8 at 64 dotted-quarter beats per minute (a bar is 1.875 s).

Ensemble (all synthesized; no samples):
* breath flute: the tune (synth.winds), breathy, with small scoops into phrase starts and swells on long notes;
* two interlocking metallophones (each plays every other eighth; only together are they the figure), panned apart,
  hand-damped so the figure stays clear; a low metallophone on the chord roots;
* a plucked lute (synth.electric.string_pluck through a small wooden body) arpeggiating the chords;
* a soft fingered bass; frame drums in a rolling 6/8 (dum, ghost, tek), jingles in the festival (B) section;
* kettle gongs on the phrase ends, a large gong softly at the loop's start and at the B section.

Form (bars): 1-4 the town (no tune) | 5-12 A | 13-20 A' (a metallophone echo answers the flute) | 21-28 B (the
festival: higher, jingles) | 29-36 A | 37-40 the flute's first cell once more, low, and the harmony turns home
(G A G A) into bar 1's D.

Render:  python3 assets_src/music/haluna_village.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum, jingle  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("haluna_theme", os.path.join(os.path.dirname(__file__), "haluna_theme.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

OUT = os.path.join(ROOT, "assets", "audio", "music", "haluna_village.ogg")
SEED = 20261104
TARGET_LUFS = -16.0
BPM = 64.0                      # dotted quarters
E8 = 60.0 / BPM / 3.0           # one eighth (s)
BAR = 6 * E8
BARS = 40
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065

INTRO_CHORDS = ["D", "D", "G", "A"]
TAIL_CHORDS = ["G", "A", "G", "A"]
CHORDS = INTRO_CHORDS + T.CHORDS_A + T.CHORDS_A2 + T.CHORDS_B + T.CHORDS_A + TAIL_CHORDS
SECTION = ["I"] * 4 + ["A"] * 8 + ["A2"] * 8 + ["B"] * 8 + ["A3"] * 8 + ["T"] * 4
TAIL_CELL = [("F#4", 2), ("E4", 1), ("D4", 2), ("E4", 1), ("F#4", 3), ("A4", 3), ("E4", 6), (None, 6)]


def bar_t(bar: int, eighth: float = 0.0) -> float:
    """Start time (s) of `eighth` in 1-based `bar`."""
    return (bar - 1) * BAR + eighth * E8


def lute_body(seed: int, sr: int = SR) -> np.ndarray:
    """A small wooden body: a few damped modes (air, top, back) and a bright click, as an impulse response."""
    g = rng(seed)
    t = np.arange(int(0.25 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((105.0, 12, 0.9), (205.0, 14, 0.7), (390.0, 10, 0.45), (560.0, 9, 0.3), (1100.0, 6, 0.2),
                    (2400.0, 4, 0.12)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * 0.08
    return ir / np.abs(ir).max()


def _human(g, t: float, eighth: int) -> float:
    """Micro-timing: a small spread, and the 6/8 lilt (the middle eighth of each group a touch late)."""
    lilt = 0.010 if eighth % 3 == 1 else 0.0
    return t + lilt + float(g.normal(0.0, 0.005))


def add_flute(mx: LoopMixer, notes: list, start: float, seed: int, vel: float, pan: float, bus: str = "flute",
              octave: int = 0) -> None:
    g = rng(seed)
    t = start
    first = True
    for i, (p, d) in enumerate(notes):
        dur = d * E8
        if p is None:
            t += dur
            first = True
            continue
        v = vel * g.uniform(0.92, 1.05) * (1.06 if d >= 3 else 1.0)
        x = breath_flute(n(p) + 12 * octave, dur * 0.97 + 0.04, v, seed=seed + 7 * i, breath=0.32,
                         scoop_cents=55.0 if first else 18.0, vib_cents=12.0 if d >= 3 else 6.0, vib_rate=4.8,
                         swell=0.28 if d >= 5 else 0.0, attack=0.07 if first else 0.035, release=0.30)
        mx.add(bus, x, t - FLUTE_PRE + float(g.normal(0, 0.004)), pan=pan)
        t += dur
        first = False


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = lute_body(SEED + 5)
    for bar, (chord, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        tones = T.CHORD_TONES[chord]
        full = sec in ("A2", "B", "A3")
        # interlocking metallophones
        for e in range(6):
            p = tones[T.INTERLOCK[e]]
            accent = 1.15 if e in (0, 3) else 1.0
            v = (0.30 if sec != "I" else 0.26) * accent * g.uniform(0.9, 1.05)
            x = metallophone_note(n(p), v, seed=SEED + 100 * bar + e, decay=2.4, hardness=0.35, ombak_hz=5.2,
                                  damp_at=E8 * 2.2)
            mx.add("metal", x, _human(g, bar_t(bar, e), e), pan=-0.38 if e % 2 == 0 else 0.38)
        # low metallophone on the root (twice a bar in the fuller sections)
        root = n(T.BASS[chord]) + 24
        for e in ((0, 3) if full else (0,)):
            x = metallophone_note(root, 0.34 if e == 0 else 0.24, seed=SEED + 9000 + 10 * bar + e, decay=4.0,
                                  hardness=0.25, ombak_hz=3.8)
            mx.add("lowmetal", x, bar_t(bar, e), pan=0.05)
        # lute arpeggio through the body
        lute = T.LUTE[chord]
        for e, k in enumerate([0, 1, 2, 3, 2, 1]):
            v = (0.42 if e in (0, 3) else 0.32) * g.uniform(0.9, 1.05)
            x = string_pluck(n(lute[k]), E8 * 2.5, v, seed=SEED + 20000 + 10 * bar + e, pick_pos=0.18, t60=2.2,
                             max_f=5000.0, release=0.12)
            mx.add("lute", fft_convolve(x, body)[: len(x) + 4000], _human(g, bar_t(bar, e), e), pan=0.18)
        # bass
        if sec != "I" or bar >= 3:
            for e, v in ((0, 0.55), (3, 0.38)):
                x = bass_note(n(T.BASS[chord]), E8 * 2.4, v, seed=SEED + 30000 + 10 * bar + e, mute=0.3)
                mx.add("bass", x, bar_t(bar, e) + 0.004, pan=0.0)
        # frame drums: a rolling 6/8 (dum ghost tek | dum ghost tek), the festival adds slaps and jingles
        pattern = [("dum", 0.55), ("ghost", 0.18), ("tek", 0.34), ("dum", 0.36), ("tek", 0.30), ("ghost", 0.16)]
        if sec == "B":
            pattern[3] = ("slap", 0.40)
        if sec == "I" and bar < 3:
            pattern = [("dum", 0.45), (None, 0), (None, 0), ("tek", 0.26), (None, 0), (None, 0)]
        for e, (stroke, v) in enumerate(pattern):
            if stroke is None:
                continue
            x = frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=bar * 6 + e, seed=SEED + 1)
            mx.add("drums", x, _human(g, bar_t(bar, e), e), pan=-0.12 if stroke == "tek" else 0.08)
        if sec == "B":
            for e in range(6):
                x = jingle(0.32 if e in (0, 3) else 0.18, variant=bar + e, open_=(e == 0), seed=SEED + 2)
                mx.add("drums", x, _human(g, bar_t(bar, e), e), pan=0.45)
    # gongs: kettle gongs on the phrase ends, a large gong at the loop start and the festival
    for bar in (4, 8, 12, 16, 20, 24, 28, 32, 36, 40):
        p = "A4" if CHORDS[bar - 1].startswith("A") else "D5"
        mx.add("gong", kettle_gong(n(p), 0.30, seed=SEED + 400 + bar, t60=2.2), bar_t(bar), pan=0.3)
    for bar, v in ((1, 0.28), (21, 0.36)):
        mx.add("gong", large_gong(n("D2"), v, seed=SEED + 500 + bar, t60=8.0), bar_t(bar), pan=-0.1)
    # the tune
    add_flute(mx, T.notes_in_order([T.PHRASE_A]), bar_t(5), SEED + 600, 0.50, -0.05)
    add_flute(mx, T.notes_in_order([T.phrase_a2()]), bar_t(13), SEED + 700, 0.50, -0.05)
    add_flute(mx, T.notes_in_order([T.PHRASE_B]), bar_t(21), SEED + 800, 0.55, -0.05)
    add_flute(mx, T.notes_in_order([T.PHRASE_A]), bar_t(29), SEED + 900, 0.52, -0.05)
    add_flute(mx, TAIL_CELL, bar_t(37), SEED + 950, 0.40, 0.1)
    # A': the metallophone answers the flute's held notes an octave up (bars 16 and 20)
    for bar, cell in ((16, ["E6", "D6", "B5"]), (20, ["A5", "B5", "D6"])):
        for i, p in enumerate(cell):
            x = metallophone_note(n(p), 0.26, seed=SEED + 1200 + 10 * bar + i, decay=3.0, hardness=0.4, ombak_hz=6.0)
            mx.add("metal", x, bar_t(bar, 1 + 1.5 * i), pan=0.55)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# flute: lute -9 LU, metallophones -7, low metallophone -10, bass -10, drums -8, gongs -14.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=6.0)
    mx.bus("flute", 0.0, send=0.30, process=lambda x: filt(x, [bq_peak(2600, 1.5, 1.0)]))
    mx.bus("metal", -0.8, send=0.38)
    mx.bus("lowmetal", -0.4, send=0.35)
    mx.bus("lute", -20.9, send=0.22, process=lambda x: filt(x, [bq_highpass(80, 0.7), bq_lowpass(5500, 0.7)]))
    mx.bus("bass", -2.6, send=0.05, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("drums", -1.6, send=0.18)
    mx.bus("gong", -12.1, send=0.40)
    build(mx)
    hall = ModFDNReverb(rt60=1.8, rt60_high=1.0, predelay=0.018, size=0.9, mod_depth=8.0, mod_rate=0.6,
                        early_level=0.30, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM * 3 / 2, 2)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"haluna_village: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
