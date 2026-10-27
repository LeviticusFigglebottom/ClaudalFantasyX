"""Shared helpers for the Brine Shoals kit (M3-ENV-02; docs/kb/art/environments/brine_shoals.md).

The geometry core is the Haluna kit's (assets_src/environments/kits/haluna/kit_common.py: MeshBuilder,
the weathering channels, the primitives, the glTF export), imported read-only. Coordinates are Godot's
(metres, +Y up, +X east, -Z north). Vertex colours follow haluna.md §4: R moss, G salt, B wet, A erosion.

This module adds what the shoals need on top: heightfield ground, the seeded **char field** that turns a
camp piece into its burned variant (per-triangle char / scorch slots, and holes burned through cloth),
and the slot renaming that gives every piece its own `bs_*` material slots (the kit's materials live in
assets/environments/kits/brine_shoals/materials/, one .tres per slot, so the import's `{asset_dir}`
slot rule finds them).
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
# Material slots (bs_materials.py writes one .tres per slot)
# ---------------------------------------------------------------------------------------------
M_MUD = "bs_mud"
M_GRIT = "bs_shell_grit"
M_TAR = "bs_timber_tar"
M_TIMBER = "bs_timber"
M_CHAR = "bs_char"
M_SCORCH = "bs_scorch"
M_CANVAS = "bs_canvas"
M_CANVAS_TEAL = "bs_canvas_teal"
M_CANVAS_SCORCHED = "bs_canvas_scorched"
M_ROPE = "bs_rope"
M_IRON = "bs_iron"
M_IRON_HOT = "bs_iron_hot"
M_BRASS = "bs_brass"
M_CERAMIC = "bs_lit_ceramic"
M_GLASS = "bs_glass"
M_GLASS_SOOT = "bs_glass_soot"
M_SALT = "bs_salt"
M_ASH = "bs_ash"
M_EMBER = "bs_ember"
M_LEAK = "bs_glimmer_leak"
M_WEED = "bs_weed"
M_BARGE = "bs_barge_white"
M_RED = "bs_lacquer_red"
M_GOLD = "bs_gold"
M_SMOKE = "bs_smoke"
M_SOOT = "bs_soot"
M_WAKE = "bs_wake"  # M3-ENV-1000 (bs_wake.py): env_boat_wake.gdshader

# Haluna generator slots reused by import -> this kit's slots.
RENAME = {
    "kit_timber": M_TIMBER,
    "kit_lashing": M_ROPE,
    "kit_cloth_sand": M_CANVAS,
    "kit_cloth": M_CANVAS,
    "kit_brass": M_BRASS,
    "kit_salt_glass": M_GLASS,
}

# Weathering presets (vertex-colour multipliers, kit_common.Weathering).
MUD_W = kc.Weathering(moss=0.0, salt=0.55, wet=0.45, erosion=0.3, noise_scale_m=2.0)
WRECK = kc.Weathering(moss=0.05, salt=0.7, wet=0.3, erosion=0.85)
CAMP = kc.Weathering(moss=0.0, salt=0.45, wet=0.0, erosion=0.55)
CLOTH = kc.Weathering(moss=0.0, salt=0.2, wet=0.0, erosion=0.3)

LOD = "-lod1"


def finalize(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Renames reused Haluna slots to this kit's and merges duplicate slots (keeps first-use order)."""
    names = [RENAME.get(m, m) for m in mb.materials]
    uniq: list[str] = []
    for n in names:
        if n not in uniq:
            uniq.append(n)
    remap = [uniq.index(n) for n in names]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    mb.materials = uniq
    # Drop slots no triangle uses (a burned variant may have charred every timber face).
    used = sorted(set(mb.tri_mat))
    if len(used) != len(mb.materials):
        keep = {old: new for new, old in enumerate(used)}
        mb.materials = [mb.materials[i] for i in used]
        mb.tri_mat = [keep[m] for m in mb.tri_mat]
    return mb


# ---------------------------------------------------------------------------------------------
# Heightfield ground
# ---------------------------------------------------------------------------------------------
def heightfield(mb: kc.MeshBuilder, xs: np.ndarray, zs: np.ndarray, height, mat: int, *, wet=None, salt=None,
                erosion: float = 0.3, variation: float = 0.5, ao=None, keep=None) -> None:
    """A (len(zs), len(xs)) grid surface y = height(X, Z). `wet`, `salt`, `ao` are optional functions of
    (X, Z, Y) giving the B, G channels and UV2.x. `keep(X, Z)` (bool grid) drops quads (holes)."""
    X, Z = np.meshgrid(xs, zs)
    Y = height(X, Z)
    P = np.stack([X, Y, Z], axis=-1)
    B = np.clip(wet(X, Z, Y), 0, 1) if wet is not None else np.zeros_like(X)
    G = np.clip(salt(X, Z, Y), 0, 1) if salt is not None else np.zeros_like(X)
    A = np.full_like(X, erosion)
    col = np.stack([np.zeros_like(X), G, B, A], axis=-1)
    occ = np.clip(ao(X, Z, Y), 0.2, 1.0) if ao is not None else np.ones_like(X)
    uv2 = np.stack([occ, np.full_like(X, variation)], axis=-1)
    uv = np.stack([X, Z], axis=-1) / 3.0
    rows, cols = X.shape
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(P.reshape(-1, 3), np.tile(kc.UP, (rows * cols, 1)), uv.reshape(-1, 2),
                           uv2.reshape(-1, 2), col.reshape(-1, 4))
    k = keep(X, Z) if keep is not None else None
    for r in range(rows - 1):
        for c in range(cols - 1):
            if k is not None and not (k[r, c] and k[r, c + 1] and k[r + 1, c] and k[r + 1, c + 1]):
                continue
            a = base + r * cols + c
            b, cc, d = a + 1, a + cols + 1, a + cols
            # Godot is +Y up with -Z north: (a, d, cc) winds counter-clockwise seen from above.
            mb.add_tri(a, d, cc, mat)
            mb.add_tri(a, cc, b, mat)
    kc.recompute_normals(mb, start_v, start_t)


def edge_fade(X: np.ndarray, Z: np.ndarray, half: float, band: float) -> np.ndarray:
    """1 inside, falling to 0 at the cell edge (|x| or |z| = half) over `band` metres, so cells tile at y 0."""
    dx = half - np.abs(X)
    dz = half - np.abs(Z)
    return kc.smoothstep(0.0, band, np.minimum(dx, dz))


# ---------------------------------------------------------------------------------------------
# Burned variants: the char field
# ---------------------------------------------------------------------------------------------
class CharField:
    """A seeded scalar 'how burned' field over a piece: 1 at the fire's seat, falling with distance and
    with height above it (fire climbs, so faces above the seat char less than faces beside it at its own
    level only once the flames are gone), broken up by noise. `level(p)` for points (..., 3)."""

    def __init__(self, seat, radius: float, rng: np.random.Generator, *, climb: float = 0.6, breakup: float = 0.35):
        self.seat = np.asarray(seat, float)
        self.radius = radius
        self.climb = climb
        self.breakup = breakup
        self.noise = kc.Noise3(rng)

    def level(self, p: np.ndarray) -> np.ndarray:
        d = np.asarray(p, float) - self.seat
        horiz = np.sqrt(d[..., 0] ** 2 + d[..., 2] ** 2)
        up = np.maximum(d[..., 1], 0.0)
        dist = horiz + up * self.climb
        base = 1.0 - kc.smoothstep(self.radius * 0.35, self.radius, dist)
        n = self.noise.fbm(np.asarray(p, float) / 0.45, 3) - 0.5
        return np.clip(base + n * self.breakup * 2.0, 0.0, 1.0)


def tri_centroids(mb: kc.MeshBuilder, start_tri: int = 0) -> np.ndarray:
    pos = np.asarray(mb.pos)
    t = np.asarray(mb.tris[start_tri:], dtype=np.int64)
    return pos[t].mean(axis=1)


def apply_char(mb: kc.MeshBuilder, field: CharField, *, start_tri: int = 0, char_at: float = 0.55,
               scorch_at: float = 0.2, wood=(M_TIMBER, "kit_timber"), rope=(M_ROPE, "kit_lashing")) -> None:
    """Re-slots timber and rope triangles by the char field: -> bs_char above `char_at`, -> bs_scorch above
    `scorch_at`. Cloth is scorch_cloth's (after burn_holes)."""
    if mb.triangle_count <= start_tri:
        return
    lv = field.level(tri_centroids(mb, start_tri))
    i_char, i_scorch = mb.material(M_CHAR), mb.material(M_SCORCH)
    for k, level in enumerate(lv):
        t = start_tri + k
        name = mb.materials[mb.tri_mat[t]]
        if name in wood or name in rope:
            if level >= char_at:
                mb.tri_mat[t] = i_char
            elif level >= scorch_at:
                mb.tri_mat[t] = i_scorch


def scorch_cloth(mb: kc.MeshBuilder, field: CharField, rim: tuple[float, float], *, start_tri: int = 0,
                 cloth=(M_CANVAS, "kit_cloth_sand")) -> None:
    """Burned canvas: a ragged black rim (bs_char) where the char level is within `rim` (just under
    burn_holes' threshold, so it edges every hole), and the rest of the plain canvas smoke-stained."""
    if mb.triangle_count <= start_tri:
        return
    lv = field.level(tri_centroids(mb, start_tri))
    i_char, i_cs = mb.material(M_CHAR), mb.material(M_CANVAS_SCORCHED)
    for k, level in enumerate(lv):
        t = start_tri + k
        name = mb.materials[mb.tri_mat[t]]
        if name not in cloth and name not in (M_CANVAS_TEAL, M_CANVAS_SCORCHED):
            continue
        if rim[0] <= level <= rim[1]:
            mb.tri_mat[t] = i_char
        elif name in cloth:
            mb.tri_mat[t] = i_cs


def burn_holes(mb: kc.MeshBuilder, field: CharField, threshold: float, *, start_tri: int = 0,
               slots=(M_CANVAS, M_CANVAS_TEAL, M_CANVAS_SCORCHED, "kit_cloth_sand")) -> None:
    """Deletes cloth triangles whose char level is above `threshold` (the canvas burned away)."""
    if mb.triangle_count <= start_tri:
        return
    lv = field.level(tri_centroids(mb, start_tri))
    keep_t, keep_m = mb.tris[:start_tri], mb.tri_mat[:start_tri]
    for k, level in enumerate(lv):
        t = start_tri + k
        if mb.materials[mb.tri_mat[t]] in slots and level > threshold:
            continue
        keep_t.append(mb.tris[t])
        keep_m.append(mb.tri_mat[t])
    mb.tris, mb.tri_mat = keep_t, keep_m


def disc(mb: kc.MeshBuilder, center, radius: float, height, mat: int, *, rings: int = 6, sectors: int = 18,
         wet: float = 0.0, salt: float = 0.0, erosion: float = 0.4, variation: float = 0.5) -> None:
    """A round surface y = height(X, Z) on a polar grid (no staircase edge, unlike a masked heightfield)."""
    center = np.asarray(center, float)
    r = np.linspace(0.0, radius, rings + 1)[1:]
    a = np.linspace(0.0, 2.0 * math.pi, sectors, endpoint=False)
    R, A = np.meshgrid(r, a, indexing="ij")
    X = center[0] + R * np.cos(A)
    Z = center[2] + R * np.sin(A)
    pts = np.vstack([[center[0], float(height(np.array(center[0]), np.array(center[2]))), center[2]],
                     np.stack([X, height(X, Z), Z], axis=-1).reshape(-1, 3)])
    n = len(pts)
    col = np.tile([0.0, salt, wet, erosion], (n, 1))
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(pts, np.tile(kc.UP, (n, 1)), pts[:, [0, 2]] / 3.0, np.tile([1.0, variation], (n, 1)), col)
    for s in range(sectors):
        s1 = (s + 1) % sectors
        mb.add_tri(base, base + 1 + s1, base + 1 + s, mat)
        for k in range(rings - 1):
            a0, a1 = base + 1 + k * sectors + s, base + 1 + k * sectors + s1
            b0, b1 = a0 + sectors, a1 + sectors
            mb.add_tri(a0, a1, b1, mat)
            mb.add_tri(a0, b1, b0, mat)
    kc.recompute_normals(mb, start_v, start_t)


def ember_bed(mb: kc.MeshBuilder, center, radius: float, count: int, rng: np.random.Generator,
              noise: kc.Noise3, *, lod: bool = False) -> None:
    """A low mound of grey ash with glowing coals and a few charred stick ends: the fire's seat."""
    center = np.asarray(center, float)
    i_ash, i_ember, i_char = mb.material(M_ASH), mb.material(M_EMBER), mb.material(M_CHAR)

    def h(X, Z):
        r = np.sqrt(X ** 2 + Z ** 2) / radius
        # A soft mound whose rim dips under the ground it lies on, so it has no visible edge.
        return center[1] - 0.05 + 0.06 * np.clip(1 - r, 0, 1) ** 0.5 + 0.07 * radius * np.clip(1 - r ** 2, 0, 1) \
            + 0.03 * (noise.fbm(np.stack([X * 3.0, np.zeros_like(X), Z * 3.0], axis=-1), 2) - 0.5)

    # The burned ground: a sooted ring wider than the ash, its rim sunk under the ground it lies on.
    ring_r = radius * 1.4

    def ring_h(X, Z):
        r = np.sqrt(X ** 2 + Z ** 2) / ring_r
        return center[1] + 0.03 - 0.12 * r ** 2

    disc(mb, center, ring_r, lambda X, Z: ring_h(X - center[0], Z - center[2]), mb.material(M_SOOT),
         rings=3 if not lod else 1, sectors=16 if not lod else 7, erosion=0.5)
    disc(mb, center, radius, lambda X, Z: h(X - center[0], Z - center[2]), i_ash, rings=6 if not lod else 2,
         sectors=18 if not lod else 7, wet=0.0, salt=0.0, erosion=0.6)
    if lod:
        return
    for k in range(count):
        # Live coals clustered toward the seat, half sunk in the ash, with dead black lumps among them.
        a, r = rng.uniform(0, 2 * math.pi), radius * rng.random() ** 1.5 * 0.85
        p = center + np.array([math.cos(a) * r, 0.0, math.sin(a) * r])
        s = rng.uniform(0.014, 0.034)
        p[1] = float(h(np.array(p[0] - center[0]), np.array(p[2] - center[2]))) - s * 0.25
        slot = i_ember if (k % 5) < 3 else i_char
        kc.rounded_block(mb, p, (s, s * 0.55, s * 0.8), slot, rot=kc.rot_y(rng.uniform(0, 3)), radius=s * 0.4,
                         seg=1, variation=float(rng.random()))
    for _k in range(max(2, count // 4)):
        a = rng.uniform(0, 2 * math.pi)
        p0 = center + np.array([math.cos(a) * radius * 0.2, 0.05, math.sin(a) * radius * 0.2])
        p1 = center + np.array([math.cos(a) * radius * 1.1, 0.02, math.sin(a) * radius * 1.1])
        kc.tube(mb, np.array([p0, p1]), rng.uniform(0.025, 0.045), 5, i_char, noise=noise, disp_m=0.01,
                variation=float(rng.random()), cap_start=True, cap_end=True)
