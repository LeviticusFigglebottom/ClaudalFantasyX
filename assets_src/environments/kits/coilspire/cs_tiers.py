"""The Coilspire's interior and its fittings (coilspire.md §0, §2). Pure numpy; see cs_common.py.

  coilspire_tiers  (spire frame) the base hall's paved floor and dais; the D-shaped landings of tiers 2-4 on
                   their corbels, with a worn kerb on the well edge; the crown floor (a central grate over the
                   well, a notch where flight 4 comes up); the five flights of cantilevered treads
                   (cs_common.plan); the copper risers on the inner wall (from each key up the wall, and a feed
                   from the wall to each landing's brazier); the tier-2 side flue and its sealed lamp-niche;
                   the beacon grate at +45.6 m with the coals glowing through it.
  flue_key         a key's housing: a copper collar on a stub out of the wall and the damper drum, origin on
                   the wall's face, +Z into the room (place it with cs_common.basis_at(angle)).
  flue_key_wheel   the hand-wheel (0.9 m, six spokes, the rim rubbed bright), origin on its axle, +Z its axis:
                   m2-slice turns this node about its local Z.
  tier_brazier     a wrought-iron tripod (0.9 m) holding a copper bowl with a bed of embers; origin on the floor.
"""

from __future__ import annotations

import math

import numpy as np

import cs_common as cs
from cs_common import kc

TRI_BUDGET = {"coilspire_tiers": (30000, 1600), "flue_key": (2500, 200), "flue_key_wheel": (2500, 160),
              "tier_brazier": (3000, 200)}

KEY_STUB = 0.62  # the wheel's plane, out from the wall's face (the wheel goes here, its axis along the wall's normal)
WHEEL_R = 0.45
NICHE = (0.55, 1.1, 0.4)  # the lamp-niche press: half along, height, depth


def _d_outline(y: float, centre: float, half: float, n: int = 40) -> np.ndarray:
    """A landing's x-z outline: the arc on the wall (embedded 5 cm) and the chord across the well."""
    r = float(cs.inner_r(y)) + 0.05
    a = np.radians(np.linspace(centre - half, centre + half, n))
    return np.stack([r * np.cos(a), r * np.sin(a)], -1)


def _sector_tiles(mb, y_top, thick, r0, r1, a0, a1, mat, *, n: int, col, uv2) -> None:
    """An annular sector slab as small convex prisms."""
    a = np.radians(np.linspace(a0, a1, n + 1))
    for k in range(n):
        q = np.array([[r0 * math.cos(a[k]), r0 * math.sin(a[k])], [r1 * math.cos(a[k]), r1 * math.sin(a[k])],
                      [r1 * math.cos(a[k + 1]), r1 * math.sin(a[k + 1])], [r0 * math.cos(a[k + 1]), r0 * math.sin(a[k + 1])]])
        cs.prism(mb, q, y_top - thick, y_top, mat, col=col, uv2=uv2)


def _tread(mb, f: cs.Flight, i: int, mat, rng, noise, *, lod: bool) -> None:
    a, top = f.tread(i)
    r_in = float(cs.inner_r(top))
    r_mid = r_in - 0.5 * f.width + 0.07
    going = abs(math.radians(f.step)) * r_in
    rot = cs.basis_at(a)
    c = np.array([math.cos(math.radians(a)), 0.0, math.sin(math.radians(a))]) * r_mid + np.array([0.0, top - 0.11, 0.0])
    kc.rounded_block(mb, c, (0.5 * going * 1.08, 0.11, 0.5 * f.width + 0.1), mat, rot=rot, radius=0.03,
                     seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.012, disp_period_m=0.3,
                     weather=cs.INNER_W, variation=float(rng.random()))


def _landing(mb, ln: cs.Landing, i_pave, i_car, rng, noise, *, lod: bool) -> None:
    outline = _d_outline(ln.y, ln.centre, ln.half, 24 if lod else 48)
    cs.prism(mb, outline, ln.y - cs.LANDING_T, ln.y, i_pave, col=(0.0, 0.05, 0.05, 0.5), uv2=(0.8, float(rng.random())))
    if lod:
        return
    # A worn kerb along the well edge (the chord) and corbels under the landing at the wall.
    p0, p1 = outline[0], outline[-1]
    d = p1 - p0
    ln_m = float(np.linalg.norm(d))
    t = d / ln_m
    inward = np.array([-t[1], t[0]])
    centre_dir = np.array([math.cos(math.radians(ln.centre)), math.sin(math.radians(ln.centre))])
    if np.dot(inward, centre_dir) < 0:
        inward = -inward
    yaw = math.atan2(-t[1], t[0])
    mid = 0.5 * (p0 + p1) + inward * 0.16
    kc.rounded_block(mb, (mid[0], ln.y + 0.06, mid[1]), (0.5 * ln_m - 0.1, 0.07, 0.16), i_car, rot=kc.rot_y(yaw),
                     radius=0.03, seg=2, noise=noise, disp_m=0.01, disp_period_m=0.3, weather=cs.INNER_W,
                     variation=float(rng.random()))
    n_corb = max(3, int(round(2.0 * ln.half / 30.0)))
    for k in range(n_corb):
        a = ln.centre - ln.half + (k + 0.5) * 2.0 * ln.half / n_corb
        r = float(cs.inner_r(ln.y - 0.9))
        c = np.array([math.cos(math.radians(a)), 0.0, math.sin(math.radians(a))]) * (r - 0.35)
        kc.rounded_block(mb, c + [0.0, ln.y - cs.LANDING_T - 0.38, 0.0], (0.22, 0.38, 0.4), i_car,
                         rot=cs.basis_at(a), radius=0.04, seg=1, weather=cs.INNER_W, variation=float(rng.random()))


def _pipe(mb, pts, mat, r=0.07, *, lod=False) -> None:
    v0 = mb.vertex_count
    kc.tube(mb, np.asarray(pts, float), r, 4 if lod else 8, mat, weather=cs.COPPER_W, variation=0.4)
    cs.patina(mb, v0, kc.rng_for("cs_pipe", int(v0)))


def _risers(mb, i_cu, *, lod: bool) -> None:
    """Copper on the inner wall: from each key up the wall to the tier above (or the crown floor), and from
    the wall over each landing's brazier, an elbow down into its bowl."""
    keys = cs.key_list()
    tops = {1: cs.TIER_Y[1] - cs.LANDING_T, 2: cs.TIER_Y[2] - cs.LANDING_T, 3: cs.TIER_Y[3] - cs.LANDING_T,
            4: cs.CROWN_Y - cs.LANDING_T}
    for tier, a, y, _kind in keys:
        d = np.array([math.cos(math.radians(a)), 0.0, math.sin(math.radians(a))])
        r0 = float(cs.inner_r(y + 0.35))
        ys = np.linspace(y + 0.3, tops[tier], 2 if lod else 6)
        pts = [d * (float(cs.inner_r(yy)) - 0.12) + np.array([0.0, yy, 0.0]) for yy in ys]
        _pipe(mb, pts, i_cu, 0.075, lod=lod)
        del r0
    for tier, a, rad, fy in cs.brazier_list()[1:]:
        d = np.array([math.cos(math.radians(a)), 0.0, math.sin(math.radians(a))])
        rw = float(cs.inner_r(fy + 2.0))
        top = fy + 2.0
        pts = [d * (rw + 0.05) + [0, top, 0], d * (rw - 0.4) + [0, top + 0.05, 0], d * (rad + 0.25) + [0, top - 0.05, 0],
               d * (rad + 0.05) + [0, top - 0.35, 0], d * rad + [0, fy + 1.15, 0]]
        _pipe(mb, pts, i_cu, 0.08, lod=lod)
        del tier


def _niche(mb, i_car, i_cu, i_ir, rng, noise) -> None:
    """The tier-2 side flue's sealed lamp-niche: a stone press against the wall beside its key, a riveted copper
    door shut over the niche, and the side flue's pipe running into its top."""
    side = [k for k in cs.key_list() if k[3] == "side"][0]
    _tier, a_key, y_key, _ = side
    ln = [x for x in cs.plan()[1] if x.tier == 2][0]
    a = a_key + 14.0 * (1.0 if cs.ang_diff(ln.centre, a_key) > 0 else -1.0)
    rot = cs.basis_at(a)
    d = np.array([math.cos(math.radians(a)), 0.0, math.sin(math.radians(a))])
    r = float(cs.inner_r(ln.y + 0.6))
    hx, hh, dep = NICHE
    c = d * (r - dep * 0.5 + 0.05) + np.array([0.0, ln.y + hh * 0.5, 0.0])
    kc.rounded_block(mb, c, (hx, hh * 0.5, dep * 0.5), i_car, rot=rot, radius=0.04, seg=2, noise=noise, disp_m=0.01,
                     disp_period_m=0.3, weather=cs.INNER_W, variation=float(rng.random()))
    door_c = d * (r - dep - 0.005) + np.array([0.0, ln.y + 0.62, 0.0])
    kc.rounded_block(mb, door_c, (0.3, 0.3, 0.02), i_cu, rot=rot, radius=0.01, seg=1, weather=cs.COPPER_W,
                     variation=0.7)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = door_c + rot @ np.array([sx * 0.25, sy * 0.25, -0.025])
            kc.rounded_block(mb, p, (0.018, 0.018, 0.012), i_ir, rot=rot, radius=0.008, seg=1)
    d_key = np.array([math.cos(math.radians(a_key)), 0.0, math.sin(math.radians(a_key))])
    rk = float(cs.inner_r(y_key))
    pts = [d_key * (rk - 0.15) + [0, y_key + 0.3, 0], d_key * (rk - 0.15) + [0, ln.y + hh + 0.25, 0],
           d * (r - 0.15) + [0, ln.y + hh + 0.25, 0], d * (r - 0.15) + [0, ln.y + hh - 0.05, 0]]
    _pipe(mb, pts, i_cu, 0.06)


def _grate(mb, y, r, i_ir, i_em, *, glow: bool, lod: bool) -> None:
    ang = np.linspace(0.0, 2.0 * math.pi, 17 if lod else 33)
    ring = np.stack([r * np.cos(ang), np.full_like(ang, y), r * np.sin(ang)], -1)
    kc.tube(mb, ring, 0.06, 4 if lod else 6, i_ir, weather=cs.IRON_W)
    n = 3 if lod else 7
    for k in range(n):
        x = -r + (k + 1) * 2.0 * r / (n + 1)
        h = math.sqrt(max(r * r - x * x, 0.0))
        for p0, p1 in (((x, -h), (x, h)), ((-h, x), (h, x))):
            kc.tube(mb, np.array([[p0[0], y, p0[1]], [p1[0], y, p1[1]]]), 0.035, 4, i_ir, weather=cs.IRON_W)
    if glow:
        ang2 = np.linspace(0.0, 2.0 * math.pi, 25)
        rr = np.array([0.0, r * 0.98])
        R, A = np.meshgrid(rr, ang2, indexing="ij")
        g = np.stack([R * np.cos(A), np.full_like(R, y + 0.15), R * np.sin(A)], -1)
        cs.surface(mb, g, i_em, outward=np.array([0.0, -1.0, 0.0]), uv=np.stack([g[..., 0], g[..., 2]], -1),
                   col=np.zeros(R.shape + (4,)), uv2=np.ones(R.shape + (2,)))


def build_tiers(name: str = "coilspire_tiers", seed: int = 1031) -> list[kc.MeshBuilder]:
    out = []
    flights, landings = cs.plan()
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_pave, i_car, i_cu, i_ir, i_em = (mb.material(cs.M_PAVING), mb.material(cs.M_CARVED), mb.material(cs.M_COPPER),
                                           mb.material(cs.M_IRON), mb.material(cs.M_EMBER))
        # The base hall: the floor (to the wall) and the dais in its middle.
        r_hall = float(cs.inner_r(0.0)) + 0.05
        ang = np.radians(np.linspace(0.0, 360.0, 25 if lod else 49)[:-1])
        cs.prism(mb, np.stack([r_hall * np.cos(ang), r_hall * np.sin(ang)], -1), -0.5, cs.TIER_Y[0], i_pave,
                 col=(0.0, 0.05, 0.05, 0.55), uv2=(0.75, 0.3), bottom=False)
        cs.prism(mb, np.stack([cs.DAIS_R * np.cos(ang), cs.DAIS_R * np.sin(ang)], -1), 0.0, cs.DAIS_H, i_car,
                 col=(0.0, 0.05, 0.0, 0.75), uv2=(0.85, 0.6), bottom=False)
        if not lod:
            cs.prism(mb, np.stack([(cs.DAIS_R + 0.35) * np.cos(ang), (cs.DAIS_R + 0.35) * np.sin(ang)], -1), 0.0, 0.14,
                     i_car, col=(0.0, 0.05, 0.0, 0.8), uv2=(0.8, 0.55), bottom=False)
        for ln in landings:
            _landing(mb, ln, i_pave, i_car, rng, noise, lod=lod)
        # The crown floor: an annulus round the well's grate, with the notch flight 4 comes up through.
        f4 = flights[3]
        notch = (f4.a1, f4.a1 + 120.0)
        r_c = float(cs.inner_r(cs.CROWN_Y)) + 0.05
        n_sec = 18 if lod else 54
        span = 360.0 - (notch[1] - notch[0])
        _sector_tiles(mb, cs.CROWN_Y, cs.LANDING_T, 0.85, r_c, notch[1], notch[1] + span, i_pave,
                      n=int(n_sec * span / 360.0), col=(0.0, 0.05, 0.05, 0.5), uv2=(0.8, 0.4))
        _sector_tiles(mb, cs.CROWN_Y, cs.LANDING_T, 0.85, r_c - 0.9, notch[0], notch[1], i_pave,
                      n=max(3, int(n_sec * 120.0 / 360.0)), col=(0.0, 0.05, 0.05, 0.5), uv2=(0.8, 0.4))
        if lod:
            # Only ever seen through the openings from outside: the floors are enough.
            out.append(mb)
            continue
        _grate(mb, cs.CROWN_Y - 0.05, 0.9, i_ir, i_em, glow=False, lod=lod)
        _grate(mb, cs.GRATE_Y, float(cs.inner_r(cs.GRATE_Y)) + 0.03, i_ir, i_em, glow=True, lod=lod)
        for f in flights:
            for i in range(1, f.count + 1):
                _tread(mb, f, i, i_car, rng, noise, lod=lod)
        _risers(mb, i_cu, lod=lod)
        _niche(mb, i_car, i_cu, i_ir, rng, noise)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Fittings
# ---------------------------------------------------------------------------------------------
def build_key(name: str = "flue_key") -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_cu, i_w = mb.material(cs.M_COPPER), mb.material(cs.M_COPPER_WORN)
        v0 = mb.vertex_count
        s = 6 if lod else 14
        z = np.array([0.0, 0.0, 1.0])
        kc.tube(mb, np.array([z * -0.15, z * 0.3]), 0.15, s, i_cu, weather=cs.COPPER_W, cap_end=True)
        kc.tube(mb, np.array([z * 0.0, z * 0.06]), 0.24, s, i_cu, weather=cs.COPPER_W, cap_end=True)  # wall flange
        kc.tube(mb, np.array([z * 0.28, z * 0.5]), 0.27, s, i_cu, weather=cs.COPPER_W, cap_start=True, cap_end=True)
        kc.tube(mb, np.array([z * 0.5, z * (KEY_STUB + 0.02)]), 0.045, 4 if lod else 8, i_w, weather=cs.COPPER_W,
                cap_end=True)
        if not lod:
            for k in range(8):  # the drum's rivets
                a = k * math.pi / 4.0
                p = np.array([0.27 * math.cos(a), 0.27 * math.sin(a), 0.39])
                kc.rounded_block(mb, p, (0.02, 0.02, 0.02), i_cu, radius=0.01, seg=1)
        cs.patina(mb, v0, kc.rng_for(name, 1041))
        out.append(mb)
    return out


def build_key_wheel(name: str = "flue_key_wheel") -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_cu, i_w = mb.material(cs.M_COPPER), mb.material(cs.M_COPPER_WORN)
        n = 12 if lod else 48
        ang = np.linspace(0.0, 2.0 * math.pi, n + 1)
        rim = np.stack([WHEEL_R * np.cos(ang), WHEEL_R * np.sin(ang), np.zeros_like(ang)], -1)
        kc.tube(mb, rim, 0.035, 4 if lod else 8, i_w, weather=kc.Weathering(moss=0.0, salt=0.1, wet=0.0, erosion=0.9),
                first_normal=np.array([0.0, 0.0, 1.0]))
        v0 = mb.vertex_count
        kc.tube(mb, np.array([[0, 0, -0.06], [0, 0, 0.07]]), 0.08, 6 if lod else 12, i_cu, weather=cs.COPPER_W,
                cap_start=True, cap_end=True)
        for k in range(6):
            a = k * math.pi / 3.0
            d = np.array([math.cos(a), math.sin(a), 0.0])
            kc.tube(mb, np.array([d * 0.07, d * (WHEEL_R - 0.02)]), 0.022, 3 if lod else 6, i_cu, weather=cs.COPPER_W)
        cs.patina(mb, v0, kc.rng_for(name, 1051), lo=0.6, hi=0.9)
        if not lod:
            for a in (0.0, math.pi):  # two handle knobs, worn brightest
                d = np.array([math.cos(a + 0.5), math.sin(a + 0.5), 0.0])
                kc.tube(mb, np.array([d * WHEEL_R + [0, 0, 0.0], d * WHEEL_R + [0, 0, 0.13]]), 0.03, 8, i_w,
                        weather=kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=1.0), cap_end=True)
        out.append(mb)
    return out


def build_brazier(name: str = "tier_brazier", seed: int = 1061) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_ir, i_cu, i_em = mb.material(cs.M_IRON), mb.material(cs.M_COPPER), mb.material(cs.M_EMBER)
        top = 0.9
        for k in range(3):
            a = k * 2.0 * math.pi / 3.0 + 0.3
            d = np.array([math.cos(a), 0.0, math.sin(a)])
            pts = [d * 0.48 + [0, 0.0, 0], d * 0.5 + [0, 0.25, 0], d * 0.4 + [0, 0.6, 0], d * 0.36 + [0, top - 0.05, 0]]
            kc.tube(mb, np.asarray(pts), 0.03, 4 if lod else 6, i_ir, weather=cs.IRON_W)
            if not lod:
                kc.rounded_block(mb, d * 0.49 + [0, 0.02, 0], (0.06, 0.02, 0.05), i_ir, rot=kc.rot_y(-a), radius=0.01,
                                 seg=1)
        if not lod:
            ang = np.linspace(0.0, 2.0 * math.pi, 25)
            ring = np.stack([0.4 * np.cos(ang), np.full_like(ang, 0.45), 0.4 * np.sin(ang)], -1)
            kc.tube(mb, ring, 0.02, 4, i_ir, weather=cs.IRON_W)
        prof_r = np.array([0.08, 0.25, 0.36, 0.4, 0.42])
        prof_y = np.array([top - 0.12, top - 0.06, top + 0.06, top + 0.18, top + 0.24])
        cs.lathe_ring(mb, prof_r, prof_y, 10 if lod else 20, i_cu, col=(0.05, 0.85, 0.1, 0.25))
        if not lod:
            v0, t0 = mb.vertex_count, mb.triangle_count
            cs.lathe_ring(mb, prof_r[1:] * 0.92, prof_y[1:] + 0.015, 20, i_cu, col=(0.3, 0.3, 0.0, 0.1))
            cs.flip_section(mb, v0, t0)
        # The ember bed: a low mound and a few coals (the flame is VFX).
        R, A = np.meshgrid(np.linspace(0.0, 0.36, 2 if lod else 4), np.linspace(0.0, 2.0 * math.pi, 9 if lod else 21),
                           indexing="ij")
        Y = top + 0.14 + 0.06 * (1.0 - (R / 0.36) ** 2)
        g = np.stack([R * np.cos(A), Y, R * np.sin(A)], -1)
        cs.surface(mb, g, i_em, outward=np.array([0.0, 1.0, 0.0]), uv=np.stack([g[..., 0], g[..., 2]], -1),
                   col=np.zeros(R.shape + (4,)), uv2=np.ones(R.shape + (2,)))
        if not lod:
            for _k in range(7):
                a = rng.uniform(0.0, 2.0 * math.pi)
                r = rng.uniform(0.0, 0.26)
                c = np.array([r * math.cos(a), top + 0.21, r * math.sin(a)])
                kc.rounded_block(mb, c, rng.uniform(0.04, 0.08, 3) * [1.0, 0.6, 1.0], i_em, radius=0.02, seg=1,
                                 rot=kc.rot_y(rng.uniform(0, math.pi)), variation=float(rng.random()))
        out.append(mb)
    return out


TARGETS = {"coilspire_tiers": build_tiers, "flue_key": build_key, "flue_key_wheel": build_key_wheel,
           "tier_brazier": build_brazier}
