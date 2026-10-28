#!/usr/bin/env python3
"""Writes Liss's hero materials (assets/characters/liss/materials/*.tres) from one table.

    python3 assets_src/characters/liss/write_materials.py

Same writer and conventions as the other heroes' (assets_src/characters/asha/write_materials.py): each material's
resource_name equals the glTF material name it replaces at load time (the hero stage), text resources,
deterministic. Liss's own maps come from liss_textures.py; the generic eye, hair, lash, brow and detail atlases are
Asha's (asha_textures.py), tinted here. Values follow act1_npcs.md §2.3-§2.7 and character_shading.md. Her metals
are copper, brass and iron (no gold, no lacquer: §2.7); the bound-light points are `glimmer_bound`, steady.
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
OUT = ROOT / "assets" / "characters" / "liss" / "materials"
T = "liss/textures/"
A = "asha/textures/"

# §2.5: hair_brown_dark #2A1C14 with sun-rust tips #7A4A2A over the outer 25% (the shader's tip_start); the lashes
# and brows take the root colour. Under the stage's warm key a brown reads warmer than it is (Rhen's lesson): the
# card root is a touch deeper and cooler.
HAIR = "Color(0.165, 0.11, 0.078, 1)"  # #2A1C14
HAIR_CARD = "Color(0.13, 0.09, 0.07, 1)"
HAIR_TIP = "Color(0.478, 0.29, 0.165, 1)"  # #7A4A2A
HAIR_SPEC = "Color(0.90, 0.82, 0.72, 1)"
HAIR_SPEC2 = "Color(0.62, 0.38, 0.22, 1)"
SKIN = {"tex_albedo": T + "liss_head_albedo.png", "tex_normal": T + "liss_head_normal.png",
        "tex_orm": T + "liss_head_orm.png", "tex_skin_mask": T + "liss_head_skinmask.png",
        "tex_detail_normal": A + "asha_skin_detail_normal.png"}
CLOTH = {"tex_albedo": T + "liss_cloth_albedo.png", "tex_normal": T + "liss_cloth_normal.png",
         "tex_orm": T + "liss_cloth_orm.png", "tex_cloth_mask": T + "liss_cloth_clothmask.png",
         "tex_detail_normal": A + "asha_thread_detail_normal.png"}
SLEEVE = {"tex_albedo": T + "liss_sleeve_albedo.png", "tex_normal": T + "liss_sleeve_normal.png",
          "tex_orm": T + "liss_sleeve_orm.png", "tex_cloth_mask": T + "liss_sleeve_clothmask.png",
          "tex_detail_normal": A + "asha_thread_detail_normal.png"}

SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # Asha's tuned skin response (M1-CHR-10); §2.6: sea-weathered, a touch rougher than Rhen's
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.85", "normal_strength": "1.0",
        "specular_scale": "0.75", "curvature_scale": "1.3", "roughness_min": "0.45", "roughness_max": "0.66",
        "cavity_albedo": "0.45", "micro_roughness": "0.1",
    }, SKIN),
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.8", "specular_scale": "0.75", "roughness_min": "0.45", "roughness_max": "0.66",
        "cavity_albedo": "0.45",
    }, SKIN),
    "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7"},
                  {"tex_albedo": T + "liss_body_albedo.png", "tex_normal": T + "liss_body_normal.png",
                   "tex_orm": T + "liss_body_orm.png", "tex_skin_mask": T + "liss_body_skinmask.png",
                   "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
    # §2.6: green-brown irises #4E4A2C (the only green-brown eyes in the party)
    "eye": ("character_eye", 0, {"col_sclera": "Color(0.80, 0.745, 0.69, 1)", "limbus_softness": "0.09",
                                 "col_iris": "Color(0.306, 0.29, 0.173, 1)",
                                 "col_limbal": "Color(0.20, 0.19, 0.11, 1)"},
            {"tex_iris": A + "asha_iris.png", "tex_sclera": A + "asha_sclera.png"}),
    "cornea": ("character_cornea", 1, {}, {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "0.9", "corner_strength": "0.7"}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                   "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                   "indirect_specular": "0.03", "col_root": HAIR, "col_tip": HAIR},
             {"tex_hair": A + "asha_facehair.png"}),
    # §2.6: straight, thick brows
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.8",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                   "root_occlusion": "0.2", "indirect_specular": "0.05",
                                   "col_root": HAIR, "col_tip": HAIR},
             {"tex_hair": A + "asha_facehair.png"}),
    "hair": ("character_hair", 0, {"col_root": HAIR_CARD, "col_tip": HAIR_TIP, "tip_start": "0.75",
                                   "col_spec_primary": HAIR_SPEC, "spec_primary_intensity": "0.35",
                                   "spec_primary_exponent": "260.0", "spec_shift_jitter": "0.3",
                                   "col_spec_secondary": HAIR_SPEC2, "spec_secondary_intensity": "0.4",
                                   "col_transmission": HAIR_SPEC2, "transmission_strength": "0.6",
                                   "indirect_specular": "0.08", "root_occlusion": "0.6", "depth_occlusion": "0.7",
                                   "kajiya_diffuse_mix": "0.15"},
             {"tex_hair": A + "asha_hair.png", "tex_hairflow": A + "asha_hairflow.png"}),
    # sailcloth, canvas and leather (no lacquer, no gold); brass in the atlas is metal (ORM B)
    "cloth": ("character_cloth", 0, {"detail_tiling": "150.0", "sheen_tint": "0.8", "sheen_intensity": "0.4"},
              CLOTH),
    # §2.3: the copper-wire mesh: bronze_patina over copper, metallic from the ORM's B
    "copper_mesh": ("character_cloth", 0, {"detail_tiling": "220.0", "detail_strength": "0.5",
                                           "sheen_intensity": "0.0", "roughness_scale": "1.0",
                                           "normal_strength": "1.2"}, SLEEVE),
    # M1-RND-21: Asha's mouth family, same values, reading Liss's head atlas
    "teeth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
    }, {"tex_albedo": T + "liss_head_albedo.png", "tex_orm": T + "liss_head_orm.png"}),
    "tongue": ("character_mouth", 0, {
        "col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6", "specular": "0.25",
    }, {}),
    "mouth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "0.5", "roughness_from_orm": "0.0",
        "ao_light_affect": "0.5",
    }, {"tex_albedo": T + "liss_head_albedo.png", "tex_orm": T + "liss_head_orm.png"}),
}
STANDARD_MATERIALS = {
    # §2.4 #7 the launcher: copper #A0603A (proposed), brass #B08D57, iron fittings #3A3A3F
    "copper": "albedo_color = Color(0.627, 0.376, 0.227, 1)\nmetallic = 1.0\nroughness = 0.42\n",
    "brass": "albedo_color = Color(0.69, 0.553, 0.341, 1)\nmetallic = 1.0\nroughness = 0.4\n",
    "iron": "albedo_color = Color(0.227, 0.227, 0.247, 1)\nmetallic = 1.0\nroughness = 0.55\n",
    # §2.3 the bound-light points: glimmer_bound #4FB3B0, steady emission (no flicker)
    "glimmer": "albedo_color = Color(0.31, 0.702, 0.69, 1)\nemission_enabled = true\n"
               "emission = Color(0.31, 0.702, 0.69, 1)\nemission_energy_multiplier = 2.5\nroughness = 0.3\n",
    # §2.5 the salvaged glass beads (transmissive): salt glass #BFE6E0, copper-green glass #4FA08A, amber #B8782E
    "bead_salt": "albedo_color = Color(0.749, 0.902, 0.878, 1)\nroughness = 0.12\nmetallic_specular = 0.7\n"
                 "rim_enabled = true\nrim = 0.3\nrim_tint = 0.8\n",
    "bead_green": "albedo_color = Color(0.31, 0.627, 0.541, 1)\nroughness = 0.12\nmetallic_specular = 0.7\n"
                  "rim_enabled = true\nrim = 0.3\nrim_tint = 0.8\n",
    "bead_amber": "albedo_color = Color(0.722, 0.471, 0.18, 1)\nroughness = 0.12\nmetallic_specular = 0.7\n"
                  "rim_enabled = true\nrim = 0.3\nrim_tint = 0.8\n",
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
