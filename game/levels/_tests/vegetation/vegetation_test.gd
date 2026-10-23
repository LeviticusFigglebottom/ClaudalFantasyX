class_name VegetationTestScene
extends Node3D
## M1-ENV-02 vegetation test scene: a Haluna beach strip at `ch02_noon`. Pins the wind globals so
## screenshot captures are deterministic, and restores the project defaults when it leaves the tree.

const PINNED_GLOBALS: Array[StringName] = [&"hymn_wind", &"hymn_wind_time", &"hymn_sun_direction"]
## Under the screenshot capture the scene swaps TAA for FXAA (M1-ENV-03, as the water test does): TAA
## history depends on how many frames a shot got and on the shot before it, so the alpha-tested
## foliage differed run to run and the shots needed a 0.018 threshold. Restored on exit.
const CAPTURE_SCENE := "res://tests/screenshots/capture.tscn"

## hymn_wind: xyz = downwind direction * speed (m/s), w = gust strength 0..1.
@export var wind := Vector4(-5.0, 0.0, -2.4, 0.6)
## hymn_wind_time is frozen at this value (seconds); advance it with `animate_wind`.
@export var wind_time_s: float = 7.4
@export var animate_wind: bool = false
## Direction towards the sun, written to hymn_sun_direction (matches the Sun node).
@export var sun_node: DirectionalLight3D

var _aa_swapped := false
var _taa_was_on := false
var _ssaa_was: Viewport.ScreenSpaceAA = Viewport.SCREEN_SPACE_AA_DISABLED


func _enter_tree() -> void:
	RenderingServer.global_shader_parameter_set(&"hymn_wind", wind)
	RenderingServer.global_shader_parameter_set(&"hymn_wind_time", wind_time_s)


func _ready() -> void:
	var top := get_tree().current_scene
	if top != null and top.scene_file_path == CAPTURE_SCENE:
		var vp := get_viewport()
		_taa_was_on = vp.use_taa
		_ssaa_was = vp.screen_space_aa
		vp.use_taa = false
		vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
		_aa_swapped = true
	if sun_node:
		RenderingServer.global_shader_parameter_set(&"hymn_sun_direction", sun_node.global_basis.z.normalized())
	set_process(animate_wind)


func _process(delta: float) -> void:
	wind_time_s += delta
	RenderingServer.global_shader_parameter_set(&"hymn_wind_time", wind_time_s)


func _exit_tree() -> void:
	if _aa_swapped:
		get_viewport().use_taa = _taa_was_on
		get_viewport().screen_space_aa = _ssaa_was
	# RenderingServer.global_shader_parameter_get is editor-only, so restore the project defaults.
	for g: StringName in PINNED_GLOBALS:
		var entry: Variant = ProjectSettings.get_setting("shader_globals/%s" % g)
		if entry is Dictionary:
			RenderingServer.global_shader_parameter_set(g, (entry as Dictionary).get("value"))
