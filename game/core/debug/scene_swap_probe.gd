class_name SceneSwapProbe
extends Node
## Scene-swap probe (M1-RND-06 fix). Run it as the main scene of a fresh process:
##   godot --headless --path . res://game/core/debug/scene_swap_probe.tscn -- --to=<res path> [--legacy]
## It enters the `from` scene (perf_budgets.json) the way the game boots, lets it settle, routes to
## `--to` through SceneRouter, then prints one line "SCENE_SWAP_PROBE <json of last_swap_stats>"
## and quits (0 = measured, 1 = no measurement). --legacy turns the router's hitch fixes off, so
## the M0 behaviour can be measured on the same build. tests/unit/test_scene_router_swap.gd runs it.

const BUDGETS_PATH := "res://game/data/debug/perf_budgets.json"
const SECTION := "scene_swap"
const OUTPUT_TAG := "SCENE_SWAP_PROBE"
const ARG_TO := "--to="
const ARG_LEGACY := "--legacy"
const EXIT_OK := 0
const EXIT_FAILED := 1


func _ready() -> void:
	if get_tree().current_scene == self:
		# The router frees the current scene, so the measuring driver must live beside it.
		var driver: Node = (get_script() as GDScript).new()
		driver.name = "SceneSwapProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


static func budgets() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(BUDGETS_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("SceneSwapProbe: cannot read %s" % BUDGETS_PATH)
		return {}
	return (parsed as Dictionary).get(SECTION, {}) as Dictionary


func _run() -> void:
	var cfg := budgets()
	var to := ""
	var legacy := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with(ARG_TO):
			to = arg.trim_prefix(ARG_TO)
		elif arg == ARG_LEGACY:
			legacy = true
	if to == "" or cfg.is_empty():
		push_error("SceneSwapProbe: needs %s<scene> and a readable %s" % [ARG_TO, BUDGETS_PATH])
		get_tree().quit(EXIT_FAILED)
		return
	if legacy:
		SceneRouter.instantiate_on_thread = false
		SceneRouter.warm_fonts = false
		SceneRouter.split_swap = false
	get_tree().change_scene_to_file(str(cfg.get("from", "")))
	for i in int(cfg.get("settle_frames", 0)):
		await get_tree().process_frame
	SceneRouter.last_swap_stats = {}
	SceneRouter.change_scene(to)
	var frames_left := int(cfg.get("timeout_frames", 0))
	while SceneRouter.is_busy() and frames_left > 0:
		frames_left -= 1
		await get_tree().process_frame
	var stats := SceneRouter.last_swap_stats
	stats["legacy"] = legacy
	print("%s %s" % [OUTPUT_TAG, JSON.stringify(stats)])
	get_tree().quit(EXIT_OK if stats.has("max_frame_ms") else EXIT_FAILED)
