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

M3-CRB-013 (the move pass): it is fought on the raft's deck, so it comes up through a breach it smashed there (dark
water, broken boards prised up, foam and weed; on its own root bone, `breach`), and the intro, the KO and the falling
frames go through that hole. Each skill has its own clip (Gnaw `attack`, `rib_lash`, `thrash`, `coil`).
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

# M3-CRB-013: it is fought on the raft's deck (y 0), not in open water, so it comes up through a breach it smashed in
# the planks: a disc of dark water a few mm over the deck, ringed by broken boards (run along the deck's planks, model
# x) and foam. The body crosses the deck at the rest arch's waterline; everything of it under the deck stays inside
# BREACH_R of that point (tools/tests/test_creatures.py measures it), so the intro and the KO go through the hole.
_I_UP = int(np.argmax(_DC[:, 1] > 1.0))  # the rising part of the arch, where y is single valued
S_WATER = float(np.interp(0.0, _DC[:_I_UP, 1], _DS[:_I_UP]))  # arclength of the rest waterline
BREACH_C = np.array([0.0, 0.0, float(np.interp(0.0, _DC[:_I_UP, 1], _DC[:_I_UP, 2]))])
BREACH_R = 1.12  # the hole's radius (the frames' broken ends reach about 1.1 m off the spine)
BREACH_Y = 0.004  # the water's height over the deck


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
    # M3-CRB-013: the breach it burst up through, a root of its own so it stays on the deck while the body rises and
    # sinks through it (the intro, the KO); also the anchor for a splash
    rig.add("breach", BREACH_C, BREACH_C + np.array([0.0, 0.3, 0.0]))
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


def breach_radius(phi):
    """The hole's ragged radius at angle phi round BREACH_C (0 is +x, pi/2 is +z): torn further toward the party,
    where the fourth frame's long broken arm comes through."""
    phi = np.asarray(phi, dtype=np.float64)
    r = BREACH_R * (1.0 + 0.035 * np.sin(3.0 * phi + 0.7) + 0.03 * noise1(phi * 2.2, SEED + 91).reshape(phi.shape))
    return r + 0.22 * g(phi - math.pi / 2, 0.62)


def breach(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """M3-CRB-013: the hole it smashed up through the deck. Dark water a few mm over the planks, lighter and broken by
    foam round the body and under the rim; the deck's boards (they run along x) snapped across the hole, their broken
    ends prised up (it came up from below) or bent down into the water, splintered pale; weed thrown up over them."""
    rng = np.random.default_rng(SEED + 90)
    bone = rig.rigid("breach")
    cx, cz = float(BREACH_C[0]), float(BREACH_C[2])
    # the water: a polar grid out under the boards' broken ends
    na = 36
    phi = np.arange(na) * 2.0 * math.pi / na
    rr = np.array([0.0, 0.2, 0.38, 0.5, 0.62, 0.76, 0.88, 0.97, 1.04])
    edge = breach_radius(phi) + 0.06
    P = np.array([(cx + r * e * math.cos(p), 0.0, cz + r * e * math.sin(p)) for r in rr for p, e in zip(phi, edge)])
    rad = np.hypot(P[:, 0] - cx, P[:, 2] - cz)
    churn = ck.fbm(P * np.array([4.5, 1.0, 4.5]), SEED + 92)
    rim = ck.smoothstep(0.8, 0.97, rad / edge[np.arange(len(P)) % na])  # under the broken deck's edge
    foam = np.clip(ck.smoothstep(0.42, 0.5, rad) * ck.smoothstep(0.7, 0.56, rad) * ck.smoothstep(-0.05, 0.3, churn),
                   0, 1)
    P[:, 1] = BREACH_Y + 0.008 * foam * ck.smoothstep(0.1, 0.5, churn + 0.4)
    T = []
    for q in range(na):  # the centre fan, then the rings
        T.append((0, q + na, (q + 1) % na + na))
    T += [tuple(int(v) + na for v in tri) for tri in ck.grid_tris(len(rr) - 1, na, True)]
    T = orient(P, np.asarray(T, dtype=np.int64), np.array([cx, -1.0, cz]))
    # dark: a well of water under the deck, a little teal stirred up round the body, black under the broken edge
    stir = ck.smoothstep(0.3, 0.55, rad) * ck.smoothstep(0.95, 0.65, rad / edge[np.arange(len(P)) % na])
    col = ck.mix(PAL["abyss_navy"] * 0.45, PAL["deep_teal_shadow"] * 0.6, (stir * (0.6 + 0.4 * churn))[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 0.6, rim[:, None])
    col = ck.mix(col, PAL["foam_white"] * 0.72, (0.8 * foam)[:, None])
    ck.finish(mesh, P, T, "carapace", col, bone, wet=np.clip(0.55 - 0.3 * rim + 0.2 * foam, 0.0, 1.0),
              cavity=np.clip(0.45 + 0.5 * rim - 0.4 * foam, 0.0, 1.0))
    # the boards: one per plank strip on each side of the hole, from the deck to its broken end
    wid = 0.22
    n_strips = int(2.0 * BREACH_R / wid) + 1
    for k in range(n_strips):
        dz = (k + 0.5) * wid - n_strips * wid / 2.0
        for side in (-1.0, 1.0):
            ang = math.atan2(dz, side * max(BREACH_R ** 2 - dz * dz, 0.04) ** 0.5)
            r_edge = float(breach_radius(ang))
            if abs(dz) > r_edge - 0.05:
                continue
            hx = (r_edge * r_edge - dz * dz) ** 0.5
            x_in = cx + side * hx  # where the board leaves the deck
            kind = rng.random()  # prised up (it came from below), bent down into the water, or snapped off nearly flat
            if kind < 0.1:
                continue  # gone altogether
            down = kind > 0.72
            tilt = math.radians(-rng.uniform(20.0, 42.0) if down else
                                rng.uniform(1.0, 7.0) if kind < 0.35 else rng.uniform(10.0, 36.0))
            lift = rng.uniform(0.08, 0.32) * (0.75 if down else 1.0)
            flat = rng.uniform(0.1, 0.18)
            w = wid * rng.uniform(0.8, 0.92)
            z0 = cz + dz + rng.uniform(-0.01, 0.01)
            inward = np.array([-side, 0.0, 0.0])
            dirn = inward * math.cos(tilt) + np.array([0.0, math.sin(tilt), 0.0])
            yaw = rng.uniform(-0.12, 0.12)  # a broken board is never quite square
            dirn = ck.rot_y(math.degrees(yaw)) @ dirn
            if down:  # it bends at the hole's edge across its whole width, so no corner of it dips under the planks
                far = min(abs(dz) + w / 2.0 + 0.012, r_edge - 0.02)
                x_in = cx + side * ((r_edge * r_edge - far * far) ** 0.5 - 0.06)
            hinge = np.array([x_in, 0.0, z0])
            # the centreline's bottom (y), and thickness, along the board: a wedge out of the deck, then the board
            path = [(hinge + side * np.array([flat, 0.0, 0.0]), 0.001, 0.006),
                    (hinge + side * np.array([flat * 0.45, 0.0, 0.0]), 0.002, 0.02),
                    (hinge, 0.004, 0.032), (hinge + dirn * lift * 0.55, 0.0, 0.034), (hinge + dirn * lift, 0.0, 0.034)]
            e_w = np.cross(np.array([0.0, 1.0, 0.0]), dirn)
            e_w /= np.linalg.norm(e_w)
            up_l = np.cross(dirn, e_w)
            up_l *= np.sign(up_l[1])
            rings = []
            for q, (c, y0, th) in enumerate(path):
                up = np.array([0.0, 1.0, 0.0]) if q < 3 else up_l
                base = c + np.array([0.0, y0, 0.0])
                rings.append(np.array([base + up * th + e_w * w / 2, base + up * th - e_w * w / 2,
                                       base - e_w * w / 2, base + e_w * w / 2]))
            end = rings[-1].mean(axis=0)
            rings += splinter_rings(end, dirn, rings[-1], rng, 0.8, (0.2, 0.7))
            Pb, Tb, _c = loft(rings, cap_start=rings[0].mean(axis=0) + side * np.array([0.004, 0.0, 0.0]),
                              cap_end=end + dirn * 0.06)
            nr = len(rings)
            top = np.concatenate([np.tile([1.0, 1.0, 0.0, 0.0], nr), [0.5, 0.5]])
            brk = np.concatenate([np.repeat([0.0, 0.0, 0.0, 0.0, 0.3, 0.8, 1.0], 4), [0.0, 1.0]])
            grain = ck.smoothstep(-0.3, 0.3, ck.fbm(Pb * np.array([2.0, 20.0, 20.0]), SEED + 93 + k))
            colb = ck.mix(PAL["timber_weathered"] * 0.62, ck.mix(PAL["timber_weathered"], PAL["laterite"], 0.2) * 0.95,
                          (0.35 + 0.4 * grain)[:, None])
            colb = ck.mix(colb, PAL["lacquer_black"] * 1.4, (0.75 * (1.0 - top))[:, None])  # the wet underside
            colb = ck.mix(colb, PAL["bone"] * 0.85, (0.85 * brk)[:, None])
            ck.finish(mesh, Pb, Tb, "rib", colb, bone, wet=np.clip(0.3 + 0.6 * (1.0 - top) + 0.3 * down, 0.0, 1.0),
                      cavity=0.2 + 0.2 * (1.0 - grain), flat=True)
            for _ in range(int(rng.integers(1, 3))):
                b0 = end + np.array([0.0, 0.0, rng.uniform(-w, w) * 0.35])
                d = dirn + rng.normal(0.0, 0.3, 3)
                Ps, Ts = nail(b0, d, rng.uniform(0.07, 0.15), rng.uniform(0.008, 0.014), np.array([0.0, 1.0, 0.0]),
                              rng.uniform(-0.4, 0.4))
                ck.finish(mesh, Ps, Ts, "rib", PAL["bone"] * rng.uniform(0.72, 0.9), bone, wet=0.2, cavity=0.2,
                          flat=True)
    # weed thrown up with it: fronds floating on the water and draped over the broken boards
    for k in range(8):
        ang = 2.0 * math.pi * k / 8 + rng.uniform(-0.25, 0.25)
        dirn = np.array([math.cos(ang), 0.0, math.sin(ang)])
        side = np.cross(dirn, [0.0, 1.0, 0.0])
        r0 = rng.uniform(0.5, 0.62)
        reach = rng.uniform(0.3, 0.55)
        pts = []
        for q in range(6):
            r = r0 + reach * q / 5
            y = BREACH_Y + 0.006 if r < float(breach_radius(ang)) - 0.04 else 0.045
            pts.append(np.array([cx, y, cz]) + dirn * r + side * 0.05 * math.sin(q * 1.4 + k))
        sp = ck.bezier(pts, 7)
        Pw, Tw = ck.tube(sp, np.linspace(0.05, 0.015, 7), 4, squash=0.2, up_hint=(0.0, 1.0, 0.0))
        colw = ck.mix(PAL["foliage_shadow"], PAL["saltgrass"] * 0.55, np.linspace(0.1, 0.6, len(Pw))[:, None])
        ck.finish(mesh, Pw, Tw, "rib", colw, bone, wet=1.0, cavity=0.3)


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


SP = [f"spine{i}" for i in range(N_SPINE)]
RB = [f"rib{k}" for k in range(len(RIBS))]

# M3-CRB-013: the spine chain measured for the clips. Every spine bone turns about x only in the arch's plane, so a
# bone's world angle (from up toward +z) is the sum of its chain's rx: a pose is written as each bone's change of
# world angle and turned into local rx by local_rx().
_JOINTS = spine_curve(N_SPINE + 1)
_BD = np.diff(_JOINTS, axis=0)
_BL = np.linalg.norm(_BD, axis=1)
_BTH = np.degrees(np.arctan2(_BD[:, 2], _BD[:, 1]))
_BS = np.array([float(s_of_u(i / N_SPINE)) for i in range(N_SPINE + 1)])
_DTH = np.degrees(np.arctan2(_DT[:, 2], _DT[:, 1]))
S_HIDDEN = float(_BS[-1]) + 1.3  # the waterline this far along the chain: the whole body and head are under


def tangent_deg(p):
    """The rest arch's tangent (degrees from up toward +z) at arclength p; straight on down past its end."""
    return np.interp(np.clip(p, 0.0, LENGTH), _DS, _DTH)


def local_rx(delta) -> np.ndarray:
    return np.diff(np.concatenate([[0.0], np.asarray(delta, dtype=np.float64)]))


def _waterline_y(delta: np.ndarray, sc: float) -> float:
    th = np.radians(_BTH + delta)
    y = _JOINTS[0, 1] + np.concatenate([[0.0], np.cumsum(_BL * np.cos(th))])
    if sc >= _BS[-1]:
        return float(y[-1] + (sc - _BS[-1]) * math.cos(th[-1]))
    j = max(int(np.searchsorted(_BS, sc, side="right")) - 1, 0)
    f = (sc - _BS[j]) / (_BS[j + 1] - _BS[j])
    return float(y[j] + f * (y[j + 1] - y[j]))


_Y_REST = _waterline_y(np.zeros(N_SPINE), S_WATER)


def emerge(sc: float) -> tuple[np.ndarray, float]:
    """The body run out of the breach along its own rest path (as an eel leaves a hole: what is out follows where the
    head went), with the chain's arclength `sc` at the waterline: (local rx per spine bone, root y). At S_WATER it is
    the rest pose; at S_HIDDEN all of it is under, standing straight down from the hole."""
    mid = 0.5 * (_BS[:-1] + _BS[1:])
    delta = tangent_deg(mid - sc + S_WATER) - tangent_deg(mid)
    return local_rx(delta), -(_waterline_y(delta, sc) - _Y_REST)


def axis_rot(axis, deg: float) -> np.ndarray:
    a = np.asarray(axis, dtype=np.float64)
    a = a / np.linalg.norm(a)
    th = math.radians(deg)
    K = np.array([[0.0, -a[2], a[1]], [a[2], 0.0, -a[0]], [-a[1], a[0], 0.0]])
    return np.eye(3) + math.sin(th) * K + (1.0 - math.cos(th)) * K @ K


def euler_of(R: np.ndarray) -> tuple[float, float, float]:
    """The kit's (rx, ry, rz) degrees of a rotation (it applies x, then y, then z about fixed axes)."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    return (math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(b), math.degrees(math.atan2(R[1, 0], R[0, 0])))


_RIB_T = [curve_at(u)[1] for u in RIBS]


def rib_rot(k: int, spin: float, rx: float = 0.0) -> tuple[float, float, float]:
    """A frame turned `spin` degrees round the body (about the spine's tangent at it: it never cuts into the body),
    then tipped rx along it."""
    return euler_of(ck.rot_x(rx) @ axis_rot(_RIB_T[k], spin))


def idle0() -> dict:
    idle = idle_clip()
    return {b: (np.asarray(idle.sample(b, 0.0)[0]), np.asarray(idle.sample(b, 0.0)[1])) for b in idle.keys}


def body_key(c: ck.Clip, t: float, delta=None, ry=None, rz=None, jaw=None, root_y=None, spins=None, rib_rx=None,
             rib_loc=None) -> None:
    """Keys a pose made of deltas: `delta` each spine bone's change of world angle (rx), `ry`/`rz` local yaw and lean
    per spine bone, the jaw's opening, the root's lift, and each frame's spin round the body (and tip, and offset)."""
    rx = local_rx(delta if delta is not None else np.zeros(N_SPINE))
    ry = np.zeros(N_SPINE) if ry is None else np.asarray(ry, dtype=np.float64)
    rz = np.zeros(N_SPINE) if rz is None else np.asarray(rz, dtype=np.float64)
    for i, b in enumerate(SP):
        c.key(b, t, (rx[i], ry[i], rz[i]))
    if jaw is not None:
        c.key("jaw", t, (jaw, 0.0, 0.0))
    if root_y is not None:
        c.key("root", t, (0.0, 0.0, 0.0), (0.0, root_y, 0.0))
    if spins is not None:
        for k, b in enumerate(RB):
            loc = (0.0, 0.0, 0.0) if rib_loc is None else tuple(rib_loc[k])
            c.key(b, t, rib_rot(k, spins[k], 0.0 if rib_rx is None else rib_rx[k]), loc)


def ramp(lo: float, hi: float, n: int = N_SPINE) -> np.ndarray:
    return np.linspace(lo, hi, n)


ALT = np.array([-1.0, 1.0, -1.0, 1.0, -1.0])  # alternate frames turn opposite ways


def strike(name: str, length: float, poses: list) -> ck.Clip:
    """A one-shot from idle's first frame back to it: `poses` are (t, body_key kwargs) between the two."""
    d = ck.Clip("_" + name, length)
    body_key(d, 0.0, jaw=0.0, root_y=0.0, spins=np.zeros(5))
    for t, kw in poses:
        body_key(d, t, **kw)
    body_key(d, length, jaw=0.0, root_y=0.0, spins=np.zeros(5))
    return ck.in_pose(d, name, idle0())


NECK = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.5, 0.75, 1.0, 1.0])


def arch(lean: float, neck: float, head: float = 0.0) -> np.ndarray:
    """A pose as spine deltas: the whole arch leant (+ toward the party, about its base), the neck raised (-) or
    dropped (+) about the crown, the head pitched (- up). The snout targets below were solved against idle's first
    frame (its snout sits 1.25 m up, 2.41 m out)."""
    return lean * np.ones(N_SPINE) + neck * NECK + np.r_[np.zeros(N_SPINE - 1), head]


def gnaw_clip() -> ck.Clip:
    """Gnaw (`attack`): it coils back through its frames, the snout drawn 0.55 m back and 0.4 m up and the head cocked
    at the party, jaw gaping (the telegraph, 0.15-0.64 s); then it lunges level, the arch leaning in and the neck
    straightening so the snout runs 0.85 m out at the height it started, and the jaw snaps shut at contact (0.8 s); it
    overshoots and settles on idle's first frame."""
    return strike("attack", 1.5, [
        (0.2, dict(delta=arch(-4.5, 7.0, -6.0), jaw=14.0, spins=ALT * 3.0)),
        (0.55, dict(delta=arch(-10.5, 18.0, -18.0), rz=ramp(0.0, 1.5), jaw=38.0, spins=ALT * 5.0)),
        (0.64, dict(delta=arch(-11.5, 20.0, -20.0), rz=ramp(0.0, 1.5), jaw=44.0, spins=ALT * 6.0)),
        (0.8, dict(delta=arch(14.0, -26.0, -4.0), jaw=-1.0, spins=-ALT * 4.0)),
        (0.92, dict(delta=arch(17.5, -33.0, -4.0), jaw=3.0, spins=-ALT * 6.0)),
        (1.15, dict(delta=arch(1.5, -3.0), jaw=6.0, spins=ALT * 2.0)),
    ])


def rib_lash_clip() -> ck.Clip:
    """Rib Lash: it winds its body away from the camera's flank, frames clenched (the telegraph, 0.15-0.6 s), then
    whips across toward the party and the camera, head sweeping low, and the frames swing round the body after it
    like flails (contact 0.8 s: the body's sweep; the frames peak a beat later), and comes back to idle."""
    away, across = ramp(3.0, 1.0), ramp(-4.5, -1.5)
    return strike("rib_lash", 1.7, [
        (0.25, dict(delta=ramp(-1.0, -5.0), ry=away * 0.6, rz=ramp(-1.5, -0.5), jaw=6.0, spins=ALT * 6.0)),
        (0.6, dict(delta=ramp(-2.0, -9.0), ry=away, rz=ramp(-3.0, -1.0), jaw=10.0, root_y=0.04, spins=ALT * 12.0)),
        (0.8, dict(delta=ramp(3.0, 1.0), ry=across * 0.6, rz=ramp(3.0, 1.0), jaw=18.0, root_y=-0.02,
                   spins=-ALT * 18.0)),
        (0.95, dict(delta=ramp(3.5, 2.0), ry=across, rz=ramp(3.5, 1.2), jaw=8.0, root_y=-0.03, spins=-ALT * 30.0)),
        (1.2, dict(delta=ramp(1.0, 0.0), ry=across * 0.25, rz=ramp(1.0, 0.3), jaw=4.0, spins=ALT * 8.0)),
    ])


THRASH_SLAM = (19.0, -15.0)  # the slam's lean and neck: the snout comes down 0.84 m, the jaw stops over the planks


def thrash_clip() -> ck.Clip:
    """Thrash (the `breaking` phase, frames gone): it whips side to side across the deck, rears up (0.8-1.2 s) and
    slams its head down on the party, stopping above the planks (contact 1.25 s), rebounds and settles."""
    def whip(side: float) -> np.ndarray:
        return side * np.array([3.0, 3.0, 3.0, 2.5, 2.5, 2.0, 2.0, 1.5, 1.5, 1.0])
    return strike("thrash", 1.9, [
        (0.18, dict(delta=ramp(-1.0, -4.0), ry=whip(1.0) * 0.8, rz=ramp(-3.0, -1.0), jaw=20.0, root_y=0.03)),
        (0.42, dict(delta=ramp(0.0, -2.0), ry=whip(-1.0), rz=ramp(4.0, 1.5), jaw=30.0, root_y=0.0)),
        (0.66, dict(delta=ramp(-1.0, -4.0), ry=whip(1.0) * 0.9, rz=ramp(-3.5, -1.2), jaw=24.0, root_y=0.03)),
        (0.85, dict(delta=arch(-8.0, 10.0, -10.0), ry=whip(-0.3), jaw=30.0, root_y=0.04)),
        (1.08, dict(delta=arch(-13.5, 17.0, -20.0), jaw=42.0, root_y=0.06)),
        (1.25, dict(delta=arch(THRASH_SLAM[0], THRASH_SLAM[1], 6.0), jaw=6.0)),
        (1.38, dict(delta=arch(10.0, -7.0), jaw=14.0)),
        (1.6, dict(delta=arch(1.0, -1.0), jaw=6.0)),
    ])


def coil_clip() -> ck.Clip:
    """Coil (gnaw_coil, a self buff): it sinks a little into the breach and winds down tight, the arch drawn in,
    the head tucked, the jaw shut, the frames wrung round it; holds in two slow tightening breaths (the buff, about 1.0
    s), then lets go back to idle."""
    # the jaw -4.5: idle's first frame holds it 5 degrees open
    tight = dict(delta=np.array([-3.0, -5.0, -6.0, -5.0, -3.0, 0.0, 4.0, 8.0, 11.0, 13.0]), jaw=-4.5)
    return strike("coil", 2.2, [
        (0.55, dict(tight, root_y=-0.16, spins=ALT * 10.0)),
        (0.95, dict(tight, delta=tight["delta"] * 1.15, root_y=-0.21, spins=ALT * 13.0)),
        (1.3, dict(tight, root_y=-0.18, spins=ALT * 11.0)),
        (1.65, dict(tight, delta=tight["delta"] * 1.2, root_y=-0.22, spins=ALT * 14.0)),
    ])


def idle_b_clip() -> ck.Clip:
    """The fidget: it lifts its head, works its jaw open and snaps it shut, and shakes its head once."""
    return strike("idle_b", 1.5, [
        (0.35, dict(delta=ramp(0.0, -5.0), jaw=18.0)),
        (0.55, dict(delta=ramp(0.0, -6.0), jaw=-0.5)),
        (0.75, dict(delta=ramp(0.0, -4.0), rz=np.r_[np.zeros(6), [1.5, 2.0, 2.5, 3.0]], jaw=2.0)),
        (0.95, dict(delta=ramp(0.0, -2.0), rz=np.r_[np.zeros(6), [-1.5, -2.0, -2.5, -3.0]], jaw=3.0)),
    ])


def _frames(length: float) -> list[float]:
    return [min(f / ck.FPS, length) for f in range(int(round(length * ck.FPS)) + 1)]


def _apply_emerge(c: ck.Clip, extra: ck.Clip, sc_of_t, wobble_of_t=None) -> None:
    """Keys the spine and the root at every baked frame: the emergence at sc_of_t(t) plus `extra`'s pose."""
    for t in _frames(c.length):
        rx, ry0 = emerge(sc_of_t(t))
        mid = 0.5 * (_BS[:-1] + _BS[1:])
        out = np.clip((mid - sc_of_t(t)) / 0.6 + 0.5, 0.0, 1.0)  # how far each bone is out of the water
        for i, b in enumerate(SP):
            r, _l = extra.sample(b, t)
            wob = 0.0 if wobble_of_t is None else wobble_of_t(t, i) * out[i]
            c.key(b, t, (rx[i] + r[0], r[1], r[2] + wob))
        _r, l = extra.sample("root", t)
        c.key("root", t, (0.0, 0.0, 0.0), (0.0, ry0 + l[1], 0.0))


def intro_clip() -> ck.Clip:
    """It bursts up out of the breach and runs its body out along its own arch, the head first, straight up, then
    over and down toward the party (0-1.2 s), rears roaring with the jaw wide (1.55 s) and settles on idle's first
    frame (2.6 s)."""
    te, length = 1.2, 2.6
    p0 = idle0()
    intro = ck.Clip("intro", length)
    extra = ck.Clip("_intro", length)
    body_key(extra, 0.0, root_y=0.0)
    body_key(extra, te, root_y=0.0)
    body_key(extra, 1.55, delta=ramp(-2.0, -16.0), jaw=None, root_y=0.12)
    body_key(extra, 1.95, delta=ramp(-1.0, -9.0), root_y=0.07)
    for b in SP + ["root"]:
        r, loc = p0[b]
        extra.key(b, length, tuple(r), tuple(loc))

    def sc(t: float) -> float:
        x = min(t / te, 1.0)
        return S_HIDDEN + (S_WATER - S_HIDDEN) * (1.0 - (1.0 - x) ** 1.8)

    _apply_emerge(intro, extra, sc, lambda t, i: 3.0 * math.sin(t * 7.0 - i * 0.8) * max(1.0 - t / te, 0.0))
    for t, jaw in ((0.0, 0.0), (0.45, 6.0), (te, 30.0), (1.55, 46.0), (1.95, 36.0)):
        intro.key("jaw", t, (jaw, 0.0, 0.0))
    intro.key("jaw", length, tuple(p0["jaw"][0]))
    for k, b in enumerate(RB):
        for t, s in ((0.0, 0.0), (0.7, 1.0), (1.2, -1.0), (1.6, 0.8), (1.95, -0.4)):
            intro.key(b, t, rib_rot(k, ALT[k] * 7.0 * s, 1.5 * s))
        intro.key(b, length, tuple(p0[b][0]))
    return intro


def ko_clip() -> ck.Clip:
    """Its death throe (it rears, jaw gaping, shuddering, 0-0.75 s), then it slides back down into the breach along its
    own arch, the head last (0.75-2.3 s)."""
    length, t0, t1 = 2.4, 0.75, 2.3
    p0 = idle0()
    ko = ck.Clip("ko", length)
    extra = ck.Clip("_ko", length)
    for b in SP + ["root"]:
        r, loc = p0[b]
        extra.key(b, 0.0, tuple(r), tuple(loc))
    shudder = np.array([1.0, -1.0] * 5)
    body_key(extra, 0.45, delta=ramp(-2.0, -14.0), rz=shudder * 1.5, root_y=0.1)
    body_key(extra, 0.6, delta=ramp(-1.5, -12.0), rz=-shudder * 1.5, root_y=0.08)
    body_key(extra, t0, delta=ramp(0.0, 4.0), root_y=0.0)
    body_key(extra, 1.4, root_y=0.0)

    def sc(t: float) -> float:
        x = min(max((t - t0) / (t1 - t0), 0.0), 1.0)
        return S_WATER + (S_HIDDEN - S_WATER) * x ** 1.7

    _apply_emerge(ko, extra, sc)
    for t, jaw in ((0.0, float(p0["jaw"][0][0])), (0.45, 44.0), (0.75, 30.0), (1.6, 22.0), (length, 18.0)):
        ko.key("jaw", t, (jaw, 0.0, 0.0))
    for k, b in enumerate(RB):
        ko.key(b, 0.0, tuple(p0[b][0]))
        for t, s in ((0.45, 1.0), (0.6, -1.0), (0.9, 0.5), (length, 0.0)):
            ko.key(b, t, rib_rot(k, ALT[k] * 6.0 * s))
    return ko


def _rest_pose_mats(rig: ck.Rig, pose: dict) -> dict:
    """{bone: skinning matrix} for `pose` ({bone: (rot, loc)}), built as the kit's export builds them."""
    import grounding  # noqa: PLC0415

    mats: dict = {}
    for b in rig.bones:
        rot, loc = pose.get(b.name, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
        M = grounding._local(b.head, rot, loc)
        mats[b.name] = M if b.parent is None else mats[b.parent] @ M
    return mats


def _path_point(p: float) -> np.ndarray:
    if p >= 0.0:
        return np.array([np.interp(p, _DS, _DC[:, i]) for i in range(3)])
    return _DC[0] + p * _DT[0]


def phase_break_clip(rig: ck.Rig) -> ck.Clip:
    """`breaking` (50% HP): it thrashes, the frames wrench round the body and burst loose (0.35-0.5 s), then slide down
    its arch one after another, the lowest first, and go under through the breach (all under by 1.8 s), before
    `hide_after` hides them; the body comes back to idle's first frame."""
    length = 1.9
    d = ck.Clip("_phase_break", length)
    body_key(d, 0.0, jaw=0.0, root_y=0.0)
    for t, s, jaw in ((0.35, 1.0, 34.0), (0.6, 0.7, 28.0), (0.9, -0.5, 20.0), (1.25, 0.25, 12.0)):
        sway = np.array([3.0 if i % 2 else -3.0 for i in range(N_SPINE)]) * s
        body_key(d, t, delta=ramp(-3.0, -12.0) * abs(s), rz=sway, jaw=jaw, root_y=0.05 * abs(s))
    body_key(d, length, jaw=0.0, root_y=0.0)
    brk = ck.in_pose(d, "phase_break", {b: v for b, v in idle0().items() if not b.startswith("rib")})
    heads = {b.name: np.asarray(b.head) for b in rig.bones}
    parent = {b.name: b.parent for b in rig.bones}
    for t in _frames(length):
        pose = {b: tuple(tuple(float(v) for v in x) for x in brk.sample(b, t)) for b in SP + ["root"]}
        mats = _rest_pose_mats(rig, pose)
        for k, b in enumerate(RB):
            start, dur = 0.5 + 0.09 * k, 0.75 + 0.1 * k
            f = min(max((t - start) / dur, 0.0), 1.0) ** 1.7
            creak = 6.0 * math.sin(t * 22.0 + k) * min(t / 0.35, 1.0) if t < 0.5 else 0.0
            spin = ALT[k] * (creak + 20.0 * float(ck.smoothstep(0.35, 0.5, t)) + 70.0 * f)
            p = S_RIB[k] - (S_RIB[k] + 1.9) * f
            Rw = ck.rot_x(float(tangent_deg(p) - tangent_deg(S_RIB[k]))) @ axis_rot(_RIB_T[k], spin)
            Mw = np.eye(4)
            Mw[:3, :3] = Rw
            Mw[:3, 3] = _path_point(p) - Rw @ heads[b]
            L = np.linalg.inv(mats[parent[b]]) @ Mw
            Rl = L[:3, :3]
            loc = L[:3, 3] - heads[b] + Rl @ heads[b]
            brk.key(b, t, euler_of(Rl), tuple(loc))
    return brk


def build_clips(rig: ck.Rig) -> list[ck.Clip]:
    idle = idle_clip()

    # ready: coiled back a little inside the frames, jaw ajar, breathing fast; a loop
    ready = ck.Clip("ready", 2.0, loop=True)
    ready.wave("root", amp_loc=(0.0, 0.025, 0.0), cycles=2, base_loc=(0.0, 0.05, 0.0))
    for i, b in enumerate(SP):
        w = (i + 1) / N_SPINE
        ready.wave(b, amp_rot=(1.2, 0.0, 0.8), cycles=2, phase=-i * 0.4, base_rot=(-3.5 * w, 0.0, 0.0))
    ready.wave("jaw", amp_rot=(3.0, 0.0, 0.0), base_rot=(13.0, 0.0, 0.0), cycles=4)
    for k in range(len(RIBS)):
        ready.wave(f"rib{k}", amp_rot=(1.2, 0.0, 1.8), cycles=2, phase=-k * 0.4 - 1.0)

    # cast (no skill of its own plays it now: gnaw_coil plays `coil`): the frames spread like a trap opening, a breath
    cast = ck.Clip("cast", 1.6)
    for t, s in ((0.0, 0.0), (0.6, 1.0), (1.1, 1.0), (1.6, 0.0)):
        for k in range(len(RIBS)):
            cast.key(f"rib{k}", t, (0.0, 0.0, (9.0 if k % 2 else -9.0) * s), (0.0, 0.05 * s, 0.0))
        for i, b in enumerate(SP):
            cast.key(b, t, (-2.5 * s * (i + 1) / N_SPINE, 0, 0))
        cast.key("jaw", t, (18 * s, 0, 0))

    hit = ck.Clip("hit", 0.5)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.5, 0.0)):
        for i, b in enumerate(SP):
            hit.key(b, t, (-1.8 * s, 0, 2.0 * s * (1 if i % 2 else -1)))

    return [idle, ready, intro_clip(), gnaw_clip(), rib_lash_clip(), thrash_clip(), coil_clip(), cast, hit, ko_clip(),
            phase_break_clip(rig), idle_b_clip()]


def build(rig: ck.Rig, joints: np.ndarray) -> tuple[ck.Mesh, ck.Mesh]:
    mesh = ck.Mesh("hullgnaw")
    bd = body(mesh, rig, joints)
    dorsal_fin(mesh, bd)
    barnacles(mesh, bd)
    waterline_collar(mesh, bd)
    head(mesh, rig, joints)
    breach(mesh, rig)
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
    info = ck.export_creature(mesh, rig, build_clips(rig), args.out, extra_meshes=[frames],
                              extras={"hymn_creature": "hullgnaw"})
    print(f"hullgnaw: {info} (body {mesh.triangle_count}, frames {frames.triangle_count})")


if __name__ == "__main__":
    main()
