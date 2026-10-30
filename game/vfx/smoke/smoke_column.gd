class_name SmokeColumn
extends Node3D
## A volumetric smoke column (M3-RND-21). Docs: docs/kb/tech/smoke.md. Data: game/data/vfx/smoke_column.json.
## Put one where a fire's smoke rises (this node is the column's foot), yawed so +X points downwind, scaled as the
## kit's smoke_plume pieces are. It builds a box that bounds the column and draws smoke_column.gdshader on its back
## faces: a march of the view ray through the column's density to the opaque scene. `profile` picks a row of the data's
## "columns"; set_quality(preset id) picks the march's steps (Low still reads as a column, with coarser billows).

const DATA_PATH := "res://game/data/vfx/smoke_column.json"
const SHADER := "res://game/vfx/smoke/smoke_column.gdshader"
## The data's column keys the shader takes as float uniforms of the same name.
const FLOAT_KEYS: Array[String] = [
	"height_m",
	"lean_m",
	"base_radius_m",
	"top_radius_m",
	"density",
	"top_thin",
	"base_fade",
	"top_fade",
	"edge_noise",
	"noise_scale_per_m",
	"rise_m_s",
	"light_energy",
	"fire_glow",
	"fire_band",
	"forward_scatter",
]
const COLOR_KEYS: Array[String] = ["col_lit", "col_core", "col_fire"]
## The spine's sideways wobble (metres, as the shader's spine()) and the box's margin past the widest radius with its
## noisy edge (the shader's density reaches radius x (1 + edge_noise / 2)).
const SPINE_WOBBLE_M := 0.8
const BOX_MARGIN_M := 0.5

static var _data_cache: Dictionary = {}

## A row of the data's "columns".
@export var profile: String = "camp"
## A per-column offset into the billows (two columns of one profile never billow alike).
@export var seed: float = 0.0
## A preset id (low, medium, high, ultra).
@export var quality: String = "high":
	set(value):
		quality = value
		_apply_quality()

var column: Dictionary = {}
var box: MeshInstance3D
var material: ShaderMaterial


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = parsed as Dictionary
		else:
			push_warning("SmokeColumn: cannot read %s" % DATA_PATH)
	return _data_cache


## GraphicsRuntime-style hook: false when the preset has no quality row.
func set_quality(preset_id: String) -> bool:
	if not (load_data().get("quality", {}) as Dictionary).has(preset_id):
		return false
	quality = preset_id
	return true


func get_quality() -> String:
	return quality


func _ready() -> void:
	column = (load_data().get("columns", {}) as Dictionary).get(profile, {}) as Dictionary
	if column.is_empty():
		push_warning("SmokeColumn: no column %s in %s" % [profile, DATA_PATH])
	material = ShaderMaterial.new()
	material.shader = load(SHADER) as Shader
	for key in FLOAT_KEYS:
		if column.has(key):
			material.set_shader_parameter(StringName(key), float(column[key]))
	for key in COLOR_KEYS:
		if column.has(key):
			material.set_shader_parameter(StringName(key), Color(str(column[key])))
	material.set_shader_parameter(&"seed", seed)
	var lo := bounds_min()
	var hi := bounds_max()
	material.set_shader_parameter(&"box_min", lo)
	material.set_shader_parameter(&"box_max", hi)
	material.set_shader_parameter(&"box_offset", (lo + hi) * 0.5)
	var mesh := BoxMesh.new()
	mesh.size = hi - lo
	box = MeshInstance3D.new()
	box.name = "SmokeBox"
	box.mesh = mesh
	box.position = (lo + hi) * 0.5
	box.material_override = material
	box.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(box)
	_apply_quality()


## The box's corners in the node's space, around the column's spine and its widest radius.
func bounds_min() -> Vector3:
	var r := _reach_m()
	return Vector3(-r, 0.0, -r - SPINE_WOBBLE_M)


func bounds_max() -> Vector3:
	var r := _reach_m()
	return Vector3(float(column.get("lean_m", 0.0)) + r, float(column.get("height_m", 14.0)), r + SPINE_WOBBLE_M)


func _reach_m() -> float:
	return float(column.get("top_radius_m", 4.0)) * (1.0 + 0.5 * float(column.get("edge_noise", 0.0))) + BOX_MARGIN_M


func _apply_quality() -> void:
	if material == null:
		return
	var row := (load_data().get("quality", {}) as Dictionary).get(quality, {}) as Dictionary
	material.set_shader_parameter(&"steps", int(row.get("steps", 16)))
