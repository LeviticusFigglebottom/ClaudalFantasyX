"""Keth Pass, the Cold Road (keth_pass.md; M3-ENV-717): the Avalanche Ram's terrace and its kit pieces. Pure numpy.

Built in the Haluna kit (its import kind and materials directory, as iskarra.py), with the kit's `kit_keth_*` slots.

  keth_terrace_ground  (arena frame) the old road's level top, the battle floor at y 0 under its flags, the seeping
                       wall's foot behind (z < WALL_Z), the scree falling 14 m to the switchback in front (+Z, the
                       camera's side) and the crags rising either side of the saddle; per-triangle crag, scree,
                       pale grass by the seep. Flags of laid road stone over the floor (tops at y 0).
  lit_terrace_wall     a 12 m module of the Lit Age retaining wall: cyclopean ceramic blocks in battered courses to
                       8.5 m, the coping broken, two conduit channels, and the seep: glimmer running out of the joints
                       and down the face in thin sheets of cold light (not ice: ADR 0015). Origin at the foot's
                       centre, the face toward +Z.
  seep_pool            the pale pool at the wall's foot where the herd drank: a rim of set stones, the seep's surface,
                       pale grass grown too long round it. Origin at its centre on the ground.
  pass_cord            a cord from post to post across a saddle, 18 m, sagging, hung with knotted keth (undyed wool
                       and red: a knot is a name). Origin at the span's centre on the ground, the cord along X.
  cairn                a road cairn of stacked stones with cords tied round it.
  keth_far_ridges      the mountains round the pass as a far ring, r 500-950 m (no snow on them: ADR 0015).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_CRAG = "kit_keth_crag"
M_SCREE = "kit_keth_scree"
M_ROAD = "kit_keth_road"
M_LIT = "kit_keth_lit_ceramic"
M_SEEP = "kit_keth_seep"
M_GRASS = "kit_keth_grass"
M_WOOL = "kit_keth_wool"
M_RED = "kit_keth_red"
M_DARK = "kit_interior_dark"
M_TIMBER = "kit_timber"

TRI_BUDGET = {"keth_terrace_ground": (26000, 2400), "lit_terrace_wall": (16000, 1200), "seep_pool": (5000, 300),
              "pass_cord": (7000, 400), "cairn": (2500, 150), "keth_far_ridges": (4000, 1500)}

FLOOR_HALF_X = 9.5  # the old road's level top, the battle floor
FLOOR_FRONT_Z = 4.6
WALL_Z = -6.6  # the wall's face
WALL_H = 8.5
WALL_T = 2.5
DROP_M = 14.0  # the switchback below the terrace's front
SEEP_POOL_AT = (-9.0, -4.2)  # the arena's seep pool (x, z), clear of the battle slots' floor
ROCK = kc.Weathering(moss=0.3, salt=0.0, wet=0.0, erosion=0.7, noise_scale_m=2.0)
LIT = kc.Weathering(moss=0.35, salt=0.1, wet=0.15, erosion=0.8, noise_scale_m=1.2)


def terrace_height(X, Z, noise: kc.Noise3) -> np.ndarray:
    X, Z = np.asarray(X, float), np.asarray(Z, float)
    ax = np.abs(X)
    n = noise.fbm(np.stack([X / 14.0, np.zeros_like(X), Z / 14.0], -1), 4) - 0.5
    # Behind the wall: the slope the old road was cut into, rising to the crags.
    back = WALL_H - 0.4 + np.clip(-(Z - WALL_Z + WALL_T), 0.0, None) * 0.55 + n * 6.0
    # In front: the scree falling to the switchback, then the valley.
    front = -DROP_M * kc.smoothstep(FLOOR_FRONT_Z, FLOOR_FRONT_Z + 12.0, Z) - 10.0 * kc.smoothstep(40.0, 90.0, Z) \
        + n * 2.5 * kc.smoothstep(FLOOR_FRONT_Z, FLOOR_FRONT_Z + 6.0, Z)
    h = np.where(Z < WALL_Z - WALL_T, back, np.where(Z > FLOOR_FRONT_Z, front, -0.04))
    # The saddle's flanks: crags rising either side beyond the floor (and beyond the wall's ends).
    flank = np.clip(ax - FLOOR_HALF_X - 1.0, 0.0, None)
    h = h + flank * 0.75 + flank ** 1.3 * 0.05 + n * 5.0 * kc.smoothstep(FLOOR_HALF_X + 1.0, FLOOR_HALF_X + 12.0, ax)
    # Under the wall itself, and the floor, stay level.
    floor = (ax < FLOOR_HALF_X) & (Z >= WALL_Z - WALL_T) & (Z <= FLOOR_FRONT_Z)
    return np.where(floor, -0.04, h)


def _axis(lo, hi, f0, f1, fine, coarse_n):
    return np.unique(np.concatenate([np.linspace(lo, f0, coarse_n), np.arange(f0, f1, fine), np.linspace(f1, hi, coarse_n)]))


def build_ground(seed: int = 1501) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("keth_terrace_ground", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("keth_terrace_ground" + ("-lod1" if lod else ""))
        if lod:
            xs, zs = np.linspace(-120.0, 120.0, 33), np.linspace(-110.0, 130.0, 33)
        else:
            xs = _axis(-120.0, 120.0, -30.0, 30.0, 1.0, 10)
            zs = _axis(-110.0, 130.0, -24.0, 26.0, 1.0, 10)
        X, Z = np.meshgrid(xs, zs)
        Y = terrace_height(X, Z, noise)
        P = np.stack([X, Y, Z], -1)
        brk = noise.fbm(P / 3.0, 2)
        col = np.stack([np.zeros_like(Y), np.zeros_like(Y), np.zeros_like(Y), 0.5 + 0.4 * brk], -1)
        start_t = mb.triangle_count
        kc.quad_strip(mb, P, mb.material(M_SCREE), uv=np.stack([X, Z], -1) / 3.0, col=col, uv2=np.array([0.9, 0.5]),
                      flip=True)
        # Per triangle: crag on the steep faces, scree on the slopes, pale grass by the seep's foot.
        pos = np.asarray(mb.pos)
        tris = np.asarray(mb.tris)[start_t:]
        a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
        ny = np.abs(kc.normalize(np.cross(b - a, c - a))[:, 1])
        cen = (a + b + c) / 3.0
        i_crag, i_scree, i_grass = mb.material(M_CRAG), mb.material(M_SCREE), mb.material(M_GRASS)
        grass = (np.hypot(cen[:, 0] - SEEP_POOL_AT[0], cen[:, 2] - SEEP_POOL_AT[1]) < 4.8) & (ny > 0.9)
        mats = np.where(ny < 0.72, i_crag, np.where(grass, i_grass, i_scree))
        mb.tri_mat = mb.tri_mat[:start_t] + [int(m) for m in mats]
        if not lod:
            _flags(mb, rng, noise)
        out.append(mb)
    return out


def _flags(mb, rng, noise) -> None:
    """The old road's laid stones over the floor, tops at y 0, a kerb of set stones along the front edge."""
    z = WALL_Z + 0.2
    while z < FLOOR_FRONT_Z - 0.15:
        w = min(rng.uniform(0.55, 0.85), FLOOR_FRONT_Z - z)
        x = -FLOOR_HALF_X + rng.uniform(0.0, 0.4)
        while x < FLOOR_HALF_X - 0.15:
            ln = min(rng.uniform(0.7, 1.3), FLOOR_HALF_X - x)
            kc.rounded_block(mb, (x + ln * 0.5, -0.09 + rng.uniform(-0.008, 0.006), z + w * 0.5),
                             (ln * 0.5 - 0.014, 0.09, w * 0.5 - 0.014), mb.material(M_ROAD),
                             rot=kc.rot_y(rng.normal(0.0, 0.01)), radius=0.02, seg=1, noise=noise, disp_m=0.006,
                             weather=ROCK, variation=float(rng.random()))
            x += ln
        z += w
    x = -FLOOR_HALF_X
    while x < FLOOR_HALF_X:
        ln = rng.uniform(0.5, 0.9)
        h = rng.uniform(0.18, 0.34)
        kc.rounded_block(mb, (x + ln * 0.5, h * 0.5 - 0.05, FLOOR_FRONT_Z + 0.2), (ln * 0.5 - 0.02, h * 0.5, 0.2),
                         mb.material(M_ROAD), rot=kc.rot_y(rng.normal(0.0, 0.06)), radius=0.05, seg=1, noise=noise,
                         disp_m=0.02, weather=ROCK, variation=float(rng.random()))
        x += ln + rng.uniform(0.02, 0.4)


def build_wall(seed: int = 1502) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lit_terrace_wall", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lit_terrace_wall" + ("-lod1" if lod else ""))
        lit = mb.material(M_LIT)
        if lod:
            kc.rounded_block(mb, (0.0, (WALL_H - 0.5) * 0.5 - 0.25, -WALL_T * 0.5), (6.0, (WALL_H + 0.5) * 0.5, WALL_T * 0.5),
                             lit, radius=0.1, seg=1)
            _seeps(mb, rng, lod=True)
            out.append(mb)
            continue
        y = -0.5
        course = 0
        while y < WALL_H - 0.2:
            ch = min(rng.uniform(1.1, 1.8), WALL_H - y)
            x = -6.0 + (0.0 if course % 2 == 0 else -rng.uniform(0.6, 1.2))
            top_course = y + ch >= WALL_H - 0.05
            while x < 6.0 - 0.1:
                ln = min(rng.uniform(1.6, 3.2), 6.0 - max(x, -6.0))
                xa = max(x, -6.0)
                if top_course and rng.random() < 0.35:
                    x += ln
                    continue  # the broken coping: a block gone
                cy = y + ch * 0.5
                fz = -cy * 0.06  # a slight batter
                kc.rounded_block(mb, (xa + ln * 0.5, cy, fz - WALL_T * 0.5), (ln * 0.5 - 0.02, ch * 0.5 - 0.02, WALL_T * 0.5),
                                 lit, rot=kc.rot_z(rng.normal(0.0, 0.015)), radius=0.12, seg=2, noise=noise, disp_m=0.05,
                                 disp_period_m=0.6, weather=LIT, variation=float(rng.random()))
                x += ln
            y += ch
            course += 1
        # The conduit channels: dark recesses up the face where the light ran once.
        for cx in (-3.0, 3.2):
            kc.rounded_block(mb, (cx, 4.4, 0.02), (0.18, 3.6, 0.04), mb.material(M_DARK), radius=0.02, seg=1)
        _seeps(mb, rng, lod=False)
        out.append(mb)
    return out


def _seeps(mb, rng, *, lod: bool) -> None:
    """The seep: thin sheets of cold light from the joints down the face to the foot (both faces built)."""
    sheets = ((-3.0, 6.4, 0.42), (3.2, 5.6, 0.36), (-0.6, 3.8, 0.7), (4.8, 2.6, 0.5))
    for k, (x, y0, w) in enumerate(sheets):
        rows = 3 if lod else 9
        t = np.linspace(0.0, 1.0, rows)
        ys = y0 - (y0 + 0.02) * t
        zs = 0.06 - ys * 0.06 + 0.03
        wob = 0.12 * np.sin(t * 7.0 + k)
        grid = np.array([[[x + wob[i] + dx, ys[i], zs[i]] for dx in (-0.5 * w * (1 + 0.6 * t[i]), 0.5 * w * (1 + 0.6 * t[i]))]
                         for i in range(rows)])
        uv = np.array([[[0.0, tt * 4.0], [1.0, tt * 4.0]] for tt in t])
        for flip in (False, True):
            kc.quad_strip(mb, grid + [0.0, 0.0, 0.004 if not flip else -0.004], mb.material(M_SEEP), uv=uv,
                          col=(0, 0, 1, 0), uv2=(1.0, 0.5), flip=flip, smooth=True)


def build_pool(seed: int = 1503) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("seep_pool", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("seep_pool" + ("-lod1" if lod else ""))
        a = np.linspace(0.0, 2 * math.pi, (12 if lod else 40) + 1)
        r = np.array([0.0, 2.5])
        A, R = np.meshgrid(a, r)
        grid = np.stack([R * np.cos(A), np.full_like(A, -0.06), R * np.sin(A)], -1)
        kc.quad_strip(mb, grid, mb.material(M_SEEP), uv=np.stack([grid[..., 0], grid[..., 2]], -1), col=(0, 0, 1, 0),
                      uv2=(1.0, 0.5), flip=True, smooth=False)
        if lod:
            out.append(mb)
            continue
        for k in range(18):
            th = 2 * math.pi * k / 18 + rng.normal(0, 0.05)
            s = rng.uniform(0.28, 0.45)
            kc.rounded_block(mb, (math.cos(th) * 2.75, s * 0.35 - 0.08, math.sin(th) * 2.75), (s, s * 0.45, s * 0.8),
                             mb.material(M_ROAD), rot=kc.rot_y(-th), radius=s * 0.3, seg=2, noise=noise, disp_m=0.03,
                             weather=ROCK, variation=float(rng.random()))
        _grass(mb, rng, 3.1, 4.6, 60)
        out.append(mb)
    return out


def _grass(mb, rng, r0, r1, n) -> None:
    """Pale grass grown too long: crossed blade cards (two-sided), 0.6-1.1 m."""
    for _k in range(n):
        th = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(r0, r1)
        c = np.array([math.cos(th) * r, 0.0, math.sin(th) * r])
        h = rng.uniform(0.6, 1.1)
        for yaw in (rng.uniform(0, math.pi), None):
            yaw = rng.uniform(0, math.pi) if yaw is None else yaw
            d = np.array([math.cos(yaw), 0.0, math.sin(yaw)]) * 0.25
            lean = np.array([rng.normal(0, 0.15), 0.0, rng.normal(0, 0.15)])
            grid = np.array([[c - d, c + d], [c - d * 0.3 + [0, h, 0] + lean, c + d * 0.3 + [0, h, 0] + lean]])
            for flip in (False, True):
                kc.quad_strip(mb, grid, mb.material(M_GRASS), uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]),
                              col=(0, 0, 0, 0.3), uv2=(0.8, 0.5), flip=flip, smooth=False)


def build_cord(seed: int = 1504) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("pass_cord", seed)
        mb = kc.MeshBuilder("pass_cord" + ("-lod1" if lod else ""))
        timber, wool, red = mb.material(M_TIMBER), mb.material(M_WOOL), mb.material(M_RED)
        top = 3.4
        for x in (-9.0, 9.0):
            kc.tube(mb, np.array([[x, -0.3, 0.0], [x + rng.normal(0, 0.05), top + 0.2, 0.0]]), np.array([0.09, 0.07]),
                    4 if lod else 7, timber, cap_end=True)
        t = np.linspace(0.0, 1.0, 13 if lod else 25)
        cord = np.stack([-9.0 + 18.0 * t, top - 0.9 * 4.0 * t * (1.0 - t), np.zeros_like(t)], -1)
        kc.tube(mb, cord, 0.018, 3 if lod else 4, wool)
        n = 30 if lod else 110
        for k in range(n):
            s_ = (k + rng.uniform(0.2, 0.8)) / n
            x = -9.0 + 18.0 * s_
            y = top - 0.9 * 4.0 * s_ * (1.0 - s_)
            ln = rng.uniform(0.3, 0.85)
            mat = red if rng.random() < 0.3 else wool
            sway = np.array([rng.normal(0, 0.03), 0.0, rng.normal(0, 0.06)])
            kc.tube(mb, np.array([[x, y, 0.0], [x, y - ln, 0.0] + sway]), 0.008 if not lod else 0.012, 3, mat)
            if not lod:
                for kk in range(int(rng.integers(1, 4))):  # the knots: a knot is a name
                    f = (kk + 1) / 4.0
                    kc.rounded_block(mb, np.array([x, y - ln * f, 0.0]) + sway * f, (0.018, 0.022, 0.018), mat,
                                     radius=0.015, seg=1)
        out.append(mb)
    return out


def build_cairn(seed: int = 1505) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("cairn", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("cairn" + ("-lod1" if lod else ""))
        y = 0.0
        r = 0.6
        for k in range(7 if not lod else 3):
            h = rng.uniform(0.16, 0.28) if not lod else 0.5
            kc.rounded_block(mb, (rng.normal(0, 0.04), y + h * 0.5, rng.normal(0, 0.04)), (r, h * 0.5, r * 0.85),
                             mb.material(M_CRAG), rot=kc.rot_y(rng.uniform(0, 3)), radius=min(r, h) * 0.4,
                             seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.03, weather=ROCK,
                             variation=float(rng.random()))
            y += h * 0.92
            r *= 0.8 if not lod else 0.6
        if not lod:
            for k, yy in enumerate((0.35, 0.75)):
                a = np.linspace(0.0, 2 * math.pi, 17)
                rr = 0.58 - yy * 0.25
                ring = np.stack([np.cos(a) * rr, np.full_like(a, yy), np.sin(a) * rr], -1)
                kc.tube(mb, ring, 0.02, 4, mb.material(M_RED if k == 0 else M_WOOL))
                for j in range(5):
                    th = rng.uniform(0, 2 * math.pi)
                    p = np.array([math.cos(th) * rr, yy, math.sin(th) * rr])
                    kc.tube(mb, np.array([p, p + [0, -0.3, 0] + np.array([math.cos(th), 0, math.sin(th)]) * 0.05]),
                            0.008, 3, mb.material(M_RED if (j + k) % 2 else M_WOOL))
        out.append(mb)
    return out


def build_far(seed: int = 1506) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("keth_far_ridges", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("keth_far_ridges" + ("-lod1" if lod else ""))
        a = np.linspace(0.0, 2 * math.pi, (40 if lod else 96) + 1)
        rs = np.array([480.0, 640.0, 820.0, 980.0])
        A, R = np.meshgrid(a, rs)
        n = noise.fbm(np.stack([np.cos(A) * 4.0, R / 300.0, np.sin(A) * 4.0], -1), 4)
        valley = 0.45 + 0.55 * kc.smoothstep(0.2, 0.9, np.abs(np.cos(A * 0.5 - math.pi * 0.5)))  # lower to the south
        Y = (60.0 + (R - 480.0) * 0.6) * valley * (0.55 + 0.9 * n) - 40.0
        Y[0] = -60.0
        grid = np.stack([R * np.sin(A), Y, -R * np.cos(A)], -1)
        col = np.stack([np.zeros_like(Y), np.zeros_like(Y), np.zeros_like(Y), np.full_like(Y, 0.5)], -1)
        kc.quad_strip(mb, grid, mb.material(M_CRAG), uv=np.stack([A * 100.0, Y / 10.0], -1), col=col,
                      uv2=np.array([1.0, 0.5]), flip=False)
        out.append(mb)
    return out


TARGETS = {
    "keth_terrace_ground": build_ground,
    "lit_terrace_wall": build_wall,
    "seep_pool": build_pool,
    "pass_cord": build_cord,
    "cairn": build_cairn,
    "keth_far_ridges": build_far,
}
