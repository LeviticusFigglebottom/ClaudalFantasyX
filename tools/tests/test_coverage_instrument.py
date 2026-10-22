"""Tests for tools/coverage (ADR 0013). Run: python3 -m unittest discover -s tools/tests

The instrumenter must keep every script parseable and behaviourally identical. Syntax cases are checked
with gdtoolkit; when `godot` (or $GODOT) is on PATH, the fixture is also run plain and instrumented and the
outputs must match exactly.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gdtoolkit.parser import parser

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "coverage"))
import instrument  # noqa: E402
import run_coverage  # noqa: E402

HELPER = '''@tool
class_name CovFixtureHelper
extends RefCounted


static func clamp_sum(values: Array[int], limit: int) -> int:
	var total := 0
	for v in values: total += v
	if total > limit: return limit
	elif total < 0: return 0
	else: return total
'''

MAIN = '''extends Node

var log_lines: PackedStringArray = []
var hp: int = 0:
	set(value):
		hp = clampi(value, 0, 99)
	get:
		return hp


func _ready() -> void:
	note("sum=%d" % CovFixtureHelper.clamp_sum([1, 2, 3], 5))
	note("sum=%d" % CovFixtureHelper.clamp_sum([-4], 5))
	note("loop=%d" % loops(4))
	note("match=%s|%s|%s" % [pick(1), pick(7), pick("x")])
	note("lambda=%s" % str(lambdas([1, 2, 3])))
	note("cond=%s" % str(conditions([], {"a": 1}, null)))
	hp = 150
	note("hp=%d" % hp)
	note("inner=%s" % Inner.greet("x"))
	note("static=%d" % twice(21)); note("semi")
	print("\\n".join(log_lines))
	get_tree().quit()


func note(s: String) -> void: log_lines.append(s)


func loops(n: int) -> int:
	var acc := 0
	for i in range(n):
		var sq := i * i
		acc += sq
	for i in n:
		var t := i + 1
		acc += t
	for j in range(1, n, 2):
		acc -= j
	for k: int in [10, 20]:
		acc += k
	var m := n
	while (m
			> 0):
		m -= 1
		if m == 1:
			break
		else:
			continue
	@warning_ignore("integer_division")
	var half := acc / 2
	var cont := 1 + \\
		2
	return half + cont


func pick(v: Variant) -> String:
	match v:
		1: return "one"
		var big when big is int and big > 5:
			return "big"
		_:
			return "other"


func lambdas(xs: Array) -> Array:
	var doubled := xs.map(func(x): return x * 2)
	var filt := func(x: int) -> bool:
		if x > 2:
			return true
		return false
	var kept := doubled.filter(filt)
	for y in xs.filter(func(q): return q != 2):
		kept.append(y)
	if kept.any(func(q): return q > 5):
		kept.append(-1)
	return kept


func conditions(arr: Array, d: Dictionary, o: Object) -> Array:
	var out := []
	if arr: out.append("arr")
	if not arr and d: out.append("dict")
	if o: out.append("obj")
	elif "a" in d and \\
			d["a"] == 1:
		out.append("in")
	return out


static func twice(x: int) -> int:
	return x * 2


func never_called() -> void:
	pass


class Inner:
	static func greet(who: String) -> String:
		var s := "hi " + who
		return s
'''


def _line_of(src: str, needle: str) -> int:
    for i, text in enumerate(src.splitlines(), 1):
        if needle in text:
            return i
    raise AssertionError(needle)


class InstrumentSyntaxTest(unittest.TestCase):
    def setUp(self) -> None:
        self.res = instrument.instrument(MAIN, 100)
        self.out = self.res.source

    def test_line_count_preserved_and_reparses(self) -> None:
        for src in (MAIN, HELPER):
            res = instrument.instrument(src)
            self.assertEqual(src.count("\n"), res.source.count("\n"))
            parser.parse(res.source)  # raises on a syntax error

    def test_probe_ids_are_consecutive_from_first_id(self) -> None:
        ids = [p.id for p in self.res.probes]
        self.assertEqual(ids, list(range(100, 100 + len(ids))))
        self.assertEqual(sorted({int(i) for i in re.findall(r"HymnCov\.[ht]\((\d+)\)", self.out)}), ids)

    def test_simple_statements_prefixed_same_line(self) -> None:
        self.assertIn("\tHymnCov.h(", self.out.splitlines()[_line_of(MAIN, "var acc := 0") - 1])
        semi = self.out.splitlines()[_line_of(MAIN, 'note("semi")') - 1]
        self.assertEqual(semi.count("HymnCov.h("), 2, semi)

    def test_inline_suites(self) -> None:
        line = self.out.splitlines()[_line_of(MAIN, "func note(") - 1]
        self.assertRegex(line, r"^func note\(s: String\) -> void: HymnCov\.h\(\d+\); log_lines\.append\(s\)$")
        line = self.out.splitlines()[_line_of(MAIN, '1: return "one"') - 1]
        self.assertRegex(line, r'^\t\t1: HymnCov\.h\(\d+\); return "one"$')

    def test_conditions_wrapped(self) -> None:
        lines = self.out.splitlines()
        self.assertRegex(lines[_line_of(MAIN, "if arr:") - 1], r"if HymnCov\.t\(\d+\) and \(arr\): HymnCov\.h")
        self.assertRegex(lines[_line_of(MAIN, 'elif "a" in d') - 1], r'elif HymnCov\.t\(\d+\) and \("a" in d and \\$')
        self.assertRegex(lines[_line_of(MAIN, "while (m") - 1], r"while HymnCov\.t\(\d+\) and \(\(m$")
        self.assertNotIn("HymnCov", lines[_line_of(MAIN, "\t\telse:") - 1])

    def test_for_iterables_keep_type(self) -> None:
        lines = self.out.splitlines()
        self.assertRegex(
            lines[_line_of(MAIN, "for i in range(n):") - 1], r"range\(\(n if HymnCov\.t\(\d+\) else n\)\)")
        self.assertRegex(lines[_line_of(MAIN, "for i in n:") - 1], r"for i in \(n if HymnCov\.t\(\d+\) else n\):")
        self.assertRegex(
            lines[_line_of(MAIN, "range(1, n, 2)") - 1], r"range\(\(1 if HymnCov\.t\(\d+\) else 1\), n, 2\)")
        self.assertRegex(lines[_line_of(MAIN, "for k: int in") - 1], r"for k: int in \(\[10, 20\] if HymnCov")

    def test_match_subject_and_guard(self) -> None:
        lines = self.out.splitlines()
        self.assertRegex(lines[_line_of(MAIN, "match v:") - 1], r"match \(v if HymnCov\.t\(\d+\) else v\):")
        self.assertNotIn("HymnCov", lines[_line_of(MAIN, "var big when") - 1])
        self.assertNotIn("HymnCov", lines[_line_of(MAIN, "\t\t_:") - 1])

    def test_lambdas_instrumented_and_attributed_to_parent(self) -> None:
        lines = self.out.splitlines()
        self.assertRegex(
            lines[_line_of(MAIN, "xs.map(") - 1], r"xs\.map\(func\(x\): HymnCov\.h\(\d+\); return x \* 2\)")
        ln = _line_of(MAIN, "\t\t\treturn true")
        self.assertIn("HymnCov.h(", lines[ln - 1])
        self.assertEqual({p.func for p in self.res.probes if p.line == ln}, {"lambdas"})
        # A lambda inside a for iterable is duplicated with its probe (same id in both copies).
        line = lines[_line_of(MAIN, "for y in xs.filter") - 1]
        self.assertEqual(len(set(re.findall(r"HymnCov\.h\((\d+)\)", line))), 1, line)
        self.assertEqual(len(re.findall(r"HymnCov\.h\((\d+)\)", line)), 2, line)

    def test_annotation_and_continuation(self) -> None:
        lines = self.out.splitlines()
        self.assertEqual(lines[_line_of(MAIN, "@warning_ignore") - 1], '\t@warning_ignore("integer_division")')
        self.assertTrue(lines[_line_of(MAIN, "var cont") - 1].startswith("\tHymnCov.h("))
        self.assertEqual(lines[_line_of(MAIN, "var cont") ], "\t\t2")

    def test_function_names(self) -> None:
        self.assertEqual(
            set(self.res.functions),
            {"_ready", "note", "loops", "pick", "lambdas", "conditions", "twice", "never_called", "Inner.greet",
             "hp.set", "hp.get"},
        )
        setter_line = _line_of(MAIN, "hp = clampi")
        self.assertEqual({p.func for p in self.res.probes if p.line == setter_line}, {"hp.set"})

    def test_class_level_code_not_instrumented(self) -> None:
        self.assertEqual(self.out.splitlines()[:4], MAIN.splitlines()[:4])
        res = instrument.instrument(HELPER)
        self.assertTrue(res.source.startswith("@tool\nclass_name CovFixtureHelper\n"))
        self.assertEqual(set(res.functions), {"clamp_sum"})

    def test_executable_lines(self) -> None:
        lines = {p.line for p in self.res.probes}
        self.assertIn(_line_of(MAIN, "match v:"), lines)
        self.assertIn(_line_of(MAIN, 'elif "a" in d'), lines)
        self.assertNotIn(_line_of(MAIN, "\t\t\td[\"a\"] == 1:"), lines)  # continuation, not a new statement
        self.assertNotIn(_line_of(MAIN, "func loops"), lines)
        self.assertNotIn(_line_of(MAIN, "\t\telse:"), lines)


class GateTest(unittest.TestCase):
    def _report(self, battle: float, files: dict) -> dict:
        return {
            "directories": {"game/battle": {"pct": battle}, "game/progression": {"pct": 90.0}},
            "files": files,
        }

    def setUp(self) -> None:
        self.base = {
            "tolerance_pp": 0.5,
            "directories": {"game/battle": 80.0, "game/progression": 90.0},
            "files": {"game/battle/a.gd": 80.0, "game/battle/old.gd": 0.0},
        }
        self.a = {"lines": 10, "covered": 8}

    def test_within_tolerance_passes(self) -> None:
        fails, _ = run_coverage.gate(self._report(79.6, {"game/battle/a.gd": self.a}), self.base)
        self.assertEqual(fails, [])

    def test_drop_beyond_tolerance_fails(self) -> None:
        fails, _ = run_coverage.gate(self._report(79.4, {"game/battle/a.gd": self.a}), self.base)
        self.assertEqual(len(fails), 1)
        self.assertIn("game/battle", fails[0])

    def test_rise_suggests_ratchet(self) -> None:
        fails, notes = run_coverage.gate(self._report(85.0, {"game/battle/a.gd": self.a}), self.base)
        self.assertEqual(fails, [])
        self.assertTrue(any("--update-baseline" in n for n in notes))

    def test_new_file_at_zero_fails(self) -> None:
        files = {"game/battle/a.gd": self.a, "game/battle/new.gd": {"lines": 3, "covered": 0}}
        fails, _ = run_coverage.gate(self._report(80.0, files), self.base)
        self.assertEqual(len(fails), 1)
        self.assertIn("new.gd", fails[0])

    def test_file_dropping_to_zero_fails_but_known_zero_does_not(self) -> None:
        files = {"game/battle/a.gd": {"lines": 10, "covered": 0}, "game/battle/old.gd": {"lines": 2, "covered": 0}}
        fails, _ = run_coverage.gate(self._report(80.0, files), self.base)
        self.assertEqual(len(fails), 1)
        self.assertIn("a.gd", fails[0])

    def test_empty_file_is_ignored(self) -> None:
        files = {"game/battle/a.gd": self.a, "game/battle/consts.gd": {"lines": 0, "covered": 0}}
        self.assertEqual(run_coverage.gate(self._report(80.0, files), self.base)[0], [])


class RunnerHelpersTest(unittest.TestCase):
    def test_add_autoload(self) -> None:
        text = '[application]\nx=1\n\n[autoload]\n\nGame="*res://g.gd"\n'
        out = run_coverage.add_autoload(text, "HymnCovSink", "hymn_coverage/hymn_cov.gd")
        self.assertIn('[autoload]\n\nHymnCovSink="*res://hymn_coverage/hymn_cov.gd"\nGame=', out)
        out = run_coverage.add_autoload("[application]\nx=1\n", "S", "s.gd")
        self.assertTrue(out.endswith('[autoload]\n\nS="*res://s.gd"\n'))

    def test_measured_files_excludes_scene_glue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("game/battle/a.gd", "game/battle/ai/b.gd", "game/battle/scene/ui.gd",
                        "game/battle/scenery.gd", "game/progression/c.gd", "game/core/d.gd"):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("extends Node\n")
            self.assertEqual(
                run_coverage.measured_files(root),
                ["game/battle/a.gd", "game/battle/ai/b.gd", "game/battle/scenery.gd", "game/progression/c.gd"],
            )

    def test_compare_runs(self) -> None:
        a = "  PASS t.gd::one\n  PASS t.gd::two\nTests: 2 run, 0 failed\n"
        self.assertEqual(run_coverage.compare_runs(a, a), [])
        b = "  PASS t.gd::one\n  FAIL t.gd::two\n"
        self.assertEqual(len(run_coverage.compare_runs(a, b)), 1)
        self.assertEqual(len(run_coverage.compare_runs(a, "  PASS t.gd::one\n")), 2)

    def test_baseline_is_consistent(self) -> None:
        base = json.loads(run_coverage.BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(set(base["directories"]), set(run_coverage.MEASURED_DIRS))
        for rel in base["files"]:
            self.assertTrue(any(rel.startswith(d + "/") for d in run_coverage.MEASURED_DIRS), rel)

    @unittest.skipIf(shutil.which("gdlint") is None, "gdlint not installed")
    def test_recorder_is_lint_clean(self) -> None:
        subprocess.run(["gdlint", str(run_coverage.RECORDER_SRC)], cwd=ROOT, check=True, capture_output=True)


GODOT = os.environ.get("GODOT", "godot")


@unittest.skipIf(shutil.which(GODOT) is None, "Godot not on PATH")
class GodotEquivalenceTest(unittest.TestCase):
    """Runs the fixture plain and instrumented: same output, and the expected lines are hit.

    One project holds both variants (the plain helper's class_name is renamed so they can coexist), so
    the slow editor import runs once.
    """

    def _write_variant(self, root: Path, sub: str, instrumented: bool) -> dict:
        d = root / sub
        d.mkdir(parents=True)
        (d / "main.tscn").write_text(
            f'[gd_scene format=3]\n\n[ext_resource type="Script" path="res://{sub}/main.gd" id="1"]\n\n'
            '[node name="Main" type="Node"]\nscript = ExtResource("1")\n'
        )
        probes: dict = {}
        next_id = 0
        for name, src in (("main.gd", MAIN), ("helper.gd", HELPER)):
            if instrumented:
                res = instrument.instrument(src, next_id)
                next_id += len(res.probes)
                probes[name] = res.probes
                src = res.source
            else:
                src = src.replace("CovFixtureHelper", "CovFixturePlainHelper")
            (d / name).write_text(src)
        return probes

    def _run(self, root: Path, scene: str, env: dict) -> str:
        proc = subprocess.run(
            [GODOT, "--headless", "--path", str(root), scene], capture_output=True, text=True, timeout=120, env=env
        )
        self.assertNotRegex(proc.stdout + proc.stderr, r"SCRIPT ERROR|Parse Error", proc.stdout + proc.stderr)
        return "\n".join(ln for ln in proc.stdout.splitlines() if not ln.startswith("Godot Engine"))

    def test_same_output_and_expected_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, hits = Path(tmp) / "proj", Path(tmp) / "hits.json"
            root.mkdir()
            project = 'config_version=5\n\n[application]\n\nconfig/name="cov_fixture"\n'
            (root / "project.godot").write_text(
                run_coverage.add_autoload(project, run_coverage.RECORDER_AUTOLOAD, run_coverage.RECORDER_RES)
            )
            (root / run_coverage.RECORDER_RES).parent.mkdir(parents=True)
            shutil.copyfile(run_coverage.RECORDER_SRC, root / run_coverage.RECORDER_RES)
            self._write_variant(root, "plain", False)
            probes = self._write_variant(root, "inst", True)
            subprocess.run([GODOT, "--headless", "--path", str(root), "--import"], capture_output=True, timeout=180)
            expected = self._run(root, "res://plain/main.tscn", dict(os.environ))
            self.assertIn("loop=", expected)
            got = self._run(root, "res://inst/main.tscn", dict(os.environ, HYMN_COV_OUT=str(hits)))
            self.assertEqual(got, expected)
            hit_ids = set(json.loads(hits.read_text())["hits"])
            hit_lines = {p.line for p in probes["main.gd"] if p.id in hit_ids}
            missed = {p.line for p in probes["main.gd"]} - hit_lines
            self.assertEqual(missed, {_line_of(MAIN, "func never_called") + 1})
            helper_hit = {p.line for p in probes["helper.gd"] if p.id in hit_ids}
            self.assertNotIn(_line_of(HELPER, "else: return total"), helper_hit)
            self.assertIn(_line_of(HELPER, "elif total < 0"), helper_hit)


if __name__ == "__main__":
    unittest.main()
