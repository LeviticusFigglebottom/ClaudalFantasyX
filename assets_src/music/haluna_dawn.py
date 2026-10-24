"""`haluna_dawn`: Cutscene A, "The Girl on the Beach" (M2-AUD-03; vertical_slice.md B01), ~2.5 min, not looped.

Original composition for this project (SPEC §2). The brief: "Solo piano and a low metallophone, very slow. It
doesn't know yet whether it's sad." A boy washes up on Haluna's beach at 06:20; a girl finds him.

The ambiguity is harmonic: D major and B minor share every note, and the piece keeps moving between them
(Dmaj7 and Bm9 under the same right hand), so the same melody reads warm or grieving by its bass. The melody is
built from two cells the slice will make familiar: the circling cell of Haluna's tune (haluna_theme.py: F# E D E |
F# A), heard here before the village plays it, and, in the middle, the Hush theme's long note and stepwise fall
(hush_theme_v2.py), transposed into B minor where the grief arrives (the cyan light in the water). The ending
stops on E over D (the 9th): not resolved, not sad either.

4/4 at 50 BPM (a bar is 4.8 s), 30 bars. Bars 1-4: the low metallophone and open fifths, a high two-note figure;
5-12: the Haluna cell, gently; 13-20: B minor, the Hush's fall; 21-28: the cell again, warmer, the metallophone
doubling its long notes; 29-30: a spread Dmaj9, left ringing.

Render:  python3 assets_src/music/haluna_dawn.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, rng  # noqa: E402
from synth.grand import PianoBody  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

_spec = importlib.util.spec_from_file_location("hush_first_verse", os.path.join(os.path.dirname(__file__),
                                                                                 "hush_first_verse.py"))
HFV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HFV)

OUT = os.path.join(ROOT, "assets", "audio", "music", "haluna_dawn.ogg")
SEED = 20261109
BPM = 50.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT

# Left hand per bar: a slow rocking figure (bass, fifth, tenth, fifth) on eighths 1, 3, 5, 7.
LH = (["D2 A2 F#3 A2", "D2 A2 F#3 A2", "B1 F#2 D3 F#2", "B1 F#2 D3 F#2"]
      + ["D2 A2 F#3 C#4", "B1 F#2 D3 A3", "G1 D2 B2 F#3", "A1 E2 C#3 E3", "D2 A2 F#3 C#4", "B1 F#2 D3 A3",
         "G1 D2 B2 F#3", "A1 E2 D3 E3"]
      + ["B1 F#2 D3 A3", "G1 D2 B2 F#3", "E2 B2 G3 D4", "F#1 C#2 A#2 E3", "B1 F#2 D3 A3", "G1 D2 B2 E3",
         "E2 B2 G3 B3", "A1 E2 C#3 G3"]
      + ["D2 A2 F#3 C#4", "B1 F#2 D3 A3", "G1 D2 B2 F#3", "A1 E2 C#3 E3", "D2 A2 F#3 C#4", "B1 F#2 D3 A3",
         "G1 D2 B2 E3", "A1 E2 D3 E3"]
      + ["D2 A2 E3 F#3", "D2 A2 E3 F#3"])
# Right hand: (pitch, beats) per section.
RH_OPEN = [(None, 2), ("F#5", 1), ("E5", 5), (None, 4), ("F#5", 1), ("E5", 3), (None, 0)]
RH_CELL = [("F#5", 2), ("E5", 1), ("D5", 1), ("E5", 4), ("F#5", 2), ("A5", 2), ("B5", 3), ("A5", 1),
           ("F#5", 2), ("E5", 1), ("D5", 1), ("B4", 4), ("D5", 2), ("E5", 2), ("E5", 4)]
RH_GRIEF = [("F#5", 3), ("E5", .5), ("D5", .5), ("B4", 3), ("A4", .5), ("B4", .5), ("A4", 1), ("D5", 1), ("E5", 2),
            ("F#5", 4), ("G5", 2), ("F#5", 1), ("E5", 1), ("D5", 3), ("C#5", .5), ("B4", .5), ("C#5", 2), ("D5", 2), ("E5", 4)]
RH_WARM = [("F#5", 2), ("E5", 1), ("D5", 1), ("E5", 2), ("F#5", 1), ("A5", 1), ("B5", 3), ("A5", 1), ("D6", 2),
           ("B5", 2), ("A5", 2), ("F#5", 1), ("E5", 1), ("D5", 2), ("E5", 2), ("F#5", 2), ("E5", 2), ("E5", 4)]
RH_END = [("A5", 2), ("F#5", 2), ("E5", 4)]
METAL = [(1, "D4", .40), (3, "B3", .36), (13, "B3", .34), (17, "G3", .30), (21, "D4", .36), (25, "D4", .32),
         (29, "D4", .30)]


def _line(notes: list, bar: int, vel: float, g, t0: float) -> list[dict]:
    out = []
    t = t0 + (bar - 1) * BAR
    for p, beats in notes:
        d = beats * BEAT
        if p is not None:
            out.append(dict(m=n(p), vel=vel * g.uniform(0.94, 1.05), t0=t + float(g.normal(0, 0.006)),
                            key_up=d + 0.035, role="mel"))
        t += d
    return out


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    t0 = 0.5
    notes = []
    for b, chord in enumerate(LH, start=1):
        ps = chord.split()
        soft = 0.75 if b <= 4 or b >= 29 else 1.0
        for i, p in enumerate(ps):
            v = (0.32 if i == 0 else 0.22) * soft * g.uniform(0.93, 1.05)
            t = t0 + (b - 1) * BAR + i * BEAT + float(g.normal(0, 0.008))
            notes.append(dict(m=n(p), vel=v, t0=t, key_up=BAR * (1.0 if i == 0 else 0.45),
                              role="bass" if i == 0 else "acc"))
    notes += _line(RH_OPEN, 1, 0.30, g, t0)
    notes += _line(RH_CELL, 5, 0.38, g, t0)
    notes += _line(RH_GRIEF, 13, 0.40, g, t0)
    notes += _line(RH_WARM, 21, 0.42, g, t0)
    notes += _line(RH_END, 29, 0.30, g, t0)
    end_t = t0 + len(LH) * BAR
    changes = [t0 + (b - 1) * BAR for b in range(2, len(LH) + 1)]
    pedal = plan_pedal(changes, start=t0, end_release=end_t + BAR, release_len=4.0, g=g, half={0, 2, 27})
    mx = Mixer(end_t + 2 * BAR + 8.0)
    mx.bus("piano", 0.0, send=0.26, process=PianoBody(pedal))
    mx.bus("metal", -9.0, send=0.45)
    for nt, x in zip(notes, render_jobs(HFV._piano_jobs(notes, pedal, SEED + 5))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    for i, (bar, p, v) in enumerate(METAL):
        x = metallophone_note(n(p), v, seed=SEED + 300 + i, decay=7.0, hardness=0.2, ombak_hz=3.2)
        mx.add("metal", x, t0 + (bar - 1) * BAR, pan=0.2)
    for i, nt in enumerate(_line(RH_WARM, 21, 0.3, rng(SEED + 7), t0)):   # the metallophone doubles the long notes
        if nt["key_up"] >= 2 * BEAT:
            x = metallophone_note(nt["m"] - 12, 0.24, seed=SEED + 400 + i, decay=4.5, hardness=0.25, ombak_hz=4.0)
            mx.add("metal", x, nt["t0"], pan=0.35)
    hall = ModFDNReverb(rt60=3.0, rt60_high=1.3, predelay=0.028, size=1.1, mod_depth=8.0, mod_rate=0.45,
                        early_level=0.22, lowcut=90.0, seed=SEED % 9973)
    m = HFV._finish(mx, hall, out_path, 4.0)
    if verbose:
        print(f"haluna_dawn: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
