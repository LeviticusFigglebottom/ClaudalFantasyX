class_name TestErrorCounter
extends Logger
## Counts script runtime errors (null access, bad casts...) so a test that crashes half-way
## is reported as FAIL instead of silently passing. push_error() from game code is NOT
## counted: tests deliberately exercise error paths.

var script_errors := 0
var last_message := ""
var _mutex := Mutex.new()


func _log_error(
	function: String,
	file: String,
	line: int,
	code: String,
	rationale: String,
	_editor_notify: bool,
	error_type: int,
	_script_backtraces: Array[ScriptBacktrace]
) -> void:
	if error_type != Logger.ERROR_TYPE_SCRIPT:
		return
	_mutex.lock()
	script_errors += 1
	last_message = "%s:%d in %s(): %s %s" % [file, line, function, code, rationale]
	_mutex.unlock()


func take() -> int:
	_mutex.lock()
	var n := script_errors
	script_errors = 0
	_mutex.unlock()
	return n
