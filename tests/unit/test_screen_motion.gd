extends TestCase
## M2-MNU-305: the UI track's own screens move like the field menu's pages (MenuMotion, M2-MNU-303).
## The bestiary, the codex, the zone map and the Settings hub fade and rise in over the field menu with
## its backdrop held still, and fade out after `closed` (emitted at once), freeing their layer on
## `gone`. A Settings page crosses over the hub; the save menu fades out. Reduced motion makes all of it
## instant. The runner has no after_each and runs no frames: each test drives the tweens through
## MenuMotion.advance / finish and frees what it opened.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}

var _saved_settings: UiSettings
var _host: Node


func before_each() -> void:
	_saved_settings = UiSettings.shared()
	UiSettings.set_shared(UiSettings.new())
	_host = Node.new()
	_root().add_child(_host)


func test_each_screen_over_the_field_menu_moves_only_its_content_and_frees_after_the_fade() -> void:
	for screen: Control in _screens(true):
		var label := screen.get_script().get_global_name() as String
		var m := screen.call(&"motion") as MenuMotion
		assert_true(m.is_moving(), "%s: the open transition runs" % label)
		m.advance(m.seconds("open_sec") * 0.25)
		for c: Variant in screen.get_meta(UiFrame.META_COVERS) as Array:
			assert_eq((c as CanvasItem).modulate.a, 1.0, "%s: the backdrop stays at full strength" % label)
		assert_eq(screen.modulate.a, 1.0, "%s: the screen itself is not faded" % label)
		assert_true(_content_alpha(screen) < 0.99, "%s: its content is" % label)
		m.finish()
		assert_eq(_content_alpha(screen), 1.0, "%s: at rest" % label)
		var layer := screen.get_parent() as CanvasLayer
		var seen: Array[String] = []
		screen.connect(&"closed", func() -> void: seen.append("closed"))
		screen.connect(&"gone", func() -> void: seen.append("gone"))
		screen.call(&"close")
		assert_eq(seen, ["closed"] as Array[String], "%s: closed at once, before the fade" % label)
		assert_false(bool(screen.call(&"is_open")), "%s: input refused while it fades" % label)
		assert_false(screen.get_tree().paused, "%s: the pause lifts at once" % label)
		assert_true(screen.visible and not layer.is_queued_for_deletion(), "%s: still drawn while it fades" % label)
		m.finish()
		assert_eq(seen, ["closed", "gone"] as Array[String], label)
		assert_true(layer.is_queued_for_deletion(), "%s: the layer frees itself once it has faded" % label)
	_done()


func test_over_the_open_world_the_backdrop_fades_with_the_screen() -> void:
	for screen: Control in _screens(false):
		var label := screen.get_script().get_global_name() as String
		var m := screen.call(&"motion") as MenuMotion
		m.advance(m.seconds("open_sec") * 0.25)
		assert_between(screen.modulate.a, 0.01, 0.99, "%s: scrim and all fade in" % label)
		m.finish()
		assert_eq(screen.modulate.a, 1.0, label)
		screen.call(&"close")
		m.finish()
	_done()


func test_reduced_motion_makes_every_screen_instant() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	for screen: Control in _screens(true):
		var label := screen.get_script().get_global_name() as String
		var m := screen.call(&"motion") as MenuMotion
		assert_false(m.is_moving(), "%s: no open transition" % label)
		assert_eq(_content_alpha(screen), 1.0, label)
		var layer := screen.get_parent() as CanvasLayer
		var seen: Array[String] = []
		screen.connect(&"gone", func() -> void: seen.append("gone"))
		screen.call(&"close")
		assert_eq(seen.size(), 1, "%s: gone at once" % label)
		assert_false(screen.visible, "%s: hidden at once" % label)
		assert_true(layer.is_queued_for_deletion(), label)
	_done()


func test_the_field_menu_opens_each_screen_over_itself() -> void:
	var menu := FieldMenu.open_in(_host, FieldMenuModel.new(GameStateData.new(), HEROES, NAMES))
	menu.motion().finish()
	menu.call(&"_open_bestiary")
	assert_true(menu.bestiary.over_menu, "the bestiary")
	menu.bestiary.close()
	menu.motion().finish()
	menu.call(&"_open_settings")
	assert_true(menu.settings_menu.over_menu, "the Settings hub")
	menu.settings_menu.close()
	menu.motion().finish()
	menu.call(&"_open_codex")
	assert_true(menu.codex_menu.over_menu, "the codex")
	var codex := menu.codex_menu
	codex.close()
	assert_true(menu.visible and menu.motion().is_moving(), "the menu is back at once and fades its rows in")
	assert_true(codex.motion().is_moving(), "while the codex fades out over it")
	codex.motion().finish()
	menu.motion().finish()
	menu.close()
	menu.motion().finish()
	_done()


func test_a_settings_page_crosses_over_the_hub() -> void:
	var hub := SettingsMenu.open_in(_host, true)
	hub.motion().finish()
	var page := hub.open_page(SettingsMenu.ROW_ACCESSIBILITY)
	assert_true(page.motion().is_moving(), "the page comes in")
	page.motion().advance(page.motion().seconds("open_sec") * 0.25)
	for c: Variant in page.get_meta(UiFrame.META_COVERS) as Array:
		assert_eq((c as CanvasItem).modulate.a, 1.0, "over the hub's own backdrop: it stays still")
	page.motion().finish()
	page.close()
	assert_false(hub.is_page_open(), "the hub has the input back at once")
	assert_true(hub.motion().is_moving(), "its rows fade back in")
	assert_true(page.motion().is_moving() and not page.is_queued_for_deletion(), "while the page fades out")
	page.motion().finish()
	hub.motion().finish()
	assert_true(page.is_queued_for_deletion(), "the page frees itself once it has faded")
	hub.close()
	hub.motion().finish()
	assert_true(hub.is_queued_for_deletion())
	_done()


func test_the_save_menu_fades_out_after_closed() -> void:
	var menu := SaveMenu.open_in(_host, SaveMenuModel.Mode.LOAD, {}, "", SaveSystem)
	var layer := menu.get_parent() as CanvasLayer
	var seen: Array[String] = []
	menu.closed.connect(func(_o: SaveMenuModel.Outcome) -> void: seen.append("closed"))
	menu.gone.connect(func() -> void: seen.append("gone"))
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(seen, ["closed"] as Array[String], "closed at once")
	assert_true(menu.visible and menu.motion().is_moving(), "then it fades")
	menu.motion().finish()
	assert_eq(seen, ["closed", "gone"] as Array[String])
	assert_true(layer.is_queued_for_deletion())
	_done()


func test_reduced_motion_skips_the_save_menu_panel_rise() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	var menu := SaveMenu.open_in(_host, SaveMenuModel.Mode.LOAD, {}, "", SaveSystem)
	for n in menu.find_children("*", "Control", true, false):
		assert_eq((n as Control).scale, Vector2.ONE, "no panel scaled for a rise: %s" % n.name)
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.visible, "and it closes at once")
	_done()


# --- helpers ------------------------------------------------------------------------------------


## The four screens the field menu opens, each on its own layer under the host.
func _screens(over: bool) -> Array[Control]:
	var enemies := BattleFixture.load_fixture(&"read_panel").db.enemies
	var out: Array[Control] = [
		BestiaryMenu.open_in(_host, BestiaryMenuModel.new(Bestiary.new({}), enemies), over),
		CodexMenu.open_in(
			_host, CodexModel.new(CodexModel.load_data(), func(_f: StringName) -> bool: return true), over
		),
		ZoneMapMenu.open_in(_host, MapModel.new(&"nowhere"), over),
		SettingsMenu.open_in(_host, over),
	]
	return out


## The lowest alpha among the screen's content (its non-cover children).
func _content_alpha(screen: Control) -> float:
	var covers := screen.get_meta(UiFrame.META_COVERS, []) as Array
	var low := 1.0
	for c in screen.get_children():
		if c is CanvasItem and not covers.has(c):
			low = minf(low, (c as CanvasItem).modulate.a)
	return low


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
