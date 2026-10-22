#!/usr/bin/env bash
# Runs every CI gate locally (mirrors .github/workflows/ci.yml). Exit 1 on the first failure.
# Godot: uses `godot` on PATH, or $GODOT. In the cloud sandbox, get it with
#   python3 tools/dev/fetch_godot.py   (see docs/kb/tech/engine.md)
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
T="timeout ${HYMN_STEP_TIMEOUT:-600}"   # no gate may hang forever

step() { printf '\n== %s\n' "$*"; }

step "Data validators";        python3 tools/validate_data.py
step "Tool unit tests";        python3 -m unittest discover -s tools/tests
step "Task board";             python3 tools/taskboard.py --check > /dev/null
step "gdlint";                 gdlint game tests
step "gdformat --check";       gdformat -l 120 --check game tests
step "Screenshot manifest";    python3 tools/screenshots/compare.py --manifest-only

if ! command -v "$GODOT" > /dev/null; then
  echo "SKIP Godot steps: '$GODOT' not found (python3 tools/dev/fetch_godot.py)"; exit 1
fi
step "Godot import"
# Pass 1 warms the import cache: on a fresh checkout Godot loads project translations
# before the CSVs are imported and logs a spurious "Failed loading resource". Gate on pass 2.
$T "$GODOT" --headless --path . --import > /tmp/hymn_import_warm.log 2>&1 || true
$T "$GODOT" --headless --path . --import > /tmp/hymn_import.log 2>&1 || true
if grep -E "SCRIPT ERROR|Parse Error|Failed to load script|Failed loading resource" /tmp/hymn_import.log; then
  echo "Import reported errors (full log: /tmp/hymn_import.log)"; exit 1
fi
step "Godot tests"
$T "$GODOT" --headless --path . res://tests/run_tests.tscn 2>&1 | tee /tmp/hymn_tests.log | grep -E "FAIL|Tests:"
if grep -E "SCRIPT ERROR|Parse Error" /tmp/hymn_tests.log; then echo "Script errors during tests"; exit 1; fi
grep -q "Tests: .* 0 failed" /tmp/hymn_tests.log
step "Boot scene smoke test (60 frames)"
$T "$GODOT" --headless --path . --quit-after 60 > /tmp/hymn_boot.log 2>&1
if grep -E "SCRIPT ERROR|ERROR" /tmp/hymn_boot.log; then echo "Boot scene errors"; exit 1; fi
step "Screenshot capture + regression (software Forward+, ADR 0009)"
set +e
$T tools/screenshots/capture.sh
cap=$?
set -e
if [ "$cap" -eq 3 ]; then
  echo "SKIP screenshot regression: no render deps (python3 tools/dev/fetch_render_deps.py)"
elif [ "$cap" -ne 0 ]; then
  echo "Screenshot capture failed (log: ${TMPDIR:-/tmp}/hymn_capture.log)"; exit 1
else
  python3 tools/screenshots/compare.py
fi
printf '\nAll local CI gates passed.\n'
