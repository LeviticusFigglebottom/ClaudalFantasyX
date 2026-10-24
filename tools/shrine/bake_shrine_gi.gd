extends Node
## Bakes the Shell Shrine's two VoxelGI lighting states (door up, door down) and saves them as the
## shipped VoxelGIData resources named in game/data/trials/shell_shrine.json room.gi_data (M2-ENV-10,
## ADR 0029: the level loads them instead of baking ~1.8 s per state on the main thread at entry).
## Run: godot --headless --path . res://tools/shrine/bake_shrine_gi.tscn [-- --out-dir=res://path/]
## (a scene, not --script, so the autoloads the level needs are up)
## It needs a rendering device: run it under godot-render (lavapipe) or a GPU, never --headless (the
## bake comes out empty). assets/PROVENANCE.md has the exact command. Then record the inputs with
## `python3 tools/shrine/gi_inputs.py --write`; tools/tests/test_shrine_gi_bake.py fails when the
## inputs (the shrine scenes, its script, the trial data, the kit's shrine pieces) change without a rebake.

const SCENE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"

var _level: ShellShrineLevel
var _frames := 0


func _ready() -> void:
	_level = (load(SCENE) as PackedScene).instantiate() as ShellShrineLevel
	_level.autostart = false
	_level.bake_at_load = false
	add_child(_level)
	print("bake_shrine_gi: level built")


func _process(_delta: float) -> void:
	_frames += 1
	if _frames == 3:
		_bake()


func _bake() -> void:
	var out_dir := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out-dir="):
			out_dir = a.trim_prefix("--out-dir=")
	var level := _level
	var paths := level.gi_data_paths()
	var failed := false
	for state: String in ["open", "closed"]:
		var t0 := Time.get_ticks_msec()
		print("bake_shrine_gi: baking %s" % state)
		var data := level.bake_state(state == "open")
		var path := str(paths.get(state, ""))
		if out_dir != "":
			path = out_dir.path_join(path.get_file())
		if data == null or path == "":
			push_error("bake_shrine_gi: no data for state %s (path '%s')" % [state, path])
			failed = true
			continue
		var err := ResourceSaver.save(data, path, ResourceSaver.FLAG_COMPRESS)
		print("bake_shrine_gi: %s -> %s (%d ms, %s)" % [state, path, Time.get_ticks_msec() - t0, error_string(err)])
		failed = failed or err != OK
	get_tree().quit(1 if failed else 0)
