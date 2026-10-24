---
id: M2-ENV-07
title: The hero banyan and the windbreak tree at final quality (replace the two PLACEHOLDER trees)
role: environment
status: review
owner_session: "env-art"
depends_on: [M1-ENV-03]
milestone: M2
request-from: environment
reviewer: rendering
---
## Goal
`banyan_placeholder` and `windbreak_placeholder` (assets_src/environments/kits/haluna/placeholders.py) are
honest stand-ins with cluster-card crowns, tagged PLACEHOLDER in their glTF extras and kit_manifest.json.
SPEC §8.4 allows no visible placeholders at M2. H07 is framed by the banyan's aerial roots; H01/H02 need the
windbreak rows' dark value masses (haluna.md §1.3, vegetation.md "Not built").

## Acceptance criteria
- [x] A hero banyan (about 14 m, fused stems with buttresses, spreading limbs, aerial and prop roots, a
      broad crown of leaf-level clusters in the vegetation format) and a windbreak tree (an original
      thick-leaved coastal tree: short trunk, dense upright oval crown, `foliage_shadow`-heavy), built by
      the vegetation generators (assets_src/environments/vegetation/), with LODs chained as vegetation.md
      "One LOD at every distance" requires, and wind channels per the vegetation convention.
      *(Two authored LODs each. As kit pieces they get their ranges from the Haluna dresser, which does not
      chain kit LODs with `visibility_parent`. That is pre-existing and kit-wide; see Notes, follow-up.)*
- [x] The pieces keep their scene contract (or the dresser maps the old names), so Haluna swaps in with no
      layout change; the PLACEHOLDER tag and reasons are removed.
- [x] Bark that reads in H07 (the aerial roots are not white sticks or black poles).
- [x] haluna_h01/h02/h07 (and veg shots if touched) re-captured and viewed; drift listed for re-approval.

## Notes
2026-10-24, env-art (worktree from `claude/env-art`; not pushed). Full write-up: vegetation.md "Broadleaf trees".

**What was built**
- `assets_src/environments/vegetation/banyan.py`, `windbreak.py`, and `canopy.py` (shared helpers: bark tubes,
  buttress flanges, bent spray cards, lumpy crown cores) grow the trees.
- `textures.py --only trees` paints `coastal_tree_leaf_*` (a 1024² atlas: banyan and windbreak leaf sprays at real
  leaf size, plus two opaque leaf mosaics for the cores) and `banyan_bark_*` (512×1024, fused root strands,
  lenticels, lichen).
- Five kit materials are appended at the end of `assets_src/environments/kits/haluna/materials.py`:
  `kit_banyan_bark`, `kit_banyan_root`, `kit_banyan_leaf`, `kit_windbreak_bark`, `kit_windbreak_leaf`.
  Nothing above that block was edited. `kit_textures.py` and `walls.py` were not touched.

**Swap approach (zero scene edits)**
- `assets_src/environments/kits/haluna/trees.py` replaces `placeholders.py` (deleted). It exports the
  vegetation trees as kit pieces under the old names, `banyan_placeholder` and `windbreak_placeholder`, with
  the axes converted and the slots renamed.
- The names are the contract: `haluna_layout.json`, the zone's collision table, and `test_haluna_zone.gd`. The
  dresser places the trees unchanged, and m2-slice needs no swap-in edits.
- build.py's `PLACEHOLDERS` keeps only `shell_shrine_massing`. kit_manifest.json and the .glb extras carry no
  PLACEHOLDER tag for the trees.
- Every other kit .glb, material and vegetation PNG is byte-identical.
- `blender_builds.json`: the haluna_kit job now also lists the vegetation tree sources.

**Triangles and budgets** (LOD0 / LOD1, budget)
- Banyan: 59,949 / 6,999 (60,000 / 10,000); .glb 3.4 MB.
  - Why that budget: one instance, the hero tree, and the H07 camera is 7 m from it, inside the crown.
  - LOD0 split: sprays 21.5k, hanging roots 17.1k, limbs and branches 8.1k, twigs 5.4k, props 4.0k,
    trunk and buttresses 3.9k.
- Windbreak: 5,785 / 430 (6,500 / 1,000); .glb 0.42 MB.
  - Why that budget: 49 instances, about 15–25 inside the 75 m LOD0 range per view.

**H07 art direction (in the data, `banyan.VARIANTS["hero"]`)**
- Two great limbs flank the chapel court. The court-side limb runs low (about 4.75 m), so it arches across the
  top of H07 with root curtains, between two twisted prop pillars.
- A kept-clear walk to the chapel door has no prop roots, and hanging roots over it are cut at 2.4 m.

**Screenshots** (lavapipe; not re-approved; RMSE vs baseline, limit 0.008; the pre-change capture of the same
shots gave 0.0008 / 0.0019 / 0.0033)
- `haluna_h07_chapel_court`, RMSE **0.2642**: intended, the whole frame changed.
  - The chapel is bracketed by a twisted prop pillar on the left and by the fused trunk and props on the right.
  - Braided brown root curtains hang from the low limb across the top. Leaf sprays line the top edge, and the
    crown's dappled shade covers the court.
  - The background windbreak row reads as dense, dark, upright ovals.
- `haluna_h01_village_from_sea`, RMSE **0.0191**: the windbreak rows behind the houses are now narrower,
  upright, dark columns instead of round blobs. The banyan (LOD1) is a broad dark mass mid-frame.
- `haluna_h02_tidewall_lane`, RMSE **0.0169**: only the windbreak regions changed (right of the right house,
  and slivers behind the left roofs). The layout puts few windbreaks in this frame.
- All three need re-approval by the Lead (`compare.py --update-baselines` after a full-manifest run). The veg_*
  shots are untouched: no vegetation shader or test scene changed.

**Gates**
- `validate_data` 0 errors. `taskboard --check` ok.
- `unittest discover -s tools/tests` (touched tools/): 502 tests OK (2 skipped).
- `verify_blender_builds --job haluna_kit --job vegetation`: 31 + 7 identical.
- No GDScript changed, so no gdlint, gdformat or Godot test run.

**Follow-ups (not done here)**
1. haluna_dresser.gd (now with the zone track) should chain kit LODs: `visibility_parent` of `<piece>` =
   `<piece>-lod1`, with the margin on LOD1's begin only, as VegetationPlant does. Kit-wide, pre-existing.
2. `kit_canopy_bark` / `kit_canopy_leaf` / `kit_canopy_leaf_dark` and `canopy_cluster_*` are now unused. The kit
   owner can delete them (those files were being edited in parallel, so they were left).
3. haluna_kit_sheet.gd still skips `banyan_placeholder` (a test scene, not touched).
4. The windbreak has a single variant (49 instances vary by yaw and scale only). A second seed would need a new
   piece name in the layout.

## Merge notes (2026-10-24, env-art parent)
- Merged into claude/env-art after M1-ENV-10 and M2-ENV-08: build.py keeps props, causeway and trees;
  kit rebuilt, `verify_blender_builds` haluna_kit 49 + vegetation 7 identical.
- **Gap the worktree missed:** `test_post_import.gd::test_kit_placeholder_pieces_are_tagged...` still
  asserted the two trees are PLACEHOLDER (the Godot tests were skipped as "no GDScript changed", but the
  .glb extras changed). Updated: only `shell_shrine_massing` is a placeholder; the trees and dock aren't.
- Shots on the merged tree (with M1-ENV-10), viewed and re-approved: h07 rmse 0.26145 (the banyan
  frames the chapel with trunk, prop pillar and root curtains), h01 0.01872 (windbreak columns), h02
  0.03102 (windbreaks, plus the ENV-10 house that sat in the old LOD hole). Palette checks 19/19.
- **Follow-up (open, for the review):** at H07 the banyan's crown hardly enters the top of frame; the shot
  reads as trunks and roots under open sky. A denser, lower crown edge over the court would finish it.

## Review log
