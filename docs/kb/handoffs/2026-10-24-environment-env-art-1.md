# Handoff — environment — 2026-10-24 — Oruvel in the storm (M3-ENV-07B)

Session: env-art worktree agent (M3-ENV-07B, claimed by env-art). Branch: the worktree branch, not pushed; the Lead
merges. `docs/kb/handoffs/live/env-art.md` is not edited (the Lead's).

## Done
- **Storm pieces** in the `oruvel_kit` job (`assets_src/environments/kits/oruvel/ov_storm.py`): `raft_deck_broken`,
  `plank_bridge_broken`, `hull_capsized`, `storm_debris`, `net_pen_split_a/b/c` (each piece's origin at its hinge;
  `SPLIT_SECTIONS`, `section_pose`), `reef_edge_far`. LOD chains inside budget, everything soaked (VC.B), no emissive
  slot. Two materials (`ov_reef`, `ov_crown`) in `ov_materials.py` (Haluna writers loaded by path). PROVENANCE rows
  appended; .glb.import files on the kit's post-import script.
- **`lut_ch01_storm`** (`ov_zone_lut.py`, a new {python} run of the job): saturation x0.75, greens and the lagoon's
  turquoise to slate, warm paint cut less, S-curve 0.55, slate-teal toe. Hand-written Texture3D .import;
  `ov_import_settings.py` now skips `lut_*` (the overwrite M3-ENV-700 notes for the Brightwater kit cannot happen here).
- **The preview**: `OruvelPreview` (`game/levels/_tests/oruvel_kit/oruvel_preview.gd`) replaces HalunaMood as the root;
  `phase` `ch01_storm` shows `states.storm`, the stand-in frame (`oruvel_storm_environment.tres`, the swell), Kell's
  beacon (fog energy 0), hides the Seventh Terrace and stands Rendering's Undertow up at `ch01_arrival` to the south
  (quality high, clock held). O17 (composed, baseline `oruvel_o17_pen_split`) and O22 (review row). Storm cameras
  have far 40 km; the day cameras are untouched.
- Tests: `tools/tests/test_oruvel_kit.py` (+9 storm tests, layout/rig staleness), `tests/unit/test_oruvel_kit_preview.gd`
  (+3: the storm frame, the state swap and beacon, the split rig vs the state).
- Docs: oruvel.md §0 (stand-in `ch01_storm` row), §2, §4, §6, §7, Revisions; the preview README; the task file
  (status review, reviewer Rendering, swap-in note for m2-slice and Combat).

## In progress
- Nothing.

## Exact next step
- Rendering reviews M3-ENV-07B (O17 and O22: `godot-render --path . res://tests/screenshots/capture.tscn --
  --manifest=res://game/levels/_tests/oruvel_kit/oruvel_preview_shots.json --shots=oruvel_o17_pen_split,oruvel_o22_storm_row
  --out=<dir>`) and appends to the task's Review log.
- **Art: write the colour script's `ch01_storm` row** (act1_ch01 §9 Art item 1). oruvel.md §0 has the stand-in (sun
  58/120 at 2.6 #F6F0E8, ambient 0.5, the sky cleared, haze #96A9B2 0.0012, lut_ch01_storm as above); if Art's row
  differs, regenerate the LUT and re-approve O17.
- m2-slice / Combat: the swap-in note in the task file (the state swap; the pen's split driven by one amount 0 -> 1
  plus a swell clock).

## Known issues
- The torn nets read as dark hashed noise at O17's distance (the Haluna net rule, alpha hash).
- The debris keel-roof's soaked tar crown reads as a smooth pale dome rather than a hull bottom.
- The broken raft (rc) is mostly hidden behind the stall raft in O17; O22 shows it.
- The Undertow's foot is lost in the haze at 18 km (`ch01_arrival` is "far off"); `ch01_landfall` is Rendering's.
- The underwater preview test prints `Error calling deferred method: 'GDScript::refresh_bounce_passes'` (UnderwaterRig,
  not this task's); all 14 oruvel tests pass.

## Gates
- Run: gdlint / gdformat --check game tests; validate_data; taskboard --check; unittest test_oruvel_kit,
  test_post_import, test_release_excludes_tests, test_fog_lamps (41 OK); verify_blender_builds --job oruvel_kit
  (53 identical); Godot --import, then tests filtered `oruvel` (14/14) and `post_import` (21/21); capture.sh for
  oruvel_o01_surfacing, oruvel_o19_dive_mooring, oruvel_o07_name_board (RMSE 0, 0.00085, 0: no drift) and
  oruvel_o17_pen_split (approved from capture.sh, PNG and capture_report.json copied to tests/screenshots/out/ first;
  baselines.json only gained its row).
- Skipped: the full screenshot manifest (only Oruvel's shots can move); the coverage step (nothing under game/battle/
  or game/progression/); the other tools unittests (only the listed ones touch these files).

## Files touched
- assets_src/environments/kits/oruvel/: ov_storm.py, ov_zone_lut.py (new); build.py, ov_materials.py,
  ov_import_settings.py, ov_preview_layout.py.
- assets/environments/kits/oruvel/: the 8 storm .glb(.import), lut_ch01_storm.png(.import), materials/ov_reef.tres,
  ov_crown.tres, kit_manifest.json; assets/PROVENANCE.md (rows appended).
- game/levels/_tests/oruvel_kit/: oruvel_preview.gd(.uid), oruvel_storm_environment.tres (new); the generated layout,
  scene and manifest; README.md.
- tools/dev/blender_builds.json (oruvel_kit: the LUT run, sources, output); tools/tests/test_oruvel_kit.py;
  tests/unit/test_oruvel_kit_preview.gd; tests/screenshots/shots.json, baselines/baselines.json,
  baselines/oruvel_o17_pen_split.png.
- docs/kb/art/environments/oruvel.md; docs/kb/tasks/M3/M3-ENV-07B-oruvel-storm.md; this handoff.
