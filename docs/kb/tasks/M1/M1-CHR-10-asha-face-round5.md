---
id: M1-CHR-10
title: Asha round 5: hair black and strand-broken, lashes, lid band, brows, teeth, mouth normals
role: character
status: doing
owner_session: "worktree-agent-a109a5ba219573018"
depends_on: [M1-CHR-09]
milestone: M1
request-from: "rendering"
---
## Goal
From the review-sweep-L entries (file:line references there).

## Acceptance criteria
- [ ] Hair reads black (asha.md:121), not auburn: check albedo, the hair shader primary tint and anisotropic highlight colour; the crown is no longer a smooth shell
- [ ] Lashes: tapered clumps, not comb teeth; the pale upper-lid band is gone (albedo, AO, or lid geometry)
- [ ] Brows: soft edges, hair-stroke density falloff
- [ ] Grief: no blue-grey tooth slab (teeth albedo and occlusion; mouth-interior AO)
- [ ] Morph normals on the mouth surface as well as skin_head (88 vertices); no diagonal striations at the smiling mouth corner
- [ ] Evenly lit skin: work with the shading (cavity, roughness breakup, the painterly close-range look per ADR 0019)
- [ ] Blender gate byte-identical; under 5 MB; §14 review strict in asha_review.md §10; then a 2x High GPU capture by the PC session (M1-QA-05c) as final judge

## Review log
