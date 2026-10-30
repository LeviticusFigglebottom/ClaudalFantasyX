"""Writes the Oruvel Underway kit's Godot materials (M3-ENV-05) from one table, so every value is in source.

    python3 assets_src/environments/kits/oruvel_underway/ou_materials.py [--out assets/environments/kits/oruvel_underway/materials]

One .tres per glTF slot the kit generators write (ou_common.M_*), so the import's `{asset_dir}/materials/` rule and
HalunaDresser both map slot -> material by name. Colours are palette.json hex or tones derived from it (named beside
each), inside the albedo floor/ceiling. Weathering materials use the shared env_weathering.gdshader (haluna.md §4
stack) with this kit's silt and coral maps and the Haluna kit's coral-concrete, coral-stone, timber, woven-panel and
detail maps (read-only). The writers are the Haluna kit's.

Everything here is under water (oruvel_underway.md §3): the shader's wet layer is on for every surface, so
`wet_darken` stays near 1 (the underwater post already absorbs) and `wet_roughness` moderate; moss and salt are off;
growth is the algae and barnacle layers over the whole depth range (`algae_band_m` -60 to -1.5 m about the datum).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
# the Haluna kit's material writers, read-only: loaded by path under its own name, so a sibling kit's `materials` module (tamsule_bell has one)
# already in sys.modules is never picked up instead.
_HM_SPEC = importlib.util.spec_from_file_location("haluna_materials", HERE.parent / "haluna" / "materials.py")
hm = sys.modules.get("haluna_materials") or importlib.util.module_from_spec(_HM_SPEC)
if "haluna_materials" not in sys.modules:
    sys.modules["haluna_materials"] = hm
    _HM_SPEC.loader.exec_module(hm)

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "oruvel_underway" / "materials"
TEX = "res://assets/environments/kits/oruvel_underway/textures/"
HTEX = "res://assets/environments/kits/haluna/textures/"
WEATHER = "res://game/shaders/environment/env_weathering.gdshader"
hexc = hm.hexc

UNDERWATER_BAND = "Vector2(-60.0, -1.5)"
CORALLINE = hexc("#A98078")  # roof_clay #B5523A greyed: crustose coralline algae, the barnacle layer's colour here

BASE = {
    "tex_detail": ("tex", HTEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "col_algae": hexc("#4F5A3A"),  # the green film on everything (the Haluna #4A5A2E, greyed)
    "col_barnacle": CORALLINE,
    "algae_band_m": UNDERWATER_BAND,
    "barnacle_band_m": UNDERWATER_BAND,
    "barnacle_bump": 1.0,
    "use_moss": False,
    "use_salt": False,
    "wet_darken": 0.9,
    "wet_roughness": 0.5,
    "wet_flatten": 0.15,
}


def weather(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(BASE)
    d.update({"tex_albedo": ("tex", albedo), "tex_normal": ("tex", normal), "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


CONCRETE = (HTEX + "coral_concrete_albedo.png", HTEX + "coral_concrete_normal.png", (2.0, 2.0))
STONE = (HTEX + "coral_stone_albedo.png", HTEX + "coral_stone_normal.png", (0.8, 0.8))
TIMBER = (HTEX + "timber_albedo.png", HTEX + "timber_normal.png", (0.4, 1.6))
WOVEN = (HTEX + "woven_panel_albedo.png", HTEX + "woven_panel_normal.png", (0.12, 0.12))
CORAL = (TEX + "coral_albedo.png", TEX + "coral_normal.png", (0.45, 0.45))
DRY_WALL = {"use_algae": False, "use_barnacles": False, "wet_darken": 1.0, "wet_roughness": 0.85, "wet_flatten": 0.0}

MATERIALS: dict[str, dict] = {
    # Lit Age coral-concrete drowned four hundred years: grey-green, a film of algae, coralline crust, worn edges.
    "ou_concrete": weather(*CONCRETE, base_triplanar=True, col_tint=hexc("#B7BCAF"), normal_strength=1.1,
                           roughness_base=0.85, cavity_darken=0.5, variation_value=0.16,
                           algae_coverage="Vector2(0.35, 0.7)", barnacle_coverage=0.16),
    # The bell-room above the air line: paler, dry, calcite gathered in the hollows (the salt layer, banded low).
    "ou_concrete_dry": weather(*CONCRETE, base_triplanar=True, col_tint=hexc("#CFCFC6"), normal_strength=1.0,
                               roughness_base=0.9, cavity_darken=0.45, variation_value=0.1, use_salt=True,
                               col_salt=hexc("#E8E4D8"), salt_band_m="Vector2(-40.0, 0.0)",
                               salt_coverage="Vector2(0.25, 0.5)", **DRY_WALL),
    # The tide-ring: bone-white calcite crust.
    "ou_calcite": weather(*STONE, base_triplanar=True, col_paint=hexc("#D9D2C2"), paint_cover=0.9,
                          normal_strength=1.2, roughness_base=0.9, cavity_darken=0.3, **DRY_WALL),
    # White Lit Age ceramic (lit_ceramic) gone green with coral: a thinner film, crust in the joints.
    "ou_ceramic": weather(*CONCRETE, base_triplanar=True, col_paint=hexc("#DCE3E0"), paint_cover=0.7,
                          normal_strength=0.3, roughness_base=0.45, specular_base=0.5, cavity_darken=0.35,
                          variation_value=0.1, col_algae=hexc("#5A6A44"), algae_coverage="Vector2(0.3, 0.65)",
                          barnacle_coverage=0.25),
    # Silt and shell sand over the roof; a faint diatom film in patches.
    "ou_silt": weather(TEX + "silt_albedo.png", TEX + "silt_normal.png", (2.5, 2.5), base_triplanar=True,
                       normal_strength=0.6, roughness_base=0.92, specular_base=0.3, cavity_darken=0.3,
                       ao_strength=0.7, variation_value=0.05, col_algae=hexc("#6A6B4A"),
                       algae_coverage="Vector2(0.05, 0.25)", use_barnacles=False, wet_darken=0.92,
                       wet_roughness=0.8, wet_flatten=0.0, detail_scale_m=1.2),
    # The dead ship's frames: black-brown tarred timber under crust and film.
    "ou_timber_tar": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#5E544C"), normal_strength=1.4,
                             roughness_base=0.75, specular_base=0.3, cavity_darken=0.5, variation_value=0.18,
                             algae_coverage="Vector2(0.3, 0.6)", barnacle_coverage=0.45),
    # The raft-town's hull bottoms, seen from below: dark timber, a beard of film and crust.
    "ou_hull": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#4E4640"), normal_strength=1.2,
                       roughness_base=0.8, cavity_darken=0.45, variation_value=0.2, col_algae=hexc("#4A5530"),
                       algae_coverage="Vector2(0.4, 0.8)", barnacle_coverage=0.5, algae_band_m="Vector2(-3.0, 0.2)",
                       barnacle_band_m="Vector2(-3.0, 0.0)"),
    "ou_cord_old": weather(*WOVEN, base_triplanar=False, col_paint=hexc("#7E705A"), paint_cover=0.8,
                           normal_strength=0.9, roughness_base=0.95, algae_coverage="Vector2(0.1, 0.3)",
                           use_barnacles=False),
    "ou_cord_new": weather(*WOVEN, base_triplanar=False, col_paint=hexc("#C9B48E"), paint_cover=0.85,  # sand_cloth
                           normal_strength=0.9, roughness_base=0.95, use_algae=False, use_barnacles=False),
}
# The reef: massive coral texture, painted (oruvel_underway.md §3).
for _name, _hex in (("ou_coral_bone", "#D9CDB4"),  # bone, bleached
                    ("ou_coral_ochre", "#B08A55"),  # dusk_gold #F2A64A greyed
                    ("ou_coral_rose", "#A8705F"),  # roof_clay #B5523A greyed
                    ("ou_coral_teal", "#5E9A96"),  # faded_teal_cloth: soft corals and fans
                    ("ou_sponge", "#8C5E45")):  # laterite #A8573A greyed
    MATERIALS[_name] = weather(*CORAL, base_triplanar=True, col_paint=hexc(_hex), paint_cover=0.72,
                               normal_strength=2.2, roughness_base=0.75, specular_base=0.35, cavity_darken=0.65,
                               variation_value=0.12, variation_warmth=0.04, use_algae=False, use_barnacles=False,
                               wet_darken=0.95)

STANDARD: dict[str, dict] = {
    "ou_rebar": {"albedo_color": hexc("#5A3422"), "roughness": 0.85, "metallic": 0.25},
    "ou_iron": {"albedo_color": hexc("#4A3A30"), "metallic": 0.5, "roughness": 0.78},
    # The one bright metal in the zone: the lantern turns it gold.
    "ou_brass": {"albedo_color": hexc("#B08D57"), "metallic": 0.85, "roughness": 0.42},
    "ou_patina": {"albedo_color": hexc("#5F8A78"), "metallic": 0.15, "roughness": 0.78},  # bronze_patina
    # The empty housings' last shards: dark, glossy, no light (no bound light anywhere in Ch1).
    "ou_glass_dark": {"albedo_color": hexc("#2C3639"), "roughness": 0.15, "metallic_specular": 0.8,
                      "cull_mode": 2},
    "ou_lead": {"albedo_color": hexc("#55585A"), "metallic": 0.4, "roughness": 0.6},
    # Seagrass and weed: two-sided straps.
    "ou_seagrass": {"albedo_color": hexc("#4E6A3A"), "roughness": 0.6, "cull_mode": 2},  # palm_green toward olive
    "ou_seagrass_tip": {"albedo_color": hexc("#7A6E45"), "roughness": 0.75, "cull_mode": 2},
    "ou_weed": {"albedo_color": hexc("#525A36"), "roughness": 0.7, "cull_mode": 2},
    # The preview's stand-in lantern: oil_lamp flame and salt_glass chimney.
    "ou_flame": {"albedo_color": hexc("#FFB16E"), "emission_enabled": "true", "emission": hexc("#FFB16E"),
                 "emission_energy_multiplier": 3.0, "shading_mode": 0},
    "ou_lantern_glass": {"transparency": 1, "albedo_color": hexc("#BFE6E0", 0.3), "roughness": 0.05,
                         "metallic_specular": 0.8},
}

# The Ch1 Underway dressing pass (the Lead, 10-30: the underwater light, the caustics): the zone is walked under the
# surface, where the water shader's projected caustics never reach, so every weathered surface lights its own web
# (env_weathering uw_caustics), strongest on the floor, fading with depth and into the murk.
UW_CAUSTICS = 1.2
for _spec in MATERIALS.values():
    _spec["params"]["uw_caustics"] = UW_CAUSTICS


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in sorted(MATERIALS.items()):
        hm.write_shader_material(out / f"{name}.tres", name, spec)
    for name, spec in sorted(STANDARD.items()):
        hm.write_standard_material(out / f"{name}.tres", name, spec)
    print(f"KIT_MAT {len(MATERIALS) + len(STANDARD)} materials -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
