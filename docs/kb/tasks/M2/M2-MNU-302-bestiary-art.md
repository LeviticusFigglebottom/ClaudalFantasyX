---
id: M2-MNU-302
title: Bestiary creature portraits rendered from the creatures track's models
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-301]
milestone: M2
request-from: lead
---
## Goal
Creature portraits for the bestiary: all 27 Act I creatures plus the slice's five, rendered from `claude/creatures`' models by the same pipeline as M2-MNU-301 (ADR 0120), framed from `creatures.json`'s `portrait` block.

## Acceptance criteria
- [ ] The portrait renderer covers every enemy with a model; one PNG each, with a PROVENANCE row.
- [ ] The bestiary page shows the portrait of a seen creature, a silhouette of an unseen one, nothing for a creature with no model.
- [ ] Tests; the bestiary shots re-approved after viewing.

## Review log
