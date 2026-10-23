"""Shared helpers for the Haluna procedural kit (M1-ENV-01, SPEC §7.4, ADR 0005).

Pure numpy geometry (bpy is imported lazily by `export_glb`), so the unit tests and `--dry-run` work
without Blender. Every random choice comes from `rng_for(piece, seed)` in a fixed order, so a rebuild
is byte-identical.

Coordinates are **Godot's**: metres, +Y up, +X east, -Z north (art README convention 6). The export
converts to Blender (+Z up) and the glTF exporter converts back, so what is written here is what
Godot imports.

Per-vertex channels (art README convention 3, haluna.md §4):
  COLOR_0.r  moss / lichen weight      0 bare .. 1 mossy (inland, shaded, upward-facing)
  COLOR_0.g  salt-crust weight         0 none .. 1 heavy (spray zone; the shader also bands by height)
  COLOR_0.b  wet / splash weight       0 dry .. 1 soaked (puddles, splash; the tide line adds more live)
  COLOR_0.a  erosion / edge wear       0 crisp .. 1 rounded, pitted, lightened (curvature x noise)
  UV2.x      baked occlusion           1 open .. 0 deep crevice
  UV2.y      per-element variation     0..1 random per block / plank / shell (tint and value shift)

Weathering parameters (`Weathering`) scale those channels per piece, so the same generator yields a
fresh piece (the tended Shell Shrine) or a drowned ruin (the Lit Age fragments).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

UP = np.array([0.0, 1.0, 0.0])


# ---------------------------------------------------------------------------------------------
# Deterministic randomness
# ---------------------------------------------------------------------------------------------
def rng_for(piece: str, seed: int) -> np.random.Generator:
    """numpy PCG64 seeded from the piece name and seed (no Python hash() randomisation)."""
    salt = sum((i + 1) * ord(ch) for i, ch in enumerate(piece))
    return np.random.default_rng(np.random.SeedSequence([seed, salt]))


@dataclass(frozen=True)
class Weathering:
    """Per-piece weathering parameters written into the vertex colours (all 0..1 multipliers)."""

    moss: float = 0.5  # R: how much moss/lichen the piece may carry where the rules allow it
    salt: float = 0.5  # G: salt crust in crevices
    wet: float = 0.0  # B: painted wetness (splash, puddles); the tide line is added in the shader
    erosion: float = 0.5  # A: edge rounding and pitting
    noise_scale_m: float = 0.6  # period of the breakup noise


FRESH = Weathering(moss=0.15, salt=0.2, wet=0.0, erosion=0.25)
VILLAGE = Weathering(moss=0.3, salt=0.45, wet=0.0, erosion=0.5)
DROWNED = Weathering(moss=0.25, salt=0.9, wet=0.35, erosion=0.95)


# ---------------------------------------------------------------------------------------------
# Small 3D value noise (deterministic, vectorised) for displacement and channel breakup
# ---------------------------------------------------------------------------------------------
class Noise3:
    """Value noise on a hashed 64^3 lattice; fbm() returns values in [0, 1]."""

    SIZE = 64

    def __init__(self, rng: np.random.Generator):
        self.table = rng.random((self.SIZE, self.SIZE, self.SIZE))

    def value(self, p: np.ndarray) -> np.ndarray:
        p = np.asarray(p, dtype=float)
        i = np.floor(p).astype(np.int64)
        f = p - i
        f = f * f * f * (f * (f * 6.0 - 15.0) + 10.0)
        n = self.SIZE
        out = np.zeros(p.shape[:-1])
        for dx in (0, 1):
            wx = f[..., 0] if dx else 1.0 - f[..., 0]
            for dy in (0, 1):
                wy = f[..., 1] if dy else 1.0 - f[..., 1]
                for dz in (0, 1):
                    wz = f[..., 2] if dz else 1.0 - f[..., 2]
                    v = self.table[(i[..., 0] + dx) % n, (i[..., 1] + dy) % n, (i[..., 2] + dz) % n]
                    out += v * wx * wy * wz
        return out

    def fbm(self, p: np.ndarray, octaves: int = 3, gain: float = 0.5) -> np.ndarray:
        total = np.zeros(np.shape(p)[:-1])
        amp, norm, q = 1.0, 0.0, np.asarray(p, dtype=float)
        for k in range(octaves):
            total += amp * self.value(q + k * 17.31)
            norm += amp
            amp *= gain
            q = q * 2.03
        return total / norm


# ---------------------------------------------------------------------------------------------
# Vector helpers
# ---------------------------------------------------------------------------------------------
def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


def rot_y(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


def rot_x(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def rot_z(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def smoothstep(e0: float, e1: float, x):
    t = np.clip((np.asarray(x, dtype=float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def any_perpendicular(v: np.ndarray) -> np.ndarray:
    ref = np.array([1.0, 0.0, 0.0]) if abs(v[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    return normalize(np.cross(v, ref))


# ---------------------------------------------------------------------------------------------
# Mesh builder (indexed; vertices are shared inside a grid so normals stay smooth)
# ---------------------------------------------------------------------------------------------
@dataclass
class MeshBuilder:
    name: str
    pos: list = field(default_factory=list)
    nrm: list = field(default_factory=list)
    uv: list = field(default_factory=list)
    uv2: list = field(default_factory=list)
    col: list = field(default_factory=list)
    tris: list = field(default_factory=list)
    tri_mat: list = field(default_factory=list)
    materials: list = field(default_factory=list)

    def material(self, name: str) -> int:
        if name not in self.materials:
            self.materials.append(name)
        return self.materials.index(name)

    @property
    def vertex_count(self) -> int:
        return len(self.pos)

    @property
    def triangle_count(self) -> int:
        return len(self.tris)

    def add_vertices(self, p, n, uv, uv2, col) -> int:
        base = len(self.pos)
        p = np.asarray(p, dtype=float).reshape(-1, 3)
        k = len(p)
        self.pos.extend(p.tolist())
        self.nrm.extend(normalize(np.broadcast_to(np.asarray(n, dtype=float).reshape(-1, 3), (k, 3))).tolist())
        self.uv.extend(np.broadcast_to(np.asarray(uv, dtype=float).reshape(-1, 2), (k, 2)).tolist())
        self.uv2.extend(np.broadcast_to(np.asarray(uv2, dtype=float).reshape(-1, 2), (k, 2)).tolist())
        self.col.extend(np.clip(np.broadcast_to(np.asarray(col, dtype=float).reshape(-1, 4), (k, 4)), 0, 1).tolist())
        return base

    def add_tri(self, a: int, b: int, c: int, mat: int) -> None:
        self.tris.append((a, b, c))
        self.tri_mat.append(mat)

    def add_grid_indices(self, base: int, rows: int, cols: int, mat: int, flip: bool = False) -> None:
        for r in range(rows - 1):
            for c in range(cols - 1):
                a = base + r * cols + c
                b, cc, d = a + 1, a + cols + 1, a + cols
                if flip:
                    self.add_tri(a, cc, b, mat)
                    self.add_tri(a, d, cc, mat)
                else:
                    self.add_tri(a, b, cc, mat)
                    self.add_tri(a, cc, d, mat)

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        p = np.asarray(self.pos)
        return p.min(axis=0), p.max(axis=0)

    def merge(self, other: "MeshBuilder", xform: np.ndarray | None = None, offset=(0.0, 0.0, 0.0)) -> None:
        """Appends another builder (optionally rotated by a 3x3 and offset), remapping materials."""
        rot = np.eye(3) if xform is None else np.asarray(xform, dtype=float)
        if not other.pos:
            return
        p = np.asarray(other.pos) @ rot.T + np.asarray(offset, dtype=float)
        n = np.asarray(other.nrm) @ rot.T
        base = self.add_vertices(p, n, other.uv, other.uv2, other.col)
        remap = [self.material(m) for m in other.materials]
        for (a, b, c), m in zip(other.tris, other.tri_mat):
            self.add_tri(a + base, b + base, c + base, remap[m])


def recompute_normals(mb: MeshBuilder, start_vertex: int = 0, start_tri: int = 0) -> None:
    """Area-weighted smooth normals over vertices [start_vertex:], welding coincident positions."""
    pos = np.asarray(mb.pos[start_vertex:], dtype=float)
    if len(pos) == 0:
        return
    tris = np.asarray(mb.tris[start_tri:], dtype=np.int64) - start_vertex
    tris = tris[(tris >= 0).all(axis=1)]
    key = np.round(pos * 2000.0).astype(np.int64)
    _, weld = np.unique(key, axis=0, return_inverse=True)
    weld = weld.reshape(-1)
    acc = np.zeros((weld.max() + 1, 3))
    a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
    fn = np.cross(b - a, c - a)
    for k in range(3):
        np.add.at(acc, weld[tris[:, k]], fn)
    n = normalize(acc[weld])
    mb.nrm[start_vertex:] = n.tolist()


# ---------------------------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------------------------
def rounded_block(mb: MeshBuilder, center, half, mat: int, *, rot=None, radius: float = 0.04, seg: int = 3,
                  noise: Noise3 | None = None, disp_m: float = 0.0, disp_period_m: float = 0.25,
                  weather: Weathering = VILLAGE, variation: float = 0.5, uv_scale: float = 1.0,
                  wet_bias: float = 0.0) -> None:
    """A displaced rounded box (one dry-stacked coral block, a slab, a plank).

    Six seg x seg grids are projected onto a rounded box (SDF-style), displaced along the normal by
    fbm, and smooth-shaded. Vertex colours: erosion is high on the rounded edges and corners, moss on
    the top face, salt in the lower corners (crevices); UV2.x darkens towards the bottom and the
    joints; UV2.y carries `variation`."""
    half = np.asarray(half, dtype=float)
    r = float(min(radius, half.min() * 0.95))
    inner = half - r
    rot = np.eye(3) if rot is None else np.asarray(rot, dtype=float)
    center = np.asarray(center, dtype=float)
    faces = [
        (np.array([1, 0, 0]), np.array([0, 0, -1]), np.array([0, 1, 0])),
        (np.array([-1, 0, 0]), np.array([0, 0, 1]), np.array([0, 1, 0])),
        (np.array([0, 1, 0]), np.array([1, 0, 0]), np.array([0, 0, -1])),
        (np.array([0, -1, 0]), np.array([1, 0, 0]), np.array([0, 0, 1])),
        (np.array([0, 0, 1]), np.array([1, 0, 0]), np.array([0, 1, 0])),
        (np.array([0, 0, -1]), np.array([-1, 0, 0]), np.array([0, 1, 0])),
    ]
    start_v, start_t = mb.vertex_count, mb.triangle_count
    t = np.linspace(-1.0, 1.0, seg + 1)
    # Bias the grid towards the edges so the rounding gets the vertices.
    t = np.sign(t) * np.abs(t) ** 0.7
    U, V = np.meshgrid(t, t)
    for nrm, ua, va in faces:
        q = (nrm[None, None, :] + U[..., None] * ua + V[..., None] * va) * half
        core = np.clip(q, -inner, inner)
        d = normalize(q - core)
        local = core + d * r
        n_local = d
        world = local @ rot.T + center
        n_world = n_local @ rot.T
        if noise is not None and disp_m > 0.0:
            amp = noise.fbm(world / disp_period_m, 3) - 0.5
            world = world + n_world * (amp[..., None] * disp_m)
        edge = np.clip(np.linalg.norm(q - core, axis=-1) / max(r, 1e-6), 0, 1)
        corner = np.clip((np.abs(q) / half).max(axis=-1) - 0.0, 0, 1)
        breakup = noise.fbm(world / weather.noise_scale_m, 2) if noise is not None else np.full(U.shape, 0.5)
        up = n_world[..., 1]
        erosion = np.clip(weather.erosion * (0.35 + 0.65 * edge) * (0.6 + 0.8 * breakup), 0, 1)
        moss = np.clip(weather.moss * smoothstep(0.3, 0.9, up) * (0.4 + 1.2 * breakup), 0, 1)
        low = 1.0 - (local[..., 1] + half[1]) / (2.0 * half[1])
        salt = np.clip(weather.salt * (0.3 + 0.7 * low * corner) * (0.5 + breakup), 0, 1)
        wet = np.clip(weather.wet * (0.5 + breakup) + wet_bias, 0, 1)
        ao = np.clip(1.0 - 0.45 * low ** 2 - 0.25 * edge * (up < 0.2), 0.25, 1.0)
        col = np.stack([moss, salt, wet, erosion], axis=-1)
        uv2 = np.stack([ao, np.full(U.shape, variation)], axis=-1)
        # Box-projected UVs (the Low tier uses them; High/Ultra are triplanar).
        uvp = np.stack([local @ ua, local @ va], axis=-1) * uv_scale
        uvp = uvp + variation * 3.7
        base = mb.add_vertices(world.reshape(-1, 3), n_world.reshape(-1, 3), uvp.reshape(-1, 2), uv2.reshape(-1, 2),
                               col.reshape(-1, 4))
        mb.add_grid_indices(base, seg + 1, seg + 1, mat)
    recompute_normals(mb, start_v, start_t)


def tube(mb: MeshBuilder, centers: np.ndarray, radii, sides: int, mat: int, *, weather: Weathering = VILLAGE,
         noise: Noise3 | None = None, disp_m: float = 0.0, disp_period_m: float = 0.2, variation: float = 0.5,
         v_scale: float = 1.0, u_repeat: float = 1.0, cap_start: bool = False, cap_end: bool = False,
         first_normal=None, ao_base: float = 1.0) -> None:
    """Generalised cylinder along a polyline (posts, poles, rebar, booms). UV u around, v along (m)."""
    centers = np.asarray(centers, dtype=float)
    radii = np.broadcast_to(np.asarray(radii, dtype=float), (len(centers),))
    tang = np.zeros_like(centers)
    tang[1:-1] = centers[2:] - centers[:-2]
    tang[0] = centers[1] - centers[0]
    tang[-1] = centers[-1] - centers[-2]
    tang = normalize(tang)
    nrm = np.zeros_like(centers)
    nrm[0] = any_perpendicular(tang[0]) if first_normal is None else normalize(np.asarray(first_normal, float))
    for i in range(1, len(centers)):
        n = nrm[i - 1] - tang[i] * np.dot(nrm[i - 1], tang[i])
        nrm[i] = normalize(n) if np.linalg.norm(n) > 1e-9 else any_perpendicular(tang[i])
    bin_ = np.cross(tang, nrm)
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    n_rings = len(centers)
    p = np.zeros((n_rings, sides + 1, 3))
    nn = np.zeros_like(p)
    for i in range(n_rings):
        dirs = np.outer(np.cos(ang), nrm[i]) + np.outer(np.sin(ang), bin_[i])
        p[i] = centers[i] + dirs * radii[i]
        nn[i] = dirs
    if noise is not None and disp_m > 0.0:
        amp = noise.fbm(p / disp_period_m, 3) - 0.5
        amp[:, -1] = amp[:, 0]
        p = p + nn * (amp[..., None] * disp_m)
    seglen = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(centers, axis=0), axis=1))])
    u = np.tile((ang / (2.0 * math.pi))[None, :] * u_repeat, (n_rings, 1))
    v = np.tile(seglen[:, None] * v_scale, (1, sides + 1))
    uv = np.stack([u + variation * 5.3, v], axis=-1)
    breakup = noise.fbm(p / weather.noise_scale_m, 2) if noise is not None else np.full(u.shape, 0.5)
    up = nn[..., 1]
    frac = np.tile((seglen / max(seglen[-1], 1e-6))[:, None], (1, sides + 1))
    col = np.stack([
        np.clip(weather.moss * smoothstep(0.2, 0.9, up) * (0.4 + breakup), 0, 1),
        np.clip(weather.salt * (0.3 + breakup * 0.7) * (1.0 - frac * 0.5), 0, 1),
        np.clip(weather.wet * breakup, 0, 1),
        np.clip(weather.erosion * (0.4 + 0.6 * breakup), 0, 1),
    ], axis=-1)
    uv2 = np.stack([np.full(u.shape, ao_base), np.full(u.shape, variation)], axis=-1)
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(p.reshape(-1, 3), nn.reshape(-1, 3), uv.reshape(-1, 2), uv2.reshape(-1, 2),
                           col.reshape(-1, 4))
    mb.add_grid_indices(base, n_rings, sides + 1, mat)
    for cap, idx, sgn in ((cap_start, 0, -1.0), (cap_end, n_rings - 1, 1.0)):
        if not cap:
            continue
        ring = p[idx, :-1]
        c = ring.mean(axis=0)
        cb = mb.add_vertices(np.vstack([ring, c[None]]), np.tile(tang[idx] * sgn, (sides + 1, 1)),
                             np.vstack([uv[idx, :-1], uv[idx, :1]]), np.tile(uv2[idx, 0], (sides + 1, 1)),
                             np.tile(col[idx, 0], (sides + 1, 1)))
        for s in range(sides):
            if sgn > 0:
                mb.add_tri(cb + s, cb + (s + 1) % sides, cb + sides, mat)
            else:
                mb.add_tri(cb + (s + 1) % sides, cb + s, cb + sides, mat)
    del start_v, start_t


def quad_strip(mb: MeshBuilder, grid: np.ndarray, mat: int, *, uv: np.ndarray, col, uv2, flip: bool = False,
               smooth: bool = True) -> None:
    """A (rows, cols, 3) grid of points as one surface (roofs, sails, nets, shells)."""
    rows, cols = grid.shape[:2]
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(grid.reshape(-1, 3), np.tile(UP, (rows * cols, 1)), np.asarray(uv).reshape(-1, 2),
                           np.broadcast_to(np.asarray(uv2, float), (rows, cols, 2)).reshape(-1, 2),
                           np.broadcast_to(np.asarray(col, float), (rows, cols, 4)).reshape(-1, 4))
    mb.add_grid_indices(base, rows, cols, mat, flip=flip)
    if smooth:
        recompute_normals(mb, start_v, start_t)


def polygon_prism(mb: MeshBuilder, outline: np.ndarray, y0: float, y1: float, mat: int, *, col, uv2,
                  uv_scale: float = 1.0, top: bool = True, bottom: bool = False) -> None:
    """Extrudes a convex XZ outline (x, z pairs, either winding) between heights y0 and y1 (flat sides)."""
    outline = np.asarray(outline, dtype=float)
    n = len(outline)
    # Orient so cross(edge, up) points outward: the signed area in (x, z) must be negative.
    area = 0.5 * float(np.sum(outline[:, 0] * np.roll(outline[:, 1], -1) - np.roll(outline[:, 0], -1) * outline[:, 1]))
    if area > 0.0:
        outline = outline[::-1].copy()
    col = np.asarray(col, float)
    uv2 = np.asarray(uv2, float)
    for i in range(n):
        a, b = outline[i], outline[(i + 1) % n]
        edge = np.array([b[0] - a[0], 0.0, b[1] - a[1]])
        out = normalize(np.cross(edge, UP))
        ln = float(np.linalg.norm(edge))
        p = np.array([[a[0], y0, a[1]], [b[0], y0, b[1]], [b[0], y1, b[1]], [a[0], y1, a[1]]])
        uv = np.array([[0, y0], [ln, y0], [ln, y1], [0, y1]]) * uv_scale
        base = mb.add_vertices(p, np.tile(out, (4, 1)), uv, np.tile(uv2, (4, 1)), np.tile(col, (4, 1)))
        mb.add_tri(base, base + 1, base + 2, mat)
        mb.add_tri(base, base + 2, base + 3, mat)
    for flag, y, nrm in ((top, y1, UP), (bottom, y0, -UP)):
        if not flag:
            continue
        p = np.column_stack([outline[:, 0], np.full(n, y), outline[:, 1]])
        uv = outline * uv_scale
        base = mb.add_vertices(p, np.tile(nrm, (n, 1)), uv, np.tile(uv2, (n, 1)), np.tile(col, (n, 1)))
        for i in range(1, n - 1):
            if nrm[1] > 0:
                mb.add_tri(base, base + i, base + i + 1, mat)
            else:
                mb.add_tri(base, base + i + 1, base + i, mat)


def plank(mb: MeshBuilder, a, b, width: float, thick: float, mat: int, *, up=UP, weather: Weathering = VILLAGE,
          variation: float = 0.5, noise: Noise3 | None = None, sag_m: float = 0.0, seg: int = 1) -> None:
    """A board from point a to b (centre line), `width` across, `thick` along `up`. UV v runs along it."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    along = b - a
    length = float(np.linalg.norm(along))
    t = along / max(length, 1e-9)
    upv = normalize(np.asarray(up, float) - t * np.dot(up, t))
    side = np.cross(t, upv)
    s = np.linspace(0.0, 1.0, seg + 1)
    sag = -4.0 * sag_m * s * (1.0 - s)
    hw, ht = width * 0.5, thick * 0.5
    # Rectangle cross-section corners (side, up) with a tiny chamfer so edges catch light.
    ch = min(hw, ht) * 0.3
    prof = np.array([[hw, ht - ch], [hw - ch, ht], [-hw + ch, ht], [-hw, ht - ch], [-hw, -ht + ch], [-hw + ch, -ht],
                     [hw - ch, -ht], [hw, -ht + ch]])
    pn = normalize(np.array([[1, 0.4], [0.4, 1], [-0.4, 1], [-1, 0.4], [-1, -0.4], [-0.4, -1], [0.4, -1], [1, -0.4]]))
    rows = []
    nrows = []
    for k, sk in enumerate(s):
        c = a + along * sk + upv * sag[k]
        rows.append(c + prof[:, :1] * side + prof[:, 1:] * upv)
        nrows.append(pn[:, :1] * side + pn[:, 1:] * upv)
    p = np.asarray(rows)
    nn = np.asarray(nrows)
    p = np.concatenate([p, p[:, :1]], axis=1)
    nn = np.concatenate([nn, nn[:, :1]], axis=1)
    k_ = p.shape[1]
    u = np.linspace(0.0, 1.0, k_)[None, :] * (width + thick) * 2.0
    v = (s * length)[:, None]
    uv = np.stack([np.broadcast_to(u + variation * 7.1, p.shape[:2]), np.broadcast_to(v, p.shape[:2])], axis=-1)
    breakup = noise.fbm(p / weather.noise_scale_m, 2) if noise is not None else np.full(p.shape[:2], 0.5)
    upness = nn[..., 1]
    col = np.stack([
        np.clip(weather.moss * smoothstep(0.3, 0.9, upness) * breakup, 0, 1),
        np.clip(weather.salt * breakup, 0, 1),
        np.clip(weather.wet * breakup, 0, 1),
        np.clip(weather.erosion * (0.5 + 0.5 * breakup), 0, 1),
    ], axis=-1)
    uv2 = np.stack([np.clip(0.75 + 0.25 * upness, 0.3, 1.0), np.full(p.shape[:2], variation)], axis=-1)
    base = mb.add_vertices(p.reshape(-1, 3), nn.reshape(-1, 3), uv.reshape(-1, 2), uv2.reshape(-1, 2),
                           col.reshape(-1, 4))
    mb.add_grid_indices(base, seg + 1, k_, mat, flip=True)
    # End caps.
    for idx, sgn in ((0, -1.0), (seg, 1.0)):
        ring = p[idx, :-1]
        c = ring.mean(axis=0)
        cb = mb.add_vertices(np.vstack([ring, c[None]]), np.tile(t * sgn, (9, 1)), np.zeros((9, 2)),
                             np.tile(uv2[idx, 0], (9, 1)), np.tile(col[idx, 0], (9, 1)))
        for q in range(8):
            if sgn > 0:
                mb.add_tri(cb + (q + 1) % 8, cb + q, cb + 8, mat)
            else:
                mb.add_tri(cb + q, cb + (q + 1) % 8, cb + 8, mat)


# ---------------------------------------------------------------------------------------------
# Blender export (imports bpy lazily)
# ---------------------------------------------------------------------------------------------
def _to_blender_object(mb: MeshBuilder, extras: dict | None):
    import bpy  # noqa: PLC0415  (only inside Blender)

    me = bpy.data.meshes.new(mb.name)
    pos = np.asarray(mb.pos, dtype=np.float64)
    bpos = np.column_stack([pos[:, 0], -pos[:, 2], pos[:, 1]])  # Godot (x, y, z) -> Blender (x, -z, y)
    tris = np.asarray(mb.tris, dtype=np.int64)
    me.vertices.add(len(pos))
    me.vertices.foreach_set("co", bpos.astype(np.float32).ravel())
    me.loops.add(len(tris) * 3)
    me.loops.foreach_set("vertex_index", tris.astype(np.int32).ravel())
    me.polygons.add(len(tris))
    me.polygons.foreach_set("loop_start", (np.arange(len(tris)) * 3).astype(np.int32))
    me.polygons.foreach_set("material_index", np.asarray(mb.tri_mat, dtype=np.int32))
    me.update(calc_edges=True)
    me.validate(clean_customdata=False)
    loop_v = tris.ravel()
    uv0 = np.asarray(mb.uv, dtype=np.float64)[loop_v].copy()
    uv1 = np.asarray(mb.uv2, dtype=np.float64)[loop_v].copy()
    uv0[:, 1] = 1.0 - uv0[:, 1]
    uv1[:, 1] = 1.0 - uv1[:, 1]
    lay0 = me.uv_layers.new(name="UVMap")
    lay0.data.foreach_set("uv", uv0.astype(np.float32).ravel())
    lay1 = me.uv_layers.new(name="UV2")
    lay1.data.foreach_set("uv", uv1.astype(np.float32).ravel())
    me.uv_layers.active = lay0
    ca = me.color_attributes.new("Weathering", "FLOAT_COLOR", "POINT")
    ca.data.foreach_set("color", np.asarray(mb.col, dtype=np.float32).ravel())
    me.color_attributes.active_color = ca
    for name in mb.materials:
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        me.materials.append(mat)
    nrm = np.asarray(mb.nrm, dtype=np.float64)
    bn = np.column_stack([nrm[:, 0], -nrm[:, 2], nrm[:, 1]])
    me.normals_split_custom_set_from_vertices(bn.astype(np.float32).tolist())
    ob = bpy.data.objects.new(mb.name, me)
    for k, v in (extras or {}).items():
        ob[k] = v
    bpy.context.scene.collection.objects.link(ob)
    return ob


def export_glb(builders: list[MeshBuilder], out_path: str, extras: dict | None = None) -> None:
    """Writes the builders as separate objects (LODs: `<name>`, `<name>-lod1`) into one .glb.
    `extras` become glTF node extras (Godot imports them as node metadata), e.g. {"placeholder": "..."}."""
    import bpy  # noqa: PLC0415

    bpy.ops.wm.read_factory_settings(use_empty=True)
    for mb in builders:
        _to_blender_object(mb, extras)
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_texcoords=True,
        export_normals=True,
        export_tangents=True,
        export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
        export_materials="EXPORT",
        export_image_format="NONE",
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_extras=bool(extras),
    )


def summary(builders: list[MeshBuilder]) -> dict:
    return {mb.name: {"triangles": mb.triangle_count, "vertices": mb.vertex_count} for mb in builders}
