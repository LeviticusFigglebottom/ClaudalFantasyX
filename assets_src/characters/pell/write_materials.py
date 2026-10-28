#!/usr/bin/env python3
"""Writes Pell's hero materials (assets/characters/pell/materials/*.tres) from one table.

    python3 assets_src/characters/pell/write_materials.py

Same writer and conventions as the other heroes' (assets_src/characters/asha/write_materials.py): each material's
resource_name equals the glTF material name it replaces at load time (the hero stage), text resources,
deterministic. Pell's own maps come from pell_textures.py; the generic eye, lash and detail atlases are Asha's
(asha_textures.py), referenced, not copied. Values follow pell.md §5-§7 and character_shading.md.

* **The fur** is the skin shader (`skin_head`, `skin_body`) on Pell's fur maps (pell.md §5, §12 Q8: a sheen lobe along
  the fur flow is Rendering's question; until then the fur's look is the maps plus these parameters): low scattering
  (`sss_strength` 0.25: fur blocks the light), a dark-brown scatter colour, a broad second specular lobe for the
  fur's soft sheen, the pore detail turned down (fur is not skin), the ORM's roughness remapped into ROUGH. The ADR
  0019 dialogue finish `skin_head_dialogue` (painterly 0.6, detail 0.35) as every hero.
* **The wet state** (Ch8, pell.md §5): `skin_head_wet` / `skin_body_wet` (the fur's roughness down
  `wet_roughness_drop`, the albedo `wet_darken` darker), `crest_wet` and `fur_wet` (darker, glossier); the scene swaps
  them in with the Crest's `crest_flat` key.
* The silhouette fringe (`fur`), the brow tufts (`fur_brow`), the whiskers (`whisker`) and the crest (`crest`) are the
  hair shader on `pell_fur.png` and `pell_feather.png`, mostly Lambert (Toma's short-card rule, `kajiya_diffuse_mix`
  0.15) and still (no wind).
* The Kirru eye (pell.md §6.1): a large dark iris `#1E1610` filling most of the visible eye, a warm limbal ring
  `#4A3426`, the sclera dark so it shows only at the corners in `lid_wide`.
* The costume and props atlas (`cloth`): reed, cord, bone, shell, cane and stone; no metal, no gold (pell.md §7: the
  cloth mask's gold and lacquer channels are 0 everywhere). The finger webs (`web`) the same shader, translucent.
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
OUT = ROOT / "assets" / "characters" / "pell" / "materials"
PARAMS = HERE / "pell_params.json"
T = "pell/textures/"
A = "asha/textures/"
ROUGH = (0.5, 0.95)  # pell_textures.ROUGH: the ORM's roughness range


def col(hexv: str, a: float = 1.0) -> str:
    h = hexv.lstrip("#")
    r, g, b = (round(int(h[i:i + 2], 16) / 255.0, 3) for i in (0, 2, 4))
    return f"Color({r}, {g}, {b}, {a})"


def tint(k: float) -> str:
    return f"Color({k:.3f}, {k:.3f}, {k:.3f}, 1)"


def fur_skin(extra: dict) -> dict:
    """The skin shader's response for fur (see the module doc)."""
    fp = extra["_fur"]
    return {"col_scatter": col("#4A2E22"), "sss_strength": str(fp["sss_thickness"]), "transmission_strength": "0.1",
            "diffuse_wrap": "0.22", "normal_blur": "0.3", "shadow_scatter": "0.4", "curvature_scale": "0.6",
            "roughness_min": str(ROUGH[0]), "roughness_max": str(ROUGH[1]), "micro_roughness": "0.08",
            "specular_scale": "0.35", "lobe_roughness_b": "2.2", "lobe_mix": "0.6", "cavity_albedo": "0.3",
            "cavity_specular": "0.9"}


def wet(extra: dict, params: dict) -> dict:
    fp = extra["_fur"]
    d = float(fp["wet_roughness_drop"])
    out = dict(params)
    out["roughness_min"] = str(round(max(ROUGH[0] - d, 0.05), 3))
    out["roughness_max"] = str(round(ROUGH[1] - d, 3))
    out["col_albedo"] = tint(1.0 - float(fp["wet_darken"]))
    out["specular_scale"] = "0.9"
    return out


def tables(extra: dict) -> dict[str, tuple[str, int, dict, dict]]:
    fp, cr, wp = extra["_fur"], extra["_crest"], extra["_whiskers"]
    skin_head = {"tex_albedo": T + "pell_head_albedo.png", "tex_normal": T + "pell_head_normal.png",
                 "tex_orm": T + "pell_head_orm.png", "tex_skin_mask": T + "pell_head_skinmask.png",
                 "tex_detail_normal": A + "asha_thread_detail_normal.png"}  # strands, not pores
    skin_body = {"tex_albedo": T + "pell_body_albedo.png", "tex_normal": T + "pell_body_normal.png",
                 "tex_orm": T + "pell_body_orm.png", "tex_skin_mask": T + "pell_body_skinmask.png",
                 "tex_detail_normal": A + "asha_thread_detail_normal.png"}
    cloth = {"tex_albedo": T + "pell_cloth_albedo.png", "tex_normal": T + "pell_cloth_normal.png",
             "tex_orm": T + "pell_cloth_orm.png", "tex_cloth_mask": T + "pell_cloth_clothmask.png",
             "tex_detail_normal": A + "asha_thread_detail_normal.png"}
    fur = fur_skin(extra)
    head = {**fur, "painterly": "0.2", "detail_tiling": "200.0", "detail_strength": "0.3", "normal_strength": "0.8"}
    head_dlg = {**fur, "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0",
                "detail_strength": "0.35", "normal_strength": "0.8"}
    body = {**fur, "painterly": "0.2", "detail_tiling": "160.0", "detail_strength": "0.3", "normal_strength": "0.8"}
    still = {"wind_response": "0.0"}
    flat = {"kajiya_diffuse_mix": "0.15", "diffuse_wrap": "0.3", "flow_strength": "0.0"}
    fur_cards = {**flat, **still, "col_root": col("#2E2219"), "col_tip": col("#4A372A"), "tip_start": "0.5",
                 "col_spec_primary": col("#C8B8A4"), "spec_primary_intensity": "0.1", "spec_primary_exponent": "60.0",
                 "spec_secondary_intensity": "0.0", "col_transmission": col("#3B2B22"), "transmission_strength": "0.1",
                 "indirect_specular": "0.04", "root_occlusion": "0.85", "depth_occlusion": "0.85",
                 "alpha_boost": "0.85", "strand_value_jitter": "0.12"}
    fur_wet = {**fur_cards, "col_root": col("#241A13"), "col_tip": col("#33261C"), "spec_primary_intensity": "0.3",
               "spec_primary_exponent": "120.0", "alpha_boost": "0.75"}
    brow = {**fur_cards, "col_root": col("#5A4434"), "col_tip": col("#8C7C68"), "tip_start": "0.4",
            "alpha_boost": "1.2"}
    whisker = {**flat, **still, "col_root": col(wp["colour"]), "col_tip": col(wp["colour"]),
               "col_spec_primary": col("#FFFFFF"), "spec_primary_intensity": "0.25", "spec_primary_exponent": "90.0",
               "spec_secondary_intensity": "0.0", "transmission_strength": "0.6", "col_transmission": col("#D8D0C0"),
               "indirect_specular": "0.1", "root_occlusion": "0.4", "depth_occlusion": "0.2", "alpha_boost": "1.6",
               "strand_value_jitter": "0.05"}
    crest = {"flow_strength": "0.0", **still, "col_root": col(cr["colour"]), "col_tip": col(cr["tips"]),
             "tip_start": "0.78", "col_spec_primary": col("#E8E6E0"), "spec_primary_intensity": "0.12",
             "spec_primary_exponent": "40.0", "spec_secondary_intensity": "0.04", "col_spec_secondary": col("#8A867E"),
             "col_transmission": col("#C8C6BE"), "transmission_strength": "0.8", "kajiya_diffuse_mix": "0.35",
             "diffuse_wrap": "0.45", "root_occlusion": "0.6", "depth_occlusion": "0.6", "alpha_boost": "1.3",
             "strand_value_jitter": "0.1"}
    crest_wet = {**crest, "col_root": col("#7C7A74"), "col_tip": col("#3E3B37"), "spec_primary_intensity": "0.35",
                 "spec_primary_exponent": "110.0", "transmission_strength": "0.3", "alpha_boost": "1.5"}
    return {
        "skin_head": ("character_skin", 0, head, skin_head),
        "skin_head_dialogue": ("character_skin", 0, head_dlg, skin_head),
        "skin_head_wet": ("character_skin", 0, wet(extra, head), skin_head),
        "skin_body": ("character_skin", 0, body, skin_body),
        "skin_body_wet": ("character_skin", 0, wet(extra, body), skin_body),
        "eye": ("character_eye", 0, {"eye_radius_m": "0.0134", "iris_radius_m": "0.0102", "pupil_radius": "0.42",
                                     "col_iris": col("#1E1610"), "col_limbal": col("#4A3426"), "limbal_width": "0.12",
                                     "limbus_softness": "0.06", "col_sclera": col("#3E2E26"),
                                     "col_sclera_scatter": col("#4A2E26")},
                {"tex_iris": A + "asha_iris.png", "tex_sclera": A + "asha_sclera.png"}),
        "cornea": ("character_cornea", 1, {}, {}),
        "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "1.0", "corner_strength": "0.75"}, {}),
        "tear_line": ("character_tear_line", 3, {}, {}),
        "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.05",
                                       "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                       "indirect_specular": "0.03", "col_root": col("#1A1310"),
                                       "col_tip": col("#2A1E18"), **still},
                 {"tex_hair": A + "asha_facehair.png"}),
        "fur": ("character_hair", 0, fur_cards, {"tex_hair": T + "pell_fur.png"}),
        "fur_wet": ("character_hair", 0, fur_wet, {"tex_hair": T + "pell_fur.png"}),
        "fur_brow": ("character_hair", 0, brow, {"tex_hair": T + "pell_fur.png"}),
        "whisker": ("character_hair", 0, whisker, {"tex_hair": T + "pell_fur.png"}),
        "crest": ("character_hair", 0, crest, {"tex_hair": T + "pell_feather.png"}),
        "crest_wet": ("character_hair", 0, crest_wet, {"tex_hair": T + "pell_feather.png"}),
        # reed, cord, bone, shell, cane and stone: the mask's A carries the reed's and the cords' fibre sheen; no
        # gold, no lacquer, no metal (pell.md §7)
        "cloth": ("character_cloth", 0, {"detail_tiling": "140.0", "sheen_tint": "0.85", "sheen_intensity": "0.35",
                                         "roughness_scale": "1.0", "transmission": "0.1"}, cloth),
        "web": ("character_cloth", 0, {"detail_strength": "0.2", "sheen_intensity": "0.0", "roughness_scale": "1.0",
                                       "transmission": "0.6"}, cloth),
        # Asha's mouth family (character_mouth, the cavity bounce), reading Pell's head atlas
        "teeth": ("character_mouth", 0, {"col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06",
                                         "ao_light_affect": "0.35"},
                  {"tex_albedo": T + "pell_head_albedo.png", "tex_orm": T + "pell_head_orm.png"}),
        "tongue": ("character_mouth", 0, {"col_albedo": "Color(0.42, 0.22, 0.21, 1)", "roughness": "0.6",
                                          "specular": "0.25"}, {}),
        "mouth": ("character_mouth", 0, {"col_albedo": "Color(1, 1, 1, 1)", "roughness": "0.5",
                                         "roughness_from_orm": "0.0", "ao_light_affect": "0.5"},
                  {"tex_albedo": T + "pell_head_albedo.png", "tex_orm": T + "pell_head_orm.png"}),
    }


def main() -> int:
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    wm.OUT = OUT
    wm.TEX = "res://assets/characters"
    OUT.mkdir(parents=True, exist_ok=True)
    table = tables(extra)
    for name, (shader, prio, params, textures) in table.items():
        wm.write_shader_material(name, shader, prio, params, textures)
    print(f"wrote {len(table)} materials to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
