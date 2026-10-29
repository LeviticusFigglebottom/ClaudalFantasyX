extends TestCase
## M3-UI-205: the field menu's Kite row. It is not there until the Kite flies; then it sits after Map, the panel
## grows a row (FieldMenu.grown_for) so all thirteen show, and it opens the Kite's world map over the menu. Cancel
## comes back; a flight closes the menu too. The trip is recorded, not made. The runner runs no frames.

const TABLE := {
	"open_flag": "kite_flying",
	"columns": ["A", "B"],
	"rows": 2,
	"regions": [],
	"destinations":
	[
		{"id": "isle", "region": "", "location_id": "isle", "spawn": "Lane", "requires_flag": "", "at": [0.1, 0.9]},
		{"id": "shoals", "region": "", "location_id": "shoals", "spawn": "Lane", "requires_flag": "", "at": [0.9, 0.1]},
	],
	"secrets": [],
}

var flags: Dictionary = {}
var trips: Array = []


func before_each() -> void:
	flags = {&"kite_flying": true}
	trips = []
	UiSettings.set_shared(UiSettings.new())


func test_no_row_until_the_kite_flies() -> void:
	var m := FieldMenuModel.new(GameStateData.new(), ParityHost.HEROES, ParityHost.NAMES)
	assert_false(_ids(m).has(FieldMenuModel.ROW_KITE), "no Kite at all: no row")
	m.kite = _kite()
	flags.erase(&"kite_flying")
	assert_false(_ids(m).has(FieldMenuModel.ROW_KITE), "grounded: no row (it would name Act III's ship early)")
	assert_eq(m.root_ids(), FieldMenuModel.ROOT_IDS, "and every other row keeps its place")
	flags[&"kite_flying"] = true
	var ids := _ids(m)
	assert_eq(ids.find(FieldMenuModel.ROW_KITE), ids.find(FieldMenuModel.ROW_MAP) + 1, "flying: after Map")
	assert_eq(ids.size(), FieldMenuModel.ROOT_IDS.size() + 1)
	assert_eq(m.root_desc(FieldMenuModel.ROW_KITE), tr("FIELD_MENU_KITE_DESC"))


func test_the_panel_grows_a_row_for_it() -> void:
	var d := FieldMenu.load_data()
	assert_eq(FieldMenu.grown_for(d, 0), d, "no extra row: the layout as it is")
	var g := FieldMenu.grown_for(d, 1)
	var pitch := HudLayout.num(d["root"], "row_pitch")
	for key: String in ["panel", "root"]:
		var was := HudLayout.rect_of(d[key])
		var now := HudLayout.rect_of(g[key])
		assert_eq(now.size.y, was.size.y + pitch, "%s: a pitch taller" % key)
		assert_eq(now.get_center(), was.get_center(), "%s: still centred" % key)
	assert_eq(int(g["root"]["max_rows"]), int(d["root"]["max_rows"]) + 1, "every row shows: no hidden Close")
	assert_eq(HudLayout.rect_of(g["objective"]).end.y, HudLayout.rect_of(d["objective"]).end.y + pitch * 0.5)
	var menu := _open()
	var root := menu.root_page()
	assert_eq(root.row_count(), FieldMenuModel.ROOT_IDS.size() + 1)
	assert_true(root.row_node(root.row_count() - 1).visible, "Close shows")
	ParityHost.free_field_menu(menu)
	_done()


func test_kite_opens_the_map_and_cancel_comes_back() -> void:
	var menu := _open()
	_choose_kite(menu)
	assert_true(menu.kite_menu != null and menu.kite_menu.is_open(), "the Kite's map opens")
	assert_false(menu.visible, "over the menu, which hides")
	assert_false(menu.handle_input(_ev(&"ui_down")), "the map has the input")
	menu.kite_menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.kite_menu, null)
	assert_true(menu.is_open() and menu.visible, "Cancel comes back to the menu")
	assert_true(trips.is_empty())
	ParityHost.free_field_menu(menu)
	_done()


func test_a_flight_closes_the_menu_too() -> void:
	var menu := _open()
	_choose_kite(menu)
	var kite := menu.kite_menu
	kite.accept()  # shoals (the cursor skips Here)
	kite.handle_input(_ev(&"ui_down"))
	kite.accept()  # Fly
	assert_eq(trips, [[&"shoals", &"Lane"]], "the Kite goes")
	assert_eq(kite.flown, &"shoals")
	assert_false(menu.is_open(), "and the field menu closes: the party is leaving")
	ParityHost.free_field_menu(menu)
	_done()


func _open() -> FieldMenu:
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	var m := FieldMenuModel.new(GameStateData.new(), ParityHost.HEROES, ParityHost.NAMES)
	m.kite = _kite()
	menu.configure(m)
	ParityHost.scene_root().add_child(menu)
	return menu


func _choose_kite(menu: FieldMenu) -> void:
	menu.root_page().set_cursor(menu.model.root_ids().find(FieldMenuModel.ROW_KITE), false)
	menu.accept()


func _kite() -> KiteMapModel:
	var bag := flags
	var log := trips
	var k := KiteMapModel.new(
		TABLE,
		func(f: StringName) -> Variant: return bag.get(f, false),
		func(f: StringName, v: Variant) -> void: bag[f] = v,
		func(loc: StringName, spawn: StringName) -> bool:
			log.append([loc, spawn])
			return true
	)
	k.here = &"isle"
	return k


func _ids(m: FieldMenuModel) -> Array[StringName]:
	var out: Array[StringName] = []
	for row in m.root_rows():
		out.append(StringName(str(row["id"])))
	return out


func _done() -> void:
	UiSettings.set_shared(null)


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
