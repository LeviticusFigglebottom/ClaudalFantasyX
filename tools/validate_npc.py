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
* Crowd rows (M3-CRE-659, ADR 0152): a row's `crowd` names a person in game/data/world/npc/crowd.json who stands
  in this zone at this stage actor (stand_in CutsceneStage/Actors/<stage_actor>, attach child); their body's actor
  scene exists; `offset` is [x, y, z] or [x, y, z, yaw_deg], inside the stand-in only.
* game/data/world/npc/crowd.json: ids unique; each person's zone is a location, their body a planned body with an
  actor scene whose age band and sex are theirs, their work a crowd work clip (or none), their tints exactly
  cloth_a, cloth_b, cloth_c and hair, each a palette.json swatch or a two-swatch mix of the cloth, earth, stone,
  accent, material, vegetation and hair families; every person has exactly one row in their zone's file. Variety:
  no body twice in one zone, and two people anywhere on one body dress at least VARIETY_MIN apart.
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
CROWD_FILE = "game/data/world/npc/crowd.json"
CROWD_ACTOR = "assets/crowd/{id}/{id}_actor.tscn"
STAGE_ACTORS = "CutsceneStage/Actors/"
PALETTE_FILE = "docs/kb/art/palette.json"
TINT_SLOTS = {"cloth_a", "cloth_b", "cloth_c", "hair"}
CLOTH_SLOTS = ("cloth_a", "cloth_b", "cloth_c")
TINT_FAMILIES = {"cloth", "earth", "stone", "accent", "material", "vegetation", "hair"}
TINT_TOLERANCE = 1.5  # sRGB 0-255 units off the nearest two-swatch mix (hex rounding)
VARIETY_MIN = 24.0  # sRGB 0-255 distance: two people on one body differ by at least this in some cloth slot
PERSON_KEYS = ("id", "zone", "stage_actor", "role", "community", "age_band", "sex", "build", "body", "tints", "work")
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


def crowd_people(root: Path) -> dict[str, dict]:
    """crowd.json's people by id ({} without the file)."""
    if not (root / CROWD_FILE).exists():
        return {}
    data = _load(root / CROWD_FILE, [])
    return {str(p.get("id")): p for p in data.get("people", []) if isinstance(p, dict)}


def _crowd_row_errors(root: Path, where: str, zone: str, row: dict, people: dict[str, dict]) -> list[str]:
    errs: list[str] = []
    pid = str(row.get("crowd", ""))
    person = people.get(pid)
    if person is None:
        return [f"{where}: crowd {pid!r} is not a person in {CROWD_FILE}"]
    if str(person.get("zone")) != zone:
        errs.append(f"{where}: crowd {pid!r} stands in {person.get('zone')!r}, not {zone!r}")
    if str(row.get("stand_in", "")) != STAGE_ACTORS + str(person.get("stage_actor", "")):
        errs.append(f"{where}: crowd {pid!r} stands at stage actor {person.get('stage_actor')!r}, "
                    f"not {row.get('stand_in')!r}")
    body = str(person.get("body", ""))
    if not (root / CROWD_ACTOR.format(id=body)).exists():
        errs.append(f"{where}: crowd {pid!r} wears body {body!r}, which has no actor scene")
    return errs


def zone_errors(root: Path, rel: str, locations: set[str], flags: set[str],
                people: dict[str, dict] | None = None) -> list[str]:
    errs: list[str] = []
    path = root / rel
    data = _load(path, errs)
    if not data:
        return errs
    if people is None:
        people = crowd_people(root)
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
        if "crowd" in row:
            errs += _crowd_row_errors(root, where, zone, row, people)
        else:
            actor = str(row.get("actor", vid))
            if not (root / ACTOR.format(id=actor)).exists():
                errs.append(f"{where}: npc_id {vid!r} has no actor scene" if actor == vid
                            else f"{where}: actor {actor!r} (worn by {vid!r}) has no actor scene")
        if "offset" in row:
            if not _point(row["offset"]):
                errs.append(f"{where}: offset is not [x, y, z] or [x, y, z, yaw_deg]")
            elif str(row.get("attach", "beside")) != "child":
                errs.append(f"{where}: an offset places a villager inside its stand-in (attach child) only")
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


def _rgb(hex_: str) -> tuple[float, float, float] | None:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(hex_)):
        return None
    return tuple(float(int(hex_[i:i + 2], 16)) for i in (1, 3, 5))  # type: ignore[return-value]


def tint_swatches(root: Path) -> list[tuple[float, float, float]]:
    """The palette.json swatches a tint may be (or mix two of)."""
    data = _load(root / PALETTE_FILE, [])
    out = []
    for s in data.get("swatches", {}).values():
        if isinstance(s, dict) and s.get("family") in TINT_FAMILIES and _rgb(str(s.get("hex"))):
            out.append(_rgb(str(s["hex"])))
    return out


def mix_distance(c: tuple, swatches: list[tuple]) -> float:
    """How far `c` lies (sRGB units) from the nearest swatch or straight mix of two swatches."""
    best = float("inf")
    for i, a in enumerate(swatches):
        for b in swatches[i:]:
            ab = [b[k] - a[k] for k in range(3)]
            ac = [c[k] - a[k] for k in range(3)]
            n = sum(x * x for x in ab)
            t = 0.0 if n == 0.0 else min(1.0, max(0.0, sum(ab[k] * ac[k] for k in range(3)) / n))
            d = sum((ac[k] - t * ab[k]) ** 2 for k in range(3)) ** 0.5
            best = min(best, d)
    return best


def tint_distance(a: dict, b: dict) -> float:
    """The largest sRGB distance over the cloth slots: how far apart two people on one body dress."""
    out = 0.0
    for s in CLOTH_SLOTS:
        ca, cb = _rgb(str(a.get(s, ""))), _rgb(str(b.get(s, "")))
        if ca and cb:
            out = max(out, sum((ca[k] - cb[k]) ** 2 for k in range(3)) ** 0.5)
    return out


def variety_errors(people: list[dict]) -> list[str]:
    """No body twice in one zone; people on one body anywhere dress at least VARIETY_MIN apart."""
    errs: list[str] = []
    seen: dict[tuple[str, str], str] = {}
    by_body: dict[str, list[dict]] = {}
    for p in people:
        key = (str(p.get("zone")), str(p.get("body")))
        if key in seen:
            errs.append(f"{CROWD_FILE}: {p.get('id')} and {seen[key]} both wear {key[1]} in {key[0]}")
        seen[key] = str(p.get("id"))
        for q in by_body.get(key[1], []):
            d = tint_distance(p.get("tints", {}), q.get("tints", {}))
            if d < VARIETY_MIN:
                errs.append(f"{CROWD_FILE}: {p.get('id')} and {q.get('id')} wear {key[1]} in near-identical tints "
                            f"({d:.0f} < {VARIETY_MIN:.0f})")
        by_body.setdefault(key[1], []).append(p)
    return errs


def crowd_errors(root: Path, locations: set[str]) -> list[str]:
    if not (root / CROWD_FILE).exists():
        return []
    errs: list[str] = []
    data = _load(root / CROWD_FILE, errs)
    bodies = data.get("bodies", {})
    works = set(data.get("work_tuning", {})) - {"doc"}
    swatches = tint_swatches(root)
    people = [p for p in data.get("people", []) if isinstance(p, dict)]
    ids: set[str] = set()
    for p in people:
        pid = str(p.get("id", ""))
        where = f"{CROWD_FILE}: {pid or '<no id>'}"
        missing = [k for k in PERSON_KEYS if k not in p]
        if missing:
            errs.append(f"{where}: lacks {', '.join(missing)}")
            continue
        if pid in ids:
            errs.append(f"{where}: id appears twice")
        ids.add(pid)
        if p["zone"] not in locations:
            errs.append(f"{where}: zone {p['zone']!r} is not a location")
        plan = bodies.get(p["body"])
        if plan is None:
            errs.append(f"{where}: body {p['body']!r} is not planned in `bodies`")
        else:
            for k in ("age_band", "sex"):
                if plan.get(k) != p[k]:
                    errs.append(f"{where}: {k} {p[k]!r} but body {p['body']} is {plan.get(k)!r}")
            if not (root / CROWD_ACTOR.format(id=p["body"])).exists():
                errs.append(f"{where}: body {p['body']!r} has no actor scene")
        if p["work"] and p["work"] not in works:
            errs.append(f"{where}: work {p['work']!r} is not a crowd work clip ({sorted(works)})")
        tints = p["tints"] if isinstance(p["tints"], dict) else {}
        if set(tints) != TINT_SLOTS:
            errs.append(f"{where}: tints must be exactly {sorted(TINT_SLOTS)}")
        for slot, hex_ in sorted(tints.items()):
            c = _rgb(str(hex_))
            if c is None:
                errs.append(f"{where}: tints.{slot} {hex_!r} is not #RRGGBB")
            elif swatches and mix_distance(c, swatches) > TINT_TOLERANCE:
                errs.append(f"{where}: tints.{slot} {hex_} is not a palette swatch or a mix of two")
    rows: dict[str, int] = {}
    zone_files = sorted((root / ZONES_DIR).glob("*.json")) if (root / ZONES_DIR).is_dir() else []
    for f in zone_files:
        for r in _load(f, []).get("villagers", []):
            if isinstance(r, dict) and "crowd" in r:
                rows[str(r["crowd"])] = rows.get(str(r["crowd"]), 0) + 1
    for pid in sorted(ids):
        if rows.get(pid, 0) != 1:
            errs.append(f"{CROWD_FILE}: {pid} has {rows.get(pid, 0)} zone rows (needs exactly 1)")
    return errs + variety_errors(people)


def npc_errors(root: Path) -> list[str]:
    errs = tuning_errors(root)
    locations = _location_ids(root)
    flags = _declared_flags(root)
    errs += crowd_errors(root, locations)
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
