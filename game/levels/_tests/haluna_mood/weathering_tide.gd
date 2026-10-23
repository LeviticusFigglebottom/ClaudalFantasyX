class_name WeatheringTide
extends Node
## The zone's tide (M1-ENV-01, haluna.md §0 "Every weathering shader reads tide_line_y and the current
## water height"): moves the zone sea (a WaterSurface) to the live water height and gives it the tide
## datum. The sea publishes both as the `hymn_water_level` global (x = water Y now, y = datum; its
## `publishes_water_level` is on), and every weathering and ground shader reads that global, so the wet
## line on stone and sand follows the sea live (the Drownbell flood rig only has to animate
## `water_height_y`). M1-ENV-05: no per-material uniforms are written any more.
##
## The same node swaps the weathering shader's quality tier (compile-time variants, README
## "Quality tiers") for every registered material, keeping all authored parameters. Its tier for a
## graphics preset is graphics_presets.json presets[].tiers.weathering (GraphicsSettings.preset_tier).

enum Quality { LOW, MEDIUM, HIGH, ULTRA }

const PRESET_TIER_SYSTEM := "weathering"
const GLOBAL_WATER_LEVEL := &"hymn_water_level"
const WEATHERING_SHADERS := {
	Quality.LOW: "res://game/shaders/environment/env_weathering_low.gdshader",
	Quality.MEDIUM: "res://game/shaders/environment/env_weathering_medium.gdshader",
	Quality.HIGH: "res://game/shaders/environment/env_weathering.gdshader",
	Quality.ULTRA: "res://game/shaders/environment/env_weathering_ultra.gdshader",
}
## Tier name (graphics_presets.json presets[].tiers.weathering) -> tier.
const TIER_NAMES := {"low": Quality.LOW, "medium": Quality.MEDIUM, "high": Quality.HIGH, "ultra": Quality.ULTRA}

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
## The zone sea. It should publish the water level (publishes_water_level). Without a sea, or with
## a sea that does not publish (a warning at _ready), this node writes `hymn_water_level` itself, so
## the shaders never keep the previous zone's level (M1-NIT-02, review-sweep-L S1). The sea
## publishes in its _process, so the wet line trails a water_height_y change by one frame, and reads
## the cleared 0,0 before the sea's first frame (README "Tide").
@export var water: WaterSurface
@export var quality: Quality = Quality.HIGH:
	set(value):
		quality = value
		_apply_quality()

var _materials: Array[ShaderMaterial] = []


func _ready() -> void:
	if water != null and not water.publishes_water_level:
		push_warning(
			"WeatheringTide %s: the sea %s does not publish hymn_water_level; writing it here" % [name, water.name]
		)
	_push()


## Adds a weathering or ground material (for the tier swap). Idempotent.
func register(mat: ShaderMaterial) -> void:
	if mat == null or _materials.has(mat):
		return
	_materials.append(mat)
	if is_weathering(mat):
		_set_tier(mat)


func registered() -> Array[ShaderMaterial]:
	return _materials


## What the weathering shaders read now (hymn_water_level): x = water height, y = datum.
func water_level() -> Vector2:
	return Vector2(water_height_y, tide_line_y)


static func is_weathering(mat: ShaderMaterial) -> bool:
	return mat.shader != null and WEATHERING_SHADERS.values().has(mat.shader.resource_path)


static func quality_for_preset(preset_id: String) -> Quality:
	return TIER_NAMES.get(GraphicsSettings.preset_tier(preset_id, PRESET_TIER_SYSTEM), Quality.HIGH)


## True when this node writes `hymn_water_level` itself: there is no sea, or the sea does not publish.
func writes_water_level() -> bool:
	return water == null or not water.publishes_water_level


func _push() -> void:
	if water != null:
		water.position.y = water_height_y
		water.tide_line_y = tide_line_y
	if writes_water_level() and is_inside_tree():
		RenderingServer.global_shader_parameter_set(GLOBAL_WATER_LEVEL, water_level())


func _apply_quality() -> void:
	for mat in _materials:
		if is_weathering(mat):
			_set_tier(mat)


func _set_tier(mat: ShaderMaterial) -> void:
	var path := String(WEATHERING_SHADERS[quality])
	if mat.shader == null or mat.shader.resource_path != path:
		mat.shader = load(path) as Shader
