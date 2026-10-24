"""Shared helpers for the broadleaf trees (M2-ENV-07): the hero banyan and the windbreak tree.

Pure numpy, Blender coordinates (metres, +Z up), like the other vegetation generators. A tree is
described once (every random draw happens while the structure is grown, in a fixed order) and then
meshed per LOD with no further randomness, so the LODs are the same tree.

  Limb       a bark tube (stem, limb, branch, twig, root) with per-ring radii
  flange     a buttress: a tube with a tall, thin elliptical section that stands on the ground
  spray      a bent alpha card carrying one painted twig of leaves (veg_common.COASTAL_ATLAS)
  core       a lumpy closed shell inside a leaf clump, one quad per face mapped to an opaque leaf
             mosaic cell, so a crown never shows sky through its middle at distance

Channels (vegetation.md "Wind conventions"): COLOR.r primary sway (z / H)^1.6, COLOR.g secondary
bob (0 on stems, rising along branches, twigs and sprays; hanging roots swing), COLOR.b phase (one per
leaf clump, shared by its branch, twigs and sprays so nothing tears), COLOR.a flutter (spray edges and
tips only); UV2.x occlusion, UV2.y tint variation on foliage / height fraction on bark.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

import veg_common as vc
from veg_common import UP, MeshBuilder

SWAY_EXPONENT = 1.6


@dataclass
class Limb:
    pts: np.ndarray  # (k, 3) centre line
    radii: np.ndarray  # (k,)
    phase: float  # COLOR.b
    g0: float = 0.0  # secondary weight at the first ring
    g1: float = 0.0  # ... and at the last
    kind: str = "bark"  # material key ("bark" | "root")
    keep: float = 0.0  # kept in a LOD when keep <= that LOD's keep fraction for its class
    cap: bool = False
    ao0: float = 0.85  # UV2.x at the first ring
    ao1: float = 0.85  # ... and at the last


def sway(z, height: float) -> np.ndarray:
    return np.clip(np.asarray(z, dtype=float) / height, 0.0, 1.0) ** SWAY_EXPONENT


def resample(pts: np.ndarray, radii: np.ndarray, step: int) -> tuple[np.ndarray, np.ndarray]:
    """Every `step`-th ring, always keeping both ends."""
    if step <= 1 or len(pts) <= 2:
        return pts, radii
    idx = list(range(0, len(pts) - 1, step)) + [len(pts) - 1]
    return pts[idx], radii[idx]


def arc_length(pts: np.ndarray) -> np.ndarray:
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])


def mesh_limb(mb: MeshBuilder, limb: Limb, mat: int, sides: int, height: float, *, step: int = 1,
              tile_m: float = vc.BANYAN_BARK_TILE_M, v0: float = 0.0) -> None:
    pts, radii = resample(limb.pts, limb.radii, step)
    arc = arc_length(pts)
    t = arc / max(arc[-1], 1e-6)
    r = sway(pts[:, 2], height)
    g = limb.g0 + (limb.g1 - limb.g0) * t
    col = np.stack([r, g, np.full_like(t, limb.phase), np.zeros_like(t)], axis=-1)
    ao = limb.ao0 + (limb.ao1 - limb.ao0) * t
    uv2 = np.stack([ao, np.clip(pts[:, 2] / height, 0.0, 1.0)], axis=-1)
    # One U repeat covers tile_m / 2 of circumference (the bark texture is twice as tall as wide).
    u_rep = max(1.0, float(round(2.0 * math.pi * float(radii.max()) / (tile_m * 0.5))))
    vc.tube(mb, pts, radii, sides, mat, v_coord=v0 + arc / tile_m, u_repeat=u_rep, col=col, uv2=uv2,
            cap_end=limb.cap)


def mesh_flange(mb: MeshBuilder, centers: np.ndarray, half_thick: np.ndarray, half_high: np.ndarray, mat: int,
                sides: int, height: float, phase: float, *, tile_m: float = vc.BANYAN_BARK_TILE_M) -> None:
    """A buttress: an elliptical-section tube whose long section axis stays vertical."""
    tang = np.zeros_like(centers)
    tang[1:-1] = centers[2:] - centers[:-2]
    tang[0] = centers[1] - centers[0]
    tang[-1] = centers[-1] - centers[-2]
    tang = vc.normalize(tang)
    up = vc.normalize(UP[None, :] - tang * (tang @ UP)[:, None])
    side = np.cross(tang, up)
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    c, s = np.cos(ang), np.sin(ang)
    P = (centers[:, None, :] + side[:, None, :] * (half_thick[:, None] * c[None, :])[..., None]
         + up[:, None, :] * (half_high[:, None] * s[None, :])[..., None])
    N = vc.normalize(side[:, None, :] * (c[None, :] / half_thick[:, None])[..., None]
                     + up[:, None, :] * (s[None, :] / half_high[:, None])[..., None])
    arc = arc_length(centers)
    perim = math.pi * (float(half_thick.max()) + float(half_high.max()))
    u_rep = max(1.0, float(round(perim / (tile_m * 0.5))))
    U, V = np.meshgrid(ang / (2.0 * math.pi) * u_rep, arc / tile_m)
    uv = np.stack([U, V], axis=-1)
    z = P[..., 2]
    col = np.stack([sway(z, height), np.zeros_like(z), np.full_like(z, phase), np.zeros_like(z)], axis=-1)
    # The flange's foot and its inner faces near the trunk sit in shade.
    ao = np.clip(0.45 + 0.5 * vc.smoothstep(0.0, 1.2, z), 0.0, 1.0)
    uv2 = np.stack([ao, np.clip(z / height, 0.0, 1.0)], axis=-1)
    # (side, up) with side = tang x up is the mirror of vc.tube's ring frame, hence flip.
    mb.add_grid(P, N, uv, uv2, col, mat, flip=True)


def mesh_spray(mb: MeshBuilder, sp: dict, mat: int, rect, cell_m: float, height: float, *, rows: int, scale: float,
               clump_center: np.ndarray, size_px: tuple[int, int], cols: int = 2) -> None:
    """One bent spray card. sp: attach, out (texture up), face (card normal), size (m, cell height),
    droop, cup, phase, tint, ao, g (secondary weight at the attach point)."""
    out = vc.normalize(np.asarray(sp["out"], dtype=float))
    face = np.asarray(sp["face"], dtype=float)
    face = vc.normalize(face - out * float(np.dot(face, out)))
    side = np.cross(out, face)
    hgt = float(sp["size"]) * scale
    wid = hgt * vc.cell_aspect(rect, size_px)
    t = np.linspace(0.0, 1.0, rows + 1)
    x = np.linspace(-1.0, 1.0, cols + 1) if rows >= 2 else np.array([-1.0, 1.0])
    T, X = np.meshgrid(t, x, indexing="ij")
    base = np.asarray(sp["attach"], dtype=float) - out * 0.04 * hgt
    P = (base[None, None, :] + out * (T * hgt)[..., None] + side * (X * wid * 0.5)[..., None]
         + face * ((float(sp["cup"]) * (X ** 2) * wid * 0.5) + 0.12 * (T ** 2) * hgt)[..., None]
         - UP * (float(sp["droop"]) * (T ** 2) * hgt)[..., None])
    radial = vc.normalize(P - clump_center)
    # The grid's geometric front is +face; Godot flips the normal on back faces, so the shading
    # normal (bent out of the clump) and the winding must agree.
    flip = float(np.dot(face, np.mean(radial.reshape(-1, 3), axis=0))) < 0
    nf = -face if flip else face
    N = vc.normalize(nf * 0.35 + radial * 0.65)
    uv = vc.atlas_uv(rect, (X + 1.0) * 0.5, 1.0 - T)
    g0 = float(sp["g"])
    col = np.stack([sway(P[..., 2], height), g0 + (1.0 - g0) * T, np.full_like(T, float(sp["phase"])),
                    np.clip(0.3 * np.abs(X) + 0.6 * T, 0.0, 1.0)], axis=-1)
    ao = np.clip(float(sp["ao"]) * (0.85 + 0.15 * T), 0.0, 1.0)
    uv2 = np.stack([ao, np.full_like(T, float(sp["tint"]))], axis=-1)
    mb.add_grid(P, N, uv, uv2, col, mat, flip=flip)


def lump(center: np.ndarray, waves: np.ndarray, d: np.ndarray) -> np.ndarray:
    """Radial scale of a lumpy shell for unit directions d (n, 3); waves rows: (kx, ky, kz, phase, amp)."""
    s = np.ones(len(d))
    for kx, ky, kz, ph, amp in waves:
        s = s + amp * np.sin(d @ np.array([kx, ky, kz]) + ph)
    return s


def mesh_core(mb: MeshBuilder, center: np.ndarray, radii: np.ndarray, waves: np.ndarray, mat: int, rect,
              height: float, *, rings: int, segs: int, phase: float, ao: tuple[float, float], tint: float,
              z_floor: float | None = None) -> None:
    """A closed lumpy ellipsoid; each face is its own quad mapped to the whole (tiling) mass cell."""
    th = np.linspace(0.0, math.pi, rings + 1)
    ph = np.linspace(0.0, 2.0 * math.pi, segs + 1)
    T, Pp = np.meshgrid(th, ph, indexing="ij")
    d = np.stack([np.sin(T) * np.cos(Pp), np.sin(T) * np.sin(Pp), -np.cos(T)], axis=-1)
    flat = d.reshape(-1, 3)
    s = lump(center, waves, flat).reshape(T.shape)
    P = center + d * radii * s[..., None]
    if z_floor is not None:
        P[..., 2] = np.maximum(P[..., 2], z_floor)
    N = vc.normalize(d / radii)
    inset = 3.0 / 1024.0  # keep the bilinear footprint inside the cell
    r0 = (rect[0] + inset, rect[1] + inset, rect[2] - inset, rect[3] - inset)
    for i in range(rings):
        for j in range(segs):
            q = np.array([P[i, j], P[i, j + 1], P[i + 1, j + 1], P[i + 1, j]])
            n = np.array([N[i, j], N[i, j + 1], N[i + 1, j + 1], N[i + 1, j]])
            uv = vc.atlas_uv(r0, np.array([0.0, 1.0, 1.0, 0.0]), np.array([1.0, 1.0, 0.0, 0.0]))
            up = (q[:, 2] - center[2]) / max(float(radii[2]), 1e-6)  # -1 bottom .. 1 top
            a = np.clip(ao[0] + (ao[1] - ao[0]) * (up * 0.5 + 0.5), 0.0, 1.0)
            col = np.stack([sway(q[:, 2], height), np.full(4, 0.35), np.full(4, phase), np.zeros(4)], axis=-1)
            uv2 = np.stack([a, np.full(4, tint)], axis=-1)
            b = mb.add_vertices(q, n, uv, uv2, col)
            # (i, j) -> (i, j+1) -> (i+1, j+1) winds counter-clockwise seen from outside.
            mb.add_tri(b, b + 1, b + 2, mat)
            mb.add_tri(b, b + 2, b + 3, mat)


def random_waves(rng: np.random.Generator, n: int, amp: float) -> np.ndarray:
    k = rng.normal(0.0, 2.2, (n, 3))
    return np.column_stack([k, rng.uniform(0.0, 2.0 * math.pi, n), rng.uniform(0.3, 1.0, n) * amp / n * 2.0])


def nearest_point(points: np.ndarray, p: np.ndarray) -> np.ndarray:
    return points[int(np.argmin(np.linalg.norm(points - p, axis=1)))]
