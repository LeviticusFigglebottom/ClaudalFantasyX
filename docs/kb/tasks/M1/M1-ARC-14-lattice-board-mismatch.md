---
id: M1-ARC-14
title: Lattice: a save naming another board is frozen, not rewritten
role: architect
status: review
reviewer: qa
owner_session: "agent-a0094ffbbf8563d67"
depends_on: [M1-ARC-13]
milestone: M1
request-from: "qa"
---
## Goal
From the review-sweep-J entries (file:line references there).

## Acceptance criteria
- [x] A save whose Lattice board differs from the loaded one is frozen (no rewrite of the board field; positions kept) (lattice_progress.gd ~:305, ~:337-341)
- [x] battle_stage.gd ~:38 and debug_readouts.gd ~:212 load the board the save names, or refuse
- [x] The start node is not added to activated when a saved position is lost (~:362)
- [x] Tests

## Notes
- **Freeze on another board.** `from_dict` freezes when `d.board` is non-empty and differs from `lattice_board.id`. The freeze works as it does for a broken board: nobody is placed, `add_character` refuses, and `to_dict` returns the save unchanged.
- **Load the board the save names.** `LatticeProgress.board_for(saved, configured)` returns the save's board, or the configured board when the save names none. `BattleStage.lattice_for` and `DebugReadouts.lattice_target` use it.
- **Invalid ids.** A saved id that is not `[a-z0-9_]+` (`LatticeBoard.is_valid_id`) builds no path: `board_for` falls back to the configured board, which then freezes the save, and `DataHealth.lattice_problem` reports it. This also covers the sweep-J nit about the unsanitised res:// path.
- **Start on a lost position.** The start is no longer written to `activated`. `LatticeTraveler.implied_start` counts it as activated in play, and the first `move` adds it to `activated`.
- **Nit: `is_frozen`.** It is now the `_frozen_flag` bool, so an empty save on a broken board is frozen too.
- **Docs.** architecture.md "Data tables gate" has the new bullets and the audit row "`lattice.board` vs the configured board".
- **Tests.** 9 new in tests/unit/test_lattice_save.gd. Results: `--filter=lattice` 37/0 failed, `--filter=save` 155/0 failed, full Godot suite 966/0 failed, and progression coverage 96.52% (baseline 95.46%).
- **Not done.** The sweep-J nit about the boot-time profile for `report_data_tables` is not part of this task.

## Review log
