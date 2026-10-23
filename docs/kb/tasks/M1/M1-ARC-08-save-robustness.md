---
id: M1-ARC-08
title: Save robustness: write-check before rename, deep shape check, deferred autosave, New Game slot policy
role: architect
status: review
owner_session: "worktree-agent-a35fbca43cd81575b"
reviewer: qa
depends_on: [M1-ARC-03, M1-ARC-06]
milestone: M1
request-from: "qa"
---
## Goal
Review-sweep-C (QA) findings on ARC-03; schedule after save v4 lands.

## Acceptance criteria
- [x] Check the write result (and flush/close) before the rename; a failed write never replaces a good save; test with a simulated failure
- [x] Deep schema check on load (types of party ids, inventory and nested state); malformed reads as corrupt
- [x] Autosave deferred out of set_chapter (call_deferred, or after the cutscene ends)
- [x] New Game never silently overwrites the previous run's autosave: separate autosave per run or a confirm

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

### Implementation (architect, 2026-10-23)
- **Write check** (`game/core/save_system.gd` `_write_checked`): store result → flush → `get_error()` → close → read back and compare, all before the rename. On failure the tmp is removed, the error is returned (`ERR_FILE_CANT_WRITE` if Godot reported none), and there is no `game_saved`. The injectable writer is `SaveSystem.store_text`. Tests: `tests/unit/test_save_write_check.gd` (a reported failure, a silent short write, a first write, autosave).
- **Deep shape** (`game/core/save_shape.gd`, new `SaveShape`): element-level checks for every state key. Whole-number versions only, which covers the 2.7 nit. A single reader, `_read_save`, now backs `load_from_slot`, `deserialize` and `slot_info`. Tests: `tests/unit/test_save_shape.gd`, including the review probe slot.
- **Deferred autosave**: `set_chapter` → `request_autosave`. It is written on a later frame at a safe point (no `hold_autosave` holder, router idle, tree unpaused). `FieldCameraDirector` holds it while a scripted shot is held. `Game.new_game()` (new `EventBus.new_game_started`) and `load_into_game` drop a pending request. Tests: `tests/unit/test_autosave_deferred.gd`, plus an updated `test_autosave.gd`.
- **New Game policy**: a confirm prompt, chosen over an autosave per run (ADR 0018, proposed). It asks only when slot 0 is readable or from a newer build. "Go back" is the default, and `ui_cancel` also goes back. Loc keys `TITLE_CONFIRM_*` were appended to `strings.csv`. Tests: `tests/unit/test_title_menu.gd` and `tests/integration/test_save_new_run.gd`.
- Docs: architecture.md, "Save robustness (M1-ARC-08)"; field_camera.md, the autosave-during-cutscene bullet.
- Not done (QA nits outside the acceptance criteria): offering recovery from a valid stale `.tmp`, and the downward `set_chapter` autosave.

- 2026-10-23 architect (worktree-agent-a35fbca43cd81575b, sweep-E fixes):
  - **S1:** `SaveShape.is_whole` bounds the magnitude at `MAX_WHOLE` (2^53) for floats and ints, so `int()` is exact. `test_huge_whole_numbers_are_rejected` covers the probe cases (currency 1e300, chapter 1e19, inventory 1e20, vitals hp 1e300, lattice points, next_uid) and a slot on disk (corrupt in the menu, null on load).
  - **S2:** `_owned` requires canonical keys (`str(int(k)) == k`, so `"05"`, `"+1"` and overflowing keys fail). `_equipment` requires `next_uid` present and greater than the highest owned uid, and every loadout uid to be 0 (empty) or owned. Test: `test_equipment_uids_must_be_consistent`.
  - **S3:** fixed with M1-ARC-07 S2 (the hold follows the shot across a reparent).
  - **S4:** keep the further-along autosave, as Amendment 1 to ADR 0018. The deferred chapter autosave is skipped (`ERR_ALREADY_EXISTS` on `autosave_finished`, plus a warning) when slot 0 has a later chapter, the same chapter with more play time, or a newer build. The exception is a run that New Game started, until its first autosave. Tests are in `tests/unit/test_save_recovery.gd` (older record, same chapter, overtaking, New Game exception, load ends it, empty/damaged/newer slot 0).
  - **Nits:** architecture.md §Save robustness documents that `flush()` is not an fsync. A failed rename now warns and **keeps** the checked temp file for recovery (M1-ARC-10) instead of deleting it (`test_a_failed_rename_keeps_the_new_save_for_recovery`). The `party_ids` semantic nit is left open and noted in architecture.md.
  - Godot `--filter=save`: 114 run, 0 failed.

## Review log
- 2026-10-23 qa (review-sweep-E): **approve-with-fixes.** I read save_system.gd, save_shape.gd, the title model and menu diffs (4789d72), ADR 0018 and the architect-9 handoff. I ran `godot --headless res://tests/run_tests.tscn -- --filter=save` (own `XDG_DATA_HOME`): 100 run, 0 failed. I also probed `SaveShape.problem` directly with 11 malformed states (scratchpad `sweepE_godot/save_probe.gd`). gdlint and gdformat are clean.
  - **The write check holds.** The order is store → flush → `get_error()` → close → read-back compare, before the rename (save_system.gd:121-134). The tmp file is removed on every failure path, and the old slot is untouched. The tests cover a reported failure, a silent short write and a first write.
  - **One reader works.** `load_from_slot`, `deserialize` and `slot_info` agree, and the version check rejects bools, fractions and newer builds.
  - **Deferred autosave:** the hold, the paused tree, the busy router and the drops on New Game and on load all behave as ADR 0018 says.
  - **The New Game confirm works.** "Go back" is the default; `ui_cancel`, the click path and `choose()` all route through `needs_new_game_confirm`, and an empty or corrupt slot 0 skips the question.
  - **Should-fix S1: whole numbers have no magnitude bound.** `SaveShape.is_whole` (save_shape.gd:62) accepts any finite integral float. `currency: 1e300`, `chapter: 1e19`, `inventory.potion: 1e20` and `party_vitals.rhen.hp: 1e300` all pass. In Godot 4.6.3, `int()` of each is -9223372036854775808, so a save that passes the check loads with negative currency, chapter or counts. Bound counts at ≤ 2^53 (or the data caps) and add the probe cases to test_save_shape.gd.
  - **Should-fix S2: equipment uid integrity.**
    - `next_uid` is never checked against `owned` (save_shape.gd:199-201). `{"next_uid": 1, "owned": {"1": {...}}}` passes, and the next `EquipmentBag.add_piece` (equipment_bag.gd:46-48) silently overwrites piece 1. Any loadout pointing at uid 1 then holds the new piece.
    - Non-canonical keys `"05"` and `"+1"` pass `_owned` (save_shape.gd:181), but `str(uid)` lookups never reach them.
    - A loadout uid that isn't in `owned` also passes.

    Require `str(int(k)) == k`, `next_uid > max(owned uid)`, and loadout uids that exist in `owned`.
  - **Should-fix S3 (shared with M1-ARC-07 S2):** `FieldCameraDirector._exit_tree` releases the hold (field_camera_director.gd:250) but keeps `_scripted_shot`. A director re-parented mid-cutscene is unheld, so the chapter autosave can snapshot mid-shot.
  - **Should-fix S4 (ADR 0018 scope):** loading an *older* record, then crossing its next chapter boundary, overwrites a further-along autosave with no prompt. That loses a run in the same way the New Game case did. At least name it in ADR 0018's Consequences, or ask on load when slot 0 is newer than the record being loaded. It could join M1-ARC-10.
  - **Nit:** `FileAccess.flush()` is a stdio flush, not an fsync. On some filesystems a power cut right after the rename can still leave an empty slot. Document the limit in architecture.md §Save robustness.
  - **Nit:** the rename-failure branch (save_system.gd:111-114) returns without the `push_warning` that the write-failure branch gives.
  - **Nit:** duplicate or unknown `party_ids` pass (`["rhen","rhen","rhen","rhen"]`, `["nobody"]`). That's shape-only, as the AC says, but it's worth a semantic check alongside M1-ARC-10.
- 2026-10-23 qa (review-sweep-F, fresh reviewer): **approve-with-fixes.** I read 3829320 and the current save_system.gd and save_shape.gd in full, ADR 0018 and Amendment 1, and test_save_recovery.gd. Checks: validate_data 0/0; `unittest discover -s tools/tests` 300 OK; taskboard --check rc 0; `dlgc --check` 0/0; gdlint and gdformat clean. Godot (own `XDG_DATA_HOME`): `--filter=save` 114 run, 0 failed. I also ran a probe test (not committed) with malformed v2 and v4 saves.
  - **Sweep-E S1 is fixed.** `is_whole` bounds ints and floats at `MAX_WHOLE` = 2^53 (save_shape.gd:75-81), so `int()` is exact everywhere `_count` and `_uid` are used. The test covers the probe values and a slot on disk.
  - **Sweep-E S2 is fixed.** `_owned` requires canonical keys (`str(int(k)) == k`, at :200). `_equipment` requires `next_uid` greater than the highest owned uid, and every loadout uid to be 0 or owned (:213-231).
  - **Sweep-E S3 is fixed** in the director: the hold follows the shot (see M1-ARC-07 sweep F for a new edge).
  - **Sweep-E S4 is fixed.** In `poll_pending_autosave` (save_system.gd:442-457), `autosave_is_further_along` skips the write with `ERR_ALREADY_EXISTS` and a warning. New Game's `_new_run` exception lasts until the first successful autosave, and `load_into_game` ends it. The tests cover older, same chapter, overtaking, New Game, load, and empty, damaged and newer slot 0.
  - **Nits fixed:** the fsync limit is documented, the rename failure warns and keeps the temp file, and `party_ids` semantics are noted.
  - **Should-fix F1: the v2→v3 migration runs before the shape check and can crash or silently coerce.** `_migrate_v2_to_v3` calls `int(old[k])` on every raw inventory value (save_system.gd:368-371), and `SaveShape` only sees the migrated result (:277-278).
    - In the probe, a v2 save with `inventory: {"potion": {"x": 1}}` raised `SCRIPT ERROR: Nonexistent 'int' constructor` at save_system.gd:369, and `deserialize` still returned a GameStateData, not null.
    - `{"potion": 1e20, "ether": "7"}` loaded as `{"ether": 7}`. The huge count wrapped negative and was dropped, and a string was coerced, with no "corrupt".
    - That breaks this task's AC2 ("malformed reads as corrupt, never a crash") for every v2 save on disk.
    - Fix: in the migration, skip (or mark as bad) any value that isn't `SaveShape.is_whole` and ≥ 0, and add the three probe cases to test_save_shape.gd or test_save_v4.gd.
  - Nit: as noted in PRG-03 sweep F, `_equipment` still allows one uid in two loadouts (two wearers) and a piece worn by the wrong character or in the wrong slot. That is the same class as S2. `wearer_of` returns the first wearer only, so `remove_piece` and the shop logic see one wearer while two heroes fight with it.
  - Nit (ADR 0018 Amendment 1, Consequences): "Continue still offers slot 0, the further-along run" is not quite true. `TitleSaveEntry.continue_slot` picks the newest `saved_at`, so once the player shrine-saves the replayed older branch, Continue offers that manual slot. The behaviour is reasonable, but the ADR sentence should match it. Also file the toast as a UI task, so the skipped autosave isn't silent to the player (pillar 4).
