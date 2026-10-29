extends TestCase
## The Kite's world map (KiteMapModel, KiteMapMenu; M3-UI-205, SPEC §6.6): places show once their flag is set,
## the one the party stands in is Here and can't be chosen, choosing asks first and Fly goes (recorded here, not
## made), a grounded Kite flies nowhere, and searching a chart square finds a secret place, which joins the list.
## The runner runs no frames and has no after_each.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"
const TABLE := {
	"open_flag": "kite_flying",
	"columns": ["A", "B", "C"],
	"rows": 2,
	"regions":
	[
		{"id": "reach", "name_key": "KITE_REGION_LOW_REACHES", "at": [0.2, 0.7]},
		{"id": "fen", "name_key": "KITE_REGION_OSSA_FEN", "at": [0.8, 0.2]},
	],
	"destinations":
	[
		{
			"id": "isle",
			"region": "reach",
			"location_id": "isle",
			"spawn": "Lane",
			"requires_flag": "",
			"at": [0.1, 0.9]
		},
		{
			"id": "shoals",
			"region": "fen",
			"location_id": "shoals",
			"spawn": "Lane",
			"requires_flag": "ch06_arrived",
			"at": [0.9, 0.1]
		},
	],
	"secrets":
	[
		{
			"id": "cove",
			"region": "fen",
			"location_id": "shoals",
			"spawn": "Lane",
			"found_flag": "kite_test_cove",
			"cell": "B2",
			"name_key": "KITE_REGION_HOLLOWMERE",
			"at": [0.5, 0.8]
		}
	],
}

var flags: Dictionary = {}
var trips: Array = []
var host: Node
var _saved_registry: LocationRegistry


func before_each() -> void:
	flags = {&"kite_flying": true, &"ch06_arrived": true}
	trips = []
	UiSettings.set_shared(UiSettings.new())
	_saved_registry = ShrineNetwork.registry
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
				"shrines": [],
			}
		)
	)
	host = Node.new()
	ParityHost.scene_root().add_child(host)


func test_places_show_by_flag_with_region_and_square() -> void:
	var m := _model()
	assert_eq(m.ids(), [&"isle", &"shoals"] as Array[StringName])
	flags.erase(&"ch06_arrived")
	assert_eq(m.ids(), [&"isle"] as Array[StringName], "a place shows once its flag is set")
	flags[&"ch06_arrived"] = true
	assert_eq(m.place_name(&"shoals"), tr("LOCATION_CH06_BRINE_SHOALS"), "by its location's name")
	assert_eq(m.region_name(&"shoals"), tr("KITE_REGION_OSSA_FEN"))
	assert_eq(m.cell_of(&"shoals"), "C1")
	assert_eq(m.cell_of(&"isle"), "A2")
	_done()


func test_flying_goes_except_here_or_grounded() -> void:
	var m := _model()
	m.here = &"isle"
	assert_true(m.is_here(&"isle"))
	assert_false(m.fly(&"isle"), "not where it stands")
	assert_true(m.fly(&"shoals"))
	assert_eq(trips, [[&"shoals", &"Lane"]])
	flags.erase(&"kite_flying")
	assert_false(m.fly(&"shoals"), "a grounded Kite flies nowhere")
	assert_eq(trips.size(), 1)
	_done()


func test_searching_a_square_finds_a_secret_once() -> void:
	var m := _model()
	assert_eq(m.search("A1"), {}, "open water")
	var found := m.search("B2")
	assert_eq(str(found["id"]), "cove")
	assert_true(bool(flags[&"kite_test_cove"]), "found: its flag is set")
	assert_true(m.ids().has(&"cove"), "and it is a destination now")
	assert_eq(m.place_name(&"cove"), tr("KITE_REGION_HOLLOWMERE"), "by its own name")
	_done()


func test_the_menu_asks_first_then_flies_and_marks_here() -> void:
	var m := _model()
	m.here = &"isle"
	var menu := KiteMapMenu.open_in(host, m)
	var rows := menu.rows_page().rows
	assert_eq(str(rows[0]["right"]), tr("KITE_HERE"))
	assert_false(bool(rows[0]["enabled"]), "here: not chosen")
	assert_eq(StringName(str(rows[-2]["id"])), KiteMapMenu.ROW_SEARCH)
	assert_eq(StringName(str(rows[-1]["id"])), KiteMapMenu.ROW_LEAVE)
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), &"shoals", "the cursor skips Here")
	assert_true(menu.desc_text().contains(tr("KITE_REGION_OSSA_FEN")), "the line names the region")
	assert_true(menu.desc_text().contains("C1"), "and the square")
	menu.accept()
	assert_eq(menu.level, KiteMapMenu.Level.CONFIRM)
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), KiteMapMenu.ROW_STAY, "Stay under the cursor")
	menu.handle_input(_ev(&"ui_down"))
	menu.accept()
	assert_eq(trips, [[&"shoals", &"Lane"]], "Fly goes")
	assert_false(menu.is_open())
	_close(menu)
	_done()


func test_the_menu_searches_a_square_and_lists_what_it_finds() -> void:
	var menu := KiteMapMenu.open_in(host, _model())
	menu.rows_page().set_cursor(menu.rows_page().rows.size() - 2, false)
	menu.accept()
	assert_eq(menu.level, KiteMapMenu.Level.SEARCH)
	menu.handle_input(_ev(&"ui_right"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.cell_name(), "B2")
	assert_eq(menu.chart().search_cell, Vector2i(1, 1), "the chart outlines it")
	assert_true(menu.desc_text().contains("B2"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, KiteMapMenu.Level.LIST)
	assert_true(menu.desc_text().contains(tr("KITE_REGION_HOLLOWMERE")), "found, by name")
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), &"cove", "the cursor goes to it")
	menu.rows_page().set_cursor(menu.rows_page().rows.size() - 2, false)
	menu.accept()
	menu.handle_input(_ev(&"ui_left"))
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.cell_name(), "C2", "the column wraps (B, A, then C)")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, KiteMapMenu.Level.LIST, "Cancel backs out of the search")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open(), "and Cancel on the list leaves")
	_close(menu)
	_done()


func _model() -> KiteMapModel:
	var bag := flags
	var log := trips
	return KiteMapModel.new(
		TABLE,
		func(f: StringName) -> Variant: return bag.get(f, false),
		func(f: StringName, v: Variant) -> void: bag[f] = v,
		func(loc: StringName, spawn: StringName) -> bool:
			log.append([loc, spawn])
			return true
	)


func _close(menu: KiteMapMenu) -> void:
	if is_instance_valid(menu) and menu.motion() != null:
		menu.motion().finish()


func _done() -> void:
	host.get_tree().paused = false
	host.get_parent().remove_child(host)
	host.free()
	ShrineNetwork.registry = _saved_registry
	UiSettings.set_shared(null)


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
