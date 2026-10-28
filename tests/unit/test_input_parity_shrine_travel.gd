extends TestCase
## Input parity for the shrine travel list (ShrineTravelMenu): choosing a place, then Go, and Cancel to stay,
## with the keyboard, the controller and the mouse through real InputEvents (InputDriver). The trip is recorded,
## not made. The runner runs no frames and has no after_each.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"

var trips: Array[StringName] = []
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
				"shrines":
				[
					{"id": "isle_shrine", "location_id": "isle", "spawn": "Shrine"},
					{"id": "shoals_camp", "location_id": "shoals", "spawn": "Shrine"},
				],
			}
		)
	)


func test_choose_a_place_and_go_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var menu := _open()
		_choose(d, menu, 0)
		assert_eq(menu.level, ShrineTravelMenu.Level.CONFIRM, "%s: choosing a place asks first" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(menu.rows_page().row_node(1))
		else:
			d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_eq(trips, [&"shoals_camp"] as Array[StringName], "%s: Go travels" % d.label())
		_close(menu)
	_done()


func test_cancel_stays_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var menu := _open()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.right_click(menu)
		else:
			d.press(&"ui_cancel")
		assert_false(menu.is_open(), "%s: Cancel stays here" % d.label())
		assert_true(trips.is_empty(), "%s: and goes nowhere" % d.label())
		_close(menu)
	_done()


func _open() -> ShrineTravelMenu:
	trips = []
	host = Node.new()
	ParityHost.scene_root().add_child(host)
	var menu := ShrineTravelMenu.open_in(host, null, [&"shoals_camp"] as Array[StringName])
	menu.travel = func(dest: StringName) -> bool:
		trips.append(dest)
		return true
	return menu


func _choose(d: InputDriver, menu: ShrineTravelMenu, index: int) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.click(menu.rows_page().row_node(index))
	else:
		d.press(&"ui_accept")


func _close(menu: ShrineTravelMenu) -> void:
	if is_instance_valid(menu) and menu.motion() != null:
		menu.motion().finish()
	host.get_tree().paused = false
	host.get_parent().remove_child(host)
	host.free()


func _done() -> void:
	ShrineNetwork.registry = _saved_registry
	InputDriver.park_pointer()
	UiSettings.set_shared(null)
