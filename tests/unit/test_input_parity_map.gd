extends TestCase
## M2-UI-26 (input parity): the zone map page (ZoneMapMenu) opened from the field menu's Map row,
## walked with the keyboard, the controller and the mouse through real InputEvents: choose places
## on the legend (and, with the mouse, on the map's glyphs and with the wheel anywhere on the page),
## back out, and the field menu takes the input again on its Map row.

const HALUNA := &"ch02/haluna"
const AT_SHRINE_FLAGS: Array[StringName] = [&"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes"]
const BEACH := Vector3(-8.0, 0.0, 6.0)

var menu: FieldMenu


func before_each() -> void:
	InputDriver.clear_screen()
	menu = null
	UiSettings.set_shared(UiSettings.new())


func test_open_choose_places_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		menu = ParityHost.open_field_menu(GameStateData.new(), ParityHost.HEROES, _haluna())
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_MAP)
		ParityHost.choose(d, root, at)
		var page := menu.map_menu
		assert_true(page != null and page.is_open(), "%s: Map opens the map" % who)
		assert_eq(page.current_poi(), &"shrine", "%s: on the objective's place" % who)
		var legend := page.legend()
		var chapel := ParityHost.row_of(legend, &"chapel")
		ParityHost.move_to(d, legend, chapel)
		assert_eq(page.current_poi(), &"chapel", "%s: the legend cursor moves" % who)
		assert_eq(page.view().highlight, &"chapel", "%s: the map rings it" % who)
		assert_eq(page.poi_line_text(), page.model.poi_line(&"chapel"), "%s: the line follows" % who)
		ParityHost.choose(d, legend, chapel)
		assert_true(page.is_open(), "%s: Confirm keeps the map open" % who)
		assert_eq(page.current_poi(), &"chapel")
		assert_eq(root.cursor, at, "%s: the field menu under it did not move" % who)
		ParityHost.back(d, page)
		assert_false(is_instance_valid(page), "%s: Cancel closes the map (its layer is gone)" % who)
		assert_true(menu.map_menu == null and menu.visible, "%s: back on the field menu" % who)
		assert_eq(root.cursor, at, "%s: on the Map row" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_SETTINGS)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the field menu has the input again" % who)
		_close()
	_done()


func test_the_mouse_picks_a_glyph_and_the_wheel_steps_over_the_map_too() -> void:
	menu = ParityHost.open_field_menu(GameStateData.new(), ParityHost.HEROES, _haluna())
	menu.root_page().set_cursor(ParityHost.row_of(menu.root_page(), FieldMenuModel.ROW_MAP), false)
	menu.accept()
	var page := menu.map_menu
	var view := page.view()
	ParityHost.hover_at(view, view.poi_marker_at(&"dock"))
	assert_eq(page.current_poi(), &"dock", "hovering a glyph chooses it")
	ParityHost.click_at(view, view.poi_marker_at(&"beach"))
	assert_eq(page.current_poi(), &"beach", "so does a click")
	var empty := Vector2(view.size.x * 0.5, view.size.y - 2.0)
	assert_eq(view.poi_at_point(empty), &"", "a spot with no glyph")
	var before := page.legend().cursor
	ParityHost.wheel_at(view, empty, 1)
	assert_eq(page.legend().cursor, before + 1, "the wheel over the map steps the places")
	ParityHost.wheel_at(page, Vector2(4.0, 4.0), -1)
	assert_eq(page.legend().cursor, before, "and over the page's backdrop")
	InputDriver.wheel(page.legend().row_node(before), 1)
	assert_eq(page.legend().cursor, before + 1, "and over the legend")
	assert_eq(page.view().highlight, page.current_poi(), "the ring follows the wheel")
	_close()
	_done()


func _haluna() -> MapModel:
	var on := AT_SHRINE_FLAGS
	return MapModel.new(HALUNA, BEACH, PI * 0.5, func(f: StringName) -> bool: return on.has(f))


func _close() -> void:
	ParityHost.free_field_menu(menu)
	menu = null


func _done() -> void:
	UiSettings.set_shared(null)
