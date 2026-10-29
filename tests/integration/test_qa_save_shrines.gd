extends TestCase
## Integration QA (M3-HER-1121): a save round trip at every save shrine in the slice and Act I. Each real zone
## (HeroGuardSources) is loaded as the game loads it; every SaveShrine in it is rested at (menu off), as the player
## does, and then:
## - the shrine names a respawn spawn, that spawn exists in the zone, and it is within REACH_M of the shrine (a load
##   puts Rhen back beside it);
## - the location it records resolves (locations.json) to this same zone scene;
## - the state saved to a slot loads back identical: flags, party and reserve, the respawn point, everything in
##   GameStateData.to_dict().
## Game.state and SaveSystem.save_dir are restored afterwards; the saves go to a scratch folder.

const SAVE_DIR := "user://test_qa_save_shrines"
const SLOT := 3
## Shrines whose respawn spawn is missing or in another zone, already handed to their owner:
## "<zone file>/<shrine>" -> task. Reported, not failed, until the fix lands.
const KNOWN_SPAWNS := {
	"haluna_wake.tscn/SaveShrine": "M3-HER-1154 (act1-chapters: no Shrine spawn; respawns in ch02/haluna)",
}
## How far from the shrine its respawn spawn may be (metres, on the ground).
const REACH_M := 8.0
const QA_FLAG := &"save_shrine_used"


func test_every_shrine_saves_and_loads_back_where_it_stands() -> void:
	var state_was := Game.state
	var dir_was: String = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	var by_path := {}
	for loc: String in HeroGuardSources.scenes_by_location():
		by_path[HeroGuardSources.scenes_by_location()[loc]] = loc
	var shrines := 0
	for path in HeroGuardSources.field_zones():
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		_host().add_child(zone)
		for n in zone.find_children("*", "Area3D", true, false):
			if n is SaveShrine:
				shrines += 1
				_round_trip(zone, n as SaveShrine, path, by_path)
		zone.free()
	Game.state = state_was
	SaveSystem.save_dir = dir_was
	_clear(SAVE_DIR)
	print("  save shrines checked: %d" % shrines)
	assert_true(shrines > 0, "the zones have save shrines (%d checked)" % shrines)


func _round_trip(zone: Node3D, shrine: SaveShrine, path: String, by_path: Dictionary) -> void:
	var where := "%s/%s" % [path.get_file(), shrine.name]
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	Game.state.reserve_ids = [&"ysolde"] as Array[StringName]
	Game.state.location_id = StringName(str(by_path.get(path, "")))
	Game.state = SaveSystem.deserialize(SaveSystem.serialize(Game.state))  # as a loaded game is (its starting gear)
	shrine.opens_menu = false
	shrine.rest()
	assert_true(bool(Game.get_flag(QA_FLAG)), "%s: resting raises %s" % [where, QA_FLAG])
	var spawn := Game.state.respawn_spawn
	assert_true(spawn != &"", "%s: names a respawn spawn" % where)
	var marker := zone.call(&"spawn_marker", spawn) as Node3D if zone.has_method(&"spawn_marker") else null
	if marker == null and KNOWN_SPAWNS.has(where):
		print("  KNOWN missing respawn spawn %s '%s': %s" % [where, spawn, KNOWN_SPAWNS[where]])
	else:
		assert_true(marker != null, "%s: its respawn spawn '%s' exists in the zone" % [where, spawn])
	if marker != null:
		var flat := (
			Vector2(
				marker.global_position.x - shrine.global_position.x, marker.global_position.z - shrine.global_position.z
			)
			. length()
		)
		assert_true(flat <= REACH_M, "%s: the spawn is %.1f m from the shrine (at most %.1f)" % [where, flat, REACH_M])
	var loc_scene := str(HeroGuardSources.scenes_by_location().get(String(Game.state.respawn_location_id), ""))
	if loc_scene != path and KNOWN_SPAWNS.has(where):
		print("  KNOWN respawn location %s '%s': %s" % [where, Game.state.respawn_location_id, KNOWN_SPAWNS[where]])
	else:
		assert_eq(
			loc_scene, path, "%s: the respawn location '%s' is this zone" % [where, Game.state.respawn_location_id]
		)
	_save_load(where)


## Act I's rest points are beats (a layout Interactable "Rest" -> a chapter beat with {"zone": "rest"} and, where the
## chapter keeps a checkpoint, {"zone": "checkpoint", "args": [spawn]}). Each is run as ZoneStory runs it: every zone
## step must name a method the zone has (ZoneStory skips a missing one silently, so a typo would rest nobody); a
## checkpoint's spawn must exist in this zone; and the state must survive a save and load like a shrine's.
func test_every_act1_rest_point_rests_and_round_trips() -> void:
	var state_was := Game.state
	var dir_was: String = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	var by_path := {}
	for loc: String in HeroGuardSources.scenes_by_location():
		by_path[HeroGuardSources.scenes_by_location()[loc]] = loc
	var rests := 0
	for path in HeroGuardSources.field_zones():
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story == null:
			zone.free()
			continue
		story.autostart = false
		_host().add_child(zone)
		var beats := story.cfg.get("beats", {}) as Dictionary
		for id: String in beats:
			var steps: Array = (beats[id] as Dictionary).get("steps", [])
			if not steps.any(func(st: Variant) -> bool: return st is Dictionary and st.get("zone", "") == "rest"):
				continue
			rests += 1
			_rest_beat(zone, steps, path, by_path, "%s beat %s" % [path.get_file(), id])
		zone.free()
	Game.state = state_was
	SaveSystem.save_dir = dir_was
	_clear(SAVE_DIR)
	print("  Act I rest points checked: %d" % rests)
	assert_true(rests > 0, "Act I has rest points (%d checked)" % rests)


func _rest_beat(zone: Node3D, steps: Array, path: String, by_path: Dictionary, where: String) -> void:
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	Game.state.location_id = StringName(str(by_path.get(path, "")))
	Game.state = SaveSystem.deserialize(SaveSystem.serialize(Game.state))
	var checkpoint := false
	for st: Variant in steps:
		if not (st is Dictionary and (st as Dictionary).has("zone")):
			continue
		var method := StringName(str(st["zone"]))
		assert_true(zone.has_method(method), "%s: the zone has %s() (ZoneStory would skip it)" % [where, method])
		if zone.has_method(method):
			zone.callv(method, st.get("args", []))
		checkpoint = checkpoint or method == &"checkpoint"
	if checkpoint:
		var marker := zone.call(&"spawn_marker", Game.state.respawn_spawn) as Node3D
		assert_true(marker != null, "%s: its checkpoint spawn '%s' exists" % [where, Game.state.respawn_spawn])
		var loc_scene := str(HeroGuardSources.scenes_by_location().get(String(Game.state.respawn_location_id), ""))
		assert_eq(loc_scene, path, "%s: the checkpoint '%s' is this zone" % [where, Game.state.respawn_location_id])
	else:
		print("  NOTE %s rests the party but keeps no checkpoint (death returns to the last one)" % where)
	_save_load(where)


func _save_load(where: String) -> void:
	var before := Game.state.to_dict()
	assert_eq(SaveSystem.save_to_slot(SLOT, Game.state), OK, "%s: saves" % where)
	var loaded := SaveSystem.load_from_slot(SLOT)
	assert_true(loaded != null, "%s: loads back" % where)
	if loaded != null:
		var after := loaded.to_dict()
		for key: String in before:
			assert_eq(_canon(after.get(key)), _canon(before[key]), "%s: %s survives the round trip" % [where, key])


## `v` as the save file holds it: JSON's numbers (an int reads back as a float; the game reads uids with int()) and
## sorted keys, so only a real change in a value differs.
static func _canon(v: Variant) -> String:
	return JSON.stringify(JSON.parse_string(JSON.stringify(v)), "", true)


static func _clear(dir: String) -> void:
	for f in DirAccess.get_files_at(dir):
		DirAccess.remove_absolute(dir.path_join(f))


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
