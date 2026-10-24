"""`tamsule`: Ch7, Tamsule port, the town of the Tamsule Bell (M3-AUD-12; act_outline.md Ch7): a 70 s seamless loop.

Original composition for this project (SPEC §2, §9): the tune, its harmony and every part below were written for this
cue. It evokes a busy harbour-market style (a hammered string over a running pluck in an uneven metre) and quotes no
existing tune or folk melody. The one borrowed phrase is our own: the B section re-bars the first phrase of the
Tidecup's song (tidecup_match.py, SONG_A) into this cue's metre, and the arena's bell is the Tidecup's Tamsule Bell
(synth.bells.tower_bell, prime A2, dark 0.35, the same colour), so the town and its arena share a voice.

Tamsule is the Reefball town: crowded, trading, lit by glimmer-tech lamps nobody questions (Liss notes aloud that the
Bell is glimmer-tech, and nobody answers). Oruvel's side has been here a week, waiting for news that is about to
arrive. So the town is bright and busy, and its middle eight bars are the Oruvel side's waiting: the Tidecup's song,
slow, over a heartbeat.

How it stays apart from Haluna (D pentatonic, 6/8, breath flute and interlocking metallophones) and Oruvel (G
mixolydian, swung 4/4, a squeezebox and an oom-pah):
* A dorian (the raised sixth, F#, is the glimmer-light's colour; B borrows F and E major from the Tidecup);
* **7/8**, grouped 2+2+3, a quaver every 0.25 s (a bar is 1.75 s): a market's uneven, hurrying step;
* the lead is a **hammered dulcimer** (three wire strings per course struck together by a light hammer, a long
  ring through a broad thin soundboard; long notes are re-struck as a soft tremolo roll, as the instrument does);
* a **running pluck** (a low, dark-bodied lute) plays every quaver in the 2+2+3 shape; a fingered bass on each group;
* frame drums on the groups; jingles in A' (the market at its fullest);
* glimmer-tech: the lamps' **hum** (a soft, slowly pulsing pair of high tones, never quite steady) and **glass** bars
  that double the tune's long notes an octave up in A';
* the harbour: rigging tinks (a halyard's shackle on a mast), and the Tamsule Bell at the loop's start and,
  softly, at B.

Form (bars): 1-4 the port (the pluck, the hum, the Bell) | 5-12 A, the tune | 13-20 A', with the glass and jingles
| 21-28 B, the Oruvel side waiting: the Tidecup's phrase in long rolled notes, the drums down to a heartbeat | 29-36
A | 37-40 the tune's head once more, and an E major turnaround back into bar 1's A minor.

Render:  python3 assets_src/music/tamsule.py   (or tools/audio/render_all.py --only tamsule)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.drums import frame_drum, jingle  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

_spec = importlib.util.spec_from_file_location("field_ambience", os.path.join(ROOT, "assets_src", "sfx",
                                                                              "field_ambience.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

OUT = os.path.join(ROOT, "assets", "audio", "music", "tamsule.ogg")
SEED = 20261220
TARGET_LUFS = -16.0
EIGHTH = 0.25                 # one quaver (s); the sidecar's bpm counts quavers
BPM = 60.0 / EIGHTH
BAR_EIGHTHS = 7               # 7/8, grouped 2+2+3
GROUPS = (0, 2, 4)            # group starts (quavers)
BAR = BAR_EIGHTHS * EIGHTH
BARS = 40
LOOP_S = BARS * BAR
BELL_PRIME = "A2"             # the Tamsule Bell (tidecup_match.py)
# Bar 1 starts this far into the file, so the wrap falls inside bar 40's running pluck, half a quaver from any
# attack. On bar 1's downbeat (the Bell, drum, bass and pluck at once after the tag's rest) and on any quaver onset
# the seam check's spectral flux measured 6-7x the median; between quavers it is under 1x.
DOWNBEAT_OFFSET_S = 2.5 * EIGHTH    # the wrap sits between two quavers (bar 40, after its third group's first)
ROLL_MIN = 3               # notes this many quavers or longer are rolled (re-struck every quaver, softer)

CHORDS = (["Am", "Am", "D", "Am"]
          + ["Am", "D", "Am", "G", "C", "D", "Em", "Am"]
          + ["Am", "D", "Am", "G", "C", "G", "D", "Am"]
          + ["Am", "F", "C", "G", "Am", "F", "E", "E"]
          + ["Am", "D", "Am", "G", "C", "D", "Em", "Am"]
          + ["Am", "D", "G", "E"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["A2"] * 8 + ["B"] * 8 + ["A3"] * 8 + ["T"] * 4
ROOTS = {"Am": "A1", "D": "D2", "G": "G1", "C": "C2", "Em": "E2", "F": "F1", "E": "E1"}
# the running pluck's chord tones: (root, fifth, octave, third) in a low-mid register
TONES = {"Am": ["A2", "E3", "A3", "C4"], "D": ["D3", "A3", "D4", "F#4"], "G": ["G2", "D3", "G3", "B3"],
         "C": ["C3", "G3", "C4", "E4"], "Em": ["E3", "B3", "E4", "G4"], "F": ["F2", "C3", "F3", "A3"],
         "E": ["E3", "B3", "E4", "G#4"]}
RUN = [0, 2, 1, 2, 0, 3, 2]   # indices into TONES per quaver: 2 + 2 + 3

# The tune, one list per 7/8 bar of (pitch | None, quavers).
TUNE_A = [
    [("E5", 2), ("A5", 2), ("G5", 1), ("E5", 2)],
    [("F#5", 2), ("E5", 2), ("D5", 3)],
    [("C5", 2), ("E5", 2), ("A4", 3)],
    [("B4", 2), ("D5", 2), ("G5", 1), ("F#5", 1), ("D5", 1)],
    [("E5", 2), ("G5", 2), ("C6", 3)],
    [("B5", 2), ("A5", 2), ("F#5", 3)],
    [("G5", 2), ("E5", 1), ("D5", 1), ("B4", 3)],
    [("A4", 4), (None, 3)],
]
TUNE_A2_END = [
    [("A5", 2), ("F#5", 1), ("E5", 1), ("D5", 3)],
    [("A4", 2), ("E5", 2), ("A5", 3)],
]
# B: the Tidecup song's first phrase (tidecup_match.SONG_A, bars 1-6) re-barred into 7/8, then its own close.
TUNE_B = [
    [("A4", 4), ("C5", 2), ("B4", 1)],
    [("A4", 5), ("G4", 1), ("F4", 1)],
    [("E4", 3), ("G4", 1), ("C5", 3)],
    [("B4", 7)],
    [("C5", 3), ("D5", 1), ("E5", 3)],
    [("F5", 2), ("E5", 2), ("C5", 3)],
    [("B4", 2), ("C5", 2), ("B4", 1), ("G#4", 2)],
    [("B4", 7)],
]
TAG = [
    [("E5", 2), ("A5", 2), ("G5", 1), ("E5", 2)],
    [("F#5", 2), ("D5", 2), ("A4", 3)],
    [("B4", 2), ("D5", 2), ("G4", 3)],
    [(None, 7)],
]


def t_of(bar: int, eighth: float = 0.0) -> float:
    """Start time (s) of quaver `eighth` (0-based) in 1-based `bar`."""
    return (bar - 1) * BAR + eighth * EIGHTH + DOWNBEAT_OFFSET_S


def board_ir(seed: int, sr: int = SR) -> np.ndarray:
    """The dulcimer's broad, thin soundboard: low, lightly damped plate modes and a bright bridge ring."""
    g = rng(seed)
    t = np.arange(int(0.3 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((150.0, 14, 0.6), (285.0, 16, 0.6), (470.0, 14, 0.5), (760.0, 12, 0.4), (1180.0, 10, 0.3),
                    (2100.0, 8, 0.25), (3600.0, 6, 0.15)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * 0.07
    return ir / np.abs(ir).max()


def lute_ir(seed: int, sr: int = SR) -> np.ndarray:
    """A deep round-backed body for the running pluck: darker and woodier than the dulcimer's board."""
    g = rng(seed)
    t = np.arange(int(0.2 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((105.0, 10, 0.9), (210.0, 12, 0.7), (380.0, 10, 0.4), (620.0, 8, 0.25), (1150.0, 6, 0.12)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * 0.09
    return ir / np.abs(ir).max()


def dulcimer(m: float, vel: float, seed: int, board: np.ndarray, ring: float = 1.6) -> np.ndarray:
    """One hammer stroke on a course of three wire strings a few cents apart (they beat as the note rings). The
    light hammer strikes near the bridge (pick_pos 0.07), so the attack is bright and the ring long. Mono."""
    g = rng(seed)
    out = None
    for j, cents in enumerate((0.0, 3.5, -2.5)):
        x = string_pluck(m + cents / 100.0, ring, vel * (1.0, 0.8, 0.7)[j], seed=seed + 7 * j, pick_pos=0.07,
                         t60=2.6, B=1.1e-4, max_f=9000.0, release=0.25)
        k = int(float(g.uniform(0.0, 0.0015)) * SR)
        y = np.zeros(len(x) + k)
        y[k:] = x
        out = y if out is None else (np.pad(out, (0, max(0, len(y) - len(out))))
                                     + np.pad(y, (0, max(0, len(out) - len(y)))))
    return fft_convolve(out, board)[: len(out) + 4000]


def lamp_hum(length: float, g, sr: int = SR) -> np.ndarray:
    """The glimmer-lamps: two high tones (E6 and A6, each a detuned pair) whose level pulses slowly and unevenly,
    like a machine running on something that is not quite steady. Stereo, exactly `length` long (wraps in the loop
    because every rate is a whole number of cycles per loop)."""
    N = int(round(length * sr))
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    for k, (p, lvl) in enumerate((("E6", 1.0), ("A6", 0.7), ("E7", 0.2))):
        f0 = midi_to_hz(n(p))
        # whole cycles per loop: the hum wraps without a seam
        f_a = round(f0 * length) / length
        f_b = round((f0 + 0.6 + 0.3 * k) * length) / length
        puls = 0.6 + 0.4 * np.sin(2 * np.pi * (round(0.35 * length + k) / length) * t + g.uniform(0, 6.28))
        s = lvl * puls * (np.sin(2 * np.pi * f_a * t + g.uniform(0, 6.28))
                          + 0.8 * np.sin(2 * np.pi * f_b * t + g.uniform(0, 6.28)))
        out[:, k % 2] += s
        out[:, 1 - k % 2] += 0.6 * s
    return out * 0.02


def tink(g, vel: float) -> np.ndarray:
    """A halyard's shackle against a metal mast: a small, high, ringing hit with a click."""
    b = float(g.uniform(0.92, 1.08))
    return vel * FA.modal([2350 * b, 3870 * b, 5600 * b, 7900 * b], [0.25, 0.14, 0.08, 0.04], [1.0, 0.6, 0.35, 0.15],
                          0.6, g, click=0.4)


def add_tune(mx: LoopMixer, bus: str, bars: list, start_bar: int, g, board, vel: float, pan: float,
             glass: bool = False) -> None:
    for i, bar_notes in enumerate(bars):
        pos = 0
        for p, d in bar_notes:
            if p is not None:
                m = n(p)
                t0 = t_of(start_bar + i, pos)
                accent = 1.08 if pos in GROUPS else 1.0
                v = vel * accent * float(g.uniform(0.94, 1.04))
                strokes = d if d >= ROLL_MIN else 1          # long notes: a soft roll, one stroke a quaver
                for s in range(strokes):
                    vs = v if s == 0 else v * (0.5 - 0.04 * min(s, 4)) * float(g.uniform(0.9, 1.05))
                    x = dulcimer(m, vs, int(g.integers(1 << 30)), board)
                    mx.add(bus, x, t0 + s * EIGHTH + float(g.normal(0, 0.004)), pan=pan + (0.08 if s % 2 else 0.0))
                if glass and d >= 2:
                    y = metallophone_note(m + 12, 0.28, seed=int(g.integers(1 << 30)), decay=3.0, hardness=0.16,
                                          ombak_hz=3.0)
                    mx.add("glass", y, t0 + 0.012, pan=0.45)
            pos += d


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    board = board_ir(SEED + 3)
    body = lute_ir(SEED + 5)
    for bar, (chord, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        tones = TONES[chord]
        quiet = sec == "B"
        for e, k in enumerate(RUN):                          # the running pluck, every quaver
            if quiet and e not in GROUPS:
                continue
            v = (0.5 if e in GROUPS else 0.36) * float(g.uniform(0.9, 1.05)) * (0.8 if quiet else 1.0)
            x = string_pluck(n(tones[k]), EIGHTH * 1.7, v, seed=SEED + 20000 + 10 * bar + e, pick_pos=0.2, t60=1.4,
                             mute=0.3, max_f=4500.0, release=0.05)
            mx.add("pluck", fft_convolve(x, body)[: len(x) + 3000], t_of(bar, e) + float(g.normal(0, 0.004)),
                   pan=-0.25 if e % 2 else -0.15)
        root = n(ROOTS[chord])
        if not (sec == "I" and bar <= 2):                    # bass on each group: root, root, fifth
            for e, m, vb in ((0, root, 0.55), (2, root + 12, 0.38), (4, root + 7, 0.42)):
                if quiet and e == 2:
                    continue
                d = (2 if e < 4 else 3) * EIGHTH * 0.9
                x = bass_note(m, d, vb * float(g.uniform(0.94, 1.04)), seed=SEED + 30000 + 10 * bar + e, mute=0.25)
                mx.add("bass", x, t_of(bar, e) + 0.004, pan=0.0)
        # drums: dum on the first group, tek on the second, dum + slap on the long third; B a heartbeat only
        if quiet:
            hits = [(0, "dum", 0.4), (4, "dum", 0.28)]
        elif sec == "I":
            hits = [(0, "dum", 0.42), (4, "dum", 0.32), (6, "ghost", 0.14)]
        else:
            hits = [(0, "dum", 0.52), (1, "ghost", 0.15), (2, "tek", 0.3), (3, "ghost", 0.14), (4, "dum", 0.42),
                    (5, "tek", 0.22), (6, "slap", 0.32)]
        if bar == 20 or bar == 36:                           # a short roll at a section's end
            hits += [(5.5, "tek", 0.2), (6.5, "tek", 0.24)]
        for e, stroke, v in hits:
            x = frame_drum(stroke, v * float(g.uniform(0.9, 1.07)), variant=int(bar * 8 + 2 * e), seed=SEED + 2)
            mx.add("drums", x, t_of(bar, e) + float(g.normal(0, 0.004)), pan=-0.1 if stroke == "tek" else 0.1)
        if sec == "A2":                                      # the market at its fullest
            for e in (1, 3, 5, 6):
                x = jingle(0.24 if e == 6 else 0.17, variant=bar + e, open_=(e == 6), seed=SEED + 4)
                mx.add("drums", x, t_of(bar, e) + float(g.normal(0, 0.003)), pan=0.4)
    # the tune
    add_tune(mx, "dulcimer", TUNE_A, 5, g, board, 0.62, 0.08)
    add_tune(mx, "dulcimer", TUNE_A[:6] + TUNE_A2_END, 13, g, board, 0.64, 0.08, glass=True)
    add_tune(mx, "dulcimer", TUNE_B, 21, g, board, 0.5, 0.05)
    add_tune(mx, "dulcimer", TUNE_A, 29, g, board, 0.64, 0.08)
    add_tune(mx, "dulcimer", TAG, 37, g, board, 0.52, 0.1)
    # the glass alone over the port at the loop's start (the lamps catching)
    for i, (p, bar, e) in enumerate((("A6", 2, 0), ("E6", 2, 4), ("F#6", 3, 2), ("E6", 4, 0))):
        x = metallophone_note(n(p), 0.22, seed=SEED + 1300 + i, decay=3.4, hardness=0.15, ombak_hz=2.5)
        mx.add("glass", x, t_of(bar, e), pan=0.5 - 0.25 * (i % 2))
    # the Tamsule Bell: the loop's start, and softly at B
    for bar, v in ((1, 0.62), (21, 0.42)):
        mx.add("bell", tower_bell(n(BELL_PRIME), v, seed=SEED + 400 + bar, t60=8.5, dark=0.35), t_of(bar), pan=-0.1)
    # the lamps' hum, the whole loop
    mx.add("hum", lamp_hum(LOOP_S, rng(SEED + 7)), 0.0)
    # rigging: a few tinks, never on the beat
    for k in range(14):
        t = float(g.uniform(0.0, LOOP_S))
        mx.add("rigging", tink(g, float(g.uniform(0.4, 1.0))), t, pan=float(g.uniform(0.3, 0.8)) * (1 if k % 2 else -1))


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], whole-loop gated integrated) for these
# levels relative to the dulcimer's tune (0 LU): the running pluck -8 LU, the bass -9, the drums -7 (a town: under
# Oruvel's and the match's drive), the glass -15 (it sounds in A' and the intro only), the Bell -12 (two strikes per
# loop), the lamps' hum -20 (felt more than heard), the rigging -24.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=9.0)
    mx.bus("dulcimer", 0.0, send=0.25, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(3000, -1.0, 1.0)]))
    mx.bus("pluck", -24.7, send=0.18, process=lambda x: filt(x, [bq_highpass(80, 0.7), bq_lowpass(3500, 0.7)]))
    mx.bus("bass", -5.8, send=0.05, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
    mx.bus("drums", -3.0, send=0.15)
    mx.bus("glass", -8.8, send=0.5)
    mx.bus("bell", -13.4, send=0.4)
    mx.bus("hum", -11.8, send=0.3, process=lambda x: filt(x, [bq_lowpass(6000, 0.7)]))
    mx.bus("rigging", -39.7, send=0.35)
    build(mx)
    harbour = ModFDNReverb(rt60=1.5, rt60_high=0.7, predelay=0.02, size=0.9, mod_depth=8.0, mod_rate=0.5,
                           early_level=0.3, lowcut=120.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=harbour, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, BAR_EIGHTHS,
                       extra={"loop_bars": BARS, "downbeat_offset_s": DOWNBEAT_OFFSET_S,
                              "meter": "7/8 (2+2+3); bpm counts quavers"})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"tamsule: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
