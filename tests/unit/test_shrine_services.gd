extends TestCase
## The zone-agnostic save shrine hook (ShrineServices, M3-C07-05): a {"save_shrine": id} payload on a
## greybox zone's trigger rests the party at that locations.json shrines row, attunes it and opens the save
## menu, then the travel list, like a placed SaveShrine; other payloads and unlisted ids do nothing. The
## runner runs no frames and has no after_each.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"

var host: Node
var services: ShrineServices
var _saved_state: GameStateData
var _saved_registry: LocationRegistry
var _saved_settings: UiSettings


func before_each() -> void:
	_saved_state = Game.state
	_saved_registry = ShrineNetwork.registry
	_saved_settings = UiSettings.shared()
	UiSettings.set_shared(UiSettings.new())
	Game.state = GameStateData.new()
	ShrineNetwork.registry = (
		LocationRegistry
		. from_dict(
			{
				"default_location": "isle",
				"locations":
				[
					{"id": "isle", "scene": ZONE, "spawn": "Lane", "name_key": "LOCATION_FIELD_TEST"},
					{"id": "shoals", "scene": ZONE, "spawn": "Lane", "name_key": "LOCATION_CH06_BRINE_SHOALS"},
				],
				"shrines":
				[
					{"id": "isle_shrine", "location_id": "isle", "spawn": "Shrine"},
					{"id": "shoals_camp", "location_id": "shoals", "spawn": "Shrine"},
				],
			}
		)
	)
	host = Node.new()
	_root().add_child(host)
	services = ShrineServices.new()
	host.add_child(services)


func test_a_save_shrine_payload_rests_attunes_and_opens_the_save_menu() -> void:
	var shrine := services.handle({"save_shrine": "shoals_camp", "beat": "shrine"})
	assert_true(shrine != null, "a listed shrine is used")
	assert_true(shrine.is_menu_open(), "the save menu opens")
	assert_true(ShrineNetwork.is_attuned(&"shoals_camp"), "attuned")
	assert_eq(Game.state.location_id, &"shoals", "the party is at the shrine's place")
	assert_eq(Game.state.respawn_spawn, &"Shrine", "and respawns at its spawn")
	assert_true(bool(Game.get_flag(&"save_shrine_used")))
	assert_true(services.handle({"save_shrine": "shoals_camp"}) == null, "not twice while the menu is open")
	_done()


func test_the_road_is_offered_after_the_save_menu_and_the_shrine_is_kept() -> void:
	Game.state.attuned_shrines = [&"isle_shrine"] as Array[StringName]
	var shrine := services.handle({"save_shrine": "shoals_camp"})
	shrine._on_menu_closed(SaveMenuModel.Outcome.SAVED)
	assert_true(shrine.travel_menu != null, "another shrine is attuned: the road is offered")
	assert_eq(shrine.travel_menu.destinations, [&"isle_shrine"] as Array[StringName])
	var road := shrine.travel_menu
	road.close()
	road.motion().finish()
	assert_true(shrine.travel_menu == null, "closing the road lets the shrine be used again")
	assert_eq(services.shrine_for(&"shoals_camp", {}), shrine, "one shrine per id, made once")
	_done()


func test_other_payloads_and_unlisted_ids_do_nothing() -> void:
	assert_true(services.handle({"shop": "haluna_market"}) == null, "not a shrine")
	assert_true(services.handle({"save_shrine": "nowhere"}) == null, "no shrines row")
	assert_true(services.shrines.is_empty())
	assert_true(Game.state.attuned_shrines.is_empty())
	_done()


func test_it_hears_field_interactions_on_the_bus() -> void:
	FieldEvents.emit_interacted(&"shrine", &"interact", {"save_shrine": "shoals_camp"})
	assert_true(services.shrines.has(&"shoals_camp"), "the bus reached the hook")
	_done()


func _done() -> void:
	for s: Variant in services.shrines.values():
		var shrine := s as SaveShrine
		if shrine.is_menu_open():
			shrine.menu.motion().finish()
	host.get_tree().paused = false
	_root().remove_child(host)
	host.free()
	Audio.stop_all_players()  # the save menu's open sound; no frame runs to end it
	host = Node.new()
	_root().add_child(host)
	services = ShrineServices.new()
	host.add_child(services)
	Game.state = _saved_state
	ShrineNetwork.registry = _saved_registry
	UiSettings.set_shared(_saved_settings)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
