extends TestCase
## M4-A2P-080: the document reader (DocumentReaderModel, DocumentReader) over the fixture records: a hand is found
## when each of its panes' marks is on its line, its lines stay gold and the marks clear; the last sets the record's
## flag; the line under the panes counts what is left; and the reader is walked with the keyboard, the controller
## and the mouse (InputDriver: real events), the wheel scrolling a long pane. The runner runs no frames.

const FIXTURE := "res://game/levels/_tests/document_reader/reader_fixture.json"

var flags: Array[StringName] = []
var reader: DocumentReader


func before_each() -> void:
	InputDriver.clear_screen()
	UiSettings.set_shared(UiSettings.new())
	flags = []
	reader = null


func test_a_hand_is_found_when_each_of_its_panes_marks_its_line() -> void:
	var m := _model(&"fixture_three")
	assert_eq(m.pane_count(), 3)
	assert_eq(m.hands_text(), tr("READER_HANDS_LEFT_FMT").format({"n": 2, "count": 2}))
	assert_eq(m.toggle(0, 0), &"", "one mark is not a hand")
	assert_eq(m.marks[0], 0)
	assert_eq(m.toggle(1, 2), &"", "a wrong line: nothing")
	assert_eq(m.toggle(1, 3), &"abrel", "the mark moves within its pane, and the hand is found")
	assert_eq(m.marks, [DocumentReaderModel.NO_MARK, DocumentReaderModel.NO_MARK, DocumentReaderModel.NO_MARK])
	assert_eq(m.found_hand_at(0, 0), &"abrel", "its lines stay found")
	assert_eq(m.toggle(0, 0), &"", "a found line takes no mark")
	assert_eq(m.marks[0], DocumentReaderModel.NO_MARK)
	assert_eq(m.hands_text(), tr("READER_HANDS_LEFT_FMT").format({"n": 1, "count": 2}))
	assert_true(flags.is_empty(), "no flag until the last")
	m.toggle(2, 2)
	m.toggle(2, 2)
	assert_eq(m.marks[2], DocumentReaderModel.NO_MARK, "marking the marked line clears it")
	m.toggle(0, 4)
	m.toggle(1, 1)
	assert_eq(m.toggle(2, 2), &"hooked")
	assert_true(m.all_found())
	assert_eq(m.hands_text(), tr("READER_ALL_FOUND"))
	assert_eq(flags, [&"fixture_done"] as Array[StringName], "the last hand sets the record's flag")
	var again := _model(&"fixture_three")
	again.restore(m.state())
	assert_true(again.all_found(), "the marks and the found hands are kept for the next opening")


func test_a_found_record_alone_has_no_hands_to_find() -> void:
	var m := _model(&"fixture_one")
	assert_eq(m.pane_count(), 1)
	assert_false(m.has_hands())
	assert_eq(m.hands_text(), "")
	assert_eq(m.pane_label(0), "", "no '1 of 1'")
	assert_eq(m.toggle(0, 1), &"")
	assert_true(flags.is_empty())


func test_the_shipped_records_are_well_formed() -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DocumentReaderModel.DATA_PATH))
	assert_true(parsed is Dictionary and (parsed as Dictionary).get("records") is Array, "records.json reads")
	for r: Dictionary in (parsed as Dictionary).get("records", []):
		var m := DocumentReaderModel.new(r, func(_f: StringName) -> void: pass)
		assert_true(m.pane_count() >= 1 and m.pane_count() <= 3, "%s: one to three panes" % m.id())
		for h: Dictionary in r.get("hands", []):
			for c: Array in h.get("lines", []):
				assert_true(int(c[1]) < m.lines(int(c[0])).size(), "%s: a hand's line exists" % m.id())


func test_the_reader_shows_marks_found_lines_and_the_count() -> void:
	_open(&"fixture_three")
	assert_eq(reader.title_text(), "Lamp-ledgers of the east stair")
	reader.set_cursor(0, 0)
	reader.mark()
	assert_true(reader.line_label(0, 0).get_node(^"Mark").visible, "the mark's bar")
	reader.set_cursor(1, 3)
	reader.mark()
	assert_false(reader.line_label(0, 0).get_node(^"Mark").visible, "found: the marks clear")
	var gold := reader.get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	assert_eq(reader.line_label(1, 3).get_theme_color(&"font_color"), gold, "and the hand's lines turn gold")
	assert_eq(reader.rule_progress(), [0.0] as Array[float], "its rule draws on")
	assert_eq(reader.hands_text(), tr("READER_HANDS_LEFT_FMT").format({"n": 1, "count": 2}))
	_close()


func test_under_reduced_motion_the_rule_is_there_at_once() -> void:
	var s := UiSettings.new()
	s.set_value(UiSettings.REDUCED_MOTION, true)
	UiSettings.set_shared(s)
	_open(&"fixture_three")
	reader.set_cursor(0, 0)
	reader.mark()
	reader.set_cursor(1, 3)
	reader.mark()
	assert_eq(reader.rule_progress(), [1.0] as Array[float])
	_close()


func test_each_device_moves_marks_and_closes() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		_open(&"fixture_three")
		var found: Array[StringName] = []
		reader.hand_found.connect(func(h: StringName) -> void: found.append(h))
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(reader.line_label(0, 0))
			assert_eq(reader.model.marks[0], 0, "%s: a click marks the line" % who)
			InputDriver.hover(reader.line_label(1, 2))
			assert_eq([reader.pane, reader.cursors[1]], [1, 2], "%s: hovering moves the cursor" % who)
			InputDriver.click(reader.line_label(1, 3))
		else:
			d.press(&"ui_accept")
			assert_eq(reader.model.marks[0], 0, "%s: Confirm marks the line" % who)
			d.press(&"ui_right")
			assert_eq(reader.pane, 1, "%s: Right moves to the next pane" % who)
			for i in 3:
				d.press(&"ui_down")
			assert_eq(reader.cursors[1], 3, "%s: Down moves the line" % who)
			d.press(&"ui_accept")
		assert_eq(found, [&"abrel"] as Array[StringName], "%s: the hand is found" % who)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.right_click(reader.line_label(1, 0))
		else:
			d.press(&"ui_cancel")
		assert_false(reader.is_open(), "%s: Cancel closes" % who)
		_close()


func test_a_long_pane_scrolls_with_the_wheel_page_keys_and_the_cursor() -> void:
	var lines: Array = []
	for i in 40:
		lines.append("A ledger line of some length, so that forty of them run well past the pane's foot. %d" % i)
	var row := {"id": "long", "title_key": "Long", "panes": [{"title_key": "Long", "lines": lines}], "hands": []}
	_open_row(row)
	assert_true(reader.max_scroll(0) > 0.0, "the pane is longer than its view")
	InputDriver.wheel(reader.pane_area(0), 2)
	assert_true(reader.scroll_of(0) > 0.0, "the wheel scrolls it")
	var before := reader.scroll_of(0)
	reader.handle_input(_ev(&"ui_page_up"))
	assert_true(reader.scroll_of(0) < before, "Page Up scrolls back")
	reader.set_cursor(0, 39)
	assert_eq(reader.scroll_of(0), reader.max_scroll(0), "the cursor's line is kept in view")
	_close()


func _model(id: StringName) -> DocumentReaderModel:
	var row := DocumentReaderModel.row_of(id, FIXTURE).duplicate(true)
	if id == &"fixture_three":
		row["flag"] = "fixture_done"
	return DocumentReaderModel.new(row, func(f: StringName) -> void: flags.append(f))


func _open(id: StringName) -> void:
	_open_row(_model(id).record)


func _open_row(row: Dictionary) -> void:
	reader = DocumentReader.open_in(_root(), DocumentReaderModel.new(row, func(f: StringName) -> void: flags.append(f)))
	reader.motion().finish()


func _close() -> void:
	if reader == null:
		return
	if reader.motion() != null:
		reader.motion().finish()
	var layer := reader.get_parent()
	if is_instance_valid(layer):
		layer.get_parent().remove_child(layer)
		layer.free()
	(Engine.get_main_loop() as SceneTree).paused = false
	reader = null


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
