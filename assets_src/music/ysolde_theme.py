"""`ysolde_theme`: Ysolde Ysel's character theme, a sketch (M3-AUD-820; act1_ch04.md §6, C4-07 and C4-09): a 61.0 s
seamless loop.

Original composition for this project (SPEC §2, §9). Original-material check: the zither's line below (C-G-D-A-B to a
held E, D-A-E-B-C to a held G, a falling answer home to C; then a Lydian half with F#) was written for this cue. It
shares no phrase with Sefir's motif (sefir_theme.py: G C D E D C#), Ansedra's court tune (ansedra.py), the Hush, or
any melody we know. The style evoked is a slow court solo for a plucked board zither over a reed drone; nothing is
quoted.

The brief: "Character theme, sketch. A cold, plucked zither-like line over a low reed drone; exact, unhurried, very
little vibrato. Ansedran lacquer and gold, not the Low Reaches." Ysolde is the Conclave's appointed tutor in
Lamptongue: she re-inks the Velamir shells on the wake wall at night (C4-07, "The Ink"), and stands alone at the foot
of the gangplank at dawn with a folded appointment under her hand (C4-09): cold, correct, appointed, and making a
name last.

So the line is built from fourths and fifths, the intervals of tuning a zither, set out in quarters and pairs of
eighths with every phrase ending on a long held note: exact, never hurried, never ornamented. The timing is
nearly mechanical (2 ms of scatter, where the Low Reaches cues use 5-8), the plucks have no vibrato at all, and the
drone does not breathe. The Ansedran colour is the key and the voicing: C major, the Order's key (sefir_theme,
ansedra), over an open C-G fifth with no third in it, the hollowness of the holy city; in the second half the line
turns Lydian (F#), cool and bright, and comes back. The gold is one gilded bowl (ansedra.py's paired metallophone
bars) at bars 1 and 9.

Ensemble (all synthesized; no samples):
* the board zither: stiff steel strings plucked near the bridge, through a small lacquered box (a shallow body with
  high, dry modes); the line;
* its open strings: a low C-G fifth plucked at the start of each phrase (bars 1, 5, 9, 13);
* the reed drone: a double reed's steady tone on C2 and G2, every partial snapped to a whole number of cycles per
  loop (exactly periodic), with a nasal formant and no tremolo;
* a gilded bowl at bars 1 and 9, high and soft.

C major / C Lydian, 4/4 at 63 BPM (a bar is 3.81 s), 16 bars: 1-4 the line's first phrase, to a held E, then G |
5-8 the answer, falling home to C | 9-12 B: Lydian (F#), up to A | 13-15 the descent to G | 16 the drone alone, a
bar of nothing, back to bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth, not on a pluck.

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
BPM = 63.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 16
LOOP_S = BARS * BAR
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
## timing scatter (s): exact
SCATTER = 0.002

## the line: one list per bar of (pitch | None, beats)
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
OPEN_STRINGS = (1, 5, 9, 13)
BOWL = [(1, "G5", 0.20), (9, "E6", 0.16)]
## the reed drone: (root, level) and its partials' levels (a double reed: strong low harmonics, a nasal formant)
DRONE = [("C2", 1.0), ("G2", 0.55)]
REED_HARM = [1.0, 0.75, 0.62, 0.45, 0.38, 0.30, 0.22, 0.17, 0.12, 0.09, 0.07, 0.05]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def lacquer_box(seed: int, sr: int = SR) -> np.ndarray:
    """A shallow lacquered box under a board zither: high, dry modes, a quick decay, a hard click."""
    g = rng(seed)
    t = np.arange(int(0.12 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((280.0, 9, 0.5), (520.0, 11, 0.6), (930.0, 10, 0.5), (1700.0, 8, 0.35), (3300.0, 6, 0.25)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.3)) * np.exp(-t / d) * 0.08
    return ir / np.abs(ir).max()


def zither(m: float, dur: float, vel: float, seed: int, box: np.ndarray) -> np.ndarray:
    """A stiff steel string plucked near the bridge: bright, exact, no vibrato; damped at the note's end."""
    x = string_pluck(m, dur, vel, seed=seed, pick_pos=0.09, t60=3.2, B=2.2e-4, max_f=9000.0, release=0.12)
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
    mx.add("drone", reed_drone(mx.L, SEED + 3), 0.0)
    for i, bar in enumerate(LINE, start=1):
        pos = 0.0
        for p, beats in bar:
            if p is not None:
                d = beats * BEAT
                v = 0.62 * g.uniform(0.97, 1.03) * (1.05 if pos == 0 else 1.0)
                x = zither(n(p), d, v, SEED + 100 * i + int(pos * 4), box)
                mx.add("zither", x, t_of(i, pos) + float(g.normal(0, SCATTER)), pan=0.1)
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
# zither's line (0 LU): the reed drone -9, the open strings -10, the bowl -14 (twice a loop).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    mx.bus("zither", 0.0, send=0.25, process=lambda x: filt(x, [bq_highpass(150, 0.7), bq_peak(3000, -1.5, 1.0)]))
    mx.bus("open", -14.4, send=0.25, process=lambda x: filt(x, [bq_lowpass(2500, 0.7)]))
    mx.bus("drone", -25.4, send=0.2, process=lambda x: filt(x, [bq_highpass(45, 0.7), bq_peak(900, 4.0, 1.5),
                                                                bq_peak(2300, 2.0, 2.0), bq_lowpass(3200, 0.7)]))
    mx.bus("bowl", -1.7, send=0.5)
    build(mx)
    hall = ModFDNReverb(rt60=2.2, rt60_high=0.9, predelay=0.03, size=1.0, mod_depth=6.0, mod_rate=0.4,
                        early_level=0.3, lowcut=110.0, seed=SEED % 9973)     # a lacquered room: clear, not wet
    _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
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
