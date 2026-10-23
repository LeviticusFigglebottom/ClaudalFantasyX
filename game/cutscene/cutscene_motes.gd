class_name CutsceneMotes
extends Node3D
## Placeholder `@vfx` motes for the first playable (M2-FP-01): a few unshaded emissive spheres
## that drift (held light sinks seaward), rise in a spiral (released light), or hold still (bound
## light), then fade and free themselves. The look rows are in game/data/cutscene/sequencer.json
## "vfx". Replace with GlimmerField emitters (game/vfx/glimmer/) when Cinematics stages the scenes.

var life_sec := 0.0
var velocity := Vector3.ZERO
var spiral_radius := 0.0
var spiral_turn_sec := 0.0

var _age := 0.0
var _motes: Array[MeshInstance3D] = []
var _starts: Array[Vector3] = []
var _phases: Array[float] = []
var _material: StandardMaterial3D


## Builds `count` motes around the local origin from one sequencer.json "vfx" row. `rng_seed`
## keeps the scatter the same every play.
func build(row: Dictionary, count: int, rng_seed: int) -> void:
	life_sec = float(row.get("life_sec", 0.0))
	var v: Array = row.get("velocity", [0.0, 0.0, 0.0])
	velocity = Vector3(float(v[0]), float(v[1]), float(v[2]))
	spiral_radius = float(row.get("spiral_radius_m", 0.0))
	spiral_turn_sec = float(row.get("spiral_turn_sec", 0.0))
	var spread := float(row.get("spread_m", 0.0))
	_material = StandardMaterial3D.new()
	_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_material.albedo_color = Color(str(row.get("color", "#FFFFFF")))
	_material.emission_enabled = true
	_material.emission = _material.albedo_color
	_material.emission_energy_multiplier = float(row.get("energy", 1.0))
	var mesh := SphereMesh.new()
	var r := float(row.get("size_m", 0.0))
	mesh.radius = r
	mesh.height = r * 2.0
	mesh.material = _material
	var rng := RandomNumberGenerator.new()
	rng.seed = rng_seed
	for i in count:
		var mi := MeshInstance3D.new()
		mi.mesh = mesh
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var p := Vector3(
			rng.randf_range(-spread, spread), rng.randf_range(0.0, spread), rng.randf_range(-spread, spread)
		)
		mi.position = p
		add_child(mi)
		_motes.append(mi)
		_starts.append(p)
		_phases.append(rng.randf() * TAU)


func mote_count() -> int:
	return _motes.size()


func _process(delta: float) -> void:
	advance(delta)


func advance(delta: float) -> void:
	_age += delta
	if life_sec > 0.0 and _age >= life_sec:
		queue_free()
		return
	for i in _motes.size():
		var p := _starts[i] + velocity * _age
		if spiral_radius > 0.0 and spiral_turn_sec > 0.0:
			var a := _phases[i] + TAU * _age / spiral_turn_sec
			p += Vector3(cos(a), 0.0, sin(a)) * spiral_radius
		_motes[i].position = p
	if _material != null and life_sec > 0.0:
		_material.albedo_color.a = clampf(1.0 - _age / life_sec, 0.0, 1.0)
