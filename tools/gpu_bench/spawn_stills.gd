class_name SpawnStills
extends Node
## A light row walk for lavapipe (cloud QA pass 6): one still per spawn after the field camera settles, instead of
## slice_sweep's timed dwell (at lavapipe's ~2 s frames its 60-frame floor costs minutes a spawn, and its memory
## outgrew the cloud box).
##   godot-render --path . --audio-driver Dummy res://tools/gpu_bench/spawn_stills.tscn -- --out=/abs/dir \
##     --chapter=ch09 --location=ch09/corrow_night --spawns=Strand,RoadGate [--frames=24 --battle=ch06_ridge_skippers]
## The F8 chapter start (the story so far and the party), then the location; each spawn is placed as WorldReturn
## places the player, and <out>/<location>_<spawn>.png is saved after --frames frames. "-" in --spawns is the
## location's arrival view; --spawns=* walks every spawn. --battle=<encounter> asks that fight from the location
## (returning there) and saves <out>/battle_<encounter>_<n>.png at --frames and every --frames after, --battle-shots
## times.

const CHAPTER_SELECT := "res://game/data/debug/chapter_select.json"
const LOAD_TIMEOUT_MS := 600000

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


func _until_idle(router: Node) -> void:
	var t := Time.get_ticks_msec()
	while bool(router.call(&"is_busy")) and Time.get_ticks_msec() - t < LOAD_TIMEOUT_MS:
		await get_tree().process_frame


func _frames(n: int) -> void:
	for i in n:
		await RenderingServer.frame_post_draw


func _save(path: String) -> void:
	get_viewport().get_texture().get_image().save_png(path)
