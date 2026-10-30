extends TestCase
## M2-HER-1110: no snapping in the field. In every chapter zone (HeroGuardSources.field_zones(), read from
## locations.json) the party (Rhen leading, Asha and Toma on his trail) runs, reverses, strafes, stops and walks from
## the zone's first spawn while each visible body's transform is sampled every frame; HeroMotionGuard.transform_snaps
## flags a step or a turn faster than the limits in motion_guard.json. Deliberate cuts (teleports) are reported apart
## and allowed.

## The stick script: [stick, frames, walk]. A run, a reversal, a strafe, a stop, a diagonal walk, a stop.
const MOVES: Array[Array] = [
	[Vector2(0, -1), 90, false],
	[Vector2(0, 1), 60, false],
	[Vector2(1, 0), 45, false],
	[Vector2.ZERO, 60, false],
	[Vector2(-0.7, -0.7), 60, true],
	[Vector2.ZERO, 60, false],
]

## Snaps already handed to their owner, "<zone file>:<hero>" -> task: reported, not failed, until the fix lands.
const KNOWN := {
	"coilspire.tscn:rhen": "M3-HER-1129 (act1-chapters: a 2 m drop beside the PathFoot spawn, and its landing pop)",
	"drowned_choir.tscn:rhen": "M4-C14-02 (Act II greybox, paused by ADR 0041: a 9 m/s drop off an edge at frame 310)",
}

## The game state before the test: the guard runs on a fresh one (no flags left by earlier tests: a zone's variants and
## a scene's staging follow the flags) and puts this back.
var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_no_hero_body_snaps_in_any_zone() -> void:
	var data := HeroMotionGuard.load_data()
	var limits := data.get("transform", {}) as Dictionary
	var dt := HeroMotionGuard.frame_sec(data)
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	for path in HeroGuardSources.field_zones():
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		_host().add_child(zone)
		var tracks := _run(zone, dt)
		if _controller(zone) != null:
			assert_eq(tracks.size(), 3, "%s: Rhen, Asha and Toma are all sampled" % path.get_file())
		for who: String in tracks:
			var rates := HeroMotionGuard.peak_rates(tracks[who] as Array[Transform3D], dt, float(limits["cut_m"]))
			print("  %s %s: peak %.2f m/s, %.0f deg/s" % [path.get_file(), who, rates["speed"], rates["turn"]])
			var found := HeroMotionGuard.transform_snaps(tracks[who] as Array[Transform3D], dt, limits)
			var snaps := HeroMotionGuard.snaps_only(found)
			for s in snaps:
				print("  %s %s frame %d: %s %.1f" % [path.get_file(), who, s["frame"], s["kind"], s["value"]])
			var key := "%s:%s" % [path.get_file(), who]
			if KNOWN.has(key) and not snaps.is_empty():
				print("  KNOWN %s, %d snaps: %s" % [key, snaps.size(), KNOWN[key]])
				continue
			assert_true(snaps.is_empty(), "%s: %s never snaps (%d snaps)" % [path.get_file(), who, snaps.size()])
		zone.free()
	Game.state = _state_was


func test_the_guard_flags_a_snap_and_passes_a_cut() -> void:
	var limits := {"max_speed_mps": 6.0, "max_yaw_rate_deg_per_sec": 480.0, "cut_m": 2.5}
	var dt := 1.0 / 60.0
	var smooth: Array[Transform3D] = []
	for i in 30:
		smooth.append(Transform3D(Basis(Vector3.UP, deg_to_rad(i * 5.0)), Vector3(i * 0.05, 0, 0)))
	assert_true(HeroMotionGuard.transform_snaps(smooth, dt, limits).is_empty(), "3 m/s and 300 deg/s are fine")
	var jumpy := smooth.duplicate()
	jumpy[10] = Transform3D(jumpy[10].basis, jumpy[10].origin + Vector3(0.5, 0, 0))
	jumpy[20] = Transform3D(Basis(Vector3.UP, deg_to_rad(20 * 5.0 + 90.0)), jumpy[20].origin)
	var kinds := HeroMotionGuard.transform_snaps(jumpy, dt, limits).map(
		func(s: Dictionary) -> StringName: return s["kind"]
	)
	assert_true(kinds.has(HeroMotionGuard.MOVE), "a half-metre hop in a frame is a snap")
	assert_true(kinds.has(HeroMotionGuard.TURN), "a quarter turn in a frame is a snap")
	var cut := smooth.duplicate()
	cut[15] = Transform3D(cut[15].basis, cut[15].origin + Vector3(10, 0, 0))
	var found := HeroMotionGuard.transform_snaps(cut, dt, limits)
	assert_true(HeroMotionGuard.snaps_only(found).is_empty(), "a teleport is a cut, not a snap")
	assert_eq(found.size(), 2, "the jump there and back are both reported as cuts")


## Places the party at the zone's first spawn and plays MOVES; returns each body's transforms, by name.
func _run(zone: Node3D, dt: float) -> Dictionary:
	var director := zone.get_node_or_null("CameraDirector") as FieldCameraDirector
	if director != null:
		director.auto_update = false
	var player := _controller(zone)
	if player == null:
		print("  %s: no field player (not a walkable zone), skipped" % zone.name)
		return {}
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	var party := player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	if party != null:
		party.set_physics_process(false)
	var spawns: Array = zone.call("spawn_names") if zone.has_method("spawn_names") else []
	if not spawns.is_empty():
		zone.call("place_at", spawns[0], zone.call("spawn_yaw_deg", spawns[0]))
	if party != null:
		party.advance(dt)  # the followers spawn on the party's first frame, on the new trail
	var bodies := _bodies(player, party, dt)
	var tracks := {}
	for move in MOVES:
		player.input_override = move[0]
		player.walk_override = move[2]
		for i in int(move[1]):
			player.step(dt)
			if party != null:
				party.advance(dt)
			bodies = _bodies(player, party, dt)
			for who: String in bodies:
				var b := bodies[who] as HeroFieldActor
				b.advance(dt)
				if not tracks.has(who):
					tracks[who] = [] as Array[Transform3D]
				(tracks[who] as Array[Transform3D]).append(b.global_transform)
	return tracks


## The visible bodies: the leader's and each follower's, by hero id; process off (the test steps them).
func _bodies(player: FieldController, party: HeroFieldParty, dt: float) -> Dictionary:
	var out := {}
	var lead := player.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	if lead != null:
		out[String(lead.hero_id)] = lead
	if party != null:
		for f in party.followers:
			var b := f.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
			if b != null:
				out[String(b.hero_id)] = b
	for b: HeroFieldActor in out.values():
		if b.is_processing():
			b.set_process(false)
			b.advance(dt)
	return out


## The zone's field player (a FieldController anywhere under it), or null.
func _controller(zone: Node) -> FieldController:
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			return n as FieldController
	return null


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
