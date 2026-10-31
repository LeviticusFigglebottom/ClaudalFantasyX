class_name QuitProbe
extends Node
## The shutdown order (PC row 85: after a slice_sweep walk the process looped `Parameter "material" is null` at exit,
## a 59 GB log). Runs headless:
##   godot --headless --path . res://game/core/debug/quit_probe.tscn -- --to=<zone scene> [--encounter=<id>]
## It enters the zone, settles, optionally starts the fight (the zone is kept resident off the tree, and a cross-zone
## return is parked: the scenes that live outside the tree), settles, prints QUIT_PROBE_QUIT and quits. The caller
## times the exit and reads the log (tests/integration/test_clean_shutdown.gd).

const ARG_TO := "--to="
const ARG_ENCOUNTER := "--encounter="
const ARG_CROSS := "--cross-return="
const SETTLE_FRAMES := 30
const TIMEOUT_FRAMES := 3600
const QUIT_TAG := "QUIT_PROBE_QUIT"


func _ready() -> void:
	if get_tree().current_scene == self:
		var driver: Node = (get_script() as GDScript).new()
		driver.name = "QuitProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	var to := ""
	var encounter := &""
	var cross := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with(ARG_TO):
			to = arg.trim_prefix(ARG_TO)
		elif arg.begins_with(ARG_ENCOUNTER):
			encounter = StringName(arg.trim_prefix(ARG_ENCOUNTER))
		elif arg.begins_with(ARG_CROSS):
			cross = arg.trim_prefix(ARG_CROSS)
	SceneRouter.change_scene(to)
	await _settle()
	if encounter != &"":
		var r := BattleRequest.make(encounter, &"", &"")
		r.return_scene = cross
		BattleRequest.change_scene = func(_path: String) -> void: pass
		BattleRequest.submit(r)
		BattleRequest.change_scene = Callable()
		SceneRouter.change_scene(BattleRequest.scene_path())
		await _settle()
		var frames := TIMEOUT_FRAMES
		while SceneRouter.return_park.building != "" and frames > 0:
			frames -= 1
			await get_tree().process_frame
	print(QUIT_TAG)
	get_tree().quit()


func _settle() -> void:
	var frames := TIMEOUT_FRAMES
	while SceneRouter.is_busy() and frames > 0:
		frames -= 1
		await get_tree().process_frame
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
