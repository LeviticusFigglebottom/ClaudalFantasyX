class_name UndertowTestRig
extends Node3D
## Drives the Undertow test scene (M1-RND-03) the way a zone or cutscene would, deterministically:
## - writes the hymn_* globals (wind, weather clock, sun direction, glimmer) every frame;
## - picks the mood (dusk, high-angle eye, night) from the current camera and applies it: key light,
##   environment, storm placement, wound intensity, the sea-glow and the held motes;
## - holds the storm clock and the weather clock at the mood's time while the screenshot capture
##   runs (capture.gd gives the first shot one process frame fewer), and swaps TAA for FXAA there.
## Moods are data (the MOODS table below is the test's "cutscene"); the storm's tunables live in
## game/data/vfx/undertow.json.

const GLOBAL_WIND := &"hymn_wind"
const GLOBAL_WIND_TIME := &"hymn_wind_time"
const GLOBAL_SUN := &"hymn_sun_direction"
const GLOBAL_TIME_OF_DAY := &"hymn_time_of_day"
const CAPTURE_SCENE := "res://tests/screenshots/capture.tscn"
const MOOD_DUSK := &"dusk"
const MOOD_EYE := &"eye"
const MOOD_NIGHT := &"night"
## The dusk mood with the storm forced to the Low tier (shells), to show Low still reads.
const MOOD_DUSK_LOW := &"dusk_low"
const LOW_TIER := "low"

@export var storm: UndertowStorm
@export var water: WaterSurface
@export var sun: DirectionalLight3D
@export var moon: DirectionalLight3D
@export var world_environment: WorldEnvironment
@export var env_dusk: Environment
@export var env_night: Environment
@export var motes: GlimmerField
@export var horizon_camera: Camera3D
@export var eye_camera: Camera3D
@export var night_camera: Camera3D
@export var low_camera: Camera3D
## Shown only at night (the lighthouse's oil lamp).
@export var night_nodes: Array[Node3D] = []
@export var frame_step_s: float = 1.0 / 60.0
@export var weather_start_s: float = 40.0
@export var wind_azimuth_deg: float = 250.0
@export var wind_speed_m_s: float = 11.0
@export_range(0.0, 1.0) var wind_gust: float = 0.6

## Per mood (the test's "cutscene" data): key light elevation and azimuth (deg, azimuth clockwise
## from north), colour and energy; time of day (h); storm clock (s); approach distance (m); wound
## intensity; scene glimmer energy (hymn_glimmer.a, the colour-script mote energy); the storm's
## ambient energy, haze colour and visibility; sea-glow energy; a forced flash (site, -1 = none,
## struck flash_age s before the frame); and the world point the mood's camera looks at.
@export var moods: Dictionary = {
	MOOD_DUSK:
	{
		"elevation": 5.0,
		"azimuth": 262.0,
		"sun_color": Color(0.949, 0.651, 0.29),
		"sun_energy": 2.2,
		"tod": 18.4,
		"time": 205.0,
		"distance": 17000.0,
		"wounds": 1.0,
		"glimmer": 0.6,
		"ambient": 0.6,
		"haze": Color(0.435, 0.416, 0.459),
		"sea_glow": 0.04,
		"flash": 1,
		"flash_age": 0.03,
		"look_at": Vector3(1000.0, 300.0, 0.0),
	},
	MOOD_EYE:
	{
		"elevation": 21.0,
		"azimuth": 245.0,
		"tod": 17.0,
		"sun_color": Color(1.0, 0.824, 0.478),
		"sun_energy": 2.6,
		"time": 205.0,
		"distance": 17000.0,
		"wounds": 1.2,
		"glimmer": 0.6,
		"ambient": 0.35,
		"visibility": 120000.0,
		"haze": Color(0.435, 0.416, 0.459),
		"sea_glow": 0.04,
		"flash": 2,
		"flash_age": 0.02,
		"look_at": Vector3(17000.0, 0.0, 0.0),
	},
	MOOD_NIGHT:
	{
		"elevation": 24.0,
		"azimuth": 215.0,
		"tod": 22.0,
		"time": 340.0,
		"distance": 15000.0,
		"wounds": 1.6,
		"glimmer": 1.5,
		"ambient": 0.12,
		"haze": Color(0.078, 0.133, 0.208),
		"sea_glow": 0.08,
		"flash": 0,
		"flash_age": 0.25,
		"look_at": Vector3(1000.0, 198.0, -60.0),
	},
}

var _frames: int = 0
var _hold: bool = false
var _mood: StringName = &""
var _base_quality: String = ""
var _weather_s: float = 0.0
var _taa_was_on: bool = false
var _ssaa_was: Viewport.ScreenSpaceAA = Viewport.SCREEN_SPACE_AA_DISABLED


func _ready() -> void:
	var top := get_tree().current_scene
	_hold = top != null and top.scene_file_path == CAPTURE_SCENE
	if _hold:
		var vp := get_viewport()
		_taa_was_on = vp.use_taa
		_ssaa_was = vp.screen_space_aa
		vp.use_taa = false
		vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	if storm != null:
		storm.playing = not _hold
		_base_quality = storm.get_quality()
	_weather_s = weather_start_s
	_aim_camera(horizon_camera, MOOD_DUSK)
	_aim_camera(eye_camera, MOOD_EYE)
	_aim_camera(night_camera, MOOD_NIGHT)
	_aim_camera(low_camera, MOOD_DUSK)
	_apply_mood(_mood_for(get_viewport().get_camera_3d()))


func _process(_delta: float) -> void:
	_frames += 1
	if not _hold:
		_weather_s = weather_start_s + _frames * frame_step_s
	var want := _mood_for(get_viewport().get_camera_3d())
	if want != _mood:
		_apply_mood(want)
	_write_globals()


func current_mood() -> StringName:
	return _mood


func _mood_for(cam: Camera3D) -> StringName:
	if cam != null and cam == night_camera:
		return MOOD_NIGHT
	if cam != null and cam == eye_camera:
		return MOOD_EYE
	if cam != null and cam == low_camera:
		return MOOD_DUSK_LOW
	return MOOD_DUSK


func _apply_mood(mood: StringName) -> void:
	_mood = mood
	var m := moods.get(MOOD_DUSK if mood == MOOD_DUSK_LOW else mood, {}) as Dictionary
	var night := mood == MOOD_NIGHT
	if sun != null:
		sun.visible = not night
		sun.light_color = m.get("sun_color", sun.light_color) as Color
		sun.light_energy = float(m.get("sun_energy", sun.light_energy))
		_aim(sun, WaterTestRig.direction_from_angles(float(m.get("elevation", 0.0)), float(m.get("azimuth", 0.0))))
	if moon != null:
		moon.visible = night
		_aim(moon, WaterTestRig.direction_from_angles(float(m.get("elevation", 0.0)), float(m.get("azimuth", 0.0))))
	for n in night_nodes:
		if n != null:
			n.visible = night
	if world_environment != null:
		world_environment.environment = env_night if night else env_dusk
	if water != null:
		water.sea_glow_energy = float(m.get("sea_glow", 0.0))
	GlimmerField.set_scene_glimmer(Color("#7FC6D9"), float(m.get("glimmer", 0.0)))
	if storm != null:
		var tier := LOW_TIER if mood == MOOD_DUSK_LOW else _base_quality
		if tier != "" and tier != storm.get_quality():
			storm.set_quality(tier)
		storm.sun = moon if night else sun
		storm.approach_distance_m = float(m.get("distance", 0.0))
		storm.wound_intensity = float(m.get("wounds", 1.0))
		storm.ambient_energy = float(m.get("ambient", 1.0))
		storm.haze_color = m.get("haze", storm.haze_color) as Color
		storm.haze_visibility_m = float(m.get("visibility", 0.0))
		var t := float(m.get("time", 0.0))
		storm.state.clear_forced_flashes()
		var site := int(m.get("flash", -1))
		if site >= 0:
			storm.force_flash(site, t - float(m.get("flash_age", 0.0)))
		storm.set_time(t)
	_write_globals()


func _aim_camera(cam: Camera3D, mood: StringName) -> void:
	var m := moods.get(mood, {}) as Dictionary
	if cam != null and m.has("look_at"):
		cam.look_at(m["look_at"] as Vector3, Vector3.UP)


func _aim(light: DirectionalLight3D, toward: Vector3) -> void:
	var up := Vector3.UP if absf(toward.y) < 0.999 else Vector3.FORWARD
	light.global_basis = Basis.looking_at(-toward, up)


func _write_globals() -> void:
	var m := moods.get(MOOD_DUSK if _mood == MOOD_DUSK_LOW else _mood, {}) as Dictionary
	var wind := WaterTestRig.direction_from_angles(0.0, wind_azimuth_deg) * wind_speed_m_s
	RenderingServer.global_shader_parameter_set(GLOBAL_WIND, Vector4(wind.x, 0.0, wind.z, wind_gust))
	RenderingServer.global_shader_parameter_set(GLOBAL_WIND_TIME, _weather_s)
	var dir := WaterTestRig.direction_from_angles(float(m.get("elevation", 0.0)), float(m.get("azimuth", 0.0)))
	RenderingServer.global_shader_parameter_set(GLOBAL_SUN, dir)
	RenderingServer.global_shader_parameter_set(GLOBAL_TIME_OF_DAY, float(m.get("tod", 12.0)))


func _exit_tree() -> void:
	GlimmerField.set_scene_glimmer(Color("#7FC6D9"), 0.0)
	if _hold:
		get_viewport().use_taa = _taa_was_on
		get_viewport().screen_space_aa = _ssaa_was
