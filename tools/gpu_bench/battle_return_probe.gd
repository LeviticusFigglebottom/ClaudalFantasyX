class_name BattleReturnProbe
extends Node
## Battle victory -> field return timing (pc-gpu, the human's 10-30 playtest: "a multi-second black screen after
## every win"). Run windowed on the real GPU, one fight per process:
##   godot --path . --audio-driver Dummy res://tools/gpu_bench/battle_return_probe.tscn -- \
##     --encounter=ch02_tideline --location=ch02/haluna [--return=<location>] [--fight-s=10]
## It enters the field location, starts the fight as a field trigger does (BattleRequest.start), lets it settle,
## forces the win (the engine's own finish), picks Return on the result screen as the player would, and times from
## that choice to:
##   - field_ms: the router done (the field scene in and its fade lifted);
##   - input_ms: the first frame the FieldController takes input with the screen clear;
## plus the worst frame and the frames over 50 ms in between. Prints one line "RETURN_PROBE <json>" and quits.

const SETTLE_FRAMES := 120
const TIMEOUT_FRAMES := 1800
const SLOW_FRAME_MS := 50.0

var _opts: Dictionary = {}
var _fight := PackedFloat64Array()


func _ready() -> void:
	# The probe outlives the scene changes it measures: it runs from the tree root, as SliceSweep does.
	if get_tree().current_scene == self:
		var driver := BattleReturnProbe.new()
		driver.name = "BattleReturnProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else ""
	if _opts.has("preset"):
		var gs := GraphicsSettings.new()
		gs.set_preset(str(_opts["preset"]))
		gs.apply_current(get_viewport(), null)
	if _opts.has("res"):
		var wh := str(_opts["res"]).split("x")
		get_window().size = Vector2i(int(wh[0]), int(wh[1]))
	_run.call_deferred()


func _run() -> void:
	var router := get_tree().root.get_node(^"SceneRouter")
	var location := StringName(str(_opts.get("location", "")))
	var spawn := StringName(str(_opts.get("spawn", "BattleReturn")))
	print("RETURN_PROBE_STEP field")
	FlowRouting.go_to(location, spawn)
	await _until(func() -> bool: return not bool(router.call(&"is_busy")))
	await _frames(SETTLE_FRAMES)
	print("RETURN_PROBE_STEP battle")
	var swapped := [false]
	var on_swap := func(_p: String) -> void: swapped[0] = true
	EventBus.scene_changed.connect(on_swap)
	BattleRequest.start(
		StringName(str(_opts.get("encounter", ""))), StringName(str(_opts.get("return", location))), spawn
	)
	await _until(func() -> bool: return bool(swapped[0]) and not bool(router.call(&"is_busy")))
	EventBus.scene_changed.disconnect(on_swap)
	await _frames(SETTLE_FRAMES)
	# --fight-s: a realistic fight length before the win (a parked return build needs the fight's time; ADR 0209).
	var fight_until := Time.get_ticks_msec() + int(float(_opts.get("fight-s", "0")) * 1000.0)
	# The fight's own frames: a return prewarm that compiles mid-fight shows here as stutter.
	var fight := PackedFloat64Array()
	var fl := Time.get_ticks_usec()
	while Time.get_ticks_msec() < fight_until:
		await get_tree().process_frame
		var fn := Time.get_ticks_usec()
		fight.append((fn - fl) / 1000.0)
		fl = fn
	_fight = fight
	print("RETURN_PROBE_STEP find %s" % get_tree().current_scene)
	var fb := _find(get_tree().current_scene, "FieldBattle")
	if fb == null:
		_report({"error": "no FieldBattle"})
		return
	var engine: Variant = fb.get(&"engine")
	if engine == null:
		_report({"error": "no engine"})
		return
	print("RETURN_PROBE_STEP win")
	engine.call(&"_finish", BattleEngine.OUTCOME_VICTORY)
	await _frames(30)  # the result screen opens
	print("RETURN_PROBE_STEP return")
	var t0 := Time.get_ticks_usec()
	fb.call(&"_on_result_choice", BattleController.CHOICE_RETURN)
	var frames := PackedFloat64Array()
	var field_ms := -1.0
	var input_ms := -1.0
	var last := t0
	for i in TIMEOUT_FRAMES:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		frames.append((now - last) / 1000.0)
		last = now
		var elapsed := (now - t0) / 1000.0
		if (
			field_ms < 0.0
			and i > 2
			and not bool(router.call(&"is_busy"))
			and _find(get_tree().current_scene, "FieldBattle") == null
		):
			field_ms = elapsed
		if field_ms >= 0.0 and input_ms < 0.0:
			var fc := _find(get_tree().current_scene, "FieldController") as FieldController
			if fc != null and fc.accepts_input and fc.screen_clear():
				input_ms = elapsed
				break
	var fc_end := _find(get_tree().current_scene, "FieldController") as FieldController
	var why := (
		"no FieldController"
		if fc_end == null
		else ("accepts_input %s, screen_clear %s" % [fc_end.accepts_input, fc_end.screen_clear()])
	)
	var worst := 0.0
	var slow := 0
	for f in frames:
		worst = maxf(worst, f)
		slow += 1 if f > SLOW_FRAME_MS else 0
	_report(
		{
			"encounter": str(_opts.get("encounter", "")),
			"field_ms": field_ms,
			"input_ms": input_ms,
			"frames": frames.size(),
			"worst_frame_ms": worst,
			"frames_over_50ms": slow,
			"fight_frames": _fight.size(),
			"fight_worst_ms": _worst(_fight),
			"fight_over_33ms": _count_over(_fight, 33.0),
			"fight_over_50ms": _count_over(_fight, SLOW_FRAME_MS),
			"input_state_at_end": why,
			"swap": router.get(&"last_swap_stats"),
		}
	)


func _report(d: Dictionary) -> void:
	print("RETURN_PROBE %s" % JSON.stringify(d))
	get_tree().quit(0 if not d.has("error") else 1)


func _find(root: Node, cls: String) -> Node:
	if root == null:
		return null
	if root.get_class() == cls or (root.get_script() != null and root.get_script().get_global_name() == cls):
		return root
	for c in root.get_children():
		var f := _find(c, cls)
		if f != null:
			return f
	return null


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _until(cond: Callable) -> void:
	for i in TIMEOUT_FRAMES:
		await get_tree().process_frame
		if cond.call():
			return


static func _worst(f: PackedFloat64Array) -> float:
	var w := 0.0
	for x in f:
		w = maxf(w, x)
	return w


static func _count_over(f: PackedFloat64Array, ms: float) -> int:
	var n := 0
	for x in f:
		n += 1 if x > ms else 0
	return n
