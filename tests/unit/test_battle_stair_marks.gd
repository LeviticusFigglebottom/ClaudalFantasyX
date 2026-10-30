extends TestCase
## M3-BPR-1325 (env-art-b's Fisher Stair marks): the Climb (a set piece entry, no fighter) anchors on the arena's
## StairHead_ward, so effects aimed at the stair land on its head, not mid-field; its turn cuts to the stair hint.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func _start() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.set_meta(BattleBossIntro.META_PLAYED, "ch08_stair_hold_1")
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], &"ch08_stair_hold_1", 20261028)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func _climb() -> BattleCombatant:
	for c in ctl.engine.entries:
		if c.entry_role == &"ward":
			return c
	return null


func test_the_climb_anchors_on_the_stair_head() -> void:
	_start()
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	var climb := _climb()
	assert_true(climb != null, "the stair hold has its Climb")
	var head := ctl.get_node(^"Arena/StairHead_ward") as Node3D
	var at := vfx.anchor(climb.id, "feet")
	var flat := Vector2(at.x - head.global_position.x, at.z - head.global_position.z)
	assert_true(flat.length() < 0.01, "the Climb stands on the stair head")
	assert_true(absf(at.y - head.global_position.y) < 0.2, "at its feet (anchor_heights.feet over the mark)")
	vfx.played.clear()
	var r := ActionResult.new()
	r.actor_id = ctl.engine.enemies[0].id
	r.skill_id = &"grip_the_stair"
	r.hits = [{"target_id": climb.id, "hit": true, "amount": 0}]
	assert_true(vfx.effects_for(r).any(func(e: Dictionary) -> bool: return e["effect"] == &"grip_the_stair"))
	_free()


func test_the_climbs_turn_cuts_to_the_stair() -> void:
	_start()
	var choreo := ctl.stage.choreo
	choreo.force_play = true
	choreo.reduced_motion = false
	choreo.skip = false
	var cam := choreo.get_node(^"BattleEntryCamera") as BattleEntryCamera
	assert_true(cam != null, "a set piece fight has the entry camera")
	assert_false(cam.hint_pose(&"ward").is_empty(), "the arena carries the stair hint")
	var r := ActionResult.new()
	r.actor_id = _climb().id
	r.skill_id = &"climb_up"
	choreo.contact.emit(r)
	assert_eq(cam.cut_for, [_climb().id] as Array[StringName], "the Climb's turn shows the stair")
	assert_true(choreo.busy_sec() > 0.0, "the next turn waits for it")
	choreo.advance(10.0)
	assert_true(choreo.camera.at_default(), "and comes home")
	_free()


func test_instant_pacing_cuts_nowhere() -> void:
	_start()
	var cam := ctl.stage.choreo.get_node(^"BattleEntryCamera") as BattleEntryCamera
	var r := ActionResult.new()
	r.actor_id = _climb().id
	r.skill_id = &"climb_up"
	ctl.stage.choreo.contact.emit(r)
	assert_true(cam.cut_for.is_empty())
	_free()
