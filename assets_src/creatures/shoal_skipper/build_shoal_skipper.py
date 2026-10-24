"""Shoal skipper, Ch6 Brine Shoals (M3-CRE-05): docs/kb/art/creatures/act1/shoal_skipper.md.

blender --background --factory-startup --python assets_src/creatures/shoal_skipper/build_shoal_skipper.py -- \
    --out assets/creatures/shoal_skipper/shoal_skipper.glb

A mudskipper grown to a dog's size on the Brine Shoals' flats: a bulbous head with eyes on top, propped on its front
fins, a tall spined dorsal fin edged deep red, mottled skin crusted with dried salt, a spawn_wound gill.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6101
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_wet": "#B59D74", "foliage_shadow": "#1E4A3A", "mortar_white": "#E6E1D6", "lacquer_red_deep": "#7A1712",
    "spawn_wound": "#3FE0C8", "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E", "sand_dry": "#EFDDB4",
}.items()}

N = 5


def spine(n: int) -> np.ndarray:
    return ck.bezier([(0, 0.3, 0.42), (0, 0.32, 0.15), (0, 0.22, -0.2), (0, 0.08, -0.5)], n)


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    j = spine(N + 1)
    for i in range(N):
        rig.add(f"spine{i}", j[i], j[i + 1], "root" if i == 0 else f"spine{i - 1}")
    rig.add("jaw", j[0] + np.array([0, -0.08, -0.05]), j[0] + np.array([0, -0.1, 0.12]), "spine0")
    rig.add("dorsal", j[1] + np.array([0, 0.12, 0]), j[3] + np.array([0, 0.2, 0]), "spine1")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"fin_{tag}", j[1] + np.array([s * 0.12, -0.1, 0.05]), np.array([s * 0.28, 0.0, 0.3]), "spine1")
        rig.add(f"eye_{tag}", j[0] + np.array([s * 0.07, 0.12, -0.08]), j[0] + np.array([s * 0.08, 0.2, -0.06]),
                "spine0")
    return rig, j


def body(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    n = 30
    path = spine(n)
    u = np.linspace(0, 1, n)
    rad = 0.17 * (1.0 - u) ** 0.5 * np.sin(np.clip(u, 0.05, 1.0) * math.pi * 0.55 + 0.6) + 0.015
    P, T = ck.tube(path, rad, 14, squash=1.0)
    mott = ck.fbm(P * 10.0, SEED)
    col = ck.mix(PAL["sand_wet"], PAL["foliage_shadow"], ck.smoothstep(0.0, 0.4, mott)[:, None] * 0.7)
    belly = ck.smoothstep(0.2, 0.08, P[:, 1])
    col = ck.mix(col, PAL["sand_dry"] * 0.9, (0.5 * belly)[:, None])
    salt = ck.smoothstep(0.25, 0.45, ck.fbm(P * 6.0, SEED + 1)) * ck.smoothstep(0.15, 0.3, P[:, 1])
    col = ck.mix(col, PAL["mortar_white"], (0.7 * salt)[:, None])
    gill = np.exp(-(((P[:, 2] - 0.2) / 0.03) ** 2)) * ck.smoothstep(0.08, 0.14, np.abs(P[:, 0]))
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, gill[:, None])
    skin = rig.chain([f"spine{i}" for i in range(N)], j)
    ck.finish(mesh, P, T, "skin", col, skin, wet=0.6 * (1 - salt), cavity=0.3 * salt, emission=gill)
    for tag in ("l", "r"):
        e = rig.bones[rig.index(f"eye_{tag}")]
        Pe, Te = ck.ellipsoid(e.tail, (0.05, 0.05, 0.05), 6, 10)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid(f"eye_{tag}"), wet=1.0)
        Ps, Ts = ck.tube(np.array([e.head, e.tail]), 0.035, 8)
        ck.finish(mesh, Ps, Ts, "skin", PAL["sand_wet"], rig.rigid(f"eye_{tag}"), wet=0.5)
    # the lower jaw
    jb = rig.bones[rig.index("jaw")]
    Pj, Tj = ck.ellipsoid((np.asarray(jb.head) + np.asarray(jb.tail)) / 2, (0.12, 0.04, 0.1), 6, 10)
    ck.finish(mesh, Pj, Tj, "skin", PAL["sand_dry"] * 0.85, rig.rigid("jaw"), wet=0.5)


def fins(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    # the dorsal sail: spines with a membrane between them
    base = spine(40)[10:30]
    h = 0.28 * np.sin(np.linspace(0.2, math.pi - 0.3, len(base)))
    top = base + np.column_stack([np.zeros(len(base)), h + 0.12, -0.03 * np.ones(len(base))])
    bot = base + np.array([0, 0.1, 0])
    P = np.vstack([bot, top])
    T = ck.grid_tris(2, len(base), False)
    edge = np.concatenate([np.zeros(len(base)), np.ones(len(base))])
    col = ck.mix(np.tile(PAL["tortoiseshell"], (len(P), 1)), np.tile(PAL["lacquer_red_deep"], (len(P), 1)),
                 (0.3 + 0.7 * edge)[:, None])
    for fl in (False, True):
        ck.finish(mesh, P + np.array([0.004 if fl else -0.004, 0, 0]), ck.flip(T) if fl else T, "fin", col,
                  rig.rigid("dorsal"), wet=0.4, cavity=0.2)
    for k in range(0, len(base), 3):
        Ps, Ts = ck.tube(np.array([bot[k], top[k] + np.array([0, 0.03, 0])]), np.array([0.008, 0.002]), 4)
        ck.finish(mesh, Ps, Ts, "fin", PAL["lacquer_red_deep"], rig.rigid("dorsal"))
    # pectoral fins: the "legs" it props on
    for tag in ("l", "r"):
        b = rig.bones[rig.index(f"fin_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        Pf, Tf = ck.tube(ck.bezier([h0, (h0 + h1) / 2 + np.array([0, 0.03, 0]), h1], 6), np.array(
            [0.05, 0.05, 0.045, 0.04, 0.035, 0.03]), 8, squash=0.45)
        ck.finish(mesh, Pf, Tf, "skin", PAL["sand_wet"] * 0.9, rig.rigid(f"fin_{tag}"), wet=0.6)


def build_clips() -> list[ck.Clip]:
    sp = [f"spine{i}" for i in range(N)]
    idle = ck.Clip("idle", 2.0, loop=True)
    idle.wave("jaw", amp_rot=(-8.0, 0, 0), base_rot=(-8.0, 0, 0), cycles=2)  # gulping
    idle.wave("dorsal", amp_rot=(0, 0, 6.0), cycles=2)
    for i, b in enumerate(sp):
        idle.wave(b, amp_rot=(0, 4.0, 0), cycles=1, phase=-i * 0.7)
    attack = ck.Clip("attack", 1.0)  # a hop-lunge
    for t, h, fwd, curl in ((0.0, 0, 0, 0), (0.3, 0.0, -0.05, 1.0), (0.5, 0.3, 0.35, -0.5), (0.65, 0.05, 0.5, 0),
                            (1.0, 0, 0, 0)):
        attack.key("root", t, (-15.0 * curl, 0, 0), (0, h, fwd))
        for i, b in enumerate(sp[2:], 2):
            attack.key(b, t, (12.0 * curl, 0, 0))
        attack.key("jaw", t, (-25.0 * max(-curl, 0) * 2, 0, 0))
    cast = ck.Clip("cast", 1.3)  # the display: dorsal raised high, fins spread, head up
    for t, s in ((0.0, 0.0), (0.4, 1.0), (0.9, 1.0), (1.3, 0.0)):
        cast.key("dorsal", t, (-20.0 * s, 0, 0), (0, 0.05 * s, 0))
        cast.key("spine0", t, (-15.0 * s, 0, 0))
        cast.key("fin_l", t, (0, 0, 25.0 * s))
        cast.key("fin_r", t, (0, 0, -25.0 * s))
    hit = ck.Clip("hit", 0.5)  # it flips back
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.5, 0.0)):
        hit.key("root", t, (-20.0 * s, 0, 0), (0, 0.08 * s, -0.12 * s))
    ko = ck.Clip("ko", 1.4)  # it flops onto its side
    for t, s in ((0.0, 0.0), (0.4, 0.6), (0.9, 1.0), (1.4, 1.0)):
        ko.key("root", t, (0, 0, 80.0 * s), (-0.1 * s, -0.02 * s, 0))
        ko.key("dorsal", t, (0, 0, -20.0 * s))
        ko.key("jaw", t, (-15.0 * s, 0, 0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, j = build_rig()
    mesh = ck.Mesh("shoal_skipper")
    body(mesh, rig, j)
    fins(mesh, rig, j)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "shoal_skipper"})
    print(f"shoal_skipper: {info}")


if __name__ == "__main__":
    main()
