---
id: M2-CHR-02
title: Toma at vertical-slice fidelity on the MPFB2 pipeline
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters; worktree subagent)"
reviewer: rendering
depends_on: [M2-CHR-01]
milestone: M2
request-from: lead
---
## Goal
Toma Okeru (docs/kb/art/characters/toma.md) built the way Rhen was (M2-CHR-01, pipeline.md §12): the MPFB2 donor
(ADR 0021, CC0 data only) driven by `toma_params.json`, the shared face API, cropped hair and a short beard as card
layers plus scalp/beard shadow in the skin albedo, the scarred red-lacquer pauldron, harness, under-tunic, indigo sash,
wrapped trousers, sandals, the tide-shield on his back and the hooked spear.

## Acceptance criteria
- [x] `assets_src/characters/toma/` builds `assets/characters/toma/toma.glb` (+ LOD1), textures and materials from source,
      reusing the Asha/Rhen modules; every output under 5 MB; LOD0 within toma.md §8.
- [x] A `toma` job in `tools/dev/blender_builds.json`, byte-identical on rebuild; `--job asha --job rhen` stay identical.
- [x] `toma_face_poses.json` (toma.md §6, brows ×1.15 range), a stage on `asha_stage.gd` and new shots with lavapipe
      baselines; no existing baseline re-approved.
- [x] The emblem never shows: the chiselled scar has no trace of the Level's shape (toma.md §3).
- [x] PROVENANCE rows, tests, and `docs/kb/art/characters/toma_review.md` with an honest §14 assessment.

## Notes
- Built: `assets_src/characters/toma/` (build_toma, toma_params, toma_hair with the beard, toma_costume with the pauldron
  and the scar depth field, toma_props with the shield and spear, toma_textures, write_materials, build.sh). Imports
  Asha's modules and `rhen_costume`; no Asha or Rhen file changed, so `--job asha --job rhen` are unaffected by
  construction (not re-run).
- Numbers: LOD0 58,160 tris (budget 66,000), LOD1 26,988 (33,000); toma.glb 4.86 MB, toma_lod1.glb 1.43 MB; 16
  textures, largest 3.06 MB. Costume atlas is 2K, not the sheet's 4K (the 5 MB blob cap); see toma_review.md §2.
- Gates: `verify_blender_builds.py --job toma` 37 identical (Blender at the job's pinned 4 threads; a 2-thread build
  differs in the LOD1 decimation); six new baselines `toma_{front,q34,profile,back,face_neutral,face_smile}`, a fresh
  capture compares at rmse 0; Godot hero_stage 4/4, character_shading 14/14, post_import 17/17; tools unittest 465 OK;
  validate_data and taskboard clean.
- Scar: one depth field cuts the mesh and paints the strata; no lacquer survives inside the circle (tested). Review
  and honest §14 notes: `docs/kb/art/characters/toma_review.md`. Rig extras (sash tails, pauldron hinge, shield
  unsling, spear bone) are follow-ups.

- **Rebuilt after the merge into claude/characters** (2026-10-24): M1-CHR-12 changed the shared face shapes, teeth and
  skin socket term, so toma.glb, toma_lod1.glb, toma_head_albedo/orm were rebuilt (`verify --job toma` 37 identical;
  58,168 LOD0 tris, 4.86 MB). The six toma_* baselines are refreshed (≤ 0.0023 rmse; this branch's own new baselines).

## Review log
