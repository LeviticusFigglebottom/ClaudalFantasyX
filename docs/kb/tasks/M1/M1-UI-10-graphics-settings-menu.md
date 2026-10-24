---
id: M1-UI-10
title: Graphics section of the settings menu (calls GraphicsRuntime)
role: ui
status: review
reviewer: architect
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M1-ARC-15]
milestone: M1
request-from: "architect"
---
## Goal
There is no graphics settings screen yet (game/ui/settings/ holds only the accessibility backend,
UiSettings). M1-ARC-15 added the runtime side, so the menu only has to list and call it.

## Acceptance criteria
- [x] A Graphics section lists the presets (`GraphicsRuntime.settings().preset_ids()`, `name_key`) and
      each setting (`settings().data["settings"]`: `label_key`, `options`), showing "Custom" when
      `settings().is_custom()`.
- [x] Choosing a preset calls `GraphicsRuntime.select_preset(id, get_viewport())`; changing one setting
      calls `GraphicsRuntime.set_override(key, value, get_viewport())`. Both save user://settings.cfg and
      apply at once (global part and the current scene). Apply behind a short fade if a change hitches
      (shadow-atlas resize, SDFGI reconverge, glimmer emitter restart).
- [x] Loc rows for the `GFX_*` keys that are still missing (graphics_settings.md, Open items).
- [x] A test drives the menu: select Low, assert `GraphicsRuntime.settings().preset_id == "low"` and the
      saved file.

## Notes
API and behavior: docs/kb/tech/graphics_settings.md, "Applying in the game (M1-ARC-15)".

- 2026-10-24 m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC):
  - `GraphicsMenu` and `GraphicsMenuModel` in `game/ui/settings/`; layout and value labels in `game/data/ui/graphics_menu.json`. The title gains a **Settings** row, enabled with or without a record; `title_menu.json` now has `max_rows` 4 and its help line is moved down to y 846. Docs: graphics_settings.md, "The Graphics menu".
  - The `*_key` label rows already existed. Added the value and menu rows (`GFX_VALUE_*`, `GFX_MENU_*`, `GFX_PRESET_CUSTOM`, `TITLE_SETTINGS`, `TITLE_HELP_SETTINGS`). `tools/tests/test_graphics_menu_data.py` checks every option has a label.
  - **No fade.** The page lives on the 2D title, so a change can't visibly hitch. A pause menu (none yet) would add the fade.
  - **Baseline re-approved: `boot_title`** (the fourth row, Settings, and the help line lower). I viewed it side by side with the old baseline; nothing else moved.
  - Tests: `tests/unit/test_graphics_menu.gd` (6, including select Low → saved file and the viewport applied), and `test_title_menu.gd` updated for the new row. The full suite has 1263 tests green; tools unittest 448 OK.
  - Not done: a scroll hint (the page shows 14 of 26 rows and scrolls with the cursor), and per-setting help text (one help line for every setting row).

## Review log
