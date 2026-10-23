extends TestCase
## M1-NIT-02 (review-sweep-L on M1-ENV-05 S1): the tide writes hymn_water_level itself whenever no
## sea publishes it, so a sea with publishes_water_level off never leaves the shaders on a stale level.


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


func test_a_tide_in_the_tree_with_a_silent_sea_pushes_without_error() -> void:
	var tide := WeatheringTide.new()
	var water := WaterSurface.new()
	water.publishes_water_level = false
	tide.water = water
	tide.add_child(water)
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(tide)
	assert_true(tide.is_inside_tree())
	tide.water_height_y = -0.3
	tide.tide_line_y = 0.1
	assert_true(tide.water_level().is_equal_approx(Vector2(-0.3, 0.1)), "the level it wrote")
	tide.get_parent().remove_child(tide)
	tide.free()
