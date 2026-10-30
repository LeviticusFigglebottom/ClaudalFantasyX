"""Act II creature voices and movement (M3-AUD-831): the Ch10-12 bosses, the Wakefin and the Ch10-11 regulars the
creatures track built from its sheets (docs/kb/art/creatures/act2/; M3-CRE-621, 623, 624, 626, 627).

Same rules and building blocks as creature_sfx.py (its docstring): synthesized here and in tools/audio/synth/
(SPEC §2, §9), no samples, no recordings, no generated audio, and no real animal's call copied. A separate source
with its own seed, so the Act I set renders byte for byte as before.

    mangrove_drowner  Ch10 boss: a dome of prop-roots round a wet core. Its roots creak like a moored hull, the drag
                      hauls water, and a low spawn moan sits under it; its death lets the roots go one by one.
    lamp_engine       Ch11 boss, a Lit Age construct: brass rings on ratchets, scissor arms that snip, twelve
                      salt-glass lamps that chime when they swing, and a steady hum (its bound light does not pulse,
                      so neither does the hum, until it dies and winds down).
    avalanche_ram     Ch12 boss: an Ullari woolback grown huge. A deep nasal bellow (formants of a long throat, not any
                      real animal's call), it chews, its hooves are broad pads on packed snow, and its wet, matted
                      locks shed water (ADR 0204 §2: no ice).
    wakefin           Ch15 boss: a spawn sailfish that is mostly a blade cutting the water. Its voice is the water:
                      the hiss of the cut, the breach, the slap of the blade; a sub thrum is the spawn in it.
    tannin_archer     Ch10: an archerfish on a mangrove root. Sculling fins, a gill click, the spit (a pressured jet
                      and its droplets), the tail slapping the water.
    gallery_ray       Ch11: a ray gliding through the air between pools. Slow wing air, a faint glassy shimmer (its
                      margin's sea-glow), the wing's slap.
    rime_urchin       Ch11: an urchin of salt-glass spines on a salt-glass plinth (re-materialled from ice, ADR
                      0015). Its spine field rattles glassy and brittle in wind; the stab cracks a spine.
    conduit_crawler   Ch11, a Lit Age construct: a small brass cleaner under a glass dome. Ticking tripod feet, a
                      bristle brush, a squeaking wiper, a faint steady hum.

assets/audio/sfx/creatures/<creature>_<event>_<n>.ogg (mono, Vorbis q4, <= -2.5 dBFS sample peak): voices -18 LUFS
momentary max, idles -20, movement -21 (targets.py's creature rules). Bosses have idle 1, attack 2, hurt 3, death 1,
movement 2; regulars idle 1, attack 2, hurt 2, death 1, movement 2. Rows: game/data/audio/sfx_creatures.json; who
sounds like what: game/data/audio/creature_voices.json.

Render:  python3 tools/audio/render_all.py --only act2_creature_sfx   (or python3 assets_src/sfx/act2_creature_sfx.py [filter])
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from creature_sfx import (IDLE, MOVE, OUT_DIR, QUALITY, VOICE, WOOD, beats, buf, burst, contour, crackle,  # noqa: E402
                          creak, finish, glass_ring, glide, gurgle, pop, roar, room, slosh, tap, thump, throat, train,
                          unit, wobble)
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, rng, smooth_noise  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.water import drip  # noqa: E402
from underwater_sfx import _n, _t, bubble_train, muffle, noise, place  # noqa: E402
from creature_sfx import Moth  # noqa: E402

SEED = 20261831
BOSSES = ("mangrove_drowner", "lamp_engine", "avalanche_ram", "wakefin", "flat_engine")
MOVE_WORD = {"drowner": "heave", "engine": "clank", "woolback": "trudge", "sailfin": "cut", "archer": "scull",
             "ray": "glide", "urchin": "rattle", "crawler": "tick",
             "lynx": "pad", "moth": "flutter", "skate": "glide", "flat_engine": "clank"}
CREATURES: dict[str, dict] = {
    "mangrove_drowner": dict(family="drowner", size=3.0, pitch=1.0, spawn=True),
    "lamp_engine": dict(family="engine", size=2.6, pitch=1.0),
    "avalanche_ram": dict(family="woolback", size=3.0, pitch=1.0),
    "wakefin": dict(family="sailfin", size=2.5, pitch=1.0, spawn=True),
    "tannin_archer": dict(family="archer", size=1.0, pitch=1.0),
    "gallery_ray": dict(family="ray", size=1.2, pitch=1.0),
    "rime_urchin": dict(family="urchin", size=0.9, pitch=1.0),
    "conduit_crawler": dict(family="crawler", size=0.6, pitch=1.0),
    # M3-AUD-849: the creatures added since (claude/creatures, M3-CRE-620's later builds); appended, so the first eight
    # keep their seeds and their bytes
    "ridge_lynx": dict(family="lynx", size=1.0, pitch=1.0),
    "cord_moth": dict(family="moth", size=1.0, pitch=1.05, rate=13.0),
    "glass_skate": dict(family="skate", size=1.1, pitch=1.0),
    "flat_engine": dict(family="flat_engine", size=2.2, pitch=0.85),
}


# --------------------------------------------------------------------------- shared pieces


def splash(g: np.random.Generator, sec: float, amp: float = 1.0, fc: float = 2600.0) -> np.ndarray:
    """A body breaking the surface: a broadband burst, a low plunge under it and droplets falling after."""
    x = buf(sec)
    place(x, burst(g, min(sec, 0.5), [bq_lowpass(fc * 2.5, 0.7), bq_highpass(300, 0.7)], 0.004, 0.09), 0.0)
    place(x, slosh(g, min(sec, 0.9), 0.8, 2.5), 0.0)
    for _ in range(int(g.integers(8, 16))):
        place(x, drip(0.25, float(g.uniform(0.8, 2.2)), seed=int(g.integers(1 << 30))),
              float(g.uniform(0.08, max(0.1, sec - 0.3))), float(g.uniform(0.15, 0.45)))
    return amp * x


def hum(g: np.random.Generator, sec: float, f0: float, amp: float = 1.0, bend: tuple[float, float] | None = None):
    """A Lit Age construct's bound light: a steady harmonic hum, two near partials beating slowly (it does not pulse).
    bend glides its pitch (from, to) as a ratio of f0, for a dying construct winding down."""
    n = _n(sec)
    t = _t(n)
    f = np.full(n, f0) if bend is None else f0 * glide(bend[0], bend[1], 0.7)(t / sec)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.45), (3, 0.2), (5, 0.08)):
        y += a * (np.sin(k * ph) + 0.6 * np.sin(k * ph * 1.003 + float(g.uniform(0, 6.28))))
    env = np.clip(t / 0.15, 0, 1) * np.clip((sec - t) / 0.2, 0, 1)
    return amp * unit(y) * env


def whoosh(g: np.random.Generator, sec: float, f_from: float, f_to: float, amp: float = 1.0) -> np.ndarray:
    """Air moved by a broad surface: noise whose band glides f_from -> f_to, swelling to the middle."""
    n = _n(sec)
    t = _t(n)
    nz = noise(g, n, [bq_lowpass(max(f_from, f_to) * 1.6, 0.7), bq_highpass(min(f_from, f_to) * 0.4, 0.7)])
    lo = muffle(nz, max(f_from, f_to) * 1.4, min(f_from, f_to) * 1.4, 0.0, sec) if f_to < f_from else nz
    env = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2
    return amp * unit(lo) * env


def moan(g: np.random.Generator, sec: float, f0, amp: float = 1.0) -> np.ndarray:
    """The low spawn moan under an Undertow-spawn (as creature_sfx's spawn voices)."""
    return amp * throat(g, sec, f0, [(260, 110, 1.0), (620, 160, 0.4), (1900, 400, 0.08)], rough=0.25, sub=0.3,
                        breath=1.0, jitter=0.03, attack=sec * 0.3, release=sec * 0.35, tilt=1.3)


BRASS = [420.0, 1130.0, 2050.0, 3300.0, 4870.0]
BRASS_DECAY = [0.35, 0.22, 0.14, 0.09, 0.06]
ICE = [3150.0, 4400.0, 6100.0, 8200.0]
ICE_DECAY = [0.05, 0.035, 0.025, 0.018]
SALT_GLASS = [2350.0, 3870.0, 5520.0, 7690.0]      # the rime urchin's salt-glass spines: lower, longer than ice
SALT_GLASS_DECAY = [0.11, 0.07, 0.045, 0.028]


def clang(g: np.random.Generator, scale: float, amp: float = 1.0, ring: float = 1.0) -> np.ndarray:
    return tap(g, [f * scale for f in BRASS], [d * ring for d in BRASS_DECAY], amp, 0.6, 0.03)


def tinkle(g: np.random.Generator, sec: float, count: int, f_lo: float, f_hi: float, amp: float = 1.0):
    """Ice or glass knocking together: short rings at random times."""
    x = buf(sec + 0.4)
    for _ in range(count):
        place(x, glass_ring(g, float(g.uniform(f_lo, f_hi)), float(g.uniform(0.12, 0.35)), float(g.uniform(0.3, 1.0))),
              float(g.uniform(0, sec)))
    return amp * x


# --------------------------------------------------------------------------- families
# Each family has idle(p, v, g), attack, hurt, death and move, like creature_sfx.py's.


class Drowner:
    """The Mangrove Drowner: twelve arched prop-roots round a wet black core, standing in the tide."""

    ROOT = [(f * 0.55, a) for f, a in WOOD]

    @classmethod
    def knock(cls, g, amp=1.0):
        return tap(g, [f for f, _ in cls.ROOT], [0.05, 0.035, 0.025, 0.015], amp, 0.7)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(3.4)
        place(x, slosh(g, 3.2, 0.6, 0.45), 0.0)
        place(x, moan(g, 2.6, wobble(58, 0.04, 0.6, g), 0.55), 0.3)
        place(x, creak(g, 1.0, 18, 70, cls.ROOT, 0.5), 0.5)
        place(x, creak(g, 0.8, 22, 85, cls.ROOT, 0.35), 1.9)
        for at in (0.9, 1.6, 2.6):
            place(x, drip(0.4, float(g.uniform(1.2, 2.0)), seed=int(g.integers(1 << 30))), at, 0.6)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """The drag: two roots reach out along the water and haul back (contact 0.7 s of 1.4 s)."""
        x = buf(2.4)
        place(x, creak(g, 0.7, 25 + 6 * v, 110, cls.ROOT, 0.8), 0.0)
        drag = roar(g, 1.0, 650) * np.sin(np.pi * np.clip(_t(_n(1.0)) / 1.0, 0, 1)) ** 1.5
        place(x, drag, 0.2, 0.8)
        place(x, slosh(g, 1.4, 1.0, 1.4), 0.65)
        place(x, cls.knock(g, 0.9), 0.7)
        place(x, cls.knock(g, 0.6), 0.76)
        place(x, moan(g, 0.9, contour(60, 82, 55, 0.4), 0.6), 0.4)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        """The cage shudders and the core recoils."""
        x = buf(1.4)
        for i in range(int(g.integers(5, 9))):
            place(x, cls.knock(g, float(g.uniform(0.4, 1.0))), 0.012 * i * (1 + v) + float(g.uniform(0, 0.03)))
        place(x, moan(g, 0.7, contour(70 + 6 * v, 95 + 8 * v, 60, 0.25), 0.8), 0.03)
        place(x, slosh(g, 0.9, 0.45, 3.0), 0.05)
        return x

    @classmethod
    def death(cls, p, v, g):
        """The roots let go one by one and splay out as it sinks."""
        x = buf(5.6)
        tt = 0.2
        for i in range(6):
            place(x, creak(g, 0.35, 30, 140 - 10 * i, cls.ROOT, 0.6), tt)
            place(x, cls.knock(g, 1.0), tt + 0.33)
            place(x, splash(g, 0.8, 0.55, 1600), tt + 0.38)
            tt += float(g.uniform(0.32, 0.5))
        place(x, moan(g, 3.2, glide(70, 38, 1.2), 0.9), 0.1)
        place(x, gurgle(g, 2.4, 22, 0.006, 0.02, 0.8), tt)
        place(x, bubble_train(g, 14, 0.004, 0.009, (0.08, 0.2), 0.5, 0.7), tt + 0.6)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.8)
        place(x, creak(g, 0.9, 20 + 5 * v, 90, cls.ROOT, 0.7), 0.0)
        place(x, slosh(g, 1.5, 0.9, 1.2), 0.2)
        return x


class Engine:
    """The Lamp Engine: a brass bell-hooded tower of gimballed rings, twelve salt-glass lamps and two shear arms."""

    @staticmethod
    def ratchet(g, sec, r0, r1, amp=1.0):
        return amp * train(g, sec, r0, r1, [2600, 3900, 5800], [0.006, 0.004, 0.003], 0.9, 0.08, 0.7)

    @staticmethod
    def snip(g, amp=1.0):
        """The shears closing: a bright blade scrape into two metal ticks."""
        x = buf(0.3)
        place(x, burst(g, 0.12, [bq_bandpass(5200, 1.4)], 0.03, 0.03), 0.0, 0.5)
        place(x, tap(g, [3100, 4700, 7200], [0.04, 0.03, 0.02], 1.0, 0.8, 0.02), 0.09)
        place(x, tap(g, [3300, 5100, 7600], [0.05, 0.03, 0.02], 0.8, 0.8, 0.02), 0.105)
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(3.4)
        place(x, hum(g, 3.3, 98.0, 0.5), 0.0)
        place(x, cls.ratchet(g, 1.2, 9, 7, 0.35), 0.2)
        place(x, cls.ratchet(g, 0.9, 7, 9, 0.3), 1.9)
        place(x, cls.snip(g, 0.3), 1.2)
        place(x, cls.snip(g, 0.25), 2.6)
        place(x, tinkle(g, 2.6, 3, 1700, 2600, 0.35), 0.4)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """The trim: the right arm winds up with its shears open and snips forward (contact 0.6 s of 1.3 s)."""
        x = buf(1.8)
        place(x, hum(g, 1.7, 98.0, 0.35), 0.0)
        place(x, cls.ratchet(g, 0.5, 6, 24 + 4 * v, 0.7), 0.05)
        place(x, whoosh(g, 0.3, 1800, 4200, 0.45), 0.35)
        place(x, cls.snip(g, 1.0), 0.53)
        place(x, clang(g, 1.0 + 0.04 * v, 0.6, 0.6), 0.62)
        place(x, tinkle(g, 0.5, 3, 1700, 2700, 0.4), 0.65)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        """The rings jolt and a lamp swings loose on its gimbal."""
        x = buf(1.6)
        place(x, clang(g, 0.92 + 0.06 * v, 1.0, 1.0), 0.0)
        place(x, cls.ratchet(g, 0.25, 30, 12, 0.5), 0.02)
        place(x, tinkle(g, 0.9, 5 + v, 1600, 2800, 0.7), 0.05)
        place(x, hum(g, 1.2, 98.0, 0.3, (1.0, 0.97)), 0.0)
        return x

    @classmethod
    def death(cls, p, v, g):
        """The rings sag, the lamps hang, the arms drop into the water and the frame kneels; the hum winds down."""
        x = buf(5.0)
        place(x, hum(g, 3.6, 98.0, 0.7, (1.0, 0.45)), 0.0)
        place(x, cls.ratchet(g, 1.8, 14, 2.5, 0.6), 0.1)
        place(x, creak(g, 1.4, 12, 45, [(f * 0.4, 1.0 / (i + 1)) for i, f in enumerate(BRASS[:3])], 0.6), 0.3)
        place(x, tinkle(g, 2.0, 7, 1500, 2600, 0.5), 0.6)
        place(x, splash(g, 1.0, 0.7, 1800), 1.9)
        place(x, splash(g, 1.0, 0.6, 1800), 2.15)
        place(x, thump(g, 90, 45, 0.18, 0.5, 0.8), 2.9, 0.9)
        place(x, clang(g, 0.7, 0.6, 1.4), 2.92)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.6)
        for i, at in enumerate((0.0, 0.3, 0.62, 0.92)):
            place(x, thump(g, 140, 80, 0.05, 0.4, 0.25), at + 0.02 * v, 0.6)
            place(x, clang(g, 1.6 + 0.1 * (i % 2), 0.35, 0.3), at + 0.005)
        place(x, cls.ratchet(g, 1.0, 8, 8, 0.25), 0.1)
        return x


class Woolback:
    """The Avalanche Ram: an Ullari woolback grown huge, its locks wet and matted (ADR 0204 §2: no ice from Ch12 to
    Ch15; M4-A2P-093 replaced the ice that hung in its locks with the water they shed)."""

    F = [(380, 140, 1.0), (950, 220, 0.5), (2300, 420, 0.15)]

    @classmethod
    def bellow(cls, g, dur, f0, rough=0.4, amp=1.0):
        return amp * throat(g, dur, f0, cls.F, rough=rough, sub=0.35, breath=0.45, jitter=0.02, attack=0.08,
                            release=dur * 0.3, tilt=0.9, rough_hz=32.0)

    @staticmethod
    def snort(g, amp=1.0):
        return amp * burst(g, 0.25, [bq_bandpass(900, 0.8), bq_lowpass(3000, 0.7)], 0.01, 0.07)

    @staticmethod
    def hoof(g, amp=1.0):
        """A broad pad on packed snow: a low thud and a crunch."""
        x = buf(0.4)
        place(x, thump(g, 120, 55, 0.07, 0.4, 0.4), 0.0)
        place(x, crackle(g, 0.12, 900, 1600, 0.8, 0.04), 0.0, 0.35)
        return amp * x

    @staticmethod
    def locks(g, sec, amp=1.0):
        """The wet, matted locks swinging: a soft heavy swish."""
        return amp * whoosh(g, sec, 700, 1500)

    @staticmethod
    def wet(g, sec, amp=1.0):
        """Water shed from the matted wool: a soft spray and a few wet grains falling."""
        x = buf(sec + 0.3)
        place(x, burst(g, min(sec, 0.3), [bq_bandpass(1500, 0.7), bq_lowpass(3000, 0.7)], 0.005, 0.08), 0.0, 0.6)
        place(x, crackle(g, sec, 40, 1200, 0.8, sec * 0.4), 0.02, 0.3)
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(3.4)
        for i in range(5):  # it chews
            place(x, crackle(g, 0.18, 300, 700, 0.9, 0.06), 0.3 + 0.55 * i, 0.4)
        place(x, cls.bellow(g, 0.7, contour(72, 84, 66, 0.3), 0.6, 0.5), 2.4)
        place(x, cls.locks(g, 1.2, 0.3), 1.0)
        place(x, cls.wet(g, 2.8, 0.3), 0.2)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """The charge: the head drops, a fore hoof stamps, and it drives through (contact 0.75 s)."""
        x = buf(2.2)
        place(x, cls.snort(g, 0.9), 0.0)
        place(x, cls.hoof(g, 0.9), 0.28)
        rumble = roar(g, 0.6, 260) * np.clip(_t(_n(0.6)) / 0.5, 0, 1) ** 1.5
        place(x, rumble, 0.3, 0.6)
        place(x, cls.locks(g, 0.6, 0.5), 0.35)
        place(x, thump(g, 95, 38, 0.2, 0.7, 0.8), 0.75, 1.0)
        place(x, cls.wet(g, 0.4, 0.6), 0.76)
        place(x, cls.bellow(g, 0.6, contour(80 + 6 * v, 110, 75, 0.3), 0.5, 0.6), 0.85)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(1.4)
        place(x, cls.bellow(g, 0.55, contour(95 + 8 * v, 140 + 10 * v, 85, 0.25), 0.3, 1.0), 0.0)
        place(x, cls.wet(g, 0.3, 0.7), 0.02)
        place(x, crackle(g, 0.15, 1200, 3200, 1.0, 0.04), 0.02, 0.4)
        place(x, cls.locks(g, 0.5, 0.4), 0.05)
        return x

    @classmethod
    def death(cls, p, v, g):
        """It kneels on its fore knees, lies down with its legs folded under it and lays its head down."""
        x = buf(5.4)
        place(x, cls.bellow(g, 1.6, glide(105, 62, 1.1), 0.5, 0.9), 0.0)
        place(x, thump(g, 85, 40, 0.2, 0.5, 0.7), 1.0, 0.9)
        place(x, thump(g, 80, 38, 0.22, 0.5, 0.7), 1.25, 0.8)
        place(x, cls.locks(g, 1.4, 0.5), 1.6)
        place(x, thump(g, 70, 32, 0.35, 0.6, 1.0), 2.4, 1.0)
        place(x, cls.wet(g, 1.2, 0.4), 2.4)
        exhale = burst(g, 1.6, [bq_bandpass(700, 0.7), bq_lowpass(2000, 0.7)], 0.3, 0.6)
        place(x, exhale, 3.2, 0.45)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.8)
        for i, at in enumerate((0.0, 0.42, 0.85, 1.25)):
            place(x, cls.hoof(g, float(g.uniform(0.6, 1.0))), at + 0.02 * v * i)
        place(x, cls.locks(g, 1.5, 0.35), 0.1)
        return x


class Sailfin:
    """The Wakefin: a spawn sailfish, mostly a tall swept blade cutting the water."""

    @staticmethod
    def cut(g, sec, amp=1.0):
        """The blade through the water: a hiss that swells and thins, a low wake under it."""
        n = _n(sec)
        t = _t(n)
        hiss = unit(noise(g, n, [bq_bandpass(2400, 0.9), bq_highpass(900, 0.7)])) * (
            0.7 + 0.3 * smooth_noise(n, 14.0, g))
        env = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 1.2
        wake = unit(noise(g, n, [bq_lowpass(380, 0.7), bq_highpass(45, 0.7)]))
        return amp * (0.7 * hiss + 0.5 * wake) * env

    @staticmethod
    def thrum(g, f0=48.0, sec=0.8, amp=1.0):
        t = _t(_n(sec))
        y = np.sin(2 * np.pi * f0 * t) * (1 + 0.3 * np.sin(2 * np.pi * 7 * t))
        return amp * y * np.clip(t / 0.03, 0, 1) * np.exp(-t / (sec * 0.35))

    @classmethod
    def idle(cls, p, v, g):
        x = buf(3.4)
        place(x, cls.cut(g, 1.5, 0.6), 0.1)
        place(x, cls.cut(g, 1.4, 0.5), 1.8)
        place(x, moan(g, 2.2, wobble(52, 0.03, 0.8, g), 0.35), 0.6)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """The breach and the sweep: it sinks, drives up out of the water, the blade sweeps the deck (0.8 s)."""
        x = buf(2.4)
        place(x, gurgle(g, 0.4, 18, 0.006, 0.016, 0.5), 0.0)
        place(x, roar(g, 0.3, 900) * np.linspace(0.2, 1.0, _n(0.3)), 0.3, 0.6)
        place(x, splash(g, 1.2, 1.0, 3000), 0.55)
        place(x, whoosh(g, 0.35, 900 + 200 * v, 3200, 0.9), 0.65)
        place(x, burst(g, 0.1, [bq_bandpass(1600, 1.0)], 0.002, 0.03), 0.8, 0.7)
        place(x, splash(g, 1.0, 0.8, 2200), 1.2)
        place(x, cls.thrum(g, 46, 0.7, 0.6), 0.8)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(1.2)
        place(x, splash(g, 0.8, 0.7, 2400), 0.0)
        place(x, cls.thrum(g, 50 + 4 * v, 0.6, 0.8), 0.0)
        place(x, burst(g, 0.08, [bq_bandpass(1200, 1.0)], 0.002, 0.02), 0.02, 0.6)
        place(x, moan(g, 0.5, contour(60, 85 + 6 * v, 55, 0.3), 0.6), 0.04)
        return x

    @classmethod
    def death(cls, p, v, g):
        """It jerks once, the blade flops over flat, it rolls belly-up and floats up to lie at the surface."""
        x = buf(4.6)
        place(x, splash(g, 0.8, 0.8, 2600), 0.0)
        place(x, burst(g, 0.12, [bq_bandpass(900, 0.9)], 0.002, 0.04), 0.55, 0.9)  # the blade slaps flat
        place(x, splash(g, 1.0, 0.7, 1800), 0.57)
        place(x, slosh(g, 2.0, 0.7, 0.8), 1.0)
        place(x, moan(g, 2.0, glide(62, 36, 1.2), 0.7), 0.2)
        place(x, bubble_train(g, 12, 0.005, 0.012, (0.1, 0.22), 0.5, 0.7), 1.8)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.6)
        place(x, cls.cut(g, 1.4 + 0.1 * v, 1.0), 0.0)
        return x


class Archer:
    """The tannin archer: an archerfish lying along a mangrove root, half out of the water."""

    @staticmethod
    def scull(g, sec, amp=1.0):
        x = buf(sec)
        tt = 0.0
        while tt < sec - 0.2:
            place(x, burst(g, 0.12, [bq_bandpass(1800, 1.0)], 0.02, 0.04), tt, float(g.uniform(0.2, 0.4)))
            tt += float(g.uniform(0.18, 0.28))
        return amp * x

    @staticmethod
    def spit(g, sec=0.14, amp=1.0):
        """The jet: water forced from the mouth (a hard pressured hiss) and its droplets landing after."""
        x = buf(sec + 0.6)
        j = burst(g, sec, [bq_bandpass(3200, 1.1), bq_highpass(1200, 0.7)], 0.003, sec * 0.5)
        place(x, j, 0.0)
        place(x, pop(g, 420, 0.04, 1.3), 0.0, 0.6)
        for _ in range(int(g.integers(5, 10))):
            place(x, drip(0.2, float(g.uniform(1.6, 2.6)), seed=int(g.integers(1 << 30))),
                  sec + float(g.uniform(0.05, 0.4)), float(g.uniform(0.2, 0.5)))
        return amp * x

    @staticmethod
    def slap(g, amp=1.0):
        x = buf(0.5)
        place(x, burst(g, 0.1, [bq_lowpass(4500, 0.7), bq_highpass(400, 0.7)], 0.001, 0.02), 0.0)
        place(x, splash(g, 0.45, 0.4, 2800), 0.005)
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.4)
        place(x, cls.scull(g, 2.2, 0.6), 0.0)
        place(x, tap(g, [1700, 2900], [0.004, 0.003], 0.3, 0.4), 0.9)  # a gill click
        place(x, tap(g, [1650, 2800], [0.004, 0.003], 0.25, 0.4), 1.6)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """It rises off the root, sights along its mouth and spits (contact 0.55 s)."""
        x = buf(1.4)
        place(x, slosh(g, 0.4, 0.35, 3.0), 0.05)
        place(x, cls.spit(g, 0.12 + 0.03 * v, 1.0), 0.5)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.9)
        place(x, cls.slap(g, 1.0), 0.02 * v)
        place(x, pop(g, 300 + 60 * v, 0.05, 1.5), 0.0, 0.4)
        return x

    @classmethod
    def death(cls, p, v, g):
        """It jerks, rolls off the root onto its side and settles at the water."""
        x = buf(2.4)
        place(x, cls.slap(g, 0.8), 0.0)
        place(x, creak(g, 0.3, 40, 160, WOOD, 0.3), 0.3)
        place(x, splash(g, 0.9, 0.9, 2200), 0.55)
        for i, at in enumerate((1.2, 1.55, 1.8)):
            place(x, cls.slap(g, 0.45 * 0.7 ** i), at)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.0)
        place(x, cls.scull(g, 0.9, 1.0), 0.0)
        place(x, slosh(g, 0.6, 0.25, 3.0), 0.1 * v)
        return x


class Ray:
    """The gallery ray: a pale diamond ray gliding through the air between pools, its margin faintly sea-lit."""

    @staticmethod
    def wing(g, count, rate, amp=1.0, decay=1.0, rate_end=None):
        # a broad soft surface, no feathers: a low band and no rustle
        return amp * beats(g, count, rate, 420, 0.7, 0.5, 0.0, decay=decay, rate_end=rate_end)

    @staticmethod
    def shimmer(g, sec, amp=1.0):
        """The margin's faint sea-glow: two soft glassy partials drifting against each other."""
        t = _t(_n(sec))
        y = np.sin(2 * np.pi * 1480 * t) + 0.7 * np.sin(2 * np.pi * 1486.5 * t) + 0.3 * np.sin(2 * np.pi * 2960 * t)
        return amp * y * np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2

    @staticmethod
    def thwack(g, amp=1.0):
        return amp * burst(g, 0.1, [bq_bandpass(1100, 0.9), bq_lowpass(3500, 0.7)], 0.001, 0.025)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(3.0)
        place(x, cls.wing(g, 3, 1.1, 0.8), 0.0)
        place(x, cls.shimmer(g, 2.6, 0.08), 0.2)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """It banks up on its right, then sweeps its left wing down across the target (contact 0.6 s)."""
        x = buf(1.5)
        place(x, whoosh(g, 0.4, 500, 1100, 0.6), 0.05)
        place(x, whoosh(g, 0.3, 1400 + 200 * v, 500, 1.0), 0.38)
        place(x, cls.thwack(g, 0.9), 0.6)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.9)
        place(x, cls.thwack(g, 0.7), 0.0)
        place(x, cls.wing(g, 4, 6.0 + v, 0.8, 0.8), 0.02)
        return x

    @classmethod
    def death(cls, p, v, g):
        """It falters and slides down to lie flat on the floor."""
        x = buf(2.8)
        place(x, cls.wing(g, 4, 2.2, 0.8, 0.75, 1.0), 0.0)
        place(x, whoosh(g, 1.0, 1200, 300, 0.7), 0.9)
        place(x, cls.thwack(g, 1.0), 1.85)
        place(x, thump(g, 160, 90, 0.05, 0.4, 0.3), 1.85, 0.6)
        place(x, cls.shimmer(g, 1.6, 0.08) * np.linspace(1, 0, _n(1.6)), 0.0)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.6)
        place(x, cls.wing(g, 2, 1.4 + 0.1 * v, 1.0), 0.0)
        return x


class Urchin:
    """The rime urchin: a test of salt-glass spines on a salt-glass plinth (the Lead, 2026-10-30, after ADR 0015's
    "nothing frozen" in Lowlight; it was ice). The spines rattle glassy and brittle: longer, inharmonic rings than
    ice's dry ticks, and a crack when one breaks."""

    @staticmethod
    def field(g, sec, rate, amp=1.0, swell=True):
        """The spine field: tiny salt-glass taps, their density swelling as a wave runs round the test."""
        x = buf(sec + 0.2)
        tt = 0.0
        while tt < sec:
            u = tt / sec
            a = np.sin(np.pi * u) ** 1.5 if swell else 1.0
            place(x, tap(g, SALT_GLASS, SALT_GLASS_DECAY, float(a * g.uniform(0.2, 1.0)), 0.4, 0.15), tt)
            tt += 1.0 / (rate * (0.4 + 0.6 * (a if swell else 1.0))) * float(g.uniform(0.6, 1.4))
        return amp * x

    @staticmethod
    def crunch(g, amp=1.0):
        """A spine cracking: a brittle glass crack, shards and a short ring."""
        x = buf(0.8)
        place(x, crackle(g, 0.15, 1500, 3600, 0.9, 0.04), 0.0)
        place(x, thump(g, 260, 140, 0.03, 0.6, 0.15), 0.0, 0.4)
        place(x, glass_ring(g, float(g.uniform(2100, 2900)), 0.5, 0.5), 0.01)
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.6)
        place(x, cls.field(g, 2.3, 26, 0.7), 0.0)
        place(x, creak(g, 0.6, 50, 180, [(1900, 1.0), (3100, 0.5)], 0.15), 1.1)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """It rocks back, then rolls in, the front spines stabbing (contact 0.5 s)."""
        x = buf(1.2)
        place(x, cls.field(g, 0.45, 40, 0.6), 0.0)
        place(x, cls.crunch(g, 1.0), 0.5)
        place(x, cls.field(g, 0.25, 120 + 20 * v, 0.7, False), 0.5)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.8)
        place(x, cls.field(g, 0.2, 160 + 30 * v, 1.0, False), 0.0)
        place(x, crackle(g, 0.1, 1800, 3600, 1.0, 0.03), 0.0, 0.5)
        return x

    @classmethod
    def death(cls, p, v, g):
        """A last clench, then the spines droop out and the test settles onto its glass plinth."""
        x = buf(2.6)
        place(x, cls.field(g, 0.2, 180, 1.0, False), 0.0)
        place(x, train(g, 1.4, 50, 6, SALT_GLASS, SALT_GLASS_DECAY, 0.2, 0.3, 0.3), 0.3, 0.8)
        place(x, tap(g, [880.0, 2150.0, 3600.0], [0.12, 0.06, 0.03], 0.8, 0.5, 0.05), 1.7)   # onto the glass plinth
        place(x, cls.crunch(g, 0.5), 1.72)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.0)
        place(x, cls.field(g, 0.8, 35 + 5 * v, 1.0), 0.0)
        return x


class Crawler:
    """The conduit crawler: a small brass cleaner under a salt-glass dome, scrubbing for four hundred years."""

    @staticmethod
    def feet(g, sec, rate, amp=1.0):
        """Two alternating tripods of brass feet on lacquered pads."""
        return amp * train(g, sec, rate, rate, [3800, 5600, 8100], [0.004, 0.003, 0.002], 1.0, 0.1, 0.5)

    @staticmethod
    def brush(g, sec, hz, amp=1.0):
        n = _n(sec)
        t = _t(n)
        b = unit(noise(g, n, [bq_bandpass(5200, 0.8)])) * np.abs(np.sin(np.pi * hz * t)) ** 2
        return amp * b * np.clip(t / 0.02, 0, 1)

    @staticmethod
    def squeak(g, amp=1.0):
        return amp * creak(g, 0.25, 260, 520, [(1900, 1.0), (3700, 0.4)])

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.2)
        place(x, hum(g, 2.1, 330.0, 0.12), 0.0)
        place(x, cls.brush(g, 1.9, 3.0, 0.4), 0.1)
        place(x, cls.squeak(g, 0.35), 0.6)
        place(x, cls.squeak(g, 0.3), 1.5)
        place(x, cls.feet(g, 1.9, 4, 0.35), 0.05)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """It rocks back and cocks the brush, then jabs it straight out (contact 0.45 s)."""
        x = buf(1.0)
        place(x, tap(g, [2400, 3900, 6100], [0.01, 0.006, 0.004], 0.6, 0.5), 0.1)  # the arm cocks
        place(x, whoosh(g, 0.15, 2000, 5000, 0.4), 0.3)
        place(x, cls.brush(g, 0.12, 4.0, 1.0), 0.45)
        place(x, clang(g, 3.0 + 0.2 * v, 0.7, 0.15), 0.45)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.8)
        place(x, cls.feet(g, 0.3, 30 + 6 * v, 0.9), 0.0)
        place(x, glass_ring(g, 1850 + 120 * v, 0.4, 0.5), 0.01)
        place(x, clang(g, 2.6, 0.6, 0.2), 0.0)
        return x

    @classmethod
    def death(cls, p, v, g):
        """Its knees fold up and the body sinks onto its belly plate, arms folded under its chin; the hum fades."""
        x = buf(2.4)
        place(x, hum(g, 1.8, 330.0, 0.25, (1.0, 0.5)), 0.0)
        place(x, train(g, 0.9, 20, 4, [3800, 5600, 8100], [0.004, 0.003, 0.002], 0.3, 0.2, 0.5), 0.1)
        place(x, thump(g, 200, 120, 0.04, 0.5, 0.25), 1.1, 0.6)
        place(x, clang(g, 2.2, 0.6, 0.35), 1.1)
        place(x, glass_ring(g, 1900, 0.5, 0.25), 1.5)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.0)
        place(x, cls.feet(g, 0.85, 11 + v, 1.0), 0.0)
        return x


class Lynx:
    """The ridge lynx (Ch12, Keth Pass): a high-pass cat in its winter coat. Ordinary, hungry, beautiful. Its voice is
    a throat (a low growl, a hiss, a yowl that shakes snow off the rocks); its feet are snowshoe paws, nearly silent."""

    F = [(700, 180, 1.0), (1700, 300, 0.5), (3100, 500, 0.2)]

    @classmethod
    def growl(cls, g, dur, f0, amp=1.0):
        return amp * throat(g, dur, wobble(f0, 0.06, 4.0, g), [(420, 140, 1.0), (1100, 260, 0.5)], rough=0.8, sub=0.6,
                            breath=0.6, attack=0.06, release=0.12, rough_hz=24.0)

    @staticmethod
    def hiss(g, sec=0.35, amp=1.0):
        return amp * burst(g, sec, [bq_bandpass(4200, 0.9), bq_highpass(1800, 0.7)], 0.01, sec * 0.5)

    @classmethod
    def yowl(cls, g, dur, top, amp=1.0):
        return amp * throat(g, dur, contour(top * 0.6, top, top * 0.5, 0.35), cls.F, rough=0.2, breath=0.3,
                            attack=0.04, release=dur * 0.3)

    @staticmethod
    def paw(g, amp=1.0):
        x = buf(0.25)
        place(x, thump(g, 160, 90, 0.025, 0.2, 0.15), 0.0, 0.5)
        place(x, crackle(g, 0.08, 500, 1400, 0.8, 0.03), 0.0, 0.25)  # powder snow
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.6)
        place(x, cls.growl(g, 1.0, 70, 0.5), 0.2)
        steam = burst(g, 0.6, [bq_bandpass(900, 0.7)], 0.15, 0.25)  # a breath that steams
        place(x, steam, 1.5, 0.3)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """The crouch, then the leap over the front row (contact 0.7 s of 1.4 s)."""
        x = buf(1.8)
        place(x, cls.growl(g, 0.45, 85 + 6 * v, 0.6), 0.0)
        place(x, cls.paw(g, 0.9), 0.42)
        place(x, cls.paw(g, 0.8), 0.46)
        place(x, whoosh(g, 0.3, 700, 1800, 0.6), 0.45)
        place(x, cls.hiss(g, 0.18, 0.7), 0.66)
        place(x, cls.paw(g, 1.0), 0.75)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(0.9)
        place(x, cls.yowl(g, 0.3, 900 + 80 * v, 0.9), 0.0)
        place(x, cls.paw(g, 0.6), 0.05)
        return x

    @classmethod
    def death(cls, p, v, g):
        """It limps two steps and lies down in the snow."""
        x = buf(2.6)
        place(x, cls.yowl(g, 0.6, 750, 0.7), 0.0)
        place(x, cls.paw(g, 0.6), 0.7)
        place(x, cls.paw(g, 0.4), 1.15)
        place(x, thump(g, 110, 60, 0.12, 0.3, 0.5), 1.5, 0.5)
        place(x, crackle(g, 0.3, 400, 1200, 0.8, 0.1), 1.5, 0.3)
        place(x, burst(g, 0.8, [bq_bandpass(800, 0.7)], 0.2, 0.3), 1.7, 0.25)  # the last breath
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.0)
        for i, at in enumerate((0.0, 0.18, 0.42, 0.6)):
            place(x, cls.paw(g, float(g.uniform(0.6, 1.0))), at + 0.02 * v)
        return x


class Skate:
    """The glass skate (Ch16, the Pale Rim): buried in white sand under shin-deep water, nearly clear, an ambusher."""

    @staticmethod
    def sand(g, sec, amp=1.0):
        return amp * crackle(g, sec, 900, 2200, 0.7, sec * 0.5)

    @classmethod
    def idle(cls, p, v, g):
        x = buf(2.4)
        place(x, slosh(g, 2.0, 0.3, 0.7), 0.0)  # the breathing back under the water
        place(x, cls.sand(g, 0.4, 0.25), 0.9)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """It erupts from the sand and slaps (contact 0.5 s of 1.2 s)."""
        x = buf(1.6)
        place(x, cls.sand(g, 0.35, 0.6), 0.1)
        place(x, splash(g, 0.9, 0.8, 2400), 0.3)
        place(x, Ray.thwack(g, 1.0), 0.5)
        place(x, splash(g, 0.7, 0.5, 2000), 0.55)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(1.0)
        place(x, Ray.thwack(g, 0.7), 0.0)
        place(x, slosh(g, 0.6, 0.5, 3.0 + v), 0.02)
        return x

    @classmethod
    def death(cls, p, v, g):
        """It flattens and lies still."""
        x = buf(2.2)
        place(x, slosh(g, 1.2, 0.7, 1.2), 0.0)
        place(x, cls.sand(g, 0.6, 0.4), 0.6)
        place(x, bubble_train(g, 6, 0.004, 0.008, (0.12, 0.2), 0.3, 0.7), 0.9)
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.2)
        place(x, slosh(g, 1.0, 0.7, 1.6 + 0.2 * v), 0.0)
        place(x, cls.sand(g, 0.3, 0.3), 0.2)
        return x


class FlatEngine:
    """The flat-engine (Ch14, the stern of Malcor Venn's barge): a bound Lit Age drum, half sunk in the lagoon, whose
    long paddles press the water flat. Its bound light is steady, so its hum never pulses; iron, not brass."""

    @staticmethod
    def press(g, sec, amp=1.0):
        """Paddles laying the water smooth: a broad low hush of water held down, no splash."""
        n = _n(sec)
        x = unit(noise(g, n, [bq_lowpass(300, 0.7), bq_highpass(40, 0.7)])) * np.sin(np.pi * np.clip(_t(n) / sec, 0, 1))
        return amp * x

    @classmethod
    def idle(cls, p, v, g):
        x = buf(3.4)
        place(x, hum(g, 3.3, 73.4, 0.6), 0.0)
        place(x, cls.press(g, 3.0, 0.5), 0.1)
        place(x, clang(g, 0.6, 0.25, 0.8), 1.4)
        return x

    @classmethod
    def attack(cls, p, v, g):
        """It bears down: the paddles press harder, the drum groans, the water flattens round the party."""
        x = buf(2.2)
        place(x, hum(g, 2.0, 73.4, 0.5, (1.0, 1.06)), 0.0)
        place(x, creak(g, 0.8, 14, 55, [(f * 0.32, 1.0 / (i + 1)) for i, f in enumerate(BRASS[:3])], 0.7), 0.1)
        place(x, cls.press(g, 1.4, 1.0), 0.3)
        place(x, clang(g, 0.55 + 0.03 * v, 0.6, 1.0), 0.9)
        return x

    @classmethod
    def hurt(cls, p, v, g):
        x = buf(1.6)
        place(x, clang(g, 0.5 + 0.04 * v, 1.0, 1.2), 0.0)
        place(x, splash(g, 0.8, 0.5, 1600), 0.05)  # a paddle knocked loose from the water
        place(x, hum(g, 1.2, 73.4, 0.3, (1.0, 0.96)), 0.0)
        return x

    @classmethod
    def death(cls, p, v, g):
        """Liss breaks it: the hum winds down, the paddles drop, and the lagoon ripples for the first time."""
        x = buf(5.0)
        place(x, hum(g, 3.4, 73.4, 0.7, (1.0, 0.4)), 0.0)
        place(x, clang(g, 0.45, 1.0, 1.6), 0.2)
        for i in range(4):
            place(x, splash(g, 0.8, 0.5, 1500), 1.0 + 0.35 * i)
        place(x, slosh(g, 2.0, 0.6, 1.6), 2.4)  # the ripples, at last
        return x

    @classmethod
    def move(cls, p, v, g):
        x = buf(1.6)
        place(x, cls.press(g, 1.4, 0.8), 0.0)
        place(x, clang(g, 0.7 + 0.05 * v, 0.3, 0.4), 0.4)
        return x


FAMILIES = {"drowner": Drowner, "engine": Engine, "woolback": Woolback, "sailfin": Sailfin, "archer": Archer,
            "ray": Ray, "urchin": Urchin, "crawler": Crawler,
            "lynx": Lynx, "moth": Moth, "skate": Skate, "flat_engine": FlatEngine}


# --------------------------------------------------------------------------- the set


def counts(cid: str) -> dict[str, int]:
    if cid in BOSSES:
        return {"idle": 1, "attack": 2, "hurt": 3, "death": 1, "move": 2}
    return {"idle": 1, "attack": 2, "hurt": 2, "death": 1, "move": 2}


def target(event: str) -> float:
    return {"idle": IDLE, "move": MOVE}.get(event, VOICE)


def build() -> dict:
    """{file stem: (callable, target)} for every file, in a fixed order."""
    out: dict = {}
    for ci, (cid, p) in enumerate(CREATURES.items()):
        fam = FAMILIES[p["family"]]
        for ei, (event, count) in enumerate(counts(cid).items()):
            word = MOVE_WORD[p["family"]] if event == "move" else event
            for v in range(count):
                seed = SEED + 1000 * ci + 100 * ei + v

                def fn(fam=fam, event=event, p=p, v=v, seed=seed) -> np.ndarray:
                    g = rng(seed)
                    x = getattr(fam, event)(p, v, g)
                    big = p["size"] >= 2.0
                    return room(x, seed + 7, mix=0.16 if big else 0.1, tail=0.6 if big else 0.3,
                                rt60=1.2 if big else 0.7)

                out[f"{cid}_{word}_{v + 1}"] = (fn, target(event))
    return out


SFX = build()
FILES = [name + ".ogg" for name in SFX]


def render(out_dir: str = OUT_DIR, verbose: bool = True, only: str = "") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for name, (fn, tgt) in SFX.items():
        if only and only not in name:
            continue
        x = finish(fn(), tgt)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=QUALITY)
        m = measure(x)
        res[name] = m
        if verbose:
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  "
                  f"peak {m['sample_peak_dbfs']:.2f}", flush=True)
    return res


if __name__ == "__main__":
    render(only=sys.argv[1] if len(sys.argv) > 1 else "")
