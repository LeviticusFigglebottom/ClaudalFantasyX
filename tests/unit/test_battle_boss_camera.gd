extends TestCase
## M3-BPR-420 (ADR 0041): each Act I boss's big moves get a shot (camera.enemy_by_skill), not the foes' default push:
## a heavy blow frames the boss at its strike point, then the hero it hits; a move on the whole party frames the boss
## from its mark. Checked live in each boss's own fight and arena. The Reach keeps the default frame (choreo.json doc).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const FIGHTS := {
	&"ch01_hullgnaw": [&"hullgnaw", [&"gnaw", &"thrash"]],
	&"ch04_spar_wraith": [&"spar_wraith", [&"haul", &"sea_lash", &"shroud_sweep"]],
	&"ch05_cinder_matron": [&"cinder_matron", [&"ladle_swing", &"slag_pour"]],
	&"ch06_inquisitor": [&"stillguard_inquisitor", [&"brine_iron", &"torch_hulk"]],
	&"drownbell": [&"drownbell", [&"hood_slam"]],
}

var ctl: BattleController


func test_each_boss_big_move_gets_its_shot() -> void:
	var by_skill := BattleChoreo.load_data()["camera"]["enemy_by_skill"] as Dictionary
	for enc: StringName in FIGHTS:
		ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
		ctl.auto_start = false
		ctl.pacing_scale = 0.0
		ctl.persist_progress = false
		var tree := Engine.get_main_loop() as SceneTree
		(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
		ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], enc, 20261028)
		var choreo := ctl.stage.choreo
		var boss: BattleCombatant = null
		for e in ctl.engine.enemies:
			if String(e.id).get_slice("#", 0) == String(FIGHTS[enc][0]):
				boss = e
		for sid: StringName in FIGHTS[enc][1]:
			var r := ActionResult.new()
			r.actor_id = boss.id
			r.skill_id = sid
			var hero := ctl.engine.party_active[0].id
			r.hits = [{"target_id": hero, "hit": true, "crit": false, "amount": 10, "statuses_added": []}]
			ctl.pacing_scale = 1.0
			choreo.force_play = true
			choreo.live = false
			choreo.frozen = true
			choreo.reduced_motion = false  # under reduced motion the camera stays still (the default frame)
			choreo.skip = false
			choreo.speed = 1.0
			ctl.engine.action_resolved.emit(r)
			choreo.seek(0.05)  # posed: the director frames it
			var want := by_skill[String(sid)] as Dictionary
			assert_eq(
				choreo.camera.shot_ids[BattleCameraDirector.LEAD],
				str(want["lead"]),
				"%s %s: its lead shot" % [enc, sid]
			)
		ctl.get_parent().remove_child(ctl)
		ctl.free()


func test_a_body_across_the_sight_line_drops_the_shot() -> void:
	# The self-rendered Reach: from behind its lunge a placed shot saw only its arm. A target point inside the body's
	# bounds says nothing (a colossus's rest bounds take in the party under its hand).
	var pose := {"pos": Vector3(0.0, 1.0, 10.0), "look": Vector3.ZERO, "fov": 50.0}
	var body := AABB(Vector3(-1.0, 0.0, 4.0), Vector3(2.0, 3.0, 2.0))
	var behind: Array[Vector3] = [Vector3(0.0, 1.0, 0.0)]
	assert_true(BattleCameraDirector._blocked(pose, body, behind), "a body between the lens and its target")
	var inside: Array[Vector3] = [Vector3(0.0, 1.0, 5.0)]
	assert_false(BattleCameraDirector._blocked(pose, body, inside), "a target inside the bounds never blocks")
	assert_false(BattleCameraDirector._blocked(pose, AABB(), behind), "no body, no block")
