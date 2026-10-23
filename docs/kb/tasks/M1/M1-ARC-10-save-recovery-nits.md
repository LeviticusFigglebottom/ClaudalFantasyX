---
id: M1-ARC-10
title: Save: leftover .tmp recovery and debug downward set_chapter
role: architect
status: done
owner_session: "worktree-agent-a35fbca43cd81575b"
depends_on: [M1-ARC-08]
reviewer: qa
milestone: M1
request-from: "qa"
---
## Goal
Two open QA minors from M1-ARC-08's handoff (docs/kb/handoffs/2026-10-23-architect-9.md).

## Acceptance criteria
- [x] A valid leftover .tmp (newer than the slot, passes SaveShape) is offered for recovery or logged; never silently discarded
- [x] Debug set_chapter moving backwards does not autosave over a later chapter (or does so only with a debug flag)
- [x] Tests

## Notes

- 2026-10-23 architect (worktree-agent-a35fbca43cd81575b):
  - **Leftover .tmp:** a temp file is *recoverable* when it is readable and newer than its slot (meta `saved_at`), or when the slot is missing or damaged. `SaveSystem.report_leftover_temps()` runs deferred from `_ready` and warns for each one. `leftover_temp_info(slot)` describes it (for a future menu prompt), and `recover_temp(slot)` renames it over the slot. The next `save_to_slot` moves a recoverable temp to `slot_NN.json.recovered` (with a warning) before it reuses the name. A torn temp is overwritten. A failed rename keeps the temp.
  - **Downward set_chapter:** it requests no autosave and warns, unless `SaveSystem.autosave_on_chapter_regress` (debug) is set. The further-along rule (ADR 0018 Amendment 1) also protects slot 0.
  - Tests: `tests/unit/test_save_recovery.gd`.

## Review log
- 2026-10-23 qa (review-sweep-F, fresh reviewer): **approve-with-fixes.** I read 3829320 (`leftover_temp_info`, `recover_temp`, `report_leftover_temps`, `_set_aside_leftover_temp`, `_on_chapter_changed`) and tests/unit/test_save_recovery.gd. Godot: `--filter=save` 114 run, 0 failed. I also ran a probe test (not committed).
  - **AC1 is met for the normal case.** A readable temp that is newer than its slot, or whose slot is missing or damaged, is warned about at startup (deferred from `_ready`), described by `leftover_temp_info`, and restorable with `recover_temp`. It is moved to `.recovered` before the next write reuses the name, and a failed rename keeps it.
  - **AC2 is met.** A downward `set_chapter` warns and requests nothing unless `autosave_on_chapter_regress` is set (save_system.gd:408-417). The further-along rule is a second guard.
  - **AC3 is met.**
  - **Should-fix F1: a temp file "recovers" over a newer build's save.** `leftover_temp_info` treats any slot status other than OK as older (save_system.gd:190), and that includes `STATUS_NEWER`. Probe: slot 5 holds `{"version": 99}`, and slot 5's `.tmp` is a valid v4 save with `saved_at: 1`. The result was `recoverable: true`, and `recover_temp(5)` returned OK and replaced the v99 save with the v4 one. `report_leftover_temps` would advise the same. After a downgrade, that loses the newer build's save. Fix: treat `STATUS_NEWER` as "not older" (not recoverable, or log only), and add the case to test_save_recovery.gd.
  - Nit: `_set_aside_leftover_temp` renames over an existing `slot_NN.json.recovered` (save_system.gd:234-236), so a second set-aside silently replaces the first. Use a numbered or timestamped name, or skip when one exists.
  - Nit: "newer" is a strict `>` on whole-second `saved_at` (:190). A temp written in the same second as the slot's save (two quick saves, then a failed rename) is not recoverable, and the next write overwrites it without a word. That is rare. Use `>=`, or compare `play_time_sec` as a tiebreak.
- 2026-10-23 lead: closing on review-sweep-F approve-with-fixes; the data-loss case (tmp vs a newer-build slot) is in M1-ARC-11 as a must-fix.
