extends TestCase
## M3-ARC-1324: GraphicsRuntime.apply_system_tiers sets WaterSphereRig's (the Reefball ball, the Tamsule Bell's
## held drop) and SmokeColumn's (the Ch6 camp's smoke) tiers with the rest, so neither stays "high" on every preset.


func _scene() -> Node:
	var host := Node3D.new()
	var sphere := WaterSphereRig.new()
	sphere.name = "Sphere"
	host.add_child(sphere)
	var smoke := SmokeColumn.new()
	smoke.name = "Smoke"
	host.add_child(smoke)
	return host


func test_both_follow_a_preset_change() -> void:
	var host := _scene()
	var sphere := host.get_node("Sphere") as WaterSphereRig
	var smoke := host.get_node("Smoke") as SmokeColumn
	assert_eq(sphere.get_quality(), "high", "both start at their default")
	assert_eq(smoke.get_quality(), "high")
	assert_eq(GraphicsRuntime.apply_system_tiers(host, "low"), 2, "both change")
	assert_eq(sphere.get_quality(), "low")
	assert_eq(smoke.get_quality(), "low")
	assert_eq(GraphicsRuntime.apply_system_tiers(host, "low"), 0, "nothing left to change on a repeat")
	GraphicsRuntime.apply_system_tiers(host, "ultra")
	assert_eq(sphere.get_quality(), "ultra")
	assert_eq(smoke.get_quality(), "ultra")
	host.free()


func test_a_preset_with_no_row_leaves_them_as_they_are() -> void:
	var host := _scene()
	assert_eq(GraphicsRuntime.apply_system_tiers(host, "potato"), 0)
	assert_eq((host.get_node("Sphere") as WaterSphereRig).get_quality(), "high")
	assert_eq((host.get_node("Smoke") as SmokeColumn).get_quality(), "high")
	host.free()
