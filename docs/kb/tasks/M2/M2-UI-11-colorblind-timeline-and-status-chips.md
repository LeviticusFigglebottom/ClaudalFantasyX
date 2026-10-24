---
id: M2-UI-11
title: Accessibility audit (1/5): the colour-blind palette on the timeline and status chips
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M1-UI-02]
milestone: M2
request-from: lead
---
## Goal
SPEC §6.11 asks for colour-blind-friendly UI options. The `palette` setting (standard / colorblind, M1-UI-02) exists. Audit whether it really reaches the turn timeline's chips and the status glyphs, fix what doesn't, and prove it with a test and a shot.

## Acceptance criteria
- [ ] Under the colorblind palette, every timeline chip (ally, enemy, ghost, current, skipped, Doom) and every status glyph draws from the overridden roles, and still reads by shape (the edge shapes, the backings, the silhouettes).
- [ ] A test walks the chips and glyphs under both palettes; ally and enemy, and buff and ailment, stay distinct under a deuteranopia simulation (contrast check on the simulated colours).
- [ ] A shot of the statuses fixture under the colorblind palette (`battle_statuses_colorblind`), viewed and approved.

## Review log
