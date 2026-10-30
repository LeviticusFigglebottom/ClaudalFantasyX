extends TestCase
## M2-CHR-01: the hero review stage (asha_stage.gd) serving Rhen. The instanced character takes the
## stage's name, every glTF material that has a hero material is replaced by it, and an emotion
## resolves through Rhen's pose table (his crooked smile: the right corner higher, the right dimple).
## M2-CHR-02: the same stage serving Toma (his smile read through the cheeks and lids; the beard cards
## in the Head share its blendshapes).
## M3-CHR-01: the same stage serving Ysolde (her rest brow on every pose; the book fans open on its
## blend shape in cast_glyph).

const RHEN_STAGE := "res://game/levels/_tests/characters/rhen/rhen_stage.tscn"
const RHEN_SMILE := "res://game/levels/_tests/characters/rhen/rhen_face_smile.tscn"
const TOMA_STAGE := "res://game/levels/_tests/characters/toma/toma_stage.tscn"
const TOMA_SMILE := "res://game/levels/_tests/characters/toma/toma_face_smile.tscn"
const YSOLDE_STAGE := "res://game/levels/_tests/characters/ysolde/ysolde_stage.tscn"
const YSOLDE_CAST := "res://game/levels/_tests/characters/ysolde/ysolde_clip_cast_glyph.tscn"
## ADR 0140: the Lead's budget for the runtime skirt work, per hero per frame.
const FOLDS_BUDGET_MS := 0.2


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


func test_ysolde_stage_assigns_every_material_and_keeps_her_rest_brow() -> void:
	var stage := (load(YSOLDE_STAGE) as PackedScene).instantiate() as AshaStage
	_host().add_child(stage)
	var ysolde := stage.find_child("Ysolde", true, false)
	assert_true(ysolde != null, "the character is named after the stage's character_name")
	var missing: Array[String] = []
	var names := {}
	var weights := {}
	for mi: MeshInstance3D in _meshes(ysolde):
		for s: int in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			if src == null:
				continue
			names[src.resource_name] = true
			if not stage.materials.has(src.resource_name):
				missing.append(src.resource_name)
		var mesh := mi.mesh as ArrayMesh
		if mesh != null and mi.name == &"Head":
			for i: int in mesh.get_blend_shape_count():
				weights[String(mesh.get_blend_shape_name(i))] = mi.get_blend_shape_value(i)
	assert_eq(missing, [] as Array[String], "every glTF material has a hero material")
	for m: String in ["hair", "hair_grey", "hair_streak", "cloth", "props", "silver", "gold"]:
		assert_true(names.has(m), m)
	assert_true(weights.has("brow_outer_up_L"), "the head has the shared shapes")
	if weights.has("brow_outer_up_L"):
		assert_between(float(weights["brow_outer_up_L"]), 0.07, 0.09, "the left brow sits higher at rest")
		assert_between(float(weights["brow_outer_up_R"]), -0.01, 0.01, "the right brow at rest")
		assert_between(float(weights["mouth_press"]), 0.09, 0.11, "the composed face presses the mouth")
	stage.free()


func test_ysolde_cast_glyph_holds_the_book_open() -> void:
	var stage := (load(YSOLDE_CAST) as PackedScene).instantiate() as AshaStage
	_host().add_child(stage)
	var book: MeshInstance3D = null
	for mi: MeshInstance3D in _meshes(stage):
		if mi.name == &"Book":
			book = mi
	assert_true(book != null, "the book is a mesh of its own")
	if book != null:
		var idx: int = book.find_blend_shape_by_name(&"book_fan")
		assert_true(idx >= 0, "the book has its book_fan shape")
		if idx >= 0:
			assert_between(book.get_blend_shape_value(idx), 0.99, 1.01, "fanned open while the glyph is traced")
	stage.free()


## M3-CHR-01: Ysolde's battle actor (her LOD1) shares her clips, and its book keeps the shape book_fan keys.
func test_ysolde_battle_actor_carries_her_clips_and_book() -> void:
	var node := (load("res://game/characters/heroes/ysolde_battle.tscn") as PackedScene).instantiate()
	var ap := node.find_child("AnimationPlayer", true, false) as AnimationPlayer
	assert_true(ap != null, "ysolde battle actor has the clips")
	if ap != null:
		for clip: StringName in [&"idle", &"book_fan", &"cast_glyph"]:
			assert_true(ap.has_animation(clip), String(clip))
	var book := node.find_child("Book", true, false) as MeshInstance3D
	assert_true(book != null and book.find_blend_shape_by_name(&"book_fan") >= 0, "the LOD1 book can fan open")
	node.free()


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


## M2-CHR-06: the battle-scale hero scenes instance the LOD1 model, which the import rule gives the hero's clips.
func test_battle_scale_heroes_carry_their_clips() -> void:
	for hero: String in ["asha", "rhen"]:
		var node := (load("res://game/characters/heroes/%s_battle.tscn" % hero) as PackedScene).instantiate()
		var ap := node.find_child("AnimationPlayer", true, false) as AnimationPlayer
		assert_true(ap != null and ap.has_animation(&"idle"), "%s battle actor plays idle" % hero)
		assert_true(node.find_child("Skeleton3D", true, false) != null, "%s battle actor is skinned" % hero)
		node.free()


## M2-CHR-05: a face variant replaces only the tags it lists; the default smile is unchanged.
func test_smile_variant_is_opt_in_data() -> void:
	var data: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://game/data/cutscene/asha_face_poses.json")
	)
	var variant: Dictionary = data["variants"]["duchenne_open"]
	assert_eq(variant.keys(), ["smile"], "the variant lists the smile only")
	assert_ne(variant["smile"], data["emotions"]["smile"], "and differs from the default")
	var stage := (
		(load("res://game/levels/_tests/characters/asha/asha_smile_variant_compare.tscn") as PackedScene).instantiate()
	)
	_host().add_child(stage)
	var compare := stage.find_child("AshaCompare", true, false)
	assert_true(compare != null, "the comparison character is built")
	stage.free()


## M1-CHR-15: HeroHelperBones (the stages' solve for hand-set poses) matches the helper keys the clips bake
## (ADR 0140: the even-numbered skirt panels, not baked, derived from the baked odd ones as HeroSkirtFolds does)
## (hero_clips.py's solve): the skirt panels and the shoulder correctives, within a degree, and the lowest panel bones'
## floor gathers (scales) within 0.03.
## Sampled on 15 fps keys: between keys the baked helpers interpolate while the solve sees the interpolated body.
func test_helper_bones_match_the_baked_clips() -> void:
	for spec: Array in [
		["asha", &"kneel_over_rhen", 1.6], ["asha", &"walk", 0.6], ["asha", &"run", 0.4], ["toma", &"talk", 1.0]
	]:
		var model := (load("res://assets/characters/%s/%s.glb" % [spec[0], spec[0]]) as PackedScene).instantiate()
		_host().add_child(model)
		var skel := model.find_child("Skeleton3D", true, false) as Skeleton3D
		var ap := model.find_child("AnimationPlayer", true, false) as AnimationPlayer
		assert_true(HeroHelperBones.has_helpers(skel), "%s has helper bones" % spec[0])
		ap.play(spec[1])
		ap.seek(float(spec[2]), true)
		ap.pause()
		HeroHelperBones.apply_folds(skel, HeroHelperBones.fold_rig(skel))  # ADR 0140: what HeroSkirtFolds sets
		var baked := {}
		var baked_s := {}
		for i: int in skel.get_bone_count():
			var n := skel.get_bone_name(i)
			if n.begins_with("DEF-armpit.") or n.begins_with("DEF-skirt_"):
				baked[i] = skel.get_bone_pose_rotation(i)
				baked_s[i] = skel.get_bone_pose_scale(i)
				skel.set_bone_pose_rotation(i, skel.get_bone_rest(i).basis.get_rotation_quaternion())
				skel.set_bone_pose_scale(i, Vector3.ONE)
		HeroHelperBones.drive(skel)
		for i: int in baked:
			var err := rad_to_deg((baked[i] as Quaternion).angle_to(skel.get_bone_pose_rotation(i)))
			assert_true(err < 1.0, "%s %s %s: %.2f deg" % [spec[0], spec[1], skel.get_bone_name(i), err])
			var ds := ((baked_s[i] as Vector3) - skel.get_bone_pose_scale(i)).length()
			assert_true(ds < 0.03, "%s %s %s: scale off by %.3f" % [spec[0], spec[1], skel.get_bone_name(i), ds])
		model.free()


## ADR 0140: every imported Asha carries the HeroSkirtFolds modifier, the clips bake no even-numbered skirt panel, and
## the modifier sets those panels from the odd ones within the frame budget.
func test_skirt_folds_are_derived_at_runtime() -> void:
	var model := (load("res://assets/characters/asha/asha.glb") as PackedScene).instantiate()
	_host().add_child(model)
	var skel := model.find_child("Skeleton3D", true, false) as Skeleton3D
	assert_true(skel.get_node_or_null("SkirtFolds") is HeroSkirtFolds, "the import adds the folds modifier")
	var ap := model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	for lib_name: StringName in ap.get_animation_library_list():
		for clip: StringName in ap.get_animation_library(lib_name).get_animation_list():
			var anim := ap.get_animation_library(lib_name).get_animation(clip)
			for t: int in anim.get_track_count():
				var bone := String(anim.track_get_path(t).get_concatenated_subnames())
				var derived := bone.begins_with("DEF-skirt_") and int(bone.substr(10).get_slice(".", 0)) % 2 == 0
				assert_false(derived, "%s bakes a derived panel: %s" % [clip, bone])
	ap.play(&"kneel_over_rhen")
	ap.seek(1.6, true)
	ap.pause()
	var rig := HeroHelperBones.fold_rig(skel)
	var n := 200
	var t0 := Time.get_ticks_usec()
	for i: int in n:
		HeroHelperBones.apply_folds(skel, rig)
	var ms := float(Time.get_ticks_usec() - t0) / n / 1000.0
	assert_true(ms < FOLDS_BUDGET_MS, "apply_folds %.3f ms per hero" % ms)
	model.free()
