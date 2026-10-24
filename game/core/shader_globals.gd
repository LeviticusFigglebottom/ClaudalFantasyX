class_name ShaderGlobals
extends RefCounted
## Writes the project's global shader uniforms (project.godot [shader_globals], e.g. hymn_sun_direction)
## and keeps a CPU-side copy of what was written. RenderingServer.global_shader_parameter_get only
## works in the editor, so gameplay code that needs the value (VegetationPlant's shelter probe aims at
## the sun, M1-ENV-03) reads it here. Scripts that drive a global write it through set_value().
##
## Zone globals (M1-RND-23, review-sweep-J S2): ZONE_GLOBALS are written back to their project.godot
## defaults on every scene swap, so a zone that never writes one does not inherit the last zone's
## value. `ShaderGlobals.install(SceneRouter)` connects that reset to SceneRouter.scene_swapping (fired
## under the opaque fade, just before the new scene enters), so the router names no system that owns
## a global. Add a global here when a zone sets it and the next zone must not see it.

## The per-zone globals: the zone night sea-glow (GlimmerField.set_scene_sea_glow) and the water level
## (the zone sea's WaterSurface, or a WeatheringTide without one).
const ZONE_GLOBALS: Array[StringName] = [&"hymn_zone_sea_glow", &"hymn_water_level"]
const ROUTER_SIGNAL := &"scene_swapping"
const SETTING_PREFIX := "shader_globals/"

static var _values: Dictionary = {}


## Sets the global uniform `name` for every shader and remembers the value.
static func set_value(name: StringName, value: Variant) -> void:
	RenderingServer.global_shader_parameter_set(name, value)
	_values[name] = value


## The last value written through set_value(), else `fallback`.
static func get_value(name: StringName, fallback: Variant = null) -> Variant:
	return _values.get(name, fallback)


## Connects reset_zone_values to `router`'s scene_swapping(scene_path) signal. Idempotent; false when
## the router has no such signal.
static func install(router: Node) -> bool:
	if not router.has_signal(ROUTER_SIGNAL):
		return false
	var hook := Callable(ShaderGlobals, &"_on_scene_swapping")
	if not router.is_connected(ROUTER_SIGNAL, hook):
		router.connect(ROUTER_SIGNAL, hook)
	return true


## Writes every ZONE_GLOBALS entry back to its project.godot default.
static func reset_zone_values() -> void:
	for name in ZONE_GLOBALS:
		set_value(name, project_default(name))


## The default a global is registered with in project.godot ([shader_globals]), else null.
static func project_default(name: StringName) -> Variant:
	var key := SETTING_PREFIX + String(name)
	if not ProjectSettings.has_setting(key):
		return null
	return (ProjectSettings.get_setting(key) as Dictionary).get("value")


static func _on_scene_swapping(_scene_path: String) -> void:
	reset_zone_values()
