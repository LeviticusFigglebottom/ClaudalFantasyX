extends TestCase
## ZoneKitDressing "snap" (the eye-height pass, 2026-10-30): Ashcrown's road graves were placed on the analytic massif,
## and the crest's built mesh lies up to 2 m under it out by the causeway, so they floated over the slope. Snapped,
## each grave's origin sits on the ground that draws (the crest's LOD0), not in the air.

const ZONE := "res://game/levels/ch05/ashcrown/ashcrown.tscn"
const PREFIX := "grave_"
const ROAD_Y := -40.0  # the road graves lie on the causeway's flanks, below the tiers' graves
const MIN_GRAVES := 20
const ABOVE_M := 0.05


func test_the_road_graves_sit_on_the_slope() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	var tree := Engine.get_main_loop() as SceneTree
	var host: Node = tree.current_scene if tree.current_scene != null else tree.root
	host.add_child(zone)
	var crest: Node3D = null
	var graves: Array[Node3D] = []
	for p: Node in zone.get_node(^"Dressing").get_children():
		if p.get_child_count() == 0 or not p is Node3D:
			continue
		var nm := String(p.get_child(0).name)
		if nm == "crest_ground":
			crest = p as Node3D
		elif nm.begins_with(PREFIX) and (p as Node3D).global_position.y < ROAD_Y:
			graves.append(p as Node3D)
	assert_true(crest != null, "the crest is dressed")
	assert_true(graves.size() >= MIN_GRAVES, "%d road graves" % graves.size())
	if crest != null:
		var body := ZoneKitDressing.trimesh_collider(crest, false)
		crest.add_child(body)
		var space := zone.get_world_3d().direct_space_state
		for g: Node3D in graves:
			var at := g.global_position
			var q := PhysicsRayQueryParameters3D.create(at + Vector3.UP * 4.0, at + Vector3.DOWN * 8.0)
			q.collide_with_bodies = true
			var hit := space.intersect_ray(q)
			assert_false(hit.is_empty(), "ground under %s" % g.name)
			if not hit.is_empty():
				assert_true(
					at.y <= float(hit["position"].y) + ABOVE_M,
					"%s at y %.2f over ground %.2f" % [g.name, at.y, float(hit["position"].y)]
				)
		crest.remove_child(body)
		body.free()
	host.remove_child(zone)
	zone.free()
