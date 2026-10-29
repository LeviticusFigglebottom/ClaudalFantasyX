extends TestCase
## Input parity for the Kite's world map (KiteMapMenu, M3-UI-205): choosing a place then Fly, searching a chart
## square, and Cancel, with the keyboard, the controller and the mouse through real InputEvents (InputDriver).
## The trip is recorded, not made. The runner runs no frames and has no after_each.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"
const TABLE := {
	"open_flag": "kite_flying",
	"columns": ["A", "B", "C"],
	"rows": 2,
	"regions": [{"id": "reach", "name_key": "KITE_REGION_LOW_REACHES", "at": [0.2, 0.7]}],
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
			"region": "reach",
			"location_id": "shoals",
			"spawn": "Lane",
			"requires_flag": "",
			"at": [0.9, 0.1]
		},
	],
	"secrets":
	[
		{
			"id": "cove",
			"region": "reach",
			"location_id": "shoals",
			"spawn": "Lane",
			"found_flag": "kite_test_cove",
			"cell": "B2",
			"name_key": "KITE_REGION_HOLLOWMERE",
			"at": [0.5, 0.8]
		}
	],
}
## The chart point at the middle of square B2 (fractions of the chart).
const B2_AT := Vector2(0.5, 0.75)

var flags: Dictionary = {}
var trips: Array = []
var host: Node
var _saved_registry: LocationRegistry


func before_each() -> void:
	InputDriver.clear_screen()
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


func test_choose_a_place_and_fly_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var menu := _open()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(menu.rows_page().row_node(1))
		else:
			d.press(&"ui_accept")
		assert_eq(menu.level, KiteMapMenu.Level.CONFIRM, "%s: choosing a place asks first" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(menu.rows_page().row_node(1))
		else:
			d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_eq(trips, [[&"shoals", &"Lane"]], "%s: Fly goes" % d.label())
		_close(menu)
	_done()


func test_search_a_square_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var menu := _open()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(menu.rows_page().row_node(2))
		else:
			d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_eq(menu.level, KiteMapMenu.Level.SEARCH, "%s: Search the chart opens the search" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			var chart := menu.chart()
			InputDriver.click_at(chart.get_global_transform_with_canvas() * (chart.size * B2_AT))
		else:
			d.press(&"ui_right")
			d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_true(bool(flags.get(&"kite_test_cove", false)), "%s: square B2 is searched" % d.label())
		assert_eq(StringName(str(menu.rows_page().current_row()["id"])), &"cove", "%s: and listed" % d.label())
		_close(menu)
	_done()


func test_cancel_leaves_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var menu := _open()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.right_click(menu)
		else:
			d.press(&"ui_cancel")
		assert_false(menu.is_open(), "%s: Cancel leaves" % d.label())
		assert_true(trips.is_empty(), "%s: and flies nowhere" % d.label())
		_close(menu)
	_done()


func _open() -> KiteMapMenu:
	flags = {&"kite_flying": true}
	trips = []
	host = Node.new()
	ParityHost.scene_root().add_child(host)
	var bag := flags
	var log := trips
	var model := KiteMapModel.new(
		TABLE,
		func(f: StringName) -> Variant: return bag.get(f, false),
		func(f: StringName, v: Variant) -> void: bag[f] = v,
		func(loc: StringName, spawn: StringName) -> bool:
			log.append([loc, spawn])
			return true
	)
	model.here = &"isle"
	return KiteMapMenu.open_in(host, model)


func _close(menu: KiteMapMenu) -> void:
	if is_instance_valid(menu) and menu.motion() != null:
		menu.motion().finish()
	host.get_tree().paused = false
	host.get_parent().remove_child(host)
	host.free()


func _done() -> void:
	ShrineNetwork.registry = _saved_registry
	InputDriver.park_pointer()
	UiSettings.set_shared(null)
