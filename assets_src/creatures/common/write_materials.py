"""Writes a creature's material resources (M2-CRE-02): assets/creatures/<id>/materials/<slot>.tres.

python3 assets_src/creatures/common/write_materials.py --creature reef_crab

Each slot in assets_src/creatures/<id>/materials.json becomes a ShaderMaterial on
res://game/shaders/creature/creature.gdshader with the listed parameters (colours as palette hex). The import rule
(game/data/import/creatures.json) puts them on the GLB's surfaces by glTF material name.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHADER = "res://game/shaders/creature/creature.gdshader"


def _value(v) -> str:
    if isinstance(v, str) and v.startswith("#"):
        h = v.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        return f"Color({r:.6g}, {g:.6g}, {b:.6g}, 1)"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return f"{float(v):.6g}"
    raise ValueError(f"unsupported parameter value {v!r}")


def material_text(slot: str, params: dict) -> str:
    lines = [
        '[gd_resource type="ShaderMaterial" load_steps=2 format=3]',
        "",
        f'[ext_resource type="Shader" path="{SHADER}" id="1_shader"]',
        "",
        "[resource]",
        f'resource_name = "{slot}"',
        'shader = ExtResource("1_shader")',
    ]
    for k in sorted(params):
        lines.append(f"shader_parameter/{k} = {_value(params[k])}")
    return "\n".join(lines) + "\n"


def write(creature: str, root: Path = ROOT) -> list[Path]:
    spec = json.loads((root / "assets_src" / "creatures" / creature / "materials.json").read_text(encoding="utf-8"))
    out_dir = root / "assets" / "creatures" / creature / "materials"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for slot in sorted(spec["slots"]):
        p = out_dir / f"{slot}.tres"
        p.write_text(material_text(slot, spec["slots"][slot]), encoding="utf-8")
        written.append(p)
    return written


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--creature", required=True)
    args = ap.parse_args()
    for p in write(args.creature):
        print(p.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
