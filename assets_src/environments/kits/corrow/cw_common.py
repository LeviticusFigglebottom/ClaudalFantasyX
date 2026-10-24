"""Shared helpers for the Corrow seawall kit (M3-ENV-04; docs/kb/art/environments/corrow.md).

The geometry core is the Haluna kit's (assets_src/environments/kits/haluna/kit_common.py: MeshBuilder,
the weathering channels, the primitives, the glTF export), imported read-only, as is the Brine Shoals
kit's heightfield helper (bs_common.heightfield). Coordinates are Godot's (metres, +Y up, +X east,
-Z north). Vertex colours follow haluna.md §4: R moss, G salt, B wet, A erosion.

What this module adds:
* `bend`: the wall pieces are modelled straight along +X with the sea on +Z and then bent onto the
  seawall's arc (R = 300 m about a centre out at sea, at local z = +R: the wall follows the bay's shore,
  concave to the sea), so segments laid at equal angular steps close exactly and anything built along
  the wall (the stair, the apron) follows the same curve.
* `grid_surface`: a (rows, cols) point grid as one smooth surface, wound so its normals face `outward`.
* `watcher_face`: the Watchers' carved face as a displacement field (closed lids, an open humming mouth,
  a crown of breaking-wave scallops), shared by the parapet heads and the sea-face reliefs.
* the slot renaming that gives every piece this kit's own `cw_*` material slots.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for _p in (HERE.parent / "haluna", HERE.parent / "brine_shoals"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import bs_common as bsc  # noqa: E402  (the Brine Shoals kit's heightfield, read-only)
import kit_common as kc  # noqa: E402  (the Haluna kit's core, read-only)

# ---------------------------------------------------------------------------------------------
# The seawall's frame (corrow.md §0)
# ---------------------------------------------------------------------------------------------
ARC_R_M = 300.0  # the walk's centre line; the centre is out at sea (+Z)
SEGMENT_M = 12.0  # arc length of one seawall_curve on the centre line
SEGMENT_DEG = math.degrees(SEGMENT_M / ARC_R_M)
WALK_Y = 12.0
TOWN_Y = 1.0
SEA_FOOT_Y = -1.0
COURSE_M = 0.5  # block course height (the texture's course pitch too)
BLOCK_M = 1.2  # block length (the texture tiles 2 blocks x 2 courses: 2.4 x 1.0 m)
WALK_HALF_M = 3.0  # walk from z -3.0 (inner kerb) to +3.0 (parapet course)
PARAPET = (3.0, 4.2, 0.9)  # z0, z1, height of the parapet course above the walk
KERB = (-3.0, -2.4, 0.5)  # z0, z1, height of the inner kerb
SEA_BATTER_DEG = 12.0
INNER_BATTER_DEG = 6.0
HEAD_PITCH_M = 3.0  # Watchers' heads on the parapet, centre to centre

# ---------------------------------------------------------------------------------------------
# Material slots (cw_materials.py writes one .tres per slot)
# ---------------------------------------------------------------------------------------------
M_LATERITE = "cw_laterite"
M_LATERITE_NEW = "cw_laterite_rebuilt"
M_CARVED = "cw_laterite_carved"
M_PAVING = "cw_paving"
M_RUBBLE = "cw_rubble"
M_EARTH = "cw_earth"
M_COBBLE = "cw_cobble"
M_HOUSE = "cw_house_stone"
M_TIMBER = "cw_timber"
M_ROPE = "cw_rope"
M_TILE = "cw_roof_tile"
M_IRON = "cw_iron"
M_DARK = "cw_interior_dark"
M_COPPER = "cw_copper"
M_HEADLAND = "cw_headland"
M_BEACON = "cw_beacon"
M_MORTAR = "cw_mortar"
M_BROKEN = "cw_laterite_broken"  # M3-ENV-04B: fresh breaks, the raw stone inside the 900-year skin

# Haluna generator slots reused by import -> this kit's slots.
RENAME = {
    "kit_timber": M_TIMBER,
    "kit_lashing": M_ROPE,
    "kit_roof_tile": M_TILE,
    "kit_mortar_white": M_MORTAR,
    "kit_thatch": M_TIMBER,
}

# Weathering presets (vertex-colour multipliers, kit_common.Weathering).
WALL_W = kc.Weathering(moss=0.0, salt=0.6, wet=0.2, erosion=0.6, noise_scale_m=1.6)
CARVED_W = kc.Weathering(moss=0.0, salt=0.45, wet=0.1, erosion=0.7, noise_scale_m=0.5)
TOWN_W = kc.Weathering(moss=0.25, salt=0.3, wet=0.1, erosion=0.5)
IRON_W = kc.Weathering(moss=0.0, salt=0.3, wet=0.4, erosion=0.3)

LOD = "-lod1"


def finalize(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Renames reused Haluna slots to this kit's, merges duplicates and drops unused slots."""
    names = [RENAME.get(m, m) for m in mb.materials]
    uniq: list[str] = []
    for n in names:
        if n not in uniq:
            uniq.append(n)
    remap = [uniq.index(n) for n in names]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    mb.materials = uniq
    used = sorted(set(mb.tri_mat))
    if len(used) != len(mb.materials):
        keep = {old: new for new, old in enumerate(used)}
        mb.materials = [mb.materials[i] for i in used]
        mb.tri_mat = [keep[m] for m in mb.tri_mat]
    return mb


# ---------------------------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------------------------
def bend_points(p: np.ndarray, radius: float = ARC_R_M) -> tuple[np.ndarray, np.ndarray]:
    """Local straight (x along the wall, z toward the sea) -> the arc about (0, 0, +radius). Returns
    (points, angles). A piece bent this way is placed on the arc at arc length s with yaw -s / radius
    (Godot's Basis(UP, yaw))."""
    p = np.asarray(p, float)
    theta = p[..., 0] / radius
    r = radius - p[..., 2]
    out = np.stack([r * np.sin(theta), p[..., 1], radius - r * np.cos(theta)], axis=-1)
    return out, theta


def bend(mb: kc.MeshBuilder, radius: float = ARC_R_M, start_vertex: int = 0) -> None:
    """Bends a builder's vertices [start_vertex:] onto the arc; normals turn with the local tangent."""
    p = np.asarray(mb.pos[start_vertex:], float)
    if len(p) == 0:
        return
    q, theta = bend_points(p, radius)
    n = np.asarray(mb.nrm[start_vertex:], float)
    c, s = np.cos(theta), np.sin(theta)
    nn = np.stack([c * n[:, 0] - s * n[:, 2], n[:, 1], s * n[:, 0] + c * n[:, 2]], axis=-1)
    mb.pos[start_vertex:] = q.tolist()
    mb.nrm[start_vertex:] = kc.normalize(nn).tolist()


def grid_surface(mb: kc.MeshBuilder, grid: np.ndarray, mat: int, *, outward, uv: np.ndarray, col: np.ndarray,
                 uv2: np.ndarray, smooth: bool = True) -> None:
    """A (rows, cols, 3) grid as one surface whose normals face `outward` (a vector, or a (rows, cols, 3)
    field). The winding is chosen from the grid's own mean cross product, so callers need not care."""
    g = np.asarray(grid, float)
    dcol = np.gradient(g, axis=1)
    drow = np.gradient(g, axis=0)
    nrm = np.cross(dcol, drow)
    flip = float(np.sum(nrm * np.broadcast_to(np.asarray(outward, float), g.shape))) < 0.0
    rows, cols = g.shape[:2]
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(g.reshape(-1, 3), np.tile(kc.UP, (rows * cols, 1)), np.asarray(uv).reshape(-1, 2),
                           np.asarray(uv2, float).reshape(-1, 2), np.asarray(col, float).reshape(-1, 4))
    mb.add_grid_indices(base, rows, cols, mat, flip=flip)
    if smooth:
        kc.recompute_normals(mb, start_v, start_t)


def course_profile(y: np.ndarray, rng_offsets: np.ndarray, *, groove_m: float = 0.022, set_m: float = 0.012,
                   base_y: float = -2.0) -> np.ndarray:
    """Displacement (m, outward) of a coursed face at heights y: a V groove at every course joint and a
    small per-course setback (`rng_offsets`, one value in [-1, 1] per course from base_y upward)."""
    k = np.floor((y - base_y) / COURSE_M).astype(int)
    k = np.clip(k, 0, len(rng_offsets) - 1)
    f = (y - base_y) / COURSE_M - np.floor((y - base_y) / COURSE_M)
    d = np.minimum(f, 1.0 - f) * COURSE_M  # metres to the nearest joint
    groove = -groove_m * (1.0 - kc.smoothstep(0.0, 0.05, d))
    return groove + set_m * rng_offsets[k]


def course_rows(y0: float, y1: float, *, base_y: float = -2.0, bevel_m: float = 0.05, mid: bool = True) -> np.ndarray:
    """Row heights for a coursed face from y0 to y1: each joint, a row `bevel_m` either side of it and
    (with `mid`) one mid-course row, so the grooves are crisp without a fine grid."""
    ys = [y0, y1]
    j = math.ceil((y0 - base_y) / COURSE_M)
    while base_y + j * COURSE_M < y1:
        yj = base_y + j * COURSE_M
        ys += [yj, yj - bevel_m, yj + bevel_m] + ([yj + COURSE_M * 0.5] if mid else [])
        j += 1
    ys += [y0 + 0.5 * min(COURSE_M, y1 - y0)]
    arr = np.unique(np.round(np.clip(np.asarray(ys), y0, y1), 5))
    return arr


# ---------------------------------------------------------------------------------------------
# The Watchers' face (corrow.md §2)
# ---------------------------------------------------------------------------------------------
def _g(x, s):
    return np.exp(-(np.asarray(x) / s) ** 2)


def _blob(x, y, cx, cy, rx, ry, power: float = 2.0):
    """A smooth bump: (1 - r^2)^power inside the ellipse (power >= 2 has no visible rim)."""
    r2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    return np.clip(1.0 - r2, 0.0, 1.0) ** power


@dataclass(frozen=True)
class FaceCarving:
    """The constants of one Watcher carving (M3-ENV-04B). `CARVING_A` is the M3-ENV-04 face exactly (the
    same numbers in the same arithmetic, so the committed heads are unchanged); `CARVING_B` is a second
    hand: an older, heavier face with lower, more downcast lids, a broader nose, a wider humming mouth and a
    crown of three long waves instead of five."""

    jaw: float = 0.43
    jaw_narrow: float = 0.16
    brow_y: float = 0.655
    brow_curve: float = 0.22
    brow_m: float = 0.016
    eye_x: float = 0.158
    eye_y: float = 0.572
    lid_rx: float = 0.1
    lid_ry: float = 0.038
    lid_m: float = 0.02
    crease_droop: float = 0.22
    nose_w0: float = 0.03
    nose_w1: float = 0.045
    tip_rx: float = 0.052
    wing_x: float = 0.056
    mouth_rx: float = 0.058
    mouth_ry: float = 0.03
    mouth_y: float = 0.236
    cheek_m: float = 0.014
    waves: float = 5.0
    wave_rise: float = 0.72
    wave_fall: float = 0.28
    wave_m: float = 0.08


CARVING_A = FaceCarving()
CARVING_B = FaceCarving(jaw=0.45, jaw_narrow=0.12, brow_y=0.665, brow_curve=0.3, brow_m=0.022, eye_x=0.165,
                        eye_y=0.56, lid_rx=0.108, lid_ry=0.034, lid_m=0.024, crease_droop=0.34, nose_w0=0.036,
                        nose_w1=0.058, tip_rx=0.062, wing_x=0.066, mouth_rx=0.066, mouth_ry=0.032, mouth_y=0.232,
                        cheek_m=0.018, waves=3.0, wave_rise=0.64, wave_fall=0.36, wave_m=0.1)


def watcher_face(u: np.ndarray, v: np.ndarray, height: float, *, crown: bool = True,
                 fade: bool = True, carving: FaceCarving = CARVING_A) -> np.ndarray:
    """Displacement (m, outward from the carving's base plane) of a Watcher's face.

    `u` across (m, 0 on the centre line; the face is symmetric), `v` up from the chin's base (m);
    `height` is the face's height, chin to crown top. A broad, flat-planed face carved in stone: a high
    brow, closed lids with a down-curving crease, a straight nose, full cheeks, an open rounded mouth (as
    if humming) and a chin, under a crown band of breaking-wave scallops. With `fade`, everything falls
    to 0 at an ellipse about the face, so the field can be laid onto a wall face (the reliefs); the
    parapet heads pass fade=False and fade it at their own block edges."""
    h = float(height)
    x = np.asarray(u, float) / h  # face units: about 0.86 wide and 1.0 tall
    y = np.asarray(v, float) / h
    ax = np.abs(x)
    # The face plane: wrapped horizontally like a shallow cylinder, set forward from the chin to the
    # crown, the jaw narrowing toward the chin.
    k = carving
    jaw = k.jaw - k.jaw_narrow * (1.0 - kc.smoothstep(0.05, 0.42, y))
    wrap = np.clip(1.0 - (x / jaw) ** 2, 0.0, 1.0) ** 1.2
    vert = kc.smoothstep(0.0, 0.14, y) * (1.0 - kc.smoothstep(0.80, 0.86, y))
    plane = wrap * vert * 0.06
    # Brow: one crisp ridge over both eyes, the forehead flat above it.
    brow_y = k.brow_y - k.brow_curve * x ** 2
    brow = (kc.smoothstep(brow_y - 0.035, brow_y, y) * (1.0 - kc.smoothstep(brow_y + 0.004, brow_y + 0.03, y))) \
        * (1.0 - kc.smoothstep(0.27, 0.36, ax)) * k.brow_m
    # Eye sockets and closed lids: a soft hollow under the brow; a convex almond lid; its lower edge a
    # thin crease curving down toward the outer corner (the eyes closed, at rest).
    eyes = np.zeros_like(x)
    for sx in (-1.0, 1.0):
        ex, ey = k.eye_x * sx, k.eye_y
        dx = x - ex
        socket = _blob(x, y, ex, ey + 0.012, 0.14, 0.075, 2.0)
        lid = _blob(x, y, ex, ey + 0.014, k.lid_rx, k.lid_ry, 1.5)
        crease_y = ey - 0.004 - 1.5 * dx ** 2 - k.crease_droop * np.maximum(dx * sx, 0.0)
        crease = _g(y - crease_y, 0.007) * (1.0 - kc.smoothstep(0.075, 0.11, np.abs(dx)))
        eyes += -socket * 0.024 + lid * k.lid_m - crease * 0.009
    # Nose: a straight ridge from between the brows to a broad, rounded tip; wings and nostril shadows.
    t = np.clip((0.625 - y) / 0.26, 0.0, 1.0)
    w = k.nose_w0 + k.nose_w1 * t
    on = kc.smoothstep(0.345, 0.375, y) * (1.0 - kc.smoothstep(0.615, 0.65, y))
    nose = _g(x, w) ** 1.5 * (0.012 + 0.05 * t ** 1.4) * on
    tip = _blob(x, y, 0.0, 0.378, k.tip_rx, 0.036, 2.0) * 0.022
    wings = (_blob(x, y, -k.wing_x, 0.372, 0.034, 0.03) + _blob(x, y, k.wing_x, 0.372, 0.034, 0.03)) * 0.022
    nostrils = (_blob(x, y, -0.028, 0.353, 0.02, 0.011) + _blob(x, y, 0.028, 0.353, 0.02, 0.011)) * 0.02
    # Cheeks: broad and full, low; a soft fold from the nose wings toward the mouth corners.
    cheeks = (_blob(x, y, -0.2, 0.37, 0.15, 0.13) + _blob(x, y, 0.2, 0.37, 0.15, 0.13)) * k.cheek_m
    fx = 0.088 + 0.3 * (0.37 - y)
    fold = (_g(ax - fx, 0.014)) * kc.smoothstep(0.22, 0.27, y) * (1.0 - kc.smoothstep(0.33, 0.37, y)) * 0.006
    # The mouth: open and rounded as if humming. Full lips around a deep oval hollow, the upper lip a
    # little longer; a philtrum groove above.
    mr = np.sqrt((x / k.mouth_rx) ** 2 + ((y - k.mouth_y) / k.mouth_ry) ** 2)
    lips = _g(mr - 1.15, 0.45) * 0.019
    hollow = (1.0 - kc.smoothstep(0.4, 1.0, mr)) * 0.04
    philtrum = _g(x, 0.016) * kc.smoothstep(0.276, 0.29, y) * (1.0 - kc.smoothstep(0.322, 0.345, y)) * 0.004
    chin = _blob(x, y, 0.0, 0.12, 0.11, 0.07) * 0.018
    d = plane + brow + eyes + nose + tip + wings - nostrils + cheeks - fold + lips - hollow - philtrum + chin
    if crown:
        # Crown: a proud band (0.80 to a scalloped top edge); each scallop a breaking wave, a long rise to a
        # rounded crest that curls forward and drops, with a hollow under the curl. Five waves across.
        n = k.waves
        cw = 0.5
        ph = (x / (2.0 * cw) + 0.5) * n
        f = ph - np.floor(ph)
        rise = np.sin(0.5 * np.pi * np.clip(f / k.wave_rise, 0.0, 1.0)) ** 1.5
        drop = np.cos(0.5 * np.pi * np.clip((f - k.wave_rise) / k.wave_fall, 0.0, 1.0)) ** 0.7
        crest = np.where(f < k.wave_rise, rise, drop)
        top = 0.88 + k.wave_m * crest
        inside = 1.0 - kc.smoothstep(cw - 0.03, cw, ax)
        band = kc.smoothstep(0.795, 0.81, y) * (1.0 - kc.smoothstep(top - 0.01, top + 0.003, y)) * inside
        # The wave's inner line: a groove following the crest down into the curl.
        curl = _g(y - (top - 0.032), 0.006) * kc.smoothstep(0.08, 0.3, f) * band
        rim = _g(y - 0.818, 0.007) * inside * 0.007
        d = d + band * 0.03 - curl * 0.008 + rim
    if fade:
        r = np.sqrt((x / 0.53) ** 2 + ((y - 0.5) / 0.55) ** 2)
        d = d * (1.0 - kc.smoothstep(0.86, 1.0, r))
    return d * h


def watcher_wear(d: np.ndarray, height: float) -> np.ndarray:
    """VC.A for a face: worn smooth (high erosion) on the proud brow, nose, lips and crown; crisp in the
    hollows. `d` is watcher_face's displacement."""
    rel = np.clip(np.asarray(d) / (0.09 * height), -1.0, 1.0)
    return np.clip(0.45 + 0.5 * rel, 0.0, 1.0)
