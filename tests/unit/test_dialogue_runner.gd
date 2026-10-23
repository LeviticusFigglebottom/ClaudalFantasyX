extends TestCase
## DialogueRunner against real dlgc output: game/data/dialogue/test/test_dialogue_fixture.dlg
## (compiled to compiled/test_dialogue_fixture.json) and the ch02 sample scene.

const FIXTURE := &"test_dialogue_fixture"
const BEACH := &"ch02_girl_on_the_beach"

var flags: DialogueFlagAccess
var runner: DialogueRunner


func before_each() -> void:
	flags = DialogueFlagAccess.new()
	runner = DialogueRunner.new(flags)
	runner.forward_events_to_bus = false


func _start(scene: StringName) -> void:
	assert_true(runner.load_scene(scene), "loads %s" % scene)
	assert_true(runner.start(), "starts %s" % scene)


## Steps until the next LINE / OPTIONS / END, skipping cues.
func _next_visible() -> DialogueStep:
	var step := runner.next()
	while step.is_cue():
		step = runner.next()
	return step


func _expect_line(line_id: String, msg: String = "") -> DialogueStep:
	var step := _next_visible()
	assert_true(step.is_line(), "expected a line %s %s" % [line_id, msg])
	assert_eq(step.line_id, StringName(line_id), msg)
	return step


## Steps until an OPTIONS step and returns it.
func _to_menu() -> DialogueStep:
	var step := _next_visible()
	while not step.is_options() and not step.is_end():
		step = _next_visible()
	assert_true(step.is_options(), "reached an options menu")
	return step


func _option_ids(step: DialogueStep) -> Array[String]:
	var out: Array[String] = []
	for o in step.options:
		out.append(String(o.line_id))
	return out


func test_lines_carry_keys_speaker_emotion_and_tags() -> void:
	_start(FIXTURE)
	var cue := runner.next()
	assert_true(cue.is_cue(), "first step is the camera cue")
	var narration := runner.next()
	assert_true(narration.is_line())
	assert_eq(narration.text_key, &"DLG_TEST_DLG_001")
	assert_eq(narration.speaker, &"", "narration has no speaker")
	var line := runner.next()
	assert_eq(line.speaker, &"rhen")
	assert_eq(line.emotion, &"worried")
	assert_eq(line.voice, "")
	assert_eq(line.tags, PackedStringArray(["tagged"]))
	assert_eq(line.src_line, 7)


func test_cue_is_returned_and_emitted() -> void:
	var seen: Array = []
	runner.cue_triggered.connect(func(c: StringName, a: Array, k: Dictionary) -> void: seen.append([c, a, k]))
	_start(FIXTURE)
	var step := runner.next()
	assert_eq(step.cue, &"camera")
	assert_eq(step.args, ["fixture_wide"])
	assert_eq(step.kwargs, {"blend": 1.5, "grade": "ch02"})
	assert_eq(seen.size(), 1)
	assert_eq(seen[0][0], &"camera")


func test_else_branch_when_no_flags() -> void:
	_start(FIXTURE)
	_expect_line("test_dlg_001")
	_expect_line("test_dlg_002")
	_expect_line("test_dlg_005", "neither flag nor counter")


func test_if_branch_when_flag_set() -> void:
	flags.set_flag(&"test_flag", true)
	_start(FIXTURE)
	_expect_line("test_dlg_001")
	_expect_line("test_dlg_002")
	_expect_line("test_dlg_003")


func test_elseif_with_comparison_and_not() -> void:
	flags.set_flag(&"test_counter", 3)
	_start(FIXTURE)
	_expect_line("test_dlg_001")
	_expect_line("test_dlg_002")
	_expect_line("test_dlg_004")


func test_set_and_event_before_options() -> void:
	var events: Array = []
	runner.event_triggered.connect(func(n: StringName, a: Array) -> void: events.append([n, a]))
	_start(FIXTURE)
	var menu := _to_menu()
	assert_true(menu.is_options())
	assert_eq(flags.get_flag(&"test_counter"), 7.0, "set applied before the menu")
	assert_eq(events.size(), 1)
	assert_eq(events[0][0], &"fixture_event")
	assert_eq(events[0][1], ["alpha", 2.0, true])


func test_option_conditions_filter_choices() -> void:
	_start(FIXTURE)
	var menu := _to_menu()
	assert_eq(_option_ids(menu), ["test_dlg_006", "test_dlg_010"] as Array[String])
	assert_eq(menu.options[1].index, 1)
	assert_eq(menu.options[1].text_key, &"DLG_TEST_DLG_010")


func test_nested_options_and_set_string() -> void:
	_start(FIXTURE)
	_to_menu()
	assert_true(runner.choose(0))
	_expect_line("test_dlg_007")
	var inner := _next_visible()
	assert_eq(_option_ids(inner), ["test_dlg_008", "test_dlg_009"] as Array[String])
	assert_true(runner.choose(0))
	_expect_line("test_dlg_012", "continues after both option blocks")
	assert_eq(flags.get_flag(&"test_text"), "nested")


func test_second_nested_option_skips_its_sibling_body() -> void:
	_start(FIXTURE)
	_to_menu()
	runner.choose(0)
	_next_visible()
	_next_visible()
	runner.choose(1)
	_expect_line("test_dlg_012")
	assert_eq(flags.get_flag(&"test_text"), false, "Nested A's set did not run")


func test_stop_ends_dialogue() -> void:
	var done: Array[int] = [0]
	runner.finished.connect(func() -> void: done[0] += 1)
	_start(FIXTURE)
	_to_menu()
	runner.choose(0)
	_next_visible()
	_next_visible()
	runner.choose(1)
	_expect_line("test_dlg_012")
	assert_true(runner.next().is_end(), "<<stop>> skips the unreachable line")
	assert_false(runner.is_running())
	assert_true(runner.next().is_end(), "stays ended")
	assert_eq(done[0], 1, "finished emitted once")


func test_jump_to_other_node() -> void:
	var nodes: Array[StringName] = []
	runner.node_started.connect(func(n: StringName) -> void: nodes.append(n))
	_start(FIXTURE)
	_to_menu()
	assert_true(runner.choose(1))
	var line := _expect_line("test_dlg_015", "or/== condition is false")
	assert_eq(line.emotion, &"smile")
	assert_eq(runner.current_node(), &"second")
	assert_eq(nodes, [&"test_dialogue_fixture", &"second"] as Array[StringName])
	assert_true(runner.next().is_end(), "end of the jumped-to node ends the dialogue")


func test_next_while_choice_pending_repeats_options() -> void:
	_start(FIXTURE)
	var menu := _to_menu()
	assert_true(runner.is_waiting_for_choice())
	assert_eq(runner.next(), menu, "same options step until choose()")
	assert_false(runner.choose(5), "out of range index is rejected")
	assert_true(runner.is_waiting_for_choice())
	assert_false(DialogueRunner.new(flags).choose(0), "choose with nothing pending is rejected")


func test_start_at_named_node() -> void:
	assert_true(runner.load_scene(FIXTURE))
	assert_true(runner.start(&"second"))
	_expect_line("test_dlg_015")
	assert_false(runner.start(&"no_such_node"))


func test_load_rejects_bad_data() -> void:
	assert_false(runner.load_data({"format": 99, "nodes": {"a": {"ops": []}}}))
	assert_false(runner.load_data({"format": 1, "nodes": {}}))
	assert_false(runner.load_scene(&"no_such_scene"))
	assert_true(runner.next().is_end(), "a runner that never started is at the end")


func test_infinite_loop_is_guarded() -> void:
	var data := {"format": 1, "start": "a", "nodes": {"a": {"ops": [{"op": "goto", "to": 0}]}}}
	assert_true(runner.load_data(data))
	runner.start()
	assert_true(runner.next().is_end())


## M1-NAR-04 fixture node `features`: alias, narrator identity, sung/notr, music waits.
func _start_features() -> void:
	assert_true(runner.load_scene(FIXTURE))
	assert_true(runner.start(&"features"))


func test_alias_and_narrator_fields() -> void:
	_start_features()
	var alias := _expect_line("test_dlg_016")
	assert_eq(alias.speaker, &"asha", "an alias keeps the real speaker (pitch, portrait, emotion)")
	assert_eq(alias.name_key, &"DLG_NAME_ASHA_THE_GIRL")
	assert_eq(tr(alias.name_key), "The girl")
	assert_eq(_expect_line("test_dlg_017").name_key, &"", "no alias: the speaker's own name")
	var vo := _expect_line("test_dlg_018")
	assert_eq([vo.speaker, vo.emotion, vo.narrator], [&"", &"tender", &"rhen"])
	var caption := _expect_line("test_dlg_019")
	assert_eq([caption.speaker, caption.emotion, caption.narrator], [&"", &"sad", &""])


func test_sung_and_do_not_translate_tags() -> void:
	_start_features()
	for id in ["016", "017", "018", "019"]:
		_expect_line("test_dlg_" + id)
	var sung := _expect_line("test_dlg_020")
	assert_true(sung.is_sung())
	assert_true(sung.is_do_not_translate())
	assert_false(runner.next().is_sung(), "a cue is never sung")


## Steps from the start of `features` to the first music wait, checking the music cue on the way.
func _to_music_wait() -> DialogueStep:
	_start_features()
	var step := runner.next()
	while not step.is_music_wait():
		assert_false(step.is_end(), "reached a music wait")
		step = runner.next()
	return step


func test_music_wait_holds_until_marker() -> void:
	var asked: Array[StringName] = []
	var done: Array[StringName] = []
	runner.music_wait_requested.connect(func(m: StringName) -> void: asked.append(m))
	runner.music_wait_satisfied.connect(func(m: StringName) -> void: done.append(m))
	var wait := _to_music_wait()
	assert_eq(wait.cue, &"wait")
	assert_eq(wait.wait_marker, &"verse_end")
	assert_eq(wait.kwargs.get("max"), 6.0, "max= is the sequencer's fallback timeout")
	assert_true(runner.is_waiting_for_marker())
	assert_eq(runner.waiting_marker(), &"verse_end")
	assert_eq(asked, [&"verse_end"] as Array[StringName])
	assert_false(runner.music_marker_reached(&"already_passed"), "another marker does not release it")
	assert_true(runner.is_waiting_for_marker())
	assert_true(runner.music_marker_reached(&"verse_end"))
	assert_false(runner.is_waiting_for_marker())
	assert_eq(done, [&"verse_end"] as Array[StringName])
	var second := runner.next()
	assert_eq(second.wait_marker, &"already_passed")
	assert_false(runner.is_waiting_for_marker(), "a marker reported earlier satisfies a later wait")
	assert_eq(asked.size(), 1, "no request for an already-passed marker")
	var silence := runner.next()
	assert_true(silence.is_music_silence())
	assert_eq(silence.kwargs, {"fade": 1.0})
	var sfx := runner.next()
	assert_eq([sfx.cue, sfx.args, sfx.kwargs], [&"sfx", ["fixture_toll"], {"vol": 0.5, "at": "asha"}])
	_expect_line("test_dlg_021")


func test_music_cue_forgets_earlier_markers() -> void:
	_start_features()
	runner.music_marker_reached(&"verse_end")
	var wait := _to_music_wait_after_start()
	assert_eq(wait.wait_marker, &"verse_end")
	assert_true(runner.is_waiting_for_marker(), "the @music cue before the wait cleared earlier markers")
	assert_true(runner.release_wait(), "a skip or timeout releases the wait")
	assert_false(runner.release_wait(), "nothing left to release")


## Like _to_music_wait but without restarting the runner.
func _to_music_wait_after_start() -> DialogueStep:
	var step := runner.next()
	while not step.is_music_wait() and not step.is_end():
		step = runner.next()
	return step


func test_next_during_music_wait_warns_and_continues() -> void:
	var done: Array[StringName] = []
	runner.music_wait_satisfied.connect(func(m: StringName) -> void: done.append(m))
	_to_music_wait()
	var tally := _WarningTally.new()
	OS.add_logger(tally)
	var step := runner.next()
	OS.remove_logger(tally)
	assert_eq(step.wait_marker, &"already_passed", "dialogue carries on instead of hanging")
	assert_eq(tally.count, 1, "the early next() is reported")
	assert_eq(done, [&"verse_end"] as Array[StringName])
	assert_true(runner.is_waiting_for_marker(), "the second wait is a fresh wait")


func test_start_resets_music_wait() -> void:
	_to_music_wait()
	assert_true(runner.start(&"features"))
	assert_false(runner.is_waiting_for_marker())


func test_options_with_none_available_are_skipped() -> void:
	var never := ["lit", false]
	var line_op := {"op": "line", "id": "x", "key": "DLG_X"}
	var menu := {"op": "options", "choices": [{"id": "o", "key": "DLG_O", "to": 1, "cond": never}], "next": 2}
	var ops := [menu, {"op": "goto", "to": 2}, line_op]
	runner.load_data({"format": 1, "start": "a", "nodes": {"a": {"ops": ops}}})
	runner.start()
	assert_eq(runner.next().line_id, &"x")


func test_camera_release_is_a_reserved_command() -> void:
	var release := DialogueStep.from_cue_op({"op": "cue", "cue": "camera", "args": ["release"], "kwargs": {"blend": 2}})
	assert_true(release.is_camera_release())
	assert_false(release.is_music_silence())
	var shot := DialogueStep.from_cue_op({"op": "cue", "cue": "camera", "args": ["H06"], "kwargs": {}})
	assert_false(shot.is_camera_release(), "a shot id is not a release")
	var music := DialogueStep.from_cue_op({"op": "cue", "cue": "music", "args": ["release"], "kwargs": {}})
	assert_false(music.is_camera_release(), "only @camera reserves 'release'")


## Counts push_warning calls.
class _WarningTally:
	extends Logger
	var count := 0

	func _log_error(
		_function: String,
		_file: String,
		_line: int,
		_code: String,
		_rationale: String,
		_editor_notify: bool,
		error_type: int,
		_script_backtraces: Array[ScriptBacktrace]
	) -> void:
		if error_type == Logger.ERROR_TYPE_WARNING:
			count += 1
