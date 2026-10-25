extends TestCase
## M3-CRE-610: FieldNpc, the villagers alive in the field. Tuning merges per villager; the turn to the player
## never snaps (each frame's yaw change stays within HeroLocomotion's rate cap), lands on the player's
## bearing and eases back to rest after the talk; talk plays and ends (directly, through the Interactable,
## and from a DialogueRunner's `finished`); a route visits its points with its pauses, ping-pongs and stops
## for the player; idle phases differ per villager; and the same inputs give the same motion.

const FISHER := "res://assets/characters/villagers/fisher/fisher_actor.tscn"
const OSU := "res://assets/characters/villagers/osu/osu_actor.tscn"
const DT := 1.0 / 60.0
## Slack on the per-frame yaw cap (float rounding of wrapf).
const EPS := 0.0001
## A heading counts as reached within this (radians).
const HEADING_TOL := 0.01
const TURN_SEC := 5.0

var made: Array[Node] = []


func _holder() -> Node3D:
	var h := Node3D.new()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(h)
	made.append(h)
	return h


func _npc(id: StringName, scene: String = FISHER, points: PackedVector3Array = PackedVector3Array()) -> FieldNpc:
	var n := FieldNpc.new()
	n.name = String(id).capitalize()
	n.npc_id = id
	n.auto_process = false
	n.actor_scene = load(scene) as PackedScene
	n.route_points = points
	_holder().add_child(n)
	return n


func _player(at: Vector3) -> Node3D:
	var p := Node3D.new()
	p.name = &"StandInPlayer"
	_holder().add_child(p)
	p.position = at
	return p


func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


## Ticks for `sec`, failing on any frame whose yaw change exceeds the cap. Returns the largest change.
func _tick_checked(n: FieldNpc, sec: float) -> float:
	var cap := n.loco.max_rate_rad * DT + EPS
	var biggest := 0.0
	for i in roundi(sec / DT):
		var before := n.yaw()
		n.tick(DT)
		var change := absf(angle_difference(before, n.yaw()))
		biggest = maxf(biggest, change)
		if change > cap:
			fail("frame %d: yaw jumped %.4f rad (cap %.4f)" % [i, change, cap])
			return biggest
	return biggest


func test_tuning_merges_defaults_and_villager_rows() -> void:
	var d := FieldNpc.load_data()
	var defaults := d["defaults"] as Dictionary
	var osu := FieldNpc.tuning_for(&"osu", d)
	var reed := FieldNpc.tuning_for(&"reed", d)
	assert_eq(reed["walk_speed_mps"], defaults["walk_speed_mps"], "a villager without a row takes the defaults")
	assert_true(float(osu["walk_speed_mps"]) < float(defaults["walk_speed_mps"]), "the elder walks slower")
	var osu_turn := (osu["locomotion"] as Dictionary)["turn"] as Dictionary
	var def_turn := (defaults["locomotion"] as Dictionary)["turn"] as Dictionary
	assert_true(float(osu_turn["max_rate_deg_per_sec"]) < float(def_turn["max_rate_deg_per_sec"]), "and turns slower")
	assert_eq(osu_turn["settle_gain"], def_turn["settle_gain"], "nested keys it does not name still merge in")
	var n := _npc(&"osu", OSU)
	assert_between(
		rad_to_deg(n.loco.max_rate_rad),
		float(osu_turn["max_rate_deg_per_sec"]) - EPS,
		float(osu_turn["max_rate_deg_per_sec"]) + EPS,
		"HeroLocomotion runs on the villager's turn"
	)
	_done()


func test_every_villager_actor_has_its_clips() -> void:
	for v: String in ["child", "fisher", "neme", "netmender", "osu", "reed", "vendor"]:
		var n := _npc(StringName(v), "res://assets/characters/villagers/%s/%s_actor.tscn" % [v, v])
		assert_true(n.anim != null, "%s: an AnimationPlayer" % v)
		if n.anim != null:
			for clip: StringName in [&"idle", &"talk", &"walk"]:
				assert_true(n.anim.has_animation(clip), "%s: clip %s" % [v, clip])
			assert_eq(String(n.anim.current_animation), "idle", "%s idles from the start" % v)
		assert_true(HeroMotion.micro_of(n.actor) != null, "%s breathes (HeroIdleMicro)" % v)
	_done()


func test_turn_to_the_player_never_snaps_and_eases_back() -> void:
	var n := _npc(&"fisher")
	var rest := n.yaw()
	var p := _player(Vector3(2.0, 0.0, 1.0))  # behind and to the side: a long turn
	n.begin_talk(p)
	assert_true(n.is_talking())
	assert_eq(String(n.anim.current_animation), "talk", "the talk gesture starts with the conversation")
	var bearing := HeroLocomotion.yaw_of(Vector3(2.0, 0.0, 1.0))
	var biggest := _tick_checked(n, TURN_SEC)
	assert_true(biggest > 0.0, "it turned")
	assert_true(absf(angle_difference(n.yaw(), bearing)) < HEADING_TOL, "it faces the player")
	n.end_talk()
	assert_false(n.is_talking())
	assert_eq(String(n.anim.current_animation), "idle", "back to idle when the talk ends")
	_tick_checked(n, float(n.tuning["return_delay_sec"]) * 0.5)
	assert_true(absf(angle_difference(n.yaw(), bearing)) < HEADING_TOL, "it holds the heading for the delay")
	_tick_checked(n, float(n.tuning["return_delay_sec"]) + TURN_SEC)
	assert_true(absf(angle_difference(n.yaw(), rest)) < HEADING_TOL, "and eases back to its resting heading")
	_done()


func test_the_turn_follows_a_moving_player_and_releases_when_they_leave() -> void:
	var n := _npc(&"fisher")
	var p := _player(Vector3(0.0, 0.0, -1.5))
	n.begin_talk(p)
	_tick_checked(n, 1.0)
	p.position = Vector3(1.5, 0.0, 0.0)
	_tick_checked(n, TURN_SEC)
	assert_true(absf(angle_difference(n.yaw(), HeroLocomotion.yaw_of(p.position))) < HEADING_TOL, "tracks")
	var ended := [false]
	n.talk_ended.connect(func() -> void: ended[0] = true)
	p.position = Vector3(float(n.tuning["release_radius_m"]) + 1.0, 0.0, 0.0)
	n.tick(DT)
	assert_true(ended[0], "walking off ends the talk")
	_done()


func test_interactable_and_dialogue_runner_drive_the_talk() -> void:
	var n := FieldNpc.new()
	n.npc_id = &"netmender"
	n.auto_process = false
	n.actor_scene = load("res://assets/characters/villagers/netmender/netmender_actor.tscn") as PackedScene
	var inter := Interactable.new()
	inter.name = &"Interactable"
	inter.id = &"test_npc_netmender"
	n.add_child(inter)
	_holder().add_child(n)
	n.player = _player(Vector3(0.0, 0.0, -1.2))
	assert_true(inter.try_interact(), "the interactable fires")
	assert_true(n.is_talking(), "using it starts the talk")
	var runner := DialogueRunner.new()
	n.follow_dialogue(runner)
	runner.emit_signal(&"finished")
	assert_false(n.is_talking(), "the dialogue finishing ends it")
	_done()


func test_route_visits_points_with_pauses_ping_pong() -> void:
	var pts := PackedVector3Array([Vector3(0.0, 0.0, -2.0), Vector3(2.0, 0.1, -2.0), Vector3(2.0, 0.0, 0.0)])
	var n := _npc(&"reed", FISHER, pts)
	var pause := float(n.tuning["pause_sec"])
	var reached: Array[int] = []
	var at: Array[float] = []
	n.point_reached.connect(
		func(i: int) -> void:
			reached.append(i)
			at.append(n.clock)
	)
	var walked := false
	var still_frames := 0
	var longest_still := 0
	var last := n.position
	for i in roundi(40.0 / DT):
		n.tick(DT)
		if n.current_clip == &"walk":
			walked = true
		still_frames = still_frames + 1 if n.position.is_equal_approx(last) else 0
		longest_still = maxi(longest_still, still_frames)
		last = n.position
	assert_true(walked, "the walk clip plays on the route")
	assert_true(reached.size() >= 4, "it reaches several points (%s)" % [reached])
	if reached.size() >= 4:
		assert_eq(reached.slice(0, 4), [0, 1, 2, 1], "ping-pong order")
	assert_true(float(longest_still) * DT >= pause - DT, "it pauses at a point (%.2f s)" % (longest_still * DT))
	for k in range(1, at.size()):
		assert_true(at[k] - at[k - 1] > pause, "leg %d starts after the pause" % k)
	assert_between(n.position.y, -EPS, pts[1].y + EPS, "the route's own Y carries it, no physics")
	_done()


func test_walking_villager_stops_for_talk_and_for_the_player() -> void:
	var pts := PackedVector3Array([Vector3(0.0, 0.0, -6.0), Vector3(0.0, 0.0, 6.0)])
	var n := _npc(&"vendor", FISHER, pts)
	for i in roundi(2.0 / DT):
		n.tick(DT)
	assert_true(n.ground_speed > 0.1, "it is walking (%.2f m/s)" % n.ground_speed)
	n.begin_talk(_player(n.position + Vector3(1.0, 0.0, 0.0)))
	for i in roundi(1.5 / DT):
		n.tick(DT)
	var held := n.position
	for i in roundi(1.0 / DT):
		n.tick(DT)
	assert_true(n.ground_speed < 0.01, "talking stops the walk")
	assert_true(n.position.distance_to(held) < 0.01, "and it stays put")
	_done()
	var m := _npc(&"vendor", FISHER, pts)
	var p := _player(Vector3(0.0, 0.0, -2.0))
	m.player = p
	for i in roundi(3.0 / DT):
		m.tick(DT)
	assert_true(m.ground_speed < 0.01, "a player within stop_radius_m holds it")
	p.position = Vector3(30.0, 0.0, 0.0)
	for i in roundi(2.0 / DT):
		m.tick(DT)
	assert_true(m.ground_speed > 0.1, "and it walks on when they leave")
	_done()


func test_idle_phases_differ_per_villager_and_are_stable() -> void:
	var a := _npc(&"fisher")
	var b := _npc(&"netmender", "res://assets/characters/villagers/netmender/netmender_actor.tscn")
	var a2 := _npc(&"fisher")
	assert_ne(a.idle_offset_sec, b.idle_offset_sec, "two villagers start their idle at different points")
	assert_eq(a.idle_offset_sec, a2.idle_offset_sec, "the same villager always starts at the same point")
	assert_between(
		a.anim.current_animation_position,
		a.idle_offset_sec - EPS,
		a.idle_offset_sec + EPS,
		"the idle clip is seeked to the offset"
	)
	_done()


func test_same_inputs_same_motion() -> void:
	var pts := PackedVector3Array([Vector3(0.0, 0.0, -2.0), Vector3(1.5, 0.0, -1.0)])
	var runs: Array = []
	for r in 2:
		var n := _npc(&"child", "res://assets/characters/villagers/child/child_actor.tscn", pts)
		var trace: Array = []
		for i in roundi(12.0 / DT):
			if i == roundi(5.0 / DT):
				n.begin_talk(_player(Vector3(-1.0, 0.0, 0.0)))
			if i == roundi(8.0 / DT):
				n.end_talk()
			n.tick(DT)
			if i % 30 == 0:
				trace.append([snappedf(n.yaw(), EPS), n.position.snappedf(EPS), n.current_clip])
		runs.append(trace)
		_done()
	assert_eq(runs[0], runs[1], "two runs trace the same path, headings and clips")


func test_route_markers_with_their_own_pause_and_loop_mode() -> void:
	var n := FieldNpc.new()
	n.npc_id = &"neme"
	n.auto_process = false
	n.actor_scene = load("res://assets/characters/villagers/neme/neme_actor.tscn") as PackedScene
	var route := Node3D.new()
	route.name = &"Route"
	n.add_child(route)
	var spots := [Vector3(0.0, 0.0, -1.5), Vector3(1.5, 0.0, -1.5), Vector3(1.5, 0.0, 0.0)]
	for i in spots.size():
		var m := Marker3D.new()
		m.position = spots[i]
		if i == 1:
			m.set_meta(FieldNpc.META_PAUSE, 0.5)
		route.add_child(m)
	var h := _holder()
	h.position = Vector3(10.0, 0.0, 0.0)
	n.position = Vector3(2.0, 0.0, 0.0)
	h.add_child(n)
	assert_eq(n.route.size(), 3, "the markers are the route")
	assert_true(n.route[0].is_equal_approx(Vector3(2.0, 0.0, -1.5)), "read once, in the parent's space")
	assert_eq(n.pauses[1], 0.5, "a marker's own pause")
	assert_eq(n.pauses[0], float(n.tuning["pause_sec"]), "the data's pause elsewhere")
	n.tuning["route_mode"] = FieldNpc.ROUTE_LOOP
	var reached: Array[int] = []
	n.point_reached.connect(func(i: int) -> void: reached.append(i))
	for i in roundi(40.0 / DT):
		n.tick(DT)
	assert_true(reached.size() >= 4, "it walks the loop (%s)" % [reached])
	if reached.size() >= 4:
		assert_eq(reached.slice(0, 4), [0, 1, 2, 0], "loop order")
	_done()
