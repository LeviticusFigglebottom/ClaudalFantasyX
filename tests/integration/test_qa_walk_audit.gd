extends TestCase
## Integration QA, the walk audit (the Lead's 10-29 list, item 4): the real party walked through Act I's stairs and
## narrow paths (tests/integration/qa_walk_routes.json) by the real FieldController (a stick toward each waypoint,
## through the live camera director, as a player drives it), with HeroFieldParty and every body advancing as in play.
## Per route it prints a report: arrival, the leader's ramp to full speed and its stop, vertical jumps and airborne
## frames on the stairs, each hero's foot slide (travel speed past what the gait's feet cover), the followers' spacing,
## catch-ups and frames their torso stands inside level geometry, and frames the camera sits inside geometry or a wall
## hides the leader. It fails on what a player would call broken: a route not walked to its end (stuck), a follower's
## torso inside geometry or the leader hidden for longer than LIMIT_FRAMES in a row, the camera inside geometry.

const ROUTES := "res://tests/integration/qa_walk_routes.json"
const DT := 1.0 / 60.0
const SETTLE_FRAMES := 30
const ARRIVE_M := 0.35
const STUCK_FRAMES := 120
const STUCK_PROGRESS_M := 0.1
const MAX_FRAMES := 7200
const LIMIT_FRAMES := 30
const STOP_FRAMES := 120
const CHEST_M := 1.3
const TORSO_RADIUS_M := 0.15
const TORSO_HEIGHT_M := 0.9
const TORSO_CENTRE_M := 1.0
const CAMERA_PROBE_M := 0.08
const STEADY_RUN_FRACTION := 0.9

var _state_was: GameStateData
var _zone: Node3D


func before_each() -> void:
	_state_was = Game.state


func test_the_party_walks_act1_stairs_and_narrow_paths() -> void:
	var data := _json(ROUTES)
	var routes := data.get("routes", {}) as Dictionary
	for id: String in routes.keys():
		var report := walk(routes[id] as Dictionary, data)
		print(format(id, report))
		for problem: String in report.get("failures", []):
			fail("%s: %s" % [id, problem])
		if _zone != null:
			_zone.free()
			_zone = null
	Game.state = _state_was


## Walks `route` and returns its report (see format()).
func walk(route: Dictionary, data: Dictionary) -> Dictionary:
	Game.new_game()
	Game.state.party_ids.assign(
		(data.get("party", []) as Array).map(func(s: Variant) -> StringName: return StringName(str(s)))
	)
	Game.state.reserve_ids.assign(
		(data.get("reserve", []) as Array).map(func(s: Variant) -> StringName: return StringName(str(s)))
	)
	for f: Variant in route.get("flags", []):
		Game.set_flag(StringName(str(f)))
	_zone = (load(str(route["scene"])) as PackedScene).instantiate() as Node3D
	var story := _zone.get(&"story") as ZoneStory if "story" in _zone else null
	if story != null:
		story.autostart = false
	if "autoplay" in _zone:
		_zone.set(&"autoplay", false)
	_host().add_child(_zone)
	var player := _controller(_zone)
	var director := player.director
	var party := player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	party.set_physics_process(false)
	if director != null:
		director.auto_update = false
	var stairs := player.get_node_or_null(NodePath(String(HeroStairs.NAME))) as HeroStairs
	if stairs != null:  # the zone is ready now: in play its deferred build lands a frame later
		stairs.build_from_layout()
	for block: Variant in route.get("hide_blocks", []):  # story gates the route assumes open
		_zone.call(&"hide_block", str(block))
	var points := _route_points(route, _zone, player)
	var report := {"failures": [] as Array[String], "points": points.size()}
	if points.is_empty():
		(report["failures"] as Array).append("no route points (check its start and waypoints)")
		return report
	party.catch_up()
	for i in SETTLE_FRAMES:
		_frame(player, director, party, Vector2.ZERO, false)
	var bodies := _bodies(player, party)  # after the settle: the followers spawn on the party's first advance
	var run := bool(route.get("run", true))
	var top := float(player.data.get("run_speed_mps" if run else "walk_speed_mps", 1.0))
	var space := _zone.get_world_3d().direct_space_state
	var leg := 0
	var frame := 0
	var best := INF
	var since_progress := 0
	var reach_frame := -1
	var last_y := player.global_position.y
	var max_dy := 0.0
	var airborne := 0
	var catchups := 0
	var clip_run := {}
	var clip_max := {}
	var hidden_run := 0
	var hidden_max := 0
	var camera_inside := 0
	var gaps := {}
	var slide := {}
	var top_speed := {}
	var hidden_why := {}
	var last_pos := {}
	for b: HeroFieldActor in bodies:
		last_pos[b] = b.get_parent().global_position
	while leg < points.size() and frame < MAX_FRAMES:
		frame += 1
		var to := points[leg]
		var flat := Vector3(to.x - player.global_position.x, 0.0, to.z - player.global_position.z)
		if flat.length() <= ARRIVE_M:
			leg += 1
			best = INF
			since_progress = 0
			continue
		if flat.length() < best - STUCK_PROGRESS_M:
			best = flat.length()
			since_progress = 0
		else:
			since_progress += 1
			if since_progress > STUCK_FRAMES:
				(report["failures"] as Array).append(
					(
						"stuck at %s on the way to waypoint %d %s: %s"
						% [player.global_position.snapped(Vector3.ONE * 0.1), leg, to, _blocker(player, flat)]
					)
				)
				break
		_frame(player, director, party, _stick_toward(player, director, flat), not run)
		var speed := Vector2(player.velocity.x, player.velocity.z).length()
		if reach_frame < 0 and speed >= top * 0.95:
			reach_frame = frame
		var dy := player.global_position.y - last_y
		last_y = player.global_position.y
		max_dy = maxf(max_dy, absf(dy))
		if not player.grounded():
			airborne += 1
		for b: HeroFieldActor in bodies:
			var node := b.get_parent() as Node3D
			var moved := node.global_position - (last_pos[b] as Vector3)
			last_pos[b] = node.global_position
			if b.loco.is_teleport(moved.length()):
				catchups += 1
				continue
			var travel := Vector2(moved.x, moved.z).length() / DT
			top_speed[b.hero_id] = maxf(float(top_speed.get(b.hero_id, 0.0)), travel)
			if travel >= top * STEADY_RUN_FRACTION:
				var feet := travel
				if travel > b.loco.run_clip_mps:
					feet = b.loco.run_clip_mps * b.loco.playback_scale(travel)
				slide[b.hero_id] = maxf(float(slide.get(b.hero_id, 0.0)), (travel - feet) / travel)
		var ahead: Node3D = player
		for f in party.followers:
			if not f.visible:
				var why := "staged" if party.staged(StringName(f.get_meta(&"hero_id", ""))) else "should_hide"
				hidden_why[StringName(f.get_meta(&"hero_id", ""))] = why
				continue
			var gap := (
				Vector2(f.global_position.x - ahead.global_position.x, f.global_position.z - ahead.global_position.z)
				. length()
			)
			var id_f := StringName(f.get_meta(&"hero_id", ""))
			var g := gaps.get(id_f, [INF, 0.0]) as Array
			gaps[id_f] = [minf(float(g[0]), gap), maxf(float(g[1]), gap)]
			ahead = f
			if _torso_inside(space, f.global_position, player):
				clip_run[id_f] = int(clip_run.get(id_f, 0)) + 1
				clip_max[id_f] = maxi(int(clip_max.get(id_f, 0)), int(clip_run[id_f]))
			else:
				clip_run[id_f] = 0
		if director != null and director.camera != null:
			var cam := director.camera.global_position
			if _point_inside(space, cam, player):
				camera_inside += 1
			var hit := space.intersect_ray(_ray(cam, player.global_position + Vector3.UP * CHEST_M, player))
			hidden_run = hidden_run + 1 if not hit.is_empty() else 0
			hidden_max = maxi(hidden_max, hidden_run)
	if leg < points.size() and (report["failures"] as Array).is_empty():
		(report["failures"] as Array).append(
			"did not reach the end in %d frames (waypoint %d of %d)" % [frame, leg, points.size()]
		)
	var stop_from := player.global_position
	var stop_frames := 0
	for i in STOP_FRAMES:
		_frame(player, director, party, Vector2.ZERO, not run)
		if Vector2(player.velocity.x, player.velocity.z).length() > 0.05:
			stop_frames = i + 1
	report["frames"] = frame
	report["reach_s"] = reach_frame * DT if reach_frame > 0 else -1.0
	report["stop_m"] = Vector2(player.global_position.x - stop_from.x, player.global_position.z - stop_from.z).length()
	report["stop_s"] = stop_frames * DT
	report["max_dy_m"] = max_dy
	report["airborne"] = airborne
	report["catchups"] = catchups
	report["gaps"] = gaps
	report["slide"] = slide
	report["top_speed"] = top_speed
	report["hidden_why"] = hidden_why
	report["clip_max"] = clip_max
	report["hidden_max"] = hidden_max
	report["camera_inside"] = camera_inside
	for id_f: StringName in clip_max.keys():
		if int(clip_max[id_f]) > LIMIT_FRAMES:
			(report["failures"] as Array).append(
				"%s stands inside geometry for %d frames in a row" % [id_f, clip_max[id_f]]
			)
	if hidden_max > LIMIT_FRAMES:
		(report["failures"] as Array).append(
			"a wall hides the leader from the camera for %d frames in a row" % hidden_max
		)
	if camera_inside > 0:
		(report["failures"] as Array).append("the camera is inside geometry for %d frames" % camera_inside)
	return report


static func format(id: String, r: Dictionary) -> String:
	var lines: Array[String] = [
		(
			"  WALK %s: %d frames, run in %.2f s, stop %.2f m in %.2f s, max dy %.3f m/frame, airborne %d, catch-ups %d"
			% [
				id,
				int(r.get("frames", 0)),
				float(r.get("reach_s", -1.0)),
				float(r.get("stop_m", 0.0)),
				float(r.get("stop_s", 0.0)),
				float(r.get("max_dy_m", 0.0)),
				int(r.get("airborne", 0)),
				int(r.get("catchups", 0))
			]
		)
	]
	var gaps := r.get("gaps", {}) as Dictionary
	for id_f: Variant in gaps.keys():
		lines.append(
			(
				"    %s: gap %.2f-%.2f m, inside geometry max %d frames"
				% [
					id_f,
					float(gaps[id_f][0]),
					float(gaps[id_f][1]),
					int((r.get("clip_max", {}) as Dictionary).get(id_f, 0))
				]
			)
		)
	var slide := r.get("slide", {}) as Dictionary
	var parts: Array[String] = []
	for h: Variant in slide.keys():
		parts.append("%s %d%%" % [h, roundi(float(slide[h]) * 100.0)])
	lines.append("    foot slide at full speed: %s" % (", ".join(parts) if not parts.is_empty() else "none measured"))
	var tops: Array[String] = []
	var top_speed := r.get("top_speed", {}) as Dictionary
	for h: Variant in top_speed.keys():
		tops.append("%s %.2f" % [h, float(top_speed[h])])
	lines.append("    top travel m/s: %s" % ", ".join(tops))
	var why := r.get("hidden_why", {}) as Dictionary
	for h: Variant in why.keys():
		lines.append("    %s hidden (%s)" % [h, why[h]])
	lines.append(
		(
			"    camera: leader hidden max %d frames, inside geometry %d frames"
			% [int(r.get("hidden_max", 0)), int(r.get("camera_inside", 0))]
		)
	)
	return "\n".join(lines)


static func _frame(
	player: FieldController, director: FieldCameraDirector, party: HeroFieldParty, stick: Vector2, walk: bool
) -> void:
	player.input_override = stick
	player.walk_override = walk
	player.step(DT)
	var stairs := player.get_node_or_null(NodePath(String(HeroStairs.NAME))) as HeroStairs
	if stairs != null:  # HeroStairs runs after the controller's step in play (its _physics_process)
		stairs.advance(DT)
	if director != null:
		director.update(DT)
	party.advance(DT)
	for b: HeroFieldActor in _bodies(player, party):
		b.advance(DT)


## The stick (Input.get_vector convention) that drives toward `flat` (an XZ direction) through the motor's
## reference yaw: the latched one while the stick is held across a shot change, else the camera's.
static func _stick_toward(player: FieldController, director: FieldCameraDirector, flat: Vector3) -> Vector2:
	var yaw := (
		player.motor.reference_yaw if player.motor.latched else (director.camera_yaw() if director != null else 0.0)
	)
	var basis := Basis(Vector3.UP, yaw)
	var dir := flat.normalized()
	return Vector2(dir.dot(basis * Vector3.RIGHT), -dir.dot(basis * Vector3.FORWARD))


## What a test move toward `flat` hits first: the collider's path, and the contact normal (or "nothing").
static func _blocker(player: FieldController, flat: Vector3) -> String:
	var hit := player.move_and_collide(flat.normalized() * 0.2, true)
	if hit == null:
		return "nothing in the way (the controller doesn't move: a floor edge or the stairs profile?)"
	var c := hit.get_collider() as Node
	var owner_path := str(c.get_path()) if c != null else "?"
	return "blocked by %s, normal %s" % [owner_path, hit.get_normal().snapped(Vector3.ONE * 0.01)]


static func _bodies(player: FieldController, party: HeroFieldParty) -> Array[HeroFieldActor]:
	var out: Array[HeroFieldActor] = []
	var lead := player.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	if lead != null:
		out.append(lead)
	for f in party.followers:
		var b := f.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
		if b != null:
			out.append(b)
	return out


static func _route_points(route: Dictionary, zone: Node3D, player: FieldController) -> Array[Vector3]:
	var out: Array[Vector3] = []
	if route.has("start_mark"):
		var stage := HeroFieldParty.find_scripted(zone, &"CutsceneStage")[0] as CutsceneStage
		player.global_position = stage.mark(StringName(str(route["start_mark"]))).global_position
	elif route.has("start_spawn"):
		zone.call(
			&"place_at",
			StringName(str(route["start_spawn"])),
			zone.call(&"spawn_yaw_deg", StringName(str(route["start_spawn"])))
		)
	elif route.has("start_point"):
		player.global_position = _v3(route["start_point"])
	if player.director != null:
		player.director.snap()
	var y := player.global_position.y
	for p: Variant in route.get("points_xz", []):
		out.append(Vector3(float(p[0]), y, float(p[1])))
	for key: String in ["stairs_up", "stairs_down"]:
		if not route.has(key):
			continue
		var row := _collision_row(zone, "stairs", str(route[key]))
		if row.is_empty():
			return []
		var foot := _v3(row["foot"])
		var head := _v3(row["head"])
		var a := foot if key == "stairs_up" else head
		var b := head if key == "stairs_up" else foot
		var along := Vector3(b.x - a.x, 0.0, b.z - a.z).normalized()
		out.append_array([a - along * 0.6, a, b, b + along * float(route.get("beyond_m", 2.0))] as Array[Vector3])
	for chain: Variant in route.get("ramp_chain", []):
		for row: Dictionary in _collision_rows(zone, "ramps"):
			if str(row.get("id", "")).begins_with(str(chain) + "_"):
				out.append(_v3(row["from"]))
				out.append(_v3(row["to"]))
	return out


static func _collision_rows(zone: Node, key: String) -> Array:
	var layout := zone.get(&"layout") as Dictionary if "layout" in zone else {}
	var rows: Array = (layout.get(key, []) as Array).duplicate()
	var seen := {}
	for row: Variant in rows:
		seen[str((row as Dictionary).get("id", ""))] = true
	var path := str(layout.get("collision_path", ""))
	if path != "":  # KitCollision may have merged the file's rows into the layout already
		for row: Variant in _json(path).get(key, []) as Array:
			if not seen.has(str((row as Dictionary).get("id", ""))):
				rows.append(row)
	return rows


static func _collision_row(zone: Node, key: String, id: String) -> Dictionary:
	for row: Variant in _collision_rows(zone, key):
		if row is Dictionary and str((row as Dictionary).get("id", "")) == id:
			return row
	return {}


static func _torso_inside(space: PhysicsDirectSpaceState3D, feet: Vector3, player: FieldController) -> bool:
	var q := PhysicsShapeQueryParameters3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = TORSO_RADIUS_M
	cap.height = TORSO_HEIGHT_M
	q.shape = cap
	q.transform = Transform3D(Basis.IDENTITY, feet + Vector3.UP * TORSO_CENTRE_M)
	q.exclude = [player.get_rid()]
	q.collide_with_areas = false
	return not space.intersect_shape(q, 1).is_empty()


static func _point_inside(space: PhysicsDirectSpaceState3D, at: Vector3, player: FieldController) -> bool:
	var q := PhysicsShapeQueryParameters3D.new()
	var s := SphereShape3D.new()
	s.radius = CAMERA_PROBE_M
	q.shape = s
	q.transform = Transform3D(Basis.IDENTITY, at)
	q.exclude = [player.get_rid()]
	q.collide_with_areas = false
	return not space.intersect_shape(q, 1).is_empty()


static func _ray(from: Vector3, to: Vector3, player: FieldController) -> PhysicsRayQueryParameters3D:
	var q := PhysicsRayQueryParameters3D.create(from, to)
	q.exclude = [player.get_rid()]
	q.collide_with_areas = false
	return q


static func _controller(zone: Node) -> FieldController:
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			return n
	return null


static func _v3(v: Variant) -> Vector3:
	return Vector3(float(v[0]), float(v[1]), float(v[2]))


static func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
