"""The Coilspire itself (coilspire.md §0, §2). Pure numpy; see cs_common.py. All in the spire frame.

  coilspire_shell  the hollow stone body on the far piece's radius law (-4 .. +46 m): the outer face in
                   0.5 m courses (grooved joints to +8 m), the inner face, the top rim, the plinth; openings
                   with stone reveals (the door under its carved breaking-wave lintel, the hearth arch, the
                   slits along the flights, the crown opening, the gallery door); the beacon gallery on its
                   corbels with an iron rail. The crown above the gallery and the inner face high up are
                   smoke-darkened.
  coilspire_flues  the three copper flues on the far law (1.25 turns each from +3 to +42 m, 0.25 m proud),
                   collars and wall straps every 3 m, stone boots at the two roots on the plinth (the third
                   rises out of the keeper's hut's roof), their heads turning into the wall at +42 m, under the gallery.
  beacon_basket    origin at the top centre (+46 m): the far piece's iron cage (eight bars from r 1.5 m
                   rising 3.2 m and leaning out to the ring at r 1.8 m) and the basket with its fire.
"""

from __future__ import annotations

import math

import numpy as np

import cs_common as cs
from cs_common import kc

TRI_BUDGET = {"coilspire_shell": (40000, 2000), "coilspire_flues": (14000, 900), "beacon_basket": (5000, 400)}

SEAM_A = cs.HEARTH_A  # the faces' u seam: the keeper's hut and the lee
GROOVE_TOP = 8.0  # course grooves in the geometry up to here (the texture carries them above)
LINTEL = (3.0, 3.75, 1.3, 0.12)  # door lintel: y0, y1, half-width, proud of the face
DOOR = (cs.DOOR_A, 0.85, 0.0, 3.0)
HEARTH = (cs.HEARTH_A, 0.9, 0.0, 1.5)
GALLERY_DOOR_HALF, GALLERY_DOOR_H = 0.45, 2.0
GALLERY_OUT = 1.15  # the balcony's reach beyond the face
GALLERY_CORBELS = 12
SOOT_Y = (cs.GALLERY_Y + 0.4, 27.0)  # outside, inside: smoke-darkened above (ragged)


def openings() -> list[tuple[float, float, float, float]]:
    """(angle deg, half-width m, y0, y1) of every opening through the wall."""
    out = [DOOR, HEARTH]
    out += [(a, cs.SLIT[0], sill, sill + cs.SLIT[1]) for a, sill in cs.slit_list()]
    out.append(cs.CROWN_OPEN)
    out.append((cs.gallery_door_a(), GALLERY_DOOR_HALF, cs.GALLERY_Y, cs.GALLERY_Y + GALLERY_DOOR_H))
    return out


def _wrap(a: float) -> float:
    """Angle (deg) into [SEAM_A, SEAM_A + 360)."""
    return SEAM_A + (a - SEAM_A) % 360.0


def _edges(ops, radius_fn) -> list[tuple[float, float, float, float]]:
    """Each opening's (a_lo, a_hi, y0, y1) in the seam's range, its jambs parallel (constant width)."""
    out = []
    for a, hw, y0, y1 in ops:
        r = float(radius_fn(0.5 * (y0 + y1)))
        d = math.degrees(hw / r)
        c = _wrap(a)
        out.append((c - d, c + d, y0, y1))
    return out


def _columns(base_n: int, edges) -> np.ndarray:
    cols = list(SEAM_A + np.linspace(0.0, 360.0, base_n + 1))
    fixed = []
    for lo, hi, _y0, _y1 in edges:
        fixed += [lo, hi]
    keep = [c for c in cols if all(abs(c - f) > 0.6 for f in fixed)] + [SEAM_A, SEAM_A + 360.0]
    return np.unique(np.round(np.asarray(keep + fixed), 6))


def _course_offsets(rng) -> np.ndarray:
    return rng.uniform(-1.0, 1.0, 200)


def outer_face_r(y, offsets) -> np.ndarray:
    """The outer face's radius at y: the far law, a per-course set and (low down) the grooved joints."""
    y = np.asarray(y, float)
    d = cs.cw.course_profile(np.maximum(y, -2.0), offsets, base_y=-2.0)
    groove_w = 1.0 - kc.smoothstep(GROOVE_TOP - 0.5, GROOVE_TOP, y)
    k = np.floor((np.maximum(y, -2.0) + 2.0) / cs.cw.COURSE_M).astype(int)
    setback = 0.012 * offsets[np.clip(k, 0, len(offsets) - 1)]
    return cs.outer_r(y) + d * groove_w + setback * (1.0 - groove_w)


def _cell_keep(cols: np.ndarray, ys: np.ndarray, edges) -> np.ndarray:
    am = 0.5 * (cols[1:] + cols[:-1])
    ym = 0.5 * (ys[1:] + ys[:-1])
    keep = np.ones((len(ys) - 1, len(cols) - 1), bool)
    for lo, hi, y0, y1 in edges:
        inside = (ym[:, None] > y0) & (ym[:, None] < y1) & (am[None, :] > lo) & (am[None, :] < hi)
        keep &= ~inside
    return keep


def _stone_colours(P: np.ndarray, A: np.ndarray, noise: kc.Noise3, w: kc.Weathering, *, sea_side: float = 1.0):
    """VC for the spire's stone: a little lichen on the lee (world north is spire angle ~240 deg), a salt
    film heavier toward the sea (local +Z, 90 deg), erosion higher on the windward side, damp at the foot."""
    br = noise.fbm(P / w.noise_scale_m, 2)
    lee = 0.5 + 0.5 * np.cos(A - math.radians(240.0))
    sea = 0.5 + 0.5 * np.cos(A - math.radians(90.0)) * sea_side
    moss = np.clip(w.moss * lee * (0.3 + 1.2 * br) * (1.0 - kc.smoothstep(6.0, 20.0, P[..., 1])), 0, 1)
    salt = np.clip(w.salt * (0.4 + 0.8 * sea) * (0.5 + br), 0, 1)
    wet = np.clip(w.wet + 0.35 * (1.0 - kc.smoothstep(-0.2, 0.8, P[..., 1])), 0, 1)
    ero = np.clip(w.erosion * (0.6 + 0.5 * sea) * (0.6 + 0.8 * br), 0, 1)
    return np.stack([moss, salt, wet, ero], -1)


def coil_stain(A: np.ndarray, Y: np.ndarray, noise: kc.Noise3) -> np.ndarray:
    """VC.G on the inner face: copper salts bloomed through the wall along each flue's path behind it (a band
    about 1 m wide either side of the coil's line), heaviest at the keys' heights, broken up by noise."""
    r = cs.inner_r(Y)
    stain = np.zeros_like(A)
    for k in range(3):
        a_k = cs.coil_angle(k, np.clip(Y, cs.COIL_Y[0] - 3.0, cs.COIL_Y[1]))
        d = (np.mod(A - a_k + math.pi, 2.0 * math.pi) - math.pi) * r
        stain = np.maximum(stain, np.exp(-(d / 1.1) ** 2))
    br = noise.fbm(np.stack([np.cos(A) * 4.0, Y / 2.5, np.sin(A) * 4.0], -1), 3)
    return np.clip(0.08 + 0.92 * stain * (0.55 + 0.9 * br), 0.0, 1.0)


def _rows_outer(edges) -> np.ndarray:
    ys = [cs.FOOTING_Y, -1.5, -0.6, -0.2]
    ys += list(cs.cw.course_rows(0.0, GROOVE_TOP, base_y=-2.0))
    ys += list(np.arange(GROOVE_TOP + 1.0, cs.SPIRE_H, 1.0))
    ys += [cs.SPIRE_H, cs.GALLERY_Y - 0.3, cs.GALLERY_Y, LINTEL[0], LINTEL[1]]
    for _lo, _hi, y0, y1 in edges:
        ys += [y0, y1]
    return np.unique(np.round(np.clip(ys, cs.FOOTING_Y, cs.SPIRE_H), 5))


def _rows_inner(edges) -> np.ndarray:
    ys = list(np.arange(0.0, cs.SPIRE_H, 1.0)) + [cs.SPIRE_H] + list(cs.TIER_Y) + [cs.CROWN_Y, cs.GRATE_Y]
    for _lo, _hi, y0, y1 in edges:
        ys += [y0, y1]
    return np.unique(np.round(np.clip(ys, -0.1, cs.SPIRE_H), 5))


def _face(mb, cols, ys, rfn, mats, noise, rng, *, inward: bool, edges, w: kc.Weathering) -> None:
    A = np.radians(cols)[None, :].repeat(len(ys), 0)
    Y = ys[:, None].repeat(len(cols), 1)
    R = rfn(Y)
    P = np.stack([R * np.cos(A), Y, R * np.sin(A)], -1)
    radial = np.stack([np.cos(A), np.zeros_like(A), np.sin(A)], -1)
    # u: arc length on the face (m), so the coursed blocks keep their size up the taper; v: height.
    uv = np.stack([(A - math.radians(SEAM_A)) * cs.outer_r(Y), Y], -1)
    col = _stone_colours(P, A, noise, w)
    if inward:
        col[..., 1] = coil_stain(A, Y, noise)
    course = np.floor((Y + 2.0) / 0.5).astype(int)
    var = rng.random(400)[np.clip(course, 0, 399)]
    if inward:
        ao = np.clip(0.55 + 0.45 * kc.smoothstep(0.0, 3.0, (Y - cs.TIER_Y[0])), 0.4, 1.0)
    else:
        ao = np.clip(0.75 + 0.25 * kc.smoothstep(-0.4, 1.5, Y), 0.5, 1.0)
    uv2 = np.stack([ao, var], -1)
    cs.surface(mb, P, mats, outward=-radial if inward else radial, uv=uv, col=col, uv2=uv2,
               keep=_cell_keep(cols, ys, edges))


def _soot_cells(cols, ys, noise: kc.Noise3, y_from: float, ragged: float) -> np.ndarray:
    am = np.radians(0.5 * (cols[1:] + cols[:-1]))
    ym = 0.5 * (ys[1:] + ys[:-1])
    Am, Ym = np.meshgrid(am, ym)
    n = noise.fbm(np.stack([np.cos(Am) * 3.0, Ym / 4.0, np.sin(Am) * 3.0], -1), 3)
    return Ym > y_from + (n - 0.5) * 2.0 * ragged


def _jambs(mb, eo, ei, rout, rin, mat, offsets) -> None:
    """Stone reveals joining the outer edge (eo) and inner edge (ei) of each opening."""
    col = np.array([0.0, 0.2, 0.0, 0.7])
    for (lo, hi, y0, y1), (ilo, ihi, _a, _b) in zip(eo, ei):
        ny = max(2, int(math.ceil((y1 - y0) / 0.5)) + 1)
        ys = np.linspace(y0, y1, ny)
        for ao, ai, toward in ((lo, ilo, 1.0), (hi, ihi, -1.0)):
            a_o, a_i = math.radians(ao), math.radians(ai)
            po = np.stack([rout(ys) * math.cos(a_o), ys, rout(ys) * math.sin(a_o)], -1)
            pi = np.stack([rin(ys) * math.cos(a_i), ys, rin(ys) * math.sin(a_i)], -1)
            g = np.stack([po, pi], 1)
            t = np.array([-math.sin(a_o), 0.0, math.cos(a_o)]) * toward
            depth = np.linalg.norm(po - pi, axis=-1)
            uv = np.stack([np.stack([np.zeros(ny), depth], 1), np.stack([ys, ys], 1)], -1)
            cs.surface(mb, g, mat, outward=t, uv=uv, col=np.broadcast_to(col, g.shape[:2] + (4,)),
                       uv2=np.broadcast_to(np.array([0.7, 0.4]), g.shape[:2] + (2,)))
        na = max(2, int(math.ceil((hi - lo) / 4.0)) + 1)
        for y, up in ((y0, 1.0), (y1, -1.0)):
            ao = np.radians(np.linspace(lo, hi, na))
            ai = np.radians(np.linspace(ilo, ihi, na))
            po = np.stack([rout(y) * np.cos(ao), np.full(na, y), rout(y) * np.sin(ao)], -1)
            pi = np.stack([rin(y) * np.cos(ai), np.full(na, y), rin(y) * np.sin(ai)], -1)
            g = np.stack([po, pi], 0)
            uv = np.stack([g[..., 0], g[..., 2]], -1)
            cs.surface(mb, g, mat, outward=np.array([0.0, up, 0.0]), uv=uv,
                       col=np.broadcast_to(col, g.shape[:2] + (4,)),
                       uv2=np.broadcast_to(np.array([0.75 if up > 0 else 0.5, 0.4]), g.shape[:2] + (2,)))
    del offsets


def wave_relief(u: np.ndarray, v: np.ndarray, height: float, waves: float = 6.0) -> np.ndarray:
    """The lintel's carving (m, proud): a row of breaking waves, each a long rise to a rounded crest that curls
    forward and drops, the Watchers' crown motif (corrow.md) laid along a lintel."""
    half = 0.5 * float(np.max(np.abs(u))) if np.size(u) else 1.0
    ph = (u / (2.0 * max(half, 1e-6)) + 0.5) * waves
    f = ph - np.floor(ph)
    rise = np.sin(0.5 * np.pi * np.clip(f / 0.72, 0.0, 1.0)) ** 1.5
    drop = np.cos(0.5 * np.pi * np.clip((f - 0.72) / 0.28, 0.0, 1.0)) ** 0.7
    crest = np.where(f < 0.72, rise, drop)
    top = (0.42 + 0.36 * crest) * height
    band = kc.smoothstep(0.1 * height, 0.16 * height, v) * (1.0 - kc.smoothstep(top - 0.02, top + 0.006, v))
    curl = np.exp(-((v - (top - 0.05)) / 0.018) ** 2) * kc.smoothstep(0.08, 0.3, f) * band
    rim = np.exp(-((v - 0.88 * height) / 0.02) ** 2) * 0.012
    return band * 0.045 - curl * 0.014 + rim


def _lintel(mb, offsets, mat) -> None:
    y0, y1, hw, proud = LINTEL
    a_c = math.radians(cs.DOOR_A)
    nu, nv = 53, 17
    u = np.linspace(-hw, hw, nu)
    v = np.linspace(0.0, y1 - y0, nv)
    U, V = np.meshgrid(u, v)
    Y = y0 + V
    R0 = outer_face_r(Y, offsets)
    A = a_c - U / R0  # +u toward decreasing a (cs.basis_at's x)
    relief = wave_relief(U, V, y1 - y0)
    edge = kc.smoothstep(hw - 0.02, hw, np.abs(U)) + kc.smoothstep(0.02, 0.0, V) + kc.smoothstep(y1 - y0 - 0.02,
                                                                                                    y1 - y0, V)
    R = R0 + (proud + relief) * (1.0 - np.clip(edge, 0, 1))
    P = np.stack([R * np.cos(A), Y, R * np.sin(A)], -1)
    radial = np.stack([np.cos(A), np.zeros_like(A), np.sin(A)], -1)
    wear = np.clip(0.4 + relief * 8.0, 0, 1)
    col = np.stack([np.zeros_like(U), np.full_like(U, 0.25), np.zeros_like(U), wear], -1)
    uv2 = np.stack([np.clip(0.8 + relief * 4.0, 0.4, 1.0), np.full_like(U, 0.62)], -1)
    cs.surface(mb, P, mat, outward=radial, uv=np.stack([U, V], -1), col=col, uv2=uv2)


def _gallery(mb, i_st, i_ir, rng) -> None:
    y = cs.GALLERY_Y
    r0 = float(cs.outer_r(y)) - 0.12
    r1 = float(cs.outer_r(y)) + GALLERY_OUT
    cs.annulus(mb, y, 0.28, r0, r1, 40, i_st, col=(0.0, 0.3, 0.05, 0.6), uv2=(0.85, 0.3), skirt_inner=False)
    for k in range(GALLERY_CORBELS):
        # Twelve corbels at 15 + 30 k deg: the flues' heads (at 90, 210 and 330 deg, just under the gallery)
        # fall in the gaps.
        a = math.radians(15.0 + 360.0 / GALLERY_CORBELS * k)
        rot = cs.basis_at(math.degrees(a))
        c = np.array([math.cos(a), 0.0, math.sin(a)]) * (r0 + 0.55) + np.array([0.0, y - 0.28 - 0.42, 0.0])
        kc.rounded_block(mb, c, (0.2, 0.42, 0.62), i_st, rot=rot, radius=0.05, seg=2,
                         weather=cs.STONE_W, variation=float(rng.random()))
    rr = r1 - 0.09
    posts = 24
    for k in range(posts):
        a = 2.0 * math.pi * k / posts
        p = np.array([rr * math.cos(a), y, rr * math.sin(a)])
        kc.tube(mb, np.array([p, p + [0.0, 1.05, 0.0]]), 0.025, 5, i_ir, weather=cs.IRON_W)
    ang = np.linspace(0.0, 2.0 * math.pi, 73)
    for h, rad in ((1.05, 0.03), (0.55, 0.018)):
        ring = np.stack([rr * np.cos(ang), np.full_like(ang, y + h), rr * np.sin(ang)], -1)
        kc.tube(mb, ring, rad, 5, i_ir, weather=cs.IRON_W)


def build_shell(name: str = "coilspire_shell", seed: int = 1001) -> list[kc.MeshBuilder]:
    out = []
    ops = openings()
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        offsets = _course_offsets(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_lat, i_in, i_soot, i_car = (mb.material(cs.M_LATERITE), mb.material(cs.M_INNER), mb.material(cs.M_SOOT),
                                      mb.material(cs.M_CARVED))
        i_ir, i_dk = mb.material(cs.M_IRON), mb.material(cs.M_DARK)
        if lod:
            ys = np.concatenate([[cs.FOOTING_Y], np.linspace(0.0, cs.SPIRE_H, 12)])
            cols = SEAM_A + np.linspace(0.0, 360.0, 19)
            mats = np.where(_soot_cells(cols, ys, noise, SOOT_Y[0], 1.0), i_soot, i_lat)
            _face(mb, cols, ys, cs.outer_r, mats, noise, rng, inward=False, edges=[], w=cs.STONE_W)
            cs.annulus(mb, cs.SPIRE_H, 0.3, float(cs.inner_r(cs.SPIRE_H)), float(cs.outer_r(cs.SPIRE_H)), 12, i_soot)
            cs.annulus(mb, 0.0, 1.5, float(cs.outer_r(0.0)) - 0.2, 6.2, 18, i_car, skirt_inner=False)
            cs.annulus(mb, cs.GALLERY_Y, 0.28, float(cs.outer_r(cs.GALLERY_Y)) - 0.1,
                       float(cs.outer_r(cs.GALLERY_Y)) + GALLERY_OUT, 12, i_car, skirt_inner=False)
            # The openings as dark insets (the door and the crown opening read at 100 m).
            for a, hw, y0, y1 in (DOOR, cs.CROWN_OPEN):
                rot = cs.basis_at(a)
                r = float(cs.outer_r(0.5 * (y0 + y1))) + 0.03
                c = np.array([math.cos(math.radians(a)), 0.0, math.sin(math.radians(a))]) * r
                p = [c + rot @ np.array([sx * hw, y, 0.0]) for sx, y in ((1, y0), (-1, y0), (-1, y1), (1, y1))]
                cs.quad(mb, np.asarray(p), i_dk, col=(0, 0, 0, 0.5), uv2=(0.5, 0.5))
            out.append(mb)
            continue
        eo = _edges(ops, cs.outer_r)
        ei = _edges(ops, cs.inner_r)

        def rout(y):
            return outer_face_r(y, offsets)

        cols_o = _columns(72, eo)
        ys_o = _rows_outer(eo)
        mats_o = np.where(_soot_cells(cols_o, ys_o, noise, SOOT_Y[0], 1.2), i_soot, i_lat)
        _face(mb, cols_o, ys_o, rout, mats_o, noise, rng, inward=False, edges=eo, w=cs.STONE_W)
        cols_i = _columns(48, ei)
        ys_i = _rows_inner(ei)
        mats_i = np.where(_soot_cells(cols_i, ys_i, noise, SOOT_Y[1], 4.0), i_soot, i_in)
        _face(mb, cols_i, ys_i, cs.inner_r, mats_i, noise, rng, inward=True, edges=ei, w=cs.INNER_W)
        _jambs(mb, eo, ei, rout, cs.inner_r, i_car, offsets)
        # The top rim, the plinth (one step up from the forecourt to the threshold), the lintel, the gallery.
        cs.annulus(mb, cs.SPIRE_H, 0.3, float(cs.inner_r(cs.SPIRE_H)), float(cs.outer_r(cs.SPIRE_H)), 36, i_soot,
                   col=(0.0, 0.1, 0.0, 0.8))
        cs.annulus(mb, 0.0, 1.5, float(cs.outer_r(0.0)) - 0.2, 6.2, 72, i_car, col=(0.1, 0.25, 0.1, 0.75),
                   uv2=(0.85, 0.45), skirt_inner=False)
        _lintel(mb, offsets, i_car)
        _gallery(mb, i_car, i_ir, rng)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The flues
# ---------------------------------------------------------------------------------------------
BOOT = (0.55, 1.2, 0.5)  # half radial, height, half along: the stone boots at the two plinth roots


def coil_polyline(k: int, samples: int) -> np.ndarray:
    """Flue k's centre line: down from its first turn into its root (a boot on the plinth, or for k 2 the hut's
    roof), the far law from +3 to +42 m, and its head turning into the wall under the gallery."""
    ys = np.linspace(cs.COIL_Y[0], cs.COIL_Y[1], samples)
    body = cs.coil_point(k, ys)
    p0 = body[0]
    root_y = BOOT[1] - 0.2 if k < 2 else 2.4
    drop = [p0 + np.array([0.0, dy, 0.0]) for dy in np.linspace(root_y - p0[1], -0.35, 4)]
    a = float(cs.coil_angle(k, cs.COIL_Y[1]))
    radial = np.array([math.cos(a), 0.0, math.sin(a)])
    top = body[-1]
    # The head turns into the wall just under the gallery's slab.
    head = [top + radial * (-0.18) + np.array([0.0, -0.04, 0.0]), top + radial * (-0.45) + np.array([0.0, -0.1, 0.0]),
            top + radial * (-0.75) + np.array([0.0, -0.12, 0.0])]
    return np.vstack([np.asarray(drop), body, np.asarray(head)])


def _collar(mb, p, t, mat, r, length) -> None:
    kc.tube(mb, np.array([p - t * length * 0.5, p + t * length * 0.5]), r, 10, mat, weather=cs.COPPER_W,
            cap_start=True, cap_end=True, variation=0.3)


def build_flues(name: str = "coilspire_flues", seed: int = 1011) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_cu, i_ir, i_st = mb.material(cs.M_COPPER), mb.material(cs.M_IRON), mb.material(cs.M_CARVED)
        for k in range(3):
            pts = coil_polyline(k, 22 if lod else 130)
            v0 = mb.vertex_count
            kc.tube(mb, pts, cs.COIL_R, 5 if lod else 12, i_cu, weather=cs.COPPER_W,
                    noise=None if lod else noise, disp_m=0.01, disp_period_m=0.5, variation=0.25 + 0.2 * k)
            cs.patina(mb, v0, rng)
            if lod:
                continue
            # Collars and straps every 3 m of height; a collar where the root drops and where the head turns.
            for y in list(np.arange(4.5, cs.COIL_Y[1], 3.0)) + [cs.COIL_Y[0], cs.COIL_Y[1]]:
                p = cs.coil_point(k, y)
                p2 = cs.coil_point(k, y + 0.05)
                t = kc.normalize(p2 - p)
                _collar(mb, p, t, i_cu, cs.COIL_R + 0.05, 0.16)
                a = float(cs.coil_angle(k, y))
                radial = np.array([math.cos(a), 0.0, math.sin(a)])
                wall = radial * float(cs.outer_r(y))
                mid = 0.5 * (wall + np.array([p[0], 0.0, p[2]])) + np.array([0.0, y, 0.0])
                kc.rounded_block(mb, mid, (0.05, 0.05, 0.5 * cs.COIL_PROUD + 0.12), i_ir, rot=cs.basis_at(math.degrees(a)),
                                 radius=0.015, seg=1, weather=cs.IRON_W, variation=float(rng.random()))
            if k < 2:
                a = math.radians(k * 120.0)
                rot = cs.basis_at(k * 120.0)
                c = np.array([math.cos(a), 0.0, math.sin(a)]) * (float(cs.outer_r(0.0)) + 0.35)
                kc.rounded_block(mb, c + [0.0, BOOT[1] * 0.5, 0.0], (BOOT[2], BOOT[1] * 0.5, BOOT[0]), i_st, rot=rot,
                                 radius=0.08, seg=2, noise=noise, disp_m=0.02, disp_period_m=0.4, weather=cs.STONE_W,
                                 variation=float(rng.random()))
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The beacon
# ---------------------------------------------------------------------------------------------
def build_beacon(name: str = "beacon_basket", seed: int = 1021) -> list[kc.MeshBuilder]:
    out = []
    cage = cs.CAGE
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_ir, i_fire, i_em = mb.material(cs.M_IRON), mb.material(cs.M_BEACON), mb.material(cs.M_EMBER)
        sides = 4 if lod else 6
        for k in range(cage["bars"]):
            a = k * 2.0 * math.pi / cage["bars"]
            c, s = math.cos(a), math.sin(a)
            p0 = np.array([c * cage["r0"], 0.0, s * cage["r0"]])
            p1 = p0 + np.array([c * cage["lean"], cage["rise"], s * cage["lean"]])
            kc.tube(mb, np.array([p0, p1]), 0.08, sides, i_ir, weather=cs.IRON_W)
        ang = np.linspace(0.0, 2.0 * math.pi, 17 if lod else 41)
        for y, r, rad in ((cage["rise"], cage["ring_r"], 0.09), (0.08, cage["r0"], 0.07)):
            ring = np.stack([r * np.cos(ang), np.full_like(ang, y), r * np.sin(ang)], -1)
            kc.tube(mb, ring, rad, sides, i_ir, weather=cs.IRON_W)
        # The basket: a deep iron bowl on four legs, filled with coals; the fire core inside it (the far
        # piece's fire blocks, so the silhouette matches at 480 m).
        prof_r = np.array([0.35, 0.8, 1.05, 1.12])
        prof_y = np.array([0.25, 0.45, 0.95, 1.35])
        cs.lathe_ring(mb, prof_r, prof_y, 10 if lod else 24, i_ir, col=(0.0, 0.1, 0.1, 0.4))
        if not lod:
            v0, t0 = mb.vertex_count, mb.triangle_count
            cs.lathe_ring(mb, prof_r * 0.94, prof_y + 0.02, 24, i_ir, col=(0.0, 0.05, 0.0, 0.2))
            cs.flip_section(mb, v0, t0)
            for k in range(4):
                a = math.pi * 0.25 + k * math.pi * 0.5
                d = np.array([math.cos(a), 0.0, math.sin(a)])
                kc.tube(mb, np.array([d * 1.08 + [0, 1.3, 0], d * 1.4 + [0, 0.02, 0]]), 0.05, 5, i_ir, weather=cs.IRON_W)
        for k in range(1 if lod else 4):
            off = np.array([rng.uniform(-0.5, 0.5), 0.9 + k * 0.45, rng.uniform(-0.5, 0.5)]) if k else np.array([0, 1.0, 0])
            kc.rounded_block(mb, off, np.array([1.1, 0.9, 1.1]) * (1.0 - 0.2 * k), i_fire, radius=0.5 * (1.0 - 0.2 * k),
                             seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.12, disp_period_m=0.6,
                             variation=0.5)
        if not lod:
            for _k in range(10):
                a = rng.uniform(0.0, 2.0 * math.pi)
                r = rng.uniform(0.3, 0.85)
                c = np.array([r * math.cos(a), 1.25 + rng.uniform(-0.05, 0.08), r * math.sin(a)])
                kc.rounded_block(mb, c, rng.uniform(0.12, 0.22, 3) * [1.0, 0.6, 1.0], i_em, radius=0.06, seg=1,
                                 rot=kc.rot_y(rng.uniform(0, math.pi)), variation=float(rng.random()))
        out.append(mb)
    return out


TARGETS = {"coilspire_shell": build_shell, "coilspire_flues": build_flues, "beacon_basket": build_beacon}
