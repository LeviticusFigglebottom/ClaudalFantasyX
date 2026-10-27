class_name CoilspirePreview
extends HalunaMood
## The Coilspire temple kit preview (M3-ENV-10; docs/kb/art/environments/coilspire.md). HalunaMood does the
## sun placement, the hymn_* globals and the capture determinism; this rig adds the two lighting phases and the
## fires:
## - `phase` &"storm" is the colour script's `ch08` frame outside (16:00, sun 30 deg / 250 deg, #FFE4CE at
##   2.0, Corrow's storm sky and `lut_ch08_storm`, the sea at +0.5 m); &"interior" is the kit's
##   `ch08_coilspire_int` frame (the same sun through the slits and the crown opening, `interior_environment`:
##   the copper green-cyan ambient, exposure 1.15, `lut_ch08_coilspire_int`). Takes effect at once when set in
##   the tree (the shots set it through their setup "nodes").
## - the fires: one shadowless OmniLight3D per layout "fire_lights" entry (the beacon) and "hearth_lights"
##   entry (the braziers and the keeping flame), [x, y, z, energy, range], added once the dresser has dressed
##   the zone. None of them lights the volumetric fog (the Lead's fog-lamp rule).

const PHASE_STORM := &"storm"
const PHASE_INTERIOR := &"interior"
const BEACON := &"Beacon"
const HEARTHS := &"Hearths"
const META_BASE := &"base_energy"
## Per phase: sun elevation, azimuth (deg), colour, energy, time of day (h), volumetric fog density, water
## height (m), beacon and hearth energy multipliers.
const PHASES: Dictionary = {
	PHASE_STORM: [30.0, 250.0, Color("#FFE4CE"), 2.0, 16.0, 0.03, 0.5, 1.0, 1.0],
	PHASE_INTERIOR: [30.0, 250.0, Color("#FFE4CE"), 2.0, 16.0, 0.01, 0.5, 1.0, 1.0],
}

@export var phase: StringName = PHASE_STORM:
	set(value):
		phase = value
		if is_node_ready():
			apply_phase()
## The `ch08_coilspire_int` frame (coilspire.md §0).
@export var interior_environment: Environment

var _beacon: Node3D
var _hearths: Node3D


func _ready() -> void:
	# The phases write into the Environments: work on this scene's own copies of the .tres files.
	if world_environment != null and world_environment.environment != null:
		world_environment.environment = world_environment.environment.duplicate()
	if interior_environment != null:
		interior_environment = interior_environment.duplicate()
	super._ready()
	if dresser != null:
		if dresser.layout.is_empty():
			dresser.dressed.connect(_on_dressed, CONNECT_ONE_SHOT)
		else:
			_on_dressed()
	apply_phase()


func _on_dressed() -> void:
	_beacon = build_lights(dresser.layout, "fire_lights", "fire_light_color", BEACON)
	add_child(_beacon)
	_hearths = build_lights(dresser.layout, "hearth_lights", "hearth_light_color", HEARTHS)
	add_child(_hearths)
	apply_phase()


## Shadowless omni lights for a layout list of [x, y, z, energy, range] (not added to the tree), none of
## which lights the volumetric fog.
static func build_lights(layout: Dictionary, key: String, color_key: String, node_name: StringName) -> Node3D:
	var root := Node3D.new()
	root.name = node_name
	var color := Color.html(str(layout.get(color_key, "#E0702E")))
	for entry: Array in layout.get(key, []):
		var light := OmniLight3D.new()
		light.light_color = color
		light.position = Vector3(float(entry[0]), float(entry[1]), float(entry[2]))
		light.light_energy = float(entry[3])
		light.omni_range = float(entry[4])
		light.shadow_enabled = false
		light.light_volumetric_fog_energy = 0.0
		light.set_meta(META_BASE, float(entry[3]))
		root.add_child(light)
	return root


## Puts the scene in `phase` (the sun, the environment, the haze, the sea's height and the fires).
func apply_phase() -> void:
	var p: Array = PHASES.get(phase, PHASES[PHASE_STORM])
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
	if world_environment != null:
		var target := _day_environment
		if phase == PHASE_INTERIOR and interior_environment != null:
			target = interior_environment
		if target != null and world_environment.environment != target:
			world_environment.environment = target
		if world_environment.environment != null:
			world_environment.environment.volumetric_fog_density = float(p[5])
	for group: Node3D in [_beacon, _hearths]:
		if group == null:
			continue
		var mult := float(p[7]) if group == _beacon else float(p[8])
		for light: OmniLight3D in group.get_children():
			light.light_energy = float(light.get_meta(META_BASE, 1.0)) * mult
	_write_globals()


## The beacon's lights (null until the zone is dressed).
func beacon() -> Node3D:
	return _beacon


## The braziers' and the keeping flame's lights (null until the zone is dressed).
func hearths() -> Node3D:
	return _hearths
