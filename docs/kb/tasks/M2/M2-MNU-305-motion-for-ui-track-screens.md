---
id: M2-MNU-305
title: Menu motion for the bestiary, codex, zone map, save and Settings screens
role: ui
status: review
owner_session: "claude/ui (ui-menus)"
reviewer: lead
depends_on: [M2-MNU-303]
milestone: M2
request-from: ui
---
## Goal
M2-MNU-303 gave the field menu and every FieldSubmenu page an open and close transition (`MenuMotion`, `game/data/ui/menu_motion.json`). The UI track's own full-screen screens (BestiaryMenu, CodexMenu, ZoneMapMenu, SaveMenu, SettingsMenu and its pages) are not FieldSubmenus and still snap open and shut, so the field menu now moves while the screens it opens do not.

## Acceptance criteria
- [x] Each screen builds a `MenuMotion` over its root in `_ready` (`play_in`, with `static_backdrop` when it opens over the field menu) and plays `play_out` on close, emitting `closed` at once and freeing its layer on `MenuMotion.gone`, as FieldSubmenu does.
- [x] Reduced motion stays instant; captures unchanged (30 settle frames).
- [x] Tests as in `tests/unit/test_menu_motion.gd`.

## Notes
- These files are the UI track's (claude/ui) and change often, so the menus track has not touched them. Whoever takes this should be on claude/ui, or claim it there first. The menus track can do it on the Lead's word.

## Implementation notes (ui-menus, 2026-10-25)
- BestiaryMenu, CodexMenu, ZoneMapMenu and SettingsMenu: `signal gone`, `over_menu`, a `MenuMotion` built in `_ready` (`play_in(over_menu)`), `play_out` on `close()` after which `gone` fires; `open_in(..., over)` frees the layer on `gone`. FieldMenu passes `over = true` for all four. The hub frees itself on `gone` too (the title instances it without a layer).
- SettingsPage: always over the hub (static backdrop); on close the hub's rows fade back in over `return_sec` while the page fades out, then the page frees itself.
- SaveMenu: keeps its own `panel_open` rise (now skipped under Reduced motion) and fades out on close; `animate = false` keeps the close instant.
- `ParityHost.back()` finishes the closing screen's fade before freeing queued layers (play does that a few frames later); `test_bestiary_menu` finishes it before checking the layer.
- Tests: `tests/unit/test_screen_motion.gd` (7): content-only motion over the field menu, scrim fading over the world, Reduced motion instant, the field menu opens each over itself and fades back in, a Settings page crosses over the hub, the save menu fades after `closed`, no panel rise under Reduced motion.
- Captures: every duration ends inside the 30 settle frames (checked by test_menu_motion), so the screens' shots grab them at rest.

## Review log
