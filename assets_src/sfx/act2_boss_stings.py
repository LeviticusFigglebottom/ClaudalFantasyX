"""Act II's creature bosses named with their own stings (M4-A2P-092; the cue sheet §3; plain git, ADR 0175).

The same frame as act1_boss_stings.py's (imported: a low gong and drum as the camera finds the boss and the title card
shows, about 4 s, and an open fifth struck high above), and in it the boss's own voice from its creature set
(act2_creature_sfx.py) and the one material that is it:

    mangrove_drowner  Ch10: the Drowner's roots hauling, prop-roots creaking like a moored hull, tannin water thrown
    lamp_engine       Ch11: the Engine's steady bound hum and its salt-glass lamps chiming as the rings swing up
    avalanche_ram     Ch12: the woolback's long bellow and the snow sliding off the shelf (ADR 0204 §2: wet, matted
                      wool, no ice)
    wakefin           Ch15: the blade cutting the black water and the breach, in the dark

battle_stings.json `boss_intro.by_arg` keys them by the intro's title key: their encounters aren't written yet, and
choreo.json `boss_intro.by_enemy` stages their intros. StingAudio tries the encounter first, then the title key.
Each has a `_soft` twin without sub-bass for reduced audio. Synthesized here and in tools/audio/synth/ (SPEC §2, §9);
each fifth is an open interval on a struck bar, not a melody.

assets/audio/act2/sfx/battle/sting_boss_<boss>.ogg / _soft.ogg (mono, q4): -16 / -17 LUFS momentary max.

Render:  python3 tools/audio/render_all.py --only act2_boss_stings
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import act1_boss_stings as S1  # noqa: E402
import act2_creature_sfx as A2  # noqa: E402
import battle_sfx as B  # noqa: E402
import creature_sfx as C  # noqa: E402
from act1_skill_sfx import creak, rumble  # noqa: E402
from synth.dsp import bq_bandpass, bq_highpass, filt, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "sfx", "battle")
SEED = 20262300


def _voice(cls, cid: str, event: str, g) -> np.ndarray:
    return getattr(cls, event)(A2.CREATURES[cid], 0, g)


def mangrove_drowner(g):
    x = S1.frame(g, "G1", "D5", SEED + 10)
    B._place(x, 0.55 * _voice(A2.Drowner, "mangrove_drowner", "attack", g), 0.25)
    B._place(x, 0.45 * creak(g, 1.4, 25, 120, ((140.0, 1.0), (380.0, 0.6), (900.0, 0.3))), 0.1)
    B._place(x, 0.35 * A2.splash(g, 1.6, 0.8, 1200), 0.7)
    return x


def lamp_engine(g):
    x = S1.frame(g, "C2", "G5", SEED + 20, drum=0.6)
    B._place(x, 0.55 * _voice(A2.Engine, "lamp_engine", "idle", g), 0.15)
    for i, f in enumerate((1760.0, 2637.0, 3520.0)):                  # the lamps chiming as the rings swing up
        B._place(x, 0.3 * C.glass_ring(g, f, 1.6, 1.0), 0.3 + 0.18 * i)
    return x


def avalanche_ram(g):
    x = S1.frame(g, "E2", "B5", SEED + 30, drum=0.9)
    B._place(x, 0.6 * _voice(A2.Woolback, "avalanche_ram", "attack", g), 0.3)
    N = B._n(S1.SEC)
    snow = filt(g.standard_normal(N), [bq_bandpass(2200, 0.6)]) * np.clip(B._t(N) / 1.2, 0, 1) * np.exp(-B._t(N) / 1.8)
    x += 0.12 * snow                                                   # the snow sliding off the shelf
    B._place(x, 0.4 * rumble(g, 2.2, 70), 0.5)
    return x


def wakefin(g):
    x = S1.frame(g, "D#2", "A#5", SEED + 40, drum=0.7)
    B._place(x, 0.6 * _voice(A2.Sailfin, "wakefin", "attack", g), 0.2)
    B._place(x, 0.4 * A2.splash(g, 1.8, 0.9, 2000), 0.55)            # the breach
    return x


BOSSES = {"mangrove_drowner": mangrove_drowner, "lamp_engine": lamp_engine, "avalanche_ram": avalanche_ram,
          "wakefin": wakefin}


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
    SFX[f"sting_boss_{_b}"] = (_sting(_fn, _i, False), S1.STING)
    SFX[f"sting_boss_{_b}_soft"] = (_sting(_fn, _i, True), S1.SOFT)
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
