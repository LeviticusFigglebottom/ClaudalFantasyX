# Handoff: ui, 2026-10-24 #11 (pseudo-localisation)

Session: the UI track (session_01NyuYPSZn7o7gYirTvz4zjs). Worktree agent on a branch from `claude/ui` 2b9012d5. Task: **M2-UI-28** (Lead queue item 3), now in `review`, reviewer lead.

## Done
- **`PseudoLoc`:** a debug pseudo-locale `en_XA`, about 40% longer, accented and bracketed, with placeholders, formats, BBCode and newlines kept.
  - It turns on with `--pseudo-loc`, `HYMN_PSEUDO_LOC=1` or F10 in the debug overlay.
  - Files: `game/core/debug/pseudo_loc.gd` and `game/data/debug/pseudo_loc.json`.
- **`TextFitProbe`** (`tests/text_fit_probe.gd`) and **`tests/unit/test_pseudo_loc_screens.gd`**: every screen group at 100% and 130% text.
- **`test_pseudo_locale.gd`** is refocused on the generator, the switch and the release guard.
- **Fixes:**
  - `HudLayout.wrap_upward` for help and hint lines: field menu, shop and inn, Swell panels, FieldSubmenu.
  - `EnemyPageView.max_width`.
  - MenuPage headers ellipsize.
  - TownMenu follows the text size.
- Findings per screen are in `docs/kb/tasks/M2/M2-UI-28-pseudo-localisation.md`, and the rule in docs/kb/tech/ui.md "Pseudo-localisation".

## Gates
- gdlint and gdformat clean. `validate_data`, `taskboard --check` and `unittest test_loc_literals` pass.
- **Godot:** `pseudo`, `input_parity`, `battle`, `menu`, `field_menu`, `shop`, `inn`, `town`, `bestiary`, `read`, `swell`, `hud`, `debug_overlay`, `title`, `ui_` and `loc` all pass.
- **Shots:** 22 captured, all RMSE 0, none updated.

## In progress
- None.

## Exact next step
1. The Lead merges the branch.
2. **M2-MNU-11** (Menus track) fixes the Status and Customize overflows and deletes their `KNOWN` rows.
3. **M2-FP-29** (m2-slice) makes the cutscene choices follow the text size.

## Known issues
- **Ellipsis warnings** remain (a list in M2-MNU-11 and the task file). They are for review, not failures.
- **Text size is not followed** by the save menu and the dialogue box yet (M2-ARC-06 and M2-ARC-07, open).

## Files touched
- **UI:**
  - `game/ui/battle/{hud_layout,enemy_page_view,menu_page,read_panel,swell_ring_view}.gd`
  - `game/ui/{bestiary/bestiary_menu,field_menu/field_menu,shop/town_menu,input/ui_input}.gd`
- **Menus track:** `game/ui/menus/field_submenu.gd` (one line).
- **Systems:** `game/core/debug/{pseudo_loc.gd,debug_overlay.gd}`, `game/data/debug/{pseudo_loc.json,debug_overlay.json}`.
- **Tests:** `tests/text_fit_probe.gd`, `tests/unit/test_pseudo_loc_screens.gd`, `tests/unit/test_pseudo_locale.gd`.
- **Docs:** `docs/kb/tech/ui.md` and `docs/kb/tasks/M2/M2-{UI-28,MNU-11,FP-29}-*.md`.
