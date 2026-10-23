---
id: M1-ARC-08
title: Save robustness: write-check before rename, deep shape check, deferred autosave, New Game slot policy
role: architect
status: review
owner_session: "worktree-agent-a8ea331609fe60dd4"
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
