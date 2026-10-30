extends SceneTree
## Re-seats a zone's wildlife on its dressed geometry (creatures, 2026-10-29: the Act I audit found perches and crab
## beaches still on the greybox layouts). Loads the zone, gives every visible mesh a trimesh collider (the kit's props
## carry no collision of their own), then for each placement in game/data/world/wildlife/<zone>.json:
##   perch   up onto a roof it hides under (a surface within ROOF_M above it), else snapped onto the surface under it;
##           with nothing within SNAP_M under it, the highest surface top (a roof, a post, a parapet) within SEARCH_M
##           of it at least PERCH_MIN_M over the local ground;
##   beach   its y set to the median ground under it; samples that miss the ground or sit under water pull it toward
##           the dry ones (the area keeps its size and yaw);
##   flock   its altitude raised to clear the ground under its centre by FLOCK_CLEAR_M.
## Prints each change and writes the snapped data to --out=DIR/<zone file> (Godot's JSON writes every number as a
## float: tools/creatures/wildlife_apply.py merges it back into the committed file, keeping integers and its layout).
## The doc string is left for a person to update.
## godot --headless --path . -s tools/creatures/wildlife_snap.gd -- --out=DIR <zone id> ...

const WILDLIFE_DIR := "res://game/data/world/wildlife/"
const LOCATIONS := "res://game/data/world/locations.json"
const SNAP_M := 0.6
const SEARCH_M := 6.0
const ROOF_M := 4.0  # a surface this close above a perch is the roof it hides under
const SEARCH_STEP_M := 0.5
const PERCH_MIN_M := 0.9
const FLOCK_CLEAR_M := 3.0
const RAY_UP_M := 30.0
const RAY_DOWN_M := 80.0
const BEACH_GRID := 5  # samples a side
const SETTLE_FRAMES := 3
const DECIMALS := 2


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := Array(OS.get_cmdline_user_args())
	var out := ""
	for a: String in args.duplicate():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
			args.erase(a)
	if out != "":
		DirAccess.make_dir_recursive_absolute(out)
	var scenes := {}
	var locs: Variant = JSON.parse_string(FileAccess.get_file_as_string(LOCATIONS))
	for l: Dictionary in locs if locs is Array else (locs as Dictionary).get("locations", []):
		scenes[str(l.get("id", ""))] = str(l.get("scene", ""))
	for zone: String in args:
		var file := WILDLIFE_DIR + zone.replace("/", "_") + ".json"
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(file))
		await _snap(zone, str(scenes.get(zone, "")), data)
		if out != "":
			var path_out := out.path_join(file.get_file())
			var f := FileAccess.open(path_out, FileAccess.WRITE)
			f.store_string(JSON.stringify(data, "  ", false) + "\n")
			f.close()
			print("wrote %s" % path_out)
	quit()


func _snap(zone: String, path: String, data: Dictionary) -> void:
	var node := (load(path) as PackedScene).instantiate() as Node3D
	root.add_child(node)
	for i in SETTLE_FRAMES:
		await process_frame
	var waters: Array[float] = []
	for w: Node in node.find_children("*", "WaterSurface", true, false):
		if (w as Node3D).is_visible_in_tree():
			waters.append((w as Node3D).global_position.y)
	var water: float = float(waters.max()) if not waters.is_empty() else -INF
	for mi: MeshInstance3D in node.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null or not mi.is_visible_in_tree() or mi.skin != null or _under_water_node(mi):
			continue
		var body := StaticBody3D.new()
		var shape := CollisionShape3D.new()
		shape.shape = mi.mesh.create_trimesh_shape()
		body.add_child(shape)
		mi.add_child(body)
	for i in SETTLE_FRAMES:
		await physics_frame
	var space := node.get_world_3d().direct_space_state
	print("== %s (water %s)" % [zone, str(water) if water > -INF else "none"])
	for flock: Dictionary in data.get("flocks", []):
		var perches: Array = flock.get("perches", [])
		for k in perches.size():
			var p: Array = perches[k]
			var at := Vector3(float(p[0]), float(p[1]), float(p[2]))
			var seat := _perch(space, at)
			if seat == Vector3.INF:
				print("  perch %s %s: no seat found (place it by hand)" % [flock["id"], at])
				continue
			if seat.distance_to(at) > 0.05:
				print("  perch %s %s -> %s" % [flock["id"], at, seat])
				perches[k] = [_r(seat.x), _r(seat.y), _r(seat.z), p[3]]
		var c := Vector2(float(flock["center"][0]), float(flock["center"][1]))
		var g := _ground(space, Vector3(c.x, RAY_UP_M, c.y))
		var alt: Array = flock.get("altitude_m", [1.0, 1.0])
		var low := maxf(g, water) + FLOCK_CLEAR_M if g != INF else -INF
		if float(alt[0]) < low:
			var lift := low - float(alt[0])
			print("  flock %s altitude %s -> +%.1f" % [flock["id"], alt, lift])
			flock["altitude_m"] = [_r(float(alt[0]) + lift), _r(float(alt[1]) + lift)]
	for beach: Dictionary in data.get("beaches", []):
		_beach(space, beach, water)
	node.get_parent().remove_child(node)
	node.free()


func _under_water_node(n: Node) -> bool:
	var p := n
	while p != null:
		if p is WaterSurface:
			return true
		p = p.get_parent()
	return false


func _perch(space: PhysicsDirectSpaceState3D, at: Vector3) -> Vector3:
	# under a roof or an awning (a surface not far above it): up onto its top, where it can be seen
	var roof := _ground(space, at + Vector3(0, RAY_UP_M, 0), RAY_UP_M)
	if roof != INF and roof > at.y + SNAP_M and roof - at.y < ROOF_M:
		return Vector3(at.x, roof, at.z)
	var h := _ground(space, at + Vector3(0, SNAP_M, 0), SNAP_M * 2.0)
	if h != INF:
		return Vector3(at.x, h, at.z)
	# nothing just under it: the highest top nearby that stands well above its own ground (a roof, a post, a parapet)
	var best := Vector3.INF
	var r := SEARCH_STEP_M
	while r <= SEARCH_M:
		var n := maxi(int(TAU * r / SEARCH_STEP_M), 8)
		for i in n:
			var a := TAU * i / n
			var q := at + Vector3(cos(a) * r, 0, sin(a) * r)
			var top := _ground(space, Vector3(q.x, at.y + RAY_UP_M * 0.25, q.z))
			if top == INF:
				continue
			var under := _ground(space, Vector3(q.x, top - 0.05, q.z))
			var lift := top - under if under != INF else top
			if lift >= PERCH_MIN_M and (best == Vector3.INF or absf(top - at.y) < absf(best.y - at.y)):
				best = Vector3(q.x, top, q.z)
		if best != Vector3.INF:
			return best
		r += SEARCH_STEP_M
	return best


func _beach(space: PhysicsDirectSpaceState3D, beach: Dictionary, water: float) -> void:
	var c := Vector2(float(beach["center"][0]), float(beach["center"][1]))
	var half := Vector2(float(beach["half_extents"][0]), float(beach["half_extents"][1]))
	var yaw := deg_to_rad(float(beach.get("yaw_deg", 0.0)))
	var y := float(beach.get("y", 0.0))
	var dry: Array[Vector3] = []
	var bad := 0
	for i in BEACH_GRID:
		for j in BEACH_GRID:
			var s := Vector2(lerpf(-1.0, 1.0, i / float(BEACH_GRID - 1)), lerpf(-1.0, 1.0, j / float(BEACH_GRID - 1)))
			var p := c + (s * half).rotated(-yaw)
			var h := _ground(space, Vector3(p.x, y + RAY_UP_M, p.y))
			if h == INF or h < water:
				bad += 1
			else:
				dry.append(Vector3(p.x, h, p.y))
	if dry.is_empty():
		print("  beach %s: no dry ground under it (place it by hand)" % beach["id"])
		return
	var ys: Array[float] = []
	var mid := Vector2.ZERO
	for d in dry:
		ys.append(d.y)
		mid += Vector2(d.x, d.z)
	ys.sort()
	mid /= dry.size()
	var new_y := ys[ys.size() / 2]
	var new_c := c if bad == 0 else c.lerp(mid, 1.0)
	if absf(new_y - y) > 0.05 or new_c.distance_to(c) > 0.05:
		print(
			(
				"  beach %s: y %.2f -> %.2f, centre %s -> %s (%d of %d samples off the dry ground)"
				% [beach["id"], y, new_y, c, new_c, bad, BEACH_GRID * BEACH_GRID]
			)
		)
		beach["y"] = _r(new_y)
		beach["center"] = [_r(new_c.x), _r(new_c.y)]


func _ground(space: PhysicsDirectSpaceState3D, from: Vector3, depth: float = RAY_DOWN_M) -> float:
	var q := PhysicsRayQueryParameters3D.create(from, from - Vector3(0, depth, 0))
	var hit := space.intersect_ray(q)
	return float((hit["position"] as Vector3).y) if not hit.is_empty() else INF


func _r(v: float) -> float:
	return snappedf(v, pow(10.0, -DECIMALS))
