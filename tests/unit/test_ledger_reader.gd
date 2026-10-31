extends TestCase
## The ledger page (LedgerReader, LedgerReaderModel; M5-A3P-1706, act3_ch17 B05): the scene's ledger entries are
## written on the open page, other lines are not; a held turn_page gate turns the page when it ends (another gate
## doesn't); turns past the last entry land on blank pages; and the page goes when the scene ends.


func test_the_model_turns_onto_blank_pages() -> void:
	var m := LedgerReaderModel.new()
	assert_eq(m.blank_turns(), 0, "nothing written yet")
	m.write("A")
	m.write("B")
	assert_eq(m.current(), PackedStringArray(["A", "B"]))
	m.turn()
	assert_true(m.current().is_empty(), "the next page comes up blank")
	m.write("C")
	m.turn()
	m.turn()
	m.turn()
	assert_eq(m.turned(), 4)
	assert_eq(m.blank_turns(), 3, "three blank pages after the last entry")


func test_entries_are_written_and_turned_by_the_held_gate() -> void:
	UiSettings.set_shared(UiSettings.new())
	var host := Node.new()
	ParityHost.scene_root().add_child(host)
	var seq := CutsceneSequencer.new()
	var reader := LedgerReader.mount(host, seq)
	var turns: Array[int] = []
	reader.page_turned.connect(func(n: int) -> void: turns.append(n))
	seq.line_shown.emit(_step(&"ch17_ledger_page_001", &"KITE_LOG_FOUND_RHEN"))
	seq.line_shown.emit(_step(&"ch17_ledger_001", &"KITE_LOG_FOUND_ASHA"))
	assert_eq(reader.shown_text(), PackedStringArray([tr("KITE_LOG_FOUND_RHEN")]), "only the ledger's own entries")
	seq.event_requested.emit(CutsceneHoldGate.EVENT_BEGIN, ["raise_staff"])
	seq.event_requested.emit(CutsceneHoldGate.EVENT_END, [])
	assert_true(turns.is_empty(), "another gate turns nothing")
	seq.event_requested.emit(CutsceneHoldGate.EVENT_BEGIN, ["turn_page"])
	assert_true(turns.is_empty(), "the page turns at the gate's end, not its start")
	seq.event_requested.emit(CutsceneHoldGate.EVENT_END, [])
	assert_eq(turns, [1] as Array[int])
	assert_true(reader.shown_text().is_empty(), "the next page is blank")
	seq.line_shown.emit(_step(&"ch17_ledger_page_002", &"KITE_LOG_FOUND_TOMA"))
	assert_eq(reader.shown_text(), PackedStringArray([tr("KITE_LOG_FOUND_TOMA")]))
	for i in 3:
		seq.event_requested.emit(CutsceneHoldGate.EVENT_BEGIN, ["turn_page"])
		seq.event_requested.emit(CutsceneHoldGate.EVENT_END, [])
	assert_eq(reader.model.blank_turns(), 3, "the blank-page end")
	assert_true(reader.shown_text().is_empty())
	var layer := reader.get_parent()
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)  # the fade is instant, so it goes at once
	seq.finished.emit(&"ch17_the_ledger")
	assert_true(layer.is_queued_for_deletion(), "the page goes when the scene ends")
	seq.free()
	host.remove_child(layer)
	layer.free()
	host.get_parent().remove_child(host)
	host.free()
	UiSettings.set_shared(null)


## The shipped scene: its ledger entries carry the prefix, and its turn gates the prompt, the data names.
func test_the_shipped_scene_matches_the_data() -> void:
	var data := LedgerReader.load_data()
	var src := FileAccess.get_file_as_string("res://game/data/dialogue/ch17/ch17_the_ledger.dlg")
	assert_true(src.contains("#line:" + str(data["line_prefix"])), "the entries carry the prefix")
	assert_true(src.contains("<<event hold_input %s>>" % data["turn_prompt"]), "the turns use the prompt")
	assert_ne(tr(str(data["title_key"])), str(data["title_key"]), "the title is translated")


static func _step(line_id: StringName, key: StringName) -> DialogueStep:
	var s := DialogueStep.new()
	s.kind = DialogueStep.Kind.LINE
	s.line_id = line_id
	s.text_key = key
	return s
