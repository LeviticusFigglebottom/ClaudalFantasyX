"""Brine Shoals wrecks (brine_shoals.md §2): ships that grounded on the bars, now black ribs and hull
sections the Saltwrights take apart. Pure numpy; see bs_common.py. All tarred timber (bs_timber_tar):
the weathering shader's height bands put the algae and barnacles at the low-water line on their own.

  wreck_hull_section   10 m of a carvel-built trader, 4.2 m beam, listing 28 deg to starboard, planks sprung
                       and missing, frames showing at the broken end, mud-filled to +0.25 m
  wreck_bow            a 6 m bow section half sunk and pitched up, its stem post rising to about 4.2 m
  wreck_mast_fallen    an 11 m mast with its yard and torn rope, lying half bedded in the mud
  wreck_mast_standing  a 7.5 m mast stub leaning 14 deg, its head split, a crosstree stump and rope ends
  wreck_ribs_large     a big hull's frames and keel: the Haluna causeway's wreck_rib generator at 1.6x
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
import causeway  # the Haluna kit's causeway pieces (read-only reuse)
from bs_common import kc

TRI_BUDGET = {
    "wreck_hull_section": (12000, 1200),
    "wreck_bow": (9000, 900),
    "wreck_mast_fallen": (5000, 500),
    "wreck_mast_standing": (4000, 400),
    "wreck_ribs_large": (5000, 500),
}

PLANK_T = 0.07  # strake thickness


def _orient(grid: np.ndarray, outward: np.ndarray) -> bool:
    """True when quad_strip must flip so the grid's faces point along `outward`."""
    n = np.cross(grid[0, 1] - grid[0, 0], grid[1, 0] - grid[0, 0])
    return float(np.dot(n, outward)) < 0.0


def shell_strip(mb: kc.MeshBuilder, outer: np.ndarray, outward: np.ndarray, mat: int, *, thick: float = PLANK_T,
                variation: float = 0.5, weather: kc.Weathering = bc.WRECK, noise: kc.Noise3 | None = None,
                inner: bool = True) -> None:
    """A plank run with thickness: `outer` is a (rows, cols, 3) grid (rows along the run), offset inward
    along its own normal by `thick` for the inner face, with edge strips closing all four sides."""
    rows, cols = outer.shape[:2]
    du = np.gradient(outer, axis=1)
    dv = np.gradient(outer, axis=0)
    n = kc.normalize(np.cross(du, dv))
    if float(np.sum(n * outward)) < 0:
        n = -n
    inn = outer - n * thick
    if noise is not None:
        breakup = noise.fbm(outer / 0.6, 2)
    else:
        breakup = np.full((rows, cols), 0.5)
    up = n[..., 1]
    col = np.stack([np.zeros((rows, cols)), np.clip(weather.salt * (0.3 + breakup), 0, 1),
                    np.clip(weather.wet * breakup, 0, 1), np.clip(weather.erosion * (0.5 + 0.5 * breakup), 0, 1)],
                   axis=-1)
    uv2 = np.stack([np.clip(0.8 + 0.2 * up, 0.4, 1.0), np.full((rows, cols), variation)], axis=-1)
    along = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(outer[:, 0], axis=0), axis=1))])
    across = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(outer[0], axis=0), axis=1))])
    uv = np.stack([np.broadcast_to(across[None, :] + variation * 3.1, (rows, cols)),
                   np.broadcast_to(along[:, None], (rows, cols))], axis=-1)
    kc.quad_strip(mb, outer, mat, uv=uv, col=col, uv2=uv2, flip=_orient(outer, outward))
    if not inner:
        return
    kc.quad_strip(mb, inn, mat, uv=uv, col=col, uv2=uv2 * np.array([0.7, 1.0]), flip=not _orient(inn, outward))
    for edge in ((slice(None), 0), (slice(None), cols - 1), (0, slice(None)), (rows - 1, slice(None))):
        e_out, e_in = outer[edge], inn[edge]
        grid = np.stack([e_out, e_in], axis=1)
        mid = grid.mean(axis=(0, 1))
        centre = outer.mean(axis=(0, 1))
        kc.quad_strip(mb, grid, mat, uv=np.zeros(grid.shape[:2] + (2,)), col=col[edge][:, None].repeat(2, 1),
                      uv2=np.array([0.6, variation]), flip=_orient(grid, mid - centre), smooth=False)


class Hull:
    """A carvel hull surface: point(x, g, side) with g 0 at the keel and 1 at the sheer."""

    def __init__(self, beam_fn, depth_fn, rocker_fn=None):
        self.beam = beam_fn
        self.depth = depth_fn
        self.rocker = rocker_fn or (lambda x: np.zeros_like(np.asarray(x, float)))

    def point(self, x, g, side: float) -> np.ndarray:
        x = np.asarray(x, float)
        g = np.asarray(g, float)
        th = g * math.pi * 0.5
        b = self.beam(x)
        d = self.depth(x)
        z = side * b * np.sin(th) ** 0.85
        y = d * (0.55 * (1.0 - np.cos(th)) + 0.45 * g ** 1.5) + self.rocker(x)
        return np.stack(np.broadcast_arrays(x, y, z), axis=-1)


def planking(mb: kc.MeshBuilder, hull: Hull, x0: float, x1: float, rng, noise, *, strakes: int = 9,
             ragged_end: float = 1.6, missing_p: float = 0.18, xform=np.eye(3), offset=(0, 0, 0),
             ragged_start: float = 0.0, seg_m: float = 0.5) -> None:
    tm = mb.material(bc.M_TAR)
    offset = np.asarray(offset, float)
    for side in (-1.0, 1.0):
        for k in range(strakes):
            g0 = k / strakes + 0.006
            g1 = (k + 1) / strakes - 0.006
            # Each strake ends raggedly at the broken end(s); some runs are missing (sprung planks).
            xa = x0 + rng.uniform(0.0, ragged_start)
            xb = x1 - rng.uniform(0.0, ragged_end) * (0.4 + 0.6 * k / strakes)
            cuts = [xa]
            x = xa
            while x < xb:
                x += rng.uniform(2.0, 4.5)
                cuts.append(min(x, xb))
            for a, b in zip(cuts[:-1], cuts[1:]):
                if b - a < 0.4:
                    continue
                high = k >= strakes - 3
                if rng.random() < missing_p * (1.6 if high else 0.6):
                    continue
                n_x = max(2, int((b - a) / seg_m) + 1)
                xs = np.linspace(a + 0.02, b - 0.02, n_x)
                gs = np.linspace(g0, g1, 3)
                X, G = np.meshgrid(xs, gs, indexing="ij")
                grid = hull.point(X, G, side) @ xform.T + offset
                axis_pt = hull.point(X, np.zeros_like(G), side) @ xform.T + offset
                outward = (grid - axis_pt).mean(axis=(0, 1)) + np.array([0.0, -0.2, 0.0])
                outward[0] = 0.0
                shell_strip(mb, grid, outward, tm, variation=float(rng.random()), noise=noise)


def frames(mb: kc.MeshBuilder, hull: Hull, xs, rng, noise, *, xform=np.eye(3), offset=(0, 0, 0), snap_p: float = 0.25,
           sides: int = 4, r: float = 0.07) -> None:
    tm = mb.material(bc.M_TAR)
    offset = np.asarray(offset, float)
    for x in xs:
        top_p = 1.0 - (rng.uniform(0.3, 0.6) if rng.random() < snap_p else 0.0)
        top_s = 1.0 - (rng.uniform(0.3, 0.6) if rng.random() < snap_p else 0.0)
        g = np.concatenate([np.linspace(top_p, 0.0, 6)[:-1], np.linspace(0.0, top_s, 6)])
        side = np.concatenate([np.full(5, -1.0), np.full(6, 1.0)])
        pts = np.array([hull.point(x, gg, s) for gg, s in zip(g, side)])
        # Set the frame inside the planking (toward the hull's centre line and up).
        centre = np.array([x, float(hull.depth(np.array(x))) * 0.6, 0.0])
        pts = pts + kc.normalize(centre - pts) * (PLANK_T + r * 0.9)
        pts = pts @ xform.T + offset
        kc.tube(mb, pts, r, sides, tm, weather=bc.WRECK, noise=noise, disp_m=0.012, variation=float(rng.random()),
                cap_start=True, cap_end=True)


def keel(mb: kc.MeshBuilder, hull: Hull, x0: float, x1: float, *, xform=np.eye(3), offset=(0, 0, 0), r: float = 0.13):
    xs = np.linspace(x0, x1, 6)
    pts = np.array([hull.point(x, 0.0, 1.0) for x in xs]) - np.array([0.0, r * 0.6, 0.0])
    kc.tube(mb, pts @ xform.T + np.asarray(offset, float), r, 4, mb.material(bc.M_TAR), weather=bc.WRECK,
            cap_start=True, cap_end=True, first_normal=(0.0, 1.0, 0.0))


def mud_fill(mb: kc.MeshBuilder, hull: Hull, x0: float, x1: float, y_m: float, *, xform, offset, n_x: int = 21,
             n_z: int = 11) -> None:
    """A horizontal mud surface at world y_m inside the hull, clipped to the hull's section there."""
    offset = np.asarray(offset, float)
    xs = np.linspace(x0 + 0.1, x1 - 0.1, n_x)
    lo = np.zeros(n_x)
    hi = np.zeros(n_x)
    gs = np.linspace(0.0, 1.0, 41)
    for i, x in enumerate(xs):
        zs = []
        for side in (-1.0, 1.0):
            pts = hull.point(np.full_like(gs, x), gs, side) @ xform.T + offset
            above = pts[:, 1] > y_m
            idx = int(np.argmax(above)) if above.any() else len(gs) - 1
            zs.append(pts[idx, 2])
        lo[i], hi[i] = min(zs) + 0.08, max(zs) - 0.08
    wx = xs  # x is unrotated: the list is about the hull's x axis only
    zmin, zmax = float(lo.min()), float(hi.max())
    zz = np.linspace(zmin, zmax, n_z)

    def keep(X, Z):
        li = np.interp(X, wx, lo)
        hi_ = np.interp(X, wx, hi)
        return (Z >= li - 0.3) & (Z <= hi_ + 0.3)

    def clampz(X, Z):
        return np.clip(Z, np.interp(X, wx, lo), np.interp(X, wx, hi))

    start = mb.vertex_count
    bc.heightfield(mb, wx, zz, lambda X, Z: np.full_like(X, y_m), mb.material(bc.M_MUD), keep=keep,
                   wet=lambda X, Z, Y: 0.6 + 0 * X, salt=lambda X, Z, Y: 0.2 + 0 * X, ao=lambda X, Z, Y: 0.7 + 0 * X)
    # Pull the grid's outer columns onto the hull's inner skin so the fill meets the planks.
    p = np.asarray(mb.pos[start:])
    p[:, 2] = clampz(p[:, 0], p[:, 2])
    mb.pos[start:] = p.tolist()


def _sink(builders_pts_min: float, depth: float) -> np.ndarray:
    return np.array([0.0, -depth - builders_pts_min, 0.0])


# ---------------------------------------------------------------------------------------------
# Hull section
# ---------------------------------------------------------------------------------------------
def build_hull_section(seed: int = 401) -> list[kc.MeshBuilder]:
    hull = Hull(lambda x: np.full_like(np.asarray(x, float), 2.1) - 0.012 * np.asarray(x, float) ** 2,
                lambda x: np.full_like(np.asarray(x, float), 2.7))
    x0, x1 = -5.0, 5.0
    xform = kc.rot_y(0.0) @ kc.rot_x(math.radians(28.0))
    probe = np.array([hull.point(x, g, s) for x in (x0, 0.0, x1) for g in np.linspace(0, 1, 9) for s in (-1, 1)])
    offset = _sink(float((probe @ xform.T)[:, 1].min()), 0.9)
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wreck_hull_section", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("wreck_hull_section" + (bc.LOD if lod else ""))
        if lod:
            for side in (-1.0, 1.0):
                X, G = np.meshgrid(np.linspace(x0, x1 - 0.8, 5), np.linspace(0.0, 1.0, 4), indexing="ij")
                grid = hull.point(X, G, side) @ xform.T + offset
                outward = np.array([0.0, -0.2, side]) @ xform.T
                shell_strip(mb, grid, outward, mb.material(bc.M_TAR), inner=False)
                kc.quad_strip(mb, grid, mb.material(bc.M_TAR), uv=np.zeros(grid.shape[:2] + (2,)),
                              col=np.array([0, 0.5, 0.2, 0.6]), uv2=np.array([0.6, 0.5]),
                              flip=not _orient(grid, outward))
            mud_fill(mb, hull, x0, x1, 0.25, xform=xform, offset=offset, n_x=5, n_z=4)
            out.append(mb)
            continue
        planking(mb, hull, x0, x1, rng, noise, xform=xform, offset=offset, ragged_end=3.4, ragged_start=1.2,
                 missing_p=0.24)
        frames(mb, hull, np.arange(x0 + 0.25, x1 + 0.4, 0.55), rng, noise, xform=xform, offset=offset, snap_p=0.45)
        keel(mb, hull, x0 - 0.2, x1 + 0.3, xform=xform, offset=offset)
        # Deck beams across the sheer, a few still carrying deck planks on the high (port) side.
        for x in np.arange(x0 + 0.8, x1 - 1.5, 2.3):
            a = hull.point(x, 1.0, -1.0) + np.array([0.0, -0.08, 0.1])
            b = hull.point(x, 1.0, 1.0) + np.array([0.0, -0.08, -0.1])
            if rng.random() < 0.3:
                b = a + (b - a) * rng.uniform(0.3, 0.6)  # snapped
            kc.tube(mb, np.array([a, b]) @ xform.T + offset, 0.075, 4, mb.material(bc.M_TAR), weather=bc.WRECK,
                    cap_start=True, cap_end=True, first_normal=(0.0, 1.0, 0.0), variation=float(rng.random()))
        for k in range(2):
            z = -1.6 + 0.28 * k
            p0 = np.array([x0 + 0.4 + rng.uniform(0, 0.6), 2.66, z])
            p1 = np.array([x0 + 3.5 + rng.uniform(0, 1.5), 2.66, z])
            kc.plank(mb, p0 @ xform.T + offset, p1 @ xform.T + offset, 0.26, 0.05, mb.material(bc.M_TAR),
                     up=np.array([0.0, 1.0, 0.0]) @ xform.T, weather=bc.WRECK, variation=float(rng.random()),
                     noise=noise)
        mud_fill(mb, hull, x0, x1, 0.25, xform=xform, offset=offset)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Bow
# ---------------------------------------------------------------------------------------------
def build_bow(seed: int = 411) -> list[kc.MeshBuilder]:
    length = 6.0

    def beam(x):
        t = np.clip(np.asarray(x, float) / length, 0.0, 1.0)
        return 1.9 * np.sqrt(np.clip(1.0 - t ** 2.2, 0.0, 1.0)) + 0.04

    def depth(x):
        t = np.clip(np.asarray(x, float) / length, 0.0, 1.0)
        return 2.5 + 0.6 * t ** 2

    def rocker(x):
        t = np.clip(np.asarray(x, float) / length, 0.0, 1.0)
        return 0.5 * t ** 3

    hull = Hull(beam, depth, rocker)
    xform = kc.rot_y(math.radians(8.0)) @ kc.rot_z(math.radians(12.0)) @ kc.rot_x(math.radians(-9.0))
    probe = np.array([hull.point(x, g, s) for x in (0.0, length * 0.5) for g in np.linspace(0, 1, 9) for s in (-1, 1)])
    offset = _sink(float((probe @ xform.T)[:, 1].min()), 1.0)
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wreck_bow", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("wreck_bow" + (bc.LOD if lod else ""))
        if lod:
            for side in (-1.0, 1.0):
                X, G = np.meshgrid(np.linspace(0.6, length, 5), np.linspace(0.0, 1.0, 4), indexing="ij")
                grid = hull.point(X, G, side) @ xform.T + offset
                outward = np.array([0.0, -0.2, side]) @ xform.T
                shell_strip(mb, grid, outward, mb.material(bc.M_TAR), inner=False)
                kc.quad_strip(mb, grid, mb.material(bc.M_TAR), uv=np.zeros(grid.shape[:2] + (2,)),
                              col=np.array([0, 0.5, 0.2, 0.6]), uv2=np.array([0.6, 0.5]),
                              flip=not _orient(grid, outward))
        else:
            planking(mb, hull, 0.0, length, rng, noise, xform=xform, offset=offset, ragged_end=0.0,
                     ragged_start=1.8, missing_p=0.14, seg_m=0.4)
            frames(mb, hull, np.arange(0.3, length - 0.6, 0.55), rng, noise, xform=xform, offset=offset)
            keel(mb, hull, -0.3, length, xform=xform, offset=offset)
        # Stem post: up from the forefoot, curving out and up past the sheer.
        t = np.linspace(0.0, 1.0, 7 if not lod else 3)
        stem = np.stack([length + 0.35 * t ** 1.5, rocker(length) - 0.1 + (depth(length) + 1.1) * t, np.zeros_like(t)],
                        axis=-1)
        kc.tube(mb, stem @ xform.T + offset, np.linspace(0.16, 0.11, len(t)), 5 if not lod else 4,
                mb.material(bc.M_TAR), weather=bc.WRECK, cap_start=True, cap_end=True, noise=None if lod else noise,
                disp_m=0.015)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Masts and ribs
# ---------------------------------------------------------------------------------------------
def _mast(mb: kc.MeshBuilder, base, top, r0: float, r1: float, rng, noise, *, lod: bool, split_top: bool = False):
    base = np.asarray(base, float)
    top = np.asarray(top, float)
    n = 10 if not lod else 3
    pts = np.linspace(base, top, n)
    kc.tube(mb, pts, np.linspace(r0, r1, n), 9 if not lod else 5, mb.material(bc.M_TAR), weather=bc.WRECK,
            noise=None if lod else noise, disp_m=0.02, disp_period_m=0.5, variation=float(rng.random()),
            cap_start=True, cap_end=not split_top, u_repeat=2.0)
    if lod:
        return
    axis = kc.normalize(top - base)
    for f in (0.35, 0.62):  # iron mast bands
        c = base + (top - base) * f
        kc.tube(mb, np.array([c - axis * 0.04, c + axis * 0.04]), (r0 + (r1 - r0) * f) * 1.08, 10,
                mb.material(bc.M_IRON))
    if split_top:
        side = kc.any_perpendicular(axis)
        for k in range(3):  # jagged splinters at the break
            a = k * 2.1 + rng.uniform(-0.3, 0.3)
            d = side * math.cos(a) + np.cross(axis, side) * math.sin(a)
            p0 = top + d * r1 * 0.5
            p1 = p0 + axis * rng.uniform(0.25, 0.6) + d * 0.03
            kc.tube(mb, np.array([p0, p1]), np.array([r1 * 0.45, 0.01]), 4, mb.material(bc.M_TAR), cap_start=True)


def _rope(mb: kc.MeshBuilder, pts, rng) -> None:
    kc.tube(mb, np.asarray(pts, float), 0.018, 4, mb.material(bc.M_ROPE), variation=float(rng.random()))


def build_mast_fallen(seed: int = 421, length: float = 11.0) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wreck_mast_fallen", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("wreck_mast_fallen" + (bc.LOD if lod else ""))
        base = np.array([-length * 0.5, -0.05, 0.0])
        top = np.array([length * 0.5, 0.12, 0.6])
        _mast(mb, base, top, 0.19, 0.11, rng, noise, lod=lod)
        # The yard, still lashed across near the head, one arm in the mud.
        c = base + (top - base) * 0.8 + np.array([0.0, 0.12, 0.0])
        yard = np.array([c + np.array([0.6, -0.15, -3.0]), c, c + np.array([-0.4, 0.25, 2.8])])
        kc.tube(mb, yard, np.array([0.07, 0.1, 0.07]), 6 if not lod else 4, mb.material(bc.M_TAR), weather=bc.WRECK,
                cap_start=True, cap_end=True)
        if not lod:
            for k in range(4):  # torn rigging trailing into the mud
                a = base + (top - base) * rng.uniform(0.5, 0.95) + np.array([0, 0.15, 0])
                t = np.linspace(0, 1, 8)
                d = np.array([rng.normal(0, 1.0), 0.0, rng.uniform(1.0, 2.5) * rng.choice([-1, 1])])
                pts = a[None] + t[:, None] * d[None] + np.array([0, 1, 0])[None] * (-0.15 * np.sin(t * math.pi) - 0.1 * t)[:, None]
                _rope(mb, pts, rng)
            # A block (pulley) still on a rope tail.
            kc.rounded_block(mb, top + np.array([-0.6, 0.0, 0.55]), (0.12, 0.08, 0.07), mb.material(bc.M_TAR),
                             radius=0.04, seg=2)
        out.append(mb)
    return out


def build_mast_standing(seed: int = 431, height: float = 7.5) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wreck_mast_standing", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("wreck_mast_standing" + (bc.LOD if lod else ""))
        lean = math.radians(14.0)
        axis = np.array([math.sin(lean), math.cos(lean), 0.0])
        base = np.array([0.0, -1.2, 0.0])
        top = base + axis * (height + 1.2)
        _mast(mb, base, top, 0.2, 0.13, rng, noise, lod=lod, split_top=True)
        # Crosstree stump.
        c = base + axis * (height + 1.2 - 1.1)
        ct = np.array([c + np.array([0.0, 0.0, -0.9]), c + np.array([0.0, 0.0, 0.5])])
        kc.tube(mb, ct, 0.06, 4, mb.material(bc.M_TAR), cap_start=True, cap_end=True, first_normal=(0, 1, 0))
        if not lod:
            for k in range(3):
                a = c + np.array([0.0, -0.05, -0.8 + 0.6 * k])
                ln = rng.uniform(1.2, 3.0)
                t = np.linspace(0, 1, 6)
                pts = a[None] + np.stack([0.15 * t * np.sin(k + t * 2), -ln * t, 0.1 * t], axis=-1)
                _rope(mb, pts, rng)
            # The heel's partners: three frame stumps of the vanished hull around the foot.
            for k in range(3):
                a = rng.uniform(0, 2 * math.pi)
                p0 = np.array([math.cos(a) * 1.2, -0.3, math.sin(a) * 1.2])
                p1 = p0 + np.array([math.cos(a) * 0.3, rng.uniform(0.6, 1.2), math.sin(a) * 0.3])
                kc.tube(mb, np.array([p0, p1]), 0.07, 4, mb.material(bc.M_TAR), cap_end=True, weather=bc.WRECK)
        out.append(mb)
    return out


def build_ribs_large(scale: float = 1.6) -> list[kc.MeshBuilder]:
    out = []
    for mb in causeway.build_wreck_rib(seed=441):
        mb.name = mb.name.replace("wreck_rib", "wreck_ribs_large")
        mb.pos = (np.asarray(mb.pos) * scale).tolist()
        mb.materials = [bc.M_TAR if m == "kit_timber" else m for m in mb.materials]
        out.append(mb)
    return out


TARGETS = {
    "wreck_hull_section": build_hull_section,
    "wreck_bow": build_bow,
    "wreck_mast_fallen": build_mast_fallen,
    "wreck_mast_standing": build_mast_standing,
    "wreck_ribs_large": build_ribs_large,
}
