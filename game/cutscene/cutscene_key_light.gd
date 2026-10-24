class_name CutsceneKeyLight
extends DirectionalLight3D
## The dialogue-range character key light (M2-FP-10; docs/kb/tech/cutscenes.md, "Key light").
##
## A zone sun's shadow cascades span hundreds of metres, so their texels are far too coarse to
## shadow a face's own nose and mouth corners at dialogue range (docs/kb/qa/gpu/
## 2026-10-23-rnd-18-20-followups.md). While a close shot is on screen this light stands in for the
## sun on the cast only: the cast's meshes move to one render layer, the sun stops lighting that
## layer, and this light, with the sun's direction and colour but a few metres of shadow range and
## character_shading.md's face bias, lights only that layer. Everything else keeps the sun.
##
## The sun still casts the cast's shadows on the ground (its shadow_caster_mask is untouched), and
## scenery within this light's shadow range still shadows the cast. disengage() puts every layer
## and the sun back exactly as they were.

## sequencer.json "key_light" (layer, shadow values, close_half_frame_m).
var config: Dictionary = {}

var _sun: DirectionalLight3D
var _sun_cull_mask := 0
## [GeometryInstance3D, original layers] per cast mesh moved onto the key layer.
var _moved: Array = []


func _init(cfg: Dictionary = {}) -> void:
	config = cfg
	name = "CutsceneKeyLight"
	visible = false
	shadow_enabled = true
	directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	# One sun in the sky, one in the fog, one in the GI: this light only keys the cast.
	sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
	light_volumetric_fog_energy = 0.0
	light_indirect_energy = 0.0


## True when `shot` frames at most config close_half_frame_m above and below its aim at the aim's
## distance (dialogue and portrait framing). `camera_pos` and `aim` are world space.
static func is_close(camera_pos: Vector3, aim: Vector3, fov_deg: float, cfg: Dictionary) -> bool:
	var half_frame := camera_pos.distance_to(aim) * tan(deg_to_rad(fov_deg) * 0.5)
	return half_frame <= float(cfg.get("close_half_frame_m", 0.0))


func layer_mask() -> int:
	return 1 << (int(config.get("layer", 1)) - 1)


func is_engaged() -> bool:
	return _sun != null


func sun() -> DirectionalLight3D:
	return _sun


## Keys `cast` (every GeometryInstance3D under each node) with a short-range copy of `sun`, turned
## by `yaw_deg` about world up and `pitch_deg` about the light's own X, at `energy_scale` times the
## sun's intensity. Re-engaging (the next close shot) first restores the previous state.
func engage(
	sun_light: DirectionalLight3D, cast: Array[Node3D], yaw_deg: float, pitch_deg: float, energy_scale: float
) -> void:
	disengage()
	if sun_light == null or not is_instance_valid(sun_light):
		return
	_sun = sun_light
	var mask := layer_mask()
	_sun_cull_mask = sun_light.light_cull_mask
	sun_light.light_cull_mask = _sun_cull_mask & ~mask
	var seen := {}
	for root in cast:
		if root == null or not is_instance_valid(root):
			continue
		var meshes: Array[Node] = root.find_children("*", "GeometryInstance3D", true, false)
		if root is GeometryInstance3D:
			meshes.append(root)
		for n in meshes:
			var g := n as GeometryInstance3D
			if seen.has(g.get_instance_id()):
				continue
			seen[g.get_instance_id()] = true
			_moved.append([g, g.layers])
			g.layers = mask
	light_cull_mask = mask
	light_color = sun_light.light_color
	light_energy = sun_light.light_energy * energy_scale
	light_intensity_lux = sun_light.light_intensity_lux * energy_scale
	light_temperature = sun_light.light_temperature
	light_specular = sun_light.light_specular
	light_angular_distance = sun_light.light_angular_distance
	shadow_bias = float(config.get("shadow_bias", shadow_bias))
	shadow_normal_bias = float(config.get("shadow_normal_bias", shadow_normal_bias))
	shadow_blur = float(config.get("shadow_blur", shadow_blur))
	directional_shadow_max_distance = float(config.get("shadow_max_distance_m", directional_shadow_max_distance))
	var b := sun_light.global_basis.orthonormalized()
	b = Basis(Vector3.UP, deg_to_rad(yaw_deg)) * b
	b = b * Basis(Vector3.RIGHT, deg_to_rad(pitch_deg))
	global_basis = b
	visible = true


## Puts the sun's cull mask and every moved mesh's layers back, and hides the light.
func disengage() -> void:
	for pair: Array in _moved:
		var g: Variant = pair[0]
		if is_instance_valid(g):
			(g as GeometryInstance3D).layers = int(pair[1])
	_moved.clear()
	if _sun != null and is_instance_valid(_sun):
		_sun.light_cull_mask = _sun_cull_mask
	_sun = null
	visible = false


func _exit_tree() -> void:
	disengage()
