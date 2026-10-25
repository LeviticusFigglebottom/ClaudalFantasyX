"""The Tamsule Bell, its goal ring and the water-drop placeholder (tamsule_bell.md §1-2; M3-ENV-01).

  tamsule_bell         the Lit Age bronze bell, hung mouth-down: sound bow with the hand-line cord and
                       the float-ring row, a glass waist of 24 ribs and 48 salt-glass bays, a solid
                       crown with 12 crown ports and 6 crown loops, bound-light conduits up every rib
  goal_ring            the bronze ring at the drop's top surface, hung from the inner apex on 3 rods
  reefball_drop_proxy  PLACEHOLDER for PC GPU's drop: the contract spheroid and the weep column

The bell and the goal ring have their origin on the arena axis at the river datum (y is absolute); the
drop placeholder has its origin at the drop's centre, so it sits on the SphereAnchor marker as is. The drop contract
(DROP_*) is shared with PC GPU (pc-gpu.md) and checked by tools/tests/test_tamsule_bell_kit.py.
"""

from __future__ import annotations

import math

import numpy as np

import tb_common as tb
from tb_common import kc

# ---- The water-drop contract (tamsule_bell.md §1) -----------------------------------------------
LIFT = 6.0  # the stack sits 6 m higher than the first draft, so the drop hangs clear above the galleries
DROP_CENTER = (0.0, 25.5 + LIFT, 0.0)
DROP_RADIUS_H = 14.0
DROP_RADIUS_V = 11.5
DROP_BOTTOM_Y = DROP_CENTER[1] - DROP_RADIUS_V  # 14.0, the weep point
DROP_TOP_Y = DROP_CENTER[1] + DROP_RADIUS_V  # 37.0, the surface and the goal ring
POOL_WATER_Y = 0.35
COLUMN_RADII = (0.8, 0.6)  # top, bottom
MIN_CLEARANCE_M = 2.0
GOAL_RING_R = 1.6

M_BRONZE = "tb_bell_bronze"
M_GLASS = "tb_salt_glass"
M_CONDUIT = "tb_glimmer_conduit"
M_PORT = "tb_port_glass"
M_DROP = "tb_drop_proxy"

TRI_BUDGET = {
    "tamsule_bell": (60000, 6000),
    "goal_ring": (2400, 300),
    "reefball_drop_proxy": (8000, 800),
}
PLACEHOLDER_REASONS = {
    "reefball_drop_proxy": "the Reefball water drop's look is PC GPU R&D (pc-gpu.md); this is the agreed "
                           "volume (tamsule_bell.md §1) so compositions can be judged",
}

RIM_Y = 21.0 + LIFT
WAIST_Y = (24.15 + LIFT, 35.0 + LIFT)
MID_RAIL_Y = (29.2 + LIFT, 29.8 + LIFT)
N_RIBS = 24
RIB_W = 0.9
RIB_PROUD = 0.4
CROWN_PORT_Y = 38.6 + LIFT
N_PORTS = 12

# Bell profiles, (r, y) control points. The inner surface is one curve from the lip to the apex.
INNER = np.array([(16.4, 21.15), (16.4, 22.0), (16.35, 23.5), (16.3, 24.15), (16.3, 26.0), (16.0, 28.0),
                  (15.6, 30.0), (15.1, 32.5), (14.5, 35.0), (14.0, 36.2), (13.1, 38.0), (11.0, 39.8), (7.5, 40.9),
                  (3.6, 41.3), (0.0, 41.4)]) + (0.0, LIFT)
OUTER_WAIST = np.array([(17.45, 24.0), (17.1, 26.0), (16.75, 28.0), (16.4, 30.0), (15.9, 32.5), (15.3, 35.0)]) + (0.0, LIFT)
OUTER_CROWN = np.array([(15.3, 35.0), (14.85, 36.6), (14.0, 38.4), (12.6, 40.0), (10.6, 41.3), (8.0, 42.25),
                        (4.8, 42.8), (0.0, 43.0)]) + (0.0, LIFT)
SOUND_BOW_OUT = np.array([(17.9, 21.05), (18.1, 21.4), (18.15, 22.0), (18.0, 22.9), (17.65, 23.6), (17.45, 24.0)]) + (0.0, LIFT)
LIP_BOTTOM = np.array([(16.4, 21.15), (16.6, 21.0), (17.5, 20.92), (17.9, 21.05)]) + (0.0, LIFT)

WORN = kc.Weathering(moss=0.0, salt=0.45, wet=0.1, erosion=0.75, noise_scale_m=1.5)
SPRAY = kc.Weathering(moss=0.25, salt=0.9, wet=0.6, erosion=0.5, noise_scale_m=2.0)


def r_at(profile: np.ndarray, y) -> np.ndarray:
    """Radius of a monotone-in-y (r, y) profile at height(s) y."""
    order = np.argsort(profile[:, 1])
    return np.interp(y, profile[order, 1], profile[order, 0])


def inner_r(y):
    return r_at(INNER, y)


def outer_r(y):
    y = np.asarray(y, float)
    return np.where(y < WAIST_Y[0], r_at(SOUND_BOW_OUT, y), np.where(y <= WAIST_Y[1], r_at(OUTER_WAIST, y),
                                                                     r_at(OUTER_CROWN, y)))


def drop_radius(y) -> np.ndarray:
    t = (np.asarray(y, float) - DROP_CENTER[1]) / DROP_RADIUS_V
    return DROP_RADIUS_H * np.sqrt(np.clip(1.0 - t * t, 0.0, None))


def drop_clearance(samples: int = 720) -> float:
    """Smallest (r, y) distance from the drop's surface to the bell's inner surface above the rim."""
    curve = tb.catmull_rom(INNER, 24)
    t = np.linspace(0.0, math.pi, samples)
    ell = np.stack([DROP_RADIUS_H * np.sin(t), DROP_CENTER[1] - DROP_RADIUS_V * np.cos(t)], axis=-1)
    ell = ell[ell[:, 1] >= RIM_Y]
    a, b = curve[:-1], curve[1:]
    best = np.inf
    for p in ell:
        ab = b - a
        tt = np.clip(np.einsum("ij,ij->i", p - a, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-12), 0, 1)
        d = np.linalg.norm(a + ab * tt[:, None] - p, axis=1).min()
        best = min(best, float(d))
    return best


# ---------------------------------------------------------------------------------------------
# Pieces of the bell
# ---------------------------------------------------------------------------------------------
def _sector_solid(mb, ys, rin, rout, az0, az1, n_az, mat, *, weather, noise, edge=0.4, top=True, bottom=True,
                  variation=0.5, sides=True):
    """A solid between the (r, y) curves rin(ys) and rout(ys), swept from az0 to az1, side walls included."""
    ys = np.asarray(ys, float)
    rin = np.asarray(rin, float)
    rout = np.asarray(rout, float)
    common = dict(weather=weather, noise=noise, variation=variation)
    tb.revolve(mb, np.stack([rout, ys], -1), az0, az1, n_az, mat, outward=1.0, edge=edge * 0.6, **common)
    tb.revolve(mb, np.stack([rin, ys], -1), az0, az1, n_az, mat, outward=-1.0, ao=0.7, **common)
    if top:
        tb.revolve(mb, [(rout[-1], ys[-1]), (rin[-1], ys[-1])], az0, az1, n_az, mat, outward=1.0, edge=edge,
                   **common)
    if bottom:
        tb.revolve(mb, [(rin[0], ys[0]), (rout[0], ys[0])], az0, az1, n_az, mat, outward=1.0, edge=edge, **common)
    for az, sgn in ((az0, -1.0), (az1, 1.0)) if sides else ():
        grid = np.stack([tb.polar(rin, az, ys), tb.polar(rout, az, ys)], axis=1)  # (rows y, 2)
        tang = tb.polar(1.0, az + 90.0, 0.0) * sgn
        nn = np.broadcast_to(tang, grid.shape)
        uv = np.stack([np.stack([np.zeros_like(ys), rout - rin], 1), np.stack([ys, ys], 1)], axis=-1)
        col = tb.surface_colors(grid, nn, weather, noise, edge=np.full(grid.shape[:2], edge))
        kc.quad_strip(mb, grid, mat, uv=uv, col=col, uv2=np.array([0.8, variation]),
                      flip=tb._orient(mb, grid, tang))


def _cord_ring(mb, y, r_base, tube_r, twists, mat, *, n_ring=480, sides=8, groove=0.35, weather=None, noise=None):
    """A twisted cord (the hand-line) around the bell at height y: one tube whose section is grooved
    by a spiral, so it reads as two or three twisted strands at a fraction of the triangles."""
    phi = np.linspace(0.0, 2.0 * math.pi, n_ring + 1)
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    P, A = np.meshgrid(phi, ang, indexing="ij")
    radial = np.stack([np.sin(P), np.zeros_like(P), -np.cos(P)], axis=-1)
    up = np.array([0.0, 1.0, 0.0])
    dirs = radial * np.cos(A)[..., None] + up * np.sin(A)[..., None]
    rr = tube_r * (1.0 - groove * 0.5 + groove * 0.5 * np.cos(3.0 * A - P * twists))
    center = radial * r_base + up * y
    p = center + dirs * rr[..., None]
    uv = np.stack([P * r_base, A * tube_r], axis=-1)
    col = tb.surface_colors(p, dirs, weather, noise, edge=0.5 + 0.5 * np.cos(3.0 * A - P * twists))
    kc.quad_strip(mb, p, mat, uv=uv, col=col, uv2=np.array([0.9, 0.4]), flip=tb._orient(mb, p, dirs[n_ring // 2,
                                                                                                    sides // 4]))


def _surface_frame(y, az, profile_fn, dy=0.05):
    """Point on the outer surface at (y, az), its outward normal and the meridian tangent (upward)."""
    r = float(profile_fn(y))
    p = tb.polar(r, az, y)
    r1, r0 = float(profile_fn(y + dy)), float(profile_fn(y - dy))
    tan_up = kc.normalize(tb.polar(r1, az, y + dy) - tb.polar(r0, az, y - dy))
    around = tb.polar(1.0, az + 90.0, 0.0)
    n = kc.normalize(np.cross(tan_up, around))
    if float(np.dot(n, tb.polar(1.0, az, 0.0))) < 0:
        n = -n
    return p, n, tan_up


def build_bell(seed: int = 701, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for("tamsule_bell", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("tamsule_bell" + ("-lod1" if lod else ""))
    bronze = mb.material(M_BRONZE)
    glass = mb.material(M_GLASS)
    n_full = 32 if lod else 144  # around the bell, outer surfaces
    n_in = 24 if lod else 96  # inner surfaces (seen only from below, in shade)
    sp = 3 if lod else 4  # spline samples per control segment
    w = dict(weather=tb.BRONZE, noise=None if lod else noise)

    # ---- Sound bow (y 21-24): lip underside, the outer bow, the sill, the inner face ----------------
    lip = tb.catmull_rom(LIP_BOTTOM, sp)
    bow = tb.catmull_rom(SOUND_BOW_OUT, sp)
    sill = [(17.45, 24.0 + LIFT), (17.62, 24.0 + LIFT), (17.62, WAIST_Y[0]), (16.3, WAIST_Y[0])]
    inner_bow = tb.catmull_rom(INNER[INNER[:, 1] <= WAIST_Y[0] + 0.01][::-1], 3)
    tb.revolve(mb, lip, 0, 360, n_full, bronze, weather=SPRAY, noise=w["noise"], outward=1.0, edge=0.9,
               wet_bias=0.25, underside_grime=0.3)
    tb.revolve(mb, bow, 0, 360, n_full, bronze, outward=1.0, edge=0.25, disp_m=0.0 if lod else 0.03,
               disp_period_m=1.8, **w)
    tb.revolve(mb, np.asarray(sill[:2]), 0, 360, n_full, bronze, outward=1.0, edge=0.6, **w)
    tb.revolve(mb, np.asarray(sill[1:3]), 0, 360, n_full, bronze, outward=1.0, edge=0.9, **w)
    tb.revolve(mb, np.asarray(sill[2:]), 0, 360, n_full, bronze, outward=1.0, edge=0.5, **w)
    tb.revolve(mb, inner_bow, 0, 360, n_in, bronze, weather=SPRAY, noise=w["noise"], outward=1.0, ao=0.6,
               wet_bias=0.2, underside_grime=0.2)

    # ---- Glass waist (y 24.15-35): ribs, the mid-rail, 48 salt-glass bays ------------------------
    ys = np.linspace(WAIST_Y[0], WAIST_Y[1], 4 if lod else 12)
    rin = inner_r(ys)
    rout = r_at(OUTER_WAIST, ys)
    step = 360.0 / N_RIBS
    for k in range(N_RIBS):
        c = k * step
        hw = math.degrees(RIB_W * 0.5 / float(rout.mean()))
        _sector_solid(mb, ys, rin, rout + RIB_PROUD, c - hw, c + hw, 1 if lod else 2, bronze, top=False,
                      bottom=False, edge=0.55, variation=float(rng.random()), **w)
        for y0, y1 in ((WAIST_Y[0], MID_RAIL_Y[0]), (MID_RAIL_Y[1], WAIST_Y[1])):
            yb = np.linspace(y0, y1, 2 if lod else 6)
            rm = (inner_r(yb) + r_at(OUTER_WAIST, yb)) * 0.5
            tb.revolve(mb, np.stack([rm, yb], -1), c + hw, c + step - hw, 1 if lod else 4, glass,
                       weather=tb.BRONZE, noise=None, outward=1.0, variation=float(rng.random()))
    yr = np.array(MID_RAIL_Y)
    _sector_solid(mb, yr, inner_r(yr) - 0.05, r_at(OUTER_WAIST, yr) + 0.18, 0, 360, n_full, bronze, edge=0.6,
                  sides=False, **w)

    # ---- Shoulder and crown (y 35 to the apex) -----------------------------------------------
    crown_out = tb.catmull_rom(OUTER_CROWN, sp)
    crown_in = tb.catmull_rom(INNER[INNER[:, 1] >= WAIST_Y[1] - 0.01][::-1], 3)  # apex -> shoulder: faces the cavity
    tb.revolve(mb, crown_out, 0, 360, n_full, bronze, outward=1.0, edge=0.15, disp_m=0.0 if lod else 0.04,
               disp_period_m=2.2, **w)
    tb.revolve(mb, crown_in, 0, 360, n_in, bronze, outward=1.0, ao=0.55, **w)
    tb.revolve(mb, [(float(inner_r(WAIST_Y[1])), WAIST_Y[1]), (15.3, WAIST_Y[1])], 0, 360, n_full, bronze, outward=1.0, edge=0.5,
               **w)
    if lod:
        return mb

    # ---- Relief: the hand-line cord, the float-ring row, a bead ring, crown ribs -------------------
    _cord_ring(mb, 22.45 + LIFT, float(outer_r(22.45 + LIFT)) + 0.1, 0.16, 90.0, bronze, n_ring=400, weather=WORN, noise=noise)
    _cord_ring(mb, 36.1 + LIFT, float(outer_r(36.1 + LIFT)) + 0.06, 0.1, 70.0, bronze, n_ring=320, sides=6, weather=WORN,
               noise=noise)
    for k in range(36):
        az = k * 10.0 + 5.0
        p, n, tan_up = _surface_frame(23.35 + LIFT, az, outer_r)
        tb.torus(mb, p + n * 0.05, n, 0.3, 0.075, 12, 5, bronze, weather=WORN, up_hint=tan_up)
    for k in range(N_RIBS):
        c = k * step
        yc = np.linspace(35.15 + LIFT, 42.4 + LIFT, 7)
        rc = r_at(OUTER_CROWN, yc)
        hw = math.degrees(0.35 / max(float(rc.mean()), 1.0))
        _sector_solid(mb, yc, rc - 0.05, rc + 0.17, c - hw, c + hw, 1, bronze, top=True, bottom=False, edge=0.7,
                      **w)

    # ---- Crown ports and crown loops --------------------------------------------------------
    port = mb.material(M_PORT)
    for k in range(N_PORTS):
        az = k * (360.0 / N_PORTS) + step * 0.5
        p, n, tan_up = _surface_frame(CROWN_PORT_Y, az, outer_r)
        tb.torus(mb, p + n * 0.1, n, 0.85, 0.2, 16, 6, bronze, weather=WORN, up_hint=tan_up)
        ring = np.radians(np.linspace(0, 360, 17))
        e1 = tan_up
        e2 = np.cross(n, e1)
        rim = p + n * 0.06 + 0.78 * (np.cos(ring)[:, None] * e1 + np.sin(ring)[:, None] * e2)
        base = mb.add_vertices(np.vstack([rim[:-1], (p + n * 0.1)[None]]), np.tile(n, (17, 1)),
                               np.vstack([np.stack([np.cos(ring[:-1]), np.sin(ring[:-1])], 1) * 0.5 + 0.5,
                                          [[0.5, 0.5]]]), np.tile([1.0, 0.5], (17, 1)), np.tile([0, 0, 0, 0], (17, 1)))
        for j in range(16):
            a_, b_ = base + j, base + (j + 1) % 16
            tri = (a_, b_, base + 16)
            pa, pb, pc = (np.asarray(mb.pos[i]) for i in tri)
            if float(np.dot(np.cross(pb - pa, pc - pa), n)) < 0:
                tri = (b_, a_, base + 16)
            mb.add_tri(*tri, port)
    for k in range(6):
        az = k * 60.0  # under the gantry head's radial beams and hangers
        base_p = tb.polar(3.6, az, float(np.interp(3.6, OUTER_CROWN[::-1, 0], OUTER_CROWN[::-1, 1])) - 0.05)
        tb.torus(mb, base_p + np.array([0.0, 0.25, 0.0]), tb.polar(1.0, az + 90.0, 0.0), 1.1, 0.32, 20, 8, bronze,
                 weather=WORN, arc_deg=200.0, start_deg=-10.0, up_hint=tb.polar(1.0, az, 0.0))

    # ---- Bound-light conduits up every rib's inner face (y 21.6 to 42) ----------------------
    cond = mb.material(M_CONDUIT)
    yc = np.linspace(21.6 + LIFT, 40.8 + LIFT, 26)
    rc = inner_r(yc) - 0.05
    for k in range(N_RIBS):
        c = k * step
        hw = np.degrees(0.07 / np.maximum(rc, 1.0))
        grid = np.stack([tb.polar(rc, c - hw, yc), tb.polar(rc, c + hw, yc)], axis=1)
        inward = -tb.polar(1.0, c, 0.0)
        uv = np.stack([np.tile([[0.0, 1.0]], (len(yc), 1)), np.stack([yc, yc], 1)], axis=-1)
        kc.quad_strip(mb, grid, cond, uv=uv, col=np.array([0.0, 0.0, 0.0, 0.0]), uv2=np.array([1.0, 0.5]),
                      flip=tb._orient(mb, grid, inward), smooth=False)
        nrm_start = mb.vertex_count - grid.shape[0] * grid.shape[1]
        mb.nrm[nrm_start:] = np.tile(inward, (grid.shape[0] * grid.shape[1], 1)).tolist()
    return mb


def build_tamsule_bell() -> list[kc.MeshBuilder]:
    return [build_bell(), build_bell(lod=True)]


def build_goal_ring(seed: int = 702) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("goal_ring", seed)
        mb = kc.MeshBuilder("goal_ring" + ("-lod1" if lod else ""))
        bronze = mb.material(M_BRONZE)
        y = DROP_TOP_Y
        tb.torus(mb, (0.0, y, 0.0), (0.0, 1.0, 0.0), GOAL_RING_R, 0.12, 16 if lod else 64, 4 if lod else 8, bronze,
                 weather=WORN, up_hint=(1.0, 0.0, 0.0))
        top = np.array([0.0, float(INNER[-1, 1]) - 0.05, 0.0])
        for k in range(3):
            a = tb.polar(GOAL_RING_R, k * 120.0, y + 0.08)
            kc.tube(mb, np.linspace(a, top + tb.polar(0.25, k * 120.0, 0.0), 4), 0.05, 4 if lod else 6, bronze,
                    weather=WORN, variation=float(rng.random()))
        kc.tube(mb, np.array([top - [0, 0.3, 0], top]), 0.3, 6 if lod else 12, bronze, weather=WORN, cap_start=True,
                cap_end=True)
        out.append(mb)
    return out


def build_drop_proxy(seed: int = 703) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("reefball_drop_proxy" + ("-lod1" if lod else ""))
        mat = mb.material(M_DROP)
        t = np.linspace(0.0, math.pi, 9 if lod else 33)
        # Origin at the drop's centre: the node sits on SphereAnchor with an identity transform.
        prof = np.stack([DROP_RADIUS_H * np.sin(t), -DROP_RADIUS_V * np.cos(t)], axis=-1)
        tb.revolve(mb, prof, 0, 360, 16 if lod else 64, mat, weather=kc.FRESH, outward=1.0)
        ys = np.linspace(DROP_BOTTOM_Y + 0.2, POOL_WATER_Y, 4 if lod else 10) - DROP_CENTER[1]
        radii = np.linspace(COLUMN_RADII[0], COLUMN_RADII[1], len(ys))
        kc.tube(mb, np.stack([np.zeros_like(ys), ys, np.zeros_like(ys)], -1), radii, 8 if lod else 16, mat,
                weather=kc.FRESH)
        out.append(mb)
    return out


TARGETS = {
    "tamsule_bell": build_tamsule_bell,
    "goal_ring": build_goal_ring,
    "reefball_drop_proxy": build_drop_proxy,
}
