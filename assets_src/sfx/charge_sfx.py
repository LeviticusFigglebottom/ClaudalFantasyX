"""The `charge` choreography style's sounds (M3-BPR-410 for M3-AUD-838): the Avalanche Ram's run at a hero.

battle-presentation's `charge` style is a long, low run with a heavy lean and a big lunge (approach 0.55 s, contact at
half the 0.3 s strike). choreo_sfx.json's `charge` row plays these on it. Built from act2_creature_sfx.py's woolback
pieces, so the run is the Ram's own body (SPEC §2, §9: all synthesized, no samples, no generated audio). Mono,
Vorbis q4, under assets/audio/sfx/choreo/ on the Combat bus.

    step_hoof_1..3      one broad padded hoof on packed snow with a crunch and the locks' swing; the approach plays
                        four of them (-21 LUFS, as every battle footfall: they repeat)
    whoosh_charge_1..2  the mass going past: a low, wide rush of air rising into the lunge, with ice rattling in the
                        coat (-20 LUFS, as every strike whoosh, ahead of the weapon contact)

Render:  python3 assets_src/sfx/charge_sfx.py   (or tools/audio/render_all.py --only charge_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from act2_creature_sfx import Woolback, tinkle, whoosh  # noqa: E402
from creature_sfx import buf, finish, roar  # noqa: E402
from synth.dsp import rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "choreo")
SEED = 20261838
STEP, WHOOSH = -21.0, -20.0


def step_hoof(v: int) -> np.ndarray:
    g = rng(SEED + v)
    x = buf(0.5)
    place(x, Woolback.hoof(g, 1.0), 0.0)
    place(x, Woolback.locks(g, 0.35, 0.25), 0.03)
    return x


def whoosh_charge(v: int) -> np.ndarray:
    g = rng(SEED + 100 + v)
    x = buf(0.9)
    rush = roar(g, 0.55, 420 + 60 * v) * np.clip(_t(_n(0.55)) / 0.45, 0, 1) ** 2
    place(x, rush, 0.0, 0.7)
    place(x, whoosh(g, 0.4, 500, 1400 + 200 * v, 1.0), 0.2)
    place(x, tinkle(g, 0.3, 5, 2600, 4400, 0.35), 0.35)
    return x


SOURCES = [(f"step_hoof_{v + 1}", (lambda i=v: step_hoof(i)), STEP) for v in range(3)] + [
    (f"whoosh_charge_{v + 1}", (lambda i=v: whoosh_charge(i)), WHOOSH) for v in range(2)]
FILES = [name + ".ogg" for name, _, _ in SOURCES]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, fn, target in SOURCES:
        x = finish(fn(), target)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        res[name] = measure(x)
        if verbose:
            m = res[name]
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  peak {m['sample_peak_dbfs']:.2f}")
    return res


if __name__ == "__main__":
    render()
