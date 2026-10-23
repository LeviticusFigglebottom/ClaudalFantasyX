---
id: M1-CHR-04
title: Asha close-range polish - lips, hair, skin micro-detail, costume materials
role: character
status: doing
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, rendering + material half; branch gpu/chr-04-materials). Mesh, lips and hair cards: cloud agent
depends_on: [M1-CHR-03]
milestone: M1
request-from: "lead"
---
## Goal
CHR-03 put Asha on the MPFB2 donor topology, which is a clear step up. At the Lead's look at `asha_face_stylized_compare`, the hero is still not at final fidelity at dialogue range.

## Acceptance criteria
- [ ] Lips: rest shape thinner and less rubbery; no dark seam line at the lip contact; the mouth interior and corners read correctly in neutral, smile and grief
- [ ] Scalp hair: no visible card blocks or gaps at dialogue range; a soft hairline; strand-level alpha detail; the braid kept (asha.md hair section)
- [ ] Skin: micro-detail (pores, fine lines) at the specified texel density; less waxy specular; the painterly close-up look stays per ADR 0019
- [ ] Costume: the bodice and vest read as cloth or leather of the right roughness, not glossy plastic (character_shading.md contract)
- [ ] Shadow banding on the shadow-side cheek: confirmed as a renderer artifact or fixed (the GPU-session check, M1-QA-05)
- [ ] §14 dialogue-range review re-run side by side with CHR-03 and recorded in asha_review.md; baselines re-approved with reasons

## Review log

## Notes: PC GPU session, rendering + material half (branch gpu/chr-04-materials)

Done on the GPU (Godot 4.6.3, RX 9070 XT), measured on all ten `asha_*` shots at High; the report is
`docs/kb/qa/gpu/2026-10-23-chr-04-materials.md`.

- **Shadow terminator (criterion "shadow banding"): fixed for the Asha stage.** `asha_stage.tscn` KeyLight and RimLight
  `shadow_normal_bias` 1.0 → 2.5. Sweep at 2× High on the face shots: 1.0 bands, 2.0 leaves a faint residue, 2.5 and
  3.0 are clean; no peter-panning at body scale (feet and staff contact hold in `asha_q34`). Tested
  (`test_asha_stage_lights_clear_the_shadow_terminator`). No skin-shader change was needed. Other rigs that key a
  face (Cinematics dialogue rigs, battle cameras) should follow the rule in character_shading.md "Shadows on characters".
- **Vest (criterion "costume"): material half done.** `cloth.tres` now sets lacquer base 0.55, coat 0.16, strength 0.55
  (lacquered leather; the shader defaults 0.35 / 0.06 / 1.0 stay for hard lacquer). Tested
  (`test_asha_vest_lacquer_is_leather_not_plastic`).

**For the cloud agent (mesh, lips, hair cards, textures; not touched here):**
1. The B (lacquer) channel of `asha_cloth_clothmask.png` is still 1.0 over the whole vest. Add wear (0.6–0.8 on
   edges, folds and around the toggles) and a leather-grain normal under the coat; the material values above assume
   that and may come down a little once the mask carries the variation.
2. Face density on the cheeks and jaw still helps: the normal bias hides the terminator, but more triangles there
   would let close-up rigs use less bias.
3. Lips and hair cards: as in the QA-05 report (`docs/kb/qa/gpu/2026-10-23-qa-05-asha.md`).
4. Baselines: every `asha_*` lavapipe baseline drifts with this branch (see the report); re-approve them together
   with the mesh work, not separately.

Status stays **doing** until the mesh half lands.
