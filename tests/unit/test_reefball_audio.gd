extends TestCase
## M3-AUD-17: Reefball by listening. ReefballAudio plays reefball_hooks.json's actions from a match's signals (by
## name, at the ball's place when a signal carries it), moves the crowd's beds and keeps the zone's, silences them
## for the naming rite and brings the murmur back after it; it reads swimmers against the water sphere (entry,
## exit with hysteresis, strokes, no stroke for a jump); and the director builds one bound to its own players.
## The sphere, the ball and the match are not on this branch, so the stand-ins are built here and name their hook
## with the `audio_class` meta (no class_name stubs: they would collide with the real classes on merge).

const SWIM_GROUP := &"reefball_swimmer"


class MatchStandIn:
	extends Node3D
	signal kickoff
	signal ball_kicked(at: Vector3)
	signal goal_scored(ball: Node3D, team: int)
	signal near_miss(a: int, b: int, c: int, d: int)
	signal naming_rite_started
	signal match_ended


class SphereStandIn:
	extends Node3D
	var radius := 5.0

	func radius_m() -> float:
		return radius


var played: Array = []
var beds: Array[StringName] = []
var fades: Array[float] = []


func before_each() -> void:
	super()
	played.clear()
	beds = [&"surf"]
	fades.clear()


func test_match_signals_play_rows_and_move_the_crowd() -> void:
	var r := _listener()
	var m := MatchStandIn.new()
	m.set_meta(ReefballAudio.META_CLASS, "ReefballMatch")
	_host().add_child(m)
	assert_true(r.wants(m), "the stand-in names the ReefballMatch hook")
	r.watch(m)
	r.watch(m)
	m.kickoff.emit()
	assert_eq(played, [[&"reefball_whistle_start", null]], "kickoff: the whistle, once (watched twice)")
	assert_eq(beds, [&"surf", &"reefball_crowd_excited"] as Array[StringName], "the stands get excited; surf stays")
	played.clear()
	m.ball_kicked.emit(Vector3(1, 2, 3))
	assert_eq(played, [[&"reefball_kick", Vector3(1, 2, 3)]], "a kick at the place the signal gives")
	played.clear()
	var ball := Node3D.new()
	_host().add_child(ball)
	ball.global_position = Vector3(4, 5, 6)
	m.goal_scored.emit(ball, 1)
	assert_eq(played, [[&"reefball_score", Vector3(4, 5, 6)], [&"reefball_cheer", null]], "the score at the ball")
	played.clear()
	m.near_miss.emit(1, 2, 3, 4)
	assert_eq(played, [[&"reefball_gasp", null]], "a four-argument signal still reaches its action")
	played.clear()
	m.naming_rite_started.emit()
	assert_eq(played, [[&"reefball_naming_rite", null]], "the naming rite")
	assert_eq(beds, [&"surf"] as Array[StringName], "the stands fall silent under the rite; the zone stays")
	assert_eq(fades.back(), 0.8, "at the rite's own fade")
	r.advance(11.0)
	assert_eq(beds, [&"surf"] as Array[StringName], "still quiet while the rite plays")
	r.advance(1.5)
	assert_eq(beds, [&"surf", &"reefball_crowd_murmur"] as Array[StringName], "the murmur comes back after it")
	assert_eq(fades.back(), 2.5, "at the crowd's fade")
	m.match_ended.emit()
	assert_eq(r.crowd, ReefballAudio.CROWD_MURMUR, "the end whistle leaves the murmur")
	ball.free()
	m.free()
	r.advance(0.1)
	assert_eq(r.watched.size(), 0, "a freed match is dropped")
	r.free()
	_done()


func test_a_node_without_the_hooks_signals_is_watched_quietly() -> void:
	var r := _listener()
	var n := Node3D.new()
	n.set_meta(ReefballAudio.META_CLASS, "ReefballBall")
	_host().add_child(n)
	r.watch(n)
	assert_eq(r.watched.size(), 1, "watched")
	assert_eq(played, [], "and nothing plays: it has none of kicked / pushed / caught / shot")
	var plain := Node3D.new()
	_host().add_child(plain)
	assert_false(r.wants(plain), "a node with no hook is left alone")
	n.free()
	plain.free()
	r.free()
	_done()


func test_swimmers_enter_swim_and_leave_the_sphere() -> void:
	var r := _listener()
	var sphere := SphereStandIn.new()
	sphere.set_meta(ReefballAudio.META_CLASS, "WaterSphereRig")
	_host().add_child(sphere)
	sphere.global_position = Vector3(0, 10, 0)
	var s := Node3D.new()
	s.add_to_group(SWIM_GROUP)
	_host().add_child(s)
	s.global_position = Vector3(10, 10, 0)
	r.watch(sphere)
	assert_eq(beds, [&"surf", &"reefball_crowd_murmur"] as Array[StringName], "the arena opens on the murmur")
	assert_eq(r.radius_of(sphere), 5.0, "the radius comes from the rig's radius_m()")
	r.advance(0.1)
	_to(r, s, Vector3(8, 10, 0))
	assert_eq(played, [], "the first read is a baseline, and outside is quiet")
	_to(r, s, Vector3(4.6, 10, 0))
	assert_eq(played, [[&"reefball_sphere_enter", Vector3(4.6, 10, 0)]], "through the wall: the entry, there")
	played.clear()
	for i in 20:
		_to(r, s, Vector3(4.6 - 0.1 * (i + 1), 10, 0))
	assert_eq(played.size(), 1, "2 m swum: one stroke every 1.6 m")
	assert_eq(played[0][0] if played.size() > 0 else &"", &"reefball_swim", "a stroke")
	played.clear()
	_to(r, s, Vector3(4.9, 10, 0))
	assert_eq(played.filter(func(p: Array) -> bool: return p[0] == &"reefball_sphere_exit"), [], "the band holds")
	played.clear()
	_to(r, s, Vector3(5.4, 10, 0))
	assert_eq(played, [[&"reefball_sphere_exit", Vector3(5.4, 10, 0)]], "out past the band: the exit")
	played.clear()
	_to(r, s, Vector3(0, 10, 0))
	assert_eq(played, [[&"reefball_sphere_enter", Vector3(0, 10, 0)]], "a jump in still crosses the wall")
	played.clear()
	_to(r, s, Vector3(0, 14.6, 0))
	assert_eq(played, [], "a jump of 4.6 m inside is not swum")
	assert_eq(s.global_position, Vector3(0, 14.6, 0), "listening never moves a swimmer")
	sphere.free()
	assert_eq(beds, [&"surf"] as Array[StringName], "the sphere leaving silences the stands, not the zone")
	r.advance(0.1)
	assert_eq(r.swimmers.size(), 0, "no sphere, no swimmers read")
	s.free()
	r.free()
	_done()


func test_the_director_builds_a_bound_listener() -> void:
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	assert_true(dir.reefball != null and dir.reefball.get_parent() == dir, "a ReefballAudio under the director")
	assert_true(dir.reefball.hooks.has("WaterSphereRig"), "configured from reefball_hooks.json")
	var sphere := SphereStandIn.new()
	sphere.set_meta(ReefballAudio.META_CLASS, "WaterSphereRig")
	_host().add_child(sphere)
	assert_true(dir.reefball.wants(sphere), "the director's listener wants the sphere")
	dir.reefball.watch(sphere)
	assert_true(dir.beds.has(&"reefball_crowd_murmur"), "set_ambience got the murmur bed")
	assert_eq((dir.beds[&"reefball_crowd_murmur"] as FadeVoice).target, 1.0, "fading in")
	dir.reefball.set_crowd(ReefballAudio.CROWD_EXCITED)
	assert_eq((dir.beds[&"reefball_crowd_murmur"] as FadeVoice).target, 0.0, "the murmur fades out")
	assert_eq((dir.beds[&"reefball_crowd_excited"] as FadeVoice).target, 1.0, "as the excited stands fade in")
	dir.advance(1.0 / 60.0)
	sphere.free()
	dir.free()
	_done()


# --------------------------------------------------------------------------- helpers


func _listener() -> ReefballAudio:
	var r := ReefballAudio.new(AudioData.table(AudioData.REEFBALL_HOOKS))
	r.player = func(id: StringName) -> void: played.append([id, null])
	r.player_at = func(id: StringName, at: Vector3) -> void: played.append([id, at])
	r.beds_now = func() -> Array[StringName]: return beds.duplicate()
	r.ambience = func(ids: Array[StringName], sec: float) -> void:
		beds = ids.duplicate()
		fades.append(sec)
	_host().add_child(r)
	return r


func _to(r: ReefballAudio, s: Node3D, at: Vector3) -> void:
	s.global_position = at
	r.advance(1.0 / 60.0)


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	pass
