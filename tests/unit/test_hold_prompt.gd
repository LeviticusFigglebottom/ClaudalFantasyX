extends TestCase
## M3-C09-05: the held-input prompt (HoldPrompt) and the CutsceneHoldGate that shows it. One
## prompt, the held action's binding for the device used last, no meter, no count, no fail:
## letting go only lets it breathe.

const RAISE_KEY := "FIELD_PROMPT_CH09_RAISE_STAFF"
const ACTION := &"field_interact"

var made: Array[Node] = []
var _was_pad := false


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()
	UiSettings.set_shared(UiSettings.new())
	_was_pad = InputNames.using_pad
	InputNames.using_pad = false
	FieldInput.ensure_actions()


func test_it_names_the_key_and_the_verb() -> void:
	var p := _prompt()
	assert_false(p.is_showing(), "nothing before a gate")
	p.show_prompt(RAISE_KEY)
	p.advance(float(HoldPrompt.load_data()["fade_sec"]))
	assert_true(p.is_showing())
	assert_eq(p.verb_text_shown(), tr(RAISE_KEY), "'Hold to raise the staff'")
	assert_eq(p.key_text_shown(), InputNames.first_name(ACTION, false), "the key")
	assert_ne(p.key_text_shown(), "", "the action is bound")
	InputNames.using_pad = true
	p.advance(0.01)
	assert_eq(p.key_text_shown(), InputNames.first_name(ACTION, true), "the pad button once the pad is used")
	_done()


func test_it_has_no_meter_and_letting_go_only_breathes() -> void:
	var d := HoldPrompt.load_data()
	var p := _prompt()
	p.show_prompt(RAISE_KEY)
	p.advance(float(d["fade_sec"]))
	for n in p.find_children("*", "", true, false):
		assert_false(n is Range, "no meter: %s" % n.name)
	assert_eq(p.find_children("*", "Label", true, false).size(), 2, "a key and a verb, no count")
	# Unheld: the plate breathes between breath_low and 1, and never goes.
	var low := 1.0
	for i in 40:
		p.advance(float(d["breath_sec"]) / 40.0)
		low = minf(low, p.plate_alpha())
		assert_true(p.is_showing(), "letting go never hides it")
	assert_between(low, float(d["breath_low"]) - 0.01, float(d["breath_low"]) + 0.05, "it breathes")
	p.set_held(true)
	p.advance(0.5)
	assert_eq(p.plate_alpha(), 1.0, "held: steady")
	p.set_held(false)
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	p.advance(float(d["breath_sec"]) * 0.5)
	assert_eq(p.plate_alpha(), 1.0, "reduced motion: no breath")
	p.hide_prompt()
	p.advance(float(d["fade_sec"]) + 0.01)
	assert_false(p.is_showing(), "hidden when the gate closes")
	_done()


func test_the_gate_shows_it_for_the_whole_gate() -> void:
	var seq := CutsceneSequencer.new()
	_keep(seq)
	var gate := CutsceneHoldGate.new()
	_keep(gate)
	gate.setup(seq, {"action": String(ACTION), "prompts": {"raise_staff": RAISE_KEY}, "layer": 33, "bottom_px": 96.0})
	assert_true(gate.prompt is HoldPrompt, "the gate's prompt is UI's widget")
	assert_eq(gate.prompt.action, ACTION)
	seq.event_requested.emit(CutsceneHoldGate.EVENT_BEGIN, [&"raise_staff"])
	assert_true(gate.gating)
	gate.prompt.advance(float(HoldPrompt.load_data()["fade_sec"]))
	assert_true(gate.prompt.is_showing())
	assert_eq(gate.prompt.verb_text_shown(), tr(RAISE_KEY))
	assert_false(gate.tick(0.1, false), "unheld: the scene waits")
	assert_false(gate.prompt.held)
	assert_true(gate.tick(0.1, true), "held: the scene moves")
	assert_true(gate.prompt.held, "and the key is lit")
	seq.event_requested.emit(CutsceneHoldGate.EVENT_END, [])
	assert_false(gate.gating)
	gate.prompt.advance(float(HoldPrompt.load_data()["fade_sec"]) + 0.01)
	assert_false(gate.prompt.is_showing(), "gone with the gate")
	_done()


func _prompt() -> HoldPrompt:
	var p := HoldPrompt.new()
	p.action = ACTION
	_keep(p)
	return p


func _keep(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	n.set_process(false)
	made.append(n)


func _done() -> void:
	InputNames.using_pad = _was_pad
	UiSettings.set_shared(null)
