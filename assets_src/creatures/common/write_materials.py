"""Writes a creature's material resources (M2-CRE-02): assets/creatures/<id>/materials/<slot>.tres.

python3 assets_src/creatures/common/write_materials.py --creature reef_crab

Each slot in assets_src/creatures/<id>/materials.json becomes a ShaderMaterial on
res://game/shaders/creature/creature.gdshader with the listed parameters (colours as palette hex). The import rule
(game/data/import/creatures.json) puts them on the GLB's surfaces by glTF material name.

An optional `held` block (M3-CRE-647, the Vowbound as foes) writes a second set to
assets/creatures/<id>/materials_held/<slot>.tres: every emissive slot (emission_energy > 0) must carry the block's
`emission_from` colour (glimmer_bound) and gets its `emission_to` (glimmer_held) at the same energy, steady (no
pulse); every other slot is copied as it is. CreatureActor's `material_dir` puts that set on the held battle scene.
Without the block nothing more is written, and the `materials/` set is the same either way.
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


HELD_DIR = "materials_held"
HELD_KEYS = {"_doc", "emission_from", "emission_to"}
PULSE_KEYS = ("emission_pulse_hz", "emission_pulse_depth")


def held_slots(slots: dict, held: dict) -> dict:
    """The held set's slot parameters: each emissive slot's `emission_from` colour becomes `emission_to` (same
    energy, steady); the rest are copied. Raises ValueError for a block or a slot it cannot apply to."""
    unknown = sorted(set(held) - HELD_KEYS)
    if unknown:
        raise ValueError(f"held: unknown key(s) {', '.join(unknown)}")
    src, dst = held.get("emission_from"), held.get("emission_to")
    if not all(isinstance(v, str) and v.startswith("#") and len(v) == 7 for v in (src, dst)):
        raise ValueError("held: emission_from and emission_to must be #RRGGBB palette colours")
    out, swapped = {}, 0
    for slot, params in slots.items():
        p = dict(params)
        if float(p.get("emission_energy", 0.0)) > 0.0:
            if str(p.get("emission_color", "")).upper() != src.upper():
                raise ValueError(f"held: emissive slot '{slot}' is not {src}, so the swap would be ambiguous")
            if any(float(p.get(k, 0.0)) != 0.0 for k in PULSE_KEYS):
                raise ValueError(f"held: emissive slot '{slot}' pulses; held light is steady")
            p["emission_color"] = dst
            swapped += 1
        out[slot] = p
    if swapped == 0:
        raise ValueError("held: no emissive slot to swap")
    return out


def _write_set(out_dir: Path, slots: dict) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for slot in sorted(slots):
        p = out_dir / f"{slot}.tres"
        p.write_text(material_text(slot, slots[slot]), encoding="utf-8")
        written.append(p)
    return written


def write(creature: str, root: Path = ROOT) -> list[Path]:
    spec = json.loads((root / "assets_src" / "creatures" / creature / "materials.json").read_text(encoding="utf-8"))
    base = root / "assets" / "creatures" / creature
    written = _write_set(base / "materials", spec["slots"])
    if "held" in spec:
        written += _write_set(base / HELD_DIR, held_slots(spec["slots"], spec["held"]))
    return written


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--creature", required=True)
    args = ap.parse_args()
    for p in write(args.creature):
        print(p.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
