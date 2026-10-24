---
id: M2-AUD-17
title: UI sounds inside the field menu's pages (Items, Equip, Lattice, Status) and the battle pause
role: audio
status: todo
owner_session: ""
depends_on: [M2-MNU-01, M2-MNU-02, M2-MNU-03, M2-MNU-04]
milestone: M2
request-from: lead
---
## Goal
claude/menus made the field menu's Items, Equip, Lattice and Status rows open a `FieldSubmenu` child
(ItemsMenu, EquipMenu, LatticeMenu, StatusMenu) and added BattlePauseMenu. `game/data/audio/ui_sfx.json` had no hooks
for any of them, so test_field_audio's field-menu walk broke at the big7 merge. The Lead's merge added one FieldMenu
watch (`node.child != null`: opening a page plays ui_confirm, closing it ui_cancel) and walked the test to the Swell
row. Inside the pages nothing is heard yet.

## Acceptance criteria
- [ ] Hooks for ItemsMenu, EquipMenu, LatticeMenu, StatusMenu and BattlePauseMenu (cursor, confirm, cancel, errors
      such as a refused equip), checked by validate_data like the other rows.
- [ ] A test walks at least one page's rows and hears each sound.

- **Renumbered (Lead merge, big8, 2026-10-24):** big7 filed this as M2-AUD-14, which collided with claude/audio's own M2-AUD-14 (menu-page SFX: item use and sort, formation swap, customize, map pan). Now M2-AUD-15, the next id free across all branches. Overlap: audio's M2-AUD-14 and M3-AUD-15 (Lattice, Equip, FieldSubmenu open and close) cover most of this; what is left here is the Status page and BattlePauseMenu.

- **Renumbered again (Lead merge, big8, 2026-10-24):** M2-AUD-15 collided with claude/audio's M2-AUD-15 (the menus public-reads request) and M2-AUD-16 is audio's too. Now M2-AUD-17.

## Review log
