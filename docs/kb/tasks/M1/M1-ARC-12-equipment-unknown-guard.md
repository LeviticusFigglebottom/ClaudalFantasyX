---
id: M1-ARC-12
title: Never drop equipment when the item tables are missing or fail to parse
role: architect
status: done
owner_session: "worktree-agent-a5a8cfa05f7795b89"
depends_on: [M1-ARC-11]
milestone: M1
request-from: "qa"
reviewer: qa
---
## Goal
From the review-sweep-H entries (file:line references there).

## Acceptance criteria
- [x] MUST: if item tables are empty or failed to parse, no loadout repair runs and no save is written over a slot (a guard plus a loud error); test with a broken equipment.json
- [x] Unknown item ids are kept in the bag as unknown pieces (round-tripped untouched) rather than dropped; only equipping them is refused
- [x] A confirmed manual save over a newer build's slot keeps a numbered copy (S2)
- [x] ADR 0018 amendment wording corrected (~:61 'at worst a hero's piece comes off')
- [x] Nits: the battle_engine petrify literal comment; `Narrator (asha)` with a space errors; the validate_data player-detection handles instanced players

## Notes
- 2026-10-23 architect (worktree-agent-a5a8cfa05f7795b89): ready for review (reviewer qa).
  - **MUST:** `ItemDB.load_dir` records missing or unparseable tables in `load_errors`. `integrity_problem()` also flags an equipment table with no equipment, gear types or equip slots. While `SaveSystem.item_tables_problem()` is non-empty, `_post_load` runs no repair and no starting gear (push_error), and `save_to_slot` returns `ERR_UNCONFIGURED` (push_error) before touching any file. Tests: test_save_item_tables.gd, covering a torn, a missing and a hollow equipment.json, a byte-identical slot 1 and slot 0, a refused autosave, and the whole bag back with the real tables.
  - **Unknown ids are kept:** `repair_loadout` deletes nothing. A worn unknown piece comes off. `equip_error` returns `unknown_equipment`, `pieces_for` hides the piece, and `unknown_uids()` lists it. A save and reload round-trip is untouched (test_save_item_tables, test_equipment, test_save_shape).
  - **S2:** a `STATUS_NEWER` slot is moved to `.newer`, `.newer.2`, … before a write (manual confirmed and New Game autosave).
  - **ADR 0018 Amendment 4** (append-only) corrects Amendment 3's Consequences.
  - **Nits:**
    - The engine uses `PETRIFY_ID := String(BattleCombatant.STATUS_PETRIFY)`, and the combatant comment is reworded.
    - dlgc: `Narrator (asha)` and `Narrator (asha) The bell.` now error with the no-space hint.
    - `scene_has_player` follows instanced sub-scenes (group "player"), inherited scenes, and a root script's `place_at`.
  - **Gate:** `HYMN_SHOTS=boot_title,save_shrine_field tools/ci_local.sh` passed every step (883 Godot tests, 0 failed; coverage within baseline; 2 shots compared, 0 failed).
  - **Not done (not in the ACs):** the `"rhenn": {}` empty loadout entry for an unknown hero is still saved.

## Review log
- 2026-10-23 qa (review-sweep-I, fresh reviewer): **approve-with-fixes.** No blocker in ARC-12's scope. I found one new data-loss path of the same class outside it (S1), which needs its own task.
  - **What I read:** the task, handoff architect-13, `git log -p` 1f64f1c..4b3647b (merge 8f09b96), ADR 0018 Amendment 4, and the save_system.gd, equipment_bag.gd, item_db.gd, inventory.gd, shop.gd, customize.gd and lattice_progress.gd paths that touch saved data.
  - **Checks:** Godot `--filter=save` 138 run, 0 failed (test_save_item_tables included). `--filter=equipment` 45 run, 0 failed. `validate_data` 0/0. Tool tests 359 OK (test_dlgc and test_locations_validate included).
  - **Probes. I tried to lose data and could not, inside ARC-12's scope:**
    - **Torn, missing or hollow equipment table:** `integrity_problem()` is non-empty, so `_post_load` returns before `repair_loadout` and `ensure_starting_gear`, and `save_to_slot` returns `ERR_UNCONFIGURED` before `_set_aside_leftover_temp`, the temp write or any rename (save_system.gd:159-167). Autosave and the New Game autosave go through the same gate.
    - **Every other writer of the slot file** checks out. `recover_temp` (:272) only renames a temp written by an earlier, healthy run. `delete_slot` is explicit. No load path rewrites a slot.
    - **Unknown pieces:** they are never deleted. `repair_loadout` only unequips them. `remove_piece` is reachable only through `sell_piece`, which refuses with `ERR_NOT_SELLABLE` because `sell_price_of(unknown)` is 0. Customize refuses through `_fit_error` (an unknown base has no slot kind). `next_uid` is persisted, so a new piece can never reuse an unknown piece's uid.
    - **Unknown consumables:** `Inventory.normalize()` would drop them, but nothing in game/ calls it, so the bag round-trips raw. A hollow items.json (it parses, with no rows) is not flagged by `integrity_problem`, but it loses nothing.
    - **.newer copies:** a STATUS_NEWER slot is renamed before the new file replaces it. If that rename succeeds and the next one fails, the slot reads empty, while the .newer copy and the checked temp both survive. The startup report offers to recover the temp. Nothing is lost.
  - **Should-fix:**
    - **S1 (data loss, same class, not in ARC-12's ACs). A broken Lattice board wipes Lattice progress.** `LatticeBoard.load_board` (lattice_board.gd:25-30) returns an empty board when `lattice_<id>.json` fails to parse. `LatticeProgress.from_dict` (lattice_progress.gd:278-293) then drops every traveller ("no start on board"), and battle_stage.gd:41 builds progress that way. The next victory writes `Game.state.lattice = progress.to_dict()` (battle_rewards.gd:29; the debug readout does the same at debug_readouts.gd:274), and the next save makes the loss permanent: every activated node and every position. That is exactly the S1 pattern, through a different table. Lead: please file **M1-ARC-13**. It needs a `load_errors` / integrity check on the board, no `from_dict` pruning or `state.lattice` write-back while the board is broken, and a save refusal, with a test using a torn `lattice_*.json`. Also audit the other "unknown ids are dropped" loaders for the same shape (`Inventory.normalize` if it is ever wired in).
    - **S2.** When saving is refused, the only player-facing signal is `SAVE_FAILED` at a shrine and `autosave_finished` reporting the error. A data build this broken should also say so once at boot (a debug overlay line, or a boot warning). Otherwise a player or tester can play a whole session that can never be saved.
    - **S3.** `.newer`, `.corrupt` and `.recovered` copies have no in-game listing. That is acceptable for M1. Note in ADR 0018 how a player restores a `.newer` copy after upgrading again (by hand-renaming it), or track a load-menu entry for M2.
  - **Nits:**
    - The `"rhenn": {}` empty loadout for an unknown hero is still saved (known, harmless).
    - The ADR 0018 Amendment 4 rationale "Customize cannot fit an ability to them (no slot)" is accurate only because `slot_of(unknown)` is empty. Say "no slot kind".
    - The dlgc `spaced_identity` hint and the `scene_has_player` instancing, inheritance and `place_at` handling are covered by their tests. Fine.
- 2026-10-23 lead: closing on review-sweep-I approve-with-fixes; the Lattice data loss of the same kind is in M1-ARC-13 (must-fix).
