extends TestCase
## M1-NIT-02 (review-sweep-L on M1-ENV-05 S1): the tide writes hymn_water_level itself whenever no
## sea publishes it, so a sea with publishes_water_level off never leaves the shaders on a stale level.


## Records every value the tide writes to the global (and still writes it: the real path runs).
class SpyTide:
	extends WeatheringTide
	var written: Array[Vector2] = []

	func _write_water_level(level: Vector2) -> void:
		written.append(level)
		super._write_water_level(level)


func test_the_tide_writes_the_level_unless_its_sea_publishes() -> void:
	var tide := WeatheringTide.new()
	assert_true(tide.writes_water_level(), "no sea: the tide writes the global")
	var water := WaterSurface.new()
	tide.water = water
	water.publishes_water_level = false
	assert_true(tide.writes_water_level(), "a sea that does not publish: the tide writes it")
	tide.water_height_y = 0.4
	assert_between(water.position.y, 0.399, 0.401, "the sea still follows the tide")
	water.publishes_water_level = true
	assert_false(tide.writes_water_level(), "the publishing sea writes it, not the tide")
	water.free()
	tide.free()


## M2-NIT-03 (review-sweep-M on M1-NIT-02 S2): asserts the value written, not the computed level, and
## leaves the global at its project default for every later test.
func test_a_tide_in_the_tree_with_a_silent_sea_writes_the_global() -> void:
	var tide := SpyTide.new()
	var water := WaterSurface.new()
	water.publishes_water_level = false
	tide.water = water
	tide.add_child(water)
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(tide)
	assert_true(tide.is_inside_tree())
	tide.written.clear()
	tide.water_height_y = -0.3
	tide.tide_line_y = 0.1
	assert_false(tide.written.is_empty(), "the tide wrote the global")
	if not tide.written.is_empty():
		assert_true(tide.written[-1].is_equal_approx(Vector2(-0.3, 0.1)), "the level it wrote: %s" % tide.written[-1])
	tide.written.clear()
	water.publishes_water_level = true
	tide.water_height_y = 0.2
	assert_true(tide.written.is_empty(), "a publishing sea: the tide writes nothing")
	tide.get_parent().remove_child(tide)
	tide.free()
	_restore_water_level()


static func _restore_water_level() -> void:
	var entry: Variant = ProjectSettings.get_setting("shader_globals/%s" % WeatheringTide.GLOBAL_WATER_LEVEL)
	if entry is Dictionary:
		RenderingServer.global_shader_parameter_set(WeatheringTide.GLOBAL_WATER_LEVEL, (entry as Dictionary)["value"])
