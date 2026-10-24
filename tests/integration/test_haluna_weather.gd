extends TestCase
## The Haluna zone and the weather clock (M2-ARC-02, m2-slice): the mood rig defers to the WeatherClock
## owner in play (it writes the wind and clock only when no owner runs or the capture holds it, and
## never resets the owner's clock on leaving), and the night applies the zone's night wind variant.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"

var zone: HalunaZone


func before_each() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	(zone.get_node("Story") as HalunaStory).autostart = false


func test_the_rig_owns_the_weather_only_while_the_owner_is_held_or_absent() -> void:
	var wc := WeatherClock.current()
	assert_true(wc != null, "SceneRouter installs the owner")
	if wc == null:
		zone.free()
		return
	var was_held := wc.is_held()
	assert_false(was_held, "nothing holds the clock in the test run")
	assert_false(HalunaMood.owns_weather(), "in play the owner writes the wind and clock")
	var holder := RefCounted.new()
	wc.hold(holder)
	assert_true(HalunaMood.owns_weather(), "a held owner (the capture) leaves it to the rig")
	wc.release(holder)
	assert_false(HalunaMood.owns_weather())
	_host().add_child(zone)
	assert_false(zone.mood.get(&"_wrote_weather"), "the rig wrote neither global in play")
	_done()


func test_night_applies_the_night_land_breeze() -> void:
	_host().add_child(zone)
	var row := WeatherClock.zone_row(ZONE)
	var night: Dictionary = (row["variants"] as Dictionary)["night"]
	var before: Variant = ShaderGlobals.get_value(&"hymn_wind")
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
	zone.set_night(cfg.get("night", {}), [])
	assert_eq(ShaderGlobals.get_value(&"hymn_wind"), WeatherClock.wind_vector(night), "the night wind")
	assert_false(zone.apply_wind_variant(&"no_such_variant"))
	ShaderGlobals.set_value(&"hymn_wind", before)
	_done()


func test_the_slice_scenes_have_wind_rows() -> void:
	for scene: String in [
		"res://game/levels/ch03/first_verse/first_verse.tscn", "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"
	]:
		assert_false(WeatherClock.zone_row(scene).is_empty(), "%s has a zone wind" % scene)
	assert_true(
		float(WeatherClock.zone_row("res://game/levels/ch03/shell_shrine/shell_shrine.tscn")["wind_m_s"]) < 1.0,
		"still air indoors"
	)
	zone.free()


func _done() -> void:
	if zone != null and is_instance_valid(zone):
		if zone.is_inside_tree():
			_host().remove_child(zone)
		zone.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
