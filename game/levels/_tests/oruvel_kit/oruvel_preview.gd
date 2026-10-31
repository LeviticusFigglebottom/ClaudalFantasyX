class_name OruvelPreview
extends HalunaMood
## The Oruvel raft-town kit preview (M3-ENV-07; docs/kb/art/environments/oruvel.md). HalunaMood does the sun, the
## hymn_* globals and the capture determinism at the colour script's `ch01`; M3-ENV-07B adds the storm:
## - `phase` &"day" is the `ch01` frame exactly as the scene is authored (nothing here touches it);
##   &"ch01_storm" is the stand-in storm sub-frame (oruvel.md §0, until Art writes the colour-script row): the
##   same sun veiled to STORM_SUN_ENERGY, `storm_environment` (lut_ch01_storm, a cleared sky, a cooler spray
##   haze), the storm swell (`storm_waves`), a rising wind; the layout's "states" "storm" (the broken pieces built
##   on first use, the intact pieces they replace hidden), Kell's beacon lit (the layout's "storm_lights"), the
##   *Seventh Terrace* gone from her mooring (she runs for open water, O13), and the Undertow standing up on the
##   southern horizon (UndertowStorm at the `ch01_arrival` preset, its clock stopped). Takes effect at once when
##   set in the tree (the storm shots set it through their setup "nodes").
## - `pen_split` poses Hullgnaw's split net-pen by the layout's "rigs" "net_pen_split" (0 = the intact pen at
##   rest, 1 = open, as the state places it): the reference for Combat's phase change (swap-in note in
##   docs/kb/tasks/M3/M3-ENV-07B-oruvel-storm.md).

const PHASE_DAY := &"day"
const PHASE_STORM := &"ch01_storm"
const STATE_STORM := "storm"
const STATE_ROOT := &"State_storm"
const LIGHTS_ROOT := &"StormLights"
const UNDERTOW := &"Undertow"
const RIG_PEN := "net_pen_split"
## The stand-in storm frame: the 10:30 sun (same angles), veiled and a touch cooler as the wall's high cloud spreads.
const STORM_SUN_ENERGY := 2.6
const STORM_SUN_COLOR := Color("#F6F0E8")
const STORM_TIME_OF_DAY_H := 11.25
const STORM_WIND_SPEED_M_S := 13.0
const STORM_WIND_GUST := 0.8
const STORM_WIND_AZIMUTH_DEG := 180.0
## The Undertow (Rendering's): far off at the colour script's arrival preset, out to sea (south), its clock held.
const UNDERTOW_PRESET := "ch01_arrival"
const UNDERTOW_AZIMUTH_DEG := 180.0
const UNDERTOW_QUALITY := "high"
const UNDERTOW_TIME_S := 205.0
const UNDERTOW_AMBIENT := 0.6
## PC pass 7 row 77: the sun stands behind the storm wall, so its glint path on the water is veiled too (at the day's
## strength it drew straight bright streaks down the sea under the cloud's bright spot).
const STORM_GLINT := 0.15
const PARAM_GLINT := &"glint_strength"

@export var phase: StringName = PHASE_DAY:
	set(value):
		phase = value
		if is_node_ready():
			apply_phase()
## The stand-in `ch01_storm` frame (lut_ch01_storm).
@export var storm_environment: Environment
## The storm's first swell, in from the sea.
@export var storm_waves: WaveSet
## The third dresser (the Seventh Terrace at the outer mooring): gone in the storm.
@export var seventh_terrace: Node3D
## Hullgnaw's split: 0 = the intact pen at rest, 1 = open (the state's pose).
@export_range(0.0, 1.0, 0.01) var pen_split: float = 1.0:
	set(value):
		pen_split = value
		if is_node_ready():
			pose_pen()
## The split sections' swell clock (s); the state's pose is at 0.
@export var swell_time_s: float = 0.0
## Stand the Undertow up in the storm (off in unit tests: it builds Rendering's storm meshes).
@export var undertow_enabled: bool = true

var _built := false
var _state_root: Node3D
var _hidden: Array[Node3D] = []
var _lights: Node3D
var _undertow: UndertowStorm
var _sections: Dictionary = {}  ## section piece -> its node in the state
var _day: Dictionary = {}  ## what the storm changes, as authored


func _ready() -> void:
	super._ready()
	if dresser != null and dresser.layout.is_empty():
		dresser.dressed.connect(apply_phase, CONNECT_ONE_SHOT)
	apply_phase()


## Puts the scene in `phase`. A scene that never leaves &"day" is never touched.
func apply_phase() -> void:
	var storm := phase == PHASE_STORM
	if not storm and not _built:
		return
	if dresser == null or dresser.layout.is_empty():
		return
	if not _built:
		_remember_day()
		_build_storm()
	_state_root.visible = storm
	for node: Node3D in _hidden:
		if is_instance_valid(node):
			node.visible = not storm
	_lights.visible = storm
	if _undertow != null:
		_undertow.visible = storm
	if seventh_terrace != null:
		seventh_terrace.visible = not storm
	if sun != null:
		sun.light_energy = STORM_SUN_ENERGY if storm else float(_day["sun_energy"])
		sun.light_color = STORM_SUN_COLOR if storm else _day["sun_color"] as Color
	if world_environment != null and storm_environment != null:
		world_environment.environment = storm_environment if storm else _day["environment"] as Environment
	if water != null and storm_waves != null:
		water.wave_set = storm_waves if storm else _day["waves"] as WaveSet
	if water != null and _day.get("water_material") != null:
		var day_mat := _day["water_material"] as ShaderMaterial
		if storm:
			var mat := day_mat.duplicate() as ShaderMaterial
			mat.set_shader_parameter(PARAM_GLINT, STORM_GLINT)
			water.material = mat
		else:
			water.material = day_mat
	time_of_day_h = STORM_TIME_OF_DAY_H if storm else float(_day["time_of_day_h"])
	wind_speed_m_s = STORM_WIND_SPEED_M_S if storm else float(_day["wind_speed"])
	wind_gust = STORM_WIND_GUST if storm else float(_day["wind_gust"])
	wind_azimuth_deg = STORM_WIND_AZIMUTH_DEG if storm else float(_day["wind_azimuth"])
	_write_globals()


func _remember_day() -> void:
	_day = {
		"sun_energy": sun.light_energy if sun != null else 0.0,
		"sun_color": sun.light_color if sun != null else Color.WHITE,
		"environment": world_environment.environment if world_environment != null else null,
		"waves": water.wave_set if water != null else null,
		"water_material": water.material as ShaderMaterial if water != null else null,
		"time_of_day_h": time_of_day_h,
		"wind_speed": wind_speed_m_s,
		"wind_gust": wind_gust,
		"wind_azimuth": wind_azimuth_deg,
	}


func _build_storm() -> void:
	_built = true
	var layout := dresser.layout
	var cfg: Dictionary = layout.get("states", {}).get(STATE_STORM, {})
	_state_root = Node3D.new()
	_state_root.name = STATE_ROOT
	add_child(_state_root)
	var rig := pen_rig(layout)
	var rig_pieces := {}
	for s: Dictionary in rig.get("sections", []):
		rig_pieces[String(s["piece"])] = s
	for spec: Dictionary in cfg.get("pieces", []):
		var piece := String(spec["piece"])
		var node := dresser.instance_piece(piece, spec.get("materials", {}), float(spec.get("lod1_from_m", -1.0)))
		if node == null:
			continue
		node.transform = CorrowPreview.piece_transform(spec)
		_state_root.add_child(node)
		# The town's own split sections (at the pen) are the rig's; the review row's copies stay where they are.
		if rig_pieces.has(piece) and not _sections.has(piece):
			var hinge: Array = rig_pieces[piece]["hinge"]
			if node.position.distance_to(Vector3(hinge[0], hinge[1], hinge[2])) < 3.0:
				_sections[piece] = node
	_hidden = CorrowPreview.find_pieces(dresser, cfg.get("hide", []))
	_lights = build_storm_lights(layout)
	add_child(_lights)
	if undertow_enabled:
		_build_undertow()
	pose_pen()


func _build_undertow() -> void:
	_undertow = UndertowStorm.new()
	_undertow.name = UNDERTOW
	_undertow.quality = UNDERTOW_QUALITY
	_undertow.start_time_s = UNDERTOW_TIME_S
	_undertow.playing = false
	_undertow.water = water
	_undertow.sun = sun
	_undertow.world_environment = world_environment
	_undertow.zone_shadow = false
	_undertow.exposure_flash = false
	_undertow.ambient_energy = UNDERTOW_AMBIENT
	if storm_environment != null:
		_undertow.haze_color = storm_environment.fog_light_color
	add_child(_undertow)
	_undertow.apply_preset(UNDERTOW_PRESET)
	_undertow.approach_azimuth_deg = UNDERTOW_AZIMUTH_DEG
	_undertow.rain_amount = 0.0


## The layout's net-pen split rig ({} when it has none).
static func pen_rig(layout: Dictionary) -> Dictionary:
	return layout.get("rigs", {}).get(RIG_PEN, {}) as Dictionary


## A split section's world transform at `amount` (0 rest .. 1 open) and swell time `t` (the rig's rule).
static func section_transform(section: Dictionary, amount: float, t: float) -> Transform3D:
	var hinge: Array = section["hinge"]
	var o: Dictionary = section["open"]
	var sw: Dictionary = section["swell"]
	var drift: Array = o["drift"]
	var tilt: Array = o["tilt_deg"]
	var swell := float(sw["pitch_deg"]) * sin(TAU * t / float(sw["period_s"]) + float(sw["phase"]))
	var basis := (
		Basis(Vector3.UP, deg_to_rad(amount * float(o["yaw_deg"])))
		* Basis.from_euler(
			Vector3(deg_to_rad(amount * (float(tilt[0]) + swell)), 0.0, deg_to_rad(amount * float(tilt[1])))
		)
	)
	var origin := Vector3(float(hinge[0]), float(hinge[1]), float(hinge[2]))
	origin += Vector3(float(drift[0]), float(drift[1]), float(drift[2])) * amount
	return Transform3D(basis, origin)


## Poses the state's split sections by `pen_split` and `swell_time_s`.
func pose_pen() -> void:
	if dresser == null:
		return
	for s: Dictionary in pen_rig(dresser.layout).get("sections", []):
		var node := _sections.get(String(s["piece"]), null) as Node3D
		if node != null:
			node.transform = section_transform(s, pen_split, swell_time_s)


## The storm's lamps for a layout (not added to the tree): per "storm_lights" entry an OmniLight3D that never lights
## volumetric fog (the fog-lamp rule) and a small flame.
static func build_storm_lights(layout: Dictionary) -> Node3D:
	var root := Node3D.new()
	root.name = LIGHTS_ROOT
	for entry: Dictionary in layout.get("storm_lights", []):
		var at: Array = entry["at"]
		var color := Color.html(str(entry.get("color", "#FFB466")))
		var light := OmniLight3D.new()
		light.name = str(entry.get("id", "Lamp"))
		light.position = Vector3(float(at[0]), float(at[1]), float(at[2]))
		light.light_color = color
		light.light_energy = float(entry.get("energy", 1.0))
		light.omni_range = float(entry.get("range_m", 8.0))
		light.shadow_enabled = false
		light.light_volumetric_fog_energy = 0.0
		root.add_child(light)
		var flame := MeshInstance3D.new()
		var mesh := SphereMesh.new()
		var r := float(entry.get("flame_r_m", 0.06))
		mesh.radius = r
		mesh.height = r * 2.6
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = color
		mat.emission_enabled = true
		mat.emission = color
		mat.emission_energy_multiplier = 4.0
		mesh.material = mat
		flame.mesh = mesh
		flame.position = light.position
		flame.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		root.add_child(flame)
	return root


## The state's node holding the storm pieces (null until the storm has been shown).
func state_root() -> Node3D:
	return _state_root


## The pen's split sections in the state, by piece (empty until the storm has been shown).
func split_sections() -> Dictionary:
	return _sections
