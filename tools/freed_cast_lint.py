#!/usr/bin/env python3
"""Finds GDScript that casts a stored node before checking it is still alive (the human's "Trying to cast a freed
object" entering a fight, 2026-10-28).

`var x := <stored ref> as SomeType` followed within LOOKAHEAD lines by `is_instance_valid(x)` is the pattern: the
check comes too late, because `as` on a freed object is already a script error. Check the raw value first
(`if not is_instance_valid(raw): continue`), then cast.

    python3 tools/freed_cast_lint.py            # lists every hit; exit 1 on any hit not in KNOWN
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("game",)
LOOKAHEAD = 3
CAST = re.compile(r"^\s*var (\w+)\s*:?=\s*(.+?)\s+as\s+\w+\s*(#.*)?$")
## Hits already filed to their owners: "path:variable" -> the request task.
KNOWN: dict[str, str] = {
    "game/audio/footstep_audio.gd:mi": "M3-HER-1150",
    "game/vfx/revenant/revenant_tells.gd:light": "M3-HER-1152",
    "game/vfx/ebbing/ebbing_motes.gd:node": "M3-HER-1161",
}


def _stored(src: str) -> bool:
    """True when the cast source is a stored value (an element, a member), not a fresh call's result."""
    return "[" in src or src.startswith("_") or "(" not in src


def scan_text(text: str) -> list[tuple[int, str]]:
    """(1-based line, variable) for each cast checked for life only after the cast."""
    lines = text.split("\n")
    out: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        m = CAST.match(line)
        if m is None or not _stored(m.group(2)):
            continue
        var = m.group(1)
        check = re.compile(r"is_instance_valid\(\s*%s\s*\)" % re.escape(var))
        if any(check.search(nxt) for nxt in lines[i + 1 : i + 1 + LOOKAHEAD]):
            out.append((i + 1, var))
    return out


def scan(root: Path = ROOT) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    for d in SCAN_DIRS:
        for path in sorted((root / d).rglob("*.gd")):
            rel = path.relative_to(root).as_posix()
            for line, var in scan_text(path.read_text(encoding="utf-8")):
                hits.append((rel, line, var))
    return hits


def main() -> int:
    bad = 0
    for rel, line, var in scan():
        task = KNOWN.get("%s:%s" % (rel, var), "")
        print("%s:%d: '%s' is cast before is_instance_valid%s" % (rel, line, var, " (%s)" % task if task else ""))
        bad += 0 if task else 1
    print("freed_cast_lint: %d new hit(s)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
