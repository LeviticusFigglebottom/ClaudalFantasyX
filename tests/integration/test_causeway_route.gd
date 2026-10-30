extends TestCase
## M2-FP-108: the Saltgrass Causeway plays on env-art's final route (M2-ENV-10). The zone instances the dressing
## (its own sky, sun and sea) instead of the greybox lighting; the generated walk floor and rails are invisible;
## every spawn stands on the floor; the story triggers sit along the path in the beat order the chapter wants.

const ZONE := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
const RAY_UP_M := 2.0
const RAY_DOWN_M := 4.0
const STAND_TOLERANCE_M := 0.25
const MIN_FIGHTS := 1
const MAX_FIGHTS := 2
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
	var space := zone.get_world_3d().direct_space_state  # queried at once: the runner never steps a frame
	var spawns := zone.get_node(^"Spawns").get_children()
	var floored := 0
	for spawn: Node in spawns:
		var p := (spawn as Node3D).global_position
		var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * RAY_UP_M, p + Vector3.DOWN * RAY_DOWN_M)
		q.exclude = [zone.player.get_rid()]
		var hit := space.intersect_ray(q)
		assert_false(hit.is_empty(), "%s has floor under it" % spawn.name)
		if not hit.is_empty():
			floored += 1
			assert_between(
				(hit["position"] as Vector3).y - p.y, -STAND_TOLERANCE_M, STAND_TOLERANCE_M, "%s on it" % spawn.name
			)
	assert_true(not spawns.is_empty() and floored == spawns.size(), "every spawn was checked against a floor")
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


## M2-FP-114 (encounter pacing): the walk from the harrier to the islet steps meets a fight or two, never the six to
## eight the greybox's fixed 25-45 m gaps would give on the final 301 m route. The Lead's FAST-TRACK (10-30, the human's
## playtest): each fight owes the post-battle grace (the Harrier's too) and then a 95-145 m gap, so the 206 m walk meets
## one at the run (two only with more than a straight line's walking).
func test_the_route_after_the_harrier_meets_one_or_two_fights() -> void:
	_load()
	var harrier := (zone.get_node(^"Triggers/harrier") as Node3D).global_position
	var steps := (zone.get_node(^"Triggers/to_shrine") as Node3D).global_position
	var enc: Dictionary = zone.layout.get("encounters", {})
	var head := (zone.get_node(^"Spawns/FromHaluna") as Node3D).global_position
	var walk := head.distance_to(steps) - head.distance_to(harrier)
	var grace := zone.encounters.grace_after_m
	var fewest := floori(walk / (maxf(float(enc.get("max_m", 1.0)), zone.encounters.min_gap_m) + grace))
	var most := floori(walk / (maxf(float(enc.get("min_m", 1.0)), zone.encounters.min_gap_m) + grace))
	assert_true(fewest >= MIN_FIGHTS, "at least %d fights (%.0f m walk)" % [MIN_FIGHTS, walk])
	assert_true(most <= MAX_FIGHTS, "at most %d fights (%.0f m walk)" % [MAX_FIGHTS, walk])
	_done()


## M2-FP-1000: the final causeway is on the map: its path drawn from the walk floor, its stops named, and the
## objective pointing on to the shrine steps.
func test_the_causeway_has_a_map_and_an_objective() -> void:
	var none := func(_f: StringName) -> bool: return false
	var m := MapModel.new(&"ch03/saltgrass_causeway", Vector3(1.4, 0.0, -0.7), 0.0, none)
	assert_true(m.has_map(), "the causeway has a map")
	var data := MapModel.load_data()
	var s := ZoneMapShapes.build(
		m.shape_kind(), m.shape_source(), m.bounds(), data["map"], data["pieces"], data["greybox"], m.shape_hints()
	)
	assert_true(s.floors.size() > 50, "the walk floor is drawn along the route (%d floors)" % s.floors.size())
	assert_eq(m.objective_poi(), &"shrine_steps", "the objective points on to the shrine")
	assert_eq(m.objective_line(), tr("OBJ_CAUSEWAY_TO_SHRINE"))
