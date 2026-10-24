extends TestCase
## M2-FP-03: New Game routing to the prologue, the prologue scene's stage and hand-off, and the
## prologue cutscene script. The hand-off travel is recorded, never performed; Game.state is a
## fresh state per test.

const PROLOGUE_SCENE := "res://game/levels/prologue/prologue.tscn"
const SCENE_ID := &"prologue_dead_city"
const LINE_KEY := &"DLG_PROLOGUE_DEAD_CITY_001"
## The M2 review build's route (first_playable.json prologue.next_location; Act I's Ch1 comes after
## the human signs off M2, M3-C01-02).
const NEXT_LOCATION := &"ch02/haluna"
const NEXT_SPAWN := &"Beach"
## Far more steps than the script has; a run that needs more is looping.
const MAX_STEPS := 100
## M2-FP-28: the colour the dusk frame must carry (colour script prologue_iskarra_dusk).
const RIM_ENERGY := 1.4
const ENERGY_TOLERANCE := 0.001
const MIN_LIGHT_SAT := 0.5
## Hues as Color.h (0..1): gold-orange is under 0.15, teal 0.45-0.55.
const WARM_HUE_MAX := 0.15
const TEAL_HUE_MIN := 0.45
const TEAL_HUE_MAX := 0.55
const MAX_SKY_CONTRIBUTION := 0.4

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
	assert_eq(travels, [[NEXT_LOCATION, NEXT_SPAWN]] as Array[Array], "on to Haluna at Beach (the M2 slice route)")
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


## M2-FP-28 (playtest: the prologue read greyscale). The towers are near-white greybox and the key is
## behind them, so without a warm rim and a teal shadow tint every face the camera sees is lit only by
## blue-grey fill and ambient. Colour script prologue_iskarra_dusk: rim #F2A64A at 1.4, shadows toward
## deep_teal_shadow, saturation x1.05.
func test_the_dusk_frame_carries_colour() -> void:
	_make_scene()
	var rim := scene.get_node_or_null(^"Rim") as DirectionalLight3D
	assert_true(rim != null, "the colour script's rim light is in the scene")
	if rim != null:
		assert_true(rim.visible)
		assert_between(rim.light_energy, RIM_ENERGY - ENERGY_TOLERANCE, RIM_ENERGY + ENERGY_TOLERANCE, "rim energy")
		assert_true(rim.light_color.s >= MIN_LIGHT_SAT, "the rim is a warm colour, not white")
		assert_true(rim.light_color.h <= WARM_HUE_MAX, "the rim is gold-orange")
		var to_light := rim.global_transform.basis.z.normalized()
		var to_camera := (scene.get_node(^"Camera") as Camera3D).global_transform.basis.z.normalized()
		assert_true(to_light.dot(to_camera) > 0.0, "the rim lights the faces the camera sees (the key is behind)")
	var env := (scene.get_node(^"WorldEnvironment") as WorldEnvironment).environment
	var amb := env.ambient_light_color
	assert_true(amb.s >= MIN_LIGHT_SAT, "the shadow fill is tinted, not grey")
	assert_true(amb.h >= TEAL_HUE_MIN and amb.h <= TEAL_HUE_MAX, "the shadows lean teal (deep_teal_shadow)")
	assert_true(env.ambient_light_sky_contribution <= MAX_SKY_CONTRIBUTION, "the sky does not average the tint away")
	assert_true(env.adjustment_enabled and env.adjustment_saturation >= 1.0, "no desaturating grade")
	_done()
