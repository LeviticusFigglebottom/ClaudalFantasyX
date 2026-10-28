"""Sail leech, Ch4 the drifting trader (M3-CRE-03): docs/kb/art/creatures/act1/sail_leech.md.

blender --background --factory-startup --python assets_src/creatures/sail_leech/build_sail_leech.py -- \
    --out assets/creatures/sail_leech/sail_leech.glb

Undertow-spawn shaped like a ray that clings to wet canvas: a 1.4 m flexible diamond of wet black carapace, its edge a
frill that ripples like a sail, glowing wound slits along its back, a whip tail and two small glowing eyes. It hangs in
the air (its origin is the hover point: the battle spec's `hover` lifts it).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 4613
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "spawn_wound": "#3FE0C8",
    "deep_teal_shadow": "#0E4A55",
}.items()}

HALF_W = 0.7
HALF_L = 0.5
WING = 3  # bones per wing
# A variant's parameters (the fen leech is longer and ribbon-flat, M3-CRE-628); these values are the sail leech's.
THICK = 0.07  # the body's thickness over its middle (the underside is 0.6 of it)
DOME = 0.04  # the back's camber across the span
FRILL = 0.022  # the edge frill's ripple (the sail-like canvas edge)
FRILL_WAVES = 14.0
SLIT_Z = (0.18, 0.11)  # the first wound slit's z and the step back to the next (four slits)
EYE = (0.09, 0.29, 0.38)  # x, y and z of the eyes
TAIL_Z0, TAIL_STEP = -0.3, 0.3  # the tail bones' first joint and their length
TAIL_PATH = ((0, 0.2, -0.3), (0, 0.18, -0.6), (0.05, 0.12, -0.9), (0.0, 0.1, -1.2))  # the tail's curve
TAIL_R = (0.04, 0.006)  # its radius at the root and the tip
TAIL_CHAIN = ((0, 0.2, -0.3), (0, 0.2, -0.6), (0, 0.2, -0.9), (0, 0.2, -1.2))  # the tail's skinning spans


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("body", (0, 0.2, -0.15), (0, 0.2, 0.25), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for k in range(WING):
            x0, x1 = s * (0.12 + k * 0.19), s * (0.12 + (k + 1) * 0.19)
            rig.add(f"wing_{tag}{k}", (x0, 0.2, 0.0), (x1, 0.2, 0.0), "body" if k == 0 else f"wing_{tag}{k - 1}")
    for k in range(3):
        rig.add(f"tail{k}", (0, 0.2, TAIL_Z0 - k * TAIL_STEP), (0, 0.2, (TAIL_Z0 - TAIL_STEP) - k * TAIL_STEP),
                "body" if k == 0 else f"tail{k - 1}")
    return rig


def _skin(rig: ck.Rig):
    left = rig.chain([f"wing_l{k}" for k in range(WING)], [(0.12 + k * 0.19, 0.2, 0.0) for k in range(WING + 1)])
    right = rig.chain([f"wing_r{k}" for k in range(WING)], [(-0.12 - k * 0.19, 0.2, 0.0) for k in range(WING + 1)])
    body = rig.index("body")

    def f(P):
        Jl, Wl = left(P)
        Jr, Wr = right(P)
        n = len(P)
        J = np.zeros((n, 2), dtype=np.int64)
        W = np.zeros((n, 2))
        ax = np.abs(P[:, 0])
        for v in range(n):
            if ax[v] < 0.12:
                w = float(ck.smoothstep(0.04, 0.12, ax[v]))
                side = Jl[v, 0] if P[v, 0] >= 0 else Jr[v, 0]
                J[v] = (body, side)
                W[v] = (1.0 - w, w)
            elif P[v, 0] >= 0:
                J[v], W[v] = Jl[v], Wl[v]
            else:
                J[v], W[v] = Jr[v], Wr[v]
        return J, W

    return f


def outline(a: np.ndarray) -> np.ndarray:
    """The ray's outline at angle a (0 = +x wing tip, pi/2 = nose): a diamond with swept, rounded wings."""
    cu, cv = np.cos(a), np.sin(a)
    t = 1.0 / (np.abs(cu) ** 1.6 + (np.abs(cv) * 0.85) ** 1.6) ** (1.0 / 1.6)
    uu, vv = cu * t, cv * t
    x = uu * HALF_W * (1.0 - 0.25 * np.abs(vv))
    z = vv * HALF_L + 0.12 * (1.0 - np.abs(uu)) * (vv > 0) - 0.08 * np.abs(uu) ** 2
    return np.column_stack([x, np.zeros_like(x), z])


def wing_body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    segs, rings = 96, 14
    ang = np.linspace(0, 2 * math.pi, segs, endpoint=False)
    edge = outline(ang)
    skin = _skin(rig)
    for top in (True, False):
        pts = []
        for k in range(rings + 1):
            r = k / rings
            ring = edge * r
            frill = FRILL * np.sin(ang * FRILL_WAVES) * ck.smoothstep(0.75, 1.0, r)
            dome = DOME * (1.0 - (ring[:, 0] / HALF_W) ** 2)
            thick = (THICK * np.sqrt(max(1.0 - r, 0.0)) + 0.004) * (1.0 if top else -0.6)
            ring[:, 1] = 0.2 + dome + frill + thick
            pts.append(ring)
        P = np.vstack(pts)
        P[:segs, 0] = 0.0
        P[:segs, 2] = 0.0
        T = ck.grid_tris(rings + 1, segs, True)
        fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
        want = 1.0 if top else -1.0
        if float((fn[:, 1] * want).sum()) < 0:
            T = ck.flip(T)
        n = ck.fbm(P * 6.0, SEED + (0 if top else 1))
        slits = np.zeros(len(P))
        if top:
            for k in range(4):
                zc = SLIT_Z[0] - k * SLIT_Z[1]
                slits = np.maximum(slits, np.exp(-((P[:, 2] - zc) / 0.014) ** 2) * ck.smoothstep(0.34, 0.1, np.abs(P[:, 0])))
            col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, n)[:, None])
        else:
            col = np.tile(ck.mix(PAL["storm_slate"], PAL["deep_teal_shadow"], 0.4), (len(P), 1))
        col = ck.mix(col, PAL["spawn_wound"] * 0.55, slits[:, None])
        ck.finish(mesh, P, T, "carapace", col, skin, wet=1.0, cavity=0.2 * (1 - slits), emission=slits)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid((s * EYE[0], EYE[1], EYE[2]), (0.025, 0.02, 0.025), 5, 8)
        ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid("body"), wet=1.0, emission=1.0)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier(list(TAIL_PATH), 16)
    P, T = ck.tube(path, np.linspace(TAIL_R[0], TAIL_R[1], 16), 6)
    skin = rig.chain(["tail0", "tail1", "tail2"], list(TAIL_CHAIN))
    ck.finish(mesh, P, T, "carapace", PAL["lacquer_black"], skin, wet=1.0)


def build_mesh(rig: ck.Rig, name: str = "sail_leech") -> ck.Mesh:
    mesh = ck.Mesh(name)
    wing_body(mesh, rig)
    tail(mesh, rig)
    return mesh


def build_clips() -> list[ck.Clip]:
    wings = [(f"wing_{t}{k}", 1.0 if t == "l" else -1.0, k) for t in "lr" for k in range(WING)]
    idle = ck.Clip("idle", 2.4, loop=True)
    for b, s, k in wings:
        idle.wave(b, amp_rot=(0.0, 0.0, 9.0 * s), cycles=1, phase=-k * 0.9)
    idle.wave("body", amp_loc=(0.0, 0.05, 0.0), cycles=1, phase=math.pi)
    for k in range(3):
        idle.wave(f"tail{k}", amp_rot=(0.0, 12.0, 0.0), cycles=1, phase=-k * 0.8)

    attack = ck.Clip("attack", 1.3)  # it drops and wraps: the wings fold down over the target
    for t, drop, fold, fwd in ((0.0, 0, 0, 0), (0.45, 0.15, -0.3, 0), (0.7, -0.7, 1.0, 0.5), (0.9, -0.7, 1.0, 0.5),
                                (1.3, 0, 0, 0)):
        attack.key("root", t, (0, 0, 0), (0, drop, fwd))
        for b, s, k in wings:
            attack.key(b, t, (0, 0, -24.0 * fold * s))
    cast = ck.Clip("cast", 1.4)  # it spreads flat and shudders
    for i, t in enumerate(np.linspace(0, 1.4, 15)):
        shud = (0.0 if i in (0, 14) else (3.0 if i % 2 else -3.0))
        env = math.sin(math.pi * t / 1.4)
        for b, s, k in wings:
            cast.key(b, float(t), (shud * env, 0, 6.0 * env * s))
    hit = ck.Clip("hit", 0.5)
    for t, c in ((0.0, 0.0), (0.12, 1.0), (0.5, 0.0)):
        hit.key("root", t, (10.0 * c, 0, 0), (0, -0.1 * c, -0.1 * c))
        for b, s, k in wings:
            hit.key(b, t, (0, 0, -18.0 * c * s))
    ko = ck.Clip("ko", 1.6)  # it falls like a wet sheet to the deck (the hover is about 1.4 m)
    for t, drop, fold in ((0.0, 0, 0), (0.4, 0.2, 0.5), (1.0, 1.25, -0.4), (1.3, 1.36, 0.2), (1.6, 1.38, 0.0)):
        ko.key("root", t, (8.0 * min(t, 1.0), 0, 0), (0, -drop, 0))
        for b, s, k in wings:
            ko.key(b, t, (0, 0, -20.0 * fold * s))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "sail_leech"})
    print(f"sail_leech: {info}")


if __name__ == "__main__":
    main()
