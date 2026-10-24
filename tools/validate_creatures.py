"""Battle creature data checks (M2-CRE-03), called by tools/validate_data.py.

- game/data/creatures/creatures.json: the defaults row and one row per creature actor (CreatureActor reads it):
  its `scene` exists under game/creatures/, keys and value types are known, `clip_by_skill` and `break_parts`
  name real skills, `phases` name a phase some enemy has.
- game/data/battle/enemies.json: an enemy's optional `model` is a res://game/creatures/...tscn that exists and that
  a creatures.json row names as its `scene`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

CREATURES_FILE = "game/data/creatures/creatures.json"
ENEMIES_FILE = "game/data/battle/enemies.json"
SKILLS_FILE = "game/data/battle/skills.json"
SCENE_PREFIX = "res://game/creatures/"

DEFAULT_KEYS = {"idle", "hit", "ko", "loop", "blend_sec", "clip_by_kind", "clip_by_skill", "ko_fade_sec",
                "stand_in", "phases", "break_parts"}
ROW_KEYS = DEFAULT_KEYS | {"scene"}
STAND_IN_KEYS = {"yaw_deg"}
PHASE_KEYS = {"clip", "idle", "offset_m", "tilt_deg", "sec"}
PART_KEYS = {"whole", "broken"}


def _num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _row_errors(w: str, row: dict, skills: set[str], phase_ids: set[str]) -> list[str]:
    errs: list[str] = []
    for k in ("idle", "hit", "ko"):
        if k in row and not (isinstance(row[k], str) and row[k]):
            errs.append(f"{w}.{k}: must be a clip name")
    if "loop" in row and not (isinstance(row["loop"], list) and all(isinstance(c, str) and c for c in row["loop"])):
        errs.append(f"{w}.loop: must be a list of clip names")
    for k in ("blend_sec", "ko_fade_sec"):
        if k in row and not (_num(row[k]) and row[k] >= 0):
            errs.append(f"{w}.{k}: must be a number >= 0")
    for k in ("clip_by_kind", "clip_by_skill"):
        m = row.get(k, {})
        if not isinstance(m, dict) or not all(isinstance(v, str) and v for v in m.values()):
            errs.append(f"{w}.{k}: must map names to clip names")
    for sid in row.get("clip_by_skill", {}) if isinstance(row.get("clip_by_skill"), dict) else []:
        if sid not in skills:
            errs.append(f"{w}.clip_by_skill: unknown skill '{sid}'")
    st = row.get("stand_in", {})
    if not isinstance(st, dict):
        errs.append(f"{w}.stand_in: must be an object")
    else:
        errs += [f"{w}.stand_in: unknown key '{k}'" for k in sorted(set(st) - STAND_IN_KEYS)]
        if "yaw_deg" in st and not _num(st["yaw_deg"]):
            errs.append(f"{w}.stand_in.yaw_deg: must be a number")
    phases = row.get("phases", {})
    if not isinstance(phases, dict):
        errs.append(f"{w}.phases: must be an object")
        phases = {}
    for pid, p in phases.items():
        pw = f"{w}.phases.{pid}"
        if pid not in phase_ids:
            errs.append(f"{pw}: no enemy has a phase '{pid}'")
        if not isinstance(p, dict):
            errs.append(f"{pw}: must be an object")
            continue
        errs += [f"{pw}: unknown key '{k}'" for k in sorted(set(p) - PHASE_KEYS)]
        for k in ("clip", "idle"):
            if k in p and not (isinstance(p[k], str) and p[k]):
                errs.append(f"{pw}.{k}: must be a clip name")
        for k in ("offset_m", "tilt_deg"):
            if k in p and not (isinstance(p[k], list) and len(p[k]) == 3 and all(_num(x) for x in p[k])):
                errs.append(f"{pw}.{k}: must be [x, y, z]")
        if "sec" in p and not (_num(p["sec"]) and p["sec"] >= 0):
            errs.append(f"{pw}.sec: must be a number >= 0")
    parts = row.get("break_parts", {})
    if not isinstance(parts, dict):
        errs.append(f"{w}.break_parts: must be an object")
        parts = {}
    for sid, part in parts.items():
        pw = f"{w}.break_parts.{sid}"
        if sid not in skills:
            errs.append(f"{pw}: unknown skill '{sid}'")
        if not isinstance(part, dict) or set(part) - PART_KEYS:
            errs.append(f"{pw}: must be an object with 'whole' and 'broken' node-name lists")
            continue
        for k in PART_KEYS:
            if not (isinstance(part.get(k), list) and part[k] and all(isinstance(n, str) and n for n in part[k])):
                errs.append(f"{pw}.{k}: must be a non-empty list of node names")
    return errs


def creature_errors(creatures: object, enemies: object, skills: object, scene_exists: Callable[[str], bool]) -> list[str]:
    """Errors for creatures.json and enemies.json `model`. `scene_exists(res_path) -> bool`."""
    w0 = CREATURES_FILE
    if not isinstance(creatures, dict):
        return [f"{w0}: must be an object"]
    skill_ids = {s.get("id") for s in (skills or {}).get("skills", []) if isinstance(s, dict)} \
        if isinstance(skills, dict) else set()
    enemy_rows = [e for e in (enemies or {}).get("enemies", []) if isinstance(e, dict)] \
        if isinstance(enemies, dict) else []
    phase_ids = {p.get("id") for e in enemy_rows for p in e.get("phases", []) if isinstance(p, dict)}
    errs: list[str] = []
    defaults = creatures.get("defaults")
    if not isinstance(defaults, dict):
        errs.append(f"{w0}.defaults: must be an object")
        defaults = {}
    else:
        missing = sorted(DEFAULT_KEYS - set(defaults))
        if missing:
            errs.append(f"{w0}.defaults: missing {', '.join(missing)}")
        errs += [f"{w0}.defaults: unknown key '{k}'" for k in sorted(set(defaults) - DEFAULT_KEYS)]
        errs += _row_errors(f"{w0}.defaults", defaults, skill_ids, phase_ids)
    rows = creatures.get("creatures")
    if not isinstance(rows, dict):
        return errs + [f"{w0}.creatures: must be an object"]
    scenes: dict[str, str] = {}
    for cid, row in rows.items():
        w = f"{w0}.creatures.{cid}"
        if not isinstance(row, dict):
            errs.append(f"{w}: must be an object")
            continue
        errs += [f"{w}: unknown key '{k}'" for k in sorted(set(row) - ROW_KEYS)]
        scene = row.get("scene")
        if not (isinstance(scene, str) and scene.startswith(SCENE_PREFIX) and scene.endswith(".tscn")):
            errs.append(f"{w}.scene: must be a {SCENE_PREFIX}...tscn path")
        else:
            if scene in scenes:
                errs.append(f"{w}.scene: {scene} is also {scenes[scene]}'s")
            scenes[scene] = cid
            if not scene_exists(scene):
                errs.append(f"{w}.scene: {scene} does not exist")
        errs += _row_errors(w, row, skill_ids, phase_ids)
    for e in enemy_rows:
        if "model" not in e:
            continue
        w = f"enemies.{e.get('id')}.model"
        m = e["model"]
        if not (isinstance(m, str) and m.startswith(SCENE_PREFIX) and m.endswith(".tscn")):
            errs.append(f"{w}: must be a {SCENE_PREFIX}...tscn path")
            continue
        if not scene_exists(m):
            errs.append(f"{w}: {m} does not exist")
        if m not in scenes:
            errs.append(f"{w}: no {CREATURES_FILE} row names {m} as its scene")
    return errs


def check_creatures(root: Path, files: dict[str, object], rep) -> None:
    def exists(res: str) -> bool:
        return (root / res[len("res://"):]).is_file()

    if CREATURES_FILE not in files:
        rep.err(f"{CREATURES_FILE}: missing")
        return
    for e in creature_errors(files[CREATURES_FILE], files.get(ENEMIES_FILE), files.get(SKILLS_FILE), exists):
        rep.err(e)
