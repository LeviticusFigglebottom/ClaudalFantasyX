"""What a blow lands on, and what a guard braces with (M3-AUD-864, the Act I foley detail pass: "battle hit and guard
sounds per enemy material"). ChoreoAudio (choreo_sfx.json) plays the attacker's weapon accent on a blow's contact and
BattleVfx the element hit; until now nothing said what was struck, so a hook on a crab's shell and on an eel's flank
sounded alike. Now a landed blow adds the struck material's layer (choreo_sfx.json `materials` / `struck`), and a
bracing enemy its own (`guards`). Liss's launcher gets its accent (she fell back to the creatures' claw).

    struck_shell_1..2    a hard carapace: a dry knock with a hollow ring under it (the reef crabs, the hermit, limpets)
    struck_soft_1..2     wet, yielding flesh: a dull slap and a squelch (eels, leeches, slugs, skippers, polyps, hounds)
    struck_feather_1..2  feathers and wings: a muffled pat and a ruffle (the gulls, the ashwing, the flue moths)
    struck_wood_1..2     waterlogged timber: a hollow, damp knock (the spar wraith)
    struck_stone_1..2    stone and slag crust: a hard, gritty crack (the slag tortoise, the cinder matron's crust)
    struck_metal_1..2    bronze, brass and armour: a struck plate's short ring (the drownbell, the inquisitor, sparkers)
    struck_spawn_1..2    the Undertow's spawn, water held in a shape: a blow that sinks into it, a gulp and a hiss
    guard_shell          a shell drawn in and clamped shut (brace)
    guard_stone          plates of slag grinding shut (brace)
    accent_launcher_1..3 Liss's launcher: the bolt's thunk home and the reel's ratchet (her Reel Shot)

Synthesized here and in tools/audio/synth/ (SPEC §2, §9). Mono, q4, plain git under assets/audio/sfx/choreo/ (ADR
0174): the struck layers at -22 LUFS momentary max (under the hit), guards and accents at -21 (the accents' rule).

Render:  python3 tools/audio/render_all.py --only act1_struck_sfx
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
from creature_sfx import buf, burst, crackle, gurgle, room, slosh, tap, thump  # noqa: E402
from field_ambience import stick_slip  # noqa: E402
from synth.dsp import bq_bandpass, bq_highpass, bq_lowpass, rng  # noqa: E402
from synth.mixer import measure, normalize_momentary, write_ogg  # noqa: E402
from underwater_sfx import place  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "sfx", "choreo")
SEED = 20262900
STRUCK, GUARD, ACCENT = -22.0, -21.0, -21.0


def struck_shell(g, v):
    x = buf(0.6)
    place(x, tap(g, [float(g.uniform(1400, 1800)), 3300.0, 5200.0], [0.03, 0.015, 0.008], 1.0, 0.9), 0.0)
    place(x, tap(g, [float(g.uniform(380, 460)), 950.0], [0.08, 0.04], 0.6, 0.3), 0.003)   # the hollow under it
    return x


def struck_soft(g, v):
    x = buf(0.6)
    place(x, burst(g, 0.06, [bq_lowpass(900, 0.7), bq_highpass(90, 0.7)], 0.002, 0.03), 0.0)
    place(x, gurgle(g, 0.18, 30, 0.004, 0.01, 0.5), 0.02)
    place(x, thump(g, 120 + 20 * v, 70, 0.04, 0.2, 0.2), 0.0, 0.5)
    return x


def struck_feather(g, v):
    x = buf(0.5)
    place(x, burst(g, 0.05, [bq_bandpass(700, 0.8), bq_lowpass(2500, 0.7)], 0.002, 0.02), 0.0)
    place(x, A2.Ray.wing(g, 2, 22.0 + 4 * v, 0.4, 0.6), 0.02)          # a ruffle
    return x


def struck_wood(g, v):
    x = buf(0.6)
    place(x, tap(g, [float(g.uniform(170, 220)), 430.0, 990.0], [0.07, 0.04, 0.02], 1.0, 0.6), 0.0)
    place(x, burst(g, 0.05, [bq_bandpass(600, 0.9)], 0.001, 0.02), 0.0, 0.3)   # damp
    return x


def struck_stone(g, v):
    x = buf(0.6)
    place(x, burst(g, 0.04, [bq_bandpass(1900, 0.8)], 0.001, 0.012), 0.0, 0.5)
    place(x, tap(g, [float(g.uniform(700, 900)), 1900.0, 3500.0], [0.05, 0.025, 0.012], 0.9, 0.5), 0.0)
    place(x, crackle(g, 0.2, 120, 2500, 0.8, 0.05), 0.01, 0.15)     # grit, under the knock so its peaks don't cap it
    return x


def struck_metal(g, v):
    x = buf(0.8)
    place(x, A2.clang(g, 0.9 + 0.1 * v, 0.7, 0.5), 0.0)
    return x


def struck_spawn(g, v):
    x = buf(0.7)
    place(x, thump(g, 90, 40, 0.08, 0.1, 0.4), 0.0, 0.7)            # it sinks into it
    place(x, slosh(g, 0.35, 0.6, 4.0), 0.0)
    hiss = burst(g, 0.3, [bq_bandpass(2600, 0.8)], 0.02, 0.12)
    place(x, hiss, 0.05, 0.25)
    return x


def guard_shell(g):
    x = buf(0.8)
    place(x, A2.whoosh(g, 0.2, 900, 400, 0.4), 0.0)                  # drawn in
    place(x, tap(g, [1500.0, 3200.0, 5100.0], [0.03, 0.015, 0.008], 0.9, 0.9), 0.18)
    place(x, tap(g, [1700.0, 3500.0], [0.025, 0.012], 0.7, 0.9), 0.21)   # clamped shut
    return x


def guard_stone(g):
    x = buf(1.0)
    place(x, stick_slip(g, 0.45, 10.0, 25.0, [(220.0, 1.0), (520.0, 0.5), (1100.0, 0.2)], q=3.0), 0.0, 0.8)
    place(x, thump(g, 140, 70, 0.06, 0.6, 0.3), 0.45, 0.8)           # plates grinding shut
    return x


def accent_launcher(g, v):
    x = buf(0.6)
    place(x, thump(g, 260, 130, 0.03, 0.9, 0.2), 0.0)               # the bolt's thunk home
    place(x, A2.Engine.ratchet(g, 0.18, 26 + 4 * v, 18, 0.5), 0.05)  # the reel
    return x


MATERIALS = ("shell", "soft", "feather", "wood", "stone", "metal", "spawn")
JOBS: list[tuple[str, object, float]] = (
    [(f"struck_{m}_{v}", (lambda fn, v: lambda g: fn(g, v))(globals()[f"struck_{m}"], v), STRUCK)
     for m in MATERIALS for v in (1, 2)]
    + [("guard_shell", guard_shell, GUARD), ("guard_stone", guard_stone, GUARD)]
    + [(f"accent_launcher_{v}", (lambda v: lambda g: accent_launcher(g, v))(v), ACCENT) for v in (1, 2, 3)]
)
FILES = [f"{name}.ogg" for name, _, _ in JOBS]


def render(out_dir: str = OUT_DIR, verbose: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    for i, (name, fn, tgt) in enumerate(JOBS):
        seed = SEED + 100 * i
        x = normalize_momentary(room(fn(rng(seed)), seed + 7, mix=0.1, tail=0.3, rt60=0.7), tgt, ceiling_db=-3.0)
        write_ogg(os.path.join(out_dir, name + ".ogg"), x, quality=4.0)
        res[name] = m = measure(x)
        if verbose:
            print(f"{name}: {m['seconds']:.2f}s  Mmax {m['momentary_max_lufs']:.2f}  TP {m['true_peak_dbtp']:.2f}")
    return res


if __name__ == "__main__":
    render()
