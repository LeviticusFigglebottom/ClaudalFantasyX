"""Writes the Pemakar kit's Godot materials (M3-ENV-03, pemakar.md §3 and §4) from one table.

    python3 assets_src/environments/kits/pemakar/pemakar_materials.py [--out assets/environments/kits/pemakar/materials]

Colours are palette.json hex (sRGB). The stone, brick, soil, thatch and timber slots use the shared
weathering shader (game/shaders/environment/env_weathering.gdshader) with the tide layers off and the salt
layer re-purposed as ash fall (pemakar.md §4: `col_salt` is the proposed `ash_fall` swatch, its height
band covers the whole mountain, and the kit writes ash into COLOR_0.g). The .tres writers are the Haluna
kit's (materials.py, read-only); material names match the glTF slots the generators write.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.append(str(HERE.parent / "haluna"))
# Haluna's .tres writers, read-only: loaded by path under its own name, so a sibling kit's `materials` module (tamsule_bell has one)
# already in sys.modules is never picked up instead.
_HM_SPEC = importlib.util.spec_from_file_location("haluna_materials", HERE.parent / "haluna" / "materials.py")
halmat = sys.modules.get("haluna_materials") or importlib.util.module_from_spec(_HM_SPEC)
if "haluna_materials" not in sys.modules:
    sys.modules["haluna_materials"] = halmat
    _HM_SPEC.loader.exec_module(halmat)

hexc = halmat.hexc
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "pemakar" / "materials"
TEX = "res://assets/environments/kits/pemakar/textures/"
HAL_TEX = "res://assets/environments/kits/haluna/textures/"
WEATHER = halmat.WEATHER
SPILL = halmat.SPILL
PLUME = "res://game/shaders/environment/env_ash_plume.gdshader"

ASH_FALL = "#8C8882"  # proposed palette swatch `ash_fall` (pemakar.md §3)

# The Pemakar weathering defaults: no tide layers; ash in the salt slot; moss and orange lichen kept.
PEMAKAR_BASE = {
    "tex_detail": ("tex", HAL_TEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "use_algae": False,
    "use_barnacles": False,
    "col_salt": hexc(ASH_FALL),
    "salt_band_m": "Vector2(-1000, 10000)",
    "salt_coverage": "Vector2(0.3, 0.75)",
    "salt_roughness": 0.95,
    "salt_cavity_gather": 0.5,
    "col_moss": hexc("#2B5529"),  # palm_green darkened 30 %
    "col_lichen": hexc("#C08A3A"),
    "moss_min_height_m": 0.0,
    "lichen_coverage": 0.1,
    "erosion_lighten": 0.04,
}


def stone(albedo: str, normal: str, tile: tuple[float, float], *, tex: str = TEX, **kw) -> dict:
    d = dict(PEMAKAR_BASE)
    d.update({"tex_albedo": ("tex", tex + albedo), "tex_normal": ("tex", tex + normal),
              "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


MATERIALS: dict[str, dict] = {
    # The stair-mountain's stone: neutral-cool and dark (the LUT keeps it so, color script ch05), ash on
    # every ledge, moss in the damp lower courses, a wide per-block value spread so fitted blocks read.
    "kit_volcanic_stone": stone("volcanic_stone_albedo.png", "volcanic_stone_normal.png", (1.0, 1.0),
                                base_triplanar=True, normal_strength=1.4, roughness_base=0.9, specular_base=0.35,
                                cavity_darken=0.4, ao_strength=0.8, variation_value=0.22, variation_warmth=0.02),
    "kit_volcanic_dressed": stone("volcanic_stone_albedo.png", "volcanic_stone_normal.png", (0.7, 0.7),
                                  base_triplanar=True, col_tint="Color(1.12, 1.12, 1.14, 1)", normal_strength=0.8,
                                  roughness_base=0.82, specular_base=0.4, cavity_darken=0.25, ao_strength=0.7,
                                  variation_value=0.12, variation_warmth=0.02, erosion_pit_darken=0.15),
    "kit_volcanic_far": stone("volcanic_stone_albedo.png", "volcanic_stone_normal.png", (8.0, 8.0),
                              base_triplanar=True, normal_strength=0.5, roughness_base=0.92, cavity_darken=0.2,
                              ao_strength=0.5, variation_value=0.08, detail_scale_m=6.0, moss_coverage=0.85,
                              moss_normal_y=0.35, moss_north_facing=0.2,
                              # the PC's pass 7 row 80: the macro layer breaks the far slopes up (env_weathering)
                              macro_strength=0.85, macro_scale_m=36.0),
    "kit_laterite_brick": stone("laterite_brick_albedo.png", "laterite_brick_normal.png", (1.0, 1.0),
                                base_triplanar=True, normal_strength=1.1, roughness_base=0.86, specular_base=0.35,
                                cavity_darken=0.35, ao_strength=0.7, variation_value=0.1, use_moss=False,
                                salt_coverage="Vector2(0.15, 0.5)"),
    "kit_laterite_tile": stone("laterite_brick_albedo.png", "laterite_brick_normal.png", (0.5, 0.5),
                               base_triplanar=True, normal_strength=0.7, roughness_base=0.75, use_moss=False),
    "kit_ash_soil": stone("ash_soil_albedo.png", "ash_soil_normal.png", (2.0, 2.0), base_triplanar=True,
                          normal_strength=1.0, roughness_base=0.95, specular_base=0.3, cavity_darken=0.3,
                          ao_strength=0.6, variation_value=0.06, moss_normal_y=0.5, moss_coverage=0.5,
                          salt_coverage="Vector2(0.25, 0.8)", salt_cavity_gather=0.2),
    "kit_fibre_thatch": stone("fibre_thatch_albedo.png", "fibre_thatch_normal.png", (1.6, 1.6),
                              base_triplanar=False, normal_strength=1.6, roughness_base=0.95, specular_base=0.2,
                              cavity_darken=0.4, variation_value=0.12, use_moss=False,
                              salt_coverage="Vector2(0.3, 0.7)"),
    # Smoked dark timber: the Haluna grain, tinted down toward timber_weathered x 0.7.
    "kit_timber_dark": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), tex=HAL_TEX, base_triplanar=True,
                             triplanar_sharpness=6.0, col_tint="Color(0.6, 0.55, 0.52, 1)", normal_strength=1.0,
                             roughness_base=0.82, specular_base=0.3, cavity_darken=0.4, variation_value=0.15,
                             use_moss=False, salt_coverage="Vector2(0.15, 0.5)"),
    "kit_plume": {"shader": PLUME, "params": {}},
    "kit_water_spill": {"shader": SPILL, "params": {"col_water": hexc("#7C9DA0"), "col_foam": hexc("#C5C8C7"),
                                                    "opacity": 0.5, "emission_energy": 0.0, "fall_speed_m_s": 2.2}},
}

STANDARD: dict[str, dict] = {
    "kit_copper_vein": {"albedo_color": hexc("#5F8A78"), "metallic": 0.35, "roughness": 0.55},  # bronze_patina
    "kit_copper_raw": {"albedo_color": hexc("#A65A2A"), "metallic": 1.0, "roughness": 0.35},  # hair_copper
    "kit_iron": {"albedo_color": hexc("#2A2624"), "metallic": 0.6, "roughness": 0.6},
    "kit_lacquer_red": {"albedo_color": hexc("#B3261E"), "roughness": 0.22, "clearcoat_enabled": "true",
                        "clearcoat": 0.6},
    "kit_lacquer_black": {"albedo_color": hexc("#1D1916"), "roughness": 0.2, "clearcoat_enabled": "true",
                          "clearcoat": 0.7},
    "kit_gold_leaf": {"albedo_color": hexc("#D4A437"), "roughness": 0.28, "metallic": 1.0},
    # The channels and paddies are dark mirrors (abyss_navy albedo) for the flames and the sky.
    "kit_channel_water": {"albedo_color": hexc("#061A2B"), "roughness": 0.04, "metallic_specular": 0.6},
    "kit_paddy_water": {"albedo_color": hexc("#061A2B"), "roughness": 0.07, "metallic_specular": 0.55},
    "kit_leaf_boat": {"albedo_color": hexc("#5E7F35"), "roughness": 0.55, "cull_mode": 2,
                      "backlight_enabled": "true", "backlight": "Color(0.35, 0.45, 0.12, 1)"},
    "kit_rice": {"albedo_color": hexc("#E6DAC0"), "roughness": 0.75},
    "kit_rice_stubble": {"albedo_color": hexc("#8F8A4E"), "roughness": 0.85, "cull_mode": 2},
    "kit_frangipani_offering": {"albedo_color": hexc("#F0E8D8"), "roughness": 0.5, "cull_mode": 2},
    # Oil flame (oil_lamp, ~2,900 K): the only warm practical light, and the brightest value in a frame.
    "kit_wick_flame": {"albedo_color": hexc("#FFB16E"), "emission_enabled": "true", "emission": hexc("#FFB16E"),
                       "emission_energy_multiplier": 10.0, "roughness": 1.0, "shading_mode": 0},
    "kit_forge_glow": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#E0702E"),
                       "emission_energy_multiplier": 3.0, "roughness": 1.0},
    "kit_soot": {"albedo_color": hexc("#1D1916"), "roughness": 0.95},
    "kit_interior_dark": {"albedo_color": hexc("#2B2622"), "roughness": 1.0},
    # A lamp-lit room seen through a door or window at night (the preview swaps it in per house).
    "kit_interior_lit": {"albedo_color": hexc("#2B2622"), "roughness": 1.0, "emission_enabled": "true",
                         "emission": hexc("#FFA757"), "emission_energy_multiplier": 0.22},
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in sorted(MATERIALS.items()):
        halmat.write_shader_material(out / f"{name}.tres", name, spec)
    for name, spec in sorted(STANDARD.items()):
        halmat.write_standard_material(out / f"{name}.tres", name, spec)
    print(f"KIT_MAT {len(MATERIALS) + len(STANDARD)} materials -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
