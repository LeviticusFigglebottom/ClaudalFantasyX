extends TestCase
## M2-UI-26 (input parity): the dialogue box's advance, a cutscene's choices, the backlog page and
## the hold to skip, each walked with the keyboard, the controller and the mouse through real
## InputEvents (InputDriver).

const BOX_SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const SEQUENCER_CONFIG := "res://game/data/cutscene/sequencer.json"
const LINE_KEY := &"DLG_CH02_BEACH_004"
const OPTION_KEYS: Array[StringName] = [&"DLG_CH02_BEACH_004", &"DLG_CH02_BEACH_004", &"DLG_CH02_BEACH_004"]
const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const FIXTURE := &"test_cutscene_fixture"

var made: Array[Node] = []
var advances: Array[int] = [0]


func before_each() -> void:
	InputDriver.clear_screen()
	_tree().paused = false
	UiSettings.set_shared(UiSettings.new())
	advances[0] = 0


func test_the_box_reveals_then_advances_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var box := _box()
		box.show_text(&"rhen", LINE_KEY)
		assert_true(box.is_revealing(), "%s: the line is revealing" % d.label())
		_confirm(d, box)
		assert_false(box.is_revealing(), "%s: the first Confirm shows the whole line" % d.label())
		assert_eq(advances[0], 0, "%s: and does not advance yet" % d.label())
		_confirm(d, box)
		assert_eq(advances[0], 1, "%s: the second Confirm advances" % d.label())
		_done()


func test_cutscene_choices_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var overlay := _overlay()
		var picked: Array[int] = []
		overlay.choices.chosen.connect(func(i: int) -> void: picked.append(i))
		overlay.choices.show_options(_options())
		_lay_out(overlay.choices)
		var buttons := _buttons(overlay.choices)
		assert_true(buttons[0].has_focus(), "%s: the first option has the focus" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(buttons[1])
			assert_true(buttons[1].has_focus(), "mouse: hover moves the focus")
			InputDriver.wheel(buttons[1], 1)
			assert_true(buttons[2].has_focus(), "mouse: the wheel steps down")
			InputDriver.wheel(buttons[2], -1)
			assert_true(buttons[1].has_focus(), "mouse: and up")
			InputDriver.click(buttons[1])
		else:
			d.press(&"ui_down")
			assert_true(buttons[1].has_focus(), "%s: Down moves the focus" % d.label())
			d.press(&"ui_down")
			d.press(&"ui_up")
			assert_true(buttons[1].has_focus(), "%s: Up comes back" % d.label())
			d.press(&"ui_accept")
		assert_eq(picked, [1] as Array[int], "%s: the second option is chosen" % d.label())
		assert_false(overlay.choices.visible, "%s: the choices close" % d.label())
		_done()


func test_the_box_does_not_advance_under_choices_on_a_click() -> void:
	var overlay := _overlay()
	overlay.box.show_text(&"rhen", LINE_KEY)
	overlay.box.skip_reveal()
	overlay.choices.show_options(_options())
	InputDriver.click(overlay.box.get_node(^"Panel") as Control)
	assert_eq(advances[0], 0, "a click on the box leaves the choices to the player")
	_done()


func test_the_backlog_opens_scrolls_and_closes_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var box := _box()
		var assist := box.get_node(^"DialogueAssist") as DialogueAssist
		assist.backlog = DialogueBacklog.new(int(DialogueAssist.load_data()["max_lines"]))
		for i in 12:
			box.show_text(&"rhen" if i % 2 == 0 else &"", LINE_KEY)
			box.skip_reveal()
		var panel := box.get_node(^"Panel") as Control
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(panel, -1)
		else:
			d.press(DialogueAssist.ACTION)
		assert_true(assist.backlog_open(), "%s: the backlog opens" % d.label())
		assert_true(_tree().paused, "%s: and holds the scene" % d.label())
		var page := assist.page
		var at := page.scroll_value()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(page, -1)
		else:
			d.press(&"ui_up")
		assert_true(page.scroll_value() < at, "%s: it scrolls back" % d.label())
		ParityHost.back(d, page)  # a right click for the mouse; the page's fade ends, so its layer goes
		assert_false(assist.backlog_open(), "%s: Cancel closes it" % d.label())
		assert_false(_tree().paused, "%s: and lets the scene go on" % d.label())
		_confirm(d, box)
		assert_eq(advances[0], 1, "%s: the box has the input again" % d.label())
		_done()


func test_hold_cancel_to_skip_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var seq := _sequencer()
		var need := float(seq.config["skip_hold_sec"])
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click_at(Vector2.ONE, MOUSE_BUTTON_RIGHT)
		else:
			d.press(&"ui_cancel")
		seq.advance(need * 0.5)
		assert_false(seq.overlay.skip_prompt.visible, "%s: a tap of Cancel is no hold" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.button_at(Vector2.ONE, MOUSE_BUTTON_RIGHT, true)
		else:
			d.hold(&"ui_cancel")
		seq.advance(need * 0.5)
		assert_true(seq.overlay.skip_prompt.visible, "%s: the fill shows while held" % d.label())
		seq.advance(need * 0.6)
		assert_true(seq.overlay.choices.visible, "%s: a full hold skips to the choice" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.button_at(Vector2.ONE, MOUSE_BUTTON_RIGHT, false)
		else:
			d.let_go(&"ui_cancel")
		assert_false(seq.overlay.skip_prompt.visible, "%s: letting go clears the fill" % d.label())
		seq.overlay.choices.pick(0)
		_done()


# --- helpers --------------------------------------------------------------------------------------


func _tree() -> SceneTree:
	return Engine.get_main_loop() as SceneTree


func _host(n: Node) -> void:
	var tree := _tree()
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


## A dialogue box on its own; time moves only through skip_reveal / advance.
func _box() -> DialogueBox:
	var box := (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
	_host(box)
	box.visible = true
	_settle(box)
	return box


func _overlay() -> CutsceneOverlay:
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER_CONFIG))
	var overlay := CutsceneOverlay.new(cfg)
	_host(overlay)
	overlay.box.visible = true
	_settle(overlay.box)
	return overlay


func _settle(box: DialogueBox) -> void:
	box.set_process(false)
	var assist := box.get_node(^"DialogueAssist") as DialogueAssist
	assist.set_process(false)
	box.advance_requested.connect(func() -> void: advances[0] += 1)


## A sequencer playing the test fixture over the field test zone, its first line up.
func _sequencer() -> CutsceneSequencer:
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	_host(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	(zone.get_node("Player") as FieldController).set_physics_process(false)
	zone.call("place_at", &"Lane")
	var stage := CutsceneStage.new()
	stage.name = "CutsceneStage"
	stage.director_path = ^"../CameraDirector"
	stage.player_path = ^"../Player"
	zone.add_child(stage)
	for folder: String in ["Shots", "Actors", "Marks"]:
		var n := Node3D.new()
		n.name = folder
		stage.add_child(n)
	var sn := CutsceneShotNode.new()
	sn.name = "wide"
	var shot := CameraShot.new()
	shot.id = &"wide"
	shot.position = Vector3(0, 6, 14)
	shot.look_at = Vector3(0, 1, 0)
	sn.shot = shot
	stage.get_node("Shots").add_child(sn)
	for id: String in ["asha"]:
		var a := Node3D.new()
		a.name = id
		stage.get_node("Actors").add_child(a)
	var spot := Marker3D.new()
	spot.name = "spot"
	stage.get_node("Marks").add_child(spot)
	var seq := CutsceneSequencer.new()
	seq.set_process(false)
	zone.add_child(seq)
	seq.play(FIXTURE, stage)
	var guard := 0
	while seq.is_playing() and not seq.overlay.box.visible and guard < 600:
		guard += 1
		(zone.get_node("CameraDirector") as FieldCameraDirector).update(1.0 / 30.0)
		seq.advance(1.0 / 30.0)
	assert_true(seq.overlay.box.visible, "the fixture's first line is up")
	return seq


## Sorts the choices' containers now, as the next frame would (focus moves and hovers are by
## position, and a test never reaches the frame's end).
func _lay_out(c: CutsceneChoices) -> void:
	c.reset_size()
	c.notification(Container.NOTIFICATION_SORT_CHILDREN)
	for box in c.find_children("*", "VBoxContainer", true, false):
		(box as Container).notification(Container.NOTIFICATION_SORT_CHILDREN)


func _options() -> Array[DialogueOption]:
	var out: Array[DialogueOption] = []
	for i in OPTION_KEYS.size():
		var o := DialogueOption.new()
		o.index = i
		o.text_key = OPTION_KEYS[i]
		out.append(o)
	return out


func _buttons(c: CutsceneChoices) -> Array[Button]:
	var out: Array[Button] = []
	for b in c.find_children("*", "Button", true, false):
		if not b.is_queued_for_deletion():
			out.append(b as Button)
	return out


## Confirm on the box with `d`'s device: ui_accept, or a click on the box's panel.
func _confirm(d: InputDriver, box: DialogueBox) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.click(box.get_node(^"Panel") as Control)
	else:
		d.press(&"ui_accept")


func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	_tree().paused = false
	UiSettings.set_shared(UiSettings.new())
	advances[0] = 0
