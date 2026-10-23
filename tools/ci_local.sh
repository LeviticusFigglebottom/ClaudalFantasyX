#!/usr/bin/env bash
# Runs every CI gate locally (mirrors .github/workflows/ci.yml). Exit 1 on the first failure.
# Godot: uses `godot` on PATH, or $GODOT. In the cloud sandbox, get it with
#   python3 tools/dev/fetch_godot.py   (see docs/kb/tech/engine.md)
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
T="timeout ${HYMN_STEP_TIMEOUT:-600}"
# Per-run log dir so parallel worktrees never clobber each other's logs.
export TMPDIR="${HYMN_LOG_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/hymn_ci.XXXXXX")}"
L="$TMPDIR"
# Per-run Godot user:// (saves, settings.cfg): parallel worktrees must not share app_userdata.
export XDG_DATA_HOME="$L/xdg_data"
mkdir -p "$XDG_DATA_HOME"
echo "logs: $L"   # no gate may hang forever

step() { printf '\n== %s\n' "$*"; }

step "Data validators";        python3 tools/validate_data.py
step "Tool unit tests";        python3 -m unittest discover -s tools/tests
step "Audio synth tests";       python3 -m unittest discover -s tools/audio/tests -p "test_*.py"
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
$T "$GODOT" --headless --path . --import > $L/hymn_import_warm.log 2>&1 || true
$T "$GODOT" --headless --path . --import > $L/hymn_import.log 2>&1 || true
if grep -E "SCRIPT ERROR|Parse Error|Failed to load script|Failed loading resource" $L/hymn_import.log; then
  echo "Import reported errors (full log: $L/hymn_import.log)"; exit 1
fi
step "Godot tests"
$T "$GODOT" --headless --path . res://tests/run_tests.tscn 2>&1 | tee $L/hymn_tests.log | grep -E "FAIL|Tests:"
if grep -E "SCRIPT ERROR|Parse Error" $L/hymn_tests.log; then echo "Script errors during tests"; exit 1; fi
grep -q "Tests: .* 0 failed" $L/hymn_tests.log
step "Coverage gate: battle/ + progression/ (ADR 0013)"
cov_t0=$SECONDS
python3 tools/coverage/run_coverage.py --godot "$GODOT" --compare-log $L/hymn_tests.log
echo "coverage step: $((SECONDS - cov_t0))s"
step "Boot scene smoke test (60 frames)"
$T "$GODOT" --headless --path . --quit-after 60 > $L/hymn_boot.log 2>&1
if grep -E "SCRIPT ERROR|ERROR" $L/hymn_boot.log; then echo "Boot scene errors"; exit 1; fi
step "Screenshot capture + regression (software Forward+, ADR 0009)"
set +e
# HYMN_SHOTS=id1,id2 restricts capture+compare to those shots. Worktree agents use it for the
# shots their change can affect; the Lead runs the full manifest on every merge (CLAUDE.md §3).
shot_args=()
if [ -n "${HYMN_SHOTS:-}" ]; then shot_args=(--shots "$HYMN_SHOTS"); echo "screenshots restricted to: $HYMN_SHOTS"; fi
timeout "${HYMN_CAPTURE_TIMEOUT:-3600}" tools/screenshots/capture.sh "${shot_args[@]}"
cap=$?
set -e
if [ "$cap" -eq 3 ]; then
  echo "SKIP screenshot regression: no render deps (python3 tools/dev/fetch_render_deps.py)"
elif [ "$cap" -ne 0 ]; then
  echo "Screenshot capture failed (log: ${TMPDIR:-/tmp}/hymn_capture.log)"; exit 1
else
  python3 tools/screenshots/compare.py "${shot_args[@]}"
fi
printf '\nAll local CI gates passed.\n'
