class_name HeroFootIK
extends SkeletonModifier3D
## Foot IK on uneven ground (M2-HER-1116, ADR 0190; tuning: game/data/hero_motion/foot_ik.json). The clips are
## authored on flat ground at the body's root, so on a slope or a step one foot floats and the other sinks. After the
## clips and the idle micro-motion, this casts a ray under each foot and moves the foot by the floor's height there
## relative to the root plane (eased: a step edge never pops), drops the hips by the lower foot's offset so that leg
## reaches, and bends each leg to its foot with a two-bone solve (thigh and shin, in the knee's own plane); the foot
## keeps its animated orientation. On flat ground nothing is touched. Add it with HeroMotion.add_foot_ik(actor).
## A rig without the named bones gets nothing. Deterministic: no randomness; the easing advances by the frames' delta.

const DATA_PATH := "res://game/data/hero_motion/foot_ik.json"
## Below this a length or a cross product counts as zero (degenerate legs).
const EPS := 1e-5

## Each foot's current offset (metres, + up), eased toward the floor under it.
var offsets := PackedFloat32Array()
var tuning: Dictionary = {}
## Physics bodies the rays ignore (the body's own collider: a FieldController's capsule).
var exclude: Array[RID] = []

var _legs: Array[PackedInt32Array] = []
var _hips := -1
var _bound: Skeleton3D
var _primed := false


func _init(cfg: Dictionary = {}) -> void:
	tuning = cfg if not cfg.is_empty() else load_data()


static func load_data(path: String = DATA_PATH) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("HeroFootIK: cannot read %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func _process_modification_with_delta(delta: float) -> void:
	var skel := get_skeleton()
	if skel != null:
		apply(skel, delta)


## Resolves the leg bones on `skel` (once per skeleton). Returns how many legs it found.
func bind(skel: Skeleton3D) -> int:
	if skel == _bound:
		return _legs.size()
	_bound = skel
	_legs.clear()
	for row: Variant in tuning.get("legs", []):
		var r := row as Dictionary
		var ids := PackedInt32Array(
			[
				skel.find_bone(str(r.get("thigh", ""))),
				skel.find_bone(str(r.get("shin", ""))),
				skel.find_bone(str(r.get("foot", "")))
			]
		)
		if not ids.has(-1):
			_legs.append(ids)
	_hips = skel.find_bone(str(tuning.get("hips", "")))
	offsets.resize(_legs.size())
	offsets.fill(0.0)
	_primed = false
	return _legs.size()


## One frame: measures the floor under each foot, eases the offsets and bends the legs. `delta` <= 0 puts the
## offsets straight on the floor (the first frame always does). Returns how many legs it bent.
func apply(skel: Skeleton3D, delta: float) -> int:
	if not bool(tuning.get("enabled", true)) or bind(skel) == 0 or not skel.is_inside_tree():
		return 0
	var xf := skel.global_transform
	var root_y := xf.origin.y
	var max_adjust := float(tuning.get("max_adjust_m", 0.0))
	var rate := float(tuning.get("adjust_rate_mps", 0.0))
	var dead_zone := float(tuning.get("dead_zone_m", 0.0))
	var feet: Array[Transform3D] = []
	var flat := true
	for i in _legs.size():
		var foot := skel.get_bone_global_pose(_legs[i][2])
		feet.append(foot)
		var raw := _floor_y(skel, xf * foot.origin, root_y) - root_y
		# The dead zone is taken off continuously (never a threshold), so leaving it never pops.
		var want := clampf(signf(raw) * maxf(absf(raw) - dead_zone, 0.0), -max_adjust, max_adjust)
		offsets[i] = want if (delta <= 0.0 or not _primed) else move_toward(offsets[i], want, rate * delta)
		flat = flat and absf(offsets[i]) < EPS
	_primed = true
	if flat:
		return 0
	var inv := xf.basis.inverse()
	var drop := 0.0
	for o in offsets:
		drop = minf(drop, o)
	if _hips >= 0 and drop < 0.0:
		var hips := skel.get_bone_global_pose(_hips)
		hips.origin += inv * (Vector3.UP * drop)
		skel.set_bone_global_pose(_hips, hips)
	var bent := 0
	for i in _legs.size():
		var target := feet[i].origin + inv * (Vector3.UP * offsets[i])
		if _solve(skel, _legs[i], target, feet[i].basis):
			bent += 1
	return bent


## The floor's height under `at` (world), from ray_up_m above the root plane to ray_down_m below; `root_y` when
## the ray finds nothing.
func _floor_y(skel: Skeleton3D, at: Vector3, root_y: float) -> float:
	var world := skel.get_world_3d()
	if world == null:
		return root_y
	var from := Vector3(at.x, root_y + float(tuning.get("ray_up_m", 0.0)), at.z)
	var to := Vector3(at.x, root_y - float(tuning.get("ray_down_m", 0.0)), at.z)
	var q := PhysicsRayQueryParameters3D.create(from, to)
	q.exclude = exclude
	var hit := world.direct_space_state.intersect_ray(q)
	return (hit["position"] as Vector3).y if not hit.is_empty() else root_y


## Bends `leg` (thigh, shin, foot bone ids) so the foot reaches `target` (skeleton space), the knee staying on its
## side of the hip-ankle line, and gives the foot `foot_basis` back. False for a degenerate leg.
func _solve(skel: Skeleton3D, leg: PackedInt32Array, target: Vector3, foot_basis: Basis) -> bool:
	var a_pt := skel.get_bone_global_pose(leg[0]).origin
	var b_pt := skel.get_bone_global_pose(leg[1]).origin
	var c_pt := skel.get_bone_global_pose(leg[2]).origin
	var upper := a_pt.distance_to(b_pt)
	var lower := b_pt.distance_to(c_pt)
	var reach := target - a_pt
	if upper < EPS or lower < EPS or reach.length() < EPS:
		return false
	var d := clampf(reach.length(), absf(upper - lower) + EPS, upper + lower - float(tuning.get("reach_slack_m", 0.0)))
	var n := (b_pt - a_pt).cross(c_pt - a_pt)
	if n.length() < EPS:
		n = skel.get_bone_global_pose(leg[0]).basis.x
	n = n.normalized()
	var dir := reach.normalized()
	var ang := acos(clampf((upper * upper + d * d - lower * lower) / (2.0 * upper * d), -1.0, 1.0))
	var now := (b_pt - a_pt).normalized()
	var k1 := dir.rotated(n, ang)
	var k2 := dir.rotated(n, -ang)
	var knee := k1 if k1.dot(now) >= k2.dot(now) else k2
	var thigh := skel.get_bone_global_pose(leg[0])
	thigh.basis = Basis(Quaternion(now, knee)) * thigh.basis
	skel.set_bone_global_pose(leg[0], thigh)
	var shin := skel.get_bone_global_pose(leg[1])
	var ankle_now := skel.get_bone_global_pose(leg[2]).origin - shin.origin
	var ankle_want := a_pt + dir * d - shin.origin
	if ankle_now.length() > EPS and ankle_want.length() > EPS:
		shin.basis = Basis(Quaternion(ankle_now.normalized(), ankle_want.normalized())) * shin.basis
		skel.set_bone_global_pose(leg[1], shin)
	var foot := skel.get_bone_global_pose(leg[2])
	foot.basis = foot_basis
	skel.set_bone_global_pose(leg[2], foot)
	return true
