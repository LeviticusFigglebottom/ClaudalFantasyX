#!/usr/bin/env python3
"""Lead tool: ADR 0203's Act I completion gate, criteria 1 and 2, on the checkout it runs in. Prints PASS or FAIL per
criterion with the evidence; exit 0 only when both pass. Run it from the batch's worktree root after an import:

  python3 tools/dev/lead/act1_gate_check.py               # both criteria (Godot from PATH or the fetch cache)
  python3 tools/dev/lead/act1_gate_check.py --only 1      # the audit alone
  python3 tools/dev/lead/act1_gate_check.py --static-only # criterion 1 without the runtime scan (a quick look; the
                                                          # gate itself needs the scan, so this never PASSes it)

1. **Audit:** tools/placeholder_audit.py (Act I, the runtime scan included) reports zero items.
2. **Playthrough:** the headless suites that play Act I pass with zero SCRIPT ERRORs in their logs:
   - qa_threads: every chapter thread start to end, save and load at every shrine;
   - qa_encounters: every Act I encounter entered, won, and left back to its zone;
   - fp_: title → New Game → Prologue → the slice → Ch3;
   - save_: save and load;
   - the continuous path, title → Ch9 → title, as one run (M3-CIN-1233's integration test, found by name:
     CONTINUOUS_GLOB). Until that test exists, criterion 2 FAILs and says so: the chapters played one by one can't
     show that the hand-offs between them hold.
Each suite runs alone (one Godot at a time), with its own XDG_DATA_HOME, and its log is kept under --logs.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "tools" / "placeholder_audit.py"
# The suites criterion 2 runs (run_tests.tscn --filter=<name>) and what each shows.
SUITES = [
    ("qa_threads", "every chapter thread start to end, save and load at every shrine"),
    ("qa_encounters", "every Act I encounter entered, won, and left"),
    ("fp_", "title → New Game → Prologue → the slice → Ch3"),
    ("save_", "save and load"),
]
CONTINUOUS_GLOB = "tests/integration/test_*continuous*.gd"
SUITE_TIMEOUT_S = 3600
TESTS_RE = re.compile(r"^Tests: (\d+) run, (\d+) failed", re.M)
FAILURE_RE = re.compile(r"^(FAILURE .*)$", re.M)
SCRIPT_ERROR = "SCRIPT ERROR"


def find_godot() -> str | None:
    found = shutil.which("godot")
    if found:
        return found
    cached = sorted(Path.home().glob(".cache/hymn/godot-*/godot"))
    return str(cached[-1]) if cached else None


def criterion_audit(static_only: bool) -> tuple[bool, list[str]]:
    """Criterion 1. Returns (passed, evidence lines)."""
    cmd = [sys.executable, str(AUDIT)] + (["--static-only"] if static_only else [])
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    m = re.search(r"placeholder audit: (\d+) items", r.stdout)
    if m is None:
        return False, ["the audit printed no count (exit %d): %s" % (r.returncode, r.stderr.strip()[-300:])]
    n = int(m.group(1))
    if static_only:
        return False, lines + ["static checks only: the gate needs the runtime scan (drop --static-only)"]
    if "no godot on PATH" in r.stderr:
        return False, lines + ["no Godot: the runtime scan didn't run, so this isn't the gate's audit"]
    return n == 0, lines


def suite_result(log: str) -> tuple[int, int, list[str], int]:
    """(run, failed, the FAILURE lines, SCRIPT ERROR count) from a run_tests log."""
    m = TESTS_RE.search(log)
    run, failed = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    return run, failed, FAILURE_RE.findall(log), log.count(SCRIPT_ERROR)


def criterion_playthrough(godot: str | None, logs: Path) -> tuple[bool, list[str]]:
    """Criterion 2. Returns (passed, evidence lines)."""
    if godot is None:
        return False, ["no Godot (python3 tools/dev/fetch_godot.py): nothing was played"]
    evidence: list[str] = []
    passed = True
    suites = list(SUITES)
    continuous = sorted(ROOT.glob(CONTINUOUS_GLOB))
    for p in continuous:
        suites.append((p.stem.removeprefix("test_"), "the continuous path (%s)" % p.name))
    if not continuous:
        passed = False
        evidence.append(
            "MISSING the continuous title → Ch9 → title test (%s; M3-CIN-1233): the hand-offs between chapters are "
            "unchecked" % CONTINUOUS_GLOB
        )
    logs.mkdir(parents=True, exist_ok=True)
    for name, what in suites:
        with tempfile.TemporaryDirectory(prefix="act1_gate_") as xdg:
            env = dict(os.environ, XDG_DATA_HOME=xdg)
            try:
                r = subprocess.run(
                    [godot, "--headless", "--path", str(ROOT), "res://tests/run_tests.tscn", "--", "--filter=%s" % name],
                    cwd=ROOT, env=env, capture_output=True, text=True, timeout=SUITE_TIMEOUT_S, check=False,
                )
                log = r.stdout + r.stderr
            except subprocess.TimeoutExpired as e:
                log = str(e.stdout or "") + "\nTIMEOUT after %d s" % SUITE_TIMEOUT_S
        (logs / ("%s.log" % name.rstrip("_"))).write_text(log, encoding="utf-8")
        run, failed, failures, script_errors = suite_result(log)
        ok = run > 0 and failed == 0 and script_errors == 0 and "TIMEOUT" not in log
        passed = passed and ok
        evidence.append(
            "%s %s (%s): %d run, %d failed, %d SCRIPT ERROR" % ("ok  " if ok else "FAIL", name, what, run, failed,
                                                                script_errors)
        )
        evidence += ["       %s" % f[:200] for f in failures[:5]]
    evidence.append("logs: %s" % logs)
    return passed, evidence


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", choices=["1", "2"], help="one criterion")
    ap.add_argument("--static-only", action="store_true", help="criterion 1 without the runtime scan (never PASSes)")
    ap.add_argument("--logs", default=str(Path(tempfile.gettempdir()) / "act1_gate_logs"), help="where suite logs go")
    args = ap.parse_args(argv)
    results: list[bool] = []
    if args.only in (None, "1"):
        ok, lines = criterion_audit(args.static_only)
        print("%s  1. Audit: zero Act I items (tools/placeholder_audit.py)" % ("PASS" if ok else "FAIL"))
        print("\n".join("      " + ln for ln in lines))
        results.append(ok)
    if args.only in (None, "2"):
        ok, lines = criterion_playthrough(find_godot(), Path(args.logs))
        print("%s  2. Playthrough: Act I played headless, zero SCRIPT ERRORs" % ("PASS" if ok else "FAIL"))
        print("\n".join("      " + ln for ln in lines))
        results.append(ok)
    print("ADR 0203 criteria %s: %s" % ("1-2" if args.only is None else args.only, "PASS" if all(results) else "FAIL"))
    print("(3-5 are the batch gate, the PC's GPU QA and the hitch budget: the Lead's and the PC's records.)")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
