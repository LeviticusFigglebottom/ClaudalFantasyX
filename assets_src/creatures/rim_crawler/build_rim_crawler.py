"""Rim crawler, Ch16 the Pale Rim (M3-CRE-628): docs/kb/art/creatures/act2/variants.md.

blender --background --factory-startup --python assets_src/creatures/rim_crawler/build_rim_crawler.py -- \
    --out assets/creatures/rim_crawler/rim_crawler.glb

A palette variant of the tide crawler: Undertow-spawn crawlers bleached by days of white water. The tide crawler's
build, rig and clips, re-coloured: a chalky carapace (mortar_white, weathered with overcast_slate) going a wet
storm_slate down its flanks and in its seams, with the spawn's lacquer_black left in the joints (each leg segment's
ends and the body's underside), and its wounds glowing through the chalk (materials.json). The base
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
    "mortar_white": "#E6E1D6", "lacquer_black": "#1D1916", "bone": "#E6DAC0", "overcast_slate": "#6F7E8E",
    "storm_slate": "#3E4A57",
}.items()}
CHALK = SW["mortar_white"] * 0.94
BLACK = SW["lacquer_black"]
# The value read on the Rim's white shallows (the Act II plan sheet: chalk on white sand, risk high): the flanks go a wet
# grey-blue toward the underside, the plates' seams are slate, and the carapace's chalk is weathered with slate mottling
WET_FLANK = SW["storm_slate"]
FLANK_BAND = (0.07, -0.06)  # metres over the body's centre: the flank darkens from the first to the second
SEAM = 0.85  # the seams' slate strength
WEATHER = 0.3  # the most the slate mottles the chalk

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
        wet = np.zeros(len(P))
        if b.name == "body":
            low = ck.smoothstep(base.BODY[1] + 0.02, base.BODY[1] - 0.12, P[:, 1])
            seam = ck.smoothstep(0.55, 0.95, np.abs(ck.fbm(P * 9.0, SEED + 1)) * 2.0) * SEAM
            lit = 1.0 - E[:, 1]
            weather = ck.smoothstep(0.0, 0.5, ck.fbm(P * 5.0, SEED + 2)) * WEATHER
            flank = ck.smoothstep(base.BODY[1] + FLANK_BAND[0], base.BODY[1] + FLANK_BAND[1], P[:, 1])
            C[:, :3] = ck.mix(C[:, :3], SW["overcast_slate"], (weather * lit)[:, None])
            C[:, :3] = ck.mix(C[:, :3], WET_FLANK, (np.maximum(flank, seam) * lit)[:, None])
            wet = flank * lit  # the flank is wet
            dark = low * 0.85 * lit
        else:
            h, tl = np.asarray(b.head), np.asarray(b.tail)
            d = tl - h
            t = np.clip(((P - h) @ d) / float(d @ d), 0.0, 1.0)
            dark = np.maximum(ck.smoothstep(0.22, 0.0, t), ck.smoothstep(0.8, 1.0, t) * 0.9)
            if b.name.endswith("_b") and b.name.startswith("leg"):
                dark = np.maximum(ck.smoothstep(0.22, 0.0, t), ck.smoothstep(0.7, 1.0, t))  # the tips dipped black
        C[:, :3] = ck.mix(C[:, :3], BLACK, dark[:, None])
        C[:, 3] = C[:, 3] * (0.2 + 0.8 * np.maximum(dark, wet))  # the chalk is dry; the black joints are still wet
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
