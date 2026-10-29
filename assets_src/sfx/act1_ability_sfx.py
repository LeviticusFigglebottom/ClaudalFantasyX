"""Every Act I ability heard as itself (M3-BPR-421 and M3-AUD-861, ADR 0041; Git LFS, ADR 0173).

battle-presentation gave each Act I ability its own battle VFX (M3-BPR-420; effects.json, each effect's `note`
says what it is), and until now each borrowed a generic row in battle_sfx.json `vfx` (an element hit, the heal,
status_apply). Each now has its own sound, made from what its note says: the material (water, iron, rope, glass,
ash, oil, shell, fire, bound light), the motion (a cut, a drop, a lift, a ring rising) and its weight. Damage
effects keep an impact on the target, since they replace an element's hit. The heroes' and Vowbound's are the most
heard and get the most care; a foe's ability carries its creature's own family (creature_sfx.py's).

Also the two Swell styles M3-BPR-422 added (choreo_sfx.json `styles`): Kerrid's `swing` (whoosh_swing, the
anchor swung round its line, and swell_kerrid, the anchor landing) and Liss's `reel` (reel_whir, the line paid
out and snubbed, and swell_liss, the reel-stop's bright brass strike).

Synthesized here and in tools/audio/synth/ (SPEC §2, §9): no samples, no recordings, no generated audio.

assets/lfs/audio/sfx/battle/abl_<effect>.ogg (mono, q4): strikes -18 LUFS momentary max, casts and supports -19,
quiet supports -20 (targets.py's combat rule, sfx/battle/*.ogg, -19 +- 2.5). assets/lfs/audio/sfx/choreo/: the Swell
styles' rows (-18, the choreo rule; swell_* -19).

Render:  python3 tools/audio/render_all.py --only act1_ability_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import creature_sfx as C  # noqa: E402
from act1_final_creature_sfx import Inquisitor, brass, grit, panes, spark, static, stone  # noqa: E402
from act1_skill_sfx import claws_on_stone, creak, rope, rumble, twang, wave  # noqa: E402
from act2_creature_sfx import clang, hum, splash, tinkle, whoosh  # noqa: E402
from creature_sfx import buf, burst, crackle, finish, glass_ring, room, slosh, tap, thump, unit  # noqa: E402
from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, bubble_train, noise, place  # noqa: E402
from vowbound_sfx import anvil, chime, flame, flare, net_light, snap, sparks, thunder  # noqa: E402

BATTLE_DIR = os.path.join(ROOT, "assets", "lfs", "audio", "sfx", "battle")
CHOREO_DIR = os.path.join(ROOT, "assets", "lfs", "audio", "sfx", "choreo")
SEED = 20261865
STRIKE, CAST, QUIET = -18.0, -19.0, -20.0
CR = C.CREATURES


# --------------------------------------------------------------------------- small building blocks


def cut(g, f0: float = 3000.0, sec: float = 0.18, amp: float = 1.0) -> np.ndarray:
    """A blade's edge through air: a fast bright swish."""
    return whoosh(g, sec, f0 * 0.5, f0, amp)


def hit(g, f0: float = 120.0, amp: float = 1.0, crack: float = 0.4) -> np.ndarray:
    """The blow landing: a low thump and a short body crack."""
    x = buf(0.6)
    place(x, thump(g, f0, f0 * 0.45, 0.08, 0.4, 0.5), 0.0)
    place(x, burst(g, 0.06, [bq_bandpass(1400, 0.8)], 0.0008, 0.015), 0.0, crack)
    return amp * x


def water_lift(g, sec: float = 1.2, amp: float = 1.0) -> np.ndarray:
    """Shallow water lifting: a gentle rising slosh and fine droplets falling back."""
    x = buf(sec + 0.4)
    s = slosh(g, sec, 0.8, 1.4)
    place(x, s * np.clip(_t(len(s)) / (sec * 0.6), 0, 1), 0.0)
    place(x, tinkle(g, sec * 0.8, 5, 1600, 3000, 0.25), sec * 0.3)
    return amp * x


def ring_rise(g, f0: float, sec: float = 1.2, amp: float = 1.0) -> np.ndarray:
    """A ring of light lifting: three glass tones a fifth apart, entering low to high."""
    x = buf(sec + 1.0)
    for i, r in enumerate((1.0, 1.5, 2.0)):
        place(x, glass_ring(g, f0 * r, sec, 0.6 - 0.12 * i), 0.12 * i)
    place(x, whoosh(g, sec * 0.7, 500, 2400, 0.25), 0.0)
    return amp * x


def ash(g, sec: float, amp: float = 1.0) -> np.ndarray:
    """Ash shaken loose: a dry, soft, fine crackle with a breath of air."""
    return amp * (0.6 * crackle(g, sec, 120, 2200, 0.7, sec * 0.5) + 0.4 * unit(noise(g, _n(sec), [bq_bandpass(1800, 0.5)]))
                  * np.sin(np.pi * np.clip(_t(_n(sec)) / sec, 0, 1)))


def oil(g, sec: float = 0.5, amp: float = 1.0) -> np.ndarray:
    """Black oil: a thick, wet, low slap that clings."""
    x = buf(sec + 0.3)
    place(x, burst(g, 0.12, [bq_lowpass(700, 0.7)], 0.002, 0.04), 0.0)
    place(x, C.gurgle(g, sec, 12, 2.0, 5.0, 0.5), 0.02)
    return amp * x


def splinter(g, amp: float = 1.0) -> np.ndarray:
    """Wood splitting: a sharp crack and small pieces skittering."""
    x = buf(0.7)
    place(x, burst(g, 0.05, [bq_bandpass(2200, 0.7)], 0.0005, 0.012), 0.0)
    place(x, creak(g, 0.15, 400, 1200), 0.0, 0.5)
    for i in range(4):
        place(x, tap(g, [1800.0, 3300.0], [0.01, 0.006], 1.0, 0.5, 0.15), 0.06 + 0.05 * i, 0.4 - 0.07 * i)
    return amp * x


def shell_crack(g, amp: float = 1.0) -> np.ndarray:
    """Shell plates cracking off: hard brittle cracks and shards."""
    x = buf(0.8)
    for i in range(3):
        place(x, tap(g, [2600.0, 4100.0, 6200.0], [0.012, 0.008, 0.005], 1.0, 0.7, 0.1), 0.04 * i, 1.0 - 0.2 * i)
    place(x, tinkle(g, 0.4, 5, 3000, 6000, 0.3), 0.08)
    return amp * x


def ink(g, sec: float = 1.2, amp: float = 1.0) -> np.ndarray:
    """Ink-dark motes settling: a low, slow, soft descending breath with a muted glass tone under it."""
    x = buf(sec + 0.6)
    place(x, whoosh(g, sec, 1400, 300, 0.4), 0.0)
    place(x, glass_ring(g, 330.0, sec, 0.3), 0.1)
    place(x, glass_ring(g, 311.0, sec, 0.2), 0.25)   # a semitone under: the hex
    return amp * x


def bound_light(g, sec: float, amp: float = 1.0) -> np.ndarray:
    """Bound light: a steady glassy hum (never pulsing) with faint knots of shimmer."""
    x = buf(sec + 0.4)
    place(x, hum(g, sec, 660.0, 0.5), 0.0)
    place(x, net_light(g, sec * 0.8, 0.6), 0.05)
    return amp * x


def smoke(g, sec: float, amp: float = 1.0) -> np.ndarray:
    """Smoke rolling over: a wide low hiss swelling and thinning."""
    n = _n(sec)
    t = _t(n)
    return amp * unit(noise(g, n, [bq_lowpass(1200, 0.6), bq_highpass(120, 0.7)])) * np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 1.5


def creature(fam, cid: str, event: str, g, v: int = 0) -> np.ndarray:
    return getattr(fam, event)(CR[cid], v, g)


def lay(*parts) -> np.ndarray:
    """Mix (signal, at, gain) parts into one buffer long enough for all of them."""
    end = max(at + len(sig) / 44100.0 for sig, at, _ in parts)
    x = buf(end + 0.05)
    for sig, at, gn in parts:
        place(x, sig, at, gn)
    return x


# --------------------------------------------------------------------------- the abilities

R = {}  # effect id -> (recipe, target)


def ability(effect: str, target: float = STRIKE):
    def deco(fn):
        R[effect] = (fn, target)
        return fn
    return deco


# the heroes
@ability("quick_hit")
def _(g):  # Rhen: a quick light cut, foam-white
    return lay((cut(g, 4200, 0.14), 0.0, 0.8), (hit(g, 160, 0.6, 0.6), 0.1, 1.0), (splash(g, 0.4, 0.3, 4200), 0.11, 1.0))


@ability("undertow_cut")
def _(g):  # Rhen: a cut that drags down like the undertow, teal spray pulled under
    return lay((cut(g, 3200, 0.2), 0.0, 0.8), (hit(g, 130, 0.7), 0.15, 1.0), (whoosh(g, 0.6, 1800, 220, 0.6), 0.16, 1.0),
               (bubble_train(g, 8, 0.004, 0.01, (0.03, 0.08), 0.4, 0.7), 0.3, 1.0))


@ability("mend", CAST)
def _(g):  # Asha: shallow water lifting off the wound
    return lay((water_lift(g, 1.3, 1.0), 0.0, 1.0), (glass_ring(g, 880.0, 1.2, 0.3), 0.5, 1.0))


@ability("hasten", CAST)
def _(g):  # Asha: quick pale streaks rising past the ally
    return lay(*[(whoosh(g, 0.22, 900 + 300 * i, 3600 + 300 * i, 0.6), 0.08 * i, 1.0) for i in range(4)],
               (glass_ring(g, 1320.0, 0.7, 0.3), 0.3, 1.0))


@ability("ward", CAST)
def _(g):  # Asha: a ring of reef-blue light lifting around the ally
    return ring_rise(g, 523.25, 1.4)


@ability("shell_breaker")
def _(g):  # Toma: shell plates cracking off the target
    return lay((whoosh(g, 0.3, 400, 1600, 0.6), 0.0, 1.0), (hit(g, 110, 1.0, 0.5), 0.25, 1.0), (shell_crack(g), 0.27, 1.0))


@ability("challenge", CAST)
def _(g):  # Toma: the challenge, a spark at the foe's head (his spear's butt struck on the deck)
    return lay((thump(g, 140, 80, 0.06, 0.4, 0.4), 0.0, 0.8), (spark(g, 0.8), 0.05, 1.0), (clang(g, 1.3, 0.4, 0.4), 0.05, 1.0))


@ability("hold_the_stair", CAST)
def _(g):  # Toma: he sets his shield over the stair
    return lay((Inquisitor.shield(g, 1.0), 0.0, 1.0), (stone(g, 0.6), 0.02, 1.0), (grit(g, 0.5, 0.3), 0.05, 1.0))


@ability("stand_firm", QUIET)
def _(g):  # Toma: feet set, dust settling
    return lay((thump(g, 120, 70, 0.06, 0.4, 0.3), 0.0, 0.8), (thump(g, 120, 70, 0.06, 0.4, 0.3), 0.18, 0.7),
               (ash(g, 0.9, 0.4), 0.2, 1.0))


@ability("stand_fast", QUIET)
def _(g):  # Ch8: a hero braces on the wall-walk
    return lay((thump(g, 130, 75, 0.06, 0.4, 0.3), 0.0, 0.8), (grit(g, 0.5, 0.4), 0.02, 1.0), (rope(g, 0.5, 300, 900), 0.15, 0.4))


@ability("return_tide")
def _(g):  # Toma's Swell: the tide thrown back out from the stair
    return lay((wave(g, 1.6, 1.0), 0.0, 1.0), (whoosh(g, 1.0, 300, 1600, 0.6), 0.3, 1.0), (hit(g, 90, 0.8), 0.4, 1.0))


@ability("ember", CAST)
def _(g):  # Ysolde: a small flame climbing the target
    return lay((flame(g, 1.0, 0.8, 1600, 60), 0.0, 1.0), (whoosh(g, 0.5, 400, 2400, 0.5), 0.0, 1.0),
               (crackle(g, 0.6, 50, 3000, 0.9, 0.3), 0.3, 0.5))


@ability("frost", CAST)
def _(g):  # Ysolde: salt-glass shards of rime falling
    return lay((tinkle(g, 1.0, 12, 2800, 6400, 1.0), 0.0, 1.0), (whoosh(g, 0.6, 3000, 900, 0.4), 0.0, 1.0),
               (glass_ring(g, 1760.0, 0.8, 0.4), 0.05, 1.0))


@ability("slow_hex", CAST)
def _(g):  # Ysolde: ink-dark motes settling over the target
    return ink(g, 1.3)


@ability("written_light", CAST)
def _(g):  # Ysolde's Swell: written strokes of pale light across each foe (a pen's stroke, made of light)
    return lay(*[(cut(g, 2600 + 400 * i, 0.22, 0.5), 0.14 * i, 1.0) for i in range(4)],
               *[(glass_ring(g, f, 1.0, 0.4), 0.14 * i + 0.1, 1.0) for i, f in enumerate((660.0, 880.0, 990.0, 1320.0))])


@ability("anchor_fall")
def _(g):  # Kerrid: the anchor comes down, dust and stone
    return lay((whoosh(g, 0.5, 1800, 300, 0.6), 0.0, 1.0), (thump(g, 90, 32, 0.3, 0.6, 0.9), 0.45, 1.0),
               (clang(g, 0.6, 0.6, 0.6), 0.45, 1.0), (grit(g, 0.8, 0.5), 0.5, 1.0))


@ability("fluke_cleave")
def _(g):  # Kerrid: the anchor-fluke bites, iron chips and splinters
    return lay((whoosh(g, 0.35, 600, 2000, 0.6), 0.0, 1.0), (hit(g, 100, 1.0), 0.3, 1.0), (clang(g, 0.8, 0.5, 0.5), 0.3, 1.0),
               (splinter(g, 0.8), 0.32, 1.0))


@ability("snub_line")
def _(g):  # Kerrid: the line snubbed hard, rope fibres snapping
    return lay((rope(g, 0.5, 400, 1400), 0.0, 1.0), (twang(g, 98.0, 0.9, 0.7), 0.35, 1.0),
               (crackle(g, 0.25, 400, 2600, 0.9, 0.08), 0.36, 0.7), (hit(g, 120, 0.7), 0.36, 1.0))


@ability("flash_housing", CAST)
def _(g):  # Liss: the lamp housing's flash in the foe's eyes (oil light)
    return lay((brass(g, 0.5, 0.4), 0.0, 1.0), (flame(g, 0.5, 0.6, 2400, 90), 0.02, 1.0), (whoosh(g, 0.25, 800, 3600, 0.5), 0.02, 1.0))


@ability("reel_shot")
def _(g):  # Liss: the line strikes home, brass bright
    return lay((whoosh(g, 0.3, 900, 3200, 0.6), 0.0, 1.0), (clang(g, 1.4, 0.7, 0.5), 0.28, 1.0), (hit(g, 140, 0.7), 0.28, 1.0))


@ability("hoist_haul", CAST)
def _(g):  # Liss (Ch8): the hoist hauls a group up
    return lay((rope(g, 1.4, 120, 520), 0.0, 1.0), (creak(g, 1.0, 50, 200), 0.2, 0.6),
               *[(tap(g, [420.0, 980.0], [0.05, 0.03], 1.0, 0.6, 0.05), 0.3 + 0.3 * i, 0.5) for i in range(3)])


# the Vowbound
@ability("brine_lash")
def _(g):  # Ilun: a lash of brine
    return lay((whoosh(g, 0.45, 500, 1700, 0.8), 0.0, 1.0), (splash(g, 1.0, 0.9, 2200), 0.38, 1.0), (chime(g, 0.3, 0.8), 0.4, 1.0))


@ability("tidal_ward", CAST)
def _(g):  # Ilun: water rising in a ring around itself
    return lay((water_lift(g, 1.6, 1.0), 0.0, 1.0), (ring_rise(g, 659.26, 1.2, 0.6), 0.3, 1.0))


@ability("floodnet", CAST)
def _(g):  # Ilun's Swell: a steady net of bound threads over each foe
    return lay((bound_light(g, 1.6, 1.0), 0.0, 1.0), (chime(g, 0.5, 1.4), 0.5, 1.0))


@ability("forge_bolt", CAST)
def _(g):  # Kahre: a forge-hot bolt
    return lay((sparks(g, 0.5, 160, 0.6, 0.2), 0.0, 1.0), (thunder(g, 1.4, 0.7, 260), 0.05, 1.0), (anvil(g, 0.4, 0.5), 0.05, 1.0))


@ability("last_strike")
def _(g):  # Kahre's Swell: raw lightning down onto the foe
    return lay((sparks(g, 0.8, 200, 0.6, 0.3), 0.0, 1.0), (burst(g, 0.05, [bq_highpass(800, 0.7)], 0.0002, 0.01), 0.3, 1.0),
               (thunder(g, 2.4, 1.0, 200), 0.3, 1.0), (anvil(g, 0.7, 0.9), 0.32, 1.0))


@ability("kite_flare", CAST)
def _(g):  # Virel: a kite's flare drifting down on the foe
    return lay((flare(g, 0.8, 0.9), 0.0, 1.0), (whoosh(g, 1.0, 2400, 700, 0.4), 0.4, 1.0))


@ability("flare_line", CAST)
def _(g):  # Virel's Swell: the kite-string burning, a flare on each foe
    return lay((flame(g, 1.6, 0.6, 1400, 80), 0.0, 1.0), (crackle(g, 1.4, 90, 3200, 0.9), 0.05, 0.4),
               *[(flare(g, 0.5, 0.6), 0.3 + 0.3 * i, 1.0) for i in range(3)])


# the foes (each in its creature's family)
@ability("ash_rake")
def _(g):
    return lay((creature(C.Moth, "ashwing", "attack", g), 0.0, 0.7), (ash(g, 0.6, 0.6), 0.15, 1.0))


@ability("wing_dust", CAST)
def _(g):
    return lay((creature(C.Moth, "ashwing", "move", g), 0.0, 0.6), (ash(g, 1.2, 0.8), 0.1, 1.0))


@ability("bank_the_fire", CAST)
def _(g):
    return lay((rumble(g, 1.4, 140), 0.0, 0.6), (flame(g, 1.2, 0.6, 700, 40), 0.1, 1.0), (crackle(g, 1.2, 40, 1800, 0.8), 0.1, 0.4))


@ability("ladle_swing")
def _(g):
    return lay((whoosh(g, 0.4, 400, 1400, 0.6), 0.0, 1.0), (oil(g, 0.5, 0.7), 0.35, 1.0), (flame(g, 0.8, 0.5, 900, 70), 0.36, 1.0),
               (hit(g, 100, 0.7), 0.35, 1.0))


@ability("slag_pour", CAST)
def _(g):
    return lay((rumble(g, 1.6, 120), 0.0, 0.6), (C.gurgle(g, 1.4, 20, 1.5, 4.0, 0.7), 0.1, 1.0),
               (crackle(g, 1.4, 70, 2400, 0.9), 0.2, 0.5), (flame(g, 1.4, 0.4, 900, 60), 0.2, 1.0))


@ability("recrust", QUIET)
def _(g):
    return lay((crackle(g, 1.0, 60, 1400, 0.8, 0.5), 0.0, 1.0), (stone(g, 0.6), 0.6, 1.0), (rumble(g, 0.8, 120), 0.0, 0.3))


@ability("breach")
def _(g):
    return lay((rumble(g, 1.6, 90), 0.0, 0.8), (thump(g, 70, 28, 0.4, 0.6, 1.2), 0.1, 1.0), (wave(g, 1.6, 1.0), 0.1, 1.0),
               (creak(g, 1.0, 30, 120, ((140.0, 1.0), (360.0, 0.6), (850.0, 0.3))), 0.2, 0.6))


@ability("crust_slam")
def _(g):
    return lay((whoosh(g, 0.4, 1400, 300, 0.6), 0.0, 1.0), (thump(g, 90, 34, 0.25, 0.5, 0.9), 0.35, 1.0), (stone(g, 0.8), 0.36, 1.0),
               (splash(g, 0.8, 0.5, 1600), 0.36, 1.0))


@ability("undertow_pull")
def _(g):
    return lay((whoosh(g, 1.2, 1600, 200, 0.7), 0.0, 1.0), (slosh(g, 1.2, 0.8, 0.9), 0.1, 1.0), (grit(g, 0.6, 0.4), 0.4, 1.0))


@ability("brine_iron")
def _(g):  # the Inquisitor's brine-iron: a salt burn
    return lay((Inquisitor.attack(0, g), 0.0, 0.8), (crackle(g, 0.6, 140, 3200, 0.9, 0.25), 0.45, 0.7))


@ability("haft_strike")
def _(g):
    return lay((whoosh(g, 0.35, 300, 1300, 0.7), 0.0, 1.0), (Inquisitor.iron(g, 0.6, 0.4), 0.3, 1.0), (hit(g, 120, 0.9), 0.3, 1.0))


@ability("shell_wall", CAST)
def _(g):  # his red shell armour closes
    return lay(*[(Inquisitor.plates(g, 0.9), 0.1 * i, 1.0) for i in range(3)], (Inquisitor.shield(g, 0.6), 0.35, 1.0))


@ability("torch_hulk", CAST)
def _(g):  # he torches the hulk: smoke over each foe
    return lay((flame(g, 1.8, 0.7, 900, 60), 0.0, 1.0), (creak(g, 1.0, 40, 160), 0.3, 0.5), (smoke(g, 2.0, 0.5), 0.4, 1.0))


@ability("hound_bite")
def _(g):
    return lay((creature(C.Hound, "raid_hound", "attack", g), 0.0, 0.9), (hit(g, 150, 0.6, 0.7), 0.12, 1.0))


@ability("pounce")
def _(g):
    return lay((creature(C.Hound, "raid_hound", "move", g), 0.0, 0.6), (whoosh(g, 0.3, 500, 1800, 0.6), 0.1, 1.0),
               (hit(g, 110, 1.0), 0.35, 1.0))


@ability("brine_spit", CAST)
def _(g):
    return lay((burst(g, 0.12, [bq_bandpass(1800, 0.7)], 0.002, 0.03), 0.0, 0.6), (splash(g, 0.5, 0.5, 3000), 0.15, 1.0))


@ability("pinch")
def _(g):
    return lay((creature(C.Crab, "reef_crab", "attack", g), 0.0, 0.8), (shell_crack(g, 0.4), 0.15, 1.0), (grit(g, 0.3, 0.3), 0.15, 1.0))


@ability("scuttle_claw")
def _(g):
    return lay((creature(C.Crab, "scuttler", "attack", g), 0.0, 0.8), (hit(g, 180, 0.6, 0.5), 0.12, 1.0))


@ability("tide_claw")
def _(g):  # the Undertow's light, sideways
    return lay((creature(C.Crab, "tide_crawler", "attack", g), 0.0, 0.8), (whoosh(g, 0.4, 2400, 600, 0.4), 0.05, 1.0),
               (hit(g, 130, 0.6), 0.15, 1.0))


@ability("housing_glare", CAST)
def _(g):  # a wreck crab's lamp-housing glare
    return lay((brass(g, 0.6, 0.6), 0.0, 1.0), (panes(g, 0.3, 0.4), 0.02, 1.0), (glass_ring(g, 1480.0, 0.9, 0.5), 0.05, 1.0))


@ability("dive_rake")
def _(g):
    return lay((whoosh(g, 0.5, 2400, 500, 0.7), 0.0, 1.0), (creature(C.Bird, "gull_harrier", "attack", g), 0.1, 0.7),
               (burst(g, 0.2, [bq_bandpass(3600, 1.0)], 0.005, 0.05), 0.45, 0.5))


@ability("wing_peck")
def _(g):
    return lay((creature(C.Bird, "squall_wing", "attack", g), 0.0, 0.8), (tap(g, [1900.0, 3400.0], [0.01, 0.006], 1.0, 0.7), 0.15, 0.6))


@ability("spark_spit", CAST)
def _(g):
    return lay((creature(C.Sparker, "vein_sparker", "attack", g), 0.0, 0.6), (spark(g, 0.8), 0.15, 1.0), (static(g, 0.5, 0.4), 0.15, 1.0))


@ability("lure_glow", CAST)
def _(g):  # the lantern eel's lure: a cold glow
    return lay((hum(g, 1.2, 440.0, 0.4), 0.0, 1.0), (glass_ring(g, 1760.0, 1.0, 0.4), 0.1, 1.0), (bubble_train(g, 5, 0.004, 0.008, (0.1, 0.2), 0.3, 0.6), 0.2, 1.0))


@ability("oil_slap")
def _(g):
    return lay((creature(C.Polyp, "oil_slug", "attack", g), 0.0, 0.7), (oil(g, 0.6, 0.9), 0.1, 1.0))


@ability("smother", CAST)
def _(g):
    return lay((oil(g, 1.0, 0.8), 0.0, 1.0), (whoosh(g, 0.8, 900, 200, 0.4), 0.1, 1.0))


@ability("polyp_mend_hit", CAST)
def _(g):  # held motes mend (sinking, never rising)
    return lay((creature(C.Polyp, "spawn_polyp", "idle", g), 0.0, 0.5), (whoosh(g, 1.0, 1400, 400, 0.3), 0.1, 1.0),
               (glass_ring(g, 587.33, 1.2, 0.35), 0.2, 1.0), (glass_ring(g, 523.25, 1.2, 0.3), 0.5, 1.0))


@ability("limpet_clamp")
def _(g):
    return lay((creature(C.Polyp, "tower_limpet", "attack", g), 0.0, 0.8), (stone(g, 0.8), 0.15, 1.0))


@ability("pull_in", QUIET)
def _(g):
    return lay((creature(C.Tortoise, "slag_tortoise", "move", g), 0.0, 0.6), (stone(g, 0.6), 0.3, 1.0), (grit(g, 0.4, 0.3), 0.32, 1.0))


@ability("shell_ram")
def _(g):
    return lay((creature(C.Tortoise, "slag_tortoise", "attack", g), 0.0, 0.8), (thump(g, 100, 40, 0.2, 0.5, 0.6), 0.3, 1.0),
               (stone(g, 0.7), 0.3, 1.0))


@ability("sail_drop")
def _(g):
    return lay((creature(C.Leech, "sail_leech", "attack", g), 0.0, 0.7), (burst(g, 0.2, [bq_lowpass(1400, 0.7)], 0.003, 0.05), 0.2, 0.8))


@ability("skim_bite")
def _(g):
    return lay((creature(C.Skipper, "shoal_skipper", "attack", g), 0.0, 0.8), (splash(g, 0.6, 0.6, 3200), 0.1, 1.0))


@ability("shoal_nip")
def _(g):
    return lay((creature(C.Swarm, "glassfry", "attack", g), 0.0, 0.8), (tinkle(g, 0.3, 4, 3600, 6400, 0.4), 0.05, 1.0))


@ability("glass_jab")
def _(g):
    return lay((creature(C.Crab, "bottle_hermit", "attack", g), 0.0, 0.8), (glass_ring(g, 2200.0, 0.4, 0.5), 0.12, 1.0),
               (hit(g, 160, 0.5, 0.6), 0.12, 1.0))


@ability("glass_flare", CAST)
def _(g):  # the hermit's bottle flares
    return lay((flame(g, 0.8, 0.7, 1800, 80), 0.0, 1.0), (glass_ring(g, 1980.0, 1.0, 0.5), 0.05, 1.0), (whoosh(g, 0.4, 600, 3000, 0.4), 0.0, 1.0))


@ability("gnaw")
def _(g):  # Hullgnaw's gnaw: the spawn's wound-light, sinking
    return lay((creature(C.Eel, "hullgnaw", "attack", g), 0.0, 0.8), (splinter(g, 0.6), 0.2, 1.0), (whoosh(g, 0.6, 1600, 300, 0.3), 0.25, 1.0))


@ability("rib_lash")
def _(g):
    return lay((whoosh(g, 0.35, 500, 1700, 0.6), 0.0, 1.0), (creak(g, 0.5, 60, 260), 0.05, 0.6), (hit(g, 110, 0.9), 0.3, 1.0))


@ability("thrash")
def _(g):
    return lay((creature(C.Eel, "hullgnaw", "hurt", g), 0.0, 0.6), (slosh(g, 1.2, 1.0, 3.0), 0.0, 1.0), (splinter(g, 0.5), 0.3, 1.0))


@ability("hood_slam")
def _(g):  # the Drownbell's hood comes down
    return lay((whoosh(g, 0.5, 1200, 300, 0.6), 0.0, 1.0), (thump(g, 80, 30, 0.35, 0.6, 1.0), 0.45, 1.0),
               (clang(g, 0.45, 0.7, 0.8), 0.45, 1.0), (splash(g, 1.0, 0.6, 1600), 0.46, 1.0))


@ability("flood_surge", CAST)
def _(g):
    return lay((wave(g, 1.6, 1.0), 0.0, 1.0), (whoosh(g, 1.0, 300, 1400, 0.4), 0.0, 1.0))


@ability("undertow_surge", CAST)
def _(g):  # the undertow drags at each foe's feet
    return lay((whoosh(g, 1.2, 1400, 180, 0.6), 0.0, 1.0), (slosh(g, 1.2, 0.8, 1.2), 0.1, 1.0),
               (bubble_train(g, 10, 0.004, 0.01, (0.04, 0.1), 0.4, 0.7), 0.3, 1.0))


@ability("haul")
def _(g):  # the Spar-Wraith hauls its spar down
    return lay((rope(g, 0.6, 200, 700), 0.0, 1.0), (whoosh(g, 0.4, 1400, 300, 0.6), 0.4, 1.0), (thump(g, 90, 36, 0.25, 0.5, 0.8), 0.75, 1.0),
               (splinter(g, 0.7), 0.76, 1.0))


@ability("sea_lash", CAST)
def _(g):
    return lay((whoosh(g, 0.6, 500, 2000, 0.7), 0.0, 1.0), (wave(g, 1.2, 0.8), 0.3, 1.0))


@ability("shroud_sweep")
def _(g):  # its rigging shrouds sweep the party
    return lay((whoosh(g, 0.8, 300, 1500, 0.8), 0.0, 1.0), (rope(g, 0.8, 200, 800), 0.1, 0.7), (hit(g, 110, 0.6), 0.6, 1.0))


@ability("spar_stab")
def _(g):
    return lay((whoosh(g, 0.25, 900, 2400, 0.6), 0.0, 1.0), (hit(g, 130, 0.9), 0.2, 1.0), (splinter(g, 0.8), 0.21, 1.0))


ABILITIES = dict(R)

# The two Swell styles (choreo folder): Kerrid's swing and Liss's reel-stop
STYLE = {
    "whoosh_swing": (lambda g: lay((whoosh(g, 0.7, 300, 1300, 0.8), 0.0, 1.0), (rope(g, 0.5, 200, 700), 0.05, 0.5),
                                   (whoosh(g, 0.5, 400, 1600, 0.7), 0.45, 1.0)), -20.0),  # the choreo whoosh rule
    "swell_kerrid": (lambda g: lay((thump(g, 80, 30, 0.35, 0.6, 1.0), 0.0, 1.0), (clang(g, 0.55, 0.8, 0.8), 0.0, 1.0),
                                   (anvil(g, 0.25, 0.5), 0.02, 1.0), (grit(g, 0.8, 0.5), 0.05, 1.0)), -19.0),
    "reel_whir": (lambda g: lay((crackle(g, 0.8, 220, 1500, 1.2), 0.0, 0.8), (whoosh(g, 0.8, 600, 2400, 0.5), 0.0, 1.0),
                                (snap(g, 0.6), 0.78, 1.0)), STRIKE),
    "swell_liss": (lambda g: lay((clang(g, 1.5, 0.9, 0.6), 0.0, 1.0), (twang(g, 110.0, 1.0, 0.6), 0.0, 1.0),
                                 (hit(g, 150, 0.7), 0.0, 1.0), (glass_ring(g, 2637.0, 0.8, 0.3), 0.02, 1.0)), -19.0),
}

JOBS: list[tuple[str, str, object, float]] = (
    [(BATTLE_DIR, f"abl_{e}", fn, t) for e, (fn, t) in ABILITIES.items()]
    + [(CHOREO_DIR, name, fn, t) for name, (fn, t) in STYLE.items()]
)
FILES = [os.path.relpath(os.path.join(d, n + ".ogg"), os.path.join(ROOT, "assets", "lfs", "audio", "sfx"))
         for d, n, _, _ in JOBS]


def render(out_dir: str = os.path.join(ROOT, "assets", "lfs", "audio", "sfx"), verbose: bool = True) -> dict:
    res = {}
    for i, (d, name, fn, tgt) in enumerate(JOBS):
        sub = os.path.relpath(d, os.path.join(ROOT, "assets", "lfs", "audio", "sfx"))
        path = os.path.join(out_dir, sub, name + ".ogg")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        seed = SEED + 100 * i
        x = finish(room(fn(rng(seed)), seed + 7, mix=0.1, tail=0.3, rt60=0.7), tgt)
        write_ogg(path, x, quality=4.0)
        res[name] = measure(x)
        if verbose:
            m = res[name]
            print(f"{sub}/{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}", flush=True)
    return res


if __name__ == "__main__":
    render()
