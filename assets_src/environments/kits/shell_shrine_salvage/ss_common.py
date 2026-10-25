"""Shared metrics and helpers for the Shell Shrine interior kit (M2-ENV-03, haluna.md §3).

Builds on the Haluna kit's geometry core (assets_src/environments/kits/haluna/kit_common.py: MeshBuilder,
Weathering, rounded_block, tube, quad_strip, Noise3, rng_for) by import, never by copy, so both kits
share one vertex-channel convention (R moss, G salt, B wet, A erosion; UV2.x occlusion, UV2.y variation)
and one exporter. Every module of this kit is prefixed `ss_` so it never shadows a Haluna module on
sys.path (the Haluna kit has its own `shrine.py`).

Coordinates are Godot's: metres, +Y up, +X east, -Z north. The room floor is y = 0, as the trial's
greybox (game/data/trials/shell_shrine.json `layout`) assumes. Kit metrics below are written into the
kit manifest (`metrics`) by build.py, so the dressing script reads them instead of repeating them.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HALUNA = HERE.parent / "haluna"
if str(HALUNA) not in sys.path:
    sys.path.append(str(HALUNA))

import kit_common as kc  # noqa: E402  (the Haluna kit's core)

# ---------------------------------------------------------------------------------------------
# Materials (glTF slot names). kit_* resolve in the Haluna kit's materials/, ss_* in this kit's.
# ---------------------------------------------------------------------------------------------
M_STONE = "kit_coral_stone"
M_MORTAR = "kit_mortar_white"
M_GLASS = "kit_salt_glass"
M_DARK = "kit_interior_dark"
M_LASHING = "kit_lashing"
M_FLOWER = "kit_garland"
M_FLOWER_THROAT = "kit_garland_throat"
M_NACRE = "ss_nacre_inlay"
M_PAVING = "ss_floor_paving"
M_SILT = "ss_silt"
M_LEAF = "ss_leaf_boat"

# ---------------------------------------------------------------------------------------------
# Kit metrics (haluna.md §3.2; the trial greybox's sizes where the brief gives none)
# ---------------------------------------------------------------------------------------------
METRICS = {
    "wall_r_m": 9.0,  # curved wall modules: inner face radius (brief: R = 9 m)
    "wall_t_m": 0.6,  # wall thickness (greybox wall_t)
    "wall_h_m": 4.0,  # interior wall height to the cornice top (greybox wall_h)
    "spring_y_m": 4.2,  # the vault springs here (cornice top)
    "apse_cx_m": 5.0,  # apse centres at x = +-5: the apses reach x = +-14 (entrance and door)
    "apse_module_deg": 36.0,  # five curved modules per apse; the entrance / door module is the middle one
    "straight_module_m": 2.5,  # straight wall module along the long sides (z = +-wall_r)
    "foundation_y_m": -2.0,  # walls and plinth go down to here (the islet's tidepool is below the floor)
    "column_d_m": 0.5,
    "column_h_m": 4.0,
    "column_inset_m": 0.32,  # column centre inside the wall's inner face
    "floor_slab_m": 1.0,  # laid as one MultiMesh; 1 m keeps every edge tile inside the walls
    "raise_m": 0.004,  # borders and aprons sit this much above the slabs (no coplanar faces)
    "apron_m": 1.4,  # paved border along the wall foot (hides the slab grid's ragged edge)
    "entrance_w_m": 3.0,
    "entrance_h_m": 3.4,
    "door_w_m": 3.0,
    "door_h_m": 3.4,
    "door_t_m": 0.6,
    "niche_r_m": 2.2,  # the conch niche in a long wall (the side pool sits in it)
    "channel_w_m": 0.4,  # inner width (brief)
    "channel_depth_m": 0.25,  # inner depth (brief)
    "channel_wall_m": 0.12,
    "channel_rim_y_m": 0.3,  # runnels stand on the floor: rim 0.3, bed 0.05
    "channel_water_y_m": 0.21,
    "channel_module_m": 1.0,
    "channel_start_r_m": 1.0,  # a basin's channels start this far from its centre (pedestal foot)
    "bend_r_m": 0.6,  # centre-line radius of the 90 degree bend
    "basin_r_m": 1.1,  # bowl rim radius (2.2 m across, brief)
    "basin_h_m": 0.9,  # bowl rim height above the floor (greybox basin_h)
    "pedestal_top_m": 0.5,  # the bowl's pivot (its origin) sits here
    "spout_r_m": 1.36,  # spout lip, from the bowl's axis; the pouring spout is local -Z
    "spout_y_m": 0.34,  # spout lip height above the bowl's origin
    "bowl_water_y_m": 0.3,  # bowl water above the bowl's origin
    "spouts_deg": [0.0, 120.0, -120.0],  # spout 0 pours; the other two are dammed
    "pool_inradius_m": 3.5,  # octagonal inner pool, 7 m across the flats (brief)
    "pool_rim_t_m": 0.3,
    "pool_rim_h_m": 0.45,
    "pool_floor_y_m": -0.4,
    "pool_apron_m": 1.5,
    "pool_notch_y_m": 0.24,  # the inlet notch in the rim (faces local -X)
    "side_pool_r_m": 1.5,  # 3 m across (brief)
    "side_pool_floor_y_m": -0.16,  # silt surface (the charm lies on it)
    "side_pool_apron_m": 0.9,
    "charm_d_m": 0.06,  # net-float charm: 6 cm (brief)
    "door_sink_m": -3.6,
    "ceiling_t_m": 0.32,
    "oculi": [[-8.4, -1.0], [1.5, -1.0], [11.3, -1.0]],  # dome centres (x, z): two open domes, the roofed cone
    "roof_oculus": 1,  # index of the oculus under Haluna's roof_fan_shell (the S01 silhouette)
    "oculus_r_m": 0.85,
    "roof_scale": 1.2,
    "roof_ring_y_m": 3.95,  # roof_fan_shell's oculus ring height above its base (unscaled; Haluna shrine.py)
    "roof_ring_r_m": 0.72,  # its clear radius, unscaled (the ring's 1.0 less its tube)
    "sun_elev_deg": 75.0,  # ch03_shrine_int "(any)": the shafts' sun; the dressing's Sun node must match
    "sun_az_deg": 180.0,  # compass bearing towards the sun (from the south: the shafts lean north)
    "porch_len_m": 2.2,  # exterior: landing outside the entrance
    "step_rise_m": 0.18,
    "step_run_m": 0.38,
}

TENDED = kc.Weathering(moss=0.12, salt=0.32, wet=0.0, erosion=0.28, noise_scale_m=0.5)  # swept and loved
WATERWORN = kc.Weathering(moss=0.08, salt=0.45, wet=0.55, erosion=0.45, noise_scale_m=0.35)  # in the flow
SEAWORN = kc.Weathering(moss=0.2, salt=0.7, wet=0.4, erosion=0.75, noise_scale_m=0.5)  # sea stones


def col4(moss, salt, wet, erosion) -> np.ndarray:
    """Stacks the four weathering channels (broadcast) into (..., 4), clipped to [0, 1]."""
    m, s, w, e = np.broadcast_arrays(*(np.asarray(v, float) for v in (moss, salt, wet, erosion)))
    return np.clip(np.stack([m, s, w, e], axis=-1), 0.0, 1.0)


def lathe(mb: kc.MeshBuilder, prof, sides: int, mat: int, *, center=(0.0, 0.0, 0.0), weather=TENDED,
          noise: kc.Noise3 | None = None, wet=None, ao=None, salt_boost=None, a0: float = 0.0,
          a1: float = 2.0 * math.pi, r_mod=None, y_mod=None, variation: float = 0.5,
          flip: bool = False) -> np.ndarray:
    """Revolves a (r, y) profile (outer -> inner order sets the facing) around +Y. Per-profile-point
    arrays `wet`, `ao`, `salt_boost` paint the channels; `r_mod(theta, i)` scales the radius per angle
    (flutes, scallops) and `y_mod(theta, i, y)` replaces the height (notches). Returns the (P, sides+1, 3) grid. Angle 0 is +X, increasing towards +Z."""
    prof = np.asarray(prof, float)
    n_p = len(prof)
    ang = np.linspace(a0, a1, sides + 1)
    grid = np.zeros((n_p, sides + 1, 3))
    for i, (r, y) in enumerate(prof):
        rr = np.full(sides + 1, r)
        if r_mod is not None:
            rr = rr * r_mod(ang, i)
        grid[i, :, 0] = np.cos(ang) * rr
        grid[i, :, 1] = y if y_mod is None else y_mod(ang, i, y)
        grid[i, :, 2] = np.sin(ang) * rr
    grid += np.asarray(center, float)
    # Facing (flip=False): normal = tangent x profile direction, so a profile that descends faces out,
    # one that ascends faces in, one moving outward faces up. Its y part is dr / |d(profile)|.
    tan = np.gradient(prof, axis=0)
    ny = tan[:, 0] / np.maximum(np.linalg.norm(tan, axis=1), 1e-9)
    if flip:
        ny = -ny
    breakup = noise.fbm(grid / weather.noise_scale_m, 2) if noise is not None else np.full(grid.shape[:2], 0.5)
    up = np.broadcast_to(ny[:, None], grid.shape[:2])
    wet_a = np.zeros(n_p) if wet is None else np.asarray(wet, float)
    ao_a = np.ones(n_p) if ao is None else np.asarray(ao, float)
    sb = np.zeros(n_p) if salt_boost is None else np.asarray(salt_boost, float)
    col = col4(weather.moss * kc.smoothstep(0.35, 0.9, up) * (0.3 + 1.2 * breakup),
               weather.salt * (0.25 + 0.75 * breakup) + sb[:, None] * breakup,
               np.maximum(weather.wet * breakup, wet_a[:, None] * (0.75 + 0.5 * breakup)),
               weather.erosion * (0.35 + 0.9 * breakup))
    seg = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))])
    u = (ang - a0)[None, :] * max(float(prof[:, 0].mean()), 0.05)
    uv = np.stack([np.broadcast_to(u, grid.shape[:2]) + variation * 3.1, np.broadcast_to(seg[:, None], grid.shape[:2])],
                  axis=-1)
    uv2 = np.stack([np.broadcast_to(ao_a[:, None], grid.shape[:2]), np.full(grid.shape[:2], variation)], axis=-1)
    kc.quad_strip(mb, grid, mat, uv=uv, col=col, uv2=uv2, flip=flip)
    return grid


def flat_ring(mb: kc.MeshBuilder, center, r0: float, r1: float, y: float, sides: int, mat: int, *, col, uv2,
              a0: float = 0.0, a1: float = 2.0 * math.pi, down: bool = False) -> None:
    """A flat annulus (r0 < r1) at height y facing up (or down)."""
    lathe_grid = np.zeros((2, sides + 1, 3))
    ang = np.linspace(a0, a1, sides + 1)
    for i, r in enumerate((r1, r0)):
        lathe_grid[i, :, 0] = np.cos(ang) * r
        lathe_grid[i, :, 2] = np.sin(ang) * r
    lathe_grid[..., 1] = y
    lathe_grid += np.asarray(center, float) * np.array([1.0, 0.0, 1.0])
    uv = lathe_grid[..., [0, 2]]
    kc.quad_strip(mb, lathe_grid, mat, uv=uv, col=col, uv2=uv2, flip=not down, smooth=False)
    n = np.array([0.0, -1.0 if down else 1.0, 0.0])
    count = 2 * (sides + 1)
    mb.nrm[-count:] = np.tile(n, (count, 1)).tolist()


def arc_point(cx: float, cz: float, r: float, a: float, y: float = 0.0) -> np.ndarray:
    """Point at angle a (radians, 0 = +X, increasing towards +Z) on a circle around (cx, cz)."""
    return np.array([cx + r * math.cos(a), y, cz + r * math.sin(a)])


def yaw_rot_for_tangent(a: float) -> np.ndarray:
    """Rotation taking local +Z to the arc's outward normal at angle a (local +X runs along the arc,
    towards decreasing angle). kc.rot_y(phi) is Godot's yaw: it takes +X to (cos phi, 0, -sin phi)."""
    return kc.rot_y(math.pi * 0.5 - a)


def ashlar_courses(y0: float, y1: float, rng, *, mean_h: float = 0.42, spread: float = 0.08,
                   snap=()) -> list[tuple]:
    """Course boundaries (y0, y1) from y0 up to y1, heights mean_h +- spread (deterministic rng). A
    boundary that would land within 0.6 x mean_h above a `snap` height moves onto it (floor line, arch
    springing), so openings start on a joint."""
    out = []
    y = y0
    snaps = sorted(float(v) for v in snap)
    while y < y1 - 1e-6:
        h = float(mean_h + spread * (rng.random() * 2.0 - 1.0))
        for sv in snaps:
            if y + 1e-6 < sv <= y + h + mean_h * 0.6:
                h = sv - y
                break
        if y1 - (y + h) < mean_h * 0.5:
            h = y1 - y
        out.append((y, y + h))
        y += h
    return out


def split_run(length: float, rng, *, mean: float, spread: float, offset: float = 0.0) -> list[tuple]:
    """Splits [0, length] into blocks of mean +- spread; `offset` shifts the first joint (running bond)."""
    cuts = [0.0]
    s = offset if offset > 1e-6 else float(mean + spread * (rng.random() * 2.0 - 1.0))
    while s < length - mean * 0.45:
        cuts.append(s)
        s += float(mean + spread * (rng.random() * 2.0 - 1.0))
    cuts.append(length)
    return list(zip(cuts[:-1], cuts[1:]))


def arc_frame(cx: float, cz: float, r_mid: float, mid: float):
    """Frame along an arc for wall_blocks: s (arc length from the mid angle) -> (centre at y 0, rot)."""
    def frame(s: float):
        a = mid + s / r_mid
        return arc_point(cx, cz, r_mid, a), yaw_rot_for_tangent(a)
    return frame


def line_frame(z_mid: float):
    """Frame along a straight wall running along X (outward +Z), its centre line at z = z_mid."""
    def frame(s: float):
        return np.array([s, 0.0, z_mid]), np.eye(3)
    return frame


def wall_blocks(mb: kc.MeshBuilder, frame, length: float, thick: float, y0: float, y1: float, rng, noise, *,
                mat: int, seg: int, weather=TENDED, joint: float = 0.014, forbid=None, block_mean: float = 0.8,
                course_mean: float = 0.42, disp_m: float = 0.018, snap=(), low_seg_below: float | None = None,
                s_range=None) -> int:
    """Coursed coral ashlar in running bond along a frame (arc_frame / line_frame), s in
    [-length / 2, length / 2] (or `s_range`). `forbid(y_lo, y_hi) -> (s_lo, s_hi) | None` removes an
    interval from a course (openings). Blocks below `low_seg_below` use seg 1 (foundations seen from
    afar). Returns the number of blocks laid."""
    lo, hi = (-length * 0.5, length * 0.5) if s_range is None else s_range
    count = 0
    for k, (cy0, cy1) in enumerate(ashlar_courses(y0, y1, rng, mean_h=course_mean, snap=snap)):
        intervals = [(lo, hi)]
        if forbid is not None:
            f = forbid(cy0, cy1)
            if f is not None:
                intervals = [(lo, min(hi, f[0])), (max(lo, f[1]), hi)]
        for s_lo, s_hi in intervals:
            run = s_hi - s_lo
            if run < 0.1:
                continue
            off = block_mean * (0.5 if k % 2 else 0.0) + block_mean * 0.25 * float(rng.random())
            for b0, b1 in split_run(run, rng, mean=block_mean, spread=block_mean * 0.3, offset=off):
                half_len = 0.5 * (b1 - b0) - joint
                if half_len < 0.035:
                    continue
                c, rot = frame(s_lo + 0.5 * (b0 + b1))
                c = c + np.array([0.0, 0.5 * (cy0 + cy1), 0.0])
                sg = 1 if (low_seg_below is not None and cy1 <= low_seg_below) else seg
                kc.rounded_block(mb, c, (half_len, 0.5 * (cy1 - cy0) - joint, thick * 0.5), mat, rot=rot,
                                 radius=0.035, seg=sg, noise=noise if sg > 1 else None, disp_m=disp_m,
                                 disp_period_m=0.22, weather=weather, variation=float(rng.random()))
                count += 1
    return count


def mortar_arc_bed(mb: kc.MeshBuilder, cx: float, cz: float, r: float, a0: float, a1: float, y0: float, y1: float,
                   mat: int, *, outward: bool, sides: int = 12) -> None:
    """A continuous mortar surface on an arc (recessed behind the block faces, so joints read white)."""
    ang = np.linspace(a0, a1, sides + 1)
    grid = np.zeros((2, sides + 1, 3))
    for i, y in enumerate((y0, y1)):
        grid[i, :, 0] = cx + np.cos(ang) * r
        grid[i, :, 1] = y
        grid[i, :, 2] = cz + np.sin(ang) * r
    uv = np.stack([np.broadcast_to(ang * r, (2, sides + 1)), grid[..., 1]], axis=-1)
    kc.quad_strip(mb, grid, mat, uv=uv, col=col4(0.0, 0.25, 0.0, 0.3), uv2=(0.55, 0.5), flip=outward, smooth=True)


def arc_slab_lod(mb: kc.MeshBuilder, cx: float, cz: float, r_in: float, r_out: float, a0: float, a1: float,
                 y0: float, y1: float, mat: int, sides: int = 4, col=None) -> None:
    """LOD stand-in for a curved wall: inner face, outer face and top as three strips."""
    colv = col4(0.05, 0.3, 0.0, 0.3) if col is None else col
    ang = np.linspace(a0, a1, sides + 1)
    for r, outward in ((r_in, False), (r_out, True)):
        grid = np.zeros((2, sides + 1, 3))
        for i, y in enumerate((y0, y1)):
            grid[i, :, 0] = cx + np.cos(ang) * r
            grid[i, :, 1] = y
            grid[i, :, 2] = cz + np.sin(ang) * r
        uv = np.stack([np.broadcast_to(ang * r, (2, sides + 1)), grid[..., 1]], axis=-1)
        kc.quad_strip(mb, grid, mat, uv=uv, col=colv, uv2=(0.8, 0.5), flip=outward)
    top = np.zeros((2, sides + 1, 3))
    for i, r in enumerate((r_out, r_in)):
        top[i, :, 0] = cx + np.cos(ang) * r
        top[i, :, 1] = y1
        top[i, :, 2] = cz + np.sin(ang) * r
    kc.quad_strip(mb, top, mat, uv=top[..., [0, 2]], col=colv, uv2=(0.9, 0.5), flip=True)


def box_proxy(mb: kc.MeshBuilder, center, half, rot=None) -> None:
    """A plain 12-triangle box (collision proxies: `<piece>-col`)."""
    rot = np.eye(3) if rot is None else np.asarray(rot, float)
    h = np.asarray(half, float)
    corners = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], float) * h
    p = corners @ rot.T + np.asarray(center, float)
    base = mb.add_vertices(p, np.tile(kc.UP, (8, 1)), np.zeros((8, 2)), np.ones((8, 2)), np.zeros((8, 4)))
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    m = mb.material("collision")
    for a, b, c, d in faces:
        mb.add_tri(base + a, base + b, base + c, m)
        mb.add_tri(base + a, base + c, base + d, m)


def prism_proxy(mb: kc.MeshBuilder, outline_xz, y0: float, y1: float) -> None:
    """A convex XZ outline extruded y0..y1 (collision proxies)."""
    kc.polygon_prism(mb, np.asarray(outline_xz, float), y0, y1, mb.material("collision"),
                     col=(0.0, 0.0, 0.0, 0.0), uv2=(1.0, 0.0), top=True, bottom=True)


def ring_proxy(mb: kc.MeshBuilder, center, r_in: float, r_out: float, y0: float, y1: float, sides: int,
               phase: float = 0.0) -> None:
    """A ring wall as `sides` box segments (collision proxies for pool rims)."""
    cx, cz = float(center[0]), float(center[2])
    for k in range(sides):
        a = phase + 2.0 * math.pi * (k + 0.5) / sides
        r_mid = 0.5 * (r_in + r_out)
        half_len = r_out * math.tan(math.pi / sides)
        box_proxy(mb, (cx + math.cos(a) * r_mid, 0.5 * (y0 + y1), cz + math.sin(a) * r_mid),
                  (half_len, 0.5 * (y1 - y0), 0.5 * (r_out - r_in)), rot=yaw_rot_for_tangent(a))


def nacre_band(mb: kc.MeshBuilder, pts: np.ndarray, normal, width: float, mat: int, *, lift: float = 0.004,
               variation: float = 0.5) -> None:
    """A thin inlay strip along a polyline, lying on a surface with the given normal (per point or one)."""
    pts = np.asarray(pts, float)
    nrm = np.broadcast_to(np.asarray(normal, float), pts.shape)
    tang = np.gradient(pts, axis=0)
    tang = kc.normalize(tang)
    side = kc.normalize(np.cross(nrm, tang))
    rows = np.stack([pts + side * width * 0.5 + nrm * lift, pts - side * width * 0.5 + nrm * lift], axis=0)
    seg = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    uv = np.stack([np.broadcast_to(seg[None, :], (2, len(pts))), np.array([[0.0], [width]]) * np.ones((2, len(pts)))],
                  axis=-1)
    base = mb.add_vertices(rows.reshape(-1, 3), np.broadcast_to(nrm, (2,) + nrm.shape).reshape(-1, 3),
                           uv.reshape(-1, 2), np.tile([1.0, variation], (2 * len(pts), 1)),
                           np.tile(col4(0.0, 0.1, 0.6, 0.1), (2 * len(pts), 1)))
    n = len(pts)
    for i in range(n - 1):
        a, b, c, d = base + i, base + i + 1, base + n + i + 1, base + n + i
        # Face along +normal: check winding against the normal once.
        e1 = rows[0, i + 1] - rows[0, i]
        e2 = rows[1, i] - rows[0, i]
        if np.dot(np.cross(e1, e2), nrm[i]) > 0:
            mb.add_tri(a, b, d, mat)
            mb.add_tri(b, c, d, mat)
        else:
            mb.add_tri(a, d, b, mat)
            mb.add_tri(b, d, c, mat)
