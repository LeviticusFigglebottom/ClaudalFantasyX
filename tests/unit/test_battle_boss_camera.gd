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


func test_a_colossus_fight_rests_farther_back() -> void:
	# M3-BPR-425 (GPU QA row 36): the Reach's arm filled most of the frame and passed over the party all fight. Its
	# fight rests farther back and higher, the whole party inside the safe frame; another fight keeps the authored rest.
	var frames: Dictionary = {}
	for enc: StringName in [&"undertows_reach", &"ch05_cinder_matron"]:
		ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
		ctl.auto_start = false
		ctl.pacing_scale = 0.0
		ctl.persist_progress = false
		var tree := Engine.get_main_loop() as SceneTree
		(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
		ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], enc, 20261028)
		var d := ctl.stage.choreo.camera
		var authored := ctl.stage.camera.get_meta(BattleCameraDirector.META_DEFAULT) as Transform3D
		frames[enc] = d.default_transform.origin.distance_to(authored.origin)
		if enc == &"undertows_reach":
			var xf := d.default_transform
			for c in ctl.engine.party_active:
				var f := ctl.stage.stand_in(c.id)
				for frac: float in [0.0, 1.0]:
					var p := (
						d._parent_inverse() * (f.global_position + Vector3.UP * float(f.spec.get("height", 1.7)) * frac)
					)
					assert_true(
						d.in_frame(xf, d.default_fov, p, d.data["safe_frame"]), "%s inside the safe frame" % c.id
					)
		ctl.get_parent().remove_child(ctl)
		ctl.free()
	assert_true(float(frames[&"undertows_reach"]) > 2.0, "the Reach's fight rests farther back")
	assert_eq(float(frames[&"ch05_cinder_matron"]), 0.0, "a fight with no row keeps the authored rest")


## The big17 gate's dry drownbell_flood: the Flood's phase moment framed the bell from its waterline, the risen water
## edge-on and invisible. A camera moment's lens stays camera.water_clear_m above the flood's target height.
func test_the_floods_phase_moment_stays_above_the_water() -> void:
	var ctl := (load("res://game/battle/scene/battle_sandbox.tscn") as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.pacing_scale = 1.0
	ctl.set_meta(BattleBossIntro.META_PLAYED, "drownbell")
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], &"drownbell", 20261023)
	ctl.stage.choreo.force_play = true
	ctl.stage.choreo.reduced_motion = false
	ctl.stage.choreo.skip = false
	var bell := ctl.engine.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(ctl.engine)
	var dir := ctl.stage.choreo.camera
	var boss := (ctl.stage.get_node(^"BattleVfx") as BattleVfx).boss
	assert_true(dir.moment_left() > 0.0, "the Flood plays its phase moment")
	var lens: Vector3 = (dir._above_water(dir._moment["pose"] as Dictionary))["pos"]
	var water := (dir._parent_inverse() * Vector3(0.0, boss.flood_target_m, 0.0)).y
	var clear := float(BattleChoreo.load_data()["camera"]["water_clear_m"])
	assert_true(lens.y >= water + clear - 0.001, "the lens %.2f m clears the flood's %.2f m" % [lens.y, water])
	dir.advance_moment(float(dir._moment["in"]) + 0.1)
	assert_true(ctl.stage.camera.position.y >= water + clear - 0.001, "and the camera does, held on the bell")
	ctl.get_parent().remove_child(ctl)
	ctl.free()
