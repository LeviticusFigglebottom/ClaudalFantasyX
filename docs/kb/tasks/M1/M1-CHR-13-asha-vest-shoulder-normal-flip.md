---
id: M1-CHR-13
title: Asha's vest shoulder has a stair-stepped vertex-normal crease (QA-08 polish item F)
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: rendering
depends_on: []
milestone: M1
request-from: "rendering"
---
## Goal
QA-08 polish item F (docs/kb/qa/gpu/2026-10-24-qa-08-asha.md, `qa08/crop_shoulder.png`) is a jagged, stair-stepped
dark shape on the vest's shoulder in `asha_face_stylized_compare`. M1-RND-23 triaged it on lavapipe (the same frame
as the GPU crop, within 0.15 grey levels on average) and found **an asset (normals) problem, not rendering**:

- **Unchanged** with both lights' shadows off, with a 4× tighter shadow range, with `shadow_normal_bias` 1.0, with
  the vest's normal map off (`normal_strength=0`), with the lacquer coat off, at the Low and Medium presets (no
  SSR, no SSIL), and with the environment reflection and SSR off. So it is not a shadow-map, terminator,
  screen-space or reflection artefact.
- No other surface shows through: with every non-vest material painted green, the shape stays on `Costume`.
- The vest textures have no such shape (the vest quadrant of the albedo, ORM and cloth mask is uniform apart
  from the arc motifs).
- **The `Costume` mesh's own vertex normals have a hard discontinuity along exactly that staircase** (the
  gradient of a normals-as-colour render, `qa08/crop_shoulder_triage.png`, bottom row). It follows the mesh grid's
  vertices.

**Likely cause** (please verify; rendering hasn't edited anything): `_outward()` in
`assets_src/characters/asha/asha_costume.py` flips each grid normal by `sign(N · q)`, where `q` is the horizontal
radial vector from the body axis. On the top of the shoulder the true normal is near vertical, so `N · q` is close
to 0, and the sign flips vertex by vertex along a staircase. The flipped vertices shade as if facing inward, which
is darker.

## Acceptance criteria
- [ ] The vest's shoulder normals are continuous: no per-vertex sign flips. For example, orient the whole panel by
      its winding or one reference face, instead of per vertex, or fall back to the vertical when `|N · q|` is small.
- [ ] Rebuilt through the normal pipeline (`assets_src/characters/asha/build.sh`); PROVENANCE row updated if the
      outputs change.
- [ ] The stair-step is gone in `asha_face_stylized_compare` (lavapipe, and the GPU crop when the PC next runs it). List the
      drifting Asha shots with their RMSE for the Lead to re-approve.

## Reproduce (lavapipe)
`capture_preset --shots=asha_face_stylized_compare --preset=high --scale=2`, cropped at (1000, 760, 500 × 200). The
A/B flags are `--light-set=shadow_enabled=false`, `--mat-set=normal_strength=0.0` and `--preset=low`. The
normals-as-colour probe (an unshaded `ALBEDO = world normal × 0.5 + 0.5` override on the `cloth` surfaces) is
described in the M1-RND-23 handoff.

## Review log
