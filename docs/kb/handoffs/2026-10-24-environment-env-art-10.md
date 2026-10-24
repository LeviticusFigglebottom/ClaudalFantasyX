# Handoff — environment (env-art worker, M3-ENV-11) — 2026-10-24

## Done
- **M3-ENV-11 a close-range Pemakar plume**, now `status: review` (reviewer: rendering). Notes in
  `docs/kb/tasks/M3/M3-ENV-11-close-range-plume.md`.
- New piece `ash_plume_near` (Pemakar job, `pemakar_skyline.py`): `ash_plume`'s surface sampled 160 × 128 with
  rounded creases, softened normals (grid-smoothed, bent toward the radial) and the small heads in UV2.x; its LOD1
  is `ash_plume`'s LOD0. `ash_plume.glb` and every other Pemakar and Ashcrown output are byte-identical
  (verify_blender_builds: pemakar_kit 63 identical, ashcrown_kit 40 identical).
- `env_ash_plume.gdshader`: a `near` group (shade lift, back-scatter, vent glow, billow shading, sky-up, a bumped
  billow normal inside ~240 m) plus `alpha_mottle`; all off by default and faded out by `near_fade_m`, so the
  town's plume is unchanged (P01, P03, Lanternfall arena: rmse 0.00000).
- Ashcrown preview: the plume is `ash_plume_near` (LOD0 to 900 m) with `ac_plume_day`'s near parameters; camera
  **A08 the crater loggia** restored and viewed; **A10** (the plume from the west outer slope) added.
- Baselines: `ashcrown_a01_approach` (rmse 0.02389) and `ashcrown_a04_anvil_hall` (0.00615) re-approved for the
  plume only; `ashcrown_a10_plume_from_the_rim` registered (the one new baseline). baselines.json carries only the
  new entry (key order restored).
- Docs: pemakar.md §2.4 and Revisions; ashcrown.md §2.5, §3, §5 (A08, A10), §7 and Revisions; the preview README.

## In progress
- Nothing. Commits are on the worktree branch only (not pushed).

## Exact next step
- Rendering reviews M3-ENV-11 (the near group's values, A08/A10/A01/A04, and whether the bumped billow normal
  should become shared shader work) and appends to its Review log.
- The Lead merges and notes it in `docs/kb/handoffs/live/env-art.md` (not edited here).

## Known issues
- A08 is soft and plain: from the loggia the plume's near face is 8 m beyond the balustrade and in the temple's
  shadow all day. A view from further away (A10) is where the near plume reads.
- O2 (660 m) still shows a few torn shards high in the column (edge-faded overhangs of the far surface).
- The plume is fat: its surface is within 10–25 m of the whole crater rim, so any zone camera in the crater is
  close to it. A narrower column for the zone would be a Pemakar silhouette change (re-renders P01/P03).
- The shader cannot see cast shadows (no `light()` pass); `lift_all_round` stands in for the temple's shadow.

## Files touched
- `assets_src/environments/kits/pemakar/pemakar_skyline.py`; `assets/environments/kits/pemakar/ash_plume_near.glb(.import)`,
  `kit_manifest.json`
- `game/shaders/environment/env_ash_plume.gdshader`
- `assets_src/environments/kits/ashcrown/ac_materials.py`, `ac_preview_layout.py`;
  `assets/environments/kits/ashcrown/materials/ac_plume_day.tres`
- `game/levels/_tests/ashcrown_kit/` (`ashcrown_layout.json`, `ashcrown_preview.tscn`, `ashcrown_preview_shots.json`, `README.md`)
- `tests/screenshots/shots.json` (A10 appended), `tests/screenshots/baselines/` (A01, A04, A10, baselines.json)
- `tools/tests/test_pemakar_kit.py`, `tools/tests/test_ashcrown_kit.py`, `tests/unit/test_ashcrown_preview.gd`
- `assets/PROVENANCE.md` (one row appended)
- `docs/kb/art/environments/pemakar.md`, `docs/kb/art/environments/ashcrown.md`, the task file, this handoff.
