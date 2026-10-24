---
id: M2-CHR-01
title: Rhen and Toma on the MPFB2 donor topology (donor_mix and face sliders)
role: character
status: todo
owner_session: ""
depends_on: [M1-CHR-03]
milestone: M2
request-from: "lead"
reviewer: rendering
---
## Goal
M1-CHR-03 rebuilt Asha and the base bodies on the CC0 hm08 donor (ADR 0021). Its follow-up list named "Rhen and Toma `donor_mix` and face sliders", but no task was filed for it (review-sweep-O). The M2 slice puts both heroes in dialogue.

## Acceptance criteria
- [ ] A `donor_mix`, macro mix and face slider set for Rhen and for Toma, per their SPEC §7.3 proportions and design sheets, behind the same interfaces as Asha's (parameters JSON, landmarks, `DEF-*` skeleton, the shape names).
- [ ] Heavy modification per ADR 0021. Only the vendored CC0 data is used, and PROVENANCE has rows for every derived file.
- [ ] LOD0 and LOD1 within the character budget; each GLB under 5 MB.
- [ ] A first dialogue-range §14 pass recorded, with the stylisation rule from ADR 0019.

## Review log
