extends TestCase
## M2-UI-27: the dialogue reveal lingers at punctuation (text_box.json "pauses"), scaled by the
## reveal speed, and publishes when each character appears (DialogueBox.time_of_char) so lip sync
## follows the pauses. The text speed setting reaches the box through DialogueAssist.

const BOX := "res://game/ui/dialogue/dialogue_box.tscn"

var made: Array[Node] = []


func before_each() -> void:
	UiSettings.set_shared(UiSettings.new())


func test_marks_pause_where_a_sentence_breathes() -> void:
	var s := _settings(40.0)
	assert_between(s.pause_after("Yes, then.", 3), 0.119, 0.121, "a comma before a space")
	assert_between(s.pause_after("Wait. Go", 4), 0.299, 0.301, "a full stop before a space")
	assert_between(s.pause_after("No— not yet", 2), 0.249, 0.251, "an em dash")
	assert_eq(s.pause_after("It cost 3.5 lume", 9), 0.0, "a decimal point does not pause")
	assert_eq(s.pause_after("Wait...", 4), 0.0, "the end of the line never pauses")
	assert_eq(s.pause_after("So... then", 2), 0.0, "inside a run of marks: no pause")
	assert_between(s.pause_after("So... then", 4), 0.299, 0.301, "only the last mark of the run")
	assert_between(s.pause_after('"Go." She', 3), 0.299, 0.301, "a closing quote may sit between")
	var fast := _settings(80.0)
	assert_between(fast.pause_after("Yes, then.", 3), 0.059, 0.061, "twice the speed, half the pause")
	_done()


func test_time_of_char_includes_the_pauses_and_the_reveal_follows_it() -> void:
	var box := _box(40.0)
	box.show_text(&"", &"Yes, then.")
	var step := 1.0 / 40.0
	assert_between(box.time_of_char(0), step - 0.0001, step + 0.0001)
	assert_between(box.time_of_char(3), step * 4 - 0.0001, step * 4 + 0.0001, "the comma itself shows on time")
	var after := box.time_of_char(4)
	assert_between(after, step * 5 + 0.119, step * 5 + 0.121, "the space after it waits for the pause")
	box.advance(box.time_of_char(3) + 0.01)
	assert_eq(box.shown_text(), "Yes,")
	box.advance(0.1)
	assert_eq(box.shown_text(), "Yes,", "still lingering")
	box.advance(0.05)
	assert_eq(box.shown_text(), "Yes, ", "then on")
	assert_between(box.reveal_duration(), box.time_of_char(9) - 0.0001, box.time_of_char(9) + 0.0001)
	box.skip_reveal()
	assert_eq(box.shown_text(), "Yes, then.", "fast-forward skips every pause")
	_done()


func test_instant_text_speed_has_no_timing_and_the_setting_reaches_the_box() -> void:
	var box := _box(40.0)
	UiSettings.shared().set_value(UiSettings.TEXT_SPEED, "instant")
	box.show_text(&"", &"Yes, then.")
	assert_eq(box.time_of_char(3), 0.0, "instant: no timing")
	box.advance(0.0)
	assert_eq(box.shown_text(), "Yes, then.", "and the whole line at once")
	UiSettings.shared().set_value(UiSettings.TEXT_SPEED, "normal")
	assert_between(box.settings.chars_per_sec, 39.9, 40.1, "back to the box's own speed")
	_done()


func _settings(cps: float) -> DialogueTextSettings:
	var s := DialogueTextSettings.load_default()
	s.chars_per_sec = cps
	return s


func _box(cps: float) -> DialogueBox:
	var box := (load(BOX) as PackedScene).instantiate() as DialogueBox
	box.settings = _settings(cps)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	made.append(box)
	return box


func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	UiSettings.set_shared(null)
