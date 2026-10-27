"""Corrow after the fall, Ch9's night and dawn (M3-ENV-708 for M3-C09-04; act1_ch09.md §9). Pure numpy.

  shroud_a, shroud_b    the drowned laid out on the strand under sailcloth: a body's shape only, the face covered,
                        the cloth tied at the neck and ankles; b lies a little turned, a fold over the arm
  shroud_small          the same, small
  strand_lamp           an oil lamp on a short stake set in the shingle (its flame emissive; the zone adds the light)
  round_shield          a Stillguard round shield of red lacquer with an iron rim and boss, laid at a man's feet
  ebbing_raft           the Ebbing raft: lacquered timber, poled, a low deck with no rail, a socket for the
                        lantern-staff at its centre, the pole laid along it
  flood_debris          what the flood floats in the low town: planks, a door, a shutter, a basket, a cloth
  milestone             the dawn road's milestone: a laterite post with the distance cut in strokes, a pebble left
                        on top

Origins on the ground (the flood debris on the water), front +Z; the shrouds lie along Z, the head at -Z. The
cut hoist rope coiled on the wall-head is the Haluna kit's `rope_coil` (by kit_dir).
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
from cw_common import kc

M_SHROUD = "cw_sail"
M_LACQUER_RED = "cw_lacquer_red"
M_LACQUER_DARK = "cw_lacquer_dark"
M_FLAME = "cw_lamp_flame"

TRI_BUDGET = {
    "shroud": (2400, 200),
    "strand_lamp": (900, 80),
    "round_shield": (900, 80),
    "ebbing_raft": (5000, 300),
    "flood_debris": (3000, 200),
    "milestone": (1200, 100),
}
BUDGET_KEY = {"shroud_a": "shroud", "shroud_b": "shroud", "shroud_small": "shroud"}


def _form(X, Z, length: float, turn: float, arm: float):
    """The height of a body lying on its back along Z (head at -Z), smoothed: head, shoulders, chest, hips,
    legs and feet as soft ellipsoids, the max of them. `turn` rolls it a little; `arm` lifts a fold."""
    L = length
    parts = (  # z centre (fraction of L from the head), half-length, half-width, height
        (0.06, 0.06, 0.09, 0.2), (0.2, 0.07, 0.22, 0.17), (0.32, 0.12, 0.19, 0.2), (0.5, 0.08, 0.18, 0.16),
        (0.7, 0.16, 0.13, 0.12), (0.95, 0.04, 0.12, 0.16))
    h = np.zeros_like(X)
    for zc, hl, hw, ht in parts:
        z0 = -L * 0.5 + zc * L
        ex = (X - turn * 0.1 * np.sign(zc - 0.5)) / (hw * L / 1.8)
        ez = (Z - z0) / (hl * L / 1.8 + 1e-6)
        h = np.maximum(h, ht * L / 1.8 * np.sqrt(np.clip(1.0 - ex ** 2 - ez ** 2, 0.0, 1.0)))
    if arm:
        ex = (X - 0.22 * L / 1.8) / (0.06 * L / 1.8)
        ez = (Z + L * 0.05) / (0.16 * L / 1.8)
        h = np.maximum(h, arm * np.sqrt(np.clip(1.0 - ex ** 2 - ez ** 2, 0.0, 1.0)))
    return h


def build_shroud(name: str, seed: int, *, length: float = 1.8, turn: float = 0.0, arm: float = 0.0) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
        nx, nz = (13, 25) if not lod else (5, 7)
        half_w, half_l = 0.42 * length / 1.8 + 0.1, length * 0.5 + 0.15
        X, Z = np.meshgrid(np.linspace(-half_w, half_w, nx), np.linspace(-half_l, half_l, nz))
        body = _form(X, Z, length, turn, arm)
        # The cloth: the body's shape blurred (sailcloth bridges the hollows), its hem falling to the ground, small
        # folds where it crumples on the shingle.
        k = np.array([0.25, 0.5, 0.25])
        soft = body.copy()
        for _ in range(2 if not lod else 1):
            soft = np.apply_along_axis(lambda r: np.convolve(np.pad(r, 1, mode="edge"), k, "valid"), 1, soft)
            soft = np.apply_along_axis(lambda c: np.convolve(np.pad(c, 1, mode="edge"), k, "valid"), 0, soft)
        y = np.maximum(soft, body * 0.92) + 0.015
        if not lod:
            p = np.stack([X, np.zeros_like(X), Z], axis=-1)
            y += (noise.fbm(p / 0.18, 2) - 0.5) * 0.025 * (1.0 - kc.smoothstep(0.0, 0.15, y))
        edge = np.minimum(1.0 - np.abs(X) / half_w, 1.0 - np.abs(Z) / half_l)
        y = y * kc.smoothstep(0.0, 0.12, edge) + 0.008
        P = np.stack([X, y, Z], axis=-1)
        uv = np.stack([X * 1.5, Z * 1.5], axis=-1)
        col = np.array([0.0, 0.25, 0.2, 0.3])  # salt in the cloth, damp from the shingle
        kc.quad_strip(mb, P, mb.material(M_SHROUD), uv=uv, col=col, uv2=np.array([0.85, float(rng.random())]),
                      flip=True)
        if not lod:
            # The ties at the neck and the ankles.
            for zf in (0.13, 0.9):
                z = -length * 0.5 + zf * length
                row = int(round((z + half_l) / (2 * half_l) * (nz - 1)))
                xs = np.linspace(-half_w * 0.7, half_w * 0.7, 9)
                ys = np.interp(xs, X[row], y[row]) + 0.01
                kc.tube(mb, np.stack([xs, ys, np.full_like(xs, z)], axis=-1), 0.012, 4, mb.material(cw.M_ROPE),
                        variation=float(rng.random()))
        out.append(mb)
    return out


def build_strand_lamp(seed: int = 901) -> list:
    import props  # noqa: PLC0415  (the Haluna kit's lathe, read-only)

    out = []
    for lod in (False, True):
        rng = kc.rng_for("strand_lamp", seed)
        mb = kc.MeshBuilder("strand_lamp" + (cw.LOD if lod else ""))
        kc.tube(mb, np.array([[0.0, -0.3, 0.0], [0.0, 0.62, 0.0]]), 0.03, 6 if not lod else 4,
                mb.material(cw.M_TIMBER), cap_end=True, variation=float(rng.random()))
        # A clay oil lamp in a twist of iron on the stake's head, its wick lit.
        props.lathe(mb, [(0.03, 0.62), (0.07, 0.65), (0.075, 0.69), (0.05, 0.71)], "cw_earthenware", rng,
                    sides=12 if not lod else 6)
        kc.rounded_block(mb, (0.0, 0.735, 0.04), (0.012, 0.025, 0.012), mb.material(M_FLAME), radius=0.008, seg=1)
        out.append(mb)
    return out


def build_round_shield(seed: int = 902, *, r: float = 0.36) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("round_shield", seed)
        mb = kc.MeshBuilder("round_shield" + (cw.LOD if lod else ""))
        sides = 20 if not lod else 8
        a = np.linspace(0.0, 2 * math.pi, sides + 1)
        # Laid face-up, leaning on its rim a little (8 degrees), a shallow dish.
        tilt = kc.rot_x(0.14)
        prof_r = np.linspace(0.0, r, 5 if not lod else 2)
        grid = np.stack([np.cos(a)[None, :] * prof_r[:, None], 0.05 + 0.04 * (1 - (prof_r / r) ** 2)[:, None]
                         + 0 * a[None, :], np.sin(a)[None, :] * prof_r[:, None]], axis=-1) @ tilt.T
        grid[..., 1] += r * math.sin(0.14) + 0.01
        uv = np.stack([np.cos(a)[None, :] * prof_r[:, None], np.sin(a)[None, :] * prof_r[:, None]], axis=-1)
        kc.quad_strip(mb, grid, mb.material(M_LACQUER_RED), uv=uv, col=np.array([0.0, 0.2, 0.3, 0.4]),
                      uv2=np.array([0.9, float(rng.random())]))
        rim = np.stack([np.cos(a) * r, np.full_like(a, 0.05), np.sin(a) * r], axis=-1) @ tilt.T
        rim[:, 1] += r * math.sin(0.14) + 0.01
        kc.tube(mb, rim, 0.02, 5 if not lod else 3, mb.material(cw.M_IRON))
        if not lod:
            boss = (np.array([0.0, 0.11, 0.0]) @ tilt.T) + [0.0, r * math.sin(0.14) + 0.01, 0.0]
            kc.rounded_block(mb, boss, (0.07, 0.035, 0.07), mb.material(cw.M_IRON), rot=tilt, radius=0.03, seg=2)
        out.append(mb)
    return out


def build_ebbing_raft(seed: int = 903, *, w: float = 2.6, l: float = 4.2) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ebbing_raft", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ebbing_raft" + (cw.LOD if lod else ""))
        dark, red = mb.material(M_LACQUER_DARK), mb.material(M_LACQUER_RED)
        # Floats: three lacquered logs under the deck.
        for x in (-w * 0.36, 0.0, w * 0.36):
            kc.tube(mb, np.array([[x, 0.0, -l * 0.5], [x, 0.0, l * 0.5]]), 0.17, 10 if not lod else 5, dark,
                    cap_start=True, cap_end=True, variation=float(rng.random()))
        # The deck: planks across, lacquered dark, a red band at bow and stern; no rail.
        n = 18 if not lod else 1
        for k in range(n):
            z = -l * 0.5 + (k + 0.5) * l / n
            slot = red if (k in (0, n - 1) and not lod) else dark
            kc.plank(mb, (-w * 0.5, 0.2, z), (w * 0.5, 0.2, z), (l / n - 0.02) if not lod else l, 0.05, slot,
                     variation=float(rng.random()), noise=None if lod else noise)
        if not lod:
            # The staff's socket at the centre: a bronze-bound block; the pole laid along the deck's edge.
            kc.rounded_block(mb, (0.0, 0.3, 0.0), (0.12, 0.06, 0.12), red, radius=0.02, seg=2)
            kc.tube(mb, np.array([[0.0, 0.35, 0.0], [0.0, 0.31, 0.0]]), 0.04, 10, mb.material(cw.M_COPPER),
                    cap_start=True)
            kc.tube(mb, np.array([[w * 0.42, 0.26, -l * 0.62], [w * 0.4, 0.26, l * 0.6]]), 0.03, 6,
                    mb.material(cw.M_TIMBER), cap_start=True, cap_end=True)
        out.append(mb)
    return out


def build_flood_debris(seed: int = 904) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("flood_debris", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("flood_debris" + (cw.LOD if lod else ""))
        tm = mb.material(cw.M_TIMBER)
        for k in range(7 if not lod else 3):
            c = np.array([rng.uniform(-1.8, 1.8), rng.uniform(-0.02, 0.04), rng.uniform(-1.8, 1.8)])
            ln = rng.uniform(0.8, 2.2)
            a = rng.uniform(0, math.pi)
            d = np.array([math.cos(a), 0.0, math.sin(a)]) * ln * 0.5
            kc.plank(mb, c - d, c + d, rng.uniform(0.15, 0.25), 0.04, tm, variation=float(rng.random()),
                     noise=None if lod else noise, up=kc.normalize(np.array([rng.normal(0, 0.1), 1.0, rng.normal(0, 0.1)])))
        if not lod:
            # A door (boards and two ledges), floating face up; a shutter; a basket half sunk; a sodden cloth.
            door = kc.rot_y(0.5)
            for k in range(4):
                x = -0.42 + k * 0.28
                kc.plank(mb, door @ np.array([x, 0.02, -0.95]) + [1.0, 0, -0.6], door @ np.array([x, 0.02, 0.95])
                         + [1.0, 0, -0.6], 0.26, 0.04, tm, variation=float(rng.random()))
            kc.rounded_block(mb, (-1.2, 0.03, 1.1), (0.4, 0.03, 0.3), tm, rot=kc.rot_y(1.2), radius=0.01, seg=1)
            import props  # noqa: PLC0415

            props.lathe(mb, [(0.15, -0.12), (0.2, 0.0), (0.22, 0.08)], "cw_wicker", rng, sides=12,
                        at=(-0.4, 0.0, -1.3))
            U, V = np.meshgrid(np.linspace(-0.6, 0.6, 7), np.linspace(-0.4, 0.4, 5))
            p = np.stack([U + 0.6, 0.02 + 0.02 * np.sin(U * 6 + V * 4), V + 1.2], axis=-1)
            kc.quad_strip(mb, p, mb.material(M_SHROUD),
                          uv=np.stack([U, V], axis=-1), col=np.array([0.0, 0.0, 0.8, 0.3]), uv2=np.array([0.8, 0.5]),
                          flip=True)
        out.append(mb)
    return out


def build_milestone(seed: int = 905) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("milestone", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("milestone" + (cw.LOD if lod else ""))
        lat = mb.material(cw.M_LATERITE)
        kc.rounded_block(mb, (0.0, 0.5, 0.0), (0.2, 0.7, 0.16), lat, radius=0.06, seg=1 if lod else 3,
                         noise=None if lod else noise, disp_m=0.012, weather=cw.WALL_W, variation=0.4)
        if not lod:
            # The distance cut in strokes on the road face (+Z): seven bars and a cross-stroke, darkened.
            dk = mb.material(cw.M_DARK)
            for k in range(7):
                x = -0.12 + k * 0.04
                kc.rounded_block(mb, (x, 0.85, 0.161), (0.008, 0.08, 0.004), dk, radius=0.003, seg=1)
            kc.rounded_block(mb, (0.0, 0.85, 0.162), (0.14, 0.008, 0.004), dk, radius=0.003, seg=1)
            kc.rounded_block(mb, (0.02, 1.215, 0.0), (0.035, 0.025, 0.03), mb.material(cw.M_RUBBLE), radius=0.02,
                             seg=2)
        out.append(mb)
    return out


TARGETS = {
    "shroud_a": lambda: build_shroud("shroud_a", 911),
    "shroud_b": lambda: build_shroud("shroud_b", 912, turn=0.6, arm=0.12),
    "shroud_small": lambda: build_shroud("shroud_small", 913, length=1.05),
    "strand_lamp": build_strand_lamp,
    "round_shield": build_round_shield,
    "ebbing_raft": build_ebbing_raft,
    "flood_debris": build_flood_debris,
    "milestone": build_milestone,
}
