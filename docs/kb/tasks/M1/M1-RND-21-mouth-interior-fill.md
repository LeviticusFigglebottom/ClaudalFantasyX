---
id: M1-RND-21
title: Mouth-interior fill light and cavity shading (grief goes near-black)
role: rendering
status: done
reviewer: character
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU)"
depends_on: [M1-QA-05]
milestone: M1
request-from: "character"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [x] The mouth interior in grief and open-mouth visemes is not near-black: a cavity fill term or a bounce approximation in the skin and mouth shading, tiered
- [x] Applies to every hero, not only Asha; documented in character_shading.md
- [~] Measured on the GPU; lavapipe shots re-approved by the Lead (measured; `asha_face_grief` awaits re-approval)

## Notes (PC GPU session, branch `gpu/rnd-21-mouth-fill`)
Report: `docs/kb/qa/gpu/2026-10-23-rnd-21-mouth-fill.md`. Design: character_shading.md, "Mouth interior".
- **New family:** `mouth` (`character_mouth{,_medium,_low}.gdshader`), with an unshadowed cavity bounce per light.
  The bounce fades with the baked occlusion and with the light behind the face, and is on every tier.
- **Asha:** teeth, tongue and mouth moved to it through `write_materials.py`, with the same values.
- **Interior luminance** (grief, GPU): the median rises 0.0121 → 0.0174 at High and 0.0121 → 0.0180 at Low. The share
  below 0.01 falls 0.30 → 0.16 at High and 0.29 → 0.14 at Low.
- **Drift:** `asha_face_grief` 0.0023 on the GPU; the other asha_* shots are unchanged (0.0000).
- **Not addressed:** the teeth still read khaki (their albedo: fault 3, M1-CHR-11).
- **Tried and dropped:** a stage fill light. It lights the whole face (too global), and a stage light doesn't reach
  zones.

## Review log
- 2026-10-24 review-sweep-P (character): **approve with fixes.**
  - **What works.** Every Asha mouth, teeth and tongue material uses the `mouth` family, and the family is in the tier table and the prewarm registry. The bounce sits outside every `#if`, so it runs on every tier. `test_hero_mouth_interiors_use_the_mouth_family_with_a_cavity_bounce` pins this; the character_shading filter is 16/0 here. The Lead re-approved `asha_face_grief` on lavapipe in d5b71c3, so criterion 3 is met. The material edits are in Character's `assets/characters/asha/materials/`. They went through `write_materials.py` with the same values, and as the Character reviewer I accept them.
  - **Finding: the bounce is shadowed by positional lights (filed as M1-RND-24).** The term is documented as "unshadowed", but it is shadowed for every positional light:
    - In `character_mouth_body.gdshaderinc` `light()`, the bounce uses `reach = LIGHT_IS_DIRECTIONAL ? 1.0 : ATTENUATION`.
    - In Godot 4, a positional light's `ATTENUATION` includes its shadow.
    - The face stage's lights are all SpotLight3D, and only `Key` (energy 7) casts shadows. So the strongest light adds no bounce inside the mouth.
    - The measured gain (median 0.0121 → 0.0174) comes only from the unshadowed Fill and rims. That likely explains why the gain is modest, and it may explain QA-08's fault A.
  - **Smaller gap.** "Applies to every hero" holds by convention only, because the test checks Asha's three files by name. M1-RND-24 also asks for a test that walks `assets/characters/*/materials/{mouth,teeth,tongue}.tres`, so Rhen and Toma (M2-CHR-01) inherit the rule.
