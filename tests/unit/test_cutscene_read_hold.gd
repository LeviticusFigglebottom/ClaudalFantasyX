extends TestCase
## An overheard bark's line stays up long enough to read (the Lead's dialogue pass, 2026-10-28): with a reading pace
## set (overheard_read_cps), an auto-advancing line holds until its whole time on screen covers its length at that
## pace, never less than the plain hold; with none set, the plain hold as before.

const SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const REVEAL_CPS := 40.0
const READ_CPS := 15.0
const HOLD := 2.4
const TOLERANCE := 0.001

var box: DialogueBox


func before_each() -> void:
	box = (load(SCENE) as PackedScene).instantiate() as DialogueBox
	box.settings = (
		DialogueTextSettings
		. from_dict(
			{
				"chars_per_sec": REVEAL_CPS,
				"min_chars_per_sec": 1.0,
				"max_chars_per_sec": 400.0,
				"blip_every_n_chars": 1,
				"blip_volume_db": 0.0,
				"narration_blip": false,
				"flap_vowels": "aeiou",
			}
		)
	)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	box.set_process(false)


func _line(chars: int) -> void:
	# A plain key: tr() returns it as is, so the line's length is known.
	box.show_text(&"rhen", StringName("x".repeat(chars)))
	box.skip_reveal()


func test_a_short_line_keeps_the_plain_hold() -> void:
	_line(30)  # 30 / 15 = 2 s on screen, less than the reveal plus the hold
	assert_between(CutsceneMotion.read_hold(box, READ_CPS, HOLD), HOLD - TOLERANCE, HOLD + TOLERANCE)
	box.free()


func test_a_long_line_holds_until_it_can_be_read() -> void:
	_line(120)  # 120 / 15 = 8 s on screen; 3 s of it is the reveal
	var want := 120.0 / READ_CPS - 120.0 / REVEAL_CPS
	assert_between(CutsceneMotion.read_hold(box, READ_CPS, HOLD), want - TOLERANCE, want + TOLERANCE)
	box.free()


func test_no_reading_pace_is_the_plain_hold() -> void:
	_line(120)
	assert_between(CutsceneMotion.read_hold(box, 0.0, HOLD), HOLD - TOLERANCE, HOLD + TOLERANCE)
	box.free()
