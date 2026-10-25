extends TestCase
## M2-UI-13: the Controls page (ControlsModel, ControlsMenu, the hub's Controls row). Listening is
## driven with synthetic key and pad events. Every test snapshots the remappable actions' InputMap
## events (after ControlsModel.defaults(), the state boot leaves) and puts them back in _done();
## nothing is written to user://settings.cfg (models save nowhere or to TEST_CFG, removed after).

const TEST_CFG := "user://test_controls_menu.cfg"

var s: UiSettings
var made: Array[Node] = []
var _snapshot: Dictionary = {}


func before_each() -> void:
	s = UiSettings.new()
	UiSettings.set_shared(s)
	made.clear()
	ControlsModel.defaults()
	_snapshot.clear()
	for action in ControlsModel.action_ids(ControlsModel.load_data()):
		var events: Array[InputEvent] = []
		for ev in InputMap.action_get_events(action):
			events.append(ev.duplicate() as InputEvent)
		_snapshot[action] = events
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_CFG))


## Frees what a test made, restores InputMap and the shared settings (the runner has no after_each).
func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()
	for action: StringName in _snapshot:
		InputMap.action_erase_events(action)
		for ev: InputEvent in _snapshot[action]:
			InputMap.action_add_event(action, ev)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_CFG))
	UiSettings.set_shared(null)


# --- the model -----------------------------------------------------------------------------


func test_the_rows_are_the_column_the_actions_and_reset() -> void:
	var m := ControlsModel.new("")
	var ids := m.row_ids()
	assert_eq(ids[0], ControlsModel.ROW_DEVICE)
	assert_eq(ids[ids.size() - 1], ControlsModel.ROW_RESET)
	assert_eq(ids.slice(1, ids.size() - 1), ControlsModel.action_ids(m.data))
	for a in [&"ui_up", &"ui_accept", &"ui_cancel", &"field_interact", &"field_move_left", &"field_walk"]:
		assert_true(ids.has(a), "%s is remappable" % a)
	assert_false(ids.has(&"debug_sandbox"), "debug actions are not")
	assert_eq(m.title_key(), "SET_MENU_CONTROLS")
	assert_eq(m.label(&"ui_accept"), tr("CTRL_ACT_UI_ACCEPT"))
	assert_eq(m.value_text(ControlsModel.ROW_DEVICE), tr("CTRL_DEVICE_KEYBOARD"))
	assert_eq(m.key_name(&"ui_accept"), "Enter")
	assert_eq(m.pad_name(&"ui_accept"), tr("CTRL_PAD_A"), "Confirm gets pad A (pad_defaults)")
	assert_eq(m.pad_name(&"ui_cancel"), tr("CTRL_PAD_B"))
	assert_eq(m.pad_name(&"ui_up"), tr("CTRL_PAD_DPAD_UP"))
	assert_eq(m.pad_name(&"field_move_left"), tr("CTRL_PAD_LSTICK_LEFT"), "an axis-only action shows its stick")
	assert_eq(m.value_text(&"ui_accept"), _cells("[ Enter ]", tr("CTRL_PAD_A")))
	assert_true(m.cycle(1), "Left / Right switch the column")
	assert_eq(m.device, ControlsModel.KIND_PAD)
	assert_eq(m.value_text(&"ui_accept"), _cells("Enter", "[ %s ]" % tr("CTRL_PAD_A")))
	assert_eq(m.help_key(), "CTRL_HELP_DEVICE")
	m.set_cursor(ids.find(&"ui_up"))
	assert_eq(m.help_key(), "CTRL_HELP_ACTION_PAD")
	_done()


func test_a_key_binds_and_applies_to_the_input_map() -> void:
	var m := ControlsModel.new("")
	assert_true(m.start_listen(&"ui_accept", ControlsModel.KIND_KEYS))
	assert_true(m.is_listening())
	assert_eq(m.help_key(), "CTRL_HELP_LISTEN_KEYS")
	assert_eq(m.feed(_key(KEY_K, false)), ControlsModel.Feed.IGNORED, "a release is not a press")
	assert_eq(m.feed(_pad(JOY_BUTTON_X)), ControlsModel.Feed.IGNORED, "a pad button on the keyboard column")
	assert_eq(m.feed(_key(KEY_K)), ControlsModel.Feed.BOUND)
	assert_false(m.is_listening())
	assert_eq(m.key_name(&"ui_accept"), "K")
	assert_true(InputMap.event_is_action(_key(KEY_K), &"ui_accept"), "InputMap has the new key")
	assert_false(InputMap.event_is_action(_key(KEY_ENTER), &"ui_accept"), "the old keys are gone")
	assert_true(InputMap.event_is_action(_pad(JOY_BUTTON_A), &"ui_accept"), "the pad binding stays")
	_done()


func test_a_key_in_use_is_swapped_never_duplicated() -> void:
	var m := ControlsModel.new("")
	m.start_listen(&"ui_accept", ControlsModel.KIND_KEYS)
	assert_eq(m.feed(_key(KEY_UP)), ControlsModel.Feed.BOUND)
	assert_eq(m.key_name(&"ui_accept"), "Up")
	assert_eq(m.key_name(&"ui_up"), "Enter", "Menu up takes Confirm's old key")
	assert_true(m.help_text().contains(tr("CTRL_ACT_UI_UP")), "the help line names the swap")
	assert_true(InputMap.event_is_action(_key(KEY_UP), &"ui_accept"))
	assert_false(InputMap.event_is_action(_key(KEY_UP), &"ui_up"))
	assert_true(InputMap.event_is_action(_key(KEY_ENTER), &"ui_up"))
	assert_true(InputMap.event_is_action(_key(KEY_UP), &"field_move_forward"), "another context keeps its key")
	assert_true(ControlsModel.check(m.bindings, m.data))
	_done()


func test_a_pad_button_in_use_is_swapped() -> void:
	var m := ControlsModel.new("")
	m.start_listen(&"ui_up", ControlsModel.KIND_PAD)
	assert_eq(m.feed(_key(KEY_K)), ControlsModel.Feed.IGNORED, "a key on the pad column")
	assert_eq(m.feed(_pad(JOY_BUTTON_A)), ControlsModel.Feed.BOUND)
	assert_eq(m.pad_name(&"ui_up"), tr("CTRL_PAD_A"))
	assert_eq(m.pad_name(&"ui_accept"), tr("CTRL_PAD_DPAD_UP"))
	assert_true(InputMap.event_is_action(_pad(JOY_BUTTON_A), &"ui_up"))
	assert_true(InputMap.event_is_action(_pad(JOY_BUTTON_DPAD_UP), &"ui_accept"))
	assert_true(InputMap.event_is_action(_motion(JOY_AXIS_LEFT_Y, -1.0), &"ui_up"), "the stick axis is kept")
	_done()


func test_escape_and_pad_b_always_back_out_of_listening() -> void:
	var m := ControlsModel.new("")
	var before := m.bindings.duplicate(true)
	m.start_listen(&"ui_cancel", ControlsModel.KIND_KEYS)
	var esc := InputEventKey.new()
	esc.keycode = KEY_ESCAPE  # keycode only, as Godot's own ui_cancel event has it
	esc.pressed = true
	assert_eq(m.feed(esc), ControlsModel.Feed.CANCELLED)
	assert_false(m.is_listening())
	m.start_listen(&"ui_accept", ControlsModel.KIND_KEYS)
	assert_eq(m.feed(_pad(JOY_BUTTON_B)), ControlsModel.Feed.CANCELLED, "pad B backs out of the keyboard column")
	m.start_listen(&"ui_accept", ControlsModel.KIND_PAD)
	assert_eq(m.feed(_key(KEY_ESCAPE)), ControlsModel.Feed.CANCELLED, "Escape backs out of the pad column")
	m.start_listen(&"ui_accept", ControlsModel.KIND_PAD)
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	assert_eq(m.feed(click), ControlsModel.Feed.CANCELLED, "so does a click")
	# Rebinding ui_cancel away does not change the hard-wired escape.
	m.start_listen(&"ui_cancel", ControlsModel.KIND_KEYS)
	assert_eq(m.feed(_key(KEY_BACKSPACE)), ControlsModel.Feed.BOUND)
	assert_eq(m.key_name(&"ui_cancel"), "Backspace")
	m.start_listen(&"ui_up", ControlsModel.KIND_KEYS)
	assert_eq(m.feed(_key(KEY_ESCAPE)), ControlsModel.Feed.CANCELLED, "Escape still cancels")
	assert_eq(m.key_name(&"ui_up"), "Up")
	m.reset_to_defaults()
	assert_eq(m.bindings, before)
	_done()


func test_cancel_can_never_be_left_unbound() -> void:
	var m := ControlsModel.new("")
	var before := m.bindings.duplicate(true)
	# Interact on pad B would hand ui_cancel pad A, which Confirm holds in the menus: rejected.
	assert_false(m.bind(&"field_interact", ControlsModel.KIND_PAD, JOY_BUTTON_B))
	# Move left has no pad button to give back: ui_cancel would have no pad input: rejected.
	assert_false(m.bind(&"field_move_left", ControlsModel.KIND_PAD, JOY_BUTTON_B))
	assert_eq(m.bindings, before, "nothing changed")
	assert_true(InputMap.event_is_action(_pad(JOY_BUTTON_B), &"ui_cancel"))
	var empty := m.bindings.duplicate(true)
	(empty[&"ui_cancel"] as Dictionary)[ControlsModel.KIND_KEYS] = []
	assert_false(ControlsModel.check(empty, m.data), "no key: not allowed")
	empty = m.bindings.duplicate(true)
	(empty[&"ui_cancel"] as Dictionary)[ControlsModel.KIND_PAD] = []
	assert_false(ControlsModel.check(empty, m.data), "no pad button: not allowed")
	_done()


func test_a_reserved_key_is_rejected_and_listening_goes_on() -> void:
	var m := ControlsModel.new("")
	m.start_listen(&"ui_up", ControlsModel.KIND_KEYS)
	assert_eq(m.feed(_key(KEY_F5)), ControlsModel.Feed.REJECTED)
	assert_true(m.is_listening())
	assert_eq(m.help_key(), "CTRL_HELP_REJECTED")
	assert_eq(m.feed(_key(KEY_PAGEUP)), ControlsModel.Feed.REJECTED, "the bestiary's page key is fixed")
	assert_eq(m.feed(_key(KEY_I)), ControlsModel.Feed.BOUND)
	assert_eq(m.key_name(&"ui_up"), "I")
	_done()


func test_reset_restores_every_default() -> void:
	var m := ControlsModel.new("")
	var before := m.bindings.duplicate(true)
	m.bind(&"ui_accept", ControlsModel.KIND_KEYS, KEY_K)
	m.bind(&"field_walk", ControlsModel.KIND_PAD, JOY_BUTTON_Y)
	assert_ne(m.bindings, before)
	m.set_cursor(m.row_ids().find(ControlsModel.ROW_RESET))
	assert_eq(m.help_key(), "CTRL_HELP_RESET")
	assert_true(m.activate(), "Confirm on the reset row resets")
	assert_eq(m.bindings, before)
	assert_eq(m.help_text(), tr("CTRL_HELP_WAS_RESET"))
	for action: StringName in ControlsModel.defaults():
		assert_eq(_texts(InputMap.action_get_events(action)), _texts(ControlsModel.defaults()[action]), str(action))
	_done()


func test_bindings_save_and_load_back() -> void:
	var other := ConfigFile.new()
	other.set_value("accessibility", "text_scale", 1.3)
	other.save(TEST_CFG)
	var m := ControlsModel.new(TEST_CFG)
	m.bind(&"ui_accept", ControlsModel.KIND_KEYS, KEY_K)
	m.bind(&"field_interact", ControlsModel.KIND_PAD, JOY_BUTTON_X)
	var cfg := ConfigFile.new()
	assert_eq(cfg.load(TEST_CFG), OK)
	assert_true(cfg.has_section("controls"))
	assert_eq(cfg.get_value("accessibility", "text_scale"), 1.3, "other sections are kept")
	assert_eq(ControlsModel.read_saved(TEST_CFG, m.data), m.bindings, "the round trip is exact")
	ControlsModel.restore_defaults()
	assert_false(InputMap.event_is_action(_key(KEY_K), &"ui_accept"))
	assert_true(ControlsModel.apply_saved(TEST_CFG), "boot applies the saved bindings")
	assert_true(InputMap.event_is_action(_key(KEY_K), &"ui_accept"))
	assert_true(InputMap.event_is_action(_pad(JOY_BUTTON_X), &"field_interact"))
	var fresh := ControlsModel.new("")
	assert_eq(fresh.key_name(&"ui_accept"), "K", "a new page shows what InputMap holds")
	m.reset_to_defaults()
	cfg = ConfigFile.new()
	cfg.load(TEST_CFG)
	assert_false(cfg.has_section("controls"), "at the defaults the section is removed")
	assert_true(cfg.has_section("accessibility"))
	_done()


func test_a_broken_saved_file_keeps_the_defaults() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("controls", "ui_accept", {"keys": [KEY_UP], "pad": [JOY_BUTTON_A]})  # Up is Menu up's
	cfg.save(TEST_CFG)
	var d := ControlsModel.load_data()
	assert_eq(ControlsModel.read_saved(TEST_CFG, d), {})
	assert_false(ControlsModel.apply_saved(TEST_CFG))
	assert_true(InputMap.event_is_action(_key(KEY_ENTER), &"ui_accept"))
	assert_false(ControlsModel.apply_saved("user://no_such_controls.cfg"), "no file: nothing to apply")
	_done()


# --- the view ------------------------------------------------------------------------------


func test_the_page_listens_and_swallows_input_while_it_does() -> void:
	var page := ControlsMenu.new("")
	page.ui_settings = s
	_add(page)
	var m := page.model
	assert_true(page.handle_input(_ev(&"ui_right")), "Right switches the column")
	assert_eq(page.value_shown(ControlsModel.ROW_DEVICE), tr("CTRL_DEVICE_PAD"))
	assert_true(page.handle_input(_ev(&"ui_left")))
	for i in m.row_ids().find(&"ui_accept"):
		page.handle_input(_ev(&"ui_down"))
	assert_eq(m.current(), &"ui_accept")
	assert_true(page.handle_input(_ev(&"ui_accept")), "Confirm listens")
	assert_true(page.is_busy())
	assert_eq(page.help_text(), tr("CTRL_HELP_LISTEN_KEYS"))
	assert_eq(page.value_shown(&"ui_accept"), _cells("[ %s ]" % tr("CTRL_CELL_WAITING"), tr("CTRL_PAD_A")))
	assert_true(page.handle_input(_ev(&"ui_cancel")), "a ui_cancel action is swallowed")
	assert_true(page.handle_input(_ev(&"ui_down")), "so is navigation")
	assert_true(page.is_open(), "the page did not close")
	assert_eq(m.current(), &"ui_accept", "the cursor did not move")
	page.close()
	assert_true(page.is_open(), "it cannot close while listening")
	assert_true(page.handle_input(_key(KEY_K)))
	assert_false(page.is_busy())
	assert_eq(page.value_shown(&"ui_accept"), _cells("[ K ]", tr("CTRL_PAD_A")))
	page._on_row_clicked(m.cursor)
	assert_true(page.is_busy(), "a click on the cursor row listens")
	page._on_row_clicked(0)
	assert_false(page.is_busy(), "a click while listening backs out")
	assert_true(page.handle_input(_ev(&"ui_cancel")))
	assert_false(page.is_open(), "Cancel closes when not listening")
	_done()


func test_the_hub_has_a_controls_row_that_opens_the_page() -> void:
	var hub := SettingsMenu.new()
	hub.ui_settings = s
	hub.save_path = ""
	_add(hub)
	var at := hub.row_ids().find(SettingsMenu.ROW_CONTROLS)
	assert_eq(hub.row_labels()[at], tr("SET_MENU_CONTROLS"))
	for i in at:
		hub.handle_input(_ev(&"ui_down"))
	assert_eq(hub.current(), SettingsMenu.ROW_CONTROLS)
	assert_eq(hub.help_text(), tr("SET_MENU_HELP_CONTROLS"))
	assert_true(hub.handle_input(_ev(&"ui_accept")))
	assert_true(hub.page is ControlsMenu)
	var page := hub.page as ControlsMenu
	assert_eq(page.model.config_path, "", "the hub's save path reaches the page")
	assert_true(hub.handle_input(_ev(&"ui_cancel")))
	assert_false(hub.is_page_open())
	assert_eq(hub.current(), SettingsMenu.ROW_CONTROLS)
	hub.close()
	_done()


# --- helpers -------------------------------------------------------------------------------


func _cells(key: String, pad: String) -> String:
	return tr("CTRL_VALUE_FMT").format({"key": key, "pad": pad})


func _texts(events: Array) -> PackedStringArray:
	var out: PackedStringArray = []
	for ev: InputEvent in events:
		out.append(ev.as_text())
	return out


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _key(code: Key, pressed: bool = true) -> InputEventKey:
	var k := InputEventKey.new()  # as a real key press: both codes (US layout)
	k.keycode = code
	k.physical_keycode = code
	k.pressed = pressed
	return k


func _pad(button: JoyButton) -> InputEventJoypadButton:
	var b := InputEventJoypadButton.new()
	b.button_index = button
	b.pressed = true
	return b


func _motion(axis: JoyAxis, value: float) -> InputEventJoypadMotion:
	var m := InputEventJoypadMotion.new()
	m.axis = axis
	m.axis_value = value
	return m
