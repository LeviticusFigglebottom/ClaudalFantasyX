extends TestCase
## M2-UI-18: the zone map (MapModel, ZoneMapShapes, ZoneMapView, RouteStrip, ZoneMapMenu) and the
## field menu's Map row: world -> map, places in order, the objective's marker on its target, the
## player's arrow, the shapes drawn from Haluna's layout and the Shell Shrine's trial, the row that
## is off where there is no map, and keyboard and mouse input.

const HALUNA := &"ch02/haluna"
const SHRINE := &"ch03/shell_shrine"
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
	assert_eq(early.objective_line(), tr("OBJ_NONE"))
	assert_false(early.objective_at().is_finite())
	assert_eq(early.errands_text(), tr("MAP_ERRANDS_NONE"))
	assert_eq(early.first_index(), 0)
	var trial := MapModel.new(SHRINE, Vector3.INF, 0.0, _flags([]))
	assert_eq(trial.objective_poi(), &"inner_pool", "the trial's line points at the inner pool")


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
	assert_eq(stops.size(), 3)
	assert_eq(stops[0]["name"], tr("MAP_ROUTE_HALUNA"))
	assert_eq([stops[0]["current"], stops[1]["current"], stops[2]["current"]], [true, false, false])
	var at_shrine := MapModel.new(SHRINE, Vector3.INF, 0.0, _flags([])).route_stops()
	assert_eq([at_shrine[0]["current"], at_shrine[2]["current"]], [false, true])
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
	assert_eq(page.route().current_index(), 0)
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
	v.setup(m, data["map"], data["pieces"])
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
