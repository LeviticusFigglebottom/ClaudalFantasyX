class_name ShaderGlobals
extends RefCounted
## Writes the project's global shader uniforms (project.godot [shader_globals], e.g. hymn_sun_direction)
## and keeps a CPU-side copy of what was written. RenderingServer.global_shader_parameter_get only
## works in the editor, so gameplay code that needs the value (VegetationPlant's shelter probe aims at
## the sun, M1-ENV-03) reads it here. Scripts that drive a global write it through set_value(), and
## restore it through reset(), so the copy never goes stale (M1-ENV-09).
##
## A node in LISTENERS_GROUP gets `LISTENER_METHOD(name, value)` whenever set_value() or reset() changes
## a global's value (VegetationPlant re-probes its shelter when the sun moves).

const SETTINGS_PREFIX := "shader_globals/"
const LISTENERS_GROUP := &"shader_globals_listeners"
const LISTENER_METHOD := &"_on_shader_global_changed"

static var _values: Dictionary = {}


## Sets the global uniform `name` for every shader and remembers the value.
static func set_value(name: StringName, value: Variant) -> void:
	RenderingServer.global_shader_parameter_set(name, value)
	var changed := not _same(get_value(name), value)
	_values[name] = value
	if changed:
		_notify(name, value)


## Restores the global uniform `name` to its project.godot default and forgets the written value.
static func reset(name: StringName) -> void:
	var value: Variant = default_value(name)
	if value == null:
		return
	RenderingServer.global_shader_parameter_set(name, value)
	var changed := not _same(get_value(name), value)
	_values.erase(name)
	if changed:
		_notify(name, value)


## The last value written through set_value(), else the project.godot default, else `fallback`.
static func get_value(name: StringName, fallback: Variant = null) -> Variant:
	if _values.has(name):
		return _values[name]
	var value: Variant = default_value(name)
	return fallback if value == null else value


## The project.godot [shader_globals] default of `name`, or null if it is not declared.
static func default_value(name: StringName) -> Variant:
	var entry: Variant = ProjectSettings.get_setting(SETTINGS_PREFIX + String(name))
	if entry is Dictionary:
		return (entry as Dictionary).get("value")
	return null


static func _notify(name: StringName, value: Variant) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	if tree != null:
		tree.call_group(LISTENERS_GROUP, LISTENER_METHOD, name, value)


static func _same(a: Variant, b: Variant) -> bool:
	return typeof(a) == typeof(b) and a == b
