---
id: M2-HER-1111
title: "Test runner: a test file with a parse error passes silently (request to QA & Tools)"
role: qa
status: doing
owner_session: "integration-qa (hero-integration track, session_01PzF7Jc4XVQdTWcaYUyCjPB)"
depends_on: []
milestone: M2
request-from: combat
---
## Goal
`tests/run_tests.gd` only counts a load failure when `load()` returns null. A test script with a GDScript parse error
loads as a non-null GDScript with no methods, so the runner prints "Tests: N run, 0 failed" and the file's tests
silently vanish (seen 2026-10-25 when a new class wasn't imported yet: 5 run, 0 failed, the new file's tests missing).

## Acceptance criteria
- [ ] In `_ready`, `if script == null:` becomes `if script == null or not script.can_instantiate():`, so a parse error
      counts as one failure ("failed to load (parse error?)").
- [ ] Run the full suite once after the change, to catch any test file that has been silently broken.

## Notes
- tests/run_tests.* is QA & Tools' (ownership.md row 12), so the hero track doesn't edit it.

## Review log
