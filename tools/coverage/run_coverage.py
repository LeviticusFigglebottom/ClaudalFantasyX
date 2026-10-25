#!/usr/bin/env python3
"""Line-coverage gate for game/battle/, game/progression/ and game/minigames/reefball/ (M1-QA-03, ADR 0013).

  python3 tools/coverage/run_coverage.py                    # measure, report, gate against baseline
  python3 tools/coverage/run_coverage.py --update-baseline  # after adding tests: ratchet the baseline
  python3 tools/coverage/run_coverage.py --filter=battle    # report only, for a subset of test files

Copies the project to a temp dir, instruments the measured scripts there (tools/coverage/instrument.py),
imports it twice with headless Godot, runs res://tests/run_tests.tscn, and collects the probe hits that
the HymnCov recorder writes on exit. Reports go to tools/coverage/out/ (coverage.txt, coverage.json,
annotated/). The working tree is never modified, except baseline.json with --update-baseline.

Exit codes: 0 ok, 1 coverage dropped below the baseline, 2 the run itself failed (instrumented project
did not import, tests failed or changed under instrumentation, Godot missing...).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instrument  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
COV_DIR = ROOT / "tools" / "coverage"
OUT_DIR = COV_DIR / "out"
BASELINE = COV_DIR / "baseline.json"
RECORDER_SRC = COV_DIR / "hymn_cov.gd"
RECORDER_RES = "hymn_coverage/hymn_cov.gd"
RECORDER_AUTOLOAD = "HymnCovSink"

# Measured directories (SPEC §5.4). Everything below them is measured except EXCLUDE (UI glue).
# game/minigames/reefball (M3-RBL-01): the headless Reefball rules core, held to the same bar.
MEASURED_DIRS = ("game/battle", "game/progression", "game/minigames/reefball")
EXCLUDE = ("game/battle/scene",)
TOLERANCE_PP = 0.5

# Never copied into the overlay project.
COPY_SKIP_TOP = {".git", ".godot", ".claude", "build", ".venv"}
COPY_SKIP_PATHS = {"tools/coverage/out", "tests/screenshots/out"}
ERROR_RE = re.compile(r"SCRIPT ERROR|Parse Error|Failed to load script|Failed loading resource")
TEST_LINE_RE = re.compile(r"^\s+(PASS|FAIL) (\S+)$", re.M)
SUMMARY_RE = re.compile(r"Tests: (\d+) run, (\d+) failed")


class RunError(Exception):
    """The measurement itself failed (exit 2)."""


# --- discovery and overlay -------------------------------------------------------------------------
def measured_files(root: Path = ROOT) -> list[str]:
    """Repo-relative paths of every measured .gd file (sorted, generic: no hard-coded file list)."""
    out: list[str] = []
    for d in MEASURED_DIRS:
        for p in sorted((root / d).rglob("*.gd")):
            rel = p.relative_to(root).as_posix()
            if not any(rel == e or rel.startswith(e + "/") for e in EXCLUDE):
                out.append(rel)
    return sorted(out)


def directory_of(rel: str) -> str:
    return next(d for d in MEASURED_DIRS if rel.startswith(d + "/"))


def _copy_ignore(src_root: Path):
    def ignore(dirpath: str, names: list[str]) -> set[str]:
        rel = Path(dirpath).resolve().relative_to(src_root)
        skip: set[str] = {"__pycache__"} & set(names)
        if rel == Path("."):
            skip |= COPY_SKIP_TOP & set(names)
        for n in names:
            if (rel / n).as_posix() in COPY_SKIP_PATHS:
                skip.add(n)
        return skip

    return ignore


def add_autoload(project_text: str, name: str, res_path: str) -> str:
    """Adds `name` as the first autoload in a project.godot text."""
    entry = f'{name}="*res://{res_path}"\n'
    if re.search(r"^\[autoload\]\s*$", project_text, re.M):
        return re.sub(r"^\[autoload\]\s*\n", lambda m: m.group(0) + entry, project_text, count=1, flags=re.M)
    return project_text.rstrip("\n") + "\n\n[autoload]\n\n" + entry


@dataclass
class Overlay:
    path: Path
    probes: dict[str, list[instrument.Probe]] = field(default_factory=dict)
    functions: dict[str, dict[str, int]] = field(default_factory=dict)


def build_overlay(dest: Path, files: list[str], root: Path = ROOT) -> Overlay:
    shutil.copytree(root, dest, ignore=_copy_ignore(root.resolve()), symlinks=True)
    ov = Overlay(dest)
    next_id = 0
    for rel in files:
        src = (root / rel).read_text(encoding="utf-8")
        try:
            res = instrument.instrument(src, next_id)
        except Exception as exc:  # lark raises several exception types
            raise RunError(f"{rel}: gdtoolkit could not parse it ({type(exc).__name__}: {exc})") from exc
        next_id += len(res.probes)
        (dest / rel).write_text(res.source, encoding="utf-8")
        ov.probes[rel] = res.probes
        ov.functions[rel] = res.functions
    rec = dest / RECORDER_RES
    rec.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RECORDER_SRC, rec)
    proj = dest / "project.godot"
    proj.write_text(add_autoload(proj.read_text(encoding="utf-8"), RECORDER_AUTOLOAD, RECORDER_RES), encoding="utf-8")
    return ov


# --- running Godot ---------------------------------------------------------------------------------
def _run(cmd: list[str], log: Path, env: dict[str, str] | None = None) -> int:
    timeout = int(os.environ.get("HYMN_STEP_TIMEOUT", "600"))
    with log.open("w", encoding="utf-8") as fh:
        try:
            return subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, env=env, timeout=timeout).returncode
        except subprocess.TimeoutExpired as exc:
            raise RunError(f"timed out after {timeout}s: {' '.join(cmd)} (log: {log})") from exc


def run_godot(godot: str, project: Path, logs: Path, hits_file: Path, test_filter: str) -> str:
    """Imports the overlay twice (pass 1 warms the cache, see ci_local.sh) and runs the test suite."""
    _run([godot, "--headless", "--path", str(project), "--import"], logs / "cov_import_warm.log")
    _run([godot, "--headless", "--path", str(project), "--import"], logs / "cov_import.log")
    imp = (logs / "cov_import.log").read_text(encoding="utf-8", errors="replace")
    bad = [ln for ln in imp.splitlines() if ERROR_RE.search(ln)]
    if bad:
        raise RunError("instrumented project failed to import:\n  " + "\n  ".join(bad[:20]))
    env = dict(os.environ, HYMN_COV_OUT=str(hits_file))
    cmd = [godot, "--headless", "--path", str(project), "res://tests/run_tests.tscn"]
    if test_filter:
        cmd += ["--", f"--filter={test_filter}"]
    code = _run(cmd, logs / "cov_tests.log", env)
    out = (logs / "cov_tests.log").read_text(encoding="utf-8", errors="replace")
    errs = [ln for ln in out.splitlines() if re.search(r"SCRIPT ERROR|Parse Error", ln)]
    summary = SUMMARY_RE.search(out)
    if errs or summary is None or summary.group(2) != "0" or code != 0:
        fails = [m.group(2) for m in TEST_LINE_RE.finditer(out) if m.group(1) == "FAIL"]
        detail = "\n  ".join((errs + fails)[:20]) or "(no summary line)"
        raise RunError(f"test suite did not pass under instrumentation (exit {code}):\n  {detail}")
    if not hits_file.exists():
        raise RunError("HymnCov wrote no hits file (did the recorder autoload run?)")
    return out


def test_results(log_text: str) -> dict[str, str]:
    return {m.group(2): m.group(1) for m in TEST_LINE_RE.finditer(log_text)}


def compare_runs(instrumented_log: str, plain_log: str) -> list[str]:
    """Differences between the instrumented and the plain run (must be none: probes are inert)."""
    a, b = test_results(instrumented_log), test_results(plain_log)
    problems: list[str] = []
    if len(a) != len(b):
        problems.append(f"test count differs: {len(a)} instrumented vs {len(b)} plain")
    for name in sorted(set(a) | set(b)):
        if a.get(name) != b.get(name):
            problems.append(f"{name}: {a.get(name, 'missing')} instrumented vs {b.get(name, 'missing')} plain")
    return problems


# --- report ----------------------------------------------------------------------------------------
def _pct(covered: int, total: int) -> float:
    return round(100.0 * covered / total, 2) if total else 100.0


def build_report(ov: Overlay, hit_ids: set[int]) -> dict:
    files: dict[str, dict] = {}
    for rel, probes in ov.probes.items():
        line_hit: dict[int, bool] = {}
        func_lines: dict[str, dict[int, bool]] = {}
        for p in probes:
            hit = p.id in hit_ids
            line_hit[p.line] = line_hit.get(p.line, False) or hit
            fl = func_lines.setdefault(p.func, {})
            fl[p.line] = fl.get(p.line, False) or hit
        covered = sum(line_hit.values())
        funcs = {}
        for name, header in sorted(ov.functions[rel].items(), key=lambda kv: kv[1]):
            fl = func_lines.get(name, {})
            funcs[name] = {"line": header, "lines": len(fl), "covered": sum(fl.values())}
        files[rel] = {
            "lines": len(line_hit),
            "covered": covered,
            "pct": _pct(covered, len(line_hit)),
            "missed": sorted(ln for ln, h in line_hit.items() if not h),
            "hit": sorted(ln for ln, h in line_hit.items() if h),
            "functions": funcs,
        }
    dirs = {}
    for d in MEASURED_DIRS:
        mine = [f for rel, f in files.items() if directory_of(rel) == d]
        total, cov = sum(f["lines"] for f in mine), sum(f["covered"] for f in mine)
        dirs[d] = {"files": len(mine), "lines": total, "covered": cov, "pct": _pct(cov, total)}
    return {"directories": dirs, "files": files}


def least_covered_functions(report: dict, n: int = 5) -> list[dict]:
    rows = []
    for rel, f in report["files"].items():
        for name, fn in f["functions"].items():
            if fn["lines"] and fn["covered"] < fn["lines"]:
                rows.append(
                    {
                        "file": rel,
                        "function": name,
                        "line": fn["line"],
                        "lines": fn["lines"],
                        "missed": fn["lines"] - fn["covered"],
                        "pct": _pct(fn["covered"], fn["lines"]),
                    }
                )
    rows.sort(key=lambda r: (r["pct"], -r["missed"], r["file"], r["line"]))
    return rows[:n]


def _ranges(lines: list[int]) -> str:
    out: list[str] = []
    for ln in lines:
        if out and isinstance(out[-1], list) and out[-1][1] == ln - 1:
            out[-1][1] = ln
        else:
            out.append([ln, ln])
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in out)


def render_text(report: dict, elapsed: float) -> str:
    lines = ["Line coverage (ADR 0013): executable statements hit by tests/run_tests.tscn", ""]
    for d, s in report["directories"].items():
        lines.append(f"{d + '/':<22} {s['pct']:6.2f}%  ({s['covered']}/{s['lines']} lines, {s['files']} files)")
    lines += ["", f"{'file':<44} {'lines':>5} {'miss':>5} {'cover':>7}  missed lines"]
    for rel, f in sorted(report["files"].items()):
        miss = f["lines"] - f["covered"]
        lines.append(f"{rel:<44} {f['lines']:>5} {miss:>5} {f['pct']:6.2f}%  {_ranges(f['missed'])}")
    lines += ["", "Least-covered functions:"]
    for r in least_covered_functions(report, 15):
        lines.append(f"  {r['pct']:6.2f}%  {r['missed']:>3} missed  {r['file']}:{r['line']} {r['function']}()")
    lines += ["", f"Measured in {elapsed:.1f}s."]
    return "\n".join(lines) + "\n"


def write_annotated(report: dict, out: Path) -> None:
    """One file per script: '+' hit, '-' missed, ' ' not executable."""
    for rel, f in report["files"].items():
        missed, hit = set(f["missed"]), set(f["hit"])
        src = (ROOT / rel).read_text(encoding="utf-8").splitlines()
        dest = out / (rel + ".txt")
        dest.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for i, text in enumerate(src, 1):
            mark = "-" if i in missed else ("+" if i in hit else " ")
            rows.append(f"{mark} {i:4d}  {text}")
        dest.write_text("\n".join(rows) + "\n", encoding="utf-8")


# --- baseline gate ---------------------------------------------------------------------------------
def gate(report: dict, baseline: dict) -> tuple[list[str], list[str]]:
    """Returns (failures, notes). Directory drops beyond the tolerance and new 0% files fail."""
    tol = float(baseline.get("tolerance_pp", TOLERANCE_PP))
    fails: list[str] = []
    notes: list[str] = []
    base_dirs = baseline.get("directories", {})
    base_files = baseline.get("files", {})
    for d, s in report["directories"].items():
        if d not in base_dirs:
            notes.append(f"{d}: no baseline yet ({s['pct']:.2f}%)")
            continue
        b = float(base_dirs[d])
        if s["pct"] < b - tol:
            fails.append(f"{d}: {s['pct']:.2f}% is below the baseline {b:.2f}% (tolerance {tol} pp)")
        elif s["pct"] > b + tol:
            notes.append(f"{d}: {s['pct']:.2f}% is above the baseline {b:.2f}%: ratchet it with --update-baseline")
    for rel, f in sorted(report["files"].items()):
        if f["lines"] == 0 or f["covered"] > 0:
            continue
        if rel not in base_files:
            fails.append(f"{rel}: new file with 0% coverage ({f['lines']} lines): add tests")
        elif float(base_files[rel]) > 0:
            fails.append(f"{rel}: dropped to 0% coverage (baseline {float(base_files[rel]):.2f}%)")
    for rel in sorted(set(base_files) - set(report["files"])):
        notes.append(f"{rel}: in the baseline but no longer measured (moved or deleted?)")
    return fails, notes


def lowered_dirs(report: dict, baseline: dict) -> list[str]:
    """Directories the new numbers would lower at all (no tolerance): the baseline only ratchets up."""
    base = baseline.get("directories", {})
    return [
        f"{d}: {s['pct']:.2f}% would lower the baseline {float(base[d]):.2f}%"
        for d, s in report["directories"].items()
        if d in base and s["pct"] < float(base[d])
    ]


def make_baseline(report: dict) -> dict:
    return {
        "_comment": "ADR 0013. Change only with --update-baseline after adding tests (docs/kb/qa/coverage.md).",
        "tolerance_pp": TOLERANCE_PP,
        "directories": {d: s["pct"] for d, s in report["directories"].items()},
        "files": {rel: f["pct"] for rel, f in sorted(report["files"].items())},
    }


def load_baseline() -> dict:
    if not BASELINE.exists():
        return {}
    return json.loads(BASELINE.read_text(encoding="utf-8"))


# --- main ------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--godot", default=os.environ.get("GODOT", "godot"), help="Godot binary (default $GODOT, godot)")
    ap.add_argument("--update-baseline", action="store_true", help="write the current numbers to baseline.json")
    ap.add_argument(
        "--accept-drop", action="store_true", help="with --update-baseline: allow lowering it (reviewer must agree)"
    )
    ap.add_argument("--compare-log", type=Path, help="plain (uninstrumented) test log: per-test results must match")
    ap.add_argument("--filter", default="", help="pass --filter to the test runner (report only, no gate)")
    ap.add_argument("--keep-tmp", action="store_true", help="keep the instrumented project for debugging")
    args = ap.parse_args(argv)

    t0 = time.monotonic()
    if shutil.which(args.godot) is None:
        print(f"coverage: Godot '{args.godot}' not found (set $GODOT)", file=sys.stderr)
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="hymn_cov."))
    project = tmp / "project"
    try:
        files = measured_files()
        ov = build_overlay(project, files)
        hits_file = tmp / "hits.json"
        log_text = run_godot(args.godot, project, OUT_DIR, hits_file, args.filter)
        if args.compare_log:
            problems = compare_runs(log_text, args.compare_log.read_text(encoding="utf-8", errors="replace"))
            if problems:
                raise RunError("instrumentation changed test results:\n  " + "\n  ".join(problems[:20]))
        hit_ids = {int(i) for i in json.loads(hits_file.read_text(encoding="utf-8"))["hits"]}
    except RunError as exc:
        print(f"coverage: FAILED: {exc}", file=sys.stderr)
        print(f"coverage: logs in {OUT_DIR}", file=sys.stderr)
        return 2
    finally:
        if args.keep_tmp:
            print(f"coverage: instrumented project kept at {project}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    report = build_report(ov, hit_ids)
    elapsed = time.monotonic() - t0
    report["elapsed_s"] = round(elapsed, 1)
    report["tests"] = len(test_results(log_text))
    report["least_covered"] = least_covered_functions(report, 15)
    text = render_text(report, elapsed)
    (OUT_DIR / "coverage.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    (OUT_DIR / "coverage.txt").write_text(text, encoding="utf-8")
    shutil.rmtree(OUT_DIR / "annotated", ignore_errors=True)
    write_annotated(report, OUT_DIR / "annotated")
    for d, s in report["directories"].items():
        print(f"coverage: {d + '/':<20} {s['pct']:6.2f}%  ({s['covered']}/{s['lines']} lines)")
    print(f"coverage: {report['tests']} tests, {elapsed:.1f}s; report: {OUT_DIR.relative_to(ROOT)}/coverage.txt")

    if args.filter:
        print("coverage: --filter given: report only, baseline not checked")
        return 0
    baseline = load_baseline()
    fails, notes = gate(report, baseline) if baseline else ([], ["no baseline.json yet"])
    if args.update_baseline:
        fails += lowered_dirs(report, baseline)
        if fails and not args.accept_drop:
            for f in fails:
                print(f"coverage: DROP {f}", file=sys.stderr)
            print("coverage: refusing to lower the baseline; fix the drop or pass --accept-drop with a review note")
            return 1
        BASELINE.write_text(json.dumps(make_baseline(report), indent=2) + "\n", encoding="utf-8")
        print(f"coverage: wrote {BASELINE.relative_to(ROOT)}")
        return 0
    for n in notes:
        print(f"coverage: note: {n}")
    for f in fails:
        print(f"coverage: DROP {f}", file=sys.stderr)
    if fails:
        print("coverage: FAILED: add tests for the new or changed code (docs/kb/qa/coverage.md)", file=sys.stderr)
        return 1
    print("coverage: OK (within baseline)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
