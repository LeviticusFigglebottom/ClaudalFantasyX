---
id: M1-ARC-10
title: Save: leftover .tmp recovery and debug downward set_chapter
role: architect
status: doing
owner_session: "worktree-agent-a35fbca43cd81575b"
depends_on: [M1-ARC-08]
milestone: M1
request-from: "qa"
---
## Goal
Two open QA minors from M1-ARC-08's handoff (docs/kb/handoffs/2026-10-23-architect-9.md).

## Acceptance criteria
- [ ] A valid leftover .tmp (newer than the slot, passes SaveShape) is offered for recovery or logged; never silently discarded
- [ ] Debug set_chapter moving backwards does not autosave over a later chapter (or does so only with a debug flag)
- [ ] Tests

## Notes

## Review log
