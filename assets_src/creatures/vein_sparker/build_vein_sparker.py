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

SEED = 5207
PAL = {k: ck.hexrgb(v) for k, v in {
    "bronze_patina": "#5F8A78", "hair_copper": "#A65A2A", "starlight": "#DCE6FF", "lacquer_black": "#1D1916",
    "sand_dry": "#EFDDB4", "foliage_shadow": "#1E4A3A",
}.items()}

NS = 4  # spine bones, head end first
NT = 7  # tail bones


def spine(n: int) -> np.ndarray:
    return ck.bezier([(0, 0.2, 0.42), (0, 0.17, 0.2), (0, 0.16, -0.05), (0, 0.15, -0.3)], n)


def tail(n: int) -> np.ndarray:
    """Back from the hips, up, then a coil that winds tighter above the rump."""
    u = np.linspace(0.0, 1.0, n)
    lead = ck.smoothstep(0.0, 0.35, u)
    ang = math.pi * 2.6 * ck.smoothstep(0.2, 1.0, u)
    r = 0.17 - 0.12 * u
    cy, cz = 0.5, -0.68
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
    # the tail, the coil brightening toward its tip
    nt = 48
    tpath = tail(nt)
    ut = np.linspace(0, 1, nt)
    P, T = ck.tube(tpath, 0.085 * (1 - ut) ** 1.3 + 0.012, 10)
    along = ut[np.argmin(((P[:, None, :] - tpath[None, :, :]) ** 2).sum(-1), axis=1)]  # nearest ring
    charge = ck.smoothstep(0.5, 1.0, along) * 0.8
    col = ck.mix(scales(P, SEED + 2), PAL["starlight"] * 0.7, charge[:, None])
    ck.finish(mesh, P, T, "scale", col, rig.chain([f"tail{i}" for i in range(NT)], jt), cavity=0.3, emission=charge)


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
    ko = ck.Clip("ko", 1.4)  # the legs splay, the coil unwinds
    for t, s in ((0.0, 0.0), (0.4, 0.6), (0.9, 1.0), (1.4, 1.0)):
        ko.key("root", t, (0, 0, 0), (0, -0.09 * s, 0))
        ko.key("head", t, (14.0 * s, 0, 0))
        for b in tl[2:]:
            ko.key(b, t, (16.0 * s, 0, 0))
        for tag in ("l", "r"):
            sd = 1.0 if tag == "l" else -1.0
            for fb in ("f", "b"):
                ko.key(f"leg_{fb}{tag}_a", t, (0, 0, -25.0 * s * sd))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, js, jt = build_rig()
    mesh = ck.Mesh("vein_sparker")
    body(mesh, rig, js, jt)
    ridge(mesh, rig, js)
    legs(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "vein_sparker"})
    print(f"vein_sparker: {info}")


if __name__ == "__main__":
    main()
