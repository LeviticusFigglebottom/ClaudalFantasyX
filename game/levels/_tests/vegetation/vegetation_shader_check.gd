extends SceneTree
## Headless compile check for the vegetation shaders (M1-ENV-02), run by tools/tests/test_vegetation.py:
##   godot --headless --path . --script res://game/levels/_tests/vegetation/vegetation_shader_check.gd
## Godot compiles a shader's front end (preprocessor, includes, types) on first use; a broken shader
## prints SHADER ERROR and exposes no uniforms. Prints one VEG_SHADER line per shader, exits 1 on failure.
## (Global-uniform registration and the GPU back end are only checked by a real renderer.)

const SHADERS: Dictionary[String, StringName] = {
	"res://game/shaders/vegetation/vegetation_foliage.gdshader": &"translucency",
	"res://game/shaders/vegetation/vegetation_foliage_low.gdshader": &"translucency",
	"res://game/shaders/vegetation/vegetation_bark.gdshader": &"col_base",
}
const WIND_UNIFORM := &"wind_response"


func _init() -> void:
	var failed := 0
	for path: String in SHADERS:
		var shader := load(path) as Shader
		var names: Array[StringName] = []
		if shader:
			for u: Dictionary in shader.get_shader_uniform_list():
				names.append(StringName(u["name"]))
		var ok := names.has(SHADERS[path]) and names.has(WIND_UNIFORM)
		print("VEG_SHADER %s %s (%d uniforms)" % ["ok" if ok else "FAIL", path, names.size()])
		failed += 0 if ok else 1
	quit(1 if failed > 0 else 0)
