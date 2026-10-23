---
id: M1-QA-05
title: Render the asha_* and char_* shots on a real GPU to separate renderer artifacts from asset faults
role: qa
status: doing
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU)
depends_on: [M1-CHR-03]
milestone: M1
request-from: "lead"
---
## Goal
The lavapipe captures of Asha show diagonal shadow banding on the cheek and harsh blotchy self-shadowing. Decide what is the CPU renderer and what is the asset.

## Acceptance criteria
- [ ] GPU captures (High and Ultra) of every asha_* and char_* shot, with diff stats against lavapipe
- [ ] Each visible defect classified as renderer artifact, shadow settings, or asset fault, in a report in docs/kb/qa/gpu/
- [ ] Recommendations for CHR-04 and Rendering (for example the shadow bias or split settings for close-ups)

## Review log
