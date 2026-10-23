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
