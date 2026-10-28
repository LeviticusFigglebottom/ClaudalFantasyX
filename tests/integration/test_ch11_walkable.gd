extends KitWalkProbe
## M4-C11-02: Ch11's greybox zones are walkable where the story walks (KitWalkProbe on their boxes and ramps): Sunken
## Vey from the landing along the galleries through the conduit court (to the housing-mark) to Lowlight's gate, and up
## the side gallery to the fig; Lowlight from the gate across the atrium into the Lamp Engine's hall, and down the
## well-shaft's two flights to the drowned sanctum (Nhoa's mark).

const VEY := "res://game/levels/ch11/sunken_vey/sunken_vey.tscn"
const LOWLIGHT := "res://game/levels/ch11/lowlight/lowlight.tscn"
const SANCTUM_Y := -8.0


func _mark(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_galleries_run_from_the_landing_to_lowlights_gate() -> void:
	open(VEY)
	var pts: Array[Vector3] = [
		zone.spawn_marker(&"Landing").position, Vector3(22, 0, 0), Vector3(33, 0, -8), Vector3(33, 0, -18)
	]
	pts.append(_mark(&"conduit_mark"))
	pts.append_array(
		[Vector3(42, 0, -22), Vector3(46, 0, -22), Vector3(70, 0, -16), Vector3(92, 0, -16)] as Array[Vector3]
	)
	var end := walk("the galleries", pts, 0.0)
	assert_true(absf(end) < 0.05, "on the gallery at the gate (y %.2f)" % end)
	walk("the side gallery", [Vector3(38, 0, -24), Vector3(38, 0, -50), _mark(&"fig_end")] as Array[Vector3], 0.0)
	close()


func test_lowlight_goes_down_the_shaft_to_the_sanctum() -> void:
	open(LOWLIGHT)
	var gate := zone.spawn_marker(&"Gate").position
	walk(
		"into the hall",
		[gate, Vector3(10, 0, 0), Vector3(10, 0, -14), zone.spawn_marker(&"EngineHall").position] as Array[Vector3],
		0.0
	)
	var pts: Array[Vector3] = [gate, Vector3(14, 0, 4), Vector3(20, 0, 4), Vector3(36, -4, 4), Vector3(40, -4, 4)]
	pts.append_array([Vector3(56, SANCTUM_Y, 4), _mark(&"nhoa")] as Array[Vector3])
	var end := walk("down the shaft", pts, 0.0)
	assert_true(absf(end - SANCTUM_Y) < 0.1, "on the sanctum's floor (y %.2f)" % end)
	close()
