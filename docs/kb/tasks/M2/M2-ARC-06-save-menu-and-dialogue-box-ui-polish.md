---
id: M2-ARC-06
title: Save menu and dialogue box: follow UiSettings and match the other menus (from the UI polish pass)
role: architect
status: review
owner_session: "claude/ui (ui-menus owns the save menu and the dialogue box since 2026-10-25)"
depends_on: [M2-UI-09]
milestone: M2
request-from: ui
---
## Goal
M2-UI-09 (the slice UI polish pass) gave every menu the UI track owns the text-size, palette and reduced-motion settings (`UiSettings.follow(root)` in `_ready`) and one help-line style (`HelpDimLabel`). The save menu (`game/ui/save/**`, Systems) and the dialogue box (`game/ui/dialogue/**`, Architect) are outside UI's ownership (docs/kb/ownership.md), so this task asks their owners for the same treatment. Found by the M2-UI-09 audit.

## Acceptance criteria
- [x] **Save menu (`save_menu.gd`):**
  - Call `UiSettings.shared().follow(self)` in `_ready`. Set `reduced_motion` on its MenuPages before `setup()`. Skip the open animation and the cursor slide under reduced motion (`save_menu.gd` ~344, ~357).
  - Use `HelpDimLabel` for the help line instead of a `text_dim` override (~234). Overrides are read once at build time, so they go stale on a palette switch.
  - **Bug:** hovering the dialog's choices moves the MenuPage cursor but not `model.dialog_cursor`. Connect `row_hovered` to the model, as `TitleMenu` now does.
  - Consider `_unhandled_input` instead of `_input` (~117), and choosing on the first click as the other menus do (~378).
- [x] **Dialogue box (`dialogue_box.tscn` / `.gd`):**
  - Use theme variations instead of hard-coded font sizes: the speaker name in `HeaderLabel` (28 px serif small caps; it is 30 px today), and the body in `BodyLabel` (30 px; it is 34 px today).
  - Define `DialogueBodySung` in `game/data/ui/theme.json`, or drop it. The UI track can add the variation if asked.
  - Call `UiSettings.shared().follow(self)`, so text size and palette reach the box.
  - The box sits at x 160, 1600 × 252, but art/ui.md §7 says (320, 812), 1280 × 220. Confirm which one holds.
- [x] Tests, and re-approve the shots that show these UIs after viewing them.

## Notes
- The API: `UiSettings.follow(root: Control)` (game/ui/settings/ui_settings.gd). It sets `root.theme` for the palette and text size now and on every change, until the root leaves the tree.
- `HelpDimLabel` is in theme.json: `HelpLabel` (24 px sans) in `text_dim`.

## Implementation notes (ui-menus, 2026-10-25)
- **Save menu:** `UiSettings.shared().follow(self)` before the build (text size and palette); the help line is `HelpDimLabel` and the subtitle a new `FlavorDimLabel` (theme.json), so no colour overrides go stale; the open rise (M2-MNU-305) and the cursor slide are skipped under Reduced motion. The hover bug was already fixed by M2-UI-26 (`row_hovered` sets `model.dialog_cursor`). `_input` stays: the menu must take input ahead of the field while the shrine holds it (no change seen worth the risk).
- **Dialogue box:** `SubtitleStyle` (M2-UI-30) already follows UiSettings and sets the name and line sizes from theme variations at runtime, so the .tscn sizes are only fallbacks. `DialogueBodySung` is now defined in theme.json (italic body, 30 px); `hymn_theme.tres` regenerated with `build_theme.gd`.
- **Box placement:** kept at 1600 x 252 from x 160 (now centred and capped at 21:9, M2-ARC-09). art/ui.md §7's 1280 x 220 is older; the wider box fits two lines of the 130 % text size, so this track keeps it and art can say otherwise.
- Checks: save 194/0, theme 8/0, dialogue 76/0; save_menu, save_menu_overwrite, dialogue_continue unchanged against their baselines.

## Review log
