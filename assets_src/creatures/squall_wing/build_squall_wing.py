"""Squall wing, Ch8 the seawall (M3-CRE-06): docs/kb/art/creatures/act1/squall_wing.md.

blender --background --factory-startup --python assets_src/creatures/squall_wing/build_squall_wing.py -- \
    --out assets/creatures/squall_wing/squall_wing.glb

Undertow-spawn in the shape of a gull, as if the storm remembered the gull harrier and got it wrong: a gaunt, small
body on wings that are too long and too thin (2.0 m tip to tip), black wet membrane in place of feathers, the
trailing edge scalloped and torn into streamers. The body is a hollow lacquer shell; its tears show the held
spawn_wound light inside (the weak point). No eyes, only two lit slits; a long black beak a little open on the same
light. The talons hang ready for the dive.

It reuses the gull harrier's rig layout, bone names and wing poses (imported from its build module, which is not
edited), and its feather-blade primitive for the streamers. The origin is the hover point (sheet: hover 1.2 m).
The creature faces +z; its right side (-x) faces the battle camera once turned toward the party, so the right wing
carries the worst tears.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "common"))
sys.path.insert(0, str(_HERE.parent / "gull_harrier"))
import build_gull_harrier as gh  # noqa: E402
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 8231
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "deep_teal_shadow": "#0E4A55",
    "spawn_wound": "#3FE0C8",
}.items()}
BLACK = PAL["lacquer_black"]
SHEEN = ck.mix(PAL["lacquer_black"], PAL["storm_slate"], 0.35)  # the wet highlight band along the spars
WOUND = PAL["spawn_wound"]

# The left wing's arm chain (x > 0); the right mirrors it. Longer and thinner than the gull's, on a smaller body.
SHOULDER = (0.06, 0.215, 0.06)
ELBOW = (0.32, 0.285, 0.0)
WRIST = (0.56, 0.32, 0.07)
TIP = (1.0, 0.18, -0.16)
LEAD = (  # the leading edge, by x
    (0.03, 0.212, 0.075), SHOULDER, ELBOW, WRIST, (0.70, 0.305, 0.04), (0.86, 0.255, -0.06), TIP,
)
CHORD = ((0.03, 0.21), (0.32, 0.15), (0.56, 0.12), (0.80, 0.075), (1.0, 0.012))
# the rents torn through each wing: (span x of the centre, chord fraction of the centre, length m, angle from
# chordwise toward the tip in degrees, half-width m); the right wing faces the camera and is torn worst
RENTS_R = ((0.16, 0.5, 0.13, 12.0, 0.03), (0.31, 0.5, 0.14, -14.0, 0.034), (0.46, 0.5, 0.12, 22.0, 0.03),
           (0.58, 0.45, 0.09, 30.0, 0.022), (0.72, 0.4, 0.07, 38.0, 0.016))
RENTS_L = ((0.22, 0.55, 0.12, -15.0, 0.026), (0.48, 0.5, 0.10, 20.0, 0.024), (0.66, 0.45, 0.07, 30.0, 0.016))
HIP = (0.035, 0.12, -0.04)
ANKLE = (0.04, 0.07, -0.20)

# The body, a gaunt lofted spindle: (z, centre y, half-width, back height, belly depth).
STATIONS = (
    (-0.34, 0.190, 0.000, 0.000, 0.000),
    (-0.31, 0.190, 0.022, 0.018, 0.020),
    (-0.23, 0.188, 0.048, 0.034, 0.042),
    (-0.12, 0.185, 0.074, 0.050, 0.070),
    (0.00, 0.186, 0.084, 0.058, 0.084),
    (0.10, 0.192, 0.078, 0.058, 0.078),
    (0.18, 0.206, 0.058, 0.048, 0.056),
    (0.24, 0.226, 0.038, 0.038, 0.036),
    (0.30, 0.246, 0.036, 0.036, 0.034),
    (0.34, 0.258, 0.046, 0.046, 0.040),
    (0.38, 0.263, 0.049, 0.049, 0.042),
    (0.42, 0.262, 0.043, 0.043, 0.038),
    (0.45, 0.258, 0.032, 0.032, 0.028),
    (0.47, 0.256, 0.000, 0.000, 0.000),
)
# the body's tears: (z of the centre, angle about the spine in degrees from the back, +90 the left flank,
# length m, angle off the body's length in degrees, half-width m); most on the camera side (-x)
BODY_TEARS = ((-0.06, -92.0, 0.16, 12.0, 0.03), (0.08, -128.0, 0.09, -25.0, 0.018),
              (-0.18, -62.0, 0.08, 30.0, 0.015), (0.03, 100.0, 0.11, -12.0, 0.02), (-0.13, 138.0, 0.08, 18.0, 0.016))
CORE_C = (0.0, 0.186, -0.03)
CORE_R = (0.026, 0.022, 0.10)  # small in the hollow, so the tears show depth before light


def _lead(x):
    xs = [p[0] for p in LEAD]
    return np.column_stack([x, np.interp(x, xs, [p[1] for p in LEAD]), np.interp(x, xs, [p[2] for p in LEAD])])


def _drop_tris(T: np.ndarray, keep_v: np.ndarray) -> np.ndarray:
    return T[keep_v[T].all(axis=1)]


def _relax_outline(T: np.ndarray, X: np.ndarray, V: np.ndarray, nx: int, nv: int, chord, seed: int,
                   iters: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Smooths the inner outlines of a holed nx-by-nv membrane grid (vertex = row * nx + column) in the
    membrane's (span, chord-metres) plane: each outline vertex moves toward the mean of its outline neighbours
    (the grid's border stays put), then takes a small fray along the outline's normal."""
    E = np.sort(np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), axis=1)
    e, cnt = np.unique(E, axis=0, return_counts=True)
    e = e[cnt == 1]
    if len(e) == 0:
        return X, V
    row, col = np.arange(len(X)) // nx, np.arange(len(X)) % nx
    pinned = (row == 0) | (row == nv - 1) | (col == 0) | (col == nx - 1)
    q = np.column_stack([X, V * chord(X)])
    nb_sum = np.zeros_like(q)
    nb_n = np.zeros(len(X))
    for _ in range(iters):
        nb_sum[:] = 0.0
        nb_n[:] = 0.0
        for i, j in ((0, 1), (1, 0)):
            np.add.at(nb_sum, e[:, i], q[e[:, j]])
            np.add.at(nb_n, e[:, i], 1.0)
        move = (nb_n > 0) & ~pinned
        q[move] = 0.4 * q[move] + 0.6 * nb_sum[move] / nb_n[move][:, None]
    # the fray: along the outline's normal (perpendicular to the neighbours' chord), a few millimetres
    nb_sum[:] = 0.0
    for i, j, sg in ((0, 1, 1.0), (1, 0, -1.0)):
        np.add.at(nb_sum, e[:, i], sg * (q[e[:, j]] - q[e[:, i]]))
    tang = nb_sum / np.maximum(np.linalg.norm(nb_sum, axis=1, keepdims=True), 1e-9)
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    fray = 0.009 * ck.value_noise(np.column_stack([q * 40.0, np.zeros(len(q))]), seed)
    move = (nb_n > 0) & ~pinned
    q[move] += nrm[move] * fray[move, None]
    X2 = q[:, 0]
    return X2, q[:, 1] / chord(X2)


# ---------------------------------------------------------------------------------------------
# Rig: the gull harrier's layout and bone names (its clips' wing poses carry over), no twine
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("body", (0, 0.186, 0), (0, 0.186, 0.15), "root")
    rig.add("neck", (0, 0.215, 0.20), (0, 0.25, 0.31), "body")
    rig.add("head", (0, 0.258, 0.32), (0, 0.262, 0.44), "neck")
    rig.add("beak", (0, 0.245, 0.43), (0, 0.235, 0.62), "head")
    rig.add("tail", (0, 0.19, -0.28), (0, 0.19, -0.48), "body")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        m = np.array([s, 1.0, 1.0])
        rig.add(f"shoulder_{tag}", np.multiply(SHOULDER, m), np.multiply(ELBOW, m), "body")
        rig.add(f"elbow_{tag}", np.multiply(ELBOW, m), np.multiply(WRIST, m), f"shoulder_{tag}")
        rig.add(f"wrist_{tag}", np.multiply(WRIST, m), np.multiply(TIP, m), f"elbow_{tag}")
        rig.add(f"leg_{tag}", np.multiply(HIP, m), np.multiply(ANKLE, m), "body")
    return rig


# ---------------------------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------------------------
def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The hollow shell: a lacquer loft with ragged tears through to the lit core."""
    segs = 22
    zs = np.concatenate([np.linspace(-0.34, 0.18, 14), np.linspace(0.21, 0.47, 9)])
    cols = list(zip(*STATIONS))

    def loft(zv, av):
        """The shell at length z and angle a about the spine (0 on the back, +pi/2 on the left flank)."""
        cy, rx, top, bot = (np.interp(zv, cols[0], cols[k]) for k in (1, 2, 3, 4))
        sv, cv = np.sin(av), np.cos(av)
        ry = np.where(cv >= 0.0, top, bot)
        e = 0.9
        return (np.column_stack([rx * np.sign(sv) * np.abs(sv) ** e, cy + ry * np.sign(cv) * np.abs(cv) ** e, zv]),
                np.column_stack([np.zeros(len(zv)), cy, zv]))

    Z = np.repeat(zs, segs)
    A = np.tile(np.arange(segs) * (2.0 * math.pi / segs), len(zs))
    T = ck.grid_tris(len(zs), segs, True)
    # the tears: ragged lens-shaped rents ripped along the ribs, through to the hollow (most on the camera side,
    # -x). Grid vertices inside a rent are pushed out onto its outline, and the triangles inside it dropped, so the
    # coarse loft still cuts a clean torn shape. Measured on the surface: z, and arc length about the spine.
    R0 = 0.075
    Zn, An = Z.copy(), A.copy()
    tear_d = np.full(len(Z), 9.0)
    rents = []
    for k, (zc, a_deg, length, ang, hw) in enumerate(BODY_TEARS):
        ac = math.radians(a_deg)
        dr = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])  # 0 deg: along the body
        rents.append((zc, ac, length, dr, hw, k))

    def rent_frame(zq, aq, zc, ac, length, dr):
        q = np.column_stack([zq - zc, ((aq - ac + math.pi) % (2.0 * math.pi) - math.pi) * R0])
        t = np.clip((q @ dr) / length + 0.5, 0.0, 1.0)
        foot = (t[:, None] - 0.5) * (length * dr)
        return q, t, foot

    for zc, ac, length, dr, hw, k in rents:
        q, t, foot = rent_frame(Zn, An, zc, ac, length, dr)
        dvec = q - foot
        d = np.linalg.norm(dvec, axis=1)
        perp = np.array([-dr[1], dr[0]])
        sgn = np.where(dvec @ perp >= 0.0, 1.0, -1.0)
        jag = ck.value_noise(np.column_stack([t * 8.0, sgn * 3.0, np.full(len(t), float(k))]), SEED + 60 + k)
        w = hw * np.sin(math.pi * t) ** 0.55 * (1.0 + 0.5 * jag) + 1e-4
        inside = d < w
        dirn = np.where((d > 1e-6)[:, None], dvec / np.maximum(d, 1e-9)[:, None], sgn[:, None] * perp)
        qn = np.where(inside[:, None], foot + dirn * w[:, None], q)
        Zn = zc + qn[:, 0]
        An = ac + qn[:, 1] / R0
        tear_d = np.minimum(tear_d, np.linalg.norm(qn - foot, axis=1) / w)
    P, C = loft(Zn, An)
    T = gh._outward(P, T, C)
    radial = P - C
    nrm = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    # ridged like a keel and ribs showing through: the storm's idea of feathers
    rib = np.abs(np.sin(P[:, 2] * 70.0)) ** 6 * ck.smoothstep(-0.25, 0.15, P[:, 2]) * (1.0 - ck.smoothstep(0.15, 0.2, P[:, 2]))
    P = P + nrm * (0.004 * rib + ck.fbm(P * 22.0, SEED + 1) * 0.004)[:, None]
    # drop the triangles inside a rent: centroid (on the rest grid) inside an outline, or all corners on one
    tri_in = (tear_d < 1.02)[T].all(axis=1)
    zc_t, ac_t = Z[T].mean(axis=1), np.angle(np.exp(1j * A[T]).mean(axis=1))
    for zc, ac, length, dr, hw, k in rents:
        q, t, foot = rent_frame(zc_t, ac_t, zc, ac, length, dr)
        tri_in |= np.linalg.norm(q - foot, axis=1) < hw * np.sin(math.pi * t) ** 0.55
    T = T[~tri_in]
    # a rent, not a patch: the lips curl inward and darken (no glow on the shell itself, so the hole reads as a
    # hole onto the dark inside); the light is a thin lit wall around each hole (the lip strip below)
    lip = ck.smoothstep(1.8, 1.0, tear_d)
    rag = ck.fbm(P * 60.0, SEED + 4)
    P = P - nrm * (0.006 * lip * (0.6 + 0.4 * rag))[:, None]
    col = ck.mix(BLACK, PAL["abyss_navy"], (0.35 * ck.smoothstep(0.0, -0.8, nrm[:, 1]))[:, None])
    col = ck.mix(col, SHEEN, (0.5 * rib * (1.0 - lip))[:, None])
    col = col * (1.0 - 0.5 * lip)[:, None]
    # the holes' outlines: edges used by one kept triangle (the loft's ends close on degenerate rows)
    E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    opp = np.concatenate([T[:, 2], T[:, 0], T[:, 1]])
    key = np.sort(E, axis=1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    open_e = (cnt[inv.reshape(-1)] == 1) & (np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1) > 1e-6)
    E, opp = E[open_e], opp[open_e]
    J_b, J_n, J_h, J_t = (rig.index(n) for n in ("body", "neck", "head", "tail"))

    def bones(Pv):
        zz = Pv[:, 2]
        n = len(Pv)
        J = np.tile([J_b, J_b], (n, 1))
        W = np.tile([1.0, 0.0], (n, 1))
        tail = zz < -0.22
        wt = ck.smoothstep(-0.22, -0.34, zz) * 0.7
        J[tail, 1] = J_t
        W[tail] = np.column_stack([1.0 - wt, wt])[tail]
        neck = (zz >= 0.16) & (zz < 0.30)
        wn = ck.smoothstep(0.16, 0.30, zz)
        J[neck, 1] = J_n
        W[neck] = np.column_stack([1.0 - wn, wn])[neck]
        head = zz >= 0.30
        wh = ck.smoothstep(0.30, 0.36, zz)
        J[head] = (J_n, J_h)
        W[head] = np.column_stack([1.0 - wh, wh])[head]
        return J, W

    ck.finish(mesh, P, T, "shell", col, bones, wet=1.0, cavity=0.3 * rib + 0.6 * lip)

    # the lit lip: a thin wall down from each hole's edge into the hollow, facing across the hole, glowing where
    # it meets the shell and going dark with depth, so a tear reads as a lit rim around a dark opening
    n_e = len(E)
    a, b = P[E[:, 0]], P[E[:, 1]]
    na, nb = nrm[E[:, 0]], nrm[E[:, 1]]
    across = (a + b) * 0.5 - P[opp]  # from the shell's side of the edge into the hole
    # two bands down the wall: a thin lit one at the lip, then the dark of the hollow
    for d0, d1, h0, h1 in ((0.0, 0.0035, 1.0, 0.7), (0.0035, 0.02, 0.15, 0.0)):
        Pl = np.vstack([a - na * d0, b - nb * d0, b - nb * d1, a - na * d1])
        ar = np.arange(n_e)
        Tl = np.vstack([np.column_stack([ar, ar + n_e, ar + 2 * n_e]),
                        np.column_stack([ar, ar + 2 * n_e, ar + 3 * n_e])])
        fn = np.cross(Pl[Tl[:, 1]] - Pl[Tl[:, 0]], Pl[Tl[:, 2]] - Pl[Tl[:, 0]])
        Tl = np.where(((fn * np.tile(across, (2, 1))).sum(axis=1) >= 0.0)[:, None], Tl, Tl[:, ::-1])
        hot = np.repeat([h0, h0, h1, h1], n_e)
        cl = ck.mix(PAL["abyss_navy"] * 0.4, WOUND * 0.6, hot[:, None])
        ck.finish(mesh, Pl, Tl, "shell", cl, bones, wet=0.5 * hot, cavity=1.0 - hot, emission=0.9 * hot)

    # the hollow: an inner wall well inside the shell, wound inward, so a tear shows the dark far side of the
    # cavity (its near side faces away and is culled) with the held light hanging in the depth
    zi = np.linspace(-0.29, 0.19, 9)
    segi = 12
    ai = np.arange(segi) * (2.0 * math.pi / segi)
    si, ci = np.sin(ai), np.cos(ai)
    rows, centre = [], []
    for z in zi:
        cy, rx, top, bot = (float(np.interp(z, cols[0], cols[k])) for k in (1, 2, 3, 4))
        ry = np.where(ci >= 0.0, top, bot) * 0.72
        rows.append(np.column_stack([0.72 * rx * si, cy + ry * ci, np.full(segi, z)]))
        centre.append(np.tile([0.0, cy, z], (segi, 1)))
    Pi, Ci = np.vstack(rows), np.vstack(centre)
    Ti = ck.flip(gh._outward(Pi, ck.grid_tris(len(zi), segi, True), Ci))
    depth = ck.smoothstep(-0.29, -0.05, Pi[:, 2]) * (1.0 - ck.smoothstep(0.05, 0.19, Pi[:, 2]))
    ci_col = ck.mix(PAL["abyss_navy"] * 0.3, PAL["deep_teal_shadow"] * 0.35, (0.6 * depth)[:, None])
    ck.finish(mesh, Pi, Ti, "shell", ci_col, bones, cavity=1.0)

    # the held light inside: what the tears show (the weak point), hanging in the dark of the hollow
    Pc, Tc = gh._ellipsoid(CORE_C, CORE_R, 8, 14)
    glow = ck.smoothstep(0.05, 0.4, ck.fbm(Pc * 30.0, SEED + 3))  # dark, with a few hot seams
    ck.finish(mesh, Pc, Tc, "core", ck.mix(PAL["deep_teal_shadow"] * 0.4, WOUND * 0.8, glow[:, None]), J_b, wet=1.0,
              emission=0.06 + 0.6 * glow)
    # two lit slits where a gull's eyes would be
    for sx in (1.0, -1.0):
        Pe, Te = gh._ellipsoid((0.0, 0.0, 0.0), (0.006, 0.0045, 0.017), 4, 8)
        Pe = ck.transform(Pe, ck.euler(0.0, sx * 14.0, -sx * 18.0), (sx * 0.044, 0.272, 0.395))
        ck.finish(mesh, Pe, Te, "core", WOUND * 0.8, J_h, emission=1.0)


def beak(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Too long and a little open: two black blades with a hook, the light in the gape."""
    ih, ij = rig.index("head"), rig.index("beak")
    s = np.linspace(0.0, 1.0, 10)
    z = 0.43 + 0.20 * s
    y = 0.268 + 0.004 * np.sin(math.pi * s) - 0.016 * s * s
    th = np.radians(np.linspace(30.0, 150.0, 4))
    rc = 0.016
    z = np.concatenate([z, z[-1] + rc * np.sin(th)])
    y = np.concatenate([y, y[-1] - rc * (1.0 - np.cos(th))])
    rad = np.concatenate([np.interp(s, (0.0, 0.4, 1.0), (0.026, 0.017, 0.010)), np.linspace(0.008, 0.002, 4)])
    P, T = gh._tube(np.column_stack([np.zeros(len(z)), y, z]), rad, 8, squash=0.55)
    edge = ck.smoothstep(0.255, 0.246, P[:, 1])
    ck.finish(mesh, P, T, "shell", ck.mix(BLACK, SHEEN, (0.6 * edge)[:, None]), ih, wet=1.0)
    s = np.linspace(0.0, 1.0, 8)
    z = 0.435 + 0.17 * s
    y = 0.245 - 0.022 * s
    P, T = gh._tube(np.column_stack([np.zeros(len(z)), y, z]), np.interp(s, (0.0, 0.7, 1.0), (0.018, 0.009, 0.002)),
                    8, squash=0.7)
    ck.finish(mesh, P, T, "shell", BLACK, ij, wet=1.0)
    # the gape's light
    Pg, Tg = gh._ellipsoid((0.0, 0.252, 0.47), (0.012, 0.008, 0.05), 4, 8)
    ck.finish(mesh, Pg, Tg, "core", WOUND * 0.7, ij, emission=0.9)


def wing(mesh: ck.Mesh, rig: ck.Rig, side: float) -> None:
    tag = "l" if side > 0 else "r"
    parts = []  # (P, T, colour, bone, wet, cavity, emission, uv, N)
    # the membrane: rows back from the leading edge, the trailing edge scalloped and torn
    NX, NV = 34, 9
    x = np.linspace(0.03, 1.0, NX)
    chord_x = [p[0] for p in CHORD]
    chord_c = [p[1] for p in CHORD]
    scallop = np.abs(np.sin(math.pi * (x - 0.03) / 0.115)) ** 0.6
    rag = 0.30 * scallop * ck.smoothstep(0.12, 0.3, x) + 0.18 * ck.fbm(np.column_stack([x * 9.0, x * 3.0, x]), SEED + 11 + int(side > 0))
    v_end = np.clip(1.0 - rag, 0.45, 1.0)

    def membrane(xs, vk):
        """A point on the membrane at span xs and chord fraction vk (from the leading edge)."""
        ch = np.interp(xs, chord_x, chord_c)
        bk = np.column_stack([0.35 * ck.smoothstep(0.5, 1.0, xs), -0.12 * ck.smoothstep(0.6, 1.0, xs),
                              -np.ones(len(xs))])
        bk /= np.linalg.norm(bk, axis=1, keepdims=True)
        cup = 0.022 * np.sin(math.pi * vk) * (ch / 0.2)
        return _lead(xs) + bk * (vk * ch)[:, None] + np.column_stack([np.zeros(len(xs)), cup, np.zeros(len(xs))])

    X = np.tile(x, NV)
    V = np.concatenate([(k / (NV - 1)) * v_end for k in range(NV)])
    T = ck.grid_tris(NV, NX, False)
    # rents: ragged lens-shaped holes torn right through the membrane between spar and trailing edge. Vertices
    # that fall inside a rent are pushed out onto its outline (so a coarse grid still cuts a clean torn shape),
    # then the triangles inside it are dropped; the lips are lifted and twisted a little apart
    rent_d = np.full(len(X), 9.0)  # distance to the nearest rent's outline, in its half-widths (<1 inside)
    lift = np.zeros(len(X))
    Xn, Vn = X.copy(), V.copy()
    for k, (xc, vc, length, ang, hw) in enumerate(RENTS_R if side < 0 else RENTS_L):
        q = np.column_stack([Xn, Vn * np.interp(Xn, chord_x, chord_c)])
        cc = np.array([xc, vc * float(np.interp(xc, chord_x, chord_c))])
        dr = np.array([math.sin(math.radians(ang)), math.cos(math.radians(ang))])
        a = cc - 0.5 * length * dr
        t = np.clip(((q - a) @ dr) / length, 0.0, 1.0)
        foot = a + t[:, None] * (length * dr)
        dvec = q - foot
        d = np.linalg.norm(dvec, axis=1)
        jag = ck.value_noise(np.column_stack([t * 7.0, np.sign(dvec @ np.array([dr[1], -dr[0]])) * 3.0,
                                              np.full(len(t), float(k))]), SEED + 50 + k)
        w = hw * np.sin(math.pi * t) ** 0.55 * (1.0 + 0.45 * jag) + 1e-4
        inside = d < w
        perp = np.array([dr[1], -dr[0]])
        dirn = np.where((d > 1e-6)[:, None], dvec / np.maximum(d, 1e-9)[:, None],
                        np.where(((q - cc) @ perp >= 0.0)[:, None], perp, -perp))
        qn = np.where(inside[:, None], foot + dirn * w[:, None], q)
        Xn = qn[:, 0]
        Vn = qn[:, 1] / np.interp(Xn, chord_x, chord_c)
        dd = np.linalg.norm(qn - foot, axis=1) / w
        side_s = np.sign(dirn @ perp)
        closer = dd < rent_d
        lift = np.where(closer, side_s * np.sin(math.pi * t) * ck.smoothstep(2.0, 1.0, dd), lift)
        rent_d = np.minimum(rent_d, dd)
    def place(Xq, Vq):
        Pq = membrane(Xq, Vq)
        jit = ck.fbm(Pq * 40.0, SEED + 31 + int(side > 0))
        return Pq + np.column_stack([np.zeros(len(Pq)), 0.010 * lift + 0.004 * jit * ck.smoothstep(2.0, 1.0, rent_d),
                                     np.zeros(len(Pq))])

    P = place(Xn, Vn)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if fn[:, 1].sum() < 0:
        T = ck.flip(T)
    # which triangles lie inside a rent: their centroid in the rest grid falls inside an outline
    Xc, Vc = X[T].mean(axis=1), V[T].mean(axis=1)
    qc = np.column_stack([Xc, Vc * np.interp(Xc, chord_x, chord_c)])
    tri_in = np.zeros(len(T), dtype=bool)
    for xc, vc, length, ang, hw in RENTS_R if side < 0 else RENTS_L:
        cc = np.array([xc, vc * float(np.interp(xc, chord_x, chord_c))])
        dr = np.array([math.sin(math.radians(ang)), math.cos(math.radians(ang))])
        a = cc - 0.5 * length * dr
        t = np.clip(((qc - a) @ dr) / length, 0.0, 1.0)
        d = np.linalg.norm(qc - (a + t[:, None] * (length * dr)), axis=1)
        tri_in |= d < hw * np.sin(math.pi * t) ** 0.55
    tri_in |= (rent_d < 1.02)[T].all(axis=1)
    # older holes: ragged tears through the membrane, away from the leading edge
    tear = ck.fbm(np.column_stack([P[:, 0] * 7.0, P[:, 2] * 9.0, P[:, 1] * 3.0]), SEED + (21 if side > 0 else 37))
    tear = tear * ck.smoothstep(0.3, 0.6, V) * ck.smoothstep(0.12, 0.25, X)
    cut = 0.17 if side > 0 else 0.13
    T = T[(tear[T].mean(axis=1) < cut) & ~tri_in]
    # the holes' outlines follow the grid in steps: walk each outline (edges of one kept triangle, the grid's own
    # border pinned) and relax it toward its neighbours along the outline, then fray it a little, so a rent's edge
    # runs as a torn line and not a saw
    Xn, Vn = _relax_outline(T, Xn, Vn, NX, NV, lambda xq: np.interp(xq, chord_x, chord_c), SEED + 60 + int(side > 0))
    P = place(Xn, Vn)
    rim = np.maximum(ck.smoothstep(cut - 0.03, cut, tear), ck.smoothstep(1.35, 1.0, rent_d))
    X, V = Xn, Vn
    xi = np.clip(np.searchsorted(x, X), 0, NX - 1)
    vein = 1.0 - scallop[xi]  # the membrane gathers into ridges between the scallops
    col = ck.mix(BLACK, PAL["abyss_navy"], (0.3 * V)[:, None])
    col = ck.mix(col, SHEEN, (0.45 * ck.smoothstep(0.12, 0.0, V) + 0.25 * vein)[:, None])
    # the lips stay black and wet (a wet catch-light, no glow): the sky through the hole is the read
    col = ck.mix(col, SHEEN, (0.35 * rim)[:, None])
    edge = np.zeros_like(rim)
    uv = np.column_stack([X * 3.0, V * 0.6])
    for up in (True, False):
        Tw = T if up else ck.flip(T)
        off = np.array([0.0, 0.0018 if up else -0.0018, 0.0])
        parts.append((P + off, Tw, col if up else col * 0.9, "chain", 1.0, 0.35 * vein, edge * 0.8, uv, None))

    # the arm: a thin black spar along the leading edge, out to the tip
    xs = np.linspace(0.02, 1.0, 22)
    path = _lead(xs) + np.array([0.0, 0.004, 0.0])
    Ps, Ts = gh._tube(path, np.interp(xs, (0.02, 0.32, 0.56, 1.0), (0.018, 0.012, 0.010, 0.003)), 7)
    knuckle = np.exp(-((Ps[:, 0] - ELBOW[0]) / 0.02) ** 2) + np.exp(-((Ps[:, 0] - WRIST[0]) / 0.02) ** 2)
    parts.append((Ps, Ts, ck.mix(BLACK, SHEEN, (0.3 + 0.4 * knuckle)[:, None]), "chain", 1.0, 0.2, 0.0, None, None))

    # the hand's streamers: what the storm made of the primaries, long, thin and frayed
    for i, (x0, phi, L, wdt) in enumerate(((0.60, 28.0, 0.30, 0.040), (0.70, 40.0, 0.38, 0.036),
                                           (0.80, 52.0, 0.42, 0.030), (0.90, 66.0, 0.36, 0.024))):
        root = _lead(np.array([x0]))[0] + np.array([0.0, -0.002, -0.02])
        ph = math.radians(phi)
        d = gh._unit((math.sin(ph), -0.18, -math.cos(ph)))
        Pb, Nb, Tb, info = gh.blade(root, d, L, wdt, K=8, lead=0.5, thick=0.002, cup=0.1, tip_start=0.45,
                                    cut=(0.25, 0.4), floor=0.3, ruffle=(0.006, 3.0), wave=(0.01, 1.2),
                                    seed=200 + i + (0 if side > 0 else 10))
        t = info["t"]
        c = ck.mix(BLACK, PAL["abyss_navy"], (0.4 * t)[:, None])
        parts.append((Pb, Tb, c, "wrist", 1.0, 0.2 * (1.0 - t), 0.0, info["uv"], Nb))

    m = np.array([side, 1.0, 1.0])
    chain = rig.chain([f"shoulder_{tag}", f"elbow_{tag}", f"wrist_{tag}"],
                      [np.multiply(p, m) for p in (SHOULDER, ELBOW, WRIST, TIP)])
    for P_, T_, col_, bone, wet, cav, em, uv_, N_ in parts:
        if side < 0:
            P_, N_, T_ = gh._mirror(P_, N_, T_)
        b = chain if bone == "chain" else rig.index(f"{bone}_{tag}")
        slot = "membrane"
        ck.finish(mesh, P_, T_, slot, col_, b, wet=wet, cavity=cav, emission=em, uv=uv_, N=N_)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Five frayed membrane streamers where a gull's fanned tail would be."""
    it = rig.index("tail")
    for i, (phi, L) in enumerate(((-26.0, 0.30), (-12.0, 0.40), (0.0, 0.46), (13.0, 0.36), (27.0, 0.27))):
        ph = math.radians(phi)
        root = (0.012 * i - 0.024, 0.19, -0.30)
        P, N, T, info = gh.blade(root, (math.sin(ph), -0.05, -math.cos(ph)), L, 0.04, K=7, lead=0.5, thick=0.002,
                                 tip_start=0.4, cut=(0.3, 0.2), floor=0.3, ruffle=(0.005, 3.0), seed=240 + i)
        c = ck.mix(BLACK, PAL["abyss_navy"], (0.35 * info["t"])[:, None])
        ck.finish(mesh, P, T, "membrane", c, it, wet=1.0, uv=info["uv"], N=N)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Thin black legs and long hooked talons, held ready."""
    for sx, tag in ((1.0, "l"), (-1.0, "r")):
        il = rig.index(f"leg_{tag}")
        m = np.array([sx, 1.0, 1.0])
        a = np.multiply(HIP, m)
        b = np.multiply(ANKLE, m)
        P, T = gh._tube(ck.bezier([a, (a + b) / 2 + (0, -0.01, 0), b], 5), np.linspace(0.011, 0.007, 5), 6)
        ck.finish(mesh, P, T, "shell", BLACK, il, wet=1.0)
        for k, spread in enumerate((-24.0, 0.0, 24.0)):
            d = ck.rot_y(spread * sx) @ gh._unit((0.0, -0.35, -1.0))
            p1 = b + d * 0.06
            claw = ck.bezier([b, p1, p1 + d * 0.035 + (0, -0.02, 0), p1 + d * 0.03 + (0, -0.05, 0.012)], 7)
            P, T = gh._tube(claw, np.linspace(0.006, 0.0012, 7), 5, cap_start=False)
            ck.finish(mesh, P, T, "shell", ck.mix(BLACK, SHEEN, 0.4), il, wet=1.0)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("squall_wing")
    body(mesh, rig)
    beak(mesh, rig)
    wing(mesh, rig, 1.0)
    wing(mesh, rig, -1.0)
    tail(mesh, rig)
    legs(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips: the gull harrier's wing poses, played stiffer (held keys, snaps instead of follow-through)
# ---------------------------------------------------------------------------------------------
HOVER = 1.2  # the sheet's hover height: the KO falls this far
W_UP, W_DOWN, W_GLIDE, W_HALF, W_TUCK, W_FLARE, W_SPREAD = (gh.W_UP, gh.W_DOWN, gh.W_GLIDE, gh.W_HALF, gh.W_TUCK,
                                                           gh.W_FLARE, gh.W_SPREAD)
W_STOOP = ((0, 52, 18), (0, -55, 0), (0, 70, -6))  # folded hard back for the stoop
W_REACH = ((-10, 10, 34), (0, 0, -8), (0, -8, 16))  # thrown up and back over the strike


def build_clips() -> list[ck.Clip]:
    wk = gh._wing_key
    idle = ck.Clip("idle", 1.4, loop=True)
    # a beat that stops dead at the top and the bottom, then a glide with a twitch
    for t, pose, bob, pitch, head in ((0.0, W_UP, 0.0, 0.0, 0.0), (0.14, W_UP, 0.0, 0.0, 0.0),
                                      (0.36, W_DOWN, 0.07, -3.0, 0.0), (0.5, W_DOWN, 0.07, -3.0, 14.0),
                                      (0.8, W_GLIDE, 0.04, -1.0, 14.0), (0.98, W_GLIDE, 0.02, 1.0, -8.0),
                                      (1.18, W_GLIDE, 0.0, 1.0, -8.0), (1.4, W_UP, 0.0, 0.0, 0.0)):
        wk(idle, t, pose)
        idle.key("body", t, (pitch, 0, 0), (0, bob, 0))
        idle.key("neck", t, (-pitch, 0, 0), (0, -0.8 * bob, 0))
        idle.key("head", t, (0, 0, head))  # the head cocks sideways in jerks, listening
        idle.key("tail", t, (-3.0 * pitch, 0, 0))

    attack = ck.Clip("attack", 1.4)  # a steep stoop on a target below it, talons and beak reaching down
    for t, pose, root, bodyr, leg, neck, beak in (
        (0.0, W_GLIDE, (0, 0, 0), (0, 0, 0), 0, 0, 0),
        (0.14, W_DOWN, (0, 0.26, -0.06), (-8, 0, 0), 0, 6, 0),  # the tell: a hard climb, two beats
        (0.28, W_UP, (0, 0.46, -0.10), (-10, 0, 0), 0, 8, 0),
        (0.38, W_UP, (0, 0.50, -0.10), (-4, 0, 0), 0, 0, 0),  # a held beat at the top
        (0.48, W_STOOP, (0, 0.30, 0.10), (52, 0, 0), -40, 10, 10),  # it folds and drops head first
        (0.62, W_STOOP, (0, -0.55, 0.42), (62, 0, 0), -110, 14, 30),  # contact: talons and beak forward and down
        (0.72, W_REACH, (0, -0.72, 0.52), (38, 0, 0), -130, 6, 34),
        (0.86, W_REACH, (0, -0.62, 0.50), (20, 0, 0), -90, 0, 10),
        (1.04, W_DOWN, (0, -0.14, 0.26), (-8, 0, 0), -20, 0, 0),
        (1.2, W_UP, (0, 0.02, 0.06), (-4, 0, 0), -4, 0, 0),
        (1.4, W_GLIDE, (0, 0, 0), (0, 0, 0), 0, 0, 0),
    ):
        wk(attack, t, pose)
        attack.key("root", t, loc=root)
        attack.key("body", t, bodyr)
        attack.key("neck", t, (neck, 0, 0))
        attack.key("beak", t, (beak, 0, 0))
        attack.key("leg_l", t, (leg, 0, 0))
        attack.key("leg_r", t, (leg * 0.92, 0, 0))
        attack.key("tail", t, (-0.3 * bodyr[0], 0, 0))

    cast = ck.Clip("cast", 1.2)  # it spreads and holds, beak wide, and the storm answers (VFX)
    for t, pose, rear, root, beak in (
        (0.0, W_GLIDE, 0, (0, 0, 0), 0),
        (0.3, W_SPREAD, -34, (0, 0.14, -0.06), 40),
        (0.62, W_SPREAD, -34, (0, 0.14, -0.06), 40),  # held stiff, no settle
        (0.8, W_SPREAD, -30, (0, 0.12, -0.05), 34),
        (1.2, W_GLIDE, 0, (0, 0, 0), 0),
    ):
        wk(cast, t, pose)
        cast.key("body", t, (rear, 0, 0))
        cast.key("root", t, loc=root)
        cast.key("neck", t, (0.4 * rear, 0, 0))
        cast.key("beak", t, (beak, 0, 0))
        cast.key("tail", t, (0.6 * rear, 0, 0))
        cast.key("leg_l", t, (0.5 * rear, 0, 0))
        cast.key("leg_r", t, (0.5 * rear, 0, 0))

    hit = ck.Clip("hit", 0.6)
    buckle = ((6, 30, -24), (0, -38, 14), (0, 44, -26))
    flail = ((-6, 0, 46), (0, 0, -8), (0, -4, 18))
    for t, l_pose, r_pose, root, roll, neck in (
        (0.0, W_GLIDE, W_GLIDE, (0, 0, 0), 0, 0),
        (0.06, flail, buckle, (0, -0.10, -0.05), 18, -20),
        (0.26, flail, buckle, (0, -0.24, -0.06), 22, -8),
        (0.42, W_DOWN, W_DOWN, (0, -0.10, -0.02), 6, 0),
        (0.6, W_GLIDE, W_GLIDE, (0, 0, 0), 0, 0),
    ):
        wk(hit, t, l_pose, ("l",))
        wk(hit, t, r_pose, ("r",))
        hit.key("root", t, loc=root)
        hit.key("body", t, (-0.3 * roll, 0, roll))
        hit.key("neck", t, (neck, 0, -0.5 * roll))

    ko = ck.Clip("ko", 1.4)  # the light goes out of it and it falls like a torn kite
    spread = ((0, -6, 30), (0, -6, 0), (0, 14, -36))
    crumple = ((0, 40, -21), (0, -45, 0), (0, 62, -12))
    for t, l_pose, r_pose, drop, bodyr, neck in (
        (0.0, W_GLIDE, W_GLIDE, 0.0, (0, 0, 0), 0),
        (0.14, W_UP, W_UP, -0.04, (-12, 0, 0), -26),
        (0.45, W_HALF, W_UP, 0.22, (16, 0, 24), -10),  # one wing goes slack first: it slews
        (0.8, W_TUCK, W_HALF, 0.75, (30, 0, 40), 12),
        (1.02, W_HALF, crumple, HOVER, (14, 0, 12), 18),
        (1.2, spread, crumple, HOVER, (8, 0, 8), 22),
        (1.4, spread, crumple, HOVER, (8, 0, 8), 22),
    ):
        wk(ko, t, l_pose, ("l",))
        wk(ko, t, r_pose, ("r",))
        ko.key("root", t, loc=(0, -drop, 0))
        ko.key("body", t, bodyr, (0, -0.1 * min(drop / HOVER, 1.0), 0))
        ko.key("neck", t, (neck, 0, 0))
        ko.key("tail", t, (min(drop, 1.0) * 12.0, 0, 0))
    for t, r in ((0.0, 0), (0.14, 24), (0.6, 8), (1.4, 14)):
        ko.key("beak", t, (r, 0, 0))
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py), measured with the hover (the floor is y -HOVER here): a wing
# the heavier, mirrored recoil (hit_b) would flail down through the floor turns up at the shoulder; as it lands the
# neck holds the beak off the floor, and the body settles onto it, not through it.
GROUNDED_LIMBS = [(f"shoulder_{tag}", 2, s, 45.0, ("hit", "hit_b")) for tag, s in (("l", 1.0), ("r", -1.0))] + [
    ("neck", 0, -1.0, 40.0, ("ko",)), ("body", gr.LIFT, 1.0, 0.1, ("ko",))]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS, floor=-HOVER)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "squall_wing"})
    print(f"squall_wing: {info}")


if __name__ == "__main__":
    main()
