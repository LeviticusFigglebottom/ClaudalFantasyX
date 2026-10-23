---
id: M1-RND-20
title: Diagonal striations at Asha's smiling mouth corner (key-light shadow terminator)
role: rendering
status: todo
owner_session: ""
depends_on: [M1-CHR-10]
milestone: M1
request-from: "character"
---
## Goal
`asha_face_smile` shows diagonal striations on the shadow-side mouth corner, on the lower lip and the skin below it. This is S2 of the review-sweep-L entry on M1-CHR-07 and S3 on M1-CHR-09. M1-CHR-10 traced it to the key light's shadow and ruled out the asset-side causes. What's left is shadow settings or the skin shader, which Character may not touch (the PC GPU session owns the shadow settings; Rendering owns `game/shaders/`).

Evidence, all lavapipe at `asha_face_smile` (details in asha_review.md §10.3):
- **Key shadow off** (`KeyLight.shadow_enabled = false`): the striations are gone.
- **Morph normals on the `mouth` primitive** (M1-CHR-10): no change. The striations sit on `skin_head`, which has had morph normals since CHR-07.
- **`directional_shadow_max_distance` 8 → 1.5 m** (finer shadow texels): the striations get *sharper*, and turn into a saw-tooth shadow edge. That rules out simple resolution blur. It is the terminator pattern: smoothed normals say lit, while the deformed corner's facets are self-shadowed at grazing light.

## Acceptance criteria
- [ ] No striations at the smiling corner in `asha_face_smile` (lavapipe, and the GPU 2× High capture)
- [ ] No new acne or peter-panning in the other asha_* shots
- [ ] Candidate fixes, for Rendering to choose from:
  - a terminator softening in `character_skin_body.gdshaderinc` (for example, fade the shadow attenuation by the geometric N·L, or apply the shadow per channel only where N·L > 0);
  - per-light `shadow_normal_bias` or `shadow_blur` (the PC session's settings);
  - or a request back to Character for more subdivision at the corner (LOD0 has 1,210 triangles of headroom).

## Review log
