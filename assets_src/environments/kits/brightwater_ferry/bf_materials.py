"""Writes the Brightwater ferry kit's Godot materials (M3-ENV-08) from one table, so every value is in source.

    python3 assets_src/environments/kits/brightwater_ferry/bf_materials.py [--out assets/environments/kits/brightwater_ferry/materials]

One .tres per glTF slot the kit generators write (bf_common.M_*), so the import's `{asset_dir}/materials/` rule and
HalunaDresser both map slot -> material by name. Colours are palette.json hex or tones derived from it (named beside
each), inside the albedo floor/ceiling. Weathering materials use the shared env_weathering.gdshader (haluna.md §4
stack) with the Haluna kit's timber, woven-panel, coral and detail maps (read-only); the kit has no maps of its own.
The writers are the Haluna kit's, loaded by path under their own module name (tamsule_bell has a `materials`
module of its own).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
# the Haluna kit's material writers, read-only: loaded by path under its own name, so a sibling kit's `materials` module (tamsule_bell has one)
# already in sys.modules is never picked up instead.
_HM_SPEC = importlib.util.spec_from_file_location("haluna_materials", HERE.parent / "haluna" / "materials.py")
hm = sys.modules.get("haluna_materials") or importlib.util.module_from_spec(_HM_SPEC)
if "haluna_materials" not in sys.modules:
    sys.modules["haluna_materials"] = hm
    _HM_SPEC.loader.exec_module(hm)

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "brightwater_ferry" / "materials"
HTEX = "res://assets/environments/kits/haluna/textures/"
WEATHER = "res://game/shaders/environment/env_weathering.gdshader"
hexc = hm.hexc

BASE = {
    "tex_detail": ("tex", HTEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "col_algae": hexc("#3E4A2A"),
    "col_barnacle": hexc("#E6DAC0"),  # bone
    "col_salt": hexc("#E8E4D8"),
    "col_moss": hexc("#2B5529"),
    "col_lichen": hexc("#C08A3A"),
    "use_moss": False,  # no moss at sea
}


def weather(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(BASE)
    d.update({"tex_albedo": ("tex", albedo), "tex_normal": ("tex", normal), "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


TIMBER = (HTEX + "timber_albedo.png", HTEX + "timber_normal.png", (0.4, 1.6))
WOVEN = (HTEX + "woven_panel_albedo.png", HTEX + "woven_panel_normal.png", (0.25, 0.25))
CORAL = (HTEX + "coral_stone_albedo.png", HTEX + "coral_stone_normal.png")
CONCRETE = (HTEX + "coral_concrete_albedo.png", HTEX + "coral_concrete_normal.png")
DRY = {"use_algae": False, "use_barnacles": False}

MATERIALS: dict[str, dict] = {
    # The main deck: timber_weathered scrubbed pale (holystoned), salt in the grain, dry. Planks by mesh UV, so the
    # grain runs along each plank.
    "bf_deck": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#E2DCD0"), normal_strength=1.1, roughness_base=0.82,
                       specular_base=0.3, cavity_darken=0.4, variation_value=0.18, variation_warmth=0.04, **DRY,
                       salt_coverage="Vector2(0.05, 0.25)"),
    # Rails, posts, ladders, spars: oiled, warmer and a little glossier than the deck, worn pale on the edges (A).
    "bf_timber": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#D8C4AA"), normal_strength=1.2, roughness_base=0.62,
                         specular_base=0.42, cavity_darken=0.45, variation_value=0.2, variation_warmth=0.05,
                         erosion_lighten=0.1, **DRY, salt_coverage="Vector2(0.04, 0.18)"),
    # The hull below the wale and the coamings: tarred near-black brown (the Brine Shoals bs_timber_tar tone),
    # barnacles and weed at the waterline from the shader's height bands (the preview's water is the datum).
    "bf_timber_tar": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#5E544C"), normal_strength=1.3,
                             roughness_base=0.6, specular_base=0.4, cavity_darken=0.5, variation_value=0.14,
                             barnacle_coverage=0.4, algae_band_m="Vector2(-0.5, 0.25)",
                             algae_coverage="Vector2(0.4, 0.75)", salt_coverage="Vector2(0.05, 0.25)",
                             wet_roughness=0.08),
    # The topsides and the deckhouse dado: sea_blue_cloth paint over timber, salt-chalked, worn through on the edges.
    "bf_paint_blue": weather(*TIMBER, base_triplanar=False, col_paint=hexc("#3C78A8"), paint_cover=0.8, normal_strength=1.0,
                             roughness_base=0.66, specular_base=0.4, cavity_darken=0.35, variation_value=0.1, **DRY,
                             salt_coverage="Vector2(0.06, 0.3)"),
    # The deckhouse boards: mortar_white lime-wash greyed (#D2CCC0), so it stays under the foam's value.
    "bf_limewash": weather(*TIMBER[:2], (0.6, 2.0), base_triplanar=False, col_paint=hexc("#D2CCC0"), paint_cover=0.97,
                           normal_strength=0.2,
                           roughness_base=0.88, specular_base=0.3, cavity_darken=0.15, variation_value=0.08, **DRY,
                           salt_coverage="Vector2(0.03, 0.15)"),
    # The stem-gull: carved timber_weathered, the wear (A) lightening the crest and the beak.
    "bf_carved": weather(*TIMBER[:2], (0.25, 0.8), base_triplanar=True, col_tint=hexc("#CBBBA6"), normal_strength=1.0,
                         roughness_base=0.75, specular_base=0.35, cavity_darken=0.5, erosion_lighten=0.14, **DRY,
                         salt_coverage="Vector2(0.08, 0.3)"),
    # The main hatch's tarpaulin and the deckhouse roof: tarred canvas.
    "bf_tarpaulin": weather(*WOVEN, base_triplanar=False, col_paint=hexc("#3A342E"), paint_cover=0.85, normal_strength=0.9,
                            roughness_base=0.7, specular_base=0.35, variation_value=0.1, **DRY,
                            salt_coverage="Vector2(0.05, 0.25)"),
    "bf_rope": weather(*WOVEN[:2], (0.12, 0.12), base_triplanar=False, col_tint=hexc("#7A6448"), normal_strength=1.0,
                       roughness_base=0.95, **DRY, salt_coverage="Vector2(0.05, 0.2)"),
    # Water jars: unglazed clay toward roof_clay.
    "bf_earthenware": weather(*CONCRETE, (0.6, 0.6), base_triplanar=True, col_paint=hexc("#A85A3E"), paint_cover=0.86,
                              normal_strength=0.5, roughness_base=0.84, cavity_darken=0.3, variation_value=0.14, **DRY,
                              salt_coverage="Vector2(0.0, 0.12)"),
    # The drowned: silvered decks and tarred sides gone grey with salt, heavy barnacles and weed to the waterline.
    "bf_wreck_timber": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#A9A49C"), normal_strength=1.5,
                               roughness_base=0.86, specular_base=0.28, cavity_darken=0.55, variation_value=0.24,
                               erosion_lighten=0.06, barnacle_coverage=0.65, algae_band_m="Vector2(-0.6, 0.4)",
                               algae_coverage="Vector2(0.5, 0.9)", salt_coverage="Vector2(0.2, 0.55)",
                               wet_roughness=0.1),
    "bf_wreck_tar": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#4A4642"), normal_strength=1.5,
                            roughness_base=0.75, specular_base=0.32, cavity_darken=0.55, variation_value=0.16,
                            barnacle_coverage=0.75, algae_band_m="Vector2(-0.8, 0.5)", algae_coverage="Vector2(0.5, 0.9)",
                            salt_coverage="Vector2(0.15, 0.45)", wet_roughness=0.08),
    # Reef heads: dark wet coral toward volcanic_stone, weed and barnacles everywhere (awash at every swell).
    "bf_reef": weather(*CORAL, (1.6, 1.6), base_triplanar=True, col_tint=hexc("#6A6A68"), normal_strength=1.4,
                       roughness_base=0.8, cavity_darken=0.5, variation_value=0.18, barnacle_coverage=0.5,
                       algae_band_m="Vector2(-1.5, 0.3)", algae_coverage="Vector2(0.55, 0.9)",
                       salt_coverage="Vector2(0.0, 0.15)", wet_darken=0.5, wet_roughness=0.08, detail_scale_m=1.0),
    # M3-ENV-746: the islet's landing, the reef's rock lifted clear of the tide: paler, salted, the weed only
    # below the walk.
    "bf_islet_rock": weather(*CORAL, (1.6, 1.6), base_triplanar=True, col_tint=hexc("#A49E92"), normal_strength=1.3,
                             roughness_base=0.85, cavity_darken=0.45, variation_value=0.16, barnacle_coverage=0.25,
                             algae_band_m="Vector2(-1.6, -0.45)", algae_coverage="Vector2(0.5, 0.85)",
                             salt_coverage="Vector2(0.1, 0.4)", wet_darken=0.45, wet_roughness=0.08,
                             detail_scale_m=1.0),
}
# Cloth: the sails' sand_cloth, the reef band's sea_blue_cloth, the awning's faded_teal_cloth, the passengers'
# indigo, sand and deep-red bundles, the rotted rag on the drowned hull, and the baskets in thatch.
for _name, _hex, _cover in (("bf_canvas", "#C9B48E", 0.78), ("bf_canvas_blue", "#3C78A8", 0.8),
                            ("bf_canvas_awning", "#5E9A96", 0.8), ("bf_cloth_indigo", "#2B3A6B", 0.85),
                            ("bf_cloth_sand", "#C9B48E", 0.8), ("bf_cloth_red", "#7A1712", 0.85),
                            ("bf_wreck_canvas", "#6E6252", 0.82), ("bf_basket", "#B08A52", 0.7)):
    # Woven cloth reads as a fine weave (a small tile, a soft normal); the baskets and mats keep the coarse weave.
    _coarse = _name == "bf_basket"
    MATERIALS[_name] = weather(*WOVEN[:2], (0.25, 0.25) if _coarse else (0.07, 0.07), base_triplanar=False,
                               col_paint=hexc(_hex), paint_cover=_cover, normal_strength=0.9 if _coarse else 0.45,
                               roughness_base=0.92, specular_base=0.25, variation_value=0.12, variation_warmth=0.04,
                               **DRY, salt_coverage="Vector2(0.0, 0.15)")

# The Seventh Terrace (M3-ENV-08B; brightwater_ferry.md §7.3): copper sheathing on the bronze stack (the Tamsule
# bell's shader with copper colours: verdigris gathered low and in streaks, worn bright on edges) and the terrace
# sails' tanned cloth. Her lacquer is the Pemakar kit's (standard, clearcoated: below), as bf_lacquer_red is.
BRONZE = "res://game/shaders/environment/env_bronze.gdshader"


MATERIALS["bf_canvas_tan"] = weather(*WOVEN[:2], (0.07, 0.07), base_triplanar=False, col_paint=hexc("#A8865E"),
                                     paint_cover=0.8, normal_strength=0.45, roughness_base=0.92, specular_base=0.25,
                                     variation_value=0.12, variation_warmth=0.04, **DRY,
                                     salt_coverage="Vector2(0.0, 0.18)")  # sand_cloth toward sand_wet
MATERIALS["bf_copper_sheathing"] = {"shader": BRONZE, "params": {
    "tex_detail": ("tex", HTEX + "weathering_detail.png"),
    "tex_normal": ("tex", HTEX + "coral_concrete_normal.png"),
    "col_bronze": hexc("#8A4A26"), "col_worn": hexc("#A65A2A"),  # hair_copper darkened / hair_copper
    "col_patina": hexc("#5F8A78"), "col_patina_pale": hexc("#8DB3A2"),  # bronze_patina / its bloom
    "col_grime": hexc("#272822"), "metallic_bronze": 0.6, "roughness_bronze": 0.5, "roughness_worn": 0.32,
    "patina_coverage": "Vector2(0.1, 0.6)", "patina_roughness": 0.85, "patina_shade_bias": 0.3,
    "streak_period_m": "Vector2(0.4, 3)", "streak_strength": 0.5, "detail_scale_m": 1.2, "normal_tile_m": 1.6,
    "normal_strength": 0.4, "wear_strength": 0.8, "ao_strength": 0.75}}

STANDARD: dict[str, dict] = {
    # The wale's line and the stem-gull's beak: lacquer_red.
    "bf_lacquer_red": {"albedo_color": hexc("#B3261E"), "roughness": 0.3, "clearcoat_enabled": "true", "clearcoat": 0.5},
    # Chain-plates, davits, the lantern cages and hoods: wet rust-dark iron.
    "bf_iron": {"albedo_color": hexc("#4A3A30"), "metallic": 0.5, "roughness": 0.6},
    "bf_brass": {"albedo_color": hexc("#B08D57"), "metallic": 0.85, "roughness": 0.45},  # brass, salt-dulled
    # The lit lantern chimney: oil_lamp glass round the flame, the frame's hottest small value.
    "bf_lamp_glass": {"albedo_color": hexc("#FFB16E"), "emission_enabled": "true", "emission": hexc("#FFB16E"),
                      "emission_energy_multiplier": 4.0, "roughness": 0.15},
    # The deckhouse windows, lamp-lit from inside: oil_lamp through a horn pane, dimmer than a flame.
    "bf_window_glow": {"albedo_color": hexc("#E8A066"), "emission_enabled": "true", "emission": hexc("#FFB16E"),
                       "emission_energy_multiplier": 1.4, "roughness": 0.6},
    # The hold under the grating, the niche's shade: deep shade above the albedo floor.
    "bf_interior_dark": {"albedo_color": hexc("#2A2622"), "roughness": 0.95},
    # The Order niche's basin and plinth: order_marble, the only white stone aboard.
    "bf_marble": {"albedo_color": hexc("#E4DED3"), "roughness": 0.35, "metallic_specular": 0.6},
    # The Seventh Terrace: raw copper (the ingots, the pot, the name-board's band and brackets), the dead Lit Age
    # lamp-housing's ceramic, the crew's rice, and the Spar-Wraith's membrane (wet black, a hard sheen) with its seams
    # in spawn_wound (faint: the motes are VFX's).
    "bf_copper_bright": {"albedo_color": hexc("#A65A2A"), "metallic": 0.95, "roughness": 0.38},
    # Pemakar lacquer (pemakar_materials.py kit_lacquer_black, and lacquer_red_deep for the galley's dado).
    "bf_lacquer_black": {"albedo_color": hexc("#1D1916"), "roughness": 0.24, "clearcoat_enabled": "true",
                         "clearcoat": 0.6},
    # M4-A2P-1401 (the Lead's 10-30 Ch4 pass): the galley's board walls in a satin of the same black. The glossy
    # clearcoat caught the night sky on every board's rounded edge indoors (nothing occludes the sky reflection
    # there), a bright streak per board; the hull keeps its gloss.
    "bf_lacquer_black_satin": {"albedo_color": hexc("#1D1916"), "roughness": 0.55, "metallic_specular": 0.3},
    "bf_lacquer_red_deep": {"albedo_color": hexc("#7A1712"), "roughness": 0.26, "clearcoat_enabled": "true",
                            "clearcoat": 0.5},
    "bf_ceramic": {"albedo_color": hexc("#DCE3E0"), "roughness": 0.5, "metallic_specular": 0.5},
    "bf_rice": {"albedo_color": hexc("#E6DAC0"), "roughness": 0.8},
    "bf_membrane": {"albedo_color": hexc("#1D1916"), "roughness": 0.12, "metallic_specular": 0.7},
    "bf_spawn_wound": {"albedo_color": hexc("#3FE0C8"), "emission_enabled": "true", "emission": hexc("#3FE0C8"),
                       "emission_energy_multiplier": 1.2, "roughness": 0.3},
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
