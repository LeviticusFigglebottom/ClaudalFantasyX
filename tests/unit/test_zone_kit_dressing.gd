extends TestCase
## M3-C06-1200, ADR 0200: ZoneKitDressing swaps an Act I greybox zone's look for env-art's kit and leaves
## the gameplay alone. Ch6's Brine Shoals is the first zone dressed: its greybox meshes hide (the kept story
## blocks stay), their collision stays, a story block's kit pieces show and hide with the block, the decor
## off the route collides, and the zone takes the kit's grade.

const SHOALS := "res://game/levels/ch06/brine_shoals/brine_shoals.tscn"
const DRESSING := "res://game/levels/ch06/brine_shoals/brine_shoals_dressing.json"

var zone: Ch06Zone


func before_each() -> void:
	_close()
	Game.new_game()
	zone = (load(SHOALS) as PackedScene).instantiate() as Ch06Zone
	zone.story.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		zone.get_parent().remove_child(zone)
		zone.free()  # a publishing WaterSurface must go before the test returns
	zone = null


func _dressing() -> ZoneKitDressing:
	return zone.get_node(^"Dressing") as ZoneKitDressing


func test_the_greybox_hides_but_keeps_its_collision() -> void:
	var layout := HalunaDresser._load_json(DRESSING)
	var keep: Array = layout["greybox"]["keep"]
	for b: Node in zone.get_node(^"Greybox").get_children():
		var mesh := b.get_node(^"Mesh") as MeshInstance3D
		assert_eq(mesh.visible, keep.has(String(b.name)), "%s: hidden unless kept" % b.name)
		if b is StaticBody3D:
			assert_false((b.get_node(^"Shape") as CollisionShape3D).disabled, "%s still collides" % b.name)
	_close()


func test_every_kit_piece_and_every_block_id_exists() -> void:
	var layout := HalunaDresser._load_json(DRESSING)
	var kit := String(layout["kit_dir"])
	var seen: Dictionary = {}
	for spec: Dictionary in layout["pieces"]:
		var piece := String(spec["piece"])
		if not seen.has(piece):
			seen[piece] = true
			assert_true(ResourceLoader.exists(kit + piece + ".glb"), "%s is a kit piece" % piece)
		if spec.has("block"):
			assert_true(_dressing().block(String(spec["block"])) != null, "block %s exists" % spec["block"])
	assert_eq(_dressing().placed.get("plank_walk", 0) > 10, true, "the plank walk runs up the road")
	_close()


func test_story_pieces_follow_their_blocks() -> void:
	var barges := _dressing().followers("Barge")
	assert_eq(barges.size(), 1, "the kit's barge follows the Barge block")
	var kit_barge := barges[0]
	assert_true(kit_barge.global_position.distance_to(Vector3(-22.5, -0.15, -44.0)) < 0.01, "where the layout puts it")
	zone.show_block("Barge")
	assert_true(kit_barge.is_visible_in_tree(), "shown with the block")
	zone.hide_block("Barge")
	assert_false(kit_barge.is_visible_in_tree(), "hidden with the block")
	assert_eq(_dressing().followers("Smoke").size(), 4, "three plumes and the hulk's fire")
	zone.hide_block("Smoke")
	for n: Node3D in _dressing().followers("Smoke"):
		assert_false(n.visible, "%s goes out with the Smoke block at dusk" % n.name)
	_close()


func test_decor_off_the_route_collides() -> void:
	var colliders := 0
	for c: Node in _dressing().get_children():
		if c.get_node_or_null(NodePath(String(ZoneKitDressing.COLLIDER))) != null:
			var shape := c.get_node(NodePath(String(ZoneKitDressing.COLLIDER))).get_child(0) as CollisionShape3D
			assert_true((shape.shape as BoxShape3D).size.length() > 0.5, "%s has a real box" % c.name)
			colliders += 1
	assert_true(colliders >= 8, "the wrecks and the burned camp collide")
	_close()


func test_the_zone_takes_the_kit_grade_and_lamps_obey_the_fog_rule() -> void:
	var env := (zone.get_node(^"WorldEnvironment") as WorldEnvironment).environment
	assert_eq(env.background_mode, Environment.BG_SKY, "the kit's sky")
	assert_true(env.adjustment_enabled and env.adjustment_color_correction != null, "the ch06 LUT")
	var fires := _dressing().find_children("*", "OmniLight3D", true, false)
	assert_eq(fires.size(), 3, "the hulk, the brazier and the dusk fire")
	for l: Node in fires:
		assert_eq((l as OmniLight3D).light_volumetric_fog_energy, 0.0, "fog-lamp rule")
	_close()
