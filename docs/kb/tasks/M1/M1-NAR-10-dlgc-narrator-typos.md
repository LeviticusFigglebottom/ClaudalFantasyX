---
id: M1-NAR-10
title: dlgc: catch Narrator misspellings and case-insensitive emotions
role: architect
status: doing
owner_session: "worktree-agent-abfc1d79a20572a9b"
depends_on: [M1-NAR-07]
milestone: M1
request-from: "narrative"
---
## Goal
Review-sweep-F findings on NAR-07.

## Acceptance criteria
- [ ] `Narator [grief] The bell.`, `Narrater [grief] ...` error with a hint; `Narator: ...` errors (not just warns) (dlgc.py ~:994)
- [ ] Emotion matching is case-insensitive for near-miss detection (`Kerid [Sad] Hi.`)
- [ ] `Kerid (sad): Hi.` errors
- [ ] Probe lines from scratchpad/freshF*.txt added to the tests

## Notes
See the review-sweep-F entries in the source tasks' Review logs for file:line.

## Review log
