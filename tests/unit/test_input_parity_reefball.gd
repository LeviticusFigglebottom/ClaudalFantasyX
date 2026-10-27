extends TestCase
## M3-UI-01 with M2-UI-26 (input parity): the Reefball HUD's choice, walked with the keyboard, the
## controller and the mouse through real InputEvents (InputDriver): move to the second option (its
## preview follows), then choose it, and the engine performs exactly that option.

const MATCH := &"tidecup_opening"
const SEED := 7

var m: ReefballMatch
var hud: ReefballHud
var ctl: ReefballHudController


func before_each() -> void:
	InputDriver.clear_screen()
	UiSettings.set_shared(UiSettings.new())


func test_choose_an_option_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_open()
		assert_true(hud.is_choosing(), "%s: the player's contact opens the choices" % d.label())
		assert_true(hud.options.size() >= 2, "%s: more than one option" % d.label())
		var first := hud.preview_lines()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(hud.page().row_node(1))
		else:
			d.press(&"ui_down")
		assert_eq(hud.cursor(), 1, "%s: the cursor moves to the second option" % d.label())
		assert_ne(hud.preview_lines(), first, "%s: the preview follows the cursor" % d.label())
		var want := hud.options[1]
		var contacts := m.contacts
		var chosen: Array = []
		m.action_resolved.connect(func(r: Dictionary) -> void: chosen.append(r), CONNECT_ONE_SHOT)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(hud.page().row_node(1))
		else:
			d.press(&"ui_accept")
		assert_eq(m.contacts, contacts + 1, "%s: the choice is performed once" % d.label())
		assert_eq(chosen.size(), 1, "%s: one result" % d.label())
		if chosen.size() == 1:
			assert_eq(chosen[0]["action"], want["action"], "%s: the option chosen is the one shown" % d.label())
			assert_eq(chosen[0]["target"], want["target"], "%s: with its target" % d.label())
			assert_eq(chosen[0]["odds"], want["odds"], "%s: at the odds previewed" % d.label())
		assert_false(hud.is_choosing(), "%s: the menu closes on a choice" % d.label())
		_close()
	_done()


func test_the_wheel_steps_the_choices() -> void:
	_open()
	var at := hud.cursor()
	var first := hud.preview_lines()
	InputDriver.wheel(hud.page().row_node(at), 1)
	assert_ne(hud.cursor(), at, "the wheel moves the cursor")
	assert_ne(hud.preview_lines(), first, "and the preview follows")
	InputDriver.wheel(hud.page().row_node(hud.cursor()), -1)
	assert_eq(hud.cursor(), at, "and back")
	_close()
	_done()


## Nothing chooses for the player while the other side has the float.
func test_input_is_ignored_on_their_contact() -> void:
	_open()
	hud.hide_choices()
	var contacts := m.contacts
	var d := InputDriver.new(InputDriver.Kind.KEYS)
	d.press(&"ui_accept")
	assert_eq(m.contacts, contacts, "no menu, no choice")
	_close()
	_done()


func _open() -> void:
	m = ReefballMatch.new()
	m.setup(ReefballDB.load_default(), MATCH, SEED)
	hud = ReefballHud.new()
	ParityHost.scene_root().add_child(hud)
	ctl = ReefballHudController.new()
	ctl.pacing_scale = 0.0
	ctl.manual = true
	ParityHost.scene_root().add_child(ctl)
	ctl.start(m, hud)
	for _i in 200:
		if hud.is_choosing() and hud.options.size() >= 2:
			return
		if hud.is_choosing():
			hud.choose(0)
		elif not ctl.flush():
			return


func _close() -> void:
	for n: Node in [hud, ctl]:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()


func _done() -> void:
	UiSettings.set_shared(null)
	InputDriver.park_pointer()
