"""Each Act I boss named with its own sting (M3-AUD-861, ADR 0041; Git LFS, ADR 0173).

battle_stings.py's `sting_boss` named every boss but the Drownbell, which has its own toll. Each boss now gets its
own sting for its intro (battle_stings.json `boss_intro.by_arg`, by encounter id): the same frame (a low gong and drum
as the camera finds it and the title card shows, about 4 s, held under the `boss_intro` duck), and in it the boss's
own voice (its creature set's sounds, creature_sfx.py / act1_final_creature_sfx.py) and the one material that is it:

    hullgnaw        Ch1: the eel's throat and ribs, and the breaking raft's timbers giving under it
    bottle_hermit   Ch4: the hermit's claws on glass, and its frosted lamp glass ringing
    spar_wraith     Ch4: the wraith's creak, and its rigging hauling taut, deadeyes knocking
    cinder_matron   Ch5: slag crackling and pouring, the Matron's grind, the gong low and hot
    inquisitor      Ch6: the brine-iron struck on stone, the shield, and the Order's hum under them (C, the Order's key)
    undertows_reach Ch8: the sea drawn up the wall into the Reach's surge, the gong at the bottom of everything

Each has a `_soft` twin without sub-bass for reduced audio (battle_stings.json `reduced`), as the shared stings do.
Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Every pitched figure is an open interval on a gong or a
struck bar, written for this file; nothing quotes a melody.

assets/lfs/audio/sfx/battle/sting_boss_<boss>.ogg / _soft.ogg (mono, q4): -16 / -17 LUFS momentary max, the
targets.py boss-sting rules.

Render:  python3 tools/audio/render_all.py --only act1_boss_stings
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import battle_sfx as B  # noqa: E402
import numpy as np  # noqa: E402

import creature_sfx as C  # noqa: E402
from act1_final_creature_sfx import Inquisitor  # noqa: E402
from act1_skill_sfx import creak, rope, wave  # noqa: E402
from act2_creature_sfx import splash, tinkle  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "lfs", "audio", "sfx", "battle")
SEED = 20261864
STING, SOFT = -16.0, -17.0
SEC = 4.2


def frame(g, root: str, fifth: str, seed: int, drum: float = 0.75) -> np.ndarray:
    """The naming: a low gong on `root` with the drum, an open fifth struck high above it."""
    N = B._n(SEC)
    x = np.zeros(N)
    B._place(x, 0.8 * large_gong(n(root), 0.95, seed=seed, t60=4.0)[:N], 0.0)
    x += drum * B._thump(78, 36, 0.32, N, g, click=0.5)
    for i, (nm, at) in enumerate(((root.replace("1", "5").replace("2", "5"), 0.02), (fifth, 0.05))):
        B._place(x, 0.3 * metallophone_note(n(nm), 0.75, seed=seed + 1 + i, decay=2.4, hardness=0.6, ombak_hz=4.5), at)
    return x


def creature(fam, cid: str, event: str, v: int, g) -> np.ndarray:
    return getattr(fam, event)(C.CREATURES[cid], v, g)


def hullgnaw(g):
    x = frame(g, "C2", "G5", SEED + 10)
    B._place(x, 0.6 * creature(C.Eel, "hullgnaw", "attack", 0, g), 0.25)
    B._place(x, 0.5 * creak(g, 1.6, 30, 140, ((160.0, 1.0), (420.0, 0.6), (1000.0, 0.3))), 0.15)
    B._place(x, 0.4 * C.thump(g, 110, 40, 0.2, 0.5, 0.6), 0.9)   # a timber gives
    return x


def bottle_hermit(g):
    x = frame(g, "E2", "B5", SEED + 20, drum=0.6)
    B._place(x, 0.6 * creature(C.Crab, "bottle_hermit", "attack", 0, g), 0.3)
    for i, f in enumerate((1980.0, 2970.0)):                        # the frosted lamp glass, rung
        B._place(x, 0.35 * C.glass_ring(g, f, 2.0, 1.0), 0.08 + 0.05 * i)
    B._place(x, 0.2 * tinkle(g, 0.6, 6, 2600, 5200, 1.0), 0.6)
    return x


def spar_wraith(g):
    x = frame(g, "B1", "F#5", SEED + 30)
    B._place(x, 0.55 * creature(C.Wraith, "spar_wraith", "idle", 0, g), 0.2)
    B._place(x, 0.5 * rope(g, 1.4, 120, 560), 0.1)
    for i in range(3):                                                # deadeyes knocking as it hauls
        B._place(x, 0.3 * C.tap(g, [420.0, 980.0, 1900.0], [0.05, 0.03, 0.015], 1.0, 0.6, 0.05), 0.5 + 0.3 * i)
    return x


def cinder_matron(g):
    x = frame(g, "G1", "D5", SEED + 40)
    B._place(x, 0.55 * creature(C.Matron, "cinder_matron", "idle", 0, g), 0.2)
    N = B._n(SEC)
    slag = C.crackle(g, SEC, 60, 2400, 0.9) * np.clip(B._t(N) / 0.6, 0, 1) * np.exp(-B._t(N) / 2.5)
    x += 0.3 * slag
    B._place(x, 0.4 * kettle_gong(n("D3"), 0.6, seed=SEED + 45, t60=2.4), 0.05)
    return x


def inquisitor(g):
    x = frame(g, "C2", "G5", SEED + 50, drum=0.5)
    B._place(x, 0.7 * Inquisitor.iron(g, 1.0, 0.8), 0.05)            # the brine-iron set down on stone
    B._place(x, 0.5 * Inquisitor.shield(g, 1.0), 0.45)
    t = B._t(B._n(SEC))
    hum = sum(a * np.sin(2 * np.pi * midi_to_hz(n(m)) * t) for m, a in (("C3", 1.0), ("G3", 0.6), ("C4", 0.3)))
    hum = filt(hum, [bq_lowpass(1200, 0.7)]) * B._swell(len(t), 0.6, 1.6, 1.6)
    x += 0.07 * hum                                                   # the Order's hum under him, in C
    return x


def undertows_reach(g):
    x = frame(g, "A1", "E5", SEED + 60, drum=0.9)
    B._place(x, 0.7 * wave(g, 1.8, 1.0), 0.0)                         # the sea drawn up the wall
    B._place(x, 0.6 * creature(C.Reach, "undertows_reach", "attack", 0, g), 0.4)
    B._place(x, 0.4 * splash(g, 2.2, 0.8, 1500), 0.5)
    return x


BOSSES = {"hullgnaw": hullgnaw, "bottle_hermit": bottle_hermit, "spar_wraith": spar_wraith,
          "cinder_matron": cinder_matron, "inquisitor": inquisitor, "undertows_reach": undertows_reach}


def _sting(fn, i: int, soft: bool):
    def f() -> np.ndarray:
        x = fn(rng(SEED + 1000 * i))
        if soft:
            x = filt(x, [bq_highpass(140, 0.9), bq_highpass(140, 0.9)])
        x = filt(x, [bq_highpass(28, 0.7)])
        return B._tail_fade(B._room(x, 2.4, 0.26, SEED + 1000 * i + 1, predelay=0.03, size=0.9, high=5000), 0.5)
    return f


SFX: dict = {}
for _i, (_b, _fn) in enumerate(BOSSES.items()):
    SFX[f"sting_boss_{_b}"] = (_sting(_fn, _i, False), STING)
    SFX[f"sting_boss_{_b}_soft"] = (_sting(_fn, _i, True), SOFT)
FILES = [name + ".ogg" for name in SFX]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, (fn, tgt) in SFX.items():
        x = C.finish(fn(), tgt)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        res[name] = measure(x)
        if verbose:
            m = res[name]
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  peak {m['sample_peak_dbfs']:.2f}")
    return res


if __name__ == "__main__":
    render()
