---
id: M3-UI-101
title: "Request (slice-polish): the battle HUD still shows initials (timeline chips, party rows); use the hero and creature portraits"
role: ui
status: todo
owner_session: ""
depends_on: [M2-MNU-301]
milestone: M3
request-from: cinematics
reviewer: cinematics
---
## Goal
ADR 0041 beat audit (self-rendered `battle_boss_intro_drownbell`, lavapipe): every chip on the turn-order timeline is
a lettered box (`R` Rhen, `A` Asha, `T` Toma, and a glyph for the Drownbell), and so is every party-panel row
(`party_row.gd`'s tinted portrait). The menus already show real portraits (M2-MNU-301: `HeroPortraits`,
`assets/ui/portraits/heroes/`), and creature portraits exist (`assets/ui/portraits/creatures/`). The timeline is
the slice's most-read UI (Pillar 4), so the initials are the most visible placeholder in every fight.

## Acceptance criteria
- [ ] Timeline chips show the hero's `HeroPortraits.face()` crop. A foe's chip shows its creature portrait, keeping
      the intent glyph and the boss colour, and an identity mark (shape, not hue alone).
- [ ] Party rows show the hero portrait. Petrify's stone strata still apply over it.
- [ ] The fallback to the initial stays for any id with no portrait.
- [ ] The battle shots re-approved after viewing.

## Review log
