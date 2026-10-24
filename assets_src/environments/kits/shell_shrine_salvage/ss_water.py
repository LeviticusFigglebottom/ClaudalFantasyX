"""Shell Shrine water and puzzle pieces (haluna.md §3.2 Channels, Shell-basins, Inner pool, Side pool).

  channel_straight_1m   carved runnel, 0.4 m wide and 0.25 m deep inside, standing on the floor (rim 0.3,
                        bed 0.05), nacre inlay bands on both rim tops and along the waterline. Runs along
                        local -Z from z = 0 to z = -1 (the dresser yaws -Z onto the flow).
  channel_bend          90 deg bend (centre-line radius 0.6) entering at z = 0 heading -Z, leaving
                        heading +X at (0.6, 0, -0.6)
  channel_t             1.4 m run with a branch to +X at z = -0.7, the branch ending at x = 0.9
  channel_spillway      0.5 m of runnel ending in a lip over a round floor sump with a ribbed stone grate
                        (centre at z = -0.95): where a basin's water is lost
  channel_sluice        1.2 m of runnel with a carved gate: posts, lintel, and a raised shell-plate gate
  channel_end           the stone that closes a runnel's end (at z = 0, the runnel on its -Z side)
  basin_pedestal        the fixed foot of a shell-basin: fluted stem, cup, plinth with a nacre ring
                        (origin on the floor; collision for the whole basin)
  basin_bowl            the turning scallop bowl, 2.2 m across, three spouts at 0 / +-120 deg from local -Z:
                        spout 0 (-Z) is open and nacre-lined, the other two are dammed. Origin = pivot, on
                        the axis at the bowl's foot; the level turns this node about Y.
  inner_pool_octagon    octagonal pool (7 m across the flats), rim, nacre-lined coping, sunk floor, paved
                        apron; the inlet notch faces local -X
  side_pool_round       the drainable side pool (3 m across): ring of coping stones, silt floor with
                        ripples and shell grit, apron; inlet notch to local -X
  spring_head           the source: a round well-curb under a fan-shell stele, its outlet to local -Z
"""

from __future__ import annotations

import math

import numpy as np

import ss_common as sc
from ss_common import kc

M = sc.METRICS

TRI_BUDGET = {
    "channel_straight_1m": (900, 40),
    "channel_bend": (2200, 120),
    "channel_t": (2400, 80),
    "channel_spillway": (3200, 120),
    "channel_sluice": (2600, 100),
    "channel_end": (300, 12),
    "basin_pedestal": (5000, 300),
    "basin_bowl": (8000, 400),
    "inner_pool_octagon": (9000, 500),
    "side_pool_round": (7000, 400),
    "spring_head": (7000, 400),
}


# ---------------------------------------------------------------------------------------------
# Runnel profile and extrusion
# ---------------------------------------------------------------------------------------------
def _profiles() -> dict:
    """Cross-section parts (x across, y up) of the runnel: left wall, bed, right wall."""
    hw = M["channel_w_m"] * 0.5
    wt = M["channel_wall_m"]
    rim = M["channel_rim_y_m"]
    bed = rim - M["channel_depth_m"]
    o = hw + wt
    left = [(-o, 0.0), (-o, rim - 0.03), (-o + 0.015, rim - 0.005), (-o + 0.04, rim), (-hw - 0.02, rim),
            (-hw - 0.005, rim - 0.01), (-hw, rim - 0.03), (-hw, bed + 0.04), (-hw + 0.015, bed + 0.01),
            (-hw + 0.035, bed)]
    right = [(-x, y) for x, y in left[::-1]]
    return {"left": left, "bed": [left[-1], right[0]], "right": right}


def _paint_profile(prof, *, water_y: float) -> np.ndarray:
    """Weathering per profile point: wet below the waterline inside, salt where the water line dries,
    erosion on the rim's arrises, a little salt at the outer foot."""
    hw = M["channel_w_m"] * 0.5
    out = []
    for x, y in prof:
        inner = abs(x) <= hw + 1e-6
        rim_top = y >= M["channel_rim_y_m"] - 0.012
        wet = 0.95 if (inner and y <= water_y + 0.03) else (0.45 if inner else 0.0)
        salt = 0.65 if (inner and abs(y - water_y - 0.035) < 0.03) else (0.45 if y < 0.03 else 0.2)
        ero = 0.65 if rim_top else 0.3
        out.append((0.0, salt, wet, ero))
    return np.asarray(out)


def extrude(mb: kc.MeshBuilder, prof, path: np.ndarray, mat: int, noise, *, cap_start: bool = False,
            cap_end: bool = False, variation: float = 0.5, paint=None) -> None:
    """Extrudes a 2D profile (x across to the right of travel, y up) along a horizontal polyline. With
    the profile running left wall -> bed -> right wall, the surfaces face out of the stone."""
    prof = np.asarray(prof, float)
    path = np.asarray(path, float)
    f = np.gradient(path, axis=0)
    f[:, 1] = 0.0
    f = kc.normalize(f)
    right = kc.normalize(np.cross(f, kc.UP))
    grid = path[:, None, :] + right[:, None, :] * prof[None, :, 0:1] + kc.UP[None, None, :] * prof[None, :, 1:2]
    grid = np.transpose(grid, (1, 0, 2))  # rows = profile points, cols = path points
    del noise  # no displacement: module ends must meet their neighbours exactly
    col = np.broadcast_to(paint[:, None, :] if paint is not None else sc.col4(0, 0.3, 0, 0.3), grid.shape[:2] + (4,))
    seg = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    pseg = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))])
    uv = np.stack([np.broadcast_to(seg[None, :], grid.shape[:2]), np.broadcast_to(pseg[:, None], grid.shape[:2])],
                  axis=-1)
    ao = np.clip(0.55 + 1.6 * prof[:, 1], 0.55, 1.0)
    uv2 = np.stack([np.broadcast_to(ao[:, None], grid.shape[:2]), np.full(grid.shape[:2], variation)], axis=-1)
    # rows = profile, cols = path: (b - a) runs along the path, (d - a) along the profile; the profile
    # order above makes path x profile point out of the stone, so flip.
    kc.quad_strip(mb, grid, mat, uv=uv, col=col, uv2=uv2, flip=True)
    for flag, k, sgn in ((cap_start, 0, -1.0), (cap_end, len(path) - 1, 1.0)):
        if not flag:
            continue
        ring = grid[:, k]
        closed = np.vstack([ring, [ring[-1] * [1, 0, 1] + [0, ring[-1][1] * 0 + path[k][1], 0]]])
        closed[-1] = path[k] + right[k] * prof[-1, 0]
        closed[-1][1] = path[k][1]
        c = closed.mean(axis=0)
        n = f[k] * sgn
        base = mb.add_vertices(np.vstack([closed, c[None]]), np.tile(n, (len(closed) + 1, 1)),
                               np.zeros((len(closed) + 1, 2)), np.tile([0.9, variation], (len(closed) + 1, 1)),
                               np.tile(sc.col4(0, 0.3, 0, 0.4), (len(closed) + 1, 1)))
        cidx = base + len(closed)
        for i in range(len(closed)):
            a, b = base + i, base + (i + 1) % len(closed)
            e = np.cross(closed[(i + 1) % len(closed)] - closed[i], c - closed[i])
            if np.dot(e, n) >= 0:
                mb.add_tri(a, b, cidx, mat)
            else:
                mb.add_tri(b, a, cidx, mat)


def runnel(mb: kc.MeshBuilder, path: np.ndarray, noise, *, parts=("left", "bed", "right"), caps=(),
           nacre: bool = True, variation: float = 0.5) -> None:
    """A runnel along `path` (y = 0 on the floor). `caps` names wall parts to cap at ("start"|"end", part)."""
    pr = _profiles()
    stone = mb.material(sc.M_STONE)
    for part in parts:
        prof = pr[part]
        paint = _paint_profile(prof, water_y=M["channel_water_y_m"])
        # The bed is lined with nacre (haluna.md §3.2): running water reads as turquoise over it, and a
        # dry channel as a pale band, so the lit route stands out in the S03 overview.
        mat = mb.material(sc.M_NACRE) if (part == "bed" and nacre) else stone
        extrude(mb, prof, path, mat, noise, cap_start=("start", part) in caps, cap_end=("end", part) in caps,
                variation=variation, paint=paint)
    if not nacre:
        return
    hw = M["channel_w_m"] * 0.5
    f = kc.normalize(np.gradient(np.asarray(path, float), axis=0) * np.array([1.0, 0.0, 1.0]))
    right = kc.normalize(np.cross(f, kc.UP))
    nac = mb.material(sc.M_NACRE)
    for part, sgn in (("left", -1.0), ("right", 1.0)):
        if part not in parts:
            continue
        # Rim-top band, and a waterline band on the inner wall (it shimmers when the water runs).
        top = path + right * (sgn * (hw + 0.05)) + kc.UP * M["channel_rim_y_m"]
        sc.nacre_band(mb, top, kc.UP, 0.03, nac, lift=0.002, variation=variation)
        wl = path + right * (sgn * (hw - 0.002)) + kc.UP * (M["channel_water_y_m"] + 0.04)
        sc.nacre_band(mb, wl, -right * sgn, 0.022, nac, lift=0.002, variation=variation)


def _runnel_lod(mb: kc.MeshBuilder, path: np.ndarray) -> None:
    hw = M["channel_w_m"] * 0.5
    wt = M["channel_wall_m"]
    rim = M["channel_rim_y_m"]
    stone = mb.material(sc.M_STONE)
    path = np.asarray(path, float)
    for a, b in zip(path[:-1], path[1:]):
        d = b - a
        ln = float(np.linalg.norm(d))
        f = d / ln
        right = np.cross(f, kc.UP)
        rot = np.column_stack([right, kc.UP, -f])
        for sgn in (-1.0, 1.0):
            kc.rounded_block(mb, 0.5 * (a + b) + right * sgn * (hw + wt * 0.5) + kc.UP * rim * 0.5,
                             (wt * 0.5, rim * 0.5, ln * 0.5), stone, rot=rot, radius=0.01, seg=1)
        kc.rounded_block(mb, 0.5 * (a + b) + kc.UP * 0.025, (hw, 0.025, ln * 0.5), stone, rot=rot, radius=0.005,
                         seg=1, wet_bias=0.9)


def _line(z0: float, z1: float, n: int) -> np.ndarray:
    return np.stack([np.zeros(n), np.zeros(n), np.linspace(z0, z1, n)], axis=-1)


def build_channel_straight(seed: int = 401) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("channel_straight_1m", seed)
    noise = kc.Noise3(rng)
    ln = M["channel_module_m"]
    mb = kc.MeshBuilder("channel_straight_1m")
    runnel(mb, _line(0.0, -ln, 5), noise)
    lod = kc.MeshBuilder("channel_straight_1m-lod1")
    _runnel_lod(lod, _line(0.0, -ln, 2))
    return [mb, lod]


def _bend_path(n: int) -> np.ndarray:
    r = M["bend_r_m"]
    a = np.linspace(math.pi, math.pi * 0.5, n)  # around centre (r, 0): from (0, 0) to (r, -r)
    return np.stack([r + r * np.cos(a), np.zeros(n), -r * np.sin(a)], axis=-1)


def build_channel_bend(seed: int = 402) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("channel_bend", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("channel_bend")
    runnel(mb, _bend_path(13), noise)
    lod = kc.MeshBuilder("channel_bend-lod1")
    _runnel_lod(lod, _bend_path(4))
    return [mb, lod]


T_LEN = 1.4
T_BRANCH_Z = -0.7
T_BRANCH_END = 0.9


def build_channel_t(seed: int = 403) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("channel_t", seed)
    noise = kc.Noise3(rng)
    hw = M["channel_w_m"] * 0.5
    o = hw + M["channel_wall_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("channel_t" + ("-lod1" if lod else ""))
        if lod:
            _runnel_lod(mb, _line(0.0, -T_LEN, 2))
            _runnel_lod(mb, np.array([[o, 0.0, T_BRANCH_Z], [T_BRANCH_END, 0.0, T_BRANCH_Z]]))
            out.append(mb)
            continue
        runnel(mb, _line(0.0, -T_LEN, 8), noise, parts=("left", "bed"))
        z_a, z_b = T_BRANCH_Z + hw, T_BRANCH_Z - hw
        runnel(mb, _line(0.0, z_a, 4), noise, parts=("right",), caps=(("end", "right"),))
        runnel(mb, _line(z_b, -T_LEN, 4), noise, parts=("right",), caps=(("start", "right"),))
        branch = np.stack([np.linspace(hw, T_BRANCH_END, 5), np.zeros(5), np.full(5, T_BRANCH_Z)], axis=-1)
        runnel(mb, branch, noise, parts=("bed",), nacre=False)
        walls = np.stack([np.linspace(o, T_BRANCH_END, 4), np.zeros(4), np.full(4, T_BRANCH_Z)], axis=-1)
        runnel(mb, walls, noise, parts=("left", "right"))
        out.append(mb)
    return out


SUMP_Z = -0.95
SUMP_R = 0.4
SUMP_TOP = 0.13


def build_channel_spillway(seed: int = 404) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("channel_spillway", seed)
    noise = kc.Noise3(rng)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("channel_spillway" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        dark = mb.material(sc.M_DARK)
        if lod:
            _runnel_lod(mb, _line(0.0, -0.5, 2))
        else:
            runnel(mb, _line(0.0, -0.5, 4), noise, caps=(("end", "left"), ("end", "right")))
            # The lip: a rounded sill the water spills over, with a nacre edge.
            kc.rounded_block(mb, (0.0, 0.04, -0.52), (0.2, 0.04, 0.04), stone, radius=0.02, seg=2, weather=sc.WATERWORN,
                             variation=0.4, wet_bias=0.6)
            sc.nacre_band(mb, np.linspace([-0.18, 0.082, -0.545], [0.18, 0.082, -0.545], 4), kc.UP, 0.02,
                          mb.material(sc.M_NACRE))
        # Sump: a curb flush with the floor, a dark throat, and a grate of radial ribs (a shell's ribs).
        sides = 8 if lod else 32
        # The sump stands proud of the floor (the floor is one layer of flags): a curb, a dark throat.
        sc.lathe(mb, [(SUMP_R - 0.06, SUMP_TOP), (SUMP_R + 0.1, SUMP_TOP), (SUMP_R + 0.15, SUMP_TOP - 0.03),
                      (SUMP_R + 0.17, 0.0)], sides, stone, center=(0.0, 0.0, SUMP_Z), weather=sc.WATERWORN,
                 noise=None if lod else noise, wet=[0.8, 0.5, 0.3, 0.2])
        sc.lathe(mb, [(SUMP_R - 0.06, SUMP_TOP), (SUMP_R - 0.06, 0.012)], sides, stone, center=(0.0, 0.0, SUMP_Z),
                 weather=sc.WATERWORN, wet=[0.95, 1.0], ao=[0.6, 0.15], flip=True)
        sc.flat_ring(mb, (0.0, 0.0, SUMP_Z), 0.0, SUMP_R - 0.05, 0.014, sides, dark, col=sc.col4(0, 0, 1, 0),
                     uv2=(0.1, 0.5))
        if not lod:
            for k in range(9):
                a = math.pi * (k + 0.5) / 9 - math.pi
                p0 = np.array([0.0, 0.0, SUMP_Z]) + np.array([math.cos(a), 0.0, math.sin(a)]) * (SUMP_R - 0.05)
                p1 = np.array([0.0, 0.0, SUMP_Z]) - np.array([math.cos(a), 0.0, math.sin(a)]) * (SUMP_R - 0.05)
                pts = np.linspace(p0, p1, 5) + np.array([0.0, 0.0, 0.0])
                pts[:, 1] = SUMP_TOP - 0.035 + 0.025 * np.sin(np.linspace(0, math.pi, 5))
                kc.tube(mb, pts, 0.022, 5, stone, weather=sc.WATERWORN, variation=float(rng.random()))
            kc.tube(mb, np.array([[0.0, 0.01, SUMP_Z], [0.0, SUMP_TOP - 0.01, SUMP_Z]]), 0.05, 8, stone, cap_end=True,
                    weather=sc.WATERWORN)
        out.append(mb)
    return out


SLUICE_LEN = 1.2


def build_channel_sluice(seed: int = 405) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("channel_sluice", seed)
    noise = kc.Noise3(rng)
    hw = M["channel_w_m"] * 0.5
    o = hw + M["channel_wall_m"]
    zc = -SLUICE_LEN * 0.5
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("channel_sluice" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        if lod:
            _runnel_lod(mb, _line(0.0, -SLUICE_LEN, 2))
        else:
            runnel(mb, _line(0.0, -SLUICE_LEN, 6), noise)
        for sgn in (-1.0, 1.0):
            kc.rounded_block(mb, (sgn * (o - 0.06), 0.46, zc), (0.08, 0.46, 0.09), stone, radius=0.02,
                             seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.006, weather=sc.TENDED,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, 0.97, zc), (o + 0.08, 0.06, 0.11), stone, radius=0.02, seg=1 if lod else 3,
                         weather=sc.TENDED, variation=0.3)
        # The gate: a plate carved with a small scallop, raised (open) between the posts' grooves.
        kc.rounded_block(mb, (0.0, 0.62, zc), (hw + 0.01, 0.2, 0.025), stone, radius=0.012, seg=1 if lod else 2,
                         weather=sc.WATERWORN, variation=0.7)
        if not lod:
            import shrine  # noqa: PLC0415  (Haluna kit: fan_shell)

            tmp = kc.MeshBuilder("gatefan")
            shrine.fan_shell(tmp, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.17, rng, noise, span_deg=150.0, ribs=7,
                             lift=0.2, droop_deg=0.0, weather=sc.TENDED)
            rot = np.column_stack([kc.UP, [0.0, 0.0, 1.0], np.cross(kc.UP, [0.0, 0.0, 1.0])])
            mb.merge(tmp, rot, (0.0, 0.47, zc + 0.03))
            sc.nacre_band(mb, np.linspace([-hw, 0.43, zc + 0.027], [hw, 0.43, zc + 0.027], 4), (0.0, 0.0, 1.0), 0.02,
                          mb.material(sc.M_NACRE))
        out.append(mb)
    return out


def build_channel_end(seed: int = 406) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("channel_end", seed)
    o = M["channel_w_m"] * 0.5 + M["channel_wall_m"]
    rim = M["channel_rim_y_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("channel_end" + ("-lod1" if lod else ""))
        kc.rounded_block(mb, (0.0, rim * 0.5 + 0.01, 0.06), (o, rim * 0.5 + 0.01, 0.07), mb.material(sc.M_STONE),
                         radius=0.03, seg=1 if lod else 3, weather=sc.TENDED, variation=float(rng.random()))
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Shell-basins: fixed pedestal + turning bowl
# ---------------------------------------------------------------------------------------------
def build_pedestal(seed: int = 411) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("basin_pedestal", seed)
    noise = kc.Noise3(rng)
    top = M["pedestal_top_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("basin_pedestal" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        sides = 10 if lod else 36
        prof = [(0.0, top), (0.6, top), (0.64, top - 0.03), (0.58, top - 0.08), (0.46, top - 0.14),
                (0.36, top - 0.2), (0.3, top - 0.24), (0.29, 0.2), (0.33, 0.17), (0.42, 0.15), (0.5, 0.12),
                (0.86, 0.11), (0.9, 0.08), (0.92, 0.0)]
        if lod:
            prof = [prof[0], prof[1], prof[4], prof[7], prof[10], prof[11], prof[-1]]

        def flutes(ang, i, prof_len=len(prof)):
            # The stem (between the cup and the base) is fluted like a whelk's columella.
            if lod or not (5 <= i <= 8):
                return np.ones_like(ang)
            return 1.0 + 0.09 * (0.5 + 0.5 * np.cos(ang * 9.0))

        sc.lathe(mb, prof, sides, stone, noise=None if lod else noise, r_mod=flutes, variation=0.3,
                 salt_boost=None if lod else [0, 0, 0.1, 0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.5, 0.6, 0.3, 0.5, 0.6],
                 wet=None if lod else [0, 0, 0.3, 0.4, 0.4, 0.3, 0.2, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0])
        if not lod:
            ang = np.linspace(0, 2 * math.pi, 73)
            ring = np.stack([np.cos(ang) * 0.72, np.full_like(ang, 0.11), np.sin(ang) * 0.72], axis=-1)
            sc.nacre_band(mb, ring, kc.UP, 0.035, mb.material(sc.M_NACRE), lift=0.002)
        out.append(mb)
    col = kc.MeshBuilder("basin_pedestal-col")
    ang = np.linspace(0, 2 * math.pi, 13)[:-1]
    r = M["basin_r_m"]
    sc.prism_proxy(col, np.stack([np.cos(ang) * r, np.sin(ang) * r], axis=-1), 0.0, M["basin_h_m"])
    return out + [col]


def _spout_angles() -> list[float]:
    """Spout directions in lathe angles (0 = +X, towards +Z): local -Z is -90 deg, then +-120."""
    return [math.radians(-90.0 + d) for d in M["spouts_deg"]]


def build_bowl(seed: int = 412) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("basin_bowl", seed)
    noise = kc.Noise3(rng)
    h = M["basin_h_m"] - M["pedestal_top_m"]  # rim height above the pivot
    r = M["basin_r_m"]
    spouts = _spout_angles()
    notch_w = 0.17
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("basin_bowl" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        nac = mb.material(sc.M_NACRE)
        ribs = 18
        sides = 18 if lod else 144
        # One profile: the inner bowl from the centre out and up, over the rolled rim, down the outside.
        prof = [(0.0, h - 0.3), (0.3, h - 0.29), (0.6, h - 0.24), (0.82, h - 0.15), (0.96, h - 0.05), (1.02, h),
                (r, h + 0.01), (r + 0.02, h - 0.03), (r - 0.02, h - 0.1), (0.95, h - 0.22), (0.75, h - 0.33),
                (0.55, h - 0.38), (0.45, 0.0), (0.0, 0.0)]
        if lod:
            prof = [prof[0], prof[3], prof[5], prof[6], prof[8], prof[10], prof[12], prof[13]]
        n_p = len(prof)

        def scallop(ang, i):
            if lod:
                return 1.0 + 0.03 * np.cos(ang * ribs)
            k = 0.0 if i == 0 or i >= n_p - 2 else (0.045 if i >= 5 else 0.03 * i / 5.0)
            return 1.0 + k * np.cos(ang * ribs)

        def notch(ang, i, y):
            # The rim dips where a spout leaves the bowl.
            if i < 4 or i > 8:
                return np.full_like(ang, y)
            d = np.min([np.abs((ang - s + math.pi) % (2 * math.pi) - math.pi) for s in spouts], axis=0)
            dip = (1.0 - kc.smoothstep(notch_w * 0.6, notch_w * 1.3, d)) * 0.08
            return y - dip * (1.0 if i >= 5 else 0.5)

        wet = [0.95, 0.95, 0.9, 0.85, 0.7, 0.5, 0.2, 0.15, 0.1, 0.1, 0.1, 0.1, 0.0, 0.0]
        sc.lathe(mb, prof, sides, stone, noise=None if lod else noise, r_mod=scallop, y_mod=notch, variation=0.45,
                 wet=None if lod else wet, salt_boost=None if lod else [0, 0, 0, 0.2, 0.5, 0.4, 0.2, 0.2, 0.3, 0.4,
                                                                        0.4, 0.5, 0.4, 0.0],
                 a0=-math.pi * 0.5, a1=math.pi * 1.5)
        # Spouts: short carved troughs out over the rim; spout 0 pours (nacre-lined), the others are dammed.
        for k, a in enumerate(spouts):
            d = np.array([math.cos(a), 0.0, math.sin(a)])
            path = np.stack([d * rr for rr in np.linspace(0.9, M["spout_r_m"], 2 if lod else 5)])
            path[:, 1] = np.linspace(h - 0.06, M["spout_y_m"] - 0.04, len(path))
            if lod:
                kc.rounded_block(mb, path.mean(axis=0) + kc.UP * 0.02, (0.12, 0.05, 0.24), stone,
                                 rot=kc.rot_y(math.atan2(-d[2], d[0]) - math.pi * 0.5), radius=0.01, seg=1)
                continue
            _spout(mb, path, noise, nac if k == 0 else None)
            if k != 0:
                kc.rounded_block(mb, d * 0.98 + kc.UP * (h - 0.05), (0.1, 0.06, 0.05), stone,
                                 rot=kc.rot_y(math.atan2(-d[2], d[0]) + math.pi * 0.5), radius=0.02, seg=2,
                                 weather=sc.TENDED, variation=0.8)
        if not lod:
            # A nacre band round the inner lip (the bowl's lit ring when water stands in it).
            ang = np.linspace(-math.pi * 0.5, math.pi * 1.5, 145)
            keep = np.min([np.abs((ang - s + math.pi) % (2 * math.pi) - math.pi) for s in spouts], axis=0) > notch_w * 1.4
            runs = np.split(np.arange(len(ang)), np.where(np.diff(keep.astype(int)) != 0)[0] + 1)
            for run in runs:
                if not keep[run[0]] or len(run) < 3:
                    continue
                aa = ang[run]
                rr = 0.985 * (1.0 + 0.045 * np.cos(aa * ribs))
                ring = np.stack([np.cos(aa) * rr, np.full_like(aa, h - 0.03), np.sin(aa) * rr], axis=-1)
                nrm = -np.stack([np.cos(aa), np.zeros_like(aa), np.sin(aa)], axis=-1)
                sc.nacre_band(mb, ring, nrm * 0.6 + kc.UP * 0.8, 0.03, nac, lift=0.003)
        out.append(mb)
    return out


def _spout(mb, path: np.ndarray, noise, nacre_mat) -> None:
    """A small runnel (0.16 wide) sloping out over the rim, with a rolled lip at its end."""
    stone = mb.material(sc.M_STONE)
    hw, wt, depth = 0.08, 0.05, 0.08
    left = [(-hw - wt, -0.06), (-hw - wt, depth - 0.01), (-hw - wt + 0.015, depth), (-hw - 0.01, depth),
            (-hw, depth - 0.015), (-hw, 0.015), (-hw + 0.02, 0.0)]
    right = [(-x, y) for x, y in left[::-1]]
    prof = left + right[1:]
    paint = np.asarray([(0.0, 0.3, 0.95 if abs(x) <= hw else 0.4, 0.55 if y >= depth - 0.01 else 0.3)
                        for x, y in prof])
    extrude(mb, prof, path, stone, noise, cap_end=True, paint=paint)
    if nacre_mat is not None:
        sc.nacre_band(mb, path + kc.UP * 0.003, kc.UP, 0.1, nacre_mat, lift=0.002)


# ---------------------------------------------------------------------------------------------
# Pools
# ---------------------------------------------------------------------------------------------
def _coping_ring(mb, rng, noise, centers_rots_halves, weather=sc.TENDED) -> None:
    stone = mb.material(sc.M_STONE)
    for c, rot, half in centers_rots_halves:
        kc.rounded_block(mb, c, half, stone, rot=rot, radius=0.035, seg=3, noise=noise, disp_m=0.01,
                         weather=weather, variation=float(rng.random()))


def build_inner_pool(seed: int = 421) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("inner_pool_octagon", seed)
    noise = kc.Noise3(rng)
    ri = M["pool_inradius_m"]
    t, rh = M["pool_rim_t_m"], M["pool_rim_h_m"]
    fy = M["pool_floor_y_m"]
    ap = M["pool_apron_m"]
    tan8 = math.tan(math.pi / 8)
    notch_half = 0.32
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("inner_pool_octagon" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        pav = mb.material(sc.M_PAVING)
        nac = mb.material(sc.M_NACRE)
        # Side k's outward normal is at angle pi + k * 45 deg (side 0 faces local -X: the inlet).
        sides = []
        for k in range(8):
            a = math.pi + k * math.pi / 4
            n = np.array([math.cos(a), 0.0, math.sin(a)])
            tang = np.array([n[2], 0.0, -n[0]])  # tang x up = n (a proper rotation)
            rot = np.column_stack([tang, kc.UP, n])
            sides.append((n, tang, rot))
        # Sunk floor and inner walls (below the coping), painted soaked.
        verts = [np.array([math.cos(math.pi + math.pi / 8 + k * math.pi / 4), 0.0,
                           math.sin(math.pi + math.pi / 8 + k * math.pi / 4)]) * ri / math.cos(math.pi / 8)
                 for k in range(8)]
        outline = np.array([[v[0], v[2]] for v in verts])
        kc.polygon_prism(mb, outline, fy - 0.1, fy, pav, col=(0.0, 0.25, 1.0, 0.4), uv2=(0.55, 0.5), top=True)
        for k in range(8):
            a, b = verts[k], verts[(k + 1) % 8]
            g = np.array([[a + kc.UP * fy, b + kc.UP * fy], [a, b]])
            # Inner wall faces the centre: rows ascend, columns run a -> b (increasing angle): t x up = in.
            kc.quad_strip(mb, g, stone, uv=np.stack([g[..., 0] + g[..., 2], g[..., 1]], axis=-1),
                          col=sc.col4(0.0, 0.3, 1.0, 0.4), uv2=(0.5, 0.5), flip=False, smooth=False)
        # Coping: per side two long stones (one gap for the notch on side 0), on the rim line.
        blocks = []
        y_c = rh * 0.5
        for k, (n, tang, rot) in enumerate(sides):
            mid = n * (ri + t * 0.5)
            full = (ri + t) * tan8 + 0.0
            spans = [(-full, full)] if k != 0 else [(-full, -notch_half), (notch_half, full)]
            for s0, s1 in spans:
                pieces = [(s0, s1)] if lod or s1 - s0 < 1.2 else [(s0, 0.5 * (s0 + s1)), (0.5 * (s0 + s1), s1)]
                for p0, p1 in pieces:
                    c = mid + tang * (0.5 * (p0 + p1)) + kc.UP * y_c
                    blocks.append((c, rot, (0.5 * (p1 - p0) - 0.01, rh * 0.5, t * 0.5)))
        if lod:
            for c, rot, half in blocks:
                kc.rounded_block(mb, c, half, stone, rot=rot, radius=0.01, seg=1)
        else:
            _coping_ring(mb, rng, noise, blocks)
        # Inlet sill in the notch (lower), lipped with nacre.
        n0, tang0, rot0 = sides[0]
        kc.rounded_block(mb, n0 * (ri + t * 0.5) + kc.UP * (M["pool_notch_y_m"] * 0.5), (notch_half - 0.01,
                         M["pool_notch_y_m"] * 0.5, t * 0.5), stone, rot=rot0, radius=0.025, seg=1 if lod else 3,
                         weather=sc.WATERWORN, variation=0.4, wet_bias=0.7)
        if not lod:
            sc.nacre_band(mb, np.linspace(n0 * (ri + 0.04) - tang0 * notch_half, n0 * (ri + 0.04) + tang0 * notch_half,
                                          4) + kc.UP * (M["pool_notch_y_m"] + 0.002), kc.UP, 0.05, nac)
            # Nacre along the coping's inner arris, all round (the pool's ring of light).
            for k, (n, tang, rot) in enumerate(sides):
                full = ri * tan8
                spans = [(-full, full)] if k != 0 else [(-full, -notch_half), (notch_half, full)]
                for s0, s1 in spans:
                    pts = np.linspace(n * (ri + 0.05) + tang * s0, n * (ri + 0.05) + tang * s1, 4) + kc.UP * (rh + 0.003)
                    sc.nacre_band(mb, pts, kc.UP, 0.05, nac)
            # The paved apron: two rows of flags along each side, mitred corners left in mortar.
            for k, (n, tang, rot) in enumerate(sides):
                for j, (d0, d1) in enumerate(((ri + t, ri + t + ap * 0.5), (ri + t + ap * 0.5, ri + t + ap))):
                    half_len = d0 * tan8 - 0.02
                    for b0, b1 in sc.split_run(2 * half_len, rng, mean=0.7, spread=0.15, offset=0.25 * j + 0.1):
                        s = -half_len + 0.5 * (b0 + b1)
                        c = n * (0.5 * (d0 + d1)) + tang * s + kc.UP * (-0.045 + M["raise_m"])
                        kc.rounded_block(mb, c, (0.5 * (b1 - b0) - 0.008, 0.045, 0.5 * (d1 - d0) - 0.008), pav,
                                         rot=rot, radius=0.016, seg=2, weather=kc.Weathering(salt=0.3, erosion=0.4,
                                                                                            wet=0.15),
                                         variation=float(rng.random()))
            ro = (ri + t + ap) / math.cos(math.pi / 8)
            outer = np.array([[math.cos(math.pi + math.pi / 8 + k * math.pi / 4) * ro,
                               math.sin(math.pi + math.pi / 8 + k * math.pi / 4) * ro] for k in range(8)])
            kc.polygon_prism(mb, outer, -0.03, -0.012, mb.material(sc.M_MORTAR), col=(0.0, 0.4, 0.0, 0.3),
                             uv2=(0.5, 0.5), top=True)
        out.append(mb)
    col = kc.MeshBuilder("inner_pool_octagon-col")
    for k in range(8):
        a = math.pi + k * math.pi / 4
        n = np.array([math.cos(a), 0.0, math.sin(a)])
        sc.box_proxy(col, n * (ri + t * 0.5) + kc.UP * (rh * 0.5), ((ri + t) * tan8, rh * 0.5, t * 0.5),
                     rot=np.column_stack([[n[2], 0.0, -n[0]], kc.UP, n]))
    return out + [col]


def build_side_pool(seed: int = 422) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("side_pool_round", seed)
    noise = kc.Noise3(rng)
    r = M["side_pool_r_m"]
    t, rh = 0.26, 0.42
    fy = M["side_pool_floor_y_m"]
    ap = M["side_pool_apron_m"]
    stones = 11
    notch = math.pi  # the inlet faces local -X
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("side_pool_round" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        silt = mb.material(sc.M_SILT)
        pav = mb.material(sc.M_PAVING)
        sides = 12 if lod else 48
        # Inner wall from the silt up to the coping, soaked below the high-water line.
        sc.lathe(mb, [(r, fy - 0.05), (r, rh - 0.02)], sides, stone, wet=[1.0, 0.6], ao=[0.5, 0.95],
                 salt_boost=[0.0, 0.5], variation=0.6)
        # Silt floor: a disc with ripples and low mounds (the drained pool's soft bed).
        nr, na = (3, 12) if lod else (12, 64)
        grid = np.zeros((nr + 1, na + 1, 3))
        for i in range(nr + 1):
            rr = r * (1.0 - i / nr) + 0.02
            for j in range(na + 1):
                a = 2 * math.pi * j / na
                p = np.array([math.cos(a) * rr, 0.0, math.sin(a) * rr])
                bump = 0.0 if lod else (0.018 * math.sin(p[0] * 9.0 + 0.6 * math.sin(p[2] * 4.0))
                                        + 0.03 * (float(noise.fbm(p[None] / 0.6, 2)[0]) - 0.5))
                grid[i, j] = p + kc.UP * (fy + bump + 0.02 * (rr / r))
        col = sc.col4(0.0, 0.2, 0.85, 0.2)
        kc.quad_strip(mb, grid, silt, uv=grid[..., [0, 2]], col=col, uv2=(0.6, 0.5), flip=True)
        # Coping ring (stones), leaving the notch at -X for the inlet.
        blocks = []
        for k in range(stones):
            a0 = notch + 0.3 + (2 * math.pi - 0.6) * k / stones
            a1 = notch + 0.3 + (2 * math.pi - 0.6) * (k + 1) / stones
            a = 0.5 * (a0 + a1)
            c = sc.arc_point(0.0, 0.0, r + t * 0.5, a, rh * 0.5)
            half_len = (r + t * 0.5) * math.sin((a1 - a0) * 0.5) - 0.012
            blocks.append((c, sc.yaw_rot_for_tangent(a), (half_len, rh * 0.5, t * 0.5)))
        if lod:
            for c, rot, half in blocks:
                kc.rounded_block(mb, c, half, stone, rot=rot, radius=0.01, seg=1)
        else:
            _coping_ring(mb, rng, noise, blocks)
        kc.rounded_block(mb, (-(r + t * 0.5), 0.12, 0.0), (t * 0.5, 0.12, (r + t * 0.5) * math.sin(0.3) - 0.01), stone,
                         radius=0.02, seg=1 if lod else 2, weather=sc.WATERWORN, wet_bias=0.6, variation=0.5)
        if not lod:
            ang = np.linspace(notch + 0.32, notch + 2 * math.pi - 0.32, 60)
            ring = np.stack([np.cos(ang) * (r + 0.04), np.full_like(ang, rh + 0.003), np.sin(ang) * (r + 0.04)],
                            axis=-1)
            sc.nacre_band(mb, ring, kc.UP, 0.045, mb.material(sc.M_NACRE))
            # Shell grit and a few pebbles in the silt (they read once the water is gone).
            for k in range(14):
                a = float(rng.random()) * 2 * math.pi
                rr = float(rng.random()) ** 0.5 * (r - 0.25)
                p = np.array([math.cos(a) * rr, fy + 0.02, math.sin(a) * rr])
                sz = 0.015 + 0.02 * float(rng.random())
                kc.rounded_block(mb, p - kc.UP * sz * 0.2, (sz, sz * 0.5, sz * 0.8), stone,
                                 rot=kc.rot_y(float(rng.random()) * 6.28), radius=sz * 0.48, seg=2,
                                 weather=sc.SEAWORN, variation=float(rng.random()), wet_bias=0.6)
            for b0, b1 in sc.split_run(2 * math.pi * (r + t + ap * 0.5), rng, mean=0.6, spread=0.12):
                rm = r + t + ap * 0.5
                a = b0 / rm + 0.5 * (b1 - b0) / rm
                c = sc.arc_point(0.0, 0.0, rm, a, -0.045 + M["raise_m"])
                kc.rounded_block(mb, c, (0.5 * (b1 - b0) - 0.01, 0.045, ap * 0.5 - 0.01), pav,
                                 rot=sc.yaw_rot_for_tangent(a), radius=0.016, seg=2,
                                 weather=kc.Weathering(salt=0.3, erosion=0.4, wet=0.1), variation=float(rng.random()))
            sc.flat_ring(mb, (0.0, 0.0, 0.0), r + t - 0.02, r + t + ap, -0.012, 48, mb.material(sc.M_MORTAR),
                         col=sc.col4(0, 0.4, 0, 0.3), uv2=(0.5, 0.5))
        out.append(mb)
    col = kc.MeshBuilder("side_pool_round-col")
    sc.ring_proxy(col, (0.0, 0.0, 0.0), r, r + t, 0.0, rh, 12)
    return out + [col]


# ---------------------------------------------------------------------------------------------
# The spring head (the trial's `source`)
# ---------------------------------------------------------------------------------------------
def build_spring_head(seed: int = 431) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("spring_head", seed)
    noise = kc.Noise3(rng)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("spring_head" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        sides = 10 if lod else 40
        # Well-curb: outer wall, rolled top, inner wall down to the water (profile: inside-out order).
        prof = [(0.0, 0.08), (0.45, 0.08), (0.5, 0.12), (0.5, 0.46), (0.56, 0.52), (0.68, 0.5), (0.72, 0.44),
                (0.7, 0.06), (0.76, 0.0)]
        if lod:
            prof = [prof[0], prof[1], prof[3], prof[5], prof[7], prof[8]]

        def notch(ang, i, y):
            if i < 3 or i > 6:
                return np.full_like(ang, y)
            d = np.abs((ang + math.pi * 0.5 + math.pi) % (2 * math.pi) - math.pi)
            return y - (1.0 - kc.smoothstep(0.12, 0.26, d)) * 0.2

        sc.lathe(mb, prof, sides, stone, noise=None if lod else noise, y_mod=None if lod else notch,
                 wet=None if lod else [1, 1, 0.9, 0.7, 0.3, 0.2, 0.1, 0.1, 0.0], variation=0.5,
                 salt_boost=None if lod else [0, 0, 0.3, 0.5, 0.3, 0.2, 0.3, 0.4, 0.5])
        # The stele behind (local +Z): a tall fan-shell standing on a block, facing the outlet (-Z).
        kc.rounded_block(mb, (0.0, 0.3, 0.86), (0.4, 0.3, 0.12), stone, radius=0.03, seg=1 if lod else 3,
                         noise=None if lod else noise, disp_m=0.008, weather=sc.TENDED, variation=0.3)
        if not lod:
            import shrine  # noqa: PLC0415

            tmp = kc.MeshBuilder("stele")
            shrine.fan_shell(tmp, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.62, rng, noise, span_deg=150.0, ribs=9,
                             lift=0.12, droop_deg=0.0, weather=sc.TENDED)
            back = np.array([0.0, 0.0, -1.0])
            rot = np.column_stack([kc.UP, back, np.cross(kc.UP, back)])
            mb.merge(tmp, rot, (0.0, 0.62, 0.84))
            sc.nacre_band(mb, np.linspace([-0.34, 0.605, 0.735], [0.34, 0.605, 0.735], 5), (0.0, 0.0, -1.0), 0.03,
                          mb.material(sc.M_NACRE))
        else:
            kc.rounded_block(mb, (0.0, 1.35, 0.84), (0.6, 0.45, 0.08), stone, radius=0.02, seg=1)
        # Outlet lip toward -Z.
        kc.rounded_block(mb, (0.0, 0.3, -0.76), (0.16, 0.04, 0.1), stone, radius=0.02, seg=1 if lod else 2,
                         weather=sc.WATERWORN, wet_bias=0.7, variation=0.6)
        out.append(mb)
    col = kc.MeshBuilder("spring_head-col")
    ang = np.linspace(0, 2 * math.pi, 11)[:-1]
    sc.prism_proxy(col, np.stack([np.cos(ang) * 0.76, np.sin(ang) * 0.76], axis=-1), 0.0, 0.52)
    sc.box_proxy(col, (0.0, 0.9, 0.86), (0.6, 0.9, 0.14))
    return out + [col]


TARGETS = {
    "channel_straight_1m": build_channel_straight,
    "channel_bend": build_channel_bend,
    "channel_t": build_channel_t,
    "channel_spillway": build_channel_spillway,
    "channel_sluice": build_channel_sluice,
    "channel_end": build_channel_end,
    "basin_pedestal": build_pedestal,
    "basin_bowl": build_bowl,
    "inner_pool_octagon": build_inner_pool,
    "side_pool_round": build_side_pool,
    "spring_head": build_spring_head,
}
