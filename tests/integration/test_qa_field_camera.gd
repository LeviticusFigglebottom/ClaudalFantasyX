extends TestCase
## Integration QA (the PC's real-GPU Act I QA, rows 21, 37 and 38): at every spawn of every Act I zone, once the party
## is laid out and the field camera has settled on the spawn's shot, the player sees the leader. Three checks:
## - in frame: his chest projects inside the viewport, in front of the camera;
## - not walled off: no drawn wall stands between the camera and his chest (FieldCameraDirector.view_blocker);
## - not covered: no follower stands on the camera's line to him (HeroFieldParty.sight_clear_m).
## Spawns already handed to their owner are listed in KNOWN: reported, not failed, until the fix lands.

const DT := 1.0 / 60.0
const SETTLE_FRAMES := 45
## Height of the leader's chest over his feet, the point the camera must see.
const CHEST_M := 1.3
## Slack on sight_clear_m (a follower eases onto its spot) and on the viewport's edge (pixels).
const SIGHT_EPS_M := 0.2
const EDGE_PX := 2.0
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
	var clear := float((HeroFieldActor.field_data().get("followers", {}) as Dictionary).get("sight_clear_m", 0.0))
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
			var problems := sight_problems(director, player, party, clear - SIGHT_EPS_M)
			for p in problems:
				if KNOWN.has(where):
					print("  KNOWN %s: %s (%s)" % [where, p, KNOWN[where]])
				else:
					fail("%s: %s" % [where, p])
		zone.free()
	Game.state = _state_was
	print("  spawns checked: %d" % checked)
	assert_true(checked > 10, "the Act I spawns were found (%d)" % checked)


## What keeps `cam` from showing the leader: out of frame, walled off, or a follower nearer than `clear` (flat) to
## the line to him. Empty when he is seen.
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
			if along > 0.0 and along < length - clear and off < clear:
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
