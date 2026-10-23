@tool
class_name WaterSurface
extends Node3D
## A body of water (M1-RND-01, SPEC §8.2 item 1). Place one per sea/lagoon/pool; docs/kb/tech/water.md.
##
## Owns: the wave field (wave_set), the look (material: a ShaderMaterial authored per zone), the
## quality tier (which compiled shader variant the material runs), and the surface mesh. It pushes
## the packed wave constants into the material, so the shader and height_at() always agree.
##
## Gameplay queries (world space; `time` is the weather clock, the value of hymn_wind_time):
##   water.height_at(Vector2(x, z), time) -> world Y of the surface
##   water.normal_at(Vector2(x, z), time) -> world normal
## Keep the node unrotated and unscaled: waves live in world XZ, only its Y offsets the rest plane.

enum Quality { LOW, MEDIUM, HIGH, ULTRA }

const OCEAN_SHADERS := {
	Quality.LOW: "res://game/shaders/water/water_ocean_low.gdshader",
	Quality.MEDIUM: "res://game/shaders/water/water_ocean_medium.gdshader",
	Quality.HIGH: "res://game/shaders/water/water_ocean.gdshader",
	Quality.ULTRA: "res://game/shaders/water/water_ocean_ultra.gdshader",
}
## Rivers have two variants: the flowmap shader is light, so Medium+ share the High one.
const RIVER_SHADERS := {
	Quality.LOW: "res://game/shaders/water/water_river_low.gdshader",
	Quality.MEDIUM: "res://game/shaders/water/water_river.gdshader",
	Quality.HIGH: "res://game/shaders/water/water_river.gdshader",
	Quality.ULTRA: "res://game/shaders/water/water_river.gdshader",
}
## Tier names as graphics_presets.json presets[].tiers.water spells them (M1-RND-07: the preset ->
## tier map lives in the presets file now).
const QUALITY_NAMES := {
	"low": Quality.LOW,
	"medium": Quality.MEDIUM,
	"high": Quality.HIGH,
	"ultra": Quality.ULTRA,
}
const PRESET_TIER_SYSTEM := "water"
const SURFACE_NODE := &"Surface"
const PARAM_SEA_GLOW := &"sea_glow_energy"
const GLOBAL_WATER_LEVEL := &"hymn_water_level"

@export var wave_set: WaveSet:
	set(value):
		wave_set = value
		_refresh()
@export var material: ShaderMaterial:
	set(value):
		material = value
		_refresh()
@export var quality: Quality = Quality.HIGH:
	set(value):
		quality = value
		_refresh()
## Use the flowmap (river) shader: material needs tex_flow; set surface_mesh to the channel mesh.
@export var river: bool = false:
	set(value):
		river = value
		_refresh()
## Night sea-glow energy (color script rule 3: 0.04-0.15 at night). It shows only while hymn_glimmer.a > 0.
@export_range(0.0, 0.15, 0.001) var sea_glow_energy: float = 0.0:
	set(value):
		sea_glow_energy = value
		if material != null:
			material.set_shader_parameter(PARAM_SEA_GLOW, value)

@export_group("Water level")
## World Y of the zone's tide-line datum (stone weathering keys its wet band to it). The current level
## is this node's Y: animate the node (tide, Drownbell flood) and everything follows.
@export var tide_line_y: float = 0.0
## Write hymn_water_level (current level, datum) every frame. Leave on for the zone's sea only: pools
## and rivers should not drive the zone's weathering.
@export var publishes_water_level: bool = true

@export_group("Mesh")
## Optional authored mesh (rivers, pools). Empty = generate the ocean grid below.
@export var surface_mesh: Mesh:
	set(value):
		surface_mesh = value
		_rebuild_mesh()
@export_range(1.0, 1000.0, 0.5, "suffix:m") var core_half_extent_m: float = 48.0
@export_range(0.05, 10.0, 0.01, "suffix:m") var core_cell_m: float = 0.5
@export_range(1.0, 20000.0, 1.0, "suffix:m") var outer_half_extent_m: float = 3000.0
@export_range(1.0, 2.0, 0.01) var cell_growth: float = 1.1
## Optional: keep the grid centred under this node (usually the active camera), snapped to whole
## core cells so the fine grid never swims.
@export var follow_target: Node3D

var _waves := GerstnerWaves.new()
var _surface: MeshInstance3D


func _ready() -> void:
	_rebuild_mesh()
	_refresh()


func _process(_delta: float) -> void:
	if publishes_water_level:
		var level := water_level()
		RenderingServer.global_shader_parameter_set(GLOBAL_WATER_LEVEL, level)
	if follow_target == null or _surface == null:
		return
	var p := follow_target.global_position
	var snap := core_cell_m * 2.0
	_surface.global_position = Vector3(snappedf(p.x, snap), global_position.y, snappedf(p.z, snap))


## What hymn_water_level carries: x = the rest plane's world Y now, y = tide_line_y.
func water_level() -> Vector2:
	return Vector2(global_position.y if is_inside_tree() else position.y, tide_line_y)


## World Y of the water surface above or below world point (xz.x, xz.y) at weather time `time`.
func height_at(xz: Vector2, time: float) -> float:
	return global_position.y + _waves.height_at(xz, time)


func normal_at(xz: Vector2, time: float) -> Vector3:
	return _waves.normal_at(xz, time)


## The packed wave field (shared with the shader); read-only use.
func waves() -> GerstnerWaves:
	return _waves


func surface() -> MeshInstance3D:
	return _surface


static func quality_for_preset(preset_id: String) -> Quality:
	return QUALITY_NAMES.get(GraphicsSettings.preset_tier(preset_id, PRESET_TIER_SYSTEM), Quality.HIGH)


static func shader_path(tier: Quality, is_river: bool) -> String:
	return String((RIVER_SHADERS if is_river else OCEAN_SHADERS)[tier])


func _refresh() -> void:
	_waves = GerstnerWaves.from_set(wave_set)
	if material == null:
		return
	var path := shader_path(quality, river)
	if material.shader == null or material.shader.resource_path != path:
		material.shader = load(path) as Shader
	var params := _waves.shader_parameters()
	for key: StringName in params:
		material.set_shader_parameter(key, params[key])
	material.set_shader_parameter(PARAM_SEA_GLOW, sea_glow_energy)
	if _surface != null:
		_surface.material_override = material
		_update_aabb()


func _rebuild_mesh() -> void:
	if not is_inside_tree():
		return
	if _surface == null:
		_surface = MeshInstance3D.new()
		_surface.name = SURFACE_NODE
		_surface.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(_surface, false, Node.INTERNAL_MODE_FRONT)
	if surface_mesh != null:
		_surface.mesh = surface_mesh
	else:
		_surface.mesh = WaterMeshBuilder.build(core_half_extent_m, core_cell_m, outer_half_extent_m, cell_growth)
	_surface.material_override = material
	_update_aabb()


# Displacement moves vertices outside the flat mesh's bounds; grow the cull box to match.
func _update_aabb() -> void:
	if _surface == null or _surface.mesh == null:
		return
	var margin := _waves.amplitude_sum
	_surface.extra_cull_margin = margin
