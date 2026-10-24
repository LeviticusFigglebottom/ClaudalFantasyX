extends TestCase
## M2-ENV-05: Haluna's entry work without changing a value. The walk collision reads the terrain's
## cached core heights (exactly height_at on those grid points), the terrain rows are filled in
## parallel, and the cast's materials load on the loader's threads during the prebuild and still
## land on every surface.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"


func test_cached_grid_heights_equal_height_at() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as HalunaZone
	zone.prebuild()
	var terrain := zone.get_node(^"HalunaMood/Terrain") as HalunaTerrain
	for p: Vector2 in [Vector2(-160, -130), Vector2(-15, -121), Vector2(0, 8), Vector2(40, 130), Vector2(-73, -19)]:
		# The mesh keeps 32-bit floats, as the heightmap does: equal at that precision.
		assert_eq(_f32(terrain.grid_height(p.x, p.y)), _f32(terrain.height_at(p.x, p.y)), "grid point %s" % p)
	var off := Vector2(-15.5, -121.25)
	assert_eq(terrain.grid_height(off.x, off.y), terrain.height_at(off.x, off.y), "off-grid falls back")
	var collision := zone.get_node(^"Collision") as HalunaCollision
	var hm := collision.heightmap
	var walk := collision.walk_rect
	var nx := hm.map_width
	for k: int in [0, 777, 12345, hm.map_data.size() - 1]:
		var x := walk.position.x + (k % nx) * collision.cell_m
		var z := walk.position.y + (k / nx) * collision.cell_m
		assert_eq(hm.map_data[k], _f32(terrain.height_at(x, z)), "the heightmap sample %d is height_at" % k)
	assert_true(zone.prebuild_msec > 0)
	zone.free()


func test_the_cast_gets_its_materials_through_the_threaded_load() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as HalunaZone
	zone.prebuild()
	var asha := zone.get_node(^"CutsceneStage/Actors/asha") as HalunaActorPose
	var checked := 0
	for n in asha.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			if src == null:
				continue
			var path := asha.materials_dir.path_join(src.resource_name + ".tres")
			if not ResourceLoader.exists(path):
				continue
			var got := mi.get_surface_override_material(s)
			assert_true(got != null and got.resource_path == path, "%s surface %d: %s" % [mi.name, s, path])
			checked += 1
	assert_true(checked > 5, "Asha's surfaces: %d" % checked)
	zone.free()


static func _f32(v: float) -> float:
	return PackedFloat32Array([v])[0]
