extends TestCase
## M2-UI-25: the dialogue assist on the real dialogue_box.tscn: the continue glyph, the session
## backlog and its page, and auto-advance. Time is driven with step(), never the clock.

const SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const LINE_KEY := &"DLG_CH02_BEACH_004"
const LINE_TEXT := "That's a very big spear for a very small conversation."
const SEQUENCER_CONFIG := "res://game/data/cutscene/sequencer.json"

var box: DialogueBox
var assist: DialogueAssist
var advances: Array[int] = [0]
var made: Array[Node] = []


func before_each() -> void:
	_tree().paused = false
	UiSettings.set_shared(UiSettings.new())
	box = (load(SCENE) as PackedScene).instantiate() as DialogueBox
	_host(box)
	_settle(box)


func _tree() -> SceneTree:
	return Engine.get_main_loop() as SceneTree


## The root is busy while the runner's _ready() runs the tests; host under the runner instead.
func _host(n: Node) -> void:
	var tree := _tree()
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _settle(b: DialogueBox) -> void:
	b.set_process(false)
	b.set_process_unhandled_input(false)
	assist = b.get_node(^"DialogueAssist") as DialogueAssist
	assist.set_process(false)
	assist.set_process_unhandled_input(false)
	assist.backlog = DialogueBacklog.new(int(DialogueAssist.load_data()["max_lines"]))
	assist.pause_backlog = false
	advances[0] = 0
	b.advance_requested.connect(func() -> void: advances[0] += 1)


func _done() -> void:
	if assist != null and assist.backlog_open():
		assist.page.close()
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	_tree().paused = false
	UiSettings.set_shared(UiSettings.new())


func _say(speaker: StringName = &"rhen", key: StringName = LINE_KEY) -> void:
	box.show_text(speaker, key)
	box.skip_reveal()


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func test_the_box_attaches_the_assist_and_the_backlog_action() -> void:
	assert_true(assist != null, "DialogueBox._ready attaches it")
	assert_true(InputMap.has_action(DialogueAssist.ACTION))
	var key := InputEventKey.new()
	key.physical_keycode = KEY_L
	assert_true(InputMap.event_is_action(key, DialogueAssist.ACTION), "keyboard L")
	var pad := InputEventJoypadButton.new()
	pad.button_index = JOY_BUTTON_Y
	assert_true(InputMap.event_is_action(pad, DialogueAssist.ACTION), "pad button 3 (Y)")
	assert_true(ControlsModel.defaults().has(DialogueAssist.ACTION), "remappable on the Controls page")
	_done()


func test_the_glyph_shows_only_while_a_revealed_line_waits() -> void:
	box.visible = true
	box.show_text(&"rhen", LINE_KEY)
	assist.step(0.0)
	assert_false(assist.glyph_control().visible, "hidden while the line reveals")
	box.skip_reveal()
	assist.step(0.0)
	assert_true(assist.glyph_control().visible, "up once the line is fully shown")
	var panel := box.get_node(^"Panel") as Control
	assert_true(panel.get_rect().encloses(assist.glyph_control().get_rect()), "inside the panel, at its bottom right")
	assert_true(assist.glyph_control().get_rect().end.x > panel.get_rect().get_center().x)
	box.advance_requested.emit()
	assist.step(0.0)
	assert_false(assist.glyph_control().visible, "gone once the player moves on")
	_say()
	box.visible = false
	assist.step(0.0)
	assert_false(assist.glyph_control().visible, "never on a hidden box")
	box.visible = true
	box.show_text(&"", &"")
	assist.step(0.0)
	assert_false(assist.is_waiting(), "an empty line never waits")
	assert_false(assist.glyph_control().visible)
	_done()


func test_the_glyph_bobs_from_accumulated_time_and_holds_under_reduced_motion() -> void:
	var g := DialogueAssist.load_data()["glyph"] as Dictionary
	var period := float(g["bob_sec"])
	_say()
	assist.step(0.0)
	var rest := assist.glyph_control().position.y
	assert_eq(assist.glyph_bob(), 0.0, "starts at rest")
	assist.step(period * 0.5)
	assert_true(is_equal_approx(assist.glyph_bob(), float(g["bob_px"])), "lowest at half a period")
	assert_true(is_equal_approx(assist.glyph_control().position.y, rest + float(g["bob_px"])))
	assist.step(period * 0.5)
	assert_true(absf(assist.glyph_bob()) < 0.001, "back at rest after one period")
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	assist.step(period * 0.5)
	assert_eq(assist.glyph_bob(), 0.0, "still under reduced motion")
	assert_true(is_equal_approx(assist.glyph_control().position.y, rest))
	_done()


func test_auto_advance_is_off_by_default() -> void:
	assert_false(UiSettings.shared().dialogue_auto_enabled())
	_say()
	assist.step(1000.0)
	assert_eq(advances[0], 0, "Off: the line waits for Confirm")
	assert_true(assist.is_waiting())
	_done()


func test_auto_advance_holds_by_line_length_then_advances_once() -> void:
	UiSettings.shared().set_value(UiSettings.DIALOGUE_AUTO, true)
	var a := DialogueAssist.load_data()["auto"] as Dictionary
	var need := float(a["base_sec"]) + float(a["per_char_sec"]) * LINE_TEXT.length()
	assert_true(is_equal_approx(assist.hold_for(LINE_TEXT.length()), need))
	assert_true(assist.hold_for(80) > assist.hold_for(10), "a longer line holds longer")
	box.show_text(&"rhen", LINE_KEY)
	assist.step(need * 2.0)
	assert_eq(advances[0], 0, "never while the line still reveals")
	box.skip_reveal()
	assist.step(need - 0.05)
	assert_eq(advances[0], 0, "still reading")
	assist.step(0.1)
	assert_eq(advances[0], 1, "then it moves on by itself")
	assist.step(need * 2.0)
	assert_eq(advances[0], 1, "once")
	box.show_text(&"", &"")
	assist.step(need * 2.0)
	assert_eq(advances[0], 1, "an empty line never auto-advances")
	_done()


func test_auto_advance_waits_while_paused_or_the_backlog_is_open() -> void:
	UiSettings.shared().set_value(UiSettings.DIALOGUE_AUTO, true)
	_say()
	assist.open_backlog()
	assert_true(assist.backlog_open())
	assist.step(1000.0)
	assert_eq(advances[0], 0, "the backlog holds the line")
	assert_false(assist.can_open_backlog(), "one backlog at a time")
	assist.page.close()
	_tree().paused = true
	assist.step(1000.0)
	assert_eq(advances[0], 0, "a pause holds it too")
	_tree().paused = false
	assert_true(is_equal_approx(assist.held_sec(), 0.0), "and the hold did not run meanwhile")
	assist.step(1000.0)
	assert_eq(advances[0], 1)
	_done()


func test_auto_advance_and_the_glyph_wait_for_choices() -> void:
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER_CONFIG))
	var overlay := CutsceneOverlay.new(cfg)
	_host(overlay)
	box = overlay.box
	box.visible = true
	_settle(box)
	UiSettings.shared().set_value(UiSettings.DIALOGUE_AUTO, true)
	_say()
	overlay.choices.visible = true
	assert_true(assist.choices_up())
	assist.step(1000.0)
	assert_eq(advances[0], 0, "choices are always the player's")
	assert_false(assist.glyph_control().visible, "and no glyph under them")
	overlay.choices.visible = false
	assist.step(1000.0)
	assert_eq(advances[0], 1)
	_done()


func test_revealed_lines_go_into_the_capped_backlog() -> void:
	_say()
	box.show_text(&"", &"")  # empty: not kept
	assert_eq(assist.backlog.size(), 1)
	var line: Dictionary = assist.backlog.lines()[0]
	assert_eq(line[DialogueBacklog.KEY_SPEAKER], "Rhen")
	assert_eq(line[DialogueBacklog.KEY_TEXT], LINE_TEXT)
	box.show_text(&"rhen", LINE_KEY)
	box.advance(0.1)
	assert_eq(assist.backlog.size(), 1, "a line half shown is not kept yet")
	var kept := DialogueBacklog.new(3)
	for i in 5:
		kept.record("", "line %d" % i)
	assert_eq(kept.size(), 3, "capped")
	assert_eq(kept.lines()[0][DialogueBacklog.KEY_TEXT], "line 2", "the oldest fall off")
	kept.record("Rhen", "  ")
	assert_eq(kept.size(), 3, "blank text is not kept")
	assert_true(int(DialogueAssist.load_data()["max_lines"]) > 0, "the session cap is data")
	_done()


func test_the_backlog_action_opens_the_page_only_while_the_box_is_up() -> void:
	box.visible = false
	assert_false(assist.can_open_backlog(), "no line on screen")
	box.visible = true
	_say()
	assist.set_process_unhandled_input(true)
	assist._unhandled_input(_ev(DialogueAssist.ACTION))
	assert_true(assist.backlog_open(), "the action opens it")
	assert_eq(assist.page.shown_lines(), [PackedStringArray(["Rhen", LINE_TEXT])] as Array[PackedStringArray])
	assert_true(assist.page.handle_input(_ev(DialogueAssist.ACTION)), "the action again closes it")
	assert_false(assist.backlog_open())
	assist.pause_backlog = true
	assist.open_backlog()
	assert_true(_tree().paused, "the page pauses the tree, so the cutscene holds")
	assert_true(assist.page.handle_input(_ev(&"ui_cancel")), "Cancel closes it")
	assert_false(_tree().paused, "and lifts the pause")
	_done()


func test_the_page_opens_at_the_latest_line_and_scrolls() -> void:
	for i in 12:
		_say(&"rhen" if i % 2 == 0 else &"")
	var page := assist.open_backlog()
	assert_eq(page.shown_lines().size(), 12)
	assert_eq(page.shown_lines()[1][0], "", "narration has no name")
	assert_true(page.max_scroll() > 0.0, "twelve lines overflow the list")
	assert_eq(page.scroll_value(), page.max_scroll(), "opens on the latest line")
	var list_h := float(((page.load_layout()["list"] as Dictionary)["rect"] as Array)[3])
	assert_true(page.max_scroll() >= page.content_height() - list_h, "the latest line is whole at the foot")
	var step := float((page.load_layout()["list"] as Dictionary)["step_px"])
	page.handle_input(_ev(&"ui_up"))
	assert_true(is_equal_approx(page.scroll_value(), page.max_scroll() - step), "Up scrolls a step back")
	page.handle_input(_ev(&"ui_down"))
	page.handle_input(_ev(&"ui_down"))
	assert_eq(page.scroll_value(), page.max_scroll(), "clamped at the foot")
	page.handle_input(_ev(&"ui_page_up"))
	assert_true(page.scroll_value() < page.max_scroll() - step, "a page is more than a step")
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	for i in 100:
		page.handle_input(wheel)
	assert_eq(page.scroll_value(), 0.0, "the wheel scrolls up to the oldest line")
	_done()


func test_an_empty_backlog_says_so() -> void:
	box.visible = true
	var page := assist.open_backlog()
	assert_eq(page.shown_lines(), [PackedStringArray(["", tr("BACKLOG_EMPTY")])] as Array[PackedStringArray])
	assert_eq(page.max_scroll(), 0.0)
	_done()


func test_the_title_screen_forgets_the_session_log() -> void:
	DialogueBacklog.shared().record("Rhen", "x")
	DialogueBacklog.forget()
	assert_true(DialogueBacklog.shared().is_empty())
	_done()
