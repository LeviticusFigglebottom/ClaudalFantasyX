class_name CorrowPreview
extends HalunaMood
## The Corrow seawall kit preview (M3-ENV-04; docs/kb/art/environments/corrow.md). HalunaMood does the
## sun placement, the hymn_* globals and the capture determinism; this rig adds the zone's two lighting
## phases and the Coilspire beacon:
## - `phase` &"front" is the colour script's `ch08` frame (16:00, sun 30 deg / 250 deg, #FFE4CE at 2.0,
##   spray haze 0.03, the sea at +0.5 m under the storm front); &"surge" is `ch08_surge` (about 16:40, the
##   sun behind the front at 0.35, haze 0.06, the sky dimmed, the sea at +1.8 m: the low town flooded to the
##   stair foot). Takes effect at once when set in the tree (the shots set it through their setup "nodes").
## - the beacon: one shadowless OmniLight3D per layout "fire_lights" entry [x, y, z, energy, range], in
##   "fire_light_color", added once the dresser has dressed the zone; brighter in the surge.

const PHASE_FRONT := &"front"
const PHASE_SURGE := &"surge"
const BEACON := &"Beacon"
## Per phase: sun elevation, azimuth (deg), colour, energy, time of day (h), volumetric fog density,
## water height (m), beacon energy multiplier, sky (background) energy, ambient energy.
const PHASES: Dictionary = {
	PHASE_FRONT: [30.0, 250.0, Color("#FFE4CE"), 2.0, 16.0, 0.03, 0.5, 1.0, 1.0, 1.0],
	PHASE_SURGE: [22.0, 255.0, Color("#FFE4CE"), 0.35, 16.67, 0.06, 1.8, 1.6, 0.42, 0.8],
}

@export var phase: StringName = PHASE_FRONT:
	set(value):
		phase = value
		if is_node_ready():
			apply_phase()

var _beacon: Node3D


func _ready() -> void:
	# The phase writes into the Environment: work on this scene's own copy of the .tres.
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
	_beacon = build_beacon_lights(dresser.layout)
	add_child(_beacon)
	apply_phase()


## The beacon lights for a layout (not added to the tree): ember_orange omnis, no shadows.
static func build_beacon_lights(layout: Dictionary) -> Node3D:
	var root := Node3D.new()
	root.name = BEACON
	var color := Color.html(str(layout.get("fire_light_color", "#E0702E")))
	for entry: Array in layout.get("fire_lights", []):
		var light := OmniLight3D.new()
		light.light_color = color
		light.position = Vector3(float(entry[0]), float(entry[1]), float(entry[2]))
		light.light_energy = float(entry[3])
		light.omni_range = float(entry[4])
		light.shadow_enabled = false
		light.set_meta(&"base_energy", float(entry[3]))
		root.add_child(light)
	return root


## Puts the scene in `phase` (sun, time of day, haze, sky, the sea's height, the beacon).
func apply_phase() -> void:
	var p: Array = PHASES.get(phase, PHASES[PHASE_FRONT])
	sun_elevation_deg = float(p[0])
	sun_azimuth_deg = float(p[1])
	time_of_day_h = float(p[4])
	water_height_m = float(p[6])
	if sun != null:
		sun.light_color = p[2]
		sun.light_energy = float(p[3])
		var toward := HalunaMood.direction_from_angles(sun_elevation_deg, sun_azimuth_deg)
		sun.global_basis = Basis.looking_at(-toward, Vector3.UP)
	if tide != null:
		tide.water_height_y = water_height_m
	if world_environment != null and world_environment.environment != null:
		var env := world_environment.environment
		env.volumetric_fog_density = float(p[5])
		env.background_energy_multiplier = float(p[8])
		env.ambient_light_energy = float(p[9])
	if _beacon != null:
		for light: OmniLight3D in _beacon.get_children():
			light.light_energy = float(light.get_meta(&"base_energy", 1.0)) * float(p[7])
	_write_globals()
