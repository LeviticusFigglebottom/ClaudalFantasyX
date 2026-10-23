---
id: M2-FP-03
title: First-playable flow - prologue, New Game routing, battle hand-off and return, end card
role: architect
status: review
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M1-ARC-06, M1-CMB-08]
milestone: M2
request-from: lead
---
## Goal
New Game → Prologue (Rhen's narration over the dead city) → Haluna beach; a field battle request that opens the CTB battle and returns to the field spawn; an end card after the Ch3 first verse that returns to the title.

## Acceptance criteria
- [x] `locations.json` new_game goes to the prologue; the prologue hands off to `ch02/haluna` at Beach.
- [x] `BattleRequest` + a field battle scene (instancing, not editing, the battle sandbox) that returns to the requesting location and spawn on victory or escape.
- [x] End card scene with a loc-keyed message; accept returns to the title.
- [x] Integration tests for each hand-off.

## Notes
- 2026-10-23 (worktree agent): built. APIs and choices in [first_playable_flow.md](../../tech/first_playable_flow.md).
  - `BattleRequest` (static start/make/submit/pending/take/clear) + `FieldBattle` (inherited `battle_sandbox.tscn`, live). Victory and escape show Return only; defeat keeps Fight again + Return (back to the field, flag unset, pre-fight vitals).
  - `ch02_tideline` (reef_crab + lantern_eel, escapable). BattleSim 500 seeds, rhen+asha / toma: 100% wins for every policy, ~10 turns, naive loses a member ~1 fight in 5.
  - Prologue scene (`game/levels/prologue/`), script `prologue_dead_city.dlg` (the SPEC §3.5 line only), `prologue` first in locations.json and `new_game` points at it. Hand-off to `ch02/haluna` / `Beach` from `game/data/flow/first_playable.json`; until that row is playable, `go_to` falls back to the default (warned).
  - End card (`game/flow/end_card.tscn`), loc keys `FLOW_END_CARD_*`.
  - Fixed `tools/validate_data.py` `scene_has_player`: a root `script = ExtResource(..)` property line (Godot's real format) now counts for place_at (was header-attribute only); test `tools/tests/test_fp_scene_place_at.py`.
  - Tests: `test_fp_field_battle.gd`, `test_fp_prologue.gd` (integration), `test_fp_end_card.gd` (unit).
  - Not done: screenshots of the prologue framing (skipped by instruction); the field trigger that calls `BattleRequest.start` belongs to the playable Haluna zone.

## Notes (handoff)
- Ready for review by **qa**. `tools/validate_data.py` (Systems-owned, shared) got a small fix so a root script defining `place_at` counts as a player (own commit + test); Systems please confirm.

## Review log
