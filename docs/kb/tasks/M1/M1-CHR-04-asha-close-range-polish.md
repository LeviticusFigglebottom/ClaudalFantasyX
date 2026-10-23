---
id: M1-CHR-04
title: Asha close-range polish - lips, hair, skin micro-detail, costume materials
role: character
status: todo
owner_session: ""
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
