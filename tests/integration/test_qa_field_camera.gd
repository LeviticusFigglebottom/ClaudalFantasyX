extends TestCase
## Integration QA (the PC's real-GPU Act I QA, rows 21, 24, 25/47, 37 and 38): at every spawn of every Act I zone, once
## the party is laid out and the field camera has settled on the spawn's shot, the player sees the leader. The checks:
## - in frame: his chest projects inside the viewport, in front of the camera;
## - not walled off: no drawn wall stands between the camera and his chest (FieldCameraDirector.view_blocker);
## - not covered: no follower stands on the camera's line to him under it (HeroFieldParty.sight_clear_m, head_m);
## - not in his face (IN_FACE_M) and not looking straight down on him (STEEP_DEG).
## Spawns already handed to their owner are listed in KNOWN: reported, not failed, until the fix lands.

const DT := 1.0 / 60.0
const SETTLE_FRAMES := 45
## Height of the leader's chest over his feet, the point the camera must see.
const CHEST_M := 1.3
## A follower's height: a camera line to the leader's chest passing higher than this over her feet clears her head.
const HEAD_M := 1.8
## How far off the camera's line to the leader a follower must stand (flat): two bodies no longer overlap there. The
## party aims wider (sight_clear_m); this is the bar for "covered". And the slack on the viewport's edge (pixels).
const COVER_M := 0.6
## On the walk, a follower may cross the line for at most this many frames in a row (rounding a corner): longer is
## covering him.
const COVER_MAX_FRAMES := 20
const COVER_WORDS := "off the camera's line"
const EDGE_PX := 2.0
## Nearer his chest than this, the camera is in his face (the PC's rows 24 and 25/47: Ch4 wake's DockShore, the
## ferry's FerryAft); steeper than this, the director's own pitch (the hub orbit, a follow shot) looks straight down on
## him (row 24: the wake's FeastEdge, InkLamp and WallDawn).
const IN_FACE_M := 1.5
const STEEP_DEG := 55.0
## The party-start walk: Haluna, Cutscene A's last mark, then the beach, the wall's gap and the lane to the Village
## spawn (x, z; haluna_layout.json lane 0), walked at WALK_MPS.
const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const BEACH_PATH_MARK := &"beach_path"
const ROUTE: Array[Vector2] = [Vector2(-18, 7), Vector2(-29, 6), Vector2(-36, 4), Vector2(-48, -1), Vector2(-52, -2.6)]
const WALK_MPS := 1.4
## Shots on the walk already handed to their owner: shot id -> task. Reported, not failed.
const KNOWN_WALK_SHOTS := {
	&"B02": "M3-HER-1160 (m2-slice: NemeTable's close shot covers the Village spawn)",
}
const ROUTE_MAX_FRAMES := 3600
const FLOOR_RAY_M := 3.0
## "<zone file>:<spawn>" -> the task that owns it.
const KNOWN := {
	"saltgrass_causeway.tscn:BeforeHarrier": "M3-HER-1156 (env-art: the fixed C07 shot looks away from the spawn)",
	"coilspire.tscn:Tier4": "M3-HER-1157 (env-art-b: the orbit looks through the spiral's steps behind him)",
}

var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_the_field_camera_sees_the_leader_at_every_spawn() -> void:
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var checked := 0
	for path in HeroGuardSources.field_zones():
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		_host().add_child(zone)
		var player := _controller(zone)
		var director := _director(zone)
		var party := (
			player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty if player != null else null
		)
		if party == null or director == null or not zone.has_method(&"spawn_names"):
			zone.free()
			continue
		player.set_physics_process(false)
		player.set_process_unhandled_input(false)
		party.set_physics_process(false)
		director.auto_update = false
		for sp: Variant in zone.call("spawn_names"):
			checked += 1
			var where := "%s:%s" % [path.get_file(), sp]
			zone.call("place_at", sp, zone.call("spawn_yaw_deg", sp))
			director.snap()
			for i in SETTLE_FRAMES:
				player.step(DT)
				director.update(DT)
				party.advance(DT)
			var problems := sight_problems(director, player, party, COVER_M)
			for p in problems:
				if KNOWN.has(where):
					print("  KNOWN %s: %s (%s)" % [where, p, KNOWN[where]])
				else:
					fail("%s (shot %s): %s" % [where, director.active_shot_id(), p])
		zone.free()
	Game.state = _state_was
	print("  spawns checked: %d" % checked)
	assert_true(checked > 10, "the Act I spawns were found (%d)" % checked)


## The human's party start (big15 playtest): from where Cutscene A leaves Rhen, the party walks up the beach, through
## the wall's gap and down the lane to the Village. Every frame the field camera sees him (sight_problems) and shows
## every follower in frame. The path is walked as the player walks it, at walk speed along ROUTE.
func test_the_walk_from_the_beach_to_the_village_keeps_the_party_in_view() -> void:
	Game.new_game()
	for f: StringName in [&"prologue_seen", &"ch02_met_asha"]:
		Game.set_flag(f)
	var zone := (load(HALUNA) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	var player := _controller(zone)
	var director := _director(zone)
	var party := player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	party.set_physics_process(false)
	director.auto_update = false
	var stage := HeroFieldParty.find_scripted(zone, &"CutsceneStage")[0] as CutsceneStage
	var route: Array[Vector3] = [stage.mark(BEACH_PATH_MARK).global_position]
	for p: Vector2 in ROUTE:
		route.append(Vector3(p.x, route[-1].y, p.y))
	player.global_position = route[0]
	director.snap()
	party.advance(DT)
	assert_eq(party.followers.size(), 2, "Asha and Toma both walk with him (Toma from the reserve)")
	var seen := {}
	var covered := {}  # problem kind -> the frames in a row it has held
	var leg := 1
	var frame := 0
	while leg < route.size() and frame < ROUTE_MAX_FRAMES:
		frame += 1
		var to := Vector3(route[leg].x, player.global_position.y, route[leg].z)
		var step := to - player.global_position
		if step.length() <= WALK_MPS * DT:
			leg += 1
		player.global_position = _floor(player, player.global_position + step.limit_length(WALK_MPS * DT))
		director.update(DT)
		party.advance(DT)
		if frame < SETTLE_FRAMES:
			continue
		var problems: Array[String] = []
		for p in sight_problems(director, player, party, COVER_M):
			var kind := _kind(p)
			covered[kind] = int(covered.get(kind, 0)) + 1
			if not p.contains(COVER_WORDS) or int(covered[kind]) > COVER_MAX_FRAMES:
				problems.append(p)
		for kind: String in covered.keys():
			if not _any_of_kind(sight_problems(director, player, party, COVER_M), kind):
				covered.erase(kind)
		problems.append_array(_followers_out_of_frame(director.camera, party))
		for p in problems:
			var key := "%s %s" % [director.active_shot_id(), _kind(p)]
			if not seen.has(key) and KNOWN_WALK_SHOTS.has(director.active_shot_id()):
				seen[key] = true
				print(
					(
						"  KNOWN on the walk, shot %s: %s (%s)"
						% [director.active_shot_id(), p, KNOWN_WALK_SHOTS[director.active_shot_id()]]
					)
				)
			elif not seen.has(key):
				seen[key] = true
				fail(
					(
						"frame %d at %s, shot %s: %s"
						% [frame, player.global_position.round(), director.active_shot_id(), p]
					)
				)
	assert_true(leg >= route.size(), "the walk reached the Village (%d frames)" % frame)
	zone.free()
	Game.state = _state_was


static func _any_of_kind(problems: Array[String], kind: String) -> bool:
	for p in problems:
		if _kind(p) == kind:
			return true
	return false


## A problem's kind for reporting it once per shot: its words before the first number or bracket.
static func _kind(problem: String) -> String:
	var re := RegEx.create_from_string("^[^0-9(]*")
	return re.search(problem).get_string()


static func _followers_out_of_frame(cam: Camera3D, party: HeroFieldParty) -> Array[String]:
	var out: Array[String] = []
	var size := cam.get_viewport().get_visible_rect().size
	for f in party.followers:
		var chest := f.global_position + Vector3.UP * CHEST_M
		var px := cam.unproject_position(chest)
		if cam.is_position_behind(chest) or px.x < 0.0 or px.y < 0.0 or px.x > size.x or px.y > size.y:
			out.append("%s is out of frame" % f.get_meta(&"hero_id", f.name))
	return out


## `at` dropped onto the floor under it (the player's own capsule aside).
static func _floor(player: FieldController, at: Vector3) -> Vector3:
	var q := PhysicsRayQueryParameters3D.create(at + Vector3.UP * FLOOR_RAY_M, at + Vector3.DOWN * FLOOR_RAY_M)
	q.exclude = [player.get_rid()]
	var hit := player.get_world_3d().direct_space_state.intersect_ray(q)
	return hit["position"] as Vector3 if not hit.is_empty() else at


## What keeps the director's camera from showing the leader: out of frame, a wall a player sees in the way (the
## director's own rule, FieldCameraDirector.view_blocker), or a follower nearer than `clear` (flat) to the line to him.
## Empty when he is seen.
static func sight_problems(
	director: FieldCameraDirector, player: FieldController, party: HeroFieldParty, clear: float
) -> Array[String]:
	var cam := director.camera
	var out: Array[String] = []
	var chest := player.global_position + Vector3.UP * CHEST_M
	var size := cam.get_viewport().get_visible_rect().size
	var px := cam.unproject_position(chest)
	if cam.is_position_behind(chest):
		out.append("the leader is behind the camera")
	elif px.x < -EDGE_PX or px.y < -EDGE_PX or px.x > size.x + EDGE_PX or px.y > size.y + EDGE_PX:
		out.append("the leader is out of frame (at %s of %s)" % [px.round(), size])
	if cam.global_position.distance_to(chest) < IN_FACE_M:
		out.append("the camera is in his face (%.2f m from his chest)" % cam.global_position.distance_to(chest))
	var down := rad_to_deg(asin(clampf(-cam.global_basis.z.y, -1.0, 1.0)))
	var computed := (
		director.active_shot != null and director.active_shot.mode in [CameraShot.Mode.ORBIT, CameraShot.Mode.FOLLOW]
	)
	if computed and down < -STEEP_DEG:  # an authored look down a stairwell (Coilspire's Tier1) is its author's
		out.append("the camera looks straight down (%.0f deg)" % down)
	var hit := director.view_blocker(chest, cam.global_position)
	if not hit.is_empty():
		out.append(
			(
				"a wall stands between the camera and the leader (%s, %.1f m from the camera, %.1f m from him)"
				% [
					_describe(hit["node"] as Node),
					cam.global_position.distance_to(hit["position"] as Vector3),
					chest.distance_to(hit["position"] as Vector3)
				]
			)
		)
	var line := Vector3(chest.x - cam.global_position.x, 0.0, chest.z - cam.global_position.z)
	var length := line.length()
	if length > 1e-3:
		var dir := line / length
		for f in party.followers:
			if not f.is_visible_in_tree():
				continue
			var rel := Vector3(
				f.global_position.x - cam.global_position.x, 0.0, f.global_position.z - cam.global_position.z
			)
			var along := rel.dot(dir)
			var off := absf(rel.dot(dir.cross(Vector3.UP)))
			var line_y := cam.global_position.y + (chest.y - cam.global_position.y) * (along / length)
			if along > 0.0 and along < length - clear and off < clear and line_y <= f.global_position.y + HEAD_M:
				out.append(
					"%s stands %.2f m off the camera's line to the leader" % [f.get_meta(&"hero_id", f.name), off]
				)
	return out


static func _describe(n: Node) -> String:
	return str(n.get_path()).trim_prefix("/root/TestRunner/")


static func _controller(zone: Node) -> FieldController:
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			return n as FieldController
	return null


static func _director(zone: Node) -> FieldCameraDirector:
	for n in zone.find_children("*", "", true, false):
		if n is FieldCameraDirector:
			return n as FieldCameraDirector
	return null


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
