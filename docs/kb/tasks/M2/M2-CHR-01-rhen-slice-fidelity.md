---
id: M2-CHR-01
title: Rhen at vertical-slice fidelity on the MPFB2 pipeline
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: rendering
depends_on: [M1-CHR-03, M1-CHR-11]
milestone: M2
request-from: lead
---
## Goal
Rhen Sallow (docs/kb/art/characters/rhen.md) built on Asha's MPFB2 donor pipeline (ADR 0021: CC0 data only), at
slice fidelity: the face and expression set from the shared §6.2 API, his short copper-tipped hair, the
single-sleeve sea-jacket with the diving gauntlet, trousers, belt and tether coil, calf wraps and sandals, Dace's
lantern on its strap, and the two crossed reef-hooks. Byte-reproducible Blender build, pure-Python materials, PROVENANCE
rows, and new lavapipe screenshot baselines.

## Acceptance criteria
- [ ] `assets_src/characters/rhen/` builds `assets/characters/rhen/rhen.glb` (+ LOD1), textures and materials from
      source; reuses the Asha modules instead of copying them; every output under 5 MB.
- [ ] A `rhen` job in `tools/dev/blender_builds.json`; `verify_blender_builds.py --job rhen` is byte-identical, and
      `--job asha` stays identical (shared modules may only gain knobs whose defaults keep Asha's bytes).
- [ ] Rhen's emotion table (rhen.md §6) as `rhen_face_poses.json`, including the crooked smile.
- [ ] A review stage plus new shots (front, three-quarter, profile, back, face neutral, face smile), baselines
      approved on lavapipe; no existing baseline re-approved.
- [ ] PROVENANCE rows; an honest §14 assessment in `docs/kb/art/characters/rhen_review.md`.

## Notes

## Review log
