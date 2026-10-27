# Handoff — environment (env-art) — 2026-10-24 — M2-ENV-12 gull normals

## Done
- **Fix at the source** (`assets_src/environments/kits/haluna/village.py`, `_loft`): the outward hint for
  `_orient_grid` was taken at column `sides // 4`, but `_orient_grid` measures the winding at the middle column
  `(sides + 1) // 2`, on the far side of the section. So every loft (body, neck, head, beak, wings, tail) was
  wound inside-out. The hint is now the measured point. The LOD lofts get smooth normals: they had all been +Y
  under `smooth=False`. The full mesh is unchanged by that because `_facet` recomputes its normals. `_loft` is
  used only by `lintel_gull`.
- `oruvel/ov_cabins._turn_lofts_outward` is now a no-op guard (signed volume is positive). I updated its
  docstring only.
- **Rebuilt, verified:** changed outputs are `haluna/lintel_gull_a|b|c.glb`, `brightwater_ferry/ferry_hull.glb`
  (stem-gull) and `oruvel/lintel_gull_open.glb`. All six jobs that source village.py (haluna, oruvel,
  brightwater_ferry, pemakar, corrow, ashcrown) are byte-identical after the rebuild.
- **Baseline:** `haluna_h03_lintel_gull` re-approved (rmse 0.04675; the drift is only the gull, now lit on its
  outer faces).
- **Manifest fix:** removed a stray `{}` job the Ashcrown merge left in `tools/dev/blender_builds.json`.
  `verify_blender_builds.py` could not load the manifest with it (KeyError 'id').
- Task M2-ENV-12 is in `review` (reviewer: rendering), with the full numbers in its Notes.

## In progress
- None.

## Exact next step
- Rendering reviews M2-ENV-12 (view `haluna_h03_lintel_gull` against the previous baseline).
- Separately, the baseline owners re-approve the stale shots below after viewing them.

## Known issues
- **Stale baselines on main (not this change):** `battle_arena_oruvel_raft_morning` (0.05175: creature models
  replace the placeholder enemies), `field_objective_line`, `field_interact_prompt`, `field_area_title` and
  `field_tip_card` (0.068), and `dialogue_continue` (0.057). In those five UI shots the Haluna tidewalls render
  wetter and darker. A control capture with the old gull glbs drifts the same, so the cause is upstream. I did
  not re-approve them.
- The beak lofts taper to 2 mm, so a few of their tip faces read ambiguously in an outwardness check. They
  render correctly.

## Gates
- gdlint and gdformat (clean); validate_data (0/0); taskboard --check (OK).
- tools unittests: test_haluna_kit, test_arenas, test_brightwater_ferry_kit and test_oruvel_kit (81 OK).
- Godot tests: `--filter=haluna` 49/0 and `--filter=arena` 13/0.
- verify_blender_builds for the six jobs above.
- Screenshots: the 17 shots that can show a gull piece were captured on lavapipe and compared.
- Skipped: coverage (nothing under game/battle or game/progression) and the full screenshot manifest.

## Files touched
- assets_src/environments/kits/haluna/village.py; assets_src/environments/kits/oruvel/ov_cabins.py (docstring)
- assets/environments/kits/haluna/lintel_gull_{a,b,c}.glb; assets/environments/kits/brightwater_ferry/ferry_hull.glb;
  assets/environments/kits/oruvel/lintel_gull_open.glb
- tests/screenshots/baselines/haluna_h03_lintel_gull.png
- tools/dev/blender_builds.json (the stray entry)
- docs/kb/tasks/M2/M2-ENV-12-haluna-gull-normals.md; this handoff
