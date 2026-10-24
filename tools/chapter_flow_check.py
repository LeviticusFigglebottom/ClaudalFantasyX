"""M3-ARC-01: checks the Act I chapter data (game/data/flow/chapters.json and the chapter files it
lists) and the greybox zone layouts they play in (docs/kb/tech/chapter_flow.md). Called from
tools/validate_data.py; `chapter_errors` and `layout_errors` are pure, so tests feed them fixtures."""
from __future__ import annotations

import json
import re
from pathlib import Path

CHAPTERS_FILE = "game/data/flow/chapters.json"
GREYBOX_SCRIPT = "res://game/world/zone/greybox_zone.gd"
LAYOUT_PATH_RE = re.compile(r'^layout_path = "(res://[^"]+)"', re.M)
ZONE_KEYS = {"party", "arrive", "beats", "barks", "overheard_hold_sec", "doc"}
END_STEPS = {"battle", "go", "scene"}
STEP_KEYS = {"play", "place", "set", "party", "zone", "beat", "if_event"} | END_STEPS
STEP_EXTRA = {"battle": {"return_spawn", "escape_spawn", "victory_flag", "party", "reserve", "seed"},
              "zone": {"args"}, "if_event": {"steps"}}
TRIGGER_KEYS = {"id", "at", "size", "yaw", "activation", "prompt_key", "payload", "requires_flag",
                "blocked_by_flag", "sets_flag", "once"}
ACTIVATIONS = {"touch", "interact"}


class Context:
    """What the chapter data may name. `layouts` maps a location id to its zone layout (None when
    the location's scene is not a greybox zone, so its spawns can't be checked here)."""

    def __init__(self, flags: set[str], dialogue: set[str], encounters: set[str], heroes: set[str],
                 locations: dict[str, str], layouts: dict[str, dict | None], scene_exists) -> None:
        self.flags = flags
        self.dialogue = dialogue
        self.encounters = encounters
        self.heroes = heroes
        self.locations = locations
        self.layouts = layouts
        self.scene_exists = scene_exists


def _when_errors(when: object, w: str, ctx: Context) -> list[str]:
    if when is None:
        return []
    if not isinstance(when, dict) or set(when) - {"set", "unset"}:
        return [f"{w}: when must be {{\"set\": [...], \"unset\": [...]}}"]
    errs = []
    for key in ("set", "unset"):
        for f in when.get(key, []):
            if f not in ctx.flags:
                errs.append(f"{w}: undeclared flag '{f}' (declare it in game/data/flags.tres)")
    return errs


def _party_errors(party: object, w: str, ctx: Context) -> list[str]:
    if not isinstance(party, dict):
        return [f"{w}: party must be {{\"party\": [...], \"reserve\": [...]}}"]
    errs = []
    for key in ("party", "reserve"):
        for h in party.get(key, []):
            if h not in ctx.heroes:
                errs.append(f"{w}: unknown hero '{h}'")
    return errs


def _spawn_errors(spawn: object, location: str, w: str, ctx: Context) -> list[str]:
    layout = ctx.layouts.get(location)
    if not isinstance(spawn, str) or not spawn:
        return [f"{w}: spawn must be a non-empty string"]
    if layout is not None and spawn not in layout.get("spawns", {}):
        return [f"{w}: {location} has no spawn '{spawn}'"]
    return []


def _step_errors(step: object, w: str, loc: str, zone: dict, ctx: Context) -> list[str]:
    if not isinstance(step, dict):
        return [f"{w}: a step must be an object"]
    kinds = [k for k in step if k in STEP_KEYS]
    if len(kinds) != 1:
        return [f"{w}: a step needs exactly one of {sorted(STEP_KEYS)}"]
    kind = kinds[0]
    errs = [f"{w}: unknown key '{k}' in a {kind} step" for k in set(step) - {kind} - STEP_EXTRA.get(kind, set())]
    v = step[kind]
    if kind == "play" and v not in ctx.dialogue:
        errs.append(f"{w}: no compiled dialogue '{v}' (game/data/dialogue/compiled)")
    elif kind == "place":
        errs += _spawn_errors(v, loc, w, ctx)
    elif kind == "set" and v not in ctx.flags:
        errs.append(f"{w}: undeclared flag '{v}'")
    elif kind == "party":
        errs += _party_errors(v, w, ctx)
    elif kind == "beat" and v not in zone.get("beats", {}):
        errs.append(f"{w}: no beat '{v}' in this zone")
    elif kind == "if_event":
        for i, s in enumerate(step.get("steps", [])):
            errs += _step_errors(s, f"{w}.steps[{i}]", loc, zone, ctx)
    elif kind == "battle":
        if v not in ctx.encounters:
            errs.append(f"{w}: unknown encounter '{v}'")
        for key in ("return_spawn", "escape_spawn"):
            if key in step:
                errs += _spawn_errors(step[key], loc, f"{w}.{key}", ctx)
        if step.get("victory_flag") and step["victory_flag"] not in ctx.flags:
            errs.append(f"{w}: undeclared victory_flag '{step['victory_flag']}'")
        if "party" in step:
            errs += _party_errors({"party": step["party"], "reserve": step.get("reserve", [])}, w, ctx)
    elif kind == "go":
        to = v if isinstance(v, dict) else {}
        target = to.get("location")
        if target not in ctx.locations:
            errs.append(f"{w}: unknown location '{target}' (locations.json)")
        else:
            errs += _spawn_errors(to.get("spawn"), target, w, ctx)
    elif kind == "scene" and not ctx.scene_exists(v):
        errs.append(f"{w}: no scene {v}")
    return errs


def _steps_errors(steps: object, w: str, loc: str, zone: dict, ctx: Context) -> list[str]:
    if not isinstance(steps, list) or not steps:
        return [f"{w}: steps must be a non-empty list"]
    errs = []
    for i, s in enumerate(steps):
        errs += _step_errors(s, f"{w}[{i}]", loc, zone, ctx)
        if isinstance(s, dict) and set(s) & END_STEPS and i != len(steps) - 1:
            errs.append(f"{w}[{i}]: a battle, go or scene step ends the run, so it must come last")
    return errs


def chapter_errors(doc: object, where: str, ctx: Context) -> list[str]:
    """A chapter file: every zone is a known location, and every step, flag, dialogue, encounter,
    hero and spawn it names exists. Trigger payloads in the zone's layout must name its beats."""
    if not isinstance(doc, dict) or not isinstance(doc.get("zones"), dict):
        return [f"{where}: needs a \"zones\" object keyed by location id"]
    errs = []
    for loc, zone in doc["zones"].items():
        w = f"{where}: zones.{loc}"
        if loc not in ctx.locations:
            errs.append(f"{w}: not a location in locations.json")
        if not isinstance(zone, dict):
            errs.append(f"{w}: must be an object")
            continue
        errs += [f"{w}: unknown key '{k}'" for k in set(zone) - ZONE_KEYS]
        if "party" in zone:
            errs += _party_errors(zone["party"], f"{w}.party", ctx)
        for i, row in enumerate(zone.get("arrive", [])):
            errs += _when_errors(row.get("when"), f"{w}.arrive[{i}]", ctx)
            errs += _steps_errors(row.get("steps"), f"{w}.arrive[{i}].steps", loc, zone, ctx)
        for bid, beat in zone.get("beats", {}).items():
            errs += _when_errors(beat.get("when"), f"{w}.beats.{bid}", ctx)
            errs += _steps_errors(beat.get("steps"), f"{w}.beats.{bid}.steps", loc, zone, ctx)
        for i, row in enumerate(zone.get("barks", [])):
            errs += _when_errors(row.get("when"), f"{w}.barks[{i}]", ctx)
            for a, b in (row.get("map", {}) or {}).items():
                errs += [f"{w}.barks[{i}]: no compiled dialogue '{d}'" for d in (a, b) if d not in ctx.dialogue]
        layout = ctx.layouts.get(loc)
        for t in (layout or {}).get("triggers", []):
            beat = (t.get("payload") or {}).get("beat")
            if beat is not None and beat not in zone.get("beats", {}):
                errs.append(f"{w}: its layout's trigger '{t.get('id')}' names no beat '{beat}'")
    return errs


def _nums(v: object, n: tuple[int, ...]) -> bool:
    return isinstance(v, list) and len(v) in n and all(isinstance(x, (int, float)) for x in v)


def layout_errors(layout: object, where: str, ctx: Context) -> list[str]:
    """A greybox zone layout: shapes of blocks, markers and triggers; trigger flags and dialogue."""
    if not isinstance(layout, dict):
        return [f"{where}: must be a JSON object"]
    errs = []
    for i, b in enumerate(layout.get("blocks", [])):
        if not (isinstance(b, dict) and _nums(b.get("pos"), (3,)) and _nums(b.get("size"), (3,))):
            errs.append(f"{where}: blocks[{i}] needs pos and size as [x, y, z]")
    for folder in ("spawns", "marks"):
        for k, v in (layout.get(folder) or {}).items():
            if not _nums(v, (3, 4)):
                errs.append(f"{where}: {folder}.{k} must be [x, y, z] or [x, y, z, yaw]")
    for k, a in (layout.get("actors") or {}).items():
        if not (isinstance(a, dict) and _nums(a.get("at"), (3, 4))):
            errs.append(f"{where}: actors.{k} needs \"at\": [x, y, z, yaw]")
    for k, s in (layout.get("shots") or {}).items():
        if not (isinstance(s, dict) and _nums(s.get("pos"), (3,)) and _nums(s.get("look_at"), (3,))):
            errs.append(f"{where}: shots.{k} needs pos and look_at as [x, y, z]")
    seen: set[str] = set()
    for i, t in enumerate(layout.get("triggers", [])):
        w = f"{where}: triggers[{i}]"
        if not isinstance(t, dict):
            errs.append(f"{w}: must be an object")
            continue
        errs += [f"{w}: unknown key '{k}'" for k in set(t) - TRIGGER_KEYS]
        tid = t.get("id")
        if not isinstance(tid, str) or not tid or tid in seen:
            errs.append(f"{w}: needs a unique non-empty id")
        seen.add(str(tid))
        if not (_nums(t.get("at"), (3,)) and _nums(t.get("size"), (3,))):
            errs.append(f"{w}: needs at and size as [x, y, z] (size y 0 = the default height)")
        if t.get("activation", "touch") not in ACTIVATIONS:
            errs.append(f"{w}: activation must be one of {sorted(ACTIVATIONS)}")
        for key in ("requires_flag", "blocked_by_flag", "sets_flag"):
            if t.get(key) and t[key] not in ctx.flags:
                errs.append(f"{w}: undeclared flag '{t[key]}'")
        dlg = (t.get("payload") or {}).get("dialogue")
        if dlg is not None and dlg not in ctx.dialogue:
            errs.append(f"{w}: no compiled dialogue '{dlg}'")
    return errs


def greybox_layout_path(scene_text: str) -> str | None:
    """The layout_path of a greybox zone scene (its root uses greybox_zone.gd), else None."""
    if GREYBOX_SCRIPT not in scene_text:
        return None
    m = LAYOUT_PATH_RE.search(scene_text)
    return m.group(1) if m else None


def _res(root: Path, res: str) -> Path:
    return root / res.removeprefix("res://")


def _load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def check(root: Path, files: dict[str, object], flags: set[str]) -> list[str]:
    """Every chapter file listed in chapters.json, and the layout of every zone they name."""
    reg = files.get(CHAPTERS_FILE)
    if reg is None:
        return []
    listed = (reg.get("chapters") or {}).get("files") if isinstance(reg, dict) else None
    if not isinstance(listed, list):
        return [f"{CHAPTERS_FILE}: needs chapters.files, a list of res:// paths"]
    locations: dict[str, str] = {}
    locs = files.get("game/data/world/locations.json")
    for row in (locs.get("locations", []) if isinstance(locs, dict) else []):
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            locations[row["id"]] = str(row.get("scene", ""))
    layouts: dict[str, dict | None] = {}
    errs: list[str] = []
    for lid, scene in locations.items():
        p = _res(root, scene)
        lp = greybox_layout_path(p.read_text(encoding="utf-8")) if p.is_file() else None
        layouts[lid] = None
        if lp is not None:
            layouts[lid] = _load(_res(root, lp)) if _res(root, lp).is_file() else {}
    enc = files.get("game/data/battle/encounters.json")
    chars = files.get("game/data/battle/characters.json")
    ctx = Context(
        flags=flags,
        dialogue={p.stem for p in (root / "game/data/dialogue/compiled").glob("*.json")},
        encounters={r.get("id") for r in (enc.get("encounters", []) if isinstance(enc, dict) else [])},
        heroes={r.get("id") for r in (chars.get("characters", []) if isinstance(chars, dict) else [])},
        locations=locations,
        layouts=layouts,
        scene_exists=lambda res: isinstance(res, str) and _res(root, res).is_file(),
    )
    named: set[str] = set()
    for f in listed:
        rel = str(f).removeprefix("res://")
        doc = files.get(rel) if rel in files else _load(root / rel)
        if doc is None:
            errs.append(f"{CHAPTERS_FILE}: no chapter file {f}")
            continue
        errs += chapter_errors(doc, rel, ctx)
        named |= set((doc.get("zones") or {}) if isinstance(doc, dict) else ())
    for lid in sorted(named):
        if ctx.layouts.get(lid) is not None:
            errs += layout_errors(ctx.layouts[lid], f"layout of {lid}", ctx)
    return errs
