extends TestCase
## M3-AUD-811: HalunaDresser builds FootstepAudio's surface areas from the layout's "footstep_surfaces": the dock is
## wood over the lagoon's water, the beach stays the scene's sand. The areas sense nothing and sit outside the
## pieces HalunaCollision reads.

const LAYOUT := "res://game/levels/ch02/haluna/haluna_layout.json"


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _dresser() -> HalunaDresser:
	var dresser := HalunaDresser.new()
	dresser.layout = HalunaDresser._load_json(LAYOUT)
	_host().add_child(dresser)
	dresser._place_footstep_surfaces(dresser.layout.get("footstep_surfaces", {}))
	return dresser


## The world point `local` metres along the dock piece's own frame.
func _on_dock(dresser: HalunaDresser, local: Vector3) -> Vector3:
	for spec: Dictionary in dresser.layout["pieces"]:
		if spec["piece"] == "dock_haluna":
			var at: Array = spec["at"]
			var basis := Basis(Vector3.UP, deg_to_rad(float(spec["yaw_deg"])))
			return Vector3(float(at[0]), float(spec["y"]), float(at[1])) + basis * local
	return Vector3.INF


func _surface(dresser: HalunaDresser, at: Vector3) -> StringName:
	var table := AudioData.table(AudioData.FOOTSTEPS) as Dictionary
	return FootstepAudio.surface_at(table, dresser.get_tree(), at, &"sand")


func test_the_dock_is_wood_and_the_shallows_water() -> void:
	var dresser := _dresser()
	for x: float in [1.0, 19.0, 37.0]:
		assert_eq(_surface(dresser, _on_dock(dresser, Vector3(x, 1.4, 0.0))), &"wood", "the deck at %.0f m" % x)
	assert_eq(_surface(dresser, _on_dock(dresser, Vector3(36.0, 1.4, 1.8))), &"wood", "the end platform")
	assert_eq(_surface(dresser, _on_dock(dresser, Vector3(19.0, -0.4, 3.5))), &"water", "wading beside the dock")
	assert_eq(_surface(dresser, Vector3(-20.0, 0.6, 0.0)), &"sand", "the beach above the water stays sand")
	dresser.free()


func test_the_areas_sense_nothing_and_stay_off_the_pieces() -> void:
	var dresser := _dresser()
	var areas := dresser.footstep_surfaces()
	assert_eq(areas.size(), (dresser.layout["footstep_surfaces"]["areas"] as Array).size())
	for a: Area3D in areas:
		assert_eq(a.collision_layer, 0, a.name)
		assert_eq(a.collision_mask, 0, a.name)
		assert_false(a.monitoring, a.name)
		assert_true(a.is_in_group(&"footstep_surface"), a.name)
		assert_false(a.get_parent() is Node3D, "under a plain Node: HalunaCollision reads Node3D children as pieces")
	dresser.free()
