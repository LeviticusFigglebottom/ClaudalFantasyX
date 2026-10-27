"""`name_board_home`: Ch4 C4-14, "the name-board" (M3-AUD-820; act1_ch04.md §6), ~58 s, through-composed.

Original composition for this project (SPEC §2). Its melody is our own: the star-path phrase Asha hums on Ch2's
beach, which haluna_dawn.py gives the piano's right hand (`RH_CELL`, the circling cell of Haluna's tune, F#-E-D-E |
F#-A), with the left-hand harmony that carried it there (`LH`, bars 5-12). Both are imported from haluna_dawn.py,
never retyped. Nothing here is derived from any existing tune.

The brief: "Piano and metallophone; the star-path phrase Asha hummed on Ch2's beach, once, slowly (the homecoming
lullaby, now for a ship that does go home)." Rhen prises the *Seventh Terrace*'s name-board off the stern more
carefully than anything he has ever salvaged; Ysolde recites the Canticle and the held motes sink seaward; the sails
come down; back aboard the ferry he refuses the boarder's fee. "That was the first thing I ever brought up for
nothing."

So the phrase is played once, slower than the beach (46 BPM against 50), with its original harmony, and the low
metallophone that opened Ch2 doubles its long notes. On the beach the cell ended on E over A and the cue stopped on
an unresolved ninth: it didn't know yet whether it was sad. Here the last E **resolves to D over D major**: the
lullaby that sends sailors home is, for once, true. The ship goes home; the board does.

D major, 4/4 at 46 BPM (a bar is 5.22 s), 10 bars: 1 the low metallophone on D and the beach's open left hand | 2-9
the star-path phrase (RH_CELL) over haluna_dawn's bars 5-12, the metallophone doubling its held notes an octave down
| 10 the resolution: D in the right hand over a spread D major, left ringing.

Render:  python3 assets_src/music/name_board_home.py   (or tools/audio/render_all.py --only name_board_home)
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
from synth.metallophone import metallophone_note  # noqa: E402
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


HD = _mod("haluna_dawn")
HFV = HD.HFV
HUSH = _mod("hush_theme_v2")

OUT = os.path.join(ROOT, "assets", "audio", "music", "name_board_home.ogg")
SEED = 20261421
BPM = 46.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
T0 = 1.5                # after the script's 2 s fade-in, so the first strike keeps its attack
# Left hand per bar: the beach's opening figure, then haluna_dawn's bars 5-12 (the harmony under RH_CELL), then home.
LH = [HD.LH[0]] + list(HD.LH[4:12])
HOME = ["D1", "D2", "A2", "F#3", "A3", "D4"]
METAL = [(1, "D4", 0.40), (10, "D4", 0.34)]


def _rh(g) -> list[dict]:
    """The star-path phrase, once, from bar 2, with a little more time on its long notes."""
    out, t = [], T0 + BAR
    for p, beats in HD.RH_CELL:
        d = beats * BEAT
        out.append(dict(m=n(p), vel=0.38 * g.uniform(0.95, 1.04) * (1.05 if beats >= 3 else 1.0),
                        t0=t + float(g.normal(0, 0.006)), key_up=d + 0.04, role="mel"))
        t += d
    return out


# Bus gains from measured bus loudness (render(stats=...)): the piano leads; the low metallophone sits about 10 LU
# under it (as on the beach). The grand piano model's raw level is far below a metallophone's, hence its low gain.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    notes = []
    for b, chord in enumerate(LH, start=1):
        soft = 0.72 if b == 1 else 0.95
        for i, p in enumerate(chord.split()):
            v = (0.31 if i == 0 else 0.21) * soft * g.uniform(0.93, 1.05)
            t = T0 + (b - 1) * BAR + i * BEAT + float(g.normal(0, 0.008))
            notes.append(dict(m=n(p), vel=v, t0=t, key_up=BAR * (1.0 if i == 0 else 0.45),
                              role="bass" if i == 0 else "acc"))
    rh = _rh(g)
    notes += rh
    end_t = T0 + len(LH) * BAR
    home = [dict(m=n(p), vel=0.27 - 0.018 * j, t0=end_t + 0.12 * j, key_up=2 * BAR, role="bass" if j < 2 else "acc")
            for j, p in enumerate(HOME)]
    home.append(dict(m=n("D5"), vel=0.33, t0=end_t + 0.55, key_up=2 * BAR, role="mel"))
    notes += home
    changes = [T0 + (b - 1) * BAR for b in range(2, len(LH) + 1)] + [end_t]
    pedal = plan_pedal(changes, start=T0, end_release=end_t + 1.6 * BAR, release_len=4.0, g=g, half={0})
    mx = Mixer(end_t + 2 * BAR + 6.0)
    mx.bus("piano", 0.0, send=0.26, process=PianoBody(pedal))
    mx.bus("metal", -26.0, send=0.45)
    for nt, x in zip(notes, render_jobs(HFV._piano_jobs(notes, pedal, SEED + 5))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    for i, (bar, p, v) in enumerate(METAL):
        x = metallophone_note(n(p), v, seed=SEED + 300 + i, decay=7.0, hardness=0.2, ombak_hz=3.2)
        mx.add("metal", x, T0 + (bar - 1) * BAR, pan=0.2)
    for i, nt in enumerate(rh):                     # the metallophone doubles the long notes, an octave down
        if nt["key_up"] >= 2 * BEAT:
            x = metallophone_note(nt["m"] - 12, 0.24, seed=SEED + 400 + i, decay=4.5, hardness=0.25, ombak_hz=4.0)
            mx.add("metal", x, nt["t0"], pan=0.35)
    hall = ModFDNReverb(rt60=3.0, rt60_high=1.3, predelay=0.028, size=1.1, mod_depth=8.0, mod_rate=0.45,
                        early_level=0.22, lowcut=90.0, seed=SEED % 9973)
    st: dict = {}
    HUSH._bus_stats(mx, st)
    if stats is not None:
        stats.update(st)
    m = HFV._finish(mx, hall, out_path, 4.0)
    if verbose:
        print("  buses", {k: round(v, 1) for k, v in st.items()})
        print(f"name_board_home: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS"
              f"  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
