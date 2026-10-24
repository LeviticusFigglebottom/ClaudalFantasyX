---
id: M2-AUD-17
title: UI sounds inside the field menu's pages (Items, Equip, Lattice, Status) and the battle pause
role: audio
status: doing
owner_session: "audio (claude/audio; worktree agent)"
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

## Notes
- 2026-10-24 audio: renumbered to M2-AUD-17 (the Lead's big8 rule; audio's M2-AUD-14 already covers Items, Formation,
  Customize and the map pan as pending hooks). This task switches the menu hooks live against claude/menus' real
  classes and adds StatusMenu and BattlePauseMenu.

## Review log
