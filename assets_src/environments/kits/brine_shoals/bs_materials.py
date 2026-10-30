"""Writes the Brine Shoals kit's Godot materials (M3-ENV-02) from one table, so every value is in source.

    python3 assets_src/environments/kits/brine_shoals/bs_materials.py [--out assets/environments/kits/brine_shoals/materials]

One .tres per glTF slot the kit generators write (bs_common.M_*), so the import's `{asset_dir}/materials/`
rule and HalunaDresser both map slot -> material by name. Colours are palette.json hex or tones derived
from it (named beside each), inside the albedo floor/ceiling. Weathering materials use the shared
env_weathering.gdshader (haluna.md §4 stack) with this kit's mud and char maps and the Haluna kit's
timber, woven-panel, sand, coral and detail maps (read-only). The writers are the Haluna kit's.
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

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "brine_shoals" / "materials"
TEX = "res://assets/environments/kits/brine_shoals/textures/"
HTEX = "res://assets/environments/kits/haluna/textures/"
WEATHER = "res://game/shaders/environment/env_weathering.gdshader"
SMOKE = "res://game/shaders/environment/env_smoke_plume.gdshader"
WAKE = "res://game/shaders/environment/env_boat_wake.gdshader"
hexc = hm.hexc

BASE = {
    "tex_detail": ("tex", HTEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "col_algae": hexc("#4A5A2E"),
    "col_barnacle": hexc("#E6DAC0"),  # bone
    "col_salt": hexc("#E8E4D8"),
    "col_moss": hexc("#2B5529"),
    "col_lichen": hexc("#C08A3A"),
    "use_moss": False,  # no moss anywhere on the shoals: everything is under salt or smoke
}


def weather(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(BASE)
    d.update({"tex_albedo": ("tex", albedo), "tex_normal": ("tex", normal), "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


TIMBER = (HTEX + "timber_albedo.png", HTEX + "timber_normal.png", (0.4, 1.6))
WOVEN = (HTEX + "woven_panel_albedo.png", HTEX + "woven_panel_normal.png", (0.25, 0.25))

MATERIALS: dict[str, dict] = {
    # Tidal mud: warm grey-brown, a thin algae film near the water, salt crust on the high, dry mud. Wet
    # mud is near-mirror (wet_roughness 0.08) so the flats carry the sky (brine_shoals.md, Act I rule).
    "bs_mud": weather(TEX + "mud_albedo.png", TEX + "mud_normal.png", (3.0, 3.0), base_triplanar=True,
                      normal_strength=0.35, roughness_base=0.7, specular_base=0.4, cavity_darken=0.3,
                      ao_strength=0.7, variation_value=0.06, use_barnacles=False,
                      algae_band_m="Vector2(-0.5, -0.05)", algae_coverage="Vector2(0.15, 0.45)",
                      col_algae=hexc("#4F5636"), salt_band_m="Vector2(0.06, 2.0)", salt_coverage="Vector2(0.0, 0.18)",
                      wet_darken=0.62, wet_roughness=0.08, wet_flatten=0.75, capillary_band_m=0.3,
                      detail_scale_m=1.2),
    # The hard: pale shell grit and shingle (the Haluna sand map greyed toward coral_stone_weathered).
    # The hard: grey shell grit and shingle (this kit's shingle map), drier than the flats, salt in the hollows.
    "bs_shell_grit": weather(TEX + "shingle_albedo.png", TEX + "shingle_normal.png", (1.0, 1.0), base_triplanar=True,
                             normal_strength=1.2, roughness_base=0.88, cavity_darken=0.35, variation_value=0.04,
                             use_barnacles=False, algae_coverage="Vector2(0.1, 0.3)",
                             salt_coverage="Vector2(0.05, 0.25)", wet_darken=0.6),
    # Wrecks: tarred near-black brown (#3A3029 at the board face), salt above, barnacles and algae at the
    # low-water line from the shader's height bands.
    "bs_timber_tar": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#5E544C"), normal_strength=1.4,
                             roughness_base=0.7, specular_base=0.35, cavity_darken=0.5, variation_value=0.18,
                             barnacle_coverage=0.6, algae_coverage="Vector2(0.5, 0.85)",
                             salt_coverage="Vector2(0.1, 0.35)", wet_roughness=0.1),
    # The camp's salvaged spars and boards: sun-silvered timber_weathered (the Haluna kit_timber look).
    "bs_timber": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#CFCDC8"), normal_strength=1.2,
                         roughness_base=0.8, specular_base=0.3, cavity_darken=0.45, variation_value=0.22,
                         variation_warmth=0.03, use_algae=False, use_barnacles=False,
                         salt_coverage="Vector2(0.05, 0.2)"),
    # Deep char: alligatored charcoal, triplanar so the checks run the same on every face.
    "bs_char": weather(TEX + "char_albedo.png", TEX + "char_normal.png", (0.5, 0.5), base_triplanar=True,
                       normal_strength=1.6, roughness_base=0.92, specular_base=0.25, cavity_darken=0.3,
                       ao_strength=0.6, variation_value=0.1, erosion_lighten=0.04, use_algae=False,
                       use_barnacles=False, use_salt=False),
    # Smoke-stained, scorched timber: timber_weathered darkened about 55 % and browned.
    "bs_scorch": weather(*TIMBER, base_triplanar=False, col_tint=hexc("#6E5A48"), normal_strength=1.2,
                         roughness_base=0.88, specular_base=0.25, cavity_darken=0.55, variation_value=0.2,
                         use_algae=False, use_barnacles=False, use_salt=False),
    "bs_rope": weather(*WOVEN[:2], (0.12, 0.12), base_triplanar=False, col_tint=hexc("#7A6448"),
                       normal_strength=1.0, roughness_base=0.95, use_algae=False, use_barnacles=False,
                       salt_coverage="Vector2(0.05, 0.2)"),
    "bs_weed": weather(TEX + "mud_albedo.png", TEX + "mud_normal.png", (0.6, 0.6), base_triplanar=True,
                       col_paint=hexc("#4A4630"), paint_cover=0.9, normal_strength=0.8, roughness_base=0.92,
                       specular_base=0.15, use_algae=False, use_barnacles=False, use_salt=False, wet_roughness=0.7,
                       wet_darken=0.8),
    "bs_salt": weather(HTEX + "coral_stone_albedo.png", HTEX + "coral_stone_normal.png", (0.5, 0.5),
                       base_triplanar=True, col_paint=hexc("#E8E4D8"), paint_cover=0.92, normal_strength=1.0,
                       roughness_base=0.85, cavity_darken=0.25, use_algae=False, use_barnacles=False, use_salt=False),
    "bs_ash": weather(HTEX + "coral_stone_albedo.png", HTEX + "coral_stone_normal.png", (0.6, 0.6), base_triplanar=True,
                      col_paint=hexc("#4E4A46"), paint_cover=0.8, normal_strength=0.5, roughness_base=0.95,
                      cavity_darken=0.35, use_algae=False, use_barnacles=False, use_salt=False),
    # Lit Age ceramic salvage: the Haluna coral-concrete greyed below lit_ceramic (it was drowned).
    "bs_lit_ceramic": weather(HTEX + "coral_concrete_albedo.png", HTEX + "coral_concrete_normal.png", (1.0, 1.0),
                              base_triplanar=True, col_tint=hexc("#A9ABA3"), normal_strength=1.0, roughness_base=0.7,
                              cavity_darken=0.45, use_barnacles=False, algae_coverage="Vector2(0.2, 0.5)"),
    # Sefir's barge: order_marble white lacquer over planking, the only clean white in the zone. Painted timber, not a
    # flat white (the PC's pass 3 on the GPU: a flat white read as unfinished): the lacquer covers the boards nearly
    # whole, the grain showing through faintly, a little salt at the waterline and in the seams, kept glossy.
    # Triplanar: the barge's small blocks (the seats, the bench) carry no planking UVs, and a mesh-UV grain streaked
    # down their faces.
    "bs_barge_white": weather(*TIMBER, base_triplanar=True, col_paint=hexc("#E4DED3"), paint_cover=0.86,
                              normal_strength=0.6, roughness_base=0.3, specular_base=0.5, cavity_darken=0.35,
                              variation_value=0.1, variation_warmth=0.02, use_barnacles=False,
                              algae_coverage="Vector2(0.1, 0.35)", salt_coverage="Vector2(0.05, 0.25)"),
}
# Sail-cloth: sun-bleached sand_cloth, the Saltwright faded teal patch, and the canvas browned by smoke.
for _name, _hex in (("bs_canvas", "#BBA987"), ("bs_canvas_teal", "#5E9A96"), ("bs_canvas_scorched", "#5A4B3C")):
    MATERIALS[_name] = weather(*WOVEN, base_triplanar=False, col_paint=hexc(_hex), paint_cover=0.78,
                               normal_strength=0.9, roughness_base=0.92, specular_base=0.25, use_algae=False,
                               variation_value=0.12, variation_warmth=0.04,
                               use_barnacles=False, salt_coverage="Vector2(0.0, 0.15)")

STANDARD: dict[str, dict] = {
    "bs_iron": {"albedo_color": hexc("#4A3A30"), "metallic": 0.5, "roughness": 0.78},
    # Iron sooted black-brown (burned plating, the burned lamp's frame): stays above the albedo floor.
    "bs_soot": {"albedo_color": hexc("#2A2420"), "metallic": 0.2, "roughness": 0.9},
    "bs_iron_hot": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#E0702E"),
                    "emission_energy_multiplier": 2.0, "roughness": 0.6},  # ember_orange
    "bs_brass": {"albedo_color": hexc("#B08D57"), "metallic": 0.85, "roughness": 0.5},  # brass, salt-dulled
    "bs_glass": {"transparency": 1, "albedo_color": hexc("#BFE6E0", 0.55), "roughness": 0.08,
                 "metallic_specular": 0.7},  # salt_glass net-floats
    # The burned lamp's surviving panes: glass blackened by the fire, no longer a mirror for the sun.
    "bs_glass_soot": {"transparency": 1, "albedo_color": hexc("#3A3530", 0.85), "roughness": 0.45},
    "bs_ember": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#E0702E"),
                 "emission_energy_multiplier": 2.5, "roughness": 0.9},  # ember_orange: the hottest warm value
    # Liss's crate: bound light, steady (colour script ch06: glimmer_bound, emission 1.2; no motes).
    "bs_glimmer_leak": {"albedo_color": hexc("#4FB3B0"), "emission_enabled": "true", "emission": hexc("#4FB3B0"),
                        "emission_energy_multiplier": 1.2, "roughness": 0.4},
    "bs_lacquer_red": {"albedo_color": hexc("#B3261E"), "roughness": 0.22, "clearcoat_enabled": "true",
                       "clearcoat": 0.6},
    "bs_gold": {"albedo_color": hexc("#D4A437"), "roughness": 0.28, "metallic": 1.0},  # gold_leaf
    # M3-ENV-703 (bs_story.py): Saltwright chalk on tarred planks (salt-white, dusty, a little thin), the Order's
    # Level-stone (order_marble greyed by the shoals) and its level line (the greybox block's #9FD8E0, 0.6).
    "bs_chalk": {"albedo_color": hexc("#D9D4C6"), "roughness": 1.0},  # opaque: no sorting against the hull
    "bs_level_stone": {"albedo_color": hexc("#C9CFCF"), "roughness": 0.7},
    "bs_level_glow": {"albedo_color": hexc("#9FD8E0"), "emission_enabled": "true", "emission": hexc("#9FD8E0"),
                      "emission_energy_multiplier": 0.6, "roughness": 0.5},
}

SHADER: dict[str, dict] = {
    # The smoke column (brine_shoals.md §2): lit at the fog albedo, dense core darker, warmed at the base.
    "bs_smoke": {"shader": SMOKE, "params": {
        "col_lit": hexc("#C4BCAE"), "col_fire": hexc("#E0702E"),
        "density": 0.72, "edge_softness": 2.0, "base_fade_m": 0.08, "top_fade": 0.45, "fire_glow": 0.3,
        "noise_scale": 3.2, "rise_speed": 0.06, "light_energy": 1.6, "col_core": hexc("#3C3C3A"),
        "forward_scatter": 0.6, "near_fade_m": 6.0}},
    # M3-ENV-1000 (bs_wake.py): a moving boat's wake; the dresser sets speed_m_s per boat (0: moored, no wake).
    "bs_wake": {"shader": WAKE, "params": {
        "col_foam": hexc("#EAEFEA"), "col_churn": hexc("#9DB8AE"), "opacity": 0.7, "speed_m_s": 1.6,
        "full_speed_m_s": 1.6, "wake_length_m": 16.0}},
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in sorted({**MATERIALS, **SHADER}.items()):
        hm.write_shader_material(out / f"{name}.tres", name, spec)
    for name, spec in sorted(STANDARD.items()):
        hm.write_standard_material(out / f"{name}.tres", name, spec)
    print(f"KIT_MAT {len(MATERIALS) + len(SHADER) + len(STANDARD)} materials -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
