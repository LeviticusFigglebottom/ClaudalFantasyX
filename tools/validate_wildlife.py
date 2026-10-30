#!/usr/bin/env python3
"""Ambient wildlife data checks (M3-CRE-611, docs/kb/art/wildlife.md). Run by tools/validate_data.py.

* game/data/world/wildlife/wildlife.json: the four kinds (gull, crab, fish, insect) with every tuning key
  WildlifeLayer reads, their scene, mesh names and material(s) that exist, [lo, hi] ranges in order, the budgets and
  culling. The insect kind (M3-CRE-616) keeps its tuning in a `moth`, a `dragonfly` and (Ch10, M4-A2P-056) a
  `firefly` table, one material per mesh.
* game/data/world/wildlife/<zone>.json (every other file there) and the review stage's data: the `zone` id names
  the file (ch02/haluna -> ch02_haluna.json) and is a locations.json location; flocks (and kingfisher flocks, Ch10),
  beaches and shoals are
  well formed (unique ids, positive counts, perches inside the flock's radius, perched_at_start no more than the
  perches), herds (Ch12's woolbacks: [x, z] centre, radius, optional y), swarms too (type moth, dragonfly or firefly, perches only on a dragonfly patrol and inside its radius), and the
  zone's totals stay within the budgets.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path

WILDLIFE_DIR = "game/data/world/wildlife"
KINDS_FILE = f"{WILDLIFE_DIR}/wildlife.json"
STAGE_FILE = "game/levels/_tests/wildlife/wildlife_stage.json"
LOCATIONS_FILE = "game/data/world/locations.json"
TEST_ZONE_PREFIX = "_tests/"

KIND_KEYS = {
    "gull": {"scale", "speed_mps", "orbit_fraction", "counter_orbit_chance", "undulate_m", "bank_max_deg",
             "pitch_max_deg", "flap_hz", "flap_s", "glide_s", "glide_dihedral_deg", "amp_rate", "decide_s",
             "perch_chance", "approach_s", "landing_speed_mps", "takeoff_s", "takeoff_lift_m", "perch_s",
             "head_turn_s", "head_yaw_deg", "head_rate", "nod_chance", "nod_hz", "gravity_mps2", "flap_start_chance",
             "flare_from", "approach_amp", "takeoff_lead_deg", "takeoff_speed_fraction"},
    "crab": {"scale", "flee_radius_m", "safe_radius_m", "flee_speed_mps", "walk_speed_mps", "turn_rate",
             "return_after_s", "shuffle_s", "shuffle_m", "gait_hz", "walk_gait_hz", "amp_rate", "arrive_m"},
    "fish": {"scale", "speed_mps", "dart_speed_mps", "spread_m", "follow_rate", "turn_rate", "wander_arrive_m",
             "wobble_m", "wobble_hz", "startle_radius_m", "startle_s", "swim_hz", "swim_hz_per_mps", "swim_amp",
             "bottom_clearance_m", "startle_follow_mult", "wobble_y_fraction"},
    "insect": {"moth", "dragonfly", "firefly"},  # tables: INSECT_KEYS
}
# the kingfisher (Ch10, M4-A2P-056) is the gull's flock with its own tuning, meshes and rows
KIND_KEYS["kingfisher"] = KIND_KEYS["gull"] | {"dive_chance", "dive_reach_m", "dive_s", "dive_speed_mps", "dive_hold_s",
                                               "dive_return_s"}  # its plunge (fen_kingfisher.md)
# the woolback (Ch12, M4-A2P-056): skinned actors in herds (WildlifeHerd), its scene an actor .tscn, no meshes table
KIND_KEYS["woolback"] = {"scale", "walk_speed_mps", "turn_rate", "graze_s", "look_chance", "look_s", "look_radius_m",
                         "look_rate", "wander_m", "spacing_m", "arrive_m", "height_m", "bounds_pad_m"}
SKINNED_KINDS = {"woolback"}
# the rim ray (Ch16, M4-A2P-056) is the fish shoal with its own tuning, mesh and rows
KIND_KEYS["ray"] = KIND_KEYS["fish"]
# The insect kind's tables (WildlifeSwarm): every key, and the ones drawn once per insect from a [lo, hi] range
# (the rest are read as plain numbers).
INSECT_KEYS = {
    "moth": {"scale", "orbit_fraction", "orbit_hz", "counter_orbit_chance", "height_m", "bob_m", "bob_hz",
             "jitter_m", "jitter_s", "jitter_rate", "dart_m", "dart_s", "dart_time_s", "dart_rate_mult", "turn_rate",
             "flutter_hz", "flutter_amp"},
    "dragonfly": {"scale", "height_m", "hover_s", "hover_amp", "drift_m", "drift_hz", "dart_m", "dart_speed_mps",
                  "dart_amp", "perch_chance", "perch_s", "flee_radius_m", "flee_m", "flee_speed_mps", "turn_rate",
                  "amp_rate", "flutter_hz"},
}
# the firefly flies the moth's orbit, and blinks
INSECT_KEYS["firefly"] = INSECT_KEYS["moth"] | {"blink_s", "blink_on_s", "glow_floor"}
INSECT_RANGES = {
    "moth": {"scale", "orbit_fraction", "orbit_hz", "bob_hz", "jitter_s", "dart_s", "flutter_hz"},
    "dragonfly": {"scale", "hover_s", "drift_hz", "dart_m", "dart_speed_mps", "perch_s", "flutter_hz"},
}
INSECT_RANGES["firefly"] = INSECT_RANGES["moth"] | {"blink_s"}
SWARM_TYPES = set(INSECT_KEYS)
KIND_MESHES = {"gull": {"flying", "perched"}, "crab": {"body"}, "fish": {"body"}, "insect": {"moth", "dragonfly", "firefly"},
               "kingfisher": {"flying", "perched"}, "ray": {"body"}}
KIND_COMMON = {"scene", "meshes", "material", "cast_shadow"}
BUDGET_KEYS = {"gulls", "kingfishers", "woolbacks", "crabs", "fish", "rays", "insects", "draw_calls", "ms_per_frame"}
# zone row tables -> (budget key, required keys, optional keys)
ROWS = {
    "flocks": ("gulls", {"id", "center", "radius_m", "altitude_m", "count", "perches"}, {"perched_at_start"}),
    "kingfishers": ("kingfishers", {"id", "center", "radius_m", "altitude_m", "count", "perches"},
                    {"perched_at_start", "water_y"}),
    "beaches": ("crabs", {"id", "center", "half_extents", "count"}, {"yaw_deg", "y"}),
    "shoals": ("fish", {"id", "center", "radius_m", "count"}, {"scale", "spread_m"}),
    "swarms": ("insects", {"id", "type", "center", "radius_m", "count"}, {"perches"}),
    "rays": ("rays", {"id", "center", "radius_m", "count"}, {"scale", "spread_m"}),
    "herds": ("woolbacks", {"id", "center", "radius_m", "count"}, {"y"}),
}
ZONE_KEYS = {"zone", "ground", "flocks", "kingfishers", "beaches", "shoals", "rays", "swarms", "herds"}


def _num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _vec(v: object, n: int) -> bool:
    return isinstance(v, list) and len(v) == n and all(_num(x) for x in v)


def _range_or_num(v: object) -> bool:
    return _num(v) or (_vec(v, 2) and v[0] <= v[1])


def _res_exists(res: str, exists: Callable[[str], bool]) -> bool:
    return isinstance(res, str) and res.startswith("res://") and exists(res)


def kinds_errors(doc: object, exists: Callable[[str], bool]) -> list[str]:
    w0 = KINDS_FILE
    if not isinstance(doc, dict):
        return [f"{w0}: must be an object"]
    errs: list[str] = []
    kinds = doc.get("kinds")
    if not isinstance(kinds, dict) or set(kinds) != set(KIND_KEYS):
        return errs + [f"{w0}.kinds: must have exactly {sorted(KIND_KEYS)}"]
    for kid, keys in KIND_KEYS.items():
        k = kinds[kid]
        w = f"{w0}.kinds.{kid}"
        if not isinstance(k, dict):
            errs.append(f"{w}: must be an object")
            continue
        common = {"scene"} if kid in SKINNED_KINDS else KIND_COMMON
        missing = (keys | common) - set(k)
        if missing:
            errs.append(f"{w}: missing {sorted(missing)}")
        unknown = set(k) - keys - common - {"_doc"}
        if unknown:
            errs.append(f"{w}: unknown keys {sorted(unknown)}")
        if kid == "insect":
            errs += _insect_table_errors(k, w)
        else:
            for key in keys & set(k):
                v = k[key]
                ok = _vec(v, 3) if key == "spread_m" else _range_or_num(v)
                if not ok:
                    errs.append(f"{w}.{key}: must be a number or a [lo, hi] range")
        if not _res_exists(k.get("scene", ""), exists):
            errs.append(f"{w}.scene: {k.get('scene')!r} does not exist")
        if kid in SKINNED_KINDS:
            if not str(k.get("scene", "")).endswith(".tscn"):
                errs.append(f"{w}.scene: must be the actor scene (.tscn)")
            continue
        material = k.get("material", "")
        if isinstance(material, dict):  # one per mesh (the insects)
            if set(material) != KIND_MESHES[kid]:
                errs.append(f"{w}.material: one per mesh, {sorted(KIND_MESHES[kid])}")
            for mk, res in sorted(material.items()):
                if not _res_exists(res, exists):
                    errs.append(f"{w}.material.{mk}: {res!r} does not exist")
        elif not _res_exists(material, exists):
            errs.append(f"{w}.material: {material!r} does not exist")
        meshes = k.get("meshes")
        if not isinstance(meshes, dict) or set(meshes) != KIND_MESHES[kid]:
            errs.append(f"{w}.meshes: must name {sorted(KIND_MESHES[kid])}")
        shadows = k.get("cast_shadow")
        if not isinstance(shadows, dict) or set(shadows) != KIND_MESHES[kid] or not all(
                isinstance(b, bool) for b in shadows.values()):
            errs.append(f"{w}.cast_shadow: a bool for each of {sorted(KIND_MESHES[kid])}")
    budgets = doc.get("budgets")
    if not isinstance(budgets, dict) or not BUDGET_KEYS <= set(budgets):
        errs.append(f"{w0}.budgets: must have {sorted(BUDGET_KEYS)}")
    else:
        for key in BUDGET_KEYS:
            if not _num(budgets[key]) or budgets[key] <= 0:
                errs.append(f"{w0}.budgets.{key}: must be a positive number")
    cull = doc.get("cull")
    if not isinstance(cull, dict) or not _num(cull.get("distance_m")) or not isinstance(cull.get("frustum"), bool):
        errs.append(f"{w0}.cull: needs distance_m (number) and frustum (bool)")
    return errs


def _insect_table_errors(k: dict, w: str) -> list[str]:
    errs: list[str] = []
    for table, keys in INSECT_KEYS.items():
        t = k.get(table)
        wt = f"{w}.{table}"
        if not isinstance(t, dict):
            errs.append(f"{wt}: must be an object")
            continue
        missing = keys - set(t)
        if missing:
            errs.append(f"{wt}: missing {sorted(missing)}")
        unknown = set(t) - keys - {"_doc"}
        if unknown:
            errs.append(f"{wt}: unknown keys {sorted(unknown)}")
        for key in keys & set(t):
            v = t[key]
            if key in INSECT_RANGES[table]:
                if not _range_or_num(v):
                    errs.append(f"{wt}.{key}: must be a number or a [lo, hi] range")
            elif not _num(v) or v < 0:
                errs.append(f"{wt}.{key}: must be a non-negative number")
    return errs


def zone_file_name(zone_id: str) -> str:
    return zone_id.replace("/", "_") + ".json"


def zone_errors(doc: object, where: str, budgets: dict, location_ids: set[str] | None) -> list[str]:
    """Errors for one placement file. `location_ids` None skips the zone-id checks (the review stage)."""
    if not isinstance(doc, dict):
        return [f"{where}: must be an object"]
    errs: list[str] = []
    unknown = set(doc) - ZONE_KEYS - {"_doc"}
    if unknown:
        errs.append(f"{where}: unknown keys {sorted(unknown)}")
    zone = doc.get("zone")
    if not isinstance(zone, str) or not zone:
        errs.append(f"{where}.zone: must be the zone's location id")
    elif location_ids is not None:
        if Path(where).name != zone_file_name(zone):
            errs.append(f"{where}: zone {zone!r} belongs in {zone_file_name(zone)}")
        if zone not in location_ids:
            errs.append(f"{where}.zone: {zone!r} is not a locations.json location")
    ground = doc.get("ground")
    physics = isinstance(ground, dict) and ground.get("physics") is True and set(ground) == {"physics"}
    if ground is not None and not physics and not (isinstance(ground, dict) and isinstance(ground.get("node"), str)
                                                   and isinstance(ground.get("method"), str)):
        errs.append(f"{where}.ground: needs node (a path from the zone root) and method, or physics: true alone")
    for table, (budget, required, optional) in ROWS.items():
        rows = doc.get(table, [])
        if not isinstance(rows, list):
            errs.append(f"{where}.{table}: must be a list")
            continue
        total = 0
        seen: set[str] = set()
        for i, row in enumerate(rows):
            w = f"{where}.{table}[{i}]"
            if not isinstance(row, dict):
                errs.append(f"{w}: must be an object")
                continue
            missing = required - set(row)
            if missing:
                errs.append(f"{w}: missing {sorted(missing)}")
                continue
            extra = set(row) - required - optional - {"_doc"}
            if extra:
                errs.append(f"{w}: unknown keys {sorted(extra)}")
            rid = row["id"]
            if not isinstance(rid, str) or not rid or rid in seen:
                errs.append(f"{w}.id: must be a unique non-empty string")
            seen.add(rid if isinstance(rid, str) else "")
            count = row["count"]
            if not isinstance(count, int) or isinstance(count, bool) or count < 1:
                errs.append(f"{w}.count: must be a positive integer")
            else:
                total += count
            errs += _row_errors(table, row, w)
        if _num(budgets.get(budget)) and total > budgets[budget]:
            errs.append(f"{where}.{table}: {total} {budget} is over the budget of {budgets[budget]}")
    return errs


def _row_errors(table: str, row: dict, w: str) -> list[str]:
    errs: list[str] = []
    if table in ("flocks", "kingfishers"):
        if not _vec(row["center"], 2):
            return [f"{w}.center: must be [x, z]"]
        r = row["radius_m"]
        if not _num(r) or r <= 0:
            return [f"{w}.radius_m: must be positive"]
        if not (_vec(row["altitude_m"], 2) and row["altitude_m"][0] <= row["altitude_m"][1]):
            errs.append(f"{w}.altitude_m: must be [lo, hi]")
        perches = row["perches"]
        if not isinstance(perches, list):
            return errs + [f"{w}.perches: must be a list"]
        cx, cz = row["center"]
        for k, p in enumerate(perches):
            if not _vec(p, 4):
                errs.append(f"{w}.perches[{k}]: must be [x, y, z, yaw_deg]")
            elif ((p[0] - cx) ** 2 + (p[2] - cz) ** 2) ** 0.5 > r:
                errs.append(f"{w}.perches[{k}]: outside the flock's radius_m")
        start = row.get("perched_at_start", 0)
        if not isinstance(start, int) or start < 0 or start > len(perches):
            errs.append(f"{w}.perched_at_start: an integer, at most the number of perches")
        if "water_y" in row:  # a kingfisher's plunge goes down to it
            wy = row["water_y"]
            if not isinstance(wy, (int, float)) or isinstance(wy, bool):
                errs.append(f"{w}.water_y: must be a number")
            elif any(_vec(p, 4) and p[1] <= wy for p in perches):
                errs.append(f"{w}.water_y: must be below every perch")
    elif table == "swarms":
        if row["type"] not in SWARM_TYPES:
            errs.append(f"{w}.type: must be one of {sorted(SWARM_TYPES)}")
        if not _vec(row["center"], 3):
            return errs + [f"{w}.center: must be [x, y, z]"]
        r = row["radius_m"]
        if not _num(r) or r <= 0:
            return errs + [f"{w}.radius_m: must be positive"]
        perches = row.get("perches", [])
        if not isinstance(perches, list):
            return errs + [f"{w}.perches: must be a list"]
        if perches and row["type"] != "dragonfly":
            errs.append(f"{w}.perches: only a dragonfly patrol perches")
        cx, _cy, cz = row["center"]
        for k, p in enumerate(perches):
            if not _vec(p, 4):
                errs.append(f"{w}.perches[{k}]: must be [x, y, z, yaw_deg]")
            elif ((p[0] - cx) ** 2 + (p[2] - cz) ** 2) ** 0.5 > r:
                errs.append(f"{w}.perches[{k}]: outside the swarm's radius_m")
    elif table == "herds":
        if not _vec(row["center"], 2):
            errs.append(f"{w}.center: must be [x, z]")
        if not _num(row["radius_m"]) or row["radius_m"] <= 0:
            errs.append(f"{w}.radius_m: must be positive")
        if "y" in row and not _num(row["y"]):
            errs.append(f"{w}.y: must be a number")
    elif table == "beaches":
        if not _vec(row["center"], 2):
            errs.append(f"{w}.center: must be [x, z]")
        if not (_vec(row["half_extents"], 2) and min(row["half_extents"]) > 0):
            errs.append(f"{w}.half_extents: must be two positive numbers")
        for key in ("yaw_deg", "y"):
            if key in row and not _num(row[key]):
                errs.append(f"{w}.{key}: must be a number")
    else:
        if not _vec(row["center"], 3):
            errs.append(f"{w}.center: must be [x, y, z]")
        if not _num(row["radius_m"]) or row["radius_m"] <= 0:
            errs.append(f"{w}.radius_m: must be positive")
        if "scale" in row and (not _num(row["scale"]) or row["scale"] <= 0):
            errs.append(f"{w}.scale: must be positive")
        if "spread_m" in row and not _vec(row["spread_m"], 3):
            errs.append(f"{w}.spread_m: must be [x, y, z]")
    return errs


def wildlife_errors(root: Path) -> list[str]:
    def exists(res: str) -> bool:
        return (root / res[len("res://"):]).is_file()

    def load(rel: str) -> object:
        try:
            return json.loads((root / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            return e

    kinds = load(KINDS_FILE)
    if isinstance(kinds, Exception):
        return [f"{KINDS_FILE}: {kinds}"]
    errs = kinds_errors(kinds, exists)
    budgets = kinds.get("budgets", {}) if isinstance(kinds, dict) else {}
    locations = load(LOCATIONS_FILE)
    location_ids = {r.get("id") for r in locations.get("locations", [])} if isinstance(locations, dict) else set()
    for p in sorted((root / WILDLIFE_DIR).glob("*.json")):
        rel = p.relative_to(root).as_posix()
        if rel == KINDS_FILE:
            continue
        doc = load(rel)
        errs += [f"{rel}: {doc}"] if isinstance(doc, Exception) else zone_errors(doc, rel, budgets, location_ids)
    stage = load(STAGE_FILE)
    if isinstance(stage, Exception):
        errs.append(f"{STAGE_FILE}: {stage}")
    else:
        errs += zone_errors(stage, STAGE_FILE, budgets, None)
        if isinstance(stage, dict) and not str(stage.get("zone", "")).startswith(TEST_ZONE_PREFIX):
            errs.append(f"{STAGE_FILE}.zone: a review stage's id starts with {TEST_ZONE_PREFIX}")
    return errs


def check_wildlife(root: Path, rep) -> None:
    for e in wildlife_errors(root):
        rep.err(e)


def main() -> int:
    errs = wildlife_errors(Path(__file__).resolve().parents[1])
    for e in errs:
        print(f"ERROR {e}")
    print(f"wildlife: {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
