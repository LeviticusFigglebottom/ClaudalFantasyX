#!/usr/bin/env python3
"""Project data validator (SPEC §5.5). Exit code 1 on any error.

Checks:
  * every JSON file under game/data parses
  * battle tables: schema, unique ids, enums, dangling references
  * localization: every *_key / tr("KEY") / dialogue #line: key exists in a loc CSV
  * story flags: every flag used in .gd / .dlg is declared in game/data/flags.tres
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


def run(root: Path) -> Report:
    rep = Report()
    files = load_json_files(root, rep)
    data_keys = check_battle(files, rep)
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
