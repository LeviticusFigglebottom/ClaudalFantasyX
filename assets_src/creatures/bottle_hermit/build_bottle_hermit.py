"""Bottle hermit, Ch4 the drifting trader (M3-CRE-03, final pass M3-CRB-004): docs/kb/art/creatures/act1/bottle_hermit.md.

blender --background --factory-startup --python assets_src/creatures/bottle_hermit/build_bottle_hermit.py -- \
    --out assets/creatures/bottle_hermit/bottle_hermit.glb

A giant hermit crab (about 1.2 m to its antennae) keeping house in the chimney glass of a ship's big deck lantern. The
glass lies on its side: thick old glass, salt-frosted, a chip broken out of the lip, barnacles and weed on its
outside, a green-bronze collar with rivets and a bail ring behind the lip, a brass seat at the neck. The crab's own
sea-glow light fills the glass and shows the soft abdomen curled inside it (painted into the glass's vertex colour,
since the creature shader is opaque), with one small closed spawn_wound mark on it (ADR 0151: a beast's weak point).
Out of the mouth: a hard granular shield, eye stalks with faceted caps, long antennae, two pairs of segmented walking
legs with spines, bristle tufts and dark pointed dactyls, one heavy tuberculate claw and one small one.

-x is the battle camera's side once the stage turns the model to the party, so the big claw, the lip's chip and the
wound mark are on -x.
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

SEED = 4511
PAL = {k: ck.hexrgb(v) for k, v in {
    "salt_glass": "#BFE6E0", "bronze_patina": "#5F8A78", "brass": "#B08D57", "laterite": "#A8573A",
    "tortoiseshell": "#6B3A1E", "lacquer_black": "#1D1916", "sea_glow": "#1C6B78", "spawn_wound": "#3FE0C8",
    "foam_white": "#EEF6F4", "deep_teal_shadow": "#0E4A55", "bone": "#E6DAC0", "coral_stone_weathered": "#B9AE98",
    "coral_stone": "#E8DCC4", "palm_green": "#3E7A3A", "foliage_shadow": "#1E4A3A", "saltgrass": "#B9B26A",
    "roof_clay": "#B5523A", "sand_cloth": "#C9B48E", "thatch": "#B08A52", "timber_weathered": "#7E6A55",
    "lagoon_teal": "#1FA3A6",
}.items()}

GY = 0.50  # the glass's axis height (its bulb rests on the floor)
ZOFF = -0.10  # the glass profile's axial coordinate to z
MZ = 0.45 + ZOFF  # the lip's front (z)
CAM = -1.0  # the battle camera's side (x sign): the big claw, the chip and the wound
NECK_A = -0.84  # the glass's back end (axial)

# The chimney's outer profile (radius, axial), back to front: a neck in a brass seat, the bulb, a shoulder, the lip.
OUTER = [(0.150, -0.84), (0.154, -0.76), (0.160, -0.67), (0.178, -0.58), (0.215, -0.50), (0.275, -0.43), (0.340, -0.36),
         (0.395, -0.29), (0.440, -0.21), (0.470, -0.13), (0.488, -0.05), (0.490, 0.02), (0.482, 0.09),
         (0.465, 0.16), (0.440, 0.23), (0.415, 0.29), (0.400, 0.34), (0.396, 0.38), (0.402, 0.415), (0.405, 0.435)]
LIP = [(0.398, 0.450), (0.382, 0.456), (0.366, 0.452), (0.360, 0.440)]
THICK = 0.045
INNER_AT = [0.40, 0.30, 0.16, 0.0, -0.16, -0.32, -0.46, -0.60, -0.72]
WOUND_A, WOUND_PHI = -0.08, -1.12  # the weak point on the glass (axial, angle from the bottom; -x side is negative)
# the lip's chips (angle, half-width in rad, depth in m): one big bite out of it on the camera's side, two nicks
CHIPS = ((-1.85, 0.42, 0.13), (-2.75, 0.2, 0.05), (1.9, 0.24, 0.06))


# ------------------------------------------------------------------------------------------------ helpers
def glass_point(r: float, a: float, phi: float) -> np.ndarray:
    """A point on the glass in model space: radius r about the axis at axial a, phi from the bottom (+x positive)."""
    return np.array([r * math.sin(phi), GY - r * math.cos(phi), a + ZOFF])


def outer_r(a: float) -> float:
    rs = [r for r, _ in OUTER]
    As = [x for _, x in OUTER]
    return float(np.interp(a, As, rs))


def frame(normal) -> np.ndarray:
    """A rotation whose +y is `normal`."""
    n = np.asarray(normal, dtype=np.float64)
    n = n / np.linalg.norm(n)
    t = np.cross(n, [0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0.0, 0.0])
    t /= np.linalg.norm(t)
    b = np.cross(t, n)
    return np.column_stack([t, n, b])


def sweep(path, rad, segs: int, up_hint=(0.0, 1.0, 0.0), squash: float = 1.0, cap0: bool = True,
          cap1: bool = True):
    """A tube along `path` like ck.tube, also returning each vertex's ring parameter t (0..1 along the path), its
    angle round the section (0 at the frame's normal, which `up_hint` sets), and its outward direction."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    rad = np.broadcast_to(np.asarray(rad, dtype=np.float64), (K,))
    tan, nrm, bin_ = ck.frames_along(path, up_hint)
    ang = np.arange(segs) * (2.0 * math.pi / segs)
    ca, sa = np.cos(ang), np.sin(ang)
    P, D, tt, aa = [], [], [], []
    for k in range(K):
        d = np.outer(ca, nrm[k]) + squash * np.outer(sa, bin_[k])
        P.append(path[k] + rad[k] * d)
        dn = np.outer(ca, nrm[k]) + np.outer(sa, bin_[k]) / max(squash, 1e-3)
        D.append(dn / np.linalg.norm(dn, axis=1, keepdims=True))
        tt.append(np.full(segs, k / (K - 1)))
        aa.append(ang)
    P, D, tt, aa = np.vstack(P), np.vstack(D), np.concatenate(tt), np.concatenate(aa)
    T = [ck.flip(ck.grid_tris(K, segs, True))]
    for cap, ring in ((cap0, 0), (cap1, K - 1)):
        if not cap:
            continue
        sgn = -1.0 if ring == 0 else 1.0
        tip = path[ring] + sgn * tan[ring] * rad[ring] * 0.3
        idx = len(P)
        P = np.vstack([P, tip[None]])
        D = np.vstack([D, (sgn * tan[ring])[None]])
        tt = np.append(tt, float(ring > 0))
        aa = np.append(aa, 0.0)
        r0 = ring * segs
        T.append(np.asarray([(r0 + s, idx, r0 + (s + 1) % segs) if ring == 0 else (r0 + s, r0 + (s + 1) % segs, idx)
                             for s in range(segs)], dtype=np.int64))
    return P, np.vstack(T), tt, aa, D


def cone(base, direction, length: float, radius: float, segs: int = 4):
    """A small pointed cone (a spine, a bristle): base ring and tip, open at the base (it sits in a surface)."""
    d = np.asarray(direction, dtype=np.float64)
    d /= np.linalg.norm(d)
    R = frame(d)
    a = np.arange(segs) * (2.0 * math.pi / segs)
    ring = np.column_stack([radius * np.cos(a), np.zeros(segs), radius * np.sin(a)]) @ R.T + base
    P = np.vstack([ring, (np.asarray(base) + d * length)[None]])
    T = np.asarray([(s, segs, (s + 1) % segs) for s in range(segs)], dtype=np.int64)
    t = np.r_[np.zeros(segs), 1.0]
    return P, ck.flip(T), t


def tan_at(path: np.ndarray, t: float) -> np.ndarray:
    """The unit tangent of a polyline at parameter t (0..1)."""
    i = min(int(t * (len(path) - 1)), len(path) - 2)
    d = path[i + 1] - path[i]
    return d / np.linalg.norm(d)


def chitin_color(P: np.ndarray, seed: int, pale: np.ndarray | float = 0.0, dark: np.ndarray | float = 0.0):
    """Mottled laterite and tortoiseshell, pale at the joints (`pale`), darkening to the tips (`dark`)."""
    blot = ck.fbm(P * 9.0, seed)
    speck = ck.value_noise(P * 70.0, seed + 5)
    c = ck.mix(PAL["laterite"], PAL["tortoiseshell"], ck.smoothstep(-0.05, 0.25, blot)[:, None] * 0.85)
    c = ck.mix(c, PAL["roof_clay"], ck.smoothstep(0.35, 0.8, speck)[:, None] * 0.5)
    c = ck.mix(c, PAL["bone"], np.broadcast_to(np.asarray(pale, dtype=np.float64), (len(P),))[:, None] * 0.75)
    return ck.mix(c, PAL["lacquer_black"], np.broadcast_to(np.asarray(dark, dtype=np.float64), (len(P),))[:, None])


def chitin_finish(mesh: ck.Mesh, P: np.ndarray, T: np.ndarray, col: np.ndarray, bone, seed: int, *, cavity=0.0,
                  joint=0.0, damp: float = 0.0) -> None:
    """Finishes a part of the crab's hard chitin as weathered shell, not a wet toy: a fine mottle in the colour,
    granular pitting in the cavity, a dry top and damp lower parts (the wetness rises toward the floor and on the
    faces turned down, and pools in the pits), and pale chalky salt dried into the joints (`joint`, 0..1)."""
    n = len(P)
    cav = np.broadcast_to(np.asarray(cavity, dtype=np.float64), (n,)).copy()
    jt = np.broadcast_to(np.asarray(joint, dtype=np.float64), (n,))
    mott = ck.fbm(P * 26.0, seed + 901)
    pit = ck.smoothstep(0.55, 0.85, ck.value_noise(P * 150.0, seed + 902))
    col = col * (1.0 + 0.22 * np.clip(mott * 2.5, -1.0, 1.0))[:, None]  # blotched, sun-faded and darker patches
    col = ck.mix(col, PAL["tortoiseshell"] * 0.6, (0.3 * pit)[:, None])
    cav = np.clip(cav + 0.35 * pit, 0.0, 1.0)
    N = ck.vertex_normals(P, T)
    low = ck.smoothstep(GY + 0.02, 0.04, P[:, 1])  # 0 at the shield's height, 1 at the floor
    down = ck.smoothstep(0.1, -0.7, N[:, 1])
    wet = 0.04 + 0.55 * low ** 1.5 + 0.2 * down + 0.3 * cav + damp
    # salt: chalky white crusted into the joints and the deepest pits on the dry upper parts, bone-dry
    salt = np.clip(jt * (0.55 + 0.45 * ck.smoothstep(-0.1, 0.25, mott)) + 0.5 * pit * (1.0 - low), 0.0, 1.0)
    salt = salt * ck.smoothstep(0.3, 0.65, ck.value_noise(P * 45.0, seed + 903) + 0.15 * jt)  # in broken patches
    chalk = ck.mix(PAL["coral_stone"], PAL["foam_white"], 0.35)
    col = ck.mix(col, chalk, (0.8 * salt)[:, None])
    cav = cav * (1.0 - 0.6 * salt)
    wet = wet * (1.0 - 0.9 * salt)
    ck.finish(mesh, P, T, "chitin", col, bone, wet=np.clip(wet, 0.02, 0.85), cavity=cav)


def granules(P: np.ndarray, D: np.ndarray, seed: int, freq: float, amp: float):
    """Granular relief: raised grains along the outward direction D; returns (P, cavity between the grains)."""
    g = ck.smoothstep(0.05, 0.6, ck.value_noise(P * freq, seed))
    return P + D * (g * amp)[:, None], (1.0 - g) * 0.45


# ------------------------------------------------------------------------------------------------ rig
def leg_points(s: float, i: int):
    """A walking leg's joints: hip, merus end (the knee), carpus end, propodus end, dactyl tip (on the floor)."""
    hip = np.array([s * 0.15, GY - 0.13, MZ - 0.03 - i * 0.11])
    knee = np.array([s * 0.47, GY + 0.04 - i * 0.04, MZ + 0.10 - i * 0.17])
    c1 = knee + np.array([s * 0.07, -0.08, 0.06 - i * 0.03])
    c2 = c1 + np.array([s * 0.09, -0.18, 0.08 - i * 0.05])
    tip = np.array([c2[0] + s * 0.03, 0.004, c2[2] + 0.10 - i * 0.04])
    return [hip, knee, c1, c2, tip]


def claw_points(s: float, k: float):
    """A cheliped's joints for side s and size k: shoulder, merus end, wrist, palm front, finger tip."""
    sh = np.array([s * 0.12, GY - 0.09, MZ + 0.0])
    e1 = np.array([s * (0.12 + 0.15 * k), GY - 0.10 - 0.05 * k, MZ + 0.17 * k])
    wr = np.array([s * (0.12 + 0.14 * k), GY - 0.06 - 0.06 * k, MZ + 0.27 * k])
    pf = np.array([s * (0.10 + 0.11 * k), GY - 0.09 - 0.07 * k, MZ + 0.27 * k + 0.28 * k])
    tip = np.array([s * (0.09 + 0.10 * k), GY - 0.10 - 0.07 * k, MZ + 0.27 * k + 0.46 * k])
    return [sh, e1, wr, pf, tip]


def eye_points(s: float):
    base = np.array([s * 0.045, GY + 0.04, MZ + 0.19])
    top = np.array([s * 0.10, GY + 0.36, MZ + 0.27])
    return base, top


def antenna_points(s: float):
    return [np.array([s * 0.07, GY + 0.0, MZ + 0.21]), np.array([s * 0.12, GY + 0.10, MZ + 0.31]),
            np.array([s * 0.22, GY + 0.46, MZ + 0.42]), np.array([s * 0.36, GY + 0.74, MZ + 0.16]),
            np.array([s * 0.46, GY + 0.66, MZ - 0.16])]


BIG_K, SMALL_K = 1.2, 0.5
CORE = (0.0, GY - 0.04, MZ - 0.02)  # the crab's centre of mass, at the glass mouth


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("glass", (0, GY, -0.25), (0, GY, 0.15), "root")
    rig.add("body", (0, GY - 0.05, MZ - 0.10), (0, GY - 0.03, MZ + 0.15), "glass")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        b, t = eye_points(s)
        rig.add(f"eye_{tag}", b, t, "body")
        ap = antenna_points(s)
        rig.add(f"antenna_{tag}", ap[0], ap[2], "body")
        for i in range(2):
            p = leg_points(s, i)
            rig.add(f"leg_{tag}{i}_a", p[0], p[1], "body")
            rig.add(f"leg_{tag}{i}_b", p[1], p[4], f"leg_{tag}{i}_a")
    p = claw_points(CAM, BIG_K)
    rig.add("claw_arm", p[0], p[2], "body")
    rig.add("claw", p[2], p[3], "claw_arm")
    fh = p[3] + np.array([0.0, 0.07, -0.04])
    rig.add("claw_finger", fh, p[4] + np.array([0.0, 0.02, 0.0]), "claw")
    q = claw_points(-CAM, SMALL_K)
    rig.add("claw_small_arm", q[0], q[2], "body")
    rig.add("claw_small", q[2], q[4], "claw_small_arm")
    # VFX anchors (unweighted): the weak point on the glass, the core and the phase burst at the crab's centre
    w = glass_point(outer_r(WOUND_A) + 0.01, WOUND_A, WOUND_PHI)
    rig.add("vfx_wound", w, w + np.array([CAM * 0.08, -0.02, 0.0]), "glass")
    rig.add("vfx_core", CORE, np.asarray(CORE) + np.array([0.0, 0.1, 0.0]), "body")
    rig.add("vfx_phase", CORE, np.asarray(CORE) + np.array([0.0, 0.1, 0.0]), "body")
    return rig


# ------------------------------------------------------------------------------------------------ the glass
def abdomen_mask(a: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """Where the soft abdomen, curled in the glass, shows through it (0..1): a sac from the mouth that spirals up the
    camera's side toward the neck, tapering, and its near flank low on the other side by the mouth."""
    u = np.clip((0.34 - a) / 0.86, 0.0, 1.0)  # 0 at the mouth .. 1 at the neck
    centre = CAM * (0.55 + 1.25 * u ** 1.1)
    width = 1.05 - 0.6 * u
    d = np.abs(np.angle(np.exp(1j * (phi - centre))))
    m = ck.smoothstep(width, width * 0.6, d) * ck.smoothstep(0.40, 0.28, a) * ck.smoothstep(-0.68, -0.50, a)
    d2 = np.abs(np.angle(np.exp(1j * (phi + CAM * 0.95))))
    m2 = ck.smoothstep(0.75, 0.4, d2) * ck.smoothstep(0.36, 0.22, a) * ck.smoothstep(-0.35, -0.05, a) * 0.85
    return np.maximum(m, m2)


def paint_glass(P: np.ndarray, a: np.ndarray, phi: np.ndarray, inner: np.ndarray):
    """The glass's colour, emission and wetness: a lamp glass lit from inside by the crab's sea-glow. The salt frost
    takes the light and glows softly, the worn clear windows show the dark inside, and the soft abdomen curled against
    the wall is a backlit shape in it, banded with its segment rings, the light brightest round its edge."""
    # salt frost over most of it, worn into clear windows here and there (and thickest where it lay, at the neck)
    frost = np.clip(0.68 + 1.5 * ck.fbm(P * 3.2, SEED + 3), 0.0, 1.0)
    frost = np.maximum(frost, ck.smoothstep(1.3, 0.5, np.abs(phi)) * 0.95)
    frost = np.maximum(frost, ck.smoothstep(-0.3, -0.65, a) * 0.85)
    streak = ck.smoothstep(0.45, 0.75, ck.value_noise(P * np.array([24.0, 24.0, 2.2]), SEED + 4))
    frost = np.clip(frost + 0.4 * streak, 0.0, 1.0)
    ab = abdomen_mask(a, phi)
    rings = 0.5 + 0.5 * np.cos((0.34 - a) * 2.0 * math.pi / 0.12)
    soft = ck.mix(PAL["laterite"], PAL["bone"], 0.25)
    soft = ck.mix(soft, PAL["tortoiseshell"], ck.smoothstep(0.4, 1.0, rings)[:, None] * 0.85)
    rim = ck.smoothstep(0.1, 0.4, ab) * ck.smoothstep(0.8, 0.45, ab)
    soft = ck.mix(soft, PAL["tortoiseshell"], (rim * 0.6)[:, None])
    clear = ck.mix(PAL["deep_teal_shadow"], PAL["sea_glow"], 0.15)
    salt = ck.mix(PAL["salt_glass"], PAL["coral_stone"], 0.45)
    col = ck.mix(clear, salt, (frost * 0.92)[:, None])
    col = ck.mix(col, PAL["coral_stone"], (ck.smoothstep(0.8, 1.0, frost) * streak * 0.5)[:, None])
    col = ck.mix(col, soft, (ab * (0.75 + 0.2 * (1.0 - frost)))[:, None])
    col = np.where(inner[:, None], ck.mix(PAL["deep_teal_shadow"], soft, (ab * 0.6)[:, None]), col)
    halo = ck.smoothstep(0.0, 0.25, ab) * ck.smoothstep(0.55, 0.2, ab)
    glow = (0.1 + 0.4 * frost + 0.15 * ck.smoothstep(0.2, -0.4, a)) * (1.0 - 0.9 * ck.smoothstep(0.3, 0.8, ab))
    glow = glow + 0.45 * halo
    glow = np.where(inner, 0.04 + 0.3 * ck.smoothstep(0.15, -0.35, a), glow)  # dark at the mouth, lit deep inside
    wet = 0.8 - 0.65 * frost
    return col, glow, wet, ab


def glass(mesh: ck.Mesh, rig: ck.Rig) -> None:
    segs = 44
    # the outer wall sampled finely where the abdomen shows through it (its segment rings need the rows)
    rows = [a for _, a in OUTER if a < -0.6] + list(np.linspace(-0.6, 0.40, 29)) + [0.415, 0.435]
    prof = [(outer_r(a), a, 0) for a in rows] + [(r, a, 1) for r, a in LIP]
    prof += [(outer_r(a) - THICK, a, 2) for a in INNER_AT] + [(0.0, NECK_A + 0.06, 2)]
    P, T = ck.lathe([(r, a) for r, a, _ in prof], segs)
    kind = np.repeat([k for _, _, k in prof], segs)
    ang = np.tile(np.arange(segs) * (2.0 * math.pi / segs), len(prof))
    phi = np.angle(np.exp(1j * ang))  # lathe angle == angle from the bottom once laid on its side
    a = P[:, 1].copy()
    r = np.hypot(P[:, 0], P[:, 2])
    # old glass is never true: a slow wobble in the wall, and the chip broken out of the lip
    wob = 1.0 + 0.012 * ck.fbm(np.column_stack([np.cos(ang) * 2, np.sin(ang) * 2, a * 4]), SEED + 9)
    jag = 0.5 + 0.5 * ck.value_noise(np.column_stack([ang * 9.0, a * 0.0, np.zeros_like(a)]), SEED + 11)
    bite = np.zeros_like(a)
    near = np.zeros(len(a), dtype=bool)
    for cphi, cw, cd in CHIPS:
        d = np.abs(np.angle(np.exp(1j * (phi - cphi))))
        bite = np.maximum(bite, cd * ck.smoothstep(cw, cw * 0.35, d) * (0.65 + 0.35 * jag))
        near |= d < cw
    cut = 0.456 - bite
    chipped = a > cut
    a = np.where(chipped, cut, a)
    r = r * wob
    lp = np.column_stack([r * np.sin(ang), a, r * np.cos(ang)])
    Q = ck.transform(lp, ck.rot_x(90.0), (0, GY, ZOFF))
    col, glow, wet, _ = paint_glass(Q, a, phi, kind == 2)
    fracture = chipped & (np.abs(cut - a) < 1e-9) & near
    col = ck.mix(col, PAL["salt_glass"], fracture[:, None] * 0.6)
    lipc = (kind == 1) | ((kind == 0) & (a > 0.42))
    edge = ck.mix(PAL["deep_teal_shadow"], PAL["salt_glass"], 0.55)  # thick glass looks green-dark at its edge
    col = ck.mix(col, edge, lipc[:, None] * 0.6)
    glow = np.where(lipc, 0.1, glow)  # the thick lip edge stays dark green-glass, not lit
    ck.finish(mesh, Q, ck.flip(T), "glass", col, rig.rigid("glass"), wet=wet, emission=glow,
              cavity=np.where(kind == 2, 0.6 * ck.smoothstep(-0.2, 0.3, a), 0.0))
    wound_mark(mesh, rig)


def wound_mark(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The weak point (ADR 0151, a beast's: one small closed mark): an old healed puncture on the soft abdomen, seen
    through the glass; a small patch laid on the glass, edged in the glass's own paint so it reads as under it."""
    n = 7
    u = np.linspace(-1.0, 1.0, n)
    A, F = np.meshgrid(u, u, indexing="ij")
    a = WOUND_A + A.ravel() * 0.05
    phi = WOUND_PHI + F.ravel() * 0.11
    r = np.array([outer_r(x) for x in a]) + 0.004
    P = np.column_stack([r * np.sin(phi), GY - r * np.cos(phi), a + ZOFF])
    col, _, _, _ = paint_glass(P, a, phi, np.zeros(len(P), dtype=bool))
    e = np.hypot(A.ravel() / 0.75, F.ravel() / 0.45)
    core = ck.smoothstep(1.0, 0.25, e)
    col = ck.mix(col, ck.mix(PAL["tortoiseshell"], PAL["spawn_wound"], 0.55), core[:, None])
    T = ck.flip(ck.grid_tris(n, n, False)) if CAM < 0 else ck.grid_tris(n, n, False)
    ck.finish(mesh, P, T, "chitin", col, rig.rigid("glass"), wet=1.0, emission=core ** 1.5,
              cavity=ck.smoothstep(0.9, 0.5, e) * 0.3)


def collar(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The green-bronze band behind the lip with its rivets and bail ring, and the brass seat at the neck."""
    segs = 48
    bands = (
        (0.20, 0.30, [(0.0, 0.0), (0.016, 0.006), (0.020, 0.018), (0.014, 0.03), (0.015, 0.6), (0.021, 0.72),
                        (0.022, 0.85), (0.016, 0.95), (0.0, 1.0)]),
        (-0.845, -0.70, [(0.012, 0.03), (0.022, 0.12), (0.018, 0.22), (0.016, 0.62), (0.026, 0.7),
                         (0.026, 0.82), (0.016, 0.9), (0.0, 1.0)]),
    )
    for b, (a0, a1, prof) in enumerate(bands):
        rows, rel = [], []
        if b == 1:  # the seat's domed back with its burner boss
            rows += [(0.0, a0 - 0.05), (0.035, a0 - 0.048), (0.045, a0 - 0.035), (0.09, a0 - 0.028), (0.14, a0 - 0.012)]
            rel += [0.022, 0.022, 0.01, 0.018, 0.018]
        for dr, f in prof:
            a = a0 + (a1 - a0) * f
            if dr > -0.1:
                rows.append((outer_r(a) + dr, a))
                rel.append(dr)
        P, T = ck.lathe(rows, segs)
        ang = np.tile(np.arange(segs) * (2.0 * math.pi / segs), len(rows))
        dent = 1.0 - 0.02 * ck.smoothstep(0.3, 0.7, ck.value_noise(np.column_stack(
            [np.cos(ang) * 3, np.sin(ang) * 3, P[:, 1] * 6]), SEED + 20 + b))
        P[:, 0] *= dent
        P[:, 2] *= dent
        Q = ck.transform(P, ck.rot_x(90.0), (0, GY, ZOFF))
        rel = np.repeat(rel, segs)
        raised = ck.smoothstep(0.015, 0.022, rel)
        n = ck.fbm(Q * 14.0, SEED + 1 + b)
        verd = np.clip(ck.smoothstep(-0.2, 0.25, n) * 0.85 + (1.0 - raised) * 0.35, 0.0, 1.0)
        col = ck.mix(PAL["brass"], PAL["bronze_patina"], verd[:, None])
        col = ck.mix(col, PAL["foam_white"], (ck.smoothstep(0.35, 0.6, ck.value_noise(Q * 40.0, SEED + 30))
                                              * (1.0 - raised) * 0.35)[:, None])
        ck.finish(mesh, Q, ck.flip(T), "metal", col, rig.rigid("glass"), wet=0.35, cavity=(1.0 - raised) * 0.55)
    # rivets on both bands
    for a, cnt, rr in ((0.22, 12, 0.008), (0.28, 12, 0.008), (-0.80, 8, 0.009)):
        for k in range(cnt):
            ph = 2.0 * math.pi * (k + 0.5 * (a > 0.25)) / cnt
            r = outer_r(a) + (0.017 if a > 0 else 0.022)
            c = glass_point(r, a, ph)
            nrm = c - np.array([0.0, GY, c[2]])
            Pr, Tr = ck.ellipsoid((0, 0, 0), (rr, rr * 0.55, rr), 3, 4)
            Pr = Pr @ frame(nrm).T + c
            col = ck.mix(PAL["brass"], PAL["bronze_patina"], 0.35 + 0.4 * (k % 3 == 0))
            ck.finish(mesh, Pr, Tr, "metal", col, rig.rigid("glass"), wet=0.3, cavity=0.1)
    # the bail lug on top of the front band and its ring, flopped back on the glass
    top = glass_point(outer_r(0.25) + 0.02, 0.25, math.pi)
    lug = [top + np.array([0, 0.0, -0.03]), top + np.array([0, 0.035, -0.02]), top + np.array([0, 0.035, 0.02]),
           top + np.array([0, 0.0, 0.03])]
    P, T, tt, aa, D = sweep(ck.bezier(lug, 7), 0.011, 6, up_hint=(1.0, 0.0, 0.0), squash=0.6)
    ck.finish(mesh, P, T, "metal", ck.mix(PAL["brass"], PAL["bronze_patina"], 0.6), rig.rigid("glass"), wet=0.3)
    cen = top + np.array([0.0, 0.05, -0.085])
    th = np.linspace(0.0, 2.0 * math.pi, 25)
    tilt = math.radians(62.0)
    ring = np.column_stack([0.075 * np.sin(th) * 0.95, 0.075 * np.cos(th) * math.cos(tilt) + 0.0,
                            -0.075 * np.cos(th) * math.sin(tilt)]) + cen
    ring[:, 1] += 0.004 * np.sin(th * 3.0)
    P, T, tt, aa, D = sweep(ring, 0.0095, 6, up_hint=(0.0, 1.0, 0.0), cap0=False, cap1=False)
    n = ck.fbm(P * 25.0, SEED + 40)
    col = ck.mix(PAL["brass"], PAL["bronze_patina"], ck.smoothstep(-0.3, 0.2, n)[:, None])
    ck.finish(mesh, P, T, "metal", col, rig.rigid("glass"), wet=0.3, cavity=0.15)


def growth(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Barnacles in clusters and weed on the glass's outside: low on the sides and toward the neck, where it lay
    longest in the water, never under it (it rests on the floor) and never over the weak point."""
    rng = np.random.default_rng(SEED)
    clusters = [(-0.62, 1.25), (-0.56, -1.2), (-0.30, 1.0), (-0.22, -0.45), (0.05, 1.45), (-0.55, 2.2),
                (-0.40, -2.35), (0.15, -2.3), (-0.12, 2.0), (0.14, -1.85)]
    for c, (ca, cph) in enumerate(clusters):
        for _ in range(int(rng.integers(2, 4))):
            a = ca + float(rng.normal(0.0, 0.035))
            ph = cph + float(rng.normal(0.0, 0.09))
            sz = float(rng.uniform(0.55, 1.15)) * (1.2 if a < -0.4 else 1.0)
            base = glass_point(outer_r(a) - 0.003, a, ph)
            nrm = base - np.array([0.0, GY, base[2]])
            nrm = nrm / np.linalg.norm(nrm)
            prof = [(0.036, 0.0), (0.028, 0.018), (0.019, 0.032), (0.012, 0.027), (0.0, 0.020)]
            prof = [(r * sz, y * sz) for r, y in prof]
            P, T = ck.lathe(prof, 6)
            rows = np.repeat(np.arange(len(prof)), 6)
            ang = np.tile(np.arange(6) * (2.0 * math.pi / 6), len(prof))
            plate = 1.0 + 0.2 * np.cos(ang * 3.0 + float(rng.uniform(0, 6))) * (rows > 0) * (rows < 3)
            P[:, 0] *= plate
            P[:, 2] *= plate
            P = P @ frame(nrm).T + base
            crater = rows >= 3
            n = ck.fbm(P * 40.0, SEED + 80 + c)
            col = ck.mix(PAL["coral_stone_weathered"], PAL["timber_weathered"], ck.smoothstep(-0.3, 0.4, n)[:, None] * 0.7)
            col = ck.mix(col, PAL["bone"], (rows == 2)[:, None] * 0.5)
            col = ck.mix(col, PAL["lacquer_black"], (rows == 4)[:, None] * 0.8)
            ck.finish(mesh, P, ck.flip(T), "chitin", col, rig.rigid("glass"), wet=0.25,
                      cavity=np.where(crater, 0.95, 0.3 * (rows % 2)))
    # weed: leafy ribbons rooted among the barnacles, lying slantwise down the curve of the glass, then hanging free
    # and curling at the ends, waved along their length
    for k in range(6):
        side = -CAM if k % 2 else CAM
        a = float(rng.uniform(-0.5, 0.1)) if side != CAM else float(rng.uniform(-0.68, -0.56))
        ph0 = side * float(rng.uniform(1.2, 1.8))
        drift = float(rng.choice([-1.0, 1.0])) * float(rng.uniform(0.08, 0.16))
        pts = []
        for f in (0.0, 0.25, 0.5, 0.7):
            aa_ = a + drift * f
            pts.append(glass_point(outer_r(aa_) + 0.008 + 0.012 * f, aa_, ph0 - side * f))
        out = pts[-1] - np.array([0.0, GY, pts[-1][2]])
        out /= np.linalg.norm(out)
        ln = float(rng.uniform(0.1, 0.2))
        end = pts[-1] + out * 0.09 + np.array([0.0, -ln, drift * 0.4])
        end[1] = max(end[1], 0.05)
        path = ck.bezier(pts + [end], 14)
        t = np.linspace(0.0, 1.0, 14)
        path[:, 2] += 0.018 * np.sin(t * 3.0 * math.pi + k) * t
        path[:, 1] = np.maximum(path[:, 1], 0.045)
        w = (0.003 + 0.0055 * np.sin(np.clip(t * 1.2, 0.0, 1.0) * math.pi) ** 0.7) * float(rng.uniform(0.85, 1.25))
        P, T, tt, aa, D = sweep(path, w, 4, up_hint=tuple(out), squash=4.0)
        col = ck.mix(PAL["palm_green"], PAL["foliage_shadow"], ck.smoothstep(0.1, 0.9, tt)[:, None] * 0.75)
        col = ck.mix(col, PAL["saltgrass"], (ck.smoothstep(0.3, 0.7, ck.value_noise(P * 30.0, SEED + 60 + k)) * 0.45)[:, None])
        ck.finish(mesh, P, T, "chitin", col, rig.rigid("glass"), wet=0.9, cavity=0.25)


# ------------------------------------------------------------------------------------------------ the crab
def shield(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The hard front of the cephalothorax: a flattened granular shield with a groove and ridges, a pointed
    rostrum between the eyes, and behind it the soft pale body going into the glass."""
    z = np.linspace(MZ - 0.14, MZ + 0.215, 15)
    u = (z - z[0]) / (z[-1] - z[0])
    path = np.column_stack([np.zeros_like(z), GY - 0.04 + 0.03 * np.sin(u * math.pi), z])
    rad = 0.165 * np.sin(np.clip(u, 0.04, 0.97) * math.pi) ** 0.45 * (1.0 - 0.25 * u ** 3)
    P, T, tt, aa, D = sweep(path, rad, 24, up_hint=(0.0, 1.0, 0.0), squash=1.0)
    up = np.cos(aa)  # 1 on top
    # flatten: a broad, low shield on top, a flatter underside
    lp = P - path[np.minimum((tt * 14).round().astype(int), 14)]
    lp[:, 1] *= np.where(lp[:, 1] > 0, 0.52, 0.42)
    P = path[np.minimum((tt * 14).round().astype(int), 14)] + lp
    hard = ck.smoothstep(0.42, 0.55, tt) * ck.smoothstep(-0.55, 0.0, up)
    groove = np.exp(-((tt - 0.6 - 0.05 * np.abs(np.sin(aa))) / 0.025) ** 2) * hard
    ridge = np.exp(-((np.abs(np.sin(aa)) - 0.55) / 0.08) ** 2) * hard * ck.smoothstep(0.62, 0.75, tt)
    P = P - D * (groove * 0.012)[:, None] + D * (ridge * 0.008)[:, None]
    P, cav = granules(P, D, SEED + 70, 110.0, 0.005 * hard)
    rost = ck.smoothstep(0.93, 1.0, tt) * ck.smoothstep(0.0, 0.8, up)
    P = P + np.array([0.0, 0.01, 0.035]) * rost[:, None]
    col = chitin_color(P, SEED + 71, pale=(1.0 - hard) * 0.8)
    col = ck.mix(col, PAL["tortoiseshell"], (ridge * 0.6 + groove * 0.4)[:, None])
    chitin_finish(mesh, P, T, col, rig.rigid("body"), SEED + 75, cavity=np.clip(cav * hard + groove * 0.9, 0.0, 1.0),
                  joint=groove * 0.7, damp=0.45 * (1.0 - hard))
    # the soft body behind the shield, into the glass, and its pale underside
    Pa, Ta = ck.ellipsoid((0.0, GY - 0.06, MZ - 0.16), (0.24, 0.21, 0.2), 9, 16)
    n = ck.fbm(Pa * 12.0, SEED + 72)
    col = ck.mix(ck.mix(PAL["bone"], PAL["laterite"], 0.4), PAL["tortoiseshell"], ck.smoothstep(0.1, 0.5, n)[:, None] * 0.4)
    ck.finish(mesh, Pa, Ta, "chitin", col, rig.rigid("body"), wet=0.9, cavity=0.35)
    # mouthparts: two bristled third maxillipeds folded under the rostrum
    for s in (1.0, -1.0):
        pts = [np.array([s * 0.03, GY - 0.09, MZ + 0.14]), np.array([s * 0.05, GY - 0.16, MZ + 0.21]),
               np.array([s * 0.035, GY - 0.12, MZ + 0.27])]
        P, T, tt, aa, D = sweep(ck.bezier(pts, 6), np.linspace(0.016, 0.008, 6), 6, squash=0.6)
        ck.finish(mesh, P, T, "chitin", chitin_color(P, SEED + 73, pale=0.5), rig.rigid("body"), wet=0.5, cavity=0.2)
        tuft(mesh, rig.rigid("body"), ck.bezier(pts, 6)[3:], np.array([0.0, -1.0, 0.3]), 0.035, 5, SEED + 74)


def tuft(mesh: ck.Mesh, bone: int, along: np.ndarray, out, length: float, n: int, seed: int) -> None:
    """A tuft of bristles (setae) along a few points: thin dark-gold cones fanning out."""
    rng = np.random.default_rng(seed)
    out = np.asarray(out, dtype=np.float64)
    for p in along:
        for _ in range(n):
            d = out / np.linalg.norm(out) + rng.normal(0.0, 0.35, 3)
            P, T, t = cone(p, d, length * float(rng.uniform(0.6, 1.1)), 0.0035, 3)
            col = ck.mix(PAL["thatch"], PAL["timber_weathered"], t[:, None] * 0.7)
            ck.finish(mesh, P, T, "chitin", col, bone, wet=0.2, cavity=0.1)


def segment(mesh: ck.Mesh, bone, p0, p1, r0: float, r1: float, seed: int, *, bend=(0.0, 0.0, 0.0), squash=0.7,
            up_hint=(0.0, 1.0, 0.0), segs: int = 8, rings: int = 7, cuff: bool = True, dark: float = 0.0,
            spines: int = 0, grain: float = 0.004):
    """One flattened, granular leg segment from joint p0 to joint p1: pinched at the joint it comes out of, a hard
    flared cuff at its far end, a dorsal keel, pale at the joints. Returns the dorsal direction at its far end."""
    p0, p1 = np.asarray(p0, dtype=np.float64), np.asarray(p1, dtype=np.float64)
    mid = (p0 + p1) / 2 + np.asarray(bend)
    path = ck.bezier([p0, mid, p1], rings)
    t = np.linspace(0.0, 1.0, rings)
    rad = (r0 + (r1 - r0) * t) * (0.72 + 0.28 * ck.smoothstep(0.0, 0.25, t) + 0.08 * np.sin(t * math.pi))
    if cuff:
        rad = rad * (1.0 + 0.12 * np.exp(-((t - 0.88) / 0.07) ** 2)) * np.where(t > 0.97, 0.8, 1.0)
    P, T, tt, aa, D = sweep(path, rad, segs, up_hint=up_hint, squash=squash)
    keel = np.exp(-((np.angle(np.exp(1j * aa))) / 0.35) ** 2)
    P = P + D * (keel * rad[np.minimum((tt * (rings - 1)).round().astype(int), rings - 1)] * 0.18)[:, None]
    P, cav = granules(P, D, seed, 140.0, grain)
    pale = ck.smoothstep(0.18, 0.0, tt) + ck.smoothstep(0.93, 1.0, tt) * 0.4
    band = np.exp(-((tt - 0.72) / 0.08) ** 2) * 0.55
    col = chitin_color(P, seed + 1, pale=np.clip(pale, 0.0, 1.0), dark=band * 0.4 + dark * tt ** 2)
    ventral = ck.smoothstep(0.0, -0.8, np.cos(aa))
    col = ck.mix(col, PAL["bone"], (ventral * 0.35)[:, None])
    chitin_finish(mesh, P, T, col, bone, seed, cavity=np.clip(cav + pale * 0.3, 0.0, 1.0), joint=np.clip(pale, 0.0, 1.0))
    tan, nrm, _ = ck.frames_along(path, up_hint)
    if spines:
        rng = np.random.default_rng(seed + 2)
        for k in range(spines):
            f = 0.25 + 0.6 * k / max(spines - 1, 1)
            i = int(round(f * (rings - 1)))
            base = path[i] + nrm[i] * rad[i] * 1.05
            d = nrm[i] * 0.8 + tan[i] * 0.9 + rng.normal(0.0, 0.1, 3)
            Ps, Ts, ts = cone(base, d, rad[i] * 0.9, rad[i] * 0.22, 4)
            col = ck.mix(PAL["laterite"], PAL["lacquer_black"], ts[:, None] * 0.85)
            chitin_finish(mesh, Ps, Ts, col, bone, seed + 3 + k, cavity=0.1)
    return path, rad, tan, nrm


def walking_leg(mesh: ck.Mesh, rig: ck.Rig, s: float, tag: str, i: int) -> None:
    hip, knee, c1, c2, tip = leg_points(s, i)
    ba, bb = rig.rigid(f"leg_{tag}{i}_a"), rig.rigid(f"leg_{tag}{i}_b")
    sd = SEED + 100 + 20 * i + (10 if s < 0 else 0)
    k0 = 0.042 - 0.004 * i
    up = (0.0, 1.0, 0.0)
    segment(mesh, ba, hip, knee, k0 * 0.9, k0, sd, bend=(0.0, 0.05, 0.0), squash=0.62, up_hint=up, rings=8,
            spines=3)
    segment(mesh, bb, knee, c1, k0 * 0.85, k0 * 0.8, sd + 3, bend=(0.0, 0.01, 0.0), squash=0.7, up_hint=up, rings=5,
            spines=1)
    path, rad, tan, nrm = segment(mesh, bb, c1, c2, k0 * 0.75, k0 * 0.62, sd + 5, bend=(s * 0.02, 0.0, 0.0),
                                  squash=0.62, up_hint=(s, 0.3, 0.0), rings=7, spines=2)
    tuft(mesh, bb, path[2:6:2] + nrm[2:6:2] * 0.02, -nrm[3] + np.array([0, -0.5, 0]), 0.045, 4, sd + 7)
    # the dactyl: long, curved, pointed, dark at the tip, a stiff fringe along it
    ctl = [c2, c2 + (tip - c2) * 0.45 + np.array([s * 0.035, 0.02, 0.0]), tip]
    path = ck.bezier(ctl, 8)
    t = np.linspace(0.0, 1.0, 8)
    rad = k0 * 0.55 * (1.0 - t) ** 0.8 + 0.0015
    P, T, tt, aa, D = sweep(path, rad, 7, up_hint=(s, 0.3, 0.0), squash=0.7)
    P, cav = granules(P, D, sd + 8, 160.0, 0.002)
    col = chitin_color(P, sd + 9, pale=ck.smoothstep(0.15, 0.0, tt), dark=ck.smoothstep(0.45, 0.95, tt))
    chitin_finish(mesh, P, T, col, bb, sd + 9, cavity=cav, joint=ck.smoothstep(0.15, 0.0, tt))
    tuft(mesh, bb, path[1:4], np.array([s * 0.6, 0.6, 0.4]), 0.04, 3, sd + 10)


def cheliped(mesh: ck.Mesh, rig: ck.Rig, s: float, k: float, big: bool) -> None:
    sh, e1, wr, pf, tip = claw_points(s, k)
    arm = rig.rigid("claw_arm" if big else "claw_small_arm")
    hand = rig.rigid("claw" if big else "claw_small")
    finger = rig.rigid("claw_finger") if big else hand
    sd = SEED + (300 if big else 400)
    r = 0.05 * k + 0.012
    segment(mesh, arm, sh, e1, r * 0.85, r, sd, bend=(0.0, 0.03 * k, 0.0), squash=0.7, rings=8, spines=0,
            grain=0.006 * k)
    path, rad, tan, nrm = segment(mesh, arm, e1, wr, r * 0.95, r * 1.1, sd + 3, bend=(s * 0.02 * k, 0.02, 0.0),
                                  squash=0.8, rings=7, spines=3 if big else 1, grain=0.007 * k)
    # the palm: heavy, flattened sideways, lumpy with tubercles, a pale-tipped crest on top
    L = np.linalg.norm(pf - wr)
    path = ck.bezier([wr, (wr + pf) / 2 + np.array([s * 0.02 * k, 0.02 * k, 0.0]), pf], 12)
    t = np.linspace(0.0, 1.0, 12)
    rad = (0.105 * k + 0.008) * (0.55 + 0.45 * np.sin(np.clip(t * 1.15, 0.0, 1.0) * math.pi * 0.62) ** 0.7)
    rad[-1] *= 0.75
    P, T, tt, aa, D = sweep(path, rad, 18 if big else 10, up_hint=(0.0, 1.0, 0.0), squash=0.62)
    up = np.cos(aa)
    outer = np.sin(aa) * (-s)  # 1 on the outer face
    lump = ck.fbm(P * (11.0 / k), sd + 5)
    P = P + D * (lump * 0.03 * k)[:, None]
    face = ck.smoothstep(-0.6, 0.2, outer + up * 0.5)
    tub = ck.smoothstep(0.15, 0.7, ck.value_noise(P * (60.0 / k), sd + 6)) * face
    P = P + D * (tub * 0.016 * k)[:, None]
    crest = np.exp(-(np.angle(np.exp(1j * aa)) / 0.3) ** 2)
    P = P + D * (crest * 0.014 * k)[:, None]
    col = chitin_color(P, sd + 7, pale=tub * 0.5 + crest * 0.25, dark=ck.smoothstep(0.85, 1.0, tt) * 0.3)
    col = ck.mix(col, PAL["tortoiseshell"], (ck.smoothstep(0.1, -0.3, lump) * 0.5)[:, None])
    col = ck.mix(col, PAL["bone"], (ck.smoothstep(0.0, -0.9, up) * 0.4)[:, None])
    chitin_finish(mesh, P, T, col, hand, sd + 7, cavity=np.clip((1.0 - tub) * 0.45 + 0.1, 0.0, 1.0),
                  joint=ck.smoothstep(0.12, 0.0, tt))
    if big:
        tuft(mesh, hand, path[3:10:3] + np.array([0.0, -rad[6] * 0.55, 0.0]), np.array([s * 0.3, -1.0, 0.2]),
             0.05, 4, sd + 8)
        # conical tubercles on the outer face and the crest, pale-tipped
        cand = np.where((tub > 0.55) & (tt > 0.12) & (tt < 0.9))[0]
        rng = np.random.default_rng(sd + 9)
        for v in rng.choice(cand, size=min(16, len(cand)), replace=False):
            Pc, Tc, tc = cone(P[v] - D[v] * 0.004, D[v] + tan_at(path, tt[v]) * 0.4, 0.022 * k, 0.009 * k, 4)
            chitin_finish(mesh, Pc, Tc, ck.mix(PAL["tortoiseshell"], PAL["bone"], tc[:, None] * 0.8), hand, sd + 9,
                          cavity=(1.0 - tc) * 0.4)
    # fixed finger (pollex) from the palm's lower front; movable finger (dactyl) hinged above it
    for kind in ("pollex", "dactyl"):
        if kind == "pollex":
            base = pf + np.array([0.0, -0.035 * k, -0.02 * k])
            ctl = [base, base + (tip - pf) * 0.5 + np.array([0.0, -0.01 * k, 0.0]), tip + np.array([0.0, 0.01 * k, 0.0])]
            bone, sgn = hand, 1.0
        else:
            base = pf + np.array([0.0, 0.045 * k, -0.03 * k])
            ctl = [base, base + (tip - pf) * 0.55 + np.array([0.0, 0.05 * k, 0.0]), tip + np.array([0.0, 0.025 * k, 0.01])]
            bone, sgn = finger, -1.0
        path = ck.bezier(ctl, 9)
        t = np.linspace(0.0, 1.0, 9)
        rad = (0.042 * k + 0.004) * (1.0 - 0.85 * t ** 1.3) + 0.002
        P, T, tt, aa, D = sweep(path, rad, 9 if big else 7, up_hint=(0.0, 1.0, 0.0), squash=0.65)
        # teeth on the cutting edge (facing the other finger), tubercles elsewhere
        edge = np.exp(-((np.angle(np.exp(1j * (aa - (0.0 if sgn > 0 else math.pi))))) / 0.5) ** 2)
        teeth = (0.5 + 0.5 * np.cos(tt * 9.0 * 2.0 * math.pi)) * edge * ck.smoothstep(0.85, 0.3, tt)
        P = P + D * (teeth * 0.012 * k)[:, None]
        P, cav = granules(P, D, sd + 10 + (kind == "dactyl"), 120.0 / k, 0.005 * k)
        col = chitin_color(P, sd + 12, pale=teeth * 0.6, dark=ck.smoothstep(0.35, 0.85, tt))
        chitin_finish(mesh, P, T, col, bone, sd + 12, cavity=cav, joint=ck.smoothstep(0.12, 0.0, tt))


def eyes_and_antennae(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        bone = rig.rigid(f"eye_{tag}")
        base, top = eye_points(s)
        mid = (base + top) / 2 + np.array([s * 0.02, 0.0, -0.02])
        path = ck.bezier([base, mid, top], 9)
        t = np.linspace(0.0, 1.0, 9)
        rad = 0.026 - 0.008 * t + 0.004 * np.exp(-((t - 0.25) / 0.05) ** 2)
        P, T, tt, aa, D = sweep(path, rad, 8, up_hint=(0.0, 0.0, 1.0), squash=0.85)
        band = 0.5 + 0.5 * np.cos(tt * 5.0 * 2.0 * math.pi)
        col = chitin_color(P, SEED + 500 + int(s > 0), pale=0.35 + 0.3 * band, dark=0.0)
        chitin_finish(mesh, P, T, col, bone, SEED + 505 + int(s > 0), cavity=0.15 * band)
        # the compound eye: a faceted cap on a pale ring
        tan = top - path[-2]
        tan = tan / np.linalg.norm(tan)
        Pe, Te = ck.ellipsoid((0, 0, 0), (0.038, 0.05, 0.038), 6, 10)
        Pe = Pe @ frame(tan).T + top + tan * 0.03
        sp = ck.smoothstep(0.3, 0.8, ck.value_noise(Pe * 160.0, SEED + 510))
        col = ck.mix(PAL["lacquer_black"], PAL["deep_teal_shadow"], sp[:, None] * 0.6)
        low = ((Pe - top) @ tan) < 0.0
        col = np.where(low[:, None], ck.mix(PAL["bone"], PAL["laterite"], 0.4), col)
        ck.finish(mesh, Pe, Te, "eye", col, bone, wet=np.where(low, 0.3, 1.0), flat=True)
        tuft(mesh, bone, path[1:3], np.array([s, 0.2, 0.6]), 0.03, 3, SEED + 520 + int(s > 0))
        # antenna: a jointed peduncle, then a long whip
        ab = rig.rigid(f"antenna_{tag}")
        ap = antenna_points(s)
        segment(mesh, ab, ap[0], ap[1], 0.016, 0.013, SEED + 530 + int(s > 0), squash=0.85, segs=6, rings=5,
                up_hint=(0.0, 0.0, 1.0), grain=0.0)
        path = ck.bezier(ap[1:], 20)
        t = np.linspace(0.0, 1.0, 20)
        P, T, tt, aa, D = sweep(path, 0.010 * (1.0 - 0.75 * t) + 0.002, 4, up_hint=(0.0, 0.0, 1.0))
        ring = 0.5 + 0.5 * np.cos(tt * 40.0 * math.pi)
        col = ck.mix(PAL["roof_clay"], PAL["bone"], (ring * 0.35)[:, None])
        col = ck.mix(col, PAL["tortoiseshell"], ck.smoothstep(0.5, 1.0, tt)[:, None] * 0.5)
        ck.finish(mesh, P, T, "chitin", col, ab, wet=0.4)


def crab(mesh: ck.Mesh, rig: ck.Rig) -> None:
    shield(mesh, rig)
    eyes_and_antennae(mesh, rig)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(2):
            walking_leg(mesh, rig, s, tag, i)
    cheliped(mesh, rig, CAM, BIG_K, True)
    cheliped(mesh, rig, -CAM, SMALL_K, False)


# ------------------------------------------------------------------------------------------------ clips
KO_CURL = 50.0  # the KO's shin curl (degrees, the left side's sign): the tips draw up and in


def build_idle() -> ck.Clip:
    idle = ck.Clip("idle", 3.0, loop=True)
    idle.wave("body", amp_rot=(2.0, 2.5, 0.0), amp_loc=(0.0, 0.008, 0.012), cycles=1)
    idle.wave("eye_l", amp_rot=(4.0, 14.0, 0.0), cycles=1)
    idle.wave("eye_r", amp_rot=(-4.0, 12.0, 0.0), cycles=1, phase=1.6)
    idle.wave("antenna_l", amp_rot=(8.0, 6.0, 0.0), cycles=2)
    idle.wave("antenna_r", amp_rot=(-6.0, 7.0, 0.0), cycles=2, phase=1.0)
    idle.wave("claw_finger", amp_rot=(-8.0, 0, 0), base_rot=(-8.0, 0, 0), cycles=2)
    idle.wave("claw_arm", amp_rot=(-3.0, 2.0, 0.0), cycles=1, phase=0.7)
    idle.wave("claw_small_arm", amp_rot=(-6.0, 0.0, 0.0), cycles=3, phase=0.3)
    idle.wave("glass", amp_rot=(0.0, 0.0, 1.0), cycles=1)
    for tag, sg in (("l", 1.0), ("r", -1.0)):
        for i in range(2):
            idle.wave(f"leg_{tag}{i}_b", amp_rot=(0.0, 0.0, 2.0 * sg), cycles=1, phase=0.8 * i + (1.5 if sg < 0 else 0))
    return idle


def pose_at0(clip: ck.Clip, bone: str):
    r, l = clip.sample(bone, 0.0)
    return tuple(float(v) for v in r), tuple(float(v) for v in l)


def build_clips() -> list[ck.Clip]:
    idle = build_idle()
    bones = ["root", "glass", "body", "eye_l", "eye_r", "antenna_l", "antenna_r", "claw_arm", "claw", "claw_finger",
             "claw_small_arm", "claw_small"] + [f"leg_{t}{i}_{p}" for t in "lr" for i in range(2) for p in "ab"]
    rest = {b: pose_at0(idle, b) for b in bones}

    # ready: the alert stance, a loop: up on its legs, the big claw cocked, eyes up and antennae forward
    ready = ck.Clip("ready", 1.6, loop=True)
    ready.wave("body", amp_rot=(1.0, 2.0, 0.0), amp_loc=(0.0, 0.006, 0.0), base_rot=(-5.0, 0.0, 0.0),
               base_loc=(0.0, 0.03, 0.05), cycles=1)
    ready.wave("claw_arm", amp_rot=(-3.0, 0.0, 0.0), base_rot=(-22.0, 0.0, 0.0), cycles=1, phase=0.5)
    ready.wave("claw_finger", amp_rot=(-6.0, 0.0, 0.0), base_rot=(-16.0, 0.0, 0.0), cycles=2)
    ready.wave("claw_small_arm", amp_rot=(-4.0, 0.0, 0.0), base_rot=(-12.0, 0.0, 0.0), cycles=2)
    ready.wave("eye_l", amp_rot=(0.0, 8.0, 0.0), base_rot=(-8.0, 0.0, 0.0), cycles=1)
    ready.wave("eye_r", amp_rot=(0.0, -8.0, 0.0), base_rot=(-8.0, 0.0, 0.0), cycles=1)
    ready.wave("antenna_l", amp_rot=(6.0, 0.0, 0.0), base_rot=(20.0, -10.0, 0.0), cycles=2)
    ready.wave("antenna_r", amp_rot=(6.0, 0.0, 0.0), base_rot=(20.0, 10.0, 0.0), cycles=2, phase=1.2)
    ready.wave("glass", amp_rot=(0.0, 0.0, 0.8), base_rot=(-2.0, 0.0, 0.0), cycles=1)

    # intro (2.6 s): shut in the glass, it hauls itself up out of the mouth, rears and raises the big claw while the
    # glass flares (rocks up on its bulb), then settles into the idle
    intro = ck.Clip("intro", 2.6)
    hidden = {"body": ((8.0, 0.0, 0.0), (0.0, -0.03, -0.2)), "claw_arm": ((30.0, 0.0, 0.0), (0, 0, 0)),
              "claw_small_arm": ((30.0, 0.0, 0.0), (0, 0, 0)), "eye_l": ((55.0, 0.0, 0.0), (0, 0, 0)),
              "eye_r": ((55.0, 0.0, 0.0), (0, 0, 0)), "antenna_l": ((50.0, 20.0, 0.0), (0, 0, 0)),
              "antenna_r": ((50.0, -20.0, 0.0), (0, 0, 0)), "claw_finger": ((0.0, 0.0, 0.0), (0, 0, 0)),
              "glass": ((0.0, 0.0, 0.0), (0, 0, 0))}
    for tag, sg in (("l", 1.0), ("r", -1.0)):
        for i in range(2):
            hidden[f"leg_{tag}{i}_a"] = ((0.0, 0.0, 10.0 * sg), (0, 0, 0))
            hidden[f"leg_{tag}{i}_b"] = ((0.0, 0.0, 40.0 * sg), (0, 0, 0))
    reared = {"body": ((-14.0, 0.0, 0.0), (0.0, 0.07, 0.08)), "claw_arm": ((-75.0, -10.0 * CAM, 0.0), (0, 0, 0)),
              "claw_finger": ((-38.0, 0.0, 0.0), (0, 0, 0)), "claw_small_arm": ((-30.0, 0.0, 0.0), (0, 0, 0)),
              "eye_l": ((-14.0, 10.0, 0.0), (0, 0, 0)), "eye_r": ((-14.0, -10.0, 0.0), (0, 0, 0)),
              "antenna_l": ((25.0, -20.0, 0.0), (0, 0, 0)), "antenna_r": ((25.0, 20.0, 0.0), (0, 0, 0)),
              "glass": ((-7.0, 0.0, 0.0), (0.0, 0.03, 0.0))}
    for tag, sg in (("l", 1.0), ("r", -1.0)):
        for i in range(2):
            reared[f"leg_{tag}{i}_a"] = ((0.0, 0.0, 6.0 * sg), (0, 0, 0))
            reared[f"leg_{tag}{i}_b"] = ((0.0, 0.0, -8.0 * sg), (0, 0, 0))
    for b in bones:
        z = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        h, rr, st = hidden.get(b, z), reared.get(b, z), rest[b]
        intro.key(b, 0.0, *h)
        intro.key(b, 0.35, *h)
        mid = tuple((np.asarray(h[0]) + np.asarray(rr[0])) * 0.5), tuple((np.asarray(h[1]) + np.asarray(rr[1])) * 0.5)
        intro.key(b, 0.8, *mid)
        intro.key(b, 1.25, *rr)
        intro.key(b, 1.7, *rr)
        intro.key(b, 2.6, *st)
    intro.key("claw_finger", 1.45, (-10.0, 0.0, 0.0))  # it snaps the claw at the top of the rear
    intro.keys["claw_finger"].sort(key=lambda k: k[0])

    attack = ck.Clip("attack", 1.0)
    for t, arm, fin, fwd, bd in ((0.0, 0, 0, 0, 0), (0.3, -40, -40, -0.03, -6), (0.45, 18, 6, 0.14, 6),
                                  (0.65, 10, 0, 0.09, 3), (1.0, 0, 0, 0, 0)):
        attack.key("claw_arm", t, (arm, 0, 0))
        attack.key("claw_finger", t, (fin, 0, 0))
        attack.key("root", t, (0, 0, 0), (0, 0, fwd))
        attack.key("body", t, (bd, 0, 0), (0, 0, fwd * 0.4))
    cast = ck.Clip("cast", 1.3)  # it pulls into the glass, which flares
    for t, s in ((0.0, 0.0), (0.35, 1.0), (0.95, 1.0), (1.3, 0.0)):
        cast.key("body", t, (6.0 * s, 0, 0), (0, 0, -0.12 * s))
        cast.key("glass", t, (-6.0 * s, 0, 0), (0, 0.03 * s, 0))
        cast.key("claw_arm", t, (20.0 * s, 0, 0))
        cast.key("eye_l", t, (40.0 * s, 0, 0))
        cast.key("eye_r", t, (40.0 * s, 0, 0))
    hit = ck.Clip("hit", 0.45)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.45, 0.0)):
        hit.key("body", t, (5.0 * s, 0, 0), (0, 0, -0.09 * s))
        hit.key("glass", t, (0, 0, 4.0 * s))
        hit.key("claw_arm", t, (14.0 * s, 0, 0))
        hit.key("eye_l", t, (30.0 * s, 0, 0))
        hit.key("eye_r", t, (30.0 * s, 0, 0))
    ko = ck.Clip("ko", 1.6)  # it slumps half out of the mouth, legs curled, the claw on the floor
    for t, s in ((0.0, 0.0), (0.7, 0.7), (1.6, 1.0)):
        ko.key("body", t, (18.0 * s, 0, 0), (0, -0.06 * s, 0.06 * s))
        ko.key("glass", t, (0, 0, -18.0 * s), (0, -0.02 * s, 0))
        for tag, sg in (("l", 1.0), ("r", -1.0)):
            for i in range(2):
                ko.key(f"leg_{tag}{i}_b", t, (0, 0, KO_CURL * s * sg))
            ko.key(f"eye_{tag}", t, (60.0 * s, 0, 0))
            ko.key(f"antenna_{tag}", t, (45.0 * s, 0, 0))
        ko.key("claw_arm", t, (25.0 * s, 0, 0))
        ko.key("claw_finger", t, (-12.0 * s, 0, 0))
    return [idle, ready, intro, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): a planted leg turns up at its hip, and each claw up at its
# shoulder, the least it takes when the body's bob, recoil or slump would press it through the floor; in the KO and
# the intro the whole model lifts the least it takes to stay on the floor.
GROUNDED_LIMBS = ([(f"leg_{tag}{i}_a", 2, 1.0 if tag == "l" else -1.0, 60.0) for tag in "lr" for i in range(2)]
                  + [("claw_arm", 0, -1.0, 45.0), ("claw_small_arm", 0, -1.0, 45.0),
                     ("root", gr.LIFT, 1.0, 0.15, ("ko", "intro", "cast"))])


# The planted feet held where they touch down (common/grounding.py pinned(); the Act I audit's foot sliding).
PINNED_LEGS = [(f"leg_{tag}{i}_a", f"leg_{tag}{i}_b", 2, 1.0 if tag == "l" else -1.0) for tag in "lr" for i in range(2)]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    pinned = gr.pinned(rig, mesh, gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS), PINNED_LEGS)
    return gr.reground(rig, mesh, pinned, GROUNDED_LIMBS)  # a held foot's toes back above the floor


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("bottle_hermit")
    glass(mesh, rig)
    collar(mesh, rig)
    growth(mesh, rig)
    crab(mesh, rig)
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "bottle_hermit"})
    print(f"bottle_hermit: {info}")


if __name__ == "__main__":
    main()
