---
id: M2-UI-29
title: Resolution and aspect audit (16:9, 16:10, 21:9, 4K; text at 100 % and 130 %)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Lead queue item 4. Check every screen at:
- 16:9: 1920 x 1080, 1280 x 720 and 3840 x 2160;
- 16:10: 1920 x 1200, and the 1280 x 800 handheld;
- 21:9: 2560 x 1080 and 3440 x 1440;

each with the text size at 100 % and 130 %. Fix the anchoring and the overflow.

## How the window maps to the layout
`project.godot` stretches canvas items with aspect `expand` from 1920 x 1080. That setting is unchanged, so no ADR. The audited windows therefore lay out in four viewports:
- 1920 x 1080: every 16:9 window;
- 1920 x 1200: both 16:10 windows;
- 2560 x 1080: the 2560 x 1080 window;
- 2580 x 1080: the 3440 x 1440 window.

The extra room is always added at the right, or at the bottom. All UI rects are at the 1920 x 1080 reference, and before this task they were anchored top-left.

## Findings (before the fix)
"Off centre" means a composition designed centred on 1920 x 1080, held at its 1920 x 1080 coordinates.

| Screen | 16:9 | 16:10 (1920 x 1200) | 21:9 (2560/2580 x 1080) | Text at 130 % |
|---|---|---|---|---|
| Title (logo, menu, help) | ok | 60 px high (120 px empty at the bottom) | 320–330 px left of centre | ok |
| Settings hub and its pages (Graphics, Audio, Accessibility, Controls) | ok | ok (the panel grows downward from the top) | panel 330 px left of centre | ok |
| Field menu | ok | panel 60 px high | panel left of centre; right margin 1059 px vs 399 px | ok |
| Items, Equip, Lattice, Status, Formation, Memories | ok | 60 px high | left of centre | Formation: a wrapped detail line kept a 1432 px tall (invisible) box at every aspect |
| Map, Bestiary, Codex | ok | 60 px high | left of centre | ok |
| Shop, inn | ok | 60 px high | left of centre | ok |
| Save menu (Systems) | ok | 60 px high | left of centre | ok |
| Dialogue box (Architect) | ok | ok (pinned to the bottom) | pinned, but 2260 px wide: long lines | ok |
| Backlog | ok | 60 px high | left of centre | ok |
| Cutscene letterbox, choices, hold to skip (m2-slice) | ok | ok (anchor fractions) | ok | ok |
| Field HUD: objective line, interaction prompt, objective cue | ok | ok | ok (top-left; the prompt and cue follow the 3D projection) | ok |
| Field HUD: tip card (top right) | ok | ok | 704 px from the right edge | ok |
| Field HUD: codex notice (lower right) | ok | 120 px above the bottom | 704 px from the right edge | ok |
| Field HUD: area title | ok | ok | band and name centred on x = 960, not 1290 | ok |
| Battle: target info, boss status | ok | ok | ok | ok |
| Battle: help line, opening banner, Swell "unlocked" float | ok | ok | left of centre | ok |
| Battle: timeline | ok | ok | 640–660 px from the right edge | ok |
| Battle: party bars | ok | 120 px above the bottom | 640–660 px from the right edge | ok |
| Battle: command menu and sub-menus | ok | 120 px above the bottom | ok | row label boxes 46 px in 40 px rows, text 3 px low |
| Battle: Swell panels | ok | 120 px above the bottom | ok | the ring's hint is 539 px in a 480 px panel |
| Battle: Read panel, result panel | ok | 60 px high | left of centre | ok |
| Battle pause (Menus) | ok | 60 px high | left of centre | the help line is 848 px in 756 px |
| Scrims and backdrops (every menu) | ok | ok (full rect) | ok (full rect) | — |

1280 x 720 and 3840 x 2160 are identical to 1920 x 1080 (canvas_items stretch). 1280 x 800 is identical to 1920 x 1200.

## Acceptance criteria
- [x] **Full-screen menus are a centred 16:9 composition.** `UiFrame.centre(root)` (`game/ui/theme/ui_frame.gd`):
  - the root becomes the centred 1920 x 1080 frame;
  - its full-rect scrims and backdrops are stretched to the whole screen, and again on every window change;
  - a root that takes the mouse gets a pass-through `FrameCatcher`, so clicks beside the frame are still swallowed (and close the Read panel).
  - It is applied to FieldMenu, FieldSubmenu (party pages, Memories, backlog, battle pause), Bestiary, Codex, ZoneMap, SettingsMenu, SettingsPage, TownMenu (shop, inn), SaveMenu, TitleMenu, ReadPanel and BattleResultPanel.
- [x] **HUD pieces keep their margin to their own edge.** A layout section's optional `"pin"` is read by `HudLayout.place()`, `pinned_rect()` and `place_frame()`. Pinned:
  - battle: help line and opening banner (top); timeline (top right); party bars (bottom right); the command menu frame and the Swell panel (bottom left); the "unlocked" float (centre);
  - field: tip card (top right); codex notice (bottom right); area title band, name and rule (top).
- [x] **Overflow at 130 %:**
  - `UiFrame.fit_line()` shrinks the Swell hint and the pause help line, only down to their 100 % size;
  - MenuPage row labels grow both ways (they stay centred on the row);
  - Formation refreshes a wrapped line's minimum size before sizing it.
- [x] **Tests:** `tests/unit/test_aspect_layouts.gd` (11 tests) with `tests/aspect_host.gd`. Every screen group is checked at 16:9, 16:10, 21:9 and 43:18, with text at 100 % and 130 %, through a real window resize:
  - no Control leaves the screen;
  - no text runs out of its panel;
  - covers cover the screen;
  - frames are centred and reference-sized;
  - HUD pieces keep their 16:9 margins;
  - a live resize refits.
  - With the fix switched off, 8 of the 11 tests fail.
- [x] **Shots:** `field_menu_21x9`, `battle_hud_21x9` (1280 x 540, laid out in 2560 x 1080); `field_menu_16x10`, `battle_hud_16x10` (1280 x 800, laid out in 1920 x 1200).
- [x] **Existing shots checked:** boot_title, field_menu, battle_hud_preview, battle_read_panel, battle_swell_ring, battle_pause, settings_hub, shop_menu_buy, field_menu_codex, field_area_title, formation_menu and dialogue_backlog are unchanged (RMSE 0). save_menu is 0.003, within its limit. `field_tip_card` was re-approved after viewing: the card now keeps its 48 px right margin and grows leftward, so it sits 2 px further left (RMSE 0.026).
- [x] **Docs:** docs/kb/tech/ui.md § Resolution and aspect (M2-UI-29).

## Files outside UI ownership (small fixes, noted)
- `game/ui/save/save_menu.gd` (Systems): one line, `UiFrame.centre(self)`.
- `game/ui/menus/field_submenu.gd` (Menus): one line, `UiFrame.centre(self)`.
- `game/ui/menus/battle_pause/battle_pause_menu.gd` (Menus): `fit_line` on the help line (two lines).
- `game/ui/menus/formation/formation_menu.gd` (Menus): one line, `update_minimum_size()`.
- `game/ui/battle/command_menu.gd`, `read_panel.gd`, `battle_result_panel.gd`, `swell_ring_view.gd`, `swell_mode_rows.gd` and `game/data/ui/battle_hud.json` are game/ui/** (UI + Combat). Nothing under game/battle/scene/** changed, and `battle_controller.gd` is untouched.
- Not changed: `game/ui/dialogue/**` (Architect). The ultrawide dialogue box width is requested as **M2-ARC-09**.

## Notes
- Menus stay a 16:9 composition at 21:9, so the title's build label sits at the frame's corner, not the screen's. That is deliberate: a menu is one composition.
- A label's `set_size()` stores a size clamped to a stale minimum. Headless tests never reach a frame's end, so `AspectHost.settle()` runs the deferred layout first; without it, containers and wrapped labels read as overflow.

## Review log
