#!/usr/bin/env python3
"""Writes Kerrid's hero materials (assets/characters/kerrid/materials/*.tres) from one table.

    python3 assets_src/characters/kerrid/write_materials.py

Same writer and conventions as the other heroes' (assets_src/characters/asha/write_materials.py): each material's
resource_name equals the glTF material name it replaces at load time (the hero stage), text resources,
deterministic. Kerrid's own maps come from kerrid_textures.py; the generic eye, lash, brow and detail atlases are
Asha's (asha_textures.py) and the cropped hair and beard use Toma's `toma_shorthair.png` (toma_textures.py), all
referenced, not copied, and tinted here. Values follow kerrid.md §3-§7 and character_shading.md.

* The cape: `cape_mat` (the woven base mats, on the costume atlas) and `fibre` (the hanging strands on
  `kerrid_fibre.png`, character_hair: palm_fibre at the root, the sun-bleached palm_fibre_pale on the outer 30%), plus
  their wet variants `cape_mat_wet` / `fibre_wet` (§4.1 #10: palm_fibre_wet, roughness down 0.2), which the Ch8-Ch9
  scenes swap in with the `cape_wet` shape.
* `burn_glow` (§3): the rope-burn shell's light, an additive emission of `glimmer_held` through `kerrid_burn_glow.png`,
  black and unlit otherwise. Its energy is `burn_glow` x `burn_glow_energy_per_unit` (kerrid_params.json `_kerrid`):
  **0 by default** (Ch5-Ch9); the scenes from Ch10 set it (0.15 -> 0.12).
* No gold anywhere (§7): the cleaver's metal is the ORM's B, never the cloth mask's gold channel.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Asha's writer, loaded by path (this file has the same name, so a plain import would find itself)
_spec = importlib.util.spec_from_file_location("asha_write_materials", HERE.parent / "asha" / "write_materials.py")
wm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wm)

ROOT = HERE.parents[2]
OUT = ROOT / "assets" / "characters" / "kerrid" / "materials"
PARAMS = HERE / "kerrid_params.json"
T = "kerrid/textures/"
A = "asha/textures/"
TOMA = "toma/textures/"


def col(hexv: str, a: float = 1.0) -> str:
    h = hexv.lstrip("#")
    r, g, b = (round(int(h[i:i + 2], 16) / 255.0, 3) for i in (0, 2, 4))
    return f"Color({r}, {g}, {b}, {a})"


# kerrid.md §5: hair_black #201A16 with grey strands #8A867E (the grey cards are their own material). Toma's cooler,
# deeper card black (M2-CHR-04: hair_black read brown under the warm stage key) and his matte, near-surface response.
HAIR = col("#201A16")
HAIR_ROOT = "Color(0.11, 0.10, 0.10, 1)"  # Toma's (M2-CHR-524)
HAIR_TIP = "Color(0.14, 0.125, 0.12, 1)"
# M2-CHR-524: at dialogue range the cards drew as near-black specks over the scalp paint. The paint between them is
# lit as skin, and the cards were darker in albedo (#111013) and darkened again by root and layer occlusion (0.7 x 0.75)
# meant for long hair's deep layers; cropped cards lie on the skin. The cards now sit near the paint's rendered value,
# so they add strand grain, not dots, and the grey cards are a thin veil (GREY_ALPHA) over the dark: salt-and-pepper
# reads as a lighter haze, not as pale chips.
CROP_AO = {"root_occlusion": "0.85", "depth_occlusion": "0.85"}
GREY_ALPHA = "0.6"  # alpha_boost of the grey cards
# alpha_boost of the scalp cards (was 1.15): where the key catches the crown, a card renders a little lighter than
# the scalp paint between cards, so card-sized coverage steps read as mottling. At 0.85 the paint carries the value
# and the cards the grain. The beard cards keep 1.1 (a full beard, dense over its own paint).
CROP_ALPHA = "0.85"
GREY = col("#8A867E")
BROW_TIP = "Color(0.25, 0.24, 0.23, 1)"  # §6.1: grey-black brows with grey hairs toward the ends
HAIR_SPEC = col("#D8CCC0")  # §5: the primary highlight tint
HAIR_SPEC2 = "Color(0.32, 0.30, 0.30, 1)"
HAIR_TT = "Color(0.20, 0.17, 0.15, 1)"
STILL = {"wind_response": "0.0"}  # cropped hair, beard, lashes and brows do not sway (§5: head-rigid)
SHORT = TOMA + "toma_shorthair.png"  # Toma's short-hair atlas (strands along +V: no flow map)
FLAT = {"kajiya_diffuse_mix": "0.15", "diffuse_wrap": "0.3"}  # §5: kajiya_diffuse_mix 0.15, matte
SHORT_HAIR = {"flow_strength": "0.0", "col_root": HAIR_ROOT, "col_tip": HAIR_TIP, "col_spec_primary": HAIR_SPEC,
              "spec_primary_intensity": "0.07", "spec_primary_exponent": "60.0", "spec_secondary_intensity": "0.0",
              "col_spec_secondary": HAIR_SPEC2, "secondary_sparkle": "0.3", "col_transmission": HAIR_TT, **FLAT,
              "transmission_strength": "0.1", "indirect_specular": "0.05", **CROP_AO,
              "alpha_boost": CROP_ALPHA, "strand_value_jitter": "0.12", **STILL}
BEARD = {**SHORT_HAIR, "spec_primary_intensity": "0.06", "indirect_specular": "0.04", "alpha_boost": "1.1"}
# §4.1 #6, §7: palm_fibre #A08C66, the sun-bleached tips palm_fibre_pale #C2B08A on the outer 30% of each strand; dry
# fibre: a broad, low highlight, light through the thin strands. Wet (#10): palm_fibre_wet #5E5038, glossier.
FIBRE = {"flow_strength": "0.0", "col_root": col("#A08C66"), "col_tip": col("#C2B08A"), "tip_start": "0.7",
         "col_spec_primary": col("#E6DCC8"), "spec_primary_intensity": "0.12", "spec_primary_exponent": "30.0",
         "spec_secondary_intensity": "0.05", "col_spec_secondary": col("#8C7650"), "secondary_sparkle": "0.5",
         "col_transmission": col("#B09060"), "transmission_strength": "0.5", "indirect_specular": "0.04",
         "root_occlusion": "0.55", "depth_occlusion": "0.55", "kajiya_diffuse_mix": "0.3", "diffuse_wrap": "0.4",
         "strand_value_jitter": "0.18", "strand_hue_jitter": "0.02", "alpha_boost": "1.1"}
FIBRE_WET = {**FIBRE, "col_root": col("#5E5038"), "col_tip": col("#6A5B42"), "spec_primary_intensity": "0.3",
             "spec_primary_exponent": "90.0", "transmission_strength": "0.2", "indirect_specular": "0.1"}
WET_TINT = "Color(0.588, 0.571, 0.549, 1)"  # palm_fibre_wet / palm_fibre per channel (#5E5038 / #A08C66)
SKIN = {"tex_albedo": T + "kerrid_head_albedo.png", "tex_normal": T + "kerrid_head_normal.png",
        "tex_orm": T + "kerrid_head_orm.png", "tex_skin_mask": T + "kerrid_head_skinmask.png",
        "tex_detail_normal": A + "asha_skin_detail_normal.png"}
CLOTH = {"tex_albedo": T + "kerrid_cloth_albedo.png", "tex_normal": T + "kerrid_cloth_normal.png",
         "tex_orm": T + "kerrid_cloth_orm.png", "tex_cloth_mask": T + "kerrid_cloth_clothmask.png",
         "tex_detail_normal": A + "asha_thread_detail_normal.png"}
CLEAVER = {"tex_albedo": T + "kerrid_cleaver_albedo.png", "tex_normal": T + "kerrid_cleaver_normal.png",
           "tex_orm": T + "kerrid_cleaver_orm.png", "tex_detail_normal": A + "asha_thread_detail_normal.png"}
GLIMMER_HELD = col("#7FC6D9")  # ADR 0022 (g): an unrisen's held light

SHADER_MATERIALS: dict[str, tuple[str, int, dict, dict]] = {
    # Asha's tuned skin response (M1-CHR-10); kerrid.md §6.1: sea-weathered, as rough as Toma's
    "skin_head": ("character_skin", 0, {
        "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.9", "normal_strength": "1.0",
        "specular_scale": "0.75", "curvature_scale": "1.3", "roughness_min": "0.46", "roughness_max": "0.66",
        "cavity_albedo": "0.45", "micro_roughness": "0.1",
    }, SKIN),
    # ADR 0019: the dialogue finish (painterly 0.6, detail 0.35), as every hero
    "skin_head_dialogue": ("character_skin", 0, {
        "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
        "normal_strength": "0.8", "specular_scale": "0.75", "roughness_min": "0.46", "roughness_max": "0.66",
        "cavity_albedo": "0.45",
    }, SKIN),
    "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7"},
                  {"tex_albedo": T + "kerrid_body_albedo.png", "tex_normal": T + "kerrid_body_normal.png",
                   "tex_orm": T + "kerrid_body_orm.png", "tex_skin_mask": T + "kerrid_body_skinmask.png",
                   "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
    # §6.1: both eyes clear and grey, iris #6C7378 with a darker limbal ring #4A5056
    "eye": ("character_eye", 0, {"col_sclera": "Color(0.79, 0.735, 0.68, 1)", "limbus_softness": "0.09",
                                 "col_iris": col("#6C7378"), "col_limbal": col("#4A5056")},
            {"tex_iris": A + "asha_iris.png", "tex_sclera": A + "asha_sclera.png"}),
    "cornea": ("character_cornea", 1, {}, {}),
    "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "1.0", "corner_strength": "0.75"}, {}),
    "tear_line": ("character_tear_line", 3, {}, {}),
    "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                   "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                   "indirect_specular": "0.03", "col_root": HAIR, "col_tip": HAIR, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    # §6.1: thick, low, straight brows
    "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.8",
                                   "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                   "root_occlusion": "0.2", "indirect_specular": "0.05", "tip_start": "0.6",
                                   "col_root": HAIR, "col_tip": BROW_TIP, **STILL},
             {"tex_hair": A + "asha_facehair.png"}),
    "hair": ("character_hair", 0, SHORT_HAIR, {"tex_hair": SHORT}),
    "hair_grey": ("character_hair", 0, {**SHORT_HAIR, "col_root": GREY, "col_tip": GREY, "alpha_boost": GREY_ALPHA}, {"tex_hair": SHORT}),
    "beard": ("character_hair", 0, BEARD, {"tex_hair": SHORT}),
    "beard_grey": ("character_hair", 0, {**BEARD, "col_root": GREY, "col_tip": GREY, "alpha_boost": GREY_ALPHA}, {"tex_hair": SHORT}),
    # §4.1: hemp, tarred canvas, rope, leather (the mask's A carries each one's sheen); no lacquer, no gold
    "cloth": ("character_cloth", 0, {"detail_tiling": "140.0", "sheen_tint": "0.8", "sheen_intensity": "0.4"}, CLOTH),
    # §4.1 #6: the cape's woven base mats (the costume atlas's cape_mat island), A 0.4 dry fibre fuzz
    "cape_mat": ("character_cloth", 0, {"detail_tiling": "120.0", "sheen_tint": "0.9", "sheen_intensity": "0.5"},
                 CLOTH),
    "cape_mat_wet": ("character_cloth", 0, {"col_albedo": WET_TINT, "detail_tiling": "120.0", "sheen_tint": "0.9",
                                            "sheen_intensity": "0.19", "roughness_scale": "0.65"}, CLOTH),
    "fibre": ("character_hair", 0, FIBRE, {"tex_hair": T + "kerrid_fibre.png"}),
    "fibre_wet": ("character_hair", 0, FIBRE_WET, {"tex_hair": T + "kerrid_fibre.png"}),
    # §4.1 #11: forged iron (metallic from the ORM's B), roughness 0.6 on the scale and 0.3 on the ground edge, as
    # authored; the tarred-rope grip is not metal
    "cleaver": ("character_cloth", 0, {"detail_strength": "0.0", "sheen_intensity": "0.0", "roughness_scale": "1.0"},
                CLEAVER),
    # M1-RND-21 / M1-RND-25: Asha's mouth family (character_mouth, the cavity bounce), same values, reading
    # Kerrid's head atlas
    "teeth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
    }, {"tex_albedo": T + "kerrid_head_albedo.png", "tex_orm": T + "kerrid_head_orm.png"}),
    "tongue": ("character_mouth", 0, {
        "col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6", "specular": "0.25",
    }, {}),
    "mouth": ("character_mouth", 0, {
        "col_albedo": "Color(1, 1, 1, 1)", "roughness": "0.5", "roughness_from_orm": "0.0",
        "ao_light_affect": "0.5",
    }, {"tex_albedo": T + "kerrid_head_albedo.png", "tex_orm": T + "kerrid_head_orm.png"}),
}


def standard_materials() -> tuple[dict[str, str], dict[str, dict]]:
    kp = json.loads(PARAMS.read_text(encoding="utf-8"))["_kerrid"]
    energy = float(kp["burn_glow_default"]) * float(kp["burn_glow_energy_per_unit"])
    # §3: the burn shell adds light only: black, no specular, no ambient, additive; the light is the mask's
    # glimmer_held at burn_glow x energy-per-unit (0 by default: nothing shows in Ch5-Ch9)
    burn = ("blend_mode = 1\nspecular_mode = 2\ndisable_ambient_light = true\ndisable_receive_shadows = true\n"
            "albedo_color = Color(0, 0, 0, 1)\nroughness = 1.0\nemission_enabled = true\n"
            f"emission = {GLIMMER_HELD}\nemission_energy_multiplier = {energy:.3f}\n")
    return {"burn_glow": burn}, {"burn_glow": {"emission_texture": T + "kerrid_burn_glow.png"}}


def main() -> int:
    wm.OUT = OUT
    wm.TEX = "res://assets/characters"
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (shader, prio, params, textures) in SHADER_MATERIALS.items():
        wm.write_shader_material(name, shader, prio, params, textures)
    standard, standard_tex = standard_materials()
    for name, body in standard.items():
        wm.write_standard_material(name, body, standard_tex.get(name, {}))
    print(f"wrote {len(SHADER_MATERIALS) + len(standard)} materials to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
