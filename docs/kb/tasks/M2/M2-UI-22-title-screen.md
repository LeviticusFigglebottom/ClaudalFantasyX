---
id: M2-UI-22
title: Title screen with an original logotype, an animated backdrop and a debug-only build label
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Intro audit item 3: the title screen is the first thing a player sees, so it should feel like the game (beautiful, a little doomed, underwater), not a bootstrap placeholder.

## Acceptance criteria
- [x] An original logotype for "Hymn of the Undertow" built from code and theme data (`TitleLogo`): the title serif, a small-caps "of the" between gold rules, and a drawn tide flourish. No images.
- [x] An animated backdrop behind the menu (`TitleBackdrop`): the caustic layer (ADR 0033), faint light shafts and drifting motes; still under reduced motion; deterministic under `--fixed-fps` captures (seeded layout, own elapsed time).
- [x] The build label shows only in debug builds (`OS.is_debug_build()`, or data `version.debug_only` false); boot's placeholder Label is removed.
- [x] Existing title behaviour and `test_title_menu.gd` unchanged and passing; new tests in `test_title_screen.gd`; data in `title_menu.json`; the `boot_title` baseline re-approved after viewing.

## Notes
`game/ui/title/title_logo.gd`, `game/ui/title/title_backdrop.gd`, `game/ui/title/title_menu.gd` / `.json`, loc rows `TITLE_LOGO_*` and `TITLE_BUILD_LABEL`. The removal of boot's Label touches `game/core/boot.gd` and `boot.tscn` (Systems Architect paths), as the Lead asked for the label change. docs/kb/tech/ui.md § Title screen (M2-UI-22).

## Review log
