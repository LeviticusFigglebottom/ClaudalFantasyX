# 0013 — Coverage gate: source instrumentation of battle/ and progression/

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** combat, progression, QA, architect (CI)
- **Author role:** QA

## Context
SPEC §5.4 says "a PR that lowers coverage of `battle/` or `progression/` gets rejected". ADR 0006 chose an in-repo test runner instead of GUT or gdUnit4, so there is no coverage tooling, and the rule could only be checked by eye in review. M1-QA-03 makes it an automatic gate.

Constraints:
- GDScript has no built-in coverage hook. Godot exposes no line-hit callback to scripts.
- Addons can't be downloaded here (GitHub is blocked), and gdUnit4's coverage support isn't usable for this anyway: it needs its own runner and a vendored addon (ADR 0006).
- Python tooling is limited to the stdlib plus pinned PyPI packages. `gdtoolkit` 4.5.0 is already pinned for gdlint/gdformat, and it ships a full Lark grammar for GDScript 4.
- Other agents edit `game/battle/` and add tests at the same time, so the tool must find files itself and must not hard-code a file list.
- The battle engine is headless and deterministic (CLAUDE.md §3). Measuring must not change behaviour.

## Options
1. **Source instrumentation (chosen).** A Python tool copies the project to a temp dir and rewrites the measured scripts there. Each executable statement first calls a static recorder (`HymnCov.h(id)`), and the recorder dumps the hit ids when the run exits. The gdtoolkit parse tree supplies statement positions, so multi-line statements, inline suites, `match` arms, lambdas, setters/getters, inner classes, and static and `@tool` functions are handled structurally, with no regexes. Real line coverage, any Godot build, about 20 to 30 s.
2. **Debugger protocol / `--debug` stepping.** Drive the remote debugger (`--remote-debug`) and single-step, or set a breakpoint on every line. This is impractical: stepping costs a round trip per line, which makes the 223-test suite take minutes to hours. The protocol is undocumented and changes between minor versions, and `--headless` test runs would need a debugger server written in Python. Rejected.
3. **Function-level static mapping.** Parse every public function and grep the tests for calls to it. This is cheap, but it only proves a function's name appears in a test, not that its branches run. It can't see dynamic dispatch (`call()`, signals, `Callable`s) and gives no line-level to-do list. Rejected as the gate. Function rollups are still reported from the option 1 data.
4. **Adopt gdUnit4 coverage.** Blocked by the addon download, and it would also undo ADR 0006. Can be revisited if ADR 0006 is ever superseded.

## Decision
Use option 1, implemented in `tools/coverage/`:
- `instrument.py` makes same-line edits only, so line numbers in errors and backtraces are unchanged:
  - simple statements: `HymnCov.h(N); stmt`
  - `if`/`elif`/`while`: `HymnCov.t(N) and (cond)`. `t()` returns true, and `and` booleanizes the same way the bare condition does.
  - `for` iterables and `match` subjects: `(e if HymnCov.t(N) else e)`. The value has the same static type and is evaluated once. For `range(...)`, the first argument is wrapped instead, because the analyzer types the loop variable as `int` only for a literal `range()` call.
- `hymn_cov.gd`: a typed `@tool` static recorder, added as the `HymnCovSink` autoload in the overlay's `project.godot`. It writes `$HYMN_COV_OUT` on `_exit_tree`. `tools/coverage/.gdignore` keeps it out of the real project.
- `run_coverage.py` instruments `game/battle/**` and `game/progression/**`, excluding `game/battle/scene/**` (UI glue). It imports the overlay twice (the same warm-up as `ci_local.sh`), runs `res://tests/run_tests.tscn`, and writes `tools/coverage/out/` (text, JSON, annotated sources).
  - It fails with exit 2 if the instrumented run reports a script error or a failing test, or if (with `--compare-log`) any per-test result differs from the plain run.
  - It fails with exit 1 if a directory drops more than **0.5 pp** below `tools/coverage/baseline.json`, if a new file has 0% coverage, or if a baselined file falls to 0%.
- Wired into `tools/ci_local.sh` after the Godot tests (it reuses their log for `--compare-log`) and into the CI `godot` job.
- The baseline only moves up, via `--update-baseline` in a PR that adds tests. `--update-baseline` refuses to lower it unless `--accept-drop` is also passed, and the reviewer must agree to that in the task's Review log.

## Consequences
- The §5.4 rule is enforced mechanically, and the report gives Combat and Progression a line-level list of untested code (`docs/kb/qa/coverage.md`).
- About 20 to 30 s extra per local CI run (two imports plus one test run of the overlay).
- What counts: lines covered at statement start. Branch coverage is not measured: in `if a and b`, the line counts as hit even if `b` never runs. `else:` lines and `match` patterns are not counted, but their bodies are. A multi-line statement counts once. Class-level `var`/`const` initializers are not counted.
- When GDScript gains syntax, gdtoolkit's grammar has to follow. Until it does, gdlint fails on the same file, so CI already flags it. Statement kinds the instrumenter doesn't know are left unprobed instead of being broken.
- Moving code between files changes per-file numbers. Only directory totals and 0% files gate, so refactors don't trip the gate.
- To measure another directory, edit `MEASURED_DIRS` and update the baseline in one reviewed commit.
