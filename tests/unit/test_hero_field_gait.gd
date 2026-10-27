extends TestCase
## M2-HER-1107: the field body's gait clips (HeroGaitClips over HeroFieldActor's blend) on M2-CHR-12's
## starts, stops, turns in place and idle variant. The state machine runs on an injected locomotion table
## (FIXTURE), so these pass with or without the characters track's clips; the body tests at the end check
## whichever the model has: the clips when it has them, the plain blend and eased spin when it does not.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const EPS := 0.0005
const FPS := 10.0
const WALK := 1.0
const RUN := 3.0
const RUN_INTENT := 3.4
const FIXTURE := {
	"walk": {"speed_mps": 0.9},
	"run": {"speed_mps": 2.8},
	"walk_start": {"length_s": 0.4, "root_travel_m": [0.0, 0.02, 0.07, 0.14, 0.22]},
	"run_start": {"length_s": 0.6, "root_travel_m": [0.0, 0.0, 0.05, 0.15, 0.35, 0.6, 0.9]},
	"walk_stop": {"length_s": 0.4, "root_travel_m": [0.0, 0.1, 0.18, 0.24, 0.27]},
	"run_stop": {"length_s": 0.5, "root_travel_m": [0.0, 0.2, 0.36, 0.47, 0.53, 0.55]},
	"turn_in_place_l90": {"length_s": 0.6, "root_yaw_deg": [0.0, 5.0, 20.0, 45.0, 70.0, 85.0, 90.0]},
	"turn_in_place_r90": {"length_s": 0.6, "root_yaw_deg": [0.0, -5.0, -20.0, -45.0, -70.0, -85.0, -90.0]},
	"turn_in_place_180":
	{"length_s": 0.9, "root_yaw_deg": [0.0, 5.0, 20.0, 50.0, 90.0, 130.0, 160.0, 175.0, 180.0, 180.0]},
	"idle_shift": {"length_s": 1.0, "loop": true},
}

var zone: Node3D
var player: FieldController
var _party_was: Array[StringName] = []
var _allowed: Array[StringName] = []


## A gait on FIXTURE whose model has `clips` (every FIXTURE clip when empty), rested and still.
func _gait(clips: Array[StringName] = [], id: StringName = &"rhen") -> HeroGaitClips:
	_allowed = clips.duplicate()
	if _allowed.is_empty():
		for k: String in FIXTURE.keys():
			_allowed.append(StringName(k))
	var cfg := HeroFieldActor.field_data()["gait_clips"] as Dictionary
	var g := HeroGaitClips.new(cfg, FIXTURE, _has, FPS, WALK, RUN, id)
	g.reset()
	return g


func _has(clip: StringName) -> bool:
	return clip in _allowed


## `n` frames at `speed` (travelling speed * DT a frame) with the rest of step()'s inputs.
func _run(g: HeroGaitClips, n: int, speed: float, intent: float = -1.0, facing: float = 0.0) -> void:
	for i in n:
		g.step(0.0, speed, speed * DT, 0.0, facing, intent, -1.0, DT)


func _cfg(key: String) -> float:
	return float((HeroFieldActor.field_data()["gait_clips"] as Dictionary)[key])


func test_speeds_come_from_locomotion_json_when_it_has_them() -> void:
	var with := HeroFieldActor.gait_speeds_from(&"rhen", FIXTURE)
	assert_eq(str(with["source"]), "locomotion")
	assert_between(float(with["walk_clip_mps"]), 0.9 - EPS, 0.9 + EPS, "walk from locomotion.json")
	assert_between(float(with["run_clip_mps"]), 2.8 - EPS, 2.8 + EPS, "run from locomotion.json")
	var without := HeroFieldActor.gait_speeds_from(&"rhen", {})
	var row := (HeroFieldActor.field_data()["heroes"] as Dictionary)["rhen"] as Dictionary
	assert_eq(str(without["source"]), "hero_motion")
	assert_eq(float(without["walk_clip_mps"]), float(row["walk_clip_mps"]), "else hero_motion.json")
	assert_eq(float(without["run_clip_mps"]), float(row["run_clip_mps"]))
	var cfg := HeroFieldActor.field_data()["gait_measure"] as Dictionary
	var ball := cfg["planted_ball"] as Dictionary
	var used := HeroFieldActor.measure_config(&"rhen")
	var new_clips := str(HeroFieldActor.gait_speeds(&"rhen")["source"]) == "locomotion"
	assert_eq(used["bones"], ball["bones"] if new_clips else cfg["bones"], "the measure follows the clip set")
	assert_true(HeroFieldActor.gait_speeds(&"rhen")["walk_clip_mps"] > 0.0)
	_done_pure()


func test_a_start_from_rest_picks_walk_or_run_by_the_target_speed() -> void:
	var g := _gait()
	_run(g, 1, 0.3, WALK)
	assert_eq(g.clip, &"walk_start", "a walk target walks off")
	g = _gait()
	_run(g, 1, 0.3, RUN_INTENT)
	assert_eq(g.clip, &"run_start", "a run target runs off")
	g = _gait()
	_run(g, 1, 0.3)
	assert_eq(g.clip, &"walk_start", "a source that cannot tell walks off")
	_run(g, 1, WALK * _cfg("run_pick_ratio") + 0.2)
	assert_eq(g.clip, &"run_start", "and switches to the run start while it is still early")
	g = _gait()
	g.step(0.0, 0.3, 0.3 * DT, PI * 0.5, 0.0, WALK, -1.0, DT)
	assert_eq(g.clip, &"", "no start when travelling off to the side (the travel turn takes it)")
	_done_pure()


func test_starts_need_a_rest_so_stop_start_jitter_does_not_restart_them() -> void:
	var g := _gait()
	_run(g, 60, WALK, WALK)
	_run(g, 3, 0.0, 0.0)
	assert_true(g.still_sec < _cfg("min_still_sec"), "only just still")
	_run(g, 1, 0.3, WALK)
	assert_ne(g.clip, &"walk_start", "a re-press before min_still_sec does not restart the start")
	_run(g, 30, WALK, WALK)
	_run(g, int(ceil(_cfg("min_still_sec") / DT)) + 30, 0.0, -1.0)
	_run(g, 1, 0.3, WALK)
	assert_eq(g.clip, &"walk_start", "after a rest it does")
	_done_pure()


func test_a_start_plays_by_the_ground_covered_and_hands_back_at_its_end() -> void:
	var g := _gait()
	var keys := (FIXTURE["walk_start"] as Dictionary)["root_travel_m"] as Array
	var speed := 0.5
	var travel := 0.0
	var ended := false
	for i in 120:
		_run(g, 1, speed, WALK)
		travel += speed * DT
		if g.clip == &"":
			ended = true
			break
		assert_true(g.clip_time <= HeroGaitClips.time_at(keys, FPS, travel) + EPS, "never ahead of the ground")
		assert_true(g.clip_time <= 0.4 + EPS, "never past its end")
		if i >= 10:
			assert_between(g.clip_time, HeroGaitClips.time_at(keys, FPS, travel) - 0.002, 0.4 + EPS, "on it")
	assert_true(ended, "it handed back to the blend")
	assert_true(travel >= 0.22 - speed * DT * 2.0, "once its travel was covered (%.3f m)" % travel)
	_done_pure()


func test_stops_pick_walk_or_run_play_once_and_give_way_to_a_restart() -> void:
	var g := _gait()
	_run(g, 60, RUN, RUN_INTENT)
	g.step(0.0, RUN, RUN * DT, 0.0, 0.0, 0.0, 0.3, DT)
	assert_eq(g.clip, &"run_stop", "letting go of a run")
	var keys := (FIXTURE["run_stop"] as Dictionary)["root_travel_m"] as Array
	assert_between(g.clip_time, HeroGaitClips.time_at(keys, FPS, 0.55 - 0.3) - EPS, 1.0, "entered where 0.3 m is left")
	_run(g, 6, 1.0, 0.0)
	_run(g, 60, 0.05, -1.0)
	assert_eq(g.clip, &"", "it finished")
	assert_eq(g.phase, HeroGaitClips.Phase.BLEND)
	g = _gait()
	_run(g, 60, WALK, WALK)
	_run(g, 1, WALK, 0.0)
	assert_eq(g.clip, &"walk_stop", "letting go of a walk")
	_run(g, 1, WALK, WALK)
	assert_eq(g.clip, &"", "pressing again gives way at once")
	_run(g, 3, 0.4, 0.0)
	assert_eq(g.clip, &"", "one stop per run of motion: no stop-start churn")
	g = _gait()
	_run(g, 2, 0.3, WALK)
	_run(g, 1, 0.3, 0.0)
	assert_eq(g.clip, &"", "a tap that never got going has no stop")
	g = _gait()
	_run(g, 60, WALK, -1.0)
	_run(g, 1, WALK * _cfg("stop_unknown_ratio") - 0.05, -1.0)
	assert_eq(g.clip, &"walk_stop", "a source that cannot tell: the speed falling under the threshold")
	_done_pure()


func test_turn_in_place_picks_the_clip_by_angle() -> void:
	var g := _gait()
	assert_eq(g.turn_role(deg_to_rad(30.0)), &"", "a small turn eases")
	assert_eq(g.turn_role(deg_to_rad(70.0)), &"turn_l90")
	assert_eq(g.turn_role(deg_to_rad(-70.0)), &"turn_r90")
	assert_eq(g.turn_role(deg_to_rad(140.0)), &"turn_180")
	assert_eq(g.turn_role(deg_to_rad(-170.0)), &"turn_180")
	var no180: Array[StringName] = [&"turn_in_place_l90", &"turn_in_place_r90"]
	assert_eq(_gait(no180).turn_role(deg_to_rad(-170.0)), &"turn_r90", "no 180: the 90 scaled")
	var none: Array[StringName] = [&"walk_start"]
	assert_eq(_gait(none).turn_role(deg_to_rad(120.0)), &"", "no turn clips: none")
	_done_pure()


func test_a_turn_follows_its_curve_and_ends_on_the_target() -> void:
	for target_deg: float in [114.0, -80.0, -170.0, 150.0]:
		var g := _gait()
		var target := deg_to_rad(target_deg)
		g.step(0.0, 0.0, 0.0, 0.0, target, -1.0, -1.0, DT)
		assert_eq(g.phase, HeroGaitClips.Phase.TURN, "%.0f deg turns in place" % target_deg)
		var last := 0.0
		var prev := 0.0
		var frames := 0
		while g.phase == HeroGaitClips.Phase.TURN and frames < 240:
			last = g.turn_yaw()
			assert_true(signf(angle_difference(prev, last)) * signf(g.turn_total) >= 0.0, "it never turns back")
			prev = last
			g.step(0.0, 0.0, 0.0, 0.0, angle_difference(last, target), -1.0, -1.0, DT)
			frames += 1
		assert_between(absf(angle_difference(last, target)), 0.0, EPS, "%.0f deg: lands on the facing" % target_deg)
	_done_pure()


func test_the_idle_variant_waits_a_per_hero_time_and_plays_once() -> void:
	var a := _gait([], &"rhen")
	var b := _gait([], &"rhen")
	assert_eq(a.idle_after_sec, b.idle_after_sec, "the same hero waits the same time")
	var lo := _cfg("idle_variant_after_sec")
	assert_between(a.idle_after_sec, lo, lo + _cfg("idle_variant_spread_sec"), "within the data's window")
	var ids: Array[float] = [_gait([], &"asha").idle_after_sec, _gait([], &"toma").idle_after_sec, a.idle_after_sec]
	assert_true(ids[0] != ids[1] or ids[1] != ids[2], "heroes do not shift in unison")
	_run(a, int(a.idle_after_sec / DT) - 2, 0.0)
	assert_eq(a.clip, &"", "not yet")
	_run(a, 4, 0.0)
	assert_eq(a.clip, &"idle_shift", "then the idle variant")
	_run(a, int(1.0 / DT) + 2, 0.0)
	assert_eq(a.clip, &"", "once")
	assert_true(a.idle_sec < 0.1, "and the clock starts over")
	_run(a, 10, 0.0)
	_run(a, 1, 0.3, WALK)
	assert_eq(a.clip, &"walk_start", "moving off ends the idle")
	_done_pure()


func test_without_the_clips_nothing_plays() -> void:
	var none: Array[StringName] = [&"no_such_clip"]
	var g := _gait(none)
	_run(g, 60, 0.0)
	_run(g, 60, RUN, RUN_INTENT)
	_run(g, 30, 0.0, 0.0)
	g.step(0.0, 0.0, 0.0, 0.0, PI * 0.9, -1.0, -1.0, DT)
	_run(g, 900, 0.0)
	assert_eq(g.clip, &"", "the blend and the eased spin only")
	assert_eq(g.phase, HeroGaitClips.Phase.BLEND)
	var bare := HeroGaitClips.new(HeroFieldActor.field_data()["gait_clips"], {}, _has, FPS, WALK, RUN, &"rhen")
	assert_false(bare.has_role(&"walk_start"), "no locomotion.json: no clip (its curves are needed)")
	_done_pure()


func test_curve_lookups() -> void:
	var keys := [0.0, 0.0, 0.1, 0.3]
	assert_eq(HeroGaitClips.time_at(keys, FPS, 0.0), 0.0)
	assert_between(HeroGaitClips.time_at(keys, FPS, 0.05), 0.15 - EPS, 0.15 + EPS, "inside a key gap")
	assert_between(HeroGaitClips.time_at(keys, FPS, 9.0), 0.3 - EPS, 0.3 + EPS, "held at the end")
	assert_between(HeroGaitClips.yaw_at(keys, FPS, 0.25), 0.2 - EPS, 0.2 + EPS)
	assert_between(HeroGaitClips.yaw_at(keys, FPS, 5.0), 0.3 - EPS, 0.3 + EPS)
	_done_pure()


# --- the body on the field player: the real model's clips when it has them, else the old behaviour ---


func test_the_body_turns_in_place_under_the_cap_and_lands_on_the_facing() -> void:
	_zone()
	var body := _body()
	body.snap()
	var cap := body.loco.max_rate_rad * DT
	var target := wrapf(player.motor.facing_yaw + deg_to_rad(120.0), -PI, PI)
	player.motor.facing_yaw = target
	var prev := body.visible_yaw()
	var worst := 0.0
	var seen: Array[StringName] = []
	for i in 150:
		body.advance(DT)
		worst = maxf(worst, absf(angle_difference(prev, body.visible_yaw())))
		prev = body.visible_yaw()
		if body.gait.clip != &"" and not body.gait.clip in seen:
			seen.append(body.gait.clip)
	assert_true(worst <= cap + EPS, "worst frame %.4f rad <= cap %.4f" % [worst, cap])
	assert_between(absf(angle_difference(body.visible_yaw(), target)), 0.0, 0.01, "lands on the facing")
	if body.gait.has_role(&"turn_l90"):
		assert_eq(seen, [&"turn_in_place_l90"] as Array[StringName], "the feet step through the turn")
	else:
		assert_true(seen.is_empty(), "no turn clip on this model: the eased spin")
	_done()


func test_the_body_starts_and_stops_a_run_with_the_clips() -> void:
	_zone()
	var body := _body()
	body.snap()
	var seen: Array[StringName] = []
	for leg: Vector2 in [Vector2(0, -1), Vector2.ZERO]:
		player.input_override = leg
		for i in 90:
			player.step(DT)
			body.advance(DT)
			assert_eq(body.action, &"", "gait clips are not cutscene actions")
			if body.gait.clip != &"" and not body.gait.clip in seen:
				seen.append(body.gait.clip)
	if body.gait.has_role(&"run_start"):
		assert_eq(seen, [&"run_start", &"run_stop"] as Array[StringName], "a run starts and stops on its clips")
		assert_eq(body.loco.run_clip_mps, float(HeroFieldActor.gait_speeds(&"rhen")["run_clip_mps"]))
	else:
		assert_true(seen.is_empty(), "no start or stop clips on this model: the blend alone")
	assert_eq(body.gait.clip, &"", "back on the blend at rest")
	_done()


func test_a_cutscene_clip_holds_the_gait_and_a_locomotion_call_lets_it_finish() -> void:
	_zone()
	var body := _body()
	body.snap()
	assert_true(body.play_clip(&"talk", 0.1))
	player.input_override = Vector2(0, -1)
	for i in 30:
		player.step(DT)
		body.advance(DT)
		assert_eq(body.gait.clip, &"", "no gait clip under a cutscene clip")
	assert_true(body.play_clip(&"idle"), "back to locomotion")
	player.input_override = Vector2.ZERO
	for i in 90:
		player.step(DT)
		body.advance(DT)
	player.input_override = Vector2(0, -1)
	for i in 4:
		player.step(DT)
		body.advance(DT)
	if body.gait.has_role(&"run_start"):
		assert_eq(body.gait.clip, &"run_start", "running off from rest")
		assert_true(body.play_clip(&"walk"), "the sequencer's locomotion call")
		assert_eq(body.gait.clip, &"run_start", "lets the start finish")
	else:
		assert_eq(body.gait.clip, &"", "no clips: the blend")
	_done()


func _zone() -> void:
	_party_was = Game.state.party_ids.duplicate()
	Game.state.party_ids.clear()
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)


func _body() -> HeroFieldActor:
	var b := player.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	b.set_process(false)
	return b


func _done() -> void:
	zone.free()
	Game.state.party_ids = _party_was


func _done_pure() -> void:
	_allowed.clear()
