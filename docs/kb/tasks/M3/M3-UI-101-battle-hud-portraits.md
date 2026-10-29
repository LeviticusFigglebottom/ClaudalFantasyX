---
id: M3-UI-101
title: "Request (slice-polish): the battle HUD still shows initials (timeline chips, party rows); use the hero and creature portraits"
role: ui
status: review
owner_session: "claude/ui (ui-menus)"
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
- [x] Timeline chips show the hero's `HeroPortraits.face()` crop. A foe's chip shows its creature portrait, keeping
      the intent glyph and the boss colour, and an identity mark (shape, not hue alone).
- [x] Party rows show the hero portrait. Petrify's stone strata still apply over it.
- [x] The fallback to the initial stays for any id with no portrait.
- [ ] The battle shots re-approved after viewing (self-rendered and viewed; the Lead approves baselines at the gate).

## Notes
- 2026-10-29 ui-menus: done on claude/ui (faces in the timeline and party rows 71689a7b; the foe picture fills its diamond and a petrified face greys under the strata, f6db67f0f). Self-rendered and viewed: battle_statuses, battle_boss_intro_drownbell, battle_hud_preview (live log 2026-10-28 06:00). Baselines are the Lead's gate. For cinematics to review.

## Review log
