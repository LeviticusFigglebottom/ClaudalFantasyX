extends TestCase
## M1-ARC-06: the shrine teleport network. Attunement persists in Game.state (save v4),
## destinations are the attuned shrines the registry lists, and a teleport goes through the
## LocationRegistry and becomes the respawn point. Travel is recorded, not performed.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"

var trips: Array[Array] = []
var here: SaveShrine
var _saved_state: GameStateData
var _saved_registry: LocationRegistry
var _saved_travel: Callable


func before_each() -> void:
	_saved_state = Game.state
	_saved_registry = ShrineNetwork.registry
	_saved_travel = ShrineNetwork.travel
	Game.state = GameStateData.new()
	ShrineNetwork.registry = (
		LocationRegistry
		. from_dict(
			{
				"default_location": "isle",
				"locations":
				[
					{"id": "isle", "scene": ZONE, "spawn": "Lane", "name_key": "LOCATION_FIELD_TEST"},
					{"id": "court", "scene": ZONE, "spawn": "Court", "name_key": "LOCATION_FIELD_TEST"},
					{
						"id": "mood",
						"scene": ZONE,
						"spawn": "Lane",
						"name_key": "LOCATION_FIELD_TEST",
						"playable": false
					},
				],
				"shrines":
				[
					{"id": "isle_shrine", "location_id": "isle", "spawn": "Shrine"},
					{"id": "court_shrine", "location_id": "court", "spawn": ""},
					{"id": "broken_shrine", "location_id": "missing"},
					{"id": "mood_shrine", "location_id": "mood", "spawn": "Lane"},
					{"id": "temple_shrine", "location_id": "court", "spawn": "", "order": true},
				],
			}
		)
	)
	ShrineNetwork.travel = func(loc: StringName, spawn: StringName) -> bool:
		trips.append([loc, spawn])
		return true
	here = _shrine(&"isle_shrine")


func _shrine(network_id: StringName) -> SaveShrine:
	var s := SaveShrine.new()
	s.network_id = network_id
	return s


func test_attuning_persists_once_in_order() -> void:
	assert_true(ShrineNetwork.attune(here))
	assert_false(ShrineNetwork.attune(here), "already attuned")
	assert_true(ShrineNetwork.attune_id(&"court_shrine"))
	assert_false(ShrineNetwork.attune_id(&""), "outside the network")
	assert_eq(Game.state.attuned_shrines, [&"isle_shrine", &"court_shrine"] as Array[StringName])
	assert_true(ShrineNetwork.is_attuned(&"court_shrine"))
	assert_false(ShrineNetwork.is_attuned(&""))
	var saves: Node = (load("res://game/core/save_system.gd") as GDScript).new()
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(saves.serialize(Game.state))))
	assert_eq(back.attuned_shrines, Game.state.attuned_shrines, "saved")
	saves.free()
	_done()


func test_destinations_are_attuned_listed_shrines_but_not_here() -> void:
	assert_eq(ShrineNetwork.destinations_from(here), [] as Array[StringName], "nothing attuned yet")
	for id: StringName in [&"court_shrine", &"isle_shrine", &"ghost_shrine", &"broken_shrine"]:
		ShrineNetwork.attune_id(id)
	assert_eq(
		ShrineNetwork.destinations_from(here),
		[&"court_shrine", &"broken_shrine"] as Array[StringName],
		"attunement order; unlisted ids are skipped"
	)
	assert_eq(here.teleport_destinations(), ShrineNetwork.destinations_from(here))
	assert_eq(ShrineNetwork.destinations_from(_shrine(&"")), [] as Array[StringName])
	assert_eq(ShrineNetwork.destinations_from(null), [] as Array[StringName])
	_done()


func test_teleport_goes_through_the_registry_and_sets_the_respawn() -> void:
	ShrineNetwork.attune(here)
	ShrineNetwork.attune_id(&"court_shrine")
	var court := _shrine(&"court_shrine")
	assert_true(court.request_teleport(&"isle_shrine"))
	assert_eq(trips, [[&"isle", &"Shrine"]] as Array[Array])
	assert_eq(Game.state.respawn_location_id, &"isle")
	assert_eq(Game.state.respawn_spawn, &"Shrine")
	assert_true(ShrineNetwork.request_teleport(here, &"court_shrine"))
	assert_eq(trips[1], [&"court", &"Court"], "an empty shrine spawn uses the location's")
	court.free()
	_done()


func test_teleport_refusals() -> void:
	ShrineNetwork.attune(here)
	ShrineNetwork.attune_id(&"broken_shrine")
	assert_false(ShrineNetwork.request_teleport(here, &"court_shrine"), "not attuned")
	assert_false(ShrineNetwork.request_teleport(here, &"isle_shrine"), "not to itself")
	assert_false(ShrineNetwork.request_teleport(here, &"broken_shrine"), "its location is unknown")
	ShrineNetwork.attune_id(&"mood_shrine")
	assert_false(ShrineNetwork.request_teleport(here, &"mood_shrine"), "a stand-in scene with no player")
	ShrineNetwork.attune_id(&"court_shrine")
	ShrineNetwork.travel = func(_l: StringName, _s: StringName) -> bool: return false
	assert_false(ShrineNetwork.request_teleport(here, &"court_shrine"), "the swap was refused")
	assert_eq(Game.state.respawn_location_id, &"", "a refused trip moves nothing")
	assert_eq(trips, [] as Array[Array])
	_done()


func test_the_order_s_shrines_go_dark_for_heretics() -> void:
	ShrineNetwork.attune(here)
	ShrineNetwork.attune_id(&"temple_shrine")
	assert_false(ShrineNetwork.is_dark(&"temple_shrine"), "lit before the heresy")
	Game.state.flags[String(SaveShrine.HERETIC_FLAG)] = true
	assert_true(ShrineNetwork.is_dark(&"temple_shrine"))
	assert_false(ShrineNetwork.is_dark(&"court_shrine"), "a shrine not the Order's keeps working")
	assert_false(ShrineNetwork.request_teleport(here, &"temple_shrine"), "no road to a dark shrine")
	assert_eq(trips, [] as Array[Array])
	_done()


func test_registry_point_and_respawn_spawn() -> void:
	assert_eq(ShrineNetwork.registry_point(&""), {})
	assert_eq(ShrineNetwork.registry_point(&"isle_shrine")["spawn"], &"Shrine")
	assert_eq(here.respawn_spawn_name(), &"Shrine", "from the registry row")
	here.respawn_spawn = &"Court"
	assert_eq(here.respawn_spawn_name(), &"Court", "the instance's own export wins")
	var loose := _shrine(&"")
	assert_eq(loose.respawn_spawn_name(), &"", "no row: the location's own spawn later")
	loose.free()
	_done()


func test_the_default_traveler_needs_an_idle_router() -> void:
	ShrineNetwork.travel = Callable()
	assert_true(ShrineNetwork._router_travel().is_valid(), "SceneRouter.world_return.go_to")
	_done()


func _done() -> void:
	if is_instance_valid(here):
		here.free()
	ShrineNetwork.registry = _saved_registry
	ShrineNetwork.travel = _saved_travel
	Game.state = _saved_state
	trips.clear()
