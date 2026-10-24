extends TestCase
## M2-UI-09: the Settings hub (SettingsMenu: Graphics, Accessibility), the Accessibility page
## (AccessibilityMenu over AccessibilityMenuModel and UiSettings), UiSettings.follow (menus outside
## battle take the text size and palette live), and the polish-pass fixes in the field menu,
## the bestiary and the title. Each test runs on its own UiSettings (set as the shared one) and
## saves nothing.

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA"}

var s: UiSettings
var made: Array[Node] = []


func before_each() -> void:
	s = UiSettings.new()
	UiSettings.set_shared(s)
	made.clear()


## Frees what a test made and puts the shared settings back (the runner has no after_each).
func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()
	(Engine.get_main_loop() as SceneTree).paused = false
	UiSettings.set_shared(null)


func test_the_accessibility_rows_are_the_settings_with_their_values() -> void:
	var m := AccessibilityMenuModel.new(s, "")
	assert_eq(m.row_ids(), s.settings())
	assert_eq(m.label(UiSettings.TEXT_SCALE), tr("SET_TEXT_SCALE"))
	assert_eq(m.value_text(UiSettings.REDUCED_MOTION), tr("GFX_VALUE_OFF"))
	assert_eq(m.value_text(UiSettings.TEXT_SCALE), tr("SET_TEXT_SCALE_100"))
	assert_eq(m.value_text(UiSettings.PALETTE), tr("SET_PALETTE_STANDARD"))
	assert_eq(m.value_text(UiSettings.TIMING_ASSIST), tr("SET_TIMING_ASSIST_OFF"))
	m.set_cursor(m.row_ids().find(UiSettings.TEXT_SCALE))
	assert_eq(m.help_key(), "SET_TEXT_SCALE_HELP")
	_done()


func test_cycling_steps_through_the_options_and_wraps() -> void:
	var m := AccessibilityMenuModel.new(s, "")
	m.set_cursor(m.row_ids().find(UiSettings.TEXT_SCALE))
	assert_true(m.cycle(1))
	assert_true(is_equal_approx(s.text_scale(), 1.15))
	assert_eq(m.value_text(UiSettings.TEXT_SCALE), tr("SET_TEXT_SCALE_115"))
	assert_true(m.cycle(1))
	assert_true(m.cycle(1), "past the last option it wraps")
	assert_true(is_equal_approx(s.text_scale(), 1.0))
	assert_true(m.cycle(-1), "left steps back")
	assert_true(is_equal_approx(s.text_scale(), 1.3))
	m.set_cursor(m.row_ids().find(UiSettings.REDUCED_MOTION))
	assert_true(m.cycle(1))
	assert_true(s.reduced_motion())
	assert_eq(m.value_text(UiSettings.REDUCED_MOTION), tr("GFX_VALUE_ON"))
	_done()


func test_a_change_is_saved_at_once() -> void:
	var path := "user://test_settings_menu.cfg"
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	var m := AccessibilityMenuModel.new(s, path)
	m.set_cursor(m.row_ids().find(UiSettings.PALETTE))
	assert_true(m.cycle(1))
	var back := UiSettings.new()
	back.load_from(path)
	assert_eq(back.palette(), &"colorblind", "the file holds the new palette")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	_done()


func test_follow_re_themes_a_menu_live_and_stops_when_it_leaves() -> void:
	var root := Control.new()
	_add(root)
	s.follow(root)
	var base := root.theme
	assert_true(base != null, "a root with no theme gets the Hymn theme")
	s.set_value(UiSettings.TEXT_SCALE, 1.3)
	assert_ne(root.theme, base, "a bigger text size swaps the theme")
	var body := root.theme.get_font_size(&"font_size", &"BodyLabel")
	assert_eq(body, roundi(base.get_font_size(&"font_size", &"BodyLabel") * 1.3))
	s.set_value(UiSettings.TEXT_SCALE, 1.0)
	assert_eq(root.theme, base, "back at the defaults it is the base theme again")
	root.get_parent().remove_child(root)
	s.set_value(UiSettings.TEXT_SCALE, 1.15)
	assert_eq(root.theme, base, "a root out of the tree is no longer followed")
	_done()


func test_the_hub_opens_each_page_and_comes_back() -> void:
	var hub := SettingsMenu.new()
	hub.ui_settings = s
	hub.save_path = ""
	hub.graphics_viewport = SubViewport.new()
	_add(hub.graphics_viewport)
	_add(hub)
	var labels := PackedStringArray([tr("SET_MENU_GRAPHICS"), tr("SET_MENU_ACCESSIBILITY"), tr("SET_MENU_CONTROLS")])
	assert_eq(hub.row_labels(), labels)
	assert_eq(hub.help_text(), tr("SET_MENU_HELP_GRAPHICS"))
	assert_true(hub.handle_input(_ev(&"ui_down")))
	assert_eq(hub.current(), SettingsMenu.ROW_ACCESSIBILITY)
	assert_eq(hub.help_text(), tr("SET_MENU_HELP_ACCESSIBILITY"))
	assert_true(hub.handle_input(_ev(&"ui_accept")))
	assert_true(hub.page is AccessibilityMenu)
	var page := hub.page as AccessibilityMenu
	assert_eq(page.model.settings, s, "the page edits the hub's settings")
	page.model.set_cursor(page.model.row_ids().find(UiSettings.TEXT_SCALE))
	assert_true(hub.handle_input(_ev(&"ui_right")), "the open page takes the input")
	assert_eq(page.value_shown(UiSettings.TEXT_SCALE), tr("SET_TEXT_SCALE_115"))
	assert_ne(page.theme, null)
	assert_true(hub.handle_input(_ev(&"ui_cancel")), "cancel closes the page")
	assert_false(hub.is_page_open())
	assert_true(hub.is_open(), "the hub is still open")
	assert_eq(hub.current(), SettingsMenu.ROW_ACCESSIBILITY, "the cursor stayed")
	var closed := [false]
	hub.closed.connect(func() -> void: closed[0] = true)
	assert_true(hub.handle_input(_ev(&"ui_cancel")))
	assert_true(closed[0])
	_done()


func test_the_field_menu_settings_row_opens_the_hub_over_it() -> void:
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(FieldMenuModel.new(GameStateData.new(), [&"rhen"] as Array[StringName], NAMES))
	_add(menu)
	for i in FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_SETTINGS):
		menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.desc_text(), tr("FIELD_MENU_SETTINGS_DESC"))
	menu.accept()
	var hub := menu.settings_menu
	assert_true(hub != null and hub.is_open(), "Settings opens the hub")
	assert_false(menu.visible, "the field menu steps aside")
	var layer := hub.get_parent() as CanvasLayer
	assert_true(layer.layer > int(BestiaryMenu.load_data()["canvas_layer"]), "over the field menu and bestiary")
	assert_eq(layer.process_mode, Node.PROCESS_MODE_ALWAYS, "it works while the field is paused")
	assert_false(menu.handle_input(_ev(&"ui_down")), "the hub takes the input")
	hub.close()
	assert_true(menu.settings_menu == null)
	assert_true(menu.visible)
	assert_true(menu.handle_input(_ev(&"ui_down")))
	menu.close()
	_done()


func test_the_field_menu_follows_the_text_size() -> void:
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(FieldMenuModel.new(GameStateData.new(), [&"rhen"] as Array[StringName], NAMES))
	_add(menu)
	var base := menu.theme
	s.set_value(UiSettings.TEXT_SCALE, 1.3)
	assert_ne(menu.theme, base)
	menu.close()
	_done()


func test_the_field_swell_mode_in_use_reads_in_the_swell_color() -> void:
	var m := FieldMenuModel.new(GameStateData.new(), [&"rhen"] as Array[StringName], NAMES)
	for row in m.mode_page_rows(&"rhen"):
		assert_eq(StringName(str(row["right_role"])), &"swell", "as on the battle Swell page")
	_done()


func test_the_bestiary_jumps_a_page_and_takes_the_wheel() -> void:
	var enemies := BattleFixture.load_fixture(&"read_panel").db.enemies
	var log := {"gull_harrier": {"read": true, "defeated": 4}, "reef_crab": {"read": false, "defeated": 2}}
	var menu := (load(BestiaryMenu.SCENE_PATH) as PackedScene).instantiate() as BestiaryMenu
	menu.pause_tree = false
	menu.configure(BestiaryMenuModel.new(Bestiary.new(log), enemies))
	_add(menu)
	var last := menu.entries().size() - 1
	assert_true(menu.handle_input(_ev(&"ui_page_down")))
	assert_eq(menu.current_id, StringName(str(menu.entries()[last]["id"])), "a page down stops at the end")
	assert_true(menu.handle_input(_ev(&"ui_left")), "left is a page up on a pad")
	assert_eq(menu.current_id, StringName(str(menu.entries()[0]["id"])))
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_DOWN
	wheel.pressed = true
	assert_true(menu.handle_input(wheel))
	assert_eq(menu.current_id, StringName(str(menu.entries()[1]["id"])), "the wheel steps one row")
	menu.close()
	_done()


func test_hovering_a_title_row_moves_the_title_s_cursor_and_help() -> void:
	var title := TitleMenu.new()
	title.save_system = SaveSystem
	_add(title)
	var at := TitleMenuModel.CHOICES.find(TitleMenuModel.CHOICE_SETTINGS)
	var page: MenuPage
	for c in title.get_children():
		if c is MenuPage:
			page = c
	page.row_hovered.emit(at)
	assert_eq(title.model.row_cursor(), at, "the model follows the hover")
	assert_eq(title.help_text(), tr("TITLE_HELP_SETTINGS"))
	_done()


func test_the_graphics_value_formats_are_loc_keys() -> void:
	var m := GraphicsMenuModel.new(null)
	assert_eq(m.format_value("render_scale", 0.5), tr("GFX_VALUE_PERCENT_FMT").format({"n": 50}))
	assert_eq(m.format_value("lod_threshold", 2.0), tr("GFX_VALUE_TIMES_FMT").format({"n": str(2.0)}))
	assert_eq(m.title_key(), "GFX_MENU_TITLE")
	_done()


# --- helpers ------------------------------------------------------------------------------


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
