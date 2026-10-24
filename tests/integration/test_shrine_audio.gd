extends TestCase
## M2-AUD-01: the Shell Shrine trial's sounds (ShrineAudio, built by the Audio autoload when the level enters the
## tree). A turn grinds at the basin; the water's new path sounds where it ends (a pour into the inner pool, a pour
## into the sluice, a spill onto a grate); the pool's fill bed runs while the water reaches the pool and stops when
## it is full; the door's valve, the side pool's drain and the charm each sound once. The zone plays the shrine cue.

const SCENE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"

var level: ShellShrineLevel
var dir: AudioDirector
var shrine: ShrineAudio
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	dir = AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	level = (load(SCENE) as PackedScene).instantiate() as ShellShrineLevel
	level.autostart = false
	level.hand_off = func(_target: String) -> void: pass
	_host().add_child(level)
	level.set_process(false)
	level.director.auto_update = false
	level.player.set_physics_process(false)
	level.hint.instant = true
	dir.attach_shrine(level)
	shrine = dir.listeners.get(level) as ShrineAudio


func test_the_zone_plays_the_shrine_cue() -> void:
	dir.apply_zone(SCENE)
	assert_eq(dir.music.current, &"shell_shrine_interior")
	var stream := dir.music.player().stream as AudioStreamOggVorbis
	assert_true(stream != null and stream.loop, "the cue loops")
	_done()


func test_a_turn_grinds_and_the_water_sounds_where_it_ends() -> void:
	assert_true(shrine != null, "the level got its listener")
	assert_true(shrine.fill != null, "the fill bed is built")
	assert_false((shrine.fill.player as AudioStreamPlayer3D).playing, "no fill while the water spills")
	_interactable(&"basin_b1").try_interact()
	assert_eq(_events().slice(0, 2), ["turn", _end_event()], "a turn, then where the water goes")
	var turn := _last_player(&"shrine_stone_turn")
	assert_true(turn != null and turn.bus == &"World", "positional, on the World bus")
	assert_between(turn.global_position.distance_to(shrine.point("b1")), 0.0, 0.01, "at the basin")
	_solve()
	assert_eq(_events().back(), "reach_pool", "the water's arrival at the pool")
	assert_true((shrine.fill.player as AudioStreamPlayer3D).playing, "the pool fills audibly")
	shrine.fill.step(1.0, -60.0)
	assert_eq(shrine.fill.gain, 1.0)
	level.advance(float(level.trial.data["insert_sec"]) + 0.1)
	level.advance(float(level.trial.data["fill_sec"]))
	assert_true(level.trial.door_open)
	assert_eq(_events().back(), "door", "the shell valve sinks")
	assert_eq(shrine.fill.target, 0.0, "the fill stops with a full pool")
	_done()


func test_the_side_pool_drains_audibly_and_the_charm_glints() -> void:
	# The turns come from the trial's own data (a search), so a puzzle change (M2-FP-22) can't break the test.
	var turns := _turns_to(level.trial.drain())
	assert_false(turns.is_empty(), "the sluice is reachable")
	for id: StringName in turns:
		_interactable(StringName("basin_%s" % id)).try_interact()
	assert_eq(_events().back(), "reach_drain", "the water into the sluice")
	level.advance(0.1)
	assert_true(_events().has("side_drain"), "the side pool empties")
	level.advance(float(level.trial.data["insert_sec"]) + 0.1)
	_interactable(&"net_float_charm").try_interact()
	assert_eq(_events().back(), "charm")
	assert_eq(_events().count("side_drain"), 1, "once")
	_done()


func test_every_event_names_a_sound_that_plays() -> void:
	for event: String in shrine.data["events"] as Dictionary:
		var id := shrine.play_event(event, Vector3.ZERO)
		assert_ne(id, &"", "%s plays" % event)
		assert_true(dir.sfx.has(id), "%s is an sfx row" % id)
	assert_eq(shrine.play_event("nope", Vector3.ZERO), &"", "unknown events are silent")
	_done()


func _end_event() -> String:
	var end := String(level.trial.trace().back())
	if end == String(level.trial.goal()):
		return "reach_pool"
	if end == String(level.trial.drain()):
		return "reach_drain"
	return "spill"


func _events() -> Array:
	return shrine.played.map(func(e: Array) -> String: return str(e[0]))


func _last_player(id: StringName) -> AudioStreamPlayer3D:
	var out: AudioStreamPlayer3D = null
	for n: Node in dir.sfx.get_children():
		if n is AudioStreamPlayer3D and String(n.name).begins_with(String(id)) and (n as AudioStreamPlayer3D).playing:
			out = n
	return out


func _solve() -> void:
	var guard := 0
	while not level.trial.reaches(level.trial.goal()) and guard < 16:
		guard += 1
		var best := &""
		var best_n := 1 << 20
		for b in level.trial.basin_ids():
			var probe := ShellShrineTrial.new(level.trial.data)
			probe.rotations = level.trial.rotations.duplicate()
			probe.rotate(b)
			var n := probe.min_turns_to(probe.goal())
			if n >= 0 and n < best_n:
				best_n = n
				best = b
		_interactable(StringName("basin_%s" % best)).try_interact()


func _interactable(id: StringName) -> Interactable:
	for n in level.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	return null


func _done() -> void:
	if level != null and is_instance_valid(level):
		_host().remove_child(level)
		level.free()
	level = null
	if dir != null and is_instance_valid(dir):
		dir.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


## The shortest basin-turn sequence from the current state that brings the water to `target`, never passing
## through a state that fills the inner pool first (that opens the door and ends the trial). Empty if none.
func _turns_to(target: StringName) -> Array[StringName]:
	var ids := level.trial.basin_ids()
	var probe := ShellShrineTrial.new(level.trial.data)
	var start: Array = []
	for id in ids:
		start.append(int(level.trial.rotations[id]))
	var seen := {str(start): true}
	var frontier: Array = [[start, [] as Array[StringName]]]
	while not frontier.is_empty():
		var next: Array = []
		for item: Array in frontier:
			var state: Array = item[0]
			for i in ids.size():
				probe.rotations[ids[i]] = int(state[i])
			if probe.reaches(target):
				return item[1]
			if probe.reaches(probe.goal()):
				continue
			for i in ids.size():
				var s2: Array = state.duplicate()
				s2[i] = (int(s2[i]) + 1) % probe.steps()
				if not seen.has(str(s2)):
					seen[str(s2)] = true
					var path: Array[StringName] = (item[1] as Array[StringName]).duplicate()
					path.append(ids[i])
					next.append([s2, path])
		frontier = next
	return []
