extends TestCase
## The Lead's Act I menu pass (controller only): a held pad direction repeats like a held key. UiInput starts a hold on
## a pad press of a repeat action, sends nothing until repeat_delay_sec, then one press-and-release every
## repeat_rate_sec (marked repeat_device), and stops when the pad lets go. A key press never starts one.

const SCRIPT := "res://game/ui/input/ui_input.gd"

var ui: Node
var got: Array[InputEvent] = []


func before_each() -> void:
	ui = (load(SCRIPT) as GDScript).new()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ui)
	got.clear()


func test_a_held_dpad_repeats_after_the_delay_then_at_the_rate() -> void:
	var d: Dictionary = ui.call(&"load_data")
	var delay := float(d["repeat_delay_sec"])
	var rate := float(d["repeat_rate_sec"])
	ui.call(&"note_pad_hold", _dpad(JOY_BUTTON_DPAD_DOWN, true))
	assert_eq(ui.call(&"held_action"), &"ui_down", "a d-pad press of ui_down starts a hold")
	var held := func() -> bool: return true
	assert_eq(ui.call(&"advance_repeat", delay * 0.5, held), 0, "nothing before the delay")
	assert_eq(ui.call(&"advance_repeat", delay * 0.5 + 0.001, held), 1, "the first repeat at the delay")
	assert_eq(ui.call(&"advance_repeat", rate * 2.0, held), 2, "then one per rate")
	ui.call(&"note_pad_hold", _dpad(JOY_BUTTON_DPAD_DOWN, false))
	assert_eq(ui.call(&"held_action"), &"", "letting go ends it")
	assert_eq(ui.call(&"advance_repeat", 5.0, held), 0)
	_done()


func test_a_pad_that_no_longer_holds_stops_and_keys_never_start_one() -> void:
	ui.call(&"note_pad_hold", _dpad(JOY_BUTTON_DPAD_UP, true))
	assert_eq(ui.call(&"advance_repeat", 5.0, func() -> bool: return false), 0, "the pad let go: no repeat")
	assert_eq(ui.call(&"held_action"), &"")
	var key := InputEventKey.new()
	key.keycode = KEY_DOWN
	key.physical_keycode = KEY_DOWN
	key.pressed = true
	ui.call(&"note_pad_hold", key)
	assert_eq(ui.call(&"held_action"), &"", "a key repeats by itself (the OS echo)")
	_done()


func test_a_repeat_is_a_marked_press_then_release() -> void:
	var catcher := _Catcher.new()
	catcher.got = got
	ui.add_child(catcher)
	ui.call(&"send_repeat", ui.get_viewport(), &"ui_down")
	var device := int((ui.call(&"load_data") as Dictionary)["repeat_device"])
	assert_eq(got.size(), 2, "a press and its release")
	if got.size() == 2:
		assert_true(got[0].is_action_pressed(&"ui_down"), "the press counts for ui_down")
		assert_true(got[1].is_action_released(&"ui_down"))
		assert_eq(got[0].device, device)
	_done()


## A held direction (a key's echo or a pad repeat) stops at a list's end; a fresh press wraps round.
func test_a_held_direction_stops_at_the_end_and_a_press_wraps() -> void:
	var page := MenuPage.new()
	page.size = Vector2(540.0, 200.0)
	ParityHost.scene_root().add_child(page)
	var rows: Array[Dictionary] = [{"id": &"a", "label": "A"}, {"id": &"b", "label": "B"}, {"id": &"c", "label": "C"}]
	page.setup(HudLayout.section(&"commands"), &"test", "", rows)
	page.set_cursor(2, false)
	MenuPage.held_probe = func(_delta: int) -> bool: return true
	assert_false(page.move(1), "held: no wrap past the last row")
	assert_eq(page.cursor, 2)
	assert_true(page.move(-1), "held: moving within the list still works")
	page.set_cursor(0, false)
	assert_false(page.move(-1), "held: no wrap past the first row")
	MenuPage.held_probe = func(_delta: int) -> bool: return false
	assert_true(page.move(-1), "a fresh press wraps")
	assert_eq(page.cursor, 2)
	MenuPage.held_probe = Callable()
	page.get_parent().remove_child(page)
	page.free()
	_done()


func _dpad(button: JoyButton, down: bool) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = button
	e.pressed = down
	return e


func _done() -> void:
	ui.get_parent().remove_child(ui)
	ui.free()


class _Catcher:
	extends Node
	var got: Array[InputEvent] = []

	func _input(event: InputEvent) -> void:
		if event is InputEventAction:
			got.append(event)
