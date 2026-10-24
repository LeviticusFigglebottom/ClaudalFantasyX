class_name BrineShoalsPreview
extends HalunaMood
## The Brine Shoals kit preview (M3-ENV-02; docs/kb/art/environments/brine_shoals.md). HalunaMood does the
## sun placement, the hymn_* globals and the capture determinism; this rig adds the zone's two lighting
## phases and the fires:
## - `phase` &"raid" is the colour script's `ch06` frame (15:30, sun 35 deg / 240 deg, #FFD5B3 at 2.4,
##   smoke haze 0.02, the fires lit); &"after" is the side scene's `ch06_after` (about 16:40, sun 24 deg /
##   255 deg, #FFC79A at 2.2, the haze thinning to 0.012, the fire lights out and the smoke thinner).
##   Takes effect at once when set in the tree (the shots set it through their setup "nodes").
## - the fire lights: one shadowless OmniLight3D per layout "fire_lights" entry [x, y, z, energy, range],
##   in "fire_light_color", added once the dresser has dressed the zone.

const PHASE_RAID := &"raid"
const PHASE_AFTER := &"after"
const SMOKE_PREFIX := "smoke_plume"
const PARAM_DENSITY := &"density"
const FIRE_LIGHTS := &"FireLights"
## Per phase: sun elevation, azimuth (deg), colour, energy, time of day (h), volumetric fog density,
## smoke density multiplier, fire lights on.
const PHASES: Dictionary = {
	PHASE_RAID: [35.0, 240.0, Color("#FFD5B3"), 2.4, 15.5, 0.02, 1.0, true],
	PHASE_AFTER: [24.0, 255.0, Color("#FFC79A"), 2.2, 16.7, 0.012, 0.45, false],
}

@export var phase: StringName = PHASE_RAID:
	set(value):
		phase = value
		if is_node_ready():
			apply_phase()

var _fires: Node3D


func _ready() -> void:
	# The phase writes the haze into the Environment: work on this scene's own copy of the .tres.
	if world_environment != null and world_environment.environment != null:
		world_environment.environment = world_environment.environment.duplicate()
	super._ready()
	if dresser != null:
		if dresser.layout.is_empty():
			dresser.dressed.connect(_on_dressed, CONNECT_ONE_SHOT)
		else:
			_on_dressed()
	apply_phase()


func _on_dressed() -> void:
	_fires = build_fire_lights(dresser.layout)
	add_child(_fires)
	apply_phase()


## The fire lights for a layout (not added to the tree): ember_orange omnis, no shadows.
static func build_fire_lights(layout: Dictionary) -> Node3D:
	var root := Node3D.new()
	root.name = FIRE_LIGHTS
	var color := Color.html(str(layout.get("fire_light_color", "#E0702E")))
	for entry: Array in layout.get("fire_lights", []):
		var light := OmniLight3D.new()
		light.light_color = color
		light.position = Vector3(float(entry[0]), float(entry[1]), float(entry[2]))
		light.light_energy = float(entry[3])
		light.omni_range = float(entry[4])
		light.shadow_enabled = false
		root.add_child(light)
	return root


## Puts the scene in `phase` (sun, time of day, haze, fires, smoke).
func apply_phase() -> void:
	var p: Array = PHASES.get(phase, PHASES[PHASE_RAID])
	sun_elevation_deg = float(p[0])
	sun_azimuth_deg = float(p[1])
	time_of_day_h = float(p[4])
	if sun != null:
		sun.light_color = p[2]
		sun.light_energy = float(p[3])
		var toward := HalunaMood.direction_from_angles(sun_elevation_deg, sun_azimuth_deg)
		sun.global_basis = Basis.looking_at(-toward, Vector3.UP)
	if world_environment != null and world_environment.environment != null:
		world_environment.environment.volumetric_fog_density = float(p[5])
	if _fires != null:
		_fires.visible = bool(p[7])
	_apply_smoke(float(p[6]))
	_write_globals()


func _apply_smoke(scale: float) -> void:
	if dresser == null:
		return
	for child: Node in dresser.get_children():
		if not String(child.name).begins_with(SMOKE_PREFIX):
			continue
		for mi: MeshInstance3D in child.find_children("*", "MeshInstance3D", true, false):
			for i in mi.get_surface_override_material_count():
				var m := mi.get_surface_override_material(i) as ShaderMaterial
				if m == null:
					continue
				var base: ShaderMaterial = m.get_meta(&"phase_base", m)
				var copy := base.duplicate() as ShaderMaterial
				copy.set_meta(&"phase_base", base)
				copy.set_shader_parameter(PARAM_DENSITY, float(base.get_shader_parameter(PARAM_DENSITY)) * scale)
				mi.set_surface_override_material(i, copy)
