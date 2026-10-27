"""`tavi_kell`: Ch7 B03, "Tavi", from "She couldn't swim" (M3-AUD-820; act1_ch07.md §6), ~32 s, through-composed.

Original composition for this project (SPEC §2): a sparse piano piece written for this beat. Its only borrowed
material is our own: the first two notes of Ch1's Oruvel town theme (oruvel.py `TUNE_A`, its first bar: D5 then B4,
the squeezebox's opening fall of a third), imported from oruvel.py, never retyped. Nothing here is derived from any
existing tune.

The brief: "Solo piano, very sparse, entering only after the line's hold. It quotes Ch1's Oruvel town theme in two
notes and doesn't finish the phrase." Tavi, Mother Kell's grandson, asks after his gran; Rhen: "She couldn't swim,
Tavi." The cutscene holds two seconds with no music while the festival goes on around them; this cue starts after
that hold, under Tavi's grief, the choice, and the empty place in the side.

So the town's tune starts twice and never gets to its third note. In Oruvel the first bar runs D-B-G and lands home
on G; here the left hand sets an open G fifth under the D and B, so the ear waits for the G, and the right hand stops.
The second try is a single D over A minor. The last chord is C major with a seventh and ninth (the B and the D of the
quote, held inside it), left to ring: no G, no home. E minor (the colour of Oruvel's B section, the only bars where the
town looked away) to C, 4/4 at 54 BPM (a bar is 4.44 s), played freely.

Bars: 1 a low E, open, very soft | 2 E minor, an inner third | 3 the quote: D5, B4 over an open G, and nothing
after it | 4 A minor, the bass alone | 5 one D5, softer, and the chord under it | 6-7 C major (add the B and D), spread
from the bass and left to ring.

Render:  python3 assets_src/music/tavi_kell.py   (or tools/audio/render_all.py --only tavi_kell)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import rng  # noqa: E402
from synth.grand import PianoBody  # noqa: E402
from synth.mixer import Mixer  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ORUVEL = _mod("oruvel")
HFV = _mod("hush_first_verse")

OUT = os.path.join(ROOT, "assets", "audio", "music", "tavi_kell.ogg")
SEED = 20261722
BPM = 54.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
T0 = 1.2                # after the script's 2 s fade-in has mostly risen
QUOTE = ORUVEL.TUNE_A[0][:2]          # [("D5", 2 eighths), ("B4", 1 eighth)]: the town's first two notes
# (bar, beat, pitch, velocity, held beats, role): the left hand and the inner voices
LH = [(1, 0.0, "E1", 0.22, 7.5, "bass"), (1, 0.08, "E2", 0.20, 7.5, "bass"), (1, 2.0, "B2", 0.15, 5.5, "acc"),
      (2, 1.0, "G3", 0.15, 3.0, "acc"), (2, 1.3, "B3", 0.14, 2.7, "acc"),
      (3, 0.0, "G2", 0.22, 4.0, "bass"), (3, 0.1, "D3", 0.17, 3.9, "acc"),
      (4, 0.0, "A1", 0.20, 4.0, "bass"), (4, 0.12, "A2", 0.17, 3.9, "acc"), (4, 2.0, "E3", 0.13, 2.0, "acc"),
      (5, 1.0, "C3", 0.16, 3.0, "acc"), (5, 1.15, "E3", 0.14, 2.85, "acc"), (5, 1.3, "A3", 0.13, 2.7, "acc")]
END = ["C1", "C2", "G2", "E3", "B3", "D4"]
END_BAR = 6


def _quote(bar: int, slow: float, vel: float, g, notes: int = 2) -> list[dict]:
    """The town's first notes at `slow` beats per eighth (Oruvel's swung eighths, here straight and very slow)."""
    out, t = [], T0 + (bar - 1) * BAR
    for p, eighths in QUOTE[:notes]:
        d = eighths * slow * BEAT
        out.append(dict(m=n(p), vel=vel * g.uniform(0.97, 1.03), t0=t + float(g.normal(0, 0.01)), key_up=d + 0.05,
                        role="mel"))
        t += d
    return out


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    notes = [dict(m=n(p), vel=v * g.uniform(0.95, 1.04),
                  t0=T0 + (bar - 1) * BAR + beat * BEAT + float(g.normal(0, 0.01)), key_up=held * BEAT, role=role) for bar, beat, p, v, held, role in LH]
    notes += _quote(3, 0.9, 0.30, g)                 # D (a long beat and a half), B, and then no G
    notes += _quote(5, 1.1, 0.24, g, notes=1)        # D alone, softer: it doesn't try the B
    end_t = T0 + (END_BAR - 1) * BAR + 0.3 * BEAT
    notes += [dict(m=n(p), vel=0.22 - 0.015 * j, t0=end_t + 0.16 * j, key_up=2 * BAR, role="bass" if j < 2 else "acc")
              for j, p in enumerate(END)]
    changes = [T0 + (b - 1) * BAR for b in (3, 4, 5)] + [end_t - 0.05]
    pedal = plan_pedal(changes, start=T0, end_release=end_t + 1.7 * BAR, release_len=4.0, g=g)
    mx = Mixer(end_t + 2 * BAR + 6.0)
    mx.bus("piano", 0.0, send=0.28, process=PianoBody(pedal))
    for nt, x in zip(notes, render_jobs(HFV._piano_jobs(notes, pedal, SEED + 5))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    room = ModFDNReverb(rt60=2.6, rt60_high=1.1, predelay=0.024, size=1.0, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.22, lowcut=90.0, seed=SEED % 9973)
    m = HFV._finish(mx, room, out_path, 4.0)
    if verbose:
        print(f"tavi_kell: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
