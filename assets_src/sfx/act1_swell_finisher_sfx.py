"""The Swell finishers' own sounds (M3-AUD-864; effects.json swell_by_hero, battle_sfx.json vfx).

Kerrid's `long_hold` and Liss's `three_reel_charge` gained their own battle VFX (`swell_weighted_swing`,
`swell_reel_stop`), which borrowed `hit_none` and `status_apply`. They play over the Swell style's contact
(swell_kerrid / swell_liss, act1_ability_sfx.py), so each is the part the contact lacks: Kerrid's flat iron sweep at
knee height with the wet sand thrown out, and Liss's brass ring locking shut and the salt-glass flash held steady on
bound light. Built from act1_ability_sfx.py's palette and rendered the same way (its seeds continue after its jobs).

Synthesized here and in tools/audio/synth/ (SPEC §2, §9): no samples, no recordings, no generated audio.
assets/audio/sfx/battle/abl_<effect>.ogg (mono, q4; plain git: small files, ADR 0039 keeps LFS for binaries over
5 MB): the sweep a strike (-18 LUFS momentary max), the reel-stop a cast (-19).

Render:  python3 tools/audio/render_all.py --only act1_swell_finisher_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import act1_ability_sfx as A  # noqa: E402
from act1_ability_sfx import CAST, STRIKE, lay, rope  # noqa: E402
from act1_final_creature_sfx import brass, grit  # noqa: E402
from act2_creature_sfx import hum, whoosh  # noqa: E402
from creature_sfx import burst, finish, glass_ring, room, tap, thump  # noqa: E402
from synth.dsp import bq_lowpass, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "battle")


def fade(x: np.ndarray) -> np.ndarray:
    """Let a texture die away instead of stopping on its last grain."""
    return x * np.linspace(1.0, 0.0, len(x)) ** 2


# The Swell finishers' own effects (effects.json swell_by_hero, M3-AUD-864). They play over the style's contact
# (swell_kerrid / swell_liss), so each is the part the contact lacks: Kerrid's flat iron sweep with the wet sand
# thrown out, and Liss's brass ring locking shut and the salt-glass flash held steady on bound light.
FINISHERS = {
    "swell_weighted_swing": (lambda g: lay((whoosh(g, 0.55, 220, 700, 0.9), 0.0, 1.0), (rope(g, 0.4, 150, 500), 0.0, 0.5),
                                           (burst(g, 0.25, [bq_lowpass(1400, 0.7)], 0.004, 0.08), 0.35, 0.8),
                                           (fade(grit(g, 0.6, 0.7)), 0.38, 1.0), (thump(g, 95, 45, 0.1, 0.4, 0.5), 0.36, 0.7)),
                             STRIKE),
    "swell_reel_stop": (lambda g: lay((tap(g, [1900.0, 3100.0], [0.02, 0.012], 0.8, 0.6, 0.02), 0.0, 1.0),
                                      (tap(g, [1700.0, 2900.0], [0.02, 0.012], 0.8, 0.6, 0.02), 0.06, 1.0),
                                      (brass(g, 0.8, 0.4), 0.12, 1.0), (glass_ring(g, 2349.0, 1.0, 0.6), 0.2, 1.0),
                                      (glass_ring(g, 3520.0, 0.8, 0.3), 0.21, 1.0), (hum(g, 0.9, 587.0, 0.25), 0.22, 1.0)),
                        CAST),
}


FILES = [f"abl_{e}.ogg" for e in FINISHERS]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for k, (e, (fn, tgt)) in enumerate(FINISHERS.items()):
        seed = A.SEED + 100 * (len(A.JOBS) + k)  # where these jobs sat at the end of act1_ability_sfx's JOBS
        x = finish(room(fn(rng(seed)), seed + 7, mix=0.1, tail=0.3, rt60=0.7), tgt)
        write_ogg(os.path.join(out_dir, f"abl_{e}.ogg"), x, quality=4.0)
        res[e] = measure(x)
        if verbose:
            print(f"battle/abl_{e}: {res[e]['seconds']:.2f}s  Mmax {res[e]['momentary_max_lufs']:.2f}", flush=True)
    return res


if __name__ == "__main__":
    render()
