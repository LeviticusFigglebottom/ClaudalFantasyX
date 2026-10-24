---
id: M1-QA-09
title: Next Asha GPU re-check (grief) with the QA-08 rigour fixes
role: qa
status: todo
owner_session: ""
reviewer: character
depends_on: [M1-RND-24, M1-CHR-12]
milestone: M1
request-from: "character"
---
## Goal
This comes from review-sweep-P on M1-QA-08. The QA-08 report was rigorous overall, with three gaps. Fix them in the next PC GPU re-capture of `asha_face_neutral`, `asha_face_smile`, `asha_face_grief` and `asha_face_stylized_compare`. Run it at 2× High and Ultra, the same way as QA-08, once M1-RND-24 and the CHR-12 grief-mouth fixes (faults A and B) are on the integration branch.

## Acceptance criteria
- [ ] **Measurements can be reproduced.** Every measured region (lid, cheek, crown, temple sheen, and any interior box) is given as a pixel rectangle in the named image. The lid and cheek R:B is reported in sRGB **and** linear, with each box's luminance, so the darker lid doesn't inflate the ratio unseen.
- [ ] **Fault A (the black rim at the grief mouth) is classed by a control.** Capture once more with the stage `Key` shadow off (through `capture_preset --mat-set`, or a stage override in the scratch copy). Name the class: shadow, bounce or asset.
- [ ] **The nose-bridge blotch is classed.** `qa08/crop_eyes.png` shows a soft dark blotch on the nose bridge, between the inner eye corners, in all six frames; give it a class and an owner.
- [ ] A strict SPEC §14 verdict per shot in `docs/kb/qa/gpu/`, with crops, as in QA-08.

## Review log
