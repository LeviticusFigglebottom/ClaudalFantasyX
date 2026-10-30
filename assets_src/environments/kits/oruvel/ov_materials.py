"""Writes the Oruvel raft-town kit's Godot materials (M3-ENV-07) from one table, so every value is in source.

    python3 assets_src/environments/kits/oruvel/ov_materials.py [--out assets/environments/kits/oruvel/materials]

One .tres per glTF slot the kit generators write (ov_common.M_*), so the import's `{asset_dir}/materials/` rule and
HalunaDresser both map slot -> material by name (and a placement's `materials` map can swap a hull's paint for another
colourway). Colours are palette.json hex or tones derived from it (named beside each), inside the albedo
floor/ceiling (#1D1916..#EBE7DF). Weathering materials use the shared env_weathering.gdshader (haluna.md §4 stack)
with the Haluna kit's timber, woven-panel, coral-concrete and detail maps (read-only); the net is the Haluna net map.
The writers are the Haluna kit's.

oruvel.md §3: nothing on a raft grows moss; salt lives above the water; the algae and barnacle layers only at the
waterline (the shader's tide band about the live water, WeatheringTide); no slot emits (every lamp is out at 10:30).
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

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "oruvel" / "materials"
HTEX = "res://assets/environments/kits/haluna/textures/"
WEATHER = "res://game/shaders/environment/env_weathering.gdshader"
hexc = hm.hexc

BASE = {
    "tex_detail": ("tex", HTEX + "weathering_detail.png"),
    "detail_scale_m": 0.5,
    "col_algae": hexc("#4A5A2E"),  # the Haluna film: a lagoon weed at the waterline
    "col_barnacle": hexc("#E6DAC0"),  # bone
    "col_salt": hexc("#E8E4D8"),
    "col_moss": hexc("#2B5529"),
    "col_lichen": hexc("#C08A3A"),
    "use_moss": False,
    "algae_band_m": "Vector2(-0.45, 0.06)",  # about the live waterline (hymn tide line)
    "algae_coverage": "Vector2(0.45, 0.85)",
    "barnacle_band_m": "Vector2(-0.6, 0.0)",
    "barnacle_coverage": 0.4,
    "salt_band_m": "Vector2(0.15, 3.0)",
    "salt_coverage": "Vector2(0.08, 0.3)",
}


def weather(albedo: str, normal: str, tile: tuple[float, float], **kw) -> dict:
    d = dict(BASE)
    d.update({"tex_albedo": ("tex", albedo), "tex_normal": ("tex", normal), "tile_m": f"Vector2({tile[0]:g}, {tile[1]:g})"})
    d.update(kw)
    return {"shader": WEATHER, "params": d}


TIMBER = (HTEX + "timber_albedo.png", HTEX + "timber_normal.png", (0.4, 1.6))
WOVEN = (HTEX + "woven_panel_albedo.png", HTEX + "woven_panel_normal.png")
CONCRETE = (HTEX + "coral_concrete_albedo.png", HTEX + "coral_concrete_normal.png")
DRY = {"use_algae": False, "use_barnacles": False}
# Decks ride at the tide line: their weed and barnacles stop below the walked top, soft edges included (PC QA row 59,
# the dive raft's deck crusted under O10). Hull timber under the deck keeps them.
DECK = {"algae_band_m": "Vector2(-0.45, -0.2)", "barnacle_band_m": "Vector2(-0.6, -0.25)"}


def paint(hex_color: str, cover: float = 0.8) -> dict:
    """Faded hull paint over the timber: worn through on the edges and laps (the shader thins it there)."""
    return weather(*TIMBER, base_triplanar=False, col_paint=hexc(hex_color), paint_cover=cover, normal_strength=1.1,
                   roughness_base=0.72, specular_base=0.38, cavity_darken=0.35, variation_value=0.12,
                   variation_warmth=0.02, erosion_lighten=0.1, wet_darken=0.55, wet_roughness=0.15)


def canvas(hex_color: str) -> dict:
    return weather(*WOVEN, (0.25, 0.25), base_triplanar=False, col_paint=hexc(hex_color), paint_cover=0.9,
                   normal_strength=0.4, roughness_base=0.92, specular_base=0.25, use_salt=False, **DRY)


MATERIALS: dict[str, dict] = {
    # Decks, bridges, cabin walls: sun-silvered timber_weathered, paler and greyer than Haluna's (no shade, all salt).
    "ov_timber": weather(*TIMBER, base_triplanar=False, **DECK, col_tint=hexc("#D6D4CE"), normal_strength=1.25,
                         roughness_base=0.82, specular_base=0.3, cavity_darken=0.45, variation_value=0.24,
                         variation_warmth=0.03, erosion_lighten=0.08, wet_darken=0.55, wet_roughness=0.14),
    # The hull bottoms below the boot line: tarred dark brown-black (#3A3029), weed and barnacles at the waterline.
    "ov_hull_tar": weather(*TIMBER, base_triplanar=False, col_paint=hexc("#3A3029"), paint_cover=0.9,
                           normal_strength=0.9, roughness_base=0.6, specular_base=0.4, cavity_darken=0.2,
                           variation_value=0.08, wet_darken=0.75, wet_roughness=0.1),
    # The keel-roofs' crowns: the same tar bleached by years of sun and salt to a warm grey-brown.
    "ov_roof_tar": weather(*TIMBER, base_triplanar=False, col_paint=hexc("#6A5E52"), paint_cover=0.85,
                           normal_strength=1.0, roughness_base=0.8, specular_base=0.3, cavity_darken=0.35,
                           variation_value=0.14, erosion_lighten=0.12, salt_band_m="Vector2(0.0, 12.0)",
                           salt_coverage="Vector2(0.12, 0.35)", **DRY),
    # The colourways (oruvel.md §3): sea_blue_cloth, roof_clay, dusk_gold, faded_teal_cloth, whitewash, all faded.
    "ov_hull_paint": paint("#5D88A6"),
    "ov_paint_red": paint("#A85F4C"),
    "ov_paint_ochre": paint("#C49A5C"),
    "ov_paint_teal": paint("#5E9A96"),
    "ov_paint_white": paint("#D6D0C4", 0.85),
    # The gulls and the keel-hull's stern post: one carved piece of grey driftwood (Haluna's kit_carved_wood).
    "ov_carved": weather(*TIMBER[:2], (0.25, 0.5), base_triplanar=True, triplanar_sharpness=6.0,
                         col_tint=hexc("#E4E0DA"), normal_strength=0.7, roughness_base=0.78, specular_base=0.3,
                         cavity_darken=0.25, variation_value=0.06, variation_warmth=0.02, **DRY),
    # Coir lashings and tarred tether / stays.
    "ov_rope": weather(*WOVEN, (0.12, 0.12), base_triplanar=False, col_tint=hexc("#9C7E5A"), normal_strength=1.0,
                       roughness_base=0.95, use_salt=False, **DRY),
    "ov_rope_tar": weather(*WOVEN, (0.12, 0.12), base_triplanar=False, col_tint=hexc("#5A4A3C"), normal_strength=1.0,
                           roughness_base=0.7, specular_base=0.4, use_salt=False, **DRY),
    # Canvas: awnings, curtains and laundry (sand_cloth, a faded madder stripe, faded_teal_cloth).
    "ov_canvas_sand": canvas("#C9B48E"),
    "ov_canvas_red": canvas("#A65A4A"),
    "ov_canvas_teal": canvas("#5E9A96"),
    # Salvaged Lit Age cladding panels: lit_ceramic greyed, a little weed left in the joints, chipped.
    "ov_ceramic": weather(*CONCRETE, (0.8, 0.8), base_triplanar=True, col_paint=hexc("#CFD6D3"), paint_cover=0.9,
                          normal_strength=0.3, roughness_base=0.45, specular_base=0.5, cavity_darken=0.35,
                          erosion_pit_darken=0.25, variation_value=0.06, **DRY),
    # Oil jars and the cook's stove: earthenware (laterite #A8573A).
    "ov_clay": weather(*CONCRETE, (0.6, 0.6), base_triplanar=True, col_paint=hexc("#A8573A"), paint_cover=0.86,
                       normal_strength=0.6, roughness_base=0.82, cavity_darken=0.3, variation_value=0.14,
                       use_salt=False, **DRY),
    # M3-ENV-07B, the storm's far reef (reef_edge_far): the bared reef flat, bleached coral rubble going dark where it
    # is still wet (VC.B), weed and barnacles at the live water.
    "ov_reef": weather(*CONCRETE, (2.0, 2.0), base_triplanar=True, col_paint=hexc("#B4AA98"), paint_cover=0.85,
                       normal_strength=0.9, roughness_base=0.7, specular_base=0.4, cavity_darken=0.45,
                       erosion_pit_darken=0.35, variation_value=0.18, wet_darken=0.6, wet_roughness=0.12,
                       use_salt=False),
    # The drowned towers' crowns standing clear: Lit Age concrete under a coral crust, weed-dark to the old waterline.
    "ov_crown": weather(*CONCRETE, (1.5, 1.5), base_triplanar=True, col_paint=hexc("#A8A699"), paint_cover=0.8,
                        normal_strength=0.8, roughness_base=0.75, specular_base=0.35, cavity_darken=0.5,
                        erosion_pit_darken=0.4, variation_value=0.14, wet_darken=0.6, wet_roughness=0.12,
                        use_salt=False),
    # M3-ENV-730 (post_credits): new timber among the old on the rebuilt moorings: the same grain, not yet silvered
    # (a warm pale #D9B98C), crisp edges, little salt.
    "ov_timber_new": weather(*TIMBER, base_triplanar=False, **DECK, col_tint=hexc("#D9B98C"), normal_strength=1.1,
                             roughness_base=0.78, specular_base=0.3, cavity_darken=0.35, variation_value=0.12,
                             variation_warmth=0.05, erosion_lighten=0.02, wet_darken=0.55, wet_roughness=0.14),
}

STANDARD: dict[str, dict] = {
    # The nets: the Haluna net map, hashed cutout (the Haluna rule: blend writes no depth and the sea drew over it).
    "ov_net": {"transparency": 3, "cull_mode": 2, "albedo_texture": ("tex", HTEX + "net_albedo.png"),
               "albedo_color": hexc("#C8B89A"), "roughness": 0.9, "uv1_scale": "Vector3(2.5, 2.5, 1)",
               "texture_filter": 5},
    # brass: the one bright metal (the scale, the lamps, the winch's pawl, the plaque).
    "ov_brass": {"albedo_color": hexc("#B08D57"), "metallic": 0.85, "roughness": 0.45},
    # Rusted dark iron: lamp hooks, the winch's crank and axle, the cook's hood and pots.
    "ov_iron": {"albedo_color": hexc("#4A3A30"), "metallic": 0.5, "roughness": 0.62},
    # Lantern chimneys and glass floats: salt_glass darkened and smoked (sooted chimneys, sea-green float glass), so
    # an unlit lantern never reads as lit against a bright sky.
    "ov_glass": {"transparency": 1, "albedo_color": hexc("#7FA49E", 0.72), "roughness": 0.18,
                 "metallic_specular": 0.6},
    # Wick spools and chits: undyed cotton and paper, gauze_white dulled.
    "ov_wick": {"albedo_color": hexc("#D9D2C2"), "roughness": 0.9},
    # The divers' lead weights.
    "ov_lead": {"albedo_color": hexc("#55585A"), "metallic": 0.6, "roughness": 0.55},
    # Doorways, the dive well's shade, the stove's mouth: deep shade above the albedo floor.
    "ov_interior_dark": {"albedo_color": hexc("#2B2622"), "roughness": 1.0},
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
