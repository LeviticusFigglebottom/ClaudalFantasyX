extends TestCase
## M2-ENV-10: the shipped Saltgrass Causeway dressing (B06) builds from its generated layout: the terrain and
## every piece instance, the saltgrass arrives as baked MultiMeshes, the sea sits at low water, and the
## m2-slice hand-off (the path polyline and the anchors) is there.

const SCENE := "res://assets/environments/zones/saltgrass_causeway/saltgrass_causeway_dressing.tscn"
## haluna.md §0: the causeway is crossed at low water.
const LOW_WATER_M := -0.7
const EPS := 0.001
## The B06 route is about 280 m of playable path (haluna.md §0); the path runs head to islet.
const MIN_PATH_M := 250.0


func _zone() -> Node3D:
	var zone := (load(SCENE) as PackedScene).instantiate() as Node3D
	add_child(zone)
	return zone


func test_the_dressing_places_the_terrain_and_the_layout_pieces() -> void:
	var zone := _zone()
	var dresser := zone.get_node("Dresser") as CausewayDresser
	assert_true(dresser != null, "the zone's dresser is a CausewayDresser")
	if dresser != null:
		assert_true(dresser.find_child("causeway_flats", true, false) != null, "the flats terrain is placed")
		var expected := (dresser.layout.get("pieces", []) as Array).size()
		var placed := 0
		for k: String in dresser.placed.keys():
			if not k.begins_with("Saltgrass"):
				placed += int(dresser.placed[k])
		assert_eq(placed, expected, "every layout piece is instanced")
	zone.queue_free()


func test_saltgrass_is_baked_multimeshes() -> void:
	var zone := _zone()
	var dresser := zone.get_node("Dresser") as CausewayDresser
	var total := 0
	for child in dresser.get_children():
		if child is MultiMeshInstance3D:
			total += (child as MultiMeshInstance3D).multimesh.instance_count
	var expected := 0
	for spec: Dictionary in dresser.layout.get("instances", []):
		expected += (spec.get("xforms", []) as Array).size()
	assert_true(total > 0, "saltgrass instances exist")
	assert_eq(total, expected, "every baked transform becomes an instance")
	zone.queue_free()


func test_the_sea_is_at_low_water() -> void:
	var zone := _zone()
	await get_tree().process_frame
	var water := zone.get_node("Water") as Node3D
	assert_between(water.global_position.y, LOW_WATER_M - EPS, LOW_WATER_M + EPS, "the sea sits at low water")
	zone.queue_free()


func test_the_handoff_path_and_anchors() -> void:
	var zone := _zone()
	var dresser := zone.get_node("Dresser") as CausewayDresser
	var path := dresser.path_points()
	var length := 0.0
	for i in range(1, path.size()):
		length += path[i].distance_to(path[i - 1])
	assert_true(length > MIN_PATH_M, "the path runs head to islet (%.0f m)" % length)
	var anchors := dresser.anchors()
	for key: String in ["head", "islet_steps", "broken_post", "tide_pools", "lit_age_ring", "drownbell_disc"]:
		assert_true(anchors.has(key), "anchor %s" % key)
	zone.queue_free()
