class_name OruvelUnderwayPreview
extends HalunaMood
## The Oruvel Underway kit preview (M3-ENV-05; docs/kb/art/environments/oruvel_underway.md). HalunaMood does the
## sun placement (the `ch01_underway` sub-frame, 08:45, 42 deg / 105 deg), the hymn_* globals and the capture
## determinism; the scene's UnderwaterRig (M2-RND-02, M2-RND-09) gives every camera the underwater look and Rhen's
## lantern. This rig adds, per shot camera, from the layout's "shots" entry:
## - where the lantern hangs (the rig's `lantern_target`; beside the lens in the preview frames);
## - the depth of the subject (`depth_m`): the sun and the ambient reach it through that much water, so they are
##   tinted by the rig's own transmittance, exp(-sigma x depth) per channel (red goes first). The rig absorbs only
##   along the camera's ray, not the light's way down, so without this a floor at 22 m was lit by the full noon sun;
## - the lighting area (§0): "open" (the crown, the terrace), "interior" (the gallery) or "deep" (the stair lip,
##   the gauge room). The area scales the ambient and the rig's in-scatter light level, because the rig lights its
##   in-scatter with the sun and no occlusion: inside the tower the water would glow like the open sea.
## Both are preview stand-ins (the rig's data `light_reference`, the sun's colour); the zone needs a downwelling term
## and a per-area light scale on the rig, requested of Rendering in the design notes.

const AREA_OPEN := &"open"
const AREA_INTERIOR := &"interior"
const AREA_DEEP := &"deep"
## Per area: ambient energy, in-scatter light scale (oruvel_underway.md §0).
const AREAS: Dictionary = {
	AREA_OPEN: [0.65, 1.0],
	AREA_INTERIOR: [0.22, 0.33],
	AREA_DEEP: [0.14, 0.2],
}
const KEY_SHOTS := "shots"
const KEY_LANTERN := "lantern"
const KEY_AREA := "area"
const KEY_DEPTH := "depth_m"
const OPTICS := "optics"
const COLORS := "colors"
const LIGHT_REFERENCE := "light_reference"
const TRANSMIT := "transmit"
const TRANSMIT_DISTANCE := "transmit_distance_m"
const MIN_TRANSMIT := 1e-3
## hymn_glimmer for the dive: held cyan (glimmer_held #7FC6D9, linear) at the colour script's `ch01` energy 1.5.
## Its alpha opens the glimmer gate that HalunaMood keeps shut by day, so the low lights (U06) draw.
const DIVE_GLIMMER := Vector4(0.2122, 0.5647, 0.6939, 1.5)

@export var rig: UnderwaterRig
## Rhen's lantern: the rig's lantern_target (a stand-in lantern mesh hangs under it).
@export var lantern: Node3D
## The `ch01` fill (#8FC3E0): the ambient before the water takes its share.
@export var fill_color := Color("#8FC3E0")
## The area in force; set by the current camera's layout entry, or by hand.
@export var area: StringName = AREA_OPEN:
	set(value):
		area = value
		if is_node_ready():
			apply_lighting()
## Metres of water over the subject (the light's way down); set by the camera's layout entry, or by hand.
@export var depth_m: float = 0.0:
	set(value):
		depth_m = value
		if is_node_ready():
			apply_lighting()

var _shot_name: StringName = &""
var _base_light_reference: float = 0.0
var _key_color := Color.WHITE


func _ready() -> void:
	# The lighting writes the ambient into the Environment: work on this scene's own copy of the .tres.
	if world_environment != null and world_environment.environment != null:
		world_environment.environment = world_environment.environment.duplicate()
	# The rig's data is a cache shared by every rig (UnderwaterRig.load_data): the area writes a private copy.
	if rig != null:
		rig.data = rig.data.duplicate(true)
	if sun != null:
		_key_color = sun.light_color
	# The lantern's light sits inside its own mesh: the mesh must cast no shadow, or its cage blots the pool.
	if lantern != null:
		for mi: MeshInstance3D in lantern.find_children("*", "MeshInstance3D", true, false):
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	super._ready()
	apply_lighting()


func _process(delta: float) -> void:
	super._process(delta)
	var cam := get_viewport().get_camera_3d()
	if cam != null and cam.name != _shot_name:
		_shot_name = cam.name
		apply_shot(_shot_name)


## The layout's entry for a shot camera ({} when it has none).
func shot_entry(shot: StringName) -> Dictionary:
	if dresser == null:
		return {}
	var shots: Dictionary = dresser.layout.get(KEY_SHOTS, {})
	return shots.get(String(shot), {})


## The dive's hymn_glimmer: held motes at the colour script's `ch01` energy (HalunaMood shuts the gate by day).
func glimmer() -> Vector4:
	return DIVE_GLIMMER


## Hangs the lantern and sets the depth and area for a shot camera (no change for one the layout doesn't list).
func apply_shot(shot: StringName) -> void:
	var entry := shot_entry(shot)
	if entry.is_empty():
		return
	if lantern != null and entry.has(KEY_LANTERN):
		var p: Array = entry[KEY_LANTERN]
		lantern.global_position = Vector3(float(p[0]), float(p[1]), float(p[2]))
	depth_m = float(entry.get(KEY_DEPTH, 0.0))
	area = StringName(str(entry.get(KEY_AREA, AREA_OPEN)))


## The rig's per-channel transmittance over `metres` of water (linear RGB), from its data's transmit colour.
func transmittance(metres: float) -> Vector3:
	var data: Dictionary = rig.data if rig != null else UnderwaterRig.load_data()
	var c := Color(str((data.get(COLORS, {}) as Dictionary).get(TRANSMIT, "#1FA3A6"))).srgb_to_linear()
	var dist := float((data.get(OPTICS, {}) as Dictionary).get(TRANSMIT_DISTANCE, 40.0))
	var sigma := (
		Vector3(-log(maxf(c.r, MIN_TRANSMIT)), -log(maxf(c.g, MIN_TRANSMIT)), -log(maxf(c.b, MIN_TRANSMIT))) / dist
	)
	return Vector3(exp(-sigma.x * metres), exp(-sigma.y * metres), exp(-sigma.z * metres))


## A colour seen through `t` (linear transmittance), back in sRGB.
static func tinted(color: Color, t: Vector3) -> Color:
	var lin := color.srgb_to_linear()
	return Color(lin.r * t.x, lin.g * t.y, lin.b * t.z, 1.0).linear_to_srgb()


## Puts the scene at `depth_m` in `area`: the sun's and the ambient's colour, the ambient energy and the rig's
## in-scatter light level.
func apply_lighting() -> void:
	var a: Array = AREAS.get(area, AREAS[AREA_OPEN])
	var t := transmittance(depth_m)
	if sun != null:
		sun.light_color = tinted(_key_color, t)
	if world_environment != null and world_environment.environment != null:
		var env := world_environment.environment
		env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
		env.ambient_light_color = tinted(fill_color, t)
		env.ambient_light_energy = float(a[0])
	if rig == null or rig.data.is_empty():
		return
	var optics: Dictionary = rig.data.get(OPTICS, {})
	if _base_light_reference <= 0.0:
		_base_light_reference = float(optics.get(LIGHT_REFERENCE, 1.0))
	optics[LIGHT_REFERENCE] = _base_light_reference / maxf(float(a[1]), 0.01)
