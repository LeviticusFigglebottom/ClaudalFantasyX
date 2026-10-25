---
id: M2-AUD-14
title: Sounds inside the menus track's pages: item use and sort, formation swap, customize, map pan
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio; worktree agent)"
depends_on: [M2-AUD-02]
milestone: M2
request-from: lead
---
## Goal
claude/menus' pages (Items, Formation, Customize, the zone map) get their own sounds; M3-AUD-15 already covers Lattice, Equip, the map open and close, tips and the title.

## Acceptance criteria
- [x] Synthesized UI sounds at -20 LUFS with PROVENANCE rows; ui_sfx.json hooks by class and signal name (pending until claude/menus merges); tests.

## Notes
- 2026-10-24 audio: `assets_src/sfx/menu_page_sfx.py` (render_all job `menu_page_sfx`, byte-identical across two
  renders) renders `ui_item_use`, `ui_item_sort`, `ui_formation_pick`, `ui_formation_swap`, `ui_customize_open`,
  `ui_craft` and `ui_map_pan` with menu_sfx.py's helpers and palette. Decoded at -19.96 to -20.36 LUFS momentary
  max, true peak -2.96 to -10.73 dBTP. Rows in `game/data/audio/sfx_ui_pages.json` (`ui_map_pan` has a 110 ms
  cooldown and volume_db -6).
- Hooks (`ui_sfx.json`, pending): new `ItemsMenu` and `FormationMenu` hooks; `EquipMenu` gains Customize's
  `level == 3` (RECIPES) and `crafted_count(bag)` rows; `ZoneMapView` gains a pan watch. New UiAudio helpers:
  `item_total`, `crafted_count`, `pans`. Names read from origin/claude/menus @ bd7ff520.
- Customize is not its own page on claude/menus: it is EquipMenu's RECIPES level (M2-MNU-09).
- The zone map has no pan on claude/menus (`ZoneMapView` fits the zone). The pan watch is scale-checked, so a
  resize stays quiet, and it plays once a pan lands. The only pannable board is the Lattice's (no hook; see
  docs/kb/tech/audio_runtime.md "The menus track's pages").
- Not heard: refused uses or moves on Items and Formation, and Customize's arming Confirm. Each result is held
  only in the page's private `_notice` / `_armed`.
- Tests: `tests/unit/test_field_audio.gd::test_ui_hooks_play_items_formation_customize_and_map_pan` (stand-ins built
  at runtime and named by `audio_class`). The M3-AUD-15 Equip test's craft step now expects `ui_craft`.

## Review log
