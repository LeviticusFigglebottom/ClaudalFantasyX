---
id: M2-MNU-03
title: Field Items page (use, sort, describe) and party Status page
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M1-PRG-02]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
The field has no way to see or use the bag, or to see a hero's numbers. Build an Items page and a Status page reached from the field menu.

## Acceptance criteria
- [x] Items: the bag by category, a description of each item, a sort, and field use of restoratives on a chosen hero (the item's own effects, written to the saved vitals; refusals in words).
- [x] Status: per hero HP, MP, stats (base and growth), gear, Swell gauge and mode, Lattice progress (movement points, nodes woken).
- [x] Keyboard, controller and mouse; UiSettings honoured; screenshots; tests.

## Notes
- **Built (agent worktree, for review by progression):** `ItemsMenuModel` + `ItemsMenu` (game/ui/menus/items/), `StatusMenuModel` + `StatusMenu` (game/ui/menus/status/), the capture driver `PartyPagesShot` (game/ui/menus/party_pages_shot.gd, shots under each page's shots/), layouts game/data/ui/items_menu.json and status_menu.json, loc keys appended to game/data/loc/menus_items.csv only. docs/kb/tech/ui.md "Items and Status pages (M2-MNU-03)" has the rules.
- **Field use** = items.json `"field": true` and a battle block that targets allies; the effect is `ItemBattleAction.resolve_on` on `PartySheet.combatant`, written with `GameStateData.record_vitals` keeping the saved Swell gauge and mode and only the carried statuses. No game/progression changes.
- **Status split** is built step by step (base_combatant, + Lattice, + gear), so base + Lattice + gear == PartySheet.combatant's total (tested for every stat).
- **Gates (scope: UI code + data + docs):** `gdformat -l 120 --check game tests` 420 unchanged; `gdlint game tests` no problems; `validate_data` 0 errors 0 warnings; `taskboard --check` exit 0; Godot `--filter=items_menu` 11 run 0 failed, `--filter=status_menu` 5 run 0 failed, `--filter=field_menu` 19 run 0 failed; screenshots `items_menu`, `items_menu_use`, `status_menu` captured, looked at, baselined, `compare.py` 3 compared 0 failed. Coverage step skipped: nothing in game/battle or game/progression touched.

## Review log
