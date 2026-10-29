extends TestCase
## Integration QA (M3-HER-1121): the playthrough guards. Every story-thread test (tests/integration/test_*_thread.gd:
## the M2 slice's first-playable thread and each Act I chapter's) is driven again with a QaLogger listening, and
## the guard fails on what those tests don't check: any engine error or script error the game raised on the way
## (a freed object, a bad cast, a missing resource), any warning a track left behind (a missing clip, cue, mark,
## sound or music), and any failure of the thread's own assertions. Warnings already handed to their owner match a
## row of qa_known.json and are reported under its task instead.
## It also fails on a story flag a thread never raises. By the end of a chapter's thread, every flag its chapter file
## waits on (`when.set`) must be set, and so must every main objective's `requires` and `until` flags in that
## chapter's zones (objectives.json: the progress spine; the slice's thread covers ch02 and ch03). A flag only an
## optional branch raises is listed in qa_known.json "unraised" (flag -> why), and reported.

const DIR := "res://tests/integration"
const KNOWN := "res://tests/integration/qa_known.json"
const THREAD_SUFFIX := "_thread.gd"
## The guard's own file is not a thread.
const SELF := "test_qa_threads.gd"
const CHAPTERS_DIR := "res://game/data/flow/chapters"
const OBJECTIVES := "res://game/data/flow/objectives.json"
## The thread file whose chapters aren't in its name.
const CHAPTERS_OF := {"test_fp_thread.gd": ["ch02", "ch03"]}


func test_every_thread_plays_through_clean() -> void:
	var known := _known()
	var unraised := _json(KNOWN).get("unraised", {}) as Dictionary
	var raised := {}  # flag -> true, for the thread being run
	var on_flag := func(flag: StringName, value: Variant) -> void:
		if value:
			raised[String(flag)] = true
	EventBus.flag_changed.connect(on_flag)
	var qa := QaLogger.new()
	OS.add_logger(qa)
	var counted := {}  # task -> count
	var threads := 0
	for file in _thread_files():
		var script := load(DIR.path_join(file)) as GDScript
		if script == null or not script.can_instantiate():
			fail("%s does not load" % file)
			continue
		threads += 1
		raised.clear()
		for method in script.get_script_method_list():
			var mname: String = method["name"]
			if not mname.begins_with("test_"):
				continue
			var tc: TestCase = script.new()
			tc.begin_test("%s::%s" % [file, mname])
			tc.before_each()
			qa.take()
			if not TestCase.runs_to_the_end(tc, mname):
				tc.fail(TestCase.SUSPENDED)
			for f in tc.failures:
				fail("%s: the thread's own check failed: %s" % [mname, f])
			for e in qa.take():
				var task := _match(known, str(e["text"]))
				if task != "":
					counted[task] = int(counted.get(task, 0)) + 1
				elif e["kind"] == QaLogger.KIND_WARNING:
					fail("%s::%s: an unexplained warning: %s (%s)" % [file, mname, e["text"], e["where"]])
				else:
					fail("%s::%s: %s %s (%s)" % [file, mname, e["kind"], e["text"], e["where"]])
		for flag in waited_on(_chapters_of(file)):
			if raised.has(flag):
				continue
			if unraised.has(flag):
				print("  KNOWN unraised %s in %s: %s" % [flag, file, unraised[flag]])
			else:
				fail("%s: the chapter waits on %s, and the thread never raises it (a softlock?)" % [file, flag])
	EventBus.flag_changed.disconnect(on_flag)
	OS.remove_logger(qa)
	for task: String in counted:
		print("  KNOWN %s: %d messages" % [task, counted[task]])
	assert_true(threads >= 2, "the slice's thread and the Act I chapters' threads were found (%d)" % threads)


static func _thread_files() -> PackedStringArray:
	var out := PackedStringArray()
	for f in DirAccess.get_files_at(DIR):
		if f.begins_with("test_") and f.ends_with(THREAD_SUFFIX) and f != SELF:
			out.append(f)
	out.sort()
	return out


## The chapters a thread plays: test_ch04_thread.gd -> ["ch04"].
static func _chapters_of(file: String) -> Array:
	return CHAPTERS_OF.get(file, [file.trim_prefix("test_").trim_suffix(THREAD_SUFFIX)])


## Every flag the chapters' beats wait on (`when.set`), and every main objective's `requires` and `until` in their
## zones, sorted.
static func waited_on(chapters: Array) -> Array[String]:
	var out: Array[String] = []
	for ch: Variant in chapters:
		_collect_when(_json(CHAPTERS_DIR.path_join(str(ch) + ".json")), out)
	var rows: Array = (_json(OBJECTIVES).get("objectives", {}) as Dictionary).get("rows", [])
	for r: Variant in rows:
		var row := r as Dictionary
		if row.get("side", false) or not chapters.has(str(row.get("zone", "")).get_slice("/", 0)):
			continue
		var flags: Array = row.get("requires", []).duplicate()
		if row.get("until") != null:
			flags.append(row["until"])
		for f: Variant in flags:
			if not out.has(str(f)):
				out.append(str(f))
	out.sort()
	return out


static func _collect_when(v: Variant, out: Array[String]) -> void:
	if v is Dictionary:
		var when: Variant = (v as Dictionary).get("when")
		if when is Dictionary:
			for f: Variant in (when as Dictionary).get("set", []):
				if not out.has(str(f)):
					out.append(str(f))
		for k: Variant in v:
			_collect_when(v[k], out)
	elif v is Array:
		for x: Variant in v:
			_collect_when(x, out)


static func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


static func _known() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var f := FileAccess.open(KNOWN, FileAccess.READ)
	if f == null:
		return out
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	for row: Variant in (parsed as Dictionary).get("known", []) if parsed is Dictionary else []:
		var re := RegEx.new()
		if re.compile(str((row as Dictionary).get("pattern", ""))) == OK:
			out.append({"re": re, "task": str((row as Dictionary).get("task", ""))})
	return out


static func _match(known: Array[Dictionary], text: String) -> String:
	for k in known:
		if (k["re"] as RegEx).search(text) != null:
			return str(k["task"])
	return ""
