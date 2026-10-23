extends TestCase
## M2-FP-03: New Game routing to the prologue, the prologue scene's stage and hand-off, and the
## prologue cutscene script. The hand-off travel is recorded, never performed; Game.state is a
## fresh state per test.

const PROLOGUE_SCENE := "res://game/levels/prologue/prologue.tscn"
const SCENE_ID := &"prologue_dead_city"
const LINE_KEY := &"DLG_PROLOGUE_DEAD_CITY_001"
const NEXT_LOCATION := &"ch02/haluna"
const NEXT_SPAWN := &"Beach"
## Far more steps than the script has; a run that needs more is looping.
const MAX_STEPS := 100

var travels: Array[Array] = []
var scene: PrologueScene
var _saved_state: GameStateData


func before_each() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()


func _done() -> void:
	if scene != null and is_instance_valid(scene):
		if scene.get_parent() != null:
			scene.get_parent().remove_child(scene)
		scene.free()
	Game.state = _saved_state


func _make_scene() -> PrologueScene:
	scene = (load(PROLOGUE_SCENE) as PackedScene).instantiate() as PrologueScene
	scene.autoplay = false
	scene.travel = func(loc: StringName, spawn: StringName) -> bool:
		travels.append([loc, spawn])
		return true
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(scene)
	return scene


func test_new_game_starts_at_the_prologue() -> void:
	var reg := LocationRegistry.load_default()
	assert_eq(reg.new_game_location, &"prologue")
	assert_eq(reg.new_game_spawn, &"Start")
	assert_true(reg.can_enter(&"prologue"), "the prologue counts as playable (place_at)")
	var to := reg.resolve(reg.new_game_location, reg.new_game_spawn)
	assert_eq(to["scene"], PROLOGUE_SCENE)
	assert_eq(to["spawn"], &"Start")
	assert_false(bool(to["fallback"]))
	assert_true(reg.has_location(NEXT_LOCATION), "the hand-off target is registered")
	_done()


func test_the_scene_is_staged_for_the_cutscene() -> void:
	_make_scene()
	assert_true(scene.get_node_or_null(^"Spawns/Start") is Marker3D, "Spawns/Start")
	assert_true(scene.place_at(&"Start"))
	assert_true(WorldReturn.place_player(scene, &"Start"), "the router can place the party")
	var shot := scene.stage.shot(&"P01")
	assert_true(shot != null, "the stage resolves P01")
	if shot != null:
		assert_eq(shot.mode, CameraShot.Mode.FIXED)
	assert_eq(scene.stage.director(), scene.director, "the stage finds the scene's director")
	assert_eq(scene.director.initial_shot, shot, "the director opens on P01")
	_done()


func test_play_sets_prologue_seen_and_hands_off_to_haluna() -> void:
	_make_scene()
	var seq := CutsceneSequencer.new()
	seq.instant = true
	scene.add_child(seq)
	scene.sequencer = seq
	assert_false(bool(Game.get_flag(&"prologue_seen")))
	scene.play()
	assert_true(bool(Game.get_flag(&"prologue_seen")), "prologue_seen is set")
	assert_true(scene.finished, "an instant cutscene ends at once")
	assert_eq(travels, [[NEXT_LOCATION, NEXT_SPAWN]] as Array[Array], "on to Haluna at Beach")
	assert_false(scene.hand_off(), "the hand-off happens once")
	assert_eq(travels.size(), 1)
	_done()


func test_the_prologue_script_runs_to_the_end() -> void:
	var runner := DialogueRunner.new()
	runner.forward_events_to_bus = false
	assert_true(runner.load_scene(SCENE_ID))
	assert_true(runner.start())
	var lines: Array[DialogueStep] = []
	var cues: Array[StringName] = []
	var cameras: Array = []
	var ended := false
	for _i in MAX_STEPS:
		var step := runner.next()
		if step.is_end():
			ended = true
			break
		if step.is_line():
			lines.append(step)
		elif step.is_cue():
			cues.append(step.cue)
			if step.cue == &"camera":
				cameras.append(step.args[0])
	assert_true(ended, "reaches END")
	assert_eq(lines.size(), 1, "one narrated line, no more story than SPEC §3.5")
	if lines.size() == 1:
		assert_eq(lines[0].text_key, LINE_KEY)
		assert_eq(lines[0].narrator, &"rhen", "Rhen's voice-over")
		assert_true(lines[0].tags.has("vo"))
		assert_ne(tr(LINE_KEY), String(LINE_KEY), "the line is translated")
	assert_eq(cameras, ["P01"], "framed on P01")
	assert_true(cues.has(&"letterbox") and cues.has(&"fade") and cues.has(&"wait"))
	_done()
