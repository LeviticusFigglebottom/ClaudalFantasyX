# 0006 — Test framework: in-repo minimal runner (not GUT or gdUnit4, for now)

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** all engineering roles, QA
- **Author role:** Lead

## Context
SPEC §4.3 allows GUT or gdUnit4. The bootstrap environment could not download addons (GitHub releases and the Asset Library were blocked), and vendoring a large addon without being able to pin and verify it is risky.

## Decision
Ship a ~150-line runner in `tests/`:
- `TestCase` (`tests/test_case.gd`): `assert_eq/ne/true/false/between`, and `before_each()`.
- `tests/run_tests.tscn`: discovers `tests/unit/test_*.gd` and `tests/integration/test_*.gd`, runs every `test_*` method, and exits 1 on failure. Filter with `-- --filter=<substring>`.
- `TestErrorCounter` (a Godot 4.5+ `Logger`) turns any script runtime error during a test into a failure, so a test that crashes partway can't pass silently. Deliberate `push_error()` calls in game code are not counted.

Command: `godot --headless --path . res://tests/run_tests.tscn`.

## Consequences
- No coverage reporting yet. **M1-QA-03** decides between adopting gdUnit4 (which has coverage tooling) or adding a coverage proxy. Until then, "coverage must not drop" in `battle/` and `progression/` is enforced in review: every public function needs at least one test.
- Migrating later to gdUnit4 is mechanical, since the assert names are close.
