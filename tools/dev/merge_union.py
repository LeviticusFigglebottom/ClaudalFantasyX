#!/usr/bin/env python3
"""Resolve the recurring append-only merge conflicts by union (CLAUDE.md §5 shared files).

During a conflicted `git merge`, run:  python3 tools/dev/merge_union.py
It resolves, if conflicted (each keyed file three-way against the merge base, by merge_keyed: a key only one
side changed takes that side's version in place, a key one side deleted and the other left alone is deleted, new
keys append, and a key both sides changed differently keeps ours and is reported; big15 lost battle-presentation's
settle_frames edits when only theirs' new ids were added):
  tests/screenshots/shots.json            shots by id: ours' order, then theirs' new shots (ids unique)
  tests/screenshots/baselines/baselines.json  dict by key (sorted)
  game/data/flags.tres                    the flags dictionary by key
  game/data/settings/prewarm_materials.json  materials list by path
  assets/PROVENANCE.md, tools/banned_terms.txt
                                          line union: ours' lines, then theirs' new lines
  game/data/loc/*.csv                     keyed union: a key one side changed (against the merge
                                          base) takes that side's line in place; new keys append;
                                          a key both sides changed keeps ours and is reported
and `git add`s each. Anything else stays conflicted for a human/agent to resolve.
Order matters for screenshots: earlier shots are not shifted by later ones (ADR 0009).
With several merge bases, git's recursive strategy hands stage 1 a virtual base that can hold its own conflict
markers (big17's shots.json). A keyed file whose base won't parse is merged against the real merge bases instead:
a side is unchanged when it equals any real base's version of the key (missing counts too), so a key only one side
moved off every base takes that side, and a key both moved off differently keeps ours and is reported.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

JSON_SHOTS = "tests/screenshots/shots.json"
JSON_BASELINES = "tests/screenshots/baselines/baselines.json"
FLAGS_TRES = "game/data/flags.tres"
PREWARM = "game/data/settings/prewarm_materials.json"
LINE_UNION = ("assets/PROVENANCE.md", "tools/banned_terms.txt")
LINE_UNION_GLOBS = ("game/data/loc/*.csv",)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def stage(path: str, n: int) -> str:
    return git("show", f":{n}:{path}")


def conflicted() -> list[str]:
    return [p for p in git("diff", "--name-only", "--diff-filter=U").splitlines() if p]


def union_lines(ours: str, theirs: str) -> str:
    seen = set(ours.splitlines())
    extra = [l for l in theirs.splitlines() if l not in seen and l.strip()]
    out = ours.rstrip("\n").splitlines() + extra
    return "\n".join(out) + "\n"


def _csv_key(line: str) -> str:
    return line.split(",", 1)[0]


def union_loc(base: str, ours: str, theirs: str) -> tuple[str, list[str]]:
    """Loc CSVs (one `KEY,text...` row per line): a plain line union keeps both versions of a key
    that one side edited, so validate_data then fails on a duplicate key. Returns (text, keys both
    sides changed differently, which keep ours)."""
    b = {_csv_key(l): l for l in base.splitlines() if l.strip()}
    t = {_csv_key(l): l for l in theirs.splitlines() if l.strip()}
    out, clashes, have = [], [], set()
    for line in ours.rstrip("\n").splitlines():
        k = _csv_key(line)
        have.add(k)
        if line.strip() and k in t and t[k] != line and k in b:
            if line == b[k]:
                line = t[k]  # only theirs changed it
            elif t[k] != b[k]:
                clashes.append(k)  # both changed it: keep ours
        out.append(line)
    out += [l for l in theirs.splitlines() if l.strip() and _csv_key(l) not in have]
    return "\n".join(out) + "\n", clashes


_MISSING = object()


def merge_keyed(base: dict, ours: dict, theirs: dict) -> tuple[dict, list[str]]:
    """Three-way merge of two keyed versions against their merge base (insertion order: ours', then theirs' new
    keys). Per key: unchanged by theirs -> ours (including ours deleting it); unchanged by ours -> theirs (including
    theirs deleting it); both changed the same way -> that; both changed differently -> ours, and the key is
    reported. Returns (merged, clashing keys)."""
    out: dict = {}
    clashes: list[str] = []
    for k in list(ours) + [k for k in theirs if k not in ours]:
        b, o, t = base.get(k, _MISSING), ours.get(k, _MISSING), theirs.get(k, _MISSING)
        o_kept, t_kept = b == o, b == t  # with several bases (Bases) both can hold while o != t: a clash
        if t is o or t == o or (t_kept and not o_kept):
            pick = o
        elif o_kept and not t_kept:
            pick = t
        else:
            pick = o
            clashes.append(str(k))
        if pick is not _MISSING:
            out[k] = pick
    return out, clashes


def _by(rows: list, key: str) -> dict:
    return {r[key]: r for r in rows}


def merge_rows(base: list, ours: list, theirs: list, key: str) -> tuple[list, list[str]]:
    """merge_keyed for a list of dicts identified by `key` (shots by id, materials by path)."""
    merged, clashes = merge_keyed(_by(base, key), _by(ours, key), _by(theirs, key))
    return list(merged.values()), clashes


_FLAGS_RE = r"^flags = (\{.*?^\})"


def _flags_of(text: str) -> dict:
    import re
    m = re.compile(_FLAGS_RE, re.S | re.M).search(text)
    return json.loads(m.group(1)) if m else {}


def union_flags(ours: str, theirs: str, base: str = "", base_flags: dict | None = None) -> tuple[str, list[str]]:
    """flags.tres keeps its `flags = {...}` block JSON-compatible (ADR 0007): merge the dicts three-way."""
    import re
    mo = re.compile(_FLAGS_RE, re.S | re.M).search(ours)
    b = base_flags if base_flags is not None else _flags_of(base)
    fo, clashes = merge_keyed(b, _flags_of(ours), _flags_of(theirs))
    body = "{\n" + ",\n".join(f"{json.dumps(k)}: {json.dumps(v)}" for k, v in fo.items()) + "\n}"
    return ours[: mo.start(1)] + body + ours[mo.end(1):], clashes


def base_stage(path: str) -> str:
    """The merge base's version (stage 1), or "" when both sides added the file."""
    try:
        return stage(path, 1)
    except subprocess.CalledProcessError:
        return ""


class Bases:
    """A key's versions in several merge bases (_MISSING where one lacks it): a side equal to any is unchanged."""

    def __init__(self, vals: list) -> None:
        self.vals = vals

    def __eq__(self, other: object) -> bool:
        return any(v is other or v == other for v in self.vals)

    __hash__ = None  # type: ignore[assignment]


def _real_bases() -> list[str]:
    try:
        return git("merge-base", "--all", "HEAD", "MERGE_HEAD").split()
    except subprocess.CalledProcessError:
        return []


def agreed(versions: list[dict]) -> dict:
    """Per key, the value every version agrees on, else Bases(each version's value, _MISSING where one lacks it)."""
    out: dict = {}
    for v in versions:
        for k in v:
            if k not in out:
                vals = [x.get(k, _MISSING) for x in versions]
                out[k] = vals[0] if all(x is vals[0] or x == vals[0] for x in vals) else Bases(vals)
    return out


def keyed_base(path: str, parse: Callable[[str], dict]) -> dict:
    """The merge base of `path` as a keyed dict: stage 1 parsed, or, when it won't parse (a virtual base with
    conflict markers), what the real merge bases agree on."""
    text = base_stage(path)
    try:
        return parse(text) if text.strip() else {}
    except (ValueError, KeyError, TypeError):
        pass
    versions: list[dict] = []
    for mb in _real_bases():
        try:
            t = git("show", f"{mb}:{path}")
        except subprocess.CalledProcessError:
            t = ""
        versions.append(parse(t) if t.strip() else {})
    print(f"VIRTUAL BASE {path}: unreadable stage 1; using what {len(versions)} real merge bases agree on")
    return agreed(versions)


def main() -> int:
    left = []
    for path in conflicted():
        known = path in (JSON_SHOTS, JSON_BASELINES, PREWARM, FLAGS_TRES) or path in LINE_UNION or any(
            Path(path).match(g) for g in LINE_UNION_GLOBS
        )
        if not known:  # binary baselines and code stay for a human/agent (and may not decode as text)
            left.append(path)
            continue
        ours, theirs = stage(path, 2), stage(path, 3)
        clashes: list[str] = []
        if path == JSON_SHOTS:
            o, t = json.loads(ours), json.loads(theirs)
            b = keyed_base(path, lambda x: _by(json.loads(x).get("shots", []), "id"))
            merged, clashes = merge_keyed(b, _by(o["shots"], "id"), _by(t["shots"], "id"))
            o["shots"] = list(merged.values())
            text = json.dumps(o, indent=2) + "\n"
        elif path == JSON_BASELINES:
            o, t = json.loads(ours), json.loads(theirs)
            o, clashes = merge_keyed(keyed_base(path, json.loads), o, t)
            text = json.dumps(dict(sorted(o.items())), indent=2) + "\n"
        elif path == PREWARM:
            o, t = json.loads(ours), json.loads(theirs)
            b = keyed_base(path, lambda x: _by(json.loads(x).get("materials", []), "path"))
            merged, clashes = merge_keyed(b, _by(o["materials"], "path"), _by(t["materials"], "path"))
            o["materials"] = list(merged.values())
            text = json.dumps(o, indent=2, ensure_ascii=False) + "\n"
        elif path == FLAGS_TRES:
            text, clashes = union_flags(ours, theirs, base_flags=keyed_base(path, _flags_of))
        elif any(Path(path).match(g) for g in LINE_UNION_GLOBS):
            text, clashes = union_loc(base_stage(path), ours, theirs)
        elif path in LINE_UNION:
            text = union_lines(ours, theirs)
        else:
            left.append(path)
            continue
        for k in clashes:
            print(f"BOTH CHANGED {path} {k}: kept ours; check theirs")
        Path(path).write_text(text)
        git("add", path)
        print(f"resolved {path}")
    for p in left:
        print(f"STILL CONFLICTED {p}")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
