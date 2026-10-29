"""`ysolde_theme`: Ysolde Ysel's character theme, final (M3-AUD-863, grown from the M3-AUD-820 sketch; ADR 0041;
act1_ch04.md §6, C4-07 "The Ink" and C4-09 the gangplank): a 91.4 s seamless loop.

Original composition for this project (SPEC §2, §9). Original-material check: the zither's line below (`LINE`: C-G-D-
A-B to a held E, D-A-E-B-C to a held G, a falling answer home to C; then a Lydian half with F#), the final's two new
Lydian bars (`NEW_BARS`: F#-B-E-A in falling and rising fourths, to a held B) and the alto zither's counter-line
(`COUNTER`: three-note chains of falling fourths and fifths, A-E-B, D-A-E, G-D-G, F#-B-E, E-B-F#, E-B-F#, D-G, each
set into a note the line holds) were written for this cue. None of it shares a phrase with Sefir's motif or its
answer (sefir_theme.py: G C D E D C#; D C G), Ansedra's court tune or its bowls' figure (ansedra.py: C-G, F-E-D-E,
A held, the D-E-F#-G lift; G-C-E-D), the Hush, or any melody we know, and the counter-line never touches C#, Sefir's
wrong note. The style evoked is a slow court duet for two plucked board zithers over a reed drone; nothing is quoted.

The brief (the sketch's): "A cold, plucked zither-like line over a low reed drone; exact, unhurried, very little
vibrato. Ansedran lacquer and gold, not the Low Reaches." The final's (M3-AUD-863): the same identity grown into a
developed form, with a second voice that answers the line, exact and cold like her. Ysolde is the Conclave's
appointed tutor in Lamptongue: she re-inks the Velamir shells on the wake wall at night (C4-07), and stands alone at
the foot of the gangplank at dawn with a folded appointment under her hand (C4-09): cold, correct, appointed, and
making a name last.

So the line is built from fourths and fifths, the intervals of tuning a zither, set out in quarters and pairs of
eighths with every phrase ending on a long held note: exact, never hurried, never ornamented. The counter-line is a
second, lower board zither (strings plucked further from the bridge, through a deeper lacquered box) that speaks only
into the line's held notes: three quarters of falling fourths, the mirror of her rising fifths. She sets a word down
and the second voice copies it out, correct, a register lower, the way she re-inks a name. Nothing warm is added: no
third under the line in the low register, no rubato, no vibrato on anything (2 ms of timing scatter, where the Low
Reaches cues use 5-8), and the drone does not breathe. The Ansedran colour is the key and the voicing: C major, the
Order's key (sefir_theme, ansedra), over an open C-G fifth with no third in it, the hollowness of the holy city; in B
the line turns Lydian (F#), cool and bright, and the F natural at the top of A'' takes it back. The gold is one
gilded bowl (ansedra.py's paired metallophone bars) at each seam of the form: bars 1, 9, 15 and 21.

Ensemble (all synthesized; no samples, recordings or AI audio):
* the board zither: stiff steel strings plucked near the bridge, through a small lacquered box (a shallow body with
  high, dry modes); the line;
* the alto zither: the counter-line, a register lower, plucked further along the string through a deeper box; it
  enters only on a held note of the line and is silent in A;
* the open strings: a low C-G fifth plucked at the start of each phrase (bars 1, 5, 9, 13, 15, 17, 21);
* the reed drone: a double reed's steady tone on C2 and G2, every partial snapped to a whole number of cycles per
  loop (exactly periodic), with a nasal formant and no tremolo;
* a gilded bowl at the form's seams (bars 1, 9, 15, 21), high and soft.

C major / C Lydian, 4/4 at 63 BPM (a bar is 3.81 s), 24 bars, 91.43 s; times from bar 1's downbeat:
* A   (bars 1-8,   0.0-30.5 s): the sketch's statement, the zither alone with its open strings: to a held E, to a
  held G, the falling answer home to C;
* A'  (bars 9-14,  30.5-53.3 s): the first phrase again, and now the alto zither answers each held note (E, G, C);
  the falling answer is cut to its last two bars, so the phrase closes sooner and colder;
* B   (bars 15-20, 53.3-76.2 s): Lydian (F#): the sketch's B up to a held A, then two new bars falling by fourths to
  a held B over the C drone (a bare major seventh, bright and unresolved); the counter answers with F# in it;
* A'' (bars 21-24, 76.2-91.4 s): the falling answer returns with F natural, the sketch's descent to G with the
  counter's last D-G under it, and a bar of the drone alone, back to bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth, not on a pluck.

`LINE`, `BAR`, `BEAT`, `SCATTER`, `lacquer_box` and `zither` are imported by act3/dace_ledger.py (her line, bars
1-7, in her own voice), so they stay as the sketch set them; the final's form is built from them.

Render:  python3 assets_src/music/ysolde_theme.py   (or tools/audio/render_all.py --only ysolde_theme)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "ysolde_theme.ogg")
SEED = 20261423
TARGET_LUFS = -16.0
## Vorbis quality: q3 fits the plain-git budget (the file must stay at or under 0.90 MB)
OGG_QUALITY = 3.0
BPM = 63.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
## timing scatter (s): exact
SCATTER = 0.002

## the line (the theme's statement, as the sketch set it): one list per bar of (pitch | None, beats)
LINE = [
    [("C5", 1), ("G4", 1), ("D5", 1), ("A4", .5), ("B4", .5)],
    [("E5", 3), (None, 1)],
    [("D5", 1), ("A4", 1), ("E5", 1), ("B4", .5), ("C5", .5)],
    [("G5", 3), (None, 1)],
    [("F5", 1), ("E5", .5), ("D5", .5), ("C5", 1), ("G4", 1)],
    [("A4", 2), ("B4", 1), ("C5", 1)],
    [("D5", 1), ("G4", 1), ("E5", 1.5), ("D5", .5)],
    [("C5", 3), (None, 1)],
    [("B4", 1), ("F#5", 1), ("E5", 1), ("B4", 1)],
    [("D5", 3), (None, 1)],
    [("A4", 1), ("E5", 1), ("F#5", 1), ("G5", 1)],
    [("A5", 3), (None, 1)],
    [("G5", 1), ("E5", .5), ("D5", .5), ("B4", 1), ("A4", 1)],
    [("E5", 2), ("D5", 1), ("B4", 1)],
    [("C5", 1), ("D5", 1), ("G4", 2)],
    [(None, 4)],
]
## the final's two new bars (B's close, Lydian)
NEW_BARS = {
    "b5": [("F#5", 1), ("B4", 1), ("E5", 1), ("A4", 1)],
    "b6": [("B4", 3), (None, 1)],
}
## the form: per bar, a LINE bar (1-based) or a NEW_BARS key
FORM: list[int | str] = [
    1, 2, 3, 4, 5, 6, 7, 8,           # A
    1, 2, 3, 4, 7, 8,                 # A'
    9, 10, 11, 12, "b5", "b6",        # B (Lydian)
    5, 14, 15, 16,                    # A''
]
BARS = len(FORM)
LOOP_S = BARS * BAR
## the alto zither's counter-line: per form bar, (pitch | None, beats), set into the line's held notes
COUNTER = {
    10: [(None, 1), ("A4", 1), ("E4", 1), ("B3", 1)],
    12: [(None, 1), ("D5", 1), ("A4", 1), ("E4", 1)],
    14: [(None, 1), ("G4", 1), ("D4", 1), ("G3", 1)],
    16: [(None, 1), ("F#4", 1), ("B3", 1), ("E4", 1)],
    18: [(None, 1), ("E5", 1), ("B4", 1), ("F#4", 1)],
    20: [(None, 1), ("E4", 1), ("B3", 1), ("F#4", 1)],
    23: [(None, 2), ("D4", 1), ("G3", 1)],
}
OPEN_STRINGS = (1, 5, 9, 13, 15, 17, 21)
BOWL = [(1, "G5", 0.20), (9, "E6", 0.16), (15, "D6", 0.15), (21, "G5", 0.18)]
## the reed drone: (root, level) and its partials' levels (a double reed: strong low harmonics, a nasal formant)
DRONE = [("C2", 1.0), ("G2", 0.55)]
REED_HARM = [1.0, 0.75, 0.62, 0.45, 0.38, 0.30, 0.22, 0.17, 0.12, 0.09, 0.07, 0.05]
## the alto zither's deeper box: (mode Hz, Q, level)
ALTO_MODES = ((190.0, 8, 0.6), (360.0, 10, 0.6), (640.0, 9, 0.45), (1150.0, 7, 0.3), (2300.0, 6, 0.15))


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def form_bar(i: int) -> list:
    """The zither's notes in form bar i (1-based)."""
    ref = FORM[i - 1]
    return NEW_BARS[ref] if isinstance(ref, str) else LINE[ref - 1]


def _box(seed: int, modes, sr: int = SR) -> np.ndarray:
    g = rng(seed)
    t = np.arange(int(0.12 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in modes:
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.3)) * np.exp(-t / d) * 0.08
    return ir / np.abs(ir).max()


def lacquer_box(seed: int, sr: int = SR) -> np.ndarray:
    """A shallow lacquered box under a board zither: high, dry modes, a quick decay, a hard click."""
    return _box(seed, ((280.0, 9, 0.5), (520.0, 11, 0.6), (930.0, 10, 0.5), (1700.0, 8, 0.35), (3300.0, 6, 0.25)), sr)


def alto_box(seed: int, sr: int = SR) -> np.ndarray:
    """The alto zither's deeper lacquered box: lower modes, still dry."""
    return _box(seed, ALTO_MODES, sr)


def zither(m: float, dur: float, vel: float, seed: int, box: np.ndarray) -> np.ndarray:
    """A stiff steel string plucked near the bridge: bright, exact, no vibrato; damped at the note's end."""
    x = string_pluck(m, dur, vel, seed=seed, pick_pos=0.09, t60=3.2, B=2.2e-4, max_f=9000.0, release=0.12)
    return fft_convolve(x, box)[: len(x) + 2000]


def alto_zither(m: float, dur: float, vel: float, seed: int, box: np.ndarray) -> np.ndarray:
    """The counter-line's string: plucked further along (rounder, still no vibrato), a shorter ring, damped exactly."""
    x = string_pluck(m, dur, vel, seed=seed, pick_pos=0.2, t60=2.4, B=1.2e-4, max_f=6000.0, release=0.10)
    return fft_convolve(x, box)[: len(x) + 2000]


def reed_drone(L: int, seed: int) -> np.ndarray:
    """The double reed's steady C-G drone, exactly periodic over the loop (every partial a whole number of cycles)."""
    g = rng(seed)
    Ls = L / SR
    t = np.arange(L) / SR
    out = np.zeros((L, 2))
    for root, lvl in DRONE:
        f0 = midi_to_hz(n(root))
        for k, a in enumerate(REED_HARM, start=1):
            f = round(f0 * k * Ls) / Ls
            for ch in range(2):
                out[:, ch] += lvl * a * np.sin(2 * np.pi * f * t + g.uniform(0, 2 * np.pi))
    return out / np.abs(out).max()


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    box = lacquer_box(SEED + 5)
    abox = alto_box(SEED + 7)
    mx.add("drone", reed_drone(mx.L, SEED + 3), 0.0)
    for i in range(1, BARS + 1):
        pos = 0.0
        for p, beats in form_bar(i):
            if p is not None:
                d = beats * BEAT
                v = 0.62 * g.uniform(0.97, 1.03) * (1.05 if pos == 0 else 1.0)
                x = zither(n(p), d, v, SEED + 100 * i + int(pos * 4), box)
                mx.add("zither", x, t_of(i, pos) + float(g.normal(0, SCATTER)), pan=0.1)
            pos += beats
    for i, notes in COUNTER.items():
        pos = 0.0
        for p, beats in notes:
            if p is not None:
                v = 0.55 * g.uniform(0.97, 1.03)
                x = alto_zither(n(p), beats * BEAT, v, SEED + 5000 + 100 * i + int(pos * 4), abox)
                mx.add("counter", x, t_of(i, pos) + float(g.normal(0, SCATTER)), pan=-0.3)
            pos += beats
    for bar in OPEN_STRINGS:
        for k, p in enumerate(("C3", "G3")):
            x = zither(n(p), 3.5 * BEAT, 0.45, SEED + 2000 + 10 * bar + k, box)
            mx.add("open", x, t_of(bar) + 0.012 * k, pan=-0.25)
    for i, (bar, p, v) in enumerate(BOWL):
        for j, det in enumerate((0.0, 0.035)):       # a gilded bowl: two bars a few cents apart (ansedra's bowls)
            y = metallophone_note(n(p) + det, v, seed=SEED + 600 + 10 * i + j, decay=6.0, hardness=0.25, ombak_hz=1.6)
            mx.add("bowl", y, t_of(bar, 0.5) + 0.004 * j, pan=0.45 - 0.2 * j)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# zither's line (0 LU): the counter-line -4 (it plays in seven bars of twenty-four), the reed drone -9, the open
# strings -10, the bowl -14 (four times a loop).
GAINS = {"zither": 0.0, "counter": -11.3, "open": -14.4, "drone": -25.4, "bowl": -1.7}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    mx.bus("zither", GAINS["zither"], send=0.25,
           process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(3000, -1.5, 1.0)]))
    mx.bus("counter", GAINS["counter"], send=0.3,
           process=lambda x: filt(x, [bq_highpass(110, 0.7), bq_lowpass(4500, 0.7)]))
    mx.bus("open", GAINS["open"], send=0.25, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    mx.bus("drone", GAINS["drone"], send=0.2,
           process=lambda x: filt(x, [bq_highpass(45, 0.7), bq_peak(900, 4.0, 1.5), bq_peak(2300, 2.0, 2.0),
                                      bq_lowpass(3200, 0.7)]))
    mx.bus("bowl", GAINS["bowl"], send=0.5)
    build(mx)
    hall = ModFDNReverb(rt60=2.2, rt60_high=0.9, predelay=0.03, size=1.0, mod_depth=6.0, mod_rate=0.4,
                        early_level=0.3, lowcut=110.0, seed=SEED % 9973)     # a lacquered room: clear, not wet
    _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=OGG_QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"ysolde_theme: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
