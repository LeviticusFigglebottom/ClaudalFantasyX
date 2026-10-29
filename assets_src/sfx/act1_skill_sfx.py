"""Act I's silent boss and set-piece skills, heard (M3-AUD-861, ADR 0041; Git LFS, ADR 0173).

These skills hit nobody, heal nobody and add no status, so BattleVfx played nothing for them and BattleAudio heard
nothing but the choreography's accents (tools/audio/act1_audio_audit.py, "Skills"). Each one is a moment the
player has to read: a telegraph that says "next turn this lands" (SPEC pillar 4, tactical clarity), a summon, or
the seawall set-piece's tide turning. Each now has its own sound, through battle_sfx.json's `skills` table (one row
per skill id). Telegraphs build and never resolve; strikes land; summons arrive on a surge.

Synthesized here and in tools/audio/synth/ (SPEC §2, §9): no samples, no recordings, no generated audio.

    rouse_polyp       the Drownbell rouses a spawn-polyp: its low under-toll, and the polyp rising out of the flood
    gnaw_coil         the Hullgnaw coils for Gnaw (2 turns): its ribs creaking tighter, a low throat building
    recrust_gather    the Cinder Matron gathers to Recrust (2 turns): ash crackle and a deep slag rumble rising
    lines_taut        the Spar-Wraith hauls its lines taut for Haul (2 turns): rope creaking up, the rigging thrumming
    reach_for_stair   a tide crawler climbs for the hand-line (telegraph): wet claws scraping up laterite
    grip_the_stair    ...and grips it: claws biting stone, the climbers jolted back
    rope_dive         a squall wing dives Liss's rope: the dive, the rope struck and twanging
    climb_up          the Climb reaches the wall-head: hands and feet on the parapet, the rope coming over
    surge_crawler     the sea throws a tide crawler onto the wall: a wave breaking, claws landing
    surge_wing        the sea throws a squall wing up: a wave breaking, a wing tearing out of the spray
    surge_ebb         the surge drains back off the wall
    storm_call_sound  Pell draws the breath for Storm-Call (telegraph): a deep intake, the note's first growl
    storm_call        Pell's Storm-Call (act1_cutscene_sfx.pell_storm_note, the same voice), and the spawn following it
    close_the_hand    Undertow's Reach closes its hand (2 turns): a huge swell drawing up, the deep groaning
    hand_closes       ...the hand closes on the Climb: water crushing in on stone
    breach_gather     Undertow's Reach gathers the Breach (4 turns): the sea drawing back off the wall, building

assets/lfs/audio/sfx/battle/<skill>.ogg (mono, Vorbis q4): telegraphs and summons -19 LUFS momentary max, strikes -18,
the Climb's arrival -20 (targets.py's combat rule, sfx/battle/*.ogg, -19 +- 2.5).

Render:  python3 tools/audio/render_all.py --only act1_skill_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from act1_cutscene_sfx import pell_storm_note  # noqa: E402
from act2_creature_sfx import splash, whoosh  # noqa: E402
from creature_sfx import (Bird, Crab, Polyp, buf, burst, crackle, finish, room, slosh, tap, throat,  # noqa: E402
                          thump, unit)
from creature_sfx import glide as bend  # noqa: E402
from field_ambience import lap, stick_slip  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.score import n as note  # noqa: E402
from underwater_sfx import _n, _t, bubble_train, noise, place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "lfs", "audio", "sfx", "battle")
SEED = 20261862
QUALITY = 4.0
TELL, STRIKE, ARRIVE = -19.0, -18.0, -20.0
CRAWLER = dict(family="crab", size=1.1, pitch=0.85, legs=4, spawn=True)   # creature_sfx.CREATURES["tide_crawler"]
WING = dict(family="bird", size=1.1, pitch=0.8, spawn=True)               # creature_sfx.CREATURES["squall_wing"]
POLYP = dict(family="polyp", size=1.0, pitch=1.0, spawn=True)             # creature_sfx.CREATURES["spawn_polyp"]


def tell(x: np.ndarray, curve: float = 1.5) -> np.ndarray:
    """A telegraph's envelope over x: building to the end, then cut short (it never resolves)."""
    sec = len(x) / 44100.0
    t = np.arange(len(x)) / 44100.0
    return x * np.clip(t / sec, 0, 1) ** curve * np.clip((sec - t) / 0.08, 0, 1)


def rumble(g, sec: float, fc: float = 160.0, amp: float = 1.0) -> np.ndarray:
    return amp * unit(noise(g, _n(sec), [bq_lowpass(fc, 0.7), bq_highpass(28, 0.7)]))


def creak(g, sec: float, lo: float, hi: float, body=((280.0, 1.0), (690.0, 0.6), (1500.0, 0.25))) -> np.ndarray:
    return stick_slip(g, sec, lo, hi, list(body))


def rope(g, sec: float, lo: float = 140.0, hi: float = 600.0) -> np.ndarray:
    return stick_slip(g, sec, lo, hi, [(900.0, 1.0), (2100.0, 0.5), (3800.0, 0.2)], q=4.0)


def twang(g, f0: float = 82.0, sec: float = 1.2, amp: float = 1.0) -> np.ndarray:
    """A taut rope struck: a low plucked string, its pitch sagging as it swings."""
    t = _t(_n(sec))
    f = f0 * (1 + 0.04 * np.exp(-t / 0.05))
    ph = 2 * np.pi * np.cumsum(f) / 44100.0
    y = sum(a * np.sin(k * ph) for k, a in ((1, 1.0), (2, 0.5), (3, 0.25), (4, 0.12)))
    return amp * unit(y) * np.exp(-t / (sec * 0.3)) * np.clip(t / 0.002, 0, 1)


def wave(g, sec: float = 1.6, amp: float = 1.0) -> np.ndarray:
    """A wave breaking on the wall: the boom, the sheet of spray, the water running back."""
    x = buf(sec + 0.5)
    place(x, thump(g, 70, 34, 0.25, 0.4, 0.9), 0.0)
    place(x, splash(g, sec, 1.0, 2000), 0.02)
    place(x, slosh(g, sec * 0.7, 0.6, 1.2), sec * 0.4)
    return amp * x


def claws_on_stone(g, sec: float, rate: float, amp: float = 1.0) -> np.ndarray:
    """Wet claw tips on laterite: hard taps with a little grit after each."""
    x = buf(sec + 0.3)
    t = 0.0
    while t < sec:
        place(x, tap(g, [1300.0 * 0.85, 2300.0 * 0.85, 3600.0 * 0.85], [0.008, 0.006, 0.004], 1.0, 0.6, 0.1), t,
              float(g.uniform(0.5, 1.0)))
        place(x, crackle(g, 0.06, 300, 1600, 0.8, 0.03), t + 0.005, 0.3)
        t += float(g.uniform(0.7, 1.3)) / rate
    return amp * x


# --------------------------------------------------------------------------- the skills


def rouse_polyp(g):
    x = buf(3.4)
    place(x, tower_bell(note("A1"), 0.45, seed=int(g.integers(1 << 30)), t60=3.0, dark=0.75), 0.0)
    place(x, bubble_train(g, 14, 0.004, 0.012, (0.05, 0.12), 0.5, 0.8), 0.6)
    place(x, Polyp.idle(POLYP, 0, g), 1.1, 0.8)
    return x


def gnaw_coil(g):
    x = buf(2.6)
    place(x, tell(creak(g, 2.2, 30, 160, ((180.0, 1.0), (520.0, 0.6), (1200.0, 0.2)))), 0.0)
    place(x, throat(g, 2.2, bend(55, 70, 1.0), [(240, 100, 1.0), (580, 160, 0.3)], rough=0.4, sub=0.4, breath=0.5,
                    attack=1.6, release=0.1, tilt=1.4) * 0.6, 0.0)
    place(x, slosh(g, 1.6, 0.4, 2.0), 0.2)
    return x


def recrust_gather(g):
    x = buf(2.8)
    place(x, tell(rumble(g, 2.4, 140), 1.2), 0.0)
    cr = crackle(g, 2.4, 70, 2600, 0.9)
    place(x, 0.5 * tell(cr, 2.0), 0.0)
    place(x, tell(crackle(g, 2.4, 25, 900, 0.7)) * 0.5, 0.0)
    return x


def lines_taut(g):
    x = buf(2.8)
    place(x, tell(rope(g, 2.3, 100, 560), 1.2), 0.0)
    t = _t(_n(2.3))
    thrum = np.sin(2 * np.pi * (70 + 40 * t / 2.3) * t) + 0.4 * np.sin(2 * np.pi * (140 + 80 * t / 2.3) * t)
    place(x, 0.4 * tell(unit(thrum)), 0.0)
    place(x, creak(g, 1.0, 50, 220), 0.4, 0.5)
    return x


def reach_for_stair(g):
    x = buf(2.2)
    claws = claws_on_stone(g, 1.6, 5.0, 1.0)
    k = _n(1.6)
    claws[:k] *= np.linspace(0.0, 1.0, k) ** 0.8   # climbing closer, then holding at the line
    place(x, claws, 0.0)
    place(x, slosh(g, 1.2, 0.3, 2.5), 0.0)
    return x


def grip_the_stair(g):
    x = buf(1.8)
    place(x, Crab.attack(CRAWLER, 0, g), 0.0)
    place(x, thump(g, 120, 55, 0.1, 0.5, 0.5), 0.12)
    place(x, rope(g, 0.6, 300, 900), 0.15, 0.6)   # the climbers' line jerked
    return x


def rope_dive(g):
    x = buf(2.2)
    place(x, Bird.attack(WING, 0, g), 0.0)
    place(x, whoosh(g, 0.5, 2400, 500, 0.6), 0.05)
    place(x, twang(g, 82.0, 1.4, 0.8), 0.48)
    return x


def climb_up(g):
    """The Climb makes the wall-head: a hand slapping onto the parapet, boots scrabbling on stone, the rope pulled
    over after them. It is good news, so it is light and quick."""
    x = buf(1.8)
    place(x, burst(g, 0.05, [bq_bandpass(900, 0.8)], 0.001, 0.015), 0.0)          # a palm on wet stone
    for i in range(3):
        place(x, thump(g, 160, 95, 0.04, 0.3, 0.25), 0.25 + 0.18 * i, 0.5)       # boots
        place(x, crackle(g, 0.08, 300, 1500, 0.8, 0.03), 0.26 + 0.18 * i, 0.3)
    place(x, rope(g, 0.7, 250, 800), 0.8, 0.6)
    return x


def surge_crawler(g):
    x = buf(2.6)
    place(x, wave(g, 1.5, 1.0), 0.0)
    place(x, Crab.move(CRAWLER, 0, g), 0.7, 0.7)
    return x


def surge_wing(g):
    x = buf(2.6)
    place(x, wave(g, 1.5, 1.0), 0.0)
    place(x, Bird.move(WING, 0, g), 0.55, 0.8)
    return x


def surge_ebb(g):
    x = buf(2.6)
    place(x, slosh(g, 2.2, 1.0, 0.8), 0.0)
    place(x, whoosh(g, 1.8, 1200, 200, 0.5), 0.1)
    for k in range(3):
        place(x, lap(g, 1.0 - 0.25 * k), 1.0 + 0.4 * k, 0.4)
    return x


def storm_call_sound(g):
    """Pell's telegraph: a deep breath drawn in, and the note's first growl, low in his chest."""
    x = buf(2.4)
    n_ = _n(1.2)
    t = _t(n_)
    intake = unit(noise(g, n_, [bq_bandpass(900, 0.6), bq_lowpass(3000, 0.7)])) * np.sin(np.pi * np.clip(t / 1.2, 0, 1))
    place(x, intake, 0.0, 0.5)
    place(x, throat(g, 1.0, bend(38, 42, 1.0), [(300, 120, 1.0), (700, 200, 0.3)], rough=0.5, sub=0.5, breath=0.4,
                    attack=0.5, release=0.1, tilt=1.4), 1.2, 0.7)
    return x


def storm_call(g):
    """Storm-Call itself: Pell's huge low note (the cutscene's own voice), and one spawn going off the wall after it."""
    note_ = pell_storm_note(g)
    x = buf(len(note_) / 44100.0 + 1.0)
    place(x, note_, 0.0)
    place(x, slosh(g, 1.6, 0.5, 1.0), 2.4)
    place(x, splash(g, 1.4, 0.6, 1500), 3.0)
    return x


def close_the_hand(g):
    x = buf(3.2)
    place(x, tell(rumble(g, 2.8, 90), 1.3), 0.0)
    place(x, tell(slosh(g, 2.6, 0.8, 0.6), 1.0), 0.1)
    place(x, throat(g, 2.6, bend(36, 46, 1.0), [(200, 90, 1.0), (450, 150, 0.4)], rough=0.6, sub=0.6, breath=0.6,
                    attack=2.0, release=0.1, tilt=1.6) * 0.5, 0.1)
    return x


def hand_closes(g):
    x = buf(2.4)
    place(x, whoosh(g, 0.35, 300, 1400, 0.6), 0.0)
    place(x, thump(g, 80, 30, 0.35, 0.5, 1.0), 0.3)
    place(x, splash(g, 1.6, 1.0, 1700), 0.3)
    place(x, creak(g, 0.8, 40, 160, ((150.0, 1.0), (380.0, 0.6), (900.0, 0.3))), 0.45, 0.5)  # stone under it
    return x


def breach_gather(g):
    """Four turns out: the sea drawing back off the wall, slowly, the deep building under it."""
    x = buf(3.6)
    place(x, whoosh(g, 3.0, 900, 160, 0.6), 0.0)
    place(x, tell(rumble(g, 3.2, 110), 1.0), 0.0)
    place(x, bubble_train(g, 10, 0.006, 0.014, (0.1, 0.25), 0.3, 0.6), 1.0)
    return x


SKILLS: list[tuple[str, object, float]] = [
    ("rouse_polyp", rouse_polyp, TELL), ("gnaw_coil", gnaw_coil, TELL), ("recrust_gather", recrust_gather, TELL),
    ("lines_taut", lines_taut, TELL), ("reach_for_stair", reach_for_stair, TELL),
    ("grip_the_stair", grip_the_stair, STRIKE), ("rope_dive", rope_dive, STRIKE), ("climb_up", climb_up, ARRIVE),
    ("surge_crawler", surge_crawler, TELL), ("surge_wing", surge_wing, TELL), ("surge_ebb", surge_ebb, ARRIVE),
    ("storm_call_sound", storm_call_sound, TELL), ("storm_call", storm_call, STRIKE),
    ("close_the_hand", close_the_hand, TELL), ("hand_closes", hand_closes, STRIKE),
    ("breach_gather", breach_gather, TELL),
]
FILES = [name + ".ogg" for name, _, _ in SKILLS]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for i, (name, fn, tgt) in enumerate(SKILLS):
        seed = SEED + 100 * i
        x = room(fn(rng(seed)), seed + 7, mix=0.12, tail=0.4, rt60=0.9)  # the battle's open air
        x = finish(x, tgt)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=QUALITY)
        res[name] = measure(x)
        if verbose:
            m = res[name]
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  peak {m['sample_peak_dbfs']:.2f}",
                  flush=True)
    return res


if __name__ == "__main__":
    render()
