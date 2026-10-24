extends TestCase
## M2-RND-01: the compute storm body. Its variants compile, UndertowBodyEffect packs a body material
## into the generated std140 layout (defaults, sRGB colours, arrays), each spatial tier maps to its
## compute twin, and without a RenderingDevice the half-res body keeps its SubViewport path.

const SHADER_DIR := "res://game/shaders/undertow"
const VARIANTS: Array[String] = ["undertow_body", "undertow_body_medium", "undertow_body_ultra"]


func test_compute_variants_compile() -> void:
	for v in VARIANTS:
		var f := load("%s/%s_compute.glsl" % [SHADER_DIR, v]) as RDShaderFile
		assert_true(f != null, "%s_compute.glsl loads" % v)
		if f != null:
			assert_eq(f.get_spirv().compile_error_compute, "", "%s_compute.glsl compiles" % v)


func test_every_tier_maps_to_its_twin() -> void:
	for v in VARIANTS:
		var body := "%s/%s.gdshader" % [SHADER_DIR, v]
		assert_eq(UndertowBodyEffect.compute_path_for(body), "%s/%s_compute.glsl" % [SHADER_DIR, v])
	assert_eq(UndertowBodyEffect.compute_path_for("%s/undertow_shell.gdshader" % SHADER_DIR), "", "no twin")


func test_pack_writes_values_defaults_and_linear_colours() -> void:
	var m := ShaderMaterial.new()
	m.shader = load("%s/undertow_body.gdshader" % SHADER_DIR) as Shader
	m.set_shader_parameter(&"march_steps", 17)
	m.set_shader_parameter(&"density_per_m", 0.004)
	m.set_shader_parameter(&"col_wound", Color(0.5, 0.25, 1.0))
	var sites := PackedVector4Array([Vector4(1, 2, 3, 4), Vector4(5, 6, 7, 8)])
	m.set_shader_parameter(&"lightning_sites", sites)
	var bytes := UndertowBodyEffect.pack(m, Vector3(0.0, 0.6, 0.8))
	assert_eq(bytes.size(), UndertowComputeLayout.SIZE)
	var rows := {}
	for row: Array in UndertowComputeLayout.FIELDS:
		rows[row[0]] = row
	assert_eq(bytes.decode_s32(int(rows["march_steps"][2])), 17)
	assert_between(bytes.decode_float(int(rows["density_per_m"][2])), 0.0039999, 0.0040001)
	# Unset: the declaration's default.
	var cov := float(rows["coverage_bias"][4])
	assert_between(bytes.decode_float(int(rows["coverage_bias"][2])), cov - 1e-6, cov + 1e-6)
	# source_color: converted from sRGB to linear, as Godot does for the spatial shader.
	var lin := Color(0.5, 0.25, 1.0).srgb_to_linear()
	var w := int(rows["col_wound"][2])
	assert_between(bytes.decode_float(w), lin.r - 1e-5, lin.r + 1e-5)
	assert_between(bytes.decode_float(w + 4), lin.g - 1e-5, lin.g + 1e-5)
	# vec4 array at a 16-byte stride.
	var l := int(rows["lightning_sites"][2])
	assert_eq(bytes.decode_float(l + 16 + 12), 8.0)
	var sun := int(rows["hymn_sun_direction"][2])
	assert_between(bytes.decode_float(sun + 8), 0.79999, 0.80001)


func test_layout_covers_every_body_uniform() -> void:
	var sh := load("%s/undertow_body.gdshader" % SHADER_DIR) as Shader
	var names := {}
	for row: Array in UndertowComputeLayout.FIELDS:
		names[row[0]] = true
	for u: Dictionary in sh.get_shader_uniform_list():
		var n := str(u["name"])
		if n in ["noise_tex", "depth_tex"]:
			continue
		assert_true(names.has(n), "the compute block lacks %s (run gen_undertow_compute.py)" % n)


func test_no_rendering_device_keeps_the_subviewport_path() -> void:
	var body := MeshInstance3D.new()
	var m := ShaderMaterial.new()
	m.shader = load("%s/undertow_body.gdshader" % SHADER_DIR) as Shader
	body.material_override = m
	assert_eq(UndertowHalfRes.use_compute(body), RenderingServer.get_rendering_device() != null)
	body.free()
