---
id: M2-ARC-04
title: Release exports exclude game/levels/_tests, but shipped code depends on it (SceneRouter fails, Haluna won't load)
role: architect
status: todo
owner_session: ""
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
- [ ] Every runtime script and scene the game uses moves out of `_tests/` (to `game/world/...`,
      `game/levels/ch02/haluna/...` and so on), with their owners. Or the exclusion is narrowed, and an ADR says
      why test content ships.
- [ ] A check that fails when a shipped path (not under `_tests/`) references `res://game/levels/_tests/`, in
      `tools/validate_data.py` or a test.
- [ ] `godot --export-release "Windows Desktop"` produces a build whose boot → title → Haluna runs with no script
      error (`build/` is gitignored).

## Review log
