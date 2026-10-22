# Coverage gate for battle/ and progression/ (SPEC §5.4, M1-QA-03, ADR 0013)

SPEC §5.4: *"a PR that lowers coverage of `battle/` or `progression/` gets rejected."* This gate enforces that rule automatically.

```bash
python3 tools/coverage/run_coverage.py                    # measure + gate (exit 1 on a drop)
python3 tools/coverage/run_coverage.py --update-baseline  # after adding tests: ratchet the baseline up
python3 tools/coverage/run_coverage.py --filter=lattice   # quick look for a subset of test files (no gate)
```

It runs as a step in `tools/ci_local.sh` (after "Godot tests") and in the CI `godot` job. It needs `godot` on PATH (or `$GODOT`, or `--godot`) and `pip install -r tools/requirements.txt` (for gdtoolkit).

## What is measured

- **Files:** every `.gd` under `game/battle/` and `game/progression/`, found by globbing on each run, so new files are picked up automatically. `game/battle/scene/**` is excluded because it is UI glue, covered by screenshots and the sandbox scene. The list lives in `MEASURED_DIRS` / `EXCLUDE` in `run_coverage.py`.
- **Lines:** the first line of every statement inside a function body, lambda, setter or getter. That includes `var`, expressions, `return`, `pass`, `break`, `continue`, and the header lines of `if`/`elif`/`while`/`for`/`match`.
- **Not counted:** `else:` lines, `match` patterns, continuation lines of a multi-line statement, `func` headers, comments, and class-level `var`/`const` initializers.
- **Test suite:** `res://tests/run_tests.tscn`, the full unit and integration suite. Every test counts, including integration tests.

## How it works

1. The tool copies the project to a temp dir (`$TMPDIR/hymn_cov.*`), skipping `.git`, `.godot`, `.claude` and build outputs.
2. `tools/coverage/instrument.py` parses each measured script with gdtoolkit's GDScript grammar and inserts probes **on the same line**, so the line numbers in errors and backtraces don't change:

   | Original | Instrumented |
   |---|---|
   | `var x := f()` | `HymnCov.h(12); var x := f()` |
   | `if a > b: return a` | `if HymnCov.t(13) and (a > b): HymnCov.h(14); return a` |
   | `while busy:` | `while HymnCov.t(15) and (busy):` |
   | `for c in _roster:` | `for c in (_roster if HymnCov.t(16) else _roster):` |
   | `for i in range(n):` | `for i in range((n if HymnCov.t(17) else n)):` (keeps `i: int`) |
   | `match stat:` | `match (stat if HymnCov.t(18) else stat):` |
   | `arr.map(func(x): return x * 2)` | `arr.map(func(x): HymnCov.h(19); return x * 2)` |

   `t()` always returns `true`, so `t() and (cond)` behaves exactly like `cond`. The ternary keeps the static type of the original expression and evaluates it once.
3. The tool copies the recorder `tools/coverage/hymn_cov.gd` (`class_name HymnCov`, static, typed) into the overlay and registers it as the `HymnCovSink` autoload. `tools/coverage/.gdignore` keeps it out of the real project.
4. It runs `godot --headless --import` twice, as `ci_local.sh` does (pass 1 warms the translation import), then runs the test runner with `HYMN_COV_OUT` set. The recorder writes the hit probe ids when it exits.
5. It writes the reports and compares against `tools/coverage/baseline.json`.

**Safety checks:** the run fails with exit 2, which is a broken gate rather than a coverage drop, in these cases:
- the instrumented project logs a parse or script error on import or during the tests;
- any test fails;
- `--compare-log <plain test log>` is given and any test's PASS/FAIL result, or the test count, differs from the plain run.

`ci_local.sh` and CI always pass the plain log. `tools/tests/test_coverage_instrument.py` also runs a fixture full of awkward syntax plain and instrumented under Godot and checks that the output is byte-identical.

## Reading the report

`tools/coverage/out/` is gitignored:

- `coverage.txt`: per-directory totals, then one row per file: executable lines, missed lines, percentage, and the **missed line numbers** as ranges (`20-24, 73`). After that come the 15 least-covered functions (`file:line name()`).
- `coverage.json`: the same data for tools. Per file it holds `lines`, `covered`, `pct`, `missed`, `hit`, and per-function `{line, lines, covered}`. It also has `least_covered`, `tests` and `elapsed_s`.
- `annotated/<path>.gd.txt`: the source with a margin mark per line. `+` means hit, `-` means never executed, and a blank means not executable. Open it next to the script and look for `-`.
- `cov_import*.log`, `cov_tests.log`: the Godot logs of the instrumented run, for when the gate itself fails.

The gate prints one line per directory, a `note:` when coverage rose (time to ratchet), and a `DROP` line for each failure.

## The gate

| Condition | Result |
|---|---|
| A directory falls more than **0.5 pp** below its baseline | exit 1 |
| A file that isn't in the baseline has executable lines and **0%** | exit 1 (a new untested file) |
| A baselined file with coverage above 0 falls to **0%** | exit 1 |
| A file moves, or is renamed, within a directory | only the directory total matters, so refactors pass |
| Coverage rose by more than 0.5 pp | passes, with a note to run `--update-baseline` |

The tolerance absorbs small denominator changes, such as a refactor that adds a few lines that are covered anyway. It isn't an allowance for untested code.

## Updating the baseline (legitimately)

`tools/coverage/baseline.json` is committed and **only goes up**.

- **Ratchet after adding tests.** When your PR adds tests and the gate says coverage rose, run `python3 tools/coverage/run_coverage.py --update-baseline` and commit `baseline.json` with the tests, in the same commit or PR.
- **Never update it to hide a drop.** If the gate fails, write the missing tests. `--update-baseline` refuses to lower any directory or zero out a file.
- **The one exception** is a deliberate drop, for example a large engine feature that lands behind a test task. That needs `--update-baseline --accept-drop`, plus a reviewer (QA, or the role pair from SPEC §12.3) recording the reason and the follow-up task id in the task's Review log.
- **Concurrent branches.** When two branches both ratchet, merge `baseline.json` by taking the lower value per key, then re-run the gate on the merged tree and ratchet again.

## Limitations

- **Line coverage, not branch coverage.** `if a and b:` counts as hit even if `b` never runs, and an inline `if x: return 1` line is hit if the condition ran, even when the `return` didn't. Use the annotated view when a line feels too green.
- Lambda lines count toward the enclosing function. Setters and getters are reported as `var.set` / `var.get`.
- The tool depends on gdtoolkit's grammar. If GDScript gains syntax that gdtoolkit can't parse yet, the run fails with exit 2, naming the file. gdlint fails on it too, so CI already flags it. Statement kinds the instrumenter doesn't know are left unprobed instead of being broken.
- `game/battle/scene/**` and everything outside the two directories are unmeasured.
- Probes cost a static call per statement. The instrumented suite runs in about the same wall time, because Godot startup dominates. A whole run takes about 20 to 30 s: two overlay imports plus one test run.
- The overlay keeps the project name, so tests that write `user://` share the real project's user dir, just as the plain test run does.
- The CI `godot` job runs the official Godot build. The baseline was recorded with the sandbox's distro build of the same 4.6.3 version. Coverage doesn't depend on the renderer, so the numbers should match. If they ever disagree, trust CI and re-baseline there.

## Current numbers (2026-10-22, 223 tests)

| Directory | Coverage | Lines |
|---|---|---|
| `game/battle/` (excl. `scene/`) | **91.70%** | 464 / 506 |
| `game/progression/` | **93.06%** | 335 / 360 |

Run time: about 19 to 29 s on the 4-core sandbox. `ci_local.sh` prints it as `coverage step: Ns`.

### To-do: the 5 least-covered functions

Ranked by percentage, then missed lines. Each item is a test to write, or dead code to delete.

1. **combat**: `game/battle/ctb_timeline.gd:19 eligible()`, **0%** (5 lines). Nothing calls it, not even the battle scene. Either test it (alive vs KO'd roster) or remove it.
2. **progression**: `game/progression/lattice_rules.gd:76 facet_name_key()`, **0%** (1 line). Add a test for a known facet's `name_key` and for the unknown-facet fallback `""`.
3. **progression**: `game/progression/lattice_progress.gd:315 _add_stat()`, **50%** (7 missed). The `magic`, `defense`, `magic_defense`, `accuracy`, `evasion` and `luck` arms and the unknown-stat `push_error` arm never run. A table-driven test over every stat id would cover them.
4. **combat**: `game/battle/ctb_timeline.gd:100 _sim_add_status()`, **57%** (3 missed). Never exercised: a non-timed status in `status_changes` (the early return), and Slow replacing Haste in a timeline preview.
5. **progression**: `game/progression/lattice_rules.gd:24 load_file()`, **60%** (2 missed). The parse-failure path (lines 27–28) is untested.

Next in line: `battle_engine.gd:131 run_enemy_turn()` at 62% (the no-valid-action idle path and the bad-data turn loss), `lattice_board.gd:25 load_board()` at 67%, and `facet_inventory.gd:21 add()` at 67%. Always check `coverage.txt` for the current list.
