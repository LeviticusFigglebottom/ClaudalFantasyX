---
id: M2-MNU-305
title: Menu motion for the bestiary, codex, zone map, save and Settings screens
role: ui
status: todo
owner_session: ""
depends_on: [M2-MNU-303]
milestone: M2
request-from: ui
---
## Goal
M2-MNU-303 gave the field menu and every FieldSubmenu page an open and close transition (`MenuMotion`, `game/data/ui/menu_motion.json`). The UI track's own full-screen screens (BestiaryMenu, CodexMenu, ZoneMapMenu, SaveMenu, SettingsMenu and its pages) are not FieldSubmenus and still snap open and shut, so the field menu now moves while the screens it opens do not.

## Acceptance criteria
- [ ] Each screen builds a `MenuMotion` over its root in `_ready` (`play_in`, with `static_backdrop` when it opens over the field menu) and plays `play_out` on close, emitting `closed` at once and freeing its layer on `MenuMotion.gone`, as FieldSubmenu does.
- [ ] Reduced motion stays instant; captures unchanged (30 settle frames).
- [ ] Tests as in `tests/unit/test_menu_motion.gd`.

## Notes
- These files are the UI track's (claude/ui) and change often, so the menus track has not touched them. Whoever takes this should be on claude/ui, or claim it there first. The menus track can do it on the Lead's word.

## Review log
