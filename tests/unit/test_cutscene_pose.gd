extends TestCase
## M2-FP-103: a posing @anim (sequencer.json hold_clips) holds through the actor's lines instead of being
## stood up by the talk clip; a requested clip that is not built yet plays its clip_stand_ins stand-in;
## @light eases a stage practical off and back on to its authored energy.

const SCENE := &"test_cutscene_pose"
const LAMP_ENERGY := 1.7
const TOLERANCE := 0.001

var stage: CutsceneStage
var seq: CutsceneSequencer
var ap: AnimationPlayer
var lamp: OmniLight3D


func before_each() -> void:
	stage = CutsceneStage.new()
	stage.name = "CutsceneStage"
	_host().add_child(stage)
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	var asha := Node3D.new()
	asha.name = "asha"
	actors.add_child(asha)
	ap = AnimationPlayer.new()
	ap.name = "AnimationPlayer"
	asha.add_child(ap)
	var lib := AnimationLibrary.new()
	for clip: StringName in [&"idle", &"talk", &"kneel_over_rhen"]:
		var a := Animation.new()
		a.length = 1.0
		lib.add_animation(clip, a)
	ap.add_animation_library(&"", lib)
	lamp = OmniLight3D.new()
	lamp.name = "Lamp"
	lamp.light_energy = LAMP_ENERGY
	asha.add_child(lamp)
	seq = CutsceneSequencer.new()
	seq.instant = true
	_host().add_child(seq)
	seq.config = CutsceneSequencer.load_config()
	seq.config["clip_stand_ins"] = {"asha/sit_up": "kneel_over_rhen"}


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	seq.free()
	stage.free()


func test_a_held_pose_is_not_stood_up_by_a_line() -> void:
	await seq.play(SCENE, stage)
	assert_eq(String(ap.current_animation), "kneel_over_rhen", "she is still kneeling after her line")
	_done()


func test_without_a_hold_the_line_plays_talk() -> void:
	seq.config["hold_clips"] = []
	await seq.play(SCENE, stage)
	assert_eq(String(ap.current_animation), "talk", "a gesture gives way to the talk clip")
	_done()


func test_an_unbuilt_clip_plays_its_stand_in() -> void:
	seq.config["hold_clips"] = ["sit_up"]
	await seq.play(SCENE, stage)
	assert_eq(String(ap.current_animation), "kneel_over_rhen", "sit_up is not built: its stand-in plays, and holds")
	_done()


func test_an_unbuilt_clip_without_a_stand_in_is_skipped() -> void:
	seq.config["hold_clips"] = ["sit_up"]
	seq.config["clip_stand_ins"] = {}
	await seq.play(SCENE, stage)
	assert_eq(String(ap.current_animation), "talk", "nothing to play: no pose is held and the line talks")
	_done()


func test_the_lamp_goes_dark_then_back_to_its_energy() -> void:
	var seen: Array[float] = []
	seq.cue_played.connect(
		func(c: StringName, _a: Array, _k: Dictionary) -> void:
			if c == &"anim":
				seen.append(lamp.light_energy)
	)
	await seq.play(SCENE, stage)
	assert_true(not seen.is_empty() and seen[0] < TOLERANCE, "dark before the line")
	assert_between(lamp.light_energy, LAMP_ENERGY - TOLERANCE, LAMP_ENERGY + TOLERANCE, "back to its authored energy")
	assert_true(seq.warnings.is_empty(), "%s" % [seq.warnings])
	_done()
