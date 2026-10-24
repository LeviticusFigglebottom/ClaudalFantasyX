---
id: M1-CHR-13
title: Asha's vest shoulder has a stair-stepped vertex-normal crease (QA-08 polish item F)
role: character
status: review
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
- [x] The vest's shoulder normals are continuous: no per-vertex sign flips. For example, orient the whole panel by
      its winding or one reference face, instead of per vertex, or fall back to the vertical when `|N · q|` is small.
- [x] Rebuilt through the normal pipeline (`assets_src/characters/asha/build.sh`); PROVENANCE row updated if the
      outputs change.
- [x] The stair-step is gone in `asha_face_stylized_compare` (lavapipe, and the GPU crop when the PC next runs it). List the
      drifting Asha shots with their RMSE for the Lead to re-approve.

## Reproduce (lavapipe)
`capture_preset --shots=asha_face_stylized_compare --preset=high --scale=2`, cropped at (1000, 760, 500 × 200). The
A/B flags are `--light-set=shadow_enabled=false`, `--mat-set=normal_strength=0.0` and `--preset=low`. The
normals-as-colour probe (an unshaded `ALBEDO = world normal × 0.5 + 0.5` override on the `cloth` surfaces) is
described in the M1-RND-23 handoff.

## Delivery (2026-10-24, characters)
- **Cause confirmed and fixed in `asha_costume.py`:** `_outward()` flipped each vertex by sign(N · q); now the whole grid
  flips by its majority sign. Together with the `_panel` winding bug (its test flipped when the winding already faced
  outward, so the front layer faced inward and only the inset back layer was seen; the per-vertex flips pushed that
  back layer in and out by its thickness, which is the staircase). Now the outer layer faces out and the back layer
  sits inside.
- Rebuilt Asha, Rhen and Toma (they share the helpers): `verify --job asha --job rhen --job toma` 44 / 31 / 37 identical.
- The black staircase along the vest's shoulder edge is gone in `asha_face_stylized_compare` (lavapipe); the jagged
  dark shape left in the middle of the shoulder is the braid's cast shadow. The GPU crop is the PC's next check.
- Drift after the rebuild (lavapipe rmse; all re-approved after viewing, except the ones that still pass):
  asha_face_neutral/smile/grief 0.0160, asha_face_stylized_compare 0.0263, asha_sleeve_s0/s4 0.0094, asha_clip_kneel 0.0095,
  asha_clip_offer_hand 0.0088, asha_clip_laugh 0.0093; rhen_front 0.0151, q34 0.0115, profile 0.0113, back 0.0120,
  face_neutral/smile 0.0199; toma_front 0.0159, q34 0.0109, profile 0.0106, back 0.0112. Passing, not re-approved:
  asha_front 0.0061, asha_q34 0.0071, asha_profile 0.0074, asha_extreme_pose 0.0073, asha_clip_walk 0.0061,
  asha_clip_face_west 0.0067, asha_clip_run 0.0077, toma_face_neutral/smile 0.0026.

## Review log
