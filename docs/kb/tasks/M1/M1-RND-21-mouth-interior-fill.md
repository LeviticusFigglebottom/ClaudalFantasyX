---
id: M1-RND-21
title: Mouth-interior fill light and cavity shading (grief goes near-black)
role: rendering
status: doing
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU)"
depends_on: [M1-QA-05]
milestone: M1
request-from: "character"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [ ] The mouth interior in grief and open-mouth visemes is not near-black: a cavity fill term or a bounce approximation in the skin and mouth shading, tiered
- [ ] Applies to every hero, not only Asha; documented in character_shading.md
- [ ] Measured on the GPU; lavapipe shots re-approved by the Lead

## Review log
