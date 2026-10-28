extends TestCase
## The title's opening reveal (TitleReveal; the "parts look primitive" pass): the logo fades in, then the choices
## rise into place, then the help line; the menu takes input from the start; Reduced motion shows everything at
## once; the whole reveal ends inside boot_title's settle frames.

## capture.sh runs the capture at --fixed-fps 60.
const CAPTURE_FPS := 60.0

var menu: TitleMenu
var _saved_settings: UiSettings


func before_each() -> void:
	_saved_settings = UiSettings.shared()
	UiSettings.set_shared(UiSettings.new())


func test_the_logo_then_the_choices_then_the_help_come_in_and_rest() -> void:
	_open()
	var r := menu.reveal
	assert_true(r.is_playing(), "it reveals")
	assert_eq(menu.logo.modulate.a, 0.0, "the logo starts unseen")
	var page := r.parts[1]["node"] as Control
	var help := r.parts[2]["node"] as Control
	var page_rest := page.position.y - float(r.parts[1]["rise"])
	assert_true(page.position.y > page_rest, "the choices start lower")
	assert_true(menu.handle_input(_ev(&"ui_down")), "input is taken during the reveal")
	r.finish()
	for n: Control in [menu.logo, page, help]:
		assert_eq(n.modulate.a, 1.0, "%s at rest" % n.name)
	assert_eq(page.position.y, page_rest, "the choices exactly in place")
	_done()


func test_reduced_motion_shows_everything_at_once() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	_open()
	assert_false(menu.reveal.is_playing())
	assert_eq(menu.logo.modulate.a, 1.0)
	_done()


func test_the_reveal_ends_inside_boot_title_s_settle_frames() -> void:
	_open()
	var shots := JSON.parse_string(FileAccess.get_file_as_string("res://tests/screenshots/shots.json")) as Dictionary
	var settle := 0
	for s: Dictionary in shots["shots"]:
		if s["id"] == "boot_title":
			settle = int(s.get("settle_frames", 0))
	assert_true(menu.reveal.duration() > 0.0)
	assert_true(menu.reveal.duration() < settle / CAPTURE_FPS, "boot_title captures the title at rest")
	_done()


func _open() -> void:
	menu = TitleMenu.new()
	menu.save_system = SaveSystem
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(menu)


func _done() -> void:
	if is_instance_valid(menu):
		menu.get_parent().remove_child(menu)
		menu.free()
	UiSettings.set_shared(_saved_settings)


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
