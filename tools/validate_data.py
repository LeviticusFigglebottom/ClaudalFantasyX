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


def run(root: Path) -> Report:
    rep = Report()
    files = load_json_files(root, rep)
    data_keys = check_battle(files, rep)
    data_keys += check_dialogue(root, files, rep)
    data_keys += check_progression(files, rep)
    data_keys += collect_keys({k: v for k, v in files.items() if k.startswith("game/data/settings/")})
    check_loc(root, data_keys, load_loc_keys(root, rep), rep)
    check_flags(root, load_flags(root, rep), rep)
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


if __name__ == "__main__":
    sys.exit(main())
