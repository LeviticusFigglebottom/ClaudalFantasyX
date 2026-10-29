"""Ilun, the Net-Warden, Asha's Vowbound (M3-CRE-638; final pass M3-CRB-008): docs/kb/art/creatures/vowbound/ilun.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/ilun/build_ilun.py -- --out assets/creatures/ilun/ilun.glb

A vast spectral manta ray with a heron's crest: wings 5.1 m across, swept back to pointed tips, over a thick domed
disc with a broad blunt head, two cephalic lobes rolled forward into scrolls, gill slits and a mouth that hold a little
of his light, and a long whip tail with a small dorsal fin. Three long heron plumes (and two short ones) sweep back
from the crown. His wing membranes thin to soft rippled trailing edges and carry a knotted fishing net drawn in light:
continuous cords laid in the wing's own chord-and-span coordinates (so they follow its curvature), a heavier head-rope
round the net's edge, and a bead at every crossing, all `glimmer_bound` (the knots brightest). A child's glass
net-float in a cord net hangs from the tail tip: the keepsake, the one part of him that is not light.

**Built hovering.** The origin is the water point under him and the rest pose floats with the disc's mid-plane at
HOVER_Y (1.35 m), so the stand-in needs no `hover` and the battle's VFX anchors (fractions of battle_sandbox.json's
2.3 m height from the water) land on him: chest on the disc's rear half, head over the crest. The disc sits forward of
the origin (toward the foes) so the tail and the float stay inside the battle HUD's safe frame. Every clip stays above
the water.

Rig (20 bones): `root`, `body`, `wing_l0..3` and `wing_r0..3` (+x is `l`), `tail_0..4`, `crest_0`, `crest_1`, `float`,
and two unweighted VFX anchors: `vfx_core` (the disc's centre, on `body`) and `vfx_keepsake` (the float, on `float`).

`python3 build_ilun.py --report` prints the triangle count, per-part counts and per-clip lows (numpy, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding  # noqa: E402

SEED = 6380
PAL = {k: ck.hexrgb(v) for k, v in {
    "deep_teal_shadow": "#0E4A55", "sea_glow": "#1C6B78", "lagoon_teal": "#1FA3A6", "reef_blue": "#1569A0",
    "salt_glass": "#BFE6E0", "foam_white": "#EEF6F4", "gauze_white": "#EBE7DF", "sand_cloth": "#C9B48E",
    "sand_wet": "#B59D74", "lacquer_black": "#1D1916",
}.items()}

# ---- planform (metres, Godot axes, facing +z) ------------------------------------------------
HOVER_Y = 1.35  # the disc's mid-plane above the water (the origin)
SPAN = 2.55  # half the wingspan
NOSE_Z = 1.85  # the blunt head's front
REAR_Z = -0.13  # the rear of the body, where the tail starts
TIP_Z = -0.15  # the wingtips, swept back (falcate)
DISC_Z = 0.87  # the disc's centre (the body bone, vfx_core)
HEAD_U = 0.12  # the head's half-width (fraction of the half span): the front is flat across it
TE_RISE = 0.45  # the trailing edge's concave sweep forward from the body to mid-wing
TIP_SWEEP = REAR_Z + TE_RISE - TIP_Z  # the trailing edge sweeps back again to meet the tip
LE_POW = 1.12  # the leading edge's sweep
SHOULDER = 0.2  # the mantle: the wings rise from the body (most at mid-span) ...
DROOP = 0.4  # ... and arch down to the tips, a canopy (a heron mantling), so the near wing shows its back
TOP_CORE, BOT_CORE = 0.27, 0.15  # the body's thickness above and below the mid-plane
TOP_WING, BOT_WING = 0.08, 0.05  # the membrane's at the wing root
SKIN_MIN = 0.004  # the thinnest edge
CORE_W = 0.5  # how far out the body's dome reaches
RIPPLE_A, RIPPLE_N = 0.07, 3.5  # the trailing edge's frozen ripple: height and waves along the span
ROWS, SEGS = 81, 46  # span stations (odd: one on the midline) and vertices round each section
WING_X = [0.5, 1.15, 1.7, 2.15, SPAN + 0.02]  # wing_0 .. wing_3 spans, out from the midline
WING_Z = 0.6  # the wing hinges' line
BODY_SLOT_X = 0.62  # triangles wholly beyond this are the membrane slot

# ---- the net -----------------------------------------------------------------------------------
NET_U0, NET_U1 = 0.25, 0.95  # the net spans these fractions of the half span
NET_INSET = 0.07  # metres in from the leading and trailing edges
NET_NQ, NET_NP = 4, 7  # diamonds across the chord and along the span
NET_WARP = 0.016  # hand-knotted: the lattice warped by up to this (net coordinates)
NET_W, ROPE_W = 0.042, 0.06  # cord and head-rope widths
NET_CHORD_FULL, NET_W_MIN = 0.8, 0.35  # Polish 2: cords full width where the net's chord is this wide, down to 35%
NET_OFF = 0.007  # off the membrane
NET_STEP_TOP, NET_STEP_BOT = 0.055, 0.1  # sampling along the cords (metres): the back is seen closer
KNOT_R, KNOT_H = 0.034, 0.01  # bead half-diagonal and height
NET_GLOW, ROPE_GLOW, KNOT_GLOW = 0.72, 0.85, 1.0  # emission masks: the knots brightest

# ---- tail, crest, float ------------------------------------------------------------------------
TAIL_R0, TAIL_R1 = 0.075, 0.009
CORD = 0.17  # the float's cord
FLOAT_R = 0.11
NET_CORD_R = 0.0055

PARTS: dict[str, int] = {}


# ---------------------------------------------------------------------------------------------
# The surface
# ---------------------------------------------------------------------------------------------
def _ramp(u):
    d = np.asarray(u, dtype=np.float64) - HEAD_U
    return 0.5 * (d + np.sqrt(d * d + 0.004))


RAMP1 = float(_ramp(1.0))


def leading(u):
    return NOSE_Z - (NOSE_Z - TIP_Z) * (_ramp(u) / RAMP1) ** LE_POW


def trailing(u):
    u = np.asarray(u, dtype=np.float64)
    return REAR_Z + TE_RISE * (1.0 - (1.0 - u) ** 3) - TIP_SWEEP * u ** 4


def mid(x):
    u = np.clip(np.abs(x) / SPAN, 0.0, 1.0)
    return HOVER_Y + SHOULDER * np.sin(math.pi * u) - DROOP * u ** 2.2


def chord_v(x, z):
    u = np.clip(np.abs(x) / SPAN, 0.0, 1.0)
    le, te = leading(u), trailing(u)
    return (z - te) / np.maximum(le - te, 1e-6)


def ripple(x, v):
    """The membrane's soft trailing edge, frozen in a ripple (the idle's twist wave moves it)."""
    u = np.clip(np.abs(np.asarray(x, dtype=np.float64)) / SPAN, 0.0, 1.0)
    te = ck.smoothstep(0.42, 0.0, v)
    return RIPPLE_A * te * ck.smoothstep(0.18, 0.55, u) * np.sin(2.0 * math.pi * RIPPLE_N * u + 0.7)


def half_thickness(x, v, top: bool):
    """Above (top) or below the mid-plane at span x and chord fraction v (0 trailing .. 1 leading edge)."""
    x = np.asarray(x, dtype=np.float64)
    u = np.clip(np.abs(x) / SPAN, 0.0, 1.0)
    core = np.exp(-(x / CORE_W) ** 2)
    T = (TOP_CORE if top else BOT_CORE) * core + (TOP_WING if top else BOT_WING) * (1.0 - u) ** 1.4 + SKIN_MIN
    vc = np.clip(v, 0.0, 1.0)
    wing = np.sin(math.pi * np.clip(vc ** 1.7 * 0.97, 0.0, 1.0)) ** 0.6  # an airfoil: thin to the trailing edge
    dome = np.sin(math.pi * np.clip(vc ** 0.85, 0.0, 1.0)) ** 0.5  # the body: a dome, the head's front rounded
    return T * (core * dome + (1.0 - core) * wing)


def relief(x, z, v, top: bool):
    """The back's spine ridge, its shoulder humps and fine skin relief (fading out over the thin membrane)."""
    x = np.asarray(x, dtype=np.float64)
    z = np.asarray(z, dtype=np.float64)
    u = np.clip(np.abs(x) / SPAN, 0.0, 1.0)
    inside = np.clip(v, 0.0, 1.0) * np.clip(1.0 - v, 0.0, 1.0) * 4.0
    fine = 0.005 * ck.fbm(np.column_stack([x.ravel() * 7.0, z.ravel() * 0.0 + 3.1, z.ravel() * 7.0]),
                          SEED + 3).reshape(x.shape) * ck.smoothstep(0.75, 0.2, u) * inside
    if not top:
        return fine * 0.6
    spine = 0.03 * np.exp(-(x / 0.07) ** 2) * ck.smoothstep(0.1, 0.35, v) * ck.smoothstep(0.95, 0.6, v)
    ax = np.abs(x)
    hump = 0.045 * np.exp(-((ax - 0.36) / 0.15) ** 2 - ((z - DISC_Z - 0.2) / 0.35) ** 2)
    brow = 0.03 * np.exp(-((ax - 0.34) / 0.07) ** 2 - ((z - NOSE_Z + 0.22) / 0.09) ** 2)
    return spine + hump + brow + fine


def surface_y(x, z, top: bool):
    v = chord_v(x, z)
    s = 1.0 if top else -1.0
    return mid(x) + ripple(x, v) + s * half_thickness(x, v, top) + relief(x, z, v, top)


def surface_normal(x, z, top: bool, h: float = 1e-3):
    dx = (surface_y(x + h, z, top) - surface_y(x - h, z, top)) / (2 * h)
    dz = (surface_y(x, z + h, top) - surface_y(x, z - h, top)) / (2 * h)
    s = 1.0 if top else -1.0
    n = np.stack([-dx * s, np.full_like(dx, s), -dz * s], axis=-1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def orient(P: np.ndarray, T: np.ndarray, want) -> np.ndarray:
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * want(P[T].mean(axis=1))).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def orient_out(P: np.ndarray, T: np.ndarray, O: np.ndarray) -> np.ndarray:
    """Winds each triangle to face the mean of its vertices' outward vectors O."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * O[T].mean(axis=1)).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def blade(path, width, thick, curl, up_hint=(1.0, 0.0, 0.0), across: int = 5, lift=None):
    """A lofted blade along `path` (K, 3): a thin sheet `width` (K,) wide and `thick` (K,) thick whose section is an
    arc of angle `curl` (K,) radians (0 flat; ~2 pi a rolled scroll), curling toward the frames' normal. `lift` (K,)
    slides the section along its width axis (a fin set on top of its root). Ends close to points.
    Returns (P, T, ring, s): each vertex's path index and its position across (-1 .. 1)."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    tan, nrm, bin_ = ck.frames_along(path, up_hint)
    width = np.broadcast_to(np.asarray(width, dtype=np.float64), (K,))
    thick = np.broadcast_to(np.asarray(thick, dtype=np.float64), (K,))
    curl = np.broadcast_to(np.asarray(curl, dtype=np.float64), (K,))
    lift = np.zeros(K) if lift is None else np.broadcast_to(np.asarray(lift, dtype=np.float64), (K,))
    s = np.linspace(-1.0, 1.0, across)
    ring_s = np.concatenate([s, s[::-1]])
    side = np.concatenate([np.ones(across), -np.ones(across)])
    rows = []
    for k in range(K):
        th = max(float(curl[k]), 1e-4)
        R = 0.5 * width[k] / (0.5 * th)
        a = ring_s * 0.5 * th
        ob = R * np.sin(a) + lift[k]
        on = R * (1.0 - np.cos(a))
        nb, nn = -np.sin(a), np.cos(a)  # the arc's normal, toward the curl's inside
        h = 0.5 * thick[k] * side
        rows.append(path[k] + np.outer(ob + h * nb, bin_[k]) + np.outer(on + h * nn, nrm[k]))
    P = np.vstack(rows)
    n = 2 * across
    T = ck.grid_tris(K, n, True)
    tips = [path[0] - tan[0] * 0.004 + bin_[0] * lift[0], path[-1] + tan[-1] * 0.004 + bin_[-1] * lift[-1]]
    P = np.vstack([P, tips])
    caps = [(j, (j + 1) % n, len(P) - 2) for j in range(n)]
    last = (K - 1) * n
    caps += [(last + j, last + (j + 1) % n, len(P) - 1) for j in range(n)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])
    ring = np.concatenate([np.repeat(np.arange(K), n), [0, K - 1]])
    sv = np.concatenate([np.tile(ring_s, K), [0.0, 0.0]])
    mid_pts = path[ring] + bin_[ring] * lift[ring][:, None] + nrm[ring] * (0.5 * (1.0 - np.cos(0.25 * curl[ring])) *
                                                                          width[ring] / np.maximum(curl[ring], 1e-4))[:, None]
    O = P - mid_pts
    O[-2] = -tan[0]
    O[-1] = tan[-1]
    return P, orient_out(P, T, O), ring, sv


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def tail_path(n: int = 51) -> np.ndarray:
    y0 = HOVER_Y
    return ck.bezier([(0.0, y0 - 0.02, REAR_Z + 0.16), (0.0, y0 - 0.05, REAR_Z - 0.45), (0.0, y0 - 0.16, REAR_Z - 0.8),
                      (0.0, y0 - 0.48, REAR_Z - 0.86), (0.0, y0 - 0.68, REAR_Z - 0.82)], n)


def crown() -> np.ndarray:
    """The crest's root on the head's crown, behind the eyes."""
    z = NOSE_Z - 0.48
    return np.array([0.0, float(surface_y(np.array(0.0), np.array(z), True)) - 0.015, z])


def tail_points() -> np.ndarray:
    return tail_path(51)[::10]  # six points, five spans: tail_0 .. tail_4


def float_centre() -> np.ndarray:
    return tail_points()[-1] - np.array([0.0, 0.012 + CORD + FLOAT_R, 0.0])


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("body", (0, HOVER_Y, DISC_Z), (0, HOVER_Y, DISC_Z + 0.5), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        parent = "body"
        for k in range(4):
            y0, y1 = float(mid(WING_X[k])), float(mid(min(WING_X[k + 1], SPAN)))
            rig.add(f"wing_{tag}{k}", (s * WING_X[k], y0, WING_Z), (s * WING_X[k + 1], y1, WING_Z), parent)
            parent = f"wing_{tag}{k}"
    pts = tail_points()
    parent = "body"
    for k in range(5):
        rig.add(f"tail_{k}", pts[k], pts[k + 1], parent)
        parent = f"tail_{k}"
    c = crown()
    rig.add("crest_0", c, c + (0, 0.45, -0.5), "body")
    rig.add("crest_1", c + (0, 0.45, -0.5), c + (0, 0.35, -1.4), "crest_0")
    tip = pts[-1]
    rig.add("float", tip, tip - (0, 0.3, 0), "tail_4")
    # M3-CRB-008: the VFX anchors, unweighted (no vertex is skinned to them)
    core = np.array([0.0, HOVER_Y + 0.05, DISC_Z])
    rig.add("vfx_core", core, core + (0, 0.2, 0), "body")
    fc = float_centre()
    rig.add("vfx_keepsake", fc, fc - (0, 0.15, 0), "float")
    return rig


def wing_skin(rig: ck.Rig):
    """By the distance out from the midline: body, then each wing bone, blended across the span boundaries."""
    body = rig.index("body")
    wings = {s: [rig.index(f"wing_{tag}{k}") for k in range(4)] for s, tag in ((1.0, "l"), (-1.0, "r"))}
    knots = [0.0] + WING_X

    def f(P):
        n = len(P)
        J = np.zeros((n, 2), dtype=np.int64)
        W = np.zeros((n, 2))
        for i in range(n):
            x = float(P[i, 0])
            chain = [body] + wings[1.0 if x >= 0 else -1.0]
            c = min(abs(x), knots[-1] - 1e-6)
            k = int(np.searchsorted(knots, c, side="right") - 1)
            t = (c - knots[k]) / (knots[k + 1] - knots[k])
            J[i] = (chain[k], chain[k])
            W[i] = (1.0, 0.0)
            if k + 1 < len(chain) and t > 0.5:
                w = float(ck.smoothstep(0.5, 1.0, t)) * 0.5
                J[i, 1], W[i] = chain[k + 1], (1.0 - w, w)
            elif k > 0 and t < 0.5:
                w = float(ck.smoothstep(0.5, 0.0, t)) * 0.5
                J[i, 1], W[i] = chain[k - 1], (1.0 - w, w)
        return J, W

    return f


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def shell_colour(P: np.ndarray, top: np.ndarray, N: np.ndarray):
    """Layered sea tones: a dark core, a sea-glow mid-wing, lagoon toward the margins, pale thin edges; a pale belly
    with its own spots; and the faint inner light, stronger along the thin margins where the light shows through."""
    x, z = P[:, 0], P[:, 2]
    ax = np.abs(x)
    uu = np.clip(ax / SPAN, 0.0, 1.0)
    vv = np.clip(chord_v(x, z), 0.0, 1.0)
    edge = 1.0 - np.minimum(vv, 1.0 - vv) * 2.0  # 1 at the leading and trailing edges
    d_le = leading(uu) - z  # metres in from the leading edge
    d_te = z - trailing(uu)  # and from the trailing edge
    margin = np.maximum(ck.smoothstep(0.1, 0.0, d_le) * ck.smoothstep(0.12, 0.35, uu), ck.smoothstep(0.93, 1.0, uu))
    te_margin = ck.smoothstep(0.2, 0.0, d_te) * ck.smoothstep(0.12, 0.3, uu)  # the trailing edge: the softest, palest
    mott = ck.fbm(P * np.array([1.4, 1.4, 1.4]), SEED)
    fine = ck.fbm(P * np.array([5.0, 5.0, 5.0]), SEED + 11)

    back = ck.mix(PAL["deep_teal_shadow"], PAL["sea_glow"], (0.7 * ck.smoothstep(0.12, 0.6, uu))[:, None])
    back = ck.mix(back, PAL["lagoon_teal"], (0.3 * ck.smoothstep(0.6, 0.97, uu))[:, None])
    back = ck.mix(back, PAL["reef_blue"], (0.22 * ck.smoothstep(0.0, 0.45, mott))[:, None])  # cool depths
    back = ck.mix(back, PAL["deep_teal_shadow"], (0.35 * ck.smoothstep(0.0, -0.4, mott))[:, None])
    spine = np.exp(-(x / 0.12) ** 2) * ck.smoothstep(0.1, 0.4, vv)
    back = ck.mix(back, PAL["deep_teal_shadow"], (0.5 * spine)[:, None])  # the darker core
    chevron = np.exp(-((ax - 0.5) / 0.18) ** 2 - ((z - DISC_Z - 0.1 + 0.45 * (ax - 0.4)) / 0.12) ** 2)
    back = ck.mix(back, PAL["salt_glass"], (0.5 * chevron * ck.smoothstep(-0.3, 0.2, fine))[:, None])
    inner = ck.smoothstep(0.32, 0.12, np.minimum(d_le, d_te)) * ck.smoothstep(0.0, 0.08, np.minimum(d_le, d_te)) \
        * ck.smoothstep(0.15, 0.35, uu)
    back = ck.mix(back, PAL["deep_teal_shadow"], (0.3 * inner)[:, None])  # a darker band inside the pale rim
    eye_x = 0.36
    socket = np.exp(-((ax - eye_x) / 0.1) ** 2 - ((z - (NOSE_Z - 0.2)) / 0.1) ** 2)
    back = ck.mix(back, PAL["deep_teal_shadow"], (0.6 * socket)[:, None])

    belly = ck.mix(PAL["foam_white"], PAL["salt_glass"], 0.55)
    belly = ck.mix(belly, PAL["lagoon_teal"], (0.15 + 0.35 * ck.smoothstep(0.25, 0.7, uu))[:, None])
    belly = ck.mix(belly, PAL["deep_teal_shadow"], (0.55 * ck.smoothstep(0.55, 0.95, np.maximum(edge, uu)))[:, None])
    spots = ck.smoothstep(0.28, 0.4, ck.fbm(P * np.array([3.2, 3.2, 3.2]), SEED + 29)) * ck.smoothstep(0.5, 0.2, uu)
    belly = ck.mix(belly, PAL["sea_glow"], (0.55 * spots)[:, None])

    under = np.where(top, 0.0, ck.smoothstep(-0.35, -0.75, N[:, 1]))  # the flanks keep the back's tones
    col = ck.mix(back, belly, under[:, None])
    # Polish 2: at the battle camera's grazing angle the near wing went pale and the net was lost in it. The membrane
    # now deepens toward the trailing edge (reef blue into the deep teal, the light seen through more water), and
    # only a thin rim at the very edge stays pale, so the bright net reads against it.
    # The battle camera sees the near wing's underside, so the pale belly deepens the same way out on the wing.
    te_deep = ck.smoothstep(0.85, 0.15, vv) * ck.smoothstep(0.12, 0.35, uu) * ck.smoothstep(0.02, 0.12, d_te)
    deep = ck.mix(PAL["reef_blue"], PAL["deep_teal_shadow"], (0.45 + 0.3 * ck.smoothstep(-0.2, 0.3, mott))[:, None])
    deep_under = ck.mix(PAL["sea_glow"], PAL["reef_blue"], 0.4)
    col = ck.mix(col, ck.mix(deep, deep_under, under[:, None]), ((0.7 - 0.1 * under) * te_deep)[:, None])
    te_margin = te_margin * ck.smoothstep(0.08, 0.0, d_te)  # the pale trailing margin pulled in to a thin rim
    col = ck.mix(col, PAL["salt_glass"], (0.55 * np.maximum(margin, te_margin))[:, None])  # thin margins pale
    col = ck.mix(col, PAL["foam_white"], (0.25 * te_margin * ck.smoothstep(-0.1, 0.4, fine))[:, None])
    glow = 0.05 + 0.32 * np.maximum(margin, te_margin) - 0.04 * socket - 0.03 * te_deep
    glow = glow + 0.07 * ck.smoothstep(0.1, 0.5, mott) * ck.smoothstep(0.1, 0.4, uu)  # light pooled in the wing
    glow = glow + 0.05 * np.exp(-((ax - 0.42 * SPAN) / (0.3 * SPAN)) ** 2) * ck.smoothstep(0.2, 0.5, vv)
    wet = np.where(top, 0.55, 0.7)
    cav = 0.35 * socket + 0.25 * spine * (1.0 - ck.smoothstep(0.0, 0.03, np.abs(x)))
    return col, np.clip(glow, 0.0, 1.0), wet, cav


def shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The disc and wings: span stations from tip to tip (denser over the body), each a closed section; pointed tips."""
    t = np.linspace(-1.0, 1.0, ROWS)
    xs = SPAN * 0.993 * np.sign(t) * np.abs(t) ** 1.18
    a = np.arange(SEGS) * (2.0 * math.pi / SEGS)
    v = 0.5 * (np.cos(a) + 1.0)  # 1 at the leading edge (a = 0)
    side = np.sign(np.sin(a))
    X = np.repeat(xs[:, None], SEGS, axis=1)
    u = np.abs(X) / SPAN
    le, te = leading(u), trailing(u)
    Z = te + v[None] * (le - te)
    S = np.broadcast_to(side[None], X.shape)
    Yt = surface_y(X, Z, True)
    Yb = surface_y(X, Z, False)
    Y = np.where(S > 0, Yt, Yb)
    P = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
    T = ck.grid_tris(ROWS, SEGS, True)
    tips = [(-SPAN, float(mid(SPAN)), TIP_Z), (SPAN, float(mid(SPAN)), TIP_Z)]
    P = np.vstack([P, tips])
    last = (ROWS - 1) * SEGS
    caps = [(k, (k + 1) % SEGS, len(P) - 2) for k in range(SEGS)]
    caps += [(last + k, last + (k + 1) % SEGS, len(P) - 1) for k in range(SEGS)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])

    def outward(c):
        zc = 0.5 * (leading(np.abs(c[:, 0]) / SPAN) + trailing(np.abs(c[:, 0]) / SPAN))
        vc = chord_v(c[:, 0], c[:, 2])
        return np.column_stack([0.05 * c[:, 0], c[:, 1] - mid(c[:, 0]) - ripple(c[:, 0], vc), 0.05 * (c[:, 2] - zc)])

    T = orient(P, T, outward)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    top = np.concatenate([(S >= 0).reshape(-1), [True, True]])  # the edges' own row takes the back's colour
    col, glow, wet, cav = shell_colour(P, top, N)
    skin = wing_skin(rig)
    membrane_tri = (np.abs(P[T][:, :, 0]) > BODY_SLOT_X).all(axis=1)
    for name, mask, slot in (("body", ~membrane_tri, "body"), ("membrane", membrane_tri, "membrane")):
        Ts = T[mask]
        used = np.unique(Ts)
        remap = np.full(len(P), -1, dtype=np.int64)
        remap[used] = np.arange(len(used))
        before = mesh.triangle_count
        ck.finish(mesh, P[used], remap[Ts], slot, col[used], skin, wet=wet[used], emission=glow[used],
                  cavity=cav[used], N=N[used])
        count(name, mesh, before)


# ---- the net of light ---------------------------------------------------------------------------
def _net_warp(p: np.ndarray, q: np.ndarray, s: float) -> tuple[np.ndarray, np.ndarray]:
    """Hand-knotted: the lattice warped smoothly (crossings stay crossings), pinned at the net's edges."""
    pts = np.column_stack([p * 6.0 + (5.0 if s > 0 else 0.0), q * 4.0, np.full(len(p), 0.5)])
    dp = NET_WARP * np.sin(math.pi * np.clip(p, 0, 1)) * ck.value_noise(pts, SEED + 41)
    dq = NET_WARP * np.sin(math.pi * np.clip(q, 0, 1)) * ck.value_noise(pts, SEED + 43)
    return p + dp, q + dq


def _net_xz(p: np.ndarray, q: np.ndarray, s: float) -> tuple[np.ndarray, np.ndarray]:
    """Net coordinates (p along the span 0..1, q across the chord 0 trailing .. 1 leading) to the planform (x, z)."""
    u = NET_U0 + p * (NET_U1 - NET_U0)
    te = trailing(u) + NET_INSET
    le = leading(u) - NET_INSET
    return s * SPAN * u, te + q * (le - te)


def _resample(p: np.ndarray, q: np.ndarray, s: float, step: float):
    x, z = _net_xz(p, q, s)
    d = np.r_[0.0, np.cumsum(np.hypot(np.diff(x), np.diff(z)))]
    n = max(int(math.ceil(d[-1] / step)), 1) + 1
    t = np.linspace(0.0, d[-1], n)
    return np.interp(t, d, p), np.interp(t, d, q)


def net_lines(s: float, step: float) -> tuple[list[tuple[np.ndarray, np.ndarray, float, float]], np.ndarray]:
    """The net's cords on one wing as (p, q, width, glow) polylines, continuous from edge to edge, and its knots (p, q).
    Two families of diagonals (q n -/+ p m = integer) make the diamond mesh; the head-rope runs round three edges."""
    lines = []
    dense = np.linspace(0.0, 1.0, 400)
    for fam in (1.0, -1.0):
        for a in range(-NET_NP - 1, NET_NQ + NET_NP + 2):
            q = (a + fam * NET_NP * dense) / NET_NQ
            ok = (q > 1e-6) & (q < 1.0 - 1e-6)
            if ok.sum() < 2:
                continue
            p0, q0 = _net_warp(dense[ok], q[ok], s)
            lines.append((*_resample(p0, q0, s, step), NET_W, NET_GLOW))
    for p, q in ((dense, np.zeros_like(dense)), (dense, np.ones_like(dense)), (np.zeros_like(dense), dense)):
        lines.append((*_resample(p, q, s, step), ROPE_W, ROPE_GLOW))
    knots = []
    for a in range(-NET_NP - 1, NET_NQ + 1):
        for b in range(0, NET_NQ + NET_NP + 1):
            p = (b - a) / (2.0 * NET_NP)
            q = (a + b) / (2.0 * NET_NQ)
            if 1e-6 < p < 1.0 - 1e-6 and 1e-6 < q < 1.0 - 1e-6:
                knots.append((p, q))
    kp, kq = _net_warp(np.array([k[0] for k in knots]), np.array([k[1] for k in knots]), s)
    return lines, np.column_stack([kp, kq])


def net(mesh: ck.Mesh, rig: ck.Rig) -> None:
    skin = wing_skin(rig)
    for top in (True, False):
        Ps, Ns, Ts, G, C = [], [], [], [], []
        base = 0
        for s in (1.0, -1.0):
            lines, knots = net_lines(s, NET_STEP_TOP if top else NET_STEP_BOT)
            for p, q, w, g in lines:
                x, z = _net_xz(p, q, s)
                n = surface_normal(x, z, top)
                pt = np.column_stack([x, surface_y(x, z, top), z]) + n * NET_OFF
                tan = np.gradient(pt, axis=0)
                sd = np.cross(n, tan)
                sd /= np.linalg.norm(sd, axis=1, keepdims=True)
                m = len(pt)
                # Polish 2: the cords thin with the chord toward the tip, where the diamonds close up, so the outer
                # wing shows its dark membrane between them instead of a solid pale sheet at the battle camera's angle
                u = np.abs(x) / SPAN
                ww = w * np.clip((leading(u) - trailing(u) - 2.0 * NET_INSET) / NET_CHORD_FULL, NET_W_MIN, 1.0)
                Ps.append(np.vstack([pt - sd * (ww * 0.5)[:, None], pt + sd * (ww * 0.5)[:, None]]))
                Ns.append(np.vstack([n, n]))
                G.append(np.full(2 * m, g))
                C.append(np.tile(ck.mix(PAL["salt_glass"], PAL["lagoon_teal"], 0.45), (2 * m, 1)))
                for k in range(m - 1):
                    Ts += [(base + k, base + m + k, base + k + 1), (base + k + 1, base + m + k, base + m + k + 1)]
                base += 2 * m
            if not top:
                continue
            for kp, kq in knots:
                x, z = _net_xz(np.array([kp]), np.array([kq]), s)
                n = surface_normal(x, z, True)[0]
                c = np.array([x[0], float(surface_y(x, z, True)[0]), z[0]]) + n * NET_OFF
                e1 = np.cross(n, (0.0, 0.0, 1.0))
                e1 /= np.linalg.norm(e1)
                e2 = np.cross(n, e1)
                V = [c + e1 * KNOT_R, c + e2 * KNOT_R, c - e1 * KNOT_R, c - e2 * KNOT_R, c + n * KNOT_H]
                Ps.append(np.array(V))
                Ns.append(np.array([n * 0.4 + e1, n * 0.4 + e2, n * 0.4 - e1, n * 0.4 - e2, n]))
                G.append(np.full(5, KNOT_GLOW))
                C.append(np.tile(PAL["salt_glass"], (5, 1)))
                for k in range(4):
                    Ts.append((base + k, base + (k + 1) % 4, base + 4))
                base += 5
        P = np.vstack(Ps)
        N = np.vstack(Ns)
        N /= np.linalg.norm(N, axis=1, keepdims=True)
        T = orient_out(P, np.asarray(Ts, dtype=np.int64), N)
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "net", np.vstack(C), skin, wet=0.3, emission=np.concatenate(G), N=N)
        count("net", mesh, before)


# ---- head ---------------------------------------------------------------------------------------
def _strip(mesh: ck.Mesh, pts: np.ndarray, w, top: bool, colour, bone, emission: float, slot: str = "body"):
    """A narrow strip laid on the shell (a gill slit, the mouth): pts (K, 2) of (x, z)."""
    x, z = pts[:, 0], pts[:, 1]
    n = surface_normal(x, z, top)
    p = np.column_stack([x, surface_y(x, z, top), z]) + n * 0.004
    tan = np.gradient(p, axis=0)
    sd = np.cross(n, tan)
    sd /= np.linalg.norm(sd, axis=1, keepdims=True)
    w = np.broadcast_to(np.asarray(w, dtype=np.float64), (len(p),))
    m = len(p)
    P = np.vstack([p - sd * w[:, None] * 0.5, p + sd * w[:, None] * 0.5])
    T = [(k, m + k, k + 1) for k in range(m - 1)] + [(k + 1, m + k, m + k + 1) for k in range(m - 1)]
    N = np.vstack([n, n])
    T = orient_out(P, np.asarray(T, dtype=np.int64), N)
    ck.finish(mesh, P, T, slot, colour, bone, wet=0.9, cavity=1.0, emission=emission, N=N)


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    body = rig.rigid("body")
    dark = ck.mix(PAL["deep_teal_shadow"], PAL["lacquer_black"], 0.45)
    before = mesh.triangle_count
    for s in (1.0, -1.0):
        x = 0.36
        z = NOSE_Z - 0.2
        y = float(mid(np.array(x))) + 0.06
        Pe, Te = ck.ellipsoid((s * x, y, z), (0.05, 0.045, 0.06), 6, 10)
        ck.finish(mesh, Pe, Te, "eye", PAL["deep_teal_shadow"], body, wet=1.0, emission=0.55)
    count("eyes", mesh, before)

    before = mesh.triangle_count
    for s in (1.0, -1.0):  # five gill slits a side on the belly, behind the mouth, each with its light inside
        for k in range(5):
            z0 = NOSE_Z - 0.55 - 0.13 * k
            xa, xb = 0.1 + 0.008 * k, 0.27 + 0.01 * k
            tt = np.linspace(0.0, 1.0, 6)
            pts = np.column_stack([s * (xa + (xb - xa) * tt), z0 + 0.05 * np.sin(math.pi * tt) - 0.03 * tt])
            _strip(mesh, pts, 0.022 * np.sin(math.pi * (0.15 + 0.7 * tt)), False, dark, body, 0.3)
    xs = np.linspace(-0.3, 0.3, 11)  # the mouth: a wide slit across the head's front edge, underneath
    zs = leading(np.abs(xs) / SPAN) - 0.06
    _strip(mesh, np.column_stack([xs, zs]), 0.035 * np.sin(math.pi * (0.08 + 0.84 * np.linspace(0, 1, 11))) ** 0.5,
           False, dark, body, 0.22)
    count("gills", mesh, before)

    before = mesh.triangle_count
    for s in (1.0, -1.0):  # the cephalic lobes: paddles from the head's front corners, rolled forward into scrolls
        x0 = 0.3
        le = float(leading(np.array(x0 / SPAN)))
        m = float(mid(np.array(x0)))
        cz, cy = le + 0.1, m - 0.1  # the scroll's centre: forward of the head, below the mid-plane
        stem = ck.bezier([(s * x0, m - 0.02, le - 0.16), (s * (x0 + 0.02), m + 0.0, le - 0.02),
                          (s * (x0 + 0.02), m + 0.02, cz - 0.04)], 6)[:-1]
        phi = np.linspace(0.0, 1.45 * math.pi, 13)
        r = 0.12 * (1.0 - 0.55 * phi / (1.45 * math.pi))
        scroll = np.column_stack([s * (x0 + 0.02 - 0.05 * phi / (1.45 * math.pi)), cy + r * np.cos(phi),
                                  cz + r * np.sin(phi)])
        path = np.vstack([stem, scroll])
        t = np.linspace(0.0, 1.0, len(path))
        width = 0.26 * (1.0 - 0.5 * t) * np.sin(math.pi * np.clip(0.2 + t, 0, 1)) ** 0.2 + 0.03
        P, T, ring, sv = blade(path, width, 0.04 * (1.0 - 0.5 * t) + 0.01, math.pi * (0.5 + 1.1 * t ** 1.5),
                               up_hint=(s, 0.0, 0.0), across=6)
        k = t[ring]
        col = ck.mix(PAL["deep_teal_shadow"], PAL["sea_glow"], (0.2 + 0.4 * k)[:, None])
        col = ck.mix(col, PAL["salt_glass"], (0.45 * ck.smoothstep(0.6, 1.0, np.abs(sv)) * k)[:, None])  # pale rims
        ck.finish(mesh, P, T, "body", col, body, wet=0.6, emission=0.06 + 0.2 * ck.smoothstep(0.6, 1.0, np.abs(sv)),
                  cavity=0.3 * (1.0 - np.abs(sv)))
    count("lobes", mesh, before)


def crest(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A grey heron's nuchal plumes made into light: long lanceolate vanes on a bright shaft, fringed at the edges."""
    c = crown()
    plumes = [  # (x splay, rise, length back, droop at the tip, vane width)
        (0.0, 0.62, 1.5, 0.3, 0.085), (0.1, 0.5, 1.32, 0.34, 0.07), (-0.1, 0.5, 1.32, 0.34, 0.07),
        (0.07, 0.2, 0.52, 0.1, 0.045), (-0.07, 0.2, 0.52, 0.1, 0.045),
    ]
    pts = [c, c + (0, 0.45, -0.5), c + (0, 0.35, -1.4)]
    bones = rig.chain(["crest_0", "crest_1"], pts)
    for sx, rise, back, droop, wd in plumes:
        n = 22 if back > 1.0 else 12
        path = ck.bezier([c + (sx * 0.2, 0.0, 0.0), c + (sx * 0.5, rise * 0.8, -back * 0.12),
                          c + (sx * 1.3, rise * 1.05, -back * 0.5), c + (sx * 2.2, rise - droop, -back)], n)
        t = np.linspace(0.0, 1.0, n)
        width = wd * np.sin(math.pi * np.clip(t, 0, 1) ** 0.75) ** 0.9 + 0.008
        width *= 1.0 - 0.22 * (np.arange(n) % 2) * ck.smoothstep(0.2, 0.4, t)  # fringed: barbs parting
        P, T, ring, sv = blade(path, width, 0.012 * (1.0 - t) + 0.004, 0.55, up_hint=(1.0, 0.0, 0.0), across=4)
        k = t[ring]
        shaft = 1.0 - np.abs(sv)
        col = ck.mix(PAL["deep_teal_shadow"], PAL["salt_glass"], ck.smoothstep(0.0, 0.4, k)[:, None])
        col = ck.mix(col, PAL["foam_white"], (0.35 * shaft * ck.smoothstep(0.3, 0.9, k))[:, None])
        glow = (0.2 + 0.25 * ck.smoothstep(0.55, 1.0, k)) * (0.55 + 0.45 * shaft)
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "crest", col, bones, wet=0.3, emission=glow)
        count("crest", mesh, before)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = tail_path(40)
    t = np.linspace(0.0, 1.0, len(path))
    P, T = ck.tube(path, TAIL_R0 * (1.0 - t) ** 1.3 + TAIL_R1, 7, cap_start=True, cap_end=True, squash=0.8,
                   up_hint=(0.0, 1.0, 0.0))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    d = np.linalg.norm(P[:, None, :] - path[None], axis=2).argmin(axis=1)
    k = t[d]
    under = ck.smoothstep(0.0, -0.8, N[:, 1])
    col = ck.mix(PAL["deep_teal_shadow"], PAL["sea_glow"], (0.15 + 0.45 * k)[:, None])
    col = ck.mix(col, PAL["salt_glass"], (0.5 * under)[:, None])
    bands = ck.smoothstep(0.45, 0.8, np.sin(2.0 * math.pi * 7.0 * k) * 0.5 + 0.5) * ck.smoothstep(0.4, 0.75, k)
    col = ck.mix(col, PAL["salt_glass"], (0.45 * bands)[:, None])  # the whip's pale rings
    chain = rig.chain([f"tail_{i}" for i in range(5)], tail_points())
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", col, chain, wet=0.6, emission=0.06 + 0.22 * k ** 2 + 0.1 * bands, N=N)
    fpath = tail_path(51)[2:9]  # the small dorsal fin at the tail's root
    ft = np.linspace(0.0, 1.0, len(fpath))
    fw = 0.13 * np.sin(math.pi * ft ** 0.7) ** 1.2 + 0.006
    Pf, Tf, ring, sv = blade(fpath, fw, 0.014, 0.05, up_hint=(1.0, 0.0, 0.0), across=4, lift=fw * 0.5 + 0.03)
    colf = ck.mix(PAL["deep_teal_shadow"], PAL["salt_glass"], (0.5 * ck.smoothstep(0.3, 1.0, sv))[:, None])
    ck.finish(mesh, Pf, Tf, "body", colf, rig.rigid("tail_0"), wet=0.6, emission=0.08 + 0.15 * ck.smoothstep(0.5, 1, sv))
    count("tail", mesh, before)


def keepsake(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The child's glass net-float on its cord at the tail tip."""
    tip = tail_points()[-1]
    fb = rig.rigid("float")
    c = float_centre()
    before = mesh.triangle_count
    Pk, Tk = ck.ellipsoid(tip + (0.0, -0.006, 0.0), (0.02, 0.028, 0.034), 4, 8)  # the cord's wrap on the tail
    ck.finish(mesh, Pk, Tk, "cord", PAL["sand_cloth"], rig.rigid("tail_4"), wet=0.5, cavity=0.3)
    path = np.array([tip + (0.0, -0.012 - CORD * f, 0.004 * math.sin(f * 6.0)) for f in np.linspace(0.0, 1.0, 7)])
    P, T = ck.tube(path, 0.006, 5, cap_start=False, cap_end=True, up_hint=(0.0, 0.0, 1.0))
    ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], fb, wet=0.5)
    Pc, Tc = ck.ellipsoid(c + (0.0, FLOAT_R * 0.96, 0.0), (0.026, 0.016, 0.026), 4, 8)  # the knot over the seal
    ck.finish(mesh, Pc, Tc, "cord", PAL["sand_wet"], fb, wet=0.6, cavity=0.4)
    count("cord", mesh, before)
    before = mesh.triangle_count
    Pg, Tg = ck.ellipsoid(c, (FLOAT_R, FLOAT_R * 0.97, FLOAT_R), 12, 18)
    d = (Pg - c) / FLOAT_R
    col = ck.mix(PAL["salt_glass"], PAL["lagoon_teal"], (0.4 * ck.smoothstep(0.2, -0.9, d[:, 1]))[:, None])  # thick glass
    glint = np.exp(-((d[:, 0] + 0.35) ** 2 + (d[:, 1] - 0.62) ** 2 + (d[:, 2] - 0.55) ** 2) / 0.04)
    col = ck.mix(col, PAL["gauze_white"], np.clip(glint, 0.0, 1.0)[:, None])  # the glint: light caught in old glass
    ck.finish(mesh, Pg, Tg, "glass", col, fb, wet=1.0)
    Ps, Ts = ck.ellipsoid(c + (0.0, FLOAT_R * 0.93, 0.0), (0.03, 0.025, 0.03), 4, 8)  # the glass seal (the pontil)
    ck.finish(mesh, Ps, Ts, "glass", PAL["salt_glass"], fb, wet=1.0)
    count("glass", mesh, before)
    before = mesh.triangle_count
    r = FLOAT_R + 0.005
    th = np.linspace(0.12, math.pi - 0.05, 12)
    for k in range(6):  # meridians from the knot to the bottom
        ph = k * math.pi / 3.0 + 0.2
        path = c + np.column_stack([r * np.sin(th) * math.cos(ph), r * np.cos(th), r * np.sin(th) * math.sin(ph)])
        P, T = ck.tube(path, NET_CORD_R, 4, cap_start=False, cap_end=False, up_hint=(0.0, 0.0, 1.0))
        ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], fb, wet=0.5)
    for lat in (-0.15, 0.7):  # a ring under the equator and one above it
        ph = np.linspace(0.0, 2.0 * math.pi, 25)
        rr = r * math.cos(lat)
        path = c + np.column_stack([rr * np.cos(ph), np.full(len(ph), r * math.sin(lat)), rr * np.sin(ph)])
        P, T = ck.tube(path, NET_CORD_R, 4, cap_start=False, cap_end=False, up_hint=(0.0, 1.0, 0.0))
        ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], fb, wet=0.5)
    count("cord", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("ilun")
    shell(mesh, rig)
    net(mesh, rig)
    head(mesh, rig)
    crest(mesh, rig)
    tail(mesh, rig)
    keepsake(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 4.0
READY_SEC = 1.4
ATTACK_SEC = 1.2
ATTACK_CONTACT = 0.55
CAST_SEC = 1.6
CAST_CONTACT = 0.8
HIT_SEC = 0.5
HIT_PEAK = 0.12
DEFEND_SEC = 1.2
KO_SEC = 1.8
VICTORY_SEC = 2.2
RISE_SEC = 2.6
DISMISS_SEC = 1.0
SPECIAL_SEC = 2.4
SPECIAL_CONTACT = 1.45
RELEASE_SEC = 3.3  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_AWAY = (0.0, 1.5, -0.45)  # where the release carries him (metres: up, and back away from the party)
FLOAT_LAG = 0.15  # the float swings this far behind the tail's motion
FLOAT_HANG = 0.85  # and counter-turns this much of it (it hangs, not quite plumb)
HANG_BONES = ("root", "body", "tail_0", "tail_1", "tail_2", "tail_3", "tail_4")
TIP_GAIN = 1.15  # wing_3 (the tip) carries this much of wing_2's flap
IDLE_FLAP = (5.0, 8.0, 10.0, 12.0)  # the idle's flap per wing segment (degrees), root to tip
IDLE_TWIST = (1.5, 3.5, 5.0, 6.5)  # and its twist (the trailing edge's ripple)
IDLE_LAG = 0.85  # radians each segment lags the one inside it: the wave travels out to the tip


def wings(c: ck.Clip, t: float, left, right=None, sweep=(0.0, 0.0)) -> None:
    """Each side's three flap angles (degrees up, about the body's length; the tip follows the third), and a forward
    sweep of wing_0 (+ forward)."""
    right = left if right is None else right
    for k in range(4):
        lv = left[min(k, 2)] * (TIP_GAIN if k == 3 else 1.0)
        rv = right[min(k, 2)] * (TIP_GAIN if k == 3 else 1.0)
        c.key(f"wing_l{k}", t, (0, -sweep[0] if k == 0 else 0.0, lv))
        c.key(f"wing_r{k}", t, (0, sweep[1] if k == 0 else 0.0, -rv))


def crest_keys(c: ck.Clip, t: float, lift: float) -> None:
    """+ lifts the plumes (about x, the tips going up), - lays them flat."""
    c.key("crest_0", t, (lift, 0, 0))
    c.key("crest_1", t, (lift * 0.6, 0, 0))


def tail_keys(c: ck.Clip, t: float, ry: float = 0.0, rx: float = 0.0) -> None:
    """ry swings the tail sideways; + rx lifts its end."""
    for k in range(5):
        c.key(f"tail_{k}", t, (rx * (0.6 + 0.15 * k), ry * (0.5 + 0.25 * k), 0))


def hang_float(c: ck.Clip) -> ck.Clip:
    """Keys the float so it hangs: it counter-turns the pitch and roll its parents give it, FLOAT_LAG behind."""
    frames = max(int(round(c.length * ck.FPS)), 1)
    for f in range(frames + 1):
        t = min(f / ck.FPS, c.length)
        s = t - FLOAT_LAG
        s = s % c.length if c.loop else max(s, 0.0)
        rx = sum(float(c.sample(b, s)[0][0]) for b in HANG_BONES)
        rz = sum(float(c.sample(b, s)[0][2]) for b in HANG_BONES)
        c.key("float", t, (-FLOAT_HANG * rx, 0, -FLOAT_HANG * rz))
    return c


def build_idle() -> ck.Clip:
    """A slow undulation travelling out along each wing to the tip (each segment's flap a beat behind the one inside
    it), with a twist wave a quarter beat behind the flap, so the soft trailing edge ripples after the leading edge;
    the disc bobbing, the tail's S swaying, the crest stirring. He hovers in place."""
    c = ck.Clip("idle", IDLE_SEC, loop=True)
    for k, amp in enumerate(IDLE_FLAP):
        c.wave(f"wing_l{k}", amp_rot=(0, 0, amp), cycles=1, phase=-IDLE_LAG * k, steps=16)
        c.wave(f"wing_r{k}", amp_rot=(0, 0, -amp), cycles=1, phase=-IDLE_LAG * k, steps=16)
    c = _with_twist(c, IDLE_TWIST)
    c.wave("body", amp_rot=(1.5, 0, 0), amp_loc=(0, 0.045, 0), cycles=1, phase=math.pi)
    for k in range(5):
        c.wave(f"tail_{k}", amp_rot=(2.0, 3.5 + 1.5 * k, 0), cycles=1, phase=-0.8 * k - 0.6)
    c.wave("crest_0", amp_rot=(3.0, 0, 0), cycles=1, phase=-1.4)
    c.wave("crest_1", amp_rot=(4.5, 0, 0), cycles=1, phase=-2.0)
    return c


def _with_twist(c: ck.Clip, amps) -> ck.Clip:
    """Re-keys the wing bones so their flap carries a twist (x) a quarter beat behind it: the travelling ripple."""
    out = ck.Clip(c.name, c.length, loop=c.loop)
    for b, ks in c.keys.items():
        if not b.startswith("wing_"):
            for t, r, l in ks:
                out.key(b, t, r, l)
            continue
        k = int(b[-1])
        for t, r, l in ks:
            ph = 2.0 * math.pi * t / c.length - IDLE_LAG * k - 0.5 * math.pi
            out.key(b, t, (amps[k] * math.sin(ph), r[1], r[2]), l)
    return out


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # he gathers: wings high, a slow down-stroke, back to rest
    for t, ly, rx, w, cr in ((0.0, 0.0, 0.0, (0, 0, 0), 0.0), (0.5, 0.08, -4.0, (20.0, 12.0, 8.0), 14.0),
                             (1.0, 0.02, 2.0, (-7.0, -5.0, -3.0), 8.0), (READY_SEC, 0.0, 0.0, (0, 0, 0), 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w)
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.5)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # the brine lash: he banks, lifts his left wing and sweeps it forward and down
    for t, rx, ry, rz, ly, wl, wr, sw, cr in (
            (0.0, 0, 0, 0, 0, (0, 0, 0), (0, 0, 0), 0.0, 0.0),
            (0.32, -6.0, -6.0, 11.0, 0.17, (26.0, 16.0, 10.0), (-4.0, -4.0, -2.0), -8.0, 12.0),
            (0.42, -5.0, -5.0, 10.0, 0.17, (28.0, 18.0, 12.0), (-4.0, -4.0, -3.0), -10.0, 12.0),
            (ATTACK_CONTACT, 6.0, 12.0, -5.0, 0.08, (-6.0, -5.0, -3.0), (6.0, 4.0, 2.0), 22.0, -4.0),
            (0.78, 3.0, 6.0, -3.0, 0.04, (-3.0, -3.0, -2.0), (3.0, 2.0, 1.0), 10.0, 0.0),
            (ATTACK_SEC, 0, 0, 0, 0, (0, 0, 0), (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, ry, rz), (0, ly, 0))
        wings(c, t, wl, wr, sweep=(sw, 0.0))
        crest_keys(c, t, cr)
        tail_keys(c, t, ry=-ry * 0.8, rx=rx * 0.4)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the tidal ward: the wings spread and curl forward round his front, a shield
    for t, rx, ly, w, sw, cr in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0),
                                 (0.4, -8.0, 0.12, (18.0, 8.0, 4.0), 6.0, 16.0),
                                 (CAST_CONTACT, -10.0, 0.15, (10.0, -12.0, -18.0), 24.0, 18.0),
                                 (1.15, -9.0, 0.14, (9.0, -12.0, -18.0), 22.0, 16.0),
                                 (CAST_SEC, 0, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """Pushed back and pitched nose up, wings flinching up, crest snapped back, rolled a little to `side`.
    The kit's mirrored hit_b would flip the wings' flinch down, so hit_b is authored: the roll to the other side,
    heavier (the kit's HIT_B amp)."""
    c = ck.Clip(name, HIT_SEC)
    near, far = (12.0, 10.0, 8.0), (15.0, 12.0, 9.0)
    for t, s in ((0.0, 0.0), (HIT_PEAK, amp), (0.3, -0.25 * amp), (HIT_SEC, 0.0)):
        c.key("body", t, (-11.0 * s, 0, 4.0 * s * side), (0, 0.04 * s, -0.08 * s))
        lw, rw = (near, far) if side > 0 else (far, near)
        wings(c, t, tuple(v * s for v in lw), tuple(v * s for v in rw))
        crest_keys(c, t, -10.0 * s)
        tail_keys(c, t, ry=4.0 * s * side, rx=6.0 * s)
    return c


def build_defend() -> ck.Clip:
    c = ck.Clip("defend", DEFEND_SEC)  # the wings fold forward over his front and hold, then open
    for t, rx, ly, w, sw, cr in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0),
                                 (0.3, -4.0, -0.04, (6.0, -15.0, -20.0), 26.0, -6.0),
                                 (0.85, -4.0, -0.04, (6.0, -15.0, -20.0), 26.0, -6.0),
                                 (DEFEND_SEC, 0, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # the fall: a flinch, then he tips back, folds his wings up and back, and settles
    for t, rx, ly, w, sw, cr, tl in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0, 0.0),
                                     (0.2, -8.0, 0.03, (10.0, 8.0, 6.0), 0.0, -8.0, 4.0),
                                     (1.0, -20.0, -0.04, (30.0, 26.0, 18.0), -14.0, -14.0, 18.0),
                                     (1.45, -24.0, -0.08, (36.0, 30.0, 22.0), -18.0, -16.0, 24.0),
                                     (KO_SEC, -24.0, -0.08, (36.0, 30.0, 22.0), -18.0, -16.0, 24.0)):
        c.key("root", t, (0, 0, 0), (0, ly, 0))
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=tl)
    return c


def build_victory() -> ck.Clip:
    c = ck.Clip("victory", VICTORY_SEC)  # he rises with the wings high and the crest up, one slow full stroke
    for t, rx, ly, w, cr in ((0.0, 0, 0, (0, 0, 0), 0.0), (0.8, -6.0, 0.25, (24.0, 14.0, 10.0), 18.0),
                             (1.45, 2.0, 0.2, (-10.0, -8.0, -5.0), 14.0), (VICTORY_SEC, 0, 0, (0, 0, 0), 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w)
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


FOLDED = (68.0, 40.0, 22.0)  # the wings closed up over his back like a shell (rise's start, dismiss's end)


def build_rise() -> ck.Clip:
    c = ck.Clip("rise", RISE_SEC)  # the unfurling, in place (the stage lifts him out of the water)
    for t, rx, w, sw, cr in ((0.0, -14.0, FOLDED, -10.0, -14.0), (0.5, -12.0, FOLDED, -10.0, -14.0),
                             (1.4, -4.0, (22.0, 12.0, 8.0), 0.0, 14.0), (2.0, 2.0, (-7.0, -5.0, -3.0), 0.0, 8.0),
                             (RISE_SEC, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 1.2)
    return c


def build_dismiss() -> ck.Clip:
    c = ck.Clip("dismiss", DISMISS_SEC)  # the folding: wings close over his back, crest down, nose dips; ends folded
    for t, rx, w, sw, cr in ((0.0, 0, (0, 0, 0), 0.0, 0.0), (0.35, -4.0, (14.0, 8.0, 6.0), 0.0, 6.0),
                             (0.8, 10.0, FOLDED, -10.0, -14.0), (DISMISS_SEC, 12.0, FOLDED, -10.0, -14.0)):
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.3)
    return c


def build_special() -> ck.Clip:
    c = ck.Clip("special", SPECIAL_SEC)  # Floodnet: wings flung wide and high, a held breath, the great sweep down
    for t, rx, ly, w, sw, cr in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0),
                                 (0.9, -8.0, 0.3, (34.0, 18.0, 12.0), -6.0, 20.0),
                                 (1.15, -9.0, 0.32, (36.0, 20.0, 13.0), -6.0, 20.0),
                                 (SPECIAL_CONTACT, 6.0, 0.05, (-15.0, -9.0, -4.0), 8.0, 4.0),
                                 (1.8, 5.0, 0.05, (-13.0, -8.0, -4.0), 6.0, 4.0),
                                 (SPECIAL_SEC, 0, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: the first release, gentle). He opens one last
    time, wings wide and the crest raised, hovers there a breath, then one slow stroke carries him up and back,
    away from the party, level and unhurried: at peace, not fallen."""
    c = ck.Clip("release", RELEASE_SEC)
    lx, ly, lz = RELEASE_AWAY
    for t, up, back, rx, w, cr, tl in ((0.0, 0.0, 0.0, 0.0, (0, 0, 0), 0.0, 0.0),
                                       (0.7, 0.08, 0.0, -5.0, (20.0, 12.0, 8.0), 14.0, -2.0),
                                       (1.3, 0.2, 0.0, -7.0, (14.0, 9.0, 6.0), 24.0, -4.0),
                                       (1.85, 0.24, 0.02, -7.0, (15.0, 10.0, 7.0), 24.0, -4.0),
                                       (2.5, 0.75, 0.4, -9.0, (-6.0, -4.0, -2.0), 16.0, -6.0),
                                       (RELEASE_SEC, 1.0, 1.0, -6.0, (12.0, 7.0, 4.0), 16.0, -5.0)):
        c.key("root", t, (0, 0, 0), (lx * back, ly * up, lz * back))
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w)
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=tl)
    return c


def build_clips() -> list[ck.Clip]:
    clips = [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(),
             build_hit("hit_b", -1.0, ck.HIT_B["amp"]), build_defend(), build_ko(),
             build_victory(), build_rise(), build_dismiss(), build_special(), build_release()]
    return [hang_float(c) for c in clips]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    rest = mesh.arrays()["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print("parts: " + ", ".join(f"{k} {v}" for k, v in PARTS.items()))
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    poser = grounding.Poser(rig, mesh)
    for c in ck.with_variety(clips):
        lows = grounding.lowest(poser, c)
        highs, disp = [], []
        for t in grounding.frame_times(c):
            P = poser.vertices(poser.matrices(grounding.pose_at(c, poser.names, t)))
            highs.append(float(P[:, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        print(f"{c.name:8s} {c.length:.2f}s: y {min(lows):+.3f}..{max(highs):.3f}; peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    rig = build_rig()
    return rig, build_mesh(rig), build_clips()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig, mesh, clips = build()
    if args.report or not args.out:
        report(rig, mesh, clips)
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "ilun"})
    print(f"ilun: {info}")


if __name__ == "__main__":
    main()
