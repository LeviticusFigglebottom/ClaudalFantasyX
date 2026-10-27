extends TestCase
## M3-ENV-710: the Prologue's Iskarra city (assets/environments/zones/iskarra/iskarra_city.tscn) after the real
## import: every piece instances its kit glb, every surface wears the kit's .tres of its slot (the Haluna
## post-import), and the towers carry their LOD1 chain.

const CITY := "res://assets/environments/zones/iskarra/iskarra_city.tscn"
const MATERIAL_DIR := "res://assets/environments/kits/haluna/materials/"
const MIN_PIECES := 19


func _meshes(root: Node) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	for n in root.find_children("*", "MeshInstance3D", true, false):
		out.append(n as MeshInstance3D)
	return out


func test_the_city_instances_its_pieces_with_kit_materials() -> void:
	var packed := load(CITY) as PackedScene
	assert_true(packed != null, "the city scene loads")
	if packed == null:
		return
	var city := packed.instantiate()
	assert_true(city.get_child_count() >= MIN_PIECES, "every piece is placed (%d)" % city.get_child_count())
	for piece in city.get_children():
		var meshes := _meshes(piece)
		assert_true(not meshes.is_empty(), "%s has meshes" % piece.name)
		for mi in meshes:
			for i in mi.mesh.get_surface_count():
				var mat := mi.get_active_material(i)
				assert_true(mat != null, "%s/%s surface %d has a material" % [piece.name, mi.name, i])
				if mat != null:
					assert_true(mat.resource_path.begins_with(MATERIAL_DIR), "%s wears a kit material" % mi.name)
	var lods := city.get_node("TowerA").find_children("*-lod1", "MeshInstance3D", true, false)
	assert_true(not lods.is_empty(), "the spire carries its LOD1")
	city.free()
