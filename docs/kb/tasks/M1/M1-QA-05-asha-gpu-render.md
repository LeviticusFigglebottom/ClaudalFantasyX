---
id: M1-QA-05
title: Render the asha_* and char_* shots on a real GPU to separate renderer artifacts from asset faults
role: qa
status: review
reviewer: character
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU)
depends_on: [M1-CHR-03]
milestone: M1
request-from: "lead"
---
## Goal
The lavapipe captures of Asha show diagonal shadow banding on the cheek and harsh blotchy self-shadowing. Decide what is the CPU renderer and what is the asset.

## Acceptance criteria
- [x] GPU captures (High and Ultra) of every asha_* and char_* shot, with diff stats against lavapipe
- [x] Each visible defect classified as renderer artifact, shadow settings, or asset fault, in a report in docs/kb/qa/gpu/
- [x] Recommendations for CHR-04 and Rendering (for example the shadow bias or split settings for close-ups)

## Notes
- 2026-10-23 PC GPU session: report docs/kb/qa/gpu/2026-10-23-qa-05-asha.md. GPU default matches lavapipe on all 14 shots (RMSE <= 0.0057): no defect is a renderer artefact. Cheek banding and blotchy self-shadowing = shadow terminator (normal bias 2.5-3.0 fixes; finer texels make it worse). Lip seam, plastic vest (100% lacquer coat at 0.06 roughness) and blocky hair cards = asset (CHR-04). Rendering follow-ups: character-lighting rule (character_shading.md), expose lacquer coat roughness as a uniform.

## Review log
- 2026-10-23 character (review-sweep-K, fresh reviewer): **approve.** No blockers.
  - **What I read:**
    - the task and `docs/kb/qa/gpu/2026-10-23-qa-05-asha.md`, including its M1-CHR-04 correction;
    - character_shading.md "Shadows on characters" (:180-186);
    - the shot stages' `shadow_normal_bias` values (asha_stage.tscn:109, 119 are now 2.5).
  - **Checks:** none run. The report is docs only, and the captures live on the PC.
  - **What passes:**
    - The method is sound. At scene settings the GPU and lavapipe agree within RMSE ≤ 0.0057 on all 14 shots, so no defect is a renderer artefact. The High and Ultra deltas are explained by what those presets change.
    - Each defect is isolated by changing one thing at a time (shadows off, bias, texel size, detail normal, curvature).
    - The finer-texels-make-it-worse result agrees with how Godot scales normal bias by texel size.
    - The recommendations landed: bias 2.5 on the Asha stage, the vest lacquer uniforms set in M1-CHR-04, and the hair and lip items carried into CHR-04 and CHR-07.
  - **Should-fix:**
    - **S1: the report measured the CHR-03 build.** M1-CHR-07 has since changed Asha's face: the smile morph normals, the lip seal and the brows. Before the next §14 face review, re-run the six face shots on the GPU at default and High (a short addendum to this report), to confirm the lip seam and terminator classes still hold.
    - **S2: the lighting rule isn't applied to the game zones yet.** The Haluna mood Sun (haluna_mood.tscn:83, 1.0) and the first-verse Sun (first_verse.tscn:169, default 1.0) light Asha at dialogue range in the first playable. Raised in M2-FP-02 S1 and M2-FP-04 S3.
  - **Nit:** the key evidence PNGs (`cheek_exp.png`, `lips_base_noshadow.png`) exist only on the PC, so a reviewer can't see them. Describe each crop in a sentence, or commit two small downscaled crops under docs/kb/qa/gpu/ (our own renders, not reference images).
