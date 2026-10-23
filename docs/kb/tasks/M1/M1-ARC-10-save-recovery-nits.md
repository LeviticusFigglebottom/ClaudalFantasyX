---
id: M1-ARC-10
title: Save: leftover .tmp recovery and debug downward set_chapter
role: architect
status: review
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
