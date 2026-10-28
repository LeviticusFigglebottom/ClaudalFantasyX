extends TestCase
## M3-RND-1315: the camp fires' tongues lick on the held weather clock. The Brine Shoals kit's two fire slots are
## materials on game/vfx/fire/flame_tongue.gdshader, which declares what they set and never reads TIME.

const SHADER := "res://game/vfx/fire/flame_tongue.gdshader"
const MATERIALS: Array[String] = [
	"res://assets/environments/kits/brine_shoals/materials/bs_fire_outer.tres",
	"res://assets/environments/kits/brine_shoals/materials/bs_fire_core.tres",
]


func test_fire_slots_use_the_flame_shader() -> void:
	var sh := load(SHADER) as Shader
	assert_true(sh != null, "the flame shader loads")
	var names := sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
	for path in MATERIALS:
		var m := load(path) as ShaderMaterial
		assert_true(m != null and m.shader == sh, "%s is a flame material" % path.get_file())
		for u in ["base_color", "tip_color", "emission", "tear"]:
			assert_true(names.has(u), "the shader declares %s" % u)
			assert_true(m.get_shader_parameter(StringName(u)) != null, "%s sets %s" % [path.get_file(), u])


func test_the_flame_is_on_the_held_clock() -> void:
	var code := FileAccess.get_file_as_string(SHADER)
	assert_true(code.contains("hymn_wind_time"), "the weather clock drives it")
	var body := code.substr(code.find("void vertex()"))
	assert_false(body.contains("TIME"), "never TIME: a capture is deterministic")
