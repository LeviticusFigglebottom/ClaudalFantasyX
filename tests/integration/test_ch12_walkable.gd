extends KitWalkProbe
## M4-C12-02: Ch12's greybox zones are walkable where the story walks (KitWalkProbe on their boxes and ramps): Keth
## Pass from its foot up the three flights past the knotted post and the Ram's shelf to the saddle's way on; Quellan
## from the pass road along the street to the inn door and up the road north; Cloudloom up the stair into the
## weaving-hall and along its aisle to Hesk's dais.

const PASS := "res://game/levels/ch12/keth_pass/keth_pass.tscn"
const QUELLAN := "res://game/levels/ch12/quellan/quellan.tscn"
const CLOUDLOOM := "res://game/levels/ch12/cloudloom/cloudloom.tscn"


func _mark(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_pass_climbs_to_the_saddle() -> void:
	open(PASS)
	var pts: Array[Vector3] = [zone.spawn_marker(&"PassFoot").position, Vector3(0, 0, -6), Vector3(0, 6, -34)]
	pts.append_array(
		[Vector3(0, 6, -40), _mark(&"knot_post"), Vector3(0, 6, -40), Vector3(6, 6, -40)] as Array[Vector3]
	)
	pts.append_array(
		[Vector3(34, 12, -40), Vector3(56, 12, -40), Vector3(84, 18, -40), _mark(&"cold_ledge")] as Array[Vector3]
	)
	pts.append_array([Vector3(95, 18, -40), Vector3(108.5, 18, -40)] as Array[Vector3])
	var end := walk("up the pass", pts, 0.0)
	assert_true(absf(end - 18.0) < 0.1, "on the saddle's way on (y %.2f)" % end)
	close()


func test_quellans_street_reaches_the_inn_and_the_road_north() -> void:
	open(QUELLAN)
	var pts: Array[Vector3] = [zone.spawn_marker(&"FromPass").position, Vector3(32, 0, 0), _mark(&"inn_door")]
	pts.append_array(
		(
			[Vector3(32, 0, 0), Vector3(56, 0, 0), Vector3(56, 0, -4), Vector3(56, 8, -36), Vector3(56, 8, -42)]
			as Array[Vector3]
		)
	)
	var end := walk("the street and the road north", pts, 0.0)
	assert_true(absf(end - 8.0) < 0.1, "at the road's top (y %.2f)" % end)
	close()


func test_cloudlooms_stair_reaches_heskss_dais() -> void:
	open(CLOUDLOOM)
	var pts: Array[Vector3] = [zone.spawn_marker(&"Approach").position, Vector3(0, 0, -5), Vector3(0, 6, -20)]
	pts.append_array([Vector3(0, 6, -50), _mark(&"hesk")] as Array[Vector3])
	var end := walk("up to the hall", pts, 0.0)
	assert_true(end > 5.9, "in the hall (y %.2f)" % end)
	close()
