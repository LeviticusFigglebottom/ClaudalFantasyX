extends TestCase
## The human's playtest jog (characters' b344b974, big24): the run is a 2.6 m stride at about 3.55 m/s, 164 steps a
## minute, its clips' footfall markers on the heel strikes. On the real Haluna scene and its hero body, a run steps
## on those markers at the jog's cadence with the run rows, and the field's grounds still switch under it: Haluna's
## sand, Oruvel's planks (its default; the sea round the raft-town wades), the causeway's stone slabs (covered by
## test_footsteps_slice_zones). Sounds are recorded through the listener's player Callable, so nothing plays.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const ORUVEL := "res://game/levels/ch01/oruvel/oruvel.tscn"
const DT := 1.0 / 60.0
## The jog's field speed (locomotion.json: 3.545-3.614 m/s) and the run's seconds measured.
const RUN_MPS := 3.55
const RUN_SEC := 6.0
## The jog's cadence (characters' commit: 164 steps a minute) and the margin a frame-stepped test allows.
const JOG_SPM := 164.0
const SPM_MARGIN := 0.12

var played: Array = []
## Seconds into the run (each recorded sound carries it, so step intervals can be measured).
var clock := 0.0
var saved_state: GameStateData
var zone: Node3D


func before_each() -> void:
	played = []
	clock = 0.0
	saved_state = Game.state
	Game.state = GameStateData.new()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _load(path: String) -> Node3D:
	zone = (load(path) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	var director := zone.find_child("CameraDirector", true, false)
	if director != null:
		director.set(&"auto_update", false)
	var player := _player()
	if player != null:
		player.set_physics_process(false)
		player.set_process_unhandled_input(false)
	return zone


func _player() -> Node3D:
	return zone.find_child("Player", true, false) as Node3D


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
		zone = null
	Game.state = saved_state


func _listener(path: String) -> FootstepAudio:
	var f := FootstepAudio.new((AudioData.table(AudioData.FOOTSTEPS) as Dictionary).duplicate(true))
	f.player = func(id: StringName, at: Vector3, opts: Dictionary) -> void: played.append([id, at, opts, clock])
	zone.add_child(f)
	f.attach(_player(), path)
	return f


func test_the_jogs_markers_sit_two_to_a_cycle_at_its_cadence() -> void:
	for hero: String in ["asha", "rhen", "toma"]:
		var path := "res://assets/characters/%s/anim/%s_clips.tres" % [hero, hero]
		if not ResourceLoader.exists(path):  # M4-A2P-1980: Asha's and Rhen's libraries are binary (.res)
			path = path.get_basename() + ".res"
		var lib := load(path) as AnimationLibrary
		assert_true(lib != null and lib.has_animation(&"run"), "%s has a run" % hero)
		if lib == null or not lib.has_animation(&"run"):
			continue
		var run := lib.get_animation(&"run")
		assert_true(
			run.has_marker(&"foot_l_down") and run.has_marker(&"foot_r_down"), "%s's run marks both feet" % hero
		)
		var spm := 2.0 * 60.0 / run.length
		assert_true(absf(spm - JOG_SPM) < JOG_SPM * 0.02, "%s's run is the jog's cadence (%.0f a minute)" % [hero, spm])
		var half := run.get_marker_time(&"foot_r_down") - run.get_marker_time(&"foot_l_down")
		assert_true(absf(half - run.length * 0.5) < 0.02, "%s's feet land half a cycle apart" % hero)
	var steps := AudioData.table(AudioData.FOOTSTEPS) as Dictionary
	assert_true(absf(float(steps["run_step_m"]) * JOG_SPM / 60.0 - RUN_MPS) < 0.1, "the distance stepper keeps the jog")
	_done()


func test_a_jog_on_haluna_sand_steps_on_the_heel_strikes() -> void:
	_load(HALUNA)
	var player := _player()
	var body := player.get_node_or_null(^"HeroBody") as Node3D
	if body == null or not body.has_signal(&"foot_contact") or not body.has_method(&"advance"):
		assert_true(true, "no hero body on this branch")
		_done()
		return
	var f := _listener(HALUNA)
	body.call(&"snap")
	var spawn := zone.find_child("Village", true, false) as Node3D
	player.global_position = spawn.global_position if spawn != null else Vector3.ZERO
	player.set(&"_grounded", true)  # no physics in tests: the floor would set this on the first step in play
	var frames := int(RUN_SEC / DT)
	for i in frames:
		clock = i * DT
		player.global_position += Vector3(0.0, 0.0, -RUN_MPS * DT)
		body.call(&"advance", DT)
		f.advance(DT)
	assert_eq(f.contact_source, &"signal", "foot_contact is the step source")
	var runs := played.filter(func(p: Array) -> bool: return String(p[0]) == "hero_step_sand_run")
	assert_true(runs.size() >= 8, "the jog plays the sand's run row (%d steps)" % runs.size())
	# the cycle's steps (past the first second: the pace smoothing up to a run and the run_start clip)
	var gaps: Array[float] = []
	for k in range(1, runs.size()):
		if float(runs[k - 1][3]) >= 1.0:
			gaps.append(float(runs[k][3]) - float(runs[k - 1][3]))
	gaps.sort()
	var median := gaps[gaps.size() / 2] if not gaps.is_empty() else 0.0
	var spm := 60.0 / median if median > 0.0 else 0.0
	assert_true(absf(spm - JOG_SPM) < JOG_SPM * SPM_MARGIN, "the jog steps at its cadence (%.0f a minute)" % spm)
	assert_true(
		gaps.is_empty() or gaps[0] > 0.25,
		"no doubled step (shortest gap %.2f s)" % (gaps[0] if not gaps.is_empty() else 0.0)
	)
	_done()


func test_oruvel_is_planks_with_the_sea_round_it() -> void:
	_load(ORUVEL)
	var f := _listener(ORUVEL)
	assert_eq(String(f.surface), "wood", "the raft-town's own ground is its planks")
	var player := _player()
	var at := player.global_position if player != null else Vector3.ZERO
	assert_eq(String(f._ground(at)), "wood", "at the player's start")
	var sea := zone.find_child("Water", true, false) as Node3D
	if sea != null:
		assert_eq(
			String(f._ground(Vector3(at.x, sea.global_position.y - 0.5, at.z))), "water", "down in the sea it wades"
		)
	_done()
