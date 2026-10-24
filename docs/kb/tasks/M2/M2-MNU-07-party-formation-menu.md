---
id: M2-MNU-07
title: Party formation menu (SPEC §6.11)
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-03]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
SPEC §6.11 asks for a party formation menu. Build it as a party page from the field menu: choose the three active fighters and the reserve, with keyboard, mouse and pad parity tests like the other party pages.

## Acceptance criteria
- [ ] Field menu row; swap active and reserve members; the order is saved (GameStateData.party_ids / reserve_ids).
- [ ] Refusals in words (e.g. an empty active line).
- [ ] Keyboard, mouse and pad parity tests; UiSettings honoured; screenshot viewed and approved.

## Notes

## Review log
