---
id: M2-UI-01
title: Swell mode menu and timing-input accessibility
role: ui
status: review
owner_session: "worktree-agent-ab3d864d1e75fe481"
depends_on: [M1-CMB-04]
milestone: M2
request-from: combat
---
## Goal
SPEC §6.2 says the mode is selectable. M1-CMB-04 ships the rules (`BattleSwell.set_mode`, `unlocked`) with no menu, and Rhen's timing ring with no assist option.

## Acceptance criteria
- [x] Players can choose a hero's fill mode from the unlocked ones, out of battle (party or Customize menu) and/or from the battle Swell page. Each mode row shows `name_key` and `desc_key`.
- [x] An accessibility setting for timing inputs, such as a wider window or auto-good, applied through the input row rather than in the engine. Coordinate with Combat on the numbers in formulas.md § Swell.
- [ ] (requested: M2-ART-01) Art review of the Swell gauge placement and the ring panel (see tech/ui.md "Swell", deviations).

## Notes
- **Reviewer: combat.** The formulas.md § Swell "Timing assist" paragraph is UI's proposal, appended for Combat to confirm. Branch `worktree-agent-ab3d864d1e75fe481`, not pushed. Docs: tech/ui.md § Swell fill modes and § Accessibility, deviation 12.
- **Mode choice, in battle.** The Swell root row stays on the menu for a Swell hero at any gauge: it shows the mode in force (dim) until the gauge is full, then the input, as before. The Swell page lists the techniques (greyed until full), then each unlocked mode (`name_key`, with "In use" or "No time" on the right). Highlighting a mode puts its `desc_key` and "Choosing it costs no time" on the help line, and the timeline shows no ghost. Choosing one calls `BattleSwell.set_mode`, redraws in place, and the turn stays with the same fighter. The glue is `SwellModeRows`, and the row text comes from `BattleMenus`.
- **Out of battle: not built.** Gauges and modes reset every battle until M2-ARC-01 carries `swell_mode` and `unlocked`, so a party-menu chooser would have nowhere to write. Neither a party menu nor a Customize menu exists yet. A mode chosen in battle lasts for that battle.
- **Timing assist** (`timing_assist`: off / wide / auto, in accessibility.json). It is applied to the input row (`UiSettings.timing_input`), never in the grading code.
  - `wide`: perfect and good windows × 1.5, clamped inside the beat. Rhen's ring becomes 0.09 / 0.225 s.
  - `auto`: a miss counts as good, through `SwellTimingRing.assist_grade`. That field is the one engine addition: Node-free, default empty, and tested.
  - The ring panel shows a short tag while the assist is on.
- **Controller (`battle_controller.gd`, still 997 lines, no lines added).** Five existing lines changed:
  - `tick()` gains the Read-panel hold (M2-UI-02).
  - `_on_menu_highlighted`'s guard calls `SwellModeRows.highlight`.
  - The Swell-page choice goes through `SwellModeRows.pick(..., _begin_target.bind(...))`.
  - The root Swell help comes from `menus.swell_root_help`.
  - The ring is built from `hud.settings.timing_input(row)`.
  These lines do not overlap the claude/first-playable hunks (checked against origin/claude/first-playable).
- **Shots:** new `battle_swell_modes` (fixture `swell_modes`: Rhen at 40, Wake highlighted). `battle_hud_preview` and `battle_swap_menu` were re-approved on purpose for the extra Swell row on Rhen's root (rmse 0.0096 and 0.0100 before). The player_preview capture script now selects Skills by id. `battle_swell_ring` is unchanged (rmse 0).
- **Tests:** `test_swell_mode_menu.gd` (12), 2 new in `test_swell_timing_ring.gd`, and updated root-row expectations in `test_battle_swell_hud`, `test_battle_controller`, `test_battle_item_menu` and `test_ui_settings`.
- M1-UI-05's open nits are untouched: a `target: "self"` technique, and the help line dropping "next in N" while the ring is open.
- **Gate:** `HYMN_SHOTS=battle_read_panel,battle_opening_banner,battle_swell_modes,bestiary_menu,battle_hud_preview,battle_swap_menu,battle_swell_ring,battle_statuses,battle_victory tools/ci_local.sh` rc 0 at b2dbe53: validate_data 0/0, tool tests 411 OK, audio 9 OK, taskboard, gdlint and gdformat clean, **1105 Godot tests, 0 failed**, coverage battle 99.93% (1524/1525) and progression 96.52% (unchanged from baseline), boot smoke OK, 9 shots at rmse 0. Filters beforehand: swell 62, bestiary 27, read_panel 12, swell_mode 12, ui 87, battle 287, all passing.

## Review log
