"""Slag tortoise, Ch5 the copper veins (M3-CRE-04): docs/kb/art/creatures/act1/slag_tortoise.md.

blender --background --factory-startup --python assets_src/creatures/slag_tortoise/build_slag_tortoise.py -- \
    --out assets/creatures/slag_tortoise/slag_tortoise.glb

A terrace tortoise whose shell carries cooled slag from the ash-plume: a glassy black crust far bigger than the
tortoise, cracked into plates with green copper weeping from the seams, a spawn_wound crack over the neck. Dusty
laterite skin, stubby legs, a beaked head on a wrinkled neck.
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

SEED = 5203
PAL = {k: ck.hexrgb(v) for k, v in {
    "volcanic_stone": "#3A3A3F", "bronze_patina": "#5F8A78", "laterite": "#A8573A", "sand_dry": "#EFDDB4",
    "spawn_wound": "#3FE0C8", "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E", "bone": "#E6DAC0",
}.items()}

SHELL_C = np.array([0.0, 0.38, -0.05])
SHELL_R = np.array([0.6, 0.42, 0.68])
# A variant's parameters (the scree crawler's frost-split scree and shaggier skin, M3-CRE-628); these values are the
# slag tortoise's: the shell's plate count, each plate's lift, faceted plates, and the skin's shag (metres).
SHELL_CELLS = 22
SHELL_LUMP = 0.06
SHELL_FLAT = False
SKIN_SHAG = 0.0
# The KO (M3-CRE-631): how far the legs tuck in (degrees) and the body rises (metres) by the end of the roll.
KO_TUCK = 40.0
KO_RISE = 0.04


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("shell", (0, 0.3, -0.3), (0, 0.3, 0.3), "root")
    rig.add("neck", (0, 0.3, 0.45), (0, 0.36, 0.72), "shell")
    rig.add("head", (0, 0.36, 0.72), (0, 0.36, 0.92), "neck")
    for sx, sz, tag in ((1, 1, "fl"), (-1, 1, "fr"), (1, -1, "bl"), (-1, -1, "br")):
        rig.add(f"leg_{tag}", (sx * 0.42, 0.28, sz * 0.38), (sx * 0.5, 0.0, sz * 0.45), "shell")
    rig.add("tail", (0, 0.25, -0.62), (0, 0.15, -0.82), "shell")
    return rig


def shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rings, segs = 22, 64
    prof = [(math.sin(math.pi / 2 * i / rings), math.cos(math.pi / 2 * i / rings)) for i in range(rings + 1)]
    P, T = ck.lathe(prof, segs)
    unit = P.copy()
    rng = np.random.default_rng(SEED)
    cells = rng.normal(size=(SHELL_CELLS, 3))
    cells[:, 1] = np.abs(cells[:, 1]) + 0.3
    cells /= np.linalg.norm(cells, axis=1, keepdims=True)
    d = unit @ cells.T
    o = np.argsort(-d, axis=1)
    gap = d[np.arange(len(d)), o[:, 0]] - d[np.arange(len(d)), o[:, 1]]
    seam = 1.0 - ck.smoothstep(0.0, 0.025, gap)
    lump = rng.uniform(0.0, SHELL_LUMP, len(cells))[o[:, 0]] + 0.03 * ck.fbm(unit * 4.0, SEED + 1)
    P = SHELL_C + unit * SHELL_R * (1.0 + lump - 0.05 * seam)[:, None]
    P[:, 1] = np.maximum(P[:, 1], 0.22)
    neck_crack = np.exp(-(((unit[:, 2] - 0.85) / 0.12) ** 2 + (unit[:, 0] / 0.2) ** 2)) * seam * (unit[:, 1] > 0.2)
    col = ck.mix(PAL["volcanic_stone"] * 0.8, PAL["lacquer_black"], (0.6 + 0.3 * ck.fbm(P * 8.0, SEED + 2))[:, None])
    col = ck.mix(col, PAL["bronze_patina"], (0.8 * seam)[:, None])
    col = ck.mix(col, PAL["sand_dry"] * 0.5, (0.15 * ck.smoothstep(0.85, 1.0, unit[:, 1]))[:, None])  # ash dust on top
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, neck_crack[:, None])
    ck.finish(mesh, P, T, "crust", col, rig.rigid("shell"), cavity=0.7 * seam, emission=neck_crack, flat=SHELL_FLAT)
    # the plastron and the tortoise's own scuted rim under the crust
    Pu, Tu = ck.lathe([(0.0, 0.2), (0.5, 0.22), (0.58, 0.28)], 48)
    Pu = Pu * np.array([1.0, 1.0, 1.12]) + np.array([0, 0, -0.05])
    ck.finish(mesh, Pu, ck.flip(Tu), "skin", PAL["tortoiseshell"], rig.rigid("shell"), cavity=0.3)


def shag(P: np.ndarray, T: np.ndarray, seed: int) -> np.ndarray:
    """The skin pushed out in tufts by SKIN_SHAG (a variant's shaggier skin); unchanged when it is 0."""
    if not SKIN_SHAG:
        return P
    tuft = ck.smoothstep(-0.2, 0.6, ck.value_noise(P * 38.0, seed)) * (0.6 + 0.4 * ck.fbm(P * 11.0, seed + 1))
    return P + ck.vertex_normals(P, T) * (SKIN_SHAG * tuft)[:, None]


def limbs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for tag in ("fl", "fr", "bl", "br"):
        b = rig.bones[rig.index(f"leg_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        P, T = ck.tube(ck.bezier([h0, (h0 + h1) / 2 + np.array([0, 0, 0.02]), h1], 6), np.array(
            [0.11, 0.12, 0.11, 0.1, 0.1, 0.11]), 10)
        P = shag(P, T, SEED + 20)
        P[:, 1] = np.maximum(P[:, 1], 0.0)  # M3-CRE-631: a flat sole on the floor (the foot's end sank 4.5 cm under it)
        wr = 0.5 + 0.5 * np.sin(P[:, 1] * 80.0)
        col = ck.mix(PAL["laterite"], PAL["sand_dry"], (0.3 * wr)[:, None])
        ck.finish(mesh, P, T, "skin", col, rig.rigid(f"leg_{tag}"), cavity=0.4 * (1 - wr))
        for k in range(3):  # blunt claws
            a = (k - 1) * 0.5
            c0 = h1 + np.array([0.06 * math.sin(a), 0.02, 0.06 * math.cos(a) * (1 if tag[0] == "f" else -1)])
            Pc, Tc = ck.ellipsoid(c0, (0.025, 0.02, 0.035), 4, 6)
            ck.finish(mesh, Pc, Tc, "skin", PAL["bone"] * 0.8, rig.rigid(f"leg_{tag}"))
    n = rig.bones[rig.index("neck")]
    P, T = ck.tube(ck.bezier([np.asarray(n.head) - np.array([0, 0, 0.1]), n.head, n.tail], 10),
                   np.linspace(0.12, 0.09, 10), 12)
    P = shag(P, T, SEED + 21)
    wr = 0.5 + 0.5 * np.sin(P[:, 2] * 90.0)
    ck.finish(mesh, P, T, "skin", ck.mix(PAL["laterite"], PAL["sand_dry"], (0.35 * wr)[:, None]), rig.rigid("neck"),
              cavity=0.5 * (1 - wr))
    h = rig.bones[rig.index("head")]
    Ph, Th = ck.ellipsoid((np.asarray(h.head) + np.asarray(h.tail)) / 2, (0.1, 0.09, 0.14), 8, 12)
    beak = ck.smoothstep(0.82, 0.92, Ph[:, 2])
    ck.finish(mesh, Ph, Th, "skin", ck.mix(PAL["laterite"], PAL["tortoiseshell"], beak[:, None]), rig.rigid("head"))
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(np.asarray(h.head) + np.array([s * 0.07, 0.04, 0.1]), (0.018,) * 3, 4, 6)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid("head"), wet=1.0)
    t = rig.bones[rig.index("tail")]
    Pt, Tt = ck.tube(np.array([t.head, t.tail]), np.array([0.06, 0.01]), 8)
    ck.finish(mesh, Pt, Tt, "skin", PAL["laterite"], rig.rigid("tail"))


def build_mesh(rig: ck.Rig, name: str = "slag_tortoise") -> ck.Mesh:
    mesh = ck.Mesh(name)
    shell(mesh, rig)
    limbs(mesh, rig)
    return mesh


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 3.2, loop=True)
    for t, out in ((0.0, 0.0), (0.8, 0.0), (1.4, -0.08), (2.2, -0.08), (2.8, 0.0), (3.2, 0.0)):
        idle.key("neck", t, (8.0 * out / 0.08, 0, 0), (0, 0, out))
    idle.wave("head", amp_rot=(0.0, 12.0, 0.0), cycles=1)
    idle.wave("shell", amp_loc=(0.0, 0.01, 0.0), cycles=2)
    attack = ck.Clip("attack", 1.2)
    for t, out, bite in ((0.0, 0.0, 0), (0.35, -0.08, 0), (0.55, 0.18, 12), (0.7, 0.16, -4), (1.2, 0.0, 0)):
        attack.key("neck", t, (bite, 0, 0), (0, 0, out))
        attack.key("shell", t, (-3.0 * out / 0.18, 0, 0), (0, 0, 0.1 * max(out, 0)))
    cast = ck.Clip("cast", 1.4)  # it withdraws into the crust
    for t, s in ((0.0, 0.0), (0.35, 1.0), (1.0, 1.0), (1.4, 0.0)):
        cast.key("neck", t, (0, 0, 0), (0, -0.02 * s, -0.28 * s))
        for tag, sx in (("fl", 1), ("fr", -1), ("bl", 1), ("br", -1)):
            cast.key(f"leg_{tag}", t, (0, 0, 0), (-sx * 0.08 * s, 0.12 * s, 0))
        cast.key("shell", t, (0, 0, 0), (0, -0.1 * s, 0))
    hit = ck.Clip("hit", 0.5)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.5, 0.0)):
        hit.key("neck", t, (0, 0, 0), (0, 0, -0.15 * s))
        hit.key("shell", t, (4.0 * s, 0, 0))
    # it rolls onto its side about the right edge. M3-CRE-631: it draws its legs in toward the plastron as it tips
    # (a left leg tucks with -z, a right one with +z), and rides up by the crust's overhang past the pivot, so the
    # crust and the legs underneath stay on the floor (they sank 8.5 cm)
    ko = ck.Clip("ko", 1.6)
    pivot = np.array([-0.55, 0.0, 0.0])
    for t, roll in ((0.0, 0.0), (0.6, -20.0), (1.2, -78.0), (1.6, -84.0)):
        R = ck.euler(0.0, 0.0, -roll)
        off = pivot - R @ pivot + np.array([0.0, KO_RISE * abs(roll) / 84.0, 0.0])
        ko.key("root", t, (0, 0, -roll), tuple(off))
        for tag, sx in (("fl", 1), ("fr", -1), ("bl", 1), ("br", -1)):
            ko.key(f"leg_{tag}", t, (abs(roll) * 0.3, 0, -sx * KO_TUCK * abs(roll) / 84.0))
        ko.key("neck", t, (25.0 * abs(roll) / 84.0, 0, 0))
    return [idle, attack, cast, hit, ko]


# The limbs kept on the floor (M3-CRE-631, common/grounding.py): a stubby leg is pushed up into the shell, by at most
# 0.2 m, wherever the shell's bob, pitch or roll would press its sole through the floor.
GROUNDED_LIMBS = [(f"leg_{tag}", gr.LIFT, 1.0, 0.2) for tag in ("fl", "fr", "bl", "br")]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "slag_tortoise"})
    print(f"slag_tortoise: {info}")


if __name__ == "__main__":
    main()
