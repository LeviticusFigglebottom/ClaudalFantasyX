"""Act I's last borrowed and silent foes, each given its own voice (M3-AUD-861, ADR 0041; Git LFS, ADR 0173).

Until now four Act I variants played another creature's files at a different pitch, and the Ch6 Inquisitor was
`silent`. Each now has its own set: the family's body from creature_sfx.py (the same rules and building blocks),
with the layer that makes it that creature on every event. Synthesized here and in tools/audio/synth/ (SPEC §2,
§9): no samples, no recordings, no generated audio. A separate source with its own seed, so creature_sfx.py's set
renders byte for byte as before.

    wreck_crab   Ch6 (docs/kb/art/creatures/act1/wreck_crab.md): a reef crab living in a broken Saltwright lamp
                 housing. It hunkers under scorched brass, so the brass knocks and rings as it moves and strikes, and
                 the housing's crazed salt-glass panes rattle when it is hit; its death tips the housing over.
    wallcrab     Ch8 (wallcrab.md): a reef crab of Corrow's grey laterite seawall, fat on its weed. Heavier and lower,
                 with grit and stone in every step and a dull stone knock where the reef crab's shell clicks.
    wall_polyp   Ch8 (wall_polyp.md): a spawn-polyp grown over one of the seawall's Watchers, the carved humming
                 faces, its roots out of the stone mouth. Under the polyp's wet voice the Watcher hums, a low
                 open-mouthed stone hum, and its mending (polyp_mend) swells it; burned off, the hum stops with a crack.
    stormgull    Ch8 (stormgull.md): a gull harrier gone dark with the weather, riding the headland's updraught and
                 carrying static. Its calls are lower and rougher than the harrier's, a charge crackles on its
                 wings, and its strikes snap with a spark.
    stillguard_inquisitor
                 Ch6 boss (M3-CRE-625: Inquisitor Hadric Moll, a person: red-lacquered shell armour, a round shield,
                 a long-hafted brine-iron held upright like a standard; he yields at 0 HP, never dies). No voice and
                 no words (SPEC §4: no VO in battle): his armour's lacquered plates, the brine-iron's haft and its
                 strike, the shield, his breath. His `death` is the yield: the iron laid down flat, the shield set
                 aside, the armour as he kneels.

assets/lfs/audio/sfx/creatures/<creature>_<event>_<n>.ogg (mono, Vorbis q4): voices -18 LUFS momentary max, idles -20,
movement -21 (targets.py's creature rules, which apply under assets/lfs/audio/ too). The Inquisitor has idle 1,
attack 2, hurt 3, yield 1, step 2; the others idle 1, attack 2, hurt 2, death 1, movement 2.

Render:  python3 tools/audio/render_all.py --only act1_final_creature_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from act2_creature_sfx import clang, hum, tinkle, whoosh  # noqa: E402
from creature_sfx import (IDLE, MOVE, QUALITY, VOICE, Bird, Crab, Polyp, buf, burst, crackle, finish, room,  # noqa: E402
                          tap, thump, unit)
from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, noise, place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "lfs", "audio", "sfx", "creatures")
SEED = 20261861

# the family numbers each starts from (creature_sfx.CREATURES' keys), varied so none is its parent pitched
CRAB_WRECK = dict(family="crab", size=1.0, pitch=0.94, legs=3)
CRAB_WALL = dict(family="crab", size=1.12, pitch=0.86, legs=3)
POLYP_WALL = dict(family="polyp", size=1.25, pitch=0.86, spawn=True)
BIRD_STORM = dict(family="bird", size=1.05, pitch=0.9)


# --------------------------------------------------------------------------- the layers that make each one itself


def brass(g, amp: float = 1.0, ring: float = 0.5) -> np.ndarray:
    """The wreck crab's lamp housing: scorched brass knocked, a short dull ring."""
    return clang(g, float(g.uniform(0.9, 1.05)), amp, ring)


def panes(g, sec: float = 0.5, amp: float = 1.0) -> np.ndarray:
    """The housing's crazed salt-glass panes rattling in their frames."""
    return tinkle(g, sec, 7, 2400, 5200, amp)


def grit(g, sec: float, amp: float = 1.0) -> np.ndarray:
    """Laterite grit under a crab's feet: dry, fine crackle low in the band."""
    return amp * (0.6 * crackle(g, sec, 140, 1800, 0.8) + 0.4 * crackle(g, sec, 60, 900, 0.7))


def stone(g, amp: float = 1.0) -> np.ndarray:
    """A dull stone knock: laterite, not shell."""
    return amp * tap(g, [420.0, 1010.0, 1830.0], [0.03, 0.018, 0.01], 1.0, 0.7, 0.05)


def watcher(g, sec: float, amp: float = 1.0, swell: bool = False) -> np.ndarray:
    """The Watcher's hum: a carved stone mouth humming, low and open (two near partials, as the Lit Age hums do)."""
    x = hum(g, sec, 98.0, 1.0)
    x = x + 0.4 * hum(g, sec, 147.0, 1.0)   # its open fifth, as the Watchers hum
    if swell:
        x = x * np.sin(np.pi * np.clip(_t(len(x)) / sec, 0, 1)) ** 0.7
    return amp * unit(x)


def static(g, sec: float, amp: float = 1.0) -> np.ndarray:
    """The charge the stormgull carries: a fine, bright crackle."""
    return amp * crackle(g, sec, 90, 4800, 1.2)


def spark(g, amp: float = 1.0) -> np.ndarray:
    """A discharge: a sharp snap with a short fizz behind it."""
    x = buf(0.4)
    place(x, burst(g, 0.03, [bq_highpass(1500, 0.7)], 0.0003, 0.004), 0.0)
    place(x, crackle(g, 0.3, 220, 5200, 1.0, 0.08), 0.005, 0.6)
    return amp * x


# --------------------------------------------------------------------------- each creature's events


class WreckCrab:
    p = CRAB_WRECK

    @classmethod
    def idle(cls, v, g):
        x = buf(1.6)
        place(x, Crab.idle(cls.p, v, g), 0.0)
        place(x, brass(g, 0.25, 0.4), 0.7)
        return x

    @classmethod
    def attack(cls, v, g):
        x = buf(1.6)
        place(x, Crab.attack(cls.p, v, g), 0.0)
        place(x, brass(g, 0.5, 0.5), 0.12 + 0.05 * v)
        return x

    @classmethod
    def hurt(cls, v, g):
        x = buf(1.4)
        place(x, Crab.hurt(cls.p, v, g), 0.0)
        place(x, brass(g, 0.6, 0.6), 0.01)
        place(x, panes(g, 0.4, 0.5), 0.03)
        return x

    @classmethod
    def death(cls, v, g):
        """It folds under the brass, and the housing tips over onto the sand: a heavy ring, the panes falling out."""
        x = buf(2.6)
        place(x, Crab.death(cls.p, v, g), 0.0)
        place(x, brass(g, 0.9, 1.0), 0.7)
        place(x, panes(g, 0.8, 0.7), 0.72)
        place(x, thump(g, 160, 70, 0.08, 0.4, 0.4), 0.7, 0.6)
        return x

    @classmethod
    def move(cls, v, g):
        x = buf(1.6)
        place(x, Crab.move(cls.p, v, g), 0.0)
        for i in range(3):
            place(x, brass(g, 0.15, 0.25), 0.15 + 0.35 * i)
        return x


class Wallcrab:
    p = CRAB_WALL

    @classmethod
    def idle(cls, v, g):
        x = buf(1.6)
        place(x, Crab.idle(cls.p, v, g), 0.0)
        place(x, grit(g, 0.6, 0.15), 0.4)
        return x

    @classmethod
    def attack(cls, v, g):
        x = buf(1.6)
        place(x, Crab.attack(cls.p, v, g), 0.0)
        place(x, stone(g, 0.5), 0.12 + 0.05 * v)
        return x

    @classmethod
    def hurt(cls, v, g):
        x = buf(1.4)
        place(x, Crab.hurt(cls.p, v, g), 0.0)
        place(x, stone(g, 0.7), 0.01)
        place(x, grit(g, 0.3, 0.3), 0.02)
        return x

    @classmethod
    def death(cls, v, g):
        x = buf(2.4)
        place(x, Crab.death(cls.p, v, g), 0.0)
        place(x, stone(g, 0.8), 0.6)
        place(x, grit(g, 0.8, 0.35), 0.62)
        return x

    @classmethod
    def move(cls, v, g):
        x = buf(1.6)
        place(x, Crab.move(cls.p, v, g), 0.0)
        place(x, grit(g, 1.2, 0.35), 0.05)
        return x


class WallPolyp:
    p = POLYP_WALL

    @classmethod
    def idle(cls, v, g):
        x = buf(2.2)
        place(x, Polyp.idle(cls.p, v, g), 0.0)
        place(x, watcher(g, 2.0, 0.3), 0.0)
        return x

    @classmethod
    def attack(cls, v, g):
        """polyp_mend: the polyp feeds its light to the crawlers, and the Watcher's hum swells with it."""
        x = buf(2.0)
        place(x, Polyp.attack(cls.p, v, g), 0.0)
        place(x, watcher(g, 1.6, 0.5, swell=True), 0.05)
        return x

    @classmethod
    def hurt(cls, v, g):
        x = buf(1.6)
        place(x, Polyp.hurt(cls.p, v, g), 0.0)
        place(x, watcher(g, 0.6, 0.3), 0.0)
        place(x, stone(g, 0.4), 0.02)
        return x

    @classmethod
    def death(cls, v, g):
        """Burned off the face: the polyp's death, and the Watcher's hum stopping as the stone brow cracks."""
        x = buf(3.0)
        place(x, Polyp.death(cls.p, v, g), 0.0)
        hm = watcher(g, 1.4, 0.5)
        place(x, hm * np.linspace(1.0, 0.0, len(hm)) ** 2, 0.0)
        place(x, stone(g, 0.9), 1.3)
        place(x, grit(g, 0.6, 0.3), 1.32)
        return x

    @classmethod
    def move(cls, v, g):
        x = buf(1.6)
        place(x, Polyp.move(cls.p, v, g), 0.0)
        return x


class Stormgull:
    p = BIRD_STORM

    @classmethod
    def idle(cls, v, g):
        x = buf(2.0)
        place(x, Bird.idle(cls.p, v, g), 0.0)
        place(x, static(g, 1.6, 0.12), 0.2)
        return x

    @classmethod
    def attack(cls, v, g):
        """dive_rake and spark_spit: the dive, and the charge snapping off it."""
        x = buf(1.8)
        place(x, Bird.attack(cls.p, v, g), 0.0)
        place(x, spark(g, 0.6), 0.2 + 0.1 * v)
        return x

    @classmethod
    def hurt(cls, v, g):
        x = buf(1.4)
        place(x, Bird.hurt(cls.p, v, g), 0.0)
        place(x, static(g, 0.4, 0.4), 0.0)
        return x

    @classmethod
    def death(cls, v, g):
        """It falls out of the updraught; the charge on it fizzes out."""
        x = buf(2.6)
        place(x, Bird.death(cls.p, v, g), 0.0)
        st = static(g, 1.4, 0.4)
        place(x, st * np.linspace(1.0, 0.0, len(st)), 0.1)
        return x

    @classmethod
    def move(cls, v, g):
        x = buf(1.6)
        place(x, Bird.move(cls.p, v, g), 0.0)
        place(x, static(g, 0.8, 0.1), 0.1)
        return x


class Inquisitor:
    """Inquisitor Hadric Moll: lacquered shell armour, the brine-iron's haft, a round shield, his breath. No voice."""

    @staticmethod
    def plates(g, amp: float = 1.0) -> np.ndarray:
        """Red-lacquered shell plates settling against each other: hard, bright knocks, damped by the lacquer."""
        x = buf(0.5)
        for i in range(int(g.integers(2, 4))):
            place(x, tap(g, [1150.0, 2050.0, 3300.0], [0.012, 0.008, 0.005], 1.0, 0.5, 0.08),
                  float(g.uniform(0, 0.12)), float(g.uniform(0.4, 1.0)))
        return amp * x

    @staticmethod
    def iron(g, amp: float = 1.0, ring: float = 0.6) -> np.ndarray:
        """The brine-iron's head: wet, pitted iron, a short dark ring."""
        return amp * tap(g, [310.0, 840.0, 1600.0, 2540.0], [ring * 0.6, ring * 0.35, ring * 0.2, ring * 0.12],
                         1.0, 0.6, 0.04)

    @staticmethod
    def breath(g, sec: float = 0.45, amp: float = 1.0, sharp: bool = False) -> np.ndarray:
        """A man's breath through his teeth: filtered noise, a short exhale (no voice in it)."""
        n = _n(sec)
        t = _t(n)
        env = np.clip(t / (0.02 if sharp else 0.08), 0, 1) * np.exp(-t / (sec * (0.25 if sharp else 0.45)))
        return amp * unit(noise(g, n, [bq_bandpass(1300, 0.7), bq_lowpass(4200, 0.7)])) * env

    @staticmethod
    def shield(g, amp: float = 1.0) -> np.ndarray:
        """The round shield: a lacquered shell boss over wood, a deep knock."""
        x = buf(0.6)
        place(x, thump(g, 180, 95, 0.06, 0.5, 0.4), 0.0)
        place(x, tap(g, [640.0, 1480.0, 2600.0], [0.04, 0.02, 0.012], 1.0, 0.6, 0.05), 0.0, 0.6)
        return amp * x

    @classmethod
    def idle(cls, v, g):
        """The iron held upright like a standard: its butt set on the stones, the armour settling, one breath."""
        x = buf(2.0)
        place(x, cls.iron(g, 0.3, 0.3), 0.1)
        place(x, cls.plates(g, 0.4), 0.15)
        place(x, cls.breath(g, 0.6, 0.25), 0.9)
        return x

    @classmethod
    def attack(cls, v, g):
        """haft_strike and brine_iron: the long haft swung, the armour moving with it, the iron coming down."""
        x = buf(2.0)
        place(x, cls.breath(g, 0.3, 0.4, sharp=True), 0.0)
        place(x, whoosh(g, 0.4 + 0.05 * v, 300, 1300 + 200 * v, 0.7), 0.02)
        place(x, cls.plates(g, 0.5), 0.05)
        place(x, cls.iron(g, 0.9, 0.7), 0.42 + 0.05 * v)
        place(x, thump(g, 130, 60, 0.1, 0.4, 0.5), 0.42 + 0.05 * v, 0.6)
        return x

    @classmethod
    def hurt(cls, v, g):
        """Struck: the blow on lacquered shell (or the shield, on the third), and the breath knocked out of him."""
        x = buf(1.4)
        if v == 2:
            place(x, cls.shield(g, 1.0), 0.0)
        else:
            place(x, cls.plates(g, 1.0), 0.0)
            place(x, thump(g, 120 + 20 * v, 70, 0.06, 0.4, 0.3), 0.0, 0.5)
        place(x, cls.breath(g, 0.4, 0.5, sharp=True), 0.03)
        return x

    @classmethod
    def death(cls, v, g):
        """He yields (M3-CRE-625's `ko`: a kneel): the iron laid down flat on the stones, the shield set aside, the
        armour as he goes down on one knee, and a long breath out. He is not killed, so nothing falls hard."""
        x = buf(3.6)
        place(x, cls.breath(g, 0.9, 0.4), 0.0)
        place(x, cls.plates(g, 0.7), 0.5)
        place(x, thump(g, 110, 70, 0.08, 0.3, 0.4), 0.55, 0.5)       # the knee on stone
        place(x, cls.iron(g, 0.6, 0.5), 1.4)                        # the iron laid down
        place(x, cls.iron(g, 0.3, 0.3), 1.52)                       # ...and settling
        place(x, cls.shield(g, 0.5), 2.3)                           # the shield set aside
        return x

    @classmethod
    def move(cls, v, g):
        """A step in armour: the foot, the plates, the sash."""
        x = buf(1.2)
        place(x, thump(g, 150, 90, 0.04, 0.3, 0.25), 0.0, 0.5)
        place(x, cls.plates(g, 0.6), 0.02)
        place(x, burst(g, 0.25, [bq_bandpass(2600, 0.8), bq_highpass(900, 0.7)], 0.02, 0.06), 0.05, 0.3)  # the sash
        place(x, thump(g, 150, 90, 0.04, 0.3, 0.25), 0.55, 0.45)
        place(x, cls.plates(g, 0.5), 0.57)
        return x


# who, which events (with counts), the movement word, and how big a room they sound in
CREATURES: dict[str, tuple] = {
    "wreck_crab": (WreckCrab, {"idle": 1, "attack": 2, "hurt": 2, "death": 1, "move": 2}, "skitter", False),
    "wallcrab": (Wallcrab, {"idle": 1, "attack": 2, "hurt": 2, "death": 1, "move": 2}, "skitter", False),
    "wall_polyp": (WallPolyp, {"idle": 1, "attack": 2, "hurt": 2, "death": 1, "move": 2}, "squelch", False),
    "stormgull": (Stormgull, {"idle": 1, "attack": 2, "hurt": 2, "death": 1, "move": 2}, "wingbeat", False),
    "stillguard_inquisitor": (Inquisitor, {"idle": 1, "attack": 2, "hurt": 3, "death": 1, "move": 2}, "step", True),
}
WORD = {"death": {"stillguard_inquisitor": "yield"}}


def build() -> dict:
    """{file stem: (callable, target)} for every file, in a fixed order."""
    out: dict = {}
    for ci, (cid, (cls, counts, move_word, big)) in enumerate(CREATURES.items()):
        for ei, (event, count) in enumerate(counts.items()):
            word = move_word if event == "move" else WORD.get(event, {}).get(cid, event)
            for v in range(count):
                seed = SEED + 1000 * ci + 100 * ei + v

                def fn(cls=cls, event=event, v=v, seed=seed, big=big) -> np.ndarray:
                    x = getattr(cls, event)(v, rng(seed))
                    return room(x, seed + 7, mix=0.12 if big else 0.1, tail=0.4 if big else 0.3,
                                rt60=0.9 if big else 0.7)

                target = {"idle": IDLE, "move": MOVE}.get(event, VOICE)
                out[f"{cid}_{word}_{v + 1}"] = (fn, target)
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
        res[name] = measure(x)
        if verbose:
            m = res[name]
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  peak {m['sample_peak_dbfs']:.2f}",
                  flush=True)
    return res


if __name__ == "__main__":
    render(only=sys.argv[1] if len(sys.argv) > 1 else "")
