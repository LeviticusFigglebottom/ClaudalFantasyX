extends TestCase
## Integration QA (M3-HER-1121): no capsule stand-ins where the human plays. Every real zone (the prologue and every
## chapter location, HeroGuardSources) is loaded as the game loads it, and every visible stand-in mesh (a node named
## StandIn: the stage actors' and the zone NPCs' capsules) is listed with its actor. In battle, every party member
## the chapter data seats must have an actor scene (battle_sandbox.json stand_ins.<id>.scene). A capsule already
## handed to its owner is listed in qa_known.json "capsules" (zone file name -> actor names) and reported, not failed.

const KNOWN := "res://tests/integration/qa_known.json"
const STANDIN := "StandIn"
const SANDBOX := "res://game/data/ui/battle_sandbox.json"
const CHAPTERS_DIR := "res://game/data/flow/chapters"
const ENCOUNTERS := "res://game/data/battle/encounters.json"
const ENEMIES := "res://game/data/battle/enemies.json"
const SKILLS := "res://game/data/battle/skills.json"
const VOWBOUND := "res://game/data/battle/vowbound.json"


func test_no_zone_shows_a_capsule_the_owners_do_not_know_of() -> void:
	var known := _json(KNOWN).get("capsules", {}) as Dictionary
	var state_was := Game.state  # a fresh state: no flags left by earlier tests pick a zone's variant
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var paths: Array[String] = HeroGuardSources.field_zones()
	var prologue := str(HeroGuardSources.scenes_by_location().get(HeroGuardSources.PROLOGUE_ID, ""))
	if prologue != "":
		paths.push_front(prologue)
	for path in paths:
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		if "autoplay" in zone:
			zone.set(&"autoplay", false)
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		_host().add_child(zone)
		var shown := capsules(zone)
		for flags in _variant_flags(zone):  # the zone as each layout variant shows it (Ch9's dawn road)
			var default_state := Game.state
			Game.state = GameStateData.new()
			Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
			for f in flags:
				Game.set_flag(StringName(f))
			zone.call(&"apply_variant")
			for who in capsules(zone):
				if not shown.has(who):
					shown.append(who)
			Game.state = default_state
		if zone.has_method(&"refresh_states") and "layout" in zone:  # each layout state's flag, in story order
			var default_state := Game.state
			Game.state = GameStateData.new()
			Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
			for row: Variant in (zone.get(&"layout") as Dictionary).get("states", []):
				var flag := str((row as Dictionary).get("flag", "")) if row is Dictionary else ""
				if flag == "":
					continue
				Game.set_flag(StringName(flag))
				zone.call(&"refresh_states")
				for who in capsules(zone):
					if not shown.has(who):
						shown.append(who)
			Game.state = default_state
		var listed: Array = known.get(path.get_file(), [])
		for who in shown:
			if listed.has(who):
				print("  KNOWN capsule %s: %s" % [path.get_file(), who])
			else:
				fail("%s shows %s as a capsule" % [path.get_file(), who])
		zone.free()
	Game.state = state_was


func test_every_party_member_has_a_battle_actor() -> void:
	var stand_ins := ((_json(SANDBOX).get("sandbox", {}) as Dictionary).get("stand_ins", {})) as Dictionary
	if stand_ins.is_empty():
		stand_ins = _find_key(_json(SANDBOX), "stand_ins") as Dictionary
	var known: Array = (_json(KNOWN).get("capsules", {}) as Dictionary).get("battle", [])
	for id in _party_ids():
		var row := stand_ins.get(id, {}) as Dictionary
		if str(row.get("scene", "")) != "":
			continue
		if known.has(id):
			print("  KNOWN capsule battle: %s" % id)
		else:
			fail("%s is a party member with no battle actor scene (battle_sandbox stand_ins)" % id)


## Every foe an encounter seats, every add a boss spawns or summons, and every Vowbound the party can call must
## have a real body: BattleStage.stand_in_spec(id) names a scene that exists (else FighterStandIn draws a primitive).
## The ones already assigned are in qa_known.json "capsules"."battle_foes" (id -> owner and task).
func test_every_foe_and_vowbound_has_a_body() -> void:
	var known := (_json(KNOWN).get("capsules", {}) as Dictionary).get("battle_foes", {}) as Dictionary
	var ids := battle_body_ids()
	assert_true(ids.size() > 10, "the encounters, spawns, summons and Vowbound are read (%d ids)" % ids.size())
	for id in ids:
		var scene := str(BattleStage.stand_in_spec(StringName(id)).get("scene", ""))
		if scene != "" and ResourceLoader.exists(scene):
			continue
		if known.has(id):
			print("  KNOWN capsule battle foe: %s (%s)" % [id, known[id]])
		else:
			fail("%s fights as a primitive stand-in (no actor scene in battle_sandbox or creatures)" % id)


## Every combatant id a battle can seat on the far side or call in: encounters.json enemies, enemies.json `spawn`
## lists, skills.json `summon`s and vowbound.json's Vowbound.
static func battle_body_ids() -> Array[String]:
	var out: Array[String] = []
	_collect_key(_json(ENCOUNTERS).get("encounters", {}), "enemies", out)
	_collect_key(_json(ENEMIES), "spawn", out)
	_collect_key(_json(SKILLS), "summon", out)
	for row: Variant in _json(VOWBOUND).get("vowbound", []):
		_add_ids([(row as Dictionary).get("id", "")], out)
	out.sort()
	return out


static func _collect_key(v: Variant, key: String, out: Array[String]) -> void:
	if v is Dictionary:
		for k: Variant in v:
			if str(k) == key:
				_add_ids(v[k] if v[k] is Array else [v[k]], out)
			else:
				_collect_key(v[k], key, out)
	elif v is Array:
		for x: Variant in v:
			_collect_key(x, key, out)


static func _add_ids(ids: Array, out: Array[String]) -> void:
	for id: Variant in ids:
		var s := str(id).get_slice("#", 0)
		if s != "" and not out.has(s):
			out.append(s)


## The flags of each of the zone layout's "variants" rows (`when.set`), when the zone applies variants.
static func _variant_flags(zone: Node) -> Array[Array]:
	var out: Array[Array] = []
	if not zone.has_method(&"apply_variant") or not "layout" in zone:
		return out
	for row: Variant in (zone.get(&"layout") as Dictionary).get("variants", []):
		var when := (row as Dictionary).get("when", {}) as Dictionary
		var flags: Array = when.get("set", [])
		if not flags.is_empty():
			out.append(flags)
	return out


## The visible stand-in capsules under `zone`, by their actor's name (the StandIn's parent).
static func capsules(zone: Node) -> Array[String]:
	var out: Array[String] = []
	for n in zone.find_children(STANDIN, "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		if g.is_visible_in_tree():
			var who := String(g.get_parent().name)
			if not out.has(who):
				out.append(who)
	out.sort()
	return out


## Every id the chapter files seat in a party or a reserve.
static func _party_ids() -> Array[String]:
	var out: Array[String] = []
	for file in DirAccess.get_files_at(CHAPTERS_DIR):
		if file.ends_with(".json"):
			_collect_party(_json(CHAPTERS_DIR.path_join(file)), out)
	out.sort()
	return out


static func _collect_party(v: Variant, out: Array[String]) -> void:
	if v is Dictionary:
		for k: Variant in v:
			if (str(k) == "party" or str(k) == "reserve") and v[k] is Array:
				for id: Variant in v[k]:
					if not out.has(str(id)):
						out.append(str(id))
			else:
				_collect_party(v[k], out)
	elif v is Array:
		for x: Variant in v:
			_collect_party(x, out)


static func _find_key(v: Variant, key: String) -> Variant:
	if v is Dictionary:
		if (v as Dictionary).has(key):
			return v[key]
		for k: Variant in v:
			var found: Variant = _find_key(v[k], key)
			if found != null:
				return found
	return null


static func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
