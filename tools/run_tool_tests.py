#!/usr/bin/env python3
"""Run a unittest suite (default tools/tests) as parallel subprocesses, one per test module (M2-NIT-06).

The same tests as `python3 -m unittest discover -s tools/tests`, but each module runs in its own process, so a
slow module no longer holds up the rest. A module named in SPLIT runs one process per TestCase class instead.
The heaviest units start first (WEIGHT). Every unit's output is kept; a failing unit's output is printed in
full. Exit status 1 if any unit fails.

    python3 tools/run_tool_tests.py              # -j defaults to HYMN_TEST_JOBS, else the CPU count
    python3 tools/run_tool_tests.py -j 2 -k lattice
    python3 tools/run_tool_tests.py -s tools/audio/tests

Tests must be independent of each other and of other processes: unique temp dirs (tempfile), no fixed
scratch paths. Children get HYMN_TEST_JOBS=1 unless the caller set it, so a module with its own pool
(test_audio_loudness) does not multiply the worker count; that module is scheduled first and given the
caller's -j as its own pool size."""
from __future__ import annotations

import argparse
import ast
import os
import re
import subprocess
import sys
import time
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Rough cold-run seconds on 4 cores (2026-10-24), only to start the long units first; unknown units weigh 0.
WEIGHT = {"test_audio_loudness": 400, "test_rig_integrity": 90, "test_items_validate": 40, "test_asha": 21,
          "test_validate_data": 21, "test_toma": 17, "test_lattice_validate": 15, "test_rhen": 12}
SPLIT = {"test_rig_integrity"}  # one process per TestCase class: each hero's probe takes ~30 s
OWN_POOL = {"test_audio_loudness"}  # measures in its own process pool, sized by HYMN_TEST_JOBS
RAN_RE = re.compile(r"^Ran (\d+) tests? in ", re.M)
SKIP_RE = re.compile(r"skipped=(\d+)")


def test_classes(path: Path) -> list[str]:
    """Top-level classes in a test module that derive (by name) from a *TestCase base."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            if any(b.endswith("TestCase") for b in bases):
                out.append(node.name)
    return out


def units(start: Path, pattern: str, keyword: str) -> list[str]:
    mods = sorted(p for p in start.glob(pattern) if p.is_file())
    out: list[str] = []
    for p in mods:
        if keyword and keyword not in p.stem:
            continue
        classes = test_classes(p) if p.stem in SPLIT else []
        out += [f"{p.stem}.{c}" for c in classes] or [p.stem]
    return sorted(out, key=lambda u: (-WEIGHT.get(u.split(".")[0], 0), u))


def run_unit(unit: str, start: Path, jobs: int) -> tuple[str, int, float, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(start)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
    if "HYMN_TEST_JOBS" not in os.environ:
        env["HYMN_TEST_JOBS"] = str(jobs if unit.split(".")[0] in OWN_POOL else 1)
    t = time.monotonic()
    proc = subprocess.run([sys.executable, "-m", "unittest", unit], cwd=ROOT, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return unit, proc.returncode, time.monotonic() - t, proc.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-s", "--start", type=Path, default=ROOT / "tools" / "tests")
    ap.add_argument("-p", "--pattern", default="test*.py")
    ap.add_argument("-k", "--keyword", default="", help="only modules whose name contains this")
    env_jobs = os.environ.get("HYMN_TEST_JOBS", "")
    ap.add_argument("-j", "--jobs", type=int, default=int(env_jobs) if env_jobs.isdigit() else os.cpu_count() or 1)
    args = ap.parse_args()
    start = args.start.resolve()
    todo = units(start, args.pattern, args.keyword)
    if not todo:
        print(f"run_tool_tests: no test modules under {start} match {args.pattern!r}")
        return 1
    jobs = max(1, args.jobs)
    t0 = time.monotonic()
    ran = skipped = 0
    failed: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(run_unit, u, start, jobs) for u in todo]
        for fut in as_completed(futures):
            unit, rc, secs, out = fut.result()
            n = sum(int(m) for m in RAN_RE.findall(out))
            s = sum(int(m) for m in SKIP_RE.findall(out.splitlines()[-1] if out.strip() else ""))
            ran, skipped = ran + n, skipped + s
            print(f"{'ok  ' if rc == 0 else 'FAIL'} {secs:7.1f}s {n:4d} tests  {unit}", flush=True)
            if rc != 0 or n == 0:
                failed.append((unit, out))
    for unit, out in failed:
        print(f"\n===== {unit} =====\n{out}")
    if not args.keyword:
        # The units must add up to exactly what `unittest discover` would run (a SPLIT module's classes too).
        expected = unittest.defaultTestLoader.discover(str(start), pattern=args.pattern).countTestCases()
        if ran != expected:
            failed.append(("(count)", ""))
            print(f"run_tool_tests: ran {ran} tests but unittest discover finds {expected}")
    status = "FAILED" if failed else "OK"
    print(f"\nrun_tool_tests: {len(todo)} units, {ran} tests ({skipped} skipped) in "
          f"{time.monotonic() - t0:.1f}s with -j {jobs}: {status}"
          + (f" ({', '.join(u for u, _ in failed)})" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
