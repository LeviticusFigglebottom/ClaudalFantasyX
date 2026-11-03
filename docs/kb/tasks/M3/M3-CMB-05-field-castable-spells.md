---
id: M3-CMB-05
title: "FAST-TRACK: healing and support spells castable outside combat (field_usable)"
role: combat
status: doing
owner_session: "combat-systems (claude/combat-systems)"
depends_on: []
milestone: M3
request-from: lead
reviewer: ui
---
## Goal
The human's playtest (2026-11-03): spells like Mend castable from the field menu, spending the caster's MP. Combat owns the rules, the `field_usable` data flag and tests; ui-menus builds the screen (M3-MNU-05).

## Acceptance criteria
- [ ] `field_usable` flag on skills.json rows, validated.
- [ ] A headless rules class (FieldSpell) with errors, preview and cast.
- [ ] Tests; a request task to ui-menus with the API.

## Review log
