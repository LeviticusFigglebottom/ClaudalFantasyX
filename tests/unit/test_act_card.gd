extends TestCase
## M3-C09-05: the act card on black (ActCard; act1_ch09.md B11 "Act II: The Truth"), its caption
## shape (the Prologue's "One month earlier."), and its act_card event hook (M3-C09-09 declares it).

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()
	UiSettings.set_shared(UiSettings.new())


func test_act_two_is_loc_keyed_on_black() -> void:
	var d := ActCard.load_data()
	var card := _card()
	assert_false(card.visible, "nothing before it is shown")
	assert_true(card.show_act(2))
	assert_eq(card.label_text(), tr("ACT_CARD_2_LABEL"))
	assert_eq(card.title_text(), tr("ACT_CARD_2_TITLE"))
	assert_eq("%s: %s" % [card.label_text(), card.title_text()], "Act II: The Truth", "the sheet's words, in English")
	assert_true(card.is_black())
	assert_eq(card.backing().color, Color(str(d["back_color"])), "on black")
	assert_eq(card.backing().color.a, 1.0, "the black is whole from the first frame")
	card.advance(float(d["in_sec"]) + 0.01)
	assert_eq(card.phase, ActCard.Phase.HOLD)
	assert_between(card.words_alpha(), 0.999, 1.001)
	var done := [false]
	card.finished.connect(func() -> void: done[0] = true)
	card.advance(float(d["hold_sec"]) + 0.01)
	card.advance(float(d["out_sec"]) + 0.01)
	assert_true(done[0], "finished once the words are out")
	assert_false(card.is_showing())
	assert_true(card.is_black() and card.visible, "the black stays for the next scene to fade in from")
	card.hide_card()
	assert_false(card.visible)
	_done()


## Act II's end (act_outline Ch16, "Act break"; M3-UI-210): the same card names Act III.
func test_act_three_closes_act_two() -> void:
	var card := _card()
	assert_true(card.show_act(3))
	assert_eq("%s: %s" % [card.label_text(), card.title_text()], "Act III: The Unbinding", "act_outline's words")
	assert_true(card.is_black())
	_done()


func test_an_unknown_act_shows_nothing() -> void:
	var card := _card()
	assert_false(card.show_act(99))
	assert_false(card.visible)
	_done()


func test_a_caption_is_one_line() -> void:
	var card := _card()
	card.show_caption("DLG_CH01_DROP_001")
	assert_eq(card.title_text(), tr("DLG_CH01_DROP_001"), "'One month earlier.'")
	assert_eq(card.label_text(), "")
	assert_true(card.is_black())
	_done()


func test_reduced_motion_does_not_rise() -> void:
	var card := _card()
	card.show_act(2)
	card.advance(0.01)
	var words := card.get_node(^"Words") as Control
	assert_true(words.position.y > 0.0, "it rises into place")
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	card.advance(0.01)
	assert_eq(words.position.y, 0.0, "reduced motion: no rise")
	_done()


func test_the_act_card_event_shows_it() -> void:
	var seq := CutsceneSequencer.new()
	_keep(seq)
	var card := _card()
	card.listen(seq)
	seq.event_requested.emit(&"something_else", [2])
	assert_false(card.is_black())
	seq.event_requested.emit(ActCard.EVENT, [2])
	assert_true(card.is_showing())
	assert_eq(card.act, 2)
	_done()


func test_open_in_puts_it_on_its_own_layer() -> void:
	var host := Node.new()
	_keep(host)
	var card := ActCard.open_in(host)
	var layer := card.get_parent() as CanvasLayer
	assert_true(layer != null)
	assert_eq(layer.layer, int(ActCard.load_data()["canvas_layer"]))
	_done()


func _card() -> ActCard:
	var c := ActCard.new()
	_keep(c)
	return c


func _keep(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	n.set_process(false)
	made.append(n)


func _done() -> void:
	UiSettings.set_shared(null)
