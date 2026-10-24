"""Ashwing, Ch5 Pemakar terraces (M3-CRE-04): docs/kb/art/creatures/act1/ashwing.md.

blender --background --factory-startup --python assets_src/creatures/ashwing/build_ashwing.py -- \
    --out assets/creatures/ashwing/ashwing.glb

A broad grey moth of the ash terraces, drawn to the Lanternfall boats' lights: rounded fore- and hindwings 1.6 m
across held flat, two pale eye-spots that read as faces, a furred body, feathered antennae. Its origin is its hover
point (the battle spec's `hover` lifts it).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 5101
PAL = {k: ck.hexrgb(v) for k, v in {
    "overcast_slate": "#6F7E8E", "storm_slate": "#3E4A57", "bone": "#E6DAC0", "timber_weathered": "#7E6A55",
    "lacquer_black": "#1D1916", "spawn_wound": "#3FE0C8", "sand_cloth": "#C9B48E", "coral_stone_weathered": "#B9AE98",
}.items()}

BODY_Y = 0.2


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("thorax", (0, BODY_Y, -0.05), (0, BODY_Y, 0.12), "root")
    rig.add("abdomen", (0, BODY_Y, -0.05), (0, BODY_Y - 0.03, -0.38), "thorax")
    rig.add("head", (0, BODY_Y, 0.12), (0, BODY_Y + 0.01, 0.2), "thorax")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"fore_{tag}", (s * 0.06, BODY_Y + 0.03, 0.06), (s * 0.8, BODY_Y + 0.03, 0.1), "thorax")
        rig.add(f"hind_{tag}", (s * 0.06, BODY_Y + 0.02, -0.04), (s * 0.6, BODY_Y + 0.02, -0.25), "thorax")
        rig.add(f"ant_{tag}", (s * 0.03, BODY_Y + 0.04, 0.19), (s * 0.12, BODY_Y + 0.14, 0.38), "head")
    return rig


def wing(mesh: ck.Mesh, rig: ck.Rig, side: float, tag: str, fore: bool) -> None:
    """A rounded wing membrane fanned from its root: polar rings around the root, with a front and a back margin."""
    root = np.array([side * 0.06, BODY_Y + (0.035 if fore else 0.025), 0.06 if fore else -0.04])
    span = 0.8 if fore else 0.6
    a0, a1 = (math.radians(-35), math.radians(25)) if fore else (math.radians(-80), math.radians(-20))
    na, nr = 22, 10
    angs = np.linspace(a0, a1, na)
    pts = []
    for k in range(nr + 1):
        r = k / nr
        ring = []
        for a in angs:
            m = math.sin((a - a0) / (a1 - a0) * math.pi) ** 0.5  # the margin rounds off at both edges
            rr = span * r * (0.35 + 0.65 * m)
            x = side * rr * math.cos(a)
            z = rr * math.sin(a) * (1.0 if fore else 1.2)
            y = 0.02 * math.sin(r * math.pi) - 0.04 * r * r
            ring.append(root + np.array([x, y, z]))
        pts.append(np.asarray(ring))
    P = np.vstack(pts)
    T = ck.grid_tris(nr + 1, na, False)
    # eye-spots: a pale ring with a dark pupil (and a spawn_wound speck in the forewing pupils)
    spot_c = root + np.array([side * span * 0.55, 0.0, (0.05 if fore else -0.2)])
    d = np.linalg.norm((P - spot_c)[:, [0, 2]], axis=1)
    ring = np.exp(-((d - 0.12) / 0.03) ** 2)
    pupil = ck.smoothstep(0.08, 0.04, d)
    speck = ck.smoothstep(0.018, 0.006, d) if fore else np.zeros(len(P))
    n = ck.fbm(P * 9.0, SEED + (1 if fore else 2))
    veins = ck.smoothstep(0.92, 1.0, np.abs(np.sin(np.arctan2(P[:, 2] - root[2], (P[:, 0] - root[0]) * side) * 9.0)))
    rr = np.linalg.norm((P - root)[:, [0, 2]], axis=1) / span
    col = ck.mix(PAL["storm_slate"], PAL["overcast_slate"] * 0.8, (0.3 + 0.4 * n)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 0.7, (0.6 * ck.smoothstep(0.8, 1.0, rr))[:, None])
    col = ck.mix(col, PAL["coral_stone_weathered"], (0.25 * ck.smoothstep(0.1, 0.5, n))[:, None])
    col = col * (1.0 - 0.25 * veins)[:, None]
    col = ck.mix(col, PAL["bone"], ring[:, None])
    col = ck.mix(col, PAL["lacquer_black"], pupil[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, speck[:, None])
    bone = rig.rigid(f"{'fore' if fore else 'hind'}_{tag}")
    for up in (True, False):
        Tw = T if up else ck.flip(T)
        fn = np.cross(P[Tw[:, 1]] - P[Tw[:, 0]], P[Tw[:, 2]] - P[Tw[:, 0]])
        if (fn[:, 1].sum() < 0) == up:
            Tw = ck.flip(Tw)
        off = np.array([0.0, 0.002 if up else -0.002, 0.0])
        ck.finish(mesh, P + off, Tw, "wing", col if up else col * 0.85, bone, cavity=0.3 * veins, emission=speck)


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier([(0, BODY_Y - 0.03, -0.4), (0, BODY_Y, -0.15), (0, BODY_Y + 0.01, 0.05), (0, BODY_Y, 0.2)], 18)
    u = np.linspace(0, 1, 18)
    rad = 0.075 * np.sin(np.clip(u, 0.05, 0.97) * math.pi) ** 0.5 * (1.0 + 0.3 * ck.smoothstep(0.6, 0.75, u))
    P, T = ck.tube(path, rad, 12)
    bands = 0.5 + 0.5 * np.sin(np.linspace(0, 1, 18) * 30.0)
    b = np.concatenate([np.repeat(bands, 12), [bands[0], bands[-1]]])[: len(P)]
    col = ck.mix(PAL["timber_weathered"], PAL["sand_cloth"], (0.4 * b)[:, None])
    skin = rig.chain(["abdomen", "thorax", "head"], [(0, BODY_Y, -0.4), (0, BODY_Y, -0.05), (0, BODY_Y, 0.12),
                                                     (0, BODY_Y, 0.2)])
    ck.finish(mesh, P, T, "fur", col, skin, cavity=0.3 * (1 - b))
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid((s * 0.045, BODY_Y + 0.01, 0.17), (0.028, 0.028, 0.028), 6, 8)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid("head"), wet=1.0)


def antennae(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for tag in ("l", "r"):
        a = rig.bones[rig.index(f"ant_{tag}")]
        h0, h1 = np.asarray(a.head), np.asarray(a.tail)
        path = ck.bezier([h0, h0 + (h1 - h0) * 0.6 + np.array([0, 0.03, 0]), h1], 8)
        P, T = ck.tube(path, np.linspace(0.006, 0.003, 8), 4)
        ck.finish(mesh, P, T, "fur", PAL["sand_cloth"] * 0.8, rig.rigid(f"ant_{tag}"))
        for k in range(1, 7):  # feather barbs
            c = path[k]
            for side in (-1.0, 1.0):
                tip = c + np.array([side * 0.025, 0.01, -0.01])
                Pb = np.array([c, tip, c + np.array([0, 0.003, 0.004])])
                ck.finish(mesh, Pb, np.array([[0, 1, 2], [0, 2, 1]]), "fur", PAL["sand_cloth"] * 0.7,
                          rig.rigid(f"ant_{tag}"))


def build_clips() -> list[ck.Clip]:
    wings = [("fore_l", 1.0), ("hind_l", 1.0), ("fore_r", -1.0), ("hind_r", -1.0)]
    idle = ck.Clip("idle", 1.8, loop=True)
    for t, flap in ((0.0, 0.0), (0.3, 1.0), (0.6, -0.6), (0.9, 0.0), (1.8, 0.0)):
        for b, s in wings:
            idle.key(b, t, (0, 0, 32.0 * flap * s))
    idle.wave("root", amp_loc=(0.0, 0.05, 0.0), cycles=1, phase=math.pi / 2)
    idle.wave("ant_l", amp_rot=(6.0, 0, 0), cycles=1)
    idle.wave("ant_r", amp_rot=(6.0, 0, 0), cycles=1, phase=0.6)
    idle.wave("abdomen", amp_rot=(4.0, 0, 0), cycles=1, phase=1.0)

    attack = ck.Clip("attack", 1.2)  # a buffet: it lunges and claps its wings at the target
    for t, flap, fwd in ((0.0, 0.0, 0.0), (0.4, -0.8, -0.1), (0.6, 1.4, 0.45), (0.75, 1.2, 0.45), (1.2, 0.0, 0.0)):
        attack.key("root", t, (8.0 * max(flap, 0), 0, 0), (0, 0.05 * flap, fwd))
        for b, s in wings:
            attack.key(b, t, (0, 0, 40.0 * flap * s))

    cast = ck.Clip("cast", 1.6)  # it hovers and shakes the ash from its wings (the VFX dust)
    for i, t in enumerate(np.linspace(0, 1.6, 17)):
        env = math.sin(math.pi * t / 1.6)
        sh = (1.0 if i % 2 else -1.0) * env if 0 < i < 16 else 0.0
        for b, s in wings:
            cast.key(b, float(t), (0, 0, (14.0 * sh + 10.0 * env) * s))
        cast.key("root", float(t), (-10.0 * env, 0, 0), (0, 0.08 * env, 0))

    hit = ck.Clip("hit", 0.6)  # it tumbles
    for t, s in ((0.0, 0.0), (0.15, 1.0), (0.6, 0.0)):
        hit.key("root", t, (0, 0, 28.0 * s), (0, -0.15 * s, -0.08 * s))
        for b, sd in wings:
            hit.key(b, t, (0, 0, -15.0 * s * sd))

    ko = ck.Clip("ko", 1.8)  # it spirals down, wings closing, and lies on its side (hover ~1.4 m)
    for t, d, spin in ((0.0, 0.0, 0.0), (0.6, 0.35, 120.0), (1.2, 1.1, 260.0), (1.5, 1.36, 330.0), (1.8, 1.38, 340.0)):
        ko.key("root", t, (0, spin, 60.0 * min(d, 1.0)), (0, -d, 0))
        for b, s in wings:
            ko.key(b, t, (0, 0, -55.0 * min(d, 1.0) * s))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("ashwing")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        wing(mesh, rig, s, tag, True)
        wing(mesh, rig, s, tag, False)
    body(mesh, rig)
    antennae(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "ashwing"})
    print(f"ashwing: {info}")


if __name__ == "__main__":
    main()
