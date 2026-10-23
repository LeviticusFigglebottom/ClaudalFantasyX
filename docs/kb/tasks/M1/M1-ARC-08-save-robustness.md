---
id: M1-ARC-08
title: Save robustness: write-check before rename, deep shape check, deferred autosave, New Game slot policy
role: architect
status: todo
owner_session: ""
depends_on: [M1-ARC-03, M1-ARC-06]
milestone: M1
request-from: "qa"
---
## Goal
Review-sweep-C (QA) findings on ARC-03; schedule after save v4 lands.

## Acceptance criteria
- [ ] Check the write result (and flush/close) before the rename; a failed write never replaces a good save; test with a simulated failure
- [ ] Deep schema check on load (types of party ids, inventory and nested state); malformed reads as corrupt
- [ ] Autosave deferred out of set_chapter (call_deferred, or after the cutscene ends)
- [ ] New Game never silently overwrites the previous run's autosave: separate autosave per run or a confirm

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

## Review log
