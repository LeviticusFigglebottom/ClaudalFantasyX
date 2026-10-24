"""Lantern eel battle model (M2-CRE-05): docs/kb/art/creatures/lantern_eel.md.

blender --background --factory-startup --python assets_src/creatures/lantern_eel/build_lantern_eel.py -- \
    --out assets/creatures/lantern_eel/lantern_eel.glb

A moray-like eel risen in a tall S out of the shallows, its head hooked toward the party like a question mark. A
curved stalk from its brow holds a six-ribbed bone cage with a cold, steady salt-glass light inside: from a distance a
lamp-diver's lamp, up close the wrong colour. A translucent dorsal frill runs its whole length, a sand-pale belly line
traces the curve, a row of faint photophores runs along each flank, and a spawn_wound gill slit glows behind the jaw.

The body is one sweep along a Catmull-Rom spine (an oval section, taller than wide), skinned along a chain of nine
spine bones with ck.Rig.chain so it bends without breaking.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 5209
PAL = {k: ck.hexrgb(v) for k, v in {
    "deep_teal_shadow": "#0E4A55", "abyss_navy": "#061A2B", "sand_wet": "#B59D74", "sea_glow": "#1C6B78",
    "lagoon_teal": "#1FA3A6", "bone": "#E6DAC0", "salt_glass": "#BFE6E0", "spawn_wound": "#3FE0C8",
    "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E", "coral_stone_weathered": "#B9AE98",
}.items()}

# The spine's control points (x, y, z), tail to snout; the spline parameter tau runs 0 .. len - 1 through them.
# Underground tail, a low run along the ground, the lower curve bowing toward the party (+z), the upper curve
# leaning back, the neck turning forward, the head (tau 10 .. 12) hooked over toward the party.
CTRL = np.array([
    (0.00, -0.55, -0.74),
    (0.03, -0.16, -0.64),
    (0.06, 0.08, -0.48),
    (0.07, 0.16, -0.24),
    (0.06, 0.34, 0.04),
    (0.03, 0.70, 0.17),
    (-0.02, 1.06, 0.06),
    (-0.05, 1.38, -0.10),
    (-0.04, 1.66, -0.10),
    (-0.01, 1.87, 0.02),
    (0.00, 1.97, 0.26),
    (0.00, 1.96, 0.52),
    (0.00, 1.90, 0.75),
])
TAU_END = float(len(CTRL) - 1)
# Section half-extents along tau: dorsal (du), ventral (dv) and lateral (w). In the head (tau >= 10) the ventral
# extent is the upper lip; the lower jaw is a separate part below it.
SEC_TAU = [0.0, 1.0, 2.0, 3.0, 4.0, 5.5, 7.0, 8.0, 9.0, 9.6, 10.12, 10.45, 10.6, 11.2, 11.7, 12.0]
SEC_DU = [0.12, 0.125, 0.13, 0.138, 0.15, 0.165, 0.16, 0.148, 0.138, 0.14, 0.15, 0.145, 0.128, 0.098, 0.066, 0.024]
SEC_DV = [0.12, 0.125, 0.13, 0.138, 0.15, 0.165, 0.16, 0.148, 0.14, 0.145, 0.145, 0.046, 0.042, 0.033, 0.026, 0.015]
SEC_W = [0.085, 0.09, 0.094, 0.098, 0.10, 0.108, 0.104, 0.098, 0.096, 0.102, 0.112, 0.11, 0.098, 0.076, 0.052, 0.025]
SEGS = 20  # around the body
J_TAU = [1.0, 2.1, 3.2, 4.1, 5.0, 5.9, 6.8, 7.7, 8.6, 9.6]  # spine joints: nine bones between them
SPINE = [f"spine_{i}" for i in range(9)]
GILL_TAU = 9.42
HINGE_TAU = 10.3
JAW_ROOT_TAU = 10.16
LIP_TAU = [10.0, 10.6, 11.2, 11.7, 12.0]
LIP_DV = [0.05, 0.042, 0.033, 0.026, 0.015]
BROW_TAU = 10.55
SIDE_CAM = -1.0  # the flank the battle camera sees once the stage turns the eel toward the party (-x)


# ---------------------------------------------------------------------------------------------
# The spine
# ---------------------------------------------------------------------------------------------
def spine(tau) -> np.ndarray:
    """Points on the uniform Catmull-Rom spline through CTRL at parameter(s) tau."""
    tau = np.atleast_1d(np.asarray(tau, dtype=np.float64))
    n = len(CTRL)
    ext = np.vstack([2 * CTRL[0] - CTRL[1], CTRL, 2 * CTRL[-1] - CTRL[-2]])
    i = np.clip(np.floor(tau).astype(np.int64), 0, n - 2)
    t = (tau - i)[:, None]
    p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def frames(tau) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(centre, tangent, lateral, dorsal) at tau. Lateral is +x made perpendicular to the tangent; dorsal is
    tangent x lateral, the back of the eel (toward -z on the rising body, up on the head)."""
    tau = np.atleast_1d(np.asarray(tau, dtype=np.float64))
    c = spine(tau)
    e = 1e-3
    tan = spine(np.clip(tau + e, 0, TAU_END)) - spine(np.clip(tau - e, 0, TAU_END))
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    x = np.array([1.0, 0.0, 0.0])
    lat = x[None] - (tan @ x)[:, None] * tan
    lat /= np.linalg.norm(lat, axis=1, keepdims=True)
    dor = np.cross(tan, lat)
    return c, tan, lat, dor


def section(tau) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return np.interp(tau, SEC_TAU, SEC_DU), np.interp(tau, SEC_TAU, SEC_DV), np.interp(tau, SEC_TAU, SEC_W)


def lip(tau) -> np.ndarray:
    """The upper lip's ventral extent: the mouth line below the spine, where the lower jaw closes."""
    return np.interp(tau, LIP_TAU, LIP_DV)


def _arc():
    tau = np.linspace(0.0, TAU_END, 6001)
    p = spine(tau)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    return tau, s


ARC_TAU, ARC_S = _arc()


def arc_of(tau) -> np.ndarray:
    return np.interp(tau, ARC_TAU, ARC_S)


def tau_of(s) -> np.ndarray:
    return np.interp(s, ARC_S, ARC_TAU)


def ring_taus() -> np.ndarray:
    """Ring positions along the spine: coarse on the buried and grounded tail, finer up the body, finest on the
    head and around the gill slit."""
    out = [0.0]
    s = 0.0
    total = float(ARC_S[-1])
    while True:
        t = float(tau_of(s))
        if t < 3.5:
            step = 0.06
        elif t < 8.6:
            step = 0.04
        elif abs(t - GILL_TAU) < 0.2:
            step = 0.011
        else:
            step = 0.02
        s += step
        if s >= total - 0.01:
            break
        out.append(float(tau_of(s)))
    out.append(TAU_END)
    return np.asarray(out)


def sweep(C, LAT, DOR, du, dv, w, segs: int, expo: float = 0.85):
    """Rings of an oval section along centres C: the kit's tube convention (ring = cos a * lateral + sin a *
    dorsal, dorsal = tangent x lateral). Returns P, T and each vertex's (sin a, cos a, ring index)."""
    a = np.arange(segs) * (2.0 * math.pi / segs)
    ca, sa = np.cos(a), np.sin(a)
    X = np.sign(ca) * np.abs(ca) ** expo
    ext = np.where(sa[None] >= 0, du[:, None], dv[:, None]) * sa[None]
    P = C[:, None, :] + LAT[:, None, :] * (w[:, None] * X[None])[..., None] + DOR[:, None, :] * ext[..., None]
    K = len(C)
    return (P.reshape(-1, 3), ck.grid_tris(K, segs, True), np.tile(sa, K), np.tile(ca, K),
            np.repeat(np.arange(K), segs))


def cap(P: np.ndarray, T: np.ndarray, ring: int, segs: int, tip, outward) -> tuple[np.ndarray, np.ndarray]:
    """Closes one end ring with a fan to `tip`, wound to face `outward`."""
    idx = len(P)
    P = np.vstack([P, np.asarray(tip)[None]])
    r0 = ring * segs
    fan = np.asarray([(r0 + s, r0 + (s + 1) % segs, idx) for s in range(segs)], dtype=np.int64)
    fan = orient(P, fan, lambda c: np.broadcast_to(np.asarray(outward), c.shape))
    return P, np.vstack([T, fan])


def orient(P: np.ndarray, T: np.ndarray, want) -> np.ndarray:
    """Flips the triangles whose face normal points against want(centroids)."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    cen = P[T].mean(axis=1)
    bad = (fn * want(cen)).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def convex(P: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Winds a small convex part outward from its centroid."""
    c = P.mean(axis=0)
    return orient(P, T, lambda q: q - c)


def align_y(n) -> np.ndarray:
    """A rotation taking +y to the unit vector n."""
    y = np.array([0.0, 1.0, 0.0])
    n = np.asarray(n, dtype=np.float64)
    n = n / np.linalg.norm(n)
    v = np.cross(y, n)
    c = float(y @ n)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k * (1.0 / (1.0 + c))


def surface(tau: float, angle_deg: float, side: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """A point on the body surface at tau and section angle (0 = lateral, 90 = dorsal), with its outward normal."""
    c, _tan, lat, dor = (v[0] for v in frames(tau))
    du, dv, w = (float(v) for v in section(tau))
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    X = math.copysign(abs(ca) ** 0.85, ca)
    h = du if sa >= 0 else dv
    p = c + lat * side * w * X + dor * h * sa
    n = lat * side * ca / max(w, 1e-6) + dor * sa / max(h, 1e-6)
    return p, n / np.linalg.norm(n)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def lure_points() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The stalk's base on the brow, its control points and its tip (where the cage hangs)."""
    base, _n = surface(BROW_TAU, 90.0)
    base = base - np.array([0.0, 0.012, 0.0])
    ctrl = np.array([base, base + (0.0, 0.20, 0.03), base + (0.0, 0.27, 0.30), base + (0.0, 0.145, 0.45)])
    return base, ctrl, ctrl[-1]


CAGE_H = 0.17


def jaw_points() -> tuple[np.ndarray, np.ndarray]:
    c, _t, _l, dor = (v[0] for v in frames(HINGE_TAU))
    hinge = c - dor * (float(lip(HINGE_TAU)) + 0.02)
    c2, _t2, _l2, dor2 = (v[0] for v in frames(TAU_END))
    chin = c2 - dor2 * 0.04 + np.array([0.0, 0.0, 0.03])
    return hinge, chin


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    pts = spine(J_TAU)
    parent = "root"
    for i, name in enumerate(SPINE):
        rig.add(name, pts[i], pts[i + 1], parent)
        parent = name
    rig.add("head", pts[-1], spine(TAU_END)[0], parent)
    hinge, chin = jaw_points()
    rig.add("jaw", hinge, chin, "head")
    _base, ctrl, tip = lure_points()
    rig.add("lure_a", ctrl[0], tip, "head")
    rig.add("lure_b", tip, tip - (0.0, CAGE_H, 0.0), "lure_a")
    return rig


def chain_skin(rig: ck.Rig):
    names = ["root"] + SPINE + ["head"]
    pts = np.vstack([spine(0.0), spine(J_TAU), spine(TAU_END)])
    return rig.chain(names, pts)


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    taus = ring_taus()
    C, _TAN, LAT, DOR = frames(taus)
    du, dv, w = section(taus)
    P, T, sa, ca, ring = sweep(C, LAT, DOR, du, dv, w, SEGS)
    tv = taus[ring]  # tau per vertex
    sv = arc_of(tv)  # arc length per vertex
    side = np.sign(ca + 1e-9)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    head = ck.smoothstep(10.06, 10.2, tv)  # 0 body and throat .. 1 the mouth's corner and the head
    ventral = ck.smoothstep(-0.35, -0.8, sa)

    # the gill slit: a short curved seam low on each side behind the jaw
    g_s = arc_of(GILL_TAU) + 0.025 * sa
    slit = np.exp(-((sv - g_s) / 0.008) ** 2) * ck.smoothstep(-0.75, -0.45, sa) * ck.smoothstep(0.35, 0.05, sa)
    lip = np.exp(-((sv - g_s) / 0.022) ** 2) * ck.smoothstep(-0.8, -0.4, sa) * ck.smoothstep(0.45, 0.1, sa)
    # skin folds on the throat where the neck turns
    fold_zone = ck.smoothstep(8.7, 9.1, tv) * ck.smoothstep(9.75, 9.5, tv) * ck.smoothstep(0.3, -0.6, sa)
    folds = fold_zone * np.maximum(np.sin(sv * 2 * math.pi / 0.045), 0.0) ** 2
    # the brow: a low bony ridge between the eyes running up to the stalk
    brow = ck.smoothstep(10.2, 10.5, tv) * ck.smoothstep(11.1, 10.7, tv) * ck.smoothstep(0.85, 1.0, sa)
    # jaw muscles behind the eyes, a moray's swollen cheeks
    cheek = np.exp(-((tv - 10.25) / 0.35) ** 2) * np.abs(ca) ** 2 * (sa > -0.2)
    rough = ck.fbm(P * 9.0, SEED + 1) * 0.004
    disp = rough - 0.012 * slit + 0.006 * lip - 0.005 * folds + 0.01 * brow + 0.012 * cheek
    disp *= ck.smoothstep(0.0, 0.4, tv)  # the buried end stays plain
    P = P + N * disp[:, None]
    # the snout tip and the buried tail close with caps
    P, T = cap(P, T, len(taus) - 1, SEGS, spine(TAU_END)[0] + _TAN[-1] * 0.012, _TAN[-1])
    P, T = cap(P, T, 0, SEGS, spine(0.0)[0] - _TAN[0] * 0.02, -_TAN[0])
    n_extra = 2
    pad = lambda a, v=0.0: np.concatenate([a, np.full(n_extra, v)])  # noqa: E731
    sa, ca, tv, sv = pad(sa, 0.0), pad(ca, 1.0), pad(tv, TAU_END), pad(sv, float(ARC_S[-1]))
    tv[-1] = 0.0
    slit, lip, folds, brow, head, ventral = (pad(a) for a in (slit, lip, folds, brow, head, ventral))

    # colour: deep teal flanks darkening to abyss navy along the spine, a sand-pale belly line, a faint
    # reticulated net of sea-glow lines, darker mottles
    up = ck.smoothstep(-0.1, 0.95, sa)
    base = ck.mix(PAL["deep_teal_shadow"], PAL["abyss_navy"] * 0.6 + PAL["deep_teal_shadow"] * 0.4, up[:, None])
    mott = ck.smoothstep(0.05, 0.35, ck.fbm(P * 5.0, SEED + 3))
    base = base * (1.0 - 0.25 * mott)[:, None]
    net = 1.0 - ck.smoothstep(0.03, 0.12, np.abs(ck.value_noise(P * np.array([9.0, 7.0, 9.0]), SEED + 4)))
    net *= (1.0 - ventral) * (0.55 + 0.45 * (1.0 - up)) * ck.smoothstep(0.3, 1.0, tv)
    base = ck.mix(base, PAL["sea_glow"], (0.8 * net)[:, None])
    belly_col = PAL["sand_wet"] * (0.92 + 0.08 * ck.fbm(P * 12.0, SEED + 5))[:, None]
    belly_col = ck.mix(belly_col, PAL["coral_stone_weathered"], 0.12)
    belly = ventral * (1.0 - head)
    col = ck.mix(base, belly_col, belly[:, None])
    # a soft edge between belly and flank: a thin darker seam reads the curve
    seam = np.exp(-((sa + 0.47) / 0.08) ** 2) * (1.0 - head)
    col = col * (1.0 - 0.3 * seam)[:, None]
    # the head: the mouth's palate (ventral side of the upper head) is dark
    mouth = head * ck.smoothstep(-0.55, -0.85, sa)
    col = ck.mix(col, PAL["lacquer_black"] * 0.9 + PAL["tortoiseshell"] * 0.1, mouth[:, None])
    # lips: a pale line along the edge of the upper jaw
    lipline = head * np.exp(-((sa + 0.42) / 0.1) ** 2) * ck.smoothstep(11.95, 11.6, tv)
    col = ck.mix(col, PAL["sand_wet"] * 0.8, (0.55 * lipline)[:, None])
    # old claw-rakes on the camera flank: three pale healed scars
    sc = scars(P)
    col = ck.mix(col, PAL["bone"] * 0.75, (0.45 * sc)[:, None])
    # the gill seam glows; its lip is darker
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, slit[:, None])
    col = col * (1.0 - 0.35 * lip * (1.0 - slit))[:, None]
    wet = 0.92 - 0.25 * ventral * (1.0 - head)
    cavity = 0.8 * slit + 0.3 * lip + 0.6 * folds + 0.4 * mouth + 0.25 * sc + 0.2 * seam
    ck.finish(mesh, P, T, "skin", col, chain_skin(rig), wet=wet, cavity=np.clip(cavity, 0, 1), emission=slit)


def scars(P: np.ndarray) -> np.ndarray:
    """Three parallel healed rakes on the camera-side flank of the upper curve (beauty in decline)."""
    c, _t, _l, _d = (v[0] for v in frames(6.7))
    d1 = np.array([0.0, 0.62, 0.78])
    d1 /= np.linalg.norm(d1)
    d2 = np.array([0.0, 0.78, -0.62])
    q = P - c
    s = q @ d1
    along = q @ d2
    out = np.zeros(len(P))
    for k in range(3):
        out += np.exp(-((s - (k - 1) * 0.035) / 0.0045) ** 2)
    win = ck.smoothstep(0.16, 0.08, np.abs(along + 0.02 * np.sin(s * 30)))
    return np.clip(out, 0, 1) * win * ck.smoothstep(0.0, 0.05, P[:, 0] * SIDE_CAM)


def jaw(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The heavy lower jaw: a long wedge under the upper lip, its floor dark, its chin pale. Its root is buried in
    the throat behind the mouth's corner, where it hinges."""
    taus = np.linspace(JAW_ROOT_TAU, TAU_END, 28)
    C, _TAN, LAT, DOR = frames(taus)
    _du, _dv, w = section(taus)
    t = np.clip((taus - HINGE_TAU) / (TAU_END - HINGE_TAU), 0.0, 1.0)
    jd = 0.06 * (1 - t) + 0.028 * t + 0.016 * np.exp(-((t - 0.12) / 0.2) ** 2)  # deep behind the corner
    mouthline = C - DOR * lip(taus)[:, None]
    hook = np.array([0.0, 0.0, 1.0])[None] * (0.025 * t ** 3)[:, None]  # the chin pushes a little past the snout
    centres = mouthline - DOR * (jd * 0.62)[:, None] + hook
    jw = np.maximum(np.minimum(w, 0.105) * 0.94, 0.024)
    jw = jw * (0.55 + 0.45 * ck.smoothstep(JAW_ROOT_TAU, HINGE_TAU + 0.15, taus))  # tucked into the throat
    P, T, sa, ca, ring = sweep(centres, LAT, DOR, jd * 0.6, jd, jw, 14, expo=0.75)
    P, T = cap(P, T, len(taus) - 1, 14, centres[-1] + _TAN[-1] * 0.015 + DOR[-1] * 0.004, _TAN[-1])
    P, T = cap(P, T, 0, 14, centres[0] - _TAN[0] * 0.02, -_TAN[0])
    sa = np.concatenate([sa, [0.0, 0.0]])
    tt = np.concatenate([t[ring], [1.0, 0.0]])
    floor = ck.smoothstep(0.5, 0.85, sa)
    underside = ck.smoothstep(-0.2, -0.65, sa)
    side_col = ck.mix(PAL["deep_teal_shadow"], PAL["abyss_navy"] * 0.6 + PAL["deep_teal_shadow"] * 0.4, 0.3)
    col = ck.mix(side_col, PAL["sand_wet"] * 0.95, underside[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 0.9 + PAL["tortoiseshell"] * 0.1, floor[:, None])
    lipline = np.exp(-((sa - 0.35) / 0.12) ** 2) * ck.smoothstep(0.98, 0.85, tt)
    col = ck.mix(col, PAL["sand_wet"] * 0.8, (0.5 * lipline)[:, None])
    ck.finish(mesh, P, T, "skin", col, rig.rigid("jaw"), wet=0.85, cavity=0.5 * floor)


def cone(base, direction, length: float, radius: float, sides: int = 4) -> tuple[np.ndarray, np.ndarray]:
    d = np.asarray(direction, dtype=np.float64)
    d /= np.linalg.norm(d)
    R = align_y(d)
    a = np.arange(sides) * (2 * math.pi / sides)
    ring = np.column_stack([np.cos(a) * radius, np.zeros(sides), np.sin(a) * radius]) @ R.T + base
    P = np.vstack([ring, np.asarray(base) + d * length])
    T = np.asarray([(s, (s + 1) % sides, sides) for s in range(sides)], dtype=np.int64)
    return P, convex(P, T)


def teeth(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Fine, slender teeth along both jaws, raked back and a little inward, longest toward the front; two longer
    fangs on the palate's midline."""
    for side in (1.0, -1.0):
        for tau in np.linspace(10.45, 11.93, 17):
            c, tan, lat, dor = (v[0] for v in frames(tau))
            w = float(section(tau)[2])
            f = (tau - 10.45) / 1.48
            L = 0.008 + 0.011 * f ** 1.4
            base = c - dor * float(lip(tau)) * 0.8 + lat * side * w * 0.8
            P, T = cone(base, -dor - tan * 0.4 - lat * side * 0.2, L, 0.0026 + 0.0012 * f)
            ck.finish(mesh, P, T, "bone", PAL["bone"], rig.rigid("head"), wet=0.6, cavity=0.1, flat=True)
        for tau in np.linspace(10.5, 11.95, 16):
            c, tan, lat, dor = (v[0] for v in frames(tau))
            w = float(section(tau)[2])
            f = (tau - 10.5) / 1.45
            L = 0.008 + 0.01 * f ** 1.4
            base = c - dor * (float(lip(tau)) + 0.004) + lat * side * min(w, 0.105) * 0.72
            P, T = cone(base, dor - tan * 0.35 - lat * side * 0.12, L, 0.0025 + 0.0011 * f)
            ck.finish(mesh, P, T, "bone", PAL["bone"], rig.rigid("jaw"), wet=0.6, cavity=0.1, flat=True)
    for tau in (11.6, 11.8):
        c, tan, lat, dor = (v[0] for v in frames(tau))
        P, T = cone(c - dor * float(lip(tau)) * 0.6, -dor - tan * 0.3, 0.024, 0.004)
        ck.finish(mesh, P, T, "bone", PAL["bone"], rig.rigid("head"), wet=0.6, flat=True)


def sphere_part(center, radius, normal, rings: int, segs: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A sphere whose +y pole faces `normal`; also returns each vertex's cosine to that pole."""
    P, T = ck.ellipsoid((0, 0, 0), (1.0, 1.0, 1.0), rings, segs)
    cosp = P[:, 1].copy()
    P = ck.transform(P * radius, align_y(normal), center)
    return P, T, cosp


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Small eyes set far forward: a dark pupil, a pale ring, in a slight socket."""
    for side in (1.0, -1.0):
        p, n = surface(11.05, 24.0, side)
        n = n + np.array([0.0, 0.0, 0.25])
        n /= np.linalg.norm(n)
        P, T, cosp = sphere_part(p - n * 0.009, 0.018, n, 6, 10)
        iris = ck.smoothstep(0.55, 0.75, cosp)
        pupil = ck.smoothstep(0.86, 0.92, cosp)
        col = ck.mix(PAL["abyss_navy"] * 0.5 + PAL["deep_teal_shadow"] * 0.5, PAL["sand_wet"] * 0.9, iris[:, None])
        col = ck.mix(col, PAL["lacquer_black"], pupil[:, None])
        ck.finish(mesh, P, T, "eye", col, rig.rigid("head"), wet=1.0)
        # tubular anterior nostrils at the snout tip
        q, m = surface(11.84, 40.0, side)
        path = ck.bezier([q - m * 0.004, q + m * 0.006 + np.array([0, 0.0, 0.010]), q + m * 0.01 + np.array([0, 0.0, 0.018])], 4)
        Pn, Tn = ck.tube(path, np.array([0.0065, 0.0058, 0.0052, 0.0048]), 6, cap_start=False, cap_end=False)
        ck.finish(mesh, Pn, Tn, "skin", PAL["deep_teal_shadow"], rig.rigid("head"), wet=0.9, cavity=0.2)


def frill(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The continuous dorsal frill: a thin ribbon on the spine from behind the head to the ground, fin-rayed,
    scalloped, with one old tear; two faces, so it reads from both sides."""
    t0, t1 = 1.55, 9.75
    s0, s1 = float(arc_of(t0)), float(arc_of(t1))
    n = int((s1 - s0) / 0.026) + 1
    sv = np.linspace(s0, s1, n)
    taus = tau_of(sv)
    C, TAN, LAT, DOR = frames(taus)
    du, _dv, _w = section(taus)
    f = (sv - s0) / (s1 - s0)  # 0 at the ground .. 1 behind the head
    h = 0.05 + 0.055 * np.sin(np.clip(f, 0, 1) * math.pi) ** 0.7
    h *= ck.smoothstep(0.0, 0.05, f) * 0.85 + 0.15
    h *= ck.smoothstep(1.0, 0.9, f) * 0.75 + 0.25
    ray = 0.035
    scallop = 1.0 - 0.16 * np.abs(np.sin(math.pi * sv / ray)) ** 0.6
    h *= scallop
    tear = float(arc_of(6.9))
    torn = np.exp(-((sv - tear) / 0.03) ** 2)
    h *= 1.0 - 0.6 * torn * (0.7 + 0.3 * np.sin(sv * 140.0))
    rows = 3
    v = np.linspace(0.0, 1.0, rows)
    base = C + DOR * (du - 0.014)[:, None]
    ruffle = 0.009 * np.sin(sv * 2 * math.pi / 0.11)
    pts = []
    for r in v:
        pts.append(base + DOR * (h * r)[:, None] + LAT * (ruffle * r ** 2)[:, None])
    grid = np.stack(pts, axis=1)  # (n, rows, 3)
    rayline = ck.smoothstep(0.75, 1.0, np.abs(np.cos(math.pi * sv / ray)))
    for side in (1.0, -1.0):
        P = (grid + LAT[:, None, :] * (0.0032 * side)).reshape(-1, 3)
        T = ck.grid_tris(n, rows, False)
        latv = np.repeat(LAT, rows, axis=0)
        T = orient_by_vertex(P, T, latv * side)
        rv = np.tile(v, n)
        col = ck.mix(PAL["deep_teal_shadow"], PAL["lagoon_teal"], (0.25 + 0.6 * rv)[:, None])
        col = ck.mix(col, PAL["deep_teal_shadow"] * 0.8, (0.5 * np.repeat(rayline, rows) * (1 - rv * 0.5))[:, None])
        edge = ck.smoothstep(0.7, 1.0, rv)
        col = ck.mix(col, PAL["salt_glass"] * 0.7 + PAL["lagoon_teal"] * 0.3, (0.3 * edge)[:, None])
        ck.finish(mesh, P, T, "fin", col, chain_skin(rig), wet=0.7, cavity=0.3 * (1 - rv) ** 2)


def orient_by_vertex(P: np.ndarray, T: np.ndarray, want_v: np.ndarray) -> np.ndarray:
    """Flips triangles whose normal points against the mean `want_v` of their vertices."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    want = want_v[T].mean(axis=1)
    bad = (fn * want).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def photophores(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A row of faint sea-glow photophores along each flank, below the lateral line."""
    s0, s1 = float(arc_of(2.2)), float(arc_of(9.15))
    n = int((s1 - s0) / 0.13)
    for side in (1.0, -1.0):
        for k in range(n + 1):
            s = s0 + (s1 - s0) * k / n
            tau = float(tau_of(s))
            p, nrm = surface(tau, -12.0 + 6.0 * math.sin(k * 1.7), side)
            f = k / n
            r = 0.0085 + 0.0055 * f
            P, T, cosp = sphere_part(p - nrm * r * 0.45, r, nrm, 2, 6)
            glow = ck.smoothstep(0.1, 0.7, cosp)
            col = ck.mix(PAL["deep_teal_shadow"], PAL["sea_glow"], (0.4 + 0.6 * glow)[:, None])
            ck.finish(mesh, P, T, "photophore", col, chain_skin(rig), wet=1.0, emission=glow)


def lure(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The stalk from the brow and the six-ribbed bone cage hanging from it, with the cold light inside."""
    base, ctrl, tip = lure_points()
    path = ck.bezier(ctrl, 18)
    u = np.linspace(0.0, 1.0, 18)
    rad = 0.017 * (1 - u) + 0.0065 * u
    rad = rad * (1.0 + 0.18 * np.exp(-((u - 0.45) / 0.04) ** 2) + 0.15 * np.exp(-((u - 0.72) / 0.035) ** 2))
    rad[0] *= 1.35  # it flares where it grows from the brow
    P, T = ck.tube(path, rad, 7, cap_start=False, cap_end=True)
    uu = np.concatenate([np.repeat(u, 7), [1.0]])
    bony = ck.smoothstep(0.35, 0.85, uu)
    col = ck.mix(PAL["deep_teal_shadow"], PAL["bone"] * 0.78, bony[:, None])
    knuckle = np.exp(-((uu - 0.45) / 0.03) ** 2) + np.exp(-((uu - 0.72) / 0.03) ** 2)
    col = col * (1.0 - 0.2 * knuckle)[:, None]
    knee = base + (tip - base) * 0.62
    ck.finish(mesh, P, T, "skin", col, rig.blend("lure_a", "lure_b", knee, tip), wet=0.9 - 0.5 * bony,
              cavity=0.4 * knuckle)
    top = tip - np.array([0.0, 0.012, 0.0])
    # the crown: a small bone knob the stalk grips
    Pk, Tk = ck.ellipsoid(top, (0.021, 0.014, 0.021), 4, 10)
    ck.finish(mesh, Pk, Tk, "bone", PAL["bone"] * 0.92, rig.rigid("lure_b"), wet=0.4, cavity=0.2)
    # six ribs bowing out around the light, a slight twist as they descend
    for i in range(6):
        phi = i * math.pi / 3 + math.pi / 6
        pts = []
        for y, r, tw in ((-0.016, 0.012, 0.0), (-0.05, 0.047, 0.12), (-0.095, 0.058, 0.24), (-0.14, 0.036, 0.34),
                         (-0.162, 0.01, 0.4)):
            a = phi + tw
            pts.append(tip + np.array([r * math.sin(a), y, r * math.cos(a)]))
        path = ck.bezier(pts, 9)
        Pr, Tr = ck.tube(path, np.full(9, 0.0052), 4, cap_start=False, cap_end=False)
        rr = np.repeat(np.linspace(0, 1, 9), 4)
        cr = PAL["bone"] * (0.85 + 0.15 * np.sin(rr * math.pi))[:, None]
        ck.finish(mesh, Pr, Tr, "bone", cr, rig.rigid("lure_b"), wet=0.4, cavity=0.15)
    # a collar under the crown where the ribs are bound
    band = []
    for i in range(13):
        a = i * 2 * math.pi / 12
        band.append(tip + np.array([0.02 * math.sin(a), -0.027, 0.02 * math.cos(a)]))
    Pb, Tb = ck.tube(np.asarray(band), 0.0035, 4, cap_start=False, cap_end=False)
    ck.finish(mesh, Pb, Tb, "bone", PAL["bone"] * 0.8, rig.rigid("lure_b"), wet=0.4, cavity=0.3)
    # the finial: a small bone drop below the cage
    Pf, Tf = ck.ellipsoid(tip - np.array([0.0, 0.166, 0.0]), (0.014, 0.016, 0.014), 4, 8)
    ck.finish(mesh, Pf, Tf, "bone", PAL["bone"] * 0.88, rig.rigid("lure_b"), wet=0.4, cavity=0.2)
    Ps, Ts = cone(tip - np.array([0.0, 0.178, 0.0]), (0.0, -1.0, 0.0), 0.022, 0.007, 5)
    ck.finish(mesh, Ps, Ts, "bone", PAL["bone"] * 0.85, rig.rigid("lure_b"), wet=0.4, flat=True)
    # the light: a cold steady salt-glass core
    Pl, Tl = ck.ellipsoid(tip - np.array([0.0, 0.092, 0.0]), (0.031, 0.042, 0.031), 7, 12)
    ck.finish(mesh, Pl, Tl, "lantern", PAL["salt_glass"], rig.rigid("lure_b"), wet=1.0, emission=1.0)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("lantern_eel")
    body(mesh, rig)
    jaw(mesh, rig)
    teeth(mesh, rig)
    eyes(mesh, rig)
    frill(mesh, rig)
    photophores(mesh, rig)
    lure(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 3.0, loop=True)
    w = 2.0 * math.pi / idle.length
    # a figure-of-eight sway travelling up the S: side to side once, fore and aft twice, each bone a beat late
    for i, b in enumerate(SPINE):
        amp = 1.5 + 1.5 * i / 8
        lag = 0.45 * i
        sway(idle, b, lambda t, a=amp, g=lag, k=i: (
            (0.8 + 0.5 * k / 8) * math.sin(w * t - g) + 0.9 * math.sin(2 * w * t - g), 0.0, a * math.sin(w * t - g)))
    sway(idle, "head", lambda t: (2.0 * math.sin(w * t - 4.2), 3.0 * math.sin(w * t - 4.2),
                                  -2.5 * math.sin(w * t - 4.2)))
    sway(idle, "jaw", lambda t: (6.0 + 3.0 * math.sin(2 * w * t + 0.6), 0.0, 0.0))
    # the lure lags the head, the cage a beat further behind: a pendulum
    sway(idle, "lure_a", lambda t: (3.0 * math.sin(w * t - 5.0) + 1.5 * math.sin(2 * w * t - 5.4), 0.0,
                                    5.0 * math.sin(w * t - 5.0)))
    sway(idle, "lure_b", lambda t: (6.0 * math.sin(w * t - 5.9) + 3.0 * math.sin(2 * w * t - 6.6), 0.0,
                                    9.0 * math.sin(w * t - 5.9)))

    attack = ck.Clip("attack", 1.1)
    # coil back (the S tightens), a straight lunge, the jaw snapping shut on contact at 0.55 s
    for t, low, up, head, jw in (
        (0.0, 0, 0, 0, 6),
        (0.32, 4, -8, -14, 32),
        (0.45, 5, -9, -16, 44),
        (0.55, -4, 12, 12, 0),
        (0.7, -4, 11, 10, 4),
        (1.1, 0, 0, 0, 6),
    ):
        for i, b in enumerate(SPINE):
            attack.key(b, t, (low if i < 4 else up, 0, 0))
        attack.key("head", t, (head, 0, 0))
        attack.key("jaw", t, (jw, 0, 0))
        attack.key("lure_a", t, (-0.6 * head, 0, 0))
        attack.key("lure_b", t, (-0.9 * head, 0, 0))

    cast = ck.Clip("cast", 1.6)
    # the tell: the head draws back and lifts the lure high and forward; the cage swings toward the target and
    # steadies; the body holds still while the light holds (release 0.9 s); then a slow sway back
    for t, up, head, la, lb, jw in (
        (0.0, 0, 0, 0, 0, 6),
        (0.45, -3.5, -20, -40, 18, 14),
        (0.75, -2.5, -12, -14, -34, 12),
        (0.9, -2.5, -12, -12, -26, 12),
        (1.15, -2.4, -12, -12, -25, 12),
        (1.6, 0, 0, 0, 0, 6),
    ):
        for i, b in enumerate(SPINE):
            cast.key(b, t, (up if i >= 4 else -0.4 * up, 0, 0))
        cast.key("head", t, (head, 0, 0))
        cast.key("lure_a", t, (la, 0, 0))
        cast.key("lure_b", t, (lb, 0, 0))
        cast.key("jaw", t, (jw, 0, 0))

    hit = ck.Clip("hit", 0.5)
    # the body kinks away at the middle, the head whips back, the lure swings wide
    for t, k, lb in ((0.0, 0.0, 0.0), (0.09, 1.0, 1.0), (0.22, 0.45, -0.6), (0.5, 0.0, 0.0)):
        for i, b in enumerate(SPINE):
            hit.key(b, t, ((-9 if 3 <= i <= 4 else (5 if i >= 5 else 0)) * k, 0, (3 if i >= 4 else 0) * k))
        hit.key("head", t, (-16 * k, 0, 4 * k))
        hit.key("jaw", t, (6 + 18 * k, 0, 0))
        hit.key("lure_a", t, (-14 * k, 0, 10 * k))
        hit.key("lure_b", t, (-25 * lb, 0, 30 * lb))

    ko = ck.Clip("ko", 1.6)
    # the light goes first: the lure droops; then the S slackens from the head down and folds into a low coil
    ko.key("lure_a", 0.0, (0, 0, 0))
    ko.key("lure_a", 0.35, (48, 0, 6))
    ko.key("lure_a", 1.6, (55, 0, 8))
    ko.key("lure_b", 0.0, (0, 0, 0))
    ko.key("lure_b", 0.25, (-10, 0, 0))
    ko.key("lure_b", 0.45, (30, 0, 0))
    ko.key("lure_b", 1.6, (20, 0, 0))
    ko.key("jaw", 0.0, (6, 0, 0))
    ko.key("jaw", 0.6, (22, 0, 0))
    ko.key("jaw", 1.6, (6, 0, 0))
    ko.key("head", 0.0, (0, 0, 0))
    ko.key("head", 0.55, (28, 0, 0))
    ko.key("head", 1.6, (20, -10, 0))
    for i, b in enumerate(SPINE):
        start = 0.35 + 0.08 * (8 - i)  # from the head down
        ko.key(b, 0.0, (0, 0, 0))
        ko.key(b, start, (0, 0, 0))
        ko.key(b, 1.6, KO_POSE[i])
    return [idle, attack, cast, hit, ko]


# The low coil each spine bone ends the KO in (degrees about the rest axes).
KO_POSE = [(0, 0, 8), (0, 0, 42), (8, 0, 40), (-20, 0, 0), (-38, 0, 0), (-40, 0, 0), (-40, 0, 0), (-36, 0, 0),
           (-30, 0, 0)]


def sway(clip: ck.Clip, bone: str, fn) -> None:
    """Keys fn(t) -> (rx, ry, rz) at every baked frame, so a sum of waves plays as authored (the kit eases into
    each key; a key per frame leaves nothing to ease)."""
    frames_n = int(round(clip.length * ck.FPS))
    for f in range(frames_n + 1):
        t = clip.length * f / frames_n
        clip.key(bone, t, fn(t))


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "lantern_eel"})
    print(f"lantern_eel: {info}")


if __name__ == "__main__":
    main()
