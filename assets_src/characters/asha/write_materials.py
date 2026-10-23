#!/usr/bin/env python3
"""Writes Asha's hero materials (assets/characters/asha/materials/*.tres) from one table.

    python3 assets_src/characters/asha/write_materials.py

Each material's resource_name equals the glTF material name it replaces at load time
(AshaStage._assign_materials). Values follow asha.md §4-§8 and character_shading.md; every
texture comes from asha_textures.py. Text resources, deterministic.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "assets" / "characters" / "asha" / "materials"
TEX = "res://assets/characters/asha/textures"
SH = "res://game/shaders/character"

# name: (shader, render_priority, {param: value}, {param: texture file})
SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.8", "normal_strength": "1.0",
        "specular_scale": "0.85",
    }, {"tex_albedo": "asha_head_albedo.png", "tex_normal": "asha_head_normal.png", "tex_orm": "asha_head_orm.png",
        "tex_skin_mask": "asha_head_skinmask.png", "tex_detail_normal": "asha_skin_detail_normal.png"}),
    # ADR 0016: dialogue / cinematic close-ups use the painterly mitigation (SPEC §14)
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.8", "specular_scale": "0.85",
    }, {"tex_albedo": "asha_head_albedo.png", "tex_normal": "asha_head_normal.png", "tex_orm": "asha_head_orm.png",
        "tex_skin_mask": "asha_head_skinmask.png", "tex_detail_normal": "asha_skin_detail_normal.png"}),
    "skin_body": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7",
    }, {"tex_albedo": "asha_body_albedo.png", "tex_normal": "asha_body_normal.png", "tex_orm": "asha_body_orm.png",
        "tex_skin_mask": "asha_body_skinmask.png", "tex_detail_normal": "asha_skin_detail_normal.png"}),
    "eye": ("character_eye", 0, {}, {"tex_iris": "asha_iris.png", "tex_sclera": "asha_sclera.png"}),
    "cornea": ("character_cornea", 1, {}, {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.15",
                                   "spec_secondary_intensity": "0.1", "transmission_strength": "0.3"},
             {"tex_hair": "asha_facehair.png"}),
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.12", "alpha_boost": "2.2",
                                   "spec_secondary_intensity": "0.1", "transmission_strength": "0.3",
                                   "root_occlusion": "0.2"},
             {"tex_hair": "asha_facehair.png"}),
    "hair": ("character_hair", 0, {"spec_secondary_intensity": "0.3"},
             {"tex_hair": "asha_hair.png", "tex_hairflow": "asha_hairflow.png"}),
    # M1-CHR-04: lacquered leather on the vest, not the shader's hard-lacquer defaults (0.35 / 0.06 / 1.0),
    # which read as patent plastic over the whole-vest lacquer mask (docs/kb/qa/gpu/2026-10-23-chr-04-materials.md)
    "cloth": ("character_cloth", 0, {"detail_tiling": "160.0", "lacquer_base_roughness": "0.55",
                                     "lacquer_coat_roughness": "0.16", "lacquer_coat_strength": "0.55"},
              {"tex_albedo": "asha_cloth_albedo.png", "tex_normal": "asha_cloth_normal.png",
               "tex_orm": "asha_cloth_orm.png", "tex_cloth_mask": "asha_cloth_clothmask.png",
               "tex_detail_normal": "asha_thread_detail_normal.png"}),
    "cloth_sleeve": ("character_cloth_sheer", 0, {"detail_tiling": "160.0", "wind_response": "0.6",
                                                  "verse_count": "0"},
                     {"tex_albedo": "asha_sleeve_albedo.png", "tex_normal": "asha_sleeve_normal.png",
                      "tex_cloth_mask": "asha_sleeve_clothmask.png", "tex_band_id": "asha_sleeve_bandid.png",
                      "tex_detail_normal": "asha_thread_detail_normal.png"}),
}
STANDARD_MATERIALS = {
    # M1-CHR-04: warmer and rougher; at 0.35 the teeth mirrored the cool sky and read blue-grey in grief
    "teeth": "albedo_color = Color(0.82, 0.76, 0.66, 1)\nroughness = 0.5\n",
    "tongue": "albedo_color = Color(0.55, 0.26, 0.25, 1)\nroughness = 0.4\n",
    "mouth": "albedo_color = Color(0.28, 0.10, 0.09, 1)\nroughness = 0.5\n",
    "staff_wood": "albedo_color = Color(0.227, 0.165, 0.125, 1)\nroughness = 0.45\n",
    "brass": "albedo_color = Color(0.69, 0.553, 0.341, 1)\nmetallic = 1.0\nroughness = 0.35\n",
    "bone": "albedo_color = Color(0.902, 0.855, 0.753, 1)\nroughness = 0.4\n",
    "tortoiseshell": "albedo_color = Color(0.42, 0.227, 0.118, 1)\nroughness = 0.15\nclearcoat_enabled = true\n",
}


def write_shader_material(name: str, shader: str, prio: int, params: dict, textures: dict) -> None:
    ext = [f'[ext_resource type="Shader" path="{SH}/{shader}.gdshader" id="sh"]']
    body = []
    for i, (param, fname) in enumerate(sorted(textures.items())):
        ext.append(f'[ext_resource type="Texture2D" path="{TEX}/{fname}" id="t{i}"]')
        body.append(f'shader_parameter/{param} = ExtResource("t{i}")')
    for param, value in sorted(params.items()):
        body.append(f"shader_parameter/{param} = {value}")
    text = f'[gd_resource type="ShaderMaterial" load_steps={len(ext) + 1} format=3]\n\n' + "\n".join(ext)
    text += f'\n\n[resource]\nresource_name = "{name}"\nrender_priority = {prio}\nshader = ExtResource("sh")\n'
    text += "\n".join(body) + "\n"
    (OUT / f"{name}.tres").write_text(text, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (shader, prio, params, textures) in SHADER_MATERIALS.items():
        write_shader_material(name, shader, prio, params, textures)
    for name, body in STANDARD_MATERIALS.items():
        (OUT / f"{name}.tres").write_text(
            f'[gd_resource type="StandardMaterial3D" format=3]\n\n[resource]\nresource_name = "{name}"\n{body}',
            encoding="utf-8")
    print(f"wrote {len(SHADER_MATERIALS) + len(STANDARD_MATERIALS)} materials to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
