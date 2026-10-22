---
id: M1-ENV-02
title: Procedural palm, frangipani, and grass with wind shader
role: environment
status: review
owner_session: environment-stream-1
reviewer: rendering
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §7.4 vegetation.

## Acceptance criteria
- [x] L-system or Geometry Nodes generator in assets_src/environments/vegetation/ (stochastic parametric L-system for frangipani; seeded numpy generators for palm, saltgrass, beach vine; Blender 5.0.1 glTF export)
- [x] Wind shader with a global wind uniform (`hymn_wind` / `hymn_wind_time`, vertex-colour weights, Low tier variant)

## Notes
- Everything is documented in docs/kb/art/environments/vegetation.md: parameters, adding a species, the wind channel convention, LODs, budgets, and an honest quality assessment.
- Shots `veg_backlit_fronds`, `veg_frangipani_close`, `veg_beach_wide` (scene `game/levels/_tests/vegetation/vegetation_test.tscn`) have approved baselines.
- Follow-ups for other roles:
  - Rendering: map the Low preset to `vegetation_foliage_low.gdshader`.
  - Character/M1-ART-02: absorb `VegetationPlant` (material map + visibility-range LODs) into a vegetation post-import script.
  - QA: add a `tests/unit` compile test (for now, `tools/tests/test_vegetation.py` runs `vegetation_shader_check.gd` headless).

## Review log
