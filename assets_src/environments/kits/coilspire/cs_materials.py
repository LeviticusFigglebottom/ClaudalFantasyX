"""Writes the Coilspire temple kit's Godot materials (M3-ENV-10) from one table, so every value is in source.

    python3 assets_src/environments/kits/coilspire/cs_materials.py [--out assets/environments/kits/coilspire/materials]

One .tres per glTF slot the generators write (cs_common.SLOTS), so the import's `{asset_dir}/materials/` rule
and HalunaDresser both map slot -> material by name. Colours are palette.json hex or tones derived from it
(named beside each), inside the albedo floor/ceiling. The stone uses the shared env_weathering.gdshader with the
Corrow kit's laterite maps (the same stone as the wall and the far spire), the ground the Haluna kit's coral
stone and the Brine Shoals kit's mud, the copper the Tamsule Bell's env_bronze.gdshader with the Haluna detail
maps (all read-only). The writers are the Haluna kit's, loaded by path under their own module name.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
# The Haluna kit's material writers, read-only: loaded by path under their own name, so a sibling kit's
# `materials` module already in sys.modules is never picked up instead (corrow/cw_materials.py does the same).
_HM_SPEC = importlib.util.spec_from_file_location("haluna_materials", HERE.parent / "haluna" / "materials.py")
hm = sys.modules.get("haluna_materials") or importlib.util.module_from_spec(_HM_SPEC)
if "haluna_materials" not in sys.modules:
    sys.modules["haluna_materials"] = hm
    _HM_SPEC.loader.exec_module(hm)

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "coilspire" / "materials"
CTEX = "res://assets/environments/kits/corrow/textures/"
HTEX = "res://assets/environments/kits/haluna/textures/"
BTEX = "res://assets/environments/kits/brine_shoals/textures/"
WEATHER = "res://game/shaders/environment/env_weathering.gdshader"
BRONZE = "res://game/shaders/environment/env_bronze.gdshader"
hexc = hm.hexc

BASE = {
    "tex_detail": ("tex", HTEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "col_salt": hexc("#D8D4CA"),  # salt film, greyed by the storm light (Corrow's)
    "col_moss": hexc("#2B5529"),
    "col_lichen": hexc("#C08A3A"),
    "use_algae": False,
    "use_barnacles": False,
    "use_moss": False,
}


def weather(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(BASE)
    d.update({"tex_albedo": ("tex", albedo), "tex_normal": ("tex", normal),
              "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


BLOCKS = (CTEX + "laterite_blocks_albedo.png", CTEX + "laterite_blocks_normal.png")
STONE = (CTEX + "laterite_albedo.png", CTEX + "laterite_normal.png")
SALT_HIGH = "Vector2(-200.0, 200.0)"  # the spire stands 40 m up: its salt is the wind's film, everywhere, light

MATERIALS: dict[str, dict] = {
    # The spire's outer face and the hut: Corrow's coursed blocks by mesh UV in metres (u around, v height),
    # salt-dulled and wind-scoured, a little lichen in the lee (VC.R, use_moss for the lichen only).
    "cs_laterite": weather(*BLOCKS, (6.0, 1.0), base_triplanar=False, col_tint=hexc("#C9BAB0"), normal_strength=1.3,
                           roughness_base=0.86, specular_base=0.35, cavity_darken=0.45, ao_strength=0.8,
                           variation_value=0.12, variation_warmth=0.04, erosion_lighten=0.06, salt_band_m=SALT_HIGH,
                           salt_coverage="Vector2(0.14, 0.44)", col_paint=hexc("#8E8076"), paint_cover=0.22, use_moss=True,
                           moss_coverage=0.0,
                           lichen_coverage=0.35, moss_min_height_m=-200.0, wet_darken=0.5, wet_roughness=0.14),
    # The inner face: the same blocks, dry and smoke-dulled; its "salt" is copper salts, verdigris bloomed through
    # the wall where the flues pass behind it (VC.G: bronze_patina lightened, #6E9E8E).
    "cs_laterite_inner": weather(*BLOCKS, (6.0, 1.0), base_triplanar=False, col_tint=hexc("#D4C6BC"),
                                 normal_strength=1.4, roughness_base=0.9, specular_base=0.3, cavity_darken=0.55,
                                 ao_strength=0.9, variation_value=0.14, variation_warmth=0.05, erosion_lighten=0.04,
                                 col_salt=hexc("#6E9E8E"), salt_band_m=SALT_HIGH, salt_coverage="Vector2(0.0, 0.72)",
                                 salt_roughness=0.9, salt_cavity_gather=1.05),
    # Nine hundred years of beacon smoke: laterite toward lacquer_black warmed (#3A2A24), never black.
    "cs_laterite_sooted": weather(*BLOCKS, (6.0, 1.0), base_triplanar=False, col_tint=hexc("#9A8A80"),
                                  normal_strength=1.2, roughness_base=0.92, specular_base=0.25, cavity_darken=0.5,
                                  ao_strength=0.85, variation_value=0.16, erosion_lighten=0.08, use_salt=False),
    # Carved and dressed stone (the lintel, reveals, corbels, dais, treads, the path): jointless, paler where
    # worn (VC.A).
    "cs_laterite_carved": weather(*STONE, (0.9, 0.9), base_triplanar=True, col_tint=hexc("#D6C8BE"),
                                  col_paint=hexc("#8A7E76"), paint_cover=0.45,
                                  normal_strength=1.1, roughness_base=0.82, specular_base=0.38, cavity_darken=0.5,
                                  ao_strength=0.85, variation_value=0.08, erosion_lighten=0.12,
                                  erosion_pit_darken=0.25, salt_band_m=SALT_HIGH, salt_coverage="Vector2(0.1, 0.38)",
                                  use_moss=True, moss_coverage=0.3, lichen_coverage=0.35, moss_min_height_m=-200.0,
                                  moss_normal_y=0.75, wet_darken=0.5, wet_roughness=0.12),
    # Floors and landings: worn smooth by feet, dusted with soot.
    "cs_paving": weather(*STONE, (1.2, 1.2), base_triplanar=False, col_tint=hexc("#D8CABF"), normal_strength=1.0,
                         roughness_base=0.74, specular_base=0.42, cavity_darken=0.45, variation_value=0.12,
                         use_salt=False),
    # The headland's rock: the far piece's cw_headland (Haluna coral_stone darkened) at a closer tile.
    "cs_rock": weather(HTEX + "coral_stone_albedo.png", HTEX + "coral_stone_normal.png", (7.0, 7.0),
                       base_triplanar=True, col_tint=hexc("#4E4E56"), normal_strength=1.1, roughness_base=0.88,
                       cavity_darken=0.6, variation_value=0.15, salt_band_m="Vector2(0.5, 30.0)",
                       salt_coverage="Vector2(0.02, 0.12)", use_moss=True, moss_coverage=0.15, lichen_coverage=0.3,
                       moss_min_height_m=4.0, wet_darken=0.55, detail_scale_m=1.5),
    # Wind-burnt turf on the crest: the Brine Shoals mud tinted toward saltgrass dulled to olive (#7E7A48).
    "cs_turf": weather(BTEX + "mud_albedo.png", BTEX + "mud_normal.png", (2.5, 2.5), base_triplanar=True,
                       col_tint=hexc("#8C8862"), normal_strength=0.7,
                       roughness_base=0.92, cavity_darken=0.35, variation_value=0.12, variation_warmth=0.08,
                       use_salt=False, detail_scale_m=1.2),
    # The scrub's canopy: foliage_shadow toward palm_green, salt-burnt.
    "cs_scrub": weather(HTEX + "canopy_cluster_albedo.png", HTEX + "canopy_cluster_normal.png", (0.6, 0.6),
                        base_triplanar=True, col_tint=hexc("#6E8A62"), normal_strength=1.4, roughness_base=0.9,
                        cavity_darken=0.5, variation_value=0.18, variation_warmth=0.1, salt_band_m=SALT_HIGH,
                        salt_coverage="Vector2(0.0, 0.25)"),
    # The keeper's hut: the same blocks at half size (small, roughly coursed stones), lime-wash gone grey in
    # patches.
    "cs_rubble": weather(*BLOCKS, (3.0, 0.5), base_triplanar=False, col_tint=hexc("#C9BAB0"), col_paint=hexc("#9C968C"),
                         paint_cover=0.24, normal_strength=1.5, roughness_base=0.88, cavity_darken=0.5,
                         variation_value=0.16, salt_band_m=SALT_HIGH, salt_coverage="Vector2(0.05, 0.25)",
                         use_moss=True, moss_coverage=0.2, lichen_coverage=0.3, moss_min_height_m=-200.0),
    # The hut's door and lintel, the driftwood, the scrub's stems: sun-silvered timber_weathered.
    "cs_timber": weather(HTEX + "timber_albedo.png", HTEX + "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                         col_tint=hexc("#CFCDC8"), normal_strength=1.2, roughness_base=0.8, specular_base=0.3,
                         cavity_darken=0.45, variation_value=0.22, variation_warmth=0.03, salt_band_m=SALT_HIGH,
                         salt_coverage="Vector2(0.05, 0.2)"),
    # The flues and risers: dark copper under bronze_patina verdigris (VC.G), worn to bright copper where hands
    # and straps go (VC.A), rain streaks down the outside (VC.B).
    "cs_copper": {"shader": BRONZE, "params": {
        "tex_detail": ("tex", HTEX + "weathering_detail.png"),
        "tex_normal": ("tex", HTEX + "coral_concrete_normal.png"),
        "col_bronze": hexc("#5A3424"), "col_worn": hexc("#B4704A"),  # copper darkened / hair_copper toward brass
        "col_patina": hexc("#5F8A78"), "col_patina_pale": hexc("#7EA393"),  # bronze_patina / its bloom
        "col_grime": hexc("#272822"), "metallic_bronze": 0.85, "roughness_bronze": 0.5, "roughness_worn": 0.32,
        "patina_coverage": "Vector2(0.12, 0.95)", "patina_roughness": 0.85, "patina_shade_bias": 0.25,
        "streak_period_m": "Vector2(0.4, 5)", "streak_strength": 0.5, "detail_scale_m": 0.7,
        "normal_tile_m": 2.0, "normal_strength": 0.5, "wear_strength": 0.9, "ao_strength": 0.75}},
}

STANDARD: dict[str, dict] = {
    # Key rims and handles, rubbed bright: copper toward brass.
    "cs_copper_worn": {"albedo_color": hexc("#B07A4E"), "metallic": 0.85, "roughness": 0.35},
    # Wrought iron: the cage, the rail, the braziers, the basket.
    "cs_iron": {"albedo_color": hexc("#3A3230"), "metallic": 0.5, "roughness": 0.6},
    # Embers in the braziers and the hearth: ember_orange, a bed, not a flame.
    "cs_ember": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#E0702E"),
                 "emission_energy_multiplier": 2.5, "roughness": 0.9},
    # The beacon fire: the far piece's cw_beacon (ember_orange at 6).
    "cs_beacon": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#E0702E"),
                  "emission_energy_multiplier": 6.0, "roughness": 0.9},
    # Beyond the hut's window: deep shade above the albedo floor.
    "cs_interior_dark": {"albedo_color": hexc("#2A2622"), "roughness": 0.95},
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
