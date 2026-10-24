"""Shared helpers for the Oruvel Underway kit (M3-ENV-05; docs/kb/art/environments/oruvel_underway.md).

The geometry core is the Haluna kit's (assets_src/environments/kits/haluna/kit_common.py: MeshBuilder, the
weathering channels, the primitives, the glTF export), imported read-only, as the Brine Shoals kit does.
Coordinates are Godot's (metres, +Y up, +X east, -Z north). Vertex colours follow haluna.md §4: R moss, G salt,
B wet, A erosion. Everything in this kit is under water, so B (wet) is 1 and R/G stay 0; growth comes from the
weathering shader's algae and barnacle layers over the whole depth range, and from the coral pieces.

This module adds: the kit's material slots (`ou_*`, written by ou_materials.py), heightfield and lathe surfaces,
a periodic noise sample (so tiling edges match), the seeded **growth field** that re-slots triangles to coral or
patina (per triangle, like the Brine Shoals char field), and the small reef generators (coral knobs, branching
coral, fans) that the tower, Lit Age and growth pieces all dress with.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HALUNA = HERE.parent / "haluna"
if str(HALUNA) not in sys.path:
    sys.path.insert(0, str(HALUNA))

import kit_common as kc  # noqa: E402  (the Haluna kit's core, read-only)

# ---------------------------------------------------------------------------------------------
# Material slots (ou_materials.py writes one .tres per slot)
# ---------------------------------------------------------------------------------------------
M_CONCRETE = "ou_concrete"
M_CONCRETE_DRY = "ou_concrete_dry"
M_CALCITE = "ou_calcite"
M_CERAMIC = "ou_ceramic"
M_SILT = "ou_silt"
M_REBAR = "ou_rebar"
M_IRON = "ou_iron"
M_BRASS = "ou_brass"
M_PATINA = "ou_patina"
M_GLASS_DARK = "ou_glass_dark"
M_TIMBER_TAR = "ou_timber_tar"
M_HULL = "ou_hull"
M_CORAL_BONE = "ou_coral_bone"
M_CORAL_OCHRE = "ou_coral_ochre"
M_CORAL_ROSE = "ou_coral_rose"
M_CORAL_TEAL = "ou_coral_teal"
M_SPONGE = "ou_sponge"
M_SEAGRASS = "ou_seagrass"
M_SEAGRASS_TIP = "ou_seagrass_tip"
M_WEED = "ou_weed"
M_CORD_OLD = "ou_cord_old"
M_CORD_NEW = "ou_cord_new"
M_LEAD = "ou_lead"
M_FLAME = "ou_flame"
M_LANTERN_GLASS = "ou_lantern_glass"

CORALS = (M_CORAL_OCHRE, M_CORAL_ROSE, M_CORAL_BONE, M_CORAL_TEAL, M_SPONGE)

# Weathering presets (vertex-colour multipliers, kit_common.Weathering): wet everywhere, no moss or salt.
DROWNED = kc.Weathering(moss=0.0, salt=0.0, wet=1.0, erosion=0.9, noise_scale_m=0.8)
CAST = kc.Weathering(moss=0.0, salt=0.0, wet=1.0, erosion=0.6, noise_scale_m=0.6)
DRY = kc.Weathering(moss=0.0, salt=0.55, wet=0.0, erosion=0.5, noise_scale_m=0.5)
REEF = kc.Weathering(moss=0.0, salt=0.0, wet=1.0, erosion=0.4, noise_scale_m=0.3)

LOD = "-lod1"
UP = kc.UP


def finalize(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Merges duplicate slots and drops unused ones (keeps first-use order)."""
    uniq: list[str] = []
    for n in mb.materials:
        if n not in uniq:
            uniq.append(n)
    remap = [uniq.index(n) for n in mb.materials]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    mb.materials = uniq
    used = sorted(set(mb.tri_mat))
    if len(used) != len(mb.materials):
        keep = {old: new for new, old in enumerate(used)}
        mb.materials = [mb.materials[i] for i in used]
        mb.tri_mat = [keep[m] for m in mb.tri_mat]
    return mb


def periodic(noise: kc.Noise3, x, y, z, period: float, scale: float, octaves: int = 3) -> np.ndarray:
    """fBm that repeats every `period` metres in x (x is wrapped onto a circle), in [0, 1]."""
    x = np.asarray(x, float)
    a = 2.0 * math.pi * x / period
    r = period / (2.0 * math.pi) / scale
    p = np.stack([np.cos(a) * r, np.asarray(y, float) / scale + 0.0 * x, np.sin(a) * r + np.asarray(z, float) / scale],
                 axis=-1)
    return noise.fbm(p, octaves)


def edge_fade(X: np.ndarray, Z: np.ndarray, half: float, band: float) -> np.ndarray:
    """1 inside, falling to 0 at the cell edge (|x| or |z| = half) over `band` metres, so cells tile at y 0."""
    return kc.smoothstep(0.0, band, np.minimum(half - np.abs(X), half - np.abs(Z)))


# ---------------------------------------------------------------------------------------------
# Surfaces
# ---------------------------------------------------------------------------------------------
def heightfield(mb: kc.MeshBuilder, xs: np.ndarray, zs: np.ndarray, height, mat: int, *, erosion: float = 0.3,
                variation: float = 0.5, ao=None, keep=None, uv_scale: float = 1.0 / 3.0) -> None:
    """A (len(zs), len(xs)) grid surface y = height(X, Z), wet (VC.B 1). `ao(X, Z, Y)` -> UV2.x;
    `keep(X, Z)` (bool grid) drops quads (holes)."""
    X, Z = np.meshgrid(xs, zs)
    Y = height(X, Z)
    P = np.stack([X, Y, Z], axis=-1)
    col = np.stack([np.zeros_like(X), np.zeros_like(X), np.ones_like(X), np.full_like(X, erosion)], axis=-1)
    occ = np.clip(ao(X, Z, Y), 0.2, 1.0) if ao is not None else np.ones_like(X)
    uv2 = np.stack([occ, np.full_like(X, variation)], axis=-1)
    uv = np.stack([X, Z], axis=-1) * uv_scale
    rows, cols = X.shape
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(P.reshape(-1, 3), np.tile(UP, (rows * cols, 1)), uv.reshape(-1, 2), uv2.reshape(-1, 2),
                           col.reshape(-1, 4))
    k = keep(X, Z) if keep is not None else None
    for r in range(rows - 1):
        for c in range(cols - 1):
            if k is not None and not (k[r, c] and k[r, c + 1] and k[r + 1, c] and k[r + 1, c + 1]):
                continue
            a = base + r * cols + c
            b, cc, d = a + 1, a + cols + 1, a + cols
            mb.add_tri(a, d, cc, mat)  # counter-clockwise seen from above (+Y up, -Z north)
            mb.add_tri(a, cc, b, mat)
    kc.recompute_normals(mb, start_v, start_t)


def lathe(mb: kc.MeshBuilder, profile, mat: int, *, sides: int = 16, center=(0.0, 0.0, 0.0), rfun=None,
          weather: kc.Weathering = CAST, variation: float = 0.5, noise: kc.Noise3 | None = None,
          disp_m: float = 0.0, xform=None) -> None:
    """A surface of revolution about +Y from a (r, y) profile listed bottom to top; normals face outward.
    `rfun(theta, y)` multiplies the radius (flutes). `xform` (3x3) rotates it about `center`."""
    prof = np.asarray(profile, float)
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    R = prof[:, 0][:, None] * np.ones_like(ang)[None, :]
    Y = prof[:, 1][:, None] * np.ones_like(ang)[None, :]
    if rfun is not None:
        R = R * rfun(ang[None, :], Y)
    P = np.stack([R * np.cos(ang)[None, :], Y, -R * np.sin(ang)[None, :]], axis=-1)
    if noise is not None and disp_m > 0.0:
        radial = kc.normalize(P * np.array([1.0, 0.0, 1.0]) + 1e-9)
        amp = noise.fbm(P / 0.25, 3) - 0.5
        amp[:, -1] = amp[:, 0]
        P = P + radial * (amp[..., None] * disp_m)
    if xform is not None:
        P = P @ np.asarray(xform, float).T
    P = P + np.asarray(center, float)
    seg = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))])
    uv = np.stack([np.tile(ang / (2 * math.pi) * 2.0, (len(prof), 1)) + variation * 3.1,
                   np.tile(seg[:, None], (1, sides + 1))], axis=-1)
    br = noise.fbm(P / weather.noise_scale_m, 2) if noise is not None else np.full(R.shape, 0.5)
    col = np.stack([np.zeros_like(R), np.zeros_like(R), np.full_like(R, weather.wet),
                    np.clip(weather.erosion * (0.4 + 0.6 * br), 0, 1)], axis=-1)
    uv2 = np.stack([np.ones_like(R), np.full_like(R, variation)], axis=-1)
    kc.quad_strip(mb, P, mat, uv=uv, col=col, uv2=uv2, flip=False)


def two_sided(mb: kc.MeshBuilder, start_v: int, start_t: int) -> None:
    """Duplicates the triangles (and vertices, with flipped normals) added since (start_v, start_t) with the
    opposite winding, for thin sheets drawn by back-face-culled shaders (fans, curtains)."""
    pos = np.asarray(mb.pos[start_v:])
    nrm = -np.asarray(mb.nrm[start_v:])
    base = mb.add_vertices(pos, nrm, mb.uv[start_v:start_v + len(pos)], mb.uv2[start_v:start_v + len(pos)],
                           mb.col[start_v:start_v + len(pos)])
    for (a, b, c), m in list(zip(mb.tris[start_t:], mb.tri_mat[start_t:])):
        mb.add_tri(a - start_v + base, c - start_v + base, b - start_v + base, m)


def sheet(mb: kc.MeshBuilder, grid: np.ndarray, mat: int, *, variation: float = 0.5, double: bool = True,
          weather: kc.Weathering = REEF) -> None:
    """A (rows, cols, 3) grid as a thin sheet, optionally two-sided."""
    rows, cols = grid.shape[:2]
    u, v = np.meshgrid(np.linspace(0, 1, cols), np.linspace(0, 1, rows))
    col = np.broadcast_to(np.array([0.0, 0.0, weather.wet, weather.erosion]), (rows, cols, 4))
    uv2 = np.broadcast_to(np.array([1.0, variation]), (rows, cols, 2))
    sv, st = mb.vertex_count, mb.triangle_count
    kc.quad_strip(mb, grid, mat, uv=np.stack([u, v], axis=-1), col=col, uv2=uv2)
    if double:
        two_sided(mb, sv, st)


def ribbon(mb: kc.MeshBuilder, pts: np.ndarray, width, side: np.ndarray, mats, *, variation: float = 0.5) -> None:
    """A flat strap along a polyline (seagrass, weed): `width` per point, `side` the across direction (unit),
    `mats` one slot per segment. One-sided: the materials draw both faces."""
    pts = np.asarray(pts, float)
    w = np.broadcast_to(np.asarray(width, float), (len(pts),))
    side = kc.normalize(np.asarray(side, float))
    left = pts - side * (w[:, None] * 0.5)
    right = pts + side * (w[:, None] * 0.5)
    tang = np.gradient(pts, axis=0)
    n = kc.normalize(np.cross(tang, side))
    nn = np.repeat(n, 2, axis=0)
    p = np.empty((2 * len(pts), 3))
    p[0::2], p[1::2] = left, right
    t = np.linspace(0.0, 1.0, len(pts))
    uv = np.stack([np.tile([0.0, 1.0], len(pts)), np.repeat(t, 2)], axis=-1)
    col = np.tile([0.0, 0.0, 1.0, 0.2], (len(p), 1))
    uv2 = np.column_stack([np.repeat(0.55 + 0.45 * t, 2), np.full(len(p), variation)])
    base = mb.add_vertices(p, nn, uv, uv2, col)
    for k in range(len(pts) - 1):
        m = mats[min(k, len(mats) - 1)]
        a, b, c, d = base + 2 * k, base + 2 * k + 1, base + 2 * k + 3, base + 2 * k + 2
        mb.add_tri(a, c, b, m)  # winds with n (tang x side)
        mb.add_tri(a, d, c, m)


def ring(mb: kc.MeshBuilder, center, radius: float, tube_r: float, mat: int, *, axis=(0.0, 1.0, 0.0), segs: int = 24,
         sides: int = 6, weather: kc.Weathering = CAST, variation: float = 0.5, arc: float = 2.0 * math.pi) -> None:
    """A torus (or an arc of one) of `radius` round `axis` through `center`."""
    axis = kc.normalize(np.asarray(axis, float))
    u = kc.any_perpendicular(axis)
    v = np.cross(axis, u)
    closed = arc >= 2.0 * math.pi - 1e-6
    t = np.linspace(0.0, arc, segs + 1)
    pts = np.asarray(center, float) + radius * (np.outer(np.cos(t), u) + np.outer(np.sin(t), v))
    if closed:
        pts[-1] = pts[0]
    kc.tube(mb, pts, tube_r, sides, mat, weather=weather, variation=variation, cap_start=not closed,
            cap_end=not closed)


def block(mb: kc.MeshBuilder, center, half, mat: int, *, rng, noise=None, rot=None, seg: int = 2, radius: float = 0.03,
          disp_m: float = 0.0, weather: kc.Weathering = DROWNED, period: float = 0.4) -> None:
    """kit_common.rounded_block with this kit's defaults."""
    kc.rounded_block(mb, center, half, mat, rot=rot, radius=radius, seg=seg, noise=noise, disp_m=disp_m,
                     disp_period_m=period, weather=weather, variation=float(rng.random()))


# ---------------------------------------------------------------------------------------------
# Growth: per-triangle re-slotting and the small reef generators
# ---------------------------------------------------------------------------------------------
def tri_centroids(mb: kc.MeshBuilder, start_tri: int = 0) -> np.ndarray:
    pos = np.asarray(mb.pos)
    t = np.asarray(mb.tris[start_tri:], dtype=np.int64)
    return pos[t].mean(axis=1)


def tri_normals(mb: kc.MeshBuilder, start_tri: int = 0) -> np.ndarray:
    pos = np.asarray(mb.pos)
    t = np.asarray(mb.tris[start_tri:], dtype=np.int64)
    return kc.normalize(np.cross(pos[t[:, 1]] - pos[t[:, 0]], pos[t[:, 2]] - pos[t[:, 0]]))


def patina(mb: kc.MeshBuilder, noise: kc.Noise3, *, start_tri: int = 0, amount: float = 0.45,
           from_slot: str = M_BRASS, to_slot: str = M_PATINA, scale: float = 0.18) -> None:
    """Re-slots brass triangles to verdigris by a noise field, undersides and low faces first."""
    if mb.triangle_count <= start_tri or from_slot not in mb.materials:
        return
    c = tri_centroids(mb, start_tri)
    n = tri_normals(mb, start_tri)
    f = noise.fbm(c / scale, 3) + 0.25 * (-n[:, 1]) + 0.1
    src, dst = mb.materials.index(from_slot), mb.material(to_slot)
    for k, level in enumerate(f):
        t = start_tri + k
        if mb.tri_mat[t] == src and level > 1.0 - amount:
            mb.tri_mat[t] = dst


def coral_knob(mb: kc.MeshBuilder, at, size: float, rng, noise, slot: str, *, squash: float = 0.6) -> None:
    """A small encrusting coral or sponge lump: a displaced, squashed sphere."""
    s = size * rng.uniform(0.7, 1.2)
    kc.rounded_block(mb, at, (s, s * squash, s * rng.uniform(0.8, 1.1)), mb.material(slot), radius=s, seg=3,
                     noise=noise, disp_m=s * 0.35, disp_period_m=max(s * 0.6, 0.02), weather=REEF,
                     variation=float(rng.random()), rot=kc.rot_y(rng.uniform(0, 6.28)))


def branch_coral(mb: kc.MeshBuilder, root, rng, slot: str, *, height: float = 0.35, depth: int = 3,
                 radius: float = 0.022, spread: float = 0.55) -> None:
    """Branching (staghorn-like) coral: tapering tubes that fork upward and outward."""
    mat = mb.material(slot)
    stack = [(np.asarray(root, float), np.array([0.0, 1.0, 0.0]), height, radius, depth)]
    while stack:
        p, d, ln, r, lvl = stack.pop()
        bend = kc.normalize(d + rng.normal(0, 0.18, 3) + np.array([0, 0.15, 0]))
        mid = p + d * ln * 0.5
        end = mid + bend * ln * 0.5
        kc.tube(mb, np.array([p, mid, end]), np.array([r, r * 0.85, r * 0.7]), 5, mat, weather=REEF,
                variation=float(rng.random()), cap_end=lvl <= 1)
        if lvl <= 1:
            continue
        for _k in range(2 if rng.random() < 0.7 else 3):
            nd = kc.normalize(bend + rng.normal(0, spread, 3) * np.array([1.0, 0.4, 1.0]))
            nd[1] = abs(nd[1]) * 0.8 + 0.25
            stack.append((end, kc.normalize(nd), ln * rng.uniform(0.55, 0.8), r * 0.72, lvl - 1))


def sea_fan(mb: kc.MeshBuilder, root, rng, slot: str, *, height: float = 0.5, width: float = 0.45, yaw: float = 0.0,
            lod: bool = False) -> None:
    """A gorgonian fan: a scalloped, slightly cupped two-sided sheet on a short stalk, facing the current."""
    rows, cols = (3, 4) if lod else (6, 9)
    v = np.linspace(0.0, 1.0, rows)[:, None]
    u = np.linspace(-1.0, 1.0, cols)[None, :]
    outline = np.sqrt(np.clip(1.0 - u ** 2, 0, 1)) * (0.6 + 0.4 * v)
    x = u * width * 0.5 * (0.35 + 0.65 * np.sin(v * math.pi * 0.9 + 0.2))
    y = v * height * (0.85 + 0.15 * outline)
    z = 0.06 * height * (u ** 2) + rng.normal(0, 0.008, (rows, cols))
    grid = np.stack([x, y + 0.04, z], axis=-1) @ kc.rot_y(yaw).T + np.asarray(root, float)
    sheet(mb, grid, mb.material(slot), variation=float(rng.random()))
    kc.tube(mb, np.array([root, np.asarray(root) + np.array([0, 0.06, 0])]), 0.012, 4, mb.material(slot),
            weather=REEF)
