extends TestCase
## The dialogue box no longer snaps (DialogueBoxMotion; the human's "parts look primitive" note): shown,
## its panel fades and rises in; a new speaker's name fades in; dismiss() fades it out, then hides it.
## Reduced motion makes all of it instant. The runner runs no frames: tests drive the tweens with
## motion().advance / finish and free the box.

const SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const LINE_KEY := &"DLG_CH02_BEACH_004"
## capture.sh runs the capture at --fixed-fps 60.
const CAPTURE_FPS := 60.0

var box: DialogueBox
var panel: Control
var _saved_settings: UiSettings


func before_each() -> void:
	_saved_settings = UiSettings.shared()
	UiSettings.set_shared(UiSettings.new())
	box = (load(SCENE) as PackedScene).instantiate() as DialogueBox
	box.visible = false  # as CutsceneOverlay builds it
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	box.set_process(false)
	panel = box.get_node(^"Panel") as Control


func test_the_durations_settle_inside_a_capture() -> void:
	var m := box.motion()
	var shots := JSON.parse_string(FileAccess.get_file_as_string("res://tests/screenshots/shots.json")) as Dictionary
	var settle := float((shots["defaults"] as Dictionary)["settle_frames"]) / CAPTURE_FPS
	for k in ["open_sec", "close_sec", "name_sec"]:
		assert_true(m.seconds(k) > 0.0, "%s is set" % k)
		assert_true(m.seconds(k) < settle, "%s ends before a capture's settle frames do" % k)
	_done()


func test_shown_the_panel_fades_and_rises_into_place() -> void:
	var rest_top := panel.offset_top
	box.visible = true
	var m := box.motion()
	assert_true(m.is_moving(), "it comes in")
	assert_eq(panel.modulate.a, 1.0, "nothing is written before the first step (a test that runs no frames)")
	m.advance(m.seconds("open_sec") * 0.25)
	assert_between(panel.modulate.a, 0.01, 0.99, "part faded")
	assert_true(panel.offset_top > rest_top, "and lower than at rest")
	m.finish()
	assert_eq(panel.modulate.a, 1.0)
	assert_eq(panel.offset_top, rest_top, "exactly where it rests")
	_done()


func test_dismiss_fades_out_then_hides_and_a_new_line_brings_it_back() -> void:
	box.visible = true
	box.motion().finish()
	var seen := [0]
	box.motion().dismissed.connect(func() -> void: seen[0] += 1)
	box.dismiss()
	assert_true(box.visible and box.motion().is_dismissing(), "still drawn while it fades")
	box.motion().advance(box.motion().seconds("close_sec") * 0.5)
	assert_between(panel.modulate.a, 0.01, 0.99, "fading")
	box.show_text(&"asha", LINE_KEY)
	assert_false(box.motion().is_dismissing(), "a line while it fades brings it back")
	box.motion().finish()
	assert_true(box.visible)
	assert_eq(panel.modulate.a, 1.0)
	box.dismiss()
	box.motion().finish()
	assert_false(box.visible, "hidden once it has faded")
	assert_eq(seen[0], 1)
	assert_eq(panel.modulate.a, 1.0, "at rest for the next time it is shown")
	_done()


func test_a_new_speaker_s_name_fades_in_and_the_same_speaker_does_not() -> void:
	box.visible = true
	box.motion().finish()
	box.show_text(&"asha", LINE_KEY)
	box.motion().finish()
	var name_label := box.get_node(^"%SpeakerName") as Control
	box.show_text(&"rhen", LINE_KEY)
	assert_true(name_label.visible and box.motion().is_name_moving(), "a new speaker's name fades in")
	box.motion().finish()
	assert_eq(name_label.modulate.a, 1.0, "the new name ends fully shown")
	box.show_text(&"rhen", LINE_KEY)
	assert_false(box.motion().is_name_moving(), "the same speaker's name stays put")
	_done()


func test_reduced_motion_makes_it_instant() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	box.visible = true
	assert_false(box.motion().is_moving(), "no fade in")
	assert_eq(panel.modulate.a, 1.0)
	box.dismiss()
	assert_false(box.visible, "hidden at once")
	_done()


func _done() -> void:
	box.free()
	UiSettings.set_shared(_saved_settings)
