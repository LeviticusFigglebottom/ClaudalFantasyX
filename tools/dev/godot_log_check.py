#!/usr/bin/env python3
"""Script-error check for Godot logs, used by tools/ci_local.sh (M1-QA-06).

    python3 tools/dev/godot_log_check.py tests  <log>   # the test run: only real script errors
    python3 tools/dev/godot_log_check.py import <log>   # the import: script errors AND broken resources

Prints the offending lines and exits 1 when there are any, else exits 0.

Why it is not a plain `grep "Parse Error"`: Godot prints "Parse Error" for a torn *text resource*
too, as "ERROR: res://x.tres:6 - Parse Error: Expected ','." A test that deliberately loads a torn
.tres (save recovery, data integrity) then failed the whole gate. Measured on 4.6.3 (2026-10-23):
  - a GDScript parse error:  "SCRIPT ERROR: Parse Error: <msg>", then "at: GDScript::reload (res://<f>.gd:<n>)",
                             then "ERROR: Failed to load script "res://<f>.gd" with error "Parse error"."
  - a torn text resource:    "ERROR: <path>.tres:<n> - Parse Error: <msg>", then "Failed loading resource: <path>".
So in a test log a "Parse Error" counts only on a SCRIPT ERROR line or a line that names a .gd file.
The import log stays strict: a torn resource *in the repository* is a real error there.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_ERROR = re.compile(r"SCRIPT ERROR|Failed to load script")
PARSE_ERROR = re.compile(r"Parse Error", re.IGNORECASE)
GD_PATH = re.compile(r"\b(?:res|user)://\S*?\.gd\b|\S+\.gd:\d+")
# Import-only: a resource that fails to parse or load while the project imports.
RESOURCE_ERROR = re.compile(r"Failed loading resource|Parse Error")


def script_errors(lines: list[str]) -> list[str]:
    """Lines that report a GDScript error (never a text-resource parse error)."""
    out = []
    for line in lines:
        if SCRIPT_ERROR.search(line):
            out.append(line)
        elif PARSE_ERROR.search(line) and GD_PATH.search(line):
            out.append(line)
    return out


def import_errors(lines: list[str]) -> list[str]:
    """Script errors plus any resource that fails to parse or load during the import."""
    return [line for line in lines if SCRIPT_ERROR.search(line) or RESOURCE_ERROR.search(line)]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2 or args[0] not in ("tests", "import"):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    lines = Path(args[1]).read_text(encoding="utf-8", errors="replace").splitlines()
    bad = script_errors(lines) if args[0] == "tests" else import_errors(lines)
    for line in bad:
        print(line)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
