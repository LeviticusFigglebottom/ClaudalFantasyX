extends TestCase
## Integration QA (M3-HER-1121): the playthrough guards. Every story-thread test (tests/integration/test_*_thread.gd:
## the M2 slice's first-playable thread and each Act I chapter's) is driven again with a QaLogger listening, and
## the guard fails on what those tests don't check: any engine error or script error the game raised on the way
## (a freed object, a bad cast, a missing resource), any warning a track left behind (a missing clip, cue, mark,
## sound or music), and any failure of the thread's own assertions. Warnings already handed to their owner match a
## row of qa_known.json and are reported under its task instead.

const DIR := "res://tests/integration"
const KNOWN := "res://tests/integration/qa_known.json"
const THREAD_SUFFIX := "_thread.gd"
## The guard's own file is not a thread.
const SELF := "test_qa_threads.gd"


func test_every_thread_plays_through_clean() -> void:
	var known := _known()
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
