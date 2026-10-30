"""The Ch6 Stillguard soldiers (M3-CHR-508), six variants on Moll's kit. Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/stillguard/build_stillguard.py -- \\
        --variant a [--out assets/characters/stillguard_a/stillguard_a.glb] [--report r.json] [--bake-dir DIR]

The standard Stillguard that Inquisitor Moll's kit derives from (hadric_moll.md): his build (build_moll.build, the
hero path on build_asha) with his costume less the Inquisitor's sash (moll_costume: the jack, the four-row cuirass, the
two whole pauldrons with the Level, the tunic's skirt and sleeves, the trousers, the wraps, the sandals, the bracers)
and his round shield on the left forearm (moll_props), but Toma's spear in the right fist (toma_props.spear, gripped
by the M2-CHR-515 prop grip on DEF-spear) instead of the brine-iron. A variant (stillguard_variants.json) sets the
build, the face sliders and the skin tone, cropped hair (moll_hair's cards, in its own colours) or a shaved head, the
open-face helm (sg_helm, over a crop it hides) and the weathered or clean atlases (sg_textures, write_materials).

The NPC budget (hadric_moll.md's LOD0 45k, LOD1 22k): no face subdivision (the villagers' head, the brows seated on the
shipped skin); every other step and every host snap (M2-CHR-11) is Moll's. Deterministic.

M3-CHR-540: a named Stillguard (sg_table.named(), Ivo Brannick) builds the same way, out to assets/characters/<id>/
under its own id; its table can drop the spear (`_variant.spear` false: the shield only, build_moll's `no_prop`) and
chip an upper front tooth (`_variant.broken_tooth`, broken_tooth below). M4-A2P-051: Warden Malcor Venn takes the
halberd (`_variant.halberd`, sg_halberd, on the spear's bone) and no shield (`_variant.shield` false), and keeps Moll's
sash (his `_costume`). The Abiding guard (Ch16, named `abiding_*`): the gold-lacquer kit under the helm with a veil
(sg_helm.veil, `_costume.veil`); the halberdiers and the captain take the halberd, the Bulwark casters Moll's own
brine-iron and shield (`_variant.iron`).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "moll"))

import build_moll as bm  # noqa: E402  (sets up the shared module path and Moll's tables, replaced below)
import moll_props  # noqa: E402
import sg_halberd  # noqa: E402
import sg_helm  # noqa: E402
from sg_table import TABLE, builds, name, variant_params  # noqa: E402
import toma_costume  # noqa: E402
import toma_props  # noqa: E402
import asha_mouth  # noqa: E402

SPEAR_BONE = "DEF-spear"
SPEAR_BONE_LEN = 0.30  # m, up the shaft from the grip (Toma's)
SPEAR_MAT = "spear"  # the shaft and its cord on the brine-iron's maps (ash, the red lacquer band)

bm.hb.MATERIALS.update({SPEAR_MAT: ((0.45, 0.36, 0.25), 0.5), "steel": ((0.10, 0.11, 0.12), 0.35)})
# LOD1 (the battle-scale read: the red shapes, the shield disc, the spear's line)
bm.hb.LOD1_RATIO.clear()
bm.hb.LOD1_RATIO.update({"Head": 0.4, "Body": 0.5, "Costume": 0.42, bm.SLEEVES: 0.45, "HairHead": 0.5, "Spear": 0.7,
                         "Shield": 0.6, "Helm": 0.5})


def spear(lm, cparams: dict):
    """Toma's spear in the right fist, built upright through the fist and turned into the held line (M2-CHR-515),
    its shaft and cord grip moved from Toma's atlas onto the brine-iron's maps (moll_props.IRON_ATLAS)."""
    return _on_iron_maps(toma_props.spear(lm, cparams, moll_props.IRON_ATLAS["band"]), lm)


def halberd(lm, cparams: dict):
    """M4-A2P-051: Malcor Venn's halberd (sg_halberd), held as the spear is and on the same bone and maps."""
    return _on_iron_maps(sg_halberd.halberd(lm, cparams, moll_props.IRON_ATLAS["band"]), lm)


def _on_iron_maps(part, lm):
    """A shafted prop's shaft and cord moved from Toma's atlas onto the brine-iron's maps; (part, mesh, bone, bone)."""
    su0, sv0, su1, sv1 = toma_costume.ATLAS["spear_shaft"]
    hu0, hv0, hu1, hv1 = moll_props.IRON_ATLAS["haft"]
    for k, m in enumerate(part.M):
        if m != "cloth":
            continue
        uv = part.UV[k]
        if all(su0 - 1e-9 <= u <= su1 + 1e-9 and sv0 - 1e-9 <= w <= sv1 + 1e-9 for u, w in uv):
            uv = tuple((hu0 + (u - su0) / (su1 - su0) * (hu1 - hu0), hv0 + (w - sv0) / (sv1 - sv0) * (hv1 - hv0))
                       for u, w in uv)
        part.UV[k] = uv
        part.M[k] = SPEAR_MAT
    part.name = "Spear"
    grip = toma_props.spear_grip(lm)
    return part, "Spear", SPEAR_BONE, (grip, grip + toma_props.spear_axis(lm) * SPEAR_BONE_LEN)


def broken_tooth(mouth_interior, share: float):
    """M3-CHR-540: asha_mouth.mouth_interior with the first upper incisor (the first tooth it lays: the central one on
    the +x side) chipped: its biting edge cut back on a slant, `share` of the crown's height at the midline edge and
    nothing at the outer edge (act1_ch08.md: "a broken front tooth"; act1_ch09.md B02: "showing a little")."""
    def build(lm, lip_line_y: float):
        part = mouth_interior(lm, lip_line_y)
        first = list(part.T).index(asha_mouth.TAG_TEETH_UP)
        n = (asha_mouth.TOOTH_FINE_NV - 1) * asha_mouth.TOOTH_FINE_NU + 2  # one fine tooth's vertices (two poles)
        tooth = np.array(part.V[first:first + n])
        x0, x1 = float(tooth[:, 0].min()), float(tooth[:, 0].max())
        z0, z1 = float(tooth[:, 2].min()), float(tooth[:, 2].max())
        for i in range(first, first + n):
            p = part.V[i]
            cut = z0 + share * (z1 - z0) * (1.0 - (float(p[0]) - x0) / (x1 - x0))
            if p[2] < cut:
                part.V[i] = np.array([p[0], p[1], cut])
        return part
    return build


def spec_for(v: str) -> dict:
    extra = variant_params(v)
    var = extra["_variant"]
    if var.get("broken_tooth"):
        asha_mouth.mouth_interior = broken_tooth(asha_mouth.mouth_interior, float(var["broken_tooth"]))
    # M4-A2P-051: Venn's halberd; `iron` keeps Moll's brine-iron (build_moll's own prop: the Abiding guard's casters)
    prop = halberd if var.get("halberd") else None if var.get("iron") else spear if var.get("spear", True) else None
    return {"name": name(v), "params": TABLE, "extra": extra, "subdiv_face": False,
            "hair": var["hair"] == "crop" and not var["helm"], "prop": prop,
            "no_prop": prop is None and not var.get("iron"),
            "no_shield": not var.get("shield", True), "helm": sg_helm.helm if var["helm"] else None}


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_stillguard.py")
    ap.add_argument("--variant", required=True, choices=builds())
    ap.add_argument("--out")
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--no-hair", action="store_true")
    args = ap.parse_args(argv)
    n = name(args.variant)
    args.out = args.out or str(ROOT / "assets" / "characters" / n / f"{n}.glb")
    return args


def main() -> int:
    args = parse_args()
    return bm.build(args, spec_for(args.variant))


if __name__ == "__main__":
    sys.exit(main())
