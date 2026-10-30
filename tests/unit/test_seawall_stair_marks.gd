extends TestCase
## The Fisher Stair in Ch8's set piece (M3-CRB-009 ask 4): every wall-head arena carries the kit's real stair, with
## the anchors battle-presentation's stair meter and climber VFX use (computed from the stair's own frame by
## b_seawall_storm.py) at its head, and a camera hint that frames it.

const ARENAS: Array[String] = ["seawall_stairhead_storm", "seawall_stairhead_hoist", "seawall_stairhead_surge"]
const HEAD_TO_ENTRY_MAX_M := 0.6


func test_every_wall_head_arena_marks_its_stair() -> void:
	for aid in ARENAS:
		var root := (load("res://assets/environments/arenas/%s/%s.tscn" % [aid, aid]) as PackedScene).instantiate()
		var head := root.get_node_or_null(^"StairHead_ward") as Marker3D
		var flight := root.get_node_or_null(^"StairFlight_ward") as Marker3D
		var entry := root.get_node_or_null(^"EntryMarker_ward") as Marker3D
		assert_true(head != null and flight != null and entry != null, "%s marks the stair" % aid)
		assert_true(
			head.position.distance_to(entry.position) < HEAD_TO_ENTRY_MAX_M,
			"%s: the head is where the Climb arrives" % aid
		)
		assert_true(flight.position.y < head.position.y, "%s: the flight runs down from the head" % aid)
		assert_true(root.get_node_or_null(^"CameraHints/the_stair_head") != null, "%s frames the stair head" % aid)
		var stair := false
		for n in root.find_children("fisher_stair*", "", true, false):
			stair = stair or n.scene_file_path.ends_with("fisher_stair.glb")
		assert_true(stair, "%s stands the kit's stair" % aid)
		root.free()
