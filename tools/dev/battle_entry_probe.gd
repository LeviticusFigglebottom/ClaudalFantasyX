extends Node
## Integration QA: enter fights the way the player does, with real frames (the human's "Trying to cast a freed
## object" entering a fight). `godot --headless --path . res://tools/dev/battle_entry_probe.tscn [-- --chapters=2,3,1]`
## For each Act I encounter of the chosen chapters (test_qa_encounters.gd's homes): New Game, the SceneRouter changes
## to its zone at its spawn, BattleRequest.start opens the fight as the zone does (the stinger, the router's fade, the
## staged build), the party wins it (foes at 1 HP, attacked on the party's turns), the result is accepted and the
## router travels back. A QaLogger records every engine and script error; one PROBE line per fight, then the count.
## The driver lives under the tree's root, so the router's scene swaps don't free it.

const HOMES_SCRIPT := "res://tests/integration/test_qa_encounters.gd"
const WAIT_FRAMES := 900
const MAX_TURNS := 80
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]

var _chapters: Array[int] = [1, 2, 3]


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--chapters="):
			_chapters.clear()
			for c in arg.trim_prefix("--chapters=").split(","):
				_chapters.append(int(c))
	var driver := Node.new()
	driver.name = "BattleEntryProbe"
	driver.set_script(get_script())
	driver.set_meta(&"driver", true)
	if not has_meta(&"driver"):
		get_tree().root.add_child.call_deferred(driver)
		driver.set_meta(&"chapters", _chapters)
		return
	_run.call_deferred()


func _run() -> void:
	_chapters.assign(get_meta(&"chapters", _chapters))
	var qa := QaLogger.new()
	OS.add_logger(qa)
	var homes: Dictionary = (load(HOMES_SCRIPT) as GDScript).call(&"encounter_homes")
	var errors := 0
	for enc: String in homes:
		var home: Array = homes[enc]
		if not _chapters.has(str(home[0]).get_slice("/", 0).trim_prefix("ch").to_int()):
			continue
		Game.new_game()
		Game.state.party_ids = PARTY.duplicate()
		qa.take()
		var note := await _fight(StringName(enc), StringName(str(home[0])), StringName(str(home[1])), str(home[2]))
		var errs: Array[String] = []
		for e in qa.take():
			if e["kind"] != QaLogger.KIND_WARNING:
				errs.append("%s %s (%s)" % [e["kind"], e["text"], e["where"]])
		errors += errs.size()
		print(
			(
				"PROBE %s: %s%s"
				% [enc, note if note != "" else "clean", "" if errs.is_empty() else " | " + " | ".join(errs)]
			)
		)
	OS.remove_logger(qa)
	print("PROBE done: %d error(s)" % errors)
	get_tree().quit(1 if errors > 0 else 0)


func _fight(enc: StringName, location: StringName, spawn: StringName, zone_path: String) -> String:
	SceneRouter.change_scene(zone_path, spawn)
	if not await _until(func() -> bool: return _current_is(zone_path) and not SceneRouter.is_busy()):
		return "the zone never loaded"
	for i in 10:
		await get_tree().physics_frame
	BattleRequest.start(enc, location, spawn)
	if not await _until(func() -> bool: return get_tree().current_scene is FieldBattle and not SceneRouter.is_busy()):
		return "the battle never opened"
	var ctl := get_tree().current_scene as FieldBattle
	ctl.pacing_scale = 0.0
	if not await _until(func() -> bool: return ctl.engine != null and not ctl.building):
		return "the battle never built"
	var turns := 0
	for _f in WAIT_FRAMES:
		if turns >= MAX_TURNS or not is_instance_valid(ctl) or ctl.state == BattleController.STATE_RESULT:
			break
		for foe in ctl.engine.enemies:
			foe.hp = mini(foe.hp, 1)
		if ctl.state == BattleController.STATE_COMMAND and ctl.engine.current != null:
			var foes := ctl.engine.living_foes_of(ctl.engine.current)
			if not foes.is_empty():
				ctl.act(&"attack", [foes[0].id])
				turns += 1
		await get_tree().process_frame
	if not is_instance_valid(ctl) or ctl.state != BattleController.STATE_RESULT:
		return (
			"no result after %d attack(s) in %d frames (outcome '%s')"
			% [turns, WAIT_FRAMES, ctl.engine.outcome if is_instance_valid(ctl) else "?"]
		)
	ctl.hud.result.accept()
	if not await _until(func() -> bool: return _current_is(zone_path) and not SceneRouter.is_busy()):
		return "won, but never got back to the zone"
	for i in 30:
		await get_tree().physics_frame
	return ""


func _current_is(path: String) -> bool:
	var cs := get_tree().current_scene
	return cs != null and cs.scene_file_path == path


func _until(cond: Callable) -> bool:
	for i in WAIT_FRAMES:
		if cond.call():
			return true
		await get_tree().process_frame
	return false
