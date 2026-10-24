extends TestCase
## M2-UI-20: the field interaction prompt. Driven by advance() with `pick` set to a scratch
## Interactable (no FieldController); the plate's placement is the pure place().

var prompt: InteractPrompt
var it: Interactable
var offer := true
var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	(Engine.get_main_loop() as SceneTree).paused = false
	UiSettings.set_shared(UiSettings.new())
	FieldInput.ensure_actions()
	offer = true
	it = Interactable.new()
	it.prompt_key = "FIELD_PROMPT_LISTEN"
	_add(it)
	prompt = InteractPrompt.new()
	prompt.pick = func() -> Interactable: return it if offer else null
	_add(prompt)


func test_it_fades_in_with_the_verb_and_the_key_then_out() -> void:
	assert_false(prompt.is_showing())
	prompt.advance(1.0)
	assert_true(prompt.is_showing(), "in reach: the plate shows")
	assert_eq(prompt.verb_text_shown(), tr("FIELD_PROMPT_LISTEN"))
	assert_eq(prompt.key_text_shown(), prompt.key_text())
	assert_ne(prompt.key_text_shown(), "", "the binding by name")
	offer = false
	prompt.advance(1.0)
	assert_false(prompt.is_showing(), "out of reach: it fades away")
	_done()


func test_an_interactable_with_no_verb_gets_the_default() -> void:
	it.prompt_key = ""
	assert_eq(prompt.verb_text(it), tr("FIELD_PROMPT_DEFAULT"))
	_done()


func test_the_keycap_follows_the_last_device() -> void:
	var events := InputMap.action_get_events(FieldInput.INTERACT)
	var key := ""
	var pad := ""
	for ev in events:
		if ev is InputEventKey and key == "":
			key = OS.get_keycode_string((ev as InputEventKey).physical_keycode)
		elif ev is InputEventJoypadButton and pad == "":
			pad = "set"
	assert_eq(prompt.key_text(), key, "keyboard first")
	var b := InputEventJoypadButton.new()
	b.pressed = true
	prompt.note_device(b)
	assert_true(prompt.using_pad)
	if pad != "":
		assert_ne(prompt.key_text(), key, "after the pad: its button")
		assert_eq(prompt.key_text(), tr("CTRL_PAD_A"), "pad A by its generic name")
	var k := InputEventKey.new()
	k.pressed = true
	prompt.note_device(k)
	assert_false(prompt.using_pad, "a key press goes back to the keyboard")
	_done()


func test_it_hides_while_a_menu_pauses_the_tree() -> void:
	prompt.advance(1.0)
	assert_true(prompt.is_showing())
	(Engine.get_main_loop() as SceneTree).paused = true
	prompt.advance(1.0)
	assert_false(prompt.is_showing(), "paused: hidden")
	(Engine.get_main_loop() as SceneTree).paused = false
	_done()


func test_placement_floats_over_the_point_or_docks() -> void:
	var size := Vector2(1920, 1080)
	var d := InteractPrompt.load_data()
	var over := prompt.place(false, Vector2(900, 400), size)
	assert_false(over["docked"])
	assert_eq(over["at"], Vector2(900, 400 - float(d["gap_px"])), "just above the point")
	var edge := prompt.place(false, Vector2(10, 400), size)
	assert_true(edge["docked"], "at the screen edge: docked")
	assert_eq(edge["at"], Vector2(960, float(d["dock_y"])), "bottom centre")
	assert_true(prompt.place(true, Vector2(900, 400), size)["docked"], "behind the camera: docked")
	_done()


func test_field_hud_attaches_both_pieces() -> void:
	var c := FieldController.new()
	_add(c)
	assert_true(c.get_node_or_null(^"ObjectiveLayer/ObjectiveHud") is ObjectiveHud)
	assert_true(c.get_node_or_null(^"InteractLayer/InteractPrompt") is InteractPrompt)
	_done()


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _done() -> void:
	UiSettings.set_shared(null)
