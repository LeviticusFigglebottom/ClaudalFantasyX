class_name WeatherClock
extends Node
## The one runtime owner of the weather clock (M2-ARC-02; docs/kb/tech/architecture.md, "The weather clock").
## - **The clock:** advances `hymn_wind_time` by the frame's delta every frame, through ShaderGlobals.set_value,
##   so water, vegetation and every shader on the weather clock move in play. It is a child of the SceneRouter
##   autoload (`WeatherClock.install(SceneRouter)`, as ShaderGlobals.install), so it keeps its value across scene
##   swaps, and it is PROCESS_MODE_PAUSABLE, so it stops with the tree. The clock is never reset.
## - **The zone wind:** on SceneRouter.scene_swapping(scene_path) it writes `hymn_wind` from
##   game/data/world/zone_weather.json: the row for that scene, else the data's default. hymn_wind is not in
##   ShaderGlobals.ZONE_GLOBALS: this owner writes it on every swap, so no zone inherits the last one's wind and
##   the two handlers on the signal never depend on their order. A scene run on its own (no swap) gets its row's
##   wind on the first running frame, and nothing when it has no row.
## - **Holds:** while anything holds the clock (hold(holder) .. release(holder), or until the holder is freed), it
##   neither advances nor writes either global; a zone wind that arrives meanwhile is written on release. The
##   screenshot capture holds it for its whole run (tests/screenshots/capture.gd), so a shot's pinned globals and a
##   rig's own writes always win and no baseline moves; a cutscene can hold it, then scrub with set_time().
## - Other code reads the clock through ShaderGlobals.get_value(&"hymn_wind_time") or time_s, and never writes it.

const DATA_PATH := "res://game/data/world/zone_weather.json"
const GLOBAL_WIND := &"hymn_wind"
const GLOBAL_WIND_TIME := &"hymn_wind_time"
const ROUTER_SIGNAL := &"scene_swapping"
const NODE_NAME := &"WeatherClock"

static var _owner_ref: WeakRef = null
static var _data_cache: Dictionary = {}

## The weather clock (s): the value of hymn_wind_time while the clock runs.
var time_s: float = 0.0
## The scene whose zone wind was applied last (or is waiting for a release), "" before any.
var zone_path: String = ""

## instance id -> WeakRef of each object holding the clock.
var _holds: Dictionary = {}
var _wind_pending := false
var _started := false


## Adds the owner under `router` and connects it to the router's scene_swapping(scene_path) signal. Idempotent:
## returns the owner already there. Null when the router has no such signal.
static func install(router: Node) -> WeatherClock:
	if not router.has_signal(ROUTER_SIGNAL):
		return null
	var clock := router.get_node_or_null(NodePath(String(NODE_NAME))) as WeatherClock
	if clock == null:
		clock = WeatherClock.new()
		clock.name = NODE_NAME
		router.add_child(clock)
	var hook := Callable(clock, &"apply_zone")
	if not router.is_connected(ROUTER_SIGNAL, hook):
		router.connect(ROUTER_SIGNAL, hook)
	if current() == null:
		_owner_ref = weakref(clock)
	return clock


## The installed owner (the first one installed, SceneRouter's in the game), or null (a freed one reads as none).
static func current() -> WeatherClock:
	if _owner_ref == null:
		return null
	return _owner_ref.get_ref() as WeatherClock


## The zone_weather.json document (cached; {} when it is missing or not an object).
static func data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if parsed is Dictionary:
			_data_cache = parsed
	return _data_cache


## The zone row for `scene_path`, or {} when the data names no such scene.
static func zone_row(scene_path: String) -> Dictionary:
	for row: Variant in data().get("zones", []):
		if row is Dictionary and String((row as Dictionary).get("scene", "")) == scene_path:
			return row
	return {}


## The hymn_wind value for `scene_path`: its zone row, else the data's default.
static func zone_wind(scene_path: String) -> Vector4:
	var row := zone_row(scene_path)
	if row.is_empty():
		var fallback: Variant = data().get("default", {})
		row = fallback if fallback is Dictionary else {}
	return wind_vector(row)


## A zone_weather row as hymn_wind: xyz = downwind direction * speed (m/s), w = gust.
static func wind_vector(row: Dictionary) -> Vector4:
	var az := deg_to_rad(float(row.get("toward_azimuth_deg", 0.0)))
	var speed := float(row.get("wind_m_s", 0.0))
	return Vector4(sin(az) * speed, 0.0, -cos(az) * speed, float(row.get("gust", 0.0)))


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_PAUSABLE
	time_s = float(ShaderGlobals.get_value(GLOBAL_WIND_TIME, 0.0))


func _process(delta: float) -> void:
	advance(delta)


## One frame of the clock: on by `delta` seconds and written, unless something holds it.
func advance(delta: float) -> void:
	if is_held():
		return
	if not _started:
		_started = true
		_apply_running_scene()
	time_s += delta
	ShaderGlobals.set_value(GLOBAL_WIND_TIME, time_s)


## Sets the clock (a cutscene's scrub). Written now unless something holds it.
func set_time(seconds: float) -> void:
	time_s = seconds
	if not is_held():
		ShaderGlobals.set_value(GLOBAL_WIND_TIME, time_s)


## Applies `scene_path`'s zone wind (SceneRouter.scene_swapping calls this, under the opaque fade).
func apply_zone(scene_path: String) -> void:
	zone_path = scene_path
	_started = true
	_wind_pending = true
	if not is_held():
		_write_wind()


## Holds the clock until release(holder) or until `holder` is freed. Holding twice with one object is one hold.
func hold(holder: Object) -> void:
	if holder != null:
		_holds[holder.get_instance_id()] = weakref(holder)


## Drops `holder`'s hold. When nothing holds the clock any more, the clock and any waiting zone wind are written.
func release(holder: Object) -> void:
	if holder == null:
		return
	_holds.erase(holder.get_instance_id())
	if not is_held():
		ShaderGlobals.set_value(GLOBAL_WIND_TIME, time_s)
		if _wind_pending:
			_write_wind()


func is_held() -> bool:
	return not holders().is_empty()


## The live objects holding the clock (freed holders are dropped here).
func holders() -> Array[Object]:
	var out: Array[Object] = []
	for id: Variant in _holds.keys():
		var o: Variant = (_holds[id] as WeakRef).get_ref()
		if o == null:
			_holds.erase(id)
		else:
			out.append(o as Object)
	return out


func _write_wind() -> void:
	_wind_pending = false
	ShaderGlobals.set_value(GLOBAL_WIND, zone_wind(zone_path))


## A scene run on its own (F6, no swap): its own row's wind, if the data has one.
func _apply_running_scene() -> void:
	var scene := get_tree().current_scene if is_inside_tree() else null
	if scene != null and not zone_row(scene.scene_file_path).is_empty():
		apply_zone(scene.scene_file_path)


func _exit_tree() -> void:
	if current() == self:
		_owner_ref = null
