---
id: M2-MNU-11
title: Status ability line and Customize change list fit a longer language at 130% text (from M2-UI-28)
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-UI-28]
milestone: M2
request-from: ui
---
## Goal
The pseudo-locale screen walk (M2-UI-28, `tests/unit/test_pseudo_loc_screens.gd`) found two overflows in the Menus track's pages at 130% text. They are in the test's `KNOWN` list, printed as warnings, until fixed.

## Acceptance criteria
- [ ] **Status page:** the worn gear's ability line (`status_menu.gd` `_line(..., wrap = true)`) runs 6 px past the panel at 130%: its column rect starts at x 1185 and is 522 px wide, but the panel ends at 1701. Keep the column inside the panel at every text size.
- [ ] **Customize:** the change list (`equip_menu.gd` `_changes`, `clip_contents`) cuts the last 3 px of a two-line change ("Tide Pearl: 1 of 4, 3 short") at 130%, with no sign of the cut. Give it the room, or ellipsize it.
- [ ] Delete both rows from `KNOWN` in `tests/unit/test_pseudo_loc_screens.gd`. `-- --filter=pseudo` passes with no `KNOWN` line printed.

## Notes
- Run it with `godot --headless --path . res://tests/run_tests.tscn -- --filter=pseudo_loc`. Every finding names the screen, the scale, the node path, the rect needed and the box.
- **Ellipses to review** (warnings, not failures). With German about 30% longer than English, these will cut real words:
  - Equip: stat names ("Magic Defense", 241 px for 192 even at 100%).
  - Equip: gear names in the list and the preview.
  - Equip: the "Customize <piece>" and "<slot> for <hero>" headers.
  - Items: "Asha (fallen)" in the hero picker.
  - Lattice: "Wake it (1 Ability Facet)" and node names in the activate panel.
  - Memories: chapter titles at 130%.
- **Already done for you, from M2-UI-28:**
  - `FieldSubmenu._framed_panel`'s help line now goes through `HudLayout.wrap_upward` (one line), so long help wraps upward from the panel's foot. No shot moved.
  - MenuPage headers ellipsize.

## Review log
