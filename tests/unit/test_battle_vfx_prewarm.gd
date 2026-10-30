extends TestCase
## The PC pass 5 row 64: one 73-119 ms frame in the 60 after the fade in five fights. A ParticleProcessMaterial
## compiles one shader per feature set, and every battle effect sets a color ramp (and most motes turbulence), which
## the registry's base spark material never compiled. Each effect layer's process material, as BattleVfx builds it,
## must match a variant the battle scenes warm behind the fade (prewarm_materials.json).

const BATTLE_SCENE := "res://game/battle/scene/battle_sandbox.tscn"


func test_every_effect_layer_draws_a_warmed_particle_variant() -> void:
	var warmed: Array[String] = []
	var registry := JSON.parse_string(FileAccess.get_file_as_string(ShaderPrewarm.REGISTRY_PATH)) as Dictionary
	for entry: Dictionary in registry.get("materials", []):
		var mat := load(str(entry.get("path", ""))) as ParticleProcessMaterial
		if mat != null and (entry.get("scenes", []) as Array).has(BATTLE_SCENE):
			warmed.append(_variant(mat))
	var vfx := BattleVfx.new()
	var effects := vfx.data.get("effects", {}) as Dictionary
	var checked := 0
	for eid: String in effects:
		var layers: Array = (effects[eid] as Dictionary).get("layers", [])
		for i in layers.size():
			for reduced: bool in [false, true]:
				vfx.reduced_motion = reduced
				var p := GPUParticles3D.new()
				p.process_material = vfx._process_for(StringName("%s#%d" % [eid, i]), layers[i] as Dictionary)
				vfx._apply_motion(p, layers[i] as Dictionary)
				var v := _variant(p.process_material as ParticleProcessMaterial)
				assert_true(warmed.has(v), "%s layer %d (%s) is warmed before the fade" % [eid, i, v])
				p.free()
				checked += 1
	assert_true(checked > 100, "every layer checked (%d)" % checked)
	vfx.free()


## The features that pick a ParticleProcessMaterial's shader, as BattleVfx sets them.
static func _variant(mat: ParticleProcessMaterial) -> String:
	return "shape=%d ramp=%s turbulence=%s" % [mat.emission_shape, mat.color_ramp != null, mat.turbulence_enabled]
