# Handoff — environment — 2026-10-24 — M3-ENV-03 Terraces of Ash (Pemakar)

Worktree agent of the env-art session (`worktree-agent-a47682c2eedaa8e26`); it resumed the paused WIP of
`worktree-agent-a5692132254e05def` (merged first). Commits are local to its branch (not pushed). Task file:
docs/kb/tasks/M3/M3-ENV-03-terraces-of-ash.md (status review, reviewer rendering; the swap-in note for
m2-slice is in the task file, not in live/env-art.md).

## Done
- Kit `assets_src/environments/kits/pemakar/` → `assets/environments/kits/pemakar/`: 25 pieces with LOD
  chains, kit manifest, 8 maps, 27 materials written by script, 61 PROVENANCE rows. Blender job
  `pemakar_kit` (4 threads; 61 files byte-identical). Import kind `pemakar_kit` (rules + post-import script,
  LOD end 4,000 m), wired into every `.glb.import` by `pemakar_import_settings.py`; KINDS updated in both
  post-import tests; asset_import.md and ownership.md rows.
- Kit fixes: the massif's trench behind the town and its bulge through the treads (pemakar_skyline.py
  `massif_height`), a lumpier plume, Ashcrown's unused slot (`pemakar_common.prune_slots`).
- Preview `game/levels/_tests/pemakar_kit/` iterated on lavapipe: P01 is now the harbour view looking north
  (pemakar.md §5 and Revisions updated); pilgrims' stair, sea road and sea lights in the layout; plume
  shader fog-free with an ember vent and a dusk rim; fewer stars; graves turned toward the path; lights for
  P06-P08; P08 reframed on the copper vein.
- Tests: tools/tests/test_pemakar_kit.py (19), tests/unit/test_pemakar_kit_preview.gd (5).
- Baselines: `pemakar_p01_waterfall_of_fires`, `pemakar_p03_among_the_graves` (re-captured identical).

## In progress
- Nothing.

## Exact next step
- The env-art session merges this branch, deletes `.godot/imported/*.glb-*` for the Pemakar kit before
  `godot --headless --path . --import` (the known import gotcha: a cached import keeps the old post-import
  script), then Rendering reviews M3-ENV-03 (review request in the task file). After that, copy the swap-in
  note from the task file into live/env-art.md for m2-slice.

## Known issues
- `stair_cascade` is not built (pemakar.md Revisions). P05's wick flame reads as a white cone at 100 mm;
  P06's falling sheet is faint at night; the copper outcrop reads as a smooth boulder in P08. P02 and
  P05-P08 are composed and lit but not registered.
- The `ash_fall` swatch is still a proposal (pemakar.md §3) for the Art Director.
- The import kind touches the Character + Tools import area by the documented procedure (asset_import.md
  "A new category"); flagged for their sign-off in ownership.md.

## Files touched
- docs/kb/art/environments/pemakar.md, docs/kb/tasks/M3/M3-ENV-03-terraces-of-ash.md, this file,
  docs/kb/ownership.md (row), docs/kb/tech/asset_import.md (row)
- assets_src/environments/kits/pemakar/{pemakar_common,pemakar_skyline,pemakar_layout,pemakar_import_settings}.py,
  assets/environments/kits/pemakar/** (new), assets/PROVENANCE.md (rows), tools/dev/blender_builds.json (job)
- game/data/import/pemakar_kit.json, game/core/import/pemakar_kit_post_import.gd (new),
  tools/tests/test_post_import.py and tests/unit/test_post_import.gd (KINDS)
- game/levels/_tests/pemakar_kit/{pemakar_kit_preview.gd,.tscn,pemakar_preview_layout.json,
  pemakar_preview_moods.json,pemakar_night_environment.tres}, game/shaders/environment/env_ash_plume.gdshader
- tests/screenshots/shots.json (2 shots), tests/screenshots/baselines/baselines.json and the two PNGs,
  tools/tests/test_pemakar_kit.py, tests/unit/test_pemakar_kit_preview.gd
