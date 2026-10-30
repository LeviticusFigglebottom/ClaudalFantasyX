#!/usr/bin/env python3
"""Writes each Stillguard soldier's materials (assets/characters/stillguard_<v>/materials/*.tres), M3-CHR-508.

    python3 assets_src/characters/stillguard/write_materials.py [--variant a ...]   # every variant when none named
    python3 assets_src/characters/stillguard/write_materials.py --variant ivo       # M3-CHR-540: a named Stillguard

Moll's table (assets_src/characters/moll/write_materials.py, loaded by path) with each soldier's own skin maps and
colours: his skin and hair colours, his eyes; the clean soldiers' cloth and shield on Moll's maps, the weathered ones'
on the shared worn atlases (sg_textures --shared); the spear's shaft and cord on the brine-iron's maps with no ember,
its blade steel and its fittings bronze (Toma's). Each material's resource_name is the glTF slot it replaces (the
characters import rule). Deterministic.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("moll_write_materials", HERE.parent / "moll" / "write_materials.py")
mw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mw)

from sg_table import builds, name, variant_params, variants  # noqa: E402

M = "moll/textures/"
WORN = "stillguard/textures/stillguard_worn_"
STEEL = "albedo_color = Color(0.353, 0.376, 0.40, 1)\nmetallic = 1.0\nroughness = 0.42\n"  # toma.md §4 #8's steel
# the spear's shaft on the brine-iron's maps: oiled ash, the red cord band; no ember
SPEAR = ("metallic = 1.0\nroughness = 1.0\nmetallic_texture_channel = 2\nroughness_texture_channel = 1\n"
         "normal_enabled = true\n")
SPEAR_TEX = {"albedo_texture": M + "moll_iron_albedo.png", "normal_texture": M + "moll_iron_normal.png",
             "metallic_texture": M + "moll_iron_orm.png", "roughness_texture": M + "moll_iron_orm.png"}
IRIS = {"a": "Color(0.20, 0.15, 0.10, 1)", "b": "Color(0.12, 0.08, 0.05, 1)", "c": "Color(0.16, 0.12, 0.09, 1)",
        "d": "Color(0.26, 0.28, 0.27, 1)", "e": "Color(0.10, 0.07, 0.05, 1)", "f": "Color(0.30, 0.24, 0.14, 1)",
        "ivo": "Color(0.24, 0.15, 0.08, 1)",  # M3-CHR-540: Ivo's warm brown
        "officer": "Color(0.22, 0.20, 0.17, 1)"}  # M3-CHR-593: the Ch8 officer's grey-brown


def hexcol(h: str, k: float = 1.0) -> str:
    r, g, b = (int(h[i:i + 2], 16) / 255.0 * k for i in (1, 3, 5))
    return f"Color({r:.3f}, {g:.3f}, {b:.3f}, 1)"


def write(v: str) -> None:
    extra = variant_params(v)
    n = name(v)
    T = f"{n}/textures/{n}_"
    worn = bool(extra["_variant"]["weathered"])
    hair = extra["_hair"]["colour"]
    table = {}
    for key, (shader, prio, params, tex) in mw.SHADER_MATERIALS.items():
        params, tex = dict(params), {k: val.replace("moll/textures/moll_head_", T + "head_")
                                     .replace("moll/textures/moll_body_", T + "body_") for k, val in tex.items()}
        if key in ("cloth", "shield") and worn:
            tex = {k: (val.replace(f"moll/textures/moll_{key}_", f"{WORN}{key}_") if k in ("tex_albedo", "tex_orm")
                       else val) for k, val in tex.items()}
        if key == "eye":
            params["col_iris"] = IRIS[v]
        if key in ("lash", "brow"):
            params["col_root"] = params["col_tip"] = hexcol(hair)
        if key == "hair":
            params["col_root"], params["col_tip"] = hexcol(hair, 0.8), hexcol(hair, 1.05)
        table[key] = (shader, prio, params, tex)
    out = ROOT / "assets" / "characters" / n / "materials"
    mw.wm.OUT = out
    mw.wm.TEX = "res://assets/characters"
    out.mkdir(parents=True, exist_ok=True)
    for key, (shader, prio, params, tex) in table.items():
        mw.wm.write_shader_material(key, shader, prio, params, tex)
    standard = {"bronze": mw.STANDARD_MATERIALS["bronze"], "steel": STEEL, "spear": SPEAR}
    if not extra["_variant"].get("spear", True):  # M3-CHR-540: no spear, so no shaft or blade materials
        standard = {"bronze": standard["bronze"]}
    for key, body in standard.items():
        mw.wm.write_standard_material(key, body, SPEAR_TEX if key == "spear" else {})
    print(f"wrote {len(table) + len(standard)} materials to {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", action="append", choices=builds())  # none named: the six soldiers
    for v in ap.parse_args().variant or variants():
        write(v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
