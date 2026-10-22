#!/usr/bin/env bash
# Runs every CI gate locally (mirrors .github/workflows/ci.yml). Exit 1 on the first failure.
# Godot: uses `godot` on PATH, or $GODOT. In the cloud sandbox, get it with
#   python3 tools/dev/fetch_godot.py   (see docs/kb/tech/engine.md)
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"

step() { printf '\n== %s\n' "$*"; }

step "Data validators";        python3 tools/validate_data.py
step "Tool unit tests";        python3 -m unittest discover -s tools/tests
step "Task board";             python3 tools/taskboard.py --check > /dev/null
step "gdlint";                 gdlint game tests
step "gdformat --check";       gdformat -l 120 --check game tests
step "Screenshot regression";  python3 tools/screenshots/compare.py

if ! command -v "$GODOT" > /dev/null; then
  echo "SKIP Godot steps: '$GODOT' not found (python3 tools/dev/fetch_godot.py)"; exit 1
fi
step "Godot import"
"$GODOT" --headless --path . --import > /tmp/hymn_import.log 2>&1 || true
if grep -E "SCRIPT ERROR|Parse Error|Failed to load script|Failed loading resource" /tmp/hymn_import.log; then
  echo "Import reported errors (full log: /tmp/hymn_import.log)"; exit 1
fi
step "Godot tests"
"$GODOT" --headless --path . res://tests/run_tests.tscn 2>&1 | tee /tmp/hymn_tests.log | grep -E "FAIL|Tests:"
if grep -E "SCRIPT ERROR|Parse Error" /tmp/hymn_tests.log; then echo "Script errors during tests"; exit 1; fi
grep -q "Tests: .* 0 failed" /tmp/hymn_tests.log
step "Boot scene smoke test (60 frames)"
"$GODOT" --headless --path . --quit-after 60 > /tmp/hymn_boot.log 2>&1
if grep -E "SCRIPT ERROR|ERROR" /tmp/hymn_boot.log; then echo "Boot scene errors"; exit 1; fi
printf '\nAll local CI gates passed.\n'
