extends KitWalkProbe
## M3-C08-1210, ADR 0200: ch08/coilspire's ways in are walkable on the kit's own collision (KitWalkProbe with the
## physics floor and the kit's trimesh pieces): from the path's top over the door's sill into the hall; from the path's
## top round to the keeper's hut, in at its side door and up to the hearth (B03's trigger); and from the crown stair's
## head out through the gallery door on to the beacon gallery (B07); and up each flight (gates open) to its top. The
## kit's LOD1 shell and tiers are closed (no doors), so their doorways collide from LOD0 ("collide_lod0_in"); the ground
## and the hut collide from LOD0.

const COILSPIRE := "res://game/levels/ch08/coilspire/coilspire.tscn"
const TERRAIN: Array[String] = ["coilspire_ground.glb"]
const HALL_Y := 39.285
const GALLERY_Y := 81.885
const COLLISION := "res://game/levels/ch08/coilspire/coilspire_collision.json"
const FLIGHTS := 5
const GATES: Array[StringName] = [&"Gate_t1", &"Gate_t2", &"Gate_t3", &"Gate_t4"]


func before_each() -> void:
	open(COILSPIRE)
	physics_floor = true
	check_kit = true
	kit_terrain = TERRAIN


func _mark(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_path_reaches_the_hall_through_the_door() -> void:
	var start := Vector3(303.4, 38.9, 151.6)
	var pts: Array[Vector3] = [start, Vector3(303.0, 38.94, 153.2), Vector3(304.6, 39.3, 154.8)]
	pts.append(zone.spawn_marker(&"SpireBase").position)
	var end := walk("into the hall", pts, start.y)
	assert_true(absf(end - HALL_Y) < 0.1, "on the hall floor (y %.2f)" % end)
	close()


func test_the_path_reaches_the_hearth_through_the_hut_door() -> void:
	var start := Vector3(303.4, 38.9, 151.6)
	var pts: Array[Vector3] = [start, _mark(&"way_forecourt_e"), _mark(&"way_hut_door_out"), _mark(&"way_hut_door_in")]
	pts.append((zone.get_node(^"Triggers/hearth") as Node3D).position)
	var end := walk("to the hearth", pts, start.y)
	assert_true(end > 38.5, "on the hut's floor (y %.2f)" % end)
	close()


func test_the_crown_stair_comes_out_on_the_gallery() -> void:
	var top := _mark(&"way_f5_10")
	var pts: Array[Vector3] = [top, _mark(&"way_gallery_door"), zone.spawn_marker(&"Gallery").position]
	var end := walk("out on to the gallery", pts, top.y)
	assert_true(absf(end - GALLERY_Y) < 0.1, "on the gallery (y %.2f)" % end)
	close()


func test_every_flight_climbs_to_its_top() -> void:
	for g in GATES:
		zone.hide_block(g)
	read_boxes()
	var ramps: Array = GreyboxZone.read_json(COLLISION).get("ramps", [])
	for f in range(1, FLIGHTS + 1):
		var rows := ramps.filter(func(r: Dictionary) -> bool: return str(r["id"]).begins_with("Flight%d_" % f))
		rows.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return _tread(a) < _tread(b))
		var pts: Array[Vector3] = [GreyboxZone._vec3(rows[0]["from"])]
		for r: Dictionary in rows:
			pts.append(GreyboxZone._vec3(r["to"]))
		var top := pts[pts.size() - 1].y
		var end := walk("flight %d" % f, pts, pts[0].y)
		assert_true(absf(end - top) < 0.1, "flight %d reaches its top (y %.2f of %.2f)" % [f, end, top])
	close()


static func _tread(row: Dictionary) -> int:
	return int(str(row["id"]).get_slice("_", 1))
