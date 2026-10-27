# Handoff — environment (env-art worker, M3-ENV-09) — 2026-10-24 (Ashcrown)

## Done
- **M3-ENV-09 Ch5 Ashcrown temple**, now `status: review` (reviewer: rendering). Task file
  `docs/kb/tasks/M3/M3-ENV-09-ashcrown-temple.md` holds the kit summary, triangle counts, the swap-in note for
  m2-slice and the known limits.
- Design notes first: `docs/kb/art/environments/ashcrown.md` (committed 37b322da before any geometry), checked
  against the act outline Ch5, bible §5.2, vowbound.md §2, decisions_log N-09, color_script `ch05` and pemakar.md;
  defines the `ch05_temple` and `ch05_temple_int` sub-frames (the colour script's `ch05` row is the festival
  night). Revised as built (§7 and Revisions).
- Kit `assets_src/environments/kits/ashcrown/` → `assets/environments/kits/ashcrown/` (9 pieces, 2 maps, 26
  materials), in the Pemakar silhouette's own frame, with its numbers (a test checks them against the silhouette
  mesh). Blender job `ashcrown_kit` (threads 4), byte-identical (40 files). Import kind `ashcrown_kit` (json, post-
  import script, KINDS in both test_post_import files, a row in docs/kb/tech/asset_import.md). PROVENANCE rows (40),
  an ownership row.
- Preview `game/levels/_tests/ashcrown_kit/` (rig `AshcrownPreview` on HalunaMood, layout generator, grade LUT,
  environment, 7 composed views + 2 overviews), viewed on lavapipe through about ten passes. Baselines
  `ashcrown_a01_approach`, `ashcrown_a04_anvil_hall` (compare: rmse 0.0).
- Tests: `tools/tests/test_ashcrown_kit.py` (22), `tests/unit/test_ashcrown_preview.gd` (5).

## In progress
- Nothing. Commits are on the worktree branch only (not pushed).

## Exact next step
- Rendering reviews M3-ENV-09 (the two sub-frames, the hall's daylight stand-ins and probe, the plume up close)
  and appends to its Review log.
- The Lead merges the branch and adds the swap-in note to `docs/kb/handoffs/live/env-art.md` (not edited here).
- Follow-ups worth filing (env-art): (1) swap Pemakar's `ashcrown_silhouette` for this kit's LOD1 pieces in
  `pemakar_layout.py` (re-renders Pemakar's baselines); (2) a near-plume piece or a softer close LOD for the
  Pemakar plume (it shows facets under ~300 m and its shaded side reads near-black).

## Known issues
- The Pemakar plume at close range (see above); A07's background is a flat haze (the lower slope has no detail at
  that distance); the tier walls are textured planes; the hall's daylight is stand-in OmniLights.
- The weathering shader paints a wet line at the tide datum: any scene in this kit's frame must set the datum to
  the sea (y −306.72) — the preview's `Tide` node does.
- `ac_preview_layout.py` and `ac_zone_lut.py` write into `game/levels/_tests/ashcrown_kit/` (outside the Blender
  job's outputs, like Corrow's); rerun them after a generator change (README there).

## Files touched
- `docs/kb/art/environments/ashcrown.md` (new), `docs/kb/tasks/M3/M3-ENV-09-ashcrown-temple.md`, this handoff.
- `assets_src/environments/kits/ashcrown/**` (new), `assets/environments/kits/ashcrown/**` (new).
- `game/core/import/ashcrown_kit_post_import.gd(.uid)`, `game/data/import/ashcrown_kit.json` (new).
- `game/levels/_tests/ashcrown_kit/**` (new).
- `tools/dev/blender_builds.json` (job appended), `assets/PROVENANCE.md` (rows appended), `docs/kb/ownership.md`
  (row appended), `docs/kb/tech/asset_import.md` (row appended), `tools/tests/test_post_import.py` and
  `tests/unit/test_post_import.gd` (KINDS), `tests/screenshots/shots.json` and `baselines/` (two shots appended).
- `tools/tests/test_ashcrown_kit.py`, `tests/unit/test_ashcrown_preview.gd(.uid)` (new).
