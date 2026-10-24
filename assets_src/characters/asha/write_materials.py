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

# M1-CHR-10: Asha's hair, lashes and brows read auburn, not black (asha.md §5). The albedo was on
# spec (#201A16), but #201A16 is a warm brown-black, and the stage's key and rim are orange: lit
# hair took the light's hue almost unfiltered (a lavapipe diagnostic with every lobe off still
# rendered the crown at sRGB 35/16/6, R:B 6:1), while the root and layer occlusion took away most
# of the cool sky fill. A neutral, slightly cool near-black keeps the mass black under a warm key
# and still reads warm-dark under it. Same value range as #201A16; under the 0x1D1916 albedo floor
# that asha_textures applies to skin, which these shader colours do not go through.
HAIR_BLACK = "Color(0.08, 0.08, 0.09, 1)"  # #141417
# The primary highlight, slightly cool so that under the warm key it reads as a pale ribbon (asha.md
# §5: "a thin, cool-white ribbon") instead of gold. The secondary and the transmission carry the
# pigment's colour, which for black hair is a dark, faintly warm brown, not the #8A5A3A of light
# through brown hair (the M1-RND-04 proposal, which character_shading.md tuned on a test bust).
HAIR_SPEC_PRIMARY = "Color(0.76, 0.85, 1.0, 1)"
HAIR_SPEC_SECONDARY = "Color(0.30, 0.27, 0.25, 1)"
HAIR_TRANSMISSION = "Color(0.29, 0.23, 0.19, 1)"

# name: (shader, render_priority, {param: value}, {param: texture file})
SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # M1-CHR-10, the evenly lit skin: the shader's roughness range (0.42-0.5) left the ORM's oily
    # T-zone and rough cheeks almost the same, so the sheen sat evenly over the face. A wider range,
    # more cavity in the albedo and more pore-scale roughness let the highlight break up by zone
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.8", "normal_strength": "1.0",
        "specular_scale": "0.85", "curvature_scale": "1.3", "roughness_min": "0.40", "roughness_max": "0.58",
        "cavity_albedo": "0.45", "micro_roughness": "0.1",
    }, {"tex_albedo": "asha_head_albedo.png", "tex_normal": "asha_head_normal.png", "tex_orm": "asha_head_orm.png",
        "tex_skin_mask": "asha_head_skinmask.png", "tex_detail_normal": "asha_skin_detail_normal.png"}),
    # ADR 0016: dialogue / cinematic close-ups use the painterly mitigation (SPEC §14)
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.8", "specular_scale": "0.85", "roughness_min": "0.40", "roughness_max": "0.58",
        "cavity_albedo": "0.45",
    }, {"tex_albedo": "asha_head_albedo.png", "tex_normal": "asha_head_normal.png", "tex_orm": "asha_head_orm.png",
        "tex_skin_mask": "asha_head_skinmask.png", "tex_detail_normal": "asha_skin_detail_normal.png"}),
    "skin_body": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7",
    }, {"tex_albedo": "asha_body_albedo.png", "tex_normal": "asha_body_normal.png", "tex_orm": "asha_body_orm.png",
        "tex_skin_mask": "asha_body_skinmask.png", "tex_detail_normal": "asha_skin_detail_normal.png"}),
    "eye": ("character_eye", 0, {"col_sclera": "Color(0.80, 0.745, 0.69, 1)", "limbus_softness": "0.09"},
            {"tex_iris": "asha_iris.png", "tex_sclera": "asha_sclera.png"}),
    "cornea": ("character_cornea", 1, {}, {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "0.9", "corner_strength": "0.7"}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    # M1-CHR-10: lashes and brows in the hair's black (they read brown), with almost no environment
    # reflection (a near-black strand should not carry the sky's colour)
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                   "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                   "indirect_specular": "0.03", "col_root": HAIR_BLACK, "col_tip": HAIR_BLACK},
             {"tex_hair": "asha_facehair.png"}),
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.6",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                   "root_occlusion": "0.2", "indirect_specular": "0.05",
                                   "col_root": HAIR_BLACK, "col_tip": HAIR_BLACK},
             {"tex_hair": "asha_facehair.png"}),
    # M1-CHR-07: the primary lobe at exponent 120 on the smooth card shell spread over the whole lit
    # side and read as a broad gold sheen, which asha.md §5 rules out ("a thin ribbon, never a broad
    # sheen"). Narrower (400), broken up per strand, and less environment reflection.
    # M1-CHR-10: the colour itself (HAIR_BLACK and the lobe tints above), the primary at 0.45
    # (0.55 read as straw streaks on the darker mass), the jitter at the shader's cap
    # so each strand breaks the ribbon, and less root and layer occlusion so the sky fill (the cool
    # half of the stage's light) reaches the mass. Rendering to confirm on a GPU.
    "hair": ("character_hair", 0, {"col_root": HAIR_BLACK, "col_tip": HAIR_BLACK,
                                   "col_spec_primary": HAIR_SPEC_PRIMARY, "spec_primary_intensity": "0.45",
                                   "spec_primary_exponent": "400.0", "spec_shift_jitter": "0.3",
                                   "col_spec_secondary": HAIR_SPEC_SECONDARY, "spec_secondary_intensity": "0.12",
                                   "col_transmission": HAIR_TRANSMISSION, "transmission_strength": "0.5",
                                   "indirect_specular": "0.1", "root_occlusion": "0.7", "depth_occlusion": "0.75"},
             {"tex_hair": "asha_hair.png", "tex_hairflow": "asha_hairflow.png"}),
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
    # M1-RND-21: the mouth interior uses the shared character_mouth family (a cavity bounce from the lit
    # lips, so an open grief mouth is not near-black). Same values as the StandardMaterial3D they were:
    # M1-CHR-04: warmer and rougher; at 0.35 the teeth mirrored the cool sky and read blue-grey in grief.
    # M1-CHR-10: still a grey slab. A diagnostic render (teeth albedo pure red, specular 0) showed the
    # slab was the teeth's specular: the sky's reflection, which the lips should hide and nothing
    # occluded. Specular 0.06 (inside the mouth only the key's own highlight should survive), and the
    # colour, roughness and occlusion now come from the teeth patch of the head atlas
    # (asha_textures.teeth_patch); the occlusion also dims the key a little (the lips shade it).
    "teeth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
    }, {"tex_albedo": "asha_head_albedo.png", "tex_orm": "asha_head_orm.png"}),
    # M1-CHR-10: the pale streak along the open grief mouth was the tongue mirroring the sky
    "tongue": ("character_mouth", 0, {
        "col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6", "specular": "0.25",
    }, {}),
    # M1-CHR-10: the mouth interior takes the head bake's occlusion (its UVs are in the head atlas),
    # so the bag darkens away from the lips instead of meeting them as one flat dark red.
    # M1-RND-25: it now also carries the lips' inner roll, so its colour comes from the head atlas
    # (asha_textures paints the bag the old flat #471A17 and the inner lip as mucosa)
    "mouth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "0.5", "roughness_from_orm": "0.0",
        "ao_light_affect": "0.5",
    }, {"tex_albedo": "asha_head_albedo.png", "tex_orm": "asha_head_orm.png"}),
}
STANDARD_MATERIALS = {
    "staff_wood": "albedo_color = Color(0.227, 0.165, 0.125, 1)\nroughness = 0.45\n",
    "brass": "albedo_color = Color(0.69, 0.553, 0.341, 1)\nmetallic = 1.0\nroughness = 0.35\n",
    "bone": "albedo_color = Color(0.902, 0.855, 0.753, 1)\nroughness = 0.4\n",
    # M1-CHR-07: polished, not a mirror; at roughness 0.15 under a full clearcoat the comb mirrored
    # the sky and read as a pale grey card above the ear
    "tortoiseshell": "albedo_color = Color(0.30, 0.16, 0.08, 1)\nroughness = 0.35\nclearcoat_enabled = true\n"
                     "clearcoat = 0.5\nclearcoat_roughness = 0.3\n",
}
# textures of the StandardMaterial3D entries: {name: {property: texture file}}
STANDARD_TEXTURES: dict[str, dict] = {}


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


def write_standard_material(name: str, body: str, textures: dict) -> None:
    files = sorted(set(textures.values()))
    ids = {f: f"t{i}" for i, f in enumerate(files)}
    head = '[gd_resource type="StandardMaterial3D" format=3]\n\n'
    if files:
        head = f'[gd_resource type="StandardMaterial3D" load_steps={len(files) + 1} format=3]\n\n'
        head += "".join(f'[ext_resource type="Texture2D" path="{TEX}/{f}" id="{ids[f]}"]\n' for f in files) + "\n"
    tex = "".join(f'{prop} = ExtResource("{ids[f]}")\n' for prop, f in sorted(textures.items()))
    (OUT / f"{name}.tres").write_text(f'{head}[resource]\nresource_name = "{name}"\n{body}{tex}', encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (shader, prio, params, textures) in SHADER_MATERIALS.items():
        write_shader_material(name, shader, prio, params, textures)
    for name, body in STANDARD_MATERIALS.items():
        write_standard_material(name, body, STANDARD_TEXTURES.get(name, {}))
    print(f"wrote {len(SHADER_MATERIALS) + len(STANDARD_MATERIALS)} materials to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
