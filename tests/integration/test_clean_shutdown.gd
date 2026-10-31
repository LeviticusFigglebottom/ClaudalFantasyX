extends TestCase
## PC row 85: after a slice_sweep walk the process looped `Parameter "material" is null` at shutdown until its log
## filled the disk (59 GB). The scenes SceneRouter keeps off the tree (the field resident through a fight, the
## fight's cross-zone return parked) were never freed by the tree's teardown, only by the engine's last cleanup
## after the RenderingServer. In a child process (QuitProbe: a zone, its fight, a parked return, then quit) the exit
## must come within EXIT_SEC of the quit, with no engine line repeated more than REPEAT_MAX times and no instance
## or material freed late.

const PROBE := "res://game/core/debug/quit_probe.tscn"
const QUIT_TAG := "QUIT_PROBE_QUIT"
const ZONE := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
const ENCOUNTER := "ch03_causeway_shore"
const CROSS := "res://game/levels/ch02/haluna/haluna.tscn"
## The whole run's wall-clock cap (the zone, the fight and the park take most of it); a looping exit hits it.
const RUN_SEC := 300
const EXIT_SEC := 20.0
const REPEAT_MAX := 5
const TIMED_OUT := 124
const LATE_FREES: Array[String] = ["Leaked instance dependency", '"material" is null']
const GODOT_ENV := "GODOT"
const BASH := "/bin/bash"
const SCRIPT_PATH := "user://test_clean_shutdown.sh"


func test_quitting_with_a_kept_zone_and_a_parked_return_exits_clean() -> void:
	var godot := OS.get_environment(GODOT_ENV)
	if godot == "":
		godot = OS.get_executable_path()
	var cmd := (
		"start=$(date +%%s.%%N); timeout %d '%s' --headless --path '%s' %s -- --to=%s --encounter=%s --cross-return=%s"
		+ ' 2>&1 | while IFS= read -r l; do case "$l" in %s) echo "$l @$(date +%%s.%%N)";; *) echo "$l";; esac;'
		+ ' done; echo "EXIT ${PIPESTATUS[0]} @$(date +%%s.%%N)"'
	)
	var line := (
		cmd % [RUN_SEC, godot, ProjectSettings.globalize_path("res://"), PROBE, ZONE, ENCOUNTER, CROSS, QUIT_TAG]
	)
	var output: Array = []
	# OS.execute with output runs one popen command line, so `$(...)` and quotes in a -c argument would be expanded
	# by that outer shell: the script goes to a file.
	var script := ProjectSettings.globalize_path(SCRIPT_PATH)
	var f := FileAccess.open(script, FileAccess.WRITE)
	f.store_string(line + "\n")
	f.close()
	var ran := OS.execute(BASH, [script], output, true)
	DirAccess.remove_absolute(script)
	var lines := str(output[0] if not output.is_empty() else "").split("\n")
	var quit_at := -1.0
	var exit_at := -1.0
	var code := -1
	var after: Dictionary = {}
	for l in lines:
		if l.begins_with(QUIT_TAG):
			quit_at = float(l.get_slice("@", 1))
		elif l.begins_with("EXIT "):
			code = int(l.get_slice(" ", 1))
			exit_at = float(l.get_slice("@", 1))
		elif quit_at >= 0.0 and (l.begins_with("ERROR") or l.begins_with("WARNING")):
			after[l] = int(after.get(l, 0)) + 1
	assert_true(
		quit_at >= 0.0, "the probe reached its quit (exit %d, bash %d): %s" % [code, ran, "\n".join(lines.slice(0, 8))]
	)
	assert_true(code != TIMED_OUT, "the process exits (no loop at shutdown)")
	assert_true(exit_at - quit_at <= EXIT_SEC, "the exit takes %.1f s after the quit" % (exit_at - quit_at))
	for l: String in after:
		assert_true(int(after[l]) <= REPEAT_MAX, "repeated %d times at exit: %s" % [after[l], l])
		for late in LATE_FREES:
			assert_false(l.contains(late), "freed after the renderer at exit: %s" % l)
