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
- [ ] Ch2 `haluna.tscn`, 11: the save shrine's 10 are Systems' scene `game/world/save_shrine/save_shrine.tscn`; the
      kit pieces are ready (M3-ENV-101), so request M3-ENV-747. Neme's stand-in has a model, so request M3-ENV-748.
- [ ] Ch3 `first_verse.tscn`, 15 CSG: env-art built the set, `assets/environments/zones/shell_shrine/first_verse_stage.tscn`
      (the final shrine, sea, shore, and the marks at their real places). slice-polish instances it (M3-ENV-745).
- [x] Ch3 `shell_shrine.tscn`, 1: the dark box behind the valve door is now the kit's `shrine_chamber_passage`
      (coursed walls, a corbelled roof, the dark beyond) in env-art's `shell_shrine_dressing.tscn`; S02/S03 pass.
- [x] Ch4 `derelict_deck_night.tscn`, 7 SphereMesh flames → the kit's `lamp_flame` (a teardrop on
      `kit_lamp_flame_hot`); also `ash_terrace_lanternfall` (Ch5). Lowlight's teal flames (Act II, paused) keep
      the bead until they get a piece of their own.
- [x] Ch4 `brightwater_ferry.tscn`, 4 kept greybox blocks: the ferry kit's `islet_landing`, `gangplank`, `stern_gate`
      and `terrace_name_board_wrapped` (bf_landing.py), previewed in `game/levels/_tests/brightwater_landing/`;
      env-art placed them in `tools/act1/ch04_ferry_dressing.py`, the keep list is empty (M3-ENV-749).
- [ ] Ch4 `haluna_wake.tscn`, 41: dressed (M3-ENV-743); act1-chapters mounts it (M3-ENV-744).
- [ ] Ch2 `banyan_placeholder` / `windbreak_placeholder` (medium, low): real trees under their old names. The same
      trees are built as `banyan_hero` / `windbreak_tree`; slice-polish switches the zone (M3-ENV-750), then env-art
      drops the old pieces.
- [ ] `tamsule_bell` drop proxy (low): `reefball_drop_proxy` is the contract shape for the Reefball water drop,
      which is PC GPU's R&D (pc-gpu.md). No Act I scene places it (`tools/act1/ch07_tamsule_bell_dressing.py` skips
      it), so nothing is on screen. The row clears when the real drop lands (Ch7, env-art-b's chapter, and pc-gpu).

## Notes
- 2026-10-28 (env-art): the derelict arena's flames self-rendered (battle_arena_derelict, _deck_night,
  _ash_terrace_lanternfall all pass, rmse ≤ 0.0074).

## Review log
