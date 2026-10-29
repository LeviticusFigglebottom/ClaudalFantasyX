"""The Vowbound's own sounds: Ilun the Net-Warden (M3-AUD-846), Kahre the Forge-Crowned and Virel the Kite-Serpent
(M3-AUD-857). Ilun's own sounds: his voice in battle and his layers on the summon's rise, call and
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

Kahre (docs/kb/art/creatures/vowbound/kahre.md) is Daro Pemakan's glimmer, a 3.4 m hornbill-headed smith-beast whose
chest is an anvil, with a mane of running sparks and a smith's hammer fused into his casque: the keepsake. Lightning,
weight and work. So: a ground hornbill's low boom for his voice, the mane's spark-crackle, thunder for his strikes, his
knuckle-walk as heavy thumps, and the hammer on the anvil (an iron ring on A4) at every moment that matters, struck
twice like a smith's tap before the blow.
Virel (docs/kb/art/creatures/vowbound/virel.md) is Wenna Corr's glimmer, a Saltwright signal kite flown alight: a
ribbon-serpent of sailcloth panels with bound light along every seam and a brass tuning key on the bridle knot, the
keepsake. Fire carried on wind. So: taut cloth luffing and snapping, a flare's breath of flame, and the key's small
brass ping. She flies; her movement is the cloth filling, never steps.
    kahre_<event>_<n>, virel_<event>_<n> in creatures/ (step / drift for movement), and kahre_rise / call / sink,
    virel_rise / call / sink in choreo/, at the same targets as Ilun's.

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

from act2_creature_sfx import BRASS, BRASS_DECAY, Ray, splash, tinkle, whoosh  # noqa: E402
from creature_sfx import (IDLE, MOVE, VOICE, buf, burst, crackle, finish, glass_ring, room, slosh, tap,  # noqa: E402
                          throat, thump, unit)
from creature_sfx import glide as bend  # noqa: E402  (Ilun's glide() below is his movement)
from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, bubble_train, noise, place  # noqa: E402

CREATURE_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "creatures")
CHOREO_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "choreo")
SEED = 20261846
LAYER = -22.0
FLOAT_HZ = 659.26   # E5: the net-float's chime
ANVIL_HZ = 440.0    # A4: Kahre's hammer on his anvil
KEY_SCALE = 1.6     # Virel's brass key: the act2 brass partials a little over an octave and a half up (672 Hz)


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


# --------------------------------------------------------------------------- Kahre the Forge-Crowned


def anvil(g, amp: float = 1.0, ring: float = 0.9) -> np.ndarray:
    """The hammer on the anvil: an iron ring on A4 (a struck bar's partials), with the strike's click."""
    x = buf(ring * 6 + 0.2)
    place(x, tap(g, [ANVIL_HZ * r for r in (1.0, 2.71, 5.15, 8.2)], [ring, ring * 0.6, ring * 0.35, ring * 0.2], 1.0,
                 0.7, 0.01), 0.0)
    place(x, burst(g, 0.05, [bq_bandpass(2400, 0.8)], 0.0005, 0.012), 0.0, 0.5)
    return amp * x


def smith_tap(g, amp: float = 1.0) -> np.ndarray:
    """A smith's tap-tap: a light touch on the anvil, then the full ring."""
    x = buf(6.0)
    place(x, anvil(g, 0.35, 0.25), 0.0)
    place(x, anvil(g, 1.0, 0.9), 0.32)
    return amp * x


def sparks(g, sec: float, rate: float = 60.0, amp: float = 1.0, tau: float = 0.0) -> np.ndarray:
    """The mane of running sparks: bright bound-light crackle, high and dry."""
    return amp * (0.7 * crackle(g, sec, rate, 5200, 1.1, tau) + 0.3 * crackle(g, sec, rate * 0.4, 2600, 0.9, tau))


def thunder(g, sec: float, amp: float = 1.0, fc: float = 260.0) -> np.ndarray:
    """A roll of thunder: a crack of broadband noise, then low noise rumbling down in irregular swells."""
    n = _n(sec)
    t = _t(n)
    rumble = noise(g, n, [bq_lowpass(fc, 0.7), bq_highpass(30, 0.7)])
    swell = np.ones(n)
    for _ in range(4):
        c, w = float(g.uniform(0.1, 0.7)) * sec, float(g.uniform(0.15, 0.4)) * sec
        swell += float(g.uniform(0.4, 1.0)) * np.exp(-((t - c) / w) ** 2)
    env = np.clip(t / 0.03, 0, 1) * np.exp(-t / (sec * 0.35))
    x = unit(rumble * swell) * env
    place(x, 0.5 * burst(g, 0.25, [bq_highpass(900, 0.7)], 0.001, 0.05), 0.0)
    return amp * x


def boom(g, sec: float, f0, amp: float = 1.0) -> np.ndarray:
    """A ground hornbill's boom, grown to his size: a low hollow hoot through a long bill."""
    contour = f0 if callable(f0) else bend(f0, f0 * 0.94)  # a boom sags a little as it ends
    return amp * throat(g, sec, contour, [(320, 110, 1.0), (760, 180, 0.25)], rough=0.08, sub=0.5, breath=0.25,
                        jitter=0.01, attack=sec * 0.35, release=sec * 0.4, tilt=1.6)


def knuckle(g, amp: float = 1.0) -> np.ndarray:
    """One fist planted: a heavy low thump on the water, a little spray, a flick from the mane."""
    x = buf(0.9)
    place(x, thump(g, 120, 52, 0.09, 0.35, 0.6), 0.0)
    place(x, slosh(g, 0.5, 0.3, 3.0), 0.02)
    place(x, sparks(g, 0.3, 40, 0.12, 0.1), 0.03)
    return amp * x


def kahre_idle(g):
    x = buf(3.6)
    place(x, boom(g, 0.9, 88), 0.1)
    place(x, boom(g, 0.8, 84, 0.8), 1.25)
    place(x, sparks(g, 3.0, 30, 0.12), 0.0)
    return x


def kahre_attack(g, v):
    """His Attack and Forge Bolt: the whole body into one blow, the hammer coming down, a crack of thunder off the anvil."""
    x = buf(4.0)
    place(x, whoosh(g, 0.4, 1800, 400, 0.6), 0.0)
    place(x, thump(g, 150, 45, 0.14, 0.5, 0.8), 0.38)
    place(x, anvil(g, 0.8, 0.7), 0.38)
    place(x, sparks(g, 0.8, 140, 0.5, 0.25), 0.39)
    place(x, thunder(g, 2.6 + 0.4 * v, 0.7, 220 + 60 * v), 0.42)
    return x


def kahre_hurt(g, v):
    x = buf(1.5)
    place(x, boom(g, 0.4, 100 + 8 * v, 0.9), 0.0)
    place(x, sparks(g, 0.5, 160, 0.5, 0.12), 0.0)
    place(x, anvil(g, 0.25, 0.2), 0.04)
    return x


def kahre_death(g):
    """He falls: a long boom going down, the mane's sparks dying out, the fists giving way, the anvil rung once."""
    x = buf(5.2)
    place(x, boom(g, 1.6, bend(92, 62, 0.8)), 0.0)
    place(x, sparks(g, 2.2, 90, 0.4, 0.6), 0.1)
    place(x, knuckle(g, 0.9), 1.1)
    place(x, thump(g, 110, 38, 0.3, 0.4, 1.2), 1.6)
    place(x, anvil(g, 0.7, 1.1), 1.9)
    return x


def kahre_step(g, v):
    x = buf(1.5)
    place(x, knuckle(g, 1.0), 0.0)
    place(x, knuckle(g, 0.7 + 0.1 * v), 0.55)
    return x


def kahre_rise(g):
    """He stands up out of the water: thunder rolling in, the mane catching spark by spark, the hammer rung on his mark."""
    x = buf(4.6)
    place(x, thunder(g, 2.4, 0.5, 180), 0.0)
    n = _n(1.6)
    place(x, sparks(g, 1.6, 120, 0.4) * np.clip(_t(n) / 1.4, 0, 1), 0.3)
    place(x, slosh(g, 1.4, 0.6, 1.2), 0.2)
    place(x, smith_tap(g, 0.9), 1.5)
    return x


def kahre_call(g):
    x = buf(4.0)
    place(x, smith_tap(g, 1.0), 0.0)
    place(x, sparks(g, 0.8, 60, 0.12, 0.3), 0.33)
    return x


def kahre_sink(g):
    """Dismissed: one ring of the anvil, the sparks going out, the thunder rolling away."""
    x = buf(4.0)
    place(x, anvil(g, 0.8, 1.0), 0.0)
    place(x, sparks(g, 1.2, 60, 0.25, 0.35), 0.05)
    place(x, thunder(g, 2.6, 0.35, 150), 0.4)
    return x


# --------------------------------------------------------------------------- Virel the Kite-Serpent


def key(g, amp: float = 1.0, ring: float = 1.4) -> np.ndarray:
    """The brass tuning key on the bridle knot: a small brass ping, swinging on its cord."""
    x = buf(ring * 0.35 * 6 + 0.2)
    place(x, tap(g, [f * KEY_SCALE for f in BRASS], [d * ring for d in BRASS_DECAY], 1.0, 0.4, 0.01), 0.0)
    return amp * x


def luff(g, sec: float, rate: float = 14.0, amp: float = 1.0, fc: float = 900.0, swell: bool = False) -> np.ndarray:
    """Sailcloth on a taut frame: the panels luffing in the wind, a fast flutter of filtered noise."""
    n = _n(sec)
    t = _t(n)
    nz = noise(g, n, [bq_bandpass(fc, 0.6), bq_lowpass(fc * 3, 0.7)])
    r = rate * (1 + 0.08 * np.sin(2 * np.pi * 0.7 * t + float(g.uniform(0, 6.28))))
    flutter = (0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(r) / len(t) * sec))) ** 2
    env = np.sin(np.pi * np.clip(t / sec, 0, 1)) if swell else np.clip(t / 0.08, 0, 1) * np.clip((sec - t) / 0.2, 0, 1)
    return amp * unit(nz * flutter) * env


def snap(g, amp: float = 1.0) -> np.ndarray:
    """A panel filling all at once: a hard cloth snap."""
    return amp * burst(g, 0.12, [bq_bandpass(1300, 0.7), bq_highpass(250, 0.7)], 0.0008, 0.018)


def flame(g, sec: float, amp: float = 1.0, fc: float = 800.0, rate: float = 35.0) -> np.ndarray:
    """The seams' fire: a soft breath of flame (low noise, slowly wavering) with small crackles in it."""
    n = _n(sec)
    t = _t(n)
    body = noise(g, n, [bq_lowpass(fc, 0.7), bq_highpass(90, 0.7)])
    waver = 1 + 0.3 * np.sin(2 * np.pi * 3.1 * t + float(g.uniform(0, 6.28)))
    env = np.clip(t / 0.15, 0, 1) * np.clip((sec - t) / 0.3, 0, 1)
    return amp * (unit(body * waver) * env + 0.35 * crackle(g, sec, rate, 3200, 0.9) * env)


def flare(g, sec: float, amp: float = 1.0) -> np.ndarray:
    """A flare thrown: a rising whoosh of fire that bursts and burns off."""
    x = buf(sec + 0.6)
    place(x, whoosh(g, sec * 0.45, 300, 2600, 0.8), 0.0)
    place(x, burst(g, sec * 0.6, [bq_lowpass(2400, 0.7), bq_highpass(150, 0.7)], 0.01, sec * 0.15), sec * 0.4)
    place(x, flame(g, sec * 0.6, 0.5, 1400, 90), sec * 0.42)
    return amp * x


def virel_idle(g):
    x = buf(3.2)
    place(x, luff(g, 2.8, 11.0, 0.5, swell=True), 0.0)
    place(x, flame(g, 2.8, 0.25), 0.1)
    place(x, key(g, 0.35), 1.7)
    return x


def virel_attack(g, v):
    """Her Attack and Kite Flare: the cloth snaps taut and a flare goes off the line, fast."""
    x = buf(2.0)
    place(x, snap(g, 0.8), 0.0)
    place(x, luff(g, 0.4, 20.0, 0.4), 0.02)
    place(x, flare(g, 0.7 + 0.1 * v, 0.9), 0.08)
    return x


def virel_hurt(g, v):
    x = buf(1.3)
    place(x, snap(g, 1.0), 0.0)
    place(x, luff(g, 0.7, 22.0 + 3 * v, 0.6), 0.01)
    place(x, key(g, 0.4, 0.5), 0.05)
    place(x, key(g, 0.25, 0.4), 0.17)
    return x


def virel_death(g):
    """She falls: the wind going out of the cloth, the seams' fire guttering, the key ringing once as she comes down."""
    x = buf(4.4)
    n = _n(2.6)
    slack = np.linspace(1.0, 0.0, n) ** 0.7
    place(x, luff(g, 2.6, 16.0, 0.8) * slack, 0.0)
    place(x, flame(g, 2.2, 0.5, 900, 60) * np.linspace(1.0, 0.0, _n(2.2)), 0.1)
    place(x, whoosh(g, 1.3, 1500, 250, 0.4), 1.0)
    place(x, key(g, 0.6, 2.2), 2.1)
    return x


def virel_drift(g, v):
    x = buf(1.8)
    place(x, luff(g, 1.5, 12.0 + 2 * v, 1.0, swell=True), 0.0)
    place(x, snap(g, 0.2), 0.5)
    return x


def virel_rise(g):
    """She lifts out of the water like a kite into wind: the cloth filling panel by panel, each seam catching alight,
    the key chiming as she takes her mark."""
    x = buf(3.8)
    n = _n(2.0)
    place(x, luff(g, 2.0, 10.0, 0.7) * np.clip(_t(n) / 1.6, 0, 1), 0.0)
    place(x, whoosh(g, 1.6, 350, 1600, 0.4), 0.1)
    for i in range(4):
        place(x, snap(g, 0.25 + 0.1 * i), 0.3 + 0.32 * i)
    place(x, flame(g, 1.8, 0.35) * np.clip(_t(_n(1.8)) / 1.0, 0, 1), 0.5)
    place(x, key(g, 0.8, 1.6), 1.8)
    return x


def virel_call(g):
    x = buf(2.6)
    place(x, key(g, 1.0, 1.4), 0.0)
    place(x, key(g, 0.45, 1.0), 0.28)
    place(x, flame(g, 1.0, 0.12), 0.1)
    return x


def virel_sink(g):
    """Dismissed: the key's ping, the cloth going slack, the fire out."""
    x = buf(3.4)
    place(x, key(g, 0.8, 1.6), 0.0)
    n = _n(1.8)
    place(x, luff(g, 1.8, 13.0, 0.6) * np.linspace(1.0, 0.0, n), 0.2)
    place(x, flame(g, 1.4, 0.3) * np.linspace(1.0, 0.0, _n(1.4)), 0.1)
    place(x, slosh(g, 1.2, 0.4, 0.9), 1.4)
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
    (CREATURE_DIR, "kahre_idle_1", _voice(kahre_idle, SEED + 101), IDLE),
    (CREATURE_DIR, "kahre_attack_1", _voice(lambda g: kahre_attack(g, 0), SEED + 102), VOICE),
    (CREATURE_DIR, "kahre_attack_2", _voice(lambda g: kahre_attack(g, 1), SEED + 103), VOICE),
    (CREATURE_DIR, "kahre_hurt_1", _voice(lambda g: kahre_hurt(g, 0), SEED + 104), VOICE),
    (CREATURE_DIR, "kahre_hurt_2", _voice(lambda g: kahre_hurt(g, 1), SEED + 105), VOICE),
    (CREATURE_DIR, "kahre_death_1", _voice(kahre_death, SEED + 106), VOICE),
    (CREATURE_DIR, "kahre_step_1", _voice(lambda g: kahre_step(g, 0), SEED + 107), MOVE),
    (CREATURE_DIR, "kahre_step_2", _voice(lambda g: kahre_step(g, 1), SEED + 108), MOVE),
    (CHOREO_DIR, "kahre_rise", _voice(kahre_rise, SEED + 111), LAYER),
    (CHOREO_DIR, "kahre_call", _voice(kahre_call, SEED + 112), LAYER),
    (CHOREO_DIR, "kahre_sink", _voice(kahre_sink, SEED + 113), LAYER),
    (CREATURE_DIR, "virel_idle_1", _voice(virel_idle, SEED + 201), IDLE),
    (CREATURE_DIR, "virel_attack_1", _voice(lambda g: virel_attack(g, 0), SEED + 202), VOICE),
    (CREATURE_DIR, "virel_attack_2", _voice(lambda g: virel_attack(g, 1), SEED + 203), VOICE),
    (CREATURE_DIR, "virel_hurt_1", _voice(lambda g: virel_hurt(g, 0), SEED + 204), VOICE),
    (CREATURE_DIR, "virel_hurt_2", _voice(lambda g: virel_hurt(g, 1), SEED + 205), VOICE),
    (CREATURE_DIR, "virel_death_1", _voice(virel_death, SEED + 206), VOICE),
    (CREATURE_DIR, "virel_drift_1", _voice(lambda g: virel_drift(g, 0), SEED + 207), MOVE),
    (CREATURE_DIR, "virel_drift_2", _voice(lambda g: virel_drift(g, 1), SEED + 208), MOVE),
    (CHOREO_DIR, "virel_rise", _voice(virel_rise, SEED + 211), LAYER),
    (CHOREO_DIR, "virel_call", _voice(virel_call, SEED + 212), LAYER),
    (CHOREO_DIR, "virel_sink", _voice(virel_sink, SEED + 213), LAYER),
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
