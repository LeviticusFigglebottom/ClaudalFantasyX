---
id: M2-QA-100
title: "Test runner: a test that awaits a frame passes without running its assertions (request to QA & Tools)"
role: qa
status: review
owner_session: "integration-qa (hero-integration track, session_01PzF7Jc4XVQdTWcaYUyCjPB)"
depends_on: []
milestone: M2
request-from: cinematics
---
## Goal
`tests/run_tests.gd` runs every test inside its own `_ready` and calls each method with `tc.call(mname)`, without
awaiting. The tree never steps a frame during the run. So a test that awaits `process_frame`, `physics_frame`, a
timer or any signal that isn't emitted synchronously suspends there forever. Every assertion after the await never
runs, and the test reports PASS.

This was found 2026-10-27 (slice-polish) in two tests, both fixed in claude/m2-slice:
- `test_slice_shots` only checked the first shot's setup, never staged a level, and hid a real bug (below);
- `test_causeway_route`'s spawn-floor test never cast a ray.

Awaits that resume synchronously are fine: an instant CutsceneSequencer's `play`, or a signal emitted inside the
call. Slice-polish probed these in test_haluna_villagers and test_cutscene_pose with a failing assert after the
await, and they do run.

A related trap: `tree.root.add_child(x)` during the run fails, because the root is busy setting up the runner. Use
`tree.current_scene`, as most tests do. `test_slice_shots` added to the root, which is why its levels never staged
once the await stopped hiding it.

## Acceptance criteria
- [x] The runner fails a test that suspends. One way: `TestCase` gets a `finished` flag that `begin_test` clears
  and a wrapper sets at the end of the method, and the runner fails any test that returns with it unset ("test
  suspended on an await: the runner never steps a frame"). Another: run each test as `await tc.call(mname)` from
  a deferred driver that does step frames. That costs runtime but lets tests await frames for real.
- [x] Run the full suite once after the change, and file each newly failing test with its owner.
- [x] Note the rule in tests/README (or test_case.gd's header).

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
