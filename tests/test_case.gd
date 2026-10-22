class_name TestCase
extends RefCounted
## Minimal test base (ADR 0006). Methods named test_* are run by tests/run_tests.gd.
## Each assertion failure is recorded with a message; a test passes if it records none.

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
