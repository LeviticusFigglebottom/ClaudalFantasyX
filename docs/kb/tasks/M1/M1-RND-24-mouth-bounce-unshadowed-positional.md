---
id: M1-RND-24
title: Mouth cavity bounce is shadowed by positional lights (unshadow it; enforce the family for every hero)
role: rendering
status: review
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
- [x] For positional lights, the bounce gets the light's distance falloff without its shadow. One option is `reach = 1.0`, because `light()` runs only inside a light's range and cone, plus a smooth range falloff. Another is a falloff the shader computes itself; choose one and document it. Directional lights are unchanged.
- [ ] Measured on the GPU: grief interior luminance and the share below 0.01, High and Low, against RND-21's numbers. Closed-mouth shots unchanged. Report whether QA-08's fault A changes, with a key-shadow-off control capture.
- [x] A test that walks `assets/characters/*/materials/` and asserts that every `mouth`, `teeth` and `tongue` material uses the `mouth` family. Today's test checks only Asha's three files by name; Rhen and Toma (M2-CHR-01) must inherit the rule.
- [x] Update character_shading.md, "Mouth interior". The Lead re-approves the affected lavapipe shots (`asha_face_grief` at least) after a side-by-side view.

## Notes (worktree-agent-a7c54615acb434f4e, 2026-10-24)
- **Choice: an additive, unshadowed second pass.** `light()` in Godot 4.6.3 gets neither the light's position nor its range: a compile probe rejects `LIGHT_POSITION`, `LIGHT_DISTANCE`, `SHADOW` and the like. So the shader can't rebuild the falloff, and `reach = 1.0` would drop the distance falloff that a far key's energy is scaled for. `character_mouth_bounce.gdshader` (`blend_add, depth_draw_never, shadows_disabled, ambient_light_disabled, fog_disabled`) adds only positional lights' bounce. With shadows disabled, its `ATTENUATION` is exactly Godot's distance and cone falloff. Directional lights keep the bounce in the base pass at reach 1, unchanged. `CharacterShaderTiers.apply_to_tree` attaches the pass to owned copies of every mouth-family material, never the `.tres`, and sets `cavity_bounce_pass`. Write_materials.py and Asha's materials are untouched. The pass is registered in prewarm_materials.json.
- **Which scenes it affects.** Only Asha uses the family today, and every Asha shot is lit by two DirectionalLight3Ds (asha_stage.tscn), so no shot's lighting changes. The spot-lit face stage (`base_body_stage.tscn`) has no mouth materials. The review's premise, that the face stage's shadowed Key spot gets no bounce, doesn't apply to the Asha shots RND-21 measured. It does apply to cutscene keys (M2-FP-10) and any spot- or omni-lit dialogue.
- **Lavapipe proxy for criterion 2 (not the GPU run).** Grief with the directional key swapped for a shadowed SpotLight3D along the same direction. Interior median, then mean, linear luminance:
  - pre-RND-24 fallback: 0.0370 / 0.0737;
  - **with the pass: 0.0388 / 0.0766**;
  - key shadow off, both variants: 0.044 / 0.0811 (they agree, so the pass reproduces the inline bounce exactly when nothing is shadowed).
  - The share below 0.01 is 0 in this rig: the directional rim still lights the interior.
  - **Still open for the PC GPU:** the High/Low grief numbers against RND-21's, in a positional-key rig.
- **QA-08 fault A: not this bug, and it doesn't change.** It's the lips' shadow on the *inner-lip skin* (`skin_head`), which no bounce reaches. With the key and rim shadows off, the rim disappears completely. With the mouth bag, teeth and tongue painted green, the dark band lies outside the green (`docs/kb/qa/gpu/qa08/crop_grief_rim_shadow_off.png`). Filed **M1-RND-25** (rendering, reviewer character).

## Review log
