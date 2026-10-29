"""Vein sparker, Ch5 the copper veins (M3-CRE-04): docs/kb/art/creatures/act1/vein_sparker.md.

blender --background --factory-startup --python assets_src/creatures/vein_sparker/build_vein_sparker.py -- \
    --out assets/creatures/vein_sparker/vein_sparker.glb

A lean terrace lizard that lives in the exposed copper veins and stores their charge (m2-slice's act1_ch05 §9): copper
-green scales, a ridge of copper spines with charged tips, and its tail held up behind it in a tight coil that brightens
as it charges. It spits the charge as lightning; water grounds it. The charge glows `starlight`, never a glimmer hue.
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

SEED = 5207
PAL = {k: ck.hexrgb(v) for k, v in {
    "bronze_patina": "#5F8A78", "hair_copper": "#A65A2A", "starlight": "#DCE6FF", "lacquer_black": "#1D1916",
    "sand_dry": "#EFDDB4", "foliage_shadow": "#1E4A3A", "spawn_wound": "#3FE0C8",
}.items()}

NS = 4  # spine bones, head end first
NT = 7  # tail bones
COIL_AXIS = (0.5, -0.68)  # the coil's centre (y, z): it winds round an axis along x above the rump
# The stored charge (M3-CRE-650): starlight is a point-source swatch (palette.json: point sources only, <=0.5% of the
# frame), so the charge glows only in points: the ridge spines' tips and a few sparks on the coil's outer face. The
# coil's last third is bare copper (it glowed starlight over its whole surface before, against that rule).
COIL_CHARGE = (0.5, 1.0)  # where along the tail (0 hips .. 1 tip) the copper shows through, fading in
COIL_SPARKS = np.linspace(0.66, 0.94, 4)  # the sparks along the tail, on the coil's flanks
COIL_SPARK_R = 0.008  # each spark's radius (m)
# The weak point (ADR 0151, M3-CRE-650): one small closed mark, an old break in the tail's root, healed over, where
# the tail lifts off the rump to climb into the coil: the one place its stored charge leaks to ground. It lies on top
# of the root, clear of the ridge spines, a little to its near side (its right, -x: the battle camera's side once the
# stage turns it to the party), where it faces up and forward to the battle camera and the review three-quarter (+x
# front) alike. In the scale slot, whose emission is now this mark alone.
BREAK_AT = np.array([-0.03, 0.34, -0.44])  # projected onto the tail's surface
BREAK_ALONG = np.array([1.0, 0.0, 0.25])  # it rings part way round the tail, a little aslant
BREAK_HALF = (0.034, 0.011)  # the glowing seam's half length and half width (m)
BREAK_LIP = (1.25, 1.9, 0.008)  # the dark healed ridge round it: x the seam's length, x its width, raised (m)
BREAK_BEND_R = 0.07  # the tail's curvature round the root (m): the mark bends to lie on it


def spine(n: int) -> np.ndarray:
    return ck.bezier([(0, 0.2, 0.42), (0, 0.17, 0.2), (0, 0.16, -0.05), (0, 0.15, -0.3)], n)


def tail(n: int) -> np.ndarray:
    """Back from the hips, up, then a coil that winds tighter above the rump."""
    u = np.linspace(0.0, 1.0, n)
    lead = ck.smoothstep(0.0, 0.35, u)
    ang = math.pi * 2.6 * ck.smoothstep(0.2, 1.0, u)
    r = 0.17 - 0.12 * u
    cy, cz = COIL_AXIS
    coil = np.column_stack([np.zeros(n), cy - r * np.cos(ang), cz - r * np.sin(ang)])
    start = np.column_stack([np.zeros(n), 0.15 + 0.18 * u, -0.22 - 0.46 * u])
    return start * (1 - lead)[:, None] + coil * lead[:, None]


def leg_pts(side: float, front: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = 0.25 if front else -0.22
    hip = np.array([side * 0.07, 0.14, z])
    knee = np.array([side * 0.24, 0.17, z + (0.03 if front else -0.04)])  # a lizard's sprawl, elbows out
    foot = np.array([side * 0.27, 0.0, z + (0.1 if front else 0.0)])
    return hip, knee, foot


def build_rig() -> tuple[ck.Rig, np.ndarray, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    js = spine(NS + 1)
    for i in reversed(range(NS)):  # hips first: a parent is added before its child
        rig.add(f"spine{i}", js[i + 1], js[i], "root" if i == NS - 1 else f"spine{i + 1}")
    rig.add("head", js[0], js[0] + np.array([0, 0.02, 0.2]), "spine0")
    rig.add("jaw", js[0] + np.array([0, -0.04, 0.0]), js[0] + np.array([0, -0.06, 0.18]), "head")
    jt = tail(NT + 1)
    for i in range(NT):
        rig.add(f"tail{i}", jt[i], jt[i + 1], f"spine{NS - 1}" if i == 0 else f"tail{i - 1}")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for front, fb in ((True, "f"), (False, "b")):
            hip, knee, foot = leg_pts(s, front)
            par = "spine0" if front else f"spine{NS - 1}"
            rig.add(f"leg_{fb}{tag}_a", hip, knee, par)
            rig.add(f"leg_{fb}{tag}_b", knee, foot, f"leg_{fb}{tag}_a")
    return rig, js, jt


def scales(P: np.ndarray, seed: int) -> np.ndarray:
    n = ck.fbm(P * 40.0, seed)  # fine scale speckle: patina green, the copper showing through
    col = ck.mix(PAL["bronze_patina"], PAL["hair_copper"], (0.7 * ck.smoothstep(0.1, 0.45, n))[:, None])
    band = ck.smoothstep(0.6, 0.85, np.abs(np.sin(P[:, 2] * 22.0 + ck.fbm(P * 6.0, seed + 3) * 2.0)))
    return ck.mix(col, PAL["foliage_shadow"], (0.45 * band)[:, None])  # dark cross-bands down the back


def body(mesh: ck.Mesh, rig: ck.Rig, js: np.ndarray, jt: np.ndarray) -> None:
    n = 28
    path = spine(n)
    u = np.linspace(0, 1, n)
    rad = 0.07 + 0.04 * np.sin(np.clip(u, 0, 1) * math.pi) ** 0.7
    P, T = ck.tube(path, rad, 14, squash=0.75)
    col = scales(P, SEED)
    col = ck.mix(col, PAL["sand_dry"] * 0.75, (0.6 * ck.smoothstep(0.2, 0.15, P[:, 1]))[:, None])  # pale belly
    names = [f"spine{i}" for i in range(NS)]
    ck.finish(mesh, P, T, "scale", col, rig.chain(names, js), cavity=0.35)
    # the head: a narrow wedge, a slit mouth, two black eyes
    hb = rig.bones[rig.index("head")]
    Ph, Th = ck.ellipsoid(np.asarray(hb.head) + np.array([0, 0.02, 0.09]), (0.075, 0.055, 0.14), 10, 16)
    Ph[:, 1] += 0.025 * ck.smoothstep(0.0, 0.05, Ph[:, 1] - hb.head[1]) * ck.smoothstep(0.2, 0.04, Ph[:, 2] - hb.head[2])
    ck.finish(mesh, Ph, Th, "scale", scales(Ph, SEED + 1), rig.rigid("head"), cavity=0.3)
    jb = rig.bones[rig.index("jaw")]
    Pj, Tj = ck.ellipsoid((np.asarray(jb.head) + np.asarray(jb.tail)) / 2 + np.array([0, 0.012, -0.01]),
                          (0.06, 0.024, 0.11), 6, 10)
    ck.finish(mesh, Pj, Tj, "scale", PAL["sand_dry"] * 0.7, rig.rigid("jaw"))
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(np.asarray(hb.head) + np.array([s * 0.06, 0.05, 0.06]), (0.02,) * 3, 5, 8)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid("head"), wet=1.0)
    # the tail, the coil's last third bare copper (the stored charge's sparks are coil_sparks)
    nt = 48
    tpath = tail(nt)
    ut = np.linspace(0, 1, nt)
    P, T = ck.tube(tpath, tail_radius(ut), 10)
    along = ut[np.argmin(((P[:, None, :] - tpath[None, :, :]) ** 2).sum(-1), axis=1)]  # nearest ring
    charge = ck.smoothstep(*COIL_CHARGE, along) * 0.8
    col = ck.mix(scales(P, SEED + 2), PAL["hair_copper"], charge[:, None])
    ck.finish(mesh, P, T, "scale", col, rig.chain([f"tail{i}" for i in range(NT)], jt), cavity=0.3)
    old_break(mesh, rig, P, T, jt)
    coil_sparks(mesh, rig, tpath, jt)


def tail_radius(u: np.ndarray) -> np.ndarray:
    return 0.085 * (1 - u) ** 1.3 + 0.012


def nearest_tail_bone(p: np.ndarray, jt: np.ndarray) -> str:
    mid = (jt[:-1] + jt[1:]) / 2.0
    return f"tail{int(np.argmin(np.linalg.norm(mid - p, axis=1)))}"


def on_surface(P: np.ndarray, T: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The point of the part (P, T) nearest q, and its face's outward normal: q projected onto each triangle's plane,
    kept where it falls inside the triangle, the nearest of those (degenerate triangles, as at a pole, are skipped)."""
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    area = np.linalg.norm(fn, axis=1)
    fn /= np.maximum(area, 1e-12)[:, None]
    d = ((q - a) * fn).sum(axis=1)
    p = q - d[:, None] * fn
    inside = area > 1e-12
    for u, v in ((a, b), (b, c), (c, a)):
        inside &= (np.cross(v - u, p - u) * fn).sum(axis=1) >= 0.0
    k = int(np.argmin(np.where(inside, np.abs(d), np.inf)))
    return p[k], fn[k]


def old_break(mesh: ck.Mesh, rig: ck.Rig, P: np.ndarray, T: np.ndarray, jt: np.ndarray) -> None:
    """The weak point (ADR 0151): a closed seam of spawn_wound light in a raised dark ridge, laid on the tail's root at
    BREAK_AT and bent to its curve. Never open, never shedding motes: it is a beast, and this is an old injury."""
    at, n = on_surface(P, T, BREAK_AT)
    a = BREAK_ALONG - n * (BREAK_ALONG @ n)
    a /= np.linalg.norm(a)
    R = np.column_stack([a, n, np.cross(a, n)])  # local x along the seam, y out of the scales, z across it
    (hl, hw), (gl, gw, rise) = BREAK_HALF, BREAK_LIP
    bone = rig.rigid(nearest_tail_bone(at, jt))
    for radii, lift, col, glow in (((hl * gl, rise, hw * gw), 0.0, PAL["lacquer_black"], 0.0),
                                   ((hl, rise * 0.75, hw), rise * 0.5, PAL["spawn_wound"] * 0.65, 1.0)):
        Pl, Tl = ck.ellipsoid((0.0, lift, 0.0), radii, 4, 10)
        Pl[:, 1] -= Pl[:, 0] ** 2 / (2.0 * BREAK_BEND_R)
        ck.finish(mesh, at + Pl @ R.T, Tl, "scale", col, bone, cavity=0.4 * (1.0 - glow), emission=glow)


def coil_sparks(mesh: ck.Mesh, rig: ck.Rig, tpath: np.ndarray, jt: np.ndarray) -> None:
    """The coil's stored charge as starlight points (the copper slot's emission), on the coil's flanks, turn about on
    its near (-x, the battle camera's) and far (+x, the review three-quarter's) side: the coil's outer face is hidden
    where it tightens, each turn inside the last."""
    for k, u in enumerate(COIL_SPARKS):
        c = tpath[int(round(u * (len(tpath) - 1)))]
        side = -1.0 if k % 2 == 0 else 1.0
        p = c + np.array([side, 0.0, 0.0]) * float(tail_radius(np.array([u]))[0])
        Ps, Ts = ck.ellipsoid(p, (COIL_SPARK_R,) * 3, 4, 6)
        ck.finish(mesh, Ps, Ts, "copper", PAL["starlight"], rig.rigid(nearest_tail_bone(p, jt)), emission=1.0)


def ridge(mesh: ck.Mesh, rig: ck.Rig, js: np.ndarray) -> None:
    """Copper spines down the back, each tip a stored charge."""
    path = spine(14)[2:13]
    for k, p in enumerate(path):
        h = 0.07 + 0.04 * math.sin(k / (len(path) - 1) * math.pi)
        base = p + np.array([0, 0.07, 0])
        tip = base + np.array([0, h, -0.02])
        bone = f"spine{min(NS - 1, int(k / len(path) * NS))}"
        P, T = ck.tube(np.array([base, tip]), np.array([0.018, 0.004]), 6)
        ck.finish(mesh, P, T, "copper", PAL["hair_copper"], rig.rigid(bone), cavity=0.2)
        Pt, Tt = ck.ellipsoid(tip, (0.011,) * 3, 4, 6)
        ck.finish(mesh, Pt, Tt, "copper", PAL["starlight"], rig.rigid(bone), emission=1.0)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for front, fb in ((True, "f"), (False, "b")):
            hip, knee, foot = leg_pts(s, front)
            for seg, p0, p1, r0, r1 in (("a", hip, knee, 0.03, 0.022), ("b", knee, foot, 0.02, 0.012)):
                P, T = ck.tube(ck.bezier([p0, (p0 + p1) / 2 + np.array([0, 0.015, 0]), p1], 5),
                               np.linspace(r0, r1, 5), 7)
                ck.finish(mesh, P, T, "scale", scales(P, SEED + 4), rig.rigid(f"leg_{fb}{tag}_{seg}"), cavity=0.3)
            for d in (-1.0, 0.0, 1.0):  # three splayed toes
                toe = foot + np.array([s * 0.02 + d * 0.025, 0.004, 0.05 + 0.01 * (1 - abs(d))])
                P, T = ck.tube(np.array([foot + [0, 0.006, 0], toe]), np.array([0.009, 0.003]), 4)
                ck.finish(mesh, P, T, "scale", PAL["hair_copper"] * 0.6, rig.rigid(f"leg_{fb}{tag}_b"))


KO_DROP = 0.05  # the KO: how far the body sinks onto its belly (m)
KO_SPLAY = 25.0  # the KO: the legs splay out (degrees at the hip, the left side's sign)


def build_clips() -> list[ck.Clip]:
    tl = [f"tail{i}" for i in range(NT)]
    idle = ck.Clip("idle", 1.8, loop=True)  # head flicks, the coil twitches, the body pumps
    idle.wave("head", amp_rot=(4.0, 8.0, 0), cycles=2, steps=6)
    idle.wave("spine1", amp_loc=(0, 0.006, 0), cycles=2)
    for i, b in enumerate(tl[3:], 3):
        idle.wave(b, amp_rot=(5.0, 3.0, 0), cycles=1, phase=-i * 0.6)
    attack = ck.Clip("attack", 0.9)  # a darting bite
    for t, fwd, bite in ((0.0, 0, 0), (0.25, -0.06, 0.3), (0.42, 0.32, 1.0), (0.55, 0.3, 0.0), (0.9, 0, 0)):
        attack.key("root", t, (0, 0, 0), (0, 0, fwd))
        attack.key("jaw", t, (25.0 * bite, 0, 0))
        attack.key("head", t, (-10.0 * bite, 0, 0))
    cast = ck.Clip("cast", 1.3)  # it rears, the coil tightens, the jaw gapes to spit the charge
    for t, s, spit in ((0.0, 0.0, 0.0), (0.45, 1.0, 0.0), (0.7, 1.0, 1.0), (0.95, 0.6, 0.6), (1.3, 0.0, 0.0)):
        cast.key("spine0", t, (-18.0 * s, 0, 0))
        cast.key("spine1", t, (-8.0 * s, 0, 0))
        cast.key("head", t, (8.0 * s - 6.0 * spit, 0, 0))
        cast.key("jaw", t, (40.0 * spit, 0, 0))
        for b in tl[3:]:
            cast.key(b, t, (-10.0 * s, 0, 0))
    hit = ck.Clip("hit", 0.5)  # a flinch sideways
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.5, 0.0)):
        hit.key("root", t, (0, 14.0 * s, 0), (0.05 * s, 0, -0.06 * s))
        hit.key("head", t, (0, -20.0 * s, 0))
    # the legs splay, the coil unwinds; M3-CRE-632: it sinks onto its belly (it dropped 0.09 m, 3.5 cm through the
    # floor) and the legs splay out flat (keyed -25, they drove the feet 0.18 m down through it)
    ko = ck.Clip("ko", 1.4)
    for t, s in ((0.0, 0.0), (0.4, 0.6), (0.9, 1.0), (1.4, 1.0)):
        ko.key("root", t, (0, 0, 0), (0, -KO_DROP * s, 0))
        ko.key("head", t, (14.0 * s, 0, 0))
        for b in tl[2:]:
            ko.key(b, t, (16.0 * s, 0, 0))
        for tag in ("l", "r"):
            sd = 1.0 if tag == "l" else -1.0
            for fb in ("f", "b"):
                ko.key(f"leg_{fb}{tag}_a", t, (0, 0, KO_SPLAY * s * sd))
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): a planted foot stays on the floor (its leg turns up at the
# hip the least it takes), the coil rides up over the floor, and the body lifts the least it takes where it would
# still press into it.
GROUNDED_LIMBS = [(f"leg_{fb}{tag}_a", 2, 1.0 if tag == "l" else -1.0, 45.0) for tag in "lr" for fb in "fb"] + [("tail2", 0, -1.0, 30.0), ("root", gr.LIFT, 1.0, 0.1)]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def build_mesh() -> tuple[ck.Rig, ck.Mesh]:
    """The rig and the skinned mesh, without Blender (M3-CRE-650: the preview sheets build from this too)."""
    rig, js, jt = build_rig()
    mesh = ck.Mesh("vein_sparker")
    body(mesh, rig, js, jt)
    ridge(mesh, rig, js)
    legs(mesh, rig)
    return rig, mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, mesh = build_mesh()
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "vein_sparker"})
    print(f"vein_sparker: {info}")


if __name__ == "__main__":
    main()
