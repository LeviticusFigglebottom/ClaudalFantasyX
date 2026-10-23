---
id: M0-LEAD-01
title: M0 bootstrap: repo, KB, CI, ADRs, task board
role: lead
status: done
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
- [x] CI gates green (locally via tools/ci_local.sh, ADR 0008; Actions has no runner yet)

## Notes
Reviewer: a fresh agent (milestone gate, SPEC §12.3). The Godot steps could not run in the bootstrap container (no engine download), so the first CI run is the real check.

## Review log
- 2026-10-22 lead: GitHub Actions runs never left `queued`. Verified instead with tools/ci_local.sh on Godot 4.6.3 (ADR 0008): 42/42 tests pass, import is clean, the boot smoke test passes, and the harness canary showed crashes and bad asserts both FAIL. Awaiting a fresh-agent review.
- 2026-10-23 lead: the fresh-agent review (approve-with-fixes) is in M1-CMB-00's log; all fixes landed (claim protocol, shared-file rule, taskboard checks, CI timeouts and boot smoke test). Closing.
