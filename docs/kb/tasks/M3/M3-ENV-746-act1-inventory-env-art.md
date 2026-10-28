---
id: M3-ENV-746
title: "Act I inventory (M3-HER-1140): env-art's 15 rows"
role: environment
status: doing
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: qa
---
## Goal
ADR 0041: clear env-art's rows of `docs/kb/qa/act1_final_inventory.md` (integration-qa's
`tools/placeholder_audit.py`, M3-HER-1140), each by fixing the item or routing what isn't env-art's to its owner.

## Rows
- [ ] Prologue `prologue.tscn`, 37 primitives (City): `iskarra_city.tscn` is ready; slice-polish mounts it (M3-ENV-739).
- [ ] Ch1 `oruvel.tscn`, 26: dressed (M3-ENV-738); slice-polish mounts it (M3-ENV-740).
- [ ] Ch1 `oruvel_underway.tscn`, 36: dressed (M3-ENV-741); slice-polish mounts it (M3-ENV-742).
- [ ] Ch2 `haluna.tscn`, 11 (HalunaMood/SaveShrine 10, NPCs/Neme 1).
- [ ] Ch3 `first_verse.tscn`, 15 CSG: the stage on the final shrine (M3-ENV-745).
- [ ] Ch3 `shell_shrine.tscn`, 1 (Dressing/ChamberPassage BoxMesh).
- [x] Ch4 `derelict_deck_night.tscn`, 7 SphereMesh flames → the kit's `lamp_flame` (a teardrop on
      `kit_lamp_flame_hot`); also `ash_terrace_lanternfall` (Ch5). Lowlight's teal flames (Act II, paused) keep
      the bead until they get a piece of their own.
- [ ] Ch4 `brightwater_ferry.tscn`, 4 kept greybox blocks (SternGate, NameBoardWrapped, IsletRock, Gangplank).
- [ ] Ch4 `haluna_wake.tscn`, 41: dressed (M3-ENV-743); act1-chapters mounts it (M3-ENV-744).
- [ ] Ch2 `banyan_placeholder` / `windbreak_placeholder` (medium, low): real trees under their old names.
- [ ] `tamsule_bell` drop proxy (low): see Notes.

## Notes
- 2026-10-28 (env-art): the derelict arena's flames self-rendered (battle_arena_derelict, _deck_night,
  _ash_terrace_lanternfall all pass, rmse ≤ 0.0074).

## Review log
