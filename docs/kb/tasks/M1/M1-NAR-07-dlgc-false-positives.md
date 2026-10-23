---
id: M1-NAR-07
title: dlgc near-miss heuristic: kill false positives, catch the remaining silent cases
role: architect
status: doing
owner_session: "agent-a82894145cf6d2aff"
depends_on: [M1-NAR-06]
milestone: M1
request-from: "narrative"
---
## Goal
7 of 10 realistic narration lines were rejected; two real near-misses still slip through.

## Acceptance criteria
- [ ] Colons between digits (6:20, 3:1) never trigger
- [ ] Error only for 1-2-word prefixes before ':'; warn for longer
- [ ] `Asha [sad] Hi there.` (missing colon) errors with a hint
- [ ] `Asha: [sad] Hi.` errors (emotion after the colon)
- [ ] Test corpus of 30+ realistic narration lines with zero false positives

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

## Review log
