extends TestCase
## M2-CHR-01: the hero review stage (asha_stage.gd) serving Rhen. The instanced character takes the
## stage's name, every glTF material that has a hero material is replaced by it, and an emotion
## resolves through Rhen's pose table (his crooked smile: the right corner higher, the right dimple).
## M2-CHR-02: the same stage serving Toma (his smile read through the cheeks and lids; the beard cards
## in the Head share its blendshapes).

const RHEN_STAGE := "res://game/levels/_tests/characters/rhen/rhen_stage.tscn"
const RHEN_SMILE := "res://game/levels/_tests/characters/rhen/rhen_face_smile.tscn"
const TOMA_STAGE := "res://game/levels/_tests/characters/toma/toma_stage.tscn"
const TOMA_SMILE := "res://game/levels/_tests/characters/toma/toma_face_smile.tscn"


func test_rhen_stage_names_the_character_and_assigns_every_material() -> void:
	var stage := (load(RHEN_STAGE) as PackedScene).instantiate() as AshaStage
	_host().add_child(stage)
	var rhen := stage.find_child("Rhen", true, false)
	assert_true(rhen != null, "the character is named after the stage's character_name")
	var missing: Array[String] = []
	var assigned := 0
	for mi: MeshInstance3D in _meshes(rhen):
		for s: int in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			if src == null:
				continue
			if not stage.materials.has(src.resource_name):
				missing.append(src.resource_name)
			elif mi.get_surface_override_material(s) != null:
				assigned += 1
	assert_eq(missing, [] as Array[String], "every glTF material has a hero material")
	assert_true(assigned > 0, "hero materials assigned")
	for cam: String in ["Front", "ThreeQuarterLeft", "Profile", "Back", "Face"]:
		assert_true(stage.get_node_or_null("Cameras/%s" % cam) is Camera3D, cam)
	stage.free()


func test_rhen_smile_is_crooked() -> void:
	var stage := (load(RHEN_SMILE) as PackedScene).instantiate() as AshaStage
	_host().add_child(stage)
	var weights := {}
	for mi: MeshInstance3D in _meshes(stage):
		var mesh := mi.mesh as ArrayMesh
		if mesh == null or mesh.get_blend_shape_count() == 0:
			continue
		for i: int in mesh.get_blend_shape_count():
			weights[String(mesh.get_blend_shape_name(i))] = mi.get_blend_shape_value(i)
	assert_true(weights.has("mouth_smile_L"), "the head has the shared shapes")
	if weights.has("mouth_smile_L"):
		assert_true(float(weights["mouth_smile_R"]) > float(weights["mouth_smile_L"]), "right corner higher")
		assert_between(float(weights["mouth_dimple_R"]), 0.29, 0.31, "right dimple")
		assert_between(float(weights["mouth_dimple_L"]), -0.01, 0.01, "no left dimple")
	stage.free()


func test_toma_stage_names_the_character_and_assigns_every_material() -> void:
	var stage := (load(TOMA_STAGE) as PackedScene).instantiate() as AshaStage
	_host().add_child(stage)
	var toma := stage.find_child("Toma", true, false)
	assert_true(toma != null, "the character is named after the stage's character_name")
	var missing: Array[String] = []
	var names := {}
	for mi: MeshInstance3D in _meshes(toma):
		for s: int in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			if src == null:
				continue
			names[src.resource_name] = true
			if not stage.materials.has(src.resource_name):
				missing.append(src.resource_name)
	assert_eq(missing, [] as Array[String], "every glTF material has a hero material")
	for m: String in ["beard", "beard_grey", "shield", "bronze", "steel", "cloth"]:
		assert_true(names.has(m), m)
	for cam: String in ["Front", "ThreeQuarterLeft", "Profile", "Back", "Face"]:
		assert_true(stage.get_node_or_null("Cameras/%s" % cam) is Camera3D, cam)
	stage.free()


func test_toma_smile_reads_through_cheeks_and_lids() -> void:
	var stage := (load(TOMA_SMILE) as PackedScene).instantiate() as AshaStage
	_host().add_child(stage)
	var weights := {}
	for mi: MeshInstance3D in _meshes(stage):
		var mesh := mi.mesh as ArrayMesh
		if mesh == null or mesh.get_blend_shape_count() == 0:
			continue
		for i: int in mesh.get_blend_shape_count():
			weights[String(mesh.get_blend_shape_name(i))] = mi.get_blend_shape_value(i)
	assert_true(weights.has("cheek_raise_L"), "the head has the shared shapes")
	if weights.has("cheek_raise_L"):
		assert_between(float(weights["cheek_raise_L"]), 0.54, 0.56, "cheek raise (toma.md §6)")
		assert_between(float(weights["lid_squint_R"]), 0.34, 0.36, "lid squint")
		assert_between(float(weights["mouth_smile_L"]), 0.59, 0.61, "symmetric smile")
		assert_between(float(weights["mouth_smile_R"]), 0.59, 0.61, "symmetric smile")
	stage.free()


func _meshes(root: Node) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	if root == null:
		return out
	for n: Node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh != null:
			out.append(mi)
	return out


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
