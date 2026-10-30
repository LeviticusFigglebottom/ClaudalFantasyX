extends Node
## The crowd placement audit (the Lead's crowd behaviour pass, 2026-10-30: "no crowd member standing in a doorway or on
## a dock edge"). Loads each zone with crowd rows (game/data/world/npc/zones/: a row's `crowd` person or bare `body`)
## as the game does, lets its collision and VillagerLayer come in, and checks every crowd member where it stands:
##   door   a node named for a door (a kit's door, a story mark such as fathers_door) within DOOR_M across the ground;
##   edge   the ground under a ring of RING points EDGE_M round its feet: a point that finds no ground, or ground more
##          than DROP_M below its feet, is a drop (a dock's, a jetty's or a platform's edge, the water beyond),
##          unless something stands above the feet there (a rail or a wall closes the edge);
##   ground no ground under the feet at all.
## godot --headless --path . res://tools/creatures/crowd_spot_audit.tscn [-- zone_id ...]
## Prints one line per zone and a line per flagged member; exits 1 when any member is flagged.

const NPC_DIR := "res://game/data/world/npc/zones/"
const LOCATIONS := "res://game/data/world/locations.json"
const SETTLE_FRAMES := 8
const DOOR_M := 1.5
const EDGE_M := 0.6
const RING := 8
const DROP_M := 0.3
const RAY_UP_M := 0.25  # from just over the feet: a prop at knee height is not the ground they stand on
const RAY_DOWN_M := 4.0
## A ring point's first ray starts this high: what it meets above the feet (a dock's rail) closes the edge.
const BARRIER_UP_M := 1.5

var flagged := 0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var scenes := {}
	var locs: Variant = JSON.parse_string(FileAccess.get_file_as_string(LOCATIONS))
	for l: Dictionary in locs if locs is Array else (locs as Dictionary).get("locations", []):
		scenes[str(l.get("id", ""))] = str(l.get("scene", ""))
	var wanted := Array(OS.get_cmdline_user_args())
	var files := Array(DirAccess.get_files_at(NPC_DIR))
	files.sort()
	for f: String in files:
		if not f.ends_with(".json"):
			continue
		var data := VillagerLayer.load_data(NPC_DIR + f)
		var zone := str(data.get("zone", ""))
		var crowd := {}
		for row: Dictionary in data.get("villagers", []):
			# a silhouette row (M3-HER-1142: the Corrow storm figure out over the water) stands where no one could
			if (row.has("crowd") or row.has("body")) and not row.has("silhouette"):
				crowd[StringName(str(row.get("npc_id", "")))] = true
		if crowd.is_empty() or (not wanted.is_empty() and not wanted.has(zone)):
			continue
		var path := str(scenes.get(zone, ""))
		if path == "" or not ResourceLoader.exists(path):
			print("%s: no scene" % zone)
			continue
		await _audit(zone, path, crowd)
	print("crowd_spot_audit: %d flagged" % flagged)
	get_tree().quit(1 if flagged > 0 else 0)


func _audit(zone: String, path: String, crowd: Dictionary) -> void:
	var node := (load(path) as PackedScene).instantiate() as Node3D
	add_child(node)
	for i in SETTLE_FRAMES:
		await get_tree().physics_frame
	var layer := node.get_node_or_null(^"VillagerLayer") as VillagerLayer
	if layer != null and layer.villagers.is_empty():
		layer.build()
	for i in SETTLE_FRAMES:
		await get_tree().physics_frame
	var doors: Array[Node3D] = []
	for n: Node in node.find_children("*", "Node3D", true, false):
		if String(n.name).to_lower().contains("door") and not n is FieldNpc:
			doors.append(n as Node3D)
	var space := node.get_world_3d().direct_space_state
	var count := 0
	var members := 0
	var lines: Array[String] = []
	for n: Node in node.find_children("*", "FieldNpc", true, false):
		var npc := n as FieldNpc
		if not crowd.has(npc.npc_id):
			continue
		count += 1
		var p := npc.global_position
		var faults := _faults(space, p, npc, doors)
		if faults.is_empty():
			continue
		members += 1
		lines.append("  %s: %s" % [npc.npc_id, "; ".join(faults)])
		var fix := _nearest_clear(space, p, npc, doors)
		if fix != Vector3.INF:
			var local := (npc.get_parent() as Node3D).to_local(fix)
			lines.append(
				(
					"    clear %.2f m away: offset [%.2f, %.2f, %.2f] in %s"
					% [Vector2(fix.x - p.x, fix.z - p.z).length(), local.x, local.y, local.z, npc.get_parent().name]
				)
			)
	flagged += members
	print("%-28s crowd %2d, flagged %d" % [zone, count, members])
	for l in lines:
		print(l)
	node.get_parent().remove_child(node)
	node.free()


## What is wrong where a crowd member stands at `p` (empty: nothing).
func _faults(space: PhysicsDirectSpaceState3D, p: Vector3, npc: FieldNpc, doors: Array[Node3D]) -> Array[String]:
	var out: Array[String] = []
	for d in doors:
		var gap := Vector2(d.global_position.x - p.x, d.global_position.z - p.z).length()
		if gap < DOOR_M and absf(d.global_position.y - p.y) < 2.5:
			out.append("by %s (%.2f m)" % [d.name, gap])
	var under := _ground(space, p, npc)
	if is_nan(under):
		out.append("no ground under its feet")
		return out
	var drops: Array[String] = []
	for k in RING:
		var a := TAU * k / RING
		var q := Vector3(p.x, under, p.z) + Vector3(cos(a), 0.0, sin(a)) * EDGE_M
		if _ground(space, q, npc, BARRIER_UP_M) > under + DROP_M:
			continue  # a rail, a wall or a step up: a barrier, not a drop
		var y := _ground(space, q, npc)
		if is_nan(y) or y < under - DROP_M:
			drops.append("%d" % roundi(rad_to_deg(a)))
	if not drops.is_empty():
		out.append("a drop within %.1f m (toward %s deg)" % [EDGE_M, ", ".join(drops)])
	return out


## The nearest clear standing spot round `p` (on the ground there), or Vector3.INF.
func _nearest_clear(space: PhysicsDirectSpaceState3D, p: Vector3, npc: FieldNpc, doors: Array[Node3D]) -> Vector3:
	for r: float in [0.1, 0.2, 0.3, 0.45, 0.6, 0.9, 1.2, 1.5, 2.0, 2.5]:
		for k in 16:
			var a := TAU * k / 16
			var q := p + Vector3(cos(a), 0.0, sin(a)) * r
			var y := _ground(space, q, npc)
			if is_nan(y) or absf(y - p.y) > DROP_M:
				continue
			q.y = y
			if _faults(space, q, npc, doors).is_empty():
				return q
	return Vector3.INF


## The ground's height under `at` (a ray down from `up_m` above), or NAN; the villager's own bodies are skipped.
func _ground(space: PhysicsDirectSpaceState3D, at: Vector3, npc: FieldNpc, up_m := RAY_UP_M) -> float:
	var q := PhysicsRayQueryParameters3D.create(at + Vector3.UP * up_m, at + Vector3.DOWN * RAY_DOWN_M)
	var skip: Array[RID] = []
	for b: Node in npc.find_children("*", "CollisionObject3D", true, false):
		skip.append((b as CollisionObject3D).get_rid())
	q.exclude = skip
	var hit := space.intersect_ray(q)
	return float((hit["position"] as Vector3).y) if not hit.is_empty() else NAN
