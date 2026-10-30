"""The Drownbell, boss of the vertical slice (M2-CRE-08; final pass M3-CRB-003): docs/kb/art/creatures/drownbell.md.

blender --background --factory-startup --python assets_src/creatures/drownbell/build_drownbell.py -- \
    --out assets/creatures/drownbell/drownbell.glb

The Shell Shrine's lost bronze bell, kept by the Undertow: a 2.4 m bell whose rim lip sits at the VFX `rim` anchor
(0.29 m), and under it a black wet mass that walks it on six jointed legs.

The bell is cast work, worn and doomed: double beads at the sound bow and the shoulder, a band of raised inscription
(an invented script, no real one) between two beads, a frieze of running waves under twelve cast fan-shells, the
shrine's sigil (a fan-shell rising out of the swell) in a roundel on the face, a petalled strike seat on the waist worn
bright where the shrine's beam struck it, an old mend (a riveted plate over a closed crack), dents, pitting, verdigris
bloom over brown run-streaks, a tide line and weed low down. Its crown is a cast plate carrying four canons (one
snapped) round a central hanging loop with a stub of broken chain; the rotten bell-rope is knotted to a canon and runs
down the left shoulder to trail on the ground, frayed at the end and weed-hung.

The wounds (ADR 0151) are open seams: torn bronze lips peeled outward, dark walls and the `spawn_wound` light along the
floor. They branch upward from the rim, so the weak point stays the rim: its cracks are the widest and brightest, the
biggest at azimuth 8 degrees (facing the battle and boss-intro cameras, which see the model from about -20 degrees,
and the review stage, +35), with a chip out of the lip under it. The rim is its
own mesh (`Rim`), with a broken variant (`RimBroken`, 105 degrees of the lip round the biggest crack gone, raw bronze at
the fractures, its light out) for `charge_broken`.

The mass under the bell: a wet black body with folds, plated where the legs leave it, a puckered maw glowing at its
underside (`vfx_phase`, where the flood pours). Each leg is jointed carapace: a femur of two telescoping plates that
dips under the lip and rises to a spurred knee, a joint membrane, a tibia with spines, and a hooked tarsus gripping the
ground; barnacle-crusted where it leaves the mouth.
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

SEED = 9311
PAL = {k: ck.hexrgb(v) for k, v in {
    "bronze_patina": "#5F8A78", "brass": "#B08D57", "coral_stone_weathered": "#B9AE98", "lacquer_black": "#1D1916",
    "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "timber_weathered": "#7E6A55", "foliage_shadow": "#1E4A3A",
    "deep_teal_shadow": "#0E4A55", "sand_wet": "#B59D74", "salt_glass": "#BFE6E0", "tortoiseshell": "#6B3A1E",
    "laterite": "#A8573A", "storm_slate": "#3E4A57", "bone": "#E6DAC0", "volcanic_stone": "#3A3A3F",
    "saltgrass": "#B9B26A", "thatch": "#B08A52",
}.items()}

LIP_Y = 0.29  # the rim's lowest edge: the VFX `rim` anchor (0.12 x 2.4 m)
RIM_TOP = 0.50  # where the rim band meets the bell body
RIM_R = 0.85
ROPE_AZ = -95.0  # the rope's azimuth (degrees; 0 = +Z, the face): down the left flank, framing the silhouette
WET_LINE = 0.75
D = math.radians
# The battle and boss-intro cameras see the model from about azimuth -20 degrees, the review stage from +35, and the
# party stands at +90: the biggest wound (the weak point) faces between them
BIG_AZ = D(8.0)
BREAK_ARC = (D(-44.0), D(61.0))  # azimuth span of the lip lost in RimBroken: round the biggest crack
SLOT0 = D(5.0)  # the frieze's first slot (the sigil's)
SIGIL_Y, SIGIL_R = 1.725, 0.135
SEAT_AZ, SEAT_Y, SEAT_R = D(-42.0), 0.87, 0.1  # the strike seat
PATCH_AZ, PATCH_Y = D(50.0), 0.95  # the old mend
BEADS = (0.60, 0.645, 1.02, 1.17, 1.355, 1.505, 1.95, 1.985)
# dents: azimuth (degrees), height, radius, depth
DENTS = ((-22.0, 0.73, 0.09, 0.018), (74.0, 1.06, 0.07, 0.015), (-62.0, 1.0, 0.1, 0.016), (122.0, 0.8, 0.08, 0.018),
         (160.0, 1.72, 0.08, 0.012), (-120.0, 1.3, 0.07, 0.012), (38.0, 2.1, 0.07, 0.012), (-95.0, 0.7, 0.07, 0.016),
         (30.0, 0.66, 0.06, 0.014), (-30.0, 2.05, 0.08, 0.012), (100.0, 2.15, 0.06, 0.01))
# hood cracks: azimuth (deg), top y, drift (m across per m up), half-width at the rim, seed, branches
# (fraction along the parent, drift, length, width scale)
HOOD_CRACKS = (
    (8.0, 1.48, -0.06, 0.04, 1, ((0.13, -0.8, 0.17, 0.6), (0.3, 0.55, 0.42, 0.7), (0.56, -0.5, 0.3, 0.6))),
    (-66.0, 1.08, -0.15, 0.024, 2, ((0.4, 0.5, 0.22, 0.6),)),
    (100.0, 0.76, 0.2, 0.018, 3, ()),
    (148.0, 1.24, 0.12, 0.026, 4, ((0.35, -0.45, 0.26, 0.6),)),
    (-150.0, 0.86, -0.1, 0.018, 5, ()),
)
# cracks on the rim only (azimuth, half-width at the lip)
RIM_ONLY = ((45.0, 0.016), (-28.0, 0.018), (-112.0, 0.016))
HOOD_Y0 = 0.495
RIM_Y0 = LIP_Y + 0.05


# ---------------------------------------------------------------------------------------------
# Small helpers (local to this build)
# ---------------------------------------------------------------------------------------------
def g(x, w):
    return np.exp(-(np.asarray(x, dtype=np.float64) / w) ** 2)


def angdiff(a, b):
    return np.angle(np.exp(1j * (np.asarray(a, dtype=np.float64) - b)))


def noise1(x, seed: int):
    x = np.atleast_1d(np.asarray(x, dtype=np.float64))
    return ck.value_noise(np.column_stack([x, np.full(len(x), 0.37 * seed), np.full(len(x), 1.7)]), seed)


def orient(P: np.ndarray, T: np.ndarray, C) -> np.ndarray:
    """Winds T outward: away from the per-vertex centres C, or from one point C."""
    C = np.asarray(C, dtype=np.float64)
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    inner = C if C.ndim == 1 else (C[T[:, 0]] + C[T[:, 1]] + C[T[:, 2]]) / 3.0
    out = (a + b + c) / 3.0 - inner
    if np.sum(np.einsum("ij,ij->i", fn, out) < 0.0) > len(T) / 2:
        return ck.flip(T)
    return T


def basis(d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    d = d / np.linalg.norm(d)
    a = np.array([0.0, 1.0, 0.0]) if abs(d[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = np.cross(d, a)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(d, e1)


def nail(base, d, length, width, bend_dir, bend, sides: int = 4):
    """A sharp, bent spike: base polygon, a narrower bent middle, a point."""
    base = np.asarray(base, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)
    d = d / np.linalg.norm(d)
    bend_dir = np.asarray(bend_dir, dtype=np.float64)
    e1, e2 = basis(d)
    rows = []
    for t, w in ((-0.05, width), (0.55, width * 0.55)):
        c = base + d * length * t + bend_dir * bend * length * max(t, 0.0) ** 2 * 0.6
        a = np.radians(45.0) + np.arange(sides) * 2.0 * math.pi / sides
        rows.append(c + w * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2)))
    tip = base + d * length + bend_dir * bend * length * 0.6
    P = np.vstack(rows + [tip[None]])
    n = sides
    T = []
    for q in range(n):
        q1 = (q + 1) % n
        T += [(q, n + q, q1), (q1, n + q, n + q1), (n + q, 2 * n, n + q1)]
    T = np.asarray(T, dtype=np.int64)
    C = np.vstack([np.repeat(base[None], n, 0), np.repeat((base + d * length * 0.55)[None], n, 0),
                   (base + d * length * 0.9)[None]])
    return P, orient(P, T, C)


def catmull(pts, n: int) -> np.ndarray:
    """n points on a Catmull-Rom curve through pts, evenly spaced by arclength."""
    pts = np.asarray(pts, dtype=np.float64)
    Q = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    seg = len(pts) - 1
    dense = []
    for i in range(seg * 40 + 1):
        f = i / 40.0
        k = min(int(f), seg - 1)
        t = f - k
        p0, p1, p2, p3 = Q[k], Q[k + 1], Q[k + 2], Q[k + 3]
        dense.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                            (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    dense = np.array(dense)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))])
    q = np.linspace(0.0, s[-1], n)
    return np.column_stack([np.interp(q, s, dense[:, i]) for i in range(3)])


def resample(path: np.ndarray, q) -> np.ndarray:
    """Points at arclength fractions q (0..1) along a polyline."""
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    return np.column_stack([np.interp(np.asarray(q) * s[-1], s, path[:, i]) for i in range(3)])


def sweep(path, rad, segs: int, up_hint=(0.0, 1.0, 0.0), squash: float = 1.0, cap0: bool = True,
          cap1: bool = True):
    """A tube along `path` like ck.tube, also returning each vertex's ring parameter t (0..1 along the path), its
    angle round the section, and its outward direction."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    rad = np.broadcast_to(np.asarray(rad, dtype=np.float64), (K,))
    tan, nrm, bin_ = ck.frames_along(path, up_hint)
    ang = np.arange(segs) * (2.0 * math.pi / segs)
    ca, sa = np.cos(ang), np.sin(ang)
    P, Dn, tt, aa = [], [], [], []
    for k in range(K):
        d = np.outer(ca, nrm[k]) + squash * np.outer(sa, bin_[k])
        P.append(path[k] + rad[k] * d)
        dn = np.outer(ca, nrm[k]) + np.outer(sa, bin_[k]) / max(squash, 1e-3)
        Dn.append(dn / np.linalg.norm(dn, axis=1, keepdims=True))
        tt.append(np.full(segs, k / (K - 1)))
        aa.append(ang)
    P, Dn, tt, aa = np.vstack(P), np.vstack(Dn), np.concatenate(tt), np.concatenate(aa)
    T = [ck.flip(ck.grid_tris(K, segs, True))]
    for cap, ring in ((cap0, 0), (cap1, K - 1)):
        if not cap:
            continue
        sgn = -1.0 if ring == 0 else 1.0
        tip = path[ring] + sgn * tan[ring] * rad[ring] * 0.3
        idx = len(P)
        P = np.vstack([P, tip[None]])
        Dn = np.vstack([Dn, (sgn * tan[ring])[None]])
        tt = np.append(tt, float(ring > 0))
        aa = np.append(aa, 0.0)
        r0 = ring * segs
        T.append(np.asarray([(r0 + s, idx, r0 + (s + 1) % segs) if ring == 0 else (r0 + s, r0 + (s + 1) % segs, idx)
                             for s in range(segs)], dtype=np.int64))
    return P, np.vstack(T), tt, aa, Dn


def barnacle(mesh: ck.Mesh, p, n, rho: float, rng, skin, slot: str, wet: float = 0.5) -> None:
    """One barnacle: a six-sided cone, its rim notched, its mouth a black pit."""
    n = np.asarray(n, dtype=np.float64)
    n = n / np.linalg.norm(n)
    e1, e2 = basis(n)
    h = rho * rng.uniform(0.6, 1.0)
    a = rng.uniform(0, 2 * math.pi) + np.arange(6) * math.pi / 3
    base = p - n * rho * 0.3 + rho * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2))
    rim = p + n * h + 0.5 * rho * (np.outer(np.cos(a + 0.5), e1) + np.outer(np.sin(a + 0.5), e2))
    pit = p + n * h * 0.45
    Pb = np.vstack([base, rim, pit[None]])
    Tb = [(i, (i + 1) % 6, 6 + i) for i in range(6)] + [((i + 1) % 6, 6 + (i + 1) % 6, 6 + i) for i in range(6)]
    Tb += [(6 + i, 6 + (i + 1) % 6, 12) for i in range(6)]
    Tb = orient(Pb, np.asarray(Tb, dtype=np.int64), p - n * rho)
    shell = ck.mix(PAL["coral_stone_weathered"] * 0.7, PAL["bone"] * 0.78, rng.uniform(0, 0.5))
    col = np.vstack([np.repeat((shell * 0.62)[None], 6, 0), np.repeat(shell[None], 6, 0), PAL["lacquer_black"][None]])
    cav = np.concatenate([np.full(6, 0.55), np.full(6, 0.1), [1.0]])
    ck.finish(mesh, Pb, Tb, slot, col, skin, wet=wet, cavity=cav, flat=True)


def disc_grid(rings: list[float], segs: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A polar grid: a centre point and rings (normalised radius rho) of `segs` points. Returns (rho, theta, T);
    theta 0 is up (+v), increasing toward +u. Wound so that +u x +v faces out."""
    rho = [0.0]
    th = [0.0]
    a = np.arange(segs) * 2.0 * math.pi / segs
    for r in rings:
        rho += [r] * segs
        th += list(a)
    T = [(0, 1 + (s + 1) % segs, 1 + s) for s in range(segs)]
    for k in range(len(rings) - 1):
        b0, b1 = 1 + k * segs, 1 + (k + 1) * segs
        for s in range(segs):
            s1 = (s + 1) % segs
            T += [(b0 + s, b0 + s1, b1 + s), (b0 + s1, b1 + s1, b1 + s)]
    return np.array(rho), np.array(th), np.asarray(T, dtype=np.int64)


# ---------------------------------------------------------------------------------------------
# The bell's form
# ---------------------------------------------------------------------------------------------
def outer_r(y: np.ndarray) -> np.ndarray:
    """The bell's outer radius by height: a lip flaring out of a narrow waist, a rounded shoulder, a domed crown."""
    y = np.asarray(y, dtype=np.float64)
    flare = 0.53 + 0.29 * ck.smoothstep(1.30, RIM_TOP, y) ** 2.2
    shoulder = 0.53 + 0.10 * np.exp(-((y - 1.80) / 0.30) ** 2)
    r = np.where(y < 1.30, flare, shoulder)
    crown = ck.smoothstep(1.98, 2.33, y)
    return r * np.sqrt(np.clip(1.0 - crown ** 2.4, 0.0, 1.0))


def crack_paths() -> list[dict]:
    """Every crack as a path in bell-surface coordinates (azimuth, y) with a half-width per point. Hood cracks start at
    the rim top and branch upward; rim cracks run from the lip up to meet them."""
    out = []

    def path(az0, y0, y1, drift, w0, seed, n, end_at_start=True):
        t = np.linspace(0.0, 1.0, n)
        y = y0 + (y1 - y0) * t
        lat = drift * (y - y0) + 0.026 * noise1(t * 5.5 + seed, SEED + seed) + 0.011 * noise1(t * 15 + seed, SEED + 50
                                                                                               + seed)
        lat = lat - (lat[0] if end_at_start else lat[-1])
        R = np.where(y < RIM_TOP, np.interp(y, RIM_OUT_Y, RIM_OUT_R), outer_r(y))
        az = az0 + lat / R
        return az, y

    for az_deg, y1, drift, w0, seed, branches in HOOD_CRACKS:
        n = max(int((y1 - HOOD_Y0) / 0.04), 6)
        az, y = path(D(az_deg), HOOD_Y0, y1, drift, w0, seed, n)
        t = np.linspace(0.0, 1.0, n)
        w = w0 * (1.0 - t) ** 0.75 * (0.8 + 0.2 * noise1(t * 9.0, SEED + 70 + seed)) + 0.0025
        out.append({"az": az, "y": y, "w": w, "where": "hood", "w0": w0})
        for b, (f, bd, ln, ws) in enumerate(branches):
            k = int(f * (n - 1))
            bn = max(int(ln / 0.04), 5)
            by1 = y[k] + ln / math.sqrt(1.0 + bd * bd)
            baz, byy = path(az[k], y[k], by1, bd, w[k] * ws, seed * 10 + b, bn)
            tb = np.linspace(0.0, 1.0, bn)
            bw = w[k] * ws * (1.0 - tb) ** 0.8 + 0.0022
            out.append({"az": baz, "y": byy, "w": bw, "where": "hood", "w0": w[k] * ws})
        # its rim part: from the lip up to the rim top, widest at the lip
        rn = 6
        big = abs(az_deg - math.degrees(BIG_AZ)) < 1.0
        raz, ry = path(D(az_deg), 0.385 if big else RIM_Y0, RIM_TOP + 0.008, drift * 0.5, w0, seed + 90, rn,
                       end_at_start=False)
        rw = np.linspace(w0 * (1.75 if big else 1.4), w0 * 1.02, rn)
        out.append({"az": raz, "y": ry, "w": rw, "where": "rim", "w0": rw[0], "big": big})
    for k, (az_deg, w0) in enumerate(RIM_ONLY):
        az, y = path(D(az_deg), RIM_Y0, RIM_TOP - 0.03, 0.1, w0, 200 + k, 5)
        out.append({"az": az, "y": y, "w": np.linspace(w0, 0.0025, 5), "where": "rim", "w0": w0, "big": False})
    return out


def rim_outer_profile() -> list[tuple[float, float]]:
    """The rim band's lathe profile, outside first (top down), round the lip, then the inside back up."""
    r_top = float(outer_r(np.array([RIM_TOP]))[0])
    return [(r_top + 0.004, RIM_TOP), (r_top + 0.016, RIM_TOP - 0.025), (0.5 * (RIM_R + r_top) + 0.02, 0.44),
            (RIM_R + 0.034, 0.405), (RIM_R + 0.03, 0.37), (RIM_R + 0.034, LIP_Y + 0.045),
            (RIM_R + 0.036, LIP_Y + 0.022), (RIM_R + 0.012, LIP_Y - 0.004), (RIM_R - 0.04, LIP_Y - 0.002),
            (RIM_R - 0.075, LIP_Y + 0.03), (r_top - 0.04, RIM_TOP - 0.08), (r_top - 0.07, RIM_TOP)]


_RP = rim_outer_profile()
RIM_OUT_Y = np.array([y for _r, y in _RP[:7]])[::-1]
RIM_OUT_R = np.array([r for r, _y in _RP[:7]])[::-1]


def _segments(paths: list[dict]) -> dict:
    A, B, WA, WB = [], [], [], []
    for p in paths:
        A.append(np.column_stack([p["az"][:-1], p["y"][:-1]]))
        B.append(np.column_stack([p["az"][1:], p["y"][1:]]))
        WA.append(p["w"][:-1])
        WB.append(p["w"][1:])
    return {"A": np.vstack(A), "B": np.vstack(B), "wa": np.concatenate(WA), "wb": np.concatenate(WB)}


def seg_distance(az, y, segs: dict, R) -> tuple[np.ndarray, np.ndarray]:
    """Distance (metres over the surface) from points (az, y) to the nearest segment, and that point's half-width."""
    az = np.atleast_1d(np.asarray(az, dtype=np.float64))
    y = np.atleast_1d(np.asarray(y, dtype=np.float64))
    R = np.broadcast_to(np.asarray(R, dtype=np.float64), az.shape)
    best = np.full(len(az), np.inf)
    bw = np.zeros(len(az))
    A, B = segs["A"], segs["B"]
    for i0 in range(0, len(az), 4096):
        sl = slice(i0, i0 + 4096)
        px = angdiff(az[sl][:, None], A[None, :, 0]) * R[sl][:, None]
        py = y[sl][:, None] - A[None, :, 1]
        bx = angdiff(B[None, :, 0], A[None, :, 0]) * R[sl][:, None]
        by = np.broadcast_to(B[None, :, 1] - A[None, :, 1], px.shape)
        t = np.clip((px * bx + py * by) / np.maximum(bx * bx + by * by, 1e-12), 0.0, 1.0)
        d = np.hypot(px - t * bx, py - t * by)
        k = np.argmin(d, axis=1)
        rows = np.arange(len(k))
        best[sl] = d[rows, k]
        tk = t[rows, k]
        bw[sl] = segs["wa"][k] * (1 - tk) + segs["wb"][k] * tk
    return best, bw


CRACKS = crack_paths()
HOOD_SEGS = _segments([c for c in CRACKS if c["where"] == "hood"])
RIM_SEGS = _segments([c for c in CRACKS if c["where"] == "rim"])
# the old mend's crack, closed and dark, running out from under the plate
OLD_CRACK = _segments([{"az": PATCH_AZ + np.array([0.02, 0.05, 0.0, -0.04, -0.02, -0.06]),
                        "y": np.array([0.70, 0.78, 0.86, 1.01, 1.09, 1.14]), "w": np.full(6, 0.004)}])


def frieze(az, y, R):
    """The cast frieze: running waves under the fan-shells, twelve slots (the first the sigil's). Returns
    (relief, raised mask, hollow mask)."""
    out = np.zeros_like(y)
    raised = np.zeros_like(y)
    hollow = np.zeros_like(y)
    # the running waves: 18 round the bell, each a slow rise and a curling fall
    s = (angdiff(az, SLOT0) + math.pi) / (2 * math.pi) * 18.0
    f = s - np.floor(s)
    yc = 1.384 + 0.094 * f ** 1.6
    body = ck.smoothstep(yc - 0.065, yc - 0.012, y) * ck.smoothstep(yc + 0.006, yc - 0.003, y)
    band = ck.smoothstep(1.366, 1.378, y) * ck.smoothstep(1.496, 1.486, y)
    out += 0.0 * body
    hollow += 0.7 * band
    # the fan-shells' ground (the shells are cast pieces of their own, `fan_shells`): dark verdigris
    hollow += ck.smoothstep(1.51, 1.53, y) * ck.smoothstep(1.94, 1.92, y)
    return out, np.clip(raised, 0, 1), np.clip(hollow, 0, 1)


def relief(az, y, with_masks: bool = False):
    """The bell's smooth cast relief (radial metres) at surface coordinates: beads, the sound bow, the inscription
    field, the frieze, dents, and the bronze pushed out round the wounds. No pitting."""
    az = np.atleast_1d(np.asarray(az, dtype=np.float64))
    y = np.atleast_1d(np.asarray(y, dtype=np.float64))
    R = outer_r(y)
    d = np.zeros_like(y)
    bead = np.zeros_like(y)
    for yc in BEADS:
        bead += g(y - yc, 0.009)
    d += 0.010 * bead
    d += 0.008 * ck.smoothstep(0.68, 0.52, y)  # the sound bow, thickened where it rings
    field = ck.smoothstep(1.178, 1.19, y) * ck.smoothstep(1.347, 1.335, y)
    d -= 0.003 * field
    fr, fr_raised, fr_hollow = frieze(az, y, R)
    d += fr
    dent = np.zeros_like(y)
    for a, yc, r, dep in DENTS:
        dist = np.hypot(angdiff(az, D(a)) * R, y - yc)
        dd = -dep * g(dist, r) + 0.3 * dep * g(dist - 1.25 * r, 0.35 * r)
        d += dd
        dent = np.maximum(dent, g(dist, r))
    cd, cw = seg_distance(az, y, HOOD_SEGS, R)
    d += 0.004 * g(cd, 0.05) * ck.smoothstep(0.002, 0.02, cw)
    # the strike seat's ground and the sigil's roundel, slightly sunk
    sd = np.hypot(angdiff(az, SEAT_AZ) * R, y - SEAT_Y)
    gd = np.hypot(angdiff(az, SLOT0) * R, y - SIGIL_Y)
    d -= 0.002 * ck.smoothstep(SEAT_R * 1.3, SEAT_R, sd) + 0.002 * ck.smoothstep(SIGIL_R * 1.25, SIGIL_R, gd)
    if not with_masks:
        return d
    raised = np.clip(bead + fr_raised, 0.0, 1.0)
    hollow = np.clip(fr_hollow + field + 0.6 * dent, 0.0, 1.0)
    return d, {"raised": raised, "hollow": hollow, "dent": dent, "crack_d": cd, "crack_w": cw, "seat_d": sd}


def bell_surf(az, y, h=0.0) -> np.ndarray:
    az = np.atleast_1d(np.asarray(az, dtype=np.float64))
    y = np.atleast_1d(np.asarray(y, dtype=np.float64))
    R = outer_r(y) + relief(az, y) + h
    return np.column_stack([R * np.sin(az), y, R * np.cos(az)])


def rim_relief(az, y):
    az = np.atleast_1d(np.asarray(az, dtype=np.float64))
    y = np.atleast_1d(np.asarray(y, dtype=np.float64))
    q = np.column_stack([np.sin(az) * 0.85, y, np.cos(az) * 0.85]) * 9.0
    crust = ck.smoothstep(0.0, 0.45, ck.fbm(q, SEED + 12)) * ck.smoothstep(0.47, 0.36, y)
    return 0.005 * crust


def rim_surf(az, y, h=0.0) -> np.ndarray:
    az = np.atleast_1d(np.asarray(az, dtype=np.float64))
    y = np.atleast_1d(np.asarray(y, dtype=np.float64))
    R = np.interp(y, RIM_OUT_Y, RIM_OUT_R) + rim_relief(az, y) + h
    return np.column_stack([R * np.sin(az), y, R * np.cos(az)])


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def leg_frame(i: int) -> np.ndarray:
    a = (i + 0.5) * 2.0 * math.pi / 6.0
    return np.array([math.sin(a), 0.0, math.cos(a)])


def leg_pts(i: int):
    """(r, y) of the leg's points in its own radial plane: femur path, knee, tibia end, the hooked tip."""
    return {"femur": [(0.40, 0.32), (0.52, 0.255), (0.70, 0.218), (0.86, 0.214), (0.97, 0.262), (1.035, 0.322)],
            "knee": (1.035, 0.322), "ankle": (1.12, 0.13), "hook": [(1.12, 0.13), (1.15, 0.06), (1.13, 0.018),
                                                                    (1.085, 0.004)]}


def W(i: int, r: float, y: float) -> np.ndarray:
    return leg_frame(i) * r + np.array([0.0, y, 0.0])


def rope_path(n: int = 60) -> np.ndarray:
    """The rope's centreline from the canon it is knotted to, over the crown and down the left shoulder, hanging free
    past the waist, over the flare and the rim, off the lip and along the ground to its frayed end."""
    a0 = D(ROPE_AZ)
    ctl = [(0.150, 2.445, 0.0), (0.255, 2.392, 0.0)]
    for y in (2.30, 2.21, 2.11, 2.02, 1.93, 1.84):
        ctl.append((float(outer_r(np.array([y]))[0] + relief(np.array([a0]), np.array([y]))[0]) + 0.036, y, 0.0))
    for y in (1.62, 1.38, 1.14, 0.94, 0.80, 0.68, 0.58):
        surf = float(outer_r(np.array([y]))[0] + relief(np.array([a0]), np.array([y]))[0]) + 0.036
        ctl.append((max(0.70 + 0.03 * (1.84 - y) / 1.84, surf), y, 0.0))
    for y in (0.47, 0.40, 0.34):
        ctl.append((float(np.interp(y, RIM_OUT_Y, RIM_OUT_R)) + 0.04, y, 0.0))
    ctl += [(0.95, 0.27, 0.0), (1.0, 0.17, 0.0), (1.07, 0.08, 0.04), (1.15, 0.04, 0.1), (1.24, 0.037, 0.18),
            (1.32, 0.04, 0.27)]
    pts = []
    for r, y, da in ctl:
        a = a0 - 0.06 * (2.45 - y) / 2.45 - da
        pts.append((r * math.sin(a), y, r * math.cos(a)))
    return catmull(pts, n)


def rope_bone_pts() -> np.ndarray:
    rp = rope_path(400)
    i1 = int(np.argmin(np.abs(rp[:, 1] - 1.84)))
    i2 = int(np.argmin(np.abs(rp[:, 1] - 0.40) + 10.0 * (np.arange(len(rp)) < i1)))
    return np.array([rp[0], rp[i1], rp[i2], rp[-1]])


def big_wound_point() -> tuple[np.ndarray, np.ndarray]:
    p = rim_surf(np.array([BIG_AZ]), np.array([0.40]))[0]
    n = np.array([math.sin(BIG_AZ), 0.0, math.cos(BIG_AZ)])
    return p, n


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.25, 0))
    rig.add("bell", (0, 0.3, 0), (0, 2.3, 0), "root")
    rig.add("rim", (0, LIP_Y, 0), (0, RIM_TOP, 0), "bell")
    rig.add("mass", (0, 0.35, 0), (0, 0.9, 0), "bell")
    for i in range(6):
        lp = leg_pts(i)
        hip = W(i, 0.50, 0.25)
        knee = W(i, *lp["knee"])
        foot = W(i, *lp["hook"][-1])
        rig.add(f"leg{i}_a", hip, knee, "mass")
        rig.add(f"leg{i}_b", knee, foot, f"leg{i}_a")
    rb = rope_bone_pts()
    rig.add("rope0", rb[0], rb[1], "bell")
    rig.add("rope1", rb[1], rb[2], "rope0")
    rig.add("rope2", rb[2], rb[3], "rope1")
    # VFX anchors (unweighted): the rim's biggest wound, the bell's centre, the mouth the flood pours from
    pw, nw = big_wound_point()
    rig.add("vfx_wound", pw, pw + nw * 0.3, "rim")
    rig.add("vfx_core", (0.0, 1.15, 0.0), (0.0, 1.55, 0.0), "bell")
    rig.add("vfx_phase", (0.0, LIP_Y, 0.0), (0.0, LIP_Y - 0.25, 0.0), "bell")
    return rig


# ---------------------------------------------------------------------------------------------
# The bell body
# ---------------------------------------------------------------------------------------------
def bell_color(P, az, y, R, m: dict, pit):
    """Worn bronze: brass on the high points and where it was struck, verdigris in the hollows with pale bloom over
    brown run-streaks, wet and weed low down under a salt tide line, scorched round the wounds."""
    n = len(P)
    pn = ck.fbm(P * 3.0, SEED + 2)
    raised, hollow = m["raised"], m["hollow"]
    patina = np.clip(0.55 + 0.9 * pn + 0.55 * hollow - 0.8 * raised + 0.2 * ck.smoothstep(1.3, 0.6, y)
                     - 0.45 * ck.smoothstep(2.12, 2.32, y), 0.0, 1.0)
    col = ck.mix(PAL["brass"], PAL["bronze_patina"], patina[:, None])
    streak = ck.smoothstep(0.1, 0.55, ck.value_noise(np.column_stack([P[:, 0] * 26.0, y * 1.1, P[:, 2] * 26.0]),
                                                     SEED + 4))
    col = ck.mix(col, PAL["tortoiseshell"] * 1.1, (0.38 * streak * (1 - raised))[:, None])
    bloom = ck.smoothstep(0.08, 0.42, ck.fbm(P * 5.5, SEED + 5)) * np.clip(0.3 + 0.8 * hollow, 0, 1)
    col = ck.mix(col, ck.mix(PAL["bronze_patina"], PAL["salt_glass"], 0.5), (0.55 * bloom)[:, None])
    worn = 0.6 + 0.4 * ck.smoothstep(-0.2, 0.3, ck.fbm(P * 9.0, SEED + 6))
    col = ck.mix(col, PAL["brass"] * 1.1, (0.62 * raised * worn)[:, None])
    strike = g(m["seat_d"], 0.2)
    col = ck.mix(col, PAL["brass"] * 1.16, (0.7 * strike)[:, None])
    col = col * (1.0 - 0.12 * pit)[:, None]
    algae = ck.smoothstep(0.78, 0.52, y) * ck.smoothstep(-0.1, 0.3, ck.fbm(P * 4.0, SEED + 8))
    col = ck.mix(col, PAL["foliage_shadow"] * 1.15, (0.5 * algae)[:, None])
    tide = g(y - 0.83 - 0.02 * ck.fbm(P * 3.0, SEED + 9), 0.016)
    col = ck.mix(col, PAL["coral_stone_weathered"] * 0.85, (0.38 * tide)[:, None])
    wet = ck.smoothstep(WET_LINE + 0.12, WET_LINE - 0.12, y)
    col = ck.mix(col, PAL["deep_teal_shadow"], (0.22 * wet)[:, None])
    halo = g(m["crack_d"], 0.065) * ck.smoothstep(0.002, 0.02, m["crack_w"])
    col = ck.mix(col, PAL["lacquer_black"], (0.6 * halo)[:, None])
    stain = g(m["crack_d"], 0.03) * ck.smoothstep(0.002, 0.02, m["crack_w"])
    col = ck.mix(col, PAL["spawn_wound"] * 0.5, (0.25 * stain)[:, None])
    od, _w = seg_distance(az, y, OLD_CRACK, R)
    line = g(od, 0.007)
    col = ck.mix(col, PAL["lacquer_black"], (0.75 * line)[:, None])
    cavity = np.clip(0.12 + 0.55 * hollow + 0.2 * pit + 0.35 * halo + 0.5 * line + 0.25 * m["dent"], 0.0, 1.0)
    emission = 0.1 * stain
    return col, wet, cavity, emission


def bell_band(mesh: ck.Mesh, rig: ck.Rig, ys: list[float], segs: int, skirt_lo: bool, skirt_hi: bool,
              flare_bottom: bool = False) -> None:
    """One band of the bell's outer surface: rows at `ys`, with skirts tucked under the neighbouring bands (they have
    other segment counts, so their edges never meet exactly)."""
    rows = sorted(ys, reverse=True)
    inset = np.zeros(len(rows))
    if skirt_hi:
        rows = [rows[0] + 0.009] + rows
        inset = np.concatenate([[0.007], inset])
    if skirt_lo:
        rows = rows + [rows[-1] - 0.009]
        inset = np.concatenate([inset, [0.007]])
    if flare_bottom:
        rows = rows + [rows[-1] - 0.006]
        inset = np.concatenate([inset, [-0.004]])
    rows = np.array(rows)
    a = np.arange(segs) * 2.0 * math.pi / segs + math.pi / segs
    AZ = np.tile(a, len(rows))
    Y = np.repeat(rows, segs)
    R0 = outer_r(Y)
    rel, m = relief(AZ, Y, with_masks=True)
    P0 = np.column_stack([np.sin(AZ), np.zeros(len(Y)), np.cos(AZ)])
    pit = ck.smoothstep(0.32, 0.75, ck.value_noise(np.column_stack([P0[:, 0] * 0.7, Y, P0[:, 2] * 0.7]) * 26.0,
                                                   SEED + 7))
    R = R0 + rel - 0.002 * pit - np.repeat(inset, segs)
    P = np.column_stack([R * np.sin(AZ), Y, R * np.cos(AZ)])
    T = ck.grid_tris(len(rows), segs, True)
    T = orient(P, T, np.column_stack([np.zeros(len(Y)), Y, np.zeros(len(Y))]))
    col, wet, cav, em = bell_color(P, AZ, Y, R0, m, pit)
    ck.finish(mesh, P, T, "bronze", col, rig.rigid("bell"), wet=wet, cavity=cav, emission=em)


def bell_inside(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The bottom annulus and the inside of the bell, dark and wet (seen when it rears, tips or loses its lip)."""
    r0 = float(outer_r(np.array([RIM_TOP]))[0])
    prof = [(r0 + 0.008, RIM_TOP)]
    for y in np.linspace(RIM_TOP, 2.05, 8):
        prof.append((float(outer_r(np.array([y]))[0]) - 0.07 - 0.03 * float(ck.smoothstep(1.6, 2.05, y)), float(y)))
    prof.append((0.0, 2.12))
    P, T = ck.lathe(prof, 30)
    y = P[:, 1]
    n = ck.fbm(P * 4.0, SEED + 30)
    col = ck.mix(PAL["bronze_patina"] * 0.42, PAL["lacquer_black"], ck.smoothstep(-0.2, 0.4, n)[:, None] * 0.6)
    worn = ck.smoothstep(0.62, 0.5, y)  # the inner lip, worn by the thing inside
    col = ck.mix(col, PAL["brass"] * 0.6, (0.4 * worn)[:, None])
    ck.finish(mesh, P, T, "bronze", col, rig.rigid("bell"), wet=0.8, cavity=np.clip(0.55 - 0.3 * worn, 0, 1))


def bell_body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    lower = [0.50, 0.545, 0.588, 0.60, 0.612, 0.633, 0.645, 0.657, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.008, 1.02,
             1.032, 1.075, 1.12, 1.15, 1.17]
    bell_band(mesh, rig, lower, 56, skirt_lo=False, skirt_hi=True, flare_bottom=True)
    insc = [1.17, 1.182, 1.20, 1.235, 1.27, 1.305, 1.33, 1.343, 1.355]
    bell_band(mesh, rig, insc, 72, skirt_lo=True, skirt_hi=True)
    frz = [1.355, 1.367, 1.385, 1.42, 1.455, 1.48, 1.493, 1.505, 1.517, 1.56, 1.62, 1.68, 1.74, 1.80, 1.86, 1.91, 1.938,
           1.95, 1.962, 1.985]
    bell_band(mesh, rig, frz, 64, skirt_lo=True, skirt_hi=True)
    crown = [1.985, 1.997, 2.03, 2.08, 2.13, 2.18, 2.23, 2.27, 2.30]
    bell_band(mesh, rig, crown, 48, skirt_lo=True, skirt_hi=False)
    bell_inside(mesh, rig)


# ---------------------------------------------------------------------------------------------
# Cast details: the inscription, the sigil, the strike seat, the mend
# ---------------------------------------------------------------------------------------------
def surface_frame(az: float, y: float, surf) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(point, outward normal, +u across (increasing azimuth), +v up the surface) at a surface coordinate."""
    p = surf(np.array([az]), np.array([y]))[0]
    pa = surf(np.array([az + 0.01]), np.array([y]))[0]
    py = surf(np.array([az]), np.array([y + 0.01]))[0]
    eu = (pa - p) / np.linalg.norm(pa - p)
    ev = (py - p) / np.linalg.norm(py - p)
    n = np.cross(eu, ev)
    n /= np.linalg.norm(n)
    return p, n, eu, ev


def stroke(mesh: ck.Mesh, a: np.ndarray, b: np.ndarray, n: np.ndarray, width: float, height: float, col_top,
           col_side, bone: int) -> None:
    """A raised cast stroke from a to b on a surface with normal n: a top and two long sides, sunk at the foot."""
    d = b - a
    ln = np.linalg.norm(d)
    d = d / ln
    s = np.cross(n, d)
    s /= np.linalg.norm(s)
    a = a - d * width * 0.4
    b = b + d * width * 0.4
    hw = width * 0.5
    P = np.array([a - s * hw - n * 0.003, b - s * hw - n * 0.003, a - s * hw * 0.7 + n * height,
                  b - s * hw * 0.7 + n * height, a + s * hw * 0.7 + n * height, b + s * hw * 0.7 + n * height,
                  a + s * hw - n * 0.003, b + s * hw - n * 0.003])
    T = np.array([(0, 1, 2), (2, 1, 3), (2, 3, 4), (4, 3, 5), (4, 5, 6), (6, 5, 7)], dtype=np.int64)
    T = orient(P, T, (a + b) * 0.5 - n * 0.05)
    col = np.array([col_side, col_side, col_top, col_top, col_top, col_top, col_side, col_side])
    cav = np.array([0.7, 0.7, 0.0, 0.0, 0.0, 0.0, 0.7, 0.7])
    ck.finish(mesh, P, T, "bronze", col, bone, wet=0.15, cavity=cav, flat=True)


def waves(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The frieze's running waves under the shells: twelve cast crests, each a slow rise and a curl over."""
    bone = rig.rigid("bell")
    R = float(outer_r(np.array([1.43]))[0])
    span = 2.0 * math.pi / 12
    pts_s = (0.0, 0.25, 0.5, 0.7, 0.84, 0.93, 0.95, 0.9, 0.82)
    pts_y = (1.392, 1.41, 1.435, 1.462, 1.481, 1.478, 1.462, 1.447, 1.452)
    for k in range(12):
        a0 = SLOT0 + (k + 0.5) * span - span * 0.5
        top = PAL["brass"] * 1.06
        side = ck.mix(PAL["bronze_patina"], PAL["brass"], 0.3) * 0.75
        prev = None
        for s_, y_ in zip(pts_s, pts_y):
            p, n, _eu, _ev = surface_frame(a0 + s_ * span, y_, bell_surf)
            if prev is not None:
                stroke(mesh, prev[0], p, prev[1], 0.014, 0.0055, top, side, bone)
            prev = (p, n)


def inscription(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The band of raised script between the beads: an invented script, glyphs of three to six strokes on a 3x5 node
    grid, a lozenge between every seventh; none where a wound runs through."""
    rng = np.random.default_rng(SEED + 60)
    bone = rig.rigid("bell")
    n_gl = 28
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    for gi in range(n_gl):
        azc = SLOT0 + (gi + 0.5) * 2.0 * math.pi / n_gl
        R = float(outer_r(np.array([1.26]))[0])
        cd, _cw = seg_distance(np.array([azc]), np.array([1.26]), HOOD_SEGS, R)
        if cd[0] < 0.07:
            continue
        top = PAL["brass"] * (1.0 + 0.1 * rng.random())
        side = ck.mix(PAL["bronze_patina"], PAL["brass"], 0.35) * 0.8
        if gi % 7 == 3:  # a lozenge
            c, nrm, eu, ev = surface_frame(azc, 1.262, bell_surf)
            for q in range(4):
                p0 = c + 0.022 * (eu * math.cos(q * math.pi / 2) + ev * math.sin(q * math.pi / 2))
                p1 = c + 0.022 * (eu * math.cos((q + 1) * math.pi / 2) + ev * math.sin((q + 1) * math.pi / 2))
                stroke(mesh, p0, p1, nrm, 0.013, 0.005, top, side, bone)
            continue
        node = (int(rng.integers(0, 3)), 4)
        used = set()
        for _s in range(int(rng.integers(3, 7))):
            for _try in range(12):
                mv = moves[int(rng.integers(0, 8))]
                nxt = (node[0] + mv[0], node[1] + mv[1])
                key = tuple(sorted([node, nxt]))
                if 0 <= nxt[0] <= 2 and 0 <= nxt[1] <= 4 and key not in used:
                    break
            else:
                break
            used.add(key)

            def at(nd):
                az = azc + (nd[0] - 1) * 0.032 / R
                yy = 1.203 + nd[1] * 0.029
                return surface_frame(az, yy, bell_surf)

            pa, na, _eu, _ev = at(node)
            pb, _nb, _eu2, _ev2 = at(nxt)
            stroke(mesh, pa, pb, na, 0.016, 0.006, top, side, bone)
            node = nxt if rng.random() < 0.8 else (int(rng.integers(0, 3)), int(rng.integers(0, 5)))


def roundel(mesh: ck.Mesh, rig: ck.Rig, az0: float, y0: float, rad: float, rings: list[float], segs: int, height_fn,
            color_fn, slot: str = "bronze") -> None:
    """A cast roundel conforming to the bell: a polar grid at (az0, y0), raised by height_fn(rho, theta) (metres;
    rho 1 is its edge, past it the grid tucks into the bell)."""
    rho, th, T = disc_grid(rings, segs)
    R = float(outer_r(np.array([y0]))[0])
    u = rho * np.sin(th) * rad
    v = rho * np.cos(th) * rad
    az = az0 + u / R
    y = y0 + v
    h = height_fn(rho, th)
    P = bell_surf(az, y, h)
    T = orient(P, T, np.array([0.0, y0, 0.0]))
    col, cav = color_fn(P, rho, th, h)
    ck.finish(mesh, P, T, slot, col, rig.rigid("bell"), wet=0.1, cavity=cav)


def sigil(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The Shell Shrine's sigil on the face: a notched border, a fan-shell of seven rays rising from a pearl, and
    under it two arcs of the swell."""
    def height(rho, th):
        h = np.where(rho <= 1.0, 0.004, -0.004)
        border = (rho >= 0.86) & (rho <= 1.0)
        notch = (np.abs(np.sin(th * 8.0)) < 0.3) & (rho > 0.9)
        h = h + np.where(border & ~notch, 0.0055, 0.0)
        up = np.abs(angdiff(th, 0.0)) < D(84.0)
        rays = np.zeros_like(rho)
        for k in range(5):
            rays = np.maximum(rays, (np.abs(angdiff(th, D(-60.0 + 30.0 * k))) < D(4.0)).astype(float))
        h = h + 0.0045 * rays * up * (rho > 0.2) * (rho < 0.62)
        h = h + 0.0045 * up * (np.abs(rho - 0.66) < 0.01)
        low = np.abs(angdiff(th, math.pi)) < D(78.0)
        h = h + 0.004 * low * ((np.abs(rho - 0.34) < 0.01) | (np.abs(rho - 0.52) < 0.01))
        h = h + 0.007 * (rho < 0.14)
        return h

    def color(P, rho, th, h):
        hi = ck.smoothstep(0.004, 0.0085, h)
        col = ck.mix(PAL["bronze_patina"] * 0.85, ck.mix(PAL["bronze_patina"], PAL["salt_glass"], 0.35),
                     ck.smoothstep(0.0, 0.4, ck.fbm(P * 8.0, SEED + 61))[:, None] * 0.5)
        col = ck.mix(col, PAL["brass"] * 1.12, (0.85 * hi)[:, None])
        return col, np.clip(0.55 - 0.55 * hi + 0.3 * (rho > 1.0), 0, 1)

    rings = [0.13, 0.22, 0.34, 0.43, 0.52, 0.6, 0.66, 0.74, 0.86, 0.94, 1.0, 1.07]
    roundel(mesh, rig, SLOT0, SIGIL_Y, SIGIL_R, rings, 36, height, color)


def fan_shells(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The frieze's fan-shells (the Shell Shrine's stone fans, haluna.md), eleven cast round the shoulder, the sigil in
    the twelfth slot: a domed fan from a hinge on the bead, five raised ribs, a scalloped rolled edge."""
    nth = 11
    half = D(58.0)
    th = np.linspace(-half, half, nth)
    rings = [0.22, 0.45, 0.68, 0.86, 0.95, 1.04]
    rib = (np.arange(nth) % 2 == 1).astype(float)  # columns 1, 3, 5, 7, 9: the ribs
    for k in range(1, 12):
        azk = SLOT0 + k * math.pi / 6.0
        rho = [0.0] + [r for r in rings for _ in range(nth)]
        tt = [0.0] + list(th) * len(rings)
        ribv = np.concatenate([[0.0], np.tile(rib, len(rings))])
        rho, tt = np.array(rho), np.array(tt)
        T = [(0, 1 + q + 1, 1 + q) for q in range(nth - 1)]
        for r in range(len(rings) - 1):
            b0, b1 = 1 + r * nth, 1 + (r + 1) * nth
            for q in range(nth - 1):
                T += [(b0 + q, b0 + q + 1, b1 + q), (b0 + q + 1, b1 + q + 1, b1 + q)]
        T = np.asarray(T, dtype=np.int64)
        scal = np.where(ribv > 0, 1.0, 0.95)  # the edge scalloped: the ribs run out further
        q = rho / scal
        h = 0.013 * np.sqrt(np.clip(1.0 - np.minimum(q, 1.0) ** 2, 0.0, 1.0)) + 0.004 * g(q - 0.9, 0.06)
        h = h + 0.004 * ribv * ck.smoothstep(0.15, 0.3, rho) * (q < 0.97) + 0.003
        h = np.where(q > 1.0, -0.004, h)
        h = np.where(np.abs(np.abs(tt) - half) < 1e-6, -0.003, h)  # the straight sides tuck in
        h[0] = 0.008
        R = float(outer_r(np.array([1.72]))[0])
        u = rho * np.sin(tt) * 0.18 * scal
        v = rho * np.cos(tt) * 0.39 * scal
        P = bell_surf(azk + u / R, 1.515 + v, h)
        T = orient(P, T, np.array([0.0, 1.7, 0.0]))
        n = ck.fbm(P * 8.0, SEED + 66 + k)
        hi = np.clip(ribv * ck.smoothstep(0.2, 0.4, rho) + g(q - 0.9, 0.07), 0.0, 1.0) * (q <= 1.0)
        col = ck.mix(PAL["bronze_patina"], ck.mix(PAL["bronze_patina"], PAL["salt_glass"], 0.4),
                     ck.smoothstep(0.0, 0.4, n)[:, None] * 0.6)
        col = ck.mix(col, PAL["brass"] * 1.1, (np.clip(0.3 + 0.7 * hi, 0, 1) * (0.7 + 0.3 * ck.smoothstep(-0.3, 0.2, n))
                                               )[:, None])
        col = ck.mix(col, PAL["tortoiseshell"] * 1.1, (0.25 * ck.smoothstep(0.2, 0.5, n) * (1 - hi))[:, None])
        ck.finish(mesh, P, T, "bronze", col, rig.rigid("bell"), wet=0.05, cavity=np.clip(0.45 - 0.45 * hi, 0, 1))


def strike_seat(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The strike seat: a petalled boss on the waist where the shrine's beam struck it, worn bright and scored."""
    def height(rho, th):
        edge = 1.0 - 0.12 * np.abs(np.cos(th * 4.0)) ** 0.5
        q = rho / edge
        h = np.where(q <= 1.0, 0.006 + 0.004 * np.sqrt(np.clip(1 - q, 0, 1)), -0.004)
        return h + 0.008 * np.sqrt(np.clip(1.0 - (rho / 0.3) ** 2, 0.0, 1.0))

    def color(P, rho, th, h):
        score = ck.smoothstep(0.3, 0.8, ck.value_noise(P * np.array([60.0, 6.0, 60.0]), SEED + 62))
        col = ck.mix(PAL["brass"] * 1.18, PAL["brass"] * 0.85, (0.5 * score)[:, None])
        col = ck.mix(col, PAL["bronze_patina"], (ck.smoothstep(0.75, 1.0, rho) * 0.6)[:, None])
        return col, np.clip(0.1 + 0.3 * score + 0.4 * (rho > 1.0), 0, 1)

    roundel(mesh, rig, SEAT_AZ, SEAT_Y, SEAT_R, [0.15, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0, 1.08], 24, height, color)


def mend(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """An old mend: a cast plate riveted over a crack (the crack runs on out from under it, closed and dark), one corner
    chipped, darker and browner than the bell."""
    rng = np.random.default_rng(SEED + 63)
    rings = [0.3, 0.6, 0.8, 0.92, 1.0, 1.07]
    rho, th, T = disc_grid(rings, 24)
    sup = 1.0 / (np.abs(np.sin(th)) ** 4 + np.abs(np.cos(th)) ** 4) ** 0.25  # a rounded square
    chip = 1.0 - 0.18 * g(angdiff(th, D(135.0)), 0.25)
    u = rho * np.sin(th) * sup * chip * 0.135
    v = rho * np.cos(th) * sup * chip * 0.15
    R = float(outer_r(np.array([PATCH_Y]))[0])
    h = np.where(rho <= 1.0, 0.008 + 0.003 * g(rho - 0.92, 0.04), -0.004)
    P = bell_surf(PATCH_AZ + u / R, PATCH_Y + v, h)
    T = orient(P, T, np.array([0.0, PATCH_Y, 0.0]))
    n = ck.fbm(P * 7.0, SEED + 64)
    col = ck.mix(PAL["brass"] * 0.7, PAL["tortoiseshell"], 0.45)
    col = ck.mix(np.tile(col, (len(P), 1)), PAL["bronze_patina"] * 0.9, (ck.smoothstep(-0.1, 0.4, n) * 0.35)[:, None])
    col = ck.mix(col, PAL["brass"] * 1.05, (0.6 * g(rho - 0.92, 0.04))[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.7 * (rho > 1.0))[:, None])
    bone = rig.rigid("bell")
    ck.finish(mesh, P, T, "bronze", col, bone, wet=0.15, cavity=np.clip(0.2 + 0.4 * (rho > 0.95), 0, 1))
    for k in range(8):
        t = k * 2.0 * math.pi / 8 + 0.2
        s1 = 1.0 / (abs(math.sin(t)) ** 4 + abs(math.cos(t)) ** 4) ** 0.25
        uu, vv = 0.8 * math.sin(t) * s1 * 0.135, 0.8 * math.cos(t) * s1 * 0.15
        c, nr, _eu, _ev = surface_frame(PATCH_AZ + uu / R, PATCH_Y + vv, bell_surf)
        c = c + nr * 0.007
        rr = 0.016 * rng.uniform(0.85, 1.1)
        Pr, Tr = ck.lathe([(0.0, rr * 0.7), (rr * 0.75, rr * 0.5), (rr, -0.002)], 6)
        e1, e2 = basis(nr)
        M = np.column_stack([e1, nr, e2])
        Pr = Pr @ M.T + c
        Tr = orient(Pr, Tr, c - nr * 0.02)
        colr = ck.mix(PAL["laterite"] * 0.85, PAL["brass"] * 0.8, rng.uniform(0.2, 0.6))
        ck.finish(mesh, Pr, Tr, "bronze", colr, bone, wet=0.2, cavity=0.3)


def low_barnacles(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A few barnacles on the bell above the rim, where the sea kept it longest."""
    rng = np.random.default_rng(SEED + 65)
    bone = rig.rigid("bell")
    placed = 0
    while placed < 9:
        az = rng.uniform(-math.pi, math.pi)
        y = rng.uniform(0.52, 0.72)
        R = float(outer_r(np.array([y]))[0])
        cd, _w = seg_distance(np.array([az]), np.array([y]), HOOD_SEGS, R)
        if cd[0] < 0.07 or np.hypot(angdiff(az, SEAT_AZ) * R, y - SEAT_Y) < 0.15:
            continue
        c, nr, _eu, _ev = surface_frame(az, y, bell_surf)
        barnacle(mesh, c, nr, rng.uniform(0.014, 0.03), rng, bone, "rim", wet=0.4)
        placed += 1


# ---------------------------------------------------------------------------------------------
# The wounds
# ---------------------------------------------------------------------------------------------
def seam(mesh: ck.Mesh, az, y, w, surf, bone: int, slot: str, glow: float, seed: int, base_col) -> None:
    """An open wound seam along a path on a surface: torn bronze lips peeled outward (bright at the tear), dark
    walls, the light along the floor. The tip closes to a point."""
    rng = np.random.default_rng(seed)
    n = len(y)
    c = surf(az, y)
    t = np.gradient(c, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    nr = np.column_stack([np.sin(az), np.zeros(n), np.cos(az)])
    lat = np.cross(nr, t)
    lat /= np.linalg.norm(lat, axis=1, keepdims=True)
    eaz = np.column_stack([np.cos(az), np.zeros(n), -np.sin(az)])
    la = np.einsum("ij,ij->i", lat, eaz)
    ly = lat[:, 1]
    R = np.linalg.norm(c[:, [0, 2]], axis=1)
    lw = 0.007 + 0.5 * w
    lh = (0.003 + 0.42 * w)
    j1 = 0.65 + 0.6 * rng.random(n)
    j2 = 0.65 + 0.6 * rng.random(n)
    tear1 = 0.15 * rng.random(n) * lw
    tear2 = 0.15 * rng.random(n) * lw
    U = np.column_stack([-(w + lw), -(w + 0.3 * lw + tear1), -w, -0.5 * w, 0 * w, 0.5 * w, w, w + 0.3 * lw + tear2,
                         w + lw])
    H = np.column_stack([np.full(n, -0.004), lh * j1, 0.25 * lh, np.full(n, 0.0022), np.full(n, 0.0016),
                         np.full(n, 0.0022), 0.25 * lh, lh * j2, np.full(n, -0.004)])
    U[-1] *= 0.05
    H[-1] = np.minimum(H[-1], 0.0015)
    AZ = az[:, None] + la[:, None] * U / R[:, None]
    YY = y[:, None] + ly[:, None] * U
    P = surf(AZ.ravel(), YY.ravel(), H.ravel())
    T = ck.grid_tris(n, 9, False)
    T = orient(P, T, np.column_stack([np.zeros(len(P)), P[:, 1], np.zeros(len(P))]))
    nv = len(P)
    base = np.broadcast_to(np.asarray(base_col, dtype=np.float64), (nv, 3))
    torn = ck.mix(base, PAL["brass"] * 1.1, 0.55)
    colmap = [base * 0.55, torn, PAL["lacquer_black"], PAL["deep_teal_shadow"] * 0.55, PAL["spawn_wound"],
              PAL["deep_teal_shadow"] * 0.55, PAL["lacquer_black"], torn, base * 0.55]
    col = np.zeros((nv, 3))
    col_id = np.tile(np.arange(9), n)
    for j in range(9):
        sel = col_id == j
        cj = colmap[j]
        col[sel] = cj[sel] if np.ndim(cj) == 2 else cj
    em = np.array([0.0, 0.0, 0.04, 0.45, 1.0, 0.45, 0.04, 0.0, 0.0])[col_id] * glow
    cav = np.array([0.35, 0.0, 0.75, 0.45, 0.0, 0.45, 0.75, 0.0, 0.35])[col_id]
    ck.finish(mesh, P, T, slot, col, bone, wet=0.5, cavity=cav, emission=em, flat=True)


def hood_wounds(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for k, c in enumerate(CRACKS):
        if c["where"] != "hood":
            continue
        base = ck.mix(PAL["bronze_patina"], PAL["brass"], 0.3) * 0.75
        seam(mesh, c["az"], c["y"], c["w"], bell_surf, rig.rigid("bell"), "bronze", 0.8, SEED + 400 + k, base)


# ---------------------------------------------------------------------------------------------
# The rim
# ---------------------------------------------------------------------------------------------
def rim_barnacle_spots() -> list[tuple[float, float, float, int]]:
    """(azimuth, y, size, seed) of the rim's barnacles: crusted thickest low down, clear of the wounds."""
    rng = np.random.default_rng(SEED + 21)
    out = []
    while len(out) < 21:  # colonies of three to five, packed close, one big in each
        a0 = rng.uniform(-math.pi, math.pi)
        y0 = LIP_Y + 0.05 + (RIM_TOP - LIP_Y - 0.11) * rng.random() ** 1.5
        d, _w = seg_distance(np.array([a0]), np.array([y0]), RIM_SEGS, RIM_R)
        if d[0] < 0.09 or abs(angdiff(a0, BIG_AZ)) * RIM_R < 0.14:
            continue
        for q in range(int(rng.integers(3, 6))):
            sz = rng.uniform(0.026, 0.042) if q == 0 else rng.uniform(0.014, 0.026)
            a = a0 + rng.normal(0.0, 0.045)
            yy = float(np.clip(y0 + rng.normal(0.0, 0.03), LIP_Y + 0.04, RIM_TOP - 0.03))
            out.append((a, yy, sz, int(rng.integers(0, 1 << 30))))
    return out[:21]


def rim_band(rig: ck.Rig, broken: bool) -> ck.Mesh:
    """The thick flared lip from LIP_Y to RIM_TOP: a cast bead, barnacle crust, a chip out of the lip under the
    biggest wound, and the open wound seams, widest and brightest here (the weak point). `broken` takes out
    105 degrees of the lip round the biggest wound: jagged fractures of raw bronze, the light gone out of it."""
    mesh = ck.Mesh("RimBroken" if broken else "Rim")
    bone = rig.rigid("rim")
    prof = _RP
    segs = 64
    if broken:
        span = 2.0 * math.pi - (BREAK_ARC[1] - BREAK_ARC[0])
        ncol = int(round(segs * span / (2.0 * math.pi))) + 1
        cols = BREAK_ARC[1] + np.linspace(0.0, span, ncol)
    else:
        ncol = segs
        cols = np.arange(segs) * 2.0 * math.pi / segs
    nrow = len(prof)
    AZ = np.tile(cols, nrow).astype(np.float64)
    r_p = np.repeat([r for r, _y in prof], ncol)
    Y = np.repeat([y for _r, y in prof], ncol).astype(np.float64)
    row = np.repeat(np.arange(nrow), ncol)
    colk = np.tile(np.arange(ncol), nrow)
    if broken:  # jagged fracture: each row's end column pushed in or out
        rng_j = np.random.default_rng(SEED + 25)
        jag = rng_j.uniform(-D(5.0), D(5.0), (2, nrow))
        AZ = AZ + np.where(colk == 0, -jag[0][row], 0.0) + np.where(colk == ncol - 1, jag[1][row], 0.0)
        AZ = AZ + np.where(colk == 1, -0.4 * jag[0][row], 0.0) + np.where(colk == ncol - 2, 0.4 * jag[1][row], 0.0)
    outside = row <= 6
    # the chip out of the lip under the biggest wound
    dch = np.abs(angdiff(AZ, BIG_AZ)) * RIM_R
    chip = 0.035 * np.clip(1.0 - dch / 0.07, 0.0, 1.0) * (Y < LIP_Y + 0.05)
    Y = Y + chip
    R = r_p + np.where(outside, rim_relief(AZ, Y), 0.0)
    P = np.column_stack([R * np.sin(AZ), Y, R * np.cos(AZ)])
    # wound by the lathe's rule (outside listed top down, round the lip, then the inside), as ck.lathe does: orient()
    # by a centre would turn the inside faces the wrong way on this thin shell
    T = ck.grid_tris(nrow, ncol, not broken)
    # colour
    n = ck.fbm(P * 9.0, SEED + 11)
    col = ck.mix(PAL["bronze_patina"] * 0.62, PAL["brass"] * 0.8, ck.smoothstep(0.1, 0.45, n)[:, None] * 0.45)
    col = ck.mix(col, PAL["deep_teal_shadow"], 0.25)
    crust = ck.smoothstep(0.001, 0.004, rim_relief(AZ, Y)) * outside
    col = ck.mix(col, PAL["coral_stone_weathered"] * 0.78, (0.75 * crust)[:, None])
    bead = g(Y - 0.405, 0.02) * outside
    col = ck.mix(col, PAL["brass"] * 1.05, (0.45 * bead * (1 - crust))[:, None])
    algae = ck.smoothstep(LIP_Y + 0.06, LIP_Y, Y) * ck.smoothstep(-0.1, 0.3, ck.fbm(P * 5.0, SEED + 13))
    col = ck.mix(col, PAL["foliage_shadow"] * 1.1, (0.6 * algae)[:, None])
    cd, cw = seg_distance(AZ, Y, RIM_SEGS, R)
    spill = g(cd, 0.05) * ck.smoothstep(0.002, 0.02, cw)
    glow_scale = 0.3 if broken else 1.0
    col = ck.mix(col, PAL["lacquer_black"], (0.55 * spill)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, (0.45 * g(cd, 0.03) * glow_scale)[:, None])
    em = 0.4 * g(cd, 0.035) * glow_scale
    chipm = ck.smoothstep(0.0, 0.01, chip)
    col = ck.mix(col, PAL["brass"] * 1.1, (0.6 * chipm)[:, None])
    cav = np.clip(0.2 + 0.3 * crust + 0.3 * spill, 0, 1)
    if broken:
        edge = np.minimum(np.abs(angdiff(AZ, BREAK_ARC[0])), np.abs(angdiff(AZ, BREAK_ARC[1])))
        scorch = ck.smoothstep(0.3, 0.0, edge)
        col = ck.mix(col, PAL["lacquer_black"], (0.7 * scorch)[:, None])
        em = em * (1.0 - scorch)
    ck.finish(mesh, P, T, "rim", col, bone, wet=0.8, cavity=cav, emission=em)
    if broken:  # the fracture faces: raw bronze, bright, dark at the rim of the break
        for end in (0, ncol - 1):
            loop = P[np.arange(nrow) * ncol + end]
            cen = loop.mean(axis=0)
            Pf = np.vstack([loop, cen[None]])
            Tf = np.array([(q, (q + 1) % nrow, nrow) for q in range(nrow)], dtype=np.int64)
            side = np.array([math.cos(cols[end]), 0.0, -math.sin(cols[end])]) * (-1.0 if end == 0 else 1.0)
            Tf = orient(Pf, Tf, cen - side * 0.05)
            colf = np.vstack([np.repeat((PAL["brass"] * 1.15)[None], nrow, 0), (PAL["brass"] * 0.9)[None]])
            ck.finish(mesh, Pf, Tf, "rim", colf, bone, wet=0.1, cavity=0.15, flat=True)
    # the wound seams
    for k, c in enumerate(CRACKS):
        if c["where"] != "rim":
            continue
        if broken and np.any((angdiff(c["az"], BREAK_ARC[0]) > -D(4.0)) & (angdiff(c["az"], BREAK_ARC[1]) < D(4.0))):
            continue
        base = ck.mix(PAL["bronze_patina"] * 0.8, PAL["sand_wet"] * 0.6, 0.3)
        glow = (1.0 if c.get("big") else 0.9) * glow_scale
        seam(mesh, c["az"], c["y"], c["w"], rim_surf, bone, "rim", glow, SEED + 500 + k, base)
    # barnacles: crusted on the band's outside, thickest low down, clear of the wounds
    for a, yy, sz, sd in rim_barnacle_spots():
        if broken and angdiff(a, BREAK_ARC[0]) > -0.05 and angdiff(a, BREAK_ARC[1]) < 0.05:
            continue
        c, nr, _eu, _ev = surface_frame(a, yy, rim_surf)
        barnacle(mesh, c, nr, sz, np.random.default_rng(sd), bone, "rim", wet=0.6)
    return mesh


# ---------------------------------------------------------------------------------------------
# The crown: plate, canons, chain stub
# ---------------------------------------------------------------------------------------------
def arch(mesh: ck.Mesh, foot_a, foot_b, height: float, thick: float, bone: int, rng, broken: bool = False) -> None:
    """A cast canon: a loop standing on the crown plate, oval in section, a bead round its crown; `broken` leaves
    one leg snapped off short, bright at the break."""
    foot_a, foot_b = np.asarray(foot_a, dtype=np.float64), np.asarray(foot_b, dtype=np.float64)
    up = np.array([0.0, 1.0, 0.0])
    half = 0.5 * np.linalg.norm((foot_b - foot_a) * np.array([1.0, 0.0, 1.0]))
    across = (foot_b - foot_a) * np.array([1.0, 0.0, 1.0]) / (2.0 * half)
    yc = max(foot_a[1], foot_b[1]) + height - half
    mid = 0.5 * (foot_a + foot_b)
    pts = [foot_a - up * 0.01, np.array([foot_a[0], 0.5 * (foot_a[1] + yc), foot_a[2]])]
    for th in np.linspace(0.0, math.pi, 7):
        pts.append(np.array([mid[0], yc, mid[2]]) - across * half * math.cos(th) + up * half * math.sin(th))
    pts += [np.array([foot_b[0], 0.5 * (foot_b[1] + yc), foot_b[2]]), foot_b - up * 0.01]
    path = np.array(pts)
    if broken:
        path = path[:5]
    t = np.linspace(0.0, 1.0, len(path))
    rad = thick * (1.0 + 0.3 * np.exp(-((t - 0.5) / 0.07) ** 2) * (not broken))
    rad[0] *= 1.3
    if not broken:
        rad[-1] *= 1.3
    P, T, tt, aa, Dn = sweep(path, rad, 6, up_hint=tuple(np.cross(across, up)), squash=0.7)
    n = ck.fbm(P * 12.0, int(rng.integers(0, 9999)))
    col = ck.mix(PAL["brass"] * 1.05, PAL["bronze_patina"], ck.smoothstep(-0.15, 0.35, n)[:, None] * 0.8)
    if broken:
        col = ck.mix(col, PAL["brass"] * 1.2, (tt > 0.9)[:, None] * 0.8)
    ck.finish(mesh, P, T, "bronze", col, bone, wet=0.05, cavity=0.2)


def crown(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The crown plate with its moulded edge, the central hanging loop, four canons round it (one snapped), and a stub
    of rusted chain hanging off the loop with its last link broken open."""
    rng = np.random.default_rng(SEED + 31)
    bone = rig.rigid("bell")
    prof = [(0.0, 2.398), (0.16, 2.39), (0.218, 2.37), (0.234, 2.345), (0.226, 2.316), (0.19, 2.294),
            (0.12, 2.278)]
    P, T = ck.lathe(prof, 30)
    n = ck.fbm(P * 10.0, SEED + 32)
    y = P[:, 1]
    edge = g(y - 2.345, 0.02)
    col = ck.mix(PAL["bronze_patina"], PAL["brass"] * 1.05, np.clip(0.35 + 0.6 * edge - 0.4 * n, 0, 1)[:, None])
    bloom = ck.smoothstep(0.1, 0.4, ck.fbm(P * 6.0, SEED + 33))
    col = ck.mix(col, ck.mix(PAL["bronze_patina"], PAL["salt_glass"], 0.45), (0.45 * bloom * (1 - edge))[:, None])
    ck.finish(mesh, P, T, "bronze", col, bone, wet=0.05, cavity=np.clip(0.35 - 0.3 * edge, 0, 1))
    # the central loop (the argent): it hung by this
    a_l = D(ROPE_AZ + 45.0)
    ax = np.array([math.sin(a_l), 0.0, math.cos(a_l)])
    arch(mesh, np.array([0, 2.39, 0]) - ax * 0.095, np.array([0, 2.39, 0]) + ax * 0.095, 0.2, 0.04, bone, rng)
    # four canons round it, leaning out
    for k in range(4):
        a = D(ROPE_AZ + 90.0 * k)
        rad_d = np.array([math.sin(a), 0.0, math.cos(a)])
        fa = rad_d * 0.1 + np.array([0, 2.388, 0])
        fb = rad_d * 0.215 + np.array([0, 2.365, 0])
        arch(mesh, fa, fb, 0.13, 0.027, bone, rng, broken=(k == 2))
    # the chain stub: three links and half of a fourth, hanging off the loop's top over the plate's edge
    top = np.array([0.0, 2.6, 0.0])
    path = catmull([top + np.array([0.0, -0.01, 0.0]), np.array([0.05, 2.53, 0.09]), np.array([0.09, 2.45, 0.17]),
                    np.array([0.12, 2.37, 0.25])], 20)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    link = 0.09
    nl = 4
    for k in range(nl):
        sk = min((k + 0.5) * link * 0.78, s[-1])
        c = np.array([np.interp(sk, s, path[:, i]) for i in range(3)])
        t = np.array([np.interp(sk, s, np.gradient(path, axis=0)[:, i]) for i in range(3)])
        t /= np.linalg.norm(t)
        e1, e2 = basis(t)
        if k % 2:
            e1, e2 = e2, e1
        qn = 4 if k == nl - 1 else 6  # the last link broken open
        loop = np.array([c + t * (link * 0.5 * math.cos(q * 2 * math.pi / 6)) + e1 * (link * 0.3 * math.sin(
            q * 2 * math.pi / 6)) for q in range(6)])
        wr = link * 0.1
        rings = []
        for q in range(6):
            tq = loop[(q + 1) % 6] - loop[(q - 1) % 6]
            tq /= np.linalg.norm(tq)
            side = np.cross(tq, e2)
            rings.append(loop[q] + wr * np.array([side, e2, -side, -e2]))
        Pc = np.vstack(rings)
        Tc = []
        for q in range(qn - 1 if qn < 6 else 6):
            q1 = (q + 1) % 6
            for m in range(4):
                m1 = (m + 1) % 4
                a_, b_, c_, d_ = q * 4 + m, q * 4 + m1, q1 * 4 + m, q1 * 4 + m1
                Tc += [(a_, c_, b_), (b_, c_, d_)]
        Tc = orient(Pc, np.asarray(Tc, dtype=np.int64), np.repeat(loop, 4, axis=0))
        colr = ck.mix(PAL["volcanic_stone"] * 0.8, PAL["laterite"] * 0.7, 0.3 + 0.15 * k)
        ck.finish(mesh, Pc, Tc, "bronze", colr, bone, wet=0.2, cavity=0.35, flat=True)


# ---------------------------------------------------------------------------------------------
# The rope
# ---------------------------------------------------------------------------------------------
def rope(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Three-strand hemp, rotten: the lay twisting down it (each strand a lobe, grooves between), bleached where it
    lies over the crown, dark and slimed with weed below the tide line; a knot round the canon, a popped strand,
    weed hanging off it, and the end unravelled into three strands and loose fibres."""
    rb = rope_bone_pts()
    chain = rig.chain(["rope0", "rope1", "rope2"], rb)
    path = rope_path(46)
    K = len(path)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    tan, nrm, bin_ = ck.frames_along(path, (1.0, 0.0, 0.0))
    segs = 9
    pitch = 0.40
    r0 = 0.033
    P, LAY = [], []
    for k in range(K):
        phi = 2.0 * math.pi * s[k] / pitch
        a = phi + np.arange(segs) * 2.0 * math.pi / segs
        lobe = np.where(np.arange(segs) % 3 == 0, 0.72, 1.0)
        rr = r0 * lobe * (1.0 - 0.15 * (s[k] / s[-1]) ** 2)
        P.append(path[k] + rr[:, None] * (np.outer(np.cos(a), nrm[k]) + np.outer(np.sin(a), bin_[k])))
        LAY.append(lobe)
    P = np.vstack(P)
    LAY = np.concatenate(LAY)
    T = ck.flip(ck.grid_tris(K, segs, True))
    nv = len(P)
    P = np.vstack([P, (path[0] - tan[0] * 0.01)[None], (path[-1] + tan[-1] * 0.008)[None]])
    cap0 = [(q, nv, (q + 1) % segs) for q in range(segs)]
    cap1 = [((K - 1) * segs + q, (K - 1) * segs + (q + 1) % segs, nv + 1) for q in range(segs)]
    T = np.vstack([T, np.asarray(cap0, dtype=np.int64), np.asarray(cap1, dtype=np.int64)])
    C = np.vstack([np.repeat(path, segs, axis=0), path[:1], path[-1:]])
    T = orient(P, T, C)
    LAY = np.concatenate([LAY, [0.72, 0.72]])
    y = P[:, 1]
    hemp = ck.mix(PAL["timber_weathered"], PAL["saltgrass"] * 0.85, ck.smoothstep(1.6, 2.3, y)[:, None] * 0.5)
    hemp = ck.mix(hemp, PAL["thatch"] * 0.8, (0.3 * ck.smoothstep(0.0, 0.4, ck.fbm(P * 14.0, SEED + 42)))[:, None])
    groove = (LAY < 0.9).astype(float)
    col = hemp * (1.0 - 0.45 * groove)[:, None]
    low = ck.smoothstep(0.95, 0.5, y)
    col = ck.mix(col, PAL["foliage_shadow"] * 1.05, (0.65 * low)[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.25 * low * groove)[:, None])
    ck.finish(mesh, P, T, "rope", col, chain, wet=np.clip(0.2 + 0.8 * low, 0, 1), cavity=0.15 + 0.6 * groove)
    rng = np.random.default_rng(SEED + 41)
    # the knot round the canon: one turn round its leg
    a = D(ROPE_AZ)
    rad_d = np.array([math.sin(a), 0.0, math.cos(a)])
    side = np.array([math.cos(a), 0.0, -math.sin(a)])
    kc = rad_d * 0.155 + np.array([0.0, 2.43, 0.0])
    turn = [kc + 0.045 * (side * math.cos(t) + rad_d * math.sin(t)) + np.array([0, 0.012 * t, 0])
            for t in np.linspace(0.0, 2.0 * math.pi * 0.95, 11)]
    Pk, Tk = ck.tube(np.array(turn), 0.026, 6)
    ck.finish(mesh, Pk, Tk, "rope", ck.mix(PAL["timber_weathered"], PAL["saltgrass"] * 0.85, 0.4), rig.rigid("rope0"),
              wet=0.2, cavity=0.3)
    # a popped strand, looping out of the lay below the tide line
    i0 = int(np.argmin(np.abs(path[:, 1] - 0.72)))
    p0, p1 = path[i0 - 1], path[i0 + 1]
    out = nrm[i0]
    loop = ck.bezier([p0 + out * 0.02, p0 + out * 0.07, p1 + out * 0.07, p1 + out * 0.02], 7)
    Pl, Tl = ck.tube(loop, 0.011, 4)
    ck.finish(mesh, Pl, Tl, "rope", PAL["timber_weathered"] * 0.7, chain, wet=0.9, cavity=0.3)
    # weed: ribbons hanging off the rope from the shoulder down
    for q in range(4):
        f0 = 0.5 + 0.09 * q + rng.uniform(-0.02, 0.02)
        sp = resample(path, np.linspace(f0, f0 + 0.1, 7))
        out_d = sp * np.array([1.0, 0.0, 1.0])
        out_d /= np.linalg.norm(out_d, axis=1, keepdims=True)
        wob = np.sin(np.linspace(0.0, 3.0, 7) + q)[:, None] * side[None] * 0.02
        sp = sp + out_d * (0.03 + 0.03 * np.linspace(0, 1, 7) ** 2)[:, None] + wob
        sp[-2:, 1] -= np.array([0.03, 0.08])
        sp[:, 1] = np.maximum(sp[:, 1], 0.05)
        wdt = np.linspace(rng.uniform(0.03, 0.04), rng.uniform(0.014, 0.02), 7)
        Pw, Tw = ck.tube(sp, wdt, 4, cap_start=False, squash=0.4, up_hint=tuple(rad_d))
        tip = np.concatenate([np.repeat(np.linspace(0, 1, 7), 4), [1.0]])[: len(Pw)]
        colw = ck.mix(PAL["foliage_shadow"] * 1.2, PAL["saltgrass"] * 0.55, (0.1 + 0.6 * tip)[:, None])
        ck.finish(mesh, Pw, Tw, "rope", colw, chain, wet=1.0, cavity=0.2)
    # the frayed end: three strands splaying, and loose fibres
    end, te = path[-1], tan[-1]
    e1, e2 = nrm[-1], bin_[-1]
    for q in range(3):
        a = q * 2.0 * math.pi / 3 + 0.4
        d = np.cos(a) * e1 + np.sin(a) * e2
        d_flat = d.copy()
        d_flat[1] = abs(d_flat[1]) * 0.3
        sp = ck.bezier([end - te * 0.02 + d * 0.012, end + te * 0.05 + d_flat * 0.03,
                        end + te * 0.12 + d_flat * 0.08 + np.array([0, 0.01, 0])], 5)
        sp[:, 1] = np.maximum(sp[:, 1], 0.014)
        Ps, Ts = ck.tube(sp, np.linspace(0.013, 0.005, 5), 4)
        ck.finish(mesh, Ps, Ts, "rope", PAL["timber_weathered"] * 0.75, rig.rigid("rope2"), wet=0.9, cavity=0.3)
        for _f in range(3):
            fd = te + d_flat * rng.uniform(0.3, 1.2) + rng.normal(0, 0.25, 3)
            fd[1] = abs(fd[1]) * 0.2 + 0.05
            fd /= np.linalg.norm(fd)
            b0 = sp[-1]
            tip = b0 + fd * rng.uniform(0.04, 0.09)
            Pf = np.array([b0 + e1 * 0.003, b0 - e1 * 0.003 + e2 * 0.003, b0 - e2 * 0.003, tip])
            Tf = orient(Pf, np.array([(0, 1, 3), (1, 2, 3), (2, 0, 3)], dtype=np.int64), b0 - fd * 0.01)
            ck.finish(mesh, Pf, Tf, "rope", PAL["saltgrass"] * 0.6, rig.rigid("rope2"), wet=0.7, cavity=0.1)


# ---------------------------------------------------------------------------------------------
# The mass and the legs
# ---------------------------------------------------------------------------------------------
def carapace_col(P, seed: int, edge=0.0, crust=0.0, membrane=0.0):
    """Lacquer-black carapace mottled to abyss navy, slate where plates are worn at the edges, salt crust, glossy
    deep-teal membrane."""
    n = len(P)
    m1 = ck.fbm(P * 7.0, seed)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"] * 1.2, ck.smoothstep(-0.1, 0.4, m1)[:, None] * 0.7)
    col = ck.mix(col, PAL["storm_slate"] * 1.05, np.broadcast_to(np.asarray(edge, dtype=np.float64), (n,))[:, None]
                 * 0.65)
    col = ck.mix(col, PAL["coral_stone_weathered"] * 0.62, np.broadcast_to(np.asarray(crust, dtype=np.float64),
                                                                           (n,))[:, None])
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.6, np.broadcast_to(np.asarray(membrane, dtype=np.float64),
                                                                     (n,))[:, None])
    return col


def plate(mesh: ck.Mesh, bone: int, path: np.ndarray, r0: float, r1: float, seed: int, side_hint, *, segs: int = 7,
          cuff: float = 0.16, crust_from: float = -1.0, keel: float = 0.18) -> None:
    """One telescoping carapace plate along `path`: pinched where it leaves the joint, a hard flared cuff at its far
    end, a keel along its top, flattened top to bottom, worn slate at the cuff and keel."""
    K = len(path)
    t = np.linspace(0.0, 1.0, K)
    rad = (r0 + (r1 - r0) * t) * (0.8 + 0.2 * ck.smoothstep(0.0, 0.3, t)) * (1.0 + cuff * g(t - 0.9, 0.08))
    rad[-1] *= 0.86
    P, T, tt, aa, Dn = sweep(path, rad, segs, up_hint=tuple(side_hint), squash=0.78)
    topm = ck.smoothstep(0.55, 0.95, Dn[:, 1])
    ridx = np.minimum(np.round(tt * (K - 1)).astype(int), K - 1)
    P = P + Dn * (keel * rad[ridx] * topm)[:, None]
    P = P + Dn * (0.004 * ck.fbm(P * 40.0, seed))[:, None]
    edge = np.clip(g(tt - 0.9, 0.06) + 0.7 * topm * 0.6, 0, 1)
    reach = np.linalg.norm(P[:, [0, 2]], axis=1)
    crust = 0.0 if crust_from < 0 else ck.smoothstep(crust_from, crust_from + 0.08, reach) * ck.smoothstep(
        crust_from + 0.26, crust_from + 0.16, reach) * ck.smoothstep(0.0, 0.4, ck.fbm(P * 12.0, seed + 1)) * topm
    col = carapace_col(P, seed + 2, edge=edge, crust=crust)
    ck.finish(mesh, P, T, "carapace", col, bone, wet=np.clip(1.0 - 0.7 * np.asarray(crust), 0.2, 1.0),
              cavity=np.clip(0.15 + 0.35 * g(tt - 0.03, 0.08), 0, 1))


def membrane(mesh: ck.Mesh, bone: int, a, b, r: float, side_hint) -> None:
    path = np.array([a, 0.5 * (a + b), b])
    P, T, tt, aa, Dn = sweep(path, np.array([r, r * 0.88, r]), 7, up_hint=tuple(side_hint), squash=0.8, cap0=False,
                             cap1=False)
    col = carapace_col(P, SEED + 77, membrane=0.9)
    ck.finish(mesh, P, T, "carapace", col, bone, wet=1.0, cavity=0.3)


def leg(mesh: ck.Mesh, rig: ck.Rig, i: int) -> None:
    rng = np.random.default_rng(SEED + 100 + i)
    lp = leg_pts(i)
    rh = leg_frame(i)
    side = np.array([rh[2], 0.0, -rh[0]])
    ba, bb = rig.rigid(f"leg{i}_a"), rig.rigid(f"leg{i}_b")
    fem = catmull([W(i, r, y) for r, y in lp["femur"]], 40)
    sd = SEED + 120 + 10 * i
    # the femur: two telescoping plates (the inner one barnacle-crusted where it leaves the mouth)
    plate(mesh, ba, resample(fem, np.linspace(0.0, 0.5, 6)), 0.056, 0.053, sd, side, crust_from=0.7)
    plate(mesh, ba, resample(fem, np.linspace(0.535, 0.97, 6)), 0.05, 0.052, sd + 3, side, crust_from=0.82)
    membrane(mesh, ba, resample(fem, [0.48])[0], resample(fem, [0.55])[0], 0.041, side)
    knee = W(i, *lp["knee"])
    ankle = W(i, *lp["ankle"])
    membrane(mesh, bb, resample(fem, [0.95])[0], knee + (ankle - knee) * 0.12, 0.04, side)
    # the knee: a spur pointing up and out
    kd = (rh * 0.6 + np.array([0.0, 1.0, 0.0]))
    Pn, Tn = nail(knee + np.array([0, 0.03, 0]), kd, 0.06, 0.024, rh, 0.4)
    ck.finish(mesh, Pn, Tn, "carapace", ck.mix(PAL["lacquer_black"], PAL["storm_slate"], 0.4), ba, wet=0.9,
              cavity=0.1, flat=True)
    # the tibia: one plate with two spines along its outer edge
    tib = catmull([knee + (ankle - knee) * 0.05, knee + (ankle - knee) * 0.5 + rh * 0.012, ankle], 6)
    plate(mesh, bb, tib, 0.046, 0.038, sd + 5, side, cuff=0.2)
    for f in (0.5,):
        p = resample(tib, [f])[0]
        Ps, Ts = nail(p + rh * 0.032, rh + np.array([0, 0.5, 0]), 0.04, 0.012, -np.array([0, 1.0, 0]), 0.5)
        ck.finish(mesh, Ps, Ts, "carapace", PAL["storm_slate"] * 0.8, bb, wet=0.9, cavity=0.1, flat=True)
    membrane(mesh, bb, ankle - (ankle - knee) * 0.06, ankle + (W(i, *lp["hook"][1]) - ankle) * 0.25, 0.031, side)
    # the hooked tarsus, curling in under to grip
    hk = catmull([W(i, r, y) for r, y in lp["hook"]], 7)
    t = np.linspace(0.0, 1.0, 7)
    rad = 0.034 * (1.0 - t) ** 0.8 + 0.002
    P, T, tt, aa, Dn = sweep(hk, rad, 6, up_hint=tuple(side), squash=0.8, cap1=False)
    P[:, 1] = np.maximum(P[:, 1], 0.0015)
    col = carapace_col(P, sd + 7, edge=ck.smoothstep(0.6, 1.0, tt) * 0.5)
    col = ck.mix(col, PAL["bone"] * 0.55, (ck.smoothstep(0.75, 1.0, tt) * 0.6)[:, None])
    ck.finish(mesh, P, T, "carapace", col, bb, wet=0.9, cavity=0.15)
    # barnacles crusting the femur where it leaves the mouth
    for f in rng.uniform(0.8, 0.92, 2):
        p = resample(fem, [f])[0]
        nrm = np.array([0.0, 1.0, 0.0]) + side * rng.uniform(-0.6, 0.6)
        barnacle(mesh, p + nrm / np.linalg.norm(nrm) * 0.038, nrm, rng.uniform(0.013, 0.022), rng, ba, "rim",
                 wet=0.6)


def mass_body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The black wet mass in the bell's mouth: folded underneath, plated where the legs leave it, wound slits glowing
    between the folds, and a puckered maw at its underside glowing where the flood pours out."""
    prof = [(0.0, 0.98), (0.3, 0.94), (0.52, 0.82), (0.63, 0.64), (0.62, 0.48), (0.58, 0.38), (0.52, 0.31),
            (0.42, 0.262), (0.31, 0.235), (0.22, 0.222), (0.165, 0.212), (0.13, 0.226), (0.09, 0.255), (0.045, 0.28),
            (0.0, 0.29)]
    segs = 28
    P, T = ck.lathe(prof, segs)
    phi = np.arctan2(P[:, 0], P[:, 2])
    rho = np.linalg.norm(P[:, [0, 2]], axis=1)
    y = P[:, 1]
    under = ck.smoothstep(0.52, 0.3, y) * ck.smoothstep(0.12, 0.2, rho)
    fold_n = ck.fbm(P * 5.0, SEED + 51)
    fold = np.cos(phi * 9.0 + 1.2 * fold_n)
    radial = P - np.column_stack([np.zeros(len(P)), np.full(len(P), 0.6), np.zeros(len(P))])
    radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-6)
    coxa = np.zeros(len(P))
    for i in range(6):
        hip = W(i, 0.46, 0.3)
        coxa = np.maximum(coxa, g(np.linalg.norm(P - hip, axis=1), 0.09))
    P = P + radial * (0.026 * fold * under + 0.03 * coxa + 0.025 * fold_n)[:, None]
    T = orient(P, T, np.array([0.0, 0.6, 0.0]))
    valley = ck.smoothstep(-0.3, -0.85, fold) * under
    slit = valley * ck.smoothstep(-0.12, 0.18, ck.fbm(P * 3.0, SEED + 52))
    maw = ck.smoothstep(0.16, 0.08, rho) * (y > 0.2)
    col = carapace_col(P, SEED + 53, edge=0.8 * ck.smoothstep(0.4, 0.95, fold) * under + 0.6 * coxa,
                       membrane=0.5 * valley)
    col = ck.mix(col, PAL["spawn_wound"] * 0.85, np.clip(slit + maw, 0, 1)[:, None])
    em = np.clip(1.0 * slit + 1.0 * maw, 0, 1)
    ck.finish(mesh, P, T, "carapace", col, rig.rigid("mass"), wet=1.0, cavity=np.clip(0.2 + 0.5 * valley, 0, 1),
              emission=em)
    # the maw's lip: a puckered ring of plates round the glow
    rng = np.random.default_rng(SEED + 54)
    for k in range(9):
        a = k * 2.0 * math.pi / 9 + rng.uniform(-0.1, 0.1)
        rd = np.array([math.sin(a), 0.0, math.cos(a)])
        b0 = rd * 0.19 + np.array([0.0, 0.215, 0.0])
        Pn, Tn = nail(b0, -rd * 0.9 + np.array([0.0, 0.25, 0.0]), 0.07, 0.02, np.array([0.0, 1.0, 0.0]), 0.3)
        ck.finish(mesh, Pn, Tn, "carapace", ck.mix(PAL["lacquer_black"], PAL["storm_slate"], 0.35), rig.rigid("mass"),
                  wet=1.0, cavity=0.2, flat=True)


def build_meshes(rig: ck.Rig) -> tuple[ck.Mesh, list[ck.Mesh]]:
    mesh = ck.Mesh("drownbell")
    bell_body(mesh, rig)
    inscription(mesh, rig)
    waves(mesh, rig)
    sigil(mesh, rig)
    fan_shells(mesh, rig)
    strike_seat(mesh, rig)
    mend(mesh, rig)
    hood_wounds(mesh, rig)
    low_barnacles(mesh, rig)
    crown(mesh, rig)
    rope(mesh, rig)
    mass_body(mesh, rig)
    for i in range(6):
        leg(mesh, rig, i)
    return mesh, [rim_band(rig, False), rim_band(rig, True)]


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
# M3-CRB-013 (the final move pass, from the battle camera): every skill has its own clip (creatures.json
# `clip_by_skill`), the flood phase has its own heavier stance and its own versions of the clips it plays (the
# phase's `clips` map), and the feet stay planted: every clip but the KO's end is re-solved so each hooked foot stays
# where it grips the ground while the bell rocks over it (`plant_feet`), lifting only where a clip steps or stamps.
# Root rotations: +x leans the crown toward its foe (+z, the face), +z leans it toward -x.
LEGS = [f"leg{i}" for i in range(6)]
MIRROR_LEG = [5, 4, 3, 2, 1, 0]  # the leg across the x = 0 plane (legs sit at azimuth (i + 0.5) x 60 degrees)
Y = np.array([0.0, 1.0, 0.0])
REST = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
# The flood's stance: sunk 12 cm on bent legs and slumped 4 degrees toward its foe, over the stage's own sink and
# tilt (creatures.json phases.flood): idle_flood rocks about it, and every clip the flood plays starts and ends on it.
FLOOD = ((4.0, 0.0, 0.0), (0.0, -0.12, 0.0))


def _leg_out(i: int, deg: float) -> tuple[float, float, float]:
    """A rotation that swings leg i up (+deg) or down about the horizontal axis across it (tangential at its hip)."""
    a = (i + 0.5) * 2.0 * math.pi / 6.0
    return (-deg * math.cos(a), 0.0, deg * math.sin(a))


def _rope_sway(deg: float) -> tuple[float, float, float]:
    """A rotation of the rope sideways (about the horizontal radial axis at its azimuth), clear of the bell."""
    a = D(ROPE_AZ)
    return (deg * math.sin(a), 0.0, deg * math.cos(a))


def _tip(rz: float, rx: float, pivot_x: float, pivot_z: float, pivot_y: float = LIP_Y) -> tuple[tuple, tuple]:
    """Rotation (rx, 0, rz) of the whole bell about a point on its lip, as a root rotation and offset."""
    R = ck.euler(rx, 0.0, rz)
    p = np.array([pivot_x, pivot_y, pivot_z])
    off = p - R @ p
    return (rx, 0.0, rz), tuple(off)


# How a move arrives at a key: eased in and out (a hold at the key), accelerating into it (a blow landing: it is
# still at full speed on the contact frame), leaving it fast and slowing (a recoil, a bounce), or between.
EASES = {"s": lambda u: u * u * (3.0 - 2.0 * u), "in": lambda u: u * u, "out": lambda u: 1.0 - (1.0 - u) ** 2,
         "in_s": lambda u: 0.5 * u * u + 0.5 * u * u * (3.0 - 2.0 * u)}


def body(c: ck.Clip, rows, stance=REST) -> None:
    """Keys the whole bell (the root) relative to `stance`: rows (t, rx, rz, lift[, ease[, ry[, z]]]), each arriving by
    its ease (EASES), keyed at every baked frame so the ease is what plays."""
    rows = [tuple(r) + ("s", 0.0, 0.0)[len(r) - 4:] for r in rows]
    (sx, sy, sz), (lx, ly, lz) = stance

    def at(r) -> tuple:
        return np.array([sx + r[1], sy + r[5], sz + r[2]]), np.array([lx, ly + r[3], lz + r[6]])

    frames = range(int(rows[0][0] * ck.FPS), int(rows[-1][0] * ck.FPS) + 1)
    ts = sorted({r[0] for r in rows} | {f / ck.FPS for f in frames if rows[0][0] <= f / ck.FPS <= rows[-1][0]})
    for t in ts:
        k = max(j for j, r in enumerate(rows) if r[0] <= t)
        if k == len(rows) - 1:
            rot, loc = at(rows[k])
        else:
            a, b = rows[k], rows[k + 1]
            e = EASES[b[4]]((t - a[0]) / (b[0] - a[0]))
            (r0, l0), (r1, l1) = at(a), at(b)
            rot, loc = r0 + (r1 - r0) * e, l0 + (l1 - l0) * e
        c.key("root", t, tuple(rot), tuple(loc))


def osc(c: ck.Clip, bone: str, t0: float, t1: float, amp, f0: float, f1: float, a0: float = 1.0,
        a1: float = 1.0) -> None:
    """A tremor of `bone` between t0 and t1 (zero at both): a swing of `amp` degrees (rx, ry, rz) at f0 rising or
    falling to f1 Hz, its size a0 -> a1 (times `amp`), keyed at each swing's peak (the keys ease, so it is smooth)."""
    c.key(bone, t0)
    t, sign = t0 + 0.25 / f0, 1.0
    while True:
        u = (t - t0) / (t1 - t0)
        f = f0 + (f1 - f0) * u
        if t > t1 - 0.25 / f:
            break
        e = a0 + (a1 - a0) * u
        c.key(bone, t, tuple(sign * e * v for v in amp))
        sign = -sign
        t += 0.5 / f
    c.key(bone, t1)


def end_on(c: ck.Clip, src: ck.Clip, t_src: float = 0.0) -> None:
    """Keys every bone either clip moves to `src`'s pose at `t_src`, at `c`'s end (no pop into it)."""
    for b in sorted(set(c.keys) | set(src.keys)):
        r, loc = src.sample(b, t_src)
        c.key(b, c.length, tuple(r), tuple(loc))


def slam(name: str, stance) -> ck.Clip:
    """Hood Slam: it dips, rears up on its hind legs with the crown thrown back (0.14-0.62 s, the tell), hangs, and
    drops forward, gathering speed, to slam the rim down at 0.8 s; the impact jolts the bell and the rim rings,
    and it settles heavily. From the flood stance the drop is shallower (the rim is already low)."""
    c = ck.Clip(name, 1.6)
    hit_rx, hit_lift = (12.5, -0.07) if stance is REST else (8.5, -0.02)
    body(c, ((0.0, 0.0, 0.0, 0.0), (0.14, 2.5, 0.0, -0.035), (0.48, -12.0, 0.0, 0.24), (0.62, -13.5, 0.0, 0.27),
             (0.8, hit_rx, 0.0, hit_lift, "in_s"), (0.9, hit_rx - 2.5, 0.0, hit_lift + 0.02, "out"),
             (1.05, hit_rx - 1.5, 0.0, hit_lift), (1.3, 3.0, 0.0, 0.0), (1.6, 0.0, 0.0, 0.0)), stance)
    osc(c, "bell", 0.8, 1.2, (1.4, 0.0, 0.5), 7.0, 6.0, 1.0, 0.0)
    osc(c, "rim", 0.8, 1.35, (0.0, 0.0, 1.8), 6.5, 6.0, 1.0, 0.0)
    for t, r in ((0.0, 0.0), (0.14, -3.0), (0.62, -12.0), (0.85, 20.0), (1.15, -7.0), (1.6, 0.0)):
        c.key("rope1", t, (r, 0, 0))
        c.key("rope2", t, (r * 0.5, 0, 0))
    return c


def build_clips() -> tuple[list[ck.Clip], dict]:
    """The clips, and per clip how its feet are planted (`plant_feet`)."""
    plant: dict = {}
    idle = ck.Clip("idle", 3.2, loop=True)
    idle.wave("bell", amp_rot=(1.0, 0.0, 1.5), cycles=1)
    idle.wave("rope0", amp_rot=_rope_sway(2.0), cycles=1, phase=0.6)
    idle.wave("rope1", amp_rot=_rope_sway(3.0), cycles=1, phase=1.2)
    idle.wave("rope2", amp_rot=_rope_sway(4.0), cycles=1, phase=1.8)
    idle.wave("mass", amp_loc=(0.0, 0.012, 0.0), cycles=2)
    plant["idle"] = {"steps": [(1, 0.6, 1.2, 0.05, 0.0, 0.0), (4, 2.0, 2.6, 0.05, 0.0, 0.0)]}  # two shift their grip

    # ready: an alert hold, lifted 10 cm on braced legs and leaning 6 degrees at its foe, its weight shifting side to
    # side, the rim shivering, the rope swinging quicker; a loop
    ready = ck.Clip("ready", 2.0, loop=True)
    ready.wave("root", amp_rot=(0.8, 0.0, 1.4), amp_loc=(0.0, 0.015, 0.0), base_rot=(6.0, 0.0, 0.0),
               base_loc=(0.0, 0.10, 0.0), cycles=1)
    ready.wave("bell", amp_rot=(0.5, 0.0, 0.9), cycles=2, phase=0.5)
    osc(ready, "rim", 0.0, 2.0, (0.0, 0.0, 0.45), 5.0, 5.0)
    ready.wave("rope1", amp_rot=_rope_sway(5.0), cycles=2, phase=0.8)
    ready.wave("rope2", amp_rot=_rope_sway(7.0), cycles=2, phase=1.4)
    ready.wave("mass", amp_loc=(0.0, 0.015, 0.0), cycles=2)

    attack = slam("attack", REST)

    cast = ck.Clip("cast", 1.8)  # the generic swing (no skill plays it now; idle_b echoes it)
    for t, rx, rz in ((0.0, 0, 0), (0.5, -13, 2), (1.0, 15, -2), (1.15, 13, -1.5), (1.4, -6, 1), (1.8, 0, 0)):
        cast.key("bell", t, (rx, 0, rz))
    for t, s in ((0.95, 0.0), (1.0, 1.0), (1.05, -1.0), (1.1, 0.8), (1.15, -0.6), (1.2, 0.4), (1.3, 0.0)):
        cast.key("rim", t, (0.0, 0.0, 1.2 * s))
    for t, r in ((0.0, 0), (0.5, 12), (1.0, -22), (1.4, 8), (1.8, 0)):
        cast.key("rope1", t, (r, 0, 0))
        cast.key("rope2", t, (r * 0.4, 0, 0))

    # The Toll: a short dip toward its foe, then it rocks far back on its legs (the crown 0.7 m back), hangs, and swings
    # the whole bell through: the rim rings at 1.0 s (the shockwave and the toll's sound), and it rocks back and forth
    # to rest while the bronze keeps trembling
    toll = ck.Clip("toll", 2.4)
    body(toll, ((0.0, 0.0, 0.0, 0.0), (0.16, 3.0, 0.0, -0.03), (0.62, -15.0, 1.5, 0.09), (0.78, -16.5, 1.8, 0.10),
                (1.0, 13.0, -1.0, -0.03, "in_s"), (1.14, 10.0, -0.6, -0.01, "out"), (1.38, -6.0, 0.5, 0.03),
                (1.65, 3.5, -0.3, 0.0), (1.95, -1.5, 0.0, 0.0), (2.4, 0.0, 0.0, 0.0)))
    osc(toll, "bell", 1.0, 2.4, (0.6, 0.0, 1.0), 6.0, 5.0, 1.5, 0.0)
    osc(toll, "rim", 1.0, 1.9, (0.0, 0.0, 2.0), 6.5, 6.0, 1.0, 0.0)
    for t, r in ((0.0, 0.0), (0.16, -3.0), (0.7, 14.0), (1.02, -24.0), (1.4, 10.0), (1.8, -4.0), (2.4, 0.0)):
        toll.key("rope1", t, (r, 0, 0))
        toll.key("rope2", t, (r * 0.45, 0, 0))

    # Gathering Toll (the two-turn tell before the Toll): it settles low, steps its legs out wide and braces, then tips
    # slowly back (9 degrees) while the bronze trembles faster and harder; the charge locks at 1.6 s (BattleBossVfx's
    # rim glow, BattleBossChoreo's gather sway), it holds, and lets go back up to its stance
    gather = ck.Clip("toll_gather", 2.6)
    body(gather, ((0.0, 0.0, 0.0, 0.0), (0.55, 1.0, 0.0, -0.08), (0.9, 0.0, 0.0, -0.085), (1.6, -9.0, 0.8, -0.07),
                  (2.15, -9.5, 0.9, -0.07), (2.6, 0.0, 0.0, 0.0)))
    osc(gather, "bell", 0.6, 2.5, (0.3, 0.0, 1.0), 2.0, 7.0, 0.3, 1.3)
    osc(gather, "rim", 0.6, 2.4, (0.0, 0.0, 1.0), 3.0, 7.0, 0.2, 1.0)
    gather.wave("rope2", amp_rot=_rope_sway(2.0), cycles=3)
    plant["toll_gather"] = {"steps": [(i, 0.12 + 0.18 * (i % 2), 0.42 + 0.18 * (i % 2), 0.06, 0.0, 0.07)
                                      for i in range(6)]
                            + [(i, 2.12 + 0.14 * (i % 2), 2.42 + 0.14 * (i % 2), 0.05, 0.07, 0.0) for i in range(6)]}

    # the blow rocks the whole bell back on its legs (peak at 0.13 s: a hit snaps in at 0.067 s), the rim jolts and
    # rings, the front feet shuffle (lift and grip again) and it settles
    hit = ck.Clip("hit", 0.6)
    body(hit, ((0.0, 0.0, 0.0, 0.0), (0.13, -9.0, 3.5, 0.05, "out"), (0.3, 3.0, -1.0, 0.0), (0.44, -1.0, 0.4, 0.0),
               (0.6, 0.0, 0.0, 0.0)))
    osc(hit, "rim", 0.06, 0.56, (0.0, 0.0, 2.2), 5.0, 5.0, 1.0, 0.0)
    for t, rx in ((0.0, 0.0), (0.1, 0.0), (0.2, -1.6), (0.36, 0.8), (0.6, 0.0)):
        hit.key("bell", t, (rx, 0.0, 0.0))
    for t, r in ((0.0, 0.0), (0.13, 9.0), (0.32, -5.0), (0.6, 0.0)):
        hit.key("rope1", t, (r, 0, 0))
    hit_steps = [(0, 0.06, 0.3, 0.05), (5, 0.12, 0.36, 0.045), (1, 0.2, 0.44, 0.035)]
    plant["hit"] = {"steps": [(i, a, b, h, 0.0, 0.0) for i, a, b, h in hit_steps]}
    hit_b = ck.varied(hit, "hit_b", **ck.HIT_B)  # the kit's mirrored, heavier hit, its shuffle on the mirrored legs
    plant["hit_b"] = {"steps": [(MIRROR_LEG[i], a, b, h * 1.2, 0.0, 0.0) for i, a, b, h in hit_steps]}

    # the flood's stance: lower, slumped toward its foe, a slow heavy wallow and a bob in the water; a loop
    flood = ck.Clip("idle_flood", 3.6, loop=True)
    flood.wave("root", amp_rot=(1.5, 0.0, 2.6), amp_loc=(0.0, 0.02, 0.0), base_rot=FLOOD[0], base_loc=FLOOD[1],
               cycles=1)
    flood.wave("bell", amp_rot=(0.6, 0.0, 0.8), cycles=2)
    flood.wave("mass", amp_loc=(0.0, 0.01, 0.0), cycles=1, phase=2.0)
    flood.wave("rope1", amp_rot=(4.0, 0.0, 6.0), cycles=1, phase=0.9)
    flood.wave("rope2", amp_rot=(6.0, 0.0, 9.0), cycles=1, phase=1.5)

    # The Flood (phase change): the blow that brings it jolts it, the bronze shudders harder and the legs scrabble
    # for grip, then they give: it lurches forward and sinks low on bent legs, rocks, and settles into the flood stance
    # (the stage sinks and tilts it into the rising water over the same 2.4 s, creatures.json)
    phase = ck.Clip("phase_change", 2.4)
    body(phase, ((0.0, 0.0, 0.0, 0.0), (0.18, -5.0, 2.0, 0.03, "out"), (0.45, 1.5, -0.5, 0.0), (1.0, 0.0, 0.0, -0.02),
                 (1.3, 8.0, -1.5, -0.17, "in"), (1.6, 5.5, 0.5, -0.13, "out"), (2.0, 3.5, -0.3, -0.125)))
    osc(phase, "bell", 0.3, 2.0, (0.6, 0.0, 1.4), 5.0, 7.0, 1.0, 0.2)
    osc(phase, "rim", 0.2, 1.7, (0.0, 0.0, 1.6), 6.0, 6.5, 1.0, 0.3)
    for t, r in ((0.0, 0.0), (0.18, 10.0), (0.6, -6.0), (1.3, 16.0), (1.7, -8.0)):
        phase.key("rope1", t, (r, 0, 0))
    end_on(phase, flood)
    plant["phase_change"] = {"steps": [(1, 0.45, 0.65, 0.05, 0.0, 0.0), (4, 0.58, 0.78, 0.05, 0.0, 0.0),
                                       (0, 0.7, 0.9, 0.05, 0.0, 0.0), (3, 0.82, 1.02, 0.04, 0.0, 0.0)]}

    # Floodtide: it heaves itself up out of its crouch, the front legs lifting high, hangs, and drops hard, stamping,
    # so the water bursts out from under the rim at 1.0 s; it bounces and sinks back into the flood stance
    flood_surge = ck.Clip("flood_surge", 2.0)
    body(flood_surge, ((0.0, 0.0, 0.0, 0.0), (0.45, -3.0, 0.0, 0.19), (0.72, -4.0, 0.0, 0.22),
                       (1.0, 2.0, 0.0, -0.06, "in"), (1.12, 1.0, 0.0, -0.035, "out"), (1.3, 1.5, 0.0, -0.05),
                       (2.0, 0.0, 0.0, 0.0)), FLOOD)
    osc(flood_surge, "bell", 1.0, 1.45, (1.2, 0.0, 0.4), 7.0, 6.0, 1.0, 0.0)
    osc(flood_surge, "rim", 1.0, 1.5, (0.0, 0.0, 1.4), 6.5, 6.0, 1.0, 0.0)
    for t, r in ((0.0, 0.0), (0.6, -10.0), (1.02, 14.0), (1.4, -5.0), (2.0, 0.0)):
        flood_surge.key("rope1", t, (r, 0, 0))
    end_on(flood_surge, flood)
    plant["flood_surge"] = {"steps": [(0, 0.3, 0.98, 0.14, 0.0, 0.0), (5, 0.36, 1.0, 0.14, 0.0, 0.0),
                                      (1, 0.42, 1.0, 0.08, 0.0, 0.0), (4, 0.46, 1.0, 0.08, 0.0, 0.0)]}

    # Undertow Surge: a heavy turn away (it twists 14 degrees on its planted legs and leans), then it hauls round the
    # other way and back, dragging: the pull lands at 1.3 s, and the drag carries on before it settles
    undertow = ck.Clip("undertow_surge", 2.4)
    body(undertow, ((0.0, 0.0, 0.0, 0.0), (0.7, 2.0, 3.0, -0.02, "s", -12.0, 0.0),
                    (1.0, 1.0, 3.0, -0.02, "s", -14.0, 0.02), (1.3, -5.0, -2.5, 0.03, "in_s", 10.0, -0.07),
                    (1.55, -4.0, -3.0, 0.03, "out", 12.0, -0.08), (1.9, -1.0, -1.0, 0.0, "s", 4.0, -0.03),
                    (2.4, 0.0, 0.0, 0.0)), FLOOD)
    for t, rz in ((0.0, 0.0), (1.0, -1.5), (1.4, 2.0), (1.9, -0.6), (2.4, 0.0)):
        undertow.key("bell", t, (0.0, 0.0, rz))
    for t, r in ((0.0, 0.0), (0.8, 12.0), (1.35, -18.0), (1.9, 6.0), (2.4, 0.0)):
        undertow.key("rope1", t, _rope_sway(r))
        undertow.key("rope2", t, _rope_sway(r * 1.3))
    end_on(undertow, flood)

    # Rouse the Spawn: it tips its mouth down toward the ground and knocks the rim on it three times, a call to the
    # spawn (the second knock at 1.2 s); each knock rings the rim
    rouse = ck.Clip("rouse_polyp", 2.2)
    body(rouse, [(t, rx, 0.0, 0.0, ease) for t, rx, ease in (
        (0.0, 0.0, "s"), (0.55, 4.5, "s"), (0.8, 3.0, "out"), (0.92, 6.5, "in"), (1.05, 3.0, "out"), (1.2, 7.0, "in"),
        (1.35, 3.0, "out"), (1.5, 6.5, "in"), (1.8, 2.0, "out"), (2.2, 0.0, "s"))], FLOOD)
    for t0 in (0.92, 1.2, 1.5):
        osc(rouse, "rim", t0, t0 + 0.26, (0.0, 0.0, 1.2), 7.0, 7.0, 1.0, 0.0)
    for t, r in ((0.0, 0.0), (0.55, 8.0), (1.0, -4.0), (1.6, 6.0), (2.2, 0.0)):
        rouse.key("rope1", t, (r, 0, 0))
    end_on(rouse, flood)

    ko = ck.Clip("ko", 2.6)  # from the flood stance it tips onto its side about the lip and slides seaward (+x)
    for t, rz, slide, drop in ((0.0, 0.0, 0.0, 0.0), (0.5, -6.0, 0.0, 0.0), (1.2, -30.0, 0.05, 0.08),
                               (1.9, -68.0, 0.15, 0.24), (2.2, -76.0, 0.2, 0.3), (2.6, -74.0, 0.22, 0.29)):
        rx = FLOOD[0][0] * (1.0 - ck.smoothstep(0.0, 1.2, t))
        rot, off = _tip(rz, float(rx), RIM_R, 0.0)
        ko.key("root", t, rot, (off[0] + slide, off[1] - drop + FLOOD[1][1], off[2]))
    for i, leg_ in enumerate(LEGS):
        ko.key(f"{leg_}_a", 0.0)
        ko.key(f"{leg_}_a", 1.4, _leg_out(i, 4.0))
        ko.key(f"{leg_}_a", 2.6, _leg_out(i, 6.0))
        ko.key(f"{leg_}_b", 0.0)
        ko.key(f"{leg_}_b", 1.4, _leg_out(i, 50.0))
        ko.key(f"{leg_}_b", 2.6, _leg_out(i, 62.0))
    plant["ko"] = {"weight": lambda i, t: 1.0 - float(ck.smoothstep(0.2, 1.0, t))}  # the legs let go

    # intro: it starts sunk in the shallows, tilted, its legs folded up; the legs unfold and reach down to grip, it
    # heaves itself up past its full height, draws back and swings to toll once (the ring at about 2.02 s; presentation
    # owns the strike-ring) and settles on idle's first frame
    intro = ck.Clip("intro", 2.8)
    body(intro, ((0.0, -4.0, 7.0, -0.2), (0.35, -3.0, 6.0, -0.19), (0.8, 0.0, 3.0, -0.12), (1.15, 2.0, -1.5, 0.1),
                 (1.4, 0.0, 0.5, 0.04), (1.55, -2.0, 0.0, 0.06), (1.8, -8.0, 0.0, 0.07),
                 (2.02, 6.0, 0.0, -0.02, "in_s"),
                 (2.25, -2.5, 0.0, 0.0, "out"), (2.5, 1.0, 0.0, 0.0)))
    for t, mass_y in ((0.0, 0.05), (0.45, 0.05), (1.0, 0.0)):
        intro.key("mass", t, (0, 0, 0), (0.0, mass_y, 0.0))
    osc(intro, "rim", 2.02, 2.5, (0.0, 0.0, 1.0), 6.0, 6.0, 1.0, 0.0)
    for t, r in ((0.0, -10.0), (0.9, 6.0), (1.5, -3.0), (1.85, 4.0), (2.08, -8.0), (2.45, 3.0)):
        intro.key("rope1", t, _rope_sway(r))
        intro.key("rope2", t, _rope_sway(r * 1.4))
    end_on(intro, idle)
    # its feet start tucked in and up under the rim, and reach out and down to their grips, one after another
    lag = [0.05 * ((i * 3) % 6) for i in range(6)]
    plant["intro"] = {"steps": [(i, 0.42 + lag[i], 0.95 + lag[i], 0.05, -0.14, 0.0, 0.1, 0.0) for i in range(6)]}
    idle_b = ck.varied(cast, "idle_b", **ck.IDLE_B)  # the kit's fidget (a small quick echo of the swing), planted

    clips = [idle, ready, intro, attack, cast, hit, ko, phase, flood, toll, gather, flood_surge, undertow, rouse,
             hit_b, idle_b, slam("attack_flood", FLOOD), ck.in_pose(hit, "hit_flood", pose_dict(FLOOD)),
             ck.in_pose(ready, "ready_flood", pose_dict(FLOOD))]
    plant["hit_flood"] = plant["hit"]
    return clips, plant


def pose_dict(stance) -> dict:
    return {"root": (np.asarray(stance[0], float), np.asarray(stance[1], float))}


# ---------------------------------------------------------------------------------------------
# Planted feet (M3-CRB-013)
# ---------------------------------------------------------------------------------------------
def _axis_rot(k: np.ndarray, rad: float) -> np.ndarray:
    k = k / np.linalg.norm(k)
    K = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    return np.eye(3) + math.sin(rad) * K + (1.0 - math.cos(rad)) * (K @ K)


def _euler_of(R: np.ndarray) -> np.ndarray:
    """The kit's Euler degrees (X, then Y, then Z about the rest axes) of a rotation."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    return np.degrees([math.atan2(R[2, 1], R[2, 2]), b, math.atan2(R[1, 0], R[0, 0])])


class LegIK:
    """Two-bone IK for leg i: the femur turns about the vertical (to face the foot) and about the axis across it, the
    tibia about the same axis at the knee, so the leg stays in its upright plane and the knee keeps pointing up."""

    def __init__(self, rig: ck.Rig, i: int) -> None:
        a, b = rig.bones[rig.index(f"leg{i}_a")], rig.bones[rig.index(f"leg{i}_b")]
        self.H, self.K, self.F = (np.asarray(p, float) for p in (a.head, b.head, b.tail))
        self.u = leg_frame(i)
        self.n = np.cross(self.u, Y)
        self.v1, self.v2 = self.K - self.H, self.F - self.K
        self.L1, self.L2 = float(np.linalg.norm(self.v1)), float(np.linalg.norm(self.v2))
        self.g0 = self._ang(self.v2) - self._ang(self.v1)

    def _ang(self, v: np.ndarray) -> float:
        return math.atan2(float(v @ Y), float(v @ self.u))

    def solve(self, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Euler degrees of the femur and the tibia that put the foot at `target` (in the mass's rest frame); a target
        out of reach gets the nearest the leg can do."""
        d = target - self.H
        dist = float(np.clip(np.linalg.norm(d), abs(self.L1 - self.L2) + 1e-4, self.L1 + self.L2 - 1e-4))
        cg = (dist * dist - self.L1 ** 2 - self.L2 ** 2) / (2.0 * self.L1 * self.L2)
        g = math.copysign(math.acos(max(-1.0, min(1.0, cg))), self.g0)
        Rb = _axis_rot(self.n, g - self.g0)
        w = self.v1 + Rb @ self.v2
        dh = d - (d @ Y) * Y
        dhl = float(np.linalg.norm(dh))
        psi = math.atan2(float(Y @ np.cross(self.u, dh)), float(self.u @ dh)) if dhl > 1e-6 else 0.0
        alpha = math.atan2(float(d @ Y), dhl) - self._ang(w)
        Ra = _axis_rot(Y, psi) @ _axis_rot(self.n, alpha)
        return _euler_of(Ra), _euler_of(Rb)


def _foot_offset(steps: list, i: int, t: float) -> np.ndarray:
    """Leg i's foot target offset from its rest grip at `t`: each step (leg, t0, t1, height, out0, out1[, up0, up1])
    lifts the foot by an arc of `height` and moves it out from its grip by out0 -> out1 (and up by up0 -> up1); before
    a leg's first step its foot holds that step's start."""
    off = None
    for s in sorted((s for s in steps if s[0] == i), key=lambda s: s[1]):
        _leg, t0, t1, h, o0, o1 = s[:6]
        y0, y1 = s[6:8] if len(s) > 6 else (0.0, 0.0)
        if t < t0:
            off = (o0, y0) if off is None else off
            break
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            e = float(ck.smoothstep(0.0, 1.0, u))
            off = (o0 + (o1 - o0) * e, y0 + (y1 - y0) * e + h * math.sin(math.pi * u))
            break
        off = (o1, y1)
    out, up = off or (0.0, 0.0)
    return leg_frame(i) * out + Y * up


def plant_feet(rig: ck.Rig, meshes: list[ck.Mesh], clips: list[ck.Clip], plant: dict) -> list[ck.Clip]:
    """Re-keys both bones of every leg at every baked frame so its foot stays on its grip (its rest position on the
    floor, or where the clip's steps move it), blended with the authored legs by the clip's `weight` (i, t)."""
    poser = gr.Poser(rig, meshes)
    iks = [LegIK(rig, i) for i in range(6)]
    mass = rig.index("mass")
    leg_bones = {f"{leg_}_{s}" for leg_ in LEGS for s in "ab"}
    out = []
    for clip in clips:
        spec = plant.get(clip.name, {})
        weight = spec.get("weight", lambda i, t: 1.0)
        fixed = ck.Clip(clip.name, clip.length, loop=clip.loop)
        fixed.keys = {b: list(ks) for b, ks in clip.keys.items() if b not in leg_bones}
        for t in gr.frame_times(clip):
            pose = gr.pose_at(clip, poser.names, t)
            Mi = np.linalg.inv(poser.matrices(pose)[mass])
            for i, ik in enumerate(iks):
                goal = ik.F + _foot_offset(spec.get("steps", []), i, t)
                ra, rb = ik.solve((Mi @ np.r_[goal, 1.0])[:3])
                w = float(weight(i, t))
                for b, r in ((f"leg{i}_a", ra), (f"leg{i}_b", rb)):
                    fixed.key(b, t, tuple(np.asarray(pose[b][0]) * (1.0 - w) + r * w))
        out.append(fixed)
    return out


def _outward(i: int) -> tuple[float, float, float]:
    """The Euler weights of a turn that swings leg i up about its own outward axis (as `_leg_out` keys it)."""
    return _leg_out(i, 1.0)


def _rope_up() -> tuple[float, float, float]:
    """The same for the rope: a turn that lifts its trailing end, about the horizontal axis across its azimuth."""
    a = math.radians(ROPE_AZ)
    return (-math.cos(a), 0.0, math.sin(a))


# Kept off the floor (M3-CRE-632, common/grounding.py): where a foot would still dip through the floor, that leg swings
# up about its outward axis the least it takes; the rope's trailing end rides up over the floor as the bell sways; and
# where the rim or the mass would touch down past the floor (the slam, the knocks, the KO, the intro's low start), the
# bell lifts the least it takes, so the rim lands on the floor (the rim is an extra mesh, measured with the body).
GROUNDED_LIMBS = [(f"{leg}_a", _outward(i), 1.0, 45.0) for i, leg in enumerate(LEGS)] + [
    ("rope2", _rope_up(), 1.0, 60.0), ("root", gr.LIFT, 1.0, 0.3)]


def export_clips(rig: ck.Rig, meshes: list[ck.Mesh]) -> list[ck.Clip]:
    """Plant the feet, keep everything on the floor (which may lift the bell), plant the feet again under the lifted
    bell, and take any foot that still dips off the floor."""
    clips, plant = build_clips()
    clips = plant_feet(rig, meshes, gr.grounded(rig, meshes, plant_feet(rig, meshes, clips, plant), GROUNDED_LIMBS),
                       plant)
    return gr.grounded(rig, meshes, clips, GROUNDED_LIMBS[:-1])


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh, extra = build_meshes(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, [mesh] + extra), args.out, extra_meshes=extra,
                              extras={"hymn_creature": "drownbell"})
    print(f"drownbell: {info}")


if __name__ == "__main__":
    main()
