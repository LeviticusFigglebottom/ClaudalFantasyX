class_name FightEntryProbe
extends Node
## Row 64 headless (cloud QA pass 6): the frames after a fight's fade lifts, CPU only. slice_sweep's dwell waits on
## frame_post_draw, which never comes headless, so this measures just the swap and the visible window.
##   godot --headless --path . --audio-driver Dummy res://tools/gpu_bench/fight_entry_probe.tscn -- [--fights=...]
## Per fight: the F8 chapter start (its party), then BattleRequest.start as the walk does. Hidden = the frames until the
## battle scene is in and the reveal isn't held; visible = the frames until the router is idle, then VISIBLE_FRAMES
## more. Prints FIGHT_ENTRY <encounter> {hidden_max_ms, visible_max_ms, visible_max_frame, over_50}: the visible
## frame index says whether the spike is the first frame after the reveal (row 64's BattleBossIntro._frame_boss).

const CHAPTER_SELECT := "res://game/data/debug/chapter_select.json"
const VISIBLE_FRAMES := 60
const TIMEOUT_MS := 120000
const VISIBLE_MAX_MS := 50.0
## [encounter, chapter, return location]
const FIGHTS := [
	["ch01_scuttlers", "ch01", "ch01/oruvel"],
	["ch02_tideline", "ch02", "ch02/haluna"],
	["ch03_causeway_shore", "ch03", "ch03/saltgrass_causeway"],
	["drownbell", "ch03", "ch03/shell_shrine"],
	["ch04_bottle_hermit", "ch04", "ch04/brightwater_ferry"],
	["ch05_cinder_matron", "ch05", "ch05/ashcrown"],
	["ch06_inquisitor", "ch06", "ch06/brine_shoals"],
]

var _opts: Dictionary = {}


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := (get_script() as GDScript).new() as Node
		driver.name = "FightEntryProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else "true"
	var saves := get_tree().root.get_node_or_null(^"SaveSystem")
	if saves != null and saves.has_method(&"hold_autosave"):
		saves.call(&"hold_autosave", self)
	var wanted := str(_opts.get("fights", "")).split(",", false)
	var router := get_tree().root.get_node(^"SceneRouter")
	for f: Array in FIGHTS:
		if not wanted.is_empty() and not wanted.has(str(f[0])):
			continue
		for start: Dictionary in DebugReadouts.chapter_starts(CHAPTER_SELECT):
			if str(start["id"]) == str(f[1]):
				DebugReadouts.apply_chapter_start(start)
		var swapped := [false]
		var on_swap := func(_p: String) -> void: swapped[0] = true
		EventBus.scene_changed.connect(on_swap)
		BattleRequest.start(StringName(str(f[0])), StringName(str(f[2])), &"")
		var hidden := await _frames_until(
			func() -> bool:
				return (
					bool(swapped[0])
					and get_tree().current_scene is FieldBattle
					and (router.call(&"reveal_holders") as Array).is_empty()
				)
		)
		EventBus.scene_changed.disconnect(on_swap)
		var visible := await _frames_until(func() -> bool: return not bool(router.call(&"is_busy")))
		visible.append_array(await _frames(VISIBLE_FRAMES))
		var vmax := 0.0
		var vat := -1
		var over := 0
		for i in visible.size():
			if visible[i] > vmax:
				vmax = visible[i]
				vat = i
			if visible[i] > VISIBLE_MAX_MS:
				over += 1
		var out := {
			"hidden_max_ms": snappedf(_max(hidden), 0.1),
			"visible_max_ms": snappedf(vmax, 0.1),
			"visible_max_frame": vat,
			"over_50": over,
			"first_visible_ms": Array(visible.slice(0, 6)).map(func(v: float) -> float: return snappedf(v, 0.1)),
		}
		print("FIGHT_ENTRY %s %s" % [f[0], JSON.stringify(out)])
		# Leave the fight for the title-less void: back to the field location, then the next.
		FlowRouting.go_to(StringName(str(f[2])), &"")
		await _frames_until(
			func() -> bool: return not (get_tree().current_scene is FieldBattle) and not bool(router.call(&"is_busy"))
		)
	get_tree().quit()


static func _max(a: PackedFloat64Array) -> float:
	var m := 0.0
	for v in a:
		m = maxf(m, v)
	return m


func _frames_until(done: Callable) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	var start := Time.get_ticks_msec()
	var prev := Time.get_ticks_usec()
	while not bool(done.call()) and Time.get_ticks_msec() - start < TIMEOUT_MS:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		out.append(float(now - prev) / 1000.0)
		prev = now
	return out


func _frames(n: int) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	var prev := Time.get_ticks_usec()
	for i in n:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		out.append(float(now - prev) / 1000.0)
		prev = now
	return out
