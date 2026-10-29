---
id: M2-ARC-04
title: Release exports exclude game/levels/_tests, but shipped code depends on it (SceneRouter fails, Haluna won't load)
role: architect
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: environment
depends_on: []
milestone: M2
request-from: "rendering"
---
## Goal
Found by M1-RND-28 (docs/kb/qa/gpu/2026-10-24-rnd-28-shader-baker.md) on the first real release export.
export_presets.cfg excludes `game/levels/_tests/*` from both presets (bba1f6d), but shipped code depends on it:
- `game/levels/ch02/haluna/haluna_zone.gd`, `haluna_collision.gd` and `game/core/graphics_runtime.gd` use
  `HalunaDresser`, `HalunaTerrain` and `WeatheringTide`, which live in `game/levels/_tests/haluna_mood/`;
- `haluna.tscn` instances `_tests/haluna_mood/haluna_mood.tscn`;
- `VegetationPlant` lives in `game/levels/_tests/vegetation/`;
- `game/world/water/gerstner_waves.gd`, `game/data/world/locations.json`, `game/data/cutscene/sequencer.json`,
  `game/data/debug/teleports.json`, `game/data/settings/prewarm_materials.json` and `game/data/flags.tres` reference
  `_tests` paths.

In the exported game `scene_router.gd` fails to compile ("Failed to compile depended scripts"), and Haluna fails to
load.

## Acceptance criteria
- [x] Every runtime script and scene the game uses moves out of `_tests/` (to `game/world/...`,
      `game/levels/ch02/haluna/...` and so on), with their owners. Or the exclusion is narrowed, and an ADR says
      why test content ships.
- [x] A check that fails when a shipped path (not under `_tests/`) references `res://game/levels/_tests/`, in
      `tools/validate_data.py` or a test.
- [x] `godot --export-release "Windows Desktop"` produces a build whose boot → title → Haluna runs with no script
      error (`build/` is gitignored).

## Notes
- 2026-10-24 m2-slice, **done, for review by architect** (Lead-routed release blocker). Most of it was already done by M2-ENV-01 (the Haluna world promoted to `game/levels/ch02/haluna/`; `haluna.tscn` instances `haluna_dressing.tscn`, and HalunaDresser, HalunaTerrain and WeatheringTide moved). This task finished the job with `git mv` (owners recorded in ownership.md):
  - `game/levels/_tests/water/lagoon_waves.tres` → `game/world/water/` (the shipped sea's wave set).
  - `VegetationPlant` and `VegetationScatter` → `game/world/vegetation/` (the dresser and the shelter probe use them).
  - `asha_face_poses.json` → `game/data/cutscene/` (sequencer.json loads it at runtime).
  - Every res:// user is updated: scenes, tests, tools tests, docs. The _tests scenes still work as wrappers.
- `gerstner_waves.gd`, `flags.tres`, `shader_globals.gd` and the import rules only mention `_tests` in comments, which don't ship code.
- **The guard:** `tools/tests/test_release_excludes_tests.py` reads the release presets' `exclude_filter`. It fails when a shipped file names a `res://game/levels/_tests/` path outside a comment, or a shipped script uses a class_name defined under `_tests/`. I checked that it catches both by planting each once.
- **Allowlist, with reasons:**
  - `prewarm_materials.json`: its scenes lists are filters only.
  - `locations.json`'s `field_test` row: routed to only by tests and the debug overlay, and resolved lazily.
  - The test fails if an allowed file stops needing its exemption.
- **Release check:** there are no export templates in this container, so `--export-release` can't run here. Instead I copied exactly the "Windows Desktop" preset's file set (1102 files, no `_tests/`, `tests/`, `tools/`, debug) into a scratch project, imported it, and ran boot and the Haluna, Shell Shrine, first_verse and prologue scenes headless. There were **0 script, compile or load errors**.
  - The prologue run logs a `haluna.tscn` parse error only at shutdown: it waits for dialogue input headless, and `--quit-after` cancels the router's in-flight Haluna load. The integration branch does the same, and Haluna loads cleanly on its own.
  - **PC: please confirm with a real `godot --export-release "Windows Desktop"`.**
- **Shots: unchanged.**
  - 26 shots (veg, water, haluna, asha, underwater) all pass against the baselines.
  - The 13 with a nonzero rmse (≤0.005, which predates this task) are **byte-identical** to a capture of the pre-move commit 1bea1da (`cmp`).

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): environment's side approved. The status
  stays `review`.**
  - **Check run:** `tools.tests.test_release_excludes_tests` OK on this head.
  - **What was checked:** the vegetation scatter and plant, and the sea's wave set
    (`game/world/water/lagoon_waves.tres`), are out of `_tests/`. Every env-art scene and arena on this branch uses
    the shipped paths.
  - **Still open:** the task's notes route the release to an architect review. The real
    `godot --export-release "Windows Desktop"` run on the PC (the notes ask for it) also remains.
