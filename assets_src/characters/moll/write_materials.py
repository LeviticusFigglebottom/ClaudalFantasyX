#!/usr/bin/env python3
"""Writes Moll's hero materials (assets/characters/moll/materials/*.tres) from one table.

    python3 assets_src/characters/moll/write_materials.py

Same writer and conventions as the other heroes' (assets_src/characters/asha/write_materials.py): each material's
resource_name equals the glTF material name it replaces at load time (the hero stage, the characters import rule),
text resources, deterministic. Moll's own maps come from moll_textures.py; the generic eye, lash, brow and detail
atlases are Asha's and the cropped hair samples Toma's short-hair atlas (Toma's matte card shading), tinted here.
Values follow hadric_moll.md §3-§6 and character_shading.md: lacquer and gold leaf in the cloth's mask (G gold,
B lacquer), the white sash a matte linen; the iron blackened, its ember emission (`ember_dull`, a dull heat-tint on
the ring's lower third) at energy 0 until Ch6 raises it to EMBER_CH6.
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
OUT = ROOT / "assets" / "characters" / "moll" / "materials"
T = "moll/textures/"
A = "asha/textures/"
SHORT = "toma/textures/toma_shorthair.png"  # toma_textures.short_hair_atlas (strands along +V: no flow map)

# §5: dark brown, cropped, grey at the temples (the `hair_grey` cards); matte like Toma's crop
HAIR = "Color(0.18, 0.141, 0.11, 1)"  # #2E241C
HAIR_ROOT = "Color(0.13, 0.10, 0.08, 1)"
HAIR_TIP = "Color(0.20, 0.157, 0.12, 1)"
GREY_ROOT = "Color(0.52, 0.50, 0.47, 1)"
GREY_TIP = "Color(0.60, 0.585, 0.55, 1)"  # #9A958C
HAIR_SPEC = "Color(0.80, 0.76, 0.70, 1)"
HAIR_SPEC2 = "Color(0.32, 0.29, 0.26, 1)"
HAIR_TT = "Color(0.22, 0.17, 0.13, 1)"
STILL = {"wind_response": "0.0"}  # cropped hair, lashes and brows do not sway
# M2-CHR-524: at dialogue range the cards drew as near-black specks over the scalp paint. The paint between them is
# lit as skin, and the cards were darker in albedo (#111013) and darkened again by root and layer occlusion (0.7 x 0.75)
# meant for long hair's deep layers; cropped cards lie on the skin. The cards now sit near the paint's rendered value,
# so they add strand grain, not dots, and the grey cards are a thin veil (GREY_ALPHA) over the dark: salt-and-pepper
# reads as a lighter haze, not as pale chips.
CROP_AO = {"root_occlusion": "0.85", "depth_occlusion": "0.85"}
GREY_ALPHA = "0.45"  # alpha_boost of the grey cards: lower than Toma's 0.6, Moll's cards are twice as long and the
# temple grey is painted under them too (moll_textures.TEMPLE_GREY_PAINT)
FLAT = {"kajiya_diffuse_mix": "0.15", "diffuse_wrap": "0.3"}
CROP = {"flow_strength": "0.0", "col_spec_primary": HAIR_SPEC, "spec_primary_intensity": "0.07", **FLAT,
        "spec_primary_exponent": "60.0", "spec_secondary_intensity": "0.0", "col_spec_secondary": HAIR_SPEC2,
        "secondary_sparkle": "0.3", "col_transmission": HAIR_TT, "transmission_strength": "0.1",
        "indirect_specular": "0.05", **CROP_AO, "alpha_boost": "1.15",
        "strand_value_jitter": "0.12", **STILL}
SKIN = {"tex_albedo": T + "moll_head_albedo.png", "tex_normal": T + "moll_head_normal.png",
        "tex_orm": T + "moll_head_orm.png", "tex_skin_mask": T + "moll_head_skinmask.png",
        "tex_detail_normal": A + "asha_skin_detail_normal.png"}
EMBER = "Color(0.478, 0.165, 0.071, 1)"  # ember_dull #7A2A12 (proposed)
EMBER_CH6 = 0.15  # §3: the iron fresh from the brazier in Ch6 (the scene sets emission_energy_multiplier to this)

SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # Asha's tuned skin response (M1-CHR-10); §5: forties, weathered, a day's shadow (a little rougher)
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.9", "normal_strength": "1.0",
        "specular_scale": "0.72", "curvature_scale": "1.3", "roughness_min": "0.47", "roughness_max": "0.68",
        "cavity_albedo": "0.45", "micro_roughness": "0.1",
    }, SKIN),
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.85", "specular_scale": "0.72", "roughness_min": "0.47", "roughness_max": "0.68",
        "cavity_albedo": "0.45",
    }, SKIN),
    "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7"},
                  {"tex_albedo": T + "moll_body_albedo.png", "tex_normal": T + "moll_body_normal.png",
                   "tex_orm": T + "moll_body_orm.png", "tex_skin_mask": T + "moll_body_skinmask.png",
                   "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
    # grey-brown irises #3E3A34 (a tired, level gaze)
    "eye": ("character_eye", 0, {"col_sclera": "Color(0.78, 0.73, 0.68, 1)", "limbus_softness": "0.09",
                                 "col_iris": "Color(0.243, 0.227, 0.204, 1)",
                                 "col_limbal": "Color(0.15, 0.14, 0.12, 1)"},
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
                                   "col_root": HAIR, "col_tip": GREY_ROOT, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    "hair": ("character_hair", 0, {**CROP, "col_root": HAIR_ROOT, "col_tip": HAIR_TIP}, {"tex_hair": SHORT}),
    "hair_grey": ("character_hair", 0, {**CROP, "col_root": GREY_ROOT, "col_tip": GREY_TIP, "alpha_boost": GREY_ALPHA}, {"tex_hair": SHORT}),
    # the costume atlas: cotton, leather, linen; lacquer (B) and gold leaf (G) in the mask, bronze metal in the ORM
    "cloth": ("character_cloth", 0, {"detail_tiling": "140.0"},
              {"tex_albedo": T + "moll_cloth_albedo.png", "tex_normal": T + "moll_cloth_normal.png",
               "tex_orm": T + "moll_cloth_orm.png", "tex_cloth_mask": T + "moll_cloth_clothmask.png",
               "tex_detail_normal": A + "asha_thread_detail_normal.png"}),
    # §3: the shield's own set (lacquered face, the painted Level matte, the bronze rim metal)
    "shield": ("character_cloth", 0, {"detail_strength": "0.0", "sheen_intensity": "0.0"},
               {"tex_albedo": T + "moll_shield_albedo.png", "tex_normal": T + "moll_shield_normal.png",
                "tex_orm": T + "moll_shield_orm.png", "tex_cloth_mask": T + "moll_shield_clothmask.png",
                "tex_detail_normal": A + "asha_thread_detail_normal.png"}),
    # M1-RND-21: Asha's mouth family, same values, reading Moll's head atlas
    "teeth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
    }, {"tex_albedo": T + "moll_head_albedo.png", "tex_orm": T + "moll_head_orm.png"}),
    "tongue": ("character_mouth", 0, {
        "col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6", "specular": "0.25",
    }, {}),
    "mouth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "0.5", "roughness_from_orm": "0.0",
        "ao_light_affect": "0.5",
    }, {"tex_albedo": T + "moll_head_albedo.png", "tex_orm": T + "moll_head_orm.png"}),
}
STANDARD_MATERIALS = {
    # §3: the brine-iron's maps (ash, lacquer band, bronze ferrule, blackened iron); the ember is off by default
    "iron": "metallic = 1.0\nroughness = 1.0\nmetallic_texture_channel = 2\nroughness_texture_channel = 1\n"
            "normal_enabled = true\nemission_enabled = true\n"
            f"emission = {EMBER}\nemission_energy_multiplier = 0.0\nemission_operator = 1\n",
    # the shield's boss: bronze with a little patina (toma.md's bronze)
    "bronze": "albedo_color = Color(0.45, 0.36, 0.22, 1)\nmetallic = 0.85\nroughness = 0.48\n",
}
STANDARD_TEXTURES: dict[str, dict] = {
    "iron": {"albedo_texture": T + "moll_iron_albedo.png", "normal_texture": T + "moll_iron_normal.png",
             "metallic_texture": T + "moll_iron_orm.png", "roughness_texture": T + "moll_iron_orm.png",
             "emission_texture": T + "moll_iron_ember.png"},
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
