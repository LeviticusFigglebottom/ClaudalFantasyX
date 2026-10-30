extends TestCase
## The save shrines' travel list (ShrineTravelMenu over ShrineNetwork): after the save menu a shrine with other
## attuned shrines offers them by place name, Stay here last; choosing one asks first with Stay under the cursor;
## Go closes the page and travels (recorded here, not performed); a refused trip says so and keeps the list; a
## load, or nowhere to go, offers nothing. The runner runs no frames and has no after_each.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"

var trips: Array[StringName] = []
var host: Node
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
					{"id": "haluna", "scene": ZONE, "spawn": "Lane", "name_key": "LOCATION_CH05_PEMAKAR"},
				],
				"shrines":
				[
					{"id": "isle_shrine", "location_id": "isle", "spawn": "Shrine"},
					{"id": "haluna_shrine", "location_id": "haluna", "spawn": "Shrine"},
					{"id": "temple_shrine", "location_id": "haluna", "spawn": "Shrine", "order": true},
				],
			}
		)
	)
	trips = []
	host = Node.new()
	_root().add_child(host)


func test_after_the_save_menu_the_other_shrines_are_offered_by_name() -> void:
	var here := _shrine(&"isle_shrine")
	Game.state.attuned_shrines = [&"isle_shrine", &"haluna_shrine"] as Array[StringName]
	var menu := here.open_travel()
	assert_true(menu != null and menu.is_open(), "somewhere to go: the road is offered")
	assert_eq(menu.destinations, [&"haluna_shrine"] as Array[StringName], "not the shrine itself")
	var rows := menu.rows_page().rows
	assert_eq(str(rows[0]["label"]), tr("LOCATION_CH05_PEMAKAR"), "by its place's name")
	assert_eq(str(rows[1]["label"]), tr("SHRINE_TRAVEL_STAY"), "Stay here last")
	assert_true(menu.desc_text().contains(tr("LOCATION_CH05_PEMAKAR")), "the line names the place")
	_done(menu)


func test_choosing_asks_first_and_go_travels() -> void:
	var menu := _offer()
	menu.accept()
	assert_eq(menu.level, ShrineTravelMenu.Level.CONFIRM, "it asks first")
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), ShrineTravelMenu.ROW_STAY, "Stay under the cursor")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, ShrineTravelMenu.Level.LIST, "Cancel backs out of the question")
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), &"haluna_shrine", "on the place it asked about")
	menu.accept()
	menu.handle_input(_ev(&"ui_down"))
	assert_true(menu.desc_text().contains(tr("LOCATION_CH05_PEMAKAR")), "Go says where")
	var chosen: Array[StringName] = []
	menu.travel_chosen.connect(func(d: StringName) -> void: chosen.append(d))
	menu.accept()
	assert_eq(trips, [&"haluna_shrine"] as Array[StringName], "travelled")
	assert_eq(chosen, [&"haluna_shrine"] as Array[StringName])
	assert_false(menu.is_open(), "and the page closes (the router fades the field)")
	_done(menu)


func test_a_refused_trip_says_so_and_keeps_the_list() -> void:
	var menu := _offer()
	menu.travel = func(_d: StringName) -> bool: return false
	assert_false(menu.go(&"haluna_shrine"))
	assert_true(menu.is_open(), "still open")
	assert_eq(menu.level, ShrineTravelMenu.Level.LIST)
	assert_eq(menu.desc_text(), tr("SHRINE_TRAVEL_REFUSED_FMT").format({"place": tr("LOCATION_CH05_PEMAKAR")}))
	_done(menu)


func test_a_dark_order_shrine_stays_on_the_list_greyed_with_the_reason() -> void:
	var here := _shrine(&"isle_shrine")
	Game.state.attuned_shrines = [&"isle_shrine", &"temple_shrine", &"haluna_shrine"] as Array[StringName]
	assert_false(ShrineNetwork.is_dark(&"temple_shrine"), "before the heresy the Order's shrine answers")
	Game.state.flags[String(SaveShrine.HERETIC_FLAG)] = true
	var menu := here.open_travel()
	var dark: Dictionary = menu.rows_page().rows[0]
	assert_false(bool(dark["enabled"]), "greyed")
	assert_eq(str(dark["right"]), tr("SHRINE_TRAVEL_DARK"), "saying why")
	assert_eq(
		StringName(str(menu.rows_page().current_row()["id"])), &"haluna_shrine", "the cursor starts on a way open"
	)
	assert_false(menu.go(&"temple_shrine"), "and a trip there is refused")
	assert_true(trips.is_empty())
	_done(menu)


func test_stay_closes_and_goes_nowhere() -> void:
	var menu := _offer()
	menu.handle_input(_ev(&"ui_down"))
	menu.accept()
	assert_false(menu.is_open(), "Stay here closes")
	assert_true(trips.is_empty(), "and goes nowhere")
	_done(menu)


func test_nowhere_to_go_offers_nothing() -> void:
	var alone := _shrine(&"isle_shrine")
	Game.state.attuned_shrines = [&"isle_shrine"] as Array[StringName]
	assert_true(alone.open_travel() == null, "only this shrine attuned: nothing to offer")
	_done(null)


func test_a_load_offers_no_road() -> void:
	var here := _shrine(&"isle_shrine")
	Game.state.attuned_shrines = [&"isle_shrine", &"haluna_shrine"] as Array[StringName]
	here._on_menu_closed(SaveMenuModel.Outcome.LOADED)
	assert_true(here.travel_menu == null, "a load leaves this place")
	here._on_menu_closed(SaveMenuModel.Outcome.SAVED)
	assert_true(here.travel_menu != null, "after a save the road is offered")
	_done(here.travel_menu)


func _offer() -> ShrineTravelMenu:
	var here := _shrine(&"isle_shrine")
	Game.state.attuned_shrines = [&"isle_shrine", &"haluna_shrine"] as Array[StringName]
	var menu := here.open_travel()
	menu.travel = func(d: StringName) -> bool:
		trips.append(d)
		return true
	return menu


func _shrine(network_id: StringName) -> SaveShrine:
	var s := SaveShrine.new()
	s.network_id = network_id
	s.opens_menu = false
	host.add_child(s)
	return s


func _done(menu: ShrineTravelMenu) -> void:
	if menu != null and is_instance_valid(menu) and menu.motion() != null:
		menu.motion().finish()
	var tree := host.get_tree()
	tree.paused = false
	_root().remove_child(host)
	host.free()
	host = Node.new()
	_root().add_child(host)
	Game.state = _saved_state
	ShrineNetwork.registry = _saved_registry
	UiSettings.set_shared(_saved_settings)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
