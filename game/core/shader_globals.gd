class_name ShaderGlobals
extends RefCounted
## Writes the project's global shader uniforms (project.godot [shader_globals], e.g. hymn_sun_direction)
## and keeps a CPU-side copy of what was written. RenderingServer.global_shader_parameter_get only
## works in the editor, so gameplay code that needs the value (VegetationPlant's shelter probe aims at
## the sun, M1-ENV-03) reads it here. Scripts that drive a global write it through set_value(), and
## restore it through reset(), so the copy never goes stale (M1-ENV-09).
##
## A node in LISTENERS_GROUP gets `LISTENER_METHOD(name, value)` whenever set_value() or reset() changes
## a global's value (VegetationPlant re-probes its shelter when the sun moves). FRAME_GLOBALS, which change
## every frame, never notify: a group call per frame over every listener would cost more than it tells.
##
## Zone globals (M1-RND-23, review-sweep-J S2): ZONE_GLOBALS are written back to their project.godot
## defaults on every scene swap, so a zone that never writes one does not inherit the last zone's
## value. `ShaderGlobals.install(SceneRouter)` connects that reset to SceneRouter.scene_swapping (fired
## under the opaque fade, just before the new scene enters), so the router names no system that owns
## a global. Add a global here when a zone sets it and the next zone must not see it.
##
## Threaded loads (M3-HER-1151): while SceneRouter instantiates a zone on a WorkerThreadPool thread (hold_writes() ..
## release_writes()), set_value() and reset() keep the copy as always but hold the RenderingServer write and send the
## last value per global when the load ends. A global write walks the materials that use the global buffer while
## the worker thread is creating the new zone's materials ("Attempting to initialize the wrong RID" from
## WeatherClock's per-frame hymn_wind_time on the return into the Saltgrass Causeway).

## The per-zone globals: the zone night sea-glow (GlimmerField.set_scene_sea_glow) and the water level
## (the zone sea's WaterSurface, or a WeatheringTide without one), and the still actors (RevenantTells,
## M3-RND-03), which a revenant's node resets when it leaves.
const ZONE_GLOBALS: Array[StringName] = [
	&"hymn_zone_sea_glow",
	&"hymn_water_level",
	&"hymn_still_actor_0",
	&"hymn_still_actor_1",
	&"hymn_still_actor_heights",
]
## Globals written every frame (the weather clock, WeatherClock, M2-ARC-02; the still actors, M3-RND-03):
## set_value() and reset() never call the listeners for them.
const FRAME_GLOBALS: Array[StringName] = [
	&"hymn_wind_time", &"hymn_still_actor_0", &"hymn_still_actor_1", &"hymn_still_actor_heights"
]
const ROUTER_SIGNAL := &"scene_swapping"
const SETTINGS_PREFIX := "shader_globals/"
const LISTENERS_GROUP := &"shader_globals_listeners"
const LISTENER_METHOD := &"_on_shader_global_changed"

static var _values: Dictionary = {}
## Nested holds of the RenderingServer writes (threaded loads), and the writes held: name -> value.
static var _write_holds := 0
static var _held_writes: Dictionary = {}


## Sets the global uniform `name` for every shader and remembers the value.
static func set_value(name: StringName, value: Variant) -> void:
	_write(name, value)
	var changed := not _same(get_value(name), value)
	_values[name] = value
	if changed:
		_notify(name, value)


## Holds the RenderingServer writes until release_writes() (SceneRouter, around a threaded instantiate). Nests.
static func hold_writes() -> void:
	_write_holds += 1


## Ends one hold; the last one sends every held global's last value.
static func release_writes() -> void:
	_write_holds = maxi(_write_holds - 1, 0)
	if _write_holds > 0:
		return
	var held := _held_writes
	_held_writes = {}
	for name: StringName in held:
		RenderingServer.global_shader_parameter_set(name, held[name])


## True while the RenderingServer writes are held.
static func writes_held() -> bool:
	return _write_holds > 0


static func _write(name: StringName, value: Variant) -> void:
	if _write_holds > 0:
		_held_writes[name] = value
	else:
		RenderingServer.global_shader_parameter_set(name, value)


## Restores the global uniform `name` to its project.godot default and forgets the written value.
static func reset(name: StringName) -> void:
	var value: Variant = default_value(name)
	if value == null:
		return
	_write(name, value)
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


## The ZONE_GLOBALS values now (SceneRouter keeps a resident field zone's, to give them back on its return).
static func zone_snapshot() -> Dictionary:
	var out := {}
	for name in ZONE_GLOBALS:
		out[name] = get_value(name, project_default(name))
	return out


## Writes back a zone_snapshot() (after the swap's reset_zone_values()).
static func restore_zone(snapshot: Dictionary) -> void:
	for name: StringName in snapshot:
		set_value(name, snapshot[name])


## The project.godot [shader_globals] default of `name`, or null if it is not declared.
static func default_value(name: StringName) -> Variant:
	var entry: Variant = ProjectSettings.get_setting(SETTINGS_PREFIX + String(name))
	if entry is Dictionary:
		return (entry as Dictionary).get("value")
	return null


## Same as default_value() (the name M1-RND-23's callers use).
static func project_default(name: StringName) -> Variant:
	return default_value(name)


static func _on_scene_swapping(_scene_path: String) -> void:
	reset_zone_values()


static func _notify(name: StringName, value: Variant) -> void:
	if FRAME_GLOBALS.has(name):
		return
	var tree := Engine.get_main_loop() as SceneTree
	if tree != null:
		tree.call_group(LISTENERS_GROUP, LISTENER_METHOD, name, value)


static func _same(a: Variant, b: Variant) -> bool:
	return typeof(a) == typeof(b) and a == b
