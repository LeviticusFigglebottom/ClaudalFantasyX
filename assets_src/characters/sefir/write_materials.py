#!/usr/bin/env python3
"""Writes Sefir's hero materials (assets/characters/sefir/materials/*.tres) from one table.

    python3 assets_src/characters/sefir/write_materials.py

Same writer and conventions as Asha's, Rhen's and Toma's (assets_src/characters/asha/write_materials.py): each
material's resource_name equals the glTF material name it replaces at load time (the hero stage), text resources,
deterministic. Sefir's own maps come from sefir_textures.py; the generic eye, hair, lash, brow and detail atlases are
Asha's (asha_textures.py), tinted here. Values follow act1_npcs.md §1.4-§1.7 and character_shading.md.

The Act II tell (act1_npcs.md §1.6, "his eyes catch light like a still pool") is a material variant, not a map: the
`sefir_eye_still` pair, `eye_still` (the eye) and `cornea_still` (the cornea with its specular raised toward a mirror),
which a scene swaps in for the `eye` and `cornea` slots. Act I uses the normal eye.
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
OUT = ROOT / "assets" / "characters" / "sefir" / "materials"
T = "sefir/textures/"
A = "asha/textures/"

# act1_npcs.md §1.5: hair_silver #CFCAC0, a cool primary highlight #F2F2F2 at 0.4, a secondary #9A948A at 0.3
HAIR = "Color(0.812, 0.792, 0.753, 1)"  # #CFCAC0
HAIR_TIP = "Color(0.835, 0.816, 0.78, 1)"  # a touch paler toward the tips (#D5D0C7)
HAIR_SPEC = "Color(0.949, 0.949, 0.949, 1)"  # #F2F2F2
HAIR_SPEC2 = "Color(0.604, 0.580, 0.541, 1)"  # #9A948A
HAIR_TT = "Color(0.78, 0.75, 0.70, 1)"  # light through pale hair: its own colour, a little warm
BROW = "Color(0.714, 0.690, 0.651, 1)"  # #B6B0A6, ash-silver
LASH = "Color(0.494, 0.471, 0.435, 1)"  # #7E786F: the lashes a shade darker than the brows (they frame the eye)
WIND = {"wind_response": "0.1"}  # §1.5: his hair barely moves in the wind (party heroes take 0.25-0.6)
STILL = {"wind_response": "0.0"}
PORES = 0.6  # §1.6: pores at 0.6 of the heroes' strength (the tiled detail normal carries them)
SKIN = {"tex_albedo": T + "sefir_head_albedo.png", "tex_normal": T + "sefir_head_normal.png",
        "tex_orm": T + "sefir_head_orm.png", "tex_skin_mask": T + "sefir_head_skinmask.png",
        "tex_detail_normal": A + "asha_skin_detail_normal.png"}
EYE = {"col_sclera": "Color(0.80, 0.755, 0.70, 1)", "limbus_softness": "0.08",
       "col_iris": "Color(0.435, 0.494, 0.471, 1)",  # #6F7E78, pale grey-green
       "col_limbal": "Color(0.290, 0.337, 0.322, 1)"}  # #4A5652
EYE_TEX = {"tex_iris": A + "asha_iris.png", "tex_sclera": A + "asha_sclera.png"}

SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # Asha's tuned skin response; §1.6: smooth by design (the detail at 0.6), no age layer
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": f"{0.8 * PORES:.2f}", "normal_strength": "1.0",
        "specular_scale": "0.85", "curvature_scale": "1.3", "roughness_min": "0.42", "roughness_max": "0.60",
        "cavity_albedo": "0.4", "micro_roughness": "0.08",
    }, SKIN),
    # §1.6: close range takes ADR 0019's dialogue finish
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": f"{0.35 * PORES:.2f}",
        "normal_strength": "0.8", "specular_scale": "0.85", "roughness_min": "0.42", "roughness_max": "0.60",
        "cavity_albedo": "0.4",
    }, SKIN),
    "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0",
                                        "detail_strength": f"{0.7 * PORES:.2f}"},
                  {"tex_albedo": T + "sefir_body_albedo.png", "tex_normal": T + "sefir_body_normal.png",
                   "tex_orm": T + "sefir_body_orm.png", "tex_skin_mask": T + "sefir_body_skinmask.png",
                   "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
    "eye": ("character_eye", 0, EYE, EYE_TEX),
    "cornea": ("character_cornea", 1, {}, {}),
    # the sefir_eye_still variant (Act II): a still pool. The eye itself is unchanged but for a darker limbus (the
    # iris reads glassier behind a mirror-bright cornea); the cornea is nearly roughness-free and wetter, with a
    # higher highlight clamp, so the environment reflects in it like a mirror
    "eye_still": ("character_eye", 0, {**EYE, "limbus_shadow": "0.6", "caustic_strength": "0.8"}, EYE_TEX),
    "cornea_still": ("character_cornea", 1, {"roughness": "0.008", "wet_strength": "1.8", "highlight_max": "32.0"},
                     {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "0.85", "corner_strength": "0.7"}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                   "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                   "indirect_specular": "0.03", "col_root": LASH, "col_tip": LASH, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.6",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                   "root_occlusion": "0.2", "indirect_specular": "0.05",
                                   "col_root": BROW, "col_tip": BROW, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    # pale hair: less root and layer occlusion than the dark heads (heavy occlusion turns silver to grey), a cool,
    # narrow primary and a soft secondary in the pigment's own grey
    "hair": ("character_hair", 0, {"col_root": HAIR, "col_tip": HAIR_TIP, "col_spec_primary": HAIR_SPEC,
                                   "spec_primary_intensity": "0.4", "spec_primary_exponent": "300.0",
                                   "spec_shift_jitter": "0.25", "col_spec_secondary": HAIR_SPEC2,
                                   "spec_secondary_intensity": "0.3", "col_transmission": HAIR_TT,
                                   "transmission_strength": "0.6", "indirect_specular": "0.1",
                                   "root_occlusion": "0.45", "depth_occlusion": "0.5", "strand_value_jitter": "0.1",
                                   "alpha_boost": "1.5",  # GPU QA row 54: the cap read translucent at 1.15
                                   **WIND},
             {"tex_hair": A + "asha_hair.png", "tex_hairflow": A + "asha_hairflow.png"}),
    # ivory and still-blue silk, the mantle's gold leaf (G) on black lacquer (B); the gold is a little rougher than
    # thread (leaf on a shell) and isotropic-ish
    # less sheen than the default: on pale silk a strong sheen lobe washed the blue to white under the warm key
    "cloth": ("character_cloth", 0, {"detail_tiling": "180.0", "detail_strength": "0.4", "sheen_intensity": "0.45",
                                     "sheen_tint": "0.85",
                                     "gold_roughness": "0.3", "gold_anisotropy": "0.2",
                                     "lacquer_base_roughness": "0.45", "lacquer_coat_roughness": "0.08",
                                     "lacquer_coat_strength": "0.8"},
              {"tex_albedo": T + "sefir_cloth_albedo.png", "tex_normal": T + "sefir_cloth_normal.png",
               "tex_orm": T + "sefir_cloth_orm.png", "tex_cloth_mask": T + "sefir_cloth_clothmask.png",
               "tex_detail_normal": A + "asha_thread_detail_normal.png"}),
    "teeth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
    }, {"tex_albedo": T + "sefir_head_albedo.png", "tex_orm": T + "sefir_head_orm.png"}),
    "tongue": ("character_mouth", 0, {
        "col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6", "specular": "0.25",
    }, {}),
    "mouth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "0.5", "roughness_from_orm": "0.0",
        "ao_light_affect": "0.5",
    }, {"tex_albedo": T + "sefir_head_albedo.png", "tex_orm": T + "sefir_head_orm.png"}),
}
STANDARD_MATERIALS = {
    # §1.4 #6: gilt metal; the crown's convex back, rim, band and stem in gold_leaf #D4A437 ...
    "gilt": "albedo_color = Color(0.831, 0.643, 0.216, 1)\nmetallic = 1.0\nroughness = 0.32\n",
    # ... and its concave face burnished gold_leaf_hi #F1D27A, roughness 0.22 (reflective, never emissive)
    "gilt_hi": "albedo_color = Color(0.945, 0.824, 0.478, 1)\nmetallic = 1.0\nroughness = 0.22\n",
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
