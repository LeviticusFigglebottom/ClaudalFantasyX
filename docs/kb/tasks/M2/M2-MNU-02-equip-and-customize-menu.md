---
id: M2-MNU-02
title: The Equip menu (weapon and armor per hero, stat-delta preview, ability slots, Customize)
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M1-PRG-02, M1-PRG-03]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
Equipment, ability slots and Customize exist as logic (`EquipmentBag`, `EquipmentEffects`, `Customize`) with no menu, and live battles never apply worn gear (the TODO in `BattleVitals.setup`). Gear bought at the Net-Rack Forge must be wearable and must count in battle.

## Acceptance criteria
- [x] Per hero: weapon and armor, each piece's ability slots (filled and empty).
- [x] Choosing a piece previews the stat delta (and abilities gained or lost) before committing; refusals said in words (`equip_error`, `unequip_error`).
- [x] Customize: craft an ability into an empty slot (`Customize.craft`), with the recipe, the items held and the shortfall shown first.
- [x] Live battles apply worn gear (`EquipmentEffects.modifier()` between the Lattice and the vitals in `BattleVitals.setup`), with a test.
- [x] Keyboard, controller and mouse; UiSettings honoured; screenshots; tests.

## Notes
- **Built (2026-10-24, worktree of claude/menus):** `game/ui/menus/equip/` `EquipMenu` (view, FieldSubmenu) + `EquipMenuModel` (Node-free) + `EquipMenuShot` and `shots/`; layout `game/data/ui/equip_menu.json`; strings `game/data/loc/menus_equip.csv` (`EQUIP_MENU_*`). Levels HEROES → GEAR (slots and ability slots) → PIECES (pieces_for, "Worn", "Take it off") or RECIPES (Customize.candidates, Ready / N short). Preview: now → next with signed, coloured deltas (`heal`/`danger`) and abilities gained/lost, built on a deep copy of the equipment through a scratch PartySheet (never mutates the save). Refusals word for word from equip_error, unequip_error and every Customize ERR. Craft asks for a second Confirm. grant_starting runs for every shown hero when the model opens.
- **Battle hook:** `game/battle/scene/battle_vitals.gd` setup() adds `EquipmentEffects.modifier()` (`BattleVitals.gear_of(state or Game.state)`) between the Lattice and the vitals when `carry`, and sets `engine.currency_multiplier` (Full Net; was not wired in live battles). `encounter_rate_pct` is still not read by the field (noted in economy.md). battle_controller.gd untouched (997 lines).
- **Gates:** gdformat --check (418 unchanged) and gdlint (no problems) on game tests; validate_data 0 errors 0 warnings; taskboard --check OK; Godot `--filter=equip` 61 run 0 failed, `--filter=battle_vitals` 14/0, `--filter=field_menu` 19/0; full suite (for the coverage compare log) 1612 run 0 failed, godot_log_check clean; coverage battle/ 99.95%, progression/ 96.69%, OK within baseline. Screenshots `equip_menu`, `equip_customize` rendered, reviewed at 1280x720, baselined; compare PASS rmse 0.00000 each.
- **Known limits:** Customize works on worn pieces only (equip a spare first). Reviewer: progression.

## Review log
