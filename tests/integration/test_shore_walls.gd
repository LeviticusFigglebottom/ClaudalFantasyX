extends TestCase
## The human's playtest (2026-10-30): "you can easily fall off and start walking in the water". Pemakar's beaches shelve
## into the sea on both sides of the harbour, so its dressing stands invisible walls on the shore line
## (tools/act1/shore_walls.gd writes them; ZoneKitDressing "edge_walls"): one body per row, every one collides,
## none draws.

const ZONE := "res://game/levels/ch05/pemakar/pemakar.tscn"
const WALLS := "res://game/levels/ch05/pemakar/pemakar_shore_walls.json"
const MIN_WALLS := 200
const SAMPLE_EVERY := 25

var zone: Node3D


func _load() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _done() -> void:
	_host().remove_child(zone)
	zone.free()


func test_the_beaches_are_walled_and_nothing_draws() -> void:
	var rows: Array = JSON.parse_string(FileAccess.get_file_as_string(WALLS))
	assert_true(rows.size() >= MIN_WALLS, "%d shore walls" % rows.size())
	_load()
	var root := zone.get_node_or_null(^"Dressing/EdgeWalls")
	assert_true(root != null, "the dressing stands its edge walls")
	if root == null:
		_done()
		return
	assert_eq(root.get_child_count(), rows.size(), "one body per row")
	for w: Node in root.get_children():
		assert_true(w is StaticBody3D, "%s is a static body" % w.name)
		assert_true(w.find_children("*", "MeshInstance3D", true, false).is_empty(), "%s draws nothing" % w.name)
	_done()


func test_a_body_can_not_cross_a_shore_wall() -> void:
	var rows: Array = JSON.parse_string(FileAccess.get_file_as_string(WALLS))
	_load()
	var space := zone.get_world_3d().direct_space_state
	for i in range(0, rows.size(), SAMPLE_EVERY):
		var p: Array = rows[i]["pos"]
		var s: Array = rows[i]["size"]
		var c := Vector3(float(p[0]), float(p[1]), float(p[2]))
		var across := Vector3(1, 0, 0) if float(s[0]) < float(s[2]) else Vector3(0, 0, 1)
		var y := c.y - float(s[1]) * 0.5 + 1.5  # chest height over the wall's foot (0.6 m under the ground)
		var a := Vector3(c.x, y, c.z) - across * 1.0
		var b := Vector3(c.x, y, c.z) + across * 1.0
		var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(a, b))
		assert_false(hit.is_empty(), "wall %d at %s stops a body crossing" % [i, c])
	_done()
