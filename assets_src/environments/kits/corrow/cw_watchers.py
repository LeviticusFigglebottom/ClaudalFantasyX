"""The Watchers and Liss's hoist (corrow.md §2). Pure numpy; see cw_common.py.

  watcher_head    a parapet merlon carved as a colossal face: 2.4 m tall, 2.1 m wide, 1.2 m deep, four
                  courses of laterite (the joints run through the face), the face to +Z (the sea). Origin
                  at the centre of its base, which stands on the parapet course (+12.9 m). The body is a
                  lofted squircle, narrower at the neck, its front displaced by cw_common.watcher_face.
  watcher_relief  the same face carved 3.0 m tall in a 3.4 x 3.6 m panel to set into the sea face. Origin
                  at the panel's bottom centre on the wall's face, leaning back 12 deg like the batter; the
                  frame's outer edge sinks 3 cm behind the face so no seam shows. Rows sit on the 0.5 m
                  course joints when the origin is placed on one.
  liss_hoist      Liss's rope-and-block hoist, in the head's frame (place it with the same transform as the
                  head it is bolted into): a 5.5 m salvaged spar stepped in an iron shoe on the inner kerb,
                  raking 35 deg out over the inner face; its head-rope back to two iron strap-plates bolted
                  into the back of the Watcher's head; side guys to ring-bolts in the kerb; a double block at
                  the tip and the fall of rope to a sling-board 9 m below it, part-way down the face. Plain rope and iron: nothing bound.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
from cw_common import kc

TRI_BUDGET = {"watcher_head": (10500, 500), "watcher_relief": (7000, 300), "liss_hoist": (3000, 300)}

HEAD_H = 2.4
HEAD_HALF_W = 1.05
HEAD_FRONT = 0.55
HEAD_BACK = 0.6
FACE_H = 2.3
FACE_BASE = 0.06
HEAD_COURSE = 0.6
SQUIRCLE_P = 3.6


def _head_width(v):
    """Half-width (m) at height v: a neck at the base, the jaw widening, the crown a touch narrower."""
    v = np.asarray(v, float)
    return HEAD_HALF_W * (0.78 + 0.22 * kc.smoothstep(0.05, 0.75, v) - 0.1 * kc.smoothstep(1.75, 2.45, v))


def _head_depth(v, front: bool):
    v = np.asarray(v, float)
    d = HEAD_FRONT if front else HEAD_BACK
    return d * (0.9 + 0.1 * kc.smoothstep(0.05, 0.6, v))


def _sq(t):
    """Squircle coordinate: sign(t)|t|^(2/p)."""
    return np.sign(t) * np.abs(t) ** (2.0 / SQUIRCLE_P)


def _joint(v, course: float, depth: float, width: float):
    f = v / course - np.floor(v / course)
    d = np.minimum(f, 1.0 - f) * course
    return -depth * (1.0 - kc.smoothstep(0.0, width, d))


BACK_PERIMETER_M = 4.2  # metres round the back, side to side (the back's u)
BLOCK_M = 0.7  # the laterite blocks' length in a course; alternate courses break joint by half a block
LOCK_M = 0.42  # the carved hair locks' spacing down the back
BAND_Y = 1.05  # the carved headband round the back of the head
EAR_Y = 1.45  # the carved ears' centre height (the face's eye line is about 1.6 m)
CROWN_RISE_M = 0.12  # M3-ENV-712: the crown domes like a skull, not a barrel's lid


def _carved_back(v, u, a, rng) -> np.ndarray:
    """M3-ENV-712 (act1-chapters' Ch9 road render: from the parapet walk the heads' backs read as smooth barrels):
    the back as built and carved. Each course's blocks with vertical joints, staggered, each block a little proud
    or sunk; the hair in heavy vertical locks above the neck, bound by a headband that runs round to the ears; the
    ears themselves carved proud on both sides. `a` is the squircle angle (back centre at -pi/2). Displacement (m)
    along the outward normal."""
    sn, cs = np.sin(a), np.cos(a)
    course = np.floor(v / HEAD_COURSE).astype(int)
    stagger = (course % 2) * 0.5 * BLOCK_M
    block = np.floor((u + stagger) / BLOCK_M).astype(int)
    proud = rng.normal(0.0, 0.012, (8, 16))[course.clip(0, 7), block.clip(0, 15)]
    f = (u + stagger) / BLOCK_M - np.floor((u + stagger) / BLOCK_M)
    vjoint = -0.018 * (1.0 - kc.smoothstep(0.0, 0.03 / BLOCK_M, np.minimum(f, 1.0 - f)))
    back_w = kc.smoothstep(-0.2, -0.6, sn)  # 0 on the cheeks and ears, 1 across the back
    lock = 0.5 + 0.5 * np.cos(2.0 * np.pi * u / LOCK_M)
    hair = back_w * kc.smoothstep(0.5, 0.8, v) * (0.075 * lock ** 1.5 - 0.02)
    band_v = np.exp(-(((v - BAND_Y) / 0.09) ** 2))
    band = 0.055 * band_v * kc.smoothstep(0.3, -0.05, sn)
    ear = 0.11 * np.abs(cs) ** 10 * np.exp(-(((v - EAR_Y) / 0.26) ** 2)) * (1.0 - band_v)
    return proud + vjoint + np.where(np.abs(v - BAND_Y) < 0.15, 0.0, hair) + band + ear


def head(name: str, seed: int, *, lod: bool, carving: cw.FaceCarving = cw.CARVING_A, base=None,
         back_sweep: float = 2.0 * np.pi - 0.52) -> kc.MeshBuilder:
    """One Watcher's head. M3-ENV-04B: `carving` picks the face (cw_common.CARVING_A is the parapet row's);
    `base(angle) -> height` lifts the bottom ring onto a broken line (the fallen and cracked heads, whose
    necks sheared; angle as the squircle's, radians), the rows spread between it and the crown; and
    `back_sweep` is the back's arc (the default is M3-ENV-04's, which laps over the face's hidden inside; the
    broken heads pass pi + 0.52, the exact remainder of the front's arc, so the base ring closes once)."""
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    mat = mb.material(cw.M_CARVED)
    rows = 10 if lod else 61  # 0.04 m: the course joints (every 0.6 m) fall on rows
    vs = np.linspace(0.0, HEAD_H, rows)
    # Front: columns across the face (dense); back: around the sides and back (sparse).
    nf, nb = (9, 9) if lod else (43, 41)
    tf = np.linspace(-1.0, 1.0, nf)
    tb = np.linspace(0.0, 1.0, nb)
    start_v, start_t = mb.vertex_count, mb.triangle_count
    V, TF = np.meshgrid(vs, tf, indexing="ij")
    # Front points: x across the squircle's front arc (angle 15..165 deg), z its depth.
    a = np.pi * 0.5 - TF * (np.pi * 0.5 - 0.26)
    if base is not None:
        b = base(a)
        V = b + (HEAD_H - b) * V / HEAD_H
    w = _head_width(V)
    x = w * _sq(np.cos(a))
    z = _head_depth(V, True) * _sq(np.sin(a))
    if lod:
        d = cw.watcher_face(x, V - FACE_BASE, FACE_H, fade=False, carving=carving) * 0.6
    else:
        d = cw.watcher_face(x, V - FACE_BASE, FACE_H, fade=False, carving=carving)
    edge = 1.0 - kc.smoothstep(0.78, 0.97, np.abs(x) / w)
    d = d * edge
    if not lod:
        d = d + _joint(V, HEAD_COURSE, 0.012, 0.03) + (noise.fbm(np.stack([x, V, z], -1) / 0.35, 3) - 0.5) * 0.012
    front = np.stack([x, V, z + d], axis=-1)
    wear = np.clip(cw.watcher_wear(d, FACE_H) + (noise.fbm(front / 0.5, 2) - 0.5) * 0.3, 0, 1)
    salt = np.clip(0.25 + 0.4 * (1.0 - kc.smoothstep(-0.01, 0.03, d)) * (noise.fbm(front / 0.4, 2)), 0, 1)
    col = np.stack([np.zeros_like(V), salt, np.full_like(V, 0.15), wear], axis=-1)
    ao = np.clip(1.0 - np.clip(-d / 0.05, 0, 1) * 0.45 - (1.0 - kc.smoothstep(0.0, 0.3, V)) * 0.25, 0.3, 1.0)
    uv = np.stack([x, V], axis=-1)
    uv2 = np.stack([ao, np.full_like(V, float(rng.random()))], axis=-1)
    cw.grid_surface(mb, front, mat, outward=np.array([0.0, 0.0, 1.0]), uv=uv, col=col, uv2=uv2, smooth=False)
    # Sides and back: from the front's right edge (angle 15 deg) round the back to its left edge (165 deg).
    V2, TB = np.meshgrid(vs, tb, indexing="ij")
    a2 = 0.26 - TB * back_sweep
    if base is not None:
        b2 = base(a2)
        V2 = b2 + (HEAD_H - b2) * V2 / HEAD_H
    w2 = _head_width(V2)
    sn = np.sin(a2)
    z2 = np.where(sn >= 0, _head_depth(V2, True), _head_depth(V2, False)) * _sq(sn)
    x2 = w2 * _sq(np.cos(a2))
    back = np.stack([x2, V2, z2], axis=-1)
    if not lod:
        nrm2 = kc.normalize(np.stack([x2 / w2 ** 2, np.zeros_like(V2), z2 / 0.36], -1))
        disp = _joint(V2, HEAD_COURSE, 0.014, 0.03) + (noise.fbm(back / 0.4, 3) - 0.5) * 0.02
        disp = disp + _carved_back(V2, TB * BACK_PERIMETER_M, a2, rng)
        back = back + nrm2 * disp[..., None]
    col2 = np.stack([np.zeros_like(V2), np.full_like(V2, 0.3), np.full_like(V2, 0.12),
                     np.clip(0.5 + (noise.fbm(back / 0.6, 2) - 0.5) * 0.6, 0, 1)], axis=-1)
    uv2b = np.stack([np.clip(0.7 + 0.3 * kc.smoothstep(0.0, 0.4, V2), 0, 1), np.full_like(V2, 0.5)], axis=-1)
    # The perimeter length for u (metres round the back).
    uvb = np.stack([TB * 4.2, V2], axis=-1)
    cw.grid_surface(mb, back, mat, outward=np.stack([x2, np.zeros_like(x2), z2], -1), uv=uvb, col=col2, uv2=uv2b,
                    smooth=False)
    # The crown's top: a shallow dome closing the last ring.
    ring_f = front[-1]
    ring_b = back[-1][1:-1]
    ring = np.vstack([ring_f, ring_b])
    c = ring.mean(axis=0) + np.array([0.0, 0.05 if lod else CROWN_RISE_M, 0.0])
    cb = mb.add_vertices(np.vstack([ring, c[None]]), np.tile(kc.UP, (len(ring) + 1, 1)),
                         np.vstack([ring[:, [0, 2]], c[None, [0, 2]]]), np.tile([0.85, 0.5], (len(ring) + 1, 1)),
                         np.tile([0.0, 0.35, 0.1, 0.7], (len(ring) + 1, 1)))
    n = len(ring)
    for k in range(n):
        p0, p1 = ring[k], ring[(k + 1) % n]
        nrm = np.cross(p1 - c, p0 - c)
        if nrm[1] >= 0:
            mb.add_tri(cb + n, cb + (k + 1) % n, cb + k, mat)
        else:
            mb.add_tri(cb + n, cb + k, cb + (k + 1) % n, mat)
    kc.recompute_normals(mb, start_v, start_t)
    return mb


def build_head(seed: int = 821) -> list[kc.MeshBuilder]:
    return [head("watcher_head", seed, lod=False), head("watcher_head", seed, lod=True)]


# ---------------------------------------------------------------------------------------------
# The sea-face relief
# ---------------------------------------------------------------------------------------------
RELIEF_W, RELIEF_H, RELIEF_FACE_H = 3.4, 3.6, 3.0
RELIEF_LEAN = math.tan(math.radians(cw.SEA_BATTER_DEG))


def _relief_rows(lod: bool) -> np.ndarray:
    if lod:
        return np.linspace(0.0, RELIEF_H, 13)
    base = np.linspace(0.0, RELIEF_H, 58)
    joints = []
    for k in range(1, int(RELIEF_H / cw.COURSE_M) + 1):
        y = k * cw.COURSE_M
        joints += [y - 0.04, y, y + 0.04]
    ys = np.unique(np.round(np.clip(np.concatenate([base, joints]), 0.0, RELIEF_H), 5))
    # Drop rows that crowd a joint row (keeps the grid even).
    keep = [ys[0]]
    for y in ys[1:]:
        if y - keep[-1] > 0.02 or any(abs(y - j) < 1e-6 for j in joints):
            keep.append(y)
    return np.unique(np.asarray(keep))


def relief(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    mat = mb.material(cw.M_CARVED)
    ys = _relief_rows(lod)
    xs = np.linspace(-RELIEF_W * 0.5, RELIEF_W * 0.5, 13 if lod else 49)
    X, Y = np.meshgrid(xs, ys)
    face_v = Y - (RELIEF_H - RELIEF_FACE_H) * 0.5
    d = cw.watcher_face(X, face_v, RELIEF_FACE_H)
    # The niche: the face is carved out of a field sunk 3 cm into the blocks, with a bevelled edge; the
    # panel's own border sits 8 mm proud of the wall's face and its outer edge sinks behind it, so no seam.
    ex = RELIEF_W * 0.5 - np.abs(X)
    ey = np.minimum(Y, RELIEF_H - Y)
    e = np.minimum(ex, ey)
    border = 0.008 * kc.smoothstep(0.0, 0.04, e)
    sink = -0.03 * (1.0 - kc.smoothstep(0.0, 0.04, e))
    inner = kc.smoothstep(0.14, 0.24, e)  # the sunk field
    disp = d + border + sink - 0.03 * inner
    if not lod:
        disp = disp + cw.course_profile(Y, np.zeros(64), groove_m=0.014, set_m=0.0, base_y=0.0) * inner \
            + (noise.fbm(np.stack([X, Y, d], -1) / 0.4, 3) - 0.5) * 0.012
    nz, ny = math.cos(math.radians(cw.SEA_BATTER_DEG)), math.sin(math.radians(cw.SEA_BATTER_DEG))
    P = np.stack([X, Y + disp * ny, -Y * RELIEF_LEAN + disp * nz], axis=-1)
    wear = np.clip(cw.watcher_wear(d, RELIEF_FACE_H) + (noise.fbm(P / 0.6, 2) - 0.5) * 0.3, 0, 1)
    breakup = noise.fbm(P / 0.8, 2)
    salt = np.clip((0.35 + 0.5 * (1.0 - kc.smoothstep(-0.01, 0.04, d))) * (0.5 + breakup), 0, 1)
    col = np.stack([np.zeros_like(X), salt, np.clip(0.2 + 0.3 * breakup, 0, 1), wear], axis=-1)
    ao = np.clip(1.0 - np.clip(-d / 0.06, 0, 1) * 0.5, 0.3, 1.0)
    cw.grid_surface(mb, P, mat, outward=np.array([0.0, ny, nz]), uv=np.stack([X, Y], -1), col=col,
                    uv2=np.stack([ao, np.full_like(X, float(rng.random()))], -1))
    return mb


def build_relief(seed: int = 831) -> list[kc.MeshBuilder]:
    return [relief("watcher_relief", seed, lod=False), relief("watcher_relief", seed, lod=True)]


# ---------------------------------------------------------------------------------------------
# Liss's hoist
# ---------------------------------------------------------------------------------------------
KERB_TOP_LOCAL = cw.WALK_Y + cw.KERB[2] - (cw.WALK_Y + cw.PARAPET[2])  # -0.4: kerb top in the head's frame
HEAD_Z_ON_WALL = (cw.PARAPET[0] + cw.PARAPET[1]) * 0.5  # the head stands at wall z 3.6
KERB_Z_LOCAL = (cw.KERB[0] + cw.KERB[1]) * 0.5 - HEAD_Z_ON_WALL  # -6.3
SPAR_M, SPAR_RAKE_DEG = 5.5, 35.0
FALL_M = 9.0


def _rope(mb: kc.MeshBuilder, a, b, sag: float, r: float, mat: int, *, n: int = 9, sides: int = 5) -> None:
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = np.linspace(0.0, 1.0, n)
    pts = a[None] + (b - a)[None] * t[:, None]
    pts[:, 1] -= 4.0 * sag * t * (1.0 - t)
    kc.tube(mb, pts, r, sides, mat, weather=cw.IRON_W, variation=0.4)


def hoist(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_t, i_r, i_i = mb.material(cw.M_TIMBER), mb.material(cw.M_ROPE), mb.material(cw.M_IRON)
    heel = np.array([0.15, KERB_TOP_LOCAL + 0.12, KERB_Z_LOCAL])
    rake = math.radians(SPAR_RAKE_DEG)
    axis = np.array([0.0, math.cos(rake), -math.sin(rake)])
    tip = heel + axis * SPAR_M
    sides = 5 if lod else 9
    kc.tube(mb, np.array([heel, heel + axis * SPAR_M * 0.5, tip]), np.array([0.09, 0.085, 0.075]), sides, i_t,
            noise=None if lod else noise, disp_m=0.01, variation=0.3, cap_start=True, cap_end=True,
            weather=kc.Weathering(moss=0.0, salt=0.4, wet=0.3, erosion=0.6))
    # Head-rope from the tip back over the walk to the strap-plates on the head's back.
    strap = np.array([0.0, 1.35, -HEAD_BACK - 0.03])
    rr = 0.016 if not lod else 0.03
    _rope(mb, tip, strap + np.array([-0.18, 0.0, 0.0]), 0.25, rr, i_r, n=6 if lod else 12, sides=3 if lod else 5)
    _rope(mb, tip, strap + np.array([0.18, 0.0, 0.0]), 0.25, rr, i_r, n=6 if lod else 12, sides=3 if lod else 5)
    # Side guys to ring-bolts in the kerb.
    for sx in (-1.0, 1.0):
        ring = np.array([sx * 2.6, KERB_TOP_LOCAL + 0.04, KERB_Z_LOCAL + 0.1])
        _rope(mb, tip - axis * 0.3, ring, 0.08, rr, i_r, n=4 if lod else 8, sides=3 if lod else 5)
        if not lod:
            kc.tube(mb, np.array([ring - [0, 0.02, 0], ring + [0, 0.05, 0]]), 0.035, 6, i_i, cap_end=True)
    # The fall: two parts of rope from the block to the sling-board.
    board_y = tip[1] - FALL_M
    for dx in (-0.06, 0.06):
        top = tip + np.array([dx, -0.25, -0.05])
        bot = np.array([top[0], board_y + 0.85, top[2]])
        kc.tube(mb, np.array([top, (top + bot) * 0.5, bot]), rr * 0.9, 3 if lod else 5, i_r, weather=cw.IRON_W)
    if lod:
        kc.rounded_block(mb, (tip[0], board_y, tip[2]), (0.32, 0.03, 0.15), i_t, seg=1, radius=0.01)
        return mb
    # Iron: the shoe at the heel, strap-plates with bolt heads on the head's back, the block's strap.
    kc.rounded_block(mb, heel - axis * 0.05 + np.array([0, -0.05, 0]), (0.16, 0.1, 0.16), i_i, radius=0.015, seg=1,
                     rot=kc.rot_x(-rake))
    for sx in (-0.18, 0.18):
        c = strap + np.array([sx, 0.0, 0.0])
        kc.rounded_block(mb, c, (0.05, 0.32, 0.012), i_i, radius=0.006, seg=1)
        for by in (-0.22, 0.22):
            kc.rounded_block(mb, c + np.array([0.0, by, -0.016]), (0.022, 0.022, 0.012), i_i, radius=0.008, seg=1)
        kc.tube(mb, np.array([c + [0, 0.0, -0.01], c + [0, 0.0, -0.09]]), 0.022, 6, i_i, cap_end=True)
    # The double block at the tip: two cheeks, an iron strap round them, the hook.
    blk = tip + np.array([0.0, -0.18, -0.02])
    kc.rounded_block(mb, blk, (0.07, 0.17, 0.12), i_t, radius=0.03, seg=2, variation=0.6)
    kc.rounded_block(mb, blk, (0.08, 0.2, 0.02), i_i, radius=0.01, seg=1)
    kc.tube(mb, np.array([tip + [0, 0.12, 0], tip - axis * 0.05]), 0.03, 6, i_i)
    # The sling-board: a plank hung from a four-leg bridle to a ring.
    ring_c = np.array([tip[0], board_y + 0.85, tip[2] - 0.05])
    kc.tube(mb, np.array([ring_c + [0, 0.03, 0], ring_c - [0, 0.03, 0]]), 0.04, 8, i_i)
    kc.plank(mb, (tip[0] - 0.32, board_y, tip[2]), (tip[0] + 0.32, board_y, tip[2]), 0.28, 0.04, i_t,
             variation=0.7, noise=noise)
    for cx in (-0.28, 0.28):
        for cz in (-0.11, 0.11):
            _rope(mb, ring_c, (tip[0] + cx, board_y + 0.02, tip[2] + cz), 0.0, 0.011, i_r, n=2, sides=4)
    # A coil of spare rope on the walk by the heel.
    coil_c = heel + np.array([0.7, -0.5, 0.9])
    t = np.linspace(0.0, 2.0 * np.pi * 3.0, 60)
    rad = 0.24 + 0.012 * t / (2 * np.pi)
    pts = np.stack([coil_c[0] + rad * np.cos(t), coil_c[1] + 0.03 + 0.018 * t / (2 * np.pi), coil_c[2] + rad * np.sin(t)], -1)
    kc.tube(mb, pts, 0.018, 5, i_r, weather=cw.IRON_W)
    return mb


def build_hoist(seed: int = 841) -> list[kc.MeshBuilder]:
    return [hoist("liss_hoist", seed, lod=False), hoist("liss_hoist", seed, lod=True)]


TARGETS = {"watcher_head": build_head, "watcher_relief": build_relief, "liss_hoist": build_hoist}
