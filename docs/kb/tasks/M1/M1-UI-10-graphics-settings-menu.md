---
id: M1-UI-10
title: Graphics section of the settings menu (calls GraphicsRuntime)
role: ui
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M1-ARC-15]
milestone: M1
request-from: "architect"
---
## Goal
There is no graphics settings screen yet (game/ui/settings/ holds only the accessibility backend,
UiSettings). M1-ARC-15 added the runtime side, so the menu only has to list and call it.

## Acceptance criteria
- [ ] A Graphics section lists the presets (`GraphicsRuntime.settings().preset_ids()`, `name_key`) and
      each setting (`settings().data["settings"]`: `label_key`, `options`), showing "Custom" when
      `settings().is_custom()`.
- [ ] Choosing a preset calls `GraphicsRuntime.select_preset(id, get_viewport())`; changing one setting
      calls `GraphicsRuntime.set_override(key, value, get_viewport())`. Both save user://settings.cfg and
      apply at once (global part and the current scene). Apply behind a short fade if a change hitches
      (shadow-atlas resize, SDFGI reconverge, glimmer emitter restart).
- [ ] Loc rows for the `GFX_*` keys that are still missing (graphics_settings.md, Open items).
- [ ] A test drives the menu: select Low, assert `GraphicsRuntime.settings().preset_id == "low"` and the
      saved file.

## Notes
API and behavior: docs/kb/tech/graphics_settings.md, "Applying in the game (M1-ARC-15)".

## Review log
