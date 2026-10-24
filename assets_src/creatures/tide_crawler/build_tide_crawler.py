"""Tide crawler, Ch8 the seawall (M3-CRE-06): docs/kb/art/creatures/act1/tide_crawler.md.

blender --background --factory-startup --python assets_src/creatures/tide_crawler/build_tide_crawler.py -- \
    --out assets/creatures/tide_crawler/tide_crawler.glb

The Undertow's foot soldier at Corrow: a grotesque echo of a shore crab (bible: grotesque echoes of sea animals). A
wet black lacquer carapace split by glimmer wounds, too many legs (six a side) arching higher than the body, and two
long striking forelegs. Built for waves of them on the Fisher Stair, so it is cheap.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 8101
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "storm_slate": "#3E4A57",
}.items()}

BODY = np.array([0.0, 0.42, 0.0])
NLEG = 6


def leg_pts(side: float, i: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = 0.25 - i * 0.1
    hip = BODY + np.array([side * 0.2, -0.04, z])
    knee = np.array([side * 0.5, 0.72 - 0.02 * i, z * 1.4])
    tip = np.array([side * 0.72, 0.0, z * 1.9 + 0.02])
    return hip, knee, tip


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("body", BODY - [0, 0, 0.2], BODY + [0, 0, 0.25], "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(NLEG):
            hip, knee, tip = leg_pts(s, i)
            rig.add(f"leg_{tag}{i}_a", hip, knee, "body")
            rig.add(f"leg_{tag}{i}_b", knee, tip, f"leg_{tag}{i}_a")
        rig.add(f"strike_{tag}", BODY + [s * 0.1, 0.0, 0.25], BODY + [s * 0.2, 0.3, 0.6], "body")
        rig.add(f"strike_{tag}_b", BODY + [s * 0.2, 0.3, 0.6], BODY + [s * 0.18, -0.1, 0.95], f"strike_{tag}")
    return rig


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    P, T = ck.ellipsoid(BODY, (0.3, 0.17, 0.36), 10, 18)
    n = ck.fbm(P * 7.0, SEED)
    wound = ck.smoothstep(0.92, 1.0, np.abs(np.sin((P[:, 0] * 1.3 + P[:, 2]) * 18.0 + n * 3.0))) * ck.smoothstep(
        BODY[1] - 0.02, BODY[1] + 0.08, P[:, 1])
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, n)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, wound[:, None])
    ck.finish(mesh, P, T, "carapace", col, rig.rigid("body"), wet=1.0, cavity=0.2, emission=wound)
    for s in (-1.0, 1.0):
        for k in range(3):  # a cluster of small glowing eyes
            Pe, Te = ck.ellipsoid(BODY + np.array([s * (0.05 + 0.04 * k), 0.12 - 0.02 * k, 0.32 - 0.02 * k]),
                                  (0.018,) * 3, 4, 6)
            ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid("body"), wet=1.0, emission=1.0)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(NLEG):
            hip, knee, tip = leg_pts(s, i)
            for seg, p0, p1, r0, r1 in (("a", hip, knee, 0.03, 0.024), ("b", knee, tip, 0.022, 0.004)):
                mid = (p0 + p1) / 2 + np.array([s * 0.04, 0.04 if seg == "a" else 0.0, 0.0])
                P, T = ck.tube(ck.bezier([p0, mid, p1], 6), np.linspace(r0, r1, 6), 6)
                ck.finish(mesh, P, T, "carapace", ck.mix(PAL["lacquer_black"], PAL["storm_slate"], 0.2),
                          rig.rigid(f"leg_{tag}{i}_{seg}"), wet=1.0)
        for seg in ("", "_b"):
            b = rig.bones[rig.index(f"strike_{tag}{seg}")]
            P, T = ck.tube(ck.bezier([b.head, b.tail], 6), np.linspace(0.04, 0.012 if seg else 0.03, 6), 7)
            ck.finish(mesh, P, T, "carapace", PAL["lacquer_black"], rig.rigid(f"strike_{tag}{seg}"), wet=1.0)


def build_clips() -> list[ck.Clip]:
    legs_ = [(f"leg_{t}{i}", 1.0 if t == "l" else -1.0, i) for t in "lr" for i in range(NLEG)]
    idle = ck.Clip("idle", 1.6, loop=True)  # legs tapping out of rhythm
    for b, s, i in legs_:
        idle.wave(f"{b}_a", amp_rot=(0, 0, 6.0 * s), cycles=2, phase=i * 1.7 + (0.9 if s < 0 else 0.0), steps=6)
    idle.wave("body", amp_loc=(0, 0.015, 0), amp_rot=(2.0, 0, 1.5), cycles=1)
    attack = ck.Clip("attack", 1.0)  # it rears and strikes with both forelegs
    for t, rear, strike in ((0.0, 0, 0), (0.35, 1.0, -1.0), (0.55, -0.3, 1.0), (0.7, 0.0, 0.8), (1.0, 0, 0)):
        attack.key("body", t, (-20.0 * rear, 0, 0), (0, 0.1 * rear, 0.1 * max(strike, 0)))
        for tag in ("l", "r"):
            attack.key(f"strike_{tag}", t, (-40.0 * strike, 0, 0))
            attack.key(f"strike_{tag}_b", t, (35.0 * max(strike, 0), 0, 0))
    cast = ck.Clip("cast", 1.2)  # the wounds pulse (the material); the body heaves
    for t, s in ((0.0, 0.0), (0.4, 1.0), (0.8, 0.6), (1.2, 0.0)):
        cast.key("body", t, (6.0 * s, 0, 0), (0, 0.06 * s, 0))
    hit = ck.Clip("hit", 0.45)  # it skitters back
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.45, 0.0)):
        hit.key("root", t, (0, 0, 0), (0, 0, -0.15 * s))
        hit.key("body", t, (10.0 * s, 0, 0))
    ko = ck.Clip("ko", 1.3)  # the legs give, it collapses
    for t, s in ((0.0, 0.0), (0.4, 0.5), (0.9, 1.0), (1.3, 1.0)):
        ko.key("body", t, (0, 0, 6.0 * s), (0, -0.3 * s, 0))
        for b, sd, i in legs_:
            ko.key(f"{b}_a", t, (0, 0, -18.0 * s * sd))
            ko.key(f"{b}_b", t, (0, 0, -40.0 * s * sd))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("tide_crawler")
    body(mesh, rig)
    legs(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "tide_crawler"})
    print(f"tide_crawler: {info}")


if __name__ == "__main__":
    main()
