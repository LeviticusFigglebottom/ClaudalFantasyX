class_name SpawnStills
extends Node
## A light row walk for lavapipe (cloud QA pass 6): one still per spawn after the field camera settles, instead of
## slice_sweep's timed dwell (at lavapipe's ~2 s frames its 60-frame floor costs minutes a spawn, and its memory
## outgrew the cloud box).
##   godot-render --path . --audio-driver Dummy res://tools/gpu_bench/spawn_stills.tscn -- --out=/abs/dir \
##     --chapter=ch09 --location=ch09/corrow_night --spawns=Strand,RoadGate [--frames=24 --battle=ch06_ridge_skippers
##     --views="name:x,y,z>tx,ty,tz;..." --fov=55]
## The F8 chapter start (the story so far and the party), then the location; each spawn is placed as WorldReturn
## places the player, and <out>/<location>_<spawn>.png is saved after --frames frames. "-" in --spawns is the
## location's arrival view; --spawns=* walks every spawn. --battle=<encounter> asks that fight from the location
## (returning there) and saves <out>/battle_<encounter>_<n>.png at --frames and every --frames after, --battle-shots
## times.

const CHAPTER_SELECT := "res://game/data/debug/chapter_select.json"
const LOAD_TIMEOUT_MS := 600000
const STORY_TIMEOUT_MS := 900000
const TAP_EVERY_MS := 1500

var _opts: Dictionary = {}


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := (get_script() as GDScript).new() as Node
		driver.name = "SpawnStillsDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else "true"
	var out_dir := str(_opts.get("out", "user://spawn_stills"))
	DirAccess.make_dir_recursive_absolute(out_dir)
	var saves := get_tree().root.get_node_or_null(^"SaveSystem")
	if saves != null and saves.has_method(&"hold_autosave"):
		saves.call(&"hold_autosave", self)
	var frames := int(_opts.get("frames", 24))
	var location := StringName(str(_opts.get("location", "")))
	for start: Dictionary in DebugReadouts.chapter_starts(CHAPTER_SELECT):
		if str(start["id"]) == str(_opts.get("chapter", "")):
			DebugReadouts.apply_chapter_start(start)
			if location == &"":
				location = StringName(str(start["location"]))
	for f in str(_opts.get("flags", "")).split(",", false):
		Game.set_flag(StringName(f))
	var router := get_tree().root.get_node(^"SceneRouter")
	FlowRouting.go_to(location, &"")
	await _until_idle(router)
	await _story_free(router)
	var tag := String(location).replace("/", "_")
	var spawns := str(_opts.get("spawns", "-")).split(",", false)
	if spawns.size() == 1 and spawns[0] == "*":
		spawns = PackedStringArray(["-"])
		var root := get_tree().current_scene.get_node_or_null(^"Spawns")
		if root != null:
			for c in root.get_children():
				spawns.append(str(c.name))
	for s in spawns:
		if s != "-":
			WorldReturn.place_player(get_tree().current_scene, StringName(s))
		await _frames(frames)
		_save(out_dir.path_join("%s_%s.png" % [tag, s.replace("-", "arrival")]))
		print("SPAWN_STILL %s %s" % [location, s])
	# --views=name:x,y,z>tx,ty,tz;... : a free camera at each point looking at its target (the field director is
	# stopped first so it can't take the view back).
	var views := str(_opts.get("views", ""))
	if views != "":
		for d in get_tree().current_scene.find_children("*", "FieldCameraDirector", true, false):
			d.process_mode = Node.PROCESS_MODE_DISABLED
		var cam := Camera3D.new()
		cam.fov = float(_opts.get("fov", 55))
		get_tree().current_scene.add_child(cam)
		for v in views.split(";", false):
			var nv := v.split(":", true, 1)
			var pts := nv[1].split(">")
			var a := pts[0].split_floats(",")
			var b := pts[1].split_floats(",")
			cam.look_at_from_position(Vector3(a[0], a[1], a[2]), Vector3(b[0], b[1], b[2]))
			cam.make_current()
			await _frames(frames)
			_save(out_dir.path_join("%s_view_%s.png" % [tag, nv[0]]))
			print("SPAWN_VIEW %s" % nv[0])
	var battle := str(_opts.get("battle", ""))
	if battle != "":
		BattleRequest.start(StringName(battle), location, &"")
		var t := Time.get_ticks_msec()
		while not (get_tree().current_scene is FieldBattle) and Time.get_ticks_msec() - t < LOAD_TIMEOUT_MS:
			await get_tree().process_frame
		await _until_idle(router)
		var ctl := get_tree().current_scene as FieldBattle
		var parts: Array = []
		if ctl != null and ctl.stage != null:
			for c in ctl.stage.get_children():
				parts.append("%s(%s)" % [c.name, c.scene_file_path])
		print("SPAWN_BATTLE %s stage %s" % [battle, ", ".join(parts)])
		for n in int(_opts.get("battle-shots", 3)):
			await _frames(frames)
			_save(out_dir.path_join("battle_%s_%d.png" % [battle, n]))
	get_tree().quit()


## Taps ui_accept (as a player reads through) until the zone's story is free and the router idle, so the spawns are
## placed in the playable field and not under an arrival cutscene. Gives up after STORY_TIMEOUT_MS.
func _story_free(router: Node) -> void:
	var t := Time.get_ticks_msec()
	var next_tap := 0
	while Time.get_ticks_msec() - t < STORY_TIMEOUT_MS:
		var story: Variant = get_tree().current_scene.get(&"story") if get_tree().current_scene != null else null
		var busy := bool(router.call(&"is_busy")) or (story is ZoneStory and not (story as ZoneStory).is_free())
		# A cutscene outside the zone story (Haluna's beach) shows as the player not taking input.
		var players := get_tree().current_scene.find_children("*", "FieldController", true, false)
		if not players.is_empty() and not (players[0] as FieldController).accepts_input:
			busy = true
		if not busy:
			return
		if Time.get_ticks_msec() >= next_tap:
			var ev := InputEventAction.new()
			ev.action = &"ui_accept"
			ev.pressed = true
			Input.parse_input_event(ev)
			var up := InputEventAction.new()
			up.action = &"ui_accept"
			Input.parse_input_event(up)
			next_tap = Time.get_ticks_msec() + TAP_EVERY_MS
		await get_tree().process_frame
	print("SPAWN_STILLS story still busy after %d s" % (STORY_TIMEOUT_MS / 1000))


func _until_idle(router: Node) -> void:
	var t := Time.get_ticks_msec()
	while bool(router.call(&"is_busy")) and Time.get_ticks_msec() - t < LOAD_TIMEOUT_MS:
		await get_tree().process_frame


func _frames(n: int) -> void:
	for i in n:
		await RenderingServer.frame_post_draw


func _save(path: String) -> void:
	get_viewport().get_texture().get_image().save_png(path)
