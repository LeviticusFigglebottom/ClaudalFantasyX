"""Scuttler, Ch1 (M3-CRE-02): a small Undertow-spawn fought before Hullgnaw (m2-slice's act1_ch01 beat sheet §9).

blender --background --factory-startup --python assets_src/creatures/scuttler/build_scuttler.py -- \
    --out assets/creatures/scuttler/scuttler.glb

A grotesque echo of a sea-louse: a 0.7 m arched back of overlapping wet black plates, each seam a thin spawn_wound
wound, a fringe of fourteen short legs, two long feelers. It rolls up when struck. Its silhouette (a low ribbed arch)
is distinct from the tide crawler's high-legged spider shape.
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

SEED = 1503
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "storm_slate": "#3E4A57",
}.items()}

NSEG = 7
LENGTH = 0.7


def seg_z(i: int) -> float:
    return LENGTH / 2 - (i + 0.5) * LENGTH / NSEG


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("front", (0, 0.15, 0.05), (0, 0.15, LENGTH / 2), "root")
    rig.add("back", (0, 0.15, 0.05), (0, 0.15, -LENGTH / 2), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"feeler_{tag}", (s * 0.05, 0.12, LENGTH / 2), (s * 0.2, 0.2, LENGTH / 2 + 0.35), "front")
    return rig


def bone_for(z: float) -> str:
    return "front" if z >= 0.05 else "back"


def plates(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED)
    for i in range(NSEG):
        z = seg_z(i)
        w = 0.24 * math.sin((i + 0.6) / (NSEG + 0.2) * math.pi) ** 0.5 + 0.05
        h = 0.18 * math.sin((i + 0.6) / (NSEG + 0.2) * math.pi) ** 0.6 + 0.03
        P, T = ck.ellipsoid((0, 0.06, z), (w, h, LENGTH / NSEG * 0.75), 8, 18)
        P[:, 1] = np.maximum(P[:, 1], 0.06)
        rear = ck.smoothstep(0.0, -1.0, (P[:, 2] - z) / (LENGTH / NSEG * 0.75))
        n = ck.fbm(P * 9.0, SEED + i)
        col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, n)[:, None])
        wound = ck.smoothstep(0.75, 1.0, rear) * ck.smoothstep(0.08, 0.14, P[:, 1])
        col = ck.mix(col, PAL["spawn_wound"] * 0.55, wound[:, None])
        ck.finish(mesh, P, T, "carapace", col, rig.rigid(bone_for(z)), wet=1.0, cavity=0.2, emission=wound)
        for s in (-1.0, 1.0):
            hip = np.array([s * w * 0.8, 0.07, z])
            tip = np.array([s * (w + 0.12), 0.0, z + rng.uniform(-0.02, 0.04)])
            Pl, Tl = ck.tube(ck.bezier([hip, (hip + tip) / 2 + np.array([s * 0.02, 0.05, 0]), tip], 5),
                             np.linspace(0.016, 0.004, 5), 5)
            ck.finish(mesh, Pl, Tl, "carapace", PAL["storm_slate"] * 0.7, rig.rigid(bone_for(z)), wet=1.0)
    Ph, Th = ck.ellipsoid((0, 0.08, LENGTH / 2 + 0.02), (0.1, 0.07, 0.07), 6, 10)
    ck.finish(mesh, Ph, Th, "carapace", PAL["lacquer_black"], rig.rigid("front"), wet=1.0)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid((s * 0.06, 0.11, LENGTH / 2 + 0.06), (0.015,) * 3, 4, 6)
        ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid("front"), wet=1.0, emission=1.0)
    for tag in ("l", "r"):
        b = rig.bones[rig.index(f"feeler_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        P, T = ck.tube(ck.bezier([h0, (h0 + h1) / 2 + np.array([0, 0.08, 0]), h1], 8), np.linspace(0.01, 0.002, 8), 4)
        ck.finish(mesh, P, T, "carapace", PAL["storm_slate"], rig.rigid(f"feeler_{tag}"), wet=1.0)


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 1.4, loop=True)
    idle.wave("feeler_l", amp_rot=(10.0, 12.0, 0), cycles=2)
    idle.wave("feeler_r", amp_rot=(10.0, -12.0, 0), cycles=2, phase=1.1)
    idle.wave("root", amp_loc=(0.0, 0.008, 0.012), cycles=2)
    attack = ck.Clip("attack", 0.9)  # a scuttling charge and a head-butt
    for t, fwd, rear in ((0.0, 0, 0), (0.3, -0.05, 1.0), (0.45, 0.4, -0.5), (0.6, 0.35, 0), (0.9, 0, 0)):
        attack.key("root", t, (0, 0, 0), (0, 0, fwd))
        attack.key("front", t, (-18.0 * rear, 0, 0))
    cast = ck.Clip("cast", 1.1)  # it arches high and the seams pulse
    for t, s in ((0.0, 0.0), (0.4, 1.0), (0.8, 1.0), (1.1, 0.0)):
        cast.key("front", t, (-14.0 * s, 0, 0))
        cast.key("back", t, (14.0 * s, 0, 0))
        cast.key("root", t, (0, 0, 0), (0, 0.05 * s, 0))
    hit = ck.Clip("hit", 0.5)  # it starts to roll up
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.5, 0.0)):
        hit.key("front", t, (35.0 * s, 0, 0))
        hit.key("back", t, (-35.0 * s, 0, 0))
    ko = ck.Clip("ko", 1.2)  # it rolls up and tips over
    for t, s in ((0.0, 0.0), (0.4, 0.8), (0.8, 1.0), (1.2, 1.0)):
        ko.key("front", t, (75.0 * s, 0, 0))
        ko.key("back", t, (-75.0 * s, 0, 0))
        ko.key("root", t, (0, 0, 70.0 * max(s - 0.5, 0) * 2), (0, 0.06 * s, 0))
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): the feelers turn up over the floor first (up to 60°), then the
# body lifts the least it takes when it curls (its ends come down past its pivot, so the arch rises over them, as a
# louse's does), and when it tips onto its side in the KO.
GROUNDED_LIMBS = [("feeler_l", 0, -1.0, 60.0), ("feeler_r", 0, -1.0, 60.0), ("root", gr.LIFT, 1.0, 0.5)]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("scuttler")
    plates(mesh, rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "scuttler"})
    print(f"scuttler: {info}")


if __name__ == "__main__":
    main()
