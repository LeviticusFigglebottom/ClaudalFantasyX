"""Writes the Tamsule Bell kit's Godot materials (M3-ENV-01) from one table, so every value is in source.

    python3 assets_src/environments/kits/tamsule_bell/materials.py [--out assets/environments/kits/tamsule_bell/materials]

Colours are palette.json hex (tamsule_bell.md §3). The kit adds no textures of its own: timber, stone and
cloth use the Haluna kit's procedural texture set and its weathering shader, and the bell uses the
kit's own env_bronze.gdshader with the Haluna detail and coral-concrete maps. The .tres writers are the
Haluna kit's (assets_src/environments/kits/haluna/materials.py, imported read-only). Material names
match the glTF slots the generators write (the tamsule_bell_kit import rules map slot -> file).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "tamsule_bell" / "materials"
BRONZE = "res://game/shaders/environment/env_bronze.gdshader"

_spec = importlib.util.spec_from_file_location("haluna_materials", HERE.parent / "haluna" / "materials.py")
hm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hm)
hexc, stone, TEX = hm.hexc, hm.stone, hm.TEX

NO_GROWTH = {"use_algae": False, "use_barnacles": False, "use_moss": False}


def lacquer(hex_: str, rough: float, **kw) -> dict:
    """Lacquer over timber: a near-full paint cover that wears through to grey timber on proud edges."""
    d = dict(base_triplanar=False, col_paint=hexc(hex_), paint_cover=0.93, normal_strength=0.35,
             roughness_base=rough, specular_base=0.55, cavity_darken=0.15, variation_value=0.08,
             erosion_lighten=0.04, salt_coverage="Vector2(0.05, 0.25)", **NO_GROWTH)
    d.update(kw)
    return stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), **d)


def cloth(hex_: str) -> dict:
    return stone("woven_panel_albedo.png", "woven_panel_normal.png", (0.25, 0.25), base_triplanar=False,
                 col_paint=hexc(hex_), paint_cover=0.92, normal_strength=0.4, roughness_base=0.92, specular_base=0.25,
                 use_salt=False, **NO_GROWTH)


MATERIALS: dict[str, dict] = {
    # The bell (tamsule_bell.md §3): worn bronze under bronze_patina verdigris, brass on worn edges.
    "tb_bell_bronze": {"shader": BRONZE, "params": {
        "tex_detail": ("tex", TEX + "weathering_detail.png"),
        "tex_normal": ("tex", TEX + "coral_concrete_normal.png"),
        "col_bronze": hexc("#5E4528"), "col_worn": hexc("#B08D57"),  # brass, darkened / brass
        "col_patina": hexc("#5F8A78"), "col_patina_pale": hexc("#8DB3A2"),  # bronze_patina / its bloom
        "col_grime": hexc("#272822"), "metallic_bronze": 0.9, "roughness_bronze": 0.5, "roughness_worn": 0.3,
        "patina_coverage": "Vector2(0.55, 0.95)", "patina_roughness": 0.85, "patina_shade_bias": 0.25,
        "streak_period_m": "Vector2(0.45, 6)", "streak_strength": 0.55, "detail_scale_m": 1.4,
        "normal_tile_m": 2.5, "normal_strength": 0.55, "wear_strength": 0.9, "ao_strength": 0.75}},
    # Timber (as the Haluna kit_timber, sun-silvered) and the piles (darker, algae and barnacles at the line).
    "tb_timber": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                       col_tint=hexc("#CFCDC8"), normal_strength=1.2, roughness_base=0.8, specular_base=0.3,
                       cavity_darken=0.45, variation_value=0.24, variation_warmth=0.03, moss_min_height_m=1.0),
    "tb_pile_timber": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                            col_tint=hexc("#A9A49B"), normal_strength=1.3, roughness_base=0.85, specular_base=0.3,
                            cavity_darken=0.5, variation_value=0.2, algae_coverage="Vector2(0.55, 0.9)",
                            barnacle_coverage=0.6, moss_min_height_m=1.2),
    # Lacquer: black on the old gantry and frames (lacquer_black, the albedo floor), red on repairs.
    "tb_lacquer_black": lacquer("#1D1916", 0.36),
    "tb_lacquer_red": lacquer("#7A1712", 0.33),  # lacquer_red_deep
    "tb_signboard": lacquer("#1D1916", 0.24, paint_cover=0.98, erosion_lighten=0.02),
    # The catch-pool and the gantry plinths: pale Lit Age ceramic-concrete, smoothed by a thousand years
    # of swimmers; algae at the waterline, a little salt above it, no barnacles inside the pool.
    "tb_lit_ceramic": stone("coral_concrete_albedo.png", "coral_concrete_normal.png", (2.0, 2.0),
                            base_triplanar=True, col_tint=hexc("#DCE3E0"), normal_strength=0.5, roughness_base=0.55,
                            specular_base=0.45, cavity_darken=0.25, variation_value=0.06, erosion_pit_darken=0.15,
                            algae_coverage="Vector2(0.45, 0.8)", barnacle_coverage=0.25,
                            salt_coverage="Vector2(0.1, 0.3)", use_moss=False),
    "tb_woven": stone("woven_panel_albedo.png", "woven_panel_normal.png", (0.8, 0.8), base_triplanar=False,
                      col_tint=hexc("#DCD3C6"), normal_strength=1.4, roughness_base=0.9, specular_base=0.25,
                      cavity_darken=0.5, variation_value=0.22, **NO_GROWTH),
    # Port roofs: nipa-palm thatch, rain-greyed and darker than Haluna's (the thatch swatch x timber).
    "tb_roof_nipa": stone("thatch_albedo.png", "thatch_normal.png", (1.6, 1.6), base_triplanar=False,
                          col_tint="Color(0.86, 0.86, 0.9, 1)", normal_strength=1.8, roughness_base=0.95,
                          specular_base=0.2, cavity_darken=0.5, variation_value=0.2, use_algae=False,
                          use_barnacles=False, use_salt=False, moss_normal_y=0.5),
    "tb_rope": stone("woven_panel_albedo.png", "woven_panel_normal.png", (0.12, 0.12), base_triplanar=False,
                     col_tint=hexc("#9C7E5A"), normal_strength=1.0, roughness_base=0.95, use_moss=False,
                     use_barnacles=False),
    "tb_float_weave": stone("woven_panel_albedo.png", "woven_panel_normal.png", (0.2, 0.2), base_triplanar=True,
                            col_paint=hexc("#C9B48E"), paint_cover=0.75, normal_strength=1.2, roughness_base=0.9,
                            **NO_GROWTH),  # sand_cloth
    # Oruvel's mooring bands (Low Reaches colours): sea-blue and bone paint, faded and salted.
    "tb_paint_sea_blue": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                               col_paint=hexc("#3C78A8"), paint_cover=0.8, roughness_base=0.7, specular_base=0.4,
                               use_moss=False),
    "tb_paint_bone": stone("timber_albedo.png", "timber_normal.png", (0.4, 1.6), base_triplanar=False,
                           col_paint=hexc("#E6DAC0"), paint_cover=0.8, roughness_base=0.7, specular_base=0.4,
                           use_moss=False),
    "tb_wake_shell": {"shader": hm.SHELL, "params": {"tex_glyph": ("tex", TEX + "shell_glyph.png")}},
}
for _dye, _hex in (("indigo", "#2B3A6B"), ("sea_blue", "#3C78A8"), ("faded_teal", "#5E9A96"), ("sand", "#C9B48E"),
                   ("red", "#B3261E")):
    MATERIALS[f"tb_cloth_{_dye}"] = cloth(_hex)  # the cloth geometry is two-sided (gallery._cloth)

STANDARD: dict[str, dict] = {
    # Salt-glass bays (salt_glass, transmissive, slightly green): the drop shows through.
    "tb_salt_glass": {"transparency": 1, "cull_mode": 2, "albedo_color": hexc("#BFE6E0", 0.3), "roughness": 0.05,
                      "metallic_specular": 0.8},
    "tb_port_glass": {"albedo_color": hexc("#2E6E6A"), "roughness": 0.06, "metallic_specular": 0.9},
    # Bound light in the ribs (glimmer_bound at the frame's 1.8, steady: no animation anywhere).
    "tb_glimmer_conduit": {"albedo_color": hexc("#4FB3B0"), "emission_enabled": "true", "emission": hexc("#4FB3B0"),
                           "emission_energy_multiplier": 1.8, "roughness": 0.3},
    "tb_gold_leaf": {"albedo_color": hexc("#D4A437"), "roughness": 0.28, "metallic": 1.0},
    "tb_interior_dark": {"albedo_color": hexc("#2B2622"), "roughness": 1.0},
    # PLACEHOLDER: the drop's look is PC GPU's (tamsule_bell.md §1); this only marks the volume.
    "tb_drop_proxy": {"transparency": 1, "albedo_color": hexc("#3FD0C9", 0.45), "roughness": 0.04,
                      "metallic_specular": 0.9, "cull_mode": 0},
}


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
