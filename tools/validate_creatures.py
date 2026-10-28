"""Battle creature data checks (M2-CRE-03), called by tools/validate_data.py.

- game/data/creatures/creatures.json: the defaults row and one row per creature actor (CreatureActor reads it):
  its `scene` exists under game/creatures/, keys and value types are known, `clip_by_skill` and `break_parts`
  name real skills, `phases` name a phase some enemy has.
- game/data/battle/enemies.json: an enemy's optional `model` is a res://game/creatures/...tscn that exists and that
  a creatures.json row names as its `scene`.
- A row with `vowbound` true (M3-CRE-638) is a Vowbound's actor: its id is a game/data/battle/vowbound.json row (the
  stand-in CreatureModels gives that Vowbound), and no enemy uses its scene as a `model`.
- `vfx_anchors` (M3-CRE-651): {"core": bone, "wound": bone} where spawn and death effects start (CreatureActor
  .vfx_anchor); a non-empty map needs a core. tools/tests/test_creatures.py checks the bones are in the GLB.
- `stand_in` may also carry `height` and `radius` (M3-CRE-640, numbers > 0): a Vowbound with no battle_sandbox.json
  stand-in row (UI's) gives its own, so the VFX anchors and the ring fit the model.
- `vowbound_pending` (M3-CRE-642): a Vowbound built ahead of its game row names, as a non-empty string, the task
  that adds its vowbound.json row (Combat's file). While it is set the missing row is allowed; once the row exists it
  is an error, so the key is dropped with the row's arrival. Only on a `vowbound` true row.
- A phase may carry `hold` (M3-CRE-647, true or false, with a `clip`): the actor stays on the clip's last frame instead
  of idling (a Vowbound's release, on its `<id>_held` foe row).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

CREATURES_FILE = "game/data/creatures/creatures.json"
ENEMIES_FILE = "game/data/battle/enemies.json"
SKILLS_FILE = "game/data/battle/skills.json"
VOWBOUND_FILE = "game/data/battle/vowbound.json"
SCENE_PREFIX = "res://game/creatures/"

DEFAULT_KEYS = {"idle", "hit", "ko", "loop", "blend_sec", "clip_by_kind", "clip_by_skill", "ko_fade_sec",
                "stand_in", "phases", "break_parts", "portrait", "contact", "hit_variants", "idle_variety",
                "hit_snap"}
ROW_KEYS = DEFAULT_KEYS | {"scene", "vowbound", "vowbound_pending", "vfx_anchors"}
VFX_ANCHOR_KEYS = {"wound", "core"}
STAND_IN_KEYS = {"yaw_deg", "hover", "height", "radius"}
PHASE_KEYS = {"clip", "idle", "offset_m", "tilt_deg", "sec", "show", "hide", "hide_after", "show_after", "clips",
              "hold"}
PART_KEYS = {"whole", "broken"}
HIT_SNAP_KEYS = {"preroll_sec", "blend_sec", "_note"}
PORTRAIT_KEYS = {"clip", "clip_time", "yaw_deg", "pitch_deg", "fov_deg", "margin", "key_energy", "rim_energy",
                 "rim_side_deg", "rim_elev_deg", "kick_energy", "kick_elev_deg"}
IDLE_VARIETY_KEYS = {"clip", "every_sec"}


def _num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _row_errors(w: str, row: dict, skills: set[str], phase_ids: set[str] | None) -> list[str]:
    """`phase_ids` None skips the phase-name check (a creature no enemy uses yet: its enemy row and phases come
    later, from the encounter designers)."""
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
    va = row.get("vfx_anchors", {})
    if not (isinstance(va, dict) and all(isinstance(v, str) and v for v in va.values())):
        errs.append(f"{w}.vfx_anchors: must map anchor names to bone names")
    else:
        errs += [f"{w}.vfx_anchors: unknown anchor '{k}'" for k in sorted(set(va) - VFX_ANCHOR_KEYS)]
        if va and "core" not in va:
            errs.append(f"{w}.vfx_anchors: needs a core (a wound falls back to it)")
    st = row.get("stand_in", {})
    if not isinstance(st, dict):
        errs.append(f"{w}.stand_in: must be an object")
    else:
        errs += [f"{w}.stand_in: unknown key '{k}'" for k in sorted(set(st) - STAND_IN_KEYS)]
        if "yaw_deg" in st and not _num(st["yaw_deg"]):
            errs.append(f"{w}.stand_in.yaw_deg: must be a number")
        for k in ("height", "radius"):
            if k in st and not (_num(st[k]) and st[k] > 0):
                errs.append(f"{w}.stand_in.{k}: must be a number > 0")
    con = row.get("contact", {})
    if not (isinstance(con, dict) and all(isinstance(k, str) and _num(v) and v >= 0 for k, v in con.items())):
        errs.append(f"{w}.contact: must map clip names to seconds >= 0")
    por = row.get("portrait", {})
    if not isinstance(por, dict):
        errs.append(f"{w}.portrait: must be an object")
    else:
        errs += [f"{w}.portrait: unknown key '{k}'" for k in sorted(set(por) - PORTRAIT_KEYS)]
        if "clip" in por and not (isinstance(por["clip"], str) and por["clip"]):
            errs.append(f"{w}.portrait.clip: must be a clip name")
        for k in sorted(PORTRAIT_KEYS - {"clip"}):
            if k in por and not _num(por[k]):
                errs.append(f"{w}.portrait.{k}: must be a number")
        if _num(por.get("fov_deg")) and not 1.0 <= por["fov_deg"] <= 120.0:
            errs.append(f"{w}.portrait.fov_deg: must be 1..120")
    hv = row.get("hit_variants", [])
    if not (isinstance(hv, list) and all(isinstance(c, str) and c for c in hv)):
        errs.append(f"{w}.hit_variants: must be a list of clip names")
    iv = row.get("idle_variety", {})
    if not isinstance(iv, dict):
        errs.append(f"{w}.idle_variety: must be an object")
    else:
        errs += [f"{w}.idle_variety: unknown key '{k}'" for k in sorted(set(iv) - IDLE_VARIETY_KEYS)]
        if "clip" in iv and not (isinstance(iv["clip"], str) and iv["clip"]):
            errs.append(f"{w}.idle_variety.clip: must be a clip name")
        ev = iv.get("every_sec", [1.0, 1.0])
        if not (isinstance(ev, list) and len(ev) == 2 and all(_num(x) for x in ev) and 0 < ev[0] <= ev[1]):
            errs.append(f"{w}.idle_variety.every_sec: must be [min, max] seconds, 0 < min <= max")
    hs = row.get("hit_snap", {})
    if not isinstance(hs, dict):
        errs.append(f"{w}.hit_snap: must be an object")
    else:
        errs += [f"{w}.hit_snap: unknown key '{k}'" for k in sorted(set(hs) - HIT_SNAP_KEYS)]
        for k in ("preroll_sec", "blend_sec"):
            if k in hs and not (_num(hs[k]) and 0 <= hs[k] <= 1.0):
                errs.append(f"{w}.hit_snap.{k}: must be 0..1 seconds")
    phases = row.get("phases", {})
    if not isinstance(phases, dict):
        errs.append(f"{w}.phases: must be an object")
        phases = {}
    for pid, p in phases.items():
        pw = f"{w}.phases.{pid}"
        if phase_ids is not None and pid not in phase_ids:
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
        for k in ("show", "hide", "hide_after", "show_after"):
            if k in p and not (isinstance(p[k], list) and all(isinstance(n, str) and n for n in p[k])):
                errs.append(f"{pw}.{k}: must be a list of node names")
        if "clips" in p and not (isinstance(p["clips"], dict)
                                 and all(isinstance(a, str) and a and isinstance(b, str) and b for a, b in p["clips"].items())):
            errs.append(f"{pw}.clips: must map clip names to clip names")
        if "hold" in p and not isinstance(p["hold"], bool):
            errs.append(f"{pw}.hold: must be true or false")
        elif p.get("hold") and "clip" not in p:
            errs.append(f"{pw}.hold: holds the phase's clip, so it needs a `clip`")
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


def creature_errors(creatures: object, enemies: object, skills: object, scene_exists: Callable[[str], bool],
                    vowbound: object = None) -> list[str]:
    """Errors for creatures.json and enemies.json `model`. `scene_exists(res_path) -> bool`. `vowbound` is
    vowbound.json (None: a `vowbound` row's id is not checked against it)."""
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
        used = isinstance(scene, str) and any(e.get("model") == scene for e in enemy_rows)
        errs += _row_errors(w, row, skill_ids, phase_ids if used else None)
        if "vowbound" in row:
            errs += _vowbound_errors(w, cid, row["vowbound"], used, vowbound, row.get("vowbound_pending"))
        elif "vowbound_pending" in row:
            errs.append(f"{w}.vowbound_pending: only on a row with vowbound true")
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


def _vowbound_errors(w: str, cid: str, flag: object, used: bool, vowbound: object, pending: object = None) -> list[str]:
    if not isinstance(flag, bool):
        return [f"{w}.vowbound: must be true or false"]
    errs: list[str] = []
    if pending is not None and not (isinstance(pending, str) and pending.strip()):
        errs.append(f"{w}.vowbound_pending: must name the task that adds the {VOWBOUND_FILE} row")
    if not flag:
        if pending is not None:
            errs.append(f"{w}.vowbound_pending: only on a row with vowbound true")
        return errs
    if used:
        errs.append(f"{w}.vowbound: a Vowbound's scene may not be an enemy's model")
    if vowbound is not None:
        rows = vowbound.get("vowbound", []) if isinstance(vowbound, dict) else []
        has_row = cid in {v.get("id") for v in rows if isinstance(v, dict)}
        if not has_row and pending is None:
            errs.append(f"{w}.vowbound: no {VOWBOUND_FILE} row '{cid}'")
        elif has_row and pending is not None:
            errs.append(f"{w}.vowbound_pending: {VOWBOUND_FILE} has the row '{cid}' now; drop the key")
    return errs


def check_creatures(root: Path, files: dict[str, object], rep) -> None:
    def exists(res: str) -> bool:
        return (root / res[len("res://"):]).is_file()

    if CREATURES_FILE not in files:
        rep.err(f"{CREATURES_FILE}: missing")
        return
    for e in creature_errors(files[CREATURES_FILE], files.get(ENEMIES_FILE), files.get(SKILLS_FILE), exists,
                             files.get(VOWBOUND_FILE)):
        rep.err(e)
