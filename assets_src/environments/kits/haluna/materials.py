"""Writes the Haluna kit's Godot materials (M1-ENV-01) from one table, so every value is in source.

    python3 assets_src/environments/kits/haluna/materials.py [--out assets/environments/kits/haluna/materials]

Colours are palette.json hex (sRGB, what a Godot colour picker shows; `source_color` uniforms
linearise them). Weathering materials use game/shaders/environment/env_weathering.gdshader (High tier;
WeatheringTide swaps the tier variant at runtime, keeping every parameter). The material names match
the glTF material slots the kit generators write, so a scene maps slot -> material by name.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "haluna" / "materials"
TEX = "res://assets/environments/kits/haluna/textures/"
VEG_TEX = "res://assets/environments/vegetation/"
WEATHER = "res://game/shaders/environment/env_weathering.gdshader"
SHELL = "res://game/shaders/environment/env_wake_shell.gdshader"
BARK = "res://game/shaders/vegetation/vegetation_bark.gdshader"
FOLIAGE = "res://game/shaders/vegetation/vegetation_foliage.gdshader"


def hexc(h: str, a: float = 1.0) -> str:
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return f"Color({r:.4g}, {g:.4g}, {b:.4g}, {a:g})"


# Shared weathering defaults (haluna.md §4); each material overrides what it needs.
WEATHER_BASE = {
    "tex_detail": ("tex", TEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "col_algae": hexc("#4A5A2E"),
    "col_barnacle": hexc("#E6DAC0"),  # bone
    "col_salt": hexc("#E8E4D8"),
    "col_moss": hexc("#2B5529"),  # palm_green #3E7A3A darkened 30 %
    "col_lichen": hexc("#C08A3A"),
}


def stone(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(WEATHER_BASE)
    d.update({"tex_albedo": ("tex", TEX + albedo), "tex_normal": ("tex", TEX + normal),
              "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


MATERIALS: dict[str, dict] = {
    # M2 final pass (env-art): per-block value spread 0.2 and a deeper cavity, so dry-stacked blocks
    # read one by one; the spray-zone salt is thinner on village walls (it whitened them to plaster).
    "kit_coral_stone": stone("coral_stone_albedo.png", "coral_stone_normal.png", (1.2, 1.2), base_triplanar=True,
                             normal_strength=1.5, roughness_base=0.86, cavity_darken=0.38, ao_strength=0.75,
                             variation_value=0.2, salt_coverage="Vector2(0.15, 0.4)"),
    "kit_coral_concrete": stone("coral_concrete_albedo.png", "coral_concrete_normal.png", (2.0, 2.0),
                                base_triplanar=True, normal_strength=1.1, roughness_base=0.8, cavity_darken=0.5,
                                barnacle_coverage=0.65, salt_coverage="Vector2(0.15, 0.35)",
                                algae_coverage="Vector2(0.6, 0.95)", variation_value=0.16,
                                # Drowned a thousand years (M2 final pass): greyed below lit_ceramic, so
                                # the ruins read as old stone in the sea, not as glowing white posts.
                                col_tint=hexc("#D2D4CB")),
    "kit_mortar_white": stone("coral_stone_albedo.png", "coral_stone_normal.png", (0.9, 0.9), base_triplanar=True,
                              normal_strength=0.35, roughness_base=0.9, col_paint=hexc("#E6E1D6"), paint_cover=0.97,
                              cavity_darken=0.04, erosion_pit_darken=0.05, ao_strength=0.4),
    # The chapel's lime-wash (review-sweep-F S2: "small foreign whiteness"): the albedo ceiling, fully
    # covering a smooth base, so the walls read order_marble white without coral stipple showing through.
    "kit_whitewash": stone("coral_concrete_albedo.png", "coral_concrete_normal.png", (2.0, 2.0), base_triplanar=True,
                           normal_strength=0.12, roughness_base=0.82, col_paint=hexc("#EBE7DF"), paint_cover=1.0,
                           cavity_darken=0.02, ao_strength=0.35, variation_value=0.03, erosion_pit_darken=0.05,
                           use_moss=False, use_algae=False, use_barnacles=False),
    "kit_order_marble": stone("coral_concrete_albedo.png", "coral_concrete_normal.png", (1.5, 1.5),
                              base_triplanar=True, normal_strength=0.25, roughness_base=0.38, specular_base=0.5,
                              col_paint=hexc("#E4DED3"), paint_cover=0.9, cavity_darken=0.05, use_moss=False,
                              use_algae=False, use_barnacles=False),
    # Sun-silvered (review-sweep-F S6): a cool grey tint takes the boards down to timber_weathered and
    # a wider per-board variation keeps them from reading as one new surface.
    "kit_timber": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                        col_tint=hexc("#CFCDC8"), normal_strength=1.2, roughness_base=0.8, specular_base=0.3,
                        cavity_darken=0.45, variation_value=0.24, variation_warmth=0.03, moss_min_height_m=1.0),
    # The lintel-gull carvings (M2 final pass): the loft UVs stretched the board grain into hard
    # stripes (H03 gull L p05 0.20 .. p95 0.78). Triplanar grain at carving scale, sun-silvered towards
    # timber_weathered +1, with a soft cavity: one carved piece of grey driftwood, not striped plywood.
    "kit_carved_wood": stone("timber_albedo.png", "timber_normal.png", (0.25, 0.5), base_triplanar=True,
                             triplanar_sharpness=6.0, col_tint=hexc("#E4E0DA"), normal_strength=0.7,
                             roughness_base=0.78, specular_base=0.3, cavity_darken=0.25, variation_value=0.06,
                             variation_warmth=0.02, use_algae=False, use_barnacles=False, moss_min_height_m=3.0),
    "kit_thatch": stone("thatch_albedo.png", "thatch_normal.png", (1.6, 1.6), base_triplanar=False,
                        # A blue-weighted gain (measured, M2 final pass): the roof rendered at Oklab C 0.098
                        # against thatch's 0.070-0.079 on screen; this brings it back onto the swatch.
                        col_tint="Color(1.0, 1.04, 1.16, 1)",
                        normal_strength=1.8, roughness_base=0.95, specular_base=0.2, cavity_darken=0.5,
                        variation_value=0.18, use_algae=False,
                        use_barnacles=False, use_salt=False, moss_normal_y=0.5),
    "kit_roof_tile": stone("roof_tile_albedo.png", "roof_tile_normal.png", (2.0, 2.4), base_triplanar=False,
                           normal_strength=1.0, roughness_base=0.62, specular_base=0.45, cavity_darken=0.2,
                           use_algae=False, use_barnacles=False, moss_normal_y=0.75),
    # Pandanus infill weathers grey-brown and unevenly (M2 final pass): a sun-greyed tint, per-panel
    # value spread and a deeper weave cavity, so a house wall is not one flat ochre card at H02 range.
    "kit_woven_panel": stone("woven_panel_albedo.png", "woven_panel_normal.png", (0.8, 0.8), base_triplanar=False,
                             col_tint=hexc("#DCD3C6"), normal_strength=1.4, roughness_base=0.9, specular_base=0.25,
                             cavity_darken=0.5, variation_value=0.22, use_algae=False, use_barnacles=False,
                             use_moss=False),
    "kit_lashing": stone("woven_panel_albedo.png", "woven_panel_normal.png", (0.12, 0.12), base_triplanar=False,
                         col_tint=hexc("#9C7E5A"), normal_strength=1.0, roughness_base=0.95, use_algae=False,
                         use_barnacles=False, use_moss=False),
    "kit_paint_sea_blue": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                                col_paint=hexc("#3C78A8"), paint_cover=0.82, roughness_base=0.7, specular_base=0.4),
    "kit_paint_red": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                           col_paint=hexc("#A8352A"), paint_cover=0.82, roughness_base=0.7, specular_base=0.4),
    "kit_wake_shell": {"shader": SHELL, "params": {"tex_glyph": ("tex", TEX + "shell_glyph.png")}},
    "kit_canopy_bark": {"shader": BARK, "params": {
        "tex_albedo": ("tex", VEG_TEX + "frangipani_bark_albedo.png"),
        "tex_normal": ("tex", VEG_TEX + "frangipani_bark_normal.png"),
        "wind_response": 0.15, "plant_height_m": 14, "sway_lean": 0.005, "sway_amplitude": 0.004,
        "sway_frequency_hz": 0.15, "gust_contrast": 1, "secondary_amplitude_m": 0.05, "flutter_amplitude_m": 0,
        # Pale banyan bark, low occlusion (review-sweep-F S4: the aerial roots read as near-black poles).
        # The shared frangipani bark texture averages ~0.26 linear, so the tint is a GAIN above 1: it
        # lifts the bark to ~0.40 linear albedo (a pale grey #AAA59A), well inside the palette floor and
        # ceiling. Shaded roots then sit about one stop under the shaded sand instead of at the toe.
        "col_base": "Color(1.18, 1.16, 1.15, 1)", "col_top": "Color(1.24, 1.21, 1.17, 1)",
        "normal_strength": 1.3, "roughness_value": 0.9,
        "ao_strength": 0.35}},
}
_FOLIAGE = {
    "tex_albedo": ("tex", TEX + "canopy_cluster_albedo.png"),
    "tex_normal_trans": ("tex", TEX + "canopy_cluster_normal.png"),
    "wind_response": 0.15, "plant_height_m": 14, "sway_lean": 0.005, "sway_amplitude": 0.004,
    "sway_frequency_hz": 0.15, "gust_contrast": 1, "secondary_amplitude_m": 0.05, "secondary_frequency_hz": 0.6,
    "flutter_amplitude_m": 0.01, "flutter_frequency_hz": 3, "col_tint": hexc("#FFFFFF"),
    "col_tint_variation": "Color(1.1, 1.05, 0.75, 1)", "tint_variation": 0.3, "underside_lighten": 0.2,
    "alpha_cutoff": 0.5, "mip_coverage_boost": 0.3, "roughness_value": 0.5, "specular_value": 0.45,
    "ao_strength": 0.85, "ao_in_albedo": 0.6, "diffuse_wrap": 0.3, "col_translucency": "Color(0.75, 0.95, 0.3, 1)",
    "translucency": 1.0, "translucency_shadow_floor": 0.3, "translucency_focus": 6, "translucency_forward": 1.2,
}
MATERIALS["kit_canopy_leaf"] = {"shader": FOLIAGE, "params": dict(_FOLIAGE)}
MATERIALS["kit_canopy_leaf_dark"] = {"shader": FOLIAGE, "params": dict(_FOLIAGE, plant_height_m=8,
                                                                     col_tint=hexc("#7E9C8A"), translucency=0.6)}

# Cloth (awnings): one slot, three dyes picked per placement (haluna.md §1.2 market).
for _dye, _hex in (("indigo", "#2B3A6B"), ("sea_blue", "#3C78A8"), ("sand", "#C9B48E")):
    MATERIALS[f"kit_cloth_{_dye}"] = stone("woven_panel_albedo.png", "woven_panel_normal.png", (0.25, 0.25),
                                           base_triplanar=False, col_paint=hexc(_hex), paint_cover=0.92,
                                           normal_strength=0.4, roughness_base=0.92, specular_base=0.25,
                                           use_algae=False, use_barnacles=False, use_moss=False, use_salt=False)

MATERIALS["kit_cloth"] = MATERIALS["kit_cloth_sand"]  # the glTF slot's default dye

# StandardMaterial3D pieces (no weathering stack needed).
STANDARD: dict[str, dict] = {
    "kit_garland": {"albedo_color": hexc("#F0E8D8"), "roughness": 0.5, "cull_mode": 2,
                    "backlight_enabled": "true", "backlight": "Color(0.6, 0.55, 0.4, 1)"},
    "kit_garland_throat": {"albedo_color": hexc("#FFD27A"), "roughness": 0.5, "cull_mode": 2},
    "kit_interior_dark": {"albedo_color": hexc("#2B2622"), "roughness": 1.0},
    "kit_rebar": {"albedo_color": hexc("#5A3422"), "roughness": 0.85, "metallic": 0.25},
    "kit_gold_leaf": {"albedo_color": hexc("#D4A437"), "roughness": 0.28, "metallic": 1.0},
    "kit_lacquer_red": {"albedo_color": hexc("#B3261E"), "roughness": 0.22, "clearcoat_enabled": "true",
                        "clearcoat": 0.6},
    # Alpha hash, not blend (review-sweep-F S6): a blended net writes no depth, so the (transparent)
    # sea drew over it and the nets vanished. Not scissor either (review-sweep-H R6): a threshold over
    # the ~0.56-coverage twine turned the far mips into a solid sheet. A hashed cutout keeps the
    # mip's coverage as a dither, which every preset's temporal AA (TAA or FSR2) resolves.
    "kit_net": {"transparency": 3, "cull_mode": 2,
                "albedo_texture": ("tex", TEX + "net_albedo.png"), "roughness": 0.9,
                "uv1_scale": "Vector3(2.5, 2.5, 1)", "texture_filter": 5},
    "kit_salt_glass": {"transparency": 1, "albedo_color": hexc("#BFE6E0", 0.55), "roughness": 0.06,
                       "metallic_specular": 0.7},
}


def _value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return f"{v:g}"
    return str(v)


def write_shader_material(path: Path, name: str, spec: dict) -> None:
    textures = sorted({v[1] for v in spec["params"].values() if isinstance(v, tuple)})
    ids = {t: f"{i + 2}_tex" for i, t in enumerate(textures)}
    lines = [f'[gd_resource type="ShaderMaterial" load_steps={len(textures) + 2} format=3]', "",
             f'[ext_resource type="Shader" path="{spec["shader"]}" id="1_shader"]']
    lines += [f'[ext_resource type="Texture2D" path="{t}" id="{ids[t]}"]' for t in textures]
    lines += ["", "[resource]", f'resource_name = "{name}"', 'shader = ExtResource("1_shader")']
    for k in sorted(spec["params"]):
        v = spec["params"][k]
        val = f'ExtResource("{ids[v[1]]}")' if isinstance(v, tuple) else _value(v)
        lines.append(f"shader_parameter/{k} = {val}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_standard_material(path: Path, name: str, spec: dict) -> None:
    textures = sorted({v[1] for v in spec.values() if isinstance(v, tuple)})
    ids = {t: f"{i + 1}_tex" for i, t in enumerate(textures)}
    lines = [f'[gd_resource type="StandardMaterial3D" load_steps={len(textures) + 1} format=3]', ""]
    lines += [f'[ext_resource type="Texture2D" path="{t}" id="{ids[t]}"]' for t in textures]
    if textures:
        lines.append("")
    lines += ["[resource]", f'resource_name = "{name}"']
    for k in sorted(spec):
        v = spec[k]
        lines.append(f'{k} = {ExtResource(ids[v[1]]) if isinstance(v, tuple) else _value(v)}')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ExtResource(i: str) -> str:  # noqa: N802 (mirrors the .tres syntax)
    return f'ExtResource("{i}")'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in sorted(MATERIALS.items()):
        write_shader_material(out / f"{name}.tres", name, spec)
    for name, spec in sorted(STANDARD.items()):
        write_standard_material(out / f"{name}.tres", name, spec)
    print(f"KIT_MAT {len(MATERIALS) + len(STANDARD)} materials -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
