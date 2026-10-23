---
id: M1-ARC-13
title: Never drop Lattice progress when the lattice tables are missing or broken
role: architect
status: review
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
