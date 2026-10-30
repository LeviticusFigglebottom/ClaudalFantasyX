"""The Lamp Engine, the Ch11 boss (M3-CRE-623): docs/kb/art/creatures/act2/lamp_engine.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/lamp_engine/build_lamp_engine.py -- \
    --out assets/creatures/lamp_engine/lamp_engine.glb

A Lit Age construct: a temple lamp-stand that walks. A 3.4 m bell-hooded brass tower on four short jointed legs.
Under the hood a lantern housing of three gimballed rings, each four petal plates round a hoop, each hoop carrying
four salt-glass lamps on gimbal forks (twelve lamps); the rings turn against each other. The lamps' light is
`glimmer_bound` (steady), the gimbal hubs are the weak points (`spawn_wound`), and sea_glow drips run down the
glass. Two long trimming arms with scissor heads hang from the hood's rim. Inside the housing, threaded on the
column, a cracked salt-glass core globe holds the brightest bound light; in the `opened` phase the rings fold back
like petals (each lamp turning back in its gimbal) and the core shows (`idle_opened`, and the strikes played
from that pose). Brass goes to bronze_patina and wet at the waterline (its knees); joints are lacquer black.

Run without Blender (`python3 build_lamp_engine.py --report`) to print the triangle count and a few poses
without exporting.
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

SEED = 6230
PAL = {k: ck.hexrgb(v) for k, v in {
    "brass": "#B08D57", "bronze_patina": "#5F8A78", "lacquer_black": "#1D1916", "salt_glass": "#BFE6E0",
    "glimmer_bound": "#4FB3B0", "spawn_wound": "#3FE0C8", "sea_glow": "#1C6B78",
}.items()}
UP = np.array([0.0, 1.0, 0.0])

WATER_Y = 0.85  # the waterline: brass goes to bronze_patina and wet below it (the water is at its knees)
# The lantern housing: an ovoid shell round the core, cut into three tiers (rings) of four petals each
CY = 2.0  # the housing's (and the core's) centre height
SHELL_A, SHELL_B = 0.62, 0.75  # horizontal and vertical semi-axes
SHELL_T = 0.03  # plate thickness
TIERS = ((-64.0, -22.0), (-22.0, 22.0), (22.0, 64.0))  # latitude bands (degrees), bottom to top
TIER_AZ = (0.0, 45.0, 45.0)  # the azimuth of each tier's first petal (+Z is 0): the upper rings are staggered from the
# bottom one, and the top ring's lamps sit clear of the shoulders (at 90 and 270 degrees) when the arms swing
PETAL_GAP = 1.2  # degrees left open between two petals
# M4-CRB-003: each ring's plates flare out toward their lower edge (radially, by up to this share), so the three rings
# overlap like shingles and the housing reads as three stacked bands at battle distance, not one smooth egg
FLARE = 0.1
FOLD = (22.0, 68.0, 50.0)  # how far each tier's petals fold back in the `opened` phase (degrees)
# how far each lamp turns back in its gimbal as its petal folds: the bottom ring's stay level, the others tip out a
# little (30 and 20 degrees), which keeps the glass clear of the folded hoop above the pivot
LEVEL = (22.0, 38.0, 30.0)
HOOP_OUT = 0.065  # a hoop stands this far off the shell (clear of the plates' flare)
LAMP_OUT = 0.21  # a lamp's gimbal pivot stands this far out from its hoop
LAMP_DY = (-0.06, 0.0, 0.0)  # and this far below it (the bottom ring's lamps hang clear of the middle ring's edge)
LAMP_SCALE = 1.2  # M4-CRB-003: the lamps' size over their profiles below (the twelve lights are the read at 12 m)
HUB_OFF = 0.16  # a gimbal hub's offset either side of its lamp
CORE_R = 0.4
COLUMN = (1.3, 3.13, 0.055)  # the central column: bottom, top, radius
# The hood: (radius, y) outside from the crown down to the lip, then the underside back in
HOOD = [(0.0, 3.3), (0.15, 3.29), (0.32, 3.24), (0.5, 3.15), (0.68, 3.03), (0.83, 2.93), (0.95, 2.86),
        (1.01, 2.83), (1.01, 2.8), (0.95, 2.81), (0.8, 2.9), (0.62, 3.0), (0.42, 3.08), (0.2, 3.12), (0.0, 3.13)]
FINIAL = [(0.0, 3.4), (0.035, 3.39), (0.06, 3.36), (0.05, 3.33), (0.03, 3.31), (0.07, 3.29), (0.1, 3.28),
          (0.0, 3.27)]
BOWL = [(0.2, 1.4), (0.3, 1.3), (0.43, 1.2), (0.57, 1.12), (0.62, 1.05), (0.6, 0.98), (0.48, 0.91), (0.3, 0.87),
        (0.12, 0.85), (0.0, 0.85)]
BODY_PIVOT = (0.0, 1.04, 0.0)  # the body leans about the hips' height, so the legs stay planted
# Legs: four short jointed legs at 45 + 90k degrees, (radius, y) of the hip, the knee and the foot
LEG_AZ = (45.0, 135.0, 225.0, 315.0)
LEG = ((0.58, 1.04), (1.0, 1.12), (1.32, 0.05))
# Arms: (x, y, z) of the shoulder, elbow, wrist and scissor tip of the left arm (+x); the right mirrors it
ARM = ((1.04, 2.86, 0.0), (1.52, 3.2, 0.18), (1.74, 2.32, 0.62), (1.62, 1.84, 1.06))
SCISSOR_PIVOT = 0.1  # the blades' pivot, this far from the wrist along the head
BLADE_LEN = 0.78  # M4-CRB-003: the shears' blades, pivot to tip (they read as shears, not needles, at 12 m)
KO_DROP = 0.55  # the KO kneel: the body settles this far, its knees in the water
DORMANT_DROP = 0.22  # the intro's dormant crouch: the body this far down on bent knees before it wakes


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def shell_pt(phi, th, s: float = 1.0) -> np.ndarray:
    """A point on the housing at latitude phi and azimuth th (degrees), scaled by s about its centre."""
    ph, t = np.broadcast_arrays(np.radians(np.asarray(phi, dtype=np.float64)),
                                np.radians(np.asarray(th, dtype=np.float64)))
    return np.stack([s * SHELL_A * np.cos(ph) * np.sin(t), CY + s * SHELL_B * np.sin(ph),
                     s * SHELL_A * np.cos(ph) * np.cos(t)], axis=-1)


def flared(P: np.ndarray, u) -> np.ndarray:
    """Points of a ring's plate pushed out radially by its flare: `u` 0 at the plate's lower edge, 1 at its upper."""
    s = 1.0 + FLARE * (1.0 - np.asarray(u, dtype=np.float64)) ** 2
    out = np.array(P, dtype=np.float64)
    out[..., 0] *= s
    out[..., 2] *= s
    return out


def az_dirs(th: float) -> tuple[np.ndarray, np.ndarray]:
    """Outward and tangent directions at azimuth th (degrees); a positive turn about the tangent tips up -> out."""
    t = math.radians(th)
    return np.array([math.sin(t), 0.0, math.cos(t)]), np.array([math.cos(t), 0.0, -math.sin(t)])


def axis_euler(axis, deg: float) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees, X then Y then Z about the rest axes (ck.euler), of a rotation by `deg` about `axis`."""
    k = np.asarray(axis, dtype=np.float64)
    k = k / np.linalg.norm(k)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return euler_of(np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * (K @ K))


def euler_of(R: np.ndarray) -> tuple[float, float, float]:
    ry = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    out = (math.degrees(rx), math.degrees(ry), math.degrees(rz))
    assert np.allclose(ck.euler(*out), R, atol=1e-9)
    return out




def orient(P: np.ndarray, T: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """Flips the triangles whose normal points against `ref` (one direction per triangle, or one for all)."""
    n = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    ref = np.broadcast_to(np.asarray(ref, dtype=np.float64), n.shape)
    bad = np.einsum("ij,ij->i", n, ref) < 0.0
    T = T.copy()
    T[bad] = T[bad][:, ::-1]
    return T


def brass(P: np.ndarray, seed: int, polish: float = 0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The frame: brass, mottled, with verdigris runs; bronze_patina and wet below the waterline.
    Returns (colour, wet, cavity)."""
    n = ck.fbm(P * 3.0, seed)
    col = PAL["brass"] * (0.86 + 0.14 * (n + 0.5) + 0.06 * polish)[:, None]
    runs = ck.smoothstep(0.12, 0.4, ck.fbm(P * np.array([4.0, 0.7, 4.0]), seed + 1)) * 0.45
    water = ck.smoothstep(WATER_Y + 0.35, WATER_Y - 0.05, P[:, 1] + 0.12 * n)
    pat = np.clip(runs + water, 0.0, 1.0)
    col = ck.mix(col, PAL["bronze_patina"] * (0.85 + 0.15 * (n + 0.5))[:, None], pat[:, None])
    wet = ck.smoothstep(WATER_Y + 0.08, WATER_Y - 0.08, P[:, 1] + 0.05 * n)
    return np.clip(col, 0.114, 0.92), wet, 0.25 * pat


def lacquer(P: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    n = ck.fbm(P * 5.0, seed)
    col = PAL["lacquer_black"] * (1.0 + 0.25 * (n + 0.5))[:, None]
    wet = ck.smoothstep(WATER_Y + 0.08, WATER_Y - 0.08, P[:, 1])
    return np.clip(col, 0.114, 1.0), np.maximum(wet, 0.35)


def frame(mesh: ck.Mesh, P, T, bones, seed: int, polish: float = 0.0, cav=0.0, flat: bool = False) -> None:
    col, wet, c = brass(P, seed, polish)
    ck.finish(mesh, P, T, "frame", col, bones, wet=np.maximum(wet, 0.15 * polish), cavity=c + cav, flat=flat)


def joint(mesh: ck.Mesh, centre, r: float, bones, seed: int, rings: int = 5, segs: int = 10) -> None:
    P, T = ck.ellipsoid(centre, (r, r, r), rings, segs)
    col, wet = lacquer(P, seed)
    ck.finish(mesh, P, T, "frame", col, bones, wet=wet, cavity=0.2)


def rod(mesh: ck.Mesh, a, b, r, bones, seed: int, segs: int = 8, n: int = 2, cap=True) -> None:
    path = np.linspace(np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64), n)
    P, T = ck.tube(path, r, segs, cap_start=cap, cap_end=cap)
    frame(mesh, P, T, bones, seed)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def tier_y(t: int) -> float:
    return CY + SHELL_B * math.sin(math.radians(0.5 * sum(TIERS[t])))


def hoop_r(t: int) -> float:
    return SHELL_A * math.cos(math.radians(0.5 * sum(TIERS[t]))) + HOOP_OUT


def petal_az(t: int, k: int) -> float:
    return TIER_AZ[t] + 90.0 * k


def pivot(t: int, k: int) -> np.ndarray:
    o, _ = az_dirs(petal_az(t, k))
    return o * (hoop_r(t) + LAMP_OUT) + UP * (tier_y(t) + LAMP_DY[t])


def leg_points(i: int) -> np.ndarray:
    o, _ = az_dirs(LEG_AZ[i])
    return np.array([o * r + UP * y for r, y in LEG])


def arm_points(side: int) -> np.ndarray:
    """side +1 the left arm (+x), -1 the right."""
    return np.array([(side * x, y, z) for x, y, z in ARM])


def scissor_frame(side: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(the head direction wrist -> tip, the blades' hinge normal, the pivot)."""
    a = arm_points(side)
    d = (a[3] - a[2]) / np.linalg.norm(a[3] - a[2])
    n = np.cross(d, np.array([side * 1.0, 0.0, 0.0]))
    n = n / np.linalg.norm(n)
    return d, n, a[2] + d * SCISSOR_PIVOT


SIDES = (("l", 1), ("r", -1))


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("body", BODY_PIVOT, (0, CY, 0), "root")
    rig.add("core", (0, CY, 0), (0, CY + 0.3, 0), "body")
    for t in range(3):
        rig.add(f"ring{t}", (0, tier_y(t), 0), (0, tier_y(t) + 0.2, 0), "body")
        for k in range(4):
            th = petal_az(t, k)
            rig.add(f"petal{t}_{k}", shell_pt(TIERS[t][0], th), shell_pt(TIERS[t][1], th), f"ring{t}")
            p = pivot(t, k)
            rig.add(f"lamp{t}_{k}", p, p + UP * 0.2, f"petal{t}_{k}")
    for i in range(4):  # the legs hang from root: the body leans about the hips without lifting a foot
        j = leg_points(i)
        rig.add(f"leg{i}_a", j[0], j[1], "root")
        rig.add(f"leg{i}_b", j[1], j[2], f"leg{i}_a")
        rig.add(f"leg{i}_c", j[2], j[2] + az_dirs(LEG_AZ[i])[0] * 0.15, f"leg{i}_b")  # the foot, kept level
    for s, side in SIDES:
        a = arm_points(side)
        rig.add(f"arm_{s}_a", a[0], a[1], "body")
        rig.add(f"arm_{s}_b", a[1], a[2], f"arm_{s}_a")
        rig.add(f"arm_{s}_c", a[2], a[3], f"arm_{s}_b")
        d, _, pv = scissor_frame(side)
        rig.add(f"blade_{s}", pv, a[3], f"arm_{s}_c")
    # VFX anchors (M4-CRB-003; unweighted, no vertex is skinned to them): the near gimbal hub of the middle ring (the
    # weak point, on its petal so it folds back with it), the core globe's centre, and the core's crack facing the
    # party (+z), where the opened burst comes from
    _, tan = az_dirs(petal_az(1, 0))
    w = pivot(1, 0) - HUB_OFF * tan
    rig.add("vfx_wound", w, w + 0.15 * az_dirs(petal_az(1, 0))[0], "petal1_0")
    rig.add("vfx_core", (0, CY, 0), (0, CY, 0.2), "core")
    c = np.array([0.0, CY + 0.12, CORE_R * 0.98])
    rig.add("vfx_phase", c, c + np.array([0.0, 0.0, 0.2]), "core")
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The bowl the legs hang from, the column, the bell hood and its finial (all on `body`)."""
    b = rig.rigid("body")
    P, T = ck.lathe(BOWL, 24)
    col, wet, cav = brass(P, SEED + 1)
    band = np.exp(-((P[:, 1] - 1.08) / 0.035) ** 2)  # the lacquered joint ring the hips sit in
    col = ck.mix(col, PAL["lacquer_black"] * 1.1, band[:, None] * 0.9)
    ck.finish(mesh, P, T, "frame", col, b, wet=np.maximum(wet, 0.4 * band), cavity=cav + 0.3 * band)
    lo, hi, r = COLUMN
    P, T = ck.tube(np.array([(0, lo, 0), (0, hi, 0)]), r, 8, cap_start=False, cap_end=False)
    frame(mesh, P, T, b, SEED + 2, polish=0.5)
    for y in (CY - CORE_R - 0.02, CY + CORE_R + 0.02):  # the collars the core turns in
        P, T = ck.lathe([(0.055, y + 0.05), (0.1, y + 0.02), (0.1, y - 0.02), (0.055, y - 0.05)], 12)
        col, wet = lacquer(P, SEED + 3)
        ck.finish(mesh, P, T, "frame", col, b, wet=wet, cavity=0.3)
    prof = []
    for k in range(len(HOOD) - 1):  # refine the bell so its bands have rows to live on
        (r0, y0), (r1, y1) = HOOD[k], HOOD[k + 1]
        steps = 2 if abs(r1 - r0) > 0.12 else 1
        for s in range(steps):
            prof.append((r0 + (r1 - r0) * s / steps, y0 + (y1 - y0) * s / steps))
    prof.append(HOOD[-1])
    P, T = ck.lathe(prof, 32)
    col, wet, cav = brass(P, SEED + 4, polish=0.4)
    under = np.repeat(np.arange(len(prof)) >= 9, 32)  # the bell's sooty underside
    rim = ck.smoothstep(2.9, 2.82, P[:, 1]) * (1.0 - under)
    crown = np.exp(-((P[:, 1] - 3.21) / 0.03) ** 2) * (1.0 - under)
    col = ck.mix(col, PAL["lacquer_black"] * 1.1, np.clip(rim + crown, 0.0, 0.9)[:, None])
    col = np.where(under[:, None], ck.mix(PAL["brass"] * 0.45, PAL["lacquer_black"], 0.5), col)
    ck.finish(mesh, P, T, "frame", col, b, wet=wet, cavity=np.where(under, 0.6, cav + 0.2 * rim))
    for s, side in SIDES:  # the shoulder brackets on the rim
        a = arm_points(side)
        rod(mesh, (side * 0.86, 2.9, 0.0), a[0], 0.045, b, SEED + 5)
    P, T = ck.lathe(FINIAL, 12)
    frame(mesh, P, T, b, SEED + 6, polish=0.8)


def petal(mesh: ck.Mesh, rig: ck.Rig, t: int, k: int) -> None:
    """One petal of a ring: a curved plate (outside, sooty inside, flat edges) and its quarter of the hoop."""
    th = petal_az(t, k)
    lo, hi = TIERS[t]
    half = 45.0 - 0.5 * PETAL_GAP
    rows, cols = 6, 10
    phis = np.linspace(hi, lo, rows)
    ths = np.linspace(th - half, th + half, cols)
    s_in = 1.0 - SHELL_T / SHELL_A
    up = ((phis - lo) / (hi - lo))[:, None]  # 0 at the plate's lower edge, 1 at its upper
    Po = flared(shell_pt(phis[:, None], ths[None, :]), up).reshape(-1, 3)
    Pi = flared(shell_pt(phis[:, None], ths[None, :], s_in), up).reshape(-1, 3)
    G = ck.grid_tris(rows, cols, False)
    centre = np.array([0.0, CY, 0.0])
    bone = rig.rigid(f"petal{t}_{k}")
    To = orient(Po, G, Po[G].mean(axis=1) - centre)
    u = np.repeat(np.linspace(0.0, 1.0, rows), cols)
    v = np.tile(np.linspace(0.0, 1.0, cols), rows)
    edge = np.minimum(np.minimum(u, 1.0 - u), np.minimum(v, 1.0 - v))
    col, wet, cav = brass(Po, SEED + 10 + 4 * t + k)
    rib = np.exp(-((v - 0.5) / 0.035) ** 2)  # a lacquered rib down the petal's middle
    lip = ck.smoothstep(0.78, 0.92, u)  # M4-CRB-003: the flared lower lip lacquered black, a dark line under each ring
    col = ck.mix(col, PAL["lacquer_black"] * 1.1, np.clip(0.8 * rib + 0.9 * lip, 0.0, 0.9)[:, None])
    ck.finish(mesh, Po, To, "frame", col, bone, wet=np.maximum(wet, 0.3 * lip),
              cavity=cav + 0.45 * ck.smoothstep(0.12, 0.0, edge) + 0.3 * rib)
    Ti = orient(Pi, G, centre - Pi[G].mean(axis=1))
    soot = ck.mix(PAL["brass"] * 0.5, PAL["lacquer_black"], 0.45 + 0.2 * ck.fbm(Pi * 4.0, SEED + 30)[:, None])
    ck.finish(mesh, Pi, Ti, "frame", np.clip(soot, 0.114, 1.0), bone, cavity=0.5)
    loop = ([(0, c) for c in range(cols)] + [(r, cols - 1) for r in range(1, rows)]
            + [(rows - 1, c) for c in range(cols - 2, -1, -1)] + [(r, 0) for r in range(rows - 2, 0, -1)])
    idx = np.array([r * cols + c for r, c in loop])
    Pe = np.vstack([Po[idx], Pi[idx]])
    Te = ck.grid_tris(2, len(idx), True)
    mid = shell_pt(0.5 * (lo + hi), th, 0.5 * (1.0 + s_in))
    Te = orient(Pe, Te, Pe[Te].mean(axis=1) - mid)
    col, wet, _ = brass(Pe, SEED + 31, polish=0.6)
    ck.finish(mesh, Pe, Te, "frame", col, bone, wet=wet, flat=True)
    # its quarter of the hoop, polished
    a = np.radians(np.linspace(th - half + 1.0, th + half - 1.0, 12))
    path = np.column_stack([hoop_r(t) * np.sin(a), np.full(len(a), tier_y(t)), hoop_r(t) * np.cos(a)])
    P, T = ck.tube(path, 0.032, 6)
    frame(mesh, P, T, bone, SEED + 32, polish=1.0)
    # the gimbal fork: two arms off the hoop out to the hubs either side of the lamp
    o, tan = az_dirs(th)
    pv = pivot(t, k)
    for sgn in (-1.0, 1.0):
        hub = pv + sgn * HUB_OFF * tan
        dth = math.degrees(math.asin(HUB_OFF / hoop_r(t)))
        a0 = math.radians(th + sgn * dth)
        root = np.array([hoop_r(t) * math.sin(a0), tier_y(t), hoop_r(t) * math.cos(a0)])
        rod(mesh, root, hub, 0.017, bone, SEED + 33, segs=6, cap=False)
        P, T = ck.ellipsoid(hub, (0.036, 0.036, 0.036), 4, 6)
        ck.finish(mesh, P, T, "hub", PAL["spawn_wound"] * 0.6, bone, wet=0.4, emission=1.0)


# A lamp in its own frame (the gimbal pivot at the origin, y up): (radius, y) profiles, top to bottom
LAMP_CUP = [(0.075, 0.0), (0.09, -0.025), (0.075, -0.08), (0.035, -0.105), (0.0, -0.11)]
LAMP_COLLAR = [(0.08, 0.02), (0.097, 0.0), (0.08, -0.02)]
LAMP_GLASS = [(0.045, 0.21), (0.055, 0.17), (0.085, 0.11), (0.096, 0.06), (0.09, 0.02), (0.075, 0.0)]
LAMP_CAP = [(0.0, 0.29), (0.025, 0.285), (0.05, 0.255), (0.064, 0.225), (0.055, 0.205), (0.04, 0.2)]


def lamp(mesh: ck.Mesh, rig: ck.Rig, t: int, k: int) -> None:
    """A salt-glass chimney lit from inside (glimmer_bound, steady), a brass fount and vented cap, a lacquered
    collar with the gimbal pins; sea_glow drips run down the glass."""
    rng = np.random.default_rng(SEED + 40 + 4 * t + k)
    th = petal_az(t, k)
    o, tan = az_dirs(th)
    R = np.column_stack([tan, UP, o])  # local x along the hub axis, z outward
    pv = pivot(t, k)
    bone = rig.rigid(f"lamp{t}_{k}")

    def place(P, s: float = LAMP_SCALE):
        return ck.transform(P, R, pv, s)

    P, T = ck.lathe(LAMP_CUP, 12)
    frame(mesh, place(P), T, bone, SEED + 41, polish=0.6)
    P, T = ck.lathe(LAMP_CAP, 12)
    frame(mesh, place(P), T, bone, SEED + 42, polish=0.6, cav=0.15)
    P, T = ck.lathe(LAMP_COLLAR, 12)
    Pw = place(P)
    col, wet = lacquer(Pw, SEED + 43)
    ck.finish(mesh, Pw, T, "frame", col, bone, wet=wet, cavity=0.2)
    for sgn in (-1.0, 1.0):  # the pins out to the hubs
        P, T = ck.tube(np.array([(sgn * 0.1, 0, 0), (sgn * (HUB_OFF - 0.02), 0, 0)]), 0.016, 6)
        Pw = place(P, 1.0)
        col, wet = lacquer(Pw, SEED + 44)
        ck.finish(mesh, Pw, T, "frame", col, bone, wet=wet)
    P, T = ck.lathe(LAMP_GLASS, 12)
    ang = np.arctan2(P[:, 0], P[:, 2])
    y = P[:, 1]
    glow = 0.3 + 0.65 * np.exp(-((y - 0.08) / 0.06) ** 2)  # the bound light at the wick's height
    drip = np.zeros(len(P))
    for _ in range(3):  # sea_glow runs down from the cap
        a0 = rng.uniform(-math.pi, math.pi)
        da = np.angle(np.exp(1j * (ang - a0)))
        drip = np.maximum(drip, np.exp(-(da / 0.22) ** 2) * ck.smoothstep(rng.uniform(0.0, 0.08), 0.2, y))
    col = ck.mix(PAL["salt_glass"], PAL["glimmer_bound"], (0.35 * glow)[:, None])
    col = ck.mix(col, PAL["sea_glow"] * 1.3, (0.7 * drip)[:, None])
    ck.finish(mesh, place(P), T, "glass", col, bone, wet=0.5 + 0.5 * drip, emission=glow * (1.0 - 0.6 * drip))


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Four short jointed legs: lacquered hip and knee balls, brass shanks, a three-clawed lamp-stand foot."""
    for i in range(4):
        j = leg_points(i)
        names = [f"leg{i}_a", f"leg{i}_b"]
        skin = rig.chain(names, j)
        joint(mesh, j[0], 0.1, rig.rigid(names[0]), SEED + 50 + i)
        joint(mesh, j[1], 0.095, skin, SEED + 54 + i)
        path = ck.bezier([j[0], 0.5 * (j[0] + j[1]) + UP * 0.03, j[1]], 6)
        P, T = ck.tube(path, np.linspace(0.085, 0.07, 6), 8, cap_start=False, cap_end=False)
        frame(mesh, P, T, skin, SEED + 58 + i)
        path = ck.bezier([j[1], j[1] + 0.45 * (j[2] - j[1]) + 0.04 * az_dirs(LEG_AZ[i])[0], j[2] + UP * 0.1], 9)
        P, T = ck.tube(path, np.array([0.072, 0.07, 0.066, 0.062, 0.058, 0.055, 0.052, 0.05, 0.048]), 8,
                       cap_start=False, cap_end=False)
        frame(mesh, P, T, skin, SEED + 62 + i)
        # M4-CRB-003: a lacquered greave collar a third of the way down the shank (the leg reads jointed, not a pole)
        g = path[3]
        dg = path[4] - path[2]
        P, T = ck.tube(np.array([g - 0.04 * dg / np.linalg.norm(dg), g + 0.04 * dg / np.linalg.norm(dg)]), 0.082, 8)
        col, wet = lacquer(P, SEED + 74 + i)
        ck.finish(mesh, P, T, "frame", col, skin, wet=wet, cavity=0.2)
        fb = rig.rigid(f"leg{i}_c")
        foot = j[2] - UP * j[2][1]  # on the ground
        P, T = ck.lathe([(0.0, 0.16), (0.045, 0.15), (0.06, 0.1), (0.1, 0.045), (0.11, 0.015), (0.1, 0.0),
                         (0.0, 0.0)], 10)
        frame(mesh, P + foot, T, fb, SEED + 66 + i)
        o, tan = az_dirs(LEG_AZ[i])
        for c in (-50.0, 0.0, 50.0):  # the claws
            d = math.cos(math.radians(c)) * o + math.sin(math.radians(c)) * tan
            path = ck.bezier([foot + UP * 0.05, foot + d * 0.12 + UP * 0.06, foot + d * 0.2 + UP * 0.012], 5)
            P, T = ck.tube(path, np.linspace(0.032, 0.012, 5), 6, cap_start=False)
            frame(mesh, P, T, fb, SEED + 70 + i)


def arms(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Two long trimming arms: a lacquered shoulder, a brass upper arm, a telescoping forearm, scissor blades."""
    for s, side in SIDES:
        a = arm_points(side)
        ua, fa, hb, bb = (rig.rigid(f"arm_{s}_a"), rig.rigid(f"arm_{s}_b"), rig.rigid(f"arm_{s}_c"),
                          rig.rigid(f"blade_{s}"))
        joint(mesh, a[0], 0.11, ua, SEED + 80)
        P, T = ck.tube(np.linspace(a[0], a[1], 4), np.array([0.075, 0.07, 0.064, 0.058]), 8, cap_start=False,
                       cap_end=False)
        frame(mesh, P, T, ua, SEED + 81)
        joint(mesh, a[1], 0.085, fa, SEED + 82)
        mid = a[1] + 0.55 * (a[2] - a[1])
        rod(mesh, a[1], mid, 0.06, fa, SEED + 83, cap=False)
        rod(mesh, mid - 0.04 * (a[2] - a[1]), a[2], 0.045, fa, SEED + 84, cap=False)
        P, T = ck.tube(np.linspace(mid - 0.03 * (a[2] - a[1]), mid + 0.02 * (a[2] - a[1]), 2), 0.072, 8)
        col, wet = lacquer(P, SEED + 85)
        ck.finish(mesh, P, T, "frame", col, fa, wet=wet)
        joint(mesh, a[2], 0.07, hb, SEED + 86)
        d, n, pv = scissor_frame(side)
        side_dir = np.cross(n, d)
        for sgn, bone in ((1.0, hb), (-1.0, bb)):  # two blades crossing at the pivot, a little open at rest
            ax = d * math.cos(math.radians(6.0)) + sgn * side_dir * math.sin(math.radians(6.0))
            tail = pv - 0.14 * ax
            tip = pv + BLADE_LEN * ax
            path = ck.bezier([tail, pv, pv + 0.45 * ax - sgn * 0.045 * side_dir, tip], 7)
            P, T = ck.tube(path, np.array([0.04, 0.058, 0.068, 0.062, 0.048, 0.028, 0.008]), 6, squash=0.3,
                           up_hint=tuple(side_dir))
            frame(mesh, P, T, bone, SEED + 87, polish=1.0)
        joint(mesh, pv, 0.045, hb, SEED + 88, rings=4, segs=8)


def core(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The core: one large cracked salt-glass globe round the brightest bound light."""
    P, T = ck.ellipsoid((0.0, CY, 0.0), (CORE_R, CORE_R, CORE_R), 16, 30)
    crack = ck.smoothstep(0.045, 0.0, np.abs(ck.fbm(P * 3.2, SEED + 90))) * ck.smoothstep(-0.2, 0.1, ck.fbm(P * 1.3, SEED + 91))
    col = ck.mix(PAL["salt_glass"], PAL["glimmer_bound"], 0.45)
    col = ck.mix(np.tile(col, (len(P), 1)), np.tile(PAL["lacquer_black"] * 1.2, (len(P), 1)), (0.85 * crack)[:, None])
    # M4-CRB-003: the light is brightest where the globe faces the party (+z) and falls toward its rim, so the bared core
    # reads as a lit glass globe from the battle camera, not a flat disc
    face = np.clip((P[:, 2]) / CORE_R, 0.0, 1.0)
    glow = 0.5 + 0.5 * face ** 0.7
    col = ck.mix(col * 0.8, col, glow[:, None])
    ck.finish(mesh, P, T, "core", col, rig.rigid("core"), wet=0.6, cavity=0.4 * crack + 0.2 * (1.0 - glow),
              emission=0.95 * glow * (1.0 - 0.8 * crack))


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("lamp_engine")
    body(mesh, rig)
    for t in range(3):
        for k in range(4):
            petal(mesh, rig, t, k)
            lamp(mesh, rig, t, k)
    legs(mesh, rig)
    arms(mesh, rig)
    core(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Poses and solves
# ---------------------------------------------------------------------------------------------
def opened_pose() -> dict:
    """The `opened` pose as {bone: (rot, loc)}: each ring's petals folded back about their lower edge, each lamp
    turned back the other way in its gimbal (level, or tipped out a little: LEVEL), the core lifted a little in its
    collars."""
    pose = {}
    for t in range(3):
        for k in range(4):
            _, tan = az_dirs(petal_az(t, k))
            pose[f"petal{t}_{k}"] = (np.array(axis_euler(tan, FOLD[t])), np.zeros(3))
            pose[f"lamp{t}_{k}"] = (np.array(axis_euler(tan, -LEVEL[t])), np.zeros(3))
    pose["core"] = (np.zeros(3), np.array([0.0, 0.05, 0.0]))
    return pose


def in_pose(base: ck.Clip, name: str, pose: dict) -> ck.Clip:
    """`base` played from `pose`: each key's rotation composed after the pose's (pose @ key, exact, unlike adding
    Euler angles), locations added; bones `base` leaves alone hold the pose."""
    out = ck.Clip(name, base.length, loop=base.loop)
    zero = (np.zeros(3), np.zeros(3))
    for b, ks in base.keys.items():
        pr, pl = pose.get(b, zero)
        Rp = ck.euler(*pr)
        for t, r, l in ks:
            out.key(b, t, euler_of(Rp @ ck.euler(*r)), tuple(np.asarray(l, float) + pl))
    for b, (pr, pl) in pose.items():
        if b not in base.keys:
            out.key(b, 0.0, tuple(pr), tuple(pl))
            out.key(b, base.length, tuple(pr), tuple(pl))
    return out


def solve_leg(i: int, drop: float, foot_y: float = 0.05) -> tuple[float, float, np.ndarray]:
    """(thigh, shin) degrees about the leg's tangent that keep the foot at foot_y with the hip lowered by `drop`,
    the knee lowered in step toward the water (the KO kneel): a coarse grid, then a fine one (deterministic). Also returns
    the foot's (radius, y)."""
    j = np.array([(r, y) for r, y in LEG])
    v1, v2 = j[1] - j[0], j[2] - j[1]

    def rot(v, deg):
        r = np.radians(deg)
        return np.column_stack([v[0] * np.cos(r) + v[1] * np.sin(r), -v[0] * np.sin(r) + v[1] * np.cos(r)])

    def search(ca: float, cb: float, span: float, step: float):
        g = np.arange(-span, span + step * 0.5, step)
        A, B = np.meshgrid(ca + g, cb + g, indexing="ij")
        A, B = A.ravel(), B.ravel()
        hip = j[0] + np.array([0.0, -drop])
        knee = hip + rot(v1, A)
        foot = knee + rot(v2, A + B)
        knee_y = j[1][1] - drop * (j[1][1] - 0.16) / KO_DROP  # the knee goes down to the water as the body settles
        cost = (foot[:, 1] - foot_y) ** 2 * 400.0 + (knee[:, 1] - knee_y) ** 2 * 40.0 + 1e-5 * (A ** 2 + B ** 2)
        cost = cost + 1000.0 * (knee[:, 1] < 0.12) + 1000.0 * (foot[:, 0] < knee[:, 0])
        k = int(np.argmin(cost))
        return float(A[k]), float(B[k]), foot[k]

    a, b, _ = search(0.0, 0.0, 80.0, 0.5)
    return search(a, b, 0.6, 0.02)


def leg_key(clip: ck.Clip, i: int, t: float, a: float, b: float, drop: float) -> None:
    _, tan = az_dirs(LEG_AZ[i])
    clip.key(f"leg{i}_a", t, axis_euler(tan, a), (0.0, -drop, 0.0))
    clip.key(f"leg{i}_b", t, axis_euler(tan, b))
    clip.key(f"leg{i}_c", t, axis_euler(tan, -(a + b)))  # the foot stays flat on the bottom




def elbow_hinge(side: int) -> np.ndarray:
    a = arm_points(side)
    h = np.cross(a[1] - a[0], a[2] - a[1])
    return h / np.linalg.norm(h)


def solve_arm(side: int, target, prefer=(0.0, 0.0, 0.0, 0.0)) -> tuple:
    """(rx, ry, rz, bend) that put the scissor tip at `target`: a coarse grid then a fine one round the best
    (deterministic), nearest `prefer` among equally good fits."""
    target = np.asarray(target, dtype=np.float64)
    a = arm_points(side)
    h = elbow_hinge(side)
    up_v, fore_v = a[1] - a[0], a[3] - a[1]

    def search(c, span, step):
        g = [np.arange(c[i] - span[i], c[i] + span[i] + 1e-9, step[i]) for i in range(4)]
        RX, RY, RZ, BB = (m.ravel() for m in np.meshgrid(*g, indexing="ij"))
        # vectorised Euler (X then Y then Z about fixed axes) and the elbow's hinge rotation
        def eul(rx, ry, rz):
            cx, sx, cy, sy, cz, sz = (np.cos(np.radians(rx)), np.sin(np.radians(rx)), np.cos(np.radians(ry)),
                                      np.sin(np.radians(ry)), np.cos(np.radians(rz)), np.sin(np.radians(rz)))
            R = np.empty((len(rx), 3, 3))
            R[:, 0, 0] = cz * cy
            R[:, 0, 1] = cz * sy * sx - sz * cx
            R[:, 0, 2] = cz * sy * cx + sz * sx
            R[:, 1, 0] = sz * cy
            R[:, 1, 1] = sz * sy * sx + cz * cx
            R[:, 1, 2] = sz * sy * cx - cz * sx
            R[:, 2, 0] = -sy
            R[:, 2, 1] = cy * sx
            R[:, 2, 2] = cy * cx
            return R
        Ru = eul(RX, RY, RZ)
        th = np.radians(BB)[:, None]
        v = fore_v[None, :]
        vf = v * np.cos(th) + np.cross(h, fore_v)[None, :] * np.sin(th) + h[None, :] * (h @ fore_v) * (1 - np.cos(th))
        tip = a[0] + np.einsum("nij,j->ni", Ru, up_v) + np.einsum("nij,nj->ni", Ru, vf)
        err = np.sum((tip - target) ** 2, axis=1)
        pr = np.asarray(prefer, dtype=np.float64)
        cost = err * 400.0 + 1e-5 * ((RX - pr[0]) ** 2 + (RY - pr[1]) ** 2 + (RZ - pr[2]) ** 2 + (BB - pr[3]) ** 2)
        k = int(np.argmin(cost))
        return np.array([RX[k], RY[k], RZ[k], BB[k]])

    best = search(np.asarray(prefer, dtype=np.float64), (90.0, 90.0, 60.0, 90.0), (6.0, 6.0, 6.0, 6.0))
    best = search(best, (6.0, 6.0, 6.0, 6.0), (1.0, 1.0, 1.0, 1.0))
    return tuple(float(v) for v in best)


def arm_key(clip: ck.Clip, s: str, side: int, t: float, sol: tuple, wrist=(0.0, 0.0, 0.0), blade: float = 0.0) -> None:
    rx, ry, rz, bend = sol
    clip.key(f"arm_{s}_a", t, (rx, ry, rz))
    clip.key(f"arm_{s}_b", t, axis_euler(elbow_hinge(side), bend))
    clip.key(f"arm_{s}_c", t, wrist)
    _, n, _ = scissor_frame(side)
    clip.key(f"blade_{s}", t, axis_euler(n, blade))


def lamp_swing(clip: ck.Clip, t_: int, k: int, t: float, deg: float, extra=(0.0, 0.0, 0.0), loc=(0.0, 0.0, 0.0)) -> None:
    """A lamp swung `deg` about its gimbal hubs (positive tips its top outward), then `extra` (rx, ry, rz)."""
    _, tan = az_dirs(petal_az(t_, k))
    R = ck.euler(*extra) @ ck.euler(*axis_euler(tan, deg))
    clip.key(f"lamp{t_}_{k}", t, euler_of(R), loc)


def face_target(t_: int, k: int, deg: float) -> tuple[float, tuple]:
    """A lamp turned toward the target (+z) through its gimbal: out about its hubs by the target's outward share
    (never inward, into its own hoop), and sideways about its outward axis by the target's sideways share."""
    th = petal_az(t_, k)
    o, tan = az_dirs(th)
    out_share = max(math.cos(math.radians(th)), 0.0)
    side = -math.sin(math.radians(th))  # the target's share along the lamp's tangent
    return deg * out_share, axis_euler(o, -deg * side)


def petal_fold(clip: ck.Clip, t_: int, k: int, t: float, deg: float) -> None:
    _, tan = az_dirs(petal_az(t_, k))
    clip.key(f"petal{t_}_{k}", t, axis_euler(tan, deg))


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
REST_SOL = (0.0, 0.0, 0.0, 0.0)


def build_clips() -> list[ck.Clip]:
    """M4-CRB-003: the move pass (docs/kb/plan/act2/bosses/lamp_engine.md, the move list). Every one-shot is authored
    from rest and played from its phase's idle first frame (`in_pose`), so it starts and ends exactly there."""
    pose = opened_pose()

    # idle: the rings turn slowly against each other, the lamps sway in their gimbals, the shears tick
    idle = ck.Clip("idle", 6.0, loop=True)
    for t_, amp in ((0, 14.0), (1, -16.0), (2, 12.0)):
        idle.wave(f"ring{t_}", amp_rot=(0.0, amp, 0.0), cycles=1)
    for t_ in range(3):
        for k in range(4):
            n = 12
            for s in range(n + 1):
                w = math.sin(2 * math.pi * s / n + 1.7 * (4 * t_ + k))
                lamp_swing(idle, t_, k, 6.0 * s / n, 3.0 * w)
    idle.wave("body", amp_loc=(0.0, 0.012, 0.0), cycles=2)
    idle.wave("core", amp_rot=(0.0, 8.0, 0.0), cycles=1)
    for s, side in SIDES:
        idle.wave(f"arm_{s}_a", amp_rot=(2.0, 0.0, side * 1.5), cycles=1, phase=0.0 if side > 0 else math.pi)
        t0 = 1.4 if side > 0 else 4.4
        for t, deg in ((0.0, 0.0), (t0, 0.0), (t0 + 0.18, 16.0), (t0 + 0.34, 0.0), (6.0, 0.0)):
            _, n, _ = scissor_frame(side)
            idle.key(f"blade_{s}", t, axis_euler(n, deg))
        for t, deg in ((0.0, 0.0), (t0 - 0.1, 0.0), (t0 + 0.18, -5.0), (t0 + 0.45, 0.0), (6.0, 0.0)):
            idle.key(f"arm_{s}_c", t, axis_euler(elbow_hinge(side), deg))

    # attack (the trim): the right arm winds up, its shears open; it reaches and snips at 0.6 s
    attack = ck.Clip("attack", 1.3)
    s, side = "r", -1
    a = arm_points(side)
    wind = solve_arm(side, a[3] + np.array([-0.15, 0.75, -0.35]), (-20.0, 0.0, 0.0, -30.0))
    reach = solve_arm(side, np.array([-0.8, 1.5, 1.65]), (40.0, 30.0, 0.0, 30.0))
    follow = solve_arm(side, np.array([-0.7, 1.35, 1.5]), reach)
    for t, sol, blade, wr in ((0.0, REST_SOL, 0.0, 0.0), (0.35, wind, 38.0, -15.0), (0.6, reach, -4.0, 10.0),
                              (0.85, follow, 0.0, 6.0), (1.3, REST_SOL, 0.0, 0.0)):
        arm_key(attack, s, side, t, sol, axis_euler(elbow_hinge(side), wr), blade)
    lw = solve_arm(1, arm_points(1)[3] + np.array([0.2, 0.25, -0.2]), (-10.0, 0.0, 0.0, -10.0))
    for t, sol in ((0.0, REST_SOL), (0.4, lw), (0.9, lw), (1.3, REST_SOL)):
        arm_key(attack, "l", 1, t, sol)
    for t, rx, ry in ((0.0, 0.0, 0.0), (0.35, -3.0, 6.0), (0.6, 5.0, -8.0), (0.85, 4.0, -6.0), (1.3, 0.0, 0.0)):
        attack.key("body", t, (rx, ry, 0.0))
    for t_ in range(3):
        for t, deg in ((0.0, 0.0), (0.6, (-1) ** t_ * 7.0), (1.3, 0.0)):
            attack.key(f"ring{t_}", t, (0.0, deg, 0.0))

    # cast (the gathering): the lamps swing one by one to face the target (+z) and lift; a held breath
    cast = ck.Clip("cast", 1.8)
    for t_ in range(3):
        for k in range(4):
            i = 4 * t_ + k
            t0 = 0.15 + 0.05 * i
            lamp_swing(cast, t_, k, 0.0, 0.0)
            lamp_swing(cast, t_, k, t0, 0.0)
            face = face_target(t_, k, 26.0)
            lamp_swing(cast, t_, k, min(t0 + 0.3, 1.0), face[0], face[1], (0.0, 0.03, 0.0))
            lamp_swing(cast, t_, k, 1.35, face[0], face[1], (0.0, 0.03, 0.0))
            lamp_swing(cast, t_, k, 1.8, 0.0)
        cast.key(f"ring{t_}", 0.0)
        cast.key(f"ring{t_}", 1.0, (0.0, (-1) ** t_ * 4.0, 0.0))
        cast.key(f"ring{t_}", 1.8)
    for sd, sg in SIDES:
        up = solve_arm(sg, arm_points(sg)[3] + np.array([sg * 0.35, 0.9, -0.25]), (-20.0, 0.0, sg * 10.0, -40.0))
        for t, sol, bl in ((0.0, REST_SOL, 0.0), (1.0, up, 30.0), (1.35, up, 30.0), (1.8, REST_SOL, 0.0)):
            arm_key(cast, sd, sg, t, sol, blade=bl)
    for t, rx, dy in ((0.0, 0.0, 0.0), (1.0, -3.0, 0.04), (1.35, -3.0, 0.04), (1.8, 0.0, 0.0)):
        cast.key("body", t, (rx, 0.0, 0.0), (0.0, dy, 0.0))

    def hit_clip(name: str, sgn: float, loose: tuple, amp: float) -> ck.Clip:
        """M3-CRE-617: the rings jolt and one lamp swings loose on its gimbal; the peak at 0.1 s."""
        c = ck.Clip(name, 0.7)
        for t, s_ in ((0.0, 0.0), (0.1, 1.0), (0.22, -0.45), (0.36, 0.2), (0.5, -0.07), (0.7, 0.0)):
            m = s_ * amp
            # M4-CRB-003: big enough to read at 12 m (the frame rocks back about its hips, the arms fly up)
            c.key("body", t, (-7.0 * m, 0.0, 3.0 * m * sgn), (0.0, -0.02 * m, 0.0))
            for t_, d in ((0, 13.0), (1, -16.0), (2, 12.0)):
                c.key(f"ring{t_}", t, (0.0, d * m * sgn, 0.0))
            for sd, sg in SIDES:
                c.key(f"arm_{sd}_a", t, (-12.0 * m, 0.0, sg * 6.0 * m))
            for t_ in range(3):
                for k in range(4):
                    if (t_, k) != loose:
                        lamp_swing(c, t_, k, t, ((-1) ** (t_ + k)) * 6.0 * m)
        for t, deg in ((0.0, 0.0), (0.1, 36.0), (0.25, -12.0), (0.4, 10.0), (0.55, -4.0), (0.7, 0.0)):
            lamp_swing(c, loose[0], loose[1], t, deg * amp)
        return c

    hit = hit_clip("hit", 1.0, (1, 3), 1.0)
    hit_b = hit_clip("hit_b", -1.0, (0, 1), 1.25)

    # ko: the core goes dark (VFX: the dead it held rise as glimmer_lift at vfx_core), the rings sag, the lamps hang, the
    # arms drop into the water and the frame settles on its knees. Authored from rest: `ko_opened` plays it from the open
    # idle (where a KO lands by design), `ko` from the closed one
    ko = ck.Clip("ko", 3.0)
    ko_shut = ck.Clip("ko", 3.0)  # closed, the petals stay shut (sagging them open shows the core through the gaps)
    for t, drop, rx in ((0.0, 0.0, 0.0), (0.3, -0.02, -3.0), (0.9, 0.08, 0.0), (1.8, 0.42, 2.0), (2.4, KO_DROP, 3.0),
                        (2.7, KO_DROP - 0.02, 2.5), (3.0, KO_DROP, 3.0)):
        ko.key("body", t, (rx, 0.0, 0.0), (0.0, -drop, 0.0))
    legs_follow(ko)
    for t_ in range(3):
        sag = 0.5 if t_ == 0 else 1.0  # the bottom ring has least room to sag (the bowl is under it)
        for k in range(4):
            for t, extra, swing in ((0.0, 0.0, 0.0), (0.8, 4.0, 8.0), (1.6, 8.0, -6.0), (2.4, 12.0, 3.0),
                                    (3.0, 12.0, 3.0)):
                petal_fold(ko, t_, k, t, extra * sag)
                lamp_swing(ko, t_, k, t, swing * (-1) ** k)  # tipping out as the petals sag
                lamp_swing(ko_shut, t_, k, t, swing * (-1) ** k)
        ko.key(f"ring{t_}", 0.0)
        ko.key(f"ring{t_}", 1.2, (0.0, (-1) ** t_ * 5.0, 0.0))
        ko.key(f"ring{t_}", 3.0, (0.0, (-1) ** t_ * 5.0, 0.0))
    ko.key("core", 0.0)
    ko.key("core", 1.5, (0.0, 10.0, 0.0), (0.0, -0.03, 0.0))
    ko.key("core", 3.0, (0.0, 12.0, 0.0), (0.0, -0.05, 0.0))
    for sd, sg in SIDES:
        a = arm_points(sg)
        limp = solve_arm(sg, np.array([sg * 1.55, 0.2 + KO_DROP, 1.25]), (25.0, 0.0, 0.0, 40.0))  # in the water
        sag = solve_arm(sg, a[3] + np.array([sg * 0.1, -0.45, 0.15]), (10.0, 0.0, 0.0, 20.0))
        for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.6, sag, 10.0), (2.0, limp, 22.0), (3.0, limp, 22.0)):
            arm_key(ko, sd, sg, t, sol, blade=bl)

    for bone, ks in ko.keys.items():
        if not bone.startswith("petal") and not bone.startswith("lamp"):
            ko_shut.keys[bone] = list(ks)

    # phase_change (`opened`, 2.0 s, the burst at 1.1 s from vfx_phase): the rings jolt and stop; the middle ring folds
    # back first, then the top and the bottom, each lamp swinging back a beat behind in its gimbal; the core lifts in its
    # collars; the arms spread. Keyed absolutely, then pinned to the closed idle's first frame and the open idle's.
    phase = ck.Clip("phase_change", 2.0)
    for t_, (t0, t1) in ((1, (0.25, 1.05)), (2, (0.55, 1.35)), (0, (0.75, 1.5))):
        for t, d in ((0.0, 0.0), (0.12, 6.0), (0.24, -4.0), (0.36, 0.0), (2.0, 0.0)):
            phase.key(f"ring{t_}", t, (0.0, d * (-1) ** t_, 0.0))
        for k in range(4):
            f = FOLD[t_]
            for t, deg in ((0.0, 0.0), (t0, 0.0), (t1, f * 1.07), (t1 + 0.3, f * 0.98), (2.0, f)):
                petal_fold(phase, t_, k, t, deg)
            lv = LEVEL[t_]
            for t, deg in ((0.0, 0.0), (t0 + 0.08, 0.0), (t1 + 0.1, -lv * 0.85), (t1 + 0.35, -lv * 1.08), (2.0, -lv)):
                lamp_swing(phase, t_, k, min(t, 2.0), deg)
    phase.key("core", 0.0)
    phase.key("core", 0.9, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    phase.key("core", 1.5, (0.0, 20.0, 0.0), (0.0, 0.07, 0.0))
    phase.key("core", 2.0, (0.0, 0.0, 0.0), (0.0, 0.05, 0.0))
    for t, rx, dy in ((0.0, 0.0, 0.0), (0.15, -3.0, 0.0), (0.4, 2.0, -0.03), (1.2, -2.0, 0.03), (2.0, 0.0, 0.0)):
        phase.key("body", t, (rx, 0.0, 0.0), (0.0, dy, 0.0))
    for sd, sg in SIDES:
        spread = solve_arm(sg, arm_points(sg)[3] + np.array([sg * 0.5, 0.55, -0.3]), (-15.0, 0.0, sg * 15.0, -30.0))
        for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.7, spread, 34.0), (1.4, spread, 34.0), (2.0, REST_SOL, 0.0)):
            arm_key(phase, sd, sg, t, sol, blade=bl)

    # idle_opened: open, the rings turn a little, the petals breathe, the core turns slowly in its collars
    opened = ck.Clip("idle_opened", 5.0, loop=True)
    for t_, amp in ((0, 5.0), (1, -6.0), (2, 4.0)):
        opened.wave(f"ring{t_}", amp_rot=(0.0, amp, 0.0), cycles=1)
    for t_ in range(3):
        for k in range(4):
            n = 10
            for s_ in range(n + 1):
                w = math.sin(2 * math.pi * s_ / n + 1.3 * (4 * t_ + k))
                petal_fold(opened, t_, k, 5.0 * s_ / n, 2.5 * w)
                lamp_swing(opened, t_, k, 5.0 * s_ / n, -2.5 * w + 3.0 * math.sin(2 * math.pi * s_ / n + 2.0 * k))
    opened.wave("core", amp_rot=(0.0, 14.0, 0.0), amp_loc=(0.0, 0.015, 0.0), cycles=1)
    opened.wave("body", amp_loc=(0.0, 0.012, 0.0), cycles=2)
    for sd, sg in SIDES:
        opened.wave(f"arm_{sd}_a", amp_rot=(2.5, 0.0, sg * 2.0), cycles=1, phase=0.0 if sg > 0 else math.pi)
    opened = in_pose(opened, "idle_opened", pose)

    # Each phase's idle first frame: every clip of the phase starts and ends there
    idle0 = {b: tuple(np.asarray(v, float) for v in idle.sample(b, 0.0)) for b in idle.keys}
    open0 = {b: tuple(np.asarray(v, float) for v in opened.sample(b, 0.0)) for b in opened.keys}

    def closed(c: ck.Clip, name: str | None = None) -> ck.Clip:
        return in_pose(c, name or c.name, idle0)

    def open_(c: ck.Clip, name: str | None = None) -> ck.Clip:
        return in_pose(c, name or f"{c.name}_opened", open0)

    # intro (2.8 s, under the boss_tall hold): dormant, slumped low on bent knees, its arms folded down and its lamps
    # hanging; the rings wake bottom to top (each jolts, then turns home) and their lamps swing up level as they wake
    # (the lighting itself is VFX: emission is static); the frame rises, the arms lift high with the shears open, and it
    # settles into idle
    intro = ck.Clip("intro", 2.8)
    for t, drop, rx in ((0.0, DORMANT_DROP, 5.0), (0.5, DORMANT_DROP, 5.0), (1.0, DORMANT_DROP * 0.85, 3.5),
                        (1.75, 0.03, -3.0), (2.2, 0.0, -1.5), (2.8, 0.0, 0.0)):
        intro.key("body", t, (rx, 0.0, 0.0), (0.0, -drop, 0.0))
    legs_follow(intro)
    for t_ in range(3):
        w = 0.45 + 0.35 * t_  # bottom to top
        off = (-1) ** t_ * 28.0
        for t, d in ((0.0, off), (w, off), (w + 0.1, off + (-1) ** t_ * 5.0), (w + 0.25, off), (2.45, 0.0), (2.8, 0.0)):
            intro.key(f"ring{t_}", t, (0.0, d, 0.0))
        for k in range(4):
            wk = w + 0.05 * k
            for t, deg in ((0.0, 14.0), (wk, 14.0), (wk + 0.22, -7.0), (wk + 0.45, 2.0), (wk + 0.6, 0.0), (2.8, 0.0)):
                lamp_swing(intro, t_, k, t, deg)
    for sd, sg in SIDES:
        a = arm_points(sg)
        fold = solve_arm(sg, np.array([sg * 1.25, 1.25, 0.8]), (20.0, 0.0, 0.0, 30.0))
        high = solve_arm(sg, a[3] + np.array([sg * 0.4, 0.9, -0.2]), (-20.0, 0.0, sg * 10.0, -40.0))
        for t, sol, bl in ((0.0, fold, 0.0), (0.9, fold, 0.0), (2.0, high, 36.0), (2.2, high, 30.0),
                           (2.8, REST_SOL, 0.0)):
            arm_key(intro, sd, sg, t, sol, blade=bl)
    intro.key("core", 0.0, (0.0, -20.0, 0.0))
    intro.key("core", 1.6, (0.0, -6.0, 0.0))
    intro.key("core", 2.8)

    # idle_b (1.4 s, the fidget): the near arm lifts and trims the air twice; the middle ring turns a little
    idle_b = ck.Clip("idle_b", 1.4)
    lift = solve_arm(-1, arm_points(-1)[3] + np.array([-0.15, 0.45, 0.15]), (-10.0, 0.0, 0.0, -20.0))
    for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.35, lift, 28.0), (0.5, lift, -2.0), (0.65, lift, 26.0),
                       (0.8, lift, -2.0), (1.4, REST_SOL, 0.0)):
        arm_key(idle_b, "r", -1, t, sol, blade=bl)
    idle_b.key("ring1", 0.0)
    idle_b.key("ring1", 0.7, (0.0, -8.0, 0.0))
    idle_b.key("ring1", 1.4)
    idle_b.key("body", 0.0)
    idle_b.key("body", 0.5, (0.0, -3.0, 0.0))
    idle_b.key("body", 1.4)

    # ready (1.6 s loop, the guard stance): it leans in, the near ring turns its lamps toward the party and every lamp
    # tips at them, the shears raised and a little open
    ready = ck.Clip("ready", 1.6, loop=True)
    ready.wave("body", amp_rot=(0.8, 0.0, 0.0), amp_loc=(0.0, 0.008, 0.0), cycles=1, base_rot=(3.0, 0.0, 0.0))
    for t_ in range(3):
        ready.key(f"ring{t_}", 0.0, (0.0, -10.0 if t_ == 1 else 0.0, 0.0))
        ready.key(f"ring{t_}", 1.6, (0.0, -10.0 if t_ == 1 else 0.0, 0.0))
        for k in range(4):
            for t, deg in ((0.0, 14.0), (0.8, 18.0), (1.6, 14.0)):
                face = face_target(t_, k, deg)
                lamp_swing(ready, t_, k, t, face[0], face[1])
    for sd, sg in SIDES:
        guard = solve_arm(sg, arm_points(sg)[3] + np.array([sg * 0.1, 0.35, 0.2]), (-10.0, 0.0, 0.0, -15.0))
        for t, bl in ((0.0, 18.0), (0.8, 24.0), (1.6, 18.0)):
            arm_key(ready, sd, sg, t, guard, blade=bl)

    # lamp_gather (1.8 s, the charge; the mark at 1.2 s): ring by ring, bottom to top, every lamp swings to the marked
    # hero (an overshoot, then still); the rings lock, the arms rise wide with the shears open and the frame leans back:
    # a held breath (the brightening is a VFX glow card on each lamp)
    gather = ck.Clip("lamp_gather", 1.8)
    for t_ in range(3):
        w = 0.1 + 0.22 * t_
        for k in range(4):
            face = face_target(t_, k, 34.0)
            over = face_target(t_, k, 40.0)
            wk = w + 0.04 * k
            lamp_swing(gather, t_, k, 0.0, 0.0)
            lamp_swing(gather, t_, k, wk, 0.0)
            lamp_swing(gather, t_, k, wk + 0.28, over[0], over[1])
            lamp_swing(gather, t_, k, wk + 0.45, face[0], face[1])
            lamp_swing(gather, t_, k, 1.45, face[0], face[1])
            lamp_swing(gather, t_, k, 1.8, 0.0)
        for t, d in ((0.0, 0.0), (w, 0.0), (w + 0.3, (-1) ** t_ * 6.0), (1.45, (-1) ** t_ * 6.0), (1.8, 0.0)):
            gather.key(f"ring{t_}", t, (0.0, d, 0.0))
    for sd, sg in SIDES:
        up = solve_arm(sg, arm_points(sg)[3] + np.array([sg * 0.45, 1.0, -0.3]), (-20.0, 0.0, sg * 10.0, -40.0))
        for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.9, up, 36.0), (1.45, up, 36.0), (1.8, REST_SOL, 0.0)):
            arm_key(gather, sd, sg, t, sol, blade=bl)
    for t, rx in ((0.0, 0.0), (0.9, -4.0), (1.2, -5.0), (1.45, -5.0), (1.8, 0.0)):
        gather.key("body", t, (rx, 0.0, 0.0))

    # lamp_burn (1.6 s, contact 0.8): the lamps swing onto the marked hero and the rings lock still (0.0-0.35), the frame
    # draws back with the arms pulled wide (the wind-up, held to 0.7); then the lamps fire together, the frame pitching
    # in as they snap fully on, and hold the steady beam (no flicker) to 1.1
    burn = ck.Clip("lamp_burn", 1.6)
    for t_ in range(3):
        for k in range(4):
            face = face_target(t_, k, 30.0)
            full = face_target(t_, k, 38.0)
            for t, (deg, ex) in ((0.0, (0.0, (0.0, 0.0, 0.0))), (0.35, face), (0.7, face), (0.8, full), (1.1, full),
                                 (1.6, (0.0, (0.0, 0.0, 0.0)))):
                lamp_swing(burn, t_, k, t, deg, ex)
        for t, d in ((0.0, 0.0), (0.3, (-1) ** t_ * 3.0), (1.1, (-1) ** t_ * 3.0), (1.6, 0.0)):
            burn.key(f"ring{t_}", t, (0.0, d, 0.0))
    for t, rx in ((0.0, 0.0), (0.35, -5.0), (0.7, -6.0), (0.8, 4.0), (0.9, 2.5), (1.1, 2.0), (1.6, 0.0)):
        burn.key("body", t, (rx, 0.0, 0.0))
    for sd, sg in SIDES:
        a = arm_points(sg)
        back = solve_arm(sg, a[3] + np.array([sg * 0.35, 0.3, -0.45]), (-15.0, 0.0, sg * 10.0, -20.0))
        fling = solve_arm(sg, a[3] + np.array([sg * 0.2, 0.15, 0.15]), back)
        for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.4, back, 0.0), (0.7, back, 0.0), (0.85, fling, 30.0),
                           (1.1, fling, 30.0), (1.6, REST_SOL, 0.0)):
            arm_key(burn, sd, sg, t, sol, blade=bl)

    # call (call_the_tenders, 1.4 s, contact 0.7): the near arm swings up high and back with its shears shut, then
    # knocks the flat of the shears against the bowl of its own frame: a ringing knock that wakes the crawlers. The
    # frame and the rings jolt with it; the far arm braces out.
    call = ck.Clip("call", 1.4)
    a = arm_points(-1)
    wind = solve_arm(-1, a[3] + np.array([0.0, 1.1, -0.45]), (-30.0, 0.0, 0.0, -40.0))
    wind2 = solve_arm(-1, a[3] + np.array([0.05, 1.2, -0.55]), wind)
    knock = solve_arm(-1, np.array([-0.98, 1.3, 0.4]), (20.0, 0.0, 0.0, 30.0))
    rebound = solve_arm(-1, np.array([-1.08, 1.42, 0.48]), knock)
    for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.45, wind, -3.0), (0.58, wind2, -3.0), (0.7, knock, -3.0),
                       (0.82, rebound, 0.0), (1.4, REST_SOL, 0.0)):
        arm_key(call, "r", -1, t, sol, blade=bl)
    brace = solve_arm(1, arm_points(1)[3] + np.array([0.3, 0.2, -0.1]), (-10.0, 0.0, 10.0, -10.0))
    for t, sol in ((0.0, REST_SOL), (0.5, brace), (1.0, brace), (1.4, REST_SOL)):
        arm_key(call, "l", 1, t, sol)
    for t, m in ((0.0, 0.0), (0.45, -0.3), (0.7, 1.0), (0.82, -0.5), (0.95, 0.25), (1.1, -0.1), (1.4, 0.0)):
        call.key("body", t, (-2.0 * m, 0.0, -3.0 * m))
        for t_, d in ((0, 5.0), (1, -6.0), (2, 4.0)):
            call.key(f"ring{t_}", t, (0.0, d * max(m, -0.5), 0.0))

    # twin_trim (phase 2, 1.7 s, contact 0.85): both arms cross high over the hood with the shears wide open (the
    # wind-up, 0.0-0.7), then both snip down and out, each at its own foe
    twin = ck.Clip("twin_trim", 1.7)
    for sd, sg in SIDES:
        high = solve_arm(sg, np.array([-sg * 0.15, 3.55, 0.7 + 0.15 * sg]), (-30.0, 0.0, sg * 15.0, -40.0))
        high2 = solve_arm(sg, np.array([-sg * 0.2, 3.62, 0.62 + 0.15 * sg]), high)
        cut = solve_arm(sg, np.array([sg * 1.15, 1.45, 1.6]), (40.0, 0.0, 0.0, 30.0))
        follow = solve_arm(sg, np.array([sg * 1.25, 1.32, 1.45]), cut)
        for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.55, high, 40.0), (0.7, high2, 44.0), (0.85, cut, -4.0),
                           (1.05, follow, 0.0), (1.7, REST_SOL, 0.0)):
            arm_key(twin, sd, sg, t, sol, blade=bl)
    for t, rx in ((0.0, 0.0), (0.6, -4.0), (0.72, -4.5), (0.85, 6.0), (1.05, 4.5), (1.7, 0.0)):
        twin.key("body", t, (rx, 0.0, 0.0))
    for t_ in range(3):
        for t, d in ((0.0, 0.0), (0.7, 0.0), (0.85, (-1) ** t_ * 7.0), (1.0, -(-1) ** t_ * 3.0), (1.7, 0.0)):
            twin.key(f"ring{t_}", t, (0.0, d, 0.0))

    # core_flare (phase 2, the open `cast_opened`, 2.0 s, contact 1.0): the petals spread wider and the frame leans
    # back with its arms flung wide (the wind-up, 0.0-0.9), then the core leans out in its collars and flares, the frame
    # pitching in after it; a pale shock across the dais is the VFX
    flare = ck.Clip("cast", 2.0)
    for t_, extra in ((0, 6.0), (1, 8.0), (2, 10.0)):
        for k in range(4):
            for t, deg in ((0.0, 0.0), (0.9, extra), (1.0, extra * 1.2), (1.4, extra), (2.0, 0.0)):
                petal_fold(flare, t_, k, t, deg)
        for t, d in ((0.0, 0.0), (0.9, 0.0), (1.0, (-1) ** t_ * 6.0), (1.15, -(-1) ** t_ * 3.0), (1.4, 0.0), (2.0, 0.0)):
            flare.key(f"ring{t_}", t, (0.0, d, 0.0))
    for t, loc in ((0.0, 0.0), (0.9, 0.04), (1.0, 0.1), (1.4, 0.1), (2.0, 0.0)):
        flare.key("core", t, (0.0, 0.0, 0.0), (0.0, 0.4 * loc, loc))
    for t, rx in ((0.0, 0.0), (0.8, -5.0), (0.9, -5.5), (1.0, 5.0), (1.4, 3.0), (2.0, 0.0)):
        flare.key("body", t, (rx, 0.0, 0.0))
    for sd, sg in SIDES:
        spread = solve_arm(sg, arm_points(sg)[3] + np.array([sg * 0.55, 0.5, -0.45]), (-15.0, 0.0, sg * 15.0, -30.0))
        for t, sol, bl in ((0.0, REST_SOL, 0.0), (0.8, spread, 34.0), (1.4, spread, 34.0), (2.0, REST_SOL, 0.0)):
            arm_key(flare, sd, sg, t, sol, blade=bl)

    phase = pin_ends(phase, idle0, open0)
    return [idle, opened, closed(intro), closed(idle_b), closed(ready), open_(ready),
            closed(attack), open_(attack), closed(cast), open_(flare),
            closed(gather), open_(gather), closed(burn), open_(burn), closed(call), open_(call),
            closed(twin), open_(twin), closed(hit), closed(hit_b), open_(hit), open_(hit_b),
            closed(ko_shut), open_(ko), phase]


def legs_follow(clip: ck.Clip, step: float = 0.1) -> None:
    """Keys the legs every `step` s to the body's drop (its y offset), so the feet stay planted on the bottom while the
    hips go down and up between the body's keys."""
    n = int(round(clip.length / step))
    for f in range(n + 1):
        t = min(step * f, clip.length)
        drop = -float(clip.sample("body", t)[1][1])
        for i in range(4):
            a_, b_, _ = solve_leg(i, drop) if abs(drop) > 1e-9 else (0.0, 0.0, None)
            leg_key(clip, i, t, a_, b_, drop)


def pin_ends(clip: ck.Clip, start: dict, end: dict) -> ck.Clip:
    """`clip` with every bone's first key set to `start`'s pose and its last to `end`'s (a phase change from one
    phase's idle first frame to the next one's); its inner keys are kept."""
    zero = (np.zeros(3), np.zeros(3))
    for b in sorted(set(clip.keys) | set(start) | set(end)):
        clip.keys[b] = [k for k in clip.keys.get(b, []) if 1e-6 < k[0] < clip.length - 1e-6]
        for t, (r, l) in ((0.0, start.get(b, zero)), (clip.length, end.get(b, zero))):
            clip.key(b, t, tuple(r), tuple(l))
    return clip


# ---------------------------------------------------------------------------------------------
# A numpy forward-kinematics check (no Blender)
# ---------------------------------------------------------------------------------------------
def fk(rig: ck.Rig, clip: ck.Clip, t: float) -> dict:
    """Each bone's pose as (R, offset) in rest space: p -> R p + offset (the export's convention)."""
    out: dict = {}
    for b in rig.bones:
        rdeg, loc = clip.sample(b.name, t)
        W = ck.euler(*rdeg)
        h = np.asarray(b.head)
        tl = h + loc - W @ h
        if b.parent:
            Rp, tp = out[b.parent]
            out[b.name] = (Rp @ W, Rp @ tl + tp)
        else:
            out[b.name] = (W, tl)
    return out


def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    a = mesh.arrays()
    for c in clips:
        for t in (0.0, c.length * 0.5, c.length):
            pose = fk(rig, c, t)
            J, W, P = a["joints"], a["weights"], a["pos"]
            out = np.zeros_like(P)
            for k in range(2):
                R = np.array([pose[rig.bones[j].name][0] for j in range(len(rig.bones))])
                o = np.array([pose[rig.bones[j].name][1] for j in range(len(rig.bones))])
                out += W[:, k:k + 1] * (np.einsum("nij,nj->ni", R[J[:, k]], P) + o[J[:, k]])
            print(f"{c.name:14s} @ {t:4.2f}s  y {out[:, 1].min():6.3f}..{out[:, 1].max():5.3f}  "
                  f"x {out[:, 0].min():6.2f}..{out[:, 0].max():5.2f}  z {out[:, 2].min():6.2f}..{out[:, 2].max():5.2f}")


# Kept off the floor (M3-CRE-632, common/grounding.py): as the KO settles the frame on its knees with a 3° pitch, a
# foot that the pitch would press into the bottom (by up to 6.5 mm) lifts the least it takes.
GROUNDED_LIMBS = [(f"leg{i}_c", gr.LIFT, 1.0, 0.05, ("ko", "ko_opened", "intro")) for i in range(4)]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and pose bounds; no export")
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    clips = build_clips()
    if args.report or not args.out:
        report(rig, mesh, clips)
        return
    info = ck.export_creature(mesh, rig, gr.grounded(rig, mesh, clips, GROUNDED_LIMBS), args.out,
                              extras={"hymn_creature": "lamp_engine"})
    print(f"lamp_engine: {info}")


if __name__ == "__main__":
    main()
