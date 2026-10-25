"""The Seawall falls (M3-ENV-04B; corrow.md §1.4 and §7): the breach pieces and the low town's rubble.
Pure numpy; see cw_common.py.

Every piece here is a 12 m slot on the R = 300 m arc (or a 24 m low-town cell), placed exactly like the
piece it replaces, so a breach swaps segments one for one:

  seawall_breach_a/b    12 m where the wall went: broken through to its stump at +0.3 .. +0.6 m (below the
                        town's +1.0 m, so the sea comes into the lanes through it), the lowest courses of
                        both faces left as a ragged sill, blocks tumbled inland into the low town and out
                        onto the rip-rap, lumps of bonded masonry. `a` carries a run of the walk's paving
                        and kerb down in the gap; `b` a broken Watcher relief panel face-up in the rubble.
  seawall_breach_end_w  the segment west of a gap: a seawall_curve (the same generator and seed, so it
  seawall_breach_end_e  joins its intact neighbour exactly) torn at its east (_w) or west (_e) end. The
                        courses step back block by block (0.6 m steps), undercut by the surge at mid-height
                        so the walk's top course overhangs the gap, a few of its slabs hanging off the
                        break; the section shows a skin of laterite round a dark rubble core, raw where it
                        broke (cw_laterite_broken). The parapet keeps its last head's footing (0.3 m torn).
  lowtown_rubble        a 24 x 24 m cell for the flooded lanes (origin at its centre on the ground, place it
                        at +1.0 m): wall blocks, a carved fragment, timbers and roof tiles from the crushed
                        houses, silt banks; heaped along the lane's sides (|x| 1.7 .. 3.4 m) and across the
                        wall-foot end (+Z), with the lane down its centre line kept clear, so the stair foot
                        still reads.

The tear profile and the breach floor are functions of the wall frame shared by all four wall pieces, so
an end and a gap segment meet at their common joint: the floor is base(z) there, and the stump below
STUMP_Y runs through.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
import cw_wall
from cw_common import kc

TRI_BUDGET = {"seawall_breach": (14000, 1100), "seawall_breach_end": (16000, 1100), "lowtown_rubble": (9000, 700)}
BUDGET_KEY = {"seawall_breach_a": "seawall_breach", "seawall_breach_b": "seawall_breach",
              "seawall_breach_end_w": "seawall_breach_end", "seawall_breach_end_e": "seawall_breach_end"}

HALF_X = cw.SEGMENT_M * 0.5
STUMP_Y = 0.5  # the wall's body survives below this everywhere in a breach
CONE_H = 2.6  # the debris cone against a torn end, at the joint
CONE_R = 4.8  # and how far it runs out into the gap
TEAR_STEP_M = 0.6  # the tear steps back half a block (blocks are 1.2 m) at a time
TEAR_DEPTH_BLOCK_M = 0.9  # blocks across the section (z), for the tear's jitter
TOP_TEAR_M = 0.3  # the parapet and kerb torn back only this far: the last head keeps its footing
TOP_COURSE_Y = 11.5  # the walk's top course, which bridges the undercut
FLOOR_Z = (-8.0, 7.6)  # the breach floor's extent across the section (local z)
INLAND_Z = (-16.0, -6.0)  # where tumbled blocks land in the low town
SEAWARD_Z = (7.0, 12.5)  # where they land on the rip-rap
BREACH_W = kc.Weathering(moss=0.0, salt=0.15, wet=0.45, erosion=0.35, noise_scale_m=0.8)
OLD_W = kc.Weathering(moss=0.0, salt=0.55, wet=0.4, erosion=0.8, noise_scale_m=0.8)


def _n2(noise: kc.Noise3, a, b, scale: float, octaves: int = 3, off: float = 0.0):
    a = np.asarray(a, float)
    p = np.stack([a / scale + off, np.full_like(a, 0.53 + off), np.asarray(b, float) / scale - off], axis=-1)
    return noise.fbm(p, octaves)


# ---------------------------------------------------------------------------------------------
# The shared frame: the breach floor and the tear profile
# ---------------------------------------------------------------------------------------------
_FLOOR_NOISE = kc.Noise3(kc.rng_for("seawall_breach_floor", 901))


def floor_base(z):
    """The breach's floor across the section at a joint: the town's ground (+1.0) inland, down to the
    stump at about +0.4 under the wall, then down onto the rip-rap's mound seaward."""
    z = np.asarray(z, float)
    town = cw.TOWN_Y - 0.06
    sill = 0.42 + 0.06 * np.sin(z * 1.7)
    y = town + (sill - town) * kc.smoothstep(-7.5, -3.5, z)
    return y + (float(cw_wall.apron_mound_y(_FLOOR_NOISE, 0.0, 6.8)) - 0.25 - sill) * kc.smoothstep(4.5, 7.4, z)


def joint_dist(x, mode: float):
    """Distance (m) from x to the joint a breach's debris cone sits on: either joint of a gap segment
    (mode 0), or the gap-side end of an end piece (mode +1 east, -1 west)."""
    x = np.asarray(x, float)
    return HALF_X - (np.abs(x) if mode == 0 else mode * x)


def debris_cone(d, z):
    """The wall's own mass piled against each torn end: a cone of rubble up to CONE_H at the joint, falling
    away over CONE_R into the gap, where the sea scoured the channel down to the sill."""
    d = np.asarray(d, float)
    z = np.asarray(z, float)
    across = kc.smoothstep(-7.0, -3.0, z) * (1.0 - kc.smoothstep(4.0, 7.4, z))
    return CONE_H * (1.0 - kc.smoothstep(0.0, CONE_R, d)) ** 1.4 * across


def floor_y(x, z, noise: kc.Noise3 | None = None, mode: float = 0.0):
    """The floor in a piece's frame: base(z), the debris cone at the torn ends, and rubble lumps that fade
    to nothing at x = +-6 (the joints)."""
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    y = floor_base(z) + debris_cone(joint_dist(x, mode), z)
    if noise is None:
        return y
    fade = 1.0 - kc.smoothstep(HALF_X - 1.5, HALF_X, np.abs(x))
    lumps = (_n2(noise, x, z, 2.2, 3, 7.0) - 0.45) * 0.55 + (_n2(noise, x, z, 0.7, 2, 3.0) - 0.5) * 0.12
    under = kc.smoothstep(-6.0, -3.0, z) * (1.0 - kc.smoothstep(5.5, 7.4, z))  # lumps on the stump, not the lanes
    return y + lumps * fade * (0.35 + 0.65 * under)


def tear_core(y):
    """How far (m) the tear has eaten into an end piece from its gap-side end at height y, before the
    per-block jitter: the toe of the lowest courses reaches the gap; the surge undercut the middle; the
    walk's top course overhangs."""
    y = np.asarray(y, float)
    toe = 0.2 + 1.0 * kc.smoothstep(STUMP_Y, 3.0, y)
    under = 2.4 * kc.smoothstep(2.0, 7.0, y) * (1.0 - kc.smoothstep(9.0, 11.4, y))
    top = 0.6 * kc.smoothstep(9.0, 11.4, y) - 0.9 * kc.smoothstep(11.4, 11.6, y)
    return np.where(y < STUMP_Y, 0.0, toe + under + top)


class Tear:
    """The tear of one end piece: L(y, z) metres eaten from the gap-side end (x = side * 6), quantised to
    half-block steps by course and by block across the section."""

    def __init__(self, side: float, seed: int):
        self.side = float(side)
        rng = kc.rng_for(f"seawall_breach_tear_{int(side)}", seed)
        self.jit = rng.uniform(0.0, 1.0, (64, 32))

    def length(self, y, z):
        y = np.asarray(y, float)
        z = np.asarray(z, float)
        k = np.clip(np.floor((y + 2.0) / cw.COURSE_M).astype(int), 0, 63)
        zb = np.clip(np.floor((z + 8.0) / TEAR_DEPTH_BLOCK_M).astype(int), 0, 31)
        j = self.jit[k, zb]
        raw = tear_core(y) + (j - 0.3) * 1.3
        steps = np.round(raw / TEAR_STEP_M) * TEAR_STEP_M
        out = np.where(y < STUMP_Y, 0.0, np.maximum(steps, 0.0))
        # The top course (the walk's slabs) is the bridge over the undercut: no more than 1.2 m torn; under
        # the parapet course and the kerb only TOP_TEAR_M (the last head keeps its footing).
        out = np.where(y >= TOP_COURSE_Y, np.minimum(out, 1.2), out)
        edge = (z >= cw.PARAPET[0] - 0.1) | (z <= cw.KERB[1] + 0.1)
        return np.where((y >= TOP_COURSE_Y) & edge, TOP_TEAR_M, out)

    def x(self, y, z):
        """x of the tear in the piece's straight frame."""
        return self.side * (HALF_X - self.length(y, z))


def _clamp_to_tear(mb: kc.MeshBuilder, tear: Tear, start_v: int, start_t: int) -> None:
    """Pulls every vertex beyond the tear back onto it (the faces and the walk of a straight segment)."""
    p = np.asarray(mb.pos[start_v:], float)
    if len(p) == 0:
        return
    lim = tear.x(np.minimum(p[:, 1], cw.WALK_Y - 0.01), p[:, 2])
    beyond = (p[:, 0] - lim) * tear.side > 0.0
    p[beyond, 0] = lim[beyond]
    mb.pos[start_v:] = p.tolist()
    kc.recompute_normals(mb, start_v, start_t)


# ---------------------------------------------------------------------------------------------
# Torn sections
# ---------------------------------------------------------------------------------------------
def _section_rows(y0: float, y1: float, lod: bool) -> np.ndarray:
    if lod:
        return np.unique(np.round(np.concatenate([[y0, y1], np.arange(math.ceil(y0), y1, 2.0)]), 5))
    eps = 0.012
    ys = [y0, y1]
    j = math.ceil((y0 + 2.0) / cw.COURSE_M)
    while -2.0 + j * cw.COURSE_M < y1:
        yj = -2.0 + j * cw.COURSE_M
        ys += [yj - eps, yj + eps]
        j += 1
    return np.unique(np.round(np.clip(ys, y0, y1), 5))


def _section_cols(z0: float, z1: float, lod: bool) -> np.ndarray:
    if lod:
        return np.linspace(z0, z1, 4)
    eps = 0.012
    zs = [z0, z1, cw.KERB[1] + 0.1 - eps, cw.KERB[1] + 0.1 + eps, cw.PARAPET[0] - 0.1 - eps, cw.PARAPET[0] - 0.1 + eps]
    j = math.ceil((z0 + 8.0) / TEAR_DEPTH_BLOCK_M)
    while -8.0 + j * TEAR_DEPTH_BLOCK_M < z1:
        zj = -8.0 + j * TEAR_DEPTH_BLOCK_M
        zs += [zj - eps, zj + eps]
        j += 1
    return np.unique(np.round(np.clip(zs, z0, z1), 5))


def torn_section(mb: kc.MeshBuilder, tear: Tear, noise: kc.Noise3, *, lod: bool) -> None:
    """The wall's section where it broke: stepped laterite blocks round a dark rubble core, facing the gap."""
    i_broken, i_core = mb.material(cw.M_BROKEN), mb.material(cw.M_RUBBLE)
    top = cw.WALK_Y - 0.004
    ys = _section_rows(STUMP_Y - 0.3, top, lod)
    zs = _section_cols(float(cw_wall.inner_z(0.0)) - 0.2, float(cw_wall.sea_z(SEA_LOW)) + 0.2, lod)
    Y, Z = np.meshgrid(ys, zs, indexing="ij")
    zi = cw_wall.inner_z(np.minimum(Y, cw_wall.INNER_TOP))
    zo = cw_wall.sea_z(np.minimum(Y, cw_wall.PARAPET_TOP))
    Zc = np.clip(Z, zi, zo)
    L = tear.length(Y, Zc)
    X = tear.side * (HALF_X - L)
    if not lod:
        X = X - tear.side * (_n2(noise, Y, Zc, 0.45, 2, 11.0) - 0.5) * 0.06
    P = np.stack([X, Y, Zc], axis=-1)
    skin = np.minimum(Zc - zi, zo - Zc)
    breakup = _n2(noise, Y, Zc, 0.9, 2, 5.0)
    wet = np.clip((1.0 - kc.smoothstep(STUMP_Y, 3.0, Y)) * 0.8 + 0.2 * breakup, 0, 1)
    col = np.stack([np.zeros_like(Y), np.clip(0.05 + 0.15 * breakup, 0, 1), wet,
                    np.clip(0.25 + 0.3 * breakup, 0, 1)], axis=-1)
    # Shade: the undercut's roof and the core are in deep shadow.
    ao = np.clip(0.95 - 0.35 * kc.smoothstep(0.6, 2.4, L) * (1.0 - kc.smoothstep(10.5, 11.6, Y))
                 - 0.2 * kc.smoothstep(1.0, 2.5, skin), 0.3, 1.0)
    course = np.floor((Y + 2.0) / cw.COURSE_M)
    var = (np.sin(course * 7.31 + np.floor(Zc / 0.9) * 3.1) * 43758.5453) % 1.0
    start_t = mb.triangle_count
    cw.grid_surface(mb, P, i_broken, outward=np.array([tear.side, 0.0, 0.0]), uv=np.stack([Zc, Y], -1), col=col,
                    uv2=np.stack([ao, var], -1), smooth=False)
    if not lod:
        c = np.asarray(mb.pos)[np.asarray(mb.tris[start_t:], dtype=np.int64)].mean(axis=1)
        zi_c = cw_wall.inner_z(np.minimum(c[:, 1], cw_wall.INNER_TOP))
        zo_c = cw_wall.sea_z(np.minimum(c[:, 1], cw_wall.PARAPET_TOP))
        core = np.minimum(c[:, 2] - zi_c, zo_c - c[:, 2]) > 1.05
        for k in np.nonzero(core)[0]:
            mb.tri_mat[start_t + k] = i_core
    # The kerb's and the parapet's own ends, torn back TOP_TEAR_M.
    xe = tear.side * (HALF_X - TOP_TEAR_M)
    kz0, kz1, kh = cw.KERB
    pz0, pz1, ph = cw.PARAPET
    for z0, z1, h in ((float(cw_wall.inner_z(cw_wall.INNER_TOP)), kz1, kh), (pz0, float(cw_wall.sea_z(cw.WALK_Y)), ph)):
        E = np.array([[[xe, cw.WALK_Y - 0.02, z0], [xe, cw.WALK_Y - 0.02, z1]],
                      [[xe, cw.WALK_Y + h, z0], [xe, cw.WALK_Y + h, z1]]])
        cw.grid_surface(mb, E, i_broken, outward=np.array([tear.side, 0.0, 0.0]), uv=E[..., [2, 1]],
                        col=np.tile([0.0, 0.1, 0.2, 0.35], (2, 2, 1)), uv2=np.tile([0.85, 0.4], (2, 2, 1)), smooth=False)
    # The walk's own thickness under its torn edge (the slab course seen end-on, between the top course
    # and the walk).
    zw = np.linspace(kz1, pz0, 3 if lod else 13)
    xw = tear.x(np.full_like(zw, 11.75), zw)
    W = np.stack([np.stack([xw, np.full_like(zw, top - 0.003), zw], -1),
                  np.stack([xw, np.full_like(zw, cw.WALK_Y + 0.02), zw], -1)])
    cw.grid_surface(mb, W, i_broken, outward=np.array([tear.side, 0.0, 0.0]), uv=W[..., [2, 1]],
                    col=np.tile([0.0, 0.1, 0.25, 0.4], W.shape[:2] + (1,)), uv2=np.tile([0.9, 0.5], W.shape[:2] + (1,)),
                    smooth=False)


SEA_LOW = STUMP_Y - 0.3


def _floor(mb: kc.MeshBuilder, x0: float, x1: float, noise: kc.Noise3, *, lod: bool, mode: float,
           z0: float = FLOOR_Z[0], z1: float = FLOOR_Z[1]) -> None:
    """The breach floor between x0 and x1: rubble over the stump, raw laterite where blocks broke on it,
    wet and puddled low."""
    i_rub, i_broken = mb.material(cw.M_RUBBLE), mb.material(cw.M_BROKEN)
    nx = max(3, int(round(abs(x1 - x0) / (3.0 if lod else 0.5))) + 1)
    nz = 5 if lod else 33
    xs = np.linspace(x0, x1, nx)
    zs = np.linspace(z0, z1, nz)
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    Y = floor_y(X, Z, None if lod else noise, mode)
    smooth_y = floor_y(X, Z, None, mode)
    P = np.stack([X, Y, Z], axis=-1)
    breakup = _n2(noise, X, Z, 1.3, 2, 19.0)
    hollow = np.clip((smooth_y + 0.05 - Y) / 0.15, 0, 1)
    col = np.stack([np.zeros_like(X), np.clip(0.15 + 0.25 * breakup, 0, 1),
                    np.clip(0.4 + 0.5 * hollow + 0.3 * (1.0 - kc.smoothstep(0.2, 1.0, Y)), 0, 1),
                    np.clip(0.5 + 0.4 * breakup, 0, 1)], axis=-1)
    ao = np.clip(0.75 + 0.25 * kc.smoothstep(-0.1, 0.25, Y - smooth_y), 0.3, 1.0)
    start_t = mb.triangle_count
    cw.grid_surface(mb, P, i_rub, outward=kc.UP, uv=np.stack([X, Z], -1), col=col,
                    uv2=np.stack([ao, np.full_like(X, 0.5)], -1))
    if not lod:
        c = np.asarray(mb.pos)[np.asarray(mb.tris[start_t:], dtype=np.int64)].mean(axis=1)
        f = _n2(noise, c[:, 0], c[:, 2], 1.6, 3, 31.0)
        for k in np.nonzero(f > 0.62)[0]:
            mb.tri_mat[start_t + k] = i_broken


def _block(mb: kc.MeshBuilder, rng: np.random.Generator, noise: kc.Noise3, center, size, mat: int, *, lod: bool,
           tilt: float = 0.5, weather: kc.Weathering = OLD_W, wet_bias: float = 0.0) -> None:
    half = np.asarray(size, float) * 0.5
    rot = kc.rot_y(rng.uniform(0.0, math.pi)) @ kc.rot_x(rng.uniform(-tilt, tilt)) @ kc.rot_z(rng.uniform(-tilt, tilt))
    kc.rounded_block(mb, center, half, mat, rot=rot, radius=0.05 if lod else min(0.08, float(half.min()) * 0.3),
                     seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.03, disp_period_m=0.5, weather=weather,
                     variation=float(rng.random()), wet_bias=wet_bias)


def _ground_at(x: float, z: float, apron_noise: kc.Noise3, mode: float) -> float:
    """Where a tumbled block lands: the town's ground inland, the floor in the gap, the rip-rap seaward."""
    if z < FLOOR_Z[0]:
        return cw.TOWN_Y
    if z > 7.0:
        return float(cw_wall.apron_mound_y(apron_noise, np.array(x), np.array(z))) + 0.1
    return float(floor_y(np.array(x), np.array(z), None, mode))


def tumbled(mb: kc.MeshBuilder, rng: np.random.Generator, noise: kc.Noise3, count: int, x_range, *, lod: bool,
            mode: float, spread=(0.35, 0.35, 0.3)) -> None:
    """Wall blocks thrown out of the breach: a share on its floor, inland into the low town and out onto
    the rip-rap (the weathered skin up, or the raw break)."""
    i_lat, i_broken, i_carved = mb.material(cw.M_LATERITE), mb.material(cw.M_BROKEN), mb.material(cw.M_CARVED)
    apron_noise = kc.Noise3(kc.rng_for("wall_apron", 811))
    for k in range(count):
        r = rng.random()
        if r < spread[0]:
            z = rng.uniform(-4.0, 6.0)
        elif r < spread[0] + spread[1]:
            z = INLAND_Z[1] - (INLAND_Z[1] - INLAND_Z[0]) * rng.random() ** 1.7
        else:
            z = SEAWARD_Z[0] + (SEAWARD_Z[1] - SEAWARD_Z[0]) * rng.random() ** 1.4
        x = rng.uniform(*x_range)
        if mode == 0 and rng.random() < 0.5:  # half of them on the cones at the torn ends
            x = (1.0 if x > 0 else -1.0) * rng.uniform(HALF_X - 2.8, HALF_X - 0.4)
        big = rng.random() < 0.3
        size = (np.array([1.2, 0.5, 0.8]) if big else np.array([0.6, 0.5, 0.7])) * rng.uniform(0.75, 1.15, 3)
        y = _ground_at(x, z, apron_noise, mode)
        mat = i_broken if rng.random() < 0.35 else (i_carved if rng.random() < 0.12 else i_lat)
        _block(mb, rng, noise, (x, y + size[1] * 0.3, z), size, mat, lod=lod, tilt=0.6,
               wet_bias=0.3 if (z > 7.0 or y < 1.1) else 0.0)
        if lod and k >= count // 3:
            break


def masonry_lump(mb: kc.MeshBuilder, rng: np.random.Generator, noise: kc.Noise3, center, size, yaw: float,
                 tilt: tuple[float, float], *, lod: bool) -> None:
    """A lump of wall still bonded: several courses of blocks thrown down together, the course joints cut
    into it, one face the old weathered skin and the others raw."""
    i_lat, i_broken = mb.material(cw.M_LATERITE), mb.material(cw.M_BROKEN)
    half = np.asarray(size, float) * 0.5
    rot = kc.rot_y(yaw) @ kc.rot_x(tilt[0]) @ kc.rot_z(tilt[1])
    start_v, start_t = mb.vertex_count, mb.triangle_count
    kc.rounded_block(mb, center, half, i_broken, rot=rot, radius=0.06, seg=1 if lod else 5, noise=None if lod else noise,
                     disp_m=0.05, disp_period_m=0.7, weather=BREACH_W, variation=float(rng.random()))
    if lod:
        return
    # The course joints (grooves every 0.5 m up the lump's own frame) and the weathered skin on its +Z face.
    p = np.asarray(mb.pos[start_v:], float)
    local = (p - np.asarray(center, float)) @ rot
    f = (local[:, 1] + half[1]) / cw.COURSE_M
    d = np.minimum(f - np.floor(f), 1.0 - (f - np.floor(f))) * cw.COURSE_M
    groove = -0.025 * (1.0 - kc.smoothstep(0.0, 0.05, d))
    n = np.asarray(mb.nrm[start_v:], float)
    mb.pos[start_v:] = (p + n * groove[:, None]).tolist()
    kc.recompute_normals(mb, start_v, start_t)
    tri = np.asarray(mb.tris[start_t:], dtype=np.int64)
    c_local = ((np.asarray(mb.pos)[tri].mean(axis=1)) - np.asarray(center, float)) @ rot
    for k in np.nonzero(c_local[:, 2] > half[2] * 0.85)[0]:
        mb.tri_mat[start_t + k] = i_lat


def sea_stub(mb: kc.MeshBuilder, rng: np.random.Generator, noise: kc.Noise3, *, lod: bool) -> None:
    """The lowest courses of the sea face left standing across the gap: a ragged sill, its top stepping
    by whole blocks (0..2 courses above STUMP_Y), down to the stump at the joints."""
    i_lat = mb.material(cw.M_LATERITE)
    xs = np.linspace(-HALF_X, HALF_X, 5 if lod else 41)
    tops = rng.integers(0, 3, 16) * cw.COURSE_M + STUMP_Y
    ys = np.array([cw_wall.SEA_FOOT_BURIED_Y, STUMP_Y, STUMP_Y + 1.0]) if lod else \
        cw.course_rows(cw_wall.SEA_FOOT_BURIED_Y, STUMP_Y + 1.0, mid=False)
    X, Y = np.meshgrid(xs, ys)
    blk = np.clip(np.floor((X + HALF_X) / cw.BLOCK_M).astype(int), 0, 15)
    top = np.where(np.abs(X) > HALF_X - 0.6, STUMP_Y, tops[blk])
    Yc = np.minimum(Y, top)
    ny, nz = math.sin(math.radians(cw.SEA_BATTER_DEG)), math.cos(math.radians(cw.SEA_BATTER_DEG))
    disp = np.zeros_like(X) if lod else cw.course_profile(Yc, rng.uniform(-1, 1, 64))
    # Collapsed rows (y clipped to the top) keep their own z: they make the stub's ragged top, back toward
    # the stump.
    P = np.stack([X, Yc + disp * ny, cw_wall.sea_z(Y) + disp * nz], axis=-1)
    breakup = _n2(noise, X, Y, 1.4, 2, 2.0)
    col = np.stack([np.zeros_like(X), np.clip(kc.smoothstep(0.4, 1.4, Yc) * (0.3 + 0.5 * breakup), 0, 1),
                    np.clip(1.0 - kc.smoothstep(0.8, 2.0, Yc) + 0.2 * breakup, 0, 1),
                    np.clip(0.5 + 0.4 * breakup, 0, 1)], axis=-1)
    uv = np.stack([X + ((np.floor(Yc + 2.0) * 0.6180339) % 1.0) * 6.0, Yc], axis=-1)
    cw.grid_surface(mb, P, i_lat, outward=np.array([0.0, ny, nz]), uv=uv, col=col,
                    uv2=np.stack([np.full_like(X, 0.8), np.full_like(X, 0.5)], -1))


# ---------------------------------------------------------------------------------------------
# The pieces
# ---------------------------------------------------------------------------------------------
def breach(name: str, seed: int, *, lod: bool, variant: str) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    _floor(mb, -HALF_X, HALF_X, noise, lod=lod, mode=0.0)
    sea_stub(mb, rng, noise, lod=lod)
    tumbled(mb, rng, noise, 58, (-HALF_X + 0.4, HALF_X - 0.4), lod=lod, mode=0.0)
    lr = kc.rng_for(name + "_lumps", seed)
    if variant == "a":
        masonry_lump(mb, lr, noise, (-2.2, 0.9, -1.0), (3.0, 1.6, 1.4), 0.35, (0.5, 0.25), lod=lod)
        masonry_lump(mb, lr, noise, (3.1, 0.75, 3.8), (2.2, 1.2, 1.1), -0.6, (-0.35, 0.4), lod=lod)
        if not lod:
            _paving_run(mb, lr, noise)
    else:
        masonry_lump(mb, lr, noise, (2.6, 0.95, -0.6), (3.4, 1.4, 1.5), -0.25, (0.25, -0.55), lod=lod)
        masonry_lump(mb, lr, noise, (-3.6, 1.15, -9.5), (2.0, 1.0, 1.2), 1.1, (0.2, 0.3), lod=lod)
        _relief_fragment(mb, lr, noise, lod=lod)
    cw.bend(mb)
    return mb


def _paving_run(mb: kc.MeshBuilder, rng: np.random.Generator, noise: kc.Noise3) -> None:
    """A run of the walk come down in the gap: slabs still in their row, broken and tilted on the rubble,
    and a length of the kerb beside them."""
    i_pave, i_lat = mb.material(cw.M_PAVING), mb.material(cw.M_LATERITE)
    x = -4.6
    for k in range(6):
        z = -1.4 + 0.15 * k + rng.uniform(-0.2, 0.2)
        y = float(floor_y(np.array(x), np.array(z), None)) + 0.35 + 0.25 * math.sin(k * 1.3)
        rot = kc.rot_y(0.25 + rng.uniform(-0.1, 0.1)) @ kc.rot_z(rng.uniform(-0.5, 0.5)) @ kc.rot_x(rng.uniform(-0.3, 0.3))
        kc.rounded_block(mb, (x, y, z), (0.58, 0.12, 0.48), i_pave, rot=rot, radius=0.03, seg=2, noise=noise,
                         disp_m=0.015, disp_period_m=0.4, weather=OLD_W, variation=float(rng.random()), wet_bias=0.2)
        x += 1.25
    kc.rounded_block(mb, (0.8, 0.95, -3.3), (2.4, 0.26, 0.32), i_lat, rot=kc.rot_y(0.12) @ kc.rot_z(0.18),
                     radius=0.04, seg=3, noise=noise, disp_m=0.03, disp_period_m=0.5, weather=OLD_W, variation=0.4)


def _relief_fragment(mb: kc.MeshBuilder, rng: np.random.Generator, noise: kc.Noise3, *, lod: bool) -> None:
    """The upper half of a sea-face Watcher (lids, brow and crown) broken off its panel and lying face-up,
    tilted, in the rubble: still humming nothing now, its mouth lost under the blocks."""
    i_carved, i_broken = mb.material(cw.M_CARVED), mb.material(cw.M_BROKEN)
    h = 3.0
    n = 4 if lod else 27
    us = np.linspace(-1.5, 1.5, n)
    vs = np.linspace(1.35, 3.1, max(3, n * 2 // 3))
    U, V = np.meshgrid(us, vs, indexing="ij")
    d = cw.watcher_face(U, V - 0.3, h, carving=cw.CARVING_B) if not lod else np.zeros_like(U)
    # The broken lower edge: a jagged line across the panel.
    jag = 1.35 + 0.25 * np.sin(U * 3.1) + 0.12 * np.sin(U * 9.0 + 1.0)
    Vc = np.maximum(V, jag)
    local = np.stack([U, Vc - 2.2, d + 0.0], axis=-1)
    rot = kc.rot_y(2.6) @ kc.rot_x(-1.25) @ kc.rot_z(0.2)
    c = np.array([-2.4, float(floor_y(np.array(-2.4), np.array(2.4))) + 0.45, 2.4])
    P = local @ rot.T + c
    wear = cw.watcher_wear(d, h)
    col = np.stack([np.zeros_like(U), np.full_like(U, 0.35), np.full_like(U, 0.3), np.clip(wear, 0, 1)], axis=-1)
    cw.grid_surface(mb, P, i_carved, outward=rot @ np.array([0.0, 0.0, 1.0]), uv=np.stack([U, Vc], -1), col=col,
                    uv2=np.stack([np.clip(1.0 - np.clip(-d / 0.06, 0, 1) * 0.5, 0.3, 1.0), np.full_like(U, 0.3)], -1))
    # The slab's thickness: a raw block under it.
    kc.rounded_block(mb, c - rot @ np.array([0.0, -0.1, 0.32]), (1.5, 0.85, 0.3), i_broken, rot=rot, radius=0.05,
                     seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.03, disp_period_m=0.5, weather=BREACH_W)


def breach_end(name: str, seed: int, *, lod: bool, side: float) -> kc.MeshBuilder:
    """A seawall_curve torn at its gap-side end (side +1: east, -1: west)."""
    tear = Tear(side, seed)
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    # The intact part is the seawall's own generator and seed, so it joins the next segment exactly.
    mb = cw_wall.seawall("seawall_curve", 801, lod=lod, bent=False)
    mb.name = name + (cw.LOD if lod else "")
    n_faces = mb.triangle_count
    _clamp_to_tear(mb, tear, 0, 0)
    del n_faces
    torn_section(mb, tear, noise, lod=lod)
    # The floor from the tear's toe to the joint, and blocks fallen at the torn face's foot.
    _floor(mb, side * 1.0, side * HALF_X, noise, lod=lod, mode=side)
    br = kc.rng_for(name + "_blocks", seed)
    x_range = (HALF_X - 3.0, HALF_X - 0.4) if side > 0 else (-HALF_X + 0.4, -HALF_X + 3.0)
    tumbled(mb, br, noise, 14, x_range, lod=lod, mode=side, spread=(0.6, 0.25, 0.15))
    if not lod:
        _hanging_slabs(mb, tear, br, noise)
    cw.bend(mb)
    return mb


def _hanging_slabs(mb: kc.MeshBuilder, tear: Tear, rng: np.random.Generator, noise: kc.Noise3) -> None:
    """Slabs of the walk hanging off the break: still hooked on the slab behind at their top edge, swung
    down 25 .. 70 deg over the gap."""
    i_pave = mb.material(cw.M_PAVING)
    for zc in (-1.5, 0.5, 1.5, 2.5):
        if rng.random() < 0.25:
            continue
        x_edge = float(tear.x(np.array(11.75), np.array(zc)))
        phi = rng.uniform(0.45, 1.2)
        hinge = np.array([x_edge, cw.WALK_Y, zc])
        half = np.array([0.55, 0.11, 0.47])
        # The slab hangs from its inner top edge: its centre is half a slab out along the swung direction.
        out = np.array([tear.side * math.cos(phi), -math.sin(phi), 0.0])
        down = np.array([tear.side * math.sin(phi), math.cos(phi), 0.0])
        center = hinge + out * half[0] - down * half[1]
        rot = kc.rot_z(-tear.side * phi) @ kc.rot_y(rng.uniform(-0.08, 0.08))
        kc.rounded_block(mb, center, half, i_pave, rot=rot, radius=0.03, seg=2, noise=noise, disp_m=0.012,
                         disp_period_m=0.4, weather=OLD_W, variation=float(rng.random()), wet_bias=0.15)


def build_breach(name: str, seed: int, variant: str):
    return lambda: [breach(name, seed, lod=False, variant=variant), breach(name, seed, lod=True, variant=variant)]


def build_end(name: str, seed: int, side: float):
    return lambda: [breach_end(name, seed, lod=False, side=side), breach_end(name, seed, lod=True, side=side)]


# ---------------------------------------------------------------------------------------------
# The low town's rubble
# ---------------------------------------------------------------------------------------------
RUBBLE_HALF = 12.0
LANE_HALF_M = 1.7
HEAP_OUT_M = 3.4


def _heap(mb: kc.MeshBuilder, noise: kc.Noise3, center, radii, height: float, mat: int, *, lod: bool, seed_off: float,
          weather_col, mix_mat: int | None = None) -> None:
    """A low, lumpy bank of silt and broken stuff: its outline ragged (the radius wanders with the angle),
    its top knobbled with stones, its rim below the ground so it rises out of it; with `mix_mat`, patches
    of the bank are the rubble showing through the silt."""
    n = 5 if lod else 13
    t = np.linspace(-1.0, 1.0, n)
    U, V = np.meshgrid(t, t, indexing="ij")
    ang = np.arctan2(V, U)
    rim = 1.0 + 0.28 * np.sin(3.0 * ang + seed_off) + 0.15 * np.sin(5.0 * ang + 2.0 * seed_off)
    r2 = (U ** 2 + V ** 2) / rim ** 2
    X = center[0] + U * radii[0]
    Z = center[1] + V * radii[1]
    body = np.clip(1.0 - r2, 0.0, 1.0)
    lumps = 0.0
    if not lod:
        lumps = ((_n2(noise, X, Z, 0.45, 2, seed_off) - 0.5) * 0.9 + (_n2(noise, X, Z, 0.18, 1, seed_off + 3.0) - 0.5) * 0.5) \
            * height
    Y = height * body ** 0.9 + lumps * body ** 0.5 - 0.08
    P = np.stack([X, Y, Z], axis=-1)
    start_t = mb.triangle_count
    cw.grid_surface(mb, P, mat, outward=kc.UP, uv=np.stack([X, Z], -1), col=np.broadcast_to(weather_col, P.shape[:2] + (4,)),
                    uv2=np.stack([np.clip(0.6 + 0.4 * Y / max(height, 1e-6), 0.3, 1.0), np.full_like(X, 0.5)], -1))
    if mix_mat is not None and not lod:
        c = np.asarray(mb.pos)[np.asarray(mb.tris[start_t:], dtype=np.int64)].mean(axis=1)
        f = _n2(noise, c[:, 0], c[:, 2], 0.6, 2, seed_off + 9.0)
        for k in np.nonzero(f > 0.55)[0]:
            mb.tri_mat[start_t + k] = mix_mat


def rubble(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_rub = mb.material(cw.M_RUBBLE)
    i_earth, i_lat, i_broken, i_t, i_tile, i_carved = (mb.material(cw.M_EARTH), mb.material(cw.M_LATERITE),
                                                       mb.material(cw.M_BROKEN), mb.material(cw.M_TIMBER),
                                                       mb.material(cw.M_TILE), mb.material(cw.M_CARVED))
    silt = np.array([0.0, 0.25, 0.15, 0.4])
    tiles = np.array([0.0, 0.2, 0.5, 0.5])
    # Silt banks along both sides of the lane and a broad one across the wall-foot end.
    heaps = []
    for sx in (-1.0, 1.0):
        z = -RUBBLE_HALF + 2.5
        while z < RUBBLE_HALF - 3.0:
            heaps.append(((sx * rng.uniform(2.4, 3.0), z), (rng.uniform(0.8, 1.2), rng.uniform(1.6, 2.6)),
                          rng.uniform(0.12, 0.26), i_earth, silt))
            z += rng.uniform(3.0, 4.5)
    heaps.append(((-6.5, RUBBLE_HALF - 3.2), (4.0, 2.0), 0.32, i_earth, silt))
    heaps.append(((6.8, RUBBLE_HALF - 3.6), (3.6, 2.2), 0.36, i_earth, silt))
    for k in range(5):  # tile spills off the crushed roofs
        sx = -1.0 if k % 2 else 1.0
        heaps.append(((sx * rng.uniform(2.6, 3.1), rng.uniform(-9.0, 7.0)), (0.7, 1.0), 0.28, i_tile, tiles))
    for k, (c, r, h, mat, colv) in enumerate(heaps):
        _heap(mb, noise, c, r, h, mat, lod=lod, seed_off=float(k) * 1.7, weather_col=colv,
              mix_mat=i_rub if mat == i_earth else None)
        if lod and k > 6:
            break
    # Wall blocks: thickest toward the wall end (+Z), along the lane's sides elsewhere; never in the lane.
    placed = 0
    tries = 0
    target = 16 if lod else 64
    while placed < target and tries < 600:
        tries += 1
        z = RUBBLE_HALF - 2.0 * RUBBLE_HALF * rng.random() ** 0.55
        wall_end = z > RUBBLE_HALF - 6.0
        x = rng.uniform(-RUBBLE_HALF + 1.0, RUBBLE_HALF - 1.0) if wall_end else \
            (1.0 if rng.random() < 0.5 else -1.0) * rng.uniform(LANE_HALF_M + 0.3, HEAP_OUT_M)
        if abs(x) < LANE_HALF_M + 0.4 and z < RUBBLE_HALF - 2.5:
            continue  # the lane stays open up to the stair foot
        size = np.array([1.2, 0.5, 0.7]) * rng.uniform(0.55, 1.1, 3)
        mat = i_broken if rng.random() < 0.4 else (i_carved if rng.random() < 0.08 else i_lat)
        _block(mb, rng, noise, (x, size[1] * 0.25, z), size, mat, lod=lod, tilt=0.5, wet_bias=0.12)
        placed += 1
    # Timbers out of the houses: roof beams and door leaves, broken, lying along the heaps.
    nt = 3 if lod else 11
    for k in range(nt):
        sx = -1.0 if k % 2 else 1.0
        x = sx * rng.uniform(2.0, 3.6)
        z = rng.uniform(-10.0, 9.0)
        yaw = rng.uniform(-0.6, 0.6) + (0.0 if rng.random() < 0.6 else math.pi * 0.5)
        ln = rng.uniform(1.4, 3.4)
        a = np.array([x - math.sin(yaw) * ln * 0.5, rng.uniform(0.05, 0.3), z - math.cos(yaw) * ln * 0.5])
        b = np.array([x + math.sin(yaw) * ln * 0.5, rng.uniform(0.05, 0.4), z + math.cos(yaw) * ln * 0.5])
        kc.plank(mb, a, b, rng.uniform(0.12, 0.3), rng.uniform(0.06, 0.14), i_t, variation=float(rng.random()),
                 noise=None if lod else noise, weather=kc.Weathering(moss=0.0, salt=0.3, wet=0.6, erosion=0.5))
    return mb


def build_rubble(seed: int = 911) -> list[kc.MeshBuilder]:
    return [rubble("lowtown_rubble", seed, lod=False), rubble("lowtown_rubble", seed, lod=True)]


TARGETS = {
    "seawall_breach_a": build_breach("seawall_breach_a", 921, "a"),
    "seawall_breach_b": build_breach("seawall_breach_b", 922, "b"),
    "seawall_breach_end_w": build_end("seawall_breach_end_w", 931, 1.0),
    "seawall_breach_end_e": build_end("seawall_breach_end_e", 932, -1.0),
    "lowtown_rubble": build_rubble,
}
