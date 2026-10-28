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
  keth_road_switchback a 10 m module of the Cold Road climbing 1 m along +X: laid stones on a 3 m bed, a dry-stone
                       parapet on the drop side (+Z), the cut bank's scree on the uphill side; modules chain end to end.
  keth_scree_slope     a 40 x 40 m scree-and-crag panel rising 18 m toward -Z, its front edge level at y 0.
  woolback_trough      the herders' stone trough, 3 x 0.8 m, and a broken herd-gate, one rail tied with red.
  cloudloom_hall       Cloudloom (keth_pass.md §5): the rock-cut weaving-hall, 24 x 16 m inside, white dressed walls to
                       9 m, the white stone floor, the beam lattice over the open roof, the loom-frame on its dais at
                       the centre, the entrance cut through the +Z wall. Stone, cord and sky: nothing frozen.
  keth_curtain         one beam's hang of keth: 240 cords, 1.2-4 m, undyed and red, knotted, two-sided strips (they cast
                       the floor's writing); origin at the beam's centre, the beam along X, the cords hanging to -Y.
  quellan_house        a dry-stone highland house, two storeys (5.2 m) on a level footing (the layout sinks its back into
                       the slope), a flat turf-edged roof, the door on +Z under a woven awning; origin at the front's
                       foot centre.
  woven_awning         a freestanding woven awning on four poles, 3 x 2.5 m, undyed wool with red weft-bands, sagging.
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

TRI_BUDGET = {"cloudloom_hall": (16000, 1200), "keth_curtain": (4000, 300), "quellan_house": (7000, 500),
              "woven_awning": (1500, 120), "keth_road_switchback": (8000, 500), "keth_scree_slope": (12000, 1000), "woolback_trough": (2000, 150),
              "keth_terrace_ground": (26000, 2400), "lit_terrace_wall": (16000, 1200), "seep_pool": (5000, 300),
              "pass_cord": (7000, 400), "cairn": (2500, 150), "keth_far_ridges": (4000, 1500),
              "quellan_inn": (12000, 700), "quellan_well": (2500, 200), "hesk_dais": (3000, 200)}

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
                # M3-ENV-717 rework (95be611's render): crisper arrises and a deeper joint, each block set a hair
                # proud or back of its neighbours, so the courses read as cut stone, not pillows.
                proud = rng.uniform(-0.05, 0.06)
                kc.rounded_block(mb, (xa + ln * 0.5, cy, fz - WALL_T * 0.5 + proud), (ln * 0.5 - 0.035,
                                 ch * 0.5 - 0.035, WALL_T * 0.5), lit, rot=kc.rot_z(rng.normal(0.0, 0.015)),
                                 radius=0.05, seg=1, noise=noise, disp_m=0.03, disp_period_m=0.6, weather=LIT,
                                 variation=float(rng.random()))
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
    # M3-ENV-717 rework: threads, not ribbons (95be611 read them as pale-blue bands).
    sheets = ((-3.0, 6.4, 0.16), (3.2, 5.6, 0.13), (-0.6, 3.8, 0.22), (4.8, 2.6, 0.18))
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


# ---------------------------------------------------------------------------------------------
# The Cold Road's zone pieces (keth_pass.md §1)
# ---------------------------------------------------------------------------------------------
ROAD_RUN = 10.0
ROAD_W = 3.0
ROAD_RISE = 1.0  # the module climbs 1 m over its 10 m run (a mule-road's 1 in 10)


def build_switchback(seed: int = 1507) -> list[kc.MeshBuilder]:
    """A 10 m laid-stone road module along +X, 3 m wide (z -1.5..1.5), climbing 1 m; the cut bank's foot on -Z, a
    dry-stone parapet on the drop side (+Z). Origin at its start, on the road's centre line; modules chain end to end
    (each starts where the last ended, 1 m up)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("keth_road_switchback", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("keth_road_switchback" + ("-lod1" if lod else ""))
        road = mb.material(M_ROAD)
        hw = ROAD_W * 0.5
        # The road bed (a sloped slab) and, at LOD0, its laid stones.
        n = 3 if lod else 11
        xs = np.linspace(0.0, ROAD_RUN, n)
        bed = np.stack([np.stack([xs, xs * ROAD_RISE / ROAD_RUN - 0.2, np.full(n, z)], -1) for z in (-hw, hw)], 1)
        kc.quad_strip(mb, bed, road, uv=bed[..., [0, 2]] / 1.2, col=(0, 0, 0, 0.5), uv2=(0.9, 0.5))
        if not lod:
            x = 0.0
            while x < ROAD_RUN - 0.1:
                ln = min(rng.uniform(0.6, 1.1), ROAD_RUN - x)
                z = -hw + rng.uniform(0.0, 0.3)
                while z < hw - 0.1:
                    w = min(rng.uniform(0.5, 0.8), hw - z)
                    y = (x + ln * 0.5) * ROAD_RISE / ROAD_RUN
                    kc.rounded_block(mb, (x + ln * 0.5, y - 0.09 + rng.uniform(-0.01, 0.006), z + w * 0.5),
                                     (ln * 0.5 - 0.016, 0.09, w * 0.5 - 0.016), road,
                                     rot=kc.rot_z(math.atan(ROAD_RISE / ROAD_RUN)) @ kc.rot_y(rng.normal(0.0, 0.015)),
                                     radius=0.02, seg=1, noise=noise, disp_m=0.008, weather=ROCK,
                                     variation=float(rng.random()))
                    z += w
                x += ln
        # The parapet on the drop side: dry-laid blocks in two courses, 0.7 m, with gaps where it has slumped.
        x = 0.0
        while x < ROAD_RUN:
            ln = rng.uniform(0.45, 0.8)
            y0 = x * ROAD_RISE / ROAD_RUN
            gap = rng.random() < 0.08
            for c, h in enumerate((0.36, 0.3)):
                if gap and c == 1:
                    continue
                if lod and c == 1:
                    break
                hh = h if not lod else 0.66
                kc.rounded_block(mb, (x + ln * 0.5, y0 + c * 0.36 + hh * 0.5 - 0.05, hw + 0.25),
                                 (ln * 0.5 - 0.02, hh * 0.5, 0.25 - c * 0.04), mb.material(M_CRAG),
                                 rot=kc.rot_y(rng.normal(0.0, 0.05)), radius=0.05, seg=1, noise=None if lod else noise,
                                 disp_m=0.02, weather=ROCK, variation=float(rng.random()))
            x += ln
        # The cut bank's foot on the uphill side: a scree skirt.
        n = 3 if lod else 11
        skirt = np.stack([np.stack([xs, xs * ROAD_RISE / ROAD_RUN - 0.1 + h, np.full(n, -hw - d)], -1)
                          for d, h in ((0.0, 0.0), (0.8, 0.45), (2.0, 1.6))], 1)
        kc.quad_strip(mb, skirt, mb.material(M_SCREE), uv=skirt[..., [0, 2]] / 1.6, col=(0, 0, 0, 0.5), uv2=(0.9, 0.5),
                      flip=True)
        out.append(mb)
    return out


def build_scree_slope(seed: int = 1508) -> list[kc.MeshBuilder]:
    """A 40 x 40 m scree-and-crag panel rising 18 m toward -Z, its +Z edge level at y 0 (where a road module's
    cut bank meets it); crag where it is steep (as keth_terrace_ground). Origin at its front edge's centre."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("keth_scree_slope", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("keth_scree_slope" + ("-lod1" if lod else ""))
        xs = np.linspace(-20.0, 20.0, 9 if lod else 41)
        zs = np.linspace(-40.0, 0.0, 9 if lod else 41)
        X, Z = np.meshgrid(xs, zs)
        n = noise.fbm(np.stack([X / 8.0, np.zeros_like(X), Z / 8.0], -1), 4) - 0.5
        ridge = noise.fbm(np.stack([X / 3.0, np.ones_like(X), Z / 3.0], -1), 3) - 0.5
        Y = 18.0 * kc.smoothstep(0.0, 40.0, -Z) ** 1.2 + n * 4.0 * kc.smoothstep(0.0, 8.0, -Z) \
            + np.clip(ridge, 0.0, None) * 5.0 * kc.smoothstep(6.0, 20.0, -Z)
        P = np.stack([X, Y, Z], -1)
        start_t = mb.triangle_count
        kc.quad_strip(mb, P, mb.material(M_SCREE), uv=np.stack([X, Z], -1) / 3.0, col=(0, 0, 0, 0.5),
                      uv2=np.array([0.9, 0.5]), flip=True)
        pos, tris = np.asarray(mb.pos), np.asarray(mb.tris)[start_t:]
        a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
        ny = np.abs(kc.normalize(np.cross(b - a, c - a))[:, 1])
        i_crag, i_scree = mb.material(M_CRAG), mb.material(M_SCREE)
        mb.tri_mat = mb.tri_mat[:start_t] + [int(i_crag if v < 0.72 else i_scree) for v in ny]
        out.append(mb)
    return out


def build_trough(seed: int = 1509) -> list[kc.MeshBuilder]:
    """The herders' stone trough (3 x 0.8 m, along X) and a broken herd-gate of lashed poles leaning off its end.
    Origin at the trough's foot centre."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("woolback_trough", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("woolback_trough" + ("-lod1" if lod else ""))
        crag = mb.material(M_CRAG)
        for (cx, cy, cz, hx, hy, hz) in ((0.0, 0.08, 0.0, 1.5, 0.08, 0.4),  # base slab
                                         (0.0, 0.36, -0.33, 1.5, 0.22, 0.07), (0.0, 0.36, 0.33, 1.5, 0.22, 0.07),
                                         (-1.43, 0.36, 0.0, 0.07, 0.22, 0.26), (1.43, 0.36, 0.0, 0.07, 0.22, 0.26)):
            kc.rounded_block(mb, (cx, cy, cz), (hx, hy, hz), crag, radius=0.04, seg=1, noise=None if lod else noise,
                             disp_m=0.01, weather=ROCK, variation=float(rng.random()))
        if not lod:  # the gate: two posts, one fallen rail, the other tied on
            t = mb.material(M_TIMBER)
            for p in ((1.9, 0.0, -0.5), (1.9, 0.0, 0.9)):
                kc.tube(mb, np.array([p, [p[0] + rng.normal(0, 0.04), 1.3, p[2]]]), 0.05, 5, t, cap_end=True)
            kc.tube(mb, np.array([[1.9, 1.0, -0.5], [1.9, 1.05, 0.9]]), 0.035, 5, t)
            kc.tube(mb, np.array([[1.9, 0.6, -0.5], [2.6, 0.05, 1.2]]), 0.035, 5, t)  # the broken rail, down
            kc.tube(mb, np.array([[1.86, 1.0, 0.9], [1.94, 0.94, 0.9]]), 0.045, 4, mb.material(M_RED))
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Quellan and Cloudloom (keth_pass.md §5)
# ---------------------------------------------------------------------------------------------
HALL_HALF = (12.0, 8.0)  # x, z inside
HALL_H = 9.0
BEAM_Y = 8.6
BEAM_SPACING = 2.0


def build_cloudloom_hall(seed: int = 1510) -> list[kc.MeshBuilder]:
    out = []
    hx, hz = HALL_HALF
    for lod in (False, True):
        rng = kc.rng_for("cloudloom_hall", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("cloudloom_hall" + ("-lod1" if lod else ""))
        white, crag, timber = mb.material(M_LIT), mb.material(M_CRAG), mb.material(M_TIMBER)
        # The floor: large white slabs (one plate at LOD1).
        if lod:
            kc.rounded_block(mb, (0.0, -0.1, 0.0), (hx, 0.1, hz), white, radius=0.02, seg=1)
        else:
            for x in np.arange(-hx, hx - 0.01, 2.0):
                for z in np.arange(-hz, hz - 0.01, 2.0):
                    kc.rounded_block(mb, (x + 1.0, -0.1 + rng.uniform(-0.004, 0.0), z + 1.0), (0.985, 0.1, 0.985),
                                     white, radius=0.015, seg=1, weather=LIT, variation=float(rng.random()))
        # The walls: dressed white inside, the summit's rough crag outside (a thick rock mass), the entrance on +Z.
        for (cx, cz, sx, sz) in ((0.0, -hz - 1.5, hx + 3.0, 1.5), (-hx - 1.5, 0.0, 1.5, hz), (hx + 1.5, 0.0, 1.5, hz)):
            kc.rounded_block(mb, (cx, HALL_H * 0.5, cz), (sx, HALL_H * 0.5, sz), white, radius=0.06, seg=1,
                             noise=None if lod else noise, disp_m=0.01, weather=LIT, variation=float(rng.random()))
            kc.rounded_block(mb, (cx * 1.12, HALL_H * 0.45, cz * 1.12), (sx * 1.05 + 0.6, HALL_H * 0.55, sz * 1.05 + 0.6),
                             crag, radius=0.6, seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.4,
                             weather=ROCK, variation=float(rng.random()))
        for sx in (-1.0, 1.0):  # the front wall, either side of the 3 m entrance
            kc.rounded_block(mb, (sx * (hx + 3.0 + 1.5) * 0.5, HALL_H * 0.5, hz + 1.5),
                             ((hx + 3.0 - 1.5) * 0.5, HALL_H * 0.5, 1.5), white, radius=0.06, seg=1, weather=LIT,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, HALL_H - 1.5, hz + 1.5), (1.5, 1.5, 1.5), white, radius=0.06, seg=1, weather=LIT)
        # The beam lattice over the open roof: main beams across X every 2 m, two long ties along Z.
        for z in np.arange(-hz + 1.0, hz, BEAM_SPACING):
            kc.rounded_block(mb, (0.0, BEAM_Y, z), (hx + 0.6, 0.14, 0.12), timber, radius=0.03, seg=1,
                             noise=None if lod else noise, disp_m=0.008)
        for x in (-hx * 0.5, hx * 0.5):
            kc.rounded_block(mb, (x, BEAM_Y + 0.28, 0.0), (0.12, 0.14, hz + 0.6), timber, radius=0.03, seg=1)
        # The loom-frame on its dais at the centre.
        kc.rounded_block(mb, (0.0, 0.15, 0.0), (2.4, 0.15, 1.6), white, radius=0.04, seg=1, weather=LIT)
        for sx in (-1.0, 1.0):
            kc.tube(mb, np.array([[sx * 1.8, 0.3, 0.0], [sx * 1.8, 3.4, 0.0]]), 0.1, 4 if lod else 8, timber,
                    cap_end=True)
        for y in (0.9, 3.1):
            kc.tube(mb, np.array([[-1.9, y, 0.0], [1.9, y, 0.0]]), 0.07, 4 if lod else 8, timber)
        if not lod:  # the warp: undyed and red threads strung between the beams of the loom
            for k, x in enumerate(np.linspace(-1.6, 1.6, 33)):
                kc.tube(mb, np.array([[x, 0.95, 0.0], [x, 3.05, 0.0]]), 0.006, 3, mb.material(M_RED if k % 6 == 0 else M_WOOL))
        out.append(mb)
    return out


def build_keth_curtain(seed: int = 1511) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("keth_curtain", seed)
        mb = kc.MeshBuilder("keth_curtain" + ("-lod1" if lod else ""))
        wool, red = mb.material(M_WOOL), mb.material(M_RED)
        n = 60 if lod else 240
        for k in range(n):
            x = rng.uniform(-3.0, 3.0)
            z = rng.normal(0.0, 0.05)
            ln = rng.uniform(1.2, 4.0)
            w = (0.012 if not lod else 0.05)
            mat = red if rng.random() < 0.28 else wool
            sway = np.array([rng.normal(0, 0.04), 0.0, rng.normal(0, 0.08)])
            top = np.array([x, -0.14, z])
            bot = top + np.array([0.0, -ln, 0.0]) + sway
            side = np.array([w, 0.0, 0.0])
            grid = np.array([[top - side, top + side], [bot - side, bot + side]])
            for flip in (False, True):
                kc.quad_strip(mb, grid, mat, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0, 0, 0, 0.3),
                              uv2=(0.9, 0.5), flip=flip, smooth=False)
            if not lod:
                for kk in range(int(rng.integers(1, 4))):  # the knots (a knot is a name): a short, wider band
                    c = top + (bot - top) * (kk + 1) / 4.0
                    k_side = np.array([0.022, 0.0, 0.0])
                    knot = np.array([[c - k_side + [0, 0.02, 0], c + k_side + [0, 0.02, 0]],
                                     [c - k_side - [0, 0.02, 0], c + k_side - [0, 0.02, 0]]]) + [0.0, 0.0, 0.004]
                    for flip in (False, True):
                        kc.quad_strip(mb, knot + ([0.0, 0.0, -0.008] if flip else 0.0), mat,
                                      uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0, 0, 0, 0.3),
                                      uv2=(0.8, 0.5), flip=flip, smooth=False)
        out.append(mb)
    return out



def _dry_stone_walls(mb, rng, noise, crag: int, w: float, d: float, h: float, *, door_half: float = 0.6,
                     door_h: float = 2.0, openings=()) -> None:
    """Dry-laid courses: rows of blocks round the four walls (the front at z 0, the back at -d), 0.35 m courses, the
    joints staggered; the door at x 0 in the front, and `openings` [(x0, x1, y0, y1)] left in the front wall."""
    y = 0.0
    course = 0
    while y < h - 0.01:
        ch = min(rng.uniform(0.3, 0.4), h - y)
        for (a, b, z_or_x, along_x) in ((-w * 0.5, w * 0.5, 0.0, True), (-w * 0.5, w * 0.5, -d, True),
                                        (-d, 0.0, -w * 0.5, False), (-d, 0.0, w * 0.5, False)):
            t = a + (0.3 if course % 2 else 0.0)
            while t < b - 0.05:
                ln = min(rng.uniform(0.5, 0.9), b - t)
                door = along_x and z_or_x == 0.0 and abs(t + ln * 0.5) < door_half and y < door_h
                door = door or (along_x and z_or_x == 0.0 and any(o[0] < t + ln * 0.5 < o[1] and o[2] <= y < o[3]
                                                                   for o in openings))
                if not door:
                    c = (t + ln * 0.5, y + ch * 0.5, z_or_x) if along_x else (z_or_x, y + ch * 0.5, t + ln * 0.5)
                    half = (ln * 0.5 - 0.015, ch * 0.5 - 0.01, 0.25) if along_x else (0.25, ch * 0.5 - 0.01, ln * 0.5 - 0.015)
                    kc.rounded_block(mb, c, half, crag, radius=0.04, seg=1, noise=noise, disp_m=0.015,
                                     weather=ROCK, variation=float(rng.random()))
                t += ln
        y += ch
        course += 1

def build_quellan_house(seed: int = 1512) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("quellan_house", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("quellan_house" + ("-lod1" if lod else ""))
        crag, timber = mb.material(M_CRAG), mb.material(M_TIMBER)
        w, d, h = 6.0, 6.0, 5.2
        if lod:
            kc.rounded_block(mb, (0.0, h * 0.5, -d * 0.5), (w * 0.5, h * 0.5, d * 0.5), crag, radius=0.1, seg=1)
        else:
            _dry_stone_walls(mb, rng, noise, crag, w, d, h)
            kc.rounded_block(mb, (0.0, 2.05, 0.05), (0.7, 0.08, 0.3), timber, radius=0.02, seg=1)  # the lintel
        # The flat roof, its turf edge, and the door's woven awning on two poles.
        kc.rounded_block(mb, (0.0, h + 0.12, -d * 0.5), (w * 0.5 + 0.2, 0.12, d * 0.5 + 0.2), timber, radius=0.03, seg=1)
        kc.rounded_block(mb, (0.0, h + 0.3, -d * 0.5), (w * 0.5 + 0.15, 0.08, d * 0.5 + 0.15), mb.material(M_GRASS),
                         radius=0.06, seg=1, noise=None if lod else noise, disp_m=0.03)
        _awning(mb, rng, (0.0, 0.0, 1.2), 2.4, 1.8, 2.3, lod)
        out.append(mb)
    return out


def _awning(mb, rng, centre, wx: float, dz: float, h: float, lod: bool, *, poles: int = 2) -> None:
    """A woven awning: a sagging cloth from the house (or two back poles) at `h` to two front poles at h - 0.25,
    undyed with red weft-bands across it."""
    cx, cy, cz = centre
    timber = mb.material(M_TIMBER)
    front = cz + dz * 0.5
    back = cz - dz * 0.5
    pole_zs = (front,) if poles == 2 else (front, back)
    for z in pole_zs:
        for sx in (-1.0, 1.0):
            top = h - (0.25 if z == front else 0.0)
            kc.tube(mb, np.array([[cx + sx * wx * 0.5, cy, z], [cx + sx * wx * 0.5, cy + top, z]]), 0.035,
                    4 if lod else 6, timber, cap_end=True)
    nu, nv = (3, 3) if lod else (9, 7)
    u = np.linspace(-0.5, 0.5, nu)
    v = np.linspace(0.0, 1.0, nv)
    U, V = np.meshgrid(u, v)
    X = cx + U * wx
    Z = back + V * dz
    Y = cy + h - 0.25 * V - 0.18 * np.sin(V * math.pi) * (1.0 - (2.0 * U) ** 2)
    grid = np.stack([X, Y, Z], -1)
    bands = (np.floor(V[:-1, :-1] * 6.0) % 3 == 1)
    for flip in (False, True):
        start = mb.triangle_count
        kc.quad_strip(mb, grid, mb.material(M_WOOL), uv=np.stack([U, V], -1) * 3.0, col=(0, 0, 0, 0.3), uv2=(0.9, 0.5),
                      flip=flip, smooth=False)
        if not lod:  # the red weft-bands
            red = mb.material(M_RED)
            for k, b in enumerate(np.repeat(bands.reshape(-1), 2)):
                if b:
                    mb.tri_mat[start + k] = red


def build_woven_awning(seed: int = 1513) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("woven_awning", seed)
        mb = kc.MeshBuilder("woven_awning" + ("-lod1" if lod else ""))
        _awning(mb, rng, (0.0, 0.0, 0.0), 3.0, 2.5, 2.4, lod, poles=4)
        out.append(mb)
    return out



# ---------------------------------------------------------------------------------------------
# M3-ENV-734: Quellan's inn and well, Hesk's dais in Cloudloom (act1-chapters' Ch12 greybox, M4-C12-02)
# ---------------------------------------------------------------------------------------------
INN_W, INN_D, INN_H = 10.0, 8.0, 5.0
INN_WINDOWS = ((-3.6, -2.4, 1.0, 2.2), (2.4, 3.6, 1.0, 2.2), (-3.6, -2.4, 3.0, 4.0), (2.4, 3.6, 3.0, 4.0))


def build_quellan_inn(seed: int = 1514) -> list[kc.MeshBuilder]:
    """Quellan's inn (the greybox's Inn, 10 x 8 x 5 m; Ysolde's confession to Asha that night): the houses' dry
    stone, wider, two rows of shuttered windows in the front, a timber gallery along it under the eaves, the flat
    turf roof, and the red banner hung from a bracket over the door (InnBanner). Front +Z at z 0."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("quellan_inn", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("quellan_inn" + ("-lod1" if lod else ""))
        crag, timber, red = mb.material(M_CRAG), mb.material(M_TIMBER), mb.material(M_RED)
        w, d, h = INN_W, INN_D, INN_H
        if lod:
            kc.rounded_block(mb, (0.0, h * 0.5, -d * 0.5), (w * 0.5, h * 0.5, d * 0.5), crag, radius=0.1, seg=1)
        else:
            _dry_stone_walls(mb, rng, noise, crag, w, d, h, door_half=0.75, door_h=2.3, openings=INN_WINDOWS)
            kc.rounded_block(mb, (0.0, 2.36, 0.05), (0.95, 0.09, 0.3), timber, radius=0.02, seg=1)  # the door's lintel
            for x0, x1, y0, y1 in INN_WINDOWS:  # the dark openings, their lintels and a shutter each side
                cx = (x0 + x1) * 0.5
                kc.rounded_block(mb, (cx, (y0 + y1) * 0.5, -0.12), ((x1 - x0) * 0.5, (y1 - y0) * 0.5, 0.02),
                                 mb.material(M_DARK), radius=0.01, seg=1)
                kc.rounded_block(mb, (cx, y1 + 0.06, 0.05), ((x1 - x0) * 0.5 + 0.15, 0.06, 0.28), timber, radius=0.02,
                                 seg=1)
                for sx in (-1.0, 1.0):
                    kc.rounded_block(mb, (cx + sx * ((x1 - x0) * 0.5 + 0.3), (y0 + y1) * 0.5, 0.3),
                                     (0.28, (y1 - y0) * 0.5, 0.025), timber, rot=kc.rot_y(sx * 0.35), radius=0.01,
                                     seg=1)
            # The gallery: a timber walk along the front at the upper floor, on brackets, with a rail.
            gy = 2.75
            kc.rounded_block(mb, (0.0, gy, 0.6), (w * 0.5 - 0.3, 0.06, 0.55), timber, radius=0.02, seg=1)
            for x in np.linspace(-w * 0.5 + 0.6, w * 0.5 - 0.6, 6):
                kc.tube(mb, np.array([[x, gy - 0.7, 0.26], [x, gy - 0.06, 1.05]]), 0.05, 5, timber)
                kc.tube(mb, np.array([[x, gy, 1.1], [x, gy + 0.95, 1.1]]), 0.035, 5, timber, cap_end=True)
            kc.tube(mb, np.array([[-w * 0.5 + 0.4, gy + 0.95, 1.1], [w * 0.5 - 0.4, gy + 0.95, 1.1]]), 0.04, 5, timber)
        kc.rounded_block(mb, (0.0, h + 0.12, -d * 0.5), (w * 0.5 + 0.25, 0.12, d * 0.5 + 0.25), timber, radius=0.03,
                         seg=1)
        kc.rounded_block(mb, (0.0, h + 0.3, -d * 0.5), (w * 0.5 + 0.2, 0.08, d * 0.5 + 0.2), mb.material(M_GRASS),
                         radius=0.06, seg=1, noise=None if lod else noise, disp_m=0.03)
        # The red banner on its bracket by the door (the greybox's InnBanner at x 0, y 2.3-4.1, z +0.1).
        kc.tube(mb, np.array([[0.0, 4.2, 0.05], [0.0, 4.2, 0.75]]), 0.03, 4 if lod else 6, timber, cap_end=True)
        nu, nv = (2, 2) if lod else (4, 8)
        u = np.linspace(-0.6, 0.6, nu)
        v = np.linspace(0.0, 1.0, nv)
        U, V = np.meshgrid(u, v)
        grid = np.stack([U, 4.15 - V * 1.8, 0.7 + 0.04 * np.sin(V * 3.0) + 0.02 * U], -1)
        for flip in (False, True):
            kc.quad_strip(mb, grid + np.array([0.0, 0.0, 0.004 if flip else 0.0]), red, uv=np.stack([U, V], -1),
                          col=(0, 0, 0, 0.3), uv2=(0.9, 0.5), flip=flip, smooth=False)
        out.append(mb)
    return out


def build_quellan_well(seed: int = 1515) -> list[kc.MeshBuilder]:
    """The square's well (the greybox's Well, 1.6 m): a ring of dry-laid stones 0.9 m high, two timber posts and
    a windlass across it, its rope down to a bucket on the rim, and a stone trough beside it."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("quellan_well", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("quellan_well" + ("-lod1" if lod else ""))
        crag, timber = mb.material(M_CRAG), mb.material(M_TIMBER)
        if lod:
            kc.tube(mb, np.array([[0.0, 0.0, 0.0], [0.0, 0.9, 0.0]]), 0.8, 8, crag, cap_end=True)
        else:
            for course, y in enumerate((0.15, 0.45, 0.75)):
                n = 9
                for k in range(n):
                    a = 2 * math.pi * (k + 0.5 * (course % 2)) / n
                    kc.rounded_block(mb, (math.cos(a) * 0.65, y, math.sin(a) * 0.65), (0.25, 0.14, 0.16), crag,
                                     rot=kc.rot_y(-a), radius=0.04, seg=1, noise=noise, disp_m=0.015, weather=ROCK,
                                     variation=float(rng.random()))
            kc.tube(mb, np.array([[0.0, -0.4, 0.0], [0.0, 0.85, 0.0]]), 0.5, 10, mb.material(M_DARK))  # the dark shaft
        for sx in (-1.0, 1.0):
            kc.tube(mb, np.array([[sx * 0.85, 0.0, 0.0], [sx * 0.85, 1.9, 0.0]]), 0.06, 4 if lod else 6, timber,
                    cap_end=True)
        kc.tube(mb, np.array([[-0.9, 1.6, 0.0], [0.9, 1.6, 0.0]]), 0.08, 4 if lod else 8, timber, cap_start=True,
                cap_end=True)
        if not lod:
            kc.tube(mb, np.array([[0.9, 1.6, 0.0], [1.05, 1.6, 0.0], [1.05, 1.4, 0.15]]), 0.02, 4, timber)  # the crank
            kc.tube(mb, np.array([[0.1, 1.55, 0.0], [0.1, 1.0, 0.0], [0.35, 0.95, 0.55]]), 0.012, 4,
                    mb.material(M_WOOL))  # the rope
            kc.tube(mb, np.array([[0.4, 0.9, 0.62], [0.4, 1.15, 0.62]]), np.array([0.13, 0.15]), 8, timber,
                    cap_start=True)  # the bucket on the rim
            kc.rounded_block(mb, (1.6, 0.3, 0.2), (0.7, 0.3, 0.3), crag, radius=0.05, seg=2, noise=noise,
                             disp_m=0.01, weather=ROCK)  # the trough
            kc.rounded_block(mb, (1.6, 0.58, 0.2), (0.6, 0.02, 0.2), mb.material(M_DARK), radius=0.01, seg=1)
        out.append(mb)
    return out


def build_hesk_dais(seed: int = 1516) -> list[kc.MeshBuilder]:
    """Hesk's place at the north end of Cloudloom's hall (the greybox's HeskDais, 6 x 3 x 0.4): the hall's white
    stone in two steps, a woven wool mat with red weft-bands on it, and a low stone seat at its back."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hesk_dais", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("hesk_dais" + ("-lod1" if lod else ""))
        white = mb.material(M_LIT)
        kc.rounded_block(mb, (0.0, 0.1, 0.0), (3.0, 0.1, 1.5), white, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, 0.3, -0.2), (2.7, 0.1, 1.2), white, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, 0.62, -1.05), (0.6, 0.22, 0.3), white, radius=0.04, seg=1 if lod else 2)
        if not lod:
            kc.rounded_block(mb, (0.0, 0.415, -0.1), (1.6, 0.015, 0.9), mb.material(M_WOOL), radius=0.01, seg=1,
                             noise=noise, disp_m=0.004)
            for z in (-0.6, 0.0, 0.6):  # the red weft-bands across the mat
                kc.rounded_block(mb, (0.0, 0.432, z - 0.1), (1.6, 0.003, 0.06), mb.material(M_RED), radius=0.002,
                                 seg=1)
        out.append(mb)
    return out

TARGETS = {
    "quellan_inn": build_quellan_inn,
    "quellan_well": build_quellan_well,
    "hesk_dais": build_hesk_dais,
    "keth_terrace_ground": build_ground,
    "lit_terrace_wall": build_wall,
    "seep_pool": build_pool,
    "pass_cord": build_cord,
    "cairn": build_cairn,
    "keth_far_ridges": build_far,
    "keth_road_switchback": build_switchback,
    "keth_scree_slope": build_scree_slope,
    "woolback_trough": build_trough,
    "cloudloom_hall": build_cloudloom_hall,
    "keth_curtain": build_keth_curtain,
    "quellan_house": build_quellan_house,
    "woven_awning": build_woven_awning,
}
