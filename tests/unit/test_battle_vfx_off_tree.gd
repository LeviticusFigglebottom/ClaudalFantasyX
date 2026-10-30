extends TestCase
## ui-menus' headless error sweep (10-29): BattleVfx and BattleBossVfx read global transforms of nodes that had left
## the tree (a hit resolved, or a deferred polyp light placed, as the fight was leaving), and every one pushed an
## engine error. Off the tree they now place nothing and read nothing.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"


func _start(encounter: StringName) -> BattleController:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.set_meta(BattleBossIntro.META_PLAYED, String(encounter))
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], encounter, 20261029)
	return ctl


func test_a_hit_off_the_tree_places_nothing() -> void:
	var ctl := _start(&"sandbox_reef")
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	var foe := ctl.engine.enemies[0].id
	assert_true(vfx.play(&"hit_none", foe) != null, "on the tree the hit plays")
	ctl.get_parent().remove_child(ctl)
	vfx.played.clear()
	assert_eq(vfx.play(&"hit_none", foe), null, "off the tree: nothing to place")
	assert_eq(vfx.play_at(&"hit_none", Vector3.ZERO), null)
	assert_eq(vfx.anchor(foe, "chest"), Vector3.ZERO, "and no global position is read")
	assert_eq(vfx.entry_mark(foe), Vector3.INF)
	assert_true(vfx.played.is_empty())
	ctl.free()


func test_a_deferred_polyp_light_waits_for_the_tree() -> void:
	var ctl := _start(&"drownbell")
	var boss := ctl.stage.get_node_or_null(^"BattleVfx/BattleBossVfx") as BattleBossVfx
	if boss == null:
		for n in ctl.find_children("*", "BattleBossVfx", true, false):
			boss = n as BattleBossVfx
	assert_true(boss != null, "the Drownbell's fight has its set piece")
	var l := OmniLight3D.new()
	boss.polyp_lights[&"probe"] = l  # a light whose node never joined the tree
	boss._place_polyp_light(&"probe")
	assert_eq(l.position, Vector3.ZERO, "a light off the tree is left where it is")
	boss.polyp_lights.erase(&"probe")
	l.free()
	ctl.get_parent().remove_child(ctl)
	ctl.free()
