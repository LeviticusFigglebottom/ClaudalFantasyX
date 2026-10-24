---
id: M2-UI-10
title: UI flair (the human's request): panel ornament, a lamplit cursor, header rules, caustic backdrops
role: ui
status: review
owner_session: "claude/ui"
reviewer: character
depends_on: [M2-UI-09]
milestone: M2
request-from: lead
---
## Goal
The human asked for the general menus and the UI theme to have more flair and look less plain. ADR 0033 records the decision and its limits (gold discipline, legibility, reduced motion, no copied UI).

## Acceptance criteria
- [x] Panels: a surface glint, corner ticks, and tide lines on tall panels, all theme data.
- [x] The cursor: a lamplit gradient fill and wash inside the gold frame and glow; the cursor row's text nudges right (and snaps under reduced motion).
- [x] Gold header rules under titled pages and menu titles.
- [x] Caustic backdrops behind the full-screen menus: still under reduced motion and deterministic in captures.
- [x] Tests (`tests/unit/test_ui_flair.gd`); the affected baselines re-approved after viewing them.

## Notes
- **Art review asked:** tune the values in theme.json, or ask for any piece to be turned off. Each one is data: `corner_tick_px` 0, `tide_lines` 0, `glint_span_pct` 0, `cursor_nudge_px` 0, and `caustic` alpha 0. Then fold the accepted pieces into art/ui.md (Art's file).
- **Also fixed:** the Settings hub and settings pages (including the Graphics page) anchored to zero size, so their backdrop never dimmed the screen.
- **Baselines re-approved after viewing (21):** boot_title, all battle_* shots, drownbell_flood, save_menu_overwrite, bestiary_menu, field_menu, field_menu_swell_modes, settings_hub and settings_accessibility.

## Review log
