---
id: M2-MNU-07
title: Party formation menu (SPEC §6.11)
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-03]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
SPEC §6.11 asks for a party formation menu. Build it as a party page from the field menu: choose the three active fighters and the reserve, with keyboard, mouse and pad parity tests like the other party pages.

## Acceptance criteria
- [x] Field menu row; swap active and reserve members; the order is saved (GameStateData.party_ids / reserve_ids).
- [x] Refusals in words (e.g. an empty active line).
- [x] Keyboard, mouse and pad parity tests; UiSettings honoured; screenshot viewed and approved.

## Notes
- Built `FormationMenu` / `FormationMenuModel` in `game/ui/menus/formation/` (layout `game/data/ui/formation_menu.json`, words `game/data/loc/menus_formation.csv`); details in docs/kb/tech/ui.md "Party formation (M2-MNU-07)".
- Field menu root: Formation after Status (eleven rows); `field_menu.json` panel 735 px, moved up 24 px; checked at 130% text (scratch render, nothing committed). Baselines `field_menu`, `field_menu_swell_modes` re-approved; new `formation_menu`.
- Active line size is `BattleEngine.MAX_ACTIVE` (the engine's own limit); the least the line may hold is `rules.min_active` (1) in the layout file.
- Live battles: `BattleRequest.make` now reads `Game.state.party_ids` / `reserve_ids` once the party has gathered (Haluna's tideline fight used the data file's party before; ZoneStory already read the save). Scripted parties still override. Tested end to end in `tests/integration/test_formation_battle.gd`.
- `MenuPage.set_cursor_shown` added (default unchanged; battle shots unaffected) so only the list with the input shows a cursor.
- Not done: a hero's role word. characters.json has no role field; needs a Story/Design data row first.
- Reviewer (progression): please check the refusal rules (min_active, the nobody-standing rule) and that a fallen hero may stand in the line with a warning.

## Review log
