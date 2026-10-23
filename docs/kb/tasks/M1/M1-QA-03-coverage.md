---
id: M1-QA-03
title: Coverage strategy for battle/ and progression/
role: qa
status: review
owner_session: qa-stream-2
reviewer: combat
depends_on: []
milestone: M1
request-from: ""
---
## Goal
ADR 0006 follow-up.

## Acceptance criteria
- [x] Adopt gdUnit4 coverage or a proxy: a source-instrumentation line-coverage proxy (ADR 0013), since gdUnit4 can't be downloaded and was set aside by ADR 0006
- [x] CI fails on coverage drop: `tools/coverage/run_coverage.py` exits 1 when a directory drops below `tools/coverage/baseline.json` by more than 0.5 pp, or when a new or baselined file is at 0%. It runs in `tools/ci_local.sh` and in the CI `godot` job.

## Notes
- Delivered 2026-10-22 by qa-stream-2. Docs: `docs/kb/qa/coverage.md`. Decision: `docs/kb/decisions/0013-coverage.md`.
- Initial baseline: `game/battle/` **91.70%** (464/506 lines, excluding `scene/`), `game/progression/` **93.06%** (335/360). 223 tests. 20–30 s per run.
- Instrumented runs are checked against the plain run: every test result and the test count must match (`--compare-log`). `tools/tests/test_coverage_instrument.py` covers the tricky syntax, and runs a fixture plain and instrumented under Godot to check the output is identical.
- To-do for Combat and Progression: the five least-covered functions are listed in `docs/kb/qa/coverage.md` (`ctb_timeline.eligible`, `lattice_rules.facet_name_key`, `lattice_progress._add_stat`, `ctb_timeline._sim_add_status`, `lattice_rules.load_file`).
- Follow-ups for the Lead: add a row to the table in `docs/kb/qa/README.md`. ADR 0006's "Consequences" now resolve to ADR 0013, so INDEX/STATUS may want a pointer.
- Reviewer (Combat): check that the instrumented battle engine still behaves the same (`--keep-tmp` leaves the overlay to inspect), and that the gate's tolerance and the 0%-file rule fit how you add code.

## Review log
- 2026-10-23 combat (review-sweep-A): **approve with fixes**. The instrumentation is sound, and I could not break it with syntax. I ran 11 tricky cases through `instrument.py`, and a fixture under Godot 4.6.3 plain and instrumented in a throwaway project, with `integer_division` treated as an error. The output was identical in every case. The cases covered: `is not`, variadic `...args`, `@abstract`, single-line lambdas inside array and dict literals and as a `reduce` argument followed by more arguments, ternaries of lambdas, nested lambdas, `await` inside `if`, match with multiple, array and dict patterns, typed-array and PackedInt32Array `for` loops that keep `:=` inference, and an inline `@warning_ignore` (it still suppresses). Line counts are preserved. The gate ran at battle 99.45% (906/911) and progression 95.42% (875/917), within the baseline, and the instrumented engine passes every battle test unchanged.
  - **blocker** (gate reliability; must be fixed before done): on unchanged `main`, `run_coverage.py --compare-log` failed 2 of 3 runs with exit 2, because `test_scene_router_swap.gd::test_swap_frame_stays_under_threshold_for_every_target` (`tests/unit/test_scene_router_swap.gd:28`, a 40 ms wall-clock threshold) fails under coverage. The plain run passed. The gate requires the whole suite to pass and match under instrumentation, so it inherits every wall-clock test's flakiness, amplified by probe overhead and the cold copied project. The test (M1-RND-06) landed after this gate was designed, but the interaction belongs to the gate. Fix: have `run_coverage.py` skip perf-tagged tests, for example with an exclude list in `baseline.json` or a `HYMN_COV_OUT` check in the perf tests. Keep those tests in the plain CI step, and have `compare_runs` ignore the excluded names.
  - **nit** (fairness): with battle at 99.45% of 911 lines, the 0.5 pp tolerance is about 4.5 uncovered lines per change. That is fair, since SPEC §5.4 says coverage may not drop, but it means every defensive `push_error` branch for bad data needs a fixture test. Add one sentence to `docs/kb/qa/coverage.md` so authors expect it. The 0%-file rule is fine for how Combat adds files: a new `sim_policy_*` file is always exercised by its integration test.
  - Engine behaviour under instrumentation is confirmed through `--compare-log` against a plain full-suite log: on the passing run, all 472 per-test results matched, including every battle and progression test. I did not inspect the overlay with `--keep-tmp`.
