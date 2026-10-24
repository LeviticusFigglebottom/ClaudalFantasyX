extends TestCase
## M2-MNU-303: menu motion. The field menu and its pages fade and rise in, fade and sink out
## (MenuMotion, menu_motion.json), the cursor eases between rows (MenuPage), Reduced motion makes all
## of it instant, and audio's ui_sfx hooks reach every page of the menus track. The runner has no
## after_each and runs no frames: each test drives the tweens through their API (MenuMotion.advance /
## finish, MenuPage.settle) and frees what it opened.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
## capture.sh runs the capture at --fixed-fps 60.
const CAPTURE_FPS := 60.0
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}

var played: Array = []
var _saved_settings: UiSettings
var _host: Node


func before_each() -> void:
	_saved_settings = UiSettings.shared()
	UiSettings.set_shared(UiSettings.new())
	_host = Node.new()
	_root().add_child(_host)
	played = []


func test_the_data_holds_every_duration_and_they_settle_inside_a_capture() -> void:
	var d := MenuMotion.load_data()
	for k in ["open_sec", "close_sec", "return_sec", "slide_px"]:
		assert_true(float(d.get(k, 0.0)) > 0.0, "%s is set" % k)
	var shots := JSON.parse_string(FileAccess.get_file_as_string("res://tests/screenshots/shots.json")) as Dictionary
	var settle := float((shots["defaults"] as Dictionary)["settle_frames"]) / CAPTURE_FPS
	for k in ["open_sec", "close_sec", "return_sec"]:
		assert_true(float(d[k]) < settle, "%s ends before a capture's settle frames do" % k)
	_done()


func test_a_page_fades_and_rises_in_and_comes_to_rest() -> void:
	var page := StatusMenu.open_in(_host, _sheet())
	var m := page.motion()
	var rest_top := page.offset_top
	assert_true(m.is_moving(), "the open transition runs")
	assert_eq(page.modulate.a, 1.0, "nothing is written before its first step (a test that runs no frames)")
	var settled := [false]
	m.settled.connect(func() -> void: settled[0] = true)
	m.advance(m.seconds("open_sec") * 0.25)
	assert_between(page.modulate.a, 0.01, 0.99, "mid-way it is part faded")
	assert_true(page.offset_top > rest_top, "and lower than at rest")
	assert_true(page.is_open(), "open (and taking input) while it comes in")
	assert_true(page.handle_input(_ev(&"ui_down")))
	m.finish()
	assert_true(settled[0], "settled")
	assert_eq(page.modulate.a, 1.0)
	assert_eq(page.offset_top, rest_top, "exactly where it rests")
	assert_false(m.is_moving())
	page.close()
	m.finish()
	_done()


func test_close_refuses_input_at_once_emits_closed_and_frees_after_the_fade() -> void:
	var page := StatusMenu.open_in(_host, _sheet())
	page.motion().finish()
	var layer := page.get_parent() as CanvasLayer
	var seen: Array[String] = []
	page.closed.connect(func() -> void: seen.append("closed"))
	page.gone.connect(func() -> void: seen.append("gone"))
	page.close()
	assert_eq(seen, ["closed"] as Array[String], "closed at once, before the fade")
	assert_false(page.is_open())
	assert_false(page.handle_input(_ev(&"ui_down")), "input refused while it closes")
	assert_false(page.handle_input(_ev(&"ui_cancel")))
	assert_eq(page.list_page().row_node(0).mouse_filter, Control.MOUSE_FILTER_IGNORE, "nor the pointer")
	assert_false(page.get_tree().paused, "the pause lifts at once")
	assert_true(page.visible, "still drawn while it fades")
	assert_false(layer.is_queued_for_deletion())
	page.motion().advance(page.motion().seconds("close_sec") * 0.5)
	assert_between(page.modulate.a, 0.01, 0.99, "fading")
	page.motion().finish()
	assert_eq(seen, ["closed", "gone"] as Array[String])
	assert_false(page.visible)
	assert_true(layer.is_queued_for_deletion(), "the layer frees itself once it has faded")
	page.close()
	assert_eq(seen.size(), 2, "a second close does nothing")
	_done()


func test_reduced_motion_makes_open_and_close_instant() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	var page := StatusMenu.open_in(_host, _sheet())
	var layer := page.get_parent() as CanvasLayer
	assert_false(page.motion().is_moving(), "no open transition")
	assert_eq(page.modulate.a, 1.0)
	assert_true(page.list_page().reduced_motion, "its pages get it too")
	var seen: Array[String] = []
	page.closed.connect(func() -> void: seen.append("closed"))
	page.gone.connect(func() -> void: seen.append("gone"))
	page.close()
	assert_eq(seen.size(), 2, "closed and gone at once")
	assert_true(seen.has("closed") and seen.has("gone"))
	assert_false(page.visible, "hidden at once")
	assert_true(layer.is_queued_for_deletion())
	assert_false(page.motion().is_moving())
	_done()


func test_a_page_over_the_field_menu_keeps_the_backdrop_still_and_the_menu_comes_back() -> void:
	var menu := FieldMenu.open_in(_host, FieldMenuModel.new(GameStateData.new(), HEROES, NAMES))
	menu.motion().advance(menu.motion().seconds("open_sec") * 0.5)
	assert_between(menu.modulate.a, 0.01, 0.99, "the field menu fades in over the field, scrim and all")
	menu.motion().finish()
	menu.root_page().set_cursor(FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_STATUS), false)
	menu.accept()
	var page := menu.child
	assert_true(page != null and page.over_menu, "the field menu's page opens over it")
	page.motion().advance(page.motion().seconds("open_sec") * 0.25)
	var covers := page.get_meta(UiFrame.META_COVERS) as Array
	assert_true(covers.size() >= 2, "scrim, caustics (and the catcher)")
	for c: Variant in covers:
		assert_eq((c as CanvasItem).modulate.a, 1.0, "the backdrop stays at full strength")
	assert_eq(page.modulate.a, 1.0, "the page itself is not faded")
	assert_between(page.list_page().modulate.a, 0.01, 0.99, "its content is")
	page.motion().finish()
	assert_eq(page.list_page().modulate.a, 1.0)
	page.handle_input(_ev(&"ui_cancel"))
	assert_true(menu.child == null and menu.visible, "the menu is back at once")
	assert_true(menu.motion().is_moving(), "its content fades back in")
	assert_eq(menu.modulate.a, 1.0, "over its own still backdrop")
	for c: Variant in page.get_meta(UiFrame.META_COVERS) as Array:
		assert_false((c as CanvasItem).visible, "the closing page's backdrop goes at once (no double scrim)")
	menu.motion().advance(menu.motion().seconds("return_sec") * 0.5)
	assert_between(menu.root_page().modulate.a, 0.01, 0.99)
	menu.motion().finish()
	page.motion().finish()
	assert_eq(menu.root_page().modulate.a, 1.0)
	menu.close()
	menu.motion().finish()
	assert_true(menu.get_parent().is_queued_for_deletion())
	_done()


func test_closing_while_coming_in_fades_out_from_where_it_was() -> void:
	var page := StatusMenu.open_in(_host, _sheet())
	var m := page.motion()
	m.advance(m.seconds("open_sec") * 0.25)
	var mid := m.progress
	page.close()
	m.advance(0.0)
	assert_true(m.progress <= mid, "it turns back from where it was")
	m.finish()
	assert_eq(m.progress, 0.0)
	assert_false(page.visible)
	_done()


func test_the_cursor_eases_to_its_row_and_reduced_motion_jumps() -> void:
	var page := StatusMenu.open_in(_host, _sheet())
	page.motion().finish()
	var list := page.list_page()
	list.settle()
	var at0 := list.cursor_rect()
	assert_eq(at0.position, list.row_rect(0).position)
	assert_true(list.move(1))
	assert_eq(list.cursor_rect().position, at0.position, "the cursor has not jumped (no frame yet)")
	list.settle()
	assert_eq(list.cursor_rect().position, list.row_rect(1).position, "it eases to the new row")
	assert_eq(list.cursor_rect().size, list.row_rect(1).size)
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	assert_true(list.reduced_motion, "a Settings change reaches an open page's cursors")
	assert_true(list.move(1))
	assert_eq(list.cursor_rect().position, list.row_rect(2).position, "Reduced motion: it jumps")
	page.close()
	_done()


func test_menus_track_hooks_read_on_every_real_page() -> void:
	var ui := UiAudio.new(AudioData.table(AudioData.UI_SFX))
	ui.player = func(id: StringName) -> void: played.append(id)
	_host.add_child(ui)
	var sheet := _sheet()
	var memories := MemoriesModel.new(MemoriesModel.load_data(), [] as Array[GameStateData])
	var field := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	field.pause_tree = false
	field.configure(FieldMenuModel.new(GameStateData.new(), HEROES, NAMES))
	var pages: Array[Control] = [
		field,
		LatticeMenu.create(sheet),
		EquipMenu.create(sheet),
		ItemsMenu.create(sheet),
		FormationMenu.create(sheet),
		StatusMenu.create(sheet),
		MemoriesMenu.create(memories),
		BattlePauseMenu.create(),
	]
	for p in pages:
		var sub := p as FieldSubmenu
		if sub != null:
			sub.pause_tree = false
		_host.add_child(p)
		var cls := String((p.get_script() as Script).get_global_name())
		assert_true(ui.wants(p), "%s has a hook" % cls)
		var hook := ui.hook_for(p)
		assert_eq(str(hook.get("class", "")), cls, "%s has its own row" % cls)
		assert_false(bool(hook.get("pending", false)), "%s's row is live" % cls)
		assert_true(
			hook.has("on_enter") and (hook.get("signals", {}) as Dictionary).has("closed"), "%s opens and closes" % cls
		)
		ui.watch(p)
		var w: Dictionary = ui.watched[-1]
		for x: Dictionary in w["watch"]:
			var e := x["expr"] as Expression
			e.execute([p], ui, false)
			assert_false(e.has_execute_failed(), "%s: %s reads" % [cls, (x["row"] as Dictionary)["expr"]])
	ui.step()
	played.clear()
	var status := pages[5] as StatusMenu
	status.handle_input(_ev(&"ui_down"))
	ui.step()
	assert_eq(played, [&"ui_cursor"], "the Status page's cursor ticks")
	played.clear()
	var pause := pages[7] as BattlePauseMenu
	pause.handle_input(_ev(&"ui_down"))
	ui.step()
	assert_eq(played, [&"ui_cursor"], "and the battle pause's")
	played.clear()
	status.close()
	ui.step()
	assert_eq(played, [&"ui_menu_close"], "a page closing plays its close")
	for p in pages:
		if p is FieldSubmenu:
			(p as FieldSubmenu).close()
		elif p is FieldMenu:
			(p as FieldMenu).close()
	_done()


# --------------------------------------------------------------------------- helpers


func _sheet() -> PartySheet:
	var state := GameStateData.new()
	state.party_ids = HEROES.duplicate()
	return PartySheet.new(state, HEROES)


func _done() -> void:
	var tree := _host.get_tree()
	tree.paused = false
	_root().remove_child(_host)
	_host.free()
	_host = null
	UiSettings.set_shared(_saved_settings)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
