---
id: M2-ARC-01
title: Carry Swell gauges and modes between battles and in saves
role: architect
status: review
reviewer: qa
owner_session: worktree-agent-a670939c5cb593976
depends_on: [M1-CMB-04, M1-CMB-08]
milestone: M2
request-from: combat
---
## Goal
In M1-CMB-04, a Swell gauge lives only for one battle. It should follow the party like HP and MP do (M1-CMB-08), along with each hero's chosen mode and the unlocked modes.

## Acceptance criteria
- [x] `BattleCombatant.swell` and `swell_mode` go out through `EventBus.battle_party_returned` and come back in through `Game.vitals_modifier()` (`BattleVitals`), after a victory or an escape. A defeat writes nothing back.
- [x] `BattleSwell.unlocked` is saved and restored. Decide whether a save shrine's rest empties gauges; the combat default is that it does not.
- [x] The save shape has its fields, with a version note in architecture.md "Saves" and tests.

## Notes
- Engine side: `BattleSwell.attach()` keeps a `swell_mode` that is already set, and `swell` is plain state on the combatant, so nothing in `game/battle/` needs to change.

- 2026-10-23 architect (worktree-agent-a670939c5cb593976): ready for review (reviewer **qa**, as for ARC-06/13).
  - Save v6 (`_migrate_v5_to_v6`, frozen literal, chained after v4 → v5). Gauges and modes in `party_vitals` (`swell`, `swell_mode`; default mode stored as no value); the party record in `GameStateData.swell`. SaveShape checks all three; DataHealth's eighth check `swell` closes saving while swell.json is broken; `Game.record_swell` refuses then too.
  - Decided: a save shrine's rest keeps gauges and modes (the combat default). A defeat writes nothing.
  - Out of battle: `BattleSwellCarry.mode_rows/set_mode/rules` for the M2-UI-01 field menu.
  - Engine: `BattleSwell.attach()` keeps a carried mode only while it is unlocked (an unknown or locked mode plays as the default and is written back as the default; ADR 0018 Amendment 6 calls this acceptable).
  - Controller: two one-line hooks (`BattleSwellCarry.attach`, `BattleVitals.send_back(engine, swell)`).
  - Gate: `HYMN_SKIP_BLENDER=1 HYMN_SHOTS=battle_hud_preview,battle_swap_menu,battle_victory,battle_statuses,battle_swell_ring tools/ci_local.sh` rc 0 (Blender step run separately in the first pass: identical). 1116 Godot tests, 0 failed; coverage battle 99.94% (1763/1764), progression 96.52%; five battle shots rmse 0; tool tests 421 OK; validate_data 0/0.

## Review log
- 2026-10-23 qa, fresh reviewer (review-sweep-M): **approve.** No blockers. I tried to lose data along every path below and found no loss outside the one case ADR 0018 Amendment 6 accepts.
  - **Checks run** (worktree at 449f856, own `XDG_DATA_HOME`): Godot `--filter=swell` 93/0 failed, `--filter=save` 184/0 (including test_swell_save, test_save_system, test_bestiary_save and test_save_data_tables), and `--filter=vitals` 25/0. validate_data 0/0, tools unittest 431 OK, gdlint and gdformat clean. Coverage was not re-run: the author's gate shows battle 99.94% and progression 96.52%, and this branch has not changed since.
  - **Paths I tried, all safe:**
    - **Round trip.** to_dict/from_dict, `_clean_vitals` and SaveShape all accept an entry that holds only `swell` or only `swell_mode`.
    - **Shrine rest.** `full_heal` erases only hp, mp and statuses, so a swell-only entry survives.
    - **A hero at full HP and MP.** The entry now stays because of `swell`, so the "no entry = full" rule still holds.
    - **Reserve members.** Both directions include them.
    - **Defeat and Retry.** Nothing is written, and Retry re-reads the saved record.
    - **Unknown ids.** Unknown unlocked ids and unknown progress rule ids survive load_saved → to_saved (`_unknown_unlocked`, `progress` copied whole).
    - **v5 → v6.** The migration is frozen and keeps an existing `swell` key.
    - **Broken swell.json.** `has_swell` is false and attach leaves the carried mode alone. Gauges and modes are written back unchanged, `record_swell` refuses, and DataHealth closes saving.
    - **Fixtures and tests.** With `carry` off, nothing is read or written.
    - **Autosave.** No handler writes a save between `battle_party_returned` and `battle_swell_returned`, because autosave waits for a safe point.
  - **Accepted loss (ADR 0018 Amendment 6):** battle_swell.gd:111 resets a carried mode that is unknown or locked in this build to the default, and the next victory writes the default back (game_state_data.gd `record_vitals`). The saved choice is gone even if a later build restores the mode. The fix is cheap: keep the saved `swell_mode` when the combatant's mode was reset by attach. Optional.
  - **Should-fix:**
    1. tests/unit/test_swell_save.gd:276-320 covers victory and defeat but not **escape**. Criterion 1 names escape. send_back's branch covers it, but add an escape case that asserts the gauge and the record are written. That pins the criterion if send_back's outcome check is ever split.
    2. game/core/game.gd:161 vs :174. While swell.json is broken, `record_party` still writes gauges and modes but `record_swell` refuses the record. The result is harmless (saving is closed), but the two halves disagree. Either guard both or neither, and document which.
    3. The "Swell rides on vitals" design means a hero whose gauge is hidden by `SwellRingView.DRAWN_KINDS` (Asha, Toma, Ysolde until M2-UI-03) fills and saves a gauge the player cannot see. That is fine for M2 internals, but M2-UI-03 must land before the slice review, or a first visible gauge will appear already full. Add it to M2-UI-03's notes.
