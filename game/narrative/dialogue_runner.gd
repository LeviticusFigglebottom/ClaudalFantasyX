class_name DialogueRunner
extends RefCounted
## Steps through a compiled dialogue scene (tools/dlgc.py output, ADR 0004). Headless: no Node
## or scene dependencies, so tests drive it directly.
##
##   var runner := DialogueRunner.new()            # flags via the Game autoload
##   runner.load_scene(&"ch02_girl_on_the_beach")
##   runner.start()
##   var step := runner.next()                      # LINE, CUE, OPTIONS or END
##   if step.is_options(): runner.choose(0)
##
## `set` and conditions go through `flags` (a DialogueFlagAccess). Cues are returned by next()
## and also emitted as cue_triggered. Events are emitted as event_triggered and forwarded to
## EventBus.dialogue_event when the autoload exists.
##
## Music waits (`@wait music=<marker>`): the runner returns the CUE step (step.is_music_wait()) and,
## unless that marker was already reported since the last @music cue, enters a waiting state and
## emits music_wait_requested(marker). The sequencer holds the dialogue (no next()) until it calls
## music_marker_reached(marker) as the score passes the marker (or release_wait() on a skip or its
## max= timeout), which emits music_wait_satisfied. Calling next() while still waiting is a
## sequencer bug: it warns, releases the wait, and carries on, so dialogue never hangs.

signal cue_triggered(cue: StringName, args: Array, kwargs: Dictionary)
signal event_triggered(event_name: StringName, args: Array)
signal node_started(node: StringName)
signal finished
signal music_wait_requested(marker: StringName)
signal music_wait_satisfied(marker: StringName)

const FORMAT_VERSION := 1
const COMPILED_DIR := "res://game/data/dialogue/compiled"
## Guards against a scene that loops forever without showing anything (e.g. jump to self).
const MAX_OPS_PER_STEP := 10000

var flags: DialogueFlagAccess
## When true, events are also emitted on the EventBus autoload (if present).
var forward_events_to_bus: bool = true
var scene_id: StringName = &""

var _nodes: Dictionary = {}
var _start_node: StringName = &""
var _node: StringName = &""
var _ops: Array = []
var _pc: int = 0
var _running: bool = false
var _pending: DialogueStep = null
var _pending_targets: Array[int] = []
var _awaiting_marker: StringName = &""
## Markers reported since the last @music cue (a set: marker -> true).
var _reached_markers: Dictionary = {}


func _init(flag_access: DialogueFlagAccess = null) -> void:
	flags = flag_access if flag_access != null else GameFlagAccess.new()


static func scene_path(id: StringName) -> String:
	return "%s/%s.json" % [COMPILED_DIR, id]


func load_scene(id: StringName) -> bool:
	return load_file(scene_path(id))


func load_file(path: String) -> bool:
	if not FileAccess.file_exists(path):
		push_error("DialogueRunner: no compiled scene at %s (run tools/dlgc.py)" % path)
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("DialogueRunner: %s is not valid JSON" % path)
		return false
	return load_data(parsed as Dictionary)


func load_data(data: Dictionary) -> bool:
	if int(data.get("format", 0)) != FORMAT_VERSION:
		push_error("DialogueRunner: unsupported format %s (want %d)" % [str(data.get("format")), FORMAT_VERSION])
		return false
	var nodes: Variant = data.get("nodes")
	if typeof(nodes) != TYPE_DICTIONARY or (nodes as Dictionary).is_empty():
		push_error("DialogueRunner: scene has no nodes")
		return false
	_nodes = nodes as Dictionary
	scene_id = StringName(str(data.get("scene", "")))
	_start_node = StringName(str(data.get("start", "")))
	_running = false
	_pending = null
	return true


func has_dialogue_node(node: StringName) -> bool:
	return _nodes.has(String(node))


## Begins at `node`, or at the scene's first node.
func start(node: StringName = &"") -> bool:
	var target := node if node != &"" else _start_node
	if not has_dialogue_node(target):
		push_error("DialogueRunner: unknown node '%s' in scene '%s'" % [target, scene_id])
		return false
	_running = true
	_pending = null
	_awaiting_marker = &""
	_reached_markers.clear()
	_enter(target)
	return true


func is_running() -> bool:
	return _running


func is_waiting_for_choice() -> bool:
	return _pending != null


func current_node() -> StringName:
	return _node


## A node's headers (`location:`, `grade:`; the current node's when `node` is empty). M2-FP-120.
func headers(node: StringName = &"") -> Dictionary:
	var n := String(node if node != &"" else _node)
	return (_nodes.get(n, {}) as Dictionary).get("headers", {})


## Advances to the next thing the player sees: a line, a cue, options, or the end.
## While options are pending, returns them again until choose() is called.
func next() -> DialogueStep:
	if _pending != null:
		push_error("DialogueRunner: options are pending; call choose() first")
		return _pending
	if not _running:
		return DialogueStep.make_end()
	if _awaiting_marker != &"":
		push_warning("DialogueRunner: next() before music marker '%s' was reached; continuing" % _awaiting_marker)
		release_wait()
	for _i in MAX_OPS_PER_STEP:
		if _pc >= _ops.size():
			return _finish()
		var op: Dictionary = _ops[_pc]
		_pc += 1
		var step := _exec(op)
		if step != null:
			return step
	push_error("DialogueRunner: no visible step after %d ops in '%s' (infinite loop?)" % [MAX_OPS_PER_STEP, _node])
	return _finish()


## Picks option `index` (DialogueOption.index) from the pending OPTIONS step.
func choose(index: int) -> bool:
	if _pending == null:
		push_error("DialogueRunner: choose() called with no options pending")
		return false
	if index < 0 or index >= _pending_targets.size():
		push_error("DialogueRunner: option %d out of range (0..%d)" % [index, _pending_targets.size() - 1])
		return false
	_pc = _pending_targets[index]
	_pending = null
	_pending_targets.clear()
	return true


func is_waiting_for_marker() -> bool:
	return _awaiting_marker != &""


## The marker the current `@wait music=` holds for; empty when not waiting.
func waiting_marker() -> StringName:
	return _awaiting_marker


## The sequencer reports each music marker as the score passes it. Returns true if this released
## the current wait. A marker reported early still counts for a later wait, until the next @music.
func music_marker_reached(marker: StringName) -> bool:
	_reached_markers[marker] = true
	if _awaiting_marker == &"" or marker != _awaiting_marker:
		return false
	release_wait()
	return true


## Ends the current music wait without its marker (player skip, or the cue's max= timeout).
func release_wait() -> bool:
	if _awaiting_marker == &"":
		return false
	var marker := _awaiting_marker
	_awaiting_marker = &""
	music_wait_satisfied.emit(marker)
	return true


## Evaluates a compiled condition (prefix array from dlgc) against `flags`.
func evaluate(expr: Array) -> Variant:
	var op := str(expr[0])
	match op:
		"lit":
			return expr[1]
		"flag":
			return flags.get_flag(StringName(str(expr[1])))
		"not":
			return not truthy(evaluate(expr[1]))
		"and":
			return truthy(evaluate(expr[1])) and truthy(evaluate(expr[2]))
		"or":
			return truthy(evaluate(expr[1])) or truthy(evaluate(expr[2]))
	return compare(op, evaluate(expr[1]), evaluate(expr[2]))


static func truthy(v: Variant) -> bool:
	match typeof(v):
		TYPE_NIL:
			return false
		TYPE_BOOL:
			return v
		TYPE_INT, TYPE_FLOAT:
			return v != 0
		TYPE_STRING, TYPE_STRING_NAME:
			return not str(v).is_empty()
	return true


## Numbers and bools compare numerically (an unset flag reads as false = 0). Strings compare
## with strings. Mismatched types are never equal, and ordering them is false.
static func compare(op: String, left: Variant, right: Variant) -> bool:
	var l: Variant = left
	var r: Variant = right
	if _is_numeric(l) and _is_numeric(r):
		l = _as_float(l)
		r = _as_float(r)
	elif typeof(l) != typeof(r) and not (_is_text(l) and _is_text(r)):
		if op != "==" and op != "!=":
			push_warning("DialogueRunner: comparing %s %s %s across types is always false" % [l, op, r])
		return op == "!="
	elif _is_text(l):
		l = str(l)
		r = str(r)
	var result := false
	match op:
		"==":
			result = l == r
		"!=":
			result = l != r
		"<":
			result = l < r
		">":
			result = l > r
		"<=":
			result = l <= r
		">=":
			result = l >= r
		_:
			push_error("DialogueRunner: unknown operator '%s'" % op)
	return result


func _exec(op: Dictionary) -> DialogueStep:
	match str(op.get("op", "")):
		"line":
			return DialogueStep.from_line_op(op)
		"cue":
			var step := DialogueStep.from_cue_op(op)
			if step.cue == &"music":
				_reached_markers.clear()
			cue_triggered.emit(step.cue, step.args, step.kwargs)
			if step.is_music_wait() and not _reached_markers.has(step.wait_marker):
				_awaiting_marker = step.wait_marker
				music_wait_requested.emit(step.wait_marker)
			return step
		"options":
			return _offer(op)
		"stop":
			return _finish()
		_:
			_exec_flow(op)
	return null


func _exec_flow(op: Dictionary) -> void:
	match str(op.get("op", "")):
		"set":
			flags.set_flag(StringName(str(op["flag"])), evaluate(op["value"] as Array))
		"if_not":
			if not truthy(evaluate(op["cond"] as Array)):
				_pc = int(op["to"])
		"goto":
			_pc = int(op["to"])
		"jump":
			var target := StringName(str(op["node"]))
			if has_dialogue_node(target):
				_enter(target)
			else:
				push_error("DialogueRunner: jump to unknown node '%s'" % target)
				_pc = _ops.size()
		"event":
			_emit_event(StringName(str(op["name"])), (op.get("args", []) as Array).duplicate(true))
		var unknown:
			push_error("DialogueRunner: unknown op '%s'" % unknown)


## Builds the OPTIONS step from the choices whose conditions hold. With none available,
## continues after the option block and returns null.
func _offer(op: Dictionary) -> DialogueStep:
	var available: Array[DialogueOption] = []
	_pending_targets.clear()
	for choice: Dictionary in op.get("choices", []):
		if choice.has("cond") and not truthy(evaluate(choice["cond"] as Array)):
			continue
		available.append(DialogueOption.from_choice(choice, available.size()))
		_pending_targets.append(int(choice["to"]))
	if available.is_empty():
		_pc = int(op.get("next", _ops.size()))
		return null
	_pending = DialogueStep.from_options(int(op.get("src", 0)), available)
	return _pending


func _enter(node: StringName) -> void:
	_node = node
	_ops = (_nodes[String(node)] as Dictionary).get("ops", [])
	_pc = 0
	node_started.emit(node)


func _finish() -> DialogueStep:
	var was_running := _running
	_running = false
	_pc = _ops.size()
	if was_running:
		finished.emit()
	return DialogueStep.make_end()


func _emit_event(event_name: StringName, args: Array) -> void:
	event_triggered.emit(event_name, args)
	if not forward_events_to_bus:
		return
	var tree := Engine.get_main_loop() as SceneTree
	var bus := tree.root.get_node_or_null(^"EventBus") if tree != null else null
	if bus != null:
		bus.emit_signal(&"dialogue_event", event_name, args)


static func _is_numeric(v: Variant) -> bool:
	return typeof(v) in [TYPE_BOOL, TYPE_INT, TYPE_FLOAT]


static func _is_text(v: Variant) -> bool:
	return typeof(v) in [TYPE_STRING, TYPE_STRING_NAME]


static func _as_float(v: Variant) -> float:
	if typeof(v) == TYPE_BOOL:
		return 1.0 if v else 0.0
	return float(v)
