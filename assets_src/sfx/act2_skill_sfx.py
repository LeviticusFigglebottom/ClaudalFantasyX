"""Act II's skills that make no hit, heal or status, given their own sound (M4-A2P-093; the cue sheet §4; plain git,
ADR 0175).

The Act II audit (tools/audio/act1_audio_audit.py --act 2, "Skills") lists every skill whose effect would be silent
but for the choreography's accents. Each gets its own sound here, made from what the skill does:

    unravel   Ch12, the cord moth's buff-strip (skills.json: it strips the woven buffs, haste, protect, shell and
              regen, from its target). A weave pulled apart: the threads drawn taut and snapping one after another,
              and a ward's glassy ring dying as it goes.

and the Wakefin's move list (Ch15, bosses/wakefin.md §4; the cue sheet §4 "Darkness telegraphs"). It is fought in the
dark, so its telegraphs are sounds (pillar 4): each has its own pitch family inside 1-4 kHz, where the `wakefin` stems
leave room, and each sound is timed to its clip (wind-up, then contact at the sheet's time):

    fin_cut        the seam's hiss running along the rail, high (2.6 -> 3.6 kHz), then the sweep across the deck (0.8 s)
    sound_dive     the blade sinking: a falling plunk (1.3 -> 0.9 kHz, the family's lowest) and the bubbles going down. It says "it's gone
                   deep", never "it's gone" (ADR 0204 §3): a slow pressure thrum stays under it to the end.
    wakefin_rise   the sea-glow ring opening under a hero: a glassy ring swelling at 1.9 kHz, then the breach (0.85 s)
    wake_wash      the hard turn and the tail slap (0.75 s), the wake washing across the deck (mid, 1.2 kHz)
    bill_strike    phase 2: it rears at the bow (a rising hiss and a creak of the bow), the stab (0.7 s), a knock on wood. Its rear is
                   a noise band rising to 1.4 kHz, under the wash's hiss and apart from the dive's tonal plunk
    close_circle   (a phase sound, phase_close_circle.ogg) it rams the hull: a hollow boom, the barge rocking and
                   creaking, the water slapping back

and two Vowbound skills (M4-A2P-024, called by Asha) whose effect is no hit, heal or status:

    nhoa_echo      Nhoa copies the last enemy action: a salt-glass sweep drawn in, and the same figure given back from
                   her, a beat later and brighter (the echo)
    cord_lift      Hesk lifts the party's statuses: pale threads drawn up (a rising plucked-cord glissando), each knot's
                   light loosing, and a soft holy bell at the top

and the Lamp Engine's conduit crawlers (Ch11, M4-A2P-022, bosses/lamp_engine.md §4), whose support skills make no
hit, heal or status:

    crawler_mend   it scuttles to the engine's leg and relights a broken part: quick leg-ticks on metal, a spark
                   catching (a crackle), and the conduit's bound light humming back up (it rises and holds, never pulses)
    crawler_tend   it tends the engine: a few unhurried leg-ticks and soft taps on the casing, a small settling hum

The Wakefin's skill ids are the sheet's proposed ones; combat owns them, and the rows wait in battle_sfx.json until they land.

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Files are assets/audio/act2/sfx/battle/skill_<id>.ogg (mono,
q4), at -19 LUFS momentary max (the combat rule).

Render:  python3 tools/audio/render_all.py --only act2_skill_sfx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import act2_creature_sfx as A2  # noqa: E402
from creature_sfx import buf, creak, finish, glass_ring, glide, room, slosh, tap, thump  # noqa: E402
from field_ambience import stick_slip  # noqa: E402
from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, rng  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from underwater_sfx import _n, _t, bubble_train, noise, place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act2", "sfx", "battle")
SEED = 20262200
QUALITY = 4.0
CAST = -19.0


def unravel(g) -> np.ndarray:
    x = buf(1.6)
    for k in range(5):                                           # threads drawn taut, each snapping
        at = 0.05 + 0.16 * k + float(g.uniform(-0.02, 0.02))
        place(x, stick_slip(g, 0.1, 400.0 + 120 * k, 1400.0, [(2200.0 + 300 * k, 1.0), (4100.0, 0.4)], q=6.0), at, 0.5)
        place(x, tap(g, [3200.0 + 250 * k, 5200.0], [0.01, 0.006], 0.8, click=0.9), at + 0.1)
    ring = glass_ring(g, 1568.0, 1.2, 0.6)                       # the ward's ring, dying as it goes
    ring *= np.linspace(1, 0, len(ring)) ** 1.5
    place(x, ring, 0.0, 0.5)
    return x


# --------------------------------------------------------------------------- the Wakefin (Ch15)
HULL = ((95.0, 1.0), (240.0, 0.7), (610.0, 0.3))                # the barge's planking


def _seam_hiss(g, sec: float, f_from: float, f_to: float) -> np.ndarray:
    """Water hissing along a narrow band that slides f_from -> f_to: the telegraph's pitch family."""
    n = _n(sec)
    t = _t(n)
    f = f_from * (f_to / f_from) ** (t / sec)
    y = np.zeros(n)
    for k in range(0, n, 512):                                   # the band follows the slide, block by block
        seg = noise(g, min(512, n - k) + 1024, [bq_bandpass(float(f[k]), 2.2)])[1024:]
        y[k: k + len(seg)] = seg
    return y / (np.abs(y).max() + 1e-9) * np.clip(t / (0.7 * sec), 0, 1) ** 1.5


def fin_cut(g) -> np.ndarray:
    x = buf(1.8)
    place(x, _seam_hiss(g, 0.8, 2600.0, 3600.0), 0.0, 0.6)      # the seam brightening along its path
    place(x, A2.Sailfin.cut(g, 0.9, 0.5), 0.1)
    place(x, A2.whoosh(g, 0.4, 3200, 900, 0.8), 0.62)             # the blade sweeps the deck
    place(x, A2.splash(g, 0.9, 0.7, 2600), 0.8)
    place(x, A2.Sailfin.thrum(g, 46, 0.6, 0.5), 0.8)
    return x


def sound_dive(g) -> np.ndarray:
    x = buf(1.9)
    plunk = glass_ring(g, 1300.0, 0.6, 0.6) * np.exp(-_t(_n(0.6)) / 0.12)
    place(x, plunk, 0.0, 1.6)
    place(x, glass_ring(g, 900.0, 0.8, 0.5) * np.exp(-_t(_n(0.8)) / 0.2), 0.22, 1.6)  # the plunk falls
    place(x, A2.slosh(g, 0.8, 0.3, 1.2), 0.0)
    place(x, bubble_train(g, 14, 0.006, 0.014, (0.04, 0.1), 0.5, 0.6), 0.15)
    t = _t(_n(1.7))
    deep = A2.Sailfin.thrum(g, 38, 1.7, 0.5) * np.clip(t / 0.6, 0, 1)                  # still there, below
    place(x, deep, 0.2)
    return x


def wakefin_rise(g) -> np.ndarray:
    x = buf(2.0)
    ring = glass_ring(g, 1900.0, 0.85, 0.7)
    ring *= np.clip(_t(len(ring)) / 0.7, 0, 1) ** 2                          # the glow ring opening, swelling
    place(x, ring, 0.0)
    place(x, glass_ring(g, 1900.0 * 1.5, 0.7, 0.08) * np.clip(_t(_n(0.7)) / 0.6, 0, 1), 0.15)
    place(x, A2.gurgle(g, 0.4, 20, 0.005, 0.014, 0.5), 0.45)
    place(x, A2.splash(g, 1.1, 1.0, 3000), 0.85)                   # the breach, bill first
    place(x, A2.whoosh(g, 0.3, 700, 2600, 0.7), 0.7)
    place(x, A2.Sailfin.thrum(g, 52, 0.6, 0.6), 0.85)
    return x


def wake_wash(g) -> np.ndarray:
    x = buf(2.0)
    place(x, A2.Sailfin.cut(g, 0.6, 0.6), 0.0)                    # the hard turn away
    place(x, thump(g, 160, 70, 0.08, 0.6, 0.4), 0.75, 0.9)       # the tail slap
    place(x, A2.splash(g, 0.8, 0.8, 1800), 0.75)
    n = _n(1.1)
    wash = noise(g, n, [bq_bandpass(1200, 0.8), bq_lowpass(2400, 0.7)]) * np.sin(np.pi * _t(n) / 1.1) ** 1.2
    place(x, wash / (np.abs(wash).max() + 1e-9), 0.85, 0.6)       # the wake over the deck
    place(x, slosh(g, 1.0, 0.7, 2.2), 1.0)
    return x


def bill_strike(g) -> np.ndarray:
    x = buf(1.6)
    place(x, A2.whoosh(g, 0.55, 400, 1400, 0.6), 0.0)             # it rears at the bow
    place(x, creak(g, 0.5, 40, 160, HULL, 0.5), 0.05)
    place(x, A2.whoosh(g, 0.18, 2400, 1200, 0.9), 0.55)            # the stab
    place(x, thump(g, 420, 180, 0.03, 1.0, 0.2), 0.7, 0.9)        # the bill on the planking
    place(x, tap(g, [700.0, 1650.0, 2900.0], [0.05, 0.03, 0.015], 0.8, click=0.8), 0.7)
    place(x, A2.splash(g, 0.7, 0.5, 2200), 0.8)
    return x


def close_circle(g) -> np.ndarray:
    x = buf(2.6)
    place(x, A2.Sailfin.cut(g, 0.6, 0.5), 0.0)
    place(x, thump(g, 70, 32, 0.25, 0.7, 1.0), 0.55, 1.0)         # it rams the hull: a hollow boom
    place(x, thump(g, 140, 60, 0.12, 0.5, 0.5), 0.56, 0.6)
    for k in range(3):                                           # the barge rocking, creaking, settling
        place(x, creak(g, 0.45, 30 + 10 * k, 120, HULL, 0.6 - 0.15 * k), 0.75 + 0.45 * k)
    place(x, slosh(g, 1.6, 0.8, 1.4), 0.65)
    return x


SKILLS: list[tuple[str, object, float]] = [("unravel", unravel, CAST), ("fin_cut", fin_cut, CAST),
                                           ("sound_dive", sound_dive, CAST), ("wakefin_rise", wakefin_rise, CAST),
                                           ("wake_wash", wake_wash, CAST), ("bill_strike", bill_strike, CAST)]
def _glass_sweep(g, f0: float, f1: float, count: int, sec: float, amp: float = 1.0) -> np.ndarray:
    x = buf(sec + 0.8)
    for k in range(count):
        f = f0 * (f1 / f0) ** (k / max(1, count - 1))
        place(x, glass_ring(g, f, 0.5, 0.5), sec * k / count)
    return amp * x


def nhoa_echo(g) -> np.ndarray:
    x = buf(2.2)
    place(x, _glass_sweep(g, 3800.0, 2300.0, 6, 0.5, 0.8), 0.0)          # drawn in
    place(x, _glass_sweep(g, 2300.0 * 1.5, 3800.0 * 1.5, 6, 0.5, 0.6), 0.75)   # given back, brighter
    air = noise(g, _n(1.4), [bq_bandpass(2800, 0.8)]) * np.sin(np.pi * _t(_n(1.4)) / 1.4) ** 2
    place(x, air / (np.abs(air).max() + 1e-9), 0.1, 0.12)
    return x


def cord_lift(g) -> np.ndarray:
    x = buf(2.6)
    for k in range(9):                                                    # pale threads drawn up
        f = 440.0 * 2 ** (k * 4 / 12 / 2)
        place(x, tap(g, [f, f * 2.01, f * 3.02], [0.25, 0.15, 0.08], 0.6, click=0.3), 0.08 * k)
    place(x, _glass_sweep(g, 1760.0, 3520.0, 5, 0.6, 0.3), 0.3)          # the knots loosing their light
    place(x, glass_ring(g, 880.0, 1.6, 0.35), 0.8)                         # a soft holy bell
    place(x, glass_ring(g, 1320.0, 1.4, 0.2), 0.82)
    return x


SKILLS += [("nhoa_echo", nhoa_echo, CAST), ("cord_lift", cord_lift, CAST)]   # appended: earlier seeds stay


def _ticks(g, count: int, gap: float, amp: float) -> np.ndarray:
    x = buf(count * gap + 0.3)
    for k in range(count):                                                 # leg tips on metal
        f = float(g.uniform(2600, 3400))
        place(x, tap(g, [f, f * 1.7, f * 2.9], [0.012, 0.008, 0.004], amp, click=0.6), k * gap * float(g.uniform(0.8, 1.2)))
    return x


def _bound_hum(sec: float, f0: float, rise: float) -> np.ndarray:
    t = _t(_n(sec))
    env = np.clip(t / rise, 0, 1) ** 1.5 * np.clip((sec - t) / 0.3, 0, 1)
    return sum(a * np.sin(2 * np.pi * f0 * k * t) for k, a in ((1, 1.0), (2, 0.45), (3, 0.2))) * env


def crawler_mend(g) -> np.ndarray:
    x = buf(1.8)
    place(x, _ticks(g, 7, 0.06, 0.6), 0.0)                                 # the scuttle to the leg
    spark = noise(g, _n(0.25), [bq_highpass(2500, 0.7)]) * (g.random(_n(0.25)) < 0.02)
    place(x, spark * 1.5, 0.45)                                            # a spark catching
    place(x, glass_ring(g, 1560.0, 0.6, 0.35), 0.5)
    place(x, _bound_hum(1.1, 196.0, 0.5) * 0.35, 0.5)                      # the light humming back up
    return x


def crawler_tend(g) -> np.ndarray:
    x = buf(1.3)
    place(x, _ticks(g, 4, 0.14, 0.45), 0.0)
    for k, at in enumerate((0.62, 0.8)):                                   # soft taps on the casing
        place(x, tap(g, [620.0 + 40 * k, 1450.0, 2600.0], [0.04, 0.02, 0.01], 0.5, click=0.2), at)
    place(x, _bound_hum(0.6, 196.0, 0.15) * 0.12, 0.65)
    return x


SKILLS += [("crawler_mend", crawler_mend, CAST), ("crawler_tend", crawler_tend, CAST)]   # appended
PHASES: list[tuple[str, object, float]] = [("close_circle", close_circle, CAST)]
FILES = [f"skill_{name}.ogg" for name, _, _ in SKILLS] + [f"phase_{name}.ogg" for name, _, _ in PHASES]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    jobs = [("skill", i, j) for i, j in enumerate(SKILLS)] + [("phase", 50 + i, j) for i, j in enumerate(PHASES)]
    for kind, i, (name, fn, tgt) in jobs:
        seed = SEED + 100 * i
        x = finish(room(fn(rng(seed)), seed + 7, mix=0.12, tail=0.4, rt60=0.9), tgt)
        write_ogg(os.path.join(out_dir, f"{kind}_{name}.ogg"), x, quality=QUALITY)
        res[f"{kind}_{name}"] = m = measure(x)
        if verbose:
            print(f"{kind}_{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  TP {m['true_peak_dbtp']:.2f}",
                  flush=True)
    return res


if __name__ == "__main__":
    render()
