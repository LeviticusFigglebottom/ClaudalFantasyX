extends TestCase
## M2-FP-108: the Saltgrass Causeway plays on env-art's final route (M2-ENV-10). The zone instances the dressing
## (its own sky, sun and sea) instead of the greybox lighting; the generated walk floor and rails are invisible;
## every spawn stands on the floor; the story triggers sit along the path in the beat order the chapter wants.

const ZONE := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
const RAY_UP_M := 2.0
const RAY_DOWN_M := 4.0
const STAND_TOLERANCE_M := 0.25
const TRIGGER_ORDER: Array[StringName] = [&"banter_posts", &"harrier", &"banter_ring", &"to_shrine"]

var zone: GreyboxZone


func _load() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as GreyboxZone
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _done() -> void:
	_host().remove_child(zone)
	zone.free()


func test_the_route_is_dressed_and_lit_by_its_own_scene() -> void:
	_load()
	assert_true(zone.dressing != null, "the final route is instanced")
	assert_true(zone.sun != null and zone.dressing.is_ancestor_of(zone.sun), "the dressing's sun lights the zone")
	assert_true(zone.dressing.get_node(^"Dresser") is CausewayZoneDresser, "dressed once, off the tree")
	assert_true(zone.dressing.get_node(^"Dresser").get_child_count() > 0, "the pieces are placed")
	var greybox := zone.get_node(^"Greybox")
	assert_true(greybox.find_children("*", "MeshInstance3D", true, false).is_empty(), "no greybox block shows")
	assert_eq(zone.find_children("*", "WorldEnvironment", true, false).size(), 1, "one sky: the dressing's")
	_done()


func test_every_spawn_stands_on_the_walk_floor() -> void:
	_load()
	await (Engine.get_main_loop() as SceneTree).physics_frame
	var space := zone.get_world_3d().direct_space_state
	for spawn: Node in zone.get_node(^"Spawns").get_children():
		var p := (spawn as Node3D).global_position
		var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * RAY_UP_M, p + Vector3.DOWN * RAY_DOWN_M)
		q.exclude = [zone.player.get_rid()]
		var hit := space.intersect_ray(q)
		assert_false(hit.is_empty(), "%s has floor under it" % spawn.name)
		if not hit.is_empty():
			assert_between(
				(hit["position"] as Vector3).y - p.y, -STAND_TOLERANCE_M, STAND_TOLERANCE_M, "%s on it" % spawn.name
			)
	_done()


func test_the_triggers_run_in_beat_order_along_the_path() -> void:
	_load()
	var head := (zone.get_node(^"Spawns/FromHaluna") as Node3D).global_position
	var last := -1.0
	for id in TRIGGER_ORDER:
		var t := zone.get_node(NodePath("Triggers/%s" % id)) as Node3D
		var d := head.distance_to(t.global_position)
		assert_true(d > last, "%s comes after the one before it (%.0f m)" % [id, d])
		last = d
	_done()
