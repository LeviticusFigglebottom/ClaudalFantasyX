extends Node
## ADR 0041 (act1-chapters): checks every story camera ("shots") of the Act I zones against the zone's built collision:
## its line of sight to its look_at, and whether it sits enclosed (inside a hull, a wall, the ground). For a failing
## shot it searches the nearest clear position at the same distance from its target (turning about the target, then
## rising), and writes the findings to SHOTS_OUT (JSON). Run as a scene (the autoloads run):
##   SHOTS_OUT=<file.json> godot --headless --path . res://tools/act1/shot_check.tscn

const ZONES: Array[String] = [
	"res://game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn",
	"res://game/levels/ch04/haluna_wake/haluna_wake.tscn",
	"res://game/levels/ch05/pemakar/pemakar.tscn",
	"res://game/levels/ch06/brine_shoals/brine_shoals.tscn",
	"res://game/levels/ch07/tamsule/tamsule.tscn",
	"res://game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn",
	"res://game/levels/ch08/corrow/corrow.tscn",
	"res://game/levels/ch08/coilspire/coilspire.tscn",
	"res://game/levels/ch09/corrow_night/corrow_night.tscn",
]
const CLEAR_FRACTION := 0.9  ## a ray reaching this far toward the target counts as clear
const ENCLOSED_RAY_M := 2.5
const ENCLOSED_HITS := 5  ## of the six axis rays
const TURNS_DEG: Array[float] = [10.0, -10.0, 20.0, -20.0, 35.0, -35.0, 50.0, -50.0, 70.0, -70.0, 90.0, -90.0]
const RISES_M: Array[float] = [0.0, 0.8, 1.6]
const MAX_SKIPS := 8


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var out := {}
	for path in ZONES:
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		add_child(zone)
		for i in 3:
			await get_tree().physics_frame
		var space := zone.get_world_3d().direct_space_state
		var exclude: Array[RID] = []
		for n in zone.find_children("*", "CollisionObject3D", true, false):
			if n is FieldController or (n is Area3D):
				exclude.append((n as CollisionObject3D).get_rid())
			elif "stage" in zone and zone.get(&"stage") != null and (zone.get(&"stage") as Node).is_ancestor_of(n):
				exclude.append((n as CollisionObject3D).get_rid())
		var layout: Dictionary = zone.get(&"layout")
		var rows := {}
		for id: String in layout.get("shots", {}):
			var shot: Dictionary = layout["shots"][id]
			var pos := _v(shot["pos"])
			var look := _v(shot["look_at"])
			var why := _fault(space, exclude, pos, look)
			if why == "":
				continue
			var fix := _search(space, exclude, pos, look)
			rows[id] = {"why": why, "pos": shot["pos"], "look_at": shot["look_at"], "fix": fix}
			print("SHOT %s %s: %s -> %s" % [path.get_file(), id, why, fix])
		out[path] = rows
		zone.queue_free()
		await get_tree().process_frame
	var f := FileAccess.open(OS.get_environment("SHOTS_OUT"), FileAccess.WRITE)
	f.store_string(JSON.stringify(out, " ", true) + "\n")
	f.close()
	get_tree().quit()


func _v(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))


## "" when the camera sees its target from open air, else what is wrong.
func _fault(space: PhysicsDirectSpaceState3D, exclude: Array[RID], pos: Vector3, look: Vector3) -> String:
	var hits := 0
	for d: Vector3 in [Vector3.UP, Vector3.DOWN, Vector3.LEFT, Vector3.RIGHT, Vector3.FORWARD, Vector3.BACK]:
		var q := PhysicsRayQueryParameters3D.create(pos, pos + d * ENCLOSED_RAY_M)
		q.exclude = exclude
		q.hit_back_faces = true
		if not space.intersect_ray(q).is_empty():
			hits += 1
	if hits >= ENCLOSED_HITS:
		return "enclosed"
	var skip := exclude.duplicate()
	for i in MAX_SKIPS:
		var q2 := PhysicsRayQueryParameters3D.create(pos, look)
		q2.exclude = skip
		q2.hit_back_faces = true
		var hit := space.intersect_ray(q2)
		if hit.is_empty() or pos.distance_to(hit["position"]) >= pos.distance_to(look) * CLEAR_FRACTION:
			return ""
		var body := hit["collider"] as CollisionObject3D
		if _seen(body):
			return "blocked by %s at %.1f m" % [body.name, pos.distance_to(hit["position"])]
		skip.append(body.get_rid())  # collision only (a bound, a rail): the camera sees through it
	return ""


## Whether a collider is something the camera sees: everything but the invisible bounds (a hidden greybox block under
## a kit dressing stands for the kit's own geometry).
static func _seen(body: CollisionObject3D) -> bool:
	return not String(body.name).contains("Bound")
