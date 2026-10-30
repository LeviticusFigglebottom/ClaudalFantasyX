"""Raid-hound, the Ch6 boss pair's hound (M3-CRE-05): docs/kb/art/creatures/act1/raid_hound.md and m2-slice's act1_ch06 §9
(mud-coloured, a greyhound's legs under a mastiff's chest, a red-lacquered muzzle cage).

blender --background --factory-startup --python assets_src/creatures/raid_hound/build_raid_hound.py -- \
    --out assets/creatures/raid_hound/raid_hound.glb

The Order raid's coursing dog: lean, long-legged, deep-chested, mud-coloured with pale underparts, in a branded leather
harness with the Order's mark. Not a monster, which is the fight's point: its weak point is only an old scar, one small
closed mark (ADR 0151, M3-CRE-650), and its KO is lying down, beaten, not dead.

**Final quality (M3-CRE-655, ADR 0041).** The first build read crude (cylinders on stick legs, a long horse-like head
in a cage of red hoops), so every part is re-modelled on the same rig, clips and contact times:
- the torso is lofted from superellipse sections (a keel under a deep chest, a tucked waist, an arched loin, a sloping
  croup), with the ribs and the flank's creases in its cavity;
- the legs are a greyhound's, sectioned across: the shoulder and upper arm, the elbow's point, a fine forearm, the
  wrist's knob and a sloped pastern in front; behind, a heavy thigh, the stifle, the gaskin, the hock's point and a
  short upright rear pastern; each on a compact hare foot with toes and dark nails, skinned along the leg's chain;
- the head is a wedge (a broad skull at the cheeks, almost no stop, a long tapering muzzle to a black nose) over a
  separate lower jaw on the jaw bone, with dark lips, a mouth and canines that show when it bites, and folded rose
  ears;
- the Order's harness is a Y-harness of `tortoiseshell` leather laid on the body (a neck ring, a strap down the breast
  between the forelegs, a girth behind the elbows, a back strap) with brass rings and the Order's mark, the Level, on a
  lacquered plate at the withers; the muzzle cage is a basket of red-lacquered bars on a leather headstall, its lower
  half riding the jaw;
- the coat is `sand_wet` into `tortoiseshell` with a darker saddle, a faint brindle, pale underparts, a dark mask, and
  wet mud on the legs and belly from the flats (vertex colour, cavity and wetness).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 6203
PAL = {k: ck.hexrgb(v) for k, v in {
    "overcast_slate": "#6F7E8E", "storm_slate": "#3E4A57", "bone": "#E6DAC0", "tortoiseshell": "#6B3A1E",
    "order_marble": "#E4DED3", "lacquer_black": "#1D1916", "brass": "#B08D57", "sand_wet": "#B59D74",
    "lacquer_red": "#B3261E", "spawn_wound": "#3FE0C8",
}.items()}
FLOOR_COL = PAL["lacquer_black"]  # palette.json's albedo floor and ceiling
CEIL_COL = ck.hexrgb("#EBE7DF")
PALE = ck.mix(PAL["sand_wet"], PAL["bone"], 0.45)  # the underparts
MUD = ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.35)  # the flats' mud on the legs
LEATHER = PAL["tortoiseshell"]
MOUTH = ck.mix(PAL["lacquer_black"], PAL["lacquer_red"], 0.3)

HIP = np.array([0.0, 0.72, -0.42])
SHOULDER = np.array([0.0, 0.78, 0.28])
KO_FORE = -20.0  # the KO's forearm turn (degrees): with the upper leg's -70, flat along the floor
PAW_Y = 0.036  # the paw bone's tail height (the rig; unchanged since M3-CRE-632)
LEGS = {  # name: (attach, x side, front?)
    "fl": (SHOULDER + np.array([0.11, -0.12, 0.02]), 1.0, True), "fr": (SHOULDER + np.array([-0.11, -0.12, 0.02]), -1.0, True),
    "bl": (HIP + np.array([0.12, -0.08, 0.0]), 1.0, False), "br": (HIP + np.array([-0.12, -0.08, 0.0]), -1.0, False),
}
# The weak point (ADR 0151, M3-CRE-650): one small closed mark, an old gaff scar healed shut on the breast below the
# throat, toward its near side (its right, -x: the battle camera's side once the stage turns it to the party). There
# the chest faces forward and a little to that side, so the battle camera and the review three-quarter (+x front)
# both see it.
SCAR_AT = SHOULDER + np.array([-0.058, -0.05, 0.17])  # projected onto the chest's surface (M3-CRE-655: on the new
# breast it sits beside the harness's breast strap, under the neck ring, where both views see it)
SCAR_ALONG = np.array([0.35, -1.0, 0.0])  # it slants down across the breast toward the midline
SCAR_HALF = (0.055, 0.012)  # the glowing seam's half length and half width (m)
SCAR_LIP = (1.3, 2.4, 0.006)  # the dark healed lip round it: x the seam's length, x its width, raised (m)
SCAR_BEND_R = 0.22  # the chest's curvature along the scar (m): the mark bends to lie on it

# ---------------------------------------------------------------------------------------------
# Shapes (Godot axes: x left, y up, facing +z; metres; the ground at y 0). Each table is a loft's stations.
# ---------------------------------------------------------------------------------------------
# the torso, across z: (z, top y, bottom y, half-width, the widest point as a fraction from the bottom)
TORSO = ((-0.585, 0.772, 0.672, 0.03, 0.5), (-0.565, 0.79, 0.615, 0.07, 0.5), (-0.53, 0.804, 0.57, 0.095, 0.52),
         (-0.46, 0.822, 0.54, 0.106, 0.55), (-0.38, 0.84, 0.556, 0.098, 0.55), (-0.3, 0.852, 0.588, 0.088, 0.55),
         (-0.22, 0.854, 0.606, 0.084, 0.55), (-0.14, 0.85, 0.585, 0.09, 0.55), (-0.06, 0.848, 0.535, 0.104, 0.58),
         (0.02, 0.85, 0.482, 0.118, 0.6), (0.1, 0.856, 0.446, 0.129, 0.6), (0.18, 0.864, 0.437, 0.132, 0.6),
         (0.25, 0.874, 0.446, 0.128, 0.6), (0.31, 0.87, 0.476, 0.12, 0.6), (0.36, 0.852, 0.51, 0.11, 0.6),
         (0.4, 0.83, 0.55, 0.104, 0.62), (0.43, 0.806, 0.586, 0.096, 0.64), (0.45, 0.782, 0.616, 0.084, 0.64),
         (0.464, 0.758, 0.646, 0.062, 0.64), (0.472, 0.738, 0.668, 0.028, 0.64))
TORSO_RINGS, TORSO_SEGS = 28, 20
TORSO_EXP = (2.5, 1.9, 2.3)  # the section's superellipse exponents: the back, the keel, the sides
RIBS = (-0.08, 0.24, 0.042, 0.0035)  # the rib cage: from z, to z, the rib spacing, the groove depth (m)
# the neck: a curve from inside the chest up to the back of the skull, deeper than wide
NECK_PATH = ((0.0, 0.75, 0.25), (0.0, 0.86, 0.33), (0.0, 0.95, 0.4), (0.0, 1.0, 0.48))
NECK_R = (0.088, 0.058)
NECK_SQUASH = 0.78
# the head (on the head bone) across z: (z, top y, bottom y, half-width); the widest point at 45% up
HEAD = ((0.435, 1.032, 0.978, 0.022), (0.455, 1.058, 0.952, 0.046), (0.49, 1.073, 0.937, 0.058),
        (0.53, 1.077, 0.936, 0.061), (0.57, 1.073, 0.94, 0.056), (0.605, 1.064, 0.944, 0.049),
        (0.64, 1.045, 0.948, 0.04), (0.68, 1.026, 0.951, 0.033), (0.72, 1.008, 0.953, 0.028),
        (0.75, 0.996, 0.955, 0.024), (0.772, 0.988, 0.958, 0.019), (0.786, 0.981, 0.963, 0.011))
# the lower jaw (on the jaw bone): (z, top y, bottom y, half-width)
JAW = ((0.5, 0.958, 0.916, 0.04), (0.55, 0.956, 0.904, 0.047), (0.6, 0.954, 0.914, 0.039),
       (0.65, 0.954, 0.924, 0.031), (0.7, 0.955, 0.933, 0.025), (0.74, 0.957, 0.94, 0.019),
       (0.765, 0.959, 0.946, 0.011))
HEAD_SEGS = 14
MOUTH_Y = 0.955  # the lips' line
EYE_AT = (0.038, 1.038, 0.6)  # x on the left
EYE_R = 0.0115
NOSE_AT = np.array([0.0, 0.976, 0.785])
CANINES = ((0.016, 0.951, 0.742, -1.0), (0.013, 0.958, 0.73, 1.0))  # (x, y, z, up or down): upper and lower
# the rose ear from its base along a fold: (x, y, z) per station on the left, its width and thickness
EAR_PATH = ((0.048, 1.058, 0.506), (0.064, 1.07, 0.488), (0.076, 1.064, 0.468), (0.082, 1.046, 0.452),
            (0.084, 1.026, 0.442))  # drooping back at rest, so the clips' ear keys (+25, +40) lift it level
EAR_W = (0.05, 0.058, 0.054, 0.04, 0.012)
EAR_T = (0.011, 0.008, 0.006, 0.005, 0.003)
EAR_STATIONS = 9
# the legs, sectioned across y: (y, centre z, centre x, half-width, front depth, back depth)
# M3-CRE-660 (primitive pass): the top three sections sit back and in, inside the chest wall, so the shoulder rises
# out of the chest as the upper arm's bulge instead of standing proud of it as a flat plate
FORELEG = ((0.78, 0.27, 0.06, 0.035, 0.045, 0.055), (0.7, 0.29, 0.074, 0.048, 0.055, 0.065),
           (0.62, 0.305, 0.086, 0.05, 0.062, 0.068), (0.54, 0.3, 0.092, 0.047, 0.054, 0.074),
           (0.46, 0.286, 0.093, 0.041, 0.04, 0.07), (0.4, 0.281, 0.093, 0.035, 0.033, 0.056),
           (0.35, 0.285, 0.093, 0.029, 0.029, 0.034), (0.28, 0.29, 0.093, 0.024, 0.026, 0.025),
           (0.2, 0.293, 0.093, 0.02, 0.021, 0.019), (0.14, 0.296, 0.093, 0.018, 0.018, 0.017),
           (0.105, 0.298, 0.093, 0.02, 0.02, 0.021), (0.075, 0.306, 0.093, 0.016, 0.016, 0.015),
           (0.05, 0.318, 0.093, 0.019, 0.02, 0.019))
HINDLEG = ((0.8, -0.46, 0.06, 0.04, 0.06, 0.07), (0.74, -0.45, 0.075, 0.06, 0.09, 0.1),
           (0.66, -0.43, 0.085, 0.068, 0.115, 0.115), (0.58, -0.4, 0.088, 0.066, 0.115, 0.11),
           (0.5, -0.36, 0.088, 0.058, 0.095, 0.1), (0.43, -0.322, 0.088, 0.048, 0.066, 0.085),
           (0.38, -0.297, 0.088, 0.04, 0.043, 0.072), (0.32, -0.312, 0.088, 0.034, 0.03, 0.064),
           (0.26, -0.346, 0.088, 0.027, 0.024, 0.05), (0.2, -0.39, 0.088, 0.022, 0.02, 0.034),
           (0.15, -0.424, 0.088, 0.02, 0.019, 0.027), (0.12, -0.438, 0.088, 0.019, 0.02, 0.03),
           (0.09, -0.43, 0.088, 0.016, 0.017, 0.017), (0.06, -0.416, 0.088, 0.018, 0.02, 0.019),
           (0.045, -0.406, 0.088, 0.02, 0.023, 0.021))
LEG_SEGS = 14
LEG_BLEND_Y = {"f": 0.62, "b": 0.64}  # above this a leg's top blends into the chest or hips (half at its top)
PAW = {"f": 0.33, "b": -0.392}  # the hare foot's centre z: its pad, then four toes ahead of it
PAW_R = (0.026, 0.023, 0.04)
SOLE_Y = 0.0015  # the soles' height: on the floor
TOES = ((0.009, 0.038, 0.016), (0.022, 0.026, 0.014))  # (x, z ahead of the pad, radius) for the middle and side toes
TAIL_PATH = ((0.0, 0.772, -0.56), (0.0, 0.7, -0.69), (0.0, 0.55, -0.77), (0.0, 0.42, -0.8), (0.0, 0.36, -0.775))
TAIL_R = (0.027, 0.005)
# the harness (laid on the body by casting rays from inside it)
STRAP_W, STRAP_T = 0.032, 0.007  # a strap's width and thickness
NECK_RING_U = 0.42  # where on the neck curve the neck ring sits (its front clears the scar)
GIRTH = ((0.0, 0.66, 0.135), (0.0, -0.2, 1.0))  # a point on the girth's plane and its normal (top leaning forward)
PLATE_R = (0.052, 0.038, 0.006)
RING_REACH = 0.07  # the straps' ends this near the neck ring follow the neck with it (most of the way at the ring)  # the Order's plate: half length (along the back), half width, thickness
# the muzzle cage: hoops at these z, standing off the snout by CAGE_GAP; bars along it at these angles (from the top)
CAGE_HOOPS = (0.62, 0.69, 0.75)
CAGE_FRONT = 0.79
CAGE_GAP = 0.011
CAGE_BARS = (0.0, 55.0, 115.0, 180.0, -115.0, -55.0)
CAGE_R = 0.0045


def leg_points(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    a, s, front = LEGS[name]
    if front:
        knee = a + np.array([0.0, -0.32, -0.02])
        ankle = knee + np.array([0.0, -0.3, 0.02])
    else:
        knee = a + np.array([0.0, -0.26, 0.14])  # the hind leg's stifle forward, hock back: a dog's angles
        ankle = knee + np.array([0.0, -0.26, -0.16])
    paw = np.array([ankle[0], PAW_Y, ankle[2] + 0.08])
    return a, knee, ankle, paw


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("hips", HIP, HIP + np.array([0, 0, 0.3]), "root")
    rig.add("chest", HIP + np.array([0, 0, 0.3]), SHOULDER, "hips")
    rig.add("neck", SHOULDER, SHOULDER + np.array([0, 0.2, 0.22]), "chest")
    rig.add("head", SHOULDER + np.array([0, 0.2, 0.22]), SHOULDER + np.array([0, 0.14, 0.52]), "neck")
    rig.add("jaw", SHOULDER + np.array([0, 0.14, 0.28]), SHOULDER + np.array([0, 0.09, 0.5]), "head")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"ear_{tag}", SHOULDER + np.array([s * 0.06, 0.3, 0.22]), SHOULDER + np.array([s * 0.09, 0.4, 0.17]),
                "head")
    rig.add("tail0", HIP + np.array([0, 0.02, -0.06]), HIP + np.array([0, -0.12, -0.3]), "hips")
    rig.add("tail1", HIP + np.array([0, -0.12, -0.3]), HIP + np.array([0, -0.32, -0.42]), "tail0")
    for name in LEGS:
        a, knee, ankle, paw = leg_points(name)
        parent = "chest" if LEGS[name][2] else "hips"
        rig.add(f"{name}_upper", a, knee, parent)
        rig.add(f"{name}_lower", knee, ankle, f"{name}_upper")
        rig.add(f"{name}_paw", ankle, paw, f"{name}_lower")
    return rig


def torso_skin(rig: ck.Rig):
    return rig.chain(["hips", "chest"], [HIP, HIP + np.array([0, 0, 0.3]), SHOULDER])


def neck_skin(rig: ck.Rig):
    return rig.chain(["chest", "neck", "head"], [SHOULDER - np.array([0, 0, 0.3]), SHOULDER,
                                                 SHOULDER + np.array([0, 0.2, 0.22]), SHOULDER + np.array([0, 0.14, 0.52])])


# ---------------------------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------------------------
def sgnpow(v: np.ndarray, p: float) -> np.ndarray:
    return np.sign(v) * np.abs(v) ** p


def smooth_table(table, n: int, passes: int = 3) -> np.ndarray:
    """A station table (rows of numbers, the first column the station) resampled at n even stations and smoothed, so
    a loft through it has no kinks at the stations."""
    t = np.asarray(table, dtype=np.float64)
    fine = np.linspace(t[0, 0], t[-1, 0], 8 * n)
    cols = [fine] + [np.interp(fine, t[:, 0], t[:, k]) for k in range(1, t.shape[1])]
    out = np.column_stack(cols)
    for _ in range(passes):
        out[1:-1, 1:] = (out[:-2, 1:] + 2.0 * out[1:-1, 1:] + out[2:, 1:]) / 4.0
    pick = np.linspace(0, len(fine) - 1, n).round().astype(int)
    return out[pick]


def close_loft(rings: list[np.ndarray], cap_start: bool = True, cap_end: bool = True,
               axis_push: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Rings of equal size (S, 3) lofted into a surface, its ends closed to a point (pushed out along the loft's axis
    by `axis_push`), wound outward (by its signed volume)."""
    K, S = len(rings), len(rings[0])
    P = np.vstack(rings)
    tris = [ck.flip(ck.grid_tris(K, S, True))]
    ends = []
    if cap_start:
        ends.append((0, rings[0].mean(axis=0) - (rings[1].mean(axis=0) - rings[0].mean(axis=0)) / max(
            np.linalg.norm(rings[1].mean(axis=0) - rings[0].mean(axis=0)), 1e-9) * axis_push))
    if cap_end:
        ends.append((K - 1, rings[-1].mean(axis=0) + (rings[-1].mean(axis=0) - rings[-2].mean(axis=0)) / max(
            np.linalg.norm(rings[-1].mean(axis=0) - rings[-2].mean(axis=0)), 1e-9) * axis_push))
    for ring, tip in ends:
        idx = len(P)
        P = np.vstack([P, tip[None]])
        r0 = ring * S
        tris.append(np.array([(r0 + s, idx, r0 + (s + 1) % S) if ring == 0 else (r0 + s, r0 + (s + 1) % S, idx)
                              for s in range(S)], dtype=np.int64))
    T = np.vstack(tris)
    if cap_start and cap_end:
        a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
        if float((a * np.cross(b, c)).sum()) < 0.0:
            T = ck.flip(T)
    return P, T


def zsection(z: float, top: float, bot: float, hw: float, wfrac: float, segs: int, exps=(2.4, 2.0, 2.3),
             cx: float = 0.0) -> np.ndarray:
    """A section across z: a superellipse, `exps` (top, bottom, sides) its exponents, widest at wfrac up."""
    th = np.arange(segs) * (2.0 * math.pi / segs)
    c, s = np.cos(th), np.sin(th)
    wy = bot + wfrac * (top - bot)
    y = np.where(c >= 0.0, wy + (top - wy) * sgnpow(c, 2.0 / exps[0]), wy + (wy - bot) * sgnpow(c, 2.0 / exps[1]))
    x = cx + hw * sgnpow(s, 2.0 / exps[2])
    return np.column_stack([x, y, np.full(segs, z)])


def ysection(y: float, cz: float, cx: float, hw: float, front: float, back: float, segs: int) -> np.ndarray:
    """A leg's section across y: an oval, deeper in front or behind."""
    th = np.arange(segs) * (2.0 * math.pi / segs)
    c, s = np.cos(th), np.sin(th)
    return np.column_stack([cx + hw * s, np.full(segs, y), cz + np.where(c >= 0.0, front, back) * c])


def normals_of(P: np.ndarray, T: np.ndarray) -> np.ndarray:
    return ck.weld_normals(P, ck.vertex_normals(P, T))


def ray_far(P: np.ndarray, T: np.ndarray, o: np.ndarray, d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The farthest point where the ray o + t d (t > 0) crosses the surface (P, T), and the surface's outward normal
    there (facing along d): from inside a body, its outer skin."""
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    e1, e2 = b - a, c - a
    h = np.cross(d, e2)
    det = (e1 * h).sum(axis=1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    s = o - a
    u = (s * h).sum(axis=1) * inv
    q = np.cross(s, e1)
    v = (q * d).sum(axis=1) * inv
    t = (e2 * q).sum(axis=1) * inv
    hit = ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1.0 + 1e-9) & (t > 1e-6)
    if not hit.any():
        raise ValueError(f"a harness ray from {o} along {d} misses the body")
    k = int(np.argmax(np.where(hit, t, -np.inf)))
    n = np.cross(e1[k], e2[k])
    n /= np.linalg.norm(n)
    if float(n @ d) < 0.0:
        n = -n
    return o + d * t[k], n


def surface_arc(P: np.ndarray, T: np.ndarray, o, e1, e2, angles) -> tuple[np.ndarray, np.ndarray]:
    """Points on the outer surface hit by rays from o in the plane (e1, e2) at `angles` (radians from e1 toward e2),
    with their normals smoothed along the arc."""
    o = np.asarray(o, dtype=np.float64)
    pts, nrm = [], []
    for a in angles:
        p, n = ray_far(P, T, o, math.cos(a) * np.asarray(e1) + math.sin(a) * np.asarray(e2))
        pts.append(p)
        nrm.append(n)
    pts, nrm = np.array(pts), np.array(nrm)
    sm = nrm.copy()
    sm[1:-1] = nrm[:-2] + 2.0 * nrm[1:-1] + nrm[2:]
    return pts, sm / np.linalg.norm(sm, axis=1, keepdims=True)


STRAP_SECTION = np.array([(1.0, -0.8), (1.0, 0.8), (0.0, 1.0), (-1.0, 0.8), (-1.0, -0.8),
                          (0.0, -1.0)])  # a strap's section (across, out): flat-sided, its face a little domed


def band(pts: np.ndarray, nrm: np.ndarray, across, width: float, thick: float, closed: bool,
         section: np.ndarray = STRAP_SECTION) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A strap laid along surface points (their normals out of the body): its inner face on the surface, `across` its
    width direction (one vector, or one per point). Returns (P, T, the section's out coordinate per vertex, 0..1)."""
    pts, nrm = np.asarray(pts, dtype=np.float64), np.asarray(nrm, dtype=np.float64)
    acr = np.broadcast_to(np.asarray(across, dtype=np.float64), pts.shape).copy()
    acr -= nrm * (acr * nrm).sum(axis=1, keepdims=True)
    acr /= np.linalg.norm(acr, axis=1, keepdims=True)
    centre = pts + nrm * (thick * 0.5 - 0.001)
    rings = [centre[k] + np.outer(section[:, 0] * width * 0.5, acr[k]) + np.outer(section[:, 1] * thick * 0.5, nrm[k])
             for k in range(len(pts))]
    if closed:
        rings.append(rings[0])
    P, T = close_loft(rings, cap_start=not closed, cap_end=not closed)
    if closed:  # a ring: wind it outward by the first face against the body's centre
        fn = np.cross(P[T[0, 1]] - P[T[0, 0]], P[T[0, 2]] - P[T[0, 0]])
        if float(fn @ (P[T[0]].mean(axis=0) - pts.mean(axis=0))) < 0.0:
            T = ck.flip(T)
    out = np.tile((section[:, 1] + 1.0) * 0.5, len(rings))
    out = np.concatenate([out, np.full(len(P) - len(out), 0.5)])
    return P, T, out


def torus(c, axis, R: float, r: float, n_major: int = 8, n_minor: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """A ring (a brass D- or O-ring) round `axis` at c."""
    ax = np.asarray(axis, dtype=np.float64)
    ax /= np.linalg.norm(ax)
    u = np.cross(ax, [0.0, 1.0, 0.0] if abs(ax[1]) < 0.9 else [1.0, 0.0, 0.0])
    u /= np.linalg.norm(u)
    v = np.cross(ax, u)
    rings = []
    for k in range(n_major + 1):
        a = 2.0 * math.pi * k / n_major
        rad = math.cos(a) * u + math.sin(a) * v
        b = np.arange(n_minor) * (2.0 * math.pi / n_minor)
        rings.append(np.asarray(c) + R * rad + r * (np.outer(np.cos(b), rad) + np.outer(np.sin(b), ax)))
    P, T = close_loft(rings, cap_start=False, cap_end=False)
    fn = np.cross(P[T[0, 1]] - P[T[0, 0]], P[T[0, 2]] - P[T[0, 0]])
    if float(fn @ (P[T[0]].mean(axis=0) - (np.asarray(c) + R * u))) < 0.0:
        T = ck.flip(T)
    return P, T


def blend_parent(skin, rig: ck.Rig, parent: str, y0: float, y1: float):
    """A leg's skin whose top (above y0, all the way at y1) shares half its weight with the body bone it hangs from."""
    ip = rig.index(parent)

    def f(P):
        J, W = skin(P)
        J, W = J.copy(), W.copy()
        w = 0.5 * ck.smoothstep(y0, y1, P[:, 1])
        top = w > 1e-6
        J[top, 1] = ip
        W[top] = np.column_stack([1.0 - w[top], w[top]])
        return J, W

    return f


def near_skin(skin, rig: ck.Rig, bone: str, at: np.ndarray, reach: float):
    """`skin` with the vertices within `reach` of `at` handed over toward `bone` (90% at `at`): a strap's end that
    rides a ring on another bone."""
    ib = rig.index(bone)

    def f(P):
        J, W = skin(P)
        J, W = J.copy(), W.copy()
        w = 0.9 * ck.smoothstep(reach, 0.0, np.linalg.norm(P - at, axis=1))
        near = w > 1e-6
        J[near, 1] = ib
        W[near] = np.column_stack([1.0 - w[near], w[near]])
        return J, W

    return f


def clamp_col(col: np.ndarray) -> np.ndarray:
    return np.clip(col, FLOOR_COL, CEIL_COL)


def coat_colour(P: np.ndarray, saddle: np.ndarray, under: np.ndarray, seed: int) -> np.ndarray:
    """Mud-coloured: sand_wet into tortoiseshell, darker along a saddle, a faint brindle on the sides, pale below."""
    n = ck.fbm(P * 9.0, seed)
    col = ck.mix(PAL["sand_wet"] * 0.86, PAL["tortoiseshell"], np.clip(0.3 + 0.6 * saddle + 0.4 * (n - 0.5), 0.0, 1.0)[:, None])
    warp = ck.fbm(P * 5.0, seed + 1)
    stripe = 0.5 + 0.5 * np.sin(P[:, 2] * 75.0 + P[:, 1] * 22.0 + warp * 8.0)
    brindle = ck.smoothstep(0.55, 0.95, stripe) * (1.0 - under) * 0.5
    col = ck.mix(col, PAL["tortoiseshell"] * 0.55, brindle[:, None])
    col = ck.mix(col, PALE, (0.85 * under)[:, None])
    col = col * (0.95 + 0.1 * ck.fbm(P * 26.0, seed + 2))[:, None]
    return clamp_col(col)


# ---------------------------------------------------------------------------------------------
# The body
# ---------------------------------------------------------------------------------------------
def torso_mesh() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The torso's surface, before colour: (P, T, the widest y per vertex, the ribs' grooves 0..1)."""
    st = smooth_table(TORSO, TORSO_RINGS)
    rings = [zsection(z, top, bot, hw, wf, TORSO_SEGS, TORSO_EXP) for z, top, bot, hw, wf in st]
    P, T = close_loft(rings, axis_push=0.01)
    wy = np.interp(P[:, 2], st[:, 0], st[:, 2] + st[:, 4] * (st[:, 1] - st[:, 2]))
    # the ribs: shallow grooves on the barrel's sides, between the elbow's line and the waist
    side = ck.smoothstep(0.35, 0.8, np.abs(P[:, 0]) / np.maximum(np.interp(P[:, 2], st[:, 0], st[:, 3]), 1e-6))
    zone = ck.smoothstep(RIBS[0], RIBS[0] + 0.06, P[:, 2]) * ck.smoothstep(RIBS[1], RIBS[1] - 0.06, P[:, 2])
    below = ck.smoothstep(wy + 0.06, wy - 0.02, P[:, 1])
    rib = (0.5 - 0.5 * np.cos(P[:, 2] * 2.0 * math.pi / RIBS[2])) * side * zone * below
    N = normals_of(P, T)
    P = P - N * (RIBS[3] * rib)[:, None]
    return P, T, wy, rib


def torso(mesh: ck.Mesh, rig: ck.Rig) -> tuple[np.ndarray, np.ndarray]:
    P, T, wy, rib = torso_mesh()
    st = smooth_table(TORSO, TORSO_RINGS)
    top = np.interp(P[:, 2], st[:, 0], st[:, 1])
    bot = np.interp(P[:, 2], st[:, 0], st[:, 2])
    saddle = ck.smoothstep(wy, top, P[:, 1])
    under = ck.smoothstep(wy - 0.02, bot + 0.04, P[:, 1])
    col = coat_colour(P, saddle, under, SEED)
    # creases: behind the elbows, the flank's tuck in front of the thigh, the groin
    elbow = np.exp(-(((np.abs(P[:, 0]) - 0.09) / 0.05) ** 2 + ((P[:, 1] - 0.5) / 0.06) ** 2 + ((P[:, 2] - 0.22) / 0.06) ** 2))
    tuck = np.exp(-(((P[:, 1] - 0.62) / 0.05) ** 2 + ((P[:, 2] + 0.3) / 0.07) ** 2)) * ck.smoothstep(0.03, 0.08, np.abs(P[:, 0]))
    cav = np.clip(0.15 + 0.45 * rib + 0.5 * elbow + 0.45 * tuck, 0.0, 1.0)
    # the belly wet with the flats' mud, in splashes
    wet = 0.45 * under * ck.smoothstep(0.35, 0.7, ck.fbm(P * 14.0, SEED + 3)) + 0.06
    col = ck.mix(col, MUD, (0.35 * under * ck.smoothstep(0.45, 0.7, ck.fbm(P * 14.0, SEED + 3)))[:, None])
    ck.finish(mesh, P, T, "coat", clamp_col(col), torso_skin(rig), cavity=cav, wet=wet)
    old_scar(mesh, rig, P, T)
    TORSO_LOOK["col"] = clamp_col(col)
    TORSO_LOOK["N"] = ck.weld_normals(P, ck.vertex_normals(P, T))
    return P, T


def neck_mesh() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    path = ck.bezier(np.array(NECK_PATH), 10)
    rad = np.linspace(NECK_R[0], NECK_R[1], 10)
    P, T = ck.tube(path, rad, 14, squash=NECK_SQUASH, up_hint=(0.0, 1.0, 0.0))
    return P, T, path


def neck(mesh: ck.Mesh, rig: ck.Rig) -> tuple[np.ndarray, np.ndarray]:
    P, T, path = neck_mesh()
    cy = np.interp(P[:, 2], path[:, 2], path[:, 1])
    saddle = ck.smoothstep(cy, cy + 0.07, P[:, 1])
    under = ck.smoothstep(cy - 0.01, cy - 0.07, P[:, 1])
    col = coat_colour(P, saddle, under, SEED + 10)
    ck.finish(mesh, P, T, "coat", col, neck_skin(rig), cavity=0.12, wet=0.04)
    return P, T


def head_mesh(table, segs: int, exps=(2.3, 2.1, 2.3)) -> tuple[np.ndarray, np.ndarray]:
    st = smooth_table(table, max(len(table) + 4, 12), passes=2)
    rings = [zsection(z, top, bot, hw, 0.45, segs, exps) for z, top, bot, hw in st]
    return close_loft(rings, axis_push=0.004)


def head(mesh: ck.Mesh, rig: ck.Rig) -> tuple[np.ndarray, np.ndarray]:
    hb = rig.rigid("head")
    P, T = head_mesh(HEAD, HEAD_SEGS)
    st = np.asarray(HEAD)
    top = np.interp(P[:, 2], st[:, 0], st[:, 1])
    bot = np.interp(P[:, 2], st[:, 0], st[:, 2])
    mid = bot + 0.45 * (top - bot)
    saddle = ck.smoothstep(mid, top, P[:, 1])
    under = ck.smoothstep(mid, bot, P[:, 1]) * ck.smoothstep(0.62, 0.52, P[:, 2])
    col = coat_colour(P, saddle, under * 0.5, SEED + 20)
    mask = ck.smoothstep(0.6, 0.74, P[:, 2])  # the dark mask down the muzzle
    col = ck.mix(col, ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.55), (0.75 * mask)[:, None])
    lips = ck.smoothstep(bot + 0.012, bot + 0.002, P[:, 1]) * ck.smoothstep(0.56, 0.6, P[:, 2])
    inside = lips * ck.smoothstep(0.7, 0.4, np.abs(P[:, 0]) / np.maximum(np.interp(P[:, 2], st[:, 0], st[:, 3]), 1e-6))
    col = ck.mix(col, PAL["lacquer_black"], lips[:, None])
    col = ck.mix(col, MOUTH, inside[:, None])
    # the eye's socket and the brow over it
    eye = np.exp(-(((np.abs(P[:, 0]) - EYE_AT[0]) / 0.02) ** 2 + ((P[:, 1] - EYE_AT[1]) / 0.016) ** 2
                   + ((P[:, 2] - EYE_AT[2]) / 0.022) ** 2))
    wet = 0.05 + 0.5 * lips
    ck.finish(mesh, P, T, "coat", clamp_col(col), hb, cavity=np.clip(0.12 + 0.5 * eye + 0.4 * lips, 0, 1), wet=wet)
    for s in (-1.0, 1.0):
        c = np.array([s * EYE_AT[0], EYE_AT[1], EYE_AT[2]])
        Pr, Tr = ck.ellipsoid(c - np.array([s * 0.002, 0.0, 0.002]), (EYE_R * 1.25, EYE_R * 1.05, EYE_R * 1.3), 4, 8)
        ck.finish(mesh, Pr, Tr, "coat", PAL["lacquer_black"], hb, cavity=0.3, wet=0.3)
        Pe, Te = ck.ellipsoid(c, (EYE_R, EYE_R * 0.9, EYE_R), 5, 8)
        ck.finish(mesh, Pe, Te, "eye", ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.55), hb, wet=1.0)
    Pn, Tn = ck.ellipsoid(NOSE_AT, (0.017, 0.013, 0.011), 5, 8)
    Pn[:, 0] *= 0.6 + 0.4 * ck.smoothstep(NOSE_AT[1] - 0.012, NOSE_AT[1] + 0.006, Pn[:, 1])
    ck.finish(mesh, Pn, Tn, "coat", PAL["lacquer_black"], hb, wet=0.8, cavity=0.15)
    for x, y, z, way in CANINES[:1]:
        for s in (-1.0, 1.0):
            canine(mesh, np.array([s * x, y, z]), way, hb)
    return P, T


def canine(mesh: ck.Mesh, at: np.ndarray, way: float, bone: int) -> None:
    path = np.array([at, at + np.array([0.0, way * 0.008, 0.001]), at + np.array([0.0, way * 0.015, 0.003])])
    P, T = ck.tube(path, np.array([0.0042, 0.003, 0.0008]), 5, cap_start=True, cap_end=True)
    ck.finish(mesh, P, T, "coat", PAL["bone"] * 0.92, bone, wet=0.4)


def jaw(mesh: ck.Mesh, rig: ck.Rig) -> None:
    jb = rig.rigid("jaw")
    P, T = head_mesh(JAW, 10, exps=(2.6, 1.9, 2.3))
    st = np.asarray(JAW)
    top = np.interp(P[:, 2], st[:, 0], st[:, 1])
    bot = np.interp(P[:, 2], st[:, 0], st[:, 2])
    under = ck.smoothstep(top - 0.01, bot, P[:, 1])
    col = coat_colour(P, np.zeros(len(P)), under * 0.6, SEED + 30)
    col = ck.mix(col, ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.5), (0.6 * ck.smoothstep(0.64, 0.74, P[:, 2]))[:, None])
    lips = ck.smoothstep(top - 0.01, top - 0.002, P[:, 1])
    inside = lips * ck.smoothstep(0.7, 0.4, np.abs(P[:, 0]) / np.maximum(np.interp(P[:, 2], st[:, 0], st[:, 3]), 1e-6))
    col = ck.mix(ck.mix(col, PAL["lacquer_black"], lips[:, None]), MOUTH, inside[:, None])
    ck.finish(mesh, P, T, "coat", clamp_col(col), jb, cavity=0.15 + 0.4 * lips, wet=0.05 + 0.5 * lips)
    x, y, z, way = CANINES[1]
    for s in (-1.0, 1.0):
        canine(mesh, np.array([s * x, y, z]), way, jb)


def ears(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Rose ears: thin leaves rising from behind the skull and folding back and out at the tip, dark behind."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        path = ck.bezier(np.array(EAR_PATH) * np.array([s, 1.0, 1.0]), EAR_STATIONS)
        tan = np.gradient(path, axis=0)
        tan /= np.linalg.norm(tan, axis=1, keepdims=True)
        face = np.array([s * 1.0, 0.6, 0.35])  # folded back: the leaf lies along the skull, its inside out and up
        broad = np.cross(tan, face)
        broad /= np.linalg.norm(broad, axis=1, keepdims=True)
        thin = np.cross(broad, tan)
        u = np.linspace(0.0, 1.0, EAR_STATIONS)
        w = np.interp(u, np.linspace(0, 1, len(EAR_W)), EAR_W)
        t = np.interp(u, np.linspace(0, 1, len(EAR_T)), EAR_T)
        segs = 12
        th = np.arange(segs) * (2.0 * math.pi / segs)
        # cupped (the edges curl in) and folded: the rose ear's crease runs down the leaf's middle, deepest mid-ear
        fold = 0.012 * np.sin(u * math.pi)
        rings = [path[k] + np.outer(np.cos(th) * w[k] * 0.5, broad[k]) + np.outer(np.sin(th) * t[k] * 0.5, thin[k])
                 + np.outer(-np.abs(np.cos(th)) * t[k] * 0.6 + fold[k] * (1.0 - np.abs(np.cos(th))) ** 2, thin[k])
                 for k in range(EAR_STATIONS)]
        P, T = close_loft(rings, axis_push=0.002)
        inner = np.tile(ck.smoothstep(0.0, 0.8, np.sin(th)), EAR_STATIONS)
        inner = np.concatenate([inner, np.zeros(len(P) - len(inner))])
        col = ck.mix(ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.5), PAL["tortoiseshell"] * 0.9, inner[:, None])
        ck.finish(mesh, P, T, "coat", clamp_col(col), rig.rigid(f"ear_{tag}"), cavity=0.45 * inner + 0.1)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier(np.array(TAIL_PATH), 12)
    P, T = ck.tube(path, np.linspace(TAIL_R[0], TAIL_R[1], 12), 7)
    u = np.concatenate([np.repeat(np.linspace(0.0, 1.0, 12), 7), [0.0, 1.0]])
    col = coat_colour(P, np.full(len(P), 0.6), np.zeros(len(P)), SEED + 40)
    col = ck.mix(col, PAL["tortoiseshell"] * 0.7, ck.smoothstep(0.7, 1.0, u)[:, None])
    tb = rig.bones
    pts = [tb[rig.index("tail0")].head, tb[rig.index("tail1")].head, tb[rig.index("tail1")].tail]
    ck.finish(mesh, P, T, "coat", col, rig.chain(["tail0", "tail1"], pts), cavity=0.15, wet=0.05)


# ---------------------------------------------------------------------------------------------
# The legs and the hare feet
# ---------------------------------------------------------------------------------------------
# The torso's colour and normals, kept by torso() for the legs' tops to blend into (M3-CRE-660).
TORSO_LOOK: dict = {}
# Where a leg's top blends into the body: from this far under the leg's first section (m), the leg's shading and
# colour turn to the body's nearest point, wholly at the section, so no seam outlines the shoulder or the thigh.
LEG_JOIN_M = 0.14


def blend_into_body(P: np.ndarray, N: np.ndarray, col: np.ndarray, top_y: float, body: tuple) -> tuple:
    """The leg's normals and colour near its top turned to the body's nearest vertex's (M3-CRE-660)."""
    bP = body[0]
    near = np.argmin(((P[:, None, :] - bP[None, :, :]) ** 2).sum(axis=2), axis=1)
    k = ck.smoothstep(top_y - LEG_JOIN_M, top_y - 0.02, P[:, 1])[:, None]
    n = N * (1.0 - k) + TORSO_LOOK["N"][near] * k
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    return n, col * (1.0 - k) + TORSO_LOOK["col"][near] * k


def leg(mesh: ck.Mesh, rig: ck.Rig, name: str, body: tuple) -> None:
    fb = "f" if LEGS[name][2] else "b"
    side = LEGS[name][1]
    table = FORELEG if fb == "f" else HINDLEG
    rings = [ysection(y, cz, side * cx, hw, f, b, LEG_SEGS) for y, cz, cx, hw, f, b in table]
    P, T = close_loft(rings, axis_push=0.006)
    a, knee, ankle, paw = leg_points(name)
    skin = rig.chain([f"{name}_upper", f"{name}_lower", f"{name}_paw"], [a, knee, ankle, paw])
    skin = blend_parent(skin, rig, "chest" if fb == "f" else "hips", LEG_BLEND_Y[fb], table[0][0])
    # colour: the coat above, pale inside and behind, mud and wet below the wrist or hock
    inner = ck.smoothstep(0.0, -0.8, (P[:, 0] - side * table[2][2]) * side / 0.05)
    saddle = ck.smoothstep(0.55, 0.75, P[:, 1]) * 0.6
    under = np.clip(0.55 * inner + 0.45 * ck.smoothstep(0.4, 0.2, P[:, 1]), 0.0, 1.0)
    col = coat_colour(P, saddle, under, SEED + 50 + list(LEGS).index(name))
    mudline = 0.2 + 0.05 * ck.fbm(P * 20.0, SEED + 60)
    mud = ck.smoothstep(mudline, mudline - 0.08, P[:, 1])
    col = ck.mix(col, MUD, (0.8 * mud)[:, None])
    # creases: where the leg enters the body, behind the elbow or the stifle
    joint = knee[1] if fb == "f" else 0.38
    crease = ck.smoothstep(LEG_BLEND_Y[fb] - 0.04, table[0][0], P[:, 1]) + 0.4 * np.exp(-((P[:, 1] - joint) / 0.04) ** 2)
    N, col = blend_into_body(P, ck.weld_normals(P, ck.vertex_normals(P, T)), clamp_col(col), table[0][0], body)
    ck.finish(mesh, P, T, "coat", clamp_col(col), skin, cavity=np.clip(0.12 + 0.5 * crease, 0, 1), wet=0.75 * mud,
              N=N)
    foot(mesh, rig, name, side, table[-1][2] * side, PAW[fb])


def foot(mesh: ck.Mesh, rig: ck.Rig, name: str, side: float, cx: float, cz: float) -> None:
    """A hare foot: an oval pad body, flat on the floor, with four toes ahead of it, their nails dark."""
    pb = rig.rigid(f"{name}_paw")
    c = np.array([cx, PAW_R[1], cz])
    P, T = ck.ellipsoid(c, PAW_R, 4, 8)
    P[:, 1] = np.maximum(P[:, 1], SOLE_Y)
    ck.finish(mesh, P, T, "coat", MUD * 0.95, pb, cavity=0.25, wet=0.85)
    for (tx, tz, tr), tag in ((TOES[0], "m"), (TOES[1], "s")):
        for sx in (-1.0, 1.0):
            tc = c + np.array([sx * tx, -PAW_R[1] + tr * 0.95, tz])
            Pt, Tt = ck.ellipsoid(tc, (tr * 0.78, tr, tr * 1.1), 3, 6)
            Pt[:, 1] = np.maximum(Pt[:, 1], SOLE_Y)
            nail = ck.smoothstep(0.3, 0.9, (Pt[:, 2] - tc[2]) / (tr * 1.1)) * ck.smoothstep(0.4, -0.2, (Pt[:, 1] - tc[1]) / tr)
            col = ck.mix(MUD, PAL["lacquer_black"], nail[:, None])
            ck.finish(mesh, Pt, Tt, "coat", col, pb, cavity=0.3 * (1.0 - nail), wet=0.85)


def legs(mesh: ck.Mesh, rig: ck.Rig, body: tuple) -> None:
    for name in LEGS:
        leg(mesh, rig, name, body)


# ---------------------------------------------------------------------------------------------
# The weak point (unchanged from M3-CRE-650, laid on the new chest)
# ---------------------------------------------------------------------------------------------
def on_surface(P: np.ndarray, T: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The point of the part (P, T) nearest q, and its face's outward normal: q projected onto each triangle's plane,
    kept where it falls inside the triangle, the nearest of those (degenerate triangles, as at a pole, are skipped)."""
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    area = np.linalg.norm(fn, axis=1)
    fn /= np.maximum(area, 1e-12)[:, None]
    d = ((q - a) * fn).sum(axis=1)
    p = q - d[:, None] * fn
    inside = area > 1e-12
    for u, v in ((a, b), (b, c), (c, a)):
        inside &= (np.cross(v - u, p - u) * fn).sum(axis=1) >= 0.0
    k = int(np.argmin(np.where(inside, np.abs(d), np.inf)))
    return p[k], fn[k]


def old_scar(mesh: ck.Mesh, rig: ck.Rig, P: np.ndarray, T: np.ndarray) -> None:
    """The weak point (ADR 0151): a closed seam of spawn_wound light in a raised dark lip, laid on the chest at SCAR_AT
    and bent to its curve. Never open, never shedding motes: it is a dog, and this is an old wound."""
    at, n = on_surface(P, T, SCAR_AT)
    a = SCAR_ALONG - n * (SCAR_ALONG @ n)
    a /= np.linalg.norm(a)
    R = np.column_stack([a, n, np.cross(a, n)])  # local x along the scar, y out of the skin, z across it
    (hl, hw), (gl, gw, rise) = SCAR_HALF, SCAR_LIP
    for radii, lift, col, glow in (((hl * gl, rise, hw * gw), 0.0, ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.5), 0.0),
                                   ((hl, rise * 0.75, hw), rise * 0.5, PAL["spawn_wound"] * 0.65, 1.0)):
        Pl, Tl = ck.ellipsoid((0.0, lift, 0.0), radii, 4, 10)
        Pl[:, 1] -= Pl[:, 0] ** 2 / (2.0 * SCAR_BEND_R)
        ck.finish(mesh, at + Pl @ R.T, Tl, "coat", col, rig.rigid("chest"), cavity=0.4 * (1.0 - glow), emission=glow)


# ---------------------------------------------------------------------------------------------
# The Order's harness and the muzzle cage
# ---------------------------------------------------------------------------------------------
def leather(mesh: ck.Mesh, P: np.ndarray, T: np.ndarray, out: np.ndarray, skin, seed: int) -> None:
    """Oiled tortoiseshell leather: burnished darker at the edges, the grain's colour wandering, a little damp."""
    edge = 1.0 - np.abs(out * 2.0 - 1.0)
    col = LEATHER * (0.86 + 0.22 * ck.fbm(P * 30.0, seed))[:, None]
    col = ck.mix(col, PAL["lacquer_black"], (0.35 * (1.0 - edge))[:, None])
    ck.finish(mesh, P, T, "leather", clamp_col(col), skin, cavity=0.2 + 0.4 * (1.0 - edge), wet=0.15)


def harness(mesh: ck.Mesh, rig: ck.Rig, body: tuple[np.ndarray, np.ndarray], neckm: tuple[np.ndarray, np.ndarray]) -> None:
    """A Y-harness: a neck ring at the neck's base, a strap down the breast between the forelegs to a girth behind the
    elbows, and a back strap from the ring to the girth over the withers, where the Order's plate rides; brass rings
    where the straps meet."""
    Pb, Tb = body
    Pn, Tn = neckm
    Pu = np.vstack([Pb, Pn])
    Tu = np.vstack([Tb, Tn + len(Pb)])
    skin = torso_skin(rig)
    # the neck ring: round the neck's curve where it leaves the shoulders
    path = ck.bezier(np.array(NECK_PATH), 41)
    k = int(round(NECK_RING_U * 40))
    o = path[k]
    tan = path[k + 1] - path[k - 1]
    tan /= np.linalg.norm(tan)
    e1 = np.array([0.0, 1.0, 0.0]) - tan * tan[1]
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(tan, e1)
    ang = np.linspace(0.0, 2.0 * math.pi, 22, endpoint=False)
    ring_pts, ring_n = surface_arc(Pu, Tu, o, e1, e2, ang)
    P, T, out = band(ring_pts, ring_n, tan, STRAP_W * 1.15, STRAP_T, closed=True)
    leather(mesh, P, T, out, rig.chain(["chest", "neck"], [SHOULDER - np.array([0, 0, 0.3]), SHOULDER,
                                                            SHOULDER + np.array([0, 0.2, 0.22])]), SEED + 70)
    ring_top = ring_pts[0]
    ring_front = ring_pts[int(np.argmin(ring_pts[:, 1] - ring_pts[:, 2]))]  # low and forward: the breast's end
    # the girth: a band round the chest behind the elbows
    gp, gn = np.asarray(GIRTH[0], dtype=np.float64), np.asarray(GIRTH[1], dtype=np.float64)
    gn /= np.linalg.norm(gn)
    g1 = np.array([0.0, 1.0, 0.0]) - gn * gn[1]
    g1 /= np.linalg.norm(g1)
    g2 = np.cross(gn, g1)
    gpts, gnrm = surface_arc(Pb, Tb, gp, g1, g2, np.linspace(0.0, 2.0 * math.pi, 28, endpoint=False))
    P, T, out = band(gpts, gnrm, gn, STRAP_W * 1.5, STRAP_T, closed=True)
    leather(mesh, P, T, out, skin, SEED + 71)
    girth_top, girth_bot = gpts[0], gpts[14]
    # the breast strap: down the midline from the neck ring's front to the girth's bottom
    o = np.array([0.0, 0.66, 0.22])
    a0 = math.atan2(ring_front[1] - o[1], ring_front[2] - o[2])
    a1 = math.atan2(girth_bot[1] - o[1], girth_bot[2] - o[2])
    ang = np.linspace(a0, a1 - (2.0 * math.pi if a1 > a0 else 0.0), 16)
    spts, snrm = surface_arc(Pu, Tu, o, np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0]), ang)
    P, T, out = band(spts, snrm, np.array([1.0, 0.0, 0.0]), STRAP_W, STRAP_T * 1.1, closed=False)
    front_skin = near_skin(skin, rig, "neck", ring_front, RING_REACH)
    leather(mesh, P, T, out, front_skin, SEED + 72)
    # the back strap: over the withers from the neck ring's top to the girth's top
    o = np.array([0.0, 0.7, 0.22])
    a0 = math.atan2(ring_top[1] - o[1], ring_top[2] - o[2])
    a1 = math.atan2(girth_top[1] - o[1], girth_top[2] - o[2])
    bpts, bnrm = surface_arc(Pu, Tu, o, np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0]), np.linspace(a0, a1, 9))
    P, T, out = band(bpts, bnrm, np.array([1.0, 0.0, 0.0]), STRAP_W, STRAP_T * 1.1, closed=False)
    leather(mesh, P, T, out, near_skin(skin, rig, "neck", ring_top, RING_REACH), SEED + 73)
    order_plate(mesh, rig, bpts[4], bnrm[4], bpts[5] - bpts[3])
    # brass: an O-ring where the breast strap meets the neck ring, D-rings at the girth's sides
    metal = clamp_col(PAL["brass"])
    Pr, Tr = torus(spts[0] + snrm[0] * STRAP_T * 1.2, snrm[0], 0.016, 0.0042)
    ck.finish(mesh, Pr, Tr, "metal", metal, front_skin, cavity=0.2)
    for idx in (7, 21):
        p, n = gpts[idx], gnrm[idx]
        Pr, Tr = torus(p + n * STRAP_T * 1.1 + np.array([0.0, -0.012, 0.0]), np.cross(n, gn), 0.014, 0.0038)
        ck.finish(mesh, Pr, Tr, "metal", metal, skin, cavity=0.2)


def order_plate(mesh: ck.Mesh, rig: ck.Rig, at: np.ndarray, n: np.ndarray, along: np.ndarray) -> None:
    """The Order's mark at the withers: a lacquered oval plate, black-rimmed, its face order_marble with the Level
    stamped across it (a level line under a dome's arc), and a brass ring behind it for the leash."""
    along = along - n * (along @ n)
    along /= np.linalg.norm(along)
    side = np.cross(n, along)
    R = np.column_stack([side, n, along])
    skin = torso_skin(rig)
    base = at + n * (STRAP_T * 1.1)
    for (rx, ry, rz), lift, col in (((PLATE_R[1] * 1.18, PLATE_R[2], PLATE_R[0] * 1.15), 0.0, PAL["lacquer_black"]),
                                    ((PLATE_R[1], PLATE_R[2], PLATE_R[0]), PLATE_R[2] * 0.5, PAL["order_marble"])):
        P, T = ck.ellipsoid((0.0, lift, 0.0), (rx, ry, rz), 3, 10)
        P[:, 1] = np.maximum(P[:, 1], lift - ry * 0.3)
        Pw = base + P @ R.T
        mark = np.zeros(len(P))
        if lift > 0.0:  # the Level: a bar across, under an arc
            bar = np.exp(-((P[:, 2] + 0.004) / 0.004) ** 2) * (np.abs(P[:, 0]) < PLATE_R[1] * 0.65)
            arc = np.exp(-((np.hypot(P[:, 0], P[:, 2] + 0.004) - 0.016) / 0.0035) ** 2) * (P[:, 2] > -0.004)
            mark = np.clip(bar + arc, 0.0, 1.0)
        ck.finish(mesh, Pw, T, "lacquer", ck.mix(col, PAL["lacquer_black"], (0.7 * mark)[:, None]), skin,
                  cavity=0.5 * mark, wet=0.7)
    Pr, Tr = torus(base - along * PLATE_R[0] * 1.5 + n * 0.012, side, 0.017, 0.0045)
    ck.finish(mesh, Pr, Tr, "metal", clamp_col(PAL["brass"]), skin, cavity=0.2)


def cage_point(z: float, theta: float, scale: float = 1.0) -> np.ndarray:
    """A point on the muzzle cage's surface: round the snout and the jaw together at z, theta from the top."""
    hz = np.asarray(HEAD)[:, 0]
    jz = np.asarray(JAW)[:, 0]
    top = float(np.interp(z, hz, np.asarray(HEAD)[:, 1])) + CAGE_GAP
    bot = float(np.interp(z, jz, np.asarray(JAW)[:, 2])) - CAGE_GAP
    hw = max(float(np.interp(z, hz, np.asarray(HEAD)[:, 3])), float(np.interp(z, jz, np.asarray(JAW)[:, 3]))) + CAGE_GAP
    cy, hh = (top + bot) / 2.0, (top - bot) / 2.0
    c, s = math.cos(theta), math.sin(theta)
    return np.array([hw * scale * float(sgnpow(np.array(s), 2.0 / 2.6)), cy + hh * scale * float(sgnpow(np.array(c), 2.0 / 2.6)), z])


def cage_skin(rig: ck.Rig):
    """The cage's lower half rides the jaw (lacquered bars that flex), its upper half the head."""
    ih, ij = rig.index("head"), rig.index("jaw")

    def f(P):
        w = ck.smoothstep(MOUTH_Y + 0.004, MOUTH_Y - 0.022, P[:, 1])
        J = np.tile([ih, ij], (len(P), 1))
        return J, np.column_stack([1.0 - w, w])

    return f


def muzzle_cage(mesh: ck.Mesh, rig: ck.Rig, headm: tuple[np.ndarray, np.ndarray]) -> None:
    """The Order's basket muzzle: red-lacquered hoops and bars round the snout and jaw, closed at the front, on a
    leather headstall over the poll (behind the ears) and up the forehead."""
    skin = cage_skin(rig)
    lac = PAL["lacquer_red"]
    for z in CAGE_HOOPS:
        pts = np.array([cage_point(z, t) for t in np.linspace(0.0, 2.0 * math.pi, 16, endpoint=False)])
        P, T = ck.tube(np.vstack([pts, pts[:1]]), CAGE_R, 4, cap_start=False, cap_end=False)
        ck.finish(mesh, P, T, "lacquer", lac, skin, cavity=0.1, wet=0.6)
    for deg in CAGE_BARS:
        th = math.radians(deg)
        zs = np.linspace(CAGE_HOOPS[0], CAGE_FRONT, 7)
        sc = 1.0 - 0.55 * ck.smoothstep(CAGE_HOOPS[-1], CAGE_FRONT, zs)  # the bars close in over the nose
        pts = np.array([cage_point(float(z), th, float(s)) for z, s in zip(zs, sc)])
        pts[-1, 2] += 0.008
        P, T = ck.tube(pts, CAGE_R * 0.9, 4)
        ck.finish(mesh, P, T, "lacquer", lac, skin, cavity=0.1, wet=0.6)
    # the headstall: from the cage's back hoop at each cheek, behind the eyes, over the poll behind the ears
    Ph, Th = headm
    hb = rig.rigid("head")
    o = np.array([0.0, 1.0, 0.545])
    left = cage_point(CAGE_HOOPS[0], math.pi / 2.0)
    over = np.array([0.0, 1.09, 0.455])
    e1 = left - o
    e1 /= np.linalg.norm(e1)
    nrm = np.cross(e1, over - o)
    nrm /= np.linalg.norm(nrm)
    e2 = np.cross(nrm, e1)
    right = left * np.array([-1.0, 1.0, 1.0]) - o
    a_end = math.atan2(float(right @ e2), float(right @ e1))
    a_end = a_end if a_end > 0.0 else a_end + 2.0 * math.pi
    pts, nr = surface_arc(Ph, Th, o, e1, e2, np.linspace(0.0, a_end, 15))
    P, T, out = band(pts, nr, nrm, STRAP_W * 0.6, STRAP_T * 0.8, closed=False)
    leather(mesh, P, T, out, hb, SEED + 80)
    top = pts[7]
    fore = cage_point(CAGE_HOOPS[0], 0.0)
    a0 = math.atan2(fore[1] - o[1], fore[2] - o[2])
    a1 = math.atan2(top[1] - o[1], top[2] - o[2])
    pts, nr = surface_arc(Ph, Th, o, np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0]), np.linspace(a0, a1, 8))
    P, T, out = band(pts, nr, np.array([1.0, 0.0, 0.0]), STRAP_W * 0.5, STRAP_T * 0.8, closed=False)
    leather(mesh, P, T, out, hb, SEED + 81)
    for sx in (-1.0, 1.0):  # brass buckles where the headstall meets the cage
        c = cage_point(CAGE_HOOPS[0], sx * math.pi / 2.0) + np.array([sx * 0.004, 0.012, -0.006])
        Pr, Tr = torus(c, np.array([sx, 0.0, 0.0]), 0.008, 0.0028, 6, 3)
        ck.finish(mesh, Pr, Tr, "metal", clamp_col(PAL["brass"]), hb, cavity=0.2)


# ---------------------------------------------------------------------------------------------
# Clips (unchanged)
# ---------------------------------------------------------------------------------------------
def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 2.4, loop=True)  # standing ready: breath, weight shifting, ears forward
    idle.wave("chest", amp_rot=(1.2, 0, 0), amp_loc=(0, 0.008, 0), cycles=2)
    idle.wave("head", amp_rot=(3.0, 6.0, 0.0), cycles=1)
    idle.wave("ear_l", amp_rot=(6.0, 0, 0), cycles=1, phase=0.4)
    idle.wave("ear_r", amp_rot=(6.0, 0, 0), cycles=1, phase=1.4)
    idle.wave("tail0", amp_rot=(0, 10.0, 0), cycles=1)
    idle.wave("root", amp_loc=(0.01, 0, 0), cycles=1)
    attack = ck.Clip("attack", 1.1)  # a lunge and bite
    for t, crouch, fwd, bite in ((0.0, 0, 0, 0), (0.3, 1.0, -0.06, 0), (0.5, -0.3, 0.55, 1.0), (0.65, 0, 0.5, 0.2),
                                  (1.1, 0, 0, 0)):
        attack.key("root", t, (0, 0, 0), (0, -0.06 * crouch, fwd))
        attack.key("hips", t, (6.0 * crouch, 0, 0))
        attack.key("neck", t, (14.0 * max(-crouch, 0) * 3 - 10 * crouch, 0, 0))
        attack.key("jaw", t, (28.0 * bite, 0, 0))
        for n in ("bl", "br"):
            attack.key(f"{n}_upper", t, (-20.0 * crouch, 0, 0))
    # the forepaws step with the lunge (the audit: they slid 37 cm along the floor): a lifted step forward into the
    # crouch's bow, up and reaching as it springs, down ahead for the bite, up again and back as it recovers
    for t, reach, fold in ATTACK_FORE_STEP:
        for n in ("fl", "fr"):
            attack.key(f"{n}_upper", t, (-reach, 0, 0))
            attack.key(f"{n}_lower", t, (fold, 0, 0))
    cast = ck.Clip("cast", 1.6)  # a howl: head up, jaw open
    for t, s in ((0.0, 0.0), (0.4, 1.0), (1.2, 1.0), (1.6, 0.0)):
        cast.key("neck", t, (-35.0 * s, 0, 0))
        cast.key("head", t, (-20.0 * s, 0, 0))
        cast.key("jaw", t, (22.0 * s, 0, 0))
        cast.key("ear_l", t, (25.0 * s, 0, 0))
        cast.key("ear_r", t, (25.0 * s, 0, 0))
    hit = ck.Clip("hit", 0.55)  # a yelp and a skid
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.55, 0.0)):
        hit.key("root", t, (0, 12.0 * s, 0), (0, 0, -0.18 * s))
        hit.key("neck", t, (15.0 * s, 0, 0))
        hit.key("tail0", t, (25.0 * s, 0, 0))
    ko = ck.Clip("ko", 1.8)  # it lies down: beaten, not dead
    for t, s in ((0.0, 0.0), (0.6, 0.5), (1.3, 1.0), (1.8, 1.0)):
        ko.key("root", t, (0, 0, 0), (0, -0.42 * s, 0))
        for n in ("fl", "fr"):  # M3-CRE-632: the forelegs reach out flat along the floor (the forearm was keyed
            ko.key(f"{n}_upper", t, (-70.0 * s, 0, 0))  # +60, which drove it 0.22 m down through the floor)
            ko.key(f"{n}_lower", t, (KO_FORE * s, 0, 0))
        for n in ("bl", "br"):
            ko.key(f"{n}_upper", t, (-80.0 * s, 0, 0))
            ko.key(f"{n}_lower", t, (110.0 * s, 0, 0))
        ko.key("neck", t, (30.0 * s, 0, 0))
        ko.key("head", t, (10.0 * s, 0, 0))
        ko.key("ear_l", t, (40.0 * s, 0, 0))
        ko.key("ear_r", t, (40.0 * s, 0, 0))
        ko.key("tail0", t, (40.0 * s, 0, 0))
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): in the lunge's crouch (the body drops and pitches onto the
# forelegs) a planted paw stays on the floor, each leg reaching forward at the shoulder or hip the least it takes.
GROUNDED_LIMBS = [(f"{n}_upper", 0, -1.0, 55.0 if n[0] == "f" else 30.0) for n in ("fl", "fr", "bl", "br")]


# The planted feet held where they touch down (common/grounding.py pinned(); the Act I audit's foot sliding).
# The forepaws' steps in the lunge: (time, reach forward, knee fold) in degrees (a negative fold tucks the paw up).
ATTACK_FORE_STEP = ((0.0, 0.0, 0.0), (0.15, 18.0, -60.0), (0.3, 20.0, -40.0), (0.4, 35.0, -70.0), (0.5, 22.0, -20.0),
                    (0.65, 22.0, -20.0), (0.8, 30.0, -70.0), (0.95, 5.0, -20.0), (1.1, 0.0, 0.0))
PINNED_LEGS = [(f"{n}_upper", f"{n}_lower", 0, -1.0) for n in ("fl", "fr", "bl", "br")]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    pinned = gr.pinned(rig, mesh, gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS), PINNED_LEGS)
    return gr.reground(rig, mesh, pinned, GROUNDED_LIMBS)  # a held foot's toes back above the floor


def build_mesh() -> tuple[ck.Rig, ck.Mesh]:
    """The rig and the skinned mesh, without Blender (M3-CRE-650: the preview sheets build from this too)."""
    rig = build_rig()
    mesh = ck.Mesh("raid_hound")
    body = torso(mesh, rig)
    neckm = neck(mesh, rig)
    headm = head(mesh, rig)
    jaw(mesh, rig)
    ears(mesh, rig)
    tail(mesh, rig)
    legs(mesh, rig, body)
    harness(mesh, rig, body, neckm)
    muzzle_cage(mesh, rig, headm)
    return rig, mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and each clip's lowest point")
    args = ap.parse_args(argv)
    rig, mesh = build_mesh()
    if args.report or not args.out:
        print(f"raid_hound: {mesh.triangle_count} triangles, {mesh.count} vertices, slots {mesh.materials}")
        return
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "raid_hound"})
    print(f"raid_hound: {info}")


if __name__ == "__main__":
    main()
