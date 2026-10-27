#!/usr/bin/env python3
"""Field villager data checks (M3-CRE-610/613, docs/kb/tech/field_npc.md). Run by tools/validate_data.py.

* game/data/world/npc/npc.json: `defaults` carries every routine section FieldNpc reads; [lo, hi] ranges are in
  order; every `villagers` row names a villager with an actor scene.
* game/data/world/npc/zones/<zone>.json (and the test stage's data): the `zone` id names the file
  (ch02/haluna -> ch02_haluna.json) and is a locations.json location; each row's npc_id (or its `actor`, a
  villager whose model it wears) has an actor scene, is
  unique in the zone and has a stand_in path; chat_with names another row that chats back; route entries are
  points or {at, pause_sec, activity} with a known activity; shelter and work_at are [x, y, z] or
  [x, y, z, yaw_deg]; storm_flag (when set) is a declared flag.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NPC_FILE = "game/data/world/npc/npc.json"
ZONES_DIR = "game/data/world/npc/zones"
STAGE_FILES = ("game/levels/_tests/npc/villager_layer_stage.json", "game/levels/_tests/npc/villager_layer_adopt.json")
LOCATIONS_FILE = "game/data/world/locations.json"
FLAGS_FILE = "game/data/flags.tres"
ACTOR = "assets/characters/villagers/{id}/{id}_actor.tscn"
TEST_ZONE_PREFIX = "_tests/"
ACTIVITIES = {"", "work"}
ATTACH = {"beside", "child"}
ROUTINE_SECTIONS = {
    "look": {"bones", "max_yaw_deg", "max_pitch_up_deg", "max_pitch_down_deg", "smoothing_sec",
             "max_rate_deg_per_sec", "max_substep_sec", "head_height_m", "player_eye_height_m"},
    "glance": {"radius_m", "hold_sec", "rest_sec"},
    "look_around": {"every_sec", "hold_sec", "yaw_deg"},
    "chat": {"max_distance_m", "turn_sec", "pause_share", "bout_sec", "quiet_sec"},
    "storm": {"react_sec", "walk_speed_mps", "brace_pitch_deg", "brace_yaw_share", "sky_every_sec", "sky_look_sec",
              "sky_pitch_deg", "idle_playback"},
}


def _load(path: Path, errs: list[str]) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        errs.append(f"{path}: cannot read ({e})")
        return {}
    if not isinstance(data, dict):
        errs.append(f"{path}: not an object")
        return {}
    return data


def _ranges(where: str, section: dict, errs: list[str]) -> None:
    for key, v in section.items():
        if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v) and v[0] > v[1]:
            errs.append(f"{where}.{key}: range {v} is not in order")


def _point(v: object) -> bool:
    return isinstance(v, list) and len(v) in (3, 4) and all(isinstance(x, (int, float)) for x in v)


def tuning_errors(root: Path) -> list[str]:
    errs: list[str] = []
    data = _load(root / NPC_FILE, errs)
    defaults = data.get("defaults", {})
    for name, keys in ROUTINE_SECTIONS.items():
        section = defaults.get(name)
        if not isinstance(section, dict):
            errs.append(f"{NPC_FILE}: defaults.{name} missing")
            continue
        missing = sorted(keys - set(section))
        if missing:
            errs.append(f"{NPC_FILE}: defaults.{name} lacks {', '.join(missing)}")
        _ranges(f"{NPC_FILE}: defaults.{name}", section, errs)
    for vid, row in data.get("villagers", {}).items():
        if not (root / ACTOR.format(id=vid)).exists():
            errs.append(f"{NPC_FILE}: villagers.{vid} has no actor scene ({ACTOR.format(id=vid)})")
        for name, section in row.items():
            if isinstance(section, dict):
                _ranges(f"{NPC_FILE}: villagers.{vid}.{name}", section, errs)
    return errs


def _declared_flags(root: Path) -> set[str]:
    try:
        text = (root / FLAGS_FILE).read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(re.findall(r'^"([a-z0-9_]+)":', text, re.M))


def _location_ids(root: Path) -> set[str]:
    data = _load(root / LOCATIONS_FILE, [])
    locs = data.get("locations", data)
    if isinstance(locs, dict):
        return set(locs)
    return {str(x.get("id")) for x in locs if isinstance(x, dict)}


def zone_errors(root: Path, rel: str, locations: set[str], flags: set[str]) -> list[str]:
    errs: list[str] = []
    path = root / rel
    data = _load(path, errs)
    if not data:
        return errs
    zone = str(data.get("zone", ""))
    if not zone.startswith(TEST_ZONE_PREFIX):
        if path.name != zone.replace("/", "_") + ".json":
            errs.append(f"{rel}: zone {zone!r} does not name the file")
        if zone not in locations:
            errs.append(f"{rel}: zone {zone!r} is not a location in {LOCATIONS_FILE}")
    flag = str(data.get("storm_flag", ""))
    if flag and flag not in flags:
        errs.append(f"{rel}: storm_flag {flag!r} is not declared in {FLAGS_FILE}")
    rows = data.get("villagers", [])
    by_id: dict[str, dict] = {}
    for i, row in enumerate(rows):
        where = f"{rel}: villagers[{i}]"
        if not isinstance(row, dict):
            errs.append(f"{where}: not an object")
            continue
        vid = str(row.get("npc_id", ""))
        if vid in by_id:
            errs.append(f"{where}: npc_id {vid!r} appears twice")
        by_id[vid] = row
        actor = str(row.get("actor", vid))
        if not (root / ACTOR.format(id=actor)).exists():
            errs.append(f"{where}: npc_id {vid!r} has no actor scene" if actor == vid
                        else f"{where}: actor {actor!r} (worn by {vid!r}) has no actor scene")
        if not str(row.get("stand_in", "")):
            errs.append(f"{where}: no stand_in")
        for key in ("shelter", "work_at"):
            if key in row and not _point(row[key]):
                errs.append(f"{where}: {key} is not [x, y, z] or [x, y, z, yaw_deg]")
        for j, entry in enumerate(row.get("route", [])):
            e = entry if isinstance(entry, dict) else {"at": entry}
            if not _point(e.get("at")) or len(e["at"]) != 3:
                errs.append(f"{where}.route[{j}]: not a point [x, y, z]")
            if str(e.get("activity", "")) not in ACTIVITIES:
                errs.append(f"{where}.route[{j}]: unknown activity {e.get('activity')!r}")
        attach = str(row.get("attach", "beside"))
        if attach not in ATTACH:
            errs.append(f"{where}: attach {attach!r} is not one of {sorted(ATTACH)}")
        elif attach == "child" and (row.get("route") or row.get("follow")):
            errs.append(f"{where}: a villager inside its stand-in (attach child) has no route or follow")
        if len(row.get("route", [])) == 1:
            errs.append(f"{where}: a route needs two or more points")
    for vid, row in by_id.items():
        mate = str(row.get("chat_with", ""))
        if not mate:
            continue
        if mate not in by_id:
            errs.append(f"{rel}: {vid} chats with {mate!r}, not a villager here")
        elif str(by_id[mate].get("chat_with", "")) != vid:
            errs.append(f"{rel}: {vid} chats with {mate}, but {mate} does not chat back")
    return errs


def npc_errors(root: Path) -> list[str]:
    errs = tuning_errors(root)
    locations = _location_ids(root)
    flags = _declared_flags(root)
    zone_files = sorted((root / ZONES_DIR).glob("*.json")) if (root / ZONES_DIR).is_dir() else []
    for f in zone_files:
        errs += zone_errors(root, str(f.relative_to(root)), locations, flags)
    for stage in STAGE_FILES:
        if (root / stage).exists():
            errs += zone_errors(root, stage, locations, flags)
    return errs


def check_npc(root: Path, rep) -> None:
    for e in npc_errors(root):
        rep.err(e)


def main() -> int:
    errs = npc_errors(Path(__file__).resolve().parents[1])
    for e in errs:
        print(f"ERROR {e}")
    print(f"npc: {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
