"""The Kirru people on Pell's build (M4-A2P-053; act2_roster: the Kirru are a people, never monsters). A variant is
assets_src/characters/kirru/variants/<id>.json: Pell's pell_params.json with that file's keys over it (dicts merged
key by key, `_about` replaced), built under its own id (assets/characters/<id>/). build_pell.py, pell_textures.py and
write_materials.py take `--variant <id>`; with none they build Pell exactly as before. Pell's cloth, fur and feather
atlases are shared (a variant writes only its own head and body maps). No bpy. Deterministic.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PELL_PARAMS = HERE / "pell_params.json"
VARIANTS = HERE.parent / "kirru" / "variants"


def variants() -> list[str]:
    return sorted(p.stem for p in VARIANTS.glob("*.json"))


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict) and k != "_about":
            out[k] = _merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def extra(variant: str | None) -> dict:
    """The merged table (Pell's when `variant` is None)."""
    base = json.loads(PELL_PARAMS.read_text(encoding="utf-8"))
    if not variant:
        return base
    over = json.loads((VARIANTS / f"{variant}.json").read_text(encoding="utf-8"))
    return dict(_merge(base, over), name=variant)


def params_file(variant: str | None, scratch: Path) -> Path:
    """A params file bb_params can load: Pell's own, or the merged table written into `scratch`."""
    if not variant:
        return PELL_PARAMS
    scratch.mkdir(parents=True, exist_ok=True)
    p = scratch / f"{variant}_params.json"
    p.write_text(json.dumps(extra(variant), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return p


def out_dir(variant: str | None) -> Path:
    return ROOT / "assets" / "characters" / (variant or "pell")
