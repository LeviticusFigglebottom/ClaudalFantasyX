"""Writes the Ashcrown temple kit's Godot materials (M3-ENV-09; ashcrown.md §3 and §4) from one table.

    python3 assets_src/environments/kits/ashcrown/ac_materials.py [--out assets/environments/kits/ashcrown/materials]

One .tres per glTF slot the generators write (ac_common.M_*, the vein slots), so the import's slot rule
and the preview's dresser map slot -> material by name. Colours are palette.json hex or tones derived
from it (named beside each). The stone slots use the shared env_weathering.gdshader with the Pemakar
kit's defaults (tide layers off, the salt layer as ash fall; `pemakar_materials.PEMAKAR_BASE`) and the
Pemakar kit's maps where the stone is the same (volcanic_stone, ash_soil), plus this kit's own
`ashlar_courses` and `paving_slabs` (ac_textures.py), so the near temple and the far one are one
material. The writers are the Haluna kit's (materials.py) and the Pemakar defaults are pemakar_materials.py,
both loaded by path under their own module names and read-only.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def _load_by_path(module_name: str, path: Path):
    """A sibling kit's module by file path under its own name (never a bare `materials` lookup, which a
    kit with its own `materials.py` already in sys.modules would answer)."""
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


hm = _load_by_path("haluna_materials", HERE.parent / "haluna" / "materials.py")
pm = _load_by_path("pemakar_materials", HERE.parent / "pemakar" / "pemakar_materials.py")

hexc = hm.hexc
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "ashcrown" / "materials"
TEX = "res://assets/environments/kits/ashcrown/textures/"
PTEX = pm.TEX  # the Pemakar kit's maps
WEATHER = hm.WEATHER
PLUME = pm.PLUME
VEIN_SLOTS = [f"ac_vein_t{k}" for k in range(7)] + ["ac_vein_floor", "ac_copper_vein"]

# Ashcrown's weathering defaults: the Pemakar ones (no tide; ash in the salt slot), ash heavier (it falls
# daily on the crown), no moss this high and this ashen, sparse orange lichen.
BASE = dict(pm.PEMAKAR_BASE)
BASE.update({"salt_coverage": "Vector2(0.35, 0.85)", "use_moss": False, "lichen_coverage": 0.06})


def weather(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(BASE)
    d.update({"tex_albedo": ("tex", albedo), "tex_normal": ("tex", normal),
              "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


MATERIALS: dict[str, dict] = {
    # The tiers: coursed ashlar by mesh UV (u along, v = height), neutral-cool, ash in G heavy.
    "ac_ashlar": weather(TEX + "ashlar_courses_albedo.png", TEX + "ashlar_courses_normal.png", (2.4, 1.0),
                         base_triplanar=False, normal_strength=1.3, roughness_base=0.9, specular_base=0.35,
                         cavity_darken=0.35, ao_strength=0.8, variation_value=0.14, variation_warmth=0.02),
    # Copings, piers, the stairs, the hall: Pemakar's volcanic stone (dressed), triplanar.
    "ac_dressed": weather(PTEX + "volcanic_stone_albedo.png", PTEX + "volcanic_stone_normal.png", (0.7, 0.7),
                          base_triplanar=True, col_tint="Color(1.12, 1.12, 1.14, 1)", normal_strength=0.8,
                          roughness_base=0.82, specular_base=0.4, cavity_darken=0.25, ao_strength=0.7,
                          variation_value=0.12, variation_warmth=0.02, erosion_pit_darken=0.15),
    "ac_paving": weather(TEX + "paving_slabs_albedo.png", TEX + "paving_slabs_normal.png", (2.4, 1.8),
                         base_triplanar=False, col_tint="Color(1.08, 1.08, 1.1, 1)", normal_strength=1.0,
                         roughness_base=0.86, specular_base=0.35, cavity_darken=0.3, ao_strength=0.7,
                         variation_value=0.08, salt_coverage="Vector2(0.25, 0.75)", salt_cavity_gather=0.7),
    "ac_ground": weather(PTEX + "ash_soil_albedo.png", PTEX + "ash_soil_normal.png", (2.0, 2.0), base_triplanar=True,
                         normal_strength=1.0, roughness_base=0.95, specular_base=0.3, cavity_darken=0.3,
                         ao_strength=0.6, variation_value=0.06, salt_coverage="Vector2(0.15, 0.6)",
                         salt_cavity_gather=0.2,
                         # the PC's pass 7 row 79: A10's mound read untextured; a finer macro breakup (env_weathering)
                         macro_strength=0.9, macro_scale_m=6.0),
    # The far mountain below: as Pemakar's kit_volcanic_far (moss bands on the terraces).
    "ac_ground_far": weather(PTEX + "volcanic_stone_albedo.png", PTEX + "volcanic_stone_normal.png", (8.0, 8.0),
                             base_triplanar=True, normal_strength=0.5, roughness_base=0.92, cavity_darken=0.2,
                             ao_strength=0.5, variation_value=0.08, detail_scale_m=6.0, use_moss=True,
                             moss_coverage=0.85, moss_normal_y=0.35, moss_north_facing=0.2,
                             salt_coverage="Vector2(0.1, 0.45)",
                             # the PC's pass 7 row 79: A10's crater-rim mound read untextured (env_weathering macro)
                             macro_strength=0.85, macro_scale_m=24.0),
    # The vent's cinder: dark, rust-flecked (laterite brick map read as scoria at a large tile, tinted down).
    "ac_cinder": weather(PTEX + "ash_soil_albedo.png", PTEX + "ash_soil_normal.png", (3.0, 3.0), base_triplanar=True,
                         col_tint="Color(0.78, 0.7, 0.66, 1)", normal_strength=1.4, roughness_base=0.97,
                         cavity_darken=0.4, salt_coverage="Vector2(0.1, 0.5)"),
    # The plume by day (the preview's override for Pemakar's ash_plume): the same shader, its ash lit by
    # the noon sky (paler, less darkened), the ember kept low to the vent, no festival glow.
    # The PC's pass 7, row 79 (env-art-b with the Lead's leave, 10-31): the kit's day plume read as solid, lumpy, cool
    # clay in a10. It takes the Ch5 zone's proven look (ch05_ashcrown_dressing.py PLUME_LOOK, viewed at the tiers, the
    # forecourt, the crown and the court): warm ash grey-brown, softer feathered billows, the sun through its edges and
    # on its rim, the crater's fire up the column's foot, a shade side that keeps its shadow; and, so it reads as smoke
    # not a solid, a little translucency with wispier, broken edges.
    "ac_plume_day": {"shader": PLUME, "params": {
        "col_body": hexc("#857D75"),  # warm ash grey-brown in daylight
        "col_body_top": hexc("#9E968C"),  # thinner, paler ash aloft
        "body_darken": 0.8, "mottle": 0.3, "edge_soft": 0.75, "ember_energy": 0.6, "ember_height": 0.18, "ember_underside": 1.0,
        "town_glow": 0.0, "rim_energy": 0.35, "opacity": 0.92, "alpha_mottle": 0.25,
        # Close up (M3-ENV-11): the edges glow looking sunward, and the vent's ember climbs the foot; all fade out by
        # 800 m, so the far read is the plume's own.
        "col_shade": hexc("#A19C99"), "shade_lift": 0.15, "lift_all_round": 0.6, "back_scatter": 0.7, "vent_glow": 0.9,
        "vent_glow_height": 0.16, "billow_shade": 0.6, "sky_up": 0.6, "near_detail": 0.6, "near_detail_m": 9.0, "detail_bump": 0.35, "near_fade_m": "Vector2(400, 800)"}},
}

COPPER = {"albedo_color": hexc("#5F8A78"), "metallic": 0.35, "roughness": 0.55}  # bronze_patina (as Pemakar)
STANDARD: dict[str, dict] = {name: dict(COPPER) for name in VEIN_SLOTS}
# The floor inlay is walked smooth and dulled with ash: rougher, so it does not mirror the loggia's light.
STANDARD["ac_vein_floor"] = {"albedo_color": hexc("#5F8A78"), "metallic": 0.2, "roughness": 0.75}
STANDARD.update({
    "ac_copper_new": {"albedo_color": hexc("#A65A2A"), "metallic": 1.0, "roughness": 0.38},  # hair_copper
    # The strike state: gameplay swaps it onto a vein slot (starlight white-blue, an ember core).
    "ac_copper_live": {"albedo_color": hexc("#A65A2A"), "metallic": 0.6, "roughness": 0.3, "emission_enabled": "true",
                       "emission": hexc("#DCE6FF"), "emission_energy_multiplier": 6.0},
    "ac_lacquer_red": {"albedo_color": hexc("#B3261E"), "roughness": 0.26, "clearcoat_enabled": "true",
                       "clearcoat": 0.5},
    "ac_lacquer_black": {"albedo_color": hexc("#1D1916"), "roughness": 0.22, "clearcoat_enabled": "true",
                         "clearcoat": 0.6},
    "ac_gold_leaf": {"albedo_color": hexc("#D4A437"), "roughness": 0.3, "metallic": 1.0},
    "ac_forge_glow": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#E0702E"),
                      "emission_energy_multiplier": 3.0, "roughness": 1.0},
    "ac_vent_glow": {"albedo_color": hexc("#E0702E"), "emission_enabled": "true", "emission": hexc("#FFB16E"),
                     "emission_energy_multiplier": 2.5, "roughness": 1.0, "shading_mode": 0},
    "ac_wick_flame": {"albedo_color": hexc("#FFB16E"), "emission_enabled": "true", "emission": hexc("#FFB16E"),
                      "emission_energy_multiplier": 8.0, "roughness": 1.0, "shading_mode": 0},
    "ac_soot": {"albedo_color": hexc("#1D1916"), "roughness": 0.95},
    "ac_interior_dark": {"albedo_color": hexc("#2B2622"), "roughness": 1.0},
})


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
