"""Writes the Corrow seawall kit's Godot materials (M3-ENV-04) from one table, so every value is in source.

    python3 assets_src/environments/kits/corrow/cw_materials.py [--out assets/environments/kits/corrow/materials]

One .tres per glTF slot the kit generators write (cw_common.M_*), so the import's `{asset_dir}/materials/`
rule and HalunaDresser both map slot -> material by name. Colours are palette.json hex or tones derived
from it (named beside each), inside the albedo floor/ceiling. Weathering materials use the shared
env_weathering.gdshader (haluna.md §4 stack) with this kit's laterite maps, the Haluna kit's timber,
woven-panel, coral, roof-tile and detail maps and the Brine Shoals kit's mud and shingle maps (all
read-only). The writers are the Haluna kit's.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
import materials as hm  # noqa: E402  (the Haluna kit's material writers, read-only)

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "corrow" / "materials"
TEX = "res://assets/environments/kits/corrow/textures/"
HTEX = "res://assets/environments/kits/haluna/textures/"
BTEX = "res://assets/environments/kits/brine_shoals/textures/"
WEATHER = "res://game/shaders/environment/env_weathering.gdshader"
hexc = hm.hexc

BASE = {
    "tex_detail": ("tex", HTEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "col_algae": hexc("#3E4A2A"),  # a dark storm-coast weed film
    "col_barnacle": hexc("#E6DAC0"),  # bone
    "col_salt": hexc("#D8D4CA"),  # salt crust, greyed by the storm light
    "col_moss": hexc("#2B5529"),
    "col_lichen": hexc("#C08A3A"),
    "use_moss": False,
}


def weather(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(BASE)
    d.update({"tex_albedo": ("tex", albedo), "tex_normal": ("tex", normal), "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


BLOCKS = (TEX + "laterite_blocks_albedo.png", TEX + "laterite_blocks_normal.png")
STONE = (TEX + "laterite_albedo.png", TEX + "laterite_normal.png")
TIMBER = (HTEX + "timber_albedo.png", HTEX + "timber_normal.png", (0.4, 1.6))
WOVEN = (HTEX + "woven_panel_albedo.png", HTEX + "woven_panel_normal.png", (0.25, 0.25))

MATERIALS: dict[str, dict] = {
    # The wall: coursed laterite by mesh UV in metres (u along the wall, v = height), so the texture's
    # courses sit on the geometry's joints and its blocks follow the curve. Salt in the spray band, a
    # weed film and barnacles at the tide line, wet low on the sea face (VC.B and the live wet line).
    "cw_laterite": weather(*BLOCKS, (6.0, 1.0), base_triplanar=False, col_tint=hexc("#D2C2B6"), normal_strength=1.3,
                           roughness_base=0.86,
                           specular_base=0.35, cavity_darken=0.45, ao_strength=0.8, variation_value=0.12,
                           variation_warmth=0.04, erosion_lighten=0.06, salt_band_m="Vector2(0.8, 9.0)",
                           salt_coverage="Vector2(0.12, 0.42)", algae_band_m="Vector2(-0.6, 2.4)",
                           algae_coverage="Vector2(0.45, 0.85)", barnacle_band_m="Vector2(-0.8, 0.8)",
                           barnacle_coverage=0.45, wet_darken=0.5, wet_roughness=0.12, capillary_band_m=0.5),
    # The courses rebuilt after the last Risings: the same blocks, fresher (no grey skin yet, less salt).
    "cw_laterite_rebuilt": weather(*BLOCKS, (6.0, 1.0), base_triplanar=False, col_tint=hexc("#F6E2D4"),
                                   normal_strength=1.4, roughness_base=0.84, specular_base=0.35, cavity_darken=0.45,
                                   ao_strength=0.8, variation_value=0.1, variation_warmth=0.05, erosion_lighten=0.03,
                                   salt_band_m="Vector2(0.8, 9.0)", salt_coverage="Vector2(0.04, 0.2)",
                                   algae_band_m="Vector2(-0.6, 2.4)", algae_coverage="Vector2(0.35, 0.7)",
                                   barnacle_band_m="Vector2(-0.8, 0.8)", barnacle_coverage=0.3, wet_darken=0.5,
                                   wet_roughness=0.12, capillary_band_m=0.5),
    # The Watchers and the stair's treads: the same stone without joints, a shade paler (the carving
    # weathered smooth), the wear (VC.A) lightening the brows, noses and lips.
    "cw_laterite_carved": weather(*STONE, (0.8, 0.8), base_triplanar=False, col_tint=hexc("#F2E6DC"),
                                  normal_strength=1.1, roughness_base=0.82, specular_base=0.38, cavity_darken=0.5,
                                  ao_strength=0.85, variation_value=0.06, erosion_lighten=0.12,
                                  erosion_pit_darken=0.25, salt_band_m="Vector2(0.8, 9.0)",
                                  salt_coverage="Vector2(0.1, 0.35)", algae_band_m="Vector2(-0.6, 0.5)",
                                  algae_coverage="Vector2(0.45, 0.85)", barnacle_coverage=0.4, wet_darken=0.5,
                                  wet_roughness=0.12),
    # The walk's slabs (1.2 x 1.0 m; their joints are the geometry's grooves, so the stone is the jointless
    # map): worn darker and smoother by feet; wet in the dishes (VC.B), near-mirror there so the walk
    # carries the storm sky.
    "cw_paving": weather(*STONE, (1.2, 1.2), base_triplanar=False, col_tint=hexc("#D8CCC4"), normal_strength=1.0,
                         roughness_base=0.7, specular_base=0.45, cavity_darken=0.4, variation_value=0.12,
                         use_algae=False, use_barnacles=False, salt_coverage="Vector2(0.05, 0.25)",
                         wet_darken=0.55, wet_roughness=0.06, wet_flatten=0.8),
    # Rip-rap and the far headland: dark weathered stone among the laterite blocks.
    "cw_rubble": weather(*STONE, (1.2, 1.2), base_triplanar=True, col_tint=hexc("#6E6660"), normal_strength=1.4,
                         roughness_base=0.82, cavity_darken=0.5, variation_value=0.2, barnacle_coverage=0.6,
                         algae_band_m="Vector2(-1.0, 0.6)", algae_coverage="Vector2(0.5, 0.9)",
                         salt_coverage="Vector2(0.1, 0.35)", wet_darken=0.5, wet_roughness=0.1),
    "cw_headland": weather(HTEX + "coral_stone_albedo.png", HTEX + "coral_stone_normal.png", (18.0, 18.0),
                           base_triplanar=True, col_tint=hexc("#5A5A62"), normal_strength=1.0, roughness_base=0.88,
                           cavity_darken=0.4, variation_value=0.15, use_barnacles=False, algae_coverage="Vector2(0.4, 0.8)",
                           salt_coverage="Vector2(0.05, 0.25)", wet_darken=0.55, detail_scale_m=4.0),
    # The low town: packed earth (the Brine Shoals mud, drier and warmer) and worn cobbles (its shingle).
    "cw_earth": weather(BTEX + "mud_albedo.png", BTEX + "mud_normal.png", (3.0, 3.0), base_triplanar=True,
                        col_tint=hexc("#E2D2BE"), normal_strength=0.5, roughness_base=0.86, cavity_darken=0.3,
                        variation_value=0.06, use_algae=False, use_barnacles=False,
                        salt_coverage="Vector2(0.0, 0.12)", wet_darken=0.6, wet_roughness=0.06, wet_flatten=0.8,
                        detail_scale_m=1.2),
    "cw_cobble": weather(BTEX + "shingle_albedo.png", BTEX + "shingle_normal.png", (1.4, 1.4), base_triplanar=True,
                         col_tint=hexc("#A89888"), normal_strength=1.1, roughness_base=0.78, cavity_darken=0.45,
                         variation_value=0.06, use_algae=False, use_barnacles=False,
                         salt_coverage="Vector2(0.0, 0.1)", wet_darken=0.6, wet_roughness=0.08),
    # Fishers' houses: rubble laterite with old lime-wash patches gone grey (mortar_white at low cover).
    "cw_house_stone": weather(*STONE, (1.0, 1.0), base_triplanar=True, col_tint=hexc("#D8C8BC"), col_paint=hexc("#B4AEA4"),
                              paint_cover=0.2,
                              normal_strength=1.3, roughness_base=0.88, cavity_darken=0.45, variation_value=0.16,
                              use_barnacles=False, use_algae=False, salt_coverage="Vector2(0.05, 0.2)"),
    # The roofs' lime-mortar ridges and hips, gone grey with salt and smoke (no brighter than the foam).
    "cw_mortar": weather(HTEX + "coral_stone_albedo.png", HTEX + "coral_stone_normal.png", (0.8, 0.8),
                         base_triplanar=True, col_paint=hexc("#A49C90"), paint_cover=0.85, normal_strength=0.8,
                         roughness_base=0.9, use_algae=False, use_barnacles=False, use_salt=False),
    "cw_roof_tile": weather(HTEX + "roof_tile_albedo.png", HTEX + "roof_tile_normal.png", (2.0, 2.4),
                            base_triplanar=False, col_tint=hexc("#E2D0C8"), normal_strength=1.0, roughness_base=0.6,
                            specular_base=0.45, cavity_darken=0.25, use_algae=False, use_barnacles=False,
                            salt_coverage="Vector2(0.05, 0.2)", wet_roughness=0.15),
    # Lintels, shutters and Liss's spar: sun-silvered timber_weathered; tarred hemp rope.
    "cw_timber": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#CFCDC8"), normal_strength=1.2,
                         roughness_base=0.8, specular_base=0.3, cavity_darken=0.45, variation_value=0.22,
                         variation_warmth=0.03, use_algae=False, use_barnacles=False,
                         salt_coverage="Vector2(0.05, 0.2)"),
    "cw_rope": weather(*WOVEN[:2], (0.12, 0.12), base_triplanar=False, col_tint=hexc("#6E5A44"), normal_strength=1.0,
                       roughness_base=0.92, use_algae=False, use_barnacles=False, salt_coverage="Vector2(0.05, 0.2)"),
}

STANDARD: dict[str, dict] = {
    # Wet rust-dark iron: the hand-line stanchions, the hoist's straps, bolts and shoe.
    "cw_iron": {"albedo_color": hexc("#4A3A30"), "metallic": 0.55, "roughness": 0.55},
    # Doorways and windows: deep shade, above the albedo floor.
    "cw_interior_dark": {"albedo_color": hexc("#2A2622"), "roughness": 0.95},
    # The Coilspire's flues: bronze_patina green-cyan.
    "cw_copper": {"albedo_color": hexc("#5F8A78"), "metallic": 0.35, "roughness": 0.6},
    # The beacon fire: ember_orange, the frame's warm accent at 480 m (colour script ch08).
    "cw_beacon": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#E0702E"),
                  "emission_energy_multiplier": 6.0, "roughness": 0.9},
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in sorted(MATERIALS.items()):
        hm.write_shader_material(out / f"{name}.tres", name, spec)
    for name, spec in sorted(STANDARD.items()):
        hm.write_standard_material(out / f"{name}.tres", name, spec)
    print(f"KIT_MAT {len(MATERIALS) + len(STANDARD)} materials -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
