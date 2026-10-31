"""Wick crawler, Ch19 the Iskarra Lamp Spire (M5-A3P-1800): docs/kb/art/creatures/act3/wick_crawler.md.

blender --background --factory-startup --python assets_src/creatures/wick_crawler/build_wick_crawler.py -- \
    --out assets/creatures/wick_crawler/wick_crawler.glb
python3 assets_src/creatures/wick_crawler/build_wick_crawler.py --report   # numpy checks, no Blender

A Lit Age lamp-tending machine still on its rounds: a lamplighter's pole that walks. A segmented brass body 1.5 m long
(seven segments tapering from 0.16 m across at the head to 0.1 m at the tail, each ringed with a rolled rim) carried
0.34 m up on fourteen fine lacquer-black legs ending in rope hooks. At its head a pair of wick-shears and a snuffer cone
on a short arm. From its last segment a thin brass pole rises, leaning forward over its back, with its own taper at
the tip, 1.4 m up: a small bound light (glimmer_bound, steady: a construct never flickers like a flame) in a salt-glass
thimble. At the pole's foot the oil reservoir that feeds it, its filler cap ringed by a hairline spawn_wound seam: the
weak point (ADR 0151), closed, a construct's. Brass goes bronze_patina in its joints and underside. Kept apart from
the conduit crawler (Ch11's round glass dome on six legs): long, low and segmented, its light held high on a pole.
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

SEED = 1800
PAL = {k: ck.hexrgb(v) for k, v in {
    "brass": "#B08D57", "bronze_patina": "#5F8A78", "lacquer_black": "#1D1916", "salt_glass": "#BFE6E0",
    "glimmer_bound": "#4FB3B0", "spawn_wound": "#3FE0C8",
}.items()}

NSEG = 7
LENGTH = 1.5
BODY_Y = 0.34  # the segments' axis over the floor
RADIUS = (0.08, 0.05)  # the head segment's and the tail segment's radius (0.16 m to 0.10 m across)
RIM = 0.012  # each segment's rolled rim stands this proud of it
HIP_DROP = 0.02
KNEE = (0.15, 0.08)  # the knee: out past the hip and up over it
FOOT = (0.24, 0.012, 0.02)  # the foot: out past the hip, its hook's height, a little forward
POLE = [(0.74, -0.62), (1.06, -0.47), (1.3, -0.32), (1.38, -0.27)]  # (y over the floor, z) after the pole's foot
THIMBLE = (0.03, 0.07)  # the taper's glass thimble: radius and height
RESERVOIR = (0.042, 0.06)  # radius and height, at the pole's foot
SHEAR_LEN = 0.22

PARTS: dict[str, tuple[int, int]] = {}


def seg_z(i: int) -> float:
    return LENGTH / 2 - (i + 0.5) * LENGTH / NSEG


def seg_r(i: int) -> float:
    return RADIUS[0] + (RADIUS[1] - RADIUS[0]) * i / (NSEG - 1)


def tail_top() -> np.ndarray:
    return np.array([0.0, BODY_Y + seg_r(NSEG - 1), seg_z(NSEG - 1)])


def leg_pts(side: float, i: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z, r = seg_z(i), seg_r(i)
    hip = np.array([side * r * 0.9, BODY_Y - HIP_DROP, z])
    knee = np.array([side * (r + KNEE[0]), BODY_Y + KNEE[1], z])
    foot = np.array([side * (r + FOOT[0]), FOOT[1], z + FOOT[2]])
    return hip, knee, foot


def pole_pts() -> list[np.ndarray]:
    """The pole's foot (in the reservoir's lid on the tail) and its points up to the taper's tip, 1.4 m up."""
    top = tail_top()
    return [np.array([0.0, top[1] + RESERVOIR[1], top[2]])] + [np.array([0.0, y, z]) for y, z in POLE]


def mark(name: str, mesh: ck.Mesh, start: int) -> None:
    lo, _hi = PARTS.get(name, (start, start))
    PARTS[name] = (min(lo, start), mesh.count)


# ---------------------------------------------------------------------------------------------
# Rig: root, a spine of seven from the tail to the head (so rearing the head moves only the front), the head with its
# shears and snuffer, fourteen legs of two, a pole of three and the taper.
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    step = LENGTH / NSEG
    parent = "root"
    for i in reversed(range(NSEG)):
        z = seg_z(i)
        rig.add(f"seg{i}", (0, BODY_Y, z - step / 2), (0, BODY_Y, z + step / 2), parent)
        parent = f"seg{i}"
    front = LENGTH / 2
    rig.add("head", (0, BODY_Y, front), (0, BODY_Y, front + 0.08), "seg0")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"shear_{tag}", (s * 0.022, BODY_Y - 0.012, front + 0.06), (s * 0.03, BODY_Y - 0.03, front + 0.06 + SHEAR_LEN),
                "head")
    rig.add("snuffer", (0, BODY_Y + 0.05, front + 0.03), (0, BODY_Y + 0.13, front + 0.14), "head")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(NSEG):
            hip, knee, foot = leg_pts(s, i)
            rig.add(f"leg_{tag}{i}_a", hip, knee, f"seg{i}")
            rig.add(f"leg_{tag}{i}_b", knee, foot, f"leg_{tag}{i}_a")
    pts = pole_pts()
    parent = f"seg{NSEG - 1}"
    for k in range(3):
        rig.add(f"pole{k}", pts[k], pts[k + 1], parent)
        parent = f"pole{k}"
    rig.add("taper", pts[3], pts[4], "pole2")
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def aged_brass(P: np.ndarray, seed: int) -> np.ndarray:
    """Brass going bronze_patina in the low places (the underside) and in patches: a thousand years of it."""
    n = ck.fbm(P * 12.0, seed)
    low = ck.smoothstep(BODY_Y + 0.02, BODY_Y - 0.08, P[:, 1])
    patina = np.clip(0.15 + 0.5 * ck.smoothstep(0.0, 0.35, n) + 0.45 * low, 0.0, 0.85)
    return ck.mix(PAL["brass"], PAL["bronze_patina"], patina[:, None])


def segments(mesh: ck.Mesh, rig: ck.Rig) -> None:
    step = LENGTH / NSEG
    for i in range(NSEG):
        z, r = seg_z(i), seg_r(i)
        z0, z1 = z - step / 2 + 0.008, z + step / 2 - 0.008
        path = np.array([[0.0, BODY_Y, zz] for zz in np.linspace(z0, z1, 5)])
        prof = r * (0.86 + 0.14 * np.sin(np.linspace(0.0, math.pi, 5)))  # each segment swells a little at its middle
        P, T = ck.tube(path, prof, 12)
        ck.finish(mesh, P, T, "body", aged_brass(P, SEED + i), rig.rigid(f"seg{i}"), wet=0.1, cavity=0.3)
        for zz in (z0 + 0.006, z1 - 0.006):  # the rolled rims at both ends, darker in their grooves
            rp = np.array([[0.0, BODY_Y, zz - 0.005], [0.0, BODY_Y, zz + 0.005]])
            Pr, Tr = ck.tube(rp, np.array([r + RIM, r + RIM]), 12, cap_start=False, cap_end=False)
            col = ck.mix(aged_brass(Pr, SEED + 20 + i), PAL["lacquer_black"], 0.25)
            ck.finish(mesh, Pr, Tr, "body", col, rig.rigid(f"seg{i}"), wet=0.1, cavity=0.5)
    # the head's cap and the tail's end plate
    Ph, Th = ck.ellipsoid((0, BODY_Y, LENGTH / 2 + 0.01), (RADIUS[0] * 0.85, RADIUS[0] * 0.85, 0.05), 6, 14)
    ck.finish(mesh, Ph, Th, "body", aged_brass(Ph, SEED + 30), rig.rigid("seg0"), wet=0.1, cavity=0.3)
    Pt, Tt = ck.ellipsoid((0, BODY_Y, -LENGTH / 2 + 0.005), (RADIUS[1] * 0.9, RADIUS[1] * 0.9, 0.03), 5, 12)
    ck.finish(mesh, Pt, Tt, "body", aged_brass(Pt, SEED + 31), rig.rigid(f"seg{NSEG - 1}"), wet=0.1, cavity=0.3)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    start = mesh.count
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(NSEG):
            hip, knee, foot = leg_pts(s, i)
            for seg, a, b, r0, r1 in (("a", hip, knee, 0.011, 0.008), ("b", knee, foot, 0.008, 0.005)):
                mid = (a + b) / 2 + np.array([0.0, 0.012, 0.0])
                P, T = ck.tube(ck.bezier([a, mid, b], 5), np.linspace(r0, r1, 5), 6)
                ck.finish(mesh, P, T, "leg", PAL["lacquer_black"], rig.rigid(f"leg_{tag}{i}_{seg}"), wet=0.1, cavity=0.2)
            Pk, Tk = ck.ellipsoid(knee, (0.012,) * 3, 4, 6)  # the brass hinge pin at the knee
            ck.finish(mesh, Pk, Tk, "body", aged_brass(Pk, SEED + 40 + i), rig.rigid(f"leg_{tag}{i}_a"), wet=0.1)
            # the rope hook: the foot curls in under itself, its point turned back toward the body
            hook = [foot, foot + np.array([s * 0.016, -0.004, 0.0]), foot + np.array([s * 0.012, 0.0, -0.014]),
                    foot + np.array([s * -0.004, 0.004, -0.012])]
            P, T = ck.tube(ck.bezier(hook, 5), np.linspace(0.005, 0.0015, 5), 5)
            P[:, 1] = np.maximum(P[:, 1], 0.0015)
            ck.finish(mesh, P, T, "leg", PAL["lacquer_black"], rig.rigid(f"leg_{tag}{i}_b"), wet=0.1)
    mark("feet", mesh, start)


def head_kit(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The wick-shears (two blades worn bright on their edges, on a pivot) and the snuffer cone on its arm."""
    front = LENGTH / 2
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        b = rig.bones[rig.index(f"shear_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        P, T = ck.tube(np.linspace(h0, h1, 5), np.array([0.009, 0.008, 0.007, 0.005, 0.0015]), 6)
        P[:, 0] = h0[0] + (P[:, 0] - h0[0]) * 0.45  # flattened into a blade
        edge = ck.smoothstep(0.3, 1.0, (P[:, 2] - h0[2]) / SHEAR_LEN) * ck.smoothstep(0.0, -0.006, P[:, 1] - h0[1])
        col = ck.mix(PAL["brass"] * 0.85, PAL["brass"] * 1.25, edge[:, None])
        ck.finish(mesh, P, T, "body", col, rig.rigid(f"shear_{tag}"), wet=0.1, cavity=0.2)
    Pp, Tp = ck.ellipsoid((0, BODY_Y - 0.012, front + 0.06), (0.03, 0.012, 0.012), 4, 8)  # the shears' pivot boss
    ck.finish(mesh, Pp, Tp, "body", PAL["lacquer_black"], rig.rigid("head"), wet=0.1)
    b = rig.bones[rig.index("snuffer")]
    h0, h1 = np.asarray(b.head), np.asarray(b.tail)
    P, T = ck.tube(np.linspace(h0, h1, 3), np.array([0.008, 0.007, 0.006]), 6)
    ck.finish(mesh, P, T, "body", aged_brass(P, SEED + 50), rig.rigid("snuffer"), wet=0.1)
    cone = [(0.0, 0.0), (0.012, 0.004), (0.026, 0.03), (0.03, 0.048)]  # (radius, depth), hanging open-mouthed
    Pc, Tc = ck.lathe([(r, -d) for r, d in cone], 12)
    Pc = Pc + h1
    ck.finish(mesh, Pc, Tc, "body", aged_brass(Pc, SEED + 51), rig.rigid("snuffer"), wet=0.1, cavity=0.4)


def pole(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The pole, its taper in a salt-glass thimble, and the oil reservoir at its foot with the weak point's seam."""
    pts = pole_pts()
    for k in range(3):
        a, b = pts[k], pts[k + 1]
        P, T = ck.tube(np.linspace(a, b, 4), np.linspace(0.014 - 0.002 * k, 0.012 - 0.002 * k, 4), 8)
        ck.finish(mesh, P, T, "body", aged_brass(P, SEED + 60 + k), rig.rigid(f"pole{k}"), wet=0.1, cavity=0.2)
    tip = pts[3]
    # the cup that holds the thimble, the thimble round the light, and the light itself
    cup = [(0.0, 0.0), (0.02, 0.0), (0.024, 0.014), (THIMBLE[0] + 0.004, 0.02)]
    Pc, Tc = ck.lathe(cup[::-1], 12)  # top first: ck.lathe's outward faces run top to bottom
    Pc = Pc + tip
    ck.finish(mesh, Pc, Tc, "body", aged_brass(Pc, SEED + 64), rig.rigid("taper"), wet=0.1, cavity=0.3)
    prof = [(THIMBLE[0], 0.0), (THIMBLE[0] * 1.05, THIMBLE[1] * 0.5), (THIMBLE[0] * 0.8, THIMBLE[1] * 0.85),
            (THIMBLE[0] * 0.25, THIMBLE[1]), (0.0, THIMBLE[1] * 1.02)]
    Pg, Tg = ck.lathe(prof[::-1], 14)
    Pg = Pg + tip + np.array([0.0, 0.018, 0.0])
    light = tip + np.array([0.0, 0.018 + THIMBLE[1] * 0.42, 0.0])
    glow = ck.smoothstep(0.06, 0.0, np.linalg.norm(Pg - light, axis=1))
    ck.finish(mesh, Pg, Tg, "glass", PAL["salt_glass"], rig.rigid("taper"), wet=0.6, emission=glow)
    Pl, Tl = ck.ellipsoid(light, (0.012, 0.022, 0.012), 6, 8)
    ck.finish(mesh, Pl, Tl, "taper", PAL["glimmer_bound"], rig.rigid("taper"), wet=0.0, emission=1.0)
    # the reservoir: a squat brass can on the last segment, the pole rising from its lid
    base = tail_top() + np.array([0.0, -0.01, 0.0])
    can = [(0.0, 0.0), (RESERVOIR[0], 0.0), (RESERVOIR[0] * 1.05, RESERVOIR[1] * 0.5), (RESERVOIR[0], RESERVOIR[1]),
           (RESERVOIR[0] * 0.55, RESERVOIR[1] * 1.08), (0.0, RESERVOIR[1] * 1.1)]
    Pr, Tr = ck.lathe(can[::-1], 14)
    Pr = Pr + base
    ck.finish(mesh, Pr, Tr, "body", aged_brass(Pr, SEED + 70), rig.rigid(f"seg{NSEG - 1}"), wet=0.15, cavity=0.4)
    # the filler cap on the reservoir's flank, toward the head, and the hairline seam round it (the weak point)
    cap_c = base + np.array([0.0, RESERVOIR[1] * 0.55, RESERVOIR[0] * 0.98])
    Pf, Tf = ck.ellipsoid(cap_c, (0.018, 0.018, 0.008), 5, 10)
    ck.finish(mesh, Pf, Tf, "body", aged_brass(Pf, SEED + 71), rig.rigid(f"seg{NSEG - 1}"), wet=0.1)
    ring = np.array([cap_c + np.array([0.021 * math.cos(a), 0.021 * math.sin(a), 0.002])
                     for a in np.linspace(0.0, 2 * math.pi, 17)])
    Ps, Ts = ck.tube(ring, np.full(len(ring), 0.0025), 4, cap_start=False, cap_end=False)
    ck.finish(mesh, Ps, Ts, "seam", PAL["spawn_wound"] * 0.65, rig.rigid(f"seg{NSEG - 1}"), wet=0.2, emission=1.0)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("wick_crawler")
    segments(mesh, rig)
    legs(mesh, rig)
    head_kit(mesh, rig)
    pole(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips (the sheet's table)
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 3.0
ATTACK_SEC = 1.1
ATTACK_CONTACT = 0.5
CAST_SEC = 1.6
CAST_CONTACT = 0.95
HIT_SEC = 0.5
KO_SEC = 1.6
KO_CURL_SEC = 0.55  # each pair's curl (eased, so the folding legs don't pop); the last pair is in before the roll
LEG_TAGS = [f"{tag}{i}" for tag in ("l", "r") for i in range(NSEG)]


def tick(c: ck.Clip, leg: str, t0: float, lift: float = 8.0, dur: float = 0.18) -> None:
    """A foot ticks: it lifts and sets down again where it was."""
    s = 1.0 if leg[0] == "l" else -1.0
    c.key(f"leg_{leg}_a", t0, (0, 0, 0))
    c.key(f"leg_{leg}_a", t0 + dur * 0.5, (0, 0, s * lift))
    c.key(f"leg_{leg}_a", t0 + dur, (0, 0, 0))


def hold_legs(c: ck.Clip, length: float) -> None:
    for leg in LEG_TAGS:
        for seg in ("a", "b"):
            c.key(f"leg_{leg}_{seg}", 0.0)
            c.key(f"leg_{leg}_{seg}", length)


def snip(c: ck.Clip, t0: float, opn: float = 22.0, dur: float = 0.24) -> None:
    for tag, s in (("l", 1.0), ("r", -1.0)):
        c.key(f"shear_{tag}", t0, (0, 0, 0))
        c.key(f"shear_{tag}", t0 + dur * 0.45, (0, s * opn, 0))
        c.key(f"shear_{tag}", t0 + dur, (0, 0, 0))


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # a wave runs down the legs, front to back; the shears snip twice
    hold_legs(c, IDLE_SEC)
    for i in range(NSEG):
        for wave in (0.0, 1.5):
            tick(c, f"l{i}", 0.1 + wave + 0.12 * i)
            tick(c, f"r{i}", 0.16 + wave + 0.12 * i)
    snip(c, 0.7)
    snip(c, 1.05)
    c.wave("pole0", amp_rot=(2.5, 0, 1.6), cycles=1)
    c.wave("pole1", amp_rot=(1.5, 0, 1.2), cycles=1, phase=0.6)
    c.wave("seg3", amp_rot=(0, 1.2, 0), cycles=1, phase=0.3)
    c.wave("seg0", amp_rot=(-1.5, 2.0, 0), cycles=2, phase=1.0)
    c.key("taper", 0.0)
    c.key("taper", IDLE_SEC)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # the trim: the head rears 20 degrees and the shears snap shut at the target
    hold_legs(c, ATTACK_SEC)
    for t, s, opn in ((0.0, 0.0, 0.0), (0.3, 1.0, 1.0), (ATTACK_CONTACT, 0.6, 0.0), (0.7, 0.4, 0.0),
                      (ATTACK_SEC, 0.0, 0.0)):
        c.key("seg1", t, (-9.0 * s, 0, 0))
        c.key("seg0", t, (-11.0 * s, 0, 0))
        c.key("head", t, (6.0 * s, 0, 0))
        c.key("shear_l", t, (0, 28.0 * opn, 0))
        c.key("shear_r", t, (0, -28.0 * opn, 0))
    for t, p in ((0.0, 0.0), (ATTACK_CONTACT, 1.0), (ATTACK_SEC, 0.0)):
        c.key("pole0", t, (-5.0 * p, 0, 0))
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the relight: the pole bows forward over the head and the taper dips to a wick
    hold_legs(c, CAST_SEC)
    for t, s in ((0.0, 0.0), (0.5, 0.7), (CAST_CONTACT, 1.0), (1.2, 0.85), (CAST_SEC, 0.0)):
        c.key("pole0", t, (40.0 * s, 0, 0))
        c.key("pole1", t, (24.0 * s, 0, 0))
        c.key("pole2", t, (16.0 * s, 0, 0))
        c.key("taper", t, (-20.0 * s, 0, 0))
        c.key("seg0", t, (5.0 * s, 0, 0))
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # the body kinks sideways in the middle, the legs on that side splay, the pole whips
    hold_legs(c, HIT_SEC)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.24, -0.35), (0.36, 0.12), (HIT_SEC, 0.0)):
        c.key("seg4", t, (0, 7.0 * s, 0))
        c.key("seg3", t, (0, 9.0 * s, 0))
        c.key("seg2", t, (0, -8.0 * s, 0))
        c.key("seg0", t, (-4.0 * s, -5.0 * s, 0))
        c.key("pole0", t, (0, 0, -14.0 * s))
        c.key("pole1", t, (0, 0, -9.0 * s))
        for i in range(NSEG):
            c.key(f"leg_l{i}_a", t, (0, 0, 9.0 * max(s, 0.0)))
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # the legs curl in under it pair by pair from the head back; it rolls onto its side
    for i in range(NSEG):
        t0 = 0.08 + 0.07 * i
        for tag, sd in (("l", 1.0), ("r", -1.0)):
            c.key(f"leg_{tag}{i}_a", 0.0)
            c.key(f"leg_{tag}{i}_b", 0.0)
            c.key(f"leg_{tag}{i}_a", t0 + KO_CURL_SEC, (0, 0, sd * 38.0))
            c.key(f"leg_{tag}{i}_b", t0 + KO_CURL_SEC, (0, 0, -sd * 95.0))
            c.key(f"leg_{tag}{i}_a", KO_SEC, (0, 0, sd * 38.0))
            c.key(f"leg_{tag}{i}_b", KO_SEC, (0, 0, -sd * 95.0))
    for t, s in ((0.0, 0.0), (0.55, 0.08), (1.22, 1.0), (1.38, 0.95), (KO_SEC, 1.0)):  # the roll eased over 0.65 s
        c.key("root", t, (0, 0, 82.0 * s), (0, 0, 0))
    for t, s in ((0.0, 0.0), (1.22, 1.0), (KO_SEC, 1.0)):
        c.key("pole0", t, (0, 0, -8.0 * s))
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# Kept off the floor (common/grounding.py): each leg turns up about its hip where its hook would dip, and in the KO the
# whole machine lifts the least it takes to lie on its side on the floor, not through it. The planted feet hold their
# spots while the body rears, kinks and bows over them.
GROUNDED_LIMBS = [(f"leg_{leg}_a", 2, 1.0 if leg[0] == "l" else -1.0, 75.0) for leg in LEG_TAGS] + [
    ("root", gr.LIFT, 1.0, 0.6, ("ko",))]
PINNED_LEGS = [(f"leg_{leg}_a", f"leg_{leg}_b", 2, 1.0 if leg[0] == "l" else -1.0) for leg in LEG_TAGS]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    pinned = gr.pinned(rig, mesh, gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS), PINNED_LEGS)
    return gr.reground(rig, mesh, pinned, GROUNDED_LIMBS)


def report(rig: ck.Rig, mesh: ck.Mesh) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    poser = gr.Poser(rig, mesh)
    for c in export_clips(rig, mesh):
        low = gr.lowest(poser, c)
        print(f"{c.name:7s} {c.length:.2f}s: lowest {min(low):+.4f}")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    if args.report or not args.out:
        report(rig, mesh)
        return
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "wick_crawler"})
    print(f"wick_crawler: {info}")


if __name__ == "__main__":
    main()
