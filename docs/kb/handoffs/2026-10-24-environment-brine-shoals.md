# Handoff — environment — 2026-10-24 — M3-ENV-02 Brine Shoals

Worktree agent of the env-art session, branched from `claude/env-art`; commits are local to its branch
(not pushed). Task file: docs/kb/tasks/M3/M3-ENV-02-brine-shoals.md (status review, reviewer rendering).

## Done
- Design notes `docs/kb/art/environments/brine_shoals.md` (first commit before geometry; revised after the
  preview: east-bank camp, hard +1.1 m, raid water −0.15 m, offshore wind toward 240°, B05 from astern).
- Kit `assets_src/environments/kits/brine_shoals/` → `assets/environments/kits/brine_shoals/`: 28 pieces with
  LOD chains (ground cells, channel cells, apron, hard, tideline, lamp burial, plank walk, five wrecks, five camp
  pieces intact + burned, brazier, Liss's crate, smoke plume, white barge), three maps, 26 materials. Blender
  job `brine_shoals_kit` (61 files byte-identical), import category `brine_shoals_kit`, PROVENANCE rows.
- Preview `game/levels/_tests/brine_shoals_kit/` (BrineShoalsPreview rig, ch06 environment + LUT, still
  `silted_flats` water, generated layout, 8 cameras, preview manifest); shader
  `game/shaders/environment/env_smoke_plume.gdshader`; baselines `brine_b01_arrival`, `brine_b05_barge_channel`.
- Tests: tools/tests/test_brine_shoals_kit.py (20), tests/unit/test_brine_shoals_preview.gd (5).
- Swap-in note for m2-slice in docs/kb/handoffs/live/env-art.md; request M3-RND-21 (smoke column).

## In progress
- Nothing.

## Exact next step
- The env-art session merges this branch into `claude/env-art` (after merging, delete
  `.godot/imported/*.glb-*` for the new kit and the import probe before `--import`, the known import gotcha),
  then the Rendering review of M3-ENV-02.

## Known issues
- Smoke is a stand-in column (M3-RND-21). Creek rims flash pale from high cameras (B10). Tent LOD1 is two
  slopes. The barge has no pole-men.
- The import category touched files in the Character + Tools import area by the documented procedure
  (asset_import.md "A new category"); flag for their review.

## Files touched
- docs/kb/art/environments/brine_shoals.md, docs/kb/tasks/M3/M3-ENV-02-brine-shoals.md,
  docs/kb/tasks/M3/M3-RND-21-shoals-smoke-column.md, docs/kb/handoffs/live/env-art.md, this file,
  docs/kb/ownership.md (row), docs/kb/tech/asset_import.md (row)
- assets_src/environments/kits/brine_shoals/** (new), assets/environments/kits/brine_shoals/** (new),
  assets/PROVENANCE.md (rows), tools/dev/blender_builds.json (job)
- game/data/import/brine_shoals_kit.json, game/core/import/brine_shoals_kit_post_import.gd (new),
  tools/tests/test_post_import.py and tests/unit/test_post_import.gd (KINDS)
- game/levels/_tests/brine_shoals_kit/** (new), game/shaders/environment/env_smoke_plume.gdshader (new)
- tests/screenshots/shots.json (2 shots), tests/screenshots/baselines/brine_b01_arrival.png,
  brine_b05_barge_channel.png, tools/tests/test_brine_shoals_kit.py, tests/unit/test_brine_shoals_preview.gd
