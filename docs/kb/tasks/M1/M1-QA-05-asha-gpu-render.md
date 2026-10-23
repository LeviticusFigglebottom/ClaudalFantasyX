---
id: M1-QA-05
title: Render the asha_* and char_* shots on a real GPU to separate renderer artifacts from asset faults
role: qa
status: done
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
- 2026-10-23 lead: closing on review-sweep-K approve; the should-fixes are in M2-FP-05 (FP), M1-ARC-15 (graphics settings never applied) or the PC queue (QA-05 re-run).
- 2026-10-23 character (review-sweep-N, fresh reviewer, on the M1-QA-05c addendum `docs/kb/qa/gpu/2026-10-23-qa-05c-asha.md`; QA-05c has no task file of its own): **approve the judgement as a record. Asha still doesn't pass SPEC §14 at dialogue range.** QA-05 stays done. This answers QA-05 S1 (the re-run on the current build) and S2's nit (the crops are now committed under `qa05c/`).
  - **What I read:** the QA-05c report and its crops (`crop_diag.png`, `crop_mouths.png`). The captures predate M1-RND-20, at bias 2.5. I compared them with today's lavapipe asha_* captures, at bias 4.5.
  - **Passes:** neutral (eyes, skin, brows, hair near-black, closed mouth seam), silhouette, and costume at q34 and front.
  - **Fails:**
    1. The smile corner terminator. **Fixed since by M1-RND-20.** It's clean on lavapipe today; confirm in the next GPU round.
    2. The grief mouth interior goes near-black (shading, Rendering). Still open, and RND-20 says the bias doesn't change it. It has no task yet.
    3. The grief teeth read as faceted gold-brass, a single strip with no tooth separation (material and geometry, Character).
    4. The lash comb, and 5. the orange lid band (asset, Character).
    6. The notch at the inner corner of the grief brow (asset).
    7–8. Polish: the vest specular blob, and the hard temple cards in the compare shot.
  - **Disagreements and gaps for the next round:**
    - The report says smile "passes once fault 1 is fixed". Sweep-M on CHR-10 recorded dead eyes and cheeks in the smile (fault 5 there). That's a §14 expression fault, and this report doesn't address it. Keep it on the next round.
    - The nose cast wedge (sweep-M fault 1) isn't judged here. RND-20's bias softened it on lavapipe; re-judge it on the GPU.
    - The ragged upper-lip vermilion border is visible in `crop_diag.png` (right half, top edge of the upper lip). Add it to Character's list.
  - **Next GPU round (the PC queue):** re-run the QA-05c capture set after RND-20 and the CHR teeth and lid fixes, and judge grief and smile only. That's the "re-run" line at the end of the report.
