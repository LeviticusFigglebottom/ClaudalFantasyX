"""Scree crawler, Ch12 the Cloudloom approach (M3-CRE-628): docs/kb/art/creatures/act2/variants.md.

blender --background --factory-startup --python assets_src/creatures/scree_crawler/build_scree_crawler.py -- \
    --out assets/creatures/scree_crawler/scree_crawler.glb

A variant of the slag tortoise: a mountain tortoise whose shell carries split scree instead of slag. The slag
tortoise's rig and clips, rebuilt through the base build's parameters (so the slag tortoise's own output is
unchanged): more, smaller and sharper plates, faceted like split stone, in grey slate (overcast_slate, storm_slate)
with dry snow packed in the splits and dusted on the crown and dark grit between the stones (no frost or rime: ADR
0015 and ADR 0204 §2 keep ice out of Ch12; M4-CRE-670), and a shaggier skin (tufted) in a cold grey-brown. The
spawn_wound crack over the neck is the base's. The base build is imported, not copied, so a fix to the slag
tortoise reaches the scree crawler on its next rebuild.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "slag_tortoise"))
import build_slag_tortoise as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 8287
SW = {k: ck.hexrgb(v) for k, v in {
    "overcast_slate": "#6F7E8E", "storm_slate": "#3E4A57", "snow": "#E8E6DF", "timber_weathered": "#7E6A55",
    "sand_dry": "#EFDDB4", "lacquer_black": "#1D1916",
}.items()}

base.SEED = SEED
base.SHELL_CELLS = 40  # split scree: more, smaller stones (slag tortoise 22)
base.SHELL_LUMP = 0.08
base.SHELL_FLAT = True  # each stone's faces read as split, not glassy
base.SKIN_SHAG = 0.022  # the shaggier skin
base.PAL = dict(base.PAL)
base.PAL.update({
    # the crust's colour is mix(volcanic_stone * 0.8, lacquer_black, 0.6..0.9): here both are slate scree
    "volcanic_stone": SW["overcast_slate"] / 0.8,
    "lacquer_black": ck.mix(SW["overcast_slate"], SW["storm_slate"], 0.45),
    "bronze_patina": ck.mix(SW["snow"], SW["overcast_slate"], 0.15),  # dry snow packed in the splits (the base's copper)
    "sand_dry": ck.mix(SW["snow"], SW["sand_dry"], 0.3),  # snow dusted on the crown; the skin's pale folds
    "laterite": ck.mix(SW["timber_weathered"], SW["overcast_slate"], 0.35),  # a cold grey-brown skin
})


GRIT_SCALE = 40.0  # grit speckles per metre
GRIT_DARKEN = 0.35


def stones(mesh: ck.Mesh) -> None:
    """Each split face its own stone's tone (the crust is faceted: its vertices come three to a face), lighter and
    darker slate in blotches about a stone wide, so the scree reads as loose stones, not one shell."""
    P, C, E = mesh.pos[0], mesh.col[0], mesh.uv2[0]
    centre = np.repeat(P.reshape(-1, 3, 3).mean(axis=1), 3, axis=0)
    tone = 0.82 + 0.3 * ck.value_noise(centre * 5.5, SEED + 7) + 0.08 * ck.value_noise(centre * 23.0, SEED + 8)
    grit = ck.smoothstep(0.7, 0.85, ck.value_noise(centre * GRIT_SCALE, SEED + 9))  # dark grit between the stones
    tone = tone * (1.0 - GRIT_DARKEN * grit)
    keep = E[:, 1] > 0.05  # the weak point's crack keeps its colour
    C[:, :3] = np.where(keep[:, None], C[:, :3], np.maximum(C[:, :3] * tone[:, None], ck.hexrgb("#1D1916")))


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = base.build_mesh(rig, "scree_crawler")
    stones(mesh)
    # the eyes keep the base's lacquer_black (the palette swatch, not the scree's slate)
    eye = mesh.materials.index("eye")
    for k, tm in enumerate(mesh.tri_mat):
        if len(tm) and tm[0] == eye:
            mesh.col[k][:, :3] = ck.hexrgb("#1D1916")
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = base.build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, base.export_clips(rig, mesh), args.out, extras={"hymn_creature": "scree_crawler"})
    print(f"scree_crawler: {info}")


if __name__ == "__main__":
    main()
