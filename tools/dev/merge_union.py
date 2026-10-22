#!/usr/bin/env python3
"""Resolve the recurring append-only merge conflicts by union (CLAUDE.md §5 shared files).

During a conflicted `git merge`, run:  python3 tools/dev/merge_union.py
It resolves, if conflicted:
  tests/screenshots/shots.json            ours' shots, then theirs' new shots (ids unique)
  tests/screenshots/baselines/baselines.json  dict union (ours wins on equal keys)
  assets/PROVENANCE.md, game/data/loc/*.csv, tools/banned_terms.txt
                                          line union: ours' lines, then theirs' new lines
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


def main() -> int:
    left = []
    for path in conflicted():
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
        elif path in LINE_UNION or any(Path(path).match(g) for g in LINE_UNION_GLOBS):
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
