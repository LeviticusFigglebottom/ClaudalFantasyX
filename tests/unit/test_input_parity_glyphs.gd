extends TestCase
## M2-UI-26 (input parity): the names of bindings on screen switch with the last device used, through
## UiInput's tracking: the interaction prompt's keycap, the tip card's text and a dialogue line's
## {action} names show the pad's after a pad press, and the keyboard's after a key press or any
## mouse click (a right click too, which UiInput takes for Cancel before anything else sees it).

const BOX_SCENE := "res://game/ui/dialogue/dialogue_box.tscn"

var made: Array[Node] = []
var flags: Dictionary = {}


func before_each() -> void:
	InputDriver.clear_screen()
	(Engine.get_main_loop() as SceneTree).paused = false
	UiSettings.set_shared(UiSettings.new())
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	flags = {&"ch02_met_asha": true}
	InputNames.using_pad = false


func test_the_tracking_follows_every_device_and_says_so() -> void:
	var changes: Array[bool] = []
	var cb := func(pad: bool) -> void: changes.append(pad)
	UiInput.device_changed.connect(cb)
	_use(InputDriver.Kind.PAD)
	assert_true(InputNames.using_pad, "a pad press")
	_use(InputDriver.Kind.KEYS)
	assert_false(InputNames.using_pad, "a key press")
	_use(InputDriver.Kind.PAD)
	InputDriver.click_at(Vector2.ONE)
	assert_false(InputNames.using_pad, "a left click")
	_use(InputDriver.Kind.PAD)
	InputDriver.click_at(Vector2.ONE, MOUSE_BUTTON_RIGHT)
	assert_false(InputNames.using_pad, "a right click (UiInput's Cancel)")
	assert_eq(changes, [true, false, true, false, true, false] as Array[bool], "each change is announced once")
	UiInput.device_changed.disconnect(cb)
	_done()


func test_the_interaction_prompt_keycap_follows_the_device() -> void:
	var it := Interactable.new()
	it.prompt_key = "FIELD_PROMPT_LISTEN"
	_add(it)
	var prompt := InteractPrompt.new()
	prompt.pick = func() -> Interactable: return it
	_add(prompt)
	var key := InputNames.first_name(FieldInput.INTERACT, false)
	var pad := InputNames.first_name(FieldInput.INTERACT, true)
	assert_ne(key, pad, "the action has a key and a pad button")
	for step: Array in _steps():
		(step[0] as Callable).call()
		prompt.advance(0.1)
		assert_eq(prompt.key_text_shown(), pad if bool(step[1]) else key, "after %s" % step[2])
	_done()


func test_a_tip_on_show_renames_its_bindings_with_the_device() -> void:
	var card := TipCard.new()
	card.tips = TutorialTips.new(
		func(f: StringName) -> bool: return bool(flags.get(f, false)),
		func(f: StringName) -> void: flags[f] = true,
		func() -> bool: return true
	)
	_add(card)
	card.advance(0.0)
	assert_true(card.is_showing(), "the objective tip")
	var raw := tr("TIP_OBJECTIVE_BODY")
	for step: Array in _steps():
		(step[0] as Callable).call()
		card.advance(0.01)
		assert_eq(card.body_text(), InputNames.fill(raw, bool(step[1])), "after %s" % step[2])
	_done()


func test_a_dialogue_line_names_its_bindings_for_the_device() -> void:
	var box := (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
	_add(box)
	box.set_process(false)
	var key := InputNames.first_name(FieldInput.INTERACT, false)
	var pad := InputNames.first_name(FieldInput.INTERACT, true)
	var line := "Press {%s}." % FieldInput.INTERACT
	box.show_text(&"", StringName(line))  # an untranslated key reads as itself
	box.skip_reveal()
	assert_eq(box.shown_text(), "Press %s." % key, "the keyboard's name")
	_use(InputDriver.Kind.PAD)
	box.show_text(&"", StringName(line))
	box.skip_reveal()
	assert_eq(box.shown_text(), "Press %s." % pad, "the pad's name after a pad press")
	_done()


# --- helpers --------------------------------------------------------------------------------------


## [what to do, pad expected, label] for a walk over every device.
func _steps() -> Array:
	return [
		[_use.bind(InputDriver.Kind.PAD), true, "a pad press"],
		[_use.bind(InputDriver.Kind.KEYS), false, "a key press"],
		[_use.bind(InputDriver.Kind.PAD), true, "a pad press again"],
		[func() -> void: InputDriver.click_at(Vector2.ONE), false, "a left click"],
		[_use.bind(InputDriver.Kind.PAD), true, "a pad press again"],
		[func() -> void: InputDriver.click_at(Vector2.ONE, MOUSE_BUTTON_RIGHT), false, "a right click"],
	]


## A real press of ui_accept with device `k` (nothing in these tests listens for it).
func _use(k: InputDriver.Kind) -> void:
	InputDriver.new(k).press(&"ui_accept")


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	InputNames.using_pad = false
	UiSettings.set_shared(null)
