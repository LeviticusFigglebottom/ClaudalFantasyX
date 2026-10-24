extends TestCase
## M2-BPR-07: per-encounter arenas. Data names real encounters and scenes; a story encounter's arena replaces the
## sandbox's WorldEnvironment, Sun and Arena (keeping Arena/Sea for the flood rig); the sandbox and the capture
## fixtures keep the sandbox's own arena; a retry keeps the arena it has. M3-BPR-01: every arena keeps the scene
## contract, and every Act I encounter names one.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const PARTY: Array[StringName] = [&"rhen", &"asha"]
## Arenas with no open water in view, so no Sea.
const DRY_ARENAS: Array[String] = ["underway_tower", "ash_terrace_lanternfall"]
## Spot checks of the Act I mapping (M3-BPR-01's table); every row with one of ACT_ONE_PREFIXES is checked too.
const ACT_ONE := {
	&"ch01_wickfry": &"underway_tower",
	&"ch01_oil_slug": &"underway_tower",
	&"ch01_underway_limpet": &"underway_tower",
	&"ch01_scuttlers": &"oruvel_raft_morning",
	&"ch01_hullgnaw": &"oruvel_raft_morning",
	&"ch03_causeway_shore": &"causeway_route_afternoon",
	&"ch04_spar_wraith": &"derelict_deck_night",
	&"ch05_cinder_matron": &"ash_terrace_lanternfall",
}
const ACT_ONE_PREFIXES: Array[String] = ["ch01_", "ch03_", "ch04_", "ch05_"]

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
		assert_true(ResourceLoader.exists(BattleArena.scene_for(db, enc)), "%s has an arena scene" % enc)
	assert_eq(BattleArena.scene_for(db, &"sandbox_reef"), "", "the sandbox keeps its own arena")
	_free()


## M3-BPR-01: every arena scene loads and keeps the contract (a WorldEnvironment, a DirectionalLight3D Sun, and a
## Sea where the place has open water).
func test_every_arena_scene_keeps_the_contract() -> void:
	var scenes := BattleArena.data().get("scenes", {}) as Dictionary
	assert_true(scenes.size() >= 7, "the two slice arenas and the five Act I ones")
	for id: String in scenes:
		var path := BattleArena.scene_of(id)
		assert_true(ResourceLoader.exists(path), "%s: %s exists" % [id, path])
		var arena := (load(path) as PackedScene).instantiate()
		assert_true(arena.get_node_or_null(^"WorldEnvironment") is WorldEnvironment, "%s has a WorldEnvironment" % id)
		assert_true(arena.get_node_or_null(^"Sun") is DirectionalLight3D, "%s has a Sun" % id)
		var has_sea := arena.get_node_or_null(^"Sea") != null
		assert_eq(has_sea, not DRY_ARENAS.has(id), "%s: a Sea only over open water" % id)
		arena.free()
	_free()


## M3-BPR-01: every Act I story encounter fights in an arena (the task table; the Underway fights underwater).
func test_act_one_encounters_have_arenas() -> void:
	var db := BattleDB.load_default()
	for enc: StringName in ACT_ONE:
		assert_eq(BattleArena.scene_for(db, enc), BattleArena.scene_of(String(ACT_ONE[enc])), "%s's arena" % enc)
	for key: Variant in db.encounters:
		var enc := String(key)
		if ACT_ONE_PREFIXES.any(func(p: String) -> bool: return enc.begins_with(p)):
			assert_ne(BattleArena.scene_for(db, StringName(enc)), "", "%s fights in an arena" % enc)
	_free()


func test_an_arena_without_a_sea_applies() -> void:
	var empty: Array[StringName] = []
	ctl.start_battle(PARTY, empty, &"ch01_wickfry", 7)
	assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), BattleArena.scene_of("underway_tower"))
	assert_true(ctl.get_node_or_null(^"Arena/OilLamp") is OmniLight3D, "the lamp came with the arena")
	assert_true(ctl.get_node_or_null(^"Arena/Sea") == null, "no sea in the drowned tower")
	assert_eq(ctl.get_children().filter(func(n: Node) -> bool: return n.name == &"Sun").size(), 1, "one sun")
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


func test_an_arena_stages_the_choreography() -> void:
	var staging := (BattleArena.data()["staging"] as Dictionary)["underway_tower"] as Dictionary
	var empty: Array[StringName] = []
	ctl.start_battle(PARTY, empty, &"ch01_underway_limpet", 7)
	var choreo := ctl.stage.choreo
	assert_eq(choreo.arena_travel, float(staging["travel_scale"]), "shorter runs underwater")
	assert_eq(choreo.arena_tempo, float(staging["tempo"]), "slower underwater")
	choreo.set_speed(1.0)
	assert_between(choreo.speed, float(staging["tempo"]) - 0.001, float(staging["tempo"]) + 0.001)
	ctl.start_battle(PARTY, empty, &"sandbox_reef", 7)
	assert_eq(ctl.stage.choreo.arena_travel, 1.0, "the sandbox stages as before")
	assert_eq(ctl.stage.choreo.arena_tempo, 1.0)
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
