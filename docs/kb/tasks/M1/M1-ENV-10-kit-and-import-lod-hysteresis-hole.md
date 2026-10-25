---
id: M1-ENV-10
title: The same LOD hysteresis hole in the Haluna kit dresser and the import LOD rules
role: environment
status: review
owner_session: "env-art"
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
- [x] Both set `visibility_parent` from LOD n to LOD n+1, with the hysteresis on LOD n+1's begin margin only, as
      `VegetationPlant.lod_range` does (or call it).
- [x] A test for each, like `test_a_distance_sweep_draws_exactly_one_lod` in `tests/unit/test_vegetation_plant.gd`.
- [ ] The Character + Tools owner signs off on the `asset_import_rules.gd` change (their path). **Pending**: see Notes.
- [x] haluna_* shot drift listed for the Lead to re-approve.

## Notes
- Don't touch `game/levels/ch02/**`, which the cloud track on `claude/m2-slice` owns.
- `game/levels/_tests/vegetation/lod_sweep_probe.gd` is the GPU check. A copy that instances one kit piece would
  confirm the kit fix.

## Notes (2026-10-24, environment, env-art worktree agent-a7f7257f59099ea20)
- **One helper.** `LodChain` (`game/world/vegetation/lod_chain.gd`, moved there beside VegetationPlant for the release build, M2-ARC-04, static, with no scene or autoload
  dependency, so the editor's post-import pass can call it) now holds the chain rule that `VegetationPlant.lod_range`
  had: `range_for` (moved, same maths), `sibling` (moved from `lod_mesh`), and `apply`, which sets the range,
  margins and fade mode, and sets or clears `visibility_parent`. `VegetationPlant.lod_range`/`lod_mesh` delegate to
  it, so their behaviour is unchanged. Callers use the class_name only, so it survives M2-ARC-04 moving
  VegetationPlant.
- **Dresser** (`haluna_dresser.gd` `instance_piece`): it's a 3-line swap inside the mesh loop. `<piece>` (LOD0) is
  the visibility child of `<piece>-lod1`, with the 2 m hysteresis on LOD1's begin margin only. LOD1's range
  (75–2500 m from the layout, end margin 2 m) is unchanged. LOD0 keeps no margins, and its end is LodChain's loose
  bound.
- **Import rules** (`asset_import_rules.gd` `_apply_lod`): every authored chain in the kit and vegetation `.glb`s is
  chained the same way, with no fade. Single-LOD assets are untouched (the early return on `lod_chains` comes
  first, and `test_a_single_lod_mesh_gets_no_visibility_parent` covers it). LODs past the table are still hidden.
  The `asset_import.md` LOD sentence is updated to match.
- **Tests:** a shared model of Godot's range check, `tests/unit/lod_range_model.gd` (moved out of
  test_vegetation_plant.gd, which now uses it). `tests/unit/test_haluna_dresser_lod.gd`:
  `test_a_distance_sweep_draws_exactly_one_lod` (three real kit pieces, the layout switch and a 40 m per-placement
  override, still camera, sweeping in and sweeping out), `test_each_piece_lod0_is_the_visibility_child_of_lod1`, and
  `test_nothing_draws_past_the_last_lod`. `tests/unit/test_post_import.gd`: `test_a_distance_sweep_draws_exactly_one_lod`
  (haluna_kit and vegetation rules on in-memory chains, plus the imported fixture and `dock_haluna.glb`), and
  `test_a_single_lod_mesh_gets_no_visibility_parent`. The fixture, vegetation and no-chain range tests now assert
  LodChain's ranges and the parent. On the base code, the new sweeps fail: a still camera draws nothing at
  73.25–76.75 m (dresser, 75 m switch), 68.25–71.75 m (kit import) and 43.25–46.75 m (vegetation import).
- **GPU** (lavapipe): `game/levels/_tests/vegetation/kit_lod_sweep_probe.gd` colours `dock_haluna`'s LODs and counts
  pixels at 69–81 m (dresser) and 64–76 m (import alone), in 0.5 m steps, from a still camera and sweeping in and
  out. It gives `KIT_LOD_SWEEP PASS`, with exactly one LOD in every row.
- **Note on stale caches:** Godot doesn't reimport a `.glb` when only its post-import script changes. A checkout
  with an existing `.godot/` keeps the old import ranges until the kit and vegetation `.glb`s are reimported. A fresh
  import (CI, ci_local) is right. Runtime dressing (dresser, VegetationPlant) overrides the import anyway.
- **Shot drift** (lavapipe, `HYMN_SKIP_BLENDER=1`, HYMN_SHOTS = the five haluna shots + veg_beach_wide): only
  **haluna_h02_tidewall_lane** drifts, rmse **0.02753** (limit 0.008). It's the intended change: the capture now
  draws a tiled-roof house at the right edge (x about 880–950 px, behind the right wall's end) and a sliver of a far
  roof at the end of the left lane (x about 340–355 px). Both sat in the old 73–77 m still-camera hole. The Lead
  should re-approve. Within limits: haluna_h01 0.00189, h03 0.00114, h04 0.00000, h07 0.00075, veg_beach_wide
  0.00000. h01/h03/h07 match the values M1-ENV-09 recorded, so that's pre-existing drift.
  `haluna_h10_dock_night` doesn't exist on this branch.
- **m2-slice:** `instance_piece` is identical in `game/levels/ch02/haluna/haluna_dresser.gd` on `claude/m2-slice`
  (only the file offset differs, +57 lines). The same hunk applies there cleanly (checked with `patch`). The Lead
  applies it after merging m2-slice if the rename merge doesn't carry it. `test_haluna_dresser_lod.gd` and the probe
  look for the layout at either path.
- **Sign-off pending:** Character + Tools (owner of `game/core/import/**`, `tests/unit/test_post_import.gd`,
  `asset_import.md`) still has to sign off on the `_apply_lod` change. Reviewer: rendering.

## Merge notes (2026-10-24, env-art parent)
- Merged into claude/env-art. **Gotcha confirmed:** a checkout with an existing `.godot/` kept the old
  import ranges (3 `--filter=import` failures) until the `.glb` imports were deleted and re-imported
  (`rm .godot/imported/*.glb-*`, then `--import`): 19/19 after. The Lead's integration worktree needs the same.
- h02 re-approved together with M2-ENV-07's windbreak change (rmse 0.03102 on the merged tree, viewed).
- The patch for m2-slice's moved `game/levels/ch02/haluna/haluna_dresser.gd` (m2-slice OK'd env-art
  applying it) is applied when env-art next merges claude/m2-slice.

## Review log
