---
id: M3-UI-210
title: "The act card names Act III: The Unbinding, for Act II's end (Ch16)"
role: ui
status: blocked
blocked-by: ADR 0041
owner_session: claude/ui (ui-menus)
reviewer: cinematics
depends_on: []
milestone: M3
---
## Goal
Act II ends at the Drowned Choir with a Rhen voice-over and the act break (act_outline Ch16). The act card (ActCard, M3-C09-05) can already show Act II's title. It should also be able to show Act III's, so Ch16's beat sheet can call it the same way Ch9 calls Act II's.

## Acceptance criteria
- [x] `act_card.json` `acts` has a row for "3": `ACT_CARD_3_LABEL` "Act III" and `ACT_CARD_3_TITLE` "The Unbinding" (act_outline's words).
- [x] `test_act_card.gd` `test_act_three_closes_act_two`.
- [ ] Ch16's `.dlg` calls it (narrative and act1-chapters, with M4-C16-01's beat sheet).

## Review log
- 2026-10-28, ui-menus: **paused (ADR 0041, the human's refocus on Act I at final quality).** What is built stays on claude/ui and merges as is; nothing is reverted. Resume when a new ADR lifts the pause.
