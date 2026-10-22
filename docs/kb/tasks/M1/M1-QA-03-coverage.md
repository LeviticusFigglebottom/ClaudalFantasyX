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
