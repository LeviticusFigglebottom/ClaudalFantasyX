class_name SceneSwapProbe
extends Node
## Scene-swap probe (M1-RND-06 fix). Run it as the main scene of a fresh process:
##   godot --headless --path . res://game/core/debug/scene_swap_probe.tscn -- --to=<res path> [--legacy]
## It enters the `from` scene (perf_budgets.json) the way the game boots, lets it settle, routes to
## `--to` through SceneRouter, then prints one line "SCENE_SWAP_PROBE <json of last_swap_stats>"
## and quits (0 = measured, 1 = no measurement). --legacy turns the router's hitch fixes off, so
## the M0 behaviour can be measured on the same build. tests/unit/test_scene_router_swap.gd runs it.
## --launch (M2-ARC-03) measures the launch instead: it enters `from` as the game boots and prints the
## stats of the boot card's reveal (SceneRouter.measure_reveal) once its visible window ends; no change.
## --frame-usec=<n> (M2-MNU-06) measures on a fake clock that advances exactly n microseconds per process
## frame (SceneRouter.set_measure_clock), so every window's frame times are known in advance and the test
## judges the real swap deterministically, whatever the machine's load.
## --resident-loads (ADR 0111, ADR 0042 §4) turns ResidentLoads on in the headless run, as the game has it, so
## tools/loading/act1_swap_sweep.py measures the Act I changes with their threaded loads behind the fade.
## --warm-resident also loads the resident set (the hero bodies) before the change, as the title does while it
## shows, so the entry measures a change made in play rather than the first one after launch.
## --encounter=<id> routes to a field battle instead of --to: it queues a BattleRequest for that encounter (as a
## field trigger does, without its stinger) and changes to the field battle scene, so the battle's arena and
## enemies load behind the fade as in play.

const BUDGETS_PATH := "res://game/data/debug/perf_budgets.json"
const SECTION := "scene_swap"
const OUTPUT_TAG := "SCENE_SWAP_PROBE"
const ARG_TO := "--to="
const ARG_LEGACY := "--legacy"
const ARG_LAUNCH := "--launch"
const ARG_FRAME_USEC := "--frame-usec="
const ARG_RESIDENT_LOADS := "--resident-loads"
const ARG_WARM_RESIDENT := "--warm-resident"
const ARG_ENCOUNTER := "--encounter="
## --round-trip=<encounter>: after the change to --to, a field battle for <encounter> and the change back to --to;
## the stats printed are the return's (the playtest's black screen after a won fight, 2026-10-30).
const ARG_ROUND_TRIP := "--round-trip="
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
	var launch := false
	var frame_usec := 0
	var warm_resident := false
	var round_trip := &""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with(ARG_TO):
			to = arg.trim_prefix(ARG_TO)
		elif arg.begins_with(ARG_FRAME_USEC):
			frame_usec = arg.trim_prefix(ARG_FRAME_USEC).to_int()
		elif arg == ARG_LEGACY:
			legacy = true
		elif arg == ARG_LAUNCH:
			launch = true
		elif arg == ARG_RESIDENT_LOADS:
			ResidentLoads.run_headless = true
		elif arg == ARG_WARM_RESIDENT:
			warm_resident = true
		elif arg.begins_with(ARG_ENCOUNTER):
			to = _queue_battle(StringName(arg.trim_prefix(ARG_ENCOUNTER)))
		elif arg.begins_with(ARG_ROUND_TRIP):
			round_trip = StringName(arg.trim_prefix(ARG_ROUND_TRIP))
	if frame_usec > 0:
		SceneRouter.set_measure_clock(frame_clock(frame_usec))
	if launch and not cfg.is_empty():
		_run_launch(cfg)
		return
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
	var resident := ResidentLoads.shared()
	if warm_resident and resident != null:
		resident.warm()
		var warm_frames := int(cfg.get("timeout_frames", 0))
		while not resident.is_ready() and warm_frames > 0:
			warm_frames -= 1
			await get_tree().process_frame
	if round_trip != &"":
		await _change_and_wait(to, cfg)
		await _change_and_wait(_queue_battle(round_trip), cfg)
		BattleRequest.clear()
	SceneRouter.last_swap_stats = {}
	SceneRouter.change_scene(to)
	var frames_left := int(cfg.get("timeout_frames", 0))
	# M1-ARC-16: the visible window (the fade lifting plus VISIBLE_MEASURE_FRAMES) ends after is_busy() does.
	while (SceneRouter.is_busy() or SceneRouter.is_measuring()) and frames_left > 0:
		frames_left -= 1
		await get_tree().process_frame
	var stats := SceneRouter.last_swap_stats
	if frames_left <= 0:  # out of frames: say what the change was still waiting on (PC pass 4 row 67)
		var holders := [SceneRouter.swap_holders(), SceneRouter.reveal_holders()]
		push_warning(
			(
				"SceneSwapProbe: timed out busy=%s measuring=%s swap holders %s reveal holders %s"
				% ([SceneRouter.is_busy(), SceneRouter.is_measuring()] + holders)
			)
		)
	stats["legacy"] = legacy
	print("%s %s" % [OUTPUT_TAG, JSON.stringify(stats)])
	get_tree().quit(EXIT_OK if stats.has("max_frame_ms") else EXIT_FAILED)


## Changes to `path` and waits until the change and its visible window are over (or the frame budget runs out).
func _change_and_wait(path: String, cfg: Dictionary) -> void:
	SceneRouter.change_scene(path)
	var frames_left := int(cfg.get("timeout_frames", 0))
	while (SceneRouter.is_busy() or SceneRouter.is_measuring()) and frames_left > 0:
		frames_left -= 1
		await get_tree().process_frame


## Queues a field battle for `encounter` (BattleRequest.submit with the change recorded, not made) and returns the
## field battle scene to route to.
static func _queue_battle(encounter: StringName) -> String:
	var r := BattleRequest.make(encounter, &"", &"")
	BattleRequest.change_scene = func(_path: String) -> void: pass
	BattleRequest.submit(r)
	BattleRequest.change_scene = Callable()
	return BattleRequest.scene_path()


## A fake clock for SceneRouter.set_measure_clock: `step_usec` microseconds per process frame, so two reads in
## one frame are equal and a read one frame later is exactly `step_usec` on.
static func frame_clock(step_usec: int) -> Callable:
	return func() -> int: return Engine.get_process_frames() * step_usec


## --launch: the reveal of `from` entered as the main scene (no SceneRouter change runs).
func _run_launch(cfg: Dictionary) -> void:
	SceneRouter.last_swap_stats = {}
	get_tree().change_scene_to_file(str(cfg.get("from", "")))
	var frames_left := int(cfg.get("timeout_frames", 0))
	while frames_left > 0 and not SceneRouter.last_swap_stats.has("visible_complete"):
		frames_left -= 1
		await get_tree().process_frame
	var stats := SceneRouter.last_swap_stats
	print("%s %s" % [OUTPUT_TAG, JSON.stringify(stats)])
	get_tree().quit(EXIT_OK if stats.has("visible_complete") else EXIT_FAILED)
