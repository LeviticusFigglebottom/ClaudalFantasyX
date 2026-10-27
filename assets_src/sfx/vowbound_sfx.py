"""Ilun the Net-Warden's own sounds (M3-AUD-846): his voice in battle and his layers on the summon's rise, call and
dismissal, for the model the creatures track is building (M3-CRE-638) and battle-presentation's summon choreography
(M3-BPR-417).

Ilun (docs/kb/story/vowbound.md §1) is a vast spectral manta ray with a heron's crest, his wings patterned like knotted
fishing net in light, and a child's glass net-float hanging from his tail: the keepsake. He is defensive water magic
and a tidal shield, and the first gentle goodbye. So his sound is broad, slow wing-water (the gallery ray's wing voice,
act2_creature_sfx.py, grown vast), the net's light as a faint glassy shimmer, and the net-float's small glass chime on E
(the Hush's key: A minor) at every moment that matters. Nothing in it is harsh: even his strike is a heavy sweep of
water, not a blow. All synthesized (SPEC §2, §9): no samples, no generated audio.

assets/audio/sfx/creatures/ilun_<event>_<n>.ogg (creature_voices.json `ilun`; CreatureAudio hears his actions,
hits and fall by his combatant id, and his model's clips once it lands):
    idle 1, attack 2, hurt 2, death 1   -20 / -18 LUFS (targets.py's creature rules)
    glide 1..2                          his movement, -21
assets/audio/sfx/choreo/ilun_<moment>.ogg (choreo_sfx.json `vowbound.layers.ilun`, played over the shared rows):
    ilun_rise   the wings unfolding out of the water, the net-light catching, the float chiming as he takes his mark
    ilun_call   the float's chime answering Asha's call
    ilun_sink   the dismissal: one soft chime, the water closing over the wings
                                        -22 LUFS (they sit under vowbound_rise / vowbound_beckon / vowbound_sink)

Render:  python3 assets_src/sfx/vowbound_sfx.py   (or tools/audio/render_all.py --only vowbound_sfx)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from act2_creature_sfx import Ray, splash, tinkle, whoosh  # noqa: E402
from creature_sfx import IDLE, MOVE, VOICE, buf, finish, glass_ring, room, slosh  # noqa: E402
from synth.dsp import rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, bubble_train, place  # noqa: E402

CREATURE_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "creatures")
CHOREO_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "choreo")
SEED = 20261846
LAYER = -22.0
FLOAT_HZ = 659.26   # E5: the net-float's chime


def chime(g, amp: float = 1.0, dur: float = 1.4) -> np.ndarray:
    """The glass net-float: a small, clear glass ring on E5 with its octave faint above it."""
    x = buf(dur + 0.1)
    place(x, glass_ring(g, FLOAT_HZ, dur, 1.0), 0.0)
    place(x, glass_ring(g, FLOAT_HZ * 2.0, dur * 0.6, 0.25), 0.004)
    return amp * x


def net_light(g, sec: float, amp: float = 1.0) -> np.ndarray:
    """The net's light catching: the ray's shimmer, a little brighter, with tiny glints along the knots."""
    x = buf(sec + 0.4)
    place(x, Ray.shimmer(g, sec, 1.0), 0.0)
    place(x, tinkle(g, sec * 0.8, 6, 2600, 4200, 0.25), sec * 0.1)
    return amp * x


def wings(g, count: int, rate: float, amp: float = 1.0) -> np.ndarray:
    """Vast wings: the ray's wingbeats slowed and lowered, a sheet of water running off each."""
    x = buf(count / rate + 1.0)
    place(x, Ray.wing(g, count, rate, 1.0), 0.0)
    for i in range(count):
        place(x, slosh(g, 0.8, 0.35, 2.0), i / rate + 0.08)
    return amp * x


# --------------------------------------------------------------------------- his voice (creatures folder)


def idle(g):
    x = buf(3.4)
    place(x, wings(g, 2, 0.8, 0.8), 0.0)
    place(x, net_light(g, 2.6, 0.1), 0.3)
    place(x, chime(g, 0.35), 1.6)
    return x


def attack(g, v):
    """A heavy sweep of water off one wing (his Attack and Brine Lash), never a blow."""
    x = buf(1.8)
    place(x, whoosh(g, 0.45, 500, 1500 + 200 * v, 0.8), 0.0)
    place(x, splash(g, 1.2, 0.9, 2200), 0.38)
    place(x, net_light(g, 0.6, 0.06), 0.4)
    return x


def hurt(g, v):
    x = buf(1.3)
    place(x, slosh(g, 0.8, 0.6, 3.0), 0.0)
    place(x, Ray.wing(g, 3, 5.0 + v, 0.6, 0.7), 0.02)
    place(x, chime(g, 0.3, 0.6), 0.05)
    return x


def death(g):
    """He falls: the wings fold, the net's light goes out downward, the float chimes once as it sinks."""
    x = buf(4.2)
    place(x, wings(g, 3, 1.6, 0.8), 0.0)
    place(x, whoosh(g, 1.4, 1600, 300, 0.6), 0.8)
    place(x, chime(g, 0.5, 2.0), 1.9)
    place(x, bubble_train(g, 10, 0.004, 0.009, (0.1, 0.2), 0.4, 0.7), 2.2)
    return x


def glide(g, v):
    x = buf(1.8)
    place(x, wings(g, 1, 0.9 + 0.1 * v, 1.0), 0.0)
    return x


# --------------------------------------------------------------------------- the summon's layers (choreo folder)


def rise(g):
    """Out of the water: a sheet of water lifting off the wings, the net-light catching, the float chiming on the mark."""
    x = buf(3.2)
    n = _n(2.0)
    lift = slosh(g, 2.0, 1.0, 0.9) * np.clip(_t(n) / 1.2, 0, 1)
    place(x, lift, 0.0)
    place(x, whoosh(g, 1.6, 400, 1800, 0.6), 0.2)
    place(x, net_light(g, 1.8, 0.12), 0.6)
    place(x, chime(g, 0.8, 1.6), 1.6)
    return x


def call(g):
    x = buf(2.0)
    place(x, chime(g, 1.0, 1.6), 0.0)
    place(x, net_light(g, 1.2, 0.08), 0.1)
    return x


def sink(g):
    """Dismissed: one soft chime, then the water closing over the wings."""
    x = buf(2.6)
    place(x, chime(g, 0.8, 1.4), 0.0)
    place(x, slosh(g, 1.6, 0.8, 0.8), 0.5)
    place(x, bubble_train(g, 6, 0.004, 0.008, (0.12, 0.2), 0.3, 0.7), 0.9)
    return x


def _voice(fn, seed):
    def f():
        x = fn(rng(seed))
        return room(x, seed + 7, mix=0.18, tail=0.7, rt60=1.4)  # he is vast, and the shrine's water is wide
    return f


JOBS: list[tuple[str, str, object, float]] = [
    (CREATURE_DIR, "ilun_idle_1", _voice(idle, SEED + 1), IDLE),
    (CREATURE_DIR, "ilun_attack_1", _voice(lambda g: attack(g, 0), SEED + 2), VOICE),
    (CREATURE_DIR, "ilun_attack_2", _voice(lambda g: attack(g, 1), SEED + 3), VOICE),
    (CREATURE_DIR, "ilun_hurt_1", _voice(lambda g: hurt(g, 0), SEED + 4), VOICE),
    (CREATURE_DIR, "ilun_hurt_2", _voice(lambda g: hurt(g, 1), SEED + 5), VOICE),
    (CREATURE_DIR, "ilun_death_1", _voice(death, SEED + 6), VOICE),
    (CREATURE_DIR, "ilun_glide_1", _voice(lambda g: glide(g, 0), SEED + 7), MOVE),
    (CREATURE_DIR, "ilun_glide_2", _voice(lambda g: glide(g, 1), SEED + 8), MOVE),
    (CHOREO_DIR, "ilun_rise", _voice(rise, SEED + 11), LAYER),
    (CHOREO_DIR, "ilun_call", _voice(call, SEED + 12), LAYER),
    (CHOREO_DIR, "ilun_sink", _voice(sink, SEED + 13), LAYER),
]
# render_all.py renders into assets/audio/sfx and names each file relative to it
FILES = [os.path.relpath(os.path.join(d, n + ".ogg"), os.path.join(ROOT, "assets", "audio", "sfx")) for d, n, _, _ in JOBS]


def render(out_dir: str = os.path.join(ROOT, "assets", "audio", "sfx"), verbose: bool = True) -> dict:
    res = {}
    for d, name, fn, target in JOBS:
        sub = os.path.relpath(d, os.path.join(ROOT, "assets", "audio", "sfx"))
        path = os.path.join(out_dir, sub, name + ".ogg")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        x = finish(fn(), target)
        write_ogg(path, x, quality=4.0)
        res[name] = measure(x)
        if verbose:
            m = res[name]
            print(f"{sub}/{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  peak {m['sample_peak_dbfs']:.2f}")
    return res


if __name__ == "__main__":
    render()
