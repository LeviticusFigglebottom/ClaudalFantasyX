---
id: M1-CHR-11
title: Asha round 6: grief teeth, lash comb, lid band, brow notch, dead eyes in the smile, upper-lip edge
role: character
status: todo
owner_session: ""
depends_on: [M1-CHR-10]
milestone: M1
request-from: "rendering"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [ ] Grief: the teeth read as teeth (not a faceted gold-brass strip): tooth geometry separation, albedo and roughness via write_materials.py
- [ ] Lashes are not a comb; no orange lid band; the brow notch is gone
- [ ] Smile: the eyes take part (lower lid raise, crow's-feet compression, Duchenne), not a smirk; the inner brows lift in grief
- [ ] The ragged upper-lip edge is smooth
- [ ] Blender gate byte-identical; under 5 MB; strict §14 in asha_review.md §11; then the PC re-captures only grief and smile on the GPU

## Review log
