"""The Underway's story props (oruvel_underway.md §2). Pure numpy; see ou_common.py.

  divers_cord  2.4 m of hemp tied across a stair (along Z, 0.9 m up, sagging) between two ring-bolts: ~100 knots, a
               quarter of them new and pale, a few with short tag ends, frayed tails at the ties
  tether_line  6 m of line from the surface (y 6) down to a brass clip and a lead weight (origin at the weight)
  wreck_ribs   the dead ship on the terrace, 15 m along X: a keel, 13 pairs of black frames arching out of the sand
               (broken off at different heights, a few gone or leaning), some strakes, the stem post, a coral head
               grown in the hold. Its frames are the kind Hullgnaw wears
  hull_keels   Oruvel from below: three lashed hulls' bottoms (11, 8 and 7 m) with weed beards, crossbeams and a
               mooring line; origin at the waterline. A stand-in until the raft-town kit ships its hulls
  old_tin      the old tin behind the coral curtain (C1-04's find): a Lit Age iron box, 0.46 m, rusted and crusted, its
               lid knocked askew, a brass clasp and a diver's cord through the handle; origin on the floor under it
  shaft_limpet the gauge room's limpet (C1-06's look, the shaft's fight): a 0.6 m ribbed shell clamped to the wall, three
               young ones beside it; origin on the wall's face, the shells toward +Z
"""

from __future__ import annotations

import math

import numpy as np

import ou_common as oc

kc = oc.kc

TRI_BUDGET = {
    "divers_cord": (4500, 100),
    "tether_line": (1500, 60),
    "wreck_ribs": (12000, 900),
    "hull_keels": (6000, 400),
    "old_tin": (1500, 120),
    "shaft_limpet": (3000, 200),
}

CORD_SPAN = 2.4
CORD_Y = 0.9
CORD_KNOTS = 100


def cord_point(s: np.ndarray) -> np.ndarray:
    """The cord's centre line, s in [0, 1] from -Z to +Z: a shallow catenary sagging 0.12 m."""
    s = np.asarray(s, float)
    z = (s - 0.5) * CORD_SPAN
    y = CORD_Y - 0.12 * (1.0 - (2.0 * s - 1.0) ** 2)
    return np.stack([0.01 * np.sin(s * 9.0), y, z], axis=-1)


def build_divers_cord(seed: int = 901) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("divers_cord", seed)
    mb = kc.MeshBuilder("divers_cord")
    old = mb.material(oc.M_CORD_OLD)
    knots = np.sort(rng.uniform(0.05, 0.95, CORD_KNOTS))
    s_list, r_list = [0.0], [0.009]
    for k in knots:
        for ds, r in ((-0.004, 0.009), (0.0, 0.02 + rng.uniform(0, 0.005)), (0.004, 0.009)):
            s_list.append(k + ds)
            r_list.append(r)
    s_list.append(1.0)
    r_list.append(0.009)
    order = np.argsort(s_list)
    s_arr, r_arr = np.asarray(s_list)[order], np.asarray(r_list)[order]
    start_t = mb.triangle_count
    kc.tube(mb, cord_point(s_arr), r_arr, 6, old, weather=oc.CAST, variation=0.3)
    # A quarter of the knots are new: pale hemp, tied since the last storm.
    new_k = knots[rng.random(CORD_KNOTS) < 0.25]
    centres = cord_point(new_k)
    cen = oc.tri_centroids(mb, start_t)
    newm = mb.material(oc.M_CORD_NEW)
    d = np.linalg.norm(cen[:, None, :] - centres[None, :, :], axis=-1).min(axis=1)
    for i in np.nonzero(d < 0.014)[0]:
        mb.tri_mat[start_t + int(i)] = newm
    # Tag ends on some knots, and the ties: ring-bolts, wraps and frayed tails.
    for k in knots[rng.random(CORD_KNOTS) < 0.12]:
        p = cord_point(np.array(k))
        L = rng.uniform(0.04, 0.12)
        kc.tube(mb, np.array([p, p + np.array([rng.normal(0, 0.01), -L, rng.normal(0, 0.01)])]), 0.005, 4,
                newm if rng.random() < 0.3 else old, weather=oc.CAST, cap_end=True)
    iron = mb.material(oc.M_IRON)
    for s, sgn in ((0.0, -1.0), (1.0, 1.0)):
        p = cord_point(np.array(s))
        oc.ring(mb, p, 0.035, 0.008, iron, axis=(1, 0, 0), segs=12, sides=4)
        kc.tube(mb, np.array([p + np.array([0, 0, sgn * 0.035]), p + np.array([0, 0, sgn * 0.12])]), 0.012, 6, iron,
                weather=oc.DROWNED, cap_end=True)
        for w in range(3):
            oc.ring(mb, p + np.array([0, 0, -sgn * (0.015 + 0.012 * w)]), 0.014, 0.006, old, axis=(0, 0, 1), segs=8,
                    sides=4)
        for _t in range(3):
            q = p + np.array([0, -0.01, -sgn * 0.05])
            L = rng.uniform(0.08, 0.2)
            kc.tube(mb, np.array([q, q + np.array([rng.normal(0, 0.02), -L, -sgn * rng.uniform(0, 0.04)])]), 0.006, 4,
                    old, weather=oc.CAST, cap_end=True)
    lod = kc.MeshBuilder("divers_cord" + oc.LOD)
    kc.tube(lod, cord_point(np.linspace(0, 1, 6)), 0.014, 3, lod.material(oc.M_CORD_OLD))
    return [mb, lod]


def build_tether_line(seed: int = 902, length: float = 6.0) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("tether_line", seed)
    out = []
    for suffix, n, sides in (("", 18, 6), (oc.LOD, 4, 3)):
        mb = kc.MeshBuilder("tether_line" + suffix)
        t = np.linspace(0.0, 1.0, n)
        pts = np.stack([0.18 * np.sin(t * math.pi) + 0.04 * np.sin(t * 7.0), 0.3 + (length - 0.3) * t,
                        0.08 * np.sin(t * 4.0)], axis=-1)
        kc.tube(mb, pts, 0.011, sides, mb.material(oc.M_CORD_OLD), weather=oc.CAST)
        if not suffix:
            brass = mb.material(oc.M_BRASS)
            oc.ring(mb, (0.0, 0.26, 0.0), 0.035, 0.007, brass, axis=(0, 0, 1), segs=14, sides=4)
            kc.tube(mb, np.array([[0, 0.226, 0], [0, 0.17, 0]]), 0.006, 4, brass, weather=oc.CAST)
            oc.lathe(mb, [(0.0, 0.0), (0.05, 0.01), (0.06, 0.06), (0.045, 0.15), (0.012, 0.17), (0.0, 0.172)],
                     mb.material(oc.M_LEAD), sides=12)
        out.append(mb)
    del rng
    return out


SHIP_L = 15.0
SHIP_FRAMES = 13
SHIP_B = 2.5  # half breadth amidships
SHIP_SINK = 0.55  # how deep the hull lies in the silt


def _half_breadth(x: float) -> float:
    u = abs(x) / (SHIP_L * 0.5)
    return SHIP_B * max(1.0 - u ** 3.2, 0.12) ** 0.55


def _frame_curve(x: float, side: float, phi_max: float, n: int) -> np.ndarray:
    b = _half_breadth(x)
    phi = np.linspace(0.05, phi_max, n)
    z = side * b * np.sin(phi) * (1.0 - 0.06 * np.clip(phi - 1.4, 0, None))
    y = 0.15 + b * 0.92 * (1.0 - np.cos(phi))
    return np.column_stack([np.full(n, x), y, z])


def build_wreck_ribs(seed: int = 903) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("wreck_ribs", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("wreck_ribs")
    tar = mb.material(oc.M_TIMBER_TAR)
    heel = kc.rot_x(0.13)
    sink = np.array([0.0, -SHIP_SINK, 0.0])

    def place(p):
        return np.asarray(p, float) @ heel.T + sink

    keel = np.array([[-SHIP_L * 0.5, 0.05, 0], [0, 0.0, 0], [SHIP_L * 0.5, 0.06, 0]])
    kc.tube(mb, place(keel), 0.17, 6, tar, weather=oc.DROWNED, noise=noise, disp_m=0.03, cap_start=True, cap_end=True)
    xs = np.linspace(-SHIP_L * 0.5 + 1.0, SHIP_L * 0.5 - 1.0, SHIP_FRAMES)
    tops = []
    for i, x in enumerate(xs):
        for side in (-1.0, 1.0):
            if rng.random() < 0.12:
                continue  # rotted away
            phi_max = rng.uniform(0.95, 1.85) if rng.random() < 0.75 else rng.uniform(0.5, 0.9)
            pts = _frame_curve(float(x), side, phi_max, 9)
            if rng.random() < 0.15:  # snapped and leaning outward
                lean = kc.rot_x(side * rng.uniform(0.15, 0.35))
                pivot = pts[3]
                pts[3:] = (pts[3:] - pivot) @ lean.T + pivot
            r = np.linspace(0.12, 0.085, len(pts)) * (1.0 + 0.1 * rng.normal())
            kc.tube(mb, place(pts), r, 5, tar, weather=oc.DROWNED, noise=noise, disp_m=0.025,
                    variation=float(rng.random()), cap_end=True, first_normal=(1.0, 0.0, 0.0))
            tops.append((place(pts[-1]), i, side))
    # Strakes still nailed on, low on the starboard side, and a stringer to port.
    for phi, xa, xb in ((0.45, -4.6, 1.8), (0.7, -2.5, 3.6), (0.95, -1.4, 0.9)):
        a = _frame_curve(xa, 1.0, phi, 2)[-1]
        b = _frame_curve(xb, 1.0, phi, 2)[-1]
        kc.plank(mb, place(a + np.array([0, 0, 0.12])), place(b + np.array([0, 0, 0.12])), 0.24, 0.06, tar,
                 up=np.array([0.0, -math.sin(phi), math.cos(phi)]), weather=oc.DROWNED, noise=noise, seg=6,
                 variation=float(rng.random()))
    a = _frame_curve(-3.6, -1.0, 1.2, 2)[-1]
    b = _frame_curve(4.2, -1.0, 1.2, 2)[-1]
    kc.plank(mb, place(a), place(b), 0.16, 0.12, tar, up=np.array([0, 0.3, -1.0]), weather=oc.DROWNED, noise=noise, seg=8)
    # Stem post at the bow (+X), the sternpost broken short.
    stem = np.array([[SHIP_L * 0.5 - 0.2, 0.05, 0], [SHIP_L * 0.5 + 0.6, 1.4, 0], [SHIP_L * 0.5 + 0.9, 2.7, 0],
                     [SHIP_L * 0.5 + 1.0, 3.3, 0]])
    kc.tube(mb, place(stem), np.array([0.16, 0.15, 0.13, 0.11]), 6, tar, weather=oc.DROWNED, noise=noise, disp_m=0.03,
            cap_end=True)
    stern = np.array([[-SHIP_L * 0.5 + 0.2, 0.05, 0], [-SHIP_L * 0.5 - 0.3, 1.1, 0], [-SHIP_L * 0.5 - 0.4, 1.6, 0.05]])
    kc.tube(mb, place(stern), 0.15, 6, tar, weather=oc.DROWNED, noise=noise, disp_m=0.03, cap_end=True)
    # The reef in the hold: a boulder coral amidships, coral on the frame tops, fans, sponges on the keel.
    kc.rounded_block(mb, place([0.6, 0.55, 0.4]), (0.6, 0.42, 0.55), mb.material(oc.M_CORAL_OCHRE), radius=0.42, seg=6,
                     noise=noise, disp_m=0.08, disp_period_m=0.35, weather=oc.REEF)
    oc.branch_coral(mb, place([0.0, 0.85, -0.3]), rng, oc.M_CORAL_BONE, height=0.3, depth=3, radius=0.022)
    oc.branch_coral(mb, place([1.3, 0.8, 0.6]), rng, oc.M_CORAL_ROSE, height=0.24, depth=3, radius=0.02)
    picks = rng.choice(len(tops), size=min(6, len(tops)), replace=False)
    for j in picks:
        p, _i, _s = tops[int(j)]
        if rng.random() < 0.5:
            oc.coral_knob(mb, p + np.array([0, 0.02, 0]), rng.uniform(0.05, 0.08), rng, noise,
                          oc.CORALS[int(rng.integers(0, 5))], squash=0.45)
        else:
            oc.branch_coral(mb, p, rng, oc.M_CORAL_BONE if rng.random() < 0.4 else oc.M_CORAL_OCHRE, height=0.15,
                            depth=2, radius=0.016)
    for k in range(3):
        p, _i, side = tops[int(rng.integers(0, len(tops)))]
        oc.sea_fan(mb, p - np.array([0, 0.3, 0]), rng, oc.M_CORAL_TEAL, height=0.55, width=0.45, yaw=0.3 * k + 1.2)
    for _k in range(6):
        x = rng.uniform(-6.0, 6.0)
        oc.coral_knob(mb, place([x, 0.2, rng.uniform(-0.15, 0.15)]), rng.uniform(0.06, 0.1), rng, noise, oc.M_SPONGE)
    lod = kc.MeshBuilder("wreck_ribs" + oc.LOD)
    kc.tube(lod, place(keel), 0.17, 4, lod.material(oc.M_TIMBER_TAR))
    for x in xs[::2]:
        for side in (-1.0, 1.0):
            kc.tube(lod, place(_frame_curve(float(x), side, 1.5, 4)), 0.11, 3, lod.material(oc.M_TIMBER_TAR))
    kc.tube(lod, place(stem), 0.14, 3, lod.material(oc.M_TIMBER_TAR))
    return [mb, lod]


HULLS = ((11.0, 2.4, 1.1, (0.0, 0.0), 0.0), (8.0, 1.8, 0.85, (1.5, 4.2), 0.04), (7.0, 0.9, 0.6, (-0.5, -4.4), -0.03))


def _hull(mb: kc.MeshBuilder, L: float, B: float, D: float, at, yaw: float, rng, noise, *, cols: int, rows: int) -> None:
    u = np.linspace(0.0, 1.0, cols)
    v = np.linspace(-1.08, 1.08, rows)
    U, V = np.meshgrid(u, v, indexing="ij")
    e = np.abs(2.0 * U - 1.0)
    hb = 0.5 * B * np.clip(1.0 - e ** 2.5, 0.02, 1.0) ** 0.6
    d = D * np.clip(1.0 - e ** 3.0, 0.05, 1.0) ** 0.5
    th = V * math.pi * 0.5
    X = (U - 0.5) * L
    Y = -d * np.cos(th) + 0.02 * (noise.fbm(np.stack([X, V, np.zeros_like(X)], -1) * 1.3, 2) - 0.5)
    Z = hb * np.sin(th)
    P = np.stack([X, Y, Z], axis=-1) @ kc.rot_y(yaw).T + np.array([at[0], 0.0, at[1]])
    col = np.broadcast_to(np.array([0.0, 0.0, 1.0, 0.6]), P.shape[:2] + (4,))
    uv = np.stack([U * L / 1.6, (V + 1.08) * B * 0.6], axis=-1)
    uv2 = np.broadcast_to(np.array([1.0, float(rng.random())]), P.shape[:2] + (2,))
    kc.quad_strip(mb, P, mb.material(oc.M_HULL), uv=uv, col=col, uv2=uv2, flip=True)


def build_hull_keels(seed: int = 904) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("hull_keels", seed)
    noise = kc.Noise3(rng)
    out = []
    for suffix, cols, rows in (("", 22, 11), (oc.LOD, 6, 4)):
        mb = kc.MeshBuilder("hull_keels" + suffix)
        for L, B, D, at, yaw in HULLS:
            _hull(mb, L, B, D, at, yaw, rng, noise, cols=cols, rows=rows)
        if suffix:
            out.append(mb)
            continue
        for L, _B, D, at, yaw in HULLS:
            keel = np.array([[-L * 0.45, -D * 0.7, 0.0], [0.0, -D - 0.04, 0.0], [L * 0.45, -D * 0.7, 0.0]])
            kc.tube(mb, keel @ kc.rot_y(yaw).T + np.array([at[0], 0, at[1]]), 0.07, 5, mb.material(oc.M_HULL),
                    weather=oc.DROWNED, cap_start=True, cap_end=True)
            weed = mb.material(oc.M_WEED)
            for _k in range(14):
                x = rng.uniform(-0.4, 0.4) * L
                th = rng.uniform(-0.9, 0.9)
                e = abs(2 * (x / L + 0.5) - 1)
                hb = 0.5 * _B * max(1 - e ** 2.5, 0.02) ** 0.6
                d = D * max(1 - e ** 3, 0.05) ** 0.5
                p = np.array([x, -d * math.cos(th), hb * math.sin(th)]) @ kc.rot_y(yaw).T + np.array([at[0], 0, at[1]])
                Lw = rng.uniform(0.2, 0.7)
                t = np.linspace(0, 1, 5)
                pts = p + np.stack([0.15 * t ** 2, -Lw * t, 0.05 * np.sin(t * 3)], axis=-1)
                oc.ribbon(mb, pts, np.linspace(0.06, 0.02, 5), np.array([0.0, 0.0, 1.0]), [weed],
                          variation=float(rng.random()))
        # Crossbeams over the hulls (just above the water) and the dive mooring line.
        for x in (-3.0, 0.5, 3.5):
            kc.tube(mb, np.array([[x, 0.3, -4.6], [x + 0.4, 0.32, 4.4]]), 0.09, 6, mb.material(oc.M_HULL),
                    weather=oc.DROWNED, cap_start=True, cap_end=True)
        kc.tube(mb, np.array([[2.0, -0.3, 1.1], [2.6, -2.5, 1.4], [3.4, -6.0, 1.6]]), 0.018, 5,
                mb.material(oc.M_CORD_OLD), weather=oc.CAST)
        out.append(mb)
    return out


def build_old_tin(seed: int = 905) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("old_tin", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("old_tin" + ("-lod1" if lod else ""))
        iron, brass, cord = mb.material(oc.M_IRON), mb.material(oc.M_BRASS), mb.material(oc.M_CORD_OLD)
        tin, crust = mb.material(oc.M_PATINA), mb.material(oc.M_CALCITE)
        seg = 1 if lod else 2
        kc.rounded_block(mb, (0.0, 0.15, 0.0), (0.23, 0.15, 0.15), tin, radius=0.025, seg=seg,
                         noise=None if lod else noise, disp_m=0.008, weather=oc.DROWNED, variation=0.7)
        # The lid, knocked askew: a little proud of the box, turned and tipped up at one corner.
        rot = kc.rot_y(math.radians(9.0)) @ kc.rot_z(math.radians(5.0))
        kc.rounded_block(mb, (0.02, 0.315, 0.01), (0.24, 0.018, 0.16), iron, rot=rot, radius=0.012, seg=seg,
                         weather=oc.DROWNED, variation=0.4)
        if not lod:
            # Calcite crust where it lay: a pale band round the foot and a scab on the lid.
            kc.rounded_block(mb, (0.0, 0.03, 0.0), (0.24, 0.03, 0.16), crust, radius=0.02, seg=1, noise=noise,
                             disp_m=0.01, weather=oc.REEF, variation=0.6)
            kc.rounded_block(mb, (-0.09, 0.335, -0.04), (0.08, 0.012, 0.06), crust, rot=rot, radius=0.01, seg=1,
                             noise=noise, disp_m=0.006, weather=oc.REEF, variation=0.3)
            kc.rounded_block(mb, (0.0, 0.22, 0.152), (0.035, 0.05, 0.008), brass, radius=0.006, seg=1,
                             weather=oc.CAST, variation=0.5)
            # The handle at the end, and a diver's cord through it, its tail on the floor.
            kc.tube(mb, np.array([[0.231, 0.2, -0.05], [0.27, 0.22, -0.03], [0.27, 0.22, 0.03], [0.231, 0.2, 0.05]]),
                    0.008, 5, iron, weather=oc.DROWNED)
            kc.tube(mb, np.array([[0.27, 0.22, 0.0], [0.33, 0.12, 0.04], [0.36, 0.01, 0.12], [0.5, 0.01, 0.2],
                                  [0.62, 0.01, 0.16]]), 0.009, 5, cord, weather=oc.CAST, variation=0.3)
        out.append(mb)
    return out


LIMPET_RIBS = 13


def _limpet(mb, at, radius: float, height: float, rng, lod: bool) -> None:
    """One limpet on a wall facing +Z: a ribbed cone from its scalloped foot on the wall to its worn apex, off-centre;
    ochre shell, the apex worn to bone."""
    ochre, bone = mb.material(oc.M_CORAL_OCHRE), mb.material(oc.M_CORAL_BONE)
    nr, na = (4, 10) if lod else (7, LIMPET_RIBS * 3)
    tip = np.array([rng.uniform(-0.15, 0.15) * radius, rng.uniform(0.0, 0.2) * radius, height])
    th = np.linspace(0.0, 2.0 * math.pi, na + 1)
    rib = 0.0 if lod else np.abs(np.sin(LIMPET_RIBS * th / 2.0)) ** 0.6
    phase = rng.uniform(0.0, 2.0 * math.pi)
    grid = np.zeros((nr + 1, na + 1, 3))
    for i, t in enumerate(np.linspace(0.0, 0.86, nr + 1)):
        r = radius * (1.0 - t) ** 0.8 * (1.0 + 0.1 * rib * (1.0 - t) + 0.03 * np.sin(3 * th + phase))
        c = np.asarray(at, float) + tip * t
        grid[i, :, 0] = c[0] + r * np.cos(th)
        grid[i, :, 1] = c[1] + r * np.sin(th)
        grid[i, :, 2] = c[2]
    uv = np.stack(np.meshgrid(th / (2.0 * math.pi), np.linspace(0.0, 1.0, nr + 1)), axis=-1)
    kc.quad_strip(mb, grid, ochre, uv=uv, col=(0.0, 0.0, 1.0, 0.6), uv2=(0.5, 0.5))
    # The worn apex, a bone cap over the last ring.
    apex = np.asarray(at, float) + tip * 0.86
    kc.tube(mb, np.array([apex - tip * 0.02, apex + tip * 0.14]), [radius * 0.16, radius * 0.02], 6 if lod else 10, bone,
            weather=oc.REEF, cap_end=True)


def build_shaft_limpet(seed: int = 906) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shaft_limpet", seed)
        mb = kc.MeshBuilder("shaft_limpet" + ("-lod1" if lod else ""))
        _limpet(mb, (0.0, 0.0, 0.0), 0.3, 0.3, rng, lod)
        if not lod:
            for at, r in (((0.55, 0.18, 0.0), 0.09), ((-0.48, -0.12, 0.0), 0.07), ((0.32, -0.38, 0.0), 0.06)):
                _limpet(mb, at, r, r * 0.9, rng, lod)
        out.append(mb)
    return out


TARGETS = {
    "divers_cord": build_divers_cord,
    "tether_line": build_tether_line,
    "wreck_ribs": build_wreck_ribs,
    "hull_keels": build_hull_keels,
    "old_tin": build_old_tin,
    "shaft_limpet": build_shaft_limpet,
}
