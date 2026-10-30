extends TestCase
## M4-A2P-050: CostumeVariant swaps one material slot (Merel's bloodied sleeve) and leaves the others alone.

const MEREL := "res://assets/characters/villagers/merel/merel.glb"
const BLOOD := "res://assets/characters/villagers/merel/materials/cloth_a_blood.tres"


func test_blood_variant_swaps_only_the_sleeve_slot() -> void:
	var merel := (load(MEREL) as PackedScene).instantiate()
	var blood := load(BLOOD) as Material
	assert_true(blood != null, "the bloodied material exists")
	var changed := CostumeVariant.apply(merel, &"cloth_a", blood)
	assert_true(changed >= 1, "at least the costume's cloth_a surface wears the stain")
	var others := 0
	for node: Node in merel.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			var worn := mi.get_active_material(i)
			if NpcTints.slot_of(mi, i) == &"cloth_a":
				assert_eq(worn, blood)
			elif worn == blood:
				others += 1
	assert_eq(others, 0, "no other slot wears the stain")
	merel.free()


func test_blood_albedo_differs_from_the_shared_atlas() -> void:
	var blood := load(BLOOD) as ShaderMaterial
	var plain := load("res://assets/characters/villagers/merel/materials/cloth_a.tres") as ShaderMaterial
	assert_ne(blood.get_shader_parameter(&"tex_albedo"), plain.get_shader_parameter(&"tex_albedo"))
	assert_eq(blood.get_shader_parameter(&"col_albedo"), plain.get_shader_parameter(&"col_albedo"))
