extends TestCase
## M2-FP-24: the channels' curbs collide (ShrineChannelCurbs), and nothing in the room is walled off by them. A
## headless flood over the room's static collision with Rhen's own capsule: from the Entry spawn, every
## interactable (the four basins, the charm, the exit) is within reach, with the door shut and after it sinks.
## The runner never steps a physics frame, so the physics space has no broadphase yet: the test does the overlap
## itself, over the only static shapes the level builds (boxes and upright cylinders).

const SCENE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"
const CELL := 0.25
const AREA := Rect2(-15.0, -10.0, 32.0, 20.0)
const FLOOR_CLEARANCE := 0.06
const EXIT := &"Exit"

var level: ShellShrineLevel


func before_each() -> void:
	level = (load(SCENE) as PackedScene).instantiate() as ShellShrineLevel
	level.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(level)
	level.set_process(false)
	level.director.auto_update = false
	level.player.set_physics_process(false)


func _free() -> void:
	level.get_parent().remove_child(level)
	level.free()


## The room's static colliders: [global Transform3D, Shape3D].
func _obstacles() -> Array:
	var out := []
	for n: Node in level.find_children("*", "CollisionShape3D", true, false):
		var cs := n as CollisionShape3D
		if cs.disabled or not (cs.get_parent() is StaticBody3D) or cs.shape == null:
			continue
		out.append([cs.global_transform, cs.shape])
	return out


## True when Rhen's capsule fits at `at` (x, z), touching nothing but the floor.
func _stands(at: Vector3, obstacles: Array) -> bool:
	var cap := (level.player.get_node(^"Shape") as CollisionShape3D).shape as CapsuleShape3D
	var lo := FLOOR_CLEARANCE
	var hi := FLOOR_CLEARANCE + cap.height
	for o: Array in obstacles:
		var t := o[0] as Transform3D
		var local := t.affine_inverse() * Vector3(at.x, t.origin.y, at.z)
		var half_h := 0.0
		var hit := false
		if o[1] is BoxShape3D:
			var h := (o[1] as BoxShape3D).size * 0.5
			half_h = h.y
			var near := Vector2(clampf(local.x, -h.x, h.x), clampf(local.z, -h.z, h.z))
			hit = near.distance_to(Vector2(local.x, local.z)) < cap.radius
		elif o[1] is CylinderShape3D:
			var cy := o[1] as CylinderShape3D
			half_h = cy.height * 0.5
			hit = Vector2(local.x, local.z).length() < cy.radius + cap.radius
		if hit and t.origin.y + half_h > lo and t.origin.y - half_h < hi:
			return false
	return true


## Every grid cell Rhen can stand in, flooded from `start` (4-neighbour steps).
func _flood(start: Vector2) -> Dictionary:
	var obstacles := _obstacles()
	var seen := {}
	var free := {}
	var todo: Array[Vector2i] = [Vector2i(roundi(start.x / CELL), roundi(start.y / CELL))]
	while not todo.is_empty():
		var c: Vector2i = todo.pop_back()
		if seen.has(c):
			continue
		seen[c] = true
		var p := Vector2(c) * CELL
		if not AREA.has_point(p) or not _stands(Vector3(p.x, 0.0, p.y), obstacles):
			continue
		free[c] = true
		for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			todo.append(c + d)
	return free


## True when a reached cell puts Rhen's capsule inside `it`'s trigger sphere (its own shape's radius).
func _reached(free: Dictionary, it: Node3D) -> bool:
	var reach := 0.0
	for n: Node in it.find_children("*", "CollisionShape3D", true, false):
		var sh := (n as CollisionShape3D).shape
		if sh is SphereShape3D:
			reach = maxf(reach, (sh as SphereShape3D).radius)
	reach += ((level.player.get_node(^"Shape") as CollisionShape3D).shape as CapsuleShape3D).radius
	var at := Vector2(it.global_position.x, it.global_position.z)
	for c: Vector2i in free:
		if (Vector2(c) * CELL).distance_to(at) <= reach:
			return true
	return false


## Floods from the Entry spawn; every interactable must be in reach, the exit only once the door is down.
func _check(label: String, door_open: bool) -> void:
	var spawn := level.get_node(^"Spawns/Entry") as Node3D
	var free := _flood(Vector2(spawn.global_position.x, spawn.global_position.z))
	assert_true(free.size() > 1000, "%s: the hall is walkable (%d cells)" % [label, free.size()])
	for n: Node in level.find_children("*", "Interactable", true, false):
		var it := n as Node3D
		if it.name == EXIT and not door_open:
			assert_false(_reached(free, it), "%s: the shut door keeps the exit" % label)
		else:
			assert_true(_reached(free, it), "%s: %s is reachable" % [label, it.name])


func test_the_curbs_collide_and_wall_nothing_off() -> void:
	var curbs := level.find_children(ShrineChannelCurbs.BODY, "StaticBody3D", true, false)
	assert_true(curbs.size() >= level.trial.basin_ids().size(), "the troughs have curbs (%d)" % curbs.size())
	var probe := (curbs[0] as Node3D).get_child(0) as CollisionShape3D
	assert_false(_stands(probe.global_position, _obstacles()), "Rhen can't stand on a curb")
	_check("door shut", false)
	level.call(&"_open_door", true)
	_check("door open", true)
	_free()
