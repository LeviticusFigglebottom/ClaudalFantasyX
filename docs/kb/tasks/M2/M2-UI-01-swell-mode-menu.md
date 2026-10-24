---
id: M2-UI-01
title: Swell mode menu and timing-input accessibility
role: ui
status: done
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
- **Out of battle: not built.** After the merge with M2-ARC-01 and M2-CMB-01, modes and unlocks carry between battles and saves. `BattleSwellCarry.mode_rows` and `set_mode` are ready, but no party or Customize menu exists to hold a chooser. The in-battle page uses `swell.mode_rows(c)` and `swell.set_mode` (the M2-CMB-01 API).
- **Timing assist** (`timing_assist`: off / wide / auto, in accessibility.json). It is applied to the input row (`UiSettings.timing_input`), never in the grading code.
  - `wide`: perfect and good windows × 1.5, clamped inside the beat. Rhen's ring becomes 0.09 / 0.225 s.
  - `auto`: a miss counts as good, through `SwellInput.assist_floor` and `_record`, for every input kind (merge with M2-CMB-01). That is the one engine addition: Node-free, default empty, and tested.
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

## Notes
- 2026-10-23 (Combat, M2-CMB-01 / M2-ARC-01): the API is ready and documented in battle_ctb.md "Swell" (API for the Swell mode menu). In battle: `ctl.swell.mode_rows(c)`, `set_mode(c, mode)`, `unlocked`, `progress_toward(mode)` and the `mode_unlocked` signal. Out of battle: `BattleSwellCarry.mode_rows(cid)`, `set_mode(cid, mode)` and `rules()` over `Game.state`. Modes carry between battles and in saves (save v6).

- **Gate after merging claude/new-session-mj8c3c (merge 9186104):** the scoped `tools/ci_local.sh` with all 9 battle and bestiary shots gives rc 0. 1169 Godot tests, 0 failed. Coverage: battle 99.94% (1770/1771), progression 96.52%, within baseline. All shots at rmse 0, so none needed re-approval.

## Review log
- 2026-10-24 review-sweep-O (combat): **approve with fixes.** Criteria 1 and 2 hold. Criterion 3 is Art's, and M2-ART-01 tracks it. That task depends on this one, so it can start now.
  - **What I read:** battle_menus.gd `swell_rows` and `swell_mode_rows`, swell_mode_rows.gd, ui_settings.gd `timing_input` (:137-160, :285-289), swell_input.gd `assist_floor` and `_record` (:53-62, :160-168), accessibility.json `timing_assist`, battle_controller.gd:699, and formulas.md § Swell "Timing assist".
  - **Checks:** Godot `--filter=` swell 124/0 failed, swell_mode 15/0, ui 87/0, battle 307/0. gdlint and gdformat are clean.
  - **Combat confirms formulas.md "Timing assist"** (UI's proposal):
    - The numbers live in accessibility.json, not in code.
    - The assist changes the row before `SwellInput.create`, and `assist_floor` maps a miss to that step's scripted good grade. Both are Node-free and use no RNG, so the engine stays deterministic.
    - Balance: `auto` makes a masher play at `good`, and `naive_swell` at good is 23.8% (M2-CMB-02), under the 25% line. So the assist needs no band of its own.
  - **Nit:** `_record` indexes `scripted_grades(assist_floor)[grades.size()]`. That's safe today, because every kind records at most `grade_count()` steps. An assert there would catch a future kind that records more.
  - **Filed as M2-UI-04:** the out-of-battle mode chooser, which isn't built for lack of a party or field menu (criterion 1 allows "and/or"). No task held it.
