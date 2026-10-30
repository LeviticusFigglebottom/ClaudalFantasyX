"""Ch9's strand of the drowned, the pieces its greybox still stood in for (env-art-b, act1_ch09.md §2). Pure numpy.

  strand_landing  the timber landing out from the strand where the Ebbing goes out: 6 x 8 m of salvaged planks on
                  three pile bents, a low kerb rail on both sides and across the seaward end, a mooring post at
                  each seaward corner with its rope. Origin at the deck's centre on its top; +Z is the sea end.
  strand_rocks    the rocks Pell comes down at the strand's east end: an 8 x 7 m mound of dark boulders and fallen
                  laterite whose top is a flat-ish shelf 4 m up (the zone's Rocks block), and the path off its west
                  face, rough slabs laid down the slope from (-3.75, 4.0) to (-9.1, 0.6) at z +2.35 (the zone's
                  RocksDown ramp). Origin at the block's base centre (y 0, the harbour's foot under the shingle).
  mole_bridge     the gangway from the strand's east end to Ch8's mole: 11.9 m of planks across two stringers rising
                  0.6 m on four trestles, a hand-rail each side. Origin at its strand end on the deck, centred;
                  it runs along +X.

  shroud_bound_a, shroud_bound_b, shroud_bound_small
                  the drowned under sailcloth as the field camera sees them (the PC's pass 3, row 51: cw_night's
                  shrouds, blurred twice and fading at the hem, read from above as soft orange rectangles): the
                  same body forms (cw_night._form, read-only) blurred once and a little fuller, a firm hem where
                  the cloth meets the shingle, creases running the length, and four ties (neck, chest, knees,
                  ankles). Face covered, shape only. Origin on the ground at the body's centre; head at -Z.

Heights and plans are the zone's collision (tools/act1/ch09_corrow_night.py); the art sits on it.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
from cw_common import kc

BUDGET_KEY = {"shroud_bound_a": "shroud_bound", "shroud_bound_b": "shroud_bound", "shroud_bound_small": "shroud_bound"}
TRI_BUDGET = {
    "shroud_bound": (4000, 300),
    "strand_landing": (9000, 800),
    "strand_rocks": (12000, 900),
    "mole_bridge": (9000, 800),
}
SOAKED = kc.Weathering(moss=0.2, salt=0.65, wet=0.55, erosion=0.6, noise_scale_m=0.5)
ROCK_W = kc.Weathering(moss=0.0, salt=0.6, wet=0.25, erosion=0.9, noise_scale_m=0.8)  # M3-ENV-1322: less wet (they read
# as glossy black spheres on the GPU)

LANDING_W, LANDING_L = 6.0, 8.0
LANDING_FLOOR_Y = -1.6  # the piles' feet in the harbour mud (the harbour floor is 1.3 m under the deck)
KERB_H = 0.5  # the zone's LandingW/E/End rails: 0.5 m over the deck
ROCKS_HALF = (4.0, 3.5)  # the Rocks block's plan (x, z) and its top
ROCKS_TOP = 4.0
PATH_TOP = (-3.75, 4.0)  # (x, y) of the path's top, on the block's west face
PATH_FOOT = (-9.1, 0.6)  # its foot on the strand's shingle
PATH_Z = 2.35
PATH_W = 1.2
BRIDGE_L, BRIDGE_RISE, BRIDGE_W = 11.9, 0.6, 4.0
BRIDGE_FLOOR_Y = -1.3  # the harbour floor under the strand end's deck
RAIL_H = 1.0


def _deck_planks(mb, rng, noise, *, x0: float, x1: float, z0: float, z1: float, y, across_x: bool, lod: bool,
                 mat: int, width: float = 0.24) -> None:
    """Boards laid across x (each from x0 to x1) stepping along z, or the other way round; `y(t)` is the deck's
    height at a fraction t along the run. A few boards are new, a few missing (never two together)."""
    if lod:
        a, b = (np.array([x0, y(0.5), (z0 + z1) * 0.5]), np.array([x1, y(0.5), (z0 + z1) * 0.5]))
        if not across_x:
            a, b = (np.array([(x0 + x1) * 0.5, y(0.0), z0]), np.array([(x0 + x1) * 0.5, y(1.0), z1]))
        kc.plank(mb, a, b, (z1 - z0) if across_x else (x1 - x0), 0.06, mat)
        return
    run0, run1 = (z0, z1) if across_x else (x0, x1)
    n = int((run1 - run0) / (width + 0.015))
    missing = -2
    for k in range(n):
        t = (k + 0.5) / n
        c = run0 + (run1 - run0) * t
        if k - missing > 3 and 2 < k < n - 2 and rng.random() < 0.05:
            missing = k
            continue
        w = width * rng.uniform(0.9, 1.05)
        yy = y(t) + rng.normal(0.0, 0.006) - 0.03
        a, b = ((x0, yy, c), (x1, yy, c)) if across_x else ((c, yy, z0), (c, yy, z1))
        kc.plank(mb, a, b, w, 0.06, mat, weather=SOAKED, variation=float(rng.random()), noise=noise)


def _post(mb, at, top: float, r: float, mat: int, rng, *, foot: float, lod: bool) -> None:
    kc.tube(mb, np.array([[at[0], foot, at[1]], [at[0], top, at[1]]]), r, 4 if lod else 8, mat, weather=SOAKED,
            cap_end=True, variation=float(rng.random()))


def build_landing(seed: int = 921) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("strand_landing", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("strand_landing" + (cw.LOD if lod else ""))
        tm, rope, iron = mb.material(cw.M_TIMBER), mb.material(cw.M_ROPE), mb.material(cw.M_IRON)
        hw, hl = LANDING_W * 0.5, LANDING_L * 0.5
        _deck_planks(mb, rng, None if lod else noise, x0=-hw, x1=hw, z0=-hl, z1=hl, y=lambda t: 0.0, across_x=True,
                     lod=lod, mat=tm)
        # Three stringers under the boards, and three bents of piles down to the mud with a cap and a cross brace.
        for x in (-hw + 0.3, 0.0, hw - 0.3):
            kc.plank(mb, (x, -0.16, -hl), (x, -0.16, hl), 0.16, 0.2, tm, up=np.array([0.0, 1.0, 0.0]), weather=SOAKED)
        for z in (-hl + 0.4, 0.0, hl - 0.4):
            kc.plank(mb, (-hw, -0.36, z), (hw, -0.36, z), 0.22, 0.2, tm, up=np.array([0.0, 1.0, 0.0]), weather=SOAKED)
            for x in (-hw + 0.35, 0.0, hw - 0.35):
                _post(mb, (x + rng.normal(0, 0.03), z + rng.normal(0, 0.03)), -0.26, 0.13, tm, rng,
                      foot=LANDING_FLOOR_Y, lod=lod)
            if not lod:
                kc.plank(mb, (-hw + 0.35, -0.5, z + 0.16), (hw - 0.35, LANDING_FLOOR_Y + 0.4, z + 0.16), 0.14, 0.05,
                         tm, up=np.array([0.0, 0.0, 1.0]), weather=SOAKED, variation=float(rng.random()))
        # The kerb: posts every ~2 m and a capping rail at KERB_H along both sides and across the sea end.
        for sx in (-1.0, 1.0):
            x = sx * (hw - 0.1)
            for k in range(5):
                z = -hl + 0.15 + k * (LANDING_L - 0.3) / 4
                _post(mb, (x, z), KERB_H - 0.06, 0.07, tm, rng, foot=-0.06, lod=lod)
            kc.plank(mb, (x, KERB_H - 0.03, -hl + 0.05), (x, KERB_H - 0.03, hl - 0.05), 0.14, 0.06, tm, weather=SOAKED,
                     variation=float(rng.random()), noise=None if lod else noise)
        for k in range(4):
            _post(mb, (-hw + 0.1 + k * (LANDING_W - 0.2) / 3, hl - 0.1), KERB_H - 0.06, 0.07, tm, rng, foot=-0.06,
                  lod=lod)
        kc.plank(mb, (-hw + 0.05, KERB_H - 0.03, hl - 0.1), (hw - 0.05, KERB_H - 0.03, hl - 0.1), 0.14, 0.06, tm,
                 weather=SOAKED, variation=float(rng.random()), noise=None if lod else noise)
        # Mooring posts at the sea corners, taller than the kerb, a rope wrapped and hanging to the water.
        for sx in (-1.0, 1.0):
            at = (sx * (hw + 0.22), hl + 0.15)
            _post(mb, at, 1.1, 0.15, tm, rng, foot=LANDING_FLOOR_Y, lod=lod)
            if not lod:
                for k in range(3):
                    y = 0.75 + k * 0.07
                    a = np.linspace(0.0, 2 * math.pi, 13)
                    ring = np.stack([at[0] + np.cos(a) * 0.17, np.full_like(a, y), at[1] + np.sin(a) * 0.17], -1)
                    kc.tube(mb, ring, 0.025, 5, rope, weather=SOAKED)
                t = np.linspace(0.0, 1.0, 7)
                fall = np.stack([at[0] + sx * 0.15 + t * sx * 0.4, 0.75 - t * 1.25 + 0.25 * t * (1 - t),
                                 at[1] + 0.1 + t * 0.6], -1)
                kc.tube(mb, fall, 0.022, 5, rope, weather=SOAKED)
                kc.rounded_block(mb, (at[0], 0.95, at[1] - 0.16), (0.06, 0.02, 0.02), iron, radius=0.01, seg=1)
        out.append(mb)
    return out


def _mound_y(noise: kc.Noise3, X, Z):
    """The mound: a shelf at ROCKS_TOP over the block's plan (never above it), falling in a broken slope to the shingle
    at about 1.3 x the plan, with crags in the slope."""
    hx, hz = ROCKS_HALF
    d = ((np.abs(X) / hx) ** 4 + (np.abs(Z) / hz) ** 4) ** 0.25
    crag = (noise.fbm(np.stack([X / 1.6, np.full_like(X, 0.37), Z / 1.6], -1), 3) - 0.5)
    fall = kc.smoothstep(1.0, 1.32 + crag * 0.12, d)
    top = ROCKS_TOP - 0.04 - np.abs(crag) * 0.08
    return top * (1.0 - fall) - 0.35 * fall + crag * 0.5 * fall * (1.0 - fall) * 4.0


def build_rocks(seed: int = 922) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("strand_rocks", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("strand_rocks" + (cw.LOD if lod else ""))
        head, rub, lat, brk = (mb.material(cw.M_HEADLAND), mb.material(cw.M_RUBBLE), mb.material(cw.M_LATERITE),
                               mb.material(cw.M_BROKEN))
        hx, hz = ROCKS_HALF
        xs = np.linspace(-hx * 1.38, hx * 1.38, 9 if lod else 47)
        zs = np.linspace(-hz * 1.38, hz * 1.38, 8 if lod else 41)
        X, Z = np.meshgrid(xs, zs)
        Y = _mound_y(noise, X, Z)
        P = np.stack([X, Y, Z], -1)
        wet = np.clip(1.0 - kc.smoothstep(0.4, 1.6, Y), 0.0, 1.0)
        col = np.stack([np.zeros_like(Y), np.full_like(Y, 0.5), wet * 0.8, np.full_like(Y, 0.85)], -1)
        uv2 = np.stack([0.55 + 0.45 * kc.smoothstep(0.0, ROCKS_TOP, Y), np.full_like(Y, 0.4)], -1)
        cw.grid_surface(mb, P, head, outward=kc.UP, uv=np.stack([X * 0.5, Z * 0.5 + Y * 0.3], -1), col=col, uv2=uv2)
        brng = kc.rng_for("strand_rocks_boulders", seed)
        n_boulders = 6 if lod else 46
        for k in range(n_boulders):
            # Boulders on the slope and round the foot (none on the shelf, none on the path's line).
            a = brng.uniform(0.0, 2 * math.pi)
            r = brng.uniform(1.0, 1.35)
            x, z = math.cos(a) * hx * r, math.sin(a) * hz * r
            if abs(z - PATH_Z) < PATH_W and x < -hx * 0.9:
                continue
            y = float(_mound_y(noise, np.array(x), np.array(z)))
            size = brng.uniform(0.5, 1.5) * (1.2 if r > 1.2 else 0.9)
            laterite = brng.random() < 0.65  # M3-ENV-1322: mostly the wall's own fallen stone, not dark rubble
            half = np.array([size * brng.uniform(0.7, 1.2), size * brng.uniform(0.4, 0.7), size * brng.uniform(0.5, 0.9)])
            half *= 0.5
            rot = kc.rot_y(brng.uniform(0, math.pi)) @ kc.rot_x(brng.uniform(-0.5, 0.5)) @ kc.rot_z(brng.uniform(-0.4, 0.4))
            kc.rounded_block(mb, (x, y + half[1] * 0.3, z), half, lat if laterite else rub, rot=rot,
                             radius=size * (0.05 if laterite else 0.09), seg=1 if lod else 2, noise=None if lod else noise,
                             disp_m=size * 0.1, disp_period_m=size * 0.45, weather=ROCK_W,
                             variation=float(brng.random()), wet_bias=0.15 if y < 1.0 else 0.0)
            if laterite and not lod and brng.random() < 0.5:  # a fresh break on the wall's stones: the fall
                kc.rounded_block(mb, (x, y + half[1] * 0.75, z), half * np.array([0.7, 0.3, 0.7]), brk, rot=rot,
                                 radius=size * 0.05, seg=1, weather=ROCK_W, variation=float(brng.random()))
        # The path off the west face: rough slabs bedded on the slope's line, rubble kerbing either side.
        (x_top, y_top), (x_foot, y_foot) = PATH_TOP, PATH_FOOT
        run = math.hypot(x_top - x_foot, y_top - y_foot)
        tilt = math.atan2(y_top - y_foot, x_top - x_foot)
        n = 4 if lod else 13
        for k in range(n):
            t = (k + 0.5) / n
            cx, cy = x_foot + (x_top - x_foot) * t, y_foot + (y_top - y_foot) * t
            ln = run / n * (1.0 if lod else brng.uniform(0.92, 1.05))
            half = np.array([ln * 0.5, 0.09, PATH_W * 0.5 * (1.0 if lod else brng.uniform(0.85, 1.0))])
            rot = kc.rot_z(tilt) @ kc.rot_y(0.0 if lod else brng.normal(0.0, 0.05))
            kc.rounded_block(mb, (cx, cy - 0.09 * math.cos(tilt) - 0.01, PATH_Z), half, rub, rot=rot, radius=0.04,
                             seg=1, noise=None if lod else noise, disp_m=0.015, weather=ROCK_W,
                             variation=float(brng.random()))
            if not lod:
                for side in (-1.0, 1.0):
                    s = brng.uniform(0.25, 0.5)
                    kc.rounded_block(mb, (cx + brng.normal(0, 0.1), cy + s * 0.15,
                                          PATH_Z + side * (PATH_W * 0.5 + s * 0.6)),
                                     (s * 0.6, s * 0.4, s * 0.5), rub, rot=kc.rot_y(brng.uniform(0, math.pi)),
                                     radius=s * 0.2, seg=2, noise=noise, disp_m=s * 0.06, weather=ROCK_W,
                                     variation=float(brng.random()), wet_bias=0.2)
        # The shingle skirt the path comes down on: the mound's foot meets the strand's shingle at its height.
        if not lod:
            for k in range(10):
                x = x_foot + brng.uniform(-0.5, 2.5)
                z = PATH_Z + brng.uniform(-2.2, 2.2)
                if abs(z - PATH_Z) < PATH_W * 0.6:
                    continue
                s = brng.uniform(0.3, 0.7)
                kc.rounded_block(mb, (x, y_foot - 0.05 + s * 0.12, z), (s * 0.7, s * 0.3, s * 0.55), rub,
                                 rot=kc.rot_y(brng.uniform(0, math.pi)), radius=s * 0.2, seg=2, noise=noise,
                                 disp_m=s * 0.05, weather=ROCK_W, variation=float(brng.random()), wet_bias=0.4)
        out.append(mb)
    return out


def build_bridge(seed: int = 923) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("mole_bridge", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("mole_bridge" + (cw.LOD if lod else ""))
        tm, iron = mb.material(cw.M_TIMBER), mb.material(cw.M_IRON)
        hw = BRIDGE_W * 0.5

        def deck_y(x: float) -> float:
            return BRIDGE_RISE * x / BRIDGE_L

        _deck_planks(mb, rng, None if lod else noise, x0=0.0, x1=BRIDGE_L, z0=-hw, z1=hw, y=lambda t: BRIDGE_RISE * t,
                     across_x=False, lod=lod, mat=tm)
        for z in (-hw + 0.25, hw - 0.25):  # the stringers, following the rise
            kc.plank(mb, (0.0, -0.16, z), (BRIDGE_L, BRIDGE_RISE - 0.16, z), 0.18, 0.22, tm,
                     up=np.array([-BRIDGE_RISE, BRIDGE_L, 0.0]), weather=SOAKED, variation=float(rng.random()))
        for x in (0.6, 4.2, 7.8, 11.3):  # trestles: two raked legs, a cap and a cross brace
            y = deck_y(x)
            kc.plank(mb, (x, y - 0.38, -hw), (x, y - 0.38, hw), 0.2, 0.18, tm, weather=SOAKED)
            for sz in (-1.0, 1.0):
                top = np.array([x, y - 0.46, sz * (hw - 0.35)])
                foot = np.array([x, BRIDGE_FLOOR_Y, sz * (hw - 0.1)])
                kc.tube(mb, np.array([foot, top]), 0.11, 4 if lod else 7, tm, weather=SOAKED, cap_end=True,
                        variation=float(rng.random()))
            if not lod:
                kc.plank(mb, (x + 0.12, y - 0.6, -hw + 0.4), (x + 0.12, BRIDGE_FLOOR_Y + 0.5, hw - 0.4), 0.14, 0.05,
                         tm, up=np.array([1.0, 0.0, 0.0]), weather=SOAKED, variation=float(rng.random()))
        # Hand-rails: posts every ~2 m, a rail along the rise, iron straps at the posts' feet.
        n = 7
        for sz in (-1.0, 1.0):
            z = sz * (hw - 0.08)
            for k in range(n):
                x = 0.1 + k * (BRIDGE_L - 0.2) / (n - 1)
                _post(mb, (x, z), deck_y(x) + RAIL_H, 0.06, tm, rng, foot=deck_y(x) - 0.25, lod=lod)
                if not lod:
                    kc.rounded_block(mb, (x, deck_y(x) - 0.12, z - sz * 0.07), (0.07, 0.08, 0.01), iron,
                                     radius=0.005, seg=1)
            kc.plank(mb, (0.0, RAIL_H, z), (BRIDGE_L, BRIDGE_RISE + RAIL_H, z), 0.1, 0.07, tm, weather=SOAKED,
                     variation=float(rng.random()), noise=None if lod else noise)
            if not lod:
                kc.plank(mb, (0.0, RAIL_H * 0.5, z), (BRIDGE_L, BRIDGE_RISE + RAIL_H * 0.5, z), 0.08, 0.05, tm,
                         weather=SOAKED, variation=float(rng.random()))
        out.append(mb)
    return out


def build_shroud_bound(name: str, seed: int, *, length: float = 1.8, turn: float = 0.0, arm: float = 0.0) -> list:
    import cw_night  # noqa: PLC0415  (the body forms, read-only)

    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        nx, nz = (15, 29) if not lod else (5, 7)
        half_w, half_l = 0.42 * length / 1.8 + 0.08, length * 0.5 + 0.1
        X, Z = np.meshgrid(np.linspace(-half_w, half_w, nx), np.linspace(-half_l, half_l, nz))
        body = cw_night._form(X, Z, length, turn, arm) * SHROUD_FULL
        k = np.array([0.25, 0.5, 0.25])
        soft = np.apply_along_axis(lambda r: np.convolve(np.pad(r, 1, mode="edge"), k, "valid"), 1, body)
        soft = np.apply_along_axis(lambda c: np.convolve(np.pad(c, 1, mode="edge"), k, "valid"), 0, soft)
        y = np.maximum(soft, body * 0.96) + 0.015
        if not lod:  # creases along the length, deeper where the cloth stands off the body
            crease = np.sin(X / half_w * math.pi * 3.0 + rng.uniform(0, 6.28)) * 0.5 + 0.5
            p = np.stack([X, np.zeros_like(X), Z], axis=-1)
            y += (crease - 0.5) * SHROUD_CREASE_M * kc.smoothstep(0.03, 0.12, y)
            y += (noise.fbm(p / 0.15, 2) - 0.5) * SHROUD_NOISE_M
        # The outline follows the body (a superellipse, tapering to the head and feet), not the grid's rectangle: from
        # the field camera above, a straight-edged hem read as a flat rectangle (the PC's pass 4, row 51).
        rr = ((np.abs(X) / half_w) ** SHROUD_OUTLINE_P + (np.abs(Z) / half_l) ** SHROUD_OUTLINE_P) ** (1.0 / SHROUD_OUTLINE_P)
        edge = np.clip(1.0 - rr, 0.0, 1.0)
        y = y * kc.smoothstep(0.0, SHROUD_HEM, edge) + 0.008
        P = np.stack([X, y, Z], axis=-1)
        uv = np.stack([X * 1.5, Z * 1.5], axis=-1)
        kc.quad_strip(mb, P, mb.material(M_SHROUD), uv=uv, col=np.array([0.0, 0.25, 0.25, 0.3]),
                      uv2=np.array([0.85, float(rng.random())]), flip=True)
        if not lod:
            for zf in SHROUD_TIES:
                z = -length * 0.5 + zf * length
                row = int(round((z + half_l) / (2 * half_l) * (nz - 1)))
                xs = np.linspace(-half_w * 0.85, half_w * 0.85, 11)
                ys = np.interp(xs, X[row], y[row]) + 0.012
                kc.tube(mb, np.stack([xs, ys, np.full_like(xs, z)], axis=-1), 0.014, 4, mb.material(cw.M_ROPE),
                        variation=float(rng.random()))
        out.append(mb)
    return out


M_SHROUD = "cw_sail"  # cw_night's shroud slot (the zones swap it for their own sailcloth)
SHROUD_FULL = 1.4  # the body forms fuller, so the cloth reads as a body under it from the field camera above
SHROUD_CREASE_M = 0.01  # shallow: over the fuller form deeper creases read as spiky ridges
SHROUD_HEM = 0.14  # the cloth rolls down to the shingle over this fraction of the half-size (cw_night: 0.12)
SHROUD_OUTLINE_P = 2.6  # the outline's superellipse exponent: rounded at the shoulders, tapering at head and feet
SHROUD_TIES = (0.13, 0.36, 0.66, 0.9)  # neck, chest, knees, ankles
SHROUD_NOISE_M = 0.006


TARGETS = {
    "shroud_bound_a": lambda: build_shroud_bound("shroud_bound_a", 931),
    "shroud_bound_b": lambda: build_shroud_bound("shroud_bound_b", 932, turn=0.6, arm=0.12),
    "shroud_bound_small": lambda: build_shroud_bound("shroud_bound_small", 933, length=1.05),
    "strand_landing": build_landing,
    "strand_rocks": build_rocks,
    "mole_bridge": build_bridge,
}
