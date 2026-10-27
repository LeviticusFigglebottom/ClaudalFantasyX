---
id: M2-MNU-304
title: Party cards on the field menu root (portrait, name, HP, MP)
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-301]
milestone: M2
request-from: ui
---
## Goal
The playtest note "parts look primitive": the field menu opened on a bare list. Its root now shows the active line as cards, using M2-MNU-301's portraits, as the follow-up the portrait agent suggested.

## Acceptance criteria
- [x] One card per place in the active line (FormationMenuModel over a PartySheet, as the next fight has them): portrait (`field_menu` page emotion: smile, worried when fallen), name, HP and MP numbers and gauges.
- [x] Cards sit between the line about the highlighted row and the Last saved block (`field_menu.json` "party"); root only; refreshed when a party page closes; a fallen hero's card dimmed.
- [x] Tests `tests/unit/test_field_menu_party_cards.gd`; field_menu, field_menu_21x9, field_menu_16x10 re-approved after viewing.

## Notes
- Also fixes a 130 % pseudo-locale overflow M2-MNU-301 brought into Formation: detail lines that start below the portrait now take the full width (formation_menu re-approved: the fallen warning spans the block).
- Reviewer: design.

## Review log
