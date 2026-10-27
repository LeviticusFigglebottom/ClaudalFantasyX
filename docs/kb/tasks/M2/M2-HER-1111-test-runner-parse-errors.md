---
id: M2-HER-1111
title: "Test runner: a test file with a parse error passes silently (request to QA & Tools)"
role: qa
status: review
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
- [x] In `_ready`, `if script == null:` becomes `if script == null or not script.can_instantiate():`, so a parse error
      counts as one failure ("failed to load (parse error?)").
- [x] Run the full suite once after the change, to catch any test file that has been silently broken.

## Notes
- tests/run_tests.* is QA & Tools' (ownership.md row 12), so the hero track doesn't edit it.

## Notes (2026-10-27, integration-qa)
- Done in b7f7bcff (claude/hero-integration): `tests/run_tests.gd` counts a script that can't instantiate (a parse
  error) as one failure, and fails a test that returns while suspended on an await
  (`TestCase.runs_to_the_end`, `TestCase.SUSPENDED`; test_qa_threads uses it too). The await rule is in
  tests/test_case.gd's header.
- Probed with throwaway files: a parse error fails ("failed to load (parse error?)"); an await on process_frame fails
  as suspended; an await on a synchronous coroutine passes.
- Full suite, the same tree with and without the change: 2836 run. The change adds exactly one failure,
  **test_slice_shots** (suspended on an await). slice-polish has already fixed it on claude/m2-slice (M2-QA-100's
  own note), so it goes green when m2-slice merges. The other 31 failures are there without the change too (being
  attributed: the live log's integration-qa section).

## Review log
