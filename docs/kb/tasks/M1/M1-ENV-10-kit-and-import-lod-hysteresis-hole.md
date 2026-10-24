---
id: M1-ENV-10
title: The same LOD hysteresis hole in the Haluna kit dresser and the import LOD rules
role: environment
status: todo
owner_session: ""
depends_on: [M1-ENV-09]
milestone: M1
request-from: "environment"
reviewer: rendering
---
## Goal
M1-ENV-09 found that two independent visibility ranges with `FADE_DISABLED` margins at one switch distance
leave a hole (a still camera within the margin draws neither mesh) and a double draw (the drawn one's range is
widened). It fixed `VegetationPlant` by chaining each LOD as the `visibility_parent` child of the next
(`VegetationPlant.lod_range`, `docs/kb/art/environments/vegetation.md` "One LOD at every distance"). Two other
places set up LOD ranges the old way:

- `game/levels/_tests/haluna_mood/haluna_dresser.gd` `instance_piece` (~:120-131): `<piece>` ends at
  `lod1_from_m` and `<piece>-lod1` begins there, each with `lod_margin_m` hysteresis.
- `game/core/import/asset_import_rules.gd` `_apply_lod` (~:200-215, owned by Character + Tools, M1-ART-02):
  the same pattern for `lods.end_m`/`margin_m` chains (`game/data/import/haluna_kit.json`, `vegetation.json`).

## Acceptance criteria
- [ ] Both set `visibility_parent` from LOD n to LOD n+1, with the hysteresis on LOD n+1's begin margin only, as
      `VegetationPlant.lod_range` does (or call it).
- [ ] A test for each, like `test_a_distance_sweep_draws_exactly_one_lod` in `tests/unit/test_vegetation_plant.gd`.
- [ ] The Character + Tools owner signs off on the `asset_import_rules.gd` change (their path).
- [ ] haluna_* shot drift listed for the Lead to re-approve.

## Notes
- Don't touch `game/levels/ch02/**`, which the cloud track on `claude/m2-slice` owns.
- `game/levels/_tests/vegetation/lod_sweep_probe.gd` is the GPU check. A copy that instances one kit piece would
  confirm the kit fix.

## Review log
