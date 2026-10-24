class_name CorrowPreview
extends HalunaMood
## The Corrow seawall kit preview (M3-ENV-04; docs/kb/art/environments/corrow.md). HalunaMood does the
## sun placement, the hymn_* globals and the capture determinism; this rig adds the zone's lighting
## phases, the Coilspire beacon and the wall's fallen state:
## - `phase` &"front" is the colour script's `ch08` frame (16:00, sun 30 deg / 250 deg, #FFE4CE at 2.0,
##   spray haze 0.03, the sea at +0.5 m under the storm front); &"surge" is `ch08_surge` (about 16:40, the
##   sun behind the front at 0.35, haze 0.06, the sky dimmed, the sea at +1.8 m: the low town flooded to the
##   stair foot). Takes effect at once when set in the tree (the shots set it through their setup "nodes").
## - M3-ENV-04B: &"fallen" is the morning after the storm (`ch08_after`, corrow.md §7: the sun low in the
##   east behind a flat overcast, `fallen_environment`, the sea still high at +1.12 m standing in the lanes);
##   &"ch09" is the colour script's `ch09` night (HalunaMood's night mood: the Moon #D2DFFF at 0.35, low and
##   half, `night_environment` with its stars, the `night_sea` look with sea-glow 0.15; slack water at
##   +0.3 m, so no water and no glow at the stair foot, ADR 0022 (g)). Both show the layout's "states"
##   "fallen": the breach pieces built on first use, and the intact pieces they replace hidden.
## - the beacon: one shadowless OmniLight3D per layout "fire_lights" entry [x, y, z, energy, range], in
##   "fire_light_color", added once the dresser has dressed the zone; brighter in the surge.

const PHASE_FRONT := &"front"
const PHASE_SURGE := &"surge"
const PHASE_FALLEN := &"fallen"
const PHASE_CH09 := &"ch09"
const BEACON := &"Beacon"
const STATE_FALLEN := &"fallen"
const STATE_PREFIX := "State_"
## Which layout state each phase shows (the intact wall when absent).
const PHASE_STATES: Dictionary = {PHASE_FALLEN: STATE_FALLEN, PHASE_CH09: STATE_FALLEN}
## How close (m) a placed piece must be to a state's "hide" entry to be the one it names.
const HIDE_MATCH_M := 0.05
const META_BASE_SKY := &"corrow_base_sky_energy"
const META_BASE_AMBIENT := &"corrow_base_ambient_energy"
## Per phase: sun elevation, azimuth (deg), colour, energy, time of day (h), volumetric fog density,
## water height (m), beacon energy multiplier, sky (background) energy and ambient energy (both as
## multipliers of the phase's Environment as authored).
const PHASES: Dictionary = {
	PHASE_FRONT: [30.0, 250.0, Color("#FFE4CE"), 2.0, 16.0, 0.03, 0.5, 1.0, 1.0, 1.0],
	PHASE_SURGE: [22.0, 255.0, Color("#FFE4CE"), 0.35, 16.67, 0.06, 1.8, 1.6, 0.42, 0.8],
	PHASE_FALLEN: [11.0, 112.0, Color("#E2E6EC"), 0.6, 7.5, 0.02, 0.45, 0.45, 1.0, 1.0],
	PHASE_CH09: [-30.0, 0.0, Color("#D2DFFF"), 0.0, 22.0, 0.006, 0.1, 0.55, 1.0, 1.0],
}

@export var phase: StringName = PHASE_FRONT:
	set(value):
		phase = value
		if is_node_ready():
			apply_phase()
## The `ch08_after` frame for &"fallen" (a flat post-storm overcast; corrow.md §7).
@export var fallen_environment: Environment

var _beacon: Node3D
var _states: Dictionary = {}  ## state name -> its Node3D (built on first use)
var _hidden: Dictionary = {}  ## state name -> Array of the dressed pieces it hides


func _ready() -> void:
	# The phases write into the Environments: work on this scene's own copies of the .tres files.
	if world_environment != null and world_environment.environment != null:
		world_environment.environment = world_environment.environment.duplicate()
	if fallen_environment != null:
		fallen_environment = fallen_environment.duplicate()
	if night_environment != null:
		night_environment = night_environment.duplicate()
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


## A layout piece's transform, as HalunaDresser places it (explicit "y", "dy", "yaw_deg", "tilt_deg",
## "scale").
static func piece_transform(spec: Dictionary) -> Transform3D:
	var at: Array = spec.get("at", [0.0, 0.0])
	var tilt: Array = spec.get("tilt_deg", [0.0, 0.0])
	var yaw := deg_to_rad(float(spec.get("yaw_deg", 0.0)))
	var basis := (
		Basis(Vector3.UP, yaw) * Basis.from_euler(Vector3(deg_to_rad(float(tilt[0])), 0.0, deg_to_rad(float(tilt[1]))))
	)
	var y := float(spec.get("y", 0.0)) + float(spec.get("dy", 0.0))
	return Transform3D(
		basis.scaled(Vector3.ONE * float(spec.get("scale", 1.0))), Vector3(float(at[0]), y, float(at[1]))
	)


## Puts the scene in `phase` (sun or moon, time of day, environment, haze, sky, the sea's height, the
## beacon, and the wall's state).
func apply_phase() -> void:
	var p: Array = PHASES.get(phase, PHASES[PHASE_FRONT])
	var night := phase == PHASE_CH09
	var wanted_mood := MOOD_NIGHT if night else MOOD_DAY
	if mood != wanted_mood:
		mood = wanted_mood
	if world_environment != null and not night:
		var target := _day_environment
		if phase == PHASE_FALLEN and fallen_environment != null:
			target = fallen_environment
		if target != null and world_environment.environment != target:
			world_environment.environment = target
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
		if not env.has_meta(META_BASE_SKY):
			env.set_meta(META_BASE_SKY, env.background_energy_multiplier)
			env.set_meta(META_BASE_AMBIENT, env.ambient_light_energy)
		env.volumetric_fog_density = float(p[5])
		env.background_energy_multiplier = float(env.get_meta(META_BASE_SKY)) * float(p[8])
		env.ambient_light_energy = float(env.get_meta(META_BASE_AMBIENT)) * float(p[9])
	if _beacon != null:
		for light: OmniLight3D in _beacon.get_children():
			light.light_energy = float(light.get_meta(&"base_energy", 1.0)) * float(p[7])
	_apply_state(PHASE_STATES.get(phase, &""))
	_write_globals()


## Shows a layout state (or the intact wall for &""): builds it on first use from the layout's
## "states", hides the dressed pieces it replaces.
func _apply_state(state: StringName) -> void:
	if dresser == null or dresser.layout.is_empty():
		return
	if state != &"" and not _states.has(state):
		_build_state(state)
	for s: StringName in _states:
		(_states[s] as Node3D).visible = s == state
	for s: StringName in _hidden:
		for node: Node3D in _hidden[s]:
			if is_instance_valid(node):
				node.visible = s != state


func _build_state(state: StringName) -> void:
	var cfg: Dictionary = dresser.layout.get("states", {}).get(String(state), {})
	var root := Node3D.new()
	root.name = STATE_PREFIX + String(state)
	add_child(root)
	_states[state] = root
	for spec: Dictionary in cfg.get("pieces", []):
		var node := dresser.instance_piece(
			String(spec["piece"]), spec.get("materials", {}), float(spec.get("lod1_from_m", -1.0))
		)
		if node == null:
			continue
		node.transform = piece_transform(spec)
		root.add_child(node)
	_hidden[state] = find_pieces(dresser, cfg.get("hide", []))


## The dressed pieces a "hide" list names: each entry {"piece", "at", "y"} matches the child of `parent`
## of that piece placed at that point.
static func find_pieces(parent: Node, entries: Array) -> Array[Node3D]:
	var out: Array[Node3D] = []
	var children := parent.get_children()
	for entry: Dictionary in entries:
		var piece := String(entry["piece"])
		var at: Array = entry["at"]
		var want := Vector3(float(at[0]), float(entry.get("y", 0.0)), float(at[1]))
		for child: Node in children:
			var n3 := child as Node3D
			if n3 == null or not is_piece(n3, piece):
				continue
			if n3.position.distance_to(want) <= HIDE_MATCH_M:
				out.append(n3)
				break
	return out


## True when a dressed node is an instance of `piece`: the dresser names a repeated piece "@Node3D@n",
## so the glTF's own mesh child (`<piece>`) is what tells.
static func is_piece(node: Node, piece: String) -> bool:
	if String(node.name) == piece or node.scene_file_path.get_file().get_basename() == piece:
		return true
	return node.get_node_or_null(NodePath(piece)) != null


## The node holding a state's pieces (null until the state has been shown).
func state_root(state: StringName) -> Node3D:
	return _states.get(state, null) as Node3D
