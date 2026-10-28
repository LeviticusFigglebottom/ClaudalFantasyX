extends TestCase
## M3-BPR-426: in a boss fight the camera holds on the boss when its phase changes and when it falls, once the action
## that did it has played; the next turn waits for the moment; none under reduced motion.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func _start(enc: StringName) -> BattleChoreo:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.set_meta(BattleBossIntro.META_PLAYED, String(enc))
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], enc, 20261028)
	var choreo := ctl.stage.choreo
	choreo.force_play = true  # the battle runs at instant pacing here; a moment plays only while choreography does
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0
	return choreo


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func _boss(base: String) -> BattleCombatant:
	for e in ctl.engine.enemies:
		if String(e.id).get_slice("#", 0) == base:
			return e
	return null


func test_a_phase_change_holds_on_the_boss_then_comes_home() -> void:
	var choreo := _start(&"ch05_cinder_matron")
	var d := choreo.camera
	ctl.engine.phase_changed.emit(_boss("cinder_matron"), &"pour")
	assert_eq(d.moments_played, [&"phase"] as Array[StringName], "the phase's moment plays")
	assert_true(choreo.busy_sec() > 1.0, "the next turn waits for it")
	choreo.advance(0.8)
	assert_false(d.at_default(), "held on the boss")
	choreo.advance(5.0)
	assert_true(d.at_default(), "home again")
	assert_eq(choreo.busy_sec(), 0.0)
	_free()


func test_the_boss_falling_holds_on_it_once() -> void:
	var choreo := _start(&"ch04_spar_wraith")
	var d := choreo.camera
	var boss := _boss("spar_wraith")
	boss.hp = 0
	var r := ActionResult.new()
	r.actor_id = ctl.engine.party_active[0].id
	choreo.contact.emit(r)
	choreo.contact.emit(r)
	assert_eq(d.moments_played, [&"fall"] as Array[StringName], "the fall's moment, once")
	_free()


func test_instant_pacing_plays_no_moment() -> void:
	# test_ch08_thread: at instant pacing nothing advances a moment, so the next turn must not wait on one.
	var choreo := _start(&"ch05_cinder_matron")
	choreo.force_play = false
	ctl.engine.phase_changed.emit(_boss("cinder_matron"), &"pour")
	assert_true(choreo.camera.moments_played.is_empty())
	assert_eq(choreo.busy_sec(), 0.0)
	_free()


func test_reduced_motion_plays_no_moment() -> void:
	var choreo := _start(&"ch05_cinder_matron")
	choreo.reduced_motion = true
	ctl.engine.phase_changed.emit(_boss("cinder_matron"), &"pour")
	assert_true(choreo.camera.moments_played.is_empty())
	assert_eq(choreo.busy_sec(), 0.0)
	_free()
