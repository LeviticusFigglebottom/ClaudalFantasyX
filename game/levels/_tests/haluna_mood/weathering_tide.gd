class_name WeatheringTide
extends Node
## Drives the tide uniforms of every weathering and ground material in a zone (M1-ENV-01,
## haluna.md §0 "Every weathering shader reads tide_line_y and the current water height"), and moves
## the WaterSurface to the same height, so the wet line on stone and sand follows the sea live (the
## Drownbell flood rig only has to animate `water_height_y`).
##
## There is no global tide uniform yet (project.godot is the Lead's; a `hymn_tide` vec2 global is
## requested in haluna_mood_review.md), so materials are registered here and written directly.
## The same node swaps the weathering shader's quality tier (compile-time variants, README
## "Quality tiers") for every registered material, keeping all authored parameters.

enum Quality { LOW, MEDIUM, HIGH, ULTRA }

const PARAM_TIDE := &"tide_line_y"
const PARAM_WATER := &"water_height_y"
const WEATHERING_SHADERS := {
	Quality.LOW: "res://game/shaders/environment/env_weathering_low.gdshader",
	Quality.MEDIUM: "res://game/shaders/environment/env_weathering_medium.gdshader",
	Quality.HIGH: "res://game/shaders/environment/env_weathering.gdshader",
	Quality.ULTRA: "res://game/shaders/environment/env_weathering_ultra.gdshader",
}
## Graphics preset id (game/data/settings/graphics_presets.json) -> tier, like WaterSurface.
const PRESET_QUALITY := {"low": Quality.LOW, "medium": Quality.MEDIUM, "high": Quality.HIGH, "ultra": Quality.ULTRA}

## Tide datum: world Y of mean sea level (haluna.md: 0.0).
@export var tide_line_y: float = 0.0:
	set(value):
		tide_line_y = value
		_push()
## Live water surface height (world Y): high water +0.9, low water -0.7 at Haluna.
@export var water_height_y: float = 0.0:
	set(value):
		water_height_y = value
		_push()
@export var water: WaterSurface
@export var quality: Quality = Quality.HIGH:
	set(value):
		quality = value
		_apply_quality()

var _materials: Array[ShaderMaterial] = []


func _ready() -> void:
	_push()


## Adds a material whose shader has the tide uniforms (weathering or ground). Idempotent.
func register(mat: ShaderMaterial) -> void:
	if mat == null or _materials.has(mat):
		return
	_materials.append(mat)
	_write(mat)
	if is_weathering(mat):
		_set_tier(mat)


func registered() -> Array[ShaderMaterial]:
	return _materials


static func is_weathering(mat: ShaderMaterial) -> bool:
	return mat.shader != null and WEATHERING_SHADERS.values().has(mat.shader.resource_path)


static func quality_for_preset(preset_id: String) -> Quality:
	return PRESET_QUALITY.get(preset_id, Quality.HIGH)


func _push() -> void:
	for mat in _materials:
		_write(mat)
	if water != null:
		water.position.y = water_height_y


func _write(mat: ShaderMaterial) -> void:
	mat.set_shader_parameter(PARAM_TIDE, tide_line_y)
	mat.set_shader_parameter(PARAM_WATER, water_height_y)


func _apply_quality() -> void:
	for mat in _materials:
		if is_weathering(mat):
			_set_tier(mat)


func _set_tier(mat: ShaderMaterial) -> void:
	var path := String(WEATHERING_SHADERS[quality])
	if mat.shader == null or mat.shader.resource_path != path:
		mat.shader = load(path) as Shader
