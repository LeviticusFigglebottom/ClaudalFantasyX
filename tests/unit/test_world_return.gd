extends TestCase
## M1-ARC-06: the location registry and return-to-world on load. Fixture zones are built here,
## packed and saved under user://, and listed in a registry made from a dictionary, so nothing
## depends on real level content. The router swap itself is async (SceneRouter.change_scene); the
## tests replace WorldReturn.change_scene with a recorder and place the player synchronously.

const TEST_DIR := "user://test_world_return"
const ZONE_A := "user://test_world_return/zone_a.tscn"
const ZONE_B := "user://test_world_return/zone_b.tscn"
const GATE_POS := Vector3(3.0, 0.0, -2.0)
const GATE_YAW_DEG := 90.0
const DOCK_POS := Vector3(-4.0, 1.0, 6.0)
const REAL_ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"

var swaps: Array[Array] = []
var loaded_slots: Array[int] = []
var wr: WorldReturn
var _saved_state: GameStateData
var _saved_dir := ""
var _saved_clock := true


func before_each() -> void:
	_saved_state = Game.state
	_saved_dir = SaveSystem.save_dir
	_saved_clock = Game.play_clock_running
	Game.state = GameStateData.new()
	DirAccess.make_dir_recursive_absolute(TEST_DIR)
	_save_zone(ZONE_A, true)
	_save_zone(ZONE_B, false)
	wr = WorldReturn.new()
	wr.registry = LocationRegistry.from_dict(_registry_doc())
	wr.change_scene = func(path: String, spawn: StringName) -> void: swaps.append([path, spawn])
	_host().add_child(wr)


func _registry_doc() -> Dictionary:
	return {
		"default_location": "zone_a",
		"new_game": {"location_id": "zone_b", "spawn": "Dock"},
		"locations":
		[
			{"id": "zone_a", "scene": ZONE_A, "spawn": "Gate", "name_key": "LOCATION_FIELD_TEST"},
			{"id": "zone_b", "scene": ZONE_B, "spawn": "Dock", "name_key": "LOCATION_FIELD_TEST"},
		],
		"shrines": [{"id": "b_shrine", "location_id": "zone_b", "spawn": ""}],
	}


## Zone A has a child named Player; zone B's hero is only in the "player" group.
func _save_zone(path: String, named_player: bool) -> void:
	var root := Node3D.new()
	root.name = "Zone"
	var spawns := Node3D.new()
	spawns.name = "Spawns"
	root.add_child(spawns)
	spawns.owner = root
	for m: Array in [["Gate", GATE_POS, GATE_YAW_DEG], ["Dock", DOCK_POS, 0.0]]:
		var marker := Marker3D.new()
		marker.name = str(m[0])
		marker.position = m[1]
		marker.rotation.y = deg_to_rad(float(m[2]))
		spawns.add_child(marker)
		marker.owner = root
	var hero := Node3D.new()
	hero.name = "Player" if named_player else "Hero"
	if not named_player:
		hero.add_to_group(WorldReturn.PLAYER_GROUP, true)
	root.add_child(hero)
	hero.owner = root
	var packed := PackedScene.new()
	packed.pack(root)
	ResourceSaver.save(packed, path)
	root.free()


func _instance(path: String) -> Node3D:
	var zone := (ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene).instantiate()
	_host().add_child(zone)
	return zone as Node3D


func test_registry_lookups() -> void:
	var reg := wr.registry
	assert_eq(reg.location_ids(), [&"zone_a", &"zone_b"] as Array[StringName])
	assert_eq(reg.scene_of(&"zone_b"), ZONE_B)
	assert_eq(reg.spawn_of(&"zone_a"), &"Gate")
	assert_eq(reg.name_key_of(&"zone_a"), "LOCATION_FIELD_TEST")
	assert_eq(reg.new_game_location, &"zone_b")
	assert_eq(reg.new_game_spawn, &"Dock")
	assert_eq(reg.shrine_point(&"b_shrine"), {"location_id": &"zone_b", "spawn": &"Dock"}, "empty spawn = location's")
	assert_eq(reg.shrine_point(&"nope"), {})
	_done()


func test_resolve_prefers_respawn_then_location_then_default() -> void:
	Game.state.respawn_location_id = &"zone_b"
	Game.state.respawn_spawn = &"Gate"
	Game.state.location_id = &"zone_a"
	assert_eq(wr.resolve(Game.state)["spawn"], &"Gate", "the saved spawn wins")
	assert_eq(wr.resolve(Game.state)["scene"], ZONE_B)
	Game.state.respawn_location_id = &""
	assert_eq(wr.resolve(Game.state)["location_id"], &"zone_a", "no respawn: the current location")
	assert_eq(wr.resolve(Game.state)["spawn"], &"Gate")
	Game.state.location_id = &"ch99/gone"
	var to := wr.resolve(Game.state)
	assert_eq(to["location_id"], &"zone_a", "unknown: the registry default")
	assert_true(bool(to["fallback"]))
	assert_eq(LocationRegistry.from_dict({}).resolve(&"x"), {}, "nothing resolves in an empty registry")
	_done()


func test_disabled_world_return_ignores_loads() -> void:
	Game.state.respawn_location_id = &"zone_b"
	EventBus.game_loaded.emit(3)
	assert_eq(swaps, [] as Array[Array], "the test runner and captures never change scene")
	assert_false(SceneRouter.world_return.enabled, "the router's copy is unarmed outside boot")
	assert_true(SceneRouter.world_return is WorldReturn)
	_done()


func test_enabled_world_return_routes_the_load_to_the_respawn_scene() -> void:
	wr.enabled = true
	Game.state.respawn_location_id = &"zone_b"
	Game.state.respawn_spawn = &"Gate"
	EventBus.game_loaded.emit(3)
	assert_eq(swaps, [[ZONE_B, &"Gate"]] as Array[Array])
	assert_eq(Game.state.location_id, &"zone_b", "the party is now there")
	_done()


func test_continue_from_a_save_file_lands_on_the_saved_spawn() -> void:
	SaveSystem.save_dir = TEST_DIR
	var s := GameStateData.new()
	s.location_id = &"zone_a"
	s.respawn_location_id = &"zone_a"
	s.respawn_spawn = &"Dock"
	assert_eq(SaveSystem.save_to_slot(1, s), OK)
	wr.enabled = true
	assert_eq(SaveSystem.load_into_game(1), OK)
	assert_eq(swaps, [[ZONE_A, &"Dock"]] as Array[Array])
	var zone := _instance(str(swaps[0][0]))
	assert_true(WorldReturn.place_player(zone, swaps[0][1]))
	var player := zone.get_node("Player") as Node3D
	assert_true(player.global_position.is_equal_approx(DOCK_POS), "placed on the Dock marker")
	zone.free()
	SaveSystem.delete_slot(1)
	_done()


func test_place_player_uses_marker_position_and_yaw() -> void:
	var zone := _instance(ZONE_A)
	assert_true(WorldReturn.place_player(zone, &"Gate"))
	var player := zone.get_node("Player") as Node3D
	assert_true(player.global_position.is_equal_approx(GATE_POS))
	assert_between(rad_to_deg(player.rotation.y), GATE_YAW_DEG - 0.01, GATE_YAW_DEG + 0.01)
	assert_false(WorldReturn.place_player(zone, &"Attic"), "unknown spawn")
	assert_false(WorldReturn.place_player(zone, &""), "no spawn named")
	assert_false(WorldReturn.place_player(null, &"Gate"))
	zone.free()
	_done()


func test_place_player_finds_the_player_group() -> void:
	var zone := _instance(ZONE_B)
	assert_true(WorldReturn.place_player(zone, &"Dock"))
	assert_true((zone.get_node("Hero") as Node3D).global_position.is_equal_approx(DOCK_POS))
	zone.free()
	_done()


func test_place_player_without_a_player_fails() -> void:
	var zone := _instance(ZONE_B)
	zone.get_node("Hero").remove_from_group(WorldReturn.PLAYER_GROUP)
	assert_false(WorldReturn.place_player(zone, &"Dock"))
	zone.free()
	_done()


func test_go_to_sends_new_game_and_teleports_through_the_registry() -> void:
	assert_true(wr.go_to(&"zone_b"))
	assert_eq(swaps, [[ZONE_B, &"Dock"]] as Array[Array])
	assert_true(wr.go_to(&"nowhere"), "unknown ids fall back to the default")
	assert_eq(swaps[1], [ZONE_A, &"Gate"])
	wr.registry = LocationRegistry.from_dict({})
	assert_false(wr.go_to(&"zone_b"))
	_done()


func test_without_a_swap_or_router_nothing_happens() -> void:
	var lone := WorldReturn.new()
	lone.registry = wr.registry
	assert_false(lone.go_to(&"zone_a"), "no change_scene and no router parent")
	lone.free()
	_done()


func test_real_registry_places_the_player_in_the_shrine_zone() -> void:
	var reg := LocationRegistry.load_default()
	var to := reg.resolve(reg.default_location)
	assert_eq(to["scene"], REAL_ZONE)
	var zone := (load(REAL_ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	(zone.get_node("Player") as Node).set_physics_process(false)
	assert_true(WorldReturn.place_player(zone, to["spawn"]), "the zone's own place_at")
	var marker := zone.get_node("Spawns/%s" % to["spawn"]) as Node3D
	assert_true((zone.get_node("Player") as Node3D).global_position.is_equal_approx(marker.global_position))
	_host().remove_child(zone)
	zone.free()
	_done()


## M1-ARC-11 (QA review-sweep-F S2 on M1-ARC-06): Continue from a location that is not in the
## registry (not added yet, or renamed) warns, goes to the default, and keeps the saved location,
## so the next save does not record the stand-in level. The respawn survives as well.
func test_continue_from_an_unregistered_location_warns_and_keeps_it() -> void:
	SaveSystem.save_dir = TEST_DIR
	var s := GameStateData.new()
	s.location_id = &"ch02/haluna"
	s.respawn_location_id = &"ch02/haluna"
	s.respawn_spawn = &"Pier"
	assert_eq(SaveSystem.save_to_slot(1, s), OK)
	wr.enabled = true
	var tally := _WarningTally.new()
	OS.add_logger(tally)
	assert_eq(SaveSystem.load_into_game(1), OK)
	OS.remove_logger(tally)
	assert_eq(swaps, [[ZONE_A, &"Gate"]] as Array[Array], "the registry default stands in")
	assert_eq(tally.matching("ch02/haluna"), 1, "the fallback is reported, naming the missing location")
	assert_eq(Game.state.location_id, &"ch02/haluna", "the saved location is kept")
	assert_eq(Game.state.respawn_location_id, &"ch02/haluna", "and so is the respawn")
	assert_eq(SaveSystem.save_to_slot(2, Game.state), OK)
	assert_eq(SaveSystem.slot_info(2)["location_id"], "ch02/haluna", "the next save records the real place")
	SaveSystem.delete_slot(1)
	SaveSystem.delete_slot(2)
	_done()


func test_go_to_an_unknown_location_keeps_the_state_location() -> void:
	Game.state.location_id = &"zone_b"
	var tally := _WarningTally.new()
	OS.add_logger(tally)
	assert_true(wr.go_to(&"nowhere"))
	OS.remove_logger(tally)
	assert_eq(tally.matching("nowhere"), 1, "warned")
	assert_eq(Game.state.location_id, &"zone_b", "the default is not recorded as the location")
	assert_true(wr.go_to(&"zone_a"))
	assert_eq(Game.state.location_id, &"zone_a", "a resolved travel still records it")
	_done()


func test_an_empty_location_uses_the_default_without_a_warning() -> void:
	wr.enabled = true
	Game.state.location_id = &""
	Game.state.respawn_location_id = &""
	var tally := _WarningTally.new()
	OS.add_logger(tally)
	EventBus.game_loaded.emit(3)
	OS.remove_logger(tally)
	assert_eq(swaps, [[ZONE_A, &"Gate"]] as Array[Array], "the documented default for no location")
	assert_eq(tally.matching("WorldReturn"), 0, "no warning: nothing was missing")
	assert_eq(Game.state.location_id, &"", "the default is still not recorded")
	_done()


## M1-ARC-11 (QA review-sweep-G S3): a stale respawn does not skip a good location_id.
func test_a_stale_respawn_continues_at_the_saved_location() -> void:
	wr.enabled = true
	Game.state.location_id = &"zone_b"
	Game.state.respawn_location_id = &"ch99/renamed_shrine"
	Game.state.respawn_spawn = &"Gate"
	var to := wr.resolve(Game.state)
	assert_eq(to["location_id"], &"zone_b", "the saved location, not the default")
	assert_eq(to["spawn"], &"Dock", "at the location's own spawn (the respawn's spawn belongs elsewhere)")
	assert_false(bool(to["fallback"]))
	var tally := _WarningTally.new()
	OS.add_logger(tally)
	EventBus.game_loaded.emit(3)
	OS.remove_logger(tally)
	assert_eq(swaps, [[ZONE_B, &"Dock"]] as Array[Array])
	assert_eq(tally.matching("ch99/renamed_shrine"), 1, "the stale respawn is reported once")
	assert_eq(Game.state.respawn_location_id, &"ch99/renamed_shrine", "and kept, like a stale location")
	Game.state.location_id = &"ch99/gone"
	swaps.clear()
	EventBus.game_loaded.emit(3)
	assert_eq(swaps, [[ZONE_A, &"Gate"]] as Array[Array], "both stale: the default")
	_done()


## M1-ARC-11 (review-sweep-G S1 on M1-ENV-04): a location whose scene has no player (a mood or
## art stand-in, marked "playable": false) is never entered. Continue and go_to warn, go to the
## default and keep the saved location, so the player is never stranded without control.
func test_a_location_with_no_player_is_never_entered() -> void:
	var doc := _registry_doc()
	(doc["locations"] as Array).append(
		{"id": "mood", "scene": ZONE_B, "spawn": "Dock", "name_key": "LOCATION_FIELD_TEST", "playable": false}
	)
	wr.registry = LocationRegistry.from_dict(doc)
	assert_true(wr.registry.has_location(&"mood"))
	assert_false(wr.registry.can_enter(&"mood"))
	assert_true(wr.registry.can_enter(&"zone_b"), "playable is the default")
	var to := wr.registry.resolve(&"mood")
	assert_eq(to["location_id"], &"zone_a")
	assert_eq(to["reason"], LocationRegistry.REASON_NOT_PLAYABLE)
	wr.enabled = true
	Game.state.location_id = &"mood"
	Game.state.respawn_location_id = &"mood"
	var tally := _WarningTally.new()
	OS.add_logger(tally)
	EventBus.game_loaded.emit(3)
	assert_true(wr.go_to(&"mood"))
	OS.remove_logger(tally)
	assert_eq(swaps, [[ZONE_A, &"Gate"], [ZONE_A, &"Gate"]] as Array[Array], "the default stands in both times")
	assert_eq(tally.matching("no player to place"), 2, "each one warns")
	assert_eq(Game.state.location_id, &"mood", "the saved location is kept")
	Game.state.respawn_location_id = &"mood"
	Game.state.location_id = &"zone_b"
	swaps.clear()
	EventBus.game_loaded.emit(3)
	assert_eq(swaps, [[ZONE_B, &"Dock"]] as Array[Array], "a stand-in respawn yields to a good location")
	_done()


## The real registry marks the Haluna mood stand-in (until game/levels/ch02/haluna/ exists).
func test_the_real_haluna_stand_in_is_not_entered() -> void:
	var reg := LocationRegistry.load_default()
	assert_true(reg.has_location(&"ch02/haluna"))
	assert_false(reg.can_enter(&"ch02/haluna"), "haluna_mood.tscn has no player")
	assert_true(reg.can_enter(reg.default_location))
	assert_true(reg.can_enter(reg.new_game_location))
	_done()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


## Collects push_warning messages.
class _WarningTally:
	extends Logger
	var messages: Array[String] = []
	var _mutex := Mutex.new()

	func _log_error(
		_function: String,
		_file: String,
		_line: int,
		code: String,
		rationale: String,
		_editor_notify: bool,
		error_type: int,
		_script_backtraces: Array[ScriptBacktrace]
	) -> void:
		if error_type == Logger.ERROR_TYPE_WARNING:
			_mutex.lock()
			messages.append("%s %s" % [code, rationale])
			_mutex.unlock()

	func matching(fragment: String) -> int:
		_mutex.lock()
		var n := 0
		for m in messages:
			if m.contains(fragment):
				n += 1
		_mutex.unlock()
		return n


func _done() -> void:
	if is_instance_valid(wr):
		wr.free()
	for p: String in [ZONE_A, ZONE_B]:
		DirAccess.remove_absolute(p)
	DirAccess.remove_absolute(TEST_DIR)
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state
	Game.play_clock_running = _saved_clock
	swaps.clear()
