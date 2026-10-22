extends TestCase
## One test per formula in the "Progression" section of docs/kb/design/formulas.md, using the
## worked examples there. Change the doc, progression_formulas.gd, and this file together.


func test_lp_gain_equals_credited_xp() -> void:
	assert_eq(ProgressionFormulas.lp_gain(105), 105)
	assert_eq(ProgressionFormulas.lp_gain(0), 0)
	assert_eq(ProgressionFormulas.lp_gain(-5), 0, "never negative")


func test_lp_threshold_grows_every_ten_points() -> void:
	assert_eq(ProgressionFormulas.lp_threshold(0), 30)
	assert_eq(ProgressionFormulas.lp_threshold(9), 30)
	assert_eq(ProgressionFormulas.lp_threshold(10), 35)
	assert_eq(ProgressionFormulas.lp_threshold(25), 40)
	assert_eq(ProgressionFormulas.lp_threshold(-3), 30, "negative clamps to 0")


func test_convert_lp() -> void:
	assert_eq(ProgressionFormulas.convert_lp(105, 0, 99), Vector2i(3, 15))
	assert_eq(ProgressionFormulas.convert_lp(70, 9, 99), Vector2i(2, 5), "threshold rises mid-award")
	assert_eq(ProgressionFormulas.convert_lp(29, 0, 99), Vector2i(0, 29))
	assert_eq(ProgressionFormulas.convert_lp(105, 0, 1), Vector2i(1, 75), "room limits the gain")
	assert_eq(ProgressionFormulas.convert_lp(105, 0, 0), Vector2i(0, 105), "at the cap LP pools")


func test_movement_room() -> void:
	assert_eq(ProgressionFormulas.movement_room(0), 99)
	assert_eq(ProgressionFormulas.movement_room(98), 1)
	assert_eq(ProgressionFormulas.movement_room(120), 0)
