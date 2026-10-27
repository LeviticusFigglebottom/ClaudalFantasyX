extends KitWalkProbe
## M3-C07-1211, ADR 0200: ch07/tamsule_bell_galleries on env-art's Tamsule Bell kit is walkable where the story walks
## (KitWalkProbe): from the party's gallery along the west walkway, down Oruvel's platform to the pool steps, the rim's
## trigger and up on to the prow; from the catch-pool spawn back up and round the walkway to the moorings' bridge, down
## to the staging and Tavi's trigger; and from the entrance to the way back to the port. Every mark and actor the
## party or the captains stand on is on a floor.

const BELL := "res://game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn"
const WALK_R := 32.8
const WALK_DECK_Y := 2.4
const DECK_Y := 2.0
const PROW_Y := 2.46
const BOARD_Y := 1.6
const OURS := 270.0
const MOORINGS_AZ := 325.0
const ARC_STEP_DEG := 5.0
const ON_FLOORS: Array[StringName] = [
	&"asha_rim",
	&"toma_rim",
	&"liss_rim",
	&"ysolde_rim",
	&"rhen_moorings",
	&"asha_ring_1",
	&"asha_ring_3",
	&"asha_ring_6",
	&"rhen_ring_6",
	&"tavi_boat",
	&"asha",
	&"toma",
	&"liss",
	&"ysolde",
	&"tavi",
	&"ione",
]


func before_each() -> void:
	open(BELL)


## The kit's arena frame: azimuth clockwise from north (-Z).
static func polar(r: float, az_deg: float, y: float = 0.0) -> Vector3:
	var a := deg_to_rad(az_deg)
	return Vector3(r * sin(a), y, -r * cos(a))


func _trigger(id: String) -> Vector3:
	return (zone.get_node(NodePath("Triggers/%s" % id)) as Node3D).position


func _on_walkway(from_az: float, to_az: float) -> Array[Vector3]:
	var out: Array[Vector3] = []
	var n := ceili(absf(to_az - from_az) / ARC_STEP_DEG)
	for i in n + 1:
		out.append(polar(WALK_R, lerpf(from_az, to_az, float(i) / n)))
	return out


func test_the_party_walks_from_the_gallery_down_to_the_prow() -> void:
	var start := zone.spawn_marker(&"Gallery").position
	var pts: Array[Vector3] = [start]
	pts.append_array(_on_walkway(262.0, OURS))
	pts.append_array([polar(30.0, OURS), zone.spawn_marker(&"PoolSteps").position, _trigger("rim"), polar(14.4, OURS)])
	var end := walk("to the prow", pts, start.y)
	assert_true(absf(end - PROW_Y) < 0.05, "on the prow step (y %.2f)" % end)
	close()


func test_the_catch_pool_spawn_reaches_the_moorings() -> void:
	var start := zone.spawn_marker(&"CatchPool").position
	var pts: Array[Vector3] = [start, polar(30.0, OURS)]
	pts.append_array(_on_walkway(OURS, MOORINGS_AZ))
	pts.append_array([polar(26.0, MOORINGS_AZ), _trigger("moorings")])
	var end := walk("to the moorings", pts, start.y)
	assert_true(absf(end - BOARD_Y) < 0.05, "on the staging (y %.2f)" % end)
	close()


func test_the_entrance_reaches_the_way_to_the_port() -> void:
	var start := zone.spawn_marker(&"Entrance").position
	var end := walk("to the port", [start, _trigger("to_port")] as Array[Vector3], start.y)
	assert_true(absf(end - WALK_DECK_Y) < 0.05, "on the walkway (y %.2f)" % end)
	close()


func test_the_party_and_the_captains_stand_on_a_floor() -> void:
	for id in ON_FLOORS:
		var m := zone.stage.mark(id)
		var p := m.position if m != null else zone.stage.actor(id).position
		var f := floor_y(p.x, p.z, p.y + 0.3)
		assert_true(absf(f - p.y) < 0.35, "%s stands on a floor (y %.2f, floor %.2f)" % [id, p.y, f])
		assert_eq(blocked_by(Vector3(p.x, f, p.z)), "", "%s has room to stand" % id)
	close()
