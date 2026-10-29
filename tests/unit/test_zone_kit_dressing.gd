extends TestCase
## M3-C06-1200, ADR 0200: ZoneKitDressing swaps an Act I greybox zone's look for env-art's kit and leaves
## the gameplay alone. Ch6's Brine Shoals is the first zone dressed: its greybox meshes hide (the kept story
## blocks stay), their collision stays, a story block's kit pieces show and hide with the block, the decor
## off the route collides, and the zone takes the kit's grade.

const SHOALS := "res://game/levels/ch06/brine_shoals/brine_shoals.tscn"
const DRESSING := "res://game/levels/ch06/brine_shoals/brine_shoals_dressing.json"

## ADR 0041: no greybox on Act I's played path. Each dressed zone may keep only the blocks that wait on another track's
## asset (the request named), and every piece it places, from any kit, exists.
const ACT1_DRESSINGS := {
	"res://game/levels/ch04/brightwater_ferry/brightwater_ferry_dressing.json": [],
	"res://game/levels/ch05/pemakar/pemakar_dressing.json": [],
	"res://game/levels/ch06/brine_shoals/brine_shoals_dressing.json": [],
	"res://game/levels/ch07/tamsule/tamsule_dressing.json": [],
	"res://game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries_dressing.json": ["Column"],  # M3-RND-27
	"res://game/levels/ch08/corrow/corrow_dressing.json": [],
	"res://game/levels/ch08/coilspire/coilspire_dressing.json": [],  # Virel is her own body (M3-CRE-700)
	"res://game/levels/ch09/corrow_night/corrow_night_dressing.json": [],
}

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
		var glb := String(spec.get("kit_dir", kit)) + String(spec["piece"]) + ".glb"
		if not seen.has(glb):
			seen[glb] = true
			assert_true(ResourceLoader.exists(glb), "%s is a kit piece" % glb)
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
	assert_eq(fires.size(), 5, "the hulk, the brazier, the dusk fire, the burning tide-wheel and the shrine")
	for l: Node in fires:
		assert_eq((l as OmniLight3D).light_volumetric_fog_energy, 0.0, "fog-lamp rule")
	_close()


func test_a_trimesh_collider_takes_the_lod1_mesh() -> void:
	var piece := (
		(load("res://assets/environments/kits/brine_shoals/camp_hard.glb") as PackedScene).instantiate() as Node3D
	)
	var body := ZoneKitDressing.trimesh_collider(piece)
	assert_eq(body.get_child_count(), 1, "one shape: the LOD1, not both LODs")
	var shape := (body.get_child(0) as CollisionShape3D).shape as ConcavePolygonShape3D
	assert_true(shape != null and shape.get_faces().size() > 9, "a trimesh with faces")
	body.free()
	piece.free()
	_close()


func test_a_trimesh_lod0_collider_takes_the_lod0_mesh() -> void:
	var piece := (
		(load("res://assets/environments/kits/brine_shoals/camp_hard.glb") as PackedScene).instantiate() as Node3D
	)
	var lod1 := ZoneKitDressing.trimesh_collider(piece)
	var lod0 := ZoneKitDressing.trimesh_collider(piece, false)
	assert_eq(lod0.get_child_count(), 1, "one shape: the LOD0")
	var faces0 := ((lod0.get_child(0) as CollisionShape3D).shape as ConcavePolygonShape3D).get_faces().size()
	var faces1 := ((lod1.get_child(0) as CollisionShape3D).shape as ConcavePolygonShape3D).get_faces().size()
	assert_true(faces0 > faces1, "the finer mesh (%d faces against %d)" % [faces0, faces1])
	lod0.free()
	lod1.free()
	piece.free()
	_close()


func test_a_lod0_box_clips_lod1_out_and_lod0_in() -> void:
	# a 2 x 2 m triangle pair (a quad in y = 0) and a box over its middle: the outside and the inside add up to it
	var quad := PackedVector3Array(
		[
			Vector3(-1, 0, -1),
			Vector3(1, 0, -1),
			Vector3(1, 0, 1),
			Vector3(-1, 0, -1),
			Vector3(1, 0, 1),
			Vector3(-1, 0, 1)
		]
	)
	var boxes := ZoneKitDressing.lod0_boxes([{"pos": [0.0, 0.0, 0.0], "size": [1.0, 1.0, 1.0], "yaw": 45.0}])
	var outside := ZoneKitDressing._clip_faces(quad, Transform3D.IDENTITY, boxes, false)
	var inside := ZoneKitDressing._clip_faces(quad, Transform3D.IDENTITY, boxes, true)
	assert_true(absf(_area(inside) - 1.0) < 1e-4, "the box's 1 m^2 inside (%.4f)" % _area(inside))
	assert_true(absf(_area(outside) - 3.0) < 1e-4, "the rest outside (%.4f)" % _area(outside))
	for p in inside:
		assert_true(absf(p.rotated(Vector3.UP, deg_to_rad(-45.0)).x) <= 0.5001, "inside stays in the turned box")
	_close()


static func _area(faces: PackedVector3Array) -> float:
	var total := 0.0
	for i in range(0, faces.size(), 3):
		total += (faces[i + 1] - faces[i]).cross(faces[i + 2] - faces[i]).length() * 0.5
	return total


func test_act1_dressings_keep_only_blocks_that_wait_on_a_request() -> void:
	_close()
	for path: String in ACT1_DRESSINGS:
		var layout := HalunaDresser._load_json(path)
		var keep: Array = (layout.get("greybox", {}) as Dictionary).get("keep", [])
		for id: Variant in keep:
			assert_true((ACT1_DRESSINGS[path] as Array).has(id), "%s keeps %s, which waits on no request" % [path, id])
		var kit := String(layout["kit_dir"])
		var seen: Dictionary = {}
		for spec: Dictionary in layout["pieces"]:
			var glb := String(spec.get("kit_dir", kit)) + String(spec["piece"]) + ".glb"
			if not seen.has(glb):
				seen[glb] = true
				assert_true(ResourceLoader.exists(glb), "%s: %s exists" % [path, glb])
