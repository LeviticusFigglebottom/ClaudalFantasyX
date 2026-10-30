class_name NewGameProbe
extends Node
## Human playtest check (cloud QA pass 6, the Lead's ask): New Game from a fresh profile plays the Prologue before
## the Underway.
##   XDG_DATA_HOME=<empty dir> godot --headless --path . --audio-driver Dummy \
##     res://tools/gpu_bench/newgame_probe.tscn -- [--secs=240]
## Boots boot.tscn as the game does, waits for the title's menu, presses New Game as the menu does (ui_accept on its
## first row; TitleMenu.start_new_game if the row isn't New Game), then taps ui_accept every TAP_S (as a player reads
## through) and prints NEWGAME_SCENE <seconds> <scene path> on each scene change, until the Underway is reached or
## --secs pass. The PASS/FAIL line says whether a Prologue scene came before ch01/oruvel_underway.

const BOOT := "res://game/core/boot.tscn"
const UNDERWAY := "oruvel_underway"
const TAP_S := 1.5
const TITLE_TIMEOUT_MS := 300000

var _opts: Dictionary = {}


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := (get_script() as GDScript).new() as Node
		driver.name = "NewGameProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else "true"
	get_tree().change_scene_to_file(BOOT)
	var t0 := Time.get_ticks_msec()
	var menu: TitleMenu = null
	while menu == null and Time.get_ticks_msec() - t0 < TITLE_TIMEOUT_MS:
		await get_tree().process_frame
		var found := get_tree().root.find_children("*", "TitleMenu", true, false)
		if not found.is_empty() and (found[0] as Node).is_inside_tree():
			menu = found[0] as TitleMenu
	if menu == null:
		print("NEWGAME_PROBE FAIL: no title menu after %d s" % (TITLE_TIMEOUT_MS / 1000))
		get_tree().quit(1)
		return
	await get_tree().create_timer(2.0).timeout
	print("NEWGAME_SCENE %.1f %s (title)" % [_s(t0), get_tree().current_scene.scene_file_path])
	var err := menu.start_new_game()
	print("NEWGAME_PROBE New Game pressed: %s" % error_string(err))
	var scenes: Array[String] = []
	var last := ""
	var next_tap := 0.0
	var secs := float(_opts.get("secs", 240))
	var start := Time.get_ticks_msec()
	while float(Time.get_ticks_msec() - start) / 1000.0 < secs:
		await get_tree().process_frame
		var cur := get_tree().current_scene
		var path := cur.scene_file_path if cur != null else "-"
		if path != last:
			last = path
			scenes.append(path)
			print("NEWGAME_SCENE %.1f %s" % [_s(t0), path])
			if path.contains(UNDERWAY):
				break
		var now := float(Time.get_ticks_msec() - start) / 1000.0
		if now >= next_tap:
			var ev := InputEventAction.new()
			ev.action = &"ui_accept"
			ev.pressed = true
			Input.parse_input_event(ev)
			var up := InputEventAction.new()
			up.action = &"ui_accept"
			Input.parse_input_event(up)
			next_tap = now + TAP_S
	var prologue_at := -1
	var underway_at := -1
	for i in scenes.size():
		if prologue_at < 0 and scenes[i].to_lower().contains("prologue"):
			prologue_at = i
		if underway_at < 0 and scenes[i].contains(UNDERWAY):
			underway_at = i
	var ok := prologue_at >= 0 and (underway_at < 0 or prologue_at < underway_at)
	print(
		(
			"NEWGAME_PROBE %s: prologue at %d, underway at %d, scenes %s"
			% ["PASS" if ok else "FAIL", prologue_at, underway_at, scenes]
		)
	)
	get_tree().quit()


func _s(t0: int) -> float:
	return float(Time.get_ticks_msec() - t0) / 1000.0
