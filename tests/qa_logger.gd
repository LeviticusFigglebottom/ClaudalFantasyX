class_name QaLogger
extends Logger
## Integration QA (M3-HER-1121): records every engine error, script error and warning the game raises while a test
## drives it, so a playthrough guard can fail on anything a track left behind, not only on script errors (the suite's
## TestErrorCounter counts those alone). Thread-safe; take() returns the entries since the last take and clears them.

const KIND_ERROR := &"error"
const KIND_SCRIPT := &"script"
const KIND_WARNING := &"warning"

var _entries: Array[Dictionary] = []
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
	var kind := KIND_ERROR
	if error_type == Logger.ERROR_TYPE_SCRIPT:
		kind = KIND_SCRIPT
	elif error_type == Logger.ERROR_TYPE_WARNING:
		kind = KIND_WARNING
	var text := rationale if rationale != "" else code
	_mutex.lock()
	_entries.append({"kind": kind, "text": text, "where": "%s:%d %s()" % [file.get_file(), line, function]})
	_mutex.unlock()


func take() -> Array[Dictionary]:
	_mutex.lock()
	var out := _entries.duplicate()
	_entries.clear()
	_mutex.unlock()
	return out
