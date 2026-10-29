extends Node
## M3-C04-1226: reads Haluna's floor height under every story point of the wake night (tools/act1/ch04_haluna_wake.py
## writes them to ch04_haluna_wake_points.json) from the zone's built walk collision, into ch04_haluna_wake_floors.json.
##   godot --headless --path . res://tools/act1/ch04_haluna_wake_floors.tscn  (a scene, so the autoloads run)

const ZONE := "res://game/levels/ch04/haluna_wake/haluna_wake.tscn"
const POINTS := "res://tools/act1/ch04_haluna_wake_points.json"
const OUT := "res://tools/act1/ch04_haluna_wake_floors.json"
const RAY_TOP_Y := 60.0
const RAY_BOTTOM_Y := -20.0
const STAND_ABOVE_GROUND_M := 3.5  ## a deck or a dock may stand this far over the ground; anything higher is a roof
const MAX_HITS := 12


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as Ch04Zone
	zone.story.autostart = false
	add_child(zone)
	for i in 3:
		await get_tree().physics_frame
	var space := zone.get_world_3d().direct_space_state
	var exclude: Array[RID] = []
	var bounds := zone.haluna_collision.get_node_or_null(^"Bounds") as CollisionObject3D
	if bounds != null:
		exclude.append(bounds.get_rid())
	var props: Array[RID] = []  # a shot's height is over the ground, not a roof or a lamp
	var prop_body := zone.haluna_collision.get_node_or_null(^"Props") as CollisionObject3D
	if prop_body != null:
		props.append(prop_body.get_rid())
	var points: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(POINTS))
	var out := {}
	var keys := points.keys()
	keys.sort()
	for key: String in keys:
		var p: Array = points[key]
		var q := PhysicsRayQueryParameters3D.create(
			Vector3(float(p[0]), RAY_TOP_Y, float(p[1])), Vector3(float(p[0]), RAY_BOTTOM_Y, float(p[1]))
		)
		q.exclude = exclude + (props if key.begins_with("shot:") or key.begins_with("look:") else [] as Array[RID])
		var hits := _hits(space, q)
		var ground := -INF
		for h: Dictionary in hits:
			if (h["collider"] as Node).name == &"Ground":
				ground = maxf(ground, (h["position"] as Vector3).y)
		var y := 0.0
		var on := "MISS"
		for h: Dictionary in hits:  # the highest surface a body can stand on: the ground or a deck on it, not a roof
			var hy := (h["position"] as Vector3).y
			if hy <= ground + STAND_ABOVE_GROUND_M and (on == "MISS" or hy > y):
				y = snappedf(hy, 0.001)
				on = String((h["collider"] as Node).name)
		out[key] = y
		print("%s %s %s" % [key, y, on])
	var f := FileAccess.open(OUT, FileAccess.WRITE)
	f.store_string(JSON.stringify(out, " ", true) + "\n")
	f.close()
	get_tree().quit()


## Every surface along the ray, top down.
func _hits(space: PhysicsDirectSpaceState3D, q: PhysicsRayQueryParameters3D) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var ex := q.exclude
	for i in MAX_HITS:
		q.exclude = ex
		var h := space.intersect_ray(q)
		if h.is_empty():
			break
		if not h["collider"] is CharacterBody3D:  # the field player standing on a spawn is not its floor
			out.append(h)
		ex.append((h["collider"] as CollisionObject3D).get_rid())
	return out
