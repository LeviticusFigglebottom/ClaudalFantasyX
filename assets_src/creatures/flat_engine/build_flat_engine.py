"""The flat-engine, the Ch14 boss part (M3-CRE-637): docs/kb/art/creatures/act2/flat_engine.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/flat_engine/build_flat_engine.py -- \
    --out assets/creatures/flat_engine/flat_engine.glb

A bound Lit Age engine on the stern of Warden Malcor Venn's pursuit barge: a squat 1.8 m iron drum, lacquer black
with brass bands going to bronze_patina, a short chimney under a bell-shaped cowl, and a salt-glass window (+z, the
party's side) with its bound light behind it (`glimmer_bound`, steady: README rule 3). Eight 3 m paddles lie flat on
the water (y 0) in a half ring astern and abeam (+z half), each on a hinge whose one small closed `spawn_wound` mark
is a weak point (ADR 0151). It is not a creature that strikes: the paddles press the lagoon flat.

y 0 is the water. The sheet has the drum "half sunk through the deck into the water"; the build models only what is
above the water (the lagoon hides the rest at night, and a modelled underwater half would only show as a too-tall
drum on the waterless review stage and portrait), so the drum ends at the waterline in a wet skirt and every clip
stays on y 0 (tools/tests GroundedClipsTest, no ALLOW entry). Rest is the pressed pose: the paddles lie on the water,
and the idle and the stilling lift them and press them back down, never through.

Two meshes on one rig, the break part's pair (CreatureActor `break_parts`, once Ch14's combat kit names the charge
skill that breaks it): `Engine` (whole: lit window, glowing hinge marks, paddles fanned) and `EngineBroken` (the drum
split along its seam, the window cracked dark, the hinge marks dark, the paddles slack at odd angles). The drum is
two halves on their own bones, so the `ko` splits the whole mesh along the same seam.

Run without Blender (`python3 build_flat_engine.py --report`) to print the triangle count and pose bounds.
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

SEED = 6370
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "brass": "#B08D57", "bronze_patina": "#5F8A78", "salt_glass": "#BFE6E0",
    "glimmer_bound": "#4FB3B0", "timber_weathered": "#7E6A55", "spawn_wound": "#3FE0C8",
}.items()}
FLOOR = 0.114  # palette.json's albedo floor (lacquer_black, #1D1916) as an sRGB channel
UP = np.array([0.0, 1.0, 0.0])

# The drum: (radius, y) from the lid's centre down the outside to the waterline, then the flat underside in
R = 0.9  # 1.8 m across
DRUM = [(0.0, 1.30), (0.3, 1.285), (0.55, 1.26), (0.75, 1.225), (0.88, 1.19), (0.9, 1.17),
        (0.93, 1.17), (0.93, 1.10), (0.9, 1.10),  # the lid band (brass)
        (0.9, 0.86), (0.9, 0.63),
        (0.925, 0.63), (0.925, 0.55), (0.9, 0.55),  # the waist band (brass)
        (0.9, 0.34), (0.9, 0.18), (0.9, 0.0), (0.6, 0.0), (0.0, 0.0)]
BANDS = ((1.10, 1.17), (0.55, 0.63))
LID_RING = (0.55, 0.75, 1.2)  # the lid's brass ring plate: from radius, to radius, above y
WET_Y = 0.22  # wet below this (the lagoon's splash line)
SEAM_AZ = 25.0  # the seam the drum splits along, through the axis at SEAM_AZ and SEAM_AZ + 180 (degrees, +z is 0)
HALVES = (("a", SEAM_AZ - 180.0, SEAM_AZ), ("b", SEAM_AZ, SEAM_AZ + 180.0))  # (name, az from, az to)
SEAM_COL = 1.5  # degrees: the extra column each side of the seam that keeps its dark line crisp
# The window (+z, on half a): a round salt-glass porthole in a brass frame
WIN_AZ, WIN_Y, WIN_R = 0.0, 0.8, 0.2
# The chimney on the lid (half b) under its bell cowl
CHIM_AZ, CHIM_D = 160.0, 0.42  # azimuth and distance from the axis
CHIM_Y0, CHIM_Y1, CHIM_R = 1.22, 1.98, 0.11
COWL = [(0.0, 2.42), (0.08, 2.41), (0.15, 2.36), (0.2, 2.27), (0.24, 2.16), (0.29, 2.07), (0.31, 2.03),
        (0.28, 2.04), (0.21, 2.11), (0.13, 2.18), (0.0, 2.21)]  # outside from the crown to the mouth, then the inside
# The paddles: eight on hinges round the after half, fanned flat on the water astern and abeam
PADDLE_AZ = tuple(-87.5 + 25.0 * i for i in range(8))
HINGE_R, HINGE_Y = R + 0.08, 0.34  # the hinge pins' axis: this far out, this high
LENGTH = 3.0  # hinge to tip
BLADE_IN = R + 0.72  # where the blade starts (the loom meets it on top)
BLADE_Y0, BLADE_T = 0.003, 0.045  # the blade's underside on the water, its thickness
# M4-CRB-009: the broken stance is a pose of the rig (the `broken` phase's `break` clip ends on it and `idle_broken`
# holds it), so the whole and broken meshes share one rest geometry and swap without a jump at any frame. In it the
# drum stands split along its seam, each half tipped out; the stack is knocked over on its half; each paddle hangs
# slewed off the fan (degrees about the vertical through its hinge; neighbours differ by at most 18, so they never
# cross), and two are jammed up off the water on their snapped hinges.
BROKEN_SPLIT = 14.0  # degrees each half tips outward about its outer base edge
BROKEN_CHIMNEY = 24.0  # degrees the stack leans (with its cowl) about its tangent
BROKEN_SLEW = (10.0, -6.0, 8.0, -4.0, 12.0, -5.0, 9.0, -8.0)
BROKEN_LIFT = (0.0, 26.0, 0.0, 0.0, 0.0, 0.0, 34.0, 0.0)  # the jammed paddles' lift off the water
# The KO from the broken stance: the jammed paddles drop back slack, the halves sag further, the stack goes over
KO_BROKEN_SPLIT, KO_BROKEN_CHIMNEY = 17.0, 34.0
# The idle (running): a slow wave of lifts round the ring, its first frame where every one-shot starts and ends
IDLE_SEC, IDLE_AMP = 6.0, 5.0
# The stilling (`cast`, the flat pulse: plan malcor_venn.md move list): the paddles lift (0-0.7 s), press at 0.8 s
CAST_SEC, CAST_CONTACT, CAST_LIFT = 1.6, 0.8, 16.0
INTRO_SEC = 2.6
BREAK_SEC, BREAK_CONTACT = 2.8, 0.6  # the break; the seam cracks open at its contact (the first ripple's cue)
WOUND_PADDLE = 3  # the hinge vfx_wound marks: the near one left of the window


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def az_dirs(th: float) -> tuple[np.ndarray, np.ndarray]:
    """Outward and tangent directions at azimuth th (degrees); a positive turn about the tangent tips up -> out."""
    t = math.radians(th)
    return np.array([math.sin(t), 0.0, math.cos(t)]), np.array([math.cos(t), 0.0, -math.sin(t)])


def rot_axis(axis, deg: float) -> np.ndarray:
    k = np.asarray(axis, dtype=np.float64)
    k = k / np.linalg.norm(k)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * (K @ K)


def euler_of(R_: np.ndarray) -> tuple[float, float, float]:
    ry = math.asin(float(np.clip(-R_[2, 0], -1.0, 1.0)))
    rx = math.atan2(R_[2, 1], R_[2, 2])
    rz = math.atan2(R_[1, 0], R_[0, 0])
    out = (math.degrees(rx), math.degrees(ry), math.degrees(rz))
    assert np.allclose(ck.euler(*out), R_, atol=1e-9)
    return out


def axis_euler(axis, deg: float) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees, X then Y then Z about the rest axes (ck.euler), of a rotation by `deg` about `axis`."""
    return euler_of(rot_axis(axis, deg))


def orient(P: np.ndarray, T: np.ndarray, ref) -> np.ndarray:
    """Flips the triangles whose normal points against `ref` (one direction per triangle, or one for all)."""
    n = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    ref = np.broadcast_to(np.asarray(ref, dtype=np.float64), n.shape)
    bad = np.einsum("ij,ij->i", n, ref) < 0.0
    T = T.copy()
    T[bad] = T[bad][:, ::-1]
    return T


class Xf:
    """A rigid placement p -> R (p - c) + c + d, composed left to right with `then`."""

    def __init__(self, R_=None, c=(0.0, 0.0, 0.0), d=(0.0, 0.0, 0.0)) -> None:
        self.R = np.eye(3) if R_ is None else np.asarray(R_, dtype=np.float64)
        self.c = np.asarray(c, dtype=np.float64)
        self.d = np.asarray(d, dtype=np.float64)

    def __call__(self, P) -> np.ndarray:
        P = np.asarray(P, dtype=np.float64)
        return (P - self.c) @ self.R.T + self.c + self.d

    def then(self, other: "Xf") -> "Xf":
        """This placement followed by `other`, as one."""
        R_ = other.R @ self.R
        # p -> other(self(p)); find c', d' with c' = 0: p -> R_ p + t
        t = other(self(np.zeros((1, 3))))[0]
        return Xf(R_, (0.0, 0.0, 0.0), t)


ID = Xf()


def arc_lathe(profile, az0: float, az1: float, segs: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A partial surface of revolution from az0 to az1 (degrees), with an extra column SEAM_COL in from each end.
    Returns (P, T, az of each vertex)."""
    inner = np.linspace(az0 + SEAM_COL, az1 - SEAM_COL, segs - 1)
    azs = np.concatenate([[az0], inner, [az1]])
    a = np.radians(azs)
    rows = [np.column_stack([r * np.sin(a), np.full(len(a), y), r * np.cos(a)]) for r, y in profile]
    return np.vstack(rows), ck.grid_tris(len(profile), len(a), False), np.tile(azs, len(profile))


def half_axis(half: str) -> tuple[np.ndarray, np.ndarray]:
    """The line a half tips outward about: (a point, the direction), the tangent at its far base point."""
    a0, a1 = next((h[1], h[2]) for h in HALVES if h[0] == half)
    o, t = az_dirs(0.5 * (a0 + a1))
    return o * R, t


def lift_axis(i: int) -> np.ndarray:
    """The axis a paddle lifts about (its hinge pin): a positive turn raises the blade off the water."""
    _, t = az_dirs(PADDLE_AZ[i])
    return -t


def hinge_pt(i: int) -> np.ndarray:
    o, _ = az_dirs(PADDLE_AZ[i])
    return o * HINGE_R + UP * HINGE_Y


def half_of(az: float) -> str:
    return "a" if HALVES[0][1] <= az <= HALVES[0][2] else "b"


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def chim_base() -> np.ndarray:
    o, _ = az_dirs(CHIM_AZ)
    return o * CHIM_D + UP * CHIM_Y0


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("drum", (0, 0, 0), (0, 1.3, 0), "root")
    for h, _, _ in HALVES:
        p, _ = half_axis(h)
        rig.add(f"half_{h}", p, p + UP * 0.6, "drum")
    c = chim_base()
    rig.add("chimney", c, c + UP * 0.8, "half_b")
    for i, az in enumerate(PADDLE_AZ):
        o, _ = az_dirs(az)
        h = hinge_pt(i)
        rig.add(f"paddle{i}", h, h + o * 0.4, f"half_{half_of(az)}")
    # M4-CRB-009, the VFX anchors (unweighted): the near hinge's mark (where hits land and the weak point is), the
    # window (the bound light: the break's going-dark), and the seam's face toward the party (where it cracks open)
    w = hinge_pt(WOUND_PADDLE) + az_dirs(PADDLE_AZ[WOUND_PADDLE])[0] * 0.05
    rig.add("vfx_wound", w, w + az_dirs(PADDLE_AZ[WOUND_PADDLE])[0] * 0.15, f"paddle{WOUND_PADDLE}")
    o, _ = az_dirs(WIN_AZ)
    c = o * (R + 0.05) + UP * WIN_Y
    rig.add("vfx_core", c, c + o * 0.2, "half_a")
    o, _ = az_dirs(SEAM_AZ)
    s = o * (R + 0.02) + UP * 0.8
    rig.add("vfx_phase", s, s + o * 0.2, "drum")
    return rig


# ---------------------------------------------------------------------------------------------
# Surfaces
# ---------------------------------------------------------------------------------------------
def iron(P: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Lacquer-black iron, a little mottled; wet and darker below the splash line. Returns (colour, wet)."""
    n = ck.fbm(P * 4.0, seed)
    col = PAL["lacquer_black"] * (1.05 + 0.3 * (n + 0.5))[:, None]
    wet = ck.smoothstep(WET_Y + 0.06, WET_Y - 0.08, P[:, 1] + 0.04 * n)
    return np.clip(col, FLOOR, 1.0), np.maximum(wet, 0.12)


def brass(P: np.ndarray, seed: int, polish: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Brass going to bronze_patina in runs. Returns (colour, patina amount)."""
    n = ck.fbm(P * 3.5, seed)
    col = PAL["brass"] * (0.84 + 0.14 * (n + 0.5) + 0.06 * polish)[:, None]
    pat = np.clip(0.35 + 0.6 * ck.smoothstep(-0.1, 0.25, ck.fbm(P * np.array([5.0, 1.2, 5.0]), seed + 1)), 0.0, 0.9)
    pat = pat * (1.0 - 0.5 * polish)
    col = ck.mix(col, PAL["bronze_patina"] * (0.85 + 0.15 * (n + 0.5))[:, None], pat[:, None])
    return np.clip(col, FLOOR, 0.92), pat


def part_iron(mesh, P, T, bone, seed, cav=0.0, flat=False) -> None:
    col, wet = iron(P, seed)
    ck.finish(mesh, P, T, "iron", col, bone, wet=wet, cavity=cav, flat=flat)


def part_brass(mesh, P, T, bone, seed, polish=0.0, cav=0.0) -> None:
    col, pat = brass(P, seed, polish)
    wet = ck.smoothstep(WET_Y + 0.06, WET_Y - 0.08, P[:, 1])
    ck.finish(mesh, P, T, "iron", col, bone, wet=np.maximum(wet, 0.1), cavity=cav + 0.2 * pat)


# ---------------------------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------------------------
def drum_half(mesh: ck.Mesh, rig: ck.Rig, half: str, xf: Xf) -> None:
    """One half of the drum: its outside (iron, the two brass bands, the seam's dark line), and the flat seam faces
    that close it (hidden while whole, the split's raw iron when it opens)."""
    a0, a1 = next((h[1], h[2]) for h in HALVES if h[0] == half)
    bone = rig.rigid(f"half_{half}")
    P, T, az = arc_lathe(DRUM, a0, a1, 12)
    col, wet = iron(P, SEED + (1 if half == "a" else 2))
    bcol, pat = brass(P, SEED + 3)
    y = P[:, 1]
    r = np.hypot(P[:, 0], P[:, 2])
    band = np.zeros(len(P))
    for lo, hi in BANDS:
        band = np.maximum(band, ((y >= lo - 1e-6) & (y <= hi + 1e-6) & (r > R + 1e-6)).astype(float))
    # M4-CRB-009: a brass ring plate on the lid (from the battle camera's height the lid was one black disc)
    band = np.maximum(band, ((y > LID_RING[2]) & (r > LID_RING[0] - 1e-6) & (r < LID_RING[1] + 1e-6)).astype(float))
    col = ck.mix(col, bcol, band[:, None])
    seam = ((np.abs(az - a0) < 1e-6) | (np.abs(az - a1) < 1e-6)) & (r > 0.5)
    col = np.where(seam[:, None], np.clip(PAL["lacquer_black"] * 0.9, FLOOR, 1.0), col)
    # bronze_patina weeps down from each band onto the black iron
    weep = ck.smoothstep(0.2, 0.45, ck.fbm(P * np.array([6.0, 0.6, 6.0]), SEED + 4)) * (1.0 - band) * (r > R - 1e-6)
    below = np.zeros(len(P))
    for lo, _ in BANDS:
        below = np.maximum(below, ck.smoothstep(lo - 0.35, lo, y) * (y < lo))
    col = ck.mix(col, PAL["bronze_patina"] * 0.6, (0.5 * weep * below)[:, None])
    cav = 0.6 * seam + 0.15 * band
    Pw = xf(P)
    ck.finish(mesh, Pw, T, "iron", col, bone, wet=np.maximum(wet, 0.3 * band * (y < WET_Y)), cavity=cav)
    # the seam faces: the profile's cross-section at each end, fanned from a point inside
    poly = np.array(DRUM)
    for az_end, sgn in ((a0, -1.0), (a1, 1.0)):
        o, t = az_dirs(az_end)
        ctr = np.array([0.45, 0.62])
        pts = np.vstack([[ctr], poly])
        Pc = np.array([o * rr + UP * yy for rr, yy in pts])
        n = len(poly)
        Tc = np.array([(0, 1 + k, 1 + (k + 1) % n) for k in range(n)], dtype=np.int64)
        Tc = orient(Pc, Tc, sgn * t)
        Pcw = xf(Pc)
        # M4-CRB-009: the drum is plated inside with brass (a Lit Age engine's bright works), so the split shows a
        # raw brass face against the black iron: at night, at battle distance, the open seam reads as broken
        col, pat = brass(Pc, SEED + 5, polish=0.8)
        rim = ck.smoothstep(0.3, 0.05, np.hypot(np.hypot(Pc[:, 0], Pc[:, 2]) - 0.45, Pc[:, 1] - 0.62))
        col = ck.mix(np.clip(PAL["lacquer_black"] * 1.2, FLOOR, 1.0), col, (0.35 + 0.65 * rim)[:, None])
        ck.finish(mesh, Pcw, Tc, "iron", col, bone, wet=0.1, cavity=0.3 + 0.2 * pat, flat=True)


def window(mesh: ck.Mesh, rig: ck.Rig, xf: Xf, broken: bool) -> None:
    """The salt-glass porthole and its brass frame. Whole: the bound light behind it (glimmer_bound, steady).
    Broken: the glass crazed into facets, dark."""
    rng = np.random.default_rng(SEED + 20)
    o, t = az_dirs(WIN_AZ)
    Rw = np.column_stack([t, UP, o])  # local x along the tangent, y up, z outward
    ctr = o * R + UP * WIN_Y
    bone = rig.rigid("half_a")

    def place(P):
        return xf(ck.transform(P, Rw, ctr))

    # the frame: a brass ring standing proud of the drum
    a = np.radians(np.linspace(0.0, 360.0, 17)[:-1])
    ring = np.column_stack([WIN_R * np.cos(a), WIN_R * np.sin(a), np.full(len(a), 0.035)])
    ring = np.vstack([ring, ring[:1]])
    P, T = ck.tube(ring, 0.032, 5, cap_start=False, cap_end=False)
    col, pat = brass(ck.transform(P, Rw, ctr), SEED + 21, polish=0.6)
    ck.finish(mesh, place(P), T, "iron", col, bone, wet=0.15, cavity=0.15 * pat)
    # a backing plate between the frame and the drum
    prof = [(WIN_R + 0.05, -0.03), (WIN_R + 0.02, 0.025), (WIN_R - 0.02, 0.025)]
    P, T = ck.lathe(prof, 16)
    P = P[:, [0, 2, 1]]  # the lathe's axis onto local z
    T = orient(P, T, np.array([0.0, 0.0, 1.0]))
    col, _ = iron(ck.transform(P, Rw, ctr), SEED + 22)
    ck.finish(mesh, place(P), T, "iron", col, bone, wet=0.15, cavity=0.3)
    # the glass: a shallow dome
    prof = [(0.0, 0.05), (0.06, 0.047), (0.12, 0.04), (0.17, 0.03), (WIN_R - 0.01, 0.022)]
    P, T = ck.lathe(prof, 16)
    P = P[:, [0, 2, 1]]
    T = orient(P, T, np.array([0.0, 0.0, 1.0]))
    rr = np.hypot(P[:, 0], P[:, 1])
    if broken:
        P = P.copy()
        P[:, 2] -= rng.uniform(0.0, 0.018, len(P)) * (rr > 0.01)  # crazed: every vertex knocked in a little
        n = ck.fbm(P * 30.0, SEED + 23)
        col = ck.mix(PAL["salt_glass"] * 0.3, PAL["lacquer_black"], (0.5 + 0.5 * ck.smoothstep(-0.1, 0.2, n))[:, None])
        ck.finish(mesh, place(P), T, "window", np.clip(col, FLOOR, 1.0), bone, wet=0.4, cavity=0.4, emission=0.0,
                  flat=True)
        return
    glow = 0.75 + 0.25 * ck.smoothstep(WIN_R, 0.0, rr)  # brightest at the centre, where the light is held
    col = ck.mix(PAL["salt_glass"], PAL["glimmer_bound"], (0.55 * glow)[:, None])
    ck.finish(mesh, place(P), T, "window", col, bone, wet=0.5, emission=glow)


def chimney(mesh: ck.Mesh, rig: ck.Rig, xf: Xf) -> None:
    """A short iron stack with brass collars, and a brass bell cowl held over its mouth on three struts."""
    bone = rig.rigid("chimney")
    c = chim_base()
    off = c - UP * c[1]
    P, T = ck.lathe([(CHIM_R, CHIM_Y1), (CHIM_R, 1.6), (CHIM_R, CHIM_Y0)], 12)
    P = P + off
    col, wet = iron(P, SEED + 30)
    soot = ck.smoothstep(1.75, CHIM_Y1, P[:, 1])
    col = ck.mix(col, np.clip(PAL["lacquer_black"] * 0.95, FLOOR, 1.0), soot[:, None])
    ck.finish(mesh, xf(P), T, "iron", col, bone, wet=wet, cavity=0.2 * soot)
    for y0, y1 in ((1.27, 1.33), (1.88, 1.93)):  # the collars
        P, T = ck.lathe([(CHIM_R, y1 + 0.01), (CHIM_R + 0.025, y1), (CHIM_R + 0.025, y0), (CHIM_R, y0 - 0.01)], 10)
        P = P + off
        part_brass(mesh, xf(P), T, bone, SEED + 31, polish=0.3)
    # the stack's mouth, dark inside
    P, T = ck.lathe([(CHIM_R - 0.02, CHIM_Y1 - 0.12), (CHIM_R - 0.02, CHIM_Y1), (CHIM_R, CHIM_Y1)], 12)
    P = P + off
    ck.finish(mesh, xf(P), T, "iron", np.clip(PAL["lacquer_black"], FLOOR, 1.0), bone, cavity=0.8)
    # the bell cowl, sooty underneath
    P, T = ck.lathe(COWL, 12)
    P = P + off
    col, pat = brass(P, SEED + 32, polish=0.2)
    under = np.repeat(np.arange(len(COWL)) >= 7, 12)
    col = np.where(under[:, None], np.clip(PAL["lacquer_black"] * 1.1, FLOOR, 1.0), col)
    ck.finish(mesh, xf(P), T, "iron", col, bone, wet=0.15, cavity=np.where(under, 0.7, 0.15 * pat))
    for k in range(3):  # the struts
        o, _ = az_dirs(CHIM_AZ + 30.0 + 120.0 * k)
        a, b = off + o * (CHIM_R - 0.01) + UP * (CHIM_Y1 - 0.03), off + o * 0.2 + UP * 2.12
        P, T = ck.tube(np.array([a, b]), 0.012, 5, cap_start=False, cap_end=False)
        part_iron(mesh, xf(P), T, bone, SEED + 33)


def hinge(mesh: ck.Mesh, rig: ck.Rig, i: int, xf: Xf, broken: bool) -> None:
    """A paddle's hinge: a brass bracket off the drum, a lacquered pin barrel along the tangent, and on the barrel's
    outer face one small closed spawn_wound mark (the weak point, ADR 0151); dark once broken."""
    az = PADDLE_AZ[i]
    o, t = az_dirs(az)
    h = hinge_pt(i)
    half = rig.rigid(f"half_{half_of(az)}")
    pad = rig.rigid(f"paddle{i}")
    for s in (-1.0, 1.0):  # the bracket's two cheeks, on the drum
        a = o * (R - 0.02) + UP * HINGE_Y + s * 0.08 * t
        P, T = ck.tube(np.array([a, h + s * 0.08 * t]), 0.04, 6, cap_start=False)
        part_brass(mesh, xf(P), T, half, SEED + 40 + i)
    P, T = ck.tube(np.array([h - 0.13 * t, h + 0.13 * t]), 0.038, 6)
    col, wet = iron(P, SEED + 41)
    ck.finish(mesh, xf(P), T, "iron", col, half, wet=np.maximum(wet, 0.3), cavity=0.2)
    # the mark: a small flat lozenge on the barrel's outside, on the paddle (it turns with the pin)
    Rl = np.column_stack([t, UP, o])
    P, T = ck.ellipsoid((0.0, 0.0, 0.0), (0.03, 0.02, 0.008), 3, 6)
    P = ck.transform(P, Rl, h + o * 0.04)
    if broken:
        ck.finish(mesh, xf(P), T, "hinge", np.clip(PAL["spawn_wound"] * 0.18, FLOOR, 1.0), pad, wet=0.3,
                  emission=0.0)
    else:
        ck.finish(mesh, xf(P), T, "hinge", PAL["spawn_wound"] * 0.6, pad, wet=0.4, emission=1.0)


def slab(stations: list[tuple[float, float]], y0: float, y1: float) -> tuple[np.ndarray, np.ndarray]:
    """A flat board along +x: `stations` (x, half width); its underside at y0, its top at y1. Local frame."""
    xs = np.array([s[0] for s in stations])
    hw = np.array([s[1] for s in stations])
    n = len(xs)
    top = np.stack([np.column_stack([xs, np.full(n, y1), -hw * f]) for f in (-1.0, 0.0, 1.0)], axis=1).reshape(-1, 3)
    bot = top.copy()
    bot[:, 1] = y0
    G = ck.grid_tris(n, 3, False)
    Tt = orient(top, G, UP)
    Tb = orient(bot, G, -UP) + len(top)
    loop = [(0, c) for c in range(3)] + [(r, 2) for r in range(1, n)] + [(n - 1, 1), (n - 1, 0)] + \
        [(r, 0) for r in range(n - 2, 0, -1)]
    idx = np.array([r * 3 + c for r, c in loop])
    P = np.vstack([top, bot])
    ring = np.vstack([P[idx], P[idx + len(top)]])
    Ts = ck.grid_tris(2, len(idx), True)
    mid = np.array([xs.mean(), 0.5 * (y0 + y1), 0.0])
    Ts = orient(ring, Ts, ring[Ts].mean(axis=1) - mid) + len(P)
    return np.vstack([P, ring]), np.vstack([Tt, Tb, Ts])


def paddle(mesh: ck.Mesh, rig: ck.Rig, i: int, xf: Xf) -> None:
    """A 3 m paddle: an iron-strapped loom down from the hinge onto a long flat blade lying on the water, timber
    darkened wet (all of the blade, the loom to the splash line)."""
    az = PADDLE_AZ[i]
    o, t = az_dirs(az)
    Rl = np.column_stack([o, UP, -t])  # local x outward, y up, z = -tangent (right-handed: x cross y = z)
    pad = rig.rigid(f"paddle{i}")
    base = UP * 0.0

    def place(P):
        return xf(ck.transform(P, Rl, base))

    tip = HINGE_R + LENGTH
    st = [(BLADE_IN, 0.09), (BLADE_IN + 0.25, 0.12), (BLADE_IN + 0.7, 0.15), (BLADE_IN + 1.2, 0.18),
          (BLADE_IN + 1.7, 0.2), (tip - 0.25, 0.2), (tip - 0.07, 0.17), (tip, 0.11)]
    P, T = slab(st, BLADE_Y0, BLADE_Y0 + BLADE_T)
    grain = ck.fbm(P * np.array([0.8, 6.0, 14.0]), SEED + 50 + i)
    Pw = ck.transform(P, Rl, base)
    col = PAL["timber_weathered"] * (0.7 + 0.2 * (grain + 0.5))[:, None]
    ck.finish(mesh, place(P), T, "timber", np.clip(col, FLOOR, 1.0), pad, wet=0.75 + 0.25 * (Pw[:, 1] < 0.02),
              cavity=0.15 * ck.smoothstep(0.0, 0.3, grain), flat=True)
    # the loom: from the hinge pin out and down onto the blade's top
    a = np.array([HINGE_R + 0.02, HINGE_Y, 0.0])
    b = np.array([BLADE_IN + 0.3, BLADE_Y0 + BLADE_T + 0.025, 0.0])
    path = np.linspace(a, b, 4)
    P, T = ck.tube(path, np.linspace(0.045, 0.035, 4), 6, cap_start=False)
    Pw = ck.transform(P, Rl, base)
    col = PAL["timber_weathered"] * (0.8 + 0.15 * (ck.fbm(P * 8.0, SEED + 60 + i) + 0.5))[:, None]
    wet = ck.smoothstep(0.16, 0.04, Pw[:, 1])
    ck.finish(mesh, place(P), T, "timber", np.clip(col, FLOOR, 1.0), pad, wet=np.maximum(wet, 0.25))
    # the iron strap where the loom meets the blade
    s0 = b + np.array([-0.16, 0.0, 0.0])
    P, T = ck.tube(np.array([s0, s0 + np.array([0.08, -0.02, 0.0])]), 0.05, 6)
    part_iron(mesh, place(P), T, pad, SEED + 61)


def build_variant(rig: ck.Rig, broken: bool) -> ck.Mesh:
    """M4-CRB-009: both meshes at the same rest geometry; the broken one's window is cracked dark and its hinge marks
    are out. Its split, toppled, slack shape is the broken stance's pose (`break`, `idle_broken`), so the swap at the
    break's first frame changes only the lights."""
    mesh = ck.Mesh("EngineBroken" if broken else "Engine")
    for h, _, _ in HALVES:
        drum_half(mesh, rig, h, ID)
    window(mesh, rig, ID, broken)
    chimney(mesh, rig, ID)
    for i in range(len(PADDLE_AZ)):
        hinge(mesh, rig, i, ID, broken)
        paddle(mesh, rig, i, ID)
    return mesh


def build_meshes(rig: ck.Rig) -> tuple[ck.Mesh, list[ck.Mesh]]:
    return build_variant(rig, False), [build_variant(rig, True)]


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
def lift(clip: ck.Clip, i: int, t: float, deg: float, slew: float = 0.0) -> None:
    """Paddle i turned `deg` up off the water about its pin, after slewing `slew` degrees about the vertical."""
    R_ = rot_axis(lift_axis(i), deg) @ ck.rot_y(slew)
    clip.key(f"paddle{i}", t, euler_of(R_))


def idle_lift(i: int, t: float) -> float:
    """The running idle's lift of paddle i at t: a slow wave of presses round the ring."""
    return IDLE_AMP * 0.5 * (1.0 - math.cos(2.0 * math.pi * (t / IDLE_SEC - i / 8.0)))


I0 = tuple(idle_lift(i, 0.0) for i in range(8))  # the idle's first frame: every one-shot starts and ends here


def tc_chim() -> np.ndarray:
    return az_dirs(CHIM_AZ)[1]


def key_halves(c: ck.Clip, t: float, deg: float) -> None:
    for h, _, _ in HALVES:
        c.key(f"half_{h}", t, axis_euler(half_axis(h)[1], deg))


def key_chimney(c: ck.Clip, t: float, deg: float) -> None:
    c.key("chimney", t, axis_euler(tc_chim(), deg))


def paddles(c: ck.Clip, keys) -> None:
    """keys: per paddle a list of (t, lift, slew) or a function i -> that list."""
    for i in range(8):
        for t, deg, sl in (keys(i) if callable(keys) else keys):
            lift(c, i, t, deg, sl)


def stilling(name: str) -> ck.Clip:
    """`cast` (the stilling, the flat pulse): from the idle every paddle lifts together, higher and higher (0-0.7 s,
    the telegraph), then all press down flat at 0.8 s and hold the water still; the drum rises and leans back on the
    lift and drops as they press; the cowl jolts. `attack` is the same clip (the sheet: it never strikes)."""
    c = ck.Clip(name, CAST_SEC)
    paddles(c, lambda i: ((0.0, I0[i], 0.0), (0.2, I0[i] + 2.0, 0.0), (0.7, CAST_LIFT, 0.0),
                          (CAST_CONTACT, 0.0, 0.0), (0.95, 1.5, 0.0), (1.1, 0.0, 0.0), (1.25, 0.0, 0.0),
                          (CAST_SEC, I0[i], 0.0)))
    for t, dy, rx in ((0.0, 0.0, 0.0), (0.7, 0.045, -1.2), (CAST_CONTACT, 0.0, 0.0), (0.9, 0.015, 0.5),
                      (1.05, 0.0, 0.0), (CAST_SEC, 0.0, 0.0)):
        c.key("drum", t, (rx, 0.0, 0.0), (0.0, dy, 0.0))
    for t, deg in ((0.0, 0.0), (0.7, -2.0), (0.82, 4.5), (0.97, -2.0), (1.15, 1.0), (1.35, 0.0), (CAST_SEC, 0.0)):
        key_chimney(c, t, deg)
    return c


def hit_clip(name: str, sgn: float, kick: int, amp: float) -> ck.Clip:
    """M3-CRE-617: the drum jolts back and one paddle kicks up; the peak at 0.1 s; from the idle's first frame."""
    c = ck.Clip(name, 0.7)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.22, -0.4), (0.36, 0.18), (0.5, -0.06), (0.7, 0.0)):
        m = s * amp
        c.key("drum", t, (-3.0 * m, 0.0, 1.6 * m * sgn), (0.0, 0.02 * max(m, 0.0), 0.0))
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.26, -0.5), (0.42, 0.2), (0.7, 0.0)):
        key_chimney(c, t, -6.0 * s * amp)
    for i in range(8):
        ks = ((0.0, 0.0), (0.1, 24.0), (0.24, 7.0), (0.38, 11.0), (0.55, 2.0), (0.7, 0.0)) if i == kick else \
            ((0.0, 0.0), (0.1, 2.0), (0.3, 0.5), (0.7, 0.0))
        for t, deg in ks:
            lift(c, i, t, I0[i] + deg * amp)
    return c


def broken_hit(name: str, sgn: float, kick: int, amp: float) -> ck.Clip:
    """The broken stance's hit: the split drum jolts, its halves rock open, the fallen stack rattles, and one slack
    paddle kicks; from and back to the broken stance."""
    c = ck.Clip(name, 0.7)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.22, -0.4), (0.36, 0.18), (0.5, -0.06), (0.7, 0.0)):
        m = s * amp
        c.key("drum", t, (-2.5 * m, 0.0, 1.2 * m * sgn), (0.0, 0.015 * max(m, 0.0), 0.0))
        key_halves(c, t, BROKEN_SPLIT + 1.5 * m)
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.26, -0.5), (0.42, 0.2), (0.7, 0.0)):
        key_chimney(c, t, BROKEN_CHIMNEY + 5.0 * s * amp)
    for i in range(8):
        ks = ((0.0, 0.0), (0.1, 16.0), (0.24, 4.0), (0.38, 7.0), (0.55, 1.0), (0.7, 0.0)) if i == kick else \
            ((0.0, 0.0), (0.1, 2.0), (0.3, 0.5), (0.7, 0.0))
        for t, deg in ks:
            lift(c, i, t, BROKEN_LIFT[i] + deg * amp, BROKEN_SLEW[i])
    return c


def build_clips() -> list[ck.Clip]:
    # idle (running): the paddles lift and press back in a slow wave round the ring, the drum throbs, the cowl sways
    idle = ck.Clip("idle", IDLE_SEC, loop=True)
    n = 12
    paddles(idle, lambda i: [(IDLE_SEC * s / n, idle_lift(i, IDLE_SEC * s / n), 0.0) for s in range(n + 1)])
    for s in range(n + 1):
        t = IDLE_SEC * s / n
        key_chimney(idle, t, 0.8 * math.sin(2.0 * math.pi * s / n))
        idle.key("drum", t, loc=(0.0, 0.004 * 0.5 * (1.0 - math.cos(4.0 * math.pi * s / n)), 0.0))

    # idle_b (the fidget): the governor knocks twice; the drum jumps, the cowl rattles, the wave hitches
    idle_b = ck.Clip("idle_b", 1.6)
    paddles(idle_b, lambda i: ((0.0, I0[i], 0.0), (0.3, I0[i] + 3.0, 0.0), (0.55, I0[i], 0.0),
                               (0.85, I0[i] + 2.0, 0.0), (1.2, I0[i], 0.0), (1.6, I0[i], 0.0)))
    for t, dy, rz in ((0.0, 0.0, 0.0), (0.25, 0.018, 0.8), (0.4, 0.0, -0.3), (0.75, 0.012, -0.6), (0.9, 0.0, 0.2),
                      (1.1, 0.0, 0.0), (1.6, 0.0, 0.0)):
        idle_b.key("drum", t, (0.0, 0.0, rz), (0.0, dy, 0.0))
    for t, deg in ((0.0, 0.0), (0.27, 3.0), (0.4, -2.0), (0.55, 1.0), (0.77, 2.5), (0.92, -1.5), (1.15, 0.5),
                   (1.6, 0.0)):
        key_chimney(idle_b, t, deg)

    # intro (under the boss camera's hold on `the_engine`): every paddle rises off the water together, slowly, the
    # drum lifting with them, a held breath; then all slam down flat at once (the Warden plants his rod) and the
    # water goes still; it settles into the running wave
    intro = ck.Clip("intro", INTRO_SEC)
    paddles(intro, lambda i: ((0.0, I0[i], 0.0), (0.3, I0[i], 0.0), (1.45, 20.0, 0.0), (1.7, 19.0, 0.0),
                              (1.95, 0.0, 0.0), (2.05, 2.0, 0.0), (2.2, 0.0, 0.0), (INTRO_SEC, I0[i], 0.0)))
    for t, dy, rx in ((0.0, 0.0, 0.0), (0.3, 0.0, 0.0), (1.45, 0.05, -1.5), (1.7, 0.05, -1.5), (1.95, 0.0, 0.5),
                      (2.08, 0.02, -0.4), (2.25, 0.0, 0.0), (INTRO_SEC, 0.0, 0.0)):
        intro.key("drum", t, (rx, 0.0, 0.0), (0.0, dy, 0.0))
    for t, deg in ((0.0, 0.0), (1.45, -3.0), (1.7, -3.0), (1.97, 6.0), (2.12, -3.0), (2.3, 1.2), (INTRO_SEC, 0.0)):
        key_chimney(intro, t, deg)

    # ready (looped while it waits its turn): the paddles held a hand off the water, trembling, the drum up
    ready = ck.Clip("ready", 1.4, loop=True)
    paddles(ready, lambda i: ((0.0, I0[i], 0.0), (0.35, 6.0 + 0.5 * (i % 2), 0.0), (0.7, 5.0, 0.0),
                              (1.05, 6.5 - 0.5 * (i % 2), 0.0), (1.4, I0[i], 0.0)))
    for t, dy in ((0.0, 0.0), (0.35, 0.012), (1.05, 0.012), (1.4, 0.0)):
        ready.key("drum", t, loc=(0.0, dy, 0.0))
    for t, deg in ((0.0, 0.0), (0.4, -1.2), (0.7, 0.6), (1.0, -1.0), (1.4, 0.0)):
        key_chimney(ready, t, deg)

    cast = stilling("cast")
    attack = stilling("attack")
    hit = hit_clip("hit", 1.0, 3, 1.0)
    hit_b = hit_clip("hit_b", -1.0, 5, 1.25)

    # break (the `broken` phase's clip; Liss's blow): the strike jolts the drum and kicks the near paddles; at 0.6 s
    # the seam cracks open (the window is already dark: the phase swaps in the broken mesh on this clip's first frame)
    # and the halves fall apart; the stack topples over on its half; the paddles go slack one by one, slewing off the
    # fan, two jamming up on their snapped hinges; it ends on the broken stance (idle_broken's first frame)
    brk = ck.Clip("break", BREAK_SEC)
    for t, rx, rz, dy in ((0.0, 0.0, 0.0, 0.0), (0.1, -4.0, 2.0, 0.03), (0.25, 1.5, -1.5, 0.0), (0.4, -1.0, 1.0, 0.015),
                          (0.55, 0.0, 0.0, 0.0), (0.64, 0.0, -1.2, 0.02), (0.78, 0.0, 0.8, 0.0), (0.92, 0.0, 0.0, 0.0),
                          (BREAK_SEC, 0.0, 0.0, 0.0)):
        brk.key("drum", t, (rx, 0.0, rz), (0.0, dy, 0.0))
    for t, deg in ((0.0, 0.0), (0.5, 0.0), (BREAK_CONTACT, 3.0), (0.7, 2.0), (1.2, BROKEN_SPLIT + 1.5),
                   (1.45, BROKEN_SPLIT - 0.5), (1.65, BROKEN_SPLIT), (BREAK_SEC, BROKEN_SPLIT)):
        key_halves(brk, t, deg)
    for t, deg in ((0.0, 0.0), (0.12, -6.0), (0.3, 3.0), (BREAK_CONTACT, 0.0), (0.9, 6.0),
                   (1.5, BROKEN_CHIMNEY + 4.0), (1.75, BROKEN_CHIMNEY - 2.0), (1.95, BROKEN_CHIMNEY),
                   (BREAK_SEC, BROKEN_CHIMNEY)):
        key_chimney(brk, t, deg)

    def slack(i: int) -> list:
        t0 = 0.65 + 0.09 * i
        kick = 14.0 if i in (3, 4) else 3.0
        out = [(0.0, I0[i], 0.0), (0.1, I0[i] + kick, 0.0), (0.3, 0.5 * I0[i], 0.0), (t0, 5.0, 0.0),
               (t0 + 0.3, 0.6 * BROKEN_LIFT[i] + 1.0, 0.4 * BROKEN_SLEW[i])]
        if BROKEN_LIFT[i] > 0.0:
            out.append((t0 + 0.55, BROKEN_LIFT[i] + 6.0, 0.85 * BROKEN_SLEW[i]))
        return out + [(t0 + 0.8, BROKEN_LIFT[i], BROKEN_SLEW[i]), (BREAK_SEC, BROKEN_LIFT[i], BROKEN_SLEW[i])]

    paddles(brk, slack)

    # idle_broken (the broken stance, looped): nothing runs; the slack paddles rock a little on the water, the jammed
    # ones tremble, the toppled stack creaks. Its first frame is the broken pose exactly
    idle_broken = ck.Clip("idle_broken", 5.0, loop=True)
    for s in range(n + 1):
        u = 2.0 * math.pi * s / n
        t = 5.0 * s / n
        for i in range(8):
            ph = 1.7 * i
            amp = 1.5 if BROKEN_LIFT[i] > 0.0 else 1.0
            lift(idle_broken, i, t, BROKEN_LIFT[i] + amp * (math.sin(u + ph) - math.sin(ph)),
                 BROKEN_SLEW[i] + 0.8 * (math.sin(u + ph + 1.0) - math.sin(ph + 1.0)))
        key_chimney(idle_broken, t, BROKEN_CHIMNEY + 0.6 * math.sin(u))
        key_halves(idle_broken, t, BROKEN_SPLIT)
    hit_broken = broken_hit("hit_broken", 1.0, 6, 1.0)
    hit_b_broken = broken_hit("hit_b_broken", -1.0, 1, 1.25)

    # ko (the stop, whole): the wave stops, the paddles sag flat on the water, the drum shudders and settles listing,
    # the stack rocks and stays leaning; then the KO fade
    ko = ck.Clip("ko", 2.4)
    paddles(ko, lambda i: ((0.0, I0[i], 0.0), (0.12, I0[i] + 2.0, 0.0), (0.5, 0.0, 0.0), (0.7, 1.0, 0.0),
                           (1.0, 0.0, 0.0), (2.4, 0.0, 0.0)))
    for t, rz, dy in ((0.0, 0.0, 0.0), (0.15, 1.5, 0.02), (0.3, -1.2, 0.0), (0.45, 0.6, 0.01), (0.6, 0.0, 0.0),
                      (1.2, 0.0, 0.0), (1.8, 2.5, 0.0), (2.4, 2.2, 0.0)):
        ko.key("drum", t, (0.0, 0.0, rz), (0.0, dy, 0.0))
    for t, deg in ((0.0, 0.0), (0.2, -5.0), (0.4, 3.0), (0.6, 0.0), (1.6, 8.0), (1.8, 6.5), (2.4, 7.0)):
        key_chimney(ko, t, deg)

    # ko_broken (the stop from the broken stance): a last shudder; the jammed paddles fall back slack on the water,
    # the halves sag further apart, the stack goes over
    ko_broken = ck.Clip("ko_broken", 2.4)
    paddles(ko_broken, lambda i: ((0.0, BROKEN_LIFT[i], BROKEN_SLEW[i]), (0.15, BROKEN_LIFT[i] + 3.0, BROKEN_SLEW[i]),
                                  (0.9, 0.0, 1.2 * BROKEN_SLEW[i]), (1.05, 4.0 if BROKEN_LIFT[i] else 0.5,
                                                                     1.2 * BROKEN_SLEW[i]),
                                  (1.25, 0.0, 1.2 * BROKEN_SLEW[i]), (2.4, 0.0, 1.2 * BROKEN_SLEW[i])))
    for t, rz, dy in ((0.0, 0.0, 0.0), (0.15, 1.5, 0.02), (0.3, -1.2, 0.0), (0.45, 0.6, 0.01), (0.6, 0.0, 0.0),
                      (2.4, 0.0, 0.0)):
        ko_broken.key("drum", t, (0.0, 0.0, rz), (0.0, dy, 0.0))
    for t, deg in ((0.0, BROKEN_SPLIT), (0.5, BROKEN_SPLIT), (1.2, KO_BROKEN_SPLIT + 1.0), (1.4, KO_BROKEN_SPLIT),
                   (2.4, KO_BROKEN_SPLIT)):
        key_halves(ko_broken, t, deg)
    for t, deg in ((0.0, BROKEN_CHIMNEY), (0.2, BROKEN_CHIMNEY - 4.0), (0.5, BROKEN_CHIMNEY),
                   (1.3, KO_BROKEN_CHIMNEY + 3.0), (1.5, KO_BROKEN_CHIMNEY - 1.0), (1.7, KO_BROKEN_CHIMNEY),
                   (2.4, KO_BROKEN_CHIMNEY)):
        key_chimney(ko_broken, t, deg)
    return [idle, idle_b, intro, ready, attack, cast, hit, hit_b, ko, brk, idle_broken, hit_broken, hit_b_broken,
            ko_broken]


# ---------------------------------------------------------------------------------------------
# Report (no Blender)
# ---------------------------------------------------------------------------------------------
def report(rig: ck.Rig, meshes: list[ck.Mesh], clips: list[ck.Clip]) -> None:
    print(f"triangles: {sum(m.triangle_count for m in meshes)} "
          f"({', '.join(f'{m.name} {m.triangle_count}' for m in meshes)}); bones {len(rig.bones)}")
    for m in meshes:
        P = np.concatenate(m.pos)
        print(f"{m.name}: rest y {P[:, 1].min():.4f}..{P[:, 1].max():.3f}  x {P[:, 0].min():.2f}..{P[:, 0].max():.2f}"
              f"  z {P[:, 2].min():.2f}..{P[:, 2].max():.2f}")
    for m in meshes:
        poser = gr.Poser(rig, m)
        for c in clips:
            lows, highs = [], []
            for t in gr.frame_times(c):
                V = poser.vertices(poser.matrices(gr.pose_at(c, poser.names, t)))
                lows.append(V[:, 1].min())
                highs.append(V[:, 1].max())
            print(f"  {m.name:13s} {c.name:7s} y {min(lows):7.4f}..{max(highs):.3f}")


# Kept on the water (M3-CRE-632, common/grounding.py): a paddle lifts about its pin the least it takes to keep its
# blade on the water when the drum's jolt (the hit) or a slewing slack paddle (the KO) would press it under; the
# drum lifts the least it takes when its jolt would tip an edge of its skirt under the waterline.
GROUNDED_LIMBS = [(f"paddle{i}", tuple(float(v) for v in lift_axis(i)), 1.0, 30.0) for i in range(8)] + [
    ("drum", gr.LIFT, 1.0, 0.2)]


def export_clips(rig: ck.Rig, meshes: list[ck.Mesh]) -> list[ck.Clip]:
    return gr.grounded(rig, meshes, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and pose bounds; no export")
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh, extra = build_meshes(rig)
    if args.report or not args.out:
        report(rig, [mesh] + extra, export_clips(rig, [mesh] + extra))
        return
    info = ck.export_creature(mesh, rig, export_clips(rig, [mesh] + extra), args.out, extra_meshes=extra,
                              extras={"hymn_creature": "flat_engine"})
    print(f"flat_engine: {info}")


if __name__ == "__main__":
    main()
