"""Writes an ambient animal's material resources (M3-CRE-611): assets/wildlife/<id>/materials/<slot>.tres.

python3 assets_src/wildlife/common/write_materials.py --wildlife gull

Each slot in assets_src/wildlife/<id>/materials.json becomes a ShaderMaterial on
res://game/world/wildlife/wildlife.gdshader with the listed parameters (colours as palette hex, vectors as
[x, y, z]). The import rule (game/data/import/wildlife.json) puts them on the GLB's surfaces by glTF material name,
and WildlifeLayer draws the meshes with them through MultiMesh.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHADER = "res://game/world/wildlife/wildlife.gdshader"


def _value(v) -> str:
    if isinstance(v, str) and v.startswith("#"):
        h = v.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        return f"Color({r:.6g}, {g:.6g}, {b:.6g}, 1)"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return f"{float(v):.6g}"
    if isinstance(v, list) and len(v) == 3 and all(isinstance(c, (int, float)) for c in v):
        return "Vector3({:.6g}, {:.6g}, {:.6g})".format(*(float(c) for c in v))
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


def write(animal: str, root: Path = ROOT) -> list[Path]:
    spec = json.loads((root / "assets_src" / "wildlife" / animal / "materials.json").read_text(encoding="utf-8"))
    out_dir = root / "assets" / "wildlife" / animal / "materials"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for slot in sorted(spec["slots"]):
        p = out_dir / f"{slot}.tres"
        p.write_text(material_text(slot, spec["slots"][slot]), encoding="utf-8")
        written.append(p)
    return written


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wildlife", required=True)
    args = ap.parse_args()
    for p in write(args.wildlife):
        print(p.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
