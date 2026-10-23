---
id: M1-ARC-08
title: Save robustness: write-check before rename, deep shape check, deferred autosave, New Game slot policy
role: architect
status: doing
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
