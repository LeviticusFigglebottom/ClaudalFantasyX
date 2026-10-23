"""Shared helpers for the procedural vegetation generators (M1-ENV-02, ADR 0005).

Pure numpy geometry (no bpy at import time, so textures.py and the unit tests can import it), plus
`export_glb()` which needs Blender.

Coordinates are Blender's: metres, +Z up, +X east, +Y north. The glTF exporter converts to Godot's
+Y up (Blender +Y becomes Godot -Z, i.e. world north = -Z as SPEC/art README require).

Per-vertex wind/shading channels (docs/kb/art/environments/vegetation.md, "Wind conventions"):
  COLOR_0.r  primary sway weight   0 at the root .. 1 where the whole plant bends most (trunk top)
  COLOR_0.g  secondary bend weight 0 at a frond/branch/blade base .. 1 at its tip (bobbing)
  COLOR_0.b  element phase         0..1 random per frond/branch/leaf/card (desynchronises motion)
  COLOR_0.a  flutter weight        0 on a rib/midrib .. 1 at a leaflet/leaf edge (fast, small)
  UV2.x      ambient occlusion     1 = open sky .. 0 = deep inside the crown (baked procedurally)
  UV2.y      tint variation        0..1 random per element; the shader shifts hue/value with it
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

UP = np.array([0.0, 0.0, 1.0])

# ---------------------------------------------------------------------------------------------
# Texture atlas layouts, shared by textures.py (which paints them) and the mesh generators (which
# map UVs into them). Rectangles are (u0, v0, u1, v1) in UV space with v = 0 at the TOP row of the
# PNG (glTF/Godot convention; Blender's V is flipped at export time by `to_blender_uv`).
# ---------------------------------------------------------------------------------------------
PALM_FROND_SIZE = (1024, 1024)
PALM_ATLAS = {
    "wing_green_a": (0.0, 0.00, 1.0, 0.25),
    "wing_green_b": (0.0, 0.25, 1.0, 0.50),
    "wing_dead": (0.0, 0.50, 1.0, 0.75),
    "rachis_green": (0.0, 0.75, 0.5, 0.8125),
    "rachis_dead": (0.0, 0.8125, 0.5, 0.875),
    "sheath": (0.0, 0.875, 0.5, 1.0),
    "husk": (0.5, 0.75, 0.75, 1.0),
    "spathe": (0.75, 0.75, 1.0, 1.0),
}
PALM_BARK_SIZE = (512, 1024)  # tiles in U (around the trunk) and V (along it)
PALM_BARK_TILE_M = 1.6  # metres of trunk covered by one V repeat

FRANGI_LEAF_SIZE = (1024, 1024)
FRANGI_ATLAS = {
    "leaf_0": (0.00, 0.0, 0.1875, 0.625),
    "leaf_1": (0.1875, 0.0, 0.375, 0.625),
    "leaf_2": (0.375, 0.0, 0.5625, 0.625),
    "leaf_3": (0.5625, 0.0, 0.75, 0.625),
    "leaf_old": (0.75, 0.0, 0.9375, 0.625),
    "stalk": (0.9375, 0.0, 1.0, 0.625),
    "flower_0": (0.0, 0.625, 0.375, 1.0),
    "flower_1": (0.375, 0.625, 0.75, 1.0),
    "bud": (0.75, 0.625, 1.0, 1.0),
}
FRANGI_BARK_SIZE = (512, 512)
FRANGI_BARK_TILE_M = 0.9

GRASS_SIZE = (512, 512)
GRASS_ATLAS = {
    "card_0": (0.0, 0.0, 0.5, 1.0),
    "card_1": (0.5, 0.0, 1.0, 1.0),
}

VINE_SIZE = (512, 512)
VINE_ATLAS = {
    "leaf_0": (0.0, 0.0, 0.5, 0.5),
    "leaf_1": (0.5, 0.0, 1.0, 0.5),
    "flower": (0.0, 0.5, 0.5, 1.0),
    "runner": (0.5, 0.5, 1.0, 0.625),
    "bud": (0.5, 0.625, 0.75, 0.875),
}


def atlas_uv(rect: tuple[float, float, float, float], u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Maps local (u, v) in [0, 1] into an atlas rectangle. Returns (..., 2)."""
    u0, v0, u1, v1 = rect
    return np.stack([u0 + (u1 - u0) * u, v0 + (v1 - v0) * v], axis=-1)


# ---------------------------------------------------------------------------------------------
# Vector helpers
# ---------------------------------------------------------------------------------------------
def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


def rotate(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    """Rodrigues rotation of vector(s) v about a unit axis."""
    axis = normalize(np.asarray(axis, dtype=float))
    c, s = math.cos(angle), math.sin(angle)
    return v * c + np.cross(axis, v) * s + np.outer(np.dot(v, axis), axis).reshape(np.shape(v)) * (1.0 - c)


def any_perpendicular(v: np.ndarray) -> np.ndarray:
    ref = np.array([1.0, 0.0, 0.0]) if abs(v[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    return normalize(np.cross(v, ref))


def parallel_transport_frames(points: np.ndarray, first_normal: np.ndarray | None = None):
    """Tangents, normals and binormals along a polyline without twist flips."""
    n = len(points)
    tang = np.zeros_like(points)
    tang[1:-1] = points[2:] - points[:-2]
    tang[0] = points[1] - points[0]
    tang[-1] = points[-1] - points[-2]
    tang = normalize(tang)
    norms = np.zeros_like(points)
    norms[0] = any_perpendicular(tang[0]) if first_normal is None else normalize(
        first_normal - tang[0] * np.dot(first_normal, tang[0]))
    for i in range(1, n):
        b = np.cross(tang[i - 1], tang[i])
        if np.linalg.norm(b) < 1e-9:
            norms[i] = norms[i - 1]
        else:
            ang = math.acos(max(-1.0, min(1.0, float(np.dot(tang[i - 1], tang[i])))))
            norms[i] = rotate(norms[i - 1], b, ang)
        norms[i] = normalize(norms[i] - tang[i] * np.dot(norms[i], tang[i]))
    binorms = np.cross(tang, norms)
    return tang, norms, binorms


def smoothstep(e0: float, e1: float, x):
    t = np.clip((np.asarray(x, dtype=float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# ---------------------------------------------------------------------------------------------
# Mesh builder
# ---------------------------------------------------------------------------------------------
@dataclass
class MeshBuilder:
    """Accumulates unshared-vertex triangle geometry with all vegetation channels."""

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
        """Adds a block of vertices (arrays of shape (k, ...)); returns the first index."""
        base = len(self.pos)
        p = np.asarray(p, dtype=float).reshape(-1, 3)
        k = len(p)
        self.pos.extend(p.tolist())
        self.nrm.extend(normalize(np.asarray(n, dtype=float).reshape(-1, 3)).tolist())
        self.uv.extend(np.broadcast_to(np.asarray(uv, dtype=float).reshape(-1, 2), (k, 2)).tolist())
        self.uv2.extend(np.broadcast_to(np.asarray(uv2, dtype=float).reshape(-1, 2), (k, 2)).tolist())
        self.col.extend(np.clip(np.broadcast_to(np.asarray(col, dtype=float).reshape(-1, 4), (k, 4)), 0, 1).tolist())
        return base

    def add_grid(self, p, n, uv, uv2, col, mat: int, flip: bool = False) -> None:
        """A (rows, cols) grid of vertices joined into quads (2 triangles each)."""
        p = np.asarray(p, dtype=float)
        rows, cols = p.shape[:2]

        def flat(a, d):
            a = np.asarray(a, dtype=float)
            return np.broadcast_to(a, (rows, cols, d)).reshape(-1, d) if a.ndim >= 2 else np.tile(a, (rows * cols, 1))

        base = self.add_vertices(p.reshape(-1, 3), flat(n, 3), flat(uv, 2), flat(uv2, 2), flat(col, 4))
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

    def add_tri(self, a: int, b: int, c: int, mat: int) -> None:
        self.tris.append((a, b, c))
        self.tri_mat.append(mat)

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        p = np.asarray(self.pos)
        return p.min(axis=0), p.max(axis=0)


def tube(mb: MeshBuilder, centers: np.ndarray, radii: np.ndarray, sides: int, mat: int, *, v_coord: np.ndarray,
         rect=(0.0, 0.0, 1.0, 1.0), u_repeat: float = 1.0, col: np.ndarray, uv2: np.ndarray,
         radius_noise=None, first_normal=None, cap_end: bool = False, swap_uv: bool = False) -> None:
    """Generalised cylinder along `centers`. UV u wraps around (u_repeat times), v = v_coord.

    `rect` maps into an atlas when the texture does not tile (u is then squeezed into the rect).
    `col` and `uv2` are per-ring arrays (n, 4) and (n, 2). `radius_noise(ring, angle) -> scale`."""
    tang, nrm, bin_ = parallel_transport_frames(centers, first_normal)
    n = len(centers)
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    p = np.zeros((n, sides + 1, 3))
    nn = np.zeros_like(p)
    for i in range(n):
        dirs = np.outer(np.cos(ang), nrm[i]) + np.outer(np.sin(ang), bin_[i])
        r = np.full(sides + 1, radii[i])
        if radius_noise is not None:
            r = r * np.array([radius_noise(i, a) for a in ang])
            r[-1] = r[0]
        p[i] = centers[i] + dirs * r[:, None]
        # Account for taper in the normal so lighting follows the cone, not a cylinder.
        dr = (radii[min(i + 1, n - 1)] - radii[max(i - 1, 0)]) / max(
            np.linalg.norm(centers[min(i + 1, n - 1)] - centers[max(i - 1, 0)]), 1e-6)
        nn[i] = normalize(dirs - tang[i] * float(np.clip(dr, -0.5, 0.5)))
    u = np.tile((ang / (2.0 * math.pi))[None, :], (n, 1))
    v = np.tile(np.asarray(v_coord, dtype=float)[:, None], (1, sides + 1))
    if swap_uv:  # atlas strips drawn lengthwise: along the tube -> rect u, around it -> rect v
        uv = atlas_uv(rect, np.clip(v, 0.0, 1.0), u)
    elif rect == (0.0, 0.0, 1.0, 1.0):
        uv = np.stack([u * u_repeat, v], axis=-1)
    else:
        uv = atlas_uv(rect, u, np.clip(v, 0.0, 1.0))
    colg = np.repeat(np.asarray(col, dtype=float)[:, None, :], sides + 1, axis=1)
    uv2g = np.repeat(np.asarray(uv2, dtype=float)[:, None, :], sides + 1, axis=1)
    mb.add_grid(p, nn, uv, uv2g, colg, mat)  # rows along, cols around: CCW = outward
    if cap_end:
        c = centers[-1] + tang[-1] * radii[-1] * 0.35
        ring = p[-1, :-1]
        base = mb.add_vertices(np.vstack([ring, c[None]]), np.vstack([nn[-1, :-1] * 0.3 + tang[-1], tang[-1][None]]),
                               np.vstack([uv[-1, :-1], uv[-1, :1]]), np.repeat(uv2g[-1, :1], sides + 1, axis=0),
                               np.repeat(colg[-1, :1], sides + 1, axis=0))
        for s in range(sides):
            mb.add_tri(base + s, base + (s + 1) % sides, base + sides, mat)


def ellipsoid(mb: MeshBuilder, center, radii, mat: int, *, rect, rings: int, segs: int, col, uv2, axis=None) -> None:
    """A UV-sphere ellipsoid, `axis` = its long (local z) axis."""
    axis = UP if axis is None else normalize(np.asarray(axis, dtype=float))
    x = any_perpendicular(axis)
    y = np.cross(axis, x)
    th = np.linspace(0.0, math.pi, rings + 1)
    ph = np.linspace(0.0, 2.0 * math.pi, segs + 1)
    T, P = np.meshgrid(th, ph, indexing="ij")
    local = np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P), -np.cos(T)], axis=-1)
    world = (local[..., 0:1] * x * radii[0] + local[..., 1:2] * y * radii[1] + local[..., 2:3] * axis * radii[2])
    nrm = local[..., 0:1] * x / radii[0] + local[..., 1:2] * y / radii[1] + local[..., 2:3] * axis / radii[2]
    uv = atlas_uv(rect, P / (2.0 * math.pi), T / math.pi)
    mb.add_grid(np.asarray(center) + world, normalize(nrm), uv, uv2, col, mat)


# ---------------------------------------------------------------------------------------------
# Small deterministic RNG wrapper (numpy PCG64) so every generator draws in a fixed order.
# ---------------------------------------------------------------------------------------------
def rng_for(species: str, seed: int) -> np.random.Generator:
    # Stable across Python runs (no hash() randomisation): fold the species name into the seed.
    salt = sum((i + 1) * ord(ch) for i, ch in enumerate(species))
    return np.random.default_rng(np.random.SeedSequence([seed, salt]))


# ---------------------------------------------------------------------------------------------
# Blender export (imports bpy lazily)
# ---------------------------------------------------------------------------------------------
def _to_blender_object(mb: MeshBuilder):
    import bpy  # noqa: PLC0415  (only inside Blender)

    me = bpy.data.meshes.new(mb.name)
    pos = np.asarray(mb.pos, dtype=np.float64)
    tris = np.asarray(mb.tris, dtype=np.int64)
    me.vertices.add(len(pos))
    me.vertices.foreach_set("co", pos.astype(np.float32).ravel())
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
    uv0[:, 1] = 1.0 - uv0[:, 1]  # our v = 0 is the top row; Blender's v = 0 is the bottom row
    uv1[:, 1] = 1.0 - uv1[:, 1]
    lay0 = me.uv_layers.new(name="UVMap")
    lay0.data.foreach_set("uv", uv0.astype(np.float32).ravel())
    lay1 = me.uv_layers.new(name="UV2")
    lay1.data.foreach_set("uv", uv1.astype(np.float32).ravel())
    me.uv_layers.active = lay0
    ca = me.color_attributes.new("Wind", "FLOAT_COLOR", "POINT")
    ca.data.foreach_set("color", np.asarray(mb.col, dtype=np.float32).ravel())
    me.color_attributes.active_color = ca
    for name in mb.materials:
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        me.materials.append(mat)
    me.normals_split_custom_set_from_vertices(np.asarray(mb.nrm, dtype=np.float32).tolist())
    ob = bpy.data.objects.new(mb.name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def export_glb(builders: list[MeshBuilder], out_path: str) -> None:
    import bpy  # noqa: PLC0415

    bpy.ops.wm.read_factory_settings(use_empty=True)
    for mb in builders:
        _to_blender_object(mb)
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,  # M1-ENV-07: Godot generates them on import (ensure_tangents, import_settings.py);
        # Blender's threaded tangent export races, so exported tangents made the build depend on --threads.
        export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
        export_materials="EXPORT",
        export_image_format="NONE",
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_extras=False,
    )


def summary(builders: list[MeshBuilder]) -> dict:
    return {mb.name: {"triangles": mb.triangle_count, "vertices": mb.vertex_count} for mb in builders}
