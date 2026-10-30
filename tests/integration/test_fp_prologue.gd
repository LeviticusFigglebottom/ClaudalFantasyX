extends TestCase
## M2-FP-03: New Game routing to the prologue, the prologue scene's stage and hand-off, and the
## prologue cutscene script. The hand-off travel is recorded, never performed; Game.state is a
## fresh state per test.

const PROLOGUE_SCENE := "res://game/levels/prologue/prologue.tscn"
const SCENE_ID := &"prologue_dead_city"
const LINE_KEY := &"DLG_PROLOGUE_DEAD_CITY_001"
## Act I's route (first_playable.json prologue.next_location): the M2 review switch flipped on 2026-10-29 under
## ADR 0042 (M3-CIN-1233), so the prologue hands off to Ch1 (M3-C01-02), not the slice's beach.
const NEXT_LOCATION := &"ch01/oruvel_underway"
const NEXT_SPAWN := &"Drop"
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
## M2-FP-28, second playtest: the figures of the line ("everyone ... is still here") read near-black.
## Their cloth (palette.json cloth family) must have colour and enough value to read in the rim light.
const MIN_FIGURE_SAT := 0.25
const MIN_FIGURE_VALUE := 0.4
## M2-FP-103: the three of the seven without a model yet stand as cloth-coloured silhouettes (City/Vigils);
## the other four are the cast (CutsceneStage/Actors), three of them on HeroFieldActor bodies.
const SILHOUETTE_COUNT := 3
## Iskarra's plaza paving top (env-art's TERRACE_TOP_Y).
const PAVING_TOP_Y := 0.4
const FEET_TOLERANCE := 0.01
const BODY_CAST: Array[StringName] = [&"rhen", &"asha", &"toma"]
const MODEL_CAST: Array[StringName] = [&"ysolde"]
## Colour script prologue_iskarra_dusk: saturation x1.05; the grade stand-in's points (lut_prologue_dusk).
const SCRIPT_SATURATION := 1.05
const GRADE_MID := 0.5
const GRADE_TOE := 0.0
## The lantern rides Rhen's body at chest height (hero_motion.json field.heroes.rhen.carry).
const LANTERN_REACH_M := 1.8
const LANTERN_ENERGY := 1.5
const SETTLE_FRAMES := 90
const SETTLE_DT := 1.0 / 30.0
const FACING_TOLERANCE := 0.2

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


func test_play_sets_prologue_seen_and_hands_off_to_ch01() -> void:
	_make_scene()
	var seq := CutsceneSequencer.new()
	seq.instant = true
	scene.add_child(seq)
	scene.sequencer = seq
	assert_false(bool(Game.get_flag(&"prologue_seen")))
	scene.play()
	assert_true(bool(Game.get_flag(&"prologue_seen")), "prologue_seen is set")
	assert_true(scene.finished, "an instant cutscene ends at once")
	assert_eq(travels, [[NEXT_LOCATION, NEXT_SPAWN]] as Array[Array], "on to Ch1's Underway at Drop (Act I)")
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
	var cards: Array = []
	var ended := false
	for _i in MAX_STEPS:
		var step := runner.next()
		if step.is_end():
			ended = true
			break
		if step.is_line() and step.tags.has(CutsceneCard.TAG):
			cards.append(step)  # the title card (the human's playtest, 2026-10-30): not narration
		elif step.is_line():
			lines.append(step)
		elif step.is_cue():
			cues.append(step.cue)
			if step.cue == &"camera":
				cameras.append(step.args[0])
	assert_true(ended, "reaches END")
	assert_eq(lines.size(), 1, "one narrated line, no more story than SPEC §3.5")
	assert_eq(cards.size(), 1, "the 'Prologue' title card opens it, so it reads as the prologue")
	if lines.size() == 1:
		assert_eq(lines[0].text_key, LINE_KEY)
		assert_eq(lines[0].narrator, &"rhen", "Rhen's voice-over")
		assert_true(lines[0].tags.has("vo"))
		assert_ne(tr(LINE_KEY), String(LINE_KEY), "the line is translated")
	assert_eq(cameras, ["P01", "P02"], "the wide on P01, drifting into the P02 two-shot")
	assert_true(cues.has(&"mark") and cues.has(&"light") and cues.has(&"vfx"), "he crosses, the wick catches, glimmer")
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


## M2-FP-28 (second playtest: still grey while the line is up). The line's subject is the seven vigils:
## each wears a cloth colour, Rhen carries his lit oil lantern, and the environment holds the colour
## script's saturation and a stand-in of its grade (gold mids, teal toe) until Rendering's LUT lands.
func test_the_figures_and_the_grade_carry_colour_while_the_line_is_up() -> void:
	_make_scene()
	var figures := scene.get_node(^"City/Vigils").find_children("*", "MeshInstance3D", false, false)
	assert_eq(figures.size(), SILHOUETTE_COUNT, "the three still without models")
	for id in BODY_CAST:
		var a := scene.stage.actor(id)
		assert_true(a != null and a.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) != null, "%s's body" % id)
	for id in MODEL_CAST:
		var a := scene.stage.actor(id)
		assert_true(
			a != null and not a.find_children("*", "AnimationPlayer", true, false).is_empty(), "%s's model" % id
		)
	for n in figures:
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue  # dressed in its hero's body (dress_vigils)
		var mat := mi.material_override if mi.material_override != null else mi.mesh.surface_get_material(0)
		var std := mat as StandardMaterial3D
		assert_true(std != null, "%s has a plain material" % mi.name)
		if std != null:
			var c := std.albedo_color
			assert_true(c.s >= MIN_FIGURE_SAT, "%s wears a colour, not grey (s %.2f)" % [mi.name, c.s])
			assert_true(c.v >= MIN_FIGURE_VALUE, "%s is not a black silhouette (v %.2f)" % [mi.name, c.v])
	var lantern := scene.stage.find_child("LanternLight", true, false) as OmniLight3D
	assert_true(lantern != null, "Rhen's oil lantern (colour script: the one practical)")
	if lantern != null:
		assert_true(lantern.light_color.s >= MIN_LIGHT_SAT and lantern.light_color.h <= WARM_HUE_MAX, "warm oil light")
		var rhen := scene.stage.actor(&"rhen")
		var reach := lantern.global_position.distance_to(rhen.global_position)
		assert_true(reach <= LANTERN_REACH_M, "the lantern is at Rhen's hand")
	var env := (scene.get_node(^"WorldEnvironment") as WorldEnvironment).environment
	assert_true(env.adjustment_saturation >= SCRIPT_SATURATION - ENERGY_TOLERANCE, "colour script saturation x1.05")
	var grade := env.adjustment_color_correction as GradientTexture1D
	assert_true(grade != null and grade.gradient != null, "the dusk grade stand-in is on")
	if grade != null and grade.gradient != null:
		var mid := grade.gradient.sample(GRADE_MID)
		assert_true(mid.r > GRADE_MID and mid.r > mid.b, "gold gain in the mids")
		var toe := grade.gradient.sample(GRADE_TOE)
		assert_true(toe.b > toe.r and toe.g > toe.r, "teal lift in the toe")
	_done()


## M2-FP-103: the lantern is dark until the line, then catches to its authored energy; glimmer rises at Rhen.
func test_the_lantern_catches_and_glimmer_rises() -> void:
	_make_scene()
	var lantern := scene.stage.find_child("LanternLight", true, false) as OmniLight3D
	var seq := CutsceneSequencer.new()
	seq.instant = true
	scene.add_child(seq)
	scene.sequencer = seq
	scene.play()
	assert_true(seq.warnings.is_empty(), "no unplaced cue: %s" % [seq.warnings])
	assert_between(lantern.light_energy, LANTERN_ENERGY - ENERGY_TOLERANCE, LANTERN_ENERGY + ENERGY_TOLERANCE, "lit")
	var mark := scene.stage.mark(&"by_asha")
	assert_false(mark.find_children("Vfx_glimmer_lift*", "", false, false).is_empty(), "glimmer at Rhen")
	var rhen := scene.stage.actor(&"rhen")
	assert_true(
		rhen.global_position.distance_to(mark.global_position) < ENERGY_TOLERANCE + 0.01, "he has crossed to Asha"
	)
	var body := rhen.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	for i in SETTLE_FRAMES:
		body.advance(SETTLE_DT)
	var to_asha := scene.stage.actor(&"asha").global_position - rhen.global_position
	var want := atan2(-to_asha.x, -to_asha.z)
	var got := body.visible_yaw()
	assert_between(
		angle_difference(got, want),
		-FACING_TOLERANCE,
		FACING_TOLERANCE,
		"his body turns to Asha (%.0f vs %.0f)" % [rad_to_deg(got), rad_to_deg(want)]
	)
	_done()


## M3-ENV-724: a vigil takes its hero's field body once hero_motion.json lists one, feet on the paving, and its
## capsule goes. Kerrid borrows Ysolde's model here, since no vigil hero has a body yet.
func test_a_vigil_takes_its_body_when_its_hero_has_one() -> void:
	var saved: Dictionary = HeroFieldActor._data_cache
	var data := HeroFieldActor.data().duplicate(true)
	var heroes: Dictionary = data["field"]["heroes"]
	heroes["kerrid"] = heroes["ysolde"]
	HeroFieldActor._data_cache = data
	_make_scene()
	var kerrid := scene.get_node(^"City/Vigils/Kerrid") as MeshInstance3D
	assert_true(kerrid.mesh == null, "his capsule goes")
	var feet := kerrid.get_node_or_null(NodePath(String(PrologueScene.VIGIL_FEET))) as Node3D
	assert_true(feet != null and feet.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) != null, "his body")
	if feet != null:
		var y := feet.global_position.y
		assert_between(y, PAVING_TOP_Y - FEET_TOLERANCE, PAVING_TOP_Y + FEET_TOLERANCE, "feet on the paving")
	for id: String in ["Pell", "Liss"]:  # M3-CHR-506, M3-CHR-03: they have their field bodies too now
		var vigil := scene.get_node(NodePath("City/Vigils/" + id)) as MeshInstance3D
		assert_true(vigil.mesh == null, id + "'s capsule goes")
	HeroFieldActor._data_cache = saved
	_done()
