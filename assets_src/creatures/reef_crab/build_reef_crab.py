"""Reef crab battle model (M2-CRE-04): docs/kb/art/creatures/reef_crab.md.

blender --background --factory-startup --python assets_src/creatures/reef_crab/build_reef_crab.py -- \
    --out assets/creatures/reef_crab/reef_crab.glb

A shore crab whose carapace is grown from drowned-house coral: a dome of lifted coral-stone plates with white
mortar seams, one red roof-tile plate, long legs, an oversized crusher on its right (the battle camera's side).
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

SEED = 4127
PAL = {k: ck.hexrgb(v) for k, v in {
    "coral_stone": "#E8DCC4", "coral_stone_weathered": "#B9AE98", "mortar_white": "#E6E1D6",
    "roof_clay": "#B5523A", "laterite": "#A8573A", "tortoiseshell": "#6B3A1E", "lacquer_black": "#1D1916",
    "sand_wet": "#B59D74", "spawn_wound": "#3FE0C8",
}.items()}

BODY_Y = 0.40  # carapace centre height
SHELL_R = (0.52, 0.21, 0.42)  # dome radii (x, y up, z forward)
SIDE_R = -1.0
LEG_Z = (0.19, 0.06, -0.08, -0.21)  # hip z of the four walking legs, front to back  # the crusher's side: its right, -x, faces the battle camera once the stage turns it to the party
# The walking legs' proportions, a variant's parameter (the root crab climbs on longer legs, M3-CRE-628): the knee's
# x, its height and its z as a factor of the hip's, then the foot's x and z factor (the foot is on the ground).
LEG_KNEE = (0.62, 0.47, 1.7)
LEG_FOOT = (0.80, 2.3)
PLASTRON_RINGS, PLASTRON_SEGS = 6, 36  # the underside's lathe (the dome's is 26 x 72)


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    rig.add("body", (0, BODY_Y, 0), (0, BODY_Y + 0.15, 0), "root")
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"eye_{tag}", (side * 0.11, 0.47, 0.33), (side * 0.13, 0.62, 0.37), "body")
        for i in range(4):
            z = LEG_Z[i]
            hip = (side * 0.36, 0.33, z)
            knee = (side * LEG_KNEE[0], LEG_KNEE[1], z * LEG_KNEE[2])
            rig.add(f"leg_{tag}{i}_a", hip, knee, "body")
            rig.add(f"leg_{tag}{i}_b", knee, (side * LEG_FOOT[0], 0.0, z * LEG_FOOT[1]), f"leg_{tag}{i}_a")
    for side, tag, s in ((SIDE_R, "crusher", 1.0), (-SIDE_R, "cutter", 0.6)):
        sh = (side * 0.26, 0.36, 0.30)
        wr = (side * (0.36 + 0.14 * s), 0.40, 0.50 + 0.04 * s)
        rig.add(f"{tag}_arm", sh, wr, "body")
        hx = side * (0.36 + 0.14 * s)
        rig.add(f"{tag}_hand", wr, (hx, 0.40, 0.54 + 0.50 * s), f"{tag}_arm")
        rig.add(f"{tag}_finger", (hx, 0.45 + 0.05 * s, 0.54 + 0.30 * s), (hx, 0.40, 0.54 + 0.56 * s), f"{tag}_hand")
    return rig


def _cells(n: int, rng: np.random.Generator) -> np.ndarray:
    """Plate centres on the dome, as unit directions (upper hemisphere)."""
    pts = []
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        y = 1.0 - (i + 0.5) / n * 0.95
        r = math.sqrt(max(1.0 - y * y, 0.0))
        a = golden * i + rng.uniform(-0.25, 0.25)
        pts.append((r * math.sin(a), y, r * math.cos(a)))
    return np.asarray(pts)


def shell(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    rings, segs = 26, 72
    prof = []
    for i in range(rings + 1):
        th = (math.pi / 2) * (i / rings) ** 0.85  # 0 at the crown, pi/2 at the rim; denser toward the rim
        prof.append((math.sin(th), math.cos(th)))
    P, T = ck.lathe(prof, segs)
    unit = P.copy()
    cells = _cells(16, rng)
    d = unit @ cells.T  # cosine to each plate centre
    order = np.argsort(-d, axis=1)
    first, second = order[:, 0], order[:, 1]
    gap = d[np.arange(len(d)), first] - d[np.arange(len(d)), second]  # 0 on a seam
    mortar = 1.0 - ck.smoothstep(0.004, 0.016, gap)  # the thin white line
    bevel = ck.smoothstep(0.0, 0.07, gap)  # plates bevel down into the seam
    lift = rng.uniform(0.012, 0.03, len(cells))
    tile_cell = int(np.argmin(np.linalg.norm(cells - np.array([0.30, 0.80, -0.30]), axis=1)))
    lift[tile_cell] = 0.05
    is_tile = first == tile_cell
    polar = np.arccos(np.clip(unit[:, 1], -1, 1)) / (math.pi / 2)  # 0 crown .. 1 rim
    azim = np.arctan2(unit[:, 0], unit[:, 2])
    # the front edge carries low blunt teeth (a crab's anterolateral margin)
    front = ck.smoothstep(0.2, 0.9, np.cos(azim)) * ck.smoothstep(0.75, 1.0, polar)
    teeth = front * 0.025 * np.maximum(np.cos(azim * 9.0), 0.0)
    c = cells[first]
    proj = unit * (0.96 / np.maximum((unit * c).sum(axis=1), 0.5))[:, None]
    flat_w = 0.92 * bevel
    unit_f = unit * (1.0 - flat_w)[:, None] + proj * flat_w[:, None]
    P = unit_f * np.asarray(SHELL_R)
    P[:, 2] += 0.04 * unit[:, 2] * (unit[:, 2] > 0)  # a broader front
    n_out = unit / np.asarray(SHELL_R)
    n_out /= np.linalg.norm(n_out, axis=1, keepdims=True)
    rough = ck.fbm(P * 11.0, SEED + 1) * 0.008
    ridge = np.where(is_tile, 0.01 * np.cos(P[:, 0] * 60.0), 0.0)
    disp = lift[first] * bevel + rough + ridge - 0.008 * (1.0 - bevel) + teeth
    P = P + n_out * disp[:, None]
    P[:, 1] += BODY_Y
    tone = rng.uniform(0.72, 0.96, len(cells))[first]
    warm = rng.uniform(0.0, 1.0, len(cells))[first]
    plate = ck.mix(PAL["coral_stone_weathered"], PAL["coral_stone"], (0.25 * warm)[:, None]) * tone[:, None]
    plate = plate * (1.0 + 0.08 * ck.fbm(P * 6.0, SEED + 2)[:, None])
    groove = (1.0 - bevel) * (1.0 - mortar)
    plate = plate * (1.0 - 0.45 * groove)[:, None]
    stain = ck.smoothstep(0.05, 0.35, ck.fbm(P * 4.0, SEED + 5))
    plate = ck.mix(plate, PAL["laterite"] * 0.9, (0.35 * stain)[:, None])
    plate = ck.mix(plate, PAL["sand_wet"] * 0.7, (0.6 * ck.smoothstep(0.75, 1.0, polar))[:, None])
    tile = PAL["roof_clay"] * (0.9 + 0.12 * np.cos(P[:, 0] * 60.0))[:, None]
    col = np.where(is_tile[:, None], tile, plate)
    col = ck.mix(col, PAL["mortar_white"], mortar[:, None])
    wet = ck.smoothstep(0.7, 1.0, polar)
    # the weak point: a crack across the back plate where the shell meets the abdomen, one small closed mark (ADR
    # 0151) low on the back. M3-CRE-631: centred on the back rim's band, so its mask peaks at 1 and reads 0.6..1 on
    # the crack (it was centred higher, where the rim term cut it to 0.16); it stays clear of the rim
    back = np.exp(-((unit[:, 0] / 0.2) ** 2) - ((unit[:, 2] + 0.92) / 0.06) ** 2)
    crack = ck.smoothstep(0.3, 0.75, back) * (0.8 + 0.2 * np.abs(np.cos(unit[:, 0] * 40.0)))
    col = ck.mix(col, PAL["spawn_wound"] * 0.5, (crack * 0.8)[:, None])
    # each plate shades as a flat slab (its own normal); only the bevels into the seams stay smooth
    smooth = ck.weld_normals(P, ck.vertex_normals(P, T))
    plate_n = cells[first] / np.asarray(SHELL_R)
    plate_n /= np.linalg.norm(plate_n, axis=1, keepdims=True)
    k = ck.smoothstep(0.02, 0.08, gap)[:, None]
    N = plate_n * k + smooth * (1.0 - k)
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    ck.finish(mesh, P, T, "shell", col, rig.rigid("body"), wet=wet * 0.6, cavity=groove * 0.9 + crack * 0.3,
              emission=crack, N=N)

    # underside: a shallow wet plastron (M3-CRE-631: coarser than the dome, since only its edge is ever seen, which
    # keeps the crab in its 8k budget)
    prof = [(0.0, -1.0)]
    for i in range(1, PLASTRON_RINGS + 1):
        th = (math.pi / 2) * i / PLASTRON_RINGS
        prof.append((math.sin(th), -math.cos(th)))
    Pu, Tu = ck.lathe(prof, PLASTRON_SEGS)
    Pu = Pu * np.array([0.47, 0.11, 0.37]) + np.array([0.0, BODY_Y - 0.035, 0.0])
    cu = ck.mix(PAL["sand_wet"], PAL["laterite"], 0.5 + 0.5 * ck.fbm(Pu * 7.0, SEED + 3)[:, None])
    ck.finish(mesh, Pu, ck.flip(Tu), "chitin", cu * 1.1, rig.rigid("body"), wet=0.9, cavity=0.3)

    # mouthparts: a few overlapping plates at the front
    for k, (x, y) in enumerate(((0.0, 0.40), (-0.06, 0.37), (0.06, 0.37), (0.0, 0.34))):
        Pm, Tm = ck.ellipsoid((x, y, 0.37), (0.05, 0.035, 0.03), 5, 8)
        ck.finish(mesh, Pm, Tm, "chitin", ck.mix(PAL["laterite"], PAL["tortoiseshell"], 0.5), rig.rigid("body"),
                  wet=0.8, cavity=0.5)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        b = rig.bones[rig.index(f"eye_{tag}")]
        path = ck.bezier([b.head, (side * 0.12, 0.54, 0.35), b.tail], 6)
        P, T = ck.tube(path, np.linspace(0.022, 0.015, 6), 8, cap_start=False, cap_end=False)
        ck.finish(mesh, P, T, "chitin", PAL["laterite"], rig.rigid(f"eye_{tag}"), wet=0.4, cavity=0.2)
        Pe, Te = ck.ellipsoid(b.tail, (0.034, 0.03, 0.034), 6, 10)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid(f"eye_{tag}"), wet=1.0)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(4):
            a = rig.bones[rig.index(f"leg_{tag}{i}_a")]
            b = rig.bones[rig.index(f"leg_{tag}{i}_b")]
            for seg, (p0, p1, r0, r1) in (("a", (a.head, a.tail, 0.058, 0.045)), ("b", (b.head, b.tail, 0.043, 0.010))):
                p0, p1 = np.asarray(p0), np.asarray(p1)
                out = np.array([math.copysign(0.05, p1[0]), 0.0, 0.0])
                mid = (p0 + p1) / 2 + (np.array([0.0, 0.04, 0.0]) if seg == "a" else out)
                path = ck.bezier([p0, mid, p1], 7)
                rad = np.linspace(r0, r1, 7) * (1.0 + 0.25 * np.sin(np.linspace(0, math.pi, 7)))
                P, T = ck.tube(path, rad, 8, squash=0.75)
                t = (P[:, 1] - 0.0) / 0.45
                col = ck.mix(PAL["tortoiseshell"], PAL["laterite"], np.clip(t, 0, 1)[:, None])
                wet = 1.0 - ck.smoothstep(0.05, 0.25, P[:, 1])
                band = ck.smoothstep(0.9, 1.0, np.abs(np.sin(np.linalg.norm(P - p0, axis=1) * 22.0)))
                ck.finish(mesh, P, T, "chitin", col * (1.0 - 0.15 * band[:, None]), rig.rigid(f"leg_{tag}{i}_{seg}"),
                          wet=wet, cavity=band * 0.5)


def claws(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    for tag, s in (("crusher", 1.0), ("cutter", 0.6)):
        arm = rig.bones[rig.index(f"{tag}_arm")]
        hand = rig.bones[rig.index(f"{tag}_hand")]
        fin = rig.bones[rig.index(f"{tag}_finger")]
        side = math.copysign(1.0, arm.head[0])
        h0, h1 = np.asarray(hand.head), np.asarray(hand.tail)
        path = ck.bezier([arm.head, (side * 0.36, 0.44, 0.40), arm.tail], 7)
        P, T = ck.tube(path, np.linspace(0.05, 0.045, 7) * (0.6 + 0.4 * s), 10, squash=0.8)
        ck.finish(mesh, P, T, "chitin", PAL["laterite"], rig.rigid(f"{tag}_arm"), wet=0.3, cavity=0.2)
        # the palm (propodus): a deep, laterally flattened block, darker below
        palm_len = 0.32 * s + 0.03
        path = ck.bezier([h0, h0 + (h1 - h0) * 0.3, h0 + np.array([0, 0, palm_len])], 8)
        rad = (0.03 + 0.12 * s) * np.sin(np.linspace(0.35, math.pi - 0.5, 8)) ** 0.6
        Pp, Tp = ck.tube(path, rad, 14, squash=0.62, up_hint=(1.0, 0.0, 0.0))
        shade = ck.smoothstep(-0.05, 0.08, Pp[:, 1] - h0[1])
        cp = ck.mix(PAL["tortoiseshell"], PAL["laterite"], shade[:, None])
        ck.finish(mesh, Pp, Tp, "chitin", cp, rig.rigid(f"{tag}_hand"), wet=0.2, cavity=(1 - shade) * 0.3)
        # the fixed finger (pollex), from the palm's lower front: on the crusher a slab of the coral-stone
        base = h0 + np.array([0.0, -0.05 * s, palm_len - 0.03])
        tip = np.asarray(fin.tail) + np.array([0.0, -0.06 * s, 0.0])
        path = ck.bezier([base, base + np.array([0, -0.01, 0.10 * s]), tip + np.array([0, -0.02, -0.04]), tip], 8)
        Pf, Tf = ck.tube(path, np.linspace(0.07, 0.012, 8) * s + 0.008, 8, squash=0.55, up_hint=(1.0, 0.0, 0.0))
        stone = tag == "crusher"
        cf = PAL["coral_stone_weathered"] * 0.92 if stone else PAL["tortoiseshell"]
        ck.finish(mesh, Pf, Tf, "shell" if stone else "chitin", cf, rig.rigid(f"{tag}_hand"), wet=0.2,
                  cavity=0.25, flat=stone)
        # the movable finger (dactyl), curving down to meet it
        f0, f1 = np.asarray(fin.head), np.asarray(fin.tail)
        path = ck.bezier([f0, f0 + np.array([0, 0.04 * s, 0.10 * s]), f1 + np.array([0, 0.02, -0.03]), f1], 8)
        Pd, Td = ck.tube(path, np.linspace(0.06, 0.01, 8) * s + 0.007, 8, squash=0.55, up_hint=(1.0, 0.0, 0.0))
        tipdark = ck.smoothstep(0.5, 1.0, np.linalg.norm(Pd - f0, axis=1) / max(np.linalg.norm(f1 - f0), 1e-6))
        cd = ck.mix(PAL["laterite"], PAL["lacquer_black"], (0.2 + 0.6 * tipdark)[:, None])
        ck.finish(mesh, Pd, Td, "chitin", cd, rig.rigid(f"{tag}_finger"), wet=0.3, cavity=0.2)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    rng = np.random.default_rng(SEED)
    mesh = ck.Mesh("reef_crab")
    shell(mesh, rig, rng)
    eyes(mesh, rig)
    legs(mesh, rig)
    claws(mesh, rig, rng)
    return mesh


LEG_TAGS = [f"{t}{i}" for t in "lr" for i in range(4)]
# The KO (M3-CRE-631): the body's (time, drop, roll) keys, and each walking leg's hip and knee turns (degrees, the
# left side's sign; mid-fall, then the end) that fold it in beside the settled body.
KO_BODY = ((0.0, 0.0, 0.0), (0.35, 0.08, 1.0), (0.7, 0.15, 2.0), (1.0, 0.21, 2.8), (1.4, 0.22, 3.0))
KO_LEG_A = (18.0, 45.0)
KO_LEG_B = (-12.0, -28.0)
# The limbs kept on the floor: (bone, rest axis, the side's sign, the most it may turn). A walking leg turns up
# about z at its hip (its tip rises), a claw up about x at the shoulder.
GROUNDED_LIMBS = [(f"leg_{leg}_a", 2, 1.0 if leg[0] == "l" else -1.0, 75.0) for leg in LEG_TAGS] + [
    ("crusher_arm", 0, -1.0, 60.0), ("cutter_arm", 0, -1.0, 60.0)]


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 2.4, loop=True)
    idle.wave("body", amp_loc=(0.0, 0.012, 0.0), amp_rot=(1.2, 0.0, 0.8), cycles=2)
    idle.wave("eye_l", amp_rot=(0.0, 12.0, 0.0), cycles=1)
    idle.wave("eye_r", amp_rot=(0.0, 10.0, 0.0), cycles=1, phase=1.3)
    idle.wave("crusher_finger", amp_rot=(-9.0, 0.0, 0.0), base_rot=(-9.0, 0.0, 0.0), cycles=1, phase=-math.pi / 2)
    idle.wave("cutter_finger", amp_rot=(-6.0, 0.0, 0.0), base_rot=(-6.0, 0.0, 0.0), cycles=2, phase=-math.pi / 2)
    idle.wave("crusher_arm", amp_rot=(-3.0, 2.0, 0.0), cycles=1)
    # a one-leg shuffle: the left second leg lifts and sets down (a left leg rises with +z; M3-CRE-631: it was keyed
    # -14, which pushed it into the floor)
    for t, r in ((0.0, 0.0), (0.9, 0.0), (1.15, 14.0), (1.4, 0.0), (2.4, 0.0)):
        idle.key("leg_l1_a", t, (0.0, 0.0, r))
    for leg in LEG_TAGS:
        idle.wave(f"leg_{leg}_a", amp_rot=(0.0, 0.0, 1.5 if leg[0] == "l" else -1.5), cycles=2)

    attack = ck.Clip("attack", 1.2)
    for t, body, root, arm, fin in (
        (0.0, (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)),
        (0.35, (-12, 0, 0), (0, 0.03, -0.05), (-55, -10, 0), (-35, 0, 0)),
        (0.5, (8, 0, 0), (0, 0, 0.28), (18, 0, 0), (6, 0, 0)),
        (0.7, (4, 0, 0), (0, 0, 0.22), (10, 0, 0), (4, 0, 0)),
        (1.2, (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)),
    ):
        attack.key("body", t, body)
        attack.key("root", t, loc=root)
        attack.key("crusher_arm", t, arm)
        attack.key("crusher_finger", t, fin)
    for leg in LEG_TAGS:
        for t, r in ((0.0, 0), (0.25, 12), (0.42, -10), (0.6, 8), (1.2, 0)):
            attack.key(f"leg_{leg}_a", t, (0, 0, r if leg[1] in "02" else -r))

    cast = ck.Clip("cast", 1.3)
    for t, body, loc, front in (
        (0.0, (0, 0, 0), (0, 0, 0), 0),
        (0.45, (-25, 0, 0), (0, 0.09, -0.06), 1),
        (0.7, (-6, 0, 0), (0, 0.03, 0.10), 0.3),
        (1.3, (0, 0, 0), (0, 0, 0), 0),
    ):
        cast.key("body", t, body, loc)
        cast.key("crusher_arm", t, (-20 * front, 0, 0))
        cast.key("cutter_arm", t, (-25 * front, 0, 0))
        for tag in ("l0", "r0", "l1", "r1"):
            cast.key(f"leg_{tag}_a", t, (0, 0, (18 if tag[0] == "l" else -18) * front))
        cast.key("crusher_finger", t, (-30 * front, 0, 0))

    hit = ck.Clip("hit", 0.5)
    for t, loc, pull in ((0.0, (0, 0, 0), 0), (0.1, (0, -0.05, -0.03), 1), (0.5, (0, 0, 0), 0)):
        hit.key("body", t, (6 * pull, 0, 0), loc)
        hit.key("crusher_arm", t, (10 * pull, -18 * pull * SIDE_R, 0))
        hit.key("cutter_arm", t, (10 * pull, 18 * pull * SIDE_R, 0))
        hit.key("eye_l", t, (25 * pull, 0, 0))
        hit.key("eye_r", t, (25 * pull, 0, 0))

    # M3-CRE-631: it settles onto its plastron and the legs fold in beside the body, knees up and the tips drawn in
    # under them, so nothing goes under the floor (it used to sink its legs 0.3 m through it)
    ko = ck.Clip("ko", 1.4)
    for t, drop, roll in KO_BODY:
        ko.key("body", t, (3.0 * drop / KO_BODY[-1][1], 0, roll), (0, -drop, 0))
    for leg in LEG_TAGS:
        s = 1.0 if leg[0] == "l" else -1.0
        delay = 0.15 * int(leg[1])
        ko.key(f"leg_{leg}_a", 0.0, (0, 0, 0))
        ko.key(f"leg_{leg}_a", 0.4 + delay, (0, 0, KO_LEG_A[0] * s))
        ko.key(f"leg_{leg}_a", 1.4, (0, 0, KO_LEG_A[1] * s))
        ko.key(f"leg_{leg}_b", 0.0, (0, 0, 0))
        ko.key(f"leg_{leg}_b", 0.6 + delay, (0, 0, KO_LEG_B[0] * s))
        ko.key(f"leg_{leg}_b", 1.4, (0, 0, KO_LEG_B[1] * s))
    for tag in ("crusher", "cutter"):
        ko.key(f"{tag}_arm", 0.0, (0, 0, 0))
        ko.key(f"{tag}_arm", 1.0, (14, 0, 0))
        ko.key(f"{tag}_arm", 1.4, (16, 0, 0))
    ko.key("eye_l", 0.0)
    ko.key("eye_l", 1.2, (60, 0, 0))
    ko.key("eye_r", 0.0)
    ko.key("eye_r", 1.2, (60, 0, 0))
    return [idle, attack, cast, hit, ko]


# The planted feet held where they touch down (common/grounding.py pinned(); the Act I audit's foot sliding).
PINNED_LEGS = [(f"leg_{leg}_a", f"leg_{leg}_b", 2, 1.0 if leg[0] == "l" else -1.0) for leg in LEG_TAGS]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    """The clips kept off the floor (M3-CRE-631, common/grounding.py): a planted foot stays on the ground while the
    body bobs or leans over it (each walking leg turns up about its hip), and the claws ride up over the floor."""
    pinned = gr.pinned(rig, mesh, gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS), PINNED_LEGS)
    return gr.reground(rig, mesh, pinned, GROUNDED_LIMBS)  # a held foot's toes back above the floor


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "reef_crab"})
    print(f"reef_crab: {info}")


if __name__ == "__main__":
    main()
