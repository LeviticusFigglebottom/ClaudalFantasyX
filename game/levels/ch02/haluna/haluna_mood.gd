class_name HalunaMood
extends Node3D
## The Haluna five-shot mood test (M1-ENV-01), graded to the `ch02_noon` sub-frame (haluna.md §0).
## - places the sun from the sub-frame's elevation/azimuth (azimuth clockwise from north = -Z);
## - writes the hymn_* shader globals (wind, weather clock, sun direction, time of day; glimmer off:
##   noon has no glimmer and no sea-glow) and restores the project defaults on exit;
## - advances the weather clock by frame_step_s per rendered frame. The haluna_* shots hold it and
##   swap TAA for FXAA through their shots.json `setup` (M1-RND-13: `hymn_wind_time` = start_time_s,
##   viewport use_taa off, FXAA), so a shot is identical wherever it sits in shots.json.
## - M2-ARC-02 (m2-slice): the wind and the weather clock are WeatherClock's in play; the rig writes them
##   only when it owns the weather (no WeatherClock, or one held by the capture). See owns_weather().
## - M2-ENV-02: `mood` &"night" switches to the `ch02_night` sub-frame (color script; haluna.md H10):
##   the sun off and the Moon on (#9DB4D9 at 0.25, 38 deg, the hymn_sun_direction global follows it),
##   the night Environment (star sky, exposure 1.1), sea-glow 0.12 with the `night_sea` look (deep
##   colour, absorption x1.0, caustics 0.25; on a copy of the sea's material), the glimmer gate open
##   (it gates sea-glow), and the dresser's oil lamps shown. Day is the scene as authored; switching
##   back restores it.

const GLOBAL_WIND := &"hymn_wind"
const GLOBAL_WIND_TIME := &"hymn_wind_time"
const GLOBAL_SUN := &"hymn_sun_direction"
const GLOBAL_TIME_OF_DAY := &"hymn_time_of_day"
const GLOBAL_GLIMMER := &"hymn_glimmer"
const MOOD_DAY := &"day"
const MOOD_NIGHT := &"night"
const PARAM_DEEP := &"col_deep"
const PARAM_CAUSTICS := &"caustic_strength"
const PARAM_ABSORPTION_SCALE := &"absorption_scale"
## hymn_glimmer by day: the alpha 0 keeps the glimmer and the sea-glow gate shut.
const DAY_GLIMMER := Vector4(1.0, 0.91, 0.72, 0.0)
## Written only while the rig owns the weather (owns_weather).
const WEATHER_GLOBALS: Array[StringName] = [GLOBAL_WIND, GLOBAL_WIND_TIME]
const PINNED_GLOBALS: Array[StringName] = [
	GLOBAL_WIND, GLOBAL_WIND_TIME, GLOBAL_SUN, GLOBAL_TIME_OF_DAY, GLOBAL_GLIMMER
]

@export var sun: DirectionalLight3D
@export var tide: WeatheringTide
## The sea; its fine grid follows whichever shot camera is current.
@export var water: WaterSurface
@export var moon: DirectionalLight3D
@export var world_environment: WorldEnvironment
@export var dresser: HalunaDresser
## &"day" (ch02_noon, as authored) or &"night" (ch02_night). Takes effect at once when set in the tree.
@export var mood: StringName = MOOD_DAY:
	set(value):
		mood = value
		if is_node_ready():
			_apply_mood()
@export_group("Sub-frame ch02_noon (haluna.md §0)")
@export var sun_elevation_deg: float = 74.0
@export var sun_azimuth_deg: float = 165.0
@export var time_of_day_h: float = 12.5
@export_group("Sub-frame ch02_night (M2-ENV-02)")
@export var night_environment: Environment
@export var moon_elevation_deg: float = 38.0
@export var moon_azimuth_deg: float = 200.0
@export var night_time_of_day_h: float = 21.5
@export_range(0.0, 0.15, 0.001) var night_sea_glow: float = 0.12
@export var night_deep_color := Color("#061A2B")
@export var night_caustic_strength: float = 0.25
## The `night_sea` water look's absorption scale (color script: x1.0; noon's lagoon_clear is x1.5).
@export var night_absorption_scale: float = 1.0
## hymn_glimmer at night: held cyan (glimmer_held #7FC6D9, linear) at 0.6; its alpha opens the
## sea-glow gate (glimmer.gdshaderinc), as in the water test's validated `water_night`.
@export var night_glimmer := Vector4(0.2122, 0.5647, 0.6939, 0.6)
@export_group("Weather")
## Weather clock at frame 0 (s); the screenshot shots pin hymn_wind_time to it.
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
var _day_environment: Environment
## The rig wrote hymn_wind / hymn_wind_time (owns_weather), so _exit_tree restores them.
var _wrote_weather := false
var _day_water_material: ShaderMaterial


func _enter_tree() -> void:
	_clock = start_time_s
	_write_globals()


func _ready() -> void:
	if sun != null:
		var toward := direction_from_angles(sun_elevation_deg, sun_azimuth_deg)
		sun.global_basis = Basis.looking_at(-toward, Vector3.UP)
	if tide != null:
		tide.water_height_y = water_height_m
	if moon != null:
		var toward_moon := direction_from_angles(moon_elevation_deg, moon_azimuth_deg)
		moon.global_basis = Basis.looking_at(-toward_moon, Vector3.UP)
	if world_environment != null:
		_day_environment = world_environment.environment
	if water != null:
		_day_water_material = water.material
	if is_night():
		_apply_mood()
	_write_globals()


func is_night() -> bool:
	return mood == MOOD_NIGHT


## Puts the scene in `mood`. Day restores everything the night changed.
func _apply_mood() -> void:
	var night := is_night()
	if sun != null:
		sun.visible = not night
	if moon != null:
		moon.visible = night
	if world_environment != null and night_environment != null:
		world_environment.environment = night_environment if night else _day_environment
	if water != null and _day_water_material != null:
		if night:
			var mat := _day_water_material.duplicate() as ShaderMaterial
			mat.set_shader_parameter(PARAM_DEEP, night_deep_color)
			mat.set_shader_parameter(PARAM_CAUSTICS, night_caustic_strength)
			mat.set_shader_parameter(PARAM_ABSORPTION_SCALE, night_absorption_scale)
			water.material = mat
		else:
			water.material = _day_water_material
		water.sea_glow_energy = night_sea_glow if night else 0.0
	var lamps := dresser.night_lamps() if dresser != null else null
	if lamps != null:
		lamps.visible = night
	_write_globals()


func _process(_delta: float) -> void:
	if water != null:
		water.follow_target = get_viewport().get_camera_3d()
	_frames += 1
	_clock = start_time_s + _frames * frame_step_s
	_write_globals()


func _exit_tree() -> void:
	# Through ShaderGlobals, so its copy of the sun does not outlive the scene (M1-ENV-09).
	for g: StringName in PINNED_GLOBALS:
		if g in WEATHER_GLOBALS and not _wrote_weather:
			continue  # the WeatherClock owner's: the clock is never reset (M2-ARC-02)
		ShaderGlobals.reset(g)


## Unit vector toward a body at elevation/azimuth (deg), with north = -Z and east = +X.
static func direction_from_angles(elevation_deg: float, azimuth_deg: float) -> Vector3:
	var e := deg_to_rad(elevation_deg)
	var a := deg_to_rad(azimuth_deg)
	return Vector3(cos(e) * sin(a), sin(e), -cos(e) * cos(a))


func weather_time() -> float:
	return _clock


## True when this rig drives the weather clock and wind itself: when no WeatherClock runs (a scene
## run on its own) or something holds it (the screenshot capture, so the mood shots stay pinned). In
## play the WeatherClock owner (M2-ARC-02) writes both, with zone_weather.json's Haluna row (the same
## trade wind as this rig's), and this rig must not be a second writer.
static func owns_weather() -> bool:
	var wc := WeatherClock.current()
	return wc == null or wc.is_held()


func _write_globals() -> void:
	if owns_weather():
		var wind := direction_from_angles(0.0, wind_azimuth_deg) * wind_speed_m_s
		RenderingServer.global_shader_parameter_set(GLOBAL_WIND, Vector4(wind.x, 0.0, wind.z, wind_gust))
		RenderingServer.global_shader_parameter_set(GLOBAL_WIND_TIME, _clock)
		_wrote_weather = true
	if is_night():
		ShaderGlobals.set_value(GLOBAL_SUN, direction_from_angles(moon_elevation_deg, moon_azimuth_deg))
		RenderingServer.global_shader_parameter_set(GLOBAL_TIME_OF_DAY, night_time_of_day_h)
	else:
		ShaderGlobals.set_value(GLOBAL_SUN, direction_from_angles(sun_elevation_deg, sun_azimuth_deg))
		RenderingServer.global_shader_parameter_set(GLOBAL_TIME_OF_DAY, time_of_day_h)
	RenderingServer.global_shader_parameter_set(GLOBAL_GLIMMER, glimmer())


## The hymn_glimmer value this mood writes (its alpha gates the sea-glow).
func glimmer() -> Vector4:
	return night_glimmer if is_night() else DAY_GLIMMER
