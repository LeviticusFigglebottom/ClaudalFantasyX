"""The Stillguard variant table (no bpy), M3-CHR-508: stillguard_variants.json merged per variant."""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLE = HERE / "stillguard_variants.json"
PREFIX = "stillguard_"


def table() -> dict:
    return json.loads(TABLE.read_text(encoding="utf-8"))


def variants() -> list[str]:
    return sorted(table()["variants"])


def name(v: str) -> str:
    return f"{PREFIX}{v}"


def variant_params(v: str) -> dict:
    """The merged table of variant `v`: Moll's bb block, the variant's overrides, `_costume`, `_variant`, `_hair` (its
    colours over `_hair_shared`, its own seed) and `_skin` (over `_skin_shared`)."""
    t = table()
    var = t["variants"][v]
    out = dict(copy.deepcopy(t["_shared"]), name=name(v))
    out.update({k: val for k, val in var.items() if not k.startswith("_")})
    out["_costume"] = copy.deepcopy(t["_costume"])
    out["_variant"] = dict(var["_variant"])
    out["_hair"] = dict(t["_hair_shared"], **var["_hair"])
    out["_skin"] = dict(t["_skin_shared"], seed=ord(v), **var["_skin"])
    out["_hair"]["seed"] = int(out["_hair"]["seed"]) + ord(v)
    return out
