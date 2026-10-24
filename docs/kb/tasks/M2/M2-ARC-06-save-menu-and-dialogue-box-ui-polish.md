---
id: M2-ARC-06
title: Save menu and dialogue box: follow UiSettings and match the other menus (from the UI polish pass)
role: architect
status: todo
owner_session: ""
depends_on: [M2-UI-09]
milestone: M2
request-from: ui
---
## Goal
M2-UI-09 (the slice UI polish pass) gave every menu the UI track owns the text-size, palette and reduced-motion settings (`UiSettings.follow(root)` in `_ready`) and one help-line style (`HelpDimLabel`). The save menu (`game/ui/save/**`, Systems) and the dialogue box (`game/ui/dialogue/**`, Architect) are outside UI's ownership (docs/kb/ownership.md), so this task asks their owners for the same treatment. Found by the M2-UI-09 audit.

## Acceptance criteria
- [ ] **Save menu (`save_menu.gd`):**
  - Call `UiSettings.shared().follow(self)` in `_ready`. Set `reduced_motion` on its MenuPages before `setup()`. Skip the open animation and the cursor slide under reduced motion (`save_menu.gd` ~344, ~357).
  - Use `HelpDimLabel` for the help line instead of a `text_dim` override (~234). Overrides are read once at build time, so they go stale on a palette switch.
  - **Bug:** hovering the dialog's choices moves the MenuPage cursor but not `model.dialog_cursor`. Connect `row_hovered` to the model, as `TitleMenu` now does.
  - Consider `_unhandled_input` instead of `_input` (~117), and choosing on the first click as the other menus do (~378).
- [ ] **Dialogue box (`dialogue_box.tscn` / `.gd`):**
  - Use theme variations instead of hard-coded font sizes: the speaker name in `HeaderLabel` (28 px serif small caps; it is 30 px today), and the body in `BodyLabel` (30 px; it is 34 px today).
  - Define `DialogueBodySung` in `game/data/ui/theme.json`, or drop it. The UI track can add the variation if asked.
  - Call `UiSettings.shared().follow(self)`, so text size and palette reach the box.
  - The box sits at x 160, 1600 × 252, but art/ui.md §7 says (320, 812), 1280 × 220. Confirm which one holds.
- [ ] Tests, and re-approve the shots that show these UIs after viewing them.

## Notes
- The API: `UiSettings.follow(root: Control)` (game/ui/settings/ui_settings.gd). It sets `root.theme` for the palette and text size now and on every change, until the root leaves the tree.
- `HelpDimLabel` is in theme.json: `HelpLabel` (24 px sans) in `text_dim`.

## Review log
