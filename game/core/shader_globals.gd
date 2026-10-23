class_name ShaderGlobals
extends RefCounted
## Writes the project's global shader uniforms (project.godot [shader_globals], e.g. hymn_sun_direction)
## and keeps a CPU-side copy of what was written. RenderingServer.global_shader_parameter_get only
## works in the editor, so gameplay code that needs the value (VegetationPlant's shelter probe aims at
## the sun, M1-ENV-03) reads it here. Scripts that drive a global write it through set_value().

static var _values: Dictionary = {}


## Sets the global uniform `name` for every shader and remembers the value.
static func set_value(name: StringName, value: Variant) -> void:
	RenderingServer.global_shader_parameter_set(name, value)
	_values[name] = value


## The last value written through set_value(), else `fallback`.
static func get_value(name: StringName, fallback: Variant = null) -> Variant:
	return _values.get(name, fallback)
