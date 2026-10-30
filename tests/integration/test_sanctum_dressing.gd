extends KitWalkProbe
## M4-A2P-043 (env-art-b): ch13/sanctum dressed in the greybox's frame (tools/act2/ch13_sanctum_dressing.py). The
## greybox keeps the collision: the party walks from the gate past the kneeling band and round the basin to the
## binding's place; the kit covers every greybox mesh; the basin holds the still water; the only lights are the bound
## light's, steady and with no specular point on the mirror.

const SANCTUM := "res://game/levels/ch13/sanctum/sanctum.tscn"
const FLOOR_Y := 0.0
const BOUND := Color("#4FB3B0")


func before_each() -> void:
	open(SANCTUM)


func test_the_gate_reaches_the_binding_round_the_basin() -> void:
	var start := zone.spawn_marker(&"Gate").position
	var pts: Array[Vector3] = [
		start, Vector3(0.0, 0.0, -15.0), Vector3(-8.0, 0.0, -15.0), Vector3(-8.0, 0.0, -42.0), Vector3(0.0, 0.0, -42.0)
	]
	var end := walk("to the binding", pts, start.y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on the nave floor at the far rim (y %.2f)" % end)
	close()


func test_the_kit_covers_the_greybox() -> void:
	var shown: Array[String] = []
	for n: Node in zone.get_node(^"Greybox").get_children():
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	close()


func test_the_basin_is_still_and_the_floor_is_the_only_light() -> void:
	var water := zone.get_node_or_null(^"Dressing/BasinWater") as WaterSurface
	assert_true(water != null, "the basin's water")
	if water != null:
		assert_eq(water.wave_set.amplitude_scale, 0.0, "no waves in the basin")
	var lights := zone.get_node(^"Dressing").find_children("*", "OmniLight3D", true, false)
	assert_true(lights.size() >= 4, "the bound light's omnis (%d)" % lights.size())
	for l: Node in lights:
		var o := l as OmniLight3D
		assert_true(o.light_color.is_equal_approx(BOUND), "%s is the bound light's colour" % o.name)
		assert_eq(o.light_specular, 0.0, "%s shows no point on the mirror" % o.name)
	close()
