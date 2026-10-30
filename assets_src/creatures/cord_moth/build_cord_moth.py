"""Cord moth, Ch12 Keth Pass along the pass-cords (M3-CRE-628): docs/kb/art/creatures/act2/cord_moth.md.

blender --background --factory-startup --python assets_src/creatures/cord_moth/build_cord_moth.py -- \
    --out assets/creatures/cord_moth/cord_moth.glb

A pale moth whose larvae live in the old keth cords on the pass-cords and eat the knots, and whose wings carry the
knot patterns they ate, as real moths carry what they fed on. Its one exaggeration: the wings carry readable knots.
A broad-winged moth, 1.4 m across, hovering at chest height with its wings held flat and wide: a furred slate body,
feathered antennae, black eyes, and across both wings rows of knotted cord like stitched lines, in the cords' own
faded dyes (lacquer_red and sea_blue_cloth). The knot rows are an original, abstract pattern: each row is a cord laid
across the wing with its knots in counted groups (a single knot, a long knot, clusters of two to four), the groups
drawn from a seeded sequence, not copied from any real script. Its weak point is a small spawn_wound crack on the
thorax.

Its origin is the hover point (the stand-in's `hover` lifts it), so its KO drifts down by exactly that height. In battle
the model is scaled 1.35x (cord_moth_battle.tscn), like the ashwing, whose flat wings read as slivers at normal size
(the Act II plan sheet): its KO falls HOVER in model space, 1.12 m in battle, the stand-in's `hover`.

Run without Blender (`python3 build_cord_moth.py --report`) for the triangle count and each clip's numbers.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 8237
PAL = {k: ck.hexrgb(v) for k, v in {
    "cumulus_lit": "#FFF8EE", "sand_cloth": "#C9B48E", "lacquer_red": "#B3261E", "sea_blue_cloth": "#3C78A8",
    "overcast_slate": "#6F7E8E", "lacquer_black": "#1D1916", "spawn_wound": "#3FE0C8",
}.items()}
WING_PALE = PAL["cumulus_lit"] * 0.9  # cumulus_lit held under the albedo ceiling
WING_ROOT = PAL["sand_cloth"]
FRINGE = ck.mix(PAL["overcast_slate"], PAL["lacquer_black"], 0.25)  # the wings' dusky margin
FRINGE_FROM = (0.84, 0.72)  # where the margin starts toward the tip (u) and the trailing edge (v)
FRINGE_DARK = 0.85
DYES = (ck.mix(PAL["lacquer_red"], PAL["sand_cloth"], 0.3), ck.mix(PAL["sea_blue_cloth"], PAL["sand_cloth"], 0.25))
BLACK = PAL["lacquer_black"]

HOVER = 0.83  # the KO comes down by this (model space); at the battle scale of 1.35 it is the stand-in's 1.12 m hover
# (lowered from 1.35 m so the battle camera sees the wings from above; hit_b's dip still clears the floor)
THORAX = np.array([0.0, 0.056, 0.03])
THORAX_R = (0.05, 0.048, 0.07)
HEAD = np.array([0.0, 0.061, 0.125])
DIHEDRAL = 0.1  # the wings rise this much per metre out
# Wing outlines on the left (+x): (u along the span, (x, z)) for the leading and the trailing edge
FORE_LEAD = ((0.0, (0.035, 0.085)), (0.35, (0.27, 0.13)), (0.75, (0.56, 0.14)), (1.0, (0.7, 0.1)))
FORE_TRAIL = ((0.0, (0.035, -0.01)), (0.35, (0.22, -0.11)), (0.75, (0.47, -0.17)), (1.0, (0.69, 0.06)))
HIND_LEAD = ((0.0, (0.03, -0.0)), (0.4, (0.2, -0.08)), (0.8, (0.38, -0.14)), (1.0, (0.44, -0.2)))
HIND_TRAIL = ((0.0, (0.03, -0.07)), (0.4, (0.12, -0.3)), (0.8, (0.3, -0.36)), (1.0, (0.43, -0.25)))
WING_NU, WING_NV = 16, 8
WING_T = 0.004  # the membrane's half-thickness
# The knot rows: (wing, v across the chord, dye) and the knot sequence's grammar
ROWS = (("fore", 0.3, 0), ("fore", 0.55, 1), ("fore", 0.8, 0), ("hind", 0.35, 1), ("hind", 0.7, 0))
ROW_N = 30  # vertices along a row
CORD_W, KNOT_W = 0.005, 0.012  # the cord's half-width and a knot's


def outline(edge, u: np.ndarray) -> np.ndarray:
    us = np.array([e[0] for e in edge])
    xs = np.array([e[1][0] for e in edge])
    zs = np.array([e[1][1] for e in edge])
    return np.column_stack([np.interp(u, us, xs), np.interp(u, us, zs)])


def wing_point(wing: str, u: np.ndarray, v: np.ndarray, side: float) -> np.ndarray:
    """A point on a wing (u along the span, v across the chord) in the moth's space, on the side `side`."""
    lead, trail = (FORE_LEAD, FORE_TRAIL) if wing == "fore" else (HIND_LEAD, HIND_TRAIL)
    a, b = outline(lead, u), outline(trail, u)
    xz = a * (1.0 - v)[:, None] + b * v[:, None]
    x = xz[:, 0]
    y = THORAX[1] + 0.02 + DIHEDRAL * x + 0.012 * np.sin(np.pi * v) * (1.0 - u)  # a slight camber near the root
    return np.column_stack([side * x, y, xz[:, 1]])


def wing_bones(wing: str, side: float) -> np.ndarray:
    """The span line of a wing: root, middle, tip (each wing has two bones on it)."""
    u = np.array([0.0, 0.5, 1.0])
    return wing_point(wing, u, np.full(3, 0.35), side)


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    rig.add("body", THORAX - np.array([0.0, 0.0, 0.12]), THORAX + np.array([0.0, 0.0, 0.1]), "root")
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        for wing in ("fore", "hind"):
            p = wing_bones(wing, side)
            rig.add(f"{wing}_{tag}0", p[0], p[1], "body")
            rig.add(f"{wing}_{tag}1", p[1], p[2], f"{wing}_{tag}0")
        rig.add(f"antenna_{tag}", HEAD + np.array([side * 0.015, 0.02, 0.02]), HEAD + np.array([side * 0.09, 0.1, 0.19]),
                "body")
    return rig


def wing_skin(rig: ck.Rig, wing: str, side: float, tag: str):
    return rig.chain([f"{wing}_{tag}0", f"{wing}_{tag}1"], wing_bones(wing, side))


# ---------------------------------------------------------------------------------------------
# Wings and their knot rows
# ---------------------------------------------------------------------------------------------
def wings(mesh: ck.Mesh, rig: ck.Rig) -> None:
    u = np.linspace(0.0, 1.0, WING_NU) ** 0.9
    v = np.linspace(0.0, 1.0, WING_NV)
    U, V = (x.ravel() for x in np.meshgrid(u, v, indexing="ij"))
    T = ck.grid_tris(WING_NU, WING_NV, False)
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        for wing in ("fore", "hind"):
            P = wing_point(wing, U, V, side)
            skin = wing_skin(rig, wing, side, tag)
            n = ck.fbm(P * np.array([14.0, 14.0, 30.0]), SEED + (1 if wing == "fore" else 2))
            col = ck.mix(WING_ROOT, WING_PALE, ck.smoothstep(0.05, 0.5, U)[:, None])
            col = col * (0.94 + 0.06 * n)[:, None]
            fringe = ck.smoothstep(FRINGE_FROM[1], 1.0, V) + ck.smoothstep(FRINGE_FROM[0], 1.0, U)
            # a dusky slate margin round each wing, so its outline holds against pale stone and sky (the Act II plan
            # sheet: pale on Keth's white walls it read as a sliver)
            col = ck.mix(col, FRINGE, np.clip(fringe, 0.0, 1.0)[:, None] * FRINGE_DARK)
            col = np.minimum(col, WING_PALE)
            for top in (True, False):
                Pt = P + np.array([0.0, WING_T if top else -WING_T, 0.0])
                Tt = T
                fn = np.cross(Pt[Tt[:, 1]] - Pt[Tt[:, 0]], Pt[Tt[:, 2]] - Pt[Tt[:, 0]])
                if (float(fn[:, 1].sum()) < 0) == top:
                    Tt = ck.flip(Tt)
                ck.finish(mesh, Pt, Tt, "wing", col if top else col * 0.92, skin, cavity=0.1 * fringe)
            # the wing's leading vein, a fine dark rib
            lead = wing_point(wing, np.linspace(0.0, 1.0, 10), np.full(10, 0.02), side) + np.array([0.0, WING_T, 0.0])
            Pv, Tv = ck.tube(lead, np.linspace(0.006, 0.002, 10), 4)
            ck.finish(mesh, Pv, Tv, "wing", ck.mix(WING_ROOT, PAL["overcast_slate"], 0.4), skin, cavity=0.2)


def knot_sequence(rng: np.random.Generator) -> np.ndarray:
    """A row's knot profile along its length (0 cord .. 1 a knot's full width): groups of one to four knots, now and
    then a long knot, with gaps between groups. Seeded and abstract."""
    prof = np.zeros(ROW_N)
    k = int(rng.integers(1, 4))
    while k < ROW_N - 2:
        group = int(rng.integers(1, 5))
        if rng.uniform() < 0.25:  # a long knot: one wide stretch
            span = min(3, ROW_N - 2 - k)
            prof[k:k + span] = 1.0
            k += span + int(rng.integers(2, 4))
            continue
        for _ in range(group):
            if k >= ROW_N - 2:
                break
            prof[k] = 1.0
            k += 2
        k += int(rng.integers(2, 4))
    return prof


def knot_rows(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED)
    profiles = [knot_sequence(rng) for _ in ROWS]
    u = np.linspace(0.1, 0.96, ROW_N)
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        for (wing, v0, dye), prof in zip(ROWS, profiles):
            # the cord follows the wing's chord line at v0, bowing a little like a stitched line
            v = np.full(ROW_N, v0) + 0.03 * np.sin(u * 5.0 + v0 * 7.0)
            line = wing_point(wing, u, v, side) + np.array([0.0, WING_T + 0.0015, 0.0])
            tan = np.gradient(line, axis=0)
            tan /= np.linalg.norm(tan, axis=1, keepdims=True)
            up = np.array([0.0, 1.0, 0.0])
            across = np.cross(up, tan)
            across /= np.linalg.norm(across, axis=1, keepdims=True)
            w = CORD_W + (KNOT_W - CORD_W) * prof
            lift = 0.0015 + 0.003 * prof  # the knots stand a little proud of the cord
            rows = [line - across * w[:, None], line + up * lift[:, None], line + across * w[:, None]]
            P = np.stack(rows, axis=1).reshape(-1, 3)
            T = ck.grid_tris(ROW_N, 3, False)
            fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
            if float(fn[:, 1].sum()) < 0:
                T = ck.flip(T)
            k = np.repeat(prof, 3)
            col = ck.mix(DYES[dye] * 0.82, DYES[dye], k[:, None])  # the knots keep their dye; the cord between is faded
            ck.finish(mesh, P, T, "knot", col, wing_skin(rig, wing, side, tag), cavity=0.3 * (1.0 - k))


# ---------------------------------------------------------------------------------------------
# Body, head, antennae
# ---------------------------------------------------------------------------------------------
def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    b = rig.rigid("body")
    P, T = ck.ellipsoid(THORAX, THORAX_R, 8, 12)
    fur = ck.smoothstep(-0.3, 0.6, ck.value_noise(P * 70.0, SEED + 10))
    P = P + ck.weld_normals(P, ck.vertex_normals(P, T)) * (0.006 * fur)[:, None]
    col = PAL["overcast_slate"] * (0.85 + 0.2 * fur)[:, None]
    ck.finish(mesh, P, T, "body", col, b, cavity=0.3 * (1.0 - fur))
    # the abdomen, banded, tapering back under the hindwings
    path = ck.bezier([THORAX + np.array([0.0, -0.005, -0.05]), THORAX + np.array([0.0, -0.01, -0.16]),
                      THORAX + np.array([0.0, -0.005, -0.28])], 10)
    Pa, Ta = ck.tube(path, np.interp(np.linspace(0, 1, 10), [0, 0.3, 1], [0.042, 0.04, 0.008]), 8)
    band = 0.5 + 0.5 * np.cos(Pa[:, 2] * 110.0)
    ca = ck.mix(PAL["overcast_slate"], ck.mix(PAL["overcast_slate"], WING_ROOT, 0.4), (0.5 * band)[:, None])
    ck.finish(mesh, Pa, Ta, "body", ca, b, cavity=0.3 * (1.0 - band))
    # the head and its big black eyes
    Ph, Th = ck.ellipsoid(HEAD, (0.032, 0.03, 0.028), 6, 10)
    ck.finish(mesh, Ph, Th, "body", PAL["overcast_slate"] * 0.9, b, cavity=0.2)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(HEAD + np.array([s * 0.026, 0.006, 0.012]), (0.017, 0.02, 0.018), 6, 8)
        ck.finish(mesh, Pe, Te, "eye", BLACK, b, wet=1.0)
    # the weak point: a small crack across the top of the thorax, glowing
    c = THORAX + np.array([0.0, THORAX_R[1] + 0.002, -0.005])
    Pw, Tw = ck.ellipsoid(c, (0.024, 0.006, 0.009), 5, 8)
    glow = ck.smoothstep(0.0, 0.006, Pw[:, 1] - c[1] + 0.002)
    ck.finish(mesh, Pw, Tw, "body", ck.mix(PAL["overcast_slate"] * 0.6, PAL["spawn_wound"] * 0.65, glow[:, None]), b,
              emission=glow)


def antennae(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        a = rig.bones[rig.index(f"antenna_{tag}")]
        h0, h1 = np.asarray(a.head), np.asarray(a.tail)
        path = ck.bezier([h0, h0 + np.array([side * 0.03, 0.07, 0.06]), h1], 8)
        P, T = ck.tube(path, np.linspace(0.004, 0.0015, 8), 4)
        ck.finish(mesh, P, T, "body", WING_ROOT * 0.8, rig.rigid(f"antenna_{tag}"))
        # the feathered vane: a flat comb either side of the shaft, widest in the middle
        wv = 0.013 * np.sin(np.linspace(0.15, math.pi - 0.15, 8))
        tan = np.gradient(path, axis=0)
        tan /= np.linalg.norm(tan, axis=1, keepdims=True)
        out = np.cross(tan, np.array([0.0, 1.0, 0.0]))
        out /= np.linalg.norm(out, axis=1, keepdims=True)
        rows = [path - out * wv[:, None], path, path + out * wv[:, None]]
        Pv = np.stack(rows, axis=1).reshape(-1, 3)
        Tv = ck.grid_tris(8, 3, False)
        for face in (Tv, ck.flip(Tv)):  # both faces, each on its own vertices
            ck.finish(mesh, Pv.copy(), face, "body", ck.mix(WING_ROOT, PAL["overcast_slate"], 0.3),
                      rig.rigid(f"antenna_{tag}"), cavity=0.2)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("cord_moth")
    wings(mesh, rig)
    knot_rows(mesh, rig)
    body(mesh, rig)
    antennae(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips (the wings beat about z: + lifts the left wing, - the right)
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 2.4
ATTACK_SEC = 1.1
ATTACK_CONTACT = 0.5
CAST_SEC = 1.6
HIT_SEC = 0.5
KO_SEC = 2.6


def key_wings(clip: ck.Clip, t: float, beat: float, tip: float = 0.0, sweep: float = 0.0, hind_lag: float = 0.0,
              hind_sweep: float = 0.0) -> None:
    """Both wings: `beat` degrees up (+) at the root, `tip` more at the outer bone, `sweep` degrees forward (+) for
    the forewings and `hind_sweep` for the hindwings (+ back), the hindwing beating `hind_lag` degrees behind."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        clip.key(f"fore_{tag}0", t, (0.0, -s * sweep, s * beat))
        clip.key(f"fore_{tag}1", t, (0.0, 0.0, s * tip))
        clip.key(f"hind_{tag}0", t, (0.0, s * hind_sweep, s * (beat - hind_lag)))
        clip.key(f"hind_{tag}1", t, (0.0, 0.0, s * tip * 0.8))


def build_idle() -> ck.Clip:
    """A slow hover: three quick beats, then a long glide with the wings held a little raised, the antennae swaying."""
    idle = ck.Clip("idle", IDLE_SEC, loop=True)
    for t, beat, tip in ((0.0, 8.0, 2.0), (0.15, 38.0, -10.0), (0.3, -24.0, 14.0), (0.45, 36.0, -10.0),
                         (0.6, -22.0, 12.0), (0.75, 34.0, -8.0), (0.9, -16.0, 10.0), (1.1, 10.0, 0.0), (1.7, 6.0, 3.0),
                         (2.1, 9.0, 1.0), (IDLE_SEC, 8.0, 2.0)):
        key_wings(idle, t, beat, tip, hind_lag=6.0 if 0.1 < t < 1.0 else 0.0)
    for t, y, rx in ((0.0, 0.0, 0.0), (0.45, 0.05, -4.0), (0.95, 0.06, -2.0), (1.7, 0.0, 2.0), (IDLE_SEC, 0.0, 0.0)):
        idle.key("root", t, (rx, 0.0, 0.0), (0.0, y, 0.0))
    idle.wave("antenna_l", amp_rot=(6.0, 4.0, 0.0), cycles=1)
    idle.wave("antenna_r", amp_rot=(6.0, -4.0, 0.0), cycles=1, phase=0.6)
    return idle


def build_attack() -> ck.Clip:
    """A dart and a wing-strike: the wings go up and back, it darts in and down, and the wings slam down and forward
    across the target at 0.5 s; then it beats back up."""
    attack = ck.Clip("attack", ATTACK_SEC)
    for t, beat, tip, sweep, root_y, rx in ((0.0, 8.0, 2.0, 0.0, 0.0, 0.0), (0.25, 58.0, -12.0, -12.0, 0.06, -18.0),
                                            (0.4, 30.0, 8.0, 0.0, -0.12, 10.0),
                                            (ATTACK_CONTACT, -42.0, 18.0, 22.0, -0.22, 16.0),
                                            (0.65, -30.0, 10.0, 12.0, -0.2, 8.0), (0.8, 30.0, -10.0, 0.0, -0.1, -4.0),
                                            (0.95, -10.0, 8.0, 0.0, -0.04, 0.0), (ATTACK_SEC, 8.0, 2.0, 0.0, 0.0, 0.0)):
        key_wings(attack, t, beat, tip, sweep, hind_lag=8.0 if 0.0 < t < ATTACK_SEC else 0.0)
        attack.key("root", t, (rx, 0.0, 0.0), (0.0, root_y, 0.3 * max(-root_y, 0.0)))
    for t, d in ((0.0, 0.0), (0.25, -18.0), (ATTACK_CONTACT, 14.0), (ATTACK_SEC, 0.0)):
        attack.key("antenna_l", t, (d, 0.0, 0.0))
        attack.key("antenna_r", t, (d, 0.0, 0.0))
    return attack


def build_cast() -> ck.Clip:
    """The unravel: it rises and tips its body up toward the party, opens its wings full (the forewings forward, the
    hindwings back, flat and wide) and holds them so the knot rows catch the light, then closes and settles."""
    cast = ck.Clip("cast", CAST_SEC)
    for t, s, beat in ((0.0, 0.0, 8.0), (0.3, 0.6, 20.0), (0.55, 1.0, 0.0), (1.15, 1.0, 0.0), (1.4, 0.4, 14.0),
                       (CAST_SEC, 0.0, 8.0)):
        key_wings(cast, t, beat, 0.0, sweep=14.0 * s, hind_sweep=12.0 * s)
        cast.key("root", t, (-38.0 * s, 0.0, 0.0), (0.0, 0.1 * s, 0.0))
    for t, d in ((0.0, 0.0), (0.55, -22.0), (1.15, -22.0), (CAST_SEC, 0.0)):
        cast.key("antenna_l", t, (d, 10.0 * d / -22.0, 0.0))
        cast.key("antenna_r", t, (d, -10.0 * d / -22.0, 0.0))
    return cast


def build_hit() -> ck.Clip:
    """It tumbles in the air, peaking at 0.1 s: rolled and pitched over, dropped, one wing flung up and the other
    down; it rights itself."""
    hit = ck.Clip("hit", HIT_SEC)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.25, 0.45), (HIT_SEC, 0.0)):
        hit.key("root", t, (22.0 * s, 0.0, 38.0 * s), (0.04 * s, -0.12 * s, -0.06 * s))
        hit.key("fore_l0", t, (0.0, 0.0, 40.0 * s))
        hit.key("fore_r0", t, (0.0, 0.0, 30.0 * s))
        hit.key("fore_l1", t, (0.0, 0.0, -20.0 * s))
        hit.key("fore_r1", t, (0.0, 0.0, 18.0 * s))
        hit.key("hind_l0", t, (0.0, 0.0, 30.0 * s))
        hit.key("hind_r0", t, (0.0, 0.0, 22.0 * s))
    return hit


KO_DROOP = -10.0  # the wings at the end, lying on the floor (the tips down to it)


def build_ko() -> ck.Clip:
    """It drifts down like a dropped scarf: falling the hover height in a slow swing from side to side, rolling and
    righting with each swing, the wings rippling and going slack, and it lies flat on the floor, wings out."""
    ko = ck.Clip("ko", KO_SEC)
    times = [k * KO_SEC / 26 for k in range(27)]
    for k, t in enumerate(times):
        e = t / KO_SEC
        fall = float(ck.smoothstep(0.0, 1.0, e)) ** 1.15
        swing = math.sin(e * 3.0 * math.pi) * (1.0 - e)
        root_y = -HOVER * fall
        ko.key("root", t, (8.0 * swing, 0.0, 28.0 * swing), (0.16 * swing, root_y, 0.12 * e))
        slack = float(ck.smoothstep(0.0, 0.9, e))
        ripple = math.sin(e * 9.0 * math.pi) * (1.0 - slack) * 22.0
        beat = (8.0 * (1.0 - slack) + KO_DROOP * slack) + ripple
        tip = -ripple * 0.8 * (1.0 - slack) + 2.0 * slack
        key_wings(ko, t, beat, tip)
        ko.key("antenna_l", t, (24.0 * slack, 0.0, -10.0 * slack))
        ko.key("antenna_r", t, (24.0 * slack, 0.0, 10.0 * slack))
    return ko


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def fk(rig: ck.Rig, clip: ck.Clip, t: float) -> dict:
    """Each bone's pose as (R, offset) in rest space: p -> R p + offset (the export's convention)."""
    out: dict = {}
    for b in rig.bones:
        rdeg, loc = clip.sample(b.name, t)
        if b.name == "root" and clip.name in ck.IN_PLACE_CLIPS:
            loc = np.array([0.0, loc[1], 0.0])
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
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)} (y 0 is the hover "
          f"point, {HOVER} m up)")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, disp = np.inf, -np.inf, []
        for f in range(frames + 1):
            P = skin(rig, arrays, fk(rig, c, min(f / ck.FPS, c.length)))
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        P = skin(rig, arrays, fk(rig, c, c.length))
        print(f"{c.name:7s} {c.length:.2f}s: y {lo:+.3f}..{hi:.3f}; at the end y {P[:, 1].min():+.3f}..{P[:, 1].max():.3f}"
              f" (over the floor: {P[:, 1].min() + HOVER:+.3f}); peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "cord_moth"})
    print(f"cord_moth: {info}")


if __name__ == "__main__":
    main()
