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
## --return=<zone> (with --encounter) measures the way back from a won random fight (the human's playtest: seconds
## of black after every battle): it enters the zone, routes to the field battle, then routes back to the zone's
## "Encounter" spawn, and prints that return's stats ("resident": the field kept through the fight, SceneRouter).
## --no-resident turns the resident field off, to measure the full reload for comparison.
## --ready-profile prints the measured change's add-to-tree frame by node: each node's `ready` is stamped as the new
## scene enters the tree (SceneRouter.scene_instantiated), and the slowest gaps print as READY_PROFILE lines (a
## node's own _ready, its children's already counted): what a zone's hidden add frame spends (Haluna's ~1.5 s).

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
## --warm-scene (M3-HER-1167) also starts the destination zone's loads before the change and lets them finish, as the
## title does for the zone its highlighted choice enters while it shows.
const ARG_WARM_SCENE := "--warm-scene"
## --round-trip=<encounter>: after the change to --to, a field battle for <encounter> and the change back to --to;
## the stats printed are the return's (the playtest's black screen after a won fight, 2026-10-30).
const ARG_ROUND_TRIP := "--round-trip="
const ARG_RETURN := "--return="
const ARG_NO_RESIDENT := "--no-resident"
const ARG_READY_PROFILE := "--ready-profile"
## --ready-profile: how many of the slowest nodes' _ready to print (READY_PROFILE <ms> <node path>).
const READY_PROFILE_TOP := 15
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
	var warm_scene := false
	var round_trip := &""
	var back_to := ""
	var profile := false
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
		elif arg == ARG_WARM_SCENE:
			warm_scene = true
		elif arg.begins_with(ARG_ENCOUNTER):
			to = _queue_battle(StringName(arg.trim_prefix(ARG_ENCOUNTER)))
		elif arg.begins_with(ARG_ROUND_TRIP):
			round_trip = StringName(arg.trim_prefix(ARG_ROUND_TRIP))
		elif arg.begins_with(ARG_RETURN):
			back_to = arg.trim_prefix(ARG_RETURN)
		elif arg == ARG_NO_RESIDENT:
			SceneRouter.keep_field_resident = false
		elif arg == ARG_READY_PROFILE:
			profile = true
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
	if warm_scene and resident != null:
		resident.load_scene(to)
		var scene_frames := int(cfg.get("timeout_frames", 0))
		while not resident.is_ready() and scene_frames > 0:
			scene_frames -= 1
			await get_tree().process_frame
	if round_trip != &"":
		await _change_and_wait(to, cfg)
		await _change_and_wait(_queue_battle(round_trip), cfg)
		BattleRequest.clear()
	if back_to != "":  # into the zone, then the fight; the change measured below is the way back
		var pending := BattleRequest.pending()
		SceneRouter.change_scene(back_to)
		await _until_idle(int(cfg.get("timeout_frames", 0)))
		BattleRequest._pending = pending  # the zone's arrival may clear it; the fight is still the one queued
		SceneRouter.change_scene(to)
		await _until_idle(int(cfg.get("timeout_frames", 0)))
		to = back_to
	SceneRouter.last_swap_stats = {}
	var stamps: Array = []
	if profile:
		SceneRouter.scene_instantiated.connect(func(n: Node) -> void: _stamp_ready(n, stamps), CONNECT_ONE_SHOT)
	SceneRouter.change_scene(to, FieldEncounters.RETURN_SPAWN if back_to != "" else &"")
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
	if profile:
		_print_ready_profile(stamps)
	print("%s %s" % [OUTPUT_TAG, JSON.stringify(stats)])
	get_tree().quit(EXIT_OK if stats.has("max_frame_ms") else EXIT_FAILED)


## Changes to `path` and waits until the change and its visible window are over (or the frame budget runs out).
func _change_and_wait(path: String, cfg: Dictionary) -> void:
	SceneRouter.change_scene(path)
	var frames_left := int(cfg.get("timeout_frames", 0))
	while (SceneRouter.is_busy() or SceneRouter.is_measuring()) and frames_left > 0:
		frames_left -= 1
		await get_tree().process_frame


## Stamps every node of `root` as it emits ready ([usec, path], in order), the first one at the start of the add.
static func _stamp_ready(root: Node, stamps: Array) -> void:
	var nodes: Array[Node] = [root]
	nodes.append_array(root.find_children("*", "", true, false))
	for n in nodes:
		var path := str(root.get_path_to(n))
		n.ready.connect(func() -> void: stamps.append([Time.get_ticks_usec(), path]), CONNECT_ONE_SHOT)
	root.tree_entered.connect(func() -> void: stamps.push_front([Time.get_ticks_usec(), "<enter>"]), CONNECT_ONE_SHOT)


## The slowest gaps between consecutive ready stamps (each node's own _ready), READY_PROFILE_TOP of them.
static func _print_ready_profile(stamps: Array) -> void:
	var costs: Array = []
	for i in range(1, stamps.size()):
		costs.append([(int(stamps[i][0]) - int(stamps[i - 1][0])) / 1000.0, str(stamps[i][1])])
	costs.sort_custom(func(a: Array, b: Array) -> bool: return float(a[0]) > float(b[0]))
	var total := (int(stamps[-1][0]) - int(stamps[0][0])) / 1000.0 if stamps.size() > 1 else 0.0
	print("READY_PROFILE total %.1f ms over %d nodes" % [total, maxi(stamps.size() - 1, 0)])
	for c: Array in costs.slice(0, READY_PROFILE_TOP):
		print("READY_PROFILE %8.1f ms  %s" % [float(c[0]), str(c[1])])


func _until_idle(frames: int) -> void:
	while (SceneRouter.is_busy() or SceneRouter.is_measuring()) and frames > 0:
		frames -= 1
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
