"""Gull harrier battle model (M2-CRE-06): docs/kb/art/creatures/gull_harrier.md.

blender --background --factory-startup --python assets_src/creatures/gull_harrier/build_gull_harrier.py -- \
    --out assets/creatures/gull_harrier/gull_harrier.glb

A gull grown to an albatross's size on the leavings of storms: long, narrow, crooked "M" wings (2.5 m tip to tip)
built from layered feather blades (primaries, secondaries, tertials, three rows of coverts, scapulars), a
cumulus_shadow mantle, foam_white head and underparts, ragged storm_slate wing-tips, a raptor's hooked beak on a
gull's head, a short fanned tail, legs tucked in flight with a hank of torn net-twine and kelp caught on the right
foot, and a lamp-diver's bone hook lodged in the throat (the spawn_wound weak point).

The origin is the hover point (battle_sandbox.json stand_ins.gull_harrier: hover 1.05, height 0.45): the body sits
from y = 0 to 0.45 above it, and the KO clip falls the 1.05 m to the ground. The creature faces +z; its right side
(-x) faces the battle camera once the stage turns it toward the party (yaw 90), so the right wing carries the
worst of the storm damage.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6113
PAL = {k: ck.hexrgb(v) for k, v in {
    "cumulus_shadow": "#8FA7C4", "overcast_slate": "#6F7E8E", "storm_slate": "#3E4A57", "foam_white": "#EEF6F4",
    "dusk_gold": "#F2A64A", "sand_cloth": "#C9B48E", "tortoiseshell": "#6B3A1E", "lacquer_black": "#1D1916",
    "sun_gold": "#FFD27A", "timber_weathered": "#7E6A55", "foliage_shadow": "#1E4A3A", "bone": "#E6DAC0",
    "spawn_wound": "#3FE0C8",
}.items()}
FOAM = PAL["foam_white"] * 0.9  # foam_white held under the albedo ceiling #EBE7DF
MANTLE = ck.mix(PAL["cumulus_shadow"], PAL["overcast_slate"], 0.45)  # cumulus_shadow deepened toward overcast_slate
TIPS = PAL["storm_slate"]
HORN = ck.mix(PAL["dusk_gold"], PAL["sand_cloth"], 0.5)  # beak and legs: dusk_gold muted toward sand_cloth
UP = np.array([0.0, 1.0, 0.0])

# The left wing's arm chain (x > 0); the right wing mirrors it.
SHOULDER = (0.12, 0.30, 0.10)
ELBOW = (0.42, 0.37, 0.05)
WRIST = (0.70, 0.415, 0.13)
TIP = (1.26, 0.29, -0.13)
HIP = (0.07, 0.11, -0.10)
ANKLE = (0.065, 0.10, -0.30)
TWINE_PTS = ((-0.065, 0.10, -0.30), (-0.07, 0.01, -0.43), (-0.075, -0.08, -0.56), (-0.08, -0.16, -0.68))  # the hank, ankle down
THROAT = np.array([-0.022, 0.268, 0.41])  # the bone hook's wound (a little to the camera side)

# The wing's surface: height y(x) (the crooked "M": up to the wrist, down to the tip), the leading edge z(x), the
# chord and half-thickness of the covert mass (the marginal and lesser coverts).
H_PTS = ((0.0, 0.29), (0.12, 0.30), (0.42, 0.37), (0.70, 0.415), (0.86, 0.40), (1.05, 0.355), (1.32, 0.26))
LE_PTS = ((0.0, 0.17), (0.12, 0.17), (0.42, 0.18), (0.70, 0.20), (0.82, 0.175), (1.0, 0.085), (1.12, 0.02))
CHORD_PTS = ((0.0, 0.11), (0.42, 0.10), (0.70, 0.09), (1.0, 0.06), (1.12, 0.04))
THICK_PTS = ((0.0, 0.05), (0.12, 0.048), (0.42, 0.034), (0.70, 0.026), (0.95, 0.014), (1.12, 0.006))

# The body, a lofted spindle from the tail to the face: (z, centre y, half-width, back height, belly depth).
STATIONS = (
    (-0.48, 0.255, 0.000, 0.000, 0.000),
    (-0.45, 0.255, 0.040, 0.025, 0.030),
    (-0.38, 0.250, 0.075, 0.045, 0.060),
    (-0.28, 0.240, 0.115, 0.075, 0.110),
    (-0.16, 0.230, 0.150, 0.095, 0.150),
    (-0.03, 0.225, 0.170, 0.105, 0.175),
    (0.08, 0.230, 0.170, 0.105, 0.180),
    (0.18, 0.245, 0.150, 0.095, 0.165),
    (0.27, 0.275, 0.110, 0.080, 0.115),
    (0.33, 0.305, 0.082, 0.070, 0.080),
    (0.38, 0.330, 0.074, 0.068, 0.072),
    (0.43, 0.348, 0.077, 0.075, 0.072),
    (0.46, 0.351, 0.077, 0.075, 0.070),
    (0.49, 0.352, 0.075, 0.072, 0.066),
    (0.515, 0.350, 0.069, 0.066, 0.060),
    (0.54, 0.345, 0.061, 0.058, 0.052),
    (0.58, 0.336, 0.038, 0.040, 0.034),
    (0.60, 0.333, 0.000, 0.000, 0.000),
)


def _f(pts, x):
    xs, ys = zip(*pts)
    return np.interp(x, xs, ys)


def _unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    return v / max(float(np.linalg.norm(v)), 1e-12)


def _outward(P: np.ndarray, T: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Winds T so its faces point away from the per-vertex reference points C (a loft's centre line)."""
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    away = P[T].mean(axis=1) - C[T].mean(axis=1)
    return T if float((fn * away).sum()) >= 0.0 else ck.flip(T)


def _mirror(P: np.ndarray, N: np.ndarray | None, T: np.ndarray):
    m = np.array([-1.0, 1.0, 1.0])
    return P * m, (None if N is None else N * m), ck.flip(T)


def _ellipsoid(center, radii, rings: int, segs: int):
    """ck.ellipsoid, wound outward like the rest of this model (the kit's primitive winds the other way)."""
    P, T = ck.ellipsoid(center, radii, rings, segs)
    return P, _outward(P, T, np.broadcast_to(np.asarray(center, dtype=np.float64), P.shape))


def _tube(path, radius, segs: int = 12, **kw):
    """ck.tube, wound outward (each vertex is pushed away from its nearest point on the path)."""
    path = np.asarray(path, dtype=np.float64)
    P, T = ck.tube(path, radius, segs, **kw)
    near = np.argmin(((P[:, None, :] - path[None, :, :]) ** 2).sum(axis=2), axis=1)
    return P, _outward(P, T, path[near])


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.12, 0))
    rig.add("body", (0, 0.22, 0), (0, 0.22, 0.2), "root")
    rig.add("neck", (0, 0.29, 0.28), (0, 0.34, 0.40), "body")
    rig.add("head", (0, 0.345, 0.42), (0, 0.35, 0.56), "neck")
    rig.add("beak", (0, 0.316, 0.545), (0, 0.30, 0.70), "head")
    rig.add("tail", (0, 0.25, -0.38), (0, 0.25, -0.60), "body")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        m = np.array([s, 1.0, 1.0])
        rig.add(f"shoulder_{tag}", np.multiply(SHOULDER, m), np.multiply(ELBOW, m), "body")
        rig.add(f"elbow_{tag}", np.multiply(ELBOW, m), np.multiply(WRIST, m), f"shoulder_{tag}")
        rig.add(f"wrist_{tag}", np.multiply(WRIST, m), np.multiply(TIP, m), f"elbow_{tag}")
        rig.add(f"leg_{tag}", np.multiply(HIP, m), np.multiply(ANKLE, m), "body")
    for i, (a, b) in enumerate(zip(TWINE_PTS, TWINE_PTS[1:])):
        rig.add(f"twine_{i}", a, b, "leg_r" if i == 0 else f"twine_{i - 1}")
    return rig


# ---------------------------------------------------------------------------------------------
# Feather blades
# ---------------------------------------------------------------------------------------------
def blade(root, d, length, width, *, K=6, lead=0.38, thick=0.004, cup=0.25, bend=0.0, tip_start=0.55,
          cut=(0.0, 0.0), floor=0.0, n_hint=UP, wave=(0.0, 0.0), ruffle=(0.0, 0.0), seed=0):
    """A feather (or a kelp ribbon) as a thin two-sided slab: a top and a bottom surface, three vertices across
    (leading edge, rachis, trailing edge) that share their edge positions, so it is closed for back-face culling
    with no alpha. Returns (P, N, T, info) where info has per-vertex `t` (0 root .. 1 tip), `top` and `across`
    (+1 leading edge .. -1 trailing edge) and a barb-streaked detail `uv`."""
    root = np.asarray(root, dtype=np.float64)
    d = _unit(d)
    w = _unit(np.cross(d, n_hint))
    u = np.cross(w, d)
    t = np.linspace(0.0, 1.0, K)
    grow = np.minimum(1.0, 0.5 + t * 2.2)
    tt = np.clip((t - tip_start) / (1.0 - tip_start), 0.0, 1.0)
    taper = np.maximum(np.sqrt(np.clip(1.0 - tt * tt, 0.0, 1.0)), floor)
    wp = width * grow * taper
    sway = wave[0] * np.sin(2.0 * math.pi * wave[1] * t + seed)

    def spine(tv):
        return root + np.outer(tv * length, d) + np.outer(bend * length * tv * tv, u) + np.outer(sway, w)

    ramp = ck.smoothstep(0.55, 1.0, t)
    tl = t * (1.0 - cut[0] * ramp)
    tr = t * (1.0 - cut[1] * ramp)
    ruf = ruffle[0] * np.sin(2.0 * math.pi * ruffle[1] * t + 1.7 * seed)
    lead_e = spine(tl) + np.outer(lead * wp, w) - np.outer(cup * wp * 0.3 - ruf, u)
    trail_e = spine(tr) - np.outer((1.0 - lead) * wp, w) - np.outer(cup * wp * 0.3 + ruf, u)
    ridge = thick * (1.0 - 0.5 * t)
    top_r = spine(t) + np.outer(ridge, u)
    bot_r = spine(t) - np.outer(ridge * 0.5, u)
    Ptop = np.stack([lead_e, top_r, trail_e], axis=1).reshape(-1, 3)
    Pbot = np.stack([lead_e, bot_r, trail_e], axis=1).reshape(-1, 3)
    Tg = ck.grid_tris(K, 3, False)
    fn = np.cross(Ptop[Tg[:, 1]] - Ptop[Tg[:, 0]], Ptop[Tg[:, 2]] - Ptop[Tg[:, 0]])
    Ttop = Tg if float((fn @ u).sum()) >= 0.0 else ck.flip(Tg)
    Tbot = ck.flip(Ttop)
    Ntop = ck.vertex_normals(Ptop, Ttop)
    Nbot = ck.vertex_normals(Pbot, Tbot)
    n = 3 * K
    P = np.vstack([Ptop, Pbot])
    N = np.vstack([Ntop, Nbot])
    T = np.vstack([Ttop, Tbot + n])
    tv = np.tile(np.repeat(t, 3), 2)
    across = np.tile(np.tile([1.0, 0.0, -1.0], K), 2)
    top = np.concatenate([np.ones(n, bool), np.zeros(n, bool)])
    along_m = tv * length
    across_m = across * np.tile(np.repeat(wp, 3), 2) * 0.5
    off = (seed * 0.731) % 1.0 * 7.0
    uv = np.column_stack([(along_m * 0.6 - np.abs(across_m) * 2.2) * 3.0 + off, across_m * 0.8 + along_m * 0.1 + off])
    return P, N, T, {"t": tv, "top": top, "across": across, "uv": uv}


def _wing_dir(x0: float, phi_deg: float, length: float) -> np.ndarray:
    """A planform direction (phi from straight back toward the wing-tip) with the slope that keeps a blade on
    the wing's crooked surface."""
    ph = math.radians(phi_deg)
    dx, dz = math.sin(ph), -math.cos(ph)
    slope = (float(_f(H_PTS, x0 + dx * length)) - float(_f(H_PTS, x0))) / length
    return _unit((dx, slope, dz))


def _arm_bone(x: float) -> str:
    return "shoulder" if x < ELBOW[0] else ("elbow" if x < WRIST[0] else "wrist")


# ---------------------------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------------------------
def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    segs = 26
    a = np.arange(segs) * (2.0 * math.pi / segs)  # 0 = the back, pi = the belly
    s, c = np.sin(a), np.cos(a)
    e = 0.82  # a fuller-than-elliptic section
    rows, centre = [], []
    for z, cy, rx, top, bot in STATIONS:
        ry = np.where(c >= 0.0, top, bot)
        rows.append(np.column_stack([rx * np.sign(s) * np.abs(s) ** e, cy + ry * np.sign(c) * np.abs(c) ** e,
                                     np.full(segs, z)]))
        centre.append(np.tile([0.0, cy, z], (segs, 1)))
    P = np.vstack(rows)
    C = np.vstack(centre)
    T = _outward(P, ck.grid_tris(len(STATIONS), segs, True), C)
    radial = P - C
    nrm = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    P = P + nrm * (ck.fbm(P * 18.0, SEED + 1) * 0.004)[:, None]  # soft contour-feather ruffling
    z = P[:, 2]
    up = nrm[:, 1]
    # the grey mantle on the back between the wings; the head, neck and underparts white
    mantle = ck.smoothstep(0.05, 0.45, up) * ck.smoothstep(-0.44, -0.30, z) * (1.0 - ck.smoothstep(0.16, 0.30, z))
    col = ck.mix(FOAM, MANTLE, mantle[:, None])
    # winter streaks on the nape and a dark smudge behind the eye (the weathering)
    streak = ck.smoothstep(0.1, 0.5, ck.fbm(np.column_stack([P[:, 0] * 30, P[:, 1] * 90, z * 20]), SEED + 2))
    nape = ck.smoothstep(0.30, 0.40, z) * ck.smoothstep(-0.2, 0.4, up)
    col = ck.mix(col, PAL["overcast_slate"], (0.35 * streak * nape)[:, None])
    for sx in (1.0, -1.0):
        smudge = np.exp(-(((P[:, 0] - sx * 0.07) / 0.03) ** 2) - ((P[:, 1] - 0.36) / 0.025) ** 2 - ((z - 0.47) / 0.04) ** 2)
        col = ck.mix(col, PAL["overcast_slate"], (0.45 * smudge)[:, None])
    # salt-stain on the belly and the vent
    stain = ck.smoothstep(0.0, 0.5, ck.fbm(P * 7.0, SEED + 3)) * ck.smoothstep(0.0, -0.6, up)
    col = ck.mix(col, PAL["sand_cloth"], (0.3 * stain)[:, None])
    # the wound: the throat around the bone hook
    dw = np.linalg.norm(P - THROAT, axis=1)
    glow = np.exp(-((dw / 0.03) ** 2))
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, (0.8 * glow)[:, None])
    cav = 0.25 * ck.smoothstep(0.0, -0.8, up) + 0.4 * glow

    ib, inn, ih, it = rig.index("body"), rig.index("neck"), rig.index("head"), rig.index("tail")

    def bones(Pv):
        zz = Pv[:, 2]
        n = len(Pv)
        J = np.tile([ib, ib], (n, 1))
        W = np.tile([1.0, 0.0], (n, 1))
        wt = ck.smoothstep(-0.32, -0.47, zz) * 0.7
        tail = zz < -0.32
        J[tail, 1] = it
        W[tail] = np.column_stack([1.0 - wt, wt])[tail]
        wn = ck.smoothstep(0.20, 0.36, zz)
        neck = (zz >= 0.20) & (zz < 0.36)
        J[neck, 1] = inn
        W[neck] = np.column_stack([1.0 - wn, wn])[neck]
        wh = ck.smoothstep(0.36, 0.46, zz)
        head = zz >= 0.36
        J[head] = (inn, ih)
        W[head] = np.column_stack([1.0 - wh, wh])[head]
        return J, W

    ck.finish(mesh, P, T, "plumage", col, bones, cavity=cav, emission=glow * 0.6)

    # the brows: a raptor's scowl over each eye
    for sx in (1.0, -1.0):
        Pb, Tb = _ellipsoid((0.0, 0.0, 0.0), (0.014, 0.006, 0.036), 4, 8)
        Pb = ck.transform(Pb, ck.euler(10.0, sx * 8.0, -sx * 34.0), (sx * 0.060, 0.379, 0.503))
        ck.finish(mesh, Pb, Tb, "plumage", FOAM * 0.97, ih, cavity=0.1)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    ih = rig.index("head")
    r = 0.015
    for sx in (1.0, -1.0):
        c = np.array([sx * 0.0655, 0.366, 0.497])
        Pe, Te = _ellipsoid((0.0, 0.0, 0.0), (r, r, r), 8, 12)
        Pe = ck.transform(Pe, ck.rot_z(-90.0 * sx) @ ck.rot_y(-sx * 18.0), c)
        cosang = ((Pe - c) @ _unit((sx, 0.05, 0.3))) / r
        ring = ck.smoothstep(0.92, 0.87, cosang)
        col = ck.mix(PAL["lacquer_black"], PAL["sun_gold"] * 0.92, ring[:, None])
        ck.finish(mesh, Pe, Te, "eye", col, ih, wet=1.0 - 0.7 * ring)


def _beak_tube(z, y, rad, segs, squash):
    path = np.column_stack([np.zeros(len(z)), y, z])
    return _tube(path, rad, segs, squash=squash)


def beak(mesh: ck.Mesh, rig: ck.Rig) -> None:
    ih, ij = rig.index("head"), rig.index("beak")
    # the upper mandible: deep and compressed, the culmen arching into a raptor's curled hook
    s = np.linspace(0.0, 1.0, 10)
    z = 0.545 + 0.15 * s
    y = 0.345 + 0.006 * np.sin(math.pi * s) - 0.012 * s * s
    th = np.radians(np.linspace(25.0, 150.0, 5))
    rc = 0.022
    z = np.concatenate([z, z[-1] + rc * np.sin(th)])
    y = np.concatenate([y, y[-1] - rc * (1.0 - np.cos(th))])
    rad = np.concatenate([np.interp(s, (0.0, 0.45, 1.0), (0.034, 0.027, 0.017)), np.linspace(0.014, 0.003, 5)])
    P, T = _beak_tube(z, y, rad, 10, 0.6)
    hook = ck.smoothstep(0.672, 0.70, P[:, 2])
    col = ck.mix(HORN, PAL["tortoiseshell"], (0.85 * hook)[:, None])
    gape = ck.smoothstep(0.330, 0.318, P[:, 1]) * (1.0 - hook)
    ck.finish(mesh, P, T, "beak", col, ih, wet=0.15, cavity=gape * 0.7)
    # the lower mandible (the "beak" bone opens it), with the gull's angle at the gonys
    s = np.linspace(0.0, 1.0, 9)
    z = 0.548 + 0.137 * s
    y = 0.321 - 0.013 * np.sin(math.pi * s * 0.9)
    rad = np.interp(s, (0.0, 0.6, 0.85, 1.0), (0.024, 0.015, 0.010, 0.003))
    P, T = _beak_tube(z, y, rad, 8, 0.78)
    spot = np.exp(-((P[:, 2] - 0.664) / 0.010) ** 2)
    col = ck.mix(HORN, PAL["tortoiseshell"], (0.8 * spot)[:, None])
    ck.finish(mesh, P, T, "beak", col, ij, wet=0.15, cavity=0.2)


def hook(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The lamp-diver's bone hook: its point lodged in the throat, the shank, lashing and a few centimetres of
    line hanging out; the wound around it glows (the weak point)."""
    inn = rig.index("neck")
    shank = ck.bezier([THROAT + (0.004, 0.012, -0.004), THROAT + (-0.004, -0.02, 0.02), THROAT + (-0.012, -0.052, 0.034)], 7)
    P, T = _tube(shank, np.linspace(0.0055, 0.0045, 7), 6)
    col = PAL["bone"] * (0.86 + 0.08 * ck.fbm(P * 90.0, SEED + 9))[:, None]
    ck.finish(mesh, P, T, "beak", col, inn, cavity=0.25)
    knot_c = THROAT + (-0.011, -0.046, 0.031)
    Pk, Tk = _ellipsoid(knot_c, (0.008, 0.007, 0.008), 4, 6)
    ck.finish(mesh, Pk, Tk, "wrack", PAL["timber_weathered"], inn, cavity=0.4)
    line = ck.bezier([knot_c, knot_c + (-0.004, -0.03, -0.005), knot_c + (0.004, -0.06, -0.018), knot_c + (0.0, -0.085, -0.03)], 8)
    Pl, Tl = _tube(line, 0.0022, 4, cap_start=False)
    ck.finish(mesh, Pl, Tl, "wrack", PAL["timber_weathered"] * 0.9, inn)
    # the wound's lip
    Pw, Tw = _ellipsoid(THROAT + (0.0, 0.004, 0.0), (0.018, 0.010, 0.016), 4, 8)
    ck.finish(mesh, Pw, Tw, "plumage", PAL["spawn_wound"] * 0.6, inn, emission=1.0, cavity=0.2)


def _blade_colors(info, top_col, bot_col):
    return np.where(info["top"][:, None], top_col, bot_col)


def wing(mesh: ck.Mesh, rig: ck.Rig, side: float) -> None:
    tag = "l" if side > 0 else "r"
    rng = np.random.default_rng(SEED + (11 if side > 0 else 29))
    parts = []  # (P, N, T, colour, slot, bone, cavity, uv)

    # the covert mass: an airfoil loft from the wing root to the end of the hand
    segs = 10
    xs = np.concatenate([np.linspace(0.0, 0.70, 9), np.linspace(0.78, 1.12, 5)])
    th = np.arange(segs) * (2.0 * math.pi / segs)
    f = (1.0 - np.cos(th)) * 0.5
    upper = np.sin(th) >= -1e-9
    rows, centre = [], []
    for x in xs:
        h, le, ch, tk = (float(_f(p, x)) for p in (H_PTS, LE_PTS, CHORD_PTS, THICK_PTS))
        yt = 2.6 * tk * (1.0 - f) * np.sqrt(f)
        y = h + np.where(upper, yt, -0.45 * yt)
        rows.append(np.column_stack([np.full(segs, x), y, le - ch * f]))
        centre.append(np.tile([x, h, le - ch * 0.35], (segs, 1)))
    P = np.vstack(rows)
    C = np.vstack(centre)
    T = _outward(P, ck.grid_tris(len(xs), segs, True), C)
    last = (len(xs) - 1) * segs
    tipc = len(P)
    P = np.vstack([P, C[last][None] + (0.012, 0.0, 0.0)])
    cap = np.asarray([(last + k, last + (k + 1) % segs, tipc) for k in range(segs)], dtype=np.int64)
    C = np.vstack([C, C[last][None]])
    T = np.vstack([T, _outward(P, cap, C)])
    n_up = np.concatenate([np.tile(np.where(upper, 1.0, 0.0), len(xs)), [1.0]])
    hand = ck.smoothstep(0.80, 1.10, P[:, 0])
    top_c = ck.mix(MANTLE, ck.mix(MANTLE, PAL["overcast_slate"], 0.5), hand[:, None])
    top_c = top_c * (1.0 + 0.05 * ck.fbm(P * 9.0, SEED + 4))[:, None]
    lead = np.concatenate([np.tile(ck.smoothstep(0.12, 0.0, f), len(xs)), [0.0]])
    top_c = ck.mix(top_c, ck.mix(MANTLE, FOAM, 0.5), (0.5 * lead)[:, None])
    col = np.where(n_up[:, None] > 0.5, top_c, FOAM * 0.97)
    parts.append((P, None, T, col, "plumage", "chain", 0.1, None))

    def add_blade(P, N, T, info, col, bone, cav):
        parts.append((P, N, T, col, "plumage", bone, cav, info["uv"]))

    def base_cavity(info, k=0.45):
        return k * (1.0 - ck.smoothstep(0.0, 0.45, info["t"]))

    # primaries P1 (inner) .. P10 (outer), roots along the hand
    lengths = (0.24, 0.26, 0.285, 0.31, 0.335, 0.355, 0.375, 0.39, 0.40, 0.375)
    broken = {6: (0.72, (0.18, 0.32))} if side < 0 else {7: (0.9, (0.05, 0.22))}
    for i in range(10):
        k = i / 9.0
        x0 = 0.70 + 0.22 * k
        L = lengths[i] + rng.uniform(-0.012, 0.008)
        cut = (rng.uniform(0.0, 0.10), rng.uniform(0.02, 0.16)) if i >= 4 else (0.0, rng.uniform(0.0, 0.05))
        floor = 0.0
        if i in broken:
            L *= broken[i][0]
            cut = broken[i][1]
            floor = 0.45
        phi = 28.0 + 38.0 * k ** 0.8
        root = (x0, float(_f(H_PTS, x0)) + 0.0025 * i, float(_f(LE_PTS, x0)) - 0.05)
        P, N, T, info = blade(root, _wing_dir(x0, phi, L), L, 0.072 - 0.012 * k, K=7, lead=0.33, bend=-0.05,
                              tip_start=0.62, cut=cut, floor=floor, thick=0.005, seed=i + (0 if side > 0 else 20))
        t = info["t"]
        tb = 0.62 - 0.42 * k + rng.uniform(-0.03, 0.03)
        dark = ck.smoothstep(tb - 0.05, tb + 0.05, t)
        fade = rng.uniform(0.0, 0.35)  # sun-faded tips
        tip_dark = ck.mix(TIPS, PAL["overcast_slate"], fade)
        top_c = ck.mix(MANTLE, tip_dark, dark[:, None])
        if i >= 8:  # the white "mirror" near the tip of the outer two
            mirror = ck.smoothstep(0.80, 0.84, t) * ck.smoothstep(0.95, 0.91, t) * (info["across"] < 0.5)
            top_c = ck.mix(top_c, FOAM * 0.95, (0.85 * mirror)[:, None])
        elif i <= 4:  # a pale tip on the inner ones
            top_c = ck.mix(top_c, FOAM, ck.smoothstep(0.93, 1.0, t)[:, None])
        bot_c = ck.mix(FOAM * 0.95, ck.mix(TIPS, PAL["overcast_slate"], 0.3), (0.95 * dark)[:, None])
        add_blade(P, N, T, info, _blade_colors(info, top_c, bot_c), "wrist", base_cavity(info))

    # primary coverts over the primaries' bases
    for i in range(7):
        k = i / 6.0
        x0 = 0.70 + 0.20 * k
        phi = 30.0 + 34.0 * k
        root = (x0, float(_f(H_PTS, x0)) + 0.012 + 0.002 * i, float(_f(LE_PTS, x0)) - 0.03)
        P, N, T, info = blade(root, _wing_dir(x0, phi, 0.13), 0.13, 0.055, K=5, lead=0.4, tip_start=0.4,
                              thick=0.004, seed=40 + i)
        top_c = ck.mix(MANTLE, TIPS, 0.15 + 0.55 * k * ck.smoothstep(0.4, 1.0, info["t"])[:, None])
        add_blade(P, N, T, info, _blade_colors(info, top_c, FOAM * 0.95), "wrist", base_cavity(info, 0.3))

    # secondaries along the forearm, with the gull's white trailing edge
    for i in range(12):
        k = i / 11.0
        x0 = 0.19 + 0.49 * k
        L = 0.205 - 0.022 * k + rng.uniform(-0.008, 0.006)
        root = (x0, float(_f(H_PTS, x0)) + 0.0015 * (11 - i), float(_f(LE_PTS, x0)) - 0.07)
        cut = (rng.uniform(0.0, 0.06), rng.uniform(0.0, 0.10))
        P, N, T, info = blade(root, _wing_dir(x0, -2.0 + 20.0 * k ** 1.5, L), L, 0.07, K=6, lead=0.4,
                              tip_start=0.6, floor=0.35, cut=cut, bend=-0.03, seed=60 + i)
        t = info["t"]
        top_c = ck.mix(MANTLE * (0.97 + 0.06 * rng.uniform()), FOAM, ck.smoothstep(0.84, 0.92, t)[:, None])
        bot_c = ck.mix(FOAM * 0.97, ck.mix(FOAM, PAL["overcast_slate"], 0.3), ck.smoothstep(0.5, 0.9, t)[:, None])
        add_blade(P, N, T, info, _blade_colors(info, top_c, bot_c), _arm_bone(x0), base_cavity(info))

    # tertials, long and inward over the body's flank
    for i in range(3):
        x0 = 0.10 + 0.035 * i
        root = (x0, float(_f(H_PTS, x0)) + 0.008 + 0.002 * (2 - i), 0.06)
        P, N, T, info = blade(root, _wing_dir(x0, -14.0 + 4.0 * i, 0.22), 0.22, 0.072, K=6, lead=0.45,
                              tip_start=0.6, floor=0.3, bend=-0.02, seed=80 + i)
        top_c = ck.mix(MANTLE, FOAM, ck.smoothstep(0.86, 0.95, info["t"])[:, None])
        add_blade(P, N, T, info, _blade_colors(info, top_c, FOAM * 0.97), "shoulder", base_cavity(info))

    # greater and median coverts in overlapping rows over the secondaries
    for row, (n, x_a, x_b, back, L, wdt, dy) in enumerate(((12, 0.17, 0.69, 0.05, 0.115, 0.06, 0.011),
                                                           (10, 0.15, 0.67, 0.025, 0.085, 0.05, 0.020))):
        for i in range(n):
            k = i / (n - 1.0)
            x0 = x_a + (x_b - x_a) * k
            root = (x0, float(_f(H_PTS, x0)) + dy + 0.0015 * (n - i) / n, float(_f(LE_PTS, x0)) - back)
            P, N, T, info = blade(root, _wing_dir(x0, 3.0 * row + 18.0 * k ** 1.5, L), L, wdt, K=5, lead=0.45,
                                  tip_start=0.35, thick=0.004, seed=100 + 20 * row + i)
            tone = 1.0 + rng.uniform(-0.03, 0.04)
            top_c = ck.mix(MANTLE * tone, FOAM, 0.06 + 0.06 * row)
            add_blade(P, N, T, info, _blade_colors(info, np.broadcast_to(top_c, (len(P), 3)), FOAM * 0.97),
                      _arm_bone(x0), base_cavity(info, 0.3))

    # scapulars: the mantle's long feathers over the wing root (blended body -> shoulder)
    for i in range(4):
        x0 = 0.05 + 0.03 * i
        root = (x0, 0.325 + 0.004 * (3 - i), 0.12 - 0.05 * i)
        P, N, T, info = blade(root, _unit((0.35 + 0.1 * i, -0.05, -1.0)), 0.17, 0.07, K=5, lead=0.5,
                              tip_start=0.5, thick=0.004, seed=120 + i)
        top_c = ck.mix(MANTLE, FOAM, 0.04 * i)
        add_blade(P, N, T, info, _blade_colors(info, np.broadcast_to(top_c, (len(P), 3)), MANTLE * 0.9),
                  "scap", base_cavity(info, 0.25))

    m = np.array([side, 1.0, 1.0])
    chain = rig.chain([f"shoulder_{tag}", f"elbow_{tag}", f"wrist_{tag}"],
                      [np.multiply(p, m) for p in (SHOULDER, ELBOW, WRIST, TIP)])
    scap = rig.blend("body", f"shoulder_{tag}", np.multiply((0.03, 0.31, 0.0), m), np.multiply((0.14, 0.31, 0.0), m))
    for P, N, T, col, slot, bone, cav, uv in parts:
        if side < 0:
            P, N, T = _mirror(P, N, T)
        if bone == "chain":
            b = chain
        elif bone == "scap":
            b = scap
        else:
            b = rig.index(f"{bone}_{tag}")
        ck.finish(mesh, P, T, slot, col, b, cavity=cav, uv=uv, N=N)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    it = rig.index("tail")
    n = 11
    for i in range(n):
        k = i / (n - 1.0) * 2.0 - 1.0
        phi = 34.0 * k
        L = 0.22 + 0.02 * abs(k)
        ph = math.radians(phi)
        root = (0.03 * k, 0.252 + 0.004 * (1.0 - abs(k)), -0.36)
        P, N, T, info = blade(root, (math.sin(ph), 0.03, -math.cos(ph)), L, 0.062, K=5, lead=0.5 - 0.1 * k,
                              tip_start=0.55, floor=0.35, thick=0.004, seed=140 + i)
        t = info["t"]
        top_c = ck.mix(ck.mix(FOAM, MANTLE, 0.35), FOAM, ck.smoothstep(0.2, 0.6, t)[:, None])
        ck.finish(mesh, P, T, "plumage", _blade_colors(info, top_c, FOAM * 0.95), it,
                  cavity=0.35 * (1.0 - ck.smoothstep(0.0, 0.5, t)), uv=info["uv"], N=N)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Legs tucked in flight, the webbed feet trailing under the tail with hooked claws."""
    for sx, tag in ((1.0, "l"), (-1.0, "r")):
        il = rig.index(f"leg_{tag}")
        m = np.array([sx, 1.0, 1.0])
        a = np.multiply((0.07, 0.115, -0.13), m)
        b = np.multiply(ANKLE, m)
        P, T = _tube(ck.bezier([a, (a + b) / 2 + (0, -0.01, 0), b], 5), np.linspace(0.016, 0.011, 5), 8,
                       squash=0.75)
        ck.finish(mesh, P, T, "beak", HORN * 0.92, il, cavity=0.2)
        for k, spread in enumerate((-20.0, 0.0, 20.0)):
            d = ck.rot_y(spread * sx) @ _unit((0.0, -0.25, -1.0))
            p1 = b + d * 0.085
            P, T = _tube(ck.bezier([b, (b + p1) / 2 + (0, 0.004, 0), p1], 5), np.linspace(0.008, 0.005, 5), 6)
            ck.finish(mesh, P, T, "beak", HORN * 0.9, il, cavity=0.15)
            claw = ck.bezier([p1, p1 + d * 0.018 + (0, -0.004, 0), p1 + d * 0.026 + (0, -0.02, 0)], 5)
            P, T = _tube(claw, np.linspace(0.005, 0.0012, 5), 6, cap_start=False)
            ck.finish(mesh, P, T, "beak", ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.5), il, wet=0.2)
        P, N, T, info = blade(b + (0, -0.004, 0), _unit((0.0, -0.25, -1.0)), 0.075, 0.065, K=4, lead=0.5,
                              tip_start=0.6, floor=0.6, thick=0.002, cup=-0.3, seed=150)
        ck.finish(mesh, P, T, "beak", HORN * 0.8, il, cavity=0.3, N=N)


def wrack(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    """A hank of torn net-twine and kelp caught on the right foot, trailing under the tail."""
    names = [f"twine_{i}" for i in range(len(TWINE_PTS) - 1)]
    chain = rig.chain(names, TWINE_PTS)
    pts = np.asarray(TWINE_PTS)
    for k in range(3):
        off = np.array([(k - 1) * 0.016, (k % 2) * 0.012, 0.0])
        ctrl = pts + np.vstack([[0, 0, 0], off * 0.5, off * 1.4 + rng.uniform(-0.02, 0.02, 3), off * 2.4])
        end = 1.0 - 0.18 * k  # frayed: the strands end at different lengths
        path = ck.bezier(ctrl, 16)[: max(int(16 * end), 4)]
        twist = np.sin(np.linspace(0, 6.0, len(path)) + k) * 0.004
        path = path + np.column_stack([twist, np.zeros(len(path)), np.cos(np.linspace(0, 6.0, len(path)) + k) * 0.004])
        P, T = _tube(path, 0.0055, 5)
        col = PAL["timber_weathered"] * (0.9 + 0.12 * ck.fbm(P * 40.0, SEED + 20 + k))[:, None]
        ck.finish(mesh, P, T, "wrack", col, chain, wet=0.35, cavity=0.2)
    # knots and the remains of a net mesh across the strands
    for c in (pts[0] + (0, -0.03, -0.02), pts[1] + (0.0, -0.01, 0.0), pts[2] + (0.004, 0.02, 0.01)):
        Pk, Tk = _ellipsoid(c, (0.012, 0.010, 0.012), 4, 6)
        ck.finish(mesh, Pk, Tk, "wrack", PAL["timber_weathered"] * 0.85, chain, wet=0.4, cavity=0.4)
    for f in (0.3, 0.9):
        q = pts[1] + (pts[2] - pts[1]) * f
        P, T = _tube(np.array([q + (-0.022, 0.0, 0.0), q + (0.0, -0.01, 0.01), q + (0.024, 0.004, 0.0)]), 0.0035, 4)
        ck.finish(mesh, P, T, "wrack", PAL["timber_weathered"] * 0.8, chain, wet=0.35)
    # two kelp ribbons, wet and ruffled
    for k, (L, wdt, side) in enumerate(((0.42, 0.05, 1.0), (0.31, 0.04, -1.0))):
        root = pts[1] + (0.008 * side, -0.01, 0.0)
        d = _unit(pts[3] - pts[1] + (0.03 * side, -0.05 * k, 0.04 * k))
        P, N, T, info = blade(root, d, L, wdt, K=10, lead=0.5, tip_start=0.7, thick=0.002, cup=0.1,
                              n_hint=(1.0, 0.0, 0.0), wave=(0.022, 1.3), ruffle=(0.008, 4.0), seed=170 + k)
        t = info["t"]
        col = ck.mix(PAL["foliage_shadow"], ck.mix(PAL["foliage_shadow"], PAL["timber_weathered"], 0.5),
                     ck.smoothstep(0.5, 1.0, t)[:, None])
        ck.finish(mesh, P, T, "wrack", col, chain, wet=0.85, uv=info["uv"], N=N)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    rng = np.random.default_rng(SEED)
    mesh = ck.Mesh("gull_harrier")
    body(mesh, rig)
    eyes(mesh, rig)
    beak(mesh, rig)
    hook(mesh, rig)
    wing(mesh, rig, 1.0)
    wing(mesh, rig, -1.0)
    tail(mesh, rig)
    legs(mesh, rig)
    wrack(mesh, rig, rng)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
# Wing poses in the left wing's convention: (shoulder, elbow, wrist) rotations in degrees about the rest axes.
# +rz raises the wing, +ry sweeps it back, +rx pitches the leading edge down. The right wing mirrors (ry, rz).
W_UP = ((0, 8, 40), (0, 0, -10), (0, 6, 14))  # the top of the upstroke
W_DOWN = ((8, -4, -34), (0, 0, 6), (4, -4, -12))  # the bottom of the downstroke
W_GLIDE = ((0, 2, 12), (0, 0, 4), (0, 4, -14))  # the crooked "M"
W_GLIDE2 = ((2, 2, 9), (0, 0, 5), (0, 4, -17))
W_FLEX = ((0, 14, 26), (0, -18, 0), (0, 30, 6))  # mid-upstroke, the hand flexed back
W_HALF = ((0, 34, 22), (0, -45, 0), (0, 62, -8))  # half folded back (the dive)
W_TUCK = ((0, 48, 30), (0, -60, 0), (0, 82, -10))  # mid-fall: swept back, lifted by the air
KO_PITCH = 10.0  # the body's pitch lying on its breast
KO_SETTLE = -0.05  # the body's drop below the root at rest on the ground
W_SPREAD = ((-6, -8, 44), (0, 0, -4), (0, -6, 12))  # spread wide and held (the cry)
W_FLARE = ((-14, -6, 30), (0, 0, -6), (0, -10, 10))  # braking over the rake


def _wing_key(clip: ck.Clip, t: float, pose, tags=("l", "r")) -> None:
    for tag in tags:
        s = 1.0 if tag == "l" else -1.0
        for bone, r in zip(("shoulder", "elbow", "wrist"), pose):
            clip.key(f"{bone}_{tag}", t, (r[0], r[1] * s, r[2] * s))


def _twine_sway(clip: ck.Clip, amp: float = 1.0) -> None:
    for i in range(3):
        clip.wave(f"twine_{i}", amp_rot=(9.0 * amp * (1 + 0.3 * i), 0.0, 5.0 * amp), cycles=1, phase=-0.7 * i - 0.5)


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 1.6, loop=True)
    for t, pose, bob, pitch in ((0.0, W_UP, 0.0, 0.0), (0.42, W_DOWN, 0.06, -2.5), (0.8, W_GLIDE, 0.048, -1.0),
                                (1.22, W_GLIDE2, 0.008, 1.0), (1.42, W_FLEX, 0.0, 0.5), (1.6, W_UP, 0.0, 0.0)):
        _wing_key(idle, t, pose)
        idle.key("body", t, (pitch, 0, 0), (0, bob, 0))
        idle.key("neck", t, (-pitch, 0, 0), (0, -0.85 * bob, 0))  # the head holds still
        idle.key("tail", t, (-3.0 * pitch, 0, 0))
    for i in range(3):
        idle.key(f"twine_{i}", 0.0, (0, 0, 0))
        idle.key(f"twine_{i}", 0.5 + 0.1 * i, (-10.0 - 4 * i, 0, 4.0))
        idle.key(f"twine_{i}", 1.05 + 0.1 * i, (8.0 + 3 * i, 0, -3.0))
        idle.key(f"twine_{i}", 1.6, (0, 0, 0))

    attack = ck.Clip("attack", 1.4)
    for t, pose, root, bodyr, leg, neck in (
        (0.0, W_GLIDE, (0, 0, 0), (0, 0, 0), 0, 0),
        (0.12, W_DOWN, (0, 0.20, -0.04), (-6, 0, 0), 0, 6),  # the tell: two quick beats, climbing
        (0.24, W_UP, (0, 0.34, -0.08), (-8, 0, 0), 0, 8),
        (0.36, W_DOWN, (0, 0.52, -0.10), (-10, 0, 0), 0, 10),
        (0.47, W_HALF, (0, 0.60, -0.08), (4, 0, 0), -10, 0),  # fold half back and tip over
        (0.62, W_HALF, (0, 0.18, 0.40), (30, 0, 0), -50, -22),  # drop forward and down
        (0.75, W_FLARE, (0, -0.32, 0.62), (-28, 0, 0), -128, 18),  # contact: talons forward, raking
        (0.86, W_FLARE, (0, -0.28, 0.70), (-14, 0, 0), -70, 10),
        (1.02, W_DOWN, (0, 0.10, 0.32), (-6, 0, 0), -20, 4),  # swing back up
        (1.2, W_UP, (0, 0.06, 0.08), (-2, 0, 0), -5, 0),
        (1.4, W_GLIDE, (0, 0, 0), (0, 0, 0), 0, 0),
    ):
        _wing_key(attack, t, pose)
        attack.key("root", t, loc=root)
        attack.key("body", t, bodyr)
        attack.key("neck", t, (neck, 0, 0))
        attack.key("leg_l", t, (leg, 0, 0))
        attack.key("leg_r", t, (leg * 0.92, 0, 0))
        attack.key("tail", t, (-0.4 * bodyr[0], 0, 0))
    for i in range(3):  # the twine trails the dive and whips through the rake
        for t, r in ((0.0, 0), (0.47, 10), (0.62, -40), (0.8, 35), (1.0, -20), (1.4, 0)):
            attack.key(f"twine_{i}", t, (r * (1.0 + 0.25 * i), 0, 0))
    for t, r in ((0.0, 0), (0.62, 0), (0.72, 24), (0.86, 6), (1.0, 0)):  # a snap of the beak through the strike
        attack.key("beak", t, (r, 0, 0))

    cast = ck.Clip("cast", 1.2)
    for t, pose, rear, root, beak_r in (
        (0.0, W_GLIDE, 0, (0, 0, 0), 0),
        (0.35, W_SPREAD, -36, (0, 0.14, -0.06), 34),
        (0.6, W_SPREAD, -38, (0, 0.16, -0.06), 38),
        (0.85, W_SPREAD, -34, (0, 0.13, -0.05), 30),
        (1.2, W_GLIDE, 0, (0, 0, 0), 0),
    ):
        _wing_key(cast, t, pose)
        cast.key("body", t, (rear, 0, 0))
        cast.key("root", t, loc=root)
        cast.key("neck", t, (0.35 * rear, 0, 0))
        cast.key("head", t, (0.25 * rear, 0, 0))
        cast.key("beak", t, (beak_r, 0, 0))
        cast.key("tail", t, (0.6 * rear, 0, 0))
        cast.key("leg_l", t, (0.5 * rear, 0, 0))
        cast.key("leg_r", t, (0.5 * rear, 0, 0))
    _twine_sway(cast, 0.8)

    hit = ck.Clip("hit", 0.6)
    buckle = ((6, 30, -24), (0, -38, 14), (0, 44, -26))
    flail = ((-6, 0, 46), (0, 0, -8), (0, -4, 18))
    for t, l_pose, r_pose, root, roll, neck in (
        (0.0, W_GLIDE, W_GLIDE, (0, 0, 0), 0, 0),
        (0.08, flail, buckle, (0, -0.08, -0.04), 14, -16),
        (0.24, flail, buckle, (0, -0.25, -0.06), 20, -6),
        (0.42, W_DOWN, W_DOWN, (0, -0.12, -0.02), 6, 2),
        (0.6, W_GLIDE, W_GLIDE, (0, 0, 0), 0, 0),
    ):
        _wing_key(hit, t, l_pose, ("l",))
        _wing_key(hit, t, r_pose, ("r",))
        hit.key("root", t, loc=root)
        hit.key("body", t, (-0.3 * roll, 0, roll))
        hit.key("neck", t, (neck, 0, -0.5 * roll))
    for i in range(3):
        for t, r in ((0.0, 0), (0.1, 25), (0.3, -18), (0.6, 0)):
            hit.key(f"twine_{i}", t, (r * (1 + 0.3 * i), 0, 0))

    ko = ck.Clip("ko", 1.4)
    spread = ((0, -6, 30), (0, -6, 0), (0, 14, -36))  # the far wing, left spread and draped
    crumple = ((0, 40, -21), (0, -45, 0), (0, 62, -12))  # the near wing, half folded on the ground
    for t, l_pose, r_pose, drop, bodyr, neck, head in (
        (0.0, W_GLIDE, W_GLIDE, 0.0, (0, 0, 0), 0, 0),
        (0.16, W_UP, W_UP, -0.04, (-10, 0, 0), -24, -10),  # struck: the wings jerk up, the head back
        (0.45, W_HALF, W_HALF, 0.18, (14, 0, 3), -10, 0),  # the wings fold and it falls
        (0.8, W_TUCK, W_TUCK, 0.68, (24, 0, 5), 10, 10),
        (1.02, W_HALF, crumple, 1.05, (14, 0, 7), 16, 6),  # it hits the ground breast first
        (1.2, spread, crumple, 1.05, (KO_PITCH, 0, 6), 20, -2),
        (1.4, spread, crumple, 1.05, (KO_PITCH, 0, 6), 21, -2),
    ):
        _wing_key(ko, t, l_pose, ("l",))
        _wing_key(ko, t, r_pose, ("r",))
        ko.key("root", t, loc=(0, -drop, 0))
        ko.key("body", t, bodyr, (0, KO_SETTLE * min(drop / 1.05, 1.0), 0))
        ko.key("neck", t, (neck, 0, 0))
        ko.key("head", t, (head, 0, 0))
        ko.key("tail", t, (min(drop, 1.0) * 12.0, 0, 0))
    for i in range(3):  # the twine streams up in the fall and lies along the ground after
        for t, r in ((0.0, 0), (0.6, -30), (1.05, -10), (1.25, 14 - 4 * i), (1.4, 18 - 4 * i)):
            ko.key(f"twine_{i}", t, (r, 0, 0))
    for t, r in ((0.0, 0), (0.16, 20), (0.6, 8), (1.4, 10)):
        ko.key("beak", t, (r, 0, 0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "gull_harrier"})
    print(f"gull_harrier: {info}")


if __name__ == "__main__":
    main()
