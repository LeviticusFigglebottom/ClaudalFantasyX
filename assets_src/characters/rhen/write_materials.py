#!/usr/bin/env python3
"""Writes Rhen's hero materials (assets/characters/rhen/materials/*.tres) from one table.

    python3 assets_src/characters/rhen/write_materials.py

Same writer and conventions as Asha's (assets_src/characters/asha/write_materials.py): each
material's resource_name equals the glTF material name it replaces at load time (AshaStage /
the hero stage), text resources, deterministic. Rhen's own maps come from rhen_textures.py; the
generic eye, hair, lash, brow and detail atlases are Asha's (asha_textures.py), tinted here.
Values follow rhen.md §4-§7 and character_shading.md.
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
OUT = ROOT / "assets" / "characters" / "rhen" / "materials"
R = "rhen/textures/"
A = "asha/textures/"

# rhen.md §5: dark-brown roots (#2E1E14) bleaching to sun-bleached copper (#A65A2A) over the outer
# 40% of each strand; the secondary highlight carries the copper so the tips glow in backlight.
HAIR_ROOT = "Color(0.18, 0.118, 0.078, 1)"  # #2E1E14
HAIR_TIP = "Color(0.651, 0.353, 0.165, 1)"  # #A65A2A
HAIR_SPEC_PRIMARY = "Color(0.941, 0.847, 0.722, 1)"  # #F0D8B8
HAIR_SPEC_SECONDARY = "Color(0.784, 0.416, 0.188, 1)"  # #C86A30
SKIN = {"tex_albedo": R + "rhen_head_albedo.png", "tex_normal": R + "rhen_head_normal.png",
        "tex_orm": R + "rhen_head_orm.png", "tex_skin_mask": R + "rhen_head_skinmask.png",
        "tex_detail_normal": A + "asha_skin_detail_normal.png"}

SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # Asha's tuned skin response (M1-CHR-10); rhen.md §6 adds salt-dry lips (rougher, in the albedo pass)
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.85", "normal_strength": "1.0",
        "specular_scale": "0.8", "curvature_scale": "1.3", "roughness_min": "0.42", "roughness_max": "0.62",
        "cavity_albedo": "0.45", "micro_roughness": "0.1",
    }, SKIN),
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.8", "specular_scale": "0.8", "roughness_min": "0.42", "roughness_max": "0.62",
        "cavity_albedo": "0.45",
    }, SKIN),
    "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7"},
                  {"tex_albedo": R + "rhen_body_albedo.png", "tex_normal": R + "rhen_body_normal.png",
                   "tex_orm": R + "rhen_body_orm.png", "tex_skin_mask": R + "rhen_body_skinmask.png",
                   "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
    # rhen.md §6: iris #4A3420, dark amber-brown
    "eye": ("character_eye", 0, {"col_sclera": "Color(0.80, 0.745, 0.69, 1)", "limbus_softness": "0.09",
                                 "col_iris": "Color(0.29, 0.204, 0.125, 1)",
                                 "col_limbal": "Color(0.40, 0.27, 0.16, 1)"},
            {"tex_iris": A + "asha_iris.png", "tex_sclera": A + "asha_sclera.png"}),
    "cornea": ("character_cornea", 1, {}, {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "0.9", "corner_strength": "0.7"}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                   "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                   "indirect_specular": "0.03", "col_root": HAIR_ROOT, "col_tip": HAIR_ROOT},
             {"tex_hair": A + "asha_facehair.png"}),
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.6",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                   "root_occlusion": "0.2", "indirect_specular": "0.05",
                                   "col_root": HAIR_ROOT, "col_tip": HAIR_ROOT},
             {"tex_hair": A + "asha_facehair.png"}),
    "hair": ("character_hair", 0, {"col_root": HAIR_ROOT, "col_tip": HAIR_TIP, "tip_start": "0.72",
                                   "col_spec_primary": HAIR_SPEC_PRIMARY, "spec_primary_intensity": "0.4",
                                   "spec_primary_exponent": "300.0", "spec_shift_jitter": "0.3",
                                   "col_spec_secondary": HAIR_SPEC_SECONDARY, "spec_secondary_intensity": "0.45",
                                   "col_transmission": HAIR_SPEC_SECONDARY, "transmission_strength": "0.9",
                                   "indirect_specular": "0.1", "root_occlusion": "0.6", "depth_occlusion": "0.7"},
             {"tex_hair": A + "asha_hair.png", "tex_hairflow": A + "asha_hairflow.png"}),
    # M1-RND-21: Asha's mouth family (character_mouth: a cavity bounce from the lit lips), same values,
    # reading Rhen's head atlas
    "teeth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
    }, {"tex_albedo": R + "rhen_head_albedo.png", "tex_orm": R + "rhen_head_orm.png"}),
    "tongue": ("character_mouth", 0, {
        "col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6", "specular": "0.25",
    }, {}),
    "mouth": ("character_mouth", 0, {
        "col_albedo": "Color(0.28, 0.1, 0.09, 1)", "roughness": "0.5", "roughness_from_orm": "0.0",
        "ao_light_affect": "0.5",
    }, {"tex_orm": R + "rhen_head_orm.png"}),
    "cloth": ("character_cloth", 0, {"detail_tiling": "140.0"},
              {"tex_albedo": R + "rhen_cloth_albedo.png", "tex_normal": R + "rhen_cloth_normal.png",
               "tex_orm": R + "rhen_cloth_orm.png", "tex_cloth_mask": R + "rhen_cloth_clothmask.png",
               "tex_detail_normal": A + "asha_thread_detail_normal.png"}),
}
STANDARD_MATERIALS = {
    # rhen.md §4: brass (lantern frame, rivets, buckle), not gold; dark steel blades
    "brass": "albedo_color = Color(0.69, 0.553, 0.341, 1)\nmetallic = 1.0\nroughness = 0.4\n",
    "steel": "albedo_color = Color(0.353, 0.376, 0.40, 1)\nmetallic = 1.0\nroughness = 0.35\n",
    # rhen.md §3: salt-glass globe (#BFE6E0), transmission 0.7, unlit by default
    "salt_glass": "transparency = 1\ncull_mode = 2\nalbedo_color = Color(0.749, 0.902, 0.878, 0.35)\n"
                  "roughness = 0.12\nmetallic_specular = 0.6\nrim_enabled = true\nrim = 0.25\n"
                  "rim_tint = 0.8\n",
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
