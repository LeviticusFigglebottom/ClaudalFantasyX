"""Conduit crawler, Ch11 Lowlight temple (M3-CRE-627): docs/kb/art/creatures/act2/conduit_crawler.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/conduit_crawler/build_conduit_crawler.py -- \
    --out assets/creatures/conduit_crawler/conduit_crawler.glb

A Lit Age conduit-cleaning machine still on its rounds: a beetle-like salt-glass dome 0.7 m long on six thin brass
legs, a brush and a wiper on its two short fore-arms, and a dim bound light inside to see by. It isn't hostile; it
tends. Its one exaggeration is that it has kept working for four hundred years. The shell is `salt_glass`, its
light `glimmer_bound` (README rule 3: a Lit Age construct's bound light, steady and unpulsing), seen through the
crown of the shell on the shell slot's emission mask. The frame is `brass` going `bronze_patina` with age, the feet
and joints `lacquer_black`, the brush's bristles `sand_cloth`. The weak point is the shell's seam, the raised bead
where its two halves meet down the back: `spawn_wound`, its own slot.

The feet stand at y 0.

Rig (18 bones): root, `body`, six legs of two (`leg_l0_a`/`leg_l0_b` .. `leg_r2_a`/`leg_r2_b`, front to back) and
two arms of two (`arm_l_a`/`arm_l_b` with the brush, `arm_r_a`/`arm_r_b` with the wiper).

`python3 build_conduit_crawler.py --report` prints the triangle count and per-clip skinned bounds (numpy, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6274
PAL = {k: ck.hexrgb(v) for k, v in {
    "salt_glass": "#BFE6E0", "brass": "#B08D57", "bronze_patina": "#5F8A78", "lacquer_black": "#1D1916",
    "glimmer_bound": "#4FB3B0", "spawn_wound": "#3FE0C8", "sand_cloth": "#C9B48E", "timber_weathered": "#7E6A55",
}.items()}

BODY_Y = 0.24  # the shell's rim (its equator) and the body's pivot
SHELL_R = (0.235, 0.2, 0.35)  # 0.7 m long, 0.47 m wide, its crown 0.44 m up
LIGHT = np.array([0.0, BODY_Y + 0.07, 0.07])  # the bound light inside, under the crown toward the front
LEG_Z = (0.17, 0.0, -0.17)
FOOT_PAD = 0.011  # the foot pads' half-height: their centres stand this high
ARM_SHOULDER = (0.075, BODY_Y - 0.035, 0.33)
LEG_RINGS = 4  # rings along each leg segment's gentle bow
KNUCKLE = (0.016, 0.026)  # the knee hinge: its radius and half-length across the leg
COLLAR = (0.16, 0.022)  # the thigh's collar: where (a share of hip to knee) and its radius
SLEEVE = (0.04, 0.55)  # the shin's piston sleeve: from and to, as shares of knee to foot

PARTS: dict[str, tuple[int, int]] = {}


def mark(name: str, mesh: ck.Mesh, start: int) -> None:
    lo, _hi = PARTS.get(name, (start, start))
    PARTS[name] = (min(lo, start), mesh.count)


def leg_pts(side: float, i: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = LEG_Z[i]
    hip = np.array([side * 0.2, BODY_Y - 0.03, z])
    knee = np.array([side * 0.33, BODY_Y + 0.09, z * 1.2])
    foot = np.array([side * 0.45, FOOT_PAD, z * 1.45 + 0.02])
    return hip, knee, foot


def arm_pts(side: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sh = np.array([side * ARM_SHOULDER[0], ARM_SHOULDER[1], ARM_SHOULDER[2]])
    elbow = np.array([side * 0.1, BODY_Y - 0.06, 0.45])
    hand = np.array([side * 0.095, 0.075, 0.53])
    return sh, elbow, hand


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    rig.add("body", (0, BODY_Y, 0), (0, BODY_Y, 0.3), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(3):
            hip, knee, foot = leg_pts(s, i)
            rig.add(f"leg_{tag}{i}_a", hip, knee, "body")
            rig.add(f"leg_{tag}{i}_b", knee, foot, f"leg_{tag}{i}_a")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        sh, elbow, hand = arm_pts(s)
        rig.add(f"arm_{tag}_a", sh, elbow, "body")
        rig.add(f"arm_{tag}_b", elbow, hand, f"arm_{tag}_a")
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def aged_brass(P: np.ndarray, seed: int) -> np.ndarray:
    """Brass going bronze_patina: verdigris in the low places and in patches, four hundred years of it."""
    n = ck.fbm(P * 11.0, seed)
    patina = np.clip(0.25 + 0.55 * ck.smoothstep(-0.05, 0.35, n) + 0.3 * ck.smoothstep(0.12, 0.0, P[:, 1]), 0.0, 0.9)
    return ck.mix(PAL["brass"], PAL["bronze_patina"], patina[:, None])


def shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rows = 10
    prof = [(math.sin(th), math.cos(th)) for th in np.linspace(0.0, math.pi / 2, rows)]
    P, T = ck.lathe(prof, 28)
    P = P * np.asarray(SHELL_R) + np.array([0.0, BODY_Y, 0.0])
    # the light inside shows through the crown: a soft glow on the glass, brightest over the light
    d = np.linalg.norm((P - LIGHT) / np.array([1.0, 1.4, 1.0]), axis=1)
    glow = 0.85 * np.exp(-(d / 0.17) ** 2)
    col = ck.mix(PAL["salt_glass"], PAL["glimmer_bound"], (0.35 * glow)[:, None])
    start = mesh.count
    ck.finish(mesh, P, T, "shell", col, rig.rigid("body"), wet=0.2, cavity=0.0, emission=glow)
    mark("shell", mesh, start)
    # the seam: a raised bead down the back where the two halves meet (the weak point)
    th = np.linspace(-math.pi / 2 + 0.12, math.pi / 2 - 0.12, 30)
    path = np.column_stack([np.zeros(len(th)), BODY_Y + SHELL_R[1] * np.cos(th) + 0.004, SHELL_R[2] * np.sin(th)])
    Ps, Ts = ck.tube(path, 0.0085, 8)
    start = mesh.count
    ck.finish(mesh, Ps, Ts, "seam", PAL["spawn_wound"] * 0.65, rig.rigid("body"), wet=0.3, emission=1.0)
    mark("seam", mesh, start)


def frame(mesh: ck.Mesh, rig: ck.Rig) -> None:
    start = mesh.count
    # the rim: a brass hoop round the shell's edge
    a = np.linspace(0.0, 2.0 * math.pi, 37)[:-1]
    loop = np.column_stack([(SHELL_R[0] + 0.006) * np.sin(a), np.full(len(a), BODY_Y), (SHELL_R[2] + 0.006) * np.cos(a)])
    loop = np.vstack([loop, loop[:1]])
    P, T = ck.tube(loop, 0.018, 6, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "frame", aged_brass(P, SEED), rig.rigid("body"), wet=0.1, cavity=0.3)
    # two transverse hoops over the shell: the Lit Age's ribs
    for z0 in (0.13, -0.12):
        r = math.sqrt(max(1.0 - (z0 / SHELL_R[2]) ** 2, 0.0))
        th = np.linspace(-math.pi / 2, math.pi / 2, 22)
        path = np.column_stack([SHELL_R[0] * r * np.sin(th) * 1.02, BODY_Y + SHELL_R[1] * r * np.cos(th) + 0.004,
                                np.full(len(th), z0)])
        P, T = ck.tube(path, 0.009, 6)
        ck.finish(mesh, P, T, "frame", aged_brass(P, SEED + 1), rig.rigid("body"), wet=0.1, cavity=0.2)
    # the belly plate and the head housing the arms hang from
    P, T = ck.ellipsoid((0.0, BODY_Y - 0.01, 0.0), (0.215, 0.055, 0.32), 6, 20)
    P[:, 1] = np.minimum(P[:, 1], BODY_Y)
    col = ck.mix(aged_brass(P, SEED + 2), PAL["lacquer_black"], 0.45)
    ck.finish(mesh, P, T, "frame", col, rig.rigid("body"), wet=0.1, cavity=0.4)
    P, T = ck.ellipsoid((0.0, BODY_Y - 0.02, 0.33), (0.12, 0.055, 0.07), 6, 14)
    ck.finish(mesh, P, T, "frame", aged_brass(P, SEED + 3), rig.rigid("body"), wet=0.1, cavity=0.3)
    mark("frame", mesh, start)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    start = mesh.count
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(3):
            hip, knee, foot = leg_pts(s, i)
            for seg, p0, p1, r0, r1 in (("a", hip, knee, 0.015, 0.012), ("b", knee, foot, 0.011, 0.008)):
                P, T = ck.tube(ck.bezier([p0, (p0 + p1) / 2 + np.array([s * 0.01, 0.012, 0.0]), p1], LEG_RINGS),
                               np.linspace(r0, r1, LEG_RINGS), 6)
                ck.finish(mesh, P, T, "frame", aged_brass(P, SEED + 10 + i), rig.rigid(f"leg_{tag}{i}_{seg}"),
                          wet=0.0, cavity=0.2)
            P, T = ck.ellipsoid(hip, (0.02, 0.02, 0.02), 4, 6)
            ck.finish(mesh, P, T, "frame", PAL["lacquer_black"], rig.rigid("body"), wet=0.1, cavity=0.3)
            # machined detail (the plan sheet: the legs read as plain thin tubes up close): a hinge knuckle across the
            # knee with brass end caps, a collar near the hip, and a piston sleeve over the shin (within the 5k budget)
            axis = np.cross(knee - hip, foot - knee)
            axis /= np.linalg.norm(axis)
            # the knuckle: lacquer-black, its end caps brass (by vertex colour along the hinge)
            knuckle = np.array([knee - axis * KNUCKLE[1], knee + axis * KNUCKLE[1]])
            P, T = ck.tube(knuckle, KNUCKLE[0], 6)
            ends = ck.smoothstep(0.6, 0.9, np.abs((P - knee) @ axis) / KNUCKLE[1])
            col = ck.mix(PAL["lacquer_black"], aged_brass(P, SEED + 20 + i), ends[:, None])
            ck.finish(mesh, P, T, "frame", col, rig.rigid(f"leg_{tag}{i}_a"), wet=0.1, cavity=0.3)
            thigh = (knee - hip) / np.linalg.norm(knee - hip)
            c = hip + (knee - hip) * COLLAR[0]
            P, T = ck.tube(np.array([c - thigh * 0.007, c + thigh * 0.007]), COLLAR[1], 6)
            ck.finish(mesh, P, T, "frame", PAL["lacquer_black"], rig.rigid(f"leg_{tag}{i}_a"), wet=0.1, cavity=0.3)
            P, T = ck.tube(np.array([knee + (foot - knee) * f for f in SLEEVE]), np.array([0.016, 0.0135]), 6)
            ck.finish(mesh, P, T, "frame", ck.mix(aged_brass(P, SEED + 30 + i), PAL["lacquer_black"], 0.25),
                      rig.rigid(f"leg_{tag}{i}_b"), wet=0.0, cavity=0.3)
    mark("legs", mesh, start)
    start = mesh.count
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(3):
            _hip, _knee, foot = leg_pts(s, i)
            P, T = ck.ellipsoid(foot, (0.022, FOOT_PAD, 0.03), 4, 8)
            ck.finish(mesh, P, T, "frame", PAL["lacquer_black"], rig.rigid(f"leg_{tag}{i}_b"), wet=0.1)
    mark("feet", mesh, start)


def arms(mesh: ck.Mesh, rig: ck.Rig) -> None:
    start = mesh.count
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        sh, elbow, hand = arm_pts(s)
        for seg, p0, p1, r in (("a", sh, elbow, 0.014), ("b", elbow, hand, 0.012)):
            P, T = ck.tube(np.array([p0, (p0 + p1) / 2, p1]), r, 6)
            ck.finish(mesh, P, T, "frame", aged_brass(P, SEED + 20), rig.rigid(f"arm_{tag}_{seg}"), wet=0.1, cavity=0.2)
        P, T = ck.ellipsoid(elbow, (0.018,) * 3, 5, 8)
        ck.finish(mesh, P, T, "frame", PAL["lacquer_black"], rig.rigid(f"arm_{tag}_a"), wet=0.1)
        bone = rig.rigid(f"arm_{tag}_b")
        if tag == "l":
            # the brush: a round brass cup, its bristles worn down to the floor
            P, T = ck.lathe([(0.0, 0.035), (0.04, 0.035), (0.042, 0.018), (0.0, 0.018)], 12)
            P = P + np.array([hand[0], hand[1] - 0.06, hand[2]])
            ck.finish(mesh, P, T, "frame", aged_brass(P, SEED + 21), bone, wet=0.1, cavity=0.3)
            P, T = ck.lathe([(0.0, 0.018), (0.038, 0.018), (0.034, 0.0), (0.0, 0.0)], 12)
            P = P + np.array([hand[0], hand[1] - 0.06, hand[2]])
            ck.finish(mesh, P, T, "frame", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.35), bone,
                      wet=0.4, cavity=0.5)
        else:
            # the wiper: a black blade across a brass bar, and a small brush behind it
            bar = np.array([[hand[0] - 0.05, hand[1] - 0.04, hand[2]], [hand[0] + 0.05, hand[1] - 0.04, hand[2]]])
            P, T = ck.tube(bar, 0.009, 6)
            ck.finish(mesh, P, T, "frame", aged_brass(P, SEED + 22), bone, wet=0.1)
            P, T = ck.ellipsoid((hand[0], hand[1] - 0.05, hand[2]), (0.05, 0.02, 0.005), 4, 10)
            ck.finish(mesh, P, T, "frame", PAL["lacquer_black"], bone, wet=0.6)
            P, T = ck.tube(np.array([hand, hand + np.array([0.0, -0.04, 0.0])]), 0.01, 6)
            ck.finish(mesh, P, T, "frame", aged_brass(P, SEED + 23), bone, wet=0.1)
    mark("arms", mesh, start)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("conduit_crawler")
    shell(mesh, rig)
    frame(mesh, rig)
    legs(mesh, rig)
    arms(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 2.0
ATTACK_SEC = 1.0
ATTACK_CONTACT = 0.45
CAST_SEC = 1.6
CAST_CONTACT = 1.0
HIT_SEC = 0.5
KO_SEC = 1.6
KO_THIGH, KO_SHIN = 52.0, -24.0  # the knees fold up and the body sinks between them, the feet where they stood
KO_DROP = 0.147  # the belly plate comes to rest 3 cm off the floor
KO_ARM = (12.0, 55.0)  # the arms fold up under its chin
TRIPODS = (("l0", "r1", "l2"), ("r0", "l1", "r2"))


def tick(c: ck.Clip, leg: str, t0: float, lift: float = 7.0, dur: float = 0.16) -> None:
    """A foot ticks: it lifts and sets down again where it was."""
    s = 1.0 if leg[0] == "l" else -1.0
    c.key(f"leg_{leg}_a", t0, (0, 0, 0))
    c.key(f"leg_{leg}_a", t0 + dur * 0.5, (0, 0, s * lift))
    c.key(f"leg_{leg}_a", t0 + dur, (0, 0, 0))


def hold_legs(c: ck.Clip, length: float) -> None:
    for tag in ("l", "r"):
        for i in range(3):
            for seg in ("a", "b"):
                c.key(f"leg_{tag}{i}_{seg}", 0.0)
                c.key(f"leg_{tag}{i}_{seg}", length)


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # it scrubs at the floor, its feet ticking
    hold_legs(c, IDLE_SEC)
    for k, group in enumerate(TRIPODS):
        for leg in group:
            for t0 in (0.15 + 0.5 * k, 1.15 + 0.5 * k):
                tick(c, leg, t0)
    for tag, ph in (("l", 0.0), ("r", math.pi)):  # the brush and the wiper scrub back and forth, never into the floor
        c.wave(f"arm_{tag}_a", amp_rot=(9.0, 0, 0), base_rot=(-9.0, 0, 0), cycles=2, phase=ph)
        c.wave(f"arm_{tag}_b", amp_rot=(7.0, 0, 0), base_rot=(-7.0, 0, 0), cycles=2, phase=ph + 0.8)
    c.wave("body", amp_rot=(0.8, 0, 0), amp_loc=(0, 0.004, 0), base_loc=(0, 0.006, 0), cycles=2, phase=0.4)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # a brush jab: it rocks back, cocks the brush, and jabs it out
    hold_legs(c, ATTACK_SEC)
    for t, rx, loc, la, lb, ra in ((0.0, 0, (0, 0, 0), 0, 0, 0), (0.25, -5.0, (0, 0.024, -0.02), -40.0, 0.0, -8.0),
                                   (ATTACK_CONTACT, 6.0, (0, 0.036, 0.03), -18.0, -58.0, -6.0),
                                   (0.62, 3.0, (0, 0.02, 0.015), -14.0, -40.0, -4.0),
                                   (ATTACK_SEC, 0, (0, 0, 0), 0, 0, 0)):
        c.key("body", t, (rx, 0, 0), loc)
        c.key("arm_l_a", t, (la, 0, 0))
        c.key("arm_l_b", t, (lb, 0, 0))
        c.key("arm_r_a", t, (ra, 0, 0))
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the repair: it leans in and its arms work fast, feet pattering
    hold_legs(c, CAST_SEC)
    for t, rx, ly in ((0.0, 0.0, 0.0), (0.3, 4.0, 0.025), (1.3, 4.0, 0.025), (CAST_SEC, 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0.0))
    n = 10
    for k in range(n + 1):
        t = 0.3 + k * (1.0 / n)
        s = 1.0 if k % 2 else -1.0
        amp = 0.0 if k in (0, n) else 1.0
        c.key("arm_l_a", t, (-20.0 + 14.0 * s * amp, 0, 0))
        c.key("arm_l_b", t, (-25.0 - 10.0 * s * amp, 0, 0))
        c.key("arm_r_a", t, (-20.0 - 14.0 * s * amp, 0, 0))
        c.key("arm_r_b", t, (-25.0 + 10.0 * s * amp, 0, 0))
    for arm in ("arm_l_a", "arm_l_b", "arm_r_a", "arm_r_b"):
        c.key(arm, 0.0)
        c.key(arm, CAST_SEC)
    for k, group in enumerate(TRIPODS):
        for leg in group:
            for t0 in (0.35 + 0.16 * k, 0.75 + 0.16 * k, 1.1 + 0.16 * k):
                tick(c, leg, t0, lift=5.0, dur=0.14)
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # it is knocked up off its feet and rocks on its legs
    hold_legs(c, HIT_SEC)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.24, -0.35), (0.36, 0.12), (HIT_SEC, 0.0)):
        c.key("body", t, (-4.0 * s, 0, 6.0 * s), (0, 0.11 * max(s, 0.0) + 0.06 * max(-s, 0.0), -0.03 * s))
        c.key("arm_l_a", t, (-18.0 * max(s, 0.0), 0, 0))
        c.key("arm_r_a", t, (-18.0 * max(s, 0.0), 0, 0))
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # its light dims (material, not modelled) and its legs fold under it
    for t, s in ((0.0, 0.0), (0.3, 0.25), (0.9, 0.8), (1.25, 1.0), (KO_SEC, 1.0)):
        c.key("body", t, (0, 0, 0), (0, -KO_DROP * s, 0))
        for tag, sd in (("l", 1.0), ("r", -1.0)):
            for i in range(3):
                c.key(f"leg_{tag}{i}_a", t, (0, 0, sd * KO_THIGH * s))
                c.key(f"leg_{tag}{i}_b", t, (0, 0, sd * KO_SHIN * s))
            c.key(f"arm_{tag}_a", t, (-KO_ARM[0] * s, 0, 0))
            c.key(f"arm_{tag}_b", t, (-KO_ARM[1] * s, 0, 0))
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender): skinned bounds, the feet and the peak time per clip
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


def skin(rig: ck.Rig, arrays: dict, pose: dict) -> np.ndarray:
    P, J, W = arrays["pos"], arrays["joints"], arrays["weights"]
    Rs = np.stack([pose[b.name][0] for b in rig.bones])
    ts = np.stack([pose[b.name][1] for b in rig.bones])
    out = np.zeros_like(P)
    for k in range(2):
        out += W[:, k:k + 1] * (np.einsum("nij,nj->ni", Rs[J[:, k]], P) + ts[J[:, k]])
    return out


def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    f0, f1 = PARTS["feet"]
    feet = np.arange(f0, f1)
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, flo, disp = np.inf, -np.inf, np.inf, []
        for f in range(frames + 1):
            P = skin(rig, arrays, fk(rig, c, min(f / ck.FPS, c.length)))
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            flo = min(flo, float(P[feet, 1].min()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        P = skin(rig, arrays, fk(rig, c, c.length))
        print(f"{c.name:7s} {c.length:.2f}s: y {lo:+.3f}..{hi:.3f}; feet lowest {flo:+.3f}; end {P[:, 1].min():+.3f}.."
              f"{P[:, 1].max():.3f} (feet {P[feet, 1].min():+.3f}); peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "conduit_crawler"})
    print(f"conduit_crawler: {info}")


if __name__ == "__main__":
    main()
