extends TestCase
## M4-CIN-1302 (act2_ch10.md B09, the farewell-tide): CutsceneHoldGate's release gate. The scene's time stands still
## while the action is held and goes on the first frame it is let go; no timer, no fail.

const RELEASE_KEY := "FIELD_PROMPT_CH09_RAISE_STAFF"
const ACTION := &"field_interact"
const DT := 1.0 / 30.0

var made: Array[Node] = []
var _was_pad := false


func before_each() -> void:
	_free_made()
	UiSettings.set_shared(UiSettings.new())
	_was_pad = InputNames.using_pad
	InputNames.using_pad = false
	FieldInput.ensure_actions()


func test_holding_holds_the_moment_and_letting_go_goes_on() -> void:
	var seq := CutsceneSequencer.new()
	_keep(seq)
	seq.set_process(true)
	var gate := _gate(seq)
	var closed: Array = []
	gate.gate_closed.connect(func() -> void: closed.append(true))
	seq.event_requested.emit(CutsceneHoldGate.EVENT_RELEASE, [&"release"])
	assert_true(gate.gating and gate.releasing, "a release gate is open")
	assert_false(seq.is_processing(), "the scene's own clock stops")
	for i in 90:
		assert_false(gate.tick(DT, true), "held: the moment holds, however long")
	assert_true(gate.gating, "still open after three held seconds")
	assert_eq(gate.held_sec, 0.0, "a release gate never feeds the scene time")
	gate.prompt.advance(float(HoldPrompt.load_data()["fade_sec"]))
	assert_eq(gate.prompt.verb_text_shown(), tr(RELEASE_KEY), "its prompt is the host's row")
	assert_false(gate.tick(DT, false), "let go")
	assert_false(gate.gating or gate.releasing, "letting go closes it")
	assert_eq(closed.size(), 1)
	assert_true(seq.is_processing(), "and the scene's clock runs on")
	_done()


func test_a_hold_gate_then_a_release_gate() -> void:
	var seq := CutsceneSequencer.new()
	_keep(seq)
	var gate := _gate(seq)
	seq.event_requested.emit(CutsceneHoldGate.EVENT_BEGIN, [&"release"])
	assert_false(gate.releasing, "hold_input is the holding kind")
	assert_true(gate.tick(DT, true), "held: the scene moves")
	seq.event_requested.emit(CutsceneHoldGate.EVENT_END, [])
	seq.event_requested.emit(CutsceneHoldGate.EVENT_RELEASE, [&"release"])
	assert_true(gate.releasing)
	assert_false(gate.tick(DT, true), "still held: nothing moves")
	assert_true(gate.gating)
	gate.tick(DT, false)
	assert_false(gate.gating, "released")
	assert_eq(gate.gates, 2, "two gates")
	_done()


func test_the_scene_ending_closes_it() -> void:
	var seq := CutsceneSequencer.new()
	_keep(seq)
	var gate := _gate(seq)
	seq.event_requested.emit(CutsceneHoldGate.EVENT_RELEASE, [&"release"])
	seq.finished.emit(&"")
	assert_false(gate.gating or gate.releasing, "a scene that ends never leaves a gate open")
	_done()


func _gate(seq: CutsceneSequencer) -> CutsceneHoldGate:
	var gate := CutsceneHoldGate.new()
	_keep(gate)
	gate.setup(seq, {"action": String(ACTION), "prompts": {"release": RELEASE_KEY}})
	return gate


func _keep(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	n.set_process(false)
	made.append(n)


func _done() -> void:
	InputNames.using_pad = _was_pad
	UiSettings.set_shared(null)
	_free_made()


func _free_made() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()
