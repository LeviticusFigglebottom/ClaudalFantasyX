class_name RippleField
extends Node
## The first ripples on a still mirror (M4-A2P-047; Ch14's escape across Ansedra's lagoon): ring sources on a
## WaterSurface's material (water_surface_body.gdshaderinc `ring_slope`). `strike()` sends one ring from a point (a
## pole stroke, a dropped gate); a `wake_target` drops a ring every wake_spacing_m it moves (the barge's wake). The
## rings keep their own clock, so a still water (time_scale 0) carries them. The field takes its own copy of the
## water's material, so the rings never reach another zone that shares it. Tuning: game/data/vfx/ripple_field.json.

const DATA_PATH := "res://game/data/vfx/ripple_field.json"
const PARAM_SOURCES := &"ripple_sources"
const PARAM_COUNT := &"ripple_count"
const PARAM_NOW := &"ripple_now_s"
const PARAM_TUNING := {
	&"ripple_speed_m_s": "speed_m_s",
	&"ripple_wavelength_m": "wavelength_m",
	&"ripple_width_m": "width_m",
	&"ripple_decay_s": "decay_s",
}
const GROUP := &"hymn_ripple_fields"

@export var water: WaterSurface
## A node whose travel across the water leaves a wake (the barge); none by default.
@export var wake_target: Node3D

## The field's clock (s): the sources' start times are on it.
var now_s := 0.0
## The live sources, oldest first: Vector4(x, z, start s, height m).
var sources: Array[Vector4] = []

var _data: Dictionary = {}
var _material: ShaderMaterial
var _last_wake := Vector3.INF


static func data() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH)) as Dictionary


## The first field in the tree (a zone has at most one), or null: cinematics strike through it.
static func find(tree: SceneTree) -> RippleField:
	return tree.get_first_node_in_group(GROUP) as RippleField if tree != null else null


func _ready() -> void:
	add_to_group(GROUP)
	_data = data()
	if water != null and water.material != null:
		_material = water.material.duplicate() as ShaderMaterial
		water.material = _material
		for key: StringName in PARAM_TUNING:
			_material.set_shader_parameter(key, float(_data[PARAM_TUNING[key]]))
	_push()


func _process(delta: float) -> void:
	advance(delta)


## Moves the field's clock on by `delta`: drops the wake, ages the sources out, and updates the water.
func advance(delta: float) -> void:
	now_s += delta
	if wake_target != null and wake_target.is_inside_tree():
		var p := wake_target.global_position
		if (
			_last_wake == Vector3.INF
			or Vector2(p.x - _last_wake.x, p.z - _last_wake.z).length() >= float(_data["wake_spacing_m"])
		):
			_last_wake = p
			strike(p, float(_data["wake_height_m"]))
	var life := float(_data["life_s"])
	while not sources.is_empty() and now_s - sources[0].z > life:
		sources.pop_front()
	_push()


## Sends one ring outward from `at` (world), `height_m` high (the data's strike height by default).
func strike(at: Vector3, height_m: float = -1.0) -> void:
	var h := height_m if height_m > 0.0 else float(_data["strike_height_m"])
	sources.append(Vector4(at.x, at.z, now_s, h))
	while sources.size() > int(_data["max_sources"]):
		sources.pop_front()
	_push()


func _push() -> void:
	if _material == null:
		return
	var arr := PackedVector4Array()
	arr.resize(int(_data["max_sources"]))
	for i in sources.size():
		arr[i] = sources[i]
	_material.set_shader_parameter(PARAM_SOURCES, arr)
	_material.set_shader_parameter(PARAM_COUNT, sources.size())
	_material.set_shader_parameter(PARAM_NOW, now_s)
