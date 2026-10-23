class_name VegetationTestScene
extends Node3D
## M1-ENV-02 vegetation test scene: a Haluna beach strip at `ch02_noon`. Pins the wind globals so
## screenshot captures are deterministic, and restores the project defaults when it leaves the tree.

const PINNED_GLOBALS: Array[StringName] = [&"hymn_wind", &"hymn_wind_time", &"hymn_sun_direction"]

## hymn_wind: xyz = downwind direction * speed (m/s), w = gust strength 0..1.
@export var wind := Vector4(-5.0, 0.0, -2.4, 0.6)
## hymn_wind_time is frozen at this value (seconds); advance it with `animate_wind`.
@export var wind_time_s: float = 7.4
@export var animate_wind: bool = false
## Direction towards the sun, written to hymn_sun_direction (matches the Sun node).
@export var sun_node: DirectionalLight3D


func _enter_tree() -> void:
	RenderingServer.global_shader_parameter_set(&"hymn_wind", wind)
	RenderingServer.global_shader_parameter_set(&"hymn_wind_time", wind_time_s)


func _ready() -> void:
	if sun_node:
		RenderingServer.global_shader_parameter_set(&"hymn_sun_direction", sun_node.global_basis.z.normalized())
	set_process(animate_wind)


func _process(delta: float) -> void:
	wind_time_s += delta
	RenderingServer.global_shader_parameter_set(&"hymn_wind_time", wind_time_s)


func _exit_tree() -> void:
	# RenderingServer.global_shader_parameter_get is editor-only, so restore the project defaults.
	for g: StringName in PINNED_GLOBALS:
		var entry: Variant = ProjectSettings.get_setting("shader_globals/%s" % g)
		if entry is Dictionary:
			RenderingServer.global_shader_parameter_set(g, (entry as Dictionary).get("value"))
