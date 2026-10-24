extends TestCase
## M2-ARC-02: WeatherClock, the one runtime owner of the weather clock (hymn_wind_time) and the zone wind
## (hymn_wind). The clock advances, pauses with the tree and survives a swap; the zone wind comes from
## game/data/world/zone_weather.json with a default; a hold (the screenshot capture's) stops every write, so
## capture pinning wins; the Drownbell flood rig never writes the clock. Every test leaves both globals at their
## project defaults.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const NO_ROW := "res://nowhere.tscn"
const STEP_S := 0.25
const EPS := 1e-5


## A stand-in router: a node with the scene_swapping(scene_path) signal, in the tree.
func _router() -> Node:
	var r := Node.new()
	r.add_user_signal(String(WeatherClock.ROUTER_SIGNAL), [{"name": "scene_path", "type": TYPE_STRING}])
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(r)
	return r


## Records every ShaderGlobals listener call.
class Listener:
	extends Node
	var heard: Array[StringName] = []

	func _on_shader_global_changed(global: StringName, _value: Variant) -> void:
		heard.append(global)


func _cleanup(router: Node) -> void:
	router.free()
	ShaderGlobals.reset(WeatherClock.GLOBAL_WIND)
	ShaderGlobals.reset(WeatherClock.GLOBAL_WIND_TIME)


func test_the_router_installs_one_owner() -> void:
	var game_clock := WeatherClock.current()
	assert_true(game_clock != null, "SceneRouter installed the owner")
	assert_eq(game_clock.get_parent(), SceneRouter as Node, "a child of the router, so it survives every swap")
	assert_eq(WeatherClock.install(SceneRouter), game_clock, "install is idempotent")
	var hook := Callable(game_clock, &"apply_zone")
	var hooks := 0
	for c: Dictionary in SceneRouter.scene_swapping.get_connections():
		if c["callable"] == hook:
			hooks += 1
	assert_eq(hooks, 1, "connected once")
	var plain := Node.new()
	assert_eq(WeatherClock.install(plain), null, "no scene_swapping signal: no owner")
	plain.free()


func test_the_clock_advances_and_writes_the_global() -> void:
	var r := _router()
	var clock := WeatherClock.install(r)
	assert_true(clock != WeatherClock.current(), "a second install never replaces the game's owner")
	clock.set_time(10.0)
	clock.advance(STEP_S)
	clock.advance(STEP_S)
	assert_between(clock.time_s, 10.5 - EPS, 10.5 + EPS, "on by each frame's delta")
	assert_between(float(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND_TIME)), 10.5 - EPS, 10.5 + EPS, "written")
	_cleanup(r)


func test_the_clock_pauses_with_the_tree() -> void:
	var r := _router()
	var clock := WeatherClock.install(r)
	var tree := Engine.get_main_loop() as SceneTree
	r.process_mode = Node.PROCESS_MODE_ALWAYS
	assert_eq(clock.process_mode, Node.PROCESS_MODE_PAUSABLE, "pausable even under an always-on router")
	assert_true(clock.can_process(), "runs while the tree runs")
	tree.paused = true
	assert_false(clock.can_process(), "stops while the tree is paused")
	tree.paused = false
	_cleanup(r)


func test_the_clock_survives_a_swap_and_is_no_zone_global() -> void:
	assert_false(ShaderGlobals.ZONE_GLOBALS.has(WeatherClock.GLOBAL_WIND_TIME), "the clock never resets")
	assert_false(ShaderGlobals.ZONE_GLOBALS.has(WeatherClock.GLOBAL_WIND), "the owner writes the wind on each swap")
	var r := _router()
	var clock := WeatherClock.install(r)
	ShaderGlobals.install(r)
	clock.set_time(30.0)
	r.emit_signal(WeatherClock.ROUTER_SIGNAL, HALUNA)
	clock.advance(STEP_S)
	assert_between(clock.time_s, 30.25 - EPS, 30.25 + EPS, "runs on from its value across the swap")
	assert_between(float(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND_TIME)), 30.25 - EPS, 30.25 + EPS)
	_cleanup(r)


func test_zone_wind_comes_from_data_with_a_default() -> void:
	var doc := WeatherClock.data()
	assert_true(doc.get("default") is Dictionary, "zone_weather.json has a default")
	assert_false(WeatherClock.zone_row(HALUNA).is_empty(), "Haluna has a row")
	var haluna := WeatherClock.zone_wind(HALUNA)
	var fallback := WeatherClock.zone_wind(NO_ROW)
	assert_eq(fallback, WeatherClock.wind_vector(doc["default"]), "a scene with no row gets the default")
	assert_ne(haluna, fallback, "the zone's own wind")
	assert_true(Vector2(fallback.x, fallback.z).length() > 0.0, "the default is not calm")
	var r := _router()
	var clock := WeatherClock.install(r)
	r.emit_signal(WeatherClock.ROUTER_SIGNAL, HALUNA)
	assert_eq(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND), haluna, "applied on the swap")
	assert_eq(clock.zone_path, HALUNA)
	r.emit_signal(WeatherClock.ROUTER_SIGNAL, NO_ROW)
	assert_eq(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND), fallback, "the next zone does not inherit it")
	_cleanup(r)


## The heading convention of the water and Haluna rigs: clockwise from north (-Z), downwind.
func test_wind_vector_heading() -> void:
	var east := WeatherClock.wind_vector({"toward_azimuth_deg": 90.0, "wind_m_s": 2.0, "gust": 0.5})
	assert_true(east.is_equal_approx(Vector4(2.0, 0.0, 0.0, 0.5)), "90 deg blows toward +X: %s" % east)
	var north := WeatherClock.wind_vector({"toward_azimuth_deg": 0.0, "wind_m_s": 3.0, "gust": 0.0})
	assert_true(north.is_equal_approx(Vector4(0.0, 0.0, -3.0, 0.0)), "0 deg blows toward -Z: %s" % north)


## Capture pinning wins: a held clock writes neither global; a zone wind that arrives meanwhile waits for release.
func test_a_hold_stops_every_write_until_release() -> void:
	var r := _router()
	var clock := WeatherClock.install(r)
	clock.set_time(5.0)
	var holder := Node.new()
	clock.hold(holder)
	clock.hold(holder)
	assert_eq(clock.holders().size(), 1, "holding twice is one hold")
	ShaderGlobals.set_value(WeatherClock.GLOBAL_WIND_TIME, 40.0)
	clock.advance(STEP_S)
	clock.set_time(7.0)
	r.emit_signal(WeatherClock.ROUTER_SIGNAL, HALUNA)
	assert_eq(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND_TIME), 40.0, "a pinned clock stays pinned")
	assert_eq(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND), ShaderGlobals.default_value(WeatherClock.GLOBAL_WIND))
	assert_between(clock.time_s, 7.0 - EPS, 7.0 + EPS, "held: does not advance")
	clock.release(holder)
	assert_eq(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND_TIME), 7.0, "release writes the clock")
	assert_eq(ShaderGlobals.get_value(WeatherClock.GLOBAL_WIND), WeatherClock.zone_wind(HALUNA), "and the waiting wind")
	clock.hold(holder)
	holder.free()
	assert_false(clock.is_held(), "a freed holder drops out")
	_cleanup(r)


func test_the_capture_holds_the_owner_for_its_run() -> void:
	var src := FileAccess.get_file_as_string("res://tests/screenshots/capture.gd")
	assert_true(src.contains("WeatherClock.current()") and src.contains("clock.hold(self)"), "capture.gd holds it")


func test_the_flood_rig_never_writes_the_clock() -> void:
	var src := FileAccess.get_file_as_string("res://game/vfx/battle/battle_boss_vfx.gd")
	assert_false(src.contains('hymn_wind_time"'), "BattleBossVfx names no clock global")
	assert_false(src.contains("GLOBAL_WIND_TIME"), "and writes none")


## The clock writes every frame, so ShaderGlobals listeners are not called for it; the wind still notifies.
func test_the_clock_does_not_wake_listeners_every_frame() -> void:
	assert_true(ShaderGlobals.FRAME_GLOBALS.has(WeatherClock.GLOBAL_WIND_TIME))
	var r := _router()
	var clock := WeatherClock.install(r)
	var ear := Listener.new()
	ear.add_to_group(ShaderGlobals.LISTENERS_GROUP)
	r.add_child(ear)
	clock.advance(STEP_S)
	clock.advance(STEP_S)
	r.emit_signal(WeatherClock.ROUTER_SIGNAL, HALUNA)
	assert_eq(ear.heard, [WeatherClock.GLOBAL_WIND] as Array[StringName], "only the wind change was heard")
	_cleanup(r)


func test_every_zone_row_names_a_scene() -> void:
	for row: Variant in WeatherClock.data().get("zones", []):
		var scene := String((row as Dictionary).get("scene", ""))
		assert_true(ResourceLoader.exists(scene), "zone_weather scene exists: %s" % scene)
