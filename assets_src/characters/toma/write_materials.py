#!/usr/bin/env python3
"""Writes Toma's hero materials (assets/characters/toma/materials/*.tres) from one table.

    python3 assets_src/characters/toma/write_materials.py

Same writer and conventions as Asha's and Rhen's (assets_src/characters/asha/write_materials.py):
each material's resource_name equals the glTF material name it replaces at load time (the hero
stage), text resources, deterministic. Toma's own maps come from toma_textures.py; the generic eye,
hair, lash, brow and detail atlases are Asha's (asha_textures.py), tinted here. Values follow
toma.md §4-§7 and character_shading.md.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Asha's writer, loaded by path (this file has the same name, so a plain import would find itself)
_spec = importlib.util.spec_from_file_location("asha_write_materials", HERE.parent / "asha" / "write_materials.py")
wm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wm)

ROOT = HERE.parents[2]
OUT = ROOT / "assets" / "characters" / "toma" / "materials"
T = "toma/textures/"
A = "asha/textures/"

# toma.md §5: hair_black, cropped and matte: the primary highlight #D8CCC0 at a low 0.25
HAIR = "Color(0.125, 0.102, 0.086, 1)"  # #201A16
GREY = "Color(0.541, 0.518, 0.471, 1)"  # #8A8478, the grey at the chin
HAIR_SPEC = "Color(0.847, 0.80, 0.753, 1)"  # #D8CCC0
STILL = {"wind_response": "0.0"}  # cropped hair, beard, lashes and brows do not sway
SKIN = {"tex_albedo": T + "toma_head_albedo.png", "tex_normal": T + "toma_head_normal.png",
        "tex_orm": T + "toma_head_orm.png", "tex_skin_mask": T + "toma_head_skinmask.png",
        "tex_detail_normal": A + "asha_skin_detail_normal.png"}
BEARD = {"flow_strength": "0.0", "col_root": HAIR, "col_tip": HAIR, "col_spec_primary": HAIR_SPEC,
         "spec_primary_intensity": "0.12", "spec_primary_exponent": "90.0", "spec_secondary_intensity": "0.08",
         "transmission_strength": "0.15", "indirect_specular": "0.04", "root_occlusion": "0.55",
         "depth_occlusion": "0.6", "alpha_boost": "1.15", **STILL}

SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # Asha's tuned skin response (M1-CHR-10); toma.md §6: deep bronze, weathered (a little rougher)
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.9", "normal_strength": "1.0",
        "specular_scale": "0.75", "curvature_scale": "1.3", "roughness_min": "0.46", "roughness_max": "0.66",
        "cavity_albedo": "0.45", "micro_roughness": "0.1",
    }, SKIN),
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.8", "specular_scale": "0.75", "roughness_min": "0.46", "roughness_max": "0.66",
        "cavity_albedo": "0.45",
    }, SKIN),
    "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7"},
                  {"tex_albedo": T + "toma_body_albedo.png", "tex_normal": T + "toma_body_normal.png",
                   "tex_orm": T + "toma_body_orm.png", "tex_skin_mask": T + "toma_body_skinmask.png",
                   "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
    # toma.md §6: steady, large irises #2A1A10
    "eye": ("character_eye", 0, {"col_sclera": "Color(0.79, 0.735, 0.68, 1)", "limbus_softness": "0.09",
                                 "col_iris": "Color(0.165, 0.102, 0.063, 1)",
                                 "col_limbal": "Color(0.20, 0.13, 0.08, 1)"},
            {"tex_iris": A + "asha_iris.png", "tex_sclera": A + "asha_sclera.png"}),
    "cornea": ("character_cornea", 1, {}, {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "1.0", "corner_strength": "0.75"}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                   "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                   "indirect_specular": "0.03", "col_root": HAIR, "col_tip": HAIR, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.7",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                   "root_occlusion": "0.2", "indirect_specular": "0.05",
                                   "col_root": HAIR, "col_tip": HAIR, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    "hair": ("character_hair", 0, {"col_root": HAIR, "col_tip": HAIR, "col_spec_primary": HAIR_SPEC,
                                   "spec_primary_intensity": "0.14", "spec_primary_exponent": "90.0",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.15",
                                   "indirect_specular": "0.06", "root_occlusion": "0.6", "depth_occlusion": "0.65",
                                   "alpha_boost": "1.6", **STILL},
             {"tex_hair": A + "asha_hair.png", "tex_hairflow": A + "asha_hairflow.png"}),
    "beard": ("character_hair", 0, BEARD, {"tex_hair": A + "asha_hair.png"}),
    "beard_grey": ("character_hair", 0, {**BEARD, "col_root": GREY, "col_tip": GREY},
                   {"tex_hair": A + "asha_hair.png"}),
    "cloth": ("character_cloth", 0, {"detail_tiling": "140.0"},
              {"tex_albedo": T + "toma_cloth_albedo.png", "tex_normal": T + "toma_cloth_normal.png",
               "tex_orm": T + "toma_cloth_orm.png", "tex_cloth_mask": T + "toma_cloth_clothmask.png",
               "tex_detail_normal": A + "asha_thread_detail_normal.png"}),
    # toma.md §4 #7: the shield's own set (scutes lacquered at 0.7, the rim at 1.0 in the mask)
    "shield": ("character_cloth", 0, {"detail_strength": "0.0", "sheen_intensity": "0.0"},
               {"tex_albedo": T + "toma_shield_albedo.png", "tex_normal": T + "toma_shield_normal.png",
                "tex_orm": T + "toma_shield_orm.png", "tex_cloth_mask": T + "toma_shield_clothmask.png",
                "tex_detail_normal": A + "asha_thread_detail_normal.png"}),
}
STANDARD_MATERIALS = {
    # Asha's mouth family (M1-CHR-10/11), reading Toma's head atlas
    "teeth": "albedo_color = Color(1, 1, 1, 1)\nroughness = 1.0\nroughness_texture_channel = 1\n"
             "metallic_specular = 0.06\nao_enabled = true\nao_light_affect = 0.35\nao_texture_channel = 0\n",
    "tongue": "albedo_color = Color(0.55, 0.26, 0.25, 1)\nroughness = 0.6\nmetallic_specular = 0.25\n",
    "mouth": "albedo_color = Color(0.28, 0.10, 0.09, 1)\nroughness = 0.5\nao_enabled = true\n"
             "ao_light_affect = 0.5\nao_texture_channel = 0\n",
    # toma.md §4: bronze_patina buckles and boss (#5F8A78 patina over bronze: a dull green-bronze metal)
    "bronze": "albedo_color = Color(0.45, 0.42, 0.30, 1)\nmetallic = 0.85\nroughness = 0.5\n",
    # toma.md §4 #8: the spear's steel #5A6066
    "steel": "albedo_color = Color(0.353, 0.376, 0.40, 1)\nmetallic = 1.0\nroughness = 0.38\n",
}
STANDARD_TEXTURES = {
    "teeth": {"albedo_texture": T + "toma_head_albedo.png", "roughness_texture": T + "toma_head_orm.png",
              "ao_texture": T + "toma_head_orm.png"},
    "mouth": {"ao_texture": T + "toma_head_orm.png"},
}


def main() -> int:
    wm.OUT = OUT
    wm.TEX = "res://assets/characters"
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (shader, prio, params, textures) in SHADER_MATERIALS.items():
        wm.write_shader_material(name, shader, prio, params, textures)
    for name, body in STANDARD_MATERIALS.items():
        wm.write_standard_material(name, body, STANDARD_TEXTURES.get(name, {}))
    print(f"wrote {len(SHADER_MATERIALS) + len(STANDARD_MATERIALS)} materials to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
