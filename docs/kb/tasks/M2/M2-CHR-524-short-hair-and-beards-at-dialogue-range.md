---
id: M2-CHR-524
title: "Short hair and beards at dialogue range: Toma, Kerrid, Moll (no blotches, no hard edges)"
role: character
status: doing
owner_session: "characters (worktree hair-wt)"
depends_on: [M2-CHR-515]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
ADR 0041, scope item 4: faces at dialogue range. Self-renders of toma_face_neutral, kerrid_face and moll_face show the
short hair (toma_hair's cards on toma_shorthair.png) and the beards as blotchy dark clusters with white flecks, not as
hair. Kerrid's beard also has a hard rectangular notch round the mouth. M1-QA-09 reported Toma's beard edge blotchy on
the PC's GPU, so it is not only the software capture.

## Acceptance criteria
- [ ] The cause is found and stated: card size and density, the atlas sampling and mips, the dither, or the region
      masks.
- [ ] Fixed in the character assets and data. A shader change needs Rendering's agreement (ownership.md).
- [ ] Every rebuilt hero verifies identically on the three numpy paths, and the tests pass.
- [ ] Self-rendered and viewed: toma_face_neutral, toma_face_smile, kerrid_face, moll_face and moll_face_yield, plus
      a full-figure shot each.

## Review log
