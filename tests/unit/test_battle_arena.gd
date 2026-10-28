extends TestCase
## M2-BPR-07: per-encounter arenas. Data names real encounters and scenes; a story encounter's arena replaces the
## sandbox's WorldEnvironment, Sun and Arena (keeping Arena/Sea for the flood rig); the sandbox and the capture
## fixtures keep the sandbox's own arena; a retry keeps the arena it has. M3-BPR-01: every arena keeps the scene
## contract, and every Act I encounter names one. M3-BPR-03: the Ch6 encounters fight on the Brine Shoals and at the
## burning camp.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const PARTY: Array[StringName] = [&"rhen", &"asha"]
## Spot checks of the Act I mapping (M3-BPR-01's table); every row with one of ACT_ONE_PREFIXES is checked too.
const ACT_ONE := {
	&"ch01_wickfry": &"underway_tower",
	&"ch01_oil_slug": &"underway_tower",
	&"ch01_underway_limpet": &"underway_tower",
	&"ch01_scuttlers": &"oruvel_raft_morning",
	&"ch01_hullgnaw": &"oruvel_raft_morning",
	&"ch03_causeway_shore": &"causeway_route_afternoon",
	&"ch04_spar_wraith": &"derelict_deck_night",
	&"ch05_cinder_matron": &"ashcrown_anvil_court",  # M3-BPR-1305: Ashcrown's anvil court (B09)
	&"ch05_stair_tortoises": &"ashcrown_forecourt_day",
	&"ch08_stair_hold_1": &"seawall_stairhead_storm",
	&"ch08_stair_hold_2": &"seawall_stairhead_hoist",
	&"undertows_reach": &"seawall_stairhead_surge",
	&"ch08_headland_gulls": &"coilspire_headland_path",
	&"ch08_flue_moths": &"coilspire_tier_landing",
}
const ACT_ONE_PREFIXES: Array[String] = ["ch01_", "ch03_", "ch04_", "ch05_", "ch08_"]
## M3-BPR-03: Ch6 (act1_ch06.md B01, B04).
const CH06 := {
	&"ch06_ridge_skippers": &"brine_shoals_afternoon",
	&"ch06_ridge_crab": &"brine_shoals_afternoon",
	&"ch06_ridge_gulls": &"brine_shoals_afternoon",
	&"ch06_flats_crabs": &"brine_shoals_afternoon",
	&"ch06_inquisitor": &"salvage_camp_burning",
}

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


## M3-BPR-01: every arena scene loads and keeps the contract (a WorldEnvironment, a DirectionalLight3D Sun, and its
## sea an ArenaSea named Sea: env-art's battle_arenas.md rule 6; the Underway's is the surface overhead, the terrace's
## the sea far below). arenas.json points at env-art's kit scenes since the big8 merge.
func test_every_arena_scene_keeps_the_contract() -> void:
	var scenes := BattleArena.data().get("scenes", {}) as Dictionary
	assert_true(scenes.size() >= 9, "the two slice arenas, the five Act I ones and the two Ch6 ones")
	for id: String in scenes:
		var path := BattleArena.scene_of(id)
		assert_true(ResourceLoader.exists(path), "%s: %s exists" % [id, path])
		var arena := (load(path) as PackedScene).instantiate()
		assert_true(arena.get_node_or_null(^"WorldEnvironment") is WorldEnvironment, "%s has a WorldEnvironment" % id)
		assert_true(arena.get_node_or_null(^"Sun") is DirectionalLight3D, "%s has a Sun" % id)
		var sea := arena.get_node_or_null(^"Sea")
		if path.begins_with("res://assets/environments/arenas/"):  # env-art's kit arenas; the Ch6 ones are greybox yet
			assert_true(sea == null or sea is ArenaSea, "%s: its Sea is an ArenaSea" % id)
		else:
			assert_true(sea != null, "%s: a greybox arena keeps a Sea for the flood rig" % id)
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


## M3-BPR-03: the Ch6 encounters fight on the Brine Shoals and at the burning camp; the camp's fire lights come
## with it, steady (no volumetric-fog banding), and the silted sea is there.
func test_ch06_encounters_have_arenas() -> void:
	var db := BattleDB.load_default()
	for enc: StringName in CH06:
		assert_eq(BattleArena.scene_for(db, enc), BattleArena.scene_of(String(CH06[enc])), "%s's arena" % enc)
	for key: Variant in db.encounters:
		if String(key).begins_with("ch06_"):
			assert_ne(BattleArena.scene_for(db, key as StringName), "", "%s fights in an arena" % key)
	var empty: Array[StringName] = []
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], empty, &"ch06_inquisitor", 7)
	assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), BattleArena.scene_of("salvage_camp_burning"))
	var fire := ctl.get_node_or_null(^"Arena/FireLight0") as OmniLight3D
	assert_true(fire != null, "the camp's fire light came with the arena")
	assert_eq(fire.light_volumetric_fog_energy, 0.0, "no fog banding")
	assert_true(ctl.get_node_or_null(^"Arena/Sea") != null, "the silted flats' water")
	_free()


func test_the_underwater_arena_applies() -> void:
	var empty: Array[StringName] = []
	ctl.start_battle(PARTY, empty, &"ch01_wickfry", 7)
	assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), BattleArena.scene_of("underway_tower"))
	assert_true(ctl.get_node_or_null(^"Arena/Lantern") != null, "the lantern came with the arena")
	assert_true(ctl.get_node_or_null(^"Arena/Underwater") is ArenaUnderwater, "and its underwater look")
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
	assert_true(ctl.get_node_or_null(^"Arena/CameraHints") != null, "the arena's other children are under Arena")
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
