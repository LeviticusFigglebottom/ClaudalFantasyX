---
id: M2-CHR-02
title: Toma at vertical-slice fidelity on the MPFB2 pipeline
role: character
status: doing
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
- [ ] `assets_src/characters/toma/` builds `assets/characters/toma/toma.glb` (+ LOD1), textures and materials from source,
      reusing the Asha/Rhen modules; every output under 5 MB; LOD0 within toma.md §8.
- [ ] A `toma` job in `tools/dev/blender_builds.json`, byte-identical on rebuild; `--job asha --job rhen` stay identical.
- [ ] `toma_face_poses.json` (toma.md §6, brows ×1.15 range), a stage on `asha_stage.gd` and new shots with lavapipe
      baselines; no existing baseline re-approved.
- [ ] The emblem never shows: the chiselled scar has no trace of the Level's shape (toma.md §3).
- [ ] PROVENANCE rows, tests, and `docs/kb/art/characters/toma_review.md` with an honest §14 assessment.

## Notes

## Review log
