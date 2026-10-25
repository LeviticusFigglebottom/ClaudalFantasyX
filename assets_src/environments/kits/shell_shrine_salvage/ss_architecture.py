"""Shell Shrine architecture (haluna.md §3.2 "Walls and columns", the interior ceiling). Pure numpy.

  floor_slab_1m          a 1 x 1 m tile of worn coral flags in running bond over a white mortar bed
  wall_curve_r9          curved wall module, R = 9 m inner face, 36 deg of arc (five per apse): coursed
                         coral ashlar on a foundation down to the tidepool, interior cornice with a nacre
                         string course, exterior coping, and a paved border along its foot
  wall_curve_entrance    the west apse's middle module: a 3 m shell arch (voussoirs fanned like scallop
                         ribs) with a fan-shell keystone on both faces and a threshold slab
  wall_curve_door        the east apse's middle module: the chamber-door frame (jamb pilasters, lintel
                         with a fan-shell boss) and a short dark passage beyond
  wall_straight_2_5m     straight module for the long walls (outward +Z, inner face on z = 0)
  wall_niche_conch       5 m long-wall module with a conch niche (R 2.2): a half-dome fluted like a
                         scallop, hinge at the back; the side pool sits in it
  column_whorl           0.5 m x 4 m column carved as stacked helical shell whorls, scalloped capital
  shrine_ceiling         the vault under roof_fan_shell (whole room): a lime-washed fluted cone under the
                         roof's own envelope, two side domes, three oculi with stone rings, ribs, rosettes

Module frames (what the dressing script relies on; also in the manifest's `metrics`):
  curved modules are built around their apse centre at the origin, centred on angle 0 (+X); the dresser
  yaws them by -alpha (alpha = the module's centre angle, 0 = +X, increasing towards +Z).
  straight and niche modules: the inner face on z = 0, the wall in z in [0, wall_t] (outward +Z).
"""

from __future__ import annotations

import math

import numpy as np

import ss_common as sc
from ss_common import kc

M = sc.METRICS

TRI_BUDGET = {
    "floor_slab_1m": (500, 4),
    "wall_curve_r9": (9000, 200),
    "wall_curve_entrance": (14000, 400),
    "wall_curve_door": (15000, 500),
    "wall_straight_2_5m": (4500, 120),
    "wall_niche_conch": (14000, 500),
    "column_whorl": (3600, 160),
    "shrine_ceiling": (44000, 4000),
}

FLOOR_WEATHER = kc.Weathering(moss=0.0, salt=0.3, wet=0.0, erosion=0.4, noise_scale_m=0.45)


# ---------------------------------------------------------------------------------------------
# Floor
# ---------------------------------------------------------------------------------------------
def build_floor_slab(seed: int = 301) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("floor_slab_1m", seed)
    noise = kc.Noise3(rng)
    size = M["floor_slab_m"]
    h = size * 0.5
    mb = kc.MeshBuilder("floor_slab_1m")
    pav = mb.material(sc.M_PAVING)
    mor = mb.material(sc.M_MORTAR)
    # Mortar bed just under the flags' top (joints read white, slightly sunk).
    bed = np.array([[[-h, -0.014, -h], [h, -0.014, -h]], [[-h, -0.014, h], [h, -0.014, h]]])
    kc.quad_strip(mb, bed, mor, uv=bed[..., [0, 2]], col=sc.col4(0, 0.4, 0, 0.3), uv2=(0.5, 0.5), flip=True,
                  smooth=False)
    rows = 2
    row_w = size / rows
    for r in range(rows):
        z = -h + row_w * (r + 0.5)
        off = 0.35 * (r % 2) + 0.2 * float(rng.random())
        for x0, x1 in sc.split_run(size, rng, mean=0.55, spread=0.15, offset=off):
            half = (0.5 * (x1 - x0) - 0.007, 0.05, 0.5 * row_w - 0.007)
            sink = 0.004 * float(rng.random())  # flags settle unevenly
            kc.rounded_block(mb, (-h + 0.5 * (x0 + x1), -0.05 - sink, z), half, pav, radius=0.018, seg=2,
                             noise=noise, disp_m=0.004, disp_period_m=0.3, weather=FLOOR_WEATHER,
                             variation=float(rng.random()), uv_scale=1.0)
    lod = kc.MeshBuilder("floor_slab_1m-lod1")
    top = np.array([[[-h, 0.0, -h], [h, 0.0, -h]], [[-h, 0.0, h], [h, 0.0, h]]])
    kc.quad_strip(lod, top, lod.material(sc.M_PAVING), uv=top[..., [0, 2]], col=sc.col4(0, 0.3, 0, 0.4),
                  uv2=(0.9, 0.5), flip=True, smooth=False)
    col = kc.MeshBuilder("floor_slab_1m-col")
    sc.box_proxy(col, (0.0, -0.1, 0.0), (h, 0.1, h))
    return [mb, lod, col]


# ---------------------------------------------------------------------------------------------
# Walls: shared parts
# ---------------------------------------------------------------------------------------------
CORNICE_PROFILE = [(0.0, 3.78), (-0.06, 3.82), (-0.1, 3.9), (-0.1, 3.97), (-0.16, 4.03), (-0.2, 4.1),
                   (-0.2, 4.17), (0.0, 4.2)]  # (inward offset from the inner face, y), bottom to top
# Outer offset from the outer face, y; listed over the top and then down the face (descending: faces out).
COPING_PROFILE = [(-0.62, 4.5), (0.06, 4.42), (0.12, 4.32), (0.1, 4.2), (0.0, 4.16)]


def _cornice_arc(mb, cx, cz, r_in, a0, a1, sides, noise, *, nacre: bool = True) -> None:
    prof = [(r_in + d, y) for d, y in CORNICE_PROFILE]
    sc.lathe(mb, prof, sides, mb.material(sc.M_STONE), center=(cx, 0, cz), a0=a0, a1=a1, noise=noise,
             ao=[0.6, 0.75, 0.9, 0.85, 0.8, 0.95, 1.0, 1.0], variation=0.4)
    if nacre:
        ang = np.linspace(a0, a1, sides * 2 + 1)
        r = r_in - 0.1
        pts = np.stack([cx + np.cos(ang) * r, np.full_like(ang, 3.935), cz + np.sin(ang) * r], axis=-1)
        nrm = -np.stack([np.cos(ang), np.zeros_like(ang), np.sin(ang)], axis=-1)
        sc.nacre_band(mb, pts, nrm, 0.045, mb.material(sc.M_NACRE))


def _coping_arc(mb, cx, cz, r_out, a0, a1, sides, noise) -> None:
    sc.lathe(mb, [(r_out + d, y) for d, y in COPING_PROFILE], sides, mb.material(sc.M_MORTAR), center=(cx, 0, cz),
             a0=a0, a1=a1, noise=noise, variation=0.2)


def _forbid_width(forbid, y0: float, y1: float) -> float:
    """The widest half-interval a forbid() removes anywhere in [y0, y1] (0 if none)."""
    w = 0.0
    for y in np.arange(y0, y1, 0.05):
        f = forbid(y, y + 0.05)
        if f is not None:
            w = max(w, abs(f[0]), abs(f[1]))
    return w


def _border_arc(mb, cx, cz, r_in, a0, a1, rng, noise) -> None:
    """Two rows of border flags along the wall foot (the apron that hides the slab grid's edge)."""
    pav = mb.material(sc.M_PAVING)
    apron = M["apron_m"]
    rows = ((r_in - apron, r_in - apron * 0.5), (r_in - apron * 0.5, r_in + 0.05))
    for k, (r0, r1) in enumerate(rows):
        r_mid = 0.5 * (r0 + r1)
        length = (a1 - a0) * r_mid
        for b0, b1 in sc.split_run(length, rng, mean=0.6, spread=0.12, offset=0.3 * k + 0.1):
            a = a0 + 0.5 * (b0 + b1) / r_mid
            c = sc.arc_point(cx, cz, r_mid, a, -0.045 + M["raise_m"])
            kc.rounded_block(mb, c, (0.5 * (b1 - b0) - 0.008, 0.045, 0.5 * (r1 - r0) - 0.008), pav,
                             rot=sc.yaw_rot_for_tangent(a), radius=0.016, seg=2, noise=noise, disp_m=0.003,
                             weather=FLOOR_WEATHER, variation=float(rng.random()))
    ang = np.linspace(a0, a1, 9)
    bed = np.zeros((2, 9, 3))
    for i, r in enumerate((r_in + 0.05, r_in - apron)):
        bed[i, :, 0] = cx + np.cos(ang) * r
        bed[i, :, 1] = -0.012
        bed[i, :, 2] = cz + np.sin(ang) * r
    kc.quad_strip(mb, bed, mb.material(sc.M_MORTAR), uv=bed[..., [0, 2]], col=sc.col4(0, 0.4, 0, 0.3),
                  uv2=(0.5, 0.5), flip=True, smooth=False)


def _arc_wall(mb, rng, noise, a0, a1, *, forbid=None, snap=(), lod: bool = False) -> None:
    """The coursed wall body, mortar beds, cornice, coping and border between angles a0..a1 around the
    origin (apse-local)."""
    r_in, t = M["wall_r_m"], M["wall_t_m"]
    r_mid = r_in + t * 0.5
    y_f, y_c = M["foundation_y_m"], CORNICE_PROFILE[0][1]
    stone = mb.material(sc.M_STONE)
    if lod:
        sc.arc_slab_lod(mb, 0.0, 0.0, r_in, r_in + t, a0, a1, y_f, M["spring_y_m"] + 0.3, stone)
        return
    length = (a1 - a0) * r_mid
    sides = max(4, int(math.ceil((a1 - a0) / math.radians(3.0))))
    sc.wall_blocks(mb, sc.arc_frame(0.0, 0.0, r_mid, 0.5 * (a0 + a1)), length, t, y_f, y_c, rng, noise, mat=stone,
                   seg=2, forbid=forbid, snap=(0.0,) + tuple(snap), low_seg_below=-0.6)
    ranges = [(a0, a1)]
    if forbid is not None:
        ga = (_forbid_width(forbid, 0.0, y_c) + 0.02) / r_mid
        ranges = [(a0, -ga), (ga, a1)]
    for b0, b1 in ranges:
        n = max(2, int(sides * (b1 - b0) / (a1 - a0)))
        sc.mortar_arc_bed(mb, 0.0, 0.0, r_in + 0.022, b0, b1, -0.02, y_c, mb.material(sc.M_MORTAR), outward=False,
                          sides=n)
        sc.mortar_arc_bed(mb, 0.0, 0.0, r_in + t - 0.022, b0, b1, y_f, y_c, mb.material(sc.M_MORTAR), outward=True,
                          sides=n)
    _cornice_arc(mb, 0.0, 0.0, r_in, a0, a1, sides, noise)
    _coping_arc(mb, 0.0, 0.0, r_in + t, a0, a1, sides, noise)
    _border_arc(mb, 0.0, 0.0, r_in, a0, a1, rng, noise)


def _arc_col(mb_col, a0, a1, segs: int = 3) -> None:
    r_in, t = M["wall_r_m"], M["wall_t_m"]
    da = (a1 - a0) / segs
    for k in range(segs):
        a = a0 + da * (k + 0.5)
        c = sc.arc_point(0.0, 0.0, r_in + t * 0.5, a, 1.1)
        sc.box_proxy(mb_col, c, ((r_in + t) * math.sin(da * 0.5) + 0.02, 3.3, t * 0.5), rot=sc.yaw_rot_for_tangent(a))


def build_wall_curve(seed: int = 311) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("wall_curve_r9", seed)
    noise = kc.Noise3(rng)
    half = math.radians(M["apse_module_deg"] * 0.5)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("wall_curve_r9" + ("-lod1" if lod else ""))
        _arc_wall(mb, rng, noise, -half, half, lod=lod)
        out.append(mb)
    col = kc.MeshBuilder("wall_curve_r9-col")
    _arc_col(col, -half, half)
    return out + [col]


# ---------------------------------------------------------------------------------------------
# Entrance (west): a shell arch
# ---------------------------------------------------------------------------------------------
ARCH_SPRING = 2.55
ARCH_BAND = 0.42


def _arch_half_width(y: float, half_w: float, rise: float) -> float:
    """Half width of the opening plus its voussoir band at height y (the courses keep clear of it)."""
    if y <= ARCH_SPRING:
        return half_w
    a, b = half_w + ARCH_BAND, rise + ARCH_BAND
    t = (y - ARCH_SPRING) / b
    return a * math.sqrt(max(0.0, 1.0 - t * t)) if t < 1.0 else 0.0


def _relief_fan(mb, center, face_normal, radius: float, rng, noise, *, ribs: int = 9, span: float = 160.0) -> None:
    """A small fan-shell relief standing on a wall face (Haluna's fan_shell, stood upright)."""
    import shrine  # noqa: PLC0415  (the Haluna kit's module: fan_shell)

    tmp = kc.MeshBuilder("fan")
    shrine.fan_shell(tmp, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), radius, rng, noise, span_deg=span, ribs=ribs, lift=0.22,
                     droop_deg=0.0, weather=sc.TENDED)
    n = kc.normalize(np.asarray(face_normal, float))
    up = np.array([0.0, 1.0, 0.0])
    rot = np.column_stack([up, n, np.cross(up, n)])
    mb.merge(tmp, rot, center)


def _voussoirs(mb, rng, noise, half_w: float, rise: float, count: int, r_mid: float, mid: float, t: float) -> None:
    stone = mb.material(sc.M_STONE)
    a_e, b_e = half_w + ARCH_BAND * 0.5, rise + ARCH_BAND * 0.5
    for k in range(count):
        phi0 = math.pi * k / count
        phi1 = math.pi * (k + 1) / count
        phi = 0.5 * (phi0 + phi1)
        s = a_e * math.cos(phi)
        y = ARCH_SPRING + b_e * math.sin(phi)
        # Ellipse normal and tangent in the wall plane (s, y).
        rn = kc.normalize(np.array([math.cos(phi) / a_e, math.sin(phi) / b_e]))
        p0 = np.array([a_e * math.cos(phi0), b_e * math.sin(phi0)])
        p1 = np.array([a_e * math.cos(phi1), b_e * math.sin(phi1)])
        half_t = 0.5 * float(np.linalg.norm(p1 - p0)) - 0.012
        a = mid + s / r_mid
        c = sc.arc_point(0.0, 0.0, r_mid, a, y)
        base_rot = sc.yaw_rot_for_tangent(a)
        tan_w, nrm_w = base_rot[:, 0], base_rot[:, 2]
        # yaw_rot_for_tangent's +X runs towards decreasing angle, i.e. decreasing s.
        radial = -tan_w * rn[0] + kc.UP * rn[1]
        along = tan_w * rn[1] + kc.UP * rn[0]
        rot = np.column_stack([radial, along, nrm_w])
        if np.linalg.det(rot) < 0:
            rot[:, 2] *= -1.0
        kc.rounded_block(mb, c, (ARCH_BAND * 0.5 - 0.01, half_t, t * 0.5 + 0.03), stone, rot=rot, radius=0.03,
                         seg=2, noise=noise, disp_m=0.012, weather=sc.TENDED, variation=float(rng.random()))


def build_wall_entrance(seed: int = 312) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("wall_curve_entrance", seed)
    noise = kc.Noise3(rng)
    half = math.radians(M["apse_module_deg"] * 0.5)
    r_in, t = M["wall_r_m"], M["wall_t_m"]
    r_mid = r_in + t * 0.5
    half_w, rise = M["entrance_w_m"] * 0.5, M["entrance_h_m"] - ARCH_SPRING
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("wall_curve_entrance" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        if lod:
            ga = (half_w + 0.05) / r_mid
            for a0, a1 in ((-half, -ga), (ga, half)):
                sc.arc_slab_lod(mb, 0.0, 0.0, r_in, r_in + t, a0, a1, M["foundation_y_m"], M["spring_y_m"] + 0.3,
                                stone, sides=2)
            sc.arc_slab_lod(mb, 0.0, 0.0, r_in, r_in + t, -ga, ga, M["entrance_h_m"] + 0.1, M["spring_y_m"] + 0.3,
                            stone, sides=2)
            sc.arc_slab_lod(mb, 0.0, 0.0, r_in, r_in + t, -ga, ga, M["foundation_y_m"], 0.0, stone, sides=2)
            out.append(mb)
            continue

        def forbid(y_lo: float, y_hi: float):
            if y_hi <= 1e-6:
                return None
            w = max(_arch_half_width(y, half_w, rise) for y in np.linspace(y_lo + 1e-4, y_hi - 1e-4, 9))
            return (-w, w) if w > 0.0 else None

        _arc_wall(mb, rng, noise, -half, half, forbid=forbid, snap=(ARCH_SPRING,))
        _voussoirs(mb, rng, noise, half_w, rise, 13, r_mid, 0.0, t)
        # Keystone fan-shells: the larger outside (S01 reads it), a smaller one over the inner face.
        top = ARCH_SPRING + rise + ARCH_BAND * 0.5
        _relief_fan(mb, sc.arc_point(0.0, 0.0, r_in + t + 0.04, 0.0, top - 0.22), (1.0, 0.0, 0.0), 0.55, rng, noise)
        _relief_fan(mb, sc.arc_point(0.0, 0.0, r_in - 0.04, 0.0, top - 0.18), (-1.0, 0.0, 0.0), 0.4, rng, noise)
        # Threshold slab through the wall, worn in the middle (where every pilgrim steps).
        kc.rounded_block(mb, (r_in + t * 0.5, -0.07, 0.0), (t * 0.5 + 0.12, 0.07, half_w + 0.05), stone, radius=0.03,
                         seg=4, noise=noise, disp_m=0.01, weather=kc.Weathering(moss=0.0, salt=0.35, erosion=0.75),
                         variation=0.35)
        # Jamb reveals: the opening's sides are block ends; line them with a smooth reveal face.
        for sgn in (-1.0, 1.0):
            a = sgn * half_w / r_mid
            c = sc.arc_point(0.0, 0.0, r_mid, a, ARCH_SPRING * 0.5)
            kc.rounded_block(mb, c, (0.06, ARCH_SPRING * 0.5 - 0.01, t * 0.5 + 0.02), stone,
                             rot=sc.yaw_rot_for_tangent(a), radius=0.02, seg=2, weather=sc.TENDED, variation=0.6)
        out.append(mb)
    col = kc.MeshBuilder("wall_curve_entrance-col")
    ga = (half_w + 0.02) / r_mid
    _arc_col(col, -half, -ga, 2)
    _arc_col(col, ga, half, 2)
    c = sc.arc_point(0.0, 0.0, r_mid, 0.0, (M["entrance_h_m"] + 4.5) * 0.5)
    sc.box_proxy(col, c, (0.3, (4.5 - M["entrance_h_m"]) * 0.5, half_w + 0.1))
    return out + [col]


# ---------------------------------------------------------------------------------------------
# Chamber door frame (east)
# ---------------------------------------------------------------------------------------------
def build_wall_door(seed: int = 313) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("wall_curve_door", seed)
    noise = kc.Noise3(rng)
    half = math.radians(M["apse_module_deg"] * 0.5)
    r_in, t = M["wall_r_m"], M["wall_t_m"]
    r_mid = r_in + t * 0.5
    hw = M["door_w_m"] * 0.5 + 0.05
    dh = M["door_h_m"] + 0.1
    passage = 2.6
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("wall_curve_door" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        dark = mb.material(sc.M_DARK)
        if lod:
            ga = hw / r_mid
            for a0, a1 in ((-half, -ga), (ga, half)):
                sc.arc_slab_lod(mb, 0.0, 0.0, r_in, r_in + t, a0, a1, M["foundation_y_m"], M["spring_y_m"] + 0.3,
                                stone, sides=2)
            sc.arc_slab_lod(mb, 0.0, 0.0, r_in, r_in + t, -ga, ga, dh, M["spring_y_m"] + 0.3, stone, sides=2)
            kc.rounded_block(mb, (r_in + t + passage, dh * 0.5, 0.0), (0.05, dh * 0.5, hw), dark, radius=0.01, seg=1)
            out.append(mb)
            continue

        def forbid(y_lo: float, y_hi: float):
            if y_hi <= 1e-6 or y_lo >= dh + 0.32 - 1e-3:
                return None
            w = hw + 0.44 if y_hi > dh + 1e-3 else hw + 0.02  # the lintel's course leaves room for it
            return (-w, w)

        _arc_wall(mb, rng, noise, -half, half, forbid=forbid, snap=(dh, dh + 0.32))
        # Lintel (one long stone) with a fan-shell boss facing the room.
        kc.rounded_block(mb, (r_mid, dh + 0.16, 0.0), (t * 0.5 + 0.05, 0.16, hw + 0.42), stone, radius=0.035, seg=4,
                         noise=noise, disp_m=0.01, weather=sc.TENDED, variation=0.2)
        _relief_fan(mb, (r_in - 0.08, dh + 0.04, 0.0), (-1.0, 0.0, 0.0), 0.3, rng, noise, ribs=7)
        # Jamb pilasters projecting 0.42 into the room: the door sits between them.
        for sgn in (-1.0, 1.0):
            z = sgn * (hw + 0.2)
            y = 0.0
            for k, hgt in enumerate((1.25, 1.2, dh - 2.45)):
                kc.rounded_block(mb, (r_in - 0.2, y + hgt * 0.5, z), (0.24 + 0.02 * (k == 0), hgt * 0.5 - 0.008, 0.2),
                                 stone, radius=0.03, seg=3, noise=noise, disp_m=0.008, weather=sc.TENDED,
                                 variation=float(rng.random()))
                y += hgt
            # Nacre fillet down each jamb's inner edge (the door's frame glints when the pool rises).
            pts = np.array([[r_in - 0.43, 0.05, sgn * hw], [r_in - 0.43, dh - 0.05, sgn * hw]])
            pts = np.linspace(pts[0], pts[1], 6)
            sc.nacre_band(mb, pts, (-1.0, 0.0, 0.0), 0.04, mb.material(sc.M_NACRE))
        # Threshold with the slot the valve sinks into.
        for sgn in (-1.0, 1.0):
            kc.rounded_block(mb, (r_in + 0.1 + sgn * 0.0, -0.06, 0.0), (0.12, 0.06, hw), stone, radius=0.02, seg=2,
                             weather=sc.TENDED, variation=0.5)
        # The passage beyond: side walls, flat slab roof, floor, and darkness at the end.
        x0, x1 = r_in + t, r_in + t + passage
        for sgn in (-1.0, 1.0):

            def side_frame(s: float, sgn=sgn):
                return np.array([0.5 * (x0 + x1) + s, 0.0, sgn * (hw + 0.25)]), kc.rot_y(0.0)

            sc.wall_blocks(mb, side_frame, passage, 0.5, 0.0, dh + 0.3, rng, noise, mat=stone, seg=2, block_mean=0.7)
        kc.rounded_block(mb, (0.5 * (x0 + x1), dh + 0.18, 0.0), (passage * 0.5, 0.18, hw + 0.5), stone, radius=0.03,
                         seg=2, weather=sc.TENDED, variation=0.7)
        kc.rounded_block(mb, (0.5 * (x0 + x1), -0.06, 0.0), (passage * 0.5, 0.06, hw), mb.material(sc.M_PAVING),
                         radius=0.02, seg=3, weather=FLOOR_WEATHER, variation=0.5)
        kc.rounded_block(mb, (x1 + 0.05, dh * 0.5, 0.0), (0.05, dh * 0.5 + 0.1, hw + 0.1), dark, radius=0.01, seg=1)
        out.append(mb)
    col = kc.MeshBuilder("wall_curve_door-col")
    ga = (hw + 0.4) / r_mid
    _arc_col(col, -half, -ga, 2)
    _arc_col(col, ga, half, 2)
    for sgn in (-1.0, 1.0):
        sc.box_proxy(col, (r_in + t + passage * 0.5, 1.8, sgn * (hw + 0.25)), (passage * 0.5, 1.8, 0.25))
        sc.box_proxy(col, (r_in - 0.2, dh * 0.5, sgn * (hw + 0.2)), (0.24, dh * 0.5, 0.2))
    sc.box_proxy(col, (r_in + t + passage + 0.05, dh * 0.5, 0.0), (0.05, dh * 0.5, hw))
    return out + [col]


# ---------------------------------------------------------------------------------------------
# Straight module and the conch niche (long walls)
# ---------------------------------------------------------------------------------------------
def _straight_parts(mb, rng, noise, x0: float, x1: float, *, forbid=None, snap=(), border: bool = True) -> None:
    t = M["wall_t_m"]
    y_f, y_c = M["foundation_y_m"], CORNICE_PROFILE[0][1]
    stone = mb.material(sc.M_STONE)
    mor = mb.material(sc.M_MORTAR)
    length = x1 - x0
    sc.wall_blocks(mb, sc.line_frame(t * 0.5), length, t, y_f, y_c, rng, noise, mat=stone, seg=2, forbid=forbid,
                   snap=(0.0,) + tuple(snap), low_seg_below=-0.6, s_range=(x0, x1))
    ranges = [(x0, x1)]
    if forbid is not None:
        w = _forbid_width(forbid, 0.0, y_c) + 0.02
        ranges = [(x0, -w), (w, x1)]
    for b0, b1 in ranges:
        for z, outer in ((0.022, False), (t - 0.022, True)):
            g = np.array([[[b0, y_f if outer else -0.02, z], [b1, y_f if outer else -0.02, z]],
                          [[b0, y_c, z], [b1, y_c, z]]])
            # Rows ascend along +Y, columns along +X: normal = +X x +Y = +Z (outward) unless flipped.
            kc.quad_strip(mb, g, mor, uv=g[..., [0, 1]], col=sc.col4(0, 0.25, 0, 0.3), uv2=(0.55, 0.5),
                          flip=not outer)
    # Cornice (inside) and coping (outside) as straight extrusions of the same profiles.
    for prof, is_in in ((CORNICE_PROFILE, True), (COPING_PROFILE, False)):
        pts = [(d, y) for d, y in prof] if is_in else [(t + d, y) for d, y in prof]
        grid = np.zeros((len(pts), 2, 3))
        for i, (z, y) in enumerate(pts):
            grid[i, 0] = (x0, y, z)
            grid[i, 1] = (x1, y, z)
        # Rows follow the profile, columns run +X: normal = (0, -dz, dy), so both need the flip.
        kc.quad_strip(mb, grid, stone if is_in else mor, uv=grid[..., [0, 1]],
                      col=sc.col4(0.05, 0.3, 0, 0.35), uv2=(0.9, 0.4), flip=True)
    pts = np.linspace([x0, 3.935, -0.1], [x1, 3.935, -0.1], 6)
    sc.nacre_band(mb, pts, (0.0, 0.0, -1.0), 0.045, mb.material(sc.M_NACRE))
    if border:
        pav = mb.material(sc.M_PAVING)
        apron = M["apron_m"]
        for k, (z0, z1) in enumerate(((-apron, -apron * 0.5), (-apron * 0.5, 0.05))):
            for b0, b1 in sc.split_run(length, rng, mean=0.6, spread=0.12, offset=0.3 * k + 0.1):
                kc.rounded_block(mb, (x0 + 0.5 * (b0 + b1), -0.045 + M["raise_m"], 0.5 * (z0 + z1)),
                                 (0.5 * (b1 - b0) - 0.008, 0.045, 0.5 * (z1 - z0) - 0.008), pav, radius=0.016, seg=2,
                                 noise=noise, disp_m=0.003, weather=FLOOR_WEATHER, variation=float(rng.random()))
        bed = np.array([[[x0, -0.012, 0.05], [x1, -0.012, 0.05]], [[x0, -0.012, -apron], [x1, -0.012, -apron]]])
        kc.quad_strip(mb, bed, mor, uv=bed[..., [0, 2]], col=sc.col4(0, 0.4, 0, 0.3), uv2=(0.5, 0.5), flip=False,
                      smooth=False)


def _straight_lod(mb, x0: float, x1: float) -> None:
    t = M["wall_t_m"]
    stone = mb.material(sc.M_STONE)
    kc.rounded_block(mb, (0.5 * (x0 + x1), 0.5 * (M["foundation_y_m"] + 4.5), t * 0.5),
                     (0.5 * (x1 - x0), 0.5 * (4.5 - M["foundation_y_m"]), t * 0.5), stone, radius=0.01, seg=1,
                     weather=sc.TENDED)


def build_wall_straight(seed: int = 314) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("wall_straight_2_5m", seed)
    noise = kc.Noise3(rng)
    h = M["straight_module_m"] * 0.5
    mb = kc.MeshBuilder("wall_straight_2_5m")
    _straight_parts(mb, rng, noise, -h, h)
    lod = kc.MeshBuilder("wall_straight_2_5m-lod1")
    _straight_lod(lod, -h, h)
    col = kc.MeshBuilder("wall_straight_2_5m-col")
    sc.box_proxy(col, (0.0, 1.1, M["wall_t_m"] * 0.5), (h, 3.3, M["wall_t_m"] * 0.5))
    return [mb, lod, col]


NICHE_SPRING = 2.5
NICHE_RISE = 1.6


def _conch(mb, rng, noise, r: float, rise: float, depth: float, y_s: float, *, lod: bool, outer: bool = False) -> None:
    """Half-dome over the niche, ribbed like a scallop with its hinge at the back (z = depth), spring y_s.
    alpha runs along the front rim (left -> top -> right), beta from the front plane to the hinge."""
    na, nb = (8, 3) if lod else (49, 14)
    ribs = 11
    grid = np.zeros((nb + 1, na + 1, 3))
    for i in range(nb + 1):
        beta = (math.pi * 0.5) * i / nb
        for j in range(na + 1):
            alpha = math.pi * j / na
            flute = 0.0 if (lod or outer) else 0.06 * (0.5 - 0.5 * math.cos(alpha * ribs * 2.0)) * math.cos(beta)
            k = 1.0 - flute
            grid[i, j] = (-r * math.cos(alpha) * math.cos(beta) * k, y_s + rise * math.sin(alpha) * math.cos(beta) * k,
                          depth * math.sin(beta) * k)
    breakup = noise.fbm(grid / 0.4, 2)
    beta_f = np.linspace(0, 1, nb + 1)[:, None] * np.ones((1, na + 1))
    col = sc.col4(0.0, 0.25 + 0.35 * breakup * beta_f, 0.0, 0.25 * breakup)
    uv = grid[..., [0, 1]] + grid[..., [2, 2]] * 0.5
    uv2 = np.stack([1.0 - 0.45 * beta_f, np.full(beta_f.shape, 0.45)], axis=-1)
    # Rows run front -> hinge, columns left -> right along the rim. Inside faces the room (-Z, down).
    kc.quad_strip(mb, grid, mb.material(sc.M_MORTAR if not outer else sc.M_STONE), uv=uv, col=col, uv2=uv2,
                  flip=outer)
    if not lod and not outer:
        # Coral ribs along every other flute ridge, converging on the hinge.
        for j in range(0, na + 1, max(1, na // (ribs * 2)) * 2):
            line = grid[:, j]
            kc.tube(mb, line + np.array([0.0, 0.0, 0.0]), 0.03, 4, mb.material(sc.M_STONE), weather=sc.TENDED,
                    variation=0.3)


def build_wall_niche(seed: int = 315) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("wall_niche_conch", seed)
    noise = kc.Noise3(rng)
    h = M["straight_module_m"]  # the niche module spans two straight slots
    r_in, t = M["niche_r_m"], M["wall_t_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("wall_niche_conch" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        if lod:
            _straight_lod(mb, -h, -r_in)
            _straight_lod(mb, r_in, h)
            kc.rounded_block(mb, (0.0, 4.0, t * 0.5), (r_in, 0.5, t * 0.5), stone, radius=0.01, seg=1)
            sc.arc_slab_lod(mb, 0.0, 0.0, r_in, r_in + t, 0.0, math.pi, M["foundation_y_m"], NICHE_SPRING, stone,
                            sides=6)
            _conch(mb, rng, noise, r_in, NICHE_RISE, r_in, NICHE_SPRING, lod=True)
            out.append(mb)
            continue

        def forbid(y_lo: float, y_hi: float):
            if y_hi <= 1e-6:
                return None
            a, b = r_in + 0.25, NICHE_RISE + 0.25
            w = 0.0
            for y in np.linspace(y_lo + 1e-4, y_hi - 1e-4, 9):
                if y <= NICHE_SPRING:
                    w = max(w, r_in)
                else:
                    tt = (y - NICHE_SPRING) / b
                    w = max(w, a * math.sqrt(max(0.0, 1.0 - tt * tt)) if tt < 1.0 else 0.0)
            return (-w, w) if w > 0.0 else None

        _straight_parts(mb, rng, noise, -h, h, forbid=forbid, snap=(NICHE_SPRING,), border=False)
        for x0, x1 in ((-h, -r_in - 0.05), (r_in + 0.05, h)):
            pav = mb.material(sc.M_PAVING)
            for b0, b1 in sc.split_run(x1 - x0, rng, mean=0.6, spread=0.1):
                for z0, z1 in ((-M["apron_m"], -0.7), (-0.7, 0.05)):
                    kc.rounded_block(mb, (x0 + 0.5 * (b0 + b1), -0.045 + M["raise_m"], 0.5 * (z0 + z1)),
                                     (0.5 * (b1 - b0) - 0.008, 0.045, 0.5 * (z1 - z0) - 0.008), pav, radius=0.016,
                                     seg=2, weather=FLOOR_WEATHER, variation=float(rng.random()))
        # The apse wall of the niche (half circle bulging to +Z) up to the conch's springing.
        r_mid = r_in + t * 0.5
        sc.wall_blocks(mb, sc.arc_frame(0.0, 0.0, r_mid, math.pi * 0.5), math.pi * r_mid, t, M["foundation_y_m"],
                       NICHE_SPRING, rng, noise, mat=stone, seg=2, block_mean=0.55, snap=(0.0,), low_seg_below=-0.6)
        sc.mortar_arc_bed(mb, 0.0, 0.0, r_in + 0.02, 0.0, math.pi, -0.02, NICHE_SPRING, mb.material(sc.M_MORTAR),
                          outward=False, sides=24)
        sc.mortar_arc_bed(mb, 0.0, 0.0, r_in + t - 0.02, 0.0, math.pi, M["foundation_y_m"], NICHE_SPRING,
                          mb.material(sc.M_MORTAR), outward=True, sides=24)
        # Impost moulding at the springing, then the conch (inside) and its stone shell (outside).
        sc.lathe(mb, [(r_in + 0.01, NICHE_SPRING - 0.12), (r_in - 0.07, NICHE_SPRING - 0.06),
                      (r_in - 0.07, NICHE_SPRING), (r_in + 0.01, NICHE_SPRING + 0.02)], 24, stone, a0=0.0,
                 a1=math.pi, noise=noise)
        _conch(mb, rng, noise, r_in, NICHE_RISE, r_in, NICHE_SPRING, lod=False)
        _conch(mb, rng, noise, r_in + t, NICHE_RISE + 0.35, r_in + t, NICHE_SPRING, lod=False, outer=True)
        # Archivolt: a ring of small voussoir stones around the niche's front rim, with a nacre fillet.
        n_v = 15
        for k in range(n_v):
            al = math.pi * (k + 0.5) / n_v
            p = np.array([-(r_in + 0.12) * math.cos(al), NICHE_SPRING + (NICHE_RISE + 0.12) * math.sin(al), 0.03])
            rn = kc.normalize(np.array([-math.cos(al) / r_in, math.sin(al) / NICHE_RISE, 0.0]))
            along = np.array([rn[1], -rn[0], 0.0])
            rot = np.column_stack([rn, along, [0.0, 0.0, 1.0]])
            if np.linalg.det(rot) < 0:
                rot[:, 1] *= -1.0
            seg_len = math.pi * (r_in + NICHE_RISE) * 0.5 / n_v
            kc.rounded_block(mb, p, (0.13, seg_len * 0.5 - 0.01, 0.1), stone, rot=rot, radius=0.025, seg=2,
                             noise=noise, disp_m=0.006, weather=sc.TENDED, variation=float(rng.random()))
        al = np.linspace(0.02, math.pi - 0.02, 40)
        rim = np.stack([-(r_in - 0.005) * np.cos(al), NICHE_SPRING + (NICHE_RISE - 0.005) * np.sin(al),
                        np.full_like(al, -0.075)], axis=-1)
        sc.nacre_band(mb, rim, (0.0, 0.0, -1.0), 0.04, mb.material(sc.M_NACRE))
        out.append(mb)
    col = kc.MeshBuilder("wall_niche_conch-col")
    for x0, x1 in ((-h, -r_in), (r_in, h)):
        sc.box_proxy(col, (0.5 * (x0 + x1), 1.1, t * 0.5), (0.5 * (x1 - x0), 3.3, t * 0.5))
    for k in range(6):
        a = math.pi * (k + 0.5) / 6
        c = sc.arc_point(0.0, 0.0, r_in + t * 0.5, a, 1.1)
        sc.box_proxy(col, c, ((r_in + t) * math.sin(math.pi / 12) + 0.03, 3.3, t * 0.5), rot=sc.yaw_rot_for_tangent(a))
    return out + [col]


# ---------------------------------------------------------------------------------------------
# Column: stacked helical shell whorls
# ---------------------------------------------------------------------------------------------
def _whorl_shaft(mb, rng, noise, y0: float, y1: float, *, sides: int, rows: int, r0: float, amp: float,
                 pitch: float) -> None:
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    ys = np.linspace(y1, y0, rows + 1)  # top -> bottom: descending profile faces outward
    grid = np.zeros((rows + 1, sides + 1, 3))
    phase = (ys[:, None] / pitch - ang[None, :] / (2.0 * math.pi)) % 1.0
    bump = np.sin(math.pi * phase) ** 0.55  # 0 in the suture, 1 on the whorl's shoulder
    shoulder = np.clip((phase - 0.15) / 0.5, 0, 1) * np.clip((1.0 - phase) / 0.35, 0, 1)
    r = r0 + amp * (0.55 * bump + 0.45 * shoulder)
    grid[..., 0] = np.cos(ang)[None, :] * r
    grid[..., 1] = ys[:, None]
    grid[..., 2] = np.sin(ang)[None, :] * r
    breakup = noise.fbm(grid / 0.3, 2)
    col = sc.col4(0.03 * breakup, 0.55 * (1.0 - bump) * (0.6 + breakup), 0.0, 0.25 + 0.45 * bump * breakup)
    uv = np.stack([np.broadcast_to(ang[None, :] * r0, grid.shape[:2]), grid[..., 1]], axis=-1)
    uv2 = np.stack([0.55 + 0.45 * bump, np.full(bump.shape, float(rng.random()))], axis=-1)
    kc.quad_strip(mb, grid, mb.material(sc.M_STONE), uv=uv, col=col, uv2=uv2)


def build_column(seed: int = 316) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("column_whorl", seed)
    noise = kc.Noise3(rng)
    rad = M["column_d_m"] * 0.5
    hgt = M["column_h_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("column_whorl" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        sides = 8 if lod else 28
        # Base: plinth disc and a torus (profile top -> bottom = faces outward).
        base = [(0.0, 0.26), (rad * 0.9, 0.26), (rad + 0.05, 0.22), (rad + 0.07, 0.16), (rad + 0.12, 0.12),
                (rad + 0.12, 0.0)]
        sc.lathe(mb, base if not lod else [base[0], base[2], base[-1]], sides, stone, noise=noise,
                 salt_boost=[0, 0.2, 0.4, 0.4, 0.5, 0.6] if not lod else None, ao=None, variation=0.2)
        if lod:
            sc.lathe(mb, [(rad, hgt - 0.4), (rad, 0.26)], sides, stone, variation=0.2)
        else:
            _whorl_shaft(mb, rng, noise, 0.24, hgt - 0.42, sides=sides, rows=44, r0=rad - 0.05, amp=0.06, pitch=0.44)
        # Capital: a scalloped flare (11 lobes) under a round abacus.
        lobes = 11
        cap = [(0.0, hgt), (rad + 0.2, hgt), (rad + 0.2, hgt - 0.1), (rad + 0.14, hgt - 0.14), (rad + 0.08, hgt - 0.2),
               (rad + 0.0, hgt - 0.3), (rad - 0.04, hgt - 0.38), (rad - 0.02, hgt - 0.44)]

        def scallop(ang, i):
            if lod or i < 3:
                return np.ones_like(ang)
            return 1.0 - 0.07 * (0.5 - 0.5 * np.cos(ang * lobes)) * (i - 2) / 5.0

        sc.lathe(mb, cap if not lod else [cap[0], cap[1], cap[2], cap[-1]], sides * (2 if not lod else 1), stone,
                 noise=noise, r_mod=scallop, variation=0.25)
        out.append(mb)
    col = kc.MeshBuilder("column_whorl-col")
    ang = np.linspace(0, 2 * math.pi, 9)[:-1]
    sc.prism_proxy(col, np.stack([np.cos(ang) * (rad + 0.05), np.sin(ang) * (rad + 0.05)], axis=-1), 0.0, hgt)
    return out + [col]


# ---------------------------------------------------------------------------------------------
# Ceiling: the vault under roof_fan_shell
# ---------------------------------------------------------------------------------------------
def roof_envelope(scale: float) -> tuple[np.ndarray, np.ndarray, float]:
    """The Haluna roof_fan_shell's lower envelope by radius (scaled, roof base at y 0): radii, the lowest
    roof point per radius bin (monotone, non-increasing outward), and the roof's outer radius."""
    import shrine  # noqa: PLC0415  (Haluna kit: roof_fan_shell)

    mb = shrine.build_roof_fan_shell()[0]
    p = np.asarray(mb.pos) * scale
    r = np.hypot(p[:, 0], p[:, 2])
    radii = np.arange(0.0, r.max() + 0.25, 0.25)
    env = np.full(len(radii), np.inf)
    idx = np.clip((r / 0.25).astype(int), 0, len(radii) - 1)
    np.minimum.at(env, idx, p[:, 1])
    # Bins with no vertices take their neighbours'; then make it fall monotonically outward.
    finite = np.isfinite(env)
    env = np.interp(radii, radii[finite], env[finite])
    env = np.minimum.accumulate(env)
    return radii, env, float(r.max())


def ceiling_layout() -> dict:
    """Where the vault, its oculi and the central roof sit (also written to the manifest)."""
    s = M["roof_scale"]
    radii, env, r_roof = roof_envelope(s)
    clear = 0.3
    # Lift the roof until its envelope, less the clearance and the vault's thickness, clears the spring
    # line everywhere inside its footprint.
    roof_y = M["spring_y_m"] + clear + M["ceiling_t_m"] - float(env.min())
    under = env + roof_y - clear - M["ceiling_t_m"]  # the highest the vault may reach, per radius
    # The roof's tiers make that envelope a staircase; the vault is the largest smooth bell (a raised
    # cosine from the oculus to the roof's rim) that stays under it everywhere.
    spring = M["spring_y_m"]
    rh, rr = M["oculus_r_m"], r_roof * 0.98
    u = np.clip((radii - rh) / (rr - rh), 0.0, 1.0)
    bell = (0.5 + 0.5 * np.cos(np.pi * u)) ** 0.8
    ok = bell > 0.03
    amp = float(np.min((under[ok] - spring) / bell[ok]))
    peak = spring + amp
    # Holes in the vault. The open domes' holes sit on their crowns; the roofed one sits where the sun,
    # through the roof's ring, meets the vault, and a slanted light well joins the two.
    el, az = math.radians(M["sun_elev_deg"]), math.radians(M["sun_az_deg"])
    travel = np.array([-math.sin(az), 0.0, math.cos(az)])
    holes, well = [], None
    for k, (ox, oz) in enumerate(M["oculi"]):
        if k != M["roof_oculus"]:
            holes.append((ox, oz))
            continue
        ring_y = roof_y + M["roof_ring_y_m"] * s
        off = travel * (ring_y - peak) / math.tan(el)
        holes.append((ox + off[0], oz + off[2]))
        well = (np.array([ox, ring_y - 0.12, oz]), np.array([ox + off[0], peak, oz + off[2]]))
    return {"radii": radii, "env": spring + amp * bell, "r_roof": r_roof, "roof_y": roof_y, "peak": peak,
            "holes": holes, "well": well}


def _well(mb: kc.MeshBuilder, bottom, top, r_top: float, r_bot: float, sides: int, mat: int) -> None:
    """A drum from `bottom` to `top` (it may lean), facing inward (seen from inside, looking up)."""
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    grid = np.zeros((2, sides + 1, 3))
    for i, (c, r) in enumerate(((np.asarray(top, float), r_top), (np.asarray(bottom, float), r_bot))):
        grid[i, :, 0] = c[0] + np.cos(ang) * r
        grid[i, :, 1] = c[1]
        grid[i, :, 2] = c[2] + np.sin(ang) * r
    uv = np.stack([np.broadcast_to(ang, (2, sides + 1)), grid[..., 1]], axis=-1)
    # Rows descend, columns increase in angle: the faces point outward; the flip turns them in.
    kc.quad_strip(mb, grid, mat, uv=uv, col=sc.col4(0.0, 0.3, 0.0, 0.3), uv2=(0.6, 0.5), flip=True)


def _plan_inside(x: np.ndarray, z: np.ndarray, grow: float) -> np.ndarray:
    cx, r = M["apse_cx_m"], M["wall_r_m"] + grow
    in_rect = (np.abs(x) <= cx) & (np.abs(z) <= r)
    in_w = np.hypot(x + cx, z) <= r
    in_e = np.hypot(x - cx, z) <= r
    return in_rect | in_w | in_e


def _vault_height(x: np.ndarray, z: np.ndarray, lay: dict, *, flutes: bool) -> tuple[np.ndarray, np.ndarray]:
    """Underside height of the vault and a 0..1 flute-ridge mask (for ribs and paint)."""
    spring = M["spring_y_m"]
    h = np.full(x.shape, spring)
    ridge = np.zeros(x.shape)
    side_peak, side_r = 1.3, 3.4
    for ox, oz, kind in ((o[0], o[1], k) for k, o in enumerate(M["oculi"])):
        dx, dz = x - ox, z - oz
        r = np.hypot(dx, dz)
        th = np.arctan2(dz, dx)
        if kind == 1:
            dome = np.interp(r, lay["radii"], lay["env"], right=spring)
            n = 24
        else:
            dome = spring + side_peak * np.clip(1.0 - (r / side_r) ** 2, 0.0, None)
            n = 14
        fade = kc.smoothstep(M["oculus_r_m"], M["oculus_r_m"] + 1.2, r) * (dome > spring + 0.05)
        wave = 0.5 + 0.5 * np.cos(th * n)
        if flutes:
            dome = dome - 0.07 * (1.0 - wave) * fade
        take = dome > h
        h = np.where(take, dome, h)
        ridge = np.where(take, wave * fade, ridge)
    return h, ridge


def build_ceiling(seed: int = 317) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("shrine_ceiling", seed)
    noise = kc.Noise3(rng)
    lay = ceiling_layout()
    cx, r_w = M["apse_cx_m"], M["wall_r_m"]
    t = M["ceiling_t_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("shrine_ceiling" + ("-lod1" if lod else ""))
        # The roof deck (the vault's outside, its rings and rosettes) is its own mesh, so the dressing
        # can keep it out of the interior's VoxelGI bake: sunlit voxels on top leaked through the vault.
        tb = kc.MeshBuilder("shrine_ceiling_top" + ("-lod1" if lod else ""))
        mor = mb.material(sc.M_MORTAR)
        stone = mb.material(sc.M_STONE)
        for surface, step in (("under", 1.2 if lod else 0.3), ("top", 1.2 if lod else 0.6)):
            sb = mb if surface == "under" else tb
            xs = np.arange(-(cx + r_w + 0.45), cx + r_w + 0.45 + 1e-6, step)
            zs = np.arange(-(r_w + 0.45), r_w + 0.45 + 1e-6, step)
            X, Z = np.meshgrid(xs, zs)
            # Snap vertices near an oculus onto its circle: the hole's edge is exact, not stair-stepped.
            # A cell is dropped when all four corners started inside a hole (snapped, they would span it).
            hole = np.zeros(X.shape, bool)
            for ox, oz in lay["holes"]:
                d = np.hypot(X - ox, Z - oz)
                inside = d < M["oculus_r_m"]
                hole |= inside
                k = inside & (d > 1e-6)
                X = np.where(k, ox + (X - ox) / np.maximum(d, 1e-6) * M["oculus_r_m"], X)
                Z = np.where(k, oz + (Z - oz) / np.maximum(d, 1e-6) * M["oculus_r_m"], Z)
            H, ridge = _vault_height(X, Z, lay, flutes=(surface == "under" and not lod))
            Y = H if surface == "under" else H + t
            grid = np.stack([X, Y, Z], axis=-1)
            keep_v = _plan_inside(X, Z, 0.45)
            breakup = noise.fbm(grid / 0.8, 2)
            col = sc.col4(0.0, 0.2 + 0.3 * (1.0 - ridge) * breakup, 0.0, 0.2 + 0.3 * breakup)
            uv2 = np.stack([0.7 + 0.3 * ridge, np.full(ridge.shape, 0.5)], axis=-1)
            rows, cols = X.shape
            start_v, start_t = sb.vertex_count, sb.triangle_count
            base = sb.add_vertices(grid.reshape(-1, 3), np.tile(kc.UP, (rows * cols, 1)), grid[..., [0, 2]].reshape(-1, 2),
                                   uv2.reshape(-1, 2), col.reshape(-1, 4))
            m = mor if surface == "under" else tb.material(sc.M_STONE)
            for r_ in range(rows - 1):
                for c_ in range(cols - 1):
                    corners = ((r_, c_), (r_, c_ + 1), (r_ + 1, c_), (r_ + 1, c_ + 1))
                    if not all(keep_v[q] for q in corners) or all(hole[q] for q in corners):
                        continue
                    a = base + r_ * cols + c_
                    b, cc, d = a + 1, a + cols + 1, a + cols
                    # Rows run +Z, columns +X: (b - a) x (d - a) = +X x +Z = -Y, i.e. facing down.
                    if surface == "under":
                        sb.add_tri(a, b, cc, m)
                        sb.add_tri(a, cc, d, m)
                    else:
                        sb.add_tri(a, cc, b, m)
                        sb.add_tri(a, d, cc, m)
            kc.recompute_normals(sb, start_v, start_t)
        # Oculus rings (stone tori, the light's edge) and their drums through the vault.
        for k, (ox, oz) in enumerate(lay["holes"]):
            yh = float(_vault_height(np.array([ox + M["oculus_r_m"]]), np.array([oz]), lay, flutes=False)[0][0])
            sides = 10 if lod else 40
            sc.lathe(mb, [(M["oculus_r_m"] - 0.02, yh + t + 0.02), (M["oculus_r_m"] - 0.02, yh - 0.02)], sides, stone,
                     center=(ox, 0.0, oz), flip=True, variation=0.6)
            ang = np.linspace(0, 2 * math.pi, sides + 1)
            ring = np.stack([ox + np.cos(ang) * M["oculus_r_m"], np.full_like(ang, yh - 0.03),
                             oz + np.sin(ang) * M["oculus_r_m"]], axis=-1)
            kc.tube(mb, ring, 0.09, 4 if lod else 8, stone, weather=sc.TENDED, variation=0.4)
            if k == M["roof_oculus"] and lay["well"] is not None:
                # The light well up to the roof's ring: a slanted drum, its inside facing the shaft.
                top, bot = lay["well"]
                _well(mb, bot + np.array([0.0, t * 0.5, 0.0]), top, M["roof_ring_r_m"] * M["roof_scale"] + 0.1,
                      M["oculus_r_m"] - 0.02, 8 if lod else 32, stone)
            else:
                kc.tube(tb, ring + np.array([0.0, t + 0.08, 0.0]), 0.14, 4 if lod else 8, tb.material(sc.M_STONE),
                        weather=sc.TENDED, variation=0.5)
                if not lod:
                    # Rosette of small fan-shells round the open oculi (the roof's language at small scale).
                    import shrine  # noqa: PLC0415

                    for i in range(8):
                        a = 2 * math.pi * (i + 0.5) / 8
                        hinge = np.array([ox + math.cos(a) * 1.05, 0.0, oz + math.sin(a) * 1.05])
                        hy = float(_vault_height(np.array([hinge[0]]), np.array([hinge[2]]), lay, flutes=False)[0][0])
                        hinge[1] = hy + t + 0.02
                        shrine.fan_shell(tb, hinge, (math.cos(a), 0.0, math.sin(a)), 0.95, rng, noise, span_deg=58.0,
                                         ribs=5, lift=0.18, droop_deg=17.0, weather=sc.TENDED)
        if not lod:
            # Coral ribs on the flute ridges, from each oculus down to the spring line.
            for k, (ox, oz) in enumerate((o[0], o[1]) for o in M["oculi"]):
                roofed = k == M["roof_oculus"]
                n = 24 if roofed else 14
                r_max = lay["r_roof"] if roofed else 3.4
                hx, hz = lay["holes"][k]
                r0 = math.hypot(hx - ox, hz - oz) + M["oculus_r_m"] + 0.12
                for i in range(n):
                    th = 2 * math.pi * i / n
                    rr = np.linspace(r0, r_max, 22)
                    px, pz = ox + np.cos(th) * rr, oz + np.sin(th) * rr
                    ok = _plan_inside(px, pz, -0.1)
                    hy, _ = _vault_height(px, pz, lay, flutes=True)
                    own = np.ones_like(px, bool)
                    for j, (qx, qz) in enumerate((o[0], o[1]) for o in M["oculi"]):
                        if j != k:
                            own &= np.hypot(px - qx, pz - qz) > np.hypot(px - ox, pz - oz)
                    m_ = ok & own & (hy > M["spring_y_m"] + 0.04)
                    if m_.sum() < 3:
                        continue
                    last = int(np.argmin(m_)) if not m_.all() else len(m_)
                    pts = np.stack([px, hy - 0.015, pz], axis=-1)[:last]
                    if len(pts) < 3:
                        continue
                    kc.tube(mb, pts, 0.045, 5, stone, weather=sc.TENDED, variation=float(rng.random()))
        out += [mb, tb]
    return out


TARGETS = {
    "floor_slab_1m": build_floor_slab,
    "wall_curve_r9": build_wall_curve,
    "wall_curve_entrance": build_wall_entrance,
    "wall_curve_door": build_wall_door,
    "wall_straight_2_5m": build_wall_straight,
    "wall_niche_conch": build_wall_niche,
    "column_whorl": build_column,
    "shrine_ceiling": build_ceiling,
}
