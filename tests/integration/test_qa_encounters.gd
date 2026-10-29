extends TestCase
## Integration QA: every Act I fight, entered from the field and back (the human hit "Trying to cast a freed object"
## entering a fight). For each encounter the Act I chapters name (encounters.json, the sandbox's aside), the guard
## builds the request the field builds (BattleRequest.make: the party, the zone and spawn to return to), opens the
## FieldBattle, wins it (every foe brought to 1 HP, then attacked), accepts the result, and loads the zone it returns
## to at its spawn, the party walking a few frames there. A QaLogger listens throughout: any engine error or script
## error (a freed object, a missing resource, a bad cast) fails it, unless qa_known.json "known" explains it. The party
## attacks, and where a set piece refuses that (Toma won't strike, the stair is held) uses a skill it accepts. Every
## fight, set pieces included, must be won (or end in its scripted escape) within MAX_TURNS.

const BATTLE := "res://game/flow/field_battle.tscn"
const ENCOUNTERS := "res://game/data/battle/encounters.json"
const CHAPTERS_DIR := "res://game/data/flow/chapters"
const LOCATIONS := "res://game/data/world/locations.json"
const KNOWN := "res://tests/integration/qa_known.json"
const SANDBOX_PREFIX := "sandbox"
const LAST_CHAPTER := 9
const MAX_TURNS := 80
const FIELD_FRAMES := 10
const DT := 1.0 / 60.0
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const RESERVE: Array[StringName] = [&"ysolde"]

var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_every_act1_fight_is_entered_won_and_left_clean() -> void:
	var known := _known()
	var qa := QaLogger.new()
	OS.add_logger(qa)
	var homes := encounter_homes()
	var fought := 0
	for enc_id: String in homes:
		Game.state = GameStateData.new()
		Game.state.party_ids = PARTY.duplicate()
		Game.state.reserve_ids = RESERVE.duplicate()
		var home: Array = homes[enc_id]
		qa.take()
		var result := _fight(StringName(enc_id), StringName(str(home[0])), StringName(str(home[1])))
		assert_eq(result, "", "%s is won" % enc_id)
		_return_to(str(home[2]), StringName(str(home[1])))
		for e in qa.take():
			if _match(known, str(e["text"])) != "" or e["kind"] == QaLogger.KIND_WARNING:
				continue
			fail("%s: %s %s (%s)" % [enc_id, e["kind"], e["text"], e["where"]])
		fought += 1
	OS.remove_logger(qa)
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	Game.state = _state_was
	print("  Act I fights entered and left: %d" % fought)
	assert_true(fought > 20, "the Act I encounters were found (%d)" % fought)


## Opens `enc` as the field does, wins it and accepts the result. Returns "" or a note.
func _fight(enc: StringName, location: StringName, spawn: StringName) -> String:
	BattleRequest.change_scene = func(_p: String) -> void: pass
	var r := BattleRequest.make(enc, location, spawn)
	BattleRequest.submit(r)
	var ctl := (load(BATTLE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.travel = func(_loc: StringName, _sp: StringName) -> bool: return true
	ctl.open_title = func(_p: String) -> void: pass
	ctl.save_system = SaveSystem
	_host().add_child(ctl)
	ctl.start_sandbox()
	var note := ""
	if ctl.engine == null:
		note = "the battle did not build"
	else:
		for _i in MAX_TURNS:
			if ctl.state == BattleController.STATE_RESULT:
				break
			rig(ctl.engine)
			if ctl.engine.current == null or not _take_turn(ctl):
				break
		if ctl.state == BattleController.STATE_RESULT:
			if ctl.engine.outcome == BattleEngine.OUTCOME_DEFEAT:
				note = "lost (the party fell)"
			ctl.hud.result.accept()
		else:
			note = "did not end by attack within %d turns (outcome '%s')" % [MAX_TURNS, ctl.engine.outcome]
	_host().remove_child(ctl)
	ctl.free()
	return note


## Tips each turn the drivers' way: every foe at 1 HP, every standing party member at full (a set piece's tide must
## not win before its objective is met).
static func rig(engine: BattleEngine) -> void:
	for foe in engine.enemies:
		foe.hp = mini(foe.hp, 1)
	for hero in engine.party_active:
		if hero.hp > 0:
			hero.hp = hero.max_hp


## The current party member acts: Attack on the first foe that takes it, else (a set piece refuses it: Toma won't
## strike, a stair is held) its first skill the engine accepts, on a foe, the ward, itself or no one. False if none.
static func _take_turn(ctl: FieldBattle) -> bool:
	var actor := ctl.engine.current
	var foes := ctl.engine.living_foes_of(actor)
	var targets: Array = []
	for f in foes:
		targets.append([f.id] as Array[StringName])
	var ward := ctl.engine.ward()
	if ward != null:
		targets.append([ward.id] as Array[StringName])
	targets.append([actor.id] as Array[StringName])
	targets.append([] as Array[StringName])
	var tries: Array[StringName] = [&"attack"]
	tries.append_array(actor.skills)
	for skill in tries:
		for t: Array[StringName] in targets:
			if ctl.act(skill, t).ok:
				return true
	return false


## Loads the zone the fight returns to at `spawn` and lets the party walk a few frames there.
func _return_to(scene_path: String, spawn: StringName) -> void:
	if scene_path == "" or not ResourceLoader.exists(scene_path):
		return
	var zone := (load(scene_path) as PackedScene).instantiate() as Node3D
	var story := zone.get(&"story") as ZoneStory if "story" in zone else null
	if story != null:
		story.autostart = false
	_host().add_child(zone)
	if zone.has_method(&"place_at") and zone.has_method(&"spawn_yaw_deg"):
		zone.call(&"place_at", spawn, zone.call(&"spawn_yaw_deg", spawn))
	var player: FieldController = null
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			player = n
	if player != null:
		player.set_physics_process(false)
		player.set_process_unhandled_input(false)
		var party := player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
		if party != null:
			party.set_physics_process(false)
		player.input_override = Vector2(0, -1)
		for i in FIELD_FRAMES:
			player.step(DT)
			if party != null:
				party.advance(DT)
	_host().remove_child(zone)
	zone.free()


## Encounter id -> [location id, spawn, scene path] of the zone it is fought from: the chapter file's zone that names
## it, else the first location of its chapter (chNN in the id). The sandbox's are left out.
static func encounter_homes() -> Dictionary:
	var scenes := {}
	var first_of_chapter := {}
	for row: Variant in _json(LOCATIONS).get("locations", []):
		var id := str((row as Dictionary).get("id", ""))
		scenes[id] = str((row as Dictionary).get("scene", ""))
		var ch := id.get_slice("/", 0)
		if ch.begins_with("ch") and not first_of_chapter.has(ch):
			first_of_chapter[ch] = id
	var named := {}  # encounter -> location
	for file in DirAccess.get_files_at(CHAPTERS_DIR):
		if not file.ends_with(".json"):
			continue
		var zones := _json(CHAPTERS_DIR.path_join(file)).get("zones", {}) as Dictionary
		for loc: String in zones:
			_names_in(zones[loc], loc, named)
	var out := {}
	for enc: Variant in _json(ENCOUNTERS).get("encounters", []):
		var id := str((enc as Dictionary).get("id", ""))
		if id.begins_with(SANDBOX_PREFIX):
			continue
		var loc := str(named.get(id, first_of_chapter.get(id.get_slice("_", 0), "")))
		if loc == "":
			loc = "ch02/haluna" if id == "drownbell" else ""
		var chapter := loc.get_slice("/", 0).trim_prefix("ch").to_int()
		if loc == "" or chapter > LAST_CHAPTER:
			continue
		out[id] = [loc, _first_spawn(str(scenes.get(loc, ""))), str(scenes.get(loc, ""))]
	return out


static func _names_in(v: Variant, loc: String, named: Dictionary) -> void:
	if v is Dictionary:
		for k: Variant in v:
			_names_in(v[k], loc, named)
	elif v is Array:
		for x: Variant in v:
			_names_in(x, loc, named)
	elif v is String and not named.has(v):
		named[v] = loc


static func _first_spawn(scene_path: String) -> String:
	var layout_path := scene_path.trim_suffix(".tscn") + "_layout.json"
	var spawns: Variant = _json(layout_path).get("spawns", {})
	if spawns is Dictionary and not (spawns as Dictionary).is_empty():
		return str((spawns as Dictionary).keys()[0])
	return ""


static func _known() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for row: Variant in _json(KNOWN).get("known", []):
		var re := RegEx.new()
		if re.compile(str((row as Dictionary).get("pattern", ""))) == OK:
			out.append({"re": re, "task": str((row as Dictionary).get("task", ""))})
	return out


static func _match(known: Array[Dictionary], text: String) -> String:
	for k in known:
		if (k["re"] as RegEx).search(text) != null:
			return str(k["task"])
	return ""


static func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
