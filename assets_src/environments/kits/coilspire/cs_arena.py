"""The headland path's battle landing (M3-ENV-713, act1_ch08.md B04: the path's random fights and its forced fight
at the mid-point). Pure numpy; see cs_common.py.

The path climbs 0.17-0.3 m per metre all the way from the wall-gate to the forecourt, and is 2.2 m wide: no place
for a fight. These two pieces are the arena's own copy of the headland (headland frame, as `coilspire_ground` and
`headland_path`), with the path's profile levelled for LAND_HALF_S either side of its mid-point and a flagged
landing there, LAND_RX x LAND_RZ, wide enough for the battle's six slots and their clear floor. The arena places
them instead of the kit's ground and path (assets_src/environments/kits/haluna/arena_scenes.py).

  arena_headland_ground  the headland's rock and turf (coilspire_ground's grid and rules) graded to the levelled
                         path and to the landing, which lies LAND_BED_DY under its flags
  arena_tier_hall        (arena frame) a tier of the spire's well for the trial's placed fights (B05, `flue_moth`),
                         opened toward the battle camera: see build_tier_hall
  arena_headland_path    the path's treads and kerbs on the levelled profile, none on the landing; the landing's
                         flags (tops at the landing height) and a kerb round its rim where the path does not cross

`landing()` gives the landing's centre (headland frame), its height and the path's tangent there.
"""

from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

import cs_common as cs
import cs_headland as ch
from cs_common import kc

TRI_BUDGET = {"arena_headland_ground": (20000, 2000), "arena_headland_path": (20000, 900),
              "arena_tier_hall": (36000, 2500)}

LAND_S = 51.0  # the path's mid-point (arc length, of 99 m)
LAND_HALF_S = 7.0  # the profile is level this far either side
LAND_RAMP_S = 9.0  # and blends back to the kit's profile over this
LAND_RX, LAND_RZ = 7.6, 5.4  # the landing's half-axes: along the path, across it
LAND_BED_DY = -0.04  # the graded ground under the flags (a joint drops a ray only this far)
FLAG_DEPTH = 0.3
KERB_GAP = 1.9  # the path's own width, left open in the rim's kerb where it enters and leaves


def _levelled_path() -> cs.PathLine:
    base = cs.PATH
    y_land = float(np.interp(LAND_S, base.s, base.y))
    w = 1.0 - kc.smoothstep(LAND_HALF_S, LAND_HALF_S + LAND_RAMP_S, np.abs(base.s - LAND_S))
    return replace(base, y=base.y * (1.0 - w) + y_land * w)


LEVELLED = _levelled_path()


def landing() -> tuple[np.ndarray, float, np.ndarray]:
    """(centre xz, height, unit tangent xz) of the landing, headland frame."""
    return LEVELLED.at(LAND_S)


def _landing_r(X, Z):
    """Elliptical radius about the landing (1 at its rim): u along the path's tangent, v across."""
    p, _y, t = landing()
    dx, dz = np.asarray(X, float) - p[0], np.asarray(Z, float) - p[1]
    u = dx * t[0] + dz * t[1]
    v = -dx * t[1] + dz * t[0]
    return np.hypot(u / LAND_RX, v / LAND_RZ), u, v


class _Levelled:
    """cs_common's PATH (read by ground_height, path_distance and the tread layout) swapped for the levelled one
    while the arena pieces are built."""

    def __enter__(self):
        self._old = cs.PATH
        cs.PATH = LEVELLED

    def __exit__(self, *exc):
        cs.PATH = self._old


_KIT_GROUND = cs.ground_height  # the kit's grading (it reads cs.PATH, levelled while the arena pieces build)


def _height(X, Z, noise_h):
    h = _KIT_GROUND(X, Z, noise_h)
    r, _u, _v = _landing_r(X, Z)
    w = 1.0 - kc.smoothstep(1.0, 1.35, r)
    return h * (1.0 - w) + (landing()[1] + LAND_BED_DY) * w


# M3-ENV-1316: the kit's fine grid stops 8.5 m north of the landing (z -50); the hill the arena's cameras see rises
# beyond it on 8-9 m cells (broad facets, and scrub set on the ground's true height floated over them). The arena's
# ground carries the fine grid on north to ARENA_FINE_Z's start, a little coarser there to stay in budget.
ARENA_FINE_Z = (-120.0, 6.0, 1.75)


def build_ground(name: str = "arena_headland_ground", seed: int = 1101) -> list[kc.MeshBuilder]:
    old = cs.ground_height
    old_fine = ch.FINE_Z
    noise_h = cs.headland_noise()
    with _Levelled():
        cs.ground_height = lambda X, Z, noise=None: _height(X, Z, noise_h)
        ch.FINE_Z = ARENA_FINE_Z
        try:
            out = ch.build_ground(name, seed)
        finally:
            cs.ground_height = old
            ch.FINE_Z = old_fine
    return out


def _drop_inside(mb: kc.MeshBuilder, r_max: float) -> None:
    """Drops the triangles whose centroid lies inside the landing (the path's treads and kerbs across it)."""
    P = np.asarray(mb.pos)
    T = np.asarray(mb.tris)
    cen = P[T].mean(axis=1)
    r, _u, _v = _landing_r(cen[:, 0], cen[:, 2])
    keep = r > r_max
    mb.tris = [tuple(t) for t in T[keep].tolist()]
    mb.tri_mat = [m for m, k in zip(mb.tri_mat, keep) if k]


def _flags(mb: kc.MeshBuilder, rng, noise, lod: bool) -> None:
    p, y, t = landing()
    i_st = mb.material(cs.M_CARVED)
    yaw = math.atan2(-t[1], t[0])
    side = np.array([-t[1], t[0]])
    if lod:
        n = 24
        a = np.linspace(0.0, 2 * math.pi, n + 1)
        ring = np.stack([np.cos(a) * LAND_RX, np.sin(a) * LAND_RZ], -1)
        g = np.array([[[p[0], y, p[1]] for _ in ring],
                      [[p[0] + u * t[0] + v * side[0], y, p[1] + u * t[1] + v * side[1]] for u, v in ring]])
        cs.surface(mb, g, i_st, outward=np.array([0.0, 1.0, 0.0]), uv=np.stack([g[..., 0], g[..., 2]], -1),
                   col=np.broadcast_to(np.array([0.0, 0.1, 0.0, 0.6]), g.shape[:2] + (4,)),
                   uv2=np.broadcast_to(np.array([0.9, 0.5]), g.shape[:2] + (2,)))
        return
    wear = kc.Weathering(moss=0.35, salt=0.25, wet=0.05, erosion=0.75)
    # Courses across the path, each a run of flags of random length, the joints staggered course to course.
    v = -LAND_RZ
    while v < LAND_RZ:
        w = rng.uniform(0.6, 0.95)
        vc = v + 0.5 * w
        half_u = LAND_RX * math.sqrt(max(0.0, 1.0 - (vc / LAND_RZ) ** 2))
        u = -half_u + rng.uniform(0.0, 0.4)
        while u < half_u - 0.25:
            ln = min(rng.uniform(0.7, 1.4), half_u - u)
            uc = u + 0.5 * ln
            cxz = p + t * uc + side * vc
            c = np.array([cxz[0], y - FLAG_DEPTH * 0.5 + rng.uniform(-0.01, 0.01), cxz[1]])
            kc.rounded_block(mb, c, (0.5 * ln - 0.015, FLAG_DEPTH * 0.5, 0.5 * w - 0.015), i_st,
                             rot=kc.rot_y(yaw + rng.uniform(-0.02, 0.02)), radius=0.012, seg=1, noise=noise,
                             disp_m=0.006, disp_period_m=0.35, weather=wear, variation=float(rng.random()))
            u += ln
        v += w
    # A kerb of set stones round the rim, open where the path enters and leaves.
    a = 0.0
    while a < 2 * math.pi:
        uu, vv = math.cos(a) * (LAND_RX + 0.25), math.sin(a) * (LAND_RZ + 0.25)
        if abs(vv) > KERB_GAP * 0.5 + 0.2 or rng.random() < 0.0:
            cxz = p + t * uu + side * vv
            h = rng.uniform(0.08, 0.22)
            c = np.array([cxz[0], y + h - 0.25, cxz[1]])
            tang = math.atan2(-(t[1] * -math.sin(a) * LAND_RX + side[1] * math.cos(a) * LAND_RZ),
                              t[0] * -math.sin(a) * LAND_RX + side[0] * math.cos(a) * LAND_RZ)
            kc.rounded_block(mb, c, (rng.uniform(0.25, 0.42), 0.25, rng.uniform(0.13, 0.2)), i_st,
                             rot=kc.rot_y(tang + rng.uniform(-0.1, 0.1)), radius=0.05, seg=1, noise=noise,
                             disp_m=0.02, disp_period_m=0.3,
                             weather=kc.Weathering(moss=0.5, salt=0.3, wet=0.05, erosion=0.8),
                             variation=float(rng.random()))
        a += rng.uniform(0.85, 1.0) / math.hypot(LAND_RX, LAND_RZ) * 1.414


def build_path(name: str = "arena_headland_path", seed: int = 1111) -> list[kc.MeshBuilder]:
    with _Levelled():
        builders = ch.build_path(name, seed)
    for lod, mb in zip((False, True), builders):
        rng = kc.rng_for(name + "_landing", seed)
        noise = kc.Noise3(rng)
        _drop_inside(mb, 1.02)
        _flags(mb, rng, noise, lod)
    return builders


# ---------------------------------------------------------------------------------------------
# The tier hall (arena frame: the floor at y 0 about the origin, bearings clockwise from -Z, the camera at +Z)
# ---------------------------------------------------------------------------------------------
# The spire's well is 7-9 m across and the battle camera stands 8 m off the slots, so no true tier fits a fight. The
# arena's hall is the trial's tier as a stage set: the well widened to HALL_R and the near arc (the camera's side) left
# open, the far HALL_SPAN either side of the back standing, with the tier's landing above on its corbels, the next
# landing higher, the flights hugging the wall between them, the copper risers from the keys, slits to the sky, and the
# sooted shaft rising to daylight.
HALL_R = 7.0  # the inner face's radius
HALL_T = 1.1  # the wall's thickness (seen only in the slits' reveals and the cut ends)
HALL_H = 13.5
HALL_SPAN = 140.0  # deg either side of the back (bearing 0): the cut ends stand outside the battle frame
HALL_ROW_M = 0.25  # wall grid rows; a course joint every second row
HALL_COL_M = 0.3
SOOT_Y = (5.5, 11.0)  # the inner face darkens over this
# (bearing, y0, y1, half-width m): the slits through the wall.
HALL_SLITS = ((-75.0, 5.6, 8.0, 0.22), (-25.0, 1.6, 3.8, 0.22), (30.0, 1.8, 4.0, 0.22), (100.0, 6.6, 8.8, 0.22))
LEDGE_1 = (4.8, -100.0, 30.0)  # the tier's landing: top y, bearing from, to
LEDGE_2 = (9.6, -20.0, 110.0)  # the next tier's
LEDGE_W = 1.65
FLIGHT_1 = (95.0, 42.0, 0.0, 4.8)  # bearing from, to; y from, to: the floor up to the landing
FLIGHT_2 = (-98.0, -22.0, 4.8, 9.6)
FLIGHT_W = 1.3
HALL_RING_M = 0.9  # the floor's courses of flags round the well's grate
HALL_GRATE_R = 0.9
HALL_KEYS = ((-40.0, 1.25), (10.0, 1.25), (-70.0, LEDGE_1[0] + 1.25))  # flue-keys: bearing, axle height
HALL_BRAZIERS = ((-10.0, 6.0, 0.0), (25.0, 6.0, 0.0), (-60.0, 6.1, LEDGE_1[0]))  # bearing, radius, floor y


def _bdir(b_deg: float) -> np.ndarray:
    b = math.radians(b_deg)
    return np.array([math.sin(b), 0.0, -math.cos(b)])


def _a(b_deg: float) -> float:
    """Bearing -> the kit's spire angle convention (cs_common.basis_at: (cos a, sin a))."""
    return b_deg - 90.0


def _wall(mb, rng, noise, lod: bool) -> None:
    i_in, i_soot, i_lat = mb.material(cs.M_INNER), mb.material(cs.M_SOOT), mb.material(cs.M_LATERITE)
    i_dark = mb.material(cs.M_DARK)
    nb = max(8, int(2 * math.radians(HALL_SPAN) * HALL_R / (HALL_COL_M if not lod else 2.0)))
    ny = int(HALL_H / (HALL_ROW_M if not lod else 2.25)) + 1
    bs = np.linspace(-HALL_SPAN, HALL_SPAN, nb + 1)
    ys = np.linspace(0.0, HALL_H, ny)
    B, Y = np.meshgrid(np.radians(bs), ys)
    R = np.full_like(B, HALL_R)
    if not lod:
        course = (np.round(Y / HALL_ROW_M).astype(int) % 2 == 0) & (Y > 0.01) & (Y < HALL_H - 0.01)
        R = R + 0.03 * course + (noise.fbm(np.stack([np.sin(B) * 3.0, Y / 2.0, np.cos(B) * 3.0], -1), 2) - 0.5) * 0.04
    P = np.stack([R * np.sin(B), Y, -R * np.cos(B)], -1)
    soot = kc.smoothstep(SOOT_Y[0], SOOT_Y[1], Y)
    col = np.stack([np.zeros_like(Y), np.full_like(Y, 0.1), np.zeros_like(Y), 0.4 + 0.2 * soot], -1)
    uv = np.stack([B * HALL_R / 2.0, Y / 2.0], -1)
    uv2 = np.stack([np.clip(0.7 + 0.3 * kc.smoothstep(0.0, 1.0, Y), 0, 1), np.full_like(Y, 0.5)], -1)
    cb, cy = 0.5 * (B[:-1, :-1] + B[1:, 1:]), 0.5 * (Y[:-1, :-1] + Y[1:, 1:])
    keep = np.ones(cb.shape, bool)
    for b, y0, y1, hw in HALL_SLITS:
        da = hw / HALL_R
        keep &= ~((np.abs(cb - math.radians(b)) < da) & (cy > y0) & (cy < y1))
    mats = np.where(kc.smoothstep(SOOT_Y[0], SOOT_Y[1], cy) + (noise.fbm(np.stack([np.sin(cb) * 2.0, cy / 3.0,
                                                                               np.cos(cb) * 2.0], -1), 2) - 0.5) * 0.6
                    > 0.5, i_soot, i_in) if not lod else i_in
    cs.surface(mb, P, mats, outward=np.stack([-np.sin(B), np.zeros_like(B), np.cos(B)], -1), uv=uv, col=col, uv2=uv2,
               keep=keep)
    # The slits' reveals (through the wall), a dark sill inside, and the cut ends and the top rim of the wall.
    ro = HALL_R + HALL_T
    for b, y0, y1, hw in HALL_SLITS:
        d, t = _bdir(b), np.array([math.cos(math.radians(b)), 0.0, math.sin(math.radians(b))])
        c0, c1 = d * HALL_R, d * ro
        for sgn in (-1.0, 1.0):
            e0, e1 = c0 + t * sgn * hw, c1 + t * sgn * hw * 1.6
            g = np.array([[e0 + [0, y0, 0], e1 + [0, y0, 0]], [e0 + [0, y1, 0], e1 + [0, y1, 0]]])
            cs.surface(mb, g, i_lat, outward=-t * sgn, uv=g[..., [0, 1]], col=np.full((2, 2, 4), 0.3),
                       uv2=np.full((2, 2, 2), 0.6))
        for yy, up in ((y0, 1.0), (y1, -1.0)):
            g = np.array([[c0 - t * hw + [0, yy, 0], c1 - t * hw * 1.6 + [0, yy, 0]],
                          [c0 + t * hw + [0, yy, 0], c1 + t * hw * 1.6 + [0, yy, 0]]])
            cs.surface(mb, g, i_lat, outward=np.array([0.0, up, 0.0]), uv=g[..., [0, 2]], col=np.full((2, 2, 4), 0.3),
                       uv2=np.full((2, 2, 2), 0.6))
    for b in (-HALL_SPAN, HALL_SPAN):
        d = _bdir(b)
        g = np.array([[d * HALL_R, d * ro], [d * HALL_R + [0, HALL_H, 0], d * ro + [0, HALL_H, 0]]])
        side = np.array([math.cos(math.radians(b)), 0.0, math.sin(math.radians(b))]) * np.sign(b)
        cs.surface(mb, g, i_lat, outward=side, uv=g[..., [0, 1]], col=np.full((2, 2, 4), 0.4), uv2=np.full((2, 2, 2), 0.7))
    bt = np.radians(np.linspace(-HALL_SPAN, HALL_SPAN, 48 if not lod else 12))
    g = np.stack([np.stack([HALL_R * np.sin(bt), np.full_like(bt, HALL_H), -HALL_R * np.cos(bt)], -1),
                  np.stack([ro * np.sin(bt), np.full_like(bt, HALL_H), -ro * np.cos(bt)], -1)])
    cs.surface(mb, g, i_dark if lod else i_soot, outward=np.array([0.0, 1.0, 0.0]), uv=g[..., [0, 2]],
               col=np.full(g.shape[:2] + (4,), 0.4), uv2=np.full(g.shape[:2] + (2,), 0.6))


def _floor(mb, rng, noise, lod: bool) -> None:
    i_pave, i_ir = mb.material(cs.M_PAVING), mb.material(cs.M_IRON)
    # The bed under the flags (a joint drops a ray only LAND_BED_DY) and the well's iron grate at the centre.
    ang = np.radians(np.linspace(0.0, 360.0, 49))
    ring = np.stack([np.sin(ang), np.zeros_like(ang), -np.cos(ang)], -1)
    g = np.stack([ring * HALL_GRATE_R, ring * (HALL_R + 0.3)]) + [0.0, LAND_BED_DY, 0.0]
    cs.surface(mb, g, i_pave, outward=np.array([0.0, 1.0, 0.0]), uv=g[..., [0, 2]], col=np.full(g.shape[:2] + (4,), 0.2),
               uv2=np.full(g.shape[:2] + (2,), 0.6))
    g = np.stack([ring * 0.0, ring * HALL_GRATE_R]) + [0.0, -0.006, 0.0]
    cs.surface(mb, g, i_ir, outward=np.array([0.0, 1.0, 0.0]), uv=g[..., [0, 2]], col=np.full(g.shape[:2] + (4,), 0.3),
               uv2=np.full(g.shape[:2] + (2,), 0.5))
    if lod:
        return
    wear = kc.Weathering(moss=0.0, salt=0.05, wet=0.0, erosion=0.7)
    r0 = HALL_GRATE_R + 0.05
    k = 0
    while r0 < HALL_R - 0.1:
        r1 = min(r0 + HALL_RING_M, HALL_R + 0.1)
        rm = 0.5 * (r0 + r1)
        n = max(6, int(2 * math.pi * rm / rng.uniform(0.9, 1.2)))
        off = rng.uniform(0.0, 360.0 / n)
        for j in range(n):
            b0 = off + j * 360.0 / n
            b1 = b0 + 360.0 / n
            # A flag as the annular sector's chord block, a little short so the joints show.
            bm = 0.5 * (b0 + b1)
            arc = math.radians(b1 - b0) * rm
            c = _bdir(bm) * rm + [0.0, -0.15 + rng.uniform(-0.008, 0.008), 0.0]
            kc.rounded_block(mb, c, (0.5 * arc - 0.02, 0.15, 0.5 * (r1 - r0) - 0.02), i_pave,
                             rot=cs.basis_at(_a(bm)), radius=0.015, seg=1, noise=noise, disp_m=0.005, disp_period_m=0.3,
                             weather=wear, variation=float(rng.random()))
        r0 = r1
        k += 1
    # The grate's bars over the well (flush with the floor).
    for x in np.linspace(-0.7, 0.7, 8):
        h = math.sqrt(max(0.0, HALL_GRATE_R ** 2 - x * x)) - 0.04
        kc.rounded_block(mb, (x, -0.035, 0.0), (0.03, 0.03, h), i_ir, radius=0.01, seg=1, weather=cs.IRON_W)


def _ledges_and_flights(mb, rng, noise, lod: bool) -> None:
    i_pave, i_car = mb.material(cs.M_PAVING), mb.material(cs.M_CARVED)
    for y, b0, b1 in (LEDGE_1, LEDGE_2):
        n = max(4, int((b1 - b0) / (6.0 if not lod else 20.0)))
        from cs_tiers import _sector_tiles  # noqa: PLC0415

        _sector_tiles(mb, y, 0.45, HALL_R - LEDGE_W, HALL_R + 0.05, _a(b0), _a(b1), i_pave, n=n,
                      col=(0.0, 0.05, 0.05, 0.5), uv2=(0.8, float(rng.random())))
        if lod:
            continue
        for b in np.linspace(b0 + 4.0, b1 - 4.0, max(3, int((b1 - b0) / 22.0))):
            c = _bdir(b) * (HALL_R - 0.35) + [0.0, y - 0.45 - 0.38, 0.0]
            kc.rounded_block(mb, c, (0.22, 0.38, 0.4), i_car, rot=cs.basis_at(_a(b)), radius=0.04, seg=1,
                             weather=cs.INNER_W, variation=float(rng.random()))
        # The well edge's worn kerb.
        for b in np.arange(b0 + 1.5, b1 - 1.0, 3.0):
            c = _bdir(b + 1.5) * (HALL_R - LEDGE_W + 0.14) + [0.0, y + 0.06, 0.0]
            arc = math.radians(3.0) * (HALL_R - LEDGE_W)
            kc.rounded_block(mb, c, (0.5 * arc - 0.03, 0.07, 0.14), i_car, rot=cs.basis_at(_a(b + 1.5)), radius=0.03,
                             seg=1, noise=noise, disp_m=0.008, weather=cs.INNER_W, variation=float(rng.random()))
    for b0, b1, y0, y1 in (FLIGHT_1, FLIGHT_2):
        n = int(round((y1 - y0) / cs.RISE_M))
        for i in range(n):
            b = b0 + (b1 - b0) * (i + 0.5) / n
            top = y0 + (i + 1) * (y1 - y0) / n
            going = abs(math.radians(b1 - b0)) * (HALL_R - 0.5 * FLIGHT_W) / n
            c = _bdir(b) * (HALL_R - 0.5 * FLIGHT_W + 0.05) + [0.0, top - 0.11, 0.0]
            kc.rounded_block(mb, c, (0.5 * going * 1.08, 0.11, 0.5 * FLIGHT_W + 0.08), i_car, rot=cs.basis_at(_a(b)),
                             radius=0.03, seg=1, noise=None if lod else noise, disp_m=0.012, disp_period_m=0.3,
                             weather=cs.INNER_W, variation=float(rng.random()))
            rise = top - 0.22 - y0
            if rise > 0.05:  # the flight's solid stone body under the tread, down to its own floor or landing
                c2 = _bdir(b) * (HALL_R - 0.5 * FLIGHT_W + 0.05) + [0.0, y0 + 0.5 * rise, 0.0]
                kc.rounded_block(mb, c2, (0.5 * going * 1.08, 0.5 * rise, 0.5 * FLIGHT_W + 0.04), i_car,
                                 rot=cs.basis_at(_a(b)), radius=0.02, seg=1, weather=cs.INNER_W,
                                 variation=float(rng.random()))


def _hall_risers(mb, lod: bool) -> None:
    from cs_tiers import _pipe  # noqa: PLC0415

    i_cu = mb.material(cs.M_COPPER)
    for b, y in HALL_KEYS:
        d = _bdir(b)
        ys = np.linspace(y + 0.3, HALL_H - 0.4, 2 if lod else 8)
        _pipe(mb, [d * (HALL_R - 0.12) + [0.0, yy, 0.0] for yy in ys], i_cu, 0.075, lod=lod)
    for b, rad, fy in HALL_BRAZIERS:
        d = _bdir(b)
        top = fy + 2.0
        _pipe(mb, [d * (HALL_R + 0.05) + [0, top, 0], d * (HALL_R - 0.4) + [0, top + 0.05, 0],
                   d * (rad + 0.25) + [0, top - 0.05, 0], d * (rad + 0.05) + [0, top - 0.35, 0], d * rad + [0, fy + 1.15, 0]],
              i_cu, 0.08, lod=lod)


def build_tier_hall(name: str = "arena_tier_hall", seed: int = 1131) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        _floor(mb, rng, noise, lod)
        _wall(mb, rng, noise, lod)
        _ledges_and_flights(mb, rng, noise, lod)
        _hall_risers(mb, lod)
        out.append(mb)
    return out


def hall_fittings() -> tuple[list[tuple[str, tuple[float, float, float], float]], list[tuple[float, float, float]]]:
    """The tier hall's kit fittings in the arena frame, (piece, at, yaw deg), and the braziers' fire points: the
    keys (flue_key on the wall, its wheel KEY_STUB out, both facing the well) and the braziers."""
    import cs_tiers  # noqa: PLC0415

    rows, fires = [], []
    for b, y in HALL_KEYS:
        d = _bdir(b)
        yaw = -b  # Basis(UP, yaw) sends the piece's +Z (out of the wall) to (sin yaw, 0, cos yaw): toward the well
        rows.append(("flue_key", tuple(float(v) for v in d * HALL_R + [0.0, y, 0.0]), yaw))
        rows.append(("flue_key_wheel", tuple(float(v) for v in d * (HALL_R - cs_tiers.KEY_STUB) + [0.0, y, 0.0]), yaw))
    for k, (b, rad, fy) in enumerate(HALL_BRAZIERS):
        p = _bdir(b) * rad + [0.0, fy, 0.0]
        rows.append(("tier_brazier", tuple(float(v) for v in p), 37.0 * k))
        fires.append(tuple(float(v) for v in p + [0.0, 1.3, 0.0]))
    return [(n, tuple(round(v, 3) for v in at), yaw) for n, at, yaw in rows], fires


TARGETS = {"arena_headland_ground": build_ground, "arena_headland_path": build_path,
           "arena_tier_hall": build_tier_hall}
