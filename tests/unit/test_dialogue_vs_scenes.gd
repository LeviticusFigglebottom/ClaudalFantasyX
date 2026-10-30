extends TestCase
## M1-NAR-02: the two vertical-slice cutscenes run through DialogueRunner down every branch.
## Each scene is explored depth-first over every option menu, under every combination of the
## upstream flags it reads (set by earlier scenes, the side scene, or gameplay). Every path must
## reach END with no runner errors or warnings; every spoken line needs a known speaker, an
## emotion, and a translated key; narration is tagged #vo; cameras use haluna.md shot ids; and
## glimmer VFX obey the light rules (released rises, held sinks, bound stays still).
## M1-NAR-05 staging: Asha's closing line stays on H05 and the walk is on H01; Rhen's recognition
## cuts to S10 on the second sung line and holds there through his question.

const BEACH := &"ch02_girl_on_the_beach"
const VERSE := &"ch03_the_first_verse"
## Far more steps than either scene has; a path that needs more is looping.
const MAX_STEPS := 600
## Flags the First Verse reads but does not set.
const VERSE_INPUTS: Array[StringName] = [
	&"ch02_rhen_named_lantern", &"ch02_rhen_stayed_with_dead", &"ch02_heard_pila", &"ch03_found_net_float"
]
## Shot ids from docs/kb/art/environments/haluna.md §5 (H Haluna, C causeway, S shrine).
## A haluna.md id, or a stage variant of one (H05_up: H05 at standing height).
const SHOT_ID_PATTERN := "^[HCS](0[1-9]|10)(_[a-z]+)?$"
## M1-NAR-05 (decisions_log N-13): Rhen's recognition on S10 holds at least this long in @wait time.
const S10_HOLD_SEC := 6.0

var speakers: DialogueSpeakers
var shot_re: RegEx
var tally: _ErrorTally


func before_each() -> void:
	speakers = DialogueSpeakers.load_default()
	shot_re = RegEx.create_from_string(SHOT_ID_PATTERN)
	tally = _ErrorTally.new()


## Runs `scene` once with `preset` flags, taking `prefix` choices and then option 0 at every
## later menu. Returns the choices taken, each menu's size, the lines seen, events, and flags.
func _run(scene: StringName, preset: Dictionary, prefix: Array[int]) -> Dictionary:
	var flags := DialogueFlagAccess.new()
	for k: String in preset:
		flags.set_flag(StringName(k), preset[k])
	var runner := DialogueRunner.new(flags)
	runner.forward_events_to_bus = false
	var events: Array = []
	runner.event_triggered.connect(func(n: StringName, a: Array) -> void: events.append([n, a]))
	var where := "%s %s %s" % [scene, preset, prefix]
	OS.add_logger(tally)
	tally.take()
	assert_true(runner.load_scene(scene), "loads " + where)
	assert_true(runner.start(), "starts " + where)
	var choices: Array[int] = []
	var sizes: Array[int] = []
	var lines: Array[StringName] = []
	## One entry per @camera: {shot, wait (seconds of @wait while on it), lines (ids spoken on it)}.
	var shots: Array[Dictionary] = []
	var letterbox := false
	var ended := false
	for _i in MAX_STEPS:
		var step := runner.next()
		if step.is_end():
			ended = true
			break
		if step.is_cue():
			letterbox = _check_cue(step, letterbox, where)
			if step.cue == &"camera" and not step.is_camera_release():
				shots.append({"shot": str(step.args[0]), "wait": 0.0, "lines": [] as Array[StringName]})
			elif step.cue == &"wait" and not step.args.is_empty() and not shots.is_empty():
				shots[-1]["wait"] = float(shots[-1]["wait"]) + float(step.args[0])
		elif step.is_line():
			_check_line(step, where)
			lines.append(step.line_id)
			if not shots.is_empty():
				(shots[-1]["lines"] as Array[StringName]).append(step.line_id)
		elif step.is_options():
			_check_options(step, where)
			var pick := prefix[choices.size()] if choices.size() < prefix.size() else 0
			sizes.append(step.options.size())
			choices.append(pick)
			assert_true(runner.choose(pick), "choose %d %s" % [pick, where])
	var problems := tally.take()
	OS.remove_logger(tally)
	assert_true(ended, "reaches END within %d steps: %s" % [MAX_STEPS, where])
	assert_eq(problems, 0, "runner errors or warnings (%s): %s" % [tally.last_message, where])
	assert_false(letterbox, "letterbox is off again at the end: " + where)
	return {"choices": choices, "sizes": sizes, "lines": lines, "events": events, "flags": flags.values, "shots": shots}


## Every path through `scene` under `preset`, one result per distinct choice sequence.
func _all_paths(scene: StringName, preset: Dictionary) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var todo: Array = [[] as Array[int]]
	while not todo.is_empty():
		var prefix: Array[int] = todo.pop_back()
		var run := _run(scene, preset, prefix)
		out.append(run)
		var taken: Array[int] = run["choices"]
		var sizes: Array[int] = run["sizes"]
		for depth in range(prefix.size(), sizes.size()):
			for alt in range(1, sizes[depth]):
				var branch: Array[int] = taken.slice(0, depth)
				branch.append(alt)
				todo.append(branch)
	return out


## Every true/false combination of `names`.
func _presets(names: Array[StringName]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for mask in 1 << names.size():
		var p := {}
		for i in names.size():
			p[String(names[i])] = (mask >> i) & 1 == 1
		out.append(p)
	return out


func _check_line(step: DialogueStep, where: String) -> void:
	var at := "%s (%s)" % [step.line_id, where]
	assert_ne(tr(step.text_key), String(step.text_key), "translated: " + at)
	if "lamptongue" in step.tags:
		assert_true(step.is_do_not_translate(), "Lamptongue is never translated (#notr): " + at)
	if step.speaker == &"":
		assert_true("vo" in step.tags, "narration is tagged #vo: " + at)
	else:
		assert_true(speakers.has(step.speaker), "known speaker: " + at)
		assert_ne(step.emotion, &"", "spoken line has an emotion: " + at)


func _check_options(step: DialogueStep, where: String) -> void:
	assert_true(step.options.size() >= 2, "a menu offers a real choice: " + where)
	for o in step.options:
		assert_ne(tr(o.text_key), String(o.text_key), "option translated: %s (%s)" % [o.line_id, where])


## Validates one cue and returns the letterbox state after it.
func _check_cue(step: DialogueStep, letterbox: bool, where: String) -> bool:
	var at := "@%s %s %s (%s)" % [step.cue, step.args, step.kwargs, where]
	match step.cue:
		&"camera":
			if not step.is_camera_release():
				assert_true(shot_re.search(str(step.args[0])) != null, "haluna.md shot id: " + at)
		&"letterbox":
			return str(step.args[0]) == "on"
		&"vfx":
			_check_glimmer(step, at)
	return letterbox


func _check_glimmer(step: DialogueStep, at: String) -> void:
	match str(step.args[0]):
		"glimmer_lift":
			assert_eq(step.kwargs.get("motion"), "spiral_up", "released light rises: " + at)
		"glimmer_held":
			assert_eq(step.kwargs.get("drift"), "down_seaward", "held light sinks: " + at)
		"glimmer_bound":
			assert_false(step.kwargs.has("motion") or step.kwargs.has("drift"), "bound light is still: " + at)


func _has(run: Dictionary, line_id: String) -> bool:
	return StringName(line_id) in (run["lines"] as Array[StringName])


func _flag(run: Dictionary, flag: String) -> Variant:
	return (run["flags"] as Dictionary).get(flag, false)


## The camera setup `line_id` was spoken on (empty if it never played).
func _shot_of(run: Dictionary, line_id: String) -> Dictionary:
	for s: Dictionary in run["shots"]:
		if StringName(line_id) in (s["lines"] as Array[StringName]):
			return s
	return {}


func _check_beach_run(run: Dictionary) -> void:
	var c: Array[int] = run["choices"]
	assert_eq(c.size(), 2, "two menus on the beach: %s" % [c])
	var named := c[0] == 0
	var stayed := c[1] == 0
	assert_eq(_flag(run, "ch02_met_asha"), true)
	assert_eq(_flag(run, "ch02_rhen_named_lantern"), named, "lantern flag %s" % [c])
	assert_eq(_flag(run, "ch02_rhen_stayed_with_dead"), stayed, "stayed flag %s" % [c])
	assert_eq(_has(run, "ch02_beach_014"), named, "lantern closing line %s" % [c])
	assert_eq(_has(run, "ch02_beach_015"), not named, "plain closing line %s" % [c])
	assert_eq(_has(run, "ch02_beach_023"), stayed, "Kell line only when he stays %s" % [c])
	assert_eq(run["events"], [[&"zone_unlock", ["haluna_village"]]], "one zone unlock %s" % [c])
	var lines: Array[StringName] = run["lines"]
	assert_eq(lines[0], &"ch02_beach_001", "opens on the dawn narration")
	assert_eq(lines[-1], &"ch02_beach_035", "closes on the narration")
	var closing := "ch02_beach_014" if named else "ch02_beach_015"
	# H05_up is H05's setup at standing height (they are up by then; PC GPU QA row 32).
	assert_eq(_shot_of(run, closing).get("shot"), "H05_up", "Asha's closing line stays on H05 (standing) %s" % [c])
	assert_eq(_shot_of(run, "ch02_beach_035").get("shot"), "H01", "the walk-up narration is on H01 %s" % [c])


func _check_verse_run(run: Dictionary, preset: Dictionary) -> void:
	var c: Array[int] = run["choices"]
	var at := "%s %s" % [preset, c]
	assert_eq(c.size(), 2, "two menus in the First Verse: " + at)
	var asked := c[0] == 0
	var told := c[1] == 0
	var lantern: bool = preset.get("ch02_rhen_named_lantern", false)
	assert_eq(_flag(run, "ch03_first_verse_sung"), true, at)
	assert_eq(_flag(run, "ch03_ilun_bound"), true, at)
	assert_eq(_flag(run, "ch03_rhen_asked_after"), asked, "asked-after flag " + at)
	assert_eq(_flag(run, "ch03_rhen_named_lullaby"), told, "lullaby flag " + at)
	for k: String in preset:
		assert_eq(_flag(run, k), preset[k], "input flag %s is not rewritten %s" % [k, at])
	assert_eq(_has(run, "ch03_verse_027"), preset.get("ch02_rhen_stayed_with_dead", false), "steps callback " + at)
	assert_eq(_has(run, "ch03_verse_034"), preset.get("ch02_heard_pila", false), "Teyo line " + at)
	assert_eq(_has(run, "ch03_verse_036"), not preset.get("ch02_heard_pila", false), "plain Ilun line " + at)
	assert_eq(_has(run, "ch03_verse_037"), preset.get("ch03_found_net_float", false), "net-float " + at)
	# Review-sweep-G B3 (Lead): Act I never voices the lantern link, so the told path is the same with or
	# without the lantern flag, and the cut lines 051/052 never play.
	for cut in ["051", "052", "053"]:
		assert_false(_has(run, "ch03_verse_" + cut), "cut line %s never plays %s" % [cut, at])
	assert_eq(_has(run, "ch03_verse_063"), told, "Imra line " + at)
	assert_true(_has(run, "ch03_verse_061"), "Toma was at Ansedra in 1001 " + at)
	assert_true(_has(run, "ch03_verse_062"), "Toma's three years " + at)
	assert_eq(_has(run, "ch03_verse_056"), not told and lantern, "gentle deflect " + at)
	assert_eq(_has(run, "ch03_verse_057"), not told and not lantern, "'twice' deflect " + at)
	for sung in ["042", "043", "044", "045", "046"]:
		assert_true(_has(run, "ch03_verse_" + sung), "verse and recognition always play %s %s" % [sung, at])
	var s10 := _shot_of(run, "ch03_verse_043")
	assert_eq(s10.get("shot"), "S10", "the cut to Rhen lands on the second sung line " + at)
	for held in ["044", "045", "046"]:
		assert_true(is_same(_shot_of(run, "ch03_verse_" + held), s10), "S10 holds through %s %s" % [held, at])
	assert_true(float(s10.get("wait", 0.0)) >= S10_HOLD_SEC, "S10 holds >= %.1f s %s" % [S10_HOLD_SEC, at])
	assert_eq(run["events"], [[&"start_battle", ["drownbell"]]], "hands off to the Drownbell " + at)


func test_beach_every_branch() -> void:
	var runs := _all_paths(BEACH, {})
	assert_eq(runs.size(), 4, "2 x 2 menu paths on the beach")
	for run in runs:
		_check_beach_run(run)


func test_first_verse_every_branch_and_input() -> void:
	var total := 0
	for preset in _presets(VERSE_INPUTS):
		var runs := _all_paths(VERSE, preset)
		assert_eq(runs.size(), 4, "2 x 2 menu paths for %s" % [preset])
		for run in runs:
			_check_verse_run(run, preset)
		total += runs.size()
	assert_eq(total, 64, "16 input combinations x 4 paths")


## The real order: each beach outcome feeds the First Verse (side scene and pickup both ways).
func test_beach_then_verse_chained() -> void:
	for beach in _all_paths(BEACH, {}):
		for extra in _presets([&"ch02_heard_pila", &"ch03_found_net_float"] as Array[StringName]):
			var preset: Dictionary = (beach["flags"] as Dictionary).duplicate()
			preset.merge(extra)
			for run in _all_paths(VERSE, preset):
				_check_verse_run(run, preset)
				assert_eq(_flag(run, "ch02_met_asha"), true, "beach flags survive into Ch3")


## Counts push_error and push_warning (not script errors; TestErrorCounter has those).
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
