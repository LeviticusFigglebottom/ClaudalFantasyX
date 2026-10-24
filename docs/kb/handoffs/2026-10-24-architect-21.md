# Handoff: 2026-10-24, architect (m2-slice), M2-ARC-04

## Done
- M2-ARC-04 (release blocker): a release export leaves out `game/levels/_tests/*`, but shipped code still depended on three things there. I moved them with `git mv`:
  - `lagoon_waves.tres` → `game/world/water/`
  - `vegetation_plant.gd` and `vegetation_scatter.gd` (with their uids) → `game/world/vegetation/`
  - `asha_face_poses.json` → `game/data/cutscene/`
- Updated every user: `haluna_dressing.tscn`, `sequencer.json`, the `_tests` wrapper scenes, the unit and integration tests, the tools tests, `saltgrass.py`, and the docs.
- Recorded the new paths in ownership.md (water, Character, Environment).
- Guard: `tools/tests/test_release_excludes_tests.py`. I checked it catches a planted path and a planted class use.
- Release-set simulation (the "Windows Desktop" exclude set, imported in a scratch project): 0 script, compile or load errors.

## In progress
- Nothing.

## Exact next step
- Architect reviews the task.
- PC runs a real `godot --export-release "Windows Desktop"` and boots into Haluna.

## Known issues
- The prologue logs a `haluna.tscn` parse error at shutdown under `--quit-after`: the router's threaded load is cancelled. The integration branch does the same; it isn't a release issue.
- ALLOWED keeps two shipped files that name `_tests` paths:
  - `prewarm_materials.json`, whose scenes lists are filters only;
  - the `locations.json` field_test row, reached only by tests and the debug overlay.

## Files touched
- The moved files above, `docs/kb/ownership.md`, `tools/tests/test_release_excludes_tests.py`, the M2-ARC-04 task file, and the reference rewrites listed in its Notes.

## Gates
- All passed: lint and format, validate_data, taskboard, the full Godot suite (1516 run, 0 failed), and tools unittest.
- Shots: 26 pass against the baselines. The 13 nonzero ones are byte-identical to a pre-move (1bea1da) capture.
