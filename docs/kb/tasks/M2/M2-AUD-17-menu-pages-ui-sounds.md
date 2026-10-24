---
id: M2-AUD-17
title: UI sounds inside the field menu's pages (Items, Equip, Lattice, Status) and the battle pause
role: audio
status: review
reviewer: qa
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
- [x] Hooks for ItemsMenu, EquipMenu, LatticeMenu, StatusMenu and BattlePauseMenu (cursor, confirm, cancel, errors
      such as a refused equip), checked by validate_data like the other rows.
- [x] A test walks at least one page's rows and hears each sound.

## Notes
- 2026-10-24 audio: renumbered to M2-AUD-17 (the Lead's big8 rule; audio's M2-AUD-14 already covers Items, Formation,
  Customize and the map pan as pending hooks). This task switches the menu hooks live against claude/menus' real
  classes and adds StatusMenu and BattlePauseMenu.

- 2026-10-24 audio: done. Every ui_sfx.json hook whose class now exists is live. ShopMenu and InnMenu are rewritten
  on real state, because their guessed signals don't exist. LatticeMenu gets the question's cursor. EquipMenu's error
  now plays only on the GEAR level, so a hover over a refused piece no longer sounds like an error. StatusMenu and
  BattlePauseMenu get new hooks. FormationMenu stays pending: no class yet. No new sound.
  test_field_audio drives the real pages through handle_input. The refused Confirms that can't be heard are listed
  in M2-AUD-15. The table is in docs/kb/tech/audio_runtime.md, "The pages live (M2-AUD-17)".

## Review log
