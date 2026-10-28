extends TestCase
## M2-FP-04: Cutscene B on the Shell Shrine set (M2-FP-116: the real shrine, not CSG). Every shot, actor and mark
## the script names exists on the stage (the only soft failure allowed is the Drownbell toll, which Audio has
## not made yet), every branch plays to its end, and the end card follows.

const SCENE := "res://game/levels/ch03/first_verse/first_verse.tscn"
## Soft failures the set may report: sounds that do not exist yet, and cue keys the placeholder
## presentation does not perform (grades, mote motion).
const ALLOWED_WARNINGS: Array[String] = ["no sound 'drownbell_toll'", "is not performed yet"]

var scene: FirstVerseScene
var saved_state: GameStateData
var changes: Array[String] = []
var requests: Array[BattleRequest] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	scene = (load(SCENE) as PackedScene).instantiate() as FirstVerseScene
	scene.autoplay = false
	scene.change_scene = func(path: String) -> void: changes.append(path)
	scene.start_battle = func(r: BattleRequest) -> void: requests.append(r)
	_host().add_child(scene)
	scene.sequencer.instant = true


func test_every_branch_plays_on_a_complete_stage_then_calls_the_drownbell() -> void:
	for flags: Array in [[], [&"ch02_heard_pila", &"ch03_found_net_float", &"ch02_rhen_stayed_with_dead"]]:
		for choice in 2:
			Game.state = GameStateData.new()
			for f: StringName in flags:
				Game.set_flag(f)
			changes.clear()
			requests.clear()
			scene.sequencer.auto_choice = choice
			scene.run()
			assert_false(scene.sequencer.is_playing(), "instant play finishes")
			assert_eq(changes, [] as Array[String], "no scene change of its own")
			assert_eq(requests.size(), 1, "the Drownbell is called to battle")
			var r := requests[0]
			assert_eq(r.encounter, &"drownbell")
			assert_eq(r.active, [&"rhen", &"asha", &"toma"] as Array[StringName], "all three, no reserve")
			assert_eq(r.reserve, [] as Array[StringName])
			assert_eq(r.victory_flag, &"ch03_drownbell_defeated")
			# M2-FP-15: a win goes back to Haluna's dock at night (B11), which ends on the end card.
			assert_eq(r.return_scene, "", "no scene: the party travels")
			assert_eq([r.return_location, r.return_spawn], [&"ch02/haluna", &"DockNight"])
			assert_true(bool(Game.get_flag(&"ch03_ilun_bound")), "the scene ran its flag writes")
			for w in scene.sequencer.warnings:
				assert_true(ALLOWED_WARNINGS.any(func(a: String) -> bool: return w.contains(a)), "stage gap: %s" % w)
	_free()


func test_the_stage_resolves_the_script_ids() -> void:
	var stage := scene.stage
	# M2-FP-11: the sun stays at bias 1.0; close shots key faces with CutsceneKeyLight (M2-FP-10).
	assert_true(stage.sun() != null and stage.sun().shadow_normal_bias == 1.0, "the zone sun keeps bias 1.0")
	for id: StringName in [&"S06", &"S07", &"S08", &"S09", &"S10", &"C08"]:
		assert_true(stage.shot(id) != null, "shot %s" % id)
	for id: StringName in [&"asha", &"toma", &"rhen"]:
		assert_true(stage.actor(id) != null, "actor %s" % id)
	# M2-FP-112: Rhen and Toma stand in their real bodies, not capsules.
	for id: StringName in [&"toma", &"rhen"]:
		assert_true(stage.actor(id).get_node_or_null(NodePath(String(HeroFieldActor.NAME))) != null, "%s's body" % id)
	for id: StringName in [&"chamber_pool", &"threshold_west", &"ilun_chamber", &"drownbell_arena", &"drownbell"]:
		assert_true(stage.mark(id) != null, "mark %s" % id)
	assert_true(stage.clip_mark(&"asha", &"emerge_doorway") != null, "Asha's doorway stand-in")
	assert_true(stage.director() != null)
	assert_true(scene.place_at(&"Start"))
	_free()


## M2-FP-116: the human's "primitive moments": the set is env-art's shrine and the kit's pieces, with no CSG left,
## and Asha stands at the inner pool for Ilun (S08) by its stand-in mark.
func test_the_set_is_the_real_shrine() -> void:
	assert_eq(scene.find_children("*", "CSGShape3D", true, false).size(), 0, "no CSG on the set")
	assert_true(scene.get_node_or_null(^"Set/Hall/Floor") != null, "env-art's shrine hall")
	var pool := scene.stage.clip_mark(&"asha", &"idle_shift")
	assert_true(pool != null, "the S08 stand-in mark")
	assert_true(scene.stage.clip_mark(&"asha", &"walk_to_chamber") == null, "S07's walk is her real clip, not a jump")
	var ilun := scene.stage.mark(&"ilun_chamber")
	assert_true(pool.global_position.distance_to(ilun.global_position) < 4.5, "Asha at the pool under Ilun")
	_free()


func _free() -> void:
	scene.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
