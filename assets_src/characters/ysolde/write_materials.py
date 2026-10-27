#!/usr/bin/env python3
"""Writes Ysolde's hero materials (assets/characters/ysolde/materials/*.tres) from one table.

    python3 assets_src/characters/ysolde/write_materials.py

Same writer and conventions as Asha's, Rhen's and Toma's (assets_src/characters/asha/write_materials.py): each
material's resource_name equals the glTF material name it replaces at load time (the hero stage), text resources,
deterministic. Ysolde's own maps come from ysolde_textures.py; the generic eye, hair, lash, brow and detail atlases
are Asha's (asha_textures.py), tinted here. Values follow ysolde.md §4-§7 and character_shading.md.
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
OUT = ROOT / "assets" / "characters" / "ysolde" / "materials"
T = "ysolde/textures/"
A = "asha/textures/"

# ysolde.md §5: hair_black #201A16, the primary tint #E0D8D0 at 0.35 and the secondary #6A4A36 at 0.4 (a cool ribbon
# highlight); grey strands #8C867D; the streak is ash: matte (#D6D2C8, the highlight off at 0.05, no secondary)
HAIR = "Color(0.125, 0.102, 0.086, 1)"  # #201A16 (the lashes and brows)
# the cards: hair_black read warm brown under the stage's orange key (as Asha's did before M1-CHR-10): the same cooler,
# deeper near-black her hair took (#141417)
HAIR_CARD = "Color(0.08, 0.08, 0.09, 1)"
HAIR_SPEC = "Color(0.878, 0.847, 0.816, 1)"  # #E0D8D0
HAIR_SPEC2 = "Color(0.416, 0.29, 0.212, 1)"  # #6A4A36
HAIR_TT = "Color(0.22, 0.18, 0.16, 1)"
GREY = "Color(0.549, 0.525, 0.49, 1)"  # #8C867D
ASH = "Color(0.839, 0.824, 0.784, 1)"  # #D6D2C8 (ash_white, proposed)
STILL = {"wind_response": "0.0"}  # pinned hair, lashes and brows: her hair is drawn up and knotted
HAIR_TEX = {"tex_hair": A + "asha_hair.png", "tex_hairflow": A + "asha_hairflow.png"}
HAIR_PARAMS = {"col_root": HAIR_CARD, "col_tip": HAIR_CARD, "col_spec_primary": HAIR_SPEC,
               "spec_primary_intensity": "0.35", "spec_primary_exponent": "300.0", "spec_shift_jitter": "0.3", "col_spec_secondary": HAIR_SPEC2,
               "spec_secondary_intensity": "0.4", "col_transmission": HAIR_TT, "transmission_strength": "0.3",
               "indirect_specular": "0.08", "root_occlusion": "0.65", "depth_occlusion": "0.7", "alpha_boost": "1.3",
               **STILL}
SKIN = {"tex_albedo": T + "ysolde_head_albedo.png", "tex_normal": T + "ysolde_head_normal.png",
        "tex_orm": T + "ysolde_head_orm.png", "tex_skin_mask": T + "ysolde_head_skinmask.png",
        "tex_detail_normal": A + "asha_skin_detail_normal.png"}
CLOTH = {"tex_albedo": T + "ysolde_cloth_albedo.png", "tex_normal": T + "ysolde_cloth_normal.png",
         "tex_orm": T + "ysolde_cloth_orm.png", "tex_cloth_mask": T + "ysolde_cloth_clothmask.png",
         "tex_detail_normal": A + "asha_thread_detail_normal.png"}
PROPS = {"tex_albedo": T + "ysolde_props_albedo.png", "tex_normal": T + "ysolde_props_normal.png",
         "tex_orm": T + "ysolde_props_orm.png", "tex_cloth_mask": T + "ysolde_props_clothmask.png",
         "tex_detail_normal": A + "asha_thread_detail_normal.png"}

SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # Asha's tuned skin response (M1-CHR-10); ysolde.md §6.1: a cooler indoor brown, 47 (a touch rougher)
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.85", "normal_strength": "1.0",
        "specular_scale": "0.75", "curvature_scale": "1.3", "roughness_min": "0.47", "roughness_max": "0.66",
        "cavity_albedo": "0.45", "micro_roughness": "0.1",
    }, SKIN),
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.8", "specular_scale": "0.75", "roughness_min": "0.47", "roughness_max": "0.66",
        "cavity_albedo": "0.45",
    }, SKIN),
    "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7"},
                  {"tex_albedo": T + "ysolde_body_albedo.png", "tex_normal": T + "ysolde_body_normal.png",
                   "tex_orm": T + "ysolde_body_orm.png", "tex_skin_mask": T + "ysolde_body_skinmask.png",
                   "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
    # ysolde.md §6.1: dark brown irises #2C1E16 with a cooler limbal ring #3E3430
    "eye": ("character_eye", 0, {"col_sclera": "Color(0.79, 0.735, 0.68, 1)", "limbus_softness": "0.09",
                                 "col_iris": "Color(0.173, 0.118, 0.086, 1)",
                                 "col_limbal": "Color(0.243, 0.204, 0.188, 1)"},
            {"tex_iris": A + "asha_iris.png", "tex_sclera": A + "asha_sclera.png"}),
    "cornea": ("character_cornea", 1, {}, {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "1.0", "corner_strength": "0.75"}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                   "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                   "indirect_specular": "0.03", "col_root": HAIR, "col_tip": HAIR, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    # thin, groomed brows (ysolde.md §6.1)
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.5",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                   "root_occlusion": "0.2", "indirect_specular": "0.05",
                                   "col_root": HAIR, "col_tip": HAIR, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    "hair": ("character_hair", 0, HAIR_PARAMS, HAIR_TEX),
    "hair_grey": ("character_hair", 0, {**HAIR_PARAMS, "col_root": GREY, "col_tip": GREY}, HAIR_TEX),
    "hair_streak": ("character_hair", 0, {**HAIR_PARAMS, "col_root": ASH, "col_tip": ASH,
                                          "spec_primary_intensity": "0.05", "spec_primary_exponent": "40.0",
                                          "spec_secondary_intensity": "0.0", "transmission_strength": "0.15",
                                          "indirect_specular": "0.02", "kajiya_diffuse_mix": "0.3",
                                          "strand_value_jitter": "0.08"}, HAIR_TEX),
    # the robe's heavy crepe (A 0.75 sheen), the collar's lacquered outside (B 0.5) and the gold script (G)
    "cloth": ("character_cloth", 0, {"detail_tiling": "150.0", "lacquer_base_roughness": "0.5",
                                     "lacquer_coat_roughness": "0.14", "lacquer_coat_strength": "0.5",
                                     "sheen_tint": "0.9", "sheen_intensity": "0.55", "gold_roughness": "0.3"},
              CLOTH),
    # ysolde.md §3: the book's and the guards' black lacquer (B 1.0) and their gold script and hairlines (G)
    "props": ("character_cloth", 0, {"detail_strength": "0.0", "sheen_intensity": "0.0",
                                     "lacquer_base_roughness": "0.4", "lacquer_coat_roughness": "0.06",
                                     "lacquer_coat_strength": "1.0", "gold_roughness": "0.25"}, PROPS),
    # M1-RND-21 / M1-RND-25: Asha's mouth family, same values, reading Ysolde's head atlas
    "teeth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
    }, {"tex_albedo": T + "ysolde_head_albedo.png", "tex_orm": T + "ysolde_head_orm.png"}),
    "tongue": ("character_mouth", 0, {
        "col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6", "specular": "0.25",
    }, {}),
    "mouth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "0.5", "roughness_from_orm": "0.0",
        "ao_light_affect": "0.5",
    }, {"tex_albedo": T + "ysolde_head_albedo.png", "tex_orm": T + "ysolde_head_orm.png"}),
}
STANDARD_MATERIALS = {
    # ysolde.md §7: `silver` #A9AEB3 (proposed): the Level-pin and the ink-guards' palm side
    "silver": "albedo_color = Color(0.663, 0.682, 0.702, 1)\nmetallic = 1.0\nroughness = 0.32\n",
    # gold_leaf #D4A437: the ring
    "gold": "albedo_color = Color(0.831, 0.643, 0.216, 1)\nmetallic = 1.0\nroughness = 0.3\n",
}
STANDARD_TEXTURES: dict[str, dict] = {}


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
