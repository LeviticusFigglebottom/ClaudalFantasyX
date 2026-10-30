extends SceneTree
## The wildlife placement audit (creatures, 2026-10-29: the Lead's Act I final-quality audit). Loads each zone that
## has a game/data/world/wildlife/<zone>.json, waits for its collision, and checks every placement against it:
##   perch   a gull's perch: the surface under it (a ray down) should be within PERCH_TOL_M of its y;
##   beach   a crab area: its corners and centre should stand on ground within BEACH_TOL_M of its y, and above any
##           water surface;
##   flock   a flock's centre: its lowest altitude should clear the ground under it by FLOCK_CLEAR_M;
##   shoal   a shoal's centre should be under a water surface (or in a drowned room: the zone notes it).
## It also reports each zone's water surfaces (where fish could now swim) and zones on the list with no wildlife file.
## godot --headless --path . -s tools/creatures/wildlife_audit.gd [-- zone_id ...]

const WILDLIFE_DIR := "res://game/data/world/wildlife/"
const LOCATIONS := "res://game/data/world/locations.json"
const PERCH_TOL_M := 0.15
const BEACH_TOL_M := 0.25
const FLOCK_CLEAR_M := 2.0
const RAY_UP_M := 4.0
const RAY_DOWN_M := 60.0
const SETTLE_FRAMES := 3


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var scenes := {}
	var locs: Variant = JSON.parse_string(FileAccess.get_file_as_string(LOCATIONS))
	for l: Dictionary in locs if locs is Array else (locs as Dictionary).get("locations", []):
		scenes[str(l.get("id", ""))] = str(l.get("scene", ""))
	var wanted := Array(OS.get_cmdline_user_args())
	for f: String in DirAccess.get_files_at(WILDLIFE_DIR):
		if not f.ends_with(".json") or f == "wildlife.json":
			continue
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WILDLIFE_DIR + f))
		var zone := str(data.get("zone", ""))
		if not wanted.is_empty() and not wanted.has(zone):
			continue
		var path := str(scenes.get(zone, ""))
		if path == "" or not ResourceLoader.exists(path):
			print("%s: no scene" % zone)
			continue
		await _audit_zone(zone, path, data)
	quit()


func _audit_zone(zone: String, path: String, data: Dictionary) -> void:
	var node := (load(path) as PackedScene).instantiate() as Node3D
	root.add_child(node)
	await process_frame
	# the kit's props carry no collision of their own: give every visible mesh a trimesh collider, as
	# wildlife_snap.gd does, so a gull on a roof or a post is judged against what the player sees
	for mi: MeshInstance3D in node.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null or not mi.is_visible_in_tree() or mi.skin != null or _in_water(mi):
			continue
		var body := StaticBody3D.new()
		var shape := CollisionShape3D.new()
		shape.shape = mi.mesh.create_trimesh_shape()
		body.add_child(shape)
		mi.add_child(body)
	for i in SETTLE_FRAMES:
		await physics_frame
	var space := node.get_world_3d().direct_space_state
	var waters: Array[float] = []
	for w: Node in node.find_children("*", "WaterSurface", true, false):
		if (w as Node3D).is_visible_in_tree():
			waters.append((w as Node3D).global_position.y)
	print("== %s  water %s" % [zone, str(waters) if not waters.is_empty() else "none"])
	var bad := 0
	for flock: Dictionary in data.get("flocks", []):
		var c := _v2(flock.get("center", [0, 0]))
		var alt := _v2(flock.get("altitude_m", [1, 1]))
		var g := _ground(space, Vector3(c.x, alt.y + RAY_UP_M, c.y))
		if g != INF and alt.x - g < FLOCK_CLEAR_M:
			bad += 1
			print(
				"  flock %s: lowest altitude %.1f clears the ground (%.1f) by %.1f" % [flock["id"], alt.x, g, alt.x - g]
			)
		for p: Array in flock.get("perches", []):
			var at := Vector3(float(p[0]), float(p[1]), float(p[2]))
			var h := _ground(space, at + Vector3(0, RAY_UP_M, 0))
			if h == INF:
				bad += 1
				print("  perch %s %s: nothing under it" % [flock["id"], _fmt(at)])
			elif absf(h - at.y) > PERCH_TOL_M:
				bad += 1
				print("  perch %s %s: the surface is at %.2f (%+.2f)" % [flock["id"], _fmt(at), h, at.y - h])
	var follows := not (data.get("ground", {}) as Dictionary).is_empty()  # crabs follow the ground: no flat y to judge
	for beach: Dictionary in data.get("beaches", []):
		var c := _v2(beach.get("center", [0, 0]))
		var half := _v2(beach.get("half_extents", [1, 1]))
		var yaw := deg_to_rad(float(beach.get("yaw_deg", 0.0)))
		var y := float(beach.get("y", 0.0))
		var worst := 0.0
		var wet := false
		var miss := 0
		for s: Vector2 in [Vector2.ZERO, Vector2(1, 1), Vector2(-1, 1), Vector2(1, -1), Vector2(-1, -1)]:
			var p := c + (s * half).rotated(-yaw)
			var h := _ground(space, Vector3(p.x, y + RAY_UP_M, p.y))
			if h == INF:
				miss += 1
				continue
			worst = maxf(worst, absf(h - y))
			for wl in waters:
				wet = wet or h < wl
		if (worst > BEACH_TOL_M and not follows) or miss > 0 or wet:
			bad += 1
			print(
				(
					"  beach %s: ground off its y %.2f by up to %.2f; %d samples on nothing%s"
					% [beach["id"], y, worst, miss, "; under water" if wet else ""]
				)
			)
	for shoal: Dictionary in data.get("shoals", []):
		var c := Vector3(float(shoal["center"][0]), float(shoal["center"][1]), float(shoal["center"][2]))
		var under := false
		for wl in waters:
			under = under or c.y < wl
		if not under:
			print("  shoal %s %s: no water surface above it (a drowned room?)" % [shoal["id"], _fmt(c)])
	print("  %d placement problem(s)" % bad)
	node.get_parent().remove_child(node)
	node.free()


func _in_water(n: Node) -> bool:
	var p := n
	while p != null:
		if p is WaterSurface:
			return true
		p = p.get_parent()
	return false


## The highest surface under `from` (a ray straight down), or INF.
func _ground(space: PhysicsDirectSpaceState3D, from: Vector3) -> float:
	var q := PhysicsRayQueryParameters3D.create(from, from - Vector3(0, RAY_DOWN_M, 0))
	q.collide_with_areas = false
	var hit := space.intersect_ray(q)
	return float((hit["position"] as Vector3).y) if not hit.is_empty() else INF


func _v2(v: Variant) -> Vector2:
	return Vector2(float(v[0]), float(v[1]))


func _fmt(v: Vector3) -> String:
	return "(%.1f, %.1f, %.1f)" % [v.x, v.y, v.z]
