---
id: M3-UI-1251
title: "FAST-TRACK (playtest 11-03): a field-menu Magic page to cast field-usable spells on the party"
role: ui
status: review
reviewer: combat
owner_session: claude/ui (ui-menus, session_01F3vrUMk5AsY8FMR6bL35TW)
depends_on: []
milestone: M3
request-from: lead
---
## Goal
The human's playtest FAST-TRACK 5 (UI half): outside battle, a hero casts a field-usable spell (Mend and the like) on
party members from the field menu, paying the caster's MP. combat-systems owns the rules (M3-CMB-1252); this page is
built against them.

## Acceptance criteria
- [x] A Magic page in the field menu: caster list, the caster's field spells with MP cost, then a target pick
  (one hero or all), with a preview line and a refusal line in words (no MP, full HP, fallen, nothing to cure).
- [x] Casting spends the caster's MP and writes the result to the save as the Items page does.
- [x] Tests and a shot.

## Notes
- Answers combat-systems' request M3-MNU-05 (on claude/combat-systems). Built over `FieldSpell` (M3-CMB-05),
  bound by name so claude/ui builds before that branch merges; until then the field menu has no Magic row.
- Checked in a throwaway merge of claude/ui + claude/combat-systems: test_magic_menu 7/0 including
  `test_the_live_field_spell_rules_drive_the_page`; shot magic_menu rendered and viewed (Mend from Asha on Rhen,
  "Asha: MP 60 → 56 · Rhen: HP 151 → 381").
## Review log
