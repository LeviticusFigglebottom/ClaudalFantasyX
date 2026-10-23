class_name HalunaMood
extends Node3D
## The Haluna five-shot mood test (M1-ENV-01), graded to the `ch02_noon` sub-frame (haluna.md §0).
## - places the sun from the sub-frame's elevation/azimuth (azimuth clockwise from north = -Z);
## - writes the hymn_* shader globals (wind, weather clock, sun direction, time of day; glimmer off:
##   noon has no glimmer and no sea-glow) and restores the project defaults on exit;
## - holds the weather clock under the screenshot capture and swaps TAA for FXAA there, so a shot is
##   identical wherever it sits in shots.json (the water rig's approach, water.md "Gotchas").

const GLOBAL_WIND := &"hymn_wind"
const GLOBAL_WIND_TIME := &"hymn_wind_time"
const GLOBAL_SUN := &"hymn_sun_direction"
const GLOBAL_TIME_OF_DAY := &"hymn_time_of_day"
const GLOBAL_GLIMMER := &"hymn_glimmer"
const PINNED_GLOBALS: Array[StringName] = [
	GLOBAL_WIND, GLOBAL_WIND_TIME, GLOBAL_SUN, GLOBAL_TIME_OF_DAY, GLOBAL_GLIMMER
]
const CAPTURE_SCENE := "res://tests/screenshots/capture.tscn"

@export var sun: DirectionalLight3D
@export var tide: WeatheringTide
## The sea; its fine grid follows whichever shot camera is current.
@export var water: WaterSurface
@export_group("Sub-frame ch02_noon (haluna.md §0)")
@export var sun_elevation_deg: float = 74.0
@export var sun_azimuth_deg: float = 165.0
@export var time_of_day_h: float = 12.5
@export_group("Weather")
## Weather clock at frame 0 (s); held here under the capture.
@export var start_time_s: float = 40.0
@export var frame_step_s: float = 1.0 / 60.0
## Haluna trade wind: blows from the east-north-east, onshore (vegetation.md reference 6 m/s).
@export var wind_azimuth_deg: float = 250.0
@export var wind_speed_m_s: float = 6.0
@export_range(0.0, 1.0) var wind_gust: float = 0.35
@export_group("Tide")
## Water height at this moment (m above the datum). Noon on the Ch2 day: mid tide, falling.
@export var water_height_m: float = 0.15

var _clock: float = 0.0
var _frames: int = 0
var _hold_clock: bool = false
var _taa_was_on: bool = false
var _ssaa_was: Viewport.ScreenSpaceAA = Viewport.SCREEN_SPACE_AA_DISABLED


func _enter_tree() -> void:
	_clock = start_time_s
	_write_globals()


func _ready() -> void:
	var top := get_tree().current_scene
	_hold_clock = top != null and top.scene_file_path == CAPTURE_SCENE
	if _hold_clock:
		var vp := get_viewport()
		_taa_was_on = vp.use_taa
		_ssaa_was = vp.screen_space_aa
		vp.use_taa = false
		vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	if sun != null:
		var toward := direction_from_angles(sun_elevation_deg, sun_azimuth_deg)
		sun.global_basis = Basis.looking_at(-toward, Vector3.UP)
	if tide != null:
		tide.water_height_y = water_height_m
	_write_globals()


func _process(_delta: float) -> void:
	if water != null:
		water.follow_target = get_viewport().get_camera_3d()
	_frames += 1
	if not _hold_clock:
		_clock = start_time_s + _frames * frame_step_s
	_write_globals()


func _exit_tree() -> void:
	if _hold_clock:
		get_viewport().use_taa = _taa_was_on
		get_viewport().screen_space_aa = _ssaa_was
	for g: StringName in PINNED_GLOBALS:
		var entry: Variant = ProjectSettings.get_setting("shader_globals/%s" % g)
		if entry is Dictionary:
			RenderingServer.global_shader_parameter_set(g, (entry as Dictionary).get("value"))


## Unit vector toward a body at elevation/azimuth (deg), with north = -Z and east = +X.
static func direction_from_angles(elevation_deg: float, azimuth_deg: float) -> Vector3:
	var e := deg_to_rad(elevation_deg)
	var a := deg_to_rad(azimuth_deg)
	return Vector3(cos(e) * sin(a), sin(e), -cos(e) * cos(a))


func weather_time() -> float:
	return _clock


func _write_globals() -> void:
	var wind := direction_from_angles(0.0, wind_azimuth_deg) * wind_speed_m_s
	RenderingServer.global_shader_parameter_set(GLOBAL_WIND, Vector4(wind.x, 0.0, wind.z, wind_gust))
	RenderingServer.global_shader_parameter_set(GLOBAL_WIND_TIME, _clock)
	RenderingServer.global_shader_parameter_set(GLOBAL_SUN, direction_from_angles(sun_elevation_deg, sun_azimuth_deg))
	RenderingServer.global_shader_parameter_set(GLOBAL_TIME_OF_DAY, time_of_day_h)
	RenderingServer.global_shader_parameter_set(GLOBAL_GLIMMER, Vector4(1.0, 0.91, 0.72, 0.0))
