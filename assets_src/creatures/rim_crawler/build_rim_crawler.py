"""Rim crawler, Ch16 the Pale Rim (M3-CRE-628): docs/kb/art/creatures/act2/variants.md.

blender --background --factory-startup --python assets_src/creatures/rim_crawler/build_rim_crawler.py -- \
    --out assets/creatures/rim_crawler/rim_crawler.glb

A palette variant of the tide crawler: Undertow-spawn crawlers bleached by days of white water. The tide crawler's
build, rig and clips, re-coloured: a chalky carapace (mortar_white) with the spawn's lacquer_black left in the
joints (each leg segment's ends, the body's underside and seams), and its wounds dimmer (materials.json). The base
build is imported, not copied, so a fix to the tide crawler reaches the rim crawler on its next rebuild.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "tide_crawler"))
import build_tide_crawler as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 8291
SW = {k: ck.hexrgb(v) for k, v in {
    "mortar_white": "#E6E1D6", "lacquer_black": "#1D1916", "bone": "#E6DAC0",
}.items()}
CHALK = SW["mortar_white"] * 0.94
BLACK = SW["lacquer_black"]

base.SEED = SEED
base.PAL = dict(base.PAL)
base.PAL.update({
    "lacquer_black": CHALK,  # bleached: the carapace chalk-white ...
    "abyss_navy": ck.mix(SW["mortar_white"], SW["bone"], 0.5) * 0.9,
    "storm_slate": CHALK,
})


def joints(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The spawn's black left in the joints: each leg segment darkens toward both its ends, and the body toward its
    underside, where the white water never scoured it. The chalk is dry, the black still wet."""
    bones = rig.bones
    for k, P in enumerate(mesh.pos):
        C, E, J = mesh.col[k], mesh.uv2[k], mesh.joints[k][:, 0]
        if E[:, 1].min() >= 0.99:  # the glowing eyes
            continue
        b = bones[int(J[0])]
        if b.name == "body":
            low = ck.smoothstep(base.BODY[1] + 0.02, base.BODY[1] - 0.12, P[:, 1])
            seam = ck.smoothstep(0.55, 0.95, np.abs(ck.fbm(P * 9.0, SEED + 1)) * 2.0) * 0.5
            dark = np.maximum(low * 0.85, seam) * (1.0 - E[:, 1])
        else:
            h, tl = np.asarray(b.head), np.asarray(b.tail)
            d = tl - h
            t = np.clip(((P - h) @ d) / float(d @ d), 0.0, 1.0)
            dark = np.maximum(ck.smoothstep(0.22, 0.0, t), ck.smoothstep(0.8, 1.0, t) * 0.9)
            if b.name.endswith("_b") and b.name.startswith("leg"):
                dark = np.maximum(ck.smoothstep(0.22, 0.0, t), ck.smoothstep(0.7, 1.0, t))  # the tips dipped black
        C[:, :3] = ck.mix(C[:, :3], BLACK, dark[:, None])
        C[:, 3] = C[:, 3] * (0.2 + 0.8 * dark)  # the chalk is dry; the black in the joints is still wet lacquer
        E[:, 0] = np.clip(E[:, 0] + 0.4 * dark, 0.0, 1.0)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("rim_crawler")
    base.body(mesh, rig)
    base.legs(mesh, rig)
    joints(mesh, rig)
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = base.build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, base.export_clips(rig, mesh), args.out, extras={"hymn_creature": "rim_crawler"})
    print(f"rim_crawler: {info}")


if __name__ == "__main__":
    main()
