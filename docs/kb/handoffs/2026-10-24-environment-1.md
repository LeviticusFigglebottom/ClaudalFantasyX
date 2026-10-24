# Handoff — environment — 2026-10-24 #1

Session: worktree-agent-a573ddba06eb06eb2 (branch `worktree-agent-a573ddba06eb06eb2`, off `claude/undertow-lead-handoff-423ixt` da9513b). Not pushed; the Lead merges.

## Done
- **M1-ENV-09 + M1-ENV-08 (LOD hole, double draw):** `VegetationPlant` now chains each LOD as the
  `visibility_parent` child of the next LOD in its chain (`VegetationPlant.lod_range`, `lod_mesh`). Godot draws a
  child only while its parent is hidden for being too close, so one range check decides each switch. The 45 m
  switch keeps its 2 m hysteresis on LOD1's begin margin. The 120 m switch into the faded LOD2 is a 118–122 m
  crossfade over the opaque LOD1. The final fade over 394–406 m is unchanged.
- **GPU proof:** `game/levels/_tests/vegetation/lod_sweep_probe.gd` (run it with godot-render, as described in its
  header) reads back three coloured probe LODs from a still camera and while sweeping in and out. The new code gives
  `LOD_SWEEP PASS`. The base code gives `FAIL 16`: a still camera drew no LOD at 44–47 m, sweeping in drew nothing
  at 119–120 m, and sweeping out drew both at 121–122 m.
- **Unit tests:** `tests/unit/test_vegetation_plant.gd` models Godot's range check as the probe measured it, and
  sweeps 0.5–390 m in 0.25 m steps with three camera histories, with the fade on and off. It also checks the
  parent chain (per base name), the final-cut fade, the sun re-probe, ShaderGlobals.reset, and that the vegetation
  scene leaves no stale sun.
- **ShaderGlobals:** `reset(name)` restores the project.godot default. `get_value` falls back to that default, and
  `default_value(name)` exists. A change notifies `LISTENERS_GROUP`. `vegetation_test.gd` and `haluna_mood.gd`
  restore their pinned globals through `reset`.
- **Shelter:** AUTO plants listen for the sun and re-probe on the next physics frame. They coalesce requests and
  skip changes under 0.5°. vegetation.md "Shelter" and "LODs" are updated.
- **Pre-existing bug fixed:** `vegetation_test.tscn` lacked `node_paths=PackedStringArray("sun_node")`, so
  `sun_node` was always null and the scene never wrote its sun. The vegetation shaders don't read
  `hymn_sun_direction`, so there's no visual change from this.
- Filed **M1-ENV-10**: the same hole in `haluna_dresser.gd` `instance_piece` and in `asset_import_rules.gd`
  `_apply_lod`, which Character + Tools owns.
- ENV-09 item 4 (the Haluna collision) is routed to the cloud track on `claude/m2-slice`, with a note in the task.

## In progress
- Nothing.

## Exact next step
- Rendering (or the Lead) reviews M1-ENV-08 and M1-ENV-09. Then the Lead re-approves the shot drift listed in
  M1-ENV-09's notes on lavapipe.

## Gate (ci_local, HYMN_SHOTS = 3 veg + 5 haluna, HYMN_SKIP_BLENDER=1)
- All steps passed up to the screenshots: 1298 Godot tests, 0 failed. Then `veg_beach_wide` FAILED at rmse
  0.03014. That's intended: the baseline is missing the centre-left palm at about 120 m because of the old hole, and
  the capture now draws it. **The Lead should re-approve it.** The other shots pass: veg_backlit_fronds 0,
  veg_frangipani_close 0, haluna_h01 0.00189, h02 0.00326, h03 0.00114, h04 0, h07 0.00075.

## Known issues
- `tests/screenshots/capture_setup.gd` (QA) still writes and restores shot `globals` with
  `RenderingServer.global_shader_parameter_set`. A shot that overrides `hymn_sun_direction` leaves ShaderGlobals
  stale. The fix is to use `ShaderGlobals.set_value` / `reset` there. It isn't my path, so it's left for QA.
- The 120 m crossfade is alpha-blended for 4 m, the way the final fade already was.

## Files touched
- game/levels/_tests/vegetation/vegetation_plant.gd, vegetation_test.gd, vegetation_test.tscn, lod_sweep_probe.gd (new)
- game/core/shader_globals.gd
- game/levels/_tests/haluna_mood/haluna_mood.gd (`_exit_tree` restore only)
- tests/unit/test_vegetation_plant.gd
- docs/kb/art/environments/vegetation.md
- docs/kb/tasks/M1/M1-ENV-08-*.md, M1-ENV-09-*.md, M1-ENV-10-*.md (new)
