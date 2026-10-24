---
id: M3-ENV-09B
title: "Pemakar's far Ashcrown from the Ashcrown kit's LOD1 (one building at every distance)"
role: environment
status: review
owner_session: "env-art"
depends_on: [M3-ENV-09]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-09, from its worker. The Pemakar kit draws Ashcrown as `ashcrown_silhouette`, while the new
Ashcrown kit is the same building up close; its origin is the silhouette's (0, 306.72, -682) in Pemakar's frame.
Replace the silhouette in `assets_src/environments/kits/pemakar/pemakar_layout.py` (and in the arena
`ash_terrace_lanternfall`, which places the layout's skyline) with the Ashcrown kit's LOD1 pieces, so the temple
is one building at every distance.

## Acceptance criteria
- [x] Pemakar's preview and the Lanternfall arena place the Ashcrown kit's LOD1 at the silhouette's transform.
      The silhouette is retired or kept only as the far LOD.
- [x] Re-capture `pemakar_p01_waterfall_of_fires`, `pemakar_p03_among_the_graves` and
      `battle_arena_ash_terrace_lanternfall`, view them, and re-approve only with a stated reason.
- [x] `verify_blender_builds` is identical for every job touched, and `test_pemakar_kit` and `test_arenas` pass.

## Notes
- 2026-10-24 (env-art, cfd4cc84): `pemakar_layout.py` places `ashcrown_tiers`, `flying_stair`, `crown_pavilion`,
  `forecourt`, `pilgrim_causeway` at `massif_rim_point()` (the Ashcrown kit's origin; its y 0 is the rim), yaw 0,
  each with `kit_dir`, `materials_dir` (the Ashcrown kit's) and `lod1_from_m` 600 (the Ashcrown preview's
  FAR_LOD1_M; a test checks they match). `PemakarKitPreview.instance_piece` honours those per-placement keys.
  The arena generator (`arena_scenes.py`) takes the glb path from `kit_dir`; the arena .tscn instances the five
  pieces at the silhouette's old arena transform, where the import's own chain (LOD0 to 70 m) draws LOD1 at 650 m.
  Not placed: `crest_ground` (Pemakar keeps its massif), `anvil_hall`/`anvil_altar` (interior), `plume_vent`
  (hidden in the bowl). `ashcrown_silhouette` is retired from both layouts but the asset and its PROVENANCE row
  stay: it is still built and `test_ashcrown_kit` reads its numbers.
- Shots: `pemakar_p01_waterfall_of_fires` re-approved (rmse 0.00164; the temple at the plume's foot is the kit's
  building, a little broader with the forecourt, same spire). `pemakar_p03_among_the_graves` rmse 0 (temple not
  in frame). `battle_arena_ash_terrace_lanternfall`: the skyline is out of frame; it fails compare (0.018) at HEAD
  too, from the creatures' poses (gull wings, crab, eel), so not re-approved: flagged for the Lead.
- No Blender job touched (layout and arena generators only), so verify_blender_builds was not needed.
- Reviewer (rendering): check the far temple's read in P01 and that LOD1 holds from the town.

## Review log
