extends Node
## Shore walls for a kit-dressed zone (env-art-b; the human's playtest, 2026-10-30: "you can easily fall off and start
## walking in the water"). The zones' shores are kit terrain, not greybox walk blocks, so zone_edges.py can't see
## them: this flood-fills the walkable ground from every spawn on a CELL_M grid, the way the controller walks (a step
## up or down of at most STEP_M, nothing colliding across at chest height), and stands a wall on every edge from a
## reachable cell to one whose ground lies more than wade_m under the zone's water. Runs along a grid line merge into
## one box. The zone's own edge walls are taken out first, so a re-run sees the bare shore.
##
##   godot --headless --path . res://tools/act1/shore_walls.tscn -- --zone=<res tscn> --layout=<res json> \
##       --out=<res json> [--wade=0.1] [--reach=400]
##
## Writes [{"pos": [x, y, z], "size": [x, y, z]}] (ZoneKitDressing's "edge_walls" rows); the zone's dressing generator
## reads the file into its dressing. Re-run after the zone's terrain, collision or water height changes, then re-run
## the generator.

const CELL_M := 0.5
const STEP_M := 0.35
const CHEST_M := 0.9
const WALL_T_M := 0.12
const WALL_H_M := 1.8
const WALL_FOOT_M := 0.6
const MAX_CELLS := 3000000

var _args := {}


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_args[kv[0]] = kv[1] if kv.size() > 1 else ""
	_run.call_deferred()


func _ground(space: PhysicsDirectSpaceState3D, x: float, z: float, from_y: float) -> float:
	var q := PhysicsRayQueryParameters3D.create(Vector3(x, from_y + 1.2, z), Vector3(x, from_y - 8.0, z))
	var hit := space.intersect_ray(q)
	return float(hit["position"].y) if not hit.is_empty() else -INF


func _run() -> void:
	var lay: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(_args["layout"]))
	var zone: Node = (load(_args["zone"]) as PackedScene).instantiate()
	add_child(zone)
	for i in 4:
		await get_tree().physics_frame
	var old := zone.get_node_or_null(^"Dressing/EdgeWalls")
	if old != null:
		old.get_parent().remove_child(old)
		old.free()
	for i in 30:
		await get_tree().physics_frame
	var tide := zone.get_node_or_null(^"Tide")
	var water_y := float(tide.get(&"water_height_y")) if tide != null else 0.0
	var wade := float(_args.get("wade", "0.1"))
	var reach := float(_args.get("reach", "400"))
	var space := get_viewport().world_3d.direct_space_state
	var ground := {}
	var queue: Array[Vector2i] = []
	var origin := Vector2i.ZERO
	for k in lay.get("spawns", {}) as Dictionary:
		var s: Array = lay["spawns"][k]
		var key := Vector2i(roundi(float(s[0]) / CELL_M), roundi(float(s[2]) / CELL_M))
		var gy := _ground(space, key.x * CELL_M, key.y * CELL_M, float(s[1]))
		if gy > -INF and gy >= water_y - wade:
			if queue.is_empty():
				origin = key
			ground[key] = gy
			queue.append(key)
	# edges: Vector3i(cell.x, cell.y, dir index) for each reachable cell's side onto deep water
	var edges: Array[Vector3i] = []
	var dirs: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
	var head := 0
	while head < queue.size() and ground.size() < MAX_CELLS:
		var c: Vector2i = queue[head]
		head += 1
		var y: float = ground[c]
		for di in 4:
			var nc := c + dirs[di]
			if ground.has(nc) or Vector2(nc - origin).length() * CELL_M > reach:
				continue
			var ny := _ground(space, nc.x * CELL_M, nc.y * CELL_M, y)
			if ny == -INF or absf(ny - y) > STEP_M:
				continue
			var a := Vector3(c.x * CELL_M, y + CHEST_M, c.y * CELL_M)
			var b := Vector3(nc.x * CELL_M, ny + CHEST_M, nc.y * CELL_M)
			if not space.intersect_ray(PhysicsRayQueryParameters3D.create(a, b)).is_empty():
				continue
			if ny < water_y - wade:
				edges.append(Vector3i(c.x, c.y, di))
				continue
			ground[nc] = ny
			queue.append(nc)
	var rows := _merge(edges, ground)
	var f := FileAccess.open(_args["out"], FileAccess.WRITE)
	f.store_string(JSON.stringify(rows, " ", false) + "\n")
	print("SHORE water_y %.2f reachable %d edges %d walls %d" % [water_y, ground.size(), edges.size(), rows.size()])
	get_tree().quit()


## Edges along one grid line (same direction, same line, consecutive cells) merge into one box just outside the edge.
func _merge(edges: Array[Vector3i], ground: Dictionary) -> Array:
	var lines := {}
	for e in edges:
		var along_x := e.z >= 2  # a ±Z edge runs along X
		var line := Vector3i(e.y if along_x else e.x, e.z, 0)
		if not lines.has(line):
			lines[line] = []
		(lines[line] as Array).append(e.x if along_x else e.y)
	var rows: Array = []
	var keys := lines.keys()
	keys.sort()
	for line: Vector3i in keys:
		var cells: Array = lines[line]
		cells.sort()
		var start: int = cells[0]
		var prev: int = cells[0]
		for i in range(1, cells.size() + 1):
			if i < cells.size() and int(cells[i]) == prev + 1:
				prev = cells[i]
				continue
			rows.append(_box(line, start, prev, ground))
			if i < cells.size():
				start = cells[i]
				prev = cells[i]
	return rows


func _box(line: Vector3i, a: int, b: int, ground: Dictionary) -> Dictionary:
	var di := line.y
	var along_x := di >= 2
	var lo := INF
	var hi := -INF
	for k in range(a, b + 1):
		var cell := Vector2i(k, line.x) if along_x else Vector2i(line.x, k)
		lo = minf(lo, ground[cell])
		hi = maxf(hi, ground[cell])
	var sgn := 1.0 if di % 2 == 0 else -1.0
	var off := (CELL_M * 0.5 + WALL_T_M * 0.5) * sgn
	var mid := (a + b) * 0.5 * CELL_M
	var length := (b - a + 1) * CELL_M
	var y0 := lo - WALL_FOOT_M
	var y1 := hi + WALL_H_M
	var pos := (
		Vector3(mid, (y0 + y1) * 0.5, line.x * CELL_M + off)
		if along_x
		else Vector3(line.x * CELL_M + off, (y0 + y1) * 0.5, mid)
	)
	var size := Vector3(length, y1 - y0, WALL_T_M) if along_x else Vector3(WALL_T_M, y1 - y0, length)
	return {
		"pos": [snappedf(pos.x, 0.001), snappedf(pos.y, 0.001), snappedf(pos.z, 0.001)],
		"size": [snappedf(size.x, 0.001), snappedf(size.y, 0.001), snappedf(size.z, 0.001)]
	}
