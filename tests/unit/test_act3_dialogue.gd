extends TestCase
## Act III scripts (the story track, M5-A3P-1000..; ADR 0207): every compiled scene of Ch17 onward and the Ending
## runs through DialogueRunner down every option path, with every flag unset and with every flag set, under the
## same bar as Act II (test_act2_dialogue.gd): each path reaches END with no runner errors or warnings and the
## letterbox off; every spoken line has a known speaker, an emotion and a translated key; narration is tagged
## #vo; options are a real choice; released light rises and bound light is still. The act's own rules (no
## Dace voice in Ch17, no "revenant" before Ch19, where light may rise) are checked statically by
## tools/tests/test_act3_rules.py.

const COMPILED_DIR := "res://game/data/dialogue/compiled/"
const ACT3_PREFIX_RE := "^(ch1[7-9]|ch2[0-9]|ending)_"
## Far more steps than any scene has; a path that needs more is looping.
const MAX_STEPS := 800

var speakers: DialogueSpeakers
var tally: _ErrorTally


func before_each() -> void:
	speakers = DialogueSpeakers.load_default()
	tally = _ErrorTally.new()


func test_every_act3_scene_runs_every_path() -> void:
	var scenes := _act3_scenes()
	assert_true(scenes.size() > 0, "there are Act III scenes to run")
	for scene in scenes:
		var flags := _flags_read(scene)
		for all_set: bool in [false, true]:
			var preset := {}
			for f: String in flags:
				preset[f] = all_set
			_all_paths(scene, preset)


## The compiled Act III scenes, by file name.
func _act3_scenes() -> Array[StringName]:
	var out: Array[StringName] = []
	var re := RegEx.create_from_string(ACT3_PREFIX_RE)
	for f in DirAccess.get_files_at(COMPILED_DIR):
		if f.ends_with(".json") and re.search(f) != null:
			out.append(StringName(f.get_basename()))
	out.sort()
	return out


## Every flag the scene's conditions read (from the compiled JSON's expressions).
func _flags_read(scene: StringName) -> Array[String]:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(COMPILED_DIR + scene + ".json"))
	var out: Array[String] = []
	_collect_flags(data, out)
	return out


func _collect_flags(v: Variant, out: Array[String]) -> void:
	if v is Array:
		var a: Array = v
		if a.size() == 2 and a[0] is String and a[0] == "flag" and a[1] is String:
			if not (a[1] as String) in out:
				out.append(a[1])
			return
		for x: Variant in a:
			_collect_flags(x, out)
	elif v is Dictionary:
		for k: Variant in v as Dictionary:
			_collect_flags((v as Dictionary)[k], out)


func _all_paths(scene: StringName, preset: Dictionary) -> void:
	var todo: Array = [[] as Array[int]]
	while not todo.is_empty():
		var prefix: Array[int] = todo.pop_back()
		var run := _run(scene, preset, prefix)
		var taken: Array[int] = run["choices"]
		var sizes: Array[int] = run["sizes"]
		for depth in range(prefix.size(), sizes.size()):
			for alt in range(1, sizes[depth]):
				var branch: Array[int] = taken.slice(0, depth)
				branch.append(alt)
				todo.append(branch)


func _run(scene: StringName, preset: Dictionary, prefix: Array[int]) -> Dictionary:
	var flags := DialogueFlagAccess.new()
	for k: String in preset:
		flags.set_flag(StringName(k), preset[k])
	var runner := DialogueRunner.new(flags)
	runner.forward_events_to_bus = false
	var where := "%s %s %s" % [scene, preset, prefix]
	OS.add_logger(tally)
	tally.take()
	assert_true(runner.load_scene(scene), "loads " + where)
	assert_true(runner.start(), "starts " + where)
	var choices: Array[int] = []
	var sizes: Array[int] = []
	var letterbox := false
	var ended := false
	for _i in MAX_STEPS:
		var step := runner.next()
		if step.is_end():
			ended = true
			break
		if step.is_cue():
			if step.is_music_wait():
				runner.release_wait()
			if step.cue == &"letterbox":
				letterbox = str(step.args[0]) == "on"
			elif step.cue == &"vfx":
				_check_glimmer(step, where)
		elif step.is_line():
			_check_line(step, where)
		elif step.is_options():
			assert_true(step.options.size() >= 2, "a menu offers a real choice: " + where)
			for o in step.options:
				assert_ne(tr(o.text_key), String(o.text_key), "option translated: %s (%s)" % [o.line_id, where])
			var pick := prefix[choices.size()] if choices.size() < prefix.size() else 0
			sizes.append(step.options.size())
			choices.append(pick)
			assert_true(runner.choose(pick), "choose %d %s" % [pick, where])
	var problems := tally.take()
	OS.remove_logger(tally)
	assert_true(ended, "reaches END within %d steps: %s" % [MAX_STEPS, where])
	assert_eq(problems, 0, "runner errors or warnings (%s): %s" % [tally.last_message, where])
	assert_false(letterbox, "letterbox is off again at the end: " + where)
	return {"choices": choices, "sizes": sizes}


func _check_line(step: DialogueStep, where: String) -> void:
	var at := "%s (%s)" % [step.line_id, where]
	assert_ne(tr(step.text_key), String(step.text_key), "translated: " + at)
	if step.speaker == &"":
		if step.narrator != &"":
			assert_true("vo" in step.tags, "voice-over narration is tagged #vo: " + at)
	else:
		assert_true(speakers.has(step.speaker), "known speaker: " + at)
		assert_ne(step.emotion, &"", "spoken line has an emotion: " + at)


## Released light rises; bound light is still; held light carries no motion (as in Act II).
func _check_glimmer(step: DialogueStep, where: String) -> void:
	var at := "@vfx %s %s (%s)" % [step.args, step.kwargs, where]
	match str(step.args[0]):
		"glimmer_lift":
			assert_eq(step.kwargs.get("motion"), "spiral_up", "released light rises: " + at)
		"glimmer_held":
			assert_false(step.kwargs.has("motion"), "held light never rises: " + at)
		"glimmer_bound":
			assert_false(step.kwargs.has("motion") or step.kwargs.has("drift"), "bound light is still: " + at)


class _ErrorTally:
	extends Logger
	var count := 0
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
		if error_type == Logger.ERROR_TYPE_SCRIPT or error_type == Logger.ERROR_TYPE_SHADER:
			return
		_mutex.lock()
		count += 1
		last_message = "%s:%d in %s(): %s %s" % [file, line, function, code, rationale]
		_mutex.unlock()

	func take() -> int:
		_mutex.lock()
		var n := count
		count = 0
		_mutex.unlock()
		return n
