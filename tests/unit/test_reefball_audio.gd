extends TestCase
## M3-AUD-17: Reefball by listening. ReefballAudio plays reefball_hooks.json's actions from a match's signals (by
## name, at the ball's place when a signal carries it), moves the crowd's beds and keeps the zone's, silences them
## for the naming rite and brings the murmur back after it; it reads swimmers against the water sphere (entry,
## exit with hysteresis, strokes, no stroke for a jump); and the director builds one bound to its own players.
## The sphere, the ball and the match are not on this branch, so the stand-ins are built here and name their hook
## with the `audio_class` meta (no class_name stubs: they would collide with the real classes on merge). The meta is
## set after a stand-in enters the tree, so the game's own Audio autoload (which tests never advance) does not hook it
## and start beds that would still be playing when the run quits.

const SWIM_GROUP := &"reefball_swimmer"
const EAR_GROUP := &"test_reefball_ear"


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
	_host().add_child(m)
	m.set_meta(ReefballAudio.META_CLASS, "ReefballMatch")
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
	_host().add_child(n)
	n.set_meta(ReefballAudio.META_CLASS, "ReefballBall")
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
	_host().add_child(sphere)
	sphere.set_meta(ReefballAudio.META_CLASS, "WaterSphereRig")
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
	for c: Callable in [dir.reefball.player, dir.reefball.player_at, dir.reefball.ambience, dir.reefball.beds_now]:
		assert_true(c.is_valid(), "bound to the director")
	assert_eq(dir.reefball.beds_now.call(), [] as Array[StringName], "no beds on yet")
	dir.reefball.muffler.call(&"underwater", true)
	assert_true(dir.muffle.is_muffled(), "the muffle goes to the director's BusMuffle")
	dir.reefball.muffler.call(&"underwater", false)
	assert_false(dir.muffle.is_muffled())
	# The beds themselves would start real playbacks (held past the run's end on the headless driver): record them.
	dir.reefball.ambience = func(ids: Array[StringName], sec: float) -> void:
		beds = ids.duplicate()
		fades.append(sec)
	dir.reefball.beds_now = func() -> Array[StringName]: return beds.duplicate()
	var sphere := SphereStandIn.new()
	_host().add_child(sphere)
	sphere.set_meta(ReefballAudio.META_CLASS, "WaterSphereRig")
	assert_true(dir.reefball.wants(sphere), "the director's listener wants the sphere")
	dir.reefball.watch(sphere)
	assert_eq(beds, [&"surf", &"reefball_crowd_murmur"] as Array[StringName], "the murmur joins the zone's beds")
	dir.reefball.set_crowd(ReefballAudio.CROWD_EXCITED)
	assert_eq(beds, [&"surf", &"reefball_crowd_excited"] as Array[StringName], "the excited stands replace it")
	dir.advance(1.0 / 60.0)
	sphere.free()
	dir.free()
	_done()


func test_the_ear_inside_the_sphere_muffles_the_world() -> void:
	var table := AudioData.table(AudioData.REEFBALL_HOOKS).duplicate(true)
	table["muffle"] = {"reason": "underwater", "ear_groups": [EAR_GROUP], "use_camera": false}
	var r := _listener(table)
	var calls: Array = []
	r.muffler = func(reason: StringName, on: bool) -> void: calls.append([reason, on])
	var sphere := SphereStandIn.new()
	_host().add_child(sphere)
	sphere.set_meta(ReefballAudio.META_CLASS, "WaterSphereRig")
	var ear := Node3D.new()
	ear.add_to_group(EAR_GROUP)
	_host().add_child(ear)
	ear.global_position = Vector3(9, 0, 0)
	r.watch(sphere)
	r.advance(0.1)
	assert_eq(calls, [], "outside: the world is clear")
	_to(r, ear, Vector3(4.0, 0, 0))
	assert_eq(calls, [[&"underwater", true]], "inside: through water")
	_to(r, ear, Vector3(4.9, 0, 0))
	assert_eq(calls.size(), 1, "the wall's band holds")
	_to(r, ear, Vector3(6.0, 0, 0))
	assert_eq(calls, [[&"underwater", true], [&"underwater", false]], "out: clear again")
	_to(r, ear, Vector3(0, 0, 0))
	sphere.free()
	r.advance(0.1)
	assert_eq(calls[-1], [&"underwater", false], "the sphere going lifts the muffle")
	assert_false(r.ear_inside)
	ear.free()
	r.free()
	_done()


func test_bus_muffle_ramps_the_low_pass_and_switches_it_off() -> void:
	var m := BusMuffle.new()
	var mix := AudioData.table(AudioData.MIX)
	m.configure(mix)
	var cfg := mix["muffle"] as Dictionary
	assert_false((cfg["buses"] as Array).has("Music"), "the score is not in the water")
	var bus := StringName(str((cfg["buses"] as Array)[0]))
	var fx := BusMuffle.effect_on(bus)
	assert_true(fx != null, "a low-pass on %s" % bus)
	assert_false(_enabled(bus, fx), "off while open")
	m.set_reason(&"underwater", true)
	m.advance(float(cfg["ramp_sec"]) * 0.5)
	assert_true(m.cutoff < float(cfg["open_hz"]) and m.cutoff > float(cfg["cutoff_hz"]), "half way down")
	assert_true(_enabled(bus, fx), "on while it closes")
	m.advance(float(cfg["ramp_sec"]))
	assert_eq(fx.cutoff_hz, float(cfg["cutoff_hz"]), "closed")
	m.set_reason(&"underwater", false)
	m.advance(float(cfg["ramp_sec"]) * 2.0)
	assert_eq(m.cutoff, float(cfg["open_hz"]), "open again")
	assert_false(_enabled(bus, fx), "and switched off")
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	assert_true(dir.muffle.buses().size() > 0, "the director builds one from mix.json")
	dir.free()
	_done()


func _enabled(bus: StringName, fx: AudioEffect) -> bool:
	var idx := AudioServer.get_bus_index(bus)
	for i in AudioServer.get_bus_effect_count(idx):
		if AudioServer.get_bus_effect(idx, i) == fx:
			return AudioServer.is_bus_effect_enabled(idx, i)
	return false


# --------------------------------------------------------------------------- helpers


func _listener(table: Dictionary = AudioData.table(AudioData.REEFBALL_HOOKS)) -> ReefballAudio:
	var r := ReefballAudio.new(table)
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
