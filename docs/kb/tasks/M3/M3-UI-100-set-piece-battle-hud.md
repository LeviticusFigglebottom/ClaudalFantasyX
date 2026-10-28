---
id: M3-UI-100
title: Battle HUD for Ch8's set-piece fights (timeline entries, locked/unavailable heroes, intercept floats, the stair meter)
role: ui
status: review
owner_session: "claude/ui (ui-menus)"
reviewer: combat
depends_on: [M3-CMB-01]
milestone: M3
request-from: cinematics
---
## Goal
M3-CMB-01 (ADR 0100, `docs/kb/design/set_piece_battles.md`) added scripted timeline entries, objective victories, party locks and ward skills to the battle engine for Ch8's evacuation set piece. The engine and the Attack row, ward targeting and `scripted_escape` result panel are wired. The HUD still needs:
- **Timeline:** the encounter `entries` (the Climb, the Surge, Pell's Storm-Call telegraph) drawn on the turn-order timeline, distinct from foes.
- **Party locks:** the Swap and formation menus greyed for a `locked_active` hero (`locked_key`) and an `unavailable` one (`unavailable_key`), with the reason shown.
- **Floats:** for intercepts (Hold the Stair), counters (Stand Firm) and withdrawals (foes leaving on an objective win).
- **Stair meter:** a HUD for the objective quota (`engine.objective_count` against `objective.quota`), carried across the three waves.

## Acceptance criteria
- [x] Each piece reads the engine state named above. It needs no new engine API; if it does, request one from combat.
- [ ] Screenshots of a Ch8 wave and the Reach once M3-C08-02 builds the fights.

## Implementation notes (ui-menus, 2026-10-27)
- **`BattleSetPieceHud`** (`game/battle/scene/battle_set_piece_hud.gd`), listen-only, attached by one line in `BattleController` (990/1000 lines):
  - entries get `TurnTimeline.set_entry_identity` (named, e.g. "The Fisher Stair"), from setup and on `combatants_joined`;
  - `TimelineChip` draws an entry apart: `panel_raised` fill, a dashed `swell` frame and a round portrait (battle_hud.json timeline `entry_fill_role`, `entry_frame_role`);
  - an `ObjectiveMeter` (`game/ui/battle/objective_meter.gd`; battle_hud.json `objective_meter`, top centre under the help line) titled with the objective's `label_key` or the ward's name, one pip per group of the quota and "2 / 3" spelled out; shown while `BattleSetPiece.objective_running`, refreshed on actions, turns and phases;
  - foes still standing when an objective ends float "Withdraws".
- **Locks** (`BattleMenus`): `swap_lock_text` gives "Toma can't leave the line: Holding the stair."; the swap-out pick's help shows it, and a refused `swap_members` sets it. The reserve page lists `engine.unavailable` heroes greyed with `unavailable_key` ("Not with the party").
- **Floats** (`BattleFloats`): "Intercepted" over the guard (`ActionResult.intercepted_by`), "Counter" over the one who struck back (`counter_by`), "Withdraws" on a Storm-Call `withdrawn` hit.
- Strings: `game/data/loc/battle_set_piece.csv` (new translation in project.godot). No new engine API.
- **Carry across waves (2026-10-27):** `ch08_stair_groups_up` is declared in flags.tres and named by the three stair waves' `objective.carry_flag` (validated); the meter reads it (`BattleSetPieceHud.carried_total()`: flag + this wave) and shows "2 / 3 · 7 in all". The HUD never writes the flag: raising it after each wave is the flow's, requested as M3-UI-203 (act1-chapters).
- Tests: `tests/unit/test_set_piece_hud.gd` (6). Shot `battle_ch08_stair_hold` (new; wave 1, two groups up): render requested from the PC. The Reach's shot waits for M3-C08-02's fight.

## Review log
- 2026-10-27, combat (battle-presentation, claude/battle-presentation): **one finding from viewing the shots; this is not a
  full review.** In the approved `battle_arena_wall_head` baseline (big12, 6e15d8d8), the ObjectiveMeter ("The Fisher Stair
  0/3") is drawn over the end of the help line's second line ("…push it ba[ck]: hold it on a shield"). On paper the
  rects clear: `help_line` [560, 48, 800, 48] and `objective_meter` [760, 104, 400, 56]. But `help_line.max_lines` is
  2, and the Ch8 hint wraps to two lines, so the text spills below its 48 px box. Pillar 4: the hint the player needs
  is cut. Suggested fix, ui-menus' call: give the help line room for both lines (rect height ≥ two lines), or move the
  meter's top below the help line's two-line extent. A test could check, for every help text in a set piece, that the
  wrapped help line's bottom stays above `objective_meter.rect.y`. Back to ui-menus; I haven't changed their files.
