---
id: M1-ARC-13
title: Never drop Lattice progress when the lattice tables are missing or broken
role: architect
status: done
owner_session: "worktree-agent-a26ce419921db7765"
depends_on: [M1-ARC-12]
milestone: M1
request-from: "qa"
reviewer: qa
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [x] MUST: a broken or missing lattice_*.json never drops Lattice progress; no save is written while it is broken (mirror the ARC-12 ItemDB guard) (lattice_progress.gd ~:278-293, battle_rewards.gd ~:29)
- [x] Unknown node ids are kept and round-trip untouched
- [x] Tests with a torn, a missing and an empty lattice table
- [x] Audit every other game/data table that save state references (party ids, inventory items, flags, locations) for the same failure mode and guard each; list them in architecture.md

## Notes
- 2026-10-23 architect (worktree-agent-a26ce419921db7765): ready for review (reviewer qa).
  - **One gate.** `DataHealth` (game/core/data_health.gd) has one named check per table: `items`, `lattice`, `battle`, `locations`, `flags` and `party_rest`. `SaveSystem.data_tables_problem(state)` replaces `item_tables_problem()` at ARC-12's two guard points. While it is non-empty, `_post_load` runs nothing and `save_to_slot` returns `ERR_UNCONFIGURED` before it touches a file. `report_data_tables()` logs it once at startup, which covers sweep-I S2 at log level.
  - **MUST.**
    - `LatticeBoard.load_board_from` and `LatticeRules.load_file` record a `load_error`. Their `integrity_problem()` also flags a hollow board (no nodes or no starts) and hollow rules (no Facets, or `move_cost <= 0`).
    - While either is broken, `LatticeProgress.from_dict` freezes the saved dict. `to_dict` returns it unchanged, `add_character` refuses, and `save_into(state)` refuses. That is the only write-back: battle_rewards.gd and the F6 cheat in debug_readouts.gd both go through it.
  - **Unknown ids are kept** on a sound board:
    - unknown activated node ids (they grant nothing);
    - a lost position (`LatticeTraveler.saved_position` is written back until the traveler moves);
    - a character with no start (`kept_characters`);
    - a gate the board lacks (`kept_gates`, kept in saved order).
    - test_lattice_save.gd was updated for this intended change.
  - **Audit** (table in architecture.md, "Data tables gate"):
    - Real loss paths found: the Lattice (the MUST), and party_rest.json. With party_rest.json broken, `record_party` would erase every carried status. It now writes nothing while that table is broken.
    - `Inventory.normalize` (unused) now refuses on broken item tables. `ItemDB.items_problem()` flags a hollow items.json.
    - Party ids, locations and flags had no pruning writer, but they are behind the gate anyway.
  - **Tests:** tests/unit/test_save_data_tables.gd (9 tests). Every guarded table is tried torn, missing and empty. For each: the gate names it, the save loads exactly as written, manual, empty-slot and auto saves are refused, slots 1 and 0 stay byte-identical, and it saves again once mended. They also cover the Lattice freeze and the refused write-back, unknown Lattice ids through a save, load and write-back, and `normalize` and `record_party` on broken tables.
  - **ADR 0018 Amendment 5** (append-only).
  - **Gate:** `HYMN_BLENDER_BASE=b7e0463 HYMN_SHOTS=boot_title,save_shrine_field,battle_victory tools/ci_local.sh` passed every step.
    - Results: 940 Godot tests, 0 failed. Coverage: battle 99.93%, progression 96.46%, both at or above baseline (the progression baseline was not ratcheted). 3 shots compared, 0 failed.
    - Without `HYMN_BLENDER_BASE` the worktree has no base ref, so every Blender job runs. One of them, `vegetation` (palm_coconut_b.glb TANGENT), fails. No asset source changes on this branch.

## Review log
- 2026-10-23 qa (review-sweep-J, fresh reviewer): **approve with should-fixes.** No blockers. The MUST holds on every path I could reach in the shipped build.
  - **What I read:** the task, handoff architect-14, `git diff 59738a0^1 59738a0` (all of game/, the tests, architecture.md "Data tables gate", ADR 0018 Amendment 5), and every writer of `Game.state.lattice` (only `LatticeProgress.save_into`, from battle_rewards.gd:30 and debug_readouts.gd:274).
  - **Checks:** `validate_data` 0/0, tool tests 382 OK, taskboard `--check` OK, gdlint clean. Godot, with my own XDG_DATA_HOME: `--filter=save_data_tables` 9/0 failed, `--filter=lattice` 29/0 failed, no script errors in either log.
  - **Tried to lose data:**
    - Broken board or rules, then a victory or F6: `save_into` refuses and `save_to_slot` returns ERR_UNCONFIGURED before it touches a file. The tests prove both slots stay byte-identical. **Holds.**
    - Unknown node, position, character or gate on a sound board: kept, and written back. **Holds**, with S2 below.
    - Loading while broken: `_post_load` skips repair and `ensure_starting_gear`, so the save loads exactly as written. Migration runs in memory only, and the write is refused. **Holds.**
    - party_rest broken: `record_party` writes nothing (game.gd:152-155). **Holds.**
    - **A sound board with a different id does lose data** (probe, not committed). I saved `{"board": "elsewhere", rhen at "far_node"}` and ran `from_dict` on the fixture board. The result is not frozen, `to_dict` rewrites `"board"` to `fixture`, and Rhen's saved position survives only until his first move. That is S1.
  - **Should-fix:**
    - **S1 (cross-board loss, latent).** `LatticeProgress.from_dict` never compares `d.board` with `lattice_board.id` (lattice_progress.gd:337-341), and `to_dict` always writes `board.id` (:305). Meanwhile the gate judges the board the *save* names (data_health.gd:100-103), but the writers load the board the *config* names (battle_stage.gd:38, debug_readouts.gd:212). Today only `standard` ships, and both configs say `standard`, so nothing breaks yet. The first second board (or a config typo) will silently re-home every traveler, though. Freeze, or keep the whole dict, when the ids differ, and add a test.
    - **S2 ("round-trips untouched" is not quite true).** For a lost position, `from_dict` adds the start node to `activated` (lattice_progress.gd:362). The written-back save then holds an id it did not have before (probe: `["far_node", "x2", "rhen_start"]`). It is harmless, since a start is free and `add_character` does the same. Either don't add it when `saved_position` is set, or say in architecture.md that the start is added.
  - **Nits:**
    - `is_frozen()` keys on a non-empty `_frozen` (lattice_progress.gd:331-332). A broken board with an empty saved dict is therefore "not frozen", and `add_character` is attempted. Nothing is lost, because `save_into` still refuses. A `_frozen_flag` bool would say what it means.
    - The board id is taken from the save unsanitised into a res:// path (data_health.gd:102 → lattice_board.gd:24). It is read-only, but a hand-edited save can point the gate at any `lattice_*.json`. Reject ids that are not `[a-z0-9_]+`.
    - `report_data_tables.call_deferred()` (save_system.gd:146) now loads BattleDB, the board, facets and locations at boot. That is fine, but it belongs in the boot-time profile.
    - The audit table in architecture.md is accurate, as far as I can verify. It would help to add the row "Lattice `board` field vs the configured board" once S1 lands.
- 2026-10-23 lead: closing on review-sweep-J approve; the board-mismatch issue (not reachable yet) is in M1-ARC-14.
