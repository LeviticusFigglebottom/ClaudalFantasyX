extends TestCase
## M2-HER-1116: HeroFootIK puts each foot on the floor under it. On flat ground nothing moves; a raised step under
## one foot lifts that foot by the step and bends its knee; lower ground under one foot drops the hips so that leg
## reaches; the legs keep their lengths; and crossing a step edge eases (no bone snaps a frame).

const MODEL := "res://assets/characters/rhen/rhen_lod1.glb"
const STEP_M := 0.12
const TOL_M := 0.01
const LENGTH_TOL_M := 0.001

## Each test works at its own site, 20 m from the last (static: the runner makes a new instance per test), because
## bodies freed by a test leave the physics space only on a physics step.
static var _sites := 0

var made: Array[Node] = []
var _site := Vector3.ZERO


func before_each() -> void:
	_sites += 1
	_site = Vector3(20.0 * _sites, 0.0, 0.0)


## Frees what the test made (each test ends with it: the runner makes a new instance per test, so before_each never
## sees the last one's nodes).
func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_a_floor_inside_the_dead_zone_moves_nothing() -> void:
	_box(Vector3(0.0, -0.5 + 0.006, 0.0), Vector3(6.0, 1.0, 6.0))  # 6 mm proud of the root: terrain noise
	var m := _model()
	var skel := HeroMotion.skeleton_of(m)
	var before := HeroMotionGuard.bone_points(skel)
	assert_eq(HeroMotion.add_foot_ik(m).apply(skel, 0.0), 0, "no leg bent for noise")
	assert_eq(HeroMotionGuard.max_bone_step(before, HeroMotionGuard.bone_points(skel)), 0.0)
	_done()


func test_flat_ground_leaves_the_pose_alone() -> void:
	_box(Vector3(0.0, -0.5, 0.0), Vector3(6.0, 1.0, 6.0))
	var m := _model()
	var skel := HeroMotion.skeleton_of(m)
	var ik := HeroMotion.add_foot_ik(m)
	var before := HeroMotionGuard.bone_points(skel)
	assert_eq(ik.apply(skel, 0.0), 0, "no leg bent on flat ground")
	assert_eq(HeroMotionGuard.max_bone_step(before, HeroMotionGuard.bone_points(skel)), 0.0, "not a bone moved")
	_done()


func test_a_step_under_one_foot_lifts_it() -> void:
	_box(Vector3(0.0, -0.5, 0.0), Vector3(6.0, 1.0, 6.0))
	var m := _model()
	var skel := HeroMotion.skeleton_of(m)
	var legs := _legs(skel)
	var l0 := _at(skel, legs[0][2])
	var r0 := _at(skel, legs[1][2])
	var hips0 := _at(skel, skel.find_bone("DEF-spine"))
	var len0 := _lengths(skel, legs[0])
	# a step 0.12 m high under the left foot only
	_box(Vector3(l0.x - _site.x, STEP_M - 0.05, l0.z - _site.z), Vector3(0.12, 0.1, 0.3))
	var ik := HeroMotion.add_foot_ik(m)
	var lift := STEP_M - float(ik.tuning["dead_zone_m"])  # the dead zone comes off every offset
	assert_eq(ik.apply(skel, 0.0), 2)
	assert_between(_at(skel, legs[0][2]).y - l0.y, lift - TOL_M, lift + TOL_M, "the left foot is on the step")
	assert_between(_at(skel, legs[1][2]).y - r0.y, -TOL_M, TOL_M, "the right foot stays")
	assert_between(_at(skel, skel.find_bone("DEF-spine")).y - hips0.y, -TOL_M, TOL_M, "the hips stay")
	var len1 := _lengths(skel, legs[0])
	for k in 2:
		assert_between(len1[k], len0[k] - LENGTH_TOL_M, len0[k] + LENGTH_TOL_M, "the leg keeps its length")
	_done()


func test_lower_ground_under_one_foot_drops_the_hips() -> void:
	var m := _model()
	var skel := HeroMotion.skeleton_of(m)
	var legs := _legs(skel)
	var l0 := _at(skel, legs[0][2])
	var r0 := _at(skel, legs[1][2])
	var hips0 := _at(skel, skel.find_bone("DEF-spine"))
	var half := (l0.x + r0.x) * 0.5 - _site.x
	var left_side := signf(l0.x - _site.x - half)
	_box(Vector3(half + left_side * 1.5, -0.5, 0.0), Vector3(3.0, 1.0, 6.0))  # the left foot's side at the root
	_box(Vector3(half - left_side * 1.5, -0.5 - STEP_M, 0.0), Vector3(3.0, 1.0, 6.0))  # the right side lower
	var ik := HeroMotion.add_foot_ik(m)
	var lift := STEP_M - float(ik.tuning["dead_zone_m"])
	ik.apply(skel, 0.0)
	assert_between(_at(skel, skel.find_bone("DEF-spine")).y - hips0.y, -lift - TOL_M, -lift + TOL_M, "hips drop")
	assert_between(_at(skel, legs[1][2]).y - r0.y, -lift - TOL_M, -lift + TOL_M, "the right foot reaches down")
	assert_between(_at(skel, legs[0][2]).y - l0.y, -TOL_M, TOL_M, "the left foot stays on its floor")
	_done()


func test_crossing_a_step_edge_eases() -> void:
	_box(Vector3(0.0, -0.5, 0.0), Vector3(6.0, 1.0, 6.0))
	var m := _model()
	var skel := HeroMotion.skeleton_of(m)
	var legs := _legs(skel)
	var ik := HeroMotion.add_foot_ik(m)
	var data := HeroMotionGuard.load_data()
	var dt := HeroMotionGuard.frame_sec(data)
	ik.apply(skel, 0.0)
	var l0 := _at(skel, legs[0][2])
	_box(Vector3(l0.x - _site.x, STEP_M - 0.05, l0.z - _site.z), Vector3(0.12, 0.1, 0.3))
	var rate := float(ik.tuning["adjust_rate_mps"])
	var prev := l0.y
	var reached := false
	for i in 30:
		skel.reset_bone_poses()  # each frame starts from the clip's pose, as the modifier stack does
		ik.apply(skel, dt)
		var y := _at(skel, legs[0][2]).y
		assert_true(absf(y - prev) <= rate * dt + 0.001, "the foot rises at most %.3f m a frame" % (rate * dt))
		prev = y
		reached = reached or y - l0.y >= STEP_M - float(ik.tuning["dead_zone_m"]) - TOL_M
	assert_true(reached, "and gets onto the step in half a second")
	_done()


func _model() -> Node3D:
	var m := (load(MODEL) as PackedScene).instantiate() as Node3D
	m.position = _site
	_add(m)
	return m


## A static box of `size` centred at `at`.
func _box(at: Vector3, size: Vector3) -> void:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	# Placed before it enters the tree: a static body moved later only moves on the next physics step.
	body.position = _site + at
	_add(body)


func _legs(skel: Skeleton3D) -> Array[PackedInt32Array]:
	var out: Array[PackedInt32Array] = []
	for s in ["L", "R"]:
		out.append(
			PackedInt32Array(
				[
					skel.find_bone("DEF-thigh.%s" % s),
					skel.find_bone("DEF-shin.%s" % s),
					skel.find_bone("DEF-foot.%s" % s)
				]
			)
		)
	return out


func _at(skel: Skeleton3D, bone: int) -> Vector3:
	return skel.global_transform * skel.get_bone_global_pose(bone).origin


func _lengths(skel: Skeleton3D, leg: PackedInt32Array) -> PackedFloat32Array:
	return PackedFloat32Array(
		[_at(skel, leg[0]).distance_to(_at(skel, leg[1])), _at(skel, leg[1]).distance_to(_at(skel, leg[2]))]
	)


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)
