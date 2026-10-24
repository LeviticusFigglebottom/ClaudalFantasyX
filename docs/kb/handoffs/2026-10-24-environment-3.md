# Handoff — environment — 2026-10-24 #3 (M2-ENV-07, env-art worktree)

## Done
- **M2-ENV-07 is in review (reviewer: rendering).** The real hero banyan and windbreak tree replace the two
  PLACEHOLDER kit trees.
- The vegetation generators `banyan.py`, `windbreak.py` and `canopy.py` grow them. `textures.py --only trees`
  paints the leaf atlas and the banyan bark.
- The kit exports them through `kits/haluna/trees.py`, which replaces `placeholders.py`, under the unchanged
  piece names. No layout or scene edits.
- Five kit materials are appended at the end of `materials.py`. Every other kit output is byte-identical.
- Tests: `tools/tests/test_broadleaf_trees.py`, and `test_haluna_kit.py` updated.
- Docs: vegetation.md "Broadleaf trees" and haluna_mood_review.md placeholder table. PROVENANCE rows appended.

## In progress
- Nothing. The branch is committed in the worktree and not pushed.

## Exact next step
- Lead: merge, run the full screenshot manifest, then re-approve `haluna_h07_chapel_court`,
  `haluna_h01_village_from_sea` and `haluna_h02_tidewall_lane` if Rendering agrees. RMSE and image reads are in
  the task file's Notes.
- Rendering: review the task.

## Known issues
- The Haluna dresser does not chain kit LODs with `visibility_parent` (kit-wide, pre-existing). The follow-up
  for the zone track is in the task Notes.
- `kit_canopy_*` materials and the `canopy_cluster` textures are unused now. They were left for the kit owner.
- Root strands are 4-sided. The windbreak has a single variant. GPU cost is unmeasured (lavapipe only).

## Files touched
- assets_src/environments/vegetation/{banyan,windbreak,canopy}.py (new); textures.py and veg_common.py
  (appended).
- assets_src/environments/kits/haluna/trees.py (new), placeholders.py (deleted), build.py, materials.py
  (appended block).
- assets/environments/kits/haluna/{banyan,windbreak}_placeholder.glb, kit_manifest.json, and materials/kit_{banyan_bark,banyan_root,banyan_leaf,windbreak_bark,windbreak_leaf}.tres.
- assets/environments/vegetation/{coastal_tree_leaf,banyan_bark}_{albedo,normal}.png (+ .import).
- tools/dev/blender_builds.json (haluna_kit sources), tools/tests/test_broadleaf_trees.py, tools/tests/test_haluna_kit.py.
- assets/PROVENANCE.md, docs/kb/art/environments/vegetation.md, docs/kb/art/environments/haluna_mood_review.md,
  docs/kb/tasks/M2/M2-ENV-07-hero-banyan-and-windbreak-trees.md.
