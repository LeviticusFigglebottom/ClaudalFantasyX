extends TestCase
## M2-BPR-07: per-encounter arenas. Data names real encounters and scenes; a story encounter's arena replaces the
## sandbox's WorldEnvironment, Sun and Arena (keeping Arena/Sea for the flood rig); the sandbox and the capture
## fixtures keep the sandbox's own arena; a retry keeps the arena it has.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const PARTY: Array[StringName] = [&"rhen", &"asha"]

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_data_names_real_encounters_and_scenes() -> void:
	var db := BattleDB.load_default()
	for enc: StringName in [&"ch02_tideline", &"drownbell"]:
		var path := BattleArena.scene_for(db, enc)
		assert_true(ResourceLoader.exists(path), "%s has an arena scene" % enc)
		var arena := (load(path) as PackedScene).instantiate()
		for n in ["WorldEnvironment", "Sun", "Sea"]:
			assert_true(arena.get_node_or_null(NodePath(n)) != null, "%s has %s" % [path, n])
		arena.free()
	assert_eq(BattleArena.scene_for(db, &"sandbox_reef"), "", "the sandbox keeps its own arena")
	_free()


func test_a_story_encounter_fights_in_its_arena() -> void:
	var sandbox_env := ctl.get_node(^"WorldEnvironment")
	var empty: Array[StringName] = []
	ctl.start_battle(PARTY, empty, &"drownbell", 7)
	assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), BattleArena.scene_for(ctl.engine.db, &"drownbell"))
	var env := ctl.get_node(^"WorldEnvironment") as WorldEnvironment
	assert_ne(env, sandbox_env, "the arena's environment replaced the sandbox's")
	assert_true(ctl.get_node_or_null(^"Arena/Sea") != null, "the flood rig's sea is there")
	assert_true(ctl.get_node_or_null(^"Arena/Fill") != null, "the arena's other children are under Arena")
	assert_eq(ctl.get_node(^"Arena").get_children().filter(func(n: Node) -> bool: return n.name == &"Dais").size(), 0)
	assert_eq(ctl.get_children().filter(func(n: Node) -> bool: return n.name == &"Sun").size(), 1, "one sun")
	ctl.start_battle(PARTY, empty, &"drownbell", 7)
	assert_eq(ctl.get_node(^"WorldEnvironment"), env, "a retry keeps the arena")
	_free()


func test_capture_fixtures_keep_the_sandbox_arena() -> void:
	var env := ctl.get_node(^"WorldEnvironment")
	ctl.run_script(BattleController.SCRIPT_PLAYER_PREVIEW)
	assert_eq(ctl.get_node(^"WorldEnvironment"), env)
	assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), "")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
