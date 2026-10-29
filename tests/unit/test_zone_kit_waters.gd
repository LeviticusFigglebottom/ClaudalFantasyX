extends TestCase
## ADR 0200, env-art-b: ZoneKitDressing's "waters" rows make the story's water real. Ch8's Corrow kept two greybox
## planes for the storm's flood in the lanes and the lake the low town drowns in; each is now a WaterSurface over the
## block's footprint at its top, hidden and shown with its block by the states rows, and none of them publishes the
## water level (the zone's sea does).

const CORROW := "res://game/levels/ch08/corrow/corrow.tscn"

var zone: GreyboxZone


func before_each() -> void:
	_close()
	Game.new_game()
	zone = (load(CORROW) as PackedScene).instantiate() as GreyboxZone
	zone.story.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		zone.get_parent().remove_child(zone)
		zone.free()  # a publishing WaterSurface must go before the test returns
	zone = null


func _water(block_id: String) -> WaterSurface:
	for n: Node3D in (zone.get_node(^"Dressing") as ZoneKitDressing).followers(block_id):
		if n is WaterSurface:
			return n as WaterSurface
	return null


func test_the_flood_and_the_lake_are_water_on_their_blocks() -> void:
	for id: String in ["Flood", "Lake"]:
		var water := _water(id)
		assert_true(water != null, "%s has a WaterSurface" % id)
		var b := zone.get_node(NodePath("Greybox/%s" % id)) as Node3D
		var mesh := (b.get_node(^"Mesh") as MeshInstance3D).mesh as BoxMesh
		var top := b.global_position.y + mesh.size.y * 0.5
		assert_between(water.global_position.y, top - 0.001, top + 0.6, "%s at its top or lifted over it" % id)
		var plane := water.surface_mesh as PlaneMesh
		assert_between(plane.size.x, mesh.size.x - 0.001, mesh.size.x + 0.001, "%s spans its block (x)" % id)
		assert_between(plane.size.y, mesh.size.z - 0.001, mesh.size.z + 0.001, "%s spans its block (z)" % id)
		assert_false(water.publishes_water_level, "%s never drives the zone's weathering" % id)
		assert_false((b.get_node(^"Mesh") as MeshInstance3D).visible, "the greybox plane is hidden")
	_close()


func test_the_waters_follow_the_story() -> void:
	var flood := _water("Flood")
	assert_false(flood.is_visible_in_tree(), "no flood before the third wave")
	zone.show_block("Flood")
	assert_true(flood.is_visible_in_tree(), "the flood comes with its block")
	zone.hide_block("Flood")
	assert_false(flood.is_visible_in_tree(), "and goes with it")
	_close()


func test_a_shown_storm_is_inside_the_camera_far_plane() -> void:
	# The Undertow stands 10-14 km out and a Camera3D's default far is 4 km: the dressing raises the current camera's
	# far plane past every shown storm (StormFarPlane), so the field and cutscene cameras see it.
	var dressing := zone.get_node(^"Dressing") as ZoneKitDressing
	var storm: UndertowStorm = null
	for n: Node3D in dressing.followers("Storm"):
		if n is UndertowStorm:
			storm = n as UndertowStorm
	assert_true(storm != null, "Corrow's storm follows the Storm block")
	var cam := zone.get_viewport().get_camera_3d()
	assert_true(cam != null, "the zone has a current camera")
	cam.far = 4000.0
	storm.visible = true
	(storm.get_node(^"FarPlane") as StormFarPlane)._process(0.0)
	assert_true(cam.far > storm.approach_distance_m + storm.state.bound_radius(), "far %.0f m" % cam.far)
	_close()
