---
id: M3-CMB-05
title: "FAST-TRACK: healing and support spells castable outside combat (field_usable)"
role: combat
status: review
owner_session: "combat-systems (claude/combat-systems)"
depends_on: []
milestone: M3
request-from: lead
reviewer: ui
---
## Goal
The human's playtest (2026-11-03): spells like Mend castable from the field menu, spending the caster's MP. Combat owns the rules, the `field_usable` data flag and tests; ui-menus builds the screen (M3-MNU-05).

## Acceptance criteria
- [x] `field_usable` flag on skills.json rows, validated.
- [x] A headless rules class (FieldSpell) with errors, preview and cast.
- [x] Tests (tests/unit/test_field_spell.gd, test_formulas, tools/tests/test_field_usable.py); a request task to ui-menus with the API.

## Notes
- Field-usable today: Mend (Asha) and Chorus Mend (Lattice). Battle buffs (Ward, Hasten, Lull's Regen) end with the battle, so they stay battle-only; the validator refuses field_usable on anything that neither heals nor cleanses.
- No party skill revives or cures yet; FieldSpell supports `cleanses` for when one lands.

## Review log
