#!/usr/bin/env python3
"""Writes each Haluna villager's materials (assets/characters/villagers/<npc>/materials/*.tres) and its actor
scene (<npc>_actor.tscn: the GLB turned to face -Z, the scene m2-slice instances for an NPC capsule), M2-CHR-03.

    python3 assets_src/characters/villagers/write_materials.py [npc ...]     # default: every params file

Same writer and conventions as the heroes' (assets_src/characters/asha/write_materials.py, loaded
by path): each material's resource_name equals the glTF material name, and the `characters` import
rule (game/data/import/characters.json) maps every slot to `<asset dir>/materials/<slot>.tres`, so an
instanced villager GLB is already dressed. Text resources, deterministic.

Per villager: the skin maps from villager_textures.py; the shared villager cloth atlas tinted per
material from `_tints` (cloth_a/b/c; leather untinted); hair, grey hair, lash and brow colours from
`_hair`; the iris from `_eyes`; optional per-material cloth shader parameters from `_cloth_params` (M3-CHR-516: the
smith's leather apron is the cloth shader, less sheen, smoother); optional brow shader parameters from
`_hair.brow_params` (M3-CHR-536: the old villagers' sparse, salt-and-pepper brows). Generic atlases (eyes, hair, lashes, brows, detail normals) are
Asha's.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("asha_write_materials", HERE.parent / "asha" / "write_materials.py")
wm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wm)

ROOT = HERE.parents[2]
PARAMS_DIR = HERE / "params"
A = "asha/textures/"
SHORT_HAIR = "toma/textures/toma_shorthair.png"  # M3-CHR-592 `tufts`: toma_textures.short_hair_atlas
# and toma's crop shading (toma/write_materials.py): a near-surface, mostly wrapped Lambert, a low broad highlight
TUFT_HAIR = {"flow_strength": "0.0", "kajiya_diffuse_mix": "0.15", "diffuse_wrap": "0.3",
             "spec_primary_intensity": "0.07", "spec_primary_exponent": "60.0", "spec_secondary_intensity": "0.0", "root_occlusion": "0.85",
             "depth_occlusion": "0.85", "alpha_boost": "0.85", "strand_value_jitter": "0.12"}
# the scene m2-slice swaps in for a haluna.tscn NPC capsule: the GLB turned to face -Z, as the capsules'
# Facing boxes do (a glTF character faces +Z); the import rule has already dressed it
ACTOR = """[gd_scene load_steps=2 format=3]

[ext_resource type="PackedScene" path="res://assets/characters/villagers/{npc}/{npc}.glb" id="glb"]

[node name="{Name}" type="Node3D"]

[node name="Model" parent="." instance=ExtResource("glb")]
transform = Transform3D(-1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0)
"""
CLOTH = "villagers/textures/villagers_cloth_"


def colour(hex_: str) -> str:
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return f"Color({r:.3f}, {g:.3f}, {b:.3f}, 1)"


def tables(npc: str, extra: dict) -> tuple[dict, dict, dict]:
    T = f"villagers/{npc}/textures/{npc}_"
    hp = extra["_hair"]
    hair = colour(hp.get("colour", "#201A16"))
    grey = colour(hp.get("grey", "#8C867D"))
    brow = colour(hp.get("brow", hp.get("colour", "#201A16")))
    spec = colour(hp.get("spec", "#D8CCC0"))
    still = {"wind_response": "0.0"}
    iris = colour(extra.get("_eyes", {}).get("iris", "#2A1A10"))
    skin = {"tex_albedo": T + "head_albedo.png", "tex_normal": T + "head_normal.png", "tex_orm": T + "head_orm.png",
            "tex_skin_mask": T + "head_skinmask.png", "tex_detail_normal": A + "asha_skin_detail_normal.png"}
    age = float(extra["_skin"].get("age", 0.0))
    rmin, rmax = f"{0.44 + 0.06 * age:.2f}", f"{0.62 + 0.08 * age:.2f}"
    hair_params = {"col_root": hair, "col_tip": hair, "col_spec_primary": spec, "spec_primary_intensity": "0.16",
                   "spec_primary_exponent": "120.0", "spec_secondary_intensity": "0.06",
                   "transmission_strength": "0.2", "indirect_specular": "0.06", "root_occlusion": "0.6",
                   "depth_occlusion": "0.65", "alpha_boost": "1.4", **still}
    hair_tex = {"tex_hair": A + "asha_hair.png", "tex_hairflow": A + "asha_hairflow.png"}
    if hp.get("tufts"):  # M3-CHR-592: Toma's short-hair atlas and his matte crop (strands along +V: no flow map)
        hair_tex = {"tex_hair": SHORT_HAIR}
        hair_params = {**hair_params, **TUFT_HAIR}
    shader = {
        "skin_head": ("character_skin", 0, {
            "painterly": "0.2", "detail_tiling": "64.0", "detail_strength": "0.8", "normal_strength": "1.0",
            "specular_scale": "0.8", "curvature_scale": "1.3", "roughness_min": rmin, "roughness_max": rmax,
            "cavity_albedo": "0.45", "micro_roughness": "0.1"}, skin),
        "skin_head_dialogue": ("character_skin", 0, {
            "painterly": "0.6", "painterly_form": "0.3", "detail_tiling": "64.0", "detail_strength": "0.35",
            "normal_strength": "0.8", "specular_scale": "0.8", "roughness_min": rmin, "roughness_max": rmax,
            "cavity_albedo": "0.45"}, skin),
        "skin_body": ("character_skin", 0, {"painterly": "0.2", "detail_tiling": "40.0", "detail_strength": "0.7"},
                      {"tex_albedo": T + "body_albedo.png", "tex_normal": T + "body_normal.png",
                       "tex_orm": T + "body_orm.png", "tex_skin_mask": T + "body_skinmask.png",
                       "tex_detail_normal": A + "asha_skin_detail_normal.png"}),
        "eye": ("character_eye", 0, {"col_sclera": "Color(0.79, 0.735, 0.68, 1)", "limbus_softness": "0.09",
                                     "col_iris": iris}, {"tex_iris": A + "asha_iris.png",
                                                         "tex_sclera": A + "asha_sclera.png"}),
        "cornea": ("character_cornea", 1, {}, {}),
        "eye_occlusion": ("character_eye_occlusion", 2, {"upper_strength": "0.95", "corner_strength": "0.7"}, {}),
        "tear_line": ("character_tear_line", 3, {}, {}),
        "lash": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.06",
                                       "spec_secondary_intensity": "0.0", "transmission_strength": "0.1",
                                       "indirect_specular": "0.03", "col_root": brow, "col_tip": brow, **still},
                 {"tex_hair": A + "asha_facehair.png"}),
        "brow": ("character_hair", 0, {"flow_strength": "0.0", "spec_primary_intensity": "0.08", "alpha_boost": "1.6",
                                       "spec_secondary_intensity": "0.05", "transmission_strength": "0.2",
                                       "root_occlusion": "0.2", "indirect_specular": "0.05",
                                       "col_root": brow, "col_tip": brow, **still,
                                       **hp.get("brow_params", {})},  # M3-CHR-536 (optional): an aged brow
                 {"tex_hair": A + "asha_facehair.png"}),
        "hair": ("character_hair", 0, hair_params, hair_tex),
        "hair_grey": ("character_hair", 0, {**hair_params, "col_root": grey, "col_tip": grey}, hair_tex),
        # M1-RND-21's mouth family, reading this villager's head atlas (Asha's values)
        "teeth": ("character_mouth", 0, {
            "col_albedo": "Color(1, 1, 1, 1)", "roughness": "1.0", "specular": "0.06", "ao_light_affect": "0.35",
        }, {"tex_albedo": T + "head_albedo.png", "tex_orm": T + "head_orm.png"}),
        "tongue": ("character_mouth", 0, {"col_albedo": "Color(0.55, 0.26, 0.25, 1)", "roughness": "0.6",
                                          "specular": "0.25"}, {}),
        "mouth": ("character_mouth", 0, {"col_albedo": "Color(0.28, 0.1, 0.09, 1)", "roughness": "0.5",
                                         "roughness_from_orm": "0.0", "ao_light_affect": "0.5"},
                  {"tex_orm": T + "head_orm.png"}),
    }
    cloth_tex = {"tex_albedo": CLOTH + "albedo.png", "tex_normal": CLOTH + "normal.png", "tex_orm": CLOTH + "orm.png",
                 "tex_cloth_mask": CLOTH + "clothmask.png", "tex_detail_normal": A + "asha_thread_detail_normal.png"}
    tuned = extra.get("_cloth_params", {})  # M3-CHR-516 (optional): extra cloth shader parameters per material
    for name, hex_ in extra["_tints"].items():
        shader[name] = ("character_cloth", 0, {"detail_tiling": "150.0", "col_albedo": colour(hex_),
                                               **tuned.get(name, {})}, cloth_tex)
    return shader, {}, {}


def write(npc: str) -> int:
    extra = json.loads((PARAMS_DIR / f"{npc}.json").read_text(encoding="utf-8"))
    out = ROOT / "assets" / "characters" / "villagers" / npc / "materials"
    wm.OUT = out
    wm.TEX = "res://assets/characters"
    out.mkdir(parents=True, exist_ok=True)
    shader, standard, std_tex = tables(npc, extra)
    for name, (sh, prio, params, textures) in shader.items():
        wm.write_shader_material(name, sh, prio, params, textures)
    for name, body in standard.items():
        wm.write_standard_material(name, body, std_tex.get(name, {}))
    actor = out.parent / f"{npc}_actor.tscn"
    actor.write_text(ACTOR.format(npc=npc, Name=npc.capitalize()), encoding="utf-8")
    print(f"wrote {len(shader) + len(standard)} materials to {out.relative_to(ROOT)} and {actor.relative_to(ROOT)}")
    return 0


def main(argv: list[str]) -> int:
    npcs = argv or sorted(p.stem for p in PARAMS_DIR.glob("*.json"))
    for npc in npcs:
        write(npc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
