---
id: M2-UI-09
title: Slice UI polish pass (an Accessibility page with text size, one Settings hub, consistent type and navigation)
role: ui
status: review
owner_session: "claude/ui"
reviewer: lead
depends_on: [M1-UI-10, M2-UI-04]
milestone: M2
request-from: lead
---
## Goal
The Lead's queue item 4 for the slice review: the menus a player meets in the slice (field menu, bestiary, Read panel, Swell menus, Vowbound HUD, settings) should read as one system, work from keyboard and controller everywhere, and the text-size option that `UiSettings` has had since M1-UI-02 should be reachable and apply outside battle.

## Acceptance criteria
- [x] An Accessibility page (reduced motion, text size, palette, timing assist) over `UiSettings`, built like the Graphics page; every change saves and applies at once.
- [x] One Settings hub (Graphics, Accessibility) opened from the title's Settings row and from a new Settings row in the field menu.
- [x] Text size, palette and reduced motion apply to the field menu, the bestiary, the settings pages and the title, not only the battle HUD.
- [x] The audit's typography, spacing and navigation inconsistencies are fixed or listed with a reason.
- [x] Loc keys for every string; tests; screenshots for the new pages (and the shots the fixes move, re-approved after viewing).

## Notes
- The shop and inn menus are m2-slice's (M2-UI-06 on claude/m2-slice); ideas for them are in docs/kb/handoffs/live/ui.md.

## Implementation notes (claude/ui, 2026-10-24)
Details are in tech/ui.md § Settings, accessibility and the polish pass. In short:
- **Settings hub (`SettingsMenu`):** Graphics and Accessibility, opened from the title and from the field menu's new Settings row (its own CanvasLayer 66, working while the field is paused).
- **Shared settings view:** `SettingsPage` + `SettingsPageModel`. `GraphicsMenu` is now a thin subclass, with its value formats as loc keys. `AccessibilityMenu` covers reduced motion, text size, palette and timing assist; each change saves at once and re-themes live.
- **`UiSettings.follow(root)`:** the field menu, the bestiary, the title, the hub and the pages take the text size and palette live, and their MenuPages take reduced motion.
- **Consistency:** a `HelpDimLabel` theme variation replaces the per-menu help overrides (theme rebuilt). The field menu's "In use" is in swell, as in battle.
- **Navigation:**
  - The bestiary pages with page up/down or left/right, and the wheel steps it.
  - The title's hover now moves its model, which was a bug.
  - The settings pages follow hover.
- **Not changed, with reasons** (tech/ui.md): the MenuPage metric families, the bestiary/save rects that are not multiples of 3, the field description's BodyLabel, and the Vowbound tint fallback.
- **Request filed:** M2-ARC-06 for the save menu and dialogue box (other owners).
- **Tests:** `test_settings_menu.gd` (11); `test_field_menu.gd` and `test_graphics_menu.gd` updated for the Settings row and the hub. Full suite 1475 run, 0 failed.
- **Shots:** new `settings_hub` and `settings_accessibility`. Re-approved after viewing: `field_menu`, `field_menu_swell_modes` and `bestiary_menu`. `boot_title` is unchanged (rmse 0).

## Review log
