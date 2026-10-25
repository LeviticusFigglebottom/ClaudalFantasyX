"""Shared helpers for the Tamsule Bell kit (M3-ENV-01; docs/kb/art/environments/tamsule_bell.md).

The kit builds on the Haluna kit's pure-numpy geometry (`kit_common`, imported read-only as `kc`, plus
`village` and `causeway` for posts, decks, roofs and shells). This module adds what an arena of
revolved bronze and ring-shaped galleries needs:

  polar(r, az, y)         a point at radius r and azimuth az (degrees clockwise from north, -Z), height y
  revolve(...)            a polyline in (r, y) swept about +Y between two azimuths (one smooth strip)
  revolve_loop(...)       a closed (r, y) cross-section swept as separate strips (hard edges between)
  ring_box(...)           an annular sector box (benches, decks, rails, ring walls)
  rename(mb, mapping)     re-slots the Haluna helpers' material names to this kit's `tb_*` slots
  surface_colors(...)     the weathering channels (R moss, G salt, B wet, A erosion) for any surface

Ring pieces are authored with their origin on the arena axis at the river datum and built at azimuth 0
(north), so a dresser places them by a rotation about Y (tamsule_bell.md §0).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HALUNA = HERE.parent / "haluna"
if str(HALUNA) not in sys.path:
    sys.path.insert(1, str(HALUNA))

import causeway  # noqa: E402  (Haluna kit, read-only)
import kit_common as kc  # noqa: E402  (Haluna kit, read-only)
import village  # noqa: E402  (Haluna kit, read-only)

__all__ = ["kc", "village", "causeway"]

# Slot renames for geometry made with the Haluna helpers.
HALUNA_SLOTS = {
    "kit_timber": "tb_timber",
    "kit_lashing": "tb_rope",
    "kit_roof_tile": "tb_roof_nipa",
    "kit_thatch": "tb_woven",
    "kit_mortar_white": "tb_lacquer_black",
    "kit_woven_panel": "tb_woven",
    "kit_wake_shell": "tb_wake_shell",
    "kit_cloth_sand": "tb_cloth_sand",
    "kit_interior_dark": "tb_interior_dark",
}

# Weathering presets (R moss, G salt, B wet, A erosion multipliers).
BRONZE = kc.Weathering(moss=0.15, salt=0.75, wet=0.15, erosion=0.35, noise_scale_m=2.5)
LACQUER = kc.Weathering(moss=0.05, salt=0.25, wet=0.0, erosion=0.45, noise_scale_m=0.8)
PILE = kc.Weathering(moss=0.1, salt=0.6, wet=0.3, erosion=0.7, noise_scale_m=0.6)
CERAMIC = kc.Weathering(moss=0.05, salt=0.35, wet=0.2, erosion=0.6, noise_scale_m=1.5)
TIMBER = kc.Weathering(moss=0.1, salt=0.35, wet=0.0, erosion=0.5, noise_scale_m=0.6)


def polar(r, az_deg, y) -> np.ndarray:
    """Arena point(s): azimuth clockwise from north (-Z), so az 90 is east (+X)."""
    a = np.radians(np.asarray(az_deg, dtype=float))
    r = np.asarray(r, dtype=float)
    y = np.asarray(y, dtype=float)
    x, z, yy = np.broadcast_arrays(r * np.sin(a), -r * np.cos(a), y)
    return np.stack([x, yy, z], axis=-1)


def rename(mb: kc.MeshBuilder, mapping: dict[str, str] | None = None) -> kc.MeshBuilder:
    """Renames material slots in place (merging duplicates, keeping triangle order)."""
    mapping = HALUNA_SLOTS if mapping is None else mapping
    new_names = [mapping.get(m, m) for m in mb.materials]
    uniq: list[str] = []
    for n in new_names:
        if n not in uniq:
            uniq.append(n)
    remap = [uniq.index(n) for n in new_names]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    mb.materials = uniq
    return mb


def surface_colors(p: np.ndarray, n: np.ndarray, weather: kc.Weathering, noise: kc.Noise3 | None, *,
                   edge=None, wet_bias=0.0, underside_grime: float = 0.0) -> np.ndarray:
    """Weathering channels for arbitrary (..., 3) points and normals (haluna.md §4 convention).
    `edge` (0..1, same shape as p[..., 0]) raises erosion/wear; shade and undersides gather salt."""
    shape = p.shape[:-1]
    breakup = noise.fbm(p / weather.noise_scale_m, 2) if noise is not None else np.full(shape, 0.5)
    up = n[..., 1]
    north = np.clip(-n[..., 2], 0.0, 1.0)
    edge = np.zeros(shape) if edge is None else np.broadcast_to(np.asarray(edge, float), shape)
    moss = weather.moss * kc.smoothstep(0.3, 0.9, up) * (0.4 + breakup) + underside_grime * np.clip(-up, 0, 1)
    salt = weather.salt * (0.35 + 0.5 * breakup + 0.35 * np.clip(-up, 0, 1) + 0.2 * north)
    wet = weather.wet * breakup + wet_bias
    ero = weather.erosion * (0.3 + 0.5 * breakup) + 0.6 * edge
    return np.clip(np.stack([moss, salt, wet, ero], axis=-1), 0.0, 1.0)


def _orient(mb: kc.MeshBuilder, grid: np.ndarray, outward: np.ndarray) -> bool:
    r, c = grid.shape[0] // 2, grid.shape[1] // 2
    du = grid[r, min(c + 1, grid.shape[1] - 1)] - grid[r, max(c - 1, 0)]
    dv = grid[min(r + 1, grid.shape[0] - 1), c] - grid[max(r - 1, 0), c]
    return float(np.dot(np.cross(du, dv), outward)) < 0.0


def revolve(mb: kc.MeshBuilder, prof: np.ndarray, az0: float, az1: float, n_az: int, mat: int, *,
            weather: kc.Weathering, noise: kc.Noise3 | None = None, outward: float = 1.0, disp_m: float = 0.0,
            disp_period_m: float = 1.0, edge=None, wet_bias=0.0, ao=1.0, variation: float = 0.5,
            underside_grime: float = 0.0, smooth: bool = True) -> None:
    """Sweeps the (r, y) polyline `prof` about +Y from az0 to az1 (degrees). The face normal is the
    profile normal (dy, -dr) times `outward`: a polyline running up the outside with +1 faces away from
    the axis, so a closed cross-section traversed counter-clockwise (r right, y up) faces out with +1."""
    prof = np.asarray(prof, dtype=float)
    az = np.linspace(az0, az1, n_az + 1)
    R, A = np.meshgrid(prof[:, 0], az, indexing="ij")
    Y = np.broadcast_to(prof[:, 1][:, None], R.shape)
    p = polar(R, A, Y)
    # Approximate normals for weathering (the strip recomputes the shading normals).
    dpr = np.gradient(prof, axis=0)
    nr = np.stack([dpr[:, 1], -dpr[:, 0]], axis=-1)  # (r, y) normal of the profile, rotated -90 deg
    nr = nr / np.maximum(np.linalg.norm(nr, axis=-1, keepdims=True), 1e-9) * outward
    nn = polar(np.broadcast_to(nr[:, 0][:, None], R.shape), A, np.broadcast_to(nr[:, 1][:, None], R.shape))
    if noise is not None and disp_m > 0.0:
        amp = noise.fbm(p / disp_period_m, 3) - 0.5
        if abs((az1 - az0) % 360.0) < 1e-6:
            amp[:, -1] = amp[:, 0]
        p = p + nn * (amp[..., None] * disp_m)
    s_len = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))])
    u = np.radians(A) * np.maximum(R, 0.5)
    uv = np.stack([u, np.broadcast_to(s_len[:, None], R.shape)], axis=-1)
    col = surface_colors(p, nn, weather, noise, edge=edge, wet_bias=wet_bias, underside_grime=underside_grime)
    ao_arr = np.broadcast_to(np.asarray(ao, float), R.shape)
    uv2 = np.stack([ao_arr, np.full(R.shape, variation)], axis=-1)
    mid = (prof.shape[0] // 2, n_az // 2)
    flip = _orient(mb, p, nn[mid])
    kc.quad_strip(mb, p, mat, uv=uv, col=col, uv2=uv2, flip=flip, smooth=smooth)


def revolve_loop(mb: kc.MeshBuilder, segments: list, az0: float, az1: float, n_az: int, mat: int, **kw) -> None:
    """A closed cross-section as a list of (polyline, outward_sign) segments, each swept as its own
    strip so the corners between segments stay hard."""
    for seg, sign in segments:
        revolve(mb, np.asarray(seg, float), az0, az1, n_az, mat, outward=sign, **kw)


def ring_box(mb: kc.MeshBuilder, r0: float, r1: float, y0: float, y1: float, az0: float, az1: float, n_az: int,
             mat: int, *, weather: kc.Weathering, noise: kc.Noise3 | None = None, caps: bool = True,
             bottom: bool = True, variation: float = 0.5, ao_top: float = 1.0, ao_side: float = 0.85) -> None:
    """An annular sector box between radii r0 < r1, heights y0 < y1 and azimuths az0 < az1."""
    common = dict(weather=weather, noise=noise, variation=variation)
    revolve(mb, [(r1, y1), (r0, y1)], az0, az1, n_az, mat, outward=1.0, ao=ao_top, **common)  # top
    revolve(mb, [(r1, y0), (r1, y1)], az0, az1, n_az, mat, outward=1.0, ao=ao_side, **common)  # outer
    revolve(mb, [(r0, y0), (r0, y1)], az0, az1, n_az, mat, outward=-1.0, ao=ao_side, **common)  # inner
    if bottom:
        revolve(mb, [(r0, y0), (r1, y0)], az0, az1, n_az, mat, outward=1.0, ao=0.5, **common)
    if caps:
        for az, sgn in ((az0, -1.0), (az1, 1.0)):
            q = polar(np.array([r0, r1, r1, r0]), az, np.array([y0, y0, y1, y1]))
            tangent = polar(1.0, az + 90.0, 0.0) * sgn
            uvq = np.array([[0, y0], [r1 - r0, y0], [r1 - r0, y1], [0, y1]])
            base = mb.add_vertices(q, np.tile(tangent, (4, 1)), uvq, np.tile([ao_side, variation], (4, 1)),
                                   np.tile(surface_colors(q[:1], tangent[None], weather, noise)[0], (4, 1)))
            n = np.cross(q[1] - q[0], q[2] - q[0])
            if float(np.dot(n, tangent)) >= 0.0:
                mb.add_tri(base, base + 1, base + 2, mat)
                mb.add_tri(base, base + 2, base + 3, mat)
            else:
                mb.add_tri(base, base + 2, base + 1, mat)
                mb.add_tri(base, base + 3, base + 2, mat)


def catmull_rom(points: np.ndarray, samples_per_seg: int) -> np.ndarray:
    """A centripetal-free (uniform) Catmull-Rom through `points` (N, d), endpoints clamped."""
    pts = np.asarray(points, dtype=float)
    p = np.vstack([pts[:1], pts, pts[-1:]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0.0, 1.0, samples_per_seg, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return np.asarray(out)


def torus(mb: kc.MeshBuilder, center, axis, radius: float, tube_r: float, n_major: int, n_minor: int, mat: int, *,
          weather: kc.Weathering, noise: kc.Noise3 | None = None, variation: float = 0.5, edge: float = 0.6,
          arc_deg: float = 360.0, start_deg: float = 0.0, up_hint=None) -> None:
    """A torus (or an arc of one) about `axis` through `center`: rings, loops, bosses."""
    axis = kc.normalize(np.asarray(axis, float))
    e1 = kc.any_perpendicular(axis) if up_hint is None else kc.normalize(np.asarray(up_hint, float)
                                                                         - axis * np.dot(up_hint, axis))
    e2 = np.cross(axis, e1)
    a = np.radians(start_deg + np.linspace(0.0, arc_deg, n_major + 1))
    ring = np.asarray(center, float) + radius * (np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2)
    kc.tube(mb, ring, tube_r, n_minor, mat, weather=weather, noise=None, variation=variation,
            u_repeat=1.0, v_scale=1.0, cap_start=arc_deg < 360.0, cap_end=arc_deg < 360.0)
    del noise, edge


def lift_flare(mb: kc.MeshBuilder, start_v: int, center_xz, half_w: float, half_d: float, y_eave: float,
               lift_m: float, reach_m: float) -> None:
    """Curls a roof's eave up beyond the wall line (Tamsule's flared eaves): vertices outside the
    half_w x half_d rectangle and within `reach_m` of the eave height rise by up to `lift_m`."""
    p = np.asarray(mb.pos[start_v:], dtype=float)
    if not len(p):
        return
    dx = np.abs(p[:, 0] - center_xz[0]) - half_w
    dz = np.abs(p[:, 2] - center_xz[1]) - half_d
    out = np.clip(np.maximum(dx, dz), 0.0, None)
    near = 1.0 - kc.smoothstep(0.0, reach_m, p[:, 1] - y_eave + 0.3)
    p[:, 1] += lift_m * (out / max(reach_m, 1e-6)) ** 2 * near
    mb.pos[start_v:] = p.tolist()


def signboard(mb: kc.MeshBuilder, center, w: float, h: float, yaw_deg: float, rng, *, thick: float = 0.08,
              strokes: int = 9, lod: bool = False) -> None:
    """A Tamsule gilded signboard: a black lacquer board, a gilded border, and original abstract glyph
    strokes in gold leaf (no real script, no religious figure). Faces +Z before the yaw."""
    rot = kc.rot_y(math.radians(yaw_deg))
    c = np.asarray(center, float)
    board = mb.material("tb_signboard")
    gold = mb.material("tb_gold_leaf")
    kc.rounded_block(mb, c, (w * 0.5, h * 0.5, thick * 0.5), board, rot=rot, radius=0.015, seg=1,
                     weather=LACQUER, variation=float(rng.random()))
    if lod:
        return
    fz = thick * 0.5 + 0.012
    bw = min(w, h) * 0.06
    for (ox, oy, hx, hy) in ((0, h * 0.5 - bw * 0.5, w * 0.5, bw * 0.5), (0, -h * 0.5 + bw * 0.5, w * 0.5, bw * 0.5),
                             (w * 0.5 - bw * 0.5, 0, bw * 0.5, h * 0.5), (-w * 0.5 + bw * 0.5, 0, bw * 0.5, h * 0.5)):
        kc.rounded_block(mb, c + rot @ np.array([ox, oy, fz]), (hx, hy, 0.012), gold, rot=rot, radius=0.006,
                         seg=1, weather=LACQUER, variation=0.5)
    # Glyph strokes: short bars and hooks laid out in a column (vertical board) or a row (horizontal).
    vertical = h >= w
    n_cells = 3 if vertical else 4
    for k in range(strokes):
        cell = k % n_cells
        t = (cell + 0.5) / n_cells - 0.5
        cx_ = 0.0 if vertical else t * (w - 3 * bw)
        cy_ = t * (h - 3 * bw) if vertical else 0.0
        size = (min(w, h) - 3 * bw) * 0.5
        ang = rng.choice([0.0, 0.5 * math.pi, 0.25 * math.pi, -0.25 * math.pi]) + rng.normal(0, 0.08)
        ln = size * rng.uniform(0.35, 0.9)
        off = np.array([cx_ + rng.uniform(-0.45, 0.45) * size, cy_ + rng.uniform(-0.45, 0.45) * size, fz])
        sr = rot @ kc.rot_z(ang)
        kc.rounded_block(mb, c + rot @ off, (ln * 0.5, size * 0.06, 0.01), gold, rot=sr, radius=0.005, seg=1,
                         weather=LACQUER, variation=0.5)
