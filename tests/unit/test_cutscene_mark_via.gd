extends TestCase
## M3-CIN-1221 (act1-chapters' patch, applied to the sequencer): `@mark <actor> <mark>
## via=<mark>,<mark>` walks the polyline through the via marks as one eased walk. CutsceneMotion's path helpers: the
## length, the leg a distance lies on, and the point there.

const PATH := [Vector3(0, 0, 0), Vector3(3, 0, 0), Vector3(3, 2.4, -4)]


func _path() -> PackedVector3Array:
	return PackedVector3Array(PATH)


func test_a_path_is_as_long_as_its_legs() -> void:
	assert_true(is_equal_approx(CutsceneMotion.path_length(_path()), 3.0 + Vector3(0, 2.4, -4).length()))
	assert_eq(CutsceneMotion.path_length(PackedVector3Array([Vector3.ONE])), 0.0, "one point: no length")


func test_a_distance_lies_on_its_leg() -> void:
	assert_eq(CutsceneMotion.path_leg(_path(), 0.0), 0)
	assert_eq(CutsceneMotion.path_leg(_path(), 2.9), 0)
	assert_eq(CutsceneMotion.path_leg(_path(), 3.1), 1, "past the corner")
	assert_eq(CutsceneMotion.path_leg(_path(), 99.0), 1, "past the end: the last leg")


func test_the_point_along_a_path_turns_the_corner_and_lands() -> void:
	assert_eq(CutsceneMotion.path_point(_path(), 0.0), Vector3.ZERO)
	assert_true(CutsceneMotion.path_point(_path(), 1.5).is_equal_approx(Vector3(1.5, 0, 0)), "on the first leg")
	assert_true(CutsceneMotion.path_point(_path(), 3.0).is_equal_approx(Vector3(3, 0, 0)), "at the corner")
	var second := Vector3(0, 2.4, -4).length()
	var half := CutsceneMotion.path_point(_path(), 3.0 + second * 0.5)
	assert_true(half.is_equal_approx(Vector3(3, 1.2, -2)), "half up the second leg (a stair's line)")
	assert_eq(CutsceneMotion.path_point(_path(), 99.0), Vector3(3, 2.4, -4), "clamped to the end")
	assert_eq(CutsceneMotion.path_point(_path(), -1.0), Vector3.ZERO, "clamped to the start")


func test_each_leg_turns_the_walker_level() -> void:
	assert_eq(CutsceneMotion.flat_dir(_path(), 0), Vector3(3, 0, 0), "the first leg")
	assert_eq(CutsceneMotion.flat_dir(_path(), 1), Vector3(0, 0, -4), "the stair's leg, level (no pitch)")
	assert_eq(CutsceneMotion.flat_dir(_path(), 2), Vector3.ZERO, "past the last point")
