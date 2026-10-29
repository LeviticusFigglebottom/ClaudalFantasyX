extends TestCase
## M3-ARC-03: the box tells a listener what it voices. `line_started(step)` fires as show_line() starts a line,
## `blip(voice)` for every blip due (the speaker, or the narrator identity on narration), and `external_voice`
## leaves the box's own Blip player quiet while blips are still counted and emitted.

const SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const LINE_KEY := &"DLG_CH02_BEACH_004"
const CPS := 10.0
const STEP_SEC := 0.5

var box: DialogueBox
var voices: Array[StringName] = []
var started: Array[DialogueStep] = []


func before_each() -> void:
	voices.clear()
	started.clear()
	box = (load(SCENE) as PackedScene).instantiate() as DialogueBox
	box.settings = (
		DialogueTextSettings
		. from_dict(
			{
				"chars_per_sec": CPS,
				"min_chars_per_sec": 1.0,
				"max_chars_per_sec": 100.0,
				"blip_every_n_chars": 1,
				"blip_volume_db": 0.0,
				"narration_blip": true,
				"flap_vowels": "aeiouAEIOU",
			}
		)
	)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	box.set_process(false)
	box.blip.connect(func(v: StringName) -> void: voices.append(v))
	box.line_started.connect(func(s: DialogueStep) -> void: started.append(s))


func _step(speaker: StringName, narrator: StringName = &"") -> DialogueStep:
	var step := DialogueStep.new()
	step.kind = DialogueStep.Kind.LINE
	step.line_id = &"test_voice_hook_001"
	step.text_key = LINE_KEY
	step.speaker = speaker
	step.narrator = narrator
	return step


func test_a_line_reports_its_step_and_each_blip_its_voice() -> void:
	var step := _step(&"asha")
	box.show_line(step)
	assert_eq(started.size(), 1)
	assert_true(started[0] == step, "the step itself")
	box.advance(STEP_SEC)
	assert_true(voices.size() > 0 and voices.size() == box.blips_played, "one signal per blip")
	for v in voices:
		assert_eq(v, &"asha")
	box.free()


func test_narration_blips_carry_the_narrator() -> void:
	box.show_line(_step(&"", &"rhen"))
	box.advance(STEP_SEC)
	assert_true(voices.size() > 0)
	assert_eq(voices[0], &"rhen", "the narrator identity, not an empty voice")
	box.free()


func test_an_external_voice_keeps_the_box_quiet() -> void:
	var own := box.get_node(^"%Blip") as AudioStreamPlayer
	box.external_voice = true
	box.show_line(_step(&"toma"))
	box.advance(STEP_SEC)
	assert_true(box.blips_played > 0 and voices.size() == box.blips_played, "still counted and emitted")
	assert_false(own.playing, "the box's own player stays quiet")
	box.free()
