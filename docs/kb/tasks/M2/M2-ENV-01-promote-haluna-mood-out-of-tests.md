---
id: M2-ENV-01
title: Promote the Haluna mood scene's shared content out of _tests/ before content lock
role: environment
status: done
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-04]
reviewer: environment
milestone: M2
request-from: "qa"
---
## Goal
The playable zone `ch02/haluna` (game/levels/ch02/haluna/haluna.tscn) instances
`game/levels/_tests/haluna_mood/haluna_mood.tscn`, so its dressing, its sea (the `hymn_water_level`
publisher), its shrine (`haluna_shrine`) and its `WeatheringTide` live in a test folder. A change made
for a mood shot can then break the shipped zone without anyone noticing (M1-ENV-06 review-sweep-L nit,
carried by M1-NIT-02; docs/kb/tech/architecture.md "Location registry").

## Acceptance criteria
- [x] The shared content moves to `game/levels/ch02/haluna/` (for example `haluna_dressing.tscn` and its scripts), and `haluna.tscn` instances that, not anything under `_tests/`.
- [x] `haluna_mood.tscn` stays as a thin test wrapper (the shot cameras and capture setup) around the promoted scene.
- [x] The five `haluna_*` shots re-render byte-identical, or any difference is explained and accepted by Rendering.
- [x] locations.json, `SaveShrine` ids, ownership.md globs and PROVENANCE paths follow the move. `validate_data`, `--filter=haluna` and `--filter=world_return` pass.
- [x] Done before content lock.

## Notes
- 2026-10-24 m2-slice: the Lead assigned this to the m2-slice track (queue top-up, item c, 00:40), since the playable zone is this track's. It touches Environment's `_tests/haluna_mood/**` claim: files move with `git mv`, so in-flight edits merge through rename detection.

- 2026-10-24 m2-slice, **done, for review by environment** (and Rendering for the noon environment's new path):
  - **The world:** `game/levels/ch02/haluna/haluna_dressing.tscn` holds the environment, sun, sea, tide, terrain, dresser, spawns and the `haluna_shrine` SaveShrine. `haluna.tscn` instances it (node still `HalunaMood`).
  - **Moved with `git mv`:** haluna_mood.gd (`HalunaMood`), haluna_dresser.gd, haluna_terrain.gd, weathering_tide.gd, haluna_layout.json, haluna_noon_environment.tres, haluna_water_material.tres and lut_ch02_noon.png (with its .import), each with its .uid.
  - **The wrapper:** `_tests/haluna_mood/haluna_mood.tscn` inherits the dressing and adds only `Cameras/H01…H07`, so `shots.json`, the prewarm scene lists and the GPU probes are unchanged.
  - **Shots:** the five `haluna_*` shots render **byte-identical** (before from a clean worktree of the pre-move head, after from the moved tree, both on lavapipe).
  - **Path updates:** the dresser's default `layout_path`, `zone_lut.py`'s output path, test_environment_shaders, test_haluna_shrine (now loads the shipped dressing), both READMEs, and ownership.md (Environment keeps the promoted world files).
  - **Dead code:** removed `HalunaZone._release_mood_cameras` (the dressing has no cameras).
  - **Unchanged:** locations.json and the SaveShrine id, location and network id.
  - **Not moved:** `game/levels/_tests/water/lagoon_waves.tres`, the sea's wave set. It is shared with the water test scenes and owned by water/rendering, so a follow-up should promote it.

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **What was checked:** the world lives in `game/levels/ch02/haluna/haluna_dressing.tscn`, `haluna.tscn`
    instances it, and no shipped scene or script under ch02 reaches into `_tests/haluna_mood` (only the README
    mentions it).
  - **Checks run:** `--filter=world_return` 17/0 and `--filter=haluna` 62/0 (both this evening).
  - **Shots:** the Haluna shots were re-approved after viewing today; their drift is env-art's own palms and
    chapel, not the move.
  - **Follow-up:** `lagoon_waves.tres` stays in `_tests/water` (water/rendering's, as noted). Done.
