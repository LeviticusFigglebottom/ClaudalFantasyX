---
id: M0-LEAD-01
title: M0 bootstrap: repo, KB, CI, ADRs, task board
role: lead
status: review
owner_session: "lead-bootstrap"
depends_on: []
milestone: M0
request-from: ""
---
## Goal
Complete SPEC §15 steps 1–6, and start the parallel streams of step 7.

## Acceptance criteria
- [ ] Repo layout per SPEC §5.1; project.godot pinned to 4.6.3, Forward+
- [ ] CLAUDE.md, KB skeleton, glossary, banned-term list
- [ ] CI: import, tests, validators, screenshot stub, export on main
- [ ] ADRs 0001–0005 (+0006 test framework, 0007 data format)
- [ ] M1 broken into tasks
- [ ] CI green on the first push (verify in Actions)

## Notes
Reviewer: a fresh agent (milestone gate, SPEC §12.3). The Godot steps could not run in the bootstrap container (no engine download), so the first CI run is the real check.

## Review log
