extends TestCase
## M3-BPR-418: the greybox Act II boss arenas (tools/arenas/gen_act2_arenas.py) load, carry their chapter's grade
## (a WorldEnvironment and the key, fill and rim lights, none adding volumetric fog energy: the Lead's rule), and drop
## into a battle by id (BattleArena.apply_scene) the way an encounter's arena does.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const IDS: Array[String] = ["fen_roots_dusk", "lowlight_engine_hall", "keth_terrace_wall", "night_sea_barge"]


func test_each_arena_loads_with_its_grade_and_quiet_lights() -> void:
	for aid in IDS:
		var path := BattleArena.scene_of(aid)
		assert_ne(path, "", "%s is in arenas.json" % aid)
		var root := (load(path) as PackedScene).instantiate()
		for name: String in ["WorldEnvironment", "Sun", "Fill", "Rim"]:
			assert_true(root.has_node(NodePath(name)), "%s has its %s" % [aid, name])
		for n in root.find_children("*", "Light3D", true, false):
			assert_eq((n as Light3D).light_volumetric_fog_energy, 0.0, "%s %s adds no fog energy" % [aid, n.name])
		root.free()


func test_an_arena_by_id_drops_into_a_battle() -> void:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha"] as Array[StringName], [], &"sandbox_reef", 20261027)
	for aid in IDS:
		var path := BattleArena.scene_of(aid)
		assert_eq(BattleArena.apply_scene(ctl, path), path, "%s applied" % aid)
		assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), path, "%s is the battle's arena" % aid)
		assert_true(ctl.has_node(NodePath(String(BattleArena.ARENA_NODE))), "%s's dressing is in" % aid)
	ctl.get_parent().remove_child(ctl)
	ctl.free()
