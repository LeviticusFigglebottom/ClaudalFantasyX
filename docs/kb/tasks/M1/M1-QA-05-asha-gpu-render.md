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
