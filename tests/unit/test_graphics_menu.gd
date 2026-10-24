extends TestCase
## M1-UI-10: the Graphics settings page (GraphicsMenu over GraphicsMenuModel) and the title's
## Settings row. The settings file is the test's own; changes apply to a SubViewport of the test's,
## so the runner's own viewport keeps its settings.

const CONFIG := "user://test_graphics_menu.cfg"
const TEST_DIR := "user://test_graphics_menu_saves"

var vp: SubViewport
var menu: GraphicsMenu
var _saved_dir := ""


func before_each() -> void:
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CONFIG))
	GraphicsRuntime.config_path = CONFIG
	GraphicsRuntime.set_settings(null)
	GraphicsRuntime.armed = false
	vp = SubViewport.new()
	_host().add_child(vp)
	_saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = TEST_DIR


func _open() -> GraphicsMenu:
	menu = GraphicsMenu.new(vp)
	_host().add_child(menu)
	return menu


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func test_rows_are_the_preset_then_every_setting_with_its_value() -> void:
	_open()
	var gs := GraphicsRuntime.settings()
	var ids := menu.model.row_ids()
	assert_eq(ids[0], GraphicsMenuModel.ROW_PRESET)
	assert_eq(ids.size(), (gs.data["settings"] as Dictionary).size() + 1, "one row per setting")
	assert_eq(menu.value_shown(GraphicsMenuModel.ROW_PRESET), tr("GFX_PRESET_" + gs.preset_id.to_upper()))
	for id in ids.slice(1):
		var shown := menu.value_shown(id)
		assert_true(shown != "" and not shown.begins_with("GFX_"), "%s shows a translated value: %s" % [id, shown])
	assert_eq(menu.model.format_value("render_scale", 0.77), "77%")
	assert_eq(menu.model.format_value("ssr", true), tr("GFX_VALUE_ON"))
	assert_eq(menu.model.format_value("aa", "msaa_2x"), tr("GFX_VALUE_MSAA_2X"))
	_done()


func test_selecting_low_saves_and_applies_it() -> void:
	_open()
	var ids := GraphicsRuntime.settings().preset_ids()
	var guard := 0
	while GraphicsRuntime.settings().preset_id != "low" and guard < ids.size():
		guard += 1
		menu.handle_input(_action(&"ui_right"))
	assert_eq(GraphicsRuntime.settings().preset_id, "low")
	assert_eq(menu.value_shown(GraphicsMenuModel.ROW_PRESET), tr("GFX_PRESET_LOW"))
	var cfg := ConfigFile.new()
	assert_eq(cfg.load(CONFIG), OK, "the choice is saved")
	var reread := GraphicsSettings.new()
	reread.load_config(CONFIG)
	assert_eq(reread.preset_id, "low", "and reads back as Low")
	var low: Dictionary = GraphicsRuntime.settings().resolve()
	var scaling := str(low.get("scaling_mode", ""))
	if scaling == "fsr":
		assert_eq(vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR, "applied to the viewport at once")
	assert_between(vp.scaling_3d_scale, float(low["render_scale"]) - 0.001, float(low["render_scale"]) + 0.001)
	_done()


func test_changing_one_setting_makes_the_preset_custom() -> void:
	_open()
	menu.model.set_cursor(menu.model.row_ids().find(&"ssr"))
	var before: Variant = GraphicsRuntime.settings().resolve()["ssr"]
	assert_true(menu.handle_input(_action(&"ui_right")))
	assert_ne(GraphicsRuntime.settings().resolve()["ssr"], before, "the value stepped")
	assert_true(GraphicsRuntime.settings().is_custom())
	assert_eq(menu.value_shown(GraphicsMenuModel.ROW_PRESET), tr("GFX_PRESET_CUSTOM"))
	assert_eq(menu.help_text(), tr("GFX_MENU_HELP_SETTING"))
	var reread := GraphicsSettings.new()
	reread.load_config(CONFIG)
	assert_true(reread.is_custom(), "the override is saved")
	menu.handle_input(_action(&"ui_left"))
	assert_eq(GraphicsRuntime.settings().resolve()["ssr"], before, "left steps back")
	_done()


func test_cycling_wraps_through_every_option() -> void:
	_open()
	var key := "aa"
	menu.model.set_cursor(menu.model.row_ids().find(StringName(key)))
	var options := GraphicsRuntime.settings().setting_options(key)
	var start: Variant = GraphicsRuntime.settings().resolve()[key]
	var seen: Array = []
	for _i in options.size():
		menu.model.cycle(1)
		seen.append(GraphicsRuntime.settings().resolve()[key])
	assert_eq(seen.size(), options.size())
	assert_eq(seen[-1], start, "a full lap comes back")
	for o: Variant in options:
		assert_true(o in seen, "%s reached" % str(o))
	_done()


func test_cancel_closes_the_page() -> void:
	_open()
	var closed := [false]
	menu.closed.connect(func() -> void: closed[0] = true)
	assert_true(menu.handle_input(_action(&"ui_cancel")))
	assert_true(closed[0])
	assert_false(menu.is_open())
	assert_false(menu.handle_input(_action(&"ui_down")), "a closed page takes no input")
	_done()


func test_the_title_settings_row_opens_the_page_and_holds_title_input() -> void:
	var title := TitleMenu.new()
	title.save_system = SaveSystem
	_host().add_child(title)
	assert_true(title.model.is_enabled(TitleMenuModel.CHOICE_SETTINGS), "Settings needs no record")
	assert_true(title.row_labels().has(tr("TITLE_SETTINGS")))
	assert_true(title.model.set_cursor(TitleMenuModel.CHOICES.find(TitleMenuModel.CHOICE_SETTINGS)))
	assert_eq(title.help_text(), tr("TITLE_HELP_SETTINGS"), "its own help even with no record")
	assert_eq(title.choose(TitleMenuModel.CHOICE_SETTINGS), OK)
	assert_true(title.is_graphics_menu_open())
	assert_false(title.handle_input(_action(&"ui_down")), "the page has the input, not the title")
	title.graphics_menu.close()
	assert_false(title.is_graphics_menu_open())
	assert_true(title.handle_input(_action(&"ui_down")), "back to the title")
	title.get_parent().remove_child(title)
	title.free()
	_done()


func _done() -> void:
	if menu != null and is_instance_valid(menu):
		if menu.get_parent() != null:
			menu.get_parent().remove_child(menu)
		menu.free()
	if is_instance_valid(vp):
		vp.get_parent().remove_child(vp)
		vp.free()
	GraphicsRuntime.set_settings(null)
	GraphicsRuntime.config_path = GraphicsSettings.CONFIG_PATH
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CONFIG))
	SaveSystem.save_dir = _saved_dir


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
