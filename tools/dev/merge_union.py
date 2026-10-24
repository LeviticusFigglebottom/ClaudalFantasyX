#!/usr/bin/env python3
"""Resolve the recurring append-only merge conflicts by union (CLAUDE.md §5 shared files).

During a conflicted `git merge`, run:  python3 tools/dev/merge_union.py
It resolves, if conflicted:
  tests/screenshots/shots.json            ours' shots, then theirs' new shots (ids unique)
  tests/screenshots/baselines/baselines.json  dict union (ours wins on equal keys)
  game/data/flags.tres                    union of the flags dictionary
  game/data/settings/prewarm_materials.json  materials list union by path
  assets/PROVENANCE.md, tools/banned_terms.txt
                                          line union: ours' lines, then theirs' new lines
  game/data/loc/*.csv                     keyed union: a key one side changed (against the merge
                                          base) takes that side's line in place; new keys append;
                                          a key both sides changed keeps ours and is reported
and `git add`s each. Anything else stays conflicted for a human/agent to resolve.
Order matters for screenshots: earlier shots are not shifted by later ones (ADR 0009).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

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


def union_flags(ours: str, theirs: str) -> str:
    """flags.tres keeps its `flags = {...}` block JSON-compatible (ADR 0007): merge the dicts."""
    import re
    pat = re.compile(r"^flags = (\{.*?^\})", re.S | re.M)
    mo, mt = pat.search(ours), pat.search(theirs)
    fo, ft = json.loads(mo.group(1)), json.loads(mt.group(1))
    for k, v in ft.items():
        fo.setdefault(k, v)
    body = "{\n" + ",\n".join(f"{json.dumps(k)}: {json.dumps(v)}" for k, v in fo.items()) + "\n}"
    return ours[: mo.start(1)] + body + ours[mo.end(1):]


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
        if path == JSON_SHOTS:
            o, t = json.loads(ours), json.loads(theirs)
            ids = {s["id"] for s in o["shots"]}
            o["shots"] += [s for s in t["shots"] if s["id"] not in ids]
            text = json.dumps(o, indent=2) + "\n"
        elif path == JSON_BASELINES:
            o, t = json.loads(ours), json.loads(theirs)
            for k, v in t.items():
                o.setdefault(k, v)
            text = json.dumps(dict(sorted(o.items())), indent=2) + "\n"
        elif path == PREWARM:
            o, t = json.loads(ours), json.loads(theirs)
            seen = {m["path"] for m in o["materials"]}
            o["materials"] += [m for m in t["materials"] if m["path"] not in seen]
            text = json.dumps(o, indent=2, ensure_ascii=False) + "\n"
        elif path == FLAGS_TRES:
            text = union_flags(ours, theirs)
        elif any(Path(path).match(g) for g in LINE_UNION_GLOBS):
            text, clashes = union_loc(stage(path, 1), ours, theirs)
            for k in clashes:
                print(f"BOTH CHANGED {path} {k}: kept ours; check theirs")
        elif path in LINE_UNION:
            text = union_lines(ours, theirs)
        else:
            left.append(path)
            continue
        Path(path).write_text(text)
        git("add", path)
        print(f"resolved {path}")
    for p in left:
        print(f"STILL CONFLICTED {p}")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
