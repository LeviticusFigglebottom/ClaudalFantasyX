---
id: M1-RND-24
title: Mouth cavity bounce is shadowed by positional lights (unshadow it; enforce the family for every hero)
role: rendering
status: doing
owner_session: "worktree-agent-a7c54615acb434f4e"
reviewer: character
depends_on: [M1-RND-21]
milestone: M1
request-from: "character"
---
## Goal
This comes from review-sweep-P on M1-RND-21. character_shading.md says the cavity bounce is "unshadowed". But `character_mouth_body.gdshaderinc` `light()` uses `reach = LIGHT_IS_DIRECTIONAL ? 1.0 : ATTENUATION`, and in Godot 4 a positional light's `ATTENUATION` includes its shadow.

The face stage (`base_body_stage.tscn`) lights the face with SpotLight3Ds, and only `Key` (energy 7) casts shadows. So the strongest light adds no bounce inside the mouth. The RND-21 gain (median 0.0121 → 0.0174) comes only from the unshadowed Fill and rims. Cutscene keys (M2-FP-10) will be shadowed too. This may also be QA-08's fault A, the hard black rim around the open grief mouth.

## Acceptance criteria
- [ ] For positional lights, the bounce gets the light's distance falloff without its shadow. One option is `reach = 1.0`, because `light()` runs only inside a light's range and cone, plus a smooth range falloff. Another is a falloff the shader computes itself; choose one and document it. Directional lights are unchanged.
- [ ] Measured on the GPU: grief interior luminance and the share below 0.01, High and Low, against RND-21's numbers. Closed-mouth shots unchanged. Report whether QA-08's fault A changes, with a key-shadow-off control capture.
- [ ] A test that walks `assets/characters/*/materials/` and asserts that every `mouth`, `teeth` and `tongue` material uses the `mouth` family. Today's test checks only Asha's three files by name; Rhen and Toma (M2-CHR-01) must inherit the rule.
- [ ] Update character_shading.md, "Mouth interior". The Lead re-approves the affected lavapipe shots (`asha_face_grief` at least) after a side-by-side view.

## Review log
