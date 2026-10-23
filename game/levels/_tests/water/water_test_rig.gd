class_name WaterTestRig
extends Node3D
## Drives the water test scene (M1-RND-01) deterministically for screenshot capture:
## - writes the hymn_* shader globals (wind, weather clock, sun direction) every frame from data;
## - places the sun from the color-script elevation/azimuth (azimuth clockwise from north = -Z);
## - switches to the night mood (moon, oil lamp, sea-glow) while night_camera is current, or holds
##   the mood named by `mood`.
## The clock counts rendered frames at a fixed step (frame_step_s), not engine delta. The screenshot
## shots hold it through their shots.json `setup` (M1-RND-13): `hymn_wind_time` pinned to
## start_time_s, FXAA instead of TAA, and the mood as `mood`, because capture.gd gives the first shot
## of a run one process frame fewer than later shots (a moving sea would shift by a frame, RMSE
## ~0.012, depending on the shot's position in shots.json) and TAA history depends on it too.

const GLOBAL_WIND := &"hymn_wind"
const GLOBAL_WIND_TIME := &"hymn_wind_time"
const GLOBAL_SUN := &"hymn_sun_direction"
const GLOBAL_TIME_OF_DAY := &"hymn_time_of_day"
const GLOBAL_GLIMMER := &"hymn_glimmer"
const PARAM_DEEP := &"col_deep"
const PARAM_CAUSTICS := &"caustic_strength"
const MOOD_DAY := &"day"
const MOOD_NIGHT := &"night"

@export var water: WaterSurface
@export var sun: DirectionalLight3D
@export var moon: DirectionalLight3D
@export var night_nodes: Array[Node3D] = []
@export var night_camera: Camera3D
## Mood to hold: &"day" or &"night". Empty: night while night_camera is current, day otherwise.
@export var mood: StringName = &""
@export_group("Day (color script ch02_noon)")
@export var sun_elevation_deg: float = 74.0
@export var sun_azimuth_deg: float = 165.0
@export var day_time_of_day_h: float = 12.5
@export var day_deep_color := Color("#1569A0")
@export var day_caustic_strength: float = 1.6
@export_group("Night (color script ch02_night)")
@export var moon_elevation_deg: float = 38.0
@export var moon_azimuth_deg: float = 200.0
@export var night_time_of_day_h: float = 21.5
@export var night_deep_color := Color("#061A2B")
@export var night_sea_glow: float = 0.12
## Moonlight focuses into caustics too, but faintly.
@export var night_caustic_strength: float = 0.25
## hymn_glimmer at night: held cyan (glimmer_held #7FC6D9, linear) at the ch04 emission 0.6. Its
## alpha also gates the sea-glow on (glimmer.gdshaderinc); by day the alpha is 0.
@export var night_glimmer := Vector4(0.2122, 0.5647, 0.6939, 0.6)
@export_group("Weather")
## Weather clock at frame 0 (s). Any value works; it only picks which moment the shots show.
@export var start_time_s: float = 40.0
## Seconds the weather clock advances per rendered frame (1/60: the capture runs at 60 fps).
@export var frame_step_s: float = 1.0 / 60.0
## Wind travel direction (azimuth, deg) and speed (m/s); w = gust strength.
@export var wind_azimuth_deg: float = 250.0
@export var wind_speed_m_s: float = 6.0
@export_range(0.0, 1.0) var wind_gust: float = 0.3

var _clock: float = 0.0
var _frames: int = 0
var _night: bool = false


func _ready() -> void:
	_clock = start_time_s
	_apply_mood(false)
	_write_globals()


func _process(_delta: float) -> void:
	_frames += 1
	_clock = start_time_s + _frames * frame_step_s
	var want_night := wants_night()
	if want_night != _night:
		_apply_mood(want_night)
	_write_globals()


## Unit vector toward a body at elevation/azimuth (deg), with north = -Z and east = +X.
static func direction_from_angles(elevation_deg: float, azimuth_deg: float) -> Vector3:
	var e := deg_to_rad(elevation_deg)
	var a := deg_to_rad(azimuth_deg)
	return Vector3(cos(e) * sin(a), sin(e), -cos(e) * cos(a))


func weather_time() -> float:
	return _clock


## The mood this frame: `mood` when set, else night while night_camera is current.
func wants_night() -> bool:
	if mood != &"":
		return mood == MOOD_NIGHT
	var cam := get_viewport().get_camera_3d()
	return cam != null and cam == night_camera


func _apply_mood(night: bool) -> void:
	_night = night
	if sun != null:
		sun.visible = not night
		_aim(sun, direction_from_angles(sun_elevation_deg, sun_azimuth_deg))
	if moon != null:
		moon.visible = night
		_aim(moon, direction_from_angles(moon_elevation_deg, moon_azimuth_deg))
	for n in night_nodes:
		if n != null:
			n.visible = night
	if water != null:
		water.sea_glow_energy = night_sea_glow if night else 0.0
		if water.material != null:
			water.material.set_shader_parameter(PARAM_DEEP, night_deep_color if night else day_deep_color)
			water.material.set_shader_parameter(
				PARAM_CAUSTICS, night_caustic_strength if night else day_caustic_strength
			)


func _aim(light: DirectionalLight3D, toward: Vector3) -> void:
	# A DirectionalLight3D shines along its -Z axis: point +Z at the body.
	var up := Vector3.UP if absf(toward.y) < 0.999 else Vector3.FORWARD
	light.global_basis = Basis.looking_at(-toward, up)


func _write_globals() -> void:
	var wind_dir := direction_from_angles(0.0, wind_azimuth_deg)
	var wind := wind_dir * wind_speed_m_s
	RenderingServer.global_shader_parameter_set(GLOBAL_WIND, Vector4(wind.x, 0.0, wind.z, wind_gust))
	RenderingServer.global_shader_parameter_set(GLOBAL_WIND_TIME, _clock)
	var body := moon_elevation_deg if _night else sun_elevation_deg
	var az := moon_azimuth_deg if _night else sun_azimuth_deg
	RenderingServer.global_shader_parameter_set(GLOBAL_SUN, direction_from_angles(body, az))
	RenderingServer.global_shader_parameter_set(
		GLOBAL_TIME_OF_DAY, night_time_of_day_h if _night else day_time_of_day_h
	)
	var glimmer := night_glimmer if _night else Vector4(night_glimmer.x, night_glimmer.y, night_glimmer.z, 0.0)
	RenderingServer.global_shader_parameter_set(GLOBAL_GLIMMER, glimmer)
