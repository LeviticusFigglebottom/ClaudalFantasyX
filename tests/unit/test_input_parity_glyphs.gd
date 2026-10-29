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


## Lead 2026-10-28 (input pass): every line that names a binding ({action}: tips, tutorial and story
## lines, any loc row) names it for both devices. Every {field_*}/{ui_*} is a real action; one with
## a pad button reads as that button after a pad press and as its key after a key press; one bound
## only to a stick (movement, camera) keeps its key name, so its line must say "stick" in words.
func test_every_prompt_names_its_bindings_for_both_devices() -> void:
	_ensure_every_action()
	var lines := _loc_rows()
	var named := 0
	for key: String in lines:
		var text := str(lines[key])
		for action: StringName in _bindings_in(text):
			named += 1
			assert_true(InputMap.has_action(action), "%s names {%s}, an action" % [key, action])
			if not InputMap.has_action(action):
				continue
			var k := InputNames.first_name(action, false)
			var p := InputNames.first_name(action, true)
			assert_ne(k, "", "%s: {%s} has a key" % [key, action])
			assert_false(InputNames.fill(text, false).contains("{%s}" % action), "%s keys: filled" % key)
			assert_false(InputNames.fill(text, true).contains("{%s}" % action), "%s pad: filled" % key)
			if _has_pad_button(action):
				assert_ne(k, p, "%s: {%s} reads as the pad's button after a pad press" % [key, action])
				assert_true(InputNames.fill(text, true).contains(p), "%s pad: %s" % [key, p])
				assert_true(InputNames.fill(text, false).contains(k), "%s keys: %s" % [key, k])
			else:
				assert_true(_has_pad_axis(action), "%s: {%s} has a pad button or a stick" % [key, action])
				assert_true(text.to_lower().contains("stick"), "%s: {%s} is a stick on the pad: say so" % [key, action])
	assert_true(named > 10, "the tips, the Ch1 tutorials and the hold prompts name bindings")


## No Act I prompt names a binding in plain words ("Press interact", "Press E"): it says {action}
## instead, so the name follows the device and the Controls page.
func test_no_act1_prompt_names_a_binding_in_plain_words() -> void:
	var re := RegEx.create_from_string(
		"\\b(Press|press|Hold|hold)\\s+(interact|E|F|Q|R|Tab|Escape|Esc|Enter|Space|Shift|A|B|X|Y)\\b"
	)
	var lines := _loc_rows()
	var act1 := 0
	for key: String in lines:
		if not _is_act1(key):
			continue
		act1 += 1
		var m := re.search(str(lines[key]))
		assert_true(m == null, "%s names a binding in words: '%s'" % [key, m.get_string() if m else ""])
	assert_true(act1 > 100, "the Act I rows were read")


## The two keycap prompts Act I uses (the interaction plate on every interactable, and the Ebbing's
## hold plate in Ch9) name field_interact's key or pad button with the device; the Ch1 shutter's
## binding (ch01_field.json) has both too.
func test_the_act1_keycaps_follow_the_device() -> void:
	_ensure_every_action()
	var hold_action := StringName(str((_json("res://game/data/flow/ch09_field.json")["hold"] as Dictionary)["action"]))
	var hold := HoldPrompt.new()
	hold.action = hold_action
	_add(hold)
	hold.show_prompt("FIELD_PROMPT_CH09_RAISE_STAFF")
	var key := InputNames.first_name(hold_action, false)
	var pad := InputNames.first_name(hold_action, true)
	assert_ne(key, pad, "the hold action has a key and a pad button")
	for step: Array in _steps():
		(step[0] as Callable).call()
		hold.advance(0.1)
		assert_eq(hold.key_text_shown(), pad if bool(step[1]) else key, "hold prompt after %s" % step[2])
	var shutter := StringName(str(_find_key(_json("res://game/data/flow/ch01_field.json"), "action")))
	assert_eq(shutter, &"field_lantern_shutter", "Ch1's held shutter")
	assert_true(_has_pad_button(shutter), "the shutter has a pad button")
	assert_ne(InputNames.first_name(shutter, false), InputNames.first_name(shutter, true), "shutter names differ")
	_done()


# --- helpers --------------------------------------------------------------------------------------


## Every action a line may name: the field's, the objective's, and each chapter's own (any
## "actions" table in game/data/flow/*.json, such as Ch1's shutter).
func _ensure_every_action() -> void:
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	for f: String in DirAccess.get_files_at("res://game/data/flow"):
		if f.ends_with(".json"):
			var actions: Variant = _find_key(_json("res://game/data/flow/" + f), "actions")
			if actions is Dictionary:
				FieldInput.add_actions(actions as Dictionary, 0.5)


## {key: English text} for every row of every loc CSV.
func _loc_rows() -> Dictionary:
	var out := {}
	for f: String in DirAccess.get_files_at("res://game/data/loc"):
		if not f.ends_with(".csv"):
			continue
		var fa := FileAccess.open("res://game/data/loc/" + f, FileAccess.READ)
		fa.get_csv_line()  # header
		while not fa.eof_reached():
			var row := fa.get_csv_line()
			if row.size() >= 2 and row[0] != "":
				out[row[0]] = row[1]
	return out


## The {name}s in `text` that name a binding: an InputMap action, or anything field_*/ui_*.
func _bindings_in(text: String) -> Array[StringName]:
	var out: Array[StringName] = []
	for m in RegEx.create_from_string("\\{([a-z_]+)\\}").search_all(text):
		var n := StringName(m.get_string(1))
		if InputMap.has_action(n) or String(n).begins_with("field_") or String(n).begins_with("ui_"):
			out.append(n)
	return out


## Act I (ADR 0041: the title to Ch9): the Ch1-Ch9 tables, their dialogue, the tips and field prompts.
func _is_act1(key: String) -> bool:
	for prefix: String in ["DLG_CH0", "TIP_", "FIELD_PROMPT_CH0", "TUT_CH0"]:
		if key.begins_with(prefix):
			return true
	return key.begins_with("FIELD_PROMPT_") and not key.begins_with("FIELD_PROMPT_CH1")


func _has_pad_button(action: StringName) -> bool:
	return InputMap.action_get_events(action).any(func(e: InputEvent) -> bool: return e is InputEventJoypadButton)


func _has_pad_axis(action: StringName) -> bool:
	return InputMap.action_get_events(action).any(func(e: InputEvent) -> bool: return e is InputEventJoypadMotion)


func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed as Dictionary if parsed is Dictionary else {}


## The first value under `key` anywhere in `d` (depth first), or null.
func _find_key(d: Dictionary, key: String) -> Variant:
	if d.has(key):
		return d[key]
	for v: Variant in d.values():
		if v is Dictionary:
			var found: Variant = _find_key(v as Dictionary, key)
			if found != null:
				return found
	return null


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
