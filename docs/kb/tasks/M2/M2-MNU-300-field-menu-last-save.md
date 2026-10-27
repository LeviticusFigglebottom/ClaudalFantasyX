---
id: M2-MNU-300
title: Field menu root shows the last save (place and time); the "Save at a shrine" tip
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-04]
milestone: M2
request-from: lead
---
## Goal
The Lead's design call (2026-10-24): the field menu gets **no** save row. Saving stays at save shrines plus the chapter autosaves (the pilgrimage pillar; shrines are rest points). Instead, the field menu's root shows where and when the game was last saved, and the tips carry a "Save at a shrine" hint.

## Acceptance criteria
- [x] The root panel shows the last save's location name and time, read from the save system's public API (never a private field), or a "Not saved yet" line.
- [x] A tip entry: saving happens at shrines.
- [x] Loc keys for every string; layout values in `game/data/ui/field_menu.json`.
- [x] Unit test; the field menu shot re-approved after viewing.

## Notes
- `FieldMenuModel.save_system` (from_game: the SaveSystem autoload) and `last_save()` / `last_save_line()`: the newest loadable slot, as Continue picks it (`TitleSaveEntry.continue_slot`), shown through `SaveSlotInfo.location_name()` and `timestamp_text(bias)`. A model with no save system (tests, test rooms) hides the block.
- The block (`field_menu.json` `last_save`) sits above the objective on the root: "Last saved", the place and time (or "Not saved yet"), and "Rest at a save shrine to keep your journey." It hides off the root, as the objective does.
- The tutorial tips gain `menu_save` (after the field menu tip, on the next field_ready): the menu does not save; shrines and new chapters do. Seen-flag `tut_menu_save_seen`.
- Shots: `field_menu`, `field_menu_21x9`, `field_menu_16x10` re-approved after viewing (a fixed autosave at Haluna, UTC). Test: `tests/unit/test_field_menu_last_save.gd`.
- Reviewer: design.

## Review log
