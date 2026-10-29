#!/usr/bin/env python3
"""The Ch5-Ch9 zones' own looks for kit slots that are flat StandardMaterials (env-art-b, M3-ENV-1325/1326): a flat
colour reads as plastic at player height, so a zone swaps the slot (ZoneKitDressing `material_paths` or
`kit_material_paths`, KitSlotSwaps in an arena) for one of these, written next to the zone by its dressing generator.

  bronze_material(name, params)          an env_bronze look (game/shaders/environment/env_bronze.gdshader): a body,
                                         a worn edge colour, a patina in the hollows, streaks and grime. Metals, and
                                         lacquers with metallic 0 (the "worn" colour is the undercoat at the chips).
  copy_material(src, name, overrides)    a kit material's text with some shader parameters (or top-level keys) set:
                                         the kit's stone with a lighter baked occlusion, a canvas made triplanar.

Not a tool to run by itself; the zone generators import it.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRONZE_SHADER = "res://game/shaders/environment/env_bronze.gdshader"
BRONZE_TEX = {"tex_detail": "res://assets/environments/kits/haluna/textures/weathering_detail.png",
              "tex_normal": "res://assets/environments/kits/haluna/textures/coral_concrete_normal.png"}


def tres_value(v) -> str:
    if isinstance(v, tuple) and len(v) == 3:
        return "Color(%.4f, %.4f, %.4f, 1)" % v
    if isinstance(v, tuple):
        return "Vector2(%g, %g)" % v
    return "%g" % v


def bronze_material(name: str, params: dict) -> str:
    lines = ['[gd_resource type="ShaderMaterial" load_steps=4 format=3]', "",
             '[ext_resource type="Shader" path="%s" id="1_shader"]' % BRONZE_SHADER,
             '[ext_resource type="Texture2D" path="%s" id="2_tex"]' % BRONZE_TEX["tex_normal"],
             '[ext_resource type="Texture2D" path="%s" id="3_tex"]' % BRONZE_TEX["tex_detail"], "",
             "[resource]", 'resource_name = "%s"' % name.removesuffix(".tres"), 'shader = ExtResource("1_shader")']
    for k in sorted(params):
        lines.append("shader_parameter/%s = %s" % (k, tres_value(params[k])))
    lines += ['shader_parameter/tex_detail = ExtResource("3_tex")', 'shader_parameter/tex_normal = ExtResource("2_tex")']
    return "\n".join(lines) + "\n"


def copy_material(src_res: str, name: str, overrides: dict) -> str:
    """`src_res`'s text renamed to `name`, each override replacing its `shader_parameter/<key>` line (or its bare
    `<key>` line for a StandardMaterial's own keys); every key must already be there once."""
    text = (ROOT / src_res.removeprefix("res://")).read_text(encoding="utf-8")
    for key, value in overrides.items():
        text, n = re.subn(r"(?m)^(shader_parameter/)?%s = .*$" % re.escape(key),
                          lambda m: "%s%s = %s" % (m.group(1) or "", key, value), text)
        assert n == 1, (src_res, key)
    return re.sub(r'(?m)^resource_name = ".*"$', 'resource_name = "%s"' % name.removesuffix(".tres"), text, count=1)


# Looks shared by more than one zone (bronze_material parameters).
LACQUER = {  # a lacquer over a black undercoat: chipped at the edges, ash or salt in the hollows (not metal)
    "col_worn": (0.0784, 0.0667, 0.0627), "col_patina": (0.4196, 0.3961, 0.3725),
    "col_patina_pale": (0.5490, 0.5333, 0.5098), "metallic_bronze": 0.0, "roughness_bronze": 0.32,
    "roughness_worn": 0.6, "patina_coverage": (0.0, 0.35), "patina_roughness": 0.95, "patina_shade_bias": 0.0,
    "streak_strength": 0.35,
    "wear_strength": 0.5, "detail_scale_m": 0.6, "normal_strength": 0.25, "normal_tile_m": 1.6,
    "variation_value": 0.12}
VERDIGRIS = {  # old copper: verdigris over a dark copper body showing at the edges
    "col_bronze": (0.3529, 0.2039, 0.1412), "col_worn": (0.6510, 0.3529, 0.1647),
    "col_patina": (0.2706, 0.3804, 0.3373), "col_patina_pale": (0.4314, 0.5137, 0.4706),
    "metallic_bronze": 0.8, "roughness_bronze": 0.5, "roughness_worn": 0.3, "patina_coverage": (0.0, 0.55),
    "patina_roughness": 0.88, "streak_strength": 0.6, "wear_strength": 0.7, "detail_scale_m": 0.6,
    "normal_strength": 0.5, "normal_tile_m": 2.0}
SEA_IRON = {  # wrought iron by the sea: rust blooming from the hollows and running down, dark metal at the worn edges
    "col_bronze": (0.2196, 0.1882, 0.1686), "col_worn": (0.3608, 0.3373, 0.3137),
    "col_patina": (0.4510, 0.2392, 0.1294), "col_patina_pale": (0.6000, 0.3529, 0.1922),
    "metallic_bronze": 0.6, "roughness_bronze": 0.7, "roughness_worn": 0.45, "patina_coverage": (0.15, 0.85),
    "patina_roughness": 0.95, "streak_strength": 0.7, "wear_strength": 0.6, "detail_scale_m": 0.5,
    "normal_strength": 0.6, "normal_tile_m": 1.6}


SWAPS_SCRIPT = "res://game/levels/act1/kit_slot_swaps.gd"


def add_kit_slot_swaps(text: str, paths: dict) -> str:
    """A written arena scene's text with a KitSlotSwaps node at its end (after every kit piece is ready), so the arena
    wears its zone's slot swaps."""
    head = re.match(r"\[gd_scene load_steps=(\d+) format=3\]", text)
    text = text.replace(head.group(0), f"[gd_scene load_steps={int(head.group(1)) + 1} format=3]", 1)
    last = list(re.finditer(r"^\[ext_resource [^\n]*\]$", text, flags=re.M))[-1]
    text = text[:last.end()] + f'\n[ext_resource type="Script" path="{SWAPS_SCRIPT}" id="slot_swaps"]' + text[last.end():]
    body = ", ".join(f'"{k}": "{v}"' for k, v in sorted(paths.items()))
    return text.rstrip("\n") + ('\n\n[node name="KitSlotSwaps" type="Node" parent="."]\n'
                                'script = ExtResource("slot_swaps")\npaths = {%s}\n' % body)


def load_generator(name: str):
    """One of tools/act1's zone generators as a module (the arena writers under assets_src read its slot looks)."""
    import importlib.util  # noqa: PLC0415
    import sys  # noqa: PLC0415

    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    spec = importlib.util.spec_from_file_location(name, here / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NEW_COPPER = {  # copper kept bright (the Tenders' rods, a smith's work): a little bloom in the hollows only
    "col_bronze": (0.5020, 0.2706, 0.1255), "col_worn": (0.8000, 0.4784, 0.2706),
    "col_patina": (0.2706, 0.3804, 0.3373), "col_patina_pale": (0.4314, 0.5137, 0.4706),
    "metallic_bronze": 1.0, "roughness_bronze": 0.4, "roughness_worn": 0.24, "patina_coverage": (0.0, 0.2),
    "patina_roughness": 0.85, "streak_strength": 0.3, "wear_strength": 0.9, "detail_scale_m": 0.5,
    "normal_strength": 0.4, "normal_tile_m": 1.6}
GOLD = {  # gilt: worn through to the ground under it at the edges, a little dulled in the hollows
    "col_bronze": (0.8314, 0.6431, 0.2157), "col_worn": (0.5490, 0.3922, 0.1961),
    "col_patina": (0.3608, 0.3451, 0.3255), "col_patina_pale": (0.5020, 0.4824, 0.4549),
    "metallic_bronze": 1.0, "roughness_bronze": 0.28, "roughness_worn": 0.45, "patina_coverage": (0.0, 0.15),
    "patina_shade_bias": 0.1, "patina_roughness": 0.85, "streak_strength": 0.2, "wear_strength": 0.6,
    "detail_scale_m": 0.5, "normal_strength": 0.3, "normal_tile_m": 1.6}


def lacquer(color: tuple, *, undercoat: tuple = (0.0784, 0.0667, 0.0627)) -> dict:
    """A lacquer of `color`: its hollows dull to an aged lacquer of the same hue (a grey dust gathered in the normal
    map's pits read as camouflage on broad leaves), chipped to `undercoat` at the edges."""
    aged = tuple(round(c * 0.6, 4) for c in color)
    pale = tuple(round(min(1.0, c * 0.75 + 0.04), 4) for c in color)
    return dict(LACQUER, col_bronze=color, col_worn=undercoat, col_patina=aged, col_patina_pale=pale,
                patina_coverage=(0.05, 0.3))
