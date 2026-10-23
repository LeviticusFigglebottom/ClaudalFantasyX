extends TestCase
## M2-FP-04: Cutscene B on the placeholder Shell Shrine set. Every shot, actor and mark the script
## names exists on the stage (the only soft failure allowed is the Drownbell toll, which Audio has
## not made yet), every branch plays to its end, and the end card follows.

const SCENE := "res://game/levels/ch03/first_verse/first_verse.tscn"
## Soft failures the set may report: sounds that do not exist yet.
const ALLOWED_WARNINGS: Array[String] = ["no sound 'drownbell_toll'"]

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
			assert_eq(r.return_scene, EndCard.SCENE, "a win goes on to the end card")
			assert_true(bool(Game.get_flag(&"ch03_ilun_bound")), "the scene ran its flag writes")
			for w in scene.sequencer.warnings:
				assert_true(ALLOWED_WARNINGS.any(func(a: String) -> bool: return w.contains(a)), "stage gap: %s" % w)
	_free()


func test_the_stage_resolves_the_script_ids() -> void:
	var stage := scene.stage
	for id: StringName in [&"S06", &"S07", &"S08", &"S09", &"S10", &"C08"]:
		assert_true(stage.shot(id) != null, "shot %s" % id)
	for id: StringName in [&"asha", &"toma", &"rhen"]:
		assert_true(stage.actor(id) != null, "actor %s" % id)
	for id: StringName in [&"chamber_pool", &"threshold_west", &"ilun_chamber", &"drownbell_arena", &"drownbell"]:
		assert_true(stage.mark(id) != null, "mark %s" % id)
	assert_true(stage.clip_mark(&"asha", &"emerge_doorway") != null, "Asha's doorway stand-in")
	assert_true(stage.director() != null)
	assert_true(scene.place_at(&"Start"))
	_free()


func _free() -> void:
	scene.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
