class_name ReturnProbe
extends Node
## Human playtest check (a), 2026-10-30 (cloud QA pass 6): the battle-victory → field return, as played.
##   godot --headless --path . --audio-driver Dummy res://tools/gpu_bench/return_probe.tscn -- [--cases=tideline,...]
## Per case: the F8 chapter start (the story so far and the party), the field location, the story flags the fight
## needs, then the fight asked for as the zone asks (a random encounter returns to "Encounter" where Rhen stood).
## The fight plays live (foes held at 1 HP, Attack on the first foe each party turn, ui_accept tapped through tips).
## At the result panel the probe waits RESULT_READ_S (a player reading it), then presses Return: t0, the victory
## exit. From t0 it holds field_move_forward and taps ui_accept every PRESS_EVERY_S once the field is shown (a
## post-battle line is read through), and records per frame the router's fade alpha, the current scene and the
## hero's position. It prints RETURN_PROBE <case> {json}:
##   black_ms        frames with the fade fully opaque (alpha >= BLACK_ALPHA) after t0
##   covered_ms      t0 → the fade fully lifted on the field scene (alpha <= CLEAR_ALPHA)
##   field_in_ms     t0 → the field scene is the current scene
##   ready_ms        t0 → the field is visible and takes input (fade clear, router idle, the hero's
##                   FieldController.accepts_input, the zone story free, the tree not paused)
##   moved_ms        t0 → the held stick first moves the hero (>= MOVE_M)
## Headless, so the timings are CPU-side (load, instance, script): no draw cost.

const CHAPTER_SELECT := "res://game/data/debug/chapter_select.json"
const BLACK_ALPHA := 0.99
const CLEAR_ALPHA := 0.01
const MOVE_M := 0.05
const PRESS_EVERY_S := 1.5
const RESULT_READ_S := 1.0
const BATTLE_TIMEOUT_S := 240.0
const RETURN_TIMEOUT_S := 60.0
const SETTLE_S := 2.0
const ENCOUNTER_SPAWN := &"Encounter"
## [case, chapter start, location, spawn, flags to set, encounter, return spawn ("" = Encounter, random), victory flag,
## party override].
const CASES := [
	[
		"tideline",
		"ch02",
		"ch02/haluna",
		"Village",
		["ch02_met_asha"],
		"ch02_tideline",
		"BattleReturn",
		"ch02_tideline_won",
		[]
	],
	[
		"causeway",
		"ch03",
		"ch03/saltgrass_causeway",
		"FromHaluna",
		["ch03_harrier_won"],
		"ch03_causeway_shore",
		"",
		"",
		[]
	],
	[
		"drownbell",
		"ch03",
		"ch03/shell_shrine",
		"",
		[],
		"drownbell",
		"DockNight",
		"ch03_drownbell_defeated",
		["rhen", "asha", "toma"],
		"ch02/haluna"
	],
	[
		"oruvel_scuttlers",
		"ch01",
		"ch01/oruvel",
		"",
		["ch01_gulls_cried"],
		"ch01_scuttlers",
		"AfterScuttlers",
		"ch01_scuttlers_won",
		["rhen"]
	],
	[
		"ch04_ferry",
		"ch04",
		"ch04/brightwater_ferry",
		"",
		["ch04_boarded_derelict"],
		"ch04_derelict_leeches",
		"",
		"",
		[]
	],
	["ch06", "ch06", "ch06/brine_shoals", "", ["ch06_arrived"], "ch06_ridge_skippers", "", "", []],
]

var _opts: Dictionary = {}


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := ReturnProbe.new()
		driver.name = "ReturnProbeDriver"
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
	var wanted := str(_opts.get("cases", "")).split(",", false)
	for c: Array in CASES:
		if wanted.is_empty() or wanted.has(str(c[0])):
			await _case(c)
	get_tree().quit()


func _router() -> Node:
	return get_tree().root.get_node(^"SceneRouter")


func _case(c: Array) -> void:
	var id := str(c[0])
	var router := _router()
	for start: Dictionary in DebugReadouts.chapter_starts(CHAPTER_SELECT):
		if str(start["id"]) == str(c[1]):
			DebugReadouts.apply_chapter_start(start)
	for f: String in c[4]:
		Game.set_flag(StringName(f))
	FlowRouting.go_to(StringName(str(c[2])), StringName(str(c[3])))
	await _until(func() -> bool: return _player() != null and not bool(router.call(&"is_busy")), 60.0)
	await _seconds(SETTLE_S)
	var loc := StringName(str(c[2]))
	var spawn := StringName(str(c[6]))
	if c.size() > 9:
		loc = StringName(str(c[9]))
	if spawn == &"":
		spawn = ENCOUNTER_SPAWN
		var p := _player()
		if p != null:
			FieldEncounters.return_points[String(loc)] = p.position
	var r := BattleRequest.make(StringName(str(c[5])), loc, spawn, StringName(str(c[7])))
	if not (c[8] as Array).is_empty():
		r.active = FirstPlayableConfig.ids(c[8])
		r.reserve = []
	BattleRequest.submit(r)
	var started := Time.get_ticks_msec()
	await _until(func() -> bool: return get_tree().current_scene is FieldBattle, 60.0)
	var ctl := get_tree().current_scene as FieldBattle
	if ctl == null:
		print('RETURN_PROBE %s {"error": "no battle"}' % id)
		return
	# Play it out.
	var next_tap := 0.0
	var t_start := Time.get_ticks_msec()
	while ctl.state != BattleController.STATE_RESULT:
		if float(Time.get_ticks_msec() - t_start) / 1000.0 > BATTLE_TIMEOUT_S:
			print('RETURN_PROBE %s {"error": "battle timeout", "state": "%s"}' % [id, ctl.state])
			return
		if ctl.engine != null:
			for foe in ctl.engine.enemies:
				foe.hp = mini(foe.hp, 1)
			if ctl.state == BattleController.STATE_COMMAND and ctl.engine.is_party_turn():
				var foes := ctl.engine.living_foes_of(ctl.engine.current)
				if not foes.is_empty():
					ctl.act(&"attack", [foes[0].id])
		var now := float(Time.get_ticks_msec() - t_start) / 1000.0
		if now >= next_tap and ctl.state not in [BattleController.STATE_COMMAND, BattleController.STATE_TARGET]:
			_tap(&"ui_accept")
			next_tap = now + PRESS_EVERY_S
		await get_tree().process_frame
	var fight_ms := Time.get_ticks_msec() - started
	await _seconds(RESULT_READ_S)
	# t0: Return on the result panel (the victory exit).
	var t0 := Time.get_ticks_usec()
	ctl.hud.result.accept()
	Input.action_press(&"field_move_forward")
	var black_ms := 0.0
	var max_frame_ms := 0.0
	var covered := -1.0
	var field_in := -1.0
	var ready := -1.0
	var moved := -1.0
	var start_pos := Vector3.INF
	var prev := t0
	var tap_at := -1.0
	var scenes: Array[String] = []
	while true:
		await get_tree().process_frame
		var now_us := Time.get_ticks_usec()
		var frame_ms := float(now_us - prev) / 1000.0
		prev = now_us
		var t := float(now_us - t0) / 1000.0
		var alpha := float(router.call(&"fade_alpha"))
		if alpha >= BLACK_ALPHA:
			black_ms += frame_ms
		var cur := get_tree().current_scene
		var path := cur.scene_file_path if cur != null else "-"
		if scenes.is_empty() or scenes.back() != path:
			scenes.append(path)
		var p := _player()
		var on_field := p != null and not (cur is FieldBattle)
		if on_field:
			max_frame_ms = maxf(max_frame_ms, frame_ms)
			if field_in < 0.0:
				field_in = t
			if covered < 0.0 and alpha <= CLEAR_ALPHA:
				covered = t
			if start_pos == Vector3.INF:
				start_pos = p.global_position
			if ready < 0.0 and alpha <= CLEAR_ALPHA and _input_live(p, cur, router):
				ready = t
			if moved < 0.0 and p.global_position.distance_to(start_pos) >= MOVE_M:
				moved = t
			if covered >= 0.0:
				if tap_at < 0.0 or t >= tap_at:
					_tap(&"ui_accept")
					tap_at = t + PRESS_EVERY_S * 1000.0
		if (ready >= 0.0 and moved >= 0.0) or t > RETURN_TIMEOUT_S * 1000.0:
			break
	Input.action_release(&"field_move_forward")
	var out := {
		"encounter": str(c[5]),
		"return": "%s/%s" % [loc, spawn],
		"fight_ms": fight_ms,
		"black_ms": roundi(black_ms),
		"field_in_ms": roundi(field_in),
		"covered_ms": roundi(covered),
		"ready_ms": roundi(ready),
		"moved_ms": roundi(moved),
		"worst_field_frame_ms": roundi(max_frame_ms),
		"scenes": scenes,
		"swap": router.get(&"last_swap_stats"),
	}
	print("RETURN_PROBE %s %s" % [id, JSON.stringify(out)])
	await _seconds(SETTLE_S)


func _input_live(p: FieldController, cur: Node, router: Node) -> bool:
	if bool(router.call(&"is_busy")) or get_tree().paused or not p.accepts_input:
		return false
	var story: Variant = cur.get(&"story")
	if story is ZoneStory and not (story as ZoneStory).is_free():
		return false
	return true


func _player() -> FieldController:
	var cur := get_tree().current_scene
	if cur == null:
		return null
	if cur.get(&"player") is FieldController:
		return cur.get(&"player") as FieldController
	var found := cur.find_children("*", "FieldController", true, false)
	return found[0] as FieldController if not found.is_empty() else null


func _tap(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event(up)


func _seconds(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _until(done: Callable, timeout_s: float) -> void:
	var start := Time.get_ticks_msec()
	while not bool(done.call()) and float(Time.get_ticks_msec() - start) / 1000.0 < timeout_s:
		await get_tree().process_frame
