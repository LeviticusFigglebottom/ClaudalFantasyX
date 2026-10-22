extends Node
## Headless test runner: `godot --headless --path . res://tests/run_tests.tscn`.
## Discovers tests/unit/test_*.gd and tests/integration/test_*.gd, runs every test_* method,
## prints a summary, and quits with exit code 1 on any failure (CI gate).
## Optional filter: `-- --filter=<substring>` restricts to matching file names.

const TEST_DIRS: Array[String] = ["res://tests/unit", "res://tests/integration"]


func _ready() -> void:
	var filter := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--filter="):
			filter = arg.trim_prefix("--filter=")
	var total := 0
	var failed := 0
	var all_failures: Array[String] = []
	var errors := TestErrorCounter.new()
	OS.add_logger(errors)
	for dir_path in TEST_DIRS:
		for file in _test_files(dir_path):
			if filter != "" and not file.contains(filter):
				continue
			var script := load("%s/%s" % [dir_path, file]) as GDScript
			if script == null:
				all_failures.append("%s: failed to load (parse error?)" % file)
				failed += 1
				continue
			for method in script.get_script_method_list():
				var mname: String = method["name"]
				if not mname.begins_with("test_"):
					continue
				var tc: TestCase = script.new()
				tc.begin_test("%s::%s" % [file, mname])
				tc.before_each()
				errors.take()
				tc.call(mname)
				if errors.take() > 0:
					tc.fail("script error: %s" % errors.last_message)
				total += 1
				if tc.failures.is_empty():
					print("  PASS %s::%s" % [file, mname])
				else:
					failed += 1
					print("  FAIL %s::%s" % [file, mname])
					all_failures.append_array(tc.failures)
	print("")
	for f in all_failures:
		printerr("FAILURE ", f)
	print("Tests: %d run, %d failed" % [total, failed])
	OS.remove_logger(errors)
	get_tree().quit(1 if failed > 0 or total == 0 else 0)


func _test_files(dir_path: String) -> PackedStringArray:
	var out := PackedStringArray()
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return out
	for f in dir.get_files():
		if f.begins_with("test_") and f.ends_with(".gd"):
			out.append(f)
	out.sort()
	return out
