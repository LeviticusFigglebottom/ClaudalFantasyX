extends TestCase
## M2-BPR-03: the battle camera director. Its data names every shot it uses and covers every choreography style; a
## party melee frames the actor then the target and is back on the default by the sequence end (before the next
## command menu); targets never leave the screen and the camera never rolls; reduced motion and skip animations
## never move it; the same choreography time gives the same frame; the shake's h_offset composes on top.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const EPS := 0.001
const SAMPLES := 24

var ctl: BattleController
var choreo: BattleChoreo
var director: BattleCameraDirector


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED, p)
	choreo = ctl.stage.choreo
	choreo.live = false
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0
	director = choreo.camera


# --- data -----------------------------------------------------------------------------------


func test_data_defines_every_shot_it_uses() -> void:
	var cam := BattleChoreo.load_data()["camera"] as Dictionary
	var shots := cam["shots"] as Dictionary
	for id in ["default", "actor", "target", "cast", "finisher"]:
		assert_true(shots.has(id), "the %s shot is defined" % id)
	for id: String in shots:
		var anchor := str((shots[id] as Dictionary)["anchor"])
		assert_true(BattleCameraDirector.ANCHORS.has(anchor), "%s anchor '%s'" % [id, anchor])
	var by_style := cam["by_style"] as Dictionary
	for sid: String in BattleChoreo.load_data()["styles"]:
		assert_true(by_style.has(sid), "style %s has camera shots" % sid)
	var pairs: Array = by_style.values()
	pairs.append(cam["enemy"])
	for pair: Dictionary in pairs:
		for slot in [BattleCameraDirector.LEAD, BattleCameraDirector.CONTACT]:
			var id := str(pair[slot])
			assert_true(id == "" or shots.has(id), "shot '%s' is defined" % id)
	_free()


func test_attaches_on_the_authored_default() -> void:
	assert_true(director != null, "BattleChoreo.attached builds the director")
	assert_true(director.at_default(), "the camera starts on its authored frame")
	var shot := director.shot_pose("default", Vector3.ZERO, Vector3.ZERO, Vector3.LEFT)
	assert_true((shot["pos"] as Vector3).distance_to(director.default_transform.origin) < EPS, "the default shot")
	_free()


# --- a party action -------------------------------------------------------------------------


func test_a_party_melee_frames_the_actor_then_the_target_then_the_default() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foe := _foe()
	ctl.act(&"attack", [foe])
	var plan := choreo.current()
	assert_eq(director.shot_ids, {"lead": "actor", "contact": "target"})
	var from: Vector3 = plan["from"]
	var to: Vector3 = plan["to"]
	var aim: Vector3 = plan["aim"]
	assert_true(director.at_default(), "the sequence starts on the default")
	choreo.seek(director._in_end)
	var lead := director.shot_pose("actor", from, to, aim)
	_assert_eq_v(ctl.stage.camera.position, lead["pos"] as Vector3, "framed on the actor")
	assert_false(director.at_default())
	var behind := (ctl.stage.camera.position - from).dot(director.axis())
	assert_true(behind < 0.0, "behind the actor, looking toward the foes")
	choreo.seek(float(plan["contact"]))
	var hit := director.shot_pose("target", from, to, aim)
	_assert_eq_v(ctl.stage.camera.position, hit["pos"] as Vector3, "framed on the target at contact")
	choreo.seek(float(plan["total"]) - EPS)
	var near_end := ctl.stage.camera.position.distance_to(director.default_transform.origin)
	assert_true(near_end < 0.05, "nearly home just before the end (%.3f m)" % near_end)
	choreo.seek(float(plan["total"]))
	assert_true(director.at_default(), "exactly the default on the sequence end")
	choreo.advance(1.0)
	assert_false(choreo.playing())
	assert_true(director.at_default(), "still the default after the sequence")
	_free()


func test_the_default_is_back_before_the_next_command_menu() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	choreo.seek(float(choreo.current()["contact"]))
	assert_false(director.at_default())
	var hold := ctl.stage.hold_after(0.0)
	choreo.advance(choreo.remaining_sec())
	assert_true(director.at_default(), "home when the sequence ends")
	ctl.tick(hold + EPS)
	assert_true(director.at_default(), "and when the controller hands the turn on")
	_free()


func test_targets_stay_on_screen_and_the_camera_never_rolls() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var cam := ctl.stage.camera
	var to_stage := director._parent_inverse()
	var whole := {}  # the whole screen; the shots themselves keep to the safe frame
	for skill: StringName in [&"attack", &"lamp_dive", &"ember"]:
		for e in ctl.engine.enemies:
			var r := _attack(e.id)
			r.skill_id = skill
			choreo._on_action_resolved(r)
			var plan := choreo.current()
			assert_true(str(director.shot_ids["lead"]) != "", "%s at %s is framed" % [skill, e.id])
			var target := ctl.stage.stand_in(e.id)
			for i in SAMPLES + 1:
				choreo.seek(float(plan["total"]) * i / SAMPLES)
				var at := "%s at %s, sample %d" % [skill, e.id, i]
				assert_true(absf(cam.global_basis.x.y) < EPS, "no roll: " + at)
				for p: Vector3 in [target.global_position, target.head_position()]:
					assert_true(director.in_frame(cam.transform, cam.fov, to_stage * p, whole), "in view: " + at)
			choreo.finish()
	_free()


func test_a_finisher_and_a_cast_use_their_own_lead_shots() -> void:
	var foe := _foe()
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var by_style := (BattleChoreo.load_data()["camera"] as Dictionary)["by_style"] as Dictionary
	for skill: StringName in [&"lamp_dive", &"ember"]:
		var r := _attack(foe)
		r.skill_id = skill
		choreo._on_action_resolved(r)
		var style := str(choreo.current()["style"])
		assert_eq(director.shot_ids["lead"], str((by_style[style] as Dictionary)["lead"]), "%s lead" % style)
		choreo.finish()
		assert_true(director.at_default(), "%s ends on the default" % style)
	_free()


# --- an enemy action ------------------------------------------------------------------------


func test_an_enemy_action_pushes_gently_and_comes_back() -> void:
	ctl.pacing_scale = 1.0
	var guard := 0
	while guard < 80 and not (choreo.playing() and not _is_party(StringName(str(choreo.current()["actor"])))):
		guard += 1
		if choreo.playing():
			choreo.finish()
		elif ctl.engine.is_party_turn() and not ctl.is_waiting():
			ctl.act(&"attack", [_foe()])
		else:
			ctl.tick(0.5)
	assert_true(choreo.playing(), "an enemy's action plays")
	var enemy := (BattleChoreo.load_data()["camera"] as Dictionary)["enemy"] as Dictionary
	assert_eq(director.shot_ids["lead"], str(enemy["lead"]))
	var plan := choreo.current()
	choreo.seek(float(plan["contact"]))
	var moved := ctl.stage.camera.position.distance_to(director.default_transform.origin)
	assert_true(moved > EPS, "it moves")
	assert_true(moved < 2.0, "only a gentle push (%.2f m)" % moved)
	choreo.finish()
	assert_true(director.at_default())
	_free()


# --- accessibility --------------------------------------------------------------------------


func test_reduced_motion_never_moves_the_camera() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	choreo.reduced_motion = true
	ctl.act(&"attack", [_foe()])
	assert_true(choreo.playing(), "the sequence still plays")
	_assert_still_through(choreo.current())
	_free()


func test_skip_animations_never_moves_the_camera() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	choreo.skip = true
	ctl.act(&"attack", [_foe()])
	assert_false(choreo.playing())
	assert_true(director.at_default())
	choreo.force_play = true  # even a forced sequence keeps the camera still under skip
	choreo._on_action_resolved(_attack(_foe()))
	assert_true(choreo.playing(), "a forced sequence plays")
	_assert_still_through(choreo.current())
	_free()


func test_the_battle_settings_rows_drive_speed_and_skip() -> void:
	var s := UiSettings.new()
	assert_eq(s.default_value(BattleChoreo.SETTING_SPEED), 1.0)
	assert_eq(s.options(BattleChoreo.SETTING_SPEED), [0.75, 1.0, 1.5, 2.0])
	assert_eq(s.options(BattleChoreo.SETTING_ANIMATIONS), ["full", "skip"])
	assert_true(s.set_value(BattleChoreo.SETTING_SPEED, 1.5))
	assert_true(s.set_value(BattleChoreo.SETTING_ANIMATIONS, "skip"))
	choreo._read_settings(s)
	assert_eq(choreo.speed, 1.5)
	assert_true(choreo.skip)
	assert_true(director.still())
	_free()


# --- determinism ----------------------------------------------------------------------------


func test_the_same_choreo_time_gives_the_same_frame() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	var plan := choreo.current()
	var t := float(plan["contact"]) * 0.7
	choreo.seek(t)
	var first := ctl.stage.camera.transform
	var fov := ctl.stage.camera.fov
	choreo.seek(float(plan["total"]) * 0.9)
	choreo.seek(t)
	assert_true(ctl.stage.camera.transform.is_equal_approx(first), "seek back: the same frame")
	assert_eq(ctl.stage.camera.fov, fov)
	var frame := director.frame_at(t)
	assert_true((frame["transform"] as Transform3D).is_equal_approx(first), "frame_at is the pure function")
	choreo.seek(0.0)
	choreo.set_speed(2.0)
	choreo.advance(t / 2.0)
	assert_between(choreo.time(), t - EPS, t + EPS)
	assert_true(ctl.stage.camera.transform.is_equal_approx(first), "the battle speed changes only the pace")
	_free()


func test_the_shake_composes_on_top() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	ctl.stage.camera.h_offset = 0.05
	choreo.seek(float(choreo.current()["contact"]))
	assert_between(ctl.stage.camera.h_offset, 0.05 - EPS, 0.05 + EPS, "the director leaves h_offset to the shake")
	ctl.stage.camera.h_offset = 0.0
	_free()


func test_a_shot_that_would_lose_a_target_falls_back_to_the_default() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	director.data = director.data.duplicate(true)
	director.data["safe_frame"] = {"left": 0.49, "right": 0.49, "top": 0.49, "bottom": 0.49}
	ctl.act(&"attack", [_foe()])
	assert_eq(director.shot_ids, {"lead": "", "contact": ""}, "no shot keeps the target in so small a frame")
	_assert_still_through(choreo.current())
	var behind := Transform3D(Basis.IDENTITY, Vector3.ZERO)
	assert_false(director.in_frame(behind, 40.0, Vector3(0.0, 0.0, 5.0), {}), "a point behind is out")
	assert_true(director.in_frame(behind, 40.0, Vector3(0.0, 0.0, -5.0), {}), "a point ahead is in")
	_free()


# --- helpers --------------------------------------------------------------------------------


func _assert_still_through(plan: Dictionary) -> void:
	for i in SAMPLES + 1:
		choreo.seek(float(plan["total"]) * i / SAMPLES)
		if not director.at_default():
			assert_true(false, "the camera moved at sample %d" % i)
			return
	assert_true(director.at_default(), "the camera never left the default")


func _attack(foe: StringName) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = &"rhen"
	r.skill_id = &"attack"
	r.hits = [{"target_id": foe, "hit": true, "crit": false, "amount": 1, "statuses_added": []}]
	return r


func _is_party(cid: StringName) -> bool:
	var c := ctl.engine.find(cid)
	return c != null and c.team == BattleCombatant.TEAM_PARTY


## The encounter sweep (10-29): Toma's shield on his mark hid the Reef Crab from Rhen's Lamp Dive. A bystander (an
## ally or another foe, neither actor nor target) across the sight line to the target's middle drops that shot.
func test_a_bystander_across_the_sight_line_keeps_the_default() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foe := _foe()
	ctl.act(&"attack", [foe])
	var plan := choreo.current()
	assert_eq(director.shot_ids["contact"], "target", "clear: the contact shot frames the target")
	var hit := director.shot_pose("target", plan["from"], plan["to"], plan["aim"])
	var mid: Vector3 = director._target_mids(plan, &"rhen")[0]
	var asha := ctl.stage.stand_in(&"asha")
	var inv := director._parent_inverse()
	var across := (hit["pos"] as Vector3).lerp(mid, 0.5)
	asha.global_position = inv.affine_inverse() * (across - Vector3.UP * 0.9)  # her middle on the sight line
	assert_false(director._bystander_boxes(&"rhen", plan["targets"]).is_empty(), "Asha is a bystander")
	director._setup(plan)
	assert_eq(director.shot_ids["contact"], "", "Asha across the line: the contact keeps the default frame")
	_free()


func _foe() -> StringName:
	for e in ctl.engine.enemies:
		if e.is_alive():
			return e.id
	return &""


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _assert_eq_v(a: Vector3, b: Vector3, msg: String) -> void:
	assert_true(a.distance_to(b) < EPS, "%s (%s vs %s)" % [msg, a, b])


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
