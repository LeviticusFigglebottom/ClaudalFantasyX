class_name TestCase
extends RefCounted
## Minimal test base (ADR 0006). Methods named test_* are run by tests/run_tests.gd.
## Each assertion failure is recorded with a message; a test passes if it records none.
## Awaits: the runner runs every test inside its own _ready and steps no frame. An await on a frame, a timer or a
## signal nobody emits during the call never resumes, so the test fails as suspended (runs_to_the_end). An await
## that resumes within the call (an instant CutsceneSequencer's play, a signal emitted inside the call, a coroutine
## that doesn't wait) is fine. Add nodes under the tree's current_scene, not its root (the root is busy then).

const SUSPENDED := "suspended on an await and never resumed: the runner steps no frame, so nothing after it ran"

var failures: Array[String] = []
var _current := ""


func before_each() -> void:
	pass


func begin_test(test_name: String) -> void:
	_current = test_name


func fail(msg: String) -> void:
	failures.append("%s: %s" % [_current, msg])


func assert_true(cond: bool, msg: String = "expected true") -> void:
	if not cond:
		fail(msg)


func assert_false(cond: bool, msg: String = "expected false") -> void:
	if cond:
		fail(msg)


func assert_eq(actual: Variant, expected: Variant, msg: String = "") -> void:
	if typeof(actual) != typeof(expected) or actual != expected:
		fail("expected <%s> got <%s> %s" % [str(expected), str(actual), msg])


func assert_ne(actual: Variant, unexpected: Variant, msg: String = "") -> void:
	if typeof(actual) == typeof(unexpected) and actual == unexpected:
		fail("did not expect <%s> %s" % [str(actual), msg])


func assert_between(actual: float, lo: float, hi: float, msg: String = "") -> void:
	if actual < lo or actual > hi:
		fail("expected %s in [%s, %s] %s" % [str(actual), str(lo), str(hi), msg])


## Calls tc.<mname>() and says whether it returned. A suspended test would otherwise pass with its assertions
## never run (M2-QA-100).
static func runs_to_the_end(tc: TestCase, mname: String) -> bool:
	var state := {"done": false}
	var run := func() -> void:
		await tc.call(mname)
		state["done"] = true
	run.call()
	return state["done"]
