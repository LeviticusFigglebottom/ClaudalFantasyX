"""Corrow's seawall (corrow.md §0 and §2): the curved wall segment and the rip-rap apron at its sea foot.
Pure numpy; see cw_common.py.

  seawall_curve   12 m of the wall (arc length on the walk's centre line), bent about R = 240 m. Origin
                  at the datum (y 0, mean sea level) on the walk's centre line; the sea is on +Z. Inner
                  face (6 deg batter) from below the town's ground to the kerb top, the kerb, the paved walk
                  at +12.0 m, the parapet course, and the sea face (12 deg batter) down into the rip-rap.
                  Every face is a grid whose rows sit on the 0.5 m course joints, displaced into V grooves
                  with a small per-course setback, so the coursing reads at range where the texture cannot.
  wall_apron      12 m of rip-rap on the sea foot (bent the same way): tumbled laterite blocks and dark
                  boulders from -1.5 to +1.0 m on a rubble mound.

Mesh UVs are metres (u along the wall before bending, v = height; the walk's v is z), so the
laterite_blocks texture's courses land on the geometry's joints and its blocks follow the curve.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
from cw_common import kc

TRI_BUDGET = {"seawall_curve": (12000, 900), "wall_apron": (6000, 500)}

HALF_X = cw.SEGMENT_M * 0.5
INNER_TOP = cw.WALK_Y + cw.KERB[2]  # the inner face rises to the kerb's top
INNER_FOOT_Y = cw.TOWN_Y - 0.4  # buried under the town's ground
SEA_FOOT_BURIED_Y = cw.SEA_FOOT_Y - 0.5  # buried in the rip-rap
PARAPET_TOP = cw.WALK_Y + cw.PARAPET[2]
TAN_IN = math.tan(math.radians(cw.INNER_BATTER_DEG))
TAN_SEA = math.tan(math.radians(cw.SEA_BATTER_DEG))
EMBRASURE_PITCH = cw.HEAD_PITCH_M  # embrasures at x = 0, +-3, +-6 (heads at +-1.5, +-4.5)


def inner_z(y):
    return cw.KERB[0] - (INNER_TOP - np.asarray(y, float)) * TAN_IN


def sea_z(y):
    return cw.PARAPET[1] + (PARAPET_TOP - np.asarray(y, float)) * TAN_SEA


def _n2(noise: kc.Noise3, a, b, scale: float, octaves: int = 3, off: float = 0.0):
    p = np.stack([np.asarray(a) / scale + off, np.full_like(np.asarray(a, float), 0.31 + off), np.asarray(b) / scale - off],
                 axis=-1)
    return noise.fbm(p, octaves)


def _face(mb: kc.MeshBuilder, xs: np.ndarray, ys: np.ndarray, zfun, normal_yz, rng, noise, *, mat: int, sea: bool,
          coarse: bool) -> None:
    """A battered coursed face: rows `ys` (on the joints), columns `xs`; z = zfun(y) displaced along the
    face normal (0, ny, nz) by course grooves, per-course setbacks and a broad bulge."""
    X, Y = np.meshgrid(xs, ys)
    offsets = rng.uniform(-1.0, 1.0, 64)
    disp = np.zeros_like(X)
    if not coarse:
        disp = cw.course_profile(Y, offsets) + (_n2(noise, X, Y, 3.5, 3, 2.0 if sea else 5.0) - 0.5) * 0.08
    ny, nz = normal_yz
    P = np.stack([X, Y + disp * ny, zfun(Y) + disp * nz], axis=-1)
    breakup = _n2(noise, X, Y, 1.6, 3, 9.0)
    runoff = np.zeros_like(X)
    if sea:
        salt = np.clip(kc.smoothstep(0.6, 2.5, Y) * (1.0 - kc.smoothstep(8.0, 11.0, Y)) * (0.45 + 0.7 * breakup), 0, 1)
        # Spray: soaked to +2.5 m, damp in streaks to +6 m where the waves break against the face; and
        # matte run-off stains hanging under every embrasure (between the heads) from the parapet down:
        # no salt and no pale wear there (dry stains: wet ones caught the sun as glossy stripes).
        e = np.abs((X + EMBRASURE_PITCH * 0.5) % EMBRASURE_PITCH - EMBRASURE_PITCH * 0.5)
        runoff = np.exp(-(e / 0.45) ** 2) * kc.smoothstep(4.0, 12.0, Y) * (0.5 + 0.8 * breakup)
        wet = np.clip((1.0 - kc.smoothstep(0.8, 2.6, Y)) + (1.0 - kc.smoothstep(2.0, 6.5, Y)) * 0.45 * breakup
                      + 0.12 * breakup, 0, 1)
        salt = np.clip(salt * (1.0 - 0.9 * runoff), 0, 1)
        moss = np.zeros_like(X)
    else:
        salt = np.clip(0.12 + 0.2 * breakup, 0, 1) * kc.smoothstep(6.0, 12.0, Y)
        wet = np.clip((1.0 - kc.smoothstep(cw.TOWN_Y, cw.TOWN_Y + 0.7, Y)) * 0.6 + 0.05 * breakup, 0, 1)
        moss = np.clip((1.0 - kc.smoothstep(cw.TOWN_Y + 0.3, cw.TOWN_Y + 3.0, Y)) * (breakup - 0.25) * 1.2, 0, 1)
    erosion = np.clip(0.45 + 0.45 * breakup + (-disp / 0.03) * 0.2 - (0.45 * runoff if sea else 0.0), 0, 1)
    col = np.stack([moss, salt, wet, erosion], axis=-1)
    groove = np.clip(-cw.course_profile(Y, np.zeros(64)) / 0.022, 0, 1) if not coarse else np.zeros_like(X)
    base_ao = kc.smoothstep(INNER_FOOT_Y, cw.TOWN_Y + 1.5, Y) * 0.35 + 0.65 if not sea else np.ones_like(X)
    ao = np.clip(base_ao - 0.35 * groove, 0.25, 1.0)
    course = np.floor((Y + 2.0) / cw.COURSE_M)
    var = (np.sin(course * 12.9898) * 43758.5453) % 1.0
    uv2 = np.stack([ao, var], axis=-1)
    # Each 1 m band of two courses takes the texture at its own offset along the wall, so the 6 m block
    # pattern never repeats in a column; the offsets depend only on the band, so segments still join.
    band = np.floor(Y + 2.0)
    uv = np.stack([X + ((band * 0.6180339) % 1.0) * 6.0, Y], axis=-1)
    outward = np.array([0.0, ny, nz])
    start_t = mb.triangle_count
    cw.grid_surface(mb, P, mat, outward=outward, uv=uv, col=col, uv2=uv2)
    if not coarse:
        _rebuilt_patches(mb, start_t, noise, sea)


def _rebuilt_patches(mb: kc.MeshBuilder, start_t: int, noise: kc.Noise3, sea: bool) -> None:
    """The wall has been rebuilt after every Rising (bible §5.4): patches of fresher laterite, whole
    courses at a time (so their edges step along the joints), set into the older salt-greyed masonry.
    Per triangle, by a seeded field over (x, course)."""
    i_new = mb.material(cw.M_LATERITE_NEW)
    c = np.asarray(mb.pos)[np.asarray(mb.tris[start_t:], dtype=np.int64)].mean(axis=1)
    course = np.floor((c[:, 1] + 2.0) / cw.COURSE_M) * cw.COURSE_M
    block = np.floor(c[:, 0] / 1.2) * 1.2
    f = _n2(noise, block, course, 7.0, 3, 23.0 if sea else 29.0)
    low = 1.0 - kc.smoothstep(5.0, 9.0, c[:, 1]) * 0.5  # the storms take the lower courses most often
    for k, v in enumerate(f * low):
        if v > 0.5:
            mb.tri_mat[start_t + k] = i_new


def _flat(mb: kc.MeshBuilder, xs: np.ndarray, zs: np.ndarray, y, mat: int, *, outward, col, uv_v=None, ao=1.0,
          vertical: bool = False, z_const: float = 0.0, ys=None) -> None:
    """A horizontal strip (y = y(X, Z)) over xs x zs, or with `vertical` a vertical strip at z = z_const
    over xs x ys."""
    if vertical:
        X, Y = np.meshgrid(xs, ys)
        P = np.stack([X, Y, np.full_like(X, z_const)], axis=-1)
        uv = np.stack([X, Y], axis=-1)
    else:
        X, Z = np.meshgrid(xs, zs)
        Y = y(X, Z) if callable(y) else np.full_like(X, y)
        P = np.stack([X, Y, Z], axis=-1)
        uv = np.stack([X, Z if uv_v is None else uv_v(X, Z)], axis=-1)
    c = np.broadcast_to(np.asarray(col(P) if callable(col) else col, float), P.shape[:2] + (4,))
    a = np.broadcast_to(np.asarray(ao(P) if callable(ao) else ao, float), P.shape[:2])
    uv2 = np.stack([a, np.full(P.shape[:2], 0.5)], axis=-1)
    cw.grid_surface(mb, P, mat, outward=np.asarray(outward, float), uv=uv, col=c, uv2=uv2)


def _walk_rows(z0: float, z1: float, slab: float = 1.0, bevel: float = 0.05) -> np.ndarray:
    zs = [z0, z1]
    k = math.ceil(z0 / slab)
    while k * slab < z1:
        zs += [k * slab, k * slab - bevel, k * slab + bevel, k * slab + slab * 0.5]
        k += 1
    return np.unique(np.round(np.clip(zs, z0, z1), 5))


def _walk_cols(x0: float, x1: float, slab: float = cw.BLOCK_M, bevel: float = 0.05) -> np.ndarray:
    xs = [x0, x1]
    k = math.ceil(x0 / slab)
    while k * slab < x1:
        xs += [k * slab, k * slab - bevel, k * slab + bevel, k * slab - slab * 0.25, k * slab + slab * 0.25]
        k += 1
    return np.unique(np.round(np.clip(xs, x0, x1), 5))


def seawall(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_lat, i_pave = mb.material(cw.M_LATERITE), mb.material(cw.M_PAVING)
    xs = np.linspace(-HALF_X, HALF_X, 5 if lod else 21)
    if not lod:  # extra columns either side of each embrasure carry its run-off stain
        emb = np.arange(-HALF_X, HALF_X + 1e-6, EMBRASURE_PITCH)
        xs = np.unique(np.round(np.clip(np.concatenate([xs, emb - 0.3, emb + 0.3]), -HALF_X, HALF_X), 5))
    n_in = (-math.cos(math.radians(cw.INNER_BATTER_DEG)), math.sin(math.radians(cw.INNER_BATTER_DEG)))
    n_sea = (math.sin(math.radians(cw.SEA_BATTER_DEG)), math.cos(math.radians(cw.SEA_BATTER_DEG)))
    if lod:
        ys_in = np.array([INNER_FOOT_Y, 6.0, INNER_TOP])
        ys_sea = np.array([SEA_FOOT_BURIED_Y, 4.0, 9.0, PARAPET_TOP])
    else:
        ys_in = cw.course_rows(INNER_FOOT_Y, INNER_TOP, mid=False)
        ys_sea = cw.course_rows(SEA_FOOT_BURIED_Y, PARAPET_TOP, mid=False)
    # Inner face: its normal points to -Z (inland) and a little up.
    _face(mb, xs, ys_in, inner_z, (n_in[1], n_in[0]), rng, noise, mat=i_lat, sea=False, coarse=lod)
    _face(mb, xs, ys_sea, sea_z, (n_sea[0], n_sea[1]), rng, noise, mat=i_lat, sea=True, coarse=lod)
    top_col = np.array([0.0, 0.2, 0.0, 0.7])
    kz0, kz1, kh = cw.KERB
    # Kerb top and its walk-side face.
    _flat(mb, xs, np.array([kz0, kz1]), INNER_TOP, i_lat, outward=kc.UP, col=top_col)
    _flat(mb, xs, None, None, i_lat, outward=(0, 0, 1), col=top_col, vertical=True, z_const=kz1,
          ys=np.array([cw.WALK_Y - 0.02, INNER_TOP]), ao=0.8)
    # The walk: slabs (1.2 x 1.0 m) dished by feet, puddled in the dish (VC.B), wet near the parapet.
    pz0, pz1, ph = cw.PARAPET
    if lod:
        wx, wz = xs, np.array([kz1, pz0])
    else:
        wx, wz = _walk_cols(-HALF_X, HALF_X), _walk_rows(kz1, pz0)
    tilt = rng.uniform(-1.0, 1.0, (32, 32, 2))

    def walk_y(X, Z):
        if lod:
            return np.full_like(X, cw.WALK_Y)
        fx = X / cw.BLOCK_M - np.floor(X / cw.BLOCK_M)
        fz = Z - np.floor(Z)
        ix = np.floor(X / cw.BLOCK_M).astype(int) % 32
        iz = np.floor(Z).astype(int) % 32
        dish = np.sin(np.pi * fx) * np.sin(np.pi * fz)
        edge = np.minimum(np.minimum(fx, 1 - fx) * cw.BLOCK_M, np.minimum(fz, 1 - fz))
        joint = 1.0 - kc.smoothstep(0.0, 0.05, edge)
        # Feet wear the middle of the walk hardest.
        wear = 0.012 + 0.02 * (1.0 - kc.smoothstep(0.5, 2.6, np.abs(Z)))
        t = tilt[ix, iz]
        return cw.WALK_Y - dish * wear - joint * 0.012 + (t[..., 0] * (fx - 0.5) + t[..., 1] * (fz - 0.5)) * 0.008

    def walk_col(P):
        X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
        low = np.clip((cw.WALK_Y - Y) / 0.03, 0, 1)
        breakup = _n2(noise, X, Z, 2.0, 3, 13.0)
        wet = np.clip(0.35 + low * 0.7 + 0.25 * breakup + kc.smoothstep(1.5, 3.0, Z) * 0.25, 0, 1)
        salt = np.clip(0.15 + 0.3 * breakup * (1 - low), 0, 1)
        return np.stack([np.zeros_like(X), salt, wet, np.clip(0.4 + 0.4 * breakup, 0, 1)], axis=-1)

    _flat(mb, wx, wz, walk_y, i_pave, outward=kc.UP, col=walk_col,
          ao=lambda P: np.clip(0.75 + 0.25 * kc.smoothstep(kz1, kz1 + 0.6, P[..., 2])
                               - 0.25 * kc.smoothstep(pz0 - 0.5, pz0, P[..., 2]), 0.3, 1.0))
    # Parapet course: the walk-side face and the top (the Watchers' heads stand on it).
    _flat(mb, xs, None, None, i_lat, outward=(0, 0, -1), col=top_col, vertical=True, z_const=pz0,
          ys=np.array([cw.WALK_Y - 0.02, cw.WALK_Y + ph * 0.5, PARAPET_TOP]), ao=0.75)
    _flat(mb, xs, np.array([pz0, (pz0 + pz1) * 0.5, pz1]), PARAPET_TOP, i_lat, outward=kc.UP,
          col=np.array([0.0, 0.45, 0.25, 0.75]))
    cw.bend(mb)
    return mb


def build_seawall(seed: int = 801) -> list[kc.MeshBuilder]:
    return [seawall("seawall_curve", seed, lod=False), seawall("seawall_curve", seed, lod=True)]


# ---------------------------------------------------------------------------------------------
# The rip-rap apron
# ---------------------------------------------------------------------------------------------
def apron_mound_y(noise: kc.Noise3, X, Z):
    """The rubble mound under the rip-rap: +0.7 against the wall's foot (awash at the storm's +0.5 m), down
    to -1.9 m 6.5 m out."""
    z0 = float(sea_z(cw.TOWN_Y)) - 0.4
    t = np.clip((Z - z0) / 6.5, 0.0, 1.0)
    return 0.7 - 2.6 * kc.smoothstep(0.0, 1.0, t) + (_n2(noise, X, Z, 2.0, 3, 4.0) - 0.5) * 0.35


def apron(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_rub, i_lat = mb.material(cw.M_RUBBLE), mb.material(cw.M_LATERITE)
    z0 = float(sea_z(cw.TOWN_Y)) - 0.6
    xs = np.linspace(-HALF_X, HALF_X, 5 if lod else 17)
    zs = np.linspace(z0, z0 + 8.0, 3 if lod else 11)

    def col(P):
        Y = P[..., 1]
        return np.stack([np.zeros_like(Y), np.clip(kc.smoothstep(0.3, 1.0, Y) * 0.5, 0, 1),
                         np.clip(1.0 - kc.smoothstep(0.4, 1.1, Y) + 0.2, 0, 1), np.full_like(Y, 0.8)], axis=-1)

    _flat(mb, xs, zs, lambda X, Z: apron_mound_y(noise, X, Z) - 0.15, i_rub, outward=kc.UP, col=col, ao=0.6)
    if not lod:
        brng = kc.rng_for(name + "_blocks", seed)
        for _k in range(64):
            x = brng.uniform(-HALF_X + 0.3, HALF_X - 0.3)
            z = z0 + 0.3 + brng.random() ** 1.6 * 6.8
            size = brng.uniform(0.6, 1.7) * (1.15 - 0.3 * (z - z0) / 7.0)
            laterite = brng.random() < 0.35
            y = float(apron_mound_y(noise, np.array(x), np.array(z)))
            half = np.array([size * brng.uniform(0.7, 1.2), size * brng.uniform(0.35, 0.6),
                             size * brng.uniform(0.5, 0.9)]) * 0.5
            rot = kc.rot_y(brng.uniform(0, math.pi)) @ kc.rot_x(brng.uniform(-0.45, 0.45)) @ kc.rot_z(brng.uniform(-0.4, 0.4))
            kc.rounded_block(mb, (x, y + half[1] * 0.4, z), half, i_lat if laterite else i_rub, rot=rot,
                             radius=size * (0.06 if laterite else 0.18), seg=2, noise=noise, disp_m=size * 0.06,
                             disp_period_m=size * 0.6, weather=kc.Weathering(moss=0.0, salt=0.6, wet=0.7, erosion=0.9),
                             variation=float(brng.random()), wet_bias=0.2 if y < 0.4 else 0.0)
    cw.bend(mb)
    return mb


def build_apron(seed: int = 811) -> list[kc.MeshBuilder]:
    return [apron("wall_apron", seed, lod=False), apron("wall_apron", seed, lod=True)]


TARGETS = {"seawall_curve": build_seawall, "wall_apron": build_apron}
