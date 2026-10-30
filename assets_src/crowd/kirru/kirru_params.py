"""The Kirru crowd bodies' parameters (kirru_bodies.json): Pell's pell_params.json with a body's overrides deep-merged on
top. Shared by build_kirru.py (Blender) and kirru_textures.py (python3), so both read the same merged file."""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BODIES = HERE / "kirru_bodies.json"
PELL_PARAMS = ROOT / "assets_src" / "characters" / "pell" / "pell_params.json"
CROWD = ROOT / "assets" / "crowd"


def bodies() -> dict:
    return json.loads(BODIES.read_text(encoding="utf-8"))


def merge(base: dict, over: dict) -> dict:
    """`over` on `base`, dict by dict (lists and values replace); `base`'s key order kept, new keys appended."""
    out = copy.deepcopy(base)
    for k, v in over.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


# Pell's costume and name-shell are measured in his own metres (pell_params `_costume`: "metres, not scaled"); on a
# body of another height every `*_m` measure there is scaled by the heights' ratio, so a youngster's mantle and cords
# fit it (the first youngster build had its mantle bunched and a cord loop standing off the shoulder).
SCALED = ("_costume", "_shell")


def _scale_m(block: dict, k: float) -> dict:
    out = {}
    for key, v in block.items():
        if key.endswith("_m") and isinstance(v, (int, float)) and not isinstance(v, bool):
            out[key] = round(float(v) * k, 6)
        elif key.endswith("_m") and isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
            out[key] = [round(float(x) * k, 6) for x in v]
        else:
            out[key] = v
    return out


def params(body: str) -> dict:
    spec = bodies()["bodies"][body]
    pell = json.loads(PELL_PARAMS.read_text(encoding="utf-8"))
    merged = merge(pell, spec["overrides"])
    k = float(merged["height_m"]) / float(pell["height_m"])
    for name in SCALED:
        merged[name] = _scale_m(merged[name], k)
    return merged


def texture_overrides(body: str) -> dict:
    """pell_textures module constants a body sets (the mantle's reed: REED, REED_SHADE)."""
    return dict(bodies()["bodies"][body].get("textures", {}))


def write_params(body: str, out_dir: Path) -> Path:
    """The merged params as <out_dir>/<body>_params.json (fixed key order and formatting)."""
    path = Path(out_dir) / f"{body}_params.json"
    path.write_text(json.dumps(params(body), indent=2) + "\n", encoding="utf-8")
    return path


def asset_dir(body: str) -> Path:
    return CROWD / body
