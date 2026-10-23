extends TestCase
## M1-RND-04: character shaders (skin, hair, eye, cornea, eye helpers, cloth). Headless compile
## checks of every tier variant, the tier table and CharacterShaderTiers, the pre-integrated skin
## fit constants against their generator, the prewarm registry, and the test stage scene.

const TIERS_JSON := "res://game/shaders/character/character_shader_tiers.json"
const BRDF_INC := "res://game/shaders/character/character_brdf.gdshaderinc"
const WIND_INC := "res://game/shaders/character/character_wind.gdshaderinc"
const FIT_SCRIPT := "res://assets_src/characters/shader_test/preintegrated_skin_fit.py"
const PRESETS_JSON := "res://game/data/settings/graphics_presets.json"
const PREWARM_JSON := "res://game/data/settings/prewarm_materials.json"
const STAGE_SCENE := "res://game/levels/_tests/character_shading/shading_test.tscn"
const ASHA_STAGE := "res://game/levels/_tests/characters/asha/asha_stage.tscn"
const ASHA_CLOTH := "res://assets/characters/asha/materials/cloth.tres"
## Shadow normal bias that clears the shadow-terminator banding on Asha's cheeks at dialogue range
## (M1-QA-05 / M1-CHR-04 GPU sweep: 1.0 bands, 2.0 leaves a faint residue, 2.5 is clean on the cheek;
## M1-RND-20 raised it to 4.5 for the smiling mouth corner's fold, which still striped at 2.5 and 3.5).
const MIN_CLOSEUP_NORMAL_BIAS := 4.5
## Lacquered leather, not patent plastic (M1-CHR-04): the vest coat may not go back to a mirror.
const MIN_VEST_COAT_ROUGHNESS := 0.12
const FIT_TOLERANCE := 1e-6
const PREINT_U_MAX := 2.0

## Uniforms every variant of a family must expose (the material contract Character authors to).
const REQUIRED := {
	"skin": ["tex_albedo", "tex_skin_mask", "tex_detail_normal", "col_scatter", "painterly", "sss_strength"],
	"hair": ["tex_hair", "tex_hairflow", "spec_primary_shift", "spec_secondary_shift", "wind_response"],
	"eye": ["tex_iris", "ior", "anterior_depth_m", "iris_radius_m", "pupil_dilation"],
	"cloth": ["tex_cloth_mask", "sheen_roughness", "gold_anisotropy", "lacquer_coat_roughness", "verse_count"],
	"cloth_sheer": ["tex_band_id", "verse_count", "sleeve_dissolve", "transmission", "wind_response"],
	"mouth":
	["col_albedo", "tex_orm", "roughness", "specular", "ao_light_affect", "cavity_bounce", "col_cavity_bounce"],
}


## Counts shader compiler errors reported through the engine log while a check runs.
class ShaderErrorLog:
	extends Logger
	var count := 0
	var _mutex := Mutex.new()

	func _log_error(
		_function: String,
		_file: String,
		_line: int,
		code: String,
		rationale: String,
		_editor_notify: bool,
		error_type: int,
		_script_backtraces: Array[ScriptBacktrace]
	) -> void:
		var text := "%s %s" % [code, rationale]
		if error_type == Logger.ERROR_TYPE_SHADER or text.contains("Shader compilation failed"):
			_mutex.lock()
			count += 1
			_mutex.unlock()


# --- compile checks ------------------------------------------------------------------------------


func test_every_variant_compiles_and_exposes_the_contract() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	for fam: String in CharacterShaderTiers.families():
		for tier: String in CharacterShaderTiers.tiers():
			var path := CharacterShaderTiers.shader_path(fam, tier)
			assert_true(ResourceLoader.exists(path), "%s/%s missing: %s" % [fam, tier, path])
			var names := _uniform_names(load(path) as Shader)
			for u: String in REQUIRED[fam]:
				assert_true(names.has(u), "%s lacks uniform %s" % [path, u])
	for path: String in _table()["single_tier"]:
		assert_true(_uniform_names(load(path) as Shader).size() > 0, "%s did not compile" % path)
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler reported errors")


func test_tier_variants_share_one_uniform_set() -> void:
	# Swapping ShaderMaterial.shader between tiers must never drop an authored parameter.
	for fam: String in CharacterShaderTiers.families():
		var reference := _uniform_names(load(CharacterShaderTiers.shader_path(fam, "high")) as Shader)
		reference.sort()
		for tier: String in CharacterShaderTiers.tiers():
			var names := _uniform_names(load(CharacterShaderTiers.shader_path(fam, tier)) as Shader)
			names.sort()
			assert_eq(names, reference, "%s/%s uniforms differ from high" % [fam, tier])


func test_includes_compile_on_their_own() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var sources: Array[String] = [
		(
			"shader_type spatial;\n#define HYMN_QUALITY HYMN_QUALITY_LOW\n"
			+ '#include "%s"\nuniform float probe;\n' % BRDF_INC
			+ "void fragment() { ALBEDO = hymn_char_preint_skin(vec3(probe), probe)"
			+ " + vec3(hymn_char_kajiya_spec(NORMAL, VIEW, NORMAL, 8.0)); }\n"
		),
		(
			"shader_type spatial;\n"
			+ '#include "%s"\nuniform float probe;\n' % WIND_INC
			+ "void vertex() { VERTEX += hymn_char_wind_offset(VERTEX, NORMAL, COLOR, MODEL_MATRIX) * probe; }\n"
		),
	]
	for src in sources:
		var sh := Shader.new()
		sh.code = src
		assert_true(_uniform_names(sh).has("probe"), "compile failed for:\n%s" % src)
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler reported errors")


func test_verse_count_is_an_int_band_index_zero_to_seven() -> void:
	for fam: String in ["cloth", "cloth_sheer"]:
		var sh := load(CharacterShaderTiers.shader_path(fam, "high")) as Shader
		var found := false
		for u: Dictionary in sh.get_shader_uniform_list():
			if str(u["name"]) == "verse_count":
				found = true
				assert_eq(int(u["type"]), TYPE_INT, "verse_count is an int")
				var hint := _floats(str(u["hint_string"]))
				assert_true(hint.size() >= 2 and hint[0] == 0.0 and hint[1] == 7.0, "S0..S7 band range: %s" % hint)
		assert_true(found, "%s has verse_count" % fam)


# --- tier table and CharacterShaderTiers -------------------------------------------------------


func test_every_graphics_preset_maps_to_a_tier_every_family_has() -> void:
	var presets: Variant = JSON.parse_string(FileAccess.get_file_as_string(PRESETS_JSON))
	var ids: Array[String] = []
	for p: Variant in (presets as Dictionary)["presets"]:
		ids.append(str((p as Dictionary)["id"]))
	assert_eq(ids.size(), 4, "low, medium, high, ultra")
	for id in ids:
		var tier := CharacterShaderTiers.tier_for_preset(id)
		for fam: String in CharacterShaderTiers.families():
			assert_ne(CharacterShaderTiers.shader_path(fam, tier), "", "%s -> %s missing for %s" % [id, tier, fam])
	assert_eq(CharacterShaderTiers.tier_for_preset("low"), "low")
	assert_eq(CharacterShaderTiers.tier_for_preset("ultra"), "high", "ultra spends its budget on resolution")
	assert_eq(CharacterShaderTiers.tier_for_preset("no_such_preset"), str(_table()["default_tier"]))


func test_apply_tier_swaps_the_shader_and_keeps_parameters() -> void:
	var mat := ShaderMaterial.new()
	mat.shader = load(CharacterShaderTiers.shader_path("skin", "high")) as Shader
	mat.set_shader_parameter("painterly", 0.7)
	mat.set_shader_parameter("col_scatter", Color(0.5, 0.2, 0.1))
	assert_eq(CharacterShaderTiers.family_of(mat.shader), "skin")
	assert_true(CharacterShaderTiers.apply_tier(mat, "low"))
	assert_eq(mat.shader.resource_path, CharacterShaderTiers.shader_path("skin", "low"))
	assert_between(float(mat.get_shader_parameter("painterly")), 0.69, 0.71, "parameter survives the swap")
	assert_eq(mat.get_shader_parameter("col_scatter"), Color(0.5, 0.2, 0.1))
	assert_false(CharacterShaderTiers.apply_tier(mat, "low"), "already low")
	assert_false(CharacterShaderTiers.apply_tier(mat, "no_such_tier"))
	assert_false(CharacterShaderTiers.apply_tier(StandardMaterial3D.new(), "low"), "not a character shader")
	var cornea := ShaderMaterial.new()
	cornea.shader = load(str(_table()["single_tier"][0])) as Shader
	assert_false(CharacterShaderTiers.apply_tier(cornea, "low"), "single-tier shaders stay")


func test_apply_to_tree_visits_each_material_once() -> void:
	var root := Node3D.new()
	var shared := ShaderMaterial.new()
	shared.shader = load(CharacterShaderTiers.shader_path("hair", "high")) as Shader
	for i in 3:
		var mi := MeshInstance3D.new()
		mi.mesh = BoxMesh.new()
		mi.material_override = shared
		root.add_child(mi)
	var surf := MeshInstance3D.new()
	surf.mesh = BoxMesh.new()
	var cloth := ShaderMaterial.new()
	cloth.shader = load(CharacterShaderTiers.shader_path("cloth", "high")) as Shader
	surf.set_surface_override_material(0, cloth)
	root.get_child(0).add_child(surf)
	assert_eq(CharacterShaderTiers.apply_to_tree(root, "medium"), 2, "hair once + cloth once")
	# Copy-on-swap (M1-RND-19): the sources stay; the three hair slots share one copy.
	assert_eq(shared.shader.resource_path, CharacterShaderTiers.shader_path("hair", "high"), "source hair kept")
	assert_eq(cloth.shader.resource_path, CharacterShaderTiers.shader_path("cloth", "high"), "source cloth kept")
	var hair_copy := (root.get_child(0) as GeometryInstance3D).material_override as ShaderMaterial
	assert_true(hair_copy != shared, "hair copied")
	assert_eq(hair_copy.shader.resource_path, CharacterShaderTiers.shader_path("hair", "medium"))
	for i in 3:
		assert_true((root.get_child(i) as GeometryInstance3D).material_override == hair_copy, "one copy, shared")
	var cloth_copy := surf.get_surface_override_material(0) as ShaderMaterial
	assert_true(cloth_copy != cloth, "cloth copied")
	assert_eq(cloth_copy.shader.resource_path, CharacterShaderTiers.shader_path("cloth", "medium"))
	root.free()


## M1-RND-19: two instances share a material override and a mesh (whose surface material is the
## import-style shared slot) and take different tiers; neither the shared resources nor the other
## instance move, and a second swap reuses the instance's own copies.
func test_apply_to_tree_copies_shared_materials_per_instance() -> void:
	var skin := ShaderMaterial.new()
	skin.resource_name = "skin_head"
	skin.shader = load(CharacterShaderTiers.shader_path("skin", "high")) as Shader
	skin.set_shader_parameter("col_scatter", Color(0.5, 0.2, 0.1))
	var hair := ShaderMaterial.new()
	hair.shader = load(CharacterShaderTiers.shader_path("hair", "high")) as Shader
	var mesh := BoxMesh.new()
	mesh.material = hair
	var a := _sharing_instance(skin, mesh)
	var b := _sharing_instance(skin, mesh)
	assert_eq(CharacterShaderTiers.apply_to_tree(a, "low"), 2, "A: skin + the mesh's hair")
	assert_eq(CharacterShaderTiers.apply_to_tree(b, "medium"), 2, "B: skin + the mesh's hair")
	assert_eq(skin.shader.resource_path, CharacterShaderTiers.shader_path("skin", "high"), "shared skin untouched")
	assert_eq(hair.shader.resource_path, CharacterShaderTiers.shader_path("hair", "high"), "shared hair untouched")
	assert_true(mesh.surface_get_material(0) == hair, "the mesh keeps its material")
	for pair: Array in [[a, "low"], [b, "medium"]]:
		var root := pair[0] as Node3D
		var tier := str(pair[1])
		var head := root.get_node("Head") as MeshInstance3D
		var head_mat := head.material_override as ShaderMaterial
		assert_true(head_mat != skin, "%s: skin copied" % tier)
		assert_eq(head_mat.shader.resource_path, CharacterShaderTiers.shader_path("skin", tier))
		assert_eq(head_mat.resource_name, "skin_head", "%s: the copy keeps its slot name" % tier)
		assert_eq(head_mat.get_shader_parameter("col_scatter"), Color(0.5, 0.2, 0.1), "%s: params kept" % tier)
		assert_true(CharacterShaderTiers.owns(head_mat, root.get_instance_id()), "%s: owned by its root" % tier)
		var hair_mi := root.get_node("Hair") as MeshInstance3D
		var hair_mat := hair_mi.get_surface_override_material(0) as ShaderMaterial
		assert_true(hair_mat != null and hair_mat != hair, "%s: the mesh material is copied into the override" % tier)
		if hair_mat != null:
			assert_eq(hair_mat.shader.resource_path, CharacterShaderTiers.shader_path("hair", tier))
	# A second swap on A reuses A's own copies and leaves B alone.
	var a_head := a.get_node("Head") as MeshInstance3D
	var a_skin := a_head.material_override
	assert_eq(CharacterShaderTiers.apply_to_tree(a, "high"), 2, "A back to high")
	assert_true(a_head.material_override == a_skin, "an owned copy is swapped in place")
	var b_skin := (b.get_node("Head") as MeshInstance3D).material_override as ShaderMaterial
	assert_eq(b_skin.shader.resource_path, CharacterShaderTiers.shader_path("skin", "medium"), "B keeps its tier")
	# Another root (or a duplicate of an owned copy, meta and all) does not own it.
	assert_false(CharacterShaderTiers.owns(a_skin, b.get_instance_id()), "B does not own A's copy")
	assert_false(
		CharacterShaderTiers.owns(a_skin.duplicate() as Material, a.get_instance_id()), "a duplicate is not owned"
	)
	# Already at the tier: nothing to copy.
	var c := _sharing_instance(skin, mesh)
	assert_eq(CharacterShaderTiers.apply_to_tree(c, "high"), 0, "already high")
	assert_true((c.get_node("Head") as MeshInstance3D).material_override == skin, "no copy without a swap")
	assert_true((c.get_node("Hair") as MeshInstance3D).get_surface_override_material(0) == null, "no override added")
	for root: Node3D in [a, b, c]:
		root.free()


func _sharing_instance(skin: Material, mesh: Mesh) -> Node3D:
	var root := Node3D.new()
	var head := MeshInstance3D.new()
	head.name = &"Head"
	head.mesh = BoxMesh.new()
	head.material_override = skin
	root.add_child(head)
	var hair := MeshInstance3D.new()
	hair.name = &"Hair"
	hair.mesh = mesh
	root.add_child(hair)
	return root


# --- pre-integrated skin fit ---------------------------------------------------------------------


func test_preintegrated_constants_match_their_generator() -> void:
	var expected := _fit_expected()
	assert_eq(expected.size(), 4, "FIT_EXPECTED has a, b, c, d")
	var inc := FileAccess.get_file_as_string(BRDF_INC)
	for key: String in ["a", "b", "c", "d"]:
		var define := "HYMN_SKIN_PREINT_%s" % key.to_upper()
		var re := RegEx.create_from_string("#define %s vec3\\(([^)]*)\\)" % define)
		var m := re.search(inc)
		assert_true(m != null, "%s defined" % define)
		if m == null:
			continue
		var got := _floats(m.get_string(1))
		var want: Array[float] = expected[key]
		for c in 3:
			assert_between(got[c], want[c] - FIT_TOLERANCE, want[c] + FIT_TOLERANCE, "%s[%d]" % [define, c])


func test_preintegrated_fit_behaves() -> void:
	var e := _fit_expected()
	# u = 0 (flat skin) is exactly the clamped cosine.
	for x: float in [-0.5, 0.0, 0.3, 1.0]:
		var d := _preint(e, x, 0.0)
		assert_between(d.x, maxf(x, 0.0) - 1e-6, maxf(x, 0.0) + 1e-6, "u=0 is Lambert at %s" % x)
	# Curved skin: light reaches past the terminator, red the furthest, and D grows with N.L.
	var u := 1.0
	var term := _preint(e, 0.0, u)
	assert_true(term.x > term.y and term.y >= term.z - 1e-4, "red scatters furthest: %s" % str(term))
	assert_true(_preint(e, -0.2, u).x > 0.0, "red wraps into the shadow")
	var prev := -1.0
	for i in 21:
		var v := _preint(e, -1.0 + 0.1 * i, u).x
		assert_true(v >= prev - 1e-6, "monotonic in N.L")
		prev = v
	assert_between(_preint(e, 1.0, PREINT_U_MAX).x, 0.8, 1.0, "lit side keeps most of its energy")


# --- prewarm and the test stage ------------------------------------------------------------------


func test_every_character_shader_is_registered_for_prewarm() -> void:
	var reg: Variant = JSON.parse_string(FileAccess.get_file_as_string(PREWARM_JSON))
	var paths: Array[String] = []
	for entry: Variant in (reg as Dictionary)["materials"]:
		var e := entry as Dictionary
		paths.append(str(e["path"]))
		if str(e["path"]).begins_with("res://game/shaders/character/"):
			assert_false((e["scenes"] as Array).is_empty(), "character entries are scene-scoped: %s" % e["path"])
	for fam: String in CharacterShaderTiers.families():
		for tier: String in CharacterShaderTiers.tiers():
			assert_true(paths.has(CharacterShaderTiers.shader_path(fam, tier)), "%s/%s registered" % [fam, tier])
	for path: String in _table()["single_tier"]:
		assert_true(paths.has(path), "%s registered" % path)


func test_stage_assigns_materials_and_builds_the_low_comparison() -> void:
	var stage := (load(STAGE_SCENE) as PackedScene).instantiate() as CharacterShadingStage
	_host().add_child(stage)
	for node_name: String in [
		"Head", "Hair", "EyeL", "CorneaR", "EyeOcclusionL", "TearLineR", "Collar", "Drape", "Sleeve"
	]:
		var gi := stage.find_child(node_name, true, false) as GeometryInstance3D
		assert_true(gi != null and gi.material_override != null, "%s has a material" % node_name)
	var dissolve := stage.find_child("SleeveDissolve", true, false) as GeometryInstance3D
	assert_true(dissolve != null and dissolve.material_override == stage.dissolve_sleeve_material)
	var low := stage.find_child("CompareLow", true, false)
	var high := stage.find_child("CompareHigh", true, false)
	assert_true(low != null and high != null, "comparison rig built")
	if low != null and high != null:
		var low_skin := (low.find_child("Head", true, false) as GeometryInstance3D).material_override as ShaderMaterial
		var high_skin := (
			(high.find_child("Head", true, false) as GeometryInstance3D).material_override as ShaderMaterial
		)
		assert_eq(low_skin.shader.resource_path, CharacterShaderTiers.shader_path("skin", "low"))
		assert_eq(high_skin.shader.resource_path, CharacterShaderTiers.shader_path("skin", "high"))
	stage.free()


# --- helpers -------------------------------------------------------------------------------------


## M1-CHR-04: the Asha close-up stage's shadowed lights carry the terminator-safe normal bias.
func test_asha_stage_lights_clear_the_shadow_terminator() -> void:
	var stage := (load(ASHA_STAGE) as PackedScene).instantiate()
	var lights := stage.find_children("*", "DirectionalLight3D", true, false)
	assert_true(lights.size() > 0, "the stage has directional lights")
	for n in lights:
		var l := n as DirectionalLight3D
		if l.shadow_enabled:
			assert_true(l.shadow_normal_bias >= MIN_CLOSEUP_NORMAL_BIAS, "%s normal bias" % l.name)
	stage.free()


## M1-CHR-04: Asha's vest lacquer is a satin coat over a leather-rough base.
func test_asha_vest_lacquer_is_leather_not_plastic() -> void:
	var m := load(ASHA_CLOTH) as ShaderMaterial
	assert_true(float(m.get_shader_parameter("lacquer_coat_roughness")) >= MIN_VEST_COAT_ROUGHNESS, "coat")
	assert_true(float(m.get_shader_parameter("lacquer_coat_strength")) < 1.0, "partial coat")


func _table() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(TIERS_JSON)) as Dictionary


func _uniform_names(sh: Shader) -> Array:
	return sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))


func _floats(text: String) -> Array[float]:
	var out: Array[float] = []
	for part in text.split(","):
		out.append(float(part.strip_edges()))
	return out


## Parses FIT_EXPECTED = {"a": (r, g, b), ...} out of the Python generator.
func _fit_expected() -> Dictionary:
	var src := FileAccess.get_file_as_string(FIT_SCRIPT)
	var out := {}
	var re := RegEx.create_from_string('"([abcd])": \\(([^)]*)\\)')
	for m in re.search_all(src):
		out[m.get_string(1)] = _floats(m.get_string(2))
	return out


## GDScript port of hymn_char_preint_skin (same constants), for behavioural checks.
func _preint(e: Dictionary, x: float, u: float) -> Vector3:
	var out := Vector3.ZERO
	for c in 3:
		var q: float = e["a"][c] * u + e["b"][c] * u * u
		var s: float = 1.0 + e["c"][c] * u + e["d"][c] * u * u
		out[c] = s * (x + sqrt(x * x + q * q)) / (1.0 + sqrt(1.0 + q * q))
	return out


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func test_hero_mouth_interiors_use_the_mouth_family_with_a_cavity_bounce() -> void:
	# M1-RND-21: the lips shadow an open mouth from every light, so the interior needs the bounce term
	# (on every tier, not gated by quality) or grief goes near-black.
	var family: Array[String] = []
	for tier: String in CharacterShaderTiers.tiers():
		family.append(CharacterShaderTiers.shader_path("mouth", tier))
	for mat_name: String in ["mouth", "teeth", "tongue"]:
		var mat := load("res://assets/characters/asha/materials/%s.tres" % mat_name) as ShaderMaterial
		assert_true(mat != null and family.has(mat.shader.resource_path), "Asha's %s uses the mouth family" % mat_name)
	var body := FileAccess.get_file_as_string("res://game/shaders/character/character_mouth_body.gdshaderinc")
	var light := body.substr(body.find("void light()"))
	var bounce := light.find("cavity_bounce")
	assert_true(bounce > 0, "light() adds the cavity bounce")
	assert_false(light.substr(0, bounce).contains("#if"), "the bounce is on every tier")
	var decl := body.substr(body.find("uniform float cavity_bounce"))
	var default := float(decl.substr(decl.find("=") + 1, decl.find(";") - decl.find("=") - 1).strip_edges())
	assert_true(default > 0.0, "the bounce is on by default")
