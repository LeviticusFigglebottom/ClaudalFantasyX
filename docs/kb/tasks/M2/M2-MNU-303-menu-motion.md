---
id: M2-MNU-303
title: Menu motion polish: page transitions, cursor easing, focus sounds, Reduced motion
role: ui
status: review
reviewer: design
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-05]
milestone: M2
request-from: lead
---
## Goal
The playtest note "parts look primitive": the menus snap. Give the field menu's pages a short open and close transition, ease the cursor between rows, play audio's `ui_sfx` focus sounds, and honour Reduced motion everywhere (no slide, no ease: instant).

## Acceptance criteria
- [x] Page transitions (open and close) on FieldSubmenu pages and the field menu; durations in data.
- [x] Cursor easing on menu rows; instant under Reduced motion.
- [x] Focus sounds through audio's `ui_sfx` hooks (no direct sound calls in pages beyond what the hooks expect).
- [x] Captures and tests are deterministic (motion settles or is skipped in captures).
- [x] Tests for both Reduced motion on and off.

## Notes
- `MenuMotion` (game/ui/menus/menu_motion.gd) drives the field menu's and every FieldSubmenu page's open/close; durations in game/data/ui/menu_motion.json: open 0.18 s (cubic out, 18 px rise at the reference), close 0.12 s (cubic in, sink), field-menu return 0.12 s. A page over the field menu (`over_menu`) keeps the shared scrim and caustics still and fades only its content; the field menu fades its content back in when a page, the bestiary, codex, map or Settings closes over it.
- `close()` still refuses input and emits `closed` at once; new `gone` signal after the fade frees the layer (mount, FieldMenu.open_in). A closing menu ignores the pointer instead of hiding at once.
- Cursor easing already existed in MenuPage; added `cursor_rect()` and `settle()` (tests), and `MenuMotion.follow_reduced_motion` keeps open pages' cursors on the live setting.
- ui_sfx.json: `pending` cleared on FieldSubmenu, LatticeMenu, EquipMenu, ItemsMenu, FormationMenu (classes, signals and every watch expression checked on the real pages in test_menu_motion); rows appended for StatusMenu, MemoriesMenu, BattlePauseMenu. test_field_audio's pending check narrowed to ZoneMapMenu, ZoneMapView, TipCard (UI track).
- Reduced motion: everything instant. Captures settle 30 frames at fixed 60 fps (0.5 s) > every duration, so baselines are unchanged.
- Docs: docs/kb/tech/ui.md § Menu motion.

## Review log
