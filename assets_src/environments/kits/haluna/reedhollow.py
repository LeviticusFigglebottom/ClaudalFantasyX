"""The walks of Ossa Fen and Reedhollow (ossa_fen.md §1; M3-ENV-733): the pieces act1-chapters' Ch10 greybox walks
on (M4-C10-02: Walk*, Pocket, Exit, Causeway, Ring*, HousePlatform*, ClutchStone). Pure numpy.

Built in the Haluna kit beside ossa_fen.py (its materials). Every walkable top is level at y 0, 3.6 m wide along X
for the strips (the greybox's), with the greybox's rails: 0.5 m high, 0.4 m wide at z +-2.0.

  root_walk_6m      a Kirru root-walk over the tannin water, 6 m along X: split mangrove poles laid across two
                    bearer roots, lashed; the rails are living prop-roots arching up out of the water along both
                    edges, a lashed pole along their tops; under it the roots go down into the water.
  reed_causeway_6m  Reedhollow's reed causeway, 6 m along X: bundled-reed fascines laid across, bound with reed
                    rope, on pole pilings; the rails are paired stakes with a twisted reed rope between them.
  reed_platform_6m  a 6 x 6 m reed platform on pilings (a house's or the shore's), the fascines laid across X,
                    a bound edge-roll round it; no rail.
  clutch_stone      the clutch's stone on the shore: a low grey boulder, its top worn smooth by Kirru feet, three
                    shallow scratched lines where they stand to sing. 1.2 x 0.8 x 1.2 m.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import ossa_fen as of

M_BARK = of.M_BARK
M_REED = of.M_REED
M_LASH = of.M_LASH
M_MUD = of.M_MUD
M_STONE = "kit_causeway_stone"

TRI_BUDGET = {"root_walk_6m": (6000, 300), "reed_causeway_6m": (6000, 300), "reed_platform_6m": (8000, 300),
              "clutch_stone": (1500, 100)}

STRIP_LEN = 6.0
HALF_W = 1.8
RAIL_Z = 2.0
RAIL_H = 0.5
WATER_Y = of.WATER_Y
PILE_FOOT_Y = -1.6


def _deck_poles(mb, x0, x1, z0, z1, rng, noise, mat, *, r: float, lod: bool) -> None:
    """Poles (or fascines) laid across Z, side by side along X, their tops at y 0."""
    if lod:
        kc.rounded_block(mb, ((x0 + x1) * 0.5, -r, (z0 + z1) * 0.5), ((x1 - x0) * 0.5, r, (z1 - z0) * 0.5), mat,
                         radius=r * 0.5, seg=1)
        return
    for x in np.arange(x0 + r, x1, 2 * r):
        dy = rng.normal(0.0, 0.006)
        a, b = z0 - rng.uniform(0.0, 0.08), z1 + rng.uniform(0.0, 0.08)
        kc.tube(mb, np.array([[x, -r + dy, a], [x, -r + dy * 0.5, (a + b) * 0.5], [x, -r - dy, b]]), r, 6, mat,
                noise=noise, disp_m=r * 0.12, cap_start=True, cap_end=True)


def build_root_walk(seed: int = 3301) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("root_walk_6m", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("root_walk_6m" + ("-lod1" if lod else ""))
        bark, lash = mb.material(M_BARK), mb.material(M_LASH)
        hl = STRIP_LEN * 0.5
        _deck_poles(mb, -hl, hl, -HALF_W, HALF_W, rng, noise, bark, r=0.075, lod=lod)
        # Two bearer roots under the poles, along X.
        for z in (-HALF_W + 0.35, HALF_W - 0.35):
            kc.tube(mb, np.array([[-hl - 0.2, -0.22, z], [0.0, -0.2, z + rng.normal(0, 0.05)], [hl + 0.2, -0.22, z]]),
                    0.11, 4 if lod else 7, bark, noise=None if lod else noise, disp_m=0.015)
        # The rails: prop-roots arching up out of the water along each edge, a lashed pole along their tops.
        for sz in (-1.0, 1.0):
            zr = sz * RAIL_Z
            n = 3 if lod else 5
            for k in range(n):
                x = -hl + (k + 0.5) * STRIP_LEN / n + rng.uniform(-0.2, 0.2)
                t = np.linspace(0.0, 1.0, 5 if lod else 9)
                foot = np.array([x - 0.6, WATER_Y - 0.8, zr + sz * 0.5])
                top = np.array([x, RAIL_H - 0.02, zr])
                pts = foot[None] + (top - foot)[None] * t[:, None]
                pts[:, 1] += np.sin(t * math.pi) * 0.35  # each root arches before it meets the rail
                pts[:, 0] += np.sin(t * math.pi) * 0.2
                kc.tube(mb, pts, np.linspace(0.09, 0.05, len(t)), 4 if lod else 6, bark)
            xs = np.linspace(-hl, hl, 3)
            kc.tube(mb, np.stack([xs, np.full(3, RAIL_H - 0.05) + rng.normal(0, 0.02, 3), np.full(3, zr)], -1), 0.06,
                    4 if lod else 6, bark, cap_start=True, cap_end=True)
            if not lod:
                for x in np.linspace(-hl + 0.6, hl - 0.6, 4):  # lashings where the rail pole meets a root
                    kc.tube(mb, np.array([[x - 0.05, RAIL_H - 0.12, zr - 0.05], [x + 0.05, RAIL_H + 0.02, zr + 0.05]]),
                            0.018, 4, lash)
        if not lod:  # lashings across the deck at the bearers
            for z in (-HALF_W + 0.35, HALF_W - 0.35):
                for x in np.arange(-hl + 0.5, hl, 1.0):
                    kc.tube(mb, np.array([[x, -0.2, z - 0.12], [x, 0.01, z], [x, -0.2, z + 0.12]]), 0.016, 4, lash)
        out.append(mb)
    return out


def _pile(mb, x, z, top, rng, lod) -> None:
    kc.tube(mb, np.array([[x, PILE_FOOT_Y, z], [x + rng.normal(0, 0.03), top, z + rng.normal(0, 0.03)]]),
            np.array([0.09, 0.07]), 4 if lod else 6, mb.material(M_BARK), cap_end=True)


def _reed_rope(mb, a, b, sag: float, rng, *, lod: bool) -> None:
    t = np.linspace(0.0, 1.0, 4 if lod else 9)
    pts = np.asarray(a)[None] + (np.asarray(b) - np.asarray(a))[None] * t[:, None]
    pts[:, 1] -= np.sin(t * math.pi) * sag
    kc.tube(mb, pts, 0.03, 4 if lod else 5, mb.material(M_LASH))
    del rng


def build_reed_causeway(seed: int = 3302) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("reed_causeway_6m", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("reed_causeway_6m" + ("-lod1" if lod else ""))
        reed, lash = mb.material(M_REED), mb.material(M_LASH)
        hl = STRIP_LEN * 0.5
        _deck_poles(mb, -hl, hl, -HALF_W, HALF_W, rng, noise, reed, r=0.11, lod=lod)
        if not lod:  # the bindings round each fascine, in rows along the causeway
            for z in (-1.2, 0.0, 1.2):
                kc.tube(mb, np.array([[-hl, -0.005, z], [hl, -0.005, z]]), 0.02, 4, lash)
        for x in np.linspace(-hl + 0.5, hl - 0.5, 3):  # the pilings under it
            for z in (-HALF_W + 0.3, HALF_W - 0.3):
                _pile(mb, x, z, -0.2, rng, lod)
        for sz in (-1.0, 1.0):  # the rails: paired stakes and a twisted reed rope
            zr = sz * RAIL_Z
            stakes = np.linspace(-hl + 0.3, hl - 0.3, 4)
            if lod:  # one stake each and a straight rail
                for x in stakes:
                    kc.tube(mb, np.array([[x, -0.4, zr], [x, RAIL_H, zr]]), 0.045, 4, mb.material(M_BARK))
                kc.tube(mb, np.array([[-hl + 0.3, RAIL_H - 0.04, zr], [hl - 0.3, RAIL_H - 0.04, zr]]), 0.03, 4,
                        mb.material(M_LASH))
                continue
            for x in stakes:
                for dz in (-0.1, 0.1):
                    kc.tube(mb, np.array([[x, -0.6, zr + dz], [x + rng.normal(0, 0.02), RAIL_H + 0.08, zr + dz * 0.6]]),
                            np.array([0.05, 0.035]), 4 if lod else 6, mb.material(M_BARK), cap_end=True)
            for x0, x1 in zip(stakes[:-1], stakes[1:]):
                _reed_rope(mb, (x0, RAIL_H - 0.04, zr), (x1, RAIL_H - 0.04, zr), 0.08, rng, lod=lod)
        out.append(mb)
    return out


def build_reed_platform(seed: int = 3303) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("reed_platform_6m", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("reed_platform_6m" + ("-lod1" if lod else ""))
        reed = mb.material(M_REED)
        _deck_poles(mb, -3.0, 3.0, -3.0, 3.0, rng, noise, reed, r=0.11, lod=lod)
        if not lod:  # the bound edge-roll round it
            for a, b in (((-3.1, -0.11, -3.1), (3.1, -0.11, -3.1)), ((3.1, -0.11, -3.1), (3.1, -0.11, 3.1)),
                         ((3.1, -0.11, 3.1), (-3.1, -0.11, 3.1)), ((-3.1, -0.11, 3.1), (-3.1, -0.11, -3.1))):
                kc.tube(mb, np.array([a, b]), 0.13, 6, reed, noise=noise, disp_m=0.01)
            for k in range(28):
                s = k / 28.0 * 4.0
                side, f = int(s), s - int(s)
                p = [(-3.1 + 6.2 * f, -3.1), (3.1, -3.1 + 6.2 * f), (3.1 - 6.2 * f, 3.1), (-3.1, 3.1 - 6.2 * f)][side]
                ang = np.linspace(0.0, 2 * math.pi, 7)
                axis_x = side in (0, 2)
                ring = np.stack([np.zeros(7), np.cos(ang) * 0.14, np.sin(ang) * 0.14], -1)
                if not axis_x:
                    ring = ring[:, [2, 1, 0]]
                kc.tube(mb, ring + np.array([p[0], -0.11, p[1]]), 0.012, 3, mb.material(M_LASH))
        for x in (-2.4, 0.0, 2.4):
            for z in (-2.4, 0.0, 2.4):
                _pile(mb, x, z, -0.2, rng, lod)
        out.append(mb)
    return out


def build_clutch_stone(seed: int = 3304) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("clutch_stone", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("clutch_stone" + ("-lod1" if lod else ""))
        stone = mb.material(M_STONE)
        v0, t0 = mb.vertex_count, mb.triangle_count
        kc.rounded_block(mb, (0.0, 0.3, 0.0), (0.6, 0.42, 0.6), stone, radius=0.35, seg=1 if lod else 4,
                         noise=None if lod else noise, disp_m=0.06, disp_period_m=0.35,
                         weather=kc.Weathering(moss=0.3, salt=0.0, wet=0.4, erosion=0.6))
        if not lod:
            p = np.asarray(mb.pos[v0:])
            top = p[:, 1] > 0.55
            p[top, 1] = 0.55 + (p[top, 1] - 0.55) * 0.3  # worn flat on top by the feet that stand on it
            mb.pos[v0:] = p.tolist()
            kc.recompute_normals(mb, v0, t0)
            for k in range(3):  # three scratched lines across the worn top
                z = -0.25 + 0.25 * k
                kc.tube(mb, np.array([[-0.32, 0.585, z + rng.normal(0, 0.02)], [0.3, 0.585, z + rng.normal(0, 0.02)]]),
                        0.012, 3, mb.material(of.M_MUD))
        out.append(mb)
    return out


TARGETS = {"root_walk_6m": build_root_walk, "reed_causeway_6m": build_reed_causeway,
           "reed_platform_6m": build_reed_platform, "clutch_stone": build_clutch_stone}
