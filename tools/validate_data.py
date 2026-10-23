#!/usr/bin/env python3
"""Project data validator (SPEC §5.5). Exit code 1 on any error.

Checks:
  * every JSON file under game/data parses
  * battle tables: schema, unique ids, enums, dangling references
  * progression: facets.json rules/facet types, and every lattice_*.json board (dangling edges,
    unreachable nodes from each start, unknown skills, stat names, gate levels, coordinates)
  * localization: every *_key / tr("KEY") / dialogue #line: key exists in a loc CSV
  * story flags: every flag used in .gd / .dlg is declared in game/data/flags.tres
  * dialogue: .dlg files compile (tools/dlgc.py), committed outputs are fresh, emotion tags, cues and
    events come from game/data/dialogue/{emotions,cues,events}.json (long lines are warnings),
    and those tables plus speakers.json and text_box.json are well-formed
  * provenance: every file under assets/ has a row in assets/PROVENANCE.md
  * banned terms (tools/banned_terms.txt) in game/, assets_src/, story docs, glossary
  * binary size limit while Git LFS is deferred (ADR 0005)
  * items (game/data/items): schema, dangling refs (abilities, recipe and shop items, characters,
    Facets), at most 4 ability slots, positive prices, declared stock flags (M1-PRG-02)

Usage: python3 tools/validate_data.py [--root PATH]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dlgc  # noqa: E402

ELEMENTS = {"none", "fire", "water", "lightning", "ice", "holy", "glimmer"}
AFFINITIES = {"normal", "weak", "resist", "immune", "absorb"}
SKILL_KINDS = {"physical", "magical", "heal", "support"}
SKILL_TARGETS = {"single_foe", "all_foes", "single_ally", "all_allies", "self"}
AI_TARGETS = {"random_foe", "lowest_hp_foe", "highest_hp_foe", "self", "random_ally", "all_foes", "all_allies"}
AI_CONDITIONS = {"self_hp_below_pct", "turn_mod", "foe_has_status", "allies_alive_below"}
STAT_KEYS = {"level", "hp", "mp", "strength", "magic", "defense", "magic_defense",
             "agility", "accuracy", "evasion", "luck"}
CANON_STATUSES = {"poison", "sleep", "silence", "darkness", "petrify", "slow", "haste", "stop",
                  "berserk", "confuse", "doom", "zombie", "shell", "protect", "reflect", "regen",
                  "armor_break", "mental_break", "power_break", "magic_break", "provoke"}
NO_PERMANENT_STATUSES = {"stop", "sleep"}  # -1 duration could stall every combatant
ONLY_PERMANENT_STATUSES = {"petrify"}  # stone never takes a turn, so a countdown never ticks
COUNTDOWN_STATUSES = {"doom"}  # a -1 countdown would never fall


LATTICE_STATS = STAT_KEYS - {"level"}
LATTICE_NODE_TYPES = {"start", "stat", "ability", "gate", "empty"}
LATTICE_NODE_FIELDS = {"start": {"character"}, "stat": {"stat", "value"}, "ability": {"skill"},
                       "gate": {"gate_level"}, "empty": set()}
LATTICE_COMMON_FIELDS = {"id", "type", "x", "y", "region"}
FACET_TYPES = {"power": "stat", "mind": "stat", "speed": "stat", "fortune": "stat",
               "ability": "ability", "key": "gate"}
FACET_RULE_KEYS = {"move_cost", "move_cost_activated", "facets_per_activation", "keys_per_gate",
                   "max_gate_level"}
FACETS_FILE = "game/data/progression/facets.json"
LATTICE_DIR = "game/data/progression"
LATTICE_GLOB = "lattice_*.json"
MAX_BINARY_BYTES = 5 * 1024 * 1024
BINARY_EXT = {".png", ".jpg", ".exr", ".wav", ".ogg", ".glb", ".blend", ".ttf", ".otf", ".webp"}
BANNED_SCAN = ["game", "assets_src", "docs/kb/story", "docs/kb/glossary.md"]
BANNED_SCAN_EXT = {".gd", ".json", ".tres", ".tscn", ".csv", ".md", ".dlg", ".py", ".txt", ".gdshader"}

GD_FLAG_RE = re.compile(r'\b(?:get_flag|set_flag)\(\s*&?"([A-Za-z0-9_]+)"')
DLG_FLAG_RE = re.compile(r"\$([a-z][a-z0-9_]*)")
GD_TR_RE = re.compile(r'\btr\(\s*"([A-Z0-9_]+)"')
DLG_LINE_RE = re.compile(r"#line:([a-z0-9_]+)")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_json_files(root: Path, rep: Report) -> dict[str, object]:
    out: dict[str, object] = {}
    for p in sorted((root / "game" / "data").rglob("*.json")):
        try:
            out[p.relative_to(root).as_posix()] = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            rep.err(f"{p.relative_to(root)}: invalid JSON: {e}")
    return out


def _table(files: dict[str, object], name: str, rep: Report) -> list[dict]:
    key = f"game/data/battle/{name}.json"
    data = files.get(key)
    if not isinstance(data, dict) or not isinstance(data.get(name), list):
        rep.err(f"{key}: missing top-level list '{name}'")
        return []
    rows = data[name]
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            rep.err(f"{key}[{i}]: row needs a string 'id'")
            continue
        if row["id"] in seen:
            rep.err(f"{key}: duplicate id '{row['id']}'")
        seen.add(row["id"])
    return [r for r in rows if isinstance(r, dict) and isinstance(r.get("id"), str)]


def _check_stats(where: str, stats: object, rep: Report) -> None:
    if not isinstance(stats, dict):
        rep.err(f"{where}: 'stats' must be an object")
        return
    missing = STAT_KEYS - stats.keys()
    if missing:
        rep.err(f"{where}: stats missing {sorted(missing)}")
    for k, v in stats.items():
        if k not in STAT_KEYS:
            rep.err(f"{where}: unknown stat '{k}'")
        elif not isinstance(v, int) or v < 0:
            rep.err(f"{where}: stat '{k}' must be a non-negative int")


def check_battle(files: dict[str, object], rep: Report) -> list[str]:
    """Validates battle tables. Returns every *_key value found (for loc checks)."""
    keys: list[str] = []
    skills = _table(files, "skills", rep)
    statuses = _table(files, "statuses", rep)
    characters = _table(files, "characters", rep)
    enemies = _table(files, "enemies", rep)
    encounters = _table(files, "encounters", rep)
    skill_ids = {s["id"] for s in skills}
    status_ids = {s["id"] for s in statuses}
    char_ids = {c["id"] for c in characters}
    enemy_ids = {e["id"] for e in enemies}
    item_ids = _ids(files, "game/data/items/items.json", "items")

    if status_ids != CANON_STATUSES:
        rep.err(f"statuses.json must declare exactly the SPEC §6.8 set; "
                f"missing {sorted(CANON_STATUSES - status_ids)}, extra {sorted(status_ids - CANON_STATUSES)}")

    for rows in (skills, statuses, characters, enemies, encounters):
        for r in rows:
            for k, v in r.items():
                if k.endswith("_key") and isinstance(v, str):
                    keys.append(v)

    for s in skills:
        w = f"skills.{s['id']}"
        if s.get("kind") not in SKILL_KINDS:
            rep.err(f"{w}: kind must be one of {sorted(SKILL_KINDS)}")
        if s.get("target") not in SKILL_TARGETS:
            rep.err(f"{w}: target must be one of {sorted(SKILL_TARGETS)}")
        if s.get("element", "none") not in ELEMENTS:
            rep.err(f"{w}: unknown element '{s.get('element')}'")
        rank = s.get("rank")
        if not isinstance(rank, int) or not 1 <= rank <= 8:
            rep.err(f"{w}: rank must be an int in 1..8")
        for key in ("power", "mp_cost", "accuracy", "delay_ranks"):
            if key in s and (not isinstance(s[key], int) or s[key] < 0):
                rep.err(f"{w}: '{key}' must be a non-negative int")
        if not isinstance(s.get("magic", False), bool):
            rep.err(f"{w}: 'magic' must be a bool")
        if "name_key" not in s:
            rep.err(f"{w}: missing name_key")
        status_rows = {st["id"]: st for st in statuses}
        for inf in s.get("statuses", []):
            if inf.get("id") not in status_ids:
                rep.err(f"{w}: inflicts unknown status '{inf.get('id')}'")
                continue
            if not status_rows[inf["id"]].get("implemented", False):
                rep.warn(f"{w}: inflicts '{inf['id']}', which the engine does not implement yet")
            dur = inf.get("duration", status_rows[inf["id"]].get("default_duration"))
            if inf["id"] in NO_PERMANENT_STATUSES and isinstance(dur, int) and dur < 0:
                rep.err(f"{w}: '{inf['id']}' must not be permanent (duration -1)")
            if inf["id"] in ONLY_PERMANENT_STATUSES and dur != -1:
                rep.err(f"{w}: '{inf['id']}' must be permanent (duration -1)")
            if inf["id"] in COUNTDOWN_STATUSES and (not isinstance(dur, int) or dur < 1):
                rep.err(f"{w}: '{inf['id']}' needs a countdown duration >= 1")
            ch = inf.get("chance", 100)
            if not isinstance(ch, int) or not 0 <= ch <= 100:
                rep.err(f"{w}: status chance must be 0..100")

    for st in statuses:
        if st.get("category") not in {"harmful", "beneficial"}:
            rep.err(f"statuses.{st['id']}: category must be harmful|beneficial")
        if not isinstance(st.get("default_duration"), int):
            rep.err(f"statuses.{st['id']}: default_duration must be an int (-1 = until cured)")
        elif st["id"] in NO_PERMANENT_STATUSES and st["default_duration"] < 1:
            rep.err(f"statuses.{st['id']}: default_duration must be >= 1")
        elif st["id"] in COUNTDOWN_STATUSES and st["default_duration"] < 1:
            rep.err(f"statuses.{st['id']}: default_duration must be >= 1")
        elif st["id"] in ONLY_PERMANENT_STATUSES and st["default_duration"] != -1:
            rep.err(f"statuses.{st['id']}: default_duration must be -1")

    hero_levels = {c.get("stats", {}).get("level") for c in characters if isinstance(c.get("stats"), dict)}
    if len(hero_levels) > 1:
        rep.err("characters: every hero must share one fixed stats.level (ADR 0012), "
                f"found {sorted(map(str, hero_levels))}")
    for c in characters:
        w = f"characters.{c['id']}"
        _check_stats(w, c.get("stats"), rep)
        for sk in c.get("skills", []):
            if sk not in skill_ids:
                rep.err(f"{w}: unknown skill '{sk}'")

    for e in enemies:
        w = f"enemies.{e['id']}"
        _check_stats(w, e.get("stats"), rep)
        own = set(e.get("skills", []))
        for sk in own:
            if sk not in skill_ids:
                rep.err(f"{w}: unknown skill '{sk}'")
        for el, aff in e.get("affinities", {}).items():
            if el not in ELEMENTS or aff not in AFFINITIES:
                rep.err(f"{w}: bad affinity {el}={aff}")
        if "role_answer" in e and e["role_answer"] not in char_ids:
            rep.err(f"{w}: role_answer '{e['role_answer']}' is not a character")
        if "currency" in e and (not isinstance(e["currency"], int) or isinstance(e["currency"], bool)
                                or e["currency"] < 0):
            rep.err(f"{w}: currency must be a non-negative int")
        if "delay_immune" in e and not isinstance(e["delay_immune"], bool):
            rep.err(f"{w}: delay_immune must be true or false")
        for d in e.get("drops", []):
            if not isinstance(d, dict) or d.get("item") not in item_ids:
                rep.err(f"{w}: drop {d!r} names an unknown item (game/data/items/items.json)")
            elif not isinstance(d.get("chance"), int) or not 0 <= d["chance"] <= 100:
                rep.err(f"{w}: drop chance must be an int in 0..100")
        ai = e.get("ai", [])
        if not ai:
            rep.err(f"{w}: needs at least one ai rule")
        if ai and "if" in ai[-1]:
            rep.warn(f"{w}: last ai rule has conditions; enemy may have no default action")
        for i, rule in enumerate(ai):
            for cond, arg in rule.get("if", {}).items():
                if cond not in AI_CONDITIONS:
                    rep.err(f"{w}.ai[{i}]: unknown condition '{cond}'")
                elif not _ai_arg_ok(cond, arg, status_ids):
                    rep.err(f"{w}.ai[{i}]: bad argument {arg!r} for '{cond}'")
            if not rule.get("pick"):
                rep.err(f"{w}.ai[{i}]: empty 'pick'")
            for opt in rule.get("pick", []):
                if opt.get("skill") not in own:
                    rep.err(f"{w}.ai[{i}]: picks skill '{opt.get('skill')}' the enemy does not have")
                if opt.get("target", "random_foe") not in AI_TARGETS:
                    rep.err(f"{w}.ai[{i}]: unknown target selector '{opt.get('target')}'")
                weight = opt.get("weight", 1)
                if not isinstance(weight, int) or isinstance(weight, bool) or weight < 0:
                    rep.err(f"{w}.ai[{i}]: weight must be an int >= 0")

    for enc in encounters:
        lineup = enc.get("enemies", [])
        if not lineup:
            rep.err(f"encounters.{enc['id']}: no enemies")
        for eid in lineup:
            if eid not in enemy_ids:
                rep.err(f"encounters.{enc['id']}: unknown enemy '{eid}'")
    return keys


def _ai_arg_ok(cond: str, arg: object, status_ids: set[str]) -> bool:
    if cond == "turn_mod":
        return (isinstance(arg, list) and len(arg) == 2 and all(isinstance(x, int) for x in arg)
                and arg[0] > 0 and 0 <= arg[1] < arg[0])
    if cond == "self_hp_below_pct":
        return isinstance(arg, int) and 1 <= arg <= 100
    if cond == "allies_alive_below":
        return isinstance(arg, int) and arg >= 1
    if cond == "foe_has_status":
        return arg in status_ids
    return False


TEXT_BOX_NUMBERS = ("chars_per_sec", "min_chars_per_sec", "max_chars_per_sec", "blip_volume_db")


def check_dialogue(root: Path, files: dict[str, object], rep: Report) -> list[str]:
    """Validates dialogue data tables and compiles every .dlg (freshness + syntax + emotion tags).
    Returns every *_key value found (for loc checks)."""
    keys: list[str] = []
    base = "game/data/dialogue"
    emotions = files.get(f"{base}/emotions.json")
    rows = emotions.get("emotions") if isinstance(emotions, dict) else None
    if not isinstance(rows, list) or not rows:
        rep.err(f"{base}/emotions.json: missing non-empty top-level list 'emotions'")
    else:
        seen: set[str] = set()
        for i, row in enumerate(rows):
            eid = row.get("id") if isinstance(row, dict) else None
            if not isinstance(eid, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", eid):
                rep.err(f"{base}/emotions.json[{i}]: needs a snake_case string 'id'")
            elif eid in seen:
                rep.err(f"{base}/emotions.json: duplicate emotion '{eid}'")
            else:
                seen.add(eid)

    speakers = files.get(f"{base}/speakers.json")
    rows = speakers.get("speakers") if isinstance(speakers, dict) else None
    if not isinstance(rows, list):
        rep.err(f"{base}/speakers.json: missing top-level list 'speakers'")
    else:
        seen = set()
        for i, row in enumerate(rows):
            sid = row.get("id") if isinstance(row, dict) else None
            if not isinstance(sid, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", sid):
                rep.err(f"{base}/speakers.json[{i}]: needs a lowercase string 'id'")
                continue
            if sid in seen:
                rep.err(f"{base}/speakers.json: duplicate speaker '{sid}'")
            if sid == dlgc.NARRATOR:
                rep.err(f"{base}/speakers.json: '{sid}' is reserved for narration lines (Narrator(id): ...)")
            seen.add(sid)
            if not isinstance(row.get("name_key"), str):
                rep.err(f"speakers.{sid}: missing name_key")
            else:
                keys.append(row["name_key"])
            pitch = row.get("blip_pitch")
            if isinstance(pitch, bool) or not isinstance(pitch, (int, float)) or pitch <= 0:
                rep.err(f"speakers.{sid}: blip_pitch must be a positive number")
            if not isinstance(row.get("portrait_id"), str) or not row["portrait_id"]:
                rep.err(f"speakers.{sid}: portrait_id must be a non-empty string")

    box = files.get(f"{base}/text_box.json")
    cfg = box.get("text_box") if isinstance(box, dict) else None
    if not isinstance(cfg, dict):
        rep.err(f"{base}/text_box.json: missing top-level object 'text_box'")
    else:
        for k in TEXT_BOX_NUMBERS:
            if isinstance(cfg.get(k), bool) or not isinstance(cfg.get(k), (int, float)):
                rep.err(f"text_box.{k} must be a number")
        nums = [cfg.get(k) for k in TEXT_BOX_NUMBERS[:3]]
        if all(isinstance(n, (int, float)) for n in nums) and not 0 < nums[1] <= nums[0] <= nums[2]:
            rep.err("text_box: need 0 < min_chars_per_sec <= chars_per_sec <= max_chars_per_sec")
        n = cfg.get("blip_every_n_chars")
        if isinstance(n, bool) or not isinstance(n, int) or n < 1:
            rep.err("text_box.blip_every_n_chars must be an int >= 1")
        if not isinstance(cfg.get("narration_blip"), bool):
            rep.err("text_box.narration_blip must be a bool")
        if not isinstance(cfg.get("flap_vowels"), str) or not cfg.get("flap_vowels"):
            rep.err("text_box.flap_vowels must be a non-empty string")

    for e in dialogue_vocab_errors(files.get(f"{base}/cues.json"), files.get(f"{base}/events.json")):
        rep.err(e)
    for e in camera_ease_errors(files.get(f"{base}/cues.json"), files.get("game/data/world/field_camera.json")):
        rep.err(e)
    errors, warnings = dlgc.check_report(root)
    for e in errors:
        rep.err(f"dlgc: {e}")
    for w in warnings:
        rep.warn(f"dlgc: {w}")
    return keys


def _arg_spec_errors(spec: object, where: str, sets: dict) -> list[str]:
    if not isinstance(spec, dict) or spec.get("type") not in dlgc.ARG_TYPES:
        return [f"{where}: needs a 'type' from {', '.join(dlgc.ARG_TYPES)}"]
    errs: list[str] = []
    if spec["type"] == "enum":
        if "set" in spec:
            if spec["set"] not in sets:
                errs.append(f"{where}: unknown set '{spec['set']}'")
        elif not isinstance(spec.get("values"), list) or not spec["values"]:
            errs.append(f"{where}: an enum needs 'values' or a 'set'")
    for bound in ("min", "max"):
        if bound in spec and (isinstance(spec[bound], bool) or not isinstance(spec[bound], (int, float))):
            errs.append(f"{where}: '{bound}' must be a number")
    return errs


def _positional_errors(args: object, where: str, sets: dict) -> list[str]:
    if not isinstance(args, list):
        return [f"{where}: 'args' must be a list"]
    errs: list[str] = []
    seen_optional = False
    for i, a in enumerate(args):
        errs += _arg_spec_errors(a, f"{where}.args[{i}]", sets)
        if isinstance(a, dict):
            if not isinstance(a.get("name"), str):
                errs.append(f"{where}.args[{i}]: needs a 'name'")
            if a.get("optional"):
                seen_optional = True
            elif seen_optional:
                errs.append(f"{where}.args[{i}]: a required arg after an optional one")
    return errs


def _reserved_value_errors(cue: str, values: dict, spec: object, cw: str) -> list[str]:
    """M1-ARC-07: a reserved value is a meaning string or {doc, kwargs: [keys of this cue]}."""
    errs: list[str] = []
    keys = set(spec.get("kwargs", {})) if isinstance(spec, dict) else set()
    for value, meaning in values.items():
        where = f"{cw}: reserved.{cue}.{value}"
        if isinstance(meaning, str) and meaning.strip():
            continue
        if not isinstance(meaning, dict) or not isinstance(meaning.get("doc"), str) or not meaning["doc"].strip():
            errs.append(f"{where}: needs a meaning string or an object with a 'doc'")
            continue
        only = meaning.get("kwargs", [])
        if not isinstance(only, list) or any(k not in keys for k in only):
            errs.append(f"{where}.kwargs: must list keys of @{cue} ({', '.join(sorted(keys)) or 'none'})")
    return errs


def camera_ease_errors(cues: object, field_camera: object) -> list[str]:
    """M1-ARC-07: cues.json's camera_eases set mirrors the eases in game/data/world/field_camera.json."""
    sets = cues.get("sets", {}) if isinstance(cues, dict) else {}
    eases = field_camera.get("eases", {}) if isinstance(field_camera, dict) else {}
    want = sorted(k for k, v in eases.items() if isinstance(v, dict)) if isinstance(eases, dict) else []
    got = sorted(sets.get("camera_eases", [])) if isinstance(sets, dict) else []
    if got != want:
        return [f"game/data/dialogue/cues.json: sets.camera_eases {got} must match the eases in "
                f"game/data/world/field_camera.json {want}"]
    return []


def dialogue_vocab_errors(cues: object, events: object) -> list[str]:
    """Shape of game/data/dialogue/cues.json and events.json (dlgc enforces their contents on .dlg files)."""
    errs: list[str] = []
    cw, ew = "game/data/dialogue/cues.json", "game/data/dialogue/events.json"
    if not isinstance(cues, dict) or not isinstance(cues.get("cues"), dict) or not cues["cues"]:
        errs.append(f"{cw}: missing non-empty object 'cues'")
        cues = {"cues": {}}
    sets = cues.get("sets", {})
    if not isinstance(sets, dict) or any(not isinstance(v, list) or not v for v in sets.values()):
        errs.append(f"{cw}: 'sets' must map names to non-empty lists")
        sets = {}
    for name, spec in cues["cues"].items():
        where = f"cues.{name}"
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            errs.append(f"{where}: cue names are snake_case")
        if not isinstance(spec, dict):
            errs.append(f"{where}: must be an object")
            continue
        errs += _positional_errors(spec.get("args", []), where, sets)
        kwargs = spec.get("kwargs", {})
        if not isinstance(kwargs, dict):
            errs.append(f"{where}: 'kwargs' must be an object")
            kwargs = {}
        for k, v in kwargs.items():
            errs += _arg_spec_errors(v, f"{where}.kwargs.{k}", sets)
        names = {a.get("name") for a in spec.get("args", []) if isinstance(a, dict)} | set(kwargs)
        for n in spec.get("one_of", []):
            if n not in names:
                errs.append(f"{where}.one_of: '{n}' is not an arg or key of this cue")
        for k, needed in spec.get("requires", {}).items():
            if k not in names or needed not in names:
                errs.append(f"{where}.requires: '{k}' and '{needed}' must both be args or keys of this cue")
    for cue, values in (cues.get("reserved") or {}).items():
        if cue not in cues["cues"] or not isinstance(values, dict):
            errs.append(f"{cw}: reserved.{cue} must name a cue and map values to their meaning")
            continue
        errs += _reserved_value_errors(cue, values, cues["cues"][cue], cw)
    rows = events.get("events") if isinstance(events, dict) else None
    if not isinstance(rows, list) or not rows:
        return errs + [f"{ew}: missing non-empty list 'events'"]
    seen: set[str] = set()
    for i, row in enumerate(rows):
        eid = row.get("id") if isinstance(row, dict) else None
        if not isinstance(eid, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", eid):
            errs.append(f"{ew}[{i}]: needs a snake_case string 'id'")
            continue
        if eid in seen:
            errs.append(f"{ew}: duplicate event '{eid}'")
        seen.add(eid)
        if not isinstance(row.get("doc"), str) or not row["doc"].strip():
            errs.append(f"events.{eid}: needs a one-line 'doc'")
        errs += _positional_errors(row.get("args", []), f"events.{eid}", sets)
    return errs


def _is_int(v: object) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def facets_errors(doc: object, where: str = FACETS_FILE) -> list[str]:
    """Checks the Facet table and the board rules. Pure: returns error strings."""
    if not isinstance(doc, dict):
        return [f"{where}: must be an object with 'rules' and 'facets'"]
    errs: list[str] = []
    rules = doc.get("rules")
    if not isinstance(rules, dict):
        errs.append(f"{where}: missing 'rules' object")
        rules = {}
    for k in sorted(FACET_RULE_KEYS):
        if not _is_int(rules.get(k)) or rules[k] < 0:
            errs.append(f"{where}: rules.{k} must be a non-negative int")
    for k in sorted(set(rules) - FACET_RULE_KEYS):
        errs.append(f"{where}: unknown rule '{k}'")
    max_level = rules["max_gate_level"] if _is_int(rules.get("max_gate_level")) else 0
    if max_level < 1:
        errs.append(f"{where}: rules.max_gate_level must be at least 1")
    facets = doc.get("facets")
    if not isinstance(facets, list):
        return errs + [f"{where}: missing 'facets' list"]
    seen: set[str] = set()
    types: set[str] = set()
    stat_owner: dict[str, str] = {}
    key_levels: set[int] = set()
    for i, f in enumerate(facets):
        if not isinstance(f, dict) or not isinstance(f.get("id"), str):
            errs.append(f"{where}: facets[{i}] needs a string 'id'")
            continue
        fid = f["id"]
        w = f"{where}: facet '{fid}'"
        if fid in seen:
            errs.append(f"{where}: duplicate facet id '{fid}'")
        seen.add(fid)
        ftype = f.get("type")
        if ftype not in FACET_TYPES:
            errs.append(f"{w}: type must be one of {sorted(FACET_TYPES)}")
            continue
        types.add(ftype)
        if f.get("activates") != FACET_TYPES[ftype]:
            errs.append(f"{w}: a {ftype} facet activates '{FACET_TYPES[ftype]}' nodes")
        if "name_key" not in f:
            errs.append(f"{w}: missing name_key")
        if FACET_TYPES[ftype] == "stat":
            stats = f.get("stats")
            if not isinstance(stats, list) or not stats:
                errs.append(f"{w}: needs a non-empty 'stats' list")
                continue
            for st in stats:
                if st not in LATTICE_STATS:
                    errs.append(f"{w}: unknown stat '{st}' (valid: {sorted(LATTICE_STATS)})")
                elif st in stat_owner:
                    errs.append(f"{w}: stat '{st}' is already activated by '{stat_owner[st]}'")
                else:
                    stat_owner[st] = fid
        if ftype == "key":
            lvl = f.get("level")
            if not _is_int(lvl) or not 1 <= lvl <= max(max_level, 1):
                errs.append(f"{w}: key level must be an int in 1..{max_level}")
            elif lvl in key_levels:
                errs.append(f"{w}: duplicate key level {lvl}")
            else:
                key_levels.add(lvl)
    for t in sorted(set(FACET_TYPES) - types):
        errs.append(f"{where}: no facet of type '{t}' (SPEC §6.4 needs all six)")
    for st in sorted(LATTICE_STATS - set(stat_owner)):
        errs.append(f"{where}: no facet activates stat '{st}'")
    for lvl in range(1, max_level + 1):
        if lvl not in key_levels:
            errs.append(f"{where}: no key facet for gate level {lvl}")
    return errs


def _check_lattice_node(n: dict, w: str, max_gate_level: int, skill_ids: set[str], char_ids: set[str],
                        starts: dict[str, str]) -> list[str]:
    errs: list[str] = []
    ntype = n["type"]
    for k in sorted(set(n) - LATTICE_COMMON_FIELDS - LATTICE_NODE_FIELDS[ntype]):
        errs.append(f"{w}: field '{k}' does not belong on a {ntype} node")
    if ntype == "stat":
        if n.get("stat") not in LATTICE_STATS:
            errs.append(f"{w}: unknown stat '{n.get('stat')}' (valid: {sorted(LATTICE_STATS)})")
        if not _is_int(n.get("value")) or n["value"] <= 0:
            errs.append(f"{w}: stat value must be a positive int")
    elif ntype == "ability":
        if n.get("skill") not in skill_ids:
            errs.append(f"{w}: unknown skill '{n.get('skill')}' (add it to skills.json)")
    elif ntype == "gate":
        lvl = n.get("gate_level")
        if not _is_int(lvl) or not 1 <= lvl <= max_gate_level:
            errs.append(f"{w}: gate needs a gate_level in 1..{max_gate_level}")
    elif ntype == "start":
        cid = n.get("character")
        if cid not in char_ids:
            errs.append(f"{w}: start for unknown character '{cid}'")
        elif cid in starts:
            errs.append(f"{w}: character '{cid}' already starts at '{starts[cid]}'")
        else:
            starts[cid] = n["id"]
    return errs


def lattice_errors(board: object, max_gate_level: int, skill_ids: set[str], char_ids: set[str],
                   where: str) -> list[str]:
    """Checks one Lattice board. Pure: returns error strings (tools/lattice_editor reuses it)."""
    if not isinstance(board, dict):
        return [f"{where}: must be an object with 'board', 'nodes' and 'edges'"]
    errs: list[str] = []
    meta = board.get("board")
    if not isinstance(meta, dict) or not isinstance(meta.get("id"), str) or "name_key" not in meta:
        errs.append(f"{where}: 'board' needs a string 'id' and a 'name_key'")
    nodes, edges = board.get("nodes"), board.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return errs + [f"{where}: needs 'nodes' and 'edges' lists"]
    ids: dict[str, dict] = {}
    coords: dict[tuple[int, int], str] = {}
    starts: dict[str, str] = {}
    for i, n in enumerate(nodes):
        if not isinstance(n, dict) or not isinstance(n.get("id"), str):
            errs.append(f"{where}: nodes[{i}] needs a string 'id'")
            continue
        nid = n["id"]
        w = f"{where}: node '{nid}'"
        if nid in ids:
            errs.append(f"{where}: duplicate node id '{nid}'")
        ids[nid] = n
        if n.get("type") not in LATTICE_NODE_TYPES:
            errs.append(f"{w}: type must be one of {sorted(LATTICE_NODE_TYPES)}")
            continue
        x, y = n.get("x"), n.get("y")
        if not _is_int(x) or not _is_int(y):
            errs.append(f"{w}: x and y must be ints")
        elif (x, y) in coords:
            errs.append(f"{w}: duplicate coordinates ({x}, {y}) with '{coords[(x, y)]}'")
        else:
            coords[(x, y)] = nid
        errs += _check_lattice_node(n, w, max_gate_level, skill_ids, char_ids, starts)
    adj: dict[str, set[str]] = {nid: set() for nid in ids}
    seen_edges: set[frozenset[str]] = set()
    for i, e in enumerate(edges):
        if not (isinstance(e, list) and len(e) == 2 and all(isinstance(v, str) for v in e)):
            errs.append(f"{where}: edges[{i}] must be a pair of node ids")
            continue
        a, b = e
        dangling = [v for v in (a, b) if v not in ids]
        if dangling:
            errs.append(f"{where}: dangling edge [{a}, {b}]: unknown node(s) {dangling}")
            continue
        if a == b:
            errs.append(f"{where}: edge [{a}, {b}] is a self-loop")
            continue
        if frozenset((a, b)) in seen_edges:
            errs.append(f"{where}: duplicate edge [{a}, {b}]")
        seen_edges.add(frozenset((a, b)))
        adj[a].add(b)
        adj[b].add(a)
    if not starts:
        errs.append(f"{where}: board has no start nodes")
    for cid, sid in sorted(starts.items()):
        seen = {sid}
        todo = [sid]
        while todo:
            for nb in adj[todo.pop()]:
                if nb not in seen:
                    seen.add(nb)
                    todo.append(nb)
        lost = [nid for nid in ids if nid not in seen]
        if lost:
            errs.append(f"{where}: {len(lost)} node(s) unreachable from {cid}'s start '{sid}': {lost[:8]}")
    return errs


def _ids(files: dict[str, object], rel: str, table: str) -> set[str]:
    doc = files.get(rel)
    rows = doc.get(table, []) if isinstance(doc, dict) else []
    return {r["id"] for r in rows if isinstance(r, dict) and isinstance(r.get("id"), str)}


def check_progression(files: dict[str, object], rep: Report) -> list[str]:
    """Validates facets.json and every Lattice board. Returns *_key values for loc checks."""
    keys: list[str] = []
    boards = sorted(k for k in files if Path(k).parent.as_posix() == LATTICE_DIR and Path(k).match(LATTICE_GLOB))
    facets = files.get(FACETS_FILE)
    if facets is None:
        if boards:
            rep.err(f"{FACETS_FILE} is missing but Lattice boards exist")
        return keys
    for e in facets_errors(facets):
        rep.err(e)
    rules = facets.get("rules") if isinstance(facets, dict) else None
    max_level = rules.get("max_gate_level") if isinstance(rules, dict) else 0
    max_level = max_level if _is_int(max_level) else 0
    for f in facets.get("facets", []) if isinstance(facets, dict) else []:
        if isinstance(f, dict) and isinstance(f.get("name_key"), str):
            keys.append(f["name_key"])
    skill_ids = _ids(files, "game/data/battle/skills.json", "skills")
    char_ids = _ids(files, "game/data/battle/characters.json", "characters")
    for rel in boards:
        board = files[rel]
        for e in lattice_errors(board, max_level, skill_ids, char_ids, rel):
            rep.err(e)
        meta = board.get("board") if isinstance(board, dict) else None
        if isinstance(meta, dict) and isinstance(meta.get("name_key"), str):
            keys.append(meta["name_key"])
    return keys


def load_loc_keys(root: Path, rep: Report) -> set[str]:
    keys: set[str] = set()
    for p in sorted((root / "game" / "data" / "loc").glob("*.csv")):
        with p.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header or header[0] != "keys":
                rep.err(f"{p.relative_to(root)}: first column header must be 'keys'")
                continue
            for row in reader:
                if not row:
                    continue
                if row[0] in keys:
                    rep.err(f"{p.relative_to(root)}: duplicate loc key {row[0]}")
                keys.add(row[0])
                if len(row) < len(header) or any(not c.strip() for c in row[1:len(header)]):
                    rep.err(f"{p.relative_to(root)}: key {row[0]} has an empty translation")
    return keys


def dlg_line_key(line_id: str) -> str:
    return "DLG_" + line_id.upper()


def check_loc(root: Path, data_keys: list[str], loc: set[str], rep: Report) -> None:
    for k in data_keys:
        if k not in loc:
            rep.err(f"missing localization key '{k}' (referenced by data)")
    for p in (root / "game").rglob("*.gd"):
        for k in GD_TR_RE.findall(p.read_text(encoding="utf-8")):
            if k not in loc:
                rep.err(f"{p.relative_to(root)}: tr('{k}') has no localization entry")
    for p in (root / "game").rglob("*.dlg"):
        for lid in DLG_LINE_RE.findall(p.read_text(encoding="utf-8")):
            if dlg_line_key(lid) not in loc:
                rep.err(f"{p.relative_to(root)}: line '{lid}' has no localization entry "
                        f"(run tools/dlgc.py)")


def load_flags(root: Path, rep: Report) -> set[str]:
    p = root / "game" / "data" / "flags.tres"
    if not p.exists():
        rep.err("game/data/flags.tres is missing")
        return set()
    m = re.search(r"^flags = (\{.*?^\})", p.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        rep.err("game/data/flags.tres: could not find 'flags = { ... }' block")
        return set()
    try:
        flags = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        rep.err(f"game/data/flags.tres: flags block must stay JSON-compatible: {e}")
        return set()
    for k, v in flags.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", k):
            rep.err(f"flags.tres: flag '{k}' must be snake_case")
        if not isinstance(v, str) or not v.strip():
            rep.err(f"flags.tres: flag '{k}' needs a description")
    return set(flags)


def check_flags(root: Path, declared: set[str], rep: Report) -> None:
    used: dict[str, str] = {}
    for p in list((root / "game").rglob("*.gd")) + list((root / "tests").rglob("*.gd")):
        for f in GD_FLAG_RE.findall(p.read_text(encoding="utf-8")):
            used.setdefault(f, p.relative_to(root).as_posix())
    for p in (root / "game").rglob("*.dlg"):
        for f in DLG_FLAG_RE.findall(p.read_text(encoding="utf-8")):
            used.setdefault(f, p.relative_to(root).as_posix())
    for f, where in sorted(used.items()):
        if f not in declared:
            rep.err(f"{where}: undeclared story flag '{f}' (declare it in game/data/flags.tres)")


def check_provenance(root: Path, rep: Report) -> None:
    assets = root / "assets"
    prov = assets / "PROVENANCE.md"
    if not prov.exists():
        rep.err("assets/PROVENANCE.md is missing")
        return
    listed: set[str] = set()
    for line in prov.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and not set(line) <= set("|-: "):
            cell = line.strip("|").split("|")[0].strip().strip("`")
            if cell and cell.lower() != "path":
                listed.add(cell)
    for p in sorted(assets.rglob("*")):
        if p.is_dir() or p.name in {"PROVENANCE.md", ".gitkeep"} or p.suffix == ".import":
            continue
        rel = p.relative_to(root).as_posix()
        if rel not in listed:
            rep.err(f"{rel}: no entry in assets/PROVENANCE.md")
    for rel in sorted(listed):
        if not (root / rel).exists():
            rep.warn(f"PROVENANCE.md lists '{rel}' but the file does not exist")


def load_banned(root: Path) -> list[re.Pattern[str]]:
    pats: list[re.Pattern[str]] = []
    for line in (root / "tools" / "banned_terms.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        flags = 0
        if line.startswith("i:"):
            flags, line = re.I, line[2:]
        pats.append(re.compile(r"(?<![A-Za-z0-9_])" + re.escape(line) + r"(?![A-Za-z0-9_])", flags))
    return pats


def check_banned(root: Path, rep: Report) -> None:
    pats = load_banned(root)
    for entry in BANNED_SCAN:
        base = root / entry
        files = [base] if base.is_file() else (sorted(base.rglob("*")) if base.exists() else [])
        for p in files:
            if not p.is_file() or p.suffix not in BANNED_SCAN_EXT:
                continue
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for pat in pats:
                    m = pat.search(line)
                    if m:
                        rep.err(f"{p.relative_to(root)}:{n}: banned term '{m.group(0)}' (SPEC §2)")


def check_binary_sizes(root: Path, rep: Report) -> None:
    for base in ("assets", "assets_src", "game", "tests"):
        d = root / base
        if not d.exists():
            continue
        for p in d.rglob("*"):
            if p.is_file() and p.suffix.lower() in BINARY_EXT and p.stat().st_size > MAX_BINARY_BYTES:
                rep.err(f"{p.relative_to(root)}: {p.stat().st_size} bytes exceeds the "
                        f"{MAX_BINARY_BYTES}-byte limit while Git LFS is deferred (ADR 0005)")


def collect_keys(obj: object) -> list[str]:
    """Every string value of a field named *_key, anywhere in nested JSON."""
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and k.endswith("_key") and isinstance(v, str):
                out.append(v)
            else:
                out += collect_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            out += collect_keys(v)
    return out


# --- Items, equipment, abilities, Customize and shops (M1-PRG-02, docs/kb/design/economy.md) --------

ITEMS_DIR = "game/data/items"
ITEM_TABLES = ("items", "equipment", "abilities", "customize", "shops")
ITEM_CATEGORIES = {"consumable", "material", "facet", "key"}
ITEM_RULE_INTS = ("stack_cap", "key_item_cap", "currency_cap")
ITEM_RANK_MIN, ITEM_RANK_MAX = 1, 8  # same range as skill ranks (formulas.md, Time)
ITEM_EFFECT_FIELDS = {"heal_hp": {"amount"}, "restore_mp": {"amount"}, "cure": {"statuses"},
                      "revive": {"hp_pct"}, "add_status": {"status", "duration"}, "delay": {"ranks"},
                      "damage": {"amount", "element"}}
EQUIP_SLOTS = {"weapon", "armor"}
MAX_EQUIP_SLOTS = 4  # SPEC §6.5: "up to four ability slots"
ABILITY_EFFECT_FIELDS = {"on_hit_element": {"element"}, "status_strike": {"status", "chance", "duration"},
                         "stat_bonus": {"stat", "amount"}, "element_guard": {"element", "affinity"},
                         "status_ward": {"status"}, "auto_status": {"status", "trigger"},
                         "economy": {"currency_mult"}, "field": {"encounter_rate_pct"},
                         "special": {"break_damage_cap"}}
ABILITY_OPTIONAL_FIELDS = {"auto_status": {"hp_below_pct"}}
GUARD_AFFINITIES = {"resist", "immune", "absorb"}
AUTO_TRIGGERS = {"always", "low_hp"}
SHOP_KINDS = {"items", "equipment"}


def _rows(doc: object, table: str, where: str, errs: list[str]) -> list[dict]:
    """Rows of doc[table] that have a unique string id; reports the rest."""
    rows = doc.get(table) if isinstance(doc, dict) else None
    if not isinstance(rows, list):
        errs.append(f"{where}: missing top-level list '{table}'")
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for i, r in enumerate(rows):
        if not isinstance(r, dict) or not isinstance(r.get("id"), str):
            errs.append(f"{where}[{i}]: row needs a string 'id'")
            continue
        if r["id"] in seen:
            errs.append(f"{where}: duplicate id '{r['id']}'")
        seen.add(r["id"])
        out.append(r)
    return out


def _pos_int(v: object) -> bool:
    return _is_int(v) and v > 0


def _need_keys(row: dict, w: str, keys: tuple[str, ...], errs: list[str]) -> None:
    for k in keys:
        if not isinstance(row.get(k), str) or not row[k]:
            errs.append(f"{w}: missing {k}")


def _item_effect_errors(e: object, w: str, refs: dict[str, set[str]]) -> list[str]:
    if not isinstance(e, dict) or e.get("type") not in ITEM_EFFECT_FIELDS:
        return [f"{w}: effect type must be one of {sorted(ITEM_EFFECT_FIELDS)}"]
    errs: list[str] = []
    t = e["type"]
    for k in sorted(ITEM_EFFECT_FIELDS[t] - set(e)):
        errs.append(f"{w}: {t} effect needs '{k}'")
    for k in sorted(set(e) - ITEM_EFFECT_FIELDS[t] - {"type"}):
        errs.append(f"{w}: field '{k}' does not belong on a {t} effect")
    for k in ("amount", "ranks"):
        if k in e and not _pos_int(e[k]):
            errs.append(f"{w}: {t}.{k} must be a positive int")
    if "hp_pct" in e and not (_is_int(e["hp_pct"]) and 1 <= e["hp_pct"] <= 100):
        errs.append(f"{w}: revive.hp_pct must be an int in 1..100")
    if "element" in e and e["element"] not in ELEMENTS:
        errs.append(f"{w}: unknown element '{e['element']}'")
    if "statuses" in e:
        sts = e["statuses"]
        if not isinstance(sts, list) or not sts:
            errs.append(f"{w}: cure.statuses must be a non-empty list")
        else:
            for s in sts:
                if s not in refs["statuses"]:
                    errs.append(f"{w}: unknown status '{s}'")
    if t == "add_status":
        s = e.get("status")
        if s not in refs["statuses"]:
            errs.append(f"{w}: unknown status '{s}'")
        if not _is_int(e.get("duration")) or e["duration"] == 0 or e["duration"] < -1:
            errs.append(f"{w}: add_status.duration must be -1 or a positive int")
        elif e["duration"] == -1 and s in NO_PERMANENT_STATUSES:
            errs.append(f"{w}: '{s}' may not be permanent (formulas.md, Stop / Sleep)")
    return errs


def _items_table_errors(doc: object, refs: dict[str, set[str]], w0: str, errs: list[str]) -> dict[str, dict]:
    rules = doc.get("rules") if isinstance(doc, dict) else None
    if not isinstance(rules, dict):
        errs.append(f"{w0}: missing 'rules' object")
        rules = {}
    for k in ITEM_RULE_INTS:
        if not _pos_int(rules.get(k)):
            errs.append(f"{w0}: rules.{k} must be a positive int")
    order = rules.get("category_order")
    if not isinstance(order, list) or sorted(order) != sorted(ITEM_CATEGORIES):
        errs.append(f"{w0}: rules.category_order must list each of {sorted(ITEM_CATEGORIES)} once")
    items: dict[str, dict] = {}
    for it in _rows(doc, "items", w0, errs):
        w = f"{w0}: item '{it['id']}'"
        items[it["id"]] = it
        cat = it.get("category")
        if cat not in ITEM_CATEGORIES:
            errs.append(f"{w}: category must be one of {sorted(ITEM_CATEGORIES)}")
            continue
        _need_keys(it, w, ("name_key", "desc_key"), errs)
        if cat == "key":
            for k in ("price", "stack_cap", "battle"):
                if k in it:
                    errs.append(f"{w}: key items have no '{k}' (they can't be sold or stacked)")
        elif not _pos_int(it.get("price")):
            errs.append(f"{w}: price must be a positive int")
        if "stack_cap" in it and not _pos_int(it["stack_cap"]):
            errs.append(f"{w}: stack_cap must be a positive int")
        if cat == "facet":
            if it.get("facet") != it["id"] or it["id"] not in refs["facets"]:
                errs.append(f"{w}: a facet item needs 'facet' equal to its id and listed in {FACETS_FILE}")
        elif "facet" in it:
            errs.append(f"{w}: only facet items carry 'facet'")
        if "field" in it and not isinstance(it["field"], bool):
            errs.append(f"{w}: 'field' must be true or false")
        if "battle" in it:
            b = it["battle"]
            if cat != "consumable":
                errs.append(f"{w}: only consumables can be used in battle")
            if not isinstance(b, dict):
                errs.append(f"{w}: 'battle' must be an object")
                continue
            if b.get("target") not in SKILL_TARGETS:
                errs.append(f"{w}: battle.target must be one of {sorted(SKILL_TARGETS)}")
            if not (_is_int(b.get("rank")) and ITEM_RANK_MIN <= b["rank"] <= ITEM_RANK_MAX):
                errs.append(f"{w}: battle.rank must be an int in {ITEM_RANK_MIN}..{ITEM_RANK_MAX}")
            effects = b.get("effects")
            if not isinstance(effects, list) or not effects:
                errs.append(f"{w}: battle.effects must be a non-empty list")
                continue
            for j, e in enumerate(effects):
                errs += _item_effect_errors(e, f"{w}: effects[{j}]", refs)
    for fid in sorted(refs["facets"] - set(items)):
        errs.append(f"{w0}: Facet '{fid}' from {FACETS_FILE} has no item row")
    return items


def _ability_effect_errors(ab: dict, w: str, refs: dict[str, set[str]]) -> list[str]:
    cat = ab["category"]
    eff = ab.get("effect")
    if not isinstance(eff, dict):
        return [f"{w}: needs an 'effect' object"]
    errs: list[str] = []
    want = ABILITY_EFFECT_FIELDS[cat]
    for k in sorted(want - set(eff)):
        errs.append(f"{w}: {cat} effect needs '{k}'")
    for k in sorted(set(eff) - want - ABILITY_OPTIONAL_FIELDS.get(cat, set())):
        errs.append(f"{w}: field '{k}' does not belong on a {cat} effect")
    if "element" in eff and eff["element"] not in ELEMENTS - {"none"}:
        errs.append(f"{w}: unknown element '{eff['element']}'")
    if "affinity" in eff and eff["affinity"] not in GUARD_AFFINITIES:
        errs.append(f"{w}: guard affinity must be one of {sorted(GUARD_AFFINITIES)}")
    if "stat" in eff and eff["stat"] not in LATTICE_STATS:
        errs.append(f"{w}: unknown stat '{eff['stat']}'")
    if "amount" in eff and not _pos_int(eff["amount"]):
        errs.append(f"{w}: amount must be a positive int")
    if "status" in eff:
        s = eff["status"]
        kind = "beneficial" if cat == "auto_status" else "harmful"
        if s not in refs["statuses"]:
            errs.append(f"{w}: unknown status '{s}'")
        elif s not in refs[kind]:
            errs.append(f"{w}: {cat} needs a {kind} status, not '{s}'")
    if cat == "status_strike":
        if not (_is_int(eff.get("chance")) and 1 <= eff["chance"] <= 100):
            errs.append(f"{w}: chance must be an int in 1..100")
        d = eff.get("duration")
        if not _is_int(d) or d == 0 or d < -1:
            errs.append(f"{w}: duration must be -1 or a positive int")
        elif d == -1 and eff.get("status") in NO_PERMANENT_STATUSES:
            errs.append(f"{w}: '{eff['status']}' may not be permanent (formulas.md, Stop / Sleep)")
    if cat == "auto_status":
        trig = eff.get("trigger")
        if trig not in AUTO_TRIGGERS:
            errs.append(f"{w}: trigger must be one of {sorted(AUTO_TRIGGERS)}")
        pct = eff.get("hp_below_pct")
        if trig == "low_hp" and not (_is_int(pct) and 1 <= pct <= 99):
            errs.append(f"{w}: a low_hp trigger needs hp_below_pct in 1..99")
        if trig == "always" and pct is not None:
            errs.append(f"{w}: an always trigger takes no hp_below_pct")
    if cat == "economy" and not (_is_int(eff.get("currency_mult")) and eff["currency_mult"] >= 2):
        errs.append(f"{w}: currency_mult must be an int of at least 2")
    if cat == "field" and not (_is_int(eff.get("encounter_rate_pct")) and 0 <= eff["encounter_rate_pct"] < 100):
        errs.append(f"{w}: encounter_rate_pct must be an int in 0..99")
    if cat == "special" and eff.get("break_damage_cap") is not True:
        errs.append(f"{w}: the only special effect is break_damage_cap: true")
    return errs


def _equipment_errors(doc: object, abilities: dict[str, dict], refs: dict[str, set[str]],
                      item_ids: set[str], w0: str, errs: list[str]) -> dict[str, dict]:
    rules = doc.get("rules") if isinstance(doc, dict) else None
    if not isinstance(rules, dict):
        errs.append(f"{w0}: missing 'rules' object")
        rules = {}
    max_slots = rules.get("max_slots")
    if not (_is_int(max_slots) and 1 <= max_slots <= MAX_EQUIP_SLOTS):
        errs.append(f"{w0}: rules.max_slots must be an int in 1..{MAX_EQUIP_SLOTS} (SPEC §6.5)")
        max_slots = MAX_EQUIP_SLOTS
    slots = rules.get("equip_slots")
    if not isinstance(slots, list) or not slots or not set(slots) <= EQUIP_SLOTS or len(set(slots)) != len(slots):
        errs.append(f"{w0}: rules.equip_slots must list slots from {sorted(EQUIP_SLOTS)} once each")
        slots = sorted(EQUIP_SLOTS)
    required = rules.get("required_slots", [])
    if not isinstance(required, list) or not set(required) <= set(slots):
        errs.append(f"{w0}: rules.required_slots must be a subset of equip_slots")
        required = []
    gear: dict[str, dict] = {}
    for g in _rows(doc, "gear_types", f"{w0} gear_types", errs):
        w = f"{w0}: gear type '{g['id']}'"
        gear[g["id"]] = g
        if g.get("slot") not in slots:
            errs.append(f"{w}: slot must be one of {slots}")
        if g.get("character") not in refs["characters"]:
            errs.append(f"{w}: unknown character '{g.get('character')}'")
        _need_keys(g, w, ("name_key",), errs)
    pieces: dict[str, dict] = {}
    for e in _rows(doc, "equipment", w0, errs):
        w = f"{w0}: '{e['id']}'"
        pieces[e["id"]] = e
        if e["id"] in item_ids:
            errs.append(f"{w}: id clashes with an item id (shops share one namespace)")
        _need_keys(e, w, ("name_key", "desc_key"), errs)
        if not _pos_int(e.get("price")):
            errs.append(f"{w}: price must be a positive int")
        gt = gear.get(e.get("type"))
        if gt is None:
            errs.append(f"{w}: unknown gear type '{e.get('type')}'")
        n = e.get("slots")
        if not (_is_int(n) and 0 <= n <= max_slots):
            errs.append(f"{w}: slots must be an int in 0..{max_slots}")
            n = max_slots
        pre = e.get("abilities", [])
        if not isinstance(pre, list):
            errs.append(f"{w}: abilities must be a list")
            pre = []
        if len(pre) > n:
            errs.append(f"{w}: {len(pre)} pre-filled abilities but only {n} slots")
        if len(set(pre)) != len(pre):
            errs.append(f"{w}: an ability appears twice")
        for a in pre:
            if a not in abilities:
                errs.append(f"{w}: unknown ability '{a}'")
            elif gt is not None and gt.get("slot") not in abilities[a].get("equip", []):
                errs.append(f"{w}: ability '{a}' does not fit a {gt.get('slot')} piece")
        stats = e.get("stats", {})
        if not isinstance(stats, dict):
            errs.append(f"{w}: stats must be an object")
            stats = {}
        for k, v in stats.items():
            if k not in LATTICE_STATS:
                errs.append(f"{w}: unknown stat '{k}'")
            elif not _pos_int(v):
                errs.append(f"{w}: stat '{k}' must be a positive int")
    starting = doc.get("starting", {}) if isinstance(doc, dict) else {}
    if not isinstance(starting, dict):
        errs.append(f"{w0}: 'starting' must be an object")
        starting = {}
    for cid in sorted(refs["characters"] - set(starting)):
        errs.append(f"{w0}: character '{cid}' has no starting gear")
    for cid, lo in starting.items():
        w = f"{w0}: starting.{cid}"
        if cid not in refs["characters"]:
            errs.append(f"{w}: unknown character")
        if not isinstance(lo, dict):
            errs.append(f"{w}: must map slot -> equipment id")
            continue
        for s in required:
            if s not in lo:
                errs.append(f"{w}: missing required slot '{s}'")
        for s, eid in lo.items():
            gt = gear.get(pieces.get(eid, {}).get("type"))
            if eid not in pieces:
                errs.append(f"{w}.{s}: unknown equipment '{eid}'")
            elif gt is not None and (gt.get("slot") != s or gt.get("character") != cid):
                errs.append(f"{w}.{s}: '{eid}' is a {gt.get('character')} {gt.get('slot')} piece")
    return pieces


def items_errors(docs: dict[str, object], refs: dict[str, set[str]]) -> list[str]:
    """Checks the item tables. Pure: returns error strings.

    docs maps 'items', 'equipment', 'abilities', 'customize', 'shops' to parsed JSON. refs holds
    sets: 'characters', 'statuses', 'harmful', 'beneficial', 'facets', 'flags'."""
    errs: list[str] = []
    w = {t: f"{ITEMS_DIR}/{t}.json" for t in ITEM_TABLES}
    items = _items_table_errors(docs.get("items"), refs, w["items"], errs)
    abilities: dict[str, dict] = {}
    for ab in _rows(docs.get("abilities"), "abilities", w["abilities"], errs):
        aw = f"{w['abilities']}: '{ab['id']}'"
        abilities[ab["id"]] = ab
        _need_keys(ab, aw, ("name_key", "desc_key"), errs)
        eq = ab.get("equip")
        if not isinstance(eq, list) or not eq or not set(eq) <= EQUIP_SLOTS:
            errs.append(f"{aw}: equip must list slots from {sorted(EQUIP_SLOTS)}")
        if ab.get("category") not in ABILITY_EFFECT_FIELDS:
            errs.append(f"{aw}: category must be one of {sorted(ABILITY_EFFECT_FIELDS)}")
            continue
        errs += _ability_effect_errors(ab, aw, refs)
    pieces = _equipment_errors(docs.get("equipment"), abilities, refs, set(items), w["equipment"], errs)
    cz = docs.get("customize")
    recipes = cz.get("recipes") if isinstance(cz, dict) else None
    if not isinstance(recipes, list):
        errs.append(f"{w['customize']}: missing top-level list 'recipes'")
        recipes = []
    seen: set[str] = set()
    for i, r in enumerate(recipes):
        rw = f"{w['customize']}: recipes[{i}]"
        if not isinstance(r, dict):
            errs.append(f"{rw}: must be an object")
            continue
        aid = r.get("ability")
        if aid not in abilities:
            errs.append(f"{rw}: unknown ability '{aid}'")
        elif aid in seen:
            errs.append(f"{rw}: second recipe for '{aid}'")
        seen.add(aid)
        parts = r.get("items")
        if not isinstance(parts, list) or not parts:
            errs.append(f"{rw}: items must be a non-empty list")
            continue
        used: set[str] = set()
        for p in parts:
            iid = p.get("item") if isinstance(p, dict) else None
            if iid not in items:
                errs.append(f"{rw}: unknown item '{iid}'")
            elif items[iid].get("category") == "key":
                errs.append(f"{rw}: key item '{iid}' can't be spent")
            if iid in used:
                errs.append(f"{rw}: item '{iid}' listed twice")
            used.add(iid)
            if not isinstance(p, dict) or not _pos_int(p.get("count")):
                errs.append(f"{rw}: count for '{iid}' must be a positive int")
    sh = docs.get("shops")
    rules = sh.get("rules") if isinstance(sh, dict) else None
    if not isinstance(rules, dict):
        errs.append(f"{w['shops']}: missing 'rules' object")
        rules = {}
    num, den = rules.get("sell_ratio_num"), rules.get("sell_ratio_den")
    if not (_is_int(num) and _pos_int(den) and 0 <= num <= den):
        errs.append(f"{w['shops']}: sell ratio must be ints with 0 <= sell_ratio_num <= sell_ratio_den, den > 0")
    if not (_is_int(rules.get("min_sell_price")) and rules["min_sell_price"] >= 0):
        errs.append(f"{w['shops']}: rules.min_sell_price must be a non-negative int")
    for shop in _rows(sh, "shops", w["shops"], errs):
        sw = f"{w['shops']}: '{shop['id']}'"
        _need_keys(shop, sw, ("name_key",), errs)
        kind = shop.get("kind")
        if kind not in SHOP_KINDS:
            errs.append(f"{sw}: kind must be one of {sorted(SHOP_KINDS)}")
        flag = shop.get("requires_flag", "")
        if flag and flag not in refs["flags"]:
            errs.append(f"{sw}: undeclared story flag '{flag}' (declare it in game/data/flags.tres)")
        stock = shop.get("stock")
        if not isinstance(stock, list) or not stock:
            errs.append(f"{sw}: stock must be a non-empty list")
            continue
        listed: set[str] = set()
        for row in stock:
            gid = row.get("item") if isinstance(row, dict) else None
            table = pieces if kind == "equipment" else items
            if gid not in table:
                errs.append(f"{sw}: unknown {'equipment' if kind == 'equipment' else 'item'} '{gid}' in stock")
            elif kind == "items" and items[gid].get("category") == "key":
                errs.append(f"{sw}: key item '{gid}' can't be sold in a shop")
            if gid in listed:
                errs.append(f"{sw}: '{gid}' is stocked twice")
            listed.add(gid)
            f = row.get("requires_flag", "") if isinstance(row, dict) else ""
            if f and f not in refs["flags"]:
                errs.append(f"{sw}: undeclared story flag '{f}' on '{gid}'")
    return errs


def check_items(files: dict[str, object], flags: set[str], rep: Report) -> list[str]:
    """Validates game/data/items/*.json. Returns *_key values for loc checks."""
    docs = {t: files.get(f"{ITEMS_DIR}/{t}.json") for t in ITEM_TABLES}
    if all(d is None for d in docs.values()):
        return []
    statuses = files.get("game/data/battle/statuses.json")
    rows = statuses.get("statuses", []) if isinstance(statuses, dict) else []
    rows = [r for r in rows if isinstance(r, dict)]
    refs = {
        "characters": _ids(files, "game/data/battle/characters.json", "characters"),
        "statuses": {r.get("id") for r in rows},
        "harmful": {r.get("id") for r in rows if r.get("category") == "harmful"},
        "beneficial": {r.get("id") for r in rows if r.get("category") == "beneficial"},
        "facets": _ids(files, FACETS_FILE, "facets"),
        "flags": flags,
    }
    for e in items_errors(docs, refs):
        rep.err(e)
    return collect_keys([d for d in docs.values() if d is not None])


def declared_flags_quiet(root: Path) -> set[str]:
    """Declared flag names without re-reporting flags.tres problems (check_flags owns those)."""
    return load_flags(root, Report())


def run(root: Path) -> Report:
    rep = Report()
    files = load_json_files(root, rep)
    data_keys = check_battle(files, rep)
    data_keys += check_dialogue(root, files, rep)
    data_keys += check_progression(files, rep)
    data_keys += check_items(files, declared_flags_quiet(root), rep)
    data_keys += collect_keys({k: v for k, v in files.items() if k.startswith("game/data/settings/")})
    data_keys += check_locations(root, files, rep)
    data_keys += check_swell(files, rep)
    check_loc(root, data_keys, load_loc_keys(root, rep), rep)
    check_flags(root, load_flags(root, rep), rep)
    check_undertow(root, files, rep)
    check_provenance(root, rep)
    check_banned(root, rep)
    check_binary_sizes(root, rep)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = ap.parse_args()
    rep = run(args.root)
    for w in rep.warnings:
        print(f"WARN  {w}")
    for e in rep.errors:
        print(f"ERROR {e}")
    print(f"validate_data: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


# --- M1-ARC-06: location registry, party rest rules, shrine instances --------------------------

LOCATIONS_FILE = "game/data/world/locations.json"
PARTY_REST_FILE = "game/data/world/party_rest.json"
SHRINE_SCENE = "res://game/world/save_shrine/save_shrine.tscn"
TSCN_HEADER_RE = re.compile(r"^\[node [^\]]*\]", re.M)
TSCN_ATTR_RE = re.compile(r'(\w+)=(?:"([^"]*)"|ExtResource\("([^"]+)"\))')
TSCN_EXT_RE = re.compile(r"^\[ext_resource [^\]]*\]", re.M)
TSCN_PROP_RE = re.compile(r'^(location_id|network_id) = &?"([^"]*)"', re.M)


def _tscn_attrs(header: str) -> dict[str, str]:
    return {k: (v or ref) for k, v, ref in TSCN_ATTR_RE.findall(header)}


def scene_spawns(text: str) -> set[str]:
    """Names of the nodes directly under the root's Spawns node in a .tscn's text."""
    out: set[str] = set()
    for m in TSCN_HEADER_RE.finditer(text):
        a = _tscn_attrs(m.group(0))
        if a.get("parent") == "Spawns" and a.get("name"):
            out.add(a["name"])
    return out


PLAYER_GROUP_RE = re.compile(r'^\[node [^\n]*groups=\[[^\]\n]*"player"', re.M)


PLACE_AT_RE = re.compile(r"^(?:static\s+)?func\s+place_at\s*\(", re.M)
PLAYER_SCENE_MAX_DEPTH = 8


def scene_has_player(text: str, scenes: dict[str, str] | None = None, scripts: dict[str, str] | None = None,
                     _depth: int = 0) -> bool:
    """True when WorldReturn.place_player can find a player in a .tscn (M1-ARC-11, review-sweep-G on
    ENV-04): a node named Player directly under the root, a node in group "player", or a root whose
    script defines place_at (the zone places its own player).
    M1-ARC-12 (review-sweep-H nit): instanced scenes count too. `scenes` maps res:// paths to .tscn
    text and `scripts` res:// paths to .gd text; with them, a node in group "player" inside any
    instanced sub-scene is found (place_player searches the group under the root), and an inherited
    scene (an instanced root) is judged by its base scene as well. A path missing from both maps is
    treated as having no player, so the rule stays conservative."""
    if _depth > PLAYER_SCENE_MAX_DEPTH:
        return False
    if PLAYER_GROUP_RE.search(text):
        return True
    ext: dict[str, str] = {}
    for m in TSCN_EXT_RE.finditer(text):
        a = _tscn_attrs(m.group(0))
        ext[a.get("id", "")] = a.get("path", "")
    for m in TSCN_HEADER_RE.finditer(text):
        a = _tscn_attrs(m.group(0))
        is_root = "parent" not in a
        if a.get("name") == "Player" and a.get("parent") == ".":
            return True
        if is_root and scripts and PLACE_AT_RE.search(scripts.get(ext.get(a.get("script", ""), ""), "")):
            return True
        sub = (scenes or {}).get(ext.get(a.get("instance", ""), ""))
        if sub is None:
            continue
        if is_root and scene_has_player(sub, scenes, scripts, _depth + 1):
            return True
        if not is_root and _scene_in_player_group(sub, scenes, _depth + 1):
            return True
    return False


def _scene_in_player_group(text: str, scenes: dict[str, str] | None, depth: int) -> bool:
    """True when a node of this scene, or of a scene it instances, is in group "player"."""
    if depth > PLAYER_SCENE_MAX_DEPTH:
        return False
    if PLAYER_GROUP_RE.search(text):
        return True
    ext = {a.get("id", ""): a.get("path", "") for a in (_tscn_attrs(m.group(0)) for m in TSCN_EXT_RE.finditer(text))}
    for m in TSCN_HEADER_RE.finditer(text):
        sub = (scenes or {}).get(ext.get(_tscn_attrs(m.group(0)).get("instance", ""), ""))
        if sub is not None and _scene_in_player_group(sub, scenes, depth + 1):
            return True
    return False


def shrine_instances(text: str) -> list[dict[str, str]]:
    """SaveShrine instances in a .tscn: [{node, location_id, network_id}] (empty values if unset)."""
    ids = set()
    for m in TSCN_EXT_RE.finditer(text):
        a = _tscn_attrs(m.group(0))
        if a.get("path") == SHRINE_SCENE:
            ids.add(a.get("id", ""))
    out: list[dict[str, str]] = []
    if not ids:
        return out
    for block in re.split(r"(?m)^(?=\[)", text):
        if not block.startswith("[node "):
            continue
        a = _tscn_attrs(block.split("\n", 1)[0])
        if a.get("instance") in ids:
            props = dict(TSCN_PROP_RE.findall(block))
            out.append({"node": a.get("name", ""), "location_id": props.get("location_id", ""),
                        "network_id": props.get("network_id", "")})
    return out


def _rest_errors(rest: object, statuses: set[str]) -> list[str]:
    w = PARTY_REST_FILE
    if not isinstance(rest, dict):
        return [f"{w}: must be an object"]
    errs: list[str] = []
    carried = rest.get("carried_statuses")
    cures = rest.get("shrine_cures")
    for key, val in (("carried_statuses", carried), ("shrine_cures", cures)):
        if not isinstance(val, list):
            errs.append(f"{w}: {key} must be a list")
            continue
        errs += [f"{w}: {key} has unknown status '{sid}'" for sid in val if sid not in statuses]
    if isinstance(carried, list) and isinstance(cures, list):
        errs += [f"{w}: shrine cure '{sid}' is never carried out of battle"
                 for sid in cures if sid in statuses and sid not in carried]
    if not _is_int(rest.get("carried_duration")):
        errs.append(f"{w}: carried_duration must be an integer")
    return errs


def locations_errors(doc: object, scenes: dict[str, str], loc: set[str], statuses: set[str],
                     rest: object, shrines: dict[str, list[dict[str, str]]],
                     scripts: dict[str, str] | None = None) -> list[str]:
    """Validates locations.json and party_rest.json. `scenes` maps res:// paths to .tscn text (a
    missing path means the scene does not exist); `shrines` maps a scene file to its SaveShrine
    instances (shrine_instances); `scripts` maps res:// paths to .gd text (scene_has_player)."""
    w = LOCATIONS_FILE
    if not isinstance(doc, dict):
        return [f"{w}: must be an object"]
    errs: list[str] = []
    locs: dict[str, dict] = {}
    rows = doc.get("locations") if isinstance(doc.get("locations"), list) else []
    for i, row in enumerate(rows):
        rw = f"{w}: locations[{i}]"
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            errs.append(f"{rw}: needs a string id")
            continue
        if row["id"] in locs:
            errs.append(f"{rw}: duplicate location id '{row['id']}'")
        locs[row["id"]] = row
        scene = row.get("scene")
        if not isinstance(scene, str) or scene not in scenes:
            errs.append(f"{rw}: scene '{scene}' does not exist")
        elif row.get("spawn") not in scene_spawns(scenes[scene]):
            errs.append(f"{rw}: spawn '{row.get('spawn')}' is not a node under Spawns in {scene}")
        playable = row.get("playable", True)
        if not isinstance(playable, bool):
            errs.append(f"{rw}: 'playable' must be true or false")
        elif (playable and isinstance(scene, str) and scene in scenes
              and not scene_has_player(scenes[scene], scenes, scripts)):
            errs.append(f"{rw}: {scene} has no player (a Player node under the root, a node in group "
                        f"\"player\" here or in an instanced scene, or a root script with place_at); mark a "
                        f"stand-in scene \"playable\": false")
        if row.get("name_key") not in loc:
            errs.append(f"{rw}: name_key '{row.get('name_key')}' has no localization entry")
    if not locs:
        errs.append(f"{w}: 'locations' must list at least one location")

    def point(where: str, lid: object, spawn: object) -> None:
        if lid not in locs:
            errs.append(f"{where}: unknown location '{lid}'")
            return
        scene = locs[str(lid)].get("scene")
        if spawn and scene in scenes and spawn not in scene_spawns(scenes[scene]):
            errs.append(f"{where}: spawn '{spawn}' is not a node under Spawns in {scene}")

    point(f"{w}: default_location", doc.get("default_location"), "")
    ng = doc.get("new_game") if isinstance(doc.get("new_game"), dict) else {}
    point(f"{w}: new_game", ng.get("location_id"), ng.get("spawn", ""))
    for where, lid in (("default_location", doc.get("default_location")), ("new_game", ng.get("location_id"))):
        if lid in locs and locs[str(lid)].get("playable", True) is False:
            errs.append(f"{w}: {where}: location '{lid}' is not playable (every fallback must have a player)")
    network: set[str] = set()
    for i, row in enumerate(doc.get("shrines") if isinstance(doc.get("shrines"), list) else []):
        rw = f"{w}: shrines[{i}]"
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            errs.append(f"{rw}: needs a string id")
            continue
        if row["id"] in network:
            errs.append(f"{rw}: duplicate shrine id '{row['id']}'")
        network.add(row["id"])
        point(rw, row.get("location_id"), row.get("spawn", ""))
    for path, found in sorted(shrines.items()):
        for s in found:
            sw = f"{path}: SaveShrine '{s['node']}'"
            if s["location_id"] and s["location_id"] not in locs:
                errs.append(f"{sw}: location_id '{s['location_id']}' is not in {w}")
            if s["network_id"] and s["network_id"] not in network:
                errs.append(f"{sw}: network_id '{s['network_id']}' has no 'shrines' row in {w}")
    return errs + _rest_errors(rest, statuses)


def check_locations(root: Path, files: dict[str, object], rep: Report) -> list[str]:
    """Validates the location registry and party rest rules (M1-ARC-06). The name keys are checked
    here, so it returns no extra loc keys."""
    doc = files.get(LOCATIONS_FILE)
    if doc is None:
        return []
    scenes: dict[str, str] = {}
    shrines: dict[str, list[dict[str, str]]] = {}
    for p in sorted((root / "game").rglob("*.tscn")):
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8")
        scenes["res://" + rel] = text
        found = shrine_instances(text)
        if found:
            shrines[rel] = found
    st = files.get("game/data/battle/statuses.json")
    ids = {r.get("id") for r in st.get("statuses", []) if isinstance(r, dict)} if isinstance(st, dict) else set()
    loc = load_loc_keys(root, Report())
    scripts = {"res://" + p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
               for p in sorted((root / "game").rglob("*.gd"))}
    for e in locations_errors(doc, scenes, loc, ids, files.get(PARTY_REST_FILE), shrines, scripts):
        rep.err(e)
    return []



# --- M1-RND-11: Undertow quality tiers (game/data/vfx/undertow.json) ----------------------------

UNDERTOW_FILE = "game/data/vfx/undertow.json"
UNDERTOW_TIERS = ("low", "medium", "high", "ultra")
UNDERTOW_BODIES = ("shells", "raymarch")
# = UndertowState.MAX_CURL_REUSE and the shader's hint_range(1, 8).
UNDERTOW_MAX_CURL_REUSE = 8
# The body include: its `#ifndef UNDERTOW_MAX_STEPS` default (a variant that defines none compiles
# that cap) and the march_steps uniform's hint_range floor are parsed from it, never copied
# (M1-RND-15, review-sweep-I on RND-11).
UNDERTOW_BODY_INC = "game/shaders/undertow/undertow_body.gdshaderinc"
UNDERTOW_STEP_CAP_RE = re.compile(r"#define UNDERTOW_MAX_STEPS (\d+)")
UNDERTOW_DEFAULT_CAP_RE = re.compile(r"#ifndef UNDERTOW_MAX_STEPS\s*\n\s*#define UNDERTOW_MAX_STEPS (\d+)")
UNDERTOW_STEPS_HINT_RE = re.compile(r"uniform int march_steps : hint_range\((\d+),\s*(\d+)\)")
IMPORT_SLICES_RE = re.compile(r"^slices/(horizontal|vertical)=(\d+)", re.M)


def _res_path(root: Path, res: str) -> Path:
    return root / res.removeprefix("res://")


def undertow_step_limits(root: Path) -> tuple[int, int] | None:
    """(march_steps floor from the uniform's hint_range, default UNDERTOW_MAX_STEPS) from the body
    include, or None when either cannot be parsed."""
    path = root / UNDERTOW_BODY_INC
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    cap = UNDERTOW_DEFAULT_CAP_RE.search(text)
    hint = UNDERTOW_STEPS_HINT_RE.search(text)
    if cap is None or hint is None:
        return None
    return int(hint.group(1)), int(cap.group(1))


def undertow_quality_errors(root: Path, doc: object, where: str = UNDERTOW_FILE) -> list[str]:
    """Tier params the storm reads at runtime: types, ranges, the compiled step cap, the noise."""
    if not isinstance(doc, dict):
        return [f"{where}: not an object"]
    errs: list[str] = []
    limits = undertow_step_limits(root)
    if limits is None:
        errs.append(f"{UNDERTOW_BODY_INC}: cannot parse the march_steps hint_range or the UNDERTOW_MAX_STEPS default")
    step_floor, default_cap = limits if limits is not None else (1, 0)
    quality = doc.get("quality", {})
    shaders = doc.get("shaders", {})
    if not isinstance(quality, dict) or not isinstance(shaders, dict):
        return errs + [f"{where}: quality and shaders must be objects"]
    if sorted(quality) != sorted(UNDERTOW_TIERS):
        errs.append(f"{where}: quality tiers must be exactly {', '.join(UNDERTOW_TIERS)}")
    for tier, t in quality.items():
        w = f"{where}: quality.{tier}"
        if not isinstance(t, dict):
            errs.append(f"{w} must be an object")
            continue
        body = t.get("body")
        if body not in UNDERTOW_BODIES:
            errs.append(f"{w}.body must be one of {UNDERTOW_BODIES}")
            continue
        steps = t.get("march_steps")
        if not _is_int(steps):
            errs.append(f"{w}.march_steps must be an int")
        elif body == "shells" and steps != 0:
            errs.append(f"{w}.march_steps must be 0 for the shell body")
        elif body == "raymarch":
            shader = shaders.get(f"body_{tier}", "")
            path = _res_path(root, shader) if shader else None
            if path is None or not path.is_file():
                errs.append(f"{w}: shaders.body_{tier} missing ({shader!r})")
            else:
                m = UNDERTOW_STEP_CAP_RE.search(path.read_text(encoding="utf-8"))
                cap = int(m.group(1)) if m else default_cap
                if not step_floor <= steps <= cap:
                    errs.append(
                        f"{w}.march_steps {steps} outside {step_floor}..{cap}"
                        " (the uniform's hint_range floor, the variant's UNDERTOW_MAX_STEPS)"
                    )
        if "curl_reuse" in t:
            r = t["curl_reuse"]
            if not _is_int(r) or not 1 <= r <= UNDERTOW_MAX_CURL_REUSE:
                errs.append(f"{w}.curl_reuse must be an int in 1..{UNDERTOW_MAX_CURL_REUSE}")
        if "temporal_jitter" in t and not isinstance(t["temporal_jitter"], bool):
            errs.append(f"{w}.temporal_jitter must be a bool")
    noise = doc.get("noise")
    if noise is not None and not isinstance(noise, dict):
        errs.append(f"{where}: noise must be an object")
    elif noise is not None:
        tex = str(noise.get("texture", ""))
        texels = noise.get("texels")
        if not tex or not _res_path(root, tex).is_file():
            errs.append(f"{where}: noise.texture missing ({tex!r})")
        if not _is_int(texels) or texels <= 0:
            errs.append(f"{where}: noise.texels must be a positive int")
        imp = _res_path(root, tex + ".import") if tex else None
        if imp is not None and imp.is_file() and _is_int(texels):
            slices = {k: int(v) for k, v in IMPORT_SLICES_RE.findall(imp.read_text(encoding="utf-8"))}
            if slices and slices.get("horizontal", 1) * slices.get("vertical", 1) != texels:
                errs.append(f"{where}: noise.texels {texels} != the 3D texture's slice count in {tex}.import")
    return errs


def check_undertow(root: Path, files: dict[str, object], rep: Report) -> None:
    if UNDERTOW_FILE not in files:
        # Invalid JSON is already reported by load_json_files; a missing file is an error too
        # (the storm cannot pick a tier without it).
        if not (root / UNDERTOW_FILE).is_file():
            rep.err(f"{UNDERTOW_FILE}: missing (the Undertow quality tiers)")
        return
    for e in undertow_quality_errors(root, files[UNDERTOW_FILE]):
        rep.err(e)


# --- M1-CMB-04: Swell gauges (game/data/battle/swell.json, formulas.md § Swell) ------------------

SWELL_FILE = "game/data/battle/swell.json"
SWELL_TRIGGERS = {"damage_taken", "damage_dealt", "ally_hurt", "heal_item"}
SWELL_INPUT_KINDS = {"timing_ring"}
SWELL_MIN_MODES = 3  # SPEC §6.2 / M1-CMB-04: at least three fill modes
RING_SEC_FIELDS = ("lead_in_sec", "beat_sec", "perfect_sec", "good_sec")


def _num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _swell_mode_errors(m: dict, w: str) -> list[str]:
    errs: list[str] = []
    if m.get("trigger") not in SWELL_TRIGGERS:
        errs.append(f"{w}: trigger must be one of {sorted(SWELL_TRIGGERS)}")
    if ("rate" in m) == ("flat" in m):
        errs.append(f"{w}: needs exactly one of 'rate' or 'flat'")
    for k in ("rate", "flat"):
        if k in m and not _pos_int(m[k]):
            errs.append(f"{w}: '{k}' must be a positive int")
    if not isinstance(m.get("starts_unlocked", False), bool):
        errs.append(f"{w}: starts_unlocked must be true or false")
    for k in ("name_key", "desc_key"):
        if not isinstance(m.get(k), str):
            errs.append(f"{w}: missing {k}")
    return errs


def _swell_input_errors(i: dict, w: str) -> list[str]:
    if i.get("kind") not in SWELL_INPUT_KINDS:
        return [f"{w}: kind must be one of {sorted(SWELL_INPUT_KINDS)}"]
    errs: list[str] = []
    if not _pos_int(i.get("beats")):
        errs.append(f"{w}: beats must be a positive int")
    for k in RING_SEC_FIELDS:
        if not _num(i.get(k)) or i[k] < 0:
            errs.append(f"{w}: '{k}' must be a number >= 0")
    if not _num(i.get("peak_at")) or not 0 < i["peak_at"] < 1:
        errs.append(f"{w}: peak_at must be a fraction in (0, 1)")
    if _num(i.get("perfect_sec")) and _num(i.get("good_sec")) and i["perfect_sec"] > i["good_sec"]:
        errs.append(f"{w}: perfect_sec must not exceed good_sec")
    grades = i.get("grades")
    if not isinstance(grades, dict) or set(grades) != {"perfect", "good", "miss"}:
        errs.append(f"{w}: grades must give perfect, good and miss")
    elif any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in grades.values()):
        errs.append(f"{w}: grade bonuses must be ints >= 0")
    return errs


def _swell_hero_errors(h: dict, w: str, skills: dict[str, dict], refs: dict[str, set[str]],
                       used: dict[str, str]) -> list[str]:
    errs: list[str] = []
    if h["id"] not in refs["characters"]:
        errs.append(f"{w}: not a character")
    if h.get("input") not in refs["inputs"]:
        errs.append(f"{w}: unknown input '{h.get('input')}'")
    techs = h.get("techniques")
    if not isinstance(techs, list) or not techs:
        return errs + [f"{w}: needs at least one technique"]
    for t in techs:
        if t not in skills:
            errs.append(f"{w}: technique '{t}' is not a skill")
        elif skills[t].get("swell") is not True:
            errs.append(f"{w}: technique '{t}' must be a skills.json row with swell: true")
        elif t in used:
            errs.append(f"{w}: technique '{t}' already belongs to {used[t]}")
        else:
            used[t] = h["id"]
    return errs


def swell_errors(doc: object, skills: dict[str, dict], char_ids: set[str]) -> list[str]:
    """Errors in swell.json against the skill rows (by id) and the hero ids."""
    w0 = SWELL_FILE
    root = doc.get("swell") if isinstance(doc, dict) else None
    if not isinstance(root, dict):
        return [f"{w0}: missing top-level object 'swell'"]
    errs: list[str] = []
    modes = _rows(root, "modes", w0, errs)
    inputs = _rows(root, "inputs", w0, errs)
    heroes = _rows(root, "heroes", w0, errs)
    if len(modes) < SWELL_MIN_MODES:
        errs.append(f"{w0}: needs at least {SWELL_MIN_MODES} fill modes, found {len(modes)}")
    for m in modes:
        errs += _swell_mode_errors(m, f"{w0}: modes.{m['id']}")
    default = root.get("default_mode")
    unlocked = {m["id"] for m in modes if m.get("starts_unlocked") is True}
    if default not in {m["id"] for m in modes}:
        errs.append(f"{w0}: default_mode '{default}' is not a mode")
    elif default not in unlocked:
        errs.append(f"{w0}: default_mode '{default}' must start unlocked")
    for i in inputs:
        errs += _swell_input_errors(i, f"{w0}: inputs.{i['id']}")
    used: dict[str, str] = {}
    refs = {"characters": char_ids, "inputs": {i["id"] for i in inputs}}
    for h in heroes:
        errs += _swell_hero_errors(h, f"{w0}: heroes.{h['id']}", skills, refs, used)
    for sid, row in skills.items():
        if row.get("swell") is True and sid not in used:
            errs.append(f"skills.{sid}: a Swell row that no hero in {w0} lists")
    return errs


def _learned_skills(files: dict[str, object]) -> set[str]:
    out: set[str] = set()
    for rel, table in (("game/data/battle/characters.json", "characters"),
                       ("game/data/battle/enemies.json", "enemies")):
        doc = files.get(rel)
        for r in doc.get(table, []) if isinstance(doc, dict) else []:
            if isinstance(r, dict):
                out |= {s for s in r.get("skills", []) if isinstance(s, str)}
    return out


def check_swell(files: dict[str, object], rep: Report) -> list[str]:
    """Validates swell.json (M1-CMB-04). Returns its *_key values for the loc check."""
    doc = files.get(SWELL_FILE)
    if doc is None:
        rep.err(f"{SWELL_FILE}: missing")
        return []
    sk = files.get("game/data/battle/skills.json")
    rows = sk.get("skills", []) if isinstance(sk, dict) else []
    skills = {r["id"]: r for r in rows if isinstance(r, dict) and isinstance(r.get("id"), str)}
    for e in swell_errors(doc, skills, _ids(files, "game/data/battle/characters.json", "characters")):
        rep.err(e)
    for sid in sorted(_learned_skills(files)):
        if skills.get(sid, {}).get("swell") is True:
            rep.err(f"skills.{sid}: a Swell technique is never learned (a character or enemy lists it)")
    return collect_keys(doc)


if __name__ == "__main__":
    sys.exit(main())
