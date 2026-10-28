"""Hullgnaw, the Ch1 boss (M3-CRE-02; final pass M3-CRB-002): docs/kb/art/creatures/act1/hullgnaw.md.

blender --background --factory-startup --python assets_src/creatures/hullgnaw/build_hullgnaw.py -- \
    --out assets/creatures/hullgnaw/hullgnaw.glb

An Undertow-spawn eel grown through a sunken ship's hull: a thick black arch rising out of the water and falling
forward. The body is an eel's (a laterally pressed section, a torn dorsal fin, a paler slate belly, a lateral line,
skin bunched in folds where the frames pinch it, hull-rub scars and barnacle crusts), swollen between five ship's
frames that ring it. Where it swelled the skin split: open seams, recessed, lipped, glowing spawn_wound from inside
(the weak point; the largest, between the fourth and fifth frames, faces the party). The frames are squared oak
timbers (adzed faces, treenail holes, iron spikes bleeding rust, splintered salt-pale ends, weed hanging), a few
stubs of hull planking still nailed across them; they are their own mesh, `Ribs`, which the `breaking` phase throws
off. The head is a skull: brow ridges over pinpoint eyes, nostril pits, gill slits, and a lower jaw too wide for it,
lipped, set with irregular nail teeth. Where it leaves the water, a frayed collar of weed and foam-wet skin.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 1301
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "spawn_wound": "#3FE0C8",
    "timber_weathered": "#7E6A55", "bone": "#E6DAC0", "foliage_shadow": "#1E4A3A", "deep_teal_shadow": "#0E4A55",
    "laterite": "#A8573A", "volcanic_stone": "#3A3A3F", "coral_stone_weathered": "#B9AE98", "foam_white": "#EEF6F4",
    "overcast_slate": "#6F7E8E", "saltgrass": "#B9B26A",
}.items()}

N_SPINE = 10
RIBS = (0.22, 0.34, 0.46, 0.58, 0.70)  # positions along the spine (0 tail .. 1 head) of the five frames
CTRL = [(0.0, -0.4, -1.3), (0.0, 1.3, -1.25), (0.0, 3.0, -0.6), (0.0, 3.0, 0.5), (0.0, 1.7, 1.15), (0.0, 1.25, 1.55)]
X_AX = np.array([1.0, 0.0, 0.0])

# The body sweep: rings along the arch, columns round it. Column j sits at phi = 2 pi j / NS: 0 is the +X flank (the
# review stage's side view), pi/2 the back (the outside of the arch), pi the -X flank (the flank the battle camera
# sees: the stand-in turns the model 90 degrees so +Z faces the party), 3 pi/2 the belly.
NR, NS = 126, 24
J_BACK, J_BELLY = NS // 4, 3 * NS // 4

# The open seams (ADR 0151: an Undertow-spawn's weak point is open wound seams): (gap between frames k and k+1,
# phi from, phi to, width m). Gap 3 (between the fourth and fifth frames, on the fall of the arch toward the party)
# carries the largest, across the back and down both flanks: `vfx_wound` sits on it.
WOUNDS = (
    (0, -0.55, 1.10, 0.12), (0, 2.05, 3.65, 0.11),
    (1, 0.15, 3.30, 0.14),
    (2, -0.65, 0.95, 0.14), (2, 2.25, 3.80, 0.13),
    (3, -0.80, 3.95, 0.28),
)
# Where on the largest seam vfx_wound sits: on the back, toward the party, a little toward the battle camera's flank.
WOUND_MAIN_PHI = math.pi / 2 + 0.3
HEAD_SCALE = 1.12  # the head's local measurements below are scaled by this


# ---------------------------------------------------------------------------------------------
# The spine curve, measured
# ---------------------------------------------------------------------------------------------
def spine_curve(n: int) -> np.ndarray:
    """The rest arch: out of the water behind, up to 2.8 m, falling forward to a low head facing +Z."""
    return ck.bezier(CTRL, n)


_DU = np.linspace(0.0, 1.0, 4001)
_DC = spine_curve(4001)
_DS = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(_DC, axis=0), axis=1))])
_DT = np.gradient(_DC, axis=0)
_DT /= np.linalg.norm(_DT, axis=1, keepdims=True)
LENGTH = float(_DS[-1])


def s_of_u(u):
    return np.interp(u, _DU, _DS)


def u_of_s(s):
    return np.interp(s, _DS, _DU)


def curve_at(u: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(point, tangent toward the head, dorsal: the outside of the arch) at spine parameter u."""
    c = np.array([np.interp(u, _DU, _DC[:, i]) for i in range(3)])
    t = np.array([np.interp(u, _DU, _DT[:, i]) for i in range(3)])
    t /= np.linalg.norm(t)
    d = np.cross(t, X_AX)
    return c, t, d / np.linalg.norm(d)


S_RIB = np.array([float(s_of_u(u)) for u in RIBS])
S_GAP = 0.5 * (S_RIB[:-1] + S_RIB[1:])


def g(x, w):
    return np.exp(-(np.asarray(x, dtype=np.float64) / w) ** 2)


def base_radius(u):
    u = np.asarray(u, dtype=np.float64)
    body = 0.34 + 0.09 * np.sin(u * math.pi)
    return body * (1.0 - 0.32 * ck.smoothstep(0.72, 1.0, u))


def radius_s(s):
    """The body radius at arclength s: pinched under each frame, swollen between them."""
    s = np.asarray(s, dtype=np.float64)
    pinch = 1.0 - 0.11 * sum(g(s - sr, 0.08) for sr in S_RIB)
    swell = 1.0 + 0.085 * sum(g(s - sg, 0.17) for sg in S_GAP)
    return base_radius(u_of_s(s)) * pinch * swell


def noise1(x, seed: int):
    x = np.atleast_1d(np.asarray(x, dtype=np.float64))
    return ck.value_noise(np.column_stack([x, np.full(len(x), 0.37 * seed), np.full(len(x), 1.7)]), seed)


# ---------------------------------------------------------------------------------------------
# Small geometry helpers (local to this build)
# ---------------------------------------------------------------------------------------------
def orient(P: np.ndarray, T: np.ndarray, C) -> np.ndarray:
    """Winds T outward: away from the per-vertex centres C (a ring's centre), or from one point C (a part's core)."""
    C = np.asarray(C, dtype=np.float64)
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    inner = C if C.ndim == 1 else (C[T[:, 0]] + C[T[:, 1]] + C[T[:, 2]]) / 3.0
    out = (a + b + c) / 3.0 - inner
    if np.sum(np.einsum("ij,ij->i", fn, out) < 0.0) > len(T) / 2:
        return ck.flip(T)
    return T


def loft(rings: list[np.ndarray], cap_start=None, cap_end=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Closed loops (equal vertex counts) joined in order; optional fan caps to a point. Returns P, T, centres."""
    n = len(rings[0])
    P = np.vstack(rings)
    C = np.vstack([np.repeat(r.mean(axis=0)[None], n, axis=0) for r in rings])
    parts = [orient(P, ck.grid_tris(len(rings), n, True), C)]
    for tip, ring, inner in ((cap_start, 0, 1), (cap_end, len(rings) - 1, len(rings) - 2)):
        if tip is None:
            continue
        idx = len(P)
        P = np.vstack([P, np.asarray(tip, dtype=np.float64)[None]])
        C = np.vstack([C, rings[ring].mean(axis=0)[None]])
        r0 = ring * n
        cap = np.array([(r0 + q, idx, r0 + (q + 1) % n) for q in range(n)], dtype=np.int64)
        parts.append(orient(P, cap, rings[inner].mean(axis=0)))
    return P, np.vstack(parts), C


def basis(d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    d = d / np.linalg.norm(d)
    a = np.array([0.0, 1.0, 0.0]) if abs(d[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = np.cross(d, a)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(d, e1)


def nail(base, d, length, width, bend_dir, bend, twist=0.0) -> tuple[np.ndarray, np.ndarray]:
    """A square-sectioned nail (a tooth, a spike's shank): base square, a narrower bent middle, a point."""
    d = d / np.linalg.norm(d)
    e1, e2 = basis(d)
    rows = []
    for t, w, tw in ((-0.012, width, 0.0), (0.55, width * 0.62, twist)):
        c = base + d * length * t + bend_dir * bend * length * max(t, 0.0) ** 2 * 0.6
        a = np.radians(45.0 + tw) + np.arange(4) * math.pi / 2
        rows.append(c + w * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2)))
    tip = base + d * length + bend_dir * bend * length * 0.6
    P = np.vstack(rows + [tip[None]])
    T = [(0, 4, 1), (1, 4, 5), (1, 5, 2), (2, 5, 6), (2, 6, 3), (3, 6, 7), (3, 7, 0), (0, 7, 4)]
    T += [(4, 8, 5), (5, 8, 6), (6, 8, 7), (7, 8, 4)]
    T = np.asarray(T, dtype=np.int64)
    C = np.vstack([np.repeat(base[None], 4, 0), np.repeat((base + d * length * 0.55)[None], 4, 0),
                   (base + d * length * 0.9)[None]])
    return P, orient(P, T, C)


def box(c, e1, e2, e3, h1, h2, h3) -> tuple[np.ndarray, np.ndarray]:
    P = np.array([c + sx * h1 * e1 + sy * h2 * e2 + sz * h3 * e3
                  for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
    T = np.array([(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6),
                  (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)], dtype=np.int64)
    return P, orient(P, T, np.repeat(np.asarray(c)[None], 8, 0))


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def wound_main_point() -> tuple[np.ndarray, np.ndarray, int]:
    """The surface point (and its outward direction) of the largest seam where vfx_wound sits, and its spine bone."""
    s = float(S_GAP[3])
    u = float(u_of_s(s))
    c, _t, d = curve_at(u)
    out = math.cos(WOUND_MAIN_PHI) * X_AX + math.sin(WOUND_MAIN_PHI) * d
    p = c + out * (float(radius_s(s)) * 0.93)
    return p, out, min(int(u * N_SPINE), N_SPINE - 1)


def head_frame(joints: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The head's rotation (columns: x side, y up, z forward) and origin: pitched 30 degrees down."""
    f = np.array([0.0, -math.sin(math.radians(30.0)), math.cos(math.radians(30.0))])
    up = np.cross(f, X_AX)
    R = np.column_stack([X_AX, up, f])
    return R, joints[-1] + f * 0.18


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    joints = spine_curve(N_SPINE + 1)
    for i in range(N_SPINE):
        rig.add(f"spine{i}", joints[i], joints[i + 1], "root" if i == 0 else f"spine{i - 1}")
    R, O = head_frame(joints)
    Rs = R * HEAD_SCALE
    rig.add("jaw", O + Rs @ np.array([0.0, -0.11, -0.24]), O + Rs @ np.array([0.0, -0.15, 0.40]), f"spine{N_SPINE - 1}")
    for k, u in enumerate(RIBS):
        i = min(int(u * N_SPINE), N_SPINE - 1)
        c = spine_curve(201)[int(u * 200)]
        rig.add(f"rib{k}", c, c + np.array([0, 0.3, 0]), f"spine{i}")
    # VFX anchors (unweighted): the weak point, the centre of mass, where the frames burst off
    pw, nw, iw = wound_main_point()
    rig.add("vfx_wound", pw, pw + nw * 0.2, f"spine{iw}")
    cc, _t, _d = curve_at(0.48)
    rig.add("vfx_core", cc, cc + np.array([0.0, 0.25, 0.0]), "spine4")
    cp, _t, dp = curve_at(RIBS[2])
    rig.add("vfx_phase", cp, cp + dp * 0.25, f"spine{int(RIBS[2] * N_SPINE)}")
    return rig, joints


# ---------------------------------------------------------------------------------------------
# The body
# ---------------------------------------------------------------------------------------------
def ring_positions() -> np.ndarray:
    """Arclengths of the body rings: denser across the seams (to open them) and the pinches (to fold them)."""
    s = np.linspace(0.0, LENGTH, 3001)
    y = np.interp(u_of_s(s), _DU, _DC[:, 1])
    uu = u_of_s(s)
    dens = np.where(y < 0.15, 0.45, 1.0) * np.where(uu > 0.96, 0.5, 1.0) * (1.0 + 0.35 * ck.smoothstep(0.74, 0.8, uu))
    dens = dens * (1.0 + 2.4 * sum(g(s - sg, 0.17) for sg in S_GAP) + 0.6 * sum(g(s - sr, 0.1) for sr in S_RIB))
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (dens[1:] + dens[:-1]) * np.diff(s))])
    return np.interp(np.linspace(0.0, cdf[-1], NR), cdf, s)


def wound_fields(s: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(open, lip, spill, core) of the seams at body coordinates (s, phi): open 1 inside a split, lip the swollen
    rolled edge, spill the bruised skin round it, core the bright depth along the split's middle."""
    opn = np.zeros(len(s))
    lip = np.zeros(len(s))
    spill = np.zeros(len(s))
    core = np.zeros(len(s))
    for n, (gi, p0, p1, width) in enumerate(WOUNDS):
        ph = p0 + np.mod(phi - p0, 2.0 * math.pi)
        t = (ph - p0) / (p1 - p0)
        inside = (t >= 0.0) & (t <= 1.0)
        tt = np.clip(t, 0.0, 1.0)
        lens = np.where(inside, np.sin(math.pi * tt) ** 0.6, 0.0)
        line = S_GAP[gi] + 0.045 * np.sin(2.7 * ph + 1.3 * gi + n) + 0.035 * noise1(ph * 2.3 + 5.0 * n, SEED + 40 + n)
        hw = 0.5 * width * lens * (0.72 + 0.28 * noise1(ph * 3.1 + 9.0 * n, SEED + 60 + n)) + 1e-4
        d = np.abs(s - line) / hw
        opn = np.maximum(opn, ck.smoothstep(1.0, 0.75, d) * (lens > 0.08))
        core = np.maximum(core, ck.smoothstep(0.75, 0.1, d) * (lens > 0.08))
        lip = np.maximum(lip, np.exp(-((d - 1.25) / 0.35) ** 2) * lens)
        spill = np.maximum(spill, np.exp(-(np.abs(s - line) / (hw + 0.12)) ** 2) * lens)
    return opn, lip, spill, core


def body(mesh: ck.Mesh, rig: ck.Rig, joints: np.ndarray) -> dict:
    """The eel's body sweep; returns what the frames and crusts are fitted to."""
    s_r = ring_positions()
    u_r = u_of_s(s_r)
    phi = np.arange(NS) * (2.0 * math.pi / NS)
    cph, sph = np.cos(phi), np.sin(phi)
    C, Tn, Dn = [], [], []
    for u in u_r:
        c, t, d = curve_at(float(u))
        C.append(c)
        Tn.append(t)
        Dn.append(d)
    C, Tn, Dn = np.array(C), np.array(Tn), np.array(Dn)
    # the section: pressed from the sides, the belly flatter, a keel line down the back
    rad = radius_s(s_r)
    S = np.repeat(s_r, NS)
    PH = np.tile(phi, NR)
    sx = np.tile(0.86 * cph, NR)
    sy = np.tile(sph * np.where(sph < 0.0, 0.9, 1.0) + 0.08 * g(cph, 0.25) * (sph > 0), NR)
    R = np.repeat(rad, NS)
    centre = np.repeat(C, NS, axis=0)
    D = np.repeat(Dn, NS, axis=0)
    out = np.outer(np.tile(cph, NR), X_AX) + np.tile(sph, NR)[:, None] * D
    P0 = centre + R[:, None] * (sx[:, None] * X_AX + sy[:, None] * D)
    # relief: lumps; skin bunched in folds beside each frame and on the inside of the bends; the lateral line
    lump = ck.fbm(P0 * 2.6, SEED + 1)
    near_rib = sum(g(S - sr, 0.15) for sr in S_RIB)
    belly_side = 0.35 + 0.65 * np.maximum(-np.tile(sph, NR), 0.0)
    patchy = ck.smoothstep(-0.25, 0.3, ck.fbm(P0 * 3.5, SEED + 6))
    fold = np.sin(2.0 * math.pi * S / 0.12 + 1.3 * np.sin(PH) + 3.0 * ck.fbm(P0 * 1.7, SEED + 3)) * (
        0.004 + 0.024 * near_rib * (0.35 + 0.65 * patchy)) * belly_side
    U = u_of_s(S)
    neck = ck.smoothstep(0.74, 0.82, U)  # the neck bunches in folds where it bends down to the head
    crease = np.sin(2.0 * math.pi * S / 0.17 + 1.6 * np.cos(PH) + 4.0 * ck.fbm(P0 * 2.2, SEED + 4))
    fold = fold + crease * 0.028 * neck * (0.3 + 0.7 * patchy) * (0.5 + 0.5 * belly_side)
    lat = np.isin(np.tile(np.arange(NS), NR), (0, NS // 2)).astype(np.float64)
    # healed welts: long raised scars across the flanks and the neck where it dragged against the hull
    welt = np.zeros(len(S))
    for s0, p0, slope in ((S_RIB[4] + 0.35, 2.9, 0.25), (S_RIB[4] + 0.6, 0.9, -0.2), (S_RIB[4] + 0.5, 3.4, 0.3),
                          (S_RIB[1] - 0.05, 3.3, 0.0), (S_RIB[0] - 0.5, 0.4, 0.35), (S_GAP[1] + 0.02, 2.7, -0.25),
                          (S_RIB[0] - 0.8, 2.9, -0.3)):
        dphi = np.angle(np.exp(1j * (PH - p0)))
        welt = np.maximum(welt, g(S - s0 - slope * dphi, 0.045) * g(dphi, 0.55))
    opn, lip, spill, core = wound_fields(S, PH)
    disp = 0.028 * lump + fold - 0.01 * lat - 0.04 * opn - 0.055 * core + 0.045 * lip + 0.018 * welt
    P = P0 + out * disp[:, None]
    T = ck.flip(ck.grid_tris(NR, NS, True))
    T = orient(P, T, centre)
    # colour: lacquer black to abyss navy, a paler slate belly, chafe bands where the frames sat, hull-rub scars,
    # the lateral line's pores, foam-wet near the water, bruised round the seams, glowing inside them
    under = ck.smoothstep(-0.15, -0.75, np.tile(sph, NR))
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.25, 0.35, lump)[:, None])
    col = ck.mix(col, PAL["storm_slate"], (0.85 * under)[:, None])
    chafe = sum(g(S - sr, 0.055) for sr in S_RIB) * (0.55 + 0.45 * ck.smoothstep(-0.3, 0.3, ck.fbm(P0 * 9.0, SEED + 5)))
    col = ck.mix(col, PAL["storm_slate"], (0.55 * np.clip(chafe, 0, 1))[:, None])
    scar_zone = np.clip(sum(g(S - sc, 0.22) * g(PH - pc, 0.5) for sc, pc in
                            ((S_GAP[0] - 0.1, 0.4), (S_GAP[2] + 0.12, 0.2), (S_RIB[3] + 0.3, 5.9),
                             (S_GAP[1], 2.6), (S_RIB[0] - 0.45, 0.9), (S_RIB[0] - 0.6, 2.6))), 0, 1)
    streak = (noise1(np.tile(np.arange(NS), NR) * 7.31, SEED + 9) > 0.1).astype(np.float64)
    scar = scar_zone * streak * ck.smoothstep(-0.2, 0.25, ck.fbm(P0 * np.array([3.0, 3.0, 3.0]), SEED + 11))
    col = ck.mix(col, PAL["overcast_slate"] * 0.8, (0.6 * scar)[:, None])
    col = ck.mix(col, PAL["overcast_slate"] * 0.7, (0.65 * welt)[:, None])
    pores = lat * (np.repeat(np.arange(NR), NS) % 2 == 0)
    col = ck.mix(col, PAL["storm_slate"] * 1.2, (0.6 * lat)[:, None])
    col = ck.mix(col, PAL["overcast_slate"], (0.8 * pores)[:, None])
    wl = ck.smoothstep(0.75, 0.05, P0[:, 1])
    foam = wl * ck.smoothstep(0.1, 0.45, ck.fbm(P0 * np.array([6.0, 2.0, 6.0]), SEED + 13))
    col = ck.mix(col, PAL["foliage_shadow"], (0.45 * wl)[:, None])
    col = ck.mix(col, PAL["foam_white"] * 0.8, (0.55 * foam)[:, None])
    col = ck.mix(col, PAL["abyss_navy"], (0.5 * spill * (1 - opn))[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.1, (0.45 * lip * (1 - opn))[:, None])
    # inside a seam: dark wet flesh at the torn edge, the light coming up from the middle, broken by fibres
    fib = 0.65 + 0.35 * ck.smoothstep(-0.3, 0.3, ck.fbm(P0 * np.array([26.0, 9.0, 26.0]), SEED + 15))
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.6, opn[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.85 * fib[:, None], core[:, None])
    emission = np.clip(0.2 * opn + 0.8 * core * fib, 0.0, 1.0)
    cavity = np.clip(0.12 + 0.5 * (fold < -0.006) * np.clip(near_rib + neck, 0, 1) + 0.35 * chafe +
                     0.8 * np.clip(opn - core, 0, 1) + 0.3 * lat, 0.0, 1.0)
    wet = np.clip(1.0 - 0.35 * chafe - 0.3 * scar, 0.4, 1.0)
    # M3-CRB-002 polish 2: the neck no longer reads as one glossy tube under the battle sun. Its upper ridge has
    # dried to a dull skin, the slime runs down the flanks in streaks (wet and glossy) between drier bands, and the
    # wrinkles' valleys hold cavity, so the sheen breaks up along the folds.
    nk = ck.smoothstep(0.72, 0.8, U) * (1.0 - opn)
    sph_v = np.tile(sph, NR)
    ridge = ck.smoothstep(0.15, 0.8, sph_v)  # the top of the neck, the outside of its bend
    run = ck.fbm(np.column_stack([S * 16.0, np.cos(PH) * 1.2, np.sin(PH) * 1.2]), SEED + 17)
    slime = ck.smoothstep(0.05, 0.3, run) * (1.0 - 0.7 * ridge)
    valley = ck.smoothstep(-0.2, -0.75, crease) * (0.4 + 0.6 * patchy)
    wet_neck = np.clip(0.3 - 0.27 * ridge + 0.65 * slime + 0.12 * valley, 0.03, 1.0)
    wet = wet * (1.0 - nk) + wet_neck * nk
    cavity = np.clip(cavity + nk * (0.45 * valley + 0.12 * (1.0 - slime) * (1.0 - ridge)), 0.0, 1.0)
    col = ck.mix(col, PAL["storm_slate"] * 0.9, (0.3 * nk * ridge * ck.smoothstep(-0.2, 0.3, lump))[:, None])
    skin = rig.chain([f"spine{i}" for i in range(N_SPINE)], joints)
    ck.finish(mesh, P, T, "carapace", col, skin, wet=wet, cavity=cavity, emission=emission)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    return {"P": P, "N": N, "S": S, "PH": PH, "s_r": s_r, "C": C, "D": Dn, "T": Tn, "open": opn, "skin": skin,
            "rad": rad}


def dorsal_fin(mesh: ck.Mesh, bd: dict) -> None:
    """A long, low, torn fin down the back, crushed flat under each frame and split across each seam."""
    P, s_r = bd["P"], bd["s_r"]
    rows, cen, hts = [], [], []
    rng = np.random.default_rng(SEED + 21)
    tears = rng.uniform(S_RIB[0] - 1.2, s_of_u(0.92), 6)
    sel = [k for k in range(NR) if s_of_u(0.08) <= s_r[k] <= s_of_u(0.99)]
    for k in sel:
        s = s_r[k]
        u = float(u_of_s(s))
        base = P[k * NS + J_BACK]
        c, t, d = curve_at(u)
        env = ck.smoothstep(0.08, 0.2, u) * (1.0 - 0.45 * ck.smoothstep(0.78, 0.9, u)) * ck.smoothstep(0.99, 0.95, u)
        crush = np.prod([1.0 - g(s - sr, 0.07) for sr in S_RIB])
        opn, _lip, _sp, _core = wound_fields(np.array([s]), np.array([math.pi / 2]))
        torn = np.prod([1.0 - 0.85 * g(s - tr, 0.05) for tr in tears])
        fray = 0.72 + 0.28 * float(noise1(s * 23.0, SEED + 22)[0])
        h = 0.17 * env * crush * (1.0 - float(opn[0])) * torn * fray
        hts.append(h)
        th = 0.022 * env + 0.004
        tip = base + d * (h + 0.005) - t * h * 0.35
        rows.append(np.array([base - X_AX * th - d * 0.01, tip - X_AX * 0.003, tip + X_AX * 0.003,
                              base + X_AX * th - d * 0.01]))
        cen.append(np.repeat((base + d * h * 0.4)[None], 4, 0))
    Pf = np.vstack(rows)
    Cf = np.vstack(cen)
    Tf = orient(Pf, ck.grid_tris(len(rows), 4, True), Cf)
    hts = np.repeat(np.array(hts), 4)
    edge = np.tile([0.0, 1.0, 1.0, 0.0], len(rows))
    ray = np.repeat((np.arange(len(rows)) % 3 == 0).astype(np.float64), 4)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"] * 1.3, (0.6 * edge)[:, None])
    col = ck.mix(col, PAL["deep_teal_shadow"], (0.35 * edge * ck.smoothstep(0.04, 0.14, hts))[:, None])
    ck.finish(mesh, Pf, Tf, "carapace", col, bd["skin"], wet=1.0, cavity=0.25 + 0.4 * ray * (1 - edge))


def barnacles(mesh: ck.Mesh, bd: dict) -> None:
    """Crusts where it rubbed the hull: beside the frames, on the crown of the arch, at the waterline."""
    rng = np.random.default_rng(SEED + 31)
    P, N, S, PH, opn = bd["P"], bd["N"], bd["S"], bd["PH"], bd["open"]
    sites = []
    for sr in S_RIB:
        for side in (-1.0, 1.0):
            for _ in range(2):
                sites.append((sr + side * rng.uniform(0.1, 0.17), rng.uniform(-0.9, 2.2) if side > 0 else
                              rng.uniform(1.0, 4.0)))
    s_top = float(s_of_u(0.5))
    sites += [(s_top + rng.normal(0, 0.12), math.pi / 2 + rng.normal(0, 0.45)) for _ in range(7)]
    s_neck = float(s_of_u(0.83))
    sites += [(s_neck + rng.normal(0, 0.18), rng.uniform(0.2, 3.0)) for _ in range(8)]
    s_wl = float(s_of_u(0.06))
    sites += [(s_wl + rng.normal(0, 0.15), rng.uniform(0, 2 * math.pi)) for _ in range(9)]
    for st, pt in sites:
        dp = np.abs(np.angle(np.exp(1j * (PH - pt))))
        k = int(np.argmin(np.abs(S - st) + 0.3 * dp))
        if opn[k] > 0.02:
            continue
        cluster = 1 + int(rng.integers(0, 3))
        for _ in range(cluster):
            p, n = P[k], N[k]
            e1, e2 = basis(n)
            off = rng.normal(0, 0.035, 2)
            p = p + e1 * off[0] + e2 * off[1]
            rho = rng.uniform(0.016, 0.042)
            h = rho * rng.uniform(0.55, 1.0)
            a = rng.uniform(0, 2 * math.pi) + np.arange(6) * math.pi / 3
            base = p - n * 0.008 + rho * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2))
            rim = p + n * h + 0.5 * rho * (np.outer(np.cos(a + 0.5), e1) + np.outer(np.sin(a + 0.5), e2))
            pit = p + n * h * 0.4
            Pb = np.vstack([base, rim, pit[None]])
            Tb = [(i, (i + 1) % 6, 6 + i) for i in range(6)] + [((i + 1) % 6, 6 + (i + 1) % 6, 6 + i) for i in range(6)]
            Tb += [(6 + i, 6 + (i + 1) % 6, 12) for i in range(6)]
            Tb = np.asarray(Tb, dtype=np.int64)
            Tb = orient(Pb, Tb, p - n * rho)
            shell = ck.mix(PAL["coral_stone_weathered"] * 0.72, PAL["bone"] * 0.8, rng.uniform(0, 0.5))
            col = np.vstack([np.repeat((shell * 0.75)[None], 6, 0), np.repeat(shell[None], 6, 0),
                             PAL["lacquer_black"][None]])
            cav = np.concatenate([np.full(6, 0.55), np.full(6, 0.1), [1.0]])
            ck.finish(mesh, Pb, Tb, "rib", col, bd["skin"], wet=0.35, cavity=cav)


def waterline_collar(mesh: ck.Mesh, bd: dict) -> None:
    """Where it leaves the water: a frayed skirt of weed-matted, foam-wet skin, and fronds spread on the water."""
    rng = np.random.default_rng(SEED + 41)
    na = 24
    a = np.arange(na) * 2.0 * math.pi / na
    rings = []
    for y, grow, rag in ((0.30, 0.97, 0.0), (0.14, 1.07, 0.03), (0.03, 1.18, 0.06)):
        u = float(np.interp(y, _DC[:400, 1], _DU[:400]))
        c, t, d = curve_at(u)
        r = float(base_radius(u)) * grow
        jit = 1.0 + rag * rng.uniform(-1.0, 1.0, na)
        drop = rag * rng.uniform(-1.2, 0.3, na)
        rings.append(c + (r * jit)[:, None] * (np.outer(np.cos(a) * 0.9, X_AX) + np.outer(np.sin(a), d))
                     - t * drop[:, None] + np.array([0.0, 0.004, 0.0]))
    P = np.vstack(rings)
    cen = np.vstack([np.repeat(r.mean(axis=0)[None], na, 0) for r in rings])
    T = orient(P, ck.grid_tris(3, na, True), cen)
    row = np.repeat([0.0, 0.5, 1.0], na)
    foam = ck.smoothstep(0.0, 0.5, ck.fbm(P * np.array([7.0, 3.0, 7.0]), SEED + 42))
    col = ck.mix(PAL["lacquer_black"], PAL["foliage_shadow"], (0.4 + 0.5 * row)[:, None])
    col = ck.mix(col, PAL["foam_white"] * 0.8, (0.4 * foam * (row > 0.2))[:, None])
    ck.finish(mesh, P, T, "carapace", col, bd["skin"], wet=1.0, cavity=0.2 + 0.4 * row)
    for k in range(9):
        ang = 2.0 * math.pi * k / 9 + rng.uniform(-0.25, 0.25)
        ring = rings[1]
        j = int(round(ang / (2.0 * math.pi) * na)) % na
        p0 = ring[j]
        dirn = np.array([math.cos(ang) * 0.9, 0.0, math.sin(ang)])
        dirn /= np.linalg.norm(dirn)
        reach = rng.uniform(0.25, 0.6)
        side = np.cross(dirn, [0.0, 1.0, 0.0])
        pts = [p0, p0 + dirn * 0.12 + np.array([0, -0.12, 0])]
        for q in range(1, 5):
            w = math.sin(q * 1.4 + k) * 0.06
            pts.append(np.array([p0[0], 0.015, p0[2]]) + dirn * (0.15 + reach * q / 4) + side * w)
        sp = ck.bezier(pts, 7)
        Pw, Tw = ck.tube(sp, np.linspace(0.055, 0.015, 7), 4, squash=0.2, up_hint=(0.0, 1.0, 0.0))
        colw = ck.mix(PAL["foliage_shadow"], PAL["saltgrass"] * 0.55, np.linspace(0.1, 0.6, len(Pw))[:, None])
        ck.finish(mesh, Pw, Tw, "rib", colw, bd["skin"], wet=1.0, cavity=0.3)


def head(mesh: ck.Mesh, rig: ck.Rig, joints: np.ndarray) -> None:
    """A skull: brow ridges over pinpoint eyes, nostril pits, gill slits behind, a wide lipped jaw, nail teeth."""
    R, O = head_frame(joints)
    Rs = R * HEAD_SCALE
    hb_bone = rig.rigid(f"spine{N_SPINE - 1}")
    jaw_bone = rig.rigid("jaw")
    zk = [-0.40, -0.30, -0.18, -0.05, 0.08, 0.22, 0.36, 0.46, 0.53, 0.565]
    wk = [0.21, 0.28, 0.33, 0.35, 0.34, 0.29, 0.23, 0.19, 0.14, 0.05]
    htk = [0.19, 0.23, 0.26, 0.28, 0.29, 0.23, 0.18, 0.15, 0.11, 0.03]
    hbk = [-0.16, -0.15, -0.13, -0.12, -0.12, -0.11, -0.10, -0.09, -0.07, -0.02]
    gills = (-0.355, -0.31, -0.265)
    zs = [-0.40, -0.385] + [z + o for z in gills for o in (-0.013, 0.0, 0.013)] + \
        [-0.22, -0.17, -0.12, -0.07, -0.02, 0.03, 0.07, 0.10, 0.13, 0.17, 0.22, 0.27, 0.32, 0.37, 0.42, 0.46, 0.49,
         0.52, 0.545]
    na = 24
    a = np.arange(na) * 2.0 * math.pi / na
    ca, sa = np.cos(a), np.sin(a)
    pw = 0.6  # a boxy section: the skull's planes, not an egg
    rings_l, info = [], []
    for z in zs:
        w, ht, hb = (float(np.interp(z, zk, v)) for v in (wk, htk, hbk))
        x = w * np.sign(ca) * np.abs(ca) ** pw
        y = np.where(sa >= 0, ht, -hb) * np.sign(sa) * np.abs(sa) ** pw
        zz = np.full(na, z)
        top = sa > 0.15
        xn = np.abs(x) / w
        # a crest down the middle of the skull, carrying the fin's line onto the head
        crest = 0.05 * g(xn, 0.14) * top * ck.smoothstep(0.3, -0.05, z) * ck.smoothstep(-0.42, -0.3, z)
        y = y + crest
        # brow ridges, a heavy overhang over each eye
        brow = 0.08 * g(z - 0.1, 0.09) * g(xn - 0.6, 0.22) * top
        y = y + brow
        x = x + np.sign(x) * 0.04 * g(z - 0.1, 0.08) * g(sa - 0.45, 0.25)
        # cheeks: the jaw muscles bulge behind the eyes, over the hinge
        x = x + np.sign(x) * 0.035 * g(z + 0.1, 0.1) * g(sa + 0.1, 0.35)
        # transverse wrinkles over the bridge of the snout
        y = y + 0.007 * np.sin(z * 95.0) * ck.smoothstep(0.17, 0.3, z) * ck.smoothstep(0.5, 0.42, z) * top
        # eye sockets under the brow
        sock = g(z - 0.13, 0.035) * g(sa - 0.32, 0.18) * (xn > 0.6)
        x = x - np.sign(x) * 0.022 * sock
        # nostril pits on the snout
        nos = g(z - 0.47, 0.025) * g(np.abs(x) - 0.08, 0.03) * top
        y = y - 0.022 * nos
        # gill slits: a groove, its rear lip raised like a flap
        gill = sum(g(z - gz, 0.006) for gz in gills) * g(sa - 0.05, 0.4) * (xn > 0.55)
        flap = sum(g(z - gz - 0.013, 0.006) for gz in gills) * g(sa - 0.05, 0.4) * (xn > 0.55)
        x = x - np.sign(x) * (0.028 * gill - 0.01 * flap)
        # a rolled upper lip along the gape (from the mouth corner forward)
        gape = ck.smoothstep(-0.2, -0.14, z) * g(sa + 0.62, 0.22)
        x = x + np.sign(x) * 0.018 * gape
        # skin wrinkles behind the jaw hinge
        x = x + np.sign(x) * 0.008 * np.sin(z * 70.0) * ck.smoothstep(-0.15, -0.3, z)
        rings_l.append(np.column_stack([x, y, zz]))
        info.append(np.column_stack([np.clip(brow / 0.08 + crest / 0.05, 0, 1), sock, nos, gill, gape,
                                     np.full(na, z), sa]))
    tipl = np.array([0.0, -0.01, 0.58])
    rearl = np.array([0.0, 0.02, -0.43])
    Pl, Tl, _Cl = loft(rings_l, cap_start=rearl, cap_end=tipl)
    inf = np.vstack(info + [np.array([[0, 0, 0, 0, 0, -0.43, 0]]), np.array([[0, 0, 0, 0, 0, 0.58, 0]])])
    brow, sock, nos, gill, gape, zl, sal = inf.T
    lump = ck.fbm(Pl * 7.0, SEED + 51)
    Pl = Pl + 0.006 * lump[:, None] * np.sign(Pl) * np.array([1.0, 0.3, 0.0])
    # warty tubercles over the snout and brow
    wart = ck.smoothstep(0.18, 0.45, ck.fbm(Pl * 16.0, SEED + 52)) * (sal > 0.2) * ck.smoothstep(-0.05, 0.15, zl)
    Pl[:, 1] += 0.016 * wart
    P = Pl @ Rs.T + O
    palate = (sal < -0.55) & (zl > -0.18)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, lump)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 0.9, (0.55 * brow + 0.35 * ck.smoothstep(-0.3, -0.7, sal))[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.2, (0.6 * wart)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.05, (0.6 * gape * ~palate)[:, None])
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.55, palate[:, None].astype(np.float64))
    scars = ck.smoothstep(0.25, 0.4, ck.fbm(Pl * np.array([4.0, 18.0, 4.0]), SEED + 53)) * (sal > -0.3)
    col = ck.mix(col, PAL["overcast_slate"] * 0.75, (0.5 * scars)[:, None])
    cav = np.clip(0.15 + 0.8 * sock + 0.9 * nos + 0.9 * gill + 0.6 * palate, 0, 1)
    ck.finish(mesh, P, Tl, "carapace", col, hb_bone, wet=1.0, cavity=cav)
    # eyes: a pinpoint in each socket, a smaller one behind it
    for sgn in (-1.0, 1.0):
        for z, rr, yy in ((0.13, 0.03, 0.075), (0.045, 0.016, 0.105)):
            w = float(np.interp(z, zk, wk))
            c = O + Rs @ np.array([sgn * (w * 0.97 - 0.004), yy, z])
            Pe, Te = ck.ellipsoid(c, (rr, rr * 0.8, rr), 4, 6)
            ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], hb_bone, wet=1.0, emission=1.0)
    # the lower jaw: wider than the skull, a U-shaped scoop with thick lips, hinged at the jaw bone
    jz = [-0.24, -0.20, -0.14, -0.07, 0.0, 0.08, 0.16, 0.24, 0.32, 0.40, 0.47, 0.53, 0.58, 0.61]
    jwk = ([-0.24, -0.1, 0.05, 0.3, 0.5, 0.6, 0.63], [0.22, 0.37, 0.42, 0.36, 0.27, 0.16, 0.04])
    rings_j, jinfo = [], []
    for z in jz:
        W = float(np.interp(z, *jwk))
        thick = 0.07
        Wi = max(W - thick, 0.0) * ck.smoothstep(0.6, 0.45, z)
        yl = float(np.interp(z, zk, hbk)) - 0.004
        yb = yl - 0.17 * float(ck.smoothstep(0.66, 0.35, z)) * float(ck.smoothstep(-0.3, -0.1, z)) - 0.02
        yf = yl - (0.10 * float(ck.smoothstep(0.55, 0.35, z)) * float(ck.smoothstep(-0.3, -0.12, z)))
        mid = 0.5 * (yl + yb)
        loop = [(-W, yl), (-W - 0.02, yl - 0.035), (-W * 0.97, mid), (-W * 0.86, yb + 0.035), (-W * 0.5, yb),
                (0.0, yb - 0.012), (W * 0.5, yb), (W * 0.86, yb + 0.035), (W * 0.97, mid), (W + 0.02, yl - 0.035),
                (W, yl), (Wi + 0.012, yl - 0.004), (Wi, yl - 0.04), (Wi * 0.95, yf + 0.012), (Wi * 0.5, yf),
                (0.0, yf + 0.008), (-Wi * 0.5, yf), (-Wi * 0.95, yf + 0.012), (-Wi, yl - 0.04), (-Wi - 0.012, yl - 0.004)]
        lp = np.array([(x, y, z) for x, y in loop])
        lp[:, 0] += np.sign(lp[:, 0]) * 0.006 * math.sin(z * 55.0)  # pleats in the jaw's skin
        rings_j.append(lp)
        jinfo.append(np.array([[1.0 if i in (0, 1, 9, 10, 11, 19) else 0.0, 1.0 if 12 <= i <= 18 else 0.0,
                                1.0 if 3 <= i <= 7 else 0.0] for i in range(len(loop))]))
    Pj, Tj, _Cj = loft(rings_j, cap_start=np.array([0.0, -0.2, -0.27]), cap_end=np.array([0.0, -0.13, 0.63]))
    ji = np.vstack(jinfo + [np.zeros((1, 3)), np.zeros((1, 3))])
    lipm, inner, chin = ji.T
    jl = ck.fbm(Pj * 6.0, SEED + 57)
    colj = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, jl)[:, None])
    colj = ck.mix(colj, PAL["storm_slate"] * 0.95, (0.65 * chin)[:, None])
    colj = ck.mix(colj, PAL["storm_slate"] * 1.15, (0.7 * lipm)[:, None])
    colj = ck.mix(colj, PAL["deep_teal_shadow"] * 0.55, inner[:, None])
    ck.finish(mesh, Pj @ Rs.T + O, Tj, "carapace", colj, jaw_bone, wet=1.0, cavity=np.clip(0.15 + 0.7 * inner, 0, 1))
    # nail teeth: upper ones hang from the gape, lower ones splay up from the too-wide jaw; irregular, some missing
    rng = np.random.default_rng(SEED + 59)
    rows = []
    for sgn in (-1.0, 1.0):
        for z in np.linspace(-0.1, 0.44, 9):
            w = float(np.interp(z, zk, wk))
            rows.append(("up", np.array([sgn * (w * 0.86), float(np.interp(z, zk, hbk)) + 0.01, z]),
                         np.array([-sgn * 0.2, -1.0, 0.1])))
        for z in np.linspace(-0.12, 0.5, 10):
            W = float(np.interp(z, *jwk))
            Wi = max(W - 0.07, 0.0)
            rows.append(("lo", np.array([sgn * (Wi + 0.035), float(np.interp(z, zk, hbk)) - 0.02, z]),
                         np.array([sgn * 0.3, 1.0, 0.15])))
    for x in (-0.07, 0.0, 0.07):
        rows.append(("up", np.array([x, -0.06, 0.5]), np.array([0.0, -1.0, 0.35])))
        rows.append(("lo", np.array([x * 1.6, -0.10, 0.57]), np.array([0.0, 1.0, 0.4])))
    for kind, pl, dl in rows:
        if rng.random() < 0.14:
            continue
        broken = rng.random() < 0.18
        length = (rng.uniform(0.09, 0.17) if kind == "lo" else rng.uniform(0.06, 0.12)) * (0.45 if broken else 1.0)
        dl = dl / np.linalg.norm(dl) + rng.normal(0, 0.18, 3)
        base = O + Rs @ pl
        d = R @ dl
        bend = R @ rng.normal(0, 1.0, 3)
        Pt, Tt = nail(base, d, length, rng.uniform(0.013, 0.02), bend / np.linalg.norm(bend),
                      rng.uniform(0.0, 0.5), rng.uniform(-25, 25))
        t = np.array([0, 0, 0, 0, 0.55, 0.55, 0.55, 0.55, 1.0])
        colt = ck.mix(PAL["laterite"] * 0.45, PAL["bone"] * rng.uniform(0.72, 0.92), ck.smoothstep(0.0, 0.6, t)[:, None])
        ck.finish(mesh, Pt, Tt, "rib", colt, jaw_bone if kind == "lo" else hb_bone, wet=0.6,
                  cavity=0.45 * (1 - t), flat=True)


# ---------------------------------------------------------------------------------------------
# The frames (the `Ribs` mesh)
# ---------------------------------------------------------------------------------------------
# per frame: (psi on the -X side, psi on the +X side) where it is broken off (0 is the crown, over the back), and a
# rack (lean along the body, twist) in degrees: no two alike, one snapped at the flank, all splayed where they broke
FRAMES = (
    (-2.30, 1.80, 5.0, -3.0),
    (-1.55, 2.40, -4.0, 4.0),
    (-2.25, 2.20, 7.0, 2.0),
    (-2.45, 1.05, -6.0, -5.0),
    (-1.75, 2.30, 4.0, 6.0),
)
PLANKS = ((1, -1.35, -0.2, 0.3), (2, 1.45, -0.18, 0.26), (4, -1.2, -0.26, 0.24))


def frame_geometry(k: int, bd: dict) -> dict:
    """The frame's centreline and its local axes: psi samples, points, radial and along-body directions."""
    u = RIBS[k]
    s = S_RIB[k]
    c, t, d = curve_at(u)
    psi_l, psi_r, lean, twist = FRAMES[k]
    M = np.column_stack([X_AX, d, t]) @ ck.rot_x(lean) @ ck.rot_y(twist)
    e_x, e_d, e_t = M[:, 0], M[:, 1], M[:, 2]
    # the body's section radius at this frame, per angle, from the nearest body ring
    kr = int(np.argmin(np.abs(bd["s_r"] - s)))
    ring = bd["P"][kr * NS:(kr + 1) * NS]
    rr = np.linalg.norm(ring - bd["C"][kr], axis=1)
    rr = np.maximum(rr, np.roll(rr, 1))
    rr = np.maximum(rr, np.roll(rr, -1))
    psis = np.linspace(psi_l, psi_r, max(int((psi_r - psi_l) / 0.17), 6))
    pts, radial = [], []
    hm = 0.085
    kink = (1.0, 0.85, 1.15, 0.95, 1.1)[k]  # where the futtocks meet (a small step out)
    for psi in psis:
        phi = math.pi / 2 - psi
        rb = float(np.interp(np.mod(phi, 2 * math.pi), np.arange(NS + 1) * 2 * math.pi / NS, np.append(rr, rr[0])))
        rc = rb + 0.03 + hm + 0.012 * (abs(psi) > kink) + 0.16 * float(ck.smoothstep(1.6, 2.5, abs(psi)))
        dirn = math.sin(psi) * e_x + math.cos(psi) * e_d
        pts.append(c + rc * dirn)
        radial.append(dirn)
    return {"c": c, "e_t": e_t, "psis": psis, "pts": np.array(pts), "radial": np.array(radial), "hm": hm,
            "hs": 0.07}


def splinter_rings(end: np.ndarray, tan: np.ndarray, ring: np.ndarray, rng, reach: float = 1.0,
                   pinch: tuple[float, float] = (0.12, 0.6)) -> list[np.ndarray]:
    """Two jagged rings past a broken end: each corner runs on as a splinter of its own length."""
    ext = rng.uniform(0.02, 0.15, len(ring)) * reach
    ext[rng.integers(0, len(ring))] = rng.uniform(0.18, 0.26) * reach
    off = ring - end
    r1 = end + off * 0.9 + np.outer(ext * 0.45, tan)
    r2 = end + off * rng.uniform(*pinch, len(ring))[:, None] + np.outer(ext, tan)
    return [r1, r2]


def weed_strand(mesh: ck.Mesh, p0, out, flat_dir, length: float, rng, bone) -> None:
    """A ribbon of weed hanging from p0: wavy, flat across `flat_dir`, blunt and torn at the end."""
    sway = rng.normal(0, 0.012, 2)
    ph = rng.uniform(0, 2 * math.pi)
    path = [p0]
    for q in range(1, 7):
        f = q / 6
        path.append(p0 + out * 0.05 * min(q, 2) + np.array([sway[0] * q + 0.015 * math.sin(ph + q * 1.9),
                                                            -length * f, sway[1] * q + 0.015 * math.cos(ph + q * 1.6)]))
    sp = np.array(path)
    wdt = np.linspace(rng.uniform(0.045, 0.065), rng.uniform(0.025, 0.04), len(sp))
    Pw, Tw = ck.tube(sp, wdt, 4, cap_start=False, squash=0.18, up_hint=tuple(flat_dir))
    tip = np.linspace(0.0, 1.0, len(sp))
    tip = np.concatenate([np.repeat(tip, 4), [1.0]])[: len(Pw)]
    colw = ck.mix(PAL["foliage_shadow"], PAL["saltgrass"] * 0.6, (0.15 + 0.6 * tip)[:, None])
    ck.finish(mesh, Pw, Tw, "rib", colw, bone, wet=1.0, cavity=0.25)


def ribs(mesh: ck.Mesh, rig: ck.Rig, bd: dict) -> None:
    rng = np.random.default_rng(SEED + 7)
    for k in range(len(RIBS)):
        bone = rig.rigid(f"rib{k}")
        fg = frame_geometry(k, bd)
        pts, radial, e_t, hm, hs, psis = fg["pts"], fg["radial"], fg["e_t"], fg["hm"], fg["hs"], fg["psis"]
        rings, along = [], []
        n = len(pts)
        for i in range(n):
            ch = rng.uniform(0.012, 0.03, 4)  # chamfers, worn unevenly
            adze = rng.normal(0.0, 0.006, 2)
            r, a = radial[i], e_t
            ho = hm + adze[0]
            loop = [(ho, hs - ch[0]), (ho - ch[0], hs), (-hm + ch[1], hs), (-hm, hs - ch[1]),
                    (-hm, -hs + ch[2]), (-hm + ch[2], -hs), (ho - ch[3], -hs + adze[1]), (ho, -hs + ch[3]),
                    (ho - 0.014, adze[1] * 0.5)]  # the seam between the doubled futtocks
            rings.append(np.array([pts[i] + rv * r + av * a for rv, av in loop]))
            along.append(i / (n - 1))
        t0 = pts[0] - pts[1]
        t1 = pts[-1] - pts[-2]
        t0 /= np.linalg.norm(t0)
        t1 /= np.linalg.norm(t1)
        pre = splinter_rings(pts[0], t0, rings[0], rng)[::-1]
        post = splinter_rings(pts[-1], t1, rings[-1], rng)
        all_rings = pre + rings + post
        P, T, Cc = loft(all_rings, cap_start=pts[0] + t0 * 0.03, cap_end=pts[-1] + t1 * 0.03)
        nl = len(all_rings)
        nv = len(all_rings[0])
        # per vertex: distance (m) to the nearest broken end, which column (grain), how far round the frame
        ring_id = np.concatenate([np.repeat(np.arange(nl), nv), [0, nl - 1]])
        endness = np.concatenate([np.repeat([1.0, 0.75] + [0.0] * n + [0.75, 1.0], nv), [1.0, 1.0]])
        seglen = float(np.mean(np.linalg.norm(np.diff(pts, axis=0), axis=1)))
        dist_end = np.minimum(ring_id - 2, nl - 3 - ring_id).clip(0) * seglen
        broken = np.clip(np.maximum(endness, ck.smoothstep(0.16, 0.0, dist_end)), 0, 1)
        col_id = np.concatenate([np.tile(np.arange(nv), nl), [0, 0]])
        grain = noise1(col_id * 3.7 + k * 11.0, SEED + 70) * 0.5 + 0.5
        psi_v = np.interp(np.clip(ring_id - 2, 0, n - 1), np.arange(n), psis)
        nrm = ck.weld_normals(P, ck.vertex_normals(P, T))
        up = ck.smoothstep(0.2, 0.8, nrm[:, 1]) * ck.smoothstep(1.0, 2.2, P[:, 1])
        salt = ck.smoothstep(0.15, 0.45, ck.fbm(P * 5.0, SEED + 71 + k))
        slime = ck.smoothstep(1.3, 2.2, np.abs(psi_v))
        worn = np.isin(col_id, (1, 6)).astype(np.float64) * np.concatenate([np.ones(nv * nl), [0, 0]])
        seam = (col_id == 8).astype(np.float64)
        col = ck.mix(PAL["timber_weathered"] * 0.3, PAL["timber_weathered"] * 0.44, grain[:, None])
        col = ck.mix(col, PAL["timber_weathered"] * 0.6, (0.3 * up + 0.3 * worn)[:, None])
        col = ck.mix(col, PAL["lacquer_black"], (0.6 * seam)[:, None])
        col = ck.mix(col, PAL["foliage_shadow"] * 0.9, (0.5 * slime)[:, None])
        col = ck.mix(col, PAL["bone"] * 0.7, (0.2 * salt * (1 - slime))[:, None])
        # iron spikes on the outer face, bleeding rust below them; a few driven, a few left standing bent
        n_sp = 4
        sp_idx = rng.choice(np.arange(2, n - 2), size=min(n_sp, n - 4), replace=False)
        rust = np.zeros(len(P))
        for j, i in enumerate(sorted(sp_idx)):
            sp = pts[i] + radial[i] * hm + e_t * rng.uniform(-0.025, 0.025)
            dh = np.linalg.norm((P - sp)[:, [0, 2]], axis=1)
            below = np.clip(sp[1] - P[:, 1], 0.0, None)
            rust = np.maximum(rust, g(np.linalg.norm(P - sp, axis=1), 0.07) +
                              0.8 * g(dh, 0.035) * np.exp(-below / 0.22) * (P[:, 1] <= sp[1] + 0.01))
            e1 = np.cross(radial[i], e_t)
            Ph, Th = box(sp + radial[i] * 0.008, radial[i], e_t, e1, 0.01, 0.019, 0.019)
            colh = ck.mix(PAL["volcanic_stone"] * 0.8, PAL["laterite"] * 0.6, rng.uniform(0.3, 0.7))
            ck.finish(mesh, Ph, Th, "rib", colh, bone, wet=0.3, cavity=0.3, flat=True)
            if j == 1:
                d = radial[i] + rng.normal(0, 0.35, 3)
                Ps, Ts = nail(sp + radial[i] * 0.015, d, rng.uniform(0.08, 0.15), 0.008, e_t, rng.uniform(0.4, 1.2))
                ck.finish(mesh, Ps, Ts, "rib", colh * 0.9, bone, wet=0.3, cavity=0.2, flat=True)
        col = ck.mix(col, PAL["laterite"] * 0.55, (0.75 * np.clip(rust, 0, 1))[:, None])
        col = ck.mix(col, PAL["bone"] * 0.88, broken[:, None])
        wet = np.clip(0.8 - 0.45 * up - 0.6 * broken, 0.15, 1.0)
        cav = np.clip(0.2 + 0.35 * (1.0 - grain) * (1 - broken) + 0.3 * rust + 0.6 * seam, 0, 1)
        ck.finish(mesh, P, T, "rib", col, bone, wet=wet, cavity=cav, flat=True)
        # treenail holes and pegs along the outer face
        for i in rng.choice(np.arange(2, n - 2), size=min(5, n - 4), replace=False):
            ctr = pts[i] + radial[i] * (hm + 0.003) + e_t * rng.uniform(-0.03, 0.03)
            e1 = np.cross(radial[i], e_t)
            a = np.arange(6) * math.pi / 3
            rr = rng.uniform(0.011, 0.016)
            Pn = np.vstack([ctr[None], ctr + rr * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e_t))])
            Tn = np.array([(0, 1 + q, 1 + (q + 1) % 6) for q in range(6)], dtype=np.int64)
            if np.dot(np.cross(Pn[Tn[0, 1]] - Pn[0], Pn[Tn[0, 2]] - Pn[0]), radial[i]) < 0:
                Tn = ck.flip(Tn)
            peg = rng.random() < 0.4
            ck.finish(mesh, Pn, Tn, "rib", PAL["timber_weathered"] * 0.75 if peg else PAL["lacquer_black"], bone,
                      wet=0.5, cavity=0.2 if peg else 1.0)
        # loose splinters standing off each broken end
        for end, tan in ((0, t0), (n - 1, t1)):
            for _ in range(1):
                base = pts[end] + radial[end] * rng.uniform(-hm, hm) * 0.6 + e_t * rng.uniform(-hs, hs) * 0.5
                d = tan + rng.normal(0, 0.15, 3)
                Ps, Ts = nail(base, d, rng.uniform(0.08, 0.16), rng.uniform(0.016, 0.024), radial[end],
                              rng.uniform(-0.3, 0.3))
                ck.finish(mesh, Ps, Ts, "rib", PAL["bone"] * rng.uniform(0.75, 0.9), bone, wet=0.15, cavity=0.2,
                          flat=True)
        # weed hanging off the frame in ragged clumps: flat wavy ribbons, olive going pale at the tips
        for _ in range(2):
            i = int(rng.integers(1, n - 1))
            if abs(psis[i]) < 0.7:
                i = 0 if rng.random() < 0.5 else n - 1
            p0 = pts[i] + radial[i] * (hm + 0.01)
            for _strand in range(int(rng.integers(1, 3))):
                weed_strand(mesh, p0 + e_t * rng.uniform(-0.05, 0.05), radial[i], e_t, rng.uniform(0.2, 0.55), rng,
                            bone)
    # stubs of hull planking still nailed across some frames, running along the body, broken off both ends
    rng = np.random.default_rng(SEED + 81)
    for k, psi, l0, l1 in PLANKS:
        bone = rig.rigid(f"rib{k}")
        fg = frame_geometry(k, bd)
        i = int(np.argmin(np.abs(fg["psis"] - psi)))
        r = fg["radial"][i]
        e_t = fg["e_t"]
        w_dir = np.cross(r, e_t)
        ctr = fg["pts"][i] + r * (fg["hm"] + 0.026)
        hw, ht = 0.085, 0.022
        rings = []
        zs = np.linspace(l0, l1, 4)
        for z in zs:
            ch = rng.uniform(0.006, 0.014)
            loop = [(ht, hw - ch), (ht - ch, hw), (-ht, hw), (-ht, -hw), (ht - ch, -hw), (ht, -hw + ch)]
            sag = 0.02 * (z / 0.3) ** 2
            rings.append(np.array([ctr + rv * r + wv * w_dir + e_t * z - r * sag for rv, wv in loop]))
        pre = splinter_rings(ctr + e_t * l0, -e_t, rings[0], rng, 0.5, (0.55, 0.95))[::-1]
        post = splinter_rings(ctr + e_t * l1, e_t, rings[-1], rng, 0.5, (0.55, 0.95))
        all_r = pre + rings + post
        P, T, _c = loft(all_r, cap_start=ctr + e_t * (l0 - 0.02), cap_end=ctr + e_t * (l1 + 0.02))
        nl = len(all_r)
        endness = np.concatenate([np.repeat([1.0, 0.7, 0.0, 0.0, 0.0, 0.0, 0.7, 1.0], 6), [1.0, 1.0]])
        grain = np.concatenate([np.tile(noise1(np.arange(6) * 2.9 + k, SEED + 82) * 0.5 + 0.5, nl), [0.5, 0.5]])
        col = ck.mix(PAL["timber_weathered"] * 0.38, PAL["timber_weathered"] * 0.56, grain[:, None])
        col = ck.mix(col, PAL["bone"] * 0.6, (0.15 * ck.smoothstep(0.1, 0.4, ck.fbm(P * 6.0, SEED + 83)))[:, None])
        col = ck.mix(col, PAL["bone"] * 0.9, endness[:, None])
        ck.finish(mesh, P, T, "rib", col, bone, wet=np.clip(0.55 - 0.5 * endness, 0.1, 1), cavity=0.25, flat=True)
        for off in (-0.05, 0.05):
            sp = ctr + r * (ht + 0.006) + w_dir * off
            Ph, Th = box(sp, r, e_t, w_dir, 0.008, 0.016, 0.016)
            ck.finish(mesh, Ph, Th, "rib", ck.mix(PAL["volcanic_stone"] * 0.8, PAL["laterite"] * 0.6, 0.5), bone,
                      wet=0.3, cavity=0.3, flat=True)


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
def idle_clip() -> ck.Clip:
    sp = [f"spine{i}" for i in range(N_SPINE)]
    idle = ck.Clip("idle", 3.0, loop=True)
    idle.wave("root", amp_loc=(0.0, 0.035, 0.0), cycles=1, phase=0.6)
    for i, b in enumerate(sp):
        idle.wave(b, amp_rot=(1.6, 0.0, 1.0), cycles=1, phase=-i * 0.35)
    idle.wave("jaw", amp_rot=(5.0, 0.0, 0.0), base_rot=(5.0, 0.0, 0.0), cycles=2)
    for k in range(len(RIBS)):  # the frames creak a beat behind the body
        idle.wave(f"rib{k}", amp_rot=(1.5, 0.0, 2.0), cycles=1, phase=-k * 0.35 - 0.9)
    return idle


def build_clips() -> list[ck.Clip]:
    sp = [f"spine{i}" for i in range(N_SPINE)]
    idle = idle_clip()

    # ready: coiled back a little inside the frames, jaw ajar, breathing fast; a loop
    ready = ck.Clip("ready", 2.0, loop=True)
    ready.wave("root", amp_loc=(0.0, 0.025, 0.0), cycles=2, base_loc=(0.0, 0.05, 0.0))
    for i, b in enumerate(sp):
        w = (i + 1) / N_SPINE
        ready.wave(b, amp_rot=(1.2, 0.0, 0.8), cycles=2, phase=-i * 0.4, base_rot=(-3.5 * w, 0.0, 0.0))
    ready.wave("jaw", amp_rot=(3.0, 0.0, 0.0), base_rot=(13.0, 0.0, 0.0), cycles=4)
    for k in range(len(RIBS)):
        ready.wave(f"rib{k}", amp_rot=(1.2, 0.0, 1.8), cycles=2, phase=-k * 0.4 - 1.0)

    # intro: it rears up out of the water to its full height, jaw wide, the frames creaking, then settles to idle
    intro = ck.Clip("intro", 2.6)
    for t, rise, rear, jaw in ((0.0, -1.7, 7.0, 0.0), (0.55, -0.9, 2.0, 6.0), (1.15, 0.18, -9.0, 30.0),
                               (1.5, 0.22, -10.0, 44.0), (1.95, 0.12, -6.0, 38.0)):
        intro.key("root", t, (0.0, 0.0, 0.0), (0.0, rise, -0.15 * min(rise, 0.0)))
        for i, b in enumerate(sp):
            w = (i + 1) / N_SPINE
            intro.key(b, t, (rear * w + (1.5 * math.sin(t * 9.0 + i) if t > 0.4 else 0.0), 0.0,
                             2.0 * math.sin(t * 5.0 - i * 0.6)))
        intro.key("jaw", t, (jaw, 0.0, 0.0))
    for k in range(len(RIBS)):
        side = 1.0 if k % 2 else -1.0
        for t, s in ((0.0, 0.0), (0.7, 1.0), (1.2, -1.0), (1.6, 0.8), (1.95, -0.4)):
            intro.key(f"rib{k}", t, (1.5 * s, 0.0, 5.0 * s * side))
    for b, ks in idle.keys.items():  # end on idle's first frame
        r, loc = idle.sample(b, 0.0)
        intro.key(b, 2.6, tuple(r), tuple(loc))

    attack = ck.Clip("attack", 1.5)
    for t, back, jaw in ((0.0, 0, 0), (0.6, -1, 28), (0.8, 1.3, 4), (1.0, 0.8, 0), (1.5, 0, 0)):
        for i, b in enumerate(sp):
            w = (i + 1) / N_SPINE
            attack.key(b, t, (7.0 * back * w, 0.0, 0.0))
        attack.key("jaw", t, (jaw, 0, 0))

    cast = ck.Clip("cast", 1.6)
    for t, s in ((0.0, 0.0), (0.6, 1.0), (1.1, 1.0), (1.6, 0.0)):
        for k in range(len(RIBS)):
            cast.key(f"rib{k}", t, (0.0, 0.0, (9.0 if k % 2 else -9.0) * s), (0.0, 0.05 * s, 0.0))
        for i, b in enumerate(sp):
            cast.key(b, t, (-2.5 * s * (i + 1) / N_SPINE, 0, 0))
        cast.key("jaw", t, (18 * s, 0, 0))

    hit = ck.Clip("hit", 0.5)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.5, 0.0)):
        for i, b in enumerate(sp):
            hit.key(b, t, (-3.0 * s, 0, 2.0 * s * (1 if i % 2 else -1)))

    ko = ck.Clip("ko", 2.4)  # it slides back down between the planks; a frame goes under last
    for t, drop, tilt in ((0.0, 0.0, 0.0), (0.6, 0.3, -6.0), (1.4, 1.6, -14.0), (2.0, 2.6, -18.0), (2.4, 3.0, -18.0)):
        ko.key("root", t, (tilt, 0, 0), (0, -drop, -0.4 * drop / 3.0))
    for i, b in enumerate(sp):
        ko.key(b, 0.0)
        ko.key(b, 1.2, (4.0 * (i + 1) / N_SPINE, 0, 0))
        ko.key(b, 2.4, (6.0 * (i + 1) / N_SPINE, 0, 0))
    # `breaking` (m2-slice act1_ch01, 50% HP): it thrashes and the ship's frames burst off and fall into the water
    brk = ck.Clip("phase_break", 1.8)
    for t, s, fall in ((0.0, 0.0, 0.0), (0.35, 1.0, 0.0), (0.6, 0.6, 0.25), (1.2, 0.2, 0.8), (1.8, 0.0, 1.0)):
        for i, b in enumerate(sp):
            brk.key(b, t, (-4.0 * s * (i + 1) / N_SPINE, 0, (3.0 if i % 2 else -3.0) * s))
        for k in range(len(RIBS)):
            side = 1.0 if k % 2 else -1.0
            brk.key(f"rib{k}", t, (25.0 * fall, 0.0, side * 70.0 * fall),
                    (side * 0.9 * fall, 0.35 * s - 3.0 * fall * fall, 0.2 * fall))
    return [idle, ready, intro, attack, cast, hit, ko, brk]


def build(rig: ck.Rig, joints: np.ndarray) -> tuple[ck.Mesh, ck.Mesh]:
    mesh = ck.Mesh("hullgnaw")
    bd = body(mesh, rig, joints)
    dorsal_fin(mesh, bd)
    barnacles(mesh, bd)
    waterline_collar(mesh, bd)
    head(mesh, rig, joints)
    frames = ck.Mesh("Ribs")  # its own node: the `breaking` phase lets the frames fall, then hides them
    ribs(frames, rig, bd)
    return mesh, frames


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, joints = build_rig()
    mesh, frames = build(rig, joints)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extra_meshes=[frames],
                              extras={"hymn_creature": "hullgnaw"})
    print(f"hullgnaw: {info} (body {mesh.triangle_count}, frames {frames.triangle_count})")


if __name__ == "__main__":
    main()
