extends TestCase
## M2-UI-18: the zone map (MapModel, ZoneMapShapes, ZoneMapView, RouteStrip, ZoneMapMenu) and the
## field menu's Map row: world -> map, places in order, the objective's marker on its target, the
## player's arrow, the shapes drawn from Haluna's layout and the Shell Shrine's trial, the row that
## is off where there is no map, and keyboard and mouse input.

const HALUNA := &"ch02/haluna"
const SHRINE := &"ch03/shell_shrine"
const UNDERWAY := &"ch01/oruvel_underway"
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const AT_SHRINE_FLAGS: Array[StringName] = [&"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes"]
const BEACH := Vector3(-8.0, 0.0, 6.0)

var menu: FieldMenu
var page: ZoneMapMenu


func before_each() -> void:
	menu = null
	page = null


# --- the model -----------------------------------------------------------------------------------


func test_world_to_map_is_one_scale_centred_and_letterboxed() -> void:
	var b := Rect2(-150.0, -150.0, 210.0, 230.0)
	var view := Rect2(0.0, 0.0, 1000.0, 500.0)
	var xf := MapModel.fit(b, view)
	var s := 500.0 / 230.0
	assert_true(is_equal_approx(xf.x.x, s) and is_equal_approx(xf.y.y, s), "the smaller fit, both axes")
	assert_true((xf * b.get_center()).is_equal_approx(view.get_center()), "centred")
	var top_left := xf * b.position
	var bottom_right := xf * b.end
	assert_true(is_equal_approx(top_left.y, 0.0) and is_equal_approx(bottom_right.y, 500.0), "fills the height")
	assert_true(top_left.x > 0.0 and bottom_right.x < 1000.0, "letterboxed across")
	assert_true((xf * Vector2(-40.0, 0.0)).x > (xf * Vector2(-50.0, 0.0)).x, "east is right")
	assert_true((xf * Vector2(0.0, -10.0)).y < (xf * Vector2(0.0, 0.0)).y, "north (-z) is up")


func test_compass_words_and_facing() -> void:
	assert_eq(MapModel.direction_key(Vector2.ZERO, Vector2(0.0, -10.0)), "MAP_DIR_N")
	assert_eq(MapModel.direction_key(Vector2.ZERO, Vector2(10.0, 0.0)), "MAP_DIR_E")
	assert_eq(MapModel.direction_key(Vector2.ZERO, Vector2(-10.0, 10.0)), "MAP_DIR_SW")
	assert_eq(MapModel.direction_key(Vector2.ZERO, Vector2(10.0, -9.0)), "MAP_DIR_NE")
	assert_true(MapModel.facing(0.0).is_equal_approx(Vector2(0.0, -1.0)), "yaw 0 faces north")
	assert_true(MapModel.facing(PI * 0.5).is_equal_approx(Vector2(-1.0, 0.0)), "PI/2 faces west")
	var fwd := Basis(Vector3.UP, 0.7) * Vector3.FORWARD
	assert_true(MapModel.facing(0.7).is_equal_approx(Vector2(fwd.x, fwd.z)), "as FieldMotor faces")


func test_places_come_in_zone_maps_order_with_their_names() -> void:
	var m := _haluna()
	var rows: Array = ZoneMaps.new().zone(HALUNA)["pois"]
	var pois := m.pois()
	assert_eq(pois.size(), rows.size())
	for i in rows.size():
		assert_eq(pois[i]["id"], StringName(str(rows[i]["id"])), "in data order")
		assert_eq(pois[i]["name"], tr(str(rows[i]["name_key"])))
		assert_eq(m.poi_rows()[i]["label"], pois[i]["name"])
	assert_true(m.has_map())
	assert_eq(m.zone_name(), tr("LOCATION_CH02_HALUNA"))


func test_the_objective_points_at_its_place_and_errands_list() -> void:
	var m := _haluna()
	assert_eq(m.objective_line(), tr("OBJ_SAVE_AT_SHRINE"))
	assert_eq(m.objective_poi(), &"shrine")
	assert_true(m.objective_at().is_equal_approx(Vector2(-67.0, 44.3)))
	assert_eq(m.first_index(), m.poi_index(&"shrine"), "the cursor starts on the objective's place")
	assert_eq(m.errand_lines(), [tr("OBJ_SIDE_TOWN")] as Array[String])
	var early := MapModel.new(HALUNA, BEACH, 0.0, _flags([]))
	assert_eq(early.objective_poi(), &"", "nothing calls before the beach")
	assert_eq(early.objective_line(), tr("OBJ_NONE_HALUNA"))
	assert_false(early.objective_at().is_finite())
	assert_eq(early.errands_text(), tr("MAP_ERRANDS_NONE"))
	assert_eq(early.first_index(), 0)
	var trial := MapModel.new(SHRINE, Vector3.INF, 0.0, _flags([]))
	assert_eq(trial.objective_poi(), &"inner_pool", "the trial's line points at the inner pool")


func test_an_order_shrine_goes_hollow_and_dark_for_heretics() -> void:
	var maps := ZoneMaps.new()
	var pois := [
		{"id": "temple", "name_key": "MAP_POI_BEACH", "kind": "shrine", "at": [0.0, 0.0], "order": true},
		{"id": "kirru", "name_key": "MAP_POI_DOCK", "kind": "shrine", "at": [4.0, 0.0]},
	]
	maps.data = {"zones": [{"id": "temple_zone", "bounds": [-10.0, -10.0, 20.0, 20.0], "pois": pois}]}
	var lit := MapModel.new(&"temple_zone", Vector3.INF, 0.0, _flags([]), maps)
	assert_eq(lit.pois()[0]["kind"], MapGlyphs.KIND_SHRINE, "lit before the heresy")
	assert_eq(str(lit.poi_rows()[0]["label"]), tr("MAP_POI_BEACH"))
	var heresy: Array[StringName] = [SaveShrine.HERETIC_FLAG]
	var dark := MapModel.new(&"temple_zone", Vector3.INF, 0.0, _flags(heresy), maps)
	assert_eq(dark.pois()[0]["kind"], MapGlyphs.KIND_SHRINE_DARK, "the hollow flame")
	var named := tr("MAP_POI_SHRINE_DARK_FMT").format({"place": tr("MAP_POI_BEACH")})
	assert_eq(str(dark.poi_rows()[0]["label"]), named, "Dark in its legend row")
	assert_eq(dark.pois()[1]["kind"], MapGlyphs.KIND_SHRINE, "a shrine not the Order's keeps its light")


func test_the_line_under_the_map_says_how_far_and_which_way() -> void:
	var m := _haluna()
	var shrine: Vector2 = m.pois()[m.poi_index(&"shrine")]["at"]
	var d := roundi(shrine.distance_to(Vector2(BEACH.x, BEACH.z)))
	var want := tr("MAP_POI_LINE_FMT").format({"name": tr("MAP_POI_SAVE_SHRINE"), "m": d, "dir": tr("MAP_DIR_SW")})
	assert_eq(m.poi_line(&"shrine"), want + " " + tr("MAP_POI_GOAL"), "and the objective says so")
	var here := MapModel.new(HALUNA, Vector3(-67.0, 0.0, 45.0), 0.0, _flags(AT_SHRINE_FLAGS))
	assert_true(
		here.poi_line(&"shrine").begins_with(tr("MAP_POI_HERE_FMT").format({"name": tr("MAP_POI_SAVE_SHRINE")}))
	)
	var nobody := MapModel.new(HALUNA, Vector3.INF, 0.0, _flags([]))
	assert_false(nobody.has_player())
	assert_eq(nobody.poi_line(&"inn"), tr("MAP_POI_INN"), "no player: the name alone")


func test_the_route_strip_marks_the_current_stop() -> void:
	var stops := _haluna().route_stops()
	assert_eq(stops.size(), 5, "M3-UI-04: two stops either side of Haluna")
	assert_eq(stops[2]["name"], tr("MAP_ROUTE_HALUNA"))
	var current: Array = []
	for s in stops:
		current.append(s["current"])
	assert_eq(current, [false, false, true, false, false])
	assert_eq(StringName(str(stops[0]["id"])), UNDERWAY, "Ch1 behind")
	assert_eq(StringName(str(stops[4]["id"])), SHRINE, "the Shell Shrine ahead")
	var at_shrine := MapModel.new(SHRINE, Vector3.INF, 0.0, _flags([])).route_stops()
	assert_eq([at_shrine[0]["current"], at_shrine[2]["current"]], [false, true])
	var first := MapModel.new(UNDERWAY, Vector3.INF, 0.0, _flags([])).route_stops()
	assert_eq(first.size(), 3, "at the start of the road: itself and the two ahead")
	assert_true(first[0]["current"])
	var act_break := MapModel.new(&"ch09/corrow_night", Vector3.INF, 0.0, _flags([])).route_stops()
	assert_eq(act_break.size(), 5, "M3-UI-206: Act I's end runs on into Act II")
	assert_eq(StringName(str(act_break[3]["id"])), &"ch10/ossa_fen", "Ossa Fen next")
	var last := MapModel.new(&"ch19/iskarra_spire", Vector3.INF, 0.0, _flags([])).route_stops()
	assert_eq(last.size(), 3, "M5-A3P-1015: at the route's end (Iskarra's spire): the two behind and itself")
	assert_true(last[2]["current"])
	assert_eq(MapModel.new(&"nowhere").route_stops().size(), 5, "off the route: the first stops")
	assert_false(MapModel.new(&"nowhere").has_map())


# --- the shapes ----------------------------------------------------------------------------------


func test_haluna_shapes_come_from_its_layout() -> void:
	var m := _haluna()
	var layout := m.shape_source()
	var data := MapModel.load_data()
	var s := ZoneMapShapes.build(m.shape_kind(), layout, m.bounds().grow(40.0), data["map"], data["pieces"])
	assert_true(s.sea and s.land.size() >= 1, "the sea, and the land inside the waterline")
	assert_eq(s.sand.size(), 1, "the beach under the tidewall")
	assert_eq(s.walls.size(), (layout["runs"] as Array).size(), "each wall run")
	assert_eq(s.lanes.size(), (layout["lanes"] as Array).size())
	assert_eq(s.pads.size(), (layout["pads"] as Array).size())
	assert_true(is_equal_approx(s.lane_width_m, float(layout["terrain"]["lane_width_m"])))
	var buildings := 0
	for p: Variant in layout["pieces"]:
		var spec: Dictionary = (data["pieces"] as Dictionary).get(str((p as Dictionary)["piece"]), {})
		if str(spec.get("style", "")) == ZoneMapShapes.STYLE_BUILDING:
			buildings += 1
	assert_eq(s.buildings.size(), buildings, "every house, the chapel and the stilt houses")
	var t: Dictionary = layout["terrain"]
	assert_true(is_equal_approx(ZoneMapShapes.shore_x(t, 0.0), 0.0), "the crescent's back at z 0")
	var tip := float(t["shore_half_len_m"])
	assert_true(is_equal_approx(ZoneMapShapes.shore_x(t, tip), float(t["shore_tip_x_m"])), "its tips")


func test_a_footprint_turns_as_the_dresser_places_the_piece() -> void:
	var yaw := deg_to_rad(35.0)
	var poly := ZoneMapShapes.footprint(Vector2(-6.0, 60.0), [0.0, -2.0, 38.0, 4.0], yaw, 1.0)
	var corner := Basis(Vector3.UP, yaw) * Vector3(38.0, 0.0, -2.0) + Vector3(-6.0, 0.0, 60.0)
	assert_true(poly[1].is_equal_approx(Vector2(corner.x, corner.z)), "Basis(UP, yaw), as HalunaDresser")
	var scaled := ZoneMapShapes.footprint(Vector2.ZERO, [0.0, 0.0, 2.0, 1.0], 0.0, 2.0)
	assert_true(scaled[2].is_equal_approx(Vector2(4.0, 2.0)))


func test_shrine_shapes_come_from_its_trial() -> void:
	var m := MapModel.new(SHRINE, Vector3.INF, 0.0, _flags([]))
	var trial := m.shape_source()
	assert_true(trial.has("room") and trial.has("layout"), "the trial's object, unwrapped")
	var data := MapModel.load_data()
	var s := ZoneMapShapes.build(m.shape_kind(), trial, m.bounds(), data["map"], data["pieces"])
	var g: Dictionary = trial["room"]
	assert_false(s.sea)
	assert_eq(s.floors.size(), 2, "the hall and the passage behind the door")
	var basins := (trial["basins"] as Dictionary).size()
	assert_eq(s.water.size(), basins + 3, "the basins, the spring, the inner pool and the side pool")
	assert_eq(s.rims.size(), basins + 2)
	assert_eq(s.structures.size(), 1, "the door")
	assert_true(s.channels.size() > basins, "the troughs")
	var door := Vector2(float(trial["layout"]["door"][0]), float(trial["layout"]["door"][1]))
	var reach := float(g["hall_half_m"]) + float(g["hall_r_m"])
	var nearest := INF
	for i in s.walls.size() - 1:  # the hall's outline (the last wall is the passage)
		for p in s.walls[i]:
			nearest = minf(nearest, p.distance_to(door))
			assert_true(absf(p.x) <= reach + 0.01, "inside the stadium's ends")
	assert_true(nearest >= float(g["door_w"]) * 0.5, "the wall is open where the door stands")


# --- Act I greybox zones (M3-UI-04) --------------------------------------------------------------


## M3-UI-04, and M3-UI-206 for Act II's fifteen (Ch10 to Ch16).
func test_every_greybox_zone_builds_a_map() -> void:
	var maps := ZoneMaps.new()
	var data := MapModel.load_data()
	var seen := 0
	for z: Variant in maps.data["zones"]:
		var row := z as Dictionary
		if str(row.get("shape_kind", "")) != String(ZoneMapShapes.KIND_GREYBOX):
			continue
		seen += 1
		var id := StringName(str(row["id"]))
		var m := MapModel.new(id, Vector3.INF, 0.0, _flags([]))
		assert_true(m.has_map(), "%s has a map" % id)
		assert_ne(m.zone_name(), str(row["name_key"]), "%s has its name" % id)
		var layout := m.shape_source()
		assert_true(layout.has("blocks"), "%s reads its layout" % id)
		var s := ZoneMapShapes.build(
			m.shape_kind(), layout, m.bounds(), data["map"], data["pieces"], data["greybox"], m.shape_hints()
		)
		assert_false(s.floors.is_empty() and s.pads.is_empty(), "%s has ground to walk" % id)
		assert_false(s.buildings.is_empty() and s.structures.is_empty(), "%s has walls or buildings" % id)
		var b := m.bounds()
		assert_true(b.size.x > 0.0 and b.size.y > 0.0, "%s has bounds" % id)
		assert_false(m.pois().is_empty(), "%s has places" % id)
		for p in m.pois():
			assert_true(b.has_point(p["at"]), "%s/%s inside the map" % [id, p["id"]])
			assert_ne(str(p["name"]), "", "%s/%s has a name" % [id, p["id"]])
			assert_true(MapGlyphs.KINDS.has(p["kind"]), "%s/%s draws as a known glyph" % [id, p["id"]])
		var on_route := false
		for r: Variant in maps.route():
			on_route = on_route or StringName(str((r as Dictionary)["id"])) == id
		assert_true(on_route, "%s is on the route" % id)
	assert_eq(
		seen,
		30,
		(
			"Act I's twelve (Ch1, Ch3's causeway (M2-FP-1000), Ch4's ferry (its wake reads Haluna's layout), Ch5 to Ch9),"
			+ " Act II's fifteen (Ch10 to Ch16, M3-UI-206) and Act III's three (the Kite, Iskarra and its spire;"
			+ " M5-A3P-1015: the Undertow and the Heart have no map)"
		)
	)


func test_greybox_blocks_sort_by_height_and_hints() -> void:
	var data := MapModel.load_data()
	var g: Dictionary = data["greybox"]
	var top := float(g["floor_top_m"])
	var over := float(g["overhead_m"])
	var thin := float(g["wall_thick_m"])
	var post := float(g["post_max_m"])
	var floor_row := {"id": "Deck", "pos": [0, -0.5, 0], "size": [8, 1, 30]}
	assert_eq(ZoneMapShapes.greybox_layer(floor_row, {}, top, over, thin, post), ZoneMapShapes.LAYER_FLOOR)
	var lane := {"id": "Lane", "pos": [0, 0.02, 0], "size": [4, 0.04, 40], "solid": false}
	assert_eq(ZoneMapShapes.greybox_layer(lane, {}, top, over, thin, post), ZoneMapShapes.LAYER_PAD)
	var rail := {"id": "Rail", "pos": [0, 0.5, 0], "size": [0.6, 1, 30]}
	assert_eq(ZoneMapShapes.greybox_layer(rail, {}, top, over, thin, post), ZoneMapShapes.LAYER_STRUCTURE)
	var house := {"id": "House", "pos": [0, 1.5, 0], "size": [6, 3, 6]}
	assert_eq(ZoneMapShapes.greybox_layer(house, {}, top, over, thin, post), ZoneMapShapes.LAYER_BUILDING)
	var mast := {"id": "Mast", "pos": [0, 4, 0], "size": [0.4, 8, 0.4]}
	assert_eq(ZoneMapShapes.greybox_layer(mast, {}, top, over, thin, post), ZoneMapShapes.LAYER_SKIP, "a post")
	var sail := {"id": "Sail", "pos": [0, 6, 0], "size": [6, 6, 0.1], "solid": false}
	assert_eq(ZoneMapShapes.greybox_layer(sail, {}, top, over, thin, post), ZoneMapShapes.LAYER_SKIP)
	var beam := {"id": "Beam", "pos": [0, 30, 0], "size": [20, 2, 3]}
	assert_eq(ZoneMapShapes.greybox_layer(beam, {}, top, over, thin, post), ZoneMapShapes.LAYER_SKIP, "overhead")
	var sea := {"id": "Sea", "pos": [0, -2, 0], "size": [80, 1, 80]}
	assert_eq(ZoneMapShapes.greybox_layer(sea, {"sea": ["Sea"]}, top, over, thin, post), ZoneMapShapes.LAYER_SEA)
	assert_eq(ZoneMapShapes.greybox_layer(house, {"skip": ["House"]}, top, over, thin, post), ZoneMapShapes.LAYER_SKIP)


func test_a_greybox_block_turns_with_its_yaw() -> void:
	var layout := {"blocks": [{"id": "Plank", "pos": [10, -0.5, 4], "size": [4, 1, 2], "yaw": 90.0}]}
	var data := MapModel.load_data()
	var s := ZoneMapShapes.build(
		ZoneMapShapes.KIND_GREYBOX, layout, Rect2(), data["map"], data["pieces"], data["greybox"], {}
	)
	assert_eq(s.floors.size(), 1)
	var corner := Basis(Vector3.UP, deg_to_rad(90.0)) * Vector3(-2.0, 0.0, -1.0) + Vector3(10.0, 0.0, 4.0)
	assert_true(s.floors[0][0].is_equal_approx(Vector2(corner.x, corner.z)), "Basis(UP, yaw), as GreyboxZone")


func test_oruvel_reads_its_sea_and_the_underway_has_none() -> void:
	var data := MapModel.load_data()
	var oruvel := MapModel.new(&"ch01/oruvel", Vector3.INF, 0.0, _flags([]))
	var s := ZoneMapShapes.build(
		oruvel.shape_kind(),
		oruvel.shape_source(),
		oruvel.bounds(),
		data["map"],
		data["pieces"],
		data["greybox"],
		oruvel.shape_hints()
	)
	assert_eq(s.seas.size(), 1, "the sea under the hulls")
	assert_true(s.floors.size() >= 10, "the hulls and the bridges")
	var under := MapModel.new(UNDERWAY, Vector3.INF, 0.0, _flags([]))
	var u := ZoneMapShapes.build(
		under.shape_kind(), under.shape_source(), under.bounds(), data["map"], data["pieces"], data["greybox"], {}
	)
	assert_eq(u.seas.size(), 0, "a drowned tower: no open water drawn")
	assert_eq(u.floors.size(), 6, "the crown, the bell-room, the galleries, the gauge room, the alcove, the lip")


func test_the_underway_view_marks_the_objective_on_its_tether() -> void:
	var m := MapModel.new(UNDERWAY, Vector3(0.0, 0.0, 15.0), PI, _flags([&"ch01_started"]))
	assert_eq(m.objective_line(), tr("OBJ_U_CROWN_TETHER"))
	assert_eq(m.objective_poi(), &"crown_tether")
	var v := _view(m)
	assert_true(v.objective_marker_at().is_equal_approx(v.map_point(Vector2(0.0, 0.6))), "on the tether")
	assert_true(Rect2(Vector2.ZERO, v.size).has_point(v.objective_marker_at()))
	assert_false(v.shapes.floors.is_empty(), "the view built the greybox shapes")
	v.free()


# --- the view and the page -----------------------------------------------------------------------


func test_the_view_marks_the_objective_and_the_player() -> void:
	var v := _view(_haluna())
	var goal := v.objective_marker_at()
	assert_true(goal.is_equal_approx(v.map_point(Vector2(-67.0, 44.3))), "on the target")
	assert_true(Rect2(Vector2.ZERO, v.size).has_point(goal), "inside the map")
	assert_true(v.player_marker_at().is_equal_approx(v.map_point(Vector2(BEACH.x, BEACH.z))))
	assert_eq(v.poi_at_point(v.poi_marker_at(&"inn")), &"inn", "a glyph is hit where it is drawn")
	assert_eq(v.poi_at_point(Vector2(-100.0, -100.0)), &"")
	assert_between(v.pulse_phase(), 0.0, 1.0)
	v.reduced_motion = true
	assert_eq(v.pulse_phase(), -1.0, "held under reduced motion")
	v.free()
	var lost := _view(MapModel.new(HALUNA, Vector3.INF, 0.0, _flags([])))
	assert_false(lost.player_marker_at().is_finite(), "no player: no arrow")
	assert_false(lost.objective_marker_at().is_finite(), "no objective: no marker")
	lost.free()


func test_the_map_row_opens_the_page_and_input_moves_through_places() -> void:
	_open_menu(_haluna())
	var rows := menu.model.root_rows()
	var at := FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_MAP)
	assert_true(rows[at]["enabled"])
	for i in at:
		menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.desc_text(), tr("FIELD_MENU_MAP_DESC"))
	menu.handle_input(_ev(&"ui_accept"))
	page = menu.map_menu
	assert_true(page != null and page.is_open(), "Map opens the map page")
	assert_false(menu.visible, "the field menu steps aside")
	assert_false(menu.handle_input(_ev(&"ui_down")), "the page takes the input")
	assert_eq(page.title_text(), tr("LOCATION_CH02_HALUNA"))
	assert_eq(page.objective_text(), tr("OBJ_SAVE_AT_SHRINE"))
	assert_eq(page.errands_text(), tr("OBJ_SIDE_TOWN"))
	assert_eq(page.help_text(), tr("MAP_HELP"))
	assert_eq(page.route().current_index(), 2, "Haluna, with Ch1's two stops behind it")
	assert_eq(page.current_poi(), &"shrine", "the cursor starts on the objective's place")
	assert_eq(page.view().highlight, &"shrine")
	assert_true(page.handle_input(_ev(&"ui_down")))
	assert_eq(page.current_poi(), &"chapel")
	assert_eq(page.view().highlight, &"chapel", "the map rings the place under the cursor")
	assert_eq(page.poi_line_text(), page.model.poi_line(&"chapel"))
	page.handle_input(_ev(&"ui_up"))
	page.handle_input(_ev(&"ui_up"))
	assert_eq(page.current_poi(), &"inn")
	assert_true(page.handle_input(_ev(&"ui_cancel")))
	assert_false(page.is_open())
	assert_true(menu.map_menu == null)
	assert_true(menu.visible and menu.is_open(), "back on the field menu")
	_free_menu()


func test_the_mouse_chooses_a_place_on_the_map_or_the_legend() -> void:
	_open_menu(_haluna())
	menu.root_page().set_cursor(FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_MAP), false)
	menu.accept()
	page = menu.map_menu
	page.view().poi_clicked.emit(&"dock")
	assert_eq(page.current_poi(), &"dock", "a click on a glyph")
	page.legend().row_clicked.emit(0)
	assert_eq(page.current_poi(), &"beach", "a click on a legend row")
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_DOWN
	wheel.pressed = true
	assert_true(page.handle_input(wheel))
	assert_eq(page.current_poi(), &"village", "the wheel steps")
	_free_menu()


func test_the_map_row_is_off_where_there_is_no_map() -> void:
	var m := FieldMenuModel.new(GameStateData.new(), [&"rhen"] as Array[StringName], NAMES)
	var at := FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_MAP)
	assert_false(m.root_rows()[at]["enabled"], "no map model: off")
	assert_eq(m.root_rows()[at]["right"], tr("FIELD_MENU_MAP_NONE_TAG"), "and says so on the row")
	assert_eq(m.root_desc(FieldMenuModel.ROW_MAP), tr("FIELD_MENU_MAP_NONE"))
	m.map = MapModel.new(&"nowhere")
	assert_false(m.root_rows()[at]["enabled"], "a zone with no map: off")
	m.map = _haluna()
	assert_true(m.root_rows()[at]["enabled"])
	assert_false(m.root_rows()[at].has("right"))
	_open_menu(null)
	menu.root_page().set_cursor(FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_MAP) - 1, false)
	menu.handle_input(_ev(&"ui_down"))
	assert_ne(menu.root_page().current_row()["id"], FieldMenuModel.ROW_MAP, "the cursor passes the row by")
	menu._accept_root(FieldMenuModel.ROW_MAP)
	assert_true(menu.map_menu == null, "and it opens nothing")
	_free_menu()


func test_the_root_shows_the_objective_where_there_is_a_map() -> void:
	_open_menu(_haluna())
	assert_eq(menu.objective_text(), _haluna().tracker.line(HALUNA), "M2-UI-17: the objective on the root")
	assert_ne(menu.objective_text(), "")
	menu.root_page().set_cursor(FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_SWELL), false)
	menu.accept()
	assert_eq(menu.objective_text(), "", "only on the root")
	_free_menu()
	_open_menu(null)
	assert_eq(menu.objective_text(), "", "no map, no objective block")
	_free_menu()


func test_the_live_model_reads_the_scene_and_the_player() -> void:
	var host := Node3D.new()
	host.add_to_group(&"player")
	host.position = Vector3(3.0, 1.0, -4.0)
	host.rotation.y = 0.5
	_root().add_child(host)
	var m := ZoneMapMenu.live_model(host)
	assert_false(m.has_map(), "the test runner's scene has no map")
	assert_true(m.player_at.is_equal_approx(Vector2(3.0, -4.0)), "the player in group 'player'")
	assert_true(is_equal_approx(m.player_yaw, 0.5))
	var from_game := FieldMenuModel.from_game()
	assert_true(from_game.live_map, "the live menu reads the field when it opens")
	host.queue_free()
	_root().remove_child(host)


# --- helpers -------------------------------------------------------------------------------------


func _flags(on: Array[StringName]) -> Callable:
	return func(f: StringName) -> bool: return on.has(f)


func _haluna() -> MapModel:
	return MapModel.new(HALUNA, BEACH, PI * 0.5, _flags(AT_SHRINE_FLAGS))


func _view(m: MapModel) -> ZoneMapView:
	var v := ZoneMapView.new()
	v.size = Vector2(1035.0, 633.0)
	_root().add_child(v)
	var data := MapModel.load_data()
	v.setup(m, data["map"], data["pieces"], data["greybox"])
	_root().remove_child(v)
	return v


func _open_menu(map: MapModel) -> void:
	var model := FieldMenuModel.new(GameStateData.new(), [&"rhen", &"asha"] as Array[StringName], NAMES)
	model.map = map
	menu = (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(model)
	_root().add_child(menu)


func _free_menu() -> void:
	if menu == null:
		return
	menu.close()
	for child in menu.get_children():
		if child is CanvasLayer:
			child.free()
	menu.get_parent().remove_child(menu)
	menu.free()
	menu = null


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


## ADR 0200 kits: a hint ending in "*" names a kit's numbered pieces, and a zone dressed from a kit reads its
## walkable shape from the layout's collision_path (blocks, and ramps as pads).
func test_kit_dressed_zones_read_their_collision_and_prefix_hints() -> void:
	assert_true(ZoneMapShapes.hint_names("Wall-*", "Wall-10"))
	assert_false(ZoneMapShapes.hint_names("Wall-*", "WallSection"), "a prefix, not a substring")
	assert_true(ZoneMapShapes.hint_names("WallSection", "WallSection"))
	assert_false(ZoneMapShapes.hint_names("WallSection", "WallSectionKerb"), "no star: the id itself")
	var data := MapModel.load_data()
	var m := MapModel.new(&"ch08/coilspire", Vector3.INF, 0.0, _flags([]))
	var s := ZoneMapShapes.build(
		m.shape_kind(), m.shape_source(), m.bounds(), data["map"], data["pieces"], data["greybox"], m.shape_hints()
	)
	assert_true(s.pads.size() >= 89, "every ramp of the spire's flights is ground to walk")
